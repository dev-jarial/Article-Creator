from pydantic import BaseModel, Json, HttpUrl

from enum import Enum

import typing as t
from datetime import datetime
from .file import FileCreate, File

class PredictionBase(BaseModel):
    status: str

    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class TOOLMODEL(str, Enum):
    TWOSTEMS = '2stems'
    FOURSTEMS = '4stems'
    FIVESTEMS = '5stems'

class Prediction(PredictionBase):
    inputs: Json[t.Any] = {}
    status: str

    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    files: t.List[File] = []

    class Config:
        orm_mode = True





class PredictionCreate(PredictionBase):
    status: str = "starting"
    tool: str = None
    inputs: t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]
    # TODO: File Need to Pass Here

    files: t.Union[t.List[FileCreate], None] = None
    


class PredictionUpdate(PredictionBase):
    status: str
    input: t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]
