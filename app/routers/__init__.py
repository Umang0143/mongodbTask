from fastapi import APIRouter

from app.routers import categories, filters, orders, payments, products, reviews, users

api_router = APIRouter()

api_router.include_router(filters.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)
api_router.include_router(users.router)
api_router.include_router(payments.router)
api_router.include_router(reviews.router)
api_router.include_router(categories.router)