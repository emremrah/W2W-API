from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from wtw import __version__
from wtw.api.app import router as api_router  # noqa
from wtw.api.router import router

origins = ["*"]  # TODO


app = FastAPI(title="What to Watch API", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/api")
async def index():
    return {"message": "What to Watch API", "version": __version__}


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400, content={"detail": exc.errors(), "body": exc.model}
    )
