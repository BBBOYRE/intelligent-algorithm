import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from server.database import SessionLocal
from server.models.audit_log import AuditLog

# 需要记录的 API 路径前缀和对应的 action 映射
ACTION_MAP = {
    "/api/documents/upload": ("upload", "document"),
    "/api/documents/upload-async": ("upload_async", "document"),
    "/api/chat": ("chat", "chat"),
    "/api/table/fill": ("table_fill", "table"),
    "/api/table/preview": ("table_preview", "table"),
    "/api/doc-ops/execute": ("doc_ops", "document"),
    "/api/kb/clear": ("kb_clear", "kb"),
    "/api/kb/create": ("kb_create", "kb"),
    "/api/auth/login": ("login", "auth"),
    "/api/auth/register": ("register", "auth"),
}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        method = request.method

        # 只记录 POST/DELETE 写操作和关键 GET
        if method not in ("POST", "DELETE", "PUT", "PATCH"):
            return await call_next(request)

        # 匹配 action
        action = None
        resource_type = ""
        for prefix, (act, res) in ACTION_MAP.items():
            if path.startswith(prefix):
                action = act
                resource_type = res
                break

        if not action:
            # DELETE /api/kb/{id} 等动态路径
            if path.startswith("/api/kb/") and method == "DELETE":
                action = "kb_delete"
                resource_type = "kb"
            elif path.startswith("/api/kb/documents/") and method == "DELETE":
                action = "doc_delete"
                resource_type = "document"
            else:
                return await call_next(request)

        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)

        # 提取 user_id（从 JWT 解析，简化处理）
        user_id = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from jose import jwt
                from config import Config
                token = auth_header[7:]
                payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
                user_id = payload.get("sub")
            except Exception:
                pass

        # 异步写入数据库
        try:
            db = SessionLocal()
            log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                detail=f"{method} {path}",
                ip_address=request.client.host if request.client else "",
                duration_ms=duration_ms,
                status_code=response.status_code,
            )
            db.add(log)
            db.commit()
            db.close()
        except Exception:
            pass

        return response
