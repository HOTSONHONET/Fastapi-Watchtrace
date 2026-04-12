import time
from functools import wraps

from ..core.logging_util import get_logger

logger = get_logger(__name__)


def traced_step(step_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            started = time.perf_counter()
            logger.info("START step=%s func=%s", step_name, func.__name__)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
                logger.info("END step=%s func=%s elapsed_ms=%s", step_name, func.__name__, elapsed_ms)
        return wrapper
    return decorator
