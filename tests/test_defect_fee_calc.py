"""Автотесты для дефекта D-04 — неверный расчёт комиссии 10%.

Баг-репорт: docs/defects/defect_04_fee_calc.md
"""
import math

import pytest

from tests.pages.transfer_page import TransferPage


@pytest.mark.defect
@pytest.mark.rub
@pytest.mark.parametrize(
    "amount, expected_fee",
    [
        ("99", "9"),
        ("110", "11"),
        ("999", "99"),
    ],
)
def test_fee_equals_ten_percent_rounded_down(page: TransferPage, amount: str, expected_fee: str):
    """Комиссия = 10% от суммы, округление вниз."""
    page.select_rub_account()
    page.type_card_number("1111222233334444")
    page.type_amount(amount)

    actual = page.fee_text()
    expected = math.floor(int(amount) * 0.1)
    assert actual == expected_fee, (
        f"Для суммы {amount} ₽ комиссия {actual} ₽, ожидалось {expected_fee} ₽. См. D-04."
    )
