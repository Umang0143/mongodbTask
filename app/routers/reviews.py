"""Reviews listing endpoint with comment search + rating filter."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.cache import cache_get, cache_set, generate_cache_key
from app.config import settings
from app.database import reviews_col
from app.utils import build_pagination, convert_mongo_data

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


def _build_search_query(search_text: str) -> dict:
    conditions: list[dict] = [{"comment": {"$regex": search_text, "$options": "i"}}]
    try:
        search_rating = int(search_text)
        if 1 <= search_rating <= 5:
            conditions.append({"rating": search_rating})
    except ValueError:
        pass
    return {"$or": conditions}


@router.get("")
def get_reviews(
    search: Optional[str] = Query(None),
    rating: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
):
    cache_key = generate_cache_key("reviews", search=search, rating=rating, page=page, limit=limit)

    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        query: dict = _build_search_query(search) if search else {}

        if rating is not None:
            query["rating"] = rating

        total_results = (
            reviews_col.count_documents(query) if query else reviews_col.estimated_document_count()
        )

        reviews = [
            convert_mongo_data(r)
            for r in reviews_col.find(query).sort("date", -1).skip((page - 1) * limit).limit(limit)
        ]

        result = {"success": True, **build_pagination(total_results, page, limit), "reviews": reviews}
        cache_set(cache_key, result, settings.CACHE_TTL)
        return result

    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to fetch reviews")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
