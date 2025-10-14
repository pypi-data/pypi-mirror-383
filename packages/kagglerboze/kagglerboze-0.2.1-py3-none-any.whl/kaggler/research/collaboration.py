"""
Collaboration Workspace

Comprehensive collaboration features for joint research projects,
including workspace management, experiment tracking, discussions,
and file sharing.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from kaggler.research.workspace import (
    CollaborationWorkspace,
    WorkspaceManager,
    WorkspaceRole
)
from kaggler.research.experiments import ExperimentTracker, Experiment
from kaggler.research.sharing import ResultSharing, SharingPermission


class DiscussionType(str, Enum):
    """Types of discussions"""
    GENERAL = "general"
    EXPERIMENT = "experiment"
    DATASET = "dataset"
    RESULT = "result"
    ISSUE = "issue"


@dataclass
class Discussion:
    """
    Discussion thread in workspace

    Attributes:
        discussion_id: Unique identifier
        workspace_id: Parent workspace
        title: Discussion title
        discussion_type: Type of discussion
        created_by: Creator user ID
        created_at: Creation timestamp
        messages: List of messages
        related_ids: Related entity IDs (experiment, dataset, etc.)
        is_resolved: Whether discussion is resolved
        metadata: Additional metadata
    """
    discussion_id: str
    workspace_id: str
    title: str
    discussion_type: DiscussionType
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    related_ids: List[str] = field(default_factory=list)
    is_resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(
        self,
        user_id: str,
        content: str,
        attachments: Optional[List[str]] = None
    ):
        """Add message to discussion"""
        message = {
            "message_id": len(self.messages),
            "user_id": user_id,
            "content": content,
            "attachments": attachments or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        self.messages.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "discussion_id": self.discussion_id,
            "workspace_id": self.workspace_id,
            "title": self.title,
            "discussion_type": self.discussion_type.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "num_messages": len(self.messages),
            "related_ids": self.related_ids,
            "is_resolved": self.is_resolved,
            "metadata": self.metadata
        }


@dataclass
class SharedFile:
    """
    Shared file in workspace

    Attributes:
        file_id: Unique identifier
        workspace_id: Parent workspace
        filename: File name
        file_type: Type (dataset, code, paper, etc.)
        uploaded_by: Uploader user ID
        uploaded_at: Upload timestamp
        size_bytes: File size
        file_path: Path to file
        description: File description
        tags: File tags
        metadata: Additional metadata
    """
    file_id: str
    workspace_id: str
    filename: str
    file_type: str
    uploaded_by: str
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    file_path: Optional[str] = None
    description: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "file_id": self.file_id,
            "workspace_id": self.workspace_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat(),
            "size_bytes": self.size_bytes,
            "description": self.description,
            "tags": self.tags,
            "metadata": self.metadata
        }


class Workspace:
    """
    Enhanced workspace for joint research projects

    Combines workspace management, experiment tracking, discussions,
    and file sharing into a unified collaboration platform.
    """

    def __init__(self, workspace_id: str, workspace_manager: WorkspaceManager):
        self.workspace_id = workspace_id
        self._workspace_manager = workspace_manager
        self._experiment_tracker = ExperimentTracker()
        self._result_sharing = ResultSharing()
        self._discussions: Dict[str, Discussion] = {}
        self._files: Dict[str, SharedFile] = {}

    def get_info(self) -> Optional[CollaborationWorkspace]:
        """Get workspace information"""
        return self._workspace_manager.get_workspace(self.workspace_id)

    def invite_collaborator(
        self,
        user_id: str,
        role: WorkspaceRole,
        invited_by: str
    ) -> bool:
        """
        Invite collaborator to workspace

        Args:
            user_id: User to invite
            role: Role to assign
            invited_by: User performing invitation

        Returns:
            True if successful
        """
        return self._workspace_manager.add_member(
            workspace_id=self.workspace_id,
            user_id=user_id,
            role=role,
            added_by=invited_by
        )

    def remove_collaborator(
        self,
        user_id: str,
        removed_by: str
    ) -> bool:
        """Remove collaborator from workspace"""
        return self._workspace_manager.remove_member(
            workspace_id=self.workspace_id,
            user_id=user_id,
            removed_by=removed_by
        )

    def share_experiment(
        self,
        experiment_id: str,
        shared_by: str,
        permission: SharingPermission = SharingPermission.VIEW
    ) -> bool:
        """
        Share experiment with workspace

        Args:
            experiment_id: Experiment to share
            shared_by: User sharing
            permission: Permission level

        Returns:
            True if successful
        """
        workspace = self.get_info()
        if not workspace:
            return False

        # Share with all workspace members
        for member_id in workspace.members.keys():
            if member_id != shared_by:
                self._result_sharing.share_result(
                    result_id=experiment_id,
                    owner_id=shared_by,
                    shared_with=member_id,
                    permission=permission
                )

        return True

    def add_discussion(
        self,
        title: str,
        discussion_type: DiscussionType,
        created_by: str,
        initial_message: str,
        related_ids: Optional[List[str]] = None
    ) -> Discussion:
        """
        Create discussion thread

        Args:
            title: Discussion title
            discussion_type: Type of discussion
            created_by: Creator user ID
            initial_message: First message
            related_ids: Related entity IDs

        Returns:
            Created Discussion
        """
        import hashlib

        discussion_id = hashlib.md5(
            f"{self.workspace_id}_{title}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        discussion = Discussion(
            discussion_id=discussion_id,
            workspace_id=self.workspace_id,
            title=title,
            discussion_type=discussion_type,
            created_by=created_by,
            related_ids=related_ids or []
        )

        discussion.add_message(
            user_id=created_by,
            content=initial_message
        )

        self._discussions[discussion_id] = discussion
        return discussion

    def add_message_to_discussion(
        self,
        discussion_id: str,
        user_id: str,
        content: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Add message to discussion

        Args:
            discussion_id: Discussion identifier
            user_id: Message author
            content: Message content
            attachments: Attachment file IDs

        Returns:
            True if successful
        """
        discussion = self._discussions.get(discussion_id)
        if not discussion:
            return False

        discussion.add_message(
            user_id=user_id,
            content=content,
            attachments=attachments
        )
        return True

    def resolve_discussion(self, discussion_id: str) -> bool:
        """Mark discussion as resolved"""
        discussion = self._discussions.get(discussion_id)
        if discussion:
            discussion.is_resolved = True
            return True
        return False

    def list_discussions(
        self,
        discussion_type: Optional[DiscussionType] = None,
        resolved: Optional[bool] = None
    ) -> List[Discussion]:
        """
        List discussions with filters

        Args:
            discussion_type: Filter by type
            resolved: Filter by resolution status

        Returns:
            List of discussions
        """
        discussions = list(self._discussions.values())

        if discussion_type:
            discussions = [d for d in discussions if d.discussion_type == discussion_type]
        if resolved is not None:
            discussions = [d for d in discussions if d.is_resolved == resolved]

        return discussions

    def share_file(
        self,
        filename: str,
        file_type: str,
        file_path: str,
        uploaded_by: str,
        size_bytes: int,
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> SharedFile:
        """
        Share file with workspace

        Args:
            filename: File name
            file_type: Type (dataset, code, paper, etc.)
            file_path: Path to file
            uploaded_by: Uploader user ID
            size_bytes: File size
            description: File description
            tags: File tags

        Returns:
            SharedFile object
        """
        import hashlib

        file_id = hashlib.md5(
            f"{self.workspace_id}_{filename}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        shared_file = SharedFile(
            file_id=file_id,
            workspace_id=self.workspace_id,
            filename=filename,
            file_type=file_type,
            uploaded_by=uploaded_by,
            size_bytes=size_bytes,
            file_path=file_path,
            description=description,
            tags=tags or []
        )

        self._files[file_id] = shared_file
        return shared_file

    def list_files(
        self,
        file_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[SharedFile]:
        """
        List files in workspace

        Args:
            file_type: Filter by file type
            tags: Filter by tags (any match)

        Returns:
            List of files
        """
        files = list(self._files.values())

        if file_type:
            files = [f for f in files if f.file_type == file_type]
        if tags:
            files = [
                f for f in files
                if any(tag in f.tags for tag in tags)
            ]

        return files

    def delete_file(self, file_id: str, deleted_by: str) -> bool:
        """
        Delete file from workspace

        Args:
            file_id: File identifier
            deleted_by: User deleting file

        Returns:
            True if successful
        """
        file = self._files.get(file_id)
        if not file:
            return False

        # Check if user has permission (owner or admin)
        workspace = self.get_info()
        if not workspace:
            return False

        user_role = workspace.members.get(deleted_by)
        if not user_role:
            return False

        # Can delete if owner of file or admin/owner of workspace
        if (file.uploaded_by == deleted_by or
            user_role in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER]):
            del self._files[file_id]
            return True

        return False

    def get_workspace_activity(
        self,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent activity in workspace

        Args:
            limit: Maximum number of activities

        Returns:
            List of activity records
        """
        activities = []

        # Add discussions
        for discussion in self._discussions.values():
            activities.append({
                "type": "discussion",
                "id": discussion.discussion_id,
                "title": discussion.title,
                "user": discussion.created_by,
                "timestamp": discussion.created_at
            })

        # Add files
        for file in self._files.values():
            activities.append({
                "type": "file",
                "id": file.file_id,
                "title": file.filename,
                "user": file.uploaded_by,
                "timestamp": file.uploaded_at
            })

        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)

        return activities[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get workspace statistics"""
        workspace = self.get_info()
        if not workspace:
            return {}

        return {
            "workspace_id": self.workspace_id,
            "name": workspace.name,
            "num_members": len(workspace.members),
            "num_datasets": len(workspace.datasets),
            "num_discussions": len(self._discussions),
            "num_files": len(self._files),
            "num_experiments": len(self._experiment_tracker.list_experiments()),
            "created_at": workspace.created_at.isoformat()
        }


def create_workspace(
    name: str,
    description: str,
    created_by: str,
    institutions: Optional[List[str]] = None
) -> Workspace:
    """
    Create new collaboration workspace

    Args:
        name: Workspace name
        description: Workspace description
        created_by: Creator user ID
        institutions: List of institutions

    Returns:
        Workspace instance
    """
    workspace_manager = WorkspaceManager()
    collab_workspace = workspace_manager.create_workspace(
        name=name,
        description=description,
        created_by=created_by,
        institutions=institutions
    )

    return Workspace(
        workspace_id=collab_workspace.workspace_id,
        workspace_manager=workspace_manager
    )
