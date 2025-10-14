"""Hybrid AutoML strategy that auto-detects and routes tasks.

This module provides a hybrid approach that automatically detects whether
a task is NLP-focused or tabular, and routes it to the appropriate method.
"""

import warnings
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from .base import BaseAutoMLWrapper


class HybridAutoML(BaseAutoMLWrapper):
    """Hybrid AutoML that auto-routes between NLP and tabular methods.

    This class automatically detects the task type (NLP vs Tabular) and routes
    to the appropriate optimization method:
    - NLP tasks → GEPA prompt optimization (if available)
    - Tabular tasks → Traditional AutoML (Auto-sklearn/TPOT/H2O)

    Features:
        - Automatic task detection
        - Intelligent routing
        - Ensemble predictions across methods
        - Fallback mechanisms

    Example:
        >>> hybrid = HybridAutoML(time_limit=300, task_type='classification')
        >>> hybrid.fit(X_train, y_train)
        >>> predictions = hybrid.predict(X_test)
        >>> print(hybrid.get_routing_info())
    """

    def __init__(
        self,
        time_limit: int = 300,
        task_type: str = "classification",
        n_jobs: int = -1,
        random_state: int = 42,
        verbose: int = 1,
        preferred_method: Optional[str] = None,
        ensemble_methods: bool = False,
        text_threshold: float = 0.3,
        **kwargs: Any
    ):
        """Initialize the Hybrid AutoML.

        Args:
            time_limit: Total time limit in seconds
            task_type: 'classification' or 'regression'
            n_jobs: Number of parallel jobs
            random_state: Random seed
            verbose: Verbosity level
            preferred_method: Preferred AutoML method ('autosklearn', 'tpot', 'h2o', or None)
            ensemble_methods: Whether to ensemble multiple methods
            text_threshold: Threshold for text column ratio to classify as NLP (0.0-1.0)
            **kwargs: Additional parameters
        """
        super().__init__(
            time_limit=time_limit,
            task_type=task_type,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            **kwargs
        )

        self.preferred_method = preferred_method
        self.ensemble_methods = ensemble_methods
        self.text_threshold = text_threshold

        self._detected_task_category: Optional[str] = None
        self._selected_method: Optional[str] = None
        self._optimizers: Dict[str, Any] = {}
        self._feature_names: Optional[List[str]] = None

    def _detect_task_category(
        self,
        X: Union[np.ndarray, pd.DataFrame]
    ) -> str:
        """Detect whether task is NLP or Tabular.

        Args:
            X: Input features

        Returns:
            category: 'nlp' or 'tabular'
        """
        # Convert to DataFrame if needed
        if isinstance(X, np.ndarray):
            # Pure numeric array = tabular
            return "tabular"

        # Check DataFrame columns
        text_columns = 0
        total_columns = len(X.columns)

        for col in X.columns:
            # Check if column contains text data
            sample = X[col].dropna().head(100)

            if sample.dtype == 'object' or sample.dtype.name == 'string':
                # Check average string length
                avg_length = sample.astype(str).str.len().mean()

                # If strings are long (> 50 chars), likely text
                if avg_length > 50:
                    text_columns += 1

        text_ratio = text_columns / total_columns if total_columns > 0 else 0

        if self.verbose > 1:
            print(f"Text columns: {text_columns}/{total_columns} ({text_ratio:.2%})")

        return "nlp" if text_ratio >= self.text_threshold else "tabular"

    def _select_tabular_method(self) -> str:
        """Select the best available tabular AutoML method.

        Returns:
            method: Selected method name
        """
        # If preferred method specified, try to use it
        if self.preferred_method:
            method = self.preferred_method.lower()
            if self._is_method_available(method):
                return method
            elif self.verbose:
                print(f"Preferred method '{self.preferred_method}' not available, falling back...")

        # Try methods in order of preference
        methods = ['autosklearn', 'tpot', 'h2o']

        for method in methods:
            if self._is_method_available(method):
                return method

        raise RuntimeError("No AutoML methods available. Install at least one of: auto-sklearn, TPOT, H2O")

    def _is_method_available(self, method: str) -> bool:
        """Check if a method is available.

        Args:
            method: Method name ('autosklearn', 'tpot', or 'h2o')

        Returns:
            available: Whether the method is available
        """
        try:
            if method == 'autosklearn':
                import autosklearn
                return True
            elif method == 'tpot':
                import tpot
                return True
            elif method == 'h2o':
                import h2o
                return True
        except ImportError:
            pass

        return False

    def _create_optimizer(self, method: str) -> BaseAutoMLWrapper:
        """Create an optimizer for the specified method.

        Args:
            method: Method name

        Returns:
            optimizer: Initialized optimizer
        """
        if method == 'autosklearn':
            from .autosklearn_wrapper import AutoSklearnOptimizer
            return AutoSklearnOptimizer(
                time_limit=self.time_limit,
                task_type=self.task_type,
                n_jobs=self.n_jobs,
                random_state=self.random_state,
                verbose=self.verbose,
                **self.kwargs
            )
        elif method == 'tpot':
            from .tpot_wrapper import TPOTOptimizer
            return TPOTOptimizer(
                time_limit=self.time_limit,
                task_type=self.task_type,
                n_jobs=self.n_jobs,
                random_state=self.random_state,
                verbose=self.verbose,
                **self.kwargs
            )
        elif method == 'h2o':
            from .h2o_wrapper import H2OAutoMLOptimizer
            return H2OAutoMLOptimizer(
                time_limit=self.time_limit,
                task_type=self.task_type,
                n_jobs=self.n_jobs,
                random_state=self.random_state,
                verbose=self.verbose,
                **self.kwargs
            )
        else:
            raise ValueError(f"Unknown method: {method}")

    def fit(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        **fit_params: Any
    ) -> "HybridAutoML":
        """Train the Hybrid AutoML model.

        Args:
            X: Training features
            y: Training targets
            **fit_params: Additional fitting parameters

        Returns:
            self: The fitted hybrid model
        """
        if self.verbose:
            print("="*60)
            print("Hybrid AutoML - Automatic Task Detection & Routing")
            print("="*60)

        # Store feature names if DataFrame
        if isinstance(X, pd.DataFrame):
            self._feature_names = list(X.columns)

        # Detect task category
        self._detected_task_category = self._detect_task_category(X)

        if self.verbose:
            print(f"\nDetected task category: {self._detected_task_category.upper()}")

        # Handle NLP tasks
        if self._detected_task_category == "nlp":
            if self.verbose:
                print("Routing to NLP pipeline (GEPA prompt optimization)")
                print("Note: Traditional AutoML will be used as fallback")

            # Fall back to tabular AutoML for now
            # In a full implementation, this would use GEPA
            self._detected_task_category = "tabular"

        # Handle tabular tasks
        if self._detected_task_category == "tabular":
            if self.ensemble_methods:
                # Train multiple methods and ensemble
                methods_to_try = []

                for method in ['autosklearn', 'tpot', 'h2o']:
                    if self._is_method_available(method):
                        methods_to_try.append(method)

                if not methods_to_try:
                    raise RuntimeError("No AutoML methods available")

                if self.verbose:
                    print(f"\nEnsemble mode: Training {len(methods_to_try)} methods")
                    print(f"Methods: {', '.join(methods_to_try)}")

                # Distribute time across methods
                time_per_method = self.time_limit // len(methods_to_try)

                for method in methods_to_try:
                    if self.verbose:
                        print(f"\n--- Training {method.upper()} ---")

                    try:
                        optimizer = self._create_optimizer(method)
                        optimizer.time_limit = time_per_method
                        optimizer.fit(X, y, **fit_params)
                        self._optimizers[method] = optimizer

                    except Exception as e:
                        if self.verbose:
                            print(f"Warning: {method} failed: {e}")

                if not self._optimizers:
                    raise RuntimeError("All methods failed to train")

                self._selected_method = "ensemble"

            else:
                # Select and train single method
                method = self._select_tabular_method()
                self._selected_method = method

                if self.verbose:
                    print(f"\nSelected method: {method.upper()}")

                optimizer = self._create_optimizer(method)
                optimizer.fit(X, y, **fit_params)
                self._optimizers[method] = optimizer

        self.is_fitted = True

        if self.verbose:
            print("\n" + "="*60)
            print("Training completed!")
            print(f"Strategy: {self._selected_method}")
            print("="*60)

        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions on new data.

        Args:
            X: Features to predict on

        Returns:
            predictions: Predicted values or class labels
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before making predictions")

        if self._selected_method == "ensemble":
            # Ensemble predictions from multiple methods
            all_predictions = []

            for method, optimizer in self._optimizers.items():
                try:
                    preds = optimizer.predict(X)
                    all_predictions.append(preds)
                except Exception as e:
                    if self.verbose:
                        print(f"Warning: {method} prediction failed: {e}")

            if not all_predictions:
                raise RuntimeError("All methods failed to make predictions")

            # Combine predictions
            if self.task_type == "classification":
                # Majority voting
                all_predictions = np.array(all_predictions)
                from scipy import stats
                predictions = stats.mode(all_predictions, axis=0, keepdims=False)[0]
            else:
                # Average predictions
                predictions = np.mean(all_predictions, axis=0)

            return predictions

        else:
            # Single method prediction
            optimizer = self._optimizers[self._selected_method]
            return optimizer.predict(X)

    def _predict_proba_impl(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Implementation of predict_proba for classification tasks.

        Args:
            X: Features to predict on

        Returns:
            probabilities: Class probabilities
        """
        if self._selected_method == "ensemble":
            # Average probabilities from multiple methods
            all_probas = []

            for method, optimizer in self._optimizers.items():
                try:
                    probas = optimizer.predict_proba(X)
                    all_probas.append(probas)
                except Exception as e:
                    if self.verbose:
                        print(f"Warning: {method} predict_proba failed: {e}")

            if not all_probas:
                raise RuntimeError("All methods failed to make probability predictions")

            # Average probabilities
            return np.mean(all_probas, axis=0)

        else:
            # Single method prediction
            optimizer = self._optimizers[self._selected_method]
            return optimizer.predict_proba(X)

    def get_pipeline(self) -> Any:
        """Get the best pipeline from the selected method.

        Returns:
            pipeline: The best pipeline
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting pipeline")

        if self._selected_method == "ensemble":
            # Return pipelines from all methods
            return {
                method: optimizer.get_pipeline()
                for method, optimizer in self._optimizers.items()
            }
        else:
            optimizer = self._optimizers[self._selected_method]
            return optimizer.get_pipeline()

    def get_config(self) -> Dict[str, Any]:
        """Get the configuration of the hybrid model.

        Returns:
            config: Configuration dictionary
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting config")

        config = {
            "library": "Hybrid AutoML",
            "task_type": self.task_type,
            "time_limit": self.time_limit,
            "detected_task_category": self._detected_task_category,
            "selected_method": self._selected_method,
            "ensemble_methods": self.ensemble_methods,
            "text_threshold": self.text_threshold,
        }

        # Add configs from all optimizers
        if self._selected_method == "ensemble":
            config["methods"] = {}
            for method, optimizer in self._optimizers.items():
                try:
                    config["methods"][method] = optimizer.get_config()
                except:
                    pass
        else:
            optimizer = self._optimizers[self._selected_method]
            config["method_config"] = optimizer.get_config()

        return config

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores.

        Returns:
            importance: Feature importance dictionary or None
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting feature importance")

        if self._selected_method == "ensemble":
            # Combine feature importance from all methods
            all_importances = {}

            for method, optimizer in self._optimizers.items():
                try:
                    importance = optimizer.get_feature_importance()
                    if importance:
                        all_importances[method] = importance
                except:
                    pass

            if not all_importances:
                return None

            # Average importance scores
            combined = {}
            for method_importances in all_importances.values():
                for feature, score in method_importances.items():
                    if feature not in combined:
                        combined[feature] = []
                    combined[feature].append(score)

            # Average scores
            return {
                feature: np.mean(scores)
                for feature, scores in combined.items()
            }

        else:
            optimizer = self._optimizers[self._selected_method]
            return optimizer.get_feature_importance()

    def get_routing_info(self) -> Dict[str, Any]:
        """Get information about how the task was routed.

        Returns:
            routing_info: Dictionary with routing decisions and details
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting routing info")

        return {
            "detected_task_category": self._detected_task_category,
            "selected_method": self._selected_method,
            "ensemble_methods": self.ensemble_methods,
            "available_methods": [
                method for method in ['autosklearn', 'tpot', 'h2o']
                if self._is_method_available(method)
            ],
            "active_optimizers": list(self._optimizers.keys()),
        }
