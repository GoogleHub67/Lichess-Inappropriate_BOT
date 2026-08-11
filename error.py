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

from bot_config import Config

def test_stockfish_path():
    """Test if Stockfish path is valid"""
    log.info(f"Testing Stockfish path: {Config.STOCKFISH_PATH}")
    
    if os.path.exists(Config.STOCKFISH_PATH):
        log.info("✓ Stockfish binary found at path")
        return True
    else:
        log.error("✗ Stockfish binary NOT found at specified path")
        log.error(f"  Expected: {Config.STOCKFISH_PATH}")
        
        # Try alternative paths
        alternatives = [
            "/usr/games/stockfish",
            "/usr/bin/stockfish",
            "stockfish",
            "./bin/stockfish",
            "/app/bin/stockfish"
        ]
        
        log.info("Checking alternative paths...")
        for alt in alternatives:
            if os.path.exists(alt):
                log.info(f"✓ Found Stockfish at: {alt}")
                return alt
        
        return False

def test_engine_startup():
    """Test if engine can be started"""
    log.info("Attempting to start Stockfish engine...")
    
    try:
        engine = chess.engine.SimpleEngine.popen_uci(Config.STOCKFISH_PATH)
        log.info("✓ Engine started successfully")
        
        # Test a simple analysis
        board = chess.Board()
        log.info("Testing engine analysis on starting position...")
        info = engine.analyse(board, chess.engine.Limit(depth=5))
        
        if info and "move" in info:
            log.info(f"✓ Engine analysis works. Best move: {info['move']}")
            log.info(f"  Score: {info['score']}")
        else:
            log.error("✗ Engine analysis returned no move")
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

def test_elo_configuration():
    """Test if engine responds to UCI_Elo configuration"""
    log.info("Testing UCI_LimitStrength and UCI_Elo configuration...")
    
    try:
        engine = chess.engine.SimpleEngine.popen_uci(Config.STOCKFISH_PATH)
        
        # Test configuration
        engine.configure({
            "UCI_LimitStrength": True,
            "UCI_Elo": 1320
        })
        log.info("✓ Engine accepted UCI_LimitStrength and UCI_Elo settings")
        
        # Analyze with ELO limit
        board = chess.Board()
        info = engine.analyse(board, chess.engine.Limit(depth=10))
        
        if info and "move" in info:
            log.info(f"✓ Engine analysis with ELO limit works. Move: {info['move']}")
        else:
            log.error("✗ Engine analysis with ELO limit failed")
            return False
        
        engine.quit()
        return True
        
    except Exception as e:
        log.error(f"✗ UCI configuration test failed: {e}", exc_info=True)
        return False

def main():
    log.info("=" * 60)
    log.info("LICHESS BOT DIAGNOSTIC TEST")
    log.info("=" * 60)
    
    results = {}
    
    log.info("\n[1/4] Testing Stockfish path...")
    results['path'] = test_stockfish_path()
    
    log.info("\n[2/4] Testing engine startup...")
    results['startup'] = test_engine_startup()
    
    log.info("\n[3/4] Testing opening book...")
    results['book'] = test_opening_book()
    
    log.info("\n[4/4] Testing ELO configuration...")
    results['elo'] = test_elo_configuration()
    
    log.info("\n" + "=" * 60)
    log.info("DIAGNOSTIC SUMMARY")
    log.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        log.info(f"{test_name.upper():15} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        log.info("\n✓ All diagnostics passed! Engine should work correctly.")
        return 0
    else:
        log.error("\n✗ Some diagnostics failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
