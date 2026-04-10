from ..core.logging_util import log_event

_CACHE = {}

def get_cache(key: str):
    log_event(f"cache.get({key})")
    return _CACHE.get(key)

def set_cache(key: str, value):
    log_event(f"cache.set({key})")
    _CACHE[key] = value