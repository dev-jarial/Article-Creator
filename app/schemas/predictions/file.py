from pydantic import BaseModel, Json

import typing as t
from datetime import datetime


class FileBase(BaseModel):
    file_url: str

class File(FileBase):
    file_url: str
    prediction_id: str

    class Config:
        orm_mode = True

class FileCreate(FileBase):
    file_url: str
    params: t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]
    
class FileUpdate(FileBase):
    file_url: str
    params: t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]
