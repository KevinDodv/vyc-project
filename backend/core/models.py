"""Model dùng chung: TimeStampedModel, AuditLog, Setting, CodeCounter, ThrottleHit."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditAction(models.TextChoices):
    CREATE = "CREATE", "Tạo"
    UPDATE = "UPDATE", "Sửa"
    CANCEL = "CANCEL", "Huỷ"
    RECALL = "RECALL", "Thu hồi"
    VOID = "VOID", "Vô hiệu"
    REVEAL = "REVEAL", "Xem đầy đủ"
    EXPORT = "EXPORT", "Xuất dữ liệu"
    ANONYMIZE = "ANONYMIZE", "Xoá thông tin người mua"
    DELETE_LINE = "DELETE_LINE", "Bỏ dòng"


class AuditLog(models.Model):
    entity = models.TextField()
    entity_id = models.BigIntegerField()
    action = models.TextField(choices=AuditAction.choices)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)  # noqa: DJ001
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "audit_log"
        constraints = [
            models.CheckConstraint(
                condition=Q(action__in=AuditAction.values), name="audit_log_action_valid"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.entity}#{self.entity_id}"


class Setting(models.Model):
    key = models.TextField(primary_key=True)
    value = models.JSONField()

    class Meta:
        db_table = "setting"

    def __str__(self) -> str:
        return self.key


class CodeCounter(TimeStampedModel):
    """Bộ đếm mã nghiệp vụ (BR-20). Khoá hàng khi cấp số (`core.codes.next_no`)."""

    prefix = models.TextField()
    period = models.TextField()
    last_no = models.IntegerField(default=0)

    class Meta:
        db_table = "code_counter"
        constraints = [
            models.UniqueConstraint(fields=["prefix", "period"], name="code_counter_prefix_period"),
        ]

    def __str__(self) -> str:
        return f"{self.prefix}/{self.period}={self.last_no}"


class ThrottleHit(models.Model):
    """Số lần gọi trong từng phút của một khoá (backend.md 5.2)."""

    key = models.TextField()
    window_start = models.DateTimeField()
    hits = models.IntegerField()

    class Meta:
        db_table = "throttle_hit"
        constraints = [
            models.UniqueConstraint(fields=["key", "window_start"], name="throttle_hit_key_window"),
        ]

    def __str__(self) -> str:
        return f"{self.key} {self.window_start:%H:%M} x{self.hits}"
