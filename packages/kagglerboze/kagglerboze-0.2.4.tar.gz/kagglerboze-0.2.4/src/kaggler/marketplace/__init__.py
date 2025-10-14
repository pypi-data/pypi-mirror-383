"""Kaggler Prompt Marketplace - A platform for sharing and rating ML prompts.

This package provides a complete marketplace system for ML prompts with:
- OAuth2 authentication (GitHub, Google)
- Prompt submission and versioning
- 5-star rating system
- Review and comment system
- Performance benchmark tracking
- Search and filtering
- Download tracking
- Leaderboard

Example:
    ```python
    from kaggler.marketplace import app, create_tables

    # Initialize database
    create_tables()

    # Run API server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    ```
"""

__version__ = "1.0.0"
__author__ = "Kaggler Team"
__license__ = "MIT"

# Import main components
from .api import app
from .database import (
    create_tables,
    drop_tables,
    get_db,
    get_db_context,
    db_manager,
)
from .models import (
    User,
    Prompt,
    Rating,
    Review,
    Download,
    Benchmark,
)
from .schemas import (
    UserResponse,
    PromptCreate,
    PromptResponse,
    PromptDetailResponse,
    RatingCreate,
    RatingResponse,
    ReviewCreate,
    ReviewResponse,
    BenchmarkCreate,
    BenchmarkResponse,
    Token,
)
from .auth import (
    get_current_user,
    create_access_token,
    verify_token,
)
from .config import settings

__all__ = [
    # FastAPI app
    "app",
    # Database
    "create_tables",
    "drop_tables",
    "get_db",
    "get_db_context",
    "db_manager",
    # Models
    "User",
    "Prompt",
    "Rating",
    "Review",
    "Download",
    "Benchmark",
    # Schemas
    "UserResponse",
    "PromptCreate",
    "PromptResponse",
    "PromptDetailResponse",
    "RatingCreate",
    "RatingResponse",
    "ReviewCreate",
    "ReviewResponse",
    "BenchmarkCreate",
    "BenchmarkResponse",
    "Token",
    # Auth
    "get_current_user",
    "create_access_token",
    "verify_token",
    # Config
    "settings",
]
