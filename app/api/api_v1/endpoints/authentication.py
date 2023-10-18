from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api import deps

from app.models.authentications.user import User, Role, UserRole, APIKey
from app.schemas.authentications.user import UserCreate, LogUser, RegisteredUser

import secrets

from datetime import datetime, timedelta

router = APIRouter()


def check_email_or_username_exists(email: str = None, username: str = None, db: Session = Depends(deps.get_db)):
    if email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            raise HTTPException(status_code=400, detail="Email already exists")
    if username:
        user = db.query(User).filter(User.username == username).first()
        if user:
            raise HTTPException(status_code=400, detail="Username already exists")



@router.post('/signup', summary="Create new user", response_model=RegisteredUser)
async def create_user(data: UserCreate, db: Session = Depends(deps.get_db)):

    check_email_or_username_exists(data.email, data.username, db=db)

    query = db.query(Role)
    roles = query.filter(Role.name.in_(['customer'])).all()
    
    user = User(
         name = data.name,
         email = data.email,
         username = data.username,
    )
    user.set_password(data.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create a list of UserRole objects in a single line using list comprehension
    user_roles = [UserRole(user_id=user.id, role_id=role.id) for role in roles]
    db.add_all(user_roles)

    api_key = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=5)
    user.api_keys.append(APIKey(key=api_key, expiration=expiration))

    db.commit()
    db.refresh(user)

    return {
        'email': user.email,
        'name': user.name,
        'username': user.username,
        'apiKey': api_key,
        'apiKeyExpiration': expiration,
        'user_id': user.id
    }


def check_login(email, password, db):
    user = db.query(User).filter(or_(User.email == email, User.username == email)).first()
    if user is None:
         raise HTTPException(status_code=401, detail="Account does not exists!")
    if not (user.verify_password(password)):
        raise HTTPException(status_code=401, detail="Incorrect User and Password!")

    return user

def clear_expired_tokens(user, db):
    current_time = datetime.utcnow()
    expired_api_keys = [api_key for api_key in user.api_keys if api_key.expiration < current_time]
    for api_key in expired_api_keys:
        db.delete(api_key)
    db.commit()


@router.post('/login', summary="Login", response_model=RegisteredUser)
async def login(data: LogUser, db: Session = Depends(deps.get_db)):
    user = check_login(data.email, data.password, db)
    clear_expired_tokens(user, db)

    api_key = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=5)
    user.api_keys.append(APIKey(key=api_key, expiration=expiration))

    db.commit()
    db.refresh(user)

    return {
        'email': user.email,
        'name': user.name,
        'username': user.username,
        'apiKey': api_key,
        'apiKeyExpiration': expiration,
        'user_id': user.id
    }



