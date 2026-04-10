from ..core.decorators import traceable
from ..repositories.user_repository import get_user_by_id
from ..repositories.order_repository import get_orders_for_user
from ..utils.transformers import enrich_user, enrich_orders

@traceable("user_orchestrator.fetch_user_context")
def fetch_user_context(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    orders = get_orders_for_user(user_id)

    enriched_user = enrich_user(user)
    enriched_orders = enrich_orders(orders)

    return enriched_user, enriched_orders