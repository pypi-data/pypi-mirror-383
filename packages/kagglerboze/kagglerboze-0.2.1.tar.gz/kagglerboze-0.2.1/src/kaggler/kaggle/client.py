"""
Kaggle API Client

Main client for interacting with Kaggle competitions
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path


class KaggleClient:
    """
    High-level client for Kaggle API operations

    Handles authentication, downloads, submissions, and leaderboard tracking
    """

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Kaggle client

        Args:
            credentials_path: Path to kaggle.json (defaults to ~/.kaggle/kaggle.json)
        """
        self.credentials_path = credentials_path or os.path.expanduser("~/.kaggle/kaggle.json")
        self._load_credentials()
        self._validate_api()

    def _load_credentials(self):
        """Load Kaggle API credentials"""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Kaggle credentials not found at {self.credentials_path}\n"
                "Please download kaggle.json from https://www.kaggle.com/settings"
            )

        with open(self.credentials_path) as f:
            credentials = json.load(f)
            self.username = credentials.get("username")
            self.key = credentials.get("key")

        if not self.username or not self.key:
            raise ValueError("Invalid kaggle.json format")

        # Set environment variables for kaggle API
        os.environ["KAGGLE_USERNAME"] = self.username
        os.environ["KAGGLE_KEY"] = self.key

    def _validate_api(self):
        """Validate API connection"""
        try:
            from kaggle import api
            api.authenticate()
            self.api = api
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with Kaggle API: {e}")

    def list_competitions(self, search: Optional[str] = None) -> List[Dict]:
        """
        List available competitions

        Args:
            search: Search term to filter competitions

        Returns:
            List of competition dicts
        """
        competitions = self.api.competitions_list(search=search)
        return [
            {
                "id": comp.id,
                "title": comp.title,
                "url": comp.url,
                "deadline": comp.deadline,
                "category": comp.category,
                "reward": comp.reward,
            }
            for comp in competitions
        ]

    def get_competition_info(self, competition: str) -> Dict:
        """
        Get competition information

        Args:
            competition: Competition name

        Returns:
            Competition info dict
        """
        comp = self.api.competition_view(competition)
        return {
            "id": comp.id,
            "title": comp.title,
            "description": comp.description,
            "url": comp.url,
            "deadline": comp.deadline,
            "category": comp.category,
            "reward": comp.reward,
            "evaluation_metric": comp.evaluationMetric,
            "total_teams": comp.totalTeams,
        }

    def download_competition(
        self,
        competition: str,
        path: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> str:
        """
        Download competition data

        Args:
            competition: Competition name
            path: Download directory (default: ./data/{competition})
            files: Specific files to download (default: all)

        Returns:
            Path to downloaded data
        """
        from .downloader import CompetitionDownloader

        downloader = CompetitionDownloader(self.api)
        return downloader.download(competition, path, files)

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
            file_path: Path to submission file
            message: Submission message

        Returns:
            Submission result dict
        """
        from .submitter import SubmissionManager

        submitter = SubmissionManager(self.api)
        return submitter.submit(competition, file_path, message)

    def get_leaderboard(
        self,
        competition: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get competition leaderboard

        Args:
            competition: Competition name
            limit: Number of entries to return

        Returns:
            List of leaderboard entries
        """
        from .leaderboard import LeaderboardTracker

        tracker = LeaderboardTracker(self.api)
        return tracker.get_leaderboard(competition, limit)

    def get_my_submissions(self, competition: str) -> List[Dict]:
        """
        Get my submissions for competition

        Args:
            competition: Competition name

        Returns:
            List of submission dicts
        """
        submissions = self.api.competitions_submissions_list(competition)
        return [
            {
                "ref": sub.ref,
                "date": sub.date,
                "description": sub.description,
                "status": sub.status,
                "publicScore": sub.publicScore,
                "privateScore": sub.privateScore,
            }
            for sub in submissions
        ]

    def download_dataset(
        self,
        dataset: str,
        path: Optional[str] = None
    ) -> str:
        """
        Download Kaggle dataset

        Args:
            dataset: Dataset name (owner/dataset-name)
            path: Download directory

        Returns:
            Path to downloaded data
        """
        path = path or f"./data/{dataset.replace('/', '_')}"
        os.makedirs(path, exist_ok=True)

        self.api.dataset_download_files(dataset, path=path, unzip=True)
        return path
