# docs/ — карта документации

Документация — **design-time source of truth** аналитики проекта. Здесь нет
кода: артефакты — чистая язык-агностичная аналитика, которую читают соседние
форки (`<org>/{backend,frontend,infra}`) и по которой автор макета вручную
собирает hi-fi субстрат на `@stit-design/ui`. Заполняют артефакты deep-dive-
скиллы (`.claude/skills/`); онбординг ведёт аналитик руками — оркестратора нет
(by design, см. `getting-started.md`).

## Слои

Поток сверху вниз: бизнес → проблемы → продукты → интерфейс / домены / экраны.

| каталог | вопрос | вход |
|---|---|---|
| [`business/`](./business/README.md) | **кто этот бизнес заказчика** (1 singleton + 6 kind) | `/business-deep-dive` · `/business-deep-dive-for-business` |
| [`business-problem/`](./business-problem/README.md) | **какие проблемы решаем и под какие метрики целимся** (`frame`-таблица + 7 kind, M:N) | `/business-problem-deep-dive` · `/business-problem-deep-dive-for-business` |
| [`projects/`](./projects/README.md) | **продукты под бизнес** (несколько; см. ниже) | `/project-deep-dive <slug>` · `/project-deep-dive-for-business` |
| `projects/_canon/` | **канон формы** продуктовых слоёв (образец, не данные) | read-only, наследуется форком |
| `projects/<slug>/` | **данные одного продукта** (vision + 7 kind + `interface/` + `domains/` + `screens/`) | скиллы слоёв `<slug>` |
| `projects/example/` | **показная витрина** screens-слоя (медисследования) | удаляется `/de-template` |

Внутри проекта `projects/<slug>/`:

- `vision.md` + 7 kind продукта (persona / capability / boundary / surface /
  integration / constraint / market) — вход `/project-deep-dive <slug>`.
- `interface/` — who / stage / situation / zone / block / ux-substrate /
  data-items — вход `/interface-deep-dive <slug>`.
- `domains/` — (опц.) DDD-артефакты бэкенда по контекстам — вход
  `/domain-deep-dive <slug> <ctx>`.
- `screens/` — flow / screen / block / shell — вход `/screen-deep-dive <slug>`.

## Аудиты (только отчёт)

- `/project-audit <slug>` · `/interface-audit <slug>` · `/screen-audit <slug>`
  — узкая консистентность внутри слоя проекта.
- `/business-problem-audit` — инварианты методологии по каждой проблеме (рой).
- `/cross-audit` — сквозная семантика между слоями (рой).

## Что docs отдаёт соседям (handoff-контракт)

`<org>/docs` — **жёсткий upstream** для остальных форков экосистемы. Контракт
**read-only и односторонний**: соседи **читают** stable-артефакты этого репо,
сами в него не пишут.

| потребитель (форк) | что читает | для чего |
|---|---|---|
| **`<org>/backend`** (`go-backend-template`) | `projects/<slug>/domains/<ctx>/` (stable) | `/scaffold` domain → Go-код; маппинг DDD → Go живёт у него (`docs/reference/domain-mapping.md`) |
| **`<org>/frontend`** (`spa-frontend-template`) | `projects/<slug>/{interface,screens}/` + product-файлы | `/fsd-deep-dive` мапит ситуации/блоки/сущности на FSD-слои |
| **`<org>/infra`** (`project-infra-template-compose`) | `projects/<slug>/{vision, surface}` | `/init-project` читает продуктовый контекст (vision / surfaces) |

Соседи держат `<org>/docs` sibling-checkout'ом рядом и резолвят путь через
свой `docs/reference/ecosystem.md`. Эти артефакты — единственное, что docs
производит для экосистемы; ничего обратно из них не импортируется.

## Где это в экосистеме

`<org>/docs` — один из **4 форкаемых шаблонов** под `stit-template/`
(`go-backend-template`, `spa-frontend-template`, `project-docs-template` — этот,
`project-infra-template-compose`), плюс корп control-plane `stit-infra/{infra,
golibinfra}` и дизайн-система `@stit-design/ui` (репо `stit-design/ui-lib`).
Роль этого репо — **design-time SoT** проекта; форкается **первым**, наполняется
аналитикой, дальше форкаются код-репо (которые его читают). Канон-карта
контрактов — `stit-infra/infra/docs/ecosystem.md`.

## Форку

- [`getting-started.md`](./getting-started.md) — путь потребителя форка (META,
  удаляется в `/de-template`).
- Устройство `.claude`-системы (rules / skills / state / settings) — корневой
  `CLAUDE.md`.

## Forward-only

Все артефакты — текущее состояние. Без «было/стало», без changelog'ов внутри
текста, без следов отменённых решений. История — в `git log`. Полное правило —
`.claude/rules/forward-only.md`.
