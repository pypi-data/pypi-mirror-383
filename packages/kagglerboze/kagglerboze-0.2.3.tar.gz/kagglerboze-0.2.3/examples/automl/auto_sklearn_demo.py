"""Auto-sklearn demonstration script.

This script demonstrates how to use the Auto-sklearn wrapper for
automated machine learning with Bayesian optimization.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer, load_diabetes
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kaggler.automl import AutoSklearnOptimizer


def demo_classification():
    """Demonstrate Auto-sklearn on classification task."""
    print("="*70)
    print("Auto-sklearn Classification Demo - Breast Cancer Dataset")
    print("="*70)

    # Load data
    data = load_breast_cancer()
    X, y = data.data, data.target

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nDataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")

    # Create optimizer
    optimizer = AutoSklearnOptimizer(
        time_limit=120,  # 2 minutes for demo
        task_type='classification',
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

    # Get configuration
    print("\n--- Model Configuration ---")
    config = optimizer.get_config()
    print(f"Library: {config['library']}")
    print(f"Training time: {config['training_time']:.2f}s")
    print(f"Best CV score: {config.get('best_score', 'N/A')}")
    print(f"Ensemble members: {config.get('n_ensemble_members', 'N/A')}")

    # Get leaderboard
    print("\n--- Ensemble Leaderboard ---")
    leaderboard = optimizer.get_leaderboard()
    print(leaderboard.head())

    # Feature importance
    print("\n--- Feature Importance (Top 10) ---")
    importance = optimizer.get_feature_importance()
    if importance:
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        for feature, score in sorted_importance[:10]:
            feature_name = data.feature_names[int(feature.split('_')[1])]
            print(f"  {feature_name}: {score:.4f}")

    print("\n" + "="*70)
    print("Auto-sklearn demo completed!")
    print("="*70)


def demo_regression():
    """Demonstrate Auto-sklearn on regression task."""
    print("\n" + "="*70)
    print("Auto-sklearn Regression Demo - Diabetes Dataset")
    print("="*70)

    # Load data
    data = load_diabetes()
    X, y = data.data, data.target

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nDataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")

    # Create optimizer
    optimizer = AutoSklearnOptimizer(
        time_limit=120,  # 2 minutes for demo
        task_type='regression',
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
    print(f"\nPredictions: {predictions[:5]}")
    print(f"Actual: {y_test[:5]}")

    print("\n" + "="*70)
    print("Regression demo completed!")
    print("="*70)


if __name__ == "__main__":
    try:
        demo_classification()
        demo_regression()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This demo requires Auto-sklearn to be installed:")
        print("  pip install auto-sklearn")
