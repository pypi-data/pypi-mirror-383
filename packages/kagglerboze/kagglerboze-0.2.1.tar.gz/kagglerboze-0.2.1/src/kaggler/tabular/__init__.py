"""
Tabular Competition Support

Automated ML pipeline for tabular competitions with:
- XGBoost/LightGBM hyperparameter optimization using genetic algorithms
- Automatic feature engineering
- Ensemble optimization

Example:
    >>> from kaggler.tabular import XGBoostGA, AutoFeatureEngineer, EnsembleOptimizer
    >>>
    >>> # Feature engineering
    >>> engineer = AutoFeatureEngineer()
    >>> X_train_fe = engineer.generate_features(X_train, y_train)
    >>> X_test_fe = engineer.transform(X_test)
    >>>
    >>> # Hyperparameter optimization
    >>> xgb_ga = XGBoostGA(population_size=20, n_generations=10)
    >>> xgb_ga.optimize(X_train_fe, y_train, X_val_fe, y_val)
    >>>
    >>> lgb_ga = LightGBMGA(population_size=20, n_generations=10)
    >>> lgb_ga.optimize(X_train_fe, y_train, X_val_fe, y_val)
    >>>
    >>> # Ensemble
    >>> ensemble = EnsembleOptimizer(method="weighted")
    >>> ensemble.add_model("xgboost", xgb_ga.best_model)
    >>> ensemble.add_model("lightgbm", lgb_ga.best_model)
    >>> ensemble.fit(X_train_fe, y_train, X_val_fe, y_val)
    >>>
    >>> # Predict
    >>> predictions = ensemble.predict(X_test_fe)
"""

from kaggler.tabular.xgboost_ga import XGBoostGA, XGBoostIndividual
from kaggler.tabular.lightgbm_ga import LightGBMGA, LightGBMIndividual
from kaggler.tabular.feature_eng import AutoFeatureEngineer, FeatureStats
from kaggler.tabular.ensemble import EnsembleOptimizer, EnsembleModel

__all__ = [
    # XGBoost
    "XGBoostGA",
    "XGBoostIndividual",
    # LightGBM
    "LightGBMGA",
    "LightGBMIndividual",
    # Feature Engineering
    "AutoFeatureEngineer",
    "FeatureStats",
    # Ensemble
    "EnsembleOptimizer",
    "EnsembleModel",
]
