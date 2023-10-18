from pydantic import BaseModel, Json, HttpUrl

import typing as t
from datetime import datetime

class UserBase(BaseModel):
    email: str
    name: str
    username: str

class User(UserBase):

    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    pass

class RegisteredUser(UserBase):
    apiKey: str = None
    user_id: str = None

class LogUser(BaseModel):
    email: str
    password: str