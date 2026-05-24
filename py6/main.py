from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from datetime import datetime

from models import Task, TaskUpdate, TaskPatch, TaskResponse
import storage

title = "Advanced Task API"
version = "2.0"

app = FastAPI(title=title, version = version)

@app.get("/")
def root():
    return {"message" : title, "version" : version}



@app.get("/tasks", response_model = list[TaskResponse]) 
def get_tasks(
    completed: Optional[bool] = Query(default = None),
    priority: Optional[str] = Query(default = None, pattern = "^(low|medium|high)$"),
    limit: Optional[int] = Query(default = None, ge = 1),
    sort_by:Optional[str] = Query(default = None, pattern = "^(created_at|priority)$")
):
    return storage.list_tasks(
        completed = completed,
        priority = priority,
        limit = limit,
        sort_by = sort_by
    )


@app.get("/tasks/search", response_model=list[TaskResponse])
def search_tasks(
    keyword: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default = None, pattern = ("^low|medium|high")),
    date_from: Optional[datetime] = Query(default = None),
    date_to: Optional[datetime] = Query(defaukt = None)
):
    return storage.search_tasks(
        keyword = keyword,
        priority = priority,
        date_from=date_from,
        date_to=date_to
    )



@app.get("/tasks/stats")
def get_stats():
    return storage.get_stats()



@app.get("/tasks/archived", response_model=list[TaskResponse])
def get_archived_tasks():
    return storage.list_archived_tasks()



@app.get("/tasks/{task_id}", response_model = TaskResponse)
def get_task(task_id : int):
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code = 404, detail = f"Задача {task_id} не найдена")
    return storage._to_response(task)




@app.post("/tasks", response_model = TaskResponse, status_code=201)
def create_task(body: Task):
    if storage.title_exists(body.title):
        raise HTTPException(status_code=400, detail=f"Задача с названием '{body.title}' уже существует")
    return storage.create_task(body.model_dump()) #model -> dict



@app.put("/tasks/{task_id}", response_model = TaskResponse)
def full_update_task(task_id: int, body : TaskUpdate):
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code= 404, detail=f"Задача {task_id} не найдена")
    
    if storage.title_exists(body.title, exclude_id = task_id):
        raise HTTPException(status_code=400, detail = f"Задача с названием {body.title} уже существует")
    return storage.update_task_full(task, body.model_dump())



@app.patch("/tasks/{task_id}", response_model = TaskResponse)
def partial_update_task(task_id: int, body: TaskPatch):
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code = 404, detail = f"Задача {task_id} не найдена")
    
    if body.title is not None and storage.title_exists(body.title, exclude_id = task_id):
        raise HTTPException(status_code=400, detail = f"Задача с названием {body.title} уже существует")
    
    return storage.update_task_partial(task, body.model_dump(exclude_unset=True))



@app.patch("/tasks/{task_id}/complete", response_model = TaskResponse)
def complete_task(task_id : int):
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code = 404, detail = f"Задача {task_id} не найдена")
    if task["completed"]:
        raise HTTPException(status_code=400, detail = "Задача уже завершена")
    return storage.complete_task(task) 



@app.delete("/tasks/{task_id}")
def delete_task(task_id : int):
    task = storage.get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code = 404, detail = f"Задача {task_id} не найдена")
    
    storage.delete_task(task_id)
    return {"message" : f"Задача {task_id} была успешно удалена"}


