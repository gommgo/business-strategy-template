# creative-research — инвентарь для фазы 2

Скрипт `_skill-build/tools/inventory.py`, 26.09.2026 17:50. Токены — Opus 5.5 по калибровке.
Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, service, forbidden — нет.

## Классы файлов

| класс | файлов | МБ | ~токенов | переносим? |
|---|---|---|---|---|
| prose | 54 | 1.6 | 587K | да |
| data | 128 | 1.5 | 613K | да |
| code | 143 | 0.5 | 208K | да |
| tool | 24 | 1.1 | 514K | да |
| root-doc | 3 | 0.3 | 111K | да |
| asset | 4910 | 5074.7 | 0K | нет |
| bundle | 8 | 0.8 | 390K | нет |
| junk | 16495 | 506.2 | 0K | нет |
| service | 1925 | 239.3 | 0K | нет |
| **итого переносим** | 352 | 5.1 | 2034K | |
| **итого не переносим** | 23338 | 5821.0 | — | |

## Папки верхнего уровня

| папка | файлов | МБ | ~токенов текста | состав |
|---|---|---|---|---|
| (корень) | 3 | 0.3 | 111K | root-doc 3 |
| 00-glossary | 2 | 0.1 | 29K | prose 2 |
| 01-creative-direction | 13 | 0.5 | 155K | prose 4, data 9 |
| 02-references-moodboards | 14 | 0.2 | 85K | prose 5, data 3, asset 5, junk 1 |
| 03-live-sites-measured | 121 | 6.9 | 131K | prose 3, data 32, asset 86 |
| 04-visual-language | 7 | 0.2 | 74K | prose 4, data 2, code 1 |
| 05-motion | 4 | 0.2 | 67K | prose 4 |
| 06-effects-catalog | 218 | 2.3 | 427K | prose 7, data 48, code 132, asset 24, bundle 7 |
| 07-stack-implementation | 4 | 0.2 | 66K | prose 3, data 1 |
| 08-uniqueness-anti-slop | 4 | 0.3 | 84K | prose 3, data 1 |
| 09-ai-execution-evaluation | 18 | 0.6 | 208K | prose 5, data 13 |
| 10-recipes | 62 | 1.6 | 473K | prose 14, data 19, code 10, asset 17, bundle 1, junk 1 |
| 90-sources | 2 | 0.1 | 0K | service 2 |
| 91-videos | 3116 | 299.1 | 0K | asset 3060, service 56 |
| 99-raw | 20102 | 5513.5 | 514K | tool 24, asset 1718, junk 16493, service 1867 |

## Служебные папки (группами, топ по размеру)

| группа | файлов | МБ |
|---|---|---|
| 99-raw/youtube | 156 | 174.5 |
| 99-raw/experiments | 1338 | 53.2 |
| 99-raw/cache | 267 | 6.6 |
| 99-raw/notes | 53 | 2.4 |
| 91-videos/transcripts | 18 | 0.7 |
| 99-raw/reports | 19 | 0.6 |
| 99-raw/prompts | 31 | 0.5 |
| 91-videos/digests | 21 | 0.4 |
| 91-videos/frames | 15 | 0.2 |
| 90-sources/sources.tsv | 1 | 0.1 |
| 99-raw/handoff-to-neighbours.md | 1 | 0.1 |
| 91-videos/catalog.md | 1 | 0.0 |
| 99-raw/tools | 1 | 0.0 |
| 90-sources/README.md | 1 | 0.0 |
| 99-raw/skills-map.md | 1 | 0.0 |

## Серые зоны (решить при переносе)

- **Крупные текстовые файлы > 1 МБ**: 0
- **PLAN.md (план ресерча)**: 1 — PLAN.md (157 КБ)
- **Индекс источников в 90-sources**: 2 — 90-sources/README.md; 90-sources/sources.tsv
- **Служебные файлы, на которые ссылается переносимое (ссылок)**: 188 — creative-research/99-raw/tools/README.md (13); creative-research/99-raw/handoff-to-neighbours.md (10); creative-research/99-raw/reports/wave4-X-audit.md (8); creative-research/99-raw/experiments/I/01-schemas/spec_check.py (8); creative-research/90-sources/README.md (7); creative-research/99-raw/reports/wave3-J-report.md (6); creative-research/99-raw/notes/triad-contract-2026-09-24.md (6); creative-research/90-sources (6); creative-research/99-raw/prompts/NEXT-SESSION-orchestrator.md (6); creative-research/99-raw/experiments/A/01-art-direction-examples/ad_check.py (5); creative-research/99-raw/experiments/F/07-yaml/build_effects.py (5); creative-research/91-videos/catalog.md (5); … ещё 176
- **Код, который ссылается на ассеты (без них сломается; число ссылок)**: 54 — 04-visual-language/marketing-tokens.css (1); 06-effects-catalog/lab/_shared/lab.css (4); 06-effects-catalog/lab/aurora-css/index.html (4); 06-effects-catalog/lab/button-expand-label/index.html (4); 06-effects-catalog/lab/card-flip-3d/index.html (4); 06-effects-catalog/lab/cinemagraph/index.html (5); 06-effects-catalog/lab/counter-up/index.html (4); 06-effects-catalog/lab/cursor-accent/index.html (4); 06-effects-catalog/lab/custom-cursor/index.html (6); 06-effects-catalog/lab/details-accordion/index.html (4); 06-effects-catalog/lab/dialog-entry-exit/index.html (4); 06-effects-catalog/lab/glass-panel/index.html (4); … ещё 42

## Код и утилиты (167 файлов)

| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |
|---|---|---|---|---|---|---|---|
| `99-raw/tools/asset_inventory.py` | 699 | asset_inventory.py — инвентарь визуальных ассетов живой страницы (агент A, волна 1 ai-media-research, 2026-09- | PIL, io, playwright, time, urllib | да | да |  |  |
| `99-raw/tools/check_links.py` | 1653 | Проверка перекрёстных ссылок, меток и структуры базы creative-research. | glob, shutil, tempfile |  | да |  | 75 |
| `99-raw/tools/color.py` | 176 | Расчёты цвета для интерфейсов без внешних зависимостей (написано агентом A волны 1, проверено по калькулятору  | math |  | да |  | 1 |
| `99-raw/tools/ctx_watch.py` | 146 | Сторож контекста агентов creative-research (копия утилиты оркестратора волн text-research от 24.09.2026; ищет  | glob, time |  | да |  | 4 |
| `99-raw/tools/effect_bench.py` | 893 | effect_bench.py — прогон лабораторных страниц эффектов (06-effects-catalog/lab/<id>/) в Chromium и WebKit. | PIL, brotli, fcntl, gzip, http, importlib, io, math, mimetypes, numpy, playwrigh | да | да | 1 | 1 |
| `99-raw/tools/effects_probe.py` | 1185 | effects_probe.py — замер эффектной страницы (creative-research, волна 1, агент C, 2026-09-24). | PIL, brotli, io, math, numpy, playwright, struct, time, zlib | да | да | 2 | 3 |
| `99-raw/tools/extract_for_audit.py` | 142 | Извлечения для аудитора X и синтезатора S (оркестратор волн creative-research, 24.09.2026; копия утилиты | yaml |  | да |  | 7 |
| `99-raw/tools/fetch.py` | 77 | Скачать страницу и сохранить читаемый текст (Markdown) в 99-raw/cache/. | bs4, hashlib, requests, subprocess | да | да |  | 1 |
| `99-raw/tools/marketing_audit.py` | 1234 | marketing_audit.py — профиль визуальных проверок `marketing` поверх ui_audit.py (creative-research, волна 3, а | PIL, color, fcntl, functools, http, io, math, numpy, playwright, signal, sockets | да | да | 1 | 7 |
| `99-raw/tools/measure_ui.py` | 1214 | Измерить визуальный слой живой веб-страницы через headless-браузер (Playwright/Chromium). | color, hashlib, playwright, time | да | да |  | 2 |
| `99-raw/tools/motion_check.py` | 2380 | motion_check.py — цикл проверки сборки: запись → кадры → метрики → сверка с motion-spec → ворота эффектов → от | PIL, base64, brotli, fcntl, functools, gzip, http, io, math, mimetypes, numpy, p | да | да | 1 | 5 |
| `99-raw/tools/orch_check.py` | 209 | Приёмочная проверка файлов creative-research (оркестратор волн, 24.09.2026; адаптация | subprocess, yaml |  | да |  | 10 |
| `99-raw/tools/page_accept.py` | 354 | page_accept.py — приёмка страницы с ИИ-ассетами в Chromium (агент J, волна 3, 23.09.2026). | PIL, contextlib, fcntl, http, io, numpy, playwright, scipy, socketserver, thread | да | да |  | 2 |
| `99-raw/tools/refs_client.py` | 3534 | refs_client.py — клиент референсов creative-research. | PIL, color, contextlib, fcntl, glob, hashlib, html, io, math, numpy, playwright, | да | да | 4 | 4 |
| `99-raw/tools/render_fetch.py` | 107 | Скачать страницу через headless-браузер (Playwright/Chromium) и сохранить читаемый Markdown в 99-raw/cache/. | hashlib, playwright, subprocess | да | да |  | 1 |
| `99-raw/tools/scroll_record.py` | 295 | scroll_record.py — запись прокрутки страницы и движение в паузах (creative-research, волна 1, агент C, 2026-09 | PIL, glob, io, math, numpy, playwright, shutil, subprocess, tempfile, time | да | да |  | 1 |
| `99-raw/tools/site_probe.py` | 446 | site_probe.py — замер живого 3D-сайта (агент A, волна 1). Дополняет 99-raw/tools/web_view.py --url. | PIL, playwright, time | да | да |  | 1 |
| `99-raw/tools/sources_collect.py` | 1609 | Сводная библиография базы creative-research: `90-sources/sources.tsv` и автоблок `90-sources/README.md`. | glob, io, shutil, tempfile |  | да | 1 | 53 |
| `99-raw/tools/transcribe_local.py` | 256 | Локальная транскрибация YouTube-видео или аудиофайла через Qwen3-ASR-1.7B (llama.cpp, CPU). | shutil, subprocess, time |  | да |  | 4 |
| `99-raw/tools/ui_audit.py` | 1474 | Объединённый прогон визуального QA страницы: измерение + сверка с токенами и порогами базы + отчёт. | color, math, playwright | да | да |  | 4 |
| `99-raw/tools/vtt2md.py` | 114 | Собирает 91-videos/transcripts/<id>.md из уже скачанных .vtt и .info.json без обращения к YouTube. | glob |  | да |  | 5 |
| `99-raw/tools/yt_dl.py` | 200 | Загрузка метаданных, субтитров и комментариев YouTube без видео и аудио, с паузами и обработкой HTTP 429. | glob, subprocess, time |  | да | 1 | 6 |
| `99-raw/tools/yt_frames.py` | 312 | Видео YouTube → кадры для «просмотра глазами» агентом (kimi-research, оркестратор, 23.09.2026). | PIL, glob, subprocess, time |  | да | 1 | 6 |
| `99-raw/tools/yt_transcript.py` | 210 | Субтитры и метаданные YouTube-видео без скачивания самого видео (через yt-dlp). | requests, yt_dlp | да | да |  | 2 |

Прочий код (143 файлов) по папкам: `06-effects-catalog/lab` 132, `10-recipes/examples` 10, `04-visual-language/marketing-tokens.css` 1

Зашитые абсолютные пути (6 разных): `/home/mm/.nvm/versions/node/v24.21.0/bin/node`; `/home/mm/Документы/app-design/.locks/browser-refs.lock`; `/home/mm/Документы/app-design/.locks/browser.lock`; `/home/mm/Документы/app-design/creative-research/99-raw/tools/.locks/browser.lock`; `/home/mm/Документы/app-design/creative-research/99-raw/tools/refs_client.py`; `/home/mm/Документы/Как_избежать_нейрослопа_(гайд`

## Ссылки из переносимых файлов (md, данные, код)

| статус | число | смысл |
|---|---|---|
| ok | 2239 | цель переносится |
| to-excluded | 614 | цель есть, но не переносится (служебное, ассет, мусор) — сломается |
| to-kimi | 0 | ведёт в kimi-research (донор) — заменить при уборке |
| missing | 551 | цели нет уже сейчас (или путь условный) |
| outside | 1 | абсолютный путь вне базы |
| short-unresolved | 169 | адрес «NN/MM» не нашёл файла (часто — номер раздела) |

Сломаются — по источнику ссылки и типу цели:

| тип цели | из md | из данных | из кода | всего |
|---|---|---|---|---|
| ассет | 8 | 7 | 227 | 242 |
| служебное | 306 | 39 | 22 | 367 |
| прочее | 5 | 0 | 0 | 5 |

Примеры to-excluded:
- `00-glossary/README.md:7 → 99-raw/reports/wave4-X-audit.md`
- `00-glossary/glossary.md:4 → 99-raw/reports/wave4-X-audit.md`
- `00-glossary/glossary.md:5 → 99-raw/reports/`
- `00-glossary/glossary.md:5 → 99-raw/notes/wave4/extracts/reports.md`
- `00-glossary/glossary.md:6 → 99-raw/reports/wave3-J-report.md`
- `00-glossary/glossary.md:8 → 91-videos/`
- `00-glossary/glossary.md:158 → 91-videos/digests/_index-W1.md`
- `00-glossary/glossary.md:180 → 91-videos/digests/_index-W1.md`
- `00-glossary/glossary.md:433 → ../site-research/99-raw/notes/sync/W4-site-2026-09-25/README.md`
- `00-glossary/glossary.md:440 → 99-raw/reports/wave4-X-audit.md`
- `00-glossary/glossary.md:443 → 99-raw/notes/wave4/extracts/reports.md`
- `00-glossary/glossary.md:445 → 99-raw/reports/wave3-J-report.md`

Примеры missing:
- `00-glossary/glossary.md:323 → refs/README.md`
- `01-creative-direction/01-concept-and-directions.md:210 → ../kimi-research/05-reviews-practice/03-default-look-k3.md`
- `01-creative-direction/01-concept-and-directions.md:517 → 01-foundations/site-brief.schema.json`
- `01-creative-direction/01-concept-and-directions.md:517 → 03-site-brief.md`
- `01-creative-direction/01-concept-and-directions.md:518 → 04-blocks/page-plan.schema.json`
- `01-creative-direction/01-concept-and-directions.md:519 → 02-site-types/vocabulary.yaml`
- `01-creative-direction/01-concept-and-directions.md:520 → 07-brief-handoff/01-from-app-description-to-brief.md`
- `01-creative-direction/01-concept-and-directions.md:521 → 03-prompting/04-template-library.md`
- `01-creative-direction/01-concept-and-directions.md:522 → 03-prompting/01-official-guidance.md`
- `01-creative-direction/01-concept-and-directions.md:523 → 07-brief-handoff/03-references-brand-assets.md`
- `01-creative-direction/01-concept-and-directions.md:523 → templates/brand.json`
- `01-creative-direction/01-concept-and-directions.md:524 → ../kimi-research/99-raw/cache/repos/`

Примеры outside:
- `PLAN.md:436 → ../`

## Входящие ссылки из соседних ресерчей

Всего 137: site-research 81; blender-research 39; claude-design-research 8; text-research 6; ux-research 3. Самые цитируемые файлы: `creative-research/01-creative-direction/ambition-levels.yaml` 23; `creative-research` 14; `creative-research/04-visual-language/03-color-surfaces-product.md` 13; `creative-research/PLAN.md` 8; `creative-research/05-motion/01-motion-principles-and-access.md` 7; `creative-research/07-stack-implementation/01-stack-choice.md` 5; `creative-research/99-raw/experiments/J/04-light-pass/src/scene.js` 4; `creative-research/99-raw/tools/motion_check.py` 4; `creative-research/99-raw/experiments/E/02-scroll-scene/README.md` 4; `creative-research/99-raw/experiments/E/01-lcp-reveal/README.md` 4

## Короткие адреса и указатели

- адресов «NN/MM» (свои и «<база> NN/MM»): 1349, из них файл не найден: 169 — зависят от нумерации папок и файлов
- указателей «→ … §» в тексте: 751 — зависят от нумерации разделов внутри файлов

## Дубли утилит (md5) в других ресерчах

- `creative-research/99-raw/tools/asset_inventory.py` = `ai-media-research/99-raw/tools/asset_inventory.py`, `site-research/99-raw/tools/asset_inventory.py`
- `creative-research/99-raw/tools/color.py` = `ai-media-research/99-raw/tools/color.py`, `site-research/99-raw/tools/color.py`, `ui-research/99-raw/tools/color.py`
- `creative-research/99-raw/tools/fetch.py` = `ai-media-research/99-raw/tools/fetch.py`, `blender-research/99-raw/tools/fetch.py`, `claude-design-research/99-raw/tools/fetch.py`, `site-research/99-raw/tools/fetch.py`, `text-research/99-raw/tools/fetch.py`, `ui-research/99-raw/tools/fetch.py`, `ux-research/99-raw/tools/fetch.py`
- `creative-research/99-raw/tools/render_fetch.py` = `ai-media-research/99-raw/tools/render_fetch.py`, `blender-research/99-raw/tools/render_fetch.py`, `claude-design-research/99-raw/tools/render_fetch.py`, `site-research/99-raw/tools/render_fetch.py`, `text-research/99-raw/tools/render_fetch.py`, `ui-research/99-raw/tools/render_fetch.py`, `ux-research/99-raw/tools/render_fetch.py`
- `creative-research/99-raw/tools/site_probe.py` = `ai-media-research/99-raw/tools/site_probe.py`, `blender-research/99-raw/tools/site_probe.py`, `site-research/99-raw/tools/site_probe.py`, `text-research/99-raw/tools/site_probe.py`
- `creative-research/99-raw/tools/vtt2md.py` = `ai-media-research/99-raw/tools/vtt2md.py`, `claude-design-research/99-raw/tools/vtt2md.py`, `site-research/99-raw/tools/vtt2md.py`, `text-research/99-raw/tools/vtt2md.py`
- `creative-research/99-raw/tools/yt_dl.py` = `ai-media-research/99-raw/tools/yt_dl.py`, `claude-design-research/99-raw/tools/yt_dl.py`, `site-research/99-raw/tools/yt_dl.py`, `text-research/99-raw/tools/yt_dl.py`
- `creative-research/99-raw/tools/yt_transcript.py` = `ai-media-research/99-raw/tools/yt_transcript.py`, `blender-research/99-raw/tools/yt_transcript.py`, `claude-design-research/99-raw/tools/yt_transcript.py`, `site-research/99-raw/tools/yt_transcript.py`, `text-research/99-raw/tools/yt_transcript.py`
- `creative-research/99-raw/tools/transcribe_local.py` = `blender-research/99-raw/tools/transcribe_local.py`, `site-research/99-raw/tools/transcribe_local.py`, `text-research/99-raw/tools/transcribe_local.py`
- `creative-research/99-raw/tools/measure_ui.py` = `site-research/99-raw/tools/measure_ui.py`, `ui-research/99-raw/tools/measure_ui.py`
- `creative-research/99-raw/tools/page_accept.py` = `site-research/99-raw/tools/page_accept.py`
- `creative-research/99-raw/tools/ui_audit.py` = `site-research/99-raw/tools/ui_audit.py`, `ui-research/99-raw/tools/ui_audit.py`

## Kimi / K3

806 строк в 75 переносимых файлах. Топ: `08-uniqueness-anti-slop/cliche-registry.yaml` 92; `08-uniqueness-anti-slop/02-uniqueness-and-variation.md` 53; `02-references-moodboards/03-moodboard-and-handoff.md` 50; `PLAN.md` 48; `01-creative-direction/drafts-for-site/site-brief-creative-fields.yaml` 47; `09-ai-execution-evaluation/02-motion-spec-storyboard-handoff.md` 41; `01-creative-direction/01-concept-and-directions.md` 38; `README.md` 30; `08-uniqueness-anti-slop/01-cliche-policy.md` 29; `01-creative-direction/02-art-direction-document.md` 27

## «Внешнее» — оценка объёма финальной уборки

- ссылок в исключаемое (служебное и т. п.): 614; строк с упоминанием служебных папок: 451
- ссылок в соседние ресерчи: 758 (из них в kimi: 0)
- меток роликов `[V:…]`: 142
- строк про Kimi/K3: 806
