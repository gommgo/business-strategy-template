---
name: fsd-audit
description: "Аудит FSD-карты кабинета в `docs/projects/<slug>/fsd/<surface>/` по папке на фронтовую поверхность: ссылки на экраны, ситуации и домены, путь и охрана страниц против маршрута и доступа экранов, тип `ui-type` из словаря компонентов, сценарии данных по наборам состояний, локали по реестру текстов, зеркало виджетов, cross-feature, пути `src/`, библиотеки и облик в ячейках. Только отчёт, правки — через `/fsd-deep-dive`. Звать перед коммитом карты, по предложению `/fsd-deep-dive` или при подозрении на рассогласование; без `<project-slug>` — пикер, без `<surface>` — все поверхности."
---

# fsd-audit

Аудит консистентности 8 артефактных файлов FSD-карты **одной
фронтовой поверхности** проекта в `docs/projects/<project-slug>/fsd/<surface>/`.
Канон формы — `docs/projects/_template/fsd/README.md`. Аудит **читает и
сообщает**, ничего не правит: каскадные правки идут через `fsd-deep-dive`.

Слой партиционируется по поверхности; ссылочные проверки внутри слоя идут
**в пределах одной поверхности**, ссылки на источники — в слои
`interface/<surface>/`, `screens/<surface>/` (экраны, блоки, реестр
текстов `texts.md`), `services/<svc>/domains/` **того же проекта**; типы
`ui-type` — в словарь компонентов
`../design-deep-dive/kb/common/components.yaml` и расширения проекта
(раздел `extensions` `docs/projects/<project-slug>/design/system.yaml`).
Аудит итерирует по каждой папке поверхности независимо; проверки — чтением
по форме `docs/projects/_template/fsd/_template/` и разделу «Связи»
канона.

## Выбор проекта и поверхности

Аргументы позиционны — `<project-slug>` первый, `<surface>` второй (опц.):

1. Первый аргумент — подпапка `docs/projects/` (кроме `_template`) →
   `<project-slug>`; иначе пикер по именам проектов. Проектов нет —
   «нечего аудитить», выйти.
2. Прочитать `surface.md`; следующий аргумент — slug фронтовой поверхности →
   одна поверхность; нет аргумента → все папки `fsd/<surface>/` проекта,
   отчёт группируется по поверхности.
3. Папка `fsd/<surface>/` для поверхности вне реестра, с типом без
   FSD-карты (`bot`, `mobile`, `api`, `other`) или у `web` рода `landing`
   и `site` (на её месте слой страницы) — сама по себе находка
   (`structure`).

Узкий scope: `<kind>` (один файл + перекрёстные ссылки) или
`<kind>:<slug>` (одна запись + 1-shell соседи).
`kind` ∈ {`entities`, `features`, `pages`, `widgets`, `app`, `shared-ui`,
`shared-api`, `shared-lib`}.

## Проверки

**Структура (`structure`)**
- Папка поверхности соответствует реестру `surface.md` и фронтовому типу
  поверхности: `web` рода `app`, `admin`, `desktop`, `embed`; папка у
  `web` рода `landing` или `site` — error (код сайта читает слой
  страницы).
- Все 8 файлов на месте, H1 = имя файла, таблицы соответствуют канону
  колонок формы (у `shared-ui` — колонка `ui-type`).

**Ссылки на источники (`source-refs`)**
- `features.situation` существует в `interface/<surface>/situation.md`.
- `pages.screen` — существующий экран `screens/<surface>/screens/<slug>/`;
  `widgets.block` (не `—`) — существующий блок
  `screens/<surface>/blocks/<slug>/`.
- `pages.path` — маршрут (`route`) экрана `pages.screen`, параметры пути
  — его `params`; не совпал — error. Экран с маршрутом без page — hint
  (экран-оверлей с маршрутом `modal:<имя>` — не page). Норма —
  `docs/projects/_template/fsd/_template/pages.md`, критерий 2.
- `pages.guard` — доступ (`access`) экрана: `public`, `authenticated` или
  роли — `who` экрана при `access: roles`; не совпал — error. Норма —
  `pages.md`, критерий 3.
- `shared-ui.ui-type` — ключ раздела `types` словаря компонентов или id
  расширения проекта; тип вне словаря и расширений — error, имя из `aka`
  — error с подсказкой типа. Норма — `shared-ui.md`, критерий 2.
- `entities.source` резолвится в `services/<svc>/domains/<ctx>/` или в
  `interface/<surface>/data-items.md`.
- Ссылка в сущность **другой поверхности** — error (изоляция).

**Внутрислойные ссылки (`layer-refs`)**
- `features.entities`, `pages.{widgets,features,entities}`,
  `widgets.{entities,features}` указывают на существующие записи.
- Зеркало: `widgets.pages` == фильтр `pages.widgets ∋ <widget>`.
- Widget с <2 page-референсами без пометки зоны каркаса — warning
  (pages-first).
- Feature, ссылающаяся на feature (через любые колонки), — error
  (cross-feature).

**Семантика (`semantics`)**
- `src/`-пути, имена файлов, импорты, названия библиотек в любой ячейке —
  warning: исполнительная сторона живёт во фронт-форке `<org>/frontend`.
- Значения облика в ячейках — цвета, шрифты, отступы, вид и размер
  компонента — warning: тему фронт выпускает из токенов дизайн-системы
  проекта (`fsd/README.md`, раздел «Связи»).
- Слайс, чьё имя не восходит к источнику (аббревиатура без соответствия
  `situation`/`screen`/домену), — hint.
- `shared-api`: entity без покрытия сценариями — warning; состояние,
  которое есть в обязательных наборах экранов поверхности (`partial-few`,
  `overflow-many`, `loading-initial`, `error-load`, `no-permission`), без
  сценария данных с тем же именем — warning; сценарий состояния, которого
  в наборах нет, — hint. Норма — `shared-api.md`, критерий 2; канон
  экранов, «Обязательный набор».
- `shared-lib`: локали не совпадают с колонками языков реестра текстов
  `screens/<surface>/texts.md` (`default` — `text`, `supported` —
  `text-<locale>`) — warning; строки локализации в самой карте вместо
  реестра — warning. Норма — `shared-lib.md`, раздел «i18n».
- `app`: init-шаг без `при падении` — warning.

**Зрелость (`maturity`)**
- `stable`-запись с пустым обязательным слотом — error.
- `stable`, ссылающийся на `draft`, — hint (не блокер).
- `**blocker**` в ветке state
  (`../entrypoint/state/projects/<project-slug>/fsd/<surface>/`) у
  `stable`-записи — error.

## Отчёт

Группировка: поверхность → категория (`structure` / `source-refs` /
`layer-refs` / `semantics` / `maturity`) → находки. Каждая находка: файл,
slug записи, severity (`error` / `warning` / `hint`), одна строка сути,
рекомендация «что сделать через `/fsd-deep-dive`». В конце — счётчик по
severity и вердикт: чисто / есть warnings / есть errors.

Stable-записи читает `/scaffold` фронт-форка `<org>/frontend`, поэтому
errors в stable материализуются в код.

## Запреты

- Не править артефакты и state — только отчёт.
- Не выдумывать «правильные» значения — рекомендация ведёт в
  `fsd-deep-dive`, не подменяет архитектора.
- Не расширять scope сверх заданного аргументами.
