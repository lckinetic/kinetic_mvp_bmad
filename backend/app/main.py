from contextlib import asynccontextmanager

from fastapi import FastAPI
import logging

from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging, safe_settings_log
from app.db.engine import get_engine, create_db_and_tables

# IMPORTANT: import models so SQLModel knows about tables before create_all()
from app.db import models  # noqa: F401

from app.api.health import router as health_router
from app.api.onramp import router as onramp_router
from app.api.offramp import router as offramp_router
from app.api.webhooks import router as webhooks_router
from app.api.workflows import router as workflows_router
from app.ui.router import router as ui_router
from app.api.ai import router as ai_router


logger = logging.getLogger("kinetic")



def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = get_engine(settings)
        create_db_and_tables(engine)
        logger.info(
            "Startup complete. %s",
            safe_settings_log(
                {
                    "MOCK_MODE": settings.mock_mode,
                    "BANXA_ENV": settings.banxa_env,
                    "DATABASE_URL": settings.database_url,
                    "BANXA_API_KEY": settings.banxa_api_key,
                    "BANXA_API_SECRET": settings.banxa_api_secret,
                    "BANXA_WEBHOOK_SECRET": settings.banxa_webhook_secret,
                }
            ),
        )
        yield

    app = FastAPI(title="Kinetic MVP API", version="0.1.0", lifespan=lifespan)
    register_error_handlers(app)

    @app.get("/")
    def root():
        return {"message": "Kinetic MVP API", "docs": "/docs", "health": "/health"}

    app.include_router(health_router)
    app.include_router(onramp_router)
    app.include_router(offramp_router)
    app.include_router(webhooks_router)
    app.include_router(workflows_router)
    app.include_router(ui_router)
    app.include_router(ai_router)

    return app


app = create_app()
