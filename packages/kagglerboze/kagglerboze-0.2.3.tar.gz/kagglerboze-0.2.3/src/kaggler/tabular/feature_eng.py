"""
Automatic Feature Engineering

Automated feature generation, selection, and transformation for tabular data.
Includes interaction features, polynomial features, and target encoding.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
from dataclasses import dataclass
from itertools import combinations
import warnings

warnings.filterwarnings("ignore")


@dataclass
class FeatureStats:
    """Statistics for generated features."""
    n_features_original: int
    n_features_generated: int
    n_features_selected: int
    feature_names: List[str]
    importance_scores: Optional[Dict[str, float]] = None


class AutoFeatureEngineer:
    """
    Automatic Feature Engineering.

    Generates and selects features automatically for tabular data:
    - Interaction features (products, ratios, differences)
    - Polynomial features (squares, cubes, roots)
    - Statistical aggregations
    - Target encoding for categorical features
    - Feature selection based on importance

    Example:
        >>> from kaggler.tabular import AutoFeatureEngineer
        >>> engineer = AutoFeatureEngineer(
        ...     generate_interactions=True,
        ...     generate_polynomials=True,
        ...     target_encode_categorical=True
        ... )
        >>> X_train_fe = engineer.generate_features(X_train, y_train)
        >>> X_test_fe = engineer.transform(X_test)
    """

    def __init__(
        self,
        generate_interactions: bool = True,
        generate_polynomials: bool = True,
        generate_statistical: bool = True,
        target_encode_categorical: bool = True,
        interaction_degree: int = 2,
        polynomial_degree: int = 2,
        max_features: Optional[int] = None,
        select_top_k: Optional[int] = None,
        selection_threshold: float = 0.01,
        random_state: int = 42,
        verbose: bool = True,
    ):
        """
        Initialize AutoFeatureEngineer.

        Args:
            generate_interactions: Generate interaction features
            generate_polynomials: Generate polynomial features
            generate_statistical: Generate statistical features
            target_encode_categorical: Use target encoding for categoricals
            interaction_degree: Degree of interaction features
            polynomial_degree: Degree of polynomial features
            max_features: Maximum number of features to generate
            select_top_k: Select top k features by importance
            selection_threshold: Minimum importance threshold
            random_state: Random seed
            verbose: Print progress
        """
        self.generate_interactions = generate_interactions
        self.generate_polynomials = generate_polynomials
        self.generate_statistical = generate_statistical
        self.target_encode_categorical = target_encode_categorical
        self.interaction_degree = interaction_degree
        self.polynomial_degree = polynomial_degree
        self.max_features = max_features
        self.select_top_k = select_top_k
        self.selection_threshold = selection_threshold
        self.random_state = random_state
        self.verbose = verbose

        self.feature_names_: List[str] = []
        self.selected_features_: List[str] = []
        self.feature_importance_: Dict[str, float] = {}
        self.categorical_encodings_: Dict[str, Dict[Any, float]] = {}
        self.numerical_cols_: List[str] = []
        self.categorical_cols_: List[str] = []
        self.stats_: Optional[FeatureStats] = None

        np.random.seed(random_state)

    def _identify_column_types(self, X: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Identify numerical and categorical columns."""
        numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()

        return numerical_cols, categorical_cols

    def _generate_interaction_features(
        self,
        X: pd.DataFrame,
        numerical_cols: List[str],
    ) -> pd.DataFrame:
        """Generate interaction features (products, ratios, differences)."""
        if not self.generate_interactions or len(numerical_cols) < 2:
            return X

        X_new = X.copy()

        if self.verbose:
            print(f"Generating interaction features (degree={self.interaction_degree})...")

        for col1, col2 in combinations(numerical_cols, 2):
            # Product
            feature_name = f"{col1}_x_{col2}"
            X_new[feature_name] = X[col1] * X[col2]

            # Ratio (with small epsilon to avoid division by zero)
            feature_name = f"{col1}_div_{col2}"
            X_new[feature_name] = X[col1] / (X[col2] + 1e-8)

            # Difference
            feature_name = f"{col1}_minus_{col2}"
            X_new[feature_name] = X[col1] - X[col2]

            # Sum
            feature_name = f"{col1}_plus_{col2}"
            X_new[feature_name] = X[col1] + X[col2]

        return X_new

    def _generate_polynomial_features(
        self,
        X: pd.DataFrame,
        numerical_cols: List[str],
    ) -> pd.DataFrame:
        """Generate polynomial features (squares, cubes, roots)."""
        if not self.generate_polynomials:
            return X

        X_new = X.copy()

        if self.verbose:
            print(f"Generating polynomial features (degree={self.polynomial_degree})...")

        for col in numerical_cols:
            # Square
            if self.polynomial_degree >= 2:
                X_new[f"{col}_squared"] = X[col] ** 2

            # Cube
            if self.polynomial_degree >= 3:
                X_new[f"{col}_cubed"] = X[col] ** 3

            # Square root (for non-negative values)
            if (X[col] >= 0).all():
                X_new[f"{col}_sqrt"] = np.sqrt(X[col])

            # Log (for positive values)
            if (X[col] > 0).all():
                X_new[f"{col}_log"] = np.log1p(X[col])

        return X_new

    def _generate_statistical_features(
        self,
        X: pd.DataFrame,
        numerical_cols: List[str],
    ) -> pd.DataFrame:
        """Generate statistical aggregation features."""
        if not self.generate_statistical or len(numerical_cols) < 2:
            return X

        X_new = X.copy()

        if self.verbose:
            print("Generating statistical features...")

        # Row-wise statistics across numerical columns
        numerical_data = X[numerical_cols].values

        X_new["row_mean"] = np.mean(numerical_data, axis=1)
        X_new["row_std"] = np.std(numerical_data, axis=1)
        X_new["row_min"] = np.min(numerical_data, axis=1)
        X_new["row_max"] = np.max(numerical_data, axis=1)
        X_new["row_median"] = np.median(numerical_data, axis=1)
        X_new["row_sum"] = np.sum(numerical_data, axis=1)
        X_new["row_range"] = X_new["row_max"] - X_new["row_min"]

        return X_new

    def _target_encode_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        categorical_cols: List[str],
        is_training: bool = True,
    ) -> pd.DataFrame:
        """Apply target encoding to categorical features."""
        if not self.target_encode_categorical or len(categorical_cols) == 0:
            return X

        X_new = X.copy()

        if self.verbose and is_training:
            print("Applying target encoding to categorical features...")

        for col in categorical_cols:
            if is_training:
                # Create a temporary dataframe for encoding
                temp_df = pd.DataFrame({col: X[col], 'target': y.values})

                # Compute mean target value for each category
                encoding_dict = temp_df.groupby(col)['target'].mean().to_dict()

                # Store encoding for transform
                self.categorical_encodings_[col] = encoding_dict

                # Global mean for unseen categories
                self.categorical_encodings_[f"{col}_global_mean"] = float(y.mean())

                X_new[f"{col}_target_enc"] = X[col].map(encoding_dict).fillna(y.mean())
            else:
                # Apply stored encoding
                global_mean = self.categorical_encodings_.get(
                    f"{col}_global_mean",
                    0.5
                )
                X_new[f"{col}_target_enc"] = X[col].map(
                    self.categorical_encodings_.get(col, {})
                ).fillna(global_mean)

            # Drop original categorical column
            X_new = X_new.drop(columns=[col])

        return X_new

    def _select_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Select top features based on importance."""
        if self.select_top_k is None and self.selection_threshold is None:
            return X, X.columns.tolist()

        if self.verbose:
            print("Selecting important features...")

        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.feature_selection import SelectFromModel

            # Train quick random forest for feature importance
            rf = RandomForestClassifier(
                n_estimators=50,
                max_depth=5,
                random_state=self.random_state,
                n_jobs=-1,
            )
            rf.fit(X, y)

            # Get feature importance
            importance = rf.feature_importances_
            self.feature_importance_ = dict(zip(X.columns, importance))

            # Select features
            if self.select_top_k is not None:
                # Select top k features
                top_features = sorted(
                    self.feature_importance_.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:self.select_top_k]
                selected = [feat for feat, _ in top_features]
            else:
                # Select features above threshold
                selector = SelectFromModel(
                    rf,
                    threshold=self.selection_threshold,
                    prefit=True
                )
                selected = X.columns[selector.get_support()].tolist()

            if self.verbose:
                print(f"Selected {len(selected)}/{len(X.columns)} features")

            return X[selected], selected

        except Exception as e:
            if self.verbose:
                print(f"Feature selection failed: {e}. Using all features.")
            return X, X.columns.tolist()

    def generate_features(
        self,
        X: pd.DataFrame,
        y: Optional[pd.Series] = None,
    ) -> pd.DataFrame:
        """
        Generate features from input data.

        Args:
            X: Input features
            y: Target variable (required for target encoding and selection)

        Returns:
            DataFrame with generated features
        """
        if self.verbose:
            print(f"Starting feature engineering on {X.shape[0]} samples...")
            print(f"Original features: {X.shape[1]}")

        # Identify column types
        self.numerical_cols_, self.categorical_cols_ = self._identify_column_types(X)

        if self.verbose:
            print(f"Numerical columns: {len(self.numerical_cols_)}")
            print(f"Categorical columns: {len(self.categorical_cols_)}")

        # Generate features
        X_fe = X.copy()

        # Interaction features
        if len(self.numerical_cols_) >= 2:
            X_fe = self._generate_interaction_features(X_fe, self.numerical_cols_)

        # Polynomial features
        if len(self.numerical_cols_) >= 1:
            X_fe = self._generate_polynomial_features(X_fe, self.numerical_cols_)

        # Statistical features
        if len(self.numerical_cols_) >= 2:
            X_fe = self._generate_statistical_features(X_fe, self.numerical_cols_)

        # Target encoding
        if len(self.categorical_cols_) > 0 and y is not None:
            # Need to add target to X temporarily for groupby
            X_temp = X_fe.copy()
            y_temp = y.copy()
            if not hasattr(y_temp, "name") or y_temp.name is None:
                y_temp.name = "target"
            X_temp[y_temp.name] = y_temp.values
            X_fe = self._target_encode_features(X_temp, y_temp, self.categorical_cols_, is_training=True)

        # Replace inf/nan values
        X_fe = X_fe.replace([np.inf, -np.inf], np.nan)
        X_fe = X_fe.fillna(X_fe.median())

        if self.verbose:
            print(f"Generated features: {X_fe.shape[1]}")

        # Feature selection
        if y is not None and (self.select_top_k is not None or self.selection_threshold is not None):
            X_fe, self.selected_features_ = self._select_features(X_fe, y)
        else:
            self.selected_features_ = X_fe.columns.tolist()

        self.feature_names_ = X_fe.columns.tolist()

        # Store statistics
        self.stats_ = FeatureStats(
            n_features_original=X.shape[1],
            n_features_generated=X_fe.shape[1],
            n_features_selected=len(self.selected_features_),
            feature_names=self.feature_names_,
            importance_scores=self.feature_importance_ if self.feature_importance_ else None,
        )

        if self.verbose:
            print(f"Final features: {len(self.selected_features_)}")
            print("Feature engineering completed!")

        return X_fe

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data using fitted feature engineering.

        Args:
            X: Input features

        Returns:
            DataFrame with engineered features
        """
        if not self.feature_names_:
            raise ValueError("Feature engineer not fitted. Call generate_features() first.")

        # Generate features (without target encoding or selection)
        X_fe = X.copy()

        # Interaction features
        if len(self.numerical_cols_) >= 2:
            X_fe = self._generate_interaction_features(X_fe, self.numerical_cols_)

        # Polynomial features
        if len(self.numerical_cols_) >= 1:
            X_fe = self._generate_polynomial_features(X_fe, self.numerical_cols_)

        # Statistical features
        if len(self.numerical_cols_) >= 2:
            X_fe = self._generate_statistical_features(X_fe, self.numerical_cols_)

        # Target encoding (using stored encodings)
        if len(self.categorical_cols_) > 0:
            for col in self.categorical_cols_:
                if col in self.categorical_encodings_:
                    global_mean = self.categorical_encodings_.get(
                        f"{col}_global_mean",
                        0.5
                    )
                    X_fe[f"{col}_target_enc"] = X[col].map(
                        self.categorical_encodings_[col]
                    ).fillna(global_mean)
                    X_fe = X_fe.drop(columns=[col])

        # Replace inf/nan values
        X_fe = X_fe.replace([np.inf, -np.inf], np.nan)
        X_fe = X_fe.fillna(X_fe.median())

        # Select same features as training
        missing_features = set(self.selected_features_) - set(X_fe.columns)
        if missing_features:
            for feat in missing_features:
                X_fe[feat] = 0

        X_fe = X_fe[self.selected_features_]

        return X_fe

    def get_feature_stats(self) -> FeatureStats:
        """
        Get statistics about generated features.

        Returns:
            FeatureStats object
        """
        if self.stats_ is None:
            raise ValueError("No features generated yet. Call generate_features() first.")

        return self.stats_

    def get_top_features(self, n: int = 10) -> List[Tuple[str, float]]:
        """
        Get top n features by importance.

        Args:
            n: Number of top features to return

        Returns:
            List of (feature_name, importance) tuples
        """
        if not self.feature_importance_:
            raise ValueError("No feature importance available. Run with feature selection enabled.")

        return sorted(
            self.feature_importance_.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
