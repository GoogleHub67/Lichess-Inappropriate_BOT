import logging
import chess
import chess.variant

log = logging.getLogger(__name__)

# List of variants the bot is strictly NOT willing to play
UNWANTED_VARIANTS = {
    "standard",       # Already covered elsewhere
    "chess960",       # Already covered elsewhere
    "fromPosition"    # Already covered elsewhere
}

# Mapping of valid non-standard Lichess variant keys to Fairy-Stockfish UCI string tags
# Includes: King of the Hill, Three-Check, Crazyhouse, Antichess, Atomic, Horde, Racing Kings
VARIANT_UCI_MAPPINGS = {
    "kingOfTheHill": "kingofthehill",
    "threeCheck": "3check",
    "crazyhouse": "crazyhouse",
    "antichess": "antichess",
    "atomic": "atomic",
    "horde": "horde",
    "racingKings": "racingkings"
}

def is_playable_variant(variant_key: str) -> bool:
    """Checks if the incoming challenge format belongs to our new variant list."""
    return variant_key in VARIANT_UCI_MAPPINGS

def should_decline_variant(variant_key: str) -> bool:
    """Returns True if the format is standard or explicitly blocked."""
    return variant_key in UNWANTED_VARIANTS

def setup_variant_board(engine, variant_key: str):
    """
    Configures Fairy-Stockfish with the proper variant setting 
    and returns the matching python-chess rule-enforcing board framework.
    """
    uci_variant_name = VARIANT_UCI_MAPPINGS.get(variant_key)
    if not uci_variant_name:
        log.warning(f"Unknown variant key '{variant_key}'. Defaulting to standard rules.")
        return chess.Board()

    try:
        log.info(f"♞ Configuring Fairy-Stockfish engine for variant: {uci_variant_name}")
        
        # Inject the variant setup configuration option token directly into the engine instance binary
        engine.configure({"UCI_Variant": uci_variant_name})
        
        # Dynamically lookup and initialize the correct rule structure board (e.g. chess.variant.AtomicBoard())
        variant_board_class = chess.variant.find_variant(uci_variant_name)
        return variant_board_class()
        
    except Exception as e:
        log.error(f"Fairy-Stockfish variant initialization crash sequence: {e}")
        return chess.Board()
