from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.urls import path
from django.views.decorators.http import require_GET

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

urlpatterns = [
    path("api/health", health),
    path("api/v1/", api_v1.urls),
    path("api/public/", api_public.urls),
]
