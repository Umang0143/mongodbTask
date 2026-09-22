import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.cache import cache_get, cache_set, generate_cache_key
from app.config import settings
from app.database import categories_col
from app.utils import build_pagination, convert_mongo_data

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/categories", tags=["Categories"])


def _build_search_query(search_text: str) -> dict:
    return {
        "$or": [
            {"name": {"$regex": search_text, "$options": "i"}},
            {"description": {"$regex": search_text, "$options": "i"}},
        ]
    }

@router.get("")
def get_categories(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
):
    cache_key = generate_cache_key("categories", search=search, page=page, limit=limit)

    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        query = _build_search_query(search.strip()) if search else {}

        total_results = (
            categories_col.count_documents(query) if query else categories_col.estimated_document_count()
        )

        categories = [
            convert_mongo_data(c)
            for c in categories_col.find(query).sort("name", 1).skip((page - 1) * limit).limit(limit)
        ]

        result = {
            "success": True,
            **build_pagination(total_results, page, limit),
            "categories": categories,
        }
        cache_set(cache_key, result, settings.CACHE_TTL)
        return result

    except Exception as exc:
        logger.exception("Failed to fetch categories")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
