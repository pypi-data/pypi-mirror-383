"""
Submission Manager

Handles submission validation and submission to Kaggle
"""

import os
import pandas as pd
from typing import Dict, Optional
from pathlib import Path


class SubmissionManager:
    """Manage competition submissions"""

    def __init__(self, api):
        self.api = api

    def submit(
        self,
        competition: str,
        file_path: str,
        message: str = ""
    ) -> Dict:
        """
        Submit predictions to competition

        Args:
            competition: Competition name
            file_path: Path to submission CSV
            message: Submission message

        Returns:
            Dict with submission result
        """
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Submission file not found: {file_path}")

        # Validate submission format
        validation_result = self.validate_submission(competition, file_path)
        if not validation_result["valid"]:
            raise ValueError(
                f"Invalid submission format:\n" +
                "\n".join(validation_result["errors"])
            )

        # Submit to Kaggle
        print(f"Submitting {file_path} to {competition}...")
        result = self.api.competition_submit(file_path, message, competition)

        return {
            "success": True,
            "message": message,
            "file": file_path,
            "result": str(result)
        }

    def validate_submission(self, competition: str, file_path: str) -> Dict:
        """
        Validate submission file format

        Args:
            competition: Competition name
            file_path: Path to submission file

        Returns:
            Dict with validation result
        """
        errors = []

        # Load submission file
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return {"valid": False, "errors": [f"Failed to read CSV: {e}"]}

        # Try to load sample submission for comparison
        sample_sub = self._load_sample_submission(competition)

        if sample_sub is not None:
            # Check columns match
            if list(df.columns) != list(sample_sub.columns):
                errors.append(
                    f"Column mismatch. Expected: {list(sample_sub.columns)}, "
                    f"Got: {list(df.columns)}"
                )

            # Check number of rows
            if len(df) != len(sample_sub):
                errors.append(
                    f"Row count mismatch. Expected: {len(sample_sub)}, "
                    f"Got: {len(df)}"
                )

            # Check ID coverage
            if "id" in df.columns and "id" in sample_sub.columns:
                missing_ids = set(sample_sub["id"]) - set(df["id"])
                if missing_ids:
                    errors.append(f"Missing IDs: {list(missing_ids)[:10]}...")

        # Check for missing values in target column
        target_col = df.columns[-1] if len(df.columns) > 1 else None
        if target_col and df[target_col].isnull().any():
            n_missing = df[target_col].isnull().sum()
            errors.append(f"Missing values in target column: {n_missing} rows")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _load_sample_submission(self, competition: str) -> Optional[pd.DataFrame]:
        """Load sample submission if available"""
        try:
            # Check if already downloaded
            data_path = f"./data/{competition}"
            sample_files = [
                "sample_submission.csv",
                "sampleSubmission.csv",
                "sample-submission.csv"
            ]

            for sample_file in sample_files:
                sample_path = os.path.join(data_path, sample_file)
                if os.path.exists(sample_path):
                    return pd.read_csv(sample_path)

            return None
        except Exception:
            return None

    def create_submission_template(
        self,
        competition: str,
        output_path: str = "submission.csv"
    ) -> str:
        """
        Create submission template from sample submission

        Args:
            competition: Competition name
            output_path: Output file path

        Returns:
            Path to created template
        """
        sample_sub = self._load_sample_submission(competition)

        if sample_sub is None:
            raise FileNotFoundError(
                f"Sample submission not found for {competition}. "
                "Please download competition data first."
            )

        # Create template with same structure
        sample_sub.to_csv(output_path, index=False)
        print(f"✓ Created submission template: {output_path}")

        return output_path
