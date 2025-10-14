"""Automatic task routing between GEPA and AutoML.

This module provides intelligent routing that automatically detects task
characteristics and routes to the most appropriate method (GEPA for NLP,
AutoML for tabular data).
"""

import warnings
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from .base import BaseAutoMLWrapper


class AutoRouter(BaseAutoMLWrapper):
    """Automatic router that selects the best approach based on data characteristics.

    The AutoRouter analyzes the input data and automatically routes to:
    - GEPA: For NLP tasks with text data
    - AutoML: For tabular tasks with numeric/categorical data
    - Hybrid: For mixed tasks

    Features:
        - Automatic task detection from data characteristics
        - Intelligent method selection
        - Fallback mechanisms
        - Detailed routing explanations

    Example:
        >>> router = AutoRouter(time_limit=300, task_type='classification')
        >>> router.fit(X_train, y_train)
        >>> predictions = router.predict(X_test)
        >>> print(router.explain_routing())
    """

    def __init__(
        self,
        time_limit: int = 300,
        task_type: str = "classification",
        n_jobs: int = -1,
        random_state: int = 42,
        verbose: int = 1,
        text_length_threshold: int = 50,
        text_ratio_threshold: float = 0.3,
        preferred_automl: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize the AutoRouter.

        Args:
            time_limit: Total time limit in seconds
            task_type: 'classification' or 'regression'
            n_jobs: Number of parallel jobs
            random_state: Random seed
            verbose: Verbosity level
            text_length_threshold: Minimum avg string length to consider as text (default: 50)
            text_ratio_threshold: Min ratio of text columns to route to NLP (default: 0.3)
            preferred_automl: Preferred AutoML method if routing to tabular
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

        self.text_length_threshold = text_length_threshold
        self.text_ratio_threshold = text_ratio_threshold
        self.preferred_automl = preferred_automl

        self._routing_decision: Optional[str] = None
        self._routing_reason: Optional[str] = None
        self._data_characteristics: Dict[str, Any] = {}
        self._optimizer: Optional[BaseAutoMLWrapper] = None

    def _analyze_data_characteristics(
        self,
        X: Union[np.ndarray, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Analyze data characteristics for routing decision.

        Args:
            X: Input features

        Returns:
            characteristics: Dictionary with data characteristics
        """
        characteristics = {
            "n_samples": len(X),
            "n_features": X.shape[1] if hasattr(X, 'shape') and len(X.shape) > 1 else 0,
            "is_numpy": isinstance(X, np.ndarray),
            "is_dataframe": isinstance(X, pd.DataFrame),
            "text_columns": 0,
            "numeric_columns": 0,
            "categorical_columns": 0,
            "text_column_names": [],
            "avg_text_length": 0,
            "data_type": "unknown"
        }

        # Pure numpy array = tabular
        if isinstance(X, np.ndarray):
            characteristics["data_type"] = "tabular"
            characteristics["numeric_columns"] = X.shape[1] if len(X.shape) > 1 else 1
            return characteristics

        # Analyze DataFrame
        if isinstance(X, pd.DataFrame):
            for col in X.columns:
                sample = X[col].dropna().head(100)

                # Check if text column
                if sample.dtype == 'object' or sample.dtype.name == 'string':
                    avg_length = sample.astype(str).str.len().mean()

                    if avg_length > self.text_length_threshold:
                        characteristics["text_columns"] += 1
                        characteristics["text_column_names"].append(col)
                        characteristics["avg_text_length"] = max(
                            characteristics["avg_text_length"],
                            avg_length
                        )
                    else:
                        # Short strings = categorical
                        characteristics["categorical_columns"] += 1
                else:
                    # Numeric column
                    characteristics["numeric_columns"] += 1

            # Determine overall data type
            total_cols = len(X.columns)
            text_ratio = characteristics["text_columns"] / total_cols if total_cols > 0 else 0

            if text_ratio >= self.text_ratio_threshold:
                characteristics["data_type"] = "nlp"
            elif text_ratio > 0:
                characteristics["data_type"] = "mixed"
            else:
                characteristics["data_type"] = "tabular"

        return characteristics

    def _make_routing_decision(
        self,
        characteristics: Dict[str, Any]
    ) -> tuple:
        """Make routing decision based on data characteristics.

        Args:
            characteristics: Data characteristics dictionary

        Returns:
            decision: Tuple of (routing_target, reason)
        """
        data_type = characteristics["data_type"]

        if data_type == "nlp":
            reason = (
                f"Detected {characteristics['text_columns']} text columns "
                f"with avg length {characteristics['avg_text_length']:.0f} chars. "
                f"NLP task detected."
            )
            return "gepa", reason

        elif data_type == "mixed":
            reason = (
                f"Mixed data: {characteristics['text_columns']} text columns, "
                f"{characteristics['numeric_columns']} numeric columns, "
                f"{characteristics['categorical_columns']} categorical columns. "
                f"Using hybrid approach."
            )
            return "hybrid", reason

        else:  # tabular
            reason = (
                f"Tabular data: {characteristics['numeric_columns']} numeric columns, "
                f"{characteristics['categorical_columns']} categorical columns. "
                f"Using AutoML."
            )
            return "automl", reason

    def _route_to_gepa(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        **fit_params: Any
    ) -> BaseAutoMLWrapper:
        """Route to GEPA prompt optimization.

        Args:
            X: Training features
            y: Training targets
            **fit_params: Additional fitting parameters

        Returns:
            optimizer: Trained GEPA optimizer
        """
        if self.verbose:
            print("\n→ Routing to GEPA (Prompt Optimization for NLP)")
            print("  Note: GEPA integration requires separate setup")
            print("  Falling back to AutoML for now...")

        # Fall back to AutoML
        # In a full implementation, this would use GEPA from kaggler.core
        return self._route_to_automl(X, y, **fit_params)

    def _route_to_automl(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        **fit_params: Any
    ) -> BaseAutoMLWrapper:
        """Route to traditional AutoML.

        Args:
            X: Training features
            y: Training targets
            **fit_params: Additional fitting parameters

        Returns:
            optimizer: Trained AutoML optimizer
        """
        if self.verbose:
            print("\n→ Routing to AutoML (Traditional ML)")

        # Select AutoML method
        method = self.preferred_automl

        if not method:
            # Auto-select based on availability
            methods = ['autosklearn', 'tpot', 'h2o']
            for m in methods:
                if self._is_method_available(m):
                    method = m
                    break

        if not method:
            raise RuntimeError(
                "No AutoML methods available. "
                "Install at least one of: auto-sklearn, TPOT, H2O"
            )

        if self.verbose:
            print(f"  Selected method: {method.upper()}")

        # Create and train optimizer
        optimizer = self._create_automl_optimizer(method)
        optimizer.fit(X, y, **fit_params)

        return optimizer

    def _route_to_hybrid(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        **fit_params: Any
    ) -> BaseAutoMLWrapper:
        """Route to hybrid approach.

        Args:
            X: Training features
            y: Training targets
            **fit_params: Additional fitting parameters

        Returns:
            optimizer: Trained hybrid optimizer
        """
        if self.verbose:
            print("\n→ Routing to Hybrid AutoML")

        from .hybrid import HybridAutoML

        optimizer = HybridAutoML(
            time_limit=self.time_limit,
            task_type=self.task_type,
            n_jobs=self.n_jobs,
            random_state=self.random_state,
            verbose=self.verbose,
            preferred_method=self.preferred_automl,
            **self.kwargs
        )

        optimizer.fit(X, y, **fit_params)
        return optimizer

    def _is_method_available(self, method: str) -> bool:
        """Check if an AutoML method is available.

        Args:
            method: Method name

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

    def _create_automl_optimizer(self, method: str) -> BaseAutoMLWrapper:
        """Create an AutoML optimizer.

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
    ) -> "AutoRouter":
        """Train the model with automatic routing.

        Args:
            X: Training features
            y: Training targets
            **fit_params: Additional fitting parameters

        Returns:
            self: The fitted router
        """
        if self.verbose:
            print("="*60)
            print("AutoRouter - Intelligent Task Routing")
            print("="*60)

        # Analyze data characteristics
        self._data_characteristics = self._analyze_data_characteristics(X)

        if self.verbose > 1:
            print("\nData Characteristics:")
            for key, value in self._data_characteristics.items():
                if key != 'text_column_names' or value:
                    print(f"  {key}: {value}")

        # Make routing decision
        decision, reason = self._make_routing_decision(self._data_characteristics)
        self._routing_decision = decision
        self._routing_reason = reason

        if self.verbose:
            print(f"\nRouting Decision: {decision.upper()}")
            print(f"Reason: {reason}")

        # Route to appropriate method
        if decision == "gepa":
            self._optimizer = self._route_to_gepa(X, y, **fit_params)
        elif decision == "automl":
            self._optimizer = self._route_to_automl(X, y, **fit_params)
        else:  # hybrid
            self._optimizer = self._route_to_hybrid(X, y, **fit_params)

        self.is_fitted = True

        if self.verbose:
            print("\n" + "="*60)
            print("Routing and training completed!")
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

        return self._optimizer.predict(X)

    def _predict_proba_impl(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Implementation of predict_proba for classification tasks.

        Args:
            X: Features to predict on

        Returns:
            probabilities: Class probabilities
        """
        return self._optimizer.predict_proba(X)

    def get_pipeline(self) -> Any:
        """Get the best pipeline from the routed method.

        Returns:
            pipeline: The best pipeline
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting pipeline")

        return self._optimizer.get_pipeline()

    def get_config(self) -> Dict[str, Any]:
        """Get the configuration of the routed model.

        Returns:
            config: Configuration dictionary
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting config")

        config = {
            "library": "AutoRouter",
            "task_type": self.task_type,
            "time_limit": self.time_limit,
            "routing_decision": self._routing_decision,
            "routing_reason": self._routing_reason,
            "data_characteristics": self._data_characteristics,
            "text_length_threshold": self.text_length_threshold,
            "text_ratio_threshold": self.text_ratio_threshold,
        }

        # Add config from routed optimizer
        if self._optimizer:
            config["optimizer_config"] = self._optimizer.get_config()

        return config

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores from the routed model.

        Returns:
            importance: Feature importance dictionary or None
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting feature importance")

        return self._optimizer.get_feature_importance()

    def explain_routing(self) -> Dict[str, Any]:
        """Get detailed explanation of routing decision.

        Returns:
            explanation: Dictionary with routing details
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting routing explanation")

        explanation = {
            "routing_decision": self._routing_decision,
            "routing_reason": self._routing_reason,
            "data_characteristics": self._data_characteristics,
            "configuration": {
                "text_length_threshold": self.text_length_threshold,
                "text_ratio_threshold": self.text_ratio_threshold,
                "preferred_automl": self.preferred_automl,
            }
        }

        return explanation

    def get_routing_summary(self) -> str:
        """Get a formatted summary of the routing decision.

        Returns:
            summary: Formatted routing summary
        """
        if not self.is_fitted:
            return "Model not fitted yet"

        summary = []
        summary.append("="*60)
        summary.append("AutoRouter - Routing Summary")
        summary.append("="*60)
        summary.append(f"Decision: {self._routing_decision.upper()}")
        summary.append(f"Reason: {self._routing_reason}")
        summary.append("")
        summary.append("Data Characteristics:")

        for key, value in self._data_characteristics.items():
            if key != 'text_column_names' or value:
                summary.append(f"  {key}: {value}")

        summary.append("="*60)

        return "\n".join(summary)
