# Артефакты FSD-карты

FSD-слой проекта **партиционируется по поверхности (surface)**: на каждую
фронтовую поверхность из реестра `surface.md` (`type: web` рода `app` /
`admin` / `desktop` / `embed`) — своя папка
`docs/projects/<project-slug>/fsd/<surface>/` с 8 плоскими md-файлами. Этот
файл — **канон слоя**; форма одной папки поверхности (те самые 8 файлов)
лежит рядом в [`_template/`](_template/) — её копируют под каждый slug
поверхности. Для `type: bot` слоя нет (композиция —
`telegram-bot-flow/<surface>/`), для `type: mobile` — тоже (композиция и
карта кода — `mobile/<surface>/`), для `type: api` — тоже (UI отсутствует).

У `type: web` FSD-карта есть только у рода `app`: у рода `landing` и `site`
на её месте слой страницы `site/<surface>/` (канон —
[`../site/README.md`](../site/README.md)) — его читает код сайта, а interface
и экранов у такой поверхности нет.

Слой — **мост «аналитика → фронт-код»**: он переводит ситуации
(`interface/<surface>/`), экраны и блоки (`screens/<surface>/`) и доменные
сущности (`services/<svc>/domains/<ctx>/`) в карту слайсов по слоям
Feature-Sliced Design. Это единственное место проекта, где FSD-имена
легальны: в interface/screens/project их нет (см. их каноны и правило
R-SEM-003 screen-аудита).

Потребитель слоя — форк `<org>/frontend` (шаблон `spa-frontend-template`,
React SPA: кабинет за логином): его `/scaffold` и `/de-template` читают
stable-записи cross-repo и сами выводят файловую раскладку
`src/<layer>/<slice>/` из kind + slug. Код сайта `<org>/site` FSD-карту не
читает — его вход слой страницы. Какую поверхность разворачивает форк, решает привязка в
код-репо (поле `surface` его `docs/stack/service.md`). **`src/`-путей, имён файлов и выбора библиотек в артефактах нет** — это
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
`docs/projects/<project-slug>/fsd/<surface>/` (одна папка на фронтовую поверхность
из реестра `surface.md`).

## Файлы

| файл | kind | описывает |
|---|---|---|
| [`entities.md`](_template/entities.md) | сущность (data-oriented) | карта entities: источник (домен / data-item), поля, связи |
| [`features.md`](_template/features.md) | сценарий действия (action-oriented) | карта features: ситуация-источник, задействованные entities, результат |
| [`pages.md`](_template/pages.md) | маршрут (1 page = 1 route) | карта pages: экран-источник, путь и guard — маршрут и доступ экрана, композиция |
| [`widgets.md`](_template/widgets.md) | переиспользуемый блок | карта widgets: блок-источник, композиция, page-референсы (≥2) |
| [`app.md`](_template/app.md) | bootstrap поверхности | init-последовательность и providers |
| [`shared-ui.md`](_template/shared-ui.md) | проектный UI-примитив | карта переиспользуемых компонентов: тип словаря, который реализует слайс (`ui-type`), без привязки к внешней UI-библиотеке |
| [`shared-api.md`](_template/shared-api.md) | контракт данных | сценарии данных по обязательным состояниям экранов, покрытие entities |
| [`shared-lib.md`](_template/shared-lib.md) | сквозная утилита | локали (ключи строк — реестр текстов экранов) и generic-состав |

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
- **page → экран** (M:1): `pages.screen` → экран
  `screens/<surface>/screens/<slug>/`.
- **page → композиция** (M:N): `pages.widgets` / `pages.features` /
  `pages.entities` — канонические источники использования.
- **widget → блок** (M:1, опц.): `widgets.block` →
  блок `screens/<surface>/blocks/<slug>/`.
- **widget ← pages** (M:N): `widgets.pages` — **зеркало для наглядности**;
  должно соответствовать фильтру `pages.widgets ∋ <widget>`. Инвариант
  **pages-first**: у widget ≥2 page-референсов, иначе блок остаётся внутри
  page-слайса.
- **entity → источник** (M:1): `entities.source` — агрегат/сущность домена
  (`<svc>/<ctx>/<slug>` из `services/<svc>/domains/<ctx>/`) или, если
  бэка нет, `data-items` своей поверхности.
- **cross-feature запрещён**: фича не ссылается на фичу; общее поднимается
  в entities/shared или композируется в page/widget.

Со слоями экранов и дизайна той же поверхности:

- **page → маршрут и доступ экрана**: `pages.path` — маршрут (`route`)
  экрана `pages.screen` с его параметрами (`params`), `pages.guard` — его
  доступ (`access`); состояние в адресе (`url-state`) код читает из экрана,
  в карте его нет (`../screens/_template/screen.md`).
- **shared-ui → тип словаря**: `shared-ui.ui-type` — тип закрытого словаря
  `kb/common/components.yaml` или расширения проекта. Слайс поднимается при
  реальном переиспользовании, поэтому не каждый тип экранов получает слайс:
  покрытие типов компонентами проверяет дизайн-система (ДС) проекта
  (`../design/README.md`, раздел «Покрытие компонентов»).
- **shared-api → состояния экранов**: сценарии данных покрывают
  обязательные наборы состояний экранов поверхности (`../screens/README.md`,
  раздел «Обязательный набор»); данные — производный демо-набор экранов.
- **shared-lib → реестр текстов**: ключи строк локализации — ключи реестра
  текстов интерфейса `screens/<surface>/texts.md`.
- **тема → токены ДС**: облика в карте нет — тему фронт выпускает из токенов
  ДС проекта (`docs/projects/<project-slug>/design/system.tokens.json`, канон
  — [`../design/README.md`](../design/README.md), раздел «ДС»).

## Статус записи

Как в interface-слое: `draft` → `stable` через `/fsd-deep-dive` по
подтверждению архитектора; понижение — только руками. `stable` может
ссылаться на `draft` (hint в `/fsd-audit`, не блокер). Фронт-форки
разворачивают только stable-записи.

## Workflow

```
/fsd-deep-dive — единственная точка входа.
```

Скилл заводит слайсы из источников (ситуации / экраны / домены), углубляет
частичные, разбирает сырьё (эскиз, набросок сценариев), ведёт переход
`draft → stable`. В конце сессии предлагает `/fsd-audit` — аудит
консистентности (битые ссылки на источники, `path` и `guard` против
маршрута и доступа экрана, `ui-type` вне словаря, рассинхрон зеркал,
widget-с-одним-референсом, cross-feature).

## Anti-patterns

- ❌ `src/`-пути, имена файлов, импорты, названия библиотек — исполнительная
  сторона (фронт-форк, его `docs/stack/` и `/scaffold`).
- ❌ Слайс без источника в аналитике (page без screen, feature без situation,
  entity без домена/data-item) — сначала аналитика, потом карта.
- ❌ FSD-имена (`widget`, `feature`, `entity`, `page`) в артефактах других
  слоёв — FSD живёт только здесь (в screens их ловит R-SEM-003 screen-аудита).
- ❌ Widget с одним page-референсом (pages-first).
- ❌ Feature, ссылающаяся на feature (cross-feature).
- ❌ Облик в карте слайсов — цвет, типографика, отступы, вид и размер
  компонента: его решает слой дизайна токенами ДС проекта, фронт выпускает из
  них тему; уровень действия (`level=primary`) — атрибут узла дерева screens,
  не карты слайсов.
- ❌ `path` или `guard`, которые расходятся с маршрутом и доступом
  экрана-источника; `ui-type` вне словаря и расширений проекта.
- ❌ Ссылка из папки одной поверхности в сущность другой поверхности —
  поверхности изолированы, общее сводит `/cross-audit`.
- ❌ `fsd/<surface>/` у поверхности `web` рода `landing` или `site`: на её
  месте слой страницы.
