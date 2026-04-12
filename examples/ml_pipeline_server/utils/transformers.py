from collections import Counter

from ..utils.math_utils import mean


def summarize_rows(rows: list[dict]) -> dict:
    numeric_columns = {}
    categorical_columns = {}

    for row in rows:
        for key, value in row.items():
            if isinstance(value, (int, float)) and key != "label":
                numeric_columns.setdefault(key, []).append(float(value))
            elif isinstance(value, str):
                categorical_columns.setdefault(key, []).append(value)

    return {
        "numeric_means": {key: round(mean(values), 3) for key, values in numeric_columns.items()},
        "categorical_top_values": {
            key: Counter(values).most_common(2) for key, values in categorical_columns.items()
        },
    }


def normalize_features(rows: list[dict], feature_columns: list[str]) -> tuple[list[dict], dict]:
    stats = {}
    normalized = []

    for column in feature_columns:
        values = [float(row[column]) for row in rows]
        min_v = min(values)
        max_v = max(values)
        stats[column] = {"min": min_v, "max": max_v}

    for row in rows:
        new_row = dict(row)
        for column in feature_columns:
            min_v = stats[column]["min"]
            max_v = stats[column]["max"]
            value = float(row[column])
            new_row[column] = 0.0 if max_v == min_v else round((value - min_v) / (max_v - min_v), 6)
        normalized.append(new_row)

    return normalized, stats
