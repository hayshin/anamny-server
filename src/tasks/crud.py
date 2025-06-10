from typing import List

from ..database import get_all_tasks, save_task
from .models import Task, TaskCreate


class TaskCRUD:
    @staticmethod
    def create_task(task_data: TaskCreate) -> Task:
        return save_task(task_data)

    @staticmethod
    def get_all_tasks() -> List[Task]:
        return get_all_tasks()
