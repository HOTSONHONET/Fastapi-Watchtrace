import requests

BASE_URL = "http://127.0.0.1:8000/api"


def main():
    print("\n1. List seeded datasets")
    print(requests.get(f"{BASE_URL}/datasets").json())

    print("\n2. Create a new dataset")
    create_dataset_payload = {
        "name": "demo_customer_risk",
        "description": "Dataset created from test client",
        "source_type": "inline",
        "rows": [
            {"customer_id": "N001", "age": 22, "income": 32000, "tenure_months": 3, "region": "east", "label": 1},
            {"customer_id": "N002", "age": 47, "income": 97000, "tenure_months": 40, "region": "west", "label": 0},
            {"customer_id": "N003", "age": 35, "income": 56000, "tenure_months": 16, "region": "north", "label": 0},
            {"customer_id": "N004", "age": 28, "income": 41000, "tenure_months": 7, "region": "south", "label": 1},
        ],
    }
    dataset = requests.post(f"{BASE_URL}/datasets", json=create_dataset_payload).json()
    print(dataset)
    dataset_id = dataset["dataset_id"]

    print("\n3. Update the dataset")
    updated = requests.put(
        f"{BASE_URL}/datasets/{dataset_id}",
        json={"description": "Updated dataset for watchtower demo"},
    ).json()
    print(updated)

    print("\n4. Train an experiment")
    experiment_payload = {
        "dataset_id": dataset_id,
        "experiment_name": "customer_risk_lr_v1",
        "config": {
            "target_column": "label",
            "feature_columns": ["age", "income", "tenure_months"],
            "algorithm": "logistic_regression",
            "test_size": 0.2,
            "normalize": True,
        },
    }
    experiment = requests.post(f"{BASE_URL}/experiments", json=experiment_payload).json()
    print(experiment)
    experiment_id = experiment["experiment_id"]

    print("\n5. Promote model registry stage")
    print(requests.patch(f"{BASE_URL}/experiments/{experiment_id}/registry", json={"stage": "production"}).json())

    print("\n6. Run predictions")
    prediction_payload = {
        "experiment_id": experiment_id,
        "records": [
            {"customer_id": "P001", "age": 23, "income": 30000, "tenure_months": 2},
            {"customer_id": "P002", "age": 51, "income": 105000, "tenure_months": 48},
            {"customer_id": "P003", "age": 30, "income": 45000, "tenure_months": 10},
        ],
    }
    prediction_batch = requests.post(f"{BASE_URL}/predictions", json=prediction_payload).json()
    print(prediction_batch)
    prediction_batch_id = prediction_batch["prediction_batch_id"]

    print("\n7. Fetch prediction batch")
    print(requests.get(f"{BASE_URL}/predictions/{prediction_batch_id}").json())

    print("\n8. Delete prediction batch")
    print(requests.delete(f"{BASE_URL}/predictions/{prediction_batch_id}").json())

    print("\n9. Delete experiment")
    print(requests.delete(f"{BASE_URL}/experiments/{experiment_id}").json())

    print("\n10. Delete dataset")
    print(requests.delete(f"{BASE_URL}/datasets/{dataset_id}").json())


if __name__ == "__main__":
    main()
