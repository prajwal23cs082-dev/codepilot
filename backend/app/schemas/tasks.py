from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class TaskBase(BaseModel):
    description: str

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: str
    project_id: str
    status: str
    plan: Optional[Any] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
