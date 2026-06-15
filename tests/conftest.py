"""Настройка окружения для автотестов.

Фикстуры:
- live_server — запускает python -m http.server в папке dist
- browser — headless Chrome на всю сессию
- page — открытая страница F-Bank с параметрами по умолчанию

Если задана переменная APP_BASE_URL — используется уже запущенный сервис (как в CI).
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.error import URLError
from urllib.request import urlopen

from tests.pages.transfer_page import TransferPage

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"


def _pick_free_port() -> int:
    """Находит свободный порт на localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_server(url: str, timeout: float = 15.0) -> None:
    """Ждёт, пока сервер начнёт отвечать."""
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1.0) as response:
                if response.status < 500:
                    return
        except (URLError, Exception) as exc:
            last_error = exc
        time.sleep(0.2)
    raise RuntimeError(f"Сервер не ответил на {url}: {last_error}")


@pytest.fixture(scope="session")
def app_url() -> str:
    """Адрес уже запущенного сервиса (для CI)."""
    return os.environ.get("APP_BASE_URL", "").rstrip("/")


@pytest.fixture(scope="session")
def live_server(app_url: str) -> Iterator[str]:
    """Поднимает сервис из папки dist или использует APP_BASE_URL."""
    if app_url:
        _wait_server(app_url)
        yield app_url
        return

    if not DIST_DIR.is_dir():
        raise RuntimeError(f"Папка dist не найдена: {DIST_DIR}")

    port = _pick_free_port()
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=str(DIST_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        _wait_server(url + "/")
        yield url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture(scope="session")
def browser() -> Iterator[webdriver.Chrome]:
    """Браузер Chrome для всех тестов сессии."""
    options = Options()
    # SHOW_BROWSER=1 — показать окно браузера при отладке
    if os.environ.get("SHOW_BROWSER", "0") not in ("1", "true", "True"):
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1024")

    chrome_path = os.environ.get("CHROME_BIN")
    if chrome_path:
        options.binary_location = chrome_path

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(20)
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def page(browser: webdriver.Chrome, live_server: str) -> TransferPage:
    """Страница F-Bank с balance=30000, reserved=20001."""
    return TransferPage(browser, base_url=live_server).open()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Сохраняет скриншот при падении теста."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    driver = item.funcargs.get("browser")
    if driver is None:
        return

    folder = ROOT / "screenshots"
    folder.mkdir(exist_ok=True)
    path = folder / f"FAIL__{item.name}.png"
    try:
        driver.save_screenshot(str(path))
        print(f"\n[скриншот] {path}")
    except Exception as exc:
        print(f"\n[ошибка скриншота] {exc}")
