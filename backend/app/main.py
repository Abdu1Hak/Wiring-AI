from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai, components, wiring
from app.config import CORS_ORIGINS
from app.seed.seed_db import seed_database


@asynccontextmanager
async def lifespan(_app: FastAPI):
    seed_database()
    yield


app = FastAPI(title="Wiring AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(components.router)
app.include_router(ai.router)
app.include_router(wiring.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
