"""Автотесты для дефекта D-01 — поле «Номер карты» принимает 17 цифр.

Связанный тест-кейс: TC-03.
Баг-репорт: docs/defects/defect_01_card_length.md
"""
import pytest

from tests.pages.transfer_page import TransferPage


@pytest.mark.defect
@pytest.mark.rub
def test_card_accepts_only_16_digits(page: TransferPage):
    """Номер карты должен содержать не больше 16 цифр."""
    page.select_rub_account()
    page.type_card_number("12345678901234567")
    digits = "".join(c for c in page.card_value() if c.isdigit())
    assert len(digits) == 16, (
        f"В поле сохранилось {len(digits)} цифр вместо 16. См. D-01."
    )


@pytest.mark.defect
@pytest.mark.rub
def test_amount_form_hidden_for_long_card(page: TransferPage):
    """Форма суммы не должна открываться при 17-значном номере."""
    page.select_rub_account()
    page.type_card_number("12345678901234567")
    stored = "".join(c for c in page.card_value() if c.isdigit())
    if len(stored) == 17:
        assert not page.amount_section_visible(), (
            "Форма «Сумма перевода» открыта для 17 цифр. См. D-01."
        )
