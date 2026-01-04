from fastapi import APIRouter

from apps.login_register import router as auth
from apps.product import router as product
from apps.socket import router as socket

main_router = APIRouter()

main_router.include_router(auth, prefix="", tags=["login"])
main_router.include_router(product, prefix="", tags=["product"])
main_router.include_router(socket, prefix="", tags=["socket"])
