"""AutoML integration for automated machine learning.

This module provides wrappers for popular AutoML libraries:
- Auto-sklearn: Bayesian optimization with meta-learning
- TPOT: Genetic programming for pipeline optimization
- H2O AutoML: Distributed training with ensemble stacking

It also includes:
- HybridAutoML: Automatic task detection and routing
- AutoMLBenchmark: Framework for comparing different methods

Example:
    >>> from kaggler.automl import AutoSklearnOptimizer
    >>> optimizer = AutoSklearnOptimizer(time_limit=300)
    >>> optimizer.fit(X_train, y_train)
    >>> predictions = optimizer.predict(X_test)

    >>> from kaggler.automl import AutoMLBenchmark
    >>> benchmark = AutoMLBenchmark(methods=['autosklearn', 'tpot', 'h2o'])
    >>> results = benchmark.run(X, y, task_type='classification')
    >>> print(benchmark.get_summary_report())
"""

from .base import AutoMLNotAvailableError, BaseAutoMLWrapper

# Import wrappers with graceful fallback
try:
    from .autosklearn_wrapper import AutoSklearnOptimizer
    AUTOSKLEARN_AVAILABLE = True
except ImportError:
    AUTOSKLEARN_AVAILABLE = False
    AutoSklearnOptimizer = None

try:
    from .tpot_wrapper import TPOTOptimizer
    TPOT_AVAILABLE = True
except ImportError:
    TPOT_AVAILABLE = False
    TPOTOptimizer = None

try:
    from .h2o_wrapper import H2OAutoMLOptimizer
    H2O_AVAILABLE = True
except ImportError:
    H2O_AVAILABLE = False
    H2OAutoMLOptimizer = None

# Always available
from .benchmark import AutoMLBenchmark
from .hybrid import HybridAutoML
from .router import AutoRouter

__all__ = [
    # Base classes
    "BaseAutoMLWrapper",
    "AutoMLNotAvailableError",
    # Wrappers
    "AutoSklearnOptimizer",
    "TPOTOptimizer",
    "H2OAutoMLOptimizer",
    # Hybrid and benchmark
    "HybridAutoML",
    "AutoMLBenchmark",
    "AutoRouter",
]

# Version info
__version__ = "0.2.0"


def get_available_methods():
    """Get list of available AutoML methods.

    Returns:
        methods: List of available method names
    """
    methods = []
    if AUTOSKLEARN_AVAILABLE:
        methods.append("autosklearn")
    if TPOT_AVAILABLE:
        methods.append("tpot")
    if H2O_AVAILABLE:
        methods.append("h2o")
    return methods


def check_installation():
    """Check which AutoML libraries are installed.

    Prints installation status for each library.
    """
    print("AutoML Library Installation Status")
    print("=" * 50)

    libraries = [
        ("Auto-sklearn", AUTOSKLEARN_AVAILABLE, "pip install auto-sklearn"),
        ("TPOT", TPOT_AVAILABLE, "pip install tpot"),
        ("H2O AutoML", H2O_AVAILABLE, "pip install h2o"),
    ]

    for name, available, install_cmd in libraries:
        status = "✓ Installed" if available else "✗ Not installed"
        print(f"{name:20s}: {status}")
        if not available:
            print(f"  Install with: {install_cmd}")

    print("=" * 50)
    print(f"\nAvailable methods: {', '.join(get_available_methods()) or 'None'}")


# Convenience function
def create_optimizer(
    method: str = "auto",
    time_limit: int = 300,
    task_type: str = "classification",
    **kwargs
):
    """Create an AutoML optimizer.

    This is a convenience function that creates the appropriate optimizer
    based on the method name.

    Args:
        method: AutoML method ('autosklearn', 'tpot', 'h2o', 'hybrid', or 'auto')
               'auto' will use HybridAutoML to automatically select the best method
        time_limit: Time limit in seconds
        task_type: 'classification' or 'regression'
        **kwargs: Additional parameters for the optimizer

    Returns:
        optimizer: Initialized AutoML optimizer

    Raises:
        ValueError: If method is unknown
        AutoMLNotAvailableError: If the requested method is not available

    Example:
        >>> optimizer = create_optimizer('tpot', time_limit=600)
        >>> optimizer.fit(X_train, y_train)
    """
    method = method.lower()

    if method == "auto" or method == "hybrid":
        return HybridAutoML(
            time_limit=time_limit,
            task_type=task_type,
            **kwargs
        )

    elif method == "autosklearn":
        if not AUTOSKLEARN_AVAILABLE:
            raise AutoMLNotAvailableError("Auto-sklearn", "auto-sklearn")
        return AutoSklearnOptimizer(
            time_limit=time_limit,
            task_type=task_type,
            **kwargs
        )

    elif method == "tpot":
        if not TPOT_AVAILABLE:
            raise AutoMLNotAvailableError("TPOT", "tpot")
        return TPOTOptimizer(
            time_limit=time_limit,
            task_type=task_type,
            **kwargs
        )

    elif method == "h2o":
        if not H2O_AVAILABLE:
            raise AutoMLNotAvailableError("H2O AutoML", "h2o")
        return H2OAutoMLOptimizer(
            time_limit=time_limit,
            task_type=task_type,
            **kwargs
        )

    else:
        available = get_available_methods()
        raise ValueError(
            f"Unknown method '{method}'. "
            f"Available methods: {', '.join(available + ['auto', 'hybrid'])}"
        )
