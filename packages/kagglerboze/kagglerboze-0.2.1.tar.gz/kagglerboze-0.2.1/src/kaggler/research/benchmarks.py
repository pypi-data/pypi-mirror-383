"""
Benchmark Runner for Research Partnerships

Provides BenchmarkRunner class for executing standardized benchmarks
with reproducibility guarantees and leaderboard integration.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json

from kaggler.research.benchmark_suite import (
    BenchmarkManager,
    StandardizedBenchmark,
    BenchmarkTask
)
from kaggler.research.leaderboard import MetricType
from kaggler.research.reproducibility import ReproducibilityManager


class TaskType(str, Enum):
    """Standard task types for benchmarks"""
    TEXT_CLASSIFICATION = "text_classification"
    NER = "ner"  # Named Entity Recognition
    SENTIMENT_ANALYSIS = "sentiment"
    TABULAR_PREDICTION = "tabular_prediction"
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    TIME_SERIES_FORECASTING = "time_series"
    REGRESSION = "regression"


@dataclass
class BenchmarkResult:
    """
    Result from running a benchmark

    Attributes:
        result_id: Unique result identifier
        benchmark_id: Associated benchmark
        user_id: User who ran benchmark
        score: Achieved score
        metrics: All computed metrics
        predictions: Model predictions
        runtime_seconds: Execution time
        config: Configuration used
        environment: Environment details
        reproducibility_hash: Hash for verification
        timestamp: When benchmark was run
    """
    result_id: str
    benchmark_id: str
    user_id: str
    score: float
    metrics: Dict[str, float] = field(default_factory=dict)
    predictions: Optional[List[Any]] = None
    runtime_seconds: float = 0.0
    config: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    reproducibility_hash: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "result_id": self.result_id,
            "benchmark_id": self.benchmark_id,
            "user_id": self.user_id,
            "score": self.score,
            "metrics": self.metrics,
            "runtime_seconds": self.runtime_seconds,
            "config": self.config,
            "environment": self.environment,
            "reproducibility_hash": self.reproducibility_hash,
            "timestamp": self.timestamp.isoformat()
        }


class BenchmarkRunner:
    """
    Runner for executing standardized benchmarks

    Provides methods to run benchmarks on datasets with standardized
    tasks (text classification, NER, sentiment, tabular prediction, etc.)
    and track results with reproducibility guarantees.
    """

    def __init__(self):
        self._benchmark_manager = BenchmarkManager()
        self._reproducibility_manager = ReproducibilityManager()
        self._results: Dict[str, BenchmarkResult] = {}

    def run_benchmark(
        self,
        benchmark_id: str,
        user_id: str,
        model_fn: Callable,
        dataset: Any,
        config: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None
    ) -> BenchmarkResult:
        """
        Run benchmark on a dataset

        Args:
            benchmark_id: Benchmark identifier
            user_id: User running benchmark
            model_fn: Model function to evaluate
            dataset: Dataset to evaluate on
            config: Configuration dict
            seed: Random seed for reproducibility

        Returns:
            BenchmarkResult with scores and metrics

        Raises:
            ValueError: If benchmark not found
        """
        import time
        import sys
        import platform

        benchmark = self._benchmark_manager.get_benchmark(benchmark_id)
        if not benchmark:
            raise ValueError(f"Benchmark {benchmark_id} not found")

        # Set seed if provided
        if seed is not None:
            self._set_seed(seed)

        # Record start time
        start_time = time.time()

        # Run model
        predictions = model_fn(dataset)

        # Calculate runtime
        runtime = time.time() - start_time

        # Compute metrics
        metrics = self._compute_metrics(
            predictions=predictions,
            ground_truth=getattr(dataset, 'labels', None),
            task=benchmark.task,
            primary_metric=benchmark.metric
        )

        # Get environment info
        environment = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "seed": str(seed) if seed else "none"
        }

        # Create reproducibility hash
        reproducibility_hash = None
        if config and seed is not None:
            # Serialize model and config for hashing
            config_str = json.dumps(config, sort_keys=True)
            hash_input = f"{benchmark_id}_{config_str}_{seed}".encode()
            reproducibility_hash = hashlib.sha256(hash_input).hexdigest()

        # Create result
        result_id = hashlib.md5(
            f"{benchmark_id}_{user_id}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        result = BenchmarkResult(
            result_id=result_id,
            benchmark_id=benchmark_id,
            user_id=user_id,
            score=metrics.get(benchmark.metric, 0.0),
            metrics=metrics,
            predictions=predictions,
            runtime_seconds=runtime,
            config=config or {},
            environment=environment,
            reproducibility_hash=reproducibility_hash
        )

        self._results[result_id] = result
        return result

    def submit_result(
        self,
        result_id: str,
        institution: str,
        method: str,
        description: str,
        code_url: Optional[str] = None,
        paper_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit benchmark result to leaderboard

        Args:
            result_id: Result identifier
            institution: Submitter's institution
            method: Method name
            description: Method description
            code_url: URL to code repository
            paper_url: URL to paper

        Returns:
            Dictionary with submission details

        Raises:
            ValueError: If result not found
        """
        result = self._results.get(result_id)
        if not result:
            raise ValueError(f"Result {result_id} not found")

        submission = self._benchmark_manager.submit_result(
            benchmark_id=result.benchmark_id,
            user_id=result.user_id,
            institution=institution,
            score=result.score,
            method=method,
            description=description,
            code_url=code_url,
            paper_url=paper_url,
            checksum=result.reproducibility_hash
        )

        return submission

    def get_leaderboard(
        self,
        benchmark_id: str,
        top_k: Optional[int] = None,
        verified_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get leaderboard for benchmark

        Args:
            benchmark_id: Benchmark identifier
            top_k: Number of top entries
            verified_only: Only verified entries

        Returns:
            List of leaderboard entries
        """
        return self._benchmark_manager.get_leaderboard(
            benchmark_id=benchmark_id,
            top_k=top_k,
            verified_only=verified_only
        ) or []

    def verify_reproducibility(
        self,
        result_id: str,
        verification_predictions: List[Any]
    ) -> bool:
        """
        Verify that results are reproducible

        Args:
            result_id: Result to verify
            verification_predictions: Predictions from reproduction

        Returns:
            True if reproducible
        """
        result = self._results.get(result_id)
        if not result or not result.predictions:
            return False

        # Compare predictions
        if len(verification_predictions) != len(result.predictions):
            return False

        # Check if predictions match (with tolerance for floats)
        for orig, verify in zip(result.predictions, verification_predictions):
            if isinstance(orig, (int, str)):
                if orig != verify:
                    return False
            elif isinstance(orig, float):
                if abs(orig - verify) > 1e-6:
                    return False

        return True

    def _set_seed(self, seed: int):
        """Set random seeds for reproducibility"""
        import random
        import numpy as np

        random.seed(seed)
        np.random.seed(seed)

        # Try to set torch seed if available
        try:
            import torch
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)
        except ImportError:
            pass

    def _compute_metrics(
        self,
        predictions: List[Any],
        ground_truth: Optional[List[Any]],
        task: BenchmarkTask,
        primary_metric: str
    ) -> Dict[str, float]:
        """
        Compute metrics for predictions

        Args:
            predictions: Model predictions
            ground_truth: True labels
            task: Benchmark task type
            primary_metric: Primary metric to compute

        Returns:
            Dictionary of metric name -> value
        """
        if ground_truth is None:
            return {primary_metric: 0.0}

        metrics = {}

        # Import sklearn metrics
        try:
            from sklearn.metrics import (
                accuracy_score, precision_score, recall_score, f1_score,
                mean_squared_error, mean_absolute_error, r2_score
            )

            if task in [BenchmarkTask.CLASSIFICATION, BenchmarkTask.DETECTION]:
                metrics['accuracy'] = accuracy_score(ground_truth, predictions)
                metrics['precision'] = precision_score(
                    ground_truth, predictions, average='weighted', zero_division=0
                )
                metrics['recall'] = recall_score(
                    ground_truth, predictions, average='weighted', zero_division=0
                )
                metrics['f1'] = f1_score(
                    ground_truth, predictions, average='weighted', zero_division=0
                )

            elif task in [BenchmarkTask.REGRESSION, BenchmarkTask.FORECASTING]:
                metrics['mse'] = mean_squared_error(ground_truth, predictions)
                metrics['mae'] = mean_absolute_error(ground_truth, predictions)
                metrics['r2'] = r2_score(ground_truth, predictions)
                metrics['rmse'] = metrics['mse'] ** 0.5

        except ImportError:
            # Fallback: simple accuracy for classification
            if task in [BenchmarkTask.CLASSIFICATION, BenchmarkTask.DETECTION]:
                correct = sum(p == t for p, t in zip(predictions, ground_truth))
                metrics['accuracy'] = correct / len(predictions)
            elif task in [BenchmarkTask.REGRESSION, BenchmarkTask.FORECASTING]:
                errors = [(p - t) ** 2 for p, t in zip(predictions, ground_truth)]
                metrics['mse'] = sum(errors) / len(errors)

        return metrics

    def create_text_classification_benchmark(
        self,
        name: str,
        dataset_id: str,
        description: str,
        created_by: str,
        num_classes: int,
        baseline_accuracy: float = 0.5
    ) -> StandardizedBenchmark:
        """
        Create text classification benchmark

        Args:
            name: Benchmark name
            dataset_id: Dataset identifier
            description: Description
            created_by: Creator user ID
            num_classes: Number of classes
            baseline_accuracy: Baseline accuracy

        Returns:
            Created benchmark
        """
        return self._benchmark_manager.create_benchmark(
            name=name,
            description=description,
            dataset_id=dataset_id,
            task=BenchmarkTask.CLASSIFICATION,
            metric="accuracy",
            metric_type=MetricType.MAXIMIZE,
            baseline_score=baseline_accuracy,
            created_by=created_by,
            metadata={"num_classes": num_classes, "task_type": "text_classification"}
        )

    def create_ner_benchmark(
        self,
        name: str,
        dataset_id: str,
        description: str,
        created_by: str,
        entity_types: List[str],
        baseline_f1: float = 0.5
    ) -> StandardizedBenchmark:
        """
        Create Named Entity Recognition benchmark

        Args:
            name: Benchmark name
            dataset_id: Dataset identifier
            description: Description
            created_by: Creator user ID
            entity_types: List of entity types
            baseline_f1: Baseline F1 score

        Returns:
            Created benchmark
        """
        return self._benchmark_manager.create_benchmark(
            name=name,
            description=description,
            dataset_id=dataset_id,
            task=BenchmarkTask.DETECTION,
            metric="f1",
            metric_type=MetricType.MAXIMIZE,
            baseline_score=baseline_f1,
            created_by=created_by,
            metadata={"entity_types": entity_types, "task_type": "ner"}
        )

    def create_sentiment_benchmark(
        self,
        name: str,
        dataset_id: str,
        description: str,
        created_by: str,
        sentiment_classes: List[str],
        baseline_accuracy: float = 0.5
    ) -> StandardizedBenchmark:
        """
        Create sentiment analysis benchmark

        Args:
            name: Benchmark name
            dataset_id: Dataset identifier
            description: Description
            created_by: Creator user ID
            sentiment_classes: Sentiment classes (e.g., ['positive', 'negative', 'neutral'])
            baseline_accuracy: Baseline accuracy

        Returns:
            Created benchmark
        """
        return self._benchmark_manager.create_benchmark(
            name=name,
            description=description,
            dataset_id=dataset_id,
            task=BenchmarkTask.CLASSIFICATION,
            metric="accuracy",
            metric_type=MetricType.MAXIMIZE,
            baseline_score=baseline_accuracy,
            created_by=created_by,
            metadata={
                "sentiment_classes": sentiment_classes,
                "task_type": "sentiment_analysis"
            }
        )

    def create_tabular_prediction_benchmark(
        self,
        name: str,
        dataset_id: str,
        description: str,
        created_by: str,
        prediction_type: str,  # "classification" or "regression"
        baseline_score: float,
        metric: str = "accuracy"
    ) -> StandardizedBenchmark:
        """
        Create tabular prediction benchmark

        Args:
            name: Benchmark name
            dataset_id: Dataset identifier
            description: Description
            created_by: Creator user ID
            prediction_type: "classification" or "regression"
            baseline_score: Baseline score
            metric: Primary metric

        Returns:
            Created benchmark
        """
        task = (
            BenchmarkTask.CLASSIFICATION
            if prediction_type == "classification"
            else BenchmarkTask.REGRESSION
        )

        metric_type = (
            MetricType.MAXIMIZE
            if metric in ["accuracy", "f1", "r2", "auc"]
            else MetricType.MINIMIZE
        )

        return self._benchmark_manager.create_benchmark(
            name=name,
            description=description,
            dataset_id=dataset_id,
            task=task,
            metric=metric,
            metric_type=metric_type,
            baseline_score=baseline_score,
            created_by=created_by,
            metadata={
                "prediction_type": prediction_type,
                "task_type": "tabular_prediction"
            }
        )

    def get_result(self, result_id: str) -> Optional[BenchmarkResult]:
        """Get result by ID"""
        return self._results.get(result_id)

    def list_results(
        self,
        benchmark_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[BenchmarkResult]:
        """
        List results with optional filters

        Args:
            benchmark_id: Filter by benchmark
            user_id: Filter by user

        Returns:
            List of results
        """
        results = list(self._results.values())

        if benchmark_id:
            results = [r for r in results if r.benchmark_id == benchmark_id]
        if user_id:
            results = [r for r in results if r.user_id == user_id]

        return results
