# Ф7 — план реализации

Ф7 пишет в шаблон то, что утверждено в Ф6 (страница `../phase-6/BLUEPRINT.md`, Р163): каноны и формы новых слоёв,
UX-дельту слоя проекта для SaaS, стыки FSD, мобильного и бота, правила и карты, тексты скилла, `design-audit` и агентов,
правки соседних скиллов и оркестраторов, описания всех скиллов и пакет закрытий базы. Код утилит — Ф8, пилоты — Ф9,
уборка и выравнивание баз — Ф10.

Входы: спецификация `../phase-6/spec/` (T1 — слой страницы, T2a — слой дизайна, T2b — холст и приёмка, T3 — слой
проекта SaaS, T4 — скиллы и пакет для кода), сводный список и порядок — `spec/T4-skills.md` §4.3–§4.4, ответы и места
действий сверки — `../phase-6/ACTIONS-SPEC.tsv`, действия по зонам — `ZONES.tsv` этой папки. Решения — `../DECISIONS.md`
Р163 (утверждение), Р164 (способ), Р165 (этот план).

Объём: ≈ 144 файла — 25 новых, 119 правок; ≈ 6,0–8,0 тыс. строк.

## 1. Способ (Р164)

- **До финала.** Оркестратор ведёт Ф7 без остановок: «да» перед агентом не ждёт, после каждого шага пишет в чат
  короткий итог (что сделано, находки, следующий шаг). Остановка и вопрос заказчику — только если шаг задевает его
  решения (источник «заказчик» в DECISIONS) или утверждённую страницу; структурные решения оркестратор принимает сам,
  записывает строкой DECISIONS и показывает в итоге.
- **Парами.** Одновременно — не больше двух агентов, и только в зонах с непересекающимися файлами (`CLAUDE.md` §6: один
  агент — одна зона). Следующая пара стартует после приёмки предыдущей.
- **Агенты** — Claude Opus 5.5 (`model: opus`), по брифу `briefs/COMMON.md` + бриф зоны. Бриф зоны оркестратор пишет
  перед её парой: по разделу зоны ниже, с уроками уже принятых зон (`CHAIN.md`). Брифы Z1 и Z2 готовы.
- **Сессии (Р166).** Сессия 1 — облачная, шаги 1–4 (восемь агентов: Z1, Z2, Z3, Z4, Z5a, Z5b, Z5c, Z10); сессия 2 — шаги
  5–8 (шесть агентов: Z6, Z7a, Z7b, Z8, Z9, RT) и закрытие Ф7. Push — перед запуском пары, сразу после каждого агента
  (коммит «на приёмке») и после приёмки каждой зоны. Лимит может оборвать сессию посреди шага: незапушенный хвост
  теряется, следующая сессия продолжает с первого непринятого шага по файлам ветки (Р119). Штатный конец сессии —
  STATE и `NEXT-SESSION-PROMPT.md` под следующую. Лимита контекста у сессии нет (Р131).

## 2. Зоны

`_template/` = `docs/projects/_template/`; скиллы — `.claude/skills/<скилл>/`; «проход» — правка одной-двух строк по
следам прежнего запрета (§4). Действия зоны — строки `ZONES.tsv` с её номером в колонке `zones` (Ф6 — действия сверки,
Ф4 — действия Ф4 с фазой Ф7).

### Z1 — каноны новых слоёв (8 новых; ≈ 885–1 075 строк; T1, T2a, T2b, T4)
- `_template/site/README.md` — канон слоя страницы; `_template/design/README.md` — канон слоя дизайна с разделами
  «Холст» (T2b §4.5) и «Пакет для кода» (T4 §6).
- Формы `_template/design/_template/`: `app-brief.yaml`, `system.yaml`, `brand.yaml`, `ARTIFACTS.md` (с «Условиями
  холста», строкой просьбы и столбцом «чей аккаунт»), `REVIEW.md`, `ready.yaml`.
- Решения: A2, A3, A5, A7, A9 (сторона слоя), B1–B10, C1–C8, D1–D6, E1–E4, E8–E10 (сторона форм), G1–G6.
- Действия: 30. Бриф — `briefs/Z1.md`.

### Z2 — каноны слоя проекта (5 новых, 19 правок; ≈ 870–1 270 строк; T3, T1, T2a, T4)
- Новые: `_template/project/object.md`, `action.md`; `_template/interface/_template/scenario.md`;
  `_template/screens/_template/map.md`, `texts.md`.
- Правки: `_template/project/` — `README.md`, `vision.md`, `surface.md`, `user.md`, `capability.md`, `boundary.md`;
  `_template/interface/` — `README.md`, `_template/situation.md`, `zone.md`, `data-items.md`, проход — `block.md`,
  `ux-substrate.md`; `_template/screens/` — `README.md`, `_template/screen.md`, `block.md`, `shell.md`, `flow.md`;
  `_template/services/` — `README.md` (проход «Committed»), `architecture.md` (A9: «своего сервиса нет»).
- Порядок внутри зоны: `project/` → `interface/` → `screens/` → `services/`.
- Решения: A1, A9 (форма архитектора), B2, B8 (строки README), D3, D5, F1–F15, H7 (проход).
- Действия: 44. Бриф — `briefs/Z2.md`.

### Z3 — стыки FSD, мобильного и бота (16 правок; ≈ 115–200 строк; T3)
- `_template/fsd/` — `README.md`, `_template/pages.md`, `shared-ui.md`, `shared-api.md`, `shared-lib.md`, проход —
  `features.md`; `_template/mobile/` — `README.md`, `_template/shell.md`, `shared-api.md`, проход — `features.md`,
  `widgets.md`; `_template/telegram-bot-flow/` — `README.md`, `_template/command.md`, `notification.md`,
  `features/window.md`, `features/use-case.md`.
- Решения: A6, B8 (README fsd), D5 (роли текстов), F7, F10, H7 (проход). Ключи mobile не переименовываются; у бота —
  добавочные `empty`, `escalate`.
- Входы: T3 §1 (A6, F7, F10), §2.1, §4.1–§4.2 (FSD, mobile, бот), §6; T1 §4.4 (README fsd); T4 «Проверено» (следы).
- Действия: 21.

### Z4 — правила и карты (1 новый, 9 правок; ≈ 160–210 строк; T4 с T1, T2a, T3)
- `CLAUDE.md`, корневой `README.md`, `CONTRIBUTING.md`, `docs/README.md`, `docs/projects/README.md`,
  `docs/getting-started.md`, `.claude/rules/forward-only.md` (абзац «Машинные файлы слоёв»), `.claude/settings.json`
  (`skillListingBudgetFraction: 0.02`), `.gitignore`; новый `.gitattributes` (G3).
- Тексты правок — T4 §1 H7 (по пунктам), B6 и C3 (строки §3), H2, G3, H12; строки для `CLAUDE.md` из §6 T1, T2a, T2b, T3.
- Ключ `skillListingBudgetFraction` агент сверяет с документацией Claude Code (settings reference); не подтвердился —
  строку не пишет и сообщает в отчёте.
- Действия: 5. `CLAUDE.md` — конституция шаблона: правки ровно по H7, любое отступление — вопрос заказчику (Р164).

### Z5 — тексты скилла (6 новых, 2 правки; ≈ 1 680–2 040 строк; T4, T1, T2a, T2b, T3)
- **5a:** `references/phases.md` (≈ 600 строк, один файл — Р118: таблица маршрутов T4 §3.1, контракты этапов из §3 пяти
  спецификаций, порядок ассетов и ДС, кто строит ДС, порядок проверок, вход с середины), `references/field-checklists.md`.
  Образец формы — `project-deep-dive/references/phases.md`. Действия: 36.
- **5b:** `references/claude-design.md` (протокол, 16 разделов — оглавление T2b §4.3, подраздел «Правки токенов» — T2a C4,
  таблица вызовов судьи — H4), `workflow-patterns.md`, `draft-stable.md`, `knowledge-base.md` (текст нынешнего
  навигатора `SKILL.md` — Р148, H2). Действия: 24.
- **5c** (после 5a и 5b): `design-deep-dive/SKILL.md` — исполнитель (frontmatter T4 §4.2, ≤ 600 знаков; точки входа и
  сводка этапов — T4 §4.2; `disable-model-invocation` снят), `scripts/README.md` — раздел `project` (утилиты по артефактам
  проекта, H10).
- Имена этапов (`brief`, `page-plan`, `mockup` …) — по T4 §3.1; `SKILL.md`, `_phase-jump.md` и `state-model.md` (Z8)
  берут их оттуда.

### Z6 — `design-audit` и агенты (4 новых; ≈ 680–880 строк; T4, правила — T1, T2a, T2b)
- `design-audit/SKILL.md`, `design-audit/references/rules.md` (категории `R-SURF` … `R-VIS`; правила — T1 §4.3, T2a §4.4,
  T2b §4.4), `.claude/agents/design-judge.md`, `.claude/agents/design-consultant.md` (frontmatter — T4 §4.2).
- Решения: H3, H4, E5. Действия: 4.

### Z7 — соседние исполнители и аудиты (36 правок; ≈ 870–1 360 строк; T3, T4)
- **7a** (14): `project-deep-dive` — `SKILL.md`, `references/phases.md` (девять фаз, новая `objects` — F12),
  `field-checklists.md`, `draft-stable.md`, `workflow-patterns.md` («Привести к канону» — F13); `project-audit` —
  `SKILL.md`, `references/rules.md`; `interface-deep-dive` — `SKILL.md`, `references/field-checklists.md`,
  `draft-stable.md`, `workflow-patterns.md`, `project-context.md`; `interface-audit` — `SKILL.md`, `references/rules.md`.
- **7b** (22): `screen-deep-dive` — `SKILL.md`, `references/tree-notation.md` (грамматика — T3 §4.3), `field-checklists.md`,
  `draft-stable.md`, `raw-input.md`, `workflow-patterns.md`, `project-context.md`, `assets-policy.md`; `screen-audit` —
  `SKILL.md`, `references/rules.md`; `fsd-deep-dive` — `SKILL.md`, `references/workflow-patterns.md`; `fsd-audit` —
  `SKILL.md`; `mobile-deep-dive` — `references/field-checklists.md`, проход — `SKILL.md`,
  `references/interface-context.md`; `mobile-audit` — `references/rules.md`; `telegram-bot-flow-deep-dive` —
  `references/field-checklists.md`; `telegram-bot-flow-audit` — `references/rules.md`; проход «Committed» —
  `service-deep-dive/references/draft-stable.md`, `domain-deep-dive/SKILL.md`,
  `domain-deep-dive/references/draft-stable.md`.
- Входы: T3 §4.6 (что правится у каждого скилла), §1, §3, §4.3–§4.4 (грамматика, правила аудитов), §2.1; T4 H7 и
  «Проверено» (следы). Описания своих `SKILL.md` — ≤ 600 знаков (H2). Действия: 7a — 1, 7b — 15.

### Z8 — оркестраторы и `/cross-audit` (1 новый, 16 правок; ≈ 570–760 строк; T4)
- `entrypoint/SKILL.md`, `references/routing.md`, `state-model.md`, `intake.md`; `entrypoint-for-business/SKILL.md`,
  `references/routing-business.md`, `product.md`, `business-language.md`, `intake-business.md`, `escalation.md`,
  `state-format-business.md`, `anti-patterns-real.md`, новая `references/site-and-look.md`; `cross-audit/SKILL.md`,
  `references/angles.md` (углы `surface-design`, `facts-business`, `promise-product`), `output-formats.md`;
  `service-audit/references/rules.md` (A9).
- Решения: A7, A8, A9 (сторона аудитов), H5, H6, H8; сигналы и ветки state — §6 T1, T2a, T2b, T3. Описания своих
  `SKILL.md` — ≤ 600 знаков.

### Z9 — описания скиллов (16 правок; ≈ 65–110 строк; T4)
- Описания 16 `SKILL.md`, которых нет в других зонах: `ajtbd-audit`, `business-deep-dive`, `hypothesis-map-audit`,
  `hypothesis-map-deep-dive`, `infrastructure-audit`, `infrastructure-deep-dive`, `job-graph-deep-dive`, `jtbd-interview`,
  `segment-deep-dive`, `swot-audit`, `swot-deep-dive`, `service-audit`, `service-deep-dive`, `mobile-audit`,
  `telegram-bot-flow-audit`, `telegram-bot-flow-deep-dive`.
- Замер всех 31 описания: каждое ≤ 600 знаков, сумма ≤ 18 тыс. Если листинг всё равно теряет описания — свернуть редкие
  скиллы до имени (`skillOverrides`), решение и строка `.claude/settings.json` — оркестратор (Р165).
- Правило описания — SKILL-MAP §7: главный случай первой фразой, категории намерений, без перечня фраз-триггеров.

### Z10 — база: пакет закрытий H11 (5 правок в `kb/`; ≈ 70–110 строк; T4, T2a, T2b)
- Процедура — T4 §1 H11: строки узлов `../phase-4/nodes/*.tsv` → `../phase-4/tools/registry.py merge` и `canon` →
  записи `kb/common/CONTRADICTIONS.md` → `refcheck.py --strict`, `mapcheck.py` → строка DECISIONS с перечнем id.
- Закрываются формой или этапом: GT-03, TR-22, TR-44, GT-42, NU-37, CM-06, CM-10, CM-12, CM-15, ST-15, ST-16, ST-19,
  ST-20, ST-23 (часть `<org>/mobile` — позицией), ST-25, NU-02, NU-03, NU-17, GL-07 и запись «Компонент»; GT-13 — из
  «Открытого» в позицию; новая норма VI-60 (D1, T2a); строка cd 06/06 §8 в `kb/common/judge.md §7` (E5).
- Файлы: `kb/common/CONTRADICTIONS.md`, `canon.tsv` (пересборка скриптом), `judge.md`, `README.md` («Как пользоваться
  `canon.tsv`», «правки базы — в шаблоне», H12), `kb/INDEX.md` §4–§5 (адреса протокола и этапов).
- Реестр и `canon.tsv` меняются только по закрытым id — сверка диффом. Действия: 6.

## 3. Порядок

| шаг | пара | почему так |
|---|---|---|
| 1 | Z1 ∥ Z2 | каноны — слова и поля, на которые ссылается всё остальное |
| 2 | Z3 ∥ Z4 | стыки ссылаются на экраны и тексты Z2; роутер и карты — на README Z1–Z2 |
| 3 | Z5a ∥ Z5b | этапы и протокол — на формах Z1–Z2; друг на друга ссылаются по id из T4 §3.1 и T2b §4.3 |
| 4 | Z5c ∥ Z10 | `SKILL.md` — по готовым `references/`; закрытия называют места этапов и протокола |
| 5 | Z6 ∥ Z7a | правила аудита — на формах и этапах; соседние скиллы — на формах Z2 |
| 6 | Z7b ∥ Z8 | оркестраторы — на этапах, аудите и формах; 7b — на Z2–Z3 |
| 7 | Z9 | последний проход по описаниям, когда все `SKILL.md` правлены |
| 8 | проверка | §6 |

Файлы пар не пересекаются (списки §2). Остановка на шаге — только по §1.

## 4. Проход по следам прежнего запрета

Облик теперь легален в слое дизайна (Р76 п. 1, H7): фразы «wireframe и hi-fi автор макета собирает вручную» уходят (где
нужна связь — «макет собирает слой дизайна `design/`»), слово «craft» заменяет «облик» (GL-17), запрет облика в слоях
interface, screens, FSD, mobile остаётся по смыслу; «Committed-скрипта-валидатора … нет» — «у слоя сервисов и доменов
скрипта-валидатора нет, проверка ручная». Файлы (поиск 28.09, `kb/` не в счёт; «Recraft» — имя модели, не след):

| зона | файлы |
|---|---|
| Z2 | `_template/interface/README.md`, `_template/interface/_template/{block,situation,ux-substrate,zone}.md`, `_template/screens/README.md` (фраза ×3), `_template/screens/_template/{block,screen}.md`, `_template/services/README.md` («Committed») |
| Z3 | `_template/fsd/README.md`, `_template/fsd/_template/{features,shared-ui}.md`, `_template/mobile/_template/{features,widgets}.md` |
| Z4 | `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `docs/README.md`, `docs/getting-started.md` |
| Z7a | `interface-deep-dive/SKILL.md`, `interface-audit/references/rules.md` |
| Z7b | `screen-deep-dive/SKILL.md`, `screen-deep-dive/references/{tree-notation,assets-policy}.md`, `screen-audit/references/rules.md`, `fsd-deep-dive/SKILL.md`, `mobile-deep-dive/SKILL.md`, `mobile-deep-dive/references/interface-context.md`, `service-deep-dive/references/draft-stable.md`, `domain-deep-dive/SKILL.md`, `domain-deep-dive/references/draft-stable.md` |

## 5. Приёмка шага (оркестратор)

0. Агент закончил — его файлы и отчёт как есть одним коммитом и push, до приёмки (Р166): работа не пропадёт, если сессия
   оборвётся на приёмке. Сообщение — по содержанию и с пометкой «на приёмке», без имён фаз сборки (`CLAUDE.md` §1):
   например, `docs(template): каноны слоёв страницы и дизайна, на приёмке`.
1. Файлы зоны — все на месте, других агент не трогал (`git status`, дифф по путям).
2. Действия зоны (`ZONES.tsv`) и решения зоны — у каждого есть реализация в названном месте (чтение раздела, поиск).
3. `python3 research/design-build/tools/refcheck.py --strict <новые и правленые md>` — 0 битых ссылок, 0 следов журнала
   (Р-номера, имена фаз сборки, пути в журнал, даты, «теперь», «было»).
4. Выборочное чтение: forward-only, стандарт текстов SKILL-MAP §7, экспертиза (`CLAUDE.md` §3: формы дают структуру и
   вопросы, а не формулировки за владельца), в `_template/` нет данных проекта; YAML и JSON парсятся.
5. Отчёт агента `reports/<зона>.md`; запись в `CHAIN.md` (время — из уведомления о завершении).
6. Строка DECISIONS «Ф7, зона N принята»; коммиты — правки приёмки в файлах шаблона (`docs(template)`,
   `feat(design-deep-dive)`, `feat(design-audit)`, `refactor(skills)`, `chore(harness)` — по содержанию, описание
   forward-only) и журнал (`docs(research)`); push в GitHub (в облаке — в ветку сессии).
7. Короткий итог в чат.

Правки по замечаниям приёмки делает тот же агент (продолжение) или оркестратор, если правка мелкая.

## 6. Проверка Ф7 (шаг 8)

- **Статическая:** `refcheck.py --strict` по всем новым и правленым текстам скилла, `kb/common/` и `_template/`;
  `mapcheck.py` по `kb/INDEX.md` — без новых «не на норму»; поиск следов §4 — 0; дифф `registry.tsv` и `canon.tsv` — только
  закрытые id; описания — каждое ≤ 600 знаков, сумма ≤ 18 тыс.; YAML и JSON форм и настроек парсятся.
- **Маршруты (Р164):** свежий агент без контекста, только чтение, проходит шесть запросов от `entrypoint` до этапа,
  исполнителя и файлов: лендинг, многостраничник, кабинет SaaS, вход с середины (готовые брендбук и тексты), клиентский
  режим (`/entrypoint-for-business`, «сайт выглядит несолидно»), стык мобильного («а мобильное приложение нарисуете?»).
  Ключ ответов оркестратор пишет до запуска по `phases.md` §1 и `entrypoint/references/routing.md` — `check/KEY.md`;
  бриф — `check/BRIEF-RT.md`, ответы — `check/routes.md`, оценка — оркестратор по ключу. Готово — 6 из 6; ошибка —
  правка в файлах зоны и повтор по упавшим запросам.
- Узкие аудиты на шаблоне без данных проекта не прогоняются — их первая проверка — пилоты Ф9.

## 7. Готово, когда

- все зоны приняты (строки DECISIONS, коммиты и push);
- статическая проверка чистая;
- маршруты — 6 из 6;
- STATE, PLAN сборки и `NEXT-SESSION-PROMPT.md` — под Ф8.

## 8. Риски

- **Два агента задели один файл** → списки зон §2 не пересекаются; приёмка сверяет дифф по путям.
- **Данные проекта в `_template/` или канон в папке проекта** → правило брифа и пункт 4 приёмки.
- **Следы журнала в текстах шаблона** → `refcheck --strict` на каждом шаге; журнал уходит в Ф10, ссылка на него станет
  битой.
- **Разнобой имён этапов** между `phases.md`, `SKILL.md`, `_phase-jump.md` и `state-model.md` → один источник — T4 §3.1;
  приёмка Z5c и Z8 сверяет id.
- **Ключ настроек листинга не тот** → Z4 сверяет с документацией Claude Code; сумма описаний меряется в Z9.
- **Агент прерван** (закрыли Claude Code, уснула машина, в облаке — погасла среда) → работу доводит новый агент по файлам
  на диске (Р119); в облаке — страховочные проверки каждые 30 минут и коммит «черновик, агент в работе».
- **Большие спецификации** (90–190 КБ) → бриф называет разделы, агент читает адресно.

## 9. После Ф7

Ф8 — код по `spec/` (сборщик и проверка входа холста, генератор приёмки, перевод холста в HTML, покрытие компонентов ДС,
манифест `ready.yaml`, сборка ДС и обратная синхронизация токенов, утилиты экранов, нормализаторы для перевода форков, блок
тем в схеме брифа, чистка журнала правок текстов, перенос проверок обслуживания в `scripts/maint/` — Р165). Затем
пилоты Ф9: лендинг, многостраничник, SaaS; план ассетов в пилотах утверждает заказчик (Р163).
