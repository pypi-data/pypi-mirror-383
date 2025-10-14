"""
Result Sharing

Manages sharing of research results, artifacts, and insights
between institutions and collaborators.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SharingPermission(str, Enum):
    """Permission levels for shared content"""
    VIEW = "view"
    DOWNLOAD = "download"
    COMMENT = "comment"
    EDIT = "edit"


class ContentType(str, Enum):
    """Types of shareable content"""
    EXPERIMENT = "experiment"
    DATASET = "dataset"
    MODEL = "model"
    NOTEBOOK = "notebook"
    REPORT = "report"
    CODE = "code"


@dataclass
class SharedContent:
    """
    Shared research content

    Attributes:
        share_id: Unique share identifier
        content_type: Type of content
        content_id: ID of the shared content
        owner_id: Owner user ID
        workspace_id: Associated workspace (optional)
        title: Content title
        description: Content description
        shared_with: Set of user/institution IDs with access
        permissions: Permission level per user/institution
        created_at: When shared
        expires_at: Expiration timestamp (optional)
        download_count: Number of downloads
        view_count: Number of views
        metadata: Additional metadata
    """
    share_id: str
    content_type: ContentType
    content_id: str
    owner_id: str
    workspace_id: Optional[str]
    title: str
    description: str
    shared_with: Set[str] = field(default_factory=set)
    permissions: Dict[str, SharingPermission] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    download_count: int = 0
    view_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if share is still valid"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def has_permission(self, user_id: str, permission: SharingPermission) -> bool:
        """Check if user has specific permission"""
        if user_id not in self.shared_with:
            return False

        user_perm = self.permissions.get(user_id, SharingPermission.VIEW)
        perm_hierarchy = {
            SharingPermission.VIEW: 1,
            SharingPermission.DOWNLOAD: 2,
            SharingPermission.COMMENT: 3,
            SharingPermission.EDIT: 4
        }

        return perm_hierarchy.get(user_perm, 0) >= perm_hierarchy.get(permission, 0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "share_id": self.share_id,
            "content_type": self.content_type.value,
            "content_id": self.content_id,
            "owner_id": self.owner_id,
            "workspace_id": self.workspace_id,
            "title": self.title,
            "description": self.description,
            "shared_with": list(self.shared_with),
            "permissions": {k: v.value for k, v in self.permissions.items()},
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "download_count": self.download_count,
            "view_count": self.view_count,
            "metadata": self.metadata
        }


class ResultSharing:
    """
    Manager for result and artifact sharing

    Handles sharing of research outputs between institutions and collaborators.
    """

    def __init__(self):
        self._shares: Dict[str, SharedContent] = {}
        self._user_shares: Dict[str, List[str]] = {}  # user_id -> share_ids
        self._content_shares: Dict[str, List[str]] = {}  # content_id -> share_ids

    def share_content(
        self,
        content_type: ContentType,
        content_id: str,
        owner_id: str,
        title: str,
        description: str,
        shared_with: List[str],
        permissions: Optional[Dict[str, SharingPermission]] = None,
        workspace_id: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> SharedContent:
        """
        Share content with users/institutions

        Args:
            content_type: Type of content
            content_id: Content identifier
            owner_id: Owner user ID
            title: Content title
            description: Description
            shared_with: List of user/institution IDs
            permissions: Permission levels per user/institution
            workspace_id: Associated workspace
            expires_in_days: Expiration period in days

        Returns:
            Created SharedContent object
        """
        import hashlib
        from datetime import timedelta

        share_id = hashlib.md5(
            f"{content_id}_{owner_id}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Set default permissions
        if not permissions:
            permissions = {user: SharingPermission.VIEW for user in shared_with}

        share = SharedContent(
            share_id=share_id,
            content_type=content_type,
            content_id=content_id,
            owner_id=owner_id,
            workspace_id=workspace_id,
            title=title,
            description=description,
            shared_with=set(shared_with),
            permissions=permissions,
            expires_at=expires_at
        )

        self._shares[share_id] = share

        # Update indices
        for user_id in shared_with:
            if user_id not in self._user_shares:
                self._user_shares[user_id] = []
            self._user_shares[user_id].append(share_id)

        if content_id not in self._content_shares:
            self._content_shares[content_id] = []
        self._content_shares[content_id].append(share_id)

        return share

    def get_share(self, share_id: str) -> Optional[SharedContent]:
        """Get share by ID"""
        return self._shares.get(share_id)

    def access_content(
        self,
        share_id: str,
        user_id: str,
        permission: SharingPermission
    ) -> bool:
        """
        Check if user can access content with permission

        Args:
            share_id: Share identifier
            user_id: User requesting access
            permission: Required permission

        Returns:
            True if access granted
        """
        share = self._shares.get(share_id)
        if not share or not share.is_valid():
            return False

        # Owner always has access
        if user_id == share.owner_id:
            return True

        return share.has_permission(user_id, permission)

    def record_view(self, share_id: str, user_id: str) -> bool:
        """Record content view"""
        if self.access_content(share_id, user_id, SharingPermission.VIEW):
            share = self._shares[share_id]
            share.view_count += 1
            return True
        return False

    def record_download(self, share_id: str, user_id: str) -> bool:
        """Record content download"""
        if self.access_content(share_id, user_id, SharingPermission.DOWNLOAD):
            share = self._shares[share_id]
            share.download_count += 1
            return True
        return False

    def update_permissions(
        self,
        share_id: str,
        user_id: str,
        new_permission: SharingPermission,
        updated_by: str
    ) -> bool:
        """
        Update user's permission

        Args:
            share_id: Share identifier
            user_id: User to update
            new_permission: New permission level
            updated_by: User performing update

        Returns:
            True if updated
        """
        share = self._shares.get(share_id)
        if not share:
            return False

        # Only owner can update permissions
        if updated_by != share.owner_id:
            raise PermissionError("Only owner can update permissions")

        if user_id in share.shared_with:
            share.permissions[user_id] = new_permission
            return True
        return False

    def add_users(
        self,
        share_id: str,
        user_ids: List[str],
        permission: SharingPermission,
        added_by: str
    ) -> bool:
        """Add users to share"""
        share = self._shares.get(share_id)
        if not share:
            return False

        # Only owner can add users
        if added_by != share.owner_id:
            raise PermissionError("Only owner can add users")

        for user_id in user_ids:
            share.shared_with.add(user_id)
            share.permissions[user_id] = permission

            # Update user index
            if user_id not in self._user_shares:
                self._user_shares[user_id] = []
            if share_id not in self._user_shares[user_id]:
                self._user_shares[user_id].append(share_id)

        return True

    def remove_users(
        self,
        share_id: str,
        user_ids: List[str],
        removed_by: str
    ) -> bool:
        """Remove users from share"""
        share = self._shares.get(share_id)
        if not share:
            return False

        # Only owner can remove users
        if removed_by != share.owner_id:
            raise PermissionError("Only owner can remove users")

        for user_id in user_ids:
            share.shared_with.discard(user_id)
            share.permissions.pop(user_id, None)

            # Update user index
            if user_id in self._user_shares:
                self._user_shares[user_id].remove(share_id)

        return True

    def list_user_shares(
        self,
        user_id: str,
        content_type: Optional[ContentType] = None
    ) -> List[SharedContent]:
        """List all shares accessible by user"""
        share_ids = self._user_shares.get(user_id, [])
        shares = [self._shares[sid] for sid in share_ids if sid in self._shares]

        # Filter by content type
        if content_type:
            shares = [s for s in shares if s.content_type == content_type]

        # Filter expired shares
        shares = [s for s in shares if s.is_valid()]

        return shares

    def list_content_shares(self, content_id: str) -> List[SharedContent]:
        """List all shares for specific content"""
        share_ids = self._content_shares.get(content_id, [])
        return [self._shares[sid] for sid in share_ids if sid in self._shares]

    def revoke_share(self, share_id: str, revoked_by: str) -> bool:
        """
        Revoke share completely

        Args:
            share_id: Share identifier
            revoked_by: User performing revocation

        Returns:
            True if revoked
        """
        share = self._shares.get(share_id)
        if not share:
            return False

        # Only owner can revoke
        if revoked_by != share.owner_id:
            raise PermissionError("Only owner can revoke share")

        # Remove from user indices
        for user_id in share.shared_with:
            if user_id in self._user_shares:
                self._user_shares[user_id].remove(share_id)

        # Remove from content index
        if share.content_id in self._content_shares:
            self._content_shares[share.content_id].remove(share_id)

        del self._shares[share_id]
        return True

    def get_share_statistics(self, share_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a share"""
        share = self._shares.get(share_id)
        if not share:
            return None

        return {
            "share_id": share_id,
            "title": share.title,
            "content_type": share.content_type.value,
            "num_users": len(share.shared_with),
            "view_count": share.view_count,
            "download_count": share.download_count,
            "created_at": share.created_at.isoformat(),
            "expires_at": share.expires_at.isoformat() if share.expires_at else None,
            "is_valid": share.is_valid()
        }
