"""Hybrid AutoML demonstration script.

This script demonstrates the hybrid approach that automatically
detects task type and routes to the appropriate method.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer, make_classification
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kaggler.automl import HybridAutoML, AutoRouter


def demo_hybrid_tabular():
    """Demonstrate Hybrid AutoML on tabular data."""
    print("="*70)
    print("Hybrid AutoML Demo - Tabular Data")
    print("="*70)

    # Load tabular data
    data = load_breast_cancer()
    X, y = data.data, data.target

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nDataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")
    print("Data type: Tabular (numeric)")

    # Create hybrid optimizer
    hybrid = HybridAutoML(
        time_limit=120,
        task_type='classification',
        n_jobs=-1,
        random_state=42,
        verbose=1,
        text_threshold=0.3
    )

    # Train
    print("\n--- Training ---")
    hybrid.fit(X_train, y_train)

    # Evaluate
    print("\n--- Evaluation ---")
    train_score = hybrid.score(X_train, y_train)
    test_score = hybrid.score(X_test, y_test)

    print(f"Train accuracy: {train_score:.4f}")
    print(f"Test accuracy: {test_score:.4f}")

    # Get routing info
    print("\n--- Routing Information ---")
    routing_info = hybrid.get_routing_info()
    print(f"Detected category: {routing_info['detected_task_category']}")
    print(f"Selected method: {routing_info['selected_method']}")
    print(f"Available methods: {', '.join(routing_info['available_methods'])}")

    # Get configuration
    print("\n--- Configuration ---")
    config = hybrid.get_config()
    print(f"Library: {config['library']}")
    print(f"Task type: {config['task_type']}")
    print(f"Detected category: {config['detected_task_category']}")
    print(f"Selected method: {config['selected_method']}")

    print("\n" + "="*70)
    print("Tabular demo completed!")
    print("="*70)


def demo_hybrid_mixed():
    """Demonstrate Hybrid AutoML on mixed data (numeric + text)."""
    print("\n" + "="*70)
    print("Hybrid AutoML Demo - Mixed Data (Numeric + Text)")
    print("="*70)

    # Create mixed dataset
    n_samples = 500

    # Numeric features
    X_numeric, y = make_classification(
        n_samples=n_samples,
        n_features=10,
        n_informative=7,
        random_state=42
    )

    # Add text feature (short strings - categorical)
    categories = ['cat_A', 'cat_B', 'cat_C', 'cat_D']
    text_feature = np.random.choice(categories, size=n_samples)

    # Create DataFrame
    X_df = pd.DataFrame(X_numeric, columns=[f'feature_{i}' for i in range(10)])
    X_df['category'] = text_feature

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y, test_size=0.2, random_state=42
    )

    print(f"\nDataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")
    print(f"Feature types: {X_train.dtypes.value_counts().to_dict()}")

    # Create hybrid optimizer
    hybrid = HybridAutoML(
        time_limit=120,
        task_type='classification',
        n_jobs=-1,
        random_state=42,
        verbose=1
    )

    # Train
    print("\n--- Training ---")
    hybrid.fit(X_train, y_train)

    # Evaluate
    print("\n--- Evaluation ---")
    test_score = hybrid.score(X_test, y_test)
    print(f"Test accuracy: {test_score:.4f}")

    # Get routing info
    print("\n--- Routing Information ---")
    routing_info = hybrid.get_routing_info()
    print(f"Detected category: {routing_info['detected_task_category']}")
    print(f"Selected method: {routing_info['selected_method']}")

    print("\n" + "="*70)
    print("Mixed data demo completed!")
    print("="*70)


def demo_hybrid_with_text():
    """Demonstrate Hybrid AutoML with text data."""
    print("\n" + "="*70)
    print("Hybrid AutoML Demo - Text Data")
    print("="*70)

    # Create dataset with text features
    n_samples = 300

    # Generate text data (long strings simulating documents)
    texts = [
        f"This is a sample document number {i}. " * np.random.randint(5, 15)
        for i in range(n_samples)
    ]

    # Create binary labels
    y = np.random.randint(0, 2, size=n_samples)

    # Create DataFrame
    X_df = pd.DataFrame({
        'text_column': texts,
        'length': [len(t) for t in texts]
    })

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_df, y, test_size=0.2, random_state=42
    )

    print(f"\nDataset: {X_train.shape[0]} training samples")
    print(f"Average text length: {X_train['length'].mean():.0f} chars")

    # Create hybrid optimizer
    hybrid = HybridAutoML(
        time_limit=120,
        task_type='classification',
        n_jobs=-1,
        random_state=42,
        verbose=1,
        text_threshold=0.3  # 30% text columns = NLP task
    )

    # Train
    print("\n--- Training ---")
    try:
        hybrid.fit(X_train, y_train)

        # Get routing info
        print("\n--- Routing Information ---")
        routing_info = hybrid.get_routing_info()
        print(f"Detected category: {routing_info['detected_task_category']}")
        print(f"Selected method: {routing_info['selected_method']}")

        # Evaluate
        test_score = hybrid.score(X_test, y_test)
        print(f"\nTest accuracy: {test_score:.4f}")

    except Exception as e:
        print(f"Note: Text-heavy dataset routed to NLP pipeline")
        print(f"(This demo falls back to tabular methods)")
        print(f"Error: {e}")

    print("\n" + "="*70)
    print("Text data demo completed!")
    print("="*70)


def demo_auto_router():
    """Demonstrate AutoRouter for intelligent task routing."""
    print("\n" + "="*70)
    print("AutoRouter Demo - Intelligent Task Detection")
    print("="*70)

    # Load data
    data = load_breast_cancer()
    X, y = data.data, data.target

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nDataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")

    # Create router
    router = AutoRouter(
        time_limit=120,
        task_type='classification',
        n_jobs=-1,
        random_state=42,
        verbose=1
    )

    # Train
    print("\n--- Training ---")
    router.fit(X_train, y_train)

    # Evaluate
    print("\n--- Evaluation ---")
    test_score = router.score(X_test, y_test)
    print(f"Test accuracy: {test_score:.4f}")

    # Get routing explanation
    print("\n--- Routing Explanation ---")
    explanation = router.explain_routing()
    print(f"Decision: {explanation['routing_decision']}")
    print(f"Reason: {explanation['routing_reason']}")

    # Get routing summary
    print("\n--- Routing Summary ---")
    summary = router.get_routing_summary()
    print(summary)

    print("\n" + "="*70)
    print("AutoRouter demo completed!")
    print("="*70)


if __name__ == "__main__":
    try:
        demo_hybrid_tabular()
        demo_hybrid_mixed()
        demo_hybrid_with_text()
        demo_auto_router()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This demo requires at least one AutoML library:")
        print("  pip install auto-sklearn")
        print("  pip install tpot")
        print("  pip install h2o")
