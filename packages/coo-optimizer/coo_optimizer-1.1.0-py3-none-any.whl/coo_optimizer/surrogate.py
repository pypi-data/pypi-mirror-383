"""
Surrogate Model Implementation
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from joblib import Parallel, delayed


class SurrogateEnsemble:
    """
    Ensemble surrogate model combining Random Forest and Gradient Boosting.
    """

    def __init__(self, kind: str = 'ensemble', random_state: int = 42):
        self.kind = kind
        self.random_state = random_state
        self.models = []

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Train surrogate models."""
        jobs = []

        if self.kind in ('rf', 'ensemble'):
            jobs.append(('rf', RandomForestRegressor(
                n_estimators=80, n_jobs=1, random_state=self.random_state, max_depth=15
            )))

        if self.kind in ('gb', 'ensemble'):
            jobs.append(('gb', GradientBoostingRegressor(
                n_estimators=150, learning_rate=0.1, max_depth=5, random_state=self.random_state
            )))

        def _fit_one(item):
            name, model = item
            model.fit(X, y)
            return (name, model)

        self.models = Parallel(n_jobs=min(len(jobs), 2))(
            delayed(_fit_one)(item) for item in jobs)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict using ensemble averaging."""
        if not self.models:
            raise RuntimeError("Surrogate not trained")

        predictions = [model.predict(X) for name, model in self.models]
        return np.mean(predictions, axis=0)
