"""
Collaborative Evolution System

Implements distributed evolution with multiple workers coordinated by a central node.
Uses Celery + Redis for task distribution and result aggregation.

Key Components:
- EvolutionCoordinator: Central coordinator managing global evolution
- WorkerNode: Distributed workers executing local evolution
- Communication Protocol: Message passing and serialization
- Merge Strategies: Combining populations from multiple sources
- Contribution Tracking: Credit assignment for worker contributions
- Sharing Protocol: Individual exchange between workers
- Celery Integration: Distributed task execution
"""

from .coordinator import EvolutionCoordinator, CoordinatorConfig
from .worker import WorkerNode, WorkerConfig
from .protocol import (
    Message,
    MessageType,
    IndividualData,
    CommunicationProtocol,
    serialize_individual,
    deserialize_individual,
    WorkStealingProtocol,
)
from .merge import (
    MergeStrategy,
    EliteMerger,
    DiversityMerger,
    ParetoMerger,
    AdaptiveMerger,
    WeightedMerger,
)
from .tracking import ContributionTracker, WorkerStats, ContributionRecord
from .sharing import (
    SharingPolicy,
    SharingProtocol,
    P2PSharingNetwork,
    AdaptiveSharingStrategy,
    BandwidthOptimizer,
)

# Import celery_app and tasks if available
try:
    from .celery_app import (
        create_celery_app,
        app as celery_app,
        WorkerPool,
        TaskMonitor,
        health_check,
    )
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    celery_app = None

__all__ = [
    # Core Components
    "EvolutionCoordinator",
    "CoordinatorConfig",
    "WorkerNode",
    "WorkerConfig",
    # Protocol
    "Message",
    "MessageType",
    "IndividualData",
    "CommunicationProtocol",
    "serialize_individual",
    "deserialize_individual",
    "WorkStealingProtocol",
    # Merge Strategies
    "MergeStrategy",
    "EliteMerger",
    "DiversityMerger",
    "ParetoMerger",
    "AdaptiveMerger",
    "WeightedMerger",
    # Tracking
    "ContributionTracker",
    "WorkerStats",
    "ContributionRecord",
    # Sharing
    "SharingPolicy",
    "SharingProtocol",
    "P2PSharingNetwork",
    "AdaptiveSharingStrategy",
    "BandwidthOptimizer",
    # Celery (if available)
    "celery_app",
    "create_celery_app",
    "CELERY_AVAILABLE",
]

__version__ = "0.3.0"
