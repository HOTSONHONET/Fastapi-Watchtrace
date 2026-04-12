import time

from ..core.logging_util import get_logger

logger = get_logger(__name__)


class ModelRegistryClient:
    def __init__(self) -> None:
        self._records: dict[str, dict] = {}

    def register_model(self, experiment_id: str, model_summary: dict, metrics: dict) -> dict:
        time.sleep(0.005)
        record = {
            "model_id": f"model_{experiment_id}",
            "experiment_id": experiment_id,
            "stage": "staging",
            "model_summary": model_summary,
            "metrics": metrics,
        }
        self._records[experiment_id] = record
        logger.info("Registered model for experiment_id=%s", experiment_id)
        return record

    def update_stage(self, experiment_id: str, stage: str) -> dict | None:
        record = self._records.get(experiment_id)
        if not record:
            return None
        record["stage"] = stage
        return record

    def get(self, experiment_id: str) -> dict | None:
        return self._records.get(experiment_id)


model_registry_client = ModelRegistryClient()
