from datetime import datetime, timedelta
from typing import Optional
from models import TaskResponse

tasks = [
    {
        "title": "Buy groceries",
        "description": "Milk, bread, eggs",
        "priority": "high",
        "deadline": datetime.now() + timedelta(days=1),
    },
    {
        "title": "Read Python docs",
        "description": "Study FastAPI documentation",
        "priority": "medium",
    },
    {
        "title": "Fix login bug",
        "description": "Users can't login with Google",
        "priority": "high",
        "deadline": datetime.now() - timedelta(days=1),
    },
    {
        "title": "Write unit tests",
        "priority": "medium",
        "deadline": datetime.now() + timedelta(days=3),
    },
    {
        "title": "Clean the house",
        "priority": "low",
    },
    {
        "title": "Call dentist",
        "description": "Schedule appointment for next week",
        "priority": "high",
    },
    {
        "title": "Update README",
        "description": "Add installation instructions",
        "priority": "low",
    },
    {
        "title": "Review pull request",
        "description": "PR #42 from teammate",
        "priority": "high",
        "deadline": datetime.now() + timedelta(hours=5),
        "completed": True
    },
    {
        "title": "Buy birthday gift",
        "description": "For mom's birthday",
        "priority": "high",
        "deadline": datetime.now() - timedelta(days=2),
    },
    {
        "title": "Learn Docker",
        "priority": "medium",
    },
    {
        "title": "Pay bills",
        "description": "Electricity and internet",
        "priority": "high",
        "deadline": datetime.now() + timedelta(days=2),
    },
    {
        "title": "Refactor storage.py",
        "description": "Too many duplicate functions",
        "priority": "low",
    },
    {
        "title": "Setup CI/CD",
        "priority": "medium",
        "deadline": datetime.now() + timedelta(days=7),
    },
    {
        "title": "Watch lecture recording",
        "description": "Database lecture from Monday",
        "priority": "medium",
    },
    {
        "title": "Go to gym",
        "priority": "low",
    },
    {
        "title": "Deploy to production",
        "description": "New release v2.0",
        "priority": "high",
        "deadline": datetime.now() + timedelta(days=1),
    },
    {
        "title": "Fix CSS layout",
        "description": "Mobile navbar is broken",
        "priority": "medium",
    },
    {
        "title": "Grocery list for party",
        "priority": "low",
        "deadline": datetime.now() + timedelta(days=4),
    },
    {
        "title": "Submit lab report",
        "description": "Lab 6 FastAPI",
        "priority": "high",
        "deadline": datetime.now() + timedelta(days=1),
    },
    {
        "title": "Backup database",
        "description": "Weekly backup",
        "priority": "medium",
    },
    {
        "title": "This task gets archived",
        "description": "21st task — triggers auto archive",
        "priority": "low",
    }
]

archived_tasks: list[dict] = []

_id_counter = 0
MAX_TASKS = 20

PRIORITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2
}


def _next_id() -> int:
    global _id_counter
    _id_counter += 1
    return _id_counter


def _init_tasks() -> None:
    for task in tasks:
        task["id"] = _next_id()
        task.setdefault("description", None)
        task.setdefault("priority", "medium")
        task.setdefault("completed", False)
        task.setdefault("deadline", None)
        task["created_at"] = datetime.now()
        task["completed_at"] = None


def _archive_old_tasks() -> None:
    global tasks, archived_tasks

    while len(tasks) > MAX_TASKS:
        oldest = min(tasks, key=lambda t: t["created_at"])
        tasks.remove(oldest)
        archived_tasks.append(oldest)


_init_tasks()
_archive_old_tasks()


def _to_response(task: dict) -> TaskResponse:
    return TaskResponse(**task)


def is_overdue(task: dict) -> bool:
    return (
        task.get("deadline") is not None
        and task["deadline"] < datetime.now()
        and not task["completed"]
    )


def title_exists(title: str, exclude_id: Optional[int] = None) -> bool:
    return any(
        t["title"].lower() == title.lower()
        and t["id"] != exclude_id
        for t in tasks
    )


def get_task_by_id(task_id: int) -> Optional[dict]:
    return next((t for t in tasks if t["id"] == task_id), None)


def create_task(data: dict) -> TaskResponse:
    task = {
        "id": _next_id(),
        "title": data["title"],
        "description": data.get("description"),
        "priority": data.get("priority", "medium"),
        "completed": data.get("completed", False),
        "deadline": data.get("deadline"),
        "created_at": datetime.now(),
        "completed_at": None
    }

    tasks.append(task)

    _archive_old_tasks()

    return _to_response(task)


def list_tasks(
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    limit: Optional[int] = None,
    sort_by: Optional[str] = None,
) -> list[TaskResponse]:

    result = list(tasks)

    if completed is not None:
        result = [t for t in result if t["completed"] == completed]

    if priority is not None:
        result = [t for t in result if t["priority"] == priority]

    if sort_by == "priority":
        result.sort(key=lambda t: PRIORITY_ORDER.get(t["priority"], 99))

    elif sort_by == "created_at":
        result.sort(key=lambda t: t["created_at"])

    if limit is not None:
        result = result[:limit]

    return [_to_response(t) for t in result]


def list_archived_tasks() -> list[TaskResponse]:
    return [_to_response(t) for t in archived_tasks]


def update_task_full(task: dict, data: dict) -> TaskResponse:
    task["title"] = data["title"]
    task["description"] = data.get("description")
    task["priority"] = data.get("priority", "medium")
    task["completed"] = data.get("completed", False)
    task["deadline"] = data.get("deadline")

    if task["completed"]:
        task["completed_at"] = datetime.now()
    else:
        task["completed_at"] = None

    return _to_response(task)


def update_task_partial(task: dict, data: dict) -> TaskResponse:
    if "title" in data:
        task["title"] = data["title"]

    if "description" in data:
        task["description"] = data["description"]

    if "priority" in data:
        task["priority"] = data["priority"]

    if "deadline" in data:
        task["deadline"] = data["deadline"]

    if "completed" in data:
        task["completed"] = data["completed"]

        if data["completed"]:
            task["completed_at"] = datetime.now()
        else:
            task["completed_at"] = None

    return _to_response(task)


def complete_task(task: dict) -> TaskResponse:
    task["completed"] = True
    task["completed_at"] = datetime.now()

    return _to_response(task)


def delete_task(task_id: int) -> None:
    task = get_task_by_id(task_id)

    if task is not None:
        tasks.remove(task)


def search_tasks(
    keyword: Optional[str] = None,
    priority: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> list[TaskResponse]:

    result = list(tasks)

    if keyword:
        kw = keyword.lower()

        result = [
            t for t in result
            if kw in t["title"].lower()
            or (t.get("description") and kw in t["description"].lower())
        ]

    if priority:
        result = [t for t in result if t["priority"] == priority]

    if date_from:
        result = [t for t in result if t["created_at"] >= date_from]

    if date_to:
        result = [t for t in result if t["created_at"] <= date_to]

    return [_to_response(t) for t in result]


def get_stats() -> dict:
    total = len(tasks)

    completed = sum(1 for t in tasks if t["completed"])

    not_completed = total - completed

    overdue = sum(1 for t in tasks if is_overdue(t))

    priority_dist = {
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for t in tasks:
        priority_dist[t["priority"]] += 1

    return {
        "total": total,
        "completed": completed,
        "not_completed": not_completed,
        "overdue": overdue,
        "by_priority": priority_dist,
    }