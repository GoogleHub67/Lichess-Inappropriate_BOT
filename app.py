import os
import sys
import asyncio
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# Route packages to match project directory layouts cleanly
src_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.join(src_dir, "config") not in sys.path: sys.path.insert(0, os.path.join(src_dir, "config"))
if os.path.join(src_dir, "src") not in sys.path: sys.path.insert(0, os.path.join(src_dir, "src"))

from bot import LichessBot

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Chess Bot is Alive and Running!")
    def log_message(self, format, *args):
        return  # Suppress noisy HTTP access logs

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    log.info(f"📡 Native HTTP health-check server listening on port {port}...")
    server.serve_forever()

def run_bot_loop():
    log.info("🚀 Launching Lichess bot event stream loop...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = LichessBot()
    try:
        loop.run_until_complete(bot.start())
    except Exception as e:
        log.error(f"❌ Bot loop crashed: {e}")

if __name__ == "__main__":
    # 1. Start the bot on a dedicated daemon thread
    threading.Thread(target=run_bot_loop, daemon=True).start()
    
    # 2. Run the blocking HTTP health-check server on the main thread
    run_http_server()
