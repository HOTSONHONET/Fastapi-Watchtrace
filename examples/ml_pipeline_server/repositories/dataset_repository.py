from ..data.seed_data import CUSTOMER_CHURN_DATASET
from ..utils.io_utils import generate_id


class DatasetRepository:
    def __init__(self) -> None:
        seed_id = "ds_seed001"
        self._datasets = {
            seed_id: {
                "dataset_id": seed_id,
                "name": "seed_customer_churn",
                "description": "Seed dataset for churn classification demo",
                "source_type": "seed",
                "rows": CUSTOMER_CHURN_DATASET,
            }
        }

    def create(self, payload: dict) -> dict:
        dataset_id = generate_id("ds")
        record = {"dataset_id": dataset_id, **payload}
        self._datasets[dataset_id] = record
        return record

    def list_all(self) -> list[dict]:
        return list(self._datasets.values())

    def get(self, dataset_id: str) -> dict | None:
        return self._datasets.get(dataset_id)

    def update(self, dataset_id: str, payload: dict) -> dict | None:
        existing = self._datasets.get(dataset_id)
        if not existing:
            return None
        existing.update(payload)
        return existing

    def delete(self, dataset_id: str) -> bool:
        return self._datasets.pop(dataset_id, None) is not None


dataset_repository = DatasetRepository()
