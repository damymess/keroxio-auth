from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    sub: str  # User ID
    email: Optional[str] = None
    garage_name: Optional[str] = None
    type: str = "access"  # "access" or "refresh"
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


def create_access_token(
    user_id: str,
    email: Optional[str] = None,
    garage_name: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a new JWT access token.

    Args:
        user_id: The user's unique identifier
        email: User's email address
        garage_name: Name of the garage
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload = {
        "sub": user_id,
        "email": email,
        "garage_name": garage_name,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def create_refresh_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a new JWT refresh token.

    Args:
        user_id: The user's unique identifier
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[TokenPayload]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token to verify
        token_type: Expected token type ("access" or "refresh")

    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Check token type
        if payload.get("type") != token_type:
            return None

        return TokenPayload(**payload)

    except JWTError:
        return None


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decode a JWT token without verification.

    Useful for extracting claims from expired tokens.

    Args:
        token: The JWT token to decode

    Returns:
        Token payload dict if decodable, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )
        return payload
    except JWTError:
        return None


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    Get the expiration time of a token.

    Args:
        token: The JWT token

    Returns:
        Expiration datetime if valid, None otherwise
    """
    payload = decode_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired.

    Args:
        token: The JWT token

    Returns:
        True if expired, False otherwise
    """
    expiry = get_token_expiry(token)
    if expiry:
        return datetime.utcnow() > expiry
    return True
