"""
Ensemble Model Optimization with COO
"""

import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
from coo_optimizer import COO


def main():
    """Example of optimizing ensemble weights with COO"""

    print("="*60)
    print("Ensemble Weight Optimization with COO")
    print("="*60)

    # Generate data
    print("\nGenerating dataset...")
    X, y = make_regression(
        n_samples=500,
        n_features=10,
        noise=5.0,
        random_state=42
    )

    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    y = (y - y.mean()) / y.std()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")

    # Train base models
    print("\nTraining base models...")
    models = []

    # Model 1: Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    models.append(('Random Forest', rf))
    print("  ✓ Random Forest trained")

    # Model 2: Gradient Boosting
    gb = GradientBoostingRegressor(n_estimators=100, random_state=42)
    gb.fit(X_train, y_train)
    models.append(('Gradient Boosting', gb))
    print("  ✓ Gradient Boosting trained")

    # Model 3: Neural Network
    nn = MLPRegressor(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
    nn.fit(X_train, y_train)
    models.append(('Neural Network', nn))
    print("  ✓ Neural Network trained")

    # Get predictions from all models
    train_predictions = np.array([model.predict(X_train)
                                 for _, model in models]).T
    test_predictions = np.array([model.predict(X_test)
                                for _, model in models]).T

    print(f"\nBase model predictions shape: {test_predictions.shape}")

    # Evaluate individual models
    print("\nIndividual Model Performance:")
    for i, (name, model) in enumerate(models):
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        print(f"  {name:20s}: MSE = {mse:.6f}, R² = {r2:.6f}")

    # Define ensemble evaluation function
    def evaluate_ensemble(weights):
        """Evaluate ensemble with given weights"""
        # Normalize weights
        weights = np.abs(weights)
        weights = weights / (np.sum(weights) + 1e-10)

        # Weighted predictions
        y_pred_test = test_predictions @ weights
        mse = mean_squared_error(y_test, y_pred_test)

        return -mse  # Negative for maximization

    # Optimize ensemble weights
    print("\nOptimizing ensemble weights with COO...")
    bounds = [(0, 1)] * len(models)  # Weights between 0 and 1

    optimizer = COO(
        bounds=bounds,
        max_iterations=30,
        n_packs=2,
        init_pack_size=10,
        surrogate_enabled=False,  # Simple problem, no surrogate needed
        random_state=42,
        verbose=True
    )

    best_weights, best_fitness, history, diagnostics = optimizer.optimize(
        evaluate_ensemble)

    # Normalize final weights
    best_weights = np.abs(best_weights)
    best_weights = best_weights / np.sum(best_weights)

    # Results
    print("\n" + "="*60)
    print("OPTIMIZATION RESULTS")
    print("="*60)
    print("\nOptimal Ensemble Weights:")
    for i, (name, _) in enumerate(models):
        print(f"  {name:20s}: {best_weights[i]:.4f}")

    print(f"\nBest Fitness (negative MSE): {best_fitness:.6f}")

    # Evaluate final ensemble
    print("\n" + "="*60)
    print("FINAL ENSEMBLE EVALUATION")
    print("="*60)

    y_train_ensemble = train_predictions @ best_weights
    y_test_ensemble = test_predictions @ best_weights

    train_mse = mean_squared_error(y_train, y_train_ensemble)
    test_mse = mean_squared_error(y_test, y_test_ensemble)
    train_r2 = r2_score(y_train, y_train_ensemble)
    test_r2 = r2_score(y_test, y_test_ensemble)

    print(f"\nEnsemble Performance:")
    print(f"  Training MSE: {train_mse:.6f}")
    print(f"  Test MSE:     {test_mse:.6f}")
    print(f"  Training R²:  {train_r2:.6f}")
    print(f"  Test R²:      {test_r2:.6f}")

    # Compare with equal weights
    equal_weights = np.ones(len(models)) / len(models)
    y_test_equal = test_predictions @ equal_weights
    equal_mse = mean_squared_error(y_test, y_test_equal)

    improvement = ((equal_mse - test_mse) / equal_mse) * 100

    print(f"\nComparison with Equal Weights:")
    print(f"  Equal weights MSE: {equal_mse:.6f}")
    print(f"  Optimized MSE:     {test_mse:.6f}")
    print(f"  Improvement:       {improvement:.2f}%")

    print("\n" + "="*60)
    print("Ensemble optimization complete!")
    print("="*60)


if __name__ == "__main__":
    main()
