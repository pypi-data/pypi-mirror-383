"""Authentication and authorization module with OAuth2 and JWT support."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings
from .database import get_db
from .models import User
from .schemas import TokenData


# Security context for password hashing (if needed later)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer()


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""

    pass


class OAuth2Provider:
    """Base class for OAuth2 providers."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """Initialize OAuth2 provider.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth provider

        Returns:
            Token response dictionary

        Raises:
            AuthenticationError: If token exchange fails
        """
        raise NotImplementedError

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider.

        Args:
            access_token: OAuth access token

        Returns:
            User information dictionary

        Raises:
            AuthenticationError: If user info retrieval fails
        """
        raise NotImplementedError


class GitHubOAuth(OAuth2Provider):
    """GitHub OAuth2 provider."""

    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_API_URL = "https://api.github.com/user"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for GitHub access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                json={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
            )

            if response.status_code != 200:
                raise AuthenticationError(f"GitHub token exchange failed: {response.text}")

            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from GitHub API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_API_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )

            if response.status_code != 200:
                raise AuthenticationError(f"GitHub user info failed: {response.text}")

            return response.json()


class GoogleOAuth(OAuth2Provider):
    """Google OAuth2 provider."""

    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_API_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for Google access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )

            if response.status_code != 200:
                raise AuthenticationError(f"Google token exchange failed: {response.text}")

            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_API_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                raise AuthenticationError(f"Google user info failed: {response.text}")

            return response.json()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token.

    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify JWT token and extract payload.

    Args:
        token: JWT token string

    Returns:
        Token data extracted from token

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email")

        if user_id is None or username is None or email is None:
            raise credentials_exception

        return TokenData(user_id=user_id, username=username, email=email)

    except JWTError:
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials from request
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    token_data = verify_token(token)

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def generate_state_token() -> str:
    """Generate random state token for CSRF protection.

    Returns:
        Random state token string
    """
    return secrets.token_urlsafe(32)


def verify_state_token(state: str, expected_state: str) -> bool:
    """Verify state token matches expected value.

    Args:
        state: State token from OAuth callback
        expected_state: Expected state token value

    Returns:
        True if tokens match, False otherwise
    """
    return secrets.compare_digest(state, expected_state)


async def authenticate_github_user(code: str, db: Session) -> User:
    """Authenticate user with GitHub OAuth.

    Args:
        code: Authorization code from GitHub
        db: Database session

    Returns:
        Authenticated user object

    Raises:
        AuthenticationError: If authentication fails
    """
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise AuthenticationError("GitHub OAuth not configured")

    github = GitHubOAuth(
        settings.GITHUB_CLIENT_ID,
        settings.GITHUB_CLIENT_SECRET,
        settings.GITHUB_REDIRECT_URI,
    )

    # Exchange code for token
    token_response = await github.exchange_code_for_token(code)
    access_token = token_response.get("access_token")

    if not access_token:
        raise AuthenticationError("Failed to get access token from GitHub")

    # Get user info
    user_info = await github.get_user_info(access_token)
    github_id = str(user_info.get("id"))
    username = user_info.get("login")
    email = user_info.get("email")

    if not github_id or not username:
        raise AuthenticationError("Failed to get user info from GitHub")

    # Create or update user in database
    user = db.query(User).filter(
        User.oauth_provider == "github",
        User.oauth_id == github_id,
    ).first()

    if user:
        # Update existing user
        user.username = username
        if email:
            user.email = email
        user.updated_at = datetime.utcnow()
    else:
        # Create new user
        user = User(
            username=username,
            email=email or f"{username}@github.placeholder",
            oauth_provider="github",
            oauth_id=github_id,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


async def authenticate_google_user(code: str, db: Session) -> User:
    """Authenticate user with Google OAuth.

    Args:
        code: Authorization code from Google
        db: Database session

    Returns:
        Authenticated user object

    Raises:
        AuthenticationError: If authentication fails
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise AuthenticationError("Google OAuth not configured")

    google = GoogleOAuth(
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
        settings.GOOGLE_REDIRECT_URI,
    )

    # Exchange code for token
    token_response = await google.exchange_code_for_token(code)
    access_token = token_response.get("access_token")

    if not access_token:
        raise AuthenticationError("Failed to get access token from Google")

    # Get user info
    user_info = await google.get_user_info(access_token)
    google_id = str(user_info.get("id"))
    email = user_info.get("email")
    username = email.split("@")[0] if email else f"user_{google_id[:8]}"

    if not google_id or not email:
        raise AuthenticationError("Failed to get user info from Google")

    # Create or update user in database
    user = db.query(User).filter(
        User.oauth_provider == "google",
        User.oauth_id == google_id,
    ).first()

    if user:
        # Update existing user
        user.username = username
        user.email = email
        user.updated_at = datetime.utcnow()
    else:
        # Create new user
        user = User(
            username=username,
            email=email,
            oauth_provider="google",
            oauth_id=google_id,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user
