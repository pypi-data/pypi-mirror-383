"""H2O AutoML demonstration script.

This script demonstrates how to use the H2O AutoML wrapper for
distributed machine learning with ensemble stacking.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_wine, load_diabetes
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kaggler.automl import H2OAutoMLOptimizer


def demo_classification():
    """Demonstrate H2O AutoML on classification task."""
    print("="*70)
    print("H2O AutoML Classification Demo - Wine Dataset")
    print("="*70)

    # Load data
    data = load_wine()
    X, y = data.data, data.target

    # Convert to DataFrame for better H2O compatibility
    X_df = pd.DataFrame(X, columns=data.feature_names)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\nDataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")
    print(f"Classes: {len(np.unique(y))}")

    # Create optimizer
    optimizer = H2OAutoMLOptimizer(
        time_limit=120,  # 2 minutes for demo
        task_type='classification',
        max_models=10,
        nfolds=5,
        n_jobs=-1,
        random_state=42,
        verbose=1
    )

    # Train
    print("\n--- Training ---")
    optimizer.fit(X_train, y_train)

    # Evaluate
    print("\n--- Evaluation ---")
    train_score = optimizer.score(X_train, y_train)
    test_score = optimizer.score(X_test, y_test)

    print(f"Train accuracy: {train_score:.4f}")
    print(f"Test accuracy: {test_score:.4f}")

    # Get predictions
    predictions = optimizer.predict(X_test)
    probabilities = optimizer.predict_proba(X_test)

    print(f"\nPredictions shape: {predictions.shape}")
    print(f"Probabilities shape: {probabilities.shape}")

    # Get leaderboard
    print("\n--- Leaderboard (Top 5) ---")
    leaderboard = optimizer.get_leaderboard()
    print(leaderboard.head())

    # Get configuration
    print("\n--- Model Configuration ---")
    config = optimizer.get_config()
    print(f"Library: {config['library']}")
    print(f"Training time: {config['training_time']:.2f}s")
    print(f"Best score: {config.get('best_score', 'N/A')}")
    print(f"Leader model: {config.get('leader_algorithm', 'N/A')}")
    print(f"Models trained: {config.get('n_models_trained', 'N/A')}")

    # Feature importance
    print("\n--- Feature Importance (Top 10) ---")
    importance = optimizer.get_feature_importance()
    if importance:
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        for feature, score in sorted_importance[:10]:
            print(f"  {feature}: {score:.4f}")

    # Get specific models from leaderboard
    print("\n--- Leaderboard Models ---")
    try:
        best_model = optimizer.get_model_by_rank(0)
        print(f"Best model: {best_model.model_id}")

        if len(leaderboard) > 1:
            second_model = optimizer.get_model_by_rank(1)
            print(f"Second best: {second_model.model_id}")
    except Exception as e:
        print(f"Could not retrieve models: {e}")

    # Cleanup
    print("\n--- Cleanup ---")
    optimizer.shutdown()
    print("H2O cluster shut down")

    print("\n" + "="*70)
    print("H2O AutoML demo completed!")
    print("="*70)


def demo_regression():
    """Demonstrate H2O AutoML on regression task."""
    print("\n" + "="*70)
    print("H2O AutoML Regression Demo - Diabetes Dataset")
    print("="*70)

    # Load data
    data = load_diabetes()
    X, y = data.data, data.target

    # Convert to DataFrame
    X_df = pd.DataFrame(X, columns=data.feature_names)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y, test_size=0.2, random_state=42
    )

    print(f"\nDataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")

    # Create optimizer
    optimizer = H2OAutoMLOptimizer(
        time_limit=120,  # 2 minutes for demo
        task_type='regression',
        max_models=10,
        nfolds=5,
        n_jobs=-1,
        random_state=42,
        verbose=1
    )

    # Train
    print("\n--- Training ---")
    optimizer.fit(X_train, y_train)

    # Evaluate
    print("\n--- Evaluation ---")
    train_score = optimizer.score(X_train, y_train)
    test_score = optimizer.score(X_test, y_test)

    print(f"Train R²: {train_score:.4f}")
    print(f"Test R²: {test_score:.4f}")

    # Get predictions
    predictions = optimizer.predict(X_test)
    print(f"\nSample predictions: {predictions[:5]}")
    print(f"Sample actual: {y_test.values[:5]}")

    # Get leaderboard
    print("\n--- Leaderboard ---")
    leaderboard = optimizer.get_leaderboard()
    print(leaderboard)

    # Cleanup
    optimizer.shutdown()

    print("\n" + "="*70)
    print("Regression demo completed!")
    print("="*70)


if __name__ == "__main__":
    try:
        demo_classification()
        demo_regression()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This demo requires H2O to be installed:")
        print("  pip install h2o")
