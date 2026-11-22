from typing import Any

from django.core.management.base import BaseCommand

from core import throttle


class Command(BaseCommand):
    help = "Xoá các dòng throttle_hit cũ hơn 1 ngày (chạy bằng cron hằng đêm)."

    def handle(self, *args: Any, **options: Any) -> None:
        deleted = throttle.purge()
        self.stdout.write(f"Đã xoá {deleted} dòng throttle_hit")
