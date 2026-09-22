import os

class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "ecommerce_dummy_db")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 1800))
    FILTER_CACHE_TTL: int = int(os.getenv("FILTER_CACHE_TTL", 3600))

    ALLOWED_ORIGINS: list[str] = ["*"]
    DEFAULT_PAGE_LIMIT: int = int(os.getenv("DEFAULT_PAGE_LIMIT", 20))


settings = Settings()