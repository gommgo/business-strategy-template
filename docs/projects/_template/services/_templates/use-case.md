---
id: <context>.<Operation>
kind: use-case
context: <context>
name: <Operation>
status: draft
relations: [<context>.<Aggregate>]
emits: []
consumes: []
---

# <Operation>

> Одна фраза, описывающая бизнес-операцию. Что хочет сделать актор.

## Actor

- **Role:** anonymous | admin | client | system
- **Channel:** HTTP API (`<METHOD> <path>`) | NATS subscriber | scheduled job | internal

## Inputs

| field | type | required | description |
|---|---|---|---|
| `<Field>` | <type> | yes | <смысл> |

## Outputs

- **On success:** `<Aggregate>DTO` (или void для DELETE-операций)
- **On failure:** см. Errors

## Dependencies

Колонка `integration` говорит, чей это порт: для внутренней инфры
(репозиторий, `Clock`, in-process reader другого контекста **этого же
сервиса**) — `—`; для **другого сервиса этого проекта** —
`` `service:<svc-slug>` `` (его функции — из `## Exposes` паспорта
провайдера); для **внешних** интеграций (платёж, email, SMS, IDP) и
**межпроектных** портов (обмен с соседним проектом бизнеса) — slug
провайдера из продуктового `integration.md`. Колонка `functions` — **какие
функции** этот use-case дёргает, записями `<integration>.<fn-slug>` (слаг
провайдера — сервиса или интеграции — точкой перед слагом функции из
`Exposes` сервиса / `## Функции` `integration.md` / клиента `_shared/`;
формат однозначен при нескольких провайдерах в одной таблице); для
внутренней инфры — `—`. Домен **transport-agnostic**: он зовёт функцию по `slug`, а как именно
(HTTP / gRPC / очередь) — знает только клиент `_shared/integrations/<slug>/`
или код сервиса-провайдера. Контекст **другого сервиса** in-process
недостижим — только `service:`-порт или событие.

| port | purpose | adapter | integration | functions |
|---|---|---|---|---|
| `<Aggregate>Repository` | хранение корневого агрегата | postgres (pgx + sqlc) | `—` | `—` |
| `Clock` | детерминированное время | `golibinfra/clock` | `—` | `—` |
| `<OtherDomain>Reader` | кросс-контекстный порт — данные из другого контекста **этого же сервиса** | адаптер в `module/adapters.go` чужого домена | `—` | `—` |
| `<OtherService>Client` | другой сервис этого проекта — зовём его функции из `Exposes` | код сервиса-провайдера | `` `service:<svc-slug>` `` | `` [`<svc-slug>.<fn-slug>`, …] `` |
| `<ExternalService>` | внешняя система — зовём по функциям, транспорт не знаем | клиент `_shared/integrations/<integration-slug>/` | `` `<integration-slug>` `` | `` [`<integration-slug>.<fn-slug>`, …] `` |
| `<SiblingProject>Client` | обмен с **соседним проектом** бизнеса | клиент `_shared/integrations/<integration-slug>/` | `` `<integration-slug>` `` (`target: sibling-project`) | `` [`<integration-slug>.<fn-slug>`, …] `` |

> **Внешние и межпроектные интеграции** держим явно: каждый порт с
> непустой колонкой `integration` ссылается на провайдера в `integration.md`,
> а его `functions` — на строки `## Функции` того провайдера и на функции
> клиента `_shared/integrations/<slug>/`. Межпроектный порт — провайдер с
> `target: sibling-project`; ребро попадает в `docs/projects/project-map.md`
> (на бизнес-языке). `/cross-audit` сверяет цепочку: `functions` здесь ↔ функция
> клиента `_shared/` ↔ строка `## Функции` `integration.md` ↔ (для соседа)
> ребро `project-map.md` и обслуживающий use-case у соседа. Порт
> `service:<svc-slug>` сверяется со строкой `Dependencies` паспорта
> **этого** сервиса и функцией `Exposes` провайдера. Синхронные вызовы
> видны в `## Steps` отдельным шагом; асинхронный обмен — через события
> (`## Events emitted` / `consumes`) и `## Messaging` паспортов.

> **Авторизация** — на уровне HTTP-middleware (`platform/authgate`), не в use-case'е. Use-case не имеет `Authorizer`-порта и не возвращает `ErrForbidden`, если репо-конвенция «есть валидная сессия → can do everything». Если в конкретном домене нужны fine-grained роли — заводи policy в `<ctx>/policies/` и **явно** добавь её здесь.

## Steps

> Нумерованный список шагов. Каждый — observable действие (Validate / Load / Construct / Apply / Persist / Emit / Return).
> Шаг с I/O называет порт из `## Dependencies` (`repo.…`, `<Client>.…`); порт, не появившийся ни в одном шаге, — сирота. Транзакция одна и мутирует **один** агрегат (инвариант слоя); вторая мутация — отдельный use-case, запущенный событием.

1. **Validate inputs:** базовая валидация формата (детальная — в VO-конструкторах)
2. **Load:** `repo.GetByID(ctx, id)` → `ErrNotFound` если нет (для Update/Delete; не нужно для Create)
3. **Construct aggregate / Apply method:** `<Aggregate>.New<Name>(...)` или `agg.<Mutator>(...)`
4. **Persist:** `repo.Insert(ctx, agg)` / `repo.Update(ctx, agg)` — в одной транзакции с outbox-записью (если есть events)
5. **Emit:** `<Event>` через `outboxkit.Publisher` (если есть events)
6. **Return DTO**

## Called aggregate methods

- [`<Aggregate>.New<Name>`](../<Aggregate>.md#new<name>)
- [`<Aggregate>.<Mutator>`](../<Aggregate>.md#<mutator>)

<!-- Если методов агрегата нет (например DELETE напрямую в репозитории): -->
<!-- - _нет_ (удаление выполняется репозиторием напрямую) -->

## Events emitted

- [`<context>.<EventName>`](../events/<EventName>.md)

<!-- Или: -->
<!-- - _нет_ -->

> Если событие потребляет **соседний проект** бизнеса (межпроектный
> асинхронный обмен) — это тоже интеграция с `target: sibling-project`:
> заведи запись в `integration.md` и ребро в `docs/projects/project-map.md`.
> Симметрично — `consumes` события, пришедшего от соседнего проекта.

## Errors

| sentinel | when | HTTP status |
|---|---|---|
| `ErrInvalid<Field>` | валидация поля упала | 400 |
| `ErrNotFound` | агрегат не найден (для Update/Delete) | 404 |
| `ErrAlreadyExists` | уникальность нарушена | 409 |

## Idempotency

> Опциональная секция: что происходит при повторном вызове с теми же Inputs — retry HTTP-клиента, redelivery брокера, двойной клик. Для read-only операций — `_N/A (read-only)_`; у мутирующего use-case'а с повторяемым каналом (HTTP, топик) секция ожидаема.

- **Strategy:** natural (повтор безопасен по построению) | key-based (`<ключ дедупликации>`) | not-idempotent (<почему это допустимо>)
- **Duplicate outcome:** <что вернёт / что произойдёт при повторе: тот же DTO, `ErrAlreadyExists`, no-op>

## Side effects beyond the aggregate

> Что меняется кроме самого агрегата. Outbox-события — **нет** (они часть транзакции). Sending real email, billing, audit log, FK-каскады в БД — да, перечислить.

- _нет_

<!-- Пример при наличии side effects: -->
<!-- - Через FK `ON DELETE SET NULL` БД обнуляет `<other_table>.<this>_id` (если был связан). -->
