from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import items
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="FastAPI CRUD Demo", lifespan=lifespan)

app.include_router(items.router, prefix="/items", tags=["items"])


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI CRUD"}
