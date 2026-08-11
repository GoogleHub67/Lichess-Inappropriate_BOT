import sys
import os
sys.path.append('../')
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Universal path where Linux installs Stockfish
    STOCKFISH_PATH: str = "/usr/games/stockfish"
    
    # Pulls your secure token from Render's Environment dashboard
    LICHESS_TOKEN: str = os.environ.get("LICHESS_TOKEN", "")
    BOOK_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "books", "gm2001.bin"))

    CPL_MIN_SAMPLES: int = 3
    DEFAULT_ELO: int = 1320

    CPL_ELO_MAP: list[tuple[int, int]] = [
        (15,  2200),
        (25,  2000),
        (40,  1800),
        (60,  1600),
        (90,  1400),
        (130, 1320),
        (999, 1320),
    ]

    ACCEPT_VARIANTS: list[str] = ["standard", "chess960"]
    ACCEPT_TIME_CONTROLS: list[str] = ["bullet", "blitz", "rapid", "classical", "correspondence"]
    DECLINE_RATED: bool = False

    CHAT_GREET: str = "Hi! I'll adapt to your level. Good luck!"
    CHAT_OFF_BOOK: str = "You're out of book! Adapting to your level now."
    CHAT_GG: str = "Good game! Review your moves - that's how you improve."
    CHAT_BLUNDER_DETECTED: str = "Ooof. Big blunder there!"
