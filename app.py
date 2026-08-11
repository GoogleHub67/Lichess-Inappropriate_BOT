import threading
import os
import sys
import subprocess
import traceback
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Lichess Bot is active!", 200

def run_bot():
    print("Starting Lichess Bot thread...", flush=True)
    try:
        # We add capture_output=True to catch the actual error stream
        result = subprocess.run(
            [sys.executable, "-m", "src.bot"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(result.stdout, flush=True)
    except subprocess.CalledProcessError as e:
        print("--- BOT CRASHED ---", flush=True)
        print(f"STDOUT:\n{e.stdout}", flush=True)
        print(f"STDERR:\n{e.stderr}", flush=True)
    except Exception as e:
        print(f"General error: {e}", flush=True)
        traceback.print_exc()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
else:
    threading.Thread(target=run_bot, daemon=True).start()
