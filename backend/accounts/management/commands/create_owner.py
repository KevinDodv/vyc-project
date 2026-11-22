"""`manage.py create_owner --username <tên>`: tạo tài khoản OWNER đầu tiên (backend.md 4.1).

Mật khẩu lấy từ biến môi trường (mặc định `OWNER_PASSWORD`, đổi tên bằng `--password-env`) hoặc
nhập tay hai lần. Không có tham số `--password` để mật khẩu không vào lịch sử shell hay `ps`.
"""

from __future__ import annotations

import getpass
import os
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from accounts.models import User
from core.roles import Role

MIN_PASSWORD_LENGTH = 8  # TK mục 4: mật khẩu >= 8 ký tự


class Command(BaseCommand):
    help = "Tạo tài khoản OWNER (chủ doanh nghiệp). Mật khẩu nhập tay hoặc lấy từ biến môi trường."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--username", required=True)
        parser.add_argument("--full-name", default="Chủ doanh nghiệp")
        parser.add_argument(
            "--password-env",
            default="OWNER_PASSWORD",
            help="Tên biến môi trường chứa mật khẩu (mặc định OWNER_PASSWORD); không có thì hỏi.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        username = str(options["username"]).strip()
        if not username or len(username) > 150:
            raise CommandError("username phải từ 1 đến 150 ký tự")
        if User.objects.filter(username=username).exists():
            raise CommandError(f"Tài khoản «{username}» đã tồn tại")

        password = os.environ.get(options["password_env"]) or self._prompt()
        if len(password) < MIN_PASSWORD_LENGTH:
            raise CommandError(f"Mật khẩu phải từ {MIN_PASSWORD_LENGTH} ký tự")

        User.objects.create_user(
            username, password, full_name=options["full_name"], role=Role.OWNER
        )
        self.stdout.write(self.style.SUCCESS(f"Đã tạo tài khoản OWNER «{username}»"))

    def _prompt(self) -> str:
        password = getpass.getpass("Mật khẩu: ")
        if password != getpass.getpass("Nhập lại mật khẩu: "):
            raise CommandError("Hai lần nhập mật khẩu không khớp")
        return password
