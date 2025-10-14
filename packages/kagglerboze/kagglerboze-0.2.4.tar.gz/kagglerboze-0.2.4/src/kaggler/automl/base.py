"""Base AutoML wrapper interface.

This module defines the abstract base class for all AutoML wrappers,
providing a unified API across different AutoML libraries.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd


class BaseAutoMLWrapper(ABC):
    """Abstract base class for AutoML wrappers.

    This class defines the common interface that all AutoML wrappers must implement.
    It provides a unified API for training, prediction, and model management across
    different AutoML libraries (Auto-sklearn, TPOT, H2O AutoML).

    Attributes:
        time_limit: Maximum time in seconds for training
        task_type: Type of ML task ('classification' or 'regression')
        n_jobs: Number of parallel jobs (-1 for all cores)
        random_state: Random seed for reproducibility
        verbose: Verbosity level (0=silent, 1=info, 2=debug)
        model: The trained model instance
        is_fitted: Whether the model has been trained
    """

    def __init__(
        self,
        time_limit: int = 300,
        task_type: str = "classification",
        n_jobs: int = -1,
        random_state: int = 42,
        verbose: int = 1,
        **kwargs: Any
    ):
        """Initialize the AutoML wrapper.

        Args:
            time_limit: Maximum training time in seconds (default: 300 = 5 minutes)
            task_type: 'classification' or 'regression'
            n_jobs: Number of parallel jobs, -1 uses all cores
            random_state: Random seed for reproducibility
            verbose: Verbosity level (0=silent, 1=info, 2=debug)
            **kwargs: Additional library-specific parameters

        Raises:
            ValueError: If task_type is not 'classification' or 'regression'
        """
        if task_type not in ["classification", "regression"]:
            raise ValueError(f"task_type must be 'classification' or 'regression', got '{task_type}'")

        self.time_limit = time_limit
        self.task_type = task_type
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.verbose = verbose
        self.kwargs = kwargs
        self.model: Optional[Any] = None
        self.is_fitted = False
        self._training_time: Optional[float] = None
        self._best_score: Optional[float] = None

    @abstractmethod
    def fit(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        **fit_params: Any
    ) -> "BaseAutoMLWrapper":
        """Train the AutoML model on the provided data.

        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
            **fit_params: Additional fitting parameters

        Returns:
            self: The fitted AutoML wrapper

        Raises:
            ValueError: If input data is invalid
            RuntimeError: If training fails
        """
        pass

    @abstractmethod
    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions on new data.

        Args:
            X: Features to predict on (n_samples, n_features)

        Returns:
            predictions: Predicted values or class labels (n_samples,)

        Raises:
            RuntimeError: If model is not fitted
            ValueError: If input data is invalid
        """
        pass

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict class probabilities for classification tasks.

        Args:
            X: Features to predict on (n_samples, n_features)

        Returns:
            probabilities: Class probabilities (n_samples, n_classes)

        Raises:
            RuntimeError: If model is not fitted or task is not classification
            ValueError: If input data is invalid
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions")

        if self.task_type != "classification":
            raise RuntimeError("predict_proba is only available for classification tasks")

        return self._predict_proba_impl(X)

    @abstractmethod
    def _predict_proba_impl(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Implementation of predict_proba. Must be overridden by subclasses."""
        pass

    @abstractmethod
    def get_pipeline(self) -> Any:
        """Get the best pipeline/model found during training.

        Returns:
            pipeline: The best trained pipeline or model

        Raises:
            RuntimeError: If model is not fitted
        """
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get the configuration of the best model.

        Returns:
            config: Dictionary containing model configuration and metadata

        Raises:
            RuntimeError: If model is not fitted
        """
        pass

    def get_training_time(self) -> Optional[float]:
        """Get the total training time in seconds.

        Returns:
            training_time: Training time in seconds, or None if not fitted
        """
        return self._training_time

    def get_best_score(self) -> Optional[float]:
        """Get the best score achieved during training.

        Returns:
            best_score: Best cross-validation or holdout score, or None if not fitted
        """
        return self._best_score

    @abstractmethod
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores.

        Returns:
            importance: Dictionary mapping feature names to importance scores,
                       or None if not available

        Raises:
            RuntimeError: If model is not fitted
        """
        pass

    def score(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series]
    ) -> float:
        """Compute the score on test data.

        Args:
            X: Test features (n_samples, n_features)
            y: True labels (n_samples,)

        Returns:
            score: Accuracy for classification, R² for regression

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before scoring")

        predictions = self.predict(X)

        if self.task_type == "classification":
            from sklearn.metrics import accuracy_score
            return accuracy_score(y, predictions)
        else:
            from sklearn.metrics import r2_score
            return r2_score(y, predictions)

    def __repr__(self) -> str:
        """String representation of the AutoML wrapper."""
        status = "fitted" if self.is_fitted else "not fitted"
        return (
            f"{self.__class__.__name__}("
            f"task_type='{self.task_type}', "
            f"time_limit={self.time_limit}s, "
            f"status={status})"
        )


class AutoMLNotAvailableError(Exception):
    """Raised when an AutoML library is not installed or available."""

    def __init__(self, library_name: str, install_command: str):
        """Initialize the error.

        Args:
            library_name: Name of the missing library
            install_command: Command to install the library
        """
        self.library_name = library_name
        self.install_command = install_command
        message = (
            f"{library_name} is not installed. "
            f"Install it with: pip install {install_command}"
        )
        super().__init__(message)
