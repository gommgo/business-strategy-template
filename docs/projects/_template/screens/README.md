# Артефакты экранов

Слой композиции и облика проекта: из аналитических артефактов
`docs/projects/<project-slug>/interface/` синтезируется детерминированная
карта экранов, по которой собираются вайрфреймы и hi-fi. Этот файл —
**канон формы** (`docs/projects/_template/screens/`); данные каждого проекта
живут в `docs/projects/<project-slug>/screens/`. Артефакты — **аналитика
композиции и облика** в терминах семантического дерева и компонентов
`@stit/ui`. **Маппинг на FSD здесь не делается** — превращение
`docs/projects/<project-slug>/screens/` в код делает автор макета вручную,
не отдельный артефакт.

## Воркфлоу

```
interface/ → синтез → screens/ → wireframe → hi-fi
 (бизнес)              (композиция,   (код на @stit/ui,
                        облик)         вручную)
```

(оба слоя — в папке проекта `docs/projects/<project-slug>/`)

1. В `docs/projects/<project-slug>/interface/` заведены и углублены
   сущности (через `interface-deep-dive`).
2. На их базе вручную создаются артефакты в
   `docs/projects/<project-slug>/screens/` — каждый ссылается на свой
   источник в interface через `slug`.
3. По `docs/projects/<project-slug>/screens/` автор макета вручную
   собирает wireframe и hi-fi субстрат на `@stit/ui`. Отдельного
   артефакта-моста между screens и кодом нет.

## 4 kind

| kind | сущность | один-в-одно про |
|---|---|---|
| [`flow`](flows/README.md) | пользовательский сценарий, объединяющий desktop-screen и mobile-decomposition | viewport-вариативность |
| [`screen`](screens/README.md) | route/view с типизированными слотами | что в каких слотах + состояния |
| [`block`](blocks/README.md) | раскрытие interface-block в дерево компонентов | как реализуется аналитический блок |
| [`shell`](shells/README.md) | каркас, объявляющий слоты | layout-капсула + responsive поведение |

## Структура папок

Канон формы (этот README + 4 kind-README) живёт один раз в
`docs/projects/_template/screens/`:

```
docs/projects/_template/screens/
├── README.md                       (этот файл)
├── flows/README.md                 (канон flow)
├── screens/README.md               (канон screen)
├── blocks/README.md                (канон block)
└── shells/README.md                (канон shell)
```

Данные экранов живут в папке проекта
`docs/projects/<project-slug>/screens/`:

```
docs/projects/<project-slug>/screens/
├── flows/
│   └── <slug>/index.md
├── screens/
│   └── <slug>/index.md
├── blocks/
│   └── <slug>/index.md
└── shells/
    └── <slug>/index.md
```

Каждая сущность — папка с `index.md`. Папка оставляет место для будущих
add-on (заметки, скриншоты, отдельные macro-вью), не плодя файлов сейчас.
Если у сущности кроме `index.md` ничего нет — это нормально.

## Форма артефакта

```markdown
---
slug: <kebab-case>
name: <человекочитаемое имя>
description: <одна фраза о сущности>
status: draft | stable
<доменные поля по kind>
---

# <slug>

<одна-две поясняющие фразы>

​```yaml
<древо | slot-fills | states | прочая структура>
​```
```

Маркеры `<>` — заполняемые места. `status` — зрелость записи относительно
критериев своего kind (как в каноне `docs/projects/_template/interface/`).
Связи — слаг-рефами в бэктиках (форма ячеек — как в interface).
Frontmatter — YAML, древо — fenced ```yaml```-блок в теле.

## Layout-язык (для дерева)

Дерево живёт в ```yaml```-блоке тела артефакта. Узлы — **семантические**:
описывают намерение композиции, не CSS-детали. Конкретный облик
(пиксели, цвета, шрифты) — в craft библиотеки `@stit/ui`.

### Naming компонентов

| префикс | источник | пример |
|---|---|---|
| `ui:` | `@stit/ui` (компонент библиотеки) | `ui:Stack`, `ui:Button`, `ui:DataList` |
| `block:` | `docs/projects/<project-slug>/screens/blocks/<slug>` (проектный блок) | `block:filters-panel` |
| `data:` | `docs/projects/<project-slug>/interface/data-items.md` (датум) | `data:study`, `data:study.name` |
| `block-*:` | зарезервированная internal-zone блока (внутри tree блока) | `block-header:`, `block-body:`, `block-footer:`, `block-aside:` |

### Layout-примитивы

| узел | роль | ключевые props |
|---|---|---|
| `ui:Stack` | вертикальная композиция | `gap=sm\|md\|lg`, `justify`, `align` |
| `ui:Row` | горизонтальная композиция | `gap`, `justify=start\|center\|end\|between\|around`, `align=start\|center\|stretch`, `wrap=true\|false` |
| `ui:Cluster` | группа без направления (плотный кластер) | `gap` |
| `ui:Grid` | сетка | `columns=N`, `gap`, либо `areas: [[…]]` |
| `ui:Pad` | внутренний отступ-обёртка | `gap` |
| `ui:Sticky` | прилипающая обёртка | `offset=top\|bottom` |
| `ui:Scroll` | скроллируемая обёртка | `axis=y\|x` |

`span=N` ставится на дочернем узле `ui:Grid` (как в CSS grid-column-span).
Размеры — токенами (`sm`, `md`, `lg`), не пикселями.

### Internal-zones блока

Дерево `block`-артефакта **начинается с зон**, а не layout-узлов: блок
имеет роли, ui-lib их оформляет (бордеры, sticky-header, fixed-footer).

```yaml
tree:
  block-header:                # toolbar / title
    - ui:Row justify=between
      - ui:Search
      - ui:Button label='Новое'
  block-body:                  # основной контент
    - ui:DataList items=data:study
  block-footer:                # пагинация / действия
    - ui:Pagination
  block-aside:                 # боковая дорожка (если есть)
    - ui:Stack
      - ui:Field label='Сортировка'
```

Зоны опциональны; блок может содержать только `block-body`.

### Grid-template-areas

Для нетривиальных сеток (дашборды, многопанельные backoffice):

```yaml
- ui:Grid
    areas:
      - [search,  search,  action]
      - [filters, list,    detail]
      - [filters, list,    detail]
    fill:
      search:  ui:Search
      action:  ui:Button label='Новое'
      filters: block:filters-panel
      list:    block:studies-list
      detail:  block:study-preview
```

## Data binding

Ссылка на датум — `data:<slug>` (slug из
`docs/projects/<project-slug>/interface/data-items.md`). Доступ к полю —
`data:<slug>.<field>`.

```yaml
- ui:DataList
    items: data:study
    columns:
      - { field: data:study.name,   label: 'Имя' }
      - { field: data:study.date,   label: 'Дата' }
      - { field: data:study.status, label: 'Статус' }
```

Lint проверяет существование slug-а в `data-items.md`. Реальный источник
данных — слой кода (FSD); артефакт фиксирует только контракт.

## Контракт с `@stit/ui`

`@stit/ui` публикует JSON-каталог компонентов
(`manifest.json` в дистрибутиве): имя + props + варианты. Lint в
`docs/projects/<project-slug>/screens/` читает manifest и ругает
неизвестные `ui:*` имена и невалидные props.

Пока manifest не опубликован — имена `ui:*` в артефактах служат
**требованиями к ui-lib**. Накопленный «список требуемого» — раздел
ниже.

### Топ-уровень компонентов (выводимые требования)

Layout-примитивы:
- `ui:Stack`, `ui:Row`, `ui:Cluster`, `ui:Grid`, `ui:Pad`,
  `ui:Sticky`, `ui:Scroll`.

Shell-каркасы:
- `ui:AppShell` (слоты header/side/main/detail/overlay/footer),
  `ui:Header`, `ui:Sidebar`, `ui:Main`, `ui:Detail`, `ui:OverlayLayer`,
  `ui:Footer`.

Data display:
- `ui:DataList`, `ui:DataTable`, `ui:Pagination`, `ui:Avatar`,
  `ui:Menu`, `ui:IconButton`, `ui:Toolbar`.

Feedback (loading/empty/error/permission):
- `ui:Skeleton`, `ui:EmptyState`, `ui:ErrorState`,
  `ui:AccessDeniedState`, `ui:OfflineState`, `ui:NotFoundState`,
  `ui:Toast`.

Overlay:
- `ui:Modal`, `ui:Drawer`, `ui:Popover`.

Forms и input:
- `ui:Form`, `ui:Field`, `ui:Input`, `ui:Checkbox`, `ui:Radio`,
  `ui:DateInput`, `ui:Search`, `ui:Button`, `ui:Calendar`,
  `ui:InputOtp`.

Список — выводимое требование, не финальный реестр. Источник правды —
`@stit/ui/manifest.json`, когда тот появится.

## Anti-patterns

- ❌ Облик в артефакте: цвета, типографика, пиксели, `style=`. Это craft
  библиотеки.
- ❌ Оси контекста как props компонентов или поля артефактов:
  `density`/`brand`/`scheme` живут на корне через `data-*`, не в YAML
  дерева.
- ❌ FSD-маппинг в screens (widget/feature/entity-имена в дереве,
  ссылки на `pages/`/`widgets/`). FSD-структура появляется в коде
  вручную при сборке wireframe/hi-fi, не в артефактах screens.
- ❌ Inline-логика: `if`/`then`, тернарники, вычислимые выражения.
  Артефакт — декларативный.
- ❌ Битый slug-реф (на несуществующий screen/block/shell/data-item).
- ❌ Расхождение зеркал interface ↔ screens: если у `interface-block` в
  `docs/projects/<project-slug>/interface/block.md` объявлены
  `ux-substrates`, тот же набор должен быть в frontmatter
  соответствующего `block`-артефакта.
- ❌ Breakpoints в `shell.tree` или в `screen.slot-fills`: облицовочный
  адаптив (sidebar→drawer) — только в `shell.responsive`. Структурный
  адаптив (1 desktop ↔ N mobile) — через `flow`, не через `screen`.
- ❌ `screen` без `shell`, `shell` без `slots`, `block` без
  `interface-block`, `flow` без `desktop` или без `mobile`.
- ❌ `block` 1:1 экрану: блок — содержимое слота, не route.

## Связь с `interface/` проекта

Источник синтеза — UX-слой того же проекта,
`docs/projects/<project-slug>/interface/`:

| screens | → ссылается на → | interface |
|---|---|---|
| `screen.blocks` | M:N | `block.md` |
| `screen.situations` | M:N | `situation.md` |
| `screen.who` | M:N | `who.md` |
| `block.interface-block` | M:1 | `block.md` |
| `block.ux-substrates` | M:N | `ux-substrate.md` (зеркало interface) |
| `data:<slug>` в дереве | M:1 | `data-items.md` |

Когда сущность interface удаляется — каскадно удаляются ссылки в
screens (правило forward-only).

## Связь с кодом

Прямой автоматической связи нет. Wireframe и hi-fi субстрат на
`@stit/ui` собирает автор макета **вручную** по
`docs/projects/<project-slug>/screens/`. Отдельного артефакта-моста между
screens и кодом нет и не планируется.
