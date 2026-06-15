"""Базовые автотесты — проверяют, что сервис работает и основные сценарии проходят.

Эти тесты должны быть зелёными. Если они падают — проблема в окружении, а не в приложении.
"""
import pytest

from tests.pages.transfer_page import TransferPage


@pytest.mark.basic
def test_main_page_lists_three_currencies(page: TransferPage):
    """На главной отображаются три счёта: рубли, доллары, евро."""
    assert page.rub_balance() == "30'000"
    assert page.rub_reserved() == "20'001"
    drv = page.driver
    assert drv.find_element(*TransferPage.USD_BALANCE).text.strip() == "100"
    assert drv.find_element(*TransferPage.EURO_BALANCE).text.strip() == "300"


@pytest.mark.basic
@pytest.mark.rub
def test_successful_transfer_shows_alert(page: TransferPage):
    """Успешный перевод: карта → сумма → кнопка → сообщение о принятии."""
    page.select_rub_account()
    page.type_card_number("1111222233334444")
    page.type_amount("100")

    assert page.fee_text() == "10"
    assert page.submit_visible()
    assert not page.no_funds_visible()

    page.submit_transfer()
    alert = page.dismiss_alert()
    assert "100" in alert
    assert "1111222233334444" in alert
    assert "принят банком" in alert


@pytest.mark.basic
@pytest.mark.rub
def test_oversized_amount_blocks_transfer(page: TransferPage):
    """При сумме больше доступного остатка перевод блокируется."""
    page.select_rub_account()
    page.type_card_number("1111222233334444")
    page.type_amount("100000")

    assert page.no_funds_visible()
    assert not page.submit_visible()
