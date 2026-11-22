"""IP thật của khách (backend.md 5.1). Chỉ dùng trong bộ nhớ để throttle và băm, không lưu."""

from __future__ import annotations

import hashlib
import ipaddress
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse

IPAddress = ipaddress.IPv4Address | ipaddress.IPv6Address
Network = ipaddress.IPv4Network | ipaddress.IPv6Network


def _parse_ip(raw: str) -> IPAddress | None:
    try:
        ip = ipaddress.ip_address(raw.strip())
    except ValueError:
        return None
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        return ip.ipv4_mapped
    return ip


def trusted_networks() -> list[Network]:
    return [ipaddress.ip_network(cidr, strict=False) for cidr in settings.TRUSTED_PROXY_CIDRS]


def _in(ip: IPAddress, nets: list[Network]) -> bool:
    return any(ip.version == net.version and ip in net for net in nets)


def resolve_client_ip(remote_addr: str | None, forwarded_for: str | None) -> str | None:
    """Trả IP khách hoặc `None` (chỉ khi request đến từ proxy được tin mà không có IP khách).

    1. `remote_addr` thuộc `TRUSTED_PROXY_CIDRS`: duyệt `X-Forwarded-For` từ phải sang trái, bỏ
       IP thuộc dải, lấy IP đầu tiên ngoài dải. Header trống, có mục không phải IP, hoặc mọi IP
       đều thuộc dải thì `None` (không lấy `remote_addr`: đó là IP của container proxy).
    2. Ngoài dải: bỏ qua header, dùng `remote_addr`.
    """
    remote = _parse_ip(remote_addr) if remote_addr else None
    if remote is None:
        return None
    nets = trusted_networks()
    if not _in(remote, nets):
        return str(remote)
    if not forwarded_for:
        return None
    for part in reversed(forwarded_for.split(",")):
        ip = _parse_ip(part)
        if ip is None:
            return None  # mục rác: không đi tiếp sang trái, phần đó do khách điều khiển
        if not _in(ip, nets):
            return str(ip)
    return None


def ip_hash(ip: str) -> str:
    """sha256(ip + IP_HASH_SALT): khoá throttle và `scan_event.ip_hash`."""
    return hashlib.sha256((ip + settings.IP_HASH_SALT).encode()).hexdigest()


def get_client_ip(request: HttpRequest) -> str | None:
    ip: str | None = getattr(request, "client_ip", None)
    return ip


class ClientIPMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        meta: dict[str, Any] = request.META
        request.client_ip = resolve_client_ip(  # type: ignore[attr-defined]
            meta.get("REMOTE_ADDR"), meta.get("HTTP_X_FORWARDED_FOR")
        )
        return self.get_response(request)
