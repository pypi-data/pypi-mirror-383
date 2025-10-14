"""
Contribution Tracking for Collaborative Evolution

Tracks worker contributions and assigns credit for best individuals.
Enables fair recognition and adaptive resource allocation.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time
import json


@dataclass
class ContributionRecord:
    """Records a single contribution from a worker"""
    worker_id: str
    individual_id: str
    generation: int
    fitness_scores: Dict[str, float]
    timestamp: float = field(default_factory=time.time)
    contribution_type: str = "individual"  # individual, population, improvement
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "worker_id": self.worker_id,
            "individual_id": self.individual_id,
            "generation": self.generation,
            "fitness_scores": self.fitness_scores,
            "timestamp": self.timestamp,
            "contribution_type": self.contribution_type,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContributionRecord":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class WorkerStats:
    """Statistics for a single worker"""
    worker_id: str
    total_contributions: int = 0
    total_evaluations: int = 0
    best_fitness: float = 0.0
    avg_fitness: float = 0.0
    pareto_count: int = 0  # Number of individuals in Pareto front
    improvement_count: int = 0  # Number of improvements to global best
    total_work_time: float = 0.0
    evaluations_per_second: float = 0.0
    success_rate: float = 1.0
    failed_tasks: int = 0
    last_contribution: Optional[float] = None
    joined_at: float = field(default_factory=time.time)
    status: str = "active"  # active, idle, failed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "worker_id": self.worker_id,
            "total_contributions": self.total_contributions,
            "total_evaluations": self.total_evaluations,
            "best_fitness": self.best_fitness,
            "avg_fitness": self.avg_fitness,
            "pareto_count": self.pareto_count,
            "improvement_count": self.improvement_count,
            "total_work_time": self.total_work_time,
            "evaluations_per_second": self.evaluations_per_second,
            "success_rate": self.success_rate,
            "failed_tasks": self.failed_tasks,
            "last_contribution": self.last_contribution,
            "joined_at": self.joined_at,
            "status": self.status
        }


class ContributionTracker:
    """
    Tracks worker contributions and computes credit assignment

    Features:
    - Track individual contributions
    - Compute worker statistics
    - Rank workers by contribution
    - Detect and reward improvements
    - Fair credit assignment
    """

    def __init__(self, objectives: List[str] = None):
        """
        Initialize contribution tracker

        Args:
            objectives: List of optimization objectives
        """
        self.objectives = objectives or ["accuracy", "speed", "cost"]
        self.contributions: List[ContributionRecord] = []
        self.worker_stats: Dict[str, WorkerStats] = {}
        self.global_best_history: List[Dict[str, Any]] = []
        self.pareto_front_history: List[Dict[str, Any]] = []

    def register_worker(self, worker_id: str) -> None:
        """Register a new worker"""
        if worker_id not in self.worker_stats:
            self.worker_stats[worker_id] = WorkerStats(worker_id=worker_id)

    def record_contribution(
        self,
        worker_id: str,
        individual: Any,
        generation: int,
        contribution_type: str = "individual"
    ) -> ContributionRecord:
        """
        Record a contribution from a worker

        Args:
            worker_id: Worker identifier
            individual: Contributed individual
            generation: Current generation
            contribution_type: Type of contribution

        Returns:
            Created contribution record
        """
        # Ensure worker is registered
        self.register_worker(worker_id)

        # Create record
        record = ContributionRecord(
            worker_id=worker_id,
            individual_id=individual.id,
            generation=generation,
            fitness_scores=individual.fitness_scores.copy(),
            contribution_type=contribution_type
        )

        self.contributions.append(record)

        # Update worker stats
        stats = self.worker_stats[worker_id]
        stats.total_contributions += 1
        stats.last_contribution = time.time()

        # Update fitness stats
        primary_fitness = individual.fitness_scores.get(self.objectives[0], 0.0)
        if primary_fitness > stats.best_fitness:
            stats.best_fitness = primary_fitness

        # Update average fitness
        total_fitness = sum(
            rec.fitness_scores.get(self.objectives[0], 0.0)
            for rec in self.contributions
            if rec.worker_id == worker_id
        )
        stats.avg_fitness = total_fitness / stats.total_contributions

        return record

    def record_evaluation(
        self,
        worker_id: str,
        evaluation_time: float,
        success: bool = True
    ) -> None:
        """
        Record an evaluation task

        Args:
            worker_id: Worker identifier
            evaluation_time: Time taken for evaluation
            success: Whether evaluation succeeded
        """
        self.register_worker(worker_id)

        stats = self.worker_stats[worker_id]
        stats.total_evaluations += 1
        stats.total_work_time += evaluation_time

        if stats.total_work_time > 0:
            stats.evaluations_per_second = stats.total_evaluations / stats.total_work_time

        if not success:
            stats.failed_tasks += 1

        stats.success_rate = (
            (stats.total_evaluations - stats.failed_tasks) / stats.total_evaluations
        )

    def check_improvement(
        self,
        individual: Any,
        worker_id: str,
        generation: int
    ) -> bool:
        """
        Check if individual improves global best

        Args:
            individual: Individual to check
            worker_id: Contributing worker
            generation: Current generation

        Returns:
            True if this is an improvement
        """
        primary_objective = self.objectives[0]
        current_fitness = individual.fitness_scores.get(primary_objective, 0.0)

        # Get previous best
        if self.global_best_history:
            prev_best = self.global_best_history[-1]["fitness"]
        else:
            prev_best = 0.0

        # Check improvement
        is_improvement = current_fitness > prev_best

        if is_improvement:
            # Record improvement
            self.global_best_history.append({
                "generation": generation,
                "fitness": current_fitness,
                "individual_id": individual.id,
                "worker_id": worker_id,
                "timestamp": time.time()
            })

            # Credit worker
            if worker_id in self.worker_stats:
                self.worker_stats[worker_id].improvement_count += 1

        return is_improvement

    def update_pareto_contributions(
        self,
        pareto_front: List[Any],
        generation: int
    ) -> None:
        """
        Update contributions for Pareto front members

        Args:
            pareto_front: Current Pareto front
            generation: Current generation
        """
        # Record Pareto front
        self.pareto_front_history.append({
            "generation": generation,
            "size": len(pareto_front),
            "individuals": [ind.id for ind in pareto_front],
            "timestamp": time.time()
        })

        # Find which workers contributed to Pareto front
        pareto_ids = {ind.id for ind in pareto_front}

        # Count contributions per worker
        worker_pareto_counts = {}
        for record in self.contributions:
            if record.individual_id in pareto_ids:
                worker_id = record.worker_id
                worker_pareto_counts[worker_id] = worker_pareto_counts.get(worker_id, 0) + 1

        # Update worker stats
        for worker_id, count in worker_pareto_counts.items():
            if worker_id in self.worker_stats:
                self.worker_stats[worker_id].pareto_count = count

    def get_worker_rankings(
        self,
        metric: str = "total_contributions"
    ) -> List[tuple[str, float]]:
        """
        Get workers ranked by a metric

        Args:
            metric: Metric to rank by (total_contributions, best_fitness, etc.)

        Returns:
            List of (worker_id, score) tuples, sorted descending
        """
        rankings = []

        for worker_id, stats in self.worker_stats.items():
            score = getattr(stats, metric, 0.0)
            rankings.append((worker_id, score))

        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings

    def compute_contribution_scores(
        self,
        weights: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        Compute overall contribution scores for workers

        Args:
            weights: Weights for different contribution factors

        Returns:
            Dictionary of worker_id -> score
        """
        if weights is None:
            weights = {
                "improvements": 0.4,
                "pareto_count": 0.3,
                "avg_fitness": 0.2,
                "evaluations": 0.1
            }

        scores = {}

        # Normalize factors
        all_improvements = [s.improvement_count for s in self.worker_stats.values()]
        all_pareto = [s.pareto_count for s in self.worker_stats.values()]
        all_fitness = [s.avg_fitness for s in self.worker_stats.values()]
        all_evals = [s.total_evaluations for s in self.worker_stats.values()]

        max_improvements = max(all_improvements) if all_improvements else 1
        max_pareto = max(all_pareto) if all_pareto else 1
        max_fitness = max(all_fitness) if all_fitness else 1
        max_evals = max(all_evals) if all_evals else 1

        # Compute weighted scores
        for worker_id, stats in self.worker_stats.items():
            score = 0.0
            score += weights.get("improvements", 0.0) * (stats.improvement_count / max_improvements)
            score += weights.get("pareto_count", 0.0) * (stats.pareto_count / max_pareto)
            score += weights.get("avg_fitness", 0.0) * (stats.avg_fitness / max_fitness)
            score += weights.get("evaluations", 0.0) * (stats.total_evaluations / max_evals)

            scores[worker_id] = score

        return scores

    def get_worker_statistics(self, worker_id: str) -> Optional[WorkerStats]:
        """Get statistics for a specific worker"""
        return self.worker_stats.get(worker_id)

    def get_all_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        total_contributions = sum(
            stats.total_contributions for stats in self.worker_stats.values()
        )
        total_evaluations = sum(
            stats.total_evaluations for stats in self.worker_stats.values()
        )
        active_workers = sum(
            1 for stats in self.worker_stats.values()
            if stats.status == "active"
        )

        return {
            "total_workers": len(self.worker_stats),
            "active_workers": active_workers,
            "total_contributions": total_contributions,
            "total_evaluations": total_evaluations,
            "total_improvements": len(self.global_best_history),
            "current_best_fitness": (
                self.global_best_history[-1]["fitness"]
                if self.global_best_history else 0.0
            ),
            "worker_stats": {
                wid: stats.to_dict()
                for wid, stats in self.worker_stats.items()
            }
        }

    def mark_worker_failed(self, worker_id: str) -> None:
        """Mark a worker as failed"""
        if worker_id in self.worker_stats:
            self.worker_stats[worker_id].status = "failed"

    def mark_worker_idle(self, worker_id: str) -> None:
        """Mark a worker as idle"""
        if worker_id in self.worker_stats:
            self.worker_stats[worker_id].status = "idle"

    def mark_worker_active(self, worker_id: str) -> None:
        """Mark a worker as active"""
        if worker_id in self.worker_stats:
            self.worker_stats[worker_id].status = "active"

    def get_contribution_timeline(
        self,
        worker_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get timeline of contributions

        Args:
            worker_id: Optional filter by worker

        Returns:
            List of contribution records
        """
        records = self.contributions

        if worker_id:
            records = [r for r in records if r.worker_id == worker_id]

        return [r.to_dict() for r in records]

    def export_statistics(self, filepath: str) -> None:
        """
        Export statistics to JSON file

        Args:
            filepath: Path to save JSON file
        """
        stats = self.get_all_statistics()
        stats["global_best_history"] = self.global_best_history
        stats["pareto_front_history"] = self.pareto_front_history

        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)

    def generate_report(self) -> str:
        """
        Generate human-readable contribution report

        Returns:
            Formatted report string
        """
        stats = self.get_all_statistics()
        rankings = self.get_worker_rankings("best_fitness")
        contribution_scores = self.compute_contribution_scores()

        report = []
        report.append("=" * 60)
        report.append("COLLABORATIVE EVOLUTION CONTRIBUTION REPORT")
        report.append("=" * 60)
        report.append("")

        # Overall statistics
        report.append("OVERALL STATISTICS")
        report.append("-" * 60)
        report.append(f"Total Workers: {stats['total_workers']}")
        report.append(f"Active Workers: {stats['active_workers']}")
        report.append(f"Total Contributions: {stats['total_contributions']}")
        report.append(f"Total Evaluations: {stats['total_evaluations']}")
        report.append(f"Global Improvements: {stats['total_improvements']}")
        report.append(f"Current Best Fitness: {stats['current_best_fitness']:.4f}")
        report.append("")

        # Worker rankings
        report.append("WORKER RANKINGS (by Best Fitness)")
        report.append("-" * 60)
        for rank, (worker_id, fitness) in enumerate(rankings[:10], 1):
            contrib_score = contribution_scores.get(worker_id, 0.0)
            worker_stats = self.worker_stats[worker_id]
            report.append(
                f"{rank}. {worker_id}: "
                f"Fitness={fitness:.4f}, "
                f"Contributions={worker_stats.total_contributions}, "
                f"Improvements={worker_stats.improvement_count}, "
                f"Score={contrib_score:.3f}"
            )
        report.append("")

        # Top contributors
        report.append("TOP CONTRIBUTORS (by Contribution Score)")
        report.append("-" * 60)
        sorted_contributors = sorted(
            contribution_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for rank, (worker_id, score) in enumerate(sorted_contributors[:10], 1):
            worker_stats = self.worker_stats[worker_id]
            report.append(
                f"{rank}. {worker_id}: "
                f"Score={score:.3f}, "
                f"Improvements={worker_stats.improvement_count}, "
                f"Pareto={worker_stats.pareto_count}, "
                f"AvgFitness={worker_stats.avg_fitness:.4f}"
            )
        report.append("")

        report.append("=" * 60)

        return "\n".join(report)
