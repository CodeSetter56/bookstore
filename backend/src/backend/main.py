from contextlib import asynccontextmanager
from fastapi import FastAPI

from .api.router import api_router
from .db.init_db import init_db
from .db.pool import pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.open()   
    await init_db()      
    yield
    await pool.close()   


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)  