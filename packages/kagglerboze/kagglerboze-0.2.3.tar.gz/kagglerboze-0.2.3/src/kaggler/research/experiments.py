"""
Experiment Tracking

MLflow-like experiment tracking for research collaborations.
Tracks experiments, parameters, metrics, and artifacts.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class ExperimentStatus(str, Enum):
    """Experiment execution status"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Experiment:
    """
    Research experiment record

    Attributes:
        experiment_id: Unique experiment identifier
        name: Experiment name
        workspace_id: Associated collaboration workspace
        user_id: User who created experiment
        status: Execution status
        start_time: When experiment started
        end_time: When experiment ended
        parameters: Experiment parameters
        metrics: Recorded metrics
        artifacts: Artifact locations
        tags: Tags for categorization
        notes: Experiment notes
        parent_id: Parent experiment (for nested runs)
    """
    experiment_id: str
    name: str
    workspace_id: str
    user_id: str
    status: ExperimentStatus = ExperimentStatus.RUNNING
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, List[tuple[float, float]]] = field(default_factory=dict)  # metric -> [(step, value)]
    artifacts: Dict[str, str] = field(default_factory=dict)  # name -> path/url
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "parameters": self.parameters,
            "metrics": {
                k: [(step, val) for step, val in v]
                for k, v in self.metrics.items()
            },
            "artifacts": self.artifacts,
            "tags": self.tags,
            "notes": self.notes,
            "parent_id": self.parent_id
        }


class ExperimentTracker:
    """
    Tracker for research experiments

    Provides MLflow-like functionality for tracking experiments,
    parameters, metrics, and artifacts in collaborative research.
    """

    def __init__(self):
        self._experiments: Dict[str, Experiment] = {}
        self._workspace_experiments: Dict[str, List[str]] = {}  # workspace_id -> experiment_ids

    def create_experiment(
        self,
        name: str,
        workspace_id: str,
        user_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None
    ) -> Experiment:
        """
        Create new experiment

        Args:
            name: Experiment name
            workspace_id: Collaboration workspace ID
            user_id: User creating experiment
            parameters: Initial parameters
            tags: Tags for categorization
            parent_id: Parent experiment ID (for nested runs)

        Returns:
            Created Experiment object
        """
        import hashlib

        experiment_id = hashlib.md5(
            f"{name}_{workspace_id}_{user_id}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            workspace_id=workspace_id,
            user_id=user_id,
            parameters=parameters or {},
            tags=tags or [],
            parent_id=parent_id
        )

        self._experiments[experiment_id] = experiment

        # Add to workspace index
        if workspace_id not in self._workspace_experiments:
            self._workspace_experiments[workspace_id] = []
        self._workspace_experiments[workspace_id].append(experiment_id)

        return experiment

    def log_parameter(self, experiment_id: str, key: str, value: Any) -> bool:
        """
        Log parameter for experiment

        Args:
            experiment_id: Experiment identifier
            key: Parameter name
            value: Parameter value

        Returns:
            True if logged successfully
        """
        experiment = self._experiments.get(experiment_id)
        if experiment:
            experiment.parameters[key] = value
            return True
        return False

    def log_parameters(self, experiment_id: str, parameters: Dict[str, Any]) -> bool:
        """Log multiple parameters"""
        experiment = self._experiments.get(experiment_id)
        if experiment:
            experiment.parameters.update(parameters)
            return True
        return False

    def log_metric(
        self,
        experiment_id: str,
        key: str,
        value: float,
        step: int = 0
    ) -> bool:
        """
        Log metric value

        Args:
            experiment_id: Experiment identifier
            key: Metric name
            value: Metric value
            step: Training step/epoch

        Returns:
            True if logged successfully
        """
        experiment = self._experiments.get(experiment_id)
        if experiment:
            if key not in experiment.metrics:
                experiment.metrics[key] = []
            experiment.metrics[key].append((step, value))
            return True
        return False

    def log_metrics(
        self,
        experiment_id: str,
        metrics: Dict[str, float],
        step: int = 0
    ) -> bool:
        """Log multiple metrics"""
        experiment = self._experiments.get(experiment_id)
        if experiment:
            for key, value in metrics.items():
                if key not in experiment.metrics:
                    experiment.metrics[key] = []
                experiment.metrics[key].append((step, value))
            return True
        return False

    def log_artifact(self, experiment_id: str, name: str, path: str) -> bool:
        """
        Log artifact (file, model, etc.)

        Args:
            experiment_id: Experiment identifier
            name: Artifact name
            path: Path or URL to artifact

        Returns:
            True if logged successfully
        """
        experiment = self._experiments.get(experiment_id)
        if experiment:
            experiment.artifacts[name] = path
            return True
        return False

    def add_tag(self, experiment_id: str, tag: str) -> bool:
        """Add tag to experiment"""
        experiment = self._experiments.get(experiment_id)
        if experiment and tag not in experiment.tags:
            experiment.tags.append(tag)
            return True
        return False

    def set_notes(self, experiment_id: str, notes: str) -> bool:
        """Set experiment notes"""
        experiment = self._experiments.get(experiment_id)
        if experiment:
            experiment.notes = notes
            return True
        return False

    def end_experiment(
        self,
        experiment_id: str,
        status: ExperimentStatus = ExperimentStatus.COMPLETED
    ) -> bool:
        """
        Mark experiment as ended

        Args:
            experiment_id: Experiment identifier
            status: Final status

        Returns:
            True if updated successfully
        """
        experiment = self._experiments.get(experiment_id)
        if experiment:
            experiment.status = status
            experiment.end_time = datetime.utcnow()
            return True
        return False

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get experiment by ID"""
        return self._experiments.get(experiment_id)

    def list_experiments(
        self,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[ExperimentStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[Experiment]:
        """
        List experiments with filters

        Args:
            workspace_id: Filter by workspace
            user_id: Filter by user
            status: Filter by status
            tags: Filter by tags

        Returns:
            List of matching experiments
        """
        if workspace_id:
            experiment_ids = self._workspace_experiments.get(workspace_id, [])
            experiments = [self._experiments[eid] for eid in experiment_ids]
        else:
            experiments = list(self._experiments.values())

        if user_id:
            experiments = [e for e in experiments if e.user_id == user_id]
        if status:
            experiments = [e for e in experiments if e.status == status]
        if tags:
            experiments = [
                e for e in experiments
                if any(tag in e.tags for tag in tags)
            ]

        return experiments

    def compare_experiments(
        self,
        experiment_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple experiments

        Args:
            experiment_ids: List of experiment IDs to compare

        Returns:
            Dictionary with comparison data
        """
        experiments = [
            self._experiments.get(eid)
            for eid in experiment_ids
            if eid in self._experiments
        ]

        if not experiments:
            return {}

        # Collect all parameter keys
        all_params = set()
        for exp in experiments:
            all_params.update(exp.parameters.keys())

        # Collect all metric keys
        all_metrics = set()
        for exp in experiments:
            all_metrics.update(exp.metrics.keys())

        comparison = {
            "experiments": [e.experiment_id for e in experiments],
            "parameters": {},
            "metrics": {},
            "status": [e.status.value for e in experiments]
        }

        # Compare parameters
        for param in all_params:
            comparison["parameters"][param] = [
                exp.parameters.get(param) for exp in experiments
            ]

        # Compare final metric values
        for metric in all_metrics:
            comparison["metrics"][metric] = [
                exp.metrics[metric][-1][1] if metric in exp.metrics and exp.metrics[metric]
                else None
                for exp in experiments
            ]

        return comparison

    def get_best_experiment(
        self,
        workspace_id: str,
        metric: str,
        maximize: bool = True
    ) -> Optional[Experiment]:
        """
        Get best experiment by metric

        Args:
            workspace_id: Workspace to search
            metric: Metric to optimize
            maximize: Whether to maximize metric

        Returns:
            Best experiment or None
        """
        experiments = self.list_experiments(
            workspace_id=workspace_id,
            status=ExperimentStatus.COMPLETED
        )

        # Filter experiments with the metric
        valid_experiments = [
            exp for exp in experiments
            if metric in exp.metrics and exp.metrics[metric]
        ]

        if not valid_experiments:
            return None

        # Get final metric value for each experiment
        def get_final_value(exp: Experiment) -> float:
            return exp.metrics[metric][-1][1]

        if maximize:
            return max(valid_experiments, key=get_final_value)
        else:
            return min(valid_experiments, key=get_final_value)

    def export_experiment(self, experiment_id: str, format: str = "json") -> Optional[str]:
        """
        Export experiment data

        Args:
            experiment_id: Experiment identifier
            format: Export format (json)

        Returns:
            Serialized experiment data or None
        """
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return None

        if format == "json":
            return json.dumps(experiment.to_dict(), indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def delete_experiment(self, experiment_id: str) -> bool:
        """Delete experiment"""
        experiment = self._experiments.get(experiment_id)
        if experiment:
            # Remove from workspace index
            workspace_id = experiment.workspace_id
            if workspace_id in self._workspace_experiments:
                self._workspace_experiments[workspace_id].remove(experiment_id)

            del self._experiments[experiment_id]
            return True
        return False
