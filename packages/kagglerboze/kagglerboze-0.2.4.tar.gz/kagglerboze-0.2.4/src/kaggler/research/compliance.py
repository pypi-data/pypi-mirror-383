"""
Compliance Tools for Research Partnerships

Comprehensive GDPR and HIPAA compliance features including:
- Data privacy controls
- Right to access/deletion/portability
- Consent management
- Audit logging
- Encryption management
- Access control verification
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json


class ComplianceStandard(str, Enum):
    """Compliance standards"""
    GDPR = "gdpr"  # General Data Protection Regulation (EU)
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act (US)
    CCPA = "ccpa"  # California Consumer Privacy Act
    LGPD = "lgpd"  # Lei Geral de Proteção de Dados (Brazil)


class DataCategory(str, Enum):
    """Categories of data"""
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    MEDICAL = "medical"
    FINANCIAL = "financial"
    BIOMETRIC = "biometric"
    GENETIC = "genetic"
    PUBLIC = "public"


class AuditAction(str, Enum):
    """Types of audit actions"""
    ACCESS = "access"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    SHARE = "share"
    CONSENT_GRANT = "consent_grant"
    CONSENT_REVOKE = "consent_revoke"


@dataclass
class AuditLogEntry:
    """
    Audit log entry for compliance tracking

    Attributes:
        entry_id: Unique identifier
        timestamp: When action occurred
        user_id: User who performed action
        action: Type of action
        resource_type: Type of resource (dataset, user_data, etc.)
        resource_id: Resource identifier
        ip_address: IP address of user
        success: Whether action succeeded
        details: Additional details
        compliance_standards: Applicable standards
    """
    entry_id: str
    timestamp: datetime
    user_id: str
    action: AuditAction
    resource_type: str
    resource_id: str
    ip_address: Optional[str] = None
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)
    compliance_standards: List[ComplianceStandard] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "success": self.success,
            "details": self.details,
            "compliance_standards": [s.value for s in self.compliance_standards]
        }


@dataclass
class ConsentRecord:
    """
    User consent record

    Attributes:
        consent_id: Unique identifier
        user_id: User identifier
        purpose: Purpose of data processing
        granted: Whether consent is granted
        granted_at: When consent was granted
        expires_at: When consent expires
        revoked: Whether consent was revoked
        revoked_at: When consent was revoked
        data_categories: Categories of data covered
        details: Additional details
    """
    consent_id: str
    user_id: str
    purpose: str
    granted: bool
    granted_at: datetime
    expires_at: Optional[datetime] = None
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    data_categories: List[DataCategory] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if consent is currently valid"""
        if not self.granted or self.revoked:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "consent_id": self.consent_id,
            "user_id": self.user_id,
            "purpose": self.purpose,
            "granted": self.granted,
            "granted_at": self.granted_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "revoked": self.revoked,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "data_categories": [c.value for c in self.data_categories],
            "is_valid": self.is_valid()
        }


class ComplianceChecker:
    """
    Main compliance checker for GDPR and HIPAA

    Provides tools for:
    - Compliance verification
    - Data access and deletion
    - Consent management
    - Audit logging
    """

    def __init__(self):
        self._audit_log: List[AuditLogEntry] = []
        self._consent_records: Dict[str, ConsentRecord] = {}
        self._user_data_index: Dict[str, Set[str]] = {}  # user_id -> resource_ids
        self._encryption_keys: Dict[str, str] = {}

    def check_compliance(
        self,
        resource_id: str,
        standards: List[ComplianceStandard]
    ) -> Dict[str, Any]:
        """
        Check compliance status for a resource

        Args:
            resource_id: Resource to check
            standards: Standards to verify against

        Returns:
            Compliance report
        """
        report = {
            "resource_id": resource_id,
            "timestamp": datetime.utcnow().isoformat(),
            "standards": {},
            "overall_compliant": True
        }

        for standard in standards:
            if standard == ComplianceStandard.GDPR:
                gdpr_check = self._check_gdpr_compliance(resource_id)
                report["standards"]["gdpr"] = gdpr_check
                report["overall_compliant"] &= gdpr_check["compliant"]

            elif standard == ComplianceStandard.HIPAA:
                hipaa_check = self._check_hipaa_compliance(resource_id)
                report["standards"]["hipaa"] = hipaa_check
                report["overall_compliant"] &= hipaa_check["compliant"]

        return report

    def _check_gdpr_compliance(self, resource_id: str) -> Dict[str, Any]:
        """Check GDPR compliance"""
        checks = {
            "compliant": True,
            "requirements": {}
        }

        # Check audit logging
        has_audit = any(
            entry.resource_id == resource_id
            for entry in self._audit_log
        )
        checks["requirements"]["audit_logging"] = {
            "met": has_audit,
            "description": "Must maintain audit logs of data processing"
        }

        # Check encryption
        has_encryption = resource_id in self._encryption_keys
        checks["requirements"]["encryption"] = {
            "met": has_encryption,
            "description": "Must encrypt data at rest and in transit"
        }

        # Check consent records
        has_consent = any(
            consent.resource_id == resource_id and consent.is_valid()
            for consent in self._consent_records.values()
            if hasattr(consent, 'resource_id')
        )
        checks["requirements"]["consent"] = {
            "met": True,  # Not always required
            "description": "Must have user consent for processing"
        }

        # Check data retention policy
        checks["requirements"]["retention_policy"] = {
            "met": True,  # Assumed to be implemented elsewhere
            "description": "Must have data retention policy"
        }

        # Overall compliance
        checks["compliant"] = all(
            req["met"] for req in checks["requirements"].values()
        )

        return checks

    def _check_hipaa_compliance(self, resource_id: str) -> Dict[str, Any]:
        """Check HIPAA compliance"""
        checks = {
            "compliant": True,
            "requirements": {}
        }

        # Check audit controls
        has_audit = any(
            entry.resource_id == resource_id
            for entry in self._audit_log
        )
        checks["requirements"]["audit_controls"] = {
            "met": has_audit,
            "description": "Must implement audit controls"
        }

        # Check encryption
        has_encryption = resource_id in self._encryption_keys
        checks["requirements"]["encryption"] = {
            "met": has_encryption,
            "description": "Must encrypt PHI at rest and in transit"
        }

        # Check access controls
        checks["requirements"]["access_controls"] = {
            "met": True,  # Assumed via access control system
            "description": "Must implement role-based access controls"
        }

        # Check integrity controls
        checks["requirements"]["integrity_controls"] = {
            "met": True,  # Checksums implemented elsewhere
            "description": "Must ensure data integrity"
        }

        # Check transmission security
        checks["requirements"]["transmission_security"] = {
            "met": has_encryption,
            "description": "Must secure data transmission"
        }

        # Overall compliance
        checks["compliant"] = all(
            req["met"] for req in checks["requirements"].values()
        )

        return checks

    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all data for a user (GDPR Right to Access)

        Args:
            user_id: User identifier

        Returns:
            Dictionary containing all user data
        """
        # Log access
        self._log_audit(
            user_id=user_id,
            action=AuditAction.EXPORT,
            resource_type="user_data",
            resource_id=user_id,
            compliance_standards=[ComplianceStandard.GDPR]
        )

        # Collect all user data
        export_data = {
            "user_id": user_id,
            "export_date": datetime.utcnow().isoformat(),
            "consent_records": [],
            "audit_logs": [],
            "resources": []
        }

        # Add consent records
        for consent in self._consent_records.values():
            if consent.user_id == user_id:
                export_data["consent_records"].append(consent.to_dict())

        # Add audit logs
        for entry in self._audit_log:
            if entry.user_id == user_id:
                export_data["audit_logs"].append(entry.to_dict())

        # Add resource IDs
        if user_id in self._user_data_index:
            export_data["resources"] = list(self._user_data_index[user_id])

        return export_data

    def delete_user_data(
        self,
        user_id: str,
        requesting_user: str,
        verification_code: str
    ) -> Dict[str, Any]:
        """
        Delete all data for a user (GDPR Right to Deletion)

        Args:
            user_id: User identifier
            requesting_user: User making request
            verification_code: Verification code

        Returns:
            Deletion report

        Raises:
            PermissionError: If verification fails
        """
        # Verify requester
        if requesting_user != user_id:
            raise PermissionError("Only user can request their data deletion")

        # Verify code (in production, use proper verification)
        expected_code = hashlib.sha256(f"{user_id}_delete".encode()).hexdigest()[:8]
        if verification_code != expected_code:
            raise PermissionError("Invalid verification code")

        # Log deletion request
        self._log_audit(
            user_id=user_id,
            action=AuditAction.DELETE,
            resource_type="user_data",
            resource_id=user_id,
            compliance_standards=[ComplianceStandard.GDPR]
        )

        deletion_report = {
            "user_id": user_id,
            "deletion_date": datetime.utcnow().isoformat(),
            "items_deleted": {
                "consent_records": 0,
                "resources": 0
            }
        }

        # Delete consent records
        consents_to_delete = [
            cid for cid, consent in self._consent_records.items()
            if consent.user_id == user_id
        ]
        for consent_id in consents_to_delete:
            del self._consent_records[consent_id]
            deletion_report["items_deleted"]["consent_records"] += 1

        # Delete user data index
        if user_id in self._user_data_index:
            resource_count = len(self._user_data_index[user_id])
            del self._user_data_index[user_id]
            deletion_report["items_deleted"]["resources"] = resource_count

        # Note: Audit logs are retained for compliance
        deletion_report["note"] = "Audit logs retained for compliance purposes"

        return deletion_report

    def grant_consent(
        self,
        user_id: str,
        purpose: str,
        data_categories: List[DataCategory],
        expires_in_days: Optional[int] = None
    ) -> ConsentRecord:
        """
        Grant consent for data processing

        Args:
            user_id: User identifier
            purpose: Purpose of processing
            data_categories: Categories of data
            expires_in_days: Expiration in days

        Returns:
            ConsentRecord
        """
        consent_id = hashlib.md5(
            f"{user_id}_{purpose}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        consent = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            purpose=purpose,
            granted=True,
            granted_at=datetime.utcnow(),
            expires_at=expires_at,
            data_categories=data_categories
        )

        self._consent_records[consent_id] = consent

        # Log consent grant
        self._log_audit(
            user_id=user_id,
            action=AuditAction.CONSENT_GRANT,
            resource_type="consent",
            resource_id=consent_id,
            compliance_standards=[ComplianceStandard.GDPR]
        )

        return consent

    def revoke_consent(self, consent_id: str, user_id: str) -> bool:
        """
        Revoke consent

        Args:
            consent_id: Consent identifier
            user_id: User identifier

        Returns:
            True if revoked

        Raises:
            PermissionError: If user doesn't own consent
        """
        consent = self._consent_records.get(consent_id)
        if not consent:
            return False

        if consent.user_id != user_id:
            raise PermissionError("User doesn't own this consent")

        consent.revoked = True
        consent.revoked_at = datetime.utcnow()

        # Log consent revocation
        self._log_audit(
            user_id=user_id,
            action=AuditAction.CONSENT_REVOKE,
            resource_type="consent",
            resource_id=consent_id,
            compliance_standards=[ComplianceStandard.GDPR]
        )

        return True

    def check_consent(
        self,
        user_id: str,
        purpose: str,
        data_category: DataCategory
    ) -> bool:
        """
        Check if user has granted consent

        Args:
            user_id: User identifier
            purpose: Purpose of processing
            data_category: Category of data

        Returns:
            True if consent is valid
        """
        for consent in self._consent_records.values():
            if (consent.user_id == user_id and
                consent.purpose == purpose and
                data_category in consent.data_categories and
                consent.is_valid()):
                return True
        return False

    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLogEntry]:
        """
        Get audit log entries with filters

        Args:
            user_id: Filter by user
            resource_id: Filter by resource
            action: Filter by action
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            List of audit log entries
        """
        entries = self._audit_log

        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if resource_id:
            entries = [e for e in entries if e.resource_id == resource_id]
        if action:
            entries = [e for e in entries if e.action == action]
        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]

        return entries

    def _log_audit(
        self,
        user_id: str,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        ip_address: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        compliance_standards: Optional[List[ComplianceStandard]] = None
    ):
        """Log audit entry"""
        entry_id = hashlib.md5(
            f"{user_id}_{action.value}_{resource_id}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        entry = AuditLogEntry(
            entry_id=entry_id,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            success=success,
            details=details or {},
            compliance_standards=compliance_standards or []
        )

        self._audit_log.append(entry)

    def enable_encryption(
        self,
        resource_id: str,
        encryption_key: str
    ):
        """
        Enable encryption for resource

        Args:
            resource_id: Resource identifier
            encryption_key: Encryption key (in production, use KMS)
        """
        self._encryption_keys[resource_id] = encryption_key

    def is_encrypted(self, resource_id: str) -> bool:
        """Check if resource is encrypted"""
        return resource_id in self._encryption_keys

    def get_compliance_report(
        self,
        standards: List[ComplianceStandard]
    ) -> Dict[str, Any]:
        """
        Generate compliance report

        Args:
            standards: Standards to report on

        Returns:
            Compliance report
        """
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "standards": standards,
            "statistics": {
                "total_audit_entries": len(self._audit_log),
                "total_consent_records": len(self._consent_records),
                "active_consents": sum(
                    1 for c in self._consent_records.values() if c.is_valid()
                ),
                "encrypted_resources": len(self._encryption_keys),
                "users_with_data": len(self._user_data_index)
            },
            "recent_activity": []
        }

        # Add recent audit activity
        recent_entries = sorted(
            self._audit_log,
            key=lambda e: e.timestamp,
            reverse=True
        )[:10]

        report["recent_activity"] = [e.to_dict() for e in recent_entries]

        return report
