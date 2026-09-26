# text-research — инвентарь для фазы 2

Скрипт `_skill-build/tools/inventory.py`, 26.09.2026 17:50. Токены — Opus 5.5 по калибровке.
Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, service, forbidden — нет.

## Классы файлов

| класс | файлов | МБ | ~токенов | переносим? |
|---|---|---|---|---|
| prose | 52 | 1.9 | 623K | да |
| data | 55 | 4.3 | 1891K | да |
| tool | 19 | 1.0 | 457K | да |
| root-doc | 3 | 0.3 | 98K | да |
| asset | 234 | 47.8 | 0K | нет |
| junk | 2017 | 49.3 | 0K | нет |
| service | 3523 | 312.4 | 0K | нет |
| **итого переносим** | 129 | 7.6 | 3070K | |
| **итого не переносим** | 5774 | 409.5 | — | |

## Папки верхнего уровня

| папка | файлов | МБ | ~токенов текста | состав |
|---|---|---|---|---|
| (корень) | 3 | 0.3 | 98K | root-doc 3 |
| 00-glossary | 2 | 0.1 | 19K | prose 2 |
| 01-foundations | 5 | 0.2 | 59K | prose 4, data 1 |
| 02-strategy-messaging | 18 | 0.6 | 187K | prose 6, data 12 |
| 03-corpus-measured | 7 | 2.6 | 1337K | prose 4, data 3 |
| 04-copy-by-block | 6 | 0.4 | 143K | prose 5, data 1 |
| 05-voice-editorial | 9 | 0.4 | 115K | prose 5, data 4 |
| 06-anti-slop | 16 | 0.5 | 154K | prose 3, data 13 |
| 07-seo-geo-copy | 7 | 0.2 | 72K | prose 4, data 3 |
| 08-russian-legal-typography | 5 | 0.3 | 85K | prose 3, data 2 |
| 09-ai-generation-evaluation | 14 | 0.4 | 140K | prose 12, data 2 |
| 10-templates-recipes | 18 | 0.6 | 202K | prose 4, data 14 |
| 90-sources | 2 | 0.1 | 0K | service 2 |
| 91-videos | 42 | 1.8 | 0K | service 42 |
| 99-raw | 5749 | 408.6 | 457K | tool 19, asset 234, junk 2017, service 3479 |

## Служебные папки (группами, топ по размеру)

| группа | файлов | МБ |
|---|---|---|
| 99-raw/youtube | 225 | 225.0 |
| 99-raw/cache | 1781 | 54.5 |
| 99-raw/experiments | 1371 | 26.9 |
| 99-raw/notes | 44 | 2.6 |
| 91-videos/transcripts | 20 | 1.3 |
| 99-raw/reports | 20 | 0.8 |
| 99-raw/prompts | 35 | 0.5 |
| 91-videos/digests | 20 | 0.5 |
| 90-sources/sources.tsv | 1 | 0.1 |
| 91-videos/catalog.md | 1 | 0.1 |
| 99-raw/tools | 1 | 0.1 |
| 99-raw/handoff-to-neighbours.md | 1 | 0.0 |
| 90-sources/README.md | 1 | 0.0 |
| 91-videos/catalog.tsv | 1 | 0.0 |
| 99-raw/skills-map.md | 1 | 0.0 |

## Серые зоны (решить при переносе)

- **Крупные текстовые файлы > 1 МБ**: 1 — 03-corpus-measured/measurements.tsv (2.3 МБ)
- **PLAN.md (план ресерча)**: 1 — PLAN.md (142 КБ)
- **Индекс источников в 90-sources**: 2 — 90-sources/README.md; 90-sources/sources.tsv
- **Служебные файлы, на которые ссылается переносимое (ссылок)**: 386 — text-research/99-raw/notes/temp-vocabulary-v0.yaml (33); text-research/99-raw/tools/README.md (24); text-research/99-raw/experiments/F/05-style-sheet-pairs/pairs.yaml (18); text-research/91-videos/digests/TUMjnmfsPeM.md (15); text-research/91-videos/digests/1UVkeqxuNRs.md (12); text-research/99-raw/cache (11); text-research/91-videos/digests/0MRJVoiqpXg.md (11); text-research/99-raw/experiments/E/04-copy-deck-v0/deck-otves-lead-v0.yaml (11); text-research/91-videos/digests/F_urkVueszI.md (10); text-research/99-raw/experiments/I/04-chain-manual/README.md (10); text-research/99-raw/experiments/E/04-copy-deck-v0/deck-kvarts-preorder-v0.yaml (10); text-research/99-raw/experiments/A/02-readability-10-texts/pairs/pairs.tsv (10); … ещё 374
- **Код, который ссылается на ассеты (без них сломается; число ссылок)**: 0

## Код и утилиты (19 файлов)

| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |
|---|---|---|---|---|---|---|---|
| `99-raw/tools/before_after_build.py` | 649 | before_after_build.py — сборка 10-templates-recipes/before-after.tsv: пары «до / после» по маркетинговым жанра | difflib, glob, io, shutil, tempfile, yaml |  | да |  | 28 |
| `99-raw/tools/check_links.py` | 1645 | Проверка перекрёстных ссылок, меток и структуры базы text-research. | glob, shutil, tempfile |  | да |  | 73 |
| `99-raw/tools/claims_check.py` | 2790 | claims_check.py — сверка текстов сайта с белым списком фактов (facts.yaml): ядро «контура честности» text-rese | copy, difflib, fnmatch, html, tempfile, unicodedata, yaml |  | да |  | 5 |
| `99-raw/tools/copy_extract.py` | 1407 | copy_extract.py — страница (URL или сохранённый HTML) → структурированный текст по слотам (JSON). | PIL, fcntl, hashlib, io, playwright, time | да | да | 2 | 8 |
| `99-raw/tools/copy_lint.py` | 2004 | copy_lint.py — линтер маркетинговых текстов RU/EN по жанрам. | dataclasses, fnmatch, html, math, pymorphy3, yaml |  | да |  | 9 |
| `99-raw/tools/copy_metrics.py` | 697 | copy_metrics.py — метрики текста страницы по жанрам и слотам (JSON извлечения → строки measurements.tsv). | copy_lint, csv, math, statistics, subprocess, tempfile, yaml |  | да |  | 6 |
| `99-raw/tools/copydeck.py` | 3731 | copydeck.py — copy deck text-research: проверка формата, сверка с фактами, линтер, экспорт в пакет kimi и обра | copy, copy_lint, fnmatch, hashlib, importlib, jsonschema, random, shutil, subpro |  | да |  | 5 |
| `99-raw/tools/ctx_watch.py` | 127 | Сторож контекста агентов (оркестратор волн text-research, 24.09.2026). | glob, time |  | да |  | 4 |
| `99-raw/tools/extract_for_audit.py` | 139 | Извлечения для аудитора X и синтезатора S (оркестратор волн text-research, 24.09.2026). | yaml |  | да |  | 7 |
| `99-raw/tools/fetch.py` | 77 | Скачать страницу и сохранить читаемый текст (Markdown) в 99-raw/cache/. | bs4, hashlib, requests, subprocess | да | да |  | 1 |
| `99-raw/tools/orch_check.py` | 186 | Приёмочная проверка файлов text-research (оркестратор волн, 24.09.2026). | subprocess, yaml |  | да |  | 8 |
| `99-raw/tools/render_fetch.py` | 107 | Скачать страницу через headless-браузер (Playwright/Chromium) и сохранить читаемый Markdown в 99-raw/cache/. | hashlib, playwright, subprocess | да | да |  | 1 |
| `99-raw/tools/site_probe.py` | 446 | site_probe.py — замер живого 3D-сайта (агент A, волна 1). Дополняет 99-raw/tools/web_view.py --url. | PIL, playwright, time | да | да |  | 1 |
| `99-raw/tools/sources_collect.py` | 1542 | Сводная библиография базы text-research: `90-sources/sources.tsv` и автоблок `90-sources/README.md`. | glob, io, shutil, tempfile |  | да | 1 | 52 |
| `99-raw/tools/transcribe_local.py` | 256 | Локальная транскрибация YouTube-видео или аудиофайла через Qwen3-ASR-1.7B (llama.cpp, CPU). | shutil, subprocess, time |  | да |  | 4 |
| `99-raw/tools/ux_dict_to_yaml.py` | 285 | ux_dict_to_yaml.py — конвертер словарей ux 07/06 (Markdown-таблицы) в YAML-правила copy_lint.py. | hashlib, yaml |  | да |  | 2 |
| `99-raw/tools/vtt2md.py` | 114 | Собирает 91-videos/transcripts/<id>.md из уже скачанных .vtt и .info.json без обращения к YouTube. | glob |  | да |  | 5 |
| `99-raw/tools/yt_dl.py` | 200 | Загрузка метаданных, субтитров и комментариев YouTube без видео и аудио, с паузами и обработкой HTTP 429. | glob, subprocess, time |  | да | 1 | 6 |
| `99-raw/tools/yt_transcript.py` | 210 | Субтитры и метаданные YouTube-видео без скачивания самого видео (через yt-dlp). | requests, yt_dlp | да | да |  | 2 |

Зашитые абсолютные пути (3 разных): `/home/mm/.nvm/versions/node/v24.21.0/bin/node`; `/home/mm/Документы/app-design/.locks/browser.lock`; `/home/mm/Документы/Как_избежать_нейрослопа_(гайд`

## Ссылки из переносимых файлов (md, данные, код)

| статус | число | смысл |
|---|---|---|
| ok | 2194 | цель переносится |
| to-excluded | 733 | цель есть, но не переносится (служебное, ассет, мусор) — сломается |
| to-kimi | 0 | ведёт в kimi-research (донор) — заменить при уборке |
| missing | 448 | цели нет уже сейчас (или путь условный) |
| outside | 6 | абсолютный путь вне базы |
| short-unresolved | 36 | адрес «NN/MM» не нашёл файла (часто — номер раздела) |

Сломаются — по источнику ссылки и типу цели:

| тип цели | из md | из данных | из кода | всего |
|---|---|---|---|---|
| служебное | 324 | 370 | 38 | 732 |
| прочее | 1 | 0 | 0 | 1 |

Примеры to-excluded:
- `00-glossary/README.md:28 → 99-raw/reports/wave4-X-audit.md`
- `00-glossary/README.md:32 → 99-raw/experiments/S2/01-glossary-build/`
- `00-glossary/glossary.md:4 → 99-raw/reports/`
- `00-glossary/glossary.md:4 → 99-raw/reports/wave4-X-audit.md`
- `00-glossary/glossary.md:312 → 99-raw/notes/temp-vocabulary-v0.yaml`
- `01-foundations/01-how-people-read-marketing-pages.md:4 → 99-raw/experiments/A/01-nng1997-recompute/`
- `01-foundations/01-how-people-read-marketing-pages.md:260 → 99-raw/experiments/A/03-reading-numbers-table/numbers.tsv`
- `01-foundations/01-how-people-read-marketing-pages.md:360 → ../../ux-research/91-videos/digests/AVKz9ZYoxgo.md`
- `01-foundations/01-how-people-read-marketing-pages.md:360 → ../../ux-research/91-videos/transcripts/AVKz9ZYoxgo.md`
- `01-foundations/02-what-copy-changes-evidence.md:4 → 99-raw/experiments/A/01-nng1997-recompute/`
- `01-foundations/02-what-copy-changes-evidence.md:231 → ../../ux-research/91-videos/digests/vxGrL3YSBvw.md`
- `01-foundations/02-what-copy-changes-evidence.md:342 → 91-videos/digests/`

Примеры missing:
- `00-glossary/README.md:9 → 01-foundations/01–03`
- `00-glossary/README.md:10 → 02-strategy-messaging/01–02`
- `00-glossary/README.md:11 → 02-strategy-messaging/03–04`
- `00-glossary/README.md:17 → 08-russian-legal-typography/01`
- `00-glossary/README.md:18 → 08-russian-legal-typography/02`
- `00-glossary/glossary.md:322 → examples/facts-kvarts.yaml`
- `01-foundations/01-how-people-read-marketing-pages.md:4 → 02-readability-10-texts/`
- `01-foundations/01-how-people-read-marketing-pages.md:4 → 03-reading-numbers-table/`
- `01-foundations/01-how-people-read-marketing-pages.md:8 → 02-myths-and-misapplied-laws.md`
- `01-foundations/01-how-people-read-marketing-pages.md:361 → 02-myths-and-misapplied-laws.md`
- `01-foundations/02-what-copy-changes-evidence.md:4 → 02-readability-10-texts/`
- `01-foundations/03-schools-formulas-myths.md:138 → ../../site-research/03-page-structure/01`

Примеры outside:
- `03-corpus-measured/01-corpus-method.md:396 → /home/mm/Документы/Как_избежать_нейрослопа_(гайд).md`
- `06-anti-slop/01-text-slop-markers-by-genre.md:258 → /home/mm/Документы/Как_избежать_нейрослопа_(гайд).md`
- `06-anti-slop/01-text-slop-markers-by-genre.md:434 → /home/mm/Документы/Как_избежать_нейрослопа_(гайд).md`
- `06-anti-slop/02-linter-spec-and-profiles.md:488 → /home/mm/Документы/Как_избежать_нейрослопа_(гайд).md`
- `08-russian-legal-typography/02-typography-for-marketing.md:438 → /home/mm/Документы/Как_избежать_нейрослопа_(гайд).md`
- `PLAN.md:302 → /home/mm/Документы/Как_избежать_нейрослопа_(гайд).md`

## Входящие ссылки из соседних ресерчей

Всего 433: site-research 398; creative-research 32; claude-design-research 3. Самые цитируемые файлы: `text-research/99-raw/notes/temp-vocabulary-v0.yaml` 133; `text-research/04-copy-by-block/copy-slots.yaml` 80; `text-research/02-strategy-messaging/02-awareness-hierarchy-objections.md` 22; `text-research/03-corpus-measured/corpus.tsv` 18; `text-research` 14; `text-research/02-strategy-messaging/examples/facts-service-renovation.yaml` 14; `text-research/09-ai-generation-evaluation/03-evaluation.md` 14; `text-research/99-raw/notes/orchestrator-notes.md` 13; `text-research/09-ai-generation-evaluation/copy-checklist.yaml` 8; `text-research/02-strategy-messaging/proof-intake.md` 7

## Короткие адреса и указатели

- адресов «NN/MM» (свои и «<база> NN/MM»): 893, из них файл не найден: 36 — зависят от нумерации папок и файлов
- указателей «→ … §» в тексте: 844 — зависят от нумерации разделов внутри файлов

## Дубли утилит (md5) в других ресерчах

- `text-research/99-raw/tools/fetch.py` = `ai-media-research/99-raw/tools/fetch.py`, `blender-research/99-raw/tools/fetch.py`, `claude-design-research/99-raw/tools/fetch.py`, `creative-research/99-raw/tools/fetch.py`, `site-research/99-raw/tools/fetch.py`, `ui-research/99-raw/tools/fetch.py`, `ux-research/99-raw/tools/fetch.py`
- `text-research/99-raw/tools/render_fetch.py` = `ai-media-research/99-raw/tools/render_fetch.py`, `blender-research/99-raw/tools/render_fetch.py`, `claude-design-research/99-raw/tools/render_fetch.py`, `creative-research/99-raw/tools/render_fetch.py`, `site-research/99-raw/tools/render_fetch.py`, `ui-research/99-raw/tools/render_fetch.py`, `ux-research/99-raw/tools/render_fetch.py`
- `text-research/99-raw/tools/site_probe.py` = `ai-media-research/99-raw/tools/site_probe.py`, `blender-research/99-raw/tools/site_probe.py`, `creative-research/99-raw/tools/site_probe.py`, `site-research/99-raw/tools/site_probe.py`
- `text-research/99-raw/tools/vtt2md.py` = `ai-media-research/99-raw/tools/vtt2md.py`, `claude-design-research/99-raw/tools/vtt2md.py`, `creative-research/99-raw/tools/vtt2md.py`, `site-research/99-raw/tools/vtt2md.py`
- `text-research/99-raw/tools/yt_dl.py` = `ai-media-research/99-raw/tools/yt_dl.py`, `claude-design-research/99-raw/tools/yt_dl.py`, `creative-research/99-raw/tools/yt_dl.py`, `site-research/99-raw/tools/yt_dl.py`
- `text-research/99-raw/tools/yt_transcript.py` = `ai-media-research/99-raw/tools/yt_transcript.py`, `blender-research/99-raw/tools/yt_transcript.py`, `claude-design-research/99-raw/tools/yt_transcript.py`, `creative-research/99-raw/tools/yt_transcript.py`, `site-research/99-raw/tools/yt_transcript.py`
- `text-research/99-raw/tools/transcribe_local.py` = `blender-research/99-raw/tools/transcribe_local.py`, `creative-research/99-raw/tools/transcribe_local.py`, `site-research/99-raw/tools/transcribe_local.py`

## Kimi / K3

3996 строк в 63 переносимых файлах. Топ: `03-corpus-measured/measurements.tsv` 3282; `04-copy-by-block/copy-slots.yaml` 83; `99-raw/tools/copydeck.py` 81; `PLAN.md` 41; `09-ai-generation-evaluation/live-test-plan.md` 39; `99-raw/tools/claims_check.py` 37; `02-strategy-messaging/meaning.schema.yaml` 36; `03-corpus-measured/corpus.tsv` 30; `10-templates-recipes/copy-deck.schema.json` 25; `10-templates-recipes/01-copy-deck-workflow.md` 24

## «Внешнее» — оценка объёма финальной уборки

- ссылок в исключаемое (служебное и т. п.): 733; строк с упоминанием служебных папок: 488
- ссылок в соседние ресерчи: 324 (из них в kimi: 0)
- меток роликов `[V:…]`: 113
- строк про Kimi/K3: 3996
