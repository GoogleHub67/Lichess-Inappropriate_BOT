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

log = logging.getLogger(__name__)
BASE_URL = "https://lichess.org"

class GameHandler:
    def __init__(self, game_id: str, token: str):
        self.game_id = game_id
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.board = chess.Board()
        self.our_color: chess.Color | None = None
        self.engine: chess.engine.SimpleEngine | None = None
        self.estimator: SkillEstimator | None = None
        self.in_book: bool = True
        self.off_book_notified: bool = False

    async def run(self):
        async with httpx.AsyncClient(base_url=BASE_URL, headers=self.headers, timeout=60) as client:
            self.client = client
            await self._start_engine()
            try:
                async with client.stream("GET", f"/api/bot/game/stream/{self.game_id}") as resp:
                    async for line in resp.aiter_lines():
                        if line.strip():
                            event = json.loads(line)
                            await self._handle_game_event(event)
            finally:
                await self._stop_engine()

    async def _handle_game_event(self, event: dict):
        etype = event.get("type")
        if etype == "gameFull":
            me_resp = await self.client.get("/api/account")
            me = me_resp.json()["id"]
            white_id = event["white"].get("id", "")
            self.our_color = chess.WHITE if white_id == me else chess.BLACK
            self.estimator = SkillEstimator(self.engine, self.our_color)
            log.info(f"Playing as {'White' if self.our_color == chess.WHITE else 'Black'}")
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
                await self.client.post(f"/api/bot/game/{self.game_id}/draw/yes")
                await self._chat("I'll take the draw.")
            elif not score.is_mate() and score.score() <= 50:
                await self.client.post(f"/api/bot/game/{self.game_id}/draw/yes")
                await self._chat("Fair enough, draw accepted.")
            else:
                await self.client.post(f"/api/bot/game/{self.game_id}/draw/no")
                await self._chat("No draws! Keep playing.")
        except Exception as e:
            log.warning(f"Draw handling failed: {e}")

    async def _handle_takeback_offer(self):
        try:
            await self.client.post(f"/api/bot/game/{self.game_id}/takeback/yes")
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
                await self.client.post(f"/api/bot/game/{self.game_id}/resign")
                await self._chat("GG, you got me.")
        except Exception as e:
            log.warning(f"Resign failed: {e}")

    async def _apply_state(self, state: dict):
        if state.get("status", "started") not in ("started", "created"):
            if hasattr(Config, 'CHAT_GG'):
                await self._chat(Config.CHAT_GG)
            return

        old_moves_count = len(self.board.move_stack)
        
        self.board = chess.Board()
        moves_str = state.get("moves", "").strip()
        if moves_str:
            for uci in moves_str.split():
                self.board.push_uci(uci)

        new_moves_count = len(self.board.move_stack)

        if self.estimator and not self.in_book and self.engine:
            if new_moves_count > old_moves_count and self.board.turn == self.our_color:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: self.estimator.record_opponent_move(self.board))

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
                        await self.client.post(f"/api/bot/game/{self.game_id}/move/{book_move.uci()}")
                        return
                    else:
                        self.in_book = False
                        log.info("Opening book exhausted. Switching to live engine analysis.")
            except Exception as e:
                self.in_book = False
                log.warning(f"Failed to read opening book ({e}). Falling back to engine.")
        else:
            self.in_book = False

        # Emergency structural fallback if Stockfish isn't loaded correctly
        if not self.engine:
            log.warning("EMERGENCY FALLBACK: Stockfish engine is not loaded. Selecting first single legal move.")
            legal_moves_list = list(self.board.legal_moves)
            if legal_moves_list:
                fallback_move = legal_moves_list[0] # Properly extracts a single move object item
                await self.client.post(f"/api/bot/game/{self.game_id}/move/{fallback_move.uci()}")
            return

        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None, 
                lambda: self.engine.analyse(self.board, chess.engine.Limit(depth=14))
            )
            
            if self.estimator:
                score_before = info["score"].pov(self.our_color)
                if score_before.is_mate():
                    self.estimator._last_eval = float('inf') if score_before.mate() > 0 else float('-inf')
                else:
                    self.estimator._last_eval = score_before.score()

            default_elo = getattr(Config, 'DEFAULT_ELO', 1500)
            current_opponent_elo = self.estimator.get_elo() if self.estimator else default_elo

            if self.estimator and hasattr(self.estimator, 'throttle_mate_move'):
                final_move = self.estimator.throttle_mate_move(
                    info=info,
                    opponent_elo=current_opponent_elo,
                    legal_moves=list(self.board.legal_moves)
                )
            else:
                final_move = info["move"]

            # Securely extract single move object if tactical evaluations fail
            if not final_move:
                final_move = info["move"] if info["move"] else list(self.board.legal_moves)[0]

            log.info(f"Sending move to Lichess: {final_move.uci()} (Target Elo Context: {current_opponent_elo})")
            await self.client.post(f"/api/bot/game/{self.game_id}/move/{final_move.uci()}")

        except Exception as e:
            log.error(f"Critical breakdown inside _make_move processing sequence: {e}")
            legal_moves_list = list(self.board.legal_moves)
            if legal_moves_list:
                panic_move = legal_moves_list[0] # Isolates a single move object cleanly to prevent double crashes
                await self.client.post(f"/api/bot/game/{self.game_id}/move/{panic_move.uci()}")

    async def _update_cpl(self, board_after_our_move: chess.Board):
        if not self.estimator:
            return
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.estimator.record_position_before_opponent_move(board_after_our_move)
            )
        except Exception as e:
            log.warning(f"CPL update failed: {e}")

    def _book_move(self) -> chess.Move | None:
        if not hasattr(Config, 'BOOK_PATH'):
            return None
        try:
            with chess.polyglot.open_reader(Config.BOOK_PATH) as reader:
                entries = list(reader.find_all(self.board))
                if not entries:
                    return None
                total = sum(e.weight for e in entries)
                r = random.uniform(0, total)
                cumulative = 0
                for entry in entries:
                    cumulative += entry.weight
                    if r <= cumulative:
                        return entry.move
                return entries[0].move
        except FileNotFoundError:
            log.warning(f"Book not found: {Config.BOOK_PATH}")
            self.in_book = False
            return None
        except Exception as e:
            log.warning(f"Book error: {e}")
            return None

    async def _stockfish_move(self, elo: int, state: dict) -> chess.Move | None:
        if not self.engine:
            return None
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.engine.configure({
                "UCI_LimitStrength": True,
                "UCI_Elo": elo
            }))
            wtime = state.get("wtime", 0)
            btime = state.get("btime", 0)
            if wtime == 0 and btime == 0:
                limit = chess.engine.Limit(depth=8)
            else:
                limit = chess.engine.Limit(
                    white_clock=wtime / 1000,
                    black_clock=btime / 1000,
                    white_inc=state.get("winc", 0) / 1000,
                    black_inc=state.get("binc", 0) / 1000,
                )
            result = await loop.run_in_executor(None, lambda: self.engine.play(self.board, limit))
            log.info(f"Stockfish ELO {elo}: {result.move.uci()}")
            return result.move
        except Exception as e:
            log.error(f"Stockfish error: {e}")
            return None

    async def _send_move(self, uci: str):
        r = await self.client.post(f"/api/bot/game/{self.game_id}/move/{uci}")
        r.raise_for_status()
        log.info(f"Sent: {uci}")

    async def _chat(self, message: str, room: str = "player"):
        try:
            await self.client.post(
                f"/api/bot/game/{self.game_id}/chat",
                data={"room": room, "text": message}
            )
        except Exception as e:
            log.warning(f"Chat failed: {e}")

    async def _start_engine(self):
        try:
            log.info(f"Spawning Stockfish engine from: {Config.STOCKFISH_PATH}")
            loop = asyncio.get_event_loop()
            self.engine = await loop.run_in_executor(
                None, lambda: chess.engine.SimpleEngine.popen_uci(Config.STOCKFISH_PATH)
            )
            log.info("--- STOCKFISH ENGINE LAUNCHED SUCCESSFULLY ---")
        except Exception as e:
            log.error(f"Engine failed to start: {e}")
            self.engine = None

    async def _stop_engine(self):
        if self.engine:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.engine.quit)
                log.info("Engine stopped")
            except Exception:
                pass
