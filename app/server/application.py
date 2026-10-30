"""API mínima do servidor central (sem dados operacionais)."""
from datetime import datetime, timezone
from fastapi import FastAPI
from app.shared.constants import APP_NAME, APP_VERSION, API_VERSION


def create_app() -> FastAPI:
    app = FastAPI(title=APP_NAME, version=APP_VERSION, docs_url=None, redoc_url=None)
    started = datetime.now(timezone.utc)

    @app.get("/health", tags=["diagnostics"])
    def health() -> dict[str, str]:
        return {"status": "online", "api_version": API_VERSION}

    @app.get("/info", tags=["diagnostics"])
    def info() -> dict[str, str | int]:
        return {
            "name": APP_NAME,
            "app_version": APP_VERSION,
            "api_version": API_VERSION,
            "started_at": started.isoformat(),
        }

    return app


app = create_app()
