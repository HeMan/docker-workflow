import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import api, web

BASE_DIR = Path(__file__).resolve().parent.parent


def run_migrations() -> None:
    """Run Alembic migrations up to head.

    Alembic's async env.py drives its own event loop via asyncio.run(), so this
    must be called off the event loop that's running the lifespan handler.
    """
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(run_migrations)
    yield


app = FastAPI(title="Todo", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
app.include_router(api.router)
app.include_router(web.router)
