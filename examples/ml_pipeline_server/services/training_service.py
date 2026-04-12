from ..core.decorators import traced_step
from ..utils.math_utils import mean, safe_divide


class TrainingService:
    @traced_step("train_model")
    def train(self, X: list[list[float]], y: list[int], feature_columns: list[str], algorithm: str) -> dict:
        positive_rows = [row for row, label in zip(X, y) if label == 1]
        negative_rows = [row for row, label in zip(X, y) if label == 0]

        positive_centroid = [round(mean([row[i] for row in positive_rows]), 4) for i in range(len(feature_columns))]
        negative_centroid = [round(mean([row[i] for row in negative_rows]), 4) for i in range(len(feature_columns))]

        weights = [round(p - n, 4) for p, n in zip(positive_centroid, negative_centroid)]
        bias = round(mean(y) - 0.5, 4)

        return {
            "algorithm": algorithm,
            "weights": dict(zip(feature_columns, weights)),
            "bias": bias,
            "training_summary": {
                "positive_rate": round(mean(y), 4),
                "class_balance_ratio": round(safe_divide(sum(y), len(y) - sum(y)), 4),
            },
        }


training_service = TrainingService()
