from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from .crud import create_user, get_user, authenticate_user, refresh_token, logout_user
from .deps import get_current_user

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=TokenResponse)
async def register(user: UserRegister):
    user = await create_user(user.username, user.password, user.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    return {"access_token": user.access_token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    user = await authenticate_user(user.username, user.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": user.access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh(token: str):
    new_token = await refresh_token(token)
    if not new_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return new_token

@router.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    await logout_user(current_user)
    return {"detail": "Successfully logged out"}

@router.get("/me", response_model=UserRegister)
async def read_users_me(current_user: str = Depends(get_current_user)):
    user = await get_user(current_user)
    return user