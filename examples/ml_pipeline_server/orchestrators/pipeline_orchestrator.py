from ..clients.model_registry_client import model_registry_client
from ..core.decorators import traced_step
from ..repositories.dataset_repository import dataset_repository
from ..repositories.experiment_repository import experiment_repository
from ..repositories.prediction_repository import prediction_repository
from ..services.data_ingestion_service import data_ingestion_service
from ..services.evaluation_service import evaluation_service
from ..services.feature_service import feature_service
from ..services.inference_service import inference_service
from ..services.monitoring_service import monitoring_service
from ..services.training_service import training_service


class PipelineOrchestrator:
    @traced_step("create_dataset_flow")
    def create_dataset(self, payload: dict) -> dict:
        enriched = data_ingestion_service.ingest(payload)
        saved = dataset_repository.create(enriched)
        return saved

    @traced_step("get_dataset_flow")
    def get_dataset(self, dataset_id: str) -> dict | None:
        return dataset_repository.get(dataset_id)

    @traced_step("list_datasets_flow")
    def list_datasets(self) -> list[dict]:
        return dataset_repository.list_all()

    @traced_step("update_dataset_flow")
    def update_dataset(self, dataset_id: str, payload: dict) -> dict | None:
        existing = dataset_repository.get(dataset_id)
        if not existing:
            return None

        merged = {
            "name": payload.get("name") or existing["name"],
            "description": payload.get("description") or existing["description"],
            "source_type": existing["source_type"],
            "rows": payload.get("rows") if payload.get("rows") is not None else existing["rows"],
        }
        enriched = data_ingestion_service.ingest(merged)
        return dataset_repository.update(dataset_id, enriched)

    @traced_step("delete_dataset_flow")
    def delete_dataset(self, dataset_id: str) -> bool:
        return dataset_repository.delete(dataset_id)

    @traced_step("train_pipeline_flow")
    def create_experiment(self, dataset_id: str, experiment_name: str, config: dict) -> dict:
        dataset = dataset_repository.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")

        prepared = feature_service.prepare(
            rows=dataset["rows"],
            feature_columns=config["feature_columns"],
            target_column=config["target_column"],
            normalize=config["normalize"],
        )
        model_summary = training_service.train(
            X=prepared["X"],
            y=prepared["y"],
            feature_columns=config["feature_columns"],
            algorithm=config["algorithm"],
        )
        metrics = evaluation_service.evaluate(
            model=model_summary,
            X=prepared["X"],
            y=prepared["y"],
            feature_columns=config["feature_columns"],
        )
        experiment = experiment_repository.create(
            {
                "dataset_id": dataset_id,
                "experiment_name": experiment_name,
                "status": "completed",
                "metrics": metrics,
                "model_summary": {
                    **model_summary,
                    "feature_columns": config["feature_columns"],
                    "normalization_stats": prepared["normalization_stats"],
                    "feature_metadata": prepared["metadata"],
                },
            }
        )
        registry_record = model_registry_client.register_model(
            experiment_id=experiment["experiment_id"],
            model_summary=experiment["model_summary"],
            metrics=metrics,
        )
        experiment["registry_record"] = registry_record
        return experiment

    @traced_step("list_experiments_flow")
    def list_experiments(self) -> list[dict]:
        return experiment_repository.list_all()

    @traced_step("get_experiment_flow")
    def get_experiment(self, experiment_id: str) -> dict | None:
        experiment = experiment_repository.get(experiment_id)
        if experiment:
            experiment["registry_record"] = model_registry_client.get(experiment_id)
        return experiment

    @traced_step("delete_experiment_flow")
    def delete_experiment(self, experiment_id: str) -> bool:
        return experiment_repository.delete(experiment_id)

    @traced_step("update_registry_stage_flow")
    def update_registry_stage(self, experiment_id: str, stage: str) -> dict | None:
        return model_registry_client.update_stage(experiment_id, stage)

    @traced_step("prediction_pipeline_flow")
    def create_prediction_batch(self, experiment_id: str, records: list[dict]) -> dict:
        experiment = experiment_repository.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")

        feature_columns = experiment["model_summary"]["feature_columns"]
        predictions = inference_service.predict(
            model_summary=experiment["model_summary"],
            records=records,
            feature_columns=feature_columns,
        )
        monitoring = monitoring_service.summarize_prediction_batch(predictions)
        batch = prediction_repository.create(
            {
                "experiment_id": experiment_id,
                "predictions": predictions,
                "monitoring": monitoring,
            }
        )
        return batch

    @traced_step("list_predictions_flow")
    def list_prediction_batches(self) -> list[dict]:
        return prediction_repository.list_all()

    @traced_step("get_prediction_flow")
    def get_prediction_batch(self, prediction_batch_id: str) -> dict | None:
        return prediction_repository.get(prediction_batch_id)

    @traced_step("delete_prediction_flow")
    def delete_prediction_batch(self, prediction_batch_id: str) -> bool:
        return prediction_repository.delete(prediction_batch_id)


pipeline_orchestrator = PipelineOrchestrator()
