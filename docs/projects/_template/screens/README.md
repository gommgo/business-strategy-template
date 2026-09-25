# Артефакты экранов

Слой композиции экранов проекта, **партиционированный по поверхности
(surface)**: из аналитических артефактов
`docs/projects/<project-slug>/interface/<surface>/` синтезируется
детерминированная карта экранов той же поверхности, по которой собираются
вайрфреймы и hi-fi. Этот файл — **канон слоя**; форма одной папки
поверхности (4 файла-формы по kind) лежит рядом в `_template/`. Данные каждого
проекта живут в `docs/projects/<project-slug>/screens/<surface>/` (по папке
на поверхность из реестра `surface.md`; поверхность с `type: bot` вместо
экранов получает слой диалогов `telegram-bot-flow/<surface>/` — см.
`../telegram-bot-flow/README.md`, поверхность с `type: mobile` — карту
приложения `mobile/<surface>/` — см. `../mobile/README.md`). Артефакты —
**аналитика композиции** в терминах семантического дерева и интерфейсных
примитивов проекта (`ui:`). **Маппинг на FSD здесь не делается** — карта
слайсов живёт в отдельном слое `fsd/<surface>/` (`../fsd/README.md`), который
читает экраны и блоки этого слоя как источник. Облик (craft: цвет,
типографика, пространство, движение) в артефакты не пишется: wireframe и
hi-fi автор макета собирает вручную, модель craft не выдумывает.

## Воркфлоу

```
interface/<surface>/ → синтез → screens/<surface>/ → wireframe → hi-fi
 (бизнес)                        (композиция)          (вручную, автор макета)
```

(оба слоя — в папке поверхности проекта
`docs/projects/<project-slug>/{interface,screens}/<surface>/`)

1. В `docs/projects/<project-slug>/interface/<surface>/` заведены и
   углублены сущности (через `interface-deep-dive`).
2. На их базе создаются артефакты в
   `docs/projects/<project-slug>/screens/<surface>/` (через
   `screen-deep-dive`) — каждый ссылается на свой источник в interface той
   же поверхности через `slug`.
3. По `docs/projects/<project-slug>/screens/<surface>/` автор макета
   вручную собирает wireframe и hi-fi; карту слайсов для фронт-кода строит
   слой `fsd/<surface>/`.

## 4 kind

| kind | сущность | один-в-одно про |
|---|---|---|
| [`flow`](_template/flow.md) | пользовательский сценарий, объединяющий desktop-screen и mobile-decomposition | viewport-вариативность |
| [`screen`](_template/screen.md) | route/view с типизированными слотами | что в каких слотах + состояния |
| [`block`](_template/block.md) | раскрытие interface-block в дерево узлов | как реализуется аналитический блок |
| [`shell`](_template/shell.md) | каркас, объявляющий слоты | layout-капсула + responsive поведение |

## Структура папок

Канон формы (этот README + 4 файла-формы по kind, как в
`_template/interface/`) живёт один раз в `docs/projects/_template/screens/`;
подпапка `_template/` описывает **одну папку поверхности**:

```
docs/projects/_template/screens/
├── README.md                       (этот файл — канон слоя)
└── _template/                      (форма одной папки поверхности)
    ├── flow.md                     (форма flow)
    ├── screen.md                   (форма screen)
    ├── block.md                    (форма block)
    └── shell.md                    (форма shell)
```

Данные экранов живут в папке поверхности проекта
`docs/projects/<project-slug>/screens/<surface>/` (одна папка на поверхность
из реестра `surface.md`):

```
docs/projects/<project-slug>/screens/
└── <surface>/
    ├── flows/
    │   └── <slug>/index.md
    ├── screens/
    │   └── <slug>/index.md
    ├── blocks/
    │   └── <slug>/index.md
    ├── shells/
    │   └── <slug>/index.md
    └── assets/
        └── <kind>/<slug>/          (визуальные референсы и ассеты сущности)
```

Каждая сущность — папка с `index.md`. Папка оставляет место для будущих
add-on (заметки, скриншоты, отдельные macro-вью), не плодя файлов сейчас.
Если у сущности кроме `index.md` ничего нет — это нормально. Поверхности
изолированы: ссылки внутри `screens/<surface>/` и зеркала с
`interface/<surface>/` — в пределах одной поверхности.

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
описывают намерение композиции, не CSS-детали. Конкретный облик (пиксели,
цвета, шрифты) — craft, в дерево не пишется.

### Naming узлов

| префикс | что это | пример |
|---|---|---|
| `ui:` | имя интерфейсного примитива проекта; в коде его реализуют проектные компоненты, у фронтовой поверхности это слайс `shared-ui` FSD-карты | `ui:Button`, `ui:Search`, `ui:Popover.Content` |
| `layout:` | нейтральный узел раскладки — не примитив (см. «Узлы раскладки») | `layout:stack`, `layout:row`, `layout:grid` |
| `icon:` | имя иконки | `icon:plus`, `icon:chevron-down` |
| `block:` | `docs/projects/<project-slug>/screens/<surface>/blocks/<slug>` (проектный блок) | `block:filters-panel` |
| `data:` | `docs/projects/<project-slug>/interface/<surface>/data-items.md` (датум) | `data:study`, `data:study.name` |
| `block-*:` | зарезервированная internal-zone блока (внутри tree блока) | `block-header:`, `block-body:`, `block-footer:`, `block-aside:` |

Часть составного примитива — `ui:<Name>.<Part>` (`ui:Popover.Trigger`,
`ui:Field.Label`). Атрибуты узлов (например, `variant=accent`) — свободные
семантические пометки автора без внешней валидации: словаря примитивов и их
атрибутов у слоя нет.

Текст — **children-узел** дерева (строка в кавычках), а не атрибут: подпись
кнопки и её иконка передаются детьми (`- 'Новое'`, `- icon:plus`).

### Узлы раскладки

Стеки, сетки и отступы — не примитивы, а **композиция дерева**
(internal-zones и порядок узлов), которую автор макета материализует
Tailwind-утилитами при ручной сборке. Намерение раскладки дерево несёт
нейтральными `layout:`-узлами:

| узел | намерение | ключевые атрибуты |
|---|---|---|
| `layout:stack` | вертикальная композиция | `gap=xs\|sm\|md\|lg`, `justify`, `align` |
| `layout:row` | горизонтальная композиция | `gap`, `justify=start\|center\|end\|between`, `align=start\|center\|stretch`, `wrap=true\|false` |
| `layout:grid` | сетка | `columns=N`, `gap`, либо `areas: [[…]]` |
| `layout:layer` | слой поверх потока (якорь overlay) | — |

`span=N` ставится на дочернем узле `layout:grid`. Размеры — токенами
намерения (`xs`, `sm`, `md`, `lg`), не пикселями. `layout:`-узел живёт только
в артефакте и превращается в раскладку при ручной сборке.

### Internal-zones блока

Дерево `block`-артефакта **начинается с зон**, а не layout-узлов: у блока
есть роли — шапка, тело, подвал, боковая дорожка; их облик (бордеры,
sticky-header, fixed-footer) задаётся при сборке, не в дереве.

```yaml
tree:
  block-header:                # toolbar / title
    - layout:row justify=between
      - ui:Search
      - ui:Button variant=accent
        - icon:plus
        - 'Новое'
  block-body:                  # основной контент
    - ui:Table
        items: data:study
  block-footer:                # пагинация / действия
    - ui:Pagination
  block-aside:                 # боковая дорожка (если есть)
    - layout:stack gap=md
      - ui:Field
        - ui:Field.Label
          - 'Сортировка'
        - ui:Select
```

Зоны опциональны; блок может содержать только `block-body`.

### Grid-template-areas

Для нетривиальных сеток (дашборды, многопанельные backoffice):

```yaml
- layout:grid
    areas:
      - [search,  search,  action]
      - [filters, list,    detail]
      - [filters, list,    detail]
    fill:
      search:  ui:Search
      action:
        - ui:Button variant=accent
          - 'Новое'
      filters: block:filters-panel
      list:    block:studies-list
      detail:  block:study-preview
```

## Data binding

Ссылка на датум — `data:<slug>` (slug из
`docs/projects/<project-slug>/interface/<surface>/data-items.md`). Доступ к
полю — `data:<slug>.<field>`.

```yaml
- ui:Table
    items: data:study
    columns:
      - { field: data:study.name,   label: 'Имя' }
      - { field: data:study.date,   label: 'Дата' }
      - { field: data:study.status, label: 'Статус' }
```

Существование slug-а в `data-items.md` той же поверхности проверяет
`/screen-audit`. Реальный источник данных — слой кода; артефакт фиксирует
только контракт.

### Состояния экрана

Канон-состояния (`loading`, `empty`, `error`, `permission-denied`,
`offline`, `not-found`) — канон слоя screens. Содержимое состояния
описывается композицией и текстом (`layout:`-узлы + children-строки) и, где
нужно, `ui:`-примитивами (`ui:Spinner`, `ui:Skeleton`).

## Anti-patterns

- ❌ Облик в артефакте: цвета, типографика, пиксели, `style=`. Craft в
  артефакты не пишется — его задаёт автор макета при ручной сборке.
- ❌ Оси контекста приложения (тема, бренд, плотность, направление письма)
  как атрибуты узлов или поля артефактов — их задаёт корень приложения в
  коде, не YAML дерева.
- ❌ FSD-маппинг в screens (widget/feature/entity-имена в дереве,
  ссылки на `pages/`/`widgets/`). Карта слайсов живёт в своём слое
  `fsd/<surface>/`; артефакты screens остаются чистой композицией.
- ❌ Inline-логика: `if`/`then`, тернарники, вычислимые выражения.
  Артефакт — декларативный.
- ❌ Битый slug-реф (на несуществующий screen/block/shell/data-item).
- ❌ Ссылка из папки одной поверхности в сущность другой поверхности —
  поверхности изолированы.
- ❌ Расхождение зеркал interface ↔ screens: если у `interface-block` в
  `docs/projects/<project-slug>/interface/<surface>/block.md` объявлены
  `ux-substrates`, тот же набор должен быть в frontmatter
  соответствующего `block`-артефакта той же поверхности.
- ❌ Breakpoints в `shell.tree` или в `screen.slot-fills`: облицовочный
  адаптив (sidebar→drawer) — только в `shell.responsive`. Структурный
  адаптив (1 desktop ↔ N mobile) — через `flow`, не через `screen`.
- ❌ `screen` без `shell`, `shell` без `slots`, `block` без
  `interface-block`, `flow` без `desktop` или без `mobile`.
- ❌ `block` 1:1 экрану: блок — содержимое слота, не route.

## Связь с `interface/<surface>/` проекта

Источник синтеза — UX-слой **той же поверхности** того же проекта,
`docs/projects/<project-slug>/interface/<surface>/`:

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

Прямой автоматической связи нет. Карту слайсов для фронт-кода строит
отдельный слой `fsd/<surface>/` (мост к `<org>/frontend` и `<org>/site`), читая
экраны и блоки этого слоя как источник. Wireframe и hi-fi автор макета
собирает вручную по `docs/projects/<project-slug>/screens/<surface>/`.
