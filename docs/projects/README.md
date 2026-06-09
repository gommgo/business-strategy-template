# Проекты

Корень решения: **несколько проектов** под одним бизнесом. Каждый проект —
папка `docs/projects/<project-slug>/`, внутри которой живёт вся аналитика
этого продукта: продуктовый слой (vision + реестр-хребет поверхностей +
kind), UX-интерфейс (`interface/<surface>/`), композиция экранов
(`screens/<surface>/`) и бизнес-домены бэкенда (`domains/`, опц.).

**Поверхность (surface) — ось продукта.** Реестр `surface.md` объявляет
поверхности (web, mobile, бот, API …), а их slug'и партиционируют
возможности, интерфейс и экраны: каждая поверхность описывается сверху вниз
в своей папке. Точки стыка **между проектами** одного бизнеса — в
[`project-map.md`](project-map.md).

## Структура

```
docs/projects/
├── README.md            (этот файл)
├── project-map.md       ← карта стыков между продуктами бизнеса (singleton)
├── _template/           ← КАНОН формы (образец, не данные проекта)
│   ├── project/         канон продуктового слоя (vision + surface-реестр + kind)
│   ├── interface/       канон UX-слоя одной поверхности (who/stage/situation/…)
│   ├── screens/         канон слоя экранов одной поверхности (flow/screen/block/shell)
│   ├── domains/         канон DDD-слоя (_templates/, _shared/)
│   └── project-map.md   канон карты проектов
└── <project-slug>/      ← ДАННЫЕ одного проекта
    ├── README.md        чем продукт, какие проблемы закрывает
    ├── vision.md        singleton + addresses-problem (M:N → business-problem)
    ├── surface.md       РЕЕСТР-ХРЕБЕТ поверхностей
    ├── user.md … market.md   кросс-поверхностные kind продукта
    ├── capability/<surface>.md   возможности по поверхности
    ├── interface/<surface>/      who/stage/situation/zone/block/ux-substrate/data-items
    ├── screens/<surface>/        flows/ screens/ blocks/ shells/ assets/
    └── domains/         (опц.) <bounded-context>/  (по контексту, не по surface)
```

Канон формы живёт **один раз** в `_template/`; папки проектов держат только
данные. Скилы читают форму из `_template/<слой>/`, пишут данные в
`<project-slug>/...`. `_template/` — read-only образец: его не правят под
конкретный проект. Форма `_template/interface/` и `_template/screens/` —
канон **одной папки поверхности**; в данных она повторяется под каждый slug
из реестра `surface.md`.

## Связь с проблемой (M:N)

Реестр проблем бизнеса (`business-problem` в `docs/business/`) — **общий
для всех проектов** слой. Каждый проект объявляет, какие проблемы он
закрывает, полем `addresses-problem` в своём `vision.md` (массив slug-рефов
на строки реестра `business-problem`). Проблему могут закрывать несколько
проектов, проект — несколько проблем (M:N). Авторская сторона связи —
продукт; обратную (какие проекты бьют в проблему) сводит `/cross-audit`.

## Взаимодействие проектов (project-map)

Проекты бизнеса не изолированы — продукты стыкуются (приложение лояльности
шлёт баллы в магазин, аналитика читает заказы). Каждый такой стык —
ребро в [`project-map.md`](project-map.md). Авторская сторона ребра —
`integration` проекта-инициатора (`target: sibling-project`); карта сводит
их в граф; техническое воплощение — порт/события в `domains/`.
Согласованность трёх сторон сверяет `/cross-audit`.

## Выбор проекта и поверхности в скилах

Скилы слоёв project / interface / domain / screen работают **в контексте
одного проекта**; interface и screen — ещё и **в контексте одной
поверхности**. Аналитический скилл принимает `<project-slug>` первым
аргументом (`/interface-deep-dive <slug> [<surface>] …`); без аргументов —
пикеры по **человекочитаемым именам**: сначала проект (заголовок из
`vision`), затем поверхность (`surface.name`). Клиент-режим
(`/entrypoint-for-business`) всегда ведёт дружелюбными пикерами «какой
продукт» и «где он работает», без slug.

Новый проект заводит `/project-deep-dive` (копирует форму из
`_template/project/` в новую папку проекта); папки поверхностей под
`interface/`/`screens/` заводят их скилы при первом заходе на поверхность —
каталоги руками не создаём.

## Каноны слоёв

- [`_template/project/README.md`](_template/project/README.md) — продукт (vision + surface-реестр + kind).
- [`_template/interface/README.md`](_template/interface/README.md) — интерфейс одной поверхности.
- [`_template/screens/README.md`](_template/screens/README.md) — экраны одной поверхности.
- [`_template/domains/README.md`](_template/domains/README.md) — бизнес-домены бэкенда.
- [`_template/project-map.md`](_template/project-map.md) — карта стыков между проектами.

## Anti-patterns

- ❌ Данные проекта в `_template/` (там только форма-образец).
- ❌ Дублирование канона в папку проекта (`<slug>/interface/README.md`
  и т.п.) — форма живёт один раз в `_template/`.
- ❌ Папка поверхности (`capability/<surface>.md`, `interface/<surface>/`,
  `screens/<surface>/`) для поверхности, которой нет в реестре `surface.md`.
- ❌ Создание каталога проекта или папки поверхности руками вместо скила.
- ❌ Жёсткие slug-валидации между проектом и `business-problem`. Связь
  семантическая (`addresses-problem`), ловит `/cross-audit`.
- ❌ Стык между продуктами бизнеса как обычная внешняя `integration`
  (`target: external`) — для соседнего проекта `target: sibling-project`
  + ребро в `project-map.md`.
