"""
Dataset Hub - Central management for research datasets

Provides unified interface for registering, discovering, and accessing
research datasets with full access control and metadata management.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from kaggler.research.metadata import DatasetMetadata, MetadataManager, DatasetType, DatasetStatus
from kaggler.research.access_control import AccessControl, AccessLevel, Permission, Role


class DatasetHub:
    """
    Central hub for managing research datasets

    Integrates metadata management and access control to provide
    a complete dataset management solution.
    """

    def __init__(self):
        self.metadata_manager = MetadataManager()
        self.access_control = AccessControl()
        self._dataset_storage: Dict[str, Any] = {}  # Simple in-memory storage

    def register_dataset(
        self,
        name: str,
        description: str,
        dataset_type: DatasetType,
        owner_id: str,
        institution: str,
        access_level: AccessLevel = AccessLevel.PUBLIC,
        license: str = "CC-BY-4.0",
        **metadata_kwargs
    ) -> DatasetMetadata:
        """
        Register a new research dataset

        Args:
            name: Dataset name
            description: Detailed description
            dataset_type: Type of data
            owner_id: Owner identifier
            institution: Institution name
            access_level: Access level (public, restricted, etc.)
            license: License identifier
            **metadata_kwargs: Additional metadata fields

        Returns:
            Created DatasetMetadata object

        Raises:
            ValueError: If dataset validation fails
        """
        # Create metadata
        metadata = self.metadata_manager.create_metadata(
            name=name,
            description=description,
            dataset_type=dataset_type,
            owner_id=owner_id,
            institution=institution,
            license=license,
            privacy_level=access_level.value,
            **metadata_kwargs
        )

        # Validate metadata
        errors = self.metadata_manager.validate_metadata(metadata)
        if errors:
            raise ValueError(f"Metadata validation failed: {', '.join(errors)}")

        # Grant owner access
        self.access_control.grant_access(
            dataset_id=metadata.id,
            user_id=owner_id,
            institution_id=institution,
            role=Role.OWNER,
            granted_by=owner_id
        )

        return metadata

    def get_dataset(self, dataset_id: str, user_id: str) -> Optional[DatasetMetadata]:
        """
        Get dataset metadata if user has access

        Args:
            dataset_id: Dataset identifier
            user_id: User requesting access

        Returns:
            DatasetMetadata if accessible, None otherwise
        """
        metadata = self.metadata_manager.get_metadata(dataset_id)
        if not metadata:
            return None

        # Check access
        access_level = AccessLevel(metadata.privacy_level)
        if not self.access_control.check_permission(
            user_id=user_id,
            dataset_id=dataset_id,
            permission=Permission.READ,
            access_level=access_level
        ):
            return None

        return metadata

    def search_datasets(
        self,
        query: Optional[str] = None,
        dataset_type: Optional[DatasetType] = None,
        institution: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> List[DatasetMetadata]:
        """
        Search for datasets with filters

        Args:
            query: Text search query
            dataset_type: Filter by dataset type
            institution: Filter by institution
            tags: Filter by tags
            user_id: User performing search (for access control)

        Returns:
            List of accessible datasets
        """
        # Build filters
        filters = {}
        if dataset_type:
            filters["dataset_type"] = dataset_type
        if institution:
            filters["institution"] = institution

        # Get matching datasets
        results = self.metadata_manager.list_metadata(filters)

        # Filter by tags if specified
        if tags:
            results = [
                ds for ds in results
                if any(tag in ds.tags for tag in tags)
            ]

        # Filter by text query
        if query:
            query_lower = query.lower()
            results = [
                ds for ds in results
                if query_lower in ds.name.lower() or query_lower in ds.description.lower()
            ]

        # Filter by access control
        if user_id:
            accessible_results = []
            for ds in results:
                access_level = AccessLevel(ds.privacy_level)
                if self.access_control.check_permission(
                    user_id=user_id,
                    dataset_id=ds.id,
                    permission=Permission.READ,
                    access_level=access_level
                ):
                    accessible_results.append(ds)
            results = accessible_results

        return results

    def request_access(
        self,
        dataset_id: str,
        user_id: str,
        institution_id: str,
        justification: str
    ) -> Dict[str, Any]:
        """
        Request access to a restricted dataset

        Args:
            dataset_id: Dataset identifier
            user_id: User requesting access
            institution_id: User's institution
            justification: Reason for access request

        Returns:
            Dictionary with request details
        """
        metadata = self.metadata_manager.get_metadata(dataset_id)
        if not metadata:
            raise ValueError(f"Dataset {dataset_id} not found")

        request_id = f"req_{dataset_id}_{user_id}_{datetime.utcnow().timestamp()}"

        # In production, this would create a pending request for approval
        return {
            "request_id": request_id,
            "dataset_id": dataset_id,
            "user_id": user_id,
            "institution_id": institution_id,
            "justification": justification,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

    def grant_dataset_access(
        self,
        dataset_id: str,
        user_id: str,
        role: Role,
        granted_by: str,
        expires_in_days: Optional[int] = None
    ) -> bool:
        """
        Grant user access to dataset

        Args:
            dataset_id: Dataset identifier
            user_id: User to grant access
            role: Role to assign
            granted_by: User granting access
            expires_in_days: Optional expiration

        Returns:
            True if granted successfully
        """
        # Check if granter has permission
        if not self.access_control.check_permission(
            user_id=granted_by,
            dataset_id=dataset_id,
            permission=Permission.SHARE
        ):
            raise PermissionError(f"User {granted_by} cannot grant access to dataset")

        self.access_control.grant_access(
            dataset_id=dataset_id,
            user_id=user_id,
            institution_id=None,
            role=role,
            granted_by=granted_by,
            expires_in_days=expires_in_days
        )
        return True

    def update_dataset(
        self,
        dataset_id: str,
        user_id: str,
        **updates
    ) -> Optional[DatasetMetadata]:
        """
        Update dataset metadata

        Args:
            dataset_id: Dataset identifier
            user_id: User performing update
            **updates: Fields to update

        Returns:
            Updated metadata or None

        Raises:
            PermissionError: If user lacks write permission
        """
        # Check write permission
        if not self.access_control.check_permission(
            user_id=user_id,
            dataset_id=dataset_id,
            permission=Permission.WRITE
        ):
            raise PermissionError(f"User {user_id} cannot update dataset {dataset_id}")

        return self.metadata_manager.update_metadata(dataset_id, **updates)

    def delete_dataset(self, dataset_id: str, user_id: str) -> bool:
        """
        Delete (archive) dataset

        Args:
            dataset_id: Dataset identifier
            user_id: User performing deletion

        Returns:
            True if deleted

        Raises:
            PermissionError: If user lacks delete permission
        """
        # Check delete permission
        if not self.access_control.check_permission(
            user_id=user_id,
            dataset_id=dataset_id,
            permission=Permission.DELETE
        ):
            raise PermissionError(f"User {user_id} cannot delete dataset {dataset_id}")

        return self.metadata_manager.delete_metadata(dataset_id)

    def publish_dataset(self, dataset_id: str, user_id: str, doi: Optional[str] = None) -> bool:
        """
        Publish dataset (change status to published)

        Args:
            dataset_id: Dataset identifier
            user_id: User performing publication
            doi: Optional DOI to assign

        Returns:
            True if published
        """
        updates = {"status": DatasetStatus.PUBLISHED}
        if doi:
            updates["doi"] = doi

        metadata = self.update_dataset(dataset_id, user_id, **updates)
        return metadata is not None

    def get_dataset_stats(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get statistics for a dataset

        Args:
            dataset_id: Dataset identifier

        Returns:
            Dictionary with statistics
        """
        metadata = self.metadata_manager.get_metadata(dataset_id)
        if not metadata:
            return {}

        grants = self.access_control.list_dataset_grants(dataset_id)
        version_history = self.metadata_manager.get_version_history(dataset_id)

        return {
            "dataset_id": dataset_id,
            "name": metadata.name,
            "num_records": metadata.num_records,
            "size_bytes": metadata.size_bytes,
            "num_collaborators": len(grants),
            "num_versions": len(version_history),
            "created_at": metadata.created_at.isoformat(),
            "updated_at": metadata.updated_at.isoformat(),
            "status": metadata.status.value,
            "citation_count": 0,  # Will be integrated with CitationTracker
        }

    def export_dataset_info(self, dataset_id: str, format: str = "json") -> Optional[str]:
        """
        Export dataset information

        Args:
            dataset_id: Dataset identifier
            format: Export format (json, etc.)

        Returns:
            Serialized dataset information
        """
        metadata = self.metadata_manager.get_metadata(dataset_id)
        if not metadata:
            return None

        info = {
            "metadata": metadata.to_dict(),
            "stats": self.get_dataset_stats(dataset_id),
            "access_grants": [
                {
                    "user_id": g.user_id,
                    "role": g.role.value,
                    "granted_at": g.granted_at.isoformat()
                }
                for g in self.access_control.list_dataset_grants(dataset_id)
            ]
        }

        if format == "json":
            return json.dumps(info, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
