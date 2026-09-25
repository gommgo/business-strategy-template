---
name: fsd-audit
description: "Аудит консистентности FSD-карты проекта в `docs/projects/<project-slug>/fsd/<surface>/` — по папке на фронтовую поверхность (`type: web|admin|desktop|embed`) из реестра `surface.md`. Невалидные ссылки на источники (situation/screen/block/домен/data-item), битые внутрислойные ссылки, рассинхрон зеркала `widgets.pages` ↔ `pages.widgets`, widget с <2 page-референсами (pages-first), cross-feature, `src/`-пути и имена библиотек в артефактах, entities без покрытия в shared-api, пустые обязательные слоты в stable-записях, папка поверхности вне реестра. Не правит артефакты, только указывает; деструктивные правки — через `fsd-deep-dive`. Использовать перед коммитом артефактов, когда `fsd-deep-dive` предлагает прогон в конце сессии, или при подозрении на рассогласование. Принимает `<project-slug>` первым аргументом; без него — пикер. Без `<surface>` — прогон по всем папкам фронтовых поверхностей; узкий scope — `<kind>` или `<kind>:<slug>`."
---

# fsd-audit

Аудит консистентности 8 артефактных файлов FSD-карты **одной
фронтовой поверхности** проекта в `docs/projects/<project-slug>/fsd/<surface>/`.
Канон формы — `docs/projects/_template/fsd/README.md`. Аудит **читает и
сообщает**, ничего не правит: каскадные правки идут через `fsd-deep-dive`.

Слой партиционируется по поверхности; ссылочные проверки внутри слоя идут
**в пределах одной поверхности**, ссылки на источники — в слои
`interface/<surface>/`, `screens/<surface>/`, `services/<svc>/domains/`
**того же проекта**. Аудит итерирует по каждой папке поверхности независимо.

## Выбор проекта и поверхности

Аргументы позиционны — `<project-slug>` первый, `<surface>` второй (опц.):

1. Первый аргумент — подпапка `docs/projects/` (кроме `_template`) →
   `<project-slug>`; иначе пикер по именам проектов. Проектов нет —
   «нечего аудитить», выйти.
2. Прочитать `surface.md`; следующий аргумент — slug фронтовой поверхности →
   одна поверхность; нет аргумента → все папки `fsd/<surface>/` проекта,
   отчёт группируется по поверхности.
3. Папка `fsd/<surface>/` для поверхности вне реестра или с типом без FSD-карты (`bot`, `mobile`, `api`, `other`) —
   сама по себе находка (`structure`).

Узкий scope: `<kind>` (один файл + перекрёстные ссылки) или
`<kind>:<slug>` (одна запись + 1-shell соседи).
`kind` ∈ {`entities`, `features`, `pages`, `widgets`, `app`, `shared-ui`,
`shared-api`, `shared-lib`}.

## Проверки

**Структура (`structure`)**
- Папка поверхности соответствует реестру `surface.md` и фронтовому типу поверхности.
- Все 8 файлов на месте, H1 = имя файла, таблицы соответствуют канону
  колонок формы.

**Ссылки на источники (`source-refs`)**
- `features.situation` существует в `interface/<surface>/situation.md`.
- `pages.screen` — существующий экран `screens/<surface>/screens/<slug>/`;
  `widgets.block` (не `—`) — существующий блок
  `screens/<surface>/blocks/<slug>/`.
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
  warning: исполнительная сторона живёт во фронт-форке поверхности
  (`<org>/frontend` или `<org>/site`).
- Слайс, чьё имя не восходит к источнику (аббревиатура без соответствия
  `situation`/`screen`/домену), — hint.
- `shared-api`: entity без покрытия сценариями — warning.
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

Stable-записи читает `/scaffold` фронт-форка поверхности
(`<org>/frontend` или `<org>/site`), поэтому errors в stable
материализуются в код.

## Запреты

- Не править артефакты и state — только отчёт.
- Не выдумывать «правильные» значения — рекомендация ведёт в
  `fsd-deep-dive`, не подменяет архитектора.
- Не расширять scope сверх заданного аргументами.
