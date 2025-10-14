"""AutoML comparison demonstration script.

This script demonstrates how to compare multiple AutoML methods
on the same dataset using the benchmark framework.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kaggler.automl import AutoMLBenchmark, get_available_methods


def demo_comparison():
    """Demonstrate AutoML method comparison."""
    print("="*70)
    print("AutoML Benchmark - Method Comparison Demo")
    print("="*70)

    # Check available methods
    available = get_available_methods()
    print(f"\nAvailable AutoML methods: {', '.join(available) if available else 'None'}")

    if not available:
        print("\nNo AutoML methods available!")
        print("Install at least one of:")
        print("  - Auto-sklearn: pip install auto-sklearn")
        print("  - TPOT: pip install tpot")
        print("  - H2O: pip install h2o")
        return

    # Load dataset
    print("\n" + "="*70)
    print("Loading dataset...")
    data = load_breast_cancer()
    X, y = data.data, data.target

    print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"Task: Binary classification")
    print(f"Classes: {np.unique(y)}")

    # Create benchmark
    print("\n" + "="*70)
    print("Creating benchmark...")
    benchmark = AutoMLBenchmark(
        methods=available,  # Use all available methods
        time_limit=120,  # 2 minutes per method
        n_jobs=-1,
        random_state=42,
        test_size=0.2,
        verbose=1
    )

    # Run benchmark
    print("\n" + "="*70)
    print("Running benchmark (this may take several minutes)...")
    results_df = benchmark.run(X, y, task_type='classification')

    # Display results
    print("\n" + "="*70)
    print("Benchmark Results")
    print("="*70)
    print(results_df.to_string(index=False))

    # Get recommendations
    print("\n" + "="*70)
    print("Recommendations")
    print("="*70)
    recommendations = benchmark.get_recommendations()

    for criterion, info in recommendations.items():
        if criterion == "error":
            print(f"\nError: {info}")
        else:
            criterion_name = criterion.replace("_", " ").title()
            print(f"\n{criterion_name}:")
            for key, value in info.items():
                print(f"  {key}: {value}")

    # Generate full report
    print("\n" + "="*70)
    print("Full Summary Report")
    print("="*70)
    report = benchmark.get_summary_report()
    print(report)

    # Export results
    output_path = "/tmp/automl_benchmark_results.csv"
    benchmark.export_results(output_path)
    print(f"\n✓ Results exported to: {output_path}")

    print("\n" + "="*70)
    print("Benchmark demo completed!")
    print("="*70)


def demo_quick_comparison():
    """Quick comparison with smaller dataset."""
    print("\n" + "="*70)
    print("Quick Comparison Demo (Smaller Dataset)")
    print("="*70)

    # Create small synthetic dataset
    from sklearn.datasets import make_classification

    X, y = make_classification(
        n_samples=500,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        random_state=42
    )

    print(f"\nDataset: {X.shape[0]} samples, {X.shape[1]} features")

    # Check available methods
    available = get_available_methods()

    if not available:
        print("No AutoML methods available. Skipping...")
        return

    # Create benchmark with shorter time
    benchmark = AutoMLBenchmark(
        methods=available,
        time_limit=60,  # 1 minute per method
        n_jobs=-1,
        random_state=42,
        test_size=0.2,
        verbose=0  # Less verbose
    )

    # Run benchmark
    results_df = benchmark.run(X, y, task_type='classification')

    # Display results
    print("\nResults:")
    print(results_df.to_string(index=False))

    # Quick recommendation
    recommendations = benchmark.get_recommendations()
    if "overall_best" in recommendations:
        best = recommendations["overall_best"]
        print(f"\n✓ Recommended method: {best['method']} (score: {best['score']:.4f})")

    print("\n" + "="*70)
    print("Quick comparison completed!")
    print("="*70)


if __name__ == "__main__":
    try:
        demo_comparison()
        demo_quick_comparison()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This demo requires at least one AutoML library:")
        print("  pip install auto-sklearn")
        print("  pip install tpot")
        print("  pip install h2o")
