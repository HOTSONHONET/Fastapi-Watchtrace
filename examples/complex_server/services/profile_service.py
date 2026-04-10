from ..core.decorators import traceable
from ..core.cache import get_cache, set_cache
from ..orchestrators.user_orchestrator import fetch_user_context
from ..services.recommendation_service import generate_recommendations
from ..services.analytics_service import compute_user_analytics
from ..utils.validators import validate_user_id, validate_flags
from ..utils.retry import retry_call

@traceable("profile_service.build_user_dashboard")
def build_user_dashboard(
    user_id: int,
    include_recommendations: bool = True,
    include_analytics: bool = True,
):
    validate_user_id(user_id)
    validate_flags(include_recommendations, include_analytics)

    cache_key = f"dashboard:{user_id}:{include_recommendations}:{include_analytics}"
    cached = get_cache(cache_key)
    if cached:
        return {
            **cached,
            "served_from_cache": True,
        }

    user, orders = retry_call(lambda: fetch_user_context(user_id))

    recommendations = []
    analytics = {}

    if include_recommendations:
        recommendations = retry_call(lambda: generate_recommendations(user, orders))

    if include_analytics:
        analytics = retry_call(lambda: compute_user_analytics(user_id, orders))

    response = {
        "user": user,
        "orders": orders,
        "recommendations": recommendations,
        "analytics": analytics,
        "served_from_cache": False,
    }

    set_cache(cache_key, response)
    return response