"""AutoML benchmark framework for comparing different methods.

This module provides tools to compare multiple AutoML methods on the same dataset
and generate comprehensive comparison reports.
"""

import time
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from .base import BaseAutoMLWrapper


class AutoMLBenchmark:
    """Benchmark framework for comparing AutoML methods.

    This class facilitates fair comparison of multiple AutoML methods on the same
    dataset. It tracks performance metrics, training time, inference time, and
    resource usage.

    Features:
        - Fair comparison across methods
        - Multiple evaluation metrics
        - Performance profiling (time, memory)
        - Automatic recommendation
        - Detailed comparison reports

    Example:
        >>> benchmark = AutoMLBenchmark(
        ...     methods=['autosklearn', 'tpot', 'h2o'],
        ...     time_limit=300
        ... )
        >>> results = benchmark.run(X, y, task_type='classification')
        >>> print(benchmark.get_recommendations())
        >>> benchmark.plot_comparison()
    """

    def __init__(
        self,
        methods: Optional[List[str]] = None,
        time_limit: int = 300,
        n_jobs: int = -1,
        random_state: int = 42,
        verbose: int = 1,
        test_size: float = 0.2,
        **kwargs: Any
    ):
        """Initialize the benchmark.

        Args:
            methods: List of methods to compare (None = all available)
            time_limit: Time limit per method in seconds
            n_jobs: Number of parallel jobs
            random_state: Random seed
            verbose: Verbosity level
            test_size: Fraction of data to use for testing
            **kwargs: Additional parameters for AutoML methods
        """
        self.methods = methods or ['autosklearn', 'tpot', 'h2o']
        self.time_limit = time_limit
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.verbose = verbose
        self.test_size = test_size
        self.kwargs = kwargs

        self.results: Dict[str, Dict[str, Any]] = {}
        self._task_type: Optional[str] = None
        self._available_methods: List[str] = []

    def _check_method_availability(self) -> List[str]:
        """Check which methods are available.

        Returns:
            available: List of available method names
        """
        available = []

        for method in self.methods:
            try:
                if method == 'autosklearn':
                    import autosklearn
                    available.append('autosklearn')
                elif method == 'tpot':
                    import tpot
                    available.append('tpot')
                elif method == 'h2o':
                    import h2o
                    available.append('h2o')
            except ImportError:
                if self.verbose:
                    print(f"Warning: {method} is not installed")

        return available

    def _create_optimizer(
        self,
        method: str,
        task_type: str
    ) -> BaseAutoMLWrapper:
        """Create an optimizer for the specified method.

        Args:
            method: Method name
            task_type: 'classification' or 'regression'

        Returns:
            optimizer: Initialized optimizer
        """
        if method == 'autosklearn':
            from .autosklearn_wrapper import AutoSklearnOptimizer
            return AutoSklearnOptimizer(
                time_limit=self.time_limit,
                task_type=task_type,
                n_jobs=self.n_jobs,
                random_state=self.random_state,
                verbose=self.verbose,
                **self.kwargs
            )
        elif method == 'tpot':
            from .tpot_wrapper import TPOTOptimizer
            return TPOTOptimizer(
                time_limit=self.time_limit,
                task_type=task_type,
                n_jobs=self.n_jobs,
                random_state=self.random_state,
                verbose=self.verbose,
                **self.kwargs
            )
        elif method == 'h2o':
            from .h2o_wrapper import H2OAutoMLOptimizer
            return H2OAutoMLOptimizer(
                time_limit=self.time_limit,
                task_type=task_type,
                n_jobs=self.n_jobs,
                random_state=self.random_state,
                verbose=self.verbose,
                **self.kwargs
            )
        else:
            raise ValueError(f"Unknown method: {method}")

    def _calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray],
        task_type: str
    ) -> Dict[str, float]:
        """Calculate evaluation metrics.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (for classification)
            task_type: 'classification' or 'regression'

        Returns:
            metrics: Dictionary of metric scores
        """
        metrics = {}

        if task_type == "classification":
            metrics["accuracy"] = accuracy_score(y_true, y_pred)

            # F1 score (macro average for multi-class)
            try:
                n_classes = len(np.unique(y_true))
                average = 'binary' if n_classes == 2 else 'macro'
                metrics["f1"] = f1_score(y_true, y_pred, average=average)
            except:
                metrics["f1"] = None

            # ROC AUC (for binary classification)
            if y_proba is not None:
                try:
                    n_classes = len(np.unique(y_true))
                    if n_classes == 2:
                        # Binary classification
                        metrics["roc_auc"] = roc_auc_score(y_true, y_proba[:, 1])
                    else:
                        # Multi-class
                        metrics["roc_auc"] = roc_auc_score(
                            y_true, y_proba, multi_class='ovr', average='macro'
                        )
                except Exception as e:
                    metrics["roc_auc"] = None

        else:  # regression
            metrics["r2"] = r2_score(y_true, y_pred)
            metrics["mse"] = mean_squared_error(y_true, y_pred)
            metrics["rmse"] = np.sqrt(metrics["mse"])
            metrics["mae"] = mean_absolute_error(y_true, y_pred)

        return metrics

    def run(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        task_type: str = "classification"
    ) -> pd.DataFrame:
        """Run benchmark on all methods.

        Args:
            X: Features
            y: Targets
            task_type: 'classification' or 'regression'

        Returns:
            results_df: DataFrame with comparison results
        """
        self._task_type = task_type

        if self.verbose:
            print("="*70)
            print("AutoML Benchmark - Method Comparison")
            print("="*70)
            print(f"Dataset: {X.shape[0]} samples, {X.shape[1] if hasattr(X, 'shape') and len(X.shape) > 1 else 'N/A'} features")
            print(f"Task type: {task_type}")
            print(f"Time limit per method: {self.time_limit}s")
            print("="*70)

        # Check available methods
        self._available_methods = self._check_method_availability()

        if not self._available_methods:
            raise RuntimeError("No AutoML methods available. Install at least one.")

        if self.verbose:
            print(f"\nAvailable methods: {', '.join(self._available_methods)}\n")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y if task_type == "classification" else None
        )

        # Benchmark each method
        for method in self._available_methods:
            if self.verbose:
                print(f"\n{'='*70}")
                print(f"Benchmarking: {method.upper()}")
                print(f"{'='*70}")

            try:
                # Create optimizer
                optimizer = self._create_optimizer(method, task_type)

                # Train
                train_start = time.time()
                optimizer.fit(X_train, y_train)
                training_time = time.time() - train_start

                # Predict
                pred_start = time.time()
                y_pred = optimizer.predict(X_test)
                inference_time = time.time() - pred_start

                # Get probabilities for classification
                y_proba = None
                if task_type == "classification":
                    try:
                        y_proba = optimizer.predict_proba(X_test)
                    except:
                        pass

                # Calculate metrics
                metrics = self._calculate_metrics(y_test, y_pred, y_proba, task_type)

                # Store results
                self.results[method] = {
                    "optimizer": optimizer,
                    "training_time": training_time,
                    "inference_time": inference_time,
                    "inference_time_per_sample": inference_time / len(X_test),
                    "metrics": metrics,
                    "success": True,
                    "error": None
                }

                if self.verbose:
                    print(f"\n✓ {method} completed successfully")
                    print(f"  Training time: {training_time:.2f}s")
                    print(f"  Inference time: {inference_time*1000:.2f}ms")
                    print(f"  Metrics: {metrics}")

            except Exception as e:
                if self.verbose:
                    print(f"\n✗ {method} failed: {str(e)}")

                self.results[method] = {
                    "optimizer": None,
                    "training_time": None,
                    "inference_time": None,
                    "inference_time_per_sample": None,
                    "metrics": {},
                    "success": False,
                    "error": str(e)
                }

        if self.verbose:
            print(f"\n{'='*70}")
            print("Benchmark completed!")
            print(f"{'='*70}\n")

        return self.get_results_dataframe()

    def get_results_dataframe(self) -> pd.DataFrame:
        """Get results as a formatted DataFrame.

        Returns:
            results_df: DataFrame with comparison results
        """
        if not self.results:
            return pd.DataFrame()

        rows = []
        for method, result in self.results.items():
            if result["success"]:
                row = {
                    "method": method,
                    "training_time_s": result["training_time"],
                    "inference_time_ms": result["inference_time"] * 1000,
                    "inference_per_sample_ms": result["inference_time_per_sample"] * 1000,
                }
                # Add metrics
                row.update(result["metrics"])
                rows.append(row)
            else:
                rows.append({
                    "method": method,
                    "error": result["error"]
                })

        df = pd.DataFrame(rows)

        # Sort by primary metric
        if self._task_type == "classification" and "accuracy" in df.columns:
            df = df.sort_values("accuracy", ascending=False)
        elif self._task_type == "regression" and "r2" in df.columns:
            df = df.sort_values("r2", ascending=False)

        return df

    def get_recommendations(self) -> Dict[str, Any]:
        """Get recommendations based on benchmark results.

        Returns:
            recommendations: Dictionary with recommendations for different criteria
        """
        if not self.results:
            return {"error": "No results available. Run benchmark first."}

        successful_results = {
            method: result
            for method, result in self.results.items()
            if result["success"]
        }

        if not successful_results:
            return {"error": "All methods failed"}

        recommendations = {}

        # Best accuracy/R²
        if self._task_type == "classification":
            best_acc_method = max(
                successful_results.items(),
                key=lambda x: x[1]["metrics"].get("accuracy", 0)
            )
            recommendations["best_accuracy"] = {
                "method": best_acc_method[0],
                "score": best_acc_method[1]["metrics"]["accuracy"]
            }
        else:
            best_r2_method = max(
                successful_results.items(),
                key=lambda x: x[1]["metrics"].get("r2", -float('inf'))
            )
            recommendations["best_r2"] = {
                "method": best_r2_method[0],
                "score": best_r2_method[1]["metrics"]["r2"]
            }

        # Fastest training
        fastest_train = min(
            successful_results.items(),
            key=lambda x: x[1]["training_time"]
        )
        recommendations["fastest_training"] = {
            "method": fastest_train[0],
            "time": fastest_train[1]["training_time"]
        }

        # Fastest inference
        fastest_inference = min(
            successful_results.items(),
            key=lambda x: x[1]["inference_time_per_sample"]
        )
        recommendations["fastest_inference"] = {
            "method": fastest_inference[0],
            "time_per_sample": fastest_inference[1]["inference_time_per_sample"]
        }

        # Overall recommendation (balanced)
        scores = {}
        for method, result in successful_results.items():
            # Normalize and combine metrics
            if self._task_type == "classification":
                perf_score = result["metrics"].get("accuracy", 0)
            else:
                perf_score = max(0, result["metrics"].get("r2", 0))

            # Penalize longer times
            time_penalty = result["training_time"] / self.time_limit

            scores[method] = perf_score * (1 - 0.3 * time_penalty)

        best_overall = max(scores.items(), key=lambda x: x[1])
        recommendations["overall_best"] = {
            "method": best_overall[0],
            "score": best_overall[1]
        }

        return recommendations

    def get_summary_report(self) -> str:
        """Generate a text summary report.

        Returns:
            report: Formatted summary report
        """
        if not self.results:
            return "No results available. Run benchmark first."

        report = []
        report.append("=" * 70)
        report.append("AutoML Benchmark Summary Report")
        report.append("=" * 70)
        report.append(f"Task type: {self._task_type}")
        report.append(f"Time limit per method: {self.time_limit}s")
        report.append("")

        # Results table
        df = self.get_results_dataframe()
        report.append("Results:")
        report.append(df.to_string(index=False))
        report.append("")

        # Recommendations
        recommendations = self.get_recommendations()
        report.append("Recommendations:")
        report.append("-" * 70)

        for criterion, info in recommendations.items():
            if criterion == "error":
                report.append(f"Error: {info}")
            else:
                criterion_name = criterion.replace("_", " ").title()
                report.append(f"{criterion_name}:")
                for key, value in info.items():
                    report.append(f"  {key}: {value}")
                report.append("")

        report.append("=" * 70)

        return "\n".join(report)

    def export_results(self, output_path: str) -> None:
        """Export results to a CSV file.

        Args:
            output_path: Path to output CSV file
        """
        df = self.get_results_dataframe()
        df.to_csv(output_path, index=False)

        if self.verbose:
            print(f"Results exported to: {output_path}")
