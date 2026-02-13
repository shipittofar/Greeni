# app/cache/redis.py
import redis.asyncio as redis

redis_client = redis.Redis(
    host="greeni_redis",  # نام کانتینر در شبکه Docker
    port=6379,
    decode_responses=True
)
