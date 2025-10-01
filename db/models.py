import asyncio

from sqlalchemy import String, Integer, Boolean, Text
from sqlmodel import Field, SQLModel, Relationship

from db import engine
from db.config import CreatedModel


class User(CreatedModel, table=True):
    full_name: str = Field(sa_type=String)
    email: str = Field(sa_type=String, unique=True)
    password: str = Field(sa_type=String)

    products: list['Product'] = Relationship(back_populates="user")


class Product(CreatedModel, table=True):
    name: str = Field(sa_type=String)
    current_price: str = Field(sa_type=String)
    user_id: int = Field(sa_type=Integer, foreign_key="users.id", ondelete='CASCADE')
    user: 'User' = Relationship(back_populates="products")
    url: str = Field(sa_type=Text)

    prices: list['Price'] = Relationship(back_populates="product")


class Price(CreatedModel, table=True):
    price: str = Field(sa_type=String)
    product_id: int = Field(sa_type=Integer, foreign_key="products.id", ondelete='CASCADE')
    check_at: bool = Field(sa_type=Boolean, default=False)

    product: 'Product' = Relationship(back_populates="prices")


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


metadata = SQLModel.metadata

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())
