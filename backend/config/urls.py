from django.conf import settings
from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.urls import URLPattern, URLResolver, path
from django.views.decorators.http import require_GET
from django.views.static import serve

from config.api import api_public, api_v1


@require_GET
def health(request: HttpRequest) -> JsonResponse:
    """Healthcheck và smoke test: không auth, không throttle, có chạm DB."""
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
    except Exception:
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})


handler404 = "core.handlers.not_found"


def media_urlpatterns() -> list[URLPattern]:
    """`/media/` do Django phục vụ khi DEBUG (máy dev). Staging, prod: Caddy đọc thẳng volume."""
    if not settings.DEBUG:
        return []
    prefix = settings.MEDIA_URL.lstrip("/")
    return [path(f"{prefix}<path:path>", serve, {"document_root": settings.MEDIA_ROOT})]


urlpatterns: list[URLPattern | URLResolver] = [
    path("api/health", health),
    path("api/v1/", api_v1.urls),
    path("api/public/", api_public.urls),
    *media_urlpatterns(),
]
