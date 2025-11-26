import os
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()


def get_redis_async() -> Redis:
    port = os.getenv("PORT", "None")
    return Redis(
        host=os.getenv("HOST", "None"),
        port=int(port),
        decode_responses=bool(os.getenv("DECODE", "None")),
        username=os.getenv("USERNAME", "None"),
        password=os.getenv("PASSWORD", "None"),
    )
