from typing import Generator

from app.db.session import SessionLocal

from fastapi import FastAPI, APIRouter, Security, Depends, HTTPException

from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader

from app.models.authentications.user import APIKey
from datetime import datetime

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse


def get_db() -> Generator:
    db = SessionLocal()
    db.current_user_id = None
    try:
        yield db
    finally:
        print("Closed!")
        db.close()


# API_KEY = "Bearer eyJhbGciOiJIUzI1NiJ9"
API_KEY_NAME = "Authorization"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# api_key_header = api_key_header.replace("Bearer ", "")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    api_key_header = api_key_header.replace("Bearer ", "")
    
    db_generator = get_db()
    db = next(db_generator, None)
    
    current_time = datetime.utcnow()
    api_resource = db.query(APIKey).filter(APIKey.key == api_key_header, APIKey.expiration > current_time).first()

    if api_resource is not None:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
