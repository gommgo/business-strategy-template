# FX — пакет правок по проверке сценариев: отчёт Ф8

Агент FX, шаг 11. Бриф — `research/design-build/phase-8/briefs/FX.md`, находки — `research/design-build/phase-8/check/runs.md`
(№ 1–21; ключи не читались). `SK` ниже — `.claude/skills/design-deep-dive/`. Тексты скилла (`references/`,
`design-audit/SKILL.md`, `scripts/README.md`) не трогались — что в них поправить, сказано в разделе «Для текстов».

## 1. Файлы

| файл | новый / правка | строк (+/−) | что внутри |
|---|---|---|---|
| `SK/scripts/project/canvas_input.py` | правка | +114/−37 | шапка правил (R-MAT-012, R-MAT-003, R-COV-007, строка про хвост списков); `listed()` — хвост «и ещё N»; `SKELETON_ADD` — совет при готовом copy deck; `voice_projection` — тяжесть, путь и пробел голоса; `copy_md`, `stitch` — пробелы и советы R-COV-002; `assets_md`, `facts_md` — хвосты и согласование; `assemble_app` — R-MAT-003 контракта на макете → R-MAT-012; `render_manifest` — итог проверки и хвост PRE; `site_items` — хвост событий L1; самопроверка |
| `SK/scripts/project/contract.py` | правка | +6/−2 | хвост R-MAT-003 «и ещё N»; справка — R-MAT-003 как отчёт контракта; самопроверка хвоста |
| `SK/scripts/project/ready.py` | правка | +21/−3 | совет R-FRESH-006; справка — где стоят факты единицы; самопроверка под утверждённые тексты `package-cabinet` и «наименьший статус» |
| `SK/scripts/project/design_audit.py` | правка | +73/−23 | справка (ключи `summary.json`, код 2 в `called`, публикуемость фактов, этапы советов); `listed()`; `sv_stage()` и `SV_STAGE` — этап совета по коду `site_validate`; `vocab_lint` — вид и этап по файлу; этапы у паспорта и форм; `ready_status()` — ключ `ready` сводки; R-MAT-010 — исполнитель и этап; хвосты и согласование числа; самопроверка |
| `SK/scripts/project/ds_sync.py` | правка | +52/−16 | справка (две дороги, R-FRESH-001); поле `Change.alias`; `_roads()`; `after_lift()`; сообщение и совет R-FRESH-001; хвост вывода `build --write`; самопроверка |
| `SK/scripts/project/ds_coverage.py` | правка | +17/−5 | `show` — строка заголовка и колонка «где стоит»; справка; согласование числа R-COV-005 без карты решений; самопроверка |
| `SK/scripts/lib/color.py` | правка | +21/−14 | справка: без истории сборки и мёртвого пути, подключение из `scripts/lib/`, пути команд |
| `SK/scripts/text/copydeck.py` | правка | +23/−8 | `_validate_wave2` — COPY-D-RULES-REF и правила базы при битой `copy_slots_ref`; справка `validate`; самопроверка обоих случаев |
| `SK/scripts/tests/fixtures/package-cabinet/manifest.yaml` | правка | +7/−4 | слой `replace`: 45 строк `texts.md` `checked` → `approved`; шапка и описание |
| `SK/scripts/tests/fixtures/input-cabinet/manifest.yaml` | правка | +3/−3 | шапка — вход mockup: R-MAT-012 на 45 строках; описание |
| `SK/scripts/tests/fixtures/package-cabinet-defects/files/design/office/input/` | пересборка `fixture_gen.py` | INPUT.md +8/−10, contract.md +50/−7, copy.md +46/−46 | вход mockup на утверждённых текстах основы |
| `research/design-build/phase-8/reports/FX.md` | новый | — | этот отчёт |

Файлов, которые снимаются из git, нет. Строки смоука не менялись.

## 2. Действия

| id | где реализовано | как проверено |
|---|---|---|
| 1 гейт текстов кабинета | `canvas_input.py`: `assemble_app` — находка R-MAT-003 `contract` (вид `texts`) на этапе контракта `mockup` (вход `mockup`, у проверки — и `motion`) идёт как R-MAT-012 `error` с префиксом «проверка входа: », сообщение и совет контракта; шапка правил; `contract.py` — справка R-MAT-003 | самопроверка: `input-cabinet` mockup — одна R-MAT-012 error, R-MAT-003 нет, итог «этап не публикуется»; wireframe на тех же строках — 0 error; `package-cabinet` mockup — 0 error; `contract.py check --stage mockup` — R-MAT-003 warning, код 0 (прогон §5) |
| 2 фикстуры | `package-cabinet/manifest.yaml` — `replace` `texts.md`, `count: 45`, шапка; `input-cabinet/manifest.yaml` — шапка; `fixture_gen.py build package-cabinet-defects package-defects` | сборка `package-cabinet`: 53 строки `approved`; `fixture_gen --check` по этим двум — совпадает; `--all` — см. §3 |
| 3 совет R-FRESH-006 | `ready.py`: `check_surface` — «ready build … — на этапе package, после отчёта /design-audit (его error закрывает или принимает заказчик)» | самопроверка `ready` (новая проверка совета); прогон `package-landing` §5 |
| 4 совет R-COV-002 | `canvas_input.py`: `SKELETON_ADD`; `stitch` и `copy_md` (страницы нет в готовом copy deck) — «этап copy: добавить слоты плана в copy deck (каркас недостающих — copydeck.py skeleton <план> -o <временный файл>; готовый copy deck не перезаписывать)»; copy deck нет — «этап copy (каркас из плана — copydeck.py skeleton)» | самопроверка: оба случая (готовый copy deck `input-landing` и copy deck, убранный на время сборки) |
| 5 итог входа | `canvas_input.py`: `render_manifest` — «вход без ошибок: этап можно публиковать, когда готов его вход по phases.md», у `mockup` ещё «(принятый вайрфрейм или его пропуск, ДС в холсте)»; с ошибками — прежний итог | самопроверка на wireframe лендинга и mockup `package-cabinet`; пересобранный `INPUT.md` фикстуры |
| 6 пробел о голосе | `canvas_input.py`: `voice_projection` — «голоса поверхности нет: строки тона во входе нет; тексты во входе — из texts.md (кабинет) · copy deck (сайт), сверка с голосом — после профиля голоса (этап meaning)»; профиль есть, строки тона нет — отдельная строка с именем профиля | самопроверка кабинета; прогон `input-cabinet` §5 |
| 7 R-COV-007 | `canvas_input.py`: `voice_projection` — `warning`; путь — как у `design_audit` (см. §3) | самопроверка: без обоих профилей путь `voice.yaml`; прогоны `input-cabinet` и `package-defects` — один путь у обеих утилит |
| 8 хвост «и ещё N» | `canvas_input.py` (`listed`: R-DEBT-002, факты без источника, R-COV-002, R-REF-003, пробелы, строка PRE, пункт L1, ошибка карт), `contract.py` R-MAT-003, `design_audit.py` (`listed`: R-COV-002 > 10 слотов, R-PROJ-001, R-MAT-006, R-MAT-010, R-MAT-011, R-DEBT-002 ×2), `ds_sync.py` (соседи алиаса) | поиск `(+`, `[:N]` по `scripts/project/`; самопроверки `canvas_input` (R-DEBT-002 «и ещё 4»), `contract` («и ещё 40»); вне файлов зоны — `tree.py`, §8 |
| 9 пробелы без согласования числа | `canvas_input.py`: «текстовые слоты плана без текста в copy deck — N: …», «тексты не того статуса или без выбора для этапа … — N: …», медиа-слоты; сообщение R-COV-002 — «без текста в copy deck — N»; попутно `ds_coverage` («типы без компонента ДС — N»), `design_audit` (R-COV-002, R-MAT-009 «строк(и)», R-SEM-002), `ds_sync` («имён — N») | самопроверка `canvas_input` (нет «N текстовых», «текст(ов)»); прогон лендинга §5 |
| 10 `ds_sync` | справка; `_value_change`, `_style_change` → `Change.alias`, `_roads()`; `to_findings` — совет: «роль: ds_sync build … --write (литерал в <путь>); примитив: правка пути primitive.… в system.tokens.json руками (меняет все ссылки на него); затем пересчёт контраста пар (build_reference_tokens.py или lib/color.py), ds_build build <slug>, публикация ДС»; сообщение — «правка заказчика на странице артефакта не поднята в токены: …»; `build --write` — «дальше — …» | самопроверка (три новые проверки); прогон `cabinet-ds` с живым `tokens.json` §5 |
| 11 `ds_coverage show` | `show` — строка заголовка «поверхность, тип, ключ, компонент, итог, где стоит», колонка «где стоит»; справка — те же колонки | самопроверка (заголовок, 19 строк, у Table — requests-list); прогон §5 |
| 12 `lib/color.py` | справка: назначение, подключение `sys.path.insert(… "..", "lib")`, команды от папки скилла, контрольные точки, пути `kb/ui/01-color/…` | `color.py selftest` — 5 из 5; `--help` |
| 13 сводка `design_audit` | `stages()` → `ready_status()`: `ready` · `partial` · `not-ready`, «—» без статуса, `null` без манифеста; справка — ключи `summary.json`, код 2 в `called`, публикуемость фактов вне R-STRUCT-003 | самопроверка (promo — `not-ready`, office — `null`); прогон `package-defects` §5 |
| 14 советы с этапом | `design_audit.py`: `SV_STAGE`, `sv_stage()` — SB-*, PJ-* → brief, SM-* → site-map, PL-* → `page-plan:<страница>`; `vocab_lint` — по файлу (попутно вид `site-map` у карты сайта вместо `site-brief`); паспорт — `art-direction` (сайт) · `passport-icons` (продукт); формы — `brand` · `design-system` · `app-brief`; R-MAT-010 — «источник закрывает слой проекта — /project-deep-dive <slug> (…), сценарии хабов — /interface-deep-dive <slug> <surface>; поле ядра без источника — … : /design-deep-dive <slug> — app-brief» | самопроверка (PL-F01 → `page-plan:spasibo`, SB-* → `brief`, R-MAT-010); прогон §5 |
| 15 битая `copy_slots_ref` | `copydeck.py`: `_validate_wave2` — ссылка не разрешается → warning COPY-D-RULES-REF «copy_slots_ref не разрешается: <ref>; правила — из базы», правила — файл базы; «правила не загружены» — только если файла нет и в базе; справка `validate` | самопроверка — оба случая (149 OK); последствие для фикстур — §3 |
| 16 `ready --help` | `ready.py`: абзац «факты единицы сайта…» — демо-факт в `open` (пробел назван), `missing:` со строкой пробела — названный пробел, готовность не держат, публикацию держит `copydeck.py validate --final`; в `blockers` — факт вне `facts.yaml`, `missing:` без строки, непубликуемый факт | чтение справки против `fact_problems` и `site()` |

## 3. Отступления от плана и спецификации
- **Решение 15 открыло дефект данных фикстуры — рецепт `landing-defects` падает (главная развилка).** Битая
  `copy_slots_ref` не глушит правила: `copydeck.py` берёт `copy-slots.yaml` базы, и у copy deck страницы `spasibo`
  (текст — константа `SPASIBO` в `.claude/skills/design-deep-dive/scripts/maint/fixture_gen.py`) слот `legal` секции
  `footer` типа `footer-legal` без `fact_ids` получает COPY-D-FACT-REQUIRED: норма `footer-legal` — `fact_required:
  always` («реквизиты — только из facts.yaml; нет — [PLACEHOLDER: реквизиты ООО]»). На статусе `assumed` это warning
  (чистая основа `package-landing` — 0 error), на `checked` и `approved` — error: рецепт `landing-defects` падает на
  `copydeck approve` («утверждённая страница не проходит validate»), а `design_audit` на фикстуре `package-defects`
  репозитория даёт лишний error R-COV-003 в copy deck `spasibo`. `fixture_gen.py` — не мой файл: правку рецепта я не
  вносил, а проверил её в песочнице (копия `fixture_gen.py` и копия папки фикстур). Посев R-DEBT-002 уже ставит демо-факт
  `company-since-2014` в закрытый copy deck; та же ссылка у слота подвала посевной копии закрывает правило. Правка — одна
  пара в списке `meta` функции `recipe_landing_defects` (текст — §4). С ней: `fixture_gen build --all` проходит (меняет
  только `package-landing-defects/manifest.yaml`), `build --all --check` — совпадает по всем пяти, самопроверка
  `design_audit` на пересобранных фикстурах — 26 OK (14 из 14 посевов, лишних error нет), `package-landing` и
  `package-cabinet` — 0 error. Варианты для оркестратора: (а) эта правка рецепта — рекомендую: шапка фикстуры остаётся
  верной, посевы на месте; (б) подвал — заглушка `[PLACEHOLDER: реквизиты ООО]` с `missing_ids: [legal-details]`, как
  велит норма, но тогда страницу не утвердить, и посевы «закрытого copy deck» (R-COV-002 error, R-DEBT-002 «в закрытом»)
  перестраиваются; (в) отказ от решения 15 — не рекомендую: у copy deck проекта снова молча не проверяются длины и
  обязательные факты (находка 11). До правки рецепта красные: `fixture_gen.py build --all --check` (код 2 — рецепт),
  `design_audit.py --selftest` (проверка «лишних error нет») и строка смоука с ней, `sync_check.py` (строка `fixtures`).
- **R-COV-007 — одно правило пути у обеих утилит.** При отсутствии обоих профилей пути расходились: `canvas_input` —
  `voice.product.yaml`, `design_audit` — `voice.yaml`. Сведено к правилу `design_audit`: путь — `voice.yaml` (он держит
  каналы поверхностей и `scope.product_voice_ref`), кроме случая, когда профиль с каналом поверхности есть, а строки тона
  `projections.tone_of_voice` в нём нет, — тогда путь этого профиля. В общих случаях пути совпадают: нет `voice.yaml`;
  нет канала `product-ui`; канал есть, профиля продукта нет (у `design_audit` — «профиля голоса продукта нет», у
  `canvas_input` — находка, только если и у `voice.yaml` нет строки тона). Пути `design_audit` не менялись: на
  `voice.yaml` держатся шапка `package-landing-defects` и посев SEEDED ключа.
- **Попутные правки в файлах зоны сверх буквы решений:** вид `site-map` у находки `vocab_lint` о карте сайта (был
  `site-brief`); согласование числа в сообщениях `ds_coverage`, `design_audit`, `ds_sync`; хвост у пункта L1 критериев
  сайта и у строки PRE манифеста; этапы советов у паспорта и форм уровня продукта (решение 14 называет валидаторы —
  формы и паспорт тоже валидаторы).

## 4. Для следующих зон
- **Оркестратору — правка рецепта `landing-defects`** (`.claude/skills/design-deep-dive/scripts/maint/fixture_gen.py`,
  функция `recipe_landing_defects`, список `meta`), проверена в песочнице; после неё — `fixture_gen.py build
  package-landing-defects` (пишет `package-landing-defects/manifest.yaml`: у слота подвала — `fact_ids:
  [company-since-2014]`, в записи claims — info COPY-F-EXAMPLE), затем `build --all --check`:

  ```diff
       meta = [("      description: 'Заявка на замер принята. Студия ремонта «Отвес», Нижний Новгород.'\n",
                "      description: 'Заявка на замер принята. Ремонтируем квартиры в Нижнем Новгороде с 2014 года.'\n"),
               ("      og_description: 'Прораб позвонит и договорится о дне замера.'\n      fact_ids: []\n",
  -             "      og_description: 'Прораб позвонит и договорится о дне замера.'\n      fact_ids: [company-since-2014]\n")]
  +             "      og_description: 'Прораб позвонит и договорится о дне замера.'\n      fact_ids: [company-since-2014]\n"),
  +            # footer-legal: факт обязателен (copy-slots.yaml) — закрытый подвал опирается на факт о компании
  +            ("        - {id: a, text: 'Студия ремонта «Отвес», Нижний Новгород', status: assumed, source: ai-self}\n"
  +             "        chosen: a\n        fact_ids: []\n",
  +             "        - {id: a, text: 'Студия ремонта «Отвес», Нижний Новгород', status: assumed, source: ai-self}\n"
  +             "        chosen: a\n        fact_ids: [company-since-2014]\n")]
  ```
  Шапку `LANDING_DEFECTS_HEAD` правка не меняет: посев R-DEBT-002 — тот же демо-факт в закрытом copy deck.
- **Контракт находок не менялся**: поля, тяжести, коды выхода — прежние. Новое в выводе: код copydeck COPY-D-RULES-REF
  (warning; `design_audit` переводит его по умолчанию в R-STRUCT-003 warning с советом «— copy»); значения ключа `ready`
  в `summary.json` — строка статуса или `null`; у `ds_sync` — поле `Change.alias` (внутреннее).
- **Владельцу `tree.py`** (вне зоны): R-SEM-014 «токена space.X нет … (есть: …)» режет список `sorted(self.space)[:12]`
  без хвоста — один вид «и ещё N» по решению 8.

## 5. Тесты и прогоны
- Самопроверки: `canvas_input` 48 OK; `contract` 26 OK; `ready` 26 OK; `ds_sync` 20 OK; `ds_coverage` 30 OK;
  `copydeck` 149 OK, 0 FAIL; `color.py selftest` 5 из 5; `design_audit` на фикстурах репозитория — 25 OK, 1 FAIL
  («лишних error нет»: R-COV-003 в copy deck `spasibo` — §3), на фикстурах с правкой рецепта — 26 OK.
- `fixture_gen.py build package-cabinet-defects package-defects` — пересобрано 3 файла `package-cabinet-defects`,
  `package-defects` без изменений; `build --all --check` — код 2 (рецепт `landing-defects`, §3); с правкой рецепта в
  песочнице — совпадает по всем пяти.
- Смоук: `--only scripts/project` — PASS 29, FAIL 1 (`design_audit.py --selftest`, §3); `scripts/text` — PASS 27;
  `scripts/maint` — PASS 24; `scripts/lib` — PASS 5; `scripts/tests` — PASS 4; XFAIL и XPASS — 0. `--validate` — 18
  списков, 218 строк, 0 ошибок; `--uncovered` — 0.
- `sync_check.py` — код 1: генераторы OK 16, FAIL 1 — `fixtures` (§3); копии и описания — OK. Строка
  `canvas-input-cabinet` (ok 0 и 1) принимает код 1 входа mockup `input-cabinet`.
- Прогоны на свежих сборках (`fixture_project.py build <имя> --out <песочница>`, дата 2026-09-29):
  - `input-landing`, `canvas_input build otves-remont-nn promo --stage wireframe` — код 0, 7 файлов; `check` — код 0,
    **0 error · 4 warning · 6 hint**: R-MAT-003 facts.yaml (draft); R-COV-002 «текстовые слоты плана без текста в copy
    deck — 52: … и ещё 46», совет — дополнить copy deck (каркас во временный файл); R-MAT-003 «тексты не того статуса
    для этапа wireframe (assumed · checked · approved): 2 — lead-form/consent (draft), footer/legal (draft)»; R-REF-003
    «… и ещё 2»; R-DEBT-002 «демо-факты во входе: 10 (… price-from-per-m2 и ещё 4)»; R-COV-001 ×5. Итог `INPUT.md` —
    «вход без ошибок: этап можно публиковать, когда готов его вход по phases.md.»; пробелы — «тексты не того статуса или
    без выбора для этапа wireframe (…) — 2: …», «текстовые слоты плана без текста в copy deck — 52: …; на артборде —
    [PLACEHOLDER]».
  - `input-cabinet`, `canvas_input build otves-office office --stage mockup` — код 1 (вход записан); `check --stage
    mockup` — код 1, **1 error · 1 warning · 0 hint**: R-MAT-012 texts.md «проверка входа: этап mockup берёт только
    approved: строк не того статуса 45 (`checked` — 45) — app.shell.help.link, … и ещё 40», совет «/screen-deep-dive
    otves-office office texts — утверждает владелец продукта»; R-COV-007 warning, путь voice.yaml. Итог `INPUT.md` —
    «этап не публикуется, пока ошибки не закрыты». Ожидание брифа совпало. `contract.py check --stage mockup` — R-MAT-003
    warning, код 0; `canvas_input check --stage wireframe` — 0 error.
  - `cabinet-ds` + живой `tokens.json` (`color-accent-solid` light `#1d4ed8` → `#1e40af`): `ds_sync check` — код 1, 1
    error R-FRESH-001 «правка заказчика на странице артефакта не поднята в токены: --color-accent-solid (color) [light]:
    сборка «#1d4ed8» → на странице «#1e40af» — был алиас {primitive.color.accent.700} — две дороги: роль — литерал в
    color.accent.solid (--write, ссылка на примитив рвётся); примитив — правка пути primitive.color.accent.700 в
    system.tokens.json руками, меняет все ссылки на него: на него же ссылаются color.accent.text»; совет — роль (`--write`),
    примитив (руками), затем контраст пар, `ds_build build otves-office`, публикация ДС. `ds_sync build` без ключа — код 0,
    предложение `/color/accent/solid/$value = {… "hex": "#1e40af"}` с той же нотой, токены не тронуты (md5 тот же);
    `--write` — «дальше — пересчёт контраста пар (…), ds_build build otves-office, публикация ДС». `ds_coverage show` —
    строка заголовка и колонка «где стоит».
  - `package-landing`: `ready build otves-remont-nn promo` — код 0, `not-ready`, единиц 2, готовых 0, источников 10,
    блокеры — как в `runs.md` (home: план proposed, текстов нет, макета нет; spasibo: тексты draft, макета нет), у `home`
    в `open` 9 демо-фактов; `ready check` — 0 находок. Правка источника без build — R-FRESH-006 с новым советом.
  - `package-defects`, `design_audit check` (фикстуры репозитория): `otves-remont-nn` — код 1, **10 error / 18 warning /
    11 hint**: 9 посевов своим правилом и путём (R-SURF-004, R-SURF-001, R-STRUCT-006, R-REF-001, R-REF-003, R-COV-002,
    R-COV-003 plans/spasibo.yaml — совет «— page-plan:spasibo», R-FRESH-006, R-MAT-008) и лишний R-COV-003 copy deck
    spasibo (COPY-D-FACT-REQUIRED, §3); `otves-office` — код 1, **5 error / 5 warning / 0 hint**: R-FRESH-001 ×3
    (DESIGN.md, tokens.json артефакта, system.tokens.css), R-FRESH-003 input/copy.md, R-COV-005 system.yaml; warning —
    R-MAT-010 (совет с `/project-deep-dive` и `— app-brief`), R-FRESH-002 ×2, R-MAT-001, R-COV-007 voice.yaml; R-MAT-003
    ушёл. Сводка: `ready` — promo `not-ready`, cabinet и office `null`; заметки «правила не загружены» нет.
  - То же на фикстурах с правкой рецепта: `otves-remont-nn` — **9 error / 18 warning / 11 hint** (лишнего error нет;
    warning +1 к `runs.md` — R-STRUCT-003 COPY-D-RULES-REF), `otves-office` — **5 error / 5 warning / 0 hint**; 14 из 14
    посевов, лишних error нет.

## 6. Строки смоука
- Не менялись: вызовы утилит те же (`help; run: --selftest` у `canvas_input`, `contract`, `ready`, `design_audit`,
  `ds_sync`, `ds_coverage`, `copydeck` ещё `run: before-after --check`; `color.py` — `run: selftest`).

## 7. Проверка
- Длина строк в правленых местах — до 120 знаков (у `copydeck.py` свой стиль длинных строк, правка по нему).
- Следы в коде зоны (`kimi|K3|gemini|qwen|gpt-|Р\d|Ф\d`, «волна», «агентом», `99-raw`, слова сравнения с прошлым) —
  в добавленных строках 0; во всём тексте файлов — только `K3` пункта критериев лендинга (id группы K, данные).
- Ключей, сети и трат нет; платных вызовов и `--live` не было.
- YAML манифестов фикстур разбирается (сборщик и его самопроверка); схем зона не меняла.
- refcheck по пересобранным md фикстуры (`INPUT.md`, `contract.md`, `copy.md`): «битые» — пути демо-проекта
  docs/projects/otves-office/…, которого в репозитории нет по замыслу фикстуры; следов 0.
- Прочитано глазами: `runs.md` целиком, брифы, места правок и места вызовов (`design_audit.fresh_input`, рецепты
  `fixture_gen.py`, `sync.yaml`, самопроверки), шапки манифестов фикстур кабинета и лендинга, норма `footer-legal`
  `copy-slots.yaml`, пример фактов фикстуры.

## 8. Открыто и не прочитано
- Открыто: правка рецепта `landing-defects` (§3, §4) — у оркестратора; до неё красные `fixture_gen --check`,
  `design_audit --selftest`, `sync_check` (строка `fixtures`). `tree.py` R-SEM-014 — хвост списка (владелец зоны
  экранов). `ready show` печатает хвост блокеров отдельной строкой «… и ещё N» — вывод команды, не сообщение находки,
  оставлен.
- Не прочитано: `KEY*.md` (по заданию); `CHAIN.md` — начало и последние записи (формат и шаг 11), не целиком; файлы
  `research/design-build/phase-4/inputs/in-drafts/` — не читались.

## Для текстов
Что изменилось в поведении и выводе — чтобы выправить тексты скилла и ключ:
- **Гейт текстов кабинета.** `canvas_input check` кабинета на входе `mockup` при строках `texts.md` не `approved` —
  R-MAT-012 `error` («проверка входа: этап mockup берёт только approved: строк не того статуса N (…) — … и ещё N»), код 1,
  итог «этап не публикуется»; вход `build` всё равно пишет. R-MAT-003 у `canvas_input` — только вайрфрейм: тексты copy
  deck и факты. `contract.py check` держит R-MAT-003 `warning` (отчёт контракта). Места: `references/phases.md` § 4
  «Второй вход», § 6 `canvas-input` и `mockup`; `docs/projects/_template/screens/README.md` § «Что слой отдаёт макету»;
  `references/claude-design.md` § 6; `scripts/README.md` (строки `canvas_input`, `contract`);
  `design-audit/references/rules.md` R-MAT-012 (добавить строки `texts.md` кабинета на макете) и R-MAT-003.
- **Итог `INPUT.md`.** Без ошибок — «вход без ошибок: этап можно публиковать, когда готов его вход по phases.md», у
  `mockup` — «(принятый вайрфрейм или его пропуск, ДС в холсте)».
- **Пробелы и сообщения входа.** «текстовые слоты плана без текста в copy deck — N: …» (R-COV-002 и пробел), «тексты не
  того статуса или без выбора для этапа … — N: …», «плана ассетов нет — медиа-слоты на артборде заглушкой placeholder:
  N» и «медиа-слоты страницы без плана ассетов — N» (R-COV-004); голос — «голоса поверхности нет: строки тона во входе
  нет; тексты во входе — из texts.md (или copy deck), сверка с голосом — после профиля голоса (этап meaning)».
- **Совет R-COV-002.** Готовый copy deck — «этап copy: добавить слоты плана в copy deck (каркас недостающих —
  copydeck.py skeleton <план> -o <временный файл>; готовый copy deck не перезаписывать)»; нет copy deck — «(каркас из
  плана — copydeck.py skeleton)». В `references/phases.md` § `copy` стоит сказать, как дополнить готовый copy deck
  слотами каркаса (утилиты слияния нет — перенос слотов руками из временного файла).
- **R-COV-007.** У `canvas_input` — `warning` на всех этапах; путь — `voice.yaml`, у профиля с каналом, но без строки
  тона — путь профиля; `design_audit` — прежний. `scripts/README.md`, `design-audit/references/rules.md` R-COV-007.
- **Хвост списков.** Везде «… и ещё N» (без «(+N)» и голого «…»).
- **`ready`.** Совет R-FRESH-006 — «на этапе package, после отчёта /design-audit (его error закрывает или принимает
  заказчик)»; `--help` — где стоят факты единицы (`open` · `blockers`), см. §2 № 16.
- **`ds_sync`.** Сообщение R-FRESH-001 — «правка заказчика на странице артефакта не поднята в токены: …»; нота алиаса и
  совет называют обе дороги и общий хвост (контраст пар, `ds_build build`, публикация ДС); справка — расхождение, где
  новее токены, сходится публикацией ДС. `references/claude-design.md` § «Правки токенов» уже говорит о дороге
  «примитив»; `scripts/README.md` (строка `ds_sync`), `rules.md` R-FRESH-001 (смысл у `ds_sync`).
- **`ds_coverage show`.** Строка заголовка; колонки — поверхность, тип, ключ, компонент, итог, где стоит.
  `scripts/README.md`, `docs/projects/_template/design/README.md` § «Покрытие компонентов», если колонки названы там.
- **`lib/color.py`.** Справка без истории и мёртвого пути; вызов — `python3 scripts/lib/color.py contrast …` из папки
  скилла.
- **`design_audit`.** Ключ `ready` сводки — статус манифеста (`ready` · `partial` · `not-ready`, «—» без статуса, `null`
  без манифеста); ключи сводки и смысл «код 2» в `called` — в `--help`; советы с этапом (SB-* → `brief`, SM-* →
  `site-map`, PL-* → `page-plan:<страница>`, паспорт → `art-direction` · `passport-icons`, формы → `brand` ·
  `design-system` · `app-brief`); R-MAT-010 — исполнитель и этап. Места: `design-audit/SKILL.md` § «Два прогона» и
  «Формат отчёта» (состав сводки, ключ `ready`), `scripts/README.md` (строка `design_audit`).
- **`copydeck.py`.** Новый код COPY-D-RULES-REF (warning) — битая `copy_slots_ref`, правила — из базы; заметка
  «правила не загружены» — только если файла нет и в базе. У copy deck проекта с ссылкой примера базы работают длины
  слотов и обязательные факты: у закрытых страниц возможны новые error (COPY-D-FACT-REQUIRED → R-COV-003). Места:
  `design-audit/SKILL.md` (заметки сводки), `rules.md` R-STRUCT-003 (COPY-D-RULES-REF — warning формы copy deck),
  `scripts/README.md` (строка `copydeck`), ключ сценария «пакет» (§5).
- **Ключ проверки.** Сценарий 1 — итог и пробелы по §5; сценарий 2 — R-MAT-012 error, код 1, R-COV-007 warning
  (voice.yaml); сценарий 3 — сообщение и совет R-FRESH-001, заголовок `show`; сценарий 4 — совет R-FRESH-006, `ready` в
  сводке, у `otves-office` нет R-MAT-003, у `otves-remont-nn` +1 warning COPY-D-RULES-REF и (до правки рецепта) лишний
  error R-COV-003.

## 9. Запись для CHAIN
```
## <NN>. FX — пакет правок по проверке сценариев (29.09, время и токены — по уведомлению)
- Сделано: правки canvas_input (+114/−37), contract (+6/−2), ready (+21/−3), design_audit (+73/−23), ds_sync
  (+52/−16), ds_coverage (+17/−5), lib/color (+21/−14), text/copydeck (+23/−8); манифесты package-cabinet (45 строк
  texts.md → approved) и input-cabinet; пересобран вход package-cabinet-defects. Решения 1–16 — в коде (отчёт §2):
  гейт текстов кабинета — R-MAT-012 error на макете; итог входа «вход без ошибок: …»; R-COV-007 warning с путём как у
  design_audit; хвост «и ещё N»; советы R-FRESH-006, R-COV-002, ds_sync (две дороги и хвост), этапы советов аудита;
  ключ ready сводки — статус манифеста; битая copy_slots_ref — COPY-D-RULES-REF и правила базы.
- Тесты: самопроверки правленых утилит зелёные (design_audit — 25/26 на фикстурах репозитория, 26/26 с правкой
  рецепта); смоук project PASS 29 / FAIL 1 (design_audit), text 27, maint 24, lib 5, tests 4; --validate и --uncovered
  чисто; sync_check — FAIL строки fixtures; прогоны сценариев — отчёт §5, ожидания брифа совпали, кроме лишнего error в
  package-defects.
- Отступления: решение 15 открыло дефект данных фикстуры (подвал footer-legal без факта в закрытом copy deck spasibo) —
  рецепт landing-defects падает на approve; правка рецепта в fixture_gen.py (не мой файл) проверена в песочнице и
  приложена (отчёт §4). R-COV-007: путь сведён к правилу design_audit.
- Стыки: оркестратору — правка рецепта и тексты по разделу «Для текстов»; владельцу tree.py — хвост R-SEM-014.
- Открыто: правка рецепта landing-defects (до неё красные fixture_gen --check, design_audit --selftest, sync_check).
- Не прочитано: KEY*.md (по заданию), in-drafts.
```
