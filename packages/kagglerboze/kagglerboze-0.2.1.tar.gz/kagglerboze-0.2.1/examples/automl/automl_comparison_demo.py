"""AutoML Comparison Demo.

This example demonstrates how to use the AutoML integration to compare
different AutoML methods on the Titanic dataset.

Features demonstrated:
1. Loading and preprocessing Titanic dataset
2. Running all 3 AutoML methods (Auto-sklearn, TPOT, H2O)
3. Comparing results with benchmarking framework
4. Generating recommendations
5. Using the Hybrid strategy
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from kaggler.automl import (
    AutoMLBenchmark,
    HybridAutoML,
    check_installation,
    create_optimizer,
    get_available_methods,
)


def load_titanic_data():
    """Load and preprocess Titanic dataset.

    Returns:
        X: Features
        y: Target (Survived)
    """
    print("Loading Titanic dataset...")

    # Create a simple Titanic dataset (if not available, use synthetic)
    try:
        # Try to load from seaborn
        import seaborn as sns
        titanic = sns.load_dataset('titanic')
    except:
        # Create synthetic Titanic-like data
        print("Creating synthetic Titanic-like data...")
        np.random.seed(42)
        n_samples = 891

        titanic = pd.DataFrame({
            'pclass': np.random.choice([1, 2, 3], n_samples),
            'sex': np.random.choice(['male', 'female'], n_samples),
            'age': np.random.normal(30, 15, n_samples).clip(1, 80),
            'sibsp': np.random.poisson(0.5, n_samples),
            'parch': np.random.poisson(0.4, n_samples),
            'fare': np.random.gamma(2, 15, n_samples),
            'embarked': np.random.choice(['S', 'C', 'Q'], n_samples),
            'survived': np.random.choice([0, 1], n_samples)
        })

    # Select features
    features = ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked']

    # Prepare data
    X = titanic[features].copy()
    y = titanic['survived'] if 'survived' in titanic.columns else titanic['Survived']

    # Handle missing values
    X['age'] = X['age'].fillna(X['age'].median())
    X['embarked'] = X['embarked'].fillna(X['embarked'].mode()[0])
    X['fare'] = X['fare'].fillna(X['fare'].median())

    # Encode categorical variables
    le = LabelEncoder()
    X['sex'] = le.fit_transform(X['sex'])

    if X['embarked'].dtype == 'object':
        X['embarked'] = le.fit_transform(X['embarked'])

    print(f"Dataset shape: {X.shape}")
    print(f"Survival rate: {y.mean():.2%}")

    return X, y


def demo_single_method():
    """Demo: Using a single AutoML method."""
    print("\n" + "="*70)
    print("DEMO 1: Single AutoML Method")
    print("="*70)

    X, y = load_titanic_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Get available methods
    available = get_available_methods()
    if not available:
        print("\nNo AutoML methods available. Please install at least one:")
        print("  pip install auto-sklearn")
        print("  pip install tpot")
        print("  pip install h2o")
        return

    print(f"\nAvailable methods: {', '.join(available)}")

    # Use the first available method
    method = available[0]
    print(f"\nUsing: {method}")

    # Create optimizer
    optimizer = create_optimizer(
        method=method,
        time_limit=120,  # 2 minutes for demo
        task_type='classification',
        verbose=1
    )

    # Train
    print("\nTraining...")
    optimizer.fit(X_train, y_train)

    # Evaluate
    score = optimizer.score(X_test, y_test)
    print(f"\nTest accuracy: {score:.4f}")

    # Get configuration
    config = optimizer.get_config()
    print(f"\nTraining time: {config['training_time']:.2f}s")

    # Get feature importance
    importance = optimizer.get_feature_importance()
    if importance:
        print("\nFeature importance:")
        sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        for feature, imp in sorted_imp[:5]:
            print(f"  {feature}: {imp:.4f}")


def demo_benchmark():
    """Demo: Benchmark multiple AutoML methods."""
    print("\n" + "="*70)
    print("DEMO 2: Benchmark Comparison")
    print("="*70)

    X, y = load_titanic_data()

    # Create benchmark
    benchmark = AutoMLBenchmark(
        methods=['autosklearn', 'tpot', 'h2o'],  # Will use only available ones
        time_limit=120,  # 2 minutes per method
        verbose=1
    )

    # Run benchmark
    print("\nRunning benchmark...")
    results_df = benchmark.run(X, y, task_type='classification')

    # Display results
    print("\n" + "="*70)
    print("BENCHMARK RESULTS")
    print("="*70)
    print(results_df.to_string(index=False))

    # Get recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)

    recommendations = benchmark.get_recommendations()
    for criterion, info in recommendations.items():
        if criterion == "error":
            print(f"Error: {info}")
        else:
            criterion_name = criterion.replace("_", " ").title()
            print(f"\n{criterion_name}:")
            for key, value in info.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")

    # Export results
    output_path = Path(__file__).parent / "benchmark_results.csv"
    benchmark.export_results(str(output_path))
    print(f"\nResults exported to: {output_path}")


def demo_hybrid_strategy():
    """Demo: Hybrid AutoML with automatic routing."""
    print("\n" + "="*70)
    print("DEMO 3: Hybrid AutoML Strategy")
    print("="*70)

    X, y = load_titanic_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Create hybrid optimizer
    hybrid = HybridAutoML(
        time_limit=120,
        task_type='classification',
        ensemble_methods=False,  # Single method for demo
        verbose=1
    )

    # Train
    print("\nTraining with Hybrid AutoML...")
    hybrid.fit(X_train, y_train)

    # Get routing info
    routing_info = hybrid.get_routing_info()
    print("\n" + "="*70)
    print("ROUTING INFORMATION")
    print("="*70)
    for key, value in routing_info.items():
        print(f"{key}: {value}")

    # Evaluate
    score = hybrid.score(X_test, y_test)
    print(f"\nTest accuracy: {score:.4f}")

    # Try ensemble mode
    print("\n" + "-"*70)
    print("Trying Ensemble Mode")
    print("-"*70)

    hybrid_ensemble = HybridAutoML(
        time_limit=180,  # 3 minutes total
        task_type='classification',
        ensemble_methods=True,  # Enable ensemble
        verbose=1
    )

    print("\nTraining ensemble...")
    hybrid_ensemble.fit(X_train, y_train)

    # Evaluate
    score_ensemble = hybrid_ensemble.score(X_test, y_test)
    print(f"\nEnsemble test accuracy: {score_ensemble:.4f}")

    # Compare
    print("\n" + "="*70)
    print("Single vs Ensemble Comparison:")
    print(f"  Single method: {score:.4f}")
    print(f"  Ensemble:      {score_ensemble:.4f}")
    print(f"  Improvement:   {(score_ensemble - score)*100:.2f}%")


def main():
    """Run all demos."""
    print("="*70)
    print("AutoML Integration - Comprehensive Demo")
    print("="*70)

    # Check installation status
    check_installation()

    # Check if any methods are available
    if not get_available_methods():
        print("\n" + "!"*70)
        print("WARNING: No AutoML methods are installed!")
        print("!"*70)
        print("\nPlease install at least one method:")
        print("  pip install auto-sklearn  # For Auto-sklearn")
        print("  pip install tpot          # For TPOT")
        print("  pip install h2o           # For H2O AutoML")
        print("\nOr install all:")
        print("  pip install kagglerboze[automl]")
        return

    try:
        # Run demos
        demo_single_method()
        input("\nPress Enter to continue to benchmark comparison...")

        demo_benchmark()
        input("\nPress Enter to continue to hybrid strategy demo...")

        demo_hybrid_strategy()

        print("\n" + "="*70)
        print("All demos completed successfully!")
        print("="*70)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
