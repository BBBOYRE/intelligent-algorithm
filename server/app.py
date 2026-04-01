import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.routes import (
    documents_router,
    chat_router,
    table_router,
    kb_router,
    files_router,
)
from utils.file_utils import ensure_runtime_dirs

def create_app() -> FastAPI:
    ensure_runtime_dirs()

    app = FastAPI(title="智能文档系统 API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(documents_router, prefix="/api", tags=["Documents"])
    app.include_router(chat_router, prefix="/api", tags=["Chat"])
    app.include_router(table_router, prefix="/api", tags=["Table"])
    app.include_router(kb_router, prefix="/api", tags=["KB"])
    app.include_router(files_router, prefix="/api", tags=["Files"])

    # Provide frontend in production mode
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    if os.path.exists(frontend_dist):
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    else:
        @app.get("/")
        async def root():
            return {"message": "API Server is running. Frontend dist not found. Please build frontend."}

    return app

app = create_app()
