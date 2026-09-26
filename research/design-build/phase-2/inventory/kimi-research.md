# kimi-research — инвентарь для фазы 2

Скрипт `_skill-build/tools/inventory.py`, 26.09.2026 11:56. Токены — Opus 5.5 по калибровке.
Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, service, forbidden — нет. **Этот ресерч — донор: в шаблон не переносится.**

## Классы файлов

| класс | файлов | МБ | ~токенов | переносим? |
|---|---|---|---|---|
| prose | 86 | 2.2 | 844K | донор |
| data | 14 | 0.2 | 67K | донор |
| code | 13 | 0.4 | 188K | донор |
| tool | 13 | 0.4 | 175K | донор |
| root-doc | 3 | 0.2 | 83K | донор |
| asset | 2342 | 598.5 | 0K | донор |
| junk | 3635 | 130.6 | 0K | донор |
| service | 14869 | 329.8 | 0K | донор |
| **итого переносим** | 0 | 0.0 | 0K | |
| **итого не переносим** | 20975 | 1062.4 | — | |

## Папки верхнего уровня

| папка | файлов | МБ | ~токенов текста | состав |
|---|---|---|---|---|
| (корень) | 3 | 0.2 | 83K | root-doc 3 |
| 00-glossary | 2 | 0.1 | 29K | prose 2 |
| 01-model-k3 | 10 | 0.2 | 66K | prose 4, data 6 |
| 02-harness-orchestration | 6 | 0.3 | 120K | prose 6 |
| 03-prompting | 5 | 0.3 | 101K | prose 5 |
| 04-skills-tools-repos | 5 | 0.2 | 67K | prose 4, data 1 |
| 05-reviews-practice | 5 | 0.2 | 66K | prose 5 |
| 06-cn-ecosystem | 4 | 0.2 | 55K | prose 4 |
| 07-brief-handoff | 19 | 0.3 | 129K | prose 14, data 2, code 3 |
| 08-director-loop-qa | 5 | 0.2 | 64K | prose 5 |
| 09-test-plan | 5 | 0.3 | 114K | prose 4, data 1 |
| 10-playbook-skill | 47 | 0.7 | 288K | prose 33, data 4, code 10 |
| 90-sources | 2 | 0.1 | 0K | service 2 |
| 91-videos | 1302 | 178.1 | 0K | asset 1289, service 13 |
| 99-raw | 19555 | 881.1 | 175K | tool 13, asset 1053, junk 3635, service 14854 |

## Служебные папки (группами, топ по размеру)

| группа | файлов | МБ |
|---|---|---|
| 99-raw/cache | 13297 | 208.0 |
| 99-raw/youtube | 11 | 65.3 |
| 99-raw/experiments | 1492 | 53.9 |
| 99-raw/notes | 19 | 1.3 |
| 99-raw/reports | 16 | 0.5 |
| 91-videos/digests | 6 | 0.3 |
| 99-raw/prompts | 18 | 0.2 |
| 91-videos/transcripts | 3 | 0.1 |
| 90-sources/sources.md | 1 | 0.1 |
| 91-videos/frames | 3 | 0.0 |
| 99-raw/tools | 1 | 0.0 |
| 90-sources/README.md | 1 | 0.0 |
| 91-videos/catalog.md | 1 | 0.0 |

## Серые зоны (решить при переносе)

- **Крупные текстовые файлы > 1 МБ**: 0
- **PLAN.md (план ресерча)**: 1 — PLAN.md (130 КБ)
- **Индекс источников в 90-sources**: 2 — 90-sources/README.md; 90-sources/sources.md
- **Служебные файлы, на которые ссылается переносимое (ссылок)**: 0
- **Код, который ссылается на ассеты (без них сломается; число ссылок)**: 0

## Код и утилиты (26 файлов)

| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |
|---|---|---|---|---|---|---|---|
| `99-raw/tools/check_links.py` | 678 | Проверка ссылок и структуры базы kimi-research (агент X, волна 3, 24.09.2026). | glob, ssl, time, urllib | да | да |  | 19 |
| `99-raw/tools/color.py` | 176 | Расчёты цвета для интерфейсов без внешних зависимостей (написано агентом A волны 1, проверено по калькулятору  | math |  | да |  | 1 |
| `99-raw/tools/fetch.py` | 77 | Скачать страницу и сохранить читаемый текст (Markdown) в 99-raw/cache/. | bs4, hashlib, requests, subprocess | да | да |  | 1 |
| `99-raw/tools/k3_checks.py` | 1518 | k3_checks.py — проверки арт-директора для сборок Kimi K3: приметы K3, выдумки, мобильная версия, сторож потока | PIL, colorsys, functools, http, io, math, playwright, socketserver, statistics,  | да | да |  | 1 |
| `99-raw/tools/kimi_run.py` | 426 | kimi_run.py — обёртка «Claude → Kimi Code 2.x (`kimi -p`)» для дизайн-итераций. ПРОТОТИП (B2, 2026-09-24). | glob, shlex, shutil, signal, statistics, subprocess, threading, time |  | да |  | 1 |
| `99-raw/tools/measure_ui.py` | 1214 | Измерить визуальный слой живой веб-страницы через headless-браузер (Playwright/Chromium). | color, hashlib, playwright, time | да | да |  | 2 |
| `99-raw/tools/render_fetch.py` | 107 | Скачать страницу через headless-браузер (Playwright/Chromium) и сохранить читаемый Markdown в 99-raw/cache/. | hashlib, playwright, subprocess | да | да |  | 1 |
| `99-raw/tools/site_probe.py` | 446 | site_probe.py — замер живого 3D-сайта (агент A, волна 1). Дополняет 99-raw/tools/web_view.py --url. | PIL, playwright, time | да | да |  | 1 |
| `99-raw/tools/ui_audit.py` | 1474 | Объединённый прогон визуального QA страницы: измерение + сверка с токенами и порогами базы + отчёт. | color, math, playwright | да | да |  | 4 |
| `99-raw/tools/vtt2md.py` | 114 | Собирает 91-videos/transcripts/<id>.md из уже скачанных .vtt и .info.json без обращения к YouTube. | glob |  | да |  | 5 |
| `99-raw/tools/yt_dl.py` | 200 | Загрузка метаданных, субтитров и комментариев YouTube без видео и аудио, с паузами и обработкой HTTP 429. | glob, subprocess, time |  | да | 1 | 6 |
| `99-raw/tools/yt_frames.py` | 312 | Видео YouTube → кадры для «просмотра глазами» агентом (kimi-research, оркестратор, 23.09.2026). | PIL, glob, subprocess, time |  | да | 1 | 6 |
| `99-raw/tools/yt_transcript.py` | 210 | Субтитры и метаданные YouTube-видео без скачивания самого видео (через yt-dlp). | requests, yt_dlp | да | да |  | 2 |
| `07-brief-handoff/templates/build_package.py` | 1243 | build_package.py — сборщик и проверщик пакета задачи K3 из brief.yaml (F, волна 2, 2026-09-24). | PIL, math, shutil, subprocess, yaml |  | да | 1 | 2 |
| `07-brief-handoff/templates/shot.py` | 378 | shot.py v3 — «глаза» дизайн-цикла Claude ↔ K3: кадры по экранам + проверки, которых не видно на ужатом кадре. | functools, http, playwright, socketserver, threading, time, urllib | да | да |  |  |
| `07-brief-handoff/templates/tokens.css` | 22 |  |  |  |  |  |  |
| `10-playbook-skill/skills/kimi-design-director/scripts/k3_checks.py` | 1518 | k3_checks.py — проверки арт-директора для сборок Kimi K3: приметы K3, выдумки, мобильная версия, сторож потока | PIL, colorsys, functools, http, io, math, playwright, socketserver, statistics,  | да | да |  | 1 |
| `10-playbook-skill/skills/kimi-design-director/scripts/kimi_run.py` | 426 | kimi_run.py — обёртка «Claude → Kimi Code 2.x (`kimi -p`)» для дизайн-итераций. ПРОТОТИП (B2, 2026-09-24). | glob, shlex, shutil, signal, statistics, subprocess, threading, time |  | да |  | 1 |
| `10-playbook-skill/skills/kimi-design-director/scripts/lang_check.py` | 80 | Z/04 lang_check: проверка языка готовой вёрстки русскоязычного сайта (без модели, без сети). | html |  | да |  | 1 |
| `10-playbook-skill/skills/kimi-design-director/scripts/stand_page.py` | 429 | stand_page.py — страница слепого попарного выбора для СТЕНДА тестов (T, волна 2, 2026-09-24). | PIL, csv, importlib, math, random, tempfile |  | да | 1 | 1 |
| `10-playbook-skill/skills/kimi-design-director/scripts/variants_page.py` | 107 | variants_page.py — страница слепого попарного выбора вариантов сайта поверх `stand_run.py page` (ai-media, аге | importlib, random |  | да | 1 | 1 |
| `10-playbook-skill/skills/kimi-design-director/templates/build_package.py` | 1243 | build_package.py — сборщик и проверщик пакета задачи K3 из brief.yaml (F, волна 2, 2026-09-24). | PIL, math, shutil, subprocess, yaml |  | да | 1 | 2 |
| `10-playbook-skill/skills/kimi-design-director/templates/shot.py` | 378 | shot.py v3 — «глаза» дизайн-цикла Claude ↔ K3: кадры по экранам + проверки, которых не видно на ужатом кадре. | functools, http, playwright, socketserver, threading, time, urllib | да | да |  |  |
| `10-playbook-skill/skills/kimi-design-director/templates/tokens.css` | 22 |  |  |  |  |  |  |
| `10-playbook-skill/skills/kimi-design-executor/scripts/lang_check.py` | 80 | Z/04 lang_check: проверка языка готовой вёрстки русскоязычного сайта (без модели, без сети). | html |  | да |  | 1 |
| `10-playbook-skill/skills/kimi-design-executor/scripts/shot.py` | 378 | shot.py v3 — «глаза» дизайн-цикла Claude ↔ K3: кадры по экранам + проверки, которых не видно на ужатом кадре. | functools, http, playwright, socketserver, threading, time, urllib | да | да |  |  |

Зашитые абсолютные пути (3 разных): `/home/mm/.nvm/versions/node/v24.21.0/bin/node`; `/home/mm/Документы/app-design/ai-media-research/99-raw/tools/stand_run.py`; `/home/mm/Документы/app-design/kimi-research/99-raw/tools/kimi_run.py`

## Ссылки из переносимых файлов (md, данные, код)

| статус | число | смысл |
|---|---|---|
| ok | 0 | цель переносится |
| to-excluded | 0 | цель есть, но не переносится (служебное, ассет, мусор) — сломается |
| to-kimi | 0 | ведёт в kimi-research (донор) — заменить при уборке |
| missing | 0 | цели нет уже сейчас (или путь условный) |
| outside | 0 | абсолютный путь вне базы |
| short-unresolved | 0 | адрес «NN/MM» не нашёл файла (часто — номер раздела) |

## Входящие ссылки из соседних ресерчей

Нет.

## Короткие адреса и указатели

- адресов «NN/MM» (свои и «<база> NN/MM»): 0, из них файл не найден: 0 — зависят от нумерации папок и файлов
- указателей «→ … §» в тексте: 0 — зависят от нумерации разделов внутри файлов

## Дубли утилит (md5) в других ресерчах

- `kimi-research/99-raw/tools/color.py` = `ai-media-research/99-raw/tools/color.py`, `creative-research/99-raw/tools/color.py`, `site-research/99-raw/tools/color.py`, `ui-research/99-raw/tools/color.py`
- `kimi-research/99-raw/tools/fetch.py` = `ai-media-research/99-raw/tools/fetch.py`, `blender-research/99-raw/tools/fetch.py`, `claude-design-research/99-raw/tools/fetch.py`, `creative-research/99-raw/tools/fetch.py`, `site-research/99-raw/tools/fetch.py`, `text-research/99-raw/tools/fetch.py`, `ui-research/99-raw/tools/fetch.py`, `ux-research/99-raw/tools/fetch.py`
- `kimi-research/99-raw/tools/render_fetch.py` = `ai-media-research/99-raw/tools/render_fetch.py`, `blender-research/99-raw/tools/render_fetch.py`, `claude-design-research/99-raw/tools/render_fetch.py`, `creative-research/99-raw/tools/render_fetch.py`, `site-research/99-raw/tools/render_fetch.py`, `text-research/99-raw/tools/render_fetch.py`, `ui-research/99-raw/tools/render_fetch.py`, `ux-research/99-raw/tools/render_fetch.py`
- `kimi-research/99-raw/tools/site_probe.py` = `ai-media-research/99-raw/tools/site_probe.py`, `blender-research/99-raw/tools/site_probe.py`, `creative-research/99-raw/tools/site_probe.py`, `site-research/99-raw/tools/site_probe.py`, `text-research/99-raw/tools/site_probe.py`
- `kimi-research/99-raw/tools/vtt2md.py` = `ai-media-research/99-raw/tools/vtt2md.py`, `claude-design-research/99-raw/tools/vtt2md.py`, `creative-research/99-raw/tools/vtt2md.py`, `site-research/99-raw/tools/vtt2md.py`, `text-research/99-raw/tools/vtt2md.py`
- `kimi-research/99-raw/tools/yt_dl.py` = `ai-media-research/99-raw/tools/yt_dl.py`, `claude-design-research/99-raw/tools/yt_dl.py`, `creative-research/99-raw/tools/yt_dl.py`, `site-research/99-raw/tools/yt_dl.py`, `text-research/99-raw/tools/yt_dl.py`
- `kimi-research/99-raw/tools/yt_transcript.py` = `ai-media-research/99-raw/tools/yt_transcript.py`, `blender-research/99-raw/tools/yt_transcript.py`, `claude-design-research/99-raw/tools/yt_transcript.py`, `creative-research/99-raw/tools/yt_transcript.py`, `site-research/99-raw/tools/yt_transcript.py`, `text-research/99-raw/tools/yt_transcript.py`
- `kimi-research/99-raw/tools/measure_ui.py` = `creative-research/99-raw/tools/measure_ui.py`, `site-research/99-raw/tools/measure_ui.py`, `ui-research/99-raw/tools/measure_ui.py`
- `kimi-research/99-raw/tools/ui_audit.py` = `creative-research/99-raw/tools/ui_audit.py`, `site-research/99-raw/tools/ui_audit.py`, `ui-research/99-raw/tools/ui_audit.py`
- `kimi-research/99-raw/tools/yt_frames.py` = `creative-research/99-raw/tools/yt_frames.py`

## Kimi / K3

4937 строк в 115 переносимых файлах. Топ: `PLAN.md` 246; `02-harness-orchestration/01-kimi-code-overview.md` 217; `09-test-plan/tests.yaml` 175; `10-playbook-skill/PLAYBOOK.md` 175; `02-harness-orchestration/04-alternative-harnesses.md` 164; `06-cn-ecosystem/01-official-cn.md` 154; `09-test-plan/01-test-plan.md` 149; `01-model-k3/01-model-card.md` 147; `02-harness-orchestration/03-control-interfaces.md` 141; `03-prompting/01-official-guidance.md` 134

## «Внешнее» — оценка объёма финальной уборки

- ссылок в исключаемое (служебное и т. п.): 0; строк с упоминанием служебных папок: 0
- ссылок в соседние ресерчи: 0 (из них в kimi: 0)
- меток роликов `[V:…]`: 0
- строк про Kimi/K3: 4937
