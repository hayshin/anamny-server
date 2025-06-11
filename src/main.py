from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .auth.api import router as auth_router
from .celery import celery_app

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Anamny Health Tracker API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.name} API"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "celery": "configured"
    }


# Include routers
app.include_router(auth_router)

# Add a test endpoint to trigger Celery tasks
@app.post("/test-celery")
def test_celery():
    from .tasks import send_email_task
    
    # Trigger a background task
    task = send_email_task.delay(
        to="test@example.com",
        subject="Test Email",
        body="This is a test email from Celery!"
    )
    
    return {
        "message": "Celery task triggered",
        "task_id": task.id
    }
