# docs/ — карта документации

Документация — **design-time source of truth** аналитики проекта. Здесь нет
кода: артефакты — чистая язык-агностичная аналитика, которую читают соседние
форки (`<org>/{backend,frontend,infra}`) и по которой автор макета вручную
собирает hi-fi субстрат на `@sftbmb/ui`. Заполняют артефакты deep-dive-
скиллы (`.claude/skills/`); рекомендуемый вход — оркестраторы `/entrypoint`
(аналитик) и `/entrypoint-for-business` (клиент), которые классифицируют сырьё
и маршрутизируют к исполнителям (прямой вызов исполнителя тоже допустим, см.
`getting-started.md`).

## Слои

Поток сверху вниз: бизнес (+ реестр проблем) → сегменты и граф работ (AJTBD) →
SWOT → Карта гипотез → продукты → интерфейс / домены / экраны.

| каталог | вопрос | вход |
|---|---|---|
| [`business/`](./business/README.md) | **кто этот бизнес заказчика и какие его проблемы решаем** (1 singleton + 5 kind + реестр `business-problem`) | `/business-deep-dive` (аналитик); клиент — `/entrypoint-for-business` |
| [`ajtbd/`](./ajtbd/README.md) | **кто наш сегмент по работам, его граф работ и трения** (Advanced JTBD, 5 kind) | `/segment-deep-dive` · `/job-graph-deep-dive` · `/jtbd-interview` (аналитик); клиент — `/entrypoint-for-business` |
| [`swot/`](./swot/README.md) | **за счёт чего возможен следующий шаг** (LinkedSWOT: `factor` · `bet`, M:N) | `/swot-deep-dive` |
| [`hypothesis-map/`](./hypothesis-map/README.md) | **под какие метрики целимся** (Карта гипотез: `goal` · `metric` · `subject` · `hypothesis` · `task`, M:N) | `/hypothesis-map-deep-dive` |
| [`projects/`](./projects/README.md) | **продукты под бизнес** (несколько; см. ниже) | `/project-deep-dive <slug>` (аналитик); клиент — `/entrypoint-for-business` |
| `projects/_canon/` | **канон формы** продуктовых слоёв (образец, не данные) | read-only, наследуется форком |
| `projects/<slug>/` | **данные одного продукта** (vision + 7 kind + `interface/` + `domains/` + `screens/`) | скиллы слоёв `<slug>` |
| `projects/example/` | **показная витрина** screens-слоя (медисследования) | удаляется `/de-template` |

Внутри проекта `projects/<slug>/`:

- `vision.md` + 7 kind продукта (user / capability / boundary / surface /
  integration / constraint / market) — вход `/project-deep-dive <slug>`.
- `interface/` — who / stage / situation / zone / block / ux-substrate /
  data-items — вход `/interface-deep-dive <slug>`.
- `domains/` — (опц.) DDD-артефакты бэкенда по контекстам — вход
  `/domain-deep-dive <slug> <ctx>`.
- `screens/` — flow / screen / block / shell — вход `/screen-deep-dive <slug>`.

## Аудиты (только отчёт)

- `/project-audit <slug>` · `/interface-audit <slug>` · `/screen-audit <slug>`
  — узкая консистентность внутри слоя проекта.
- `/ajtbd-audit` — инварианты методологии графа работ по каждому сегменту (рой).
- `/swot-audit` — инварианты LinkedSWOT по каждой проблеме (рой).
- `/hypothesis-map-audit` — инварианты Карты гипотез по каждой проблеме (рой).
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

`<org>/docs` — один из **5 форкаемых шаблонов** под `sftbmb-core/`
(`corp-infra-template`, `go-backend-template`, `spa-frontend-template`,
`project-docs-template` — этот, `project-infra-template-compose`), плюс 2 общие
библиотеки: Go-lib `sftbmb-core/golibinfra` и дизайн-система `@sftbmb/ui` (репо
`sftbmb-core/ui-lib`). Корп control-plane — репо `corp-infra-template` (managed =
инстанс на `*.sftbmb.ru`, self-hosted = ваш форк; вендор-лока нет). Роль этого
репо — **design-time SoT** проекта; форкается **первым**, наполняется аналитикой,
дальше форкаются код-репо (которые его читают). Канон-карта контрактов
(и self-hosted-канон) — `corp-infra-template/docs/ecosystem.md`.

## Форку

- [`getting-started.md`](./getting-started.md) — путь потребителя форка (META,
  удаляется в `/de-template`).
- [`../client-onboarding/`](../client-onboarding/README.md) — комплект
  онбординга заказчика (`windows.md` / `macos.md`): поставить Claude Desktop,
  скачать форк и зайти в `/entrypoint-for-business`. Один файл под ОС, отдаём
  заказчику.
- Устройство `.claude`-системы (rules / skills / state / settings) — корневой
  `CLAUDE.md`.

## Forward-only

Все артефакты — текущее состояние. Без «было/стало», без changelog'ов внутри
текста, без следов отменённых решений. История — в `git log`. Полное правило —
`.claude/rules/forward-only.md`.
