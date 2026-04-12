from fastapi import APIRouter, HTTPException

from ..models.schemas import (
    DatasetCreateRequest,
    DatasetResponse,
    DatasetUpdateRequest,
    ExperimentCreateRequest,
    ExperimentResponse,
    GenericDeleteResponse,
    PredictionRequest,
    PredictionResponse,
    RegistryUpdateRequest,
)
from ..orchestrators.pipeline_orchestrator import pipeline_orchestrator

router = APIRouter()


@router.get("/datasets")
async def list_datasets():
    return pipeline_orchestrator.list_datasets()


@router.post("/datasets", response_model=DatasetResponse)
async def create_dataset(payload: DatasetCreateRequest):
    try:
        return pipeline_orchestrator.create_dataset(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    dataset = pipeline_orchestrator.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.put("/datasets/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(dataset_id: str, payload: DatasetUpdateRequest):
    try:
        updated = pipeline_orchestrator.update_dataset(dataset_id, payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not updated:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return updated


@router.delete("/datasets/{dataset_id}", response_model=GenericDeleteResponse)
async def delete_dataset(dataset_id: str):
    deleted = pipeline_orchestrator.delete_dataset(dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"deleted": True, "resource_id": dataset_id, "resource_type": "dataset"}


@router.get("/experiments")
async def list_experiments():
    return pipeline_orchestrator.list_experiments()


@router.post("/experiments", response_model=ExperimentResponse)
async def create_experiment(payload: ExperimentCreateRequest):
    try:
        return pipeline_orchestrator.create_experiment(
            dataset_id=payload.dataset_id,
            experiment_name=payload.experiment_name,
            config=payload.config.model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: str):
    experiment = pipeline_orchestrator.get_experiment(experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.patch("/experiments/{experiment_id}/registry")
async def update_registry_stage(experiment_id: str, payload: RegistryUpdateRequest):
    updated = pipeline_orchestrator.update_registry_stage(experiment_id, payload.stage)
    if not updated:
        raise HTTPException(status_code=404, detail="Registry record not found")
    return updated


@router.delete("/experiments/{experiment_id}", response_model=GenericDeleteResponse)
async def delete_experiment(experiment_id: str):
    deleted = pipeline_orchestrator.delete_experiment(experiment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {"deleted": True, "resource_id": experiment_id, "resource_type": "experiment"}


@router.get("/predictions")
async def list_predictions():
    return pipeline_orchestrator.list_prediction_batches()


@router.post("/predictions", response_model=PredictionResponse)
async def create_prediction_batch(payload: PredictionRequest):
    try:
        return pipeline_orchestrator.create_prediction_batch(
            experiment_id=payload.experiment_id,
            records=payload.records,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/predictions/{prediction_batch_id}")
async def get_prediction_batch(prediction_batch_id: str):
    batch = pipeline_orchestrator.get_prediction_batch(prediction_batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Prediction batch not found")
    return batch


@router.delete("/predictions/{prediction_batch_id}", response_model=GenericDeleteResponse)
async def delete_prediction_batch(prediction_batch_id: str):
    deleted = pipeline_orchestrator.delete_prediction_batch(prediction_batch_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prediction batch not found")
    return {"deleted": True, "resource_id": prediction_batch_id, "resource_type": "prediction_batch"}
