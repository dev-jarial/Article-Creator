from pydantic import BaseModel
from typing import Optional, Any
from sqlalchemy import Column, Enum, JSON, Text
from datetime import datetime


class ArticleBase(BaseModel):
    pass


class Arcticle(ArticleBase):
    pass


from typing import Optional, Any

class ArticleCreate(BaseModel):
    language: str
    main_keywords: str
    urls: Optional[str]
    status: Optional[str] = 'draft'
    keywords: Optional[str]
    heading_data: Optional[Any]
    parsed_prompt:Optional[str]
    created_at: Optional[datetime]
    total_words: Optional[int]
    cost: Optional[float]
    

class ArticleUpdate(BaseModel):
    language: Optional[str]
    main_keywords: Optional[str]
    urls: Optional[str]
    status: Optional[str]
    keywords: Optional[str]
    heading_data: Optional[Any]
    parsed_prompt: Optional[str]
    created_at: Optional[datetime]
    total_words: Optional[int]
    cost : Optional[float]
    is_meta : Optional[bool]