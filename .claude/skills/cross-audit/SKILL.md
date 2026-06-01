---
name: cross-audit
description: Сквозной семантический аудит консистентности между слоями документации проекта — project ↔ interface ↔ domain ↔ screen. Запускает рой агентов параллельно, каждый под своим углом (persona ↔ who, capability ↔ situation/domain, surface ↔ zone/screen, integration ↔ domain, constraint ↔ surface/integration, market ↔ capability), читает оба слоя + state, ищет семантические тупики и противоречия — НЕ через slug-валидацию, а через смысловую проверку («персона без UX-покрытия», «capability без бизнес-кода», «зона висит без поверхности»). Не правит, только отчёт. Использовать перед релизом, после крупного апдейта project- или interface-слоя, или когда `/project-deep-dive` / `/interface-deep-dive` предлагают прогон. Сводный отчёт + список findings; deep-dive по каждому — отдельный шаг руками аналитика.
---

# cross-audit

Сквозной семантический аудит **между слоями** документации:

- `docs/project/` (продукт — vision/persona/capability/...)
- `docs/interface/` (UX — who/stage/situation/zone/block/...)
- `docs/domains/` (бизнес-домены бэкенда — если каталог существует)
- `docs/screens/` (композиция экранов — если каталог существует)

Аудит **не валидирует slug** между слоями (связи семантические, см.
`docs/project/README.md`). Аудит читает оба слоя и спрашивает агентов
«в чём смысл сочетается, а в чём расходится» — это требует LLM, не grep.

`/project-audit` ловит внутренние тупики **внутри project-слоя**.
`/interface-audit` — внутри interface. Cross-audit — между.

## Точки входа

| вызов | поведение |
|---|---|
| `/cross-audit` | полный прогон всех применимых углов (5-8 в зависимости от наличия domain/screen) |
| `/cross-audit <lens>` | прогон одного угла |
| `/cross-audit --quick` | быстрый прогон с 3 самыми важными углами (persona↔who, capability↔situation, surface↔zone) |

`lens` ∈ {`persona-who`, `capability-situation`, `capability-domain`,
`surface-zone`, `surface-screen`, `integration-domain`,
`constraint-surface`, `market-capability`}.

См. `references/angles.md`.

## Что делать при запуске

1. Прочитать `docs/project/README.md`, `docs/interface/README.md`, и
   (если есть) `docs/domains/README.md` / `docs/screens/README.md` —
   освежить каноны.
2. Прочитать `references/angles.md` — список углов и контекста на
   каждый.
3. **Проверить наличие слоёв.** `docs/domains/` и `docs/screens/` могут
   отсутствовать (например, продукт без backend, или ещё не дошли).
   Углы, требующие отсутствующего слоя, пропускаются с пометкой в
   отчёте.
4. Определить, какие углы применимы — по args или по полному
   прогону.
5. **Спавнить агентов параллельно** (см. ниже).
6. Собрать ответы. Каждый агент возвращает findings в едином формате.
7. Сгруппировать findings по углам, отсортировать по severity.
8. Через `AskUserQuestion` пройти по top-K findings — что делать с
   каждым: «принять как корректное», «нужна правка», «false positive».
9. Перезаписать `audit-state/last-report.md` с reasoning-trace и
   решениями аналитика.

## Рой агентов

Каждый агент получает:

- путь к двум каталогам слоёв (`docs/<src>/`, `docs/<dst>/`);
- свой lens (один из 8);
- промпт-инструкцию из `references/angles.md` для этого lens;
- стандартный schema для findings (`references/findings-format.md`).

Спавн — через `Agent` tool, **subagent_type: general-purpose**, чтобы
агент мог:

- `Read` файлы слоёв;
- `Grep` для быстрых проверок упоминаний;
- (опционально) `WebSearch` — если lens требует внешнего контекста
  (например, проверить, что constraint типа `regulation` действительно
  применима к описанной нише).

Все агенты спавнятся в **одном** message-блоке для параллельности.

### Промпт-каркас для агента

```
Lens: <name>
Source layer: <path-1>
Destination layer: <path-2>

Цель: семантически сопоставить записи в source и destination — найти
тупики, противоречия, потери покрытия. Не slug-валидация: связь
семантическая, агент сам решает, соответствует ли запись X записи Y.

Прочитай:
- <конкретные файлы из source-layer>
- <конкретные файлы из destination-layer>
- state каждого скилла, обслуживающего эти слои (если файлы есть).

Найди:
- <конкретные паттерны для этого lens из angles.md>

Верни ТОЛЬКО валидный JSON по схеме findings-format.md, без пояснений
и preamble. Каждый finding:
{
  "lens": "<lens>",
  "severity": "error" | "warning" | "hint",
  "title": "одна строка-заголовок",
  "evidence": "конкретные slug/файлы/места, где видно",
  "suggestion": "что аналитику дальше делать"
}

Если ничего не нашёл — пустой массив [].
Не выдумывай findings ради чисел.
```

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Семантический тупик, ломает целостность | persona без покрытия в interface.who; surface без зон; integration без бизнес-домена |
| `warning` | Подозрительная несостыковка | capability упомянута, но в interface ситуаций под неё «впритык»; market покрывает capability, которой у нас нет; constraint не привязан ни к surface, ни к integration |
| `hint` | Гипотеза / возможная новая capability | market показывает gap, у нас нет capability на эту территорию; в interface есть ситуация, которая не имеет capability-якоря в project |

## Углы проверки (lenses)

Полный список — `references/angles.md`. Краткая карта:

| lens | source | destination | основной вопрос |
|---|---|---|---|
| `persona-who` | `docs/project/persona.md` | `docs/interface/who.md` | каждая persona имеет хотя бы одно who-покрытие? каждое who сводимо к одной persona? |
| `capability-situation` | `docs/project/capability.md` | `docs/interface/situation.md` | каждая capability реализуется ≥1 ситуацией? есть ли ситуации без capability-якоря? |
| `capability-domain` | `docs/project/capability.md` | `docs/domains/` (если есть) | у каждой capability есть бизнес-код в domain? |
| `surface-zone` | `docs/project/surface.md` | `docs/interface/zone.md` | каждая surface имеет ≥1 зону? каждая зона принадлежит surface? |
| `surface-screen` | `docs/project/surface.md` | `docs/screens/` (если есть) | каждая surface имеет ≥1 screen-композицию? |
| `integration-domain` | `docs/project/integration.md` | `docs/domains/` (если есть) | каждая integration имеет адаптер в domain? |
| `constraint-surface` | `docs/project/constraint.md` | `docs/project/surface.md`, `docs/project/integration.md` | каждый constraint привязан семантически к surface или integration? |
| `market-capability` | `docs/project/market.md` | `docs/project/capability.md` | конкуренты покрывают наши capabilities? есть ли gap, где конкурент умеет, а мы нет (signal к новой capability)? |

## Формат отчёта

```
=== /cross-audit ===
Слои: project, interface, domain, screen
Углы: 8 запущено, 8 ответили
Время: <duration> · агентов: 8

[error] persona-who → persona:doctor не имеет соответствия в
  docs/interface/who.md (нет роли, выполняющей действия персонажа).
  Доказательство: persona:doctor.context = «врач инициирующей клиники»;
    в who.md нет ни одной записи с инициирующей ролью.
  Что делать: либо завести who:doctor через /interface-deep-dive who,
  либо пересмотреть persona в /project-deep-dive persona:doctor.

[error] surface-zone → surface:web-partner не имеет ни одной зоны в
  docs/interface/zone.md (zone.md упоминает только админ-зоны).
  Доказательство: surface:web-partner.type=web; zone.md → [`admin-overview`,
    `study-card`] — все принадлежат admin-поверхности по описаниям.
  Что делать: завести зоны для web-partner через /interface-deep-dive
  zone, или пересмотреть surface.

[warning] capability-domain → capability:send-referral не имеет
  явного домена в docs/domains/.
  Доказательство: capability:send-referral.value = «один клик»; в
    docs/domains/ есть только `auth`, `billing`, `inventory`.
  Что делать: добавить домен `referrals` через /domain-deep-dive,
  или пересмотреть, действительно ли capability нужна.

[hint] market-capability → конкурент klara-app покрывает «mobile-первый
  опыт», у нас нет capability на mobile.
  Доказательство: market:klara-app.description = «mobile-first
    referrals»; capability.md → нет записи про mobile.
  Что делать: рассмотреть, нужно ли это вам — открыть
  /project-deep-dive capability для обсуждения.

Сводка: 2 error / 1 warning / 1 hint.
```

После отчёта — `AskUserQuestion` по каждому top-K finding (до 4 в
раунде):

- «Принять как корректное» — finding записывается в last-report как
  принятый, при следующем прогоне может игнорироваться (см.
  `references/angles.md` про suppressions).
- «Действительно нужно править» — finding идёт в next-actions,
  скилл предлагает запустить `/project-deep-dive` или
  `/interface-deep-dive` (но **не вызывает сам**).
- «False positive» — записывается, но игнорируется.
- «Обсудить позже» — оставить в last-report без решения.

## `audit-state/last-report.md`

```markdown
---
ran-on: <UTC-ts>
lenses-run: 8
layers: { project: yes, interface: yes, domain: yes, screen: no }
findings: { error: X, warning: Y, hint: Z }
verdicts: { accepted: A, needs-fix: B, false-positive: C, deferred: D }
---

# Reasoning trace

## Lens: persona-who
- agent-id: agent-7c
- duration: 18s
- findings: 3
- verdicts: [accepted, needs-fix, accepted]
- details:
  - finding-1 (error): … → verdict: needs-fix
  - finding-2 (warning): … → verdict: accepted
  - …

## Lens: capability-situation
- …

…
```

## Suppressions

Findings, помеченные «false positive», сохраняются в
`audit-state/suppressions.md`:

```markdown
- lens: persona-who; pattern: "persona:doctor without who"; reason: <от
  аналитика, через Other в AskUserQuestion>; suppressed-since: <ts>
```

При следующем прогоне агент-lens получает suppressions как контекст и
**не** генерирует те же findings, если они подпадают под паттерн.
Suppressions можно вручную удалить из файла, чтобы заново всплыли.

## Что не делать

- **Не править артефакты.** Cross-audit — только отчёт и решения
  аналитика, что с findings делать.
- **Не вызывать другие скилы автоматически.** В next-actions — текст,
  что запустить.
- **Не выдумывать findings.** Если агент вернул пустой массив — так
  и пишем «0 findings» по этому lens.
- **Не игнорировать отсутствующие слои.** `docs/domains/` нет — lens
  `capability-domain` и `integration-domain` пропускаются с явной
  пометкой «слой не существует» в отчёте.
- **Не запускать рой повторно** для одной сессии. Если findings много —
  пройти по ним постепенно. Повторный прогон — следующая сессия или
  явный `/cross-audit` запуск.
- **Не предлагать клиенту запустить** `/cross-audit`. Это аналитический
  инструмент; в `project-deep-dive-for-business` он не упоминается.
