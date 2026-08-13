import os
import sys
import threading
import logging
import asyncio
from flask import Flask

src_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.join(src_dir, "config") not in sys.path: sys.path.insert(0, os.path.join(src_dir, "config"))
if os.path.join(src_dir, "src") not in sys.path: sys.path.insert(0, os.path.join(src_dir, "src"))

from bot import LichessBot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

# Track state to ensure the bot logs into Lichess only once per container boot
bot_started = False
bot_lock = threading.Lock()

def start_bot_thread():
    global bot_started
    with bot_lock:
        if not bot_started:
            bot_started = True
            log.info("🚀 Booting Lichess Bot login stream from web trigger...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            bot = LichessBot()
            try:
                loop.run_until_complete(bot.start())
            except Exception as e:
                log.error(f"❌ Bot loop error: {e}")

@app.route('/')
def home():
    # Automatically kickstart/wake the bot thread the moment a ping hits the web URL
    threading.Thread(target=start_bot_thread, daemon=True).start()
    return "♟️ Chess Bot Web Service is Alive and Logging In!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
