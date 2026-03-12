import os
import sys

from celery import Celery

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", BROKER_URL)

celery = Celery(
    "socialguard",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["app.worker.tasks"],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_default_queue="celery",
)

if sys.platform == "darwin":
    # Avoid macOS Objective-C fork crashes with Celery prefork.
    celery.conf.update(worker_pool="solo", worker_concurrency=1)
