def validate_non_empty_rows(rows: list[dict]) -> None:
    if not rows:
        raise ValueError("rows must not be empty")


def validate_columns_exist(rows: list[dict], columns: list[str]) -> None:
    if not rows:
        raise ValueError("rows must not be empty")
    sample = rows[0]
    missing = [column for column in columns if column not in sample]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_target_not_in_features(target_column: str, feature_columns: list[str]) -> None:
    if target_column in feature_columns:
        raise ValueError("target column must not be present in feature columns")
