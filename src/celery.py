from celery import Celery
from .config import settings

# Create Celery instance
celery_app = Celery(
    "anamny",
    broker=f"redis://redis:6379/0",
    backend=f"redis://redis:6379/0",
    include=["src.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
)

# Auto-discover tasks
celery_app.autodiscover_tasks()

# Your FastAPI app and other code below
