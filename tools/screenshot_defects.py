"""Скрипт для создания скриншотов к баг-репортам.

Запуск из корня репозитория:
    python tools/screenshot_defects.py

Результат сохраняется в папку screenshots/.
"""
from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)

sys.path.insert(0, str(ROOT))
from tests.pages.transfer_page import TransferPage  # noqa: E402


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait(url: str) -> None:
    end = time.monotonic() + 10
    while time.monotonic() < end:
        try:
            urlopen(url, timeout=1.0).read()
            return
        except URLError:
            time.sleep(0.2)
    raise RuntimeError(f"Сервер не отвечает: {url}")


def _chrome() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,1024")
    return webdriver.Chrome(options=opts)


def main() -> int:
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=str(DIST),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        _wait(base + "/")
        drv = _chrome()
        try:
            p = TransferPage(drv, base_url=base)

            # Главная страница
            p.open().driver.save_screenshot(str(OUT / "main_screen.png"))
            time.sleep(0.3)

            # D-01: 17 цифр в номере карты
            p.open().select_rub_account().type_card_number("12345678901234567")
            time.sleep(0.3)
            drv.save_screenshot(str(OUT / "defect_01_card.png"))

            # D-02: отрицательная сумма
            p.open().select_rub_account().type_card_number("1111222233334444").type_amount("-100")
            time.sleep(0.3)
            drv.save_screenshot(str(OUT / "defect_02_minus.png"))

            # D-03: граница остатка
            p.open(balance=110, reserved=0).select_rub_account()
            p.type_card_number("1111222233334444").type_amount("100")
            time.sleep(0.3)
            drv.save_screenshot(str(OUT / "defect_03_limit.png"))

            # D-04: неверная комиссия
            p.open(balance=30000, reserved=0).select_rub_account()
            p.type_card_number("1111222233334444").type_amount("99")
            time.sleep(0.3)
            drv.save_screenshot(str(OUT / "defect_04_fee.png"))

            print(f"Скриншоты сохранены в {OUT}")
            return 0
        finally:
            drv.quit()
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
