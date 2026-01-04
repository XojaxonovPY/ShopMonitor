import json
import random
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse

from apps.depends import SessionDep
from db.models import User
from instruments.login import create_refresh_token, verify_token, get_password_hash, UserSession
from instruments.login import get_user, create_access_token, verify_password
from instruments.tasks import send_verification_code
from schemas import RegisterSchema, LoginSchema, UserResponseSchema
from schemas import TokenResponseSchema, MessageResponseSchema
from utils.settings import redis

router = APIRouter()

BodyStr = Annotated[str, Body(embed=True)]


@router.post("/user/register", response_model=MessageResponseSchema, status_code=status.HTTP_200_OK)
async def register(session: SessionDep, user: RegisterSchema) -> JSONResponse:
    query: User | None = await User.get(session, email=user.email)
    if query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")
    data: dict = {
        "full_name": user.full_name,
        "email": user.email,
        'password': await get_password_hash(user.password)
    }
    code: str = str(random.randrange(10 ** 5, 10 ** 6))
    await redis.set(code, json.dumps(data))
    await send_verification_code(data, code=code)
    return JSONResponse({'message': 'emailga tastiqlash code yuborildi'})


@router.post("/user/verify/code/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def verify_code(session: SessionDep, code: BodyStr) -> User:
    data = await redis.get(code)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect code")
    user_data: dict = json.loads(data)
    user: User = await User.create(session, **user_data)
    return user


@router.post("/login/", response_model=TokenResponseSchema, status_code=status.HTTP_200_OK)
async def login(session: SessionDep, form_data: LoginSchema) -> JSONResponse:
    user: User | None = await get_user(session, email=form_data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    verify = await verify_password(form_data.password, user.password)
    if not verify:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    access_token: str = await create_access_token(data={"sub": user.email})
    refresh_token_: str = await create_refresh_token(data={"sub": user.email})
    return JSONResponse({"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"})


@router.post("/refresh", response_model=TokenResponseSchema, status_code=status.HTTP_200_OK)
async def refresh_token(refresh_token_: BodyStr) -> JSONResponse:
    payload: dict = await verify_token(refresh_token_)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_data: dict = {"sub": payload.get("sub")}
    new_access_token: str = await create_access_token(user_data)
    new_refresh_token: str = await create_refresh_token(user_data)
    return JSONResponse({"access_token": new_access_token, "refresh_token": new_refresh_token})


@router.get("/users/me", response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
async def read_users_me(current_user: UserSession) -> User:
    return current_user
