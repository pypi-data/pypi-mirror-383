"""
Collaboration Workspace

Manages collaborative research workspaces for institutions
to work together on datasets and experiments.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class WorkspaceRole(str, Enum):
    """Roles within a workspace"""
    MEMBER = "member"
    CONTRIBUTOR = "contributor"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass
class CollaborationWorkspace:
    """
    Collaborative research workspace

    Attributes:
        workspace_id: Unique workspace identifier
        name: Workspace name
        description: Workspace description
        created_by: Creator user ID
        created_at: Creation timestamp
        institutions: List of participating institutions
        datasets: List of shared dataset IDs
        members: Dictionary of member_id -> role
        settings: Workspace settings
        metadata: Additional metadata
    """
    workspace_id: str
    name: str
    description: str
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    institutions: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    members: Dict[str, WorkspaceRole] = field(default_factory=dict)
    settings: Dict[str, any] = field(default_factory=dict)
    metadata: Dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary"""
        return {
            "workspace_id": self.workspace_id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "institutions": self.institutions,
            "datasets": self.datasets,
            "members": {k: v.value for k, v in self.members.items()},
            "settings": self.settings,
            "metadata": self.metadata
        }


class WorkspaceManager:
    """
    Manager for collaboration workspaces

    Handles workspace creation, member management, and resource sharing.
    """

    def __init__(self):
        self._workspaces: Dict[str, CollaborationWorkspace] = {}
        self._user_workspaces: Dict[str, List[str]] = {}  # user_id -> workspace_ids

    def create_workspace(
        self,
        name: str,
        description: str,
        created_by: str,
        institutions: Optional[List[str]] = None
    ) -> CollaborationWorkspace:
        """
        Create new collaboration workspace

        Args:
            name: Workspace name
            description: Workspace description
            created_by: Creator user ID
            institutions: List of institutions

        Returns:
            Created CollaborationWorkspace
        """
        import hashlib

        workspace_id = hashlib.md5(
            f"{name}_{created_by}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        workspace = CollaborationWorkspace(
            workspace_id=workspace_id,
            name=name,
            description=description,
            created_by=created_by,
            institutions=institutions or []
        )

        # Add creator as owner
        workspace.members[created_by] = WorkspaceRole.OWNER

        self._workspaces[workspace_id] = workspace

        # Add to user index
        if created_by not in self._user_workspaces:
            self._user_workspaces[created_by] = []
        self._user_workspaces[created_by].append(workspace_id)

        return workspace

    def get_workspace(self, workspace_id: str) -> Optional[CollaborationWorkspace]:
        """Get workspace by ID"""
        return self._workspaces.get(workspace_id)

    def add_member(
        self,
        workspace_id: str,
        user_id: str,
        role: WorkspaceRole,
        added_by: str
    ) -> bool:
        """
        Add member to workspace

        Args:
            workspace_id: Workspace identifier
            user_id: User to add
            role: Role to assign
            added_by: User performing the action

        Returns:
            True if added successfully

        Raises:
            PermissionError: If user lacks permission
        """
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return False

        # Check if adder has permission
        adder_role = workspace.members.get(added_by)
        if not adder_role or adder_role not in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER]:
            raise PermissionError(f"User {added_by} cannot add members to workspace")

        workspace.members[user_id] = role

        # Add to user index
        if user_id not in self._user_workspaces:
            self._user_workspaces[user_id] = []
        if workspace_id not in self._user_workspaces[user_id]:
            self._user_workspaces[user_id].append(workspace_id)

        return True

    def remove_member(
        self,
        workspace_id: str,
        user_id: str,
        removed_by: str
    ) -> bool:
        """
        Remove member from workspace

        Args:
            workspace_id: Workspace identifier
            user_id: User to remove
            removed_by: User performing the action

        Returns:
            True if removed successfully

        Raises:
            PermissionError: If user lacks permission
        """
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return False

        # Check if remover has permission
        remover_role = workspace.members.get(removed_by)
        if not remover_role or remover_role not in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER]:
            raise PermissionError(f"User {removed_by} cannot remove members from workspace")

        # Cannot remove owner
        if workspace.members.get(user_id) == WorkspaceRole.OWNER:
            raise PermissionError("Cannot remove workspace owner")

        if user_id in workspace.members:
            del workspace.members[user_id]

            # Update user index
            if user_id in self._user_workspaces:
                self._user_workspaces[user_id].remove(workspace_id)

            return True
        return False

    def update_member_role(
        self,
        workspace_id: str,
        user_id: str,
        new_role: WorkspaceRole,
        updated_by: str
    ) -> bool:
        """
        Update member's role

        Args:
            workspace_id: Workspace identifier
            user_id: User to update
            new_role: New role
            updated_by: User performing the action

        Returns:
            True if updated successfully
        """
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return False

        # Check permission
        updater_role = workspace.members.get(updated_by)
        if not updater_role or updater_role not in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER]:
            raise PermissionError(f"User {updated_by} cannot update member roles")

        if user_id in workspace.members:
            workspace.members[user_id] = new_role
            return True
        return False

    def add_dataset(
        self,
        workspace_id: str,
        dataset_id: str,
        added_by: str
    ) -> bool:
        """
        Add dataset to workspace

        Args:
            workspace_id: Workspace identifier
            dataset_id: Dataset to add
            added_by: User performing the action

        Returns:
            True if added successfully
        """
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return False

        # Check permission
        role = workspace.members.get(added_by)
        if not role or role == WorkspaceRole.MEMBER:
            raise PermissionError(f"User {added_by} cannot add datasets to workspace")

        if dataset_id not in workspace.datasets:
            workspace.datasets.append(dataset_id)
            return True
        return False

    def remove_dataset(
        self,
        workspace_id: str,
        dataset_id: str,
        removed_by: str
    ) -> bool:
        """Remove dataset from workspace"""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return False

        # Check permission
        role = workspace.members.get(removed_by)
        if not role or role == WorkspaceRole.MEMBER:
            raise PermissionError(f"User {removed_by} cannot remove datasets from workspace")

        if dataset_id in workspace.datasets:
            workspace.datasets.remove(dataset_id)
            return True
        return False

    def list_user_workspaces(self, user_id: str) -> List[CollaborationWorkspace]:
        """List all workspaces for a user"""
        workspace_ids = self._user_workspaces.get(user_id, [])
        return [self._workspaces[wid] for wid in workspace_ids if wid in self._workspaces]

    def list_institution_workspaces(self, institution: str) -> List[CollaborationWorkspace]:
        """List all workspaces for an institution"""
        return [
            ws for ws in self._workspaces.values()
            if institution in ws.institutions
        ]

    def get_workspace_members(self, workspace_id: str) -> Dict[str, WorkspaceRole]:
        """Get all members and their roles"""
        workspace = self._workspaces.get(workspace_id)
        return workspace.members if workspace else {}

    def get_workspace_datasets(self, workspace_id: str) -> List[str]:
        """Get all datasets in workspace"""
        workspace = self._workspaces.get(workspace_id)
        return workspace.datasets if workspace else []

    def delete_workspace(self, workspace_id: str, deleted_by: str) -> bool:
        """
        Delete workspace

        Args:
            workspace_id: Workspace identifier
            deleted_by: User performing deletion

        Returns:
            True if deleted

        Raises:
            PermissionError: If user is not owner
        """
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return False

        # Only owner can delete
        if workspace.members.get(deleted_by) != WorkspaceRole.OWNER:
            raise PermissionError("Only workspace owner can delete workspace")

        # Remove from user indices
        for user_id in workspace.members.keys():
            if user_id in self._user_workspaces:
                self._user_workspaces[user_id].remove(workspace_id)

        del self._workspaces[workspace_id]
        return True

    def get_workspace_statistics(self, workspace_id: str) -> Optional[Dict[str, any]]:
        """Get workspace statistics"""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return None

        return {
            "workspace_id": workspace_id,
            "name": workspace.name,
            "num_members": len(workspace.members),
            "num_institutions": len(workspace.institutions),
            "num_datasets": len(workspace.datasets),
            "created_at": workspace.created_at.isoformat(),
            "institutions": workspace.institutions
        }
