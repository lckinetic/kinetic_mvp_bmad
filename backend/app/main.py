from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
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
from app.api.assistant import router as assistant_router
from app.api.workspaces import router as workspaces_router
from app.api.treasury import router as treasury_router
from app.api.recipients import router as recipients_router
from app.api.payout_workflows import router as payout_workflows_router
from app.api.activity import router as activity_router
from app.api.alerts import router as alerts_router


logger = logging.getLogger("kinetic")


class NoCacheStaticFiles(StaticFiles):
    """Serve UI kit assets without browser caching (local dev JSX reload)."""

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if isinstance(response, Response):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
        return response



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
                    "AI_PROVIDER": settings.ai_provider,
                    "AI_MODEL": settings.ai_model,
                    "OPENAI_API_KEY": settings.openai_api_key,
                    "OPENAI_BASE_URL": settings.openai_base_url,
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

    repo_root = Path(__file__).resolve().parents[2]
    ui_kit_dir = repo_root / "ui_kits" / "app"
    if ui_kit_dir.exists():
        app.mount("/ui-kit", NoCacheStaticFiles(directory=str(ui_kit_dir), html=True), name="ui-kit")

    @app.get("/")
    def root():
        return {"message": "Kinetic MVP API", "docs": "/docs", "health": "/health", "ui_kit": "/ui-kit"}

    app.include_router(health_router)
    app.include_router(onramp_router)
    app.include_router(offramp_router)
    app.include_router(webhooks_router)
    app.include_router(workflows_router)
    app.include_router(ui_router)
    app.include_router(ai_router)
    app.include_router(assistant_router)
    app.include_router(workspaces_router)
    app.include_router(treasury_router)
    app.include_router(recipients_router)
    app.include_router(payout_workflows_router)
    app.include_router(activity_router)
    app.include_router(alerts_router)

    return app


app = create_app()
