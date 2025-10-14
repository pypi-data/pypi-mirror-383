"""
Evolution Engine - Core GEPA Implementation

Implements the main evolutionary loop for prompt optimization.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class Individual:
    """Represents a single prompt individual in the population"""
    prompt: str
    fitness_scores: Dict[str, float] = field(default_factory=dict)
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            import uuid
            self.id = str(uuid.uuid4())[:8]


@dataclass
class EvolutionConfig:
    """Configuration for evolution engine"""
    population_size: int = 20
    generations: int = 10
    mutation_rate: float = 0.3
    crossover_rate: float = 0.5
    elitism_rate: float = 0.1
    objectives: List[str] = field(default_factory=lambda: ["accuracy", "speed", "cost"])
    max_workers: int = 4
    teacher_model: str = "claude-3-5-sonnet-20241022"
    student_model: str = "claude-3-5-sonnet-20241022"


class EvolutionEngine:
    """
    Main evolution engine implementing GEPA

    GEPA (Genetic-Pareto Reflective Evolution) combines:
    - Genetic Algorithm for population evolution
    - Pareto optimization for multi-objective optimization
    - Reflection mechanism for intelligent mutation
    """

    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.population: List[Individual] = []
        self.generation = 0
        self.history: List[Dict[str, Any]] = []
        self.best_individuals: List[Individual] = []

    def initialize_population(self, seed_prompts: List[str]) -> List[Individual]:
        """Initialize population with seed prompts"""
        population = []

        # Use provided seeds
        for prompt in seed_prompts[:self.config.population_size]:
            population.append(Individual(prompt=prompt, generation=0))

        # Generate variations if needed
        while len(population) < self.config.population_size:
            base_prompt = np.random.choice(seed_prompts)
            # Simple variation for now (will be enhanced with reflection)
            varied = self._simple_variation(base_prompt)
            population.append(Individual(prompt=varied, generation=0))

        return population

    def _simple_variation(self, prompt: str) -> str:
        """Create simple variation of prompt"""
        variations = [
            f"{prompt}\n\nBe precise and specific.",
            f"{prompt}\n\nProvide detailed reasoning.",
            f"Task: {prompt}\n\nFollow these instructions carefully.",
        ]
        return np.random.choice(variations)

    def evaluate_population(
        self,
        population: List[Individual],
        eval_func: Callable[[str], Dict[str, float]]
    ) -> List[Individual]:
        """Evaluate fitness of all individuals in parallel"""

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(eval_func, ind.prompt): ind
                for ind in population
            }

            for future in as_completed(futures):
                individual = futures[future]
                try:
                    scores = future.result()
                    individual.fitness_scores = scores
                except Exception as e:
                    print(f"Error evaluating individual {individual.id}: {e}")
                    # Assign poor scores on failure
                    individual.fitness_scores = {
                        obj: 0.0 for obj in self.config.objectives
                    }

        return population

    def select_parents(
        self,
        population: List[Individual],
        n_parents: int
    ) -> List[Individual]:
        """Select parents using tournament selection"""
        parents = []
        tournament_size = 3

        for _ in range(n_parents):
            # Tournament selection
            tournament = np.random.choice(population, tournament_size, replace=False)
            # Select best based on primary objective (accuracy)
            best = max(
                tournament,
                key=lambda x: x.fitness_scores.get("accuracy", 0.0)
            )
            parents.append(best)

        return parents

    def generate_offspring(
        self,
        parents: List[Individual],
        n_offspring: int
    ) -> List[Individual]:
        """Generate offspring through crossover and mutation"""
        offspring = []

        while len(offspring) < n_offspring:
            # Select two parents
            parent1, parent2 = np.random.choice(parents, 2, replace=False)

            # Crossover
            if np.random.random() < self.config.crossover_rate:
                child_prompt = self._crossover(parent1.prompt, parent2.prompt)
            else:
                child_prompt = parent1.prompt

            # Mutation
            if np.random.random() < self.config.mutation_rate:
                child_prompt = self._mutate(child_prompt)

            child = Individual(
                prompt=child_prompt,
                generation=self.generation + 1,
                parent_ids=[parent1.id, parent2.id]
            )
            offspring.append(child)

        return offspring

    def _crossover(self, prompt1: str, prompt2: str) -> str:
        """Semantic crossover of two prompts"""
        # Simple implementation: combine parts of both prompts
        lines1 = prompt1.split('\n')
        lines2 = prompt2.split('\n')

        # Take first half from prompt1, second half from prompt2
        mid1 = len(lines1) // 2
        mid2 = len(lines2) // 2

        combined = lines1[:mid1] + lines2[mid2:]
        return '\n'.join(combined)

    def _mutate(self, prompt: str) -> str:
        """Mutate prompt (will be enhanced with reflection)"""
        mutations = [
            lambda p: f"{p}\n\nImportant: Be precise.",
            lambda p: f"{p}\n\nNote: Check edge cases.",
            lambda p: p.replace(".", ".\n"),  # Add line breaks
        ]
        mutation_func = np.random.choice(mutations)
        return mutation_func(prompt)

    def survivor_selection(
        self,
        population: List[Individual],
        offspring: List[Individual]
    ) -> List[Individual]:
        """Select survivors for next generation"""
        combined = population + offspring

        # Sort by accuracy (primary objective)
        combined.sort(
            key=lambda x: x.fitness_scores.get("accuracy", 0.0),
            reverse=True
        )

        # Keep top individuals
        n_elite = int(self.config.population_size * self.config.elitism_rate)
        elite = combined[:n_elite]

        # Fill rest randomly from remaining
        remaining = combined[n_elite:]
        n_remaining = self.config.population_size - n_elite
        survivors = elite + list(np.random.choice(remaining, n_remaining, replace=False))

        return survivors

    def evolve(
        self,
        seed_prompts: List[str],
        eval_func: Callable[[str], Dict[str, float]],
        generations: Optional[int] = None
    ) -> Individual:
        """
        Main evolution loop

        Args:
            seed_prompts: Initial prompts to start evolution
            eval_func: Function to evaluate prompt quality
            generations: Number of generations (uses config if None)

        Returns:
            Best individual found
        """
        generations = generations or self.config.generations

        # Initialize
        self.population = self.initialize_population(seed_prompts)
        self.population = self.evaluate_population(self.population, eval_func)

        # Evolution loop
        for gen in range(generations):
            self.generation = gen

            # Log generation stats
            best = max(
                self.population,
                key=lambda x: x.fitness_scores.get("accuracy", 0.0)
            )
            avg_accuracy = np.mean([
                ind.fitness_scores.get("accuracy", 0.0)
                for ind in self.population
            ])

            print(f"Generation {gen}: Best={best.fitness_scores.get('accuracy', 0.0):.3f}, "
                  f"Avg={avg_accuracy:.3f}")

            # Save to history
            self.history.append({
                "generation": gen,
                "best_accuracy": best.fitness_scores.get("accuracy", 0.0),
                "avg_accuracy": avg_accuracy,
                "best_prompt": best.prompt
            })

            # Selection
            n_parents = self.config.population_size // 2
            parents = self.select_parents(self.population, n_parents)

            # Generate offspring
            n_offspring = self.config.population_size
            offspring = self.generate_offspring(parents, n_offspring)

            # Evaluate offspring
            offspring = self.evaluate_population(offspring, eval_func)

            # Survivor selection
            self.population = self.survivor_selection(self.population, offspring)

        # Return best individual
        best = max(
            self.population,
            key=lambda x: x.fitness_scores.get("accuracy", 0.0)
        )
        return best

    def get_pareto_front(self) -> List[Individual]:
        """Get Pareto-optimal individuals (implemented in pareto.py)"""
        from .pareto import ParetoOptimizer
        optimizer = ParetoOptimizer(self.config.objectives)
        return optimizer.compute_pareto_front(self.population)
