import threading
import os
import sys
import subprocess
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Lichess Bot is active!", 200

def run_bot():
    print("Starting Lichess Bot thread...", flush=True)
    try:
        # Run the script using the same module method mentioned in your README
        subprocess.run([sys.executable, "-m", "src.bot"], check=True)
    except Exception as e:
        print(f"Bot execution stopped with error: {e}", flush=True)

if __name__ == "__main__":
    # Start bot logic on a separate thread so it doesn't block Flask
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Render routes traffic to port 10000 by default for Docker
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
else:
    # This block triggers when Gunicorn loads app:app
    threading.Thread(target=run_bot, daemon=True).start()
