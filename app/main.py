from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.exception_handlers import register_exception_handlers

app = FastAPI(title="Speech Learning API")

app.include_router(api_router, prefix="/api")
register_exception_handlers(app)

