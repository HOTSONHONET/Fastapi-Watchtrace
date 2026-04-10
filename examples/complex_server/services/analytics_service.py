from ..core.decorators import traceable
from ..utils.math_utils import average
from ..clients.payment_client import fetch_payment_score

@traceable("analytics_service.compute_user_analytics")
def compute_user_analytics(user_id: int, orders: list[dict]) -> dict:
    amounts = [o["amount"] for o in orders]
    payment_data = fetch_payment_score(user_id)

    return {
        "avg_order_value": average(amounts),
        "max_order_value": max(amounts) if amounts else 0,
        "min_order_value": min(amounts) if amounts else 0,
        "payment_score": payment_data["payment_score"],
        "risk_level": payment_data["risk_level"],
    }