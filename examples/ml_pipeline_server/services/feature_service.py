from ..clients.feature_store_client import feature_store_client
from ..core.decorators import traced_step
from ..utils.transformers import normalize_features
from ..utils.validators import validate_columns_exist, validate_target_not_in_features


class FeatureService:
    @traced_step("prepare_features")
    def prepare(self, rows: list[dict], feature_columns: list[str], target_column: str, normalize: bool) -> dict:
        validate_columns_exist(rows, feature_columns + [target_column])
        validate_target_not_in_features(target_column, feature_columns)

        metadata = feature_store_client.fetch_feature_metadata(feature_columns)

        transformed_rows = rows
        normalization_stats = {}
        if normalize:
            transformed_rows, normalization_stats = normalize_features(rows, feature_columns)

        X = [[float(row[col]) for col in feature_columns] for row in transformed_rows]
        y = [int(row[target_column]) for row in transformed_rows]

        return {
            "X": X,
            "y": y,
            "rows": transformed_rows,
            "metadata": metadata,
            "normalization_stats": normalization_stats,
        }


feature_service = FeatureService()
