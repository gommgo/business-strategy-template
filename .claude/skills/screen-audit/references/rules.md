# Реестр правил `screen-audit`

Каждое правило: `id`, `severity`, `scope`, что проверяет, как проверять,
рекомендация в отчёт.

Категории:

- **R-STRUCT** — структурная целостность (ошибки модели).
- **R-MIRROR** — синхронность зеркал (внутри screens и с interface).
- **R-SEM** — семантические подозрения, anti-patterns канона.
- **R-COV** — coverage и стиль.

Все пути ниже — в папке текущего проекта
`docs/projects/<project-slug>/`. Сокращённо: `…/screens/` —
`docs/projects/<project-slug>/screens/`; `…/interface/` —
`docs/projects/<project-slug>/interface/`.

«Папка существует» — это `…/screens/<kind-folder>/<slug>/index.md`
читается без ошибок (`flows`, `screens`, `blocks`, `shells`).

`docs/projects/example/` — образцовый проект, в аудите не участвует.
`docs/projects/_canon/screens/` — канон формы; из него читаются только
критерии и инвентарь, не данные.

---

## R-STRUCT (структура)

### R-STRUCT-001 «валидность ссылок внутри screens»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: каждое slug-значение в ссылочном поле указывает на
  существующую папку рабочей зоны:
  - `flow.desktop` (массив) → `screens/<slug>/`
  - `flow.mobile` (массив) → `screens/<slug>/`
  - `flow.transitions[].from` / `.to` → `screens/<slug>/`
  - `screen.shell` → `shells/<slug>/`
  - `screen.blocks` (массив) → `blocks/<slug>/`
  - `screen.transitions-to-screen` (массив) → `screens/<slug>/`
  - `screen.mobile-of` → `flows/<slug>/`
  - `block.used-by-screens` (массив) → `screens/<slug>/`
  - `block:<slug>` внутри `slot-fills`/`states` (screens) → `blocks/<slug>/`
  - `block:<slug>` внутри `tree` через `slots` (block-контейнер) → `blocks/<slug>/`
- **рекомендация**: «Завести stub через `/screen-deep-dive
  <kind>:<missing-slug>` или заменить ссылку на существующий slug».

### R-STRUCT-002 «валидность ссылок в interface»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: каждый interface-slug в ссылочном поле существует как
  строка в `…/interface/<file>.md`:
  - `flow.who` (массив) → `who.md`
  - `screen.situations` (массив) → `situation.md`
  - `screen.who` (массив) → `who.md`
  - `block.interface-block` → `block.md`
  - `block.ux-substrates` (массив) → `ux-substrate.md`
  - `data:<slug>` (одиночный) или `data:<slug>.<field>` внутри
    `slot-fills`/`states` (screen), `tree` (block), `block.data`-карты →
    `data-items.md`
- **рекомендация**: «Завести запись в interface через
  `/interface-deep-dive <kind>:<missing-slug>` (это другой скилл) или
  заменить ссылку на существующий interface-slug через
  `/screen-deep-dive <kind>:<slug>`».

### R-STRUCT-003 «дубликат slug»

- **severity**: `error`.
- **scope**: каждый kind независимо.
- **проверка**: внутри одного kind все `slug` уникальны (фактический
  дубль — два `slug:` с одним значением в разных папках одного kind).
  Файловая система не даст двух папок с одним именем, но `slug` во
  frontmatter может разойтись с именем папки — см. R-STRUCT-004.
- **рекомендация**: «Переименовать дубликат через
  `/screen-deep-dive` (каскадно правит ссылки)».

### R-STRUCT-004 «slug папки ≠ frontmatter.slug»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: имя папки `…/screens/<kind-folder>/<X>/` совпадает с
  `slug: <X>` в её `index.md`.
- **рекомендация**: «Привести в соответствие через
  `/screen-deep-dive <kind>:<slug>` — скилл переименует папку и
  пересчитает ссылки».

### R-STRUCT-005 «status вне enum»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: `status` ∈ {`draft`, `stable`}.
- **рекомендация**: «Поправить status через `/screen-deep-dive
  <kind>:<slug>`».

### R-STRUCT-006 «`screen.viewport` вне enum»

- **severity**: `error`.
- **scope**: `screens/`.
- **проверка**: `viewport` ∈ {`desktop`, `mobile`, `any`}.
- **рекомендация**: «Поправить viewport через `/screen-deep-dive
  screen:<slug>`».

### R-STRUCT-007 «`shell.slots[*].accepts` вне enum»

- **severity**: `error`.
- **scope**: `shells/`.
- **проверка**: для каждого слота `accepts` ∈
  {`block`, `tree`, `block | tree`, `block (modal/drawer)`}.
- **рекомендация**: «Поправить `accepts` через `/screen-deep-dive
  shell:<slug>`».

### R-STRUCT-008 «`shell.responsive` вне enum»

- **severity**: `error`.
- **scope**: `shells/`.
- **проверка**: для каждого `responsive[<bp>][<slot>]` —
  `bp` ∈ {`xs`, `sm`, `md`, `lg`, `xl`}, значение ∈
  {`visible`, `drawer-via-burger`, `overlay`, `stacked`, `hidden`}.
  Каждый `<slot>` в responsive есть в `shell.slots`.
- **рекомендация**: «Поправить `responsive` через `/screen-deep-dive
  shell:<slug>`».

### R-STRUCT-009 «shell без `slots`»

- **severity**: `error`.
- **scope**: `shells/`.
- **проверка**: `shell.slots` непуст и не `—`. Для каждого слота указаны
  и `required`, и `accepts`.
- **рекомендация**: «Завести слоты через `/screen-deep-dive
  shell:<slug>`, либо удалить shell, если он бессодержателен».

### R-STRUCT-010 «block без `block-body`»

- **severity**: `error`.
- **scope**: `blocks/`.
- **проверка**: `block.tree` содержит зону `block-body` хотя бы с одним
  узлом.
- **рекомендация**: «Добавить `block-body` через `/screen-deep-dive
  block:<slug>` — это обязательная зона блока».

### R-STRUCT-011 «`screen.slot-fills` вводит слот, не объявленный в shell»

- **severity**: `error`.
- **scope**: `screens/` ↔ `shells/`.
- **проверка**: каждый ключ в `screen.slot-fills` есть в `shell.slots`
  у соответствующего `screen.shell`. То же для каждого слота, упомянутого
  в `screen.states[<state>]` (override).
- **рекомендация**: «Убрать неизвестный слот из `slot-fills`/`states`
  или объявить его в shell через `/screen-deep-dive shell:<shell-slug>`».

### R-STRUCT-012 «нарушение `accepts` в `slot-fills`»

- **severity**: `error`.
- **scope**: `screens/` ↔ `shells/`.
- **проверка**: содержимое `slot-fills[<slot>]` совместимо с
  `shell.slots[<slot>].accepts`:
  - `accepts: block` → только `block:<slug>` или `—`;
  - `accepts: tree` → только inline-дерево или `—`;
  - `accepts: block | tree` → любое из двух или `—`;
  - `accepts: block (modal/drawer)` → только `block:<slug>` или `—`.
  То же для override в `states`.
- **рекомендация**: «Привести содержимое в соответствие с `accepts`
  через `/screen-deep-dive screen:<slug>` либо пересмотреть `accepts`
  через `/screen-deep-dive shell:<shell-slug>`».

### R-STRUCT-013 «незаполненный `required`-слот в screen»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: `screens/` ↔ `shells/`.
- **проверка**: для каждого слота shell c `required: true` —
  `screen.slot-fills[<slot>]` непуст и не `—`.
- **рекомендация**: «Заполнить слот через `/screen-deep-dive
  screen:<slug>`; либо сделать слот опциональным в shell, если
  это сознательное решение, через `/screen-deep-dive shell:<shell-slug>`».

### R-STRUCT-014 «slug блока (screens) ≠ slug interface-block»

- **severity**: `error`.
- **scope**: `blocks/`.
- **проверка**: `block.slug` совпадает с `block.interface-block` (одно
  имя на двух слоях — канон).
- **рекомендация**: «Привести slug к одному значению через
  `/screen-deep-dive block:<slug>` (каскадно переименует ссылки)».

### R-STRUCT-015 «flow с пустым `desktop` или пустым `mobile`»

- **severity**: `error`.
- **scope**: `flows/`.
- **проверка**: оба массива непусты.
- **рекомендация**: «Заполнить через `/screen-deep-dive flow:<slug>`,
  либо это не flow — удалить или переосмыслить как одиночный screen с
  `viewport: any`».

### R-STRUCT-016 «один screen-slug в `flow.desktop` и `flow.mobile`»

- **severity**: `error`.
- **scope**: `flows/`.
- **проверка**: множества `desktop` и `mobile` не пересекаются. На
  разных viewport — разные screen.
- **рекомендация**: «Развести в два screen-slug через
  `/screen-deep-dive flow:<slug>` (один — desktop, другой — mobile),
  либо это просто screen с `viewport: any` — удалить flow».

### R-STRUCT-017 «`flow.transitions` пересекает desktop ↔ mobile»

- **severity**: `error`.
- **scope**: `flows/`.
- **проверка**: для каждого `transitions[i]` — оба `from` и `to`
  принадлежат `flow.mobile` (transitions описывают только mobile-серию).
- **рекомендация**: «Удалить cross-viewport transition через
  `/screen-deep-dive flow:<slug>` — переходы desktop↔mobile не пишутся,
  это разные viewport одного flow».

### R-STRUCT-018 «`screen.transitions-to-screen` внутри одного flow»

- **severity**: `warning`.
- **scope**: `screens/` ↔ `flows/`.
- **проверка**: если оба screen упомянуты в одном `flow.mobile` —
  явный `transitions-to-screen` дублирует `flow.transitions`. Явный
  `transitions-to-screen` нужен для переходов наружу из flow.
- **рекомендация**: «Перенести переход в `flow.transitions` через
  `/screen-deep-dive flow:<flow-slug>`, либо подтвердить, что это
  выход наружу — тогда target screen не должен быть в той же mobile-
  серии».

### R-STRUCT-019 «незакрытое значение опционального ссылочного поля»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: опциональное ссылочное поле либо отсутствует, либо
  непустой массив/slug, либо `—`. Пустой массив `[]` без явного `—`,
  или ссылка на несуществующий slug — нарушают канон.
- **рекомендация**: «Поправить через `/screen-deep-dive <kind>:<slug>`:
  убрать поле, поставить `—`, или указать существующий slug».

---

## R-MIRROR (зеркала)

### R-MIRROR-001 «`block.ux-substrates` (screens) ↔ `block.ux-substrates` (interface)»

- **severity**: `error`.
- **scope**: `blocks/` ↔ `…/interface/block.md`.
- **проверка**: для каждого блока B в screens — множество
  `B.ux-substrates` равно множеству `ux-substrates` строки с тем же
  slug в `…/interface/block.md`. Сравнение как мультимножество (порядок
  не важен).
- **рекомендация**: «Пересинхронизировать через `/screen-deep-dive
  block:<slug>` — скилл переспросит источник правды (screens-вариант,
  interface-вариант, или смысловое расхождение → blocker)».

### R-MIRROR-002 «`block.used-by-screens` ↔ фактические ссылки на блок в screens»

- **severity**: `error`.
- **scope**: `blocks/` ↔ `screens/`.
- **проверка**: для каждого блока B — `B.used-by-screens` равно
  множеству screen-slug, в чьих `slot-fills` или `states` встречается
  `block:<B.slug>` (любое поле, любой state).
- **рекомендация**: «Пересчитать через `/screen-deep-dive block:<slug>`
  — `used-by-screens` выводимо из screens, скилл синхронизирует
  автоматически».

### R-MIRROR-003 «`screen.blocks` ↔ `block:` в `slot-fills`/`states`»

- **severity**: `error`.
- **scope**: `screens/`.
- **проверка**: для каждого screen S — `S.blocks` равно множеству
  block-slug, на которые ссылается `block:<slug>` в теле (slot-fills и
  states-override).
- **рекомендация**: «Пересчитать через `/screen-deep-dive screen:<slug>`
  — `blocks` выводимо из тела, скилл синхронизирует автоматически».

### R-MIRROR-004 «`screen.viewport` несовместим с участием в flow»

- **severity**: `error`.
- **scope**: `screens/` ↔ `flows/`.
- **проверка**:
  - если screen упомянут в `flow.desktop` — `viewport` ∈ {`desktop`, `any`};
  - если в `flow.mobile` — `viewport` ∈ {`mobile`, `any`}.
- **рекомендация**: «Поправить через `/screen-deep-dive screen:<slug>`
  (привести viewport к согласованному значению) или через
  `/screen-deep-dive flow:<flow-slug>` (исключить screen из не своей
  серии)».

### R-MIRROR-005 «`screen.mobile-of` ↔ `flow.mobile`»

- **severity**: `error`.
- **scope**: `screens/` ↔ `flows/`.
- **проверка**: если `screen.mobile-of = <flow-slug>` — `screen.slug` ∈
  `flow.mobile` указанного flow.
- **рекомендация**: «Привести через `/screen-deep-dive screen:<slug>`
  (убрать `mobile-of` или сменить на правильный flow) или через
  `/screen-deep-dive flow:<flow-slug>` (добавить screen в `mobile`)».

---

## R-SEM (семантика, anti-patterns канона)

Все маркеры ниже — индикаторы; срабатывание означает «подозрение, проверь».
Аналитик имеет право объяснить «нет, это не так», и при подтверждении
warning не превращается в правку.

### R-SEM-001 «облик в дереве»

- **severity**: `warning`.
- **scope**: `screens/` (slot-fills, states), `blocks/` (tree),
  `shells/` (tree, responsive).
- **проверка**: в любом узле дерева присутствуют маркеры craft:
  - hex-цвета: `#` сразу за которым цифра/буква a-f (например, `#fff`,
    `#ab12cd`);
  - токены цвета: `color:`, `background:`, `bg=`, `bg-` с дальнейшим
    значением;
  - пиксельные значения: число + `px` (например, `16px`, `8px`);
  - типографика: `font`, `font-size`, `font-weight`, `line-height`,
    `letter-spacing`;
  - сырой стиль: `style=`.
- **рекомендация**: «Облик — craft в `@stit-design/ui`. Убрать из
  артефакта через `/screen-deep-dive <kind>:<slug>`; токены — на
  стороне ui-lib».

### R-SEM-002 «тематические оси (`density`/`brand`/`scheme`) в дереве»

- **severity**: `warning`.
- **scope**: `screens/`, `blocks/`, `shells/`.
- **проверка**: в любом узле или в любом props присутствует
  `density=` / `brand=` / `scheme=` / `density:` / `brand:` / `scheme:`.
  Тематические оси живут на корне через `data-*`, не как props
  компонентов и не как поля артефактов.
- **рекомендация**: «Убрать тематическую ось из узла через
  `/screen-deep-dive <kind>:<slug>` — это `data-theme`/`data-density`
  на корне приложения, а не контракт компонента».

### R-SEM-003 «FSD-имена в дереве или frontmatter»

- **severity**: `warning`.
- **scope**: `screens/`, `blocks/`, `shells/`, `flows/`.
- **проверка**: упоминания `widget:`, `feature:`, `entity:`, путей
  `pages/`, `widgets/`, `features/`, `entities/`, имён с суффиксом
  `Widget`, `Feature`, `Page` в значениях полей или в узлах дерева.
- **рекомендация**: «FSD-структура живёт в коде, который пишется по
  screens вручную, не в самих артефактах. Убрать FSD-имена через
  `/screen-deep-dive <kind>:<slug>`».

### R-SEM-004 «breakpoints в `slot-fills` или `block.tree`»

- **severity**: `warning`.
- **scope**: `screens/` (slot-fills, states), `blocks/` (tree).
- **проверка**: ключи или маркеры `xs:`, `sm:`, `md:`, `lg:`, `xl:`
  в slot-fills (screen) или tree (block). В этих местах breakpoints
  жить не должны — облицовочный адаптив только в `shell.responsive`,
  структурный — через `flow`.
- **рекомендация**: «Перенести в `shell.responsive` через
  `/screen-deep-dive shell:<shell-slug>` (облицовочный адаптив) либо
  оформить как `flow` через `/screen-deep-dive flow:<slug>`
  (структурный — разные viewport → разные screen)».

### R-SEM-005 «inline-cтейты в `block.tree`»

- **severity**: `warning`.
- **scope**: `blocks/`.
- **проверка**: в `block.tree` присутствуют узлы `ui:Skeleton`,
  `ui:EmptyState`, `ui:ErrorState`, `ui:AccessDeniedState`,
  `ui:OfflineState`, `ui:NotFoundState`.
- **рекомендация**: «Состояния — слой screen, не block. Перенести в
  `screen.states` через `/screen-deep-dive screen:<потребитель>`».

### R-SEM-006 «один `data:<slug>` под разными именованными слотами `block.data`»

- **severity**: `warning`.
- **scope**: `blocks/`.
- **проверка**: в `block.data: { <param>: data:<slug> }` один и тот же
  `data:<slug>` фигурирует в двух разных `<param>`.
- **рекомендация**: «Переиспользовать data-items напрямую через одно
  имя; перепроектировать через `/screen-deep-dive block:<slug>`».

### R-SEM-007 «слотовый узел shell непуст»

- **severity**: `warning`.
- **scope**: `shells/`.
- **проверка**: узел дерева shell с пометкой `(fills: $<slot>)` не
  имеет вложенных детей. Содержимое слота — задача screen, не shell.
- **рекомендация**: «Очистить слотовый узел через `/screen-deep-dive
  shell:<slug>` — содержимое идёт через `screen.slot-fills`».

### R-SEM-008 «пустой обязательный слот frontmatter»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: все 4 kind; список обязательных слотов по kind — в
  `screen-deep-dive/references/field-checklists.md` и в `Форма
  frontmatter` каждого kind-README.
- **проверка**: для каждой записи — каждый обязательный слот непуст
  и не `—`.
- **рекомендация**: «Заполнить через `/screen-deep-dive <kind>:<slug>`;
  для stable обязательные слоты не могут быть пусты».

### R-SEM-009 «`description` совпадает с `name`»

- **severity**: `warning`.
- **scope**: все 4 kind.
- **проверка**: `description` после трима/lowercase = `name` или
  содержится в `name` целиком, не добавляя смысла.
- **рекомендация**: «`description` должен пояснять что/зачем, а не
  повторять `name` — уточнить через `/screen-deep-dive <kind>:<slug>`».

### R-SEM-010 «`screen.situations` не покрывает ситуации экрана»

- **severity**: `warning`.
- **scope**: `screens/` ↔ `blocks/` ↔ `…/interface/ux-substrate.md`.
- **проверка**: вывод множества «ситуаций, чьи ux-substrates есть на
  экране» — через `screen.blocks → block.ux-substrates →
  ux-substrate.situation` (поле `situation` в `…/interface/ux-substrate.md`).
  Если какая-то такая ситуация отсутствует в `screen.situations` —
  warning.
- **рекомендация**: «Дополнить `screen.situations` через
  `/screen-deep-dive screen:<slug>` (скилл предложит точечный батч)».

### R-SEM-011 «`screen.states` не покрывает 6 канон-состояний»

- **severity**: `hint` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: `screens/`.
- **проверка**: в `screen.states` присутствуют все ключи: `loading`,
  `empty`, `error`, `permission-denied`, `offline`, `not-found`. Для
  каждого — либо непустой override (минимум один слот переопределён),
  либо явный комментарий «здесь не применимо» в теле.
- **рекомендация**: «Дополнить через `/screen-deep-dive screen:<slug>`;
  для stable канон-состояния обязательны».

### R-SEM-012 «flow с одним screen и в `desktop`, и в `mobile`»

- **severity**: `warning`.
- **scope**: `flows/`.
- **проверка**: `len(flow.desktop) == 1 AND len(flow.mobile) == 1` И
  оба указывают на разные screen-slug, при этом `mobile` содержит ровно
  один экран. Если на mobile один экран и на desktop один — это не
  flow (нечего разводить).
- **рекомендация**: «Это не flow — переосмыслить через
  `/screen-deep-dive flow:<slug>` (удалить, заменить на один screen с
  `viewport: any`)».

### R-SEM-013 «структурный адаптив через `shell.responsive`»

- **severity**: `warning`.
- **scope**: `shells/`.
- **проверка**: эвристика — в `shell.responsive` много слотов уходит в
  `hidden` на mobile-breakpoints (`xs`, `sm`) одновременно с тем, что
  есть `flow`, разводящий те же роли на отдельные mobile-screen.
  Возможный признак того, что то, что описано в `responsive` как
  «спрятать», на самом деле — структурный разрез (flow), а не
  облицовка.
- **рекомендация**: «Проверить, не лучше ли описать как `flow` через
  `/screen-deep-dive flow:<slug>`. Если облицовка осознанная — ответ
  аналитика снимает подозрение».

---

## R-COV (coverage и стиль)

### R-COV-001 «shell без screens»

- **severity**: `hint`.
- **scope**: `shells/`.
- **проверка**: для каждого `shell.slug` есть хотя бы один screen с
  `screen.shell == slug`.
- **рекомендация**: «Завести screen с этим shell через
  `/screen-deep-dive screen` либо удалить shell через
  `/screen-deep-dive` (каскадно)».

### R-COV-002 «block без потребителей»

- **severity**: `hint`.
- **scope**: `blocks/`.
- **проверка**: блок не упомянут ни в одном `screen.blocks` и ни в
  одном `block:<slug>` в slot-fills/states/tree.
- **рекомендация**: «Завести screen с этим блоком через
  `/screen-deep-dive screen`, либо удалить блок через
  `/screen-deep-dive block:<slug>` (каскадно)».

### R-COV-003 «screen недостижим»

- **severity**: `hint`.
- **scope**: `screens/`.
- **проверка**: screen не упомянут ни в одном `flow.desktop` /
  `flow.mobile`, не имеет `entrypoint: true`, не является целью ни
  одного `transitions-to-screen` другого screen.
- **рекомендация**: «Сделать `entrypoint=true`, добавить в flow или
  сделать целью перехода через `/screen-deep-dive screen:<slug>`,
  либо удалить (каскадно)».

### R-COV-004 «stable ссылается на draft»

- **severity**: `hint`.
- **scope**: все ссылочные поля внутри screens.
- **проверка**: запись со `status: stable` имеет ссылку на запись с
  `status: draft` (внутри screens; ссылки в interface проверяет
  `interface-audit`).
- **рекомендация**: «Не блокирует stable, но стоит докопать draft-
  соседа: `/screen-deep-dive <kind>:<slug-соседа>`».

### R-COV-005 «короткое `description`»

- **severity**: `hint`.
- **scope**: все 4 kind.
- **проверка**: длина `description` меньше 10 символов.
- **рекомендация**: «`description` слишком короткое для смысловой
  ясности; уточнить через `/screen-deep-dive <kind>:<slug>`».

### R-COV-006 «`ui:Component` отсутствует в выводимом инвентаре»

- **severity**: `hint`.
- **scope**: все 4 kind, узлы дерева.
- **проверка**: имя `ui:<Foo>` не входит в список «топ-уровень
  компонентов» в каноне `docs/projects/_canon/screens/README.md`
  (выводимое требование, пока `@stit-design/ui/manifest.json` не
  опубликован). Прорывной hint, не error — это, скорее всего, ui-lib
  gap.
- **рекомендация**: «Похоже на gap к ui-lib. Подтвердить через
  `/screen-deep-dive <kind>:<slug>` (скилл предложит зафиксировать
  `ui-lib gap: ui:Foo — для <зачем>` в state-заметке) или заменить на
  существующий компонент из инвентаря».

### R-COV-007 «asset-файл из `assets: [...]` не существует»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: для каждой записи `assets: [f1, f2, ...]` —
  `…/screens/assets/<kind>/<slug>/<fN>` существует как файл.
- **рекомендация**: «Удалить отсутствующий файл из `assets` через
  `/screen-deep-dive <kind>:<slug>`, либо положить файл в
  `…/screens/assets/<kind>/<slug>/`».

### R-COV-008 «`ux-substrate` не представлен узлом в `block.tree`»

- **severity**: `hint` (если `status: draft`), `warning` (если
  `status: stable`).
- **scope**: `blocks/`.
- **проверка**: для каждого `block.ux-substrates[i]` — в `block.tree`
  есть узел, которому этот субстрат соответствует. Полностью автомат
  не сделает — эвристика на соответствие slug/имени; спорные —
  оставлять для аналитика.
- **рекомендация**: «Раскрыть субстрат узлом дерева через
  `/screen-deep-dive block:<slug>` или убрать его из `ux-substrates`
  (если перестал быть частью блока — это смысловое решение)».

### R-COV-009 «slug папки не kebab-case»

- **severity**: `hint`.
- **scope**: все 4 kind.
- **проверка**: имя папки `[a-z0-9]+(-[a-z0-9]+)*`.
- **рекомендация**: «Переименовать через `/screen-deep-dive
  <kind>:<slug>` — скилл переименует папку и пересчитает ссылки».
