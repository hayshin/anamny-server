from celery import Celery

celery = Celery(
    __name__,
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

# Your FastAPI app and other code below
