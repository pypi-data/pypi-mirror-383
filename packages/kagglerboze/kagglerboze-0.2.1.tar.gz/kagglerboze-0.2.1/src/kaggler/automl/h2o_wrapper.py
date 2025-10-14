"""H2O AutoML wrapper for distributed machine learning.

This module provides a wrapper around H2O AutoML, which offers distributed
training, automatic feature engineering, and ensemble stacking with a leaderboard.
"""

import time
import warnings
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from .base import AutoMLNotAvailableError, BaseAutoMLWrapper

try:
    import h2o
    from h2o.automl import H2OAutoML
    H2O_AVAILABLE = True
except ImportError:
    H2O_AVAILABLE = False


class H2OAutoMLOptimizer(BaseAutoMLWrapper):
    """H2O AutoML optimizer with distributed training and ensemble stacking.

    H2O AutoML provides scalable automated machine learning with distributed
    training capabilities. It trains multiple models and builds stacked ensembles
    to achieve high performance.

    Features:
        - Distributed training (can scale to clusters)
        - Automatic feature engineering
        - Stacked ensemble models
        - LeaderBoard with multiple models
        - Support for classification and regression

    Example:
        >>> optimizer = H2OAutoMLOptimizer(time_limit=300, task_type='classification')
        >>> optimizer.fit(X_train, y_train)
        >>> predictions = optimizer.predict(X_test)
        >>> leaderboard = optimizer.get_leaderboard()

    Note:
        H2O requires initialization before use. The wrapper handles this automatically.
    """

    def __init__(
        self,
        time_limit: int = 300,
        task_type: str = "classification",
        n_jobs: int = -1,
        random_state: int = 42,
        verbose: int = 1,
        max_models: int = 20,
        nfolds: int = 5,
        balance_classes: bool = False,
        **kwargs: Any
    ):
        """Initialize the H2O AutoML optimizer.

        Args:
            time_limit: Total time limit in seconds (default: 300)
            task_type: 'classification' or 'regression'
            n_jobs: Number of parallel jobs (-1 for all cores)
            random_state: Random seed for reproducibility
            verbose: Verbosity level (0=silent, 1=info, 2=debug)
            max_models: Maximum number of models to train (default: 20)
            nfolds: Number of cross-validation folds
            balance_classes: Whether to balance classes (for classification)
            **kwargs: Additional H2O AutoML parameters

        Raises:
            AutoMLNotAvailableError: If H2O is not installed
            ValueError: If task_type is invalid
        """
        if not H2O_AVAILABLE:
            raise AutoMLNotAvailableError(
                "H2O AutoML",
                "h2o"
            )

        super().__init__(
            time_limit=time_limit,
            task_type=task_type,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            **kwargs
        )

        self.max_models = max_models
        self.nfolds = nfolds
        self.balance_classes = balance_classes
        self._h2o_initialized = False
        self._train_frame = None
        self._target_column = "target"

        # Initialize H2O
        self._initialize_h2o()

        # Configure H2O AutoML
        max_runtime_secs = time_limit
        max_runtime_secs_per_model = max(30, time_limit // max(1, max_models))

        # Set verbosity
        if verbose == 0:
            h2o.no_progress()

        self.automl_params = {
            "max_runtime_secs": max_runtime_secs,
            "max_models": max_models,
            "seed": random_state,
            "nfolds": nfolds,
            "balance_classes": balance_classes if task_type == "classification" else False,
            "max_runtime_secs_per_model": max_runtime_secs_per_model,
            "keep_cross_validation_predictions": True,
            "keep_cross_validation_models": False,
            **kwargs
        }

    def _initialize_h2o(self) -> None:
        """Initialize H2O cluster."""
        if self._h2o_initialized:
            return

        try:
            # Check if H2O is already running
            try:
                h2o.cluster().shutdown()
                time.sleep(1)
            except:
                pass

            # Initialize with appropriate settings
            nthreads = self.n_jobs if self.n_jobs > 0 else -1

            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                h2o.init(
                    nthreads=nthreads,
                    max_mem_size="4G",
                    strict_version_check=False
                )

            self._h2o_initialized = True

            if self.verbose:
                print("H2O cluster initialized")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize H2O: {str(e)}")

    def fit(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        **fit_params: Any
    ) -> "H2OAutoMLOptimizer":
        """Train the H2O AutoML model.

        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
            **fit_params: Additional parameters (e.g., validation_frame)

        Returns:
            self: The fitted optimizer

        Raises:
            ValueError: If input data is invalid
            RuntimeError: If training fails
        """
        if self.verbose:
            print(f"Starting H2O AutoML {self.task_type} optimization...")
            print(f"Time limit: {self.time_limit}s")
            print(f"Max models: {self.max_models}")

        # Convert to DataFrame if needed
        if isinstance(X, np.ndarray):
            X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
        else:
            X_df = X.copy()

        if isinstance(y, np.ndarray):
            y_series = pd.Series(y, name=self._target_column)
        else:
            y_series = y.copy()
            y_series.name = self._target_column

        # Combine features and target
        train_df = X_df.copy()
        train_df[self._target_column] = y_series.values

        # Validate input
        if len(train_df) == 0:
            raise ValueError("Training data is empty")

        # Convert to H2O Frame
        try:
            self._train_frame = h2o.H2OFrame(train_df)

            # Set target as factor for classification
            if self.task_type == "classification":
                self._train_frame[self._target_column] = (
                    self._train_frame[self._target_column].asfactor()
                )

            # Get feature names
            feature_names = [col for col in self._train_frame.columns if col != self._target_column]

        except Exception as e:
            raise ValueError(f"Failed to convert data to H2O Frame: {str(e)}")

        # Train the model
        start_time = time.time()

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')

                self.model = H2OAutoML(**self.automl_params)
                self.model.train(
                    x=feature_names,
                    y=self._target_column,
                    training_frame=self._train_frame,
                    **fit_params
                )

            self._training_time = time.time() - start_time
            self.is_fitted = True

            # Get best score
            leaderboard = self.model.leaderboard.as_data_frame()
            if not leaderboard.empty:
                # Get the metric (first metric column after model_id)
                metric_col = leaderboard.columns[1]
                self._best_score = float(leaderboard[metric_col].iloc[0])

            if self.verbose:
                print(f"Training completed in {self._training_time:.2f}s")
                if self._best_score:
                    print(f"Best model score: {self._best_score:.4f}")
                print(f"Total models trained: {len(self.model.leaderboard)}")

        except Exception as e:
            raise RuntimeError(f"H2O AutoML training failed: {str(e)}")

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

        # Convert to DataFrame if needed
        if isinstance(X, np.ndarray):
            X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
        else:
            X_df = X.copy()

        # Convert to H2O Frame
        try:
            test_frame = h2o.H2OFrame(X_df)
        except Exception as e:
            raise ValueError(f"Failed to convert data to H2O Frame: {str(e)}")

        # Make predictions
        predictions_h2o = self.model.leader.predict(test_frame)

        # Convert back to numpy
        if self.task_type == "classification":
            # Get predicted class
            predictions = predictions_h2o['predict'].as_data_frame().values.flatten()
        else:
            # Get predicted value
            predictions = predictions_h2o.as_data_frame().values.flatten()

        return predictions

    def _predict_proba_impl(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Implementation of predict_proba for classification tasks.

        Args:
            X: Features to predict on (n_samples, n_features)

        Returns:
            probabilities: Class probabilities (n_samples, n_classes)
        """
        # Convert to DataFrame if needed
        if isinstance(X, np.ndarray):
            X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
        else:
            X_df = X.copy()

        # Convert to H2O Frame
        test_frame = h2o.H2OFrame(X_df)

        # Make predictions
        predictions_h2o = self.model.leader.predict(test_frame)

        # Extract probability columns (all columns except 'predict')
        prob_cols = [col for col in predictions_h2o.columns if col != 'predict']
        probabilities = predictions_h2o[prob_cols].as_data_frame().values

        return probabilities

    def get_pipeline(self) -> Any:
        """Get the best model (leader) from the leaderboard.

        Returns:
            model: The best H2O model

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting pipeline")

        return self.model.leader

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
            "library": "H2O AutoML",
            "task_type": self.task_type,
            "time_limit": self.time_limit,
            "training_time": self._training_time,
            "best_score": self._best_score,
            "max_models": self.max_models,
            "nfolds": self.nfolds,
            "balance_classes": self.balance_classes,
            "n_jobs": self.n_jobs,
            "random_state": self.random_state,
        }

        # Add leader model information
        try:
            leader = self.model.leader
            config["leader_model_id"] = leader.model_id
            config["leader_algorithm"] = leader.algo

            # Get model parameters
            config["leader_params"] = leader.params

        except Exception as e:
            if self.verbose > 1:
                print(f"Could not extract leader model info: {e}")

        # Add leaderboard size
        try:
            config["n_models_trained"] = len(self.model.leaderboard)
        except:
            pass

        return config

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores from the best model.

        Returns:
            importance: Dictionary mapping feature names to importance scores,
                       or None if not available

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting feature importance")

        try:
            leader = self.model.leader

            # Get variable importance
            var_imp = leader.varimp(use_pandas=True)

            if var_imp is not None and not var_imp.empty:
                # Convert to dictionary
                importance = {}
                for _, row in var_imp.iterrows():
                    importance[row['variable']] = float(row['relative_importance'])

                return importance

        except Exception as e:
            if self.verbose > 1:
                print(f"Could not extract feature importance: {e}")

        return None

    def get_leaderboard(self) -> pd.DataFrame:
        """Get the H2O AutoML leaderboard with all trained models.

        Returns:
            leaderboard: DataFrame with model rankings and scores

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting leaderboard")

        try:
            leaderboard = self.model.leaderboard.as_data_frame()
            return leaderboard
        except Exception as e:
            raise RuntimeError(f"Failed to get leaderboard: {str(e)}")

    def get_model_by_rank(self, rank: int) -> Any:
        """Get a model from the leaderboard by its rank.

        Args:
            rank: Model rank (0-indexed, 0 is the best model)

        Returns:
            model: The H2O model at the specified rank

        Raises:
            RuntimeError: If model is not fitted
            ValueError: If rank is out of bounds
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting models")

        try:
            leaderboard = self.model.leaderboard.as_data_frame()

            if rank < 0 or rank >= len(leaderboard):
                raise ValueError(
                    f"Rank {rank} is out of bounds. Leaderboard has {len(leaderboard)} models."
                )

            model_id = leaderboard.iloc[rank]['model_id']
            return h2o.get_model(model_id)

        except Exception as e:
            raise RuntimeError(f"Failed to get model by rank: {str(e)}")

    def get_all_models(self) -> List[Any]:
        """Get all trained models from the leaderboard.

        Returns:
            models: List of all H2O models

        Raises:
            RuntimeError: If model is not fitted
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting models")

        try:
            leaderboard = self.model.leaderboard.as_data_frame()
            models = []

            for model_id in leaderboard['model_id']:
                models.append(h2o.get_model(model_id))

            return models

        except Exception as e:
            raise RuntimeError(f"Failed to get all models: {str(e)}")

    def shutdown(self) -> None:
        """Shutdown the H2O cluster.

        This should be called when you're done using H2O to free up resources.
        """
        if self._h2o_initialized:
            try:
                h2o.cluster().shutdown()
                self._h2o_initialized = False
                if self.verbose:
                    print("H2O cluster shut down")
            except Exception as e:
                if self.verbose > 1:
                    print(f"Error shutting down H2O: {e}")

    def __del__(self):
        """Cleanup when the object is deleted."""
        # Note: We don't automatically shutdown H2O in __del__
        # because it might be used by other objects
        pass
