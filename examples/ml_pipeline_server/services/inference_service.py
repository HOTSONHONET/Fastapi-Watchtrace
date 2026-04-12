from ..core.decorators import traced_step
from ..utils.math_utils import sigmoid
from ..utils.validators import validate_columns_exist


class InferenceService:
    @traced_step("run_inference")
    def predict(self, model_summary: dict, records: list[dict], feature_columns: list[str]) -> list[dict]:
        validate_columns_exist(records, feature_columns)
        weights = [model_summary["weights"][column] for column in feature_columns]
        bias = model_summary["bias"]

        predictions = []
        for record in records:
            vector = [float(record[column]) for column in feature_columns]
            score = sum(v * w for v, w in zip(vector, weights)) + bias
            probability = sigmoid(score)
            predictions.append(
                {
                    "customer_id": record.get("customer_id", "unknown"),
                    "score": round(score, 4),
                    "probability": round(probability, 4),
                    "predicted_label": 1 if probability >= 0.5 else 0,
                }
            )
        return predictions


inference_service = InferenceService()
