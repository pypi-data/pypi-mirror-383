"""
Neural Network Hyperparameter Tuning with COO
"""

import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
from coo_optimizer import COO


def main():
    """Example of tuning neural network hyperparameters"""

    print("="*60)
    print("Neural Network Hyperparameter Tuning with COO")
    print("="*60)

    # Generate synthetic data
    print("\nGenerating synthetic regression dataset...")
    X, y = make_regression(
        n_samples=500,
        n_features=10,
        noise=10.0,
        random_state=42
    )

    # Preprocess
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()
    X = scaler_X.fit_transform(X)
    y = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")

    # Define evaluation function
    def evaluate_nn(params):
        """
        Evaluate neural network with given hyperparameters.
        Returns negative MSE for maximization.
        """
        learning_rate, hidden_size, alpha = params

        # Clip to valid ranges
        learning_rate = float(np.clip(learning_rate, 1e-4, 1e-1))
        hidden_size = int(np.clip(round(hidden_size), 10, 100))
        alpha = float(np.clip(alpha, 1e-6, 1e-2))

        try:
            model = MLPRegressor(
                hidden_layer_sizes=(hidden_size,),
                learning_rate_init=learning_rate,
                alpha=alpha,
                max_iter=500,
                random_state=42,
                early_stopping=True
            )

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)

            return -mse  # Negative for maximization

        except:
            return -1e10  # Bad fitness if training fails

    # Define hyperparameter bounds
    bounds = [
        (1e-4, 1e-1),  # learning_rate
        (10, 100),     # hidden_layer_size
        (1e-6, 1e-2)   # alpha (L2 regularization)
    ]

    print("\nHyperparameter search space:")
    print(f"  Learning rate: [{bounds[0][0]:.6f}, {bounds[0][1]:.6f}]")
    print(f"  Hidden units:  [{bounds[1][0]}, {bounds[1][1]}]")
    print(f"  Alpha (L2):    [{bounds[2][0]:.6e}, {bounds[2][1]:.6e}]")

    # Optimize
    print("\nOptimizing hyperparameters with COO...")
    optimizer = COO(
        bounds=bounds,
        max_iterations=30,
        n_packs=2,
        init_pack_size=12,
        surrogate_enabled=True,
        random_state=42,
        verbose=True
    )

    best_params, best_fitness, history, diagnostics = optimizer.optimize(
        evaluate_nn)

    # Extract best hyperparameters
    best_lr, best_hidden, best_alpha = best_params
    best_hidden = int(round(best_hidden))

    print("\n" + "="*60)
    print("OPTIMIZATION RESULTS")
    print("="*60)
    print(f"Best Hyperparameters Found:")
    print(f"  Learning Rate: {best_lr:.6e}")
    print(f"  Hidden Units:  {best_hidden}")
    print(f"  Alpha (L2):    {best_alpha:.6e}")
    print(f"\nBest Fitness (negative MSE): {best_fitness:.6f}")
    print(f"Function Evaluations: {diagnostics['cache_size']}")

    # Train final model with best hyperparameters
    print("\n" + "="*60)
    print("FINAL MODEL EVALUATION")
    print("="*60)

    final_model = MLPRegressor(
        hidden_layer_sizes=(best_hidden,),
        learning_rate_init=best_lr,
        alpha=best_alpha,
        max_iter=1000,
        random_state=42
    )

    final_model.fit(X_train, y_train)

    # Evaluate on train and test
    y_train_pred = final_model.predict(X_train)
    y_test_pred = final_model.predict(X_test)

    train_mse = mean_squared_error(y_train, y_train_pred)
    test_mse = mean_squared_error(y_test, y_test_pred)
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)

    print(f"\nTraining Performance:")
    print(f"  MSE: {train_mse:.6f}")
    print(f"  R²:  {train_r2:.6f}")

    print(f"\nTest Performance:")
    print(f"  MSE: {test_mse:.6f}")
    print(f"  R²:  {test_r2:.6f}")

    print("\n" + "="*60)
    print("Hyperparameter tuning complete!")
    print("="*60)


if __name__ == "__main__":
    main()
