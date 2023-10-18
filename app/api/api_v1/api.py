from fastapi import APIRouter
from app.api.api_v1.endpoints import predictions, files, authentication, prompts, settings, articles

api_router = APIRouter()
api_router.include_router(authentication.router)
api_router.include_router(predictions.router, prefix="/predictions")
api_router.include_router(files.router, prefix="/files")
api_router.include_router(prompts.router, prefix="/prompts")
api_router.include_router(settings.router, prefix="/settings")
api_router.include_router(articles.router, prefix="/articles")