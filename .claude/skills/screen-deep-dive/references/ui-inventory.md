# Инвентарь `ui:Component`

Источник правды о том, какие имена `ui:*` существуют и какие props они
принимают, — **манифест** пакета `@stit/ui` (`manifest.json` в
дистрибутиве). Канон screens собственного списка компонентов не ведёт:
имя `ui:<Name>` валидно ⇔ `<Name>` есть в словаре `components`
манифеста. Скилл использует манифест в режиме углубления дерева, чтобы
предлагать `ui:Component` как опции (не выдумывая имена, props и
значения enum).

## Где искать манифест

Порядок поиска (сверху вниз):

1. **Соседний репо экосистемы** `ui-lib/`:
   `../ui-lib/dist/manifest.json` (относительно корня этого
   репозитория).
2. **У потребителя с установленным пакетом**:
   `node_modules/@stit/ui/manifest.json`.

Найденный — `Read` (файл большой; читать точечно нужные ключи, не
целиком). Если манифест недоступен ни по одному пути — сказать об этом
аналитику, компоненты наугад не предлагать: узлы собираются из
`layout:`-узлов и `block:`-рефов, а выбор `ui:*` откладывается
state-заметкой.

## Что в манифесте (реальная форма)

Ключи верхнего уровня, важные скиллу: `components` (словарь по имени
компонента), `componentsByFamily`, `taxonomy`, `axes`, `notAvailable`,
`taskMap`, `icons`.

У компонента `components.<Name>`: `subpath`, `import`,
`taxonomy {level, family, archetype}`, `runtime`, `requiresStylesheet`,
`requiresTailwindSource`, `props` — **массив объектов**, у compound —
`parts` (массив частей, каждая со своим `props`):

```json
{
  "components": {
    "Button": {
      "subpath": "@stit/ui/button",
      "taxonomy": { "level": "atom", "family": "actions", "archetype": "atom" },
      "props": [
        { "name": "variant", "tsType": "ButtonVariant", "required": false,
          "values": ["accent", "secondary", "outline", "ghost", "destructive"],
          "default": "accent" },
        { "name": "tone", "tsType": "ButtonTone", "required": false,
          "values": ["primary", "secondary", "tertiary"], "default": "primary",
          "availableWhen": "variant === 'accent'" },
        { "name": "size", "tsType": "ButtonSize", "required": false,
          "values": ["xs", "sm", "md", "lg"], "default": "md" }
      ],
      "parts": null
    },
    "Popover": {
      "parts": [
        { "name": "Trigger", "namespace": "Popover.Trigger", "slot": "trigger", "props": [] },
        { "name": "Content", "namespace": "Popover.Content", "slot": "content", "props": [] }
      ]
    }
  }
}
```

Отсюда:

- **имя** `ui:<Name>` — только ключ из `components`;
- **props** — только имена из `props[]` компонента; значение пропа с
  заданным `values` — строго из списка; `availableWhen` — условие
  применимости (например, `tone` у Button действует при
  `variant=accent`);
- **части compound** — `ui:<Name>.<Part>` по `parts[].name`
  (`ui:Popover.Trigger`, `ui:Field.Label`, `ui:Select.Option`); props
  части — из её `props[]`;
- **подписи и иконки** — children-узлы (`- 'Новое'`, `- icon:plus`),
  не props: пропсов `label`/`icon`/`title` у компонентов нет.

### `taxonomy.families` — группировка опций

`taxonomy.families`: `actions` · `forms` · `overlays` · `navigation` ·
`feedback` · `data-display` · `layout`. Состав семейств —
`componentsByFamily` (не собирать руками).

### `axes` — оси контекста, не props

`axes`: `data-brand` (открытое значение — id бренд-пресета заказчика),
`data-scheme` (`light|dark`), `data-density` (`comfortable|compact`),
`data-mode` (`wireframe`), `dir` (`ltr|rtl`). Все живут на корне
приложения (`StitProvider` / узел-носитель) — в дерево артефактов как
props не попадают.

### `notAvailable` — запланированные компоненты

Массив `{name, plannedAt, task, aka?}` — чего в библиотеке ещё нет, но
запланировано (Dialog, Drawer, Tabs, Table, Toast, Menu, Pagination,
Sidebar, Navbar, Skeleton, Card, Form, …). `aka` — альтернативные имена
(`Toast` ← `Toaster`, `Menu` ← `DropdownMenu`/`ContextMenu`,
`ToggleGroup` ← `SegmentedControl`). Использование такого имени в
дереве — осознанный **forward-реф** с пометкой `(planned)`:
`ui:Table (planned)`. Props у forward-рефа не описываются (контракта
ещё нет) — намерение несут children и текст; `/screen-audit` репортит
такой реф как gap.

### `taskMap` — подсказки «задача → компоненты»

Словарь «человеческая задача → список компонентов» («форма входа» →
`Field, Input, Button`; «выбор из списка» → `Field, Select`; «метка /
индикатор» → `Badge, Tag, Spinner`; …). Использовать для подсказок в
`AskUserQuestion`-опциях: когда аналитик описывает узел задачей, скилл
подбирает опции по `taskMap`, а не перебирает весь словарь.

### `icons` — реестр иконок

Ключ `icons` манифеста — указатель `{manifest, subpath, count}` на
под-манифест иконок (в дистрибутиве — `dist/icons/manifest.json`). Там
`icons[]` с `{name, kind: glyph|brand, subpath, keywords}`. Реф в
дереве — `icon:<slug>`, где `<slug>` — хвост `subpath` после
`@stit/ui/icons/` (`plus`, `chevron-down`, `brands/visa`). Подбор — по
`keywords`.

## Layout — не компоненты

Layout-примитивов и shell-каркасов в библиотеке нет и не планируется:
раскладка — `layout:`-узлы дерева (`layout:stack` · `layout:row` ·
`layout:grid` · `layout:layer`, см. канон слоя «Узлы раскладки»),
материализуемые Tailwind-утилитами при сборке. Не искать
Stack/Row/Grid/AppShell в манифесте и не предлагать их как `ui:*`.

## Как предлагать опции по месту в дереве

- слот shell, который заполняется блоком → не предлагать
  `ui:Component` (предлагать `block:<slug>` или inline-дерево);
- состояние `loading` в `screen.states` → `feedback`-семейство:
  `ui:Spinner`; `ui:Skeleton (planned)` — forward-реф;
- прочие состояния (`empty`/`error`/`permission-denied`/`offline`/
  `not-found`) → композиция `layout:`-узлов + текст-children (+
  `ui:Button` для действия «повторить»/«создать»);
- `tree` блока, корневая обёртка `block-body` → `layout:`-узлы;
  скролл — `ui:ScrollArea`;
- `tree` блока, контент `block-body` → `data-display` (`Badge`, `Tag`)
  или `forms` (по смыслу субстрата, через `taskMap`); коллекции —
  forward-рефы (`ui:Table (planned)`, `ui:Card (planned)`);
- `tree` shell → `layout:`-узлы + forward-рефы навигации
  (`ui:Navbar (planned)`, `ui:Sidebar (planned)`);
- overlay → `overlays`: `ui:Popover`; `ui:Dialog (planned)` /
  `ui:Drawer (planned)` — forward-рефы.

## Когда компонента нет

Кратко (см. также SKILL.md `## Инвентарь ui:Component`):

- имя есть в `notAvailable` (включая `aka`) → forward-реф
  `ui:<Name> (planned)` (каноническое имя из `name`, не из `aka`);
- имени нет ни в `components`, ни в `notAvailable` → **в дерево оно не
  попадает**: узел собирается из существующих компонентов и
  `layout:`-узлов, а потребность фиксируется в
  `../entrypoint/state/projects/<project-slug>/screens/<surface>/<kind>/<slug>.md`,
  секция `## Что копать дальше`, строкой
  `ui-lib gap: нужен ui:<имя> — <зачем>` (обратная связь библиотеке).

## Props: enum vs свободные значения

- **`values` задан** (например, `variant`, `size`, `tone`,
  `scrollbars`) — опции в `AskUserQuestion` строго по списку из
  манифеста; учитывать `availableWhen`.
- **string / number** — Other (свободная форма): `placeholder='…'`
  только если проп `placeholder` есть в `props[]` компонента.
- **boolean** — две опции (`true` / `false`), либо не указывать
  (умолчание из `default`).
- **сложные** (`columns: [...]`, `items: data:study`) — отдельный
  раунд углубления, аналитик пишет конструкцию через Other,
  скилл валидирует синтаксис `data:<slug>`.
- **текст** (подпись кнопки, заголовок) — children-узел, не проп;
  формулировка — аналитика (Other).

## Что НЕ делать

- Не выдумывать имена компонентов вне `components` и `notAvailable`.
  Никаких `ui:SmartTable` или `ui:FancyCard` «по смыслу».
- Не выдумывать значения enum props и сами имена props — только из
  манифеста.
- Не передавать текст/иконку через несуществующие props
  (`label=`, `icon=`, `title=`) — это children-узлы.
- Не помечать `(planned)` компонент, которого нет в `notAvailable`,
  и не опускать пометку у того, который там есть.
- Не предлагать FSD-имена (`StudiesListWidget`, `FiltersFeature`).
- Не помещать в дерево имя без префикса (`Button` вместо
  `ui:Button`): в каноне screens живут только компоненты манифеста
  (`ui:`), узлы раскладки (`layout:`), иконки (`icon:`), проектные
  блоки (`block:`) и датумы (`data:`).
