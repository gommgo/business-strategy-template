# ai-media-research — инвентарь для фазы 2

Скрипт `_skill-build/tools/inventory.py`, 26.09.2026 17:50. Токены — Opus 5.5 по калибровке.
Политика по умолчанию: содержимое (prose, data, root-doc) и код (code, tool) — переносим; asset, bundle, junk, service, forbidden — нет.

## Классы файлов

| класс | файлов | МБ | ~токенов | переносим? |
|---|---|---|---|---|
| prose | 79 | 3.8 | 1453K | да |
| data | 138 | 1.4 | 575K | да |
| code | 19 | 0.1 | 49K | да |
| tool | 28 | 1.2 | 530K | да |
| root-doc | 3 | 0.4 | 127K | да |
| asset | 5905 | 2414.2 | 0K | нет |
| junk | 29135 | 1528.9 | 0K | нет |
| service | 5639 | 491.9 | 0K | нет |
| other | 1 | 1.0 | 0K | нет |
| **итого переносим** | 267 | 6.9 | 2735K | |
| **итого не переносим** | 40680 | 4436.0 | — | |

## Папки верхнего уровня

| папка | файлов | МБ | ~токенов текста | состав |
|---|---|---|---|---|
| (корень) | 3 | 0.4 | 127K | root-doc 3 |
| 00-glossary | 2 | 0.2 | 64K | prose 2 |
| 01-web-assets-landscape | 5 | 0.3 | 108K | prose 4, data 1 |
| 02-providers-platforms | 8 | 0.6 | 266K | prose 8 |
| 03-image-models | 38 | 0.7 | 270K | prose 4, data 34 |
| 04-video-models | 33 | 0.4 | 141K | prose 4, data 29 |
| 05-prompting | 9 | 0.6 | 243K | prose 7, data 2 |
| 06-art-direction-consistency | 9 | 0.3 | 99K | prose 5, data 4 |
| 07-vector-svg-icons | 5 | 0.1 | 38K | prose 5 |
| 08-image-post-processing | 5 | 0.2 | 54K | prose 5 |
| 09-video-pipeline | 5 | 0.1 | 53K | prose 5 |
| 10-web-integration | 158 | 7.8 | 93K | prose 6, code 15, asset 137 |
| 11-evaluation-qa | 18 | 0.3 | 104K | prose 4, data 14 |
| 12-legal-provenance | 5 | 0.2 | 62K | prose 5 |
| 13-routing-matrix | 16 | 0.5 | 183K | prose 5, data 11 |
| 14-recipes | 125 | 3.1 | 279K | prose 7, data 43, code 4, asset 62, junk 8, other 1 |
| 15-tools-atlas | 3 | 0.1 | 22K | prose 3 |
| 90-sources | 2 | 0.2 | 0K | service 2 |
| 91-videos | 130 | 4.6 | 0K | service 130 |
| 99-raw | 40368 | 4422.3 | 530K | tool 28, asset 5706, junk 29127, service 5507 |

## Служебные папки (группами, топ по размеру)

| группа | файлов | МБ |
|---|---|---|
| 99-raw/tools | 343 | 272.4 |
| 99-raw/cache | 1790 | 93.0 |
| 99-raw/experiments | 2311 | 79.6 |
| 99-raw/youtube | 423 | 31.1 |
| 99-raw/phase5 | 428 | 4.9 |
| 99-raw/notes | 132 | 4.6 |
| 91-videos/transcripts | 90 | 3.5 |
| 99-raw/reports | 34 | 0.9 |
| 91-videos/digests | 37 | 0.9 |
| 99-raw/prompts | 46 | 0.6 |
| 90-sources/bibliography.md | 1 | 0.2 |
| 91-videos/catalog.md | 1 | 0.2 |
| 91-videos/catalog.tsv | 1 | 0.1 |
| 91-videos/README.md | 1 | 0.0 |
| 90-sources/README.md | 1 | 0.0 |

## Серые зоны (решить при переносе)

- **Крупные текстовые файлы > 1 МБ**: 0
- **PLAN.md (план ресерча)**: 1 — PLAN.md (207 КБ)
- **Индекс источников в 90-sources**: 1 — 90-sources/README.md
- **Служебные файлы, на которые ссылается переносимое (ссылок)**: 481 — ai-media-research/99-raw/experiments/C1/06-model-cards-build/build_cards.py (36); ai-media-research/99-raw/phase5/runs/README.md (26); ai-media-research/99-raw/tools/README.md (24); ai-media-research/99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md (20); ai-media-research/99-raw/phase5/runs/3-prompt-form/README.md (16); ai-media-research/99-raw/phase5/inputs/D2/questions_v2.json (16); ai-media-research/99-raw/reports/wave1-C1-report.md (15); ai-media-research/99-raw/experiments/_ledger.jsonl (13); ai-media-research/91-videos/digests (10); ai-media-research/99-raw/phase5/runs/MS-marea/loop_rife_bridge.py (10); ai-media-research/99-raw/cache (9); ai-media-research/99-raw/experiments/3D/README.md (9); … ещё 469
- **Код, который ссылается на ассеты (без них сломается; число ссылок)**: 12 — 10-web-integration/pages/00-hero-summary.html (11); 10-web-integration/pages/01-image-hero.html (7); 10-web-integration/pages/02-video-hero.html (8); 10-web-integration/pages/02b-video-source-media.html (6); 10-web-integration/pages/03-alpha-object-hero.html (6); 10-web-integration/pages/04-two-states-spotlight.html (12); 10-web-integration/pages/05-scroll-sequence.html (3); 10-web-integration/pages/07-effects-grain-layers.html (6); 10-web-integration/pages/08-svg-icons-favicons.html (3); 10-web-integration/pages/css/base.css (1); 14-recipes/examples/demo-landing/css/site.css (3); 14-recipes/examples/demo-landing/index.html (13)

## Код и утилиты (47 файлов)

| файл | строк | назначение (docstring) | импорты | сеть | CLI | абс. пути | служ. пути |
|---|---|---|---|---|---|---|---|
| `99-raw/tools/ab_analyze.py` | 387 | ab_analyze.py — анализ A/B формы промта (D2, волна 2, 2026-09-23): мощность, судья вслепую, метрики, решение. | PIL, hashlib, math, numpy, random |  | да |  | 3 |
| `99-raw/tools/alpha_check.py` | 135 | alpha_check.py — проверка прозрачности (вырез, нативная альфа модели, матирование). Агент H, волна 2, 23.09.20 | PIL, edit_check, numpy, scipy |  | да |  | 1 |
| `99-raw/tools/asset_audit.py` | 2630 | asset_audit.py — единая автоматическая приёмка ИИ-ассетов сайта (агент K, волна 3, 23.09.2026). | PIL, contextlib, hashlib, importlib, io, math, numpy, random, rapidocr, scipy, s |  | да |  | 10 |
| `99-raw/tools/asset_inventory.py` | 699 | asset_inventory.py — инвентарь визуальных ассетов живой страницы (агент A, волна 1 ai-media-research, 2026-09- | PIL, io, playwright, time, urllib | да | да |  |  |
| `99-raw/tools/avif_pick.sh` | 15 |  |  |  |  | 1 | 2 |
| `99-raw/tools/check_links.py` | 1205 | Проверка перекрёстных ссылок, меток и структуры базы ai-media-research. | glob |  | да |  | 60 |
| `99-raw/tools/color.py` | 176 | Расчёты цвета для интерфейсов без внешних зависимостей (написано агентом A волны 1, проверено по калькулятору  | math |  | да |  | 1 |
| `99-raw/tools/edit_check.py` | 462 | edit_check.py — проверка правки картинки нейросетью и композит оригинала обратно (агент H, волна 2, 23.09.2026 | PIL, io, numpy, scipy, tempfile |  | да |  | 1 |
| `99-raw/tools/fetch.py` | 77 | Скачать страницу и сохранить читаемый текст (Markdown) в 99-raw/cache/. | bs4, hashlib, requests, subprocess | да | да |  | 1 |
| `99-raw/tools/mp_client.py` | 3066 | mp_client.py — клиент каналов фазы 5 вне Media API polza: RouterAI, Gen-API, polza-chat, polza-images. | PIL, base64, concurrent, fcntl, hashlib, io, math, mimetypes, polza, polza_catal | да | да |  | 18 |
| `99-raw/tools/page_accept.py` | 378 | page_accept.py — приёмка страницы с ИИ-ассетами в Chromium (агент J, волна 3, 23.09.2026). | PIL, contextlib, fcntl, http, io, numpy, playwright, scipy, socketserver, thread | да | да |  | 2 |
| `99-raw/tools/polza.py` | 1431 | polza.py — клиент Media API polza.ai для ai-media-research: сухой прогон по умолчанию, трата только с --live. | PIL, base64, concurrent, fcntl, hashlib, mimetypes, polza_catalog, random, shuti | да | да |  | 6 |
| `99-raw/tools/polza_catalog.py` | 1388 | polza_catalog.py — каталог polza.ai как данные: снимки, нормализация медиа-моделей, таблица, сравнение | hashlib, math, time, urllib | да | да |  | 5 |
| `99-raw/tools/prompt_compile.py` | 2112 | prompt_compile.py — компилятор промтов: спецификация ассета → промт в диалекте модели + параметры задания. | PIL, copy, hashlib, jsonschema, polza_catalog, random, yaml |  | да |  | 4 |
| `99-raw/tools/provenance_check.py` | 638 | provenance_check.py — бесплатная проверка провенанса ИИ-ассетов (0 ₽, без сети). | PIL, hashlib, numpy, scipy, shutil, subprocess, tempfile |  | да |  |  |
| `99-raw/tools/render_fetch.py` | 107 | Скачать страницу через headless-браузер (Playwright/Chromium) и сохранить читаемый Markdown в 99-raw/cache/. | hashlib, playwright, subprocess | да | да |  | 1 |
| `99-raw/tools/routing_check.py` | 425 | routing_check.py 1.1 — проверка 13-routing-matrix/routing.yaml (агент N, волна 3, 24.09.2026; v1.1 — агент U,  | mp_client, polza_catalog, yaml |  | да |  | 7 |
| `99-raw/tools/site_probe.py` | 446 | site_probe.py — замер живого 3D-сайта (агент A, волна 1). Дополняет 99-raw/tools/web_view.py --url. | PIL, playwright, time | да | да |  | 1 |
| `99-raw/tools/stand_run.py` | 920 | stand_run.py — стенд моделей ai-media-research: задания фазы 5, сбор результатов, автометрики, контактные лист | PIL, base64, html, importlib, io, math, numpy, polza_catalog, prompt_compile, ra |  | да |  | 10 |
| `99-raw/tools/tests/test_asset_audit.py` | 397 | Тесты asset_audit.py (агент K, волна 3, 23.09.2026). Без сети и платных вызовов. | PIL, asset_audit, contextlib, io, numpy, scipy, shutil, subprocess, tempfile, tr |  | да |  | 8 |
| `99-raw/tools/tests/test_prompt_compile.py` | 284 | Офлайн-тесты prompt_compile.py v2 (D2, волна 2). Без сети и генераций. | PIL, prompt_compile, subprocess, tempfile |  | да |  | 8 |
| `99-raw/tools/tests/test_prompt_compile_x2.py` | 101 | Офлайн-тесты исправлений prompt_compile.py v2.1.1 (агент X2, 24.09.2026; дефекты стыка из демо M `14-recipes/` | copy, prompt_compile |  | да |  | 4 |
| `99-raw/tools/tile_check.py` | 97 | tile_check.py — бесшовность текстуры: метрика шва, тайл разрезом минимальной ошибки, превью (агент H2, волна 2 | PIL, numpy |  | да |  | 1 |
| `99-raw/tools/video_loop_check.py` | 452 | video_loop_check.py — приёмка ИИ-видео для сайта: шов петли, «живость», мёртвые концы, склейки, дрейф неподвиж | PIL, edit_check, glob, numpy, scipy, subprocess |  | да |  | 1 |
| `99-raw/tools/vlm_to_dna.py` | 1101 | vlm_to_dna.py — паспорт визуала бренда (visual DNA): VLM-бриф сетки бренд-картинок → черновик паспорта, | PIL, color, copy, jsonschema, math, numpy, palette, subprocess, tempfile |  | да |  | 9 |
| `99-raw/tools/vtt2md.py` | 114 | Собирает 91-videos/transcripts/<id>.md из уже скачанных .vtt и .info.json без обращения к YouTube. | glob |  | да |  | 5 |
| `99-raw/tools/yt_dl.py` | 200 | Загрузка метаданных, субтитров и комментариев YouTube без видео и аудио, с паузами и обработкой HTTP 429. | glob, subprocess, time |  | да | 1 | 6 |
| `99-raw/tools/yt_transcript.py` | 210 | Субтитры и метаданные YouTube-видео без скачивания самого видео (через yt-dlp). | requests, yt_dlp | да | да |  | 2 |
| `10-web-integration/pages/00-hero-summary.html` | 123 |  |  |  |  |  | 1 |
| `10-web-integration/pages/01-image-hero.html` | 101 |  |  |  |  |  | 1 |
| `10-web-integration/pages/02-video-hero.html` | 81 |  |  |  |  |  | 1 |
| `10-web-integration/pages/02b-video-source-media.html` | 36 |  |  |  |  |  | 1 |
| `10-web-integration/pages/03-alpha-object-hero.html` | 81 |  |  |  |  |  | 1 |
| `10-web-integration/pages/04-two-states-spotlight.html` | 105 |  |  |  |  |  | 1 |
| `10-web-integration/pages/05-scroll-sequence.html` | 50 |  |  |  |  |  | 1 |
| `10-web-integration/pages/07-effects-grain-layers.html` | 75 |  |  |  |  |  |  |
| `10-web-integration/pages/08-svg-icons-favicons.html` | 50 |  |  |  |  |  |  |
| `10-web-integration/pages/css/base.css` | 73 |  |  |  |  |  | 1 |
| `10-web-integration/pages/js/focal.js` | 36 |  |  |  |  |  |  |
| `10-web-integration/pages/js/hero-video.js` | 76 |  |  |  |  |  | 1 |
| `10-web-integration/pages/js/scroll-seq.js` | 51 |  |  |  |  |  |  |
| `10-web-integration/pages/js/spotlight.js` | 79 |  |  |  |  |  |  |
| `10-web-integration/pages/js/stacked-alpha.js` | 74 |  |  |  |  |  |  |
| `14-recipes/examples/demo-landing/css/site.css` | 110 |  |  |  |  |  |  |
| `14-recipes/examples/demo-landing/index.html` | 161 |  |  |  |  |  |  |
| `14-recipes/examples/demo-landing/js/focal.js` | 36 |  |  |  |  |  |  |
| `14-recipes/examples/demo-landing/js/hero-video.js` | 76 |  |  |  |  |  | 1 |

Зашитые абсолютные пути (2 разных): `/home/mm/.nvm/versions/node/v24.21.0/bin/node`; `/home/mm/Документы/app-design/ai-media-research/99-raw/tools/bin`

## Ссылки из переносимых файлов (md, данные, код)

| статус | число | смысл |
|---|---|---|
| ok | 2171 | цель переносится |
| to-excluded | 1355 | цель есть, но не переносится (служебное, ассет, мусор) — сломается |
| to-kimi | 0 | ведёт в kimi-research (донор) — заменить при уборке |
| missing | 1146 | цели нет уже сейчас (или путь условный) |
| outside | 0 | абсолютный путь вне базы |
| short-unresolved | 237 | адрес «NN/MM» не нашёл файла (часто — номер раздела) |

Сломаются — по источнику ссылки и типу цели:

| тип цели | из md | из данных | из кода | всего |
|---|---|---|---|---|
| ассет | 30 | 71 | 221 | 322 |
| служебное | 815 | 199 | 19 | 1033 |

Примеры to-excluded:
- `00-glossary/README.md:20 → 99-raw/notes/wave4/S-build/`
- `00-glossary/glossary.md:545 → ../99-raw/phase5/README.md`
- `00-glossary/glossary.md:561 → ../99-raw/tools/README.md`
- `00-glossary/glossary.md:569 → ../99-raw/tools/README.md`
- `00-glossary/glossary.md:571 → ../99-raw/reports/wave4-X-audit.md`
- `00-glossary/glossary.md:581 → ../99-raw/phase5/plan-summary.md`
- `00-glossary/glossary.md:583 → 99-raw/phase5/jobs/`
- `00-glossary/glossary.md:583 → ../99-raw/phase5/README.md`
- `01-web-assets-landscape/01-asset-slots-by-page-type.md:647 → 99-raw/experiments/A/`
- `01-web-assets-landscape/02-live-sites-measured.md:7 → 99-raw/experiments/A/01-site-inventory/`
- `01-web-assets-landscape/02-live-sites-measured.md:56 → 99-raw/tools/README.md`
- `01-web-assets-landscape/02-live-sites-measured.md:211 → 99-raw/experiments/A/03-lcp-by-hero/`

Примеры missing:
- `00-glossary/glossary.md:81 → wan/2.5`
- `00-glossary/glossary.md:201 → google/gemini-omni-1.1-flash`
- `00-glossary/glossary.md:205 → bytedance/seedance-1.5-pro`
- `00-glossary/glossary.md:293 → qwen/image-2.1`
- `00-glossary/glossary.md:297 → qwen/image-2.1`
- `00-glossary/glossary.md:594 → 02-providers-platforms/01`
- `00-glossary/glossary.md:594 → 12-legal-provenance/04`
- `00-glossary/glossary.md:594 → 05-prompting/06`
- `00-glossary/glossary.md:595 → 13-routing-matrix/03`
- `00-glossary/glossary.md:595 → 13-routing-matrix/04`
- `00-glossary/glossary.md:595 → 12-legal-provenance/04`
- `00-glossary/glossary.md:596 → 09-video-pipeline/01`

## Входящие ссылки из соседних ресерчей

Всего 471: site-research 281; creative-research 127; text-research 52; claude-design-research 7; blender-research 4. Самые цитируемые файлы: `ai-media-research/01-web-assets-landscape/01-asset-slots-by-page-type.md` 133; `ai-media-research/05-prompting/asset-spec.schema.json` 66; `ai-media-research/11-evaluation-qa/02-vlm-critic-and-rubrics.md` 25; `ai-media-research/13-routing-matrix/routing.yaml` 24; `ai-media-research/10-web-integration/01-images-delivery.md` 23; `ai-media-research/01-web-assets-landscape/02-live-sites-measured.md` 22; `ai-media-research/10-web-integration/03-text-over-media-and-effects.md` 21; `ai-media-research/01-web-assets-landscape/03-ai-fit-trust-and-slop.md` 19; `ai-media-research/01-web-assets-landscape/sites.csv` 19; `ai-media-research/12-legal-provenance/04-agent-policy.md` 19

## Короткие адреса и указатели

- адресов «NN/MM» (свои и «<база> NN/MM»): 805, из них файл не найден: 237 — зависят от нумерации папок и файлов
- указателей «→ … §» в тексте: 1679 — зависят от нумерации разделов внутри файлов

## Дубли утилит (md5) в других ресерчах

- `ai-media-research/99-raw/tools/asset_inventory.py` = `creative-research/99-raw/tools/asset_inventory.py`, `site-research/99-raw/tools/asset_inventory.py`
- `ai-media-research/99-raw/tools/color.py` = `creative-research/99-raw/tools/color.py`, `site-research/99-raw/tools/color.py`, `ui-research/99-raw/tools/color.py`
- `ai-media-research/99-raw/tools/fetch.py` = `blender-research/99-raw/tools/fetch.py`, `claude-design-research/99-raw/tools/fetch.py`, `creative-research/99-raw/tools/fetch.py`, `site-research/99-raw/tools/fetch.py`, `text-research/99-raw/tools/fetch.py`, `ui-research/99-raw/tools/fetch.py`, `ux-research/99-raw/tools/fetch.py`
- `ai-media-research/99-raw/tools/render_fetch.py` = `blender-research/99-raw/tools/render_fetch.py`, `claude-design-research/99-raw/tools/render_fetch.py`, `creative-research/99-raw/tools/render_fetch.py`, `site-research/99-raw/tools/render_fetch.py`, `text-research/99-raw/tools/render_fetch.py`, `ui-research/99-raw/tools/render_fetch.py`, `ux-research/99-raw/tools/render_fetch.py`
- `ai-media-research/99-raw/tools/site_probe.py` = `blender-research/99-raw/tools/site_probe.py`, `creative-research/99-raw/tools/site_probe.py`, `site-research/99-raw/tools/site_probe.py`, `text-research/99-raw/tools/site_probe.py`
- `ai-media-research/99-raw/tools/vtt2md.py` = `claude-design-research/99-raw/tools/vtt2md.py`, `creative-research/99-raw/tools/vtt2md.py`, `site-research/99-raw/tools/vtt2md.py`, `text-research/99-raw/tools/vtt2md.py`
- `ai-media-research/99-raw/tools/yt_dl.py` = `claude-design-research/99-raw/tools/yt_dl.py`, `creative-research/99-raw/tools/yt_dl.py`, `site-research/99-raw/tools/yt_dl.py`, `text-research/99-raw/tools/yt_dl.py`
- `ai-media-research/99-raw/tools/yt_transcript.py` = `blender-research/99-raw/tools/yt_transcript.py`, `claude-design-research/99-raw/tools/yt_transcript.py`, `creative-research/99-raw/tools/yt_transcript.py`, `site-research/99-raw/tools/yt_transcript.py`, `text-research/99-raw/tools/yt_transcript.py`

## Kimi / K3

0 строк в 0 переносимых файлах.

## «Внешнее» — оценка объёма финальной уборки

- ссылок в исключаемое (служебное и т. п.): 1355; строк с упоминанием служебных папок: 1344
- ссылок в соседние ресерчи: 173 (из них в kimi: 0)
- меток роликов `[V:…]`: 581
- строк про Kimi/K3: 0
