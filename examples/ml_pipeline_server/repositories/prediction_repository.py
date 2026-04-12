from ..utils.io_utils import generate_id


class PredictionRepository:
    def __init__(self) -> None:
        self._batches: dict[str, dict] = {}

    def create(self, payload: dict) -> dict:
        batch_id = generate_id("pred")
        record = {"prediction_batch_id": batch_id, **payload}
        self._batches[batch_id] = record
        return record

    def list_all(self) -> list[dict]:
        return list(self._batches.values())

    def get(self, prediction_batch_id: str) -> dict | None:
        return self._batches.get(prediction_batch_id)

    def delete(self, prediction_batch_id: str) -> bool:
        return self._batches.pop(prediction_batch_id, None) is not None


prediction_repository = PredictionRepository()
