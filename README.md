# Web Log Reports

Учебный web-сервис генерации отчетов на основе журналов web-сервера.
Курсовой проект по дисциплине «Конструирование программного обеспечения».
Автор: Улыбин А. А., группа ПИбд-42, УлГТУ, 2026.

## Что есть сейчас

Минимальный прототип на Python 3.12 и FastAPI: разбор CLF/Combined-записей,
прием пакета строк, базовая статистика, тесты и конфигурация GitHub Actions.
Это основа для лабораторной 5, а не полная реализация курсового проекта.

Планируются Fluent Bit, постоянное хранение и отбор данных, аналитика pandas,
PDF через Jinja2/WeasyPrint, web-интерфейс и Docker Compose.
Связи компонентов описаны в [архитектуре](docs/architecture.md).

## Структура

```text
web-log-project/
  .github/workflows/ci.yml       # проверка, тесты, метрики, сборка
  .githooks/commit-msg           # локальная проверка сообщения
  .github/pull_request_template.md
  src/web_log_reports/
    main.py                     # HTTP API
    parser.py                   # разбор и валидация
    analytics.py                # базовые показатели
  tests/unit/                   # модульные тесты
  tests/integration/            # API + парсер + аналитика
  scripts/check_commits.py
  scripts/collect_metrics.py
  docs/architecture.md
  docs/metrics/README.md         # контрольные точки
  docs/LAB5_GUIDE.md             # пошаговая настройка GitHub
  pyproject.toml
  CHANGELOG.md
```

## Локальный запуск в PowerShell

Из этой папки, при установленном Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -m uvicorn web_log_reports.main:app --reload
```

Если `.venv` уже создана на Python 3.12, достаточно активировать ее и установить
зависимости. Swagger UI: http://127.0.0.1:8000/docs.
В другом окне PowerShell:

```powershell
$body = @{ lines = @('127.0.0.1 - - [12/Nov/2026:10:00:00 +0400] "GET / HTTP/1.1" 200 123') } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/logs -Method Post -ContentType 'application/json' -Body $body
Invoke-RestMethod -Uri http://127.0.0.1:8000/stats
```

`GET /health` возвращает состояние сервиса. Ошибочная строка отклоняет весь
пакет с кодом 400; ошибка структуры запроса возвращает 422.
Хранилище в памяти предназначено для прототипа и одного процесса.
Формат отправки Fluent Bit потребуется согласовать отдельно.

## Проверки и метрики

```powershell
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
New-Item -ItemType Directory -Force reports
python -m pytest --cov=web_log_reports --cov-branch --cov-report=term-missing --cov-report=xml:reports/coverage.xml --cov-report=html:reports/htmlcov --cov-fail-under=80 --junitxml=reports/junit.xml
python scripts/collect_metrics.py
python -m build --no-isolation
```

Исправление форматирования: `python -m ruff format src tests scripts`.
Проверка импорта/стиля: `python -m ruff check --fix src tests scripts`, затем
просмотреть diff. Не применять исправления без проверки изменений.

В `reports/metrics.json` собираются: число замечаний линтера, средняя и
максимальная цикломатическая сложность, покрытие строк и ветвей, число
успешных и неуспешных тестов, ошибки и пропуски тестов, время их выполнения.
Здесь «замечание линтера» не означает подтвержденный дефект программы.
Порог pytest-cov 80% относится к совокупному покрытию строк и ветвей.
Отдельные проценты строк и ветвей берутся из Coverage XML.

## Управление кодом

- `main` — проверенное состояние проекта; изменения через Pull Request.
- `feature/<задача>`, `fix/<ошибка>`, `docs/<документация>` — короткие ветки.
- Сообщение: `тип(область): описание`, например `feat(parser): parse access logs`.
- Допустимые типы: feat, fix, docs, style, refactor, perf, test, build, ci,
  chore, revert. Область необязательна. Заголовок — до 100 символов.
- Локальный hook: `git config core.hooksPath .githooks` после `git init`.
  В Linux/macOS дополнительно `chmod +x .githooks/commit-msg`.
- Merge-коммиты GitHub исключены из проверки. Squash для учебного процесса
  отключен, чтобы сохранить проверенные сообщения отдельных коммитов.
- CI повторяет проверку коммитов независимо от наличия hook у разработчика.
- Релиз — аннотированный тег `v0.1.0` и запись GitHub Release после зеленого CI.

Публикация проекта и защита `main` выполняются по [инструкции](docs/LAB5_GUIDE.md).
Текст для отчёта по GitHub находится в [материалах лабораторной 5](docs/LAB5_REPORT.md).

## План следующего этапа
1.	Выбрать из списка задач несколько для формирования прототипа. Определить цель создания прототипа.
2.	Реализовать. Реализация задач может быть неполной. 
3.	Сделать выводы по планам проекта, т. к. целью создания прототипа является как уточнение задач по проекту с преподавателем, так и оценка собственных возможностей по работе над проектом с учетом используемых технологий, оценок задач.
