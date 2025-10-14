"""
Celery Tasks for Collaborative Evolution

Defines distributed tasks for evaluation and evolution.
"""

from typing import Dict, List, Any
import time
import os

try:
    from celery import Celery, Task
    from celery.utils.log import get_task_logger
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Fallback for when Celery is not installed
    class Celery:
        def __init__(self, *args, **kwargs):
            pass
        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    class get_task_logger:
        def __init__(self, name):
            import logging
            self.logger = logging.getLogger(name)
        def info(self, *args, **kwargs):
            self.logger.info(*args, **kwargs)
        def error(self, *args, **kwargs):
            self.logger.error(*args, **kwargs)
        def warning(self, *args, **kwargs):
            self.logger.warning(*args, **kwargs)

from ..core.evolution import Individual, EvolutionEngine, EvolutionConfig
from .protocol import serialize_individual, deserialize_individual, IndividualData

# Initialize Celery app
app = Celery("kaggler_collaborative")
app.config_from_object("kaggler.collaborative.celeryconfig")

logger = get_task_logger(__name__)


class CallbackTask(Task):
    """Base task with callbacks for monitoring"""

    def on_success(self, retval, task_id, args, kwargs):
        """Success callback"""
        logger.info(f"Task {task_id} completed successfully")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback"""
        logger.error(f"Task {task_id} failed: {exc}")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry callback"""
        logger.warning(f"Task {task_id} retrying: {exc}")


@app.task(base=CallbackTask, bind=True, name="kaggler.collaborative.tasks.evaluate_individual")
def evaluate_individual(
    self,
    individual_data: Dict[str, Any],
    eval_func_name: str = "default"
) -> Dict[str, Any]:
    """
    Evaluate a single individual

    Args:
        individual_data: Serialized individual data
        eval_func_name: Name of evaluation function to use

    Returns:
        Dictionary with evaluation results
    """
    start_time = time.time()

    try:
        # Deserialize individual
        ind_data = IndividualData.from_dict(individual_data)

        # Get evaluation function
        eval_func = _get_eval_function(eval_func_name)

        # Evaluate
        fitness_scores = eval_func(ind_data.prompt)

        # Update individual
        ind_data.fitness_scores = fitness_scores

        elapsed = time.time() - start_time

        logger.info(
            f"Evaluated individual {ind_data.id}: "
            f"fitness={fitness_scores.get('accuracy', 0.0):.3f}, "
            f"time={elapsed:.2f}s"
        )

        return {
            "individual": ind_data.to_dict(),
            "fitness_scores": fitness_scores,
            "elapsed_time": elapsed,
            "worker_id": self.request.hostname,
            "task_id": self.request.id
        }

    except Exception as e:
        logger.error(f"Error evaluating individual: {e}")
        raise


@app.task(base=CallbackTask, bind=True, name="kaggler.collaborative.tasks.evaluate_population")
def evaluate_population(
    self,
    population_data: List[Dict[str, Any]],
    eval_func_name: str = "default"
) -> Dict[str, Any]:
    """
    Evaluate a population of individuals

    Args:
        population_data: List of serialized individuals
        eval_func_name: Name of evaluation function

    Returns:
        Dictionary with evaluation results
    """
    start_time = time.time()

    try:
        # Get evaluation function
        eval_func = _get_eval_function(eval_func_name)

        # Evaluate each individual
        results = []
        for ind_dict in population_data:
            ind_data = IndividualData.from_dict(ind_dict)
            fitness_scores = eval_func(ind_data.prompt)
            ind_data.fitness_scores = fitness_scores
            results.append(ind_data.to_dict())

        elapsed = time.time() - start_time

        logger.info(
            f"Evaluated population of {len(results)} individuals "
            f"in {elapsed:.2f}s ({elapsed/len(results):.3f}s per individual)"
        )

        return {
            "population": results,
            "count": len(results),
            "elapsed_time": elapsed,
            "worker_id": self.request.hostname,
            "task_id": self.request.id
        }

    except Exception as e:
        logger.error(f"Error evaluating population: {e}")
        raise


@app.task(base=CallbackTask, bind=True, name="kaggler.collaborative.tasks.run_local_evolution")
def run_local_evolution(
    self,
    seed_prompts: List[str],
    generations: int = 5,
    population_size: int = 10,
    eval_func_name: str = "default",
    objectives: List[str] = None
) -> Dict[str, Any]:
    """
    Run local evolution on a worker

    Args:
        seed_prompts: Initial prompts
        generations: Number of generations
        population_size: Population size
        eval_func_name: Evaluation function name
        objectives: Optimization objectives

    Returns:
        Dictionary with evolution results
    """
    start_time = time.time()

    try:
        objectives = objectives or ["accuracy", "speed", "cost"]

        # Get evaluation function
        eval_func = _get_eval_function(eval_func_name)

        # Configure evolution
        config = EvolutionConfig(
            population_size=population_size,
            generations=generations,
            objectives=objectives,
            max_workers=1  # Single-threaded within task
        )

        # Run evolution
        engine = EvolutionEngine(config)
        best = engine.evolve(seed_prompts, eval_func, generations)

        # Get best individuals
        best_individuals = sorted(
            engine.population,
            key=lambda x: x.fitness_scores.get("accuracy", 0.0),
            reverse=True
        )[:5]

        elapsed = time.time() - start_time

        logger.info(
            f"Local evolution completed: "
            f"{generations} generations, "
            f"best_fitness={best.fitness_scores.get('accuracy', 0.0):.3f}, "
            f"time={elapsed:.2f}s"
        )

        return {
            "best_individual": {
                "id": best.id,
                "prompt": best.prompt,
                "fitness_scores": best.fitness_scores,
                "generation": best.generation
            },
            "best_individuals": [
                {
                    "id": ind.id,
                    "prompt": ind.prompt,
                    "fitness_scores": ind.fitness_scores,
                    "generation": ind.generation
                }
                for ind in best_individuals
            ],
            "generations_completed": generations,
            "population_size": len(engine.population),
            "elapsed_time": elapsed,
            "worker_id": self.request.hostname,
            "task_id": self.request.id
        }

    except Exception as e:
        logger.error(f"Error in local evolution: {e}")
        raise


@app.task(base=CallbackTask, bind=True, name="kaggler.collaborative.tasks.merge_populations")
def merge_populations(
    self,
    populations_data: List[List[Dict[str, Any]]],
    target_size: int,
    merge_strategy: str = "elite",
    objectives: List[str] = None
) -> Dict[str, Any]:
    """
    Merge multiple populations

    Args:
        populations_data: List of populations (each is list of individuals)
        target_size: Target merged population size
        merge_strategy: Merge strategy to use
        objectives: Optimization objectives

    Returns:
        Dictionary with merged population
    """
    start_time = time.time()

    try:
        from .merge import EliteMerger, DiversityMerger, ParetoMerger, AdaptiveMerger

        objectives = objectives or ["accuracy", "speed", "cost"]

        # Convert to Individual objects
        populations = []
        for pop_data in populations_data:
            population = []
            for ind_dict in pop_data:
                ind_data = IndividualData.from_dict(ind_dict)
                individual = Individual(
                    prompt=ind_data.prompt,
                    fitness_scores=ind_data.fitness_scores,
                    generation=ind_data.generation,
                    parent_ids=ind_data.parent_ids,
                    id=ind_data.id
                )
                population.append(individual)
            populations.append(population)

        # Select merge strategy
        if merge_strategy == "elite":
            merger = EliteMerger(target_size)
        elif merge_strategy == "diversity":
            merger = DiversityMerger(target_size)
        elif merge_strategy == "pareto":
            merger = ParetoMerger(target_size, objectives)
        else:
            merger = EliteMerger(target_size)

        # Merge
        merged = merger.merge(populations, generation=0)

        elapsed = time.time() - start_time

        logger.info(
            f"Merged {len(populations)} populations "
            f"({sum(len(p) for p in populations)} individuals) "
            f"into {len(merged)} individuals "
            f"in {elapsed:.2f}s"
        )

        return {
            "merged_population": [
                {
                    "id": ind.id,
                    "prompt": ind.prompt,
                    "fitness_scores": ind.fitness_scores,
                    "generation": ind.generation
                }
                for ind in merged
            ],
            "input_populations": len(populations),
            "input_size": sum(len(p) for p in populations),
            "output_size": len(merged),
            "elapsed_time": elapsed,
            "worker_id": self.request.hostname,
            "task_id": self.request.id
        }

    except Exception as e:
        logger.error(f"Error merging populations: {e}")
        raise


def _get_eval_function(func_name: str):
    """
    Get evaluation function by name

    Args:
        func_name: Function name

    Returns:
        Evaluation function
    """
    # Default simple evaluation function
    def default_eval(prompt: str) -> Dict[str, float]:
        """Default evaluation function"""
        # Simple heuristic based on prompt length and keywords
        score = min(len(prompt) / 200.0, 1.0)

        # Bonus for good keywords
        good_keywords = ["precise", "accurate", "detailed", "specific", "carefully"]
        for keyword in good_keywords:
            if keyword.lower() in prompt.lower():
                score += 0.1

        score = min(score, 1.0)

        return {
            "accuracy": score,
            "speed": 1.0,  # Mock speed
            "cost": 0.5    # Mock cost
        }

    # In production, could load custom evaluation functions
    # For now, return default
    return default_eval


# Task monitoring utilities

@app.task(name="kaggler.collaborative.tasks.health_check")
def health_check() -> Dict[str, Any]:
    """Health check task"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "celery_available": CELERY_AVAILABLE
    }


@app.task(name="kaggler.collaborative.tasks.get_worker_stats")
def get_worker_stats() -> Dict[str, Any]:
    """Get worker statistics"""
    from celery import current_app

    stats = current_app.control.inspect().stats()
    active = current_app.control.inspect().active()
    registered = current_app.control.inspect().registered()

    return {
        "stats": stats,
        "active_tasks": active,
        "registered_tasks": registered,
        "timestamp": time.time()
    }


# Utility functions for task management

def distribute_evaluation_tasks(
    individuals: List[Individual],
    eval_func_name: str = "default"
) -> List[Any]:
    """
    Distribute evaluation tasks to workers

    Args:
        individuals: List of individuals to evaluate
        eval_func_name: Evaluation function name

    Returns:
        List of AsyncResult objects
    """
    tasks = []

    for individual in individuals:
        ind_data = IndividualData(
            id=individual.id,
            prompt=individual.prompt,
            fitness_scores={},
            generation=individual.generation,
            parent_ids=individual.parent_ids
        )

        task = evaluate_individual.delay(ind_data.to_dict(), eval_func_name)
        tasks.append(task)

    return tasks


def distribute_evolution_tasks(
    seed_prompts_list: List[List[str]],
    generations: int = 5,
    population_size: int = 10,
    eval_func_name: str = "default"
) -> List[Any]:
    """
    Distribute evolution tasks to workers

    Args:
        seed_prompts_list: List of seed prompt sets (one per worker)
        generations: Number of generations
        population_size: Population size
        eval_func_name: Evaluation function name

    Returns:
        List of AsyncResult objects
    """
    tasks = []

    for seed_prompts in seed_prompts_list:
        task = run_local_evolution.delay(
            seed_prompts,
            generations,
            population_size,
            eval_func_name
        )
        tasks.append(task)

    return tasks


def wait_for_tasks(
    tasks: List[Any],
    timeout: float = None
) -> List[Dict[str, Any]]:
    """
    Wait for tasks to complete

    Args:
        tasks: List of AsyncResult objects
        timeout: Timeout in seconds

    Returns:
        List of results
    """
    results = []

    for task in tasks:
        try:
            result = task.get(timeout=timeout)
            results.append(result)
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            results.append({"error": str(e), "task_id": task.id})

    return results
