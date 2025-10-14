"""
Unit tests for COO optimizer
"""

import numpy as np
import pytest
from coo_optimizer import COO, CanineOlfactoryOptimization


class TestCOOBasics:
    """Test basic COO functionality"""

    def test_initialization(self):
        """Test COO initialization"""
        bounds = [(-5, 5), (-5, 5)]
        optimizer = COO(bounds, max_iterations=10, random_state=42)

        assert optimizer.dim == 2
        assert optimizer.max_iterations == 10
        assert len(optimizer.bounds) == 2

    def test_sphere_function(self):
        """Test optimization on simple sphere function"""
        def sphere(x):
            return -np.sum(x**2)  # Negative for maximization

        bounds = [(-5, 5)] * 3
        optimizer = COO(bounds, max_iterations=20,
                        random_state=42, verbose=False)
        best_pos, best_fit, history, diag = optimizer.optimize(sphere)

        # Should find solution close to origin
        assert best_fit > -1.0
        assert len(history) == 20
        assert diag['iterations'] == 20
        assert np.linalg.norm(best_pos) < 2.0

    def test_convergence(self):
        """Test that algorithm improves over iterations"""
        def rastrigin(x):
            A = 10
            return -(A * len(x) + np.sum(x**2 - A * np.cos(2 * np.pi * x)))

        bounds = [(-5.12, 5.12)] * 5
        optimizer = COO(bounds, max_iterations=30,
                        random_state=42, verbose=False)
        _, _, history, _ = optimizer.optimize(rastrigin)

        # Check improvement over time
        assert history[-1] >= history[0], "Algorithm should improve"
        assert history[-5:][0] <= history[-1], "Should converge towards end"

    def test_bounds_clipping(self):
        """Test that solutions stay within bounds"""
        def simple_func(x):
            return -np.sum(x**2)

        bounds = [(-2, 2), (-3, 3)]
        optimizer = COO(bounds, max_iterations=15, random_state=42)
        best_pos, _, _, _ = optimizer.optimize(simple_func)

        assert bounds[0][0] <= best_pos[0] <= bounds[0][1]
        assert bounds[1][0] <= best_pos[1] <= bounds[1][1]

    def test_caching(self):
        """Test evaluation caching"""
        call_count = {'count': 0}

        def counted_func(x):
            call_count['count'] += 1
            return -np.sum(x**2)

        bounds = [(-5, 5)] * 2
        optimizer = COO(bounds, max_iterations=10, random_state=42)
        _, _, _, diag = optimizer.optimize(counted_func)

        # Cache should have entries
        assert diag['cache_size'] > 0
        assert diag['cache_size'] <= call_count['count']


class TestCOOAdvanced:
    """Test advanced COO features"""

    def test_surrogate_enabled(self):
        """Test with surrogate enabled"""
        def expensive_func(x):
            return -(x[0]**2 + x[1]**2)

        bounds = [(-5, 5), (-5, 5)]
        optimizer = COO(bounds, max_iterations=20,
                        surrogate_enabled=True, random_state=42)
        best_pos, best_fit, _, _ = optimizer.optimize(expensive_func)

        assert best_fit > -2.0

    def test_surrogate_disabled(self):
        """Test with surrogate disabled"""
        def func(x):
            return -(x[0]**2 + x[1]**2)

        bounds = [(-5, 5), (-5, 5)]
        optimizer = COO(bounds, max_iterations=20,
                        surrogate_enabled=False, random_state=42)
        best_pos, best_fit, _, _ = optimizer.optimize(func)

        assert best_fit > -2.0

    def test_multiple_packs(self):
        """Test with different number of packs"""
        def func(x):
            return -np.sum(x**2)

        bounds = [(-5, 5)] * 3

        # Single pack
        opt1 = COO(bounds, n_packs=1, max_iterations=15, random_state=42)
        _, fit1, _, _ = opt1.optimize(func)

        # Multiple packs
        opt2 = COO(bounds, n_packs=3, max_iterations=15, random_state=42)
        _, fit2, _, _ = opt2.optimize(func)

        # Both should find good solutions
        assert fit1 > -1.0
        assert fit2 > -1.0

    def test_different_dimensions(self):
        """Test on different dimensionalities"""
        def func(x):
            return -np.sum(x**2)

        for dim in [2, 5, 10]:
            bounds = [(-5, 5)] * dim
            optimizer = COO(bounds, max_iterations=15, random_state=42)
            best_pos, best_fit, _, _ = optimizer.optimize(func)

            assert len(best_pos) == dim
            assert best_fit > -dim * 2.0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_single_dimension(self):
        """Test 1D optimization"""
        def func(x):
            return -(x[0] - 3)**2

        bounds = [(0, 10)]
        optimizer = COO(bounds, max_iterations=20, random_state=42)
        best_pos, best_fit, _, _ = optimizer.optimize(func)

        # Should find minimum near x=3
        assert abs(best_pos[0] - 3) < 1.0

    def test_asymmetric_bounds(self):
        """Test with asymmetric bounds"""
        def func(x):
            return -(x[0]**2 + x[1]**2)

        bounds = [(-10, 5), (0, 20)]
        optimizer = COO(bounds, max_iterations=15, random_state=42)
        best_pos, _, _, _ = optimizer.optimize(func)

        assert bounds[0][0] <= best_pos[0] <= bounds[0][1]
        assert bounds[1][0] <= best_pos[1] <= bounds[1][1]

    def test_reproducibility(self):
        """Test that random_state ensures reproducibility"""
        def func(x):
            return -np.sum(x**2)

        bounds = [(-5, 5)] * 3

        opt1 = COO(bounds, max_iterations=15, random_state=42)
        pos1, fit1, _, _ = opt1.optimize(func)

        opt2 = COO(bounds, max_iterations=15, random_state=42)
        pos2, fit2, _, _ = opt2.optimize(func)

        np.testing.assert_array_almost_equal(pos1, pos2, decimal=5)
        assert abs(fit1 - fit2) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
