---
name: screen-audit
description: "Аудит экранов кабинета в `docs/projects/<slug>/screens/<surface>/` по папке на поверхность: ссылки и зеркала с interface и продуктом, нотация дерева и компоненты из словаря, наборы состояний, карта экранов и маршрутов со сводом `map.md`, контракты блоков, реестр текстов и роли строк, доступность и узкий экран, облик и FSD-имена в артефактах. Только отчёт, правки — через `/screen-deep-dive`. Звать перед коммитом экранов, по предложению `/screen-deep-dive` в конце сессии или при подозрении на рассогласование; без `<project-slug>` — пикер, без `<surface>` — все поверхности."
---

# screen-audit

Аудит консистентности экранов **одной поверхности** проекта в
`docs/projects/<project-slug>/screens/<surface>/`: четыре kind (flow ·
screen · block · shell), свод карты экранов `map.md` и реестр текстов
интерфейса `texts.md`. Канон формы —
`docs/projects/_template/screens/README.md` и файлы-формы в подпапке
`_template/`. Аудит **читает и сообщает**, ничего не правит: каскадные
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
| `/screen-audit …` (без slug) | `AskUserQuestion`-пикер **по именам** проектов (исключая `_template` и `infrastructure`); затем все поверхности |

1. Если первый аргумент совпадает с именем подпапки `docs/projects/`
   (кроме `_template` и `infrastructure`) — это `<project-slug>`. Иначе — пикер **по
   именам** проектов (исключить `_template` и `infrastructure`). Если проектов нет —
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
| `/screen-audit <project-slug> <surface> map` | свод и решения `map.md` против экранов |
| `/screen-audit <project-slug> <surface> texts` | реестр `texts.md` против ключей деревьев |

`kind` ∈ {`flow`, `screen`, `block`, `shell`}.
`<kind>` и `<kind>:<slug>` требуют заданной `<surface>` (kind живёт в
конкретной поверхности).

## Что аудит читает

- Рабочая зона:
  `docs/projects/<project-slug>/screens/<surface>/{flows,screens,blocks,shells}/*/index.md`,
  `map.md` и `texts.md` поверхности.
- Соседи: `docs/projects/<project-slug>/screens/<surface>/assets/<kind>/<slug>/`
  (для проверки asset-файлов).
- Зеркала и ссылки interface **той же поверхности**:
  `docs/projects/<project-slug>/interface/<surface>/{who,situation,scenario,zone,block,ux-substrate,data-items}.md`.
- Продуктовый слой того же проекта: `object.md`, `action.md`,
  `capability/<surface>.md`, разделы `MVP` и `Devices and accessibility`
  `vision.md`.
- Реестр-хребет `docs/projects/<project-slug>/surface.md` — перечень
  поверхностей (для R-SURF).
- Словарь компонентов `../design-deep-dive/kb/common/components.yaml` и
  расширения словаря проекта — раздел `extensions`
  `docs/projects/<project-slug>/design/system.yaml`.

Узлы `ui:` сверяются со словарём и расширениями, атрибуты — с закрытым
списком канона, ключи `states` — со словарём состояний экрана
(производный YAML
`../design-deep-dive/kb/ux/06-feedback-states-motion/screen-states.yaml`),
ключи `text:` — с реестром; имена `icon:` сверяет слой дизайна. Разбор
дерева, наборы состояний и свод `map.md` считают утилиты раздела
`project` скилла дизайна — `tree`, `states`, `screen_map`:
`check <project-slug> [<surface>] --json` печатает строки находок с
правилом этого реестра, код 1 — есть `error`
(`../design-deep-dive/scripts/README.md § project`); реестр текстов
проверяет линтер `copy_lint.py texts.md` в жанре `interface`. Какие
правила считают утилиты, а какие остаются чтением, — вступление
`references/rules.md`. Когда окружения нет, аудит проверяет то же
чтением по канону, а в отчёте — строка «утилиты не запускались».

**Чего аудит не читает**:

- Другие проекты `docs/projects/<other-slug>/` — аудит скоупится в
  один проект; межпроектные несостыковки ловит `/cross-audit`.
- Другие поверхности того же проекта при разрешении ссылок — каждая
  папка `screens/<surface>/` аудитится в своих границах; ссылка в чужую
  поверхность — error (R-XSURF-001), а кросс-поверхностную сверку делает
  `/cross-audit`.
- `docs/projects/_template/screens/` — это канон формы, не рабочая зона.
  Из него читаются только критерии и anti-patterns, не данные.
- `../entrypoint/state/projects/<project-slug>/screens/<surface>/<kind>/<slug>.md`
  — рабочая память скилла `screen-deep-dive` в едином дереве state
  оркестратора; аудит её не трогает.

## Что делать при запуске

1. Определить `<project-slug>` и (опц.) `<surface>` (см. «Выбор проекта
   и поверхности»).
2. Прочитать канон `docs/projects/_template/screens/README.md` и
   файлы-формы `_template/{flow,screen,block,shell,map,texts}.md` —
   освежить нотацию дерева, словарь состояний и обязательный набор,
   контракты блоков, тексты интерфейса, доступность и узкий экран,
   anti-patterns, форму frontmatter.
3. Прочитать `references/rules.md` — реестр проверок с тяжестью.
4. Прочитать реестр `docs/projects/<project-slug>/surface.md`. Сверить
   с подпапками `docs/projects/<project-slug>/screens/`: папка вне
   реестра — error (R-SURF-001), поверхность маршрута приложения без
   папки screens — hint (R-SURF-002), папка у сайта, лендинга, бота или
   мобильного приложения — error (R-SURF-003).
5. Для каждой папки поверхности из scope (одна заданная `<surface>` или
   все) прочитать её рабочую зону
   `docs/projects/<project-slug>/screens/<surface>/` (или подмножество
   по args). Прогнать правила **в пределах этой поверхности**: сначала
   утилиты (`tree`, `states`, `screen_map` — `check --json`; реестр —
   `copy_lint.py texts.md`), затем правила чтением; собрать findings.
6. Сгруппировать по поверхности, внутри — по сущности; отсортировать по
   severity внутри.
7. Вывести отчёт в чат.
8. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | Невалидная ссылка, в том числе в продуктовый слой и реестр текстов; дубликат `slug`; `slug` папки ≠ `slug` во frontmatter; дерево не парсится; `ui:` вне словаря и расширений; ключ `states` вне словаря; `screen` ссылается на слот, не объявленный в shell; нарушение `accepts`; рассинхрон зеркал; поле вне перечня; маршрут вне реестра; роль строки ≠ роль части компонента; ошибка тостом; два главных действия на экране; не один `main` у каркаса; папка поверхности вне реестра `surface.md`; ссылка из папки одной поверхности в сущность другой |
| `warning` | Семантическое подозрение, рискует смыслом | Облик/оси контекста/breakpoints/FSD-имена в дереве; атрибут вне закрытого списка; inline-cтейты в `block.tree`; `screen.situations` не покрывает ситуации экрана; пустой обязательный слот, непокрытый набор состояний, неполный контракт блока, тупик — у черновика; переход без обратного пути; `hidden` без другого пути; частое действие только в меню |
| `hint` | Coverage / стиль, не ломает | shell без screens; block без потребителей; screen недостижим у черновика; stable ссылается на draft; литерал текста у черновика; строка реестра без ключа; короткое `description`; поверхность реестра без папки screens |

Подробный реестр — `references/rules.md`.

## Stable как ужесточение

Часть правил повышают severity при `status: stable` записи (у `map.md` —
при stable самого свода):

- пустой обязательный слот frontmatter, непокрытый обязательный набор
  состояний, неполный контракт формы или коллекции без объёма, тупик,
  список без состояния в адресе, не один заголовок экрана, master-detail
  без мобильного потока, основной каркас без состояний приложения:
  `warning` (draft) → `error` (stable);
- экран недостижим от стартового экрана роли, литерал текста в дереве:
  `hint` (draft) → `error` (stable);
- `block.tree` не содержит узла для объявленного `ux-substrate`,
  коллекция без способа на узком экране: `hint` (draft) → `warning`
  (stable);
- `map.md`: свод расходится с экранами, нет «Перехода», конвенций
  доступности, строк «Узкого экрана», решения о мобильном — `warning` →
  `error`; решение без основания — `hint` → `error`.

Это потому, что для stable канон требует одновременно ✅ всех 6 пунктов
`../screen-deep-dive/references/draft-stable.md`. На draft те же дыры —
ожидаемое незаконченное состояние. Точная тяжесть каждого правила — в
`references/rules.md`.

## Формат отчёта

В чат:

```
=== /screen-audit <project-slug> ===
Поверхностей в scope: K (web-clinic, web-admin). Прочитано: 4 kind × K, N записей.

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

[error] web-clinic / block:studies-list → R-STRUCT-021: `ui:Search` вне словаря — это имя из `aka` типа `SearchInput`.
  Что делать: заменить на ui:SearchInput через /screen-deep-dive <project-slug> web-clinic block:studies-list.

[warning] web-clinic / screen:studies-workspace → R-SEM-011: набор состояний не покрыт — нет `empty-filtered`
  (в блоке studies-list есть поиск).
  Что делать: дописать дельту или «не применимо: причина» через
  /screen-deep-dive <project-slug> web-clinic screen:studies-workspace.

[warning] web-clinic / block:studies-list → tree содержит `ui:Skeleton` (inline-state в block).
  Что делать: перенести в screen.states через /screen-deep-dive <project-slug> web-clinic screen:<потребитель>.

[hint] web-admin / shell:auth-shell → ни один screen не ссылается на этот shell.
  Что делать: завести screen с shell=auth-shell или удалить shell через
  /screen-deep-dive <project-slug> web-admin (каскадно).

Сводка: 5 error / 2 warning / 1 hint.
```

Пример — иллюстрация формы отчёта, а не данные проекта.

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

### Карта, контракты, тексты, доступность, узкий экран (R-RT-*, R-CP-*, R-TX-*, R-AX-*, R-MB-*)
- ...

## Поверхность <surface-2>
- ...
```

## Что не делать

- **Только отчёт.** Артефакты правит `screen-deep-dive`; аудит его не
  запускает — это делает аналитик по выводу аудита.
- **Не понижать `stable → draft`.** Максимум — hint «возможно,
  понизить?» в отчёте.
- **Не выдумывать findings.** Если правило не сработало — не писать
  «возможно, тут что-то не так на всякий случай».
- **Interface-слой — только читать.** Битая interface-ссылка чинится в
  `interface-deep-dive`. При расхождении зеркала `ux-substrates` отчёт
  указывает оба слоя той же поверхности, а источник правды выбирает
  аналитик через `screen-deep-dive`.
- **Без suppressions.** Структурные правила детерминированы — зеркало
  синхронно или нет, slot/fill валиден или нет. Подозрения R-SEM аналитик
  может объяснить в диалоге, и ответ снимает их в этом прогоне, но отчёт
  их не подавляет: следующий прогон вправе сработать снова (в отличие от
  `/cross-audit`, `/swot-audit` и `/hypothesis-map-audit`, которые ведут
  suppressions).
