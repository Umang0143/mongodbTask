"""Payments listing endpoint with search across status / method / amount."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.cache import cache_get, cache_set, generate_cache_key
from app.config import settings
from app.database import payments_col
from app.utils import build_pagination, convert_mongo_data

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payments", tags=["Payments"])


def _build_search_query(search_text: str) -> dict:
    conditions: list[dict] = [
        {"status": {"$regex": search_text, "$options": "i"}},
        {"method": {"$regex": search_text, "$options": "i"}},
    ]
    try:
        conditions.append({"amount": float(search_text)})
    except ValueError:
        pass
    return {"$or": conditions}


@router.get("")
def get_payments(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
):
    cache_key = generate_cache_key("payments", search=search, page=page, limit=limit)

    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        query = _build_search_query(search.strip()) if search else {}

        total_results = (
            payments_col.count_documents(query) if query else payments_col.estimated_document_count()
        )

        payments = [
            convert_mongo_data(p)
            for p in payments_col.find(query).sort("payment_date", -1).skip((page - 1) * limit).limit(limit)
        ]

        result = {"success": True, **build_pagination(total_results, page, limit), "payments": payments}
        cache_set(cache_key, result, settings.CACHE_TTL)
        return result

    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to fetch payments")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
