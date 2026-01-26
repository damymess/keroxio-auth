from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.utils.jwt import verify_token, TokenPayload
from app.database import get_db
from app import crud, models

# OAuth2 scheme for form-based login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

# HTTP Bearer scheme for API access
http_bearer = HTTPBearer(auto_error=False)


async def get_token_from_header(
    oauth2_token: Optional[str] = Depends(oauth2_scheme),
    bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> str:
    """Extract token from either OAuth2 or Bearer header."""
    if bearer_credentials:
        return bearer_credentials.credentials
    if oauth2_token:
        return oauth2_token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Validate JWT token and return current user.

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token
    token_data = verify_token(token, token_type="access")
    if token_data is None:
        raise credentials_exception

    # Get user from database
    user = crud.get_user(db, user_id=int(token_data.sub))
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get current active user.

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    """
    Get current user if authenticated, None otherwise.

    Useful for endpoints that work both authenticated and anonymously.
    """
    if not token:
        return None

    token_data = verify_token(token, token_type="access")
    if token_data is None:
        return None

    return crud.get_user(db, user_id=int(token_data.sub))


def get_db_session():
    """Dependency for database session (alias for get_db)."""
    return Depends(get_db)
