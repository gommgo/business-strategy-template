# Т-код-blender — строки зон кода в статьях базы `blender`

Зона: статьи `kb/blender/**/*.md` и названный машинный файл `13-tools-atlas/atlas.tsv`. Коммит начала `1e0cd2a` (ветка
`main`). Работа 03.10 оборвалась на лимите модели после правок и проверок; 06.10 дерево сверено с файлом передачи (список
изменённых md тот же, после передачи файлов базы никто не менял), самопроверки и смоук повторены, отчёт записан.
Источники строк: `text-zones-v2/_code-blender.md` (К1б), «Для текстов» отчётов К14, Д-blender-1, К12 (обход `flock`, путь
машины — только `kb/blender/**`), Д-blender-2, дополнение координатора об атласе. Пути ниже — от `kb/blender/`, утилиты —
от корня скилла `.claude/skills/design-deep-dive/`.

## Файлы

47 md и `atlas.tsv`. Глава `12-recipes`: `README.md`, `00-how-to-use.md`, рецепты `01`–`10`, `12`–`17` (16 файлов).
Глава `05-modeling` — 01–05; `06-materials-lighting-render` — 01–04; `11-evaluation-qa` — 01, 02, 03, 04, 06;
`13-tools-atlas` — `README.md`, 01, 03; `03-bpy-api/01`, `03-bpy-api/snippets/README.md`, `04-ai-agents-mcp/01`, `08-export-gltf/03`,
`08-export-gltf/04`, `09-web-runtime/02`, `09-web-runtime/06`, `09-web-runtime/examples/hero-lazy/README.md`, `10-ai-3d-generation-assets/02`,
`00-glossary/README.md`, корневые `README.md` и `PLAN.md`. Диф по 47 md: +164 −174 строки. `atlas.tsv`: мои — две снятые
строки данных (остальной диф файла — зона данных). Файлы `15-showcase/**`, `99-raw/**`, `scripts/` и чужие базы не правились.

Рабочие файлы зоны: `~/.cache/design-deep-dive/out/f10/Т-код-blender/` — `HANDOFF.md`; `apply.py` (точные замены со счётом
вхождений) и списки замен `e01`–`e07`; `recipe_diff.py` (сборка `build.py` и `post.py` из блоков md, как это делает
`run_recipes.py`, и побайтная сверка с `examples/`); выводы проверок.

## Строки: источник → место → итог

Итого: **внесено 156 мест**, **уже так — 5**, **по коду иначе — 4**, **не внесено — 30 мест и группа меток К14 п. 5** (причины —
в таблице).

| источник (отчёт, пункт) | файл и место | итог |
|---|---|---|
| К1б, TR-57 | `12-recipes/00-how-to-use.md`, таблица рецептов | уже так: `scripts/site/vocab_lint.py` — 0 ошибок, 0 предупреждений (тегов `slot:`/`block:` в файле нет, проверено id — 0) |
| К14 п. 1 | `00-glossary/README.md:156` | внесено |
| К14 п. 1 | `11-evaluation-qa/01-scene-geometry-checks.md:53` | внесено |
| К14 п. 1 | `README.md:61` | внесено |
| К14 п. 1 | `13-tools-atlas/atlas.tsv:151` | уже так (строку внесла зона данных) |
| К14 п. 1 | `references/phases.md:926–927` | уже так: строка сама говорит «без правки» |
| К14 п. 1, сверх строк — по коду | `11/01:64` (`\|\| [ $? -le 2 ]` и комментарий «1–2 — вердикт, 3 — сбой»), `11/03:7` (код выхода 2/1/0), `11/03:57`, `11/03:184` (`\|\| [ $? -le 2 ]`) | внесено — 4 места: без `--strict` код 0 при выполненном замере, обёртка `\|\| [ $? -le 2 ]` больше ничего не ловит; `11/03:7` — по смыслу строки `11/01:53` |
| К14 п. 2, таблица «построчно», решение «копия» (22) | рецепты 13 (6), 14 (3), 15 (4), 16 (5), 17 (4) | внесено — 22 |
| К14 п. 2, «папка» | `14:5`, `15:6`, `16:6–7`, `17:5`, `17:243` | внесено — 5 |
| К14 п. 2, «папка», новая ссылка «снять» | `14:280` | не внесено: ссылка на журнал дорожки — уборка следов |
| К14 п. 2, образец пути и файл, который пишет утилита | `13:6`, `14:175` | внесено — 2 |
| К14 п. 2, решение «ссылку снять» (15) | `13:77, 201, 273, 338`; `14:3, 68, 110, 281`; `15:334, 335` (журналы `HANDOFF-2.md`); `16:4` (2), `16:79`, `16:357` | не внесено: метки и ссылки без цели — уборка следов (задание) |
| К14 п. 2, сверх таблицы | `14:179` (хвост → `$DDD_HOME/out/blender/recipes/14-product-in-code/kb.json`), `15:6`, `15:229` (хвост «ворота KB …» снят), `17:5`, `13:203`, `13:206` | внесено — 6 |
| К14 п. 2, сверх таблицы | `13:274` (`slot_run.py`, `blender_run.py` → `../../scripts/blender/…`) | внесено |
| К14 п. 2, сверх таблицы | `15:131` | по коду иначе: см. «Расхождения», п. 3 |
| К14 п. 3 | `12-recipes/README.md:6`, `:11`; `00-how-to-use.md:5` | внесено — 3 |
| К14 п. 3 | `12-recipes/README.md:9` | по коду иначе: см. «Расхождения», п. 2 |
| К14 п. 3, сверх — по коду | `12-recipes/README.md:10` («системным Python 3» → «Python окружения скилла»), `:97–98` (примеры — `examples/<рецепт>/src/`); `00-how-to-use.md:6` (путь прогонщика), `:147` (то же о `# run: system`), `:148` (итог — `$DDD_HOME/out/blender/run_recipes/result.json`), `:150` (`sys.path` на `scripts/blender`, не на `_kit`) | внесено — 6 |
| К14 п. 4 | `05-modeling/01…05`, 19 строк `sys.path` на `D1/_lib` | внесено: `sys.path.insert(0, "../../scripts/blender")` |
| К14 п. 4 | `12-recipes/05-scroll-showcase.md:43` | по коду иначе: см. «Расхождения», п. 1 |
| К14 п. 4, путь `…/03-bpy-api/snippets` | `05-modeling/03` (2), `06/01` (2), `06/02` (4), `06/03` (2), `06/04` (3), `03-bpy-api/01:125`, `03-bpy-api/snippets/README.md:26, 41, 108` | внесено — 17 (у К14 счёт 14 — без трёх присваиваний `p = …`/`SNIPPETS = …`) |
| К14 п. 4, путь `…/12-recipes/examples/_kit` | рецепты 01–10, 12 — 11 строк | внесено строкой `examples/<slug>/build.py` (условие К14 п. 4: строка md совпадает со строкой `build.py`); см. «Расхождения», п. 1 |
| К14 п. 5 | метки `[проверено: 99-raw/experiments/…]` и ссылки без цели, глава `14-code-3d` | не внесено: вне задания — уборка следов; ссылки на файлы, переехавшие в `examples/<рецепт>/src/`, переведены (строки К14 п. 2 и п. 7) |
| К14 п. 6 | `17-khr-materials-variants.md:121` | по коду иначе: см. «Расхождения», п. 4 |
| К14 п. 6 | `17:122`, `17:126`, фраза перед блоком | внесено — 3; имена моделей во фразе — в «», путь `export_web.py` — полный `examples/17-khr-materials-variants/src/export_web.py` (см. «Расхождения», п. 5) |
| К14 п. 6 | `12-recipes/README.md:12`, `:96` — «3 из 3» блоков `# run: system` → «2 из 2» | внесено — 2; `run_doc_blocks.py --dry-run` по 13–17: `system 2` |
| К14 п. 7 | `15:334` (`zweb_all.py` → `examples/15-hybrid-blender-code/src/zweb_all.py`, `zbuild.py`); `13:164` (модуль `kbr` в блоке — комментарий с путём `kbr.py`); `17:193` (`kbp.COLORWAYS` — путь `kbp.py`) | внесено — 3 |
| К14 п. 7 | модули `zkin`, `zmat`, `zpass`, `kbb`, `sdano_lib`, `sdano_v2` | уже так: текст рецептов 13, 16, 17 их не называет |
| Д-blender-1 п. 1 | `01:50`, `02:36`, `03:35`, `04:37`, `05:40`, `07:39`, `08:77`, `09:114`, `12:107` | внесено — 9; блоки md совпадают с `build.py` и `post.py` побайтно (`recipe_diff.py`: 0 строк расхождения) |
| Д-blender-1 п. 1 | `03-device-mockup.md:46` — путь скриншота в `99-raw` | не внесено: файла нет, замены нет ни в строке, ни в коде (вопрос 5 Д-blender-1 открыт) |
| Д-blender-1 п. 2 | `09-web-runtime/02-r3f-drei-and-other-engines.md:402` | внесено: `$DDD_HOME/node` |
| Д-blender-1 п. 3 | `11-evaluation-qa/03-export-and-page-gates.md:193` | внесено: «hero-lazy» без буквы, как заголовок страницы примера |
| Д-blender-1 п. 4 и дополнение координатора | `13-tools-atlas/README.md:4–5` (вступление — о колонке `source`: `manual`, `live:<площадка>`, `cache:repos`, `cache:registry`; день — колонка `collected`), `:18–19` (п. 1 без скрипта), `:32–33` (п. 8 снят, пункты 9–10 стали 8–9); `01-blender-addons-extensions.md:25`, `:110`; `03-pipeline-cli-services.md:4`, `:27`; `README.md:1010–1011`; `00-glossary/README.md:136` | внесено — 9 |
| Д-blender-1 п. 5 | `13-tools-atlas/03-pipeline-cli-services.md:16` — «[I §4]» | внесено: «→ §1 (`../08-export-gltf/03-compression-textures-budgets.md §1.2, §4`)», адрес — колонка `where_in_base` строки атласа |
| дополнение координатора | `13-tools-atlas/atlas.tsv` — строки `extract_sections.py` и `atlas_collect.py` (`base-utility`) | внесено: 155 строк файла, 154 записи, 16 колонок у всех, имена уникальны; порядок и поля остальных строк не тронуты |
| дополнение координатора | счёт «156»: `13-tools-atlas/README.md:14`, `README.md:845` | внесено: 154 записи; в `README.md:845` и число строк файла 157 → 155 |
| дополнение координатора | норма обновления атласа | не внесено: способа обновить атлас в скилле нет (утилиты нет в `scripts/`) |
| дополнение координатора | `PLAN.md:532, 607, 625, 820`; `11-evaluation-qa/05-master-checklist.md:201` — обе утилиты | не внесено: журнал базы и метка сборки чек-листа, не статьи атласа — уборка следов |
| К12, `flock` | `kb/blender/**/*.md` | уже так: обёрток `flock … browser.lock` в статьях нет |
| К12, путь машины в прозе | `04-ai-agents-mcp/01-mcp-for-blender.md:144` (`"command": "uvx"`), `PLAN.md:52` (`blender` из PATH) | внесено — 2 |
| К12, путь машины в командах и блоках | `03-bpy-api/snippets/README.md:140` (`cd` снят); `05-modeling/05:306` (`../../scripts/blender/preflight_block.py`); `06/02:148` (`../../scripts/blender/data/studio_small_09_1k.hdr`); `06/03:381` (путь от корня базы); `08/03:356–357`, `08/04:58`, `08/04:592–593`, `09/06:348–349`, `10/02:296–297` (`BASE=$DDD_HOME`, без `~/.nvm` в PATH, `cd` снят); `09-web-runtime/examples/hero-lazy/README.md:17` (`NODE_PATH=$DDD_HOME/node/node_modules`); `11/01:61, 93, 238`; `11/02:92`; `11/03:55, 114, 166, 168, 183`; `11/04:88`; `11/06:198` (`R=.`); `14:4` (`$DDD_HOME/node`), `14:176` (`R=.`) | внесено — 23 |
| К12, путь машины | `14-code-3d/README.md:5`, `:100` | не внесено: глава `14-code-3d` вне задания |
| Д-blender-2 «Для текстов» | 5 пунктов: md витрины со следами, `_shared/code3d/README.md`, `keyboard/README.md:59, 90, 132`, `zveno/art-direction.md:119–159` и `judge/`, копии в базе creative | не внесено: все о файлах `15-showcase/**` (и копиях в creative) — задание запрещает править витрину |

## Расхождения строк с кодом

1. **Строка пути в рецептах 01–12** (К14 п. 4). Строка даёт `sys.path.insert(0, "../../scripts/blender")`, но тем же пунктом
   требует совпадения строки md со строкой `examples/<slug>/build.py`. В `build.py` зона данных записала
   `import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", "scripts", "blender"))  # перенос: rk.py — scripts/blender`;
   внесено это. У рецепта 05 две строки пути (`_kit` и `H/_lib`) в `build.py` слиты в одну («rk.py и animx.py»). Следствие:
   блок с `__file__` исполняет только `run_recipes.py` (он пишет `build.py`); у `run_doc_blocks.py` пространство имён блока
   Blender без `__file__`. В главах 05, 06, 03 строки — `"../../scripts/blender"` (их исполняет `run_doc_blocks.py`, рабочая
   папка — корень базы).
2. **Путь прогонщика в прозе** (К14 п. 3, `12-recipes/README.md:9`). Строка — `../../scripts/blender/run_recipes.py`;
   `refcheck.py` разрешает путь в обратных кавычках от папки файла, и эта форма битая. Внесено `../../../scripts/blender/run_recipes.py`
   (как у `rk.py` в том же файле); в `00-how-to-use.md:6` та же правка. По той же причине пути исходников в прозе рецептов
   13–17 — от папки рецептов (`examples/<рецепт>/src/…`), а в метках и командах блоков кода — от корня базы
   (`12-recipes/examples/<рецепт>/src/…`): блоки исполняются с рабочей папкой `kb/blender`.
3. **`15-hybrid-blender-code.md:131`** (К14 п. 2: `T=…/99-raw/tools` → `../../scripts/blender/…`). Блок берёт из `T` бинарники
   KTX и gltfpack (`$T/bin/…`) и `node_modules` (`cd $T/node`, `node $T/node/validate.mjs`); они живут в окружении скилла:
   `$DDD_HOME/bin/KTX-Software-4.4.2-Linux-x86_64/`, `$DDD_HOME/bin/gltfpack-1.2/`, `$DDD_HOME/node/` (`kbpaths.py`: `bin_dir`,
   `node_home`). Внесено `T=$DDD_HOME`, `~/.nvm/…` из PATH снят (node — из PATH). Так же — блоки `08/03`, `08/04 §7.3`, `09/06 §3.3`,
   `10/02 §5.1`.
4. **`17-khr-materials-variants.md:121`** (К14 п. 6: `# run: skip — блоку нужны …`). `run_doc_blocks.py` пропускает блок по
   «# run: skip» в первых двух строках, а `run_recipes.py` — только по «[не проверено]» или «[не исполняется]» в первой
   строке: с текстом строки `run_recipes.py` исполнил бы блок в Blender. Внесено
   `# run: skip [не исполняется] — блоку нужны три модели проекта: сырой экспорт и две после постобработки` — пропуск у обеих
   утилит (как у остальных отрывков 13–17: `[не исполняется] # run: skip`). Проверено: `run_doc_blocks.py --dry-run` — `skip`,
   разбор `run_recipes.blocks()` — `skip`.
5. **Фраза перед блоком рецепта 17** (К14 п. 6). Имена моделей (`kb_web_raw.glb`, `kb_desk.glb`, `kb_mob.glb`) в обратных
   кавычках `refcheck.py` считает битыми путями (файлов в базе нет — о том и фраза); внесены в «». `export_web.py` — полным
   путём `examples/17-khr-materials-variants/src/export_web.py`.
6. **`06-materials-lighting-render/03-render-engines-color.md:381`**. Путь машины снят (блок исполняется от корня базы:
   `99-raw/experiments/D2/01-brand-color`), но папки `D2` в дереве нет, модуля `palette` (`de2000`, `srgb2lab`, `hex2srgb`) нет
   и в `scripts/blender/` — блок «белая печь» не исполнится. Нужна правка кода или блока — в «Соседям».

## Соседям и в общие файлы

- **Код (`scripts/blender/`).** (1) Метки пропуска у прогонщиков разные: `run_recipes.py` — «[не проверено]» или
  «[не исполняется]» в первой строке; `run_doc_blocks.py` — «[не проверено]» или «# run: skip» в первых двух строках. Свести к
  одной паре или признавать обе. (2) `run_doc_blocks.py` не даёт блоку `__file__`: блоки рецептов 01–12 исполняются только
  через `run_recipes.py`; либо задать `__file__` в RUNNER, либо писать в `build.py` строку пути от рабочей папки. (3) Модуль
  `palette` для блока «белая печь» (`06-materials-lighting-render/03-render-engines-color.md §5`, строка 381) — перенести в
  `scripts/blender/` или перевести блок на `img_metrics.de2000`.
  (4) `11-evaluation-qa/04-regression-set.md §2` и `regression/README.md` зовут `regression/run_set.py`, `make_manifest.py`,
  `manifest.json` — в дереве их нет (в папке только README). (5) Пути сырья `99-raw/…` в докстрингах и комментариях — 18 файлов
  `scripts/blender/` (`rk.py:5–8`, `d1lib.py:3`, `d2lib.py:2`, `presets.py:50`, `preflight_block.py:1` и др.).
- **Уборка следов (тексты).** 15 ссылок «снять» рецептов 13–17 и `14:280`; метки К14 п. 5; глава `14-code-3d` (в том числе
  пути машины `14-code-3d/README.md:5, :100`); `PLAN.md:532, 607, 625, 820` и `11/05:201` — утилиты, которых нет; `README.md:1010–1012` —
  `sources_collect.py`, `check_links.py`, `ctx_watch.py` вне `scripts/blender/` и «помощники — `03-bpy-api/snippets/`» (файлы лежат в
  `scripts/blender/`, в `snippets/` только README); таблица строк корневого `README.md` (папка `13-tools-atlas` — снимок по
  `wc -l`, правлена только строка `atlas.tsv`). На изменённых строках остались 17 старых битых ссылок от корня базы
  (`15-showcase/…`, `99-raw/…`, `run_c_post.sh`) — их видит `accept.py`.
- **Витрина.** Строки «Для текстов» Д-blender-2 — для того, кто правит `15-showcase/**` (эта зона их не вносит).
- **Атлас.** `13-tools-atlas/README.md` п. 1: «руками заполнены только лицензии, их ограничения и „ценность для агента“» — у 76
  записей `source` = `manual`; сверить формулировку при уборке.
- `kb/INDEX.md`, `references/`, `docs/` — правок не требуют: счёта записей атласа там нет.

## Проверки

- `scripts/blender/run_recipes.py --selftest` — 8 OK, код 0; `scripts/blender/run_doc_blocks.py --selftest` — 8 OK, код 0
  (03.10 и повтор 06.10).
- `run_doc_blocks.py --dry-run` по 47 изменённым md — код 0, `BLOCKS 168: blender 100, system 7, bash 19, js 25, skip 17`;
  рецепты 13–17 — `BLOCKS 28: system 2, js 12, skip 14`. Разбор `run_recipes.blocks()`: 01–12 — blender 11, system 2, skip 0;
  13–17 — исполняемых в Blender 0. Число ограждений блоков в каждом изменённом md — как в HEAD.
- Сборка `build.py`/`post.py` из блоков md против `examples/` (`recipe_diff.py`) — 0 строк расхождения у 13 файлов; новая
  сборка не вернёт снятых штампов. `post.py` у 13, 16, 17 нет — прогон их не собирал (у 17 блок теперь `skip`).
- `scripts/tests/smoke.py --only kb` — PASS 42, FAIL 0 (03.10 и повтор 06.10).
- `scripts/maint/normcheck.py --base HEAD --list-lost <47 md>` — 454 находки НОРМА (потеряно 278, появилось 176): все —
  ожидаемые замены строк: пути машины и `99-raw` → `../../scripts/blender`, `$DDD_HOME`, `examples/<рецепт>/src/`; коды выхода
  `qa_pipeline.py`; числа и id внутри снятых путей (`03-bpy-api`, `D1/_lib`, `E/26-doc-snippets`, `npm-F1`); счёт атласа 156 →
  154, 157 → 155; снятые штампы `D1/03…D2/04`, `A/06`, `H/12`, `F1`, `F2`; три даты (следы) в изменённых строках
  `00-how-to-use.md:5`, `12-recipes/README.md:6, 96`. Неожиданных потерь нет.
- `scripts/maint/refcheck.py --strict` по 106 md базы вне `99-raw` и `15-showcase`: было 2303 битых и 397 следов, стало 2275 и
  392; новых находок 0, снято 33 (28 битых, 5 следов).
- `scripts/maint/accept.py --base HEAD --mask '.claude/skills/design-deep-dive/kb/blender/*'` — следов в изменённых строках 0;
  «ссылки» — 17 старых битых ссылок на изменённых строках (выше); «маски» — 278 файлов других зон в общем дереве; разбор,
  код, следы `.py` — OK.
- `scripts/maint/canon_check.py` — код 0 (ошибок 0, предупреждений 0); `scripts/maint/mapcheck.py kb/INDEX.md` — код 0;
  `scripts/maint/sync_check.py` — генераторы OK 17, FAIL 0, копий расходится 0.
- `scripts/site/vocab_lint.py kb/blender/12-recipes/00-how-to-use.md` — 0 ошибок.
- Читатели `atlas.tsv` в `scripts/` — нет (поиск `atlas.tsv` и `13-tools-atlas` по `scripts/`: 0); таблица разбирается
  `csv` — 155 строк, 16 колонок у всех.

## Вопросы

1. Строки Д-blender-2 о витрине (`_shared/code3d/README.md`: «npm-trial» → «npm-зависимости скилла», «паспорт Z» →
   `zveno/art-direction.md §4`; пути сырья `keyboard/README.md`; списки кадров `judge/`) — кто вносит, если витрину правит
   только зона данных?
2. Форма ссылки в прозе вложенных статей: от папки файла (так внесено — `refcheck.py` её разрешает) или от корня базы (форма
   строк К14 и большинства старых ссылок базы — у `refcheck.py` они битые)? Уборке следов нужна одна форма.
3. Строка пути в рецептах 01–12: оставить `__file__` (как в `build.py`) или перейти на `"../../scripts/blender"` и
   пересобрать `build.py` — тогда блоки исполнит и `run_doc_blocks.py`.
4. Скриншот рецепта 03 (`03:46`, файла в `99-raw` нет): положить картинку в `examples/03-device-mockup/` или сменить источник
   текстуры — нужна правка кода и текста рецепта.
