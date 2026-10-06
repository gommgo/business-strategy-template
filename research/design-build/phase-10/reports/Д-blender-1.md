# Д-blender-1 — машинные файлы базы blender: `09-web-runtime`, `12-recipes/examples`, `13-tools-atlas`

Коммит начала — `1e0cd2a`. Список зоны — 64 файла, тронуто 58 (205 строк заменены по месту, число строк файлов прежнее).
Маркеры зоны: 274 → 69; целевые `machine`, `research` — 0; остаток — ложные срабатывания, обозначения вариантов,
ссылки на существующие файлы витрины и одна строка исполняемого кода. Данные, числа, ключи и логика кода не менялись.
Git — только чтение. Пути ниже — от `.claude/skills/design-deep-dive/kb/blender/`, утилиты — от корня скилла.

## Файлы

Маркеры — сумма по классам `kbscan.py` с классами `--extra`; «→» — до и после.

| файл | что сделано | маркеры |
|---|---|---|
| `09-web-runtime/examples/camera-path-scroll/build_scene.py` | строка запуска: `99-raw/tools/…` и путь опыта → `scripts/blender/blender_run.py kb/blender/09-web-runtime/examples/camera-path-scroll/build_scene.py` | 1 → 0 |
| `09-web-runtime/examples/camera-path-scroll/index.html` | «см. `99-raw/experiments/F2/06-anim-damp`» → «см. blender 09/03 §6» | 1 → 0 |
| `09-web-runtime/examples/hero-lazy/hero.js` | шапка: «(эталон F1, собран из `99-raw/…`)» → «(эталон)» | 1 → 0 |
| `09-web-runtime/examples/hero-lazy/index.html` | `<title>`: «hero-lazy (F1)» → «hero-lazy» | 1 → 0 |
| `09-web-runtime/examples/r3f-hero/build.sh` | комментарий: «песочница `~/.cache/blender-research/npm-F2`» → «песочница npm — `$DDD_HOME/node`» | 2 → 0 |
| `09-web-runtime/examples/r3f-hero/src/Hero.jsx` | шапка без «(эксперимент F2/02-r3f-hero)» | 1 → 0 |
| `09-web-runtime/page-3d-gates.yaml` | не тронут: «(D)» — шкала серьёзности B/S/D | 2 → 2 |
| `12-recipes/examples/{01,02,03,04,05,06,07,08,09,10,12}-*/build.py` (11) | шапка «Сгенерировано K/01 из …» → «Сгенерировано run_recipes.py из …» — строка, которую пишет генератор; id опытов в комментариях блоков → короткий адрес базы: 01 `(D1/03)` → `(blender 05/04 §1)`; 02 → `формы — blender 05/04 §3, паспорт — blender 06/02 §6`; 03 → `телефон (blender 05/04 §2)`; 04 → `(blender 05/04 §5)`; 05 → `слоты — blender 07/03 §1.2`; 07 → `(blender 05/04 §6: …)` | 28 → 11 |
| `12-recipes/examples/{02-icon-series,08-sequence-video-alpha}/post.py` (2) | та же шапка; 08: «команды A/06 (encode.py)» → «команды кодирования (blender 06/04 §2–3)» | 3 → 0 |
| `12-recipes/examples/01-hero-product/index.html` | «эталон hero-lazy (F1)» → «эталон hero-lazy (09-web-runtime/examples/hero-lazy)» | 2 → 1 |
| `12-recipes/examples/05-scroll-showcase/index.html` | `<title>` без «(страница H/21)»; комментарий: «страница H/21» → «страница скраба по прокрутке (blender 07/03 §3.3)» | 2 → 0 |
| `12-recipes/examples/09-glass-product/index.html`, `index_css.html` | комментарий «(F2)» → «(blender 09/04 §3)» | 2 → 0 |
| `12-recipes/examples/12-model-viewer-ar/index.html` | метка: `[проверено: 99-raw/experiments/K/09-mv-page — загрузка и рендер в Chromium; …]` → `[проверено: загрузка и рендер в Chromium; AR на устройствах не проверен]` | 1 → 0 |
| `12-recipes/examples/*/web/*/web_stats.json` (12: `icon_bell`, `icon_chat`, `icon_folder`, `phone`, `phone_phone`, `sculpture_ink_34`, `sculpture_pearl_23`, `case_reveal`, `logo`, `island`, `glass`, `field`) | `model`, 4 × `views[].file`, `sheet`: путь машины → путь от папки примера (`icon_bell.glb`, `web/icon_bell/web_view_0_az35_el20.png`) | 156 → 12 |
| `12-recipes/examples/01-hero-product/web/case/web_stats.json` | не тронут: пути уже без машины | 1 → 1 |
| `12-recipes/examples/08-sequence-video-alpha/numbers.json` | `passport.glb`: путь машины → `../04-abstract-sculpture/sculpture_ink_34_raw.glb` | 2 → 0 |
| `12-recipes/examples/01-hero-product/dist/*.js` (2) | не тронуты: собранные бандлы | 2 → 2 |
| `12-recipes/examples/13-wow-light-hero/src/{kbb,kbm,kbp,kbr,zkin,zmat,zmetrics,zpass,zrender,zstudio}.py` (10) | докстринг без «дорожка KB», «Дорожка Z», «дорожки Z»; `kbp.py` — без «(дорожка KB, 15-showcase)» | 18 → 7 |
| `12-recipes/examples/13-wow-light-hero/src/brender.py` | докстринг: «, фаза 2 (v2, дорожка KB2)» → «(v2)» | 3 → 3 |
| `12-recipes/examples/14-product-in-code/src/build.sh` | комментарии без штампа «CD3:» (2 строки) | 4 → 4 |
| `12-recipes/examples/14-product-in-code/src/model_a.js` | комментарии без штампа «KB3:» (2 строки) и без «Фаза 2:» в шапке — как в копиях витрины | 8 → 8 |
| `12-recipes/examples/15-hybrid-blender-code/src/model_c.js` | комментарии без штампа «KB3:» (2 строки) | 1 → 1 |
| `12-recipes/examples/15-hybrid-blender-code/src/zgeo.py` | докстринг без «Дорожка Z» | 2 → 1 |
| `12-recipes/examples/15-hybrid-blender-code/src/zweb_all.py` | докстринг: «крюка CD2», «дорожка Z2» сняты; комментарий без «Z3:» | 1 → 1 |
| `12-recipes/examples/15-hybrid-blender-code/src/zbuild.py` | не тронут: ложные срабатывания | 4 → 4 |
| `12-recipes/examples/16-relight-by-passes/src/fonarik.js` | шапка без штампа «(SD3)» (2 места) | 3 → 3 |
| `12-recipes/examples/16-relight-by-passes/src/sdano_lib.py` | докстринг: «дорожка SD (15-showcase «Сдано»)» → «сцена «Сдано» (15-showcase/sdano)» | 5 → 4 |
| `12-recipes/examples/16-relight-by-passes/src/sdano_v2.py` | докстринг: «фаза 2 дорожки SD: сцена B/C поверх sdano_lib (фаза 1 не меняется)» → «сцена B/C «Сдано» поверх sdano_lib (sdano_lib не меняется)» | 1 → 0 |
| `12-recipes/examples/16-relight-by-passes/src/run_v2.py` | докстринг без «фаза 2:»; маркеры — «(C)» — вариант и код | 2 → 2 |
| `12-recipes/examples/16-relight-by-passes/src/passes_convert.py` | не тронут: «(C)» — вариант | 1 → 1 |
| `13-tools-atlas/atlas.tsv` | 27 замен в 73 строках, 157 строк × 16 колонок: метки `[проверено: K]`, `[проверено: O]` → `[проверено]`; сняты `[K §4]` (2), `(I §4)`, `[V:wave2]`, «(O)» у адреса `04-ai-agents-mcp/06-07` (2), «автор O, волна 3», «автор H, перенесено …» (2), «этой волной» (3), «как считала волна 1», «для волны 4»; «рекомендация C1» → «рекомендация базы»; «для O» → «для супервизора фонового Blender»; «воротам K и J» → «воротам базы»; «упомянут V» → «упомянут в ролике»; «§1.1 G/03» → «10-ai-3d-generation-assets/03 §1.1»; «(A/03, …)», «(K §4, …)» — без буквы; «из реестров A/C2/F2» → «из сохранённых реестров»; «фоновых экспериментов» → «фоновых запусков» (строка 141), «источник чисел «N из N» в отчётах» — без «в отчётах» (строка 152); колонка `source`: `cache:C2-repos.json` → `cache:repos` (21), `cache:A/F2-registry` → `cache:registry` (33); правка зоны кода К14 в строке 151 (коды выхода `qa_pipeline.py`) | 13 → 1 |

Итог по классам: `machine` 74 → 0; `research` 74 → 0; `raw` 5 → 1; `process` 44 → 2; `showcase` 9 → 8; `letters` 67 → 57;
`words` 1 → 1; сумма 274 → 69.

## Остаток маркеров

- `raw` (1): `12-recipes/examples/03-device-mockup/build.py:15` — исполняемый код читает `99-raw` (раздел ниже).
- `process` (2), ложные: `13-wow-light-hero/src/kbm.py:6` — формула «L/100»; `14-product-in-code/src/build.sh:9` —
  переменная пути `$R/15-showcase`.
- `showcase` (8): `13-wow-light-hero/src/kbp.py:3`; `14-product-in-code/src/build.sh:2, 5, 9`;
  `15-hybrid-blender-code/src/zweb_all.py:2`; `16-relight-by-passes/src/fonarik.js:1`; `…/sdano_lib.py:1, 5` — ссылки ведут в
  существующие файлы `15-showcase/` (`keyboard/passport.json`, `_shared/code3d/`, `sdano/art-direction.md`); строка
  `build.sh:9` — исполняемая. Судьбу ссылок решает решение о витрине.
- `letters` (57):
  - `09-web-runtime/page-3d-gates.yaml:9, 10` — «(D)» — серьёзность шкалы B/S/D;
  - `build(P)` — имя и вызов функции (15): `01-hero-product/build.py:26, 47`; `04-abstract-sculpture/build.py:18, 44`;
    `05-scroll-showcase/build.py:24, 63`; `07-lowpoly-diorama/build.py:69, 96`; `09-glass-product/build.py:16, 49`;
    `01-hero-product/index.html:42`; `13-wow-light-hero/src/kbb.py:1`; `15-hybrid-blender-code/src/zbuild.py:452, 527`;
    `16-relight-by-passes/src/sdano_lib.py:1`;
  - аргументы и имена в коде (19): `13-…/brender.py:91, 121, 131`; `kbb.py:178, 199`; `zrender.py:228`;
    `14-…/model_a.js:69, 92, 200, 232, 255, 307`; `15-…/zbuild.py:166, 342`; `zgeo.py:45`; `16-…/fonarik.js:56, 220`;
    `run_v2.py:42`; `sdano_lib.py:623`;
  - обозначение варианта A, B, C — код, предрендер Blender, гибрид (6): `13-…/kbp.py:1`; `14-…/model_a.js:294, 365`;
    `15-…/model_c.js:23`; `16-…/passes_convert.py:1`; `run_v2.py:55`;
  - «(R)» в названии видеокарты, поле `info.gpu` (13): строка 18 каждого `web_stats.json`;
  - минифицированный код (2): `01-hero-product/dist/hero.js:1`, `dist/RoomEnvironment-F4HHI32D.js:1`.
- `words` (1): `13-tools-atlas/atlas.tsv:54` — «субагент-критик» — устройство описываемого инструмента.

Вне классов сканера, не тронуто:
- «фаза 1», «фаза 2», «итерация 2» в комментариях к значениям — название версии сцены, по которой значение выбрано:
  `13-…/zstudio.py:19, 331, 332, 380`; `zpass.py:51`; `zmat.py:91`; `kbp.py:100`; `15-…/zbuild.py:259, 339`;
  `16-…/sdano_v2.py:36`; `sdano_lib.py:449`. В шапках-описаниях файлов слово снято;
- «KIT §4», «KIT §4.4» в `13-…/kbr.py:3`, `zstudio.py:3` — ссылка на существующий `15-showcase/KIT.md`;
- `[V:<id> mm:ss]` в `atlas.tsv` (строки 11, 78, 79, 98) — ссылка на ролик по `kb/common/evidence.md`;
- `atlas.tsv`: условия замера в `notes` («на машине без CUDA», «версия системная 7.1», «на этой машине») и колонка
  `collected` — данные.

## Ключи и значения, которые читает код

- **Читает `99-raw`:** `12-recipes/examples/03-device-mockup/build.py:15` —
  `screenshot=f"{rk.ROOT}/99-raw/experiments/K/02-hero-page/mobile/shot_mobile_thr_quick_0.png"`: текстура экрана
  телефона; файла нет ни в папке примера, ни под `99-raw`. Строка не тронута; та же строка — в блоке
  `12-recipes/03-device-mockup.md:46`.
- **Шапка `build.py` и `post.py`** — текст `scripts/blender/run_recipes.py:109, 118`; после правки шапки 13 файлов
  совпадают со строкой генератора.
- **Первая строка блока рецепта** — `run_recipes.py` ищет в ней `[не проверено]`, `[не исполняется]`, `# run: system`;
  эти слова на месте.
- **`web_stats.json`:** `run_recipes.py:147–155` читает `info`, `frame_time`, `console` — не тронуты. Поля `model`,
  `views[].file`, `sheet` код не читает, но пишет: `scripts/blender/web_view.py:276, 298, 313` кладут путь так, как он
  пришёл в вызове, а `run_recipes.py` зовёт с полным путём — новый прогон рецепта вернёт путь машины.
- **`numbers.json`:** файл пишет `scripts/blender/rk.py:392–398`; `passport.glb` — значение паспорта рецепта 08
  (`build.py:10`, `f"{rk.ROOT}/…"`), код его из файла не читает; новый прогон вернёт полный путь.
- **`09-web-runtime/page-3d-gates.yaml`** — пороги `scripts/blender/gate_check.py`; не тронут.
- **`atlas.tsv`** — читателей в `scripts/` нет. Значения колонки `source` изменены: `cache:repos`, `cache:registry`.
- **`14-product-in-code/src/build.sh:9, 16–25`** — зовёт `15-showcase/_shared/code3d/build.sh`; снятие витрины ломает
  команду `./build.sh kb`.

## Производные

`build.py` и `post.py` рецептов 01–12 собирает `run_recipes.py` из блоков `12-recipes/<рецепт>.md`: новый прогон
запишет в пример строки md. Правки комментариев в блоках — те же строки md (раздел «Для текстов», п. 1). Собранные
бандлы `01-hero-product/dist/` не правились.

## Для фикстур

Нет: `fixture_gen.py build --all --check` — совпадает.

## Для текстов

Пути — от `kb/blender/`.

1. Блоки кода рецептов — строки, с которых собраны `build.py`, `post.py` и страницы примеров:
   - `12-recipes/01-hero-product.md:50` — «(D1/03)» → «(blender 05/04 §1)»;
   - `12-recipes/02-icon-series.md:36` — «(формы D1/04, паспорт D2/04)» → «(формы — blender 05/04 §3, паспорт — blender 06/02 §6)»;
   - `12-recipes/03-device-mockup.md:35` — «телефон D1/02 + скриншот» → «телефон (blender 05/04 §2) + скриншот»;
     `:46` — путь скриншота в `99-raw` (файла нет);
   - `12-recipes/04-abstract-sculpture.md:37` — «(D1/06)» → «(blender 05/04 §5)»;
   - `12-recipes/05-scroll-showcase.md:40` — «(слоты, H/12)» → «(слоты — blender 07/03 §1.2)»;
   - `12-recipes/07-lowpoly-diorama.md:39` — «остров D1/07 (палитра, GN-инстансы)» → «остров (blender 05/04 §6: палитра, GN-инстансы)»;
   - `12-recipes/08-sequence-video-alpha.md:77` — «команды A/06 (encode.py)» → «команды кодирования (blender 06/04 §2–3)»;
   - `12-recipes/09-glass-product.md:114` — «(F2)» → «(blender 09/04 §3)»;
   - `12-recipes/12-model-viewer-ar.md:107` — метка без пути `99-raw/experiments/K/09-mv-page`.
2. `09-web-runtime/02-r3f-drei-and-other-engines.md:402` — «`~/.cache/blender-research/npm-F2`» → `$DDD_HOME/node`.
3. `11-evaluation-qa/03-export-and-page-gates.md:193` — «hero-lazy (F1)»: заголовок страницы примера — «Камера 1954 — hero-lazy».
4. Атлас: `13-tools-atlas/README.md:4, 18, 32–33`; `01-blender-addons-extensions.md:25, 110`;
   `03-pipeline-cli-services.md:4, 27`; `README.md:845, 1010–1011` — «пересобирается `atlas_collect.py`», «реестры
   A/C2/F2», `extract_sections.py`: этих утилит в `scripts/blender/` нет. Значения `source` в таблице — `manual`,
   `live:<площадка>`, `cache:repos`, `cache:registry`.
5. `13-tools-atlas/03-pipeline-cli-services.md:16` — «[I §4]»: в парной строке `atlas.tsv:62` буква и раздел сняты,
   адрес — колонка `where_in_base` (`08-export-gltf/03 §1.2, §4`).

## Файлы к снятию

Нет.

## Вопросы

1. `13-tools-atlas/atlas.tsv:155` (`extract_sections.py`) и `:157` (`atlas_collect.py`) описывают утилиты, которых нет в
   `scripts/blender/`; `where_in_base` обеих строк — `../../scripts/blender/README.md`. Снять строки или оставить: счёт
   «156 записей» стоит в `13-tools-atlas/README.md:14` и `README.md:845`.
2. `12-recipes/examples/01-hero-product/web/case/web_stats.json`: `file` и `sheet` — имена от папки `web/case/`; в
   остальных 12 файлах теперь путь от папки примера (`web/<имя>/…`), как в задании. Выровнять 01 под них?
3. Имена `cache:repos` и `cache:registry` в колонке `source` атласа — подтвердить.
4. «Фаза 1 / фаза 2» в комментариях к значениям исходников рецептов 13–16 оставлены как имена версий сцены (11 строк,
   раздел «Остаток»); в шапках-описаниях слово снято — так же сделано в копиях витрины соседней зоной. Снимать ли
   слово и в комментариях: замена требует назвать версию сцены по-другому.
5. Рецепт 03 читает скриншот из `99-raw`, которого нет: положить картинку в папку примера или заменить источник
   текстуры — зона кода и текстов рецепта.

## Проверки

- Разбор: 30 файлов `.py` компилируются (без `__pycache__` в дереве), 13 файлов `.json` читаются, `build.sh` × 2 —
  `sh -n` и `bash -n`; `atlas.tsv` — 157 строк по 16 колонок.
- `run_recipes.py --selftest`, `run_doc_blocks.py --selftest`, `gate_check.py --selftest`,
  `qa_pipeline.py --selftest` — OK. `web_view.py` и `site_probe.py` не запускались: их самопроверка открывает браузер.
- `scripts/tests/smoke.py --only kb` — PASS 42, FAIL 0.
- `scripts/maint/sync_check.py` — генераторы OK 17, FAIL 0, находок 0. `fixture_gen.py build --all --check` — совпадает.
- `scripts/maint/accept.py --base 1e0cd2a --masks-file …/Д-blender-1.masks`: под масками 58 файлов — ссылки 0, разбор 13
  файлов 0 находок, код 30 файлов 0, следы 30 файлов 0. Код выхода 1 — из-за 220 файлов соседних зон вне масок; в
  папках зоны чужих правок нет.
