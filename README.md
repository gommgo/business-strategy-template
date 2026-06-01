# ST IT — шаблон проекта дизайна

Шаблон, который импортируется **под проект**. Аналитик описывает
продукт в `docs/project/`, интерфейс — аналитическими артефактами в
`docs/interface/`, композицию и облик — артефактами в `docs/screens/`.
По `docs/screens/` автор макета **вручную** собирает wireframe и hi-fi
субстрат на библиотеке `@stit-design/ui`.

Поток: **продукт (vision/persona/capability/...) → интерфейс (who/
situation/zone/...) → экраны (flow/screen/block/shell) → wireframe →
hi-fi субстрат.** Артефакты — чистая аналитика и на код напрямую не
мапятся; превращение в код — ручная работа автора макета, не отдельный
артефакт.

## Два репозитория

| Репо | Что | Роль |
|---|---|---|
| **этот** | артефакты аналитики продукта, интерфейса и экранов, воркфлоу скилов | проектный шаблон |
| **`@stit-design/ui`** (репо `ui-lib`) | библиотека компонентов + галерея | потребляется как зависимость из Gitea registry |

Граница чистая: библиотека строится один раз и версионируется; проект
её **потребляет**, не правит.

## Структура

```
docs/project/     продуктовая аналитика — корень всего (см. docs/project/README.md):
  vision.md         singleton: Problem / Success / Non-goals
  persona.md        сегменты адресатов
  capability.md     бизнес-возможности верхнего уровня
  boundary.md       явные non-goals с обоснованием
  surface.md        поверхности (web/mobile/api/admin/bot/...)
  integration.md    внешние системы
  constraint.md     регуляторика / SLA / контракты
  market.md         рыночные аналоги
docs/interface/   аналитика интерфейса (см. docs/interface/README.md):
  who.md            участники
  stage.md          этапы бизнес-процесса (порядок строк = порядок этапов)
  situation.md      ситуации (кто/когда/что/ради чего/с какими данными)
  zone.md           зоны интерфейса (parent-zone — вложенность)
  block.md          блоки (узел навигации + контейнер субстратов)
  ux-substrate.md   UX-субстраты (type + name + situation)
  data-items.md     элементы данных (entry/exit ситуации)
docs/domains/     (опционально) бизнес-домены бэкенда:
  <ctx>/            контексты по DDD-канону
docs/screens/     аналитика композиции и облика (см. docs/screens/README.md):
  flows/            пользовательские сценарии (viewport-вариативность)
  screens/          route/view с типизированными слотами
  blocks/           раскрытие interface-block в дерево компонентов
  shells/           каркасы со слотами
  assets/           визуальные референсы артефактов
.claude/
  skills/
    project-deep-dive               — аналитик ведёт через 8 фаз вижн-мейкинга
    project-deep-dive-for-business  — клиент-режим: бизнес-язык, эскалация, push в client/<ts>
    project-audit                   — внутрипроектная консистентность
    interface-deep-dive · interface-audit
    domain-deep-dive                — DDD-артефакты бэкенда
    screen-deep-dive · screen-audit
    cross-audit                     — сквозная семантика project ↔ interface ↔ domain ↔ screen
  rules/
    forward-only
```

## Воркфлоу

Начинаем с продукта — без него UX-аналитика и экраны зависают в
воздухе. Сквозной аудит — в конце, или после крупных изменений.

```
1. /project-deep-dive                 — продуктовая аналитика для аналитика
   ИЛИ /project-deep-dive-for-business  — то же для клиента (бизнес-язык, эскалация,
                                          push в branch client/<UTC-ts>).
2. /project-audit                     — узкий аудит внутри project-слоя.
3. /interface-deep-dive               — UX-сущности (who/situation/zone) из якорей
                                        project.persona / capability / surface.
4. /interface-audit                   — консистентность interface.
5. /domain-deep-dive                  — (опц.) бизнес-домены бэкенда; контекст и
                                        use-case цепляются к project.capability,
                                        адаптеры — к project.integration.
6. /screen-deep-dive                  — flows/screens/blocks/shells из interface +
                                        project.surface как scope.
7. /screen-audit                      — консистентность screens.
8. /cross-audit                       — сквозной семантический аудит project ↔
                                        interface ↔ domain ↔ screen (рой агентов).
```

Каждый deep-dive ведёт сессию через `AskUserQuestion`, держит state в
`.claude/skills/<имя>/state/`, не выдумывает домен, не повышает
`draft → stable` без явного подтверждения.

## Инварианты

- **Forward-only** — только «что есть и куда идём», без журналов прошлого.
- **Артефакты — source of truth**, всё остальное собирается по ним.
  Project — корень, всё растёт оттуда.
- **Связи между слоями семантические**, не slug-валидируемые.
  `/cross-audit` ловит расхождения через рой агентов, не grep.
- **Дизайн-облик — из craft-экспертизы библиотеки**, не из головы агента.
- **Продуктовая экспертиза — из ответов бизнеса**, не из головы агента.
- **Коммит / push — гейт человека.** Без явной просьбы агент не коммитит.
