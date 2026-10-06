# Т-код-text — строки зон кода и решения приёмки в базе text

Коммит начала — `1e0cd2a`. Пути — от `.claude/skills/design-deep-dive/`. Работа шла в два захода (обрыв среды 429): на
диске после обрыва была только своя правка `10/01`, остальное `kb/text` совпадало со снимком начала.

## Файлы

- Статьи (28): `kb/text/README.md`, `PLAN.md`; `02-strategy-messaging/` README, 02, 03; `03-corpus-measured/` README, 01,
  02, 03; `04-copy-by-block/` 01, 03, 04; `05-voice-editorial/` README, 01, 03; `06-anti-slop/` README, 01, 02;
  `07-seo-geo-copy/03`; `08-russian-legal-typography/` README, 02; `09-ai-generation-evaluation/` README,
  `live-test-plan.md`, `prompts/p2-meaning.md`; `10-templates-recipes/` README, 01, 02, 03.
- Машинные файлы (11): `02/meaning.schema.yaml`, `02/message-hierarchy.schema.yaml`, `02/facts.schema.yaml`,
  `05/voice.schema.yaml`, `06/lexicon/artifacts.yaml`, `06/lexicon/marketing-role.yaml`, `06/lexicon/ru-mkt.yaml`,
  `03/thresholds.yaml`, `05/examples/voice-grafa-b2b.yaml`, `05/examples/voice-peklo-bold.yaml`,
  `10/examples/ru-okoshko-webinar.yaml`.
- Новые (2): `05-voice-editorial/examples/facts-demo-grafa.yaml`, `facts-demo-peklo.yaml`.

## Строки → место → итог

| источник | файл и место | итог |
|---|---|---|
| К4а: `--all-variants` отчётом | 10/01 §4.2; §10 строка команды «варианты — отчётом» | внесено |
| К4а: открытый выбор `select`, COPY-D-CHOSEN | 10/01 §4.3 (абзац после п. 5) | внесено; по коду ещё таблица переходов 10/01 §1.1 и таблица статусов 10/README: `chosen` у `draft` нужен, когда вариант вышел из `draft` |
| К4а: одна иерархия, COPY-D-HIERARCHY | 10/01 §3, после таблицы точек человека | внесено (каркас — заметка: так говорит `--help` `skeleton`) |
| К4а: запись файла | 10/01 §1.2 | внесено; по коду — пример §10: копии deck в папке исходного (`W`), иначе `approve` не находит факты (проверено песочницей) |
| К4а: 10/02 `rebase_refs`, `variant.checks` | 10/02 §4 (абзац), §5 | внесено: `rebase_refs` в коде нет, абзац говорит текущее поведение (ссылки от папки исходного файла) |
| К4а: 10/README шаг вариантов и команда | 10/README выжимка п. 6, блок команд | внесено |
| К4а: `messenger-prefill` | 04/04 §1, после таблицы слотов | внесено (сверено с `copy-slots.yaml`) |
| К4а: сверка смысла `meaning-claims` | 02/README, после строки проверки B1 | внесено |
| К4б: внешние правила линтера | 06/02 выжимка п. 5, §2.6 | внесено |
| К4б: 06/README строка 36 | 06/README выжимка п. 10 | внесено |
| К4б: плотность маркеров `allow_error: false`; микрокопи у шести жанров | 06/02 §6 (конец), §4 (после таблицы профилей) | внесено (сверено с `profiles.yaml`: `allow_error: false`, якорь `ux_on_page` у шести жанров) |
| К4б: шапка и `overrides` в `claims-rules.yaml` | `08/claims-rules.yaml` | не внесено: файл не зоны (решает владелец); по коду поправлена статья 08/README: «`copy_lint.py` его не подключает (разово — `--rules`)» |
| К4б: `x-hero-first-optional`, `x-blocker-optional` | 02/02 §2.2 п. 7, §4.3 | внесено |
| К4б: голос продукта без сайта | 05/01 §2.3 | внесено (`…/voice.product.yaml` — форма образца, иначе refcheck видит битый путь) |
| К4б + К4в: сущности `product`, `place` | 02/03 §7.1, новый пункт «Сущности» | внесено одной записью |
| К4в: имя сущности и COPY-D-LEN | 10/01 выжимка п. 16 | внесено (сверено: нижняя граница не действует у заголовков, верхняя действует) |
| К12: путь машины в text | 03/01 [S10], 06/01 §11 и [S1], 06/02 [S2], 08/02 [S10], PLAN.md (3) | внесено: 8 из 8, гайд заказчика назван без пути; обёрток `flock … browser.lock` в статьях text нет — уже так |
| Д-text-1: `before_after_build.py`, `copy_metrics.py`, `orch_check.py`, «только скриптами» | 10/README стр. 22 и блок команд; README базы: таблица утилит, «Как обновлять» | внесено: преемник — `copydeck.py before-after` (пустой `why`, остальное — данные); `orch_check.py` → `scripts/maint/accept.py`; строки `before_after_build`, `copy_metrics`, `copy_extract` сняты |
| Д-text-1: источник `J3-examples` | 10/02 §7, 10/03 | внесено (в таблице такой колонки нет) |
| Д-text-1: id `B2-2`, `W1-7`, `A4`, `X24` в live-test-plan; заголовок 09/03 §3.4 | — | не внесено: переименование идёт вместе с `copy-checklist.yaml` и `copy-rubric.yaml`, они не названы; следы — уборке |
| Д-text-1: `copy-checklist.yaml` 350, 363 | — | не внесено: машинный файл не назван, правка содержательная |
| Д-text-2: `corpus.tsv`, `measurements.tsv` | 03/README (строки файлов, утилиты, `corpus-D`), 03/01, 03/02, 03/03, 04/01, 04/03, 07/03 | внесено; `copy_metrics.py` в 09/live-test-plan → `copy_lint.py --metrics-only` (живой ключ «замеры корпуса для порогов») |
| сверх строк: пути окружения исследования | README базы (4), 02/README (2), p2-meaning, 06/01, 06/02, 05/01, 05/README | внесено: `99-raw/tools/venv-*` → `~/.cache/design-deep-dive/venv/bin/python` (`scripts/README.md`; pymorphy3 и jsonschema там есть) |

## Решения приёмки по машинным файлам

1. «контракт тройки v2 §N» → норма там, где живёт (`kb/common/owners.md`, сверено поиском): § Форматы обмена — шапки
   `facts.schema.yaml` и `message-hierarchy.schema.yaml`, `x-owner` и два места `facts.schema.yaml` (description `kind`,
   комментарий `x-site-brief-proof`), шапка `meaning.schema.yaml`, `source` в `artifacts.yaml`; § Темы — `x-owner`
   `meaning.schema.yaml` (поля «смысл» брифа) и `voice.schema.yaml` (голос у text); § Общие правила тройки — `source` в
   `ru-mkt.yaml` (FAQ) и `marketing-role.yaml:106` («Нам доверяют»); § Правила владения — шапка `marketing-role.yaml`
   (поправки ux для сайта). 14 замен, номер пункта ушёл везде. `x-owner`, `source` код не читает (поиск по `scripts/`).
2. `thresholds.yaml`: `corpus-D:` → `corpus:` — 354 значения `rows[].source` и строка шапки 14 (2 вхождения), всего 356;
   структура файла иначе та же (сравнение разобранных YAML). Код поле не читает. Упоминания `corpus-D` в статьях были
   путями `99-raw/cache/corpus-D/…`, которых нет, — сняты вместе с опорой; норма об этике (копии чужих страниц не входят
   в базу) осталась.
3. `x-status` снят в `meaning.schema.yaml` и `message-hierarchy.schema.yaml` (код читает только `x-status-rules` схемы
   copy deck).
4. `meaning.schema.yaml`: «дубли сводит исполнитель слоя страницы».
5. Демо-факты голоса скопированы в `05-voice-editorial/examples/`; в шапках копий сняты штамп и буквы исполнителей,
   путь формата — `../../02-strategy-messaging/facts.schema.yaml`; четыре ссылки `facts_ref` и `claims_boundaries_ref` →
   `facts-demo-*.yaml`. Попутно: путь образца в 05/03, строка о демо-фактах в 05/README.
6. `ru-okoshko-webinar.yaml`: в шапке, `notes`, `basis`, `reason` сняты J3, E, F, G, C, H, X34, S1a, дата; «E 03 §3.5» →
   «text 04/03 §3.5» (раздел есть). Данные без заметок совпадают с исходными (сравнение разобранных YAML).
   `authors: ['J3 (…)']` и `selection.by: 'редактор J3 (демо)'` — данные, не тронуты.

## Расхождения строк и статей с кодом (внесено по коду)

- `apply-selection` есть: 10/01 §4.3 п. 3 (запись голосов командой), снят пункт «Команды выбора нет»; README базы
  (блок команд, К29, таблица «в развитие»).
- Копии deck в другой папке теряют ссылки (подтверждено: `approve` — «facts.yaml не найден по facts_ref»): пример 10/01
  §10 и блок команд README базы пишут копии рядом с исходным.
- `why` в `before-after.tsv`: `copydeck.py before-after --check` — к заполнению 0; строка «`why` у 112 пар» снята.
- Таблица переходов 10/01: `import-kimi`, `upgrade`, `make_skeleton.py` нет → `skeleton`, `import-copy` (`--help`).
  Строка `copydeck.py` в таблице утилит README базы — подкоманды по `--help`.
- 02/02: `validate.py` нет → `scripts/text/validate_meaning.py`.

## Проверки (после последней правки)

- `scripts/tests/smoke.py --only scripts/text` — PASS 21, FAIL 0.
- `scripts/maint/sync_check.py` — генераторы OK 17, FAIL 0, находок 0 (статья ux 07/06 не тронута).
- `scripts/creative/spec_check.py canvas-map` — error 0, warning 0, info 12.
- `validate_voice.py` на обоих примерах — OK; `--selftest` — OK (мутации голоса продукта 7 из 7); контроль с битой
  ссылкой на факты — FAIL, как и должно; `claims_check.py lint-facts` на двух копиях — 0/0/0.
- `copydeck.py validate ru-okoshko-webinar.yaml` — код 0.
- Читатели схем вне text: `marketing_audit.py`, `mockup_checks.py`, `site_validate.py`, `ds_coverage.py`, `dc_texts.py` —
  selftest OK.
- `refcheck.py --strict` по 28 статьям: новых битых и следов 0; битых 709 → 649, следов 340 → 330.
- `normcheck.py --base HEAD --list-lost`: НОРМА 273 (потеряно 162, появилось 109, изменено 2) — все ожидаемые замены:
  снятые файлы и утилиты с их версиями и ключами (`corpus.tsv`, `measurements.tsv`, `copy_metrics` 0.3.2,
  `orch_check.py`, `before_after_build.py`, абзац «Повторяемость» о колонках `corpus.tsv`, `run_final.sh`), пути
  окружения и машины, внесённые строки; заголовки 03/01 §4, §5 без имён утилит (номера разделов те же; в
  `before-after.tsv` ссылок на 03/01 нет).
- `canon_check.py` — 0 ошибок, 0 предупреждений; `mapcheck.py kb/INDEX.md` — код 0.
- `accept.py --base HEAD --mask 'kb/text/*'`: разбор 53 — 0 находок, следы 0; «ссылки» — 9 на тронутых строках, все
  старые пути `99-raw/…` и `PROMPT.md` (новых нет, см. refcheck); «маски» FAIL — правки других зон в том же дереве.

## Не внесено — дальше

- Подкоманд `export-kimi`, `import-kimi`, `upgrade` нет, а пакет kimi описан как текущий: 10/01 выжимка п. 17, 20, §6,
  §7, §10; 10/README (статусы, команды, «Куда уходят поля»); README базы п. 7. Преемник `export --stage` выгружает вход
  холста, а не пакет kimi — нужен разбор владельца (вопрос 1).
- Утилиты, которых нет, вне строк: `check_intake.py` (14 мест в 09/*), `make_skeleton.py` (5 в 09/*), `k3_checks.py`
  (02/03, 10/01 §9), `copy_extract.py` (03/01 §4, 10/01 §9), `build_copy_slots.py` (04/README, README базы),
  `sources_collect.py` (README базы, PLAN), `check_rubric.py` (09/README).
- `thresholds.yaml`: шапка (стр. 3) и верхний `source` называют `corpus.tsv`, `measurements.tsv`; `tools` — версии
  `copy_metrics`, `copy_extract`. Поле не названо решением — владельцу.

## Отдать в общие файлы и соседям

- Владельцу `08/claims-rules.yaml`: шапка о читателях и блок `overrides` (линтер файл не подключает).
- Зоне фикстур: `scripts/tests/fixtures/input-site/files/voice.yaml` ведёт `facts_ref` в `99-raw/…/facts-demo-grafa.yaml`.
- Уборке следов: id живых тестов и заголовок 09/03 §3.4 вместе с `copy-checklist.yaml` и `copy-rubric.yaml`; «контракт
  v2» в статьях (02/README стр. 5 и 44).

## Список «снять»

- `kb/text/99-raw/experiments/F/04-voice-samples/facts-demo-grafa.yaml`, `facts-demo-peklo.yaml` — оригиналы; копии в
  `05-voice-editorial/examples/`, примеры ссылаются на копии.

## Вопросы

1. Пакет kimi в 10/01, 10/README и README базы: переписать на выгрузку во вход холста (`export --stage`) или снять?
2. 03/01 §4–§5 описывают инструменты исследования как метод (сбор блоков, метрики): оставить записью метода или сжать?
3. `authors` и `selection.by` примера вебинара несут «J3» — данные по решению 6 не тронуты; заменить нейтральными?
4. Верхний `source` и шапка `thresholds.yaml` называют файлы, которых нет: снять или назвать корпус без файлов?
