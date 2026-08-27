# docs/ — карта документации

Документация — **design-time source of truth** стратегии бизнеса (и проектирования
продукта, когда он нужен). Здесь нет кода: артефакты — чистая язык-агностичная
аналитика. Когда стратегия рождает продукт, его артефакты читают соседние форки
(`<org>/{backend,frontend,infra}` и `<org>/<bot>`) и по ним автор макета вручную собирает hi-fi
субстрат на `@stit/ui`. Заполняют артефакты deep-dive-
скиллы (`.claude/skills/`); рекомендуемый вход — оркестраторы `/entrypoint`
(аналитик) и `/entrypoint-for-business` (клиент), которые классифицируют сырьё
и маршрутизируют к исполнителям (прямой вызов исполнителя тоже допустим, см.
`getting-started.md`).

## Слои

Поток сверху вниз: бизнес (+ реестр проблем) → сегменты и граф работ (AJTBD) →
SWOT → Карта гипотез (терминал — `task`). Исход — задача, закрывающая проблему,
либо **опционально** продукт → интерфейс / сервисы и домены / экраны;
физика всех продуктов — ИТ-периметр бизнеса (`projects/infrastructure/`).

| каталог | вопрос | вход |
|---|---|---|
| [`business/`](./business/README.md) | **кто этот бизнес заказчика и какие его проблемы решаем** (1 singleton + 5 kind + реестр `business-problem`) | `/business-deep-dive` (аналитик); клиент — `/entrypoint-for-business` |
| [`ajtbd/`](./ajtbd/README.md) | **кто наш сегмент по работам, его граф работ и трения** (Advanced JTBD, 5 kind) | `/segment-deep-dive` · `/job-graph-deep-dive` · `/jtbd-interview` (аналитик); клиент — `/entrypoint-for-business` |
| [`swot/`](./swot/README.md) | **за счёт чего возможен следующий шаг** (LinkedSWOT: `factor` · `bet`, M:N) | `/swot-deep-dive` |
| [`hypothesis-map/`](./hypothesis-map/README.md) | **под какие метрики целимся** (Карта гипотез: `goal` · `metric` · `subject` · `hypothesis` · `task`, M:N) | `/hypothesis-map-deep-dive` |
| [`projects/`](./projects/README.md) | **продукты под бизнес** (опционально, когда исход — продукт; несколько, см. ниже) | `/project-deep-dive <slug>` (аналитик); клиент — `/entrypoint-for-business` |
| `projects/_template/` | **канон формы** продуктовых слоёв (образец, не данные) | read-only, наследуется форком |
| `projects/<slug>/` | **данные одного продукта** (vision + surface-реестр + kind + `capability/<surface>` + `interface/<surface>/` + `screens/<surface>/` или `telegram-bot-flow/<surface>/` + `services/`) | скиллы слоёв `<slug>` |
| `projects/project-map.md` | **карта стыков между продуктами бизнеса** (межпроектный граф) | сводится из `integration`, сверяет `/cross-audit` |
| [`projects/infrastructure/`](./projects/infrastructure/README.md) | **ИТ-периметр бизнеса** (сервера · рантаймы · общие платформенные ресурсы · джобы · размещение; один на все проекты) | `/infrastructure-deep-dive` |

Поверхность (`surface`) — ось продукта: реестр `surface.md` объявляет
поверхности, а их slug'и партиционируют возможности, интерфейс и экраны.
Внутри проекта `projects/<slug>/`:

- `vision.md` + реестр-хребет `surface.md` + кросс-поверхностные kind
  (user / integration / boundary / constraint / market) — вход
  `/project-deep-dive <slug>`.
- `capability/<surface>.md` — возможности по поверхности — вход
  `/project-deep-dive <slug>`.
- `interface/<surface>/` — who / stage / situation / zone / block /
  ux-substrate / data-items — вход `/interface-deep-dive <slug> [<surface>]`.
- `screens/<surface>/` — flow / screen / block / shell — вход
  `/screen-deep-dive <slug> [<surface>]`.
- `telegram-bot-flow/<surface>/` — фичи `features/<feature>/` (dialog /
  window / use-case бота) + сквозные `command` / `notification` на корне
  (для поверхностей с `type: bot` — вместо `screens/`) — вход
  `/telegram-bot-flow-deep-dive <slug> [<surface>]`.
- `services/` — сервисная топология бэкенда: реестры `service.md` /
  `platform.md`, singleton `architecture.md`, паспорта сервисов — вход
  `/service-deep-dive <slug>`.
- `services/<svc>/domains/` — DDD-артефакты бэкенда по bounded-context,
  внутри сервиса-владельца (surface-агностичны) — вход
  `/domain-deep-dive <slug> <ctx>`.

## Аудиты (только отчёт)

- `/project-audit <slug>` · `/interface-audit <slug>` · `/screen-audit <slug>`
  · `/telegram-bot-flow-audit <slug>` · `/service-audit <slug>` — узкая
  консистентность внутри слоя проекта.
- `/infrastructure-audit` — структура ИТ-периметра (размещение, рефы,
  сироты).
- `/ajtbd-audit` — инварианты методологии графа работ по каждому сегменту (рой).
- `/swot-audit` — инварианты LinkedSWOT по каждой проблеме (рой).
- `/hypothesis-map-audit` — инварианты Карты гипотез по каждой проблеме (рой).
- `/cross-audit` — сквозная семантика между слоями (рой).

## Что docs отдаёт соседям (handoff-контракт)

`<org>/strategy` — **жёсткий upstream** для остальных форков экосистемы (актуален,
когда стратегия дошла до продукта). Контракт **read-only и односторонний**: соседи
**читают** stable-артефакты этого репо, сами в него не пишут.

| потребитель (форк) | что читает | для чего |
|---|---|---|
| **`<org>/backend`** (`go-backend-template`) | `projects/<slug>/services/<svc>/domains/<ctx>/` + `services/_shared/` (VO + клиенты интеграций) + паспорт `services/<svc>/README.md` (stable) | `/scaffold` domain → Go-код **по сервису**: паспорт задаёт границы деплой-юнита (Exposes / Dependencies / Resources / Messaging), домены — начинку; маппинг DDD → Go (включая `integration-client` → порт/адаптер) живёт у него (`docs/reference/domain-mapping.md`) |
| **`<org>/frontend`** (`spa-frontend-template`) | `projects/<slug>/fsd/<surface>/` (stable-карта слайсов) + `{interface,screens}/<surface>/` + product-файлы (контекст) | `/scaffold` и `/de-template` фронта разворачивают stable-записи FSD-карты в код (`src/`-пути выводят сами); карта проектируется здесь — `/fsd-deep-dive` (по SPA-поверхности) |
| **`<org>/<bot>`** (`telegram-bot-template`) | `projects/<slug>/telegram-bot-flow/<surface>/` (фичи: диалоги, окна, use-case'ы бота-оркестратора) + `interface/<surface>/` + `services/*/domains/` (доменные use-case'ы и события под оркестратор) | проектирование и scaffold диалогов бота: StatesGroup, окна, виджеты, getter'ы, сервисы-оркестраторы, обработчики |
| **`<org>/infra`** (`project-infra-template-compose`) | `projects/<slug>/{vision, surface}` + `projects/<slug>/services/{service,platform}.md` + секции `Resources`/`Messaging` паспортов + весь `projects/infrastructure/` | `/init-project` + материализация смысловой топологии e2e: что билдить (сервисы), где располагать (placement/runtime/server), что провижинить (БД/кэши/бакеты/топики); runtime-механика (реплики, размеры, манифесты) — решение infra |

Соседи держат `<org>/strategy` sibling-checkout'ом рядом и резолвят путь через
свой `docs/reference/ecosystem.md`. Эти артефакты — единственное, что docs
производит для экосистемы; ничего обратно из них не импортируется.

## Где это в экосистеме

`<org>/strategy` — один из **6 форкаемых шаблонов** под `stit-core/`
(`corp-infra-template`, `go-backend-template`, `spa-frontend-template`,
`telegram-bot-template`, `business-strategy-template` — этот,
`project-infra-template-compose`), плюс 2 общие
библиотеки: Go-lib `stit-core/golibinfra` и дизайн-система `@stit/ui` (репо
`stit-core/ui-lib`). Корп control-plane — репо `corp-infra-template` (managed =
инстанс на `*.stit.tech`, self-hosted = ваш форк; вендор-лока нет). Роль этого
репо — **design-time SoT** стратегии; форкается **первым**, наполняется аналитикой,
дальше — когда стратегия рождает продукт — форкаются код-репо (которые его читают).
Канон-карта контрактов (и self-hosted-канон) — `corp-infra-template/docs/ecosystem.md`.

## Форку

- [`getting-started.md`](./getting-started.md) — путь потребителя форка (META).
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
