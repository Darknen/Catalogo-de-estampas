"""API local do servidor central; dados operacionais não expostos sem autenticação."""
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.shared.constants import APP_NAME, APP_VERSION, API_VERSION
from app.server.database import Database, SCHEMA_VERSION
from config.settings import settings


def create_app(database: Database | None = None) -> FastAPI:
    db = database or Database(settings.database_path)
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db.initialize()
        app.state.database = db
        yield
    app = FastAPI(title=APP_NAME, version=APP_VERSION, docs_url=None, redoc_url=None, lifespan=lifespan)
    started = datetime.now(timezone.utc)

    @app.get('/health', tags=['diagnostics'])
    def health() -> dict[str,str]:
        return {'status':'online','api_version':API_VERSION}

    @app.get('/info', tags=['diagnostics'])
    def info() -> dict[str,str|int]:
        return {'name':APP_NAME,'app_version':APP_VERSION,'api_version':API_VERSION,
                'started_at':started.isoformat(),'schema_version':SCHEMA_VERSION}

    return app

app = create_app()
