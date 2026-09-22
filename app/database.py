"""
MongoDB connection setup.
Import `db` collections from here wherever needed — keeps one connection pool
shared across the whole app instead of every router opening its own client.
"""

import logging
from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import settings

logger = logging.getLogger(__name__)

client: MongoClient = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]

products_col: Collection = db["products"]
orders_col: Collection = db["orders"]
users_col: Collection = db["users"]
payments_col: Collection = db["payments"]
reviews_col: Collection = db["reviews"]
categories_col: Collection = db["categories"]


def check_mongo_connection() -> bool:
    
    try:
        client.admin.command("ping")
        logger.info("MongoDB connected successfully.")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("MongoDB connection failed: %s", exc)
        return False
