# ux-research — инвентарь для фазы 2

Скрипт `_skill-build/tools/inventory.py`, 26.09.2026 11:56. Токены — Opus 5.5 по калибровке.
Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, service, forbidden — нет.

## Классы файлов

| класс | файлов | МБ | ~токенов | переносим? |
|---|---|---|---|---|
| prose | 71 | 6.1 | 1752K | да |
| data | 2 | 0.4 | 124K | да |
| tool | 10 | 0.1 | 41K | да |
| root-doc | 2 | 0.2 | 73K | да |
| asset | 53 | 597.2 | 0K | нет |
| service | 1716 | 296.1 | 0K | нет |
| **итого переносим** | 85 | 6.8 | 1990K | |
| **итого не переносим** | 1769 | 893.3 | — | |

## Папки верхнего уровня

| папка | файлов | МБ | ~токенов текста | состав |
|---|---|---|---|---|
| (корень) | 3 | 0.3 | 103K | prose 1, root-doc 2 |
| 01-foundations | 5 | 0.5 | 131K | prose 5 |
| 02-ia-navigation | 3 | 0.2 | 55K | prose 3 |
| 03-layout-placement | 5 | 0.3 | 76K | prose 5 |
| 04-components-patterns | 11 | 1.1 | 306K | prose 11 |
| 05-flows-journeys | 6 | 0.5 | 162K | prose 6 |
| 06-feedback-states-motion | 5 | 0.4 | 119K | prose 5 |
| 07-ux-writing | 8 | 0.6 | 159K | prose 7, data 1 |
| 08-accessibility | 5 | 0.4 | 142K | prose 5 |
| 09-mobile | 5 | 0.5 | 137K | prose 5 |
| 10-design-systems-consistency | 3 | 0.2 | 47K | prose 3 |
| 11-ai-generated-ui | 5 | 0.4 | 114K | prose 5 |
| 12-evaluation-checklists | 6 | 0.9 | 284K | prose 5, data 1 |
| 13-app-types | 5 | 0.4 | 114K | prose 5 |
| 90-sources | 2 | 0.2 | 0K | service 2 |
| 91-videos | 176 | 8.6 | 0K | service 176 |
| 99-raw | 1601 | 884.6 | 41K | tool 10, asset 53, service 1538 |

## Служебные папки (группами, топ по размеру)

| группа | файлов | МБ |
|---|---|---|
| 99-raw/youtube | 446 | 262.2 |
| 99-raw/cache | 993 | 19.2 |
| 91-videos/transcripts | 83 | 4.6 |
| 99-raw/notes | 39 | 4.5 |
| 91-videos/digests | 91 | 3.9 |
| 99-raw/reports | 28 | 1.0 |
| 99-raw/prompts | 31 | 0.4 |
| 90-sources/sources.tsv | 1 | 0.2 |
| 91-videos/catalog.md | 1 | 0.1 |
| 99-raw/handoff-to-ui-research.md | 1 | 0.0 |
| 91-videos/catalog.tsv | 1 | 0.0 |
| 90-sources/README.md | 1 | 0.0 |

## Серые зоны (решить при переносе)

- **Крупные текстовые файлы > 1 МБ**: 0
- **PLAN.md (план ресерча)**: 1 — PLAN.md (81 КБ)
- **Индекс источников в 90-sources**: 2 — 90-sources/README.md; 90-sources/sources.tsv
- **Служебные файлы, на которые ссылается переносимое (ссылок)**: 99 — ux-research/91-videos/digests (11); ux-research/90-sources (10); ux-research/99-raw/reports/wave4-X-audit.md (7); ux-research/91-videos/digests/u-SB1s2PTds.md (7); ux-research/91-videos/digests/GCJ6k3tD50A.md (6); ux-research/91-videos/digests/6Vh49gMvirE.md (6); ux-research/91-videos/digests/2juq00vrvl0.md (6); ux-research/90-sources/sources.tsv (5); ux-research/91-videos/digests/9Msod5MrJbo.md (5); ux-research/91-videos/digests/qktwIWZNFY4.md (5); ux-research/91-videos/digests/I4UIIISgl2U.md (5); ux-research/91-videos/digests/xEtKkLdAnvI.md (5); … ещё 87
- **Код, который ссылается на ассеты (без них сломается; число ссылок)**: 0

## Код и утилиты (10 файлов)

| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |
|---|---|---|---|---|---|---|---|
| `99-raw/tools/ax.sh` | 6 |  |  |  |  | 1 | 1 |
| `99-raw/tools/before_after_build.py` | 83 | Сборка 07-ux-writing/before-after.tsv: пары «до / после» из таблиц папки 07 (Плохо / Хорошо; словари замен 07/ | glob, io |  |  |  | 2 |
| `99-raw/tools/checklist_export.py` | 165 | Экспорт сводного чек-листа в YAML. | glob, io, yaml |  |  |  | 2 |
| `99-raw/tools/fetch.py` | 77 | Скачать страницу и сохранить читаемый текст (Markdown) в 99-raw/cache/. | bs4, hashlib, requests, subprocess | да | да |  | 1 |
| `99-raw/tools/m3_fetch.py` | 515 | Скачать страницу m3.material.io и сохранить читаемый Markdown в 99-raw/cache/. | bs4, difflib, hashlib, html, requests, subprocess, time | да | да |  | 2 |
| `99-raw/tools/render_fetch.py` | 107 | Скачать страницу через headless-браузер (Playwright/Chromium) и сохранить читаемый Markdown в 99-raw/cache/. | hashlib, playwright, subprocess | да | да |  | 1 |
| `99-raw/tools/sources_collect.py` | 252 | Сводная библиография базы ux-research. | glob, io |  |  |  | 11 |
| `99-raw/tools/transcribe_local.py` | 233 | Локальная транскрибация YouTube-видео или аудиофайла через Qwen3-ASR-1.7B (llama.cpp, CPU). | shutil, subprocess, time |  | да |  | 4 |
| `99-raw/tools/vtt2md.py` | 111 | Собирает 91-videos/transcripts/<id>.md из уже скачанных .vtt и .info.json без обращения к YouTube. | glob |  | да | 3 | 5 |
| `99-raw/tools/yt_transcript.py` | 210 | Субтитры и метаданные YouTube-видео без скачивания самого видео (через yt-dlp). | requests, yt_dlp | да | да |  | 2 |

Зашитые абсолютные пути (4 разных): `/home/mm/.cache/tmp/claude-1000/-home-mm----------/114b2b30-8909-48b5-9403-5787f03c373c/scratchpad/yt/cm`; `/home/mm/Документы/ux-research/91-videos/transcripts`; `/home/mm/Документы/ux-research/99-raw/tools/fetch.py`; `/home/mm/Документы/ux-research/99-raw/youtube`

## Ссылки из переносимых файлов (md, данные, код)

| статус | число | смысл |
|---|---|---|
| ok | 2921 | цель переносится |
| to-excluded | 229 | цель есть, но не переносится (служебное, ассет, мусор) — сломается |
| to-kimi | 0 | ведёт в kimi-research (донор) — заменить при уборке |
| missing | 456 | цели нет уже сейчас (или путь условный) |
| outside | 3 | абсолютный путь вне базы |
| short-unresolved | 27 | адрес «NN/MM» не нашёл файла (часто — номер раздела) |

Сломаются — по источнику ссылки и типу цели:

| тип цели | из md | из данных | из кода | всего |
|---|---|---|---|---|
| служебное | 208 | 15 | 6 | 229 |

Примеры to-excluded:
- `00-glossary.md:3 → 99-raw/reports/wave4-X-audit.md`
- `00-glossary.md:396 → 91-videos/catalog.md`
- `00-glossary.md:397 → 90-sources/sources.tsv`
- `00-glossary.md:398 → 99-raw/reports/wave4-X-audit.md`
- `01-foundations/03-frameworks-domain-to-screens.md:877 → 91-videos/transcripts/UkAWsPcWvBM.md`
- `01-foundations/03-frameworks-domain-to-screens.md:878 → 91-videos/transcripts/YnYLTmxdWIQ.md`
- `01-foundations/README.md:16 → ../99-raw/notes/wave1/A-notes.md`
- `01-foundations/README.md:16 → ../99-raw/reports/wave1-A-report.md`
- `02-ia-navigation/02-navigation-patterns.md:955 → 91-videos/transcripts/P1CYZ65b5SA.md`
- `03-layout-placement/01-page-anatomy-templates.md:806 → 91-videos/transcripts/P1CYZ65b5SA.md`
- `04-components-patterns/01-data-tables.md:1078 → ../91-videos/digests/23AQBZzDUIo.md`
- `04-components-patterns/03-dashboards-and-kpi.md:1039 → ../91-videos/digests/ZqNRywpO3bE.md`

Примеры missing:
- `00-glossary.md:46 → 01-foundations/03`
- `00-glossary.md:108 → 05-flows-journeys/03`
- `00-glossary.md:109 → 10-design-systems-consistency/01`
- `00-glossary.md:120 → 01-foundations/01`
- `00-glossary.md:135 → 02-ia-navigation/01`
- `00-glossary.md:178 → 07-ux-writing/02`
- `00-glossary.md:193 → 05-flows-journeys/01`
- `00-glossary.md:235 → 01-foundations/01`
- `00-glossary.md:242 → 07-ux-writing/06`
- `00-glossary.md:257 → 04-components-patterns/01`
- `00-glossary.md:258 → 06-feedback-states-motion/04`
- `00-glossary.md:392 → 11-ai-generated-ui/01`

Примеры outside:
- `07-ux-writing/03-russian-interface-text.md:1182 → /home/mm/Документы/Как_избежать_нейрослопа_(гайд).md`
- `07-ux-writing/06-banned-words-and-patterns.md:358 → /home/mm/Документы/Как_избежать_нейрослопа_(гайд).md`
- `07-ux-writing/06-banned-words-and-patterns.md:712 → /home/mm/Документы/Как_избежать_нейрослопа_(гайд).md`

## Входящие ссылки из соседних ресерчей

Всего 646: site-research 273; text-research 225; creative-research 61; ui-research 44; ai-media-research 17; blender-research 16; claude-design-research 10. Самые цитируемые файлы: `ux-research/06-feedback-states-motion/04-dark-patterns-and-ethics.md` 70; `ux-research/07-ux-writing/06-banned-words-and-patterns.md` 64; `ux-research` 42; `ux-research/07-ux-writing/03-russian-interface-text.md` 33; `ux-research/07-ux-writing/01-principles-voice-and-tone.md` 30; `ux-research/06-feedback-states-motion/03-motion-and-microinteractions.md` 29; `ux-research/12-evaluation-checklists/01-expert-review-protocols.md` 24; `ux-research/11-ai-generated-ui/02-research-and-benchmarks.md` 24; `ux-research/07-ux-writing/02-microcopy-by-component.md` 23; `ux-research/08-accessibility` 21

## Короткие адреса и указатели

- адресов «NN/MM» (свои и «<база> NN/MM»): 48, из них файл не найден: 27 — зависят от нумерации папок и файлов
- указателей «→ … §» в тексте: 1701 — зависят от нумерации разделов внутри файлов

## Дубли утилит (md5) в других ресерчах

- `ux-research/99-raw/tools/fetch.py` = `ai-media-research/99-raw/tools/fetch.py`, `blender-research/99-raw/tools/fetch.py`, `claude-design-research/99-raw/tools/fetch.py`, `creative-research/99-raw/tools/fetch.py`, `kimi-research/99-raw/tools/fetch.py`, `site-research/99-raw/tools/fetch.py`, `text-research/99-raw/tools/fetch.py`, `ui-research/99-raw/tools/fetch.py`
- `ux-research/99-raw/tools/render_fetch.py` = `ai-media-research/99-raw/tools/render_fetch.py`, `blender-research/99-raw/tools/render_fetch.py`, `claude-design-research/99-raw/tools/render_fetch.py`, `creative-research/99-raw/tools/render_fetch.py`, `kimi-research/99-raw/tools/render_fetch.py`, `site-research/99-raw/tools/render_fetch.py`, `text-research/99-raw/tools/render_fetch.py`, `ui-research/99-raw/tools/render_fetch.py`

## Kimi / K3

11 строк в 3 переносимых файлах. Топ: `11-ai-generated-ui/02-research-and-benchmarks.md` 8; `11-ai-generated-ui/01-failure-modes-catalog.md` 2; `11-ai-generated-ui/04-constraints-prompts-and-checks.md` 1

## «Внешнее» — оценка объёма финальной уборки

- ссылок в исключаемое (служебное и т. п.): 229; строк с упоминанием служебных папок: 222
- ссылок в соседние ресерчи: 179 (из них в kimi: 0)
- меток роликов `[V:…]`: 1291
- строк про Kimi/K3: 11
