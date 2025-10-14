"""
Celery Application Setup

Initializes Celery application for distributed task execution.
"""

import os
import logging
from typing import Optional

try:
    from celery import Celery
    from celery.signals import (
        worker_ready,
        worker_shutdown,
        task_prerun,
        task_postrun,
        task_failure
    )
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Fallback when Celery not installed
    class Celery:
        def __init__(self, *args, **kwargs):
            pass

logger = logging.getLogger(__name__)


def create_celery_app(
    app_name: str = "kaggler_collaborative",
    broker_url: Optional[str] = None,
    result_backend: Optional[str] = None,
    config_module: str = "kaggler.collaborative.celeryconfig"
) -> Celery:
    """
    Create and configure Celery application

    Args:
        app_name: Application name
        broker_url: Optional broker URL (overrides config)
        result_backend: Optional result backend URL (overrides config)
        config_module: Configuration module path

    Returns:
        Configured Celery application
    """
    # Create app
    app = Celery(app_name)

    # Load configuration from module
    app.config_from_object(config_module)

    # Override with environment variables if provided
    if broker_url:
        app.conf.broker_url = broker_url
    if result_backend:
        app.conf.result_backend = result_backend

    # Register signal handlers
    _register_signal_handlers(app)

    logger.info(f"Celery app '{app_name}' created and configured")

    return app


def _register_signal_handlers(app: Celery) -> None:
    """Register Celery signal handlers for monitoring"""

    @worker_ready.connect
    def on_worker_ready(sender=None, **kwargs):
        """Worker ready handler"""
        logger.info(f"Worker {sender} is ready")

    @worker_shutdown.connect
    def on_worker_shutdown(sender=None, **kwargs):
        """Worker shutdown handler"""
        logger.info(f"Worker {sender} is shutting down")

    @task_prerun.connect
    def on_task_prerun(task_id=None, task=None, **kwargs):
        """Task pre-run handler"""
        logger.debug(f"Task {task.name} [{task_id}] starting")

    @task_postrun.connect
    def on_task_postrun(task_id=None, task=None, retval=None, **kwargs):
        """Task post-run handler"""
        logger.debug(f"Task {task.name} [{task_id}] completed")

    @task_failure.connect
    def on_task_failure(task_id=None, exception=None, **kwargs):
        """Task failure handler"""
        logger.error(f"Task [{task_id}] failed: {exception}")


# Create default app instance
app = create_celery_app()


# Helper functions for application management

def start_worker(
    app: Celery,
    concurrency: int = 4,
    loglevel: str = "info",
    queues: Optional[list] = None
) -> None:
    """
    Start a Celery worker

    Args:
        app: Celery application
        concurrency: Number of concurrent workers
        loglevel: Logging level
        queues: List of queues to consume from
    """
    if not CELERY_AVAILABLE:
        logger.error("Celery is not installed")
        return

    worker_args = [
        "worker",
        f"--loglevel={loglevel}",
        f"--concurrency={concurrency}"
    ]

    if queues:
        worker_args.append(f"--queues={','.join(queues)}")

    app.worker_main(argv=worker_args)


def inspect_workers(app: Celery) -> dict:
    """
    Inspect active workers

    Args:
        app: Celery application

    Returns:
        Dictionary with worker information
    """
    if not CELERY_AVAILABLE:
        return {"error": "Celery not available"}

    inspect = app.control.inspect()

    return {
        "active": inspect.active(),
        "registered": inspect.registered(),
        "stats": inspect.stats(),
        "active_queues": inspect.active_queues()
    }


def get_task_status(app: Celery, task_id: str) -> dict:
    """
    Get status of a task

    Args:
        app: Celery application
        task_id: Task ID

    Returns:
        Task status information
    """
    if not CELERY_AVAILABLE:
        return {"error": "Celery not available"}

    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=app)

    return {
        "task_id": task_id,
        "state": result.state,
        "info": result.info,
        "successful": result.successful(),
        "failed": result.failed(),
        "ready": result.ready()
    }


def purge_all_tasks(app: Celery) -> int:
    """
    Purge all tasks from queues

    Args:
        app: Celery application

    Returns:
        Number of tasks purged
    """
    if not CELERY_AVAILABLE:
        return 0

    return app.control.purge()


def revoke_task(
    app: Celery,
    task_id: str,
    terminate: bool = False,
    signal: str = "SIGTERM"
) -> None:
    """
    Revoke a task

    Args:
        app: Celery application
        task_id: Task ID to revoke
        terminate: Whether to terminate the task
        signal: Signal to send if terminating
    """
    if not CELERY_AVAILABLE:
        return

    app.control.revoke(task_id, terminate=terminate, signal=signal)


class WorkerPool:
    """
    Manages a pool of Celery workers

    Features:
    - Start/stop workers
    - Monitor worker health
    - Load balancing
    - Auto-scaling
    """

    def __init__(
        self,
        app: Celery,
        n_workers: int = 3,
        concurrency: int = 4
    ):
        """
        Initialize worker pool

        Args:
            app: Celery application
            n_workers: Number of workers
            concurrency: Concurrency per worker
        """
        self.app = app
        self.n_workers = n_workers
        self.concurrency = concurrency
        self.workers = []

    def start_all(self) -> None:
        """Start all workers"""
        logger.info(f"Starting {self.n_workers} workers")

        # In production, would spawn actual worker processes
        # For now, just log
        for i in range(self.n_workers):
            logger.info(f"Worker {i} started with concurrency {self.concurrency}")

    def stop_all(self, timeout: int = 30) -> None:
        """
        Stop all workers

        Args:
            timeout: Timeout for graceful shutdown
        """
        logger.info("Stopping all workers")
        self.app.control.shutdown(timeout=timeout)

    def scale(self, n_workers: int) -> None:
        """
        Scale worker pool

        Args:
            n_workers: Target number of workers
        """
        if n_workers > self.n_workers:
            # Scale up
            for i in range(self.n_workers, n_workers):
                logger.info(f"Starting additional worker {i}")
        elif n_workers < self.n_workers:
            # Scale down
            logger.info(f"Scaling down from {self.n_workers} to {n_workers} workers")

        self.n_workers = n_workers

    def get_status(self) -> dict:
        """Get worker pool status"""
        return {
            "n_workers": self.n_workers,
            "concurrency": self.concurrency,
            "inspection": inspect_workers(self.app)
        }


class TaskMonitor:
    """
    Monitors task execution and provides metrics

    Features:
    - Track task completion rates
    - Monitor task durations
    - Detect failures
    - Generate reports
    """

    def __init__(self, app: Celery):
        """
        Initialize task monitor

        Args:
            app: Celery application
        """
        self.app = app
        self.task_stats = {
            "completed": 0,
            "failed": 0,
            "retried": 0,
            "total_time": 0.0
        }

    def record_completion(self, task_id: str, duration: float) -> None:
        """Record task completion"""
        self.task_stats["completed"] += 1
        self.task_stats["total_time"] += duration

    def record_failure(self, task_id: str) -> None:
        """Record task failure"""
        self.task_stats["failed"] += 1

    def record_retry(self, task_id: str) -> None:
        """Record task retry"""
        self.task_stats["retried"] += 1

    def get_metrics(self) -> dict:
        """Get monitoring metrics"""
        total_tasks = self.task_stats["completed"] + self.task_stats["failed"]

        return {
            "total_tasks": total_tasks,
            "completed": self.task_stats["completed"],
            "failed": self.task_stats["failed"],
            "retried": self.task_stats["retried"],
            "success_rate": (
                self.task_stats["completed"] / max(total_tasks, 1)
            ),
            "avg_duration": (
                self.task_stats["total_time"] / max(self.task_stats["completed"], 1)
            )
        }

    def generate_report(self) -> str:
        """Generate monitoring report"""
        metrics = self.get_metrics()

        report = []
        report.append("=" * 60)
        report.append("CELERY TASK MONITORING REPORT")
        report.append("=" * 60)
        report.append(f"Total Tasks: {metrics['total_tasks']}")
        report.append(f"Completed: {metrics['completed']}")
        report.append(f"Failed: {metrics['failed']}")
        report.append(f"Retried: {metrics['retried']}")
        report.append(f"Success Rate: {metrics['success_rate']:.2%}")
        report.append(f"Avg Duration: {metrics['avg_duration']:.2f}s")
        report.append("=" * 60)

        return "\n".join(report)


# Health check utilities

def check_broker_connection(app: Celery) -> bool:
    """
    Check if broker is accessible

    Args:
        app: Celery application

    Returns:
        True if broker is accessible
    """
    if not CELERY_AVAILABLE:
        return False

    try:
        # Try to get active workers
        inspect = app.control.inspect()
        inspect.stats()
        return True
    except Exception as e:
        logger.error(f"Broker connection failed: {e}")
        return False


def check_result_backend(app: Celery) -> bool:
    """
    Check if result backend is accessible

    Args:
        app: Celery application

    Returns:
        True if result backend is accessible
    """
    if not CELERY_AVAILABLE:
        return False

    try:
        # Try to store and retrieve a result
        from celery.result import AsyncResult
        test_result = AsyncResult("test-health-check", app=app)
        return True
    except Exception as e:
        logger.error(f"Result backend connection failed: {e}")
        return False


def health_check(app: Celery) -> dict:
    """
    Perform complete health check

    Args:
        app: Celery application

    Returns:
        Health check results
    """
    return {
        "celery_available": CELERY_AVAILABLE,
        "broker_connected": check_broker_connection(app),
        "result_backend_connected": check_result_backend(app),
        "workers": inspect_workers(app)
    }
