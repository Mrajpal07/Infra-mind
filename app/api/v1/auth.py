"""Authentication API endpoints."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


# Demo user storage (replace with database in production)
DEMO_USERS = {
    "admin@example.com": {
        "email": "admin@example.com",
        "hashed_password": get_password_hash("admin123"),
        "full_name": "Admin User",
        "is_active": True,
    }
}


class Token(BaseModel):
    """Token response schema."""
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    
    email: str | None = None


class UserCreate(BaseModel):
    """User creation schema."""
    
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    """User response schema."""
    
    email: str
    full_name: str
    is_active: bool


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserResponse:
    """Get current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = DEMO_USERS.get(email)
    if user is None:
        raise credentials_exception
    
    return UserResponse(
        email=user["email"],
        full_name=user["full_name"],
        is_active=user["is_active"],
    )


@router.post(
    "/login",
    response_model=Token,
    summary="Login for access token",
    description="OAuth2 compatible token login, get an access token for future requests.",
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Authenticate user and return access token."""
    user = DEMO_USERS.get(form_data.username)
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires,
    )
    
    return Token(access_token=access_token)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account.",
)
async def register(user_data: UserCreate) -> UserResponse:
    """Register a new user."""
    if user_data.email in DEMO_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    DEMO_USERS[user_data.email] = {
        "email": user_data.email,
        "hashed_password": get_password_hash(user_data.password),
        "full_name": user_data.full_name,
        "is_active": True,
    }
    
    return UserResponse(
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get details of the currently authenticated user.",
)
async def get_me(current_user: Annotated[UserResponse, Depends(get_current_user)]) -> UserResponse:
    """Get current user details."""
    return current_user
