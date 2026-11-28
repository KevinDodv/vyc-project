"""BR-20: mã nghiệp vụ lấy số từ bảng đếm có khoá hàng, không thủng số, không trùng số."""

from __future__ import annotations

import re
import threading
from datetime import date

import pytest
from django.db import connection, transaction

from core import codes
from core.models import CodeCounter


@pytest.mark.django_db
def test_br20_receipt_code_format_and_sequence() -> None:
    with transaction.atomic():
        assert codes.receipt_code(date(2026, 11, 20)) == "PN-261120-001"
        assert codes.receipt_code(date(2026, 11, 20)) == "PN-261120-002"


@pytest.mark.django_db
def test_br20_counter_restarts_by_period_and_prefix() -> None:
    with transaction.atomic():
        assert codes.receipt_code(date(2026, 11, 20)) == "PN-261120-001"
        assert codes.receipt_code(date(2026, 11, 21)) == "PN-261121-001"  # sang ngày mới
        assert codes.issue_code(date(2026, 11, 20)) == "PX-261120-001"  # tiền tố khác
        assert codes.material_lot_code(date(2026, 11, 20)) == "NL-2611-0001"  # theo tháng
        assert codes.material_lot_code(date(2026, 11, 28)) == "NL-2611-0002"
        assert codes.material_lot_code(date(2026, 12, 1)) == "NL-2612-0001"


@pytest.mark.django_db
def test_br20_code_patterns() -> None:
    d = date(2026, 11, 17)
    with transaction.atomic():
        assert codes.production_order_code(d) == "LSX-2611-001"
        assert codes.product_lot_code("QC1", d) == "QC1-261117-01"
        assert codes.ingredient_lot_code("Q", d) == "Q-2611-01"
        assert codes.ingredient_receipt_code(d) == "PNP-261117-001"
        assert codes.scent_trial_code(d) == "TL-2611-01"
        assert codes.label_roll_code(d) == "CT-2611-01"
        assert codes.supplier_code("CQ") == "NCC-CQ-001"
        assert codes.plot_code("CQ", "012") == "D-CQ-012-01"
        first = codes.customer_code()  # seed 0004 đã đẩy bộ đếm nên không đoán số tuyệt đối
        second = codes.customer_code()
    assert re.fullmatch(r"KH-\d{4,}", first)
    assert re.fullmatch(r"KH-\d{4,}", second)
    assert int(second[3:]) == int(first[3:]) + 1


@pytest.mark.django_db
def test_br20_two_digit_number_grows_to_three_after_99() -> None:
    d = date(2026, 11, 17)
    CodeCounter.objects.create(prefix="QC1", period="261117", last_no=98)
    with transaction.atomic():
        assert codes.product_lot_code("QC1", d) == "QC1-261117-99"
        assert codes.product_lot_code("QC1", d) == "QC1-261117-100"


@pytest.mark.django_db
def test_br20_rollback_returns_the_number() -> None:
    d = date(2026, 11, 20)
    with transaction.atomic():
        assert codes.receipt_code(d) == "PN-261120-001"
    with pytest.raises(RuntimeError), transaction.atomic():
        assert codes.receipt_code(d) == "PN-261120-002"
        raise RuntimeError("nghiệp vụ lỗi sau khi cấp số")
    with transaction.atomic():
        assert codes.receipt_code(d) == "PN-261120-002"  # không thủng số


@pytest.mark.django_db(transaction=True)
def test_br20_next_no_requires_atomic_block() -> None:
    with pytest.raises(RuntimeError, match=r"transaction.atomic"):
        codes.next_no("PN", "261120")


@pytest.mark.django_db(transaction=True)
def test_br20_parallel_transactions_never_duplicate() -> None:
    threads_n, per_thread = 5, 4
    results: list[int] = []
    errors: list[BaseException] = []
    lock = threading.Lock()
    start = threading.Barrier(threads_n)

    def worker() -> None:
        try:
            start.wait()
            for _ in range(per_thread):
                with transaction.atomic():
                    n = codes.next_no("PN", "261120")
                with lock:
                    results.append(n)
        except BaseException as exc:
            errors.append(exc)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker) for _ in range(threads_n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert sorted(results) == list(range(1, threads_n * per_thread + 1))
