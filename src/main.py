from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
# from .tasks.api import router as tasks_router  # Temporarily disabled
from .auth.api import router as auth_router

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


# Include routers
app.include_router(auth_router)
# app.include_router(tasks_router)  # Temporarily disabled
