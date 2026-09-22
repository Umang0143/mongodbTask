"""Common helper functions shared across routers."""

import math
from datetime import datetime
from typing import Any

from bson import ObjectId


def convert_mongo_data(data: Any) -> Any:
    """Recursively converts MongoDB ObjectIds and Datetimes into JSON-safe strings."""
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, datetime):
        return data.isoformat()
    if isinstance(data, list):
        return [convert_mongo_data(item) for item in data]
    if isinstance(data, dict):
        return {key: convert_mongo_data(value) for key, value in data.items()}
    return data


def build_pagination(total_results: int, page: int, limit: int) -> dict:
    """Returns the common pagination block used by every list endpoint."""
    total_pages = math.ceil(total_results / limit) if total_results > 0 else 0
    return {
        "total_results": total_results,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
