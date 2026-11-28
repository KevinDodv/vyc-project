"""Hai NinjaAPI: `api_v1` (nội bộ, cookie phiên) và `api_public` (công khai, chỉ GET).

Mỗi nhóm route nằm trong app của nó; file này chỉ gắn router (backend.md 3.1).
"""

from django.conf import settings
from ninja import NinjaAPI

from accounts.api import router as accounts_router
from accounts.api import users_router
from catalog.api.areas import router as areas_router
from catalog.api.certificates import router as certificates_router
from catalog.api.customers import router as customers_router
from catalog.api.goods_types import router as goods_types_router
from catalog.api.ingredients import router as ingredients_router
from catalog.api.materials import router as materials_router
from catalog.api.prices import router as prices_router
from catalog.api.products import router as products_router
from catalog.api.recipes import router as recipes_router
from catalog.api.settings import router as settings_router
from catalog.api.suppliers import router as suppliers_router
from core.api.images import router as images_router
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
api_v1.add_router("/users", users_router)
api_v1.add_router("/areas", areas_router)
api_v1.add_router("/goods-types", goods_types_router)
api_v1.add_router("/materials", materials_router)
api_v1.add_router("/prices", prices_router)
api_v1.add_router("/suppliers", suppliers_router)
api_v1.add_router("/customers", customers_router)
api_v1.add_router("/certificates", certificates_router)
api_v1.add_router("/settings", settings_router)
api_v1.add_router("/ingredients", ingredients_router)
api_v1.add_router("/recipes", recipes_router)
api_v1.add_router("/products", products_router)
api_v1.add_router("/images", images_router)
api_public.add_router("", public_router)
