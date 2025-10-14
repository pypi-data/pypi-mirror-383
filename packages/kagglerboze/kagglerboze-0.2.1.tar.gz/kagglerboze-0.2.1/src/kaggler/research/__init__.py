"""
Research Partnerships Infrastructure

This module provides comprehensive tools for managing research partnerships,
including dataset sharing, benchmarking, collaboration, and compliance.

Main Components:
- Dataset Hub: Manage and share research datasets
- Benchmark Suite: Standardized benchmarks with reproducibility
- Collaboration Tools: Workspaces and experiment tracking
- Citation Tracking: Track dataset usage and research impact
- Compliance: Privacy, licensing, and ethics controls
"""

from kaggler.research.dataset_hub import DatasetHub
from kaggler.research.metadata import DatasetMetadata, MetadataManager
from kaggler.research.access_control import AccessControl, AccessLevel, APIKeyManager
from kaggler.research.benchmark_suite import StandardizedBenchmark, BenchmarkManager, BenchmarkTask
from kaggler.research.benchmarks import BenchmarkRunner, BenchmarkResult, TaskType
from kaggler.research.reproducibility import ReproducibilityManager, ExperimentChecksum
from kaggler.research.leaderboard import ResearchLeaderboard, LeaderboardEntry
from kaggler.research.workspace import CollaborationWorkspace, WorkspaceManager, WorkspaceRole
from kaggler.research.collaboration import Workspace, Discussion, SharedFile, DiscussionType
from kaggler.research.experiments import ExperimentTracker, Experiment
from kaggler.research.sharing import ResultSharing, SharingPermission
from kaggler.research.citations import CitationTracker, Citation
from kaggler.research.privacy import PrivacyControl, DataAnonymizer, ConsentManager
from kaggler.research.licensing import LicenseManager, License
from kaggler.research.ethics import EthicsReview, EthicsStatus
from kaggler.research.compliance import (
    ComplianceChecker,
    ComplianceStandard,
    DataCategory,
    AuditAction,
    AuditLogEntry,
    ConsentRecord
)

__all__ = [
    # Dataset Hub
    "DatasetHub",
    "DatasetMetadata",
    "MetadataManager",
    "AccessControl",
    "AccessLevel",
    "APIKeyManager",
    # Benchmark Suite
    "StandardizedBenchmark",
    "BenchmarkManager",
    "BenchmarkTask",
    "BenchmarkRunner",
    "BenchmarkResult",
    "TaskType",
    "ReproducibilityManager",
    "ExperimentChecksum",
    "ResearchLeaderboard",
    "LeaderboardEntry",
    # Collaboration
    "CollaborationWorkspace",
    "WorkspaceManager",
    "WorkspaceRole",
    "Workspace",
    "Discussion",
    "SharedFile",
    "DiscussionType",
    "ExperimentTracker",
    "Experiment",
    "ResultSharing",
    "SharingPermission",
    # Citation
    "CitationTracker",
    "Citation",
    # Compliance
    "PrivacyControl",
    "DataAnonymizer",
    "ConsentManager",
    "LicenseManager",
    "License",
    "EthicsReview",
    "EthicsStatus",
    "ComplianceChecker",
    "ComplianceStandard",
    "DataCategory",
    "AuditAction",
    "AuditLogEntry",
    "ConsentRecord",
]

__version__ = "0.1.0"
