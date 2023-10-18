from typing import Optional
from pydantic import BaseSettings
from urllib.parse import quote_plus
import os

from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    DB_USER: str = os.environ.get('DB_USER')
    DB_PASSWORD: str = os.environ.get('DB_PASSWORD')
    DB_HOST: str = os.environ.get('DB_HOST')
    DB_PORT: str = os.environ.get('DB_PORT')
    DB_NAME: str = os.environ.get('DB_NAME')

    SQLALCHEMY_DATABASE_URI: Optional[str] = 'mysql://{0}:{1}@{2}:{3}/{4}'.format(DB_USER, quote_plus(DB_PASSWORD), DB_HOST, DB_PORT, DB_NAME)


    # File Upload Path
    # AUDIO_OUTPUT_PATH: str = os.environ.get("AUDIO_OUTPUT_PATH")

    # Splitter
    # SPLITTER_AUDIO_UPLOAD_PATH: str = os.environ.get('SPLITTER_AUDIO_UPLOAD_PATH') 

    # SPLEETER_PATH: str = os.environ.get("SPLEETER_PATH")

    # BASE URL
    BASE_URL: str = os.environ.get('BASE_URL')

    # STATIC URL
    STATIC_URL: str = os.environ.get('STATIC_URL')


    # Log File
    LOG_FILE: str = os.environ.get('LOG_FILE')




settings = Settings()