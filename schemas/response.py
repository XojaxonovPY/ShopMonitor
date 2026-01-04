from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl


class TokenResponseSchema(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class UserResponseSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class MessageResponseSchema(BaseModel):
    message: Optional[str] = None


class ProductResponseSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    current_price: Optional[str] = None
    url: Optional[HttpUrl] = None
    created_at: Optional[datetime] = None


class PriceResponseSchema(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    price: Optional[str] = None
    check_at: Optional[bool] = None
    created_at: Optional[datetime] = None
