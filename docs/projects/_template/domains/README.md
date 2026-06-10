# Артефакты доменов

DDD-first документация бизнес-домена бэкенда — опциональный слой проекта. Артефакты — **первичный source of truth** проектирования; код вторичен и генерируется/пишется по ним.

В отличие от `interface/` и `screens/`, домены партиционируются **по bounded-context, не по поверхности (surface)**: бэкенд surface-агностичен — одна доменная модель обслуживает все поверхности продукта. Поверхность входит в домен только через `Channel` use-case'а (`HTTP API …`) и через внешние/межпроектные интеграции (см. ниже).

Этот файл — **канон формы** (`docs/projects/_template/domains/`); шаблоны (`_templates/`) и форма-образец `_shared/README.md` живут здесь, один раз на все проекты. Данные доменов каждого проекта живут в его папке `docs/projects/<project-slug>/domains/`.

## Структура

Канон формы живёт один раз в `docs/projects/_template/domains/`:

```
docs/projects/_template/domains/
├── README.md                  ← этот файл
├── _templates/                ← пустые шаблоны для копирования
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

Данные доменов живут в папке проекта `docs/projects/<project-slug>/domains/`:

```
docs/projects/<project-slug>/domains/
├── _shared/                   ← cross-context VO + конкретные клиенты интеграций
│   ├── README.md              ← роллап: какие VO и клиенты живут здесь и для кого
│   ├── <Name>.md              ← kind: vo, платформенный VO (PhotoRef, MoneyAmount, …)
│   └── integrations/
│       └── <integration-slug>/
│           └── README.md      ← kind: integration-client, клиент внешней системы / соседа
└── <bounded-context>/
    ├── README.md              ← purpose, ubiquitous language (роллап на контекст)
    ├── <Aggregate>.md         ← kind: aggregate, root entity + inline-VO внутри
    ├── events/
    │   └── <Event>.md         ← kind: event
    ├── use-cases/
    │   └── <Operation>.md     ← kind: use-case
    └── policies/
        └── <PolicyName>.md    ← kind: policy
```

`_shared/` держит два рода платформенных артефактов: **cross-context VO**
(заводим только когда VO реально нужен в ≥2 контекстах одного проекта и не
несёт доменной семантики; внутри-контекстные VO остаются inline в
aggregate-файле) и **клиенты интеграций** (`integrations/<integration-slug>/`)
— конкретное воплощение интеграции, к которой обращаются домены: транспорт,
функции с `slug`, ошибки. Домен зовёт функцию клиента по `slug`, оставаясь
transport-agnostic; что это HTTP/gRPC/очередь — знает только клиент.

## Kinds

| kind | назначение | где живёт |
|---|---|---|
| `aggregate` | бизнес-сущность с консистентной границей: root entity + inline-VO внутри | `<ctx>/<Name>.md` |
| `entity` | child entity сильной сложности (опционально) | `<ctx>/<Name>.md` |
| `event` | domain event для outbox | `<ctx>/events/<Name>.md` |
| `use-case` | бизнес-операция (orchestration) | `<ctx>/use-cases/<Name>.md` |
| `policy` | pure правило / authz / rate-limit | `<ctx>/policies/<Name>.md` |
| `vo` | cross-context платформенный VO (только для `_shared/`) | `_shared/<Name>.md` |
| `integration-client` | конкретный клиент внешней системы / соседа: транспорт + функции с `slug` | `_shared/integrations/<integration-slug>/README.md` |

## Frontmatter (общий контракт)

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

## Обязательные секции по kind

Сверяются вручную по этой таблице (committed-скрипта-валидатора в репо нет;
дисциплину держит `/domain-deep-dive` по чек-листу `draft → stable`).
Программный валидатор формы — **в планах** (пересмотр — когда наберётся
достаточно доменов, чтобы ручная сверка стала узким местом); пока проверка
ручная по этой таблице и по `field-checklists.md` скилла `/domain-deep-dive`.

| kind | обязательные H2 |
|---|---|
| `aggregate` | Identity, Properties, Methods, Invariants, Lifecycle, Boundary, Contained Entities, Spanning Invariants, Value Objects, Events, Relations, Use Cases |
| `entity` | Identity, Properties, Methods, Invariants, Lifecycle, Relations |
| `event` | Trigger, Payload, Consumers, Delivery semantics |
| `use-case` | Actor, Inputs, Outputs, Dependencies, Steps, Called aggregate methods, Events emitted, Errors |
| `policy` | Kind of decision, Inputs, Rules, Outcomes, Used by |
| `vo` | Properties, Invariants, Constructor, Consumed by |
| `integration-client` | Transport, Functions, Errors |

Контекст-`README.md`: Purpose, Aggregates, Use cases, Events, Cross-context dependencies, Ubiquitous Language.

**Язык артефактов.** Имена H2-секций, заголовки колонок таблиц и поле-метки
(`Source`, `Constraints`, `preconditions`, `guard`, `Equality`, …) — на
английском: это структурные идентификаторы handoff-контракта, по ним
`<org>/backend` разворачивает Go-код (маппинг — его
`docs/reference/domain-mapping.md`). Вся проза — описания, бизнес-значения,
пояснения, примеры — по-русски.

Stateless / aggregate-of-one / пустые consumers — пишутся явной пометкой `N/A` или `_нет_`. Пустых таблиц быть не должно.

## Внешние и межпроектные интеграции

Каждый выход кода наружу поднимается до явной записи в продуктовом слое
`docs/projects/<project-slug>/integration.md` (провайдер + его функции) и
получает **конкретный клиент** в `_shared/integrations/<integration-slug>/`.
Домен остаётся **transport-agnostic**: в `## Dependencies` use-case объявляет,
**какие функции** интеграции дёргает (по `slug`), а как именно (HTTP / gRPC /
очередь / SDK) — дело клиента.

В `## Dependencies` use-case колонка `integration`:

- **внутренняя инфра** (репозиторий, `Clock`, reader другого контекста
  **этого** проекта) — `integration` = `—`, функции не нужны;
- **внешняя система** (платёж, email, SMS, IDP, webhook) — `integration` =
  slug провайдера в `integration.md` с `target: external`; use-case
  перечисляет потребляемые функции `` [`<integration>.<fn-slug>`] ``, их
  конкретика — в клиенте `_shared/integrations/<integration>/`;
- **соседний проект бизнеса** — `integration` = slug провайдера с
  `target: sibling-project` (+ `sibling-project` → slug проекта). Outbound —
  функции клиента к соседу; inbound (сосед зовёт нас) — use-case с
  соответствующим `Actor`. Ребро стыка сводится в
  [`../../project-map.md`](../../project-map.md) на бизнес-языке.

`/cross-audit` сверяет цепочку: потребляемая функция в use-case ↔ функция
клиента `_shared/` ↔ строка `## Функции` в `integration.md` ↔ (для соседа)
ребро `project-map.md` и обслуживающий use-case у соседа. Внутри-проектные
связи (между контекстами) остаются `relations` / `emits` / `consumes` —
они **не** интеграции и в `integration.md` не попадают.

## Workflow

```
0. Шаблоны берём из канона docs/projects/_template/domains/_templates/,
   копируем в папку доменов проекта (PROJECT=docs/projects/<project-slug>,
   TPL=docs/projects/_template/domains/_templates).

1. Скопировать шаблоны:
     mkdir -p $PROJECT/domains/<ctx>/{events,use-cases,policies}
     cp $TPL/aggregate.md       $PROJECT/domains/<ctx>/<Aggregate>.md
     cp $TPL/event.md           $PROJECT/domains/<ctx>/events/<Event>.md
     cp $TPL/use-case.md        $PROJECT/domains/<ctx>/use-cases/<Op>.md
     cp $TPL/policy.md          $PROJECT/domains/<ctx>/policies/<Pol>.md
     cp $TPL/context-readme.md  $PROJECT/domains/<ctx>/README.md
   # Если обнаружен cross-context платформенный VO:
     cp $TPL/vo-shared.md       $PROJECT/domains/_shared/<Name>.md
   # Если домен обращается к внешней системе / соседу — клиент интеграции:
     mkdir -p $PROJECT/domains/_shared/integrations/<integration-slug>
     cp $TPL/integration-client.md \
        $PROJECT/domains/_shared/integrations/<integration-slug>/README.md

2. Заполнить вручную минимум: frontmatter + properties (имена, типы)
   + methods/operations (имена). Принести Claude.

3. /domain-deep-dive <project-slug> <ctx>
   — пачкой по волнам, AskUserQuestion'ами добиваем секции inside-out.

4. Ручная сверка формы по чек-листу draft → stable
   — frontmatter, обязательные H2, ref-целостность; всё держится →
     промоушн status: draft → stable.
```

После `stable` артефакты потребляет соседний backend-репо (`<org>/backend`,
форк `go-backend-template`) — его `/scaffold` (вариант domain) разворачивает
Go-код по ним. Это шаг **в том репо**, не в этом design-time SoT.

## Gate

Committed-скрипта-валидатора и git-хуков в этом репо нет (markdown-only
design-SoT). Промоушн `draft → stable` — **ручной review** по дисциплине:
`/domain-deep-dive` сверяет форму по чек-листу `references/draft-stable.md`
(frontmatter, обязательные H2, ref-целостность, тест-критерий kind'а) и
повышает `status` только с явного подтверждения архитектора. Точечные правки
уже-stable артефакта — прямым `Edit`.

## Anti-patterns

- ❌ Создавать отдельный файл для **внутри-контекстной** VO. Она живёт inline в aggregate-файле. (Исключение: cross-context платформенный VO — `_shared/<Name>.md` с `kind: vo`.)
- ❌ Описывать I/O-операции как методы агрегата. Если нужен репо/порт — это use-case.
- ❌ Spanning invariant между двумя aggregate'ами. Запрещено DDD.
- ❌ Cross-context relation типа `composition`. Только `reference` (по ID).
- ❌ Промоутить `status: stable` в обход чек-листа `draft → stable` (форма не сверена).
- ❌ Класть в `_shared/` доменный VO (например `Phone`, `Email`). `_shared/` — только для платформенных типов без доменной семантики.
- ❌ Транспорт интеграции (HTTP-метод, endpoint, gRPC, очередь) в use-case или aggregate. Домен дёргает функцию по `slug`; транспорт живёт в клиенте `_shared/integrations/<slug>/`.
- ❌ Клиент интеграции в `<ctx>/` вместо `_shared/integrations/`. Клиент платформенный и общий между контекстами; в доменном контексте — только потребление функций.
- ❌ Сигнатура/endpoint функции в продуктовом `integration.md`. Там бизнес-описание функции; конкретика — в клиенте `_shared/`.
