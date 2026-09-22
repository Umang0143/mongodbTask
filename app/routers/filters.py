"""Global filter options endpoint (brands, colors, dynamic price ranges)."""

import logging
import math

from fastapi import APIRouter, HTTPException

from app.cache import cache_get, cache_set
from app.config import settings
from app.database import products_col

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/filters", tags=["Filters"])

CACHE_KEY = "global_filters"


def _build_price_ranges(min_price: float, max_price: float) -> list[dict]:
    min_p = math.floor(min_price)
    max_p = math.ceil(max_price)
    step = (max_p - min_p) // 4

    if step <= 0:
        return []

    return [
        {"label": f"Under ₹{min_p + step}", "value": f"0-{min_p + step}"},
        {
            "label": f"₹{min_p + step} - ₹{min_p + step * 2}",
            "value": f"{min_p + step}-{min_p + step * 2}",
        },
        {
            "label": f"₹{min_p + step * 2} - ₹{min_p + step * 3}",
            "value": f"{min_p + step * 2}-{min_p + step * 3}",
        },
        {"label": f"Above ₹{min_p + step * 3}", "value": f"{min_p + step * 3}+"},
    ]


@router.get("")
def get_filter_options():
    cached = cache_get(CACHE_KEY)
    if cached:
        return cached

    try:
        brands = sorted(b for b in products_col.distinct("brand") if b)
        colors = sorted(c for c in products_col.distinct("color") if c)

        price_stats = list(
            products_col.aggregate(
                [{"$group": {"_id": None, "min_price": {"$min": "$price"}, "max_price": {"$max": "$price"}}}]
            )
        )

        price_ranges = []
        if price_stats and price_stats[0].get("min_price") is not None:
            price_ranges = _build_price_ranges(price_stats[0]["min_price"], price_stats[0]["max_price"])

        result = {"brands": brands, "colors": colors, "dynamic_prices": price_ranges}
        cache_set(CACHE_KEY, result, settings.FILTER_CACHE_TTL)
        return result

    except Exception as exc:
        logger.exception("Failed to build filter options")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
