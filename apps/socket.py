import asyncio
from typing import Any

from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from db.models import Product, Price, User
from db.sessions import AsyncSessionLocal
from instruments.login import get_current_user

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.rooms: dict[int, list[WebSocket]] = {}

    async def connect(self, pk: int, websocket: WebSocket):
        self.rooms.setdefault(pk, []).append(websocket)

    async def disconnect(self, pk: int | None, websocket: WebSocket):
        if pk in self.rooms:
            self.rooms[pk].remove(websocket)
            if not self.rooms[pk]:
                del self.rooms[pk]

    async def send_products(self, pk: int, data_list: list[dict[str, Any]]):
        data = {"products": data_list}
        active_connections = self.rooms.get(pk, [])
        for ws in active_connections[:]:
            try:
                await ws.send_json(data)
            except Exception as e:
                print(f"Xatolik yuz berdi, ulanish yopilmoqda: {e}")
                await self.disconnect(pk, ws)


manager = ConnectionManager()


@router.websocket("/ws/products/")
async def get_products(websocket: WebSocket, token: str):
    pk: int | None = None
    email: str | None = None
    try:
        await websocket.accept()
        async with AsyncSessionLocal() as session:
            current_user: User = await get_current_user(session, token)
            pk = current_user.id
            email = current_user.email
        await manager.connect(pk, websocket)
        while True:
            async with AsyncSessionLocal() as session:
                products: list[Product] = await Product.query(
                    session,
                    select(Product)
                    .join(User).where(User.email == email)
                    .order_by(Product.current_price, Product.name), all_=True
                )
                data: list[dict[str, Any]] = [
                    {'id': product.id, 'name': product.name, 'price': product.current_price}
                    for product in products
                ]
                await manager.send_products(pk, data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        await manager.disconnect(pk, websocket)
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@router.websocket("/ws/products/prices/{pk}")
async def get_products_prices(websocket: WebSocket, pk: int):
    try:
        await websocket.accept()
        await manager.connect(pk, websocket)
        while True:
            async with AsyncSessionLocal() as session:
                prices: list[Price] = await Price.get(session, product_id=pk, all_=True)
                data: list[dict[str, Any]] = [
                    {'id': price.id, 'price': price.price}
                    for price in prices
                ]
                await manager.send_products(pk, data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        await manager.disconnect(pk, websocket)
