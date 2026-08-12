import os
import sys
import asyncio
import threading
import logging
from flask import Flask

# Route packages to match project directory layouts cleanly
src_dir = os.path.dirname(os.path.abspath(__file__))
config_folder_path = os.path.join(src_dir, "config")
src_folder_path = os.path.join(src_dir, "src")

if config_folder_path not in sys.path:
    sys.path.insert(0, config_folder_path)
if src_folder_path not in sys.path:
    sys.path.insert(0, src_folder_path)

from bot import LichessBot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# 🟢 CRITICAL: This variable name MUST match the second half of the gunicorn command (app:app)
app = Flask(__name__)

@app.route('/')
def home():
    return "♟️ Chess Bot Server is Alive and Healthy!"

def run_bot_background():
    log.info("🚀 Launching Lichess Bot stream listener in background thread...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = LichessBot()
    try:
        loop.run_until_complete(bot.start())
    except Exception as e:
        log.error(f"❌ Background bot execution crashed: {e}")

# The 429 Gatekeeper check
if not os.environ.get("WERKZEUG_RUN_MAIN") and threading.active_count() <= 2:
    def delayed_start():
        import time
        time.sleep(2)
        bot_thread = threading.Thread(target=run_bot_background, daemon=True)
        bot_thread.start()

    threading.Thread(target=delayed_start, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
