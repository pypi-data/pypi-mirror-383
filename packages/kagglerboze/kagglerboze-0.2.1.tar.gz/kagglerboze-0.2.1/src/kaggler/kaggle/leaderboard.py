"""
Leaderboard Tracker

Track competition leaderboard and submission scores
"""

from typing import Dict, List, Optional
import pandas as pd


class LeaderboardTracker:
    """Track leaderboard positions and scores"""

    def __init__(self, api):
        self.api = api

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
        try:
            leaderboard = self.api.competition_leaderboard_view(competition)

            entries = []
            for entry in leaderboard[:limit]:
                entries.append({
                    "teamId": entry.teamId,
                    "teamName": entry.teamName,
                    "score": entry.score,
                    "submissionDate": entry.submissionDate,
                })

            return entries
        except Exception as e:
            print(f"Failed to fetch leaderboard: {e}")
            return []

    def get_my_rank(self, competition: str) -> Optional[Dict]:
        """
        Get my current rank in competition

        Args:
            competition: Competition name

        Returns:
            Dict with rank info or None
        """
        submissions = self.api.competitions_submissions_list(competition)

        if not submissions:
            return None

        # Get best submission
        best_sub = max(
            submissions,
            key=lambda x: float(x.publicScore) if x.publicScore else 0
        )

        return {
            "score": best_sub.publicScore,
            "date": best_sub.date,
            "description": best_sub.description,
        }

    def compare_with_baseline(
        self,
        competition: str,
        my_score: float
    ) -> Dict:
        """
        Compare score with leaderboard

        Args:
            competition: Competition name
            my_score: My score to compare

        Returns:
            Comparison statistics
        """
        leaderboard = self.get_leaderboard(competition, limit=1000)

        if not leaderboard:
            return {"error": "Failed to fetch leaderboard"}

        scores = [float(entry["score"]) for entry in leaderboard if entry["score"]]

        # Calculate percentile
        better_than = sum(1 for s in scores if my_score > s)
        percentile = (better_than / len(scores)) * 100 if scores else 0

        # Find approximate rank
        rank = len(scores) - better_than + 1

        return {
            "my_score": my_score,
            "rank": rank,
            "total_teams": len(scores),
            "percentile": percentile,
            "top_score": max(scores) if scores else None,
            "median_score": sorted(scores)[len(scores)//2] if scores else None,
            "improvement_needed": max(scores) - my_score if scores else None,
        }

    def track_progress(
        self,
        competition: str,
        submissions_file: str = "submissions_history.csv"
    ) -> pd.DataFrame:
        """
        Track submission progress over time

        Args:
            competition: Competition name
            submissions_file: File to save history

        Returns:
            DataFrame with submission history
        """
        submissions = self.api.competitions_submissions_list(competition)

        history = []
        for sub in submissions:
            history.append({
                "date": sub.date,
                "description": sub.description,
                "publicScore": sub.publicScore,
                "privateScore": sub.privateScore,
                "status": sub.status,
            })

        df = pd.DataFrame(history)

        # Sort by date
        if not df.empty and "date" in df.columns:
            df = df.sort_values("date")
            df.to_csv(submissions_file, index=False)
            print(f"✓ Saved submission history to {submissions_file}")

        return df

    def predict_shake_up(
        self,
        competition: str,
        cv_score: float,
        public_score: float
    ) -> Dict:
        """
        Predict potential leaderboard shake-up

        Args:
            competition: Competition name
            cv_score: Cross-validation score
            public_score: Public leaderboard score

        Returns:
            Shake-up prediction
        """
        difference = public_score - cv_score

        if abs(difference) < 0.01:
            confidence = "high"
            prediction = "stable"
            message = "CV and public scores align well"
        elif difference > 0.02:
            confidence = "medium"
            prediction = "possible_drop"
            message = "Public score higher than CV - possible overfitting to public test"
        elif difference < -0.02:
            confidence = "medium"
            prediction = "possible_rise"
            message = "Public score lower than CV - may improve on private test"
        else:
            confidence = "high"
            prediction = "stable"
            message = "Slight difference is normal"

        return {
            "cv_score": cv_score,
            "public_score": public_score,
            "difference": difference,
            "prediction": prediction,
            "confidence": confidence,
            "message": message,
        }
