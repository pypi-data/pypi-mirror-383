"""Auto-sklearn wrapper for automated machine learning.

This module provides a wrapper around Auto-sklearn, an automated machine learning
toolkit that leverages Bayesian optimization, meta-learning, and ensemble construction.
"""

import time
import warnings
from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd

from .base import AutoMLNotAvailableError, BaseAutoMLWrapper

try:
    import autosklearn.classification
    import autosklearn.regression
    from autosklearn.metrics import accuracy, f1, mean_squared_error, r2
    AUTOSKLEARN_AVAILABLE = True
except ImportError:
    AUTOSKLEARN_AVAILABLE = False


class AutoSklearnOptimizer(BaseAutoMLWrapper):
    """Auto-sklearn AutoML optimizer with Bayesian optimization and meta-learning.

    Auto-sklearn automatically searches for the right learning algorithm and
    optimizes its hyperparameters. It uses Bayesian optimization, meta-learning,
    and ensemble construction to find the best model.

    Features:
        - Automatic preprocessing (imputation, encoding, scaling)
        - Bayesian hyperparameter optimization
        - Meta-learning from previous experiments
        - Automatic ensemble building
        - Support for classification and regression

    Example:
        >>> optimizer = AutoSklearnOptimizer(time_limit=300, task_type='classification')
        >>> optimizer.fit(X_train, y_train)
        >>> predictions = optimizer.predict(X_test)
        >>> pipeline = optimizer.get_pipeline()
    """

    def __init__(
        self,
        time_limit: int = 300,
        task_type: str = "classification",
        n_jobs: int = -1,
        random_state: int = 42,
        verbose: int = 1,
        ensemble_size: int = 50,
        memory_limit: int = 3072,
        **kwargs: Any
    ):
        """Initialize the Auto-sklearn optimizer.

        Args:
            time_limit: Total time limit in seconds (default: 300)
            task_type: 'classification' or 'regression'
            n_jobs: Number of parallel jobs (-1 for all cores)
            random_state: Random seed for reproducibility
            verbose: Verbosity level (0=silent, 1=info, 2=debug)
            ensemble_size: Number of models to consider for ensemble (default: 50)
            memory_limit: Memory limit in MB (default: 3072 = 3GB)
            **kwargs: Additional Auto-sklearn parameters

        Raises:
            AutoMLNotAvailableError: If Auto-sklearn is not installed
            ValueError: If task_type is invalid
        """
        if not AUTOSKLEARN_AVAILABLE:
            raise AutoMLNotAvailableError(
                "Auto-sklearn",
                "auto-sklearn"
            )

        super().__init__(
            time_limit=time_limit,
            task_type=task_type,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            **kwargs
        )

        self.ensemble_size = ensemble_size
        self.memory_limit = memory_limit

        # Split time between model search and ensemble building
        per_run_time_limit = max(30, time_limit // 10)

        # Configure Auto-sklearn
        common_params = {
            "time_left_for_this_task": time_limit,
            "per_run_time_limit": per_run_time_limit,
            "ensemble_size": ensemble_size,
            "ensemble_nbest": ensemble_size,
            "memory_limit": memory_limit,
            "seed": random_state,
            "n_jobs": n_jobs if n_jobs > 0 else None,
            "disable_evaluator_output": verbose == 0,
            **kwargs
        }

        # Create the appropriate model
        if task_type == "classification":
            self.model = autosklearn.classification.AutoSklearnClassifier(**common_params)
        else:
            self.model = autosklearn.regression.AutoSklearnRegressor(**common_params)

    def fit(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        **fit_params: Any
    ) -> "AutoSklearnOptimizer":
        """Train the Auto-sklearn model.

        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
            **fit_params: Additional parameters (e.g., dataset_name)

        Returns:
            self: The fitted optimizer

        Raises:
            ValueError: If input data is invalid
            RuntimeError: If training fails
        """
        if self.verbose:
            print(f"Starting Auto-sklearn {self.task_type} optimization...")
            print(f"Time limit: {self.time_limit}s")
            print(f"Ensemble size: {self.ensemble_size}")

        # Convert to numpy arrays if needed
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

            # Get best score from the model
            if hasattr(self.model, 'cv_results_'):
                # Get the best score from cross-validation
                cv_results = self.model.cv_results_
                if 'mean_test_score' in cv_results:
                    self._best_score = float(np.max(cv_results['mean_test_score']))

            if self.verbose:
                print(f"Training completed in {self._training_time:.2f}s")
                if self._best_score:
                    print(f"Best CV score: {self._best_score:.4f}")
                print(f"Ensemble size: {len(self.model.get_models_with_weights())}")

        except Exception as e:
            raise RuntimeError(f"Auto-sklearn training failed: {str(e)}")

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
        """Get the best pipeline found by Auto-sklearn.

        Returns:
            pipeline: The best trained pipeline

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting pipeline")

        # Get the ensemble's best model
        models = self.model.get_models_with_weights()
        if models:
            # Return the model with highest weight
            best_model = max(models, key=lambda x: x[0])
            return best_model[1]

        return self.model

    def get_config(self) -> Dict[str, Any]:
        """Get the configuration of the best model.

        Returns:
            config: Dictionary containing model configuration and metadata

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting config")

        config = {
            "library": "auto-sklearn",
            "task_type": self.task_type,
            "time_limit": self.time_limit,
            "training_time": self._training_time,
            "best_score": self._best_score,
            "ensemble_size": self.ensemble_size,
            "memory_limit": self.memory_limit,
            "n_jobs": self.n_jobs,
            "random_state": self.random_state,
        }

        # Get ensemble information
        try:
            models_with_weights = self.model.get_models_with_weights()
            config["n_ensemble_members"] = len(models_with_weights)
            config["ensemble_weights"] = [float(w) for w, _ in models_with_weights]
        except:
            pass

        # Get model statistics
        try:
            sprint_statistics = self.model.sprint_statistics()
            config["statistics"] = sprint_statistics
        except:
            pass

        return config

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores from the best model.

        Returns:
            importance: Dictionary mapping feature indices to importance scores,
                       or None if not available

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting feature importance")

        try:
            # Get the best model from ensemble
            models = self.model.get_models_with_weights()
            if not models:
                return None

            # Get the highest weighted model
            best_weight, best_model = max(models, key=lambda x: x[0])

            # Try to extract feature importance
            if hasattr(best_model, 'feature_importances_'):
                importances = best_model.feature_importances_
                return {f"feature_{i}": float(imp) for i, imp in enumerate(importances)}

        except Exception as e:
            if self.verbose > 1:
                print(f"Could not extract feature importance: {e}")

        return None

    def get_leaderboard(self) -> pd.DataFrame:
        """Get leaderboard of all evaluated models.

        Returns:
            leaderboard: DataFrame with model rankings and scores

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting leaderboard")

        models_with_weights = self.model.get_models_with_weights()

        leaderboard_data = []
        for i, (weight, model) in enumerate(models_with_weights):
            leaderboard_data.append({
                "rank": i + 1,
                "weight": weight,
                "model": str(model),
            })

        return pd.DataFrame(leaderboard_data)

    def refit(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series]
    ) -> "AutoSklearnOptimizer":
        """Refit the ensemble on new data.

        This refits the existing ensemble on new data without re-running
        the optimization process.

        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)

        Returns:
            self: The refitted optimizer

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before refitting")

        # Convert to numpy arrays if needed
        if isinstance(X, pd.DataFrame):
            X_train = X.values
        else:
            X_train = X

        if isinstance(y, pd.Series):
            y_train = y.values
        else:
            y_train = y

        self.model.refit(X_train, y_train)

        return self
