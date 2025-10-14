"""
Core COO Algorithm Implementation
"""

import numpy as np
import math
from typing import Callable, List, Tuple, Optional, Dict
from joblib import Parallel, delayed
from .surrogate import SurrogateEnsemble


class CanineOlfactoryOptimization:
    """
    Canine Olfactory Optimization (COO) Algorithm

    A bio-inspired optimization algorithm that mimics the cooperative
    search behavior of canine packs tracking scents.

    Parameters
    ----------
    bounds : List[Tuple[float, float]]
        Search space bounds [(lower_1, upper_1), ..., (lower_d, upper_d)]
    n_packs : int, default=2
        Number of independent search packs
    init_pack_size : int, default=10
        Initial number of dogs per pack
    min_pack_size : int, default=8
        Minimum pack size (for adaptive sizing)
    max_iterations : int, default=100
        Maximum number of iterations
    surrogate_enabled : bool, default=True
        Whether to use surrogate-assisted evaluation
    random_state : Optional[int], default=None
        Random seed for reproducibility
    verbose : bool, default=False
        Whether to print progress information

    Examples
    --------
    >>> from coo_optimizer import COO
    >>> def objective(x):
    ...     return -sum(x**2)  # Maximize (minimize sum of squares)
    >>> bounds = [(-5, 5), (-5, 5), (-5, 5)]
    >>> optimizer = COO(bounds, max_iterations=50)
    >>> best_pos, best_fit, history, diagnostics = optimizer.optimize(objective)
    >>> print(f"Best fitness: {best_fit:.6f}")
    """

    def __init__(
        self,
        bounds: List[Tuple[float, float]],
        n_packs: int = 2,
        init_pack_size: int = 10,
        min_pack_size: int = 8,
        max_iterations: int = 100,
        surrogate_enabled: bool = True,
        surrogate_kind: str = 'ensemble',
        random_state: Optional[int] = None,
        verbose: bool = False
    ):
        self.bounds = np.array(bounds)
        self.dim = len(bounds)
        self.lower = self.bounds[:, 0]
        self.upper = self.bounds[:, 1]

        self.n_packs = n_packs
        self.init_pack_size = init_pack_size
        self.min_pack_size = min_pack_size
        self.max_iterations = max_iterations

        self.surrogate_enabled = surrogate_enabled
        self.surrogate_kind = surrogate_kind

        self.random_state = random_state
        self.verbose = verbose

        if random_state is not None:
            np.random.seed(random_state)

        # Algorithm state
        self.best_position = None
        self.best_fitness = -np.inf
        self.convergence_history = []
        self.evaluation_cache = {}
        self.surrogate = None

        # Hyperparameters
        self.momentum_weight = 0.6
        self.local_attraction = 0.3
        self.sigma1_init = 0.35
        self.sigma2_init = 0.12
        self.zigzag_prob = 0.18

    def _cached_eval(self, params: np.ndarray, func: Callable) -> float:
        """Evaluate function with caching."""
        key = tuple(np.round(params, 8).tolist())
        if key not in self.evaluation_cache:
            self.evaluation_cache[key] = float(func(params))
        return self.evaluation_cache[key]

    def _clip_population(self, population: np.ndarray) -> np.ndarray:
        """Clip population to stay within bounds."""
        return np.clip(population, self.lower, self.upper)

    def optimize(
        self,
        objective_function: Callable[[np.ndarray], float]
    ) -> Tuple[np.ndarray, float, List[float], Dict]:
        """
        Run the COO optimization algorithm.

        Parameters
        ----------
        objective_function : Callable
            Function to maximize: f(x) -> fitness (higher is better)

        Returns
        -------
        best_position : np.ndarray
            Best solution found
        best_fitness : float
            Best fitness value achieved
        convergence_history : List[float]
            Best fitness at each iteration
        diagnostics : Dict
            Additional diagnostic information
        """
        # Initialize packs
        packs = []
        for _ in range(self.n_packs):
            positions = self.lower + \
                np.random.rand(self.init_pack_size, self.dim) * \
                (self.upper - self.lower)
            velocities = np.zeros_like(positions)
            packs.append({'positions': positions, 'velocities': velocities})

        X_history = []
        y_history = []
        no_improve_count = 0

        if self.verbose:
            print(
                f"COO Optimization: {self.dim}D, {self.max_iterations} iterations")

        # Main loop
        for iteration in range(self.max_iterations):
            sigma1 = self.sigma1_init * math.exp(-0.05 * iteration)
            sigma2 = self.sigma2_init * math.exp(-0.07 * iteration)
            coop_weight = 0.4 + 0.6 * (iteration / max(1, self.max_iterations))

            # Adaptive pack sizing
            if no_improve_count > 10:
                for pack in packs:
                    cur_size = pack['positions'].shape[0]
                    if cur_size > self.min_pack_size:
                        new_size = max(self.min_pack_size, cur_size - 1)
                        pack['positions'] = pack['positions'][:new_size]
                        pack['velocities'] = pack['velocities'][:new_size]

            # Train surrogate
            use_surrogate = False
            if self.surrogate_enabled and iteration % 5 == 0 and len(X_history) >= 30:
                try:
                    self.surrogate = SurrogateEnsemble(
                        kind=self.surrogate_kind)
                    self.surrogate.fit(np.vstack(X_history),
                                       np.array(y_history))
                    use_surrogate = True
                except:
                    use_surrogate = False

            # Process packs
            for pack in packs:
                positions = pack['positions']
                velocities = pack['velocities']
                n_dogs = positions.shape[0]

                # Evaluate
                if use_surrogate and self.surrogate is not None:
                    try:
                        fitness = self.surrogate.predict(positions)
                        top_idx = np.argsort(-fitness)[:max(1, n_dogs//2)]
                        exact_fitness = np.array(
                            [self._cached_eval(p, objective_function) for p in positions[top_idx]])
                        fitness[top_idx] = exact_fitness
                    except:
                        fitness = np.array(
                            [self._cached_eval(p, objective_function) for p in positions])
                else:
                    fitness = np.array(
                        [self._cached_eval(p, objective_function) for p in positions])

                X_history.extend(positions.tolist())
                y_history.extend(fitness.tolist())

                # Update best
                local_best_idx = np.argmax(fitness)
                local_best_pos = positions[local_best_idx].copy()
                local_best_fit = fitness[local_best_idx]

                if local_best_fit > self.best_fitness:
                    self.best_fitness = local_best_fit
                    self.best_position = local_best_pos.copy()
                    no_improve_count = 0
                else:
                    no_improve_count += 1

                # Update velocities and positions
                for i in range(n_dogs):
                    dir_local = local_best_pos - positions[i]
                    dir_global = (
                        self.best_position - positions[i] if self.best_position is not None else np.zeros(self.dim))

                    velocities[i] = (self.momentum_weight * velocities[i] +
                                     self.local_attraction * dir_local +
                                     coop_weight * dir_global / (n_dogs + 1))

                    positions[i] = positions[i] + velocities[i] + \
                        sigma1 * np.random.randn(self.dim)

                    if np.random.rand() < self.zigzag_prob:
                        positions[i] += sigma2 * np.random.randn(self.dim) * np.sin(
                            2 * math.pi * iteration / max(1, self.max_iterations))

                    positions[i] = np.clip(
                        positions[i], self.lower, self.upper)

                pack['positions'] = positions
                pack['velocities'] = velocities

            self.convergence_history.append(self.best_fitness)

            if self.verbose and (iteration % 10 == 0 or iteration == self.max_iterations - 1):
                print(
                    f"Iter {iteration:3d}: Best = {self.best_fitness:.6f}, Cache = {len(self.evaluation_cache)}")

        diagnostics = {
            'cache_size': len(self.evaluation_cache),
            'iterations': self.max_iterations,
            'final_pack_sizes': [pack['positions'].shape[0] for pack in packs]
        }

        return self.best_position, self.best_fitness, self.convergence_history, diagnostics


# Alias for convenience
COO = CanineOlfactoryOptimization
