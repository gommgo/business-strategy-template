---
id: <context>.<Name>
kind: event
context: <context>
name: <Name>
status: draft
relations: [<context>.<Aggregate>]
emits: []
consumes: []
---

# <Name>

> Одно предложение: что произошло в бизнесе. В прошедшем времени (`UserRegistered`, `EmailVerified`, `OrderCancelled`). Суффикс `Event` **не** используется — имя самодостаточно.

## Trigger

- **Source aggregate:** [`<context>.<Aggregate>`](../<Aggregate>.md)
- **Triggering use-case:** [`<context>.<UseCase>`](../use-cases/<UseCase>.md)
- **When:** после успешного коммита транзакции, в которой произошло изменение

## Payload

| field | type | description |
|---|---|---|
| `EventID` | UUID v7 | ключ идемпотентности; уникален для каждого экземпляра события |
| `OccurredAt` | timestamp | момент произошедшего изменения |
| `<Aggregate>ID` | UUID v7 | идентификатор агрегата-источника |
| `<custom field>` | <type> | <зачем нужно консьюмерам> |

## Consumers

| consumer | bounded context | reaction |
|---|---|---|
| `<HandlerName>` | `<context>` | <что делает в ответ> |

<!-- Если на старте консьюмеров нет: -->
<!-- - _нет на старте_ -->

## Delivery semantics

- **Delivery:** at-least-once
- **Ordering:** none | per-aggregate (partition key = `<Aggregate>ID`)
- **Idempotency key:** `EventID` (или `<Aggregate>ID` + дискриминатор)
- **Retention:** outbox держит до подтверждения всеми консьюмерами

## Notes

> Дополнительные ограничения и договорённости о совместимости payload — что консьюмерам нельзя ломать.

- _нет_
