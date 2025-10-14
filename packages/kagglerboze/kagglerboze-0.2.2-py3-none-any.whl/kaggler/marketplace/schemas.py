"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""

    oauth_provider: str = Field(..., pattern="^(github|google)$")
    oauth_id: str


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    oauth_provider: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Prompt Schemas
class PromptBase(BaseModel):
    """Base prompt schema."""

    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=10)
    description: Optional[str] = Field(None, max_length=2000)
    domain: str = Field(..., max_length=100)
    task: str = Field(..., max_length=100)
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)


class PromptCreate(PromptBase):
    """Schema for creating a new prompt."""

    parent_id: Optional[int] = None


class PromptUpdate(BaseModel):
    """Schema for updating a prompt."""

    title: Optional[str] = Field(None, min_length=5, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    description: Optional[str] = Field(None, max_length=2000)
    domain: Optional[str] = Field(None, max_length=100)
    task: Optional[str] = Field(None, max_length=100)
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)


class PromptResponse(PromptBase):
    """Schema for prompt response."""

    id: int
    user_id: int
    version: int
    parent_id: Optional[int]
    is_active: int
    created_at: datetime
    updated_at: datetime
    average_rating: Optional[float] = None
    download_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class PromptDetailResponse(PromptResponse):
    """Detailed prompt response with relationships."""

    user: UserResponse
    ratings: List["RatingResponse"] = []
    reviews: List["ReviewResponse"] = []
    benchmarks: List["BenchmarkResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# Rating Schemas
class RatingBase(BaseModel):
    """Base rating schema."""

    rating: int = Field(..., ge=1, le=5)


class RatingCreate(RatingBase):
    """Schema for creating a rating."""

    pass


class RatingUpdate(RatingBase):
    """Schema for updating a rating."""

    pass


class RatingResponse(RatingBase):
    """Schema for rating response."""

    id: int
    prompt_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Review Schemas
class ReviewBase(BaseModel):
    """Base review schema."""

    content: str = Field(..., min_length=10, max_length=5000)


class ReviewCreate(ReviewBase):
    """Schema for creating a review."""

    pass


class ReviewUpdate(ReviewBase):
    """Schema for updating a review."""

    pass


class ReviewResponse(ReviewBase):
    """Schema for review response."""

    id: int
    prompt_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


# Download Schemas
class DownloadResponse(BaseModel):
    """Schema for download response."""

    id: int
    prompt_id: int
    user_id: int
    downloaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Benchmark Schemas
class BenchmarkBase(BaseModel):
    """Base benchmark schema."""

    metric: str = Field(..., max_length=100)
    score: float
    dataset: str = Field(..., max_length=255)


class BenchmarkCreate(BenchmarkBase):
    """Schema for creating a benchmark."""

    pass


class BenchmarkResponse(BenchmarkBase):
    """Schema for benchmark response."""

    id: int
    prompt_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Authentication Schemas
class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token payload data."""

    user_id: int
    username: str
    email: str


class OAuthCallbackRequest(BaseModel):
    """OAuth callback request schema."""

    code: str
    state: Optional[str] = None


# Search and Filter Schemas
class PromptSearchParams(BaseModel):
    """Schema for prompt search parameters."""

    query: Optional[str] = None
    domain: Optional[str] = None
    task: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    min_downloads: Optional[int] = Field(None, ge=0)
    sort_by: str = Field("created_at", pattern="^(created_at|rating|downloads|accuracy)$")
    order: str = Field("desc", pattern="^(asc|desc)$")
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry."""

    rank: int
    prompt: PromptResponse
    average_rating: float
    download_count: int
    review_count: int

    model_config = ConfigDict(from_attributes=True)


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response."""

    entries: List[LeaderboardEntry]
    total: int
    updated_at: datetime


# Statistics Schemas
class PromptStats(BaseModel):
    """Schema for prompt statistics."""

    total_downloads: int
    total_ratings: int
    average_rating: Optional[float]
    total_reviews: int
    total_benchmarks: int
    rating_distribution: dict[int, int]  # {1: count, 2: count, ...}


class UserStats(BaseModel):
    """Schema for user statistics."""

    total_prompts: int
    total_downloads: int
    total_ratings: int
    total_reviews: int
    average_prompt_rating: Optional[float]


# Error Response Schema
class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Pagination Schema
class PaginatedResponse(BaseModel):
    """Generic paginated response."""

    items: List[PromptResponse]
    total: int
    limit: int
    offset: int
    has_more: bool
