# blender-research — инвентарь для фазы 2

Скрипт `_skill-build/tools/inventory.py`, 26.09.2026 17:50. Токены — Opus 5.5 по калибровке.
Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, service, forbidden — нет.

## Классы файлов

| класс | файлов | МБ | ~токенов | переносим? |
|---|---|---|---|---|
| prose | 128 | 4.4 | 1664K | да |
| data | 100 | 1.2 | 513K | да |
| code | 144 | 1.5 | 676K | да |
| tool | 46 | 0.7 | 287K | да |
| root-doc | 2 | 0.3 | 112K | да |
| asset | 7764 | 2509.0 | 0K | нет |
| bundle | 14 | 3.4 | 1658K | нет |
| junk | 9807 | 148.4 | 0K | нет |
| service | 5057 | 378.2 | 0K | нет |
| **итого переносим** | 420 | 8.1 | 3252K | |
| **итого не переносим** | 22642 | 3038.9 | — | |

## Папки верхнего уровня

| папка | файлов | МБ | ~токенов текста | состав |
|---|---|---|---|---|
| (корень) | 2 | 0.3 | 112K | root-doc 2 |
| 00-glossary | 1 | 0.1 | 33K | prose 1 |
| 01-web-3d-landscape | 6 | 0.3 | 116K | prose 6 |
| 02-blender-workflow | 5 | 0.2 | 63K | prose 5 |
| 03-bpy-api | 14 | 0.6 | 194K | prose 6, code 5, junk 3 |
| 04-ai-agents-mcp | 8 | 0.6 | 195K | prose 8 |
| 05-modeling | 6 | 0.2 | 73K | prose 6 |
| 06-materials-lighting-render | 5 | 0.2 | 62K | prose 5 |
| 07-animation | 5 | 0.2 | 70K | prose 5 |
| 08-export-gltf | 5 | 0.3 | 141K | prose 5 |
| 09-web-runtime | 56 | 6.1 | 872K | prose 11, data 14, code 9, asset 13, bundle 2, junk 7 |
| 10-ai-3d-generation-assets | 5 | 0.1 | 52K | prose 5 |
| 11-evaluation-qa | 13 | 0.2 | 89K | prose 8, data 3, code 2 |
| 12-recipes | 253 | 19.6 | 236K | prose 19, data 26, code 24, asset 176, junk 8 |
| 13-tools-atlas | 5 | 0.2 | 50K | prose 4, data 1 |
| 14-code-3d | 10 | 0.2 | 52K | prose 10 |
| 15-showcase | 1798 | 173.1 | 2213K | prose 24, data 56, code 104, asset 1578, bundle 12, junk 24 |
| 90-sources | 2 | 0.1 | 0K | service 2 |
| 91-videos | 171 | 5.2 | 0K | service 171 |
| 99-raw | 20692 | 2839.3 | 287K | tool 46, asset 5997, junk 9765, service 4884 |

## Служебные папки (группами, топ по размеру)

| группа | файлов | МБ |
|---|---|---|
| 99-raw/youtube | 658 | 251.9 |
| 99-raw/experiments | 3509 | 88.9 |
| 99-raw/cache | 516 | 14.3 |
| 99-raw/tools | 11 | 12.3 |
| 99-raw/notes | 119 | 3.9 |
| 91-videos/transcripts | 106 | 3.9 |
| 91-videos/digests | 62 | 1.2 |
| 99-raw/reports | 29 | 1.0 |
| 99-raw/prompts | 41 | 0.6 |
| 91-videos/catalog.md | 1 | 0.1 |
| 90-sources/sources.tsv | 1 | 0.1 |
| 91-videos/catalog.tsv | 1 | 0.1 |
| 90-sources/README.md | 1 | 0.0 |
| 99-raw/handoff-to-neighbours.md | 1 | 0.0 |
| 91-videos/README.md | 1 | 0.0 |

## Серые зоны (решить при переносе)

- **Крупные текстовые файлы > 1 МБ**: 0
- **PLAN.md (план ресерча)**: 1 — PLAN.md (134 КБ)
- **Индекс источников в 90-sources**: 2 — 90-sources/README.md; 90-sources/sources.tsv
- **Служебные файлы, на которые ссылается переносимое (ссылок)**: 437 — blender-research/99-raw/tools/README.md (45); blender-research/99-raw/tools (13); blender-research/99-raw/experiments/D1/_lib/d1lib.py (12); blender-research/99-raw/experiments/C1/12-protocol-objects/proto_lib.py (10); blender-research/99-raw/reports/wave2-W3-report.md (9); blender-research/99-raw/tools/node (8); blender-research/99-raw/experiments/C1/12-protocol-objects/run_proto.py (8); blender-research/99-raw/reports/wave2-W4-report.md (7); blender-research/99-raw/experiments/F1/06-doc-snippets (7); blender-research/90-sources (7); blender-research/99-raw/experiments/A/02-runtime-registry/registry.json (6); blender-research/99-raw/experiments/D1/09-doc-snippets (6); … ещё 425
- **Код, который ссылается на ассеты (без них сломается; число ссылок)**: 41 — 09-web-runtime/examples/hero-lazy/index.html (2); 12-recipes/examples/01-hero-product/index.html (2); 12-recipes/examples/02-icon-series/index.html (3); 12-recipes/examples/02-icon-series/post.py (1); 12-recipes/examples/08-sequence-video-alpha/index.html (2); 12-recipes/examples/12-model-viewer-ar/index.html (2); 15-showcase/_shared/build_index.py (2); 15-showcase/_shared/index-draft-s1.html (36); 15-showcase/gallery/build.py (2); 15-showcase/keyboard/a-code/assets/page.css (2); 15-showcase/keyboard/a-code/index.html (10); 15-showcase/keyboard/a-code/src/adapter_b.js (1); … ещё 29

## Код и утилиты (190 файлов)

| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |
|---|---|---|---|---|---|---|---|
| `99-raw/tools/anim_diff.py` | 239 | anim_diff.py (агент H) — анимация «как в Blender» против «как в three r186» в ОДНИ И ТЕ ЖЕ моменты. | gltf_diff, playwright, shutil, subprocess, tempfile, time | да | да | 1 | 1 |
| `99-raw/tools/asr_compare.py` | 161 | Сравнение распознавания Whisper (JSON с GPU-сервера) и локального Qwen3-ASR (91-videos/transcripts/<id>.md). | difflib |  | да |  | 1 |
| `99-raw/tools/asr_dl.py` | 167 | Скачивание звука YouTube на GPU-сервере через обратный SOCKS-туннель с ноутбука (VPN заказчика). | glob, subprocess, time |  | да |  | 1 |
| `99-raw/tools/asr_feed.py` | 288 | Подача звука на GPU-сервер: скачать здесь (yt-dlp через VPN) → Opus 16 кГц моно → залить в /root/blender-asr/a | glob, queue, subprocess, threading, time |  | да |  | 9 |
| `99-raw/tools/asr_merge.py` | 165 | Склейка двух распознаваний одного звука (faster-whisper): «основа» с пунктуацией + «полный» без пропусков. | difflib, glob, time |  | да |  |  |
| `99-raw/tools/asr_qc.py` | 305 | Проверка JSON распознавания (faster-whisper, GPU-сервер) на брак. Запускается на сервере, только stdlib. | difflib, glob, statistics, zlib |  | да |  | 1 |
| `99-raw/tools/asr_queue.py` | 42 | Очередь локального распознавания речи (Qwen3-ASR через transcribe_local.py) по списку id. | subprocess, time |  | да |  | 7 |
| `99-raw/tools/asr_server.py` | 230 | GPU-распознавание роликов YouTube для blender-research (сервер с RTX A5000, /root/blender-asr/). | faster_whisper, glob, numpy, site, time, yt_dlp | да | да |  | 1 |
| `99-raw/tools/asr_status.py` | 152 | Сводка по транскриптам роликов каталога → 99-raw/youtube/transcripts_status.md (лёгкая: только чтение текстов) | csv, time |  | да |  | 11 |
| `99-raw/tools/asr_subs.py` | 132 | Ручные субтитры YouTube без HTTP 429 — рецепт ai-media-research (99-raw/experiments/V/01-video-catalog/dl.py). | glob, subprocess, time |  | да |  | 8 |
| `99-raw/tools/asr_terms.py` | 75 | Как распознавание записало ключевые термины: частоты вариантов написания по всем транскриптам (только stdlib). | glob |  | да |  |  |
| `99-raw/tools/asr_tunnel.sh` | 29 |  |  |  |  |  | 5 |
| `99-raw/tools/asr_wer.py` | 91 | ≈WER распознавания против ручных субтитров YouTube (эталон). Запускается на сервере, только stdlib. | difflib |  | да |  | 1 |
| `99-raw/tools/atlas_collect.py` | 745 | atlas_collect.py (агент L, волна 3) — собирает 13-tools-atlas/atlas.tsv из реестров и живых источников. | subprocess, time, urllib | да | да | 2 | 28 |
| `99-raw/tools/blender_run.py` | 91 | Запуск Python-кода в Blender без окна (background) с таймаутом, кодом выхода и журналом. | shutil, subprocess, time |  | да | 1 | 1 |
| `99-raw/tools/blender_supervisor.py` | 305 | blender_supervisor.py — фоновый Blender 5.2 под надзором для агента (агент O, волна 3, 23.09.2026). | shutil, signal, socket, subprocess, time | да | да | 1 | 1 |
| `99-raw/tools/bpy_probe.py` | 973 | bpy_probe.py — справочник по Python API, который отвечает сам Blender (JSON). Замена MCP-инструментам | addon_utils, ast, bl_ui, bpy, difflib, gpu, math, numpy, shutil, subprocess, tra |  | да |  | 14 |
| `99-raw/tools/check_links.py` | 847 | Проверка перекрёстных ссылок и структуры базы blender-research. | glob |  | да |  | 24 |
| `99-raw/tools/ctx_watch.py` | 173 | Сторож контекста агентов испытания blender-research 15-showcase (копия creative-research/99-raw/tools/ctx_watc | glob, time |  | да |  | 5 |
| `99-raw/tools/ctx_watch_v1.py` | 147 | Сторож контекста агентов испытания blender-research 15-showcase (копия creative-research/99-raw/tools/ctx_watc | glob, time |  | да |  | 5 |
| `99-raw/tools/extract_sections.py` | 71 | Компактные извлечения разделов из Markdown-файлов базы (для аудитора и синтезатора волны 4). | glob |  | да |  | 5 |
| `99-raw/tools/fetch.py` | 77 | Скачать страницу и сохранить читаемый текст (Markdown) в 99-raw/cache/. | bs4, hashlib, requests, subprocess | да | да |  | 1 |
| `99-raw/tools/fx_probe.py` | 252 | fx_probe.py (агент F2, перенесено в 99-raw/tools агентом U волна 4) — замер своей демо-страницы с 3D/шейдерным | PIL, functools, http, math, playwright, socketserver, threading, time | да | да |  | 2 |
| `99-raw/tools/gate_check.py` | 68 | gate_check.py — общий модуль ворот качества страницы с 3D по отчёту site_probe.py (агент U, волна 4 — перенос |  |  | да |  | 1 |
| `99-raw/tools/gltf_check.py` | 95 | Проверка glTF/GLB: валидатор Khronos + инспекция gltf-transform + сводка «готово ли для веба». | subprocess |  | да |  | 2 |
| `99-raw/tools/gltf_diff.py` | 465 | gltf_diff.py — сравнение «как выглядит в Blender» и «как выглядит в three.js» при ОДИНАКОВЫХ камере, свете и т | PIL, functools, http, math, numpy, playwright, shutil, socketserver, subprocess, | да | да |  |  |
| `99-raw/tools/gltf_load_bench.py` | 169 | gltf_load_bench.py — замер загрузки GLB в three.js (r186) в headless Chromium на GPU: холодная загрузка (с док | functools, http, playwright, shutil, socketserver, tempfile, threading | да | да |  |  |
| `99-raw/tools/gltf_web_inspect.py` | 185 | gltf_web_inspect.py — что three.js (r186 по умолчанию) реально создаёт из glTF/GLB: дамп сцены в JSON. | functools, http, playwright, shutil, socketserver, tempfile, threading | да | да |  |  |
| `99-raw/tools/lint_agent_code.py` | 70 | lint_agent_code.py — самопроверка текста скрипта агента регулярными выражениями до отправки в Blender (агент U |  |  | да |  | 3 |
| `99-raw/tools/node/validate.mjs` | 20 |  |  |  |  |  |  |
| `99-raw/tools/qa_pipeline.py` | 373 | qa_pipeline.py (агент J, волна 3) — сводный конвейер проверок: сцена → GLB → страница; JSON с порогами и верди | gate_check, glb_lint_block, serve_br, shutil, struct, subprocess, tempfile, time |  | да | 1 | 4 |
| `99-raw/tools/render_fetch.py` | 107 | Скачать страницу через headless-браузер (Playwright/Chromium) и сохранить читаемый Markdown в 99-raw/cache/. | hashlib, playwright, subprocess | да | да |  | 1 |
| `99-raw/tools/render_views.py` | 325 | Рендер модели с нескольких ракурсов + контактный лист + статистика геометрии. Запускается ВНУТРИ Blender: | OpenImageIO, bmesh, bpy, math, mathutils, numpy, time, warnings |  | да |  |  |
| `99-raw/tools/run_doc_blocks.py` | 96 | run_doc_blocks.py (агент J, волна 3) — исполнить блоки кода итоговых .md в напечатанном виде; обобщение раннер | shutil, subprocess, tempfile |  | да | 1 | 2 |
| `99-raw/tools/scene_check.py` | 663 |  | bmesh, bpy, math, mathutils |  |  |  | 2 |
| `99-raw/tools/site_probe.py` | 446 | site_probe.py — замер живого 3D-сайта (агент A, волна 1). Дополняет 99-raw/tools/web_view.py --url. | PIL, playwright, time | да | да |  | 1 |
| `99-raw/tools/slot_run.py` | 292 | slot_run.py — очередь для тяжёлых запусков, когда параллельно работают несколько агентов (испытание 15-showcas | fcntl, subprocess, time |  | да | 1 |  |
| `99-raw/tools/slot_run_v1.py` | 137 | slot_run.py — очередь для тяжёлых запусков, когда параллельно работают несколько агентов (испытание 15-showcas | fcntl, subprocess, time |  | да | 1 |  |
| `99-raw/tools/slot_run_v21.py` | 274 | slot_run.py — очередь для тяжёлых запусков, когда параллельно работают несколько агентов (испытание 15-showcas | fcntl, subprocess, time |  | да | 1 |  |
| `99-raw/tools/sources_collect.py` | 436 | Сводная библиография базы blender-research. | glob, io |  | да |  | 22 |
| `99-raw/tools/three_probe.py` | 69 | three_probe.py (агент H) — загрузить GLB в three r186 (Chromium, GPU) и выполнить JS-проверку; вывести JSON. | gltf_diff, playwright, shutil, tempfile | да | да | 1 | 1 |
| `99-raw/tools/transcribe_local.py` | 256 | Локальная транскрибация YouTube-видео или аудиофайла через Qwen3-ASR-1.7B (llama.cpp, CPU). | shutil, subprocess, time |  | да |  | 4 |
| `99-raw/tools/vtt2md.py` | 111 | Собирает 91-videos/transcripts/<id>.md из уже скачанных .vtt и .info.json без обращения к YouTube. | glob |  | да | 3 | 6 |
| `99-raw/tools/web_view.py` | 429 | Проверка 3D в браузере: GLB в three.js или готовая страница — через headless Chromium на реальной видеокарте. | PIL, functools, http, playwright, shutil, socketserver, tempfile, threading, tim | да | да |  |  |
| `99-raw/tools/whisper2md.py` | 113 | Собирает 91-videos/transcripts/<id>.md из JSON распознавания (faster-whisper на GPU-сервере) и сохранённых |  |  | да |  | 7 |
| `99-raw/tools/yt_transcript.py` | 210 | Субтитры и метаданные YouTube-видео без скачивания самого видео (через yt-dlp). | requests, yt_dlp | да | да |  | 2 |

Прочий код (144 файлов) по папкам: `15-showcase/keyboard` 42, `12-recipes/examples` 24, `15-showcase/zveno` 19, `15-showcase/_shared` 18, `15-showcase/sdano` 12, `09-web-runtime/examples` 9, `15-showcase/velmora` 7, `03-bpy-api/snippets` 5, `15-showcase/vote` 4, `11-evaluation-qa/regression` 2, `15-showcase/gallery` 1, `15-showcase/verdict` 1

Зашитые абсолютные пути (14 разных): `/home/mm/.local/bin/blender`; `/home/mm/.nvm/versions/node/v24.21.0/bin`; `/home/mm/.nvm/versions/node/v24.21.0/bin:$PATH`; `/home/mm/Документы/app-design/.locks`; `/home/mm/Документы/app-design/blender-research`; `/home/mm/Документы/app-design/blender-research/03-bpy-api/snippets`; `/home/mm/Документы/app-design/blender-research/12-recipes/examples/02-icon-series`; `/home/mm/Документы/app-design/blender-research/12-recipes/examples/08-sequence-video-alpha`; `/home/mm/Документы/app-design/blender-research/12-recipes/examples/_kit`; `/home/mm/Документы/app-design/blender-research/91-videos/transcripts`

## Ссылки из переносимых файлов (md, данные, код)

| статус | число | смысл |
|---|---|---|
| ok | 2357 | цель переносится |
| to-excluded | 1292 | цель есть, но не переносится (служебное, ассет, мусор) — сломается |
| to-kimi | 0 | ведёт в kimi-research (донор) — заменить при уборке |
| missing | 1952 | цели нет уже сейчас (или путь условный) |
| outside | 1 | абсолютный путь вне базы |
| short-unresolved | 132 | адрес «NN/MM» не нашёл файла (часто — номер раздела) |

Сломаются — по источнику ссылки и типу цели:

| тип цели | из md | из данных | из кода | всего |
|---|---|---|---|---|
| ассет | 82 | 207 | 295 | 584 |
| служебное | 567 | 73 | 55 | 695 |
| прочее | 7 | 0 | 6 | 13 |

Примеры to-excluded:
- `00-glossary/README.md:9 → 99-raw/reports/wave4-X-glossary-draft.md`
- `00-glossary/README.md:239 → 99-raw/tools/README.md`
- `00-glossary/README.md:568 → 91-videos/`
- `00-glossary/README.md:569 → 91-videos/digests/`
- `00-glossary/README.md:570 → 99-raw/reports/wave4-X-audit.md`
- `00-glossary/README.md:570 → 99-raw/experiments/X/`
- `01-web-3d-landscape/01-effects-catalog.md:6 → 99-raw/experiments/A/`
- `01-web-3d-landscape/01-effects-catalog.md:740 → 99-raw/notes/wave1/A-notes.md`
- `01-web-3d-landscape/01-effects-catalog.md:751 → 99-raw/experiments/A/sites/`
- `01-web-3d-landscape/02-when-3d-budgets-loading.md:5 → 99-raw/experiments/A/`
- `01-web-3d-landscape/03-runtime-landscape.md:7 → 99-raw/experiments/A/02-runtime-registry`
- `01-web-3d-landscape/03-runtime-landscape.md:69 → 99-raw/experiments/A/02-runtime-registry/registry.json`

Примеры missing:
- `01-web-3d-landscape/01-effects-catalog.md:441 → ../../ui-research/07-iconography-imagery/02`
- `01-web-3d-landscape/01-effects-catalog.md:751 → 03-bundle-sizes`
- `01-web-3d-landscape/01-effects-catalog.md:751 → 04-lcp-canvas`
- `01-web-3d-landscape/01-effects-catalog.md:751 → 05-detect-gpu`
- `01-web-3d-landscape/01-effects-catalog.md:751 → 06-deliverable-sizes`
- `01-web-3d-landscape/02-when-3d-budgets-loading.md:225 → build/three.module.js`
- `01-web-3d-landscape/02-when-3d-budgets-loading.md:253 → ./three.core.js`
- `01-web-3d-landscape/02-when-3d-budgets-loading.md:292 → ../../ux-research/06-feedback-states-motion/03`
- `01-web-3d-landscape/02-when-3d-budgets-loading.md:432 → 04-lcp-canvas`
- `01-web-3d-landscape/02-when-3d-budgets-loading.md:432 → 05-detect-gpu`
- `01-web-3d-landscape/02-when-3d-budgets-loading.md:432 → 03-bundle-sizes`
- `01-web-3d-landscape/02-when-3d-budgets-loading.md:432 → 06-deliverable-sizes`

Примеры outside:
- `15-showcase/KIT.md:4 → /home/mm/.claude/plans/cheerful-frolicking-teapot.md`

## Входящие ссылки из соседних ресерчей

Всего 219: creative-research 136; site-research 45; ai-media-research 28; claude-design-research 7; text-research 3. Самые цитируемые файлы: `blender-research/01-web-3d-landscape/02-when-3d-budgets-loading.md` 41; `blender-research` 21; `blender-research/09-web-runtime/05-performance-a11y-fallbacks.md` 21; `blender-research/01-web-3d-landscape/01-effects-catalog.md` 18; `blender-research/01-web-3d-landscape/04-reference-sites-measured.md` 16; `blender-research/09-web-runtime/03-scroll-interaction-animation.md` 16; `blender-research/12-recipes/00-how-to-use.md` 15; `blender-research/07-animation/04-js-vs-blender-vs-prerender.md` 14; `blender-research/11-evaluation-qa/05-master-checklist.md` 11; `blender-research/01-web-3d-landscape/03-runtime-landscape.md` 8

## Короткие адреса и указатели

- адресов «NN/MM» (свои и «<база> NN/MM»): 1147, из них файл не найден: 132 — зависят от нумерации папок и файлов
- указателей «→ … §» в тексте: 1455 — зависят от нумерации разделов внутри файлов

## Дубли утилит (md5) в других ресерчах

- `blender-research/99-raw/tools/fetch.py` = `ai-media-research/99-raw/tools/fetch.py`, `claude-design-research/99-raw/tools/fetch.py`, `creative-research/99-raw/tools/fetch.py`, `site-research/99-raw/tools/fetch.py`, `text-research/99-raw/tools/fetch.py`, `ui-research/99-raw/tools/fetch.py`, `ux-research/99-raw/tools/fetch.py`
- `blender-research/99-raw/tools/render_fetch.py` = `ai-media-research/99-raw/tools/render_fetch.py`, `claude-design-research/99-raw/tools/render_fetch.py`, `creative-research/99-raw/tools/render_fetch.py`, `site-research/99-raw/tools/render_fetch.py`, `text-research/99-raw/tools/render_fetch.py`, `ui-research/99-raw/tools/render_fetch.py`, `ux-research/99-raw/tools/render_fetch.py`
- `blender-research/99-raw/tools/site_probe.py` = `ai-media-research/99-raw/tools/site_probe.py`, `creative-research/99-raw/tools/site_probe.py`, `site-research/99-raw/tools/site_probe.py`, `text-research/99-raw/tools/site_probe.py`
- `blender-research/99-raw/tools/yt_transcript.py` = `ai-media-research/99-raw/tools/yt_transcript.py`, `claude-design-research/99-raw/tools/yt_transcript.py`, `creative-research/99-raw/tools/yt_transcript.py`, `site-research/99-raw/tools/yt_transcript.py`, `text-research/99-raw/tools/yt_transcript.py`
- `blender-research/99-raw/tools/transcribe_local.py` = `creative-research/99-raw/tools/transcribe_local.py`, `site-research/99-raw/tools/transcribe_local.py`, `text-research/99-raw/tools/transcribe_local.py`

## Kimi / K3

3 строк в 3 переносимых файлах. Топ: `15-showcase/sdano/a-code/style.css` 1; `15-showcase/sdano/b-blender/style.css` 1; `15-showcase/sdano/c-hybrid/style.css` 1

## «Внешнее» — оценка объёма финальной уборки

- ссылок в исключаемое (служебное и т. п.): 1292; строк с упоминанием служебных папок: 1672
- ссылок в соседние ресерчи: 92 (из них в kimi: 0)
- меток роликов `[V:…]`: 515
- строк про Kimi/K3: 3
