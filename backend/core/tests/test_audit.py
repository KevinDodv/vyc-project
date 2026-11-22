"""audit.snapshot / audit.record và CHECK của audit_log.action."""

from __future__ import annotations

from typing import Any

import pytest
from django.db import IntegrityError, transaction

from core import audit
from core.models import AuditAction, AuditLog, CodeCounter

pytestmark = pytest.mark.django_db


def test_snapshot_jsonifies_and_hides_password(owner: Any) -> None:
    snap = audit.snapshot(owner)
    assert snap["username"] == "owner"
    assert snap["role"] == "OWNER"
    assert "password" not in snap
    assert audit.snapshot(owner, ["username"]) == {"username": "owner"}


def test_record_update_snapshots_before_and_after(owner: Any) -> None:
    before = audit.snapshot(CodeCounter(prefix="PN", period="261120", last_no=3))
    counter = CodeCounter.objects.create(prefix="PN", period="261120", last_no=4)
    log = audit.record(owner, counter, "UPDATE", before=before, reason="thử")
    assert log.entity == "code_counter"
    assert log.entity_id == counter.pk
    assert log.before is not None
    assert log.before["last_no"] == 3
    assert log.after is not None
    assert log.after["last_no"] == 4
    assert log.reason == "thử"
    assert log.user_id == owner.pk


def test_delete_line_has_null_after(owner: Any) -> None:
    counter = CodeCounter.objects.create(prefix="PN", period="261120", last_no=4)
    log = audit.record(owner, counter, AuditAction.DELETE_LINE)
    assert log.after is None
    assert log.before is not None
    assert log.before["last_no"] == 4


@pytest.mark.parametrize("action", ["REVEAL", "EXPORT", "ANONYMIZE", "DELETE_LINE"])
def test_extra_actions_are_accepted_by_check_constraint(owner: Any, action: str) -> None:
    counter = CodeCounter.objects.create(prefix="PN", period="261120", last_no=1)
    assert audit.record(owner, counter, action).action == action


def test_db_rejects_unknown_action(owner: Any) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        AuditLog.objects.create(entity="x", entity_id=1, action="HACK", user_id=owner.pk)
