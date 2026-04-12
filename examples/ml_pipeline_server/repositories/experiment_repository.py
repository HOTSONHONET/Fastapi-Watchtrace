from ..utils.io_utils import generate_id


class ExperimentRepository:
    def __init__(self) -> None:
        self._experiments: dict[str, dict] = {}

    def create(self, payload: dict) -> dict:
        experiment_id = generate_id("exp")
        record = {"experiment_id": experiment_id, **payload}
        self._experiments[experiment_id] = record
        return record

    def get(self, experiment_id: str) -> dict | None:
        return self._experiments.get(experiment_id)

    def list_all(self) -> list[dict]:
        return list(self._experiments.values())

    def update(self, experiment_id: str, payload: dict) -> dict | None:
        existing = self._experiments.get(experiment_id)
        if not existing:
            return None
        existing.update(payload)
        return existing

    def delete(self, experiment_id: str) -> bool:
        return self._experiments.pop(experiment_id, None) is not None


experiment_repository = ExperimentRepository()
