# Domain Artifacts

DDD-first документация бизнес-домена бэкенда — опциональный слой проекта. Артефакты — **первичный source of truth** проектирования; код вторичен и генерируется/пишется по ним.

Этот файл — **канон формы** (`docs/projects/_canon/domains/`); шаблоны (`_templates/`) и форма-образец `_shared/README.md` живут здесь, один раз на все проекты. Данные доменов каждого проекта живут в его папке `docs/projects/<project-slug>/domains/`.

## Структура

Канон формы живёт один раз в `docs/projects/_canon/domains/`:

```
docs/projects/_canon/domains/
├── README.md                  ← этот файл
├── _templates/                ← пустые шаблоны для копирования
│   ├── aggregate.md
│   ├── entity.md              (опционально, для сложных child entities)
│   ├── vo-shared.md           (kind: vo — для _shared/, не для inline-VO внутри aggregate)
│   ├── event.md
│   ├── use-case.md
│   ├── policy.md
│   └── context-readme.md
└── _shared/
    └── README.md              ← форма-образец роллапа cross-context VO
```

Данные доменов живут в папке проекта `docs/projects/<project-slug>/domains/`:

```
docs/projects/<project-slug>/domains/
├── _shared/                   ← cross-context VO и integration events
│   ├── README.md              ← роллап: какие VO живут здесь и для кого
│   └── <Name>.md              ← kind: vo, платформенный VO (PhotoRef, MoneyAmount, …)
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

`_shared/` — заводим только когда VO реально нужен в ≥2 контекстах одного проекта и не несёт доменной семантики. Внутри-контекстные VO остаются inline в aggregate-файле.

## Kinds

| kind | назначение | где живёт |
|---|---|---|
| `aggregate` | бизнес-сущность с консистентной границей: root entity + inline-VO внутри | `<ctx>/<Name>.md` |
| `entity` | child entity сильной сложности (опционально) | `<ctx>/<Name>.md` |
| `event` | domain event для outbox | `<ctx>/events/<Name>.md` |
| `use-case` | бизнес-операция (orchestration) | `<ctx>/use-cases/<Name>.md` |
| `policy` | pure правило / authz / rate-limit | `<ctx>/policies/<Name>.md` |
| `vo` | cross-context платформенный VO (только для `_shared/`) | `_shared/<Name>.md` |

## Frontmatter (общий контракт)

```yaml
id: user.User                 # <context>.<Name>, стабильный кросс-реф
kind: aggregate               # aggregate|entity|vo|event|use-case|policy
context: user
name: User                    # human-readable
status: draft                 # draft → stable (через валидатор)
relations: [user.UserId, auth.Session]
emits: [user.UserRegistered]
consumes: [verification.EmailVerified]
```

## Обязательные секции по kind

См. валидатор `scripts/tools/validate-domain-doc.sh`. Кратко:

| kind | обязательные H2 |
|---|---|
| `aggregate` | Identity, Properties, Methods, Invariants, Lifecycle, Boundary, Contained Entities, Spanning Invariants, Value Objects, Events, Relations, Use Cases |
| `entity` | Identity, Properties, Methods, Invariants, Lifecycle, Relations |
| `event` | Trigger, Payload, Consumers, Delivery semantics |
| `use-case` | Actor, Inputs, Outputs, Dependencies, Steps, Called aggregate methods, Events emitted, Errors |
| `policy` | Kind of decision, Inputs, Rules, Outcomes, Used by |
| `vo` | Properties, Invariants, Constructor, Consumed by |

Контекст-`README.md`: Purpose, Aggregates, Use cases, Events, Cross-context dependencies, Ubiquitous Language.

Stateless / aggregate-of-one / пустые consumers — пишутся явной пометкой `N/A` или `_нет_`. Пустых таблиц быть не должно.

## Workflow

```
0. Шаблоны берём из канона docs/projects/_canon/domains/_templates/,
   копируем в папку доменов проекта (PROJECT=docs/projects/<project-slug>,
   TPL=docs/projects/_canon/domains/_templates).

1. Скопировать шаблоны:
     mkdir -p $PROJECT/domains/<ctx>/{events,use-cases,policies}
     cp $TPL/aggregate.md       $PROJECT/domains/<ctx>/<Aggregate>.md
     cp $TPL/event.md           $PROJECT/domains/<ctx>/events/<Event>.md
     cp $TPL/use-case.md        $PROJECT/domains/<ctx>/use-cases/<Op>.md
     cp $TPL/policy.md          $PROJECT/domains/<ctx>/policies/<Pol>.md
     cp $TPL/context-readme.md  $PROJECT/domains/<ctx>/README.md
   # Если обнаружен cross-context платформенный VO:
     cp $TPL/vo-shared.md       $PROJECT/domains/_shared/<Name>.md

2. Заполнить вручную минимум: frontmatter + properties (имена, типы)
   + methods/operations (имена). Принести Claude.

3. /domain-deep-dive <project-slug> <ctx>
   — пачкой по волнам, AskUserQuestion'ами добиваем секции inside-out.

4. scripts/tools/validate-domain-doc.sh $PROJECT/domains/<ctx>
   — зелёный → промоушн status: draft → stable.

5. /smartdev → /plan <task>
   — планировщик читает stable-артефакты, разносит работу по слоям.

6. scaffold (вариант domain/endpoint/event)
   — скаффолдит код по stable-артефактам.
```

## Gate

- **Pre-commit hook** (`scripts/git-hooks/pre-commit`) гонит валидатор на изменённых `docs/projects/*/domains/**.md`.
- **Soft-guidance** — Claude-хуков в шаблоне нет; `scaffold`/`domain-deep-dive` по дисциплине идут по stable-артефактам и не стартуют на `status: draft` / красном валидаторе.

## Anti-patterns

- ❌ Создавать отдельный файл для **внутри-контекстной** VO. Она живёт inline в aggregate-файле. (Исключение: cross-context платформенный VO — `_shared/<Name>.md` с `kind: vo`.)
- ❌ Описывать I/O-операции как методы агрегата. Если нужен репо/порт — это use-case.
- ❌ Spanning invariant между двумя aggregate'ами. Запрещено DDD.
- ❌ Cross-context relation типа `composition`. Только `reference` (по ID).
- ❌ Промоутить `status: stable` руками без зелёного валидатора.
- ❌ Класть в `_shared/` доменный VO (например `Phone`, `Email`). `_shared/` — только для платформенных типов без доменной семантики.
