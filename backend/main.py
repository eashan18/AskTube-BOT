from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import videos, chat, health
from .config.logging_config import setup_logging
from .config.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings)

    app = FastAPI(title="AskTube AI")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(videos.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(health.router, prefix="/api")

    return app


app = create_app()
