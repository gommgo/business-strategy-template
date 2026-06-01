---
name: project-audit
description: Узкий аудит консистентности продуктового слоя `docs/project/` (vision + 7 табличных kinds: persona, capability, boundary, surface, integration, constraint, market) — невалидные enum, дубликаты slug, пустые обязательные слоты в stable-записях, невалидные status, рассинхрон stable со state-blocker'ами, семантические подозрения внутри project (capability без persona, surface без persona, boundary с backlog-обоснованием, constraint без source, market без url/sources), coverage-дыры (persona без покрытия, vision stable при пустых соседях). Сквозную проверку с interface/domain/screen-слоями делает `/cross-audit`, не этот скилл. Не правит артефакты, только отчёт; деструктивные правки — через `/project-deep-dive`. Использовать перед коммитом артефактов, когда `/project-deep-dive` предлагает прогон в конце сессии, перед `/cross-audit`, или когда аналитик подозревает рассогласование внутри project-слоя.
---

# project-audit

Аудит консистентности 1 singleton + 7 табличных файлов в `docs/project/`.
Канон — `docs/project/README.md`. Аудит **читает и сообщает**, ничего не
правит: каскадные правки идут через `/project-deep-dive`.

**Сквозную проверку** (project ↔ interface ↔ domain ↔ screen) делает
`/cross-audit`. Здесь — только внутрипроектная.

## Точки входа

| вызов | поведение |
|---|---|
| `/project-audit` | полный прогон 8 файлов |
| `/project-audit <kind>` | прогон одного файла + ссылающихся соседей |
| `/project-audit <kind>:<slug>` | одна запись + 1-shell соседи |

`kind` ∈ {`vision`, `persona`, `capability`, `boundary`, `surface`,
`integration`, `constraint`, `market`}.

## Что делать при запуске

1. Прочитать `docs/project/README.md` — освежить канон.
2. Прочитать `references/rules.md` — реестр проверок с severity.
3. Прочитать все 8 файлов (или подмножество по args).
4. Прочитать `state/` обоих скиллов (`project-deep-dive/state/` и
   `project-deep-dive-for-business/state/`) — для проверок типа «stable
   с blocker-вопросами».
5. Прогнать правила по очереди. Собрать findings.
6. Сгруппировать по сущности, отсортировать по severity внутри.
7. Вывести отчёт в чат.
8. Перезаписать `audit-state/last-report.md` с reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | Дубликат `slug`; невалидное enum-значение; пустой обязательный слот в `stable`; vision без Problem или Success; stable со `**blocker**` в state |
| `warning` | Семантическое подозрение | capability без persona в массиве; surface без persona; boundary с backlog-обоснованием в `why` («нет ресурсов»); constraint без `source`; market без `url`/`sources`; integration с `direction` но без `owner` |
| `hint` | Coverage / стиль, не ломает | persona без жителей в capability/surface; vision stable при пустой persona-таблице; stable со ссылкой на draft; очень короткое `description` |

Подробный реестр — `references/rules.md`.

## Формат отчёта

В чат:

```
=== /project-audit ===
Прочитано: 8 файлов, N записей.

[error] vision → раздел Success пустой. status: stable.
  Что делать: дописать Success или понизить до draft через
  /project-deep-dive.

[error] capability:send-referral → status: stable, но `persona = —`.
  Что делать: связать с persona через /project-deep-dive capability:send-referral.

[warning] boundary:no-mobile → why = «не делаем мобильное приложение, нет ресурсов».
  Похоже на backlog в маскировке (anti-pattern из boundary.md).
  Что делать: пересмотреть формулировку через /project-deep-dive boundary:no-mobile.

[hint] persona:doctor → ни одна capability и ни одна surface не
  ссылается на эту персону.
  Что делать: либо подключить к capability/surface, либо рассмотреть
  удаление через /project-deep-dive.

Сводка: 2 error / 1 warning / 1 hint.
```

Группировка — по сущности; внутри — `error → warning → hint`.

## `audit-state/last-report.md`

Отчёт лежит **рядом со скиллом**:

```
.claude/skills/project-audit/audit-state/last-report.md
```

После каждого прогона перезаписывается одним файлом с reasoning-trace:
какие правила запускал, какие записи проверил, что нашёл, почему. Это
не журнал — следующий прогон перезатирает. В git, чтобы команда могла
читать.

Структура:

```markdown
---
ran-on: <scope: all | kind | kind:slug>
files-read: 8
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила структуры (R-STRUCT-*)
- R-STRUCT-001 «дубликаты slug»: ...
- R-STRUCT-002 «обязательные слоты в stable»: ...
...

## Правила семантики (R-SEM-*)
- ...

## Правила coverage (R-COV-*)
- ...
```

## Что не делать

- **Не править артефакты.** Аудит — только отчёт. Все правки — через
  `/project-deep-dive`.
- **Не понижать `stable → draft`.** Максимум — error «обязательный
  слот пустой при stable» в отчёте, аналитик понизит руками.
- **Не выдумывать findings.** Если правило не сработало — не писать
  «возможно, тут что-то не так на всякий случай».
- **Не делать кросс-слойную проверку** (project ↔ interface / domain /
  screen). Это `/cross-audit`.
- **Не аккумулировать историю** в `audit-state/`. Перезаписывать
  `last-report.md` каждый прогон.
- **Не запускать `/project-deep-dive`** автоматически из аудита. Это
  делает аналитик руками по выводу аудита.
- **Не предлагать клиенту запустить** `/project-audit`. Это аналитический
  инструмент; в `project-deep-dive-for-business` он не упоминается.
