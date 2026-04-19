import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.routes import (
    documents_router,
    chat_router,
    table_router,
    kb_router,
    files_router,
    doc_ops_router,
    auth_router,
    tasks_router,
    audit_router,
    analytics_router,
    teams_router,
    api_keys_router,
    webhooks_router,
    team_activity_router,
    kg_router,
    settings_router,
    inbox_router,
    memos_router,
)
from utils.file_utils import ensure_runtime_dirs

def get_resource_path(relative_path: str) -> str:
    """极其关键：兼容开发环境与 PyInstaller 打包环境的路径计算"""
    if getattr(sys, 'frozen', False):
        # 运行打包后的 EXE 时，定位到 _MEIPASS 临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境下，直接相对于项目根目录
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path)

def create_app() -> FastAPI:
    ensure_runtime_dirs()

    # 初始化数据库
    from server.database import init_db
    init_db()

    app = FastAPI(title="智能文档系统 API", version="2.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Filled-Count"] # [核心修复] 暴露自定义请求头给前端
    )

    app.include_router(auth_router, prefix="/api", tags=["Auth"])
    app.include_router(documents_router, prefix="/api", tags=["Documents"])
    app.include_router(chat_router, prefix="/api", tags=["Chat"])
    app.include_router(table_router, prefix="/api", tags=["Table"])
    app.include_router(kb_router, prefix="/api", tags=["KB"])
    app.include_router(files_router, prefix="/api", tags=["Files"])
    app.include_router(doc_ops_router, prefix="/api", tags=["DocOps"])
    app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
    app.include_router(audit_router, prefix="/api", tags=["Audit"])
    app.include_router(analytics_router, prefix="/api", tags=["Analytics"])
    app.include_router(teams_router, prefix="/api", tags=["Teams"])
    app.include_router(api_keys_router, prefix="/api", tags=["ApiKeys"])
    app.include_router(webhooks_router, prefix="/api", tags=["Webhooks"])
    app.include_router(team_activity_router, prefix="/api", tags=["TeamActivity"])
    app.include_router(kg_router, prefix="/api", tags=["KnowledgeGraph"])
    app.include_router(settings_router, prefix="/api", tags=["Settings"])
    app.include_router(inbox_router, prefix="/api", tags=["Inbox"])
    app.include_router(memos_router, prefix="/api", tags=["Memos"])

    # 审计中间件（记录写操作日志）
    from server.middleware.audit import AuditMiddleware
    app.add_middleware(AuditMiddleware)

    # 动态挂载前端静态文件
    frontend_dist = get_resource_path(os.path.join("frontend", "dist"))
    if os.path.exists(frontend_dist):
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    else:
        @app.get("/")
        async def root():
            return {"message": f"API 运行中。未找到前端资源，预期路径: {frontend_dist}"}

    return app

app = create_app()