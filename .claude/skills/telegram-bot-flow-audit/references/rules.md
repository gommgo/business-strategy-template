# Реестр правил `telegram-bot-flow-audit`

Каждое правило: `id`, `severity`, `scope`, что проверяет, как проверять,
пример нарушения/нормы, рекомендация в отчёт.

Категории:

- **R-SURF** — целостность хребта поверхностей (папка ↔ реестр `surface.md`).
- **R-XSURF** — изоляция поверхностей (ссылка не уходит в чужую поверхность).
- **R-XFEAT** — изоляция фич (ссылка не уходит в чужую фичу минуя мосты).
- **R-STRUCT** — структурная целостность: форма артефактов, enum'ы, slug-рефы.
- **R-MIRROR** — синхронность зеркал (внутри слоя и с interface).
- **R-GRAPH** — связность графа диалогов и уникальность структурных идентификаторов.
- **R-DATA** — контракты данных (getter, dialog-data, плейсхолдеры).
- **R-TG** — инварианты модели Telegram.
- **R-SEM** — семантические подозрения, anti-patterns канона (смысловой разбор, не grep).
- **R-COV** — coverage и стиль.

Слой партиционирован по поверхности (surface): на каждую поверхность с
`type: bot` из реестра `docs/projects/<project-slug>/surface.md` — папка
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/` с корневыми
реестрами `command.md`, `notification.md` и папкой `features/`, где каждая
фича — `features/<feature>/` из трёх файлов: `dialog.md` (один диалог),
`window.md` (все окна — H2-секциями `## <window-slug>`), `use-case.md`
(все use-case'ы бота — H2-секциями `## <uc-slug>`) и `assets/`. Сокращённо:
`…/bot-flow/` — `docs/projects/<project-slug>/telegram-bot-flow/<surface>/`;
`…/feat/` — её папка фичи `features/<feature>/`;
`…/interface/` — `docs/projects/<project-slug>/interface/<surface>/`
(зеркала **той же поверхности**); `…/domains/` —
`docs/projects/<project-slug>/services/*/domains/` (домены сервисов, по
всем сервисам; read-only контекст — контекст уникален в проекте,
сервис-владелец выводится из пути).

**Изоляция двухуровневая.** R-STRUCT/R-MIRROR/R-GRAPH/R-DATA/R-TG/R-SEM/R-COV
применяются **в пределах одной поверхности**: зеркала сверяются с
`…/interface/` той же поверхности, корневые реестры — в пределах поверхности.
А внутри-фичевые ссылочные поля (`dialog.windows`, `widget.transition`,
`widget.action`, `getter.*.source`) разрешаются **в пределах одной фичи** —
среди записей той же папки `…/feat/`. Аудит итерирует по каждой папке
поверхности из scope отдельно, внутри неё — по каждой фиче. R-SURF/R-XSURF
— про границу между поверхностями; R-XFEAT — про границу между фичами.

«Секция существует» — в `…/feat/window.md`/`…/feat/use-case.md` есть
H2-секция `## <slug>` (заголовок секции = slug; мета-блок ```yaml```
читается без ошибок). «Диалог существует» — `…/feat/dialog.md` фичи `<slug>`
читается без ошибок (slug фичи = slug диалога). «Строка существует» — в
таблице `command.md`/`notification.md` корня есть строка с этим `slug`.

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
- **пример**: норма-с-оговоркой — `tg-client-bot` объявлен, папки (или в
  ней `features/`) нет: синтез сознательно отложен.
- **рекомендация**: «Поверхность объявлена как бот, но её фичи ещё не
  начаты — завести через `/telegram-bot-flow-deep-dive <project-slug>
  <slug>`, либо это сознательно отложено».

---

## R-XSURF (изоляция поверхностей)

### R-XSURF-001 «ссылка из одной поверхности в другую»

- **severity**: `error`.
- **scope**: все 5 kind любой папки `…/bot-flow/`; зеркала с
  `…/interface/`.
- **проверка**: каждое slug-значение в ссылочном поле (внутрь слоя —
  `windows`, `transition`, `started-by`, `starts`, `action`, `source`,
  `feature:<slug>`; в interface — `who`, `situations`, `interface-block`,
  `ux-substrates`, `data:<slug>`) разрешается среди записей **той же**
  поверхности. Если slug не найден в своей поверхности, но найден в другой
  (в её `bot-flow/`, `screens/` или `interface/`) — это пересечение
  границы (а не просто битая ссылка R-STRUCT): поверхности изолированы.
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

## R-XFEAT (изоляция фич)

### R-XFEAT-001 «ссылка из одной фичи в другую минуя мосты»

- **severity**: `error`.
- **scope**: внутри-фичевые ссылочные поля любой фичи `…/feat/`:
  `dialog.windows`, `widget.transition` (кроме `start:<feature>`),
  `widget.action`, `getter.*.source`.
- **проверка**: каждое внутри-фичевое slug-значение (окно фичи, use-case
  фичи) разрешается среди записей **той же** фичи (`window.md` /
  `use-case.md` своей папки `…/feat/`). Если slug не найден в своей фиче,
  но найден в другой фиче той же поверхности — это пересечение границы (а
  не просто битая ссылка R-STRUCT/R-STRUCT-020): фичи изолированы так же,
  как поверхности. Между фичами легитимны **только** мосты:
  `widget.transition: start:<feature>` (войти в диалог другой фичи),
  корневые реестры `command`/`notification` и реф `feature:<slug>` в их
  полях, а также `dialog.started-by: feature:<slug>`.
- **пример**: нарушение — `widget.transition: confirm`, где `confirm` —
  окно фичи `feedback`, а виджет живёт в фиче `booking`; норма —
  `transition: start:feedback` (вход во вложенный диалог другой фичи).
  Нарушение — `widget.action: use-case:list-services`, где этот use-case
  есть только в `use-case.md` фичи `catalog`; норма — завести use-case в
  своей фиче или войти в фичу `catalog` через `start:`.
- **рекомендация**: «Фичи изолированы — внутри-фичевая ссылка не должна
  уходить в чужую фичу. Войти в чужую фичу через `start:<feature>` на
  виджете, либо завести сущность в своей фиче через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>`. Общее
  между фичами сводят корневые реестры и `/cross-audit`».

---

## R-STRUCT (структура: форма, enum'ы, slug-рефы)

### R-STRUCT-001 «секция без мета-блока / диалог без frontmatter»

- **severity**: `error`.
- **scope**: `…/feat/dialog.md`, `…/feat/window.md`, `…/feat/use-case.md`.
- **проверка**: каждая фича `…/feat/` несёт `dialog.md` с читаемым
  frontmatter; каждая H2-секция `## <slug>` в `window.md`/`use-case.md`
  содержит читаемый мета-блок ```yaml```. Секция-заголовок без мета-блока
  или файл вне формы — сущности нет, ссылки на неё битые.
- **пример**: нарушение — `## confirm` в `window.md` без ```yaml```-блока
  (один скриншот в `assets/`); норма — `## confirm` + мета-блок + тело,
  ассеты в `…/feat/assets/confirm/`.
- **рекомендация**: «Завести секцию/мета-блок через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>`
  либо удалить пустой заголовок».

### R-STRUCT-002 «заголовок секции ≠ мета `slug` / имя фичи ≠ `dialog.slug`»

- **severity**: `error`.
- **scope**: `…/feat/dialog.md` (frontmatter `slug`), `…/feat/window.md`,
  `…/feat/use-case.md` (заголовки секций).
- **проверка**: заголовок секции `## <X>` в `window.md`/`use-case.md` —
  канонический slug записи (на него ссылаются `windows`, `action`,
  `source`); если мета-блок несёт собственный `slug`, он совпадает с
  заголовком. Имя папки фичи `features/<X>/` совпадает с `slug: <X>` во
  frontmatter её `dialog.md` (фича = один диалог, slug фичи = slug
  диалога).
- **пример**: нарушение — заголовок `## guests`, а `dialog.windows`
  ссылается на `guest`; нарушение — папка `features/booking/` со
  `slug: book` в `dialog.md`.
- **рекомендация**: «Привести в соответствие через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>` —
  скилл переименует и пересчитает ссылки».

### R-STRUCT-003 «дубль slug»

- **severity**: `error`.
- **scope**: window/use-case — в пределах **фичи**; command/notification —
  в пределах **поверхности**.
- **проверка**: window slug (заголовок `## <slug>` в `window.md`)
  уникален **в пределах фичи**; use-case slug (заголовок `## <slug>` в
  `use-case.md`) уникален **в пределах фичи** (две секции с одним
  заголовком — дубль). Для command/notification — колонка `slug` таблицы
  корня уникальна в пределах поверхности. Совпадение slug между фичами
  (например, окно `confirm` в двух фичах) или между поверхностями — **не
  дубль** (записи изолированы).
- **пример**: нарушение — две секции `## confirm` в одном `window.md`; две
  строки `order-confirmed` в `notification.md`. Норма — окно `confirm` в
  фиче `booking` и окно `confirm` в фиче `reorder` — разные записи.
- **рекомендация**: «Переименовать дубликат через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>` (каскадно правит
  ссылки)».

### R-STRUCT-004 «обязательное поле отсутствует»

- **severity**: `error`.
- **scope**: все 5 kind; перечни обязательных полей — в каноне фичи
  `_template/features/README.md` (frontmatter `dialog`, мета-блоки
  `window`/`use-case`, H3-секции `use-case`) и «Колонки» в
  `_template/command.md`, `_template/notification.md`.
- **проверка**: каждое обязательное поле/колонка/секция **присутствует** в
  записи:
  - dialog (frontmatter): `slug`, `name`, `description`, `states-group`,
    `windows`, `started-by`, `launch-mode`, `who`, `status`;
  - window (мета-блок): `name`, `state`, `interface-block`,
    `ux-substrates`, `situations`, `who`, `status` (slug — заголовок H2);
  - use-case (мета-блок): `name`, `operation`, `who`, `status` (slug —
    заголовок H2) + H3-секции `### Actor`, `### Inputs`, `### Outputs`,
    `### Dependencies`, `### Steps`, `### Errors`;
  - command: все 9 колонок; notification: все 9 колонок.
  Поле есть, но пустое/`—` там, где `—` не разрешён, — это R-SEM-007
  (зависит от `status`); отсутствие поля/секции целиком — ошибка формы
  всегда.
- **пример**: нарушение — окно без `state` (код не построит адрес
  `<states-group>.<state>`); use-case без секции `### Outputs` (нечему
  быть исходом для `when` окна).
- **рекомендация**: «Дозаполнить форму через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-005 «`status` вне enum»

- **severity**: `error`.
- **scope**: все 5 kind.
- **проверка**: `status` ∈ {`draft`, `stable`}.
- **рекомендация**: «Поправить status через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-006 «`dialog.launch-mode` вне enum»

- **severity**: `error`.
- **scope**: `…/feat/dialog.md`.
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
- **scope**: `…/feat/window.md` (секция `widgets` тела окна).
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
- **scope**: `…/feat/window.md` (секция `getter` тела окна).
- **проверка**: каждый `source` — `use-case:<uc-slug>` (use-case **бота**
  фичи, реф без точки), `dialog-data`, `start-data` или `const`. Чтение
  данных идёт через use-case бота, тот ходит в домен; доменный
  `use-case:<ctx>.<Operation>` (с точкой) в `source` **не** ставится — он
  живёт в `Dependencies` use-case'а бота. Существование секции use-case'а
  бота проверяет R-STRUCT-020.
- **пример**: нарушение — `source: api /services` (транспорт — забота
  кода) или `source: use-case:catalog.ListServices` (доменный реф в
  getter); норма — `source: use-case:list-services` (use-case бота фичи).
- **рекомендация**: «Поправить источник через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>` —
  данные окна идут через use-case бота фичи (реф без точки)».

### R-STRUCT-010 «`notification.trigger` вне форм»

- **severity**: `error`.
- **scope**: `command.md`/`notification.md` корня — здесь `notification.md`.
- **проверка**: `trigger` — `event:<ctx>.<Event>`,
  `schedule: <по-русски>` или `integration:<slug>` (slug существует в
  `integration.md` проекта).
- **пример**: нарушение — `trigger: когда захотим` или `trigger: cron
  0 9 * * *` (синтаксис кода); норма — `schedule: ежедневно в 9 по
  времени брони`.
- **рекомендация**: «Поправить триггер через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  notification:<slug>`».

### R-STRUCT-011 «`dialog.windows` → секции `window.md` фичи»

- **severity**: `error`.
- **scope**: `…/feat/dialog.md` (`windows`) ↔ `…/feat/window.md` той же
  фичи.
- **проверка**: каждый slug в `dialog.windows` — существующая H2-секция
  `## <slug>` в `window.md` **этой же фичи**.
- **пример**: нарушение — `windows: [services, guests, addres, confirm]`
  при секции `## address`.
- **рекомендация**: «Исправить опечатку или завести окно через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  window:<missing-slug>`».
- **примечание**: slug, найденный только в другой фиче, — R-XFEAT-001; в
  другой поверхности — R-XSURF-001.

### R-STRUCT-012 «секция окна вне `dialog.windows` фичи»

- **severity**: `error`.
- **scope**: `…/feat/window.md` ↔ `…/feat/dialog.md` той же фичи.
- **проверка**: каждая H2-секция `## <slug>` в `window.md` фичи числится в
  `dialog.windows` единственного диалога фичи (фича = один диалог + его
  окна; окно, не входящее в состав диалога, — артефакт-сирота).
- **пример**: нарушение — секция `## summary` в `window.md`, которой нет в
  `dialog.windows`; норма — каждое окно фичи перечислено в составе её
  диалога.
- **рекомендация**: «Добавить окно в `dialog.windows` или удалить секцию
  через `/telegram-bot-flow-deep-dive <project-slug> <surface>
  dialog:<feature>` / `window:<slug>`».

### R-STRUCT-013 «невалидный `transition` виджета»

- **severity**: `error`.
- **scope**: `…/feat/window.md` (поля `transition` виджетов, включая `to`
  в условных списках `{ to, when }`).
- **проверка**: каждое значение `transition` — одно из:
  - `<window-slug>` — окно, существующее секцией `## <window-slug>` в
    `window.md` **той же фичи** (окно чужой фичи — нарушение: между фичами
    только `start:`/`done`, ловит R-XFEAT-001);
  - `back`;
  - `done`;
  - `start:<feature>` — фича существует (её папка `features/<feature>/` с
    `dialog.md`).
- **пример**: нарушение — `transition: confirm`, где `confirm` — окно фичи
  `feedback`, а виджет в фиче `booking`; норма — `transition: start:feedback`.
- **рекомендация**: «Поправить переход через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`:
  цель — окно той же фичи, `back`, `done` или `start:<feature>`».

### R-STRUCT-014 «невалидный `dialog.started-by`»

- **severity**: `error`.
- **scope**: `…/feat/dialog.md` ↔ `command.md`, `notification.md` корня,
  фичи `features/` поверхности.
- **проверка**: каждый элемент `started-by` имеет форму `command:<slug>` |
  `notification:<slug>` | `feature:<slug>` и адресат существует:
  - `command:<slug>` / `notification:<slug>` — строка в реестре корня;
  - `feature:<X>` — фича `X` существует **и** у какого-то её окна есть
    виджет с `transition: start:<эта-фича>` (вход не выдуман: фича X
    реально входит в эту через `start:`; рассинхрон — сюда же).
- **пример**: нарушение — `started-by: [main-menu]` (без префикса kind),
  `started-by: [window:menu]` (форма `window:` упразднена) или
  `started-by: [feature:main-menu]`, где из фичи `main-menu` нет
  `start:booking`.
- **рекомендация**: «Поправить входы через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<feature>`
  (и/или дописать `start:` на виджете окна-входа фичи-источника)».

### R-STRUCT-015 «`command.starts` → фича»

- **severity**: `error`.
- **scope**: `command.md` ↔ фичи `features/` поверхности.
- **проверка**: `starts` — `feature:<slug>` с существующей фичей
  `features/<slug>/` (её диалог) либо `—` (статичный ответ, описан в
  `description`).
- **пример**: нарушение — `starts: dialog:booking` (форма `dialog:`
  упразднена) или `starts: feature:bookng` (опечатка); норма —
  `starts: feature:booking`.
- **рекомендация**: «Завести фичу или поправить реф через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> command:<slug>`».

### R-STRUCT-016 «`notification.action` → `command.md`/фича»

- **severity**: `error`.
- **scope**: `notification.md` ↔ `command.md` корня, фичи `features/`
  поверхности.
- **проверка**: `action` — `command:<slug>` (строка есть в `command.md`),
  `feature:<slug>` (фича `features/<slug>/` существует) либо `—`.
- **пример**: нарушение — `action: dialog:booking` (форма `dialog:`
  упразднена); норма — `action: feature:booking` или
  `action: command:start-booking-deeplink`.
- **рекомендация**: «Завести команду-deep-link/фичу или поправить реф
  через `/telegram-bot-flow-deep-dive <project-slug> <surface>
  notification:<slug>`».

### R-STRUCT-017 «битый `data:<slug>` → словарь interface»

- **severity**: `error`.
- **scope**: `…/feat/window.md` (поля `getter.*.data`, `message.media` в
  форме `data:<slug>.<поле>`).
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
- **scope**: `…/feat/dialog.md` (`who`), `…/feat/window.md` (`who`,
  `situations`, `interface-block`, `ux-substrates`),
  `…/feat/use-case.md` (`who`), `command.md` (`who`),
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
- **scope**: все 5 kind.
- **проверка**: `slug` — `[a-z0-9]+(-[a-z0-9]+)*`; `states-group` —
  PascalCase (англ.); `state` — UPPER_SNAKE (англ.); `operation` use-case
  бота — PascalCase (англ.); `id` виджета — snake_case; ключи getter'а —
  snake_case.
- **пример**: нарушение — `states-group: бронирование` (код-репо строит
  из него имя группы состояний); `operation: submit_booking` (нужен
  PascalCase `SubmitBooking`).
- **рекомендация**: «Привести к канону языка контракта через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-020 «`widget.action`/`getter.source` → use-case бота фичи»

- **severity**: `error`.
- **scope**: `…/feat/window.md` (`action` виджетов; `getter.*.source` в
  форме `use-case:<uc-slug>`) ↔ `…/feat/use-case.md` той же фичи.
- **проверка**: каждый реф `use-case:<uc-slug>` **без точки** (use-case
  бота) разрешается в существующую H2-секцию `## <uc-slug>` в
  `use-case.md` **той же фичи** — это ребро внутри слоя, slug-валидируемо.
  Реф **с точкой** (`use-case:<ctx>.<Operation>`) на виджете/в getter — не
  здесь: доменный use-case адресуется только из `Dependencies` use-case'а
  бота (на виджете/в getter он подозрителен — см. R-SEM-001). `action: —`
  — чистая навигация, проверки нет.
- **пример**: нарушение — `action: use-case:submit-draft`, а секции
  `## submit-draft` в `use-case.md` фичи нет; нарушение —
  `action: use-case:booking.SubmitOrder` (доменный реф на виджете). Норма
  — `action: use-case:submit-booking` при секции `## submit-booking`.
- **рекомендация**: «Завести use-case бота через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> use-case:<uc-slug>`
  либо поправить реф на виджете/в getter (use-case бота — без точки; домен
  адресуется из его `Dependencies`)».
- **примечание**: uc-slug, найденный только в другой фиче, — R-XFEAT-001.

---

## R-MIRROR (зеркала)

### R-MIRROR-001 «`dialog.transitions` ↔ `transition` виджетов окон»

- **severity**: `error`.
- **scope**: `…/feat/dialog.md` (сводка `transitions` тела) ↔
  `…/feat/window.md` (поля `transition` виджетов) той же фичи.
- **проверка**: сводный граф `transitions` диалога — выводимое зеркало;
  источник правды — `transition` на виджетах его окон. Для каждой пары
  `{ from, to }` сводки существует виджет окна `from` с переходом в `to`
  (`done` — с `transition: done`); и обратно — каждый авторский переход
  виджетов представлен в сводке. Расхождение в любую сторону — рассинхрон.
- **пример**: нарушение — сводка содержит `{ from: guests, to: confirm }`,
  а виджеты окна `guests` ведут только в `address`; норма — сводка
  пересчитана после правки окна.
- **рекомендация**: «Пересинхронизировать через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<feature>` —
  сводка выводима из окон, скилл пересчитает (смысловое расхождение —
  вопрос аналитику)».

### R-MIRROR-002 «`window.ux-substrates` ↔ interface `block.ux-substrates`»

- **severity**: `error`.
- **scope**: мета-блок окна-секции в `…/feat/window.md` ↔
  `…/interface/block.md` **той же поверхности**.
- **проверка**: для каждой секции окна — множество `ux-substrates` её
  мета-блока равно множеству `ux-substrates` строки `interface-block`
  (из того же мета-блока) в `…/interface/block.md`. Сравнение как
  множество (порядок не важен).
- **пример**: нарушение — interface-блок объявил
  `[services-list, services-next]`, мета-блок окна — только
  `[services-list]`.
- **рекомендация**: «Пересинхронизировать через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>` —
  скилл переспросит источник правды (окно отстало от блока, блок
  изменился, или смысловое расхождение → blocker)».

---

## R-GRAPH (граф диалогов)

Граф окон диалога фичи: вершины — `dialog.windows`, рёбра — `transition`
виджетов окон той же фичи (источник правды; сводка `transitions` —
зеркало). `back` ребром вперёд не считается; `done` — выход из графа;
`start:<feature>` — ребро в другую фичу (растит стек). Граф считается **в
пределах фичи**; матрёшка `start:` — межфичевое ребро поверхности.

### R-GRAPH-001 «диалог без `started-by`»

- **severity**: `error`.
- **scope**: `…/feat/dialog.md`.
- **проверка**: `started-by` непуст и не `—`. Диалог без входа недостижим:
  ни команда, ни кнопка другой фичи, ни уведомление в него не ведут.
- **пример**: нарушение — `started-by: —` у фичи `feedback`; норма —
  `started-by: [feature:booking]` + `start:feedback` на виджете окна фичи
  `booking`.
- **рекомендация**: «Объявить вход через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> dialog:<feature>` (команда, кнопка-`start:` из
  другой фичи или уведомление), либо фича не нужна — удалить (каскадно)».

### R-GRAPH-002 «окно-сирота»

- **severity**: `warning`.
- **scope**: `…/feat/window.md` в пределах своей фичи.
- **проверка**: окно не первое в `dialog.windows` и ни один `transition`
  виджетов окон той же фичи не ведёт в него. Канонный автопереход
  «следующее окно» идёт по порядку `windows`, но если в окно не ведёт ни
  явный переход, ни предыдущий шаг (предыдущее окно уводит в обход) —
  окно подвисло.
- **пример**: нарушение — `address` в `windows`, но `guests` ведёт сразу
  в `confirm` обоими исходами.
- **рекомендация**: «Дотянуть переход в окно через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  window:<источник>`, либо убрать окно из фичи (каскадно)».

### R-GRAPH-003 «тупиковое окно»

- **severity**: `error`.
- **scope**: `…/feat/window.md`.
- **проверка**: из окна есть выход: хотя бы один виджет с `transition`
  (окно той же фичи / `back` / `done` / `start:<feature>`). Окно без
  единого перехода — участник заперт (recovery протухших кнопок — не выход
  из живого окна).
- **пример**: нарушение — финальное окно «Спасибо!» без `done`; норма —
  кнопка «В меню» с `transition: done`.
- **рекомендация**: «Добавить переход или `done` через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>` —
  из каждого окна должен быть путь к завершению».

### R-GRAPH-004 «недостижимое окно»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: `…/feat/window.md` в пределах своей фичи.
- **проверка**: транзитивно: от первого окна `dialog.windows` по рёбрам
  переходов (плюс автопереход на следующее окно там, где шаг не уводит в
  сторону) достижимо каждое окно фичи. Ловит цепочки, где входящие
  рёбра есть, но сами идут из недостижимых окон.
- **рекомендация**: «Проверить граф диалога через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<feature>` —
  достроить путь или убрать ветку».

### R-GRAPH-005 «матрёшка `start:` без `done`»

- **severity**: `warning`.
- **scope**: фичи поверхности (междиалоговые рёбра `start:<feature>`).
- **проверка**: каждая фича, в которую входят через `start:<feature>`
  (вложенный диалог — стек растёт), имеет в графе своих окон хотя бы одно
  окно с `transition: done` — иначе стек не сворачивается к родителю.
  Отдельно — цикл `start:` (A → B → A) без `done` на уровнях: стек растёт
  бесконечно.
- **пример**: нарушение — `booking start:→ address-picker`, а в фиче
  `address-picker` ни одного окна с `done`.
- **рекомендация**: «Добавить `done` на завершающем окне вложенной фичи
  через `/telegram-bot-flow-deep-dive <project-slug> <surface>
  window:<slug>`».

### R-GRAPH-006 «два диалога с одним `states-group`»

- **severity**: `error`.
- **scope**: `…/feat/dialog.md` всех фич в пределах поверхности.
- **проверка**: значения `states-group` уникальны среди диалогов **всей
  поверхности** (фичи разных диалогов не дублируют группу) — из них код
  строит группы состояний.
- **рекомендация**: «Переименовать группу через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<feature>`».

### R-GRAPH-007 «дубль `state` внутри диалога фичи»

- **severity**: `error`.
- **scope**: `…/feat/window.md` в пределах своей фичи.
- **проверка**: среди окон диалога фичи значения `state` уникальны —
  адрес окна в коде `<states-group>.<state>` должен быть однозначным.
  Совпадение `state` между фичами — не дубль (у них разные `states-group`).
- **рекомендация**: «Переименовать state через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-GRAPH-008 «дубль `id` виджета в окне»

- **severity**: `error`.
- **scope**: `…/feat/window.md` (секция `widgets`, включая узлы внутри
  `row:`).
- **проверка**: `id` уникален в пределах окна — из него код строит
  callback-данные.
- **рекомендация**: «Переименовать id через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-GRAPH-009 «дубль `operation` use-case бота в фиче»

- **severity**: `error`.
- **scope**: `…/feat/use-case.md` в пределах своей фичи.
- **проверка**: значения `operation` (PascalCase) уникальны среди
  use-case'ов бота **одной фичи** — из них код строит имя
  сервиса/handler'а оркестрации. Совпадение `operation` между фичами — не
  дубль (фичи изолированы).
- **рекомендация**: «Переименовать operation через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  use-case:<uc-slug>`».

---

## R-DATA (контракты данных)

### R-DATA-001 «плейсхолдер без ключа getter»

- **severity**: `error`.
- **scope**: `…/feat/window.md` (`message.text`, `validation`, `label`
  виджетов с `{…}` вне item-контекста, `errors`).
- **проверка**: каждый плейсхолдер `{ключ}` текста окна обеспечен ключом
  в секции `getter`. Исключение — `{item.…}` внутри `label`/
  `selected-label` виджета с `items` (контекст элемента списка).
- **пример**: нарушение — `{selected_summary}` в тексте, в `getter` —
  только `services`.
- **рекомендация**: «Добавить ключ getter (source + fallback) через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-DATA-002 «ключ getter без `fallback`»

- **severity**: `error`.
- **scope**: `…/feat/window.md` (секция `getter`).
- **проверка**: каждый ключ getter'а имеет непустой `fallback` — окно не
  падает, когда источник недоступен.
- **пример**: норма — `fallback: пустой список — окно живо, «Далее»
  доступна`.
- **рекомендация**: «Дописать fallback через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>` —
  что показывает окно при недоступном источнике».

### R-DATA-003 «`items` виджета без ключа getter»

- **severity**: `error`.
- **scope**: `…/feat/window.md` (виджеты `select`/`multiselect`).
- **проверка**: значение `items` каждого виджета — существующий ключ
  секции `getter` того же окна.
- **рекомендация**: «Добавить ключ getter или поправить `items` через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-DATA-004 «несериализуемое в `dialog-data`»

- **severity**: `warning`.
- **scope**: `…/feat/dialog.md` (секция `dialog-data` тела).
- **проверка**: смысловой разбор описаний ключей: контракт накопления —
  только JSON-примитивы (строки, числа, списки, словари). Подозрения:
  «объект datetime», «сущность Order», «агрегат», «файл», ссылки на
  доменные типы вместо описания формы.
- **пример**: нарушение — `booking_date: объект даты брони`; норма —
  `booking_date: дата брони строкой ISO`.
- **рекомендация**: «Переописать ключ JSON-формой через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> dialog:<feature>`».

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
  «подтвердить заказ» при `starts` на фичу, в середину диалога которой она
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
  команду-deep-link или фичу.
- **пример**: нарушение — «Заказ готов. Кнопки: „Повторить“, „Оценить“,
  „Отменить“»; норма — одно действие `command:start-reorder-deeplink`
  (или `feature:reorder`), остальное — внутри диалога фичи.
- **рекомендация**: «Спроектировать вход в фичу через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>` (фича + одна
  точка провала из уведомления)».

---

## R-SEM (семантика, anti-patterns канона)

Все маркеры ниже — индикаторы; срабатывание означает «подозрение,
проверь». Это смысловой разбор прочитанного, не grep: аналитик имеет право
объяснить «нет, это осознанно», и при подтверждении warning не
превращается в правку.

### R-SEM-001 «`action`/`source` не похож на use-case бота»

- **severity**: `warning`.
- **scope**: `…/feat/window.md` (`action` виджетов, `getter.*.source` в
  форме `use-case:…`).
- **проверка**: значение `action`/`source` — реф `use-case:<uc-slug>` на
  **use-case бота** фичи (kebab-case slug, **без точки**) либо для `action`
  — `—` (чистая навигация). Существование секции use-case'а бота — строгая
  проверка R-STRUCT-020; здесь — смысловые подозрения на форму: «сохраняет
  в базу», имя функции/endpoint'а (`POST /orders`), описание действия
  по-русски вместо рефа, доменный реф с точкой
  (`use-case:booking.SubmitOrder`) на виджете/в getter (домен адресуется
  из `Dependencies` use-case'а бота, не отсюда).
- **пример**: нарушение — `action: записать заказ в БД` или
  `action: use-case:booking.SubmitOrder` (доменный реф на виджете); норма
  — `action: use-case:submit-booking` (use-case бота фичи).
- **рекомендация**: «Адресовать действие use-case'у бота фичи через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`;
  сам use-case бота дёргает домен в своих `Dependencies`».

### R-SEM-002 «бизнес-правило в `when`»

- **severity**: `warning`.
- **scope**: `…/feat/window.md` (условные переходы `{ to, when }`),
  `…/feat/dialog.md` (сводка `transitions`).
- **проверка**: `when` формулируется как **исход use-case бота**, не как
  правило, придуманное окном. Подозрения: сравнения с числами и порогами
  («если сумма > 1000», «больше 8 гостей»), упоминания скидок/лимитов/
  статусов как вычисляемых окном, любые «если <бизнес-условие>» без
  отсылки к результату действия.
- **пример**: нарушение — `when: 'если сумма > 1000 — скидка'`; норма —
  `when: 'use-case бота вернул «нужен адрес»'`.
- **рекомендация**: «Переформулировать как исход use-case бота через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`;
  само правило живёт в домене (`/domain-deep-dive`)».

### R-SEM-003 «`trigger: event:…` на событие, которого нет в доменах сервисов»

- **severity**: `warning`.
- **scope**: `notification.md` корня ↔ `…/domains/<ctx>/events/`
  (read-only, поиск по всем сервисам).
- **проверка**: для `trigger: event:<ctx>.<Event>` — контекст `<ctx>`
  существует в `…/domains/` (у какого-то сервиса), событие `<Event>`
  находится среди его событий
  (по имени, смысловое сопоставление). Отсутствие домена/события —
  подозрение: либо опечатка, либо событие ещё не спроектировано. Сверку
  payload ↔ плейсхолдеры `content` ведёт `/cross-audit`.
- **рекомендация**: «Поправить реф через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> notification:<slug>`, либо спроектировать
  событие через `/domain-deep-dive <project-slug> <ctx>`».

### R-SEM-004 «окно без соотносимой ситуации»

- **severity**: `warning`.
- **scope**: `…/feat/window.md` ↔ `…/interface/situation.md` (смысловой
  разбор).
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
- **scope**: `…/feat/window.md` (`message`, `widgets`), `notification.md`
  корня (`content`).
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
- **scope**: все 5 kind.
- **проверка**: маркеры кода: `.ftl`-ключи (`order-confirmed-msg =`),
  имена python-файлов/модулей (`dialogs/booking.py`), классы
  `aiogram_dialog` (`Dialog(`, `Window(`, `Button(`, `Format(`),
  callback-строки (`callback_data=`), регистрация роутеров; в use-case
  бота — класс сервиса, метод API-клиента, формат запроса, ретраи. Слой —
  аналитика композиции; маппинг на код делает код-репо.
- **пример**: нарушение — «окно реализуется классом `Window` с
  `Format('{services}')`»; норма — `message.text` с плейсхолдером и
  getter.
- **рекомендация**: «Убрать код через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> <kind>:<slug>` — структурные идентификаторы
  слоя (`states-group`, `state`, `operation`, `id`, ключи getter'а) уже
  всё, что нужно код-репо».

### R-SEM-007 «пустой обязательный слот»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: все 5 kind; перечни обязательных полей — в R-STRUCT-004.
- **проверка**: каждое обязательное поле/колонка/секция непусто и не `—`
  (кроме мест, где `—` — легитимное значение: `start-data`, `payload`,
  `starts`, `action`, `media`, `errors.invalid-input`, а у use-case бота —
  пустой `### Dependencies` без доменных рефов при работе только со
  стейтом). Для stable дыра уезжает в код-репо — потому error.
- **рекомендация**: «Заполнить через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> <kind>:<slug>`; для stable обязательные слоты
  не могут быть пусты».

### R-SEM-008 «inline-логика в тексте»

- **severity**: `warning`.
- **scope**: `…/feat/window.md` (`message.text`), `notification.md` корня
  (`content`).
- **проверка**: текст содержит ветвление словами: «если X — показываем Y»,
  «(для VIP другой текст)», «либо …, либо …» как инструкция показа.
  Вариативность текста выражается ключами getter'а или разными окнами/
  уведомлениями.
- **пример**: нарушение — «Если доставка: укажите адрес. Если самовывоз:
  ждём вас»; норма — два окна, маршрутизируемые исходом use-case бота.
- **рекомендация**: «Развести через ключ getter'а или отдельные окна —
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-SEM-009 «виджет без соотносимого атома»

- **severity**: `warning`.
- **scope**: `…/feat/window.md` ↔ `…/interface/ux-substrate.md` (смысловой
  разбор).
- **проверка**: каждый виджет и предъявление текста соотносимы с атомами
  блока-источника: `команда` → `button`, `ввод` → `text-input`, `выбор` →
  `select`/`multiselect`/`calendar`, `инфо`/`список` → текст и `items`.
  Виджет, не находящий атома (окно умеет больше, чем блок), и атом без
  воплощения (окно умеет меньше) — рассинхрон синтеза.
- **рекомендация**: «Сверить состав через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> window:<slug>`; недостающий атом — в interface
  через `/interface-deep-dive`».

### R-SEM-010 «бизнес-правило в `Steps` use-case бота»

- **severity**: `warning`.
- **scope**: `…/feat/use-case.md` (секция `### Steps`).
- **проверка**: шаги use-case'а бота — **оркестрация** (валидация формата
  ввода → вызов доменного use-case → разбор исхода → апдейт стейта →
  возврат исхода), не бизнес-правило. Подозрения: сравнения с числами и
  порогами («если гостей > 8 — отказать»), вычисление скидок/лимитов/
  цен/статусов, инвариант, придуманный оркестратором, любое
  бизнес-решение, которое должен принимать домен.
- **пример**: нарушение — `Steps: «3. Если сумма > 1000 — применить
  скидку 10%»`; норма — `Steps: «2. Call domain: use-case:billing.PriceOrder.
  3. Map outcome: исход домена → исход bot UC»`.
- **рекомендация**: «Перенести правило в доменный use-case через
  `/domain-deep-dive <project-slug> <ctx>`, а bot UC оставить вызов и
  маршрутизацию исхода через `/telegram-bot-flow-deep-dive <project-slug>
  <surface> use-case:<uc-slug>`».

### R-SEM-011 «`Dependencies` use-case бота на доменный use-case, которого нет в доменах сервисов»

- **severity**: `warning`.
- **scope**: `…/feat/use-case.md` (секция `### Dependencies`) ↔
  `…/domains/<ctx>/use-cases/` (read-only, поиск по всем сервисам).
- **проверка**: для каждого рефа `use-case:<ctx>.<Operation>` **с точкой**
  в `Dependencies` — контекст `<ctx>` существует в `…/domains/` (у
  какого-то сервиса), операция
  `<Operation>` находится среди его use-case (по имени, смысловое
  сопоставление). Домен может ещё не существовать: отсутствие
  домена/use-case —
  подозрение (опечатка либо домен ещё не спроектирован), не приговор.
- **пример**: подозрение — `Dependencies: use-case:booking.CreateOrder`,
  а в `services/*/domains/booking/use-cases/` такого нет; норма — реф на
  существующий доменный use-case.
- **рекомендация**: «Поправить реф через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> use-case:<uc-slug>`, либо спроектировать
  доменный use-case через `/domain-deep-dive <project-slug> <ctx>`».

### R-SEM-012 «use-case бота без `Dependencies` и без работы со стейтом»

- **severity**: `warning`.
- **scope**: `…/feat/use-case.md` (смысловой разбор `### Dependencies` +
  `### Steps`).
- **проверка**: use-case бота, который не дёргает ни одного доменного
  use-case (`### Dependencies` без доменных рефов) и не читает/пишет
  `dialog-data` (нет стейт-зависимостей и стейт-шагов), — подозрение на
  лишнюю сущность: чистая навигация — это `widget.transition`, отдельный
  use-case ей не нужен. Оркестратор существует, чтобы сходить в домен или
  поработать со стейтом.
- **пример**: подозрение — use-case `go-next`, чьи `Dependencies` пусты, а
  `Steps` — «вернуть переход на следующее окно»; норма — такой переход
  делает `widget.transition`, use-case удаляется.
- **рекомендация**: «Убрать use-case и оставить `widget.transition`, либо
  дотянуть оркестрацию (вызов домена / работа со стейтом) через
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  use-case:<uc-slug>`».

---

## R-COV (coverage и стиль)

### R-COV-001 «блок interface bot-поверхности без окна»

- **severity**: `hint`.
- **scope**: `…/interface/block.md` ↔ окна всех фич `…/feat/window.md`
  поверхности (смысловой разбор, чтение целиком).
- **проверка**: для каждой строки `…/interface/block.md` этой поверхности
  существует окно (в какой-нибудь фиче) с `interface-block` на неё. Блок
  без окна — дыра синтеза: UX-анализ есть, композиция не доехала.
- **рекомендация**: «Синтезировать окно через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window`, либо
  это сознательно отложено».

### R-COV-002 «реестр команд без `/start`»

- **severity**: `warning`.
- **scope**: `command.md` корня.
- **проверка**: при непустых `features/` в `command.md` есть строка с
  `command: /start` (без параметра). Бот без `/start` не имеет главного
  входа.
- **рекомендация**: «Завести `/start` (с `stack: reset` и фичей главного
  меню) через `/telegram-bot-flow-deep-dive <project-slug>
  <surface> command`».

### R-COV-003 «deep-link только в тексте уведомления»

- **severity**: `warning`.
- **scope**: `notification.md` ↔ `command.md` корня (смысловой разбор).
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
  `status: draft` (диалог на окна/use-case'ы фичи, окно на use-case бота,
  команда на фичу, уведомление на команду/фичу). Не блокирует stable, но
  код-репо прочитает stable-вход с draft-потрохами.
- **рекомендация**: «Докопать draft-соседа:
  `/telegram-bot-flow-deep-dive <project-slug> <surface>
  <kind>:<slug-соседа>`».

### R-COV-005 «media-референс на отсутствующий файл»

- **severity**: `error`.
- **scope**: `…/feat/window.md` (`message.media` в форме `assets/…`).
- **проверка**: путь `assets/<window-slug>/<file>` существует как файл в
  `…/feat/assets/` той же фичи.
- **рекомендация**: «Положить файл в `…/feat/assets/<window-slug>/`
  либо поправить/убрать `media` через `/telegram-bot-flow-deep-dive
  <project-slug> <surface> window:<slug>`».

### R-COV-006 «окно без `errors`»

- **severity**: `hint` (если `status: draft`), `warning` (если
  `status: stable`).
- **scope**: `…/feat/window.md`.
- **проверка**: тело окна содержит секцию `errors` с каноническими
  ключами `backend-unavailable` и `invalid-input` (текст или явный `—`).
  Содержательные ошибки — часть контракта окна; технический recovery —
  забота код-репо и здесь не описывается.
- **рекомендация**: «Дописать `errors` через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`».

### R-COV-007 «короткое `description`»

- **severity**: `hint`.
- **scope**: все 5 kind (где есть `description`/`name`).
- **проверка**: длина `description` меньше 10 символов либо `description`
  дословно повторяет `name`, не добавляя смысла.
- **рекомендация**: «`description` должен пояснять что/зачем — уточнить
  через `/telegram-bot-flow-deep-dive <project-slug> <surface>
  <kind>:<slug>`».

### R-COV-008 «осиротевший use-case бота»

- **severity**: `hint`.
- **scope**: `…/feat/use-case.md` ↔ `…/feat/window.md` той же фичи
  (смысловой разбор, чтение соседей фичи целиком).
- **проверка**: для каждой секции use-case'а бота фичи существует
  `widget.action` или `getter.*.source` (в каком-нибудь окне той же фичи),
  ссылающийся на неё через `use-case:<uc-slug>`. Use-case бота, на который
  не ссылается ни один виджет/getter, — осиротевшая оркестрация: либо окно
  ещё не дотянуто, либо use-case лишний.
- **пример**: подозрение — секция `## cancel-booking` в `use-case.md`,
  которую не дёргает ни одна кнопка фичи.
- **рекомендация**: «Сослаться на use-case с виджета/getter через
  `/telegram-bot-flow-deep-dive <project-slug> <surface> window:<slug>`,
  либо удалить лишний use-case (`use-case:<uc-slug>`)».
