def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def safe_divide(a: float, b: float) -> float:
    return a / b if b else 0.0


def sigmoid(x: float) -> float:
    import math

    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    else:
        z = math.exp(x)
        return z / (1 + z)
