#!/usr/bin/env python3
"""
Diagnostic script to test if Stockfish engine is working correctly.
Run this to debug engine initialization and move generation.
"""

import os
import sys
import chess
import chess.engine
import logging
import shutil

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Direct Python to look inside the config directory
src_dir = os.path.dirname(os.path.abspath(__file__))
config_folder_path = os.path.join(src_dir, "config")
if config_folder_path not in sys.path:
    sys.path.insert(0, config_folder_path)

try:
    from bot_config import Config
except ImportError:
    # Fallback if config is structural/named config.py instead of folder wrapper
    try:
        import config as Config
    except ImportError:
        class Config:
            STOCKFISH_PATH = "./stockfish"
            BOOK_PATH = "./assets/books/gm2001.bin"

def test_stockfish_path():
    """Test if Stockfish path is valid and fallback safely"""
    log.info(f"Testing Stockfish path: {Config.STOCKFISH_PATH}")
    
    # Check if the primary configured path exists
    if os.path.exists(Config.STOCKFISH_PATH):
        log.info("✓ Stockfish binary found at configured path")
        return Config.STOCKFISH_PATH
        
    log.error("✗ Stockfish binary NOT found at specified path")
    log.error(f"  Expected: {Config.STOCKFISH_PATH}")
    
    # Render fallback 1: Check if 'stockfish' is globally available in system PATH via apt-get
    global_path = shutil.which("stockfish")
    if global_path:
        log.info(f"✓ Found global Linux Stockfish package at: {global_path}")
        return global_path
    
    # Render fallback 2: Check common relative paths in Ubuntu environments
    alternatives = [
        "stockfish",
        "./stockfish",
        "src/stockfish",
        "/usr/games/stockfish",
        "/usr/bin/stockfish",
        "/app/stockfish"
    ]
    
    log.info("Checking alternative paths...")
    for alt in alternatives:
        # Check relative to current working directory
        full_path = os.path.join(os.getcwd(), alt) if not alt.startswith('/') else alt
        if os.path.exists(full_path):
            log.info(f"✓ Found Stockfish at alternative path: {full_path}")
            return full_path
            
    log.error("✗ Stockfish binary NOT found in any alternative system paths")
    return False

def test_engine_startup(verified_path):
    """Test if engine can be started using the verified path"""
    log.info(f"Attempting to start Stockfish engine using binary: {verified_path}")
    
    try:
        # Give execution permissions just in case it's a raw downloaded binary on Linux
        if os.path.exists(verified_path) and not verified_path.endswith('.exe'):
            try:
                os.chmod(verified_path, 0o755)
            except Exception:
                pass
                
        engine = chess.engine.SimpleEngine.popen_uci(verified_path)
        log.info("✓ Engine started successfully via python-chess popen_uci")
        
        # Test a simple analysis
        board = chess.Board()
        log.info("Testing engine analysis on starting position...")
        result = engine.play(board, chess.engine.Limit(depth=5))
        
        if result and result.move:
            log.info(f"✓ Engine analysis works. Best move: {result.move}")
            log.info(f"  Score: {result.info.get('score', 'Unknown')}")
        else:
            log.error("✗ Engine analysis returned no move")
            engine.quit()
            return False
        
        engine.quit()
        log.info("✓ Engine shutdown cleanly")
        return True
        
    except FileNotFoundError as e:
        log.error(f"✗ Stockfish binary not found: {e}")
        return False
    except Exception as e:
        log.error(f"✗ Engine startup failed: {e}", exc_info=True)
        return False

def test_opening_book():
    """Test if opening book is accessible"""
    log.info(f"Testing opening book path: {Config.BOOK_PATH}")
    
    if os.path.exists(Config.BOOK_PATH):
        log.info("✓ Opening book file found")
        file_size_mb = os.path.getsize(Config.BOOK_PATH) / (1024 * 1024)
        log.info(f"  File size: {file_size_mb:.1f} MB")
        return True
    else:
        log.warning("✗ Opening book file NOT found")
        log.warning(f"  Expected: {Config.BOOK_PATH}")
        return False

def test_elo_configuration(verified_path):
    """Test if engine responds to UCI_Elo configuration"""
    log.info("Testing UCI_LimitStrength and UCI_Elo configuration...")
    
    try:
        engine = chess.engine.SimpleEngine.popen_uci(verified_path)
        
        # Test configuration
        engine.configure({"UCI_LimitStrength": True})
        engine.configure({"UCI_Elo": 1320})
        log.info("✓ Engine accepted UCI_LimitStrength and UCI_Elo settings")
        
        # Analyze with ELO limit
        board = chess.Board()
        result = engine.play(board, chess.engine.Limit(depth=10))
        
        if result and result.move:
            log.info(f"✓ Engine analysis with ELO limit works. Move: {result.move}")
        else:
            log.error("✗ Engine analysis with ELO limit failed")
            engine.quit()
            return False
        
        engine.quit()
        return True
        
    except Exception as e:
        log.error(f"✗ UCI configuration test failed: {e}", exc_info=True)
        return False

def main():
    log.info("=" * 60)
    log.info("LICHESS BOT DIAGNOSTIC TEST (RENDER LINUX COMPATIBLE)")
    log.info("=" * 60)
    
    results = {}
    
    log.info("\n[1/4] Testing Stockfish path...")
    stockfish_path_result = test_stockfish_path()
    
    # Strict boolean assignment fix based on string output
    if stockfish_path_result:
        results['path'] = True
        log.info(f"\n[2/4] Testing engine startup with verified path: {stockfish_path_result}")
        results['startup'] = test_engine_startup(stockfish_path_result)
        
        log.info("\n[3/4] Testing ELO configuration...")
        results['elo'] = test_elo_configuration(stockfish_path_result)
    else:
        results['path'] = False
        results['startup'] = False
        results['elo'] = False
        log.error("\n[2/4 & 4/4] Skipping engine execution tests due to missing binary path.")
    
    log.info("\n[4/4] Testing opening book...")
    results['book'] = test_opening_book()
    
    log.info("\n" + "=" * 60)
    log.info("DIAGNOSTIC SUMMARY")
    log.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        log.info(f"{test_name.upper():15} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        log.info(f"\n🎉 SUCCESS: All diagnostics passed! Update your config path to: {stockfish_path_result}")
        return 0
    else:
        log.error("\n✗ Some diagnostics failed. Render environment is missing Stockfish.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
