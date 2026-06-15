"""Дополнительные сценарии: правила ввода и граничные значения.

Не привязаны к конкретным дефектам — проверяют ожидаемое поведение приложения.
"""
import pytest

from tests.pages.transfer_page import TransferPage


@pytest.mark.basic
@pytest.mark.rub
def test_card_field_strips_letters(page: TransferPage):
    """В поле карты остаются только цифры."""
    page.select_rub_account()
    page.type_card_number("abcd1234EFGH5678!@#$9012()*&3456")
    digits = "".join(c for c in page.card_value() if c.isdigit())
    assert digits == "1234567890123456"


@pytest.mark.basic
@pytest.mark.rub
def test_card_field_adds_spaces(page: TransferPage):
    """Цифры номера карты разделяются пробелами по 4."""
    page.select_rub_account()
    page.type_card_number("1234567890123456")
    assert page.card_value() == "1234 5678 9012 3456"


@pytest.mark.basic
@pytest.mark.rub
def test_amount_hidden_for_15_digit_card(page: TransferPage):
    """При 15 цифрах форма суммы не показывается."""
    page.select_rub_account()
    page.type_card_number("123456789012345")
    assert not page.amount_section_visible()


@pytest.mark.basic
@pytest.mark.rub
def test_amount_shown_for_16_digit_card(page: TransferPage):
    """При ровно 16 цифрах форма суммы появляется."""
    page.select_rub_account()
    page.type_card_number("1234567890123456")
    assert page.amount_section_visible()


@pytest.mark.basic
@pytest.mark.rub
def test_transfer_ok_when_total_below_limit(page: TransferPage):
    """Сумма с комиссией меньше остатка — перевод разрешён."""
    page.open(balance=110, reserved=0)
    page.select_rub_account()
    page.type_card_number("1111222233334444")
    page.type_amount("99")
    assert page.submit_visible()
    assert not page.no_funds_visible()


@pytest.mark.basic
@pytest.mark.rub
def test_transfer_blocked_when_total_above_limit(page: TransferPage):
    """Сумма с комиссией больше остатка — перевод запрещён."""
    page.open(balance=110, reserved=0)
    page.select_rub_account()
    page.type_card_number("1111222233334444")
    page.type_amount("101")
    assert page.no_funds_visible()
    assert not page.submit_visible()


@pytest.mark.basic
@pytest.mark.rub
def test_large_balance_has_apostrophe_separator(page: TransferPage):
    """Большие суммы отображаются с разделителем тысяч."""
    page.open(balance=1234567, reserved=0)
    assert page.rub_balance() == "1'234'567"


@pytest.mark.basic
@pytest.mark.rub
def test_zero_balance_display(page: TransferPage):
    """Нулевой баланс отображается корректно."""
    page.open(balance=0, reserved=0)
    assert page.rub_balance() == "0"
    assert page.rub_reserved() == "0"


@pytest.mark.basic
@pytest.mark.rub
def test_rub_card_opens_transfer_form(page: TransferPage):
    """Клик по «Рубли» открывает форму перевода."""
    page.select_rub_account()
    assert page.driver.find_elements(*TransferPage.CARD_INPUT)
    assert not page.amount_section_visible()
