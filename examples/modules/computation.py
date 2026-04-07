import numpy as np


def compute_mean(sample_size: int = 1000) -> float:
    """Compute the mean of a random sample."""
    data = np.random.rand(sample_size)
    return np.mean(data)

