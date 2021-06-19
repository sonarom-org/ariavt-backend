
from typing import Optional

from datetime import timedelta

from fastapi import Depends, HTTPException, status, APIRouter, Header
from fastapi.security import OAuth2PasswordRequestForm

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.security.methods import create_access_token,\
    authenticate_user, get_current_user
from app.security.models import Token


router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-token")
async def verify_access_token(authorization: str = Header(None)):
    access_token = authorization.split(' ')[1]
    user = await get_current_user(access_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"token": access_token, "user": user.username}
