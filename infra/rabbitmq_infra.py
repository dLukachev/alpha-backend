import os
import json
import uuid
from typing import Any, Dict, Optional

import pika

DEFAULT_QUEUE = os.getenv("QUEUE_NAME", "finance_tasks")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")


def publish_task_one_shot(
    function_path: str,
    data: Dict[str, Any],
    task_id: Optional[str] = None,
    priority: Optional[int] = None,
    amqp_url: str = RABBITMQ_URL,
    queue: str = DEFAULT_QUEUE,
) -> str:
    if ":" not in function_path:
        raise ValueError(
            'function_path должен быть вида "package.module:function_name" или просто быть'
        )

    tid = task_id or str(uuid.uuid4())
    payload = {
        "task_id": tid,
        "function": function_path,
        "data": {**data, "task_id": tid} if data else {"task_id": tid},
    }
    body = json.dumps(payload).encode("utf-8")

    params = pika.URLParameters(amqp_url)
    connection = pika.BlockingConnection(params)
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)

        props = pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            message_id=tid,
            priority=priority,
        )

        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=body,
            properties=props,
        )
        return tid
    finally:
        try:
            connection.close()
        except Exception:
            pass
