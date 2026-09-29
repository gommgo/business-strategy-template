# ДФ9 — план разгрузки перед пилотами

ДФ9 убирает из скилла `design-deep-dive` большую часть переусложнения, которое нашли пять агентов перед Ф9 (Р216): стопы
сверх пяти гейтов становятся докладом, хрупкие механизмы (отпечаток одобрения, вход холста на поверхность) — по
единице, код без потребителя и лаборатория уходят `git rm`, шум с понятной правкой снимается. Пороги и эвристики, пользу
которых покажет только пилот, остаются мягким режимом с замером в Ф9; тексты `kb/` — одним проходом в Ф10 (Р132), кроме
строк, которые останавливают пилот. Решение заказчика — Р218; мерило — Р203.

Входы: свод `prep/OVERENG.md` и отчёты `prep/OE-1.md` … `OE-5.md` (разделы 2–4); `PLAN.md` этой папки (Ш0 п. 6, §4, §10
вопрос 7); `ACTIONS.tsv` (строки ДФ9 и `OE…`); `../DECISIONS.md` Р203, Р213–Р218; образец — `../phase-8/PLAN.md` §4–§5;
поправки к общему брифу кода — `briefs/COMMON-DF9.md`, цепочка — `CHAIN.md`, проверка плана — `tools/df9_check.py`;
указатель `scripts/README.md` (кто кого зовёт), списки смоука `scripts/tests/smoke/*.tsv`, `scripts/maint/data/sync.yaml`
и `fixtures.yaml`; стандарт текстов — `../phase-3/SKILL-MAP.md` §7. Класс и зона каждой находки — `DF9-ZONES.tsv`
(`id` · `class` · `zone` · `note`): 114 находок OE и семь пунктов свода §2 (id `OV-1` … `OV-7`).

Счёт по 114 находкам: `правка` 74, `удаление` 11, `замер` 11, `Ф10` 16, `оставить` 2; пункты свода — все `правка`.
Зон 10: восемь кодовых (D1–D5, D6a, D6b, D7) и две текстовые (D8, D9); пар 5; ≈ 13 ч работы агентов и ≈ 2–2,5 ч
приёмки и шагов оркестратора; вместе с проверкой ДФ9 и агентом сценариев — две длинные сессии (§9). Удаляются 18 файлов
(лаборатория, код без потребителя), 9 подкоманд (7 у `chain_inputs`, `verify-page` и `upgrade` у `copydeck`) и мёртвые
ветки; стопы сверх пяти гейтов, которые нашёл свод, становятся докладом.

Пути: `SK` = `.claude/skills/design-deep-dive/`; `scripts/…`, `kb/…`, `references/…` — от `SK`; `_template/` —
`docs/projects/_template/`. Маски файлов зон — от корня репозитория (их берёт `ZONE_GLOBS` журнального
`../phase-8/tools/accept.py`). База ДФ9 — коммит `7e6d57e`.

## 1. Способ

- **Как Ф8.** Зоны с непересекающимися файлами, агенты парами (не больше двух одновременно), бриф зоны
  `briefs/D<N>.md` — перед парой, общий бриф кода `../phase-8/briefs/COMMON.md` с поправками `briefs/COMMON-DF9.md`,
  коммит «на приёмке» сразу после агента, приёмка по §5, строка DECISIONS «ДФ9, зона D<N> принята» и запись `CHAIN.md`.
  Следующая пара — после приёмки обеих зон.
- **Код раньше текстов.** Семь кодовых зон меняют поведение утилит и пишут, что меняется в текстах, разделом отчёта «Для
  текстов»; тексты скилла правят две текстовые зоны последней пары (D8 — процесс и канон слоёв, D9 — холст, аудит и
  указатель). Почему так, а не «зона правит свои тексты»: `phases.md`, `claude-design.md`, `rules.md` и указатель
  `scripts/README.md` задевает смысл почти каждой кодовой зоны — будь тексты у кодовых зон, эти четыре файла держали бы
  пары последовательно и разгрузка шла бы по одной зоне; тексты описывают утилиты, которые уже есть (урок C17 Ф8);
  правило «гейт или доклад» пишется одним голосом в одном месте (`phases.md § Принципы всех этапов`), остальные тексты на
  него ссылаются (SKILL-MAP §7). Исключения: README доменов `scripts/<домен>/README.md` переписывает кодовая зона домена —
  она знает свои утилиты; строки `kb/`, которые останавливают пилот, правит зона, которая меняет утилиту, — зона их
  называет.
- **Удаление — часть зоны.** Файлы из списка зоны агент снимает `git rm -q` (папку — `git rm -rq`), вызывающее место в
  своих файлах — в той же зоне (§4 «Удаление»).
- **Контракты между зонами** — §4; меняются только через оркестратора. Главные: партия входа холста и источники
  единицы (D1 пишет, D2 читает).
- **Шаг оркестратора Р** — в приёмке пары 3: `canon.tsv` ссылается на удалённые `make_skeleton.py` и
  `copy_extract.py` (§4 «Реестр»).
- **Где.** Локальная сессия на машине заказчика (Р187): окружение `$DDD_HOME`, смоук и фикстуры — там. Push — в
  `github main` после каждого агента и каждой приёмки, как в Ф8.

## 2. Зоны

У каждой зоны: файлы и маски; находки (`DF9-ZONES.tsv`, колонка `zone`); что делает; что удаляет — с доказательством
«никто не зовёт» (поиск — в `note` строки); строки `kb/`, которые правит; синхронность (фикстуры, смоук, ключ); проверка
с ожидаемым выводом; что передаёт текстовым зонам. Везде: справка своих файлов — о текущем поведении (forward-only);
снимая стоп, зона понижает тяжесть находки и оставляет правило и совет, а не глушит её (урок Ф8, `CHAIN.md`).

### D1 — вход холста: гейт 2, единицы, критерии приёмки (пара 1; ≈ 80–90 мин)
- **Файлы:** `scripts/project/canvas_input.py`, `contract.py`, `ds_coverage.py`; фикстуры с входом холста
  (`package-cabinet-defects`, `package-defects` — пересборка `fixture_gen.py`); списки смоука `project-canvas.tsv`,
  `project-demo.tsv`, `project-ds.tsv` — если меняются строки.
- **Маски файлов:** `.claude/skills/design-deep-dive/scripts/project/canvas_input.py`,
  `.claude/skills/design-deep-dive/scripts/project/contract.py`,
  `.claude/skills/design-deep-dive/scripts/project/ds_coverage.py`,
  `.claude/skills/design-deep-dive/scripts/tests/fixtures/*`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/project-canvas.tsv`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/project-demo.tsv`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/project-ds.tsv`
- **Находки:** OE1-01, OE1-03, OE1-04, OE1-05, OE1-06, OE1-07, OE1-10, OE1-13, OE1-14, OE5-03, OE5-04, OE5-05, OV-1
  (часть входа и приёмки), OV-3.
- **Что делает:**
  1. Гейт и сигнал в проверке входа (§4 «Тяжесть проверки входа»): `R-MAT-012 error` — только гейт 2 и целостность
     входа; остальные точки — `warning` с тем же правилом и советом. Итог манифеста «этап не публикуется» — только при
     `error`.
  2. Партия входа: `build` и `check` принимают `--page ID[,ID…]` (сайт) и `--screen SLUG[,…]` (кабинет); без ключа —
     все единицы, как сейчас. Во входе — только единицы партии (`pages/<id>/`, разделы экранов `contract.md`, строки
     `copy.md`, демо-набор); их список — поле `units` передней части `INPUT.md`; единицы вне партии — строка «Пробелов»
     («вне партии: …»), их находки во вход не идут. `check` без ключа берёт партию из `INPUT.md`; `build` чистит папки
     страниц вне партии. У кабинета гейт текстов и «экран stable» — у экранов партии.
  3. Источники единицы для отпечатка одобрения — функции `unit_sources()` и `unit_fingerprint()` (контракт — §4); сама
     зона отпечаток не считает.
  4. `x-*` на любом уровне документа — расширение, не поле; поле без правила `x-canvas-map` — `R-FRESH-003 warning`,
     вход собирается (флаг `blocked` снят).
  5. Критерии приёмки (`site_items`, `app_items`, `common_items`): `B` остаётся у честности — группа B (B1–B3) и J3 —
     и у пунктов места «после сборки» (гейт 5); прочие `B` места «макет» — `S`. C4 — «нет кластера примет бан-листа;
     одиночная примета — вопрос заказчику». B1 и B2 кабинета — способ «глаза»: скрипта сверки с `demo-data.json` нет.
     Бан-лист в брифе исполнителя не меняется — рабочая форма для Opus.
  6. `contract.py`: пункты PRE (`R-MAT-011`) — `warning` на обоих этапах; `R-MAT-003` о строках `texts.md` — как было
     (на макете вход делает из него `R-MAT-012` — гейт 2).
  7. `ds_coverage.py`: `severity()` — `error` только у поверхности кабинета на макете и только для «тип без ключа или
     компонента», форм и расширений; «не нарисовано состояние» — `warning`; у сайта `R-COV-005` — `warning` всегда.
- **Удаляет:** ветку `ban_list` «приметы прошлой итерации» (`review/checks.json`) и разбор строки «Проверки макета» в
  `artifacts()` (поле `checks`) — `checks.json` пишет только заглушка самопроверки `design_audit.py`, поле никто не
  читает (OE1-07). Файлов не снимает.
- **Строки kb:** нет.
- **Синхронность:** `fixture_gen.py build package-cabinet-defects package-defects`, затем `build --all --check` —
  совпадает; `sync_check.py all` — 0 (строки `canvas-input-*` принимают код 0 и 1, `fixtures` — совпадает). Ключ:
  сценарии 1 и 2 — счёт тот же (0 · 4 · 6 и 1 · 1 · 0), меняются только сообщения; сценарий 4B — меньше `error` у
  `otves-office` (вход без `R-MAT-012` сверх гейта); посевы `KEY-seeded.md` не мягчают (R-COV-005 посева — «тип без
  компонента» на макете кабинета — остаётся `error`).
- **Проверка:** `canvas_input.py --selftest`, `contract.py --selftest`, `ds_coverage.py --selftest` — OK, с новыми
  случаями: партия `--page`, гейт 2 — единственный `error`, `x-*` во вложенном поле, непокрытое поле — `warning` и вход
  записан, отпечаток единицы не меняют правка соседней страницы и даты в `ARTIFACTS.md`, меняет правка своего текста.
  На сборках фикстур (`fixture_project.py build <имя>`, `--today 2026-09-29`):
  - `input-site`, `check stalkon corp --stage mockup` — до правки 34 `error` (copy deck 15, план ассетов 15,
    арт-дирекция, ДС, публикация ДС, факты); после — 16 `error` (тексты 15, факты 1), план ассетов, арт-дирекция и ДС —
    `warning`; с `--page home` — 2 `error` (тексты `home`, факты), остальные 14 страниц — строка «вне партии»;
  - `input-landing`, `--stage mockup` — до 5 `error`, после 3 (тексты — 2, факты — 1); `--stage wireframe` — 0 · 4 · 6,
    как в ключе;
  - `input-cabinet`, `--stage mockup` — 1 `error` (тексты 45 строк — гейт 2) · 1 `warning`, как в ключе; с
    `--screen plan-dashboard` — тот же гейт у одного экрана.
  `smoke.py --only scripts/project` — 0 FAIL.
- **Для текстов:** `phases.md` (`canvas-input`, `wireframe`, `mockup`, §4 PRE), `claude-design.md` (§ Вход холста,
  § Приёмка), `rules.md` (R-MAT-012, R-MAT-011, R-COV-005, R-FRESH-003), указатель (строки `canvas_input`,
  `ds_coverage`, `contract`) — ключи, тяжести, партия.

### D6b — приёмка ассетов (пара 1; ≈ 45 мин)
- **Файлы:** `scripts/ai-media/asset_audit.py`, `tests/test_asset_audit.py`, `check_icons.py`, `palette.py`.
- **Маски файлов:** `.claude/skills/design-deep-dive/scripts/ai-media/asset_audit.py`,
  `.claude/skills/design-deep-dive/scripts/ai-media/tests/test_asset_audit.py`,
  `.claude/skills/design-deep-dive/scripts/ai-media/check_icons.py`,
  `.claude/skills/design-deep-dive/scripts/ai-media/palette.py`
- **Находки:** OE3-05, OE3-06, OE3-16, OE3-21; часть OE3-17 (мёртвые ветки).
- **Что делает:** правила шапки и штриха Lucide — только у набора Lucide: ключ набора у `audit` (умолчание — Lucide) и
  `check_icons.py`, у другого набора эти флаги — `warn`; `QA-PROV-VISIBLE-MARK` — `warn` с листом углов вместо
  `needs_human`; нет моделей OCR или бинарника — строка «поставьте `install.sh --groups ocr --models`» (или `--bin`)
  вместо хвоста трассировки; `palette.py` — командная строка (картинки → палитра JSON, `--k`, `--json`), модульный вызов
  не меняется.
- **Удаляет:** мёртвые ветки `asset_audit.py` — путь `EXP / "L"` и модуль `ab_analyze` (файла нет; поиск по `.claude/` —
  других упоминаний в коде нет). Файлов не снимает.
- **Строки kb:** нет. Смоук не трогает: строку `palette.py` (`import-only` → `help`) переводит D6a в паре 4.
- **Проверка:** `asset_audit.py selftest` и `tests/test_asset_audit.py` — зелёные (76 проверок и новые: Heroicons
  «home» при наборе не Lucide — `warn`, не fail; Lucide — как было); `audit --slot hero --ocr off` на кадрах
  `assets/calibration/` 17-f04 и 19-e08 — без `needs_human` от метки в углу (набор только читается, Р109);
  `palette.py <картинка> --json` — палитра; `smoke.py --only scripts/ai-media` — 0 FAIL.
- **Для текстов:** указатель (строки `asset_audit`, `check_icons`, `palette`), README ai-media (D6a), `phases.md`
  (`assets`, `passport-icons`, `design-system` — палитра ассетов командой).

### D2 — приёмка и пакет (пара 2; ≈ 75–85 мин)
- **Файлы:** `scripts/project/ready.py`, `design_audit.py`; формы `_template/design/_template/REVIEW.md` и `ready.yaml`;
  фикстуры `package-landing-defects`, `package-defects` (пересборка); список смоука `project-package.tsv`.
- **Маски файлов:** `.claude/skills/design-deep-dive/scripts/project/ready.py`,
  `.claude/skills/design-deep-dive/scripts/project/design_audit.py`,
  `docs/projects/_template/design/_template/REVIEW.md`,
  `docs/projects/_template/design/_template/ready.yaml`,
  `.claude/skills/design-deep-dive/scripts/tests/fixtures/*`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/project-package.tsv`
- **Находки:** OE1-02, OE1-08, OE1-11, OE1-12, OE1-21, OE4-07, OE4-08, OE5-02, OE5-10, OV-2; часть OE1-01 (R-COV-002) и
  OE1-13 (R-MAT-005).
- **Что делает:**
  1. Отпечаток одобрения — по единице (§4 «Источники единицы»): `sha256` строк «артборды:<`dc_to_html.fingerprint`
     артбордов>» и «источники:<`canvas_input.unit_fingerprint`>»; `ready show` печатает его для колонки «отпечаток»
     `REVIEW.md`; `R-MAT-004` и `fresh_adaptive` (`R-FRESH-005` адаптивной копии) сверяют с ним. Пересборка входа, дата
     в `ARTIFACTS.md`, `starter` в `system.yaml`, вход `motion` и правка соседней единицы одобрение не снимают.
  2. `ready`: единица готова по гейтам 2–4 и закрытой композиции (план `approved`, экран `stable`): тексты `approved`,
     факты публикуемы или пробел назван, макет принят с совпавшим отпечатком (или пропущен решением). ДС не утверждена,
     покрытие ДС (по типам своего экрана, а не всей поверхности) и FSD-карта не `stable` — строки `open` единицы для
     решения заказчика, не `blockers`.
  3. `R-MAT-005` по единице: у таблицы «Пункты ACCEPTANCE» `REVIEW.md` — необязательная колонка «страница или экран»;
     непройденный пункт с единицей держит только её, без единицы — все принятые единицы, как сейчас.
  4. `R-COV-002`: «страница передана в дизайн» — страница в партии текущего входа (`pages/<id>/` или `units` из
     `INPUT.md`) или со строкой «Приёмка» в `REVIEW.md`.
  5. `R-FRESH-005` статичных копий и `kit.json` (`fresh_copies`) — `warning`, пока в `ARTIFACTS.md` нет строки «Проверки
     макета: разрешены»; с просьбой — `error`, как было.
  6. `R-COV-008` (`cov_receivers`): получатели — `analytics.crm` и `constraints.integrations` брифа; каналы конверсии —
     не получатели; совпадение со строкой `integration.md` — по любому слову получателя.
  7. Формы: `REVIEW.md` — отпечаток «артборды и источники единицы», колонка единицы у пунктов; `ready.yaml` — `open`
     несёт и решения заказчика (ДС, покрытие, FSD).
- **Удаляет:** нет.
- **Строки kb:** нет.
- **Синхронность:** `fixture_gen.py build package-landing-defects package-defects`, затем `build --all --check`;
  `sync_check.py all` — 0 (`ready-landing`, `ready-cabinet`, `fixtures`). Ключ: сценарий 4A — те же блокеры единиц
  (план `proposed`, текстов нет, макета нет; `spasibo` — тексты `draft`, макета нет), без «ДС не утверждена» в
  `blockers`; 4B — счёт пересчитывает оркестратор (§3 «Синхронность»), все 14 посевов — тем же правилом и путём.
- **Проверка:** `ready.py --selftest`, `design_audit.py --selftest` — OK (package-landing и package-cabinet — 0 `error`;
  package-defects — 14 посевов, лишних `error` нет), с новыми случаями: правка даты «последнего чтения» в
  `ARTIFACTS.md` и пересборка входа — отпечаток единицы тот же; правка copy deck соседней страницы — тот же; правка
  артборда или своего текста — другой, `R-MAT-004`; FSD-карты нет — единица готова, строка `open`. `smoke.py --only
  scripts/project` — 0 FAIL.
- **Для текстов:** `claude-design.md § Приёмка`, `phases.md` (`acceptance`, `package`), `design/README.md § Пакет для
  кода`, `rules.md` (R-MAT-004, R-MAT-005, R-COV-002, R-COV-008, R-FRESH-005), указатель (`ready`, `design_audit`).

### D5 — проверки макета (пара 2; ≈ 80–90 мин)
- **Файлы:** `scripts/claude-design/mockup_checks.py`, `literal_tokens.py`, `copies_compare.py`, `dc_to_html.py`
  (одна строка сообщения), `kit/diffshots.py`, `kit/marks.js`, `kit/export.py` (заголовки), `shot_v3.py` (снятие);
  `scripts/ui/ui_audit.py`; список смоука `claude-design.tsv`.
- **Маски файлов:** `.claude/skills/design-deep-dive/scripts/claude-design/mockup_checks.py`,
  `.claude/skills/design-deep-dive/scripts/claude-design/literal_tokens.py`,
  `.claude/skills/design-deep-dive/scripts/claude-design/copies_compare.py`,
  `.claude/skills/design-deep-dive/scripts/claude-design/dc_to_html.py`,
  `.claude/skills/design-deep-dive/scripts/claude-design/shot_v3.py`,
  `.claude/skills/design-deep-dive/scripts/claude-design/kit/diffshots.py`,
  `.claude/skills/design-deep-dive/scripts/claude-design/kit/marks.js`,
  `.claude/skills/design-deep-dive/scripts/claude-design/kit/export.py`,
  `.claude/skills/design-deep-dive/scripts/ui/ui_audit.py`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/claude-design.tsv`
- **Находки:** OE4-01, OE4-02, OE4-03, OE4-04, OE4-05, OE4-06, OE4-12, OE4-14, OE4-15, OE4-21; строка про Node из
  OE4-16.
- **Что делает:** `mockup_checks`: примета срабатывает только на своей поверхности (`surface` реестра `tells.yaml`);
  одиночная примета вида — `minor` (вопрос), `major` — кластер реестра, код выхода 2 — `critical` или кластер;
  `M-NAV` — `major` (как пункт D2 приёмки); `LOOK-SERIF-DISPLAY` и `LOOK-BG-WARM` молчат, когда гарнитура или цвет фона —
  значение токенов из `--tokens`; табличный `copy.md` кабинета разбирается, ключ `--demo demo-data.json` — числа и записи
  демо-набора не дают `HON-NUMBERS` и `HON-COPY`. `literal_tokens`: семейство `size` и образцы цветовых твиков не
  сверяются, `--accepted` не повышает до `error`. `copies_compare`: артборды страницы «Состояния» — вне автоматических
  пар (только `--pairs`). `ui_audit` A2: значение со шкалы токенов (`--tokens`) — не находка. `dc_to_html`: сообщение
  «нужен Node … (системный Node; путь — `kbpaths.py --bins`)» — без «install.sh ставит Node». Заголовки `kit/` — без
  агента и даты. Функции, которые читает `canvas_input` (`literal_tokens.load_tokens`, `kit_manifest.classes`), не
  меняются.
- **Удаляет:** `scripts/claude-design/shot_v3.py` (`git rm`) и его строку в `claude-design.tsv` (OE4-14: поиск
  `shot_v3` по `.claude/` — этапы, аудит, утилиты не зовут; указатель — D9; строка kb cd 06-design-process/README.md —
  список Ф10).
- **Строки kb:** нет (реестр `tells.yaml` не меняется: его читает и вход холста).
- **Синхронность:** фикстуры с собранными файлами не задевает; `sync_check.py all` — 0. Ключ не меняется (сценарии
  утилит макета не зовут).
- **Проверка:** `mockup_checks.py selftest`, `literal_tokens.py --selftest`, `copies_compare.py --selftest`,
  `dc_to_html.py --selftest`, `ui_audit.py --selftest` — OK, с новыми случаями: синтетика `analyze(surface='app')` с рядом
  «12 · 4 · 3 · 87 %» — без `LOOK-STATS-ROW`; одиночная `LOOK-THREE-CARDS` — `minor`, код 0; `M-NAV` на посадочной без
  меню — `major`; `copy.md` кабинета с `--demo` — без `HON-NUMBERS`. `literal_tokens.py scan
  kb/claude-design/05-design-artifacts/example --tokens …` — до правки 26 находок, после — без 9 размеров и 2 образцов
  твика (≈ 15). `smoke.py --only scripts/claude-design` и `--only scripts/ui` — 0 FAIL; браузерные прогоны — только при
  ≥ 2 ГБ свободной памяти.
- **Для текстов:** `claude-design.md` (§ Проверки по постоянной просьбе, § Правки токенов — строка «раскладка
  артборда»), `rules.md` (R-VIS-001, R-VIS-004), указатель (строки утилит `claude-design`, `ui_audit`; снятая
  `shot_v3`).

### D3 — тексты страницы (пара 3; ≈ 80–90 мин)
- **Файлы:** `scripts/text/copydeck.py`, `claims_check.py`, `chain_inputs.py`, `validate_voice.py`, `README.md`;
  снятие `copy_extract.py`, `check_intake.py`, `make_skeleton.py`; схема `kb/text/10-templates-recipes/
  copy-deck.schema.json` (поле `claims_allow`); строка S3 `kb/text/09-ai-generation-evaluation/02-generation-pipeline.md`;
  фикстуры `package-landing-defects`, `package-defects` (пересборка); список смоука `text.tsv`.
- **Маски файлов:** `.claude/skills/design-deep-dive/scripts/text/copydeck.py`,
  `.claude/skills/design-deep-dive/scripts/text/claims_check.py`,
  `.claude/skills/design-deep-dive/scripts/text/chain_inputs.py`,
  `.claude/skills/design-deep-dive/scripts/text/validate_voice.py`,
  `.claude/skills/design-deep-dive/scripts/text/copy_extract.py`,
  `.claude/skills/design-deep-dive/scripts/text/check_intake.py`,
  `.claude/skills/design-deep-dive/scripts/text/make_skeleton.py`,
  `.claude/skills/design-deep-dive/scripts/text/README.md`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/text.tsv`,
  `.claude/skills/design-deep-dive/scripts/tests/fixtures/*`,
  `.claude/skills/design-deep-dive/kb/text/10-templates-recipes/copy-deck.schema.json`,
  `.claude/skills/design-deep-dive/kb/text/09-ai-generation-evaluation/02-generation-pipeline.md`
- **Находки:** OE2-02, OE2-04, OE2-07 (README text), OE2-09 (строка kb), OE2-10, OE2-12, OE2-13, OE2-19, OE2-21,
  OE2-22.
- **Что делает:** `approve`: пустые `meta.title` и `meta.description` — `warning`, утверждение проходит (ворота
  публикации — `validate --final`, как было); `claims_allow` слота и страницы — список `{rule, reason, by}` только для
  `COPY-F-CLASS` и `COPY-F-NUM`: запись `claims` считает `error` без обойдённых, `approve` и `--final` их чтут, вывод
  `check` перечисляет обходы заметкой; схема copy deck — поле `claims_allow` (слот и страница) с `drop` в `x-canvas-map`
  (`spec_check.py canvas-map` — 0); сообщения без «урок «Кварца»» и «Решение заказчика п. 16»; `meaning-claims` не
  сверяет возражения, страхи и альтернативы; `claims_check lint-facts`: разрешение `pending` — `warning` до `--final`;
  `validate_voice`: отрицательные мутации — только в `--selftest`; строка S3 text 09/02 §1.1 — «доля допущений выше 30 %
  — доклад заказчику по счётчикам `basis_kinds` (`validate_any.py`)»; README text — утилита → вызов → выход, за
  ключами — `--help`. API `copydeck`, которое читают `canvas_input`, `ready`, `design_audit` и `fixture_gen`
  (`deck_root`, `pages_of`, `sections_of`, `slots_of`, `chosen_variant`, `_status_of`, `text_hash`, `export_copy_md`,
  `copy_md_rules`, `Facts`, `export_facts_md`, `fact_source_line`, `norm_ws`, `COPY_TITLE`, `COPY_RULE`), не меняется.
- **Удаляет** (`git rm`; доказательства — `note` строк OE2-10, OE2-12, OE2-13): `scripts/text/copy_extract.py`,
  `check_intake.py`, `make_skeleton.py`; в `copydeck.py` — `verify-page` (`cmd_verify_page`, `run_copy_extract`, ключи
  `--extract`, `--html`, `--browser`, `--url`), `upgrade` (`upgrade_deck`, `cmd_upgrade`) и ветки v0 (`COPY-D-V0`); в
  `chain_inputs.py` — `digest-meaning`, `hierarchy-input`, `section-input`, `edit-input`, `assemble`, `apply-edits`,
  `canvas-texts` (остаются `meaning-claims`, `judge-input`, `judge-score`); упоминания `make_skeleton` в справке
  `copydeck.py` и `chain_inputs.py`; строки `text.tsv`; журнальные разделы README text. `before-after` остаётся —
  генератор `text-before-after` в `sync.yaml`. Упоминания в `phases.md`, `_template/site/README.md`, указателе — D8 и
  D9; в `canon.tsv` — шаг оркестратора Р; в текстах kb — список Ф10 (§9).
- **Синхронность:** `fixture_gen.py build package-landing-defects package-defects`, `build --all --check`;
  `sync_check.py all` — 0 (`text-before-after`, `canvas-maps`, `fixtures`); `smoke.py --validate` и `--uncovered` —
  чисто. Ключ: сценарий 4B — меньше находок R-STRUCT-003 (pending фактов, пустая мета), посевы 5, 6, 14 — прежние.
- **Проверка:** `copydeck.py --selftest` (с новыми случаями: `approve` без меты — утверждено с `warning`; `claims_allow`
  на «Зарплата и кадры» — `approve` проходит, обход в выводе; `claims_allow` на `COPY-L-*` не снимает находку),
  `claims_check.py --selftest`, `chain_inputs.py --selftest`, `validate_voice.py` (с файлом проекта — без строк
  мутаций), `copydeck.py before-after --check` — OK; эталон `meaning-otves.yaml` через `meaning-claims` → `copydeck.py
  claims` — до 8 · 53 · 78, после — без находок на возражениях и страхах (число — в отчёт); `smoke.py --only
  scripts/text` — 0 FAIL.
- **Для текстов:** `phases.md` (`meaning`, `copy` стр. 372, `copy-audit`, §3), `_template/site/README.md` (стр. 201,
  шаги цепочки), `design-audit/SKILL.md` (обходы — `claims_allow`), указатель (строки `copydeck`, `chain_inputs`,
  `validate_voice`; снятые утилиты).

### D4 — сайт и подача (пара 3; ≈ 65–75 мин)
- **Файлы:** `scripts/site/site_validate.py`, `page_anatomy.py`, `README.md`; `scripts/creative/spec_check.py`,
  `ad_check.py`, `README.md`, снятие `idle_probe.py`; схема `kb/creative/09-ai-execution-evaluation/
  art-direction.v1.schema.json`; списки смоука `site.tsv`, `creative.tsv`.
- **Маски файлов:** `.claude/skills/design-deep-dive/scripts/site/site_validate.py`,
  `.claude/skills/design-deep-dive/scripts/site/page_anatomy.py`,
  `.claude/skills/design-deep-dive/scripts/site/README.md`,
  `.claude/skills/design-deep-dive/scripts/creative/spec_check.py`,
  `.claude/skills/design-deep-dive/scripts/creative/ad_check.py`,
  `.claude/skills/design-deep-dive/scripts/creative/idle_probe.py`,
  `.claude/skills/design-deep-dive/scripts/creative/README.md`,
  `.claude/skills/design-deep-dive/kb/creative/09-ai-execution-evaluation/art-direction.v1.schema.json`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/site.tsv`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/creative.tsv`
- **Находки:** OE2-01, OE2-08, OE2-14, OE2-15, OE2-16, OE2-18, OV-6; README site из OE2-07.
- **Что делает:** `PJ-03` у страницы брифа типа `thank-you-page`, `legal-page`, `not-found-page` — `warning`; `SB-D02` и
  `SB-A02` — `warning`, сообщения `SB-D01`, `SB-D02`, `SB-A02`, `PL-P03`, `PL-O02` — без номеров решений заказчика и
  букв агентов; самопроверка и `--all` по примерам базы — на закреплённой дате примеров 2026-09-29 (`--today`
  переопределяет); `spec_check plan`: нормы облика `TR-*` — `warning` (схема `TR-S` и уровень эффекта — как было),
  `PL-C01` несёт их уровень; `ad_check`: меньше трёх направлений, различие пары меньше двух осей, меньше трёх
  материальных семейств — `warning`; схема арт-дирекции `directions.minItems` 3 → 1 (примеры базы проходят);
  `page_anatomy`: сеть только ключом `--net`, по умолчанию без сети; README site — о текущем; README creative — без
  `idle_probe`. `spec_check.canvas_check`, `ptr_match`, `cmd_spec`, `moment_line` и `Ctx`, которые читает вход холста,
  не меняются.
- **Удаляет:** `scripts/creative/idle_probe.py` (`git rm`) и его строку `creative.tsv`: поиск `idle_probe` по
  `.claude/` — код, этапы, аудит и ворота после сборки (`page_gates`) не зовут, покой холста у 3D меряет `site_probe`;
  указатель — D9; рецепты creative 10 и глоссарий kb — список Ф10.
- **Строки kb:** только схема арт-дирекции (данные, совместимое ослабление).
- **Синхронность:** фикстуры с собранными файлами не задевает; `sync_check.py all` — 0 (`site-checklist`,
  `site-crosswalk`, `creative-levels`, `canvas-maps`). Ключ: сценарий 4B — меньше `error` R-STRUCT-002 (PJ-03 служебных
  страниц, SB-D02, SB-A02) и R-STRUCT-004 (`ad_check`); проверка самопроверки `design_audit` «советы SB-* — этап
  brief» держится на находках любой тяжести.
- **Проверка:** `site_validate.py --selftest` — OK и с `--today 2026-11-02` (мина снята); `site_validate.py <сборка
  input-landing>/…/site/promo` — до 7 `error` (PJ-03 ×5, PL-F00, SB-F01), после — PJ-03 `error` только у `guide`
  (`article-page`), у `spasibo`, `privacy`, `consent`, `not-found` — `warning`; `--all --quiet` — 0 `error`;
  `spec_check.py --selftest`, `canvas-map`, `levels --check` — OK; `ad_check.py --selftest` и по примерам базы — 0
  `error`; `page_anatomy.py --selftest` — OK без сети. `smoke.py --only scripts/site`, `--only scripts/creative` —
  0 FAIL.
- **Для текстов:** `phases.md` (`page-plan`, `design-handoff`, `moodboard`, `art-direction`: число направлений при
  строгом бренде), `rules.md` (R-STRUCT-002, R-STRUCT-004), указатель (`site_validate`, `page_anatomy --net`,
  `spec_check`, `ad_check`, снятый `idle_probe`).

### D6a — генерация (пара 4; ≈ 75–85 мин)
- **Файлы:** `scripts/ai-media/routing_check.py`, `prompt_compile.py`, `tests/test_prompt_compile*.py`, `stand_run.py`,
  `README.md`; снятие `vm_sheet.py`, `validate_recipes.py`; строки kb: `kb/ai-media/README.md`,
  `14-recipes/00-cheatsheet.md`, `14-recipes/01-hero-recipes.md`, `14-recipes/04-capability-map.md`; список смоука
  `ai-media.tsv`.
- **Маски файлов:** `.claude/skills/design-deep-dive/scripts/ai-media/routing_check.py`,
  `.claude/skills/design-deep-dive/scripts/ai-media/prompt_compile.py`,
  `.claude/skills/design-deep-dive/scripts/ai-media/tests/test_prompt_compile*.py`,
  `.claude/skills/design-deep-dive/scripts/ai-media/stand_run.py`,
  `.claude/skills/design-deep-dive/scripts/ai-media/vm_sheet.py`,
  `.claude/skills/design-deep-dive/scripts/ai-media/validate_recipes.py`,
  `.claude/skills/design-deep-dive/scripts/ai-media/README.md`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/ai-media.tsv`,
  `.claude/skills/design-deep-dive/kb/ai-media/README.md`,
  `.claude/skills/design-deep-dive/kb/ai-media/14-recipes/00-cheatsheet.md`,
  `.claude/skills/design-deep-dive/kb/ai-media/14-recipes/01-hero-recipes.md`,
  `.claude/skills/design-deep-dive/kb/ai-media/14-recipes/04-capability-map.md`
- **Находки:** OE3-01, OE3-02, OE3-04 (README ai-media), OE3-10, OE3-15, OE3-17, OE3-23, OV-4, OV-7 (часть).
- **Что делает:** `routing_check`: снимки каталогов по умолчанию — последние в `$DDD_HOME/cache/ai-media`, проверка
  ссылок на опыты фазы 5 (`phase5_test`) снята, справка — о текущем; `prompt_compile`: снимок каталога читается только
  командами, которым он нужен (`--help`, `ratios`, `validate` без `--model` отвечают без снимка); `jobs` по умолчанию —
  одно задание (диалект семейства, 1 повтор, без сидов, тега и агента опыта), A/B — явными ключами; `stand_run collect`:
  путь паспорта — от корня выходов (`relative_to`), `--root` без папки агента E; README ai-media — утилита → вызов →
  выход, за ключами — `--help`, с правками D6b; строка смоука `palette.py` — `help`. Строки kb: шпаргалка 14/00 «Перед
  работой» (стр. 9–17) и чек-лист (стр. 106–113), README ai-media (стр. 38–42), карта 14/04 (стр. 367) — «перед
  платным вызовом — `estimate` без ошибок и «да» заказчика; снимки, `routing_check` и сверка баланса — сигнал»; рецепт
  hero 14/01 стр. 96–108 — вызовы `$DDD_HOME/venv/bin/python scripts/ai-media/…`, `jobs … --out $DDD_HOME/out/…`, без
  `99-raw/tools`, `venv-D2` и `99-raw/phase5/jobs`.
- **Удаляет:** `scripts/ai-media/vm_sheet.py`, `validate_recipes.py` (`git rm`) и их строки `ai-media.tsv`: поиск по
  `.claude/` — код, этапы, аудит, фикстуры не зовут, `validate_recipes` читает `99-raw` и падает на всех рецептах;
  упоминания в kb — список Ф10. Журнальные разделы README ai-media (OE3-04). Остаются до Ф10 — обслуживание матрицы
  маршрутов и сценарии (`note` OE3-17).
- **Синхронность:** фикстуры не задевает; `sync_check.py all` — 0. Ключ не меняется.
- **Проверка:** `routing_check.py` без аргументов — на последних снимках в `$DDD_HOME` без ошибок `phase5_test`; код 0
  или только настоящие расхождения моделей и цен — списком в отчёт (до правки — «снимок не найден», со снимками 29.09 —
  137 ошибок у 29 из 33 маршрутов, настоящих — 0); `prompt_compile.py --help` при пустом `DDD_HOME` — справка; `jobs
  <спецификация> --models <модель>` без ключей — 1 задание, `polza.py estimate` — цена одного задания (до правки —
  6 заданий: 24 ₽ вместо 4 ₽ у модели прогона OE-3); тесты `test_prompt_compile.py` (98) и `test_prompt_compile_x2.py`
  (15) — зелёные;
  `stand_run.py selftest` — OK, `collect --root <папка паспортов вне kb>` — без трассировки; `smoke.py --only
  scripts/ai-media` — 0 FAIL (XFAIL — прежние, с причиной).
- **Для текстов:** `kb/INDEX.md` (стр. 223–224) и `phases.md` (`asset-plan`, `assets`) — D8; указатель (строки
  ai-media, снятые утилиты, «Подробный README домена») — D9.

### D7 — 3D, окружение и обслуживание (пара 4; ≈ 65–75 мин)
- **Файлы:** снятие `scripts/blender/vote/`, `scripts/blender/regression/`, `scripts/maint/orch_check.py`,
  `calibrate.py`, `calibration.json`, `count_tokens.py`, `layers.py`; правка `scripts/blender/qa_pipeline.py`,
  `gate_check.py`, `README.md`, `scripts/install.sh`, `package.json`, `scripts/maint/check_links.py` (комментарий),
  `SK/.gitignore` (строки `vote/`); строки kb: `kb/common/judge.md` §7, `kb/blender/README.md` (стр. 54, 61); списки
  смоука `blender.tsv`, `maint.tsv`.
- **Маски файлов:** `.claude/skills/design-deep-dive/scripts/blender/vote/*`,
  `.claude/skills/design-deep-dive/scripts/blender/regression/*`,
  `.claude/skills/design-deep-dive/scripts/blender/qa_pipeline.py`,
  `.claude/skills/design-deep-dive/scripts/blender/gate_check.py`,
  `.claude/skills/design-deep-dive/scripts/blender/README.md`,
  `.claude/skills/design-deep-dive/.gitignore`,
  `.claude/skills/design-deep-dive/scripts/install.sh`,
  `.claude/skills/design-deep-dive/scripts/package.json`,
  `.claude/skills/design-deep-dive/scripts/maint/orch_check.py`,
  `.claude/skills/design-deep-dive/scripts/maint/calibrate.py`,
  `.claude/skills/design-deep-dive/scripts/maint/calibration.json`,
  `.claude/skills/design-deep-dive/scripts/maint/count_tokens.py`,
  `.claude/skills/design-deep-dive/scripts/maint/layers.py`,
  `.claude/skills/design-deep-dive/scripts/maint/check_links.py`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/blender.tsv`,
  `.claude/skills/design-deep-dive/scripts/tests/smoke/maint.tsv`,
  `.claude/skills/design-deep-dive/kb/common/judge.md`,
  `.claude/skills/design-deep-dive/kb/blender/README.md`
- **Находки:** OE3-07, OE3-11, OE3-12, OE4-16, OE4-18; README blender из OE3-04 и OV-7.
- **Что делает:** `gate_check.py` — код 1 только при строке B; `qa_pipeline.py page` — вердикт fail только при строке B
  (тяжесть B/S/D из `gate_check.evaluate`), S и D — в отчёте; `install.sh` — неработающий esbuild — предупреждение, а
  не отказ установки; `package.json` — без восьми пакетов песочницы испытания 15-showcase (строка `x-ddd-used-by`
  «песочница испытания 15-showcase (npm-trial)»); README blender — утилита → вызов → выход, за ключами — `--help`, без
  журнала исследования; `judge.md` §7 — страница пар 3D-кадров — общая `stand_run.py page` (протокол судьи не меняется);
  `kb/blender/README.md` — строки 54 (голосование) и 61 (маршрут «Проверить готовое» без прогона регрессии).
- **Удаляет** (`git rm`; доказательства — `note` OE3-11, OE3-12, OE4-18): `scripts/blender/vote/` (`build_pairs.py`,
  `tally.py`, `vote_server.py`, `index.html`) и пять строк `.gitignore`; `scripts/blender/regression/`
  (`make_manifest.py`, `run_set.py` — падают при импорте); `scripts/maint/orch_check.py`, `calibrate.py`,
  `calibration.json`, `count_tokens.py`, `layers.py`; их строки `blender.tsv` и `maint.tsv`. Остаются: `check_links`
  (ссылки kb для уборки Ф10), `run_recipes`, `run_doc_blocks`, `fx_probe`, `anim_diff`, `sheet`, `d1exp` — Ф10.
- **Синхронность:** фикстуры не задевает; `sync_check.py all` — 0; смоук `kb.tsv` (компиляция эталонов blender) не
  меняется. Ключ не меняется.
- **Проверка:** до снятия пакетов песочницы — поиск их имён (`gsap`, `lenis`, `maath`, `troika-three-text` и др.) по
  `scripts/` и спискам смоука: импортов и путей в `$DDD_HOME/node` нет (`site_probe`, `web_view`, `motion_check`,
  `marketing_audit` распознают библиотеки на чужой странице по рантайму, а не грузят пакеты; код 3D-рецептов 13–17 в kb
  — список Ф10);
  `gate_check.py --selftest` — OK, с новым случаем: только S — код 0; `qa_pipeline.py --help` — как было (`help rc=3`
  без Blender); `install.sh --dry-run` — план npm без пакетов песочницы; после приёмки оркестратор запускает `install.sh`
  (переустановка npm по новому `package.json`), затем `install.sh --check` — 0 ошибок;
  `check_links.py --selftest`, `refcheck.py --selftest` — OK; `smoke.py --only scripts/blender`, `--only scripts/maint`,
  `--only scripts/install.sh` — 0 FAIL; `smoke.py --validate`, `--uncovered` — чисто.
- **Для текстов:** указатель (снятые утилиты и данные `maint/calibration.json`, строки `gate_check`, `qa_pipeline`,
  «Подробный README домена»), `docs/getting-started.md` — не меняется (ключи установки те же).

### D8 — тексты: процесс и канон слоя страницы (пара 5; ≈ 80–90 мин)
- **Файлы:** `SKILL.md`, `references/phases.md`, `draft-stable.md`, `workflow-patterns.md`, `field-checklists.md`,
  `knowledge-base.md`; `_template/site/README.md`; строки `kb/INDEX.md`.
- **Маски файлов:** `.claude/skills/design-deep-dive/SKILL.md`,
  `.claude/skills/design-deep-dive/references/phases.md`,
  `.claude/skills/design-deep-dive/references/draft-stable.md`,
  `.claude/skills/design-deep-dive/references/workflow-patterns.md`,
  `.claude/skills/design-deep-dive/references/field-checklists.md`,
  `.claude/skills/design-deep-dive/references/knowledge-base.md`,
  `docs/projects/_template/site/README.md`,
  `.claude/skills/design-deep-dive/kb/INDEX.md`
- **Находки:** OE2-06, OE2-20, OE3-14, OE3-18, OE4-09, OE4-10, OE5-01, OE5-06, OE5-07, OE5-08, OE5-14, OE5-15, OE5-16,
  OE5-17, OE5-20, OE5-24, OE5-25, OV-5; разделы «Для текстов» зон D1–D7 о своих файлах.
- **Что делает:** `phases.md` § Принципы всех этапов — единственное место правила «жёстко — пять гейтов, остальное —
  доклад»; §9 «Не пропускаются никогда» → «обязательные артефакты маршрута: пропуск — долг в заметке, остановка — только
  гейт» и SKILL.md «Ворота не пропускаются» — ссылкой туда (OE5-01); §0 «`/design-audit` в цепочке» — на переходах
  утилита `design_audit check`, скилл — перед итоговым коммитом и по просьбе (OE5-08); §3 — S1–S11 — карта шагов, а не
  «ни один шаг не пропускается»; S10 по желанию, S11 открытым выбором (OE5-07); `meaning` — доля допущений докладом
  (OE5-17); `funnel` — получатель в брифе, строка `integration.md` долгом (OE5-16); `copy` — без `make_skeleton`;
  `copy-audit` — одна команда `copydeck.py check` (OE2-06); `design-handoff` — SITE-PRE-25 перед `mockup`, SITE-PRE-26
  «не применимо» (OE5-15); `art-direction`, порядок ассетов — паспорт при генерации (OE3-14, OE5-14), число направлений
  (D4); `design-system`, `style-tiles` — контраст пар `color.py contrast` (OE4-09, OV-5), палитра ассетов командой
  `palette.py` (D6b); `ds-components` — конвенция `data-state` (D1), иллюстрации кабинета (OE3-18); `canvas-input`,
  `wireframe`, `mockup` — партия `--page`/`--screen`, `error` входа — гейт 2 (D1); `fix-round` — «по просьбе» (OE4-10,
  OE5-24); `acceptance`, `package` — B/S и FSD (D1, D2); §10 — у L0 нет `motion` (OE5-25). `draft-stable.md` — закрытие
  на переходе этапа (OE5-06); `workflow-patterns.md` — точки сохранения (OE5-08); `_template/site/README.md` — стр. 201,
  «шаги цепочки не пропускаются», правка заказчика на холсте (OE5-11); `kb/INDEX.md` — стр. 223–224 (`routing_check` —
  сигнал, OV-4), стр. 340 (`refs_client` — по просьбе, OE2-20), стр. 342 (контраст — `color.py`, OE4-09).
- **Удаляет:** упоминания снятых утилит в своих файлах (поиск имён из §4 «Удаление» по маскам зоны — 0).
- **Синхронность:** `sync_check.py descriptions` — описание SKILL.md не растёт; `mapcheck.py kb/INDEX.md` — без новых
  «НЕ НОРМА»; `refcheck.py --strict` по правленым md — 0 в тронутых строках.
- **Проверка:** чтение по стандарту SKILL-MAP §7; поиск «не пропускается», «0 error», «≥ 1 находка»,
  `build_reference_tokens`, `make_skeleton`, `routing_check.*0 ошибок` по маскам зоны — только законные места.
- **Для текстов:** —.

### D9 — тексты: холст, аудит и указатель (пара 5; ≈ 80–90 мин)
- **Файлы:** `references/claude-design.md`; `.claude/skills/design-audit/SKILL.md`, `references/rules.md`;
  `scripts/README.md`; `_template/design/README.md` и формы `_template/design/_template/` (кроме правок D2).
- **Маски файлов:** `.claude/skills/design-deep-dive/references/claude-design.md`,
  `.claude/skills/design-audit/SKILL.md`,
  `.claude/skills/design-audit/references/rules.md`,
  `.claude/skills/design-deep-dive/scripts/README.md`,
  `docs/projects/_template/design/*`
- **Находки:** OE3-19, OE4-11, OE4-13, OE5-11, OE5-12; части OE2-07, OE3-04, OE4-09, OE4-10, OE5-08, OE5-10, OE5-14;
  разделы «Для текстов» зон D1–D7.
- **Что делает:** `claude-design.md` — вход «0 ошибок» → `error` входа только гейт 2 и партия (D1); приёмка — B/S,
  отпечаток единицы (D1, D2); свежий аудит — ноль находок законен (OE4-11, OE5-12); «варианты макета» —
  `stand_run.py page` (OE4-13); правки заказчика на холсте — откат только при фактах и праве (OE5-11); контраст —
  `color.py` (OE4-09); раунд правок — проверки по просьбе (OE4-10); копии — свежесть `warning` без просьбы (D2).
  `rules.md` — тяжести правил по «Для текстов» (R-MAT-012, R-MAT-011, R-MAT-004, R-MAT-005, R-COV-002, R-COV-005,
  R-COV-008, R-FRESH-003, R-FRESH-005, R-VIS-001, R-VIS-004, R-STRUCT-002, R-STRUCT-004; строка 162 — контраст); формат
  заголовков `### R-… «…» · \`тяжесть\`` не меняется — его читает `design_audit.rules_catalog()`.
  `design-audit/SKILL.md` — когда звать скилл (OE5-08), обходы — и `claims_allow` (D3). `scripts/README.md` — строки
  снятых утилит и данных (§4 «Удаление»), новые ключи (`--page`, `--screen`, `--net`, набор иконок, `palette.py`),
  «Подробный README домена» → «за ключами — `--help`, README домена — назначение и вызов», § Ворота после сборки — коды
  замеров не решают (OE3-19). `_template/design/README.md` — пакет без условия FSD (OE5-10), паспорт при генерации
  (OE5-14), покрытие — `data-state` (D1).
- **Удаляет:** упоминания снятых утилит в своих файлах.
- **Синхронность:** `design_audit.py --selftest` — OK (реестр читается, R-VIS — пять правил); `sync_check.py
  descriptions` — описание `design-audit` не растёт; `refcheck.py --strict` по правленым md — 0 в тронутых строках.
- **Проверка:** каждая строка указателя — утилита есть (`ls`), ключи — как в `--help`; поиск имён снятых утилит по
  маскам зоны — 0.
- **Для текстов:** —.

## 3. Порядок пар

| пара | зоны | почему так |
|---|---|---|
| 1 | D1 ∥ D6b | D1 меняет контракт входа холста (партия, тяжести) и даёт источники единицы — их читает D2; фикстуры входа пересобирает только D1; D6b ни от кого не ждёт и ничьих выходов не меняет, её правки опишет README ai-media в паре 4 |
| 2 | D2 ∥ D5 | D2 — после D1 (`unit_fingerprint`, партия входа); фикстуры пакета пересобирает только D2; D5 фикстур не задевает и функций, которые читает вход холста, не меняет |
| 3 | D3 ∥ D4 | D3 пересобирает те же фикстуры copy deck, что D2 (`package-landing-defects`, `package-defects`), поэтому не в паре с ней; D4 фикстур не задевает; шаг оркестратора Р — в приёмке этой пары, до полного смоука |
| 4 | D6a ∥ D7 | D6a — после D6b: README ai-media описывает приёмку ассетов уже с её правками; D7 ни от кого не ждёт; обе без фикстур |
| 5 | D8 ∥ D9 | тексты описывают утилиты, которые уже есть; «Для текстов» всех кодовых зон собраны; правило «гейт или доклад» — одно место (`phases.md`), D9 на него ссылается |

Длинные цепочки — D1 → D2 → тексты, D6b → D6a → тексты. После пары 5 — проверка ДФ9 (§6). Остановка — только если
шаг задевает решения заказчика (§8, спорные места) или приёмка не сошлась.

## 4. Сквозные правила

### Пять гейтов и мягкий режим (Р203)
Жёстко работу останавливают пять гейтов: (1) генерация — только по утверждённому заказчиком плану ассетов; (2) чистовой
макет — только на утверждённых текстах и подтверждённых фактах; (3) в публикацию не уходят демо-факты, заглушки и
утверждения без источника; (4) пакет для кода — только принятый макет с совпавшим отпечатком; (5) ворота после сборки
блокируют только B. Остальное — доклад: находка остаётся с тем же правилом и советом, тяжесть — `warning` (или `hint`),
код выхода — по контракту находок (1 — только при `error`), решает заказчик, обход — с записанной причиной. Снятый стоп
не глушится: тихий пропуск прячет дефект.

**Тяжесть проверки входа холста** (D1; тексты — D8, D9):

| остаётся `error` | становится `warning` |
|---|---|
| на макете у единиц партии: тексты не статуса этапа, слоты плана без текста, copy deck страницы нет (гейт 2) | план страницы не утверждён (вайрфрейм и макет) |
| факты не `confirmed`, факт без источника, фактов нет (гейт 2) | арт-дирекции нет, не утверждена, направление не выбрано |
| токенов ДС нет — облик рисовать не из чего | ДС не утверждена, не опубликована (нет адреса в `ARTIFACTS.md`) |
| источник не разбирается, нет брифа или ни одного плана, остаток шаблона во входе | план ассетов не утверждён или его нет (без генерации — не гейт 1); файл ассета без файла или лицензии |
| кабинет на макете: строки `texts.md` не `approved` у экранов партии (гейт 2) | поля референса мудборда; набор формы не из `lead-forms.yaml`; профиль бюджета не резолвится |
| — | пункты PRE (`R-MAT-011`), находки `ds_coverage` о состояниях, `ds_build` (`R-FRESH-001`) внутри проверки входа |
| — | движение: статичный макет не принят, нет спецификации, ошибки `spec_check spec`; поле без правила `x-canvas-map` |

### Партия входа холста (D1 пишет; D2, D8, D9 читают)
- `canvas_input build|check <slug> <surface> [--page ID[,ID…] | --screen SLUG[,…]] --stage …`; без ключа — все единицы.
- Передняя часть `INPUT.md` — поле `units: [<id>…]`; «Пробелы» — строка «вне партии: …»; `pages/<id>/` — только у
  страниц партии (`build` снимает папки остальных); у кабинета разделы экранов `contract.md`, строки `copy.md` и
  записи демо-набора — только экранов партии; `ACCEPTANCE.md` — пункты по партии.
- `check` без `--page`/`--screen` берёт партию из `units` действующего входа.

### Источники единицы и отпечаток одобрения (D1 пишет функцию, D2 — отпечаток)
- `canvas_input.unit_sources(slug, surface, unit, repo=None)` → строки `{id, path, fingerprint}`;
  `canvas_input.unit_fingerprint(slug, surface, unit, repo=None)` → `"sha256:…"` по отсортированным строкам «id · путь:
  отпечаток» или `None`, если единицы нет.
- Страница сайта: план страницы; copy deck — `text_hash` выбранных текстов этой страницы; план ассетов страницы и файлы
  её слотов по манифесту; спецификация движения страницы; факты, на которые ссылаются её слоты данных и `fact_ids`
  текстов (записи фактов); уровень продукта — токены ДС (`system.tokens.css`, иначе DTCG), `system.yaml` без поля
  `starter`, бренд, арт-дирекция поверхности.
- Экран кабинета: файл экрана, его блоки и каркас по дереву, строки `texts.md`, которые он называет (ключ, текст,
  статус); токены ДС, `system.yaml` без `starter`, бриф на вид.
- Не входят: `ARTIFACTS.md`, `REVIEW.md`, `INPUT.md` и файлы входа, файлы `kb/`, `review/*`, заметки state, копии
  холста.
- Отпечаток одобрения (D2) — `sha256` строк «артборды:<`dc_to_html.fingerprint` артбордов единицы>» и
  «источники:<`unit_fingerprint`>»; его печатает `ready show`, пишет этап `acceptance` в колонку «отпечаток»
  `REVIEW.md`; `R-MAT-004`, `ready` и `fresh_adaptive` сверяют с ним.

### Удаление
- Файл из списка зоны агент снимает `git rm -q` (папку — `git rm -rq`), другие команды git, меняющие индекс или рабочее
  дерево, не выполняет (`briefs/COMMON-DF9.md`).
- До снятия — поиск вызывающих по имени во всём `.claude/` и `docs/` (`grep -rn <имя>`). Импорт, строка смоука,
  фикстура, строка `scripts/maint/data/*.yaml` в файлах зоны снимаются в той же зоне. Упоминание в текстах скилла
  (`SKILL.md`, `references/`, `.claude/skills/design-audit/`, `scripts/README.md`, `_template/`) удаление не держит: зона
  пишет его в «Для текстов», снимает текстовая зона пары 5 — так указатель и `phases.md` не держат пары. Упоминание в
  текстах `kb/` — в список Ф10 (§9), кроме строк, которые зона называет. Вызов из файла другой зоны или из кода вне
  списка — удаление не делается, запись в отчёт.
- Список снятых файлов ДФ9 (18): `scripts/text/copy_extract.py`, `check_intake.py`, `make_skeleton.py` (D3);
  `scripts/creative/idle_probe.py` (D4); `scripts/claude-design/shot_v3.py` (D5); `scripts/ai-media/vm_sheet.py`,
  `validate_recipes.py` (D6a); `scripts/blender/vote/` — `build_pairs.py`, `tally.py`, `vote_server.py`, `index.html`,
  `scripts/blender/regression/` — `make_manifest.py`, `run_set.py`, `scripts/maint/orch_check.py`, `calibrate.py`,
  `calibration.json`, `count_tokens.py`, `layers.py` (D7). Внутри файлов: подкоманды `chain_inputs` (7), `copydeck
  verify-page` и `upgrade`, ветки v0, ветки `asset_audit` к `99-raw` и `ab_analyze`, ветка `checks.json` входа холста.
- Решения заказчика и ядро свода §5 не снимаются: пять гейтов, калибровочный набор `assets/calibration/`, утверждение
  плана ассетов, судья — Opus по `kb/common/judge.md`, модель — только Opus, ключи — вне репозитория; контур честности
  текстов, линтер, `canvas_input` как сборщик, `ds_build` и покрытие ДС, `ready`, пакеты судьи, компилятор промтов и
  приёмка ассетов, ворота после сборки, обслуживание `sync_check`, `refcheck`, `canon_check`, `mapcheck`, `fixture_gen`.

### Реестр норм — шаг оркестратора Р (приёмка пары 3)
`kb/common/canon.tsv` собирает журнальный `../phase-4/tools/registry.py canon` из узлов `../phase-4/nodes/*.tsv`, а
`canon_check` (он в смоуке: `maint.tsv`) проверяет, что пути копий есть. После D3 в копиях остаются пути снятых файлов:
TR-04 — `scripts/text/copy_extract.py` (снять из списка копий), TR-54 — `scripts/text/make_skeleton.py` (копия нормы
«каркас — из анатомии блока и плана» теперь `scripts/text/copydeck.py`: `skeleton` строит каркас из плана и анатомии
блока), CN-95 — `scripts/text/copy_extract.py` (снять). Оркестратор до полного смоука пары: правка трёх строк узлов
`02-TR.tsv` и `10-CN.tsv` (колонка копий) → `registry.py check` → `merge` → `canon` → `canon_check.py` — 0 →
`mapcheck.py kb/INDEX.md` — без новых «НЕ НОРМА»; коммит `docs(research)` и `refactor(design-deep-dive)` по
содержанию. Остальные снятые файлы в узлах не названы (поиск по `../phase-4/nodes/` — 0); `asset_inventory.py` в CN-95,
CN-96 остаётся; строка нормы с `verify-page` в тексте (не путь) — Ф10.

### Синхронность фикстур, смоука и ключа
- **Фикстуры с собранными файлами** (`scripts/maint/data/fixtures.yaml`, рецепты не меняются): у пары один владелец —
  D1 (`package-cabinet-defects`, `package-defects`), D2 (`package-landing-defects`, `package-defects`), D3
  (`package-landing-defects`, `package-defects`); `cabinet-ds` и `package-landing` не меняются. Владелец —
  `fixture_gen.py build <имена>`, затем `build --all --check` — совпадает; дифф фикстур — в отчёт.
- **`sync.yaml`** — без правок: строки `canvas-input-*` принимают код 0 и 1, `text-before-after` остаётся,
  `fixtures` — совпадает после пересборки. `sync_check.py all` — 0 после каждой зоны.
- **Смоук** — снимаются 18 строк: `text.tsv` 3, `creative.tsv` 1, `claude-design.tsv` 1, `ai-media.tsv` 2,
  `blender.tsv` 6, `maint.tsv` 5; `palette.py` в `ai-media.tsv` — `import-only` → `help` (D6a). Новых строк нет: новое
  поведение держат самопроверки. `smoke.py --validate` и `--uncovered` — чисто; полный смоук — PASS меньше на снятые
  проверки, FAIL 0, XFAIL — прежние две с причиной.
- **Ключ сценариев** `../phase-8/check/KEY.md` правит оркестратор по разделам «Для ключа» отчётов после пары 3 и в
  проверке ДФ9 повтором `../phase-8/tools/ct_prepare.sh <папка> key`. Ожидание:

| сценарий | что меняется | откуда |
|---|---|---|
| 1 — лендинг, вход вайрфрейма | счёт 0 · 4 · 6 тот же, 7 файлов; в `INPUT.md` — поле `units`; сообщения | D1 |
| 2 — кабинет, вход макета | 1 `error` (45 строк — гейт 2) · 1 `warning`, код 1 — те же | D1 |
| 3 — ДС | без изменений | — |
| 4A — манифест | блокеры единиц те же (план, тексты, макет); ДС, покрытие, FSD — строки `open`, а не блокеры | D2 |
| 4B — аудит | `otves-remont-nn` 9 · 18 · 11 — меньше находок: PJ-03 служебных страниц, SB-D02 и SB-A02, `ad_check`, `pending` фактов, пустая мета, свежесть копий без просьбы; `otves-office` 5 · 5 · 0 — `error` не больше; числа — по `ct_prepare` | D1–D4 |

  `KEY-seeded.md` — без правок: мягче не стал ни один из 14 посевов (R-COV-002 посева — copy deck закрыт, `error`;
  R-COV-005 — тип без компонента на макете кабинета, `error`; R-MAT-008 — генерация до утверждения плана, гейт 1;
  R-FRESH-001, -003, -006, R-REF, R-SURF, R-STRUCT-006 — не тронуты).

### Тексты вслед за кодом
- Кодовая зона пишет «Для текстов»: файл, раздел, что было и что стало по смыслу (без готовых формулировок —
  формулирует D8 или D9 по стандарту SKILL-MAP §7). Текстовые зоны получают отчёты D1–D7 и этот план.
- Правило «гейт или доклад» — `phases.md § Принципы всех этапов`; `SKILL.md`, `claude-design.md`, `design-audit/SKILL.md`,
  `rules.md` ссылаются на него, а не пересказывают.
- Строки `kb/` правит только зона, которая их называет (D3, D6a, D7, D8); остальная проза `kb/` — Ф10 (Р132).
- Описания скиллов (`description` в `SKILL.md`) не растут: `sync_check.py descriptions` — 0.

### Forward-only и код
Справка, докстринги и сообщения тронутых файлов — о текущем поведении: без агентов, волн, фаз, дат, Р-номеров и
«было / стало» (урок: `routing_check.py`, `kit/*`, сообщения `site_validate` и `copydeck`); данные с датой (снимки) —
данные. Правка по месту, без переформатирования. Пути — через `kbpaths` и `docpaths`; сеть и траты — только явными
ключами; платных вызовов и `--live` нет.

## 5. Приёмка зоны (оркестратор)

0. Агент закончил — его файлы и отчёт `reports/D<N>.md` одним коммитом и push, до приёмки: `feat(design-deep-dive): …,
   на приёмке` (по содержанию, без имён фаз).
1. `python3 ../phase-8/tools/accept.py D<N> --base <коммит до пары> --smoke <папки зоны>`: файлы — только под масками
   зоны (маски §2 — в `ZONE_GLOBS`, `phase-9/reports/*` — в `ALWAYS`); снятые файлы — из списка §4 и `git ls-files` их
   не видит; md — `refcheck --strict`; JSON и YAML разбираются, схемы — метасхема; в `.py` — без следов журнала.
2. Находки зоны (`DF9-ZONES.tsv`, колонка `zone`) — в таблице отчёта с местом и способом проверки; чтение мест правки.
3. Ожидаемое из §2 зоны — повтор команд оркестратором на свежих сборках фикстур; расхождение — разбор с агентом, а не
   правка ожидания.
4. Самопроверки и тесты зоны — зелёные; `smoke.py --only <папки>` — 0 FAIL; `--validate`, `--uncovered` — чисто.
5. Синхронность: владелец фикстур пары — `fixture_gen.py build --all --check` совпадает; `sync_check.py all` — 0;
   после пары 3 — шаг Р (§4) до полного смоука.
6. Стоп → доклад: выборочно — находка снятого стопа осталась с правилом, советом и тяжестью `warning`, код выхода 0.
7. Удаления: `grep -rn <имя>` по `.claude/` и `docs/` — остались только места, отданные в «Для текстов» или в список Ф10.
8. Полный смоук — в конце пары, после приёмки обеих зон: 0 FAIL (память — ≥ 2 ГБ свободных до запуска).
9. Строка DECISIONS «ДФ9, зона D<N> принята» (время — из уведомления), запись `CHAIN.md` из отчёта, «Для ключа» — в
   `KEY.md` (после пары 3 и в §6), «Для текстов» — в бриф D8 или D9; коммиты правок приёмки и журнала; push; итог в чат.

Правка по замечанию — тот же агент продолжением или оркестратор, если правка мелкая.

## 6. Проверка ДФ9

- **Смоук:** `python3 scripts/tests/smoke.py` (из `SK`) — 0 FAIL, XFAIL — только с причиной (самопроверки цен каталогов);
  `--validate`, `--uncovered` — чисто.
- **Синхронность:** `scripts/maint/sync_check.py all` — 0 FAIL (генераторы, фикстуры, копия грамматики, описания);
  `scripts/maint/fixture_gen.py build --all --check` — 5 из 5 совпадают.
- **Статика:** `python3 research/design-build/phase-8/tools/static_check.py --base 7e6d57e` — 0: `refcheck --strict` по md,
  правленым в ДФ9 (тронутые строки), следы в `scripts/`, разбор YAML, JSON и frontmatter, схемы kb и примеры баз
  (в том числе схемы арт-дирекции и copy deck после D4, D3), `mapcheck`, `canon_check`, `sync_check`, реестр и
  `canon.tsv` байт в байт после шага Р, тесты `scripts/*/tests/` (`test_asset_audit`, `test_prompt_compile`,
  `test_prompt_compile_x2`).
- **Снятое:** `git ls-files` — нет 18 файлов §4; поиск их имён и снятых подкоманд (`verify-page`, `upgrade_deck`,
  `digest-meaning`, `hierarchy-input`, `section-input`, `edit-input`, `apply-edits`, `canvas-texts`) по `SKILL.md`,
  `references/`, `.claude/skills/design-audit/`, `scripts/`, `_template/` — 0; в `kb/` — только список Ф10.
- **Мягкий режим на фикстурах** (§2): `input-site --stage mockup` — `error` только тексты и факты, с `--page home` —
  2; `input-landing` — вайрфрейм 0 · 4 · 6, макет 3 `error`; `site_validate` на `input-landing` — PJ-03 `error` только у
  `guide`; `site_validate.py --selftest --today 2026-11-02` — OK; `routing_check.py` — код 0; `prompt_compile jobs` —
  одно задание; `ready`: одобрение переживает пересборку входа и дату в `ARTIFACTS.md` (самопроверка `ready`).
- **Сценарии:** `research/design-build/phase-8/tools/ct_prepare.sh <папка> key` — совпадает с `KEY.md` после правок
  оркестратора; свежий агент сценариев по `../phase-8/check/BRIEF-CT.md` (ответы — `../phase-8/check/runs.md` или
  `phase-9/check/runs.md` по решению оркестратора) — 4 из 4 «верно», 14 из 14 посевов своим правилом и путём, лишних
  `error` нет; находки о текстах — правка оркестратором или строка Ф9.
- **Окружение:** после `install.sh` (npm по новому `package.json`) — `install.sh --check` — 0 ошибок.
- **План:** `python3 research/design-build/phase-9/tools/df9_check.py coverage` и `masks` — чисто (проверено при
  написании плана: 121 строка, 114 находок ровно по разу; пересечений масок в парах нет).

## 7. Готово, когда

- зоны D1–D9 (с D6a, D6b) приняты: строки DECISIONS, коммиты, push;
- шаг Р сделан: узлы, реестр и `canon.tsv` байт в байт, `canon_check` — 0;
- проверка §6 чистая, сценарии — 4 из 4, `KEY.md` приведён к выводу;
- `ACTIONS.tsv` — строки с `ДФ9` отмечены сделанными; `PLAN.md` Ф9 — без обходов, которые снял ДФ9 (служебные планы
  заранее, одобрения одним проходом, вход после закрытия всех страниц), журнал замера — с находками класса `замер`;
  список Ф10 (§9) — в `../PLAN.md` «Ф10»; STATE и `NEXT-SESSION-PROMPT.md` — под старт Ф9 со словом заказчика.

## 8. Риски и спорные места

- **D1 — самая большая зона** (≈ 90 мин, вход холста 2,8 тыс. строк) → бриф называет функции (`assemble_site`,
  `assemble_app`, `site_items`, `app_items`, `common_items`, `ban_list`, `artifacts`, `render_manifest`, `freshness`,
  `check_surface`, `write_input`, `cmd_build`); при нехватке контекста — отчёт по текущему состоянию, остаток
  (критерии приёмки, `ds_coverage`) — продолжатель той же зоны до пары 2.
- **Два агента задели один файл** → маски пар не пересекаются (`tools/df9_check.py masks`); фикстуры — один владелец на
  пару; указатель, `phases.md`, `claude-design.md`, `rules.md` — только пара 5.
- **Контракт партии и источников единицы разошёлся у D1 и D2** → форма — §4; D2 начинает с `unit_fingerprint` из отчёта
  D1; приёмка D2 гоняет связку на фикстуре.
- **Понижение тяжести спрятало дефект** → находка остаётся с правилом и советом; приёмка сверяет ожидаемые счета §2;
  сценарий 4B и посевы — в §6.
- **Шаг Р забыт** → `canon_check` в смоуке падает на путях снятых файлов; шаг — пункт 5 приёмки пары 3.
- **Снятая утилита упомянута в kb** → пилот не идёт по этим разделам (лаборатория, 3D, рецепты цепочки промтов);
  список Ф10 (§9) — вход уборки kb.
- **Два текстовых агента пишут одно правило по-разному** → правило живёт в `phases.md § Принципы`, D9 ссылается;
  приёмка пары 5 читает стык (`claude-design.md § Приёмка` и `phases.md acceptance`, `rules.md` и § Принципы).
- **Память машины** (15 ГБ, два агента и смоук) → браузерные прогоны — при ≥ 2 ГБ свободной памяти; полный смоук — у
  оркестратора в конце пары.

Спорные места — решает оркестратор (строкой DECISIONS), план идёт по рекомендации:
1. **`claims_allow` (OE2-04).** Текст схемы copy deck говорит: «ложную находку сверки лечат правкой текста или
   facts.yaml». Р203 новее: обход — с записанной причиной. План: обход только для эвристик `COPY-F-CLASS` и `COPY-F-NUM`,
   с причиной и тем, кто решил; право, `never_claim` и «утверждение шире факта» не обходятся; `--final` обход чтит и
   перечисляет. Иначе — `замер`, и пилот упрётся в подгонку текста под корень слова.
2. **`regression/` blender (OE3-12) против Р58** («регрессионный набор пересоздаём на пилотах»). Код падает при импорте,
   3D в пилотах нет, Р218 новее — снять; пересоздание, если понадобится, — из истории git.
3. **`kb/common/judge.md` §7 (OE3-11).** Правится одна строка — страница пар 3D-кадров — общая `stand_run.py page`;
   протокол судьи (рубрика, слепота, прогоны) не меняется. Если оркестратор считает строку частью протокола — `vote/`
   остаётся до Ф10, OE3-11 — класс `Ф10`.
4. **Готовность без утверждённой ДС (OE1-12).** План: ДС, покрытие и FSD — строки `open`, жёстко — гейты 2–4 и закрытая
   композиция. Альтернатива — оставить «ДС не утверждена» блокером (облик макета — из ДС).
5. **Имя расширения DTCG `org.ui-research.*` (OE4-22)** — вне ДФ9: ≈ 366 мест в нормах ui и creative; решить до первой
   ДС пилота — «оставить осознанно» (рекомендация, переименование — Ф10) или правка в ОП1.
6. **`stand_page.py` (OE4-13)** остаётся: на нём стенд T-1 Ф9 и `judge-jobs --from-stand-page`; правится только строка
   протокола холста.

## 9. Что остаётся Ф9 и Ф10

**Оценка.** Пять пар, десять зон: D1 ≈ 90, D6b ≈ 45, D2 ≈ 80, D5 ≈ 85, D3 ≈ 85, D4 ≈ 70, D6a ≈ 80, D7 ≈ 70, D8 ≈ 85,
D9 ≈ 85 мин — ≈ 13 ч агентов; по парам (длиннейшая зона) ≈ 7 ч, приёмка ≈ 2 ч, шаг Р ≈ 20 мин, проверка ДФ9 со
сценариями ≈ 1–1,5 ч — ≈ 10–11 ч, две длинные локальные сессии. P0 (калибровка судьи) идёт параллельно, как в плане Ф9.

**Замер в Ф9** (класс `замер`, строки журнала замера пилотов): OE1-09 каскад правки токена и хвост README артефакта ДС;
OE1-20 вес входа и пересборки; OE2-03 круги «правка → утверждение»; OE2-05 плотность маркеров на утверждённых текстах;
OE3-08 лимиты трат пилота; OE3-09 маршруты вне компилятора; OE4-19 пресеты `ui_audit` у кабинета; OE4-20 загрузки
`/_blob` в копиях; OE5-09 токены до первого вайрфрейма; OE5-13 адаптивная копия — время и польза; OE5-22 служебные
страницы. И части правок: доля «не применимо» в наборах состояний (OE1-10), срабатывания C4 (OE1-14), доля ложных
COPY-F-CLASS и COPY-F-NUM и обходы `claims_allow` (OE2-04), висячие предлоги и COPY-F-NAME (OE2-21), `QA-COLOR-WARM` без
паспорта (OE3-06), допуск литералов (OE4-06), короткие страницы в парах копий (OE4-21), цена судьи текстов (OE5-07).

**Ф10** (класс `Ф10` и хвосты правок):
- тексты `kb/` одним проходом (Р132): упоминания снятых утилит и подкоманд — поиск имён §4 по `kb/` (≈ 60 файлов: промты
  и цепочка text 09/02, рецепты creative 10, база ai-media 13–15, blender 11, README баз с `orch_check`, cd 06
  README), витрина 15-showcase, `99-raw`, `PLAN.md` баз, бандлы three.js (OE3-22), рецепты 3D с путём машины и
  `rk.out_dir` (OE3-13), блоки команд с путём машины и шаблон «путь машины» в `traces.tsv` (OE4-15), §8–§9 процедуры
  site 10/01 (OE2-17), строка site 10/01 §1.2 о статусе подачи L0 (OE5-25), cd 06/04 §9 (OE4-11), одно правило — одна
  копия (OE5-21);
- код: один порядок кодов выхода (OE1-15), ошибка разбора первой (OE1-16), опорная дата демо-набора (OE1-17), одна
  декларация проекции (OE1-19), ширины проекта (OE1-22), список критериев приёмки данными базы (OE1-13), право только в
  сверке фактов (OE2-11), TR-07/08 выводить (OE2-15), исследовательские ключи `page_anatomy`, `ia_probe`,
  `claims_check inventory`, `copy_lint --metrics-only` (OE2-18), цены самопроверок формулой (OE3-03), эталон и штрих
  иконок параметром (OE3-05), оставшиеся утилиты обслуживания и лаборатории (OE3-17: `asset_inventory`, `channel_diff`,
  стенд `stand_run`, `polza_catalog diff`, `split_recraft`, blender `run_recipes`, `run_doc_blocks`, `fx_probe`,
  `anim_diff`, `sheet`), коды замеров ворот (OE3-19), фикстуры своими файлами (OE4-17), npm по группам, scipy и Python
  3.11 (OE4-16), `check_links` и три проверки ссылок (OE4-18), `kit.json` вне git (OE4-08), имя расширения DTCG
  (OE4-22), два профиля голоса (OE5-18), проекции `app-brief` (OE5-19), служебные файлы в диффах (OE5-23);
- `оставить`: порядок колонок `texts.md` (OE1-18), знание о моделях в коде до Ф10 (OE3-20).
