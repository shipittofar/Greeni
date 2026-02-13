from fastapi import APIRouter
from app.tasks.example import add

router = APIRouter()

@router.get("/add-task")
def run_add_task(a: int = 1, b: int = 2):
    task = add.delay(a, b)
    return {"task_id": task.id}
