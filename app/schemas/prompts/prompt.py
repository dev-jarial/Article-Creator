from pydantic import BaseModel
from typing import Optional
from datetime import datetime
class PromptBase(BaseModel):
    pass


class Prompt(PromptBase):
    pass


class PromptCreate(PromptBase):
    name: str
    description: str
    text_area: str
    gpt_model: str
    temperature: float
    max_length: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float


class PromptUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    text_area: Optional[str]
    gpt_model: Optional[str]
    temperature: Optional[float]
    max_length: Optional[int]
    top_p: Optional[float]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]