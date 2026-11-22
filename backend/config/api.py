"""Hai NinjaAPI: `api_v1` (nội bộ, cookie phiên) và `api_public` (công khai, chỉ GET).

Mỗi nhóm route nằm trong app của nó; file này chỉ gắn router (backend.md 3.1).
"""

from django.conf import settings
from ninja import NinjaAPI

from accounts.api import router as accounts_router
from catalog.api.products import router as products_router
from core.handlers import register_handlers
from core.permissions import OWNER_ONLY
from website.api.public import router as public_router

# Swagger chỉ bật khi DEBUG; prod không phơi schema ra ngoài (OpenAPI xuất bằng lệnh quản lý).
_docs = "/docs" if settings.DEBUG else None
_schema = "/openapi.json" if settings.DEBUG else None

api_v1 = NinjaAPI(
    title="VYC nội bộ",
    version="1",
    urls_namespace="api_v1",
    auth=OWNER_ONLY,  # route nào quên khai vai thì chỉ OWNER vào được (backend.md 4.3)
    docs_url=_docs,
    openapi_url=_schema,
)
api_public = NinjaAPI(
    title="VYC công khai",
    version="1",
    urls_namespace="api_public",
    auth=None,
    docs_url=_docs,
    openapi_url=_schema,
)

register_handlers(api_v1)
register_handlers(api_public)

api_v1.add_router("/auth", accounts_router)
api_v1.add_router("/products", products_router)
api_public.add_router("", public_router)
