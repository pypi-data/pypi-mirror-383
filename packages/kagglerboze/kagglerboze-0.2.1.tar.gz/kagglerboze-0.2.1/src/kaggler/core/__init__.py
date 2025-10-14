"""
KagglerBoze Core Module - GEPA Implementation

This module implements the Genetic-Pareto Reflective Evolution algorithm
for prompt optimization without fine-tuning.

Based on: arXiv:2507.19457
"""

from .evolution import EvolutionEngine, EvolutionConfig
from .pareto import ParetoOptimizer
from .reflection import ReflectionEngine
from .mutation import MutationStrategy
from .crossover import CrossoverOperator

__all__ = [
    "EvolutionEngine",
    "EvolutionConfig",
    "ParetoOptimizer",
    "ReflectionEngine",
    "MutationStrategy",
    "CrossoverOperator",
]

__version__ = "0.1.0"
