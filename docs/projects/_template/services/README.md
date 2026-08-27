# Артефакты сервисов

Смысловое проектирование бэкенда продукта — слой проекта, обязательный для
любого продукта с бэкендом: из каких **сервисов** состоит приложение, какими
доменами (bounded context) каждый владеет, чем сервисы обмениваются
(sync-вызовы и события через брокер), какие ресурсы им нужны («потребность +
технология») и какое платформенное общее их связывает. Артефакты — **первичный
source of truth** проектирования; код вторичен и генерируется/пишется по ним.

Слой **deployment-agnostic**: одна и та же топология материализуется и в
kubernetes, и в compose на сплит-серверах — поэтому здесь нет runtime-механики
(реплик, размеров, портов, манифестов). Где сервисы физически живут, решает
ИТ-периметр бизнеса (`docs/projects/infrastructure/`, реестр `placement.md`),
а runtime-механику — инфра-репо `<org>/infra`.

**Монолит — частный случай**: один сервис `type: api` с несколькими доменами
внутри. «Нет сервисов» не бывает, если есть бэкенд; вырасти из монолита в
микросервисы = добавить папки сервисов и перенести домены.

Ось партиционирования бэкенда — **сервис** (как surface для фронта): реестр
`service.md` объявляет сервисы, каждый получает папку
`services/<service-slug>/` с паспортом и (для доменных сервисов) папкой
`domains/<ctx>/`. Домены партиционируются по bounded-context **внутри
сервиса** и остаются **surface-агностичны**: одна доменная модель обслуживает
все поверхности продукта.

Этот файл — **канон формы** (`docs/projects/_template/services/`); формы
реестров (`service.md` · `platform.md` · `architecture.md`), шаблоны
(`_templates/`) и форма-образец `_shared/README.md` живут здесь, один раз на
все проекты. Данные каждого проекта живут в его папке
`docs/projects/<project-slug>/services/`.

## Структура

Канон формы живёт один раз в `docs/projects/_template/services/`:

```
docs/projects/_template/services/
├── README.md                  ← этот файл
├── service.md                 ← форма реестра-хребта сервисов
├── platform.md                ← форма реестра платформенных ресурсов проекта
├── architecture.md            ← форма singleton'а топологии
├── _templates/                ← пустые шаблоны для копирования
│   ├── service-readme.md      (паспорт сервиса)
│   ├── worker.md              (kind: worker — фоновый воркер сервиса)
│   ├── aggregate.md
│   ├── entity.md              (опционально, для сложных child entities)
│   ├── vo-shared.md           (kind: vo — для _shared/, не для inline-VO внутри aggregate)
│   ├── event.md
│   ├── use-case.md
│   ├── policy.md
│   ├── integration-client.md  (kind: integration-client — клиент внешней системы в _shared/)
│   └── context-readme.md
└── _shared/
    └── README.md              ← форма-образец роллапа cross-context VO и клиентов интеграций
```

Данные слоя живут в папке проекта `docs/projects/<project-slug>/services/`:

```
docs/projects/<project-slug>/services/
├── service.md                 ← реестр-хребет: объявляет сервисы
├── platform.md                ← платформенные ресурсы проекта (брокер, api-gateway, CDN, …)
├── architecture.md            ← singleton: свод топологии + авторские решения разбиения
├── _shared/                   ← общее между сервисами: cross-context VO + клиенты интеграций
│   ├── README.md              ← роллап: какие VO и клиенты живут здесь и для кого
│   ├── <Name>.md              ← kind: vo, платформенный VO (PhotoRef, MoneyAmount, …)
│   └── integrations/
│       └── <integration-slug>/
│           └── README.md      ← kind: integration-client, клиент внешней системы / соседа
└── <service-slug>/            ← по папке на сервис из реестра
    ├── README.md              ← паспорт сервиса (kind: service-passport)
    ├── workers/               ← фоновые воркеры сервиса (если есть)
    │   └── <worker-slug>.md   ← kind: worker (Trigger · Handles · Semantics · On failure)
    └── domains/               ← только у доменных сервисов (type: api | worker)
        └── <bounded-context>/
            ├── README.md      ← purpose, ubiquitous language (роллап на контекст)
            ├── <Aggregate>.md ← kind: aggregate, root entity + inline-VO внутри
            ├── events/
            │   └── <Event>.md ← kind: event
            ├── use-cases/
            │   └── <Operation>.md ← kind: use-case
            └── policies/
                └── <PolicyName>.md ← kind: policy
```

## Инварианты слоя

1. **Минимум один сервис.** Монолит = один `api`-сервис с несколькими
   контекстами — валидная топология, не упрощение.
2. **Контекст живёт ровно в одном сервисе; слаги контекстов уникальны в
   пределах проекта** (сквозь все сервисы). Поэтому id доменных артефактов
   (`<context>.<Name>`) и рефы `use-case:<ctx>.<Operation>` /
   `event:<ctx>.<Event>` (telegram-bot-flow, межслойные связи)
   **сервисо-агностичны** — сервис-владелец однозначно выводится из пути
   `services/*/domains/<ctx>/`. Слаг контекста — kebab-case, как все слаги
   репозитория; маппинг в имена пакетов кода — забота код-репо.
3. **Ресурс принадлежит ровно одному сервису** (его таблица `Resources`).
   Shared database между сервисами запрещён; данные соседа — только через его
   `Exposes`-функции (sync) или события (async).
4. **Каждое потребляемое событие имеет продюсера**: строка `consumes` в
   `Messaging` одного сервиса обязана иметь парную `produces` (тот же
   `broker` + `topic` + `event`) у сервиса-владельца контекста события.
5. **Одна транзакция — один агрегат.** Use-case в одной транзакции создаёт
   или мутирует не более одного агрегата (плюс outbox-запись его событий);
   согласованность между агрегатами — eventual: событие + policy / воркер /
   consumer. Осознанное исключение обосновывается явно в
   `## Side effects beyond the aggregate` use-case'а — молчаливых двойных
   мутаций не бывает.
6. **Deployment-agnostic.** Размещение по серверам/рантаймам — в
   `docs/projects/infrastructure/placement.md`, паспорта его не дублируют.

## Kinds

| kind | назначение | где живёт |
|---|---|---|
| строка реестра сервисов | объявление сервиса: тип, поверхности | `service.md` |
| `service-passport` | паспорт одного сервиса: Exposes · Owned Contexts · Dependencies · Resources · Messaging · Workers | `<svc>/README.md` |
| `worker` | фоновый воркер сервиса: триггер, оркестрация доменных use-case'ов, семантика потребления | `<svc>/workers/<slug>.md` |
| строка реестра платформы | платформенный ресурс проекта: брокер, api-gateway, CDN, object storage | `platform.md` |
| `architecture` (singleton) | свод топологии + авторские решения разбиения | `architecture.md` |
| `aggregate` | бизнес-сущность с консистентной границей: root entity + inline-VO внутри | `<svc>/domains/<ctx>/<Name>.md` |
| `entity` | child entity сильной сложности (опционально) | `<svc>/domains/<ctx>/<Name>.md` |
| `event` | domain event для outbox | `<svc>/domains/<ctx>/events/<Name>.md` |
| `use-case` | бизнес-операция (orchestration) | `<svc>/domains/<ctx>/use-cases/<Name>.md` |
| `policy` | pure правило / authz / rate-limit | `<svc>/domains/<ctx>/policies/<Name>.md` |
| `vo` | cross-context платформенный VO (только для `_shared/`) | `_shared/<Name>.md` |
| `integration-client` | конкретный клиент внешней системы / соседа: транспорт + функции с `slug` | `_shared/integrations/<integration-slug>/README.md` |

Формы реестров и singleton'а (критерии, «Что НЕ», тест-критерии, колонки,
пустые таблицы) — в файлах `service.md`, `platform.md`, `architecture.md`
этого канона; при заведении слоя они копируются в проект целиком.

## Frontmatter (доменные артефакты)

Доменные артефакты несут frontmatter — как и прежде, **без поля сервиса**
(сервис выводится из пути; дубль породил бы рассинхрон при переносе контекста):

```yaml
id: user.User                 # <context>.<Name>, стабильный кросс-реф
kind: aggregate               # aggregate|entity|vo|event|use-case|policy
context: user
name: User                    # человекочитаемое имя
status: draft                 # draft → stable (ручная сверка формы)
relations: [user.UserId, auth.Session]
emits: [user.UserRegistered]
consumes: [verification.EmailVerified]
```

Реестры, паспорт сервиса и `architecture.md` — **без frontmatter** (kind
определяется именем файла / позицией, как у продуктовых kind).

## Обязательные секции по kind

Сверяются вручную по этой таблице; дисциплину держат `/service-deep-dive`
(сервисный уровень) и `/domain-deep-dive` (доменный) по чек-листам
`draft → stable`.

| kind | обязательные H2 |
|---|---|
| `service-passport` | Purpose, Exposes, Owned Contexts, Dependencies, Resources, Messaging, Workers, Fronts, Notes |
| `worker` | Trigger, Handles, Semantics, On failure, Notes |
| `aggregate` | Identity, Properties, Methods, Invariants, Lifecycle, Boundary, Contained Entities, Spanning Invariants, Value Objects, Events, Relations, Use Cases |
| `entity` | Identity, Properties, Methods, Invariants, Lifecycle, Relations |
| `event` | Trigger, Payload, Consumers, Delivery semantics |
| `use-case` | Actor, Inputs, Outputs, Dependencies, Steps, Called aggregate methods, Events emitted, Errors |
| `policy` | Kind of decision, Inputs, Rules, Outcomes, Used by |
| `vo` | Properties, Invariants, Constructor, Consumed by |
| `integration-client` | Transport, Functions, Errors |

Контекст-`README.md`: Purpose, Aggregates, Use cases, Events, Cross-context
dependencies, Ubiquitous Language.

**Язык артефактов.** Имена H2-секций, заголовки колонок таблиц, enum-значения
и поле-метки (`Source`, `Constraints`, `preconditions`, `guard`, `Equality`,
…) — на английском: это структурные идентификаторы handoff-контракта, по ним
`<org>/backend` разворачивает Go-код (маппинг — его
`docs/reference/domain-mapping.md`), а `<org>/infra` читает топологию. Вся
проза — описания, бизнес-значения, пояснения, примеры — по-русски.

Примеры адаптеров и пакетов в шаблонах `_templates/` (pgx/sqlc,
`golibinfra`, `outboxkit`, `authgate` и т.п.) — иллюстрации целевого стека
по умолчанию, не часть контракта: слой остаётся язык-агностичным, выбор
технологий — за `platform.md` и архитектором.

Stateless / aggregate-of-one / пустые consumers — пишутся явной пометкой
`N/A` или `_нет_`. Пустых таблиц быть не должно.

**Use-case'ы чтения.** Запись (мутация) — всегда отдельный use-case-файл.
Чтение (`Get<Name>`, `List<Name>s`) получает файл, только когда несёт
бизнес-правила (видимость по ролям, доменная агрегация, платная выдача);
тривиальная выборка либо не документируется вовсе, либо остаётся строкой
**без ссылки** в `README.md § Use cases` контекста — код-репо скаффолдит её
без отдельного артефакта. Это защита от двух крайностей: церемонии вокруг
голого SELECT и бизнес-правила чтения, потерянного в коде.

## Связи: sync, async, платформа

**Sync сервис → сервис** — три высоты с общим `slug`, по аналогии с внешними
интеграциями, но внутри слоя:

1. **сервисный уровень** (авторская сторона ребра): строка
   `` `service:<slug>` `` в `## Dependencies` паспорта потребителя;
2. **каталог**: функция в `## Exposes` паспорта провайдера
   (`backed-by: use-case:<ctx>.<Operation>`);
3. **доменный уровень** (потребление): в `## Dependencies` use-case'а колонка
   `integration` принимает `` `service:<svc-slug>` ``, а `functions` — функции
   из `Exposes` провайдера записями `<svc-slug>.<fn-slug>`.

**In-process reader чужого контекста возможен только в пределах одного
сервиса.** Контекст другого сервиса достижим только как `service:`-порт
(sync) или через события (async). Сервисы этого проекта друг для друга —
**не интеграции**: в `integration.md` они не попадают (он — для внешних
систем и соседних проектов).

**Воркеры внутри сервиса**: фоновые процессы того же деплой-юнита
(консьюмер топика, периодическая задача). Критерий: общий код/данные и
деплой вместе — воркер сервиса; отдельный деплой-юнит, живущий только на
событиях/расписании, — сервис `type: worker`. Реестр — таблица `## Workers`
паспорта, полное описание — файл `workers/<slug>.md` (kind `worker`):
`Trigger` (topic — с парной строкой `consumes` в `Messaging`; расписание —
смыслом, cron — runtime), `Handles` (какие **доменные use-case'ы** дёргает,
M:N — воркер оркестрирует, бизнес-правил не держит, как use-case бота),
`Semantics` (идемпотентность · retry → DLQ · ordering · батчинг —
стратегиями, без чисел: транспортная механика живёт здесь, не в
transport-agnostic домене), `On failure` (судьба сообщения + сигнал людям).
Воркеры размещаются вместе со своим сервисом — отдельной строки
`placement` им не нужно.

**Async через брокер**: событие остаётся доменным артефактом
(transport-agnostic, outbox; домен топиков не знает). Привязка
«событие → topic → брокер» живёт **только** в `## Messaging` паспортов;
брокер — запись `platform.md` (`type: message-broker`), а `topic` — сквозной
идентификатор: пара `(broker, topic)` у консьюмера обязана существовать у
продюсера с тем же `event:<ctx>.<Event>`.

**Платформа**: сервис объявляет нужду в платформенном ресурсе строкой
`` `platform:<slug>` `` в `Dependencies` (или `broker` в `Messaging`);
ресурс, который не требует ни один паспорт, — сирота (находка аудита).
Колонка `provided-by` в `platform.md` говорит, свой это ресурс проекта
(`own`) или общий ресурс бизнеса (`` `shared:<slug>` `` → запись в
`docs/projects/infrastructure/shared-platform.md`).

## Внешние и межпроектные интеграции

Каждый выход кода наружу поднимается до явной записи в продуктовом слое
`docs/projects/<project-slug>/integration.md` (провайдер + его функции) и
получает **конкретный клиент** в `_shared/integrations/<integration-slug>/`.
Домен остаётся **transport-agnostic**: в `## Dependencies` use-case объявляет,
**какие функции** интеграции дёргает (по `slug`), а как именно (HTTP / gRPC /
очередь / SDK) — дело клиента. Формат записи в колонке `functions` —
`<integration>.<fn-slug>` (слаг провайдера точкой перед слагом функции; для
порта к сервису проекта — `<svc-slug>.<fn-slug>`): однозначен при нескольких
интеграциях у одного use-case'а.

В `## Dependencies` use-case колонка `integration`:

- **внутренняя инфра того же сервиса** (репозиторий, `Clock`, in-process
  reader другого контекста **этого** сервиса) — `integration` = `—`;
- **другой сервис этого проекта** — `integration` =
  `` `service:<svc-slug>` ``; функции — из `Exposes` провайдера;
- **внешняя система** (платёж, email, SMS, IDP, webhook) — `integration` =
  slug провайдера в `integration.md` с `target: external`; конкретика — в
  клиенте `_shared/integrations/<integration>/`;
- **соседний проект бизнеса** — `integration` = slug провайдера с
  `target: sibling-project` (+ `sibling-project` → slug проекта). Ребро стыка
  сводится в [`../../project-map.md`](../../project-map.md) на бизнес-языке.

Клиент интеграции может «хоститься» gateway-сервисом: поле `fronted-by` в его
frontmatter (`` service:<svc-slug> `` | `—`). При наличии gateway остальные
сервисы к интеграции напрямую не ходят — зовут функции gateway из его
`Exposes`.

`/cross-audit` сверяет цепочку: потребляемая функция в use-case ↔ функция
клиента `_shared/` ↔ строка `## Функции` в `integration.md` ↔ (для соседа)
ребро `project-map.md` и обслуживающий use-case у соседа. Внутри-сервисные
связи между контекстами остаются `relations` / `emits` / `consumes`.

## Сводимость в C4

Слой спроектирован так, что C4-модель выводится из артефактов без догадок
(генерация — отдельным промптом, когда понадобится):

| высота C4 | откуда выводится |
|---|---|
| L1 System Context | `vision` + `user` + `integration.md` (`target: external`) + `project-map.md` |
| L2 Containers | `service.md` + паспорта (Exposes/Dependencies/Messaging/Resources) + `platform.md` + `infrastructure/shared-platform.md` |
| L3 Components | `services/<svc>/domains/<ctx>/` (контексты, агрегаты, use-case'ы, события) |
| Deployment | `infrastructure/{server,runtime,placement}.md` |

Это держится на двух правилах: каждое ребро авторски записано ровно в одном
месте (surfaces — `service.md`; sync — `Dependencies`; async — `Messaging`;
внешнее — `integration.md`; размещение — `placement.md`), и все рёбра —
типизированные slug-рефы, не свободный текст. Полноту картины (недоборы)
держат coverage-углы аудитов, отсутствие лишнего (переборы) —
anti-pattern-правила.

## Workflow

```
0. Формы и шаблоны берём из канона (PROJECT=docs/projects/<project-slug>,
   TPL=docs/projects/_template/services).

1. Завести слой (один раз на проект):
     mkdir -p $PROJECT/services
     cp $TPL/service.md      $PROJECT/services/service.md
     cp $TPL/platform.md     $PROJECT/services/platform.md
     cp $TPL/architecture.md $PROJECT/services/architecture.md

2. Завести сервис: строка в service.md →
     mkdir -p $PROJECT/services/<svc>
     cp $TPL/_templates/service-readme.md $PROJECT/services/<svc>/README.md

3. Завести воркер сервиса: строка в `## Workers` паспорта →
     mkdir -p $PROJECT/services/<svc>/workers
     cp $TPL/_templates/worker.md $PROJECT/services/<svc>/workers/<slug>.md

4. Завести контекст внутри сервиса:
     mkdir -p $PROJECT/services/<svc>/domains/<ctx>/{events,use-cases,policies}
     cp $TPL/_templates/aggregate.md       $PROJECT/services/<svc>/domains/<ctx>/<Aggregate>.md
     cp $TPL/_templates/event.md           $PROJECT/services/<svc>/domains/<ctx>/events/<Event>.md
     cp $TPL/_templates/use-case.md        $PROJECT/services/<svc>/domains/<ctx>/use-cases/<Op>.md
     cp $TPL/_templates/policy.md          $PROJECT/services/<svc>/domains/<ctx>/policies/<Pol>.md
     cp $TPL/_templates/context-readme.md  $PROJECT/services/<svc>/domains/<ctx>/README.md
   # Если обнаружен cross-context платформенный VO:
     cp $TPL/_templates/vo-shared.md       $PROJECT/services/_shared/<Name>.md
   # Если домен обращается к внешней системе / соседу — клиент интеграции:
     mkdir -p $PROJECT/services/_shared/integrations/<integration-slug>
     cp $TPL/_templates/integration-client.md \
        $PROJECT/services/_shared/integrations/<integration-slug>/README.md

5. /service-deep-dive <project-slug>
   — сервисный уровень: реестр, паспорта, воркеры, платформа, разбиение,
     топология.

6. /domain-deep-dive <project-slug> <ctx>
   — доменный уровень: пачкой по волнам, AskUserQuestion'ами добиваем секции.

7. Ручная сверка формы по чек-листам draft → stable
   — frontmatter, обязательные H2, ref-целостность, инварианты слоя →
     промоушн status: draft → stable.
```

После `stable` артефакты потребляют соседи: `<org>/backend` (форк
`go-backend-template`) разворачивает Go-код по паспорту и доменам сервиса;
`<org>/infra` читает реестры и секции Resources/Messaging, чтобы знать, что
билдить и провижинить. Это шаги **в тех репо**, не в этом design-time SoT.

## Gate

Committed-скрипта-валидатора и git-хуков в этом репо нет (markdown-only
design-SoT). Промоушн `draft → stable` — **ручной review** по дисциплине:
`/service-deep-dive` сверяет сервисный уровень (паспорта, реестры, инварианты
слоя — уникальность контекстов, владелец ресурса, парность
produces/consumes, соответствие папок реестру), `/domain-deep-dive` —
доменные артефакты по чек-листу `references/draft-stable.md`. Повышение
`status` — только с явного подтверждения архитектора. Точечные правки
уже-stable артефакта — прямым `Edit`. Узкий аудит слоя —
`/service-audit <project-slug>`.

## Anti-patterns

- ❌ **Распределённый монолит.** Sync-цепочка `service → service → service`
  в одном пользовательском сценарии. Default межсервисного обмена — событие
  через брокер; sync — осознанное решение, обоснованное в
  `architecture.md § Decisions`.
- ❌ **Shared database.** Один ресурс в `Resources` двух сервисов или чтение
  чужих таблиц. Данные соседа — через его `Exposes` или события.
- ❌ **Бизнес-логика в gateway / edge / bot-сервисе.** Gateway нормализует и
  маппит, edge агрегирует, bot оркестрирует; правила — в доменах
  `api`/`worker`-сервисов. Папка `domains/` у сервиса типов
  `gateway`/`edge`/`bot` — находка аудита.
- ❌ **Событие без продюсера.** `consumes` без парного `produces` (тот же
  `broker` + `topic` + `event`) у владельца контекста события.
- ❌ **Контекст, размазанный по двум сервисам.** Один bounded context — ровно
  один сервис. Нужен «кусок» чужого контекста — это `Exposes`-функция или
  событие, не вторая папка.
- ❌ **Runtime-механика в паспорте.** Реплики, CPU/RAM, порты, helm-values,
  env-переменные, имена docker-образов. Слой говорит «нужен postgres под
  заказы», а не «postgres 16, 2 vCPU». Размещение — в
  `infrastructure/placement.md`.
- ❌ **Входной api-gateway как сервис.** Трафик-роутер — запись `platform.md`;
  сервисом он становится, только когда в нём появляется наш проектируемый код
  (тогда это `edge`).
- ❌ **Внутренний сервис в `integration.md`.** Сервисы одного проекта друг
  для друга — не интеграции; их связи — `Dependencies`/`Exposes`/`Messaging`.
- ❌ **Микросервис на каждый контекст «по привычке».** Разбиение — решение со
  смыслом (`architecture.md § Decisions`); монолит из одного `api`-сервиса с
  пятью контекстами — валидная топология.
- ❌ **Топология, авторенная в `architecture.md`.** Диаграмма — свод; ребро,
  которого нет в паспортах/реестрах, не существует.
- ❌ **Transport-детали в `Exposes` / сигнатуры в паспорте.** `Exposes` —
  бизнес-каталог функций; протоколы и endpoint'ы — материализация кода
  (`<org>/backend`) и клиент `_shared/integrations/`.
- ❌ Создавать отдельный файл для **внутри-контекстной** VO. Она живёт inline
  в aggregate-файле. (Исключение: cross-context платформенный VO —
  `_shared/<Name>.md` с `kind: vo`.)
- ❌ Описывать I/O-операции как методы агрегата. Если нужен репо/порт — это
  use-case.
- ❌ **Мутация двух агрегатов в одной транзакции use-case'а.** Инвариант
  слоя: одна транзакция — один агрегат; второй меняется eventual — через
  событие + policy/воркер. Исключение — только явно обоснованное в
  `## Side effects beyond the aggregate`.
- ❌ **Status-поле без Lifecycle.** Property-enum статуса в `Properties`
  при `Lifecycle: N/A` — маркер недопроектированного жизненного цикла:
  либо таблица переходов покрывает все значения enum, либо статус не enum.
- ❌ Spanning invariant между двумя aggregate'ами. Запрещено DDD.
- ❌ Cross-context relation типа `composition`. Только `reference` (по ID).
- ❌ Промоутить `status: stable` в обход чек-листов `draft → stable`.
- ❌ Класть в `_shared/` доменный VO (например `Phone`, `Email`). `_shared/` —
  только для платформенных типов без доменной семантики.
- ❌ Транспорт интеграции (HTTP-метод, endpoint, gRPC, очередь) в use-case
  или aggregate. Домен дёргает функцию по `slug`; транспорт живёт в клиенте
  `_shared/integrations/<slug>/`.
- ❌ Клиент интеграции в папке сервиса вместо `_shared/integrations/`. Клиент
  платформенный и общий; «хостинг» gateway-сервисом — поле `fronted-by`.
- ❌ Сигнатура/endpoint функции в продуктовом `integration.md`. Там
  бизнес-описание функции; конкретика — в клиенте `_shared/`.
