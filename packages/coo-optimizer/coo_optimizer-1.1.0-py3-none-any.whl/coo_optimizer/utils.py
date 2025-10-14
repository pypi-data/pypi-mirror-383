"""
Utility functions for COO optimizer
"""

import numpy as np


def clip_bounds(x, bounds):
    """Clip values to bounds."""
    lower = np.array([b[0] for b in bounds])
    upper = np.array([b[1] for b in bounds])
    return np.clip(x, lower, upper)


def normalize_weights(weights):
    """Normalize weights to sum to 1."""
    weights = np.abs(weights)
    return weights / (np.sum(weights) + 1e-10)
