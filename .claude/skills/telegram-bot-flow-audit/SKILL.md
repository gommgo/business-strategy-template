---
name: telegram-bot-flow-audit
description: "Аудит консистентности артефактов композиции телеграм-бота проекта в `docs/projects/<project-slug>/telegram-bot-flow/<surface>/` — по папке на bot-поверхность из реестра `surface.md`, внутри неё по фичам (dialog · window · use-case бота в `features/<feature>/`; command · notification на корне). Битые slug-рефы (внутри фичи, в interface той же поверхности), невалидные enum (`launch-mode`, `stack`, `widget`, `source`), рассинхрон зеркал (`dialog.transitions` ↔ `transition` виджетов окон, `window.ux-substrates` ↔ interface `block.ux-substrates`, `dialog.windows` ↔ окна фичи), разрывы графа (окно-сирота, тупик, диалог без `started-by`, недостижимое окно, матрёшка `start:` без `done`, дубль `states-group`/`state`/`operation`/`id`), контракты данных (плейсхолдер без getter, ключ без `fallback`, несериализуемое в `dialog-data`), оркестрация (`widget.action`/`getter.source` на несуществующий use-case бота фичи, bot UC без `Dependencies` и стейта, осиротевший use-case), Telegram-инварианты (`/start` без `stack: reset`, команда-шаг, уведомление без `idempotency`, клавиатура-сценарий), семантические подозрения (бизнес-правило в `when`/`Steps`, bot UC `Dependencies` на отсутствующий доменный use-case, `trigger` на отсутствующее событие домена, облик/код в артефактах), coverage-дыры (блок interface без окна, реестр команд без `/start`, deep-link только в тексте уведомления), папка поверхности вне реестра или для `type ≠ bot`, ссылка из одной поверхности в другую, из одной фичи в чужую минуя `start:`/`command`. Не правит артефакты, только указывает; деструктивные правки — через `telegram-bot-flow-deep-dive`. Использовать перед коммитом артефактов слоя, после сессии `telegram-bot-flow-deep-dive` (скилл предлагает прогон в конце), при подозрении на рассинхрон зеркал или разрыв графа диалогов, или перед `/cross-audit`, если трогали bot-поверхность. Принимает `<project-slug>` первым аргументом; без него — пикер по проектам. Без `<surface>` — прогон по всем bot-поверхностям; с `<surface>` — одна. Полный прогон по 5 kind — без kind-аргумента; узкий — `<kind>` или `<kind>:<slug>`."
---

# telegram-bot-flow-audit

Аудит консистентности 5 артефактных kind композиции телеграм-бота **одной
bot-поверхности** проекта в
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/` (dialog ·
window · use-case бота — в фичах; command · notification — на корне). Канон
формы — `docs/projects/_template/telegram-bot-flow/README.md`, канон фичи в
подпапке `_template/features/README.md` (dialog · window · use-case) и
табличные каноны `_template/command.md`, `_template/notification.md`. Аудит
**читает и сообщает**, ничего не правит: каскадные правки идут через
`telegram-bot-flow-deep-dive`.

Слой партиционирован по поверхности (surface): на каждую поверхность с
`type: bot` из реестра `docs/projects/<project-slug>/surface.md` — своя
папка `telegram-bot-flow/<surface>/` с реестрами корня (`command.md`,
`notification.md`) и папкой `features/`, где каждая фича — `features/<feature>/`
из трёх файлов (`dialog.md` — один диалог; `window.md` — все окна
H2-секциями `## <window-slug>`; `use-case.md` — все use-case'ы бота
H2-секциями `## <uc-slug>`) и `assets/`. **Изоляция двухуровневая**: ссылки
внутри `telegram-bot-flow/<surface>/` и зеркала с `interface/<surface>/` —
**в пределах одной поверхности**, а внутри поверхности внутри-фичевые рёбра
(`window` ↔ `dialog` ↔ `use-case`) — **в пределах одной фичи**. Аудит
итерирует **по каждой папке поверхности** независимо, внутри неё — **по
каждой фиче**.

Аудит работает **в контексте одного проекта** (см. «Выбор проекта и
поверхности»). Дальше по тексту `<project-slug>` — выбранный проект,
`<surface>` — поверхность (одна или все bot-поверхности).

## Выбор проекта и поверхности

Аргументы позиционны — `<project-slug>` первый, `<surface>` второй
(опционален):

| вызов | проект · поверхность |
|---|---|
| `/telegram-bot-flow-audit <project-slug> <surface> …` | взять `<project-slug>` и `<surface>` |
| `/telegram-bot-flow-audit <project-slug> …` (без surface) | проект задан; **все** bot-поверхности проекта |
| `/telegram-bot-flow-audit …` (без slug) | `AskUserQuestion`-пикер **по именам** проектов (исключая `_template`); затем все bot-поверхности |

1. Если первый аргумент совпадает с именем подпапки `docs/projects/`
   (кроме `_template`) — это `<project-slug>`. Иначе — пикер **по
   именам** проектов (исключить `_template`). Если проектов нет —
   сказать «нечего аудитить», выйти.
2. Прочитать реестр `docs/projects/<project-slug>/surface.md`. Если
   следующий аргумент совпадает со `slug` строки реестра — это
   `<surface>` (одна поверхность), остаток args — scope. Если аргумента
   нет — поверхности **все** с `type: bot` (плюс каждая существующая
   папка `telegram-bot-flow/<X>/` — даже если `X` нет в реестре или
   `type` не `bot`: такие папки попадают в scope ради R-SURF-001/002).
   Внутри папки поверхности фичи берутся из `features/` целиком.
3. Все чтения скоупятся в
   `docs/projects/<project-slug>/telegram-bot-flow/<surface>/` (одну или
   каждую), зеркала `docs/projects/<project-slug>/interface/<surface>/`,
   read-only контекст `docs/projects/<project-slug>/services/*/domains/` и
   `audit-state/<project-slug>/`.

## Точки входа

После того как `<project-slug>` и (опц.) `<surface>` определены, остаток
args задаёт scope:

| вызов | поведение |
|---|---|
| `/telegram-bot-flow-audit <project-slug>` | полный прогон всех 5 kind в каждой папке bot-поверхности |
| `/telegram-bot-flow-audit <project-slug> <surface>` | полный прогон всех 5 kind одной поверхности |
| `/telegram-bot-flow-audit <project-slug> <surface> <kind>` | прогон одного kind поверхности + перекрёстные ссылки внутри неё |
| `/telegram-bot-flow-audit <project-slug> <surface> <kind>:<slug>` | одна запись + соседи по ссылкам внутри её фичи (её окна/use-case'ы, входы) |

`kind` ∈ {`dialog`, `window`, `use-case`, `command`, `notification`}. Для
`dialog` `<slug>` — имя папки фичи в `features/` (= slug её диалога); для
`window`/`use-case` `<slug>` — заголовок H2-секции `## <slug>` в `window.md`/
`use-case.md` фичи; для `command`/`notification` — `slug` строки таблицы
корня. `<kind>` и `<kind>:<slug>` требуют заданной `<surface>` (kind живёт
в конкретной поверхности, а внутри-фичевые — в конкретной фиче).

## Что аудит читает

- Рабочая зона:
  `docs/projects/<project-slug>/telegram-bot-flow/<surface>/` — корневые
  реестры `command.md`, `notification.md` и фичи
  `features/<feature>/{dialog.md, window.md, use-case.md}` (окна и
  use-case'ы — H2-секциями `## <slug>`).
- Соседи: `…/telegram-bot-flow/<surface>/features/<feature>/assets/<slug>/`
  (для проверки media-референсов).
- Зеркала interface **той же поверхности**:
  `docs/projects/<project-slug>/interface/<surface>/{who,situation,block,ux-substrate,data-items}.md`.
- Реестр-хребет `docs/projects/<project-slug>/surface.md` — перечень
  поверхностей и их `type` (для R-SURF).
- Read-only контекст для семантических углов:
  `docs/projects/<project-slug>/services/*/domains/<ctx>/{use-cases,events}/`
  (по всем сервисам — контекст уникален в проекте, сервис-владелец
  выводится из пути) — существует ли доменный use-case из `Dependencies`
  use-case'а бота и событие из `notification.trigger`;
  `docs/projects/<project-slug>/integration.md` — для
  `trigger: integration:<slug>`. Домен может ещё не существовать: bot UC
  опираются на его use-case'ы, но отсутствие домена — подозрение, не
  ошибка модели.

**Чего аудит не читает**:

- Другие проекты `docs/projects/<other-slug>/` — аудит скоупится в один
  проект; межпроектные несостыковки ловит `/cross-audit`.
- Другие поверхности того же проекта при разрешении ссылок — каждая папка
  `telegram-bot-flow/<surface>/` аудитится в своих границах; ссылка в
  чужую поверхность — error (R-XSURF-001), а кросс-поверхностную сверку
  (включая словарь данных) делает `/cross-audit`.
- Другие фичи той же поверхности при разрешении внутри-фичевых ссылок —
  каждая фича `features/<feature>/` аудитится в своих границах; ссылка из
  фичи в окно/use-case чужой фичи минуя `start:`/`command`/`feature:` —
  error (R-XFEAT-001). Общее между фичами сводит корневые реестры и
  `/cross-audit`.
- `docs/projects/_template/telegram-bot-flow/` — это канон формы, не
  рабочая зона. Из него читаются только критерии, enum'ы и anti-patterns,
  не данные.
- `services/` — правками: домены сервисов (`services/*/domains/`)
  читаются только как контекст «существует ли адресат рефа»; глубину
  сверки payload событий с плейсхолдерами `content` ведёт `/cross-audit`
  (углы `botflow-domain` · `botflow-service`), проектирование домена —
  `/domain-deep-dive`.
- Код-репо бота (форк `telegram-bot-template`) — слой кода, не предмет
  этого аудита.
- `state/…` скилла `telegram-bot-flow-deep-dive` — рабочая память другого
  скилла; аудит её не трогает.

## Что делать при запуске

1. Определить `<project-slug>` и (опц.) `<surface>` (см. «Выбор проекта и
   поверхности»).
2. Прочитать канон `docs/projects/_template/telegram-bot-flow/README.md`,
   канон фичи `_template/features/README.md` (dialog · window · use-case)
   и табличные каноны `_template/command.md`, `_template/notification.md` —
   освежить виджет-язык, форму getter'а, форму секции use-case бота,
   инварианты модели Telegram, anti-patterns.
3. Прочитать `references/rules.md` — реестр проверок с тяжестью.
4. Прочитать реестр `docs/projects/<project-slug>/surface.md`. Сверить с
   подпапками `docs/projects/<project-slug>/telegram-bot-flow/`: папка вне
   реестра — error (R-SURF-001), папка для поверхности с `type ≠ bot` —
   error (R-SURF-002), bot-поверхность реестра без папки — hint
   (R-SURF-003).
5. Для каждой папки поверхности из scope прочитать её рабочую зону (или
   подмножество по args): корневые реестры и фичи `features/<feature>/`.
   Прогнать структурные и зеркальные правила **в пределах этой
   поверхности**, внутри-фичевые рёбра — **в пределах каждой фичи**,
   собрать findings.
6. Прогнать семантические углы (R-SEM) и coverage (R-COV) — это **чтение
   и смысловой разбор**, не grep: сопоставить `Dependencies` use-case'ов
   бота с use-case доменов, `trigger` — с событиями, `widget.action`/
   `getter.source` — с use-case'ами бота фичи, окна — с блоками и
   ситуациями interface, тексты и `Steps` — с anti-patterns облика/кода/
   бизнес-правил. Спорное — флагом «подозрение», не приговором.
7. Сгруппировать по поверхности, внутри — по фиче и сущности; отсортировать
   по severity внутри.
8. Вывести отчёт в чат.
9. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | Битый slug-реф; `transition` на окно чужой фичи; `widget.action`/`getter.source` на несуществующий use-case бота фичи; дубль `slug`/`states-group`/`state`/`operation`/`id`; `launch-mode`/`stack`/`widget`/`source`/`status` вне enum; рассинхрон зеркал (`dialog.transitions` ↔ виджеты, `ux-substrates` ↔ interface, `windows` ↔ окна фичи); плейсхолдер без ключа getter; ключ getter без `fallback`; `/start` без `stack: reset`; уведомление без `idempotency`; тупиковое окно; диалог без `started-by`; папка поверхности вне реестра или для `type ≠ bot`; ссылка из одной поверхности в другую; ссылка из одной фичи в чужую минуя `start:`/`command`/`feature:` |
| `warning` | Семантическое подозрение, рискует смыслом | Бизнес-правило в `when` или в `Steps` use-case бота; bot UC `Dependencies` на доменный use-case, которого нет в `services/*/domains/`; bot UC без `Dependencies` и без работы со стейтом (чистая навигация — это transition); `trigger: event:…` на событие, которого нет в `services/*/domains/`; команда-шаг (`/next`); клавиатура-сценарий в уведомлении; несериализуемое в `dialog-data`; облик (HTML, эмодзи-оформление как требование) или код (`.ftl`-ключи, python-имена) в артефакте; окно без соотносимой ситуации; окно-сирота; матрёшка `start:` без `done`; пустой обязательный слот draft-записи; deep-link только в тексте уведомления |
| `hint` | Coverage / стиль, не ломает | Блок interface bot-поверхности без окна (дыра синтеза); use-case бота, на который не ссылается ни один `widget.action`/`getter.source` фичи (осиротевшая оркестрация); bot-поверхность реестра без папки слоя; stable ссылается на draft; реестр команд без `/start` при живых фичах |

Подробный реестр — `references/rules.md`.

## Stable как ужесточение

Часть правил повышают severity при `status: stable`:

- пустой обязательный слот frontmatter / колонки: `warning` (draft) →
  `error` (stable);
- окно без `errors` (нет ни `backend-unavailable`, ни `invalid-input`,
  хотя бы как `—`): `hint` (draft) → `warning` (stable);
- недостижимое окно (входящие есть, но цепочка от первого окна не
  доходит): `warning` (draft) → `error` (stable).

Это потому, что stable-артефакты слоя читает код-репо бота (форк
`telegram-bot-template`) — дыра в stable уезжает в генерацию кода. На
draft те же дыры — ожидаемое незаконченное состояние. Битые рефы и
рассинхрон зеркал — `error` независимо от `status`.

## Семантические углы — разбор, не grep

Правила R-SEM и R-COV не сводятся к сличению строк:

- `widget.action`/`getter.source` указывают на use-case бота фичи
  (`use-case:<uc-slug>` **без точки**) — это slug-валидируемое ребро
  внутри фичи (R-STRUCT-020). А вот `Dependencies` use-case'а бота
  сверяются с `services/*/domains/<ctx>/use-cases/` **по смыслу
  адресации**
  (контекст и операция существуют — `use-case:<ctx>.<Operation>` **с
  точкой**), и `when` — на «исход use-case бота, не правило окна»:
  «use-case вернул „нужен адрес“» — норма, «если сумма > 1000» —
  подозрение на доменное решение в окне; такое же бизнес-правило в
  `Steps` use-case'а бота — подозрение на правило в оркестраторе.
- Соотнесение окна с ситуациями и блоком interface — смысловая рифма
  (окно реализует блок, виджеты соотносимы с атомами), не равенство строк.
- Coverage-дыры (блок без окна, deep-link без команды, осиротевший
  use-case бота) выводятся чтением соседних файлов фичи целиком, не grep'ом
  по одному.

Срабатывание R-SEM — «подозрение, проверь»: аналитик имеет право объяснить
«нет, это осознанно», и подтверждённый warning не превращается в правку.

## Формат отчёта

В чат:

```
=== /telegram-bot-flow-audit <project-slug> ===
Bot-поверхностей в scope: K (tg-client-bot), фич: F. Прочитано: 5 kind, N записей.

[error] tg-client-bot / папка слоя есть, а поверхности нет в реестре surface.md.
  Что делать: завести строку в surface.md через /project-deep-dive <project-slug>,
  либо удалить папку telegram-bot-flow/<surface>/.

[error] tg-client-bot / booking / dialog → невалидная ссылка windows[2] = `addres`
  (нет секции ## addres в window.md этой фичи).
  Что делать: исправить опечатку или завести окно через
  /telegram-bot-flow-deep-dive <project-slug> tg-client-bot window:addres.

[error] tg-client-bot / booking / dialog → transitions расходится с transition виджетов окон:
  сводка содержит { from: guests, to: confirm }, но ни один виджет окна `guests` туда не ведёт.
  Что делать: пересинхронизировать через /telegram-bot-flow-deep-dive <project-slug> tg-client-bot
  dialog:booking (источник правды — transition виджетов).

[error] tg-client-bot / booking / window:services → action = `use-case:submit-draft`
  не находит секции ## submit-draft в use-case.md этой фичи.
  Что делать: завести use-case бота или поправить реф через
  /telegram-bot-flow-deep-dive <project-slug> tg-client-bot window:services.

[error] tg-client-bot / booking / window:services → плейсхолдер {selected_summary} в message.text
  не обеспечен ключом getter.
  Что делать: добавить ключ getter с source и fallback через
  /telegram-bot-flow-deep-dive <project-slug> tg-client-bot window:services.

[error] tg-client-bot / command:start-menu → `/start` со `stack: push`.
  Что делать: поставить stack: reset через /telegram-bot-flow-deep-dive <project-slug>
  tg-client-bot command:start-menu — вход всегда сбрасывает стек.

[warning] tg-client-bot / booking / use-case:submit-booking → Steps содержит «если гостей > 8 —
  отказать» — бизнес-правило в оркестраторе, не вызов домена.
  Что делать: перенести правило в доменный use-case через /domain-deep-dive <project-slug> booking,
  а bot UC оставить маршрутизацию исхода через
  /telegram-bot-flow-deep-dive <project-slug> tg-client-bot use-case:submit-booking.

[warning] tg-client-bot / booking / use-case:submit-booking → Dependencies ссылается на
  use-case:booking.CreateOrder, которого нет в services/*/domains/booking/use-cases/.
  Что делать: спроектировать use-case через /domain-deep-dive <project-slug> booking,
  либо поправить реф (домен опционален — если осознанно, объяснить).

[hint] tg-client-bot / booking / interface-блок `loyalty-status` не реализован ни одним окном (дыра синтеза).
  Что делать: завести окно через /telegram-bot-flow-deep-dive <project-slug> tg-client-bot window,
  либо это сознательно отложено.

Сводка: 6 error / 2 warning / 1 hint.
```

Группировка — по поверхности, внутри — по фиче, внутри фичи — по сущности;
в пределах сущности — `error → warning → hint`. Для табличных kind корня
(command, notification) к finding'у добавляется `файл:строка` таблицы; для
dialog — путь к `features/<feature>/dialog.md`; для window/use-case — путь
к `features/<feature>/window.md`/`use-case.md` и заголовок секции
`## <slug>` (и строка, когда нарушение точечное).

## `audit-state/<project-slug>/last-report.md`

Отчёт лежит **рядом со скиллом**, не в
`docs/projects/<project-slug>/telegram-bot-flow/` и не в корне проекта, и
скоупится по проекту:

```
.claude/skills/telegram-bot-flow-audit/audit-state/<project-slug>/last-report.md
```

Дальше по тексту скилла — короткое `audit-state/`, это сокращение того же
пути (с учётом текущего `<project-slug>`).

После каждого прогона перезаписывается одним файлом с reasoning-trace:
какие правила запускал, какие записи проверил, что нашёл, почему. Это не
журнал — следующий прогон перезатирает. В git, чтобы команда могла читать.

Структура:

```markdown
---
project: <project-slug>
ran-on: <scope: all-surfaces | surface | surface kind | surface kind:slug>
surfaces: [<surface-1>]
features: [<surface-1>/<feature-1>]
kinds-read: 5 × surfaces
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила хребта (R-SURF-*)
- R-SURF-001 «папка поверхности вне реестра»: сверил подпапки
  telegram-bot-flow/ с surface.md — лишних нет.
- R-SURF-002 «папка для surface с type ≠ bot»: ...

## Поверхность <surface-1>

### Изоляция фич (R-XFEAT-*)
- R-XFEAT-001 «ссылка из фичи в чужую минуя start:/command»: ...

### Фича <feature-1>

#### Правила структуры (R-STRUCT-*)
- R-STRUCT-011 «dialog.windows → окна фичи»: проверил M ссылок, нашёл K битых.
  - dialog:booking.windows[2] = `addres` → нет секции ## addres в window.md → error.
- R-STRUCT-020 «widget.action/getter.source → use-case бота фичи»: ...
...

#### Правила зеркал (R-MIRROR-*)
- R-MIRROR-001 «dialog.transitions ↔ transition виджетов»: ...

#### Правила графа (R-GRAPH-*)
- ...

#### Правила данных (R-DATA-*)
- ...

#### Telegram-инварианты (R-TG-*)
- ...

#### Правила семантики (R-SEM-*)
- ...

#### Правила coverage (R-COV-*)
- ...
```

## Что не делать

- **Не править артефакты.** Аудит — только отчёт. Все правки — через
  `telegram-bot-flow-deep-dive`.
- **Не понижать `stable → draft`.** Максимум — hint «возможно, понизить?»
  в отчёте.
- **Не выдумывать findings.** Если правило не сработало — не писать
  «возможно, тут что-то не так на всякий случай».
- **Не лезть правками в interface-слой
  (`docs/projects/<project-slug>/interface/<surface>/`).** Если
  interface-ссылка битая — это `interface-deep-dive`. Если зеркало
  `ux-substrates` расходится — отчёт указывает оба слоя той же
  поверхности, но решение источника правды делает аналитик через
  `telegram-bot-flow-deep-dive`.
- **Не лезть в `services/`.** Домены сервисов (`services/*/domains/`)
  читаются read-only как контекст адресации доменного `Dependencies`
  use-case'а бота (`use-case:<ctx>.<Operation>`)
  и `event:…`; отсутствие адресата — warning в отчёте, заведение
  use-case/события — `/domain-deep-dive`, не этот скилл.
- **Не смешивать проекты.** Аудит скоупится в один `<project-slug>`;
  межпроектные несостыковки — предмет `/cross-audit`, не этот скилл.
- **Не смешивать поверхности.** Каждая папка `telegram-bot-flow/<surface>/`
  аудитится в своих границах: ссылки внутри слоя и зеркала с interface
  разрешаются только в пределах той же поверхности; ссылка в чужую
  поверхность — error (R-XSURF-001). Кросс-поверхностную сверку (включая
  словарь данных и payload событий) делает `/cross-audit`.
- **Не смешивать фичи.** Внутри поверхности каждая фича
  `features/<feature>/` аудитится в своих границах: внутри-фичевые рёбра
  (`window` ↔ `dialog` ↔ `use-case`) разрешаются только среди записей своей
  фичи; ссылка из фичи в окно/use-case чужой фичи минуя
  `start:`/`command`/`feature:` — error (R-XFEAT-001). Общее между фичами
  сводят корневые реестры и `/cross-audit`.
- **Не аккумулировать историю** в `audit-state/`. Перезаписывать
  `last-report.md` каждый прогон.
- **Не превращать семантический warning в правку без аналитика.** R-SEM —
  подозрения; аналитик может объяснить «это осознанно», и ответ снимает
  подозрение в этом прогоне. Suppressions при этом не ведутся: следующий
  прогон вправе сработать снова.
- **Не запускать `telegram-bot-flow-deep-dive`** автоматически из аудита.
  Это делает аналитик руками по выводу аудита.
- **Не аудитить `docs/projects/_template/telegram-bot-flow/`** — это канон
  формы; из него читаются только критерии, enum'ы и anti-patterns, не
  данные.
