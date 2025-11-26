import asyncio
import json
import importlib
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pika

from infra.redis_infra import get_redis_async
from infra.rabbitmq_infra import RABBITMQ_URL, DEFAULT_QUEUE

redis = get_redis_async()

def import_function(function_path: str):
    """
    импортирует функцию по строке
    """
    module_path, function_name = function_path.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, function_name)


def process_message(ch, method, properties, body):
    """
    обрабатывает сообщение из очереди
    """
    try:
        message = json.loads(body)
        task_id = message["task_id"]
        function_path = message["function"]
        data = message.get("data", {})

        try:
            function = import_function(function_path)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(function(data))
            finally:
                loop.close()

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except ModuleNotFoundError as e:
            print(f"Module not found for task {task_id}: {str(e)}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except AttributeError as e:
            print(f"Function not found for task {task_id}: {str(e)}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error processing task {task_id}: {str(e)}")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    """
    запускает воркера для обработки задач
    """
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=DEFAULT_QUEUE, durable=True)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue=DEFAULT_QUEUE, on_message_callback=process_message)

    print(f"Worker started. Listening to queue '{DEFAULT_QUEUE}'...")
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()
