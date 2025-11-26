import datetime
import random
import asyncio
from infra.redis_infra import get_redis_async

from database.models import async_session
from database.repo import ResultRepository


async def finance_model(needed_data: dict) -> None:
    task_id = needed_data.get("task_id", None)
    if not task_id:
        pass
    print(f"Task ID: {task_id}")
    redis = get_redis_async()
    if not isinstance(needed_data, dict):
        await redis.set(needed_data.get("task_id"), "error result func", 3600)
    time_sleep = random.randint(1, 10)
    await asyncio.sleep(time_sleep)

    await redis.set(needed_data.get("task_id"), "result func", 3600)

    async with async_session() as session:
        needed_data.pop("task_id")
        repo = ResultRepository(session)
        res = await repo.create(
            data=f"{needed_data}", result="result", time_create=datetime.datetime.now()
        )
        print(res.id, res.data, res.result, res.time_create)
