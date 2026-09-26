# Спецификация переноса — часть «Код» (агент B, 26.09.2026)

Вход: `../SKILL-MAP.md` (источник правды раскладки), `../../DECISIONS.md` (Р-номер = строка; свежие — Р99–Р111), `SPEC.md` агента A
(§9 «Передача агенту B», §10 п. 16), `scan-handoff.tsv` (266 файлов), `manifest-rules.yaml`, `expected-content.tsv`, SYNTHESIS §4 и §6.9,
свежий инвентарь `../../freeze/inventory/`, выжимки Ф2 (разделы «Код и утилиты»), сам код — сканом AST и глазами.
Выход — файлы этой папки:

| файл | что это |
|---|---|
| `tools-map.tsv` | 299 строк: каждый исполняемый файл-кандидат (266 передачи A + 7 из `_skill-build/tools/` + 8 данных кода из опытов + 18 файлов эталонного кода kb с правкой) — решение, место, зависимости, правки, смоук |
| `patches/` | 103 файла механических правок `patches/<место от корня скилла>.yaml` (252 правки, 298 замен) |
| `apply_patches.py` | применяет правки к нетронутой копии источника; `--check`, `--record`, `--apply-to`, `--diff`; модуль для `migrate.py` |
| `overlay/.claude/skills/design-deep-dive/scripts/` | `lib/kbpaths.py`, `requirements.txt`, `package.json`, `install.sh`, `tests/smoke.py` + `tests/smoke-list.tsv`, `README.md` |
| `code-xfail.tsv` | известные падения смоука без окружения (причина) — вшиты в `smoke-list.tsv` |
| `code-smoke.tsv` | итог смоука по взятым файлам в трёх раскладках (§7) |
| `code_stage.py` | генерация `smoke-list.tsv` и `README.md` overlay из `tools-map.tsv`; сборка временных раскладок; смоук в песочнице — образец для `migrate.py` |

Временные папки (в журнал не идут, правило `j-staging`): `.staging-code/`, `.staging-code-faithful/`, `.staging-code-results/`.
Воспроизвести: `python3 apply_patches.py --check` (≈ 1 с) → `python3 code_stage.py --gen --build` и `--build --faithful` → `--smoke`,
`--smoke --faithful`, `--smoke --faithful --source-cache --only ai-media --tag srccache` (≈ 3 мин каждый) → `--report`.

## 1. Итог в цифрах

| база | кандидатов | взято | утилит и шагов | модулей | тестов | данных | эталонного кода kb | дублей | не взято |
|---|---|---|---|---|---|---|---|---|---|
| ux | 10 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | 7 |
| ui | 10 | 4 | 3 | 1 | 0 | 0 | 0 | 1 | 5 |
| site | 31 | 14 | 13 | 0 | 0 | 1 | 0 | 12 | 5 |
| text | 28 | 14 | 13 | 0 | 0 | 1 | 0 | 9 | 5 |
| creative | 32 | 11 | 9 | 1 | 0 | 1 | 0 | 14 | 7 |
| ai-media | 65 | 52 | 23 | 7 | 3 | 19 | 0 | 5 | 8 |
| blender | 95 | 64 | 28 | 14 | 2 | 2 | 18 | 4 | 27 |
| claude-design | 21 | 14 | 14 | 0 | 0 | 0 | 0 | 5 | 2 |
| `_skill-build/tools` | 7 | 4 | 3 | 0 | 0 | 1 | 0 | 0 | 3 |
| **итого** | **299** | **178** | **107** | **23** | **5** | **25** | **18** | **52** | **69** |

«Утилит и шагов» — kind utility, step, maint, kit. Взято 178 = 75 без правок (`take`) + 103 с правками (`adapt`). Дублей 52: 43 побайтных
(md5) и 9 версий-дублей — старые копии утилит, у которых канон другой версии по SYNTHESIS §4.1 (`page_accept` site и creative → ai-media,
надмножество; пять `check_links` → общий в `scripts/maint/`; два `orch_check` → канон site). 22 дубля — псевдонимы взятого канона: не
копируются, ссылки на них ведут к канону (SKILL-MAP §2.2). Не взято 69: сбор источников и роликов 32, обслуживание ресерча 15, замер
жанра 5, 3D-генераторы (Р72) 3, npm-файлы (сведены в `scripts/package.json`) 3, старые версии 3, остальное — по одному с решением
(Р39, Р80, Р33, §4.2, решения B §9).

Объём взятого: 4,83 МБ, ≈ 2,17 млн токенов (оценка `count_tokens`), из них `scripts/` — 4,75 МБ, ≈ 2,13 млн; overlay `scripts/` — 7 файлов,
0,10 МБ, ≈ 42 тыс. Оценка A «код B ≈ 3–5 МБ, 1,5–2 млн токенов» — сходится (токенов чуть больше); общий объём шаблона — в пределах Р111.

Проверки: смоук на раскладке «как после переноса» — 206 PASS, 0 FAIL, 10 XFAIL (§7); `/home/mm` в `scripts/` — 0 (и в 18 файлах
эталонного кода kb с правкой — 0); файлов-инструкций в `scripts/` — 0; правки детерминированны (два прогона `--apply-to` дают одно
дерево, отпечаток sha256 списка файлов — `b3890a85f2d34221`; `apply_patches.py --check`: 103 файла, 0 ошибок, `result_sha256` сверены);
`freeze.py --verify` после всех прогонов — 0 добавлено, 0 удалено, 0 изменено.

## 2. `tools-map.tsv`

Колонки по брифу: `source` (от корня app-design), `md5`, `canonical` (`yes` | `dup-of:<source>`), `verdict` (`take` — копия без правок,
`adapt` — есть файл правки, `skip`), `why` (Р-номер, раздел SYNTHESIS или SKILL-MAP), `dest` (от корня шаблона), `kind`, `deps_py` (имена
pip), `deps_node` (npm с версией), `deps_bin` (бинарники и где их ищут), `patches` (коды правок, §3), `smoke` (§7), `notes`.

- `kind`: `utility` — утилита с CLI; `step` — шаг конвейера из опытов (Р33, Р37, Р54, Р66); `module` — модуль, который импортируют;
  `kit` — kit Claude Design; `maint` — обслуживание базы; `test` — тесты; `data` — данные и README, которые читает код или человек рядом
  с кодом; **`ref`** (сверх брифа) — эталонный код kb с механической правкой: место — как у правила содержимого (`d-kb`), правка — только
  пути к модулям, уехавшим в `scripts/blender/`.
- Канон: в группе побайтно одинаковых файлов `yes` — взятая копия (если есть) или первая по порядку баз; остальные `dup-of:<канон>`.
  Версии-дубли (9, в `notes` — «версия-дубль») — тоже `dup-of:<канон>`, но sha256 у них другой: канон — надмножество или общий
  проверщик. Если канон взят, у дубля `dest` = место канона (псевдоним), иначе `dest` пуст.
- Одна копия на утилиту (SKILL-MAP §2.2): `scripts/<база>/` — по базе-канону; модули общего пользования — `scripts/lib/` (только `color.py`,
  его импортируют ui, creative, ai-media); `kit` — `scripts/claude-design/kit/`; обслуживание — `scripts/maint/`.
- Переименования (место — решение раскладки, CLI не менялся): text B1 `validate.py` → `scripts/text/validate_meaning.py` (схемы meaning и
  message-hierarchy), B2 `validate.py` → `scripts/text/validate_facts.py` (facts, voc) — иначе два `validate.py` в одной папке;
  `validate_any.py` импортирует `validate_meaning`. Модули и шаги опытов ai-media и библиотеки blender положены плоско рядом с
  утилитами домена (импорты «рядом» работают без правок путей); подпапки — только `scripts/blender/{vote,regression,node}/`,
  `scripts/ai-media/tests/`, `scripts/claude-design/kit/`.

## 3. Механические правки

**Формат** (`apply_patches.py`, докстринг): `patches/<dest от корня скилла>.yaml` — `source`, `source_sha256` (правка применяется только к
этому содержимому), `dest`, `result_sha256` (пишет `--record`), `edits` — список `{code, find, replace, count, note}`; `find`/`replace` —
строка или список строк (склеиваются `\n`). Правки применяются по порядку, каждая к результату предыдущих: `find` обязан встретиться ровно
`count` раз (по умолчанию 1), иначе `PatchError`; замена — все непересекающиеся вхождения. Другой sha256 источника или результата —
ошибка. Выбран формат «замены с ожидаемым счётчиком», а не unified diff: он точен без контекста строк, читается глазами и проверяется
счётчиком.

**Коды** (колонка `patches`): файлов с кодом / правок.

| код | что | файлов / правок |
|---|---|---|
| `boot` | подключение `scripts/lib` и `import kbpaths` (строкой после `HERE = …` или импорта) | 42 / 42 |
| `root` | корень базы или утилиты от `__file__` → `kbpaths.kb('<база>')` / `kbpaths.scripts(...)` | 50 / 51 |
| `kb` | пути в соседние базы `<APP>/<база>-research/…` → `kbpaths.kb('<база>')`; строки путей, которые генератор пишет в выход, — в форме после переноса | 5 / 15 |
| `imp` | импорты соседей и модулей опытов (`sys.path` на старые папки, `_exec_tool`, вызов `page_accept.py` ai-media) | 33 / 36 |
| `abs` | прочие абсолютные `/home/mm/…` (в том числе в справке и README) | 13 / 13 |
| `lock` | блокировки → `kbpaths.lock_path()` (таблица в §4) | 10 / 18 |
| `out` | выходы `99-raw/cache/…`, `99-raw/experiments/_…`, `HERE/out` → `kbpaths.out()` | 17 / 23 |
| `cache` | кэши (снимки каталогов, net_cache, refs, C2PA) → `kbpaths.cache()` | 7 / 7 |
| `venv` | `venv-*` в `99-raw/tools` → `kbpaths.python()` | 4 / 4 |
| `bin` | Blender, Brave, node, `99-raw/tools/bin/…` → `kbpaths.which()`/`bin_dir()` (в bash — `${DDD_HOME:-…}/bin`) | 17 / 22 |
| `node` | `99-raw/tools/node/node_modules`, npm-песочницы `~/.cache/blender-research/npm-*` → `$DDD_HOME/node` | 8 / 8 |
| `data` | данные, уехавшие в `scripts/<база>/data/`, `tests/fixtures/`, `kb/<база>/99-raw/…` | 9 / 12 |
| `model` | модели ONNX → `kbpaths.models()` | 1 / 1 |
| `key` | ключи — только из окружения | 0 / 0: ключи уже читаются из переменных или файлов `~/.config/…` вне репозитория (Р53), правок не понадобилось |

Не трогал: логику, CLI, форматы вывода, Kimi-ветки, судью, схемы; строки справки вида `python3 99-raw/tools/<утилита>.py …` (устарели, но
без `/home/mm`); пути входов опытов, которые не переносятся (они и так не найдутся — §8). Единственные строки «данных» в коде, которые
поменялись, — пути, которые генератор пишет в выходной файл, переписываемый переносом (`build_profile.py`, `ux_dict_to_yaml.py`): иначе их
`--check` после переноса всегда видит расхождение. Итог правки смотреть: `python3 apply_patches.py --diff scripts/<домен>/<файл>`.

## 4. `scripts/lib/kbpaths.py` — API

Только stdlib, без абсолютных путей; корень скилла — `Path(__file__).resolve().parents[2]`. Подключение в утилите (строка `boot`):
`sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib")); import kbpaths` (в подпапках — `"..", ".."`;
в эталонном коде kb путь к `scripts/blender` считается от файла: пять уровней вверх до корня скилла). Работает и внутри Blender (проверено).

| функция | что возвращает |
|---|---|
| `skill(*p)`, `repo(*p)`, `assets(*p)` | корень скилла, корень шаблона (skill → skills → .claude → корень), `assets/` |
| `kb(база=None, *p)` | `kb/<база>/…`; принимает и «site-research»; неизвестная база — `ValueError` |
| `scripts(домен=None, *p)`, `data(домен, *p)` | `scripts/<домен>/…`, `scripts/<домен>/data/…` (домены — 8 баз + lib, maint, tests) |
| `use(домен)` | добавить `scripts/<домен>/` в `sys.path` — модули соседнего домена (`kbpaths.use("ui"); import ui_audit`) |
| `home(*p)` | `$DDD_HOME` → `$XDG_CACHE_HOME/design-deep-dive` → `~/.cache/design-deep-dive` |
| `venv(*p)`, `python()` | venv окружения; его Python (нет venv — текущий интерпретатор) |
| `node_home()`, `node_modules(*p)`, `node_env(env)` | `$DDD_HOME/node` (package.json скилла), его `node_modules`; окружение с PATH и NODE_PATH |
| `bin_dir(*p)`, `models(*p)`, `browsers()` | `$DDD_HOME/bin`, `…/models`, `…/browsers` |
| `out(домен, *p)`, `cache(домен, *p)` | каталоги выходов и кэшей `$DDD_HOME/{out,cache}/<домен>/…` (создаются) |
| `locks_dir()`, `lock_path(имя="browser", домен=None)`, `lock(имя, домен, timeout=900)` | каталог блокировок; путь файла; контекст flock с ожиданием (TimeoutError по истечении) |
| `which(имя, env=None, names=())`, `blender()`, `node()`, `npx()`, `ffmpeg()`, `ffprobe()`, `brave()` | переменная `DDD_<ИМЯ>` → `$DDD_HOME/bin/<имя>` или `bin/<имя>/<имя>` → `node_modules/.bin` → PATH; не нашли — имя как есть (импорт и `--help` работают без бинарника) |
| `key(имя, required=False)` | ключ API только из переменной окружения |
| `playwright_env(env)` | PLAYWRIGHT_BROWSERS_PATH на `$DDD_HOME/browsers`, если браузеры стоят там (при импорте модуль ставит это по умолчанию, если переменной нет и каталог есть) |

Диагностика: `python3 scripts/lib/kbpaths.py` — таблица «что где», `--selftest` — 15 проверок без сети.
Переменные: `DDD_HOME`, `DDD_BLENDER`, `DDD_NODE`, `DDD_NPX`, `DDD_NPM`, `DDD_FFMPEG`, `DDD_FFPROBE`, `DDD_BRAVE`, `DDD_CHROMIUM`,
`PLAYWRIGHT_BROWSERS_PATH`; ключи — как у утилит (`POLZA_API_KEY`, `ROUTERAI_API_KEY`, `GENAPI_API_KEY`, `PSI_API_KEY`, файлы `~/.config/…`).

**Окружение** `$DDD_HOME/{venv, node, bin, models, browsers, out, cache, locks}` — как SKILL-MAP §1 плюс `cache/` (снимки каталогов,
ответы API, net_cache отдельно от выходов; §11 п. 5).

**Блокировки**: имя файла сохранено, поэтому проверка «замок держит предок» (`page_accept`, `asset_audit`) работает как в источнике.

| источник | теперь |
|---|---|
| `app-design/.locks/browser.lock` (общий: тройка, `slot_run`) | `$DDD_HOME/locks/browser.lock` |
| `app-design/.locks/browser-refs.lock` | `$DDD_HOME/locks/browser-refs.lock` |
| `app-design/.locks/{blender-slot-1,2,render}.lock`, `slot_run.log` | `$DDD_HOME/locks/…` (`SLOT_RUN_LOCKS` по-прежнему переопределяет) |
| `<база>/99-raw/tools/.locks/{browser,heavy,blender}.lock` | `$DDD_HOME/locks/<база>/{browser,heavy,blender}.lock` |
| kit: `--lock` / `KIT_BROWSER_LOCK` (необязательная) | без изменений; общий замок — `--lock $DDD_HOME/locks/browser.lock` |

## 5. Раскладка `scripts/` (итог)

```
scripts/  README.md requirements.txt package.json install.sh
  lib/            kbpaths.py color.py
  ux/             checklist_export.py
  ui/             ui_audit.py measure_ui.py build_reference_tokens.py
  site/           README.md site_validate page_gates ab_plan vocab_lint checklist_export plan_to_assets page_anatomy geo_probe ia_probe
                  run_axe_targets build_profile
  text/           README.md copydeck claims_check copy_lint ux_dict_to_yaml copy_extract run_checks
                  validate_meaning validate_facts validate_voice validate_any check_intake chain_inputs make_skeleton
  creative/       README.md marketing_audit motion_check scroll_record refs_client spec_check ad_check validate_stack registry_check
                  recipe_check idle_probe
  ai-media/       README.md polza polza_catalog mp_client routing_check prompt_compile vlm_to_dna asset_audit edit_check alpha_check
                  tile_check video_loop_check avif_pick.sh provenance_check page_accept stand_run asset_inventory
                  image_metrics text_zone composition_metrics palette series_metrics split_grid check_icons split_recraft
                  layout_check channel_diff validate_recipes loop_rife_bridge svg_sheet vm_sheet
                  tests/{test_asset_audit, test_prompt_compile, test_prompt_compile_x2}.py, tests/fixtures/{*.png,*.spec.json,D02/,D03/}
                  data/ (lucide-ref/, genapi_prices_2026-09-23.json — правила A; svgo.keep-signature.config.mjs — tools-map)
  blender/        README.md blender_run bpy_probe lint_agent_code blender_supervisor render_views scene_check gate_check qa_pipeline
                  gltf_check gltf_web_inspect gltf_diff gltf_load_bench three_probe anim_diff web_view fx_probe site_probe run_doc_blocks
                  slot_run img_metrics sheet run_recipes rk bpyx agent_scene hygiene test_bpyx test_agent_helpers d1lib d1exp d2lib
                  presets scene_audit passport_asserts preflight_block glb_lint_block serve_br animx
                  node/validate.mjs  regression/{run_set,make_manifest}.py  vote/{build_pairs,tally,vote_server}.py + index.html
                  data/studio_small_09_1k.hdr (правило A)
  claude-design/  mockup_checks stand_page shot_v3 lang_check  kit/{shot,diffshots,export}.py canvas.html marks.js example/
  maint/          check_links (версия site) orch_check (канон site) count_tokens calibration.json calibrate layers
  tests/          smoke.py smoke-list.tsv
```

## 6. Зависимости и установка

- `requirements.txt` — версии общего venv (`venv-freeze.txt`) и окружений базы, на которых утилиты проверялись; секции-группы:
  `core` (схемы, YAML, numpy/scipy/Pillow, Playwright 1.63, pypdf, brotli — уже стоят в venv), `net` (requests для `geo_probe`), `morph`
  (pymorphy3 — по желанию: меняет плотность маркеров, пороги сняты без неё), `svg` (cairosvg, svgelements, scikit-image, vtracer),
  `ocr` (RapidOCR 3.9.2 + onnxruntime 1.30), `media` (rembg — удаление фона, Р71).
- `package.json` — npm с точными версиями из lock-файлов базы и песочниц `npm-trial`/`npm-F2` (SYNTHESIS §4.3 + то, что читают утилиты и
  эталонный код): gltf-transform 4.5.0, gltf-validator, gltfpack, meshoptimizer, draco3dgltf, svgo 4.1.0, resvg-js, lucide-static 1.47.0,
  Lottie, web-vitals 6.2.2, axe-core 4.13.0, esbuild 0.28.2, three 0.186.0, postprocessing 6.39.5, n8ao 2.0.1, React 19.3 + R3F 9.8 +
  drei 10.7.8 и пакеты песочницы испытания; поле `x-ddd-used-by` — кто что использует.
- `install.sh` — идемпотентный: каталоги окружения; venv + pip по группам (`--groups core,net,…|all`); npm в `$DDD_HOME/node` (сверка по
  sha256 `package.json`) и копия `blender/node/validate.mjs` туда же (ESM ищет `gltf-validator` рядом с файлом по realpath, симлинк не
  годится); `--bin` — 11 пакетов бинарников, 15 файлов со sha256 (c2patool 0.27.22, exiftool 13.59, libavif 1.4.2, libjxl 0.12.0, libwebp 1.6.0, rife-ncnn-vulkan
  20221029, realesrgan-ncnn-vulkan 20220424, vtracer 1.0.0-alpha.4, potrace 1.16, gltfpack 1.2, KTX-Software 4.4.2) и `--models` —
  7 моделей ONNX (u2netp, isnet-general-use, Depth Anything V2 Small, PP-OCRv5 ×4) с sha256 установленного файла; источник — `--from DIR`
  / `--models-from DIR` (та же раскладка, что старые `99-raw/tools/{bin,models}`) или адрес релиза (§11 п. 7); `--browsers`
  (Playwright chromium в `$DDD_HOME/browsers`), `--catalogs` (снимки polza, RouterAI, Gen-API и список доверия C2PA — бесплатные GET),
  `--check`, `--dry-run`. Системное (Blender 5.2.2, ffmpeg, Node 24, Brave, bwrap, systemd-run, flock, libcairo2) только проверяет.
  Проверено `--dry-run` в песочнице: все 15 + 7 sha256 совпали с файлами старых `bin/` и `models/` ai-media и blender.
- **В venv ничего не ставил.** Смоуку хватило окружения; недостающее — не чистый Python (cffi для cairosvg, scikit-image, onnxruntime,
  opencv) или меняет поведение утилиты (pymorphy3). Чистые пакеты групп `net`, `morph`, `svgelements` можно поставить `install.sh --groups`.

## 7. Смоук

**Как.** `scripts/tests/smoke.py` прогоняет `smoke-list.tsv` (184 строки: взятое в `scripts/` и `kb/` + overlay) Python окружения с
таймаутом 90 с, в пустой рабочей папке, и печатает таблицу. Виды проверок (через «;»): `help [rc=N]`, `run: ARGS [rc=N]` (самопроверка;
`{skill}` в аргументах — корень скилла), `import-only` (импорт без `main`), `compile` (синтаксис: `.py`, `bash -n`, `node --check`),
`data`. Колонка `xfail` («run: причина» — только для run) превращает известное падение без окружения в XFAIL; прошедшая — XPASS.
Мой прогон — `code_stage.py --smoke` в `bwrap`: база app-design только для чтения, сеть отключена, браузеры Playwright, Brave и Blender
спрятаны, `DDD_HOME` временный, venv — общий.

| раскладка | что | PASS | FAIL | XFAIL | XPASS |
|---|---|---|---|---|---|
| `full` — по брифу: `kb/<база>` — симлинки на базы | код с правками против базы как есть | 203 | 3 | 9 | 1 |
| `faithful` — как после переноса: kb по файлам `expected-content.tsv`, 323 файла с переписанными путями (`scan-rewrites.tsv`), данные кода | главный результат | **206** | **0** | **10** | 0 |
| `srccache` — faithful + кэши ai-media источника (снимки каталогов, C2PA), только ai-media | проверка снимко-зависимого | 50 | 0 | 4 | 4 |

Три FAIL в `full` — артефакты этой раскладки: kb только для чтения (самопроверка `site_validate` пишет временную папку рядом с примерами)
и kb без переписывания путей (`--check` у `build_profile` и `ux_dict_to_yaml` сравнивает выход с файлом, который перенос переписывает);
в `faithful` все три — PASS. XPASS `validate_voice` в `full` — там доступны файлы опыта F/04, которые не переносятся.
Самопроверки, которые прошли в песочнице (без браузера и сети): `ui_audit`, `marketing_audit`, `motion_check`, `site_validate`,
`page_gates` (64/64), `ab_plan` (35/35), `vocab_lint`, `geo_probe` (33), `ia_probe` (26), `build_profile --check`,
`copydeck`, `claims_check`, `copy_lint`, `copy_extract`, `ux_dict_to_yaml --check`, `check_intake`, `chain_inputs`, `validate_meaning`,
`validate_facts`, `validate_any` на примерах kb, `run_checks` (8 эталонов copy deck: 0 ошибок, 30 с), `spec_check`, `recipe_check`,
`registry_check`, `validate_stack`, `ad_check`, `edit_check`, `video_loop_check`, `stand_run`, `stand_page`, `mockup_checks`,
`lang_check` на `kit/example`, `build_reference_tokens --out`, `color`, `check_links --selftest`, `kbpaths --selftest`, `install.sh --dry-run`.

**Отдельно проверено:** цепочка импорта Blender-модулей внутри Blender 5.2.2 (`blender -b --factory-startup`, песочница):
`rk, bpyx, d1lib, d1exp, d2lib, presets, animx, agent_scene, hygiene, preflight_block, glb_lint_block` импортируются, `kbpaths` отдаёт
`kb/blender`, `$DDD_HOME/node`, `$DDD_HOME/bin/gltfpack-1.2/gltfpack`; пути `sys.path` в 14 эталонных файлах kb ведут в `scripts/blender`;
`mp_client selftest` с кэшами источника даёт 39/41 — ровно как исходник в базе (2 цены RouterAI разошлись со свежим снимком).

**XFAIL — известные ограничения без окружения** (`code-xfail.tsv`):

| файл | проверка | причина | как снять |
|---|---|---|---|
| `ai-media/prompt_compile.py`, `tests/test_prompt_compile*.py` | help, run | нет снимка каталога polza (`99-raw/cache` не переносится) | `install.sh --catalogs`; со снимком источника — XPASS |
| `ai-media/polza_catalog.py`, `mp_client.py` | run selftest | самопроверки сравнивают снимки каталогов | `install.sh --catalogs` (polza_catalog со снимками источника — XPASS) |
| `ai-media/check_icons.py`, `svg_sheet.py` | help | нет cairosvg (cffi, libcairo2), scikit-image | `install.sh --groups core,svg` |
| `ai-media/provenance_check.py` | run selftest | нет c2patool и exiftool | `install.sh --bin` |
| `creative/refs_client.py` | run selftest | проверяет, что Brave на месте | Brave в PATH или `DDD_BRAVE` |
| `text/validate_voice.py` | run | примеры голоса ссылаются на факты `99-raw/experiments/F/04-voice-samples/facts-demo-*.yaml` | §11 п. 3 |

## 8. Исключения: взято, но без окружения или входов не работает целиком

- Нужен Blender (смоук — только синтаксис, импорт проверен в Blender отдельно): `bpyx`, `agent_scene`, `hygiene`, тесты bpyx,
  `render_views`, `scene_check`, `rk` и библиотеки D1/D2/E/H/C1, эталонные `build.py`.
- Без `--help` или поднимают браузер при запуске: `run_axe_targets.py` (аргументы и Playwright на уровне модуля — только компиляция),
  `idle_probe`, `lint_agent_code`, `three_probe`, `lang_check`, `layout_check`, `sheet`, `serve_br`, `run_doc_blocks`, `slot_run` — импорт.
- Входы опытов и фазы 5 не переносятся (правила A, «без ассетов» Р16): самопроверки `vlm_to_dna` (сетка бренда F, задание F-05),
  `asset_audit` и `test_asset_audit` (CC0-кадры, кейсы H/03, клипы K/03), `page_anatomy --selftest` (страница M/00); `layout_check`
  (шаблон и вырез M/06); `validate_recipes` (зовёт `polza_catalog price` — нужен снимок); `channel_diff` (снимки routerai/genapi);
  `routing_check` проверка № 11 (задания `phase5/jobs` — адаптация по Р54); `make_manifest`, `run_set` (данные регрессии — Р58, манифест
  ищется в `kb/blender/11-evaluation-qa/regression/manifest.json`); `vote/build_pairs` (якоря чужих сайтов A/sites); рецепт 03 (скриншот K/02).
- `site/checklist_export.py --check` — в замороженной базе YAML уже расходится с md (исходник даёт тот же ответ); смоук — `help`.
- Генераторы производных файлов (`ux/checklist_export`, `site/checklist_export`) при перезапуске запишут пути в новой форме (`ui/…`,
  `../../scripts/site/…`) — это верно для раскладки, но даст дифф с перенесёнными YAML.
- Самопроверка `site_validate` создаёт и удаляет `.selftest-*` рядом с `kb/site/10-playbooks-contracts/examples/` (так в источнике).
- Страница голосования blender — самодостаточная папка: `build_pairs`, `tally`, `vote_server` пишут `img/`, `pairs*.json`, `votes/`,
  `results.*` рядом с `index.html` в `scripts/blender/vote/`, `tally` — блок в `kb/blender/15-showcase/VERDICT.md` (§11 п. 4).

## 9. Решения B по кандидатам без решения (показать; действуют, пока не отменены)

| кандидат | решение | почему |
|---|---|---|
| `text/…/J/08-examples/run_checks.py` (SPEC §10 п. 16) | взять → `scripts/text/run_checks.py` | единственная сквозная проверка 8 эталонов copy deck; проходит за 30 с; `AGENTS.md` рядом не берётся |
| `ai-media/…/3D/**/{glb_pipeline,compare_video,glb_probe}.py` (SPEC §10 п. 16) | не брать | Р72: 3D-генераторы не используем; скрипты — только для «управляемого поворота» сгенерированной модели |
| creative `I/01-schemas/compat_check.py` (в правиле `cr-validators`, Р37 «и др.») | не брать | не в SYNTHESIS §4.1; выжимка — «история волн»; читает данные опыта A/02, которые не переносятся |
| blender `atlas_collect.py` (§4.1 «по решению») | не брать | входы — реестры опытов A/02, C2/00, F2/01 (не переносятся), атлас — скоропорт |
| blender `run_doc_blocks.py`, `slot_run.py` (§4.1 «по решению») | взять с правкой | исполняемая документация держит блоки кода md рабочими; очередь тяжёлых запусков нужна при нескольких агентах и 15 ГБ ОЗУ |
| creative `scroll_record.py` (§4.2 «не брать») | взять модулем | его импортирует взятый `motion_check` (`read_frames`, `find_flash`, `diff_regions`, `sheet`) — без него запись не разбирается |
| эталонный код kb blender: `build.py` ×11, `make_poster` ×2, `post.py` ×2, `build_scene.py`, `build.sh` ×2 (SPEC §9) | правка путей, место — kb | SYNTHESIS §4.1: «rk.py + build.py ×12 — с адаптацией»; без правки рецепты тянули бы `rk` из замороженной базы по абсолютному пути |
| `check_links.py` — «одна общая версия» | версия site → `scripts/maint/`, корень по умолчанию `kb/site`, другая база — `--root kb/<база>` | самая новая в линии ui → ai-media → text → site, с самопроверкой; остальные 5 версий — псевдонимы общего (ссылки ведут к нему) |
| `orch_check.py` | версия site → `scripts/maint/`; версии text и creative — псевдонимы | канон SYNTHESIS §4.1 |
| данные кода из опытов | взять `kind=data`: спецификации D/02 (E1–E5) и D/03 (B1, B2) — фикстуры тестов `prompt_compile`; `svgo.keep-signature.config.mjs` — конфиг `svg_sheet` | SPEC §9: «данные модулей внутри папок опытов → строкой tools-map с kind=data» |

## 10. Передача агенту C (`migrate.py`)

1. **Код по `tools-map.tsv`.** Строка на точный `source` главнее правил содержимого (SPEC §2). Для каждой строки:
   - `verdict=take` → копия байтов в `dest` (путь от корня шаблона), права — как у источника (`shutil.copymode`; `install.sh` — 0755);
     в `path-map.tsv` — `copy`.
   - `verdict=adapt` → `apply_patches.apply_patch(apply_patches.load_patch(apply_patches.patch_file_for(dest)))`: сверяет sha256 источника,
     счётчики и `result_sha256`; ошибка — стоп сборки. В `path-map.tsv` — `patched`, число замен — сумма `count` правок файла.
   - `verdict=skip`, `canonical=dup-of:…`, `dest` не пуст → псевдоним (22): не копировать, в `path-map.tsv` — «старый путь → `dest`
     канона», ссылки на него переписываются к канону (§7.1 SPEC). У 9 версий-дублей sha256 не совпадает с каноном — сверку «псевдоним
     = побайтный дубль» к строкам tools-map не применять. `skip` без `dest` → ничего (ссылки на него — «на непереносимое»).
   - Строки `_skill-build/tools/*` добавляют копию в `scripts/maint/`; зеркало журнала (`j-mirror`) остаётся.
   - Строки с источником в `99-raw/experiments/…` (`kind=data`: фикстуры, конфиг svgo) берутся, хотя правило `g-raw` их пропускает.
   - `kind=ref` (18 файлов kb): `dest` совпадает с местом правила `d-kb`; класть результат правки вместо простой копии; это код — §7.1
     переписывание к ним не применяется (SPEC §7.1 п. 1).
   - `kind=data` с `.md` (`scripts/{ai-media,blender,creative,site,text}/README.md`): сначала правка (`/home/mm`), затем переписывание
     путей §7.1 от старого места `…/99-raw/tools/README.md` (рекомендация, §11 п. 2).
   Проверка состава: каждая строка `scan-handoff.tsv` есть в `tools-map.tsv` (266 из 266); каждая правка — на строку `adapt`; места
   назначения копий уникальны (проверено генератором).
2. **Overlay** `overlay/.claude/skills/design-deep-dive/scripts/**` — как есть, поверх (после) строк tools-map; `README.md` и
   `tests/smoke-list.tsv` уже сгенерированы из `tools-map.tsv` (`code_stage.py --gen` — пересобрать, если tools-map поменяется).
3. **Данные кода** агента A (`purpose=code-data`: `scripts/ai-media/data/lucide-ref/`, `genapi_prices…json`, `scripts/blender/data/…hdr`)
   — по `expected-content.tsv`, с этими же путями их читает код.
4. **Проверки кода в `check`:** `python3 apply_patches.py --check` → 0 ошибок; `grep -rIl /home/mm scripts/` в дереве → 0 файлов; нет
   файлов-инструкций в `scripts/`; смоук: `python3 code_stage.py --smoke --root .staging --tag staging` (песочница как у меня; окружение
   смоука — в `.staging-code-results/`, дерево `.staging` не меняется) → **0 FAIL** (ожидаемо 10 XFAIL; XPASS — если окружение богаче);
   сырые строки — `.staging-code-results/code-smoke-staging.raw.tsv`. Смоук — только в песочнице (сеть отключена, браузеры и Blender
   спрятаны, источник только для чтения); самопроверка `site_validate` на время создаёт `.selftest-*` в `kb/site/…/examples/` — отпечаток
   дерева считать до смоука или после него.
5. `DDD_HOME` в шаблоне не создаётся и в git не попадает; `install.sh` в сборке не запускать (только `--dry-run`).

## 11. На решение

| № | пункт | рекомендация |
|---|---|---|
| 1 | **Проверка ссылок после переноса.** A просит, чтобы `scripts/maint/check_links.py` разрешал пути как `new_resolve` (SPEC §9); это смена логики, не механика. Версия site перенесена с правкой только корня | проверку «битых не больше» в `migrate.py check` делать `rules_eval.new_resolve`/`link_scan` (A); `check_links` — проверщик структуры одной базы (`--root kb/<база>`); общий проверщик по порядку `new_resolve` — при адаптации (Ф8) |
| 2 | README утилит `scripts/<база>/README.md` — md вне kb, 407 упоминаний путей `99-raw/…` (правило §7.1 SPEC их не видит: оно для kb) | переписывать в `migrate.py` тем же правилом §7.1, что md kb (после правки `/home/mm`) |
| 3 | `validate_voice` падает после переноса: `kb/text/05-voice-editorial/examples/voice-{grafa-b2b,peklo-bold}.yaml` ссылаются (`facts_ref`) на `text-research/99-raw/experiments/F/04-voice-samples/facts-demo-{grafa,peklo}.yaml` (2 файла, 44 КБ), правила A их не берут | взять оба в `kb/text/99-raw/experiments/F/04-voice-samples/` как raw-norm (правка `manifest-rules.yaml`, решение оркестратора); иначе XFAIL остаётся до уборки |
| 4 | Файлы, которые утилиты пишут внутри скилла по своей природе: страница голосования (`scripts/blender/vote/{img,votes,votes-test}/`, `pairs*.json`, `results.*`), `kb/site/10-playbooks-contracts/examples/.selftest-*/` | дописать в `.gitignore` скилла (файл оркестратора) |
| 5 | Каталог `$DDD_HOME/cache/` сверх списка SKILL-MAP §1 (кэши отдельно от выходов) | принять |
| 6 | Решения B по кандидатам без решения (§9) | принять, показать заказчику строкой |
| 7 | `install.sh`: адреса архивов бинарников и моделей записаны по релизам, но сетью не проверены (в сборке сеть не использовалась); у libavif, vtracer и моделей PP-OCR адреса нет | на этой машине первый запуск — `install.sh --bin --from <старый bin> --models --models-from <старые models>` (sha256 сверены в `--dry-run`); адреса проверить при первом запуске с сетью, расхождение ловит sha256 |
| 8 | Brave: `kbpaths.brave()` находит обёртку `brave-browser` из PATH; источник звал сам бинарник `/opt/brave.com/brave/brave` | на этой машине задать `DDD_BRAVE=/opt/brave.com/brave/brave` (в настройке окружения скилла) — поведение как в источнике |
| 9 | Устаревшие строки справки в коде (`python3 99-raw/tools/<утилита>.py …`, venv-* в сообщениях) — без `/home/mm`, запуск не ломают | поправить одним проходом при адаптации (Ф8) вместе со смысловыми правками |
| 10 | Генераторы производных файлов (`checklist_export` ux и site) после правки пишут пути в форме новой раскладки, а перенесённые YAML остались частично в старой (пути-каталоги без расширения переписывание A не трогает) — первая перегенерация даст дифф | перегенерировать при адаптации (Ф8) отдельным коммитом; для `build_profile` и `ux_dict_to_yaml` уже согласовано правкой (`--check` зелёный) |
