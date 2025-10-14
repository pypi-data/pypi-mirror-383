"""
Communication Protocol for Collaborative Evolution

Defines message types, serialization, and communication patterns
between coordinator and workers.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import time
import pickle
import base64
from datetime import datetime


class MessageType(Enum):
    """Types of messages in the protocol"""
    # Registration
    WORKER_REGISTER = "worker_register"
    WORKER_REGISTERED = "worker_registered"

    # Task Distribution
    TASK_ASSIGN = "task_assign"
    TASK_RESULT = "task_result"
    TASK_FAILED = "task_failed"

    # Individual Sharing
    SHARE_INDIVIDUAL = "share_individual"
    SHARE_POPULATION = "share_population"
    BROADCAST_BEST = "broadcast_best"

    # Synchronization
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    GENERATION_COMPLETE = "generation_complete"

    # Health Monitoring
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"
    WORKER_FAILED = "worker_failed"

    # Control
    START_EVOLUTION = "start_evolution"
    STOP_EVOLUTION = "stop_evolution"
    PAUSE_EVOLUTION = "pause_evolution"
    RESUME_EVOLUTION = "resume_evolution"


@dataclass
class IndividualData:
    """Serializable representation of an Individual"""
    id: str
    prompt: str
    fitness_scores: Dict[str, float]
    generation: int
    parent_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndividualData":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Message:
    """Communication message between coordinator and workers"""
    type: MessageType
    sender_id: str
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)
    message_id: Optional[str] = None

    def __post_init__(self):
        if self.message_id is None:
            import uuid
            self.message_id = str(uuid.uuid4())
        # Ensure type is MessageType enum
        if isinstance(self.type, str):
            self.type = MessageType(self.type)

    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps({
            "type": self.type.value,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp,
            "data": self.data,
            "message_id": self.message_id
        })

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Deserialize from JSON string"""
        data = json.loads(json_str)
        return cls(
            type=MessageType(data["type"]),
            sender_id=data["sender_id"],
            timestamp=data["timestamp"],
            data=data["data"],
            message_id=data.get("message_id")
        )


def serialize_individual(individual: Any) -> str:
    """
    Serialize Individual object to base64-encoded string

    Args:
        individual: Individual object from evolution.py

    Returns:
        Base64-encoded pickle string
    """
    try:
        # Create IndividualData from Individual
        ind_data = IndividualData(
            id=individual.id,
            prompt=individual.prompt,
            fitness_scores=individual.fitness_scores.copy(),
            generation=individual.generation,
            parent_ids=individual.parent_ids.copy(),
            metadata={}
        )

        # Serialize to JSON (more portable than pickle)
        json_str = json.dumps(ind_data.to_dict())
        return base64.b64encode(json_str.encode()).decode()

    except Exception as e:
        raise ValueError(f"Failed to serialize individual: {e}")


def deserialize_individual(data: str) -> IndividualData:
    """
    Deserialize Individual from base64-encoded string

    Args:
        data: Base64-encoded string

    Returns:
        IndividualData object
    """
    try:
        json_str = base64.b64decode(data.encode()).decode()
        ind_dict = json.loads(json_str)
        return IndividualData.from_dict(ind_dict)

    except Exception as e:
        raise ValueError(f"Failed to deserialize individual: {e}")


class CommunicationProtocol:
    """
    Manages communication protocol between coordinator and workers

    Features:
    - Message routing
    - Heartbeat monitoring
    - Failure detection
    - Message ordering
    """

    def __init__(self, node_id: str, heartbeat_interval: float = 10.0):
        """
        Initialize protocol handler

        Args:
            node_id: Unique identifier for this node
            heartbeat_interval: Seconds between heartbeats
        """
        self.node_id = node_id
        self.heartbeat_interval = heartbeat_interval
        self.last_heartbeat: Dict[str, float] = {}
        self.message_queue: List[Message] = []
        self.sent_messages: Dict[str, Message] = {}
        self.received_messages: Dict[str, Message] = {}

    def create_message(
        self,
        msg_type: MessageType,
        data: Dict[str, Any] = None
    ) -> Message:
        """Create a new message"""
        return Message(
            type=msg_type,
            sender_id=self.node_id,
            data=data or {}
        )

    def send_message(self, message: Message) -> None:
        """
        Send message (store for tracking)

        In production, this would actually send via Redis/message queue
        """
        self.sent_messages[message.message_id] = message
        self.message_queue.append(message)

    def receive_message(self, message: Message) -> None:
        """
        Receive and process message

        Args:
            message: Received message
        """
        self.received_messages[message.message_id] = message

        # Update heartbeat if applicable
        if message.type == MessageType.HEARTBEAT:
            self.last_heartbeat[message.sender_id] = time.time()

    def send_heartbeat(self) -> Message:
        """Send heartbeat message"""
        message = self.create_message(
            MessageType.HEARTBEAT,
            {"status": "alive", "timestamp": time.time()}
        )
        self.send_message(message)
        return message

    def check_heartbeats(self, timeout: float = 30.0) -> List[str]:
        """
        Check for failed nodes based on heartbeat timeout

        Args:
            timeout: Seconds before considering node failed

        Returns:
            List of failed node IDs
        """
        current_time = time.time()
        failed_nodes = []

        for node_id, last_beat in self.last_heartbeat.items():
            if current_time - last_beat > timeout:
                failed_nodes.append(node_id)

        return failed_nodes

    def create_task_message(
        self,
        task_type: str,
        task_data: Dict[str, Any]
    ) -> Message:
        """Create task assignment message"""
        return self.create_message(
            MessageType.TASK_ASSIGN,
            {
                "task_type": task_type,
                "task_data": task_data,
                "assigned_at": time.time()
            }
        )

    def create_result_message(
        self,
        task_id: str,
        result_data: Dict[str, Any],
        success: bool = True
    ) -> Message:
        """Create task result message"""
        msg_type = MessageType.TASK_RESULT if success else MessageType.TASK_FAILED
        return self.create_message(
            msg_type,
            {
                "task_id": task_id,
                "result_data": result_data,
                "completed_at": time.time()
            }
        )

    def create_share_individual_message(
        self,
        individual: Any
    ) -> Message:
        """Create message to share individual"""
        serialized = serialize_individual(individual)
        return self.create_message(
            MessageType.SHARE_INDIVIDUAL,
            {
                "individual": serialized,
                "fitness_scores": individual.fitness_scores,
                "generation": individual.generation
            }
        )

    def create_share_population_message(
        self,
        population: List[Any],
        generation: int
    ) -> Message:
        """Create message to share entire population"""
        serialized_pop = [serialize_individual(ind) for ind in population]
        return self.create_message(
            MessageType.SHARE_POPULATION,
            {
                "population": serialized_pop,
                "generation": generation,
                "population_size": len(population)
            }
        )

    def extract_individuals_from_message(self, message: Message) -> List[IndividualData]:
        """Extract individuals from a message"""
        individuals = []

        if message.type == MessageType.SHARE_INDIVIDUAL:
            ind_data = deserialize_individual(message.data["individual"])
            individuals.append(ind_data)

        elif message.type == MessageType.SHARE_POPULATION:
            for serialized in message.data["population"]:
                ind_data = deserialize_individual(serialized)
                individuals.append(ind_data)

        elif message.type == MessageType.BROADCAST_BEST:
            for serialized in message.data.get("best_individuals", []):
                ind_data = deserialize_individual(serialized)
                individuals.append(ind_data)

        return individuals

    def get_pending_messages(self, msg_type: Optional[MessageType] = None) -> List[Message]:
        """
        Get pending messages, optionally filtered by type

        Args:
            msg_type: Optional message type filter

        Returns:
            List of pending messages
        """
        if msg_type:
            return [msg for msg in self.message_queue if msg.type == msg_type]
        return self.message_queue.copy()

    def clear_message_queue(self) -> None:
        """Clear the message queue"""
        self.message_queue.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get protocol statistics"""
        return {
            "node_id": self.node_id,
            "messages_sent": len(self.sent_messages),
            "messages_received": len(self.received_messages),
            "pending_messages": len(self.message_queue),
            "tracked_nodes": len(self.last_heartbeat),
            "active_nodes": len([
                node_id for node_id, last_beat in self.last_heartbeat.items()
                if time.time() - last_beat < 30.0
            ])
        }


class WorkStealingProtocol:
    """
    Implements work stealing for load balancing

    Workers can steal tasks from overloaded workers
    """

    def __init__(self):
        self.worker_loads: Dict[str, int] = {}
        self.task_assignments: Dict[str, str] = {}  # task_id -> worker_id

    def assign_task(self, task_id: str, worker_id: str) -> None:
        """Assign task to worker"""
        self.task_assignments[task_id] = worker_id
        self.worker_loads[worker_id] = self.worker_loads.get(worker_id, 0) + 1

    def complete_task(self, task_id: str) -> None:
        """Mark task as completed"""
        if task_id in self.task_assignments:
            worker_id = self.task_assignments[task_id]
            self.worker_loads[worker_id] = max(0, self.worker_loads.get(worker_id, 0) - 1)
            del self.task_assignments[task_id]

    def get_overloaded_workers(self, threshold: int = 10) -> List[str]:
        """Get workers with load above threshold"""
        return [
            worker_id for worker_id, load in self.worker_loads.items()
            if load > threshold
        ]

    def get_underloaded_workers(self, threshold: int = 3) -> List[str]:
        """Get workers with load below threshold"""
        return [
            worker_id for worker_id, load in self.worker_loads.items()
            if load < threshold
        ]

    def should_steal_work(self, worker_id: str, steal_threshold: float = 0.5) -> bool:
        """
        Determine if worker should steal work

        Args:
            worker_id: Worker considering stealing
            steal_threshold: Ratio of avg load to trigger stealing

        Returns:
            True if worker should attempt work stealing
        """
        if not self.worker_loads:
            return False

        my_load = self.worker_loads.get(worker_id, 0)
        avg_load = sum(self.worker_loads.values()) / len(self.worker_loads)

        return my_load < avg_load * steal_threshold

    def get_steal_candidate(self, worker_id: str) -> Optional[str]:
        """
        Get best candidate worker to steal from

        Returns worker with highest load (excluding self)
        """
        candidates = {
            wid: load for wid, load in self.worker_loads.items()
            if wid != worker_id and load > 0
        }

        if not candidates:
            return None

        return max(candidates, key=candidates.get)
