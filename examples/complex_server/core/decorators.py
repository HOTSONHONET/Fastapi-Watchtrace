import time
from functools import wraps
from ..core.logging_util import log_event

def traceable(name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            log_event(f"ENTER {name}")
            try:
                return func(*args, **kwargs)
            finally:
                duration = (time.perf_counter() - start) * 1000
                log_event(f"EXIT {name} took {duration:.2f} ms")
        return wrapper
    return decorator