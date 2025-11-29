import datetime
import random
import asyncio
from infra.redis_infra import get_redis_async

from database.models import async_session
from database.repo import ResultRepository

import json


async def finance_model(needed_data: dict) -> None:
    task_id = needed_data.get("task_id", None)
    if not task_id:
        pass
    print(f"Task ID: {task_id}")
    redis = get_redis_async()
    if not isinstance(needed_data, dict):
        await redis.set(
            needed_data.get("task_id"),
            json.dumps(
                {
                    "status": "failed",
                }
            ),
            3600,
        )
    time_sleep = random.randint(1, 10)
    await asyncio.sleep(time_sleep)

    await redis.set(
        needed_data.get("task_id"),
        json.dumps(
            {
                "status": "done",
                "result": {
                    "score": 0.73,
                    "decision": "approve",
                    "probability_default": 0.15,
                    "monthly_payment": 12500,
                    "approved_amount": 450000,
                    "revenue_series": [100000, 120000, 140000, 160000, 180000],
                    "recommendations": [
                        "Сумма запроса находится в приемлемом диапазоне.",
                        "Примерный ежемесячный платёж — 12,500 ₽; проверить платёжеспособность.",
                        "Низкая вероятность дефолта — можно рассмотреть выдачу при нормальной истории.",
                        "Решение модели: одобрено — подготовить документы для выдачи.",
                    ],
                },
            }
        ),
        3600,
    )

    async with async_session() as session:
        needed_data.pop("task_id")
        repo = ResultRepository(session)
        res = await repo.create(
            data=f"{needed_data}",
            result="""{
                "status": "done",
                "result": {
                    "score": 0.73,
                    "decision": "approve",
                    "probability_default": 0.15,
                    "monthly_payment": 12500,
                    "approved_amount": 450000,
                    "revenue_series": [100000, 120000, 140000, 160000, 180000],
                    "recommendations": [
                        "Сумма запроса находится в приемлемом диапазоне.",
                        "Примерный ежемесячный платёж — 12,500 ₽; проверить платёжеспособность.",
                        "Низкая вероятность дефолта — можно рассмотреть выдачу при нормальной истории.",
                        "Решение модели: одобрено — подготовить документы для выдачи.",
                    ],
                },
            }""",
            time_create=datetime.datetime.now(),
        )
        print(res.id, res.data, res.result, res.time_create)
