import asyncio
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select

from db.models import User
from db.sessions import SessionDep

# ⚙️ Konfiguratsiya
SECRET_KEY = "zqxwcevrbtynumikol123456765432"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 🔐 Parolni tekshirish (bcrypt, async-safe)
async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(pwd_context.verify, plain_password, hashed_password)


# 🔐 Parolni xeshlash
async def get_password_hash(password: str) -> str:
    return await asyncio.to_thread(pwd_context.hash, password)


# 👤 Userni username orqali olish
async def get_user(session: SessionDep, email) -> Optional[User]:
    result = await User.query(session, select(User).where(User.email == email), True)
    return result


# 🔑 Access token yaratish (JWT)
async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = await asyncio.to_thread(jwt.encode, to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# 🧑 Hozirgi foydalanuvchini olish
async def get_current_user(
        session: SessionDep, token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await asyncio.to_thread(jwt.decode, token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(session, username)
    if user is None:
        raise credentials_exception
    return user


async def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # bu yerda user_id
    except JWTError:
        return None
