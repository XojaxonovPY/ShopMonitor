import json
import random

from fastapi import APIRouter, Depends, HTTPException

from db.models import User
from db.sessions import SessionDep
from instruments.forms import RegisterForm, LoginForm, TokenResponse, VerifyCodeForm
from instruments.login import get_user, create_access_token, verify_password
from instruments.login import get_current_user, create_refresh_token, verify_token, get_password_hash
from instruments.tasks import send_verification_code
from utils.settings import redis

login_register = APIRouter()


@login_register.post("/user/register")
async def register(session: SessionDep, user: RegisterForm):
    query = await User.get(session, User.email, user.email)
    if query:
        raise HTTPException(status_code=400, detail="Email is already registered")

    data = {
        "full_name": user.full_name,
        "email": user.email,
        'password': await get_password_hash(user.password)
    }

    code = str(random.randrange(10 ** 5, 10 ** 6))
    await redis.set(code, json.dumps(data))
    await send_verification_code(data, code=code)
    return {'message': 'emailga tastiqlash code yuborildi'}


@login_register.post("/user/verify/code/", response_model=User)
async def verify_code(session: SessionDep, code: VerifyCodeForm):
    data = await redis.get(code.code)
    if not data:
        raise HTTPException(status_code=400, detail="Incorrect code")
    user_data = json.loads(data)
    user = await User.create(session, **user_data)
    return user


@login_register.post("/login/", response_model=TokenResponse)
async def login(session: SessionDep, form_data: LoginForm):
    user = await get_user(session, form_data.email)
    verify = await verify_password(form_data.password, user.password)
    if not user or not verify:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = await create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@login_register.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    payload = await verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_data = {"sub": payload["sub"]}
    new_access_token = await create_access_token(user_data)
    new_refresh_token = await create_refresh_token(user_data)
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


@login_register.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
