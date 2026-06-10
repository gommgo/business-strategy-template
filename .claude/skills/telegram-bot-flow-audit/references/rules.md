# Реестр правил `telegram-bot-flow-audit`

Каждое правило: `id`, `severity`, `scope`, что проверяет, как проверять,
пример нарушения/нормы, рекомендация в отчёт.

Категории:

- **R-SURF** — целостность хребта поверхностей (папка ↔ реестр `surface.md`).
- **R-XSURF** — изоляция поверхностей (ссылка не уходит наружу).
- **R-STRUCT** — структурная целостность: форма артефактов, enum'ы, slug-рефы.
- **R-MIRROR** — синхронность зеркал (внутри слоя и с interface).
- **R-GRAPH** — связность графа диалогов и уникальность структурных идентификаторов.
- **R-DATA** — контракты данных (getter, dialog-data, плейсхолдеры).
- **R-TG** — инварианты модели Telegram.
- **R-SEM** — семантические подозрения, anti-patterns канона (смысловой разбор, не grep).
- **R-COV** — coverage и стиль.

Слой партиционирован по поверхности (surface): на каждую поверхность с
`type: bot` из реестра `docs/projects/<project-slug>/surface.md` — папка
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/` с подпапками
`dialogs/`, `windows/`, таблицами `command.md`, `notification.md` и
`assets/`. Сокращённо: `…/bot-flow/` —
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/`;
`…/interface/` — `docs/projects/<project-slug>/interface/<surface>/`
(зеркала **той же поверхности**); `…/domains/` —
`docs/projects/<project-slug>/domains/` (read-only контекст).

Правила R-STRUCT/R-MIRROR/R-GRAPH/R-DATA/R-TG/R-SEM/R-COV применяются
**в пределах одной поверхности**: ссылочные поля разрешаются среди записей
той же папки `…/bot-flow/`, зеркала сверяются с `…/interface/` той же
поверхности. Аудит итерирует по каждой папке поверхности из scope
отдельно. R-SURF/R-XSURF — про границу между поверхностями.

«Папка существует» — это `…/bot-flow/<kind-folder>/<slug>/index.md`
читается без ошибок (`dialogs`, `windows`). «Строка существует» — в
таблице `command.md`/`notification.md` есть строка с этим `slug`.

`docs/projects/_template/telegram-bot-flow/` — канон формы; из него
читаются только критерии, enum'ы и anti-patterns, не данные.

---

## R-SURF (хребет поверхностей)

### R-SURF-001 «папка поверхности вне реестра»

- **severity**: `error`.
- **scope**: подпапки `docs/projects/<project-slug>/telegram-bot-flow/` ↔
  `surface.md`.
- **проверка**: каждая подпапка `telegram-bot-flow/<X>/` имеет строку
  `slug: X` в реестре `docs/projects/<project-slug>/surface.md`. Хребет
  ведёт реестр — папки диалогов для поверхности вне реестра быть не
  должно.
- **пример**: нарушение — папка `telegram-bot-flow/support-bot/` при
  реестре без строки `support-bot`; норма — каждая папка слоя отвечает
  строке реестра.
- **рекомендация**: «Завести строку `<X>` в `surface.md` через
  `/project-deep-dive <project-slug>`, либо удалить папку
  `telegram-bot-flow/<X>/` (она осиротела относительно хребта)».

### R-SURF-002 «папка слоя для surface с `type ≠ bot`»

- **severity**: `error`.
- **scope**: подпапки `telegram-bot-flow/` ↔ колонка `type` реестра.
- **проверка**: для каждой подпапки `telegram-bot-flow/<X>/` строка `X`
  реестра имеет `type: bot`. Слой встаёт **на место** `screens/<surface>/`
  только для bot-поверхности; web/mobile/embed получают экраны.
- **пример**: нарушение — `telegram-bot-flow/web-clinic/` при
  `web-clinic · type: web`; норма — диалоги только у `type: bot`.
- **рекомендация**: «Либо поверхность на самом деле бот — поправить `type`
  через `/project-deep-dive <project-slug>`, либо это web/embed (включая
  mini-app Telegram) — её композиция живёт в `screens/<surface>/`, папку
  `telegram-bot-flow/<X>/` удалить».

### R-SURF-003 «bot-поверхность реестра без папки слоя»

- **severity**: `hint` (coverage).
- **scope**: строки реестра с `type: bot` ↔ подпапки `telegram-bot-flow/`.
- **проверка**: для каждой строки `surface.md` с `type: bot` существует
  папка `telegram-bot-flow/<slug>/`. Отсутствие — не ошибка модели, а
  непокрытая поверхность (диалоги ещё не синтезировали).
- **пример**: норма-с-оговоркой — `tg-client-bot` объявлен, папки нет:
  синтез сознательно отложен.
- **рекомендация**: «Поверхность объявлена как бот, но её диалоги ещё не
  начаты — завести через `/telegram-bot-flow-deep-dive <project-slug>
  <slug>`, либо это сознательно отложено».

---

## R-XSURF (изоляция поверхностей)

### R-XSURF-001 «ссылка из одной поверхности в другую»

- **severity**: `error`.
- **scope**: все 4 kind любой папки `…/bot-flow/`; зеркала с
  `…/interface/`.
- **проверка**: каждое slug-значение в ссылочном поле (внутрь слоя —
  `windows`, `dialog`, `transition`, `started-by`, `starts`, `action`; в
  interface — `who`, `situations`, `interface-block`, `ux-substrates`,
  `data:<slug>`) разрешается среди записей **той же** поверхности. Если
  slug не найден в своей поверхности, но найден в другой (в её
  `bot-flow/`, `screens/` или `interface/`) — это пересечение границы (а
  не просто битая ссылка R-STRUCT): поверхности изолированы.
- **пример**: нарушение — `window.interface-block: lab-results` из
  `interface/web-clinic/block.md`, когда окно живёт в
  `telegram-bot-flow/tg-client-bot/`; норма — блок-источник из
  `interface/tg-client-bot/block.md`.
- **рекомендация**: «Поверхности изолированы — ссылка не должна уходить в
  чужую папку. Завести сущность в своей поверхности через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>` (или
  `/interface-deep-dive` для interface-источника той же поверхности), либо
  убрать ссылку. Общее между поверхностями сводит `/cross-audit`».

---

## R-STRUCT (структура: форма, enum'ы, slug-рефы)

### R-STRUCT-001 «сущность без `index.md`»

- **severity**: `error`.
- **scope**: `dialogs/`, `windows/`.
- **проверка**: каждая подпапка `dialogs/<slug>/` и `windows/<slug>/`
  содержит читаемый `index.md` с frontmatter. Пустая папка или файл вне
  формы — сущности нет, ссылки на неё битые.
- **пример**: нарушение — `windows/confirm/` с одним скриншотом внутри;
  норма — `windows/confirm/index.md` + ассеты в `assets/windows/confirm/`.
- **рекомендация**: «Завести `index.md` через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>`
  либо удалить пустую папку».

### R-STRUCT-002 «slug папки ≠ frontmatter.slug»

- **severity**: `error`.
- **scope**: `dialogs/`, `windows/`.
- **проверка**: имя папки `…/bot-flow/<kind-folder>/<X>/` совпадает с
  `slug: <X>` в её `index.md`.
- **пример**: нарушение — папка `windows/guests/` со `slug: guest` во
  frontmatter.
- **рекомендация**: «Привести в соответствие через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>` —
  скилл переименует папку и пересчитает ссылки».

### R-STRUCT-003 «дубль slug»

- **severity**: `error`.
- **scope**: каждый kind в пределах поверхности независимо.
- **проверка**: внутри одного kind одной поверхности все `slug` уникальны:
  для dialog/window — frontmatter-`slug` папок, для command/notification —
  колонка `slug` таблицы (две строки с одним значением — дубль).
  Совпадение slug между поверхностями — не дубль (записи изолированы).
- **пример**: нарушение — две строки `order-confirmed` в
  `notification.md`.
- **рекомендация**: «Переименовать дубликат через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>` (каскадно правит
  ссылки)».

### R-STRUCT-004 «обязательное поле отсутствует»

- **severity**: `error`.
- **scope**: все 4 kind; перечни обязательных полей — «Форма frontmatter»
  в `_template/dialogs/README.md`, `_template/windows/README.md` и
  «Колонки» в `_template/command.md`, `_template/notification.md`.
- **проверка**: каждое обязательное поле/колонка **присутствует** в записи
  (dialog: `slug`, `name`, `description`, `states-group`, `windows`,
  `started-by`, `launch-mode`, `who`, `status`; window: `slug`, `name`,
  `description`, `dialog`, `state`, `interface-block`, `ux-substrates`,
  `situations`, `who`, `status`; command: все 9 колонок; notification: все
  9 колонок). Поле есть, но пустое/`—` там, где `—` не разрешён, — это
  R-SEM-007 (зависит от `status`); отсутствие поля целиком — ошибка формы
  всегда.
- **пример**: нарушение — окно без `state` (код не построит адрес
  `<states-group>.<state>`).
- **рекомендация**: «Дозаполнить форму через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-005 «`status` вне enum»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: `status` ∈ {`draft`, `stable`}.
- **рекомендация**: «Поправить status через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-006 «`dialog.launch-mode` вне enum»

- **severity**: `error`.
- **scope**: `dialogs/`.
- **проверка**: `launch-mode` ∈ {`standard`, `root`, `single-top`,
  `exclusive`}.
- **пример**: нарушение — `launch-mode: main` (нет такого режима).
- **рекомендация**: «Поправить через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> dialog:<slug>`».

### R-STRUCT-007 «`command.stack` вне enum»

- **severity**: `error`.
- **scope**: `command.md`.
- **проверка**: `stack` ∈ {`reset`, `push`}.
- **рекомендация**: «Поправить через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> command:<slug>`».

### R-STRUCT-008 «`widget` вне виджет-языка»

- **severity**: `error`.
- **scope**: `windows/` (секция `widgets` тела).
- **проверка**: каждый узел списка — либо `widget:` ∈ {`button`, `url`,
  `select`, `multiselect`, `text-input`, `calendar`}, либо группировка
  `row:` (внутри — те же виджеты). Поля узла соответствуют своему виджету
  (канон слоя § Виджет-язык): `url` без `action`/`transition`,
  `multiselect` с `items`/`selected-label` и т.д.
- **пример**: нарушение — `widget: inline-keyboard` (это класс кода, не
  виджет-язык); норма — `widget: button` + `row:` для ряда.
- **рекомендация**: «Привести к виджет-языку канона через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-STRUCT-009 «`getter.source` вне форм»

- **severity**: `error`.
- **scope**: `windows/` (секция `getter`).
- **проверка**: каждый `source` — `use-case:<ctx>.<Operation>`,
  `dialog-data`, `start-data` или `const`.
- **пример**: нарушение — `source: api /services` (транспорт — забота
  кода); норма — `source: use-case:catalog.ListServices`.
- **рекомендация**: «Поправить источник через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-STRUCT-010 «`notification.trigger` вне форм»

- **severity**: `error`.
- **scope**: `notification.md`.
- **проверка**: `trigger` — `event:<ctx>.<Event>`,
  `schedule: <по-русски>` или `integration:<slug>` (slug существует в
  `integration.md` проекта).
- **пример**: нарушение — `trigger: когда захотим` или `trigger: cron
  0 9 * * *` (синтаксис кода); норма — `schedule: ежедневно в 9 по
  времени брони`.
- **рекомендация**: «Поправить триггер через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  notification:<slug>`».

### R-STRUCT-011 «`dialog.windows` → `windows/`»

- **severity**: `error`.
- **scope**: `dialogs/` ↔ `windows/`.
- **проверка**: каждый slug в `dialog.windows` — существующая папка
  `windows/<slug>/` этой поверхности.
- **пример**: нарушение — `windows: [services, guests, addres, confirm]`
  при папке `windows/address/`.
- **рекомендация**: «Исправить опечатку или завести окно через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  window:<missing-slug>`».
- **примечание**: slug, найденный только в другой поверхности, —
  R-XSURF-001.

### R-STRUCT-012 «`window.dialog` → `dialogs/`»

- **severity**: `error`.
- **scope**: `windows/` ↔ `dialogs/`.
- **проверка**: `window.dialog` — существующая папка `dialogs/<slug>/`
  этой поверхности (ровно один диалог).
- **рекомендация**: «Завести диалог или поправить реф через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-STRUCT-013 «невалидный `transition` виджета»

- **severity**: `error`.
- **scope**: `windows/` (поля `transition` виджетов, включая `to` в
  условных списках `{ to, when }`).
- **проверка**: каждое значение `transition` — одно из:
  - `<window-slug>` — окно, существующее в `windows/` **и принадлежащее
    тому же диалогу** (`window.dialog` совпадает; окно чужого диалога —
    нарушение: между диалогами только `start:`/`done`);
  - `back`;
  - `done`;
  - `start:<dialog-slug>` — диалог существует в `dialogs/`.
- **пример**: нарушение — `transition: confirm`, где `confirm` принадлежит
  диалогу `feedback`, а окно — диалогу `booking`; норма —
  `transition: start:feedback`.
- **рекомендация**: «Поправить переход через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`:
  цель — окно того же диалога, `back`, `done` или `start:<dialog-slug>`».

### R-STRUCT-014 «невалидный `dialog.started-by`»

- **severity**: `error`.
- **scope**: `dialogs/` ↔ `command.md`, `windows/`, `notification.md`.
- **проверка**: каждый элемент `started-by` имеет форму `command:<slug>` |
  `window:<slug>` | `notification:<slug>` и адресат существует в своём
  реестре/папке этой поверхности. Для `window:<slug>` — у какого-то
  виджета этого окна действительно есть `transition: start:<этот-диалог>`
  (вход не выдуман; рассинхрон — сюда же).
- **пример**: нарушение — `started-by: [menu]` (без префикса kind) или
  `started-by: [window:menu]`, где из `menu` нет `start:booking`.
- **рекомендация**: «Поправить входы через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<slug>`
  (и/или дописать `start:` на виджете окна-входа)».

### R-STRUCT-015 «`command.starts` → `dialogs/`»

- **severity**: `error`.
- **scope**: `command.md` ↔ `dialogs/`.
- **проверка**: `starts` — `dialog:<slug>` с существующей папкой
  `dialogs/<slug>/` либо `—` (статичный ответ, описан в `description`).
- **рекомендация**: «Завести диалог или поправить реф через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> command:<slug>`».

### R-STRUCT-016 «`notification.action` → `command.md`/`dialogs/`»

- **severity**: `error`.
- **scope**: `notification.md` ↔ `command.md`, `dialogs/`.
- **проверка**: `action` — `command:<slug>` (строка есть в `command.md`),
  `dialog:<slug>` (папка есть в `dialogs/`) либо `—`.
- **рекомендация**: «Завести команду-deep-link/диалог или поправить реф
  через `/telegram-bot-flow-deep-dive <project-slug> <surface>
  notification:<slug>`».

### R-STRUCT-017 «битый `data:<slug>` → словарь interface»

- **severity**: `error`.
- **scope**: `windows/` (поля `getter.*.data`, `message.media` в форме
  `data:<slug>.<поле>`).
- **проверка**: каждый реф `data:<slug>` (и база `data:<slug>.<поле>`)
  существует строкой в `…/interface/data-items.md` **той же поверхности**.
- **пример**: нарушение — `data: data:servce` при строке `service` в
  `data-items.md`.
- **рекомендация**: «Завести датум через `/interface-deep-dive
  <project-slug> <surface> data-items:<missing-slug>` (это другой скилл)
  или поправить реф через `/telegram-bot-flow-deep-dive <project-slug>
  <surface> window:<slug>`».
- **примечание**: датум, найденный только в другой поверхности, —
  R-XSURF-001; кросс-поверхностную сверку словаря ведёт `/cross-audit`.

### R-STRUCT-018 «битый interface-реф (`who`/`situations`/`interface-block`/`ux-substrates`)»

- **severity**: `error`.
- **scope**: `dialogs/` (`who`), `windows/` (`who`, `situations`,
  `interface-block`, `ux-substrates`), `command.md` (`who`),
  `notification.md` (`to`).
- **проверка**: каждый slug существует строкой в соответствующем файле
  `…/interface/` **той же поверхности**: `who` / `to` → `who.md`,
  `situations` → `situation.md`, `interface-block` → `block.md`,
  `ux-substrates` → `ux-substrate.md`.
- **рекомендация**: «Завести запись в interface той же поверхности через
  `/interface-deep-dive <project-slug> <surface> <kind>:<missing-slug>`
  или поправить реф через `/telegram-bot-flow-deep-dive <project-slug>
  <surface> <kind>:<slug>`».

### R-STRUCT-019 «slug не kebab-case / структурный идентификатор не в своём регистре»

- **severity**: `hint`.
- **scope**: все 4 kind.
- **проверка**: `slug` — `[a-z0-9]+(-[a-z0-9]+)*`; `states-group` —
  PascalCase (англ.); `state` — UPPER_SNAKE (англ.); `id` виджета —
  snake_case; ключи getter'а — snake_case.
- **пример**: нарушение — `states-group: бронирование` (код-репо строит
  из него имя группы состояний).
- **рекомендация**: «Привести к канону языка контракта через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>`».

---

## R-MIRROR (зеркала)

### R-MIRROR-001 «`dialog.transitions` ↔ `transition` виджетов окон»

- **severity**: `error`.
- **scope**: `dialogs/` (сводка `transitions` тела) ↔ `windows/` (поля
  `transition` виджетов).
- **проверка**: сводный граф `transitions` диалога — выводимое зеркало;
  источник правды — `transition` на виджетах его окон. Для каждой пары
  `{ from, to }` сводки существует виджет окна `from` с переходом в `to`
  (`done` — с `transition: done`); и обратно — каждый авторский переход
  виджетов представлен в сводке. Расхождение в любую сторону — рассинхрон.
- **пример**: нарушение — сводка содержит `{ from: guests, to: confirm }`,
  а виджеты окна `guests` ведут только в `address`; норма — сводка
  пересчитана после правки окна.
- **рекомендация**: «Пересинхронизировать через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<slug>` —
  сводка выводима из окон, скилл пересчитает (смысловое расхождение —
  вопрос аналитику)».

### R-MIRROR-002 «`window.ux-substrates` ↔ interface `block.ux-substrates`»

- **severity**: `error`.
- **scope**: `windows/` ↔ `…/interface/block.md` **той же поверхности**.
- **проверка**: для каждого окна — множество `window.ux-substrates` равно
  множеству `ux-substrates` строки `window.interface-block` в
  `…/interface/block.md`. Сравнение как множество (порядок не важен).
- **пример**: нарушение — interface-блок объявил
  `[services-list, services-next]`, окно — только `[services-list]`.
- **рекомендация**: «Пересинхронизировать через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>` —
  скилл переспросит источник правды (окно отстало от блока, блок
  изменился, или смысловое расхождение → blocker)».

### R-MIRROR-003 «`dialog.windows` ↔ `window.dialog`»

- **severity**: `error`.
- **scope**: `dialogs/` ↔ `windows/`.
- **проверка**: двусторонне:
  - каждое окно из `dialog.windows` имеет `window.dialog = <этот dialog>`;
  - каждое окно с `window.dialog = D` присутствует в `D.windows`;
  - ни одно окно не числится в `windows` двух диалогов (окно принадлежит
    ровно одному).
- **пример**: нарушение — `confirm` числится и в `booking.windows`, и в
  `reorder.windows`; норма — общий шаг выносится в отдельный диалог и
  вызывается `start:`.
- **рекомендация**: «Пересинхронизировать принадлежность через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<slug>`
  (или `window:<slug>`) — скилл сведёт обе стороны».

---

## R-GRAPH (граф диалогов)

Граф окон диалога: вершины — `dialog.windows`, рёбра — `transition`
виджетов (источник правды; сводка `transitions` — зеркало). `back` ребром
вперёд не считается; `done` — выход из графа; `start:` — ребро в другой
диалог.

### R-GRAPH-001 «диалог без `started-by`»

- **severity**: `error`.
- **scope**: `dialogs/`.
- **проверка**: `started-by` непуст и не `—`. Диалог без входа недостижим:
  ни команда, ни кнопка, ни уведомление в него не ведут.
- **пример**: нарушение — `started-by: —` у диалога `feedback`; норма —
  `started-by: [window:confirm]` + `start:feedback` на виджете.
- **рекомендация**: «Объявить вход через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> dialog:<slug>` (команда, кнопка-`start:` или
  уведомление), либо диалог не нужен — удалить (каскадно)».

### R-GRAPH-002 «окно-сирота»

- **severity**: `warning`.
- **scope**: `windows/` в пределах своего диалога.
- **проверка**: окно не первое в `dialog.windows` и ни один `transition`
  виджетов окон того же диалога не ведёт в него. Канонный автопереход
  «следующее окно» идёт по порядку `windows`, но если в окно не ведёт ни
  явный переход, ни предыдущий шаг (предыдущее окно уводит в обход) —
  окно подвисло.
- **пример**: нарушение — `address` в `windows`, но `guests` ведёт сразу
  в `confirm` обоими исходами.
- **рекомендация**: «Дотянуть переход в окно через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  window:<источник>`, либо убрать окно из диалога (каскадно)».

### R-GRAPH-003 «тупиковое окно»

- **severity**: `error`.
- **scope**: `windows/`.
- **проверка**: из окна есть выход: хотя бы один виджет с `transition`
  (окно того же диалога / `back` / `done` / `start:`). Окно без единого
  перехода — участник заперт (recovery протухших кнопок — не выход из
  живого окна).
- **пример**: нарушение — финальное окно «Спасибо!» без `done`; норма —
  кнопка «В меню» с `transition: done`.
- **рекомендация**: «Добавить переход или `done` через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>` —
  из каждого окна должен быть путь к завершению».

### R-GRAPH-004 «недостижимое окно»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: `windows/` в пределах своего диалога.
- **проверка**: транзитивно: от первого окна `dialog.windows` по рёбрам
  переходов (плюс автопереход на следующее окно там, где шаг не уводит в
  сторону) достижимо каждое окно диалога. Ловит цепочки, где входящие
  рёбра есть, но сами идут из недостижимых окон.
- **рекомендация**: «Проверить граф диалога через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<slug>` —
  достроить путь или убрать ветку».

### R-GRAPH-005 «матрёшка `start:` без `done`»

- **severity**: `warning`.
- **scope**: `dialogs/` + `windows/` (междиалоговые рёбра `start:`).
- **проверка**: каждый диалог, в который входят через `start:` (вложенный
  — стек растёт), имеет в своём графе хотя бы одно окно с
  `transition: done` — иначе стек не сворачивается к родителю. Отдельно —
  цикл `start:` (A → B → A) без `done` на уровнях: стек растёт
  бесконечно.
- **пример**: нарушение — `booking start:→ address-picker`, а в
  `address-picker` ни одного `done`.
- **рекомендация**: «Добавить `done` на завершающем окне вложенного
  диалога через `/telegram-bot-flow-deep-dive <project-slug> <surface>
  window:<slug>`».

### R-GRAPH-006 «два диалога с одним `states-group`»

- **severity**: `error`.
- **scope**: `dialogs/` в пределах поверхности.
- **проверка**: значения `states-group` уникальны среди диалогов
  поверхности — из них код строит группы состояний.
- **рекомендация**: «Переименовать группу через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<slug>`».

### R-GRAPH-007 «дубль `state` внутри диалога»

- **severity**: `error`.
- **scope**: `windows/` в пределах своего диалога.
- **проверка**: среди окон одного диалога значения `state` уникальны —
  адрес окна в коде `<states-group>.<state>` должен быть однозначным.
- **рекомендация**: «Переименовать state через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-GRAPH-008 «дубль `id` виджета в окне»

- **severity**: `error`.
- **scope**: `windows/` (секция `widgets`, включая узлы внутри `row:`).
- **проверка**: `id` уникален в пределах окна — из него код строит
  callback-данные.
- **рекомендация**: «Переименовать id через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

---

## R-DATA (контракты данных)

### R-DATA-001 «плейсхолдер без ключа getter»

- **severity**: `error`.
- **scope**: `windows/` (`message.text`, `validation`, `label` виджетов с
  `{…}` вне item-контекста, `errors`).
- **проверка**: каждый плейсхолдер `{ключ}` текста окна обеспечен ключом
  в секции `getter`. Исключение — `{item.…}` внутри `label`/
  `selected-label` виджета с `items` (контекст элемента списка).
- **пример**: нарушение — `{selected_summary}` в тексте, в `getter` —
  только `services`.
- **рекомендация**: «Добавить ключ getter (source + fallback) через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-DATA-002 «ключ getter без `fallback`»

- **severity**: `error`.
- **scope**: `windows/` (секция `getter`).
- **проверка**: каждый ключ getter'а имеет непустой `fallback` — окно не
  падает, когда источник недоступен.
- **пример**: норма — `fallback: пустой список — окно живо, «Далее»
  доступна`.
- **рекомендация**: «Дописать fallback через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>` —
  что показывает окно при недоступном источнике».

### R-DATA-003 «`items` виджета без ключа getter»

- **severity**: `error`.
- **scope**: `windows/` (виджеты `select`/`multiselect`).
- **проверка**: значение `items` каждого виджета — существующий ключ
  секции `getter` того же окна.
- **рекомендация**: «Добавить ключ getter или поправить `items` через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-DATA-004 «несериализуемое в `dialog-data`»

- **severity**: `warning`.
- **scope**: `dialogs/` (секция `dialog-data`).
- **проверка**: смысловой разбор описаний ключей: контракт накопления —
  только JSON-примитивы (строки, числа, списки, словари). Подозрения:
  «объект datetime», «сущность Order», «агрегат», «файл», ссылки на
  доменные типы вместо описания формы.
- **пример**: нарушение — `booking_date: объект даты брони`; норма —
  `booking_date: дата брони строкой ISO`.
- **рекомендация**: «Переописать ключ JSON-формой через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<slug>`».

### R-DATA-005 «плейсхолдер `content` уведомления без источника»

- **severity**: `hint`.
- **scope**: `notification.md`.
- **проверка**: плейсхолдеры `{…}` в `content` приходят из payload
  триггера. Для `trigger: schedule:`/`integration:` — в `description`/
  `trigger` должно быть понятно, откуда значение; для `event:` глубокую
  сверку с `Payload` события делает `/cross-audit`, здесь — только флаг,
  если источник не угадывается вовсе.
- **рекомендация**: «Уточнить источник плейсхолдера через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  notification:<slug>`».

---

## R-TG (инварианты модели Telegram)

### R-TG-001 «`/start` без `stack: reset`»

- **severity**: `error`.
- **scope**: `command.md`.
- **проверка**: каждая строка, чья `command` — `/start` или форма
  deep-link `/start <param>`, имеет `stack: reset`. Вход всегда сбрасывает
  стек.
- **пример**: нарушение — `start-booking-deeplink · /start booking_<id> ·
  push`.
- **рекомендация**: «Поставить `stack: reset` через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  command:<slug>`».

### R-TG-002 «команда-шаг»

- **severity**: `warning`.
- **scope**: `command.md` (смысловой разбор).
- **проверка**: команда читается как движение внутри сценария, а не вход:
  имена/описания вида `/next`, `/confirm`, `/back`, «следующий шаг»,
  «подтвердить заказ» при `starts` на диалог, в середину которого она
  «прыгает». Движение внутри сценария делают виджеты окон.
- **пример**: нарушение — `/confirm · подтверждает текущий заказ`; норма
  — кнопка «Подтвердить» в окне `confirm`.
- **рекомендация**: «Перенести действие в виджет окна через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  window:<slug>`, команду удалить».

### R-TG-003 «уведомление без идемпотентности»

- **severity**: `error`.
- **scope**: `notification.md`.
- **проверка**: `idempotency` непуст и не `—` — называет ключ дедупликации
  (повтор триггера не даёт второго сообщения).
- **пример**: норма — `id события`, `booking_id + дата напоминания`.
- **рекомендация**: «Назвать ключ дедупликации через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  notification:<slug>`».

### R-TG-004 «клавиатура-сценарий в уведомлении»

- **severity**: `warning`.
- **scope**: `notification.md` (смысловой разбор `content` + `action`).
- **проверка**: уведомление пытается быть окном вне стека: в `content`
  описано больше одного действия («выберите…», перечень кнопок), или
  `action` подан списком. У уведомления максимум одно действие — провал в
  команду-deep-link или диалог.
- **пример**: нарушение — «Заказ готов. Кнопки: „Повторить“, „Оценить“,
  „Отменить“»; норма — одно действие `command:start-reorder-deeplink`,
  остальное — внутри диалога.
- **рекомендация**: «Спроектировать вход в диалог через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>` (диалог + одна
  точка провала из уведомления)».

---

## R-SEM (семантика, anti-patterns канона)

Все маркеры ниже — индикаторы; срабатывание означает «подозрение,
проверь». Это смысловой разбор прочитанного, не grep: аналитик имеет право
объяснить «нет, это осознанно», и при подтверждении warning не
превращается в правку.

### R-SEM-001 «`action` не похож на use-case»

- **severity**: `warning`.
- **scope**: `windows/` (`action` виджетов, `getter.*.source`).
- **проверка**: значение `action` — `use-case:<ctx>.<Operation>`
  (kebab-case контекст, PascalCase операция) либо `—` (чистая навигация).
  Подозрения: «сохраняет в базу», имя функции/endpoint'а
  (`POST /orders`), описание действия по-русски вместо рефа, `use-case:`
  без контекста. Дополнительно — read-only сверка с `…/domains/`: контекст
  `<ctx>` существует как `domains/<ctx>/`, операция находится среди его
  use-case (отсутствие — подозрение на невыросший домен, не приговор).
- **пример**: нарушение — `action: записать заказ в БД`; норма —
  `action: use-case:booking.SubmitOrder`.
- **рекомендация**: «Адресовать действие use-case'у домена через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`;
  если use-case ещё не спроектирован — это разговор для
  `/domain-deep-dive <project-slug> <ctx>`».

### R-SEM-002 «бизнес-правило в `when`»

- **severity**: `warning`.
- **scope**: `windows/` (условные переходы `{ to, when }`),
  `dialogs/` (сводка `transitions`).
- **проверка**: `when` формулируется как **исход use-case**, не как
  правило, придуманное окном. Подозрения: сравнения с числами и порогами
  («если сумма > 1000», «больше 8 гостей»), упоминания скидок/лимитов/
  статусов как вычисляемых окном, любые «если <бизнес-условие>» без
  отсылки к результату действия.
- **пример**: нарушение — `when: 'если сумма > 1000 — скидка'`; норма —
  `when: 'use-case вернул «нужен адрес»'`.
- **рекомендация**: «Переформулировать как исход use-case через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`;
  само правило живёт в домене (`/domain-deep-dive`)».

### R-SEM-003 «`trigger: event:…` на событие, которого нет в domains»

- **severity**: `warning`.
- **scope**: `notification.md` ↔ `…/domains/<ctx>/events/` (read-only).
- **проверка**: для `trigger: event:<ctx>.<Event>` — контекст `<ctx>`
  существует в `domains/`, событие `<Event>` находится среди его событий
  (по имени, смысловое сопоставление). Отсутствие домена/события —
  подозрение: либо опечатка, либо событие ещё не спроектировано. Сверку
  payload ↔ плейсхолдеры `content` ведёт `/cross-audit`.
- **рекомендация**: «Поправить реф через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> notification:<slug>`, либо спроектировать
  событие через `/domain-deep-dive <project-slug> <ctx>`».

### R-SEM-004 «окно без соотносимой ситуации»

- **severity**: `warning`.
- **scope**: `windows/` ↔ `…/interface/situation.md` (смысловой разбор).
- **проверка**: `situations` окна не пуст (пустой при `stable` — R-SEM-007)
  и перечисленные ситуации **по смыслу** разыгрываются в окне: то, что
  участник делает в окне (текст, виджеты, действия), узнаётся в
  goal/action ситуаций. Окно, чей смысл не находит ни одной ситуации
  interface, — дыра анализа: композиция придумала шаг, которого UX-слой
  не знает.
- **пример**: подозрение — окно «Оценка заказа» при `situations:
  [make-order]` и отсутствии ситуации про оценку.
- **рекомендация**: «Либо дозавести ситуацию в interface
  (`/interface-deep-dive <project-slug> <surface>`), либо пересмотреть
  привязку окна через `/telegram-bot-flow-deep-dive <project-slug>
  <surface> window:<slug>`».

### R-SEM-005 «облик в артефакте»

- **severity**: `warning`.
- **scope**: `windows/` (`message`, `widgets`), `notification.md`
  (`content`).
- **проверка**: маркеры облика: HTML/Markdown-разметка как требование
  (`<b>`, `**жирный**`, «выделить жирным»), эмодзи-оформление как
  обязательное свойство («обязательно с 🎉»), «жирная/красная кнопка»,
  описание форматирования вместо содержания. Эмодзи как **содержание**
  примера текста (галочка в `selected-label`) — норма; требование стиля —
  подозрение.
- **пример**: нарушение — `label: '<b>Далее</b>'`; норма —
  `label: 'Далее →'` (оформление — забота кода и контента).
- **рекомендация**: «Снять облик через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> <kind>:<slug>` — форматирование делает
  код-репо».

### R-SEM-006 «код в артефакте»

- **severity**: `warning`.
- **scope**: все 4 kind.
- **проверка**: маркеры кода: `.ftl`-ключи (`order-confirmed-msg =`),
  имена python-файлов/модулей (`dialogs/booking.py`), классы
  `aiogram_dialog` (`Dialog(`, `Window(`, `Button(`, `Format(`),
  callback-строки (`callback_data=`), регистрация роутеров. Слой —
  аналитика композиции; маппинг на код делает код-репо.
- **пример**: нарушение — «окно реализуется классом `Window` с
  `Format('{services}')`»; норма — `message.text` с плейсхолдером и
  getter.
- **рекомендация**: «Убрать код через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> <kind>:<slug>` — структурные идентификаторы
  слоя (`states-group`, `state`, `id`, ключи getter'а) уже всё, что нужно
  код-репо».

### R-SEM-007 «пустой обязательный слот»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: все 4 kind; перечни обязательных полей — в R-STRUCT-004.
- **проверка**: каждое обязательное поле/колонка непусто и не `—` (кроме
  мест, где `—` — легитимное значение: `start-data`, `payload`, `starts`,
  `action`, `media`, `errors.invalid-input`). Для stable дыра уезжает в
  код-репо — потому error.
- **рекомендация**: «Заполнить через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> <kind>:<slug>`; для stable обязательные слоты
  не могут быть пусты».

### R-SEM-008 «inline-логика в тексте»

- **severity**: `warning`.
- **scope**: `windows/` (`message.text`), `notification.md` (`content`).
- **проверка**: текст содержит ветвление словами: «если X — показываем Y»,
  «(для VIP другой текст)», «либо …, либо …» как инструкция показа.
  Вариативность текста выражается ключами getter'а или разными окнами/
  уведомлениями.
- **пример**: нарушение — «Если доставка: укажите адрес. Если самовывоз:
  ждём вас»; норма — два окна, маршрутизируемые исходом use-case.
- **рекомендация**: «Развести через ключ getter'а или отдельные окна —
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-SEM-009 «виджет без соотносимого атома»

- **severity**: `warning`.
- **scope**: `windows/` ↔ `…/interface/ux-substrate.md` (смысловой
  разбор).
- **проверка**: каждый виджет и предъявление текста соотносимы с атомами
  блока-источника: `команда` → `button`, `ввод` → `text-input`, `выбор` →
  `select`/`multiselect`/`calendar`, `инфо`/`список` → текст и `items`.
  Виджет, не находящий атома (окно умеет больше, чем блок), и атом без
  воплощения (окно умеет меньше) — рассинхрон синтеза.
- **рекомендация**: «Сверить состав через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> window:<slug>`; недостающий атом — в interface
  через `/interface-deep-dive`».

---

## R-COV (coverage и стиль)

### R-COV-001 «блок interface bot-поверхности без окна»

- **severity**: `hint`.
- **scope**: `…/interface/block.md` ↔ `windows/` (смысловой разбор,
  чтение обоих файлов целиком).
- **проверка**: для каждой строки `…/interface/block.md` этой поверхности
  существует окно с `interface-block` на неё. Блок без окна — дыра
  синтеза: UX-анализ есть, композиция не доехала.
- **рекомендация**: «Синтезировать окно через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window`, либо
  это сознательно отложено».

### R-COV-002 «реестр команд без `/start`»

- **severity**: `warning`.
- **scope**: `command.md`.
- **проверка**: при непустых `dialogs/` в `command.md` есть строка с
  `command: /start` (без параметра). Бот без `/start` не имеет главного
  входа.
- **рекомендация**: «Завести `/start` (с `stack: reset` и диалогом
  главного меню) через `/telegram-bot-flow-deep-dive <project-slug>
  <surface> command`».

### R-COV-003 «deep-link только в тексте уведомления»

- **severity**: `warning`.
- **scope**: `notification.md` ↔ `command.md` (смысловой разбор).
- **проверка**: упоминание deep-link'а в `content`/`description`
  уведомления (форма `/start <…>`, «по ссылке открывается…») доехало до
  реестра: существует строка `command.md`, чья `command` — этот deep-link,
  и `action` уведомления на неё ссылается. Deep-link, живущий только в
  тексте, код-репо не зарегистрирует.
- **пример**: нарушение — `content: «Повторить заказ: /start reorder_42»`
  при `action: —` и отсутствии команды `reorder` в реестре.
- **рекомендация**: «Завести команду-deep-link и сослаться на неё в
  `action` через `/telegram-bot-flow-deep-dive <project-slug> <surface>
  command` + `notification:<slug>`».

### R-COV-004 «stable ссылается на draft»

- **severity**: `hint`.
- **scope**: все ссылочные поля внутри слоя.
- **проверка**: запись со `status: stable` ссылается на запись слоя со
  `status: draft` (диалог на окна, команда на диалог, уведомление на
  команду/диалог). Не блокирует stable, но код-репо прочитает stable-вход
  с draft-потрохами.
- **рекомендация**: «Докопать draft-соседа:
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  <kind>:<slug-соседа>`».

### R-COV-005 «media-референс на отсутствующий файл»

- **severity**: `error`.
- **scope**: `windows/` (`message.media` в форме `assets/…`).
- **проверка**: путь `assets/windows/<slug>/<file>` существует как файл в
  `…/bot-flow/assets/`.
- **рекомендация**: «Положить файл в `…/bot-flow/assets/windows/<slug>/`
  либо поправить/убрать `media` через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> window:<slug>`».

### R-COV-006 «окно без `errors`»

- **severity**: `hint` (если `status: draft`), `warning` (если
  `status: stable`).
- **scope**: `windows/`.
- **проверка**: тело окна содержит секцию `errors` с каноническими
  ключами `backend-unavailable` и `invalid-input` (текст или явный `—`).
  Содержательные ошибки — часть контракта окна; технический recovery —
  забота код-репо и здесь не описывается.
- **рекомендация**: «Дописать `errors` через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-COV-007 «короткое `description`»

- **severity**: `hint`.
- **scope**: все 4 kind.
- **проверка**: длина `description` меньше 10 символов либо `description`
  дословно повторяет `name`, не добавляя смысла.
- **рекомендация**: «`description` должен пояснять что/зачем — уточнить
  через `/telegram-bot-flow-deep-dive <project-slug> <surface>
  <kind>:<slug>`».
