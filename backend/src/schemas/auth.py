"""Authentication schemas."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password has minimum requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)."""

    id: int
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for decoded JWT token payload."""

    sub: str  # user_id
    exp: int  # expiration timestamp
    type: Literal["access", "refresh"]
    iat: Optional[int] = None  # issued at timestamp


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str
