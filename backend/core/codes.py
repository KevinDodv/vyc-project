"""Mã nghiệp vụ theo BR-20: số thứ tự lấy từ `code_counter` có khoá hàng, không dùng MAX()+1."""

from __future__ import annotations

from datetime import date

from django.db import connection

from core.timeutil import period_yymm, period_yymmdd

# Kỳ đếm của các mã không đếm lại (khách hàng).
NO_PERIOD = "-"


def next_no(prefix: str, period: str) -> int:
    """Cấp số kế tiếp của (prefix, period). Phải gọi trong `transaction.atomic` của service.

    Khoá hàng giữ tới khi giao dịch nghiệp vụ commit; rollback thì số cũng trả lại.
    """
    if not connection.in_atomic_block:
        raise RuntimeError("core.codes.next_no phải chạy trong transaction.atomic")
    with connection.cursor() as cur:
        cur.execute(
            """INSERT INTO code_counter (prefix, period, last_no, created_at, updated_at)
               VALUES (%s, %s, 1, now(), now())
               ON CONFLICT (prefix, period)
               DO UPDATE SET last_no = code_counter.last_no + 1, updated_at = now()
               RETURNING last_no""",
            [prefix, period],
        )
        row = cur.fetchone()
    if row is None:
        raise RuntimeError("INSERT ... RETURNING không trả dòng nào")
    return int(row[0])


def format_code(head: str, period: str, no: int, width: int) -> str:
    """`PN-261120-001`. Số vượt độ rộng thì tự dài ra (NN hết 99 sang NNN, BR-20)."""
    return f"{head}-{period}-{no:0{width}d}"


def _daily(prefix: str, d: date, width: int) -> str:
    period = period_yymmdd(d)
    return format_code(prefix, period, next_no(prefix, period), width)


def _monthly(prefix: str, d: date, width: int) -> str:
    period = period_yymm(d)
    return format_code(prefix, period, next_no(prefix, period), width)


def receipt_code(d: date) -> str:
    """Phiếu nhập: PN-YYMMDD-NNN, đếm lại theo ngày."""
    return _daily("PN", d, 3)


def issue_code(d: date) -> str:
    """Phiếu xuất: PX-YYMMDD-NNN, đếm lại theo ngày."""
    return _daily("PX", d, 3)


def ingredient_receipt_code(d: date) -> str:
    """Phiếu nhập phụ liệu: PNP-YYMMDD-NNN, đếm lại theo ngày."""
    return _daily("PNP", d, 3)


def material_lot_code(d: date) -> str:
    """Lô nguyên liệu: NL-YYMM-NNNN, đếm lại theo tháng."""
    return _monthly("NL", d, 4)


def production_order_code(d: date) -> str:
    """Lệnh sản xuất: LSX-YYMM-NNN, đếm lại theo tháng."""
    return _monthly("LSX", d, 3)


def scent_trial_code(d: date) -> str:
    """Đợt thử lưu hương: TL-YYMM-NN, đếm lại theo tháng."""
    return _monthly("TL", d, 2)


def label_roll_code(d: date) -> str:
    """Cuộn tem: CT-YYMM-NN, đếm lại theo tháng."""
    return _monthly("CT", d, 2)


def product_lot_code(formula_or_sku: str, d: date) -> str:
    """Lô thành phẩm (= mã mẻ): <mã công thức hoặc SKU>-YYMMDD-NN, đếm theo ngày pha + mã."""
    return _daily(formula_or_sku, d, 2)


def ingredient_lot_code(ingredient_code: str, d: date) -> str:
    """Lô phụ liệu và bán thành phẩm: <mã phụ liệu>-YYMM-NN, đếm theo tháng + mã phụ liệu."""
    return _monthly(ingredient_code, d, 2)


def supplier_code(area_code: str) -> str:
    """Người bán: NCC-<mã xã>-NNN, đếm theo xã."""
    return format_code("NCC", area_code, next_no("NCC", area_code), 3)


def plot_code(area_code: str, supplier_no: int | str) -> str:
    """Đồi quế: D-<mã xã>-<số NCC>-NN, đếm theo người bán."""
    period = f"{area_code}-{supplier_no}"
    return f"D-{period}-{next_no('D', period):02d}"


def customer_code() -> str:
    """Khách hàng: KH-NNNN, không đếm lại."""
    return f"KH-{next_no('KH', NO_PERIOD):04d}"
