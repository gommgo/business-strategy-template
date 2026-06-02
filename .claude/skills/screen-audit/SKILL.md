---
name: screen-audit
description: Аудит консистентности аналитических артефактов экранов проекта в `docs/projects/<project-slug>/screens/` — невалидные ссылки на slug (внутри screens и в interface-слое того же проекта), рассинхрон зеркал (`block.ux-substrates` ↔ interface, `screen.blocks` ↔ реально использованные `block:` в дереве, `block.used-by-screens`), нарушения slot-fills (необъявленный слот, нарушение `accepts`, незаполненный `required`-слот в stable-screen), `viewport` против участия в flow, отсутствие канон-состояний, anti-patterns (облик/breakpoints/FSD-имена в дереве, inline-cтейты в block.tree), coverage-дыры (shell/block без потребителей, недостижимый screen). Не правит артефакты, только указывает; деструктивные правки — через `screen-deep-dive`. Использовать перед коммитом артефактов, когда `screen-deep-dive` предлагает прогон в конце сессии, или когда аналитик подозревает рассогласование между файлами и зеркалами с interface. Принимает `<project-slug>` первым аргументом; без него — пикер по проектам. Полный прогон по 4 kind — без kind-аргумента; узкий — `<kind>` или `<kind>:<slug>`.
---

# screen-audit

Аудит консистентности 4 артефактных kind экранов **одного проекта** в
`docs/projects/<project-slug>/screens/` (flow · screen · block ·
shell). Канон формы — `docs/projects/_canon/screens/README.md` и
README'ы по 4 kind в его подпапках. Аудит **читает и сообщает**,
ничего не правит: каскадные правки идут через `screen-deep-dive`.

Аудит работает **в контексте одного проекта** (см. «Выбор проекта»).
Дальше по тексту `<project-slug>` — выбранный проект.

## Выбор проекта

| вызов | проект |
|---|---|
| `/screen-audit <project-slug> …` | взять `<project-slug>` |
| `/screen-audit …` (без slug) | `AskUserQuestion`-пикер по папкам `docs/projects/` (исключая `_canon`) |

1. Если первый аргумент совпадает с именем подпапки `docs/projects/`
   (кроме `_canon`) — это `<project-slug>`; остаток args — scope.
2. Иначе — пикер по подпапкам `docs/projects/` (исключить `_canon`).
   Если проектов нет — сказать «нечего аудитить», выйти.
3. Все чтения скоупятся в `docs/projects/<project-slug>/screens/`,
   `docs/projects/<project-slug>/interface/` (зеркала) и
   `audit-state/<project-slug>/`.

## Точки входа

После того как `<project-slug>` определён, остаток args задаёт scope:

| вызов | поведение |
|---|---|
| `/screen-audit <project-slug>` | полный прогон всех 4 kind проекта |
| `/screen-audit <project-slug> <kind>` | прогон одного kind + перекрёстные ссылки |
| `/screen-audit <project-slug> <kind>:<slug>` | одна запись + 1-shell соседи по ссылкам |

`kind` ∈ {`flow`, `screen`, `block`, `shell`}.

## Что аудит читает

- Рабочая зона:
  `docs/projects/<project-slug>/screens/{flows,screens,blocks,shells}/*/index.md`.
- Соседи: `docs/projects/<project-slug>/screens/assets/<kind>/<slug>/`
  (для проверки asset-файлов).
- Зеркала interface того же проекта:
  `docs/projects/<project-slug>/interface/{who,situation,block,ux-substrate,data-items}.md`.
- Контракт ui-lib: «топ-уровень компонентов» в каноне
  `docs/projects/_canon/screens/README.md` (пока
  `@stit-design/ui/manifest.json` не опубликован).

**Чего аудит не читает**:

- Другие проекты `docs/projects/<other-slug>/` — аудит скоупится в
  один проект; межпроектные несостыковки ловит `/cross-audit`.
- `docs/projects/_canon/screens/` — это канон формы, не рабочая зона.
  Из него читаются только критерии/anti-patterns/инвентарь, не данные.
- `docs/projects/example/` — образцовый проект, не рабочая зона.
  Игнорировать.
- Исходники библиотеки — это слой кода, не предмет screens.
- `state/<project-slug>/<kind>/<slug>.md` скилла `screen-deep-dive` —
  рабочая память другого скилла; аудит её не трогает.

## Что делать при запуске

1. Определить `<project-slug>` (см. «Выбор проекта»).
2. Прочитать канон `docs/projects/_canon/screens/README.md` и 4
   kind-README'я в его подпапках — освежить канон композиции,
   layout-язык, anti-patterns, форму frontmatter.
3. Прочитать `references/rules.md` — реестр проверок с тяжестью.
4. Прочитать рабочую зону
   `docs/projects/<project-slug>/screens/` (или подмножество по args).
5. Прогнать правила по очереди. Собрать findings.
6. Сгруппировать по сущности, отсортировать по severity внутри.
7. Вывести отчёт в чат.
8. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | Невалидная ссылка; дубликат `slug`; `slug` папки ≠ `slug` во frontmatter; `screen` ссылается на слот, не объявленный в shell; нарушение `accepts` (`tree` там, где `accepts: block`); рассинхрон зеркал; `block.interface-block.slug ≠ block.slug`; transition между desktop- и mobile-screen; `status` или `viewport` вне enum |
| `warning` | Семантическое подозрение, рискует смыслом | Облик/breakpoints/FSD-имена в дереве; inline-cтейты в `block.tree`; `screen.situations` не покрывает ситуации, чьи ux-substrates есть на экране; пустой обязательный слот frontmatter; `description` совпадает с `name`; flow с одним screen и в `desktop`, и в `mobile`; `screen.viewport` несовместим с участием в `flow.desktop`/`mobile` |
| `hint` | Coverage / стиль, не ломает | shell без screens; block без потребителей; screen недостижим (не в flow, не entrypoint, не таргет переходов); stable ссылается на draft; `ui:Component` отсутствует в выводимом инвентаре; короткое `description` |

Подробный реестр — `references/rules.md`.

## Stable как ужесточение

Часть правил повышают severity при `status: stable`:

- пустой обязательный слот frontmatter: `warning` (draft) → `error` (stable);
- `screen.states` не покрывает 6 канон-состояний: `hint` (draft) → `error` (stable);
- `block.tree` не содержит узла для объявленного `ux-substrate`:
  `hint` (draft) → `warning` (stable).

Это потому, что для stable канон требует одновременно ✅ всех 6 пунктов
`screen-deep-dive/references/draft-stable.md`. На draft те же дыры —
ожидаемое незаконченное состояние.

## Формат отчёта

В чат:

```
=== /screen-audit <project-slug> ===
Прочитано: 4 kind, N записей (F flow, S screen, B block, H shell).

[error] screen:studies-workspace → невалидная ссылка screen.shell = `app-shel` (нет в shells/).
  Что делать: исправить опечатку или завести shell через
  /screen-deep-dive <project-slug> shell:app-shel.

[error] screen:studies-workspace → slot-fills.foo не объявлен в shell `app-shell`
  (slots: side, main, detail, overlay).
  Что делать: убрать slot-fills.foo или объявить слот в shell через
  /screen-deep-dive <project-slug> shell:app-shell.

[error] block:studies-list → рассинхрон ux-substrates со screens-слоем:
  interface объявил [a, b, c], screens объявил [a, b].
  Что делать: пересинхронизировать через /screen-deep-dive <project-slug> block:studies-list
  (скилл переспросит источник правды).

[warning] block:studies-list → tree содержит `ui:Skeleton` (inline-state в block).
  Что делать: перенести в screen.states через /screen-deep-dive <project-slug> screen:<потребитель>.

[hint] shell:auth-shell → ни один screen не ссылается на этот shell.
  Что делать: завести screen с shell=auth-shell или удалить shell через
  /screen-deep-dive <project-slug> (каскадно).

Сводка: 3 error / 1 warning / 1 hint.
```

Группировка — по сущности; внутри — `error → warning → hint`.

## `audit-state/<project-slug>/last-report.md`

Отчёт лежит **рядом со скиллом**, не в
`docs/projects/<project-slug>/screens/` и не в корне проекта, и
скоупится по проекту:

```
.claude/skills/screen-audit/audit-state/<project-slug>/last-report.md
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
kinds-read: 4
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила структуры (R-STRUCT-*)
- R-STRUCT-001 «валидность ссылок внутри screens»: проверил M ссылок, нашёл K битых.
  - screen:studies-workspace.shell = `app-shel` → нет в shells/ → error.
- R-STRUCT-002 «валидность ссылок в interface»: ...
...

## Правила зеркал (R-MIRROR-*)
- R-MIRROR-001 «block.ux-substrates ↔ interface»: ...

## Правила семантики (R-SEM-*)
- ...

## Правила coverage (R-COV-*)
- ...
```

## Что не делать

- **Не править артефакты.** Аудит — только отчёт. Все правки — через
  `screen-deep-dive`.
- **Не понижать `stable → draft`.** Максимум — hint «возможно,
  понизить?» в отчёте.
- **Не выдумывать findings.** Если правило не сработало — не писать
  «возможно, тут что-то не так на всякий случай».
- **Не лезть в interface-слой проекта
  (`docs/projects/<project-slug>/interface/`) правками.** Если
  interface ссылка битая — это `interface-deep-dive`. Если зеркало
  `ux-substrates` расходится — отчёт указывает оба слоя, но решение
  источника правды делает аналитик через `screen-deep-dive`.
- **Не смешивать проекты.** Аудит скоупится в один `<project-slug>`;
  межпроектные несостыковки — предмет `/cross-audit`, не этот скилл.
- **Не аккумулировать историю** в `audit-state/`. Перезаписывать
  `last-report.md` каждый прогон.
- **Не запускать `screen-deep-dive`** автоматически из аудита. Это
  делает аналитик руками по выводу аудита.
- **Не аудитить `docs/projects/example/`** — это образцовый проект, не
  рабочая зона.
- **Не аудитить `docs/projects/_canon/screens/`** — это канон формы;
  из него читаются только критерии и инвентарь, не данные.
- **Не аудитить `state/<project-slug>/<kind>/<slug>.md`** — рабочая
  память `screen-deep-dive`, не предмет screens-канона.
