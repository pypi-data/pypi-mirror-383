"""
Reproducibility Manager

Ensures experiment reproducibility through checksums, environment tracking,
and configuration management.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import platform


@dataclass
class ExperimentChecksum:
    """
    Checksum for reproducible experiments

    Attributes:
        experiment_id: Unique experiment identifier
        code_checksum: Hash of code used
        data_checksum: Hash of input data
        config_checksum: Hash of configuration
        environment_checksum: Hash of environment info
        seed: Random seed used
        timestamp: When checksum was created
        metadata: Additional metadata
    """
    experiment_id: str
    code_checksum: str
    data_checksum: str
    config_checksum: str
    environment_checksum: str
    seed: int
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "experiment_id": self.experiment_id,
            "code_checksum": self.code_checksum,
            "data_checksum": self.data_checksum,
            "config_checksum": self.config_checksum,
            "environment_checksum": self.environment_checksum,
            "seed": self.seed,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

    def compute_full_checksum(self) -> str:
        """Compute combined checksum from all components"""
        combined = (
            f"{self.code_checksum}:{self.data_checksum}:"
            f"{self.config_checksum}:{self.environment_checksum}:{self.seed}"
        )
        return hashlib.sha256(combined.encode()).hexdigest()


@dataclass
class EnvironmentInfo:
    """
    Environment information for reproducibility

    Attributes:
        python_version: Python version
        platform: Operating system
        libraries: Dictionary of library versions
        hardware: Hardware information
        timestamp: When info was captured
    """
    python_version: str
    platform: str
    libraries: Dict[str, str] = field(default_factory=dict)
    hardware: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "python_version": self.python_version,
            "platform": self.platform,
            "libraries": self.libraries,
            "hardware": self.hardware,
            "timestamp": self.timestamp.isoformat()
        }


class ReproducibilityManager:
    """
    Manager for experiment reproducibility

    Tracks experiment configurations, environments, and checksums
    to ensure reproducible results.
    """

    def __init__(self):
        self._checksums: Dict[str, ExperimentChecksum] = {}
        self._environments: Dict[str, EnvironmentInfo] = {}

    def create_checksum(
        self,
        experiment_id: str,
        code: str,
        data: bytes,
        config: Dict[str, Any],
        seed: int
    ) -> ExperimentChecksum:
        """
        Create reproducibility checksum for experiment

        Args:
            experiment_id: Unique experiment identifier
            code: Code string or file content
            data: Input data bytes
            config: Configuration dictionary
            seed: Random seed

        Returns:
            ExperimentChecksum object
        """
        # Compute individual checksums
        code_checksum = hashlib.sha256(code.encode()).hexdigest()
        data_checksum = hashlib.sha256(data).hexdigest()
        config_checksum = hashlib.sha256(
            json.dumps(config, sort_keys=True).encode()
        ).hexdigest()

        # Capture environment info
        env_info = self.capture_environment()
        env_checksum = hashlib.sha256(
            json.dumps(env_info.to_dict(), sort_keys=True).encode()
        ).hexdigest()

        checksum = ExperimentChecksum(
            experiment_id=experiment_id,
            code_checksum=code_checksum,
            data_checksum=data_checksum,
            config_checksum=config_checksum,
            environment_checksum=env_checksum,
            seed=seed
        )

        self._checksums[experiment_id] = checksum
        self._environments[experiment_id] = env_info

        return checksum

    def verify_checksum(
        self,
        experiment_id: str,
        code: str,
        data: bytes,
        config: Dict[str, Any],
        seed: int
    ) -> bool:
        """
        Verify experiment matches stored checksum

        Args:
            experiment_id: Experiment identifier
            code: Code to verify
            data: Data to verify
            config: Configuration to verify
            seed: Random seed to verify

        Returns:
            True if checksums match
        """
        stored_checksum = self._checksums.get(experiment_id)
        if not stored_checksum:
            return False

        # Create new checksum with same parameters
        new_checksum = self.create_checksum(
            experiment_id=f"{experiment_id}_verify",
            code=code,
            data=data,
            config=config,
            seed=seed
        )

        # Compare checksums
        return (
            stored_checksum.code_checksum == new_checksum.code_checksum and
            stored_checksum.data_checksum == new_checksum.data_checksum and
            stored_checksum.config_checksum == new_checksum.config_checksum and
            stored_checksum.seed == new_checksum.seed
        )

    def capture_environment(self) -> EnvironmentInfo:
        """
        Capture current environment information

        Returns:
            EnvironmentInfo object
        """
        import sys

        env_info = EnvironmentInfo(
            python_version=sys.version,
            platform=platform.platform(),
            hardware={
                "processor": platform.processor(),
                "machine": platform.machine()
            }
        )

        # Try to capture library versions
        try:
            import pkg_resources
            installed_packages = {
                pkg.key: pkg.version
                for pkg in pkg_resources.working_set
            }
            env_info.libraries = installed_packages
        except:
            pass

        return env_info

    def get_checksum(self, experiment_id: str) -> Optional[ExperimentChecksum]:
        """Get stored checksum for experiment"""
        return self._checksums.get(experiment_id)

    def get_environment(self, experiment_id: str) -> Optional[EnvironmentInfo]:
        """Get stored environment info for experiment"""
        return self._environments.get(experiment_id)

    def compare_environments(
        self,
        experiment_id_1: str,
        experiment_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare environments between two experiments

        Args:
            experiment_id_1: First experiment
            experiment_id_2: Second experiment

        Returns:
            Dictionary with comparison results
        """
        env1 = self._environments.get(experiment_id_1)
        env2 = self._environments.get(experiment_id_2)

        if not env1 or not env2:
            return {"error": "One or both environments not found"}

        differences = {
            "python_version_match": env1.python_version == env2.python_version,
            "platform_match": env1.platform == env2.platform,
            "library_differences": {}
        }

        # Compare libraries
        all_libs = set(env1.libraries.keys()) | set(env2.libraries.keys())
        for lib in all_libs:
            v1 = env1.libraries.get(lib)
            v2 = env2.libraries.get(lib)
            if v1 != v2:
                differences["library_differences"][lib] = {
                    "env1": v1,
                    "env2": v2
                }

        return differences

    def export_checksum(self, experiment_id: str, format: str = "json") -> Optional[str]:
        """
        Export checksum information

        Args:
            experiment_id: Experiment identifier
            format: Export format (json)

        Returns:
            Serialized checksum or None
        """
        checksum = self._checksums.get(experiment_id)
        env = self._environments.get(experiment_id)

        if not checksum:
            return None

        data = {
            "checksum": checksum.to_dict(),
            "environment": env.to_dict() if env else None
        }

        if format == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def list_checksums(self) -> List[str]:
        """List all stored experiment IDs"""
        return list(self._checksums.keys())
