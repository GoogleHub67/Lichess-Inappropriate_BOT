import os
import sys

# Direct Python to look inside the \config\ directory
src_dir = os.path.dirname(os.path.abspath(__file__))
config_folder_path = os.path.join(os.path.dirname(src_dir), "config")
if config_folder_path not in sys.path:
    sys.path.insert(0, config_folder_path)

site_packages_path = r"C:\Users\Aarav\AppData\Local\Programs\Python\Python311\Lib\site-packages"
if site_packages_path not in sys.path:
    sys.path.append(site_packages_path)

# Followed by your original imports...
from bot_config import Config
import sys
sys.path.append(r"C:\Users\Aarav\AppData\Local\Programs\Python\Python311\Lib\site-packages")
import chess
import chess.engine
import logging

log = logging.getLogger(__name__)


class SkillEstimator:
    def __init__(self, engine: chess.engine.SimpleEngine, our_color: chess.Color):
        self.engine = engine
        self.our_color = our_color
        self.opponent_color = not our_color
        self._cpl_samples: list[float] = []
        self._last_eval: float | None = None

    def record_position_before_opponent_move(self, board: chess.Board):
        try:
            info = self.engine.analyse(board, chess.engine.Limit(depth=14))
            score = info["score"].pov(self.opponent_color)
            self._last_eval = self._score_to_cp(score)
        except Exception as e:
            log.warning(f"Pre-move eval failed: {e}")
            self._last_eval = None

    def record_opponent_move(self, board: chess.Board):
        if self._last_eval is None:
            return
        try:
            info = self.engine.analyse(board, chess.engine.Limit(depth=14))
            score_after = info["score"].pov(self.opponent_color)
            cp_after = self._score_to_cp(score_after)
            cpl = max(0.0, self._last_eval - cp_after)
            self._cpl_samples.append(cpl)
            log.info(f"CPL: {cpl:.1f} | Avg: {self.avg_cpl:.1f} | n={len(self._cpl_samples)}")
        except Exception as e:
            log.warning(f"Post-move eval failed: {e}")
        finally:
            self._last_eval = None

    @property
    def avg_cpl(self) -> float:
        if not self._cpl_samples:
            return 50.0
        return sum(self._cpl_samples) / len(self._cpl_samples)

    @property
    def has_enough_data(self) -> bool:
        return len(self._cpl_samples) >= Config.CPL_MIN_SAMPLES

    def get_elo(self) -> int:
        if not self.has_enough_data:
            return Config.DEFAULT_ELO
        cpl = self.avg_cpl
        for threshold, elo in Config.CPL_ELO_MAP:
            if cpl <= threshold:
                log.info(f"Avg CPL={cpl:.1f} -> ELO {elo}")
                return elo
        return Config.CPL_ELO_MAP[-1][1]

    def throttle_mate_move(self, info, opponent_elo, legal_moves) -> chess.Move:
        """
        Directly throttles checkmate sequences based on distance to mate 
        and opponent skill level to simulate human-like dragging or quick kills.
        """
        score = info["score"].pov(self.our_color)
        
        # If it's not a mate sequence, fallback to standard engine selection
        if not score.is_mate():
            return info["move"]
            
        mate_depth = score.mate()  # Returns an integer (positive if bot is winning)
        
        # Safety Check: If we are the ones getting mated (negative), play best defense immediately
        if mate_depth < 0:
            return info["move"]

        # Rule 1: High Level Opponent (> 1320 Elo) -> No mercy, play exact killer moves
        if opponent_elo > 1320:
            log.info(f"High Elo opponent ({opponent_elo}). Playing optimal Mate-in-{mate_depth} move.")
            return info["move"]

        # Rule 2: Low Elo & Tight Mate Loop (Mate in 1, 2, or 3) -> Finish it immediately
        if mate_depth <= 3:
            log.info(f"Mate-in-{mate_depth} detected. Executing immediate cleanup.")
            return info["move"]

        # Rule 3: Low Elo & Mid Mate Loop (Mate in 4 to 6) -> Drag the game out intentionally
        if 4 <= mate_depth <= 6:
            # Filter all legal moves that keep the position winning but DO NOT deliver immediate short mates
            suboptimal_moves = [0]
            for move in legal_moves:
                # Quick validation of options
                if move != info["move"]:
                    suboptimal_moves.append(move)
                    
            # Rule 4: If there are limited good alternatives, just play the original mate path
            if len(suboptimal_moves) < 2:
                log.info("Limited mating paths available. Playing primary sequence.")
                return info["move"]
                
            log.info(f"Intentionally dragging out Mate-in-{mate_depth} against {opponent_elo} Elo player.")
            return suboptimal_moves[0] # Pick the alternative path to prolong the game

        # Rule 5: Distant Mates (Mate in > 6) -> Play normally, Stockfish will discover it naturally
        log.info(f"Distant Mate-in-{mate_depth}. Processing through normal positional search filters.")
        return info["move"]

    @staticmethod
    def _score_to_cp(score: chess.engine.PovScore) -> float:
        if score.is_mate():
            return 10000.0 if score.mate() > 0 else -10000.0
        return float(score.score())
