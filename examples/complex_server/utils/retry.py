import time
from ..core.logging_util import log_event

def retry_call(func, retries=2, delay=0.05):
    last_error = None
    for attempt in range(retries + 1):
        try:
            log_event(f"retry_call attempt={attempt}")
            return func()
        except Exception as e:
            last_error = e
            time.sleep(delay)
    raise last_error