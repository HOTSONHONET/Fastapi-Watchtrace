from ..core.logging_util import log_event

def validate_user_id(user_id: int):
    log_event(f"validate_user_id({user_id})")
    if user_id <= 0:
        raise ValueError("user_id must be positive")

def validate_flags(include_recommendations: bool, include_analytics: bool):
    log_event("validate_flags()")
    if not isinstance(include_recommendations, bool):
        raise ValueError("include_recommendations must be bool")
    if not isinstance(include_analytics, bool):
        raise ValueError("include_analytics must be bool")