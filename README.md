# ST IT — шаблон проекта дизайна

Шаблон, который импортируется **под бизнес**. Аналитик начинает с бизнеса
заказчика в `docs/business/`, формализует его проблемы по методологии
(SWOT + Карта гипотез) в `docs/business-problem/` — слой
**многопроблемный**, под проблемы заводит **продукты** в
`docs/projects/<slug>/` (несколько проектов под одним бизнесом). У каждого
продукта свои интерфейс (`interface/`), композиция (`screens/`) и
опционально домены (`domains/`), вложенные в его папку. По `screens/`
автор макета **вручную** собирает wireframe и hi-fi субстрат на библиотеке
`@stit-design/ui`.

Поток: **бизнес (profile/segment/competitor/...) → бизнес-проблемы
(`frame`-таблица; SWOT factor/bet → goal/metric/subject/hypothesis/task,
каждая запись несёт `problem`, M:N) → продукты (`projects/<slug>/`:
vision + addresses-problem / persona / capability /...) → интерфейс
(who/situation/zone/...) → экраны (flow/screen/block/shell) → wireframe →
hi-fi субстрат.** Артефакты — чистая аналитика и на код напрямую не
мапятся; превращение в код — ручная работа автора макета, не отдельный
артефакт.

Юр-рамка: гарантируем доставку проекта по scope; метрики
`docs/business-problem/` — best-effort таргет (совместно с бизнесом),
не гарантия исхода.

## Два репозитория

| Репо | Что | Роль |
|---|---|---|
| **этот** | артефакты аналитики продуктов, интерфейса и экранов, воркфлоу скилов | проектный шаблон |
| **`@stit-design/ui`** (репо `ui-lib`) | библиотека компонентов + галерея | потребляется как зависимость из Gitea registry |

Граница чистая: библиотека строится один раз и версионируется; проект
её **потребляет**, не правит.

## Структура

```
docs/business/    профиль бизнеса заказчика — верх, один бизнес (см. docs/business/README.md):
  profile.md        singleton: Бизнес / Модель / Позиционирование / Контекст
  segment.md        кого обслуживает бизнес
  offering.md       что продаёт
  channel.md        каналы привлечения/продажи/доставки
  competitor.md     рынок (наполняет рой web-research)
  current-metric.md текущие KPI — baseline-кандидаты
  material.md       реестр источников (сайт/PDF/презентация/соцсети)
docs/business-problem/  формализация проблем — многопроблемный (см. docs/business-problem/README.md):
  frame.md          ТАБЛИЦА проблем (строка = проблема: problem/guarantee/target/out-of-control/scope)
  factor.md         SWOT-фактор (+ problem[], area: strength|weakness|trend|threat)
  bet.md            стратегическая ставка (+ problem[])
  goal.md           цель карты гипотез без цифр (+ problem[])
  metric.md         метрика-таргет (+ problem[]; current/target/source/attribution/acceptance)
  subject.md        субъект влияния (+ problem[]; мотивация, негативный)
  hypothesis.md     гипотеза (+ problem[]; если·то·потому что·тогда→metric)
  task.md           задача проверки гипотезы (+ problem[])
docs/projects/    продукты под бизнес (см. docs/projects/README.md):
  _canon/           КАНОН формы (образец, не данные проекта):
    project/          канон продукта (vision + 7 kind)
    interface/        канон UX (who/stage/situation/zone/block/ux-substrate/data-items)
    screens/          канон экранов (flow/screen/block/shell)
    domains/          канон DDD (_templates/, _shared/)
  <slug>/           ДАННЫЕ одного продукта:
    vision.md         singleton: Problem / Success / Non-goals + addresses-problem (M:N → frame)
    persona.md … market.md   7 kind продукта (persona/capability/boundary/surface/integration/constraint/market)
    interface/        who/stage/situation/zone/block/ux-substrate/data-items
    domains/          (опц.) <ctx>/ контексты по DDD-канону
    screens/          flows/ screens/ blocks/ shells/ + assets/
  example/          образцовый проект (витрина артефактов)
.claude/
  skills/
    business-deep-dive              — профиль бизнеса: приём материалов + рой web-research
    business-deep-dive-for-business — клиент-режим профиля бизнеса
    business-problem-deep-dive      — SWOT + Карта гипотез по каждой проблеме, ядро — метрики
    business-problem-deep-dive-for-business — клиент-режим проблем (бизнес-язык)
    business-problem-audit          — семантические инварианты методологии по каждой проблеме (рой)
    project-deep-dive               — продукт: <project-slug> аргументом или пикер/новый проект
    project-deep-dive-for-business  — клиент-режим: дружелюбный пикер продукта, эскалация, push в client/<ts>
    project-audit                   — внутрипроектная консистентность одного продукта
    interface-deep-dive · interface-audit   — <project-slug> аргументом или пикер
    domain-deep-dive                — DDD-артефакты бэкенда продукта
    screen-deep-dive · screen-audit         — <project-slug> аргументом или пикер
    cross-audit                     — сквозная семантика business ↔ business-problem ↔ (по каждому проекту: project ↔ interface ↔ domain ↔ screen)
  rules/
    forward-only
```

## Воркфлоу

Начинаем с бизнеса заказчика — без него проблемы и продукты висят в
воздухе. Слои project / interface / domain / screen — **по проекту**:
скилл принимает `<project-slug>` (без него — пикер по `docs/projects/`).
Сквозной аудит — в конце, или после крупных изменений.

```
1. /business-deep-dive                — профиль бизнеса (один бизнес): приём
   ИЛИ /business-deep-dive-for-business  материалов клиента + рой web-research.
2. /business-problem-deep-dive        — SWOT (factor/bet) → Карта гипотез (goal/
   ИЛИ /business-problem-deep-dive-for-business  metric/subject/hypothesis/task)
                                        по каждой проблеме (frame — таблица).
                                        Ядро — метрики (best-effort таргет).
3. /business-problem-audit            — инварианты методологии по каждой проблеме (рой).
4. /project-deep-dive <slug>          — продукт: vision (+ addresses-problem) /
   ИЛИ /project-deep-dive-for-business   persona / capability из business-problem.
                                        Без <slug> — пикер / заведение нового проекта.
5. /project-audit <slug>              — узкий аудит внутри продукта.
6. /interface-deep-dive <slug>        — UX-сущности (who/situation/zone) из якорей
                                        persona / capability / surface проекта.
7. /interface-audit <slug>            — консистентность interface проекта.
8. /domain-deep-dive <slug> <ctx>     — (опц.) бизнес-домены бэкенда; контекст и
                                        use-case цепляются к capability проекта,
                                        адаптеры — к integration проекта.
9. /screen-deep-dive <slug>           — flows/screens/blocks/shells из interface +
                                        surface проекта как scope.
10. /screen-audit <slug>              — консистентность screens проекта.
11. /cross-audit                      — сквозной семантический аудит business ↔
                                        business-problem ↔ (по каждому проекту:
                                        project ↔ interface ↔ domain ↔ screen) (рой).
```

Каждый deep-dive ведёт сессию через `AskUserQuestion`, держит state в
`.claude/skills/<имя>/state/` (слои продукта — с разбивкой по
`<project-slug>`), не выдумывает домен, не повышает `draft → stable` без
явного подтверждения.

## Инварианты

- **Forward-only** — только «что есть и куда идём», без журналов прошлого.
- **Артефакты — source of truth**, всё остальное собирается по ним.
  Бизнес — верх; проблемы — многопроблемный слой; продукты — корни
  решений (несколько под одним бизнесом); всё растёт сверху вниз.
- **Канон формы продуктовых слоёв — один раз в `docs/projects/_canon/`**,
  данные — в папках проектов; канон не дублируется в проект.
- **Связи между слоями семантические**, не slug-валидируемые. Проблема ↔
  продукт — M:N (`vision.addresses-problem`). `/cross-audit` ловит
  расхождения через рой агентов (по каждому проекту), не grep.
- **Метрика — best-effort таргет, не гарантия.** Гарантируем доставку
  проекта по scope; на метрику целимся совместно с бизнесом.
- **Дизайн-облик — из craft-экспертизы библиотеки**, не из головы агента.
- **Продуктовая и бизнес-проблемная экспертиза — из ответов бизнеса**,
  не из головы агента.
- **Коммит / push — гейт человека.** Без явной просьбы агент не коммитит.
