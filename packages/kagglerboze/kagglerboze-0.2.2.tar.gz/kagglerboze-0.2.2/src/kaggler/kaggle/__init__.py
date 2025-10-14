"""
Kaggle API Integration

Wrapper around Kaggle API for competition automation
"""

from .client import KaggleClient
from .downloader import CompetitionDownloader
from .submitter import SubmissionManager
from .leaderboard import LeaderboardTracker

__all__ = [
    "KaggleClient",
    "CompetitionDownloader",
    "SubmissionManager",
    "LeaderboardTracker",
]
