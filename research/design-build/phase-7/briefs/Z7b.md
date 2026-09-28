# Z7b — соседние исполнители и аудиты: экраны, FSD, мобильное, бот, сервисы и домены

Сначала прочитай общий бриф `research/design-build/phase-7/briefs/COMMON.md`, план `phase-7/PLAN.md` (§1–§5) и цепочку
`phase-7/CHAIN.md` целиком — там передачи зон 1–7a, 10: что записано в формах экранов (зона 2), в стыках FSD, мобильного
и бота (зона 3) и в этапах скилла дизайна (5a). Параллельно с тобой работает Z8 (`entrypoint`,
`entrypoint-for-business`, `cross-audit`, `service-audit/references/rules.md`) — её файлы не трогай.

## Зона
Двадцать три правки в скиллах, которые ведут и проверяют экраны, FSD-карту, мобильное приложение и бота, плюс проход по
следам прежнего запрета в скиллах сервисов и доменов. Формы уже приняли: нотацию дерева экранов с `ui:` из закрытого
словаря, ключи и наборы состояний по словарю S01–S24, карту экранов и реестр маршрутов, реестр текстов интерфейса с
ролями, контракты блоков, доступность и узкий экран (зона 2); стыки FSD, мобильного и бота (зона 3). Исполнители и
аудиты должны вести и проверять именно эти формы.

| скилл (`.claude/skills/…`) | файлы | что |
|---|---|---|
| `screen-deep-dive` | `SKILL.md`, `references/tree-notation.md`, `field-checklists.md`, `draft-stable.md`, `raw-input.md`, `workflow-patterns.md`, `project-context.md`, `assets-policy.md` | грамматика дерева — T3 §4.3 (совпадает с разделом «Нотация» README screens); `ui:` — тип словаря `kb/common/components.yaml` или расширение проекта; ключи и наборы состояний; `map.md` — свод, не авторится; `texts.md` — реестр текстов и роли; контракты блоков (форма, коллекция, плитка); доступность и узкий экран; «Сводка состояния» — порядок этапов SaaS (ST-17); шаг «Привести к канону» (F13); проход |
| `screen-audit` | `SKILL.md`, `references/rules.md` | правила по T3 §4.4 (нотация и `ui:`, ключи и наборы состояний вместо R-SEM-011, `source: own`, RT, CP, AX, MB, тексты — ключ в реестре, роль); проход |
| `fsd-deep-dive` | `SKILL.md`, `references/workflow-patterns.md`, `references/draft-stable.md` (строка о потребителе карты) | `path` = `route`, `guard` = `access`, колонка `ui-type`, ключи i18n = ключи `texts.md`, сценарии `shared-api` по наборам состояний; «не для рода `landing`, `site`» (B8); тема — из токенов ДС; проход |
| `fsd-audit` | `SKILL.md` | правила по T3 §4.4 (`path` = `route`, `guard` = `access`, `ui-type` из словаря, сценарии `shared-api` покрывают наборы) |
| `mobile-deep-dive` | `references/field-checklists.md`; проход — `SKILL.md`, `references/interface-context.md` | стыки зоны 3: `states` ↔ S-id, `empty` у экрана с коллекцией, тексты с ролями, токены ДС в `shell`, паритет и урезание |
| `mobile-audit` | `references/rules.md` | ключи `states` — по таблице соответствия S-id; `empty` у экрана с коллекцией (ST-05) |
| `telegram-bot-flow-deep-dive` | `references/field-checklists.md` | `getter.<ключ>.empty` рядом с `fallback`; `escalate`; путь к человеку; роли текстов (TX-43) |
| `telegram-bot-flow-audit` | `references/rules.md` | R-DATA-002: `empty` и `fallback` раздельно (ST-24); путь к человеку: свободный ввод или ИИ без пути — warning, кнопочный бот — hint (ST-19) |
| `service-deep-dive`, `domain-deep-dive` | `service-deep-dive/references/draft-stable.md`, `domain-deep-dive/SKILL.md`, `domain-deep-dive/references/draft-stable.md` | проход: «Committed-скрипта-валидатора … нет» → «у слоя сервисов и доменов скрипта-валидатора нет, проверка ручная» |

Описания `SKILL.md`, которые правишь (`screen-deep-dive`, `screen-audit`, `fsd-deep-dive`, `fsd-audit`,
`mobile-deep-dive`, `domain-deep-dive`), — ≤ 600 знаков (H2): главный случай первой фразой, категории намерений, без
перечня фраз-триггеров (SKILL-MAP §7).

## Решения зоны
A4 (порядок этапов SaaS в «Сводке состояния» — ST-17), A6 (стыки мобильного и бота), B8, D5, F6, F7, F10, F13, F14, F15,
H2 (описания), H7 (проход по следам прежнего запрета в файлах зоны — PLAN §4, строка Z7b).

Действия — 15 строк `phase-7/ZONES.tsv` с `7b` в `zones`: ST-16, ST-17, ST-19, TX-45 (Ф6); GL-09, CM-01, CM-05, CM-07,
CM-10, CM-12, ST-05, ST-16, ST-19, ST-24, TX-45 (Ф4). Текст действия Ф4 — `phase-4/actions.tsv`, место —
`spec/T3-saas-layer.md` §2.1. У строки с несколькими зонами ты делаешь часть в скиллах.

## Id и имена — один источник
- Нотация, ключи, поля и разделы — как их записали зоны 2 и 3 (README и формы `docs/projects/_template/screens/`, `fsd/`,
  `mobile/`, `telegram-bot-flow/`; отчёты `phase-7/reports/Z2.md`, `Z3.md` §4). Грамматика в `tree-notation.md` и раздел
  «Нотация» README screens — одно и то же: расхождение — ошибка, бери README, опиши в отчёте.
- Ключи mobile и бота не переименовываются — только добавления (handoff-контракт, `CLAUDE.md` §8).
- Id новых правил аудитов — по T3 §4.4 в системе id каждого аудита (`R-<категория>-NNN`), без коллизий.
- Этапы слоя проекта SaaS — `design-deep-dive/references/phases.md` (зона 5a).

## Что читать
Журнал (`research/design-build/`):
- `phase-6/BLUEPRINT.md` — маршруты «SaaS и кабинет», «Мобильное и бот», группа F, A4, A6, B8, D5;
- `phase-6/spec/T3-saas-layer.md` — §1: A4, A6, D5, F6, F7, F10, F13, F14, F15; §2.1; §3; §4.3 (грамматика дерева);
  §4.4 (правила `/screen-audit`, `/fsd-audit`, `/mobile-audit`, `/telegram-bot-flow-audit`); §4.6;
- `phase-6/spec/T4-skills.md` — вступление («Следы прежнего запрета»), §1 H2, H7 (проход);
- `phase-4/nodes/05-ST.md` — §1.1, §1.2, §1.4 (словарь, сопоставление, наборы и приоритет);
- `phase-6/ACTIONS-SPEC.tsv`, `phase-4/actions.tsv` — строки действий зоны;
- `DECISIONS.md` — Р29, Р79, Р121, Р124, Р125, Р127, Р150, Р158, Р163 и строки «Ф7, зона … принята».

Шаблон: все файлы зоны — целиком до правки; README и формы
`docs/projects/_template/screens/`, `fsd/`, `mobile/`, `telegram-bot-flow/` (зоны 2, 3); `CLAUDE.md` §2, §3, §8.

База: `kb/common/components.yaml` (шапка, группы), `glossary.md` (статьи «Компонент», «Состояние», «Поток»).

## Как писать
- Исполнитель спрашивает — владелец отвечает (`CLAUDE.md` §3); тексты интерфейса — черновик «допущением», утверждает
  владелец продукта.
- Проход: «craft» → «облик»; фраза «wireframe и hi-fi автор макета собирает вручную» уходит, где нужна связь — «макет
  собирает слой дизайна `design/`»; запрет облика в screens, FSD, mobile остаётся по смыслу.
- Правило аудита — что проверяет, серьёзность, откуда норма; проверка — чтением по форме; утилита — только если она
  описана в `design-deep-dive/scripts/README.md`.

## Проверка
Общий бриф; длины `description` правленых `SKILL.md` ≤ 600 знаков (счёт `python3`); в файлах зоны нет «craft», фразы о
ручной сборке wireframe и hi-fi и «Committed-скрипта»; грамматика `tree-notation.md` совпадает с README screens; id
новых правил не совпадают с существующими.

## Уроки принятых зон (CHAIN 01–04)
- FSD-карту читает только `<org>/frontend` (B8): строки «`<org>/frontend` или `<org>/site`» в `fsd-audit/SKILL.md`,
  `fsd-deep-dive/SKILL.md` и `references/draft-stable.md` — поправить.
- Места правил и чек-листов fsd, mobile, бота — отчёт `phase-7/reports/Z3.md` §4 (R-DATA-002 — `empty` и `fallback`
  раздельно, пример нормы R-DATA-002 описывает `empty`; путь к человеку — README бота § Путь к человеку; строка
  «Отложенные правки» — `mobile/_template/shell.md § Offline`).
- Серьёзность правила «экран mobile с коллекцией без `empty`» — реши сам по шкале `mobile-audit` (у веба непокрытое
  обязательное состояние — warning, у `stable` — error) и опиши в отчёте.
- Нотация, словарь состояний, реестр текстов, контракты блоков — `screens/README.md` и формы зоны 2 (отчёт Z2 §4);
  планшетная ширина — ключ `sm` (правило MB-08).
- Правка текста интерфейса с холста кабинета приходит от `design-deep-dive` блокером и предложением соседа: этап
  `ui-texts` `screen-deep-dive` принимает её как вход с середины (строка `texts.md` → `assumed`, проверки, `approved`
  словом заказчика) — `claude-design.md § Правки заказчика`.
- `refcheck.py` находит файлы корня репозитория: `CLAUDE.md` пиши в обратных кавычках.

## Отчёт
`research/design-build/phase-7/reports/Z7b.md`.
