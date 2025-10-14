"""
Access Control and API Key Management

Implements role-based access control (RBAC), API key generation,
and permission management for research datasets.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import secrets
import hashlib
import hmac


class AccessLevel(str, Enum):
    """Access levels for datasets"""
    PUBLIC = "public"
    INSTITUTION_ONLY = "institution_only"
    RESTRICTED = "restricted"
    PRIVATE = "private"


class Permission(str, Enum):
    """Individual permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"


class Role(str, Enum):
    """User roles"""
    VIEWER = "viewer"
    RESEARCHER = "researcher"
    COLLABORATOR = "collaborator"
    OWNER = "owner"
    ADMIN = "admin"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.VIEWER: {Permission.READ},
    Role.RESEARCHER: {Permission.READ},
    Role.COLLABORATOR: {Permission.READ, Permission.WRITE, Permission.SHARE},
    Role.OWNER: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE},
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.SHARE, Permission.ADMIN},
}


@dataclass
class APIKey:
    """
    API Key for institutional access

    Attributes:
        key_id: Unique key identifier
        key_hash: Hashed API key (for security)
        institution_id: Institution identifier
        name: Human-readable key name
        permissions: Set of granted permissions
        created_at: Creation timestamp
        expires_at: Expiration timestamp
        last_used: Last usage timestamp
        is_active: Whether key is active
        rate_limit: Requests per hour
        usage_count: Total number of uses
    """
    key_id: str
    key_hash: str
    institution_id: str
    name: str
    permissions: Set[Permission] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True
    rate_limit: int = 1000  # requests per hour
    usage_count: int = 0

    def is_valid(self) -> bool:
        """Check if API key is valid"""
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def has_permission(self, permission: Permission) -> bool:
        """Check if key has specific permission"""
        return permission in self.permissions

    def record_usage(self):
        """Record API key usage"""
        self.last_used = datetime.utcnow()
        self.usage_count += 1


@dataclass
class AccessGrant:
    """
    Access grant for a user/institution to a dataset

    Attributes:
        grant_id: Unique grant identifier
        dataset_id: Dataset identifier
        user_id: User identifier (optional)
        institution_id: Institution identifier (optional)
        role: Granted role
        granted_by: ID of user who granted access
        granted_at: Grant timestamp
        expires_at: Expiration timestamp (optional)
        conditions: Additional access conditions
    """
    grant_id: str
    dataset_id: str
    user_id: Optional[str]
    institution_id: Optional[str]
    role: Role
    granted_by: str
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    conditions: Dict[str, any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if grant is still valid"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def get_permissions(self) -> Set[Permission]:
        """Get permissions for this grant"""
        return ROLE_PERMISSIONS.get(self.role, set())


class AccessControl:
    """
    Access control manager for datasets

    Handles permission checks, role assignments, and access grants.
    """

    def __init__(self):
        self._access_grants: Dict[str, List[AccessGrant]] = {}  # dataset_id -> grants
        self._user_roles: Dict[str, Dict[str, Role]] = {}  # user_id -> {dataset_id: role}

    def grant_access(
        self,
        dataset_id: str,
        user_id: Optional[str],
        institution_id: Optional[str],
        role: Role,
        granted_by: str,
        expires_in_days: Optional[int] = None
    ) -> AccessGrant:
        """
        Grant access to a dataset

        Args:
            dataset_id: Dataset identifier
            user_id: User to grant access to
            institution_id: Institution to grant access to
            role: Role to assign
            granted_by: ID of granting user
            expires_in_days: Optional expiration in days

        Returns:
            Created AccessGrant
        """
        grant_id = self._generate_grant_id(dataset_id, user_id, institution_id)

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        grant = AccessGrant(
            grant_id=grant_id,
            dataset_id=dataset_id,
            user_id=user_id,
            institution_id=institution_id,
            role=role,
            granted_by=granted_by,
            expires_at=expires_at
        )

        if dataset_id not in self._access_grants:
            self._access_grants[dataset_id] = []
        self._access_grants[dataset_id].append(grant)

        # Update user roles cache
        if user_id:
            if user_id not in self._user_roles:
                self._user_roles[user_id] = {}
            self._user_roles[user_id][dataset_id] = role

        return grant

    def revoke_access(self, grant_id: str) -> bool:
        """
        Revoke an access grant

        Args:
            grant_id: Grant identifier

        Returns:
            True if revoked, False if not found
        """
        for dataset_id, grants in self._access_grants.items():
            for grant in grants:
                if grant.grant_id == grant_id:
                    grants.remove(grant)
                    # Update user roles cache
                    if grant.user_id and grant.user_id in self._user_roles:
                        self._user_roles[grant.user_id].pop(dataset_id, None)
                    return True
        return False

    def check_permission(
        self,
        user_id: str,
        dataset_id: str,
        permission: Permission,
        access_level: AccessLevel = AccessLevel.PUBLIC
    ) -> bool:
        """
        Check if user has permission for dataset

        Args:
            user_id: User identifier
            dataset_id: Dataset identifier
            permission: Required permission
            access_level: Dataset access level

        Returns:
            True if user has permission
        """
        # Public datasets allow read access
        if access_level == AccessLevel.PUBLIC and permission == Permission.READ:
            return True

        # Check user's grants
        grants = self._access_grants.get(dataset_id, [])
        for grant in grants:
            if grant.user_id == user_id and grant.is_valid():
                if permission in grant.get_permissions():
                    return True

        return False

    def get_user_role(self, user_id: str, dataset_id: str) -> Optional[Role]:
        """Get user's role for a dataset"""
        return self._user_roles.get(user_id, {}).get(dataset_id)

    def list_user_grants(self, user_id: str) -> List[AccessGrant]:
        """List all grants for a user"""
        result = []
        for grants in self._access_grants.values():
            for grant in grants:
                if grant.user_id == user_id and grant.is_valid():
                    result.append(grant)
        return result

    def list_dataset_grants(self, dataset_id: str) -> List[AccessGrant]:
        """List all grants for a dataset"""
        grants = self._access_grants.get(dataset_id, [])
        return [g for g in grants if g.is_valid()]

    def _generate_grant_id(
        self,
        dataset_id: str,
        user_id: Optional[str],
        institution_id: Optional[str]
    ) -> str:
        """Generate unique grant ID"""
        raw_id = f"{dataset_id}_{user_id}_{institution_id}_{datetime.utcnow().timestamp()}"
        return hashlib.md5(raw_id.encode()).hexdigest()[:16]


class APIKeyManager:
    """
    Manager for API keys and institutional access

    Handles API key generation, validation, rotation, and rate limiting.
    """

    def __init__(self):
        self._api_keys: Dict[str, APIKey] = {}  # key_id -> APIKey
        self._key_lookup: Dict[str, str] = {}  # key_hash -> key_id
        self._usage_tracking: Dict[str, List[datetime]] = {}  # key_id -> request times

    def create_api_key(
        self,
        institution_id: str,
        name: str,
        permissions: Set[Permission],
        expires_in_days: Optional[int] = 365
    ) -> tuple[str, APIKey]:
        """
        Create new API key

        Args:
            institution_id: Institution identifier
            name: Key name
            permissions: Set of permissions
            expires_in_days: Expiration period in days

        Returns:
            Tuple of (plain_key, APIKey object)
        """
        # Generate secure random key
        plain_key = secrets.token_urlsafe(32)
        key_hash = self._hash_key(plain_key)
        key_id = hashlib.md5(f"{institution_id}_{name}_{datetime.utcnow()}".encode()).hexdigest()[:16]

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            institution_id=institution_id,
            name=name,
            permissions=permissions,
            expires_at=expires_at
        )

        self._api_keys[key_id] = api_key
        self._key_lookup[key_hash] = key_id
        self._usage_tracking[key_id] = []

        return plain_key, api_key

    def validate_api_key(self, plain_key: str) -> Optional[APIKey]:
        """
        Validate API key and return associated key object

        Args:
            plain_key: Plain text API key

        Returns:
            APIKey object if valid, None otherwise
        """
        key_hash = self._hash_key(plain_key)
        key_id = self._key_lookup.get(key_hash)

        if not key_id:
            return None

        api_key = self._api_keys.get(key_id)
        if not api_key or not api_key.is_valid():
            return None

        return api_key

    def check_rate_limit(self, key_id: str) -> bool:
        """
        Check if API key is within rate limit

        Args:
            key_id: Key identifier

        Returns:
            True if within limit
        """
        api_key = self._api_keys.get(key_id)
        if not api_key:
            return False

        # Clean up old requests (older than 1 hour)
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)

        recent_requests = [
            ts for ts in self._usage_tracking.get(key_id, [])
            if ts > one_hour_ago
        ]
        self._usage_tracking[key_id] = recent_requests

        return len(recent_requests) < api_key.rate_limit

    def record_request(self, key_id: str):
        """Record API request"""
        api_key = self._api_keys.get(key_id)
        if api_key:
            api_key.record_usage()
            self._usage_tracking.setdefault(key_id, []).append(datetime.utcnow())

    def revoke_api_key(self, key_id: str) -> bool:
        """
        Revoke API key

        Args:
            key_id: Key identifier

        Returns:
            True if revoked
        """
        api_key = self._api_keys.get(key_id)
        if api_key:
            api_key.is_active = False
            return True
        return False

    def rotate_api_key(self, key_id: str) -> Optional[tuple[str, APIKey]]:
        """
        Rotate API key (revoke old, create new)

        Args:
            key_id: Key identifier

        Returns:
            Tuple of (new_plain_key, new_APIKey) or None
        """
        old_key = self._api_keys.get(key_id)
        if not old_key:
            return None

        # Revoke old key
        old_key.is_active = False

        # Create new key with same settings
        return self.create_api_key(
            institution_id=old_key.institution_id,
            name=f"{old_key.name} (rotated)",
            permissions=old_key.permissions,
            expires_in_days=365
        )

    def list_institution_keys(self, institution_id: str) -> List[APIKey]:
        """List all API keys for an institution"""
        return [
            key for key in self._api_keys.values()
            if key.institution_id == institution_id
        ]

    def _hash_key(self, plain_key: str) -> str:
        """Hash API key using SHA-256"""
        return hashlib.sha256(plain_key.encode()).hexdigest()
