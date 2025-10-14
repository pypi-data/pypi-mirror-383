"""
Tests for surrogate models
"""

import numpy as np
import pytest
from coo_optimizer.surrogate import SurrogateEnsemble


class TestSurrogateEnsemble:
    """Test surrogate ensemble functionality"""

    def test_initialization(self):
        """Test surrogate initialization"""
        surrogate = SurrogateEnsemble(kind='ensemble', random_state=42)
        assert surrogate.kind == 'ensemble'
        assert surrogate.random_state == 42
        assert len(surrogate.models) == 0

    def test_rf_only(self):
        """Test Random Forest only"""
        X = np.random.randn(100, 5)
        y = np.sum(X**2, axis=1)

        surrogate = SurrogateEnsemble(kind='rf', random_state=42)
        surrogate.fit(X, y)

        assert len(surrogate.models) == 1
        assert surrogate.models[0][0] == 'rf'

    def test_gb_only(self):
        """Test Gradient Boosting only"""
        X = np.random.randn(100, 5)
        y = np.sum(X**2, axis=1)

        surrogate = SurrogateEnsemble(kind='gb', random_state=42)
        surrogate.fit(X, y)

        assert len(surrogate.models) == 1
        assert surrogate.models[0][0] == 'gb'

    def test_ensemble(self):
        """Test full ensemble"""
        X = np.random.randn(100, 5)
        y = np.sum(X**2, axis=1)

        surrogate = SurrogateEnsemble(kind='ensemble', random_state=42)
        surrogate.fit(X, y)

        assert len(surrogate.models) == 2
        model_names = [name for name, _ in surrogate.models]
        assert 'rf' in model_names
        assert 'gb' in model_names

    def test_prediction(self):
        """Test prediction functionality"""
        X_train = np.random.randn(100, 3)
        y_train = np.sum(X_train**2, axis=1)

        X_test = np.random.randn(20, 3)

        surrogate = SurrogateEnsemble(kind='ensemble', random_state=42)
        surrogate.fit(X_train, y_train)
        predictions = surrogate.predict(X_test)

        assert len(predictions) == 20
        assert predictions.dtype == np.float64

    def test_prediction_accuracy(self):
        """Test that predictions are reasonable"""
        # Simple quadratic function
        X_train = np.random.randn(200, 2)
        y_train = np.sum(X_train**2, axis=1)

        X_test = np.array([[0, 0], [1, 1], [2, 2]])
        y_test_expected = np.array([0, 2, 8])

        surrogate = SurrogateEnsemble(kind='ensemble', random_state=42)
        surrogate.fit(X_train, y_train)
        predictions = surrogate.predict(X_test)

        # Predictions should be in reasonable range
        assert np.all(predictions >= -1)
        assert np.all(predictions <= 10)

        # Should roughly follow the pattern
        assert predictions[0] < predictions[1] < predictions[2]

    def test_no_fit_error(self):
        """Test that predicting without fitting raises error"""
        surrogate = SurrogateEnsemble()
        X_test = np.random.randn(10, 3)

        with pytest.raises(RuntimeError, match="Surrogate not trained"):
            surrogate.predict(X_test)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
