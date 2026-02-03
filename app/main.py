from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="X8 Network SaaS Platform API"
)


@app.get("/")
async def root():
    return ...

