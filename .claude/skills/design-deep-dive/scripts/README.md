# Утилиты скилла design-deep-dive

Указатель собран при переносе из списка утилит сборки (`tools-map.tsv`).
Пути — от `scripts/`. Запуск — Python окружения: `~/.cache/design-deep-dive/venv/bin/python scripts/<домен>/<утилита>.py --help`;
пути к базе, выходы, кэши, блокировки, бинарники — `lib/kbpaths.py` (`python3 lib/kbpaths.py` показывает, что где).
Окружение ставит `install.sh` (`--dry-run` — только показать план); проверка — `tests/smoke.py`.

Колонки: назначение — первая фраза описания утилиты; вход — как её запускать (подробно — `--help` и README домена);
выход — куда пишет по умолчанию (`$DDD_HOME` = `~/.cache/design-deep-dive`); зависимости — Python, npm, бинарники.

## lib — общие модули

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `lib/color.py` | module | Расчёты цвета для интерфейсов без внешних зависимостей. | `--help` | stdout / `--out` | stdlib |

## ux — логика продукта

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `ux/checklist_export.py` | utility | Экспорт сводного чек-листа в YAML. | см. докстринг | `kb/ux/12-evaluation-checklists/master-checklist.yaml` | PyYAML |

## ui — визуальный язык

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `ui/build_reference_tokens.py` | utility | Генератор эталонной схемы токенов для `09-design-tokens/04-reference-token-schema.md`. | `--help` | `--out`: tokens.json, tokens.css, theme.css, report.txt | stdlib |
| `ui/measure_ui.py` | utility | Измерить визуальный слой живой веб-страницы через headless-браузер (Playwright/Chromium). | `--help` | `$DDD_HOME/out/ui/measurements`, `$DDD_HOME/out/ui/screens` | playwright; chromium (Playwright) |
| `ui/ui_audit.py` | utility | Объединённый прогон визуального QA страницы: измерение + сверка с токенами и порогами базы + отчёт. | `--help` | `$DDD_HOME/out/ui/audit` | playwright; chromium (Playwright) |

## site — сайты и лендинги

Подробный README домена — `site/README.md` (из базы).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `site/ab_plan.py` | utility | план и проверка A/B-теста страницы сайта. | `--help` | stdout / `--out` | stdlib |
| `site/checklist_export.py` | utility | сводный чек-лист сайта из Markdown в YAML. | `--help` | `kb/site/09-ai-generation-evaluation/site-checklist.yaml` | PyYAML |
| `site/geo_probe.py` | utility | доступность страницы для поисковых и ИИ-ботов. | `--help` | stdout / `--out` | PyYAML, playwright, requests, urllib3; chromium (Playwright, --render) |
| `site/ia_probe.py` | utility | структура многостраничного сайта по HTTP. | `--help` | `$DDD_HOME/out/site/ia_probe/selftest`, `$DDD_HOME/out/site/ia_probe` | stdlib |
| `site/page_anatomy.py` | utility | анатомия живой посадочной страницы или страницы сайта. | `--help` | `$DDD_HOME/cache/site` | Pillow, playwright; web-vitals 6.2.2; chromium (Playwright) |
| `site/page_gates.py` | utility | единые ворота страницы по профилю бюджета. | `--help` | stdout / `--out` | PyYAML |
| `site/plan_to_assets.py` | utility | каркас плана ассетов ai-media из медиа- и 3D-слотов page-plan. | `--help` | stdout / `--out` | PyYAML |
| `site/site_validate.py` | utility | схемы и перекрёстные ссылки контрактов сайта. | `--help` | stdout / `--out` | PyYAML, jsonschema, referencing |
| `site/vocab_lint.py` | utility | проверка YAML, JSON и Markdown на идентификаторы вне словаря site-research. | `--help` | stdout / `--out` | PyYAML |
| `site/build_profile.py` | step | маркетинговый профиль UX-чек-листа для сайта. генератор kb/site/…/ux-marketing-profile.tsv и kb/site/99-raw/experiments/K/02-ux-profile/ac-profile.tsv; сводка — в $DDD_HOME/out | `--help` | `kb/site/09-ai-generation-evaluation/ux-marketing-profile.tsv`, `kb/site/99-raw/experiments/K/02-ux-profile/ac-profile.tsv` | PyYAML |
| `site/run_axe_targets.py` | step | K/03 — axe-core 4.13 с адресами узлов: какие элементы проваливают color-contrast и прочие правила SG-A11Y-01. нет main и --help: запуск сразу поднимает браузер (Playwright) — смоук только компиляция; axe-core — из $DDD_HOME/node | см. докстринг | stdout / `--out` | playwright; axe-core 4.13.0; chromium (Playwright) |

Данные кода: `site/README.md`.

## text — тексты

Подробный README домена — `text/README.md` (из базы).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `text/claims_check.py` | utility | сверка текстов сайта с белым списком фактов (facts.yaml): ядро «контура честности» text-research. | `--help` | stdout / `--out` | PyYAML |
| `text/copy_extract.py` | utility | страница (URL или сохранённый HTML) → структурированный текст по слотам (JSON). | `--help` | stdout / `--out` | Pillow, playwright; chromium (Playwright) |
| `text/copy_lint.py` | utility | линтер маркетинговых текстов RU/EN по жанрам. | `--help` | stdout / `--out` | PyYAML, pymorphy3 |
| `text/copydeck.py` | utility | copy deck text-research: проверка формата, сверка с фактами, линтер, экспорт в пакет kimi и обратно. | `--help` | stdout / `--out` | PyYAML, jsonschema |
| `text/ux_dict_to_yaml.py` | utility | конвертер словарей ux 07/06 (Markdown-таблицы) в YAML-правила copy_lint.py. | `--help` | `kb/text/06-anti-slop/lexicon/ux-07-06.yaml` | PyYAML |
| `text/chain_inputs.py` | step | проекции входов промтов P2–P7 и «код между шагами» цепочки генерации copy deck. | `--help` | stdout / `--out` | PyYAML |
| `text/check_intake.py` | step | проверка выхода промта P1 (разбор брифа) кодом. | `--help` | stdout / `--out` | PyYAML |
| `text/make_skeleton.py` | step | иерархия сообщений (B1) → скелет copy deck v1 (J) для шага S5 цепочки. | `--help` | stdout / `--out` | PyYAML |
| `text/run_checks.py` | step | J/08: все проверки примеров 10-templates-recipes/examples/*.yaml в порядке E и I: claims_check.py --legal-category → copy_lint.py → copydeck.py check → copydeck.py valida… решение B — взять (единственная сквозная проверка 8 эталонов copy deck); AGENTS.md рядом не берётся; выход — $DDD_HOME/out/text/run_checks | `--help` | `$DDD_HOME/out/text/run_checks` | PyYAML |
| `text/validate_any.py` | step | проверки B1 (схема + смысл) для meaning и иерархий вне 02-strategy-messaging/examples/. импорт B1 validate по пути опыта → import validate_meaning | см. докстринг | stdout / `--out` | jsonschema |
| `text/validate_facts.py` | step | B2/01 — проверка схем B2: загрузка yaml.safe_load, метасхема draft 2020-12, валидация примеров и отрицательных случаев. переименован: B2 validate.py → validate_facts.py (facts, voc); нет main — проверки идут при импорте, запуск без ключей и есть самопроверка | `--help` | stdout / `--out` | PyYAML, jsonschema |
| `text/validate_meaning.py` | step | Проверка схем B1 (meaning, message-hierarchy) и примеров: загрузка, JSON Schema 2020-12, смысловые проверки. переименован: B1 validate.py → validate_meaning.py (схемы meaning и message-hierarchy); validate_any импортирует его | `--help` | stdout / `--out` | PyYAML, jsonschema |
| `text/validate_voice.py` | step | проверка voice.schema.yaml (F) и профилей голоса: схема, смысловые проверки, отрицательные мутации. | `--help` | stdout / `--out` | PyYAML, jsonschema |

Данные кода: `text/README.md`.

## creative — подача и движение

Подробный README домена — `creative/README.md` (из базы).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `creative/marketing_audit.py` | utility | профиль визуальных проверок `marketing` поверх ui_audit.py. | `--help` | `$DDD_HOME/out/creative/audit` | Pillow, PyYAML, numpy, playwright; chromium (Playwright) |
| `creative/motion_check.py` | utility | цикл проверки сборки: запись → кадры → метрики → сверка с motion-spec → ворота эффектов → отчёт. | `--help` | `$DDD_HOME/out/creative/motion` | Pillow, PyYAML, brotli, numpy, playwright; chromium (Playwright), ffmpeg, flock |
| `creative/refs_client.py` | utility | клиент референсов creative-research. | `--help` | `$DDD_HOME/cache/creative/refs` | Pillow, numpy, playwright; brave 153 (DDD_BRAVE или PATH), chromium |
| `creative/ad_check.py` | step | опыты A/01 и A/02: проверка примеров art-direction. нет main и --help: проверки идут при запуске; вывод → $DDD_HOME/out/creative/ad_check | `--help` | `$DDD_HOME/out/creative/ad_check` | PyYAML, jsonschema, referencing |
| `creative/idle_probe.py` | step | J/02 · зонд «рисует ли холст в покое» — два снимка счётчика вызовов WebGL внутри одной паузы. без --help: запуск поднимает браузер | см. докстринг | stdout / `--out` | playwright; chromium (Playwright) |
| `creative/recipe_check.py` | step | проверка рецептов 10-recipes/recipes/*.recipe.yaml. | `--help` | stdout / `--out` | PyYAML, jsonschema |
| `creative/registry_check.py` | step | H/03: проверка cliche-registry.yaml — обязательные поля и словари, кластеры, id; разрешение ссылок cliche:<id> в файлах базы. нет main: запуск = проверка реестра клише | `--help` | stdout / `--out` | PyYAML |
| `creative/spec_check.py` | step | проверки и проекции подачи для исполнителя. | `--help` | stdout / `--out` | PyYAML, jsonschema, referencing |
| `creative/validate_stack.py` | step | Проверка 07-stack-implementation/stack.yaml: YAML, обязательные поля, уникальность id, effect-id по treatment.v0, ссылки alternatives. нет main: запуск = проверка stack.yaml | `--help` | stdout / `--out` | PyYAML |
| `creative/scroll_record.py` | module | запись прокрутки страницы и движение в паузах. | модуль / без `--help` | stdout / `--out` | Pillow, numpy, playwright; chromium (Playwright), ffmpeg, ffprobe |

Данные кода: `creative/README.md`.

## ai-media — картинки и видео

Подробный README домена — `ai-media/README.md` (из базы).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `ai-media/alpha_check.py` | utility | проверка прозрачности (вырез, нативная альфа модели, матирование). | `--help` | stdout / `--out` | Pillow, numpy, scipy |
| `ai-media/asset_audit.py` | utility | единая автоматическая приёмка ИИ-ассетов сайта. | `--help` | `$DDD_HOME/out/ai-media/audit`, `$DDD_HOME/cache/ai-media/polza` | Pillow, PyYAML, numpy, rapidocr, scipy; ffmpeg, ffprobe, flock; $DDD_HOME/bin: exiftool, c2patool, libjxl (ssimulacra2, djxl), libavif (avifdec), libwebp (dwebp); models/ocr |
| `ai-media/asset_inventory.py` | utility | инвентарь визуальных ассетов живой страницы. | `--help` | stdout / `--out` | Pillow, playwright; chromium (Playwright) |
| `ai-media/avif_pick.sh` | utility |  | см. докстринг | stdout / `--out` | $DDD_HOME/bin: libavif 1.4.2 (avifenc, avifdec), libjxl 0.12.0 (ssimulacra2) |
| `ai-media/edit_check.py` | utility | проверка правки картинки нейросетью и композит оригинала обратно. | `--help` | stdout / `--out` | Pillow, numpy, scipy |
| `ai-media/mp_client.py` | utility | клиент каналов фазы 5 вне Media API polza: RouterAI, Gen-API, polza-chat, polza-images. | `--help` | `$DDD_HOME/cache/ai-media`, `$DDD_HOME/out/ai-media`, `$DDD_HOME/out/ai-media/_mp` | Pillow; ffprobe (необязательно) |
| `ai-media/page_accept.py` | utility | приёмка страницы с ИИ-ассетами в Chromium. | `--help` | stdout / `--out` | Pillow, numpy, playwright, scipy; chromium (Playwright) |
| `ai-media/polza.py` | utility | клиент Media API polza.ai для ai-media-research: сухой прогон по умолчанию, трата только с --live. | `--help` | `$DDD_HOME/out/ai-media`, `$DDD_HOME/out/ai-media/_polza` | Pillow; ffprobe (необязательно) |
| `ai-media/polza_catalog.py` | utility | каталог polza.ai как данные: снимки, нормализация медиа-моделей, таблица, сравнение снимков, калькулятор цены и валидатор входа по каталогу (библиотека для polza.py). | `--help` | `$DDD_HOME/cache/ai-media/polza` | stdlib |
| `ai-media/prompt_compile.py` | utility | компилятор промтов: спецификация ассета → промт в диалекте модели + параметры задания. | `--help` | stdout / `--out` | Pillow, PyYAML, jsonschema |
| `ai-media/provenance_check.py` | utility | бесплатная проверка провенанса ИИ-ассетов (0 ₽, без сети). | `--help` | `$DDD_HOME/cache/ai-media/c2pa-trust-2026-09-23` | Pillow, numpy, scipy; ffmpeg; $DDD_HOME/bin: exiftool 13.59, c2patool 0.27.22 |
| `ai-media/routing_check.py` | utility | проверка 13-routing-matrix/routing.yaml. | `--help` | `$DDD_HOME/out/ai-media/phase5/jobs` | PyYAML |
| `ai-media/stand_run.py` | utility | стенд моделей ai-media-research: задания фазы 5, сбор результатов, автометрики, контактные листы, страница слепого попарного голосования, подсчёт голосов, мини-стенд ново… | `--help` | `$DDD_HOME/out/ai-media/phase5/jobs`, `$DDD_HOME/out/ai-media/_polza/E` | Pillow, PyYAML, numpy, scipy |
| `ai-media/tile_check.py` | utility | бесшовность текстуры: метрика шва, тайл разрезом минимальной ошибки, превью. | `--help` | stdout / `--out` | Pillow, numpy |
| `ai-media/video_loop_check.py` | utility | приёмка ИИ-видео для сайта: шов петли, «живость», мёртвые концы, склейки, дрейф неподвижных зон и камеры, однородность хромакея, стык клипов цепочки, контактный лист. | `--help` | stdout / `--out` | Pillow, numpy, scipy; ffmpeg, ffprobe |
| `ai-media/vlm_to_dna.py` | utility | паспорт визуала бренда (visual DNA): VLM-бриф сетки бренд-картинок → черновик паспорта, проверка по схеме и смыслу, сверка прогонов, грейд .cube, вывод из токенов UI, спе… | `--help` | `$DDD_HOME/out/ai-media/phase5/jobs` | Pillow, jsonschema, numpy |
| `ai-media/channel_diff.py` | step | N/04 — разница двух снимков каталогов RouterAI и Gen-API (дополнение к polza_catalog.py diff). разница снимков каналов; нет main — запуск при импорте | см. докстринг | `$DDD_HOME/cache/ai-media` | stdlib |
| `ai-media/layout_check.py` | step | M/06b — проверка вёрстки текстового шаблона по DOM (до OCR): прямоугольники строк текста (Range.getClientRects) не выходят DOM-проверка шаблона OG; входы опыта M/06 (шаблон, вырез) не переносятся | см. докстринг | `$DDD_HOME/out/ai-media/layout_check` | Pillow, playwright; chromium (Playwright) |
| `ai-media/loop_rife_bridge.py` | step | RIFE-мост петли: k промежуточных кадров от последнего кадра к первому (оптический поток RIFE v4.6, ncnn/Vulkan), без RIFE-мост петли; нет main | см. докстринг | stdout / `--out` | ffmpeg; $DDD_HOME/bin: rife-ncnn-vulkan (v4.6, Vulkan) |
| `ai-media/split_recraft.py` | step | B/14 — нарезка сетки иконок Recraft на отдельные SVG для лендинга. нарезка сетки иконок Recraft; svgo — из $DDD_HOME/node | см. докстринг | stdout / `--out` | svgelements; svgo 4.1.0; node (svgo) |
| `ai-media/svg_sheet.py` | step | разбор SVG (Recraft, LLM → SVG): метрики, гигиена с сохранением подписи, листы на светлом и тёмном фоне. recolor и листы SVG | `--help` | stdout / `--out` | Pillow, cairosvg, numpy; svgo 4.1.0; node (svgo) |
| `ai-media/validate_recipes.py` | step | M/10 — проверка 14-recipes/recipes/*.yaml: схема (jsonschema, venv-D2), существование файлов (doc, spec.example, валидатор рецептов 14-recipes; нет main — запуск при импорте | см. докстринг | `$DDD_HOME/out/ai-media/validate_recipes` | PyYAML, jsonschema |
| `ai-media/vm_sheet.py` | step | лист видео-моделей: кадры 0/25/50/75/100 %, метрики `video_loop_check.py`, цена и время из паспорта. листы видео | `--help` | stdout / `--out` | Pillow, numpy; ffmpeg |
| `ai-media/check_icons.py` | module | G · проверка SVG-иконки по нормам ui-research 07/01 и спецификации Lucide (кодом, без глаз). | `--help` | stdout / `--out` | Pillow, cairosvg, numpy, scikit-image, scipy, svgelements |
| `ai-media/composition_metrics.py` | module | F/04 composition_metrics.py — маркеры «среднего вида» и пригодности кадра под веб, кодом. | модуль / без `--help` | stdout / `--out` | Pillow, numpy, scipy |
| `ai-media/image_metrics.py` | module | Опыт A/04: простые метрики маркеров «сгенерированности» (IMG-M01, M03, M04, M05, M17) на картинках живых сайтов. | модуль / без `--help` | stdout / `--out` | Pillow, numpy, scipy |
| `ai-media/palette.py` | module | F/05 palette.py — палитра (k-means в OKLab с долями), ΔE к эталону, перенос цвета (Reinhard, MKL) и экспорт 3D LUT (.cube). | модуль / без `--help` | stdout / `--out` | Pillow, numpy |
| `ai-media/series_metrics.py` | module | F/06 series_metrics.py — согласованность серии картинок без платных судей. | модуль / без `--help` | stdout / `--out` | Pillow, numpy |
| `ai-media/split_grid.py` | module | F/06 split_grid.py — разрезать сетку R×C одной генерации на ячейки: поиск светлых/ровных «желобов», иначе — равное деление. | модуль / без `--help` | stdout / `--out` | Pillow, numpy |
| `ai-media/text_zone.py` | module | F/02 text_zone.py — контраст HTML-текста поверх картинки по зоне и минимальный скрим. | модуль / без `--help` | stdout / `--out` | Pillow, numpy |
| `ai-media/tests/test_asset_audit.py` | test | Тесты asset_audit.py. | `--help` | stdout / `--out` | Pillow, numpy, scipy; ffmpeg |
| `ai-media/tests/test_prompt_compile.py` | test | Офлайн-тесты prompt_compile.py v2. | `--help` | stdout / `--out` | Pillow |
| `ai-media/tests/test_prompt_compile_x2.py` | test | Офлайн-тесты исправлений prompt_compile.py v2.1.1. | `--help` | stdout / `--out` | stdlib |

Данные кода: `ai-media/README.md`, `ai-media/data/svgo.keep-signature.config.mjs`, `ai-media/tests/fixtures/D02/E1.spec.json`, `ai-media/tests/fixtures/D02/E2.spec.json`, `ai-media/tests/fixtures/D02/E3.spec.json`, `ai-media/tests/fixtures/D02/E4.spec.json`, `ai-media/tests/fixtures/D02/E5.spec.json`, `ai-media/tests/fixtures/D03/B1.spec.json`, `ai-media/tests/fixtures/D03/B2.spec.json`, `ai-media/tests/fixtures/frame-A.png`, `ai-media/tests/fixtures/mask-white-change.png`, `ai-media/tests/fixtures/product.png`, `ai-media/tests/fixtures/source.png`, `ai-media/tests/fixtures/style-ref.png`, `ai-media/tests/fixtures/v2-edit.spec.json`, `ai-media/tests/fixtures/v2-loop.spec.json`, `ai-media/tests/fixtures/v2-product.spec.json`, `ai-media/tests/fixtures/v2-series.spec.json`, `ai-media/tests/fixtures/v2-shots.spec.json`.

## blender — 3D

Подробный README домена — `blender/README.md` (из базы).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `blender/anim_diff.py` | utility | анимация «как в Blender» против «как в three r186» в ОДНИ И ТЕ ЖЕ моменты. | `--help` | stdout / `--out` | playwright; three 0.186.0 (с jsDelivr, сеть); blender 5.2.2, chromium (Playwright) |
| `blender/blender_run.py` | utility | Запуск Python-кода в Blender без окна (background) с таймаутом, кодом выхода и журналом. | `--help` | `$DDD_HOME/out/blender/logs` | blender 5.2.2 |
| `blender/blender_supervisor.py` | utility | фоновый Blender 5.2 под надзором для агента. | `--help` | stdout / `--out` | blender 5.2.2, bwrap, systemd-run |
| `blender/bpy_probe.py` | utility | справочник по Python API, который отвечает сам Blender (JSON). | `--help` | stdout / `--out` | numpy; blender 5.2.2 |
| `blender/fx_probe.py` | utility | замер своей демо-страницы с 3D/шейдерным эффектом. | `--help` | stdout / `--out` | Pillow, playwright; chromium (Playwright) |
| `blender/gate_check.py` | utility | общий модуль ворот качества страницы с 3D по отчёту site_probe.py. | `--help` | stdout / `--out` | stdlib |
| `blender/gltf_check.py` | utility | Проверка glTF/GLB: валидатор Khronos + инспекция gltf-transform + сводка «готово ли для веба». | `--help` | stdout / `--out` | @gltf-transform/cli 4.5.0, gltf-validator 2.0.0-dev.3.10, gltfpack 1.2.0, meshoptimizer 1.2.0, draco3dgltf 1.5.7; node (gltf-transform, gltf-validator, gltfpack) |
| `blender/gltf_diff.py` | utility | сравнение «как выглядит в Blender» и «как выглядит в three.js» при ОДИНАКОВЫХ камере, свете и тонмаппинге. | `--help` | stdout / `--out` | Pillow, numpy, playwright; three 0.186.0 (с jsDelivr, сеть); blender 5.2.2, chromium (Playwright) |
| `blender/gltf_load_bench.py` | utility | замер загрузки GLB в three.js (r186) в headless Chromium на GPU: холодная загрузка (с докачкой декодеров с jsDelivr), тёплые загрузки (декодеры готовы; медиана N), первый… | `--help` | stdout / `--out` | playwright; three 0.186.0 (с jsDelivr, сеть); chromium (Playwright) |
| `blender/gltf_web_inspect.py` | utility | что three.js (r186 по умолчанию) реально создаёт из glTF/GLB: дамп сцены в JSON. | `--help` | stdout / `--out` | playwright; three 0.186.0 (с jsDelivr, сеть); chromium (Playwright) |
| `blender/img_metrics.py` | utility | числа кадра до глаз и до судьи. | `--help` | stdout / `--out` | Pillow, numpy |
| `blender/lint_agent_code.py` | utility | самопроверка текста скрипта агента регулярными выражениями до отправки в Blender (агент U, волна 4 — CLI из кода lint_agent_code() в 02-blender-workflow/03-patterns-antip… | см. докстринг | stdout / `--out` | stdlib |
| `blender/node/validate.mjs` | utility |  | см. докстринг | stdout / `--out` | gltf-validator 2.0.0-dev.3.10; node 24 |
| `blender/qa_pipeline.py` | utility | сводный конвейер проверок: сцена → GLB → страница; JSON с порогами и вердиктом. | `--help` | stdout / `--out` | blender 5.2.2, node, chromium (Playwright) |
| `blender/render_views.py` | utility | Рендер модели с нескольких ракурсов + контактный лист + статистика геометрии. | см. докстринг | stdout / `--out` | numpy; blender 5.2.2 (внутри) |
| `blender/run_doc_blocks.py` | utility | исполнить блоки кода итоговых .md в напечатанном виде; обобщение раннеров D2/99 (run_all.py), E/26 (md_blocks.py + run_md.py), H/30, F2/09. | см. докстринг | stdout / `--out` | blender 5.2.2 |
| `blender/scene_check.py` | utility | Blender 5.2.2 — scene_check.py: проверка сцены и ассета кодом, одна строка JSON. | см. докстринг | stdout / `--out` | blender 5.2.2 (внутри) |
| `blender/sheet.py` | utility | лист сравнения кадров с подписями (испытание 15-showcase). | см. докстринг | stdout / `--out` | Pillow |
| `blender/site_probe.py` | utility | замер живого 3D-сайта. | `--help` | stdout / `--out` | Pillow, playwright; chromium (Playwright) |
| `blender/slot_run.py` | utility | очередь для тяжёлых запусков, когда параллельно работают несколько агентов. | см. докстринг | stdout / `--out` | flock (очередь для blender и браузера) |
| `blender/three_probe.py` | utility | загрузить GLB в three r186 (Chromium, GPU) и выполнить JS-проверку; вывести JSON. | см. докстринг | stdout / `--out` | playwright; three 0.186.0 (с jsDelivr, сеть); chromium (Playwright) |
| `blender/vote/build_pairs.py` | utility | собрать pairs.json и img/ страницы «Кадр против кадра» из кадров судьи предметов. | см. докстринг | `blender/vote/{img/,pairs.json}` — папка страницы голосования | Pillow |
| `blender/vote/tally.py` | utility | итоги слепого голосования «Кадр против кадра» → results.json, results.md и блок в вердикте. | см. докстринг | блок итогов в `kb/blender/15-showcase/VERDICT.md`; results.* рядом со страницей | stdlib |
| `blender/vote/vote_server.py` | utility | локальный сервер страницы «Кадр против кадра». | см. докстринг | `blender/vote/votes/` (или `--dir`) | stdlib |
| `blender/web_view.py` | utility | Проверка 3D в браузере: GLB в three.js или готовая страница — через headless Chromium на реальной видеокарте. | `--help` | stdout / `--out` | Pillow, playwright; three 0.186.0 (с jsDelivr, сеть); chromium (Playwright) |
| `blender/run_recipes.py` | step | K/01 — сквозной прогон рецептов 12-recipes: блоки ```python рецепта (в напечатанном виде, по порядку) → один скрипт examples/<slug>/build.py → Blender 5.2.2 без окна (ble… сквозной прогон рецептов (K/01); без --help | см. докстринг | `$DDD_HOME/out/blender/run_recipes` | blender 5.2.2, ffmpeg |
| `blender/agent_scene.py` | module | Blender 5.2.2 — [проверено: 99-raw/experiments/I/01-own-collection-vs-wipe] работа агента в чужой сцене: | модуль / без `--help` | stdout / `--out` | blender 5.2.2 (внутри) |
| `blender/animx.py` | module | animx — помощники анимации для Blender 5.2. | модуль / без `--help` | stdout / `--out` | blender 5.2.2 (внутри) |
| `blender/bpyx.py` | module | bpyx — проверенные помощники Python API для Blender 5.2. | модуль / без `--help` | stdout / `--out` | numpy; blender 5.2.2 (внутри) |
| `blender/d1exp.py` | module | Blender 5.2.2 — помощники экспериментов D1: рендер варианта в плитку, контактный лист, разбор GLB, постобработка. | модуль / без `--help` | stdout / `--out` | numpy; @gltf-transform/cli 4.5.0; blender 5.2.2 (внутри), node (npx gltf-transform) |
| `blender/d1lib.py` | module | d1lib — помощники моделирования кодом для Blender 5.2. | модуль / без `--help` | stdout / `--out` | numpy, scipy; blender 5.2.2 (внутри) |
| `blender/d2lib.py` | module | d2lib — помощники D2 поверх bpyx (Blender 5.2.2): циклорама, студийные схемы света от размера ассета, паспорт серии. | модуль / без `--help` | stdout / `--out` | blender 5.2.2 (внутри) |
| `blender/glb_lint_block.py` | module | Python 3.10+ (без bpy) — [проверено: 99-raw/experiments/E/26-doc-snippets/glb_lint_result.json, run_md04.py] проверка готового GLB: | модуль / без `--help` | stdout / `--out` | stdlib |
| `blender/hygiene.py` | module | Blender 5.2.2 — [проверено: 99-raw/experiments/I/02-file-hygiene] гигиена СВОЕГО файла агента: отчёт и чистка | модуль / без `--help` | stdout / `--out` | blender 5.2.2 (внутри) |
| `blender/passport_asserts.py` | module | Blender 5.2.2 — утверждения по паспорту ассета: габариты, контакты частей, бюджет треугольников (C1/16) | модуль / без `--help` | stdout / `--out` | blender 5.2.2 (внутри) |
| `blender/preflight_block.py` | module | Blender 5.2.2 / glTF-IO 5.2.40 — [проверено: 99-raw/experiments/E/26-doc-snippets/preflight_test.py, run_md04.py] предэкспортная проверка сцены для веба | модуль / без `--help` | stdout / `--out` | blender 5.2.2 (внутри) |
| `blender/presets.py` | module | Blender 5.2.2 / glTF-Blender-IO 5.2.40 — пресеты bpy.ops.export_scene.gltf для веба (three r186). | модуль / без `--help` | stdout / `--out` | @gltf-transform/cli 4.5.0; blender 5.2.2 (внутри); gltfpack, toktx для постобработки |
| `blender/rk.py` | module | rk — набор рецептов 12-recipes. | модуль / без `--help` | `kb/blender/12-recipes/examples/<рецепт>/` (постер, GLB, numbers.json) | numpy; @gltf-transform/cli 4.5.0; blender 5.2.2 (внутри), node (npx gltf-transform); $DDD_HOME/bin: gltfpack 1.2, KTX-Software 4.4.2 (toktx) |
| `blender/scene_audit.py` | module | Blender 5.2.2 — аудит сцены для агента (отправляется целиком через execute_blender_code или запускается в фоне) | модуль / без `--help` | stdout / `--out` | blender 5.2.2 (внутри) |
| `blender/serve_br.py` | module | Локальный сервер «как продакшен-хостинг»: отдаёт предсжатые brotli-файлы (file.br) при Accept-Encoding: br, правильные Content-Type (wasm, glb, ktx2, avif), Cache-Control… | модуль / без `--help` | stdout / `--out` | brotli |
| `blender/regression/make_manifest.py` | maint | Сборка manifest.json регрессионного набора из готовых экспериментов (без новых рендеров). | см. докстринг | stdout / `--out` | stdlib |
| `blender/regression/run_set.py` | maint | прогон регрессионного набора (manifest.json) через qa_pipeline.py и сравнение с базовой линией. | см. докстринг | stdout / `--out` | blender 5.2.2, chromium (через qa_pipeline) |
| `blender/test_agent_helpers.py` | test | Тесты agent_scene.py и hygiene.py для Blender 5.2.x. | модуль / без `--help` | stdout / `--out` | blender 5.2.2 (внутри) |
| `blender/test_bpyx.py` | test | Тесты bpyx.py для Blender 5.2.x. | модуль / без `--help` | stdout / `--out` | blender 5.2.2 (внутри) |

Данные кода: `blender/README.md`, `blender/vote/index.html`.

## claude-design — макеты

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `claude-design/lang_check.py` | utility | Z/04 lang_check: проверка языка готовой вёрстки русскоязычного сайта (без модели, без сети). | см. докстринг | stdout / `--out` | stdlib |
| `claude-design/mockup_checks.py` | utility | проверки арт-директора для сборок Kimi K3: приметы K3, выдумки, мобильная версия, сторож потока. | `--help` | stdout / `--out` | Pillow, playwright; chromium (Playwright) |
| `claude-design/shot_v3.py` | utility | shot.py v3 — «глаза» дизайн-цикла Claude ↔ K3: кадры по экранам + проверки, которых не видно на ужатом кадре. | `--help` | stdout / `--out` | playwright; chromium (Playwright) |
| `claude-design/stand_page.py` | utility | страница слепого попарного выбора для СТЕНДА тестов. | `--help` | stdout / `--out` | Pillow |
| `claude-design/kit/canvas.html` | kit |  | `--help` | stdout / `--out` | stdlib |
| `claude-design/kit/diffshots.py` | kit | «изменилось только то, что просили»: сравнение двух снимков shot.py по меткам #N. | `--help` | stdout / `--out` | Pillow, numpy |
| `claude-design/kit/example/booking.html` | kit |  | `--help` | stdout / `--out` | stdlib |
| `claude-design/kit/example/canvas.json` | kit |  | `--help` | stdout / `--out` | stdlib |
| `claude-design/kit/example/landing.html` | kit |  | `--help` | stdout / `--out` | stdlib |
| `claude-design/kit/example/site.css` | kit |  | `--help` | stdout / `--out` | stdlib |
| `claude-design/kit/example/tokens.css` | kit |  | `--help` | stdout / `--out` | stdlib |
| `claude-design/kit/export.py` | kit | экспорт холста без интерфейса Claude Design: PDF по артбордам, PNG 2×, standalone.html, zip. | `--help` | stdout / `--out` | Pillow, playwright, pypdf; chromium (Playwright) |
| `claude-design/kit/marks.js` | kit |  | см. докстринг | stdout / `--out` | stdlib |
| `claude-design/kit/shot.py` | kit | «глаза» холста для работы из чата: PNG каждого артборда (с метками #N и без), весь холст, marks.json. | `--help` | stdout / `--out` | Pillow, playwright; chromium (Playwright) |

## maint — обслуживание базы

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `maint/calibrate.py` | maint | Калибровка оценки токенов под Opus 5.5 через `claude -p` (API-ключ не нужен). | `--help` | stdout / `--out` | claude (CLI Claude Code, claude -p) |
| `maint/check_links.py` | maint | Проверка перекрёстных ссылок, меток и структуры базы site-research. | `--help` | stdout / `--out` | stdlib |
| `maint/count_tokens.py` | maint | Объём тематического контента в ресерчах app-design: файлы, символы, токены. | `--help` | stdout / `--out` | stdlib |
| `maint/layers.py` | maint | Сколько весят уже готовые «сжатые слои» ресерчей (в токенах Opus 5.5 по calibration.json). | см. докстринг | stdout / `--out` | stdlib |
| `maint/orch_check.py` | maint | Приёмочная проверка файлов site-research. | см. докстринг | stdout / `--out` | PyYAML |

Данные кода: `maint/calibration.json`.

## Данные, которые читает только код

Кроме файлов выше (из tools-map): `ai-media/data/lucide-ref/` (эталонные иконки Lucide, ISC — для `check_icons`),
`ai-media/data/genapi_prices_2026-09-23.json` (прайс Gen-API — `mp_client`), `blender/data/studio_small_09_1k.hdr`
(HDRI по умолчанию `gltf_diff`, CC0) — их кладут правила содержимого.
