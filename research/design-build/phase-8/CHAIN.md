# Ф8 — цепочка агентов зон кода

Каждый агент Ф8 читает этот файл целиком перед работой. Свою запись он пишет в конец отчёта зоны
(`reports/<зона>.md`, раздел «Запись для CHAIN»), сюда её переносит оркестратор: так два параллельных агента не пишут в
один файл. План — `PLAN.md`, действия по зонам — `ZONES.tsv`, общий бриф — `briefs/COMMON.md`, брифы зон — `briefs/`,
решения — `../DECISIONS.md` (Р183, Р187 и строки «Ф8, зона … принята»).

Формат записи:

```
## <NN>. <зона> — <тема> (<дата>, ≈ <мин> мин, в уведомлении — <тыс.> токенов)
- Сделано: файлы (новые / правленые, строк); действия зоны — с местом реализации.
- Тесты: смоук зоны, самопроверки, `--check`, прогон на фикстуре или примерах — итог.
- Отступления: что сделано не по плану и почему; решение оркестратора.
- Стыки: что передаю следующим зонам — кому и что (контракты, ключи вызова, форматы, пути).
- Открыто: что не решено и что это закроет (зона, МЗ, Ф9, Ф10).
- Не прочитано: что осталось вне чтения и почему.
```

Время записи — по уведомлению о завершении агента (агенты его завышают).

Порядок (Р183, Р187): 0 — окружение и общий бриф → 1 — C1 ∥ C2 → 2 — C3 ∥ C4 → 3 — C5 ∥ C6 → 4 — C7 ∥ C8 →
5 — C9 ∥ C10 → 6 — C11 ∥ C12 → 7 — C13 ∥ C14 → 8 — C15 ∥ C16 → МЗ → 9 — C17 → 10 — оркестратор → 11 — проверка.

## Уроки прежних фаз (для всех зон)
- Файлы результата — рабочие артефакты заказчика: пиши их по мере готовности; сессия может оборваться, работу спасают
  файлы на диске, прерванную зону доводит новый агент по ним (Р119).
- Инструмент может не дать записать отчёт — тогда полный текст в ответе, файл пишет оркестратор.
- Правка по месту, без переформатирования: агент Ф7, переписавший файлы под ширину, раздул дифф и спрятал потери.
- Снимок `CLAUDE.md` в контексте агента бывает старым — главный файл на диске.
- Большие файлы и спецификации — адресно: разделы, функции, подкоманды из брифа.
- Механический проход по многим файлам — один раз, со сверкой каждого места.

## Шаг 0 — окружение (29.09)
- `install.sh --python /usr/bin/python3.13 --groups core,net,morph,svg` — без ошибок (≈ 42 с): доставлены группа svg
  (cairosvg), npm-зависимости в `$DDD_HOME/node` (npm предупредил: скрипт установки `esbuild` заблокирован настройкой
  `allowScripts` npm — эталонные сборки blender на `esbuild` проверить на шаге МЗ), каталоги `bin/`, `models/`, `node/`.
- Смоук — PASS 207, FAIL 0, XFAIL 6 (снимки каталогов ai-media — 5; `provenance_check` без c2patool и exiftool — 1),
  XPASS 3 (`check_icons.py`, `svg_sheet.py` — cairosvg есть; `refs_client` — Brave есть), ≈ 95 с.

----

## 01. C1 — основа: пути, окружение, смоук, фикстуры (29.09, ≈ 55 мин, в уведомлении — 592 тыс. токенов)
- Сделано: новые — `scripts/lib/docpaths.py` (661), `scripts/tests/fixture_project.py` (439), фикстура
  `scripts/tests/fixtures/minimal/` (манифест + 3 своих файла), 18 списков `scripts/tests/smoke/*.tsv`; правлены —
  `kbpaths.py` (+140/−31), `install.sh` (+258/−67), `smoke.py` (+110/−9), `requirements.txt`, `package.json`. Действия:
  H10-docpaths, GT-03 и T4-G4 (соседний чекаут — в `kbpaths --selftest`), ENV-5 и H10-smoke (списки `smoke/`, дубль —
  код 2, `--validate`, `--uncovered`), ENV-6 (сборщик фикстур), ENV-1 (Python ≥ 3.12), ENV-2 (`--playwright-match`),
  ENV-3 (`--ffmpeg`, PATH в `kbpaths`), ENV-7 (все 21 адрес рабочие, «вручную» нет), BL-5 (`--from` несколькими папками,
  поиск по имени), BL-6 (`--bins`), CN-115 (справка Blender Lab), T2a-designmd (линтеров нет), DEC-kimi (0).
- Тесты: смоук зоны 0 FAIL; самопроверки `kbpaths` 24, `docpaths` 32, `fixture_project` 20; `install.sh --dry-run`,
  `--check` — 0; `--from` по старым папкам — 15 из 15 бинарников и 7 из 7 моделей (установка во временный `DDD_HOME` —
  22 «ok»).
- Отступления: снят суффикс `-research` в `kbpaths`; статический ffmpeg через PATH процесса; ffmpeg — сборки Martin Riedl
  7.1.1; Blender Lab — справкой; манифест фикстуры шире брифа (`extends`, `replace`, `drop`); `capability` — слой
  `docpaths`; `allowScripts` для esbuild.
- Стыки: `docpaths` (`parser`/`parse`, `Call`, пути слоёв, `Surface.route`/`layers`, `rel` для `path` находок, `status`),
  `DDD_REPO` читает только `docpaths`; манифест и `built()` сборщика; списки `smoke/` по зонам; ffmpeg по имени после
  `import kbpaths` — отчёт C1 §4.
- Открыто: установка `--all --from` — МЗ (команда — отчёт §4); указатель `scripts/README.md` — C17.
- Не прочитано: README scripts вне lib и project; брифы C3–C16 — поиском; код утилит других папок — поиском вызовов.
- Решения оркестратора (строка DECISIONS «Ф8, зона 1 принята»): отступления приняты; `smoke-list.tsv` снят из git.

## 02. C2 — ui, ux и проверки экрана (29.09, ≈ 48 мин, в уведомлении — 676 тыс. токенов)
- Сделано: новые `scripts/ux/states_export.py` (414), `scripts/ui/data/thresholds.yaml` (28), `marketing-profile.yaml`
  (116), производный `kb/ux/06-feedback-states-motion/screen-states.yaml` (316); правки `ui_audit.py` (+828/−95: скрытое
  вне I1, H, F; I1m «проверить F83»; F3 тач 44 зоной; H8 в знаках; K2 потолок пресета; I10; J9 выравнивание; D3/D4/L4
  профиля; токены ДС JSON или CSS; ширины из `acceptance-widths.yaml`, `--acceptance`; id приметы из `tells.yaml#checks`;
  `--slop-params`), `measure_ui.py` (порог шапки по поверхности, `--selftest`), `build_reference_tokens.py`,
  `checklist_export.py` (`--check`, хэш вместо времени); kb: ux 06/01 (S23, S24), `master-checklist.yaml`, ui 11/04 §3,
  пример дашборда и `app.css`, `components.yaml`. 25 действий.
- Тесты: смоук ui и ux — 0 FAIL; `ui_audit --selftest` 54 OK, `measure_ui` 7/7, `states_export` 17/17; `--check` обоих
  генераторов — 0; дашборд: прежняя вёрстка — J9 FAIL (сдвиг 16 px ×2), после правки — 0 FAIL.
- Отступления: ключи `ui_audit:<id>` в `tells.yaml#checks`; D4 — `glow_max 1` в данных; профиль — API для
  `marketing_audit`; consumer без `--tokens` — шкалы пресета; F1 24 везде + F3 44 на таче; `generated_at` →
  `source_sha256_16`.
- Стыки: C3 — форма `screen-states.yaml`, `screen_states` → файл#ключ; C4 — `load_profile`/`apply_profile`, свой D4
  снять, новые id и поля строк; C10 — `thresholds.yaml` (`font_sizes`, `header_height`); C7 — UX-PRC-12 в профиле site.
- Открыто: «S01–S22» сжатого слоя; S23 в строке `route` §3.1; creative 09/03 §4.2 (D3, D4, F1, H8, K2); README и `audit/`
  примеров ui; шапка CSS эталонных токенов; m29 скрипта §3 — Ф10.
- Не прочитано: ux 12/02, `effects.yaml`, ui 09/04, creative 09/03 — только нужные места.
- Решения оркестратора (строка DECISIONS «Ф8, зона 2 принята»): отступления приняты; строки `ui_audit:*` (9) внесены в
  `tells.yaml#checks`; строки смоука C2 — в `smoke/ui.tsv`, `smoke/ux.tsv`; профиль site пересобран отдельным коммитом.

## 03. C4 — creative: данные и валидаторы подачи (29.09, ≈ 58 мин, в уведомлении — 918 тыс. токенов)
- Сделано: правлены `ambition-levels.yaml` (+176/−65), схемы `art-direction.v1` (+364/−106), `treatment` (+51/−40),
  `motion-spec` (+51/−13), `marketing-tokens.json`, `stack.yaml`, `block-treatments.yaml`, рубрика, `effects.yaml`
  (строка), 6 примеров арт-дирекции; утилиты `spec_check.py` (+485/−68, команды `canvas-map`, `levels --check`),
  `ad_check.py`, `validate_stack.py`, `registry_check.py` (переписаны), `marketing_audit.py` (+332/−232), README папки
  (переписан: журнал прежних агентов снят, описаны все утилиты папки), `smoke/creative.tsv`. 40 действий — отчёт C4 §2.
- Тесты: смоук creative PASS 22, FAIL 0; site, ui, claude-design — 0 FAIL; самопроверки 24 + 35 + 11 + 11 + 45 OK;
  `levels --check`, `canvas-map` — 0; примеры — 0 ошибок; `marketing_audit` в браузере на примере рецепта L0.
- Отступления: `budgets.page` и `fonts_kb` — зеркало до переключения `threshold_ref` у C14; L2 — кадр в покое 30 / 60,
  «мир» при прокрутке 50 / 100 (по решению узла GT-08); потолки петель сняты из схемы `treatment`; `source` референса —
  три значения; шкала K2 из токенов; MKT-C2 — находка; число COPY-C-18 из `pass_when` до поля C15.
- Стыки: форма `x-canvas-map` и id документов (C7, C8, C11); `$defs/reference` (C7); пути ключей уровней (C7, C14,
  C11); `per_sections` (C15); `ad_check --json` (C13) — отчёт C4 §4.
- Открыто: зеркало `budgets.page` — C14; расхождения реестра клише (9) — Ф10; порог wasm — пилот Ф9; v0-схемы creative и
  тексты базы о них — Ф10; `canvas:frame` в примере blender `zveno` не проходит шаблон свойства — владелец примера, Ф10.
- Не прочитано: `effect-gates.yaml`, `motion_check.py`, `ui_audit.py` — только места стыков; creative 01/03 — частично.
- Решения оркестратора (строка DECISIONS «Ф8, зона 4 принята»): отступления приняты; строки `marketing_audit:*` (3)
  внесены в `tells.yaml#checks`; `ambition-levels.yaml` вписан в файлы C14 для снятия зеркала вместе с `threshold_ref`.

## 04. C3 — project: экраны (29.09, ≈ 61 мин, в уведомлении — 787 тыс. токенов)
- Сделано: новые `scripts/project/findings.py` (247), `layer.py` (783), `tree.py` (1 341), `states.py` (696),
  `screen_map.py` (979), `normalize.py` (942), `data/screens.yaml` (19); фикстуры `scripts/tests/fixtures/cabinet` (27
  файлов, проект `otves-office`, поверхность `office`), `cabinet-defects` (14 дефектов правками `replace`),
  `cabinet-freeform` (вольная запись); `smoke/project-screens.tsv` (+7). 13 действий — отчёт C3 §2.
- Тесты: смоук project PASS 13; самопроверки findings 14, layer 9, tree 27, states 21, screen_map 17, normalize 12;
  чистый слой — 0 находок, `build` байт в байт, пустой дифф нормализатора; дефекты — 14 из 14 по одной находке
  (12 `error`, 2 `warning`; плюс 7 подсказок R-TX-006 от ушедших ключей); вольная форма — после `--write` 0 `error`.
- Отступления: второй общий модуль `layer.py`; правила сверх брифа (R-STRUCT, R-TX); `offline` и `stale` — чтением (в
  «Решениях» `map.md` нет машинного поля); `no-permission` из строки маршрута — только при `access: roles`; присутствие
  строк свода — R-RT-008; правила выводимых колонок свода — в справке и `data/screens.yaml`; `kind` находки — открытое
  слово-slug; R-SEM-015 механически — две проверки из пяти; R-TX-004 — одна находка на ключ.
- Стыки: контракт находок — `findings.py` (форма и пример — отчёт C3 §4); вызов `check`/`show`/`build`; Python-API
  `layer`, `tree` (`ui_types` — C5), `states` (`dump` — C6, C11), `screen_map` (`derive`, `render` — C11); фикстура
  `cabinet` — база C5, C6, C11, C13 (токены `space.md`, `space.sm`); тексты под утилиты — C17.
- Открыто: машинное поле решений поверхности (`offline`, `stale`) — Ф9 или Ф10; строгая достижимость по навигации;
  зеркала и перечни `screen-audit` — кандидаты в утилиты после пилота.
- Не прочитано: in-drafts (правило); каноны FSD, бота, mobile вне состояний; нормы отдельных типов словаря.
- Решения оркестратора (строка DECISIONS «Ф8, зона 3 принята»): отступления приняты; прогон оркестратора на
  фикстурах совпал с ключом брифа.

## 05. C6 — project: демо-набор и контракт генерации (29.09, ≈ 46 мин, в уведомлении — 716 тыс. токенов)
- Сделано: новые `scripts/project/demo_data.py` (916), `contract.py` (1 215), `data/demo.yaml` (122 — нормы крайних
  случаев с адресом в базе); фикстура `scripts/tests/fixtures/cabinet-demo/` (поверх `cabinet`: атрибуты остальных
  типов, 8 утверждённых строк реестра); `smoke/project-demo.tsv` (+3). 4 действия — отчёт C6 §2.
- Тесты: смоук project — 0 FAIL; самопроверки `demo_data` 37, `contract` 25; контракт на фикстуре — 10 разделов §7.3 и
  раздел на каждый экран, S-id экрана = набор `states.py` ∪ ключи `states`, источники существуют; демо-набор — объёмы
  0 / 1 / 60 / 3 000, крайние случаи, `example: true` везде, повтор — байт в байт; снятый `volume` и пустые `examples`
  — находки с путём.
- Отступления: находки — правила `design-audit` (R-MAT-011 с номером пункта PRE, R-MAT-003, R-COV-005, R-DEBT-002);
  снятый `volume` — `error`, пустые `examples` — `hint`; строки текстов во входе дважды (контракт и `copy.md`) — из
  одного фильтра; окно записей набора — 50; текст без `examples` — видимая подпись, имён модуль не сочиняет;
  детерминизм хэшем, без `random`; контракт — этапы `wireframe` и `mockup`; объём ≈ 2,1 тыс. строк.
- Стыки: C11 — `D.build`/`D.dumps` → `demo-data.json`, `C.build(lay, stage, demo=doc)` → `render`, `as_dict`,
  `findings`, `C.text_rows` для `copy.md`, итог блока PRE — находки R-MAT-011; C13 — правила модулей и выбор этапа;
  C17 — тексты под утилиты (отчёт C6 §4).
- Открыто: дубль строк текстов во входе — пересмотреть после пилота SaaS.
- Не прочитано: см. отчёт C6 §8.
- Решения оркестратора (строка DECISIONS «Ф8, зона 6 принята»): отступления приняты; развилка текстов — (а).

## 06. C5 — project: ДС (29.09, ≈ 48 мин, в уведомлении — 713 тыс. токенов)
- Сделано: новые `scripts/project/ds_build.py` (1 379), `ds_sync.py` (956), `ds_coverage.py` (754); схемы
  `kb/common/{brand,system,app-brief}.schema.yaml` (122, 195, 339) со строками `kb/common/README.md`; шапка
  `components.yaml`; фикстура `scripts/tests/fixtures/cabinet-ds/` (43 файла: токены DTCG, проза, карта решений, бренд,
  бриф на вид, собранные производные, 17 компонентов с превью состояний); `smoke/project-ds.tsv` (+3). 14 действий —
  отчёт C5 §2.
- Тесты: смоук project — 0 FAIL; самопроверки `ds_build` 30, `ds_sync` 18, `ds_coverage` 29; на фикстуре `ds_build
  check` — 0, правка токена без `build` — R-FRESH-001, битый `$value` и ссылка в пустоту — R-STRUCT-006; круг «туда и
  обратно» на примере cd — те же имена и значения (2 строки из 98 — источник в `meta` и кавычки шрифта); `ds_coverage`
  — 0 на полной фикстуре, находка на каждый посеянный пробел.
- Отступления: `kind` находок — `design-system`; команда `show` у всех трёх; NU-15 — кегль узкой ширины выводится
  сборкой (`x-narrow` передней части `DESIGN.md`, блок `@media` в CSS), поля в DTCG нет; имена CSS-переменных 1:1 с
  путями DTCG против таблицы переименований ui 09/04 §6.3; примитивы и движение в `tokens.json` артефакта не идут;
  расширение `org.design-deep-dive.artifact`; фикстура с `ui:AddressMap` (расширение словаря на экране).
- Стыки: C7 — схема бренда `kb/common/brand.schema.yaml` (`$id` `urn:app-design:common:brand:1`), форма `themes`; C11 —
  `stage:` в передней части `INPUT.md`, перед макетом кабинета — `ds_coverage check --stage mockup` и `ds_build check`;
  C13 — вызовы `check --json`, `form_errors()`, фикстура `cabinet-ds`; C17 — тексты (отчёт C5 §4).
- Открыто: мост к Tailwind (`@theme inline`) — код-репо; режим `narrow` в DTCG — решение базы ui, Ф10.
- Не прочитано: см. отчёт C5 §8.
- Решения оркестратора (строка DECISIONS «Ф8, зона 5 принята»): отступления приняты; NU-15 — вариант (а), приложение
  читает `x-narrow` до пилота SaaS; имена CSS-переменных — 1:1 по Р42.

## 07. C7 — site: бриф, план, словарь, валидатор, профиль (29.09, ≈ 57 мин, в уведомлении — 823 тыс. токенов)
- Сделано: схемы `site-brief` (+465/−53: `themes` с `switcher`, `brand: {ref, expression}`, `$defs/reference` по форме
  C4, `x-canvas-map`), `page-plan` (+365/−9: `x-canvas-map`, умолчание `3d[].load`), `site-map`; `site_validate.py`
  (+242/−96: темы и бренд, `recipe:`, уровни и доля из `ambition-levels.yaml`, подача через `spec_check.py plan` — PL-C01,
  `x-effect-levels` — PL-C02, только v1), `vocab_lint.py` (+108/−13: таблица соответствия), `build_profile.py` (+185/−60:
  сверка с версией чек-листа ux, основания профиля существуют); `vocabulary.yaml`, `crosswalk.tsv`
  (`email-sender-name`), `legal-requirements.yaml` (LR-RU-25…28), три примера и два `brand.yaml`, README своих разделов,
  `smoke/site.tsv`; профиль ux пересобран. 28 действий — отчёт C7 §2.
- Тесты: смоук site PASS 22; самопроверки `site_validate` (пример + 26 посеянных случаев), `vocab_lint` 12,
  `build_profile` 13; `build_profile --check`, `canvas-map` (11 файлов), метасхема — 0; `--all` — 0 ошибок; сценарий
  оркестратора — SB-B01, SB-C01, PL-D02, page-transition на L1 проходит.
- Отступления: `themes.switcher` сверх формы C5; `brand.expression.direction` оставлено до Ф10; бренд примеров — рядом с
  брифом; проверки подачи — через `spec_check.py plan` (PL-C01); `3d[].load` по умолчанию `on-interaction`; валидатор
  только v1, `x-supersedes` сняты; версия чек-листа — `source_sha256_16`; поля холста в нескольких картах — C11
  объединяет `from`; основания профиля — каноны вместо 14 ссылок в пустоту.
- Стыки: C11 — поля и указатели карт брифа и плана (отчёт C7 §4); C9 — умолчание `3d[].load`; C13 — коды `site_validate`;
  C8 — `req:LR-RU-28`, слот `email-sender-name`; C17 — тексты шаблона сайта, коды процедуры, указатель.
- Открыто: провенанс прежнего исполнителя в данных `crosswalk.tsv` (141 строка) и `vocabulary.yaml` (2) — Ф10; схемы
  v0/v0.9 и ссылки примеров на неперенесённые опыты — Ф10; `ac-profile.tsv` из `99-raw` — Ф10.
- Не прочитано: см. отчёт C7 §8.
- Решения оркестратора (строка DECISIONS «Ф8, зона 7 принята»): отступления приняты; в `app-brief` (схема и форма) —
  `themes.switcher` и форма референса как у брифа сайта.

## 08. C8 — text: copy deck, факты, смысл, голос (29.09, ≈ 103 мин, в уведомлении — 490 тыс. токенов)
- Сделано: правки `scripts/text/` — `copydeck.py` (4 559 строк, +1 605/−778), `claims_check.py` (3 132, +693/−352),
  `validate_meaning.py`, `validate_voice.py`, `make_skeleton.py`, `chain_inputs.py`, `run_checks.py`,
  `validate_facts.py`, `validate_any.py`, `check_intake.py`, своя часть README, `smoke/text.tsv`; kb: 6 схем text,
  `claims-rules.yaml` (68 правил, COPY-L-FCST-01, COPY-L-JOB-01), `before-after.tsv` (`why` у 112 строк), 8 примеров copy
  deck, 8 наборов фактов text и site (демо-факты «Сталькона» переписаны связно). 28 действий — отчёт C8 §2.
- Тесты: смоук text PASS 24; самопроверки `copydeck` 147, `claims_check` 128 (калибровки К17–К27), `validate_meaning`
  21 (К30), `validate_voice` 22 + 7 мутаций, `make_skeleton` 9, `chain_inputs` 13; `run_checks` — 0 ошибок на 8 примерах
  по 6 шагам; три примера site v1 — каркас из плана → `validate` 0, `approve` чистит журнал, выгрузка `copy.md` и
  `facts.md` по протоколу, приём правленого `copy.md` — вариант `source: customer`; `canvas-map` по 5 схемам — 0.
- Отступления: демо-факты — ошибка с `--final`, без него — info; COPY-D-STAGE — ошибка на макете, раньше — warning;
  `approve` требует прохождения `validate`; тексты агента в примерах — `assumed` (юридические — `draft`); метки волн и
  агентов в справке сняты; К28 — у C15.
- Стыки: контракт `copy.md` (синтаксис и пример — отчёт C8 §4; читают C10, C11); API выгрузки и приёма (`export_canvas`,
  `export_copy_md`, `export_facts_md`, `import-copy`) — C11, C10; `req:LR-RU-28`, `email-sender-name` — C7; тексты шаблона
  и протокола о статусе `assumed` и воротах этапов — C17; временный словарь в `copy_lint`, `copy_extract` — C15.
- Открыто: остаток README text (94 битых пути, 21 след журнала — чужие разделы) — C15 (свой раздел) и Ф10; правила длины
  слота `email-sender-name` — Ф10 или пилот.
- Не прочитано: см. отчёт C8 §8.
- Решения оркестратора (строка DECISIONS «Ф8, зона 8 принята»): отступления приняты; `validate_voice.py --help` —
  справка вместо трассировки (правка при приёмке), строка смоука — `help; run:`.

## 09. C9 — план ассетов, инвентарь и референсы (29.09, ≈ 48 мин, в уведомлении — 724 тыс. токенов)
- Сделано: новая схема `kb/ai-media/05-prompting/asset-plan.schema.json` (275: `status` и `approval`, `key`, дорога 3D,
  `source` с `render`, `task_codes` или `recipe:`, `ai_fit`, id слотов — словарь site, `x-canvas-map`); фикстура
  `scripts/tests/fixtures/asset-plan/`; `plan_to_assets.py` переписан (1 102: режим проекта `build|check <slug>`,
  `--check`, `--types`, `--spec-role`, `--selftest`, находки по контракту C3); `asset_inventory.py` (без маскировки,
  GSAP по рантайму); `refs_client.py` (без превью работ и автора площадок со входом); `asset-spec.schema.json`
  (`role.page_type` — id словаря, класс — `role.page_class`); три примера `asset-plan.home.yaml`; README site, ai-media,
  creative; строки смоука. 14 действий — отчёт C9 §2.
- Тесты: смоук site PASS 25, ai-media 51, creative 22; самопроверки `plan_to_assets` 52, `asset_inventory` 9 (Chromium,
  `file://`), `refs_client` 46 (с Brave — пункт МЗ закрыт); схемы — метасхема, `canvas-map` — 0; `--check` примеров — 0
  ошибок; посеянные дефекты — R-MAT-002, R-STRUCT-005; 10 новых типов страниц — 0 ошибок.
- Отступления: `page_type` плана ассетов — id словаря, класс ai-media — `media_class`; каркас меняет форму прежних
  файлов; `key` — по правилу канона; `build --write` — только для страниц без плана; утилита site говорит контрактом
  находок `project/`; `--spec-role`; перечень `role.page_type` → шаблон id, прежний — `role.page_class`; телефонный UA —
  Pixel 7 с `HeadlessChrome` (честный); автор снят в записях работ площадок; `handoff` — в форме `refs.md`.
- Стыки: C11 — карта `asset-plan` (`assets.md`, `decisions.assets_mode`, `decisions.three_d` — объединить с картой
  уровней); C13 — `plan_to_assets.py check <slug> [<surface>] --json`, правила, фикстура `asset-plan`; C14 и C15 — приём
  без маскировки UA и GSAP по рантайму; C17 — тексты (отчёт C9 §4).
- Открыто: полный шаблон §8 ai-media 01/01 и чек-лист плана ассетов — Ф10; `prompt_compile.py` берёт фразу из
  `role.page_type` — после пилота генерации; автор у записей галерей (CSSDA) — Ф9 или юрист.
- Не прочитано: см. отчёт C9 §8.
- Решения оркестратора (строка DECISIONS «Ф8, зона 9 принята»): отступления приняты; шаблон §8 ai-media 01/01 — поля
  страницы и статус приведены к схеме при приёмке (полное выравнивание — Ф10); `handoff` `refs_client` оставлен до пилота.

## 10. C10 — claude-design: копии холста и проверки макета (29.09, ≈ 58 мин, в уведомлении — 786 тыс. токенов)
- Сделано: новые `scripts/claude-design/dc_to_html.py` (910), `copies_compare.py` (436), `dc_texts.py` (526),
  `literal_tokens.py` (992), `kit/kit_manifest.py` (399), фикстура `scripts/tests/fixtures/canvas/`; правки
  `mockup_checks.py` (+1 118/−472), `kit/shot.py` (+49/−11), `stand_page.py`, `shot_v3.py`, `lang_check.py` (следы,
  справка, синтаксис `copy.md`), `smoke/claude-design.tsv` (+5). 23 действия — отчёт C10 §2.
- Тесты: смоук claude-design PASS 27; самопроверки dc_to_html 49, literal_tokens 36, kit_manifest 23, dc_texts 15,
  copies_compare 12, mockup_checks 67, stand_page 9; на примере «Спица» — 8 артбордов → 8 HTML, кадры по `kit.json` без
  ошибок консоли; копия против себя — 0; круг copy deck → артборд → `dc_texts` → `import-copy` — 32 слота из 32 без
  находок формата; `literal_tokens` — 26 литералов вне токенов (значения узкой ширины); VI-03 в браузере — «три
  карточки» на бенто не срабатывает, «центрированный hero» на орбите — по высоте и центру.
- Отступления: новые проверки `LOOK-TYPE-SCALE`, `LOOK-HEADER`, `LOOK-BENTO`, `LOOK-ORBIT`, `FORM-FIELDS`,
  `FORM-FORBIDDEN` — сразу с целевым префиксом; вердикт кластера не считается (пороги — проза, калибровка — Ф9); правки
  находок по-русски; статичная копия — только на ширине своей рамки; `lang_check --copy` — синтаксис C8; общая блокировка
  браузера; `dc_texts` — только страницы сайта (тексты кабинета — через `/screen-deep-dive`); объём ≈ 4,4 тыс. строк.
- Стыки: C11 — `kit_manifest` (классы экрана, эталонные границы), `--artboards`, разметка `data-slot`; C13 — вызовы
  `check` пяти утилит, `dc_to_html fingerprint` для сверки с `REVIEW.md`, JSON `mockup_checks` (`summary.domains`,
  `summary.clusters`), строка происхождения копии; C12 — кадры по `kit.json`; C17 — тексты (отчёт C10 §4).
- Открыто: правка текстов кабинета с холста машинно — после пилота SaaS; случайные ширины внутри классов — Ф9 (NU-05).
- Не прочитано: см. отчёт C10 §8.
- Решения оркестратора (строка DECISIONS «Ф8, зона 10 принята»): отступления приняты; VI-03 — вариант (а): строки
  `tells.yaml#checks` для шести проверок и поле `check` у четырёх примет внесены, у бенто и орбиты — `allow: cards`,
  `allow: center-hero` (расхождений `k3_allow` в реестре клише — 7 вместо 9).

## 11. C12 — судья и паспорт визуала на Opus (29.09, ≈ 54 мин, в уведомлении — 816 тыс. токенов)
- Сделано: правки `asset_audit.py` (+977/−341: `judge-jobs` — пакет для агента `design-judge`, `judge-parse`, `agree`,
  уровень доверия из группы `judge`), `test_asset_audit.py`, `stand_run.py` (текстовые карточки), `mp_client.py`
  (задания судьи и 3D-сети Gen-API сняты), `vlm_to_dna.py` (`build` — пакет той же формы, `parse`), своя часть README
  ai-media; `thresholds.yaml` (группа `judge`, `hero_mobile_kb`), 12 рубрик (без параметров модели, штраф за
  избыточность, версия 1.1), `judge-response.schema.json`, `visual-dna.schema.json` и 4 паспорта-примера, строка
  `judge.md §6`, `smoke/ai-media.tsv`. 17 действий — отчёт C12 §2.
- Тесты: смоук ai-media PASS 53, FAIL 0; `test_asset_audit` 76/76 (до зоны — 30/34), `vlm_to_dna` 33, `stand_run` 12;
  калибровка — 18 пар, 108 заданий, заглушки дали 5 из 5; моделей и платных вызовов нет.
- Отступления: в рубриках сняты ещё `repeat_share`, `swap_sides`, вводные — по протоколу; `transcribe` снят из заданий,
  раздел схемы ответа оставлен; `judge-jobs` без `--rubric` — вопросы в строке входа (макет, страница); калибровочная пара
  получает только вопрос рубрики (у `bl-c1-mug`, `ui-settings` вопросы слабые — Ф9); кадры пары близкой пропорции
  приводятся к меньшему размеру; имена ключей группы `judge` и определение «расхождения в сессии» — зоны; исправлен сбой
  `build_page` на малых страницах голосования.
- Стыки: контракт пакета, ключа и ответа, порядок вызова агента и разбора — отчёт C12 §4 (C17 — тексты `claude-design.md
  § 11`, `phases.md` `passport-icons`, `field-checklists.md`, указатель); C13 — метафоры `illustration.metaphors[].id`,
  `vlm_to_dna.py validate`; C14 — `budget.image.hero_mobile_kb`, `audit --mobile`.
- Открыто: тексты базы о судье (ai-media 11/02, 11/01, 15/02 и др.) — Ф10; уточнение вопросов калибровки — Ф9 (JU-20).
- Не прочитано: см. отчёт C12 §8.
- Решения оркестратора (строка DECISIONS «Ф8, зона 12 принята»): отступления приняты; при приёмке — `fast` в описании
  видео схемы арт-дирекции, из `effectiveness.rubric.json#vlm_judge.settings` сняты параметры модели и повторов.

## 12. C11 — project: вход холста и критерии приёмки (29.09, ≈ 63 мин, в уведомлении — 829 тыс. токенов)
- Сделано: новая `scripts/project/canvas_input.py` (2 728: `build <slug> <surface> --stage …`, `check`, `--selftest`);
  форма `REVIEW.md` — колонка «артборды»; фикстуры `input-landing` (поверх `asset-plan`), `input-site` («Сталькон», 15
  планов), `input-cabinet` (`cabinet-ds` + `cabinet-demo`); `smoke/project-canvas.tsv`. 15 действий — отчёт C11 §2.
- Тесты: смоук project PASS 26; самопроверка 38 OK (≈ 29 с); сборка в двух процессах — одинаковые байты; лендинг
  `wireframe` — 7 файлов, `check` 0 `error`, повтор без изменений; правка плана → R-FRESH-002, правка входа →
  R-FRESH-003, `mockup` при copy deck не `approved` → R-MAT-012; поле источника без правила — ошибка с именем поля;
  многостраничник — 15 страниц по карте; кабинет `mockup` — 0 `error`, `copy.md` из `approved`, без ДС — пробел.
- Отступления: проверка входа до публикации — R-MAT-012 (`error`); сайт и кабинет на макете — разная тяжесть текстов (по
  решениям C6, C8); у брифа на вид кабинета нет `x-canvas-map` — проекция правилом сборщика; колонка «этап» и новые id
  пунктов `ACCEPTANCE.md`; ключи `--today`, `--schema`; copy deck фикстуры лендинга — пример text с правками `replace`;
  объём 2,7 тыс. строк.
- Стыки: C13 — `check` (правила, `kind`), передняя часть `INPUT.md`, таблицы `ACCEPTANCE.md`, колонка «артборды»,
  отпечаток входа — sha256 `INPUT.md`; C14 — стабильный вывод `page_gates.py --resolve`; C16 — сборка всех этапов на
  фикстурах `input-*`; C17 — статусы этапов в протоколе и `phases.md`, «Кто собирает», R-MAT-012, указатель (отчёт C11 §4).
- Открыто: `x-canvas-map` брифа на вид — Ф10; пример copy deck «Отвеса» под план главной — Ф10; одно правило текстов
  сайта и кабинета на макете — после пилотов.
- Не прочитано: см. отчёт C11 §8.
- Решения оркестратора (строка DECISIONS «Ф8, зона 11 принята»): отступления приняты, R-MAT-012 — вариант (а); этап
  `motion` у кабинета — отказ с кодом 2 (канон: у кабинета этапа движения нет), правка при приёмке.

## Шаг 0 — вторая локальная сессия (29.09)
- `install.sh --python /usr/bin/python3.13 --groups core,net,morph,svg` — без ошибок (≈ 2 с: npm пересобрал нативный
  `esbuild`); полный смоук — PASS 287, FAIL 0, XFAIL 6, XPASS 3 (как на конец первой сессии).
- Скрипты агентов из scratchpad первой сессии — в журнал: генераторы фикстур с дефектами (`tools/c13/`), генератор и
  пересборка фикстуры `cabinet-ds` (`tools/c5/`). Продолжатели C13 и C14 — по брифам `briefs/C13-cont.md`,
  `C14-cont.md` (решения оркестратора по развилкам C14 — в брифе продолжения).

## 13. C13 — project: манифест готовности и структурный аудит (29.09, три агента: первый оборвался по ошибке API, первый продолжатель остановлен концом сессии; второй продолжатель ≈ 32 мин, в уведомлении — 480 тыс. токенов)
- Сделано: новые `scripts/project/ready.py` (982: `build`, `check` — R-FRESH-006, `show`, `form_errors`),
  `design_audit.py` (2 544: `check` — R-SURF … R-DEBT с вызовом валидаторов баз и утилит `project/`, правила чтением и
  перечень R-VIS в сводке `summary.json`; `visual` — отчёты `mockup_checks` → R-VIS-001); фикстуры `package-landing`,
  `package-cabinet` (чистые основы), `package-landing-defects`, `package-cabinet-defects`, `package-defects` (14
  дефектов); генераторы фикстур — `tools/c13/`; `smoke/project-package.tsv` (+2). 11 действий — отчёт C13 §2.
- Тесты: смоук project PASS 30; самопроверки `ready` 24, `design_audit` 24; `package-defects` — 14 из 14 своим правилом
  и с путём, лишних `error` 0, лишние `warning` и `hint` — данные основ (отчёт C13 §5); `ready build` → `check` — 0.
- Отступления: свои основы фикстур `package-*`; отпечаток одобрения — артборды единицы и `INPUT.md`; `ready show`,
  `design_audit visual`, `--today`, сводка файлом; перевод кодов валидаторов в правила; R-REF-001 шире перечня;
  R-COV-002 счётом; правки второго продолжателя по сверке с реестром (R-REF-006, заметка о несверенной свежести,
  `motion_spec_ref` секций, `group` слота, генерация вне плана ассетов сайта).
- Стыки: вызовы `ready` и `design_audit`, покрытие реестра утилитой — C17; фикстуры с дефектами — вход сценария «пакет»,
  перегенерация генераторами журнала при смене форматов; отказ `page_gates.py --resolve` — находка понятна.
- Открыто: тексты генераторов входа (`review/REVIEW.md` в `ACCEPTANCE.md`, путь строки S23 в контракте) — Ф10.
- Не прочитано: см. отчёт C13 §8.
- Решения оркестратора (строка DECISIONS «Ф8, зона 13 принята»): отступления приняты; основы фикстур — (а); дефект 13
  сверяется по сообщению (строка в `check/KEY-seeded.md`); прогон оркестратора на `package-defects` совпал с ключом.

## 14. C14 — ворота страницы, движения и 3D (29.09; первый агент — до сигнала при ≈ 946 тыс. токенов, продолжатель ≈ 25 мин и доводка ≈ 10 мин, в уведомлении — 441 тыс. токенов)
- Сделано: `page_gates.py` сводит соседей (`--anatomy --accept --motion --gate3d` → вердикт B/S/D, слои эффектов и 3D,
  зеркала D); `page_accept.py` и `gate_check.py` почти переписаны; `motion_check.py`, `page_anatomy.py`, `site_probe.py`,
  `web_view.py` — условия замера из `budgets.yaml conditions`, тишина под тяжёлым замком, честная автоматизация, GSAP по
  рантайму, прогон «постер без 3D»; новый `kb/blender/09-web-runtime/page-3d-gates.yaml`; `effect-gates.yaml` —
  `threshold_ref` у владельцев величин и поле `limits`; по решениям — EG-WEIGHT-11, `level_of` из одной таблицы,
  `PAUSE_LABELS`, телефонные ширины приёмки с DPR телефона. 36 действий — отчёт C14 §2.
- Тесты: самопроверки `page_gates` 106, `page_accept` 23, `motion_check` 63, `plan_to_assets` 53, `marketing_audit` 46,
  `page_anatomy` 32, `gate_check` 12; смоук site, ai-media, creative, blender — 0 FAIL; связка на `01-hero-product` —
  blocked, B 2, S 6, D 1 до и после правок; соседний чекаут — 18 из 18.
- Отступления: строка EG-WEIGHT-11 и поле `limits`; объединение подписей паузы; `acceptance[]` с `device` и `dpr`.
- Стыки: JSON утилит ворот и «кто кого зовёт» — отчёт C14 §4 (C17); `page_gates.py --resolve` без изменений (C11, C13).
- Открыто: калибровка WEB-03, WEB-10, число wasm подачи — Ф9; замер 3D на видеокарте — МЗ; тексты базы о воротах — Ф10.
- Не прочитано: большие утилиты — адресно.
- Решения оркестратора (строка DECISIONS «Ф8, зона 14 принята»): EG-WEIGHT-02 — прежний смысл, wasm подачи — EG-WEIGHT-11;
  копия `page_type_levels.default` снята; десктоп 2 500 у лидогенерации — остаётся; телефонные ширины приёмки — с DPR
  телефона; подписи паузы — один список у трёх потребителей.

## 15. C15 — text: линтер и словари (29.09, ≈ 75 мин, в уведомлении — 933 тыс. токенов)
- Сделано: правки `scripts/text/copy_lint.py` (3 225, +1 420/−200: жанр `interface`, роль — вход с отказом на неизвестной
  роли, типе и части компонента, реестр `texts.md`, межстрочные проверки ux 07/06 §7.3, поправки по жанрам, словарь site
  v1, калибровки К1–К16 и К28, аудит страницы, `--voice`, `--customer-words`, `tell` находок), `ux_dict_to_yaml.py` (640:
  роли §7.2 и `body`, переносимые шаблоны, оговорки ячеек, `delegated`, `role_lengths`, `--selftest` на Python и Node),
  `copy_extract.py` (без маскировки автоматизации, меню первого экрана, id словаря site), своя часть README; kb text —
  профиль `interface`, лексикон (поправки с `genres`, 14 анализаторов, К1, К3, К4, К7, К11, К13, К14, VI-29, TX-23),
  `copy-slots.yaml` (+176/−103: `site_slot` снят, 13 ролей, 11 записей `lint_as`), мета, GEO, набор, рубрика, чек-лист;
  перегенерирован `ux-07-06.yaml`; `tells.yaml` — примета `uniform-card-copy`; фикстуры `cabinet-texts`,
  `cabinet-texts-defects`; журнальный скрипт `tools/c15/copy_slots_tr06.py`. 41 действие — отчёт C15 §2.
- Тесты: смоук text PASS 26; project 30, site 27, creative 22 (+1 XPASS), claude-design 27 — 0 FAIL; самопроверки
  `copy_lint` 86 (сводка уровней по 7 жанрам), `ux_dict_to_yaml` 24 (Python и Node — одни совпадения), `copy_extract` OK;
  `--check` словаря ux — актуален; реестры: `cabinet-texts` — 0 находок, `cabinet-texts-defects` — 4 из 4, `cabinet`
  (C3) — 0 error, 3 warning; 8 примеров copy deck — 0 error.
- Отступления: оговорки ячеек канона — в конвертере (`QUALIFIED`, `NAMING`) до правки канона в Ф10; строки §6.5 —
  `delegated`; длины §12 — в производном словаре; 11 записей `lint_as` (с `email-sender-name`); роли секций — по блокам
  site; К15 — примета поверхности `text`; реестр C3 — 3 warning по канону; `--voice` — EXT с приоритетом 55; у `landing`
  снят повтор `ru-syn-chopped: warning`; строка `copy_metrics.py` README снята.
- Стыки: вызов линтера на реестре и строке, id находок, API — C17, C13 (отчёт C15 §4); `ux_dict_to_yaml.py --check` — C16;
  перегенерация `ux-07-06.yaml` — отдельным коммитом (список изменений — §4); паритет `lint_allow` мета — C8.
- Открыто: тексты `cabinet` — оркестратор; канон ux 07/06 и 07/01 §12 — Ф10; калибровка межстрочных проверок — Ф9;
  тексты под утилиты — C17; провенанс kimi в данных text — Ф10.
- Не прочитано: `in-drafts` (правило); ux 07/03, 07/04 — нужные строки; `copydeck.py`, `canvas_input.py` — места стыков.
- Решения оркестратора (строка DECISIONS «Ф8, зона 15 принята»): отступления приняты; оговорки ячеек канона — в
  конвертере до правки канона в Ф10; фикстура C3 `cabinet` остаётся как есть (три предупреждения линтера верны, чистый
  пример — `cabinet-texts`); `ux-07-06.yaml` — отдельным коммитом; фикстуры пакета пересобраны генератором C16.

## 16. C16 — обслуживание: `scripts/maint/` (29.09, ≈ 45 мин, в уведомлении — 628 тыс. токенов)
- Сделано: новые `scripts/maint/refcheck.py` (300), `mapcheck.py` (175), `canon_check.py` (528), `sync_check.py` (399),
  `fixture_gen.py` (776), данные `maint/data/traces.tsv`, `sync.yaml`, `fixtures.yaml`; правки `check_links.py`
  (+283/−160: раскладка `kb/<база>/`, `--base`, `--all`), справка `count_tokens.py`, `layers.py`, `calibrate.py`,
  `orch_check.py`, `kb/common/README.md` (утилиты проверки `canon.tsv`), `smoke/maint.tsv`. Действия: H10-maint,
  T4-H11, S6-CN-122, TX-01 (часть), F7-Z7b-1, F7-Z9-1, BL-8, DEC-kimi, Р204 (генераторы фикстур), BL-7 (часть).
- Тесты: смоук maint PASS 24; самопроверки 12 + 8 + 20 + 9 + 8 + 47; `refcheck --strict` и `mapcheck` — вывод байт в
  байт как у журнальных (56 файлов); `canon_check` — 0 ошибок, 5 предупреждений; `sync_check` — OK 16, XFAIL 1, копия
  грамматики и описания (17 485) в норме; `fixture_gen --check` — 5 из 5 (до C15); `design_audit --selftest` — 14 из 14
  дефектов; смоук project — PASS 30.
- Отступления: шаблоны следов — данные `traces.tsv`; правила `canon_check` сверх реестра (ключи, «Открытое» с позицией,
  копии — предупреждением); чек-лист site — XFAIL; список синхронности шире брифа; `approve --at` в рецепте;
  `check_links` — соседи по папкам, ролики по форме; `--help` у `orch_check`, `layers`; объём ≈ 2,3 тыс. строк.
- Стыки: указатель `scripts/README.md § maint` — C17 (§4); после C15 — пересборка `package-landing-defects`; шаг 10 —
  `canon_check`, `mapcheck`, `refcheck` после пакета закрытий; VI-02 — правка генератора чек-листа site.
- Открыто: генератор чек-листа site; 4 выровненные копии и TR-04 в `canon.tsv`; копии в журнале (Ф10); мёртвые ссылки
  баз (Ф10).
- Не прочитано: `check_links.py` — адресно; базы — только места находок.
- Решения оркестратора (строка DECISIONS «Ф8, зона 16 принята»): отступления приняты; генератор чек-листа site —
  вариант (а), шаг 10 (путь в скилле, пометки «?» у источников вне скилла, затем снять `xfail`); предупреждения
  `canon_check` — пакет закрытий шага 10.

## Шаг МЗ — машина заказчика (29.09, оркестратор)
- Установка `--all` со старыми `bin/` и `models/`, `--catalogs`, `--check` — 0 ошибок; смоук PASS 305, FAIL 0, XFAIL 2
  (самопроверки каталогов: число цены и дата снимка в коде — Ф9), XPASS 7; тесты Blender 25/25, 4/4.
- BL-3: эталон blender 01 — условный кейс 64 × 24 × 50 мм, пересобран (`blender_run.py build.py`, `make_poster.py`), числа
  прогона в рецепте и копиях обновлены; блоки кода рецептов держат путь `sys.path` к источнику — `run_recipes.py` на них
  не запускать до правки в Ф10.
- Замер 3D на видеокарте — `web_view.py`, `gltf_load_bench.py` на эталоне (числа — Р208). Урок: `web_view.py` пишет в
  `web_stats.json` абсолютные пути модели и кадров — перед записью в пример базы путь делать относительным.
