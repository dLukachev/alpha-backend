import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.exceptions import HTTPException

from utils.data_model import PayloadModel

from infra.redis_infra import get_redis_async
from infra.rabbitmq_infra import publish_task_one_shot

from database.models import async_session
from database.repo import ResultRepository

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

@app.get("/")
async def health():
    return Response("Status: ok", 200)

@app.post("/finance")
async def enqueue_financial_model(payload: PayloadModel):
    print(payload.data)
    if not payload or not payload.data:
        raise HTTPException(status_code=400, detail="Dict not found")

    async with async_session() as session:
        repo = ResultRepository(session)
        data_in_db = await repo.get_by_data(payload.data)

    if data_in_db:
        return Response(f"{data_in_db.result}", 200)

    task_id = publish_task_one_shot(
        function_path="utils.simple_finance_model:finance_model",
        data=payload.data,
    )
    return Response(json.dumps({"task_id": task_id}), 200)


@app.get("/task/{task_id}")
async def get_task_result(task_id: str):
    redis = get_redis_async()
    result = await redis.get(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(result, 200)

@app.get("/redis_health")
async def redis_health():
    redis = get_redis_async()
    await redis.set("redis_health", 123, 10)
    data = await redis.get("redis_health")
    if int(data) == 123:
        return Response("ok", 200)
    else:
        return Response("not ok", 400)