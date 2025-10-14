"""
Benchmark Suite

Standardized benchmarks for research datasets with reproducibility
and leaderboard management.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from kaggler.research.leaderboard import ResearchLeaderboard, MetricType
from kaggler.research.reproducibility import ReproducibilityManager


class BenchmarkTask(str, Enum):
    """Types of benchmark tasks"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RANKING = "ranking"
    GENERATION = "generation"
    DETECTION = "detection"
    SEGMENTATION = "segmentation"
    FORECASTING = "forecasting"


@dataclass
class StandardizedBenchmark:
    """
    Standardized benchmark definition

    Attributes:
        benchmark_id: Unique benchmark identifier
        name: Benchmark name
        description: Detailed description
        dataset_id: Associated dataset
        task: Type of task
        metric: Primary metric name
        metric_type: Optimization direction
        baseline_score: Baseline score
        created_at: Creation timestamp
        created_by: Creator ID
        evaluation_protocol: Evaluation instructions
        train_split: Training split specification
        test_split: Test split specification
        validation_split: Validation split specification
        constraints: Any constraints (time, memory, etc.)
        metadata: Additional metadata
    """
    benchmark_id: str
    name: str
    description: str
    dataset_id: str
    task: BenchmarkTask
    metric: str
    metric_type: MetricType
    baseline_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    evaluation_protocol: str = ""
    train_split: str = "train"
    test_split: str = "test"
    validation_split: str = "val"
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "benchmark_id": self.benchmark_id,
            "name": self.name,
            "description": self.description,
            "dataset_id": self.dataset_id,
            "task": self.task.value,
            "metric": self.metric,
            "metric_type": self.metric_type.value,
            "baseline_score": self.baseline_score,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "evaluation_protocol": self.evaluation_protocol,
            "train_split": self.train_split,
            "test_split": self.test_split,
            "validation_split": self.validation_split,
            "constraints": self.constraints,
            "metadata": self.metadata
        }


class BenchmarkManager:
    """
    Manager for research benchmarks

    Handles benchmark creation, submission, evaluation, and leaderboards.
    """

    def __init__(self):
        self._benchmarks: Dict[str, StandardizedBenchmark] = {}
        self._leaderboards: Dict[str, ResearchLeaderboard] = {}
        self._reproducibility_manager = ReproducibilityManager()

    def create_benchmark(
        self,
        name: str,
        description: str,
        dataset_id: str,
        task: BenchmarkTask,
        metric: str,
        metric_type: MetricType,
        baseline_score: float,
        created_by: str,
        evaluation_protocol: str = "",
        **kwargs
    ) -> StandardizedBenchmark:
        """
        Create new benchmark

        Args:
            name: Benchmark name
            description: Detailed description
            dataset_id: Associated dataset ID
            task: Benchmark task type
            metric: Primary metric
            metric_type: Optimization direction
            baseline_score: Baseline performance
            created_by: Creator user ID
            evaluation_protocol: Evaluation instructions
            **kwargs: Additional benchmark parameters

        Returns:
            Created StandardizedBenchmark
        """
        import hashlib

        benchmark_id = hashlib.md5(
            f"{name}_{dataset_id}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        benchmark = StandardizedBenchmark(
            benchmark_id=benchmark_id,
            name=name,
            description=description,
            dataset_id=dataset_id,
            task=task,
            metric=metric,
            metric_type=metric_type,
            baseline_score=baseline_score,
            created_by=created_by,
            evaluation_protocol=evaluation_protocol,
            **kwargs
        )

        self._benchmarks[benchmark_id] = benchmark

        # Create associated leaderboard
        self._leaderboards[benchmark_id] = ResearchLeaderboard(
            benchmark_id=benchmark_id,
            metric_type=metric_type
        )

        return benchmark

    def get_benchmark(self, benchmark_id: str) -> Optional[StandardizedBenchmark]:
        """Get benchmark by ID"""
        return self._benchmarks.get(benchmark_id)

    def list_benchmarks(
        self,
        dataset_id: Optional[str] = None,
        task: Optional[BenchmarkTask] = None
    ) -> List[StandardizedBenchmark]:
        """
        List benchmarks with optional filters

        Args:
            dataset_id: Filter by dataset
            task: Filter by task type

        Returns:
            List of benchmarks
        """
        benchmarks = list(self._benchmarks.values())

        if dataset_id:
            benchmarks = [b for b in benchmarks if b.dataset_id == dataset_id]
        if task:
            benchmarks = [b for b in benchmarks if b.task == task]

        return benchmarks

    def submit_result(
        self,
        benchmark_id: str,
        user_id: str,
        institution: str,
        score: float,
        method: str,
        description: str,
        code: Optional[str] = None,
        data: Optional[bytes] = None,
        config: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        code_url: Optional[str] = None,
        paper_url: Optional[str] = None,
        **metadata
    ) -> Optional[Dict[str, Any]]:
        """
        Submit result to benchmark

        Args:
            benchmark_id: Benchmark identifier
            user_id: User submitting
            institution: User's institution
            score: Achieved score
            method: Method name
            description: Method description
            code: Code used (for reproducibility)
            data: Data checksum input
            config: Configuration used
            seed: Random seed
            code_url: URL to code
            paper_url: URL to paper
            **metadata: Additional metadata

        Returns:
            Dictionary with submission details or None if benchmark not found
        """
        benchmark = self._benchmarks.get(benchmark_id)
        if not benchmark:
            return None

        leaderboard = self._leaderboards.get(benchmark_id)
        if not leaderboard:
            return None

        # Create reproducibility checksum if provided
        checksum = None
        if code and data and config and seed is not None:
            exp_checksum = self._reproducibility_manager.create_checksum(
                experiment_id=f"{benchmark_id}_{user_id}_{datetime.utcnow().timestamp()}",
                code=code,
                data=data,
                config=config,
                seed=seed
            )
            checksum = exp_checksum.compute_full_checksum()

        # Submit to leaderboard
        entry = leaderboard.submit_result(
            user_id=user_id,
            institution=institution,
            score=score,
            method=method,
            description=description,
            code_url=code_url,
            paper_url=paper_url,
            checksum=checksum,
            **metadata
        )

        return {
            "entry_id": entry.entry_id,
            "benchmark_id": benchmark_id,
            "score": score,
            "checksum": checksum,
            "submission_date": entry.submission_date.isoformat()
        }

    def verify_submission(
        self,
        benchmark_id: str,
        entry_id: str,
        code: str,
        data: bytes,
        config: Dict[str, Any],
        seed: int
    ) -> bool:
        """
        Verify submission reproducibility

        Args:
            benchmark_id: Benchmark identifier
            entry_id: Entry to verify
            code: Code to verify
            data: Data to verify
            config: Configuration to verify
            seed: Seed to verify

        Returns:
            True if verification successful
        """
        leaderboard = self._leaderboards.get(benchmark_id)
        if not leaderboard:
            return False

        entry = leaderboard.get_entry(entry_id)
        if not entry or not entry.checksum:
            return False

        # Verify with reproducibility manager
        experiment_id = f"verify_{entry_id}"
        new_checksum = self._reproducibility_manager.create_checksum(
            experiment_id=experiment_id,
            code=code,
            data=data,
            config=config,
            seed=seed
        )

        is_reproducible = new_checksum.compute_full_checksum() == entry.checksum

        if is_reproducible:
            leaderboard.mark_reproducible(entry_id, True)
            leaderboard.verify_entry(entry_id, True)

        return is_reproducible

    def get_leaderboard(
        self,
        benchmark_id: str,
        top_k: Optional[int] = None,
        verified_only: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get leaderboard for benchmark

        Args:
            benchmark_id: Benchmark identifier
            top_k: Return top K entries
            verified_only: Only verified entries

        Returns:
            List of leaderboard entries or None
        """
        leaderboard = self._leaderboards.get(benchmark_id)
        if not leaderboard:
            return None

        entries = leaderboard.get_rankings(
            top_k=top_k,
            verified_only=verified_only
        )

        return [e.to_dict() for e in entries]

    def get_benchmark_statistics(self, benchmark_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for benchmark

        Args:
            benchmark_id: Benchmark identifier

        Returns:
            Dictionary with statistics or None
        """
        benchmark = self._benchmarks.get(benchmark_id)
        leaderboard = self._leaderboards.get(benchmark_id)

        if not benchmark or not leaderboard:
            return None

        stats = leaderboard.get_statistics()
        stats["benchmark_name"] = benchmark.name
        stats["benchmark_task"] = benchmark.task.value
        stats["baseline_score"] = benchmark.baseline_score

        return stats

    def delete_benchmark(self, benchmark_id: str) -> bool:
        """
        Delete benchmark

        Args:
            benchmark_id: Benchmark identifier

        Returns:
            True if deleted
        """
        if benchmark_id in self._benchmarks:
            del self._benchmarks[benchmark_id]
            if benchmark_id in self._leaderboards:
                del self._leaderboards[benchmark_id]
            return True
        return False

    def export_benchmark(self, benchmark_id: str, format: str = "json") -> Optional[str]:
        """
        Export benchmark and leaderboard

        Args:
            benchmark_id: Benchmark identifier
            format: Export format (json)

        Returns:
            Serialized benchmark data or None
        """
        import json

        benchmark = self._benchmarks.get(benchmark_id)
        leaderboard = self._leaderboards.get(benchmark_id)

        if not benchmark:
            return None

        data = {
            "benchmark": benchmark.to_dict(),
            "leaderboard": leaderboard.get_rankings() if leaderboard else [],
            "statistics": self.get_benchmark_statistics(benchmark_id)
        }

        if format == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
