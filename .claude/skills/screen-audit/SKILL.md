---
name: screen-audit
description: Аудит консистентности аналитических артефактов экранов в `docs/screens/` — невалидные ссылки на slug (внутри screens и в `docs/interface/`), рассинхрон зеркал (`block.ux-substrates` ↔ interface, `screen.blocks` ↔ реально использованные `block:` в дереве, `block.used-by-screens`), нарушения slot-fills (необъявленный слот, нарушение `accepts`, незаполненный `required`-слот в stable-screen), `viewport` против участия в flow, отсутствие канон-состояний, anti-patterns (облик/breakpoints/FSD-имена в дереве, inline-cтейты в block.tree), coverage-дыры (shell/block без потребителей, недостижимый screen). Не правит артефакты, только указывает; деструктивные правки — через `screen-deep-dive`. Использовать перед коммитом артефактов, когда `screen-deep-dive` предлагает прогон в конце сессии, или когда аналитик подозревает рассогласование между файлами и зеркалами с interface. Полный прогон по 4 kind — без аргументов; узкий — `<kind>` или `<kind>:<slug>`.
---

# screen-audit

Аудит консистентности 4 артефактных kind в `docs/screens/` (flow ·
screen · block · shell). Канон композиции — `docs/screens/README.md` и
README'ы по 4 kind в подпапках. Аудит **читает и сообщает**, ничего не
правит: каскадные правки идут через `screen-deep-dive`.

## Точки входа

| вызов | поведение |
|---|---|
| `/screen-audit` | полный прогон всех 4 kind |
| `/screen-audit <kind>` | прогон одного kind + перекрёстные ссылки |
| `/screen-audit <kind>:<slug>` | одна запись + 1-shell соседи по ссылкам |

`kind` ∈ {`flow`, `screen`, `block`, `shell`}.

## Что аудит читает

- Рабочая зона: `docs/screens/{flows,screens,blocks,shells}/*/index.md`.
- Соседи: `docs/screens/assets/<kind>/<slug>/` (для проверки asset-файлов).
- Зеркала interface: `docs/interface/{who,situation,block,ux-substrate,data-items}.md`.
- Контракт ui-lib: «топ-уровень компонентов» в `docs/screens/README.md`
  (пока `@stit-design/ui/manifest.json` не опубликован).

**Чего аудит не читает**:

- `docs/screens/example/` — образцовый набор, не рабочая зона. Игнорировать.
- Исходники библиотеки — это слой кода, не предмет screens.
- `state/<kind>/<slug>.md` скилла `screen-deep-dive` — рабочая память
  другого скилла; аудит её не трогает.

## Что делать при запуске

1. Прочитать `docs/screens/README.md` и 4 kind-README'я — освежить канон
   композиции, layout-язык, anti-patterns, форму frontmatter.
2. Прочитать `references/rules.md` — реестр проверок с тяжестью.
3. Прочитать рабочую зону (или подмножество по args).
4. Прогнать правила по очереди. Собрать findings.
5. Сгруппировать по сущности, отсортировать по severity внутри.
6. Вывести отчёт в чат.
7. Перезаписать `audit-state/last-report.md` с reasoning-trace.

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
=== /screen-audit ===
Прочитано: 4 kind, N записей (F flow, S screen, B block, H shell).

[error] screen:studies-workspace → невалидная ссылка screen.shell = `app-shel` (нет в shells/).
  Что делать: исправить опечатку или завести shell через
  /screen-deep-dive shell:app-shel.

[error] screen:studies-workspace → slot-fills.foo не объявлен в shell `app-shell`
  (slots: side, main, detail, overlay).
  Что делать: убрать slot-fills.foo или объявить слот в shell через
  /screen-deep-dive shell:app-shell.

[error] block:studies-list → рассинхрон ux-substrates со screens-слоем:
  interface объявил [a, b, c], screens объявил [a, b].
  Что делать: пересинхронизировать через /screen-deep-dive block:studies-list
  (скилл переспросит источник правды).

[warning] block:studies-list → tree содержит `ui:Skeleton` (inline-state в block).
  Что делать: перенести в screen.states через /screen-deep-dive screen:<потребитель>.

[hint] shell:auth-shell → ни один screen не ссылается на этот shell.
  Что делать: завести screen с shell=auth-shell или удалить shell через
  /screen-deep-dive (каскадно).

Сводка: 3 error / 1 warning / 1 hint.
```

Группировка — по сущности; внутри — `error → warning → hint`.

## `audit-state/last-report.md`

Отчёт лежит **рядом со скиллом**, не в `docs/screens/` и не в
корне проекта:

```
.claude/skills/screen-audit/audit-state/last-report.md
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
- **Не лезть в `docs/interface/` правками.** Если interface ссылка
  битая — это `interface-deep-dive`. Если зеркало `ux-substrates`
  расходится — отчёт указывает оба слоя, но решение источника правды
  делает аналитик через `screen-deep-dive`.
- **Не аккумулировать историю** в `audit-state/`. Перезаписывать
  `last-report.md` каждый прогон.
- **Не запускать `screen-deep-dive`** автоматически из аудита. Это
  делает аналитик руками по выводу аудита.
- **Не аудитить `docs/screens/example/`** — это эталон, не рабочая зона.
- **Не аудитить `state/<kind>/<slug>.md`** — рабочая память
  `screen-deep-dive`, не предмет screens-канона.
