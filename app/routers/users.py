"""Users listing endpoint with search across name / email / phone."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.cache import cache_get, cache_set, generate_cache_key
from app.config import settings
from app.database import users_col
from app.utils import build_pagination, convert_mongo_data

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["Users"])


def _build_search_query(search_text: str) -> dict:
    conditions: list[dict] = [
        {"name": {"$regex": search_text, "$options": "i"}},
        {"email": {"$regex": search_text, "$options": "i"}},
    ]
    try:
        conditions.append({"phone": int(search_text)})
    except ValueError:
        pass
    return {"$or": conditions}


@router.get("")
def get_users(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
):
    cache_key = generate_cache_key("users", search=search, page=page, limit=limit)

    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        query = _build_search_query(search.strip()) if search else {}

        total_results = users_col.count_documents(query) if query else users_col.estimated_document_count()

        users = [
            convert_mongo_data(u)
            for u in users_col.find(query).sort("created_at", -1).skip((page - 1) * limit).limit(limit)
        ]

        result = {"success": True, **build_pagination(total_results, page, limit), "users": users}
        cache_set(cache_key, result, settings.CACHE_TTL)
        return result

    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to fetch users")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
