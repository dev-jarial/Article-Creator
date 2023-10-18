from starlette.status import HTTP_403_FORBIDDEN
from app.models.authentications.user import APIKey, User
from fastapi import FastAPI, APIRouter, Security, Depends, HTTPException

def get_user_id(db, api_key):
    api_resource = db.query(APIKey).filter(APIKey.key == api_key).first()
    if api_resource is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
    user_id = api_resource.user_id
    return user_id

def get_user(db, api_key):
    user_id = get_user_id(db, api_key=api_key)
    user = db.query(User).filter(User.id == user_id).first()
    return user