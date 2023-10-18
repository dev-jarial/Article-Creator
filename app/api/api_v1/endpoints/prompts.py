from fastapi import APIRouter, Depends, HTTPException
from app.schemas.prompts.prompt import PromptCreate, PromptUpdate
from sqlalchemy.orm import Session
from app.api import deps
from app.models.prompts.prompt import Prompt
from app.models.authentications.user import User
from fastapi.security.api_key import APIKey as SecureAPIKey
from app.lib.utils.api_tools import get_user, get_user_id
from datetime import datetime
import re
from sqlalchemy import asc

router = APIRouter()


@router.get("/{prompt_id}", tags=["prompts"])
def get_prompt(prompt_id: str, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    
    user_id = get_user_id(db, api_key)

    query = db.query(Prompt)
    prompt = query.filter(Prompt.prompt_id == prompt_id).filter(Prompt.user_id == user_id).first()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

# List
@router.get("/", tags=["prompts"])
def get_prompt_list(db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    user_id = get_user_id(db, api_key)
    prompts = db.query(Prompt).filter(Prompt.user_id == user_id).order_by(asc(Prompt.name)).all()

    if not prompts:
        raise HTTPException(status_code=404, detail="Prompts not found")

    return prompts


def lowercase_braces(match):
    return match.group(0).lower()

@router.post("/", status_code=200)
def create(prompt: PromptCreate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    user = get_user(db, api_key=api_key)

    filtered_prompt = re.sub(r'\{.*?\}', lowercase_braces, prompt.text_area)

    db_prompt = Prompt(
        name=prompt.name,
        description=prompt.description,
        text_area=filtered_prompt,
        gpt_model=prompt.gpt_model,
        temperature=prompt.temperature,
        max_length=prompt.max_length,
        top_p=prompt.top_p,
        frequency_penalty=prompt.frequency_penalty,
        presence_penalty=prompt.presence_penalty,
        created_at=datetime.now(),
        user=user
    )
    db.add_all([db_prompt])
    db.commit()
    db.refresh(db_prompt)

    return db_prompt

@router.put("/{prompt_id}", status_code=200)
def update(prompt_id: str, prompt_update: PromptUpdate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    user_id = get_user_id(db, api_key)
    prompt = db.query(Prompt).filter(Prompt.prompt_id == prompt_id).filter(Prompt.user_id == user_id).first()
    db_prompt = update_prompt(prompt, prompt_update, db)
    return db_prompt

@router.delete("/{prompt_id}", status_code=204)
def delete(prompt_id: str, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    prompt = db.query(Prompt).get(prompt_id)

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    db.delete(prompt)
    db.commit()

    return None

@router.post("/{prompt_id}/duplicate", status_code=201)
def duplicate(prompt_id: str,prompt:PromptUpdate, db: Session = Depends(deps.get_db), api_key: SecureAPIKey = Depends(deps.get_api_key)):
    user = get_user(db, api_key=api_key)
    prompt = db.query(Prompt).filter(Prompt.prompt_id == prompt_id).filter(Prompt.user_id == user.id).first()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    duplicate_prompt = Prompt(
        name=prompt.name,
        description=prompt.description,
        text_area=prompt.text_area,
        gpt_model=prompt.gpt_model,
        temperature=prompt.temperature,
        max_length=prompt.max_length,
        top_p=prompt.top_p,
        frequency_penalty=prompt.frequency_penalty,
        presence_penalty=prompt.presence_penalty,
        created_at=datetime.now(),
        user=user
    )

    db.add(duplicate_prompt)
    db.commit()
    db.refresh(duplicate_prompt)

    return duplicate_prompt


def update_prompt(prompt: Prompt, prompt_update: PromptUpdate, db: Session):
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # TODO: Check Logic as top_p is not updating
    for attr, value in prompt_update.dict(exclude_unset=True).items():
        setattr(prompt, attr, value)

    db.commit()
    db.refresh(prompt)

    return prompt

def update_prompt(prompt: Prompt, prompt_update: PromptUpdate, db: Session):
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    for attr, value in prompt_update.dict(exclude_unset=True).items():
        setattr(prompt, attr, value)

    db.commit()
    db.refresh(prompt)

    return prompt
