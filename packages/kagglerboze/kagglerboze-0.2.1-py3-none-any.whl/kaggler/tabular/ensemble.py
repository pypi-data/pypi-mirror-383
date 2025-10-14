"""
Ensemble Model Optimizer

Optimizes ensemble models through stacking, blending, and weight optimization.
Combines multiple models for improved predictions.
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass
import warnings
from scipy.optimize import minimize

warnings.filterwarnings("ignore")


@dataclass
class EnsembleModel:
    """Model in the ensemble."""
    name: str
    model: Any
    weight: float = 1.0
    predictions: Optional[np.ndarray] = None
    score: float = 0.0


class EnsembleOptimizer:
    """
    Ensemble Model Optimizer.

    Combines multiple models using:
    - Simple averaging/voting
    - Weighted averaging with optimized weights
    - Stacking with meta-learner
    - Rank averaging

    Example:
        >>> from kaggler.tabular import EnsembleOptimizer
        >>> ensemble = EnsembleOptimizer(method="weighted")
        >>> ensemble.add_model("xgboost", xgb_model)
        >>> ensemble.add_model("lightgbm", lgb_model)
        >>> ensemble.fit(X_train, y_train, X_val, y_val)
        >>> predictions = ensemble.predict(X_test)
    """

    def __init__(
        self,
        method: str = "weighted",
        meta_learner: Optional[Any] = None,
        optimize_weights: bool = True,
        cv_folds: int = 5,
        random_state: int = 42,
        verbose: bool = True,
    ):
        """
        Initialize EnsembleOptimizer.

        Args:
            method: Ensemble method ("simple", "weighted", "stacking", "rank")
            meta_learner: Meta-learner for stacking (if None, uses LogisticRegression)
            optimize_weights: Optimize weights for weighted averaging
            cv_folds: Number of CV folds for stacking
            random_state: Random seed
            verbose: Print progress
        """
        self.method = method
        self.meta_learner = meta_learner
        self.optimize_weights = optimize_weights
        self.cv_folds = cv_folds
        self.random_state = random_state
        self.verbose = verbose

        self.models: List[EnsembleModel] = []
        self.weights_: Optional[np.ndarray] = None
        self.is_fitted_ = False

        np.random.seed(random_state)

    def add_model(
        self,
        name: str,
        model: Any,
        weight: float = 1.0,
    ) -> None:
        """
        Add a model to the ensemble.

        Args:
            name: Model name
            model: Trained model (must have predict/predict_proba methods)
            weight: Initial weight (for weighted averaging)
        """
        if not hasattr(model, "predict"):
            raise ValueError(f"Model {name} must have predict method")

        self.models.append(EnsembleModel(
            name=name,
            model=model,
            weight=weight,
        ))

        if self.verbose:
            print(f"Added model: {name} (weight={weight})")

    def _simple_average(
        self,
        predictions: List[np.ndarray],
    ) -> np.ndarray:
        """Simple average of predictions."""
        return np.mean(predictions, axis=0)

    def _weighted_average(
        self,
        predictions: List[np.ndarray],
        weights: np.ndarray,
    ) -> np.ndarray:
        """Weighted average of predictions."""
        # Normalize weights
        weights = weights / np.sum(weights)

        # Compute weighted average
        weighted_preds = np.zeros_like(predictions[0])
        for pred, weight in zip(predictions, weights):
            weighted_preds += weight * pred

        return weighted_preds

    def _rank_average(
        self,
        predictions: List[np.ndarray],
    ) -> np.ndarray:
        """Rank average of predictions."""
        # Convert to ranks
        ranks = []
        for pred in predictions:
            if pred.ndim == 2:
                # For probabilities, use positive class
                pred = pred[:, 1]
            rank = pd.Series(pred).rank(pct=True).values
            ranks.append(rank)

        # Average ranks
        avg_rank = np.mean(ranks, axis=0)

        return avg_rank

    def _optimize_weights(
        self,
        predictions: List[np.ndarray],
        y_true: np.ndarray,
        metric: str = "accuracy",
    ) -> np.ndarray:
        """
        Optimize ensemble weights to minimize loss.

        Args:
            predictions: List of model predictions
            y_true: True labels
            metric: Metric to optimize ("accuracy" or "logloss")

        Returns:
            Optimized weights
        """
        n_models = len(predictions)

        def objective(weights):
            """Objective function to minimize."""
            # Normalize weights
            weights = weights / np.sum(weights)

            # Compute weighted prediction
            weighted_pred = self._weighted_average(predictions, weights)

            # Compute loss
            if metric == "accuracy":
                # Binary predictions
                if weighted_pred.ndim == 2:
                    weighted_pred = weighted_pred[:, 1]
                pred_labels = (weighted_pred > 0.5).astype(int)
                loss = -np.mean(pred_labels == y_true)  # Negative accuracy
            else:  # logloss
                if weighted_pred.ndim == 2:
                    weighted_pred = weighted_pred[:, 1]
                # Clip predictions to avoid log(0)
                weighted_pred = np.clip(weighted_pred, 1e-7, 1 - 1e-7)
                loss = -np.mean(
                    y_true * np.log(weighted_pred) +
                    (1 - y_true) * np.log(1 - weighted_pred)
                )

            return loss

        # Initialize with equal weights
        initial_weights = np.ones(n_models) / n_models

        # Constraints: weights sum to 1 and are non-negative
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
        bounds = [(0, 1) for _ in range(n_models)]

        # Optimize
        result = minimize(
            objective,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        if not result.success:
            if self.verbose:
                print("Weight optimization failed. Using equal weights.")
            return initial_weights

        return result.x

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> "EnsembleOptimizer":
        """
        Fit the ensemble on training data.

        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (required for weight optimization)
            y_val: Validation labels (required for weight optimization)

        Returns:
            Self
        """
        if len(self.models) == 0:
            raise ValueError("No models added to ensemble. Call add_model() first.")

        if self.verbose:
            print(f"Fitting ensemble with {len(self.models)} models...")
            print(f"Method: {self.method}")

        # Get predictions from all models
        val_predictions = []

        for model_info in self.models:
            model = model_info.model

            # Get validation predictions
            if X_val is not None:
                if hasattr(model, "predict_proba"):
                    pred = model.predict_proba(X_val)
                else:
                    pred = model.predict(X_val)

                val_predictions.append(pred)

                # Evaluate individual model
                if pred.ndim == 2:
                    pred_labels = (pred[:, 1] > 0.5).astype(int)
                else:
                    pred_labels = (pred > 0.5).astype(int)

                score = np.mean(pred_labels == y_val)
                model_info.score = float(score)

                if self.verbose:
                    print(f"{model_info.name}: {score:.4f}")

        # Optimize ensemble
        if self.method == "simple":
            # Equal weights
            self.weights_ = np.ones(len(self.models)) / len(self.models)

        elif self.method == "weighted":
            if self.optimize_weights and X_val is not None and y_val is not None:
                if self.verbose:
                    print("Optimizing ensemble weights...")

                self.weights_ = self._optimize_weights(
                    val_predictions,
                    y_val.values,
                    metric="accuracy",
                )

                if self.verbose:
                    for model_info, weight in zip(self.models, self.weights_):
                        print(f"{model_info.name}: weight={weight:.4f}")
            else:
                # Use scores as weights
                scores = np.array([m.score for m in self.models])
                self.weights_ = scores / np.sum(scores)

        elif self.method == "stacking":
            if X_val is None or y_val is None:
                raise ValueError("Stacking requires validation data")

            if self.verbose:
                print("Training meta-learner...")

            # Create meta-features from model predictions
            meta_features = np.column_stack(val_predictions)

            # Train meta-learner
            if self.meta_learner is None:
                from sklearn.linear_model import LogisticRegression
                self.meta_learner = LogisticRegression(random_state=self.random_state)

            self.meta_learner.fit(meta_features, y_val)

        elif self.method == "rank":
            # No fitting needed for rank averaging
            self.weights_ = np.ones(len(self.models)) / len(self.models)

        else:
            raise ValueError(f"Unknown method: {self.method}")

        # Mark as fitted before evaluation
        self.is_fitted_ = True

        # Evaluate ensemble
        if X_val is not None and y_val is not None:
            ensemble_pred = self.predict(X_val)
            ensemble_score = np.mean(ensemble_pred == y_val)

            if self.verbose:
                print(f"\nEnsemble score: {ensemble_score:.4f}")

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict using the ensemble.

        Args:
            X: Features to predict

        Returns:
            Predicted labels
        """
        if not self.is_fitted_:
            raise ValueError("Ensemble not fitted. Call fit() first.")

        # Get predictions from all models
        predictions = []
        for model_info in self.models:
            model = model_info.model

            if hasattr(model, "predict_proba"):
                pred = model.predict_proba(X)
            else:
                pred = model.predict(X)

            predictions.append(pred)

        # Combine predictions
        if self.method == "simple":
            ensemble_pred = self._simple_average(predictions)

        elif self.method == "weighted":
            ensemble_pred = self._weighted_average(predictions, self.weights_)

        elif self.method == "stacking":
            # Create meta-features
            meta_features = np.column_stack(predictions)
            return self.meta_learner.predict(meta_features)

        elif self.method == "rank":
            ensemble_pred = self._rank_average(predictions)

        else:
            raise ValueError(f"Unknown method: {self.method}")

        # Convert to labels
        if ensemble_pred.ndim == 2:
            ensemble_pred = ensemble_pred[:, 1]

        return (ensemble_pred > 0.5).astype(int)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict probabilities using the ensemble.

        Args:
            X: Features to predict

        Returns:
            Predicted probabilities
        """
        if not self.is_fitted_:
            raise ValueError("Ensemble not fitted. Call fit() first.")

        # Get predictions from all models
        predictions = []
        for model_info in self.models:
            model = model_info.model

            if hasattr(model, "predict_proba"):
                pred = model.predict_proba(X)
            else:
                # Convert predictions to probabilities
                pred = model.predict(X)
                if pred.ndim == 1:
                    pred = np.column_stack([1 - pred, pred])

            predictions.append(pred)

        # Combine predictions
        if self.method == "simple":
            ensemble_pred = self._simple_average(predictions)

        elif self.method == "weighted":
            ensemble_pred = self._weighted_average(predictions, self.weights_)

        elif self.method == "stacking":
            # Create meta-features
            meta_features = np.column_stack(predictions)
            return self.meta_learner.predict_proba(meta_features)

        elif self.method == "rank":
            # Rank average gives continuous values
            rank_avg = self._rank_average(predictions)
            return np.column_stack([1 - rank_avg, rank_avg])

        else:
            raise ValueError(f"Unknown method: {self.method}")

        # Ensure 2D output
        if ensemble_pred.ndim == 1:
            ensemble_pred = np.column_stack([1 - ensemble_pred, ensemble_pred])

        return ensemble_pred

    def get_model_weights(self) -> Dict[str, float]:
        """
        Get model weights in the ensemble.

        Returns:
            Dictionary mapping model names to weights
        """
        if not self.is_fitted_:
            raise ValueError("Ensemble not fitted. Call fit() first.")

        if self.weights_ is None:
            return {m.name: m.weight for m in self.models}

        return {m.name: w for m, w in zip(self.models, self.weights_)}

    def get_model_scores(self) -> Dict[str, float]:
        """
        Get individual model scores.

        Returns:
            Dictionary mapping model names to scores
        """
        return {m.name: m.score for m in self.models}
