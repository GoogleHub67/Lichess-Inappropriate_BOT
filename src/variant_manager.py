import chess
import chess.variant # Required for variant board rule logic structures

# Map incoming Lichess variant keys to Fairy-Stockfish UCI string specs
LICHESS_VARIANT_MAPPINGS = {
    "standard": "chess",
    "chess960": "chess960",
    "crazyhouse": "crazyhouse",
    "antichess": "antichess",
    "atomic": "atomic",
    "horde": "horde",
    "kingOfTheHill": "kingofthehill",
    "racingKings": "racingkings",
    "threeCheck": "3check"
}

def setup_variant_engine(engine_instance, lichess_variant_key):
    """
    Injects the target variant configuration parameters straight into Fairy-Stockfish
    and returns the correct python-chess variant board object framework.
    """
    # Fallback to standard chess if variant is unknown
    uci_variant = LICHESS_VARIANT_MAPPINGS.get(lichess_variant_key, "chess")
    
    try:
        print(f"⚙️ Sending UCI_Variant setup token to Fairy-Stockfish: {uci_variant}")
        
        # Configure the running engine instance binary
        engine_instance.configure({"UCI_Variant": uci_variant})
        
        # Dynamically load the correct internal rule-checker board state class
        if uci_variant == "chess":
            return chess.Board()
        else:
            return chess.variant.find_variant(uci_variant)()
            
    except Exception as e:
        print(f"❌ Variant Engine Setup Failed: {e}. Falling back to standard rules.")
        return chess.Board()
