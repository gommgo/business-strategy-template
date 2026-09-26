# site-research — инвентарь для фазы 2

Скрипт `_skill-build/tools/inventory.py`, 26.09.2026 11:56. Токены — Opus 5.5 по калибровке.
Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, service, forbidden — нет.

## Классы файлов

| класс | файлов | МБ | ~токенов | переносим? |
|---|---|---|---|---|
| prose | 45 | 2.0 | 666K | да |
| data | 70 | 2.4 | 914K | да |
| tool | 27 | 1.2 | 538K | да |
| root-doc | 2 | 0.3 | 88K | да |
| asset | 596 | 86.7 | 0K | нет |
| junk | 769 | 17.5 | 0K | нет |
| service | 2148 | 251.6 | 0K | нет |
| **итого переносим** | 144 | 5.9 | 2206K | |
| **итого не переносим** | 3513 | 355.8 | — | |

## Папки верхнего уровня

| папка | файлов | МБ | ~токенов текста | состав |
|---|---|---|---|---|
| (корень) | 2 | 0.3 | 88K | root-doc 2 |
| 00-glossary | 2 | 0.1 | 24K | prose 2 |
| 01-foundations | 7 | 0.3 | 93K | prose 4, data 3 |
| 02-site-types | 7 | 0.6 | 224K | prose 4, data 3 |
| 03-page-structure | 4 | 0.2 | 56K | prose 4 |
| 04-blocks | 10 | 0.5 | 196K | prose 4, data 6 |
| 05-conversion-funnels | 5 | 0.3 | 82K | prose 4, data 1 |
| 06-multipage-ia | 7 | 0.3 | 90K | prose 3, data 4 |
| 07-seo-geo-performance-analytics | 10 | 0.5 | 165K | prose 5, data 5 |
| 08-legal-trust-a11y | 5 | 0.2 | 69K | prose 4, data 1 |
| 09-ai-generation-evaluation | 8 | 0.8 | 249K | prose 4, data 4 |
| 10-playbooks-contracts | 50 | 0.8 | 332K | prose 7, data 43 |
| 90-sources | 2 | 0.2 | 0K | service 2 |
| 91-videos | 40 | 1.5 | 0K | service 40 |
| 99-raw | 3498 | 355.3 | 538K | tool 27, asset 596, junk 769, service 2106 |

## Служебные папки (группами, топ по размеру)

| группа | файлов | МБ |
|---|---|---|
| 99-raw/youtube | 204 | 198.5 |
| 99-raw/experiments | 1413 | 36.0 |
| 99-raw/cache | 361 | 10.7 |
| 99-raw/notes | 69 | 3.2 |
| 91-videos/transcripts | 20 | 1.0 |
| 99-raw/reports | 20 | 0.8 |
| 99-raw/prompts | 35 | 0.6 |
| 91-videos/digests | 18 | 0.4 |
| 90-sources/sources.tsv | 1 | 0.1 |
| 91-videos/catalog.md | 1 | 0.1 |
| 99-raw/tools | 2 | 0.1 |
| 90-sources/README.md | 1 | 0.0 |
| 99-raw/handoff-to-neighbours.md | 1 | 0.0 |
| 91-videos/catalog.tsv | 1 | 0.0 |
| 99-raw/skills-map.md | 1 | 0.0 |

## Серые зоны (решить при переносе)

- **Крупные текстовые файлы > 1 МБ**: 0
- **PLAN.md (план ресерча)**: 1 — PLAN.md (163 КБ)
- **Индекс источников в 90-sources**: 2 — 90-sources/README.md; 90-sources/sources.tsv
- **Служебные файлы, на которые ссылается переносимое (ссылок)**: 165 — text-research/99-raw/notes/temp-vocabulary-v0.yaml (133); site-research/99-raw/notes/sync/creative-wave1-for-site-2026-09-24/README.md (22); site-research/99-raw/tools/README.md (18); text-research/99-raw/notes/orchestrator-notes.md (13); site-research/99-raw/notes/sync/creative-wave2-for-site-2026-09-24/README.md (11); site-research/99-raw/experiments/E/01-validate/validate.py (10); site-research/99-raw/prompts/_common.md (9); site-research/99-raw/notes/triad-contract-2026-09-24.md (9); site-research/99-raw/handoff-to-neighbours.md (9); site-research/90-sources/README.md (9); site-research/99-raw/experiments/F/01-quiz-forms-ru (7); site-research/99-raw/notes/wave2/H-notes.md (7); … ещё 153
- **Код, который ссылается на ассеты (без них сломается; число ссылок)**: 2 — 99-raw/tools/ia_probe.py (2); 99-raw/tools/page_anatomy.py (5)

## Код и утилиты (27 файлов)

| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |
|---|---|---|---|---|---|---|---|
| `99-raw/tools/ab_plan.py` | 424 | ab_plan.py — план и проверка A/B-теста страницы сайта (агент P, волна 2 site-research, 2026-09-24). | math, random, statistics |  | да |  | 9 |
| `99-raw/tools/asset_inventory.py` | 699 | asset_inventory.py — инвентарь визуальных ассетов живой страницы (агент A, волна 1 ai-media-research, 2026-09- | PIL, io, playwright, time, urllib | да | да |  |  |
| `99-raw/tools/check_links.py` | 1686 | Проверка перекрёстных ссылок, меток и структуры базы site-research. | glob, shutil, tempfile |  | да |  | 82 |
| `99-raw/tools/checklist_export.py` | 362 | checklist_export.py — сводный чек-лист сайта из Markdown в YAML (агент K, волна 3 site-research, 2026-09-24). | io, tempfile, yaml |  | да |  | 8 |
| `99-raw/tools/color.py` | 176 | Расчёты цвета для интерфейсов без внешних зависимостей (написано агентом A волны 1, проверено по калькулятору  | math |  | да |  | 1 |
| `99-raw/tools/ctx_watch.py` | 120 | Сторож контекста агентов site-research (копия утилиты оркестратора волн text-research от 24.09.2026 11:21; | time |  | да |  | 4 |
| `99-raw/tools/extract_for_audit.py` | 258 | Извлечения для аудитора X (и синтезатора S) базы site-research — оркестратор волн site, сессия 2, 24.09.2026. | yaml |  | да |  | 16 |
| `99-raw/tools/fetch.py` | 77 | Скачать страницу и сохранить читаемый текст (Markdown) в 99-raw/cache/. | bs4, hashlib, requests, subprocess | да | да |  | 1 |
| `99-raw/tools/geo_probe.py` | 1104 | geo_probe.py — доступность страницы для поисковых и ИИ-ботов (site-research, агент H, волна 2, 2026-09-24). | csv, fcntl, hashlib, html, playwright, requests, socket, time, urllib, urllib3,  | да | да | 2 | 6 |
| `99-raw/tools/ia_probe.py` | 1855 | ia_probe.py — структура многостраничного сайта по HTTP (агент G, волна 2 site-research, 2026-09-24). | gzip, hashlib, html, http, io, random, socket, ssl, statistics, threading, time, | да | да |  | 8 |
| `99-raw/tools/measure_ui.py` | 1214 | Измерить визуальный слой живой веб-страницы через headless-браузер (Playwright/Chromium). | color, hashlib, playwright, time | да | да |  | 2 |
| `99-raw/tools/orch_check.py` | 201 | Приёмочная проверка файлов site-research (оркестратор волн site, 24.09.2026; основа — orch_check.py оркестрато | subprocess, yaml |  | да |  | 8 |
| `99-raw/tools/page_accept.py` | 354 | page_accept.py — приёмка страницы с ИИ-ассетами в Chromium (агент J, волна 3, 23.09.2026). | PIL, contextlib, fcntl, http, io, numpy, playwright, scipy, socketserver, thread | да | да |  | 2 |
| `99-raw/tools/page_anatomy.py` | 2603 | page_anatomy.py — анатомия живой посадочной страницы или страницы сайта (агент M, волна 1 site-research, 2026- | PIL, base64, contextlib, csv, fcntl, html, http, io, playwright, signal, socket, | да | да | 3 | 13 |
| `99-raw/tools/page_gates.py` | 1078 | page_gates.py — единые ворота страницы по профилю бюджета (P v0, волна 2; K v1, волна 3; site-research, 2026-0 | copy, glob, html, yaml |  | да |  | 3 |
| `99-raw/tools/plan_to_assets.py` | 193 | plan_to_assets.py — каркас плана ассетов ai-media из медиа- и 3D-слотов page-plan (site-research, агент J, вол | csv, yaml |  | да |  | 1 |
| `99-raw/tools/render_fetch.py` | 107 | Скачать страницу через headless-браузер (Playwright/Chromium) и сохранить читаемый Markdown в 99-raw/cache/. | hashlib, playwright, subprocess | да | да |  | 1 |
| `99-raw/tools/site_brief_to_kimi.py` | 394 | site_brief_to_kimi.py — проекция site-brief (v0/v1) + page-plan (v1) в brief.yaml kimi (site-research, агент J | PIL, subprocess, yaml | да | да |  | 2 |
| `99-raw/tools/site_probe.py` | 446 | site_probe.py — замер живого 3D-сайта (агент A, волна 1). Дополняет 99-raw/tools/web_view.py --url. | PIL, playwright, time | да | да |  | 1 |
| `99-raw/tools/site_validate.py` | 1325 | site_validate.py — схемы и перекрёстные ссылки контрактов сайта (site-research, агент J, волна 3, 2026-09-24). | copy, jsonschema, referencing, shutil, tempfile, yaml |  | да |  | 6 |
| `99-raw/tools/sources_collect.py` | 1639 | Сводная библиография базы site-research: `90-sources/sources.tsv` и автоблок `90-sources/README.md`. | glob, io, shutil, tempfile |  | да | 1 | 56 |
| `99-raw/tools/transcribe_local.py` | 256 | Локальная транскрибация YouTube-видео или аудиофайла через Qwen3-ASR-1.7B (llama.cpp, CPU). | shutil, subprocess, time |  | да |  | 4 |
| `99-raw/tools/ui_audit.py` | 1474 | Объединённый прогон визуального QA страницы: измерение + сверка с токенами и порогами базы + отчёт. | color, math, playwright | да | да |  | 4 |
| `99-raw/tools/vocab_lint.py` | 339 | vocab_lint.py — проверка YAML, JSON и Markdown на идентификаторы вне словаря site-research (агент B, волна 1,  | csv, difflib, tempfile, yaml |  | да |  | 3 |
| `99-raw/tools/vtt2md.py` | 114 | Собирает 91-videos/transcripts/<id>.md из уже скачанных .vtt и .info.json без обращения к YouTube. | glob |  | да |  | 5 |
| `99-raw/tools/yt_dl.py` | 200 | Загрузка метаданных, субтитров и комментариев YouTube без видео и аудио, с паузами и обработкой HTTP 429. | glob, subprocess, time |  | да | 1 | 6 |
| `99-raw/tools/yt_transcript.py` | 210 | Субтитры и метаданные YouTube-видео без скачивания самого видео (через yt-dlp). | requests, yt_dlp | да | да |  | 2 |

Зашитые абсолютные пути (4 разных): `/home/mm/.nvm/versions/node/v24.21.0/bin/node`; `/home/mm/Документы/app-design/.locks/browser.lock`; `/home/mm/Документы/app-design/site-research/99-raw/tools/.locks/browser.lock`; `/home/mm/Документы/Как_избежать_нейрослопа_(гайд`

## Ссылки из переносимых файлов (md, данные, код)

| статус | число | смысл |
|---|---|---|
| ok | 3372 | цель переносится |
| to-excluded | 558 | цель есть, но не переносится (служебное, ассет, мусор) — сломается |
| to-kimi | 280 | ведёт в kimi-research (донор) — заменить при уборке |
| missing | 536 | цели нет уже сейчас (или путь условный) |
| outside | 2 | абсолютный путь вне базы |
| short-unresolved | 110 | адрес «NN/MM» не нашёл файла (часто — номер раздела) |

Сломаются — по источнику ссылки и типу цели:

| тип цели | из md | из данных | из кода | всего |
|---|---|---|---|---|
| служебное | 318 | 212 | 27 | 557 |
| прочее | 1 | 0 | 0 | 1 |

Примеры to-excluded:
- `00-glossary/README.md:4 → 99-raw/prompts/_common.md`
- `00-glossary/glossary.md:4 → 99-raw/reports/wave4-X-audit.md`
- `00-glossary/glossary.md:5 → 99-raw/reports/`
- `00-glossary/glossary.md:84 → 99-raw/notes/triad-contract-2026-09-24.md`
- `00-glossary/glossary.md:95 → 99-raw/notes/sync/`
- `00-glossary/glossary.md:410 → 99-raw/reports/`
- `00-glossary/glossary.md:414 → 99-raw/reports/wave4-X-audit.md`
- `00-glossary/glossary.md:416 → 99-raw/reports/`
- `01-foundations/01-how-visitors-decide.md:4 → 99-raw/cache/`
- `01-foundations/01-how-visitors-decide.md:365 → ../../ux-research/91-videos/digests/b2VdPF9svEU.md`
- `01-foundations/02-cro-evidence-and-folklore.md:4 → 99-raw/experiments/A/04-sample-size/`
- `01-foundations/02-cro-evidence-and-folklore.md:151 → 99-raw/experiments/A/04-sample-size/result.tsv`

Примеры missing:
- `01-foundations/01-how-visitors-decide.md:56 → 02-myths-and-misapplied-laws.md`
- `01-foundations/01-how-visitors-decide.md:120 → 02-length-goal-message-match.md`
- `01-foundations/01-how-visitors-decide.md:135 → 02-what-copy-changes-evidence.md`
- `01-foundations/01-how-visitors-decide.md:254 → 02-what-copy-changes-evidence.md`
- `01-foundations/01-how-visitors-decide.md:360 → 01-foundations/01-principles-and-laws.md`
- `01-foundations/01-how-visitors-decide.md:360 → 02-myths-and-misapplied-laws.md`
- `01-foundations/01-how-visitors-decide.md:361 → 03-layout-placement/03-hierarchy-and-attention.md`
- `01-foundations/01-how-visitors-decide.md:361 → 13-app-types/02-client-facing-app-playbook.md`
- `01-foundations/01-how-visitors-decide.md:362 → 06-feedback-states-motion/04-dark-patterns-and-ethics.md`
- `01-foundations/01-how-visitors-decide.md:362 → 11-ai-generated-ui/01-failure-modes-catalog.md`
- `01-foundations/01-how-visitors-decide.md:363 → 01-foundations/01-how-people-read-marketing-pages.md`
- `01-foundations/01-how-visitors-decide.md:363 → 02-what-copy-changes-evidence.md`

Примеры to-kimi:
- `01-foundations/01-how-visitors-decide.md:143 → kimi 07/01`
- `01-foundations/03-site-brief.md:34 → kimi 07/01`
- `01-foundations/03-site-brief.md:38 → kimi 07/01`
- `01-foundations/03-site-brief.md:70 → ../kimi-research/03-prompting/03-prompt-anatomy-k3.md`
- `01-foundations/03-site-brief.md:197 → ../../kimi-research/07-brief-handoff/03-references-brand-assets.md`
- `01-foundations/03-site-brief.md:214 → kimi 07/01`
- `01-foundations/03-site-brief.md:271 → kimi 07/01`
- `01-foundations/03-site-brief.md:275 → kimi 07/01`
- `01-foundations/03-site-brief.md:438 → kimi-research`
- `02-site-types/01-site-and-page-taxonomy.md:48 → kimi 07/01`
- `02-site-types/01-site-and-page-taxonomy.md:51 → kimi 07/01`
- `02-site-types/01-site-and-page-taxonomy.md:369 → ../kimi-research/99-raw/cache/repos/Nutlope__hallmark/`

Примеры outside:
- `06-multipage-ia/02-navigation-linking-i18n.md:483 → ../../`
- `PLAN.md:363 → ../`

## Входящие ссылки из соседних ресерчей

Всего 124: creative-research 110; text-research 12; claude-design-research 2. Самые цитируемые файлы: `site-research/10-playbooks-contracts/02-playbooks-landings.md` 15; `site-research` 12; `site-research/02-site-types/vocabulary.yaml` 7; `site-research/04-blocks/blocks.yaml` 6; `site-research/07-seo-geo-performance-analytics/page-gates.yaml` 6; `site-research/10-playbooks-contracts/examples/saas-okoshko/plans/home.yaml` 5; `site-research/10-playbooks-contracts/examples/lead-services-otves/plans/home.yaml` 5; `site-research/09-ai-generation-evaluation/ai-landing-markers.yaml` 4; `site-research/10-playbooks-contracts/examples/corporate-b2b-stalkon/plans/home.yaml` 4; `site-research/99-raw/notes/sync/W4-site-2026-09-25/README.md` 3

## Короткие адреса и указатели

- адресов «NN/MM» (свои и «<база> NN/MM»): 829, из них файл не найден: 110 — зависят от нумерации папок и файлов
- указателей «→ … §» в тексте: 792 — зависят от нумерации разделов внутри файлов

## Дубли утилит (md5) в других ресерчах

- `site-research/99-raw/tools/asset_inventory.py` = `ai-media-research/99-raw/tools/asset_inventory.py`, `creative-research/99-raw/tools/asset_inventory.py`
- `site-research/99-raw/tools/color.py` = `ai-media-research/99-raw/tools/color.py`, `creative-research/99-raw/tools/color.py`, `kimi-research/99-raw/tools/color.py`, `ui-research/99-raw/tools/color.py`
- `site-research/99-raw/tools/fetch.py` = `ai-media-research/99-raw/tools/fetch.py`, `blender-research/99-raw/tools/fetch.py`, `claude-design-research/99-raw/tools/fetch.py`, `creative-research/99-raw/tools/fetch.py`, `kimi-research/99-raw/tools/fetch.py`, `text-research/99-raw/tools/fetch.py`, `ui-research/99-raw/tools/fetch.py`, `ux-research/99-raw/tools/fetch.py`
- `site-research/99-raw/tools/render_fetch.py` = `ai-media-research/99-raw/tools/render_fetch.py`, `blender-research/99-raw/tools/render_fetch.py`, `claude-design-research/99-raw/tools/render_fetch.py`, `creative-research/99-raw/tools/render_fetch.py`, `kimi-research/99-raw/tools/render_fetch.py`, `text-research/99-raw/tools/render_fetch.py`, `ui-research/99-raw/tools/render_fetch.py`, `ux-research/99-raw/tools/render_fetch.py`
- `site-research/99-raw/tools/site_probe.py` = `ai-media-research/99-raw/tools/site_probe.py`, `blender-research/99-raw/tools/site_probe.py`, `creative-research/99-raw/tools/site_probe.py`, `kimi-research/99-raw/tools/site_probe.py`, `text-research/99-raw/tools/site_probe.py`
- `site-research/99-raw/tools/vtt2md.py` = `ai-media-research/99-raw/tools/vtt2md.py`, `claude-design-research/99-raw/tools/vtt2md.py`, `creative-research/99-raw/tools/vtt2md.py`, `kimi-research/99-raw/tools/vtt2md.py`, `text-research/99-raw/tools/vtt2md.py`
- `site-research/99-raw/tools/yt_dl.py` = `ai-media-research/99-raw/tools/yt_dl.py`, `claude-design-research/99-raw/tools/yt_dl.py`, `creative-research/99-raw/tools/yt_dl.py`, `kimi-research/99-raw/tools/yt_dl.py`, `text-research/99-raw/tools/yt_dl.py`
- `site-research/99-raw/tools/yt_transcript.py` = `ai-media-research/99-raw/tools/yt_transcript.py`, `blender-research/99-raw/tools/yt_transcript.py`, `claude-design-research/99-raw/tools/yt_transcript.py`, `creative-research/99-raw/tools/yt_transcript.py`, `kimi-research/99-raw/tools/yt_transcript.py`, `text-research/99-raw/tools/yt_transcript.py`
- `site-research/99-raw/tools/transcribe_local.py` = `blender-research/99-raw/tools/transcribe_local.py`, `creative-research/99-raw/tools/transcribe_local.py`, `text-research/99-raw/tools/transcribe_local.py`
- `site-research/99-raw/tools/measure_ui.py` = `creative-research/99-raw/tools/measure_ui.py`, `kimi-research/99-raw/tools/measure_ui.py`, `ui-research/99-raw/tools/measure_ui.py`
- `site-research/99-raw/tools/page_accept.py` = `creative-research/99-raw/tools/page_accept.py`
- `site-research/99-raw/tools/ui_audit.py` = `creative-research/99-raw/tools/ui_audit.py`, `kimi-research/99-raw/tools/ui_audit.py`, `ui-research/99-raw/tools/ui_audit.py`

## Kimi / K3

783 строк в 58 переносимых файлах. Топ: `02-site-types/crosswalk.tsv` 141; `01-foundations/03-site-brief.md` 56; `PLAN.md` 52; `09-ai-generation-evaluation/01-generators-and-ai-landing-markers.md` 45; `01-foundations/site-brief.kimi-map.tsv` 40; `10-playbooks-contracts/01-procedure-brief-to-pages.md` 36; `README.md` 32; `09-ai-generation-evaluation/ai-landing-markers.yaml` 30; `09-ai-generation-evaluation/02-site-checklist.md` 24; `09-ai-generation-evaluation/site-checklist.yaml` 23

## «Внешнее» — оценка объёма финальной уборки

- ссылок в исключаемое (служебное и т. п.): 558; строк с упоминанием служебных папок: 395
- ссылок в соседние ресерчи: 1377 (из них в kimi: 280)
- меток роликов `[V:…]`: 158
- строк про Kimi/K3: 783
