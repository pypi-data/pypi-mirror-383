"""
Evolution Coordinator for Collaborative Evolution

Central coordinator managing distributed evolution across multiple workers.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import time
import threading
from queue import Queue
import logging

from ..core.evolution import Individual, EvolutionConfig
from ..core.pareto import ParetoOptimizer
from .protocol import (
    CommunicationProtocol,
    Message,
    MessageType,
    IndividualData,
    deserialize_individual
)
from .merge import MergeStrategy, EliteMerger, AdaptiveMerger
from .tracking import ContributionTracker
from .worker import WorkerNode, WorkerConfig

logger = logging.getLogger(__name__)


@dataclass
class CoordinatorConfig:
    """Configuration for evolution coordinator"""
    coordinator_id: str = "coordinator"
    population_size: int = 50
    n_workers: int = 3
    generations: int = 20
    sync_interval: int = 5  # Sync workers every N generations
    objectives: List[str] = field(default_factory=lambda: ["accuracy", "speed", "cost"])
    merge_strategy: str = "adaptive"  # elite, diversity, pareto, adaptive
    enable_tracking: bool = True
    broadcast_best_count: int = 5
    worker_timeout: float = 60.0  # Seconds before considering worker failed


class EvolutionCoordinator:
    """
    Central coordinator for distributed evolution

    Features:
    - Manage worker pool
    - Distribute evaluation tasks
    - Merge populations from workers
    - Track contributions
    - Maintain global Pareto frontier
    - Handle worker failures
    """

    def __init__(
        self,
        config: CoordinatorConfig,
        eval_func: Callable[[str], Dict[str, float]]
    ):
        """
        Initialize coordinator

        Args:
            config: Coordinator configuration
            eval_func: Function to evaluate individual fitness
        """
        self.config = config
        self.eval_func = eval_func

        # Communication
        self.protocol = CommunicationProtocol(config.coordinator_id)

        # Workers
        self.workers: Dict[str, WorkerNode] = {}
        self.worker_status: Dict[str, str] = {}  # worker_id -> status

        # Evolution state
        self.generation = 0
        self.global_population: List[Individual] = []
        self.pareto_front: List[Individual] = []
        self.global_best: Optional[Individual] = None

        # Merge strategy
        self.merge_strategy = self._create_merge_strategy()

        # Contribution tracking
        self.tracker = ContributionTracker(config.objectives) if config.enable_tracking else None

        # Pareto optimizer
        self.pareto_optimizer = ParetoOptimizer(config.objectives)

        # History
        self.history: List[Dict[str, Any]] = []

        # Control
        self.is_running = False
        self.message_queue: Queue = Queue()

        logger.info(f"Coordinator {config.coordinator_id} initialized")

    def _create_merge_strategy(self) -> MergeStrategy:
        """Create merge strategy based on config"""
        strategy_name = self.config.merge_strategy.lower()

        if strategy_name == "elite":
            return EliteMerger(self.config.population_size)
        elif strategy_name == "adaptive":
            return AdaptiveMerger(
                self.config.population_size,
                self.config.generations,
                self.config.objectives
            )
        elif strategy_name == "diversity":
            from .merge import DiversityMerger
            return DiversityMerger(self.config.population_size)
        elif strategy_name == "pareto":
            from .merge import ParetoMerger
            return ParetoMerger(self.config.population_size, self.config.objectives)
        else:
            logger.warning(f"Unknown strategy {strategy_name}, using elite")
            return EliteMerger(self.config.population_size)

    def register_worker(
        self,
        worker_id: str,
        worker: Optional[WorkerNode] = None
    ) -> None:
        """
        Register a worker with coordinator

        Args:
            worker_id: Unique worker identifier
            worker: Optional WorkerNode instance
        """
        if worker:
            self.workers[worker_id] = worker
        self.worker_status[worker_id] = "registered"

        if self.tracker:
            self.tracker.register_worker(worker_id)

        logger.info(f"Worker {worker_id} registered")

    def create_workers(
        self,
        seed_prompts: List[str]
    ) -> None:
        """
        Create worker nodes

        Args:
            seed_prompts: Initial prompts for workers
        """
        for i in range(self.config.n_workers):
            worker_id = f"worker_{i}"

            worker_config = WorkerConfig(
                worker_id=worker_id,
                population_size=self.config.population_size // self.config.n_workers,
                local_generations=self.config.sync_interval,
                objectives=self.config.objectives
            )

            worker = WorkerNode(worker_config, self.eval_func)
            self.register_worker(worker_id, worker)

            # Initialize worker with seed prompts
            worker.engine.population = worker.engine.initialize_population(seed_prompts)
            worker.local_population = worker.engine.population

        logger.info(f"Created {self.config.n_workers} workers")

    def start_evolution(
        self,
        seed_prompts: List[str]
    ) -> Individual:
        """
        Start distributed evolution

        Args:
            seed_prompts: Initial prompts

        Returns:
            Best individual found
        """
        self.is_running = True

        # Create workers if not already created
        if not self.workers:
            self.create_workers(seed_prompts)

        # Start all workers
        for worker in self.workers.values():
            worker.start()

        # Main evolution loop
        for gen in range(self.config.generations):
            self.generation = gen

            logger.info(f"=== Generation {gen} ===")

            # Assign work to workers
            self._assign_work_to_workers()

            # Wait for workers to complete
            self._wait_for_workers()

            # Collect populations from workers
            worker_populations = self._collect_populations()

            # Merge populations
            self.global_population = self.merge_strategy.merge(
                worker_populations,
                gen
            )

            # Update Pareto front
            self.pareto_front = self.pareto_optimizer.compute_pareto_front(
                self.global_population
            )

            # Update global best
            self._update_global_best()

            # Track contributions
            if self.tracker:
                self._track_contributions(worker_populations)

            # Broadcast best individuals to workers
            if gen % self.config.sync_interval == 0:
                self._broadcast_best_individuals()

            # Check worker health
            self._check_worker_health()

            # Log progress
            self._log_progress()

            # Save history
            self._save_generation_history()

        # Stop workers
        self.stop_evolution()

        return self.global_best

    def _assign_work_to_workers(self) -> None:
        """Assign evolution tasks to workers"""
        for worker_id, worker in self.workers.items():
            if self.worker_status.get(worker_id) == "active" or \
               self.worker_status.get(worker_id) == "registered":

                # Get best prompts to seed worker
                seed_prompts = []
                if self.global_population:
                    best = sorted(
                        self.global_population,
                        key=lambda x: x.fitness_scores.get("accuracy", 0.0),
                        reverse=True
                    )[:5]
                    seed_prompts = [ind.prompt for ind in best]

                # Create task
                task = {
                    "id": f"gen_{self.generation}_worker_{worker_id}",
                    "type": "evolve",
                    "seed_prompts": seed_prompts,
                    "generations": self.config.sync_interval
                }

                worker.assign_task(task)
                self.worker_status[worker_id] = "active"

    def _wait_for_workers(self, timeout: float = None) -> None:
        """Wait for workers to complete their tasks"""
        timeout = timeout or self.config.worker_timeout
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if all workers completed
            all_completed = True

            for worker_id, worker in self.workers.items():
                results = worker.get_results()
                if not results and self.worker_status.get(worker_id) == "active":
                    all_completed = False

            if all_completed:
                break

            time.sleep(0.5)

        # Check for timeouts
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            logger.warning(f"Worker timeout after {elapsed:.1f}s")

    def _collect_populations(self) -> List[List[Individual]]:
        """Collect populations from all workers"""
        populations = []

        for worker_id, worker in self.workers.items():
            # Get results
            results = worker.get_results()

            if results:
                # Process latest result
                result = results[-1]
                if result.get("success"):
                    # Get worker's population
                    worker_pop = worker.get_best_individuals(
                        n=self.config.population_size // self.config.n_workers
                    )
                    if worker_pop:
                        populations.append(worker_pop)

                    logger.info(
                        f"Collected {len(worker_pop)} individuals from {worker_id}"
                    )
            else:
                # Fallback to worker's current population
                worker_pop = worker.get_best_individuals(
                    n=self.config.population_size // self.config.n_workers
                )
                if worker_pop:
                    populations.append(worker_pop)

        return populations

    def _update_global_best(self) -> None:
        """Update global best individual"""
        if not self.global_population:
            return

        best = max(
            self.global_population,
            key=lambda x: x.fitness_scores.get("accuracy", 0.0)
        )

        if self.global_best is None or \
           best.fitness_scores.get("accuracy", 0.0) > \
           self.global_best.fitness_scores.get("accuracy", 0.0):
            self.global_best = best
            logger.info(
                f"New global best: {self.global_best.fitness_scores.get('accuracy', 0.0):.4f}"
            )

    def _track_contributions(self, worker_populations: List[List[Individual]]) -> None:
        """Track worker contributions"""
        if not self.tracker:
            return

        # Track contributions from each worker
        for i, population in enumerate(worker_populations):
            worker_id = f"worker_{i}" if i < len(self.workers) else f"worker_{i}"

            for individual in population:
                self.tracker.record_contribution(
                    worker_id,
                    individual,
                    self.generation
                )

                # Check for improvements
                self.tracker.check_improvement(
                    individual,
                    worker_id,
                    self.generation
                )

        # Update Pareto contributions
        self.tracker.update_pareto_contributions(
            self.pareto_front,
            self.generation
        )

    def _broadcast_best_individuals(self) -> None:
        """Broadcast best individuals to all workers"""
        if not self.global_population:
            return

        # Get top individuals
        best = sorted(
            self.global_population,
            key=lambda x: x.fitness_scores.get("accuracy", 0.0),
            reverse=True
        )[:self.config.broadcast_best_count]

        # Send to workers
        for worker in self.workers.values():
            message = self.protocol.create_message(
                MessageType.BROADCAST_BEST,
                {
                    "best_individuals": [
                        worker.protocol.create_share_individual_message(ind).data["individual"]
                        for ind in best
                    ],
                    "generation": self.generation
                }
            )
            worker._handle_message(message)

        logger.info(f"Broadcasted {len(best)} best individuals to workers")

    def _check_worker_health(self) -> None:
        """Check worker health and handle failures"""
        failed_workers = self.protocol.check_heartbeats(timeout=self.config.worker_timeout)

        for worker_id in failed_workers:
            if worker_id in self.worker_status:
                logger.warning(f"Worker {worker_id} failed")
                self.worker_status[worker_id] = "failed"

                if self.tracker:
                    self.tracker.mark_worker_failed(worker_id)

    def _log_progress(self) -> None:
        """Log evolution progress"""
        if not self.global_population:
            return

        best_fitness = self.global_best.fitness_scores.get("accuracy", 0.0) \
                       if self.global_best else 0.0

        avg_fitness = sum(
            ind.fitness_scores.get("accuracy", 0.0)
            for ind in self.global_population
        ) / len(self.global_population)

        logger.info(
            f"Generation {self.generation}: "
            f"Best={best_fitness:.4f}, "
            f"Avg={avg_fitness:.4f}, "
            f"Pareto Size={len(self.pareto_front)}"
        )

        # Log worker stats
        for worker_id, worker in self.workers.items():
            stats = worker.get_statistics()
            logger.info(
                f"  {worker_id}: "
                f"Gen={stats['current_generation']}, "
                f"Evals={stats['total_evaluations']}, "
                f"Success={stats['success_rate']:.2%}"
            )

    def _save_generation_history(self) -> None:
        """Save generation history"""
        if not self.global_population:
            return

        best_fitness = self.global_best.fitness_scores.get("accuracy", 0.0) \
                       if self.global_best else 0.0

        avg_fitness = sum(
            ind.fitness_scores.get("accuracy", 0.0)
            for ind in self.global_population
        ) / len(self.global_population)

        self.history.append({
            "generation": self.generation,
            "best_fitness": best_fitness,
            "avg_fitness": avg_fitness,
            "pareto_size": len(self.pareto_front),
            "population_size": len(self.global_population),
            "active_workers": sum(
                1 for status in self.worker_status.values()
                if status == "active"
            ),
            "timestamp": time.time()
        })

    def stop_evolution(self) -> None:
        """Stop evolution and all workers"""
        self.is_running = False

        for worker in self.workers.values():
            worker.stop()

        logger.info("Evolution stopped")

    def get_global_best(self) -> Optional[Individual]:
        """Get global best individual"""
        return self.global_best

    def get_pareto_front(self) -> List[Individual]:
        """Get current Pareto front"""
        return self.pareto_front

    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        stats = {
            "generation": self.generation,
            "population_size": len(self.global_population),
            "pareto_size": len(self.pareto_front),
            "n_workers": len(self.workers),
            "active_workers": sum(
                1 for status in self.worker_status.values()
                if status == "active"
            ),
            "failed_workers": sum(
                1 for status in self.worker_status.values()
                if status == "failed"
            ),
            "best_fitness": (
                self.global_best.fitness_scores.get("accuracy", 0.0)
                if self.global_best else 0.0
            ),
            "history": self.history
        }

        # Add tracker stats if available
        if self.tracker:
            stats["contributions"] = self.tracker.get_all_statistics()

        return stats

    def generate_report(self) -> str:
        """Generate comprehensive evolution report"""
        stats = self.get_statistics()

        report = []
        report.append("=" * 70)
        report.append("COLLABORATIVE EVOLUTION REPORT")
        report.append("=" * 70)
        report.append("")

        # Overall statistics
        report.append("EVOLUTION STATISTICS")
        report.append("-" * 70)
        report.append(f"Total Generations: {stats['generation']}")
        report.append(f"Global Population Size: {stats['population_size']}")
        report.append(f"Pareto Front Size: {stats['pareto_size']}")
        report.append(f"Best Fitness: {stats['best_fitness']:.4f}")
        report.append("")

        # Worker statistics
        report.append("WORKER STATISTICS")
        report.append("-" * 70)
        report.append(f"Total Workers: {stats['n_workers']}")
        report.append(f"Active Workers: {stats['active_workers']}")
        report.append(f"Failed Workers: {stats['failed_workers']}")
        report.append("")

        for worker_id, worker in self.workers.items():
            worker_stats = worker.get_statistics()
            report.append(f"{worker_id}:")
            report.append(f"  Status: {self.worker_status.get(worker_id, 'unknown')}")
            report.append(f"  Generation: {worker_stats['current_generation']}")
            report.append(f"  Evaluations: {worker_stats['total_evaluations']}")
            report.append(f"  Success Rate: {worker_stats['success_rate']:.2%}")
            report.append(f"  Evals/sec: {worker_stats['evaluations_per_second']:.2f}")
            report.append("")

        # Contribution tracking
        if self.tracker:
            report.append("")
            report.append(self.tracker.generate_report())

        report.append("=" * 70)

        return "\n".join(report)

    def export_results(self, filepath: str) -> None:
        """
        Export results to JSON file

        Args:
            filepath: Path to save results
        """
        import json

        results = {
            "config": {
                "population_size": self.config.population_size,
                "generations": self.config.generations,
                "n_workers": self.config.n_workers,
                "objectives": self.config.objectives,
                "merge_strategy": self.config.merge_strategy
            },
            "statistics": self.get_statistics(),
            "global_best": {
                "prompt": self.global_best.prompt if self.global_best else None,
                "fitness_scores": self.global_best.fitness_scores if self.global_best else {},
                "id": self.global_best.id if self.global_best else None
            },
            "pareto_front": [
                {
                    "id": ind.id,
                    "prompt": ind.prompt,
                    "fitness_scores": ind.fitness_scores
                }
                for ind in self.pareto_front
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results exported to {filepath}")
