# Утилиты blender-research

Все пути — от корня `kb/blender/` (от корня скилла). Проверены оркестратором 22.09.2026 на этой машине
(Debian 13, 20 потоков, 15 ГБ ОЗУ, Intel Iris Xe без CUDA; Blender 5.2.2 LTS; Node 24.21; Chromium из Playwright).

## Веб и видео (скопированы из `../../kb/ux`, формат тот же)

| Утилита | Что делает | Пример |
|---|---|---|
| `fetch.py` | Скачивает страницу в читаемый Markdown в `99-raw/cache/`, PDF — через `pdftotext` | `python3 99-raw/tools/fetch.py "URL"` |
| `render_fetch.py` | То же через headless-браузер: для SPA-документации (docs.blender.org отдаётся и обычным fetch; для r3f.docs.pmnd.rs, spline, needle — этим) | `python3 99-raw/tools/render_fetch.py "URL" --scroll` |
| `yt_transcript.py` | Поиск по YouTube, метаданные, субтитры с таймкодом раз в минуту → `91-videos/transcripts/<id>.md` | `--search "blender geometry nodes" -n 20`, `--info URL`, `URL --comments 40` |
| `transcribe_local.py` | Локальное распознавание речи (Qwen3-ASR 1.7B, CPU, ~0,43 от реального времени) для роликов без субтитров | `python3 99-raw/tools/transcribe_local.py URL` |
| `vtt2md.py` | Собирает транскрипты из уже скачанных `.vtt` и `.info.json` без обращения к YouTube | `python3 99-raw/tools/vtt2md.py ids.txt` |

## Blender

| Утилита | Что делает | Пример |
|---|---|---|
| `blender_run.py` | Запуск скрипта или выражения в Blender без окна: `--factory-startup` по умолчанию, таймаут, код выхода (1 — исключение, 124 — таймаут), журнал в `99-raw/experiments/_logs/`, фильтр шума рендера | `python3 blender_run.py my.py -- арг1 арг2`; `--expr "import bpy; print(bpy.app.version_string)"`; `--blend scene.blend`; `--user-prefs` (с аддонами пользователя) |
| `render_views.py` | Скрипт для Blender: импорт `.glb/.gltf/.fbx/.obj/.stl/.ply/.usd*/.abc` или открытие `.blend`, нейтральная студия, 4 / 6 / N ракурсов, контактный лист, `stats.json` (треугольники после модификаторов, n-гоны, неманифолдные рёбра, неприменённый масштаб, материалы и типы нод, текстуры, габариты) | `python3 blender_run.py render_views.py -- model.glb out/ --views 4 --size 512 [--clay] [--engine workbench]` |
| `bpy_probe.py` (агент B) | Справочник по API, который отвечает сам Blender 5.2.2 (JSON): параметры операторов и `poll()` в фоне, свойства типов и enum, сокеты ноды с учётом режима (`enabled`), список нод дерева, **фактические** значения динамических перечислений, модификаторы, типы сокетов интерфейса, поиск по API, устаревшие свойства, окружение. Замена MCP-инструментам `bpy_api_lookup` и `describe_node_type` без окна и без MCP | `python3 bpy_probe.py node ShaderNodeMix data_type=RGBA`; `op export_scene.gltf --out p.json`; `enum scene.render.engine`; `nodes GeometryNodeTree instance`; `search smooth`; `deprecated`; `env`. Код выхода 3 — ошибка с `did_you_mean`. Запускать напрямую: через `blender_run.py` вывод режется до 400 строк |
| `venv-bpy/` (агент B) — **удалён 23.09.2026 по решению владельца** | `bpy==5.2.2` из PyPI (Python 3.13, 1,0 ГБ) — Blender как модуль для тестов без бинарника; пересоздать при надобности (колесо 402 МБ) | `uv venv --python /usr/bin/python3 99-raw/tools/venv-bpy && uv pip install --python 99-raw/tools/venv-bpy/bin/python bpy==5.2.2` |

Библиотека функций-помощников для кода Blender 5.2 — `bpyx.py` (47 функций, 25/25 тестов в
`blender -b` и в `bpy` из PyPI); подключение — `../../kb/blender/03-bpy-api/snippets/README.md`.

Исправление 23.09 (по находке B): `render_views.py` считал габариты по `bound_box` вычисленного объекта, а у текста
и кривых в 5.2.2 он не учитывает extrude и bevel. Теперь габариты — по вершинам вычисленного меша в мировых
координатах (запасной путь — `bound_box` оригинала после вычисления depsgraph); проверено на тексте с extrude+bevel
и кривой с bevel.

Проверенные факты окружения: EEVEE в фоне работает через EGL на Intel Iris Xe (кадр 480×270 ≈ 4 с), Cycles —
только CPU (16 сэмплов 480×270 ≈ 1 с). Экспорт glTF: «Khronos glTF Blender I/O v5.2.40», Draco и Meshopt доступны.
Встроенный Python Blender 3.13: numpy, OpenImageIO, MaterialX, USD (`pxr`), OpenVDB.

## glTF

| Утилита | Что делает | Пример |
|---|---|---|
| `gltf_check.py` | Валидатор Khronos (JSON-отчёт) + `gltf-transform inspect` + подсказки для веба (несжатая геометрия, PNG, текстуры > 2048, вес > 5 МБ, draw calls > 100) | `python3 gltf_check.py model.glb [--json] [--out report.md]` |
| `node/` | Локальный npm-набор: `gltf-transform` 4.5.0, `gltfpack` 1.2, `gltf-validator`, `meshoptimizer`, `draco3dgltf`; `node/validate.mjs` | `cd 99-raw/tools/node && npx gltf-transform optimize in.glb out.glb --compress meshopt --texture-compress webp`; `npx gltfpack -i in.glb -o out.glb -cc` |

| `gltf_diff.py` (агент E) | «Как в Blender» против «как в three r186»: одна камера (FOV 40°, ракурсы по габариту), один HDRI (по умолчанию `data/studio_small_09_1k.hdr`, CC0), одна пара тонмаппинга (standard↔NoToneMapping, neutral↔NeutralToneMapping, agx↔AgXToneMapping); `diff_sheet.png` (Blender \| three \| карта ΔE), `diff_metrics.json` (IoU силуэтов, ΔE2000 среднее и p95, SSIM по L*). Пороги E/02: ΔE ≤ 3,5 и IoU ≥ 0,99 — совпадает; ΔE > 6 или IoU < 0,95 — поломка | `python3 gltf_diff.py scene.blend out/ --glb model.glb [--tone neutral] [--engine cycles] [--hdri none --keep-lights]`; `--compare A.png B.png out_prefix` |
| `gltf_web_inspect.py` (агент E) | Что three r186 создал из файла (JSON): объекты и их типы, санитизированные имена и `userData`, атрибуты геометрии, морфы, инстансы, материалы с картами (`colorSpace`, `channel`, сжатие), клипы (`--anim-sample T`), вызовы и память первого кадра | `python3 gltf_web_inspect.py model.glb --out report.json` |
| `gltf_load_bench.py` (агент E) | Цена загрузки: холодная и тёплая загрузка, первый кадр (компиляция + заливка текстур), время кадра, вызовы, оценка памяти GPU (геометрия и текстуры, KTX2 — по уровням мипмапов); `--throttle N` — CPU ×N | `python3 gltf_load_bench.py a.glb b.glb --runs 3 [--throttle 4] --json out.json` |

Бинарники без sudo (агент E): `99-raw/tools/bin/KTX-Software-4.4.2-Linux-x86_64/bin/toktx` (добавить в PATH для
`gltf-transform etc1s/uastc/ktx2`) и нативный `99-raw/tools/bin/gltfpack-1.2/gltfpack` (с BasisU и WebP: `-tc`, `-tw`
работают только в нём, npm-сборка их не умеет). Пресеты экспорта с проверкой ключей по RNA и командами постобработки —
`presets.py`; помощники сборки тестовых сцен — `99-raw/experiments/E/_lib/`; извлечь и
исполнить блоки `python` из итогового .md — `99-raw/experiments/E/26-doc-snippets/md_blocks.py` + `run_md.py`.

Предупреждение (E/07, E/24): `bpyx.export_glb(apply_modifiers=True)` по умолчанию удаляет shape keys у объектов с
модификаторами — для морф-анимации экспортировать с `apply_modifiers=False` или применять модификаторы до shape keys.

## Браузер

| Утилита | Что делает | Пример |
|---|---|---|
| `web_view.py` (модель) | GLB в three.js (r186 по умолчанию, jsDelivr) с Draco/KTX2/Meshopt, ракурсы как у `render_views.py`, `web_stats.json`: загрузка, GPU, draw calls, треугольники, материалы, текстуры, extensionsUsed, анимации; `--anim` — кадры анимации | `python3 web_view.py model.glb out/ --tone agx\|neutral\|aces\|none --env room\|none\|file.hdr --bg transparent` |
| `web_view.py --page` | Локальная страница: скриншоты на долях прокрутки, draw calls за кадр (перехват WebGL), FPS при прокрутке, ошибки консоли | `python3 web_view.py --page demo/index.html out/ --scroll 0,0.5,1 [--mobile]` |
| `web_view.py --url` | Живой сайт: то же + вес сети по категориям (3D, текстуры, картинки, видео, JS, WASM), движки (`window.__THREE__` и др.), LCP/CLS/долгие задачи; `--throttle` — CPU ×4 и «медленный 4G» | `python3 web_view.py --url https://site out/ --wait 8000 --throttle` |
| `site_probe.py` (агент A) — **для живых 3D-сайтов вместо `web_view.py --url`** | Вес по фактически переданным байтам (у сжатых на лету ответов нет content-length — `web_view.py` пишет 0), форматы по сигнатуре первых байт (glTF, KTX2, Draco, Basis, EXR, HDR, PLY, WASM), контексты WebGL/WebGL2/WebGPU/OffscreenCanvas, вызовы отрисовки в WebGL и WebGPU, время до первого 3D-кадра, прокрутка колесом (работает с Lenis и виртуальным скроллом), LCP с элементом, TBT до и во время прокрутки, WebGPU включён флагами, `--mobile` (Pixel 7), `--reduced-motion`, кнопки-ворота (`--click`) | `python3 site_probe.py https://site out/ [--mobile] [--throttle] [--reduced-motion] [--click "button.enter"]`; пакетный прогон и сводки — `99-raw/experiments/A/tools/` (`run_list.py`, `summarize.py`) |

Проверено: WebGL2 на реальной видеокарте через ANGLE (GL и Vulkan), `navigator.gpu` присутствует;
threejs.org на 22.09.2026 работает на r186; npm: three 0.186.0, @react-three/fiber 9.7.0, drei 10.7.8,
@babylonjs/core 9.27.1, playcanvas 2.22.3, @google/model-viewer 4.3.1, @needle-tools/engine 6.0.0-alpha.3,
@splinetool/runtime 2.0.55, gsap 3.15.0, lenis 1.3.26, postprocessing 6.39.5, @theatre/core 0.7.2 (последний
релиз май 2024), three-stdlib 2.36.1 (ноябрь 2025).

## Проверка результата (агент J, волна 3; добавлено оркестратором сессии 3)

Процедура и пороги — `../../kb/blender/11-evaluation-qa/` (01 сцена, 02 рендер и критика, 03 ворота GLB и страницы, 04 регрессионный набор,
05 сводный чек-лист). Проверено оркестратором 23.09 18:28: `qa_pipeline.py scene` на `C1/12/out/laptop.blend` — `pass`, Blender 0,5 с.

| Утилита | Что делает | Пример |
|---|---|---|
| `scene_check.py` (агент J) | Проверка сцены **внутри Blender** (напрямую `python3` не запускается — только через `qa_pipeline.py scene` или текстом в `execute_blender_code`; совместима с безопасным режимом MCP). Область ассета — коллекции `ASSET_*`, иначе вся сцена минус подложка (ловец теней, пол шире ассета ×3). Паспорт: `dims_m` ±5 %, `touch` ≤ 1 мм, `on_ground`, `max_tris`, `allow_floating`, `style: lowpoly` — из переменной `PASSPORT` или `coll["passport"]`. Парение — по меш-зазору (компоненты связности), спрятанные детали — чётностью луча, двойные вершины до сварки, неманифолд, вывернутые нормали (объём со знаком), неплоские n-гоны, видимые сырые рёбра, материалы и процедуры, свет, кадр по проекции вершин, бюджет. Коды M…, вердикт fail/review/pass; одна строка `SCENE_CHECK {json}`. Калибровка — `99-raw/experiments/J/01-calibration` | `python3 qa_pipeline.py scene a.blend [b.blend …] --passport p.json` (или `--passports map.json`; ≈ 2 с на 32 сцены) |
| `qa_pipeline.py` (агент J) | Сводный конвейер с вердиктом и JSON. `scene`: scene_check + `preflight()` E. `glb`: валидатор → `glb_lint()` E → `gltf_web_inspect` → [`gltf_diff` по копии `.blend` только с `ASSET_*`] → [`gltf_load_bench`], бюджет `--max-tris/--max-kb`. `page`: `site_probe` → `gate_check()` F1 + проверка import map (одна версия three; min-ядро только с переназначением). Код выхода 0 pass / 1 review / 2 fail / 3 сбой; временные папки удаляет (`--keep`) | `python3 qa_pipeline.py glb m.glb --blend s.blend --diff --out r.json`; `… page 09-web-runtime/examples/hero-lazy [--reduced] [--mobile]` |
| `run_doc_blocks.py` (агент J) | Исполняемая документация: блоки ```python (фоновый Blender, перед каждым — заводская сцена; `# run: system` — системный python3) и ```bash (из корня базы, с `OUT_DIR`) итоговых .md в напечатанном виде; JS пропускается (раннеры F2/09, H/30); `[не проверено]` или `# run: skip` в первых строках блока — пропуск | `python3 run_doc_blocks.py 11-evaluation-qa/0*.md --json r.json` → `RESULT 9/9` |
| `three_probe.py` (агент H, перенесён J из `experiments/H/_lib/`) | Грузит GLB в three r186 (Chromium, GPU) и выполняет JS-проверку (тело async-функции с `THREE, gltf, scene, renderer, camera, render`) → JSON; ворота анимации: клипы, длительности, позы, четверти турнтейбла. Аргументы позиционные (`--help` нет) | `python3 three_probe.py m.glb check.js --out r.json` |
| `anim_diff.py` (агент H, перенесён J) | Анимация в Blender против three r186 в одни и те же моменты: кадры EEVEE и three, IoU / ΔE2000 / SSIM по кадрам (функции `gltf_diff.py`), лист сравнения | `python3 anim_diff.py s.blend out/ --glb m.glb --frames 1,31,61 [--clip Reveal] [--mute-nla]` |

Регрессионный набор — `../../kb/blender/11-evaluation-qa/regression/` (`manifest.json` 33 записи, `run_set.py`: `--tiers core,negative,k`,
`--compare baseline`; полный прогон ≈ 57 с). **Предупреждение к `gltf_diff.py`** (J/03): источник `.blend` рендерится как есть —
если в нём студия (циклорама, пол), сравнение ложно «сломано» (IoU 0,002, ΔE 9,96); сравнивать по копии «только ассет»
(`qa_pipeline.py glb --diff` делает её сам). Кандидаты агента I перенесены в волне 4 (агент U, раздел ниже): `agent_scene.py` и `hygiene.py` → `../../kb/blender/03-bpy-api/snippets/` (тест `test_agent_helpers.py`, 4/4), `lint_agent_code()` → `lint_agent_code.py`.

## Рецепты (агент K, волна 3; добавлено оркестратором сессии 3)

| Утилита | Что делает | Пример |
|---|---|---|
| `rk.py` (агент K) | Обёртка для рецептов над `bpyx`, `d1lib`, `d2lib`, пресетами E и аудитом/утверждениями C1: паспорт → `build(P)` → проверки → рендер → экспорт; `rk.reset()` — только для фонового файла или своей сцены (в сцене человека — уборка по тегу, `02-blender-workflow/01 §2`) | см. `../../kb/blender/12-recipes/00-how-to-use.md` и `examples/<рецепт>/build.py` |
| `run_recipes.py` (агент K) | Прогон рецептов: блоки python/bash из .md, валидатор и загрузка в three для каждого GLB, страницы в Chromium; ≈ 3 мин на 12 рецептов | `python3 run_recipes.py 12-recipes/0[1-9]-*.md 12-recipes/1[0-2]-*.md` |

## Эксплуатация (агент O, волна 3; добавлено оркестратором сессии 3)

| Утилита | Что делает | Пример |
|---|---|---|
| `blender_supervisor.py` (агент O) | Фоновый Blender 5.2 под надзором: `start` / `exec` / `status` / `stop` / `replay` через Unix-сокет; шаг = транзакция (успех → контрольная точка `.blend`, ошибка → откат); перезапуск и восстановление после `sys.exit`, бесконечного цикла, segfault, OOM; журнал JSONL; лимиты `--mem` / `--cpu` (`systemd-run`, с `MemorySwapMax=0`) и изоляция `--sandbox` (`bwrap`: запись только в WORK, без сети, без домашней папки). Код выхода `exec`: 0 успех, 1 исключение в коде, 2 процесс убит или упал. Процедура — `../../kb/blender/04-ai-agents-mcp/06-headless-operations.md`, угрозы — `07-security.md` | `python3 blender_supervisor.py start WORK --sandbox --mem 4G`; `… exec WORK build.py --timeout 120 -- 0.5`; `… stop WORK` |

## Атлас инструментов (агент L, волна 3; добавлено оркестратором сессии 3)

| Утилита | Что делает | Пример |
|---|---|---|
| `atlas_collect.py` (агент L) | Собирает `../../kb/blender/13-tools-atlas/atlas.tsv` (156 записей, 16 колонок: версия, дата релиза, последний коммит, звёзды, лицензия и её ограничения, цена, работа без окна, ключ, статус живости, где в базе) из реестров A (`A/02-runtime-registry/registry.json`), C2 (`C2/00-repo-liveness/repos.json`), F2 (`F2/01-npm-registry/`) и живых источников (npm, PyPI, ungh.cc → GitHub API, Forgejo projects.blender.org, extensions.blender.org) с кэшем `99-raw/experiments/L/00-atlas-collect/cache.json`; вручную в скрипте — только лицензии, ограничения и «ценность для агента». Добавить инструмент — одна запись `E(...)` в `ENTRIES`. GitHub API без токена — 60 запросов в час на машину | `python3 99-raw/tools/atlas_collect.py [--refresh] [--offline] [--only npm,pypi,gh,forgejo,ext]` (без `--refresh` — секунды, из кэша) |

## Аудит (агент X, волна 4; добавлено оркестратором сессии 3)

| Утилита | Что делает | Пример |
|---|---|---|
| `check_links.py` (агент X, адаптация `../maint/check_links.py`) | Перекрёстные ссылки базы: пути (включая `99-raw/experiments/<агент>/NN` и диапазоны), `§N.M`, `[S<n>]`, `[V:<id>]` (дайджест или только транскрипт), полнота README, обязательные разделы. Эвристики дают ложные ERROR на сокращениях вида «A `01 §22`» — результат смотреть глазами (на 23.09: 132 ERROR, настоящих 22) | `python3 ../maint/check_links.py [--only 02,11] [--json out.json]` (≈ 7 с) |

## Перенесено и исправлено в волне 4 (агент U, по рекомендациям аудита X §12)

Новые утилиты (перенос помощников агентов в общие места; помощники, доказанные экспериментами, — код не менялся,
только путь и, где сказано, обёртка CLI/модуля):

| Утилита | Что делает | Пример |
|---|---|---|
| `agent_scene.py`, `hygiene.py` (агент I) | Из `99-raw/experiments/I/01-own-collection-vs-wipe/` и `I/02-file-hygiene/`, рядом с `bpyx` (импортов, зависящих от пути, не было — переносить было нечего чинить). `agent_scene`: `begin()`/`finish()` — идемпотентная сборка в сцене человека по тегу (custom properties), не по имени; чужое не трогает, эвакуирует чужое из своей коллекции вместо удаления. `hygiene`: `hygiene_report()` (только отчёт, годится и в сцене человека) / `hygiene_clean()` (чистка — только в своём фоновом файле). Тест — `test_agent_helpers.py` (4/4) | `../../kb/blender/03-bpy-api/snippets/README.md` (раздел «Помощники агента») |
| `lint_agent_code.py` (агент I, код `../../kb/blender/02-blender-workflow/03-patterns-antipatterns.md` §6) | CLI-обёртка: самопроверка текста скрипта агента регулярными выражениями (14 правил `M…`-подобных кодов ERROR/WARN) до отправки в Blender; файлы или stdin → JSON, код выхода 0 чисто / 1 есть замечания. 24/24 скрипта C1/11 — те же срабатывания, что у `99-raw/experiments/I/04-doc-blocks/` | `python3 lint_agent_code.py script.py [script2.py …]`; `cat script.py \| python3 lint_agent_code.py -` |
| `gate_check.py` (агент F1, код `../../kb/blender/09-web-runtime/05-performance-a11y-fallbacks.md` §7.2; была ещё копия K `K/02-hero-page/gates.py`, теперь один модуль) | Ворота качества страницы по отчёту `site_probe.py`: LCP/CLS/TBT/вес/3D-КБ/вызовы/DPR (+ `reduce`). Правки U: «3D-ассеты, КБ» считает и категорию `site_probe.py` `"bin"` (не только `model3d`+`texture3d` — иначе отдельно отданные `.bin`-буферы glTF вне бюджета, находка K/04: 412 КБ мимо счёта); порог TBT десктопа условный по решению аудита **R20** — без текстур `"texture3d"` (KTX2 и т. п.) 150 мс, при их наличии 200 мс (эталон hero-lazy 172–175 мс: теперь `pass`, раньше `fail` при 150); телефон — 300 мс при CPU×4, без изменений. `qa_pipeline.py page` импортирует этот модуль вместо своей копии | `from gate_check import gate_check`; `python3 gate_check.py probe.json desktop [--reduced]` |
| `fx_probe.py` (агент F2) | Из `99-raw/experiments/F2/00-tools/` без изменений кода (путей, зависящих от места файла, не было) — замер демо-страницы с 3D/шейдерным эффектом: desktop/mobile/reduce/uncapped, покой и прокрутка отдельно, сеть по категориям, `window.__bench` | `python3 fx_probe.py ROOT_DIR page.html OUT_DIR [--modes desktop,mobile,reduce,uncapped]` |

Правки существующих утилит (код не переписывался сверх находки, каждая — с повторным прогоном, числа — в
`99-raw/experiments/U/*/README.md`):

| Утилита | Что изменилось | Проверка (до → после) |
|---|---|---|
| `gltf_diff.py` (агент E) | В EEVEE-ветке добавлен `world.sun_threshold = 0.0` (было только `world.use_sun_shadow = False`, который не отключает само извлечение «солнца» из ярких пятен HDRI — RNA 5.2.2 подтвердил разницу описаний). Иначе EEVEE выносит превышение `sun_threshold` (умолчание 10) в отдельный направленный свет, которого нет у чистого IBL в three (D2) | На калибровочной сцене E/02: ΔE2000 среднее 3,123 → 2,697; на ракурсе 200°/35° (верх куба) 5,09 → **3,19** (зашёл в порог ≤ 3,5); IoU не изменился (0,996) |
| `blender_supervisor.py` (агент O) | `start` считает длину `WORK/sup/blender.sock` в байтах и сразу падает понятной ошибкой при > 107 (`sizeof(sockaddr_un.sun_path)` Linux − 1 байт на `'\0'`), вместо `call()`, ждущего `START_MAX` = 90 с и падающего «нет сокета» (X/01) | Длинный путь: 90 с ожидания → **0,024 с** мгновенная ошибка; короткий путь: `start`/`exec`/`stop` — как в O/01, без изменений |
| `qa_pipeline.py` (агент J) | `glb`: новая проверка `NAME_COLLISION` — коллизии имён узлов `.glb` после санитизации three (`02-blender-workflow/01` §8.2 `three_name()`, парсится JSON-чанк `.glb` напрямую, без Blender/three) → `ERROR`, критично для интерактива. `page`: `gate_check()` теперь из общего модуля (см. выше), не своя копия; `run_page()` раздаёт демо-страницу из временной копии папки — раньше `serve_br.precompress()` писал `file.br` прямо в `09-web-runtime/examples/…` в базе (замечание оркестратора после отчёта S1 §6) | GLB `I/03-names-blender-to-js/out/raw.glb` → `fail`, поймал `hotspot_buy` (+ `Mug001`/`Mug.001`); GLB `../../kb/blender/12-recipes/examples/01-hero-product/case.glb` → `pass`, чисто. `page 09-web-runtime/examples/hero-lazy`: по сохранённым пробам F1/J (172–175 мс) вердикт TBT `fail`→`pass` при новом пороге 200; живой повтор после фикса копии — `pass` 9/9 (195 мс), список `.br` в базе не изменился |
| `presets.py` (агент E, `../../kb/blender/99-raw/experiments/E/24-presets/`) | Новый пресет `"addressable_nodes"` (П-57: база — параметры `static_hero`; постобработка `gltfpack -cc -kn -ke`) — для меток `hotspot_*`/`cam_*`/extras и кликов по частям, в отличие от `static_hero`/`mobile_light`, которые их теряют | На `I/03` `names.blend`: имена и extras пустышек (`hotspot_buy`, `cam_start`, `hero_body` и др.) целы после экспорта и постобработки, валидатор Khronos 0/0 |
| `serve_br.py` (агент F1, `../../kb/blender/99-raw/experiments/F1/02-hero-variants/`) | `start()`: `httpd.shutdown` оборачивается так, что следом всегда идёт `server_close()` (J §3 п. 11) — работает и для вызывающих, которые зовут только `.shutdown()`, без их правки. Одного `server_close()` эмпирически недостаточно для немедленного повторного `bind()` на тот же порт (соединение в `TIME_WAIT`) — добавлен `allow_reuse_address = True` | Тот же порт дважды подряд (`start`→запрос→`shutdown`→`start`): было `Address already in use`, стало `OK`; двойной `close()` (как в `qa_pipeline.py`) — безопасен |

Не исправлено, только пометка (K, `99-raw/experiments/K/09-mv-page/README.md`, `99-raw/reports/wave3-K-report.md` §4): **`web_view.py
--page` не видит вызовы отрисовки model-viewer** — на живой странице с `<model-viewer>` (событие `load` есть,
`canActivateAR`, вес и ошибки консоли — нормально) зонд показывает **0 вызовов отрисовки**, хотя рендер идёт.
Перехват `web_view.py` патчит `WebGLRenderingContext`/`WebGL2RenderingContext.prototype` до навигации — этого обычно
достаточно и для канваса в Shadow DOM (патч прототипа общий на документ, Shadow DOM не создаёт новую область
видимости JS), поэтому патч по прототипу тут не объясняет находку без дополнительной проверки; вероятная причина
(`[не проверено]`) — `<model-viewer>` может рендерить через `OffscreenCanvas`, переданный в отдельный поток
(Worker/`transferControlToOffscreen`), где патч, поставленный в основном потоке, не действует. Разбор — не в объёме
этой волны; для model-viewer считать вызовы отрисовки глазами по FPS или искать в `@google/model-viewer` факт
использования `OffscreenCanvas`.

## Синтез (агент S2, волна 4; добавлено оркестратором сессии 3)

| Скрипт | Что делает | Пример |
|---|---|---|
| `99-raw/notes/wave4/S2/make_map.py` | Пересобирает «Карту файлов» корневого `README.md` (строки и описания файлов папок 01–13) после правок базы | `python3 99-raw/notes/wave4/S2/make_map.py --apply` |
| `99-raw/notes/wave4/S2/make_glossary.py` | Проверяет и пересобирает `../../kb/blender/00-glossary/README.md` из данных `gloss_*.txt` (колонка «Где» — существование файла и раздела) | `python3 99-raw/notes/wave4/S2/make_glossary.py --check` / `--apply` |

## Среда агента-дизайнера вне базы (настроено оркестратором 23.09.2026 по решению владельца)

| Что | Где | Проверка |
|---|---|---|
| MCP `blender-lab` — официальный Blender Lab MCP v1.0.3 + фоновый Blender 5.2.2 в одной песочнице `bwrap` (своя сеть, запись только в `~/blender-agent-work`, `-Y`, `--factory-startup`) | `~/.local/share/blender-agent/` (`run_blender_lab_mcp.sh`, `inside.sh`, `start_bridge.py`, `addon/`, `mcp-venv/`, `README.md`) | `~/.local/share/blender-agent/mcp-venv/bin/python ~/.local/share/blender-agent/selftest.py` → `SELFTEST PASS` (куб, EEVEE 256², `~/.ssh`/проекты/сеть недоступны); `claude mcp list` → Connected |
| MCP `blender` — mcp-for-blender закреплён `==2.0.3`, `DISABLE_TELEMETRY=true`; автозапуск на 9876 выключен (умолчание в аддоне) | `~/.claude.json`, `~/.config/blender/5.2/scripts/addons/blender_mcp.py` (копия до правки — `.bak-autostart-20260923`) | `claude mcp list`; в Blender с окном галочка Auto-Start Server снята |

## Эксперименты

Каждый эксперимент — папка `99-raw/experiments/<агент>/<NN-короткое-имя>/`: скрипт(ы), `README.md` (цель, команда,
результат, вывод, версия Blender/three), маленькие результаты (PNG ≤ 1024 px, GLB). Большие промежуточные файлы
удалять. Ссылка из файлов базы: `[проверено: 99-raw/experiments/B/03-geonodes-api]`.

## Оркестратор (сессия 2)

| Утилита | Что делает | Пример |
|---|---|---|
| `extract_sections.py` | Компактные извлечения из Markdown: для каждого файла — заголовок, строка метаданных и разделы `## …` по регулярному выражению (по умолчанию «Выжимка для агента», «Открытые вопросы и противоречия», «Чек-лист») с номерами строк; для аудитора и синтезатора волны 4 (не читать 70 файлов целиком) | `python3 99-raw/tools/extract_sections.py 05-modeling -o 99-raw/notes/wave4/extracts/05-modeling.md`; отчёты: `… 99-raw/reports --glob 'wave*-report.md' --sections 'противореч\|пробел\|термин' -o …` |
| `sources_collect.py` (агент S1 волны 4, адаптация ux-research) | Сводная библиография: разделы «Источники» содержательных файлов 01–13 и ролики дайджестов `91-videos/digests/` → `90-sources/sources.tsv` (дедупликация по нормализованному URL; записи без URL — по названию; внутренние ссылки на эксперименты и файлы агентов исключаются; тип и надёжность — эвристика) и `90-sources/README.md` (по типам и папкам, топ-20, единичные ненадёжные, не открывшиеся по отчётам и заметкам). ≈ 1 с | `python3 99-raw/tools/sources_collect.py [--dry] [--debug out.tsv]` |
