from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from utils.settings import Settings

SQLALCHEMY_DATABASE_URL = Settings.DB_URL

engine: AsyncEngine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, future=True)
