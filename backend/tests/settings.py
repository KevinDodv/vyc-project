"""Settings cho pytest: ENVIRONMENT=dev rồi nạp config.settings.

config.settings mặc định ENVIRONMENT=prod (fail-safe) nên test phải tự đặt dev trước khi nạp.
pytest-django nạp settings trước conftest.py, vì vậy việc đặt biến nằm ở module này.
"""

import os

os.environ.setdefault("ENVIRONMENT", "dev")

from config.settings import *  # noqa: F403
