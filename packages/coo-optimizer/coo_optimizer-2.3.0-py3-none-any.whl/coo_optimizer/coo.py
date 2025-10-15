"""
Complete Full-Featured COO Package
===================================

This is the COMPLETE implementation merging all features from:
1. COO_Algorithm_Standalone.py
2. Comprehensive_ML_Comparison_Study.py  
3. All advanced features

Ready for use in both scripts and as a package.

Features:
- Multi-pack architecture
- Surrogate-assisted evaluation (RF + GB ensemble)
- Adaptive pack sizing
- Elitist cross-pack exchange
- Gradient-based local refinement
- Reacquisition (zigzag) movement
- Evaluation caching
- Momentum-based velocity updates
"""

import numpy as np
import math
from typing import Callable, List, Tuple, Optional, Dict
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor


# ======================
# Surrogate Ensemble
# ======================
class SurrogateEnsemble:
    """
    Ensemble surrogate model combining Random Forest and Gradient Boosting.

    Provides robust fitness predictions by averaging multiple base models.
    """

    def __init__(self, kind: str = 'ensemble', random_state: int = 42, n_jobs: int = -1):
        """
        Initialize surrogate ensemble.

        Parameters
        ----------
        kind : str
            Type of surrogate: 'rf', 'gb', or 'ensemble'
        random_state : int
            Random seed for reproducibility
        n_jobs : int
            Number of parallel jobs for training
        """
        self.kind = kind
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.models = []

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'SurrogateEnsemble':
        """
        Train surrogate model(s) on historical data.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training positions
        y : np.ndarray, shape (n_samples,)
            Training fitness values

        Returns
        -------
        self : SurrogateEnsemble
        """
        jobs = []

        if self.kind in ('rf', 'ensemble'):
            jobs.append(('rf', RandomForestRegressor(
                n_estimators=80,
                n_jobs=1,
                random_state=self.random_state,
                max_depth=15
            )))

        if self.kind in ('gb', 'ensemble'):
            jobs.append(('gb', GradientBoostingRegressor(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=5,
                random_state=self.random_state
            )))

        def _fit_one(item):
            name, model = item
            model.fit(X, y)
            return (name, model)

        n_parallel = min(len(jobs), abs(self.n_jobs)
                         if self.n_jobs != -1 else 2)
        self.models = Parallel(n_jobs=n_parallel)(
            delayed(_fit_one)(item) for item in jobs
        )

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict fitness values using ensemble averaging.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Query positions

        Returns
        -------
        predictions : np.ndarray, shape (n_samples,)
            Predicted fitness values
        """
        if not self.models:
            raise RuntimeError("Surrogate not trained. Call fit() first.")

        predictions = []
        for name, model in self.models:
            predictions.append(model.predict(X))

        predictions = np.vstack(predictions)
        return predictions.mean(axis=0)


# ======================
# Complete COO Algorithm
# ======================
class CanineOlfactoryOptimization:
    """
    Complete Canine Olfactory Optimization (COO) Algorithm v3

    A bio-inspired optimization algorithm that simulates cooperative
    pack hunting behaviors of canines with ALL advanced features.

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
    surrogate_kind : str, default='ensemble'
        Type of surrogate model: 'rf', 'gb', or 'ensemble'
    surrogate_retrain_freq : int, default=5
        Iterations between surrogate retraining
    surrogate_min_samples : int, default=30
        Minimum samples required to train surrogate
    elitist_exchange_freq : int, default=6
        Iterations between cross-pack elite exchange
    grad_refinement_pct : float, default=0.10
        Percentage of top solutions to refine with gradients
    use_gradient : bool, default=True
        Whether to use gradient-based refinement
    use_elitist : bool, default=True
        Whether to use elitist cross-pack exchange
    use_adaptive_pack : bool, default=True
        Whether to use adaptive pack sizing
    cache_decimals : int, default=8
        Decimal places for evaluation caching
    random_state : Optional[int], default=None
        Random seed for reproducibility
    verbose : bool, default=False
        Whether to print progress information

    Examples
    --------
    >>> from complete_coo import CanineOlfactoryOptimization
    >>> def objective(x):
    ...     return -sum(x**2)  # Maximize (minimize sum of squares)
    >>> bounds = [(-5, 5), (-5, 5), (-5, 5)]
    >>> optimizer = CanineOlfactoryOptimization(bounds, max_iterations=50)
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
        surrogate_retrain_freq: int = 5,
        surrogate_min_samples: int = 30,
        elitist_exchange_freq: int = 6,
        grad_refinement_pct: float = 0.10,
        use_gradient: bool = True,
        use_elitist: bool = True,
        use_adaptive_pack: bool = True,
        cache_decimals: int = 8,
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
        self.surrogate_retrain_freq = surrogate_retrain_freq
        self.surrogate_min_samples = surrogate_min_samples

        self.elitist_exchange_freq = elitist_exchange_freq
        self.grad_refinement_pct = grad_refinement_pct

        self.use_gradient = use_gradient
        self.use_elitist = use_elitist
        self.use_adaptive_pack = use_adaptive_pack

        self.cache_decimals = cache_decimals
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
        self.gradient_step = 0.03
        self.gradient_eps = 1e-4

    def _params_to_key(self, params: np.ndarray) -> Tuple:
        """Convert parameter array to hashable cache key."""
        return tuple(np.round(params, self.cache_decimals).tolist())

    def _cached_eval(self, params: np.ndarray, func: Callable) -> float:
        """
        Evaluate function with caching to avoid redundant evaluations.

        Parameters
        ----------
        params : np.ndarray
            Parameter vector to evaluate
        func : Callable
            Objective function

        Returns
        -------
        fitness : float
            Fitness value (cached if previously evaluated)
        """
        key = self._params_to_key(params)

        if key not in self.evaluation_cache:
            result = func(params)
            # Handle both tuple and float returns
            if isinstance(result, tuple):
                value = result[0]
            else:
                value = result
            self.evaluation_cache[key] = float(value)

        return self.evaluation_cache[key]

    def _batch_eval(self, population: np.ndarray, func: Callable) -> np.ndarray:
        """
        Evaluate population with caching.

        Parameters
        ----------
        population : np.ndarray, shape (n, dim)
            Population to evaluate
        func : Callable
            Objective function

        Returns
        -------
        fitness : np.ndarray, shape (n,)
            Fitness values
        """
        return np.array([self._cached_eval(ind, func) for ind in population])

    def _clip_population(self, population: np.ndarray) -> np.ndarray:
        """Clip population to stay within bounds."""
        return np.clip(population, self.lower, self.upper)

    def _compute_numerical_gradient(
        self,
        position: np.ndarray,
        func: Callable
    ) -> np.ndarray:
        """
        Compute numerical gradient using central differences.

        Parameters
        ----------
        position : np.ndarray
            Current position
        func : Callable
            Objective function

        Returns
        -------
        gradient : np.ndarray
            Numerical gradient vector
        """
        gradient = np.zeros(self.dim)

        for j in range(self.dim):
            pos_plus = position.copy()
            pos_minus = position.copy()

            pos_plus[j] += self.gradient_eps
            pos_minus[j] -= self.gradient_eps

            f_plus = self._cached_eval(pos_plus, func)
            f_minus = self._cached_eval(pos_minus, func)

            gradient[j] = (f_plus - f_minus) / (2 * self.gradient_eps)

        return gradient

    def _initialize_packs(self) -> List[Dict]:
        """
        Initialize multiple packs with random positions and zero velocities.

        Returns
        -------
        packs : List[Dict]
            List of pack dictionaries containing positions and velocities
        """
        packs = []

        for _ in range(self.n_packs):
            positions = self.lower + np.random.rand(
                self.init_pack_size, self.dim
            ) * (self.upper - self.lower)

            velocities = np.zeros_like(positions)

            packs.append({
                'positions': positions,
                'velocities': velocities
            })

        return packs

    def _train_surrogate(
        self,
        X_history: List[np.ndarray],
        y_history: List[float]
    ) -> Optional[SurrogateEnsemble]:
        """
        Train surrogate model on historical evaluations.

        Parameters
        ----------
        X_history : List[np.ndarray]
            Historical positions
        y_history : List[float]
            Historical fitness values

        Returns
        -------
        surrogate : SurrogateEnsemble or None
            Trained surrogate model, or None if training failed
        """
        if len(X_history) < self.surrogate_min_samples:
            return None

        try:
            X_train = np.vstack(X_history)
            y_train = np.array(y_history)

            surrogate = SurrogateEnsemble(
                kind=self.surrogate_kind,
                random_state=self.random_state
            )
            surrogate.fit(X_train, y_train)

            return surrogate

        except Exception as e:
            if self.verbose:
                print(f"Warning: Surrogate training failed: {e}")
            return None

    def _adaptive_pack_sizing(
        self,
        packs: List[Dict],
        no_improve_count: int
    ) -> None:
        """
        Adaptively reduce pack sizes during stagnation.

        Parameters
        ----------
        packs : List[Dict]
            Pack dictionaries to modify
        no_improve_count : int
            Number of iterations without improvement
        """
        if not self.use_adaptive_pack:
            return

        if no_improve_count > 10:
            for pack in packs:
                current_size = pack['positions'].shape[0]

                if current_size > self.min_pack_size:
                    new_size = max(self.min_pack_size, current_size - 1)
                    pack['positions'] = pack['positions'][:new_size]
                    pack['velocities'] = pack['velocities'][:new_size]

    def _elitist_exchange(
        self,
        packs: List[Dict],
        pack_bests: List[Tuple[float, np.ndarray]],
        func: Callable
    ) -> None:
        """
        Exchange elite solutions across packs.

        Parameters
        ----------
        packs : List[Dict]
            Pack dictionaries to modify
        pack_bests : List[Tuple[float, np.ndarray]]
            Best solutions from each pack (fitness, position)
        func : Callable
            Objective function for evaluation
        """
        if not self.use_elitist or len(pack_bests) < 2:
            return

        # Sort and select top elites
        sorted_bests = sorted(pack_bests, key=lambda x: -x[0])
        top_elites = [pos for _,
                      pos in sorted_bests[:min(3, len(sorted_bests))]]

        # Inject elites into worst positions of each pack
        for pack in packs:
            fitness_values = self._batch_eval(pack['positions'], func)
            worst_idx = int(np.argmin(fitness_values))

            for elite_pos in top_elites:
                # Add small perturbation to elite
                perturbed = elite_pos + np.random.randn(self.dim) * 0.01
                perturbed = np.clip(perturbed, self.lower, self.upper)
                pack['positions'][worst_idx] = perturbed

    def _gradient_refinement(
        self,
        packs: List[Dict],
        func: Callable
    ) -> None:
        """
        Apply gradient-based local refinement to top solutions.

        Parameters
        ----------
        packs : List[Dict]
            Pack dictionaries to modify
        func : Callable
            Objective function
        """
        if not self.use_gradient:
            return

        # Collect all positions
        all_positions = np.vstack([pack['positions'] for pack in packs])
        all_fitness = self._batch_eval(all_positions, func)

        # Select top candidates
        n_top = max(1, int(len(all_positions) * self.grad_refinement_pct))
        top_indices = np.argsort(-all_fitness)[:n_top]

        # Apply gradient descent to each
        for idx in top_indices:
            position = all_positions[idx].copy()
            current_fitness = all_fitness[idx]

            # Compute gradient
            gradient = self._compute_numerical_gradient(position, func)

            # Normalize and apply trust region
            grad_norm = np.linalg.norm(gradient) + 1e-12
            step = self.gradient_step * (gradient / grad_norm)
            step = np.clip(step, -0.07, 0.07)

            # New position
            new_position = np.clip(position + step, self.lower, self.upper)
            new_fitness = self._cached_eval(new_position, func)

            # Update if improved
            if new_fitness > current_fitness:
                # Find which pack and index to update
                offset = 0
                for pack in packs:
                    pack_size = pack['positions'].shape[0]

                    if idx < offset + pack_size:
                        local_idx = idx - offset
                        pack['positions'][local_idx] = new_position
                        pack['velocities'][local_idx] *= 0.3  # Dampen velocity
                        break

                    offset += pack_size

    def optimize(
        self,
        objective_function: Callable[[np.ndarray], float]
    ) -> Tuple[np.ndarray, float, List[float], Dict]:
        """
        Run the complete COO optimization algorithm with all features.

        Parameters
        ----------
        objective_function : Callable
            Function to maximize: f(x) -> fitness (higher is better)
            Input: np.ndarray of shape (dim,)
            Output: float (fitness value) or tuple (fitness, model)

        Returns
        -------
        best_position : np.ndarray
            Best solution found

        best_fitness : float
            Best fitness value achieved

        convergence_history : List[float]
            Best fitness at each iteration

        diagnostics : Dict
            Additional diagnostic information:
            - 'cache_size': Number of unique evaluations
            - 'iterations': Total iterations performed
            - 'final_pack_sizes': Pack sizes at termination
            - 'no_improvement_streak': Consecutive iterations without improvement
        """
        # Initialize
        packs = self._initialize_packs()
        X_history = []
        y_history = []
        no_improve_count = 0
        best_prev = -np.inf

        if self.verbose:
            print("="*70)
            print("Canine Olfactory Optimization (COO) v3 - Complete")
            print("="*70)
            print(f"Dimensions: {self.dim}")
            print(f"Packs: {self.n_packs}")
            print(f"Initial pack size: {self.init_pack_size}")
            print(f"Max iterations: {self.max_iterations}")
            print(
                f"Surrogate: {self.surrogate_kind if self.surrogate_enabled else 'Disabled'}")
            print(
                f"Gradient refinement: {'Enabled' if self.use_gradient else 'Disabled'}")
            print(
                f"Elitist exchange: {'Enabled' if self.use_elitist else 'Disabled'}")
            print(
                f"Adaptive pack sizing: {'Enabled' if self.use_adaptive_pack else 'Disabled'}")
            print("="*70 + "\n")

        # Main optimization loop
        for iteration in range(self.max_iterations):
            # Update exploration parameters (exponential decay)
            sigma1 = self.sigma1_init * math.exp(-0.05 * iteration)
            sigma2 = self.sigma2_init * math.exp(-0.07 * iteration)

            # Adaptive cooperation weight (increases over time)
            coop_weight = 0.4 + 0.6 * (iteration / max(1, self.max_iterations))

            # Adaptive pack sizing
            self._adaptive_pack_sizing(packs, no_improve_count)

            # Train surrogate periodically
            use_surrogate = False
            if (self.surrogate_enabled and
                iteration % self.surrogate_retrain_freq == 0 and
                    len(X_history) >= self.surrogate_min_samples):

                self.surrogate = self._train_surrogate(X_history, y_history)
                use_surrogate = self.surrogate is not None

            # Process each pack
            pack_bests = []

            for pack_idx, pack in enumerate(packs):
                positions = pack['positions']
                velocities = pack['velocities']
                n_dogs = positions.shape[0]

                # Evaluate positions
                if use_surrogate and self.surrogate is not None:
                    try:
                        # Surrogate predictions
                        predicted_fitness = self.surrogate.predict(positions)

                        # Exact evaluation of top 50%
                        n_exact = max(1, n_dogs // 2)
                        top_indices = np.argsort(-predicted_fitness)[:n_exact]
                        exact_fitness = self._batch_eval(
                            positions[top_indices],
                            objective_function
                        )
                        predicted_fitness[top_indices] = exact_fitness

                        fitness = predicted_fitness

                    except Exception as e:
                        # Fallback to exact evaluation
                        if self.verbose:
                            print(
                                f"Surrogate prediction failed: {e}, using exact evaluation")
                        fitness = self._batch_eval(
                            positions, objective_function)
                else:
                    # Exact evaluation
                    fitness = self._batch_eval(positions, objective_function)

                # Store history for surrogate training
                X_history.extend(positions.tolist())
                y_history.extend(fitness.tolist())

                # Find pack-local best
                local_best_idx = int(np.argmax(fitness))
                local_best_position = positions[local_best_idx].copy()
                local_best_fitness = float(fitness[local_best_idx])

                # Update global best
                if local_best_fitness > self.best_fitness:
                    self.best_fitness = local_best_fitness
                    self.best_position = local_best_position.copy()
                    no_improve_count = 0

                pack_bests.append((local_best_fitness, local_best_position))

                # Update velocities and positions
                for i in range(n_dogs):
                    # Attraction to local best
                    dir_local = local_best_position - positions[i]

                    # Attraction to global best
                    dir_global = (self.best_position - positions[i]
                                  if self.best_position is not None
                                  else np.zeros(self.dim))

                    # Velocity update (momentum + cooperation)
                    velocities[i] = (
                        self.momentum_weight * velocities[i] +
                        self.local_attraction * dir_local +
                        coop_weight * dir_global / (n_dogs + 1)
                    )

                    # Position update with sniffing noise
                    positions[i] = (
                        positions[i] +
                        velocities[i] +
                        sigma1 * np.random.randn(self.dim)
                    )

                    # Reacquisition (zigzag) movement
                    if np.random.rand() < self.zigzag_prob:
                        zigzag_noise = (sigma2 * np.random.randn(self.dim) *
                                        np.sin(2 * math.pi * iteration /
                                               max(1, self.max_iterations)))
                        positions[i] += zigzag_noise

                    # Clip to bounds
                    positions[i] = np.clip(
                        positions[i], self.lower, self.upper)

                # Update pack
                pack['positions'] = positions
                pack['velocities'] = velocities

            # Elitist exchange across packs
            if iteration % self.elitist_exchange_freq == 0:
                self._elitist_exchange(packs, pack_bests, objective_function)

            # Gradient-based refinement
            self._gradient_refinement(packs, objective_function)

            # Update stagnation counter
            if self.best_fitness <= best_prev + 1e-9:
                no_improve_count += 1
            else:
                no_improve_count = 0

            best_prev = self.best_fitness
            self.convergence_history.append(self.best_fitness)

            # Verbose output
            if self.verbose and (iteration % 10 == 0 or iteration == self.max_iterations - 1):
                pack_sizes = [pack['positions'].shape[0] for pack in packs]
                print(f"Iter {iteration:3d} | Best: {self.best_fitness:10.6f} | "
                      f"Pack sizes: {pack_sizes} | Cache: {len(self.evaluation_cache)}")

        # Collect diagnostics
        diagnostics = {
            'cache_size': len(self.evaluation_cache),
            'iterations': self.max_iterations,
            'final_pack_sizes': [pack['positions'].shape[0] for pack in packs],
            'no_improvement_streak': no_improve_count
        }

        if self.verbose:
            print("\n" + "="*70)
            print("Optimization Complete")
            print("="*70)
            print(f"Best fitness: {self.best_fitness:.8f}")
            print(f"Total evaluations: {len(self.evaluation_cache)}")
            print(f"Best position: {self.best_position}")
            print("="*70)

        return (
            self.best_position,
            self.best_fitness,
            self.convergence_history,
            diagnostics
        )


# Alias for convenience
COO = CanineOlfactoryOptimization


# ======================
# Example Usage
# ======================
if __name__ == "__main__":
    """
    Example: Optimize a simple test function
    """

    print("\n" + "="*70)
    print("Complete COO Algorithm - Example")
    print("="*70)

    # Define objective function (Rastrigin - challenging multimodal function)
    def rastrigin(x):
        """
        Rastrigin function (minimization problem, so we negate for maximization)
        Global minimum at x = [0, 0, ...] with f(x) = 0
        """
        A = 10
        n = len(x)
        result = A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))
        return -result  # Negate for maximization

    # Define search space
    dimensions = 5
    bounds = [(-5.12, 5.12)] * dimensions

    # Create optimizer with ALL features enabled
    optimizer = COO(
        bounds=bounds,
        n_packs=2,
        init_pack_size=12,
        min_pack_size=8,
        max_iterations=50,
        surrogate_enabled=True,
        surrogate_kind='ensemble',
        use_gradient=True,
        use_elitist=True,
        use_adaptive_pack=True,
        random_state=42,
        verbose=True
    )

    # Run optimization
    best_pos, best_fit, history, diagnostics = optimizer.optimize(rastrigin)

    # Results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Best position: {best_pos}")
    print(f"Best fitness (negated): {best_fit:.8f}")
    print(f"True optimum fitness: 0.000000")
    print(f"Distance to optimum: {np.linalg.norm(best_pos):.6f}")
    print(f"Unique evaluations: {diagnostics['cache_size']}")
    print(f"Final pack sizes: {diagnostics['final_pack_sizes']}")
    print("="*70)
