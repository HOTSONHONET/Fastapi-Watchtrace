from ..core.logging_util import log_event

def average(values):
    log_event("math_utils.average()")
    if not values:
        return 0
    return sum(values) / len(values)

def percentile_bucket(amount: float):
    log_event("math_utils.percentile_bucket()")
    if amount > 1500:
        return "very_high"
    if amount > 800:
        return "high"
    if amount > 300:
        return "medium"
    return "low"