"""AutoML comparison framework (alias for benchmark module).

This module provides the same functionality as benchmark.py for backward compatibility.
Use AutoMLBenchmark for comparing different AutoML methods.
"""

from .benchmark import AutoMLBenchmark

# Re-export for convenience
__all__ = ["AutoMLBenchmark"]
