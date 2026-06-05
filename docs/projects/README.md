# Проекты

Корень решения: **несколько проектов** под одним бизнесом. Каждый проект —
папка `docs/projects/<project-slug>/`, внутри которой живёт вся аналитика
этого продукта: продуктовый слой (vision + 7 kind), UX-интерфейс
(`interface/`), бизнес-домены бэкенда (`domains/`, опц.) и композиция
экранов (`screens/`).

## Структура

```
docs/projects/
├── README.md            (этот файл)
├── _canon/              ← КАНОН формы (образец, не данные проекта)
│   ├── project/         канон продуктового слоя (vision + 7 kind)
│   ├── interface/       канон UX-слоя (who/stage/situation/...)
│   ├── screens/         канон слоя экранов (flow/screen/block/shell)
│   └── domains/         канон DDD-слоя (_templates/, _shared/)
├── <project-slug>/      ← ДАННЫЕ одного проекта
│   ├── README.md        чем продукт, какие проблемы закрывает
│   ├── vision.md        singleton + addresses-problem (M:N → business-problem)
│   ├── user.md … market.md   7 kind продукта
│   ├── interface/       who/stage/situation/zone/block/ux-substrate/data-items
│   ├── screens/         flows/ screens/ blocks/ shells/
│   └── domains/         (опц.) <bounded-context>/
└── example/             ← показная витрина screens-слоя (удаляется /de-template)
```

Канон формы живёт **один раз** в `_canon/`; папки проектов держат только
данные. Скилы читают форму из `_canon/<слой>/`, пишут данные в
`<project-slug>/...`. `_canon/` — read-only образец: его не правят под
конкретный проект.

## Связь с проблемой (M:N)

Реестр проблем бизнеса (`business-problem` в `docs/business/`) — **общий
для всех проектов** слой. Каждый проект объявляет, какие проблемы он
закрывает, полем `addresses-problem` в своём `vision.md` (массив slug-рефов
на строки реестра `business-problem`). Проблему могут закрывать несколько
проектов, проект — несколько проблем (M:N). Авторская сторона связи —
продукт; обратную (какие проекты бьют в проблему) сводит `/cross-audit`.

## Выбор проекта в скилах

Скилы слоёв project / interface / domain / screen работают **в контексте
одного проекта**. Аналитический скилл принимает `<project-slug>` первым
аргументом (`/interface-deep-dive <slug> …`); без него — предлагает пикер
по папкам `docs/projects/`. Клиент-режим (`*-for-business`) всегда
показывает дружелюбный пикер «какой продукт обсуждаем», без slug.

Новый проект заводит `/project-deep-dive` (копирует форму из
`_canon/project/` в новую папку проекта) — каталоги руками не создаём.

## Каноны слоёв

- [`_canon/project/README.md`](_canon/project/README.md) — продукт (vision + 7 kind).
- [`_canon/interface/README.md`](_canon/interface/README.md) — интерфейс.
- [`_canon/screens/README.md`](_canon/screens/README.md) — экраны.
- [`_canon/domains/README.md`](_canon/domains/README.md) — бизнес-домены бэкенда.

## Anti-patterns

- ❌ Данные проекта в `_canon/` (там только форма-образец).
- ❌ Дублирование канона в папку проекта (`<slug>/interface/README.md`
  и т.п.) — форма живёт один раз в `_canon/`.
- ❌ Создание каталога проекта руками вместо `/project-deep-dive`.
- ❌ Жёсткие slug-валидации между проектом и `business-problem`. Связь
  семантическая (`addresses-problem`), ловит `/cross-audit`.
