from os import getenv

from dotenv import load_dotenv

from utils.env_path import Env_path
from redis.asyncio import Redis

load_dotenv(Env_path)


class Settings:
    DB_URL = getenv('DB_URL')
    ADMIN_USERNAME = getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = getenv('ADMIN_PASSWORD')
    REDIS_HOST = getenv('REDIS_HOST')
    EMAIL_FROM = getenv('EMAIL_FROM')
    EMAIL_PASSWORD = getenv('EMAIL_PASSWORD')


redis = Redis.from_url(Settings.REDIS_HOST, decode_responses=True)
