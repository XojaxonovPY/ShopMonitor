from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

from apps import login_register, product, socket
from instruments.schedular import start_scheduler
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app:FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Shop Monitor API", lifespan=lifespan)

app.include_router(login_register, prefix="", tags=["product"])
app.include_router(product, prefix="", tags=["login"])
app.include_router(socket, prefix="", tags=["socket"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Shop Monitor API",
        version="1.0.0",
        description="Shop Monitor API with JWT Auth",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")

app.openapi = custom_openapi

# import bcrypt
#
# print(bcrypt.hashpw("3".encode(), salt=bcrypt.gensalt()))
