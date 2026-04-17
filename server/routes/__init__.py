from server.routes.documents import router as documents_router
from server.routes.chat import router as chat_router
from server.routes.table import router as table_router
from server.routes.kb import router as kb_router
from server.routes.files import router as files_router
from server.routes.doc_ops import router as doc_ops_router
from server.routes.auth import router as auth_router
from server.routes.tasks import router as tasks_router
from server.routes.audit import router as audit_router
from server.routes.analytics import router as analytics_router
from server.routes.teams import router as teams_router

__all__ = [
    "documents_router",
    "chat_router",
    "table_router",
    "kb_router",
    "files_router",
    "doc_ops_router",
    "auth_router",
    "tasks_router",
    "audit_router",
    "analytics_router",
    "teams_router",
]
