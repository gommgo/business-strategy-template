# Артефакты экранов

Слой композиции и облика проекта, **партиционированный по поверхности
(surface)**: из аналитических артефактов
`docs/projects/<project-slug>/interface/<surface>/` синтезируется
детерминированная карта экранов той же поверхности, по которой собираются
вайрфреймы и hi-fi. Этот файл — **канон слоя**; форма одной папки
поверхности (4 файла-формы по kind) лежит рядом в `_template/`. Данные каждого
проекта живут в `docs/projects/<project-slug>/screens/<surface>/` (по папке
на поверхность из реестра `surface.md`; поверхность с `type: bot` вместо
экранов получает слой диалогов `telegram-bot-flow/<surface>/` — см.
`../telegram-bot-flow/README.md`). Артефакты — **аналитика композиции и облика** в
терминах семантического дерева и компонентов `@stit/ui`. **Маппинг на FSD
здесь не делается** — карта слайсов живёт в отдельном слое `fsd/<surface>/`
(`../fsd/README.md`), который читает экраны и блоки этого слоя как источник;
wireframe и hi-fi по screens собирает автор макета вручную.

## Воркфлоу

```
interface/<surface>/ → синтез → screens/<surface>/ → wireframe → hi-fi
 (бизнес)                        (композиция,          (код на @stit/ui,
                                  облик)                вручную)
```

(оба слоя — в папке поверхности проекта
`docs/projects/<project-slug>/{interface,screens}/<surface>/`)

1. В `docs/projects/<project-slug>/interface/<surface>/` заведены и
   углублены сущности (через `interface-deep-dive`).
2. На их базе вручную создаются артефакты в
   `docs/projects/<project-slug>/screens/<surface>/` — каждый ссылается на
   свой источник в interface той же поверхности через `slug`.
3. По `docs/projects/<project-slug>/screens/<surface>/` автор макета
   вручную собирает wireframe и hi-fi субстрат на `@stit/ui`. Отдельного
   артефакта-моста между screens и кодом нет.

## 4 kind

| kind | сущность | один-в-одно про |
|---|---|---|
| [`flow`](_template/flow.md) | пользовательский сценарий, объединяющий desktop-screen и mobile-decomposition | viewport-вариативность |
| [`screen`](_template/screen.md) | route/view с типизированными слотами | что в каких слотах + состояния |
| [`block`](_template/block.md) | раскрытие interface-block в дерево компонентов | как реализуется аналитический блок |
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
описывают намерение композиции, не CSS-детали. Конкретный облик
(пиксели, цвета, шрифты) — в craft библиотеки `@stit/ui`.

### Naming компонентов

| префикс | источник | пример |
|---|---|---|
| `ui:` | словарь `components` манифеста `@stit/ui` (см. «Контракт с `@stit/ui`») | `ui:Button`, `ui:Search`, `ui:Popover.Content` |
| `layout:` | нейтральный узел раскладки — не компонент (см. «Узлы раскладки») | `layout:stack`, `layout:row`, `layout:grid` |
| `icon:` | реестр иконок манифеста `@stit/ui` | `icon:plus`, `icon:brands/visa` |
| `block:` | `docs/projects/<project-slug>/screens/<surface>/blocks/<slug>` (проектный блок) | `block:filters-panel` |
| `data:` | `docs/projects/<project-slug>/interface/<surface>/data-items.md` (датум) | `data:study`, `data:study.name` |
| `block-*:` | зарезервированная internal-zone блока (внутри tree блока) | `block-header:`, `block-body:`, `block-footer:`, `block-aside:` |

Текст — **children-узел** дерева (строка в кавычках), не props: у
компонентов библиотеки нет `label=` / `title=` / `icon=` — подпись
кнопки и её иконка передаются детьми (`- 'Новое'`, `- icon:plus`).

### Узлы раскладки

Layout-примитивов в `@stit/ui` нет и не планируется: стеки, сетки и
отступы — не компоненты, а **композиция дерева** (internal-zones и
порядок узлов), которую автор макета материализует Tailwind-утилитами
при сборке. Намерение раскладки дерево несёт нейтральными
`layout:`-узлами:

| узел | намерение | ключевые props |
|---|---|---|
| `layout:stack` | вертикальная композиция | `gap=xs\|sm\|md\|lg`, `justify`, `align` |
| `layout:row` | горизонтальная композиция | `gap`, `justify=start\|center\|end\|between`, `align=start\|center\|stretch`, `wrap=true\|false` |
| `layout:grid` | сетка | `columns=N`, `gap`, либо `areas: [[…]]` |
| `layout:layer` | слой поверх потока (якорь overlay) | — |

`span=N` ставится на дочернем узле `layout:grid`. Размеры — токенами
намерения (`xs`, `sm`, `md`, `lg`), не пикселями. `layout:`-узел — не
требование к библиотеке: он живёт только в артефакте и превращается в
Tailwind-утилиты при ручной сборке.

### Internal-zones блока

Дерево `block`-артефакта **начинается с зон**, а не layout-узлов: блок
имеет роли, ui-lib их оформляет (бордеры, sticky-header, fixed-footer).

```yaml
tree:
  block-header:                # toolbar / title
    - layout:row justify=between
      - ui:Search
      - ui:Button variant=accent
        - icon:plus
        - 'Новое'
  block-body:                  # основной контент
    - ui:Table (planned)
        items: data:study
  block-footer:                # пагинация / действия
    - ui:Pagination (planned)
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
- ui:Table (planned)
    items: data:study
    columns:
      - { field: data:study.name,   label: 'Имя' }
      - { field: data:study.date,   label: 'Дата' }
      - { field: data:study.status, label: 'Статус' }
```

Существование slug-а в `data-items.md` той же поверхности проверяет
`/screen-audit`. Реальный источник данных — слой кода (FSD); артефакт
фиксирует только контракт.

## Контракт с `@stit/ui`

Источник правды словаря компонентов — манифест пакета
`@stit/ui/manifest.json`: в экосистеме рядом — `../ui-lib/dist/manifest.json`,
у потребителя с установленным пакетом — `node_modules/@stit/ui/manifest.json`.
Канон screens собственного списка компонентов **не ведёт** — экраны
собираются на словаре манифеста:

- имя `ui:<Name>` валидно ⇔ `<Name>` есть в словаре `components`
  манифеста;
- props и их значения — из массива `props[]` компонента (объекты
  `{name, tsType, required, values?, default}`); если у пропа задан
  `values` — значение только из списка. Например, у `ui:Button`
  `variant ∈ accent | secondary | outline | ghost | destructive`, тон —
  отдельный проп `tone` (действует при `variant=accent`);
- части compound-компонентов — `ui:<Name>.<Part>` по массиву `parts`
  компонента (`ui:Popover.Trigger`, `ui:Field.Label`); props части — из
  её `props[]`;
- реф `icon:<slug>` валиден ⇔ иконка есть в реестре иконок: ключ
  `icons` манифеста указывает на под-манифест (`icons.manifest`, в
  дистрибутиве — `dist/icons/manifest.json`), где `icons[]` несёт
  `subpath` вида `@stit/ui/icons/<slug>`; `<slug>` — хвост subpath
  (`plus`, `chevron-down`, `brands/visa`);
- компонент из `notAvailable` манифеста (запланированный) — осознанный
  **forward-реф**: в дереве помечается суффиксом `(planned)`
  (`ui:Table (planned)`); props у него не описываются — контракта ещё
  нет, намерение несут children и текст. `/screen-audit` репортит такой
  реф как gap;
- имени нет ни в `components`, ни в `notAvailable` — в дерево оно не
  попадает: узел собирается из существующих компонентов и
  `layout:`-узлов, а потребность фиксируется как «ui-lib gap» в
  state-заметке скилла (обратная связь библиотеке).

Проверки ведёт `/screen-audit`, читающий манифест. Живой
референс-потребитель манифеста — соседняя галерея `ui-gallery`: каталог
и плейграунд компонентов она выводит из `manifest.json` автоматически —
доказательство, что по словарю манифеста UI действительно собирается.

### Состояния экрана

Канон-состояния (`loading`, `empty`, `error`, `permission-denied`,
`offline`, `not-found`) — канон слоя screens, от словаря библиотеки они
не зависят. Их облик описывается композицией и текстом (`layout:`-узлы
+ children-строки); когда в манифесте есть подходящий компонент — рефом
(`ui:Spinner`; `ui:Skeleton (planned)` — forward-реф).

## Anti-patterns

- ❌ Облик в артефакте: цвета, типографика, пиксели, `style=`. Это craft
  библиотеки.
- ❌ Оси контекста как props компонентов или поля артефактов:
  `data-brand` / `data-scheme` / `data-density` / `data-mode` живут на
  корне приложения, `dir` — на узле-носителе (`StitProvider`), не в
  YAML дерева.
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

Прямой автоматической связи нет. Wireframe и hi-fi субстрат на
`@stit/ui` собирает автор макета **вручную** по
`docs/projects/<project-slug>/screens/<surface>/`. Отдельного
артефакта-моста между screens и кодом нет и не планируется.
