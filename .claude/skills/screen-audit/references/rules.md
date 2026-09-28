# Реестр правил `screen-audit`

Каждое правило: `id`, `severity`, `scope`, что проверяет, как проверять,
откуда норма, рекомендация в отчёт.

Категории:

- **R-SURF** — целостность хребта поверхностей (папка ↔ реестр `surface.md`).
- **R-XSURF** — изоляция поверхностей (ссылка не уходит наружу).
- **R-STRUCT** — структурная целостность (ошибки модели): ссылки,
  перечни, грамматика дерева, словарь компонентов, ключи состояний.
- **R-MIRROR** — синхронность зеркал (внутри screens и с interface).
- **R-SEM** — семантические подозрения, anti-patterns канона.
- **R-COV** — coverage и стиль.
- **R-RT** — карта экранов, маршруты, переходы и свод `map.md`.
- **R-CP** — контракты блоков и действий.
- **R-TX** — тексты интерфейса и реестр `texts.md`.
- **R-AX** — доступность.
- **R-MB** — узкий экран.

Слой экранов партиционирован по поверхности (surface): на каждую
поверхность из реестра `docs/projects/<project-slug>/surface.md` — папка
`docs/projects/<project-slug>/screens/<surface>/` с подпапками
`{flows,screens,blocks,shells}` и `assets/`. Сокращённо: `…/screens/` —
`docs/projects/<project-slug>/screens/<surface>/`; `…/interface/` —
`docs/projects/<project-slug>/interface/<surface>/` (зеркала **той же
поверхности**).

Правила R-STRUCT/R-MIRROR/R-SEM/R-COV и R-RT/R-CP/R-TX/R-AX/R-MB
применяются **в пределах одной поверхности**: ссылочные поля разрешаются
среди записей той же папки `…/screens/`, зеркала сверяются с
`…/interface/` той же поверхности.
Аудит итерирует по каждой папке поверхности из scope отдельно.
R-SURF/R-XSURF — про границу между поверхностями.

«Папка существует» — это `…/screens/<kind-folder>/<slug>/index.md`
читается без ошибок (`flows`, `screens`, `blocks`, `shells`).

`docs/projects/_template/screens/` — канон формы; из него читаются только
критерии, перечни, словарь состояний и anti-patterns, не данные. Узлы
`ui:` сверяются со словарём компонентов
`../design-deep-dive/kb/common/components.yaml` (раздел `types`, части —
`parts`, чужие имена — `aka`) и с расширениями проекта (раздел
`extensions` карты решений `docs/projects/<project-slug>/design/system.yaml`);
атрибуты узлов — с закрытым списком канона; имена `icon:` сверяет слой
дизайна.

Кроме папки поверхности аудит читает то, что называют правила: interface
той же поверхности; продуктовый слой того же проекта — `object.md`,
`action.md`, `capability/<surface>.md`, разделы `MVP` и `Devices and
accessibility` `vision.md`. Проверки — чтением по форме. Разбор дерева,
наборы состояний и свод `map.md` считают утилиты `tree`, `states`,
`screen_map` раздела `project` скилла дизайна
(`../design-deep-dive/scripts/README.md § project`); пока их файлов нет,
аудит проверяет то же чтением по канону. Пороги норм названы адресом
базы знаний скилла дизайна (короткий адрес «ux 04/01 §2» —
`../design-deep-dive/kb/INDEX.md` §1), числа из базы в правила не
копируются. Покрытие типов экранов компонентами дизайн-системы и
клавиатурный контракт расширений словаря проверяет `/design-audit`
(R-COV-005).

---

## R-SURF (хребет поверхностей)

### R-SURF-001 «папка поверхности вне реестра»

- **severity**: `error`.
- **scope**: подпапки `docs/projects/<project-slug>/screens/` ↔
  `surface.md`.
- **проверка**: каждая подпапка `screens/<X>/` имеет строку `slug: X` в
  реестре `docs/projects/<project-slug>/surface.md`. Хребет ведёт реестр
  — папки экранов для поверхности вне реестра быть не должно.
- **рекомендация**: «Завести строку `<X>` в `surface.md` через
  `/project-deep-dive <project-slug>`, либо удалить папку `screens/<X>/`
  (она осиротела относительно хребта)».

### R-SURF-002 «поверхность реестра без папки screens»

- **severity**: `hint` (coverage).
- **scope**: `surface.md` ↔ подпапки `screens/`.
- **проверка**: для каждой строки реестра `surface.md` маршрута
  приложения (`web` рода `app`; `admin`, `desktop`, `embed`) существует
  папка `screens/<slug>/`. Отсутствие — не ошибка модели, а непокрытая
  поверхность (экраны ещё не синтезировали).
- **рекомендация**: «Поверхность объявлена в `surface.md`, но её экраны
  ещё не начаты — завести через `/screen-deep-dive <project-slug>
  <slug>`, либо это сознательно отложено».

### R-SURF-003 «папка экранов у поверхности не маршрута приложения»

- **severity**: `error`.
- **scope**: подпапки `docs/projects/<project-slug>/screens/` ↔ `type` и
  `web-kind` строк `surface.md`.
- **проверка**: папка `screens/<X>/` есть только у поверхности `web`
  рода `app`; `admin`, `desktop` или `embed`. У `web` рода `landing` и
  `site` на месте экранов слой страницы `site/<X>/`, у `mobile` — слой
  `mobile/<X>/`, у `bot` — `telegram-bot-flow/<X>/`; у `web` без рода
  маршрута нет.
- **норма**: канон слоя (вступление, «Anti-patterns»); колонка
  `web-kind` — `docs/projects/_template/project/surface.md`.
- **рекомендация**: «Род или тип поверхности — через
  `/project-deep-dive <project-slug>`; смысл и тексты страницы — в слой
  страницы (`/design-deep-dive <project-slug> <X>`); папку экранов — удалить
  каскадом по подтверждению».

---

## R-XSURF (изоляция поверхностей)

### R-XSURF-001 «ссылка из одной поверхности в другую»

- **severity**: `error`.
- **scope**: все 4 kind любой папки `…/screens/`; зеркала с
  `…/interface/`.
- **проверка**: каждое slug-значение в ссылочном поле (внутрь screens
  или в interface) разрешается среди записей **той же** поверхности.
  Если slug не найден в своей поверхности, но найден в другой — это
  пересечение границы (а не просто битая ссылка R-STRUCT-001/002):
  поверхности изолированы. Зеркала `block.ux-substrates`,
  `screen.situations`/`who`/`blocks` сверяются с `interface/<surface>/`
  **той же** поверхности.
- **рекомендация**: «Поверхности изолированы — ссылка не должна уходить в
  чужую папку. Завести сущность в своей поверхности через
  `/screen-deep-dive <project-slug> <surface> <kind>`
  (или `/interface-deep-dive` для interface-источника той же
  поверхности), либо убрать ссылку. Общее между поверхностями сводит
  `/cross-audit`».

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
  - `screen.transitions-to-screen[].to` (массив записей) → `screens/<slug>/`
  - `screen.mobile-of` → `flows/<slug>/`
  - `block.used-by-screens` (массив) → `screens/<slug>/`
  - `block.tiles[].link` → `screens/<slug>/`
  - `block:<slug>` внутри `slot-fills`/`states` (screens) → `blocks/<slug>/`
  - `block:<slug>` внутри `tree` через `slots` (block-контейнер) → `blocks/<slug>/`
- **рекомендация**: «Завести stub через `/screen-deep-dive
  <project-slug> <surface> <kind>:<missing-slug>` или заменить ссылку на
  существующий slug этой поверхности».
- **примечание**: если slug отсутствует в своей поверхности, но есть в
  другой — это R-XSURF-001 (пересечение границы), а не битая ссылка.

### R-STRUCT-002 «валидность ссылок в interface той же поверхности»

- **severity**: `error`.
- **scope**: все 4 kind; зеркала — `…/interface/` той же поверхности.
- **проверка**: каждый interface-slug в ссылочном поле существует как
  строка в `…/interface/<file>.md` **той же поверхности**:
  - `flow.who` (массив) → `who.md`
  - `screen.situations` (массив) → `situation.md`
  - `screen.who` (массив) → `who.md`
  - `screen.zone` → `zone.md`
  - `block.interface-block` → `block.md`
  - `block.ux-substrates` (массив) → `ux-substrate.md`
  - `data:<slug>` (одиночный) или `data:<slug>.<field>` внутри
    `slot-fills`/`states` (screen), `tree` (block), `block.data`-карты,
    `form[].field`, `tiles[].value` → `data-items.md` (атрибут после
    точки — R-STRUCT-023)
- **рекомендация**: «Завести запись в interface той же поверхности через
  `/interface-deep-dive <project-slug> <surface> <kind>:<missing-slug>`
  (это другой скилл) или заменить ссылку на существующий interface-slug
  этой поверхности через `/screen-deep-dive <project-slug> <surface>
  <kind>:<slug>`».
- **примечание**: interface-slug, найденный только в другой поверхности —
  R-XSURF-001, не R-STRUCT-002.

### R-STRUCT-003 «дубликат slug»

- **severity**: `error`.
- **scope**: каждый kind в пределах поверхности независимо.
- **проверка**: внутри одного kind одной поверхности все `slug`
  уникальны (фактический дубль — два `slug:` с одним значением в разных
  папках одного kind). Файловая система не даст двух папок с одним
  именем, но `slug` во frontmatter может разойтись с именем папки — см.
  R-STRUCT-004. Совпадение slug между поверхностями — не дубль (записи
  изолированы), это норма.
- **рекомендация**: «Переименовать дубликат через
  `/screen-deep-dive <project-slug> <surface>` (каскадно правит
  ссылки)».

### R-STRUCT-004 «slug папки ≠ frontmatter.slug»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: имя папки `…/screens/<kind-folder>/<X>/` совпадает с
  `slug: <X>` в её `index.md`.
- **рекомендация**: «Привести в соответствие через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>` — скилл переименует папку и
  пересчитает ссылки».

### R-STRUCT-005 «status вне enum»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: `status` ∈ {`draft`, `stable`}.
- **рекомендация**: «Поправить status через `/screen-deep-dive <project-slug> <surface>
  <kind>:<slug>`».

### R-STRUCT-006 «поле экрана вне перечня»

- **severity**: `error`.
- **scope**: `screens/`.
- **проверка**: `viewport` ∈ {`desktop`, `mobile`, `any`}; `type` ∈
  {`dashboard`, `list`, `object`, `edit`, `wizard`, `settings`,
  `master-detail`, `canvas`, `auth`, `service`}; `access` ∈ {`public`,
  `authenticated`, `roles`}; `url-state` — подмножество {`tab`, `page`,
  `filters`, `sort`, `view`, `panel`} или `—`; `indexed`, `entrypoint` ∈
  {`true`, `false`}; `transitions-to-screen` — записи с ключами `to`,
  `trigger`, `keeps`, `back`.
- **норма**: форма `docs/projects/_template/screens/_template/screen.md`
  («Форма frontmatter»); канон слоя, «Экран: тип, карта и маршрут».
- **рекомендация**: «Выбрать значение из перечня через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>`».

### R-STRUCT-007 «поле слота каркаса вне перечня»

- **severity**: `error`.
- **scope**: `shells/`.
- **проверка**: для каждого слота `accepts` ∈
  {`block`, `tree`, `block | tree`, `block (modal/drawer)`}, `landmark` ∈
  {`main`, `navigation`, `complementary`, `region`, `—`}.
- **норма**: форма `docs/projects/_template/screens/_template/shell.md`.
- **рекомендация**: «Поправить поле слота через `/screen-deep-dive <project-slug> <surface>
  shell:<slug>`».

### R-STRUCT-008 «`shell.responsive` вне enum»

- **severity**: `error`.
- **scope**: `shells/`.
- **проверка**: для каждого `responsive[<bp>][<slot>]` —
  `bp` ∈ {`xs`, `sm`, `md`, `lg`, `xl`} (имена диапазонов, границы —
  токены `breakpoint.*` дизайн-системы), значение ∈
  {`visible`, `drawer-via-burger`, `overlay`, `stacked`, `hidden`,
  `fullscreen`, `bottom-sheet`}. Каждый `<slot>` в responsive есть в
  `shell.slots`.
- **норма**: форма `shell.md` («Форма frontmatter»); канон слоя, «Ключи
  `responsive` и брейкпоинты».
- **рекомендация**: «Поправить `responsive` через `/screen-deep-dive <project-slug> <surface>
  shell:<slug>`».

### R-STRUCT-009 «shell без `slots`»

- **severity**: `error`.
- **scope**: `shells/`.
- **проверка**: `shell.slots` непуст и не `—`. Для каждого слота указаны
  `required`, `accepts` и `landmark`.
- **рекомендация**: «Завести слоты через `/screen-deep-dive <project-slug> <surface>
  shell:<slug>`, либо удалить shell, если он бессодержателен».

### R-STRUCT-010 «block без `block-body`»

- **severity**: `error`.
- **scope**: `blocks/`.
- **проверка**: `block.tree` содержит зону `block-body` хотя бы с одним
  узлом.
- **рекомендация**: «Добавить `block-body` через `/screen-deep-dive <project-slug> <surface>
  block:<slug>` — это обязательная зона блока».

### R-STRUCT-011 «`screen.slot-fills` вводит слот, не объявленный в shell»

- **severity**: `error`.
- **scope**: `screens/` ↔ `shells/`.
- **проверка**: каждый ключ в `screen.slot-fills` есть в `shell.slots`
  у соответствующего `screen.shell`. То же для каждого слота, упомянутого
  в `screen.states[<state>]` (override).
- **рекомендация**: «Убрать неизвестный слот из `slot-fills`/`states`
  или объявить его в shell через `/screen-deep-dive <project-slug> <surface> shell:<shell-slug>`».

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
  через `/screen-deep-dive <project-slug> <surface> screen:<slug>` либо пересмотреть `accepts`
  через `/screen-deep-dive <project-slug> <surface> shell:<shell-slug>`».

### R-STRUCT-013 «незаполненный `required`-слот в screen»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: `screens/` ↔ `shells/`.
- **проверка**: для каждого слота shell c `required: true` —
  `screen.slot-fills[<slot>]` непуст и не `—`.
- **рекомендация**: «Заполнить слот через `/screen-deep-dive <project-slug> <surface>
  screen:<slug>`; либо сделать слот опциональным в shell, если
  это сознательное решение, через `/screen-deep-dive <project-slug> <surface> shell:<shell-slug>`».

### R-STRUCT-014 «slug блока (screens) ≠ slug interface-block»

- **severity**: `error`.
- **scope**: `blocks/`.
- **проверка**: `block.slug` совпадает с `block.interface-block` (одно
  имя на двух слоях — канон).
- **рекомендация**: «Привести slug к одному значению через
  `/screen-deep-dive <project-slug> <surface> block:<slug>` (каскадно переименует ссылки)».

### R-STRUCT-015 «flow с пустым `desktop` или пустым `mobile`»

- **severity**: `error`.
- **scope**: `flows/`.
- **проверка**: оба массива непусты.
- **рекомендация**: «Заполнить через `/screen-deep-dive <project-slug> <surface> flow:<slug>`,
  либо это не flow — удалить или переосмыслить как одиночный screen с
  `viewport: any`».

### R-STRUCT-016 «один screen-slug в `flow.desktop` и `flow.mobile`»

- **severity**: `error`.
- **scope**: `flows/`.
- **проверка**: множества `desktop` и `mobile` не пересекаются. На
  разных viewport — разные screen.
- **рекомендация**: «Развести в два screen-slug через
  `/screen-deep-dive <project-slug> <surface> flow:<slug>` (один — desktop, другой — mobile),
  либо это просто screen с `viewport: any` — удалить flow».

### R-STRUCT-017 «`flow.transitions` пересекает desktop ↔ mobile»

- **severity**: `error`.
- **scope**: `flows/`.
- **проверка**: для каждого `transitions[i]` — оба `from` и `to`
  принадлежат `flow.mobile` (transitions описывают только mobile-серию).
- **рекомендация**: «Удалить cross-viewport transition через
  `/screen-deep-dive <project-slug> <surface> flow:<slug>` — переходы desktop↔mobile не пишутся,
  это разные viewport одного flow».

### R-STRUCT-018 «`screen.transitions-to-screen` внутри одного flow»

- **severity**: `warning`.
- **scope**: `screens/` ↔ `flows/`.
- **проверка**: если оба screen упомянуты в одном `flow.mobile` —
  явный `transitions-to-screen` дублирует `flow.transitions`. Явный
  `transitions-to-screen` нужен для переходов наружу из flow.
- **рекомендация**: «Перенести переход в `flow.transitions` через
  `/screen-deep-dive <project-slug> <surface> flow:<flow-slug>`, либо подтвердить, что это
  выход наружу — тогда target screen не должен быть в той же mobile-
  серии».

### R-STRUCT-019 «незакрытое значение опционального ссылочного поля»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: опциональное ссылочное поле либо отсутствует, либо
  непустой массив/slug, либо `—`. Пустой массив `[]` без явного `—`,
  или ссылка на несуществующий slug — нарушают канон.
- **рекомендация**: «Поправить через `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`:
  убрать поле, поставить `—`, или указать существующий slug».

### R-STRUCT-020 «дерево не парсится»

- **severity**: `error`.
- **scope**: экраны (`slot-fills`, `states`), блоки (`tree`,
  `states`), каркасы (`tree`).
- **проверка**: ```yaml```-блок тела разбирается как YAML, и узлы
  следуют грамматике: узел без детей — строка-голова, узел с детьми —
  словарь из одного ключа-головы со списком детей, структурные атрибуты —
  словарь; голова — `<префикс>:<имя>` с парами `атрибут=значение` без
  пробелов внутри; префикс — `ui`, `layout`, `block`, `data`, `text`,
  `icon`. Корни: у блока — внутренние области `block-*`, у экрана —
  слоты и ключи состояний, у каркаса — список узлов. Утилита `tree`; без
  неё — разбор YAML и чтение по грамматике.
- **норма**: канон слоя, «Нотация дерева».
- **рекомендация**: «Привести дерево к грамматике через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>` (у папки с
  многими такими деревьями — пакет «Привести к канону»)».

### R-STRUCT-021 «компонент вне словаря»

- **severity**: `error`.
- **scope**: все деревья поверхности.
- **проверка**: каждый `ui:<Тип>` — ключ раздела `types` словаря
  компонентов или id расширения проекта; `ui:<Тип>.<Часть>` — часть из
  `parts` типа. Имя из `aka` — нарушение; находка называет тип, у
  которого это имя в `aka` (`Navbar` → `TopBar`, `Search` →
  `SearchInput`).
- **норма**: канон слоя, «Узлы» («Компонент — тип закрытого словаря»);
  правило 1 шапки `kb/common/components.yaml`.
- **рекомендация**: «Заменить на тип словаря через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`; потребность,
  которой в словаре нет, — расширение в слое дизайна
  (`/design-deep-dive <project-slug>`)».

### R-STRUCT-022 «ключ `states` вне словаря»

- **severity**: `error`.
- **scope**: экраны (`states`), блоки (`states`).
- **проверка**: каждый ключ — из словаря состояний экрана канона слоя
  (24 ключа, `empty-first-run` … `generating`). Идеальное состояние —
  `slot-fills`, ключа у него нет.
- **норма**: канон слоя, «Состояния экрана»; ux 06/01 §2.
- **рекомендация**: «Заменить ключом словаря через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`; ключ, за
  которым стоят несколько состояний словаря, скилл разбирает с
  аналитиком».

### R-STRUCT-023 «ссылка в продуктовый слой в пустоту»

- **severity**: `error`.
- **scope**: экраны, блоки, `texts.md` ↔ `object.md`,
  `action.md`, `capability/<surface>.md` того же проекта.
- **проверка**: `screen.object` и объектный тип в `screen.params` —
  объект таблицы «Объекты» `object.md`; `screen.main-task` — возможность
  файла **этой** поверхности (возможность другой поверхности —
  R-XSURF-001); `screen.key-action`, атрибут `action=`,
  `collection.bulk`, `tiles[].action`, `trigger` перехода-действия и
  колонка `action` реестра — действие `action.md`; колонка `object`
  реестра — объект; `data:<item>.<атрибут>` — атрибут таблицы «Атрибуты»
  у объекта, на который ссылается `data-items.object` датума. `—` по
  правилам формы — не ссылка. Существование проверяется здесь; тот ли
  это объект и та ли возможность по смыслу — `/cross-audit`.
- **норма**: канон слоя, «Связь с `interface/<surface>/` и продуктом»;
  форма `screen.md`.
- **рекомендация**: «Завести объект, действие или возможность через
  `/project-deep-dive <project-slug>` или поправить ссылку через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-024 «поле блока вне перечня»

- **severity**: `error`.
- **scope**: блоки.
- **проверка**: `source` ∈ {`screen`, `own`}; `form[].required` ∈ {`—`,
  `true`, `false`}; `collection.task` ∈ {`find`, `compare`,
  `one-record`, `act`}; `collection.volume` — `{typical, max}` числами;
  `collection.narrow` ∈ {`priority-columns`, `scroll-sticky`,
  `accordion-row`, `column-tabs`, `detail-screen`}; `tiles[].good` ∈
  {`up`, `down`, `target`}.
- **норма**: форма `docs/projects/_template/screens/_template/block.md`.
- **рекомендация**: «Выбрать значение из перечня через
  `/screen-deep-dive <project-slug> <surface> block:<slug>`».

### R-STRUCT-025 «основной каркас без состояний приложения»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: основной каркас (каркас рабочих экранов с
  навигацией).
- **проверка**: в теле есть раздел `## Состояния приложения` со
  строками `service-unavailable`, `maintenance`, `session-expiry`,
  `connection-lost`, `demo-mode`: у строки — где видно, форма и ключи
  текстов, либо «не применимо: причина».
- **норма**: форма `shell.md`, критерий 7 и раздел «Состояния
  приложения»; ux 04/08 §2.2; решение о сценарии истечения сессии —
  раздел `MVP` vision.
- **рекомендация**: «Объявить состояния приложения через
  `/screen-deep-dive <project-slug> <surface> shell:<slug>`; экраны их не
  повторяют».

---

## R-MIRROR (зеркала)

### R-MIRROR-001 «`block.ux-substrates` (screens) ↔ `block.ux-substrates` (interface)»

- **severity**: `error`.
- **scope**: `blocks/` ↔ `…/interface/<surface>/block.md` **той же поверхности**.
- **проверка**: для каждого блока B в screens — множество
  `B.ux-substrates` равно множеству `ux-substrates` строки с тем же
  slug в `…/interface/<surface>/block.md` **той же поверхности**. Сравнение как
  мультимножество (порядок не важен).
- **рекомендация**: «Пересинхронизировать через `/screen-deep-dive <project-slug> <surface>
  block:<slug>` — скилл переспросит источник правды (screens-вариант,
  interface-вариант, или смысловое расхождение → blocker)».

### R-MIRROR-002 «`block.used-by-screens` ↔ фактические ссылки на блок в screens»

- **severity**: `error`.
- **scope**: `blocks/` ↔ `screens/`.
- **проверка**: для каждого блока B — `B.used-by-screens` равно
  множеству screen-slug, в чьих `slot-fills` или `states` встречается
  `block:<B.slug>` (любое поле, любой state).
- **рекомендация**: «Пересчитать через `/screen-deep-dive <project-slug> <surface> block:<slug>`
  — `used-by-screens` выводимо из screens, скилл синхронизирует
  автоматически».

### R-MIRROR-003 «`screen.blocks` ↔ `block:` в `slot-fills`/`states`»

- **severity**: `error`.
- **scope**: `screens/`.
- **проверка**: для каждого screen S — `S.blocks` равно множеству
  block-slug, на которые ссылается `block:<slug>` в теле (slot-fills и
  states-override).
- **рекомендация**: «Пересчитать через `/screen-deep-dive <project-slug> <surface> screen:<slug>`
  — `blocks` выводимо из тела, скилл синхронизирует автоматически».

### R-MIRROR-004 «`screen.viewport` несовместим с участием в flow»

- **severity**: `error`.
- **scope**: `screens/` ↔ `flows/`.
- **проверка**:
  - если screen упомянут в `flow.desktop` — `viewport` ∈ {`desktop`, `any`};
  - если в `flow.mobile` — `viewport` ∈ {`mobile`, `any`}.
- **рекомендация**: «Поправить через `/screen-deep-dive <project-slug> <surface> screen:<slug>`
  (привести viewport к согласованному значению) или через
  `/screen-deep-dive <project-slug> <surface> flow:<flow-slug>` (исключить screen из не своей
  серии)».

### R-MIRROR-005 «`screen.mobile-of` ↔ `flow.mobile`»

- **severity**: `error`.
- **scope**: `screens/` ↔ `flows/`.
- **проверка**: если `screen.mobile-of = <flow-slug>` — `screen.slug` ∈
  `flow.mobile` указанного flow.
- **рекомендация**: «Привести через `/screen-deep-dive <project-slug> <surface> screen:<slug>`
  (убрать `mobile-of` или сменить на правильный flow) или через
  `/screen-deep-dive <project-slug> <surface> flow:<flow-slug>` (добавить screen в `mobile`)».

---

## R-SEM (семантика, anti-patterns канона)

Все маркеры ниже — индикаторы; срабатывание означает «подозрение, проверь».
Аналитик имеет право объяснить «нет, это не так», и при подтверждении
warning не превращается в правку.

### R-SEM-001 «облик в дереве»

- **severity**: `warning`.
- **scope**: `screens/` (slot-fills, states), `blocks/` (tree),
  `shells/` (tree, responsive).
- **проверка**: в любом узле дерева присутствуют маркеры облика:
  - hex-цвета: `#` сразу за которым цифра/буква a-f (например, `#fff`,
    `#ab12cd`);
  - токены цвета: `color:`, `background:`, `bg=`, `bg-` с дальнейшим
    значением;
  - пиксельные значения: число + `px` (например, `16px`, `8px`);
  - типографика: `font`, `font-size`, `font-weight`, `line-height`,
    `letter-spacing`;
  - вид и размер компонента: `variant=`, `size=`;
  - сырой стиль: `style=`.
- **норма**: канон слоя, «Нотация дерева», «Атрибуты», «Anti-patterns».
- **рекомендация**: «Облик в артефакт экранов не пишется: его решает
  слой дизайна `design/` токенами дизайн-системы, макет собирает он же.
  Убрать из артефакта через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`; уровень
  действия, если он был выражен видом, — атрибут `level`».

### R-SEM-002 «оси контекста в дереве»

- **severity**: `warning`.
- **scope**: `screens/`, `blocks/`, `shells/`.
- **проверка**: в любом узле, атрибуте узла или поле frontmatter
  присутствует маркер оси: `scheme=` / `brand=` / `density=` / `dir=`
  (и варианты с `:`). Тема (цветовая схема), бренд, плотность и
  направление письма — оси контекста приложения: их задаёт корень
  приложения в коде, а не узел дерева. Аналитик может объяснить
  исключение и снять подозрение.
- **рекомендация**: «Убрать ось контекста из узла через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>` — ось
  контекста задаёт корень приложения в коде, а не узел дерева».

### R-SEM-003 «FSD-имена в дереве или frontmatter»

- **severity**: `warning`.
- **scope**: `screens/`, `blocks/`, `shells/`, `flows/`.
- **проверка**: упоминания `widget:`, `feature:`, `entity:`, путей
  `pages/`, `widgets/`, `features/`, `entities/`, имён с суффиксом
  `Widget`, `Feature`, `Page` в значениях полей или в узлах дерева.
- **рекомендация**: «Карта слайсов ведётся в `fsd/<surface>/`
  (`/fsd-deep-dive`), screens остаются чистой композицией. Убрать
  FSD-имена через `/screen-deep-dive <project-slug> <surface>
  <kind>:<slug>`».

### R-SEM-004 «breakpoints в `slot-fills` или `block.tree`»

- **severity**: `warning`.
- **scope**: `screens/` (slot-fills, states), `blocks/` (tree).
- **проверка**: ключи или маркеры `xs:`, `sm:`, `md:`, `lg:`, `xl:`
  в slot-fills (screen) или tree (block). В этих местах breakpoints
  жить не должны — облицовочный адаптив только в `shell.responsive`,
  структурный — через `flow`.
- **рекомендация**: «Перенести в `shell.responsive` через
  `/screen-deep-dive <project-slug> <surface> shell:<shell-slug>` (облицовочный адаптив) либо
  оформить как `flow` через `/screen-deep-dive <project-slug> <surface> flow:<slug>`
  (структурный — разные viewport → разные screen)».

### R-SEM-005 «inline-cтейты в `block.tree`»

- **severity**: `warning`.
- **scope**: `blocks/`.
- **проверка**: в `block.tree` присутствуют узлы-индикаторы состояний
  (`ui:Spinner`, `ui:Skeleton`, `ui:Progress`, `ui:Alert`, `ui:Toast` и
  подобные по смыслу), либо композиция, явно изображающая
  загрузку, пустоту или ошибку (текст вида «не удалось…», «пока нет…» как
  состояние, а не контент). Индикатор длительного действия с действием
  остановки (`duration: long`) — содержимое, а не состояние.
- **норма**: канон слоя, «Частные правила» (блок со своим источником).
- **рекомендация**: «Состояния — в `states` экрана, а у блока со своим
  источником (`source: own`) — в его разделе `states`. Перенести через
  `/screen-deep-dive <project-slug> <surface> screen:<потребитель>` или
  `block:<slug>`».

### R-SEM-006 «один `data:<slug>` под разными именованными слотами `block.data`»

- **severity**: `warning`.
- **scope**: `blocks/`.
- **проверка**: в `block.data: { <param>: data:<slug> }` один и тот же
  `data:<slug>` фигурирует в двух разных `<param>`.
- **рекомендация**: «Переиспользовать data-items напрямую через одно
  имя; перепроектировать через `/screen-deep-dive <project-slug> <surface> block:<slug>`».

### R-SEM-007 «слотовый узел shell непуст»

- **severity**: `warning`.
- **scope**: `shells/`.
- **проверка**: узел дерева shell с атрибутом `fills=$<slot>` в голове не
  имеет вложенных детей. Содержимое слота — задача screen, не shell.
- **рекомендация**: «Очистить слотовый узел через `/screen-deep-dive <project-slug> <surface>
  shell:<slug>` — содержимое идёт через `screen.slot-fills`».

### R-SEM-008 «пустой обязательный слот frontmatter»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: все 4 kind; список обязательных слотов по kind — в
  `screen-deep-dive/references/field-checklists.md` и в `Форма
  frontmatter` каждого файла-формы (`_template/<kind>.md`).
- **проверка**: для каждой записи — каждый обязательный слот непуст
  и не `—`.
- **рекомендация**: «Заполнить через `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`;
  для stable обязательные слоты не могут быть пусты».

### R-SEM-009 «`description` совпадает с `name`»

- **severity**: `warning`.
- **scope**: все 4 kind.
- **проверка**: `description` после трима/lowercase = `name` или
  содержится в `name` целиком, не добавляя смысла.
- **рекомендация**: «`description` должен пояснять что/зачем, а не
  повторять `name` — уточнить через `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-SEM-010 «`screen.situations` не покрывает ситуации экрана»

- **severity**: `warning`.
- **scope**: `screens/` ↔ `blocks/` ↔ `…/interface/<surface>/ux-substrate.md`.
- **проверка**: вывод множества «ситуаций, чьи ux-substrates есть на
  экране» — через `screen.blocks → block.ux-substrates →
  ux-substrate.situation` (поле `situation` в `…/interface/<surface>/ux-substrate.md`).
  Если какая-то такая ситуация отсутствует в `screen.situations` —
  warning.
- **рекомендация**: «Дополнить `screen.situations` через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>` (скилл предложит точечный батч)».

### R-SEM-011 «обязательный набор состояний не покрыт»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: экраны, блоки с `source: own`.
- **проверка**: набор экрана — объединение условий канона:
  `loading-initial` и `error-load` — экран грузит данные;
  `empty-first-run` и `partial-few` — на экране есть коллекция,
  `empty-filtered` — поиск или фильтр; строка типа экрана и строка
  «Экран или маршрут целиком» таблицы типов (строки матрицы ux 06/01
  §3.1); строки компонентов блоков — у типов с ключом `screen_states`
  словаря; `no-permission` — `access: roles`; `not-found` — параметр
  объекта в `params`; `offline` — поверхность работает без сети (раздел
  «Решения» `map.md`); `stale` — живые данные; отказы ситуаций экрана
  (`situation.refusals`); `in-progress-background` — действие экрана у
  возможности с `duration: background`. Каждое состояние набора — дельта
  хотя бы одного слота или `'не применимо: причина'` с непустой
  причиной. У блока с `source: own` набор — `loading-initial`,
  `error-load`, у коллекции ещё `empty-first-run`, `empty-filtered`,
  `partial-few`. Утилита `states`; без неё — сборка набора по списку
  канона.
- **норма**: канон слоя, «Обязательный набор», «Частные правила»; ux
  06/01 §2, §3.1.
- **рекомендация**: «Дописать дельты или причины «не применимо» через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>` (у блока —
  `block:<slug>`); «продумай состояния» словами набор не заменяет».

### R-SEM-012 «flow с одним screen и в `desktop`, и в `mobile`»

- **severity**: `warning`.
- **scope**: `flows/`.
- **проверка**: `len(flow.desktop) == 1 AND len(flow.mobile) == 1` И
  оба указывают на разные screen-slug, при этом `mobile` содержит ровно
  один экран. Если на mobile один экран и на desktop один — это не
  flow (нечего разводить).
- **рекомендация**: «Это не flow — переосмыслить через
  `/screen-deep-dive <project-slug> <surface> flow:<slug>` (удалить, заменить на один screen с
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
  `/screen-deep-dive <project-slug> <surface> flow:<slug>`. Если облицовка осознанная — ответ
  аналитика снимает подозрение».

### R-SEM-014 «атрибут или ключ структуры вне списка»

- **severity**: `warning`.
- **scope**: все деревья поверхности.
- **проверка**: атрибуты узла `ui:` — только `level`, `action`,
  `illustration`, `items`, `columns`, `value`, `fills`; узла `layout:` —
  только `gap`, `justify`, `align`, `wrap`, `columns`, `areas`, `fill`,
  `span`, `fills`; ключи структуры — `items`, `columns`, `areas`, `fill`,
  `children`. Значения: `level` ∈ {`primary`, `secondary`, `tertiary`};
  `gap` — имя токена группы `space` дизайн-системы, а не число;
  `illustration` — только у `ui:EmptyState`; `fills` — только в дереве
  каркаса. Один атрибут — в одном месте узла (не в голове и в структуре
  сразу). Метафору иллюстрации по списку паспорта визуала сверяет
  `/design-audit` (R-REF-007).
- **норма**: канон слоя, «Атрибуты», «Нотация дерева».
- **рекомендация**: «Снять атрибут или перенести решение туда, где оно
  живёт (облик — слой дизайна, ось контекста — корень приложения), через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-SEM-015 «частное правило состояний нарушено»

- **severity**: `warning`.
- **scope**: экраны (`states`), блоки (`states`), каркасы.
- **проверка** (чтением дельт):
  - `not-found` описывает объект в архиве или корзине — это
    `archived-deleted`; маршрут вне реестра описан состоянием — это
    служебный экран `type: service`;
  - `generating` без действия остановки;
  - экран повторяет состояния приложения (сервис недоступен, плановые
    работы, истечение сессии, нет связи, демо-режим) вместо раздела
    основного каркаса;
  - главная кнопка видна в шапке, а пустое состояние дублирует её
    главной кнопкой; на экране с несколькими пустыми состояниями — не
    только текст и третичные кнопки;
  - дельта `offline` не называет, что доступно из кэша, что отложено и
    какие статусы у отложенных правок.
- **норма**: канон слоя, «Частные правила»; ux 06/01 §4.8; ux 13/03 §6.
- **рекомендация**: «Поправить дельту через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

---

## R-COV (coverage и стиль)

### R-COV-001 «shell без screens»

- **severity**: `hint`.
- **scope**: `shells/`.
- **проверка**: для каждого `shell.slug` есть хотя бы один screen с
  `screen.shell == slug`.
- **рекомендация**: «Завести screen с этим shell через
  `/screen-deep-dive <project-slug> <surface> screen` либо удалить shell через
  `/screen-deep-dive <project-slug> <surface>` (каскадно)».

### R-COV-002 «block без потребителей»

- **severity**: `hint`.
- **scope**: `blocks/`.
- **проверка**: блок не упомянут ни в одном `screen.blocks` и ни в
  одном `block:<slug>` в slot-fills/states/tree.
- **рекомендация**: «Завести screen с этим блоком через
  `/screen-deep-dive <project-slug> <surface> screen`, либо удалить блок через
  `/screen-deep-dive <project-slug> <surface> block:<slug>` (каскадно)».

### R-COV-003 «screen недостижим»

- **severity**: `hint` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: экраны, каркасы, потоки, `map.md`.
- **проверка**: обход от стартовых экранов ролей (`entrypoint: true`,
  роль — `who` экрана). Из достигнутого экрана достижимы: цели его
  `transitions-to-screen`; экраны мобильной серии его потока по
  `flow.transitions`; экраны зон, которые стоят пунктами навигации
  основного каркаса (раздел «Навигация» `map.md`) для той же роли. Экран,
  до которого обход не дошёл ни от одной его роли, — находка; у
  поверхности с экранами нет ни одного стартового — `error`. Служебные
  экраны (`type: service`) достижимы по определению.
- **норма**: канон слоя, «Экран: тип, карта и маршрут»; ux 05/02 §9.
- **рекомендация**: «Сделать экран стартовым для роли, добавить переход
  или пункт навигации через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>`, либо удалить
  (каскадно)».

### R-COV-004 «stable ссылается на draft»

- **severity**: `hint`.
- **scope**: все ссылочные поля внутри screens.
- **проверка**: запись со `status: stable` имеет ссылку на запись с
  `status: draft` (внутри screens; ссылки в interface проверяет
  `interface-audit`).
- **рекомендация**: «Не блокирует stable, но стоит докопать draft-
  соседа: `/screen-deep-dive <project-slug> <surface> <kind>:<slug-соседа>`».

### R-COV-005 «короткое `description`»

- **severity**: `hint`.
- **scope**: все 4 kind.
- **проверка**: длина `description` меньше 10 символов.
- **рекомендация**: «`description` слишком короткое для смысловой
  ясности; уточнить через `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-COV-006 «asset-файл из `assets: [...]` не существует»

- **severity**: `error`.
- **scope**: все 4 kind.
- **проверка**: для каждой записи `assets: [f1, f2, ...]` —
  `…/screens/assets/<kind>/<slug>/<fN>` существует как файл.
- **рекомендация**: «Удалить отсутствующий файл из `assets` через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`, либо положить файл в
  `…/screens/assets/<kind>/<slug>/`».

### R-COV-007 «`ux-substrate` не представлен узлом в `block.tree`»

- **severity**: `hint` (если `status: draft`), `warning` (если
  `status: stable`).
- **scope**: `blocks/`.
- **проверка**: для каждого `block.ux-substrates[i]` — в `block.tree`
  есть узел, которому этот субстрат соответствует (по типу узла и
  назначению субстрата: `ввод` — поле, `команда` — действие, `список` —
  коллекция). Полностью автомат не сделает; спорные — оставлять для
  аналитика.
- **рекомендация**: «Раскрыть субстрат узлом дерева через
  `/screen-deep-dive <project-slug> <surface> block:<slug>` или убрать его из `ux-substrates`
  (если перестал быть частью блока — это смысловое решение)».

### R-COV-008 «slug папки не kebab-case»

- **severity**: `hint`.
- **scope**: все 4 kind.
- **проверка**: имя папки `[a-z0-9]+(-[a-z0-9]+)*`.
- **рекомендация**: «Переименовать через `/screen-deep-dive <project-slug> <surface>
  <kind>:<slug>` — скилл переименует папку и пересчитает ссылки».

---

## R-RT (карта экранов, маршруты, переходы)

Карта экранов и реестр маршрутов — поля экранов; `map.md` — их свод и
решения «один раз на приложение». Канон — экраны: расхождение свода —
находка здесь, правят экран и пересобирают свод.

### R-RT-001 «маршрут не уникален или вне реестра»

- **severity**: `error`.
- **scope**: экраны, `map.md` («Маршруты»).
- **проверка**: один маршрут — один экран на вьюпорт: общий `route`
  допустим только у экранов одного потока на разных вьюпортах. Каждый
  маршрут экрана — строка «Маршрутов», каждая строка «Маршрутов» —
  маршрут существующего экрана, строка-запрет «маршрутов вне списка
  нет» на месте. Служебные маршруты (маршрут вне реестра, ошибка
  сервиса, плановые работы) — экраны `type: service`, если их решил
  раздел `MVP` vision.
- **норма**: канон слоя, «Экран: тип, карта и маршрут» («Реестр
  маршрутов закрыт»); форма `map.md`; ux 13/04 §15.
- **рекомендация**: «Развести маршруты или завести экран через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>`, затем
  пересобрать свод — `/screen-deep-dive <project-slug> <surface> map`».

### R-RT-002 «тупик: экрану некуда вести»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: экраны.
- **проверка**: у экрана нет исходящих переходов
  (`transitions-to-screen`, переходы его мобильной серии в потоке), а его
  дерево не даёт двух и больше действий «что дальше» (узлы с `action=`,
  ссылки на экраны). Навигация каркаса — путь, а не продолжение задачи:
  она «что дальше» не заменяет. Служебный экран с путём на стартовый
  экран роли — не тупик.
- **норма**: ux 05/02 §5.4, §9; «Конечные состояния» сценария interface
  той же поверхности.
- **рекомендация**: «Назвать переходы или действия «что дальше» через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>`».

### R-RT-003 «переход без обратного пути»

- **severity**: `warning`.
- **scope**: экраны (`transitions-to-screen`).
- **проверка**: у записи перехода `back` пуст: не назван путь назад и
  не записано `irreversible`.
- **норма**: форма `screen.md` (`transitions-to-screen`); ux 05/02 §9.
- **рекомендация**: «Назвать, как вернуться, или отметить необратимость
  через `/screen-deep-dive <project-slug> <surface> screen:<slug>`».

### R-RT-004 «навигация глубже нормы, с дублем или на экране»

- **severity**: `error` — видимых уровней больше нормы; `warning` — дубль
  пункта или узел навигации в дереве экрана.
- **scope**: `map.md` («Навигация»), основной каркас, экраны.
- **проверка**: видимых уровней навигации в боковой панели — не больше
  нормы ux 13/04 §16; пункт не повторяется в двух панелях; узел навигации
  (`items=nav`) — в дереве основного каркаса, а не в `slot-fills` или
  `states` экрана: состав и порядок пунктов от экрана не зависят.
- **норма**: канон слоя, «Экран: тип, карта и маршрут» («Навигация —
  узел дерева основного каркаса»); форма `map.md` («Свод»).
- **рекомендация**: «Поднять уровни в зоны или вкладки объекта, убрать
  дубль, перенести навигацию в каркас через
  `/screen-deep-dive <project-slug> <surface> shell:<slug>`».

### R-RT-005 «список без состояния в адресе»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: экраны с `type: list` или `master-detail`.
- **проверка**: `url-state` задан и не `—`: фильтры, сортировка,
  страница, открытая панель — что есть на экране. Порог коллекции, после
  которого состояние в адресе нужно и другим экранам, — R-CP-007.
- **норма**: форма `screen.md` (`url-state` обязателен у `list` и
  `master-detail`); канон слоя, «Экран: тип, карта и маршрут».
- **рекомендация**: «Назвать, что живёт в адресе, через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>`».

### R-RT-006 «раздел «Переход» пуст или без проверки»

- **severity**: `warning` (если `map.md` в `draft`), `error` (если
  `map.md` в `stable`).
- **scope**: `map.md` («Переход») ↔ экраны
  (`transitions-to-screen[].keeps`).
- **проверка**: раздел есть; у каждой строки — где живёт, срок, что
  переживает, как проверить; каждое `keeps` переходов экранов — предмет
  строки раздела: экран не обещает того, чего «Переход» не держит.
- **норма**: форма `map.md` (критерий 5, «Решения поверхности»); ux 13/04
  §13; ux 05/05 §9.
- **рекомендация**: «Дописать строки и способ проверки через
  `/screen-deep-dive <project-slug> <surface> map`».

### R-RT-007 «экраны по шаблону или без объекта»

- **severity**: `warning`.
- **scope**: экраны, `map.md` («Решения»).
- **проверка**: при четырёх и больше экранах поверхности типы не все
  одинаковы; у экрана с `object: —` есть строка «Решений» с причиной;
  экран без объекта и без роли («главная», «обзор») — находка. Значение
  `type` вне перечня — R-STRUCT-006.
- **норма**: канон слоя, «Экран: тип, карта и маршрут»; ux 13/04 §14.
- **рекомендация**: «Назвать тип, объект или решение «без объекта» через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>`».

### R-RT-008 «свод `map.md` расходится с экранами»

- **severity**: `warning` (если `map.md` в `draft`), `error` (если
  `map.md` в `stable`); нет `map.md` у поверхности с экранами —
  `warning`, при stable-экранах — `error`.
- **scope**: `map.md` ↔ экраны, зоны interface той же поверхности,
  основной каркас.
- **проверка**: frontmatter — `surface` (slug папки) и `status`, разделы
  формы на месте. Строка «Карты экранов» и «Маршрутов» — на каждый экран
  и ни одной без экрана; значения строк совпадают с полями экрана; выводимые
  колонки — по правилам раздела «Свод» формы. «Навигация» — пункты из
  корневых зон interface с `order` и их дочерних зон, видимость — из
  `who` и `access` экранов. Утилита `screen_map`; без неё — сверка
  чтением.
- **норма**: форма `map.md` (критерии 1–3, «Свод»).
- **рекомендация**: «Пересобрать свод по экранам через
  `/screen-deep-dive <project-slug> <surface> map`: канон — экраны, свод
  руками не правят».

### R-RT-009 «решение поверхности без основания»

- **severity**: `hint` (если `map.md` в `draft`), `error` (если `map.md`
  в `stable`).
- **scope**: `map.md` («События», «Конвенции», «Узкий экран»,
  «Решения»).
- **проверка**: у строки авторского раздела — решение и основание
  (адрес нормы или решение владельца); у «Решений» — ещё кто теряет;
  пустой авторский раздел у stable-свода — находка. Полноту разделов по
  составу проверяют R-CP-001 («События»), R-AX-003 («Конвенции»),
  R-MB-002 («Узкий экран»).
- **норма**: форма `map.md` (критерий 4, «Статус»); ux 13/04 §28.
- **рекомендация**: «Назвать основание через
  `/screen-deep-dive <project-slug> <surface> map`; формулировки
  решений — аналитика и бизнеса».

---

## R-CP (контракты блоков и действий)

Контракт действия собирается из словаря действий, матрицы, атрибутов
узла, переходов и строки «Событий»; контракты формы, коллекции и плитки
блок несёт во frontmatter (канон слоя, «Контракты блоков»; форма
`block.md`). Пороги — адресом базы, числа в правила не копируются.

### R-CP-001 «действие без события»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: деревья экранов и блоков ↔ `map.md` («События»).
- **проверка**: у каждого действия, названного атрибутом `action=`, есть
  строка «Событий» с формой сообщения. Действие есть в словаре —
  R-STRUCT-023.
- **норма**: форма `map.md`, критерий 6; канон слоя, «Контракты блоков»
  (результат); ux 04/10 §1.1.
- **рекомендация**: «Завести строку события через
  `/screen-deep-dive <project-slug> <surface> map`».

### R-CP-002 «главное действие не одно или разрушительное»

- **severity**: `error`.
- **scope**: экраны вместе с блоками их слотов.
- **проверка**: вне оверлеев на экране — не больше одного узла
  `level=primary`; второй допустим только в блоке со своим источником
  (`source: own`); действие с `reversibility` `soft-delete` или
  `irreversible` (`action.md`) не стоит с `level=primary`.
- **норма**: канон слоя, «Контракты блоков»; ux 04/10 §1.2.
- **рекомендация**: «Понизить уровень лишнего действия через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-CP-003 «защита не по обратимости»

- **severity**: `warning`.
- **scope**: деревья ↔ сценарии и ситуации interface той же поверхности.
- **проверка**: у действия с `reversibility: irreversible` — шаг защиты в
  сценарии и в дереве (подтверждение `ui:ConfirmModal` или иной шаг
  защиты); частое обратимое действие (`undo` в ситуации с `frequency`
  `hours-daily` или `daily`) не стоит за подтверждением — у него отмена.
- **норма**: канон слоя, «Контракты блоков» (защита); ux 05/03 §7.2.
- **рекомендация**: «Добавить шаг защиты или заменить подтверждение
  отменой через `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`;
  шаг сценария — `/interface-deep-dive`».

### R-CP-004 «контракт поля формы неполон»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`); тип, длины или перечень поля в `form` вместо ссылки
  на атрибут — `warning`.
- **scope**: блоки с субстратом `ввод` или `выбор`.
- **проверка**: `form` есть; у записи — `field` (`data:<item>.<атрибут>`),
  `control`, `required`, `format`, `validation`, `error`, `default`,
  `autocomplete`; `control` — тип узла, привязанного к полю в дереве;
  `error` — ключ `text:` строки роли `error`; `default` и `autocomplete` —
  значение или «нет: причина».
- **норма**: форма `block.md` («Контракт поля формы»); ux 04/05 §1.1.
- **рекомендация**: «Дописать запись поля через
  `/screen-deep-dive <project-slug> <surface> block:<slug>`; правило поля
  формулирует аналитик, инвариант домена — архитектор».

### R-CP-005 «контрол не по числу вариантов»

- **severity**: `warning`.
- **scope**: блоки (`form[].control`) ↔ «Атрибуты» `object.md`.
- **проверка**: контрол согласован с числом значений атрибута (`values`)
  и числом выборов по таблице ux 04/06 §1: одиночный выбор из немногих —
  радиогруппа, из среднего числа — список выбора, из многих — поле с
  автодополнением; несколько выборов — флажки или список; да или нет —
  переключатель или флажок.
- **норма**: ux 04/06 §1.
- **рекомендация**: «Сменить контрол через
  `/screen-deep-dive <project-slug> <surface> block:<slug>`».

### R-CP-006 «форма тяжелее нормы или согласие включено»

- **severity**: `warning`.
- **scope**: блоки (`form`).
- **проверка**: число полей на шаге и в модальном окне — в пределах ux
  04/05 §2.5; поле согласия по умолчанию выключено.
- **норма**: ux 04/05 §2.5; форма `block.md`.
- **рекомендация**: «Разбить форму на шаги или вынести из модального
  окна, выключить согласие по умолчанию через
  `/screen-deep-dive <project-slug> <surface> block:<slug>`».

### R-CP-007 «коллекция без объёма или без инструментов объёма»

- **severity**: объём не объявлен — `warning` (если `status: draft`),
  `error` (если `status: stable`); нет инструмента по порогу — по пометке
  основания строки таблицы ux 04/01 §2: `[система]` или `[консенсус]` —
  `error`, прочие — `warning`.
- **scope**: блоки с `ui:Table`, `ui:List`, `ui:TreeView`,
  повторяемой `ui:Card`; экраны, где они стоят.
- **проверка**: `collection` есть и `volume` объявлен; по `volume.max` и
  числу видимых колонок — инструменты строк порогов ux 04/01 §2.1–§2.2:
  пагинация и поиск или фильтр в дереве, управление колонками, `url-state`
  у экрана, массовые действия (`bulk`) и экспорт.
- **норма**: форма `block.md` («Контракт коллекции»); ux 04/01 §2.
- **рекомендация**: «Объявить объём или добавить инструмент через
  `/screen-deep-dive <project-slug> <surface> block:<slug>`; числа объёма
  — от аналитика».

### R-CP-008 «модальное окно не для этой задачи»

- **severity**: `warning`.
- **scope**: блоки в слотах `accepts: block (modal/drawer)`, деревья с
  `ui:Modal`.
- **проверка**: форма в модальном окне — в пределах ux 04/05 §2.5 и без
  вложенных оверлеев; правка строки таблицы — не в модальном окне;
  модальное окно открывает человек, событие системы — не модальное окно.
- **норма**: ux 04/07 §1; тип `Modal` словаря компонентов (`use_instead`).
- **рекомендация**: «Вынести задачу в экран или панель через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-CP-009 «ошибка тостом или одно событие — две формы»

- **severity**: `error`.
- **scope**: `map.md` («События»), деревья состояний.
- **проверка**: у ошибки форма сообщения — не тост: ни в строке
  «Событий», ни узлом `ui:Toast` в дельте ошибки; одно событие — одна
  строка «Событий» и одна форма на всём продукте.
- **норма**: форма `map.md` («События»); ux 04/08 §2.2; тип `Toast`
  словаря компонентов.
- **рекомендация**: «Выбрать одну форму по строке развилки через
  `/screen-deep-dive <project-slug> <surface> map`».

### R-CP-010 «длительное действие без индикатора»

- **severity**: `warning`.
- **scope**: экраны с действиями возможностей, у которых в паспорте
  `duration` `long` или `background`.
- **проверка**: `long` — в дереве индикатор (`ui:Progress`) и действие
  остановки; `background` — `in-progress-background` в наборе экрана
  (R-SEM-011) и сообщение о завершении.
- **норма**: канон слоя, «Контракты блоков» (длительность); ux 06/02
  §2.2, §5.2.
- **рекомендация**: «Добавить индикатор и остановку или фоновое
  состояние через `/screen-deep-dive <project-slug> <surface> screen:<slug>`».

### R-CP-011 «плитка показателя без контракта»

- **severity**: `warning`; число плиток верхнего ряда вне нормы — `hint`.
- **scope**: блоки с `ui:KpiTile`.
- **проверка**: `tiles` есть; у записи — `value`, `question`,
  `precision`, `baseline`, `good`, `thresholds`, `delta`, `period`,
  `link`, `action`, `no-data`; незаполненное поле — решение «показатель
  не выводить», названное аналитиком; число плиток верхнего ряда — по ux
  04/03 §4.3.
- **норма**: форма `block.md` («Контракт плитки показателя»); ux 04/03
  §4.3.
- **рекомендация**: «Дописать контракт через
  `/screen-deep-dive <project-slug> <surface> block:<slug>`; вопрос, базу
  и пороги формулирует бизнес или аналитик».

### R-CP-012 «частое действие только в меню»

- **severity**: `warning`.
- **scope**: деревья экранов ↔ ситуации interface той же поверхности.
- **проверка**: действие ситуации экрана с `frequency` `hours-daily` или
  `daily` стоит только внутри `ui:Menu`, узла на виду нет.
- **норма**: канон слоя, «Контракты блоков»; ux 04/10 §1.2.
- **рекомендация**: «Вынести действие на виду через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

---

## R-TX (тексты интерфейса)

Тексты поверхности живут в реестре `texts.md`, в дереве — ключ
`text:<key>` (канон слоя, «Тексты интерфейса»; форма `texts.md`).
Словарь запретов и межстрочные проверки строка проходит на этапе «тексты
интерфейса»; аудит проверяет форму реестра, ключи, роли и статусы.
Утверждённые строки к чистовому макету сверяет `/design-audit`.

### R-TX-001 «ключ текста без строки реестра»

- **severity**: `error`.
- **scope**: деревья экранов, блоков и каркасов, раздел «Состояния
  приложения» каркаса, `form[].error`, `tiles[].no-data`.
- **проверка**: каждый `text:<key>` — строка `texts.md` той же
  поверхности.
- **норма**: канон слоя, «Тексты интерфейса», «Данные и тексты в
  дереве».
- **рекомендация**: «Завести строку через
  `/screen-deep-dive <project-slug> <surface> texts`».

### R-TX-002 «роль строки не совпала с ролью части»

- **severity**: `error`.
- **scope**: деревья ↔ `texts.md`.
- **проверка**: роль строки (`role`) — роль текстовой части, под которой
  стоит узел, по разделу `text_roles` словаря компонентов (под
  `ui:Button` — `action`, под `ui:Field.Error` — `error`, под
  `ui:EmptyState` — `empty`); у части с двумя ролями — одна из них;
  последний сегмент ключа — роль строки. Текст вне компонента — роль по
  месту (заголовок экрана — `title`) и по правилу «Тексты состояний»
  канона.
- **норма**: канон слоя, «Тексты интерфейса», «Частные правила»; раздел
  `text_roles` `kb/common/components.yaml`; ux 07/06 §7.2.
- **рекомендация**: «Поправить роль строки или узел через
  `/screen-deep-dive <project-slug> <surface> texts`».

### R-TX-003 «литерал текста в дереве»

- **severity**: `error` (если `status: stable`), `hint` (если
  `status: draft`).
- **scope**: все деревья поверхности.
- **проверка**: строка-лист в кавычках или `label:` с литералом вместо
  ключа `text:<key>`.
- **норма**: канон слоя, «Данные и тексты в дереве».
- **рекомендация**: «Заменить ключом со строкой реестра `assumed` через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-TX-004 «строка stable-экрана ниже `checked`»

- **severity**: `error`.
- **scope**: stable-экраны вместе с блоками их слотов и каркасом.
- **проверка**: каждый ключ дерева — строка со статусом `checked` или
  `approved`. Утверждение владельцем для stable экрана не требуется.
- **норма**: канон слоя, «Тексты интерфейса»; форма `texts.md` («Статус
  строки»).
- **рекомендация**: «Провести строки через проверки этапа «тексты
  интерфейса» — `/screen-deep-dive <project-slug> <surface> texts`».

### R-TX-005 «реестр не по форме»

- **severity**: `error`.
- **scope**: `texts.md`.
- **проверка**: колонки формы в её порядке (`key` · `role` · `text` ·
  `maxlen` · `action` · `object` · `group` · `context` · `status`,
  колонки `text-<locale>` — после); `key` — сегменты
  `{раздел}.{экран}.{элемент}.{роль}` латиницей; ключи уникальны; `role` —
  из закрытого списка ux 07/06 §7.2 или `body`; `status` ∈ {`assumed`,
  `checked`, `approved`}; у `checked` и `approved` — `maxlen` числом.
  Ссылки `action` и `object` — R-STRUCT-023.
- **норма**: форма `texts.md` («Колонки», «Статус строки»); ux 07/05
  §3.1.
- **рекомендация**: «Привести реестр к форме через
  `/screen-deep-dive <project-slug> <surface> texts`».

### R-TX-006 «строка реестра без ключа в деревьях»

- **severity**: `hint`.
- **scope**: `texts.md` ↔ деревья поверхности.
- **проверка**: ключ строки не встречается ни в одном дереве, ни в
  `form`, `tiles` и разделе «Состояния приложения» — осиротевшая строка.
- **норма**: форма `texts.md` (критерий 3).
- **рекомендация**: «Удалить строку или вернуть ключ в дерево через
  `/screen-deep-dive <project-slug> <surface> texts`».

### R-TX-007 «синоним, число или пустой смысл в строке»

- **severity**: `warning`.
- **scope**: `texts.md` ↔ `object.md`, `action.md` (чтением).
- **проверка**: строка называет объект синонимом из `aliases` или
  действие словом из `banned`; несёт число, имя, дату или сумму
  литералом вместо подстановки; у строки с подстановкой, омонимом или
  ограничением длины пуст `context`.
- **норма**: форма `texts.md` (критерии 4, 6, 7); ux 07/05 §3.2, §4.4.
- **рекомендация**: «Переписать строку через
  `/screen-deep-dive <project-slug> <surface> texts`; правка возвращает
  её в `assumed`».

---

## R-AX (доступность)

Слой экранов объявляет структуру доступности; исполняют и проверяют её
дизайн-система и приёмка макета (канон слоя, «Доступность и узкий
экран»). Клавиатурный контракт типа — словарь компонентов, у расширения
его проверяет `/design-audit` (R-COV-005).

### R-AX-001 «лендмарк `main` не один»

- **severity**: `error`.
- **scope**: каркасы.
- **проверка**: ровно один слот каркаса с `landmark: main`.
- **норма**: форма `shell.md` («Форма frontmatter»); канон слоя,
  «Доступность и узкий экран».
- **рекомендация**: «Назначить один главный слот через
  `/screen-deep-dive <project-slug> <surface> shell:<slug>`».

### R-AX-002 «заголовок экрана не один»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: экраны вместе с блоками слотов.
- **проверка**: в основном содержимом экрана вне оверлеев — ровно один
  текстовый узел роли `title`; у оверлея заголовок — `Modal.Header` или
  `Drawer.Header`.
- **норма**: канон слоя, «Доступность и узкий экран» («Заголовок»).
- **рекомендация**: «Оставить один заголовок экрана через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>`».

### R-AX-003 «конвенции доступности не записаны»

- **severity**: `warning` (если `map.md` в `draft`), `error` (если
  `map.md` в `stable`).
- **scope**: `map.md` («Конвенции»).
- **проверка**: есть строки «Доступность»: фокус при открытии и закрытии
  оверлея, удалении строки, смене маршрута и ошибке формы; объявления
  (найдено, сохраняется, готово, тост); помощь в одном месте; повторный
  ввод и вставка в поля входа; лимит времени сессии.
- **норма**: форма `map.md` («Решения поверхности», «Конвенции»); канон
  слоя, «Доступность и узкий экран»; ux 13/04 §23.
- **рекомендация**: «Записать конвенции через
  `/screen-deep-dive <project-slug> <surface> map`».

### R-AX-004 «перетаскивание без другого пути»

- **severity**: `warning`.
- **scope**: экраны с узлом перетаскивания (например `ui:FileUpload`,
  перестановка строк, канбан).
- **проверка**: раздел `## Доступность` экрана называет путь одним
  указателем и с клавиатуры.
- **норма**: форма `screen.md` («Доступность»); канон слоя, «Доступность
  и узкий экран» («Отступления экрана»).
- **рекомендация**: «Описать другой путь через
  `/screen-deep-dive <project-slug> <surface> screen:<slug>`».

### R-AX-005 «статус объекта только иконкой или меткой»

- **severity**: `warning`.
- **scope**: деревья поверхности (чтением).
- **проверка**: статус объекта показан текстом из статусов глоссария
  (`object.md`, колонка `statuses`), а не только иконкой или меткой без
  подписи.
- **норма**: канон слоя, «Доступность и узкий экран» («Статус
  объекта»).
- **рекомендация**: «Показать статус текстом через
  `/screen-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-AX-006 «помощь не в одном месте»

- **severity**: `warning`.
- **scope**: каркасы, экраны.
- **проверка**: у основного каркаса — один узел помощи; экраны не заводят
  свою помощь в других местах.
- **норма**: форма `shell.md`, критерий 6; канон слоя, «Доступность и
  узкий экран» (конвенции).
- **рекомендация**: «Свести помощь в узел каркаса через
  `/screen-deep-dive <project-slug> <surface> shell:<slug>`».

---

## R-MB (узкий экран)

Правила раздела не применяются, если vision (`Devices and
accessibility`) записал «только десктоп». Нативное приложение — отдельная
поверхность `type: mobile` со своим слоем и аудитом (`/mobile-audit`).

### R-MB-001 «способ реализации мобильного не решён»

- **severity**: `warning` (если `map.md` в `draft`), `error` (если
  `map.md` в `stable`).
- **scope**: `map.md` («Решения»).
- **проверка**: строка о способе реализации мобильного — адаптив,
  отдельная мобильная версия, PWA или нативное приложение — с
  отвергнутыми вариантами и причиной; нативное приложение — строка
  `type: mobile` в реестре `surface.md`.
- **норма**: форма `map.md` («Решения»); ux 09/01 §2.
- **рекомендация**: «Записать решение через
  `/screen-deep-dive <project-slug> <surface> map`; новую поверхность —
  `/project-deep-dive <project-slug>`».

### R-MB-002 «тип экрана без строки «Узкий экран»»

- **severity**: `warning` (если `map.md` в `draft`), `error` (если
  `map.md` в `stable`).
- **scope**: `map.md` («Узкий экран») ↔ экраны.
- **проверка**: у каждого `type` экранов поверхности и у каркаса —
  строка с ответами на пять вопросов (reveal, divide, resize, reposition,
  swap); сценарий, которого на узкой ширине сознательно нет, — строка
  урезания с основанием и сроком пересмотра.
- **норма**: форма `map.md` («Узкий экран»); ux 09/01 §4.2, §8; ux 13/04
  §24.
- **рекомендация**: «Дописать строку через
  `/screen-deep-dive <project-slug> <surface> map`».

### R-MB-003 «`hidden` без другого пути»

- **severity**: `warning`.
- **scope**: каркасы (`responsive`).
- **проверка**: у слота с поведением `hidden` на диапазоне функции
  доступны иначе на том же диапазоне — другой слот, пункт навигации,
  меню.
- **норма**: форма `shell.md` (`behaviour`); канон слоя, «Доступность и
  узкий экран».
- **рекомендация**: «Назвать другой путь или сменить поведение через
  `/screen-deep-dive <project-slug> <surface> shell:<slug>`».

### R-MB-004 «навигация на узком экране не по числу разделов»

- **severity**: `warning`.
- **scope**: `map.md` («Навигация», колонка `narrow`), основной каркас.
- **проверка**: навигация на узкой ширине — нижняя панель вкладок или
  выдвижная панель — выбрана по числу разделов по ux 09/02 §1.6.
- **норма**: канон слоя, «Доступность и узкий экран»; ux 09/02 §1.6.
- **рекомендация**: «Сменить вариант навигации на узкой ширине через
  `/screen-deep-dive <project-slug> <surface> shell:<slug>`».

### R-MB-005 «master-detail без мобильного потока»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: экраны с `type: master-detail` ↔ потоки.
- **проверка**: экран стоит в `desktop` потока, у которого в `mobile`
  минимум два экрана — список и детали.
- **норма**: форма `flow.md`, критерий 6.
- **рекомендация**: «Завести поток через
  `/screen-deep-dive <project-slug> <surface> flow`».

### R-MB-006 «коллекция без способа на узком экране»

- **severity**: `hint` (если `status: draft`), `warning` (если
  `status: stable`).
- **scope**: блоки с `collection`.
- **проверка**: `collection.narrow` задан.
- **норма**: форма `block.md` («Контракт коллекции»); ux 09/03 §2.2.
- **рекомендация**: «Выбрать способ через
  `/screen-deep-dive <project-slug> <surface> block:<slug>`».

### R-MB-007 «оверлей на узком экране без поведения»

- **severity**: `warning`.
- **scope**: каркасы.
- **проверка**: у слота `accepts: block (modal/drawer)` на самом узком
  объявленном диапазоне — поведение `fullscreen` или `bottom-sheet`.
- **норма**: форма `shell.md` (`behaviour`); ux 04/07 §1.4.
- **рекомендация**: «Назначить поведение через
  `/screen-deep-dive <project-slug> <surface> shell:<slug>`».

### R-MB-008 «планшетная ширина не решена»

- **severity**: `warning`.
- **scope**: каркасы.
- **проверка**: у каркаса — поведение слотов на диапазоне `sm` (в него
  попадает класс окна medium) или в теле каркаса «не применимо:
  причина».
- **норма**: канон слоя, «Доступность и узкий экран», «Ключи
  `responsive` и брейкпоинты».
- **рекомендация**: «Решить поведение на `sm` через
  `/screen-deep-dive <project-slug> <surface> shell:<slug>`».
