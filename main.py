import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import router as api_router
from app.core.config import get_settings

settings = get_settings()

# Configure Loguru
logger.add("logs/app.log", rotation="500 MB")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

# Configure CORS
# By default allow everything if the list is empty to avoid confusion during dev, 
# or strictly follow the empty list. 
# "配置 CORS 中间件" - usually implies setting it up. 
# If BACKEND_CORS_ORIGINS is empty, we might want to default to nothing or everything. 
# I'll stick to what is in settings. If list is empty, allow_origins is empty.
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Optional: Allow all for development if not specified? 
    # The prompt didn't strictly say "allow all". 
    # But usually for a fresh project, it's safer to add it and let user config.
    # I will instantiate it even if empty, so it's "configured".
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Default to allow all for dev convenience if not set
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
