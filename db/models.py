from sqlalchemy import String, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.config import Model, Base


class User(Model):
    full_name: Mapped[str] = mapped_column(String(length=55))
    email: Mapped[str] = mapped_column(String(length=55), unique=True)
    password: Mapped[str] = mapped_column(String(length=25))

    products: Mapped[list['Product']] = relationship('Product', back_populates="user", lazy='selectin')


class Product(Model):
    name: Mapped[str] = mapped_column(String(length=70))
    current_price: Mapped[str] = mapped_column(String(length=55))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    url: Mapped[str] = mapped_column(Text)
    user: Mapped['User'] = relationship(back_populates="products")

    prices: Mapped[list['Price']] = relationship('Price', back_populates="product", lazy='selectin')


class Price(Model):
    price: Mapped[str] = mapped_column(String(length=50))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete='CASCADE'))
    check_at: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped['Product'] = relationship('Product', back_populates="prices", lazy='joined')


metadata = Base.metadata
