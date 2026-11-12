# Лабораторная работа 5 на GitHub

Хостинг проекта — **GitHub**, CI — **GitHub Actions**, проверка и слияние изменений — **Pull Request (PR)**.
Тема: web-сервис генерации PDF-отчётов на основе логов web-сервера.
Модель разработки, этапы и стек из лабораторных 3 и 4 сохраняются.

Файлы подготовлены локально. Создание репозитория, защита main, удалённые запуски и Release подтверждаются после выполнения действий на GitHub.

## 1 Создать репозиторий

1. Открыть https://github.com/new.
2. **Owner** — ваш аккаунт; **Repository name** — `web-log-reports`.
3. **Description** — `Web-сервис генерации PDF-отчётов на основе логов web-сервера. Курсовой проект по КПО`.
4. Для защиты ветки на GitHub Free выбрать **Public**. Для Private нужен тариф с этой функцией, например GitHub Pro. Проверить возможности своего аккаунта.
5. **Add README** выключить, **Add .gitignore** и **Choose a license** не выбирать: локальные файлы уже подготовлены.
6. Нажать **Create repository** и скопировать HTTPS-адрес.

Пример адреса: `https://github.com/ВАШ_ЛОГИН/web-log-reports.git`.
Вставлять пароль в URL не нужно; вход выполняется предложенным Git Credential Manager способом.

## 2 Подготовить окружение и загрузить файлы

PowerShell, из каталога приложения:

```powershell
cd 'C:\Политех\КПО\Project\web-log-project'
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
python -m pytest
```

Если .venv ещё нет, перед активацией создать её: `py -3.12 -m venv .venv`.

Что делают команды:

| Команда | Назначение |
| --- | --- |
| `cd ...` | Переходит в каталог приложения |
| `.\.venv\Scripts\Activate.ps1` | Подключает Python и библиотеки виртуального окружения к текущему терминалу |
| `python -m pip install -e '.[dev]'` | Устанавливает приложение в редактируемом режиме и инструменты разработки из pyproject.toml |
| `python -m ruff check src tests scripts` | Проверяет код линтером, например на неиспользуемые импорты |
| `python -m ruff format --check src tests scripts` | Проверяет форматирование без изменения файлов |
| `python -m pytest` | Запускает модульные и интеграционные тесты |

`python -m` запускает указанный модуль через выбранный Python.
Эти команды выполняют локальную подготовку и проверки; загрузка на GitHub
выполняется позднее командой `git push`.

Для тестовых файлов pytest использует служебный каталог `.pytest-tmp`
внутри проекта, заданный в pyproject.toml. Это позволяет запускать тесты
без обращения к недоступному `%TEMP%\pytest-of-Alexander`.
При новом запуске pytest очищает этот служебный каталог; свои файлы туда
не помещать. Каталог исключён из Git через .gitignore.

Для нового локального репозитория:

```powershell
git init -b main
git config user.name 'Улыбин А. А.'
git config user.email 'ВАШ_EMAIL'
git config core.hooksPath .githooks
git add .
git diff --cached --stat
git commit -m 'chore: initialize project and GitHub Actions'
git remote add origin https://github.com/ВАШ_ЛОГИН/web-log-reports.git
git push -u origin main
```

Заменить ВАШ_EMAIL и ВАШ_ЛОГИН своими данными. При `git add .` находиться именно в web-log-project.
Если Git уже инициализирован, сначала посмотреть `git status`, `git branch` и `git remote -v`.
Существующий origin меняется командой `git remote set-url origin <HTTPS-адрес>`.

На GitHub в корне должны быть .github, src, tests, scripts, docs, README и pyproject.toml.
В .gitignore исключены .venv, reports, dist, .env и реальные журналы.
Первый push создаёт main; после него включить её защиту и далее работать через PR.

## 3 Проверить GitHub Actions

Открыть **Actions → CI → запуск первого push**.
Файл конфигурации — `.github/workflows/ci.yml`.

| Job и имя проверки | Действия |
| --- | --- |
| commit-policy | Проверка заголовков коммитов |
| lint | Ruff check и Ruff format --check |
| tests-and-metrics | Unit/integration, покрытие, JUnit, Radon, metrics.json |
| build | Wheel и sdist после успеха остальных jobs |

Первые три jobs выполняются параллельно. Build зависит от успешного завершения всех трёх.
Метрики и загрузка отчётов выполняются и при падении тестов; ошибка тестирования остаётся ошибкой job.
Если исходного XML-отчёта нет, сборщик отмечает отсутствующий файл и завершается с ошибкой.

Внизу страницы запуска находится раздел **Artifacts**:

- `quality-reports-<run_id>-<attempt>` — metrics.json, junit.xml, coverage.xml, HTML-покрытие, ruff.json и complexity.json;
- `dist-<run_id>-<attempt>` — wheel и sdist.

JSON также выводится в **Summary** запуска. XML-отчёты сохраняются файлами; отдельные аннотации покрытия и интерфейс результатов тестов сторонними actions не подключены.
Срок хранения артефактов — 30 дней.

Workflow запускается на push веток, push тегов, PR в main и вручную через workflow_dispatch.
При push в ветку открытого PR возможны два запуска: проверка ветки и проверка PR.
PR тестирует пробное слияние с main, а commit-policy проверяет исходные коммиты PR.
Для контрольных замеров этапов использовать теги на main.
Автоматическое развёртывание опционально по заданию и здесь не включено.

## 4 Защитить main

После первого CI открыть **Settings → Branches → Add classic branch protection rule**.
В некоторых версиях интерфейса кнопка называется **Add rule**.
В **Branch name pattern** указать `main`.

Включить:

- **Require a pull request before merging**.
- **Require status checks to pass before merging** и выбрать **все четыре**: `commit-policy`, `lint`, `tests-and-metrics`, `build`.
- **Require branches to be up to date before merging**.
- **Require conversation resolution before merging**.
- **Do not allow bypassing the above settings** — правило применяется и к владельцу.

Проверки появляются в поиске после их первого запуска.
Для индивидуального проекта **Require approvals** оставить выключенным: автор PR не может заменить второго проверяющего своим одобрением.
Самопроверку оформить в описании PR и просмотром diff.
**Allow force pushes**, **Allow deletions** и **Lock branch** не включать.
Сохранить правило. Если вместо classic rules используются Rulesets, задать аналогичные требования для main, включить их применение и не добавлять участников в bypass.

В **Settings → General → Pull Requests** оставить **Allow merge commits**.
Для принятой учебной схемы выключить squash и rebase merge, чтобы сохранить проверенные коммиты.

Сам файл CI не включает защиту ветки на сервере. Требование PR, обязательные проверки и запрет обхода обеспечивают ограничение.

## 5 Ветки и коммиты

Используется GitHub Flow: постоянная main и короткие ветки реальных задач, например `feature/log-ingestion`, `feature/pdf-reports`, `fix/invalid-log-date`.
В PR указывается ссылка на задачу YouGile и этап разработки.

Сообщение: `тип(область): описание`; область необязательна, заголовок до 100 символов.
Типы: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.

```text
feat(parser): parse access log records
fix(api): reject invalid log batch
test: cover empty statistics
ci: collect quality metrics
```

Локальная проверка подключается через `git config core.hooksPath .githooks`.
В Linux/macOS также выполнить `chmod +x .githooks/commit-msg`.
Hook и CI проверяют заголовок по правилам проекта; merge-коммиты пропускаются.

Для демонстрации hook подготовить изменение README и выполнить `git add README.md`, затем `git commit -m 'update'`.
Коммит должен быть отклонён. Повторить с правильным сообщением: `git commit -m 'docs: describe next increment goals'`.

## 6 Первый Pull Request

```powershell
git switch main
git pull --ff-only
git switch -c docs/add-project-goals
```

Добавить в README цели следующего инкремента, затем:

```powershell
git add README.md
git commit -m 'docs: describe next increment goals'
git push -u origin docs/add-project-goals
```

На GitHub: **Compare & pull request** или **Pull requests → New pull request**.
Base — main, compare — docs/add-project-goals.
Заполнить шаблон из .github/pull_request_template.md, нажать **Create pull request**.
Проверить **Files changed** и **Checks**. После успеха выбрать **Merge pull request → Confirm merge**.
Проверить отдельный запуск Actions на main и обновить локальную main через `git pull --ff-only`.

Для демонстрации блокировки создать ветку `test/lint-gate`, добавить неиспользуемый `import os` в main.py,
зафиксировать `test: demonstrate lint gate` и открыть PR.
Ruff F401 делает lint красным, а защита main блокирует Merge.
Удалить импорт коммитом `fix: remove unused import`, дождаться зелёного CI.
Этот демонстрационный PR можно закрыть: функциональных изменений после исправления нет.

## 7 Метрики по этапам

Даты и теги приведены в [контрольных точках](metrics/README.md).
Автоматически собираются:

1. Количество замечаний Ruff.
2. Средняя цикломатическая сложность.
3. Максимальная цикломатическая сложность.
4. Покрытие строк.
5. Покрытие ветвей.
6. Число passed, failed, errors и skipped тестов.
7. Время тестирования в секундах.

Покрытие и сложность относятся к коду приложения; lint — к src, tests и scripts.
Порог pytest-cov 80% относится к совокупному покрытию строк и ветвей.
Замечание линтера не считается подтверждённым дефектом.

Снимок содержит дату, проверенный SHA, ref и URL запуска Actions.
После этапа поставить тег на проверенный commit main, дождаться CI, скачать quality-reports.
Сохранить metrics.json в docs/metrics отдельным docs-коммитом через PR.
SHA внутри снимка относится к измеренной версии и отличается от последующего коммита документации.
Снимки в Git сохраняют историю после истечения срока артефактов.

Для прошедших этапов без истории кода и измерений не создавать вымышленные значения.
Начать с текущей базовой точки `stage/baseline`.

## 8 Релиз

После успеха main проверить CHANGELOG и версию.
Изменение версии в pyproject.toml и API выполнить отдельным PR.
Текущая версия прототипа — 0.1.0.

```powershell
git switch main
git pull --ff-only
git log -1 --oneline
git tag -a v0.1.0 -m 'Prototype release 0.1.0'
git push origin v0.1.0
```

После успешного CI для тега скачать и распаковать dist-артефакт.
На странице репозитория: **Releases → Draft a new release**.
Выбрать существующий v0.1.0, название «Прототип 0.1.0», описание из CHANGELOG.
Прикрепить wheel и sdist в блоке вложений; после проверки нажать **Publish release**.
Исходные ZIP/TAR-архивы тега GitHub формирует отдельно.
Версия v1.0.0 относится к будущей полной реализации требований.

## 9 Доказательства для отчёта

- URL и страница репозитория с деревом файлов.
- Ветки, история коммитов и отклонение неправильного сообщения.
- Защита main с четырьмя обязательными проверками.
- PR с неуспешным lint и заблокированным Merge, затем исправление.
- Успешный PR и результат слияния.
- Зелёный Actions и артефакты quality-reports и dist.
- Реальные метрики, JUnit и покрытие, таблица замеров по этапам.
- Тег и опубликованный GitHub Release.

Скриншоты делать после выполнения действий. Локальная проверка не подтверждает удалённый запуск Actions и настройки защиты.

## Официальные источники

- https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository
- https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
- https://www.conventionalcommits.org/en/v1.0.0/
- https://docs.astral.sh/ruff/configuration/
- https://radon.readthedocs.io/en/latest/commandline.html
