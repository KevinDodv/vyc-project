from __future__ import annotations

import pytest
from django.test import Client


@pytest.mark.django_db
def test_health_ok(client: Client) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.django_db
def test_health_rejects_post(client: Client) -> None:
    assert client.post("/api/health").status_code == 405


@pytest.mark.django_db
def test_both_apis_are_mounted_and_default_to_error_shape(
    client: Client, owner_client: Client
) -> None:
    # Stub rỗng nên mọi đường dẫn là 404, nhưng phải đúng hình dạng lỗi của mục 3.2.
    for path in ("/api/v1/nothing", "/api/public/nothing"):
        r = client.get(path)
        assert r.status_code == 404
        assert set(r.json()) == {"code", "message", "details"}
