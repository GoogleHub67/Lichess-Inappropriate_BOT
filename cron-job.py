import os
import sys
import time
import logging
import requests

# Configure logging to output directly to Render's live stream console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Fetch configuration from Environment Variables
HEARTBEAT_URL = os.getenv("HEARTBEAT_URL")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "30"))  # Default: 5 minutes

# Global penalty tracker to add permanent delays to the main loop if rate limits persist
persistent_delay_penalty = 0

def send_heartbeat():
    """Sends a heartbeat ping and penalizes the interval if rate limits are hit."""
    global persistent_delay_penalty
    
    if not HEARTBEAT_URL:
        logging.error("HEARTBEAT_URL environment variable is not set. Exiting.")
        sys.exit(1)

    try:
        response = requests.get(HEARTBEAT_URL, timeout=10)
        
        if response.status_code == 200:
            logging.info("Heartbeat successful (200 OK).")
            return True
            
        elif response.status_code == 429:
            # Increase the permanent sleep penalty by 3 seconds for every 429 encountered
            persistent_delay_penalty += 3
            logging.warning(
                f"Rate limited (429)! Adding 3s penalty. "
                f"Total added loop delay is now +{persistent_delay_penalty}s."
            )
            return False
            
        else:
            logging.warning(f"Heartbeat received unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Heartbeat network connection error: {e}")
        return False

def main():
    """Continuous execution loop that dynamic slows down based on 429 penalties."""
    global persistent_delay_penalty
    
    logging.info(f"Starting adaptive heartbeat tracker. Base Interval: {INTERVAL_SECONDS}s")
    
    # Absolute safety barrier: prevent accidental 0-second script loop spam
    base_interval = max(INTERVAL_SECONDS, 10)

    while True:
        send_heartbeat()
        
        # Calculate final sleep window: Base time + whatever 429 penalties accumulated
        total_sleep_time = base_interval + persistent_delay_penalty
        
        logging.info(f"Waiting {total_sleep_time}s before next heartbeat cycle...")
        time.sleep(total_sleep_time)

if __name__ == "__main__":
    main()
