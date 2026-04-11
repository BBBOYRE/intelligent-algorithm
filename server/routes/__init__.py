from server.routes.documents import router as documents_router
from server.routes.chat import router as chat_router
from server.routes.table import router as table_router
from server.routes.kb import router as kb_router
from server.routes.files import router as files_router

__all__ = [
    "documents_router",
    "chat_router",
    "table_router",
    "kb_router",
    "files_router",
]
