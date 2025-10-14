"""TPOT demonstration script.

This script demonstrates how to use the TPOT wrapper for
genetic programming-based pipeline optimization.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris, load_boston
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kaggler.automl import TPOTOptimizer


def demo_classification():
    """Demonstrate TPOT on classification task."""
    print("="*70)
    print("TPOT Classification Demo - Iris Dataset")
    print("="*70)

    # Load data
    data = load_iris()
    X, y = data.data, data.target

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\nDataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")
    print(f"Classes: {len(np.unique(y))}")

    # Create optimizer
    optimizer = TPOTOptimizer(
        time_limit=120,  # 2 minutes for demo
        task_type='classification',
        population_size=20,  # Smaller for demo
        generations=5,
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

    print(f"\nPredictions: {predictions}")
    print(f"Probabilities shape: {probabilities.shape}")

    # Get best pipeline
    print("\n--- Best Pipeline ---")
    pipeline = optimizer.get_pipeline()
    print(pipeline)

    # Export pipeline
    output_file = "/tmp/tpot_iris_pipeline.py"
    optimizer.export_pipeline(output_file)
    print(f"\nPipeline exported to: {output_file}")

    # Get configuration
    print("\n--- Configuration ---")
    config = optimizer.get_config()
    print(f"Library: {config['library']}")
    print(f"Training time: {config['training_time']:.2f}s")
    print(f"Best score: {config.get('best_score', 'N/A')}")
    print(f"Evaluated individuals: {config.get('n_evaluated_individuals', 'N/A')}")

    # Get evaluated pipelines
    print("\n--- Evaluated Pipelines (Top 5) ---")
    pipelines_df = optimizer.get_evaluated_pipelines()
    if not pipelines_df.empty:
        print(pipelines_df.head())

    # Feature importance
    print("\n--- Feature Importance ---")
    importance = optimizer.get_feature_importance()
    if importance:
        for feature, score in importance.items():
            feature_name = data.feature_names[int(feature.split('_')[1])]
            print(f"  {feature_name}: {score:.4f}")

    # Pareto front
    print("\n--- Pareto Front ---")
    pareto = optimizer.get_pareto_front()
    if pareto:
        print(f"Number of Pareto-optimal solutions: {len(pareto['pipelines'])}")

    print("\n" + "="*70)
    print("TPOT demo completed!")
    print("="*70)


def demo_regression():
    """Demonstrate TPOT on regression task."""
    print("\n" + "="*70)
    print("TPOT Regression Demo - Boston Housing Dataset")
    print("="*70)

    try:
        # Load data (using load_boston or alternative)
        try:
            data = load_boston()
            X, y = data.data, data.target
        except:
            # load_boston is deprecated, use alternative
            from sklearn.datasets import fetch_california_housing
            data = fetch_california_housing()
            X, y = data.data[:500], data.target[:500]  # Smaller subset for demo

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        print(f"\nDataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")

        # Create optimizer
        optimizer = TPOTOptimizer(
            time_limit=120,  # 2 minutes for demo
            task_type='regression',
            population_size=20,
            generations=5,
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
        print(f"Sample actual: {y_test[:5]}")

        print("\n" + "="*70)
        print("Regression demo completed!")
        print("="*70)

    except Exception as e:
        print(f"Regression demo skipped: {e}")


if __name__ == "__main__":
    try:
        demo_classification()
        demo_regression()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This demo requires TPOT to be installed:")
        print("  pip install tpot")
