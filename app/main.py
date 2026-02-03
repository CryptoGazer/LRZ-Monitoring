import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.services.workers import Workers
from app.services.parser import parse_tag
from app.core.db import save_metric
from app.core.config import settings

TAGS = ["tag1", "tag2", "tag3", "tag4", "tag5"]  # TODO: Add all tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    workers = Workers(
        tags=TAGS,
        interval_sec=60,
        parse_fn=parse_tag,
        save_fn=save_metric,
    )
    await workers.start()
    app.state.workers = workers  # ??
    yield
    await workers.stop()



app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="LRZ IKOM Monitoring for 'Messe'",
    lifespan=lifespan
)

