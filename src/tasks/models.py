from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    deadline: Optional[datetime] = None
    description: str


class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
