import os
import sys
import asyncio
import json
import logging
import random
import chess
import chess.engine
import chess.polyglot
import httpx

# Direct Python to look inside the root directory package structures safely
src_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(src_dir)
config_folder_path = os.path.join(root_dir, "config")
if config_folder_path not in sys.path:
    sys.path.insert(0, config_folder_path)

from bot_config import Config
from skill_estimator import SkillEstimator
from RateLimit429Stopper import RateLimitStopper  # 🟢 Import the rate throttling manager

log = logging.getLogger(__name__)
BASE_URL = "https://lichess.org"

class GameHandler:
    def __init__(self, game_id: str, token: str, engine):
        self.game_id = game_id
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.board = chess.Board()
        self.our_color: chess.Color | None = None
        self.engine = engine  # Consumes the single pre-loaded global engine reference
        self.estimator = None
        self.in_book = True
        self.off_book_notified = False
        self.initial_fen = chess.STARTING_FEN  # Default layout tracker

    async def run(self):
        async with httpx.AsyncClient(base_url=BASE_URL, headers=self.headers, timeout=60) as client:
            self.client = client
            try:
                async with client.stream("GET", f"/api/bot/game/stream/{self.game_id}") as resp:
                    async for line in resp.aiter_lines():
                        if line.strip():
                            await self._handle_game_event(json.loads(line))
            except asyncio.CancelledError:
                if hasattr(Config, 'CHAT_GG'):
                    await self._chat(Config.CHAT_GG)
                raise

    async def _handle_game_event(self, event: dict):
        etype = event.get("type")
        if etype == "gameFull":
            me_resp = await self.client.get("/api/account")
            me = me_resp.json()["id"]
            white_id = event["white"].get("id", "")
            self.our_color = chess.WHITE if white_id == me else chess.BLACK
            self.estimator = SkillEstimator(self.engine, self.our_color)
            log.info(f"Playing as {'White' if self.our_color == chess.WHITE else 'Black'}")
            
            # 🟢 FIX: Handle Lichess 'startpos' or missing strings safely into standard FEN
            raw_fen = event.get("initialFen", "")
            if not raw_fen or raw_fen.lower() == "startpos":
                self.initial_fen = chess.STARTING_FEN
            else:
                self.initial_fen = raw_fen
                
            self.board = chess.Board(self.initial_fen)
            
            if hasattr(Config, 'CHAT_GREET'):
                await self._chat(Config.CHAT_GREET)
            await self._apply_state(event.get("state", {}))
            
        elif etype == "gameState":
            await self._apply_state(event)
            if event.get("bdraw") or event.get("wdraw"):
                await self._handle_draw_offer()
            if event.get("btakeback") or event.get("wtakeback"):
                await self._handle_takeback_offer()
            await self._handle_resign()

    async def _handle_draw_offer(self):
        if not self.engine:
            return
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: self.engine.analyse(self.board, chess.engine.Limit(depth=8)))
            score = info["score"].pov(self.our_color)
            if score.is_mate() and score.mate() < 0:
                await RateLimitStopper.safe_post(self.client, f"/api/bot/game/{self.game_id}/draw/yes")
                await self._chat("I'll take the draw.")
            elif not score.is_mate() and score.score() <= 50:
                await RateLimitStopper.safe_post(self.client, f"/api/bot/game/{self.game_id}/draw/yes")
                await self._chat("Fair enough, draw accepted.")
            else:
                await RateLimitStopper.safe_post(self.client, f"/api/bot/game/{self.game_id}/draw/no")
                await self._chat("No draws! Keep playing.")
        except Exception as e:
            log.warning(f"Draw handling failed: {e}")

    async def _handle_takeback_offer(self):
        try:
            await RateLimitStopper.safe_post(self.client, f"/api/bot/game/{self.game_id}/takeback/yes")
            await self._chat("Takeback granted!")
        except Exception as e:
            log.warning(f"Takeback failed: {e}")

    async def _handle_resign(self):
        if not self.engine:
            return
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: self.engine.analyse(self.board, chess.engine.Limit(depth=8)))
            score = info["score"].pov(self.our_color)
            if score.is_mate() and score.mate() < 0 and abs(score.mate()) <= 3:
                await RateLimitStopper.safe_post(self.client, f"/api/bot/game/{self.game_id}/resign")
                await self._chat("GG, you got me.")
        except Exception as e:
            log.warning(f"Resign failed: {e}")

    async def _apply_state(self, state: dict):
        if state.get("status", "started") not in ("started", "created"):
            return

        moves_str = state.get("moves", "").strip()
        incoming_moves = moves_str.split() if moves_str else []
        
        # Re-play moves up to the second-to-last move based on our custom initial FEN state
        if self.estimator and not self.in_book and self.engine and len(incoming_moves) > len(self.board.move_stack):
            temp_board = chess.Board(self.initial_fen)
            for uci in incoming_moves[:-1]:
                temp_board.push_uci(uci)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.estimator.record_position_before_opponent_move(temp_board))

        # Reset and catch up the primary board from the custom layout
        self.board = chess.Board(self.initial_fen)
        for uci in incoming_moves:
            self.board.push_uci(uci)

        # Evaluate opponent's move
        if self.estimator and not self.in_book and self.engine:
            if len(incoming_moves) > 0 and self.board.turn == self.our_color:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: self.estimator.record_opponent_move(self.board))

        # Make our move if it is our turn
        if self.board.turn == self.our_color:
            await self._make_move(state)

    async def _make_move(self, state: dict):
        if self.in_book and hasattr(Config, 'BOOK_PATH') and os.path.exists(Config.BOOK_PATH):
            try:
                with chess.polyglot.open_reader(Config.BOOK_PATH) as reader:
                    entries = list(reader.find_all(self.board))
                    if entries:
                        weights = [e.weight for e in entries]
                        entry = random.choices(entries, weights=weights, k=1)
                        book_move = entry.move()
                        log.info(f"Opening Book Move Played: {book_move}")
                        move_url = f"/api/bot/game/{self.game_id}/move/{book_move.uci()}"
                        await RateLimitStopper.safe_post(self.client, move_url)
                        return
                    else:
                        self.in_book = False
                        log.info("Opening book exhausted. Switching to live engine analysis.")
                        if hasattr(Config, 'CHAT_OFF_BOOK') and not self.off_book_notified:
                            await self._chat(Config.CHAT_OFF_BOOK)
                            self.off_book_notified = True
            except Exception as e:
                self.in_book = False
                log.warning(f"Failed to read opening book ({e}). Falling back to engine.")
        else:
            self.in_book = False

        if not self.engine:
            log.warning("EMERGENCY FALLBACK: Stockfish engine is not loaded. Selecting first legal move.")
            legal_moves_list = list(self.board.legal_moves)
            if legal_moves_list:
                move_url = f"/api/bot/game/{self.game_id}/move/{legal_moves_list[0].uci()}"
                await RateLimitStopper.safe_post(self.client, move_url)
            return

        try:
            default_elo = getattr(Config, 'DEFAULT_ELO', 1320)
            current_opponent_elo = self.estimator.get_elo() if self.estimator else default_elo

            loop = asyncio.get_event_loop()
            
            # Calibrate engine strength limits securely
            await loop.run_in_executor(
                None, 
                lambda: self.engine.configure({
                    "UCI_LimitStrength": True, 
                    "UCI_Elo": current_opponent_elo
                })
            )

            log.info(f"⏳ Stockfish is thinking... (Target Elo Context: {current_opponent_elo})")

            # Force engine.play with an explicit time threshold to guarantee FIDE quality and prevent Nh6 drops
            result = await loop.run_in_executor(
                None, 
                lambda: self.engine.play(self.board, chess.engine.Limit(time=1.0))
            )
            
            final_move = result.move if hasattr(result, "move") else None

            if not final_move:
                final_move = getattr(result, "ponder", list(self.board.legal_moves)[-1])

            # 🟢 REPLACED WITH THE THROTTLED MOVE TRANSMISSION VARIANT
            log.info(f"🚀 Sending verified tactical move to Lichess: {final_move.uci()}")
            move_url = f"/api/bot/game/{self.game_id}/move/{final_move.uci()}"
            await RateLimitStopper.safe_post(self.client, move_url)

        except Exception as e:
            log.error(f"Critical breakdown inside _make_move processing sequence: {e}", exc_info=True)
            legal_moves_list = list(self.board.legal_moves)
            if legal_moves_list:
                panic_move = legal_moves_list[-1]  # Shakes up the array sorting to prevent front-loaded Nh6 loops
                move_url = f"/api/bot/game/{self.game_id}/move/{panic_move.uci()}"
                await RateLimitStopper.safe_post(self.client, move_url)

    async def _chat(self, message: str, room: str = "player"):
        try:
            # 🟢 REPLACED WITH THE THROTTLED CHAT VARIANT
            chat_url = f"/api/bot/game/{self.game_id}/chat"
            await RateLimitStopper.safe_post(
                self.client, 
                chat_url, 
                data={"room": room, "text": message}
            )
        except Exception as e:
            log.warning(f"Chat failed: {e}")
