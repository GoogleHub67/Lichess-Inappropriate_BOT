import os
import sys
import asyncio
import threading
import logging
import chess.engine
from flask import Flask

src_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.join(src_dir, "config") not in sys.path: sys.path.insert(0, os.path.join(src_dir, "config"))
if os.path.join(src_dir, "src") not in sys.path: sys.path.insert(0, os.path.join(src_dir, "src"))

from bot import LichessBot
from bot_config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
global_engine = None  # 🟢 Global reference container

@app.route('/')
def home():
    return "♟️ Shared Engine Server is Alive!"

def run_bot_background():
    global global_engine
    log.info("🚀 Launching global engine instance...")
    
    # Create a dedicated event loop for background systems
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Spawn ONE single Stockfish instance for the entire app life
        global_engine = chess.engine.SimpleEngine.popen_uci(Config.STOCKFISH_PATH)
        log.info("✅ GLOBAL STOCKFISH LOADED SUCCESSFULLY")
        
        # Pass the global engine reference into your bot
        bot = LichessBot(engine=global_engine)
        loop.run_until_complete(bot.start())
    except Exception as e:
        log.error(f"❌ Background crash: {e}")
    finally:
        if global_engine:
            try: global_engine.quit()
            except: pass

if not os.environ.get("WERKZEUG_RUN_MAIN") and threading.active_count() <= 2:
    threading.Thread(target=run_bot_background, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
