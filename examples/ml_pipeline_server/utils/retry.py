import time
from functools import wraps


def retry(times: int = 2, delay_s: float = 0.01):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # pragma: no cover - demo retry
                    last_error = exc
                    time.sleep(delay_s)
            raise last_error
        return wrapper
    return decorator
