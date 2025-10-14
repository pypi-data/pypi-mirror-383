"""
Worker Node for Collaborative Evolution

Implements distributed worker that executes local evolution
and coordinates with central coordinator.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import time
import threading
from queue import Queue
import logging

from ..core.evolution import EvolutionEngine, EvolutionConfig, Individual
from .protocol import (
    CommunicationProtocol,
    Message,
    MessageType,
    serialize_individual,
    deserialize_individual,
    IndividualData
)

logger = logging.getLogger(__name__)


@dataclass
class WorkerConfig:
    """Configuration for worker node"""
    worker_id: str
    coordinator_url: str = "redis://localhost:6379"
    population_size: int = 10
    local_generations: int = 5
    share_interval: int = 2  # Share best every N generations
    heartbeat_interval: float = 10.0
    objectives: List[str] = field(default_factory=lambda: ["accuracy", "speed", "cost"])
    max_workers: int = 2  # For local parallelization
    enable_work_stealing: bool = True


class WorkerNode:
    """
    Distributed worker node for collaborative evolution

    Features:
    - Execute local evolution with subset of population
    - Share best individuals with coordinator
    - Receive global best individuals
    - Adaptive workload balancing
    - Failure recovery
    """

    def __init__(
        self,
        config: WorkerConfig,
        eval_func: Callable[[str], Dict[str, float]]
    ):
        """
        Initialize worker node

        Args:
            config: Worker configuration
            eval_func: Function to evaluate individual fitness
        """
        self.config = config
        self.eval_func = eval_func
        self.worker_id = config.worker_id

        # Initialize evolution engine
        self.evolution_config = EvolutionConfig(
            population_size=config.population_size,
            generations=config.local_generations,
            objectives=config.objectives,
            max_workers=config.max_workers
        )
        self.engine = EvolutionEngine(self.evolution_config)

        # Communication
        self.protocol = CommunicationProtocol(
            config.worker_id,
            config.heartbeat_interval
        )

        # State
        self.is_running = False
        self.current_generation = 0
        self.local_population: List[Individual] = []
        self.global_best: List[Individual] = []
        self.task_queue: Queue = Queue()
        self.result_queue: Queue = Queue()

        # Threading
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.work_thread: Optional[threading.Thread] = None

        # Statistics
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "individuals_shared": 0,
            "individuals_received": 0,
            "total_evaluations": 0,
            "start_time": None,
            "total_work_time": 0.0
        }

        logger.info(f"Worker {self.worker_id} initialized")

    def start(self) -> None:
        """Start worker node"""
        if self.is_running:
            logger.warning(f"Worker {self.worker_id} already running")
            return

        self.is_running = True
        self.stats["start_time"] = time.time()

        # Register with coordinator
        self._register_with_coordinator()

        # Start background threads
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

        self.work_thread = threading.Thread(target=self._work_loop, daemon=True)
        self.work_thread.start()

        logger.info(f"Worker {self.worker_id} started")

    def stop(self) -> None:
        """Stop worker node"""
        self.is_running = False

        # Wait for threads to finish
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        if self.work_thread:
            self.work_thread.join(timeout=5)

        logger.info(f"Worker {self.worker_id} stopped")

    def _register_with_coordinator(self) -> None:
        """Register this worker with coordinator"""
        message = self.protocol.create_message(
            MessageType.WORKER_REGISTER,
            {
                "worker_id": self.worker_id,
                "population_size": self.config.population_size,
                "capabilities": {
                    "max_workers": self.config.max_workers,
                    "objectives": self.config.objectives
                }
            }
        )
        self.protocol.send_message(message)
        logger.info(f"Worker {self.worker_id} registered with coordinator")

    def _heartbeat_loop(self) -> None:
        """Background thread for sending heartbeats"""
        while self.is_running:
            try:
                self.protocol.send_heartbeat()
                time.sleep(self.config.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

    def _work_loop(self) -> None:
        """Background thread for processing work"""
        while self.is_running:
            try:
                # Check for new tasks
                if not self.task_queue.empty():
                    task = self.task_queue.get()
                    self._process_task(task)

                # Check for messages from coordinator
                self._check_messages()

                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Work loop error: {e}")

    def _process_task(self, task: Dict[str, Any]) -> None:
        """Process a task from queue"""
        start_time = time.time()
        task_type = task.get("type")

        try:
            if task_type == "evolve":
                result = self._execute_local_evolution(task)
            elif task_type == "evaluate":
                result = self._evaluate_individuals(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            # Record success
            self.stats["tasks_completed"] += 1
            elapsed = time.time() - start_time
            self.stats["total_work_time"] += elapsed

            # Send result
            self.result_queue.put({
                "task_id": task.get("id"),
                "result": result,
                "success": True,
                "elapsed_time": elapsed
            })

        except Exception as e:
            logger.error(f"Task processing error: {e}")
            self.stats["tasks_failed"] += 1

            self.result_queue.put({
                "task_id": task.get("id"),
                "error": str(e),
                "success": False
            })

    def _execute_local_evolution(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute local evolution

        Args:
            task: Task specification with seed prompts

        Returns:
            Results with best individuals
        """
        seed_prompts = task.get("seed_prompts", [])
        generations = task.get("generations", self.config.local_generations)

        # Initialize or update population
        if not self.local_population:
            self.local_population = self.engine.initialize_population(seed_prompts)

        # Integrate global best if available
        if self.global_best:
            # Replace some individuals with global best
            n_replace = min(len(self.global_best), len(self.local_population) // 4)
            self.local_population[-n_replace:] = self.global_best[:n_replace]

        # Run local evolution
        self.engine.population = self.local_population
        for gen in range(generations):
            self.current_generation += 1

            # Evaluate population
            self.engine.population = self.engine.evaluate_population(
                self.engine.population,
                self.eval_func
            )
            self.stats["total_evaluations"] += len(self.engine.population)

            # Selection and reproduction
            n_parents = self.config.population_size // 2
            parents = self.engine.select_parents(self.engine.population, n_parents)
            offspring = self.engine.generate_offspring(parents, self.config.population_size)

            # Evaluate offspring
            offspring = self.engine.evaluate_population(offspring, self.eval_func)
            self.stats["total_evaluations"] += len(offspring)

            # Survivor selection
            self.engine.population = self.engine.survivor_selection(
                self.engine.population,
                offspring
            )

            # Share best individuals periodically
            if gen % self.config.share_interval == 0:
                self._share_best_individuals()

        # Update local population
        self.local_population = self.engine.population

        # Get best individuals
        best_individuals = sorted(
            self.local_population,
            key=lambda x: x.fitness_scores.get("accuracy", 0.0),
            reverse=True
        )[:5]

        return {
            "best_individuals": [serialize_individual(ind) for ind in best_individuals],
            "generation": self.current_generation,
            "population_size": len(self.local_population),
            "best_fitness": best_individuals[0].fitness_scores if best_individuals else {}
        }

    def _evaluate_individuals(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a batch of individuals

        Args:
            task: Task with individuals to evaluate

        Returns:
            Evaluation results
        """
        individuals_data = task.get("individuals", [])

        # Deserialize individuals
        individuals = []
        for ind_data_dict in individuals_data:
            ind_data = IndividualData.from_dict(ind_data_dict)
            individual = Individual(
                prompt=ind_data.prompt,
                fitness_scores={},
                generation=ind_data.generation,
                parent_ids=ind_data.parent_ids,
                id=ind_data.id
            )
            individuals.append(individual)

        # Evaluate
        evaluated = self.engine.evaluate_population(individuals, self.eval_func)
        self.stats["total_evaluations"] += len(evaluated)

        # Serialize results
        results = [
            {
                "id": ind.id,
                "fitness_scores": ind.fitness_scores
            }
            for ind in evaluated
        ]

        return {
            "evaluations": results,
            "count": len(results)
        }

    def _share_best_individuals(self) -> None:
        """Share best individuals with coordinator"""
        if not self.local_population:
            return

        # Get top individuals
        n_share = max(1, len(self.local_population) // 10)
        best = sorted(
            self.local_population,
            key=lambda x: x.fitness_scores.get("accuracy", 0.0),
            reverse=True
        )[:n_share]

        # Send to coordinator
        message = self.protocol.create_share_population_message(
            best,
            self.current_generation
        )
        self.protocol.send_message(message)
        self.stats["individuals_shared"] += len(best)

        logger.info(
            f"Worker {self.worker_id} shared {len(best)} individuals "
            f"(gen {self.current_generation})"
        )

    def _check_messages(self) -> None:
        """Check for messages from coordinator"""
        messages = self.protocol.get_pending_messages()

        for message in messages:
            try:
                self._handle_message(message)
            except Exception as e:
                logger.error(f"Message handling error: {e}")

        # Clear processed messages
        self.protocol.clear_message_queue()

    def _handle_message(self, message: Message) -> None:
        """Handle a message from coordinator"""
        if message.type == MessageType.BROADCAST_BEST:
            self._receive_global_best(message)

        elif message.type == MessageType.TASK_ASSIGN:
            task_data = message.data.get("task_data", {})
            self.task_queue.put(task_data)

        elif message.type == MessageType.STOP_EVOLUTION:
            self.stop()

        elif message.type == MessageType.SYNC_REQUEST:
            self._handle_sync_request(message)

    def _receive_global_best(self, message: Message) -> None:
        """Receive and integrate global best individuals"""
        individuals_data = self.protocol.extract_individuals_from_message(message)

        # Convert to Individual objects
        self.global_best = []
        for ind_data in individuals_data:
            individual = Individual(
                prompt=ind_data.prompt,
                fitness_scores=ind_data.fitness_scores.copy(),
                generation=ind_data.generation,
                parent_ids=ind_data.parent_ids,
                id=ind_data.id
            )
            self.global_best.append(individual)

        self.stats["individuals_received"] += len(individuals_data)

        logger.info(
            f"Worker {self.worker_id} received {len(individuals_data)} "
            f"global best individuals"
        )

    def _handle_sync_request(self, message: Message) -> None:
        """Handle synchronization request from coordinator"""
        # Send current state
        response = self.protocol.create_message(
            MessageType.SYNC_RESPONSE,
            {
                "generation": self.current_generation,
                "population_size": len(self.local_population),
                "stats": self.stats.copy(),
                "status": "active" if self.is_running else "stopped"
            }
        )
        self.protocol.send_message(response)

    def assign_task(self, task: Dict[str, Any]) -> None:
        """
        Assign a task to this worker

        Args:
            task: Task specification
        """
        self.task_queue.put(task)

    def get_results(self) -> List[Dict[str, Any]]:
        """Get completed results"""
        results = []
        while not self.result_queue.empty():
            results.append(self.result_queue.get())
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get worker statistics"""
        stats = self.stats.copy()

        if stats["start_time"]:
            stats["uptime"] = time.time() - stats["start_time"]

        if stats["total_work_time"] > 0:
            stats["evaluations_per_second"] = (
                stats["total_evaluations"] / stats["total_work_time"]
            )
        else:
            stats["evaluations_per_second"] = 0.0

        stats["success_rate"] = (
            stats["tasks_completed"] /
            max(1, stats["tasks_completed"] + stats["tasks_failed"])
        )

        stats["current_generation"] = self.current_generation
        stats["population_size"] = len(self.local_population)

        return stats

    def get_best_individuals(self, n: int = 5) -> List[Individual]:
        """
        Get best individuals from local population

        Args:
            n: Number of individuals to return

        Returns:
            List of best individuals
        """
        if not self.local_population:
            return []

        sorted_pop = sorted(
            self.local_population,
            key=lambda x: x.fitness_scores.get("accuracy", 0.0),
            reverse=True
        )

        return sorted_pop[:n]

    def reset(self) -> None:
        """Reset worker state"""
        self.current_generation = 0
        self.local_population = []
        self.global_best = []

        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "individuals_shared": 0,
            "individuals_received": 0,
            "total_evaluations": 0,
            "start_time": time.time() if self.is_running else None,
            "total_work_time": 0.0
        }

        logger.info(f"Worker {self.worker_id} reset")
