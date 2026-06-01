---
name: interface-audit
description: Аудит консистентности аналитических артефактов интерфейса в `docs/interface/` — невалидные ссылки на slug, циклы parent-zone, рассинхрон зеркал ситуации, тупики (зона без блоков, блок без субстратов или участников), пустые обязательные слоты в stable-записях, семантические подозрения (goal как предусловие, using-what с обликом), coverage-дыры (who/stage без покрытия ситуациями). Не правит артефакты, только указывает; деструктивные правки — через `interface-deep-dive`. Использовать перед коммитом артефактов, когда `interface-deep-dive` предлагает прогон в конце сессии, или когда аналитик подозревает рассогласование между файлами. Полный прогон по 7 файлам — без аргументов; узкий — `<kind>` или `<kind>:<slug>`.
---

# interface-audit

Аудит консистентности 7 артефактных файлов в `docs/interface/`. Канон —
`docs/interface/README.md`. Аудит **читает и сообщает**, ничего не
правит: каскадные правки идут через `interface-deep-dive`.

## Точки входа

| вызов | поведение |
|---|---|
| `/interface-audit` | полный прогон всех 7 файлов |
| `/interface-audit <kind>` | прогон одного файла + перекрёстные ссылки |
| `/interface-audit <kind>:<slug>` | одна запись + 1-shell соседи по ссылкам |

`kind` ∈ {`who`, `stage`, `situation`, `zone`, `block`, `ux-substrate`, `data-items`}.

## Что делать при запуске

1. Прочитать `docs/interface/README.md` — освежить канон.
2. Прочитать `references/rules.md` — реестр проверок с тяжестью.
3. Прочитать все 7 файлов (или подмножество по args).
4. Прогнать правила по очереди. Собрать findings.
5. Сгруппировать по сущности, отсортировать по severity внутри.
6. Вывести отчёт в чат.
7. Перезаписать `audit-state/last-report.md` с reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | Невалидная ссылка; цикл `parent-zone`; дубликат `slug` в одном файле; рассинхрон зеркал; `block` без `ux-substrates` или без `who`; явный `transition-to-block` внутри одной зоны |
| `warning` | Семантическое подозрение, рискует смыслом | Пустой обязательный слот; `goal` похож на предусловие; `using-what` содержит облик; `block` без хотя бы одного входа; `description` совпадает с `name` |
| `hint` | Coverage / стиль, не ломает | Stable со ссылкой на draft; `who` или `stage` без покрытия ситуациями; `zone` без блоков; очень короткое `description` |

Подробный реестр — `references/rules.md`.

## Формат отчёта

В чат:

```
=== /interface-audit ===
Прочитано: 7 файлов, N записей.

[error] situation:submit-referral → невалидная ссылка situation.who = `doctor` (нет в who.md).
  Что делать: завести `doctor` через /interface-deep-dive who, или
  заменить на существующий who-slug.

[error] zone:study-card → цикл parent-zone: study-card → studies → study-card.
  Что делать: пересмотреть иерархию через /interface-deep-dive zone:study-card.

[warning] situation:submit-referral → goal «авторизуется, чтобы продолжить работу»
  похож на предусловие следующего шага (anti-pattern из situation.md).
  Что делать: уточнить «зачем именно так» в /interface-deep-dive situation:submit-referral.

[hint] who:doctor → нет ни одной ситуации с who = doctor.
  Что делать: либо завести ситуацию-инициатор, либо удалить who:doctor
  через /interface-deep-dive (каскадно).

Сводка: 3 error / 1 warning / 1 hint.
```

Группировка — по сущности; внутри — `error → warning → hint`.

## `audit-state/last-report.md`

Отчёт лежит **рядом со скиллом**, не в `docs/interface/` и не в
корне проекта:

```
.claude/skills/interface-audit/audit-state/last-report.md
```

Дальше по тексту скилла — короткое `audit-state/`, это сокращение
того же пути.

После каждого прогона перезаписывается одним файлом с reasoning-trace:
какие правила запускал, какие записи проверил, что нашёл, почему. Это
не журнал — следующий прогон перезатирает. В git, чтобы команда могла
читать.

Структура:

```markdown
---
ran-on: <scope: all | kind | kind:slug>
files-read: 7
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила структуры (R-STRUCT-*)
- R-STRUCT-001 «валидность ссылок»: проверил M ссылок, нашёл K битых.
  - situation:submit-referral.who = `doctor` → нет в who.md → error.
- R-STRUCT-002 «цикл parent-zone»: ...
...

## Правила зеркал (R-MIRROR-*)
- ...

## Правила семантики (R-SEM-*)
- ...

## Правила coverage (R-COV-*)
- ...
```

## Что не делать

- **Не править артефакты.** Аудит — только отчёт. Все правки — через
  `interface-deep-dive`.
- **Не понижать `stable → draft`.** Максимум — hint «возможно,
  понизить?» в отчёте.
- **Не выдумывать findings.** Если правило не сработало — не писать
  «возможно, тут что-то не так на всякий случай».
- **Не аккумулировать историю** в `audit-state/`. Перезаписывать
  `last-report.md` каждый прогон.
- **Не запускать `interface-deep-dive`** автоматически из аудита. Это
  делает аналитик руками по выводу аудита.
