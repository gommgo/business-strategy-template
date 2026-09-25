# docs/ — карта документации

Документация — **design-time source of truth** стратегии бизнеса (и проектирования
продукта, когда он нужен). Здесь нет кода: артефакты — чистая язык-агностичная
аналитика. Когда стратегия рождает продукт, его stable-артефакты читают соседние
форки (`<org>/{backend,frontend,site,mobile,infra}` и `<org>/<bot>`, см. «Что docs
отдаёт соседям»). На код аналитика напрямую не мапится: переход к фронт-коду — через
FSD-карту `fsd/<surface>/` (единственное место, где FSD-имена легальны), к коду
мобильного приложения — через карту `mobile/<surface>/`; wireframe и hi-fi по
`screens/<surface>/` автор макета собирает вручную. Заполняют артефакты deep-dive-
скиллы (`.claude/skills/`); рекомендуемый вход — оркестраторы `/entrypoint`
(аналитик) и `/entrypoint-for-business` (клиент), которые классифицируют сырьё
и маршрутизируют к исполнителям (прямой вызов исполнителя тоже допустим, см.
`getting-started.md`).

## Слои

Поток сверху вниз: бизнес (+ реестр проблем и стейкхолдеры) → сегменты и граф работ
(AJTBD) → SWOT → Карта гипотез (терминал — `task`). Исход — задача, закрывающая
проблему, либо **опционально** продукт → интерфейс / сервисы и домены / экраны,
FSD-карта, диалоги бота или карта мобильного приложения; физика всех продуктов —
ИТ-периметр бизнеса (`projects/infrastructure/`).

| каталог | вопрос | вход |
|---|---|---|
| [`business/`](./business/README.md) | **кто этот бизнес заказчика, какие его проблемы решаем и кто в нём принимает решения** (1 singleton + 5 kind + реестр `business-problem` + стейкхолдеры `stakeholder` · `stakeholder-map`) | `/business-deep-dive` (аналитик); клиент — `/entrypoint-for-business` |
| [`ajtbd/`](./ajtbd/README.md) | **кто наш сегмент по работам, его граф работ и трения** (Advanced JTBD, 5 kind) | `/segment-deep-dive` · `/job-graph-deep-dive` · `/jtbd-interview` (аналитик); клиент — `/entrypoint-for-business` |
| [`swot/`](./swot/README.md) | **за счёт чего возможен следующий шаг** (LinkedSWOT: `factor` · `bet`, M:N) | `/swot-deep-dive` |
| [`hypothesis-map/`](./hypothesis-map/README.md) | **под какие метрики целимся** (Карта гипотез: `goal` · `metric` · `subject` · `hypothesis` · `task`, M:N) | `/hypothesis-map-deep-dive` |
| [`projects/`](./projects/README.md) | **продукты под бизнес** (опционально, когда исход — продукт; несколько, см. ниже) | `/project-deep-dive <slug>` (аналитик); клиент — `/entrypoint-for-business` |
| `projects/_template/` | **канон формы** продуктовых слоёв (образец, не данные) | read-only, наследуется форком |
| `projects/<slug>/` | **данные одного продукта** (vision + surface-реестр + kind + `capability/<surface>` + `interface/<surface>/` + `screens/<surface>/`, `telegram-bot-flow/<surface>/` или `mobile/<surface>/` — по `type` поверхности + `fsd/<surface>/` для фронтовых поверхностей + `services/`) | скиллы слоёв `<slug>` |
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
- `fsd/<surface>/` — FSD-карта фронтовой поверхности (`type: web` / `admin` /
  `desktop` / `embed`): entities / features / pages / widgets / app /
  shared-ui / shared-api / shared-lib, мост к фронт-коду — вход
  `/fsd-deep-dive <slug> [<surface>]`.
- `telegram-bot-flow/<surface>/` — фичи `features/<feature>/` (dialog /
  window / use-case бота) + сквозные `command` / `notification` на корне
  (для поверхностей с `type: bot` — вместо `screens/`) — вход
  `/telegram-bot-flow-deep-dive <slug> [<surface>]`.
- `mobile/<surface>/` — карта мобильного приложения: entities / screens /
  flows / features / shell / entry-points / permissions / system-actions /
  widgets / background-tasks / shared-api / shared-lib (для поверхностей с
  `type: mobile` — вместо `screens/`) — вход
  `/mobile-deep-dive <slug> [<surface>]`.
- `services/` — сервисная топология бэкенда: реестры `service.md` /
  `platform.md`, singleton `architecture.md`, паспорта сервисов — вход
  `/service-deep-dive <slug>`.
- `services/<svc>/domains/` — DDD-артефакты бэкенда по bounded-context,
  внутри сервиса-владельца (surface-агностичны) — вход
  `/domain-deep-dive <slug> <ctx>`.

## Аудиты (только отчёт)

- `/project-audit <slug>` · `/interface-audit <slug>` · `/screen-audit <slug>`
  · `/fsd-audit <slug>` · `/telegram-bot-flow-audit <slug>` ·
  `/mobile-audit <slug>` · `/service-audit <slug>` — узкая консистентность
  внутри слоя проекта.
- `/infrastructure-audit` — структура ИТ-периметра (размещение, рефы,
  сироты).
- `/ajtbd-audit` — инварианты методологии графа работ по каждому сегменту (рой).
- `/swot-audit` — инварианты LinkedSWOT по каждой проблеме (рой).
- `/hypothesis-map-audit` — инварианты Карты гипотез по каждой проблеме (рой).
- `/cross-audit` — сквозная семантика между слоями (рой).

## Связи между слоями

Связи **семантические**, не slug-валидируемые. Сквозные рёбра авторятся
**снизу вверх**: проектная или UX-сущность ссылается на глобальную
(`situation.jobs` · `situation.capabilities` · `situation.hypotheses`,
`capability.jobs` · `capability.hypotheses`, `user.segments`,
`subject.segments`); обратную сторону и несостыковки сводит рой `/cross-audit`
(по каждому проекту). Подробности каждой связи — в README слоёв.

| связь | смысл |
|---|---|
| `business/profile` · `competitor` → `swot/factor` | сильные/слабые стороны и тренды/угрозы вырастают из картины бизнеса |
| `business/current-metric` → `hypothesis-map/metric.current` | текущий KPI бизнеса — baseline целевой метрики |
| `ajtbd/segment` → `hypothesis-map/subject` · `projects/<slug>/user` | сегмент по работам проявляется субъектом влияния и пользователем продукта |
| `ajtbd/segment-problem` → `business/business-problem` · `vision.Problem` | трение сегмента доказывает проблему бизнеса и проблему продукта |
| `ajtbd/job` (Big / Core) → `vision.Success` | успех продукта целит в работу сегмента |
| `ajtbd/job-graph.value-mechanics` → `capability` | механики ценности графа работ — кандидаты в возможности продукта |
| `ajtbd/solution` ↔ `business/competitor` · `offering` | нанятое решение сопоставляется с игроком рынка или офером бизнеса |
| `swot/bet.promoted-to` → `hypothesis-map/goal` · `hypothesis` | ставка дотягивается до цели или гипотезы |
| `business/business-problem` ↔ `projects/<slug>/vision.addresses-problem` | проблема ↔ продукт, M:N; авторская сторона — продукт |
| `hypothesis-map/goal` · `metric` · `subject` → `vision` · `capability` · `user` | цель, метрика и субъект проявляются в проекте |
| `business/stakeholder` ↔ `subject` · `user` · `who` · `swot/factor` · `bet` · `goal` · `constraint` | человек-решатель внутри заказчика в других линзах (`manifests-as`); детали — [`business/README.md`](./business/README.md) |
| `user` → `interface/<surface>/who` | пользователь продукта проявляется ролью участника |
| `capability/<surface>` → `interface/<surface>/situation` + домен сервиса-владельца | возможность реализуется ситуациями той же поверхности и доменом |
| `surface` → `capability/` · `interface/` · `screens/` · `telegram-bot-flow/` · `mobile/` · `fsd/` | поверхность — ось партиционирования продуктовых слоёв |
| `integration` → функции → клиент `services/_shared/integrations/<slug>/` → use-case | бизнес-каталог функций, конкретный клиент, потребление по `slug` (домен transport-agnostic); стык продуктов бизнеса — `project-map.md` |
| `fsd/<surface>/` ← `situation` · `screen` / `block` · домен | карта слайсов фронта строится из аналитики поверхности |
| `window` → `interface/block`; `widget.action` / `getter` → use-case бота → доменный use-case; `notification` ← `event:<ctx>.<Event>` | бот — фронтенд без собственных бизнес-правил: правила в домене, оркестрация — в use-case бота |
| мобильные `screen` · `feature` → `situation`; `entity` → агрегат домена или `local`; точки входа, системные действия, виджеты, фоновые задачи → `situation`; push, обновление виджета, фон ← `event:<ctx>.<Event>` | всё, что живёт вне экранов, тоже обосновано ситуацией; посредники платформы (доставка push, ассистент, облачное распознавание речи) — `integration`, неснимаемые свойства платформы и правила магазина — `constraint` |

## Что docs отдаёт соседям (handoff-контракт)

`<org>/strategy` — **жёсткий upstream** для остальных форков экосистемы (актуален,
когда стратегия дошла до продукта). Контракт **read-only и односторонний**: соседи
**читают** stable-артефакты этого репо, сами в него не пишут.

| потребитель (форк) | что читает | для чего |
|---|---|---|
| **`<org>/backend`** (`go-backend-template`) | `projects/<slug>/services/<svc>/domains/<ctx>/` + `services/_shared/` (VO + клиенты интеграций) + паспорт `services/<svc>/README.md` (stable) | `/scaffold` domain → Go-код **по сервису**: паспорт задаёт границы деплой-юнита (Exposes / Dependencies / Resources / Messaging), домены — начинку; маппинг DDD → Go (включая `integration-client` → порт/адаптер) живёт у него (`docs/reference/domain-mapping.md`) |
| **`<org>/frontend`** (`spa-frontend-template`) | `projects/<slug>/fsd/<surface>/` (stable-карта слайсов) + `{interface,screens}/<surface>/` + product-файлы + `services/*/domains/` (контекст) | `/scaffold` и `/de-template` фронта разворачивают stable-записи FSD-карты в код (`src/`-пути выводят сами); карта проектируется здесь — `/fsd-deep-dive` (по фронтовой поверхности) |
| **`<org>/site`** (`ssr-frontend-template`) | `projects/<slug>/fsd/<surface>/` (stable-карта слайсов) + `{interface,screens}/<surface>/` (контекст: аудитории, ситуации, экраны, блоки) | `/scaffold` и `/de-template` сайта разворачивают stable-записи FSD-карты в страницы и коллекции; карта проектируется здесь — `/fsd-deep-dive` |
| **`<org>/<bot>`** (`telegram-bot-template`) | `projects/<slug>/telegram-bot-flow/<surface>/` (фичи: диалоги, окна, use-case'ы бота-оркестратора) + `interface/<surface>/` + `services/*/domains/` (доменные use-case'ы и события под оркестратор) | проектирование и scaffold диалогов бота: StatesGroup, окна, виджеты, getter'ы, сервисы-оркестраторы, обработчики |
| **`<org>/mobile`** (`mobile-template`) | `projects/<slug>/mobile/<surface>/` (stable-карта приложения, 12 kind) + `interface/<surface>/` + `services/*/domains/` (контекст ситуаций, сущностей и событий) | `/scaffold` и `/de-template` мобильного репо разворачивают stable-записи карты в три места — `shared/`, `androidApp/`, `iosApp/` (пути выводят сами; маппинг kind → код — его `docs/reference/strategy-mapping.md`); карта проектируется здесь — `/mobile-deep-dive` (по мобильной поверхности) |
| **`<org>/infra`** (`project-infra-template-compose`) | скиллы хаба — `projects/<slug>/vision.md` и `surface.md`; остальное — контекстом планирования: `services/{service,platform}.md`, секции `Resources`/`Messaging` паспортов, `projects/infrastructure/` | `/init-project` (scope продукта → карта сервисов), `/stack-deep-dive` (публичные поверхности → сабдомены и edge-роуты), `/de-template` (шапка `CLAUDE.md`/`README.md` под проект), `/smartdev` (sanity на старте сессии). Сервисную топологию и ИТ-периметр хаб читает как контекст, когда планирует работу (`/plan`, программы сквозных задач в `.claude/plans/`): что билдить, где располагать, что провижинить; runtime-механика (реплики, размеры, манифесты) — решение infra |

Соседи держат `<org>/strategy` sibling-checkout'ом рядом (по умолчанию
`../strategy`; как переопределить путь — в обвязке соседа). Эти артефакты —
единственное, что docs производит для экосистемы; ничего обратно из них не
импортируется.

## Где это в экосистеме

`<org>/strategy` — форк одного из 7 шаблонов `stit-core/*`:
`business-strategy-template` → `<org>/strategy` (этот),
`project-infra-template-compose` → `<org>/infra`, `go-backend-template` →
`<org>/backend`, `spa-frontend-template` → `<org>/frontend`,
`ssr-frontend-template` → `<org>/site`, `telegram-bot-template` → `<org>/<bot>`,
`mobile-template` → `<org>/mobile`; рядом — библиотеки `golibinfra` (Go) и
`pylibinfra` (Python). Форки одной орги лежат рядом sibling-checkout'ами.

Флоу: проект **стартует здесь** — стратегия и проектирование продукта до кода.
Спроектированный продукт уходит в **операционный хаб `<org>/infra`**: там
`/init-project` читает strategy и поднимает инфру, сквозная задача ведётся
программой в `.claude/plans/` инфры, а агенты расходятся по сиблингам и работают
обвязкой того репо. Изменение дизайна по ходу — агент из хаба приходит сюда и
работает скиллами этого репо; прямой заход сюда — тоже нормальный режим. Канон
карты и флоу — `docs/reference/ecosystem.md` хаба `<org>/infra`.

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
