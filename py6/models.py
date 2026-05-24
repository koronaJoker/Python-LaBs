from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class Task(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    completed: bool = False
    deadline: Optional[datetime] = None



class TaskUpdate(BaseModel):
    title: str = Field(..., min_length = 1, max_length = 100)
    description: Optional[str] = None
    priority: str = Field(default = "medium", pattern = "^(low|medium|high)$")
    completed: bool = False
    deadline : Optional[datetime] = None



class TaskPatch(BaseModel):
    title:Optional[str] = Field(default = None, min_length = 1, max_length = 100)
    description: Optional[str] = None
    priority: Optional[str] = Field(default = None, pattern = "^(low|medium|high)$")
    deadline: Optional[datetime] = None



class TaskResponse(BaseModel):
    id: int
    title:str
    description: Optional[str]
    priority: str
    completed: bool
    deadline: Optional[datetime]
    created_at: datetime
    completed_at: Optional[datetime] = None
