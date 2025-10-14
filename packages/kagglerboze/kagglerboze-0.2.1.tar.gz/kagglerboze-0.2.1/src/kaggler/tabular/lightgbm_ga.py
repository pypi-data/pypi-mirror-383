"""
LightGBM Genetic Algorithm Optimizer

Genetic algorithm-based hyperparameter optimization for LightGBM models.
Uses population-based search with cross-validation fitness evaluation.
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass
import random
import time
from tqdm import tqdm


@dataclass
class LightGBMIndividual:
    """Individual in the genetic algorithm population."""
    params: Dict[str, Any]
    fitness: float = 0.0
    cv_scores: List[float] = None

    def __post_init__(self):
        if self.cv_scores is None:
            self.cv_scores = []


class LightGBMGA:
    """
    LightGBM Genetic Algorithm Optimizer.

    Optimizes LightGBM hyperparameters using genetic algorithm with:
    - Population-based search
    - Tournament selection
    - Uniform/blend crossover
    - Gaussian mutation
    - Elitism preservation

    Example:
        >>> from kaggler.tabular import LightGBMGA
        >>> optimizer = LightGBMGA(population_size=20, n_generations=10)
        >>> best_params = optimizer.optimize(X_train, y_train, X_val, y_val)
        >>> predictions = optimizer.predict(X_test)
    """

    def __init__(
        self,
        population_size: int = 20,
        n_generations: int = 15,
        mutation_rate: float = 0.2,
        crossover_rate: float = 0.8,
        elitism_ratio: float = 0.1,
        n_folds: int = 5,
        early_stopping_rounds: int = 50,
        objective: str = "binary",
        metric: str = "auc",
        n_jobs: int = -1,
        random_state: int = 42,
        verbose: bool = True,
    ):
        """
        Initialize LightGBMGA optimizer.

        Args:
            population_size: Number of individuals in population
            n_generations: Number of generations to evolve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            elitism_ratio: Fraction of top individuals to preserve
            n_folds: Number of CV folds for fitness evaluation
            early_stopping_rounds: Early stopping for LightGBM
            objective: LightGBM objective function
            metric: Evaluation metric
            n_jobs: Number of parallel jobs
            random_state: Random seed
            verbose: Print progress
        """
        self.population_size = population_size
        self.n_generations = n_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_ratio = elitism_ratio
        self.n_folds = n_folds
        self.early_stopping_rounds = early_stopping_rounds
        self.objective = objective
        self.metric = metric
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.verbose = verbose

        self.best_individual: Optional[LightGBMIndividual] = None
        self.best_model = None
        self.population: List[LightGBMIndividual] = []
        self.history: List[Dict[str, float]] = []

        random.seed(random_state)
        np.random.seed(random_state)

        # Hyperparameter search space
        self.param_space = {
            "num_leaves": (20, 150),
            "max_depth": (3, 10),
            "learning_rate": (0.001, 0.3),
            "n_estimators": (50, 1000),
            "min_child_samples": (10, 100),
            "min_child_weight": (1e-5, 10.0),
            "subsample": (0.5, 1.0),
            "colsample_bytree": (0.5, 1.0),
            "reg_alpha": (0.0, 10.0),
            "reg_lambda": (0.0, 10.0),
            "min_split_gain": (0.0, 1.0),
            "subsample_freq": (0, 10),
        }

    def _create_individual(self) -> LightGBMIndividual:
        """Create a random individual."""
        params = {}
        for param, (low, high) in self.param_space.items():
            if param in ["num_leaves", "max_depth", "n_estimators", "min_child_samples", "subsample_freq"]:
                params[param] = random.randint(int(low), int(high))
            else:
                params[param] = random.uniform(low, high)

        # Add fixed parameters
        params.update({
            "objective": self.objective,
            "metric": self.metric,
            "boosting_type": "gbdt",
            "random_state": self.random_state,
            "n_jobs": self.n_jobs,
            "verbose": -1,
        })

        return LightGBMIndividual(params=params)

    def _evaluate_fitness(
        self,
        individual: LightGBMIndividual,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> float:
        """
        Evaluate individual fitness using cross-validation.

        Args:
            individual: Individual to evaluate
            X: Training features
            y: Training labels

        Returns:
            Mean CV score (higher is better)
        """
        try:
            import lightgbm as lgb
            from sklearn.model_selection import cross_val_score

            model = lgb.LGBMClassifier(**individual.params)

            # Use stratified k-fold CV
            scores = cross_val_score(
                model,
                X,
                y,
                cv=self.n_folds,
                scoring="roc_auc" if self.metric == "auc" else "accuracy",
                n_jobs=1,  # LightGBM already uses parallel processing
            )

            individual.cv_scores = scores.tolist()
            individual.fitness = float(np.mean(scores))

            return individual.fitness

        except Exception as e:
            if self.verbose:
                print(f"Error evaluating individual: {e}")
            individual.fitness = 0.0
            return 0.0

    def _tournament_selection(
        self,
        tournament_size: int = 3,
    ) -> LightGBMIndividual:
        """Select individual using tournament selection."""
        tournament = random.sample(self.population, tournament_size)
        return max(tournament, key=lambda ind: ind.fitness)

    def _crossover(
        self,
        parent1: LightGBMIndividual,
        parent2: LightGBMIndividual,
    ) -> Tuple[LightGBMIndividual, LightGBMIndividual]:
        """
        Perform crossover between two parents.
        Uses blend crossover for continuous parameters.
        """
        if random.random() > self.crossover_rate:
            return parent1, parent2

        child1_params = {}
        child2_params = {}

        for param in self.param_space.keys():
            if param in ["num_leaves", "max_depth", "n_estimators", "min_child_samples", "subsample_freq"]:
                # Uniform crossover for integers
                if random.random() < 0.5:
                    child1_params[param] = parent1.params[param]
                    child2_params[param] = parent2.params[param]
                else:
                    child1_params[param] = parent2.params[param]
                    child2_params[param] = parent1.params[param]
            else:
                # Blend crossover for continuous
                alpha = 0.5
                v1, v2 = parent1.params[param], parent2.params[param]
                child1_params[param] = alpha * v1 + (1 - alpha) * v2
                child2_params[param] = (1 - alpha) * v1 + alpha * v2

        # Copy fixed parameters
        for key in ["objective", "metric", "boosting_type", "random_state", "n_jobs", "verbose"]:
            child1_params[key] = parent1.params[key]
            child2_params[key] = parent2.params[key]

        return (
            LightGBMIndividual(params=child1_params),
            LightGBMIndividual(params=child2_params),
        )

    def _mutate(self, individual: LightGBMIndividual) -> LightGBMIndividual:
        """
        Mutate individual using Gaussian noise.
        """
        if random.random() > self.mutation_rate:
            return individual

        mutated_params = individual.params.copy()

        # Select random parameter to mutate
        param = random.choice(list(self.param_space.keys()))
        low, high = self.param_space[param]

        if param in ["num_leaves", "max_depth", "n_estimators", "min_child_samples", "subsample_freq"]:
            # Integer mutation
            delta = random.randint(-2, 2)
            mutated_params[param] = max(int(low), min(int(high), individual.params[param] + delta))
        else:
            # Gaussian mutation for continuous
            sigma = (high - low) * 0.1
            noise = np.random.normal(0, sigma)
            mutated_params[param] = max(low, min(high, individual.params[param] + noise))

        return LightGBMIndividual(params=mutated_params)

    def optimize(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> Dict[str, Any]:
        """
        Optimize hyperparameters using genetic algorithm.

        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)

        Returns:
            Best hyperparameters found
        """
        import lightgbm as lgb

        start_time = time.time()

        # Initialize population
        if self.verbose:
            print(f"Initializing population of {self.population_size} individuals...")

        self.population = [self._create_individual() for _ in range(self.population_size)]

        # Evaluate initial population
        for ind in tqdm(self.population, desc="Initial evaluation", disable=not self.verbose):
            self._evaluate_fitness(ind, X_train, y_train)

        # Evolution loop
        for generation in range(self.n_generations):
            if self.verbose:
                print(f"\n--- Generation {generation + 1}/{self.n_generations} ---")

            # Sort by fitness
            self.population.sort(key=lambda ind: ind.fitness, reverse=True)

            # Track best individual
            if self.best_individual is None or self.population[0].fitness > self.best_individual.fitness:
                self.best_individual = self.population[0]

            # Log statistics
            fitnesses = [ind.fitness for ind in self.population]
            stats = {
                "generation": generation + 1,
                "best_fitness": max(fitnesses),
                "mean_fitness": np.mean(fitnesses),
                "std_fitness": np.std(fitnesses),
            }
            self.history.append(stats)

            if self.verbose:
                print(f"Best: {stats['best_fitness']:.4f} | "
                      f"Mean: {stats['mean_fitness']:.4f} | "
                      f"Std: {stats['std_fitness']:.4f}")

            # Elitism: preserve top individuals
            n_elite = max(1, int(self.population_size * self.elitism_ratio))
            new_population = self.population[:n_elite]

            # Generate offspring
            while len(new_population) < self.population_size:
                # Selection
                parent1 = self._tournament_selection()
                parent2 = self._tournament_selection()

                # Crossover
                child1, child2 = self._crossover(parent1, parent2)

                # Mutation
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)

                # Evaluate offspring
                self._evaluate_fitness(child1, X_train, y_train)
                if len(new_population) < self.population_size:
                    new_population.append(child1)

                if len(new_population) < self.population_size:
                    self._evaluate_fitness(child2, X_train, y_train)
                    new_population.append(child2)

            self.population = new_population

        # Train final model with best parameters
        if self.verbose:
            print("\n" + "="*50)
            print("Training final model with best parameters...")

        self.best_model = lgb.LGBMClassifier(**self.best_individual.params)

        if X_val is not None and y_val is not None:
            self.best_model.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                callbacks=[lgb.early_stopping(self.early_stopping_rounds, verbose=False)],
            )
        else:
            self.best_model.fit(X_train, y_train)

        elapsed_time = time.time() - start_time

        if self.verbose:
            print(f"Optimization completed in {elapsed_time:.2f} seconds")
            print(f"Best fitness: {self.best_individual.fitness:.4f}")
            print(f"Best CV scores: {self.best_individual.cv_scores}")

        return self.best_individual.params

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions using the best model.

        Args:
            X: Features to predict

        Returns:
            Predicted labels
        """
        if self.best_model is None:
            raise ValueError("Model not trained. Call optimize() first.")

        return self.best_model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict class probabilities.

        Args:
            X: Features to predict

        Returns:
            Predicted probabilities
        """
        if self.best_model is None:
            raise ValueError("Model not trained. Call optimize() first.")

        return self.best_model.predict_proba(X)

    def get_best_params(self) -> Dict[str, Any]:
        """
        Get best hyperparameters found.

        Returns:
            Dictionary of best parameters
        """
        if self.best_individual is None:
            raise ValueError("No optimization run yet. Call optimize() first.")

        return self.best_individual.params.copy()

    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance from best model.

        Returns:
            DataFrame with feature importance
        """
        if self.best_model is None:
            raise ValueError("Model not trained. Call optimize() first.")

        importance = self.best_model.feature_importances_

        # Get feature names - handle both trained and fitted models
        if hasattr(self.best_model, 'feature_names_in_'):
            feature_names = self.best_model.feature_names_in_
        elif hasattr(self.best_model, 'feature_name_'):
            feature_names = self.best_model.feature_name_
        else:
            feature_names = [f"feature_{i}" for i in range(len(importance))]

        df = pd.DataFrame({
            "feature": feature_names,
            "importance": importance,
        })

        return df.sort_values("importance", ascending=False).reset_index(drop=True)
