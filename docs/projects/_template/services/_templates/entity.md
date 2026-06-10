---
id: <context>.<Name>
kind: entity
context: <context>
name: <Name>
status: draft
relations: [<context>.<ParentAggregate>]
emits: []
consumes: []
---

# <Name>

> Одна-две фразы: что это в бизнесе. Child entity внутри агрегата `<ParentAggregate>`; снаружи агрегата напрямую недоступна.

> **Используй этот kind только когда child entity действительно сложна и заслуживает отдельного файла.** В большинстве случаев документируй child entities как подсекцию в файле aggregate'а.

## Identity

- **ID type:** <тип, обычно UUID v7>
- **ID scope:** локальный внутри `<ParentAggregate>` (внешние ссылки запрещены)
- **Mutable:** yes/no

## Properties

| name | type | required | brief |
|---|---|---|---|
| `<Field>` | <Type> | yes | <бизнес-значение> |

### `<Field>`

- **Constraints:** <правила валидации, длины, форматы>
- **Default:** —
- **Source:** input | derived | computed | system
- **Description:** <чем является в бизнесе>

## Methods

| name | brief |
|---|---|
| `<Method>` | <что делает> |

### `<Method>(...)`

- **params:** <что приходит>
- **returns:** <результат или sentinel-ошибка>
- **preconditions:** <бизнес-условия>
- **postconditions:** <что становится истинным>
- **events emitted:** <event или _нет_>

## Invariants

1. **<Инвариант 1>.** Гарантируется <конструктором / методом / БД-constraint>.

## Lifecycle

| from | event/method | to | guard | side effects |
|---|---|---|---|---|
| ∅ | `<конструктор>` | exists | — | <что происходит> |

<!-- если stateless: -->
<!-- _Lifecycle: N/A (stateless)._ -->

## Relations

| target | cardinality | type | description |
|---|---|---|---|
| `<context>.<ParentAggregate>` | N..1 | composition | принадлежит родительскому агрегату |
