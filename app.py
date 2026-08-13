import os
import sys
import asyncio
import threading
import logging
import chess.engine
from http.server import HTTPServer, BaseHTTPRequestHandler

src_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.join(src_dir, "config") not in sys.path: sys.path.insert(0, os.path.join(src_dir, "config"))
if os.path.join(src_dir, "src") not in sys.path: sys.path.insert(0, os.path.join(src_dir, "src"))

from bot import LichessBot
from bot_config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Chess Bot is Alive and Running!")
    def log_message(self, format, *args):
        return

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def run_bot_loop():
    log.info("🚀 Launching background event loop & loading Stockfish...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Spawn global engine instance once
        engine = chess.engine.SimpleEngine.popen_uci(Config.STOCKFISH_PATH)
        log.info("✅ GLOBAL STOCKFISH LOADED SUCCESSFULLY")
        
        # 🟢 Pass engine instance explicitly here!
        bot = LichessBot(engine=engine)
        loop.run_until_complete(bot.start())
    except Exception as e:
        log.error(f"❌ Bot loop crashed: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_bot_loop, daemon=True).start()
    run_http_server()
