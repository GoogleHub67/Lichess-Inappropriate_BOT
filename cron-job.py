import os
import sys
import time
import logging
import requests

# Configure logging to output directly to Render's live log stream
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Fetch configuration from Environment Variables
HEARTBEAT_URL = os.getenv("HEARTBEAT_URL")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "300"))  # Default: 5 minutes

def send_heartbeat():
    """Sends a ping to the tracking endpoint and logs the result."""
    if not HEARTBEAT_URL:
        logging.error("HEARTBEAT_URL environment variable is not set. Exiting.")
        sys.exit(1)

    try:
        # Strict timeout prevents Render worker threads from hanging indefinitely
        response = requests.get(HEARTBEAT_URL, timeout=10)
        
        if response.status_code == 200:
            logging.info(f"Heartbeat successful. Status code: {response.status_code}")
        else:
            logging.warning(f"Heartbeat received unexpected status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Heartbeat failed! Connection error: {e}")

def main():
    """Continuous execution loop for background tracking."""
    logging.info(f"Starting cron-job heartbeat tracker. Interval: {INTERVAL_SECONDS}s")
    
    while True:
        send_heartbeat()
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
