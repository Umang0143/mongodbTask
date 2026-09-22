"""Orders listing endpoint with smart search (status / amount / date)."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.cache import cache_get, cache_set, generate_cache_key
from app.config import settings
from app.database import orders_col
from app.utils import build_pagination, convert_mongo_data

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/orders", tags=["Orders"])


def _build_search_query(search_text: str) -> dict:
    conditions: list[dict] = [{"status": {"$regex": f"^{search_text}", "$options": "i"}}]

    try:
        conditions.append({"total_amount": float(search_text)})
    except ValueError:
        pass

    try:
        search_date = datetime.strptime(search_text, "%d-%m-%y")
        next_date = search_date + timedelta(days=1)
        conditions.append({"order_date": {"$gte": search_date, "$lt": next_date}})
    except ValueError:
        pass

    return {"$or": conditions}


@router.get("")
def get_orders(
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
):
    cache_key = generate_cache_key("orders", search=search, page=page, limit=limit)

    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        query = _build_search_query(search.strip()) if search else {}

        total_results = orders_col.count_documents(query) if query else orders_col.estimated_document_count()

        orders = [
            convert_mongo_data(o)
            for o in orders_col.find(query).sort("order_date", -1).skip((page - 1) * limit).limit(limit)
        ]

        result = {"success": True, **build_pagination(total_results, page, limit), "orders": orders}
        cache_set(cache_key, result, settings.CACHE_TTL)
        return result

    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to fetch orders")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
