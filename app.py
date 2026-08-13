import os
import sys
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# 🟢 Pure WSGI Flask instance for Gunicorn to bind cleanly without boot failure
app = Flask(__name__)

@app.route('/')
def home():
    return "♟️ Chess Bot Web Service is Alive and Healthy!"

# Note: Do not spawn raw asyncio loops or engines at the file import level.
# If you need background running, keep app.py strictly as the health-check interface.

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
