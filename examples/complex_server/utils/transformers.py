from ..core.logging_util import log_event
from ..utils.math_utils import percentile_bucket

def enrich_user(user: dict) -> dict:
    log_event("transformers.enrich_user()")
    return {
        **user,
        "display_name": f"{user['name']} ({user['tier'].upper()})",
        "age_band": "young" if user["age"] < 30 else "adult",
    }

def enrich_orders(orders: list[dict]) -> list[dict]:
    log_event("transformers.enrich_orders()")
    enriched = []
    for order in orders:
        enriched.append({
            **order,
            "bucket": percentile_bucket(order["amount"]),
            "is_large": order["amount"] > 1000,
        })
    return enriched

def build_summary(user: dict, orders: list[dict]) -> dict:
    log_event("transformers.build_summary()")
    total = sum(o["amount"] for o in orders)
    return {
        "user_name": user["name"],
        "order_count": len(orders),
        "total_spent": total,
    }