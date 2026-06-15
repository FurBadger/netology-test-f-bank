"""Page Object — описание элементов страницы F-Bank.

Все обращения к странице собраны здесь, чтобы тесты оставались читаемыми.
При изменении вёрстки правится только этот файл.
"""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TransferPage:
    """Страница перевода F-Bank."""

    # Счета на главной
    RUB_BALANCE = (By.ID, "rub-sum")
    RUB_RESERVED = (By.ID, "rub-reserved")
    USD_BALANCE = (By.ID, "usd-sum")
    EURO_BALANCE = (By.ID, "euro-sum")

    # Форма перевода
    RUB_CARD = (By.XPATH, "//h2[normalize-space(text())='Рубли']/ancestor::button[1]")
    CARD_INPUT = (By.XPATH, "//input[@placeholder='0000 0000 0000 0000']")
    AMOUNT_INPUT = (By.XPATH, "//input[@placeholder='1000']")
    FEE_VALUE = (By.ID, "comission")  # опечатка в id — как в приложении
    SUBMIT_BTN = (By.XPATH, "//button[.//span[normalize-space(text())='Перевести']]")
    NO_FUNDS_MSG = (By.XPATH, "//*[contains(normalize-space(text()),'Недостаточно средств на счете')]")
    AMOUNT_SECTION = (By.XPATH, "//h3[normalize-space(text())='Сумма перевода:']")

    WAIT_SEC = 5

    def __init__(self, driver: WebDriver, base_url: str = "http://localhost:8000"):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, self.WAIT_SEC)

    def open(self, balance: int | str = 30000, reserved: int | str = 20001) -> "TransferPage":
        """Открывает страницу с заданным балансом и резервом."""
        self.driver.get(f"{self.base_url}/?balance={balance}&reserved={reserved}")
        self.wait.until(EC.presence_of_element_located(self.RUB_BALANCE))
        return self

    def select_rub_account(self) -> "TransferPage":
        """Нажимает на карточку рублёвого счёта."""
        try:
            self.wait.until(EC.element_to_be_clickable(self.RUB_CARD)).click()
        except Exception:
            fallback = (
                By.XPATH,
                "//h2[normalize-space(text())='Рубли']"
                "/ancestor::*[contains(@class,'g-button') or self::button or self::div][1]",
            )
            self.wait.until(EC.element_to_be_clickable(fallback)).click()
        self.wait.until(EC.visibility_of_element_located(self.CARD_INPUT))
        return self

    def type_card_number(self, value: str) -> "TransferPage":
        """Вводит номер карты."""
        field = self.wait.until(EC.visibility_of_element_located(self.CARD_INPUT))
        field.click()
        field.send_keys(Keys.CONTROL, "a", Keys.DELETE)
        field.send_keys(value)
        return self

    def type_amount(self, value: str) -> "TransferPage":
        """Вводит сумму перевода."""
        field = self.wait.until(EC.visibility_of_element_located(self.AMOUNT_INPUT))
        field.click()
        field.send_keys(Keys.CONTROL, "a", Keys.DELETE)
        field.send_keys(value)
        return self

    def submit_transfer(self) -> "TransferPage":
        """Нажимает кнопку «Перевести»."""
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BTN)).click()
        return self

    def dismiss_alert(self) -> str:
        """Закрывает alert и возвращает его текст."""
        WebDriverWait(self.driver, self.WAIT_SEC).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        text = alert.text
        alert.accept()
        return text

    def card_value(self) -> str:
        return self.driver.find_element(*self.CARD_INPUT).get_attribute("value") or ""

    def amount_value(self) -> str:
        return self.driver.find_element(*self.AMOUNT_INPUT).get_attribute("value") or ""

    def fee_text(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.FEE_VALUE)).text.strip()

    def rub_balance(self) -> str:
        return self.driver.find_element(*self.RUB_BALANCE).text.strip()

    def rub_reserved(self) -> str:
        return self.driver.find_element(*self.RUB_RESERVED).text.strip()

    def amount_section_visible(self) -> bool:
        try:
            return self.driver.find_element(*self.AMOUNT_SECTION).is_displayed()
        except Exception:
            return False

    def submit_visible(self) -> bool:
        try:
            return self.driver.find_element(*self.SUBMIT_BTN).is_displayed()
        except Exception:
            return False

    def no_funds_visible(self) -> bool:
        try:
            return self.driver.find_element(*self.NO_FUNDS_MSG).is_displayed()
        except Exception:
            return False
