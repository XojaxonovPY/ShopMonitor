import asyncio

from fastapi import APIRouter
from fastapi import WebSocket
from sqlalchemy import select
from starlette.websockets import WebSocketDisconnect

from db.models import Product, Price, User
from db.sessions import SessionDep
from instruments.login import decode_token

#
socket = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.rooms: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.rooms.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.rooms:
            self.rooms[user_id].remove(websocket)
            if not self.rooms[user_id]:
                del self.rooms[user_id]

    async def send_products(self, user_id: int, products: list[Product]):
        data = {"products": [p.model_dump(mode='json') for p in products]}
        for ws in self.rooms.get(user_id, []):
            await ws.send_json(data)


manager = ConnectionManager()


@socket.websocket("/ws/products/")
async def get_products(session: SessionDep, websocket: WebSocket, token: str):
    current_user = await decode_token(token)
    print(current_user)
    await manager.connect(current_user, websocket)
    try:
        while True:
            await asyncio.sleep(5)
            products: list[Product] = await Product.query(
                session,
                select(Product).join(User).where(User.email == current_user)
            )
            products.sort(key=lambda p: (p.current_price, p.name))
            await manager.send_products(current_user, products)

    except WebSocketDisconnect:
        manager.disconnect(current_user, websocket)


@socket.websocket("/ws/products/prices/{pk}")
async def get_products_prices(session: SessionDep, websocket: WebSocket, pk: int):
    await manager.connect(pk, websocket)
    try:
        while True:
            await asyncio.sleep(5)
            prices: list[Price] = await Price.get(session, Price.product_id, pk, all_=True)
            await manager.send_products(pk, prices)
    except WebSocketDisconnect:
        manager.disconnect(pk, websocket)
