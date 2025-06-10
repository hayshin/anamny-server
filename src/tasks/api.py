from typing import List

from fastapi import APIRouter

from .crud import TaskCRUD
from .models import Task, TaskCreate

router = APIRouter(prefix="/tasks")


@router.post("/create", response_model=Task)
async def create_task(task_data: TaskCreate):
    return TaskCRUD.create_task(task_data)


@router.get("/get_all", response_model=List[Task])
async def get_tasks():
    return TaskCRUD.get_all_tasks()
