from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.exception_handlers import register_exception_handlers

app = FastAPI(title="Speech Learning API")

app.include_router(api_router, prefix="/api")
app.mount("/clips", StaticFiles(directory="data/clips"), name="clips")
app.mount(
    "/reference-audio",
    StaticFiles(directory="data/audio/reference"),
    name="reference-audio",
)
app.mount("/media", StaticFiles(directory="data/media"), name="media")
register_exception_handlers(app)
