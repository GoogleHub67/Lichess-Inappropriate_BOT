import chess
import chess.engine
import logging
from config import Config

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

    @staticmethod
    def _score_to_cp(score: chess.engine.PovScore) -> float:
        if score.is_mate():
            return 10000.0 if score.mate() > 0 else -10000.0
        return float(score.score())