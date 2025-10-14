"""
Ethics Review Support

Manages ethical review processes for research datasets and experiments.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EthicsStatus(str, Enum):
    """Status of ethics review"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    CONDITIONAL_APPROVAL = "conditional_approval"
    REJECTED = "rejected"
    EXPIRED = "expired"


class EthicsCategory(str, Enum):
    """Categories of ethical concerns"""
    HUMAN_SUBJECTS = "human_subjects"
    ANIMAL_RESEARCH = "animal_research"
    SENSITIVE_DATA = "sensitive_data"
    DUAL_USE = "dual_use"
    ENVIRONMENTAL = "environmental"
    BIAS_FAIRNESS = "bias_fairness"


@dataclass
class EthicsReview:
    """
    Ethics review record

    Attributes:
        review_id: Unique review identifier
        dataset_id: Dataset being reviewed
        categories: List of ethical concern categories
        status: Review status
        reviewer_id: ID of reviewer
        institution: Reviewing institution
        submitted_at: Submission timestamp
        reviewed_at: Review completion timestamp
        approved_at: Approval timestamp
        expires_at: Approval expiration
        conditions: Conditions for approval
        concerns: Identified ethical concerns
        recommendations: Reviewer recommendations
        notes: Additional notes
    """
    review_id: str
    dataset_id: str
    categories: List[EthicsCategory]
    status: EthicsStatus = EthicsStatus.PENDING
    reviewer_id: Optional[str] = None
    institution: Optional[str] = None
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    conditions: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    notes: str = ""

    def is_valid(self) -> bool:
        """Check if approval is still valid"""
        if self.status not in [EthicsStatus.APPROVED, EthicsStatus.CONDITIONAL_APPROVAL]:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "review_id": self.review_id,
            "dataset_id": self.dataset_id,
            "categories": [c.value for c in self.categories],
            "status": self.status.value,
            "reviewer_id": self.reviewer_id,
            "institution": self.institution,
            "submitted_at": self.submitted_at.isoformat(),
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "conditions": self.conditions,
            "concerns": self.concerns,
            "recommendations": self.recommendations,
            "notes": self.notes
        }


class EthicsReviewManager:
    """
    Manager for ethics reviews

    Handles submission, review, and tracking of ethical approvals.
    """

    def __init__(self):
        self._reviews: Dict[str, EthicsReview] = {}
        self._dataset_reviews: Dict[str, List[str]] = {}  # dataset_id -> review_ids

    def submit_review(
        self,
        dataset_id: str,
        categories: List[EthicsCategory],
        institution: Optional[str] = None,
        concerns: Optional[List[str]] = None
    ) -> EthicsReview:
        """
        Submit dataset for ethics review

        Args:
            dataset_id: Dataset identifier
            categories: Ethical concern categories
            institution: Submitting institution
            concerns: Identified concerns

        Returns:
            Created EthicsReview object
        """
        import hashlib

        review_id = hashlib.md5(
            f"{dataset_id}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        review = EthicsReview(
            review_id=review_id,
            dataset_id=dataset_id,
            categories=categories,
            institution=institution,
            concerns=concerns or []
        )

        self._reviews[review_id] = review

        # Update dataset index
        if dataset_id not in self._dataset_reviews:
            self._dataset_reviews[dataset_id] = []
        self._dataset_reviews[dataset_id].append(review_id)

        return review

    def assign_reviewer(self, review_id: str, reviewer_id: str) -> bool:
        """Assign reviewer to ethics review"""
        review = self._reviews.get(review_id)
        if review:
            review.reviewer_id = reviewer_id
            review.status = EthicsStatus.UNDER_REVIEW
            return True
        return False

    def complete_review(
        self,
        review_id: str,
        status: EthicsStatus,
        reviewer_id: str,
        conditions: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        notes: str = "",
        approval_period_days: int = 365
    ) -> bool:
        """
        Complete ethics review

        Args:
            review_id: Review identifier
            status: Review outcome status
            reviewer_id: ID of reviewer
            conditions: Conditions for approval
            recommendations: Reviewer recommendations
            notes: Additional notes
            approval_period_days: Days until approval expires

        Returns:
            True if completed successfully
        """
        from datetime import timedelta

        review = self._reviews.get(review_id)
        if not review:
            return False

        if review.reviewer_id and review.reviewer_id != reviewer_id:
            raise PermissionError("Only assigned reviewer can complete review")

        review.status = status
        review.reviewed_at = datetime.utcnow()
        review.conditions = conditions or []
        review.recommendations = recommendations or []
        review.notes = notes

        if status in [EthicsStatus.APPROVED, EthicsStatus.CONDITIONAL_APPROVAL]:
            review.approved_at = datetime.utcnow()
            review.expires_at = datetime.utcnow() + timedelta(days=approval_period_days)

        return True

    def get_review(self, review_id: str) -> Optional[EthicsReview]:
        """Get review by ID"""
        return self._reviews.get(review_id)

    def get_dataset_reviews(self, dataset_id: str) -> List[EthicsReview]:
        """Get all reviews for dataset"""
        review_ids = self._dataset_reviews.get(dataset_id, [])
        return [self._reviews[rid] for rid in review_ids if rid in self._reviews]

    def get_latest_review(self, dataset_id: str) -> Optional[EthicsReview]:
        """Get most recent review for dataset"""
        reviews = self.get_dataset_reviews(dataset_id)
        if not reviews:
            return None
        return max(reviews, key=lambda r: r.submitted_at)

    def check_approval(self, dataset_id: str) -> bool:
        """Check if dataset has valid approval"""
        latest_review = self.get_latest_review(dataset_id)
        return latest_review.is_valid() if latest_review else False

    def list_pending_reviews(
        self,
        reviewer_id: Optional[str] = None
    ) -> List[EthicsReview]:
        """List pending reviews, optionally filtered by reviewer"""
        reviews = [
            r for r in self._reviews.values()
            if r.status in [EthicsStatus.PENDING, EthicsStatus.UNDER_REVIEW]
        ]

        if reviewer_id:
            reviews = [r for r in reviews if r.reviewer_id == reviewer_id]

        return reviews

    def add_concern(self, review_id: str, concern: str) -> bool:
        """Add ethical concern to review"""
        review = self._reviews.get(review_id)
        if review:
            review.concerns.append(concern)
            return True
        return False

    def add_recommendation(self, review_id: str, recommendation: str) -> bool:
        """Add recommendation to review"""
        review = self._reviews.get(review_id)
        if review:
            review.recommendations.append(recommendation)
            return True
        return False

    def renew_approval(
        self,
        review_id: str,
        renewal_period_days: int = 365
    ) -> bool:
        """
        Renew ethics approval

        Args:
            review_id: Review identifier
            renewal_period_days: Renewal period in days

        Returns:
            True if renewed successfully
        """
        from datetime import timedelta

        review = self._reviews.get(review_id)
        if not review:
            return False

        if review.status not in [EthicsStatus.APPROVED, EthicsStatus.CONDITIONAL_APPROVAL]:
            return False

        review.expires_at = datetime.utcnow() + timedelta(days=renewal_period_days)
        return True

    def generate_ethics_report(self, dataset_id: str) -> Dict:
        """Generate ethics compliance report"""
        reviews = self.get_dataset_reviews(dataset_id)
        latest_review = self.get_latest_review(dataset_id)

        if not reviews:
            return {
                "dataset_id": dataset_id,
                "has_review": False,
                "status": "no_review",
                "message": "No ethics review on record"
            }

        all_concerns = []
        all_recommendations = []
        for review in reviews:
            all_concerns.extend(review.concerns)
            all_recommendations.extend(review.recommendations)

        return {
            "dataset_id": dataset_id,
            "has_review": True,
            "latest_status": latest_review.status.value if latest_review else None,
            "is_approved": self.check_approval(dataset_id),
            "total_reviews": len(reviews),
            "categories_reviewed": list(set(
                c.value for r in reviews for c in r.categories
            )),
            "total_concerns": len(all_concerns),
            "concerns": all_concerns,
            "recommendations": all_recommendations,
            "expires_at": latest_review.expires_at.isoformat() if (
                latest_review and latest_review.expires_at
            ) else None
        }

    def get_statistics(self) -> Dict:
        """Get ethics review statistics"""
        total_reviews = len(self._reviews)
        status_counts = {}

        for review in self._reviews.values():
            status = review.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        category_counts = {}
        for review in self._reviews.values():
            for category in review.categories:
                cat = category.value
                category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_reviews": total_reviews,
            "status_breakdown": status_counts,
            "category_breakdown": category_counts,
            "datasets_reviewed": len(self._dataset_reviews)
        }
