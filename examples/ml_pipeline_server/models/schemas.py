from typing import Any, Optional

from pydantic import BaseModel, Field


class DatasetCreateRequest(BaseModel):
    name: str
    description: str
    source_type: str = "inline"
    rows: list[dict[str, Any]] = Field(default_factory=list)


class DatasetResponse(BaseModel):
    dataset_id: str
    name: str
    description: str
    source_type: str
    rows: list[dict[str, Any]]
    row_count: int
    stats: dict[str, Any]


class TrainingConfig(BaseModel):
    target_column: str = "label"
    feature_columns: list[str] = Field(default_factory=lambda: ["age", "income", "tenure_months"])
    algorithm: str = "logistic_regression"
    test_size: float = 0.2
    normalize: bool = True


class ExperimentCreateRequest(BaseModel):
    dataset_id: str
    experiment_name: str
    config: TrainingConfig


class ConfusionMatrix(BaseModel):
    tp: int
    tn: int
    fp: int
    fn: int


class ExperimentMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    avg_probability: float
    confusion_matrix: ConfusionMatrix

class ExperimentResponse(BaseModel):
    experiment_id: str
    dataset_id: str
    experiment_name: str
    status: str
    metrics: ExperimentMetrics
    model_summary: dict[str, Any]
    registry_record: dict[str, Any]


class PredictionRequest(BaseModel):
    experiment_id: str
    records: list[dict[str, Any]]


class PredictionResponse(BaseModel):
    prediction_batch_id: str
    experiment_id: str
    predictions: list[dict[str, Any]]
    monitoring: dict[str, Any]


class DatasetUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rows: Optional[list[dict[str, Any]]] = None


class RegistryUpdateRequest(BaseModel):
    stage: str


class GenericDeleteResponse(BaseModel):
    deleted: bool
    resource_id: str
    resource_type: str
