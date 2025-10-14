"""FastAPI application with RESTful endpoints for the Prompt Marketplace."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Session, joinedload
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import get_db, create_tables
from .models import User, Prompt, Rating, Review, Download, Benchmark
from .schemas import (
    PromptCreate,
    PromptUpdate,
    PromptResponse,
    PromptDetailResponse,
    RatingCreate,
    RatingUpdate,
    RatingResponse,
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    DownloadResponse,
    BenchmarkCreate,
    BenchmarkResponse,
    Token,
    OAuthCallbackRequest,
    PromptSearchParams,
    LeaderboardResponse,
    LeaderboardEntry,
    PromptStats,
    UserStats,
    PaginatedResponse,
    ErrorResponse,
)
from .auth import (
    get_current_user,
    create_access_token,
    generate_state_token,
    authenticate_github_user,
    authenticate_google_user,
    AuthenticationError,
)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RESTful API for the Kaggler Prompt Marketplace",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    create_tables()


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow(),
    }


# ========================
# Authentication Endpoints
# ========================

@app.get("/auth/github", tags=["Authentication"])
async def github_login():
    """Initiate GitHub OAuth login flow.

    Returns:
        OAuth authorization URL and state token
    """
    state = generate_state_token()
    auth_url = settings.get_github_oauth_url(state)
    return {"auth_url": auth_url, "state": state}


@app.post("/auth/github/callback", response_model=Token, tags=["Authentication"])
async def github_callback(
    request: OAuthCallbackRequest,
    db: Session = Depends(get_db),
):
    """Handle GitHub OAuth callback.

    Args:
        request: OAuth callback request with code
        db: Database session

    Returns:
        JWT access token
    """
    try:
        user = await authenticate_github_user(request.code, db)
        access_token = create_access_token(
            data={
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
            }
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@app.get("/auth/google", tags=["Authentication"])
async def google_login():
    """Initiate Google OAuth login flow.

    Returns:
        OAuth authorization URL and state token
    """
    state = generate_state_token()
    auth_url = settings.get_google_oauth_url(state)
    return {"auth_url": auth_url, "state": state}


@app.post("/auth/google/callback", response_model=Token, tags=["Authentication"])
async def google_callback(
    request: OAuthCallbackRequest,
    db: Session = Depends(get_db),
):
    """Handle Google OAuth callback.

    Args:
        request: OAuth callback request with code
        db: Database session

    Returns:
        JWT access token
    """
    try:
        user = await authenticate_google_user(request.code, db)
        access_token = create_access_token(
            data={
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
            }
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@app.get("/auth/me", tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "oauth_provider": current_user.oauth_provider,
        "created_at": current_user.created_at,
    }


# ========================
# Prompt Endpoints
# ========================

@app.post("/prompts", response_model=PromptResponse, status_code=status.HTTP_201_CREATED, tags=["Prompts"])
async def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new prompt.

    Args:
        prompt_data: Prompt creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created prompt
    """
    # Validate parent_id if provided
    if prompt_data.parent_id:
        parent = db.query(Prompt).filter(Prompt.id == prompt_data.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent prompt {prompt_data.parent_id} not found",
            )

    # Create prompt
    prompt = Prompt(
        user_id=current_user.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        domain=prompt_data.domain,
        task=prompt_data.task,
        accuracy=prompt_data.accuracy,
        parent_id=prompt_data.parent_id,
    )

    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    return prompt


@app.get("/prompts", response_model=PaginatedResponse, tags=["Prompts"])
async def list_prompts(
    query: Optional[str] = Query(None, description="Search query"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    task: Optional[str] = Query(None, description="Filter by task"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum rating"),
    sort_by: str = Query("created_at", regex="^(created_at|rating|downloads|accuracy)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List prompts with filtering and pagination.

    Args:
        query: Search query string
        domain: Filter by domain
        task: Filter by task
        min_rating: Minimum rating filter
        sort_by: Sort field
        order: Sort order (asc/desc)
        limit: Page size
        offset: Page offset
        db: Database session

    Returns:
        Paginated list of prompts
    """
    # Base query
    base_query = db.query(Prompt).filter(Prompt.is_active == 1)

    # Apply filters
    if query:
        base_query = base_query.filter(
            (Prompt.title.contains(query)) | (Prompt.description.contains(query))
        )
    if domain:
        base_query = base_query.filter(Prompt.domain == domain)
    if task:
        base_query = base_query.filter(Prompt.task == task)

    # Apply rating filter
    if min_rating:
        # Subquery for average ratings
        rating_subquery = (
            db.query(
                Rating.prompt_id,
                func.avg(Rating.rating).label("avg_rating")
            )
            .group_by(Rating.prompt_id)
            .having(func.avg(Rating.rating) >= min_rating)
            .subquery()
        )
        base_query = base_query.join(rating_subquery, Prompt.id == rating_subquery.c.prompt_id)

    # Get total count
    total = base_query.count()

    # Apply sorting
    if sort_by == "rating":
        # Sort by average rating
        rating_subquery = (
            db.query(
                Rating.prompt_id,
                func.avg(Rating.rating).label("avg_rating")
            )
            .group_by(Rating.prompt_id)
            .subquery()
        )
        base_query = base_query.outerjoin(rating_subquery, Prompt.id == rating_subquery.c.prompt_id)
        sort_column = rating_subquery.c.avg_rating
    elif sort_by == "downloads":
        # Sort by download count
        download_subquery = (
            db.query(
                Download.prompt_id,
                func.count(Download.id).label("download_count")
            )
            .group_by(Download.prompt_id)
            .subquery()
        )
        base_query = base_query.outerjoin(download_subquery, Prompt.id == download_subquery.c.prompt_id)
        sort_column = download_subquery.c.download_count
    elif sort_by == "accuracy":
        sort_column = Prompt.accuracy
    else:  # created_at
        sort_column = Prompt.created_at

    # Apply order
    if order == "asc":
        base_query = base_query.order_by(asc(sort_column))
    else:
        base_query = base_query.order_by(desc(sort_column))

    # Apply pagination
    prompts = base_query.limit(limit).offset(offset).all()

    return PaginatedResponse(
        items=prompts,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total,
    )


@app.get("/prompts/{prompt_id}", response_model=PromptDetailResponse, tags=["Prompts"])
async def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
):
    """Get detailed prompt information.

    Args:
        prompt_id: Prompt ID
        db: Database session

    Returns:
        Detailed prompt information
    """
    prompt = (
        db.query(Prompt)
        .options(
            joinedload(Prompt.user),
            joinedload(Prompt.ratings),
            joinedload(Prompt.reviews).joinedload(Review.user),
            joinedload(Prompt.benchmarks),
        )
        .filter(Prompt.id == prompt_id, Prompt.is_active == 1)
        .first()
    )

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt {prompt_id} not found",
        )

    return prompt


@app.put("/prompts/{prompt_id}", response_model=PromptResponse, tags=["Prompts"])
async def update_prompt(
    prompt_id: int,
    prompt_data: PromptUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a prompt.

    Args:
        prompt_id: Prompt ID
        prompt_data: Prompt update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated prompt
    """
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.is_active == 1,
    ).first()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt {prompt_id} not found",
        )

    if prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this prompt",
        )

    # Update fields
    update_data = prompt_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)

    prompt.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(prompt)

    return prompt


@app.delete("/prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Prompts"])
async def delete_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a prompt (soft delete).

    Args:
        prompt_id: Prompt ID
        current_user: Current authenticated user
        db: Database session
    """
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.is_active == 1,
    ).first()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt {prompt_id} not found",
        )

    if prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this prompt",
        )

    # Soft delete
    prompt.is_active = 0
    prompt.updated_at = datetime.utcnow()

    db.commit()


# ========================
# Rating Endpoints
# ========================

@app.post("/prompts/{prompt_id}/rate", response_model=RatingResponse, tags=["Ratings"])
async def rate_prompt(
    prompt_id: int,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rate a prompt.

    Args:
        prompt_id: Prompt ID
        rating_data: Rating data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created or updated rating
    """
    # Check if prompt exists
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.is_active == 1,
    ).first()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt {prompt_id} not found",
        )

    # Check if user already rated this prompt
    existing_rating = db.query(Rating).filter(
        Rating.prompt_id == prompt_id,
        Rating.user_id == current_user.id,
    ).first()

    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_data.rating
        existing_rating.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        # Create new rating
        rating = Rating(
            prompt_id=prompt_id,
            user_id=current_user.id,
            rating=rating_data.rating,
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating


@app.get("/prompts/{prompt_id}/ratings", response_model=List[RatingResponse], tags=["Ratings"])
async def get_prompt_ratings(
    prompt_id: int,
    db: Session = Depends(get_db),
):
    """Get all ratings for a prompt.

    Args:
        prompt_id: Prompt ID
        db: Database session

    Returns:
        List of ratings
    """
    ratings = db.query(Rating).filter(Rating.prompt_id == prompt_id).all()
    return ratings


# ========================
# Review Endpoints
# ========================

@app.post("/prompts/{prompt_id}/review", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED, tags=["Reviews"])
async def create_review(
    prompt_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a review for a prompt.

    Args:
        prompt_id: Prompt ID
        review_data: Review data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created review
    """
    # Check if prompt exists
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.is_active == 1,
    ).first()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt {prompt_id} not found",
        )

    # Create review
    review = Review(
        prompt_id=prompt_id,
        user_id=current_user.id,
        content=review_data.content,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@app.get("/prompts/{prompt_id}/reviews", response_model=List[ReviewResponse], tags=["Reviews"])
async def get_prompt_reviews(
    prompt_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get reviews for a prompt.

    Args:
        prompt_id: Prompt ID
        limit: Page size
        offset: Page offset
        db: Database session

    Returns:
        List of reviews
    """
    reviews = (
        db.query(Review)
        .options(joinedload(Review.user))
        .filter(Review.prompt_id == prompt_id)
        .order_by(desc(Review.created_at))
        .limit(limit)
        .offset(offset)
        .all()
    )

    return reviews


# ========================
# Download Endpoints
# ========================

@app.post("/prompts/{prompt_id}/download", response_model=DownloadResponse, tags=["Downloads"])
async def download_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a prompt and track the download.

    Args:
        prompt_id: Prompt ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Download record
    """
    # Check if prompt exists
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.is_active == 1,
    ).first()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt {prompt_id} not found",
        )

    # Create download record
    download = Download(
        prompt_id=prompt_id,
        user_id=current_user.id,
    )

    db.add(download)
    db.commit()
    db.refresh(download)

    return download


# ========================
# Benchmark Endpoints
# ========================

@app.post("/prompts/{prompt_id}/benchmarks", response_model=BenchmarkResponse, status_code=status.HTTP_201_CREATED, tags=["Benchmarks"])
async def create_benchmark(
    prompt_id: int,
    benchmark_data: BenchmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a benchmark for a prompt.

    Args:
        prompt_id: Prompt ID
        benchmark_data: Benchmark data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created benchmark
    """
    # Check if prompt exists and user owns it
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.is_active == 1,
    ).first()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt {prompt_id} not found",
        )

    if prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add benchmarks to this prompt",
        )

    # Create benchmark
    benchmark = Benchmark(
        prompt_id=prompt_id,
        metric=benchmark_data.metric,
        score=benchmark_data.score,
        dataset=benchmark_data.dataset,
    )

    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)

    return benchmark


@app.get("/prompts/{prompt_id}/benchmarks", response_model=List[BenchmarkResponse], tags=["Benchmarks"])
async def get_prompt_benchmarks(
    prompt_id: int,
    db: Session = Depends(get_db),
):
    """Get benchmarks for a prompt.

    Args:
        prompt_id: Prompt ID
        db: Database session

    Returns:
        List of benchmarks
    """
    benchmarks = db.query(Benchmark).filter(Benchmark.prompt_id == prompt_id).all()
    return benchmarks


# ========================
# Leaderboard Endpoint
# ========================

@app.get("/prompts/leaderboard", response_model=LeaderboardResponse, tags=["Leaderboard"])
async def get_leaderboard(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get top rated prompts leaderboard.

    Args:
        domain: Filter by domain
        limit: Number of results
        db: Database session

    Returns:
        Leaderboard entries
    """
    # Subquery for average ratings
    rating_subquery = (
        db.query(
            Rating.prompt_id,
            func.avg(Rating.rating).label("avg_rating"),
            func.count(Rating.id).label("rating_count"),
        )
        .group_by(Rating.prompt_id)
        .subquery()
    )

    # Subquery for download counts
    download_subquery = (
        db.query(
            Download.prompt_id,
            func.count(Download.id).label("download_count"),
        )
        .group_by(Download.prompt_id)
        .subquery()
    )

    # Subquery for review counts
    review_subquery = (
        db.query(
            Review.prompt_id,
            func.count(Review.id).label("review_count"),
        )
        .group_by(Review.prompt_id)
        .subquery()
    )

    # Main query
    query = (
        db.query(
            Prompt,
            rating_subquery.c.avg_rating,
            download_subquery.c.download_count,
            review_subquery.c.review_count,
        )
        .join(rating_subquery, Prompt.id == rating_subquery.c.prompt_id)
        .outerjoin(download_subquery, Prompt.id == download_subquery.c.prompt_id)
        .outerjoin(review_subquery, Prompt.id == review_subquery.c.prompt_id)
        .filter(Prompt.is_active == 1)
    )

    if domain:
        query = query.filter(Prompt.domain == domain)

    results = query.order_by(desc(rating_subquery.c.avg_rating)).limit(limit).all()

    entries = [
        LeaderboardEntry(
            rank=idx + 1,
            prompt=prompt,
            average_rating=avg_rating or 0.0,
            download_count=download_count or 0,
            review_count=review_count or 0,
        )
        for idx, (prompt, avg_rating, download_count, review_count) in enumerate(results)
    ]

    return LeaderboardResponse(
        entries=entries,
        total=len(entries),
        updated_at=datetime.utcnow(),
    )


# ========================
# Statistics Endpoints
# ========================

@app.get("/prompts/{prompt_id}/stats", response_model=PromptStats, tags=["Statistics"])
async def get_prompt_stats(
    prompt_id: int,
    db: Session = Depends(get_db),
):
    """Get statistics for a prompt.

    Args:
        prompt_id: Prompt ID
        db: Database session

    Returns:
        Prompt statistics
    """
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.is_active == 1,
    ).first()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt {prompt_id} not found",
        )

    # Get counts
    total_downloads = db.query(func.count(Download.id)).filter(Download.prompt_id == prompt_id).scalar()
    total_ratings = db.query(func.count(Rating.id)).filter(Rating.prompt_id == prompt_id).scalar()
    total_reviews = db.query(func.count(Review.id)).filter(Review.prompt_id == prompt_id).scalar()
    total_benchmarks = db.query(func.count(Benchmark.id)).filter(Benchmark.prompt_id == prompt_id).scalar()

    # Get average rating
    avg_rating = db.query(func.avg(Rating.rating)).filter(Rating.prompt_id == prompt_id).scalar()

    # Get rating distribution
    rating_dist = {}
    for i in range(1, 6):
        count = db.query(func.count(Rating.id)).filter(
            Rating.prompt_id == prompt_id,
            Rating.rating == i,
        ).scalar()
        rating_dist[i] = count

    return PromptStats(
        total_downloads=total_downloads,
        total_ratings=total_ratings,
        average_rating=avg_rating,
        total_reviews=total_reviews,
        total_benchmarks=total_benchmarks,
        rating_distribution=rating_dist,
    )


@app.get("/users/me/stats", response_model=UserStats, tags=["Statistics"])
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get statistics for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        User statistics
    """
    # Get counts
    total_prompts = db.query(func.count(Prompt.id)).filter(
        Prompt.user_id == current_user.id,
        Prompt.is_active == 1,
    ).scalar()

    total_downloads = db.query(func.count(Download.id)).filter(
        Download.user_id == current_user.id,
    ).scalar()

    total_ratings = db.query(func.count(Rating.id)).filter(
        Rating.user_id == current_user.id,
    ).scalar()

    total_reviews = db.query(func.count(Review.id)).filter(
        Review.user_id == current_user.id,
    ).scalar()

    # Get average rating for user's prompts
    avg_prompt_rating = (
        db.query(func.avg(Rating.rating))
        .join(Prompt, Rating.prompt_id == Prompt.id)
        .filter(Prompt.user_id == current_user.id)
        .scalar()
    )

    return UserStats(
        total_prompts=total_prompts,
        total_downloads=total_downloads,
        total_ratings=total_ratings,
        total_reviews=total_reviews,
        average_prompt_rating=avg_prompt_rating,
    )
