# ML Pipeline Server Example

This example is designed for WatchTower demos. It simulates a layered ML platform with enough depth to generate interesting traces:

- dataset CRUD
- feature preparation
- model training
- evaluation
- model registry stage update
- batch prediction
- monitoring summaries
- prediction batch CRUD

## Folder structure

```text
examples/ml_pipeline_server
├── api
│   └── routes.py
├── clients
│   ├── feature_store_client.py
│   └── model_registry_client.py
├── core
│   ├── cache.py
│   ├── config.py
│   ├── decorators.py
│   └── logging_util.py
├── data
│   └── seed_data.py
├── main.py
├── models
│   └── schemas.py
├── orchestrators
│   └── pipeline_orchestrator.py
├── repositories
│   ├── dataset_repository.py
│   ├── experiment_repository.py
│   └── prediction_repository.py
├── services
│   ├── data_ingestion_service.py
│   ├── evaluation_service.py
│   ├── feature_service.py
│   ├── inference_service.py
│   ├── monitoring_service.py
│   └── training_service.py
├── test
│   └── call_server.py
└── utils
    ├── io_utils.py
    ├── math_utils.py
    ├── retry.py
    ├── transformers.py
    └── validators.py
```

## Run

```bash
cd examples/ml_pipeline_server
pip install -r requirements.txt
uvicorn main:app --reload
```

## Demo flow

1. `GET /api/datasets`
2. `POST /api/datasets`
3. `PUT /api/datasets/{dataset_id}`
4. `POST /api/experiments`
5. `PATCH /api/experiments/{experiment_id}/registry`
6. `POST /api/predictions`
7. `GET /api/predictions/{prediction_batch_id}`
8. Delete resources

Or run the bundled client:

```bash
python test/call_server.py
```

## Why this is good for WatchTower

The training and prediction flows cross multiple layers:

- route -> orchestrator
- orchestrator -> services
- services -> utils / validators / clients
- orchestrator -> repositories
- orchestrator -> model registry client

That creates a visibly richer trace than a simple CRUD server.
