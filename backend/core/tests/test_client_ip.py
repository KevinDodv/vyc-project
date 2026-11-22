"""Tin `X-Forwarded-For` chỉ khi REMOTE_ADDR thuộc TRUSTED_PROXY_CIDRS (backend.md 5.1)."""

from __future__ import annotations

from typing import Any

import pytest
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, override_settings

from core.clientip import ClientIPMiddleware, get_client_ip, ip_hash, resolve_client_ip

COMPOSE = "172.28.0.0/24"
PROXY = "172.28.0.5"


class TestTrustedProxy:
    @pytest.fixture(autouse=True)
    def _trust_compose_subnet(self, settings: Any) -> None:
        settings.TRUSTED_PROXY_CIDRS = [COMPOSE]

    def test_proxy_trusted_uses_forwarded_ip(self) -> None:
        assert resolve_client_ip(PROXY, "203.0.113.9") == "203.0.113.9"

    def test_walks_right_to_left_and_skips_trusted_hops(self) -> None:
        assert resolve_client_ip(PROXY, "203.0.113.9, 172.28.0.7") == "203.0.113.9"

    def test_client_cannot_spoof_by_prepending(self) -> None:
        # Khách gửi "1.1.1.1" ở đầu: lấy IP ngoài dải bên phải nhất, không phải bên trái.
        assert resolve_client_ip(PROXY, "1.1.1.1, 203.0.113.9") == "203.0.113.9"

    def test_missing_header_gives_none(self) -> None:
        assert resolve_client_ip(PROXY, None) is None
        assert resolve_client_ip(PROXY, "") is None

    def test_all_hops_trusted_gives_none(self) -> None:
        assert resolve_client_ip(PROXY, "172.28.0.9, 172.28.0.7") is None

    def test_garbage_entry_gives_none(self) -> None:
        assert resolve_client_ip(PROXY, "1.1.1.1, not-an-ip") is None

    def test_untrusted_remote_ignores_header(self) -> None:
        assert resolve_client_ip("198.51.100.4", "203.0.113.9") == "198.51.100.4"

    def test_ipv4_mapped_ipv6_is_normalised(self) -> None:
        assert resolve_client_ip(PROXY, "::ffff:203.0.113.9") == "203.0.113.9"

    def test_ipv6_client(self) -> None:
        assert resolve_client_ip(PROXY, "2001:db8::1") == "2001:db8::1"


@override_settings(TRUSTED_PROXY_CIDRS=[])
def test_empty_trusted_list_never_trusts_header() -> None:
    assert resolve_client_ip("172.28.0.5", "203.0.113.9") == "172.28.0.5"
    assert resolve_client_ip("198.51.100.4", "203.0.113.9") == "198.51.100.4"


@override_settings(TRUSTED_PROXY_CIDRS=["127.0.0.1/32", "::1/128"])
def test_dev_loopback_ranges() -> None:
    assert resolve_client_ip("127.0.0.1", "203.0.113.9") == "203.0.113.9"
    assert resolve_client_ip("::1", "203.0.113.9") == "203.0.113.9"


def test_remote_addr_missing_or_invalid_gives_none() -> None:
    assert resolve_client_ip(None, "203.0.113.9") is None
    assert resolve_client_ip("garbage", None) is None


@override_settings(TRUSTED_PROXY_CIDRS=[COMPOSE])
def test_middleware_sets_request_client_ip() -> None:
    seen: list[str | None] = []

    def view(request: HttpRequest) -> HttpResponse:
        seen.append(get_client_ip(request))
        return HttpResponse("ok")

    mw = ClientIPMiddleware(view)
    rf = RequestFactory()
    mw(rf.get("/", REMOTE_ADDR=PROXY, HTTP_X_FORWARDED_FOR="203.0.113.9"))
    mw(rf.get("/", REMOTE_ADDR=PROXY))
    mw(rf.get("/", REMOTE_ADDR="198.51.100.4", HTTP_X_FORWARDED_FOR="203.0.113.9"))
    assert seen == ["203.0.113.9", None, "198.51.100.4"]


@pytest.mark.parametrize("ip", ["203.0.113.9", "2001:db8::1"])
def test_ip_hash_is_stable_and_not_the_ip(ip: str) -> None:
    assert ip_hash(ip) == ip_hash(ip)
    assert ip not in ip_hash(ip)
    assert len(ip_hash(ip)) == 64
