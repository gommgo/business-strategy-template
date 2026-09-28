# Ф8 — план адаптации кода

Ф8 делает скилл технически рабочим (`../PLAN.md § Готовность по фазам`): утилиты по файлам проекта `scripts/project/`
(H10), код баз под схемы v1 и решения Ф4–Ф7, судья и разбор картинок на Opus, вход холста вместо веток прежнего
исполнителя макета, жанр «интерфейс» у линтера, демо-факты, окружение с установкой, проверки обслуживания в
`scripts/maint/` (Р165). Смоук, тесты и самопроверки зелёные, утилиты прогнаны на примерах баз. Пилоты — Ф9, уборка базы
и журнала — Ф10.

Входы: план сборки `../PLAN.md` («Ф8», «Готовность по фазам», «Риски») и бэклог `../STATE.md § Дальше`; спецификация
`../phase-6/spec/` — T4 §1 H3, H4, H10, H11, G1–G6, §6; T1 B5, B9, §4.3, §6; T2a C1, C4–C8, D2, §4.2–§4.5, §6; T2b E1,
E2, E7, E8, E10, §4.4–§4.5, §6; T3 D5, F6–F9, F13, §4.3–§4.5, §6; 165 действий Ф4 с фазой Ф8 — `../phase-4/actions.tsv`,
их место и смысл — `../phase-4/nodes/*.tsv`; части Ф8 действий сверки Ф6 — `../phase-6/ACTIONS-SPEC.tsv`; отчёты зон Ф7
`../phase-7/reports/` (§3, §4, §6) и строки Р168–Р181. Действия по зонам — `ZONES.tsv` этой папки: 282 строки — 165
действий Ф4; 25 пунктов H10; 26 — «Ф8 от T…» и открытое спецификаций; 11 — части Ф8 действий сверки Ф6; 36 — отчёты Ф7;
9 — бэклог STATE; 7 — окружение; 2 — решения журнала; 1 — пакет закрытий. У каждой строки — зона или причина «вне» (17
строк «вне», все с причиной). Что прочитано, что нет, и спорные места — `README-plan-notes.md`; спорные места решены
оркестратором (Р183), ответы заказчика на §10 — строкой DECISIONS в начале Ф8.

Объём: ≈ 15–23 тыс. строк кода, данных и тестов; ≈ 75 новых файлов (≈ 30 из них — списки смоука и файлы фикстур) и
≈ 130 правок. Почти половина объёма — новые утилиты `project/` и `claude-design/`. 17 зон агентов, шаг оркестратора,
шаг на машине заказчика и проверка; ≈ 16–20 часов работы — три облачные сессии и одна локальная (§1).

Пути: `scripts/…`, `kb/…`, `references/…`, `assets/…` — от `.claude/skills/design-deep-dive/`; `_template/` —
`docs/projects/_template/`; «узел» — строка `../phase-4/nodes/*.tsv` по id.

## 1. Способ

- **Как Ф7** (Р164–Р167), если заказчик подтвердит (§10, вопрос 1): оркестратор ведёт фазу без остановок, после шага —
  короткий итог в чат; вопрос заказчику — только если шаг задевает его решения; структурные решения — оркестратор,
  строкой DECISIONS.
- **Парами.** Одновременно — не больше двух агентов, файлы пары не пересекаются (списки §2, общие файлы — правила §4).
  Следующая пара — после приёмки обеих зон.
- **Агенты** — Claude Opus 5.5 (`model: opus`), бюджет контекста ≈ 700 тыс. Бриф — общий бриф кода
  `briefs/COMMON.md` (пишет оркестратор до шага 1 по §4–§5) и бриф зоны перед её парой: разделы зоны из §2, уроки
  `CHAIN.md` Ф8 и ответы оркестратора на спорные места. Агент сам гоняет тесты, смоук и самопроверки в окружении
  `$DDD_HOME`; не делает: git, платные вызовы и `--live`, запись вне файлов зоны, `$DDD_HOME` и scratchpad.
- **Сессии.** Шаг 0 каждой облачной сессии — окружение (§4, «Окружение облака»): облако не хранит `$DDD_HOME` между
  сессиями. Шаг кода длиннее шага текста Ф7: агент ≈ 60–90 мин, приёмка со смоуком и прогонами ≈ 20–30 мин — шаг
  ≈ 1,5–2 ч. Предложение: 1-я облачная сессия — шаги 1–4 (8 агентов); 2-я — шаги 5–8 (8 агентов); 3-я — шаг 9, шаг
  оркестратора и проверка Ф8 (§6); локальная сессия на машине заказчика (МЗ) — после шага 8 или вместе с 3-й. Облачная
  сессия ведёт шаги без остановок, пока не кончится лимит; обрыв — следующая сессия продолжает с первого непринятого шага
  по файлам ветки (Р119).
- **Push** — перед парой (брифы), сразу после каждого агента (коммит «на приёмке»), после каждой приёмки (строка
  текущего шага в STATE). Пока агент работает — страховочные проверки `send_later` каждые 30 минут и коммит «черновик,
  агент в работе».

## 2. Зоны

Действия зоны — строки `ZONES.tsv` с её кодом в колонке `zone` (у действия может быть несколько зон — каждая делает свою
часть, её называет `note`). Везде: справка своих файлов (`--help`, докстринг, README домена) — о текущем поведении
(BL-7); следы прежнего исполнителя макета в своих файлах — 0 (DEC-kimi); строки смоука — в своём списке
`scripts/tests/smoke/<файл>.tsv`.

### C1 — основа: пути, окружение, смоук, фикстуры (шаг 1; ≈ 450–750 строк)
- **Файлы:** `scripts/lib/kbpaths.py` (домен `project`, переменная репозитория); новый `scripts/lib/docpaths.py`;
  `scripts/install.sh`, `requirements.txt`, `package.json` (если решение по линтерам формата — «ставить»);
  `scripts/tests/smoke.py`, `smoke-list.tsv` → списки `scripts/tests/smoke/*.tsv` (по папке; у `project/` — по зоне:
  `project-screens`, `-ds`, `-demo`, `-canvas`, `-package`); новый `scripts/tests/fixture_project.py`; `.gitignore`
  скилла — если появятся новые выходы.
- **Что делает:** корень репозитория для утилит `project/` — репозиторий скилла, `--repo` или переменная окружения
  (код-репо указывает соседний чекаут `../strategy`, тесты — временную копию); установка под Python ≥ 3.12 (выбор
  интерпретатора, шапка требований), совместимость с браузерами образа (версия Playwright под `PLAYWRIGHT_BROWSERS_PATH`
  ключом установки), ffmpeg без системной установки (статическая сборка с sha256 — или шаг 0 сессии), адреса загрузки
  (ENV-7), `--from` старых `bin/` и `models/`, Blender Lab — по желанию, без mcp-for-blender (CN-115), `DDD_BRAVE`; смоук
  читает все списки папки; сборщик демо-проекта во временную папку по манифесту фикстуры (слои: примеры баз и свои
  файлы фикстуры, копий примеров нет).
- **Действия:** GT-03 (часть), CN-115; H10-docpaths, H10-smoke, T4-G4, T2a-designmd (решение), BL-5, BL-6, ENV-1…ENV-3,
  ENV-5…ENV-7, DEC-kimi — 15 строк.
- **Входы:** T4 H10 (абзац о `docpaths`), G4; Р53, Р59, Р87, Р90; §4 и `README-plan-notes.md` («Окружение облака»).
- **Среда:** облако; бинарники и модели с `--from` — МЗ.

### C2 — ui, ux и проверки экрана (шаг 1; ≈ 700–1 100)
- **Файлы:** `scripts/ui/ui_audit.py`, `measure_ui.py`, `build_reference_tokens.py`; новый `scripts/ui/data/` (таблица
  профиля `marketing`; порог кеглей — одно место для скрипта ui 11/04 §3 и `mockup_checks.py`);
  `scripts/ux/checklist_export.py` и новый генератор словаря и матрицы состояний (образец — `checklist_export.py`); kb:
  производный YAML словаря S01–S24 и матрицы в `kb/ux/06-feedback-states-motion/`, перегенерация
  `kb/ux/12-evaluation-checklists/master-checklist.yaml`, скрипт m11 в ui 11/04 §3, пример
  `kb/ui/14-recipes/examples/03-dashboard.html` и `app.css`, `kb/common/components.yaml` — `screen_states` ссылкой на
  YAML (если нужно).
- **Что делает:** `ui_audit` — скрытое вне I1 и H, текст над медиа — WARN F83, полировка E1 и E2 только в профиле
  `marketing`, таблица профиля — данными, набор ширин из файла, тач 44, шкала отступов, кегли и значения — из токенов ДС
  проекта, длина строки в знаках, потолок длительностей из пресета, эмодзи без «©» и «↔», находка несёт id приметы,
  выравнивание соседних карточек (дашборд с браком — 0 FAIL сегодня, BL-1); `measure_ui` — порог шапки по поверхности;
  `build_reference_tokens` — `size.control.lg` на таче ≥ 44, без `landing-h1`; YAML словаря и матрицы — генератором из
  md с `--check` (ST-26); перегенерация мастер-чек-листа.
- **Действия:** 22 из 165 (GT-39, GT-40, CM-02, CM-17, ST-01, ST-10, ST-26, NU-01, NU-09, NU-10, NU-16, NU-18, NU-20,
  NU-24, VI-01, VI-12, VI-15, VI-22, VI-23, VI-30, VI-43, VI-44) и BL-1, BL-4, DEC-kimi — 25.
- **Входы:** узлы 03-GT, 04-CM, 05-ST (с `05-ST.md` §2.1), 06-NU, 08-VI; ux 06/01 §2–§3; `kb/common/components.yaml`,
  `acceptance-widths.yaml`; `effects.yaml#glass-panel`; `../phase-3/calibration/REPORT.md` §8 п. 1; Р49, Р125.
- **Среда:** облако (Playwright и Chromium образа — §4).

### C3 — project: экраны (шаг 2; ≈ 1 400–2 000)
- **Файлы:** новые `scripts/project/tree.py`, `states.py`, `screen_map.py`, `normalize.py`; фикстура кабинета в
  `scripts/tests/fixtures/` (продукт, interface, экраны, `map.md`, `texts.md` — иллюстрация, `example: true` в машинных
  файлах); `tests/smoke/project-screens.tsv`.
- **Что делает:** разбор компактной YAML-нотации дерева по грамматике README экранов (узлы, закрытый список атрибутов,
  `ui:` и части — по словарю и расширениям карты решений, `text:` — ключ реестра, `gap` — имя `space.*` ДС); наборы
  состояний экрана и блока (ST-05, ST-10, ST-12; приоритет — правило канона, а не поле экрана); генерируемые разделы
  свода `map.md` и проверки RT-01…RT-08; приведение заполненного проекта к канону — механические правки в терминах
  канона (тип по `aka` словаря, ключи состояний по таблице README mobile, литерал → ключ `texts.md`, атрибуты), смысловые
  поля остаются пустыми для владельца; формат находок для `design_audit` (§4).
- **Действия:** ST-01 (часть), ST-05, ST-06, ST-07, ST-12, ST-15, ST-16, NU-17; H10-screens, T3-scripts, F7-Z2-1,
  F7-Z7b-2, ENV-6 — 13.
- **Входы:** T3 F6, F7, F13, §4.3–§4.5 (таблица соответствий — спецификация нормализатора, в код не переносится как
  «прежнее»); `_template/screens/README.md` и формы `screen`, `block`, `shell`, `flow`, `map`, `texts`;
  `screen-audit/references/rules.md` (R-RT, R-SEM-011, R-STRUCT); отчёт Z7b §3–§6; Р124, Р125, Р179; YAML состояний C2.
- **Среда:** облако.

### C4 — creative: данные и валидаторы подачи (шаг 2; ≈ 700–1 100)
- **Файлы:** `scripts/creative/spec_check.py`, `ad_check.py`, `validate_stack.py`, `registry_check.py`,
  `marketing_audit.py`, README; kb creative: `01-creative-direction/ambition-levels.yaml`; в
  `09-ai-execution-evaluation/` — `art-direction.v1.schema.json`, `treatment.schema.json`, `motion-spec.schema.json`,
  `block-treatments.yaml`; `06-effects-catalog/effects.yaml`, `07-stack-implementation/stack.yaml`,
  `04-visual-language/marketing-tokens.json`, примеры арт-дирекции и подачи; `tests/smoke/creative.tsv`. Не трогает
  `effect-gates.yaml`, `motion_check.py` (C14), `refs_client.py` (C9), реестр клише (Ф10).
- **Что делает:** числа уровней — только в `ambition-levels.yaml`: пики, акценты, петли в зоне с телефоном, свойства,
  хроматические, доля и полосы цены, `budgets.effects` (видео, ключ wasm без числа — GT-22 открыт), ссылки на ворота 3D и
  профиль site; код читает YAML, а не константы; `x-canvas-map` в `treatment`, `motion-spec`, `maps_to` без Kimi — первая
  зона-писатель, форма ключа — §4; `art-direction.v1`: `$defs/reference` с `values`, `source`, `captured`,
  `lifecycle.history` необязательно, `executor_block` и `handoff.kimi` сняты; `ad_check.py FILE`; `spec_check.py` на
  файлах проекта; валидаторы на v1, чтение соседей через kbpaths; `registry_check` сверяет `k3_allow` с `checks` и
  статусы; `marketing_audit` — id приметы, тач 44, длительности из токенов, порог записи, доля полосы по кадру страницы.
- **Действия:** 27 из 165 (TR-14, TR-23, TR-24, TR-44, GT-07, GT-08, GT-11, GT-20, GT-21, GT-22, GT-24, GT-25, GT-26,
  GT-28, NU-01, NU-09, NU-26, NU-33, NU-34, NU-36, VI-01, VI-03, VI-08, VI-24, VI-34, CN-65, CN-66) и 13 — 40.
- **Входы:** узлы 02-TR, 03-GT, 06-NU, 08-VI, 10-CN; T2a C6–C8, §4.4 п. 1, §4.5 «Ф8 от T2a»; T2b E1 (таблица
  проекции), E7; Р40, Р44, Р151.
- **Среда:** облако.

### C5 — project: ДС (шаг 3; ≈ 1 200–1 800)
- **Файлы:** новые `scripts/project/ds_coverage.py`, `ds_build.py`, `ds_sync.py`; новые схемы форм `brand` (из
  `site-brief $defs`), `system`, `app-brief` — в `kb/common/` (Р183) со строками таблицы файлов `kb/common/README.md`;
  шапка `kb/common/components.yaml` (имя скрипта покрытия); фикстура ДС — слой из примера
  `kb/claude-design/05-design-artifacts/example/design-system/`; `tests/smoke/project-ds.tsv`. Фикстура кабинета C3 —
  только чтение, недостающее — своим слоем.
- **Что делает:** покрытие (Р29): типы `ui:` stable-экранов и слотов действия и форм планов → `components` и
  `extensions` карты решений → компоненты артефакта; обязательные и объявленные состояния; у расширения — `keyboard` и
  `text_roles`; производные ДС из DTCG — `system.tokens.css`, передняя часть `DESIGN.md`, `tokens.json` артефакта
  списками, README из `DESIGN.md`; основной текст на узкой ширине (NU-15); проверка формата DTCG (спорное 3); обратная
  синхронизация — «имя ДС → путь DTCG», сверка живого `tokens.json` с собранным.
- **Действия:** CM-01, CM-04, CM-06, CM-15, NU-15; H10-ds_coverage, H10-ds_build_sync, H10-schemas-design, T2a-brand,
  T2a-ds, F7-Z6-2, F7-Z6-5, F7-Z6-10, ENV-6 — 14.
- **Входы:** T2a C1, C4, C5, §4.2 (формы без схем), §4.4 п. 7–11; `_template/design/README.md § ДС`, `§ Производные`;
  формы `_template/design/_template/{system,app-brief,brand}.yaml`; `components.yaml` (шапка, `project_extension`);
  ui 09/04; cd 05/01 §3–§5; Р29, Р63, Р100.
- **Среда:** облако.

### C6 — project: демо-набор и контракт генерации (шаг 3; ≈ 700–1 000)
- **Файлы:** новые `scripts/project/demo_data.py`, `contract.py`; слой фикстуры кабинета — своим слоем;
  `tests/smoke/project-demo.tsv`.
- **Что делает:** демо-набор `example: true` из глоссария объектов, объёмов коллекций и крайних случаев (ux 06/01 §6.2,
  ux 13/04 §12); контракт генерации — 10 разделов ux 11/04 §7.3 с разделом на экран (обязательные состояния — S-id из
  `states.py`, ST-02), у раздела — источник, чтобы провал на макете вёл в слой проекта.
- **Действия:** H10-demo_contract, T3-scripts, S6-ST-02, F7-Z2-1 — 4 строки; объём — два модуля.
- **Входы:** T3 F8, F9; `_template/screens/README.md § Что слой отдаёт макету`; формы `object.md`, `action.md`, `block.md`
  (`volume`); `claude-design.md § Вход холста` (кабинет); Р69.
- **Среда:** облако.

### C7 — site: бриф, план, словарь, валидатор, профиль (шаг 4; ≈ 700–1 000)
- **Файлы:** `scripts/site/site_validate.py`, `vocab_lint.py`, `build_profile.py`, README (своя часть); kb site: в
  `10-playbooks-contracts/schemas/` — `site-brief`, `page-plan`, `site-map` (`.schema.json`); `02-site-types/vocabulary.yaml`,
  `crosswalk.tsv`; `08-legal-trust-a11y/legal-requirements.yaml`; `09-ai-generation-evaluation/ux-marketing-profile.tsv`
  (перегенерация); примеры `10-playbooks-contracts/examples/*/` (бриф, планы, карта); `tests/smoke/site.tsv`. Не трогает:
  `page_gates.py`, `page_anatomy.py`, `budgets.yaml`, `page-gates.yaml` (C14), `plan_to_assets.py` и
  `asset-plan.home.yaml` (C9), `facts.yaml` примеров (C8).
- **Что делает:** `site-brief` v1 — блок `themes`, `brand.ref` на схему `brand` (C5), значения референсов,
  `x-canvas-map` по таблице T2b E1, ссылка `x-kimi-projection` снята; `page-plan` — `x-canvas-map`, умолчание
  `3d[].load` (GT-09); `site_validate` — темы и бренд, `recipe:` плана существует, уровни из `ambition-levels.yaml`,
  `x-effect-levels` подачи, вызов `spec_check.py plan`, кто читает схемы v0 и v0.9 (CN-42); `vocab_lint` — таблица
  соответствий; `build_profile` — сверка с версией чек-листа ux и перегенерация профиля отдельным коммитом (Р112);
  `email-sender-name` в словаре и `crosswalk.tsv`; строки права (LR-RU).
- **Действия:** 18 из 165 (TR-07, TR-22, TR-25, TR-37, TR-44, TR-48, TR-53, TR-57, GT-09, GT-24, GT-25, GT-29, GT-41,
  NU-09, NU-23, JU-04, CN-42, CN-61) и 10 — 28.
- **Входы:** узлы 02-TR, 03-GT, 06-NU, 09-JU, 10-CN; T1 B5, B9, §4.2, §6; T2a C1, C6; T2b E1 (таблица сайта); отчёт Z1
  §3 п. 1; Р112, Р169.
- **Среда:** облако.

### C8 — text: copy deck, факты, смысл, голос (шаг 4; ≈ 1 300–1 900)
- **Файлы:** `scripts/text/copydeck.py`, `claims_check.py`, `validate_meaning.py`, `validate_voice.py`,
  `validate_facts.py`, `validate_any.py`, `make_skeleton.py`, `chain_inputs.py`, `check_intake.py`, `run_checks.py`,
  README (своя часть); kb text: `10-templates-recipes/copy-deck.schema.json`; в `02-strategy-messaging/` — схемы
  `facts`, `meaning`, `message-hierarchy`, `voc` (`.schema.yaml`); `05-voice-editorial/voice.schema.yaml`;
  `08-russian-legal-typography/claims-rules.yaml`; примеры copy deck и фактов text, `facts.yaml` примеров site v1;
  `tests/smoke/text.tsv`.
- **Что делает:** статус `assumed` (перечень, `x-status-rules`, код); `approve` чистит журнал правки и отклонённые
  варианты, `validate` их не требует (B9); каркас copy deck из плана и сверка стыка (`make_skeleton` — только без плана);
  `block` — против `blocks.yaml`; ядро первого экрана без `hero`; `use` и демо-факты `example: true` — `validate --final`
  и `claims_check` их не пропускают; числительные словами (TX-28); голос продукта — ситуации интерфейса и профиль
  `voice: product` (TX-31); `x-canvas-map` text — перенацелить, ключи `publish_filter`, `never_claim_md`, `copy_md`
  сохранить; `export-kimi` и `import-kimi` → выгрузка во вход холста (`copy.md`, `facts.md`, «Нельзя утверждать») и приём
  `copy.md` с холста вариантом `source: customer`; `verify-page`, `apply-selection`; калибровки К18–К30 с самопроверкой;
  id — словарь site через kbpaths.
- **Действия:** 18 из 165 (TR-03, TR-04, TR-13, TR-16, TR-17, TR-18, TR-19, TR-20, TR-44, TR-54, TX-28, TX-31, CN-47,
  CN-52, CN-60, CN-61, CN-62, CN-63) и 10 — 28.
- **Входы:** узлы 02-TR, 07-TX, 10-CN; T1 B6, B7, B9, §4.2; T2b E1 (факты, тексты), E10; T3 D5, F9;
  `kb/text/99-raw/reports/wave4-X-audit.md` §7 (К1–К31 — читать до уборки `99-raw`); Р34, Р69, Р101, Р157, Р158, Р169.
- **Среда:** облако.

### C9 — план ассетов, инвентарь и референсы (шаг 5; ≈ 500–800)
- **Файлы:** `scripts/site/plan_to_assets.py`, `scripts/ai-media/asset_inventory.py`, `scripts/creative/refs_client.py`;
  kb: `ai-media/05-prompting/asset-spec.schema.json`, новая схема плана ассетов рядом с каноном формата (ai-media 01/01
  §8), примеры `kb/site/10-playbooks-contracts/examples/*/asset-plan.home.yaml`; строки своих утилит в README и списках
  смоука site, ai-media, creative.
- **Что делает:** схема плана ассетов — `status` и `approval`, `key`, дорога 3D, `source` с `render`, `task_codes` или
  `recipe:`, `ai_fit`; id — словарь site и проекция `crosswalk.tsv`; `plan_to_assets` строит и проверяет план на файлах
  проекта (и на 10 новых типах страниц); `asset-spec` — `page_type` словаря; `asset_inventory` — без маскировки
  автоматизации, с признаками GSAP по рантайму; `refs_client` — без превью работ площадок, экспорт без `author`.
- **Действия:** 8 из 165 (TR-03, TR-07, TR-40, TR-41, VI-56, VI-58, CN-95, CN-96 — части по файлам) и 6 — 14.
- **Входы:** ai-media 01/01 §8; T2a D2, §4.2 (строка плана ассетов), §4.3; узлы 02-TR, 08-VI, 10-CN; отчёт Z1 §3 п. 3;
  Р40, Р151, Р163.
- **Среда:** облако; самопроверка `refs_client` без Brave — ожидаемое падение, Brave — МЗ.

### C10 — claude-design: копии холста и проверки макета (шаг 5; ≈ 1 200–1 800)
- **Файлы:** `scripts/claude-design/mockup_checks.py`, `kit/shot.py`; новые `claude-design/dc_to_html.py`,
  `copies_compare.py`, `dc_texts.py`, `literal_tokens.py`, `kit/kit_manifest.py`; `stand_page.py`, `shot_v3.py`,
  `lang_check.py` — только следы прежнего исполнителя и справка; `tests/smoke/claude-design.tsv`. Фикстура — исходники
  холста и ДС `kb/claude-design/05-design-artifacts/example/` (восемь артбордов, `canvas.json`, артефакт ДС).
- **Что делает:** статичная копия артборда — перевод исходника по правилу cd 05/02 §5; сверка адаптивной копии со
  статичной (тексты дословно, геометрия в допуске); обратный разбор текстов исходника в формат `copy.md` (его принимает
  C8); «литерал ∈ значений токенов ДС» (Р63); манифест `kit.json` из `acceptance-widths.yaml` (артборды и копии × ширины
  × темы, класс экрана, границы ДС ± 1 px); `mockup_checks` — без K3-специфики и сторожа потока прежнего исполнителя,
  входы таблицами или YAML, источник у строк фактов, F-NUMBERS с единицей и объектом, формы по `lead-forms.yaml`, пороги
  кеглей и шапки по поверхности, признаки бенто, орбиты, стрелок и вариации карточек, id приметы в находке, кластер — в
  единице домена.
- **Действия:** 12 из 165 (GT-42, NU-01, NU-05, VI-01, VI-03, VI-04, VI-10, VI-12, VI-17, VI-26, VI-29, VI-43) и 11 — 23.
- **Входы:** T2b E1 (раскладка `input/`), E2, E8, E10, §4.4 п. 8–9; `claude-design.md § HTML-копии и kit`, `§ Приёмка`;
  cd 05/01 §3, cd 05/02 §5, cd 06/04 §3–§9, cd 06/05; `common/tells.yaml` (`checks`, `domains`), `acceptance-widths.yaml`;
  узлы 06-NU, 08-VI; Р28, Р46, Р63, Р76 п. 27.
- **Среда:** облако.

### C11 — project: вход холста и критерии приёмки (шаг 6; ≈ 1 300–2 000)
- **Файлы:** новый `scripts/project/canvas_input.py`; колонка «артборды» таблицы одобрения формы
  `_template/design/_template/REVIEW.md` (Р183); фикстуры лендинга и многостраничника — манифесты слоёв из примеров баз
  (`site/10-playbooks-contracts/examples/lead-services-otves`, `corporate-b2b-stalkon`, copy deck text, подача и
  движение creative, ДС cd) и недостающие файлы продукта; `tests/smoke/project-canvas.tsv`.
- **Что делает:** `build <slug> <surface> --stage directions|wireframe|mockup|motion` — `input/` под этап: `INPUT.md`
  (пути, статусы и отпечатки источников, «Going with», пробелы, итог проверки), `brief.yaml` по `x-canvas-map`
  владельцев; сайт — `pages/<page-id>/{page.yaml, copy.md, assets.md, motion.md}`; кабинет — `contract.md`, `copy.md` из
  `texts.md`, `demo-data.json` (C6), `assets.md`; тексты — по статусу этапа; `build.perf` — через `page_gates.py
  --resolve`; `ACCEPTANCE.md` по роду и уровню (A–H с поправками, I–L сайта с местом проверки, состояния и класс экрана
  кабинета, среда); `check` — проверка входа до публикации (поле без правила, остатки шаблона, факты, тексты нужного
  статуса, ассеты, референсы, PRE кабинета, `spec_check.py spec` у движения), находки R-FRESH-002…004 и R-MAT-012 для
  `design_audit`; соответствие «артборд → страница» для отпечатков одобрения (форма — в брифе, F7-Z5b-1).
- **Действия:** 4 из 165 (TR-22, TR-44, GT-42, NU-37 — сборщик) и 11 — 15.
- **Входы:** T2b E1, E2, E7, §3, §4.1–§4.4; `claude-design.md § Вход холста`, `§ Задание по этапу`, `§ Приёмка`;
  `phases.md § canvas-input`; `_template/design/README.md § Холст`, форма `ARTIFACTS.md` (условия холста); отчёты Z5b §6,
  Z6 §6; Р101, Р157, Р158.
- **Среда:** облако.

### C12 — судья и паспорт визуала на Opus (шаг 6; ≈ 700–1 100)
- **Файлы:** `scripts/ai-media/asset_audit.py` (судья, `budget.image`), `tests/test_asset_audit.py`, `stand_run.py`,
  `mp_client.py`, `vlm_to_dna.py`, README (своя часть); kb: `ai-media/11-evaluation-qa/thresholds.yaml` (группа `judge`,
  `budget.image`), `11-evaluation-qa/rubrics/*.rubric.json` (12 рубрик), `rubrics/judge-response.schema.json` (если
  нужно), `06-art-direction-consistency/visual-dna.schema.json`; `kb/common/judge.md §6` (строка ключей); строки смоука
  ai-media своих утилит. `assets/calibration/` — только чтение.
- **Что делает:** `judge-jobs` пишет пакет для отдельной сессии Opus — агента `design-judge`: кадры вслепую, вопросы
  рубрики, формат ответа по `judge-response.schema.json`, оба порядка пары и повторы — отдельными заданиями, ключ слепоты
  вне пакета; задания калибровки — из `assets/calibration/index.yaml` (пары, поле `rubric`); `judge-parse` принимает
  ответы сессий (находка — из двух прогонов из трёх, пара — большинством); `agree` и `trust_level` — пороги из группы
  `judge` (Уилсон, F1, доля «не уверен», число сессий); в рубриках нет модели, температуры, seed, `reasoning_effort`,
  `judge.system` штрафует избыточность; задания судьи в `mp_client` сняты, Gen-API без 3D-моделей; `stand_run.py page` —
  режим текстовых карточек; `vlm_to_dna.py build` — пакет той же формы для сессии Opus вместо VLM другого вендора; схема
  паспорта — `icon3d` ссылкой на паспорт blender, поля `illustration` по системе ui, `video.tempo: fast`, ссылка на
  арт-дирекцию в происхождении.
- **Действия:** 13 из 165 (GT-20, VI-49, VI-51, VI-53, VI-54, JU-01, JU-07, JU-18, JU-19, JU-20, JU-23, JU-31, CN-92) и 4
  — 17.
- **Входы:** `kb/common/judge.md` целиком; `.claude/agents/design-judge.md`; `claude-design.md § Проверки по постоянной
  просьбе`; ai-media 11/02 §6; T4 H4; узлы 08-VI, 09-JU, 10-CN; Р5, Р47, Р55, Р60.
- **Среда:** облако; OCR-модели `asset_audit` — МЗ (в зоне не меняются).

### C13 — project: манифест готовности и структурный аудит (шаг 7; ≈ 1 300–2 000)
- **Файлы:** новые `scripts/project/ready.py`, `design_audit.py`; фикстура с посеянными дефектами для проверки Ф8 (ключ
  находок — в журнале, пишет оркестратор до запуска); `tests/smoke/project-package.tsv`.
- **Что делает:** `ready build` и `--check` — манифест по форме `_template/design/_template/ready.yaml` (род и потребитель
  из реестра, источники со статусами и sha256, единицы — композиция, тексты, макет по вердикту `REVIEW.md` с совпавшим
  отпечатком, `budget_profile`, `gate_exceptions`, `after_build` из `ACCEPTANCE.md`, `open`; `perf` по роду;
  `frontend_design`; `blockers`; `status` из единиц); `design_audit` — структурный прогон R-SURF … R-DEBT: зовёт
  валидаторы баз и утилиты `project/`, сам проверяет детерминированные правила (раскладка, схемы, ссылки, slug, покрытие,
  проекции, производные, статусы, каналы голоса против родов — R-COV-007), правила «чтением» перечисляет для скилла;
  тяжесть — по этапу из статусов файлов; выход — находки JSON и сводка, `last-report.md` пишет скилл.
- **Действия:** VI-04 (часть) и H10-ready, H10-design_audit, T1-rules, T2a-rules, T2b-rules, F7-Z1-2, F7-Z5b-1, F7-Z6-1,
  F7-Z6-4, ENV-6 — 11.
- **Входы:** `design-audit/SKILL.md`, `references/rules.md` целиком (64 правила — спецификация); T4 G1, G2, G5, G6, H3; T1
  §4.3, T2a §4.4, T2b §4.4; форма `ready.yaml`, `_template/design/README.md § Пакет для кода`; `phases.md § package`,
  `§ Порядок проверок`; отчёт Z6 §3–§6.
- **Среда:** облако.

### C14 — ворота страницы, движения и 3D (шаг 7; ≈ 800–1 300)
- **Файлы:** `scripts/site/page_gates.py`, `page_anatomy.py`; `scripts/ai-media/page_accept.py`;
  `scripts/creative/motion_check.py` (и `scroll_record.py`, если нужно); `scripts/blender/gate_check.py`, `site_probe.py`,
  `web_view.py`; `scripts/site/geo_probe.py`, `ia_probe.py`, `run_axe_targets.py` — запуск из соседнего чекаута (G4),
  правка — если нужна; строки своих утилит в README и списках смоука; kb: в `site/07-seo-geo-performance-analytics/` —
  `budgets.yaml`, `page-gates.yaml`; `creative/09-ai-execution-evaluation/effect-gates.yaml`; новый YAML порогов ворот 3D
  рядом с blender 09/05.
- **Что делает:** у величины один владелец ворот, у соседей — зеркало D: `page_gates` сводит JSON `page_accept`,
  `motion_check`, `gate_check`, берёт умолчания уровня из `ambition-levels.yaml`, проверяет постер видео (SG-PERF-16);
  `page_accept` — `--budget-profile`, `--root`, окно и условия из `budgets.yaml`, CLS двумя порогами, петли всей страницы
  и 6-я секунда, 0,3 %/с, набор ширин из файла, тяжёлый замок; `motion_check` — слой подачи по режимам, только `reduced`,
  округление станций по схеме, пороги через `threshold_ref`; `gate_check` — LCP и CLS зеркалом, вес 3D из YAML, вклад 3D
  разностью с прогоном «постер без 3D»; `site_probe`, `web_view` — GSAP по рантайму; `page_anatomy` — момент первой
  отрисовки H1, без маскировки автоматизации; строки ворот (SG-PERF-02, SG-WEIGHT-09, SG-A11Y-03, -04, -07, EG-WEIGHT-02,
  -04, EG-A11Y-17…19, новая строка прелоадера) и `budgets.yaml` (окно, условия, `market_reference`, `overrides`); запуск
  из соседнего чекаута (G4). JSON-поля утилит ворот — контракт между ними (GT-43), меняются в этой зоне вместе.
- **Действия:** 32 из 165 (GT-01, GT-03, GT-04, GT-05, GT-06, GT-11, GT-14, GT-15, GT-16, GT-17, GT-20, GT-21, GT-22,
  GT-24, GT-25, GT-30, GT-32, GT-33, GT-34, GT-36, GT-37, GT-38, GT-43, NU-01, NU-31, NU-32, NU-33, NU-34, CN-65, CN-71,
  CN-95, CN-96) и 4 — 36.
- **Входы:** узлы 03-GT, 06-NU, 10-CN; site 07/03 §3–§4, `page-gates.yaml#phases`; creative 09/03, `effect-gates.yaml`;
  blender 09/05 §1, §7; T4 G4, G5; `docs/README.md § Что docs отдаёт соседям` («Ворота после сборки»); Р46, Р99.
- **Среда:** облако — Chromium образа и ffmpeg шага 0; замеры 3D на видеокарте и three.js с jsDelivr — МЗ; числа облака
  пороги не калибруют.

### C15 — text: линтер и словари (шаг 8; ≈ 1 000–1 500)
- **Файлы:** `scripts/text/copy_lint.py`, `ux_dict_to_yaml.py`, `copy_extract.py`, README (своя часть); kb text:
  `06-anti-slop/profiles.yaml`, `06-anti-slop/lexicon/*.yaml` (`ux-07-06.yaml` — перегенерация, `marketing-role.yaml`,
  `ru-punct.yaml`, анализаторы, словари C), `04-copy-by-block/copy-slots.yaml`; в `07-seo-geo-copy/` — `meta-rules.yaml`,
  `geo-rules.yaml`; `08-russian-legal-typography/typography-rules.yaml` (если нужно); в `09-ai-generation-evaluation/` —
  `copy-checklist.yaml`, `copy-rubric.yaml`; `kb/common/tells.yaml` — строка К15, если вносится; строки смоука text.
- **Что делает:** жанр `interface` — профиль, роли прозы `body`, `help`, `email`, длины по ролям из md конвертером,
  уровни ux 07/06 без поправок сайта; роль — вход линтера (`--role`, поле `role`, реестр `texts.md`, роль части из
  `components.yaml#text_roles`, отказ на неизвестной роли и типе); межстрочные анализаторы ux 07/06 §7.3 над реестром
  (имя действия по потоку, синонимы по `object.md#aliases`, формы меню и статусов, дубли, длины, форматы и ICU, знак
  диапазона и разряды, ты и вы, ё и е, уровень чтения); поправки по жанрам (`overrides[].genres`); перегенерация словаря
  ux (кириллица в Python и JS, `UX_ROLES` с `body`, заплатки сняты) и `--check`; записи слотов с `lint_as` и
  `rules_owner`, роли в `section_roles`, `site_slot` снят; калибровки К1–К31 линтера с самопроверкой; `copy_extract` —
  меню первой секции, без маскировки автоматизации.
- **Действия:** 34 из 165 (TR-03, TR-04, TR-06, TR-08, TR-14, TR-58, TX-01, TX-04…TX-09, TX-12, TX-13, TX-15, TX-18,
  TX-21…TX-25, TX-27, TX-40, TX-42, TX-45, VI-29, VI-39 ×2, CN-53, CN-54, CN-59, CN-64, CN-95) и 7 — 41.
- **Входы:** узлы 02-TR, 07-TX, 08-VI, 10-CN; ux 07/06 §7, ux 07/05 §3–§4; text 06/02;
  `kb/text/99-raw/reports/wave4-X-audit.md` §7; T3 D5, §6; `_template/screens/_template/texts.md`; Р33, Р34, Р49, Р127.
- **Среда:** облако (node есть).

### C16 — обслуживание: `scripts/maint/` (шаг 8; ≈ 900–1 400)
- **Файлы:** новые `scripts/maint/canon_check.py`, `refcheck.py`, `mapcheck.py` (перенос из журнала) и проверка
  синхронности — производные генераторов (`--check`), управляемая копия грамматики `tree-notation.md` против README
  экранов, описания скиллов ≤ 600 знаков и сумма ≤ 18 тыс.; `maint/check_links.py` под раскладку `kb/<база>/`; справка
  `count_tokens.py`, `layers.py`, `orch_check.py`, `calibrate.py`; `kb/common/README.md` (строки «Как пользоваться
  `canon.tsv`»: проверка — утилиты `scripts/maint/`); `tests/smoke/maint.tsv`.
- **Что делает:** проверки `canon.tsv` (одно место на норму, id уникальны, пути и разделы существуют), ссылок и следов
  журнала в текстах скилла, карты по канонам — без путей в журнал; до Ф10 процедура H11 идёт через `registry.py` журнала,
  после уборки — через эти утилиты.
- **Действия:** TX-01 (часть) и H10-maint, T4-H11, S6-CN-122, F7-Z7b-1, F7-Z9-1, BL-8, DEC-kimi — 8.
- **Входы:** `../tools/refcheck.py`, `../tools/mapcheck.py`, `../phase-4/tools/registry.py` (`check`, `canon`),
  `../phase-7/tools/static_check.py` (раздел описаний); T4 H11; `kb/common/README.md`; Р136, Р161, Р165, Р179.
- **Среда:** облако.

### C17 — тексты под утилиты (шаг 9; ≈ 300–600 строк правок в ≈ 22 файлах)
- **Файлы:** `scripts/README.md` (указатель); `design-deep-dive/SKILL.md` (по месту) и в `references/` — `phases.md`,
  `claude-design.md`, `field-checklists.md`, `draft-stable.md`, `workflow-patterns.md`, `knowledge-base.md`;
  `design-audit/SKILL.md`, `references/rules.md`; `screen-deep-dive/SKILL.md` и в `references/` — `tree-notation.md`,
  `field-checklists.md`, `draft-stable.md`, `workflow-patterns.md`; `screen-audit/SKILL.md`, `references/rules.md`;
  `mobile-audit/references/rules.md` (R-STRUCT-005 — если называет словарь); `_template/design/README.md`; `kb/INDEX.md`
  §5 (строка покрытия ДС); `docs/getting-started.md` — если меняется запуск установки.
- **Что делает:** тексты называют утилиты, которые есть, их вход и выход; «собран без утилиты» остаётся запасным путём,
  когда окружения нет; вызов судьи — пакет `judge-jobs` и агент; указатель — пути `project/…py` и колонки указателя, новые
  утилиты `claude-design/`, `maint/`, `lib/docpaths.py`, «кто кого зовёт» у ворот и поля JSON (GT-43), находки refcheck в
  нетронутых строках указателя; forward-only, стандарт SKILL-MAP §7; описания `SKILL.md` не растут выше 600 знаков.
- **Действия:** GT-43 (часть), ST-01, ST-05, ST-26 (строки аудитов), F7-Z5b-2, F7-Z5c-1, F7-Z5c-2, BL-7 — 8.
- **Входы:** отчёты зон Ф8 §4; `../phase-7/PLAN.md` §4–§5; `../phase-3/SKILL-MAP.md` §7.
- **Среда:** облако.

### Шаг 10 — оркестратор
- **VI-02:** переименование id примет (`K3-<хвост>` → `LOOK-<хвост>`, `F-<хвост>` → `HON-<хвост>`; `M-*`, `V-*`, `E-*` и
  ключи `k3_allow` не меняются) скриптом журнала `tools/` этой папки, регулярка с границей слева `(?<![A-Za-z0-9-])`,
  одним коммитом по коду (`mockup_checks.py`, `claims_check.py`), README text, `common/tells.yaml#checks`, примерам
  `art-direction-*.json` и копиям строки VI-02 в kb; производный YAML (`site-checklist.yaml`) — пересборкой генератора
  после правки источника, а не правкой копии; сначала сухой прогон с диффом, после — смоук и `--check` генераторов.
- **H11-Ф8:** пакет закрытий по процедуре H11 — TX-28 и TX-31 закрывает утилита, у TR-06 — новый текст позиции (записи
  слотов сделаны, длины — пилот): строки узлов → `registry.py merge`, `canon` → `kb/common/CONTRADICTIONS.md` →
  refcheck, mapcheck → строка DECISIONS.

### МЗ — шаг на машине заказчика
`install.sh --all` с `--from` и `--models-from` (старые `bin/`, `models/`), `--catalogs` (свежие снимки каталогов
ai-media — к Ф9), `install.sh --check`; полный смоук; тесты Blender (`blender -b`: `test_bpyx.py`, `test_agent_helpers.py`);
эталон blender 01 — нейтральные габариты (BL-3); выборочный замер 3D на видеокарте (`web_view.py`, `gltf_load_bench.py`)
на примере базы; `DDD_BRAVE` и самопроверка `refs_client`. Как проводить — §10, вопрос 2.

## 3. Порядок

| шаг | пара | почему так |
|---|---|---|
| 0 | окружение сессии; общий бриф кода | §4; бриф — до первой пары |
| 1 | C1 ∥ C2 | пути, установка и смоук нужны всем; словарь состояний (C2) — вход утилит экранов |
| 2 | C3 ∥ C4 | утилиты экранов — на `docpaths` и YAML состояний; данные подачи и первый `x-canvas-map` — раньше их читателей (site, ворота, вход холста) |
| 3 | C5 ∥ C6 | ДС и демо-набор с контрактом берут разбор дерева и наборы C3; схема `brand` — раньше ссылки из брифа сайта |
| 4 | C7 ∥ C8 | бриф и план сайта читают уровни creative (C4) и схему `brand` (C5); выгрузка текстов и формат `copy.md` нужны холсту и приёму правок |
| 5 | C9 ∥ C10 | план ассетов — на формате плана страницы (C7); копии и проверки макета — на данных ui (C2) и формате `copy.md` (C8) |
| 6 | C11 ∥ C12 | вход холста собирает C3–C10; судья и паспорт нужны аудиту шага 7 |
| 7 | C13 ∥ C14 | аудит и манифест зовут утилиты всех зон; ворота — на данных C4, их ключи вызова для аудита не меняются |
| 8 | C15 ∥ C16 | линтер и обслуживание ни от кого не ждут; их читают только тексты и проверка |
| 9 | C17 | тексты описывают утилиты, которые уже есть |
| 10 | оркестратор | переименование и закрытия — когда зоны сдали свои файлы |
| 11 | проверка Ф8 | §6 |
| МЗ | машина заказчика | после шага 8 или вместе с 3-й облачной сессией |

Длинная цепочка — C1 → C3 → C5 → C11 → C13 → C17 (с C2 → C3 и C4 → C7 → C9 → C11). Остановка на шаге — только по §1.
Один файл в разных шагах правят разные зоны только последовательно (README доменов, списки смоука `site`, `ai-media`,
`creative`, `text`, `kb/common/components.yaml`, `tells.yaml`).

## 4. Сквозные правила кода

- **Окружение облака (проверено 28.09).** Python по умолчанию 3.11, но закрепления требуют ≥ 3.12 — ставить
  `scripts/install.sh --python /usr/bin/python3.13 --groups core,net,morph,svg` в `$DDD_HOME` сессии (по умолчанию
  `~/.cache/design-deep-dive`; группы core, net, morph ставятся ≈ 20 с; libcairo для svg в образе есть); npm-зависимости —
  тем же вызовом (реестр npm открыт). Playwright 1.63 ищет Chromium 1243, в образе — 1194 (`/opt/pw-browsers`), CDN
  Playwright закрыт — до ключа установки C1 в venv ставится `playwright==1.56.0` (запуск и кириллица проверены). ffmpeg и
  ffprobe нет — `apt-get install -y ffmpeg` или статическая сборка с GitHub (зоны C12, C14). Смоук на таком окружении
  сегодня: PASS 207, FAIL 0, XFAIL 9. Закрыто политикой или нет в облаке: Blender, видеокарта, модели Hugging Face,
  OCR-модели, Brave, каналы генерации и каталоги (polza, RouterAI, Gen-API), three.js с jsDelivr — это МЗ.
- **Пути.** Базу, соседние утилиты, данные, выходы, кэши, блокировки и бинарники код находит только через
  `lib/kbpaths.py`; файлы проекта `docs/projects/<slug>/…` — только через `lib/docpaths.py` (корень — репозиторий скилла;
  `--repo` или переменная окружения — другой чекаут). Путей от рабочей папки, домашних папок источника, `99-raw/tools`,
  `<база>-research` нет. Выходы — `$DDD_HOME/out/<домен>/` или `--out`; в репозиторий утилита пишет только свои
  производные файлы проекта по форме (`input/`, статичные копии и `kit.json`, `ready.yaml`, производные ДС, генерируемые
  разделы `map.md`) и только командой `build`; `--check` ничего не пишет; `normalize` без явного `--write` показывает дифф.
- **`DDD_HOME`** — окружение вне репозитория, одно на машину (Р90): venv, npm, бинарники, модели, браузеры, выходы,
  блокировки; в git из него ничего не идёт.
- **Модель — только Opus** (Р5, Р47, Р55). Оценка, анализ, решения и тексты — Claude Opus 5.5 в сессии Claude Code
  (агент `design-judge`; разбор сетки бренда — пакет той же формы); код готовит пакеты заданий и разбирает ответы, моделей
  сам не вызывает, идентификаторов моделей других вендоров как умолчаний оценки в коде нет. Генерация картинок и видео —
  модели ai-media через polza, RouterAI, Gen-API, только по утверждённому плану ассетов и только `--live`; в Ф8 — сухой
  прогон, 0 ₽.
- **Ключи — вне репозитория** (Р53): только переменные окружения владельца через `kbpaths.key()`; в коде, тестах,
  фикстурах, логах и отчётах ключей нет. Ф8 ключей не требует.
- **Контракты между зонами** (меняются только через оркестратора):
  - `x-canvas-map` — один ключ проекции во вход холста у схем владельцев: объект с `stages` (этапы входа) и правилами по
    файлу входа — поле холста → `{rule: copy | map | derive | drop | claude_fills, from: [JSON Pointer источника], note}`;
    у text под ключ переезжают готовые блоки карт с прежними именами (`publish_filter`, `facts_md`, `missing_md`,
    `never_claim_md`, `copy_md`), заголовки колонок — по протоколу холста. Первой форму пишет C4 (шаг 2) и фиксирует
    отчётом; C7 и C8 следуют; поле источника без правила — ошибка сборщика (C11).
  - `copy.md` — формат выгрузки текстов по протоколу (`## <section_id>` → `[<slot_id>]` → текст со статусом): точный
    синтаксис фиксирует C8 (шаг 4); его же пишет `dc_texts` (C10) и читает сборщик (C11).
  - Находки утилит `project/` для `design_audit` — строки JSON `{rule, severity, surface, kind, ref, path, message,
    fix}`, тяжесть `error | warning | hint`; код выхода 0 — ошибок нет, 1 — есть, 2 — вызов или окружение. Первой пишет
    C3.
  - Вызов утилит `project/`: `<команда> <slug> [<surface>] [--repo DIR] [--stage …] [--out …] [--json]`; команды
    `build` и `check`; `--selftest` — на встроенной фикстуре.
  - JSON-отчёты ворот (`page_accept`, `motion_check`, `gate_check` → `page_gates`) — внутри C14 (GT-43).
  - Пакет заданий судьи — формирует C12; тексты вызова — C17.
- **Тесты.** У новой утилиты — `--selftest` без сети и строка смоука; у изменённой — самопроверка покрывает новое
  поведение (например, TR-16 — «на 8 примерах»); производные файлы генераторов пересобираются байт в байт (`--check`).
- **Фикстуры.** `scripts/tests/fixtures/` — демо-проекты, которые сборщик C1 раскладывает во временную папку из слоёв:
  примеры баз по манифесту (без копий) и свои файлы там, где примеров нет (кабинет, продукт); свои файлы — иллюстрация,
  в машинных — `example: true`. В `docs/projects/` данных нет, папок проектов не заводим.
- **Forward-only в коде.** Докстринг, `--help`, комментарии и сообщения — о текущем поведении: без волн, агентов,
  дат, имени снятого генератора, «было / стало»; данные с датой (снимки прайсов) — данные. Зона чистит справку своих
  файлов; полная уборка — Ф10.
- **Схемы и данные kb.** Правка схемы — добавления и совместимые изменения, кроме снятий, которые называют действия
  (`x-kimi-*`, `handoff.kimi`, `executor_block`, `site_slot`); метасхема Draft 2020-12; примеры базы проходят новую схему
  (правит зона-владелец). Числа норм меняются только по действию: пороги — у владельцев величин.
- **Не трогать:** `assets/calibration/` (утверждён заказчиком, Р109); `CLAUDE.md`; описания `SKILL.md` сверх 600
  знаков; чужие файлы; git.

## 5. Приёмка шага (оркестратор)

0. Агент закончил — его файлы и отчёт как есть одним коммитом и push, до приёмки. Сообщение — по содержанию, с пометкой
   «на приёмке», без имён фаз (`CLAUDE.md` §1): `feat(design-deep-dive): вход холста под этап, на приёмке`.
1. Файлы зоны — только свои (`git status`, дифф по путям), других агент не трогал.
2. Действия зоны (`ZONES.tsv`) — реализация в названном месте: чтение, поиск, прогон.
3. Тесты и смоук: `python3 scripts/tests/smoke.py --only <папки зоны>` и полный смоук в конце шага — 0 FAIL, XFAIL — только
   с причиной в колонке `xfail`; тесты зоны (`tests/*`) зелёные.
4. Самопроверки новых и изменённых утилит (`--selftest`, `selftest`) и `--check` генераторов — зелёные.
5. Прогон на примерах: утилита зоны на фикстуре или примерах баз даёт ожидаемое — у утилит `project/` ожидаемый результат
   записан в брифе до запуска.
6. Схемы и данные: JSON и YAML парсятся, схемы проходят метасхему, примеры баз — схемы; `registry.py check` — без новых
   ошибок.
7. Тексты зоны: `refcheck.py --strict` по новым и правленым md — 0 битых, 0 следов журнала; в коде зоны нет следов
   прежнего исполнителя (кроме данных), моделей других вендоров как умолчаний оценки, Р- и Ф-номеров, дат в справке.
8. Выборочное чтение кода: пути через kbpaths и docpaths, сеть и траты — только явными ключами, ключей нет, справка —
   forward-only.
9. Отчёт зоны `reports/<зона>.md`; запись в `CHAIN.md` (время — из уведомления); строка DECISIONS «Ф8, зона N принята»;
   коммиты — правки приёмки в шаблоне (`feat(design-deep-dive)`, `refactor(design-deep-dive)`, `fix(design-deep-dive)`,
   `docs(template)`, `refactor(skills)` — по содержанию) и журнал (`docs(research)`); push; итог в чат.

Правки по замечаниям — тот же агент (продолжением) или оркестратор, если правка мелкая.

## 6. Проверка Ф8 (шаг 11)

- **Смоук и тесты в облаке:** полный смоук — 0 FAIL, XFAIL — только с причиной (бинарники, модели, Blender, Brave,
  каталоги); тесты `scripts/*/tests/` зелёные; самопроверки всех новых утилит зелёные.
- **Производные:** все генераторы `--check` (словарь ux для линтера, профиль site, мастер-чек-лист, словарь и матрица
  состояний, производные ДС на фикстуре) — байт в байт; копия грамматики совпадает с README экранов.
- **Схемы:** все схемы kb проходят метасхему; примеры баз — свои схемы; `x-canvas-map` есть у всех источников входа.
- **Обслуживание:** `scripts/maint/refcheck.py --strict` по текстам, правленым в Ф8, — 0; `maint/mapcheck.py kb/INDEX.md` —
  без новых «НЕ НОРМА»; `maint/canon_check.py` — 0 ошибок; реестр и `canon.tsv` пересобираются байт в байт
  (`registry.py`), меняются только id пакета закрытий; описания скиллов — каждое ≤ 600 знаков, сумма ≤ 18 тыс.
- **Следы:** kimi, K3 и `kimi -p` в `scripts/` — 0 (кроме снимков данных); идентификаторы моделей других вендоров как
  умолчания оценки — 0; фраз «пока утилиты нет» у утилит, которые есть, — 0.
- **Соседний чекаут:** копия репозитория во временной папке, утилиты ворот и `project/` запускаются из
  `../strategy/.claude/skills/design-deep-dive/scripts/…` с рабочей папкой код-репо — находят базу и проект (G4, GT-03).
- **Прогон по сценариям** (как маршруты Ф7): свежий агент без контекста, по `SKILL.md`, указателю и `--help`, проходит на
  фикстурах четыре сценария — лендинг (`canvas_input build --stage wireframe` → `check`), кабинет (`tree`, `states`,
  `screen_map` → вход `mockup` с контрактом и демо-набором), ДС (`ds_build` → `ds_coverage` → `ds_sync --check`), пакет
  (`ready build` → `design_audit` на фикстуре с посеянными дефектами). Ключ — до запуска: `check/KEY.md`; бриф —
  `check/BRIEF-CT.md`; ответы — `check/runs.md`. Готово — 4 из 4 и все посеянные дефекты найдены.
- **МЗ:** `install.sh --check` — 0 ошибок; полный смоук на машине заказчика — 0 FAIL; тесты Blender зелёные.

## 7. Готово, когда

- зоны C1–C17 приняты (строки DECISIONS, коммиты, push);
- шаг 10 сделан: переименование id одним коммитом, пакет закрытий — строкой DECISIONS;
- проверка §6 чистая, сценарии — 4 из 4;
- шаг МЗ сделан — или его пункты перенесены в Ф9 словом заказчика;
- STATE, `../PLAN.md` и `NEXT-SESSION-PROMPT.md` — под Ф9.

## 8. Риски

- **Два агента задели один файл** → списки §2 не пересекаются; смоук разбит по спискам; указатель `scripts/README.md`
  правит только C17; приёмка сверяет дифф по путям.
- **Контракты между зонами расходятся** (`x-canvas-map`, `copy.md`, находки, JSON ворот) → форма — §4, первый писатель
  фиксирует её отчётом, читатели — в следующих шагах; приёмка гоняет связку на фикстуре.
- **Облако не равно машине заказчика** (Python 3.13 против системного 3.11, Playwright 1.56 и Chromium 141 против 1.63 и
  153, ffmpeg доустановкой, нет видеокарты, закрытые хосты) → числа облака пороги не калибруют; замеры и Blender — МЗ;
  смоук держит ожидаемые падения с причиной.
- **Разрастание задачи** → зона делает свои действия; найденное сверх — в отчёт, решает оркестратор.
- **Большие файлы кода** (`copydeck.py` 3,7 тыс. строк, `refs_client.py` 3,5, `mp_client.py` 3,1, `claims_check.py` 2,8,
  `asset_audit.py` 2,6, `page_anatomy.py` 2,6, `motion_check.py` 2,4) → бриф называет функции и подкоманды, агент читает
  по `def` и `add_parser`, а не целиком.
- **Снятие веток прежнего исполнителя ломает вызовы** (например, `run_checks.py` и `chain_inputs.py` зовут экспорт) →
  поиск вызывающих до снятия, смоук после.
- **Регулярка переименования цепляет чужие id** (`COPY-F-QUOTE`) → граница слева, сухой прогон с диффом (VI-02).
- **Живой судья в Ф8 не гоняется** → формат пакета и разбор ответов проверяются офлайн на заглушках; первый прогон судьи
  по калибровочному набору — Ф9 (JU-20); `omitClaudeMd` требует Claude Code ≥ 2.1.271.
- **Схемы меняют примеры** → зона-владелец правит свои примеры в том же шаге; прогон примеров — пункт приёмки.
- **Агент прерван** → работу доводит новый агент по файлам на диске (Р119); в облаке — страховочные проверки и коммит
  «черновик, агент в работе».

## 9. После Ф8

Ф9 — пилоты: лендинг, многостраничник, SaaS; до старта — бюджет генерации (открытое решение `../PLAN.md`) и свежие
снимки каталогов ai-media (устаревают с 30.09; из облака каналы закрыты — снимать на машине заказчика); первым делом —
прогон судьи по калибровочному набору (JU-20) и согласие с голосами заказчика на парах пилота. Ф10 — уборка: пункты «вне»
`ZONES.tsv` с пометкой «уборка Ф10», копии норм и справка кода, `99-raw`, журнал. Соседние шаблоны кода (`<org>/site`,
`<org>/frontend`, `<org>/mobile`, `<org>/<bot>`, `<org>/infra`) учатся читать слой страницы и `ready.yaml` отдельной
работой (Р163, п. 3).

## 10. Вопросы заказчику

1. **Способ Ф8.** (а) Как Ф7: до финала без остановок, парами, облачная сессия до лимита, push после каждого агента и
   приёмки, итог шага — в чат. (б) Показ после каждого шага и «да» перед следующим. **Рекомендация — (а):** зоны не
   задевают ваших решений; вопрос появится, только если шаг их заденет.
2. **Шаг на вашей машине** — Blender 5.2.2, видеокарта, модели и старые `bin/` и `models/` для `install.sh --from`,
   Brave, свежие каталоги генерации: из облака этого нет или закрыто политикой. (а) Одна локальная сессия Claude Code в
   конце Ф8 (≈ 1–2 ч): установка `--all`, смоук, тесты Blender, эталон blender 01 на нейтральные габариты, выборочный
   замер 3D. (б) Вы запускаете `install.sh --check` и смоук по инструкции и присылаете вывод; Blender-пункты — в Ф9.
   (в) Всё машинное — в начале Ф9. **Рекомендация — (а):** пилоты начнутся на проверенном окружении, а правка эталона
   blender закроется в фазе, где её решили (Р108).
3. **Калибровочный набор, кадры 10 и 12** (`gen-b1`, `gen-b3`, «уровень» пресета A): на кадре активен не тот пункт
   навигации. Набор утверждён вами (Р109), разметку без вашего слова не меняем. (а) Дописать в `notes` двух кадров строку
   об известном дефекте, кадры не трогать. (б) Оставить как есть до калибровки судьи в Ф9. (в) Перерендерить кадры —
   исходного окружения нет, дорого. **Рекомендация — (а):** судья кадров с разметкой не видит, а человек при калибровке
   не примет дефект за норму уровня.
