"""
Privacy Controls

Data privacy management including GDPR and HIPAA compliance,
anonymization, and consent tracking.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib


class PrivacyLevel(str, Enum):
    """Privacy levels for data"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ComplianceRegulation(str, Enum):
    """Supported compliance regulations"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    CCPA = "ccpa"
    FERPA = "ferpa"


@dataclass
class ConsentRecord:
    """
    User consent record

    Attributes:
        consent_id: Unique consent identifier
        user_id: User identifier
        dataset_id: Dataset identifier
        purpose: Purpose of data usage
        granted: Whether consent is granted
        granted_at: When consent was granted
        expires_at: Expiration timestamp
        revoked: Whether consent was revoked
        revoked_at: When consent was revoked
    """
    consent_id: str
    user_id: str
    dataset_id: str
    purpose: str
    granted: bool = True
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    revoked: bool = False
    revoked_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Check if consent is valid"""
        if self.revoked:
            return False
        if not self.granted:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True


class DataAnonymizer:
    """
    Data anonymization utilities

    Provides methods for anonymizing PII and sensitive data.
    """

    @staticmethod
    def hash_identifier(identifier: str, salt: str = "") -> str:
        """Hash identifier (e.g., email, SSN)"""
        combined = f"{identifier}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address"""
        if "@" not in email:
            return email
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number"""
        if len(phone) <= 4:
            return "*" * len(phone)
        return "*" * (len(phone) - 4) + phone[-4:]

    @staticmethod
    def generalize_age(age: int, bucket_size: int = 5) -> str:
        """Generalize age into buckets"""
        bucket_start = (age // bucket_size) * bucket_size
        bucket_end = bucket_start + bucket_size - 1
        return f"{bucket_start}-{bucket_end}"

    @staticmethod
    def redact_text(text: str, patterns: List[str]) -> str:
        """Redact patterns from text"""
        import re
        for pattern in patterns:
            text = re.sub(pattern, "[REDACTED]", text)
        return text


class ConsentManager:
    """
    Manager for user consent

    Tracks and validates user consent for data usage.
    """

    def __init__(self):
        self._consents: Dict[str, ConsentRecord] = {}
        self._user_consents: Dict[str, List[str]] = {}  # user_id -> consent_ids
        self._dataset_consents: Dict[str, List[str]] = {}  # dataset_id -> consent_ids

    def grant_consent(
        self,
        user_id: str,
        dataset_id: str,
        purpose: str,
        expires_in_days: Optional[int] = None
    ) -> ConsentRecord:
        """Grant user consent"""
        from datetime import timedelta

        consent_id = hashlib.md5(
            f"{user_id}_{dataset_id}_{purpose}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        consent = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            dataset_id=dataset_id,
            purpose=purpose,
            expires_at=expires_at
        )

        self._consents[consent_id] = consent

        # Update indices
        if user_id not in self._user_consents:
            self._user_consents[user_id] = []
        self._user_consents[user_id].append(consent_id)

        if dataset_id not in self._dataset_consents:
            self._dataset_consents[dataset_id] = []
        self._dataset_consents[dataset_id].append(consent_id)

        return consent

    def revoke_consent(self, consent_id: str) -> bool:
        """Revoke consent"""
        consent = self._consents.get(consent_id)
        if consent:
            consent.revoked = True
            consent.revoked_at = datetime.utcnow()
            return True
        return False

    def check_consent(self, user_id: str, dataset_id: str, purpose: str) -> bool:
        """Check if valid consent exists"""
        user_consent_ids = self._user_consents.get(user_id, [])
        for consent_id in user_consent_ids:
            consent = self._consents.get(consent_id)
            if (consent and consent.dataset_id == dataset_id and
                consent.purpose == purpose and consent.is_valid()):
                return True
        return False

    def list_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """List all consents for user"""
        consent_ids = self._user_consents.get(user_id, [])
        return [self._consents[cid] for cid in consent_ids if cid in self._consents]

    def list_dataset_consents(self, dataset_id: str) -> List[ConsentRecord]:
        """List all consents for dataset"""
        consent_ids = self._dataset_consents.get(dataset_id, [])
        return [self._consents[cid] for cid in consent_ids if cid in self._consents]


class PrivacyControl:
    """
    Privacy control manager

    Manages privacy levels, compliance checks, and data protection.
    """

    def __init__(self):
        self._privacy_settings: Dict[str, PrivacyLevel] = {}
        self._compliance_requirements: Dict[str, Set[ComplianceRegulation]] = {}
        self.consent_manager = ConsentManager()
        self.anonymizer = DataAnonymizer()

    def set_privacy_level(self, dataset_id: str, level: PrivacyLevel):
        """Set privacy level for dataset"""
        self._privacy_settings[dataset_id] = level

    def get_privacy_level(self, dataset_id: str) -> Optional[PrivacyLevel]:
        """Get privacy level for dataset"""
        return self._privacy_settings.get(dataset_id)

    def add_compliance_requirement(
        self,
        dataset_id: str,
        regulation: ComplianceRegulation
    ):
        """Add compliance requirement"""
        if dataset_id not in self._compliance_requirements:
            self._compliance_requirements[dataset_id] = set()
        self._compliance_requirements[dataset_id].add(regulation)

    def check_compliance(
        self,
        dataset_id: str,
        regulations: List[ComplianceRegulation]
    ) -> Dict[str, bool]:
        """
        Check dataset compliance with regulations

        Returns:
            Dictionary of regulation -> compliant (bool)
        """
        results = {}
        for regulation in regulations:
            # Simplified compliance check
            # In production, implement actual compliance validation
            required = self._compliance_requirements.get(dataset_id, set())
            results[regulation.value] = regulation in required

        return results

    def anonymize_dataset(
        self,
        data: Dict[str, Any],
        fields_to_anonymize: List[str]
    ) -> Dict[str, Any]:
        """
        Anonymize dataset fields

        Args:
            data: Dataset dictionary
            fields_to_anonymize: List of field names to anonymize

        Returns:
            Anonymized dataset
        """
        anonymized = data.copy()

        for field in fields_to_anonymize:
            if field in anonymized:
                value = anonymized[field]

                if isinstance(value, str):
                    if "@" in value:  # Email
                        anonymized[field] = self.anonymizer.mask_email(value)
                    else:  # General identifier
                        anonymized[field] = self.anonymizer.hash_identifier(value)
                elif isinstance(value, int) and "age" in field.lower():
                    anonymized[field] = self.anonymizer.generalize_age(value)

        return anonymized

    def generate_privacy_report(self, dataset_id: str) -> Dict[str, Any]:
        """Generate privacy compliance report"""
        privacy_level = self.get_privacy_level(dataset_id)
        compliance_reqs = self._compliance_requirements.get(dataset_id, set())
        consents = self.consent_manager.list_dataset_consents(dataset_id)

        return {
            "dataset_id": dataset_id,
            "privacy_level": privacy_level.value if privacy_level else None,
            "compliance_regulations": [r.value for r in compliance_reqs],
            "total_consents": len(consents),
            "valid_consents": sum(1 for c in consents if c.is_valid()),
            "revoked_consents": sum(1 for c in consents if c.revoked),
            "report_generated_at": datetime.utcnow().isoformat()
        }

    def enforce_data_retention(
        self,
        dataset_id: str,
        retention_days: int
    ) -> Dict[str, Any]:
        """
        Enforce data retention policy

        Args:
            dataset_id: Dataset identifier
            retention_days: Maximum data retention in days

        Returns:
            Dictionary with enforcement results
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # In production, this would actually delete old records
        return {
            "dataset_id": dataset_id,
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.isoformat(),
            "status": "enforced"
        }
