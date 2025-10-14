"""
Titanic Survival Prediction Demo

Complete solution for Titanic competition using:
- Automatic feature engineering
- Genetic algorithm hyperparameter optimization
- Ensemble optimization

Target: 85%+ accuracy

Usage:
    python examples/tabular/titanic_demo.py

    Or with custom parameters:
    python examples/tabular/titanic_demo.py --population-size 30 --generations 20
"""

import sys
import os
import argparse
import time
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from kaggler.tabular import (
    XGBoostGA,
    LightGBMGA,
    AutoFeatureEngineer,
    EnsembleOptimizer,
)


def load_titanic_data():
    """
    Load Titanic dataset.

    If data doesn't exist locally, creates a synthetic dataset for demo.
    """
    try:
        # Try to load from local file
        train_df = pd.read_csv("train.csv")
        test_df = pd.read_csv("test.csv")
        print("Loaded Titanic data from local files")
    except FileNotFoundError:
        print("Creating synthetic Titanic-like dataset for demo...")

        # Create synthetic data
        np.random.seed(42)
        n_samples = 891

        # Generate features
        pclass = np.random.choice([1, 2, 3], size=n_samples, p=[0.24, 0.21, 0.55])
        sex = np.random.choice(["male", "female"], size=n_samples, p=[0.65, 0.35])
        age = np.random.normal(30, 12, size=n_samples).clip(0, 80)
        sibsp = np.random.poisson(0.5, size=n_samples).clip(0, 8)
        parch = np.random.poisson(0.4, size=n_samples).clip(0, 6)
        fare = np.random.exponential(32, size=n_samples).clip(0, 512)
        embarked = np.random.choice(["S", "C", "Q"], size=n_samples, p=[0.72, 0.19, 0.09])

        # Generate survival based on features (realistic pattern)
        survival_prob = np.full(n_samples, 0.3)
        survival_prob = survival_prob + 0.4 * (sex == "female").astype(int)  # Women more likely to survive
        survival_prob = survival_prob + 0.15 * (pclass == 1).astype(int)  # First class more likely
        survival_prob = survival_prob + 0.1 * (age < 15).astype(int)  # Children more likely
        survival_prob = survival_prob - 0.1 * (pclass == 3).astype(int)  # Third class less likely
        survival_prob = np.clip(survival_prob, 0, 1)

        survived = (np.random.random(n_samples) < survival_prob).astype(int)

        train_df = pd.DataFrame({
            "PassengerId": range(1, n_samples + 1),
            "Survived": survived,
            "Pclass": pclass,
            "Sex": sex,
            "Age": age,
            "SibSp": sibsp,
            "Parch": parch,
            "Fare": fare,
            "Embarked": embarked,
        })

        # Create test set
        test_df = train_df.sample(n=200, random_state=42).copy()
        test_df = test_df.drop(columns=["Survived"])

        print(f"Created synthetic dataset: {len(train_df)} train, {len(test_df)} test")

    return train_df, test_df


def preprocess_data(df):
    """Preprocess Titanic data."""
    df = df.copy()

    # Fill missing values
    df["Age"] = df["Age"].fillna(df["Age"].median())
    df["Fare"] = df["Fare"].fillna(df["Fare"].median())
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # Select features
    feature_cols = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]

    return df[feature_cols]


def main():
    parser = argparse.ArgumentParser(description="Titanic Survival Prediction Demo")
    parser.add_argument("--population-size", type=int, default=10, help="GA population size")
    parser.add_argument("--generations", type=int, default=5, help="Number of generations")
    parser.add_argument("--no-ensemble", action="store_true", help="Skip ensemble step")
    parser.add_argument("--output", type=str, default="submission.csv", help="Output file")
    args = parser.parse_args()

    print("=" * 60)
    print("TITANIC SURVIVAL PREDICTION DEMO")
    print("=" * 60)

    start_time = time.time()

    # Load data
    print("\n[1/6] Loading data...")
    train_df, test_df = load_titanic_data()

    # Preprocess
    print("\n[2/6] Preprocessing data...")
    X = preprocess_data(train_df)
    y = train_df["Survived"]
    X_test = preprocess_data(test_df)

    # Split into train and validation
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")

    # Feature engineering
    print("\n[3/6] Engineering features...")
    engineer = AutoFeatureEngineer(
        generate_interactions=True,
        generate_polynomials=True,
        generate_statistical=True,
        target_encode_categorical=True,
        select_top_k=50,
        verbose=True,
    )

    X_train_fe = engineer.generate_features(X_train, y_train)
    X_val_fe = engineer.transform(X_val)
    X_test_fe = engineer.transform(X_test)

    print(f"\nFeature engineering stats:")
    stats = engineer.get_feature_stats()
    print(f"  Original features: {stats.n_features_original}")
    print(f"  Generated features: {stats.n_features_generated}")
    print(f"  Selected features: {stats.n_features_selected}")

    # XGBoost optimization
    print("\n[4/6] Optimizing XGBoost...")
    xgb_ga = XGBoostGA(
        population_size=args.population_size,
        n_generations=args.generations,
        n_folds=3,
        early_stopping_rounds=50,
        verbose=True,
    )

    xgb_params = xgb_ga.optimize(X_train_fe, y_train, X_val_fe, y_val)
    xgb_pred = xgb_ga.predict(X_val_fe)
    xgb_accuracy = np.mean(xgb_pred == y_val)

    print(f"\nXGBoost validation accuracy: {xgb_accuracy:.4f} ({xgb_accuracy*100:.2f}%)")

    # LightGBM optimization
    print("\n[5/6] Optimizing LightGBM...")
    lgb_ga = LightGBMGA(
        population_size=args.population_size,
        n_generations=args.generations,
        n_folds=3,
        early_stopping_rounds=50,
        verbose=True,
    )

    lgb_params = lgb_ga.optimize(X_train_fe, y_train, X_val_fe, y_val)
    lgb_pred = lgb_ga.predict(X_val_fe)
    lgb_accuracy = np.mean(lgb_pred == y_val)

    print(f"\nLightGBM validation accuracy: {lgb_accuracy:.4f} ({lgb_accuracy*100:.2f}%)")

    # Ensemble
    if not args.no_ensemble:
        print("\n[6/6] Building ensemble...")
        ensemble = EnsembleOptimizer(
            method="weighted",
            optimize_weights=True,
            verbose=True,
        )

        ensemble.add_model("xgboost", xgb_ga.best_model)
        ensemble.add_model("lightgbm", lgb_ga.best_model)

        ensemble.fit(X_train_fe, y_train, X_val_fe, y_val)

        ensemble_pred = ensemble.predict(X_val_fe)
        ensemble_accuracy = np.mean(ensemble_pred == y_val)

        print(f"\nEnsemble validation accuracy: {ensemble_accuracy:.4f} ({ensemble_accuracy*100:.2f}%)")
        print("\nModel weights:")
        for name, weight in ensemble.get_model_weights().items():
            print(f"  {name}: {weight:.4f}")

        # Use ensemble for final predictions
        final_model = ensemble
        final_accuracy = ensemble_accuracy
    else:
        # Use best individual model
        if xgb_accuracy >= lgb_accuracy:
            final_model = xgb_ga
            final_accuracy = xgb_accuracy
            print("\nUsing XGBoost as final model")
        else:
            final_model = lgb_ga
            final_accuracy = lgb_accuracy
            print("\nUsing LightGBM as final model")

    # Generate predictions
    print("\nGenerating test predictions...")
    test_predictions = final_model.predict(X_test_fe)

    # Create submission file
    submission = pd.DataFrame({
        "PassengerId": test_df["PassengerId"] if "PassengerId" in test_df else range(1, len(test_predictions) + 1),
        "Survived": test_predictions,
    })

    submission.to_csv(args.output, index=False)
    print(f"Saved predictions to {args.output}")

    # Summary
    elapsed_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Final validation accuracy: {final_accuracy:.4f} ({final_accuracy*100:.2f}%)")
    print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")

    if final_accuracy >= 0.85:
        print("\nSUCCESS: Achieved 85%+ accuracy target!")
    else:
        print(f"\nNote: Accuracy {final_accuracy*100:.2f}% < 85% target")
        print("Try increasing population_size and generations for better results")

    print("\nFeature importance (top 10):")
    importance_df = xgb_ga.get_feature_importance().head(10)
    for idx, row in importance_df.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")


if __name__ == "__main__":
    main()
