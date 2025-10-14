"""SQLAlchemy database models for the Prompt Marketplace."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    """User model for authentication and identity."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    oauth_provider = Column(String(50), nullable=False)  # 'github', 'google'
    oauth_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prompts = relationship("Prompt", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("oauth_provider", "oauth_id", name="uq_oauth_provider_id"),
        Index("idx_user_oauth", "oauth_provider", "oauth_id"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Prompt(Base):
    """Prompt model for storing submitted prompts."""

    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    description = Column(Text)
    domain = Column(String(100), nullable=False, index=True)  # e.g., 'vision', 'nlp', 'tabular'
    task = Column(String(100), nullable=False, index=True)  # e.g., 'classification', 'regression'
    accuracy = Column(Float)  # Performance metric
    version = Column(Integer, default=1, nullable=False)
    parent_id = Column(Integer, ForeignKey("prompts.id", ondelete="SET NULL"))  # For versioning
    is_active = Column(Integer, default=1, nullable=False)  # Soft delete
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="prompts")
    ratings = relationship("Rating", back_populates="prompt", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="prompt", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="prompt", cascade="all, delete-orphan")
    benchmarks = relationship("Benchmark", back_populates="prompt", cascade="all, delete-orphan")
    parent = relationship("Prompt", remote_side=[id], backref="versions")

    __table_args__ = (
        Index("idx_prompt_domain_task", "domain", "task"),
        Index("idx_prompt_user", "user_id"),
        Index("idx_prompt_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Prompt(id={self.id}, title='{self.title}', domain='{self.domain}', task='{self.task}')>"

    @property
    def average_rating(self) -> Optional[float]:
        """Calculate average rating for this prompt."""
        if not self.ratings:
            return None
        return sum(r.rating for r in self.ratings) / len(self.ratings)

    @property
    def download_count(self) -> int:
        """Get total download count."""
        return len(self.downloads)


class Rating(Base):
    """Rating model for 5-star ratings."""

    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prompt = relationship("Prompt", back_populates="ratings")
    user = relationship("User", back_populates="ratings")

    __table_args__ = (
        UniqueConstraint("prompt_id", "user_id", name="uq_prompt_user_rating"),
        Index("idx_rating_prompt", "prompt_id"),
        Index("idx_rating_user", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<Rating(id={self.id}, prompt_id={self.prompt_id}, user_id={self.user_id}, rating={self.rating})>"


class Review(Base):
    """Review model for text reviews and comments."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prompt = relationship("Prompt", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    __table_args__ = (
        Index("idx_review_prompt", "prompt_id"),
        Index("idx_review_user", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, prompt_id={self.prompt_id}, user_id={self.user_id})>"


class Download(Base):
    """Download tracking model."""

    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    downloaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    prompt = relationship("Prompt", back_populates="downloads")
    user = relationship("User", back_populates="downloads")

    __table_args__ = (
        Index("idx_download_prompt", "prompt_id"),
        Index("idx_download_user", "user_id"),
        Index("idx_download_date", "downloaded_at"),
    )

    def __repr__(self) -> str:
        return f"<Download(id={self.id}, prompt_id={self.prompt_id}, user_id={self.user_id})>"


class Benchmark(Base):
    """Benchmark model for performance tracking."""

    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    metric = Column(String(100), nullable=False)  # e.g., 'accuracy', 'f1', 'rmse'
    score = Column(Float, nullable=False)
    dataset = Column(String(255), nullable=False)  # Dataset name
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    prompt = relationship("Prompt", back_populates="benchmarks")

    __table_args__ = (
        Index("idx_benchmark_prompt", "prompt_id"),
        Index("idx_benchmark_metric", "metric"),
        Index("idx_benchmark_dataset", "dataset"),
    )

    def __repr__(self) -> str:
        return f"<Benchmark(id={self.id}, prompt_id={self.prompt_id}, metric='{self.metric}', score={self.score})>"
