import asyncio
import logging
import httpx

log = logging.getLogger(__name__)

class RateLimitStopper:
    """
    Global interceptor for Lichess API outbound traffic.
    Guarantees no 429 loops by enforcing backoffs without dropping/resigning games.
    """
    _lock = asyncio.Lock()
    _backoff_delay = 1.0  # Safe initial baseline

    @classmethod
    async def safe_post(cls, client: httpx.AsyncClient, url: str, data: dict = None, json_data: dict = None) -> httpx.Response:
        """Executes POST requests safely with smart rate limit interception."""
        async with cls._lock:
            while True:
                try:
                    # Execute the outbound move or challenge ping
                    if json_data is not None:
                        response = await client.post(url, json=json_data)
                    else:
                        response = await client.post(url, data=data)

                    # Case A: Connection passes cleanly
                    if response.status_code == 200:
                        cls._backoff_delay = 1.0  # Reset backoff window
                        return response

                    # Case B: Lichess 429 Rate Limit Intercepted
                    elif response.status_code == 429:
                        # Attempt to honor Lichess's explicit Retry-After header window
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            sleep_time = float(retry_after) + 0.5
                            log.warning(f"⚠️ Lichess 429 hit! Honoring Retry-After header. Freezing worker loop for {sleep_time}s...")
                        else:
                            sleep_time = cls._backoff_delay
                            log.warning(f"⚠️ Lichess 429 hit! No header found. Applying backoff sleep for {sleep_time}s...")
                            cls._backoff_delay = min(cls._backoff_delay * 2, 60.0) # Exponential ceiling up to 60s

                        # Freeze the queue, wait it out, and automatically loop to retry the move
                        await asyncio.sleep(sleep_time)
                        continue

                    # Handle standard non-429 payload failures gracefully
                    else:
                        log.error(f"HTTP Server responded with status code {response.status_code} for {url}")
                        return response

                except httpx.RequestError as exc:
                    log.error(f"Network transport connectivity failure tracking request to {url}: {exc}")
                    await asyncio.sleep(2.0)
                    continue
