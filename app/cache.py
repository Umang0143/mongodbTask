import json
import logging
from typing import Any, Optional

import redis

from app.config import settings

logger = logging.getLogger(__name__)

try:
    redis_client: Optional[redis.Redis] = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )
    redis_client.ping()
    logger.info("Redis connected successfully.")
except redis.ConnectionError:
    logger.warning("Redis connection failed — running without cache.")
    redis_client = None


def generate_cache_key(prefix: str, **kwargs: Any) -> str:
    """Builds a deterministic cache key from a prefix + query params."""
    key_parts = [f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None]
    return f"{prefix}:" + "&".join(key_parts)


def cache_get(key: str) -> Optional[dict]:
    """Returns parsed JSON from cache, or None on miss / no redis / bad data."""
    if not redis_client:
        return None
    try:
        cached = redis_client.get(key)
        return json.loads(cached) if cached else None
    except (redis.RedisError, json.JSONDecodeError) as exc:
        logger.warning("Cache read failed for key=%s: %s", key, exc)
        return None


def cache_set(key: str, value: dict, ttl: int) -> None:
    """Writes JSON to cache. Failures are logged, never raised."""
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except redis.RedisError as exc:
        logger.warning("Cache write failed for key=%s: %s", key, exc)
