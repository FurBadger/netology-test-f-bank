# Тестирование F-Bank

Итоговая работа по дисциплине **«Тестирование прикладного ПО»** (преподаватель — Филипп Воронов).

В репозитории — результаты тестирования учебного банковского сервиса F-Bank: ручные тест-кейсы, баг-репорты, автотесты на Selenium и настройка GitHub Actions. В приложении есть заложенные дефекты, поэтому часть автотестов не проходит — CI-сборка намеренно красная.

## Быстрый старт

```
# 1. Запустить сервис
cd dist
python -m http.server 8000

# 2. Установить зависимости и запустить тесты (из корня репозитория)
pip install -r requirements.txt
python -m pytest
```

Открыть в браузере: `http://localhost:8000/?balance=30000&reserved=20001`

Дополнительные команды:

| Команда | Назначение |
|---|---|
| `python -m pytest -m basic` | только базовые тесты (проходят) |
| `python -m pytest -m defect` | тесты на найденные дефекты (падают) |
| `SHOW_BROWSER=1 python -m pytest` | запуск с видимым окном браузера |
| `APP_BASE_URL=http://127.0.0.1:8000 python -m pytest` | тесты против уже запущенного сервиса |

## Структура репозитория

```
test-f-bank/
├── dist/                          # приложение из dist.zip
├── docs/
│   ├── qa_plan.md                 # план тестирования
│   ├── coverage_matrix.md         # эквивалентные классы и граничные значения
│   ├── smoke_checklist.md         # чек-лист ручного прогона
│   ├── manual_tests/cases.md      # 5 тест-кейсов
│   └── defects/                   # баг-репорты
├── tests/
│   ├── pages/transfer_page.py     # Page Object
│   ├── test_basic_checks.py       # базовые проверки
│   ├── test_input_rules.py        # дополнительные сценарии
│   └── test_defect_*.py           # автотесты на дефекты
├── tools/screenshot_defects.py    # скрипт для скриншотов
├── screenshots/
└── .github/workflows/selenium-ci.yml
```

## Найденные дефекты

| ID | Описание | Severity | Автотест |
|---|---|---|---|
| [D-01](docs/defects/defect_01_card_length.md) | Поле «Номер карты» принимает 17 цифр | Major | `test_defect_card_length.py` |
| [D-02](docs/defects/defect_02_negative_sum.md) | Принимается отрицательная сумма перевода | Critical | `test_defect_negative_sum.py` |
| [D-03](docs/defects/defect_03_balance_edge.md) | На границе доступного остатка перевод блокируется | Major | `test_defect_balance_edge.py` |
| [D-04](docs/defects/defect_04_fee_calc.md) | Неверный расчёт комиссии 10% | Major | `test_defect_fee_calc.py` |

По заданию нужно найти минимум 2 дефекта — найдено **4**.

## Ручное тестирование

Описано в [`docs/manual_tests/cases.md`](docs/manual_tests/cases.md): 5 тест-кейсов (TC-01 — TC-05), из них 2 проходят, 3 выявляют дефекты D-01, D-02, D-03.

## CI / GitHub Actions

Файл [`.github/workflows/selenium-ci.yml`](.github/workflows/selenium-ci.yml) запускает автотесты при push и pull request. Ожидаемый результат прогона: **8 failed, 12 passed** (всего 20 тестов).

## Используемые инструменты

Python 3.10+, pytest, Selenium 4.27, Google Chrome, GitHub Actions.
