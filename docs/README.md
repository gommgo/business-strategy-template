# docs/ — карта документации

Документация — **design-time source of truth** стратегии бизнеса (и проектирования
продукта, когда он нужен). Здесь нет кода: артефакты — чистая язык-агностичная
аналитика. Когда стратегия рождает продукт, его stable-артефакты читают соседние
форки (`<org>/{backend,frontend,site,mobile,infra}` и `<org>/<bot>`, см. «Что docs
отдаёт соседям»). На код аналитика напрямую не мапится: переход к фронт-коду кабинета —
через FSD-карту `fsd/<surface>/` (единственное место, где FSD-имена легальны), к коду
сайта и лендинга — через слой страницы `site/<surface>/`, к коду мобильного
приложения — через карту `mobile/<surface>/`; макет собирает слой дизайна `design/` в
Claude Design по слою страницы или экранам. Заполняют артефакты deep-dive-
скиллы (`.claude/skills/`); рекомендуемый вход — оркестраторы `/entrypoint`
(аналитик) и `/entrypoint-for-business` (клиент), которые классифицируют сырьё
и маршрутизируют к исполнителям (прямой вызов исполнителя тоже допустим, см.
`getting-started.md`).

## Слои

Поток сверху вниз: бизнес (+ реестр проблем и стейкхолдеры) → сегменты и граф работ
(AJTBD) → SWOT → Карта гипотез (терминал — `task`). Исход — задача, закрывающая
проблему, либо **опционально** продукт → интерфейс / сервисы и домены / экраны,
FSD-карта, слой страницы сайта и лендинга, диалоги бота или карта мобильного
приложения, облик продукта; физика всех продуктов — ИТ-периметр бизнеса
(`projects/infrastructure/`).

| каталог | вопрос | вход |
|---|---|---|
| [`business/`](./business/README.md) | **кто этот бизнес заказчика, какие его проблемы решаем и кто в нём принимает решения** (1 singleton + 5 kind + реестр `business-problem` + стейкхолдеры `stakeholder` · `stakeholder-map`) | `/business-deep-dive` (аналитик); клиент — `/entrypoint-for-business` |
| [`ajtbd/`](./ajtbd/README.md) | **кто наш сегмент по работам, его граф работ и трения** (Advanced JTBD, 5 kind) | `/segment-deep-dive` · `/job-graph-deep-dive` · `/jtbd-interview` (аналитик); клиент — `/entrypoint-for-business` |
| [`swot/`](./swot/README.md) | **за счёт чего возможен следующий шаг** (LinkedSWOT: `factor` · `bet`, M:N) | `/swot-deep-dive` |
| [`hypothesis-map/`](./hypothesis-map/README.md) | **под какие метрики целимся** (Карта гипотез: `goal` · `metric` · `subject` · `hypothesis` · `task`, M:N) | `/hypothesis-map-deep-dive` |
| [`projects/`](./projects/README.md) | **продукты под бизнес** (опционально, когда исход — продукт; несколько, см. ниже) | `/project-deep-dive <slug>` (аналитик); клиент — `/entrypoint-for-business` |
| `projects/_template/` | **канон формы** продуктовых слоёв (образец, не данные) | read-only, наследуется форком |
| `projects/<slug>/` | **данные одного продукта** (vision + surface-реестр + kind, в том числе `object.md` · `action.md` + файлы уровня продукта `facts.yaml` · `voice*.yaml` + `capability/<surface>` + `interface/<surface>/` (кроме сайта и лендинга) + `screens/<surface>/`, `site/<surface>/`, `telegram-bot-flow/<surface>/` или `mobile/<surface>/` — по `type` и роду поверхности + `fsd/<surface>/` для фронтовых поверхностей кабинета + облик `design/` + `services/`) | скиллы слоёв `<slug>` |
| `projects/project-map.md` | **карта стыков между продуктами бизнеса** (межпроектный граф) | сводится из `integration`, сверяет `/cross-audit` |
| [`projects/infrastructure/`](./projects/infrastructure/README.md) | **ИТ-периметр бизнеса** (сервера · рантаймы · общие платформенные ресурсы · джобы · размещение; один на все проекты) | `/infrastructure-deep-dive` |

Поверхность (`surface`) — ось продукта: реестр `surface.md` объявляет
поверхности, а их slug'и партиционируют возможности, интерфейс и экраны.
Внутри проекта `projects/<slug>/`:

- `vision.md` + реестр-хребет `surface.md` (тип и род поверхности `web-kind`) +
  кросс-поверхностные kind (user / integration / boundary / constraint /
  market), глоссарий объектов `object.md` и словарь действий `action.md` — вход
  `/project-deep-dive <slug>`.
- `capability/<surface>.md` — возможности по поверхности — вход
  `/project-deep-dive <slug>`.
- `facts.yaml` · `voice*.yaml` — факты и голос продукта (профили бренда и
  продукта), по желанию — слова клиента: машинные файлы по схемам базы скилла,
  одни на все поверхности — вход `/design-deep-dive <slug>`.
- `site/<surface>/` — слой страницы сайта и лендинга (`web` рода `landing` и
  `site` — вместо interface, screens и FSD): бриф, смысл, карта сайта, иерархии
  сообщений, планы и тексты страниц по слотам — вход
  `/design-deep-dive <slug> [<surface>]`.
- `interface/<surface>/` — who / stage / situation / scenario / zone / block /
  ux-substrate / data-items (кроме сайта и лендинга) — вход
  `/interface-deep-dive <slug> [<surface>]`.
- `screens/<surface>/` — flow / screen / block / shell, карта экранов `map.md`
  и тексты интерфейса `texts.md` (`web` рода `app`; `admin`, `desktop`,
  `embed`) — вход `/screen-deep-dive <slug> [<surface>]`.
- `fsd/<surface>/` — FSD-карта фронтовой поверхности (`web` рода `app`;
  `admin`, `desktop`, `embed`): entities / features / pages / widgets / app /
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
- `design/` — облик продукта: бренд, дизайн-система, бриф на вид кабинета,
  паспорт визуала, ассеты; `design/<surface>/` — арт-дирекция, ассеты, движение,
  холст с макетом и его приёмка, манифест готовности (`web`, `admin`, `desktop`,
  `embed`) — вход `/design-deep-dive <slug> [<surface>]`.
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
- `/design-audit <slug>` — слой страницы, слой дизайна и файлы уровня продукта:
  схемы, ссылки, покрытие текстами, фактами, ассетами и компонентами
  дизайн-системы, свежесть производных и приёмки; макет — по просьбе заказчика.
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
`capability.trace`, `user.segments`, `subject.segments`); обратную сторону и
несостыковки сводит рой `/cross-audit` (по каждому проекту). Подробности каждой
связи — в README слоёв.

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
| `surface` → `capability/<surface>` · `interface/` · `screens/` · `site/` · `telegram-bot-flow/` · `mobile/` · `fsd/` · `design/<surface>/` | поверхность — ось партиционирования продуктовых слоёв |
| `integration` → функции → клиент `services/_shared/integrations/<slug>/` → use-case | бизнес-каталог функций, конкретный клиент, потребление по `slug` (домен transport-agnostic); стык продуктов бизнеса — `project-map.md` |
| `fsd/<surface>/` ← `situation` · `screen` / `block` · домен | карта слайсов фронта строится из аналитики поверхности |
| `window` → `interface/block`; `widget.action` / `getter` → use-case бота → доменный use-case; `notification` ← `event:<ctx>.<Event>` | бот — фронтенд без собственных бизнес-правил: правила в домене, оркестрация — в use-case бота |
| мобильные `screen` · `feature` → `situation`; `entity` → агрегат домена или `local`; точки входа, системные действия, виджеты, фоновые задачи → `situation`; push, обновление виджета, фон ← `event:<ctx>.<Event>` | всё, что живёт вне экранов, тоже обосновано ситуацией; посредники платформы (доставка push, ассистент, облачное распознавание речи) — `integration`, неснимаемые свойства платформы и правила магазина — `constraint` |
| `business/material.md` · `current-metric.md` · `profile.md` → `projects/<slug>/facts.yaml` | факт страницы опирается на источник бизнеса |
| `hypothesis-map/metric.md` · `business/current-metric.md` → `site-brief.business.kpi` | цель воронки — метрика проблемы (цель, не гарантия) |
| `user` · `ajtbd/segment.md` · `segment-problem.md` → `meaning.audience` | аудитория и боли страницы |
| `vision` · `capability` · `boundary` · `market` → `meaning` · copy deck | страница обещает то, что продукт делает |
| `integration` → получатели заявок брифа | лендинг без бэкенда отдаёт заявки во внешние системы |
| `site/<surface>/plans` (медиа- и 3D-слоты) → `design/<surface>/assets/plans`; `treatment` ← арт-дирекция | ассеты — из слотов плана, подача — от арт-дирекции |
| `screens/<surface>` (`ui:`, роли текстов) → `projects/<slug>/design/system.yaml` | каждый тип экрана — компонент дизайн-системы, каждая роль — стиль текста |
| `vision` · `user#Постура` · `surface` · `object#statuses` → `projects/<slug>/design/app-brief.yaml` | бриф на вид кабинета — проекция продукта |
| `projects/<slug>/voice.yaml` · `projects/<slug>/voice.product.yaml` → тексты страницы, интерфейса, бота; README дизайн-системы | один голос продукта на всех поверхностях |
| `projects/<slug>/design/system.tokens.json` → `fsd` (тема), `mobile` (`shell`) | токены дизайн-системы — источник темы кода |

## Что docs отдаёт соседям (handoff-контракт)

`<org>/strategy` — **жёсткий upstream** для остальных форков экосистемы (актуален,
когда стратегия дошла до продукта). Контракт **read-only и односторонний**: соседи
**читают** stable-артефакты этого репо, сами в него не пишут. У слоёв страницы и
дизайна «закрыто» — статус в самом файле по его схеме или форме. Пакета-копии нет:
код-репо читает закрытые файлы по путям ниже, а готовность поверхности к сборке сводит
производный манифест `design/<surface>/ready.yaml` (канон —
[`projects/_template/design/README.md`](./projects/_template/design/README.md), раздел
«Пакет для кода»).

| потребитель (форк) | что читает | для чего |
|---|---|---|
| **`<org>/backend`** (`go-backend-template`) | `projects/<slug>/services/<svc>/domains/<ctx>/` + `services/_shared/` (VO + клиенты интеграций) + паспорт `services/<svc>/README.md` (stable) | `/scaffold` domain → Go-код **по сервису**: паспорт задаёт границы деплой-юнита (Exposes / Dependencies / Resources / Messaging), домены — начинку; маппинг DDD → Go (включая `integration-client` → порт/адаптер) живёт у него (`docs/reference/domain-mapping.md`) |
| **`<org>/frontend`** (`spa-frontend-template`) | поверхности `web` рода `app`; `admin`, `desktop`, `embed`: `projects/<slug>/fsd/<surface>/` (stable-карта слайсов) + `screens/<surface>/` (экраны; карта `map.md` — маршруты, доступ, состояние в URL; реестр `texts.md` — ключи i18n) + `interface/<surface>/`, глоссарий объектов и словарь действий, `services/<svc>/domains/` — контекстом + `design/`: токены, проза и карта решений дизайн-системы («тип → компонент», расширения с клавиатурой, «роль текста → стиль», конвенции), бриф на вид (плотность, темы), продуктовый паспорт визуала, ассеты продукта (иконки, иллюстрации, шрифты) + `design/<surface>/`: адаптивные HTML-копии принятых экранов, `REVIEW.md`, манифест готовности `ready.yaml` | `/scaffold` и `/de-template` фронта разворачивают stable-записи FSD-карты в код (`src/`-пути выводят сами): тема и компоненты — по дизайн-системе, тексты — по ключам, состояния — по словарю экранов; бриф скилла `frontend-design` — из манифеста, цвета и шрифты — только из дизайн-системы проекта; карта проектируется здесь — `/fsd-deep-dive` (по фронтовой поверхности), облик — `/design-deep-dive` |
| **`<org>/site`** (`ssr-frontend-template`) | поверхности `web` рода `landing` и `site`: слой страницы `projects/<slug>/site/<surface>/` — бриф (языки, ограничения, платформа, аналитика, каналы заявок), карта (у рода `site`: шаблоны, `chrome`, коллекции, адреса, `build_order`), планы (секции, блоки и варианты каталога, слоты, `budget_profile`, `ambition_level`, `x-gate-exception`, SEO, право, события, формы, `treatment`), тексты по слотам (выбранные варианты, мета, OG, FAQ) + факты и голос продукта (`facts.yaml`, `voice*.yaml`) + `design/`: токены дизайн-системы с CSS-переменными, проза, карта решений, бренд и ассеты продукта + `design/<surface>/`: арт-дирекция, спецификации движения, ассеты с манифестом, адаптивные HTML-копии страниц, `REVIEW.md`, манифест готовности `ready.yaml` + получатели заявок — `integration.md`; каталоги блоков, форм, событий и `head` — из базы скилла соседним чекаутом (`../strategy/.claude/skills/design-deep-dive/kb/…`) | `/scaffold` и `/de-template` сайта собирают из закрытых файлов страницы и коллекции по плану и текстам: тема — из токенов, ассеты и движение — по манифесту и спецификациям; бриф скилла `frontend-design` — из манифеста (род поверхности, уровень амбиций, потолок движения), цвета и шрифты — только из дизайн-системы проекта; ворота после сборки — ниже; слой проектируется здесь — `/design-deep-dive` |
| **`<org>/<bot>`** (`telegram-bot-template`) | `projects/<slug>/telegram-bot-flow/<surface>/` (фичи: диалоги, окна, use-case'ы бота-оркестратора; пустой ответ `empty` у ключей getter'а и путь к человеку `escalate`) + `interface/<surface>/` + `services/<svc>/domains/` (доменные use-case'ы и события под оркестратор) + голос продукта (`voice*.yaml`) | проектирование и scaffold диалогов бота: StatesGroup, окна, виджеты, getter'ы, сервисы-оркестраторы, обработчики; тексты — одним голосом с вебом |
| **`<org>/mobile`** (`mobile-template`) | `projects/<slug>/mobile/<surface>/` (stable-карта приложения, 12 kind) + `interface/<surface>/` + `services/<svc>/domains/` (контекст ситуаций, сущностей и событий) + токены дизайн-системы продукта `design/` — значения темы (оболочка `shell`, «Theme & locale») + голос продукта (`voice*.yaml`) | `/scaffold` и `/de-template` мобильного репо разворачивают stable-записи карты в три места — `{shared,androidApp,iosApp}/` (пути выводят сами; маппинг kind → код — `<org>/mobile/docs/reference/strategy-mapping.md`); тема и тексты — одной дизайн-системой и одним голосом с вебом; карта проектируется здесь — `/mobile-deep-dive` (по мобильной поверхности) |
| **`<org>/infra`** (`project-infra-template-compose`) | скиллы хаба — `projects/<slug>/vision.md` и `surface.md` (род веб-поверхности `web-kind`: `landing` и `site` — код `<org>/site`, `app` — `<org>/frontend`); остальное — контекстом планирования: `services/{service,platform}.md`, секции `Resources`/`Messaging` паспортов, `projects/infrastructure/`, манифесты готовности поверхностей | `/init-project` (scope продукта → карта сервисов; род поверхности → какой код-репо поднимать), `/stack-deep-dive` (публичные поверхности → сабдомены и edge-роуты), `/de-template` (шапка `CLAUDE.md`/`README.md` под проект), `/smartdev` (sanity на старте сессии). Сервисную топологию и ИТ-периметр хаб читает как контекст, когда планирует работу (`/plan`, программы сквозных задач в `<org>/infra/.claude/plans/`): что билдить, где располагать, что провижинить; runtime-механика (реплики, размеры, манифесты) — решение infra |

Соседи держат `<org>/strategy` sibling-checkout'ом рядом (по умолчанию
`../strategy`; как переопределить путь — в обвязке соседа). Эти артефакты —
единственное, что docs производит для экосистемы; ничего обратно из них не
импортируется.

**Ворота после сборки.** Скорость, вес, доступность и поведение собранной страницы
код-репо проверяет утилитами скилла `design-deep-dive` из того же соседнего чекаута
(`../strategy/.claude/skills/design-deep-dive/scripts/…`) в окружении машины
`~/.cache/design-deep-dive/`, которое ставит `scripts/install.sh` скилла: одна копия
утилит и порогов, версия — коммит стратегии; результаты остаются в код-репо. Фаза
`build` — собранная страница: `page_anatomy.py` → `page_accept.py` → `page_gates.py` с
профилем бюджета плана и его исключениями `x-gate-exception`; `geo_probe.py`,
`ia_probe.py` (многостраничник), `run_axe_targets.py`, `claims_check.py` и
`lang_check.py` на собранном HTML, `motion_check.py`; у страниц с 3D — `site_probe.py`,
`gate_check.py`, `gltf_load_bench.py`, `web_view.py`; визуальный аудит —
`marketing_audit.py` или `ui_audit.py`; пункты `after_build` манифеста `ready.yaml`.
Фаза `live` — поле живой страницы (`page-gates.yaml#phases`). У кабинета лабораторных
порогов для экранов в базе нет: поле p75, RUM и сценарии реакции на собранном
приложении (канон дизайна, раздел «Пакет для кода»). В CI код-репо стратегия
клонируется рядом тем же путём, с доступом на чтение.

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
