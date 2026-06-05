---
name: interface-audit
description: Аудит консистентности аналитических артефактов интерфейса проекта в `docs/projects/<project-slug>/interface/` — невалидные ссылки на slug, циклы parent-zone, рассинхрон зеркал ситуации, тупики (зона без блоков, блок без субстратов или участников), пустые обязательные слоты в stable-записях, семантические подозрения (goal как предусловие, using-what с обликом), coverage-дыры (who/stage без покрытия ситуациями). Не правит артефакты, только указывает; деструктивные правки — через `interface-deep-dive`. Использовать перед коммитом артефактов, когда `interface-deep-dive` предлагает прогон в конце сессии, или когда аналитик подозревает рассогласование между файлами. Принимает `<project-slug>` первым аргументом; без него — пикер по проектам. Полный прогон по 7 файлам — без kind-аргумента; узкий — `<kind>` или `<kind>:<slug>`.
---

# interface-audit

Аудит консистентности 7 артефактных файлов интерфейса **одного
проекта** в `docs/projects/<project-slug>/interface/`. Канон формы —
`docs/projects/_canon/interface/README.md`. Аудит **читает и
сообщает**, ничего не правит: каскадные правки идут через
`interface-deep-dive`.

Аудит работает **в контексте одного проекта** (см. «Выбор проекта»).
Дальше по тексту `<project-slug>` — выбранный проект.

## Выбор проекта

| вызов | проект |
|---|---|
| `/interface-audit <project-slug> …` | взять `<project-slug>` |
| `/interface-audit …` (без slug) | `AskUserQuestion`-пикер по папкам `docs/projects/` (исключая `_canon`) |

1. Если первый аргумент совпадает с именем подпапки `docs/projects/`
   (кроме `_canon`) — это `<project-slug>`; остаток args — scope.
2. Иначе — пикер по подпапкам `docs/projects/` (исключить `_canon`).
   Если проектов нет — сказать «нечего аудитить», выйти.
3. Все чтения скоупятся в `docs/projects/<project-slug>/interface/`
   и `audit-state/<project-slug>/`.

## Точки входа

После того как `<project-slug>` определён, остаток args задаёт scope:

| вызов | поведение |
|---|---|
| `/interface-audit <project-slug>` | полный прогон всех 7 файлов проекта |
| `/interface-audit <project-slug> <kind>` | прогон одного файла + перекрёстные ссылки |
| `/interface-audit <project-slug> <kind>:<slug>` | одна запись + 1-shell соседи по ссылкам |

`kind` ∈ {`who`, `stage`, `situation`, `zone`, `block`, `ux-substrate`, `data-items`}.

## Что делать при запуске

1. Определить `<project-slug>` (см. «Выбор проекта»).
2. Прочитать `docs/projects/_canon/interface/README.md` — освежить
   канон формы.
3. Прочитать `references/rules.md` — реестр проверок с тяжестью.
4. Прочитать все 7 файлов
   `docs/projects/<project-slug>/interface/` (или подмножество по
   args).
5. Прогнать правила по очереди. Собрать findings.
6. Сгруппировать по сущности, отсортировать по severity внутри.
7. Вывести отчёт в чат.
8. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

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
=== /interface-audit <project-slug> ===
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

## `audit-state/<project-slug>/last-report.md`

Отчёт лежит **рядом со скиллом**, не в
`docs/projects/<project-slug>/interface/` и не в корне проекта, и
скоупится по проекту:

```
.claude/skills/interface-audit/audit-state/<project-slug>/last-report.md
```

Дальше по тексту скилла — короткое `audit-state/`, это сокращение
того же пути (с учётом текущего `<project-slug>`).

После каждого прогона перезаписывается одним файлом с reasoning-trace:
какие правила запускал, какие записи проверил, что нашёл, почему. Это
не журнал — следующий прогон перезатирает. В git, чтобы команда могла
читать.

Структура:

```markdown
---
project: <project-slug>
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
- **Не реализовывать suppressions.** В отличие от `/cross-audit`,
  `/swot-audit` и `/hypothesis-map-audit` (семантические findings, бывают
  ложные), структурный аудит детерминирован — зеркало синхронно или нет,
  ссылка существует или нет. Ложных срабатываний не бывает, подавлять
  нечего.
- **Не смешивать проекты.** Аудит скоупится в один `<project-slug>`;
  межпроектные несостыковки — предмет `/cross-audit`, не этот скилл.
- **Не запускать `interface-deep-dive`** автоматически из аудита. Это
  делает аналитик руками по выводу аудита.
