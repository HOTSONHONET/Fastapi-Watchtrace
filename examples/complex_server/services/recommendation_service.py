from ..core.decorators import traceable
from ..clients.inventory_client import fetch_popular_categories
from ..utils.transformers import build_summary

@traceable("recommendation_service.generate_recommendations")
def generate_recommendations(user: dict, orders: list[dict]) -> list[str]:
    popular_categories = fetch_popular_categories()
    summary = build_summary(user, orders)

    user_categories = {o["category"] for o in orders}
    recommendations = []

    for category in popular_categories:
        if category not in user_categories:
            recommendations.append(f"Try {category}")

    if summary["total_spent"] > 2000:
        recommendations.append("Offer premium loyalty coupon")

    return recommendations[:5]