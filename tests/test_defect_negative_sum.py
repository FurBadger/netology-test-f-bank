"""Автотесты для дефекта D-02 — принимается отрицательная сумма.

Связанный тест-кейс: TC-04.
Баг-репорт: docs/defects/defect_02_negative_sum.md
"""
import pytest

from tests.pages.transfer_page import TransferPage


@pytest.mark.defect
@pytest.mark.rub
def test_negative_sum_hides_submit_button(page: TransferPage):
    """Кнопка «Перевести» не должна появляться для отрицательной суммы."""
    page.select_rub_account()
    page.type_card_number("1111222233334444")
    page.type_amount("-100")
    if page.amount_value().startswith("-"):
        assert not page.submit_visible(), (
            "Перевод -100 ₽ доступен — это недопустимо. См. D-02."
        )


@pytest.mark.defect
@pytest.mark.rub
def test_minus_sign_removed_from_amount(page: TransferPage):
    """Знак минус должен отбрасываться при вводе суммы."""
    page.select_rub_account()
    page.type_card_number("1111222233334444")
    page.type_amount("-100")
    assert not page.amount_value().startswith("-"), (
        f"В поле осталось значение «{page.amount_value()}». См. D-02."
    )
