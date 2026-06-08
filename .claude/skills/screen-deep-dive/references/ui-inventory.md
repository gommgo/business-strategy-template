# Инвентарь `ui:Component`

Источник правды о том, какие имена `ui:*` существуют и какие props
принимают, — `manifest.json` пакета `@stit/ui` (когда тот
будет опубликован). Скилл использует его в режиме углубления дерева,
чтобы предлагать `ui:Component` как опции (не выдумывая имена).

## Где искать manifest

Порядок поиска (сверху вниз):

1. **Соседний репо** `ui-lib/` (рядом с этим проектом):
   `../ui-lib/manifest.json`. Если есть — читать его.
2. **Fallback** — раздел «Топ-уровень компонентов» в каноне
   `docs/projects/_template/screens/README.md`. Это «выводимые
   требования», не окончательный реестр; покрывает основные категории,
   но без детального списка props.

Скилл проверяет (1), потом (2). Найденный — `Read`.

## Что в manifest (ожидаемая форма)

```json
{
  "components": {
    "Stack": {
      "category": "layout-primitive",
      "props": {
        "gap": { "type": "enum", "values": ["sm", "md", "lg"] },
        "justify": { "type": "enum", "values": ["start", "center", "end", "between", "around"] },
        "align": { "type": "enum", "values": ["start", "center", "stretch"] }
      },
      "children": "any"
    },
    "Button": {
      "category": "form",
      "props": {
        "variant": { "type": "enum", "values": ["primary", "secondary", "ghost", "danger"] },
        "icon": { "type": "string" },
        "label": { "type": "string", "required": true }
      },
      "children": "none"
    }
  }
}
```

Реальная форма может отличаться — скилл должен мочь распарсить
любую разумную схему (`components` как объект с именами компонентов
как ключами; у каждого — `props`, опционально `category`).

## Категории (для группировки в опциях AskUserQuestion)

Из канона `docs/projects/_template/screens/README.md`:

| категория | компоненты (выводимый минимум) |
|---|---|
| **layout-primitive** | `Stack`, `Row`, `Cluster`, `Grid`, `Pad`, `Sticky`, `Scroll` |
| **shell-frame** | `AppShell`, `Header`, `Sidebar`, `Main`, `Detail`, `OverlayLayer`, `Footer` |
| **data-display** | `DataList`, `DataTable`, `Pagination`, `Avatar`, `Menu`, `IconButton`, `Toolbar` |
| **feedback** | `Skeleton`, `EmptyState`, `ErrorState`, `AccessDeniedState`, `OfflineState`, `NotFoundState`, `Toast` |
| **overlay** | `Modal`, `Drawer`, `Popover` |
| **form** | `Form`, `Field`, `Input`, `Checkbox`, `Radio`, `DateInput`, `Search`, `Button`, `Calendar`, `InputOtp` |

Когда углубляем узел дерева — скилл предлагает опции из релевантной
категории:

- слот shell, который заполняется блоком → не предлагать
  `ui:Component` (предлагать `block:<slug>` или inline-дерево);
- inline-дерево в `slot-fills`/`states` для `loading` →
  feedback (`ui:Skeleton`);
- inline-дерево в `states` для `empty`/`error`/`permission-denied`/
  `offline`/`not-found` → feedback (соответствующий `…State`);
- `tree` блока, корневой обёртки `block-body` → layout-primitive
  (`ui:Stack`/`ui:Scroll`/`ui:Grid`);
- `tree` блока, контент `block-body` → data-display или form (по
  смыслу субстрата);
- `tree` shell → shell-frame (`ui:AppShell`/`ui:Header`/…).

## Когда инвентаря не хватает

См. SKILL.md `## Инвентарь ui:Component`.

Кратко: если ни один компонент из инвентаря не подходит к
семантике узла, скилл через `AskUserQuestion`:

- «Предложить новый компонент `ui:<имя>` как требование к ui-lib?»
  (опции: «да» / «нет, попробуем что-то из инвентаря»).
- По «да» — Other для имени (PascalCase, начинается с `ui:`); в
  `state/<project-slug>/<kind>/<slug>.md`, секция `## Что копать
  дальше`, добавляется строка: `ui-lib gap: нужен ui:<имя> — <зачем>`.
- Компонент попадает в дерево с предложенным именем; lint аудита
  его признает «зарегистрированный gap», не error.

## Props: enum vs свободные значения

- **enum** (например, `gap=sm|md|lg`, `justify=start|center|...`)
  — опции в `AskUserQuestion` строго по списку из manifest.
- **string / number** — Other (свободная форма):
  `placeholder='Поиск исследований'`, `rows=8`.
- **bool** — две опции (`true` / `false`), либо не указывать
  (умолчание).
- **сложные** (`columns: [...]`, `items: data:study`) — отдельный
  раунд углубления, аналитик пишет конструкцию через Other,
  скилл валидирует синтаксис `data:<slug>`.

## Что НЕ делать

- Не выдумывать имена компонентов вне инвентаря и вне процедуры
  «ui-lib gap». Никаких `ui:SmartTable` или `ui:FancyCard` «по
  смыслу».
- Не выдумывать значения enum props — только из manifest.
- Не предлагать FSD-имена (`StudiesListWidget`, `FiltersFeature`).
- Не помещать в дерево `ui:` без префикса (`Button` вместо
  `ui:Button`): в каноне screens живут только компоненты из
  `@stit/ui` (`ui:`), проектные блоки (`block:`) и датумы
  (`data:`).
