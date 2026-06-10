---
name: telegram-bot-flow-audit
description: "Аудит консистентности артефактов композиции телеграм-бота проекта в `docs/projects/<project-slug>/telegram-bot-flow/<surface>/` — по папке на bot-поверхность из реестра `surface.md` (dialog · window · command · notification). Битые slug-рефы (внутри слоя, в interface той же поверхности), невалидные enum (`launch-mode`, `stack`, `widget`, `source`), рассинхрон зеркал (`dialog.transitions` ↔ `transition` виджетов окон, `window.ux-substrates` ↔ interface `block.ux-substrates`, `dialog.windows` ↔ `window.dialog`), разрывы графа (окно-сирота, тупик, диалог без `started-by`, недостижимое окно, матрёшка `start:` без `done`, дубль `states-group`/`state`/`id`), контракты данных (плейсхолдер без getter, ключ без `fallback`, несериализуемое в `dialog-data`), Telegram-инварианты (`/start` без `stack: reset`, команда-шаг, уведомление без `idempotency`, клавиатура-сценарий), семантические подозрения (бизнес-правило в `when`, `action` мимо use-case, `trigger` на отсутствующее событие домена, облик/код в артефактах), coverage-дыры (блок interface без окна, реестр команд без `/start`, deep-link только в тексте уведомления), папка поверхности вне реестра или для `type ≠ bot`, ссылка из одной поверхности в другую. Не правит артефакты, только указывает; деструктивные правки — через `telegram-bot-flow-deep-dive`. Использовать перед коммитом артефактов слоя, после сессии `telegram-bot-flow-deep-dive` (скилл предлагает прогон в конце), при подозрении на рассинхрон зеркал или разрыв графа диалогов, или перед `/cross-audit`, если трогали bot-поверхность. Принимает `<project-slug>` первым аргументом; без него — пикер по проектам. Без `<surface>` — прогон по всем bot-поверхностям; с `<surface>` — одна. Полный прогон по 4 kind — без kind-аргумента; узкий — `<kind>` или `<kind>:<slug>`."
---

# telegram-bot-flow-audit

Аудит консистентности 4 артефактных kind композиции телеграм-бота **одной
bot-поверхности** проекта в
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/` (dialog ·
window · command · notification). Канон формы —
`docs/projects/_template/telegram-bot-flow/README.md` и канон каждого kind
в подпапке `_template/` (`dialogs/README.md`, `windows/README.md`,
`command.md`, `notification.md`). Аудит **читает и сообщает**, ничего не
правит: каскадные правки идут через `telegram-bot-flow-deep-dive`.

Слой партиционирован по поверхности (surface): на каждую поверхность с
`type: bot` из реестра `docs/projects/<project-slug>/surface.md` — своя
папка `telegram-bot-flow/<surface>/` с `dialogs/`, `windows/`,
`command.md`, `notification.md` и `assets/`. Все ссылки внутри
`telegram-bot-flow/<surface>/` и зеркала с `interface/<surface>/` — **в
пределах одной поверхности**. Аудит итерирует **по каждой папке
поверхности** независимо.

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
3. Все чтения скоупятся в
   `docs/projects/<project-slug>/telegram-bot-flow/<surface>/` (одну или
   каждую), зеркала `docs/projects/<project-slug>/interface/<surface>/`,
   read-only контекст `docs/projects/<project-slug>/domains/` и
   `audit-state/<project-slug>/`.

## Точки входа

После того как `<project-slug>` и (опц.) `<surface>` определены, остаток
args задаёт scope:

| вызов | поведение |
|---|---|
| `/telegram-bot-flow-audit <project-slug>` | полный прогон всех 4 kind в каждой папке bot-поверхности |
| `/telegram-bot-flow-audit <project-slug> <surface>` | полный прогон всех 4 kind одной поверхности |
| `/telegram-bot-flow-audit <project-slug> <surface> <kind>` | прогон одного kind поверхности + перекрёстные ссылки внутри неё |
| `/telegram-bot-flow-audit <project-slug> <surface> <kind>:<slug>` | одна запись + соседи по ссылкам внутри поверхности (её диалог/окна, её входы) |

`kind` ∈ {`dialog`, `window`, `command`, `notification`}. Для
`dialog`/`window` `<slug>` — имя папки в `dialogs/`/`windows/`; для
`command`/`notification` — `slug` строки таблицы. `<kind>` и
`<kind>:<slug>` требуют заданной `<surface>` (kind живёт в конкретной
поверхности).

## Что аудит читает

- Рабочая зона:
  `docs/projects/<project-slug>/telegram-bot-flow/<surface>/` —
  `dialogs/*/index.md`, `windows/*/index.md`, `command.md`,
  `notification.md`.
- Соседи: `…/telegram-bot-flow/<surface>/assets/<kind>/<slug>/` (для
  проверки media-референсов).
- Зеркала interface **той же поверхности**:
  `docs/projects/<project-slug>/interface/<surface>/{who,situation,block,ux-substrate,data-items}.md`.
- Реестр-хребет `docs/projects/<project-slug>/surface.md` — перечень
  поверхностей и их `type` (для R-SURF).
- Read-only контекст для семантических углов:
  `docs/projects/<project-slug>/domains/<ctx>/{use-cases,events}/` —
  существуют ли use-case из `action`/`getter.source` и событие из
  `notification.trigger`; `docs/projects/<project-slug>/integration.md` —
  для `trigger: integration:<slug>`.

**Чего аудит не читает**:

- Другие проекты `docs/projects/<other-slug>/` — аудит скоупится в один
  проект; межпроектные несостыковки ловит `/cross-audit`.
- Другие поверхности того же проекта при разрешении ссылок — каждая папка
  `telegram-bot-flow/<surface>/` аудитится в своих границах; ссылка в
  чужую поверхность — error (R-XSURF-001), а кросс-поверхностную сверку
  (включая словарь данных) делает `/cross-audit`.
- `docs/projects/_template/telegram-bot-flow/` — это канон формы, не
  рабочая зона. Из него читаются только критерии, enum'ы и anti-patterns,
  не данные.
- `domains/` — правками: домен читается только как контекст «существует ли
  адресат рефа»; глубину сверки payload событий с плейсхолдерами `content`
  ведёт `/cross-audit`, проектирование домена — `/domain-deep-dive`.
- Код-репо бота (форк `telegram-bot-template`) — слой кода, не предмет
  этого аудита.
- `state/…` скилла `telegram-bot-flow-deep-dive` — рабочая память другого
  скилла; аудит её не трогает.

## Что делать при запуске

1. Определить `<project-slug>` и (опц.) `<surface>` (см. «Выбор проекта и
   поверхности»).
2. Прочитать канон `docs/projects/_template/telegram-bot-flow/README.md`
   и каноны kind в подпапке `_template/` — освежить виджет-язык, форму
   getter'а, инварианты модели Telegram, anti-patterns.
3. Прочитать `references/rules.md` — реестр проверок с тяжестью.
4. Прочитать реестр `docs/projects/<project-slug>/surface.md`. Сверить с
   подпапками `docs/projects/<project-slug>/telegram-bot-flow/`: папка вне
   реестра — error (R-SURF-001), папка для поверхности с `type ≠ bot` —
   error (R-SURF-002), bot-поверхность реестра без папки — hint
   (R-SURF-003).
5. Для каждой папки поверхности из scope прочитать её рабочую зону (или
   подмножество по args). Прогнать структурные и зеркальные правила **в
   пределах этой поверхности**, собрать findings.
6. Прогнать семантические углы (R-SEM) и coverage (R-COV) — это **чтение
   и смысловой разбор**, не grep: сопоставить `action`/`getter.source` с
   use-case доменов, `trigger` — с событиями, окна — с блоками и
   ситуациями interface, тексты — с anti-patterns облика/кода. Спорное —
   флагом «подозрение», не приговором.
7. Сгруппировать по поверхности, внутри — по сущности; отсортировать по
   severity внутри.
8. Вывести отчёт в чат.
9. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | Битый slug-реф; `transition` на окно чужого диалога; дубль `slug`/`states-group`/`state`/`id`; `launch-mode`/`stack`/`widget`/`source`/`status` вне enum; рассинхрон зеркал (`dialog.transitions` ↔ виджеты, `ux-substrates` ↔ interface, `windows` ↔ `window.dialog`); плейсхолдер без ключа getter; ключ getter без `fallback`; `/start` без `stack: reset`; уведомление без `idempotency`; тупиковое окно; диалог без `started-by`; папка поверхности вне реестра или для `type ≠ bot`; ссылка из одной поверхности в другую |
| `warning` | Семантическое подозрение, рискует смыслом | Бизнес-правило в `when`; `action` не похож на `use-case:<ctx>.<Operation>`; `trigger: event:…` на событие, которого нет в `domains/`; команда-шаг (`/next`); клавиатура-сценарий в уведомлении; несериализуемое в `dialog-data`; облик (HTML, эмодзи-оформление как требование) или код (`.ftl`-ключи, python-имена) в артефакте; окно без соотносимой ситуации; окно-сирота; матрёшка `start:` без `done`; пустой обязательный слот draft-записи; deep-link только в тексте уведомления |
| `hint` | Coverage / стиль, не ломает | Блок interface bot-поверхности без окна (дыра синтеза); bot-поверхность реестра без папки слоя; stable ссылается на draft; реестр команд без `/start` при живых диалогах |

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

- `action`/`getter.source` сверяются с `domains/<ctx>/use-cases/` **по
  смыслу адресации** (контекст и операция существуют), а `when` — на
  «исход use-case, не правило окна»: «use-case вернул „нужен адрес“» —
  норма, «если сумма > 1000» — подозрение на доменное решение в окне.
- Соотнесение окна с ситуациями и блоком interface — смысловая рифма
  (окно реализует блок, виджеты соотносимы с атомами), не равенство строк.
- Coverage-дыры (блок без окна, deep-link без команды) выводятся чтением
  обоих файлов целиком, не grep'ом по одному.

Срабатывание R-SEM — «подозрение, проверь»: аналитик имеет право объяснить
«нет, это осознанно», и подтверждённый warning не превращается в правку.

## Формат отчёта

В чат:

```
=== /telegram-bot-flow-audit <project-slug> ===
Bot-поверхностей в scope: K (tg-client-bot). Прочитано: 4 kind × K, N записей.

[error] tg-client-bot / папка слоя есть, а поверхности нет в реестре surface.md.
  Что делать: завести строку в surface.md через /project-deep-dive <project-slug>,
  либо удалить папку telegram-bot-flow/<surface>/.

[error] tg-client-bot / dialog:booking → невалидная ссылка windows[2] = `addres` (нет в windows/ этой поверхности).
  Что делать: исправить опечатку или завести окно через
  /telegram-bot-flow-deep-dive <project-slug> tg-client-bot window:addres.

[error] tg-client-bot / dialog:booking → transitions расходится с transition виджетов окон:
  сводка содержит { from: guests, to: confirm }, но ни один виджет окна `guests` туда не ведёт.
  Что делать: пересинхронизировать через /telegram-bot-flow-deep-dive <project-slug> tg-client-bot
  dialog:booking (источник правды — transition виджетов).

[error] tg-client-bot / window:services → плейсхолдер {selected_summary} в message.text
  не обеспечен ключом getter.
  Что делать: добавить ключ getter с source и fallback через
  /telegram-bot-flow-deep-dive <project-slug> tg-client-bot window:services.

[error] tg-client-bot / command:start-menu → `/start` со `stack: push`.
  Что делать: поставить stack: reset через /telegram-bot-flow-deep-dive <project-slug>
  tg-client-bot command:start-menu — вход всегда сбрасывает стек.

[warning] tg-client-bot / window:guests → when = «если гостей больше 8 — показать предупреждение»
  читается как бизнес-правило окна, не исход use-case.
  Что делать: переформулировать как исход use-case:booking.SetGuests через
  /telegram-bot-flow-deep-dive <project-slug> tg-client-bot window:guests
  (правило живёт в домене; если домен его не знает — это разговор для /domain-deep-dive).

[hint] tg-client-bot / interface-блок `loyalty-status` не реализован ни одним окном (дыра синтеза).
  Что делать: завести окно через /telegram-bot-flow-deep-dive <project-slug> tg-client-bot window,
  либо это сознательно отложено.

Сводка: 5 error / 1 warning / 1 hint.
```

Группировка — по поверхности, внутри — по сущности; в пределах сущности —
`error → warning → hint`. Для табличных kind (command, notification) к
finding'у добавляется `файл:строка` таблицы; для dialog/window — путь к
`index.md` (и строка, когда нарушение точечное).

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
kinds-read: 4 × surfaces
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила хребта (R-SURF-*)
- R-SURF-001 «папка поверхности вне реестра»: сверил подпапки
  telegram-bot-flow/ с surface.md — лишних нет.
- R-SURF-002 «папка для surface с type ≠ bot»: ...

## Поверхность <surface-1>

### Правила структуры (R-STRUCT-*)
- R-STRUCT-011 «dialog.windows → windows/»: проверил M ссылок, нашёл K битых.
  - dialog:booking.windows[2] = `addres` → нет в windows/ → error.
...

### Правила зеркал (R-MIRROR-*)
- R-MIRROR-001 «dialog.transitions ↔ transition виджетов»: ...

### Правила графа (R-GRAPH-*)
- ...

### Правила данных (R-DATA-*)
- ...

### Telegram-инварианты (R-TG-*)
- ...

### Правила семантики (R-SEM-*)
- ...

### Правила coverage (R-COV-*)
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
- **Не лезть в `domains/`.** Домен читается read-only как контекст
  адресации (`use-case:…`, `event:…`); отсутствие адресата — warning в
  отчёте, заведение use-case/события — `/domain-deep-dive`, не этот скилл.
- **Не смешивать проекты.** Аудит скоупится в один `<project-slug>`;
  межпроектные несостыковки — предмет `/cross-audit`, не этот скилл.
- **Не смешивать поверхности.** Каждая папка `telegram-bot-flow/<surface>/`
  аудитится в своих границах: ссылки внутри слоя и зеркала с interface
  разрешаются только в пределах той же поверхности; ссылка в чужую
  поверхность — error (R-XSURF-001). Кросс-поверхностную сверку (включая
  словарь данных и payload событий) делает `/cross-audit`.
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
