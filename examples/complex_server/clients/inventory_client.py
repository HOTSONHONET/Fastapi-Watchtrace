import time
from ..core.decorators import traceable
from ..core.logging_util import log_event

@traceable("inventory_client.fetch_popular_categories")
def fetch_popular_categories() -> list[str]:
    log_event("Calling inventory service")
    time.sleep(0.06)
    return ["electronics", "fitness", "books", "travel"]