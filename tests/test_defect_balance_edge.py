"""Автотесты для дефекта D-03 — перевод блокируется на границе остатка.

Связанный тест-кейс: TC-05.
Баг-репорт: docs/defects/defect_03_balance_edge.md
"""
import pytest

from tests.pages.transfer_page import TransferPage


@pytest.mark.defect
@pytest.mark.rub
def test_exact_limit_allows_transfer(page: TransferPage):
    """Если сумма с комиссией равна остатку — перевод должен быть разрешён."""
    page.open(balance=110, reserved=0)
    page.select_rub_account()
    page.type_card_number("1111222233334444")
    page.type_amount("100")

    assert page.fee_text() == "10"
    assert page.submit_visible(), (
        "При сумме 100 ₽ и комиссии 10 ₽ (итого 110) перевод должен быть доступен. См. D-03."
    )
    assert not page.no_funds_visible()
