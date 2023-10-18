from pydantic import BaseModel
from typing import Optional

class SettingBase(BaseModel):
    pass

class Setting(SettingBase):
    pass

class SettingUpdate(SettingBase):
    api_key: Optional[str]
    prompt_id: Optional[str]