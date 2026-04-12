from collections import Counter

from ..core.decorators import traced_step
from ..utils.math_utils import mean


class MonitoringService:
    @traced_step("collect_monitoring")
    def summarize_prediction_batch(self, predictions: list[dict]) -> dict:
        probs = [p["probability"] for p in predictions]
        labels = [p["predicted_label"] for p in predictions]
        return {
            "avg_probability": round(mean(probs), 4) if probs else 0.0,
            "predicted_label_distribution": dict(Counter(labels)),
            "high_risk_count": sum(1 for p in predictions if p["probability"] > 0.75),
        }


monitoring_service = MonitoringService()
