"""
Individual Sharing Protocol and Advanced Merge Strategies

Implements protocols for exchanging individuals between workers and
advanced merging strategies for distributed populations.
"""

from typing import List, Dict, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
import time
import numpy as np
from collections import defaultdict

from ..core.evolution import Individual
from .protocol import CommunicationProtocol, Message, MessageType, serialize_individual
from .merge import MergeStrategy


@dataclass
class SharingPolicy:
    """Policy for sharing individuals between workers"""
    share_frequency: int = 5  # Share every N generations
    share_count: int = 3  # Number of individuals to share
    share_threshold: float = 0.7  # Only share if fitness > threshold * max_fitness
    enable_diversity: bool = True  # Prefer diverse individuals
    bidirectional: bool = True  # Enable bidirectional sharing

    def should_share(self, generation: int) -> bool:
        """Check if should share this generation"""
        return generation % self.share_frequency == 0

    def filter_candidates(
        self,
        candidates: List[Individual],
        max_fitness: float
    ) -> List[Individual]:
        """Filter candidates based on policy"""
        if not candidates:
            return []

        # Filter by threshold
        threshold = self.share_threshold * max_fitness
        filtered = [
            ind for ind in candidates
            if ind.fitness_scores.get("accuracy", 0.0) >= threshold
        ]

        return filtered


class SharingProtocol:
    """
    Protocol for sharing individuals between workers

    Features:
    - Selective sharing based on fitness
    - Diversity-aware sharing
    - Anti-duplicate mechanisms
    - Bandwidth optimization
    """

    def __init__(
        self,
        node_id: str,
        policy: Optional[SharingPolicy] = None
    ):
        """
        Initialize sharing protocol

        Args:
            node_id: Unique node identifier
            policy: Sharing policy
        """
        self.node_id = node_id
        self.policy = policy or SharingPolicy()
        self.shared_individuals: Set[str] = set()  # Track shared IDs
        self.received_individuals: Dict[str, Individual] = {}
        self.sharing_history: List[Dict[str, Any]] = []

    def select_individuals_to_share(
        self,
        population: List[Individual],
        generation: int
    ) -> List[Individual]:
        """
        Select individuals to share with others

        Args:
            population: Local population
            generation: Current generation

        Returns:
            List of individuals to share
        """
        if not self.policy.should_share(generation):
            return []

        if not population:
            return []

        # Get max fitness
        max_fitness = max(
            ind.fitness_scores.get("accuracy", 0.0)
            for ind in population
        )

        # Filter candidates
        candidates = self.policy.filter_candidates(population, max_fitness)

        # Exclude already shared
        candidates = [
            ind for ind in candidates
            if ind.id not in self.shared_individuals
        ]

        if not candidates:
            return []

        # Select diverse individuals if enabled
        if self.policy.enable_diversity:
            selected = self._select_diverse_individuals(
                candidates,
                self.policy.share_count
            )
        else:
            # Just take top N
            selected = sorted(
                candidates,
                key=lambda x: x.fitness_scores.get("accuracy", 0.0),
                reverse=True
            )[:self.policy.share_count]

        # Mark as shared
        for ind in selected:
            self.shared_individuals.add(ind.id)

        # Record sharing event
        self.sharing_history.append({
            "generation": generation,
            "count": len(selected),
            "avg_fitness": np.mean([
                ind.fitness_scores.get("accuracy", 0.0)
                for ind in selected
            ]),
            "timestamp": time.time()
        })

        return selected

    def _select_diverse_individuals(
        self,
        candidates: List[Individual],
        n: int
    ) -> List[Individual]:
        """
        Select diverse individuals using greedy diversity selection

        Args:
            candidates: Pool of candidates
            n: Number to select

        Returns:
            Selected diverse individuals
        """
        if len(candidates) <= n:
            return candidates

        selected = []
        remaining = candidates.copy()

        # Start with best individual
        best = max(remaining, key=lambda x: x.fitness_scores.get("accuracy", 0.0))
        selected.append(best)
        remaining.remove(best)

        # Greedily select most diverse
        while len(selected) < n and remaining:
            best_candidate = None
            best_score = -1

            for candidate in remaining:
                # Compute diversity score (weighted by fitness and distance)
                fitness = candidate.fitness_scores.get("accuracy", 0.0)

                # Min distance to selected
                min_dist = min(
                    self._compute_distance(candidate, sel)
                    for sel in selected
                )

                # Combined score
                score = fitness * 0.5 + min_dist * 0.5

                if score > best_score:
                    best_score = score
                    best_candidate = candidate

            if best_candidate:
                selected.append(best_candidate)
                remaining.remove(best_candidate)

        return selected

    def _compute_distance(self, ind1: Individual, ind2: Individual) -> float:
        """
        Compute distance between two individuals

        Uses prompt length difference as simple distance metric
        """
        return abs(len(ind1.prompt) - len(ind2.prompt)) / 100.0

    def integrate_received_individuals(
        self,
        received: List[Individual],
        local_population: List[Individual],
        strategy: str = "replace_worst"
    ) -> List[Individual]:
        """
        Integrate received individuals into local population

        Args:
            received: Received individuals
            local_population: Local population
            strategy: Integration strategy

        Returns:
            Updated population
        """
        if not received:
            return local_population

        # Store received individuals
        for ind in received:
            self.received_individuals[ind.id] = ind

        # Apply integration strategy
        if strategy == "replace_worst":
            return self._replace_worst_integration(received, local_population)
        elif strategy == "tournament":
            return self._tournament_integration(received, local_population)
        elif strategy == "append":
            return local_population + received
        else:
            return self._replace_worst_integration(received, local_population)

    def _replace_worst_integration(
        self,
        received: List[Individual],
        local_population: List[Individual]
    ) -> List[Individual]:
        """Replace worst individuals with received ones"""
        # Sort local population
        sorted_pop = sorted(
            local_population,
            key=lambda x: x.fitness_scores.get("accuracy", 0.0),
            reverse=True
        )

        # Replace worst with received
        n_replace = min(len(received), len(local_population) // 4)
        updated = sorted_pop[:-n_replace] + received[:n_replace]

        return updated

    def _tournament_integration(
        self,
        received: List[Individual],
        local_population: List[Individual]
    ) -> List[Individual]:
        """Integrate via tournament selection"""
        combined = local_population + received

        # Run tournament to select best
        tournament_size = 3
        selected = []

        target_size = len(local_population)

        while len(selected) < target_size:
            tournament = np.random.choice(combined, tournament_size, replace=False)
            winner = max(
                tournament,
                key=lambda x: x.fitness_scores.get("accuracy", 0.0)
            )
            if winner not in selected:
                selected.append(winner)

        return selected[:target_size]

    def get_sharing_statistics(self) -> Dict[str, Any]:
        """Get sharing statistics"""
        return {
            "total_shared": len(self.shared_individuals),
            "total_received": len(self.received_individuals),
            "sharing_events": len(self.sharing_history),
            "avg_shared_per_event": (
                np.mean([h["count"] for h in self.sharing_history])
                if self.sharing_history else 0
            )
        }


class P2PSharingNetwork:
    """
    Peer-to-peer sharing network for decentralized collaboration

    Enables workers to share directly with each other without
    going through coordinator.
    """

    def __init__(self):
        self.peers: Dict[str, CommunicationProtocol] = {}
        self.connections: Dict[str, List[str]] = defaultdict(list)
        self.routing_table: Dict[str, str] = {}

    def register_peer(
        self,
        peer_id: str,
        protocol: CommunicationProtocol
    ) -> None:
        """Register a peer in the network"""
        self.peers[peer_id] = protocol
        self.connections[peer_id] = []

    def connect_peers(self, peer1_id: str, peer2_id: str) -> None:
        """Establish connection between two peers"""
        if peer1_id not in self.connections[peer2_id]:
            self.connections[peer1_id].append(peer2_id)
            self.connections[peer2_id].append(peer1_id)

    def broadcast_individual(
        self,
        sender_id: str,
        individual: Individual
    ) -> None:
        """Broadcast individual to all connected peers"""
        if sender_id not in self.peers:
            return

        sender_protocol = self.peers[sender_id]

        # Send to all connected peers
        for peer_id in self.connections.get(sender_id, []):
            if peer_id in self.peers:
                message = sender_protocol.create_share_individual_message(individual)
                self.peers[peer_id].receive_message(message)

    def targeted_share(
        self,
        sender_id: str,
        target_id: str,
        individuals: List[Individual]
    ) -> bool:
        """Share individuals with specific target"""
        if sender_id not in self.peers or target_id not in self.peers:
            return False

        sender_protocol = self.peers[sender_id]
        target_protocol = self.peers[target_id]

        # Send population message
        message = sender_protocol.create_share_population_message(
            individuals,
            generation=0
        )
        target_protocol.receive_message(message)

        return True

    def get_network_topology(self) -> Dict[str, Any]:
        """Get network topology information"""
        return {
            "total_peers": len(self.peers),
            "total_connections": sum(len(conns) for conns in self.connections.values()) // 2,
            "connections": dict(self.connections),
            "avg_degree": (
                np.mean([len(conns) for conns in self.connections.values()])
                if self.connections else 0
            )
        }


class AdaptiveSharingStrategy:
    """
    Adaptive sharing strategy that adjusts based on performance

    Features:
    - Adjust sharing frequency based on improvement rate
    - Adjust sharing count based on diversity
    - Learn which peers provide best individuals
    """

    def __init__(self, initial_policy: Optional[SharingPolicy] = None):
        self.policy = initial_policy or SharingPolicy()
        self.performance_history: List[float] = []
        self.diversity_history: List[float] = []
        self.peer_quality: Dict[str, float] = defaultdict(float)
        self.adaptation_interval = 10

    def update_policy(
        self,
        generation: int,
        population: List[Individual],
        improvement_rate: float
    ) -> None:
        """
        Update sharing policy based on current state

        Args:
            generation: Current generation
            population: Current population
            improvement_rate: Recent improvement rate
        """
        if generation % self.adaptation_interval != 0:
            return

        # Track performance
        avg_fitness = np.mean([
            ind.fitness_scores.get("accuracy", 0.0)
            for ind in population
        ])
        self.performance_history.append(avg_fitness)

        # Track diversity
        diversity = self._compute_diversity(population)
        self.diversity_history.append(diversity)

        # Adjust sharing frequency
        if improvement_rate < 0.01:  # Stuck
            # Share more frequently to get new genetic material
            self.policy.share_frequency = max(2, self.policy.share_frequency - 1)
            self.policy.share_count = min(10, self.policy.share_count + 1)
        elif improvement_rate > 0.1:  # Improving well
            # Share less frequently, focus on local search
            self.policy.share_frequency = min(10, self.policy.share_frequency + 1)

        # Adjust diversity preference
        if diversity < 0.5:  # Low diversity
            self.policy.enable_diversity = True
            self.policy.share_threshold = max(0.5, self.policy.share_threshold - 0.1)
        else:  # High diversity
            self.policy.enable_diversity = False
            self.policy.share_threshold = min(0.9, self.policy.share_threshold + 0.1)

    def _compute_diversity(self, population: List[Individual]) -> float:
        """Compute population diversity"""
        if len(population) < 2:
            return 0.0

        lengths = [len(ind.prompt) for ind in population]
        return float(np.std(lengths) / (np.mean(lengths) + 1e-6))

    def rank_peers(self, peer_id: str) -> float:
        """Get quality ranking for a peer"""
        return self.peer_quality.get(peer_id, 0.5)

    def update_peer_quality(
        self,
        peer_id: str,
        received_individual: Individual,
        improvement: bool
    ) -> None:
        """Update peer quality based on contribution"""
        if improvement:
            self.peer_quality[peer_id] += 0.1
        else:
            self.peer_quality[peer_id] = max(0.0, self.peer_quality[peer_id] - 0.05)

    def get_strategy_statistics(self) -> Dict[str, Any]:
        """Get strategy statistics"""
        return {
            "current_policy": {
                "share_frequency": self.policy.share_frequency,
                "share_count": self.policy.share_count,
                "share_threshold": self.policy.share_threshold,
                "enable_diversity": self.policy.enable_diversity
            },
            "performance_trend": (
                self.performance_history[-1] - self.performance_history[0]
                if len(self.performance_history) > 1 else 0.0
            ),
            "diversity_trend": (
                self.diversity_history[-1] - self.diversity_history[0]
                if len(self.diversity_history) > 1 else 0.0
            ),
            "top_peers": sorted(
                self.peer_quality.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }


class BandwidthOptimizer:
    """
    Optimizes bandwidth usage for distributed sharing

    Features:
    - Compress individuals before sending
    - Batch multiple individuals
    - Prioritize high-value individuals
    - Rate limiting
    """

    def __init__(
        self,
        max_bandwidth: float = 1000.0,  # KB/s
        batch_size: int = 10
    ):
        self.max_bandwidth = max_bandwidth
        self.batch_size = batch_size
        self.bytes_sent = 0
        self.bytes_received = 0
        self.last_reset = time.time()

    def can_send(self, size_bytes: float) -> bool:
        """Check if can send given bandwidth constraints"""
        # Reset counter every second
        if time.time() - self.last_reset > 1.0:
            self.bytes_sent = 0
            self.last_reset = time.time()

        return (self.bytes_sent + size_bytes) <= (self.max_bandwidth * 1024)

    def batch_individuals(
        self,
        individuals: List[Individual]
    ) -> List[List[Individual]]:
        """Batch individuals for efficient transmission"""
        batches = []

        for i in range(0, len(individuals), self.batch_size):
            batch = individuals[i:i + self.batch_size]
            batches.append(batch)

        return batches

    def compress_individual(self, individual: Individual) -> str:
        """Compress individual for transmission"""
        # In production, use actual compression (gzip, etc.)
        # For now, just serialize
        return serialize_individual(individual)

    def record_sent(self, size_bytes: float) -> None:
        """Record bytes sent"""
        self.bytes_sent += size_bytes

    def record_received(self, size_bytes: float) -> None:
        """Record bytes received"""
        self.bytes_received += size_bytes

    def get_statistics(self) -> Dict[str, Any]:
        """Get bandwidth statistics"""
        return {
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "bandwidth_utilization": self.bytes_sent / (self.max_bandwidth * 1024),
            "max_bandwidth_kb_s": self.max_bandwidth
        }
