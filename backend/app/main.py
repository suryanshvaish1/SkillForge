
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import router
from app.core.config import get_settings
from app.core.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hooks."""
    setup_logging()
    settings = get_settings()
    logger.info("Starting {} (env={})", settings.app_name, settings.app_env)

    # Eagerly load heavy singletons so first request isn't slow
    from app.services.skill_extractor import get_skill_extractor
    from app.services.gap_analyser import get_gap_analyser
    from app.services.pathway_generator import get_recommender

    get_skill_extractor()
    get_gap_analyser()
    get_recommender()
    logger.info("All services initialised successfully")

    yield  # App is running

    logger.info("Shutting down {}", settings.app_name)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="AI-driven adaptive learning pathway generator for corporate onboarding",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_debug,
        log_level=settings.log_level.lower(),
    )
