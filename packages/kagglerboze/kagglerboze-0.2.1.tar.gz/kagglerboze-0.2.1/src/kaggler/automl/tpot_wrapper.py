"""TPOT wrapper for genetic programming-based AutoML.

This module provides a wrapper around TPOT (Tree-based Pipeline Optimization Tool),
which uses genetic programming to optimize machine learning pipelines.
"""

import time
import warnings
from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd

from .base import AutoMLNotAvailableError, BaseAutoMLWrapper

try:
    from tpot import TPOTClassifier, TPOTRegressor
    TPOT_AVAILABLE = True
except ImportError:
    TPOT_AVAILABLE = False


class TPOTOptimizer(BaseAutoMLWrapper):
    """TPOT optimizer using genetic programming for pipeline optimization.

    TPOT uses genetic programming to automatically design and optimize machine
    learning pipelines. It explores various combinations of preprocessing steps,
    feature engineering, and model selection.

    Features:
        - Genetic programming for pipeline optimization
        - Automatic feature construction
        - Model selection and hyperparameter tuning
        - Export to scikit-learn pipeline
        - Support for classification and regression

    Example:
        >>> optimizer = TPOTOptimizer(time_limit=300, task_type='classification')
        >>> optimizer.fit(X_train, y_train)
        >>> predictions = optimizer.predict(X_test)
        >>> optimizer.export_pipeline('best_pipeline.py')
    """

    def __init__(
        self,
        time_limit: int = 300,
        task_type: str = "classification",
        n_jobs: int = -1,
        random_state: int = 42,
        verbose: int = 1,
        population_size: int = 100,
        generations: int = 100,
        cv: int = 5,
        **kwargs: Any
    ):
        """Initialize the TPOT optimizer.

        Args:
            time_limit: Total time limit in seconds (default: 300)
            task_type: 'classification' or 'regression'
            n_jobs: Number of parallel jobs (-1 for all cores)
            random_state: Random seed for reproducibility
            verbose: Verbosity level (0=silent, 1=info, 2=debug)
            population_size: Number of individuals in genetic programming population
            generations: Number of generations to run (if time permits)
            cv: Number of cross-validation folds
            **kwargs: Additional TPOT parameters

        Raises:
            AutoMLNotAvailableError: If TPOT is not installed
            ValueError: If task_type is invalid
        """
        if not TPOT_AVAILABLE:
            raise AutoMLNotAvailableError(
                "TPOT",
                "tpot"
            )

        super().__init__(
            time_limit=time_limit,
            task_type=task_type,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            **kwargs
        )

        self.population_size = population_size
        self.generations = generations
        self.cv = cv

        # Calculate generations based on time limit (rough estimate)
        if "max_time_mins" not in kwargs:
            max_time_mins = max(1, time_limit // 60)
        else:
            max_time_mins = kwargs.pop("max_time_mins")

        # Configure verbosity
        verbosity_map = {0: 0, 1: 2, 2: 3}
        tpot_verbosity = verbosity_map.get(verbose, 2)

        # Configure TPOT
        common_params = {
            "generations": generations,
            "population_size": population_size,
            "cv": cv,
            "random_state": random_state,
            "verbosity": tpot_verbosity,
            "n_jobs": n_jobs,
            "max_time_mins": max_time_mins,
            "max_eval_time_mins": max(1, max_time_mins // 10),
            "early_stop": 5,  # Stop if no improvement for 5 generations
            **kwargs
        }

        # Create the appropriate model
        if task_type == "classification":
            self.model = TPOTClassifier(**common_params)
        else:
            self.model = TPOTRegressor(**common_params)

    def fit(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        **fit_params: Any
    ) -> "TPOTOptimizer":
        """Train the TPOT model using genetic programming.

        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
            **fit_params: Additional parameters (e.g., sample_weight)

        Returns:
            self: The fitted optimizer

        Raises:
            ValueError: If input data is invalid
            RuntimeError: If training fails
        """
        if self.verbose:
            print(f"Starting TPOT {self.task_type} optimization...")
            print(f"Time limit: {self.time_limit}s")
            print(f"Population size: {self.population_size}")
            print(f"Max generations: {self.generations}")

        # Convert to numpy arrays if needed (TPOT prefers numpy)
        if isinstance(X, pd.DataFrame):
            X_train = X.values
        else:
            X_train = X

        if isinstance(y, pd.Series):
            y_train = y.values
        else:
            y_train = y

        # Validate input
        if len(X_train) != len(y_train):
            raise ValueError(
                f"X and y must have the same length: {len(X_train)} vs {len(y_train)}"
            )

        # Train the model
        start_time = time.time()

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                self.model.fit(X_train, y_train, **fit_params)

            self._training_time = time.time() - start_time
            self.is_fitted = True

            # Store best score
            if hasattr(self.model, 'fitted_pipeline_'):
                # Get best CV score
                self._best_score = self.model.score(X_train, y_train)

            if self.verbose:
                print(f"Training completed in {self._training_time:.2f}s")
                if self._best_score:
                    print(f"Best pipeline score: {self._best_score:.4f}")
                if hasattr(self.model, 'evaluated_individuals_'):
                    print(f"Evaluated {len(self.model.evaluated_individuals_)} individuals")

        except Exception as e:
            raise RuntimeError(f"TPOT training failed: {str(e)}")

        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions on new data.

        Args:
            X: Features to predict on (n_samples, n_features)

        Returns:
            predictions: Predicted values or class labels

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions")

        # Convert to numpy if needed
        if isinstance(X, pd.DataFrame):
            X_test = X.values
        else:
            X_test = X

        return self.model.predict(X_test)

    def _predict_proba_impl(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Implementation of predict_proba for classification tasks.

        Args:
            X: Features to predict on (n_samples, n_features)

        Returns:
            probabilities: Class probabilities (n_samples, n_classes)
        """
        # Convert to numpy if needed
        if isinstance(X, pd.DataFrame):
            X_test = X.values
        else:
            X_test = X

        return self.model.predict_proba(X_test)

    def get_pipeline(self) -> Any:
        """Get the best pipeline found by TPOT.

        Returns:
            pipeline: The best scikit-learn pipeline

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting pipeline")

        return self.model.fitted_pipeline_

    def get_config(self) -> Dict[str, Any]:
        """Get the configuration of the best pipeline.

        Returns:
            config: Dictionary containing pipeline configuration and metadata

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting config")

        config = {
            "library": "TPOT",
            "task_type": self.task_type,
            "time_limit": self.time_limit,
            "training_time": self._training_time,
            "best_score": self._best_score,
            "population_size": self.population_size,
            "generations": self.generations,
            "cv": self.cv,
            "n_jobs": self.n_jobs,
            "random_state": self.random_state,
        }

        # Add pipeline details
        if hasattr(self.model, 'fitted_pipeline_'):
            config["pipeline"] = str(self.model.fitted_pipeline_)

        # Add evaluation statistics
        if hasattr(self.model, 'evaluated_individuals_'):
            config["n_evaluated_individuals"] = len(self.model.evaluated_individuals_)

        if hasattr(self.model, 'pareto_front_fitted_pipelines_'):
            config["pareto_front_size"] = len(
                self.model.pareto_front_fitted_pipelines_
            )

        return config

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores from the best pipeline.

        Returns:
            importance: Dictionary mapping feature indices to importance scores,
                       or None if not available

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting feature importance")

        try:
            pipeline = self.model.fitted_pipeline_

            # Try to get feature importance from the final estimator
            if hasattr(pipeline, 'steps'):
                # Get the last step (the estimator)
                final_estimator = pipeline.steps[-1][1]

                if hasattr(final_estimator, 'feature_importances_'):
                    importances = final_estimator.feature_importances_
                    return {f"feature_{i}": float(imp) for i, imp in enumerate(importances)}

                elif hasattr(final_estimator, 'coef_'):
                    # For linear models
                    coef = final_estimator.coef_
                    if len(coef.shape) > 1:
                        # Multi-class classification
                        importances = np.abs(coef).mean(axis=0)
                    else:
                        importances = np.abs(coef)
                    return {f"feature_{i}": float(imp) for i, imp in enumerate(importances)}

        except Exception as e:
            if self.verbose > 1:
                print(f"Could not extract feature importance: {e}")

        return None

    def export_pipeline(self, output_file: str) -> None:
        """Export the best pipeline to a Python file.

        Args:
            output_file: Path to the output Python file

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before exporting pipeline")

        try:
            self.model.export(output_file)
            if self.verbose:
                print(f"Pipeline exported to: {output_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to export pipeline: {str(e)}")

    def get_pareto_front(self) -> Optional[Dict[str, Any]]:
        """Get the Pareto front of pipelines (trade-off between accuracy and complexity).

        Returns:
            pareto_front: Dictionary with Pareto-optimal pipelines and their scores,
                         or None if not available

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting Pareto front")

        if not hasattr(self.model, 'pareto_front_fitted_pipelines_'):
            return None

        pareto_front = {
            "pipelines": [],
            "scores": []
        }

        try:
            for pipeline_key in self.model.pareto_front_fitted_pipelines_:
                pipeline = self.model.pareto_front_fitted_pipelines_[pipeline_key]
                score = self.model.evaluated_individuals_.get(pipeline_key, {}).get('internal_cv_score', None)

                pareto_front["pipelines"].append(str(pipeline))
                pareto_front["scores"].append(score)

            return pareto_front

        except Exception as e:
            if self.verbose > 1:
                print(f"Could not extract Pareto front: {e}")
            return None

    def get_evaluated_pipelines(self) -> pd.DataFrame:
        """Get all evaluated pipelines and their scores.

        Returns:
            pipelines: DataFrame with all evaluated pipelines and their scores

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting evaluated pipelines")

        if not hasattr(self.model, 'evaluated_individuals_'):
            return pd.DataFrame()

        pipelines_data = []
        for pipeline_str, metrics in self.model.evaluated_individuals_.items():
            pipelines_data.append({
                "pipeline": pipeline_str,
                "cv_score": metrics.get('internal_cv_score', None),
                "operator_count": metrics.get('operator_count', None),
            })

        df = pd.DataFrame(pipelines_data)
        if not df.empty and 'cv_score' in df.columns:
            df = df.sort_values('cv_score', ascending=False)

        return df
