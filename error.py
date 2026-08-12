import os
import sys
import asyncio
import logging

# 🟢 FIX: Path injection MUST be at the top before importing custom modules
src_dir = os.path.dirname(os.path.abspath(__file__))
config_folder_path = os.path.join(src_dir, "config")
if config_folder_path not in sys.path:
    sys.path.insert(0, config_folder_path)

# Standard chess and project module imports
import chess
import chess.engine
from bot_config import Config
from bot import LichessBot  

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

async def run_diagnostics():
    log.info("=" * 60)
    log.info("LICHESS BOT DIAGNOSTIC TEST (RENDER LINUX COMPATIBLE)")
    log.info("=" * 60)

    path_pass = False
    startup_pass = False
    elo_pass = False
    book_pass = False

    # [1/4] Testing Stockfish path
    log.info("\n[1/4] Testing Stockfish path...")
    log.info(f"Testing Stockfish path: {Config.STOCKFISH_PATH}")
    if os.path.exists(Config.STOCKFISH_PATH):
        log.info("✓ Stockfish binary found at configured path")
        path_pass = True
    else:
        log.warning("✗ Stockfish binary NOT found at path")

    # [2/4] Testing engine startup
    if path_pass:
        log.info("\n[2/4] Testing engine startup...")
        try:
            engine = chess.engine.SimpleEngine.popen_uci(Config.STOCKFISH_PATH)
            log.info("✓ Engine started successfully via python-chess popen_uci")
            
            log.info("Testing engine analysis on starting position...")
            board = chess.Board()
            info = engine.analyse(board, chess.engine.Limit(depth=5))
            log.info(f"✓ Engine analysis works. Best move: {info.get('move')}")
            
            engine.quit()
            log.info("✓ Engine shutdown cleanly")
            startup_pass = True
        except Exception as e:
            log.error(f"✗ Engine startup or analysis failed: {e}")

    # [3/4] Testing ELO configuration
    if startup_pass:
        log.info("\n[3/4] Testing ELO configuration...")
        try:
            engine = chess.engine.SimpleEngine.popen_uci(Config.STOCKFISH_PATH)
            engine.configure({"UCI_LimitStrength": True, "UCI_Elo": Config.DEFAULT_ELO})
            log.info("✓ Engine accepted UCI_LimitStrength and UCI_Elo settings")
            engine.quit()
            elo_pass = True
        except Exception as e:
            log.error(f"✗ ELO configuration failed: {e}")

    # [4/4] Testing opening book
    log.info("\n[4/4] Testing opening book...")
    log.info(f"Testing opening book path: {Config.BOOK_PATH}")
    if os.path.exists(Config.BOOK_PATH):
        log.info("✓ Opening book file found and verified")
        book_pass = True
    else:
        log.warning("✗ Opening book file NOT found")
        log.warning(f"  Expected: {Config.BOOK_PATH}")

    log.info("\n" + "=" * 60)
    log.info("DIAGNOSTIC SUMMARY")
    log.info("=" * 60)
    log.info(f"PATH            {'✓ PASS' if path_pass else '✗ FAIL'}")
    log.info(f"STARTUP         {'✓ PASS' if startup_pass else '✗ FAIL'}")
    log.info(f"ELO             {'✓ PASS' if elo_pass else '✗ FAIL'}")
    log.info(f"BOOK            {'✓ PASS' if book_pass else '✗ FAIL'}")

    # Only crash deployment if Stockfish itself breaks.
    # A missing opening book is non-critical and will proceed anyway.
    if not path_pass or not startup_pass or not elo_pass:
        log.error("\n✗ Critical diagnostics failed. Render environment is missing Stockfish or misconfigured.")
        sys.exit(1)
        
    if not book_pass:
        log.warning("\n⚠️ Warning: Opening book missing, but engine is healthy. Running bot without a book.")
    else:
        log.info("\n🎉 All systems operational! Ready to play.")

    log.info("🚀 Booting main Lichess bot client execution loop...\n")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_diagnostics())
    
    # Hand over control to the main bot streaming event loop
    bot = LichessBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        log.info("Bot stopped manually. GG.")
