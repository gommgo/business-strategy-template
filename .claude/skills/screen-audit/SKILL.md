---
name: screen-audit
description: "Аудит консистентности аналитических артефактов экранов проекта в `docs/projects/<project-slug>/screens/<surface>/` — по папке на поверхность (surface) из реестра `surface.md`. Невалидные ссылки на slug (внутри screens той же поверхности и в interface-слое той же поверхности), рассинхрон зеркал (`block.ux-substrates` ↔ interface, `screen.blocks` ↔ реально использованные `block:` в дереве, `block.used-by-screens`), нарушения slot-fills (необъявленный слот, нарушение `accepts`, незаполненный `required`-слот в stable-screen), `viewport` против участия в flow, отсутствие канон-состояний, anti-patterns (облик/breakpoints/FSD-имена в дереве, inline-cтейты в block.tree), coverage-дыры (shell/block без потребителей, недостижимый screen), папка поверхности вне реестра, ссылка из одной поверхности в другую. Не правит артефакты, только указывает; деструктивные правки — через `screen-deep-dive`. Использовать перед коммитом артефактов, когда `screen-deep-dive` предлагает прогон в конце сессии, или когда аналитик подозревает рассогласование между файлами и зеркалами с interface. Принимает `<project-slug>` первым аргументом; без него — пикер по проектам. Без `<surface>` — прогон по всем папкам поверхностей; с `<surface>` — одна поверхность. Полный прогон по 4 kind — без kind-аргумента; узкий — `<kind>` или `<kind>:<slug>`."
---

# screen-audit

Аудит консистентности 4 артефактных kind экранов **одной поверхности**
проекта в `docs/projects/<project-slug>/screens/<surface>/` (flow ·
screen · block · shell). Канон формы —
`docs/projects/_template/screens/README.md` и README'ы по 4 kind в его
подпапках. Аудит **читает и сообщает**, ничего не правит: каскадные
правки идут через `screen-deep-dive`.

Слой композиции **партиционирован по поверхности (surface)**: на каждую
поверхность из реестра `docs/projects/<project-slug>/surface.md` — своя
папка `screens/<surface>/` с подпапками `{flows,screens,blocks,shells}`
и `assets/`. Все ссылки внутри `screens/<surface>/` и зеркала с
`interface/<surface>/` — **в пределах одной поверхности**. Аудит
итерирует **по каждой папке поверхности** независимо.

Аудит работает **в контексте одного проекта** (см. «Выбор проекта и
поверхности»). Дальше по тексту `<project-slug>` — выбранный проект,
`<surface>` — поверхность (одна или все).

## Выбор проекта и поверхности

Аргументы позиционны — `<project-slug>` первый, `<surface>` второй
(опционален):

| вызов | проект · поверхность |
|---|---|
| `/screen-audit <project-slug> <surface> …` | взять `<project-slug>` и `<surface>` |
| `/screen-audit <project-slug> …` (без surface) | проект задан; **все** папки поверхностей проекта |
| `/screen-audit …` (без slug) | `AskUserQuestion`-пикер **по именам** проектов (исключая `_template`); затем все поверхности |

1. Если первый аргумент совпадает с именем подпапки `docs/projects/`
   (кроме `_template`) — это `<project-slug>`. Иначе — пикер **по
   именам** проектов (исключить `_template`). Если проектов нет —
   сказать «нечего аудитить», выйти.
2. Прочитать реестр `docs/projects/<project-slug>/surface.md`. Если
   следующий аргумент совпадает со `slug` строки реестра — это
   `<surface>` (одна поверхность), остаток args — scope. Если аргумента
   нет — поверхностей **все**: аудит проходит по каждой папке
   `screens/<surface>/` отдельно, отчёт группируется по поверхности.
3. Все чтения скоупятся в `docs/projects/<project-slug>/screens/<surface>/`
   (одну или каждую), зеркала `docs/projects/<project-slug>/interface/<surface>/`
   и `audit-state/<project-slug>/`.

## Точки входа

После того как `<project-slug>` и (опц.) `<surface>` определены, остаток
args задаёт scope:

| вызов | поведение |
|---|---|
| `/screen-audit <project-slug>` | полный прогон всех 4 kind в каждой папке поверхности |
| `/screen-audit <project-slug> <surface>` | полный прогон всех 4 kind одной поверхности |
| `/screen-audit <project-slug> <surface> <kind>` | прогон одного kind поверхности + перекрёстные ссылки внутри неё |
| `/screen-audit <project-slug> <surface> <kind>:<slug>` | одна запись + 1-shell соседи по ссылкам внутри поверхности |

`kind` ∈ {`flow`, `screen`, `block`, `shell`}.
`<kind>` и `<kind>:<slug>` требуют заданной `<surface>` (kind живёт в
конкретной поверхности).

## Что аудит читает

- Рабочая зона:
  `docs/projects/<project-slug>/screens/<surface>/{flows,screens,blocks,shells}/*/index.md`.
- Соседи: `docs/projects/<project-slug>/screens/<surface>/assets/<kind>/<slug>/`
  (для проверки asset-файлов).
- Зеркала interface **той же поверхности**:
  `docs/projects/<project-slug>/interface/<surface>/{who,situation,block,ux-substrate,data-items}.md`.
- Реестр-хребет `docs/projects/<project-slug>/surface.md` — перечень
  поверхностей (для R-SURF).
- Контракт ui-lib: «топ-уровень компонентов» в каноне
  `docs/projects/_template/screens/README.md` (пока
  `@stit/ui/manifest.json` не опубликован).

**Чего аудит не читает**:

- Другие проекты `docs/projects/<other-slug>/` — аудит скоупится в
  один проект; межпроектные несостыковки ловит `/cross-audit`.
- Другие поверхности того же проекта при разрешении ссылок — каждая
  папка `screens/<surface>/` аудитится в своих границах; ссылка в чужую
  поверхность — error (R-XSURF-001), а кросс-поверхностную сверку делает
  `/cross-audit`.
- `docs/projects/_template/screens/` — это канон формы, не рабочая зона.
  Из него читаются только критерии/anti-patterns/инвентарь, не данные.
- Исходники библиотеки — это слой кода, не предмет screens.
- `state/<project-slug>/<surface>/<kind>/<slug>.md` скилла
  `screen-deep-dive` — рабочая память другого скилла; аудит её не
  трогает.

## Что делать при запуске

1. Определить `<project-slug>` и (опц.) `<surface>` (см. «Выбор проекта
   и поверхности»).
2. Прочитать канон `docs/projects/_template/screens/README.md` и 4
   kind-README'я в его подпапках — освежить канон композиции,
   layout-язык, anti-patterns, форму frontmatter.
3. Прочитать `references/rules.md` — реестр проверок с тяжестью.
4. Прочитать реестр `docs/projects/<project-slug>/surface.md`. Сверить
   с подпапками `docs/projects/<project-slug>/screens/`: папка вне
   реестра — error (R-SURF-001), поверхность реестра без папки screens —
   hint (R-SURF-002).
5. Для каждой папки поверхности из scope (одна заданная `<surface>` или
   все) прочитать её рабочую зону
   `docs/projects/<project-slug>/screens/<surface>/` (или подмножество
   по args). Прогнать правила **в пределах этой поверхности**, собрать
   findings.
6. Сгруппировать по поверхности, внутри — по сущности; отсортировать по
   severity внутри.
7. Вывести отчёт в чат.
8. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | Невалидная ссылка; дубликат `slug`; `slug` папки ≠ `slug` во frontmatter; `screen` ссылается на слот, не объявленный в shell; нарушение `accepts` (`tree` там, где `accepts: block`); рассинхрон зеркал; `block.interface-block.slug ≠ block.slug`; transition между desktop- и mobile-screen; `status` или `viewport` вне enum; папка поверхности вне реестра `surface.md`; ссылка из папки одной поверхности в сущность другой |
| `warning` | Семантическое подозрение, рискует смыслом | Облик/breakpoints/FSD-имена в дереве; inline-cтейты в `block.tree`; `screen.situations` не покрывает ситуации, чьи ux-substrates есть на экране; пустой обязательный слот frontmatter; `description` совпадает с `name`; flow с одним screen и в `desktop`, и в `mobile`; `screen.viewport` несовместим с участием в `flow.desktop`/`mobile` |
| `hint` | Coverage / стиль, не ломает | shell без screens; block без потребителей; screen недостижим (не в flow, не entrypoint, не таргет переходов); stable ссылается на draft; `ui:Component` отсутствует в выводимом инвентаре; короткое `description`; поверхность реестра без папки screens |

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
Поверхностей в scope: K (web-clinic, tg-bot). Прочитано: 4 kind × K, N записей.

[error] web-clinic / папка экранов не имеет поверхности в реестре surface.md.
  Что делать: завести строку в surface.md через /project-deep-dive <project-slug>,
  либо удалить папку screens/<surface>/.

[error] web-clinic / screen:studies-workspace → невалидная ссылка screen.shell = `app-shel` (нет в shells/ этой поверхности).
  Что делать: исправить опечатку или завести shell через
  /screen-deep-dive <project-slug> web-clinic shell:app-shel.

[error] web-clinic / screen:studies-workspace → slot-fills.foo не объявлен в shell `app-shell`
  (slots: side, main, detail, overlay).
  Что делать: убрать slot-fills.foo или объявить слот в shell через
  /screen-deep-dive <project-slug> web-clinic shell:app-shell.

[error] web-clinic / block:studies-list → рассинхрон ux-substrates с interface-слоем той же поверхности:
  interface объявил [a, b, c], screens объявил [a, b].
  Что делать: пересинхронизировать через /screen-deep-dive <project-slug> web-clinic block:studies-list
  (скилл переспросит источник правды).

[warning] web-clinic / block:studies-list → tree содержит `ui:Skeleton` (inline-state в block).
  Что делать: перенести в screen.states через /screen-deep-dive <project-slug> web-clinic screen:<потребитель>.

[hint] tg-bot / shell:auth-shell → ни один screen не ссылается на этот shell.
  Что делать: завести screen с shell=auth-shell или удалить shell через
  /screen-deep-dive <project-slug> tg-bot (каскадно).

Сводка: 3 error / 1 warning / 1 hint.
```

Группировка — по поверхности, внутри — по сущности; в пределах сущности
— `error → warning → hint`.

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
ran-on: <scope: all-surfaces | surface | surface kind | surface kind:slug>
surfaces: [<surface-1>, <surface-2>]
kinds-read: 4 × surfaces
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила хребта (R-SURF-*)
- R-SURF-001 «папка поверхности вне реестра»: сверил подпапки screens/
  с surface.md — нашёл K лишних.
- R-SURF-002 «поверхность реестра без папки screens»: ...

## Поверхность <surface-1>

### Правила структуры (R-STRUCT-*)
- R-STRUCT-001 «валидность ссылок внутри screens»: проверил M ссылок, нашёл K битых.
  - screen:studies-workspace.shell = `app-shel` → нет в shells/ → error.
- R-STRUCT-002 «валидность ссылок в interface той же поверхности»: ...
...

### Правила зеркал (R-MIRROR-*)
- R-MIRROR-001 «block.ux-substrates ↔ interface той же поверхности»: ...

### Правила семантики (R-SEM-*)
- ...

### Правила coverage (R-COV-*)
- ...

## Поверхность <surface-2>
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
  (`docs/projects/<project-slug>/interface/<surface>/`) правками.** Если
  interface ссылка битая — это `interface-deep-dive`. Если зеркало
  `ux-substrates` расходится — отчёт указывает оба слоя той же
  поверхности, но решение источника правды делает аналитик через
  `screen-deep-dive`.
- **Не смешивать проекты.** Аудит скоупится в один `<project-slug>`;
  межпроектные несостыковки — предмет `/cross-audit`, не этот скилл.
- **Не смешивать поверхности.** Каждая папка `screens/<surface>/`
  аудитится в своих границах: ссылки внутри screens и зеркала с
  interface разрешаются только в пределах той же поверхности; ссылка в
  чужую поверхность — error (R-XSURF-001). Кросс-поверхностную сверку
  делает `/cross-audit`, не этот скилл.
- **Не аккумулировать историю** в `audit-state/`. Перезаписывать
  `last-report.md` каждый прогон.
- **Не реализовывать suppressions.** В отличие от `/cross-audit`,
  `/swot-audit` и `/hypothesis-map-audit` (семантические findings, бывают
  ложные), структурный аудит детерминирован — зеркало синхронно или нет,
  slot/fill валиден или нет. Ложных срабатываний не бывает, подавлять нечего.
- **Не запускать `screen-deep-dive`** автоматически из аудита. Это
  делает аналитик руками по выводу аудита.
- **Не аудитить `docs/projects/_template/screens/`** — это канон формы;
  из него читаются только критерии и инвентарь, не данные.
- **Не аудитить `state/<project-slug>/<surface>/<kind>/<slug>.md`** —
  рабочая память `screen-deep-dive`, не предмет screens-канона.
