"""Log JSON một dòng và gửi 5xx về webhook (backend.md 7.4).

Trường: ts, level, logger, msg, request_id, user_id. Không log cookie, mật khẩu, IP gốc, số điện
thoại người mua: chỉ truyền vào `extra` những thứ an toàn.
"""

from __future__ import annotations

import contextlib
import json
import logging
import threading
import urllib.request
from datetime import UTC, datetime
from typing import Any

from django.conf import settings

# Trường LogRecord mặc định, không chép vào JSON.
_RESERVED = frozenset(vars(logging.makeLogRecord({}))) | {
    "message",
    "asctime",
    "taskName",
    "request",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", None),
        }
        for key, value in vars(record).items():
            if key not in _RESERVED and key not in payload and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class WebhookHandler(logging.Handler):
    """Gửi bản ghi ERROR về `ERROR_WEBHOOK_URL` (tắt khi biến trống). Không bao giờ raise."""

    def emit(self, record: logging.LogRecord) -> None:
        url = getattr(settings, "ERROR_WEBHOOK_URL", "")
        if not url.startswith("https://"):
            return
        try:
            text = f"[{settings.ENVIRONMENT}] {record.name}: {record.getMessage()}"
            body = json.dumps({"text": text[:1800]}).encode()
            threading.Thread(target=self._post, args=(url, body), daemon=True).start()
        except Exception:
            self.handleError(record)

    @staticmethod
    def _post(url: str, body: bytes) -> None:
        req = urllib.request.Request(  # noqa: S310
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        with contextlib.suppress(OSError):
            urllib.request.urlopen(req, timeout=5).close()  # noqa: S310
