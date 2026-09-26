# claude-design-research — инвентарь для фазы 2

Скрипт `_skill-build/tools/inventory.py`, 26.09.2026 17:50. Токены — Opus 5.5 по калибровке.
Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, service, forbidden — нет.

## Классы файлов

| класс | файлов | МБ | ~токенов | переносим? |
|---|---|---|---|---|
| prose | 34 | 0.7 | 244K | да |
| data | 11 | 0.1 | 33K | да |
| code | 23 | 0.2 | 92K | да |
| tool | 11 | 0.2 | 94K | да |
| root-doc | 2 | 0.1 | 29K | да |
| asset | 136 | 20.7 | 0K | нет |
| junk | 1 | 0.0 | 0K | нет |
| service | 136 | 93.4 | 0K | нет |
| forbidden | 13663 | 444.5 | 0K | нет |
| **итого переносим** | 81 | 1.3 | 493K | |
| **итого не переносим** | 13936 | 558.6 | — | |

## Папки верхнего уровня

| папка | файлов | МБ | ~токенов текста | состав |
|---|---|---|---|---|
| (корень) | 2 | 0.1 | 29K | root-doc 2 |
| 01-product | 2 | 0.1 | 38K | prose 2 |
| 02-claude-code-bridge | 2 | 0.1 | 28K | prose 2 |
| 03-practice-pipelines | 2 | 0.1 | 44K | prose 2 |
| 04-claude-code-native | 12 | 0.2 | 85K | prose 2, data 1, code 9 |
| 05-design-artifacts | 26 | 0.2 | 63K | prose 8, data 4, code 14 |
| 06-design-process | 24 | 0.3 | 112K | prose 18, data 6 |
| 90-sources | 1 | 0.0 | 0K | service 1 |
| 91-videos | 17 | 0.4 | 0K | service 17 |
| 99-raw | 13929 | 558.5 | 94K | tool 11, asset 136, junk 1, service 118, forbidden 13663 |

## Служебные папки (группами, топ по размеру)

| группа | файлов | МБ |
|---|---|---|
| 99-raw/cache | 13663 | 444.5 |
| 99-raw/youtube | 24 | 91.5 |
| 99-raw/experiments | 74 | 1.1 |
| 99-raw/notes | 6 | 0.3 |
| 91-videos/transcripts | 7 | 0.2 |
| 91-videos/digests | 8 | 0.2 |
| 99-raw/reports | 6 | 0.1 |
| 99-raw/prompts | 8 | 0.1 |
| 90-sources/sources.md | 1 | 0.0 |
| 91-videos/catalog.md | 1 | 0.0 |
| 91-videos/README.md | 1 | 0.0 |

## Серые зоны (решить при переносе)

- **Крупные текстовые файлы > 1 МБ**: 0
- **PLAN.md (план ресерча)**: 1 — PLAN.md (34 КБ)
- **Индекс источников в 90-sources**: 1 — 90-sources/sources.md
- **Служебные файлы, на которые ссылается переносимое (ссылок)**: 33 — claude-design-research/99-raw/cache/cc-2.1.281-design (7); claude-design-research/91-videos (6); claude-design-research/99-raw/cache (5); claude-design-research/99-raw/experiments/D/01-kit-smoke (4); claude-design-research/90-sources/sources.md (4); claude-design-research/99-raw/cache/repos (3); claude-design-research/91-videos/catalog.md (3); claude-design-research/99-raw/notes/A-notes.md (2); claude-design-research/99-raw/notes/C-notes.md (2); claude-design-research/99-raw/notes/V-notes.md (2); claude-design-research/99-raw/reports/C-report.md (2); claude-design-research/91-videos/digests/SUMMARY.md (2); … ещё 21
- **Код, который ссылается на ассеты (без них сломается; число ссылок)**: 0

## Код и утилиты (34 файлов)

| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |
|---|---|---|---|---|---|---|---|
| `99-raw/tools/cc_bunfs_extract.py` | 89 | Извлечь встроенные файлы из бинарника Claude Code (Bun standalone) — только чтение бинарника. | fnmatch, glob, mmap, struct, subprocess |  | да |  |  |
| `99-raw/tools/fetch.py` | 77 | Скачать страницу и сохранить читаемый текст (Markdown) в 99-raw/cache/. | bs4, hashlib, requests, subprocess | да | да |  | 1 |
| `99-raw/tools/lang_check.py` | 95 | Z/04 lang_check: проверка языка готовой вёрстки русскоязычного сайта (без модели, без сети). | html |  | да |  | 1 |
| `99-raw/tools/mockup_checks.py` | 1538 | k3_checks.py — проверки арт-директора для сборок Kimi K3: приметы K3, выдумки, мобильная версия, сторож потока | PIL, colorsys, functools, http, io, math, playwright, socketserver, statistics,  | да | да |  | 1 |
| `99-raw/tools/render_fetch.py` | 107 | Скачать страницу через headless-браузер (Playwright/Chromium) и сохранить читаемый Markdown в 99-raw/cache/. | hashlib, playwright, subprocess | да | да |  | 1 |
| `99-raw/tools/shot_v3.py` | 396 | shot.py v3 — «глаза» дизайн-цикла Claude ↔ K3: кадры по экранам + проверки, которых не видно на ужатом кадре. | functools, http, playwright, socketserver, threading, time, urllib | да | да |  |  |
| `99-raw/tools/sources_collect.py` | 141 | Сводный список источников базы claude-design-research → 90-sources/sources.md. | urllib | да | да |  | 16 |
| `99-raw/tools/stand_page.py` | 443 | stand_page.py — страница слепого попарного выбора для СТЕНДА тестов (T, волна 2, 2026-09-24). | PIL, csv, importlib, math, random, tempfile |  | да | 1 | 2 |
| `99-raw/tools/vtt2md.py` | 114 | Собирает 91-videos/transcripts/<id>.md из уже скачанных .vtt и .info.json без обращения к YouTube. | glob |  | да |  | 5 |
| `99-raw/tools/yt_dl.py` | 200 | Загрузка метаданных, субтитров и комментариев YouTube без видео и аудио, с паузами и обработкой HTTP 429. | glob, subprocess, time |  | да | 1 | 6 |
| `99-raw/tools/yt_transcript.py` | 210 | Субтитры и метаданные YouTube-видео без скачивания самого видео (через yt-dlp). | requests, yt_dlp | да | да |  | 2 |
| `04-claude-code-native/kit/canvas.html` | 221 |  |  |  |  |  |  |
| `04-claude-code-native/kit/diffshots.py` | 189 | kit/diffshots.py — «изменилось только то, что просили»: сравнение двух снимков shot.py по меткам #N. | PIL, numpy |  | да |  |  |
| `04-claude-code-native/kit/example/booking.html` | 110 |  |  |  |  |  |  |
| `04-claude-code-native/kit/example/landing.html` | 144 |  |  |  |  |  |  |
| `04-claude-code-native/kit/example/site.css` | 141 |  |  |  |  |  |  |
| `04-claude-code-native/kit/example/tokens.css` | 111 |  |  |  |  |  |  |
| `04-claude-code-native/kit/export.py` | 252 | kit/export.py — экспорт холста без интерфейса Claude Design: PDF по артбордам, PNG 2×, standalone.html, zip. | PIL, base64, mimetypes, playwright, pypdf, shot, time, zipfile | да | да |  |  |
| `04-claude-code-native/kit/marks.js` | 424 |  |  |  |  |  |  |
| `04-claude-code-native/kit/shot.py` | 640 | kit/shot.py — «глаза» холста для работы из чата: PNG каждого артборда (с метками #N и без), весь холст, marks. | PIL, fcntl, functools, http, playwright, socketserver, threading, time, urllib | да | да |  |  |
| `05-design-artifacts/example/canvas/project/Booking.dc.html` | 140 |  |  |  |  |  |  |
| `05-design-artifacts/example/canvas/project/Dir-Cobalt.dc.html` | 63 |  |  |  |  |  |  |
| `05-design-artifacts/example/canvas/project/Dir-Graphite.dc.html` | 58 |  |  |  |  |  |  |
| `05-design-artifacts/example/canvas/project/Dir-Paper.dc.html` | 55 |  |  |  |  |  |  |
| `05-design-artifacts/example/canvas/project/Landing-Phone.dc.html` | 144 |  |  |  |  |  |  |
| `05-design-artifacts/example/canvas/project/Main.dc.html` | 148 |  |  |  |  |  |  |
| `05-design-artifacts/example/canvas/project/Wire-Desktop.dc.html` | 93 |  |  |  |  |  |  |
| `05-design-artifacts/example/canvas/project/Wire-Phone.dc.html` | 67 |  |  |  |  |  |  |
| `05-design-artifacts/example/design-system/project/components/Button/preview.html` | 16 |  |  |  |  |  |  |
| `05-design-artifacts/example/design-system/project/components/Cover/preview.html` | 45 |  |  |  |  |  |  |
| `05-design-artifacts/example/design-system/project/components/Field/preview.html` | 36 |  |  |  |  |  |  |
| `05-design-artifacts/example/design-system/project/components/ServiceCard/preview.html` | 35 |  |  |  |  |  |  |
| `05-design-artifacts/example/design-system/project/components/Steps/preview.html` | 23 |  |  |  |  |  |  |
| `05-design-artifacts/example/design-system/project/components/bundle.css` | 124 |  |  |  |  |  |  |

Зашитые абсолютные пути (2 разных): `/home/mm/.nvm/versions/node/v24.21.0/bin/node`; `/home/mm/Документы/app-design/ai-media-research/99-raw/tools/stand_run.py`

## Ссылки из переносимых файлов (md, данные, код)

| статус | число | смысл |
|---|---|---|
| ok | 244 | цель переносится |
| to-excluded | 66 | цель есть, но не переносится (служебное, ассет, мусор) — сломается |
| to-kimi | 0 | ведёт в kimi-research (донор) — заменить при уборке |
| missing | 245 | цели нет уже сейчас (или путь условный) |
| outside | 0 | абсолютный путь вне базы |
| short-unresolved | 96 | адрес «NN/MM» не нашёл файла (часто — номер раздела) |

Сломаются — по источнику ссылки и типу цели:

| тип цели | из md | из данных | из кода | всего |
|---|---|---|---|---|
| служебное | 63 | 0 | 3 | 66 |

Примеры to-excluded:
- `01-product/01-claude-design-product.md:9 → 99-raw/cache/`
- `01-product/01-claude-design-product.md:9 → 99-raw/notes/A-notes.md`
- `01-product/01-claude-design-product.md:461 → 99-raw/notes/C-notes.md`
- `01-product/01-claude-design-product.md:498 → 91-videos/`
- `01-product/01-claude-design-product.md:504 → 91-videos/`
- `01-product/01-claude-design-product.md:600 → 99-raw/cache/`
- `01-product/01-claude-design-product.md:619 → ../ux-research/99-raw/cache/www.anthropic.com_news_claude-design-anthropic-labs_0573c409.md`
- `01-product/01-claude-design-product.md:638 → 99-raw/notes/V-notes.md`
- `01-product/01-claude-design-product.md:638 → 99-raw/notes/C-notes.md`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:8 → 99-raw/cache/cc-2.1.281-design/`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:505 → 99-raw/cache/cc-2.1.281-design/`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:512 → 99-raw/cache/cc-2.1.281-design/`

Примеры missing:
- `01-product/01-claude-design-product.md:576 → ../kimi-research/09-test-plan/`
- `01-product/01-claude-design-product.md:637 → ../kimi-research/99-raw/cache/platform.claude.com_claude-prompting-best-practices.md`
- `01-product/01-claude-design-product.md:637 → ../kimi-research/99-raw/notes/wave1/E-notes.md`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:34 → .design-sync/conventions.md`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:131 → bunfs/chunk-p041d5e2.js`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:167 → ~/.claude/settings.json`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:251 → project/canvas.json`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:256 → api/tokens.md`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:297 → .design-sync/config.json`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:325 → ../kimi-research/07-brief-handoff/`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:441 → ../kimi-research/02-harness-orchestration/05-architecture-recommendation.md`
- `02-claude-code-bridge/01-claude-code-and-claude-design.md:447 → .design-sync/conventions.md`

## Входящие ссылки из соседних ресерчей

Всего 13: creative-research 7; ux-research 6. Самые цитируемые файлы: `claude-design-research/91-videos/digests/6XNhZu6mJlE.md` 8; `claude-design-research` 2; `claude-design-research/99-raw/reports/E-report.md` 2; `claude-design-research/99-raw/cache/rive.app_pricing_ebd26c5e.md` 1

## Короткие адреса и указатели

- адресов «NN/MM» (свои и «<база> NN/MM»): 155, из них файл не найден: 96 — зависят от нумерации папок и файлов
- указателей «→ … §» в тексте: 307 — зависят от нумерации разделов внутри файлов

## Дубли утилит (md5) в других ресерчах

- `claude-design-research/99-raw/tools/fetch.py` = `ai-media-research/99-raw/tools/fetch.py`, `blender-research/99-raw/tools/fetch.py`, `creative-research/99-raw/tools/fetch.py`, `site-research/99-raw/tools/fetch.py`, `text-research/99-raw/tools/fetch.py`, `ui-research/99-raw/tools/fetch.py`, `ux-research/99-raw/tools/fetch.py`
- `claude-design-research/99-raw/tools/render_fetch.py` = `ai-media-research/99-raw/tools/render_fetch.py`, `blender-research/99-raw/tools/render_fetch.py`, `creative-research/99-raw/tools/render_fetch.py`, `site-research/99-raw/tools/render_fetch.py`, `text-research/99-raw/tools/render_fetch.py`, `ui-research/99-raw/tools/render_fetch.py`, `ux-research/99-raw/tools/render_fetch.py`
- `claude-design-research/99-raw/tools/vtt2md.py` = `ai-media-research/99-raw/tools/vtt2md.py`, `creative-research/99-raw/tools/vtt2md.py`, `site-research/99-raw/tools/vtt2md.py`, `text-research/99-raw/tools/vtt2md.py`
- `claude-design-research/99-raw/tools/yt_dl.py` = `ai-media-research/99-raw/tools/yt_dl.py`, `creative-research/99-raw/tools/yt_dl.py`, `site-research/99-raw/tools/yt_dl.py`, `text-research/99-raw/tools/yt_dl.py`
- `claude-design-research/99-raw/tools/yt_transcript.py` = `ai-media-research/99-raw/tools/yt_transcript.py`, `blender-research/99-raw/tools/yt_transcript.py`, `creative-research/99-raw/tools/yt_transcript.py`, `site-research/99-raw/tools/yt_transcript.py`, `text-research/99-raw/tools/yt_transcript.py`

## Kimi / K3

218 строк в 19 переносимых файлах. Топ: `99-raw/tools/mockup_checks.py` 58; `03-practice-pipelines/01-practice-and-pipelines.md` 38; `README.md` 33; `04-claude-code-native/01-claude-design-in-claude-code-session.md` 27; `PLAN.md` 19; `02-claude-code-bridge/01-claude-code-and-claude-design.md` 13; `99-raw/tools/stand_page.py` 8; `99-raw/tools/shot_v3.py` 4; `06-design-process/stand/S1-kvarts/01-description-and-questions.md` 3; `06-design-process/stand/S2-smena/brief.yaml` 3

## «Внешнее» — оценка объёма финальной уборки

- ссылок в исключаемое (служебное и т. п.): 66; строк с упоминанием служебных папок: 85
- ссылок в соседние ресерчи: 99 (из них в kimi: 0)
- меток роликов `[V:…]`: 62
- строк про Kimi/K3: 218
