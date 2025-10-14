"""
Celery Configuration for Collaborative Evolution

Configures Celery for distributed task execution with Redis backend.
"""

import os
from kombu import Queue

# Broker settings
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Task serialization
TASK_SERIALIZER = "json"
RESULT_SERIALIZER = "json"
ACCEPT_CONTENT = ["json"]
TIMEZONE = "UTC"
ENABLE_UTC = True

# Task result expiration
RESULT_EXPIRES = 3600  # 1 hour

# Task execution settings
TASK_ACKS_LATE = True
TASK_REJECT_ON_WORKER_LOST = True
TASK_TIME_LIMIT = 3600  # 1 hour hard limit
TASK_SOFT_TIME_LIMIT = 3300  # 55 minutes soft limit

# Worker settings
WORKER_PREFETCH_MULTIPLIER = 1  # One task at a time for better load balancing
WORKER_MAX_TASKS_PER_CHILD = 100  # Restart worker after 100 tasks
WORKER_DISABLE_RATE_LIMITS = False

# Queue configuration
TASK_DEFAULT_QUEUE = "evolution"
TASK_DEFAULT_EXCHANGE = "evolution"
TASK_DEFAULT_ROUTING_KEY = "evolution.default"

TASK_QUEUES = (
    Queue("evolution", routing_key="evolution.#"),
    Queue("evaluation", routing_key="evaluation.#"),
    Queue("priority", routing_key="priority.#"),
)

# Task routing
TASK_ROUTES = {
    "kaggler.collaborative.tasks.evaluate_individual": {
        "queue": "evaluation",
        "routing_key": "evaluation.individual"
    },
    "kaggler.collaborative.tasks.evaluate_population": {
        "queue": "evaluation",
        "routing_key": "evaluation.population"
    },
    "kaggler.collaborative.tasks.run_local_evolution": {
        "queue": "evolution",
        "routing_key": "evolution.local"
    },
    "kaggler.collaborative.tasks.merge_populations": {
        "queue": "priority",
        "routing_key": "priority.merge"
    },
}

# Monitoring
WORKER_SEND_TASK_EVENTS = True
TASK_SEND_SENT_EVENT = True

# Optimization
BROKER_POOL_LIMIT = 10
BROKER_CONNECTION_TIMEOUT = 10
BROKER_CONNECTION_RETRY = True
BROKER_CONNECTION_MAX_RETRIES = 10

# Retry policy
TASK_AUTORETRY_FOR = (Exception,)
TASK_RETRY_KWARGS = {"max_retries": 3}
TASK_RETRY_BACKOFF = True
TASK_RETRY_BACKOFF_MAX = 600  # 10 minutes max
TASK_RETRY_JITTER = True

# Result backend settings
RESULT_BACKEND_TRANSPORT_OPTIONS = {
    "master_name": "mymaster",
    "visibility_timeout": 3600,
}

# Security (if using authentication)
BROKER_USE_SSL = os.getenv("CELERY_BROKER_USE_SSL", "False").lower() == "true"
REDIS_BACKEND_USE_SSL = os.getenv("CELERY_REDIS_BACKEND_USE_SSL", "False").lower() == "true"
