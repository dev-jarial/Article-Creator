from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api import deps
from app.core.config import settings

import json
import uuid

router = APIRouter()

# Upload
@router.post("/upload", status_code=200)
async def create(file: UploadFile = File(...), db: Session = Depends(deps.get_db)):

    if "audio/" not in file.content_type:
        return {"error": "File must be an MP3 audio file."}
    
    # TODO: Check 7 Min Length

    # Unique Name: Need to Polish This
    unique_id = uuid.uuid4()
    file_name = str(unique_id)+'-'+file.filename

    file_path = f"statics/{file_name}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    file_url = settings.STATIC_URL+file_name
    return {
        'file_url': file_url,
        'file_name': file.filename
    }



