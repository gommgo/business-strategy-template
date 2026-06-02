# ST IT — шаблон проекта дизайна

Шаблон, который импортируется **под проект**. Аналитик начинает с
бизнеса заказчика в `docs/business/`, формализует его проблему по
методологии (SWOT + Карта гипотез) в `docs/business-problem/`, под неё
описывает продукт в `docs/project/`, интерфейс — аналитическими
артефактами в `docs/interface/`, композицию и облик — артефактами в
`docs/screens/`. По `docs/screens/` автор макета **вручную** собирает
wireframe и hi-fi субстрат на библиотеке `@stit-design/ui`.

Поток: **бизнес (profile/segment/competitor/...) → бизнес-проблема
(SWOT factor/bet → goal/metric/subject/hypothesis/task) → продукт
(vision/persona/capability/...) → интерфейс (who/situation/zone/...) →
экраны (flow/screen/block/shell) → wireframe → hi-fi субстрат.**
Артефакты — чистая аналитика и на код напрямую не мапятся; превращение в
код — ручная работа автора макета, не отдельный артефакт.

Юр-рамка: гарантируем доставку проекта по scope; метрики
`docs/business-problem/` — best-effort таргет (совместно с бизнесом),
не гарантия исхода.

## Два репозитория

| Репо | Что | Роль |
|---|---|---|
| **этот** | артефакты аналитики продукта, интерфейса и экранов, воркфлоу скилов | проектный шаблон |
| **`@stit-design/ui`** (репо `ui-lib`) | библиотека компонентов + галерея | потребляется как зависимость из Gitea registry |

Граница чистая: библиотека строится один раз и версионируется; проект
её **потребляет**, не правит.

## Структура

```
docs/business/    профиль бизнеса заказчика — верх (см. docs/business/README.md):
  profile.md        singleton: Бизнес / Модель / Позиционирование / Контекст
  segment.md        кого обслуживает бизнес
  offering.md       что продаёт
  channel.md        каналы привлечения/продажи/доставки
  competitor.md     рынок (наполняет рой web-research)
  current-metric.md текущие KPI — baseline-кандидаты
  material.md       реестр источников (сайт/PDF/презентация/соцсети)
docs/business-problem/  формализация проблемы (см. docs/business-problem/README.md):
  frame.md          singleton: Проблема / Гарантируем / Целимся / Вне контроля / Scope
  factor.md         SWOT-фактор (area: strength|weakness|trend|threat)
  bet.md            стратегическая ставка «действие, чтобы ценность»
  goal.md           цель карты гипотез (критерий успеха без цифр)
  metric.md         метрика-таргет (current/target/source/attribution/acceptance)
  subject.md        субъект влияния (+ мотивация, негативный)
  hypothesis.md     гипотеза (если·то·потому что·тогда→metric)
  task.md           задача проверки гипотезы
docs/project/     продуктовая аналитика — корень решения (см. docs/project/README.md):
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
    business-deep-dive              — профиль бизнеса: приём материалов + рой web-research
    business-deep-dive-for-business — клиент-режим профиля бизнеса
    business-problem-deep-dive      — SWOT + Карта гипотез, ядро — метрики
    business-problem-deep-dive-for-business — клиент-режим проблемы (бизнес-язык)
    business-problem-audit          — семантические инварианты методологии (рой)
    project-deep-dive               — аналитик ведёт через 8 фаз вижн-мейкинга
    project-deep-dive-for-business  — клиент-режим: бизнес-язык, эскалация, push в client/<ts>
    project-audit                   — внутрипроектная консистентность
    interface-deep-dive · interface-audit
    domain-deep-dive                — DDD-артефакты бэкенда
    screen-deep-dive · screen-audit
    cross-audit                     — сквозная семантика business ↔ business-problem ↔ project ↔ interface ↔ domain ↔ screen
  rules/
    forward-only
```

## Воркфлоу

Начинаем с бизнеса заказчика — без него проблема и продукт висят в
воздухе. Сквозной аудит — в конце, или после крупных изменений.

```
1. /business-deep-dive                — профиль бизнеса: приём материалов клиента
   ИЛИ /business-deep-dive-for-business  (сайт/PDF/презентации) + рой web-research.
2. /business-problem-deep-dive        — SWOT (factor/bet) → Карта гипотез (goal/
   ИЛИ /business-problem-deep-dive-for-business  metric/subject/hypothesis/task).
                                        Ядро — метрики (best-effort таргет).
3. /business-problem-audit            — семантические инварианты методологии (рой).
4. /project-deep-dive                 — продукт: vision/persona/capability из
   ИЛИ /project-deep-dive-for-business   business-problem.goal/subject/metric.
5. /project-audit                     — узкий аудит внутри project-слоя.
6. /interface-deep-dive               — UX-сущности (who/situation/zone) из якорей
                                        project.persona / capability / surface.
7. /interface-audit                   — консистентность interface.
8. /domain-deep-dive                  — (опц.) бизнес-домены бэкенда; контекст и
                                        use-case цепляются к project.capability,
                                        адаптеры — к project.integration.
9. /screen-deep-dive                  — flows/screens/blocks/shells из interface +
                                        project.surface как scope.
10. /screen-audit                     — консистентность screens.
11. /cross-audit                      — сквозной семантический аудит business ↔
                                        business-problem ↔ project ↔ interface ↔
                                        domain ↔ screen (рой агентов).
```

Каждый deep-dive ведёт сессию через `AskUserQuestion`, держит state в
`.claude/skills/<имя>/state/`, не выдумывает домен, не повышает
`draft → stable` без явного подтверждения.

## Инварианты

- **Forward-only** — только «что есть и куда идём», без журналов прошлого.
- **Артефакты — source of truth**, всё остальное собирается по ним.
  Бизнес — верх, продукт — корень решения; всё растёт сверху вниз.
- **Связи между слоями семантические**, не slug-валидируемые.
  `/cross-audit` ловит расхождения через рой агентов, не grep.
- **Метрика — best-effort таргет, не гарантия.** Гарантируем доставку
  проекта по scope; на метрику целимся совместно с бизнесом.
- **Дизайн-облик — из craft-экспертизы библиотеки**, не из головы агента.
- **Продуктовая и бизнес-проблемная экспертиза — из ответов бизнеса**,
  не из головы агента.
- **Коммит / push — гейт человека.** Без явной просьбы агент не коммитит.
