import os
import sys
import asyncio
import json
import logging
import httpx
import xml.etree.ElementTree as ET

# 1. Track down the parent folder (Lichess-Inappropriate_BOT)
src_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(src_dir)

# 2. Tell Python where the 'config' folder lives (Linux safe path joining)
config_folder_path = os.path.join(project_root, "config")
if config_folder_path not in sys.path:
    sys.path.insert(0, config_folder_path)

# 3. Now run imports
from bot_config import Config  # Successfully pulls from \config\bot_config.py
from game_handler import GameHandler

# Configure logging to output to stdout for Render logs to capture it smoothly
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log"),
    ],
)
log = logging.getLogger(__name__)

BASE_URL = "https://lichess.org"


def patch_config_via_xml():
    """
    Parses config.xml and patches the Config class attributes 
    dynamically in-memory without changing config.py source code.
    """
    xml_path = os.path.join(project_root, "tests", "config.xml")
    
    if not os.path.exists(xml_path):
        log.warning(f"config.xml not found at {xml_path}. Relying on hardcoded defaults.")
        return

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 1. Parse Game Settings Nodes
        game_settings = root.find("game_settings")
        if game_settings is not None:
            def_elo_node = game_settings.find("default_elo")
            if def_elo_node is not None and def_elo_node.text:
                Config.DEFAULT_ELO = int(def_elo_node.text)

            decline_node = game_settings.find("decline_rated")
            if decline_node is not None and decline_node.text:
                Config.DECLINE_RATED = decline_node.text.lower() == "true"

            variants_node = game_settings.find("accept_variants")
            if variants_node is not None:
                Config.ACCEPT_VARIANTS = [v.text for v in variants_node.findall("variant") if v.text]

            tc_node = game_settings.find("accept_time_controls")
            if tc_node is not None:
                Config.ACCEPT_TIME_CONTROLS = [t.text for t in tc_node.findall("time_control") if t.text]

        # 2. Parse Chat Text Elements
        bot_chat = root.find("bot_chat")
        if bot_chat is not None:
            greet_node = bot_chat.find("greet")
            if greet_node is not None and greet_node.text:
                Config.CHAT_GREET = greet_node.text

            off_book_node = bot_chat.find("off_book")
            if off_book_node is not None and off_book_node.text:
                Config.CHAT_OFF_BOOK = off_book_node.text

            gg_node = bot_chat.find("gg")
            if gg_node is not None and gg_node.text:
                Config.CHAT_GG = greet_node.text if gg_node.text is None else gg_node.text

            blunder_node = bot_chat.find("blunder_detected")
            if blunder_node is not None and blunder_node.text:
                Config.CHAT_BLUNDER_DETECTED = blunder_node.text
        
        log.info("In-memory patching completed successfully from config.xml!")
    except Exception as e:
        log.error(f"Failed to inject XML rules onto Config module attributes: {e}")


# Run the configuration sync immediately before initialization
patch_config_via_xml()


class LichessBot:
    def __init__(self):
        self.token = Config.LICHESS_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.active_games: dict[str, asyncio.Task] = {}

    async def start(self):
        async with httpx.AsyncClient(base_url=BASE_URL, headers=self.headers, timeout=30) as client:
            response = await client.get("/api/account")
            
            # Catch bad authentication states early to prevent runtime KeyError crashes
            if response.status_code == 401:
                log.critical("CRITICAL: Lichess API Token rejected! (401 Unauthorized). Verify your token string in the environment variables.")
                return

            profile = response.json()
            if "username" not in profile:
                log.critical(f"CRITICAL: Failed to parse user profile. Network payload: {profile}")
                return

            log.info(f"Logged in as: {profile['username']}")
            if profile.get("title") != "BOT":
                log.info("Upgrading to BOT account...")
                await client.post("/api/bot/account/upgrade")

        log.info("INAPPROPRIATE_BOT is ONLINE")
        await self._stream_events()

    async def _stream_events(self):
        log.info("Listening for events...")
        backoff = 1
        while True:
            try:
                async with httpx.AsyncClient(
                    base_url=BASE_URL, headers=self.headers, timeout=None
                ) as client:
                    async with client.stream("GET", "/api/stream/event") as resp:
                        resp.raise_for_status()
                        backoff = 1
                        async for line in resp.aiter_lines():
                            if line.strip():
                                try:
                                    await self._handle_event(json.loads(line))
                                except Exception as e:
                                    log.error(f"Event error: {e}")
            except Exception as e:
                log.error(f"Stream dropped: {e} - retry in {backoff}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)

    async def _handle_event(self, event: dict):
        etype = event.get("type")

        if etype == "challenge":
            await self._handle_challenge(event["challenge"])

        elif etype == "gameStart":
            gid = event["game"]["id"]
            if gid not in self.active_games:
                log.info(f"Game starting: {gid}")
                task = asyncio.create_task(self._run_game(gid))
                self.active_games[gid] = task

        elif etype == "gameFinish":
            gid = event["game"]["id"]
            task = self.active_games.pop(gid, None)
            if task:
                task.cancel()
            log.info(f"Game finished: {gid} | Active: {len(self.active_games)}")

    async def _handle_challenge(self, challenge: dict):
        cid        = challenge["id"]
        challenger = challenge["challenger"]["name"]
        variant    = challenge.get("variant", {}).get("key", "standard")
        speed      = challenge.get("speed", "blitz")
        rated      = challenge.get("rated", False)

        log.info(f"Challenge: {challenger} | {variant} | {speed} | rated={rated}")

        if variant not in Config.ACCEPT_VARIANTS:
            await self._decline(cid, "variant"); return
        if speed not in Config.ACCEPT_TIME_CONTROLS:
            await self._decline(cid, "tooSlow"); return
        if Config.DECLINE_RATED and rated:
            await self._decline(cid, "casual"); return

        async with httpx.AsyncClient(base_url=BASE_URL, headers=self.headers) as c:
            await c.post(f"/api/challenge/{cid}/accept")
        log.info(f"Accepted: {challenger}")

    async def _decline(self, cid: str, reason: str = "generic"):
        async with httpx.AsyncClient(base_url=BASE_URL, headers=self.headers) as c:
            await c.post(f"/api/challenge/{cid}/decline", data={"reason": reason})

    async def _run_game(self, game_id: str):
        try:
            await GameHandler(game_id, self.token).run()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.error(f"Game {game_id} error: {e}", exc_info=True)


if __name__ == "__main__":
    bot = LichessBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        log.info("Bot stopped. GG.")
