# ui-research — инвентарь для фазы 2

Скрипт `_skill-build/tools/inventory.py`, 26.09.2026 17:50. Токены — Opus 5.5 по калибровке.
Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, service, forbidden — нет.

## Классы файлов

| класс | файлов | МБ | ~токенов | переносим? |
|---|---|---|---|---|
| prose | 106 | 5.0 | 1747K | да |
| data | 7 | 0.5 | 197K | да |
| code | 9 | 0.1 | 44K | да |
| tool | 10 | 0.3 | 146K | да |
| root-doc | 3 | 0.2 | 54K | да |
| asset | 77 | 105.9 | 0K | нет |
| junk | 2 | 0.2 | 0K | нет |
| service | 1091 | 26.1 | 0K | нет |
| **итого переносим** | 135 | 6.0 | 2187K | |
| **итого не переносим** | 1170 | 132.3 | — | |

## Папки верхнего уровня

| папка | файлов | МБ | ~токенов текста | состав |
|---|---|---|---|---|
| (корень) | 3 | 0.2 | 54K | root-doc 3 |
| 00-glossary | 2 | 0.3 | 110K | prose 2 |
| 01-color | 8 | 0.4 | 134K | prose 8 |
| 02-typography | 8 | 0.4 | 149K | prose 8 |
| 03-spacing-sizing | 5 | 0.2 | 61K | prose 5 |
| 04-shape-elevation | 5 | 0.2 | 63K | prose 5 |
| 05-layout-grid | 8 | 0.5 | 161K | prose 8 |
| 06-components-visual | 10 | 0.4 | 136K | prose 10 |
| 07-iconography-imagery | 4 | 0.2 | 59K | prose 4 |
| 08-motion | 5 | 0.2 | 87K | prose 5 |
| 09-design-tokens | 7 | 0.5 | 219K | prose 7 |
| 10-design-systems-atlas | 7 | 0.4 | 132K | prose 7 |
| 11-styles-trends | 6 | 0.3 | 108K | prose 6 |
| 12-ai-generated-ui | 6 | 0.3 | 100K | prose 6 |
| 13-evaluation-checklists | 5 | 0.2 | 61K | prose 5 |
| 14-recipes | 36 | 1.1 | 409K | prose 20, data 7, code 9 |
| 90-sources | 2 | 0.3 | 0K | service 2 |
| 91-videos | 59 | 2.0 | 0K | service 59 |
| 99-raw | 1119 | 130.3 | 146K | tool 10, asset 77, junk 2, service 1030 |

## Служебные папки (группами, топ по размеру)

| группа | файлов | МБ |
|---|---|---|
| 99-raw/cache | 980 | 21.8 |
| 91-videos/transcripts | 38 | 1.5 |
| 99-raw/notes | 20 | 1.2 |
| 99-raw/reports | 15 | 0.6 |
| 91-videos/digests | 20 | 0.5 |
| 90-sources/bibliography.md | 1 | 0.3 |
| 99-raw/prompts | 15 | 0.2 |
| 91-videos/README.md | 1 | 0.0 |
| 90-sources/README.md | 1 | 0.0 |

## Серые зоны (решить при переносе)

- **Крупные текстовые файлы > 1 МБ**: 0
- **PLAN.md (план ресерча)**: 1 — PLAN.md (29 КБ)
- **Индекс источников в 90-sources**: 1 — 90-sources/README.md
- **Служебные файлы, на которые ссылается переносимое (ссылок)**: 105 — ui-research/91-videos/digests (30); ui-research/99-raw/notes/wave2/M-notes.md (14); ui-research/91-videos/digests/01-schoger-refactoring-ui-css-day-2019.md (11); ui-research/91-videos/digests/09-kole-jain-dashboard-and-ai-slop.md (11); ui-research/91-videos/digests/14-birman-aesthetics-in-ui.md (9); ui-research/91-videos/digests/07-tim-gabe-type-space-8pt-grid.md (9); ui-research/99-raw/notes/wave1/B-notes.md (8); ui-research/91-videos/digests/03-refactoring-ui-screencasts.md (8); ui-research/91-videos/README.md (8); ui-research/90-sources (8); ui-research/91-videos/digests/04-schoger-think-like-visual-designer.md (7); ui-research/99-raw/notes/wave2/D-notes.md (7); … ещё 93
- **Код, который ссылается на ассеты (без них сломается; число ссылок)**: 0

## Код и утилиты (19 файлов)

| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |
|---|---|---|---|---|---|---|---|
| `99-raw/tools/analyze_measurements.py` | 301 | Сводный разбор измерений: таблицы и распределения для 10-design-systems-atlas/04-*.md. | glob |  |  | 1 | 1 |
| `99-raw/tools/build_reference_tokens.py` | 1588 | Генератор эталонной схемы токенов для `09-design-tokens/04-reference-token-schema.md`. | color, itertools |  | да |  | 3 |
| `99-raw/tools/check_links.py` | 818 | Проверка перекрёстных ссылок и структуры базы ui-research. | glob |  | да |  | 18 |
| `99-raw/tools/color.py` | 176 | Расчёты цвета для интерфейсов без внешних зависимостей (написано агентом A волны 1, проверено по калькулятору  | math |  | да |  | 1 |
| `99-raw/tools/fetch.py` | 77 | Скачать страницу и сохранить читаемый текст (Markdown) в 99-raw/cache/. | bs4, hashlib, requests, subprocess | да | да |  | 1 |
| `99-raw/tools/measure_ui.py` | 1214 | Измерить визуальный слой живой веб-страницы через headless-браузер (Playwright/Chromium). | color, hashlib, playwright, time | да | да |  | 2 |
| `99-raw/tools/render_fetch.py` | 107 | Скачать страницу через headless-браузер (Playwright/Chromium) и сохранить читаемый Markdown в 99-raw/cache/. | hashlib, playwright, subprocess | да | да |  | 1 |
| `99-raw/tools/retry_transcripts.sh` | 27 |  |  |  |  |  | 3 |
| `99-raw/tools/ui_audit.py` | 1474 | Объединённый прогон визуального QA страницы: измерение + сверка с токенами и порогами базы + отчёт. | color, math, playwright | да | да |  | 4 |
| `99-raw/tools/yt_transcript.py` | 210 | Субтитры и метаданные YouTube-видео без скачивания самого видео (через yt-dlp). | requests, yt_dlp | да | да |  | 2 |
| `14-recipes/examples/01-table-with-filters.html` | 197 |  |  |  |  |  |  |
| `14-recipes/examples/02-form.html` | 99 |  |  |  |  |  |  |
| `14-recipes/examples/03-dashboard.html` | 91 |  |  |  |  |  |  |
| `14-recipes/examples/04-empty-state.html` | 57 |  |  |  |  |  |  |
| `14-recipes/examples/05-modal.html` | 77 |  |  |  |  |  |  |
| `14-recipes/examples/06-settings.html` | 86 |  |  |  |  |  |  |
| `14-recipes/examples/07-object-page.html` | 99 |  |  |  |  |  |  |
| `14-recipes/examples/app.css` | 584 |  |  |  |  |  |  |
| `14-recipes/examples/tokens.css` | 637 |  |  |  |  |  | 1 |

Зашитые абсолютные пути (1 разных): `/home/mm/Документы/ui-research/99-raw/cache/measurements`

## Ссылки из переносимых файлов (md, данные, код)

| статус | число | смысл |
|---|---|---|
| ok | 2502 | цель переносится |
| to-excluded | 282 | цель есть, но не переносится (служебное, ассет, мусор) — сломается |
| to-kimi | 0 | ведёт в kimi-research (донор) — заменить при уборке |
| missing | 852 | цели нет уже сейчас (или путь условный) |
| outside | 0 | абсолютный путь вне базы |
| short-unresolved | 321 | адрес «NN/MM» не нашёл файла (часто — номер раздела) |

Сломаются — по источнику ссылки и типу цели:

| тип цели | из md | из данных | из кода | всего |
|---|---|---|---|---|
| ассет | 24 | 0 | 0 | 24 |
| служебное | 257 | 0 | 1 | 258 |

Примеры to-excluded:
- `00-glossary/README.md:26 → 91-videos/digests/`
- `00-glossary/glossary.md:19 → 91-videos/digests/`
- `00-glossary/glossary.md:1747 → 99-raw/prompts/_common.md`
- `01-color/06-character-gradients-tools.md:39 → 99-raw/tools`
- `02-typography/01-font-selection.md:698 → ../91-videos/digests/`
- `02-typography/01-font-selection.md:851 → 99-raw/notes/wave1/B-notes.md`
- `02-typography/01-font-selection.md:857 → ../91-videos/digests/01-schoger-refactoring-ui-css-day-2019.md`
- `02-typography/01-font-selection.md:858 → ../91-videos/digests/02-schoger-little-details-laracon-2018.md`
- `02-typography/01-font-selection.md:859 → ../91-videos/digests/15-korolkova-typography-cyrillic.md`
- `02-typography/02-type-scale.md:502 → ../91-videos/digests/`
- `02-typography/02-type-scale.md:1105 → 99-raw/notes/wave1/B-notes.md`
- `02-typography/02-type-scale.md:1116 → ../91-videos/digests/02-schoger-little-details-laracon-2018.md`

Примеры missing:
- `00-glossary/glossary.md:985 → 02-illustration-system-avatars-images.md`
- `00-glossary/glossary.md:1349 → ../11-styles-trends/02`
- `00-glossary/glossary.md:1353 → ../11-styles-trends/02`
- `00-glossary/glossary.md:1403 → ../11-styles-trends/04`
- `00-glossary/glossary.md:1439 → ../09-design-tokens/05`
- `00-glossary/glossary.md:1509 → ../13-evaluation-checklists/02`
- `00-glossary/glossary.md:1543 → /llms.txt`
- `00-glossary/glossary.md:1746 → 01-color/03`
- `01-color/01-color-models-and-scales.md:188 → src/light.ts`
- `01-color/01-color-models-and-scales.md:188 → src/dark.ts`
- `01-color/01-color-models-and-scales.md:190 → polaris-tokens/src/colors.ts`
- `01-color/01-color-models-and-scales.md:194 → ant-design-colors/src/generate.ts`

## Входящие ссылки из соседних ресерчей

Всего 694: creative-research 280; ux-research 170; ai-media-research 128; claude-design-research 46; blender-research 27; text-research 25; site-research 18. Самые цитируемые файлы: `ui-research/11-styles-trends/04-anti-slop-ui.md` 89; `ui-research` 83; `ui-research/07-iconography-imagery/02-illustration-system-avatars-images.md` 40; `ui-research/11-styles-trends/02-style-tiles-and-character-knobs.md` 36; `ui-research/13-evaluation-checklists/02-rubrics-and-vlm-critic.md` 36; `ui-research/08-motion/03-reduced-motion-and-motion-tokens.md` 32; `ui-research/03-spacing-sizing` 30; `ui-research/07-iconography-imagery/01-icons.md` 23; `ui-research/01-color` 21; `ui-research/11-styles-trends/01-style-dictionary-for-quiz.md` 20

## Короткие адреса и указатели

- адресов «NN/MM» (свои и «<база> NN/MM»): 371, из них файл не найден: 321 — зависят от нумерации папок и файлов
- указателей «→ … §» в тексте: 1406 — зависят от нумерации разделов внутри файлов

## Дубли утилит (md5) в других ресерчах

- `ui-research/99-raw/tools/color.py` = `ai-media-research/99-raw/tools/color.py`, `creative-research/99-raw/tools/color.py`, `site-research/99-raw/tools/color.py`
- `ui-research/99-raw/tools/fetch.py` = `ai-media-research/99-raw/tools/fetch.py`, `blender-research/99-raw/tools/fetch.py`, `claude-design-research/99-raw/tools/fetch.py`, `creative-research/99-raw/tools/fetch.py`, `site-research/99-raw/tools/fetch.py`, `text-research/99-raw/tools/fetch.py`, `ux-research/99-raw/tools/fetch.py`
- `ui-research/99-raw/tools/render_fetch.py` = `ai-media-research/99-raw/tools/render_fetch.py`, `blender-research/99-raw/tools/render_fetch.py`, `claude-design-research/99-raw/tools/render_fetch.py`, `creative-research/99-raw/tools/render_fetch.py`, `site-research/99-raw/tools/render_fetch.py`, `text-research/99-raw/tools/render_fetch.py`, `ux-research/99-raw/tools/render_fetch.py`
- `ui-research/99-raw/tools/measure_ui.py` = `creative-research/99-raw/tools/measure_ui.py`, `site-research/99-raw/tools/measure_ui.py`
- `ui-research/99-raw/tools/ui_audit.py` = `creative-research/99-raw/tools/ui_audit.py`, `site-research/99-raw/tools/ui_audit.py`

## Kimi / K3

45 строк в 17 переносимых файлах. Топ: `14-recipes/examples/audit/01-table-with-filters.html.json` 3; `14-recipes/examples/audit/01-table-with-filters.html.md` 3; `14-recipes/examples/audit/02-form.html.json` 3; `14-recipes/examples/audit/02-form.html.md` 3; `14-recipes/examples/audit/03-dashboard.html.json` 3; `14-recipes/examples/audit/03-dashboard.html.md` 3; `14-recipes/examples/audit/04-empty-state.html.json` 3; `14-recipes/examples/audit/04-empty-state.html.md` 3; `14-recipes/examples/audit/05-modal.html.json` 3; `14-recipes/examples/audit/05-modal.html.md` 3

## «Внешнее» — оценка объёма финальной уборки

- ссылок в исключаемое (служебное и т. п.): 282; строк с упоминанием служебных папок: 374
- ссылок в соседние ресерчи: 44 (из них в kimi: 0)
- меток роликов `[V:…]`: 0
- строк про Kimi/K3: 45
