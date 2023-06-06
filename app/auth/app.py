from fastapi import FastAPI
from sqlalchemy.orm import clear_mappers

from app.auth import dependencies as deps
from app.auth.routes import auth_router


def create_app():
    fastapi_app = FastAPI(
        title="Auth server",
        docs_url="/",
    )
    fastapi_app.include_router(auth_router)
    return fastapi_app


app = create_app()


@app.on_event("startup")
async def startup_event():
    deps.register_mapping()


@app.on_event("shutdown")
async def startup_event():
    clear_mappers()
