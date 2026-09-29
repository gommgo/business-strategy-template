# Утилиты скилла design-deep-dive

Указатель по папкам: утилиты баз знаний, `project` — утилиты по файлам проекта, `lib` — общие модули, `tests` — смоук и
фикстуры, `maint` — обслуживание; цепочка ворот собранной страницы — § Ворота после сборки.
Пути — от `scripts/`. Запуск — Python окружения: `~/.cache/design-deep-dive/venv/bin/python scripts/<домен>/<утилита>.py --help`;
пути к базе, выходы, кэши, блокировки, бинарники — `lib/kbpaths.py` (`python3 lib/kbpaths.py` показывает, что где).
Окружение ставит `install.sh` (§ Окружение); проверка — `tests/smoke.py` (§ tests).

Колонки: назначение — первая фраза описания утилиты; вход — как её запускать (подробно — `--help` и README домена);
выход — куда пишет по умолчанию (`$DDD_HOME` = `~/.cache/design-deep-dive`); зависимости — Python, npm, бинарники.

## Окружение — `install.sh`

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `install.sh` | maint | окружение утилит скилла вне репозитория — одно на машину для всех клонов; повторный запуск ставит только недостающее. | без ключей — venv (группа pip `core`), npm-зависимости, каталоги выходов; `--python python3.13` — Python 3.12–3.13 (без ключа — python3.13, python3.12 или python3 не ниже 3.12); `--groups core,net,morph,svg,ocr,media` или `all`; `--bin`, `--models`, `--browsers`, `--ffmpeg`; `--all` — всё это сразу; `--from DIR` и `--models-from DIR` — бинарники и модели из локальных папок, ключ повтором; `--playwright-match` — Playwright под Chromium из `PLAYWRIGHT_BROWSERS_PATH`; `--catalogs` — снимки каталогов генерации и список доверия C2PA (сеть, 0 ₽); `--dry-run` — план без изменений; `--check` — сверка установленного (версии, sha256) | `$DDD_HOME`: venv, node, bin, models, out, cache, locks | bash; Python 3.12–3.13; Node 24 и npm |

Системное, которое скрипт не ставит, и переменные его путей (Blender 5.2.2 — `DDD_BLENDER`, Node — `DDD_NODE`, Brave —
`DDD_BRAVE`, bwrap, systemd-run, flock, lzip, libcairo2) — `install.sh --help`; что нашлось — `install.sh --check`.

## lib — общие модули

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `lib/color.py` | module | Расчёты цвета для интерфейсов без внешних зависимостей. | `--help` | stdout / `--out` | stdlib |
| `lib/kbpaths.py` | module | пути скилла и окружения его утилит: база, соседние утилиты, данные, выходы, кэши, блокировки, бинарники, ключи. | `python3 lib/kbpaths.py` — что где; `--bins` — внешние программы; `--selftest` — в том числе запуск из соседнего чекаута | stdout | stdlib |
| `lib/docpaths.py` | module | раскладка файлов проекта `docs/projects/<slug>/` для утилит `project/`: корень данных, реестр поверхностей, пути слоёв, статусы файлов. | `python3 lib/docpaths.py [<slug>] [--repo DIR] [--json]` — поверхности, слои, файлы уровня продукта; `--selftest` | stdout | stdlib; статусы YAML — PyYAML, если есть |

## ux — логика продукта

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `ux/checklist_export.py` | utility | Экспорт сводного чек-листа в YAML. | `[--check]` — сверка байт в байт без записи | `kb/ux/12-evaluation-checklists/master-checklist.yaml` | PyYAML |
| `ux/states_export.py` | utility | Экспорт словаря состояний экрана и матрицы «экран или компонент × состояние» в YAML. | `[--check]` — сверка байт в байт без записи; `--selftest` | `kb/ux/06-feedback-states-motion/screen-states.yaml` (его читают `project/states.py` и аудиты экранов) | PyYAML |

## ui — визуальный язык

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `ui/build_reference_tokens.py` | utility | Генератор эталонной схемы токенов ui (ui 09/04). | `[--out DIR]` | `$DDD_HOME/out/ui/reference-tokens`: tokens.json, tokens.css, theme.css, report.txt | stdlib |
| `ui/measure_ui.py` | utility | Измерить визуальный слой живой веб-страницы через headless-браузер (Playwright/Chromium). | `URL [--viewport WxH] [--surface app\|page] [--preset A\|B\|C\|D]`; `--batch`, `--summary`, `--selftest` | `$DDD_HOME/out/ui/measurements`, `$DDD_HOME/out/ui/screens` | playwright; chromium (Playwright) |
| `ui/ui_audit.py` | utility | Визуальный QA экрана или страницы: измерение computed styles, сверка с токенами ДС и порогами базы ui, отчёт. | `ПУТЬ_ИЛИ_URL [--preset admin\|consumer] [--tokens ФАЙЛ]` (DTCG или CSS токенов ДС) `[--acceptance] [--touch] [--scheme both]`; `--slop-params` — параметры скрипта маркеров ui 11/04; `--selftest` | `$DDD_HOME/out/ui/audit` | playwright; chromium (Playwright) |

Данные кода: `ui/data/thresholds.yaml` (пороги кеглей и высоты шапки — общие для `measure_ui`, `ui_audit` и
`mockup_checks`), `ui/data/marketing-profile.yaml` (профиль `marketing` страницы сайта — его читают `ui_audit` и
`marketing_audit`).

## site — сайты и лендинги

Подробный README домена — `site/README.md` (из базы).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `site/ab_plan.py` | utility | план и проверка A/B-теста страницы сайта. | `--help` | stdout / `--out` | stdlib |
| `site/checklist_export.py` | utility | сводный чек-лист сайта из Markdown в YAML. | `[--check]` — сверка без записи; `--selftest` | `kb/site/09-ai-generation-evaluation/site-checklist.yaml` | PyYAML |
| `site/geo_probe.py` | utility | доступность страницы для поисковых и ИИ-ботов: robots, коды, head, текст без JS, JSON-LD, SSR. | `URL --out DIR` (§ Ворота после сборки) | stdout / `--out` | PyYAML, playwright, requests, urllib3; chromium (Playwright, --render) |
| `site/ia_probe.py` | utility | структура многостраничного сайта по HTTP: robots, sitemap, шаблоны URL, шапка и подвал, крошки, hreflang, 404. | `URL --out DIR`; `--batch`, `--selftest` | `$DDD_HOME/out/site/ia_probe/selftest`, `$DDD_HOME/out/site/ia_probe` | stdlib |
| `site/page_anatomy.py` | utility | анатомия живой посадочной страницы или страницы сайта: структура, призывы, формы, согласия, скорость, вес. | `URL OUT [--mobile] [--inp]`; `--selftest` | `<OUT>/anatomy_<устройство>.json`; кэш — `$DDD_HOME/cache/site` | Pillow, playwright; web-vitals 6.2.2; chromium (Playwright) |
| `site/page_gates.py` | utility | ворота собранной страницы: вердикт PASS / S / B по `page-gates.yaml` с порогами профиля бюджета. | `--profile P --anatomy DIR --accept DIR --motion DIR --gate3d ФАЙЛ … [--geo] [--ia] [--axe] [--plan] [--json]` (§ Ворота после сборки); `--resolve P` — профиль бюджета JSON; `--conditions`; `--selftest` | stdout: таблица или `--json` | PyYAML |
| `site/plan_to_assets.py` | utility | план ассетов страницы: каркас из медиа- и 3D-слотов плана страницы и проверка плана. | `build <slug> [<surface>] [--page ID …] [--write]` — каркасы, с `--write` — в проект страницам без плана ассетов; `check <slug> [<surface>] [--json]` — находки контракта `project/`; вне проекта — `PAGE_PLAN [--out ФАЙЛ]`, `--check ФАЙЛ … [--plan PAGE_PLAN]`, `--spec-role`, `--types` | `build` — `$DDD_HOME/out/site/plan_to_assets/<slug>/`, с `--write` — `…/design/<surface>/assets/plans/<page-id>.yaml` | PyYAML, jsonschema |
| `site/site_validate.py` | utility | схемы и перекрёстные ссылки контрактов сайта: бриф, план страницы, карта сайта, каталог блоков, формы. | `ПУТЬ… [--today ГГГГ-ММ-ДД] [--json OUT] [--quiet]` (папка поверхности — со всеми стыками); `--all`, `--selftest` | stdout / `--json` | PyYAML, jsonschema, referencing |
| `site/vocab_lint.py` | utility | идентификаторы вне словаря site в YAML, JSON и Markdown; проверка таблицы соответствий словарей. | `ФАЙЛ… [--map КЛЮЧ=ПРОСТРАНСТВО]`; `--check-crosswalk` — таблица `crosswalk.tsv`; `--selftest` | stdout | PyYAML |
| `site/build_profile.py` | step | маркетинговый профиль UX-чек-листа для страниц сайта: решение по каждому пункту UX-* сводного чек-листа ux. | без ключей — пересборка; `--check` — сверка без записи (код 1 — расходится); `--selftest` | `kb/site/09-ai-generation-evaluation/ux-marketing-profile.tsv`, `kb/site/99-raw/experiments/K/02-ux-profile/ac-profile.tsv` | PyYAML |
| `site/run_axe_targets.py` | step | axe-core с адресами узлов: какие элементы проваливают color-contrast и прочие правила SG-A11Y-01. | `ID URL MARKET OUTDIR` (§ Ворота после сборки); замок браузера — снаружи | `<OUTDIR>/<id>.json` | playwright; axe-core 4.13.0; chromium (Playwright) |

Данные кода: `site/README.md`.

## text — тексты

Подробный README домена — `text/README.md` (из базы).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `text/claims_check.py` | utility | сверка текстов сайта с белым списком фактов (facts.yaml): ядро «контура честности» базы text. | `check ВХОД [--facts ФАЙЛ] [--genre …] [--jurisdiction …] [--legal-category …]` (copy deck, `copy.md`, md, HTML); `lint-facts ФАКТЫ`; `inventory`, `rules-schema` | stdout / `--json`, `--md` | PyYAML |
| `text/copy_extract.py` | utility | страница (URL или сохранённый HTML) → структурированный текст по слотам (JSON). | `URL [-o OUT] [--genre …]`; `--html ФАЙЛ`; `--batch`; `--selftest` | stdout / `-o` | Pillow, playwright; chromium (Playwright) |
| `text/copy_lint.py` | utility | линтер текстов RU/EN по жанру и роли строки: маркетинговые тексты сайта и тексты интерфейса. | `ФАЙЛ… [--genre …]`; реестр `texts.md` — целиком в жанре `interface`; одна строка — `- --genre interface --role РОЛЬ` или `--component Тип.Часть`; `--voice ФАЙЛ`, `--customer-words ФАЙЛ`; коды: 0 — нет error, 2 — есть, 1 — ошибка вызова | stdout / `--json`, `--md` | PyYAML, pymorphy3 |
| `text/copydeck.py` | utility | copy deck: каркас из плана страницы, проверка формата и стыка, сверка с фактами, линтер, статусы, выбор вариантов, утверждение, выгрузка во вход холста и приём правок текста с холста. | `skeleton PLAN -o DECK`; `check DECK [--update OUT [--promote]]`; `validate DECK [--final]`; `approve DECK --page ID --by КТО -o OUT`; `export DECK --page ID --stage directions\|wireframe\|mockup`; `import-copy COPY.md --deck DECK --page ID -o OUT`; `export-assets`, `export-variants`, `apply-selection`, `verify-page`; коды: 0 — нет error, 2 — есть, 1 — ошибка входа | stdout / `--json`, `--md`; `export` — `$DDD_HOME/out/text/export` | PyYAML, jsonschema |
| `text/ux_dict_to_yaml.py` | utility | словарь запретов ux 07/06 и длины по ролям ux 07/01 §12 → производный YAML для copy_lint.py. | без ключей — пересборка; `--check` — сверка без записи (код 3 — устарел); `--selftest` | `kb/text/06-anti-slop/lexicon/ux-07-06.yaml` | PyYAML |
| `text/chain_inputs.py` | step | проекции входов промтов P2–P7 и «код между шагами» цепочки генерации copy deck. | `digest-meaning`, `meaning-claims`, `hierarchy-input`, `section-input`, `edit-input`, `judge-input`, `judge-score`, `assemble`, `apply-edits`, `canvas-texts`; `--selftest` | stdout / `--out` | PyYAML |
| `text/check_intake.py` | step | проверка выхода промта P1 (разбор брифа) кодом. | `--help` | stdout / `--out` | PyYAML |
| `text/make_skeleton.py` | step | каркас copy deck v1 из иерархии сообщений, когда плана страницы нет (шаг S5 цепочки промтов). | `ИЕРАРХИЯ [--facts Ф] [--voice Г] [--page-id ID] -o OUT`; `--selftest`; с планом — `copydeck.py skeleton` | stdout / `-o` | PyYAML |
| `text/run_checks.py` | step | все проверки примеров copy deck базы по порядку аудита текстов: claims_check.py --legal-category → copy_lint.py → copydeck.py check → copydeck.py validate. | без ключей | `$DDD_HOME/out/text/run_checks` | PyYAML |
| `text/validate_any.py` | step | проверки смысла (схема + смысл) для meaning и иерархий сообщений проекта, вне примеров базы. | `ФАЙЛ …` | stdout | jsonschema |
| `text/validate_facts.py` | step | проверка схем фактов и голоса клиента (facts.schema.yaml, voc.schema.yaml) и примеров базы. | без ключей | stdout | PyYAML, jsonschema |
| `text/validate_meaning.py` | step | проверка схем смысла и иерархии сообщений и примеров базы: схема, смысловые проверки, отрицательные случаи. | `[--quiet]` | stdout | PyYAML, jsonschema |
| `text/validate_voice.py` | step | проверка voice.schema.yaml и профилей голоса бренда (voice.yaml) и продукта (voice.product.yaml): схема, смысловые проверки, отрицательные мутации. | `[ФАЙЛ …]`; без файлов — примеры базы | stdout; итог — `$DDD_HOME/out/text` | PyYAML, jsonschema |

Данные кода: `text/README.md`.

Коды выхода проверок текста: у `claims_check.py`, `copy_lint.py`, `copydeck.py`, `run_checks.py` 0 — `error` нет, 2 —
есть `error`, 1 — ошибка вызова или входа; у `validate_*.py` 1 — есть ошибки. У утилит `project/` порядок обратный:
1 — есть `error`, 2 — сбой вызова (§ project).

## creative — подача и движение

Подробный README домена — `creative/README.md` (из базы).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `creative/marketing_audit.py` | utility | визуальные проверки страницы сайта: профиль `marketing` поверх ui_audit.py и свои проверки подачи. | `URL\|ФАЙЛ.html [--level L0\|L1\|L2] [--acceptance] [--art-direction ФАЙЛ] [--levels ФАЙЛ] [--allow cliche:…]`; `--batch`, `--profile-md`, `--selftest` | `$DDD_HOME/out/creative/audit` | Pillow, PyYAML, numpy, playwright; chromium (Playwright) |
| `creative/motion_check.py` | utility | цикл проверки сборки: запись → кадры → метрики → сверка с motion-spec → ворота эффектов → отчёт. | `ЦЕЛЬ --level L0\|L1\|L2 [--page-type T] [--spec ФАЙЛ] [--out DIR]` (§ Ворота после сборки); `report --in DIR`; `--selftest` | `$DDD_HOME/out/creative/motion` | Pillow, PyYAML, brotli, numpy, playwright; chromium (Playwright), ffmpeg, flock |
| `creative/refs_client.py` | utility | клиент референсов: вход заказчика в площадки, режимы «поиск» и «ассистент», библиотека заказчика, мудборд, выгрузки в бриф и базу. | `login`, `search`, `get`, `enrich`, `lib list\|show\|tag\|dedup\|export [--format jsonl\|brief\|base-safe]`, `board`, `handoff МУДБОРД --out DIR`, `selftest` | `$DDD_HOME/cache/creative/refs` | Pillow, numpy, playwright; brave 153 (DDD_BRAVE или PATH), chromium |
| `creative/ad_check.py` | step | проверка арт-дирекции сайта: файл проекта или пример базы. | `[ФАЙЛ …] [--json]` — без файлов все примеры базы; `--selftest` | stdout; `--json` — один JSON | PyYAML, jsonschema, referencing |
| `creative/idle_probe.py` | step | J/02 · зонд «рисует ли холст в покое» — два снимка счётчика вызовов WebGL внутри одной паузы. без --help: запуск поднимает браузер | см. докстринг | stdout / `--out` | playwright; chromium (Playwright) |
| `creative/recipe_check.py` | step | проверка рецептов 10-recipes/recipes/*.recipe.yaml. | `--help` | stdout / `--out` | PyYAML, jsonschema |
| `creative/registry_check.py` | step | Проверка реестра клише kb/creative/08-uniqueness-anti-slop/cliche-registry.yaml и его стыков. | `[--refs DIR …] [--json]`; `--selftest` | stdout | PyYAML |
| `creative/spec_check.py` | step | проверки и проекции подачи: treatment плана страницы, спецификация движения, варианты подачи блоков, проекция во вход холста. | `plan ПЛАН`, `spec СПЕЦИФИКАЦИЯ`, `blocks`, `moments`, `motion-md`, `values`, `levels [--check]`, `canvas-map [ФАЙЛ …]`; `--levels ФАЙЛ`; `--selftest` | stdout | PyYAML, jsonschema, referencing |
| `creative/validate_stack.py` | step | Проверка каталога стека подачи kb/creative/07-stack-implementation/stack.yaml. | `[--file ФАЙЛ]`; `--selftest` | stdout | PyYAML |
| `creative/scroll_record.py` | module | запись прокрутки страницы и движение в паузах; модуль motion_check.py. | модуль / без `--help` | stdout / `--out` | Pillow, numpy, playwright; chromium (Playwright), ffmpeg, ffprobe |

Данные кода: `creative/README.md`.

## ai-media — картинки и видео

Подробный README домена — `ai-media/README.md` (из базы).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `ai-media/alpha_check.py` | utility | проверка прозрачности (вырез, нативная альфа модели, матирование). | `--help` | stdout / `--out` | Pillow, numpy, scipy |
| `ai-media/asset_audit.py` | utility | автоматическая приёмка ИИ-ассетов сайта и пакет судьи по рубрике. | `audit ПУТЬ… [--mode M] [--slot hero\|section\|product\|icon\|og] [--stage web] [--mobile]`; `judge-jobs (--items ФАЙЛ \| --from-stand-page DIR \| --calibration) [--rubric R] [--mode checklist\|defects\|pairwise] [--runs 3]` — пакет заданий агенту `design-judge`; `judge-parse ПАКЕТ` — разбор ответов; `agree`, `calibrate`, `thresholds [--check]`, `selftest` | `$DDD_HOME/out/ai-media/audit`, пакеты судьи — `$DDD_HOME/out/ai-media/judge`, `$DDD_HOME/cache/ai-media/polza` | Pillow, PyYAML, numpy, rapidocr, scipy; ffmpeg, ffprobe, flock; $DDD_HOME/bin: exiftool, c2patool, libjxl (ssimulacra2, djxl), libavif (avifdec), libwebp (dwebp); models/ocr |
| `ai-media/asset_inventory.py` | utility | инвентарь визуальных ассетов живой страницы. | `URL OUT_DIR [--mobile] [--quick] [--throttle]`; `--selftest` | папка OUT_DIR: инвентарь JSON, контактный лист | Pillow, playwright; chromium (Playwright) |
| `ai-media/avif_pick.sh` | utility | минимальный AVIF, проходящий порог SSIMULACRA2. | `<вход.png> <выход.avif> [порог]` | файл выхода; строки q, байты, s2 — stdout | $DDD_HOME/bin: libavif 1.4.2 (avifenc, avifdec), libjxl 0.12.0 (ssimulacra2) |
| `ai-media/edit_check.py` | utility | проверка правки картинки нейросетью и композит оригинала обратно. | `--help` | stdout / `--out` | Pillow, numpy, scipy |
| `ai-media/mp_client.py` | utility | клиент каналов генерации вне Media API polza: RouterAI, Gen-API, polza-chat, polza-images. | `estimate JOBS…`, `run JOB` (сухой прогон; трата — только `--live`), `batch`, `status`, `download`, `ledger`, `show`, `snapshot`, `selftest` | `$DDD_HOME/cache/ai-media`, `$DDD_HOME/out/ai-media`, `$DDD_HOME/out/ai-media/_mp` | Pillow; ffprobe (необязательно) |
| `ai-media/page_accept.py` | utility | приёмка страницы с ассетами в Chromium: вес, LCP, CLS, картинки, видео и постер, движение, reduce, F83. | `PAGE --out DIR [--budget-profile P] [--mobile --throttle] [--acceptance]` (§ Ворота после сборки) | `<DIR>/accept_<режим>.json` | Pillow, numpy, playwright, scipy; chromium (Playwright) |
| `ai-media/polza.py` | utility | клиент Media API polza.ai для ai-media-research: сухой прогон по умолчанию, трата только с --live. | `--help` | `$DDD_HOME/out/ai-media`, `$DDD_HOME/out/ai-media/_polza` | Pillow; ffprobe (необязательно) |
| `ai-media/polza_catalog.py` | utility | каталог polza.ai как данные: снимки, нормализация медиа-моделей, таблица, сравнение снимков, калькулятор цены и валидатор входа по каталогу (библиотека для polza.py). | `--help` | `$DDD_HOME/cache/ai-media/polza` | stdlib |
| `ai-media/prompt_compile.py` | utility | компилятор промтов: спецификация ассета → промт в диалекте модели + параметры задания. | `--help` | stdout / `--out` | Pillow, PyYAML, jsonschema |
| `ai-media/provenance_check.py` | utility | бесплатная проверка провенанса ИИ-ассетов (0 ₽, без сети). | `--help` | `$DDD_HOME/cache/ai-media/c2pa-trust-2026-09-23` | Pillow, numpy, scipy; ffmpeg; $DDD_HOME/bin: exiftool 13.59, c2patool 0.27.22 |
| `ai-media/routing_check.py` | utility | проверка 13-routing-matrix/routing.yaml. | `--help` | `$DDD_HOME/out/ai-media/phase5/jobs` | PyYAML |
| `ai-media/stand_run.py` | utility | стенд моделей ai-media: задания по рецептам стенда, сбор результатов, автометрики, контактные листы, страница слепого попарного голосования (картинки и текстовые варианты), подсчёт голосов. | `build`, `estimate`, `run`, `collect`, `metrics`, `sheet`, `page [--text ЛИСТ --text-key КЛЮЧ]` — текстовые карточки листа `copydeck.py export-variants`; `tally --key КЛЮЧ [--selection OUT]` — победы меток для `copydeck.py apply-selection`; `ministand`, `selftest` | `$DDD_HOME/out/ai-media/phase5/jobs`, `$DDD_HOME/out/ai-media/_polza/E` | Pillow, PyYAML, numpy, scipy |
| `ai-media/tile_check.py` | utility | бесшовность текстуры: метрика шва, тайл разрезом минимальной ошибки, превью. | `--help` | stdout / `--out` | Pillow, numpy |
| `ai-media/video_loop_check.py` | utility | приёмка ИИ-видео для сайта: шов петли, «живость», мёртвые концы, склейки, дрейф неподвижных зон и камеры, однородность хромакея, стык клипов цепочки, контактный лист. | `--help` | stdout / `--out` | Pillow, numpy, scipy; ffmpeg, ffprobe |
| `ai-media/vlm_to_dna.py` | utility | паспорт визуала бренда (visual DNA): разбор сетки бренд-картинок сессией Opus → черновик паспорта, проверка по схеме и смыслу, сверка прогонов, грейд .cube, вывод из токенов UI, спецификация ассета. | `grid`; `build СЕТКА [--runs 2]` — пакет для агента `design-judge`; `parse ПАКЕТ --out ФАЙЛ [--art-direction ФАЙЛ]`; `validate`, `compare`, `lut`, `from-tokens`, `to-spec`, `selftest` | пакеты — `$DDD_HOME/out/ai-media/dna`; `$DDD_HOME/out/ai-media/phase5/jobs` | Pillow, jsonschema, numpy |
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
| `ai-media/tests/test_asset_audit.py` | test | Тесты asset_audit.py без сети и платных вызовов: пороги, проверки картинок на синтетике, пакет судьи на заглушках ответов. | `--help` | stdout / `--out` | Pillow, numpy, scipy; ffmpeg |
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
| `blender/gate_check.py` | utility | ворота страницы с 3D по отчёту зонда site_probe.py (probe*.json). | `ПРОБА mobile\|desktop [--reduced] [--baseline ПРОБА_БЕЗ_3D] [--profile P] [--json]` (§ Ворота после сборки); `--selftest` | stdout | stdlib |
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
| `blender/site_probe.py` | utility | замер страницы с 3D (живой сайт или собранная страница): сеть, контексты, вызовы отрисовки, кадры, LCP, TBT. | `URL OUT_DIR [--mobile] [--throttle] [--quick] [--no-3d [--block ШАБЛОН …]] [--reduced-motion]` (§ Ворота после сборки); `--selftest` | `<OUT_DIR>/probe[…].json` и кадры | Pillow, playwright; chromium (Playwright) |
| `blender/slot_run.py` | utility | очередь для тяжёлых запусков, когда параллельно работают несколько агентов. | см. докстринг | stdout / `--out` | flock (очередь для blender и браузера) |
| `blender/three_probe.py` | utility | загрузить GLB в three r186 (Chromium, GPU) и выполнить JS-проверку; вывести JSON. | см. докстринг | stdout / `--out` | playwright; three 0.186.0 (с jsDelivr, сеть); chromium (Playwright) |
| `blender/vote/build_pairs.py` | utility | собрать pairs.json и img/ страницы «Кадр против кадра» из кадров судьи предметов. | см. докстринг | `blender/vote/{img/,pairs.json}` — папка страницы голосования | Pillow |
| `blender/vote/tally.py` | utility | итоги слепого голосования «Кадр против кадра» → results.json, results.md и блок в вердикте. | см. докстринг | блок итогов в `kb/blender/15-showcase/VERDICT.md`; results.* рядом со страницей | stdlib |
| `blender/vote/vote_server.py` | utility | локальный сервер страницы «Кадр против кадра». | см. докстринг | голоса — `<dir>/votes/<голосующий>.json` (папка `--dir`) | stdlib |
| `blender/web_view.py` | utility | Проверка 3D в браузере: GLB в three.js или готовая страница — через headless Chromium на реальной видеокарте. | `<модель.glb> OUT_DIR`; `--page ФАЙЛ OUT_DIR`; `--url URL OUT_DIR`; `--selftest` | stdout / `--out` | Pillow, playwright; three 0.186.0 (с jsDelivr, сеть); chromium (Playwright) |
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

Статичные копии, кадры и проверки холста (протокол — `../references/claude-design.md § HTML-копии и kit`, `§ Проверки
по постоянной просьбе`). Утилиты с командами `build` и `check` по проекту — тот же вызов и те же находки, что у раздела
`project` (§ project).

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `claude-design/dc_to_html.py` | utility | статичные HTML-копии артбордов холста Claude Design: перевод исходника `<Имя>.dc.html` в обычный HTML. | `build <slug> <surface>`; `check <slug> <surface>` — R-FRESH-005; `fingerprint <slug> <surface> [--artboards А.dc.html,Б.dc.html]` — отпечаток артбордов для `REVIEW.md`; вне проекта — `convert ФАЙЛ … [--out DIR] [--tweak имя=значение]`; `--selftest` | `build` — `…/design/<surface>/canvas/html/<Имя>.html`; `convert` — `$DDD_HOME/out/claude-design/dc_to_html` | Node (renderVals) |
| `claude-design/kit/kit_manifest.py` | kit | манифест кадров kit.json HTML-копий холста: копии × ширины приёмки × темы, класс экрана, границы ДС. | `build <slug> <surface>`; `check <slug> <surface>` — R-FRESH-005; вне проекта — `make ПАПКА_КОПИЙ [--tokens ФАЙЛ] [--route page\|app] [--out ФАЙЛ]`; `--selftest` | `build` — `…/design/<surface>/canvas/html/kit.json` | PyYAML |
| `claude-design/copies_compare.py` | utility | сверка адаптивной копии страницы или экрана со статичными копиями её артбордов. | `check <slug> <surface> [--pairs СТРАНИЦА=А.html,Б.html] [--tol 8] [--no-geometry]` — R-VIS-001; вне проекта — `pair АДАПТИВНАЯ СТАТИЧНЫЕ…`; `--selftest [--browser]` | stdout | playwright; chromium (Playwright) |
| `claude-design/dc_texts.py` | utility | тексты исходников холста в формате `copy.md`: обратный разбор правок заказчика для приёма в copy deck. | `show <slug> <surface> --page ID [--artboards …] [--out ФАЙЛ]`; вне проекта — `file АРТБОРД… [--deck DECK --page ID]`; `--selftest`; дальше — `copydeck.py import-copy` | stdout / `--out` (например, scratchpad) | Node (renderVals) |
| `claude-design/literal_tokens.py` | utility | «литерал ∈ значений токенов ДС»: облик артбордов холста и адаптивных копий против токенов продукта. | `check <slug> <surface> [--accepted] [--all-stages]` — R-VIS-004 (`warning`, у принятого макета — `error`); вне проекта — `scan ФАЙЛ… --tokens ФАЙЛ`, `tokens ФАЙЛ…`; `--selftest` | stdout | stdlib; Node (renderVals) |
| `claude-design/lang_check.py` | utility | проверка языка готовой вёрстки русскоязычной страницы: HTML-копии артбордов, сборка (без модели и сети). | `ПАПКА_ИЛИ_HTML [--copy copy.md] [--json]`; коды: 0 — чисто, 1 — есть находки, 2 — нет аргумента | stdout | stdlib |
| `claude-design/mockup_checks.py` | utility | проверки макета по отрисованной HTML-копии: приметы «дефолтного вида», честность содержимого, формы, телефон, наложения, ресайз. | `page КОПИЯ [--acceptance] [--surface page\|app] [--preset A-D] [--tokens ФАЙЛ] [--facts facts.md\|facts.yaml] [--copy copy.md --page ID] [--assets …] [--forms …] [--allow …] --json OUT`; `resize КОПИЯ`; `selftest`; коды `page`: 0 — нет critical и major, 2 — есть, 1 — ошибка, 3 — мало памяти | `--json`, `--md`; кадры — `--shots DIR` | Pillow, playwright; chromium (Playwright) |
| `claude-design/shot_v3.py` | utility | кадры страницы или сборки по экранам и проверки, которых не видно на ужатом кадре (любой URL или папка). | `ЦЕЛЬ OUTDIR [--views WxH,…] [--routes /,/x] [--strict]` | `<OUTDIR>`: кадры, shots.json | playwright; chromium (Playwright) |
| `claude-design/stand_page.py` | utility | страница слепого попарного выбора для стенда тестов. | `build`, `simulate`, `tally`, `power`, `fake`, `selftest` | stdout / `--out` | Pillow |
| `claude-design/kit/canvas.html` | kit | холст kit для `shot.py serve`: рамки артбордов по `canvas.json`. | данные | — | — |
| `claude-design/kit/diffshots.py` | kit | «изменилось только то, что просили»: сравнение двух снимков shot.py по меткам #N. | `--help` | stdout / `--out` | Pillow, numpy |
| `claude-design/kit/example/booking.html` | kit | пример холста kit: артборд. | данные | — | — |
| `claude-design/kit/example/canvas.json` | kit | пример холста kit: манифест рамок. | данные | — | — |
| `claude-design/kit/example/landing.html` | kit | пример холста kit: артборд. | данные | — | — |
| `claude-design/kit/example/site.css` | kit | пример холста kit: стили. | данные | — | — |
| `claude-design/kit/example/tokens.css` | kit | пример холста kit: токены. | данные | — | — |
| `claude-design/kit/export.py` | kit | экспорт холста без интерфейса Claude Design: PDF по артбордам, PNG 2×, standalone.html, zip. | `--help` | stdout / `--out` | Pillow, playwright, pypdf; chromium (Playwright) |
| `claude-design/kit/marks.js` | kit | нумерованные метки #N поверх артборда для правок из чата. | подключают `canvas.html` и `shot.py` | — | — |
| `claude-design/kit/shot.py` | kit | «глаза» холста для работы из чата: PNG каждого кадра HTML-копий (с метками #N и без), весь холст, marks.json. | `ПАПКА_КОПИЙ OUTDIR [--manifest kit.json] [--widths manifest\|acceptance] [--themes light,dark] [--prev marks.json]`; `serve ПАПКА_ПРОЕКТА` | `<OUTDIR>`: PNG, marks.json, marks.md, shots.json | Pillow, playwright; chromium (Playwright) |

## Ворота после сборки — кто кого зовёт

Фаза `build` в репозитории кода: собранную страницу проверяют утилиты этого скилла, запущенные соседним чекаутом
`../strategy/.claude/skills/design-deep-dive/scripts/…` с рабочей папкой код-репо; окружение — `$DDD_HOME` машины.
Порядок: замеры (`page_anatomy`, `page_accept --budget-profile`, `motion_check`; у страницы с 3D — `site_probe` дважды,
второй раз с `--no-3d`, и `gate_check` по каждому прогону) → вердикт `page_gates.py --profile <budget_profile плана>
--anatomy … --accept … --motion … --gate3d …`. Вердикт — поля `verdict`, `B`, `S` вывода `page_gates.py --json`: код 1
— есть B (страница не передаётся), 0 — нет; S — исправить или записать исключением `x-gate-exception` плана. Пункты
`after_build` манифеста `ready.yaml` — команды этой таблицы. Профиль бюджета без замера — `page_gates.py --resolve P`
(его читает `project/canvas_input.py`).

| звено | выход | кто читает | поля |
|---|---|---|---|
| `site/page_anatomy.py URL OUT [--mobile] --inp` | `<OUT>/anatomy_<desktop\|mobile>.json` | `page_gates.py --anatomy OUT` | `summary.*` (`lcp_ms`, `cls_session`, `tbt_ms`, `inp_wv_ms`/`inp_lab_ms`, `first_screen_kb`, `session_kb`, `title_len`, `canonical`, `lang`, `h1_n`, `nojs_*`, `overflow_x_px`, `layout_zoomed`, `burger`, `header_nav_links`, `cta_first_screen`, `tracking_before_action`, `cmp*`, `forms_n`, `consent_*`, `policy_link_in_form`, `footer_ogrn`), `pre.lcp[]`, `fin.lcp[]`, `fin.wv_cls`, `first_screen.{t, by_type_kb}`, `network.{third_party[], by_type_kb, tracking_requests[]}`, `nav.html_kb`, `dom.headings`, `dom.ctas`, `nojs.{h1_raw_n, h1_raw}`, `cookies_before`, `h1_paint.{first_op, first_hidden, t_first, t_visible, t_opaque, in_first_screen}` |
| `ai-media/page_accept.py PAGE --out DIR --budget-profile P [--mobile --throttle]` | `<DIR>/accept_<режим>.json` | `page_gates.py --accept DIR`; `motion_check.py --f83` | верх: `tool`, `mode`, `device` (`desktop`/`mobile`), `throttle`, `profile {id, level, log}`, `thresholds {first_screen_kb, lcp_goal, lcp_poor, cls_goal, cls_poor}`, `window_after_load_s`, `viewport`, `verdict {pass, fail[], warn[], ok[]}`; `no_preference`: `lcp {t, tag, size, url, lazy, fp}`, `cls`, `tbt_ms`, `first_screen_kb {тип: КБ}`, `first_screen_total_kb`, `weight_measured`, `dom {imgs[], vids[], ua, webdriver, overflow_px}`, `media_first[]`, `motion_6s {pct, videos_playing, pause_control, moving}`, `loops {scope, found[], checked[], pause_control, without_pause[]}`, `console[]`, `contrast[]`; `reduce`: то же + `media_kb`, `session_kb`, `motion {…}`; `acceptance[] {width, device, dpr, overflow_px, over[], no_wh[]}` |
| `creative/motion_check.py PAGE --level L --page-type T --out DIR` | `<DIR>/results.json`, `<DIR>/gates.json`, `<DIR>/gates.md` | `page_gates.py --motion DIR` | `results.<desk\|mob\|rm>.derived.{moving_6s_without_pause, loops_without_pause, flash_fail, flash_area_frac, intro_fail}`, `.vitals.{lcp_ms, tbt_ms}`, `.cls.window_max`, `.net.{first_kb, session_kb, font_kb}`; в gates.json — `rows[] {id, mode, verdict, severity, found, threshold}`, `level`, `page_type`, `presentation` |
| `blender/site_probe.py URL OUT --quick [--mobile --throttle] [--no-3d]` | `<OUT>/probe[…].json` | `blender/gate_check.py` | `vitals_pre_scroll.{lcp.tag, lcp.t, cls, tbt_ms, first_draw_ms}`, `network.{transfer_kb, by_category}`, `idle.dc_median`, `idle_motion_pct`, `detected.canvases[]`, `console_errors`, `no_3d.aborted` |
| `blender/gate_check.py ПРОБА mode [--reduced] --baseline ПРОБА_БЕЗ_3D --profile P --json` | stdout JSON | `page_gates.py --gate3d ФАЙЛ …`; `qa_pipeline.py page` (кортежи функции `gate_check`) | `tool`, `probe`, `mode`, `reduced`, `baseline`, `profile`, `gates`, `rows[] {id, key, check, value, limit, severity (B/S/D), status (PASS/FAIL/SKIP), note, mirror}`, `summary {B, S, D, blocked}` |
| `site/geo_probe.py URL --out DIR` · `site/ia_probe.py URL --out DIR` · `site/run_axe_targets.py ID URL MARKET DIR` | `<id>.json` · `<id>/ia.json` · `<id>.json` | `page_gates.py --geo`, `--ia`, `--axe` | флаги `head-kit.yaml`; `summary`, `sitemap`, `robots`, `not_found`; `axe.violations[].nodes[]` с адресами |
| `site/page_gates.py --profile P …` | stdout: таблица или `--json` | код-репо; `ready.yaml#after_build` | `--json`: `profile`, `level`, `log`, `verdict`, `B`, `S`, `gates[] {id, device, status, value, threshold, severity, note, source, mirror, excepted?, site_checklist, scope}`, `layers {effects {tool, level, path, B, S, D, na, fails[]}, three_d[] {probe, mode, reduced, B, S, D, blocked}}`, `sources {…: bool}`; код 1 — есть B, 2 — ошибка вызова |
| `site/page_gates.py --resolve P [--site-level L]` | stdout JSON | `project/canvas_input.py`, `project/design_audit.py` | `id`, `level`, `page_type`, `outcome`, `weight`, `all_levels`, `log`; неизвестный профиль — код 2 и сообщение |

Кроме ворот на собранной странице код-репо гоняет `claims_check.py` и `lang_check.py` на собранном HTML, визуальный
аудит `marketing_audit.py` (страница сайта) или `ui_audit.py` (экран); у 3D — ещё `gltf_load_bench.py` и `web_view.py`.

## project — утилиты по артефактам проекта

Утилиты папки `project/` знают раскладку `docs/projects/<slug>/` и читают артефакты проекта: слой страницы, слой
дизайна, файлы уровня продукта, экраны. Движки без знания раскладки — перевод копий холста, кадры, контраст, покрытие по
двум спискам — живут в папках баз; знание о раскладке собрано здесь, чтобы смена формы слоя правилась в одной папке.
Корень данных — ключ `--repo DIR`, переменная `DDD_REPO` или репозиторий скилла (модуль `lib/docpaths.py`, рядом с
`kbpaths`): так репозиторий кода указывает соседний чекаут стратегии. Соседние скиллы шаблона зовут их по пути
`../design-deep-dive/scripts/project/…` — одна копия утилит и одно окружение на все скиллы. Ниже `…` — папка проекта
`docs/projects/<slug>`.

- **Вызов** — `<утилита> <команда> <slug> [<surface>] [--repo DIR] [--stage …] [--out DIR] [--json]`: `build` пишет
  свои производные файлы проекта (с `--out DIR` — вне проекта), `check` ничего не пишет, `show` печатает разбор;
  `--selftest` — самопроверка на встроенной фикстуре, без сети. Без `<surface>` — все поверхности, которые ведёт
  утилита.
- **Вывод `check`** — находки: без `--json` — таблица и строка итога по тяжести (`error` · `warning` · `hint`); с
  `--json` — только строки JSON `{rule, severity, surface, kind, ref, path, message, fix}` (формат —
  `project/findings.py`). `rule` — id правила аудита (`/design-audit`, у экранов — `/screen-audit`), `ref` — запись и
  место в ней, `fix` — что сделать и каким скиллом.
- **Коды выхода:** 0 — ошибок нет (предупреждения и подсказки не мешают); 1 — есть `error` (у `normalize check` — есть
  правки); 2 — ошибка вызова или окружения: нет проекта, поверхности, файла словаря.
- **Что дальше:** `error` держит этап — правка там, куда ведёт `fix`, затем повтор `check`; `warning` и `hint` —
  доклад владельцу. Какие находки останавливают работу, а какие решает заказчик, — `../references/phases.md § Принципы
  всех этапов`.

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `project/findings.py` | module | формат находок утилит раздела: одна копия для утилит и их читателей. | `--validate ФАЙЛ` (строки JSON находок, `-` — stdin); `--selftest`; из Python — `import findings as F` | stdout | stdlib |
| `project/layer.py` | module | чтение файлов проекта для утилит раздела: слой экранов, interface, продукт, карта решений и токены ДС, словарь компонентов. | `<slug> <surface> [--repo DIR] [--json]`; `--selftest`; из Python — `layer.Layer(slug, surface, repo)` | stdout | PyYAML |
| `project/tree.py` | utility | разбор деревьев слоя экранов по грамматике канона и проверки узлов; зовут `/screen-deep-dive`, `/screen-audit`. | `check <slug> [<surface>]` — R-STRUCT-020, -021, R-SEM-014, R-TX-001…006 и соседние; `show <slug> [<surface>]` — разобранные деревья | stdout | PyYAML |
| `project/states.py` | utility | обязательные наборы состояний экрана и блока по правилам канона и проверка ключей `states`; зовут `/screen-deep-dive`, `/screen-audit`. | `check <slug> [<surface>]` — R-STRUCT-022, R-SEM-011, R-SEM-015 (механическая часть); `show <slug> [<surface>]` — набор: ключ, почему, покрыт ли | stdout | PyYAML |
| `project/screen_map.py` | utility | свод `map.md` поверхности кабинета: генерируемые разделы по полям экранов и проверки карты экранов и маршрутов; зовут `/screen-deep-dive`, `/screen-audit`, `canvas_input`. | `build <slug> [<surface>]` — генерируемые разделы; `check <slug> [<surface>]` — R-RT-001…009, R-COV-003, R-STRUCT-006, -023 | `build` — `…/screens/<surface>/map.md` (`--out DIR` — `<DIR>/<surface>/map.md`) | PyYAML |
| `project/normalize.py` | utility | приведение заполненного слоя экранов к канону: механические правки, смысловые поля — пустыми для владельца; зовёт `/screen-deep-dive`. | `check <slug> [<surface>]` — дифф и список владельцу; `build <slug> [<surface>] --write` — правка по месту, `--out DIR` — копия | stdout; с `--write` — файлы слоя экранов | PyYAML |
| `project/demo_data.py` | utility | производный демо-набор поверхности кабинета для входа холста; зовёт `canvas_input`. | `build <slug> <surface> [--seed S] [--anchor ГГГГ-ММ-ДД] [--out DIR]`; `check <slug> [<surface>]` — R-MAT-011 (PRE-14), R-DEBT-002 | stdout; `--out DIR` — `<DIR>/demo-data.json` | PyYAML |
| `project/contract.py` | utility | контракт генерации экранов кабинета для входа холста: десять разделов ux 11/04 §7.3 и раздел на экран; зовёт `canvas_input`. | `build <slug> <surface> [--stage wireframe\|mockup] [--out DIR]`; `check <slug> [<surface>] [--stage …]` — R-MAT-011 (пункты PRE), R-MAT-003, R-COV-005, R-DEBT-002 | stdout; `--out DIR` — `<DIR>/contract.md` | PyYAML |
| `project/ds_build.py` | utility | производные ДС из токенов DTCG и проверка их свежести и формата токенов; этап `design-system`, `/design-audit`. | `build <slug>`; `check <slug>` — R-STRUCT-006 (формат DTCG схемой), R-FRESH-001; `show <slug>` — токены: путь, имя переменной, тип, значения по режимам | `build` — `…/design/system.tokens.css`, передняя часть `…/design/DESIGN.md`, `tokens.json` и `README.md` артефакта ДС | PyYAML, jsonschema |
| `project/ds_coverage.py` | utility | покрытие типов компонентов ДС продукта: экраны и планы → карта решений → артефакт ДС; этапы `ds-components`, `canvas-input`, `/design-audit`. | `check <slug> [<surface>] [--stage ds-components\|mockup]` — R-COV-005; `show <slug> [<surface>]` — таблица покрытия; из Python — `form_errors(kind, data)`: форма бренда, карты решений и брифа на вид по схемам `kb/common/` | stdout | PyYAML, jsonschema |
| `project/ds_sync.py` | utility | правки токенов с claude.ai обратно в DTCG: «имя ДС → путь DTCG» и сверка живого tokens.json артефакта; протокол холста. | `check <slug> --live ФАЙЛ` — R-FRESH-001; `build <slug> --live ФАЙЛ [--write \| --out DIR]` — правки DTCG, без ключа — предложение; `show <slug> [--live ФАЙЛ]` | stdout; с `--write` — `…/design/system.tokens.json` | PyYAML |
| `project/canvas_input.py` | utility | вход холста поверхности: сборка входа под этап, критерии приёмки и проверка входа; этап `canvas-input`, `/design-audit`. | `build <slug> <surface> --stage directions\|wireframe\|mockup\|motion`; `check <slug> [<surface>] [--stage …]` — R-FRESH-002…004, R-MAT-012, R-MAT-003 и находки соседей; `--today ГГГГ-ММ-ДД`, `--schema ФАЙЛ` | `build` — `…/design/<surface>/input/` (`--out DIR` — вне проекта) | PyYAML, jsonschema, referencing |
| `project/ready.py` | utility | манифест готовности поверхности к сборке для репозитория кода и проверка его свежести; этапы `acceptance`, `package`, `/design-audit`. | `build <slug> <surface>`; `check <slug> [<surface>]` — R-FRESH-006; `show <slug> <surface>` — единицы, отпечаток одобрения из `REVIEW.md` и текущий; `--today` | `build` — `…/design/<surface>/ready.yaml` (`--out DIR` — `<DIR>/ready.yaml`) | PyYAML |
| `project/design_audit.py` | utility | структурный прогон правил `/design-audit` по файлам проекта; зовёт валидаторы баз и утилиты раздела. | `check <slug> [<surface>] [--visual-list] [--today …]`; `visual <slug> <surface> --report [ЕДИНИЦА=]ОТЧЁТ.json …` — отчёты `mockup_checks.py page` → R-VIS-001 | stdout (с `--json` — строки находок); `$DDD_HOME/out/project/design_audit/<slug>/`: findings.jsonl, summary.json | PyYAML, jsonschema |

Данные кода: `project/data/screens.yaml` (выводимые колонки свода `map.md`), `project/data/demo.yaml` (нормы
демо-набора с адресом базы).

Прогон на демо-проекте: `python3 tests/fixture_project.py build <фикстура>` печатает корень данных, дальше —
`<утилита> check <slug> --repo <корень>` (фикстуры — § tests).

**Без окружения** (облачная сессия без установленного окружения, отказ утилиты) этап собирает файл по форме или
раскладке, отмечает в нём, что файл собран без утилиты, и проходит ту же проверку чтением
(`../references/phases.md § Как читать`); аудиты — `/design-audit` и соседние — проверяют такой файл чтением по своим
правилам. Первая сессия с окружением пересобирает его утилитой: вход холста с такой пометкой `canvas_input check`
показывает устаревшим (R-FRESH-002), прочие производные — расхождением со сборкой.

## tests — смоук и фикстуры

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `tests/smoke.py` | test | смоук утилит скилла: каждая утилита импортируется и отвечает на `--help` или самопроверку; без сети и браузера. | без ключей — все списки `tests/smoke/`; `--only ПОДСТРОКА` — строки по пути; `--list ФАЙЛ` — один список; `--validate` — проверка списков без запуска (дубль пары «путь + вид проверки» — ошибка); `--uncovered` — утилиты без строки; `--tsv ФАЙЛ` | stdout: PASS · FAIL · XFAIL · XPASS | stdlib |
| `tests/fixture_project.py` | utility | сборщик демо-проекта во временную папку для прогонов и самопроверок утилит `project/`. | `list`; `build ИМЯ [--out DIR] [--json]` — печатает корень данных для `--repo`; `--selftest`; из Python — `with fixture_project.built("ИМЯ") as fx:` | `$DDD_HOME/out/tests/fixtures/<имя>/` | PyYAML |

Списки смоука — `tests/smoke/<папка>.tsv`, колонки `path · kind · smoke · xfail`: строка на утилиту или файл данных,
ожидаемое падение — только с причиной в колонке `xfail`. Фикстуры — `tests/fixtures/<имя>/`: манифест `manifest.yaml`
(`project`, `extends`, слои `kb`, `files`, `replace`, `drop`) и свои файлы с пометкой иллюстрации; список —
`fixture_project.py list`. Основы: `minimal` (лендинг и кабинет, примеры баз), `cabinet` (чистый слой экранов кабинета
`otves-office`), `cabinet-ds`, `cabinet-demo`, `cabinet-texts`, `asset-plan`, `canvas`, `input-landing`, `input-site`,
`input-cabinet`, `package-landing`, `package-cabinet`; с посеянными дефектами — `cabinet-defects`, `cabinet-freeform`
(вольная запись для нормализатора), `cabinet-texts-defects`, `package-landing-defects`, `package-cabinet-defects`,
`package-defects`. Фикстуры с файлами, собранными утилитами, пересобирает `maint/fixture_gen.py`.

## maint — обслуживание базы

| утилита | вид | назначение | вход | выход | зависимости |
|---|---|---|---|---|---|
| `maint/calibrate.py` | maint | Калибровка оценки токенов баз знаний (`kb/<база>/`) под Claude Opus 5.5 через `claude -p` Claude Code (API-ключ не нужен, сессия Claude Code — да). | `[--prose N] [--data N] [--code N] [--seed S]` | `maint/calibration.json` | claude (CLI Claude Code, claude -p) |
| `maint/canon_check.py` | maint | Проверка таблицы «норма → место» `kb/common/canon.tsv` и её сверка с записями `kb/common/CONTRADICTIONS.md`. | `[--canon ФАЙЛ] [--contradictions ФАЙЛ] [--json]`; `--selftest`; коды: 0 — ошибок нет, 1 — есть, 2 — нет файла | stdout | PyYAML |
| `maint/check_links.py` | maint | Проверка перекрёстных ссылок, меток и структуры одной базы знаний `kb/<база>/`. | `--base ИМЯ \| --all` (без них — база рабочей папки, иначе все); `--root`, `--only`, `--out`, `--json`, `--quiet-info`, `--no-raw`; `--selftest` | stdout / `--out` | stdlib |
| `maint/count_tokens.py` | maint | Объём тематического контента баз знаний скилла (`kb/<база>/`): файлы, символы, оценка токенов. | `[--by-folder] [--csv ФАЙЛ]` | stdout / `--csv` | stdlib |
| `maint/fixture_gen.py` | maint | пересборка фикстур `tests/fixtures/`, в которых лежат файлы, собранные утилитами скилла. | `list`; `build ИМЯ… \| --all [--check] [--fixtures DIR]`; `--selftest`; коды: 0 — собрано или совпало, 1 — `--check` нашёл расхождение, 2 — ошибка | файлы фикстур (с `--check` — ничего) | PyYAML |
| `maint/layers.py` | maint | Сколько весят «сжатые слои» баз знаний скилла (`kb/<база>/`) — в токенах по коэффициентам `calibration.json`. | без ключей | stdout | stdlib |
| `maint/mapcheck.py` | maint | Проверка карты знаний по `kb/common/canon.tsv`: адрес карты не должен вести в копию нормы вместо её канона. | `ФАЙЛ… [--canon ФАЙЛ]` (обычно `kb/INDEX.md`); `--selftest`; код 1 — есть адрес «не на норму» | stdout | stdlib |
| `maint/orch_check.py` | maint | Приёмочная проверка файлов базы site (`kb/site/`) по формату базы: разделы, метки, штампы, машинные файлы, ссылки. | `[ПАПКА …] [--selftest-tools]` | stdout | PyYAML |
| `maint/refcheck.py` | maint | Проверка ссылок и forward-only в текстах скилла design-deep-dive (kb/common, kb/INDEX.md, SKILL.md и др.). | `ФАЙЛ… [--strict] [--quiet]` — `--strict`: код 1 и при следах журнала; `--selftest` | stdout | stdlib |
| `maint/sync_check.py` | maint | проверка синхронности скилла одним вызовом: производные против генераторов, копии против канона, описания скиллов в пределах. | `[all \| generators \| copies \| descriptions] [--only ID,…] [--list] [--json]`; `--selftest`; коды: 0 — FAIL нет, 1 — есть FAIL, расхождение копии или описание вне пределов, 2 — ошибка данных | stdout | PyYAML |

Данные кода: `maint/calibration.json`, `maint/data/traces.tsv` (шаблоны следов журнала для `refcheck`, `mapcheck`,
`canon_check`), `maint/data/sync.yaml` (генераторы, копии и описания для `sync_check`; новый генератор или копия —
строка данных), `maint/data/fixtures.yaml` (рецепты `fixture_gen`).

## Данные, которые читает только код

Кроме файлов выше: `ai-media/data/lucide-ref/` (эталонные иконки Lucide, ISC — для `check_icons`),
`ai-media/data/genapi_prices_2026-09-23.json` (прайс Gen-API — `mp_client`), `blender/data/studio_small_09_1k.hdr`
(HDRI по умолчанию `gltf_diff`, CC0) — их кладут правила содержимого.
