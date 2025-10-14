"""
Research Leaderboard

Manages benchmark leaderboards with reproducibility verification
and result validation.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MetricType(str, Enum):
    """Metric optimization direction"""
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"


@dataclass
class LeaderboardEntry:
    """
    Single entry in research leaderboard

    Attributes:
        entry_id: Unique entry identifier
        benchmark_id: Associated benchmark
        user_id: User who submitted
        institution: User's institution
        score: Achieved score
        method: Method/model name
        description: Method description
        submission_date: When submitted
        verified: Whether result is verified
        reproducible: Whether result is reproducible
        checksum: Reproducibility checksum
        code_url: URL to code (optional)
        paper_url: URL to paper (optional)
        metadata: Additional metadata
    """
    entry_id: str
    benchmark_id: str
    user_id: str
    institution: str
    score: float
    method: str
    description: str
    submission_date: datetime = field(default_factory=datetime.utcnow)
    verified: bool = False
    reproducible: bool = False
    checksum: Optional[str] = None
    code_url: Optional[str] = None
    paper_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entry_id": self.entry_id,
            "benchmark_id": self.benchmark_id,
            "user_id": self.user_id,
            "institution": self.institution,
            "score": self.score,
            "method": self.method,
            "description": self.description,
            "submission_date": self.submission_date.isoformat(),
            "verified": self.verified,
            "reproducible": self.reproducible,
            "checksum": self.checksum,
            "code_url": self.code_url,
            "paper_url": self.paper_url,
            "metadata": self.metadata
        }


class ResearchLeaderboard:
    """
    Leaderboard manager for research benchmarks

    Tracks submissions, ranks results, and verifies reproducibility.
    """

    def __init__(self, benchmark_id: str, metric_type: MetricType = MetricType.HIGHER_IS_BETTER):
        self.benchmark_id = benchmark_id
        self.metric_type = metric_type
        self._entries: Dict[str, LeaderboardEntry] = {}
        self._rankings: List[str] = []  # Sorted list of entry_ids

    def submit_result(
        self,
        user_id: str,
        institution: str,
        score: float,
        method: str,
        description: str,
        code_url: Optional[str] = None,
        paper_url: Optional[str] = None,
        checksum: Optional[str] = None,
        **metadata
    ) -> LeaderboardEntry:
        """
        Submit result to leaderboard

        Args:
            user_id: User submitting
            institution: User's institution
            score: Achieved score
            method: Method name
            description: Method description
            code_url: URL to code repository
            paper_url: URL to paper
            checksum: Reproducibility checksum
            **metadata: Additional metadata

        Returns:
            Created LeaderboardEntry
        """
        import hashlib

        entry_id = hashlib.md5(
            f"{self.benchmark_id}_{user_id}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        entry = LeaderboardEntry(
            entry_id=entry_id,
            benchmark_id=self.benchmark_id,
            user_id=user_id,
            institution=institution,
            score=score,
            method=method,
            description=description,
            code_url=code_url,
            paper_url=paper_url,
            checksum=checksum,
            metadata=metadata
        )

        self._entries[entry_id] = entry
        self._update_rankings()

        return entry

    def verify_entry(self, entry_id: str, verified: bool = True) -> bool:
        """
        Mark entry as verified

        Args:
            entry_id: Entry identifier
            verified: Verification status

        Returns:
            True if updated
        """
        entry = self._entries.get(entry_id)
        if entry:
            entry.verified = verified
            return True
        return False

    def mark_reproducible(self, entry_id: str, reproducible: bool = True) -> bool:
        """
        Mark entry as reproducible

        Args:
            entry_id: Entry identifier
            reproducible: Reproducibility status

        Returns:
            True if updated
        """
        entry = self._entries.get(entry_id)
        if entry:
            entry.reproducible = reproducible
            return True
        return False

    def get_rankings(
        self,
        top_k: Optional[int] = None,
        verified_only: bool = False,
        reproducible_only: bool = False
    ) -> List[LeaderboardEntry]:
        """
        Get ranked leaderboard entries

        Args:
            top_k: Return top K entries only
            verified_only: Only return verified entries
            reproducible_only: Only return reproducible entries

        Returns:
            List of ranked entries
        """
        entries = [self._entries[eid] for eid in self._rankings]

        # Apply filters
        if verified_only:
            entries = [e for e in entries if e.verified]
        if reproducible_only:
            entries = [e for e in entries if e.reproducible]

        # Apply limit
        if top_k:
            entries = entries[:top_k]

        return entries

    def get_entry(self, entry_id: str) -> Optional[LeaderboardEntry]:
        """Get specific entry"""
        return self._entries.get(entry_id)

    def get_user_entries(self, user_id: str) -> List[LeaderboardEntry]:
        """Get all entries for a user"""
        return [e for e in self._entries.values() if e.user_id == user_id]

    def get_institution_entries(self, institution: str) -> List[LeaderboardEntry]:
        """Get all entries for an institution"""
        return [e for e in self._entries.values() if e.institution == institution]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get leaderboard statistics

        Returns:
            Dictionary with statistics
        """
        entries = list(self._entries.values())
        if not entries:
            return {
                "total_submissions": 0,
                "verified_submissions": 0,
                "reproducible_submissions": 0,
                "unique_institutions": 0,
                "unique_users": 0
            }

        scores = [e.score for e in entries]
        institutions = set(e.institution for e in entries)
        users = set(e.user_id for e in entries)

        return {
            "total_submissions": len(entries),
            "verified_submissions": sum(1 for e in entries if e.verified),
            "reproducible_submissions": sum(1 for e in entries if e.reproducible),
            "unique_institutions": len(institutions),
            "unique_users": len(users),
            "best_score": max(scores) if self.metric_type == MetricType.HIGHER_IS_BETTER else min(scores),
            "mean_score": sum(scores) / len(scores),
            "institutions": list(institutions)
        }

    def delete_entry(self, entry_id: str) -> bool:
        """
        Delete entry from leaderboard

        Args:
            entry_id: Entry identifier

        Returns:
            True if deleted
        """
        if entry_id in self._entries:
            del self._entries[entry_id]
            self._update_rankings()
            return True
        return False

    def _update_rankings(self):
        """Update rankings based on scores"""
        entries = list(self._entries.values())

        if self.metric_type == MetricType.HIGHER_IS_BETTER:
            entries.sort(key=lambda e: e.score, reverse=True)
        else:
            entries.sort(key=lambda e: e.score)

        self._rankings = [e.entry_id for e in entries]

    def export_leaderboard(self, format: str = "json") -> str:
        """
        Export leaderboard

        Args:
            format: Export format (json)

        Returns:
            Serialized leaderboard
        """
        import json

        data = {
            "benchmark_id": self.benchmark_id,
            "metric_type": self.metric_type.value,
            "entries": [e.to_dict() for e in self.get_rankings()],
            "statistics": self.get_statistics()
        }

        if format == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
