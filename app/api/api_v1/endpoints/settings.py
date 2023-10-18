from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.prompts.setting import Setting
from app.models.authentications.user import User
from app.schemas.prompts.setting import SettingUpdate
from fastapi.security.api_key import APIKey as SecureAPIKey
from app.lib.utils.api_tools import get_user_id
import openai



router = APIRouter()

# Get the api_key from database

# @router.get("/{user_id}", status_code=200)
# def get_setting(user_id: str, db: Session = Depends(deps.get_db)):
#     setting = db.query(Setting).filter(Setting.user_id == user_id).all()
#     return setting

@router.get("/", tags=["settings"])
def get_setting_list(db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    user_id = get_user_id(db, api_key)
    # print(user_id)
    settings = db.query(Setting).filter(Setting.user_id == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Setting not found")
    return settings




# OpenAI API key validation code
def is_api_key_valid(api_key: str):
    try:
        openai.api_key = api_key
        response = openai.Completion.create(
            engine="davinci",
            prompt="This is a test.",
            max_tokens=5
        )
    except openai.OpenAIError as e:
        return False
    else:
        return True
    
@router.put("/", status_code=200)
def update_setting(setting_update: SettingUpdate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    # Check if the API key is valid
    print("#####",setting_update.prompt_id)
    if not is_api_key_valid(setting_update.api_key):
        raise HTTPException(status_code=400, detail="Invalid API key")
    
    user_id = get_user_id(db, api_key)
    
    setting = db.query(Setting).filter(Setting.user_id == user_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not setting:
        # If the setting doesn't exist, create a new one
        setting = Setting(user_id=user_id, api_key=setting_update.api_key,prompt_id=setting_update.prompt_id)
        db.add(setting)
    else:
        # Update the api_key for the existing setting
        setting.api_key = setting_update.api_key
        setting.prompt_id=setting_update.prompt_id
    db.commit()
    db.refresh(setting)
    return setting
