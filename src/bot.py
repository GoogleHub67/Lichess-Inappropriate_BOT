import os
import sys

# 1. Track down the parent folder (Lichess-Inappropriate_BOT)
src_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(src_dir)

# 2. Tell Python where the 'config' folder lives
config_folder_path = os.path.join(project_root, "config")
if config_folder_path not in sys.path:
    sys.path.insert(0, config_folder_path)

# 3. Add site-packages as a secondary fallback for dependencies
site_packages_path = r"C:\Users\Aarav\AppData\Local\Programs\Python\Python311\Lib\site-packages"
if site_packages_path not in sys.path:
    sys.path.append(site_packages_path)

# 4. Now run imports
import asyncio
import json
import logging
import httpx
from bot_config import Config  # Successfully pulls from \config\bot_config.py
from game_handler import GameHandler

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


class LichessBot:
    def __init__(self):
        self.token = Config.LICHESS_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.active_games: dict[str, asyncio.Task] = {}

    async def start(self):
        async with httpx.AsyncClient(base_url=BASE_URL, headers=self.headers, timeout=30) as client:
            profile = (await client.get("/api/account")).json()
            log.info(f"Logged in as: {profile['username']}")
            if profile.get("title") != "BOT":
                log.info("Upgrading to BOT account...")
                await client.post("/api/bot/account/upgrade")

        log.info("StopBlunderingInOpeningsYouIdiot is ONLINE")
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
