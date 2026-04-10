import time
from ..core.decorators import traceable
from ..core.logging_util import log_event

@traceable("payment_client.fetch_payment_score")
def fetch_payment_score(user_id: int) -> dict:
    log_event(f"Calling payment service for user {user_id}")
    time.sleep(0.07)
    return {
        "payment_score": 84 + (user_id % 10),
        "risk_level": "low" if user_id % 2 else "medium",
    }