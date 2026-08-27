# Артефакты FSD-карты

FSD-слой проекта **партиционируется по поверхности (surface)**: на каждую
SPA-поверхность из реестра `surface.md` (`type: web` / `admin` / `desktop` /
`embed`) — своя папка `docs/projects/<project-slug>/fsd/<surface>/` с 8
плоскими md-файлами. Этот файл — **канон слоя**; форма одной папки
поверхности (те самые 8 файлов) лежит рядом в [`_template/`](_template/) —
её копируют под каждый slug поверхности. Для `type: bot` слоя нет
(композиция — `telegram-bot-flow/<surface>/`), для `type: api` — тоже (UI
отсутствует).

Слой — **мост «аналитика → фронт-код»**: он переводит ситуации
(`interface/<surface>/`), экраны и блоки (`screens/<surface>/`) и доменные
сущности (`services/<svc>/domains/<ctx>/`) в карту слайсов по слоям
Feature-Sliced Design. Это единственное место проекта, где FSD-имена
легальны: в interface/screens/project их по-прежнему нет (см. их каноны и
правило R-SEM-003 screen-аудита).

Потребитель слоя — форк `<org>/frontend` (шаблон `spa-frontend-template`):
его `/scaffold` и `/de-template` читают stable-записи cross-repo и сами
выводят файловую раскладку `src/<layer>/<slice>/` из kind + slug.
**`src/`-путей, имён файлов и выбора библиотек в артефактах нет** — это
исполнительная сторона фронт-форка (его `docs/stack/`).

## Структура

```
docs/projects/_template/fsd/
├── README.md          ← этот файл (канон слоя)
└── _template/         ← форма одной папки поверхности (копируется под surface)
    ├── app.md
    ├── pages.md
    ├── widgets.md
    ├── features.md
    ├── entities.md
    ├── shared-ui.md
    ├── shared-api.md
    └── shared-lib.md
```

Данные живут в папке поверхности проекта
`docs/projects/<project-slug>/fsd/<surface>/` (одна папка на SPA-поверхность
из реестра `surface.md`).

## Файлы

| файл | kind | описывает |
|---|---|---|
| [`entities.md`](_template/entities.md) | сущность (data-oriented) | карта entities: источник (домен / data-item), поля, связи |
| [`features.md`](_template/features.md) | сценарий действия (action-oriented) | карта features: ситуация-источник, задействованные entities, результат |
| [`pages.md`](_template/pages.md) | маршрут (1 page = 1 route) | карта pages: экран-источник, путь, guard, композиция |
| [`widgets.md`](_template/widgets.md) | переиспользуемый блок | карта widgets: блок-источник, композиция, page-референсы (≥2) |
| [`app.md`](_template/app.md) | bootstrap поверхности | init-последовательность и providers |
| [`shared-ui.md`](_template/shared-ui.md) | проектный UI-примитив | карта переиспользуемых компонентов (design-system-agnostic) |
| [`shared-api.md`](_template/shared-api.md) | контракт данных | сценарии данных для мок-режима, покрытие entities |
| [`shared-lib.md`](_template/shared-lib.md) | сквозная утилита | i18n-локали и generic-состав |

Порядок проектирования — **inside-out**: entities → features → pages →
widgets → app → shared-ui → shared-api → shared-lib.

## Принципы оформления

Как в interface-слое: один файл — одна таблица сущностей одного типа
(app/shared-api/shared-lib дополнительно держат свои секции по канону
своего файла). H1 = имя файла = kind, frontmatter не нужен. Первые три
колонки везде — `slug` · `name` · `description`, **последняя** — `status`
(`draft` \| `stable`, зрелость записи). Форма ячеек — единая по проекту
(см. канон interface-слоя): slug-рефы в бэктиках, массивы питон-стилем,
пустое опциональное — `—`.

Имена слайсов — по сценарию/сущности источника (`situation.name`,
имя агрегата), не аббревиатуры.

## Связи

Внутри поверхности (канонические источники и зеркала):

- **feature → ситуация** (M:1): `features.situation` →
  `interface/<surface>/situation.md`.
- **feature → сущности** (M:N): `features.entities` → `entities.md`.
- **page → экран** (M:1): `pages.screen` → `screens/<surface>/screen.md`.
- **page → композиция** (M:N): `pages.widgets` / `pages.features` /
  `pages.entities` — канонические источники использования.
- **widget → блок** (M:1, опц.): `widgets.block` →
  `screens/<surface>/block.md`.
- **widget ← pages** (M:N): `widgets.pages` — **зеркало для наглядности**;
  должно соответствовать фильтру `pages.widgets ∋ <widget>`. Инвариант
  **pages-first**: у widget ≥2 page-референсов, иначе блок остаётся внутри
  page-слайса.
- **entity → источник** (M:1): `entities.source` — агрегат/сущность домена
  (`<svc>/<ctx>/<slug>` из `services/<svc>/domains/<ctx>/`) или, если
  бэка нет, `data-items` своей поверхности.
- **cross-feature запрещён**: фича не ссылается на фичу; общее поднимается
  в entities/shared или композируется в page/widget.

## Статус записи

Как в interface-слое: `draft` → `stable` через `/fsd-deep-dive` по
подтверждению архитектора; понижение — только руками. `stable` может
ссылаться на `draft` (hint в `/fsd-audit`, не блокер). Форк
`<org>/frontend` разворачивает только stable-записи.

## Workflow

```
/fsd-deep-dive — единственная точка входа.
```

Скилл заводит слайсы из источников (ситуации / экраны / домены), углубляет
частичные, разбирает сырьё (эскиз, набросок сценариев), ведёт переход
`draft → stable`. В конце сессии предлагает `/fsd-audit` — аудит
консистентности (битые ссылки на источники, рассинхрон зеркал,
widget-с-одним-референсом, cross-feature).

## Anti-patterns

- ❌ `src/`-пути, имена файлов, импорты, названия библиотек — исполнительная
  сторона (`<org>/frontend`, его `docs/stack/` и `/scaffold`).
- ❌ Слайс без источника в аналитике (page без screen, feature без situation,
  entity без домена/data-item) — сначала аналитика, потом карта.
- ❌ FSD-имена (`widget`, `feature`, `entity`, `page`) в артефактах других
  слоёв — FSD живёт только здесь (R-SEM-003 в screen-аудите остаётся).
- ❌ Widget с одним page-референсом (pages-first).
- ❌ Feature, ссылающаяся на feature (cross-feature).
- ❌ Облик, цвет, размеры, варианты компонентов — это screens + craft
  `@stit/ui`, не карта слайсов.
- ❌ Ссылка из папки одной поверхности в сущность другой поверхности —
  поверхности изолированы, общее сводит `/cross-audit`.
