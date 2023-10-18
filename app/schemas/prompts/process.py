from pydantic import BaseModel
from typing import Optional, Any
from sqlalchemy import Column, Enum, Text
from datetime import datetime

class ProcessBase(BaseModel):
    pass


class Process(ProcessBase):
    pass


class Process(BaseModel):
    status: str = 'pending'
    response: Optional[str]
    cost: float
    created_at: datetime
    heading_data: Optional[Any]
    prompt_format: Optional[str]