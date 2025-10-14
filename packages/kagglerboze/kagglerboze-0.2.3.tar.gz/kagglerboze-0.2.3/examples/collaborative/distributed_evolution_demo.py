"""
Distributed Evolution Demo

Demonstrates collaborative evolution with multiple workers,
comparing performance vs single-node evolution.
"""

import time
import sys
from typing import Dict, List
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kaggler.collaborative import (
    EvolutionCoordinator,
    CoordinatorConfig,
    WorkerNode,
    WorkerConfig,
)
from kaggler.core.evolution import Individual, EvolutionEngine, EvolutionConfig


def mock_eval_function(prompt: str) -> Dict[str, float]:
    """
    Mock evaluation function for demonstration

    In production, this would call actual model evaluation
    """
    import hashlib
    import time

    # Simulate evaluation time
    time.sleep(0.1)

    # Generate deterministic score based on prompt
    prompt_hash = int(hashlib.md5(prompt.encode()).hexdigest(), 16)
    base_score = (prompt_hash % 1000) / 1000.0

    # Bonus for length (heuristic)
    length_bonus = min(len(prompt) / 500.0, 0.2)

    # Bonus for good keywords
    keywords = ["analyze", "precise", "detailed", "accurate", "systematic"]
    keyword_bonus = sum(0.05 for kw in keywords if kw in prompt.lower())

    accuracy = min(base_score + length_bonus + keyword_bonus, 1.0)

    # Mock speed (inverse of length)
    speed = max(0.1, 1.0 - len(prompt) / 1000.0)

    # Mock cost (proportional to length)
    cost = len(prompt) / 100.0

    return {
        "accuracy": accuracy,
        "speed": speed,
        "cost": cost
    }


def run_single_node_evolution(
    seed_prompts: List[str],
    generations: int = 10,
    population_size: int = 30
) -> tuple[Individual, float]:
    """
    Run evolution on single node

    Returns:
        Tuple of (best_individual, elapsed_time)
    """
    print("\n" + "="*70)
    print("SINGLE-NODE EVOLUTION")
    print("="*70)

    start_time = time.time()

    config = EvolutionConfig(
        population_size=population_size,
        generations=generations,
        objectives=["accuracy", "speed", "cost"],
        max_workers=4
    )

    engine = EvolutionEngine(config)
    best = engine.evolve(seed_prompts, mock_eval_function, generations)

    elapsed = time.time() - start_time

    print(f"\nCompleted in {elapsed:.2f}s")
    print(f"Best fitness: {best.fitness_scores.get('accuracy', 0.0):.4f}")
    print(f"Total evaluations: ~{population_size * generations * 2}")

    return best, elapsed


def run_distributed_evolution(
    seed_prompts: List[str],
    generations: int = 10,
    population_size: int = 30,
    n_workers: int = 3
) -> tuple[Individual, float, Dict]:
    """
    Run distributed evolution with multiple workers

    Returns:
        Tuple of (best_individual, elapsed_time, statistics)
    """
    print("\n" + "="*70)
    print(f"DISTRIBUTED EVOLUTION ({n_workers} workers)")
    print("="*70)

    start_time = time.time()

    # Configure coordinator
    config = CoordinatorConfig(
        population_size=population_size,
        n_workers=n_workers,
        generations=generations,
        sync_interval=5,
        objectives=["accuracy", "speed", "cost"],
        merge_strategy="adaptive",
        enable_tracking=True
    )

    # Create coordinator
    coordinator = EvolutionCoordinator(config, mock_eval_function)

    # Run evolution
    best = coordinator.start_evolution(seed_prompts)

    elapsed = time.time() - start_time

    # Get statistics
    stats = coordinator.get_statistics()

    print(f"\nCompleted in {elapsed:.2f}s")
    print(f"Best fitness: {best.fitness_scores.get('accuracy', 0.0):.4f}")
    print(f"Total evaluations: {sum(w.get_statistics()['total_evaluations'] for w in coordinator.workers.values())}")
    print(f"Active workers: {stats['active_workers']}/{stats['n_workers']}")

    return best, elapsed, stats


def visualize_comparison(
    single_time: float,
    distributed_time: float,
    single_best: Individual,
    distributed_best: Individual,
    stats: Dict
):
    """Visualize performance comparison"""
    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON")
    print("="*70)

    speedup = single_time / distributed_time
    print(f"\nSpeedup: {speedup:.2f}x")
    print(f"Single-node time: {single_time:.2f}s")
    print(f"Distributed time: {distributed_time:.2f}s")
    print(f"Time saved: {single_time - distributed_time:.2f}s ({(1 - distributed_time/single_time)*100:.1f}%)")

    print("\nBest Fitness:")
    print(f"  Single-node: {single_best.fitness_scores.get('accuracy', 0.0):.4f}")
    print(f"  Distributed: {distributed_best.fitness_scores.get('accuracy', 0.0):.4f}")

    improvement = distributed_best.fitness_scores.get('accuracy', 0.0) - single_best.fitness_scores.get('accuracy', 0.0)
    print(f"  Improvement: {improvement:+.4f} ({improvement/single_best.fitness_scores.get('accuracy', 1.0)*100:+.1f}%)")

    print("\nPareto Front:")
    print(f"  Size: {stats['pareto_size']}")

    print("\nWorker Statistics:")
    for worker_id, worker_stats in stats.get('contributions', {}).get('worker_stats', {}).items():
        print(f"  {worker_id}:")
        print(f"    Contributions: {worker_stats['total_contributions']}")
        print(f"    Improvements: {worker_stats['improvement_count']}")
        print(f"    Best fitness: {worker_stats['best_fitness']:.4f}")
        print(f"    Pareto count: {worker_stats['pareto_count']}")


def visualize_contribution_timeline(stats: Dict):
    """Visualize contribution timeline"""
    print("\n" + "="*70)
    print("CONTRIBUTION TIMELINE")
    print("="*70)

    history = stats.get('history', [])
    if not history:
        print("No history available")
        return

    print("\nGeneration | Best Fitness | Avg Fitness | Pareto Size | Active Workers")
    print("-" * 70)

    for entry in history[::2]:  # Every 2 generations
        gen = entry['generation']
        best = entry['best_fitness']
        avg = entry['avg_fitness']
        pareto = entry['pareto_size']
        workers = entry['active_workers']

        # Simple bar chart
        bar_length = int(best * 40)
        bar = "█" * bar_length

        print(f"{gen:^10} | {best:^12.4f} | {avg:^11.4f} | {pareto:^11} | {workers:^14}")
        print(f"           {bar}")


def main():
    """Main demo"""
    print("\n" + "="*70)
    print("COLLABORATIVE EVOLUTION DEMO")
    print("="*70)

    # Seed prompts
    seed_prompts = [
        "Analyze the given data and provide insights.",
        "Perform a detailed systematic analysis of the dataset.",
        "Examine the data carefully and extract key patterns.",
        "Provide a comprehensive evaluation of the information.",
        "Conduct a thorough investigation of the data points.",
    ]

    # Parameters
    GENERATIONS = 10
    POPULATION_SIZE = 30
    N_WORKERS = 3

    print(f"\nConfiguration:")
    print(f"  Generations: {GENERATIONS}")
    print(f"  Population size: {POPULATION_SIZE}")
    print(f"  Number of workers: {N_WORKERS}")
    print(f"  Seed prompts: {len(seed_prompts)}")

    # Run single-node evolution
    single_best, single_time = run_single_node_evolution(
        seed_prompts,
        GENERATIONS,
        POPULATION_SIZE
    )

    # Run distributed evolution
    distributed_best, distributed_time, stats = run_distributed_evolution(
        seed_prompts,
        GENERATIONS,
        POPULATION_SIZE,
        N_WORKERS
    )

    # Visualize comparison
    visualize_comparison(
        single_time,
        distributed_time,
        single_best,
        distributed_best,
        stats
    )

    # Visualize contribution timeline
    visualize_contribution_timeline(stats)

    # Show best prompts
    print("\n" + "="*70)
    print("BEST PROMPTS")
    print("="*70)

    print("\nSingle-node best:")
    print(f"  {single_best.prompt[:100]}...")
    print(f"  Fitness: {single_best.fitness_scores}")

    print("\nDistributed best:")
    print(f"  {distributed_best.prompt[:100]}...")
    print(f"  Fitness: {distributed_best.fitness_scores}")

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
