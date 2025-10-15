"""
Basic COO Optimization Example
"""

import numpy as np
import matplotlib.pyplot as plt
from coo_optimizer import COO


def main():
    """Basic optimization example on Rastrigin function"""

    print("="*60)
    print("COO Basic Optimization Example")
    print("="*60)

    # Define Rastrigin function (challenging multimodal function)
    def rastrigin(x):
        """
        Rastrigin function - has many local minima.
        Global minimum at x = [0, 0, ...] with f(x) = 0
        We negate for maximization.
        """
        A = 10
        n = len(x)
        result = A * n + np.sum(x**2 - A * np.cos(2 * np.pi * x))
        return -result  # Negative for maximization

    # Problem setup
    dimensions = 5
    bounds = [(-5.12, 5.12)] * dimensions

    print(f"\nProblem:")
    print(f"  Function: Rastrigin")
    print(f"  Dimensions: {dimensions}")
    print(f"  Bounds: {bounds[0]}")
    print(f"  Global optimum: x = [0, 0, 0, 0, 0], f(x) = 0")

    # Create optimizer
    print(f"\nInitializing COO optimizer...")
    optimizer = COO(
        bounds=bounds,
        n_packs=2,
        init_pack_size=10,
        max_iterations=50,
        surrogate_enabled=True,
        random_state=42,
        verbose=True
    )

    # Optimize
    print(f"\nStarting optimization...")
    best_position, best_fitness, history, diagnostics = optimizer.optimize(
        rastrigin)

    # Results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Best position found: {best_position}")
    print(f"Best fitness (negated): {best_fitness:.6f}")
    print(f"True optimum fitness: 0.000000")
    print(f"Distance to optimum: {np.linalg.norm(best_position):.6f}")
    print(f"Function evaluations: {diagnostics['cache_size']}")
    print(f"Final pack sizes: {diagnostics['final_pack_sizes']}")

    # Plot convergence
    plt.figure(figsize=(10, 6))
    plt.plot(history, linewidth=2, color='#2ecc71')
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Best Fitness', fontsize=12)
    plt.title('COO Convergence on Rastrigin Function',
              fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('coo_basic_convergence.png', dpi=300)
    print(f"\nConvergence plot saved as 'coo_basic_convergence.png'")
    plt.show()


if __name__ == "__main__":
    main()
