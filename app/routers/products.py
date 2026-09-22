"""Products listing endpoint with search, filters, and pagination."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.cache import cache_get, cache_set, generate_cache_key
from app.config import settings
from app.database import products_col
from app.utils import build_pagination, convert_mongo_data

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/products", tags=["Products"])


def _build_price_filter(price_range: List[str]) -> list[dict]:
    conditions = []
    for price in price_range:
        if "-" in price:
            min_p, max_p = price.split("-", 1)
            conditions.append({"price": {"$gte": float(min_p), "$lte": float(max_p)}})
        elif "+" in price:
            min_p = price.replace("+", "")
            conditions.append({"price": {"$gte": float(min_p)}})
    return conditions


@router.get("")
def get_products(
    search: Optional[str] = Query(None),
    brand: Optional[List[str]] = Query(None),
    color: Optional[List[str]] = Query(None),
    price_range: Optional[List[str]] = Query(None),
    rating: Optional[float] = Query(None),
    is_prime: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
):
    cache_key = generate_cache_key(
        "products",
        search=search,
        brand=brand,
        color=color,
        price_range=price_range,
        rating=rating,
        is_prime=is_prime,
        page=page,
        limit=limit,
    )

    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        query: dict = {}

        if search:
            query["name"] = {"$regex": search.strip(), "$options": "i"}
        if brand:
            query["brand"] = {"$in": brand}
        if color:
            query["color"] = {"$in": color}
        if rating is not None:
            query["rating"] = rating
        if is_prime == "true":
            query["is_prime"] = True
        elif is_prime == "false":
            query["is_prime"] = False

        if price_range:
            price_conditions = _build_price_filter(price_range)
            if len(price_conditions) == 1:
                query.update(price_conditions[0])
            elif price_conditions:
                query["$or"] = price_conditions

        total_results = (
            products_col.count_documents(query) if query else products_col.estimated_document_count()
        )

        skip = (page - 1) * limit
        products = [
            convert_mongo_data(p)
            for p in products_col.find(query).sort("rating", -1).skip(skip).limit(limit)
        ]

        result = {
            "success": True,
            "applied_filters": convert_mongo_data(query),
            **build_pagination(total_results, page, limit),
            "products": products,
        }

        cache_set(cache_key, result, settings.CACHE_TTL)
        return result

    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to fetch products")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
