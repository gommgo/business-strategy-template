# D6a — генерация: отчёт ДФ9

Пути `scripts/…`, `kb/…`, `references/…` — от `.claude/skills/design-deep-dive/`. База — `5d5e86a` (файлы зоны с `7e6d57e`
не менялись). Платных вызовов и `--live` не было; `polza.py estimate` — с `POLZA_BASE_URL=http://127.0.0.1:9` (без сети).

## 1. Файлы

| файл | новый / правка | строк (+/−) | что внутри (функции, подкоманды, ключи, разделы) |
|---|---|---|---|
| `scripts/ai-media/routing_check.py` | правка | 417 (+68/−77) | справка о текущем: сверка — сигнал, не стоп; снимки — последние в `$DDD_HOME/cache/ai-media`; что проверяет (11 пунктов); запуск и коды 0 · 1 · 2. Сняты `TEST_ID`, `known_test_ids()`, проверка `phase5_test` и поле `phase5_test` в обязательных полях маршрута. `main`: ключи `--polza`, `--routerai`, `--genapi` (имя папки или путь, по умолчанию — последний снимок), нет снимка polza — строка с командой установки и код 2; отчёт — строка «Снимки, с которыми матрицу сверяли при обновлении (`catalog_snapshots`)» рядом со снимками прогона; JSON — поле `snapshots {used, matrix}`; `--help` — вся справка; сообщения и докстринг — «ai-media 12/0x» вместо буквы агента; комментарии без «перенос», «v1.1» |
| `scripts/ai-media/prompt_compile.py` | правка | 2 131 (+82/−64) | справка о текущем (что делает, команды, умолчания `jobs`, какие команды читают снимок, запуск, коды выхода); `VERSION = "2.2"`; модульные `SNAPSHOT_DIR`, `CATALOG`, `NORMALIZED` сняты → `snapshot_dir()` (ленивое чтение, нет снимка — строка «нет снимков … — снимок каталога polza: scripts/install.sh --catalogs …» и код 2), `catalog_file()`; `load_catalog(path=None)`, `load_normalized(path=None)`; паспорт компиляции — `catalog_file()`; `make_jobs(…, dialects_list=None, repeats=1, seeds=(), tag=None, agent=None, …)` — диалект семейства `fam["format"]`, без seed, тега и агента (поле `agent` не пишется), заметка «<spec>: диалект D, вариант k»; CLI `jobs` — те же умолчания и справка ключей; `validate` без `--model` — без каталога; `--help` — вся справка; сообщения вывода без агентов и `venv-D2` (звук `-an`, инверсия маски, i2v, `upload`, аутпейнт, `prepare`, `catalog_check`); PyYAML — строка про Python окружения скилла |
| `scripts/ai-media/stand_run.py` | правка | 1 154 (+134/−29) | справка (`collect`, `page`, `selftest`); `import os`; `IMAGE_EXT`; `collect_rows(root, agent=None)` — путь паспорта от `root`, файл без `path` пропускается; `cmd_collect`; `page_rows(src)` — таблица `collect`, паспорта в папке или картинки папки без паспортов; `cmd_page` — стенд (группы голосования, пары между моделями) и план/папка (группа — `meta.spec` или подпапка, вариант — «модель#номер» или имя файла, пары между всеми вариантами группы), не-картинки — строка в stderr, нет пар — код 2; CLI: `collect --root` (по умолчанию `POLZA_OUT_ROOT` или `$DDD_HOME/out/ai-media/_polza`), `--agent A` вместо `--any-agent`; `page ВХОД` — справка входа и `--tests`; `selftest` +3 проверки; `--help` — вся справка; комментарий `JOBS` без `routing_check` |
| `scripts/ai-media/tests/test_prompt_compile.py` | правка | 310 (+35/−10) | шапка о текущем; `import os`; CLI `jobs` A/B — `--seeds 101,202` явно; имя проверки «validate polza_catalog»; раздел 12 — `pc.snapshot_dir()`; раздел 13 — 4 проверки: `make_jobs` по умолчанию, CLI `jobs` без ключей формы — 1 задание, без снимка `--help`/`ratios`/`validate` — код 0, `validate --model`/`compile` — код 2 и строка установки |
| `scripts/ai-media/tests/test_prompt_compile_x2.py` | правка | 102 (+5/−5) | шапка о текущем, комментарий `kbpaths` |
| `scripts/ai-media/README.md` | правка | 130 (+124/−345) | о текущем: вступление (нормы в базе, `kbpaths`, окружение, выходы, снимки, `--help`); «Генерация по плану ассетов» (цепочка спецификация → `jobs` → `estimate` → «да» заказчика → `--live` → приёмка → выбор; снимки и `routing_check` — сигнал) и таблица утилит генерации; «Приёмка ассетов — `asset_audit.py`» (команды, 90 проверок, 92 с `--ocr`, `--icon-set`, `QA-PROV-VISIBLE-MARK` — предупреждение с листом углов, строки окружения и поле `env`) и таблица утилит приёмки (`check_icons.py`, `palette.py` с командной строкой и др.); «Выбор из вариантов — `stand_run.py`»; «Деньги и ключи»; «Обслуживание базы»; «Тесты и данные» |
| `scripts/tests/smoke/ai-media.tsv` | правка | 51 (+3/−5) | `palette.py` — `utility · help`; `check_icons.py` — `utility · help` без xfail; `prompt_compile.py` — `help` без xfail; строки `vm_sheet.py`, `validate_recipes.py` сняты |
| `kb/ai-media/README.md` | правка строк 38–42 | +5/−4 | п. 2 — снимки и `routing_check.py` — сигнал, не стоп (без даты); п. 3 — перед платным вызовом `estimate` без ошибок и «да» заказчика |
| `kb/ai-media/14-recipes/00-cheatsheet.md` | правка «Перед работой» и чек-листа | +10/−8 | «Перед работой» (стр. 11–19): п. 1 — гейт «`estimate` без ошибок и «да» заказчика», вызовы `$DDD_HOME/venv/bin/python scripts/ai-media/…`, `jobs` — одно задание; п. 2 — снимки и `routing_check` — сигнал; п. 3 — сверка баланса — сигнал; п. 4 (ключи) — без изменений; чек-лист стр. 110 и 112 |
| `kb/ai-media/14-recipes/01-hero-recipes.md` | правка блока команд (стр. 97–110) | +12/−11 | вызовы `$P scripts/ai-media/…` с `P=$DDD_HOME/venv/bin/python` из корня скилла, выходы — `$DDD_HOME/out/ai-media/demo-hero`, `jobs` без `--dialects`/`--test`/`--agent` (одно задание), `estimate` — 4,00 ₽ (1K), строка о ручной доводке паспорта |
| `kb/ai-media/14-recipes/04-capability-map.md` | правка стр. 367 | +1/−1 | чек-лист: гейт `estimate` и «да» заказчика; модель и id — из `routing.yaml`; снимок и `routing_check.py` — сигнал |
| `scripts/ai-media/vm_sheet.py` | снят (`git rm -q`) | −170 | — |
| `scripts/ai-media/validate_recipes.py` | снят (`git rm -q`) | −71 | — |
| `research/design-build/phase-9/reports/D6a.md` | новый | — | этот отчёт |

## 2. Находки

| id | что сделано и где (файл: функция / подкоманда / ключ / раздел) | как проверено |
|---|---|---|
| OE3-01 | `routing_check.py`: снимки по умолчанию — последние (`pc.Snapshot(a.polza)`, `mp.RouterCatalog(a.routerai)`, `mp.GenapiCatalog(a.genapi)`, `None` → последний), `catalog_snapshots` матрицы — строкой в отчёте и `snapshots.matrix` в JSON; сняты `known_test_ids`, проверка `phase5_test` и поле в обязательных; справка — «сигнал, не стоп»; нет снимка polza — код 2. Строки kb «сверка — сигнал»: `kb/ai-media/README.md` стр. 38–42, шпаргалка 14/00, карта 14/04 стр. 367; `kb/INDEX.md` — D8 («Для текстов») | без аргументов: до — «снимок не найден: 2026-09-25_1411», код 1; после — снимки `polza 2026-09-29 · RouterAI 2026-09-29_1306 · Gen-API 2026-09-29_1306`, 33 маршрута, 136 вариантов, 0 ошибок, 0 предупреждений, код 0. Копия матрицы со снимками 29.09 до правки — 137 ошибок у 29 маршрутов, все `phase5_test`, настоящих 0. Негативная копия (цена 9 ₽ вместо 7 ₽, модель `bytedance/seedream-404`, без поля `phase5_test`) — 2 ошибки, код 1. Пустой `DDD_HOME` — строка с `install.sh --catalogs`, код 2; `--genapi nope` — 7 предупреждений «каталог Gen-API не загружен», код 0 |
| OE3-02 | `prompt_compile.py`: снимок читают `snapshot_dir()`/`catalog_file()` при первой команде, которой нужен каталог (compile, jobs, chain, matrix, validate с `--model`); `--help`, `ratios`, `validate` без `--model` отвечают без снимка | пустой `DDD_HOME`: `--help`, `jobs --help`, `ratios`, `validate` — код 0; `validate --model`, `compile` — «нет снимков … — снимок каталога polza: scripts/install.sh --catalogs …», код 2 (то же — проверки раздела 13 `test_prompt_compile.py`); `vlm_to_dna.py selftest` без снимка — пропуск компиляции (ловит «нет снимков»), 33/33; со снимком — 33/33 |
| OE3-04 | `scripts/ai-media/README.md` переписан о текущем (351 → 130 строк): утилита → вызов → выход, за ключами — `--help`; сняты агенты и волны, «Будут добавлены агентами», «Правила» фаз, `99-raw/tools`, `venv-D2`, `venv-G`, `ab_analyze.py`, `fetch.py`, `yt_dl.py` и разделы утилит, которых в папке нет; правки D6b («Для текстов» п. 2) внесены. Указатель («Подробный README домена») — D9 | `refcheck --strict` — 79 ссылок, 0 битых, 0 следов; ширина прозы ≤ 120; вызовы в таблицах сверены с `--help` и `add_parser` утилит; число проверок приёмки — прогон `tests/test_asset_audit.py`: 90/90 |
| OE3-10 | `stand_run.py`: `collect_rows` — путь паспорта `relative_to(root)` (корень выходов, а не `kb`); `collect --root` по умолчанию — выходы `polza.py` (`POLZA_OUT_ROOT` или `$DDD_HOME/out/ai-media/_polza`), фильтр агента «E» снят → `--agent A`; `page` — из выхода `polza.py`: папка паспортов или таблица `collect` (план — группа на спецификацию, пары между всеми вариантами), а также папка картинок без паспортов (§3 п. 1) | до правки (старая версия из `git show HEAD` на паспортах вне `kb`): без ключа — 0 результатов (фильтр «E»), с `--any-agent` — `ValueError: … is not in the subpath of …/kb/ai-media`; после: `collect --root <scratchpad>/pp` — 4 результата, путь `pilot-x/day/….passport.json`, без трассировки; `collect` по умолчанию на пустом `_polza` — 0, код 0; `page <папка паспортов>` — 2 группы, 2 основные пары (варианты одной модели — в паре), `page results.jsonl --tests ab-b2-illustr` — 1 пара; `selftest` — 15/15 (+3: collect вне базы и `--agent`, страница из выхода polza.py, папка кадров без паспортов); `stand_page.py selftest` (модуль `stand_run`) — PASS; `asset_audit` (`--from-stand-page`) — 90/90 |
| OE3-15 | шпаргалка 14/00 «Перед работой» (стр. 11–19) и чек-лист (стр. 110, 112), README базы (стр. 38–42): перед платным вызовом — `estimate` без ошибок и «да» заказчика; снимки, `routing_check` и сверка баланса — сигнал | чтение; `refcheck --strict` по тронутым строкам — 0 битых, 0 следов (находки файла — в нетронутых строках, §7) |
| OE3-17 | сняты `scripts/ai-media/vm_sheet.py` (−170), `validate_recipes.py` (−71) и их строки `ai-media.tsv`. Утилиты обслуживания матрицы и сценариев из `note` (asset_inventory, channel_diff, stand_run build…ministand, polza_catalog diff/table, routing_check, split_recraft) — не тронуты | поиск до снятия (`grep -rn` по `.claude/`, `docs/`): код, этапы, аудит, фикстуры, `maint/data` не зовут; упоминания — указатель `scripts/README.md` стр. 140–141 (D9), `kb` (список Ф10, §8); `git ls-files` их не видит; `smoke --validate`, `--uncovered` — чисто |
| OE3-23 | `prompt_compile.py jobs` по умолчанию — одно задание (диалект семейства, 1 вариант, без seed, тега и агента), A/B — `--dialects`, `--repeats`, `--seeds`, `--tag`, `--agent`, `--test`; рецепт hero 14/01 (стр. 97–110) — вызовы `$DDD_HOME/venv/bin/python scripts/ai-media/…`, `jobs … --out $DDD_HOME/out/ai-media/demo-hero/…`, без `99-raw/tools`, `venv-D2`, `99-raw/phase5/jobs` | `jobs D03/B2 --models openai/gpt-image-2.5-sunburst`: до — 6 заданий (prose, sections, json × 2 повтора, агент `phase5-D`, тег `D-ab-…`), `estimate` 24,00 ₽; после — 1 задание (`sections`, вариант 1, без `agent`, тег `ab-b2-illustr-sections-…-1`), `estimate` 4,00 ₽; D02/E1 — 42,00 → 7,00 ₽; A/B явными ключами (`--dialects prose,sections,json --repeats 2 --seeds 101,202`) — 6 заданий. Рецепт hero прогнан целиком (кроме `asset_audit` мастера): `validate` — `ok: true`, `to-spec` → `compile` → `jobs` 1 задание → `estimate` 0 ошибок, 4,00 ₽ |
| OV-4 | = OE3-01, OE3-15, OE3-23: `routing_check` — сигнал, `jobs` — одно задание, рецепт hero — без путей исследования; `kb/INDEX.md` — D8 | см. строки выше |
| OV-7 (часть D6a) | `relative_to` в `stand_run.py` (OE3-10) и README ai-media о текущем (OE3-04); README blender — D7, форма утверждения иллюстраций — D8 | см. OE3-10, OE3-04 |

## 3. Отступления от плана и спецификации

1. **`page` принимает и папку картинок без паспортов** (кадры 3D, снимки сборок): группа — подпапка, вариант — имя файла.
   Бриф называет вход «из выхода `polza.py`», но D7 (OE3-11: `kb/common/judge.md` §7, `kb/blender/README.md`) и D9
   (OE4-13: «варианты макета» в `claude-design.md`) направляют на `stand_run.py page` кадры Blender и снимки холста —
   это не паспорта polza, и без такого входа у их строк нет рабочего пути. Варианты: оставить (предлагаю: функция `page_rows` и
   своя проверка самопроверки) или снять ветку папки — тогда D7 и D9 нужен другой вход.
2. **Пары у заданий плана — между всеми вариантами группы**, в том числе одной модели (вариант — «модель#номер», при
   нескольких файлах результата — «.n», совпадение подписей — «·2»); у заданий стенда пары — между моделями группы
   голосования, как раньше. Не-картинки (видео) на страницу не попадают — строка в stderr (раньше Pillow падал
   трассировкой); нет пар — код 2. Формат ключа страницы тот же (`pairs[pid].A/B.model` — подпись варианта), его читают
   `tally` и `asset_audit.py judge-jobs --from-stand-page`.
3. **`routing_check`**: поле `phase5_test` снято и из обязательных полей маршрута — поле журнала опытов; иначе матрица
   без него (уборка базы в Ф10) давала бы ошибку. Снимок выбирается ключом на канал (`--polza`, `--routerai`,
   `--genapi`), а не одним `--snapshot`: имена папок у каналов разные (`polza/2026-09-29`, `routerai/2026-09-29_1306`).
   Нет снимка polza — код 2 и строка с командой (было «снимок не найден», код 1). Новое в выводе — строка
   `catalog_snapshots` и поле JSON `snapshots`; потребителей JSON в коде нет (поиск по `.claude/`).
4. **`prompt_compile`**: нет снимка — код 2 (было: `SystemExit` при импорте, код 1; строка «нет снимков» сохранена — её
   ловит `vlm_to_dna.py selftest`). `VERSION` «2.1.1 (2026-09-24, X2)» → «2.2»: умолчания `jobs` сменились, поле
   `compiler` паспорта компиляции — «2.2». Сообщения вывода почищены от агентов, кодов опытов и `venv-D2` (7 строк),
   внутренние комментарии с метками D2/D2b/X2/F2 не тронуты — Ф10.
5. **Задание без `agent`** (без `--agent`): `polza.py` и `mp_client.py` берут агента по умолчанию (`--agent` клиента,
   `POLZA_AGENT`/`MP_AGENT`, иначе `unknown`) — выходы идут в `$DDD_HOME/out/ai-media/_polza/unknown/<дата>/`, если
   пилот не задал агента. Варианты: оставить (задание не несёт агента опыта) или ставить агента по умолчанию
   `plan` — решает оркестратор.
6. **Рецепт hero**: скелет паспорта из `from-tokens` не годится для `to-spec` («в паспорте нет style_blocks.photo») —
   звено 2 таблицы рецепта и есть «from-tokens → руками → validate». В блок команд добавлена строка-комментарий о ручной
   доводке, `validate` и `to-spec` идут от готового паспорта демо `$B/dna-forest-roast.json`; цена — 4,00 ₽ (1K:
   `to-spec` ставит 1K) вместо 7,00 ₽ (2K у спецификации M-01, чей вход лежит в `99-raw`). Рецепт больше не пишет в `kb`:
   выходы — `$DDD_HOME/out/ai-media/demo-hero`. Блок стал на строку длиннее (97–110 вместо 97–109).
7. **Карта 14/04 стр. 367 — без id Flare:** `refcheck` принимает id `openai/…` в обратных кавычках за путь (ложная битая
   в тронутой строке); строка отсылает к `routing.yaml`, где id и живёт.
8. **README ai-media шире списка снятого:** кроме журнальных разделов брифа сняты разделы утилит, которых в папке нет
   («Веб и видео», «Субтитры YouTube», «Цвет» — `color.py` в `../lib/`, «Локальные бинарники», «Вектор и SVG» с
   `99-raw/tools/…`) и раздел `check_links.py` (утилита в `maint/`, зона D7); пересказ ключей заменён отсылкой к `--help`.

## 4. Для следующих зон

- **`stand_run.py page ВХОД --out СТРАНИЦА [--tests ГРУППА,…] [--repeat 0.1] [--seed 7]`** — ВХОД: папка выходов
  `polza.py` (паспорта `*.passport.json`), таблица `collect` (`.jsonl`) или папка картинок без паспортов. Группы:
  задания стенда — `meta.vote_groups` или `test/task/arm`; задания плана — `meta.spec`; папка — подпапка (картинки в
  корне — имя папки). Ключ `<СТРАНИЦА>.key.json` — прежний формат. D7 (кадры 3D) и D9 (снимки сборок холста):
  `stand_run.py page <папка кадров> --out <страница>` → голоса → `stand_run.py tally <голоса>.json --key <страница>.key.json`.
- **`stand_run.py collect [--root DIR] [--agent A] [--out results.jsonl]`** — строки те же, `passport` — от DIR;
  `--any-agent` снят. `collect_rows(root, agent=None)` и `page_rows(src)` — функции модуля.
- **`prompt_compile.py`**: `jobs SPEC… --models ID[,…]` — одно задание на спецификацию и модель; `make_jobs(spec_paths,
  models, dialects_list=None, repeats=1, seeds=(), tag=None, agent=None, *, …)`; снимок — `snapshot_dir()`,
  `catalog_file()` (модульных `SNAPSHOT_DIR`, `CATALOG`, `NORMALIZED` нет; внешних читателей, кроме теста, не было).
- **`routing_check.py [ROUTING.yaml] [--polza|--routerai|--genapi SNAP] [--md F] [--json F]`** — код 0 · 1 · 2; JSON:
  `ok`, `errors`, `warnings`, `rows`, `snapshots {used, matrix}`.
- **Оркестратор, Ш0:** пилоту с генерацией — `install.sh --catalogs` (без снимка `prompt_compile` отвечает только на
  `--help`, `ratios`, `validate`; `routing_check` — код 2).

## 5. Тесты и прогоны

- **До правки:** `routing_check.py` без аргументов — «снимок не найден: 2026-09-25_1411», код 1; копия `routing.yaml`
  со снимками 29.09 — 137 ошибок у 29 из 33 маршрутов, все `phase5_test`, настоящих 0; `jobs` без ключей — 6 заданий,
  `estimate` 24,00 ₽ (B2) и 42,00 ₽ (E1); `stand_run collect` на паспортах вне `kb` — 0 результатов, с `--any-agent` —
  `ValueError`; `test_prompt_compile.py` 98/98, `test_prompt_compile_x2.py` 15/15.
- **После:** `routing_check.py` без аргументов — 0 ошибок, 0 предупреждений, код 0 (настоящих расхождений моделей и цен
  на снимках 29.09 — нет); негативная копия — 2 ошибки, код 1; пустой `DDD_HOME` — код 2. `prompt_compile.py --help` при
  пустом `DDD_HOME` — справка, код 0; `jobs <спецификация> --models <модель>` — 1 задание, `polza.py estimate` —
  4,00 ₽ (B2), 7,00 ₽ (E1). `test_prompt_compile.py` — 102/102 (98 + 4 новых), `test_prompt_compile_x2.py` — 15/15.
  `stand_run.py selftest` — 15/15; `collect --root <папка паспортов вне kb>` — 4 результата, без трассировки.
  `stand_page.py selftest` — PASS; `vlm_to_dna.py selftest` — 33/33 (и без снимка — пропуск компиляции, 33/33);
  `tests/test_asset_audit.py` — 90/90.
- **Смоук** `python3 scripts/tests/smoke.py --only scripts/ai-media` — PASS 54, FAIL 0, XFAIL 2 (прежние:
  `mp_client.py run selftest`, `polza_catalog.py run selftest` — числа снимков), XPASS 4 (`provenance_check` selftest,
  `svg_sheet` help, два теста компилятора — снимок есть); было у D6b — PASS 54, XFAIL 2, XPASS 6: −2 строки снятых
  утилит, `check_icons` и `prompt_compile` help — из XPASS в PASS. `--validate` — 18 списков, 200 строк, 0 ошибок;
  `--uncovered` — 0.
- **Синхронность:** `scripts/maint/sync_check.py all` — генераторы OK 17, FAIL 0; копий расходится 0; описания OK;
  находок 0. Фикстуры зона не задевает.

## 6. Строки смоука

`scripts/tests/smoke/ai-media.tsv`:
- `scripts/ai-media/palette.py	utility	help	` (было `module · import-only`);
- `scripts/ai-media/check_icons.py	utility	help	` (было `module · help`, xfail «help: нужны cairosvg …»);
- `scripts/ai-media/prompt_compile.py	utility	help	` (снят xfail «help: нужен снимок каталога polza …» — справка
  отвечает без снимка);
- сняты `scripts/ai-media/validate_recipes.py	step	compile` и `scripts/ai-media/vm_sheet.py	step	help`;
- остаются с причиной: `tests/test_prompt_compile.py`, `tests/test_prompt_compile_x2.py` — «run: нужен снимок каталога
  polza — install.sh --catalogs» (тестам снимок нужен); `mp_client.py`, `polza_catalog.py` — прежние XFAIL.

## 7. Проверка

- `refcheck --strict`: `scripts/ai-media/README.md` — 0 битых, 0 следов; тронутые строки `kb` — 0 битых, 0 следов
  (в нетронутых строках тех же файлов — 126, 7, 39, 79 битых и следы журнала — проза базы, Ф10; в блоке команд рецепта
  hero `refcheck` не смотрит — он внутри ограды кода).
- Следы в коде (шаблоны приёмки): `stand_run.py` — 0; `routing_check.py` — 3, `prompt_compile.py` — 6, тесты — 36 и 9:
  все — id и семейства моделей генерации (`qwen/image-2.1`, `gpt-image-*`, «Gemini API» в комментарии диалекта) —
  данные маршрутов и диалектов, не умолчания оценки; дат, Р- и Ф-номеров, агентов в справке тронутых файлов нет.
- Ключей в коде, тестах и отчёте нет; сеть — нет (утилиты зоны сеть не открывают; `estimate` — на `127.0.0.1:9`).
- Синтаксис `.py` — прогонами; JSON и YAML зона не правила. Прочитано глазами: `routing_check.py` целиком;
  `prompt_compile.py` — справка, загрузка, `validate_spec` (модельная часть), `compile_prompt`, `ratio_variants`,
  `make_jobs`, `main`; `stand_run.py` — справка, `build` (заголовок), `collect`, `page`, `build_page`, `tally`,
  `ministand`, `selftest`, `main`; тесты компилятора целиком; README ai-media целиком; строки `kb` и их окрестности.

## 8. Открыто и не прочитано

- **Открыто, Ф10 (проза и данные `kb`, строки вне зоны):** `vm_sheet.py` — `kb/ai-media/README.md` стр. 56, 446;
  `validate_recipes.py` — `kb/ai-media/14-recipes/README.md` стр. 22, `kb/ai-media/CONTRADICTIONS.md` стр. 369,
  `99-raw/`; поле `phase5_test` и `catalog_snapshots` с путями `99-raw/cache/…` в `routing.yaml` (данные), строка 6
  шапки `routing.yaml` («0 ошибок»); `kb/ai-media/13-routing-matrix/04-update-procedure.md` §2 и §2.1 (строка «`тест T не
  найден` — поправить `phase5_test`», «0 ошибок — иначе §2.1», стр. 112 — `99-raw/tools/venv-D/…stand_run.py collect`),
  `kb/ai-media/README.md` «Как обновлять» п. 1 (`catalog_snapshots` — запись сверки, снимки прогона — последние);
  рецепт hero стр. 89 (строка таблицы «задание фазы 5 … `99-raw/phase5/jobs`»); `compile:` одиннадцати
  `14-recipes/recipes/*.yaml` (`99-raw/tools/venv-D2/…`); шпаргалка 14/00 стр. 4 («снимки каталогов `2026-09-25_1411`»).
- **Открыто, Ф10 (код вне зоны или вне брифа):** комментарии `prompt_compile.py` с метками D2/D2b/X2/F2 и ссылками
  `[V:…]`; путь заданий стенда `$DDD_HOME/out/ai-media/phase5/jobs` и агент «E» в `stand_run build/ministand` (стенд —
  лаборатория до Ф10); справки `polza_catalog.py`, `polza.py` (`99-raw/cache`, «агент B»), `channel_diff.py`,
  `layout_check.py` (`99-raw/tools/.locks`), `split_recraft.py`, `svg_sheet.py` (`venv-G`) — файлы ai-media вне списка
  зоны; `--agent` по умолчанию у заданий плана (§3 п. 5).
- **Замер Ф9:** число вариантов на ассет плана (`--repeats`) и сумма `estimate` против строки плана; пригодность страницы
  пар для кадров 3D и снимков сборок.
- **Не прочитано:** `prompt_compile.py` вне названных мест (линты, блоки, диалекты) — правка их не касалась;
  `stand_run.py` `metrics`, `sheet`, `PAGE_HTML`; `polza.py` и `mp_client.py` — только места `agent`, `out_dir`, паспорт;
  `KEY.md`, `KEY-seeded.md` — только поиск имён (правило ДФ9).

## Для текстов

Что меняется по смыслу; формулировки — текстовые зоны по SKILL-MAP §7.

1. **`kb/INDEX.md` стр. 223–224** (D8): было — «перед генерацией — свежие снимки каталогов и `routing_check.py` без
   ошибок»; стало — перед платным вызовом — `estimate` без ошибок и «да» заказчика; снимки каталогов и `routing_check.py`
   (по умолчанию — последние снимки в `$DDD_HOME/cache/ai-media`) — сигнал: расхождение модели или цены — сверить строку
   плана и `estimate`, а не стоп (так уже говорят README базы, шпаргалка 14/00 и карта 14/04).
2. **`references/phases.md` `asset-plan`** (D8, «Точка заказчика», «Проверка»): генерация по утверждённому плану —
   задания `prompt_compile.py jobs <спецификация> --models <модель>` — по умолчанию одно задание на спецификацию и модель
   (варианты плана — `--repeats N`, сравнение форм промта — только явными ключами), цена — `polza.py estimate`
   (`mp_client.py estimate`) по файлу заданий против строки плана, «да» заказчика — до `--live`; `routing_check.py` и
   снимки — сигнал. «Выбор из вариантов — попарно (ai-media 11/03 §4)» — команда: `stand_run.py page <папка выходов
   polza.py> --out <страница>` → голоса → `stand_run.py tally` (группа — спецификация, пары между всеми её вариантами).
   Окружение этапа с генерацией — `install.sh --catalogs` (без снимка компилятор заданий не собирает).
3. **`references/phases.md` `assets`** (D8): серии и заметные картинки — тот же путь (одно задание по умолчанию,
   `estimate`, «да» заказчика), выбор из вариантов — `stand_run.py page`.
4. **Указатель `scripts/README.md`** (D9):
   - стр. 115 «Подробный README домена — `ai-media/README.md` (из базы)»: README домена — о текущем (утилита → вызов →
     выход: генерация по плану, приёмка, выбор из вариантов, деньги и ключи, обслуживание базы); «из базы» — снять;
   - `ai-media/prompt_compile.py` (стр. 128): вход — `validate SPEC [--model ID]`, `compile SPEC --model ID`,
     `jobs SPEC… --models ID[,…] [--out F]` (одно задание по умолчанию; A/B — `--dialects`, `--repeats`, `--seeds`),
     `chain`, `ratios`, `matrix`; снимок каталога читают только compile, jobs, chain, matrix и validate с `--model`;
   - `ai-media/routing_check.py` (стр. 130): было «проверка 13-routing-matrix/routing.yaml», выход
     `$DDD_HOME/out/ai-media/phase5/jobs`; стало — сверка матрицы маршрутов с последними снимками каталогов, сигнал;
     вход `[ROUTING.yaml] [--polza|--routerai|--genapi SNAP] [--md F] [--json F]`, выход — stdout, `--md`, `--json`,
     читает `$DDD_HOME/cache/ai-media`; код 2 — нет снимка polza;
   - `ai-media/stand_run.py` (стр. 131): было `$DDD_HOME/out/ai-media/_polza/E`; стало — `collect [--root DIR] [--agent
     A]` (корень — выходы `polza.py`), `page ВХОД` — папка выходов `polza.py`, таблица `collect` или папка картинок
     (кадры 3D, снимки сборок);
   - строки `ai-media/validate_recipes.py` и `ai-media/vm_sheet.py` (стр. 140–141) — снять (файлы сняты);
   - `check_icons.py`, `palette.py`, `asset_audit.py` — по «Для текстов» D6b п. 1.
5. **`references/claude-design.md` «варианты макета»** (D9, OE4-13): страница пар из снимков сборок —
   `stand_run.py page <папка снимков> --out <страница>`: папка без паспортов, группа — подпапка, вариант — имя файла.

## Для ключа

Не меняется: сценарии 1–4B и 14 посевов утилиты зоны не вызывают (поиск по `phase-8/check/KEY.md`, `KEY-seeded.md` —
0; в `phase-8/tools/` — только маска зоны Ф8 в `accept.py`).

## 9. Запись для CHAIN

```
## <NN>. D6a — генерация (30.09, ≈ <мин> мин, в уведомлении — <тыс.> токенов)
- Сделано: правлены `scripts/ai-media/routing_check.py` (+68/−77), `prompt_compile.py` (+82/−64), `stand_run.py`
  (+134/−29), `tests/test_prompt_compile.py` (+35/−10), `test_prompt_compile_x2.py` (+5/−5), `README.md` (351 → 130,
  о текущем), `smoke/ai-media.tsv` (+3/−5), строки kb: README ai-media 38–42, шпаргалка 14/00 «Перед работой» и
  чек-лист, рецепт hero 14/01 97–110, карта 14/04 стр. 367; сняты `vm_sheet.py`, `validate_recipes.py`. OE3-01, OV-4 —
  `routing_check` на последних снимках `$DDD_HOME/cache/ai-media`, `phase5_test` снят, ключи `--polza/--routerai/--genapi`,
  код 2 без снимка; OE3-02 — снимок читают только compile, jobs, chain, matrix, validate `--model`; OE3-23 — `jobs` по
  умолчанию одно задание, A/B явными ключами, рецепт hero без путей исследования; OE3-10, OV-7 — `collect` от корня
  выходов, `--agent` вместо папки «E», `page` из выхода `polza.py` и из папки картинок; OE3-15 — «перед платным
  вызовом — `estimate` и «да» заказчика; снимки, `routing_check`, баланс — сигнал»; OE3-04 — README о текущем; OE3-17.
- Тесты: `routing_check` — 0 ошибок, код 0 (до — «снимок не найден»; 137 ошибок `phase5_test` на снимках 29.09);
  `jobs` — 1 задание, `estimate` 4 ₽ (до — 6 и 24 ₽); тесты компилятора 102/102 и 15/15; `stand_run selftest` 15/15;
  смоук `scripts/ai-media` — PASS 54, FAIL 0, XFAIL 2, XPASS 4; `--validate`, `--uncovered` — чисто; `sync_check all` — 0.
- Отступления: `page` и по папке картинок без паспортов (кадры 3D D7, снимки сборок D9); пары плана — между всеми
  вариантами; `phase5_test` снят и из обязательных полей; снимок — ключом на канал; код 2 без снимка у обеих утилит;
  `VERSION` 2.2; задание без `agent`; рецепт hero — готовый паспорт демо, 4 ₽ (1K), выходы вне kb; стр. 367 без id Flare.
- Стыки: D7, D9 — `stand_run.py page <папка> --out <страница>`; D8, D9 — «Для текстов» отчёта; Ш0 — `install.sh
  --catalogs` для пилота с генерацией.
- Открыто: проза и данные kb с `vm_sheet`, `validate_recipes`, `phase5_test`, `99-raw` — Ф10; комментарии компилятора
  с метками опытов — Ф10; агент по умолчанию у заданий плана — решение оркестратора; число вариантов и сумма
  `estimate` против плана — замер Ф9.
- Не прочитано: `prompt_compile.py` вне мест правки, `stand_run.py` `metrics`/`sheet`, `polza.py` и `mp_client.py` вне
  мест `agent` и паспорта; `KEY.md`, `KEY-seeded.md` — только поиск.
```
