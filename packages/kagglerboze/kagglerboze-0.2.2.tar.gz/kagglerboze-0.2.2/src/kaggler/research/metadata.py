"""
Dataset Metadata Management

Handles metadata for research datasets including descriptions, versioning,
schema information, and data lineage tracking.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib


class DatasetType(str, Enum):
    """Types of research datasets"""
    TABULAR = "tabular"
    IMAGE = "image"
    TEXT = "text"
    TIME_SERIES = "time_series"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"
    GRAPH = "graph"


class DatasetStatus(str, Enum):
    """Dataset publication status"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class DatasetMetadata:
    """
    Comprehensive metadata for a research dataset

    Attributes:
        id: Unique dataset identifier
        name: Dataset name
        description: Detailed description
        dataset_type: Type of data (tabular, image, etc.)
        owner_id: ID of the dataset owner
        institution: Institution or organization
        version: Dataset version (semantic versioning)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        status: Publication status
        license: License identifier
        privacy_level: Privacy classification
        doi: Digital Object Identifier (optional)
        tags: List of tags for categorization
        schema: Data schema information
        size_bytes: Dataset size in bytes
        num_records: Number of records/samples
        checksum: SHA-256 checksum for integrity
        provenance: Data lineage and source information
        citation_text: Suggested citation format
        related_papers: List of related paper URLs/DOIs
        custom_metadata: Additional custom fields
    """
    id: str
    name: str
    description: str
    dataset_type: DatasetType
    owner_id: str
    institution: str
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: DatasetStatus = DatasetStatus.DRAFT
    license: str = "CC-BY-4.0"
    privacy_level: str = "public"
    doi: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    schema: Dict[str, Any] = field(default_factory=dict)
    size_bytes: int = 0
    num_records: int = 0
    checksum: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    citation_text: Optional[str] = None
    related_papers: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dataset_type": self.dataset_type.value,
            "owner_id": self.owner_id,
            "institution": self.institution,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "license": self.license,
            "privacy_level": self.privacy_level,
            "doi": self.doi,
            "tags": self.tags,
            "schema": self.schema,
            "size_bytes": self.size_bytes,
            "num_records": self.num_records,
            "checksum": self.checksum,
            "provenance": self.provenance,
            "citation_text": self.citation_text,
            "related_papers": self.related_papers,
            "custom_metadata": self.custom_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetMetadata":
        """Create metadata from dictionary"""
        data = data.copy()
        data["dataset_type"] = DatasetType(data["dataset_type"])
        data["status"] = DatasetStatus(data["status"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)

    def compute_checksum(self, data: bytes) -> str:
        """Compute SHA-256 checksum for dataset"""
        self.checksum = hashlib.sha256(data).hexdigest()
        return self.checksum

    def generate_citation(self) -> str:
        """Generate citation text if not provided"""
        if self.citation_text:
            return self.citation_text

        year = self.created_at.year
        doi_part = f" doi:{self.doi}" if self.doi else ""
        self.citation_text = (
            f"{self.institution} ({year}). {self.name}. "
            f"Version {self.version}.{doi_part}"
        )
        return self.citation_text


class MetadataManager:
    """
    Manager for dataset metadata operations

    Handles CRUD operations, validation, and versioning of dataset metadata.
    """

    def __init__(self):
        self._metadata_store: Dict[str, DatasetMetadata] = {}
        self._version_history: Dict[str, List[DatasetMetadata]] = {}

    def create_metadata(
        self,
        name: str,
        description: str,
        dataset_type: DatasetType,
        owner_id: str,
        institution: str,
        **kwargs
    ) -> DatasetMetadata:
        """
        Create new dataset metadata

        Args:
            name: Dataset name
            description: Detailed description
            dataset_type: Type of data
            owner_id: Owner identifier
            institution: Institution name
            **kwargs: Additional metadata fields

        Returns:
            Created DatasetMetadata object
        """
        dataset_id = self._generate_id(name, institution)

        metadata = DatasetMetadata(
            id=dataset_id,
            name=name,
            description=description,
            dataset_type=dataset_type,
            owner_id=owner_id,
            institution=institution,
            **kwargs
        )

        self._metadata_store[dataset_id] = metadata
        self._version_history[dataset_id] = [metadata]

        return metadata

    def get_metadata(self, dataset_id: str) -> Optional[DatasetMetadata]:
        """Retrieve metadata by dataset ID"""
        return self._metadata_store.get(dataset_id)

    def update_metadata(
        self,
        dataset_id: str,
        **updates
    ) -> Optional[DatasetMetadata]:
        """
        Update existing metadata

        Args:
            dataset_id: Dataset identifier
            **updates: Fields to update

        Returns:
            Updated metadata or None if not found
        """
        metadata = self._metadata_store.get(dataset_id)
        if not metadata:
            return None

        # Create new version for history
        import copy
        old_version = copy.deepcopy(metadata)
        self._version_history[dataset_id].append(old_version)

        # Update fields
        for key, value in updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        metadata.updated_at = datetime.utcnow()
        return metadata

    def list_metadata(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[DatasetMetadata]:
        """
        List datasets with optional filters

        Args:
            filters: Dictionary of field filters

        Returns:
            List of matching metadata objects
        """
        results = list(self._metadata_store.values())

        if filters:
            for key, value in filters.items():
                results = [
                    m for m in results
                    if getattr(m, key, None) == value
                ]

        return results

    def delete_metadata(self, dataset_id: str) -> bool:
        """
        Delete metadata (soft delete by archiving)

        Args:
            dataset_id: Dataset identifier

        Returns:
            True if deleted, False if not found
        """
        metadata = self._metadata_store.get(dataset_id)
        if not metadata:
            return False

        metadata.status = DatasetStatus.ARCHIVED
        metadata.updated_at = datetime.utcnow()
        return True

    def get_version_history(self, dataset_id: str) -> List[DatasetMetadata]:
        """Get version history for a dataset"""
        return self._version_history.get(dataset_id, [])

    def validate_metadata(self, metadata: DatasetMetadata) -> List[str]:
        """
        Validate metadata completeness and correctness

        Args:
            metadata: Metadata to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not metadata.name or len(metadata.name) < 3:
            errors.append("Dataset name must be at least 3 characters")

        if not metadata.description or len(metadata.description) < 10:
            errors.append("Description must be at least 10 characters")

        if not metadata.license:
            errors.append("License must be specified")

        if metadata.num_records < 0:
            errors.append("Number of records cannot be negative")

        if metadata.size_bytes < 0:
            errors.append("Dataset size cannot be negative")

        # Validate version format (semantic versioning)
        if not self._is_valid_version(metadata.version):
            errors.append("Version must follow semantic versioning (e.g., 1.0.0)")

        return errors

    def _generate_id(self, name: str, institution: str) -> str:
        """Generate unique dataset ID"""
        raw_id = f"{institution}_{name}_{datetime.utcnow().timestamp()}"
        return hashlib.md5(raw_id.encode()).hexdigest()[:16]

    def _is_valid_version(self, version: str) -> bool:
        """Validate semantic version format"""
        parts = version.split(".")
        if len(parts) != 3:
            return False
        return all(part.isdigit() for part in parts)

    def export_metadata(self, dataset_id: str, format: str = "json") -> Optional[str]:
        """
        Export metadata to various formats

        Args:
            dataset_id: Dataset identifier
            format: Export format (json, yaml, xml)

        Returns:
            Serialized metadata string or None
        """
        metadata = self.get_metadata(dataset_id)
        if not metadata:
            return None

        if format == "json":
            return json.dumps(metadata.to_dict(), indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
