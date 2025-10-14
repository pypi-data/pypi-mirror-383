"""
Database Models for Research Partnerships

SQLAlchemy models for all research partnership entities.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, JSON, Enum as SQLEnum, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


# Association tables for many-to-many relationships
collaboration_datasets = Table(
    'collaboration_datasets',
    Base.metadata,
    Column('collaboration_id', String(16), ForeignKey('collaborations.id')),
    Column('dataset_id', String(16), ForeignKey('datasets.id'))
)

collaboration_members = Table(
    'collaboration_members',
    Base.metadata,
    Column('collaboration_id', String(16), ForeignKey('collaborations.id')),
    Column('user_id', String(100)),
    Column('role', String(50))
)


class DatasetModel(Base):
    """Dataset table model"""
    __tablename__ = 'datasets'

    id = Column(String(16), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    dataset_type = Column(String(50), nullable=False)
    owner_id = Column(String(100), nullable=False, index=True)
    institution = Column(String(255), nullable=False, index=True)
    version = Column(String(20), default="1.0.0")
    status = Column(String(50), default="draft")
    license = Column(String(100), default="CC-BY-4.0")
    privacy_level = Column(String(50), default="public")
    doi = Column(String(100), nullable=True)
    size_bytes = Column(Integer, default=0)
    num_records = Column(Integer, default=0)
    checksum = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # JSON fields
    tags = Column(JSON, default=list)
    schema = Column(JSON, default=dict)
    provenance = Column(JSON, default=dict)
    custom_metadata = Column(JSON, default=dict)

    # Relationships
    benchmarks = relationship("BenchmarkModel", back_populates="dataset")
    citations = relationship("CitationModel", back_populates="dataset")
    api_keys = relationship("APIKeyModel", back_populates="dataset")


class BenchmarkModel(Base):
    """Benchmark table model"""
    __tablename__ = 'benchmarks'

    id = Column(String(16), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    dataset_id = Column(String(16), ForeignKey('datasets.id'), nullable=False, index=True)
    task = Column(String(50), nullable=False)
    metric = Column(String(100), nullable=False)
    metric_type = Column(String(50), nullable=False)
    baseline_score = Column(Float, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # JSON fields
    evaluation_protocol = Column(Text)
    constraints = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)

    # Relationships
    dataset = relationship("DatasetModel", back_populates="benchmarks")
    submissions = relationship("SubmissionModel", back_populates="benchmark")


class SubmissionModel(Base):
    """Benchmark submission table model"""
    __tablename__ = 'submissions'

    id = Column(String(16), primary_key=True)
    benchmark_id = Column(String(16), ForeignKey('benchmarks.id'), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    institution = Column(String(255), nullable=False)
    score = Column(Float, nullable=False)
    method = Column(String(255), nullable=False)
    description = Column(Text)
    code_url = Column(String(500), nullable=True)
    paper_url = Column(String(500), nullable=True)
    checksum = Column(String(64), nullable=True)
    verified = Column(Boolean, default=False)
    reproducible = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # JSON field
    metadata = Column(JSON, default=dict)

    # Relationships
    benchmark = relationship("BenchmarkModel", back_populates="submissions")


class CollaborationModel(Base):
    """Collaboration workspace table model"""
    __tablename__ = 'collaborations'

    id = Column(String(16), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # JSON fields
    institutions = Column(JSON, default=list)
    settings = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)

    # Many-to-many relationships
    datasets = relationship(
        "DatasetModel",
        secondary=collaboration_datasets,
        backref="collaborations"
    )


class CitationModel(Base):
    """Citation tracking table model"""
    __tablename__ = 'citations'

    id = Column(String(16), primary_key=True)
    dataset_id = Column(String(16), ForeignKey('datasets.id'), nullable=False, index=True)
    paper_title = Column(String(500), nullable=False)
    paper_authors = Column(JSON, nullable=False)
    paper_url = Column(String(500), nullable=True)
    doi = Column(String(100), nullable=True, index=True)
    publication_date = Column(DateTime, nullable=True)
    venue = Column(String(255), nullable=True)
    citation_text = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)
    added_by = Column(String(100), nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    # JSON field
    metadata = Column(JSON, default=dict)

    # Relationships
    dataset = relationship("DatasetModel", back_populates="citations")


class APIKeyModel(Base):
    """API key table model"""
    __tablename__ = 'api_keys'

    id = Column(String(16), primary_key=True)
    key_hash = Column(String(64), nullable=False, unique=True, index=True)
    institution_id = Column(String(100), nullable=False, index=True)
    dataset_id = Column(String(16), ForeignKey('datasets.id'), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=1000)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)

    # JSON field
    permissions = Column(JSON, default=list)

    # Relationships
    dataset = relationship("DatasetModel", back_populates="api_keys")


class ExperimentModel(Base):
    """Experiment tracking table model"""
    __tablename__ = 'experiments'

    id = Column(String(16), primary_key=True)
    name = Column(String(255), nullable=False)
    workspace_id = Column(String(16), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="running")
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    parent_id = Column(String(16), nullable=True)
    notes = Column(Text, nullable=True)

    # JSON fields
    parameters = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)
    artifacts = Column(JSON, default=dict)
    tags = Column(JSON, default=list)


class ConsentModel(Base):
    """User consent tracking table model"""
    __tablename__ = 'consents'

    id = Column(String(16), primary_key=True)
    user_id = Column(String(100), nullable=False, index=True)
    dataset_id = Column(String(16), nullable=False, index=True)
    purpose = Column(String(255), nullable=False)
    granted = Column(Boolean, default=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)


class EthicsReviewModel(Base):
    """Ethics review table model"""
    __tablename__ = 'ethics_reviews'

    id = Column(String(16), primary_key=True)
    dataset_id = Column(String(16), nullable=False, index=True)
    status = Column(String(50), default="pending")
    reviewer_id = Column(String(100), nullable=True)
    institution = Column(String(255), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    # JSON fields
    categories = Column(JSON, default=list)
    conditions = Column(JSON, default=list)
    concerns = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)


class AuditLogModel(Base):
    """Audit log table model for compliance"""
    __tablename__ = 'audit_logs'

    id = Column(String(16), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    success = Column(Boolean, default=True)

    # JSON fields
    details = Column(JSON, default=dict)
    compliance_standards = Column(JSON, default=list)


class DiscussionModel(Base):
    """Discussion thread table model"""
    __tablename__ = 'discussions'

    id = Column(String(16), primary_key=True)
    workspace_id = Column(String(16), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    discussion_type = Column(String(50), nullable=False)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_resolved = Column(Boolean, default=False)

    # JSON fields
    messages = Column(JSON, default=list)
    related_ids = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)


class SharedFileModel(Base):
    """Shared file table model"""
    __tablename__ = 'shared_files'

    id = Column(String(16), primary_key=True)
    workspace_id = Column(String(16), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    uploaded_by = Column(String(100), nullable=False, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    size_bytes = Column(Integer, default=0)
    file_path = Column(String(1000), nullable=True)
    description = Column(Text, nullable=True)

    # JSON fields
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)


# Database initialization helper
def init_db(engine):
    """Initialize database schema"""
    Base.metadata.create_all(engine)


def drop_db(engine):
    """Drop all tables"""
    Base.metadata.drop_all(engine)
