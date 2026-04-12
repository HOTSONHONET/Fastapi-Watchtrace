from ..core.decorators import traced_step
from ..utils.math_utils import mean, safe_divide, sigmoid


class EvaluationService:
    @traced_step("evaluate_model")
    def evaluate(self, model: dict, X: list[list[float]], y: list[int], feature_columns: list[str]) -> dict:
        weights = [model["weights"][column] for column in feature_columns]
        bias = model["bias"]

        probabilities = []
        predictions = []
        for row in X:
            score = sum(v * w for v, w in zip(row, weights)) + bias
            prob = sigmoid(score)
            pred = 1 if prob >= 0.5 else 0
            probabilities.append(prob)
            predictions.append(pred)

        tp = sum(1 for p, t in zip(predictions, y) if p == 1 and t == 1)
        tn = sum(1 for p, t in zip(predictions, y) if p == 0 and t == 0)
        fp = sum(1 for p, t in zip(predictions, y) if p == 1 and t == 0)
        fn = sum(1 for p, t in zip(predictions, y) if p == 0 and t == 1)

        accuracy = safe_divide(tp + tn, len(y))
        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        avg_probability = mean(probabilities)

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "avg_probability": round(avg_probability, 4),
            "confusion_matrix": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        }


evaluation_service = EvaluationService()
