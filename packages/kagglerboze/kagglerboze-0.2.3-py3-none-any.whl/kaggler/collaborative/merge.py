"""
Merge Strategies for Collaborative Evolution

Implements different strategies for merging populations from multiple workers.
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import numpy as np
from dataclasses import dataclass


@dataclass
class MergeStats:
    """Statistics from a merge operation"""
    input_populations: int
    input_size: int
    output_size: int
    diversity_before: float
    diversity_after: float
    avg_fitness_before: float
    avg_fitness_after: float
    merge_strategy: str
    merge_time: float


class MergeStrategy(ABC):
    """
    Abstract base class for merge strategies

    Subclasses implement different approaches for combining populations
    from multiple workers into a unified population.
    """

    def __init__(self, target_size: int):
        """
        Initialize merge strategy

        Args:
            target_size: Desired size of merged population
        """
        self.target_size = target_size

    @abstractmethod
    def merge(
        self,
        populations: List[List[Any]],
        generation: int
    ) -> List[Any]:
        """
        Merge multiple populations into one

        Args:
            populations: List of populations (each is list of Individuals)
            generation: Current generation number

        Returns:
            Merged population
        """
        pass

    def _compute_diversity(self, population: List[Any]) -> float:
        """
        Compute population diversity

        Uses prompt length variance as simple diversity metric
        """
        if not population:
            return 0.0

        lengths = [len(ind.prompt) for ind in population]
        return float(np.std(lengths))

    def _compute_avg_fitness(
        self,
        population: List[Any],
        objective: str = "accuracy"
    ) -> float:
        """Compute average fitness for an objective"""
        if not population:
            return 0.0

        scores = [ind.fitness_scores.get(objective, 0.0) for ind in population]
        return float(np.mean(scores))


class EliteMerger(MergeStrategy):
    """
    Elite Merging Strategy

    Keeps top N individuals from all populations combined.
    Simple and effective for exploitation.
    """

    def __init__(self, target_size: int, objective: str = "accuracy"):
        """
        Initialize elite merger

        Args:
            target_size: Number of individuals to keep
            objective: Fitness objective to optimize
        """
        super().__init__(target_size)
        self.objective = objective

    def merge(
        self,
        populations: List[List[Any]],
        generation: int
    ) -> List[Any]:
        """
        Merge by keeping top individuals

        Args:
            populations: List of populations
            generation: Current generation

        Returns:
            Merged population with best individuals
        """
        # Combine all populations
        combined = []
        for pop in populations:
            combined.extend(pop)

        if not combined:
            return []

        # Sort by fitness (descending)
        combined.sort(
            key=lambda x: x.fitness_scores.get(self.objective, 0.0),
            reverse=True
        )

        # Keep top N
        return combined[:self.target_size]


class DiversityMerger(MergeStrategy):
    """
    Diversity-Based Merging Strategy

    Maintains population diversity while keeping good fitness.
    Balances exploration and exploitation.
    """

    def __init__(
        self,
        target_size: int,
        elite_ratio: float = 0.3,
        objective: str = "accuracy"
    ):
        """
        Initialize diversity merger

        Args:
            target_size: Target population size
            elite_ratio: Fraction of elite individuals to keep
            objective: Primary fitness objective
        """
        super().__init__(target_size)
        self.elite_ratio = elite_ratio
        self.objective = objective

    def merge(
        self,
        populations: List[List[Any]],
        generation: int
    ) -> List[Any]:
        """
        Merge with diversity preservation

        Strategy:
        1. Keep top elite_ratio% individuals
        2. Fill rest with diverse individuals
        """
        # Combine populations
        combined = []
        for pop in populations:
            combined.extend(pop)

        if not combined:
            return []

        # Sort by fitness
        combined.sort(
            key=lambda x: x.fitness_scores.get(self.objective, 0.0),
            reverse=True
        )

        # Select elite
        n_elite = int(self.target_size * self.elite_ratio)
        merged = combined[:n_elite]

        # Fill rest with diverse individuals
        remaining = combined[n_elite:]
        n_diverse = self.target_size - n_elite

        if remaining:
            diverse_individuals = self._select_diverse(remaining, n_diverse)
            merged.extend(diverse_individuals)

        return merged[:self.target_size]

    def _select_diverse(
        self,
        candidates: List[Any],
        n_select: int
    ) -> List[Any]:
        """
        Select diverse individuals using greedy diversity selection

        Args:
            candidates: Pool of candidates
            n_select: Number to select

        Returns:
            Selected diverse individuals
        """
        if len(candidates) <= n_select:
            return candidates

        selected = []
        remaining = candidates.copy()

        # Start with random individual
        first = np.random.choice(remaining)
        selected.append(first)
        remaining.remove(first)

        # Greedily select most diverse
        while len(selected) < n_select and remaining:
            best_candidate = None
            best_diversity = -1

            for candidate in remaining:
                # Compute min distance to selected
                min_dist = min(
                    self._distance(candidate, selected_ind)
                    for selected_ind in selected
                )

                if min_dist > best_diversity:
                    best_diversity = min_dist
                    best_candidate = candidate

            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)

        return selected

    def _distance(self, ind1: Any, ind2: Any) -> float:
        """
        Compute distance between two individuals

        Uses Levenshtein distance on prompts as simple metric
        """
        # Simple distance: difference in prompt lengths
        # In production, could use edit distance or embedding similarity
        return abs(len(ind1.prompt) - len(ind2.prompt))


class ParetoMerger(MergeStrategy):
    """
    Pareto-Based Merging Strategy

    Combines Pareto frontiers from multiple populations.
    Best for multi-objective optimization.
    """

    def __init__(
        self,
        target_size: int,
        objectives: List[str] = None
    ):
        """
        Initialize Pareto merger

        Args:
            target_size: Target population size
            objectives: List of objectives to optimize
        """
        super().__init__(target_size)
        self.objectives = objectives or ["accuracy", "speed", "cost"]

    def merge(
        self,
        populations: List[List[Any]],
        generation: int
    ) -> List[Any]:
        """
        Merge using Pareto dominance

        Strategy:
        1. Compute Pareto fronts for each population
        2. Combine all fronts
        3. Recompute global Pareto ranking
        4. Select by rank and crowding distance
        """
        from ..core.pareto import ParetoOptimizer

        # Combine populations
        combined = []
        for pop in populations:
            combined.extend(pop)

        if not combined:
            return []

        # Compute Pareto ranking
        optimizer = ParetoOptimizer(self.objectives)
        ranked_solutions = optimizer.assign_ranks(combined)

        # Compute crowding distances
        optimizer.compute_crowding_distance(ranked_solutions)

        # Sort by rank, then by crowding distance
        ranked_solutions.sort(
            key=lambda sol: (sol.rank, -sol.crowding_distance)
        )

        # Select top individuals
        selected = [sol.individual for sol in ranked_solutions[:self.target_size]]

        return selected


class AdaptiveMerger(MergeStrategy):
    """
    Adaptive Merging Strategy

    Adjusts merge strategy based on evolution progress and performance.
    Uses elite merging early, switches to diversity later.
    """

    def __init__(
        self,
        target_size: int,
        max_generations: int,
        objectives: List[str] = None
    ):
        """
        Initialize adaptive merger

        Args:
            target_size: Target population size
            max_generations: Total number of generations
            objectives: Optimization objectives
        """
        super().__init__(target_size)
        self.max_generations = max_generations
        self.objectives = objectives or ["accuracy", "speed", "cost"]

        # Initialize sub-strategies
        self.elite_merger = EliteMerger(target_size)
        self.diversity_merger = DiversityMerger(target_size)
        self.pareto_merger = ParetoMerger(target_size, objectives)

        self.performance_history: List[float] = []

    def merge(
        self,
        populations: List[List[Any]],
        generation: int
    ) -> List[Any]:
        """
        Adaptively select merge strategy

        Early generations: Elite merging (exploitation)
        Middle generations: Diversity merging (exploration)
        Late generations: Pareto merging (optimization)
        """
        progress = generation / max(self.max_generations, 1)

        # Compute current population quality
        combined = []
        for pop in populations:
            combined.extend(pop)

        if not combined:
            return []

        avg_fitness = self._compute_avg_fitness(combined)
        self.performance_history.append(avg_fitness)

        # Check if we're stuck (no improvement)
        is_stuck = self._is_stuck()

        # Select strategy adaptively
        if is_stuck:
            # Use diversity merger to escape local optimum
            strategy = self.diversity_merger
            strategy_name = "diversity"
        elif progress < 0.3:
            # Early: elite merging
            strategy = self.elite_merger
            strategy_name = "elite"
        elif progress < 0.7:
            # Middle: diversity merging
            strategy = self.diversity_merger
            strategy_name = "diversity"
        else:
            # Late: Pareto merging
            strategy = self.pareto_merger
            strategy_name = "pareto"

        print(f"Generation {generation}: Using {strategy_name} merge strategy")

        return strategy.merge(populations, generation)

    def _is_stuck(self, window: int = 5, threshold: float = 0.01) -> bool:
        """
        Check if evolution is stuck (no improvement)

        Args:
            window: Number of generations to check
            threshold: Minimum improvement required

        Returns:
            True if stuck
        """
        if len(self.performance_history) < window:
            return False

        recent = self.performance_history[-window:]
        improvement = max(recent) - min(recent)

        return improvement < threshold


class WeightedMerger(MergeStrategy):
    """
    Weighted Merging Strategy

    Assigns weights to workers based on their contribution quality.
    Better workers get more representation in merged population.
    """

    def __init__(
        self,
        target_size: int,
        worker_weights: Dict[str, float] = None,
        objective: str = "accuracy"
    ):
        """
        Initialize weighted merger

        Args:
            target_size: Target population size
            worker_weights: Weights for each worker
            objective: Primary objective
        """
        super().__init__(target_size)
        self.worker_weights = worker_weights or {}
        self.objective = objective

    def merge(
        self,
        populations: List[List[Any]],
        generation: int
    ) -> List[Any]:
        """
        Merge with weighted sampling

        Workers with higher weights contribute more individuals
        """
        if not populations:
            return []

        # If no weights, use equal weights
        if not self.worker_weights:
            self.worker_weights = {
                f"worker_{i}": 1.0 for i in range(len(populations))
            }

        # Combine and tag individuals with source
        combined = []
        for i, pop in enumerate(populations):
            worker_id = f"worker_{i}"
            for ind in pop:
                combined.append((ind, worker_id))

        # Sort by fitness
        combined.sort(
            key=lambda x: x[0].fitness_scores.get(self.objective, 0.0),
            reverse=True
        )

        # Weighted selection
        selected = []
        worker_counts = {wid: 0 for wid in self.worker_weights.keys()}

        # Calculate target counts per worker
        total_weight = sum(self.worker_weights.values())
        target_counts = {
            wid: int(self.target_size * weight / total_weight)
            for wid, weight in self.worker_weights.items()
        }

        # Select individuals respecting weights
        for ind, worker_id in combined:
            if len(selected) >= self.target_size:
                break

            if worker_counts.get(worker_id, 0) < target_counts.get(worker_id, 0):
                selected.append(ind)
                worker_counts[worker_id] = worker_counts.get(worker_id, 0) + 1

        # Fill remaining slots with best available
        remaining = self.target_size - len(selected)
        if remaining > 0:
            for ind, _ in combined:
                if ind not in selected:
                    selected.append(ind)
                    if len(selected) >= self.target_size:
                        break

        return selected

    def update_weights(
        self,
        worker_contributions: Dict[str, float]
    ) -> None:
        """
        Update worker weights based on contributions

        Args:
            worker_contributions: Contribution scores for each worker
        """
        self.worker_weights = worker_contributions.copy()
