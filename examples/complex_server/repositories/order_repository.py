import time
from ..data.seed_data import ORDERS
from ..core.decorators import traceable
from ..core.logging_util import log_event

@traceable("order_repository.get_orders_for_user")
def get_orders_for_user(user_id: int):
    log_event(f"Fetching orders for user {user_id}")
    time.sleep(0.05)
    return ORDERS.get(user_id, [])