"""
Pareto Optimization - Multi-objective optimization

Implements Pareto frontier computation for balancing
multiple objectives (accuracy, speed, cost).
"""

from typing import List, Dict
from dataclasses import dataclass
import numpy as np


@dataclass
class ParetoSolution:
    """Represents a solution in Pareto space"""
    individual: any  # Individual from evolution.py
    objectives: Dict[str, float]
    rank: int = 0
    crowding_distance: float = 0.0


class ParetoOptimizer:
    """
    Pareto optimization for multi-objective problems

    Balances multiple competing objectives:
    - Accuracy (maximize)
    - Speed/Latency (minimize)
    - Cost (minimize)
    """

    def __init__(self, objectives: List[str]):
        self.objectives = objectives
        # Define which objectives to maximize vs minimize
        self.maximize = {"accuracy", "precision", "recall", "f1"}
        self.minimize = {"speed", "cost", "latency", "tokens"}

    def dominates(self, solution1: ParetoSolution, solution2: ParetoSolution) -> bool:
        """
        Check if solution1 dominates solution2

        Solution1 dominates solution2 if:
        - It's at least as good in all objectives
        - It's strictly better in at least one objective
        """
        at_least_as_good = True
        strictly_better = False

        for obj in self.objectives:
            score1 = solution1.objectives.get(obj, 0.0)
            score2 = solution2.objectives.get(obj, 0.0)

            if obj in self.maximize:
                # For maximize objectives, higher is better
                if score1 < score2:
                    at_least_as_good = False
                if score1 > score2:
                    strictly_better = True
            else:
                # For minimize objectives, lower is better
                if score1 > score2:
                    at_least_as_good = False
                if score1 < score2:
                    strictly_better = True

        return at_least_as_good and strictly_better

    def compute_pareto_front(self, population: List[any]) -> List[any]:
        """
        Compute Pareto frontier from population

        Returns individuals that are not dominated by any other individual
        """
        # Convert population to ParetoSolutions
        solutions = [
            ParetoSolution(
                individual=ind,
                objectives=ind.fitness_scores.copy()
            )
            for ind in population
        ]

        pareto_front = []

        for candidate in solutions:
            is_dominated = False

            for other in solutions:
                if candidate.individual.id == other.individual.id:
                    continue

                if self.dominates(other, candidate):
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_front.append(candidate.individual)

        return pareto_front

    def assign_ranks(self, population: List[any]) -> List[ParetoSolution]:
        """
        Assign Pareto ranks to all solutions

        Rank 0 = Pareto front
        Rank 1 = Dominated only by rank 0
        etc.
        """
        solutions = [
            ParetoSolution(
                individual=ind,
                objectives=ind.fitness_scores.copy()
            )
            for ind in population
        ]

        ranked_solutions = []
        remaining = solutions.copy()
        current_rank = 0

        while remaining:
            # Find Pareto front in remaining
            front = []
            for candidate in remaining:
                is_dominated = False
                for other in remaining:
                    if candidate.individual.id == other.individual.id:
                        continue
                    if self.dominates(other, candidate):
                        is_dominated = True
                        break

                if not is_dominated:
                    candidate.rank = current_rank
                    front.append(candidate)

            # Remove front from remaining
            for sol in front:
                remaining.remove(sol)
                ranked_solutions.append(sol)

            current_rank += 1

        return ranked_solutions

    def compute_crowding_distance(self, solutions: List[ParetoSolution]) -> None:
        """
        Compute crowding distance for diversity preservation

        Crowding distance measures how close a solution is to its neighbors.
        Higher crowding distance = more unique/diverse solution.
        """
        n = len(solutions)

        if n <= 2:
            # Boundary solutions get infinite distance
            for sol in solutions:
                sol.crowding_distance = float('inf')
            return

        # Initialize distances
        for sol in solutions:
            sol.crowding_distance = 0.0

        # For each objective
        for obj in self.objectives:
            # Sort by objective value
            solutions.sort(key=lambda s: s.objectives.get(obj, 0.0))

            # Boundary solutions get infinite distance
            solutions[0].crowding_distance = float('inf')
            solutions[-1].crowding_distance = float('inf')

            # Get objective range
            obj_range = (
                solutions[-1].objectives.get(obj, 0.0) -
                solutions[0].objectives.get(obj, 0.0)
            )

            if obj_range == 0:
                continue

            # Compute distances for middle solutions
            for i in range(1, n - 1):
                distance = (
                    solutions[i + 1].objectives.get(obj, 0.0) -
                    solutions[i - 1].objectives.get(obj, 0.0)
                ) / obj_range
                solutions[i].crowding_distance += distance

    def select_best_tradeoff(
        self,
        pareto_front: List[any],
        weights: Dict[str, float] = None
    ) -> any:
        """
        Select best solution from Pareto front based on weights

        Args:
            pareto_front: List of non-dominated solutions
            weights: Importance weights for each objective

        Returns:
            Individual with best weighted score
        """
        if not weights:
            # Default equal weights
            weights = {obj: 1.0 / len(self.objectives) for obj in self.objectives}

        best_solution = None
        best_score = float('-inf')

        for individual in pareto_front:
            # Compute weighted score
            score = 0.0
            for obj in self.objectives:
                obj_score = individual.fitness_scores.get(obj, 0.0)

                # Normalize based on objective type
                if obj in self.minimize:
                    # For minimize objectives, invert score
                    obj_score = 1.0 / (1.0 + obj_score)

                score += weights.get(obj, 0.0) * obj_score

            if score > best_score:
                best_score = score
                best_solution = individual

        return best_solution

    def visualize_pareto_front(
        self,
        pareto_front: List[any],
        obj_x: str = "accuracy",
        obj_y: str = "cost"
    ) -> Dict[str, List[float]]:
        """
        Get data for visualizing Pareto front

        Returns dict with x and y coordinates
        """
        x_values = []
        y_values = []

        for individual in pareto_front:
            x_values.append(individual.fitness_scores.get(obj_x, 0.0))
            y_values.append(individual.fitness_scores.get(obj_y, 0.0))

        return {
            "x": x_values,
            "y": y_values,
            "x_label": obj_x,
            "y_label": obj_y
        }
