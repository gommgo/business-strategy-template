# Getting started — от шаблона к docs-репо проекта

**[META]** Этот файл — для потребителя шаблона. Описывает путь от форка до
docs-репо проекта, который ничего не помнит про шаблон. Удаляется на шаге
де-темплейтизации (`/de-template`).

Принцип: **аналитика первична.** Здесь нет кода и нет оркестратора-онбординга —
онбординг ведёт **аналитик руками** через рой deep-dive-скиллов, сверху вниз:
бизнес заказчика → его проблемы → продукты → интерфейс / домены / экраны.
Артефакты `docs/` — design-time source of truth для соседних форков
(`<org>/{backend,frontend,infra}`).

## 0. Форк

1. Gitea (`https://git.stit.tech`) → `stit-template/project-docs-template` →
   **Use this template** → `<org>/docs`.
2. `git clone git@git.stit.tech:<org>/docs.git && cd docs`.
3. Форкается **первым** в экосистеме: backend/frontend/infra-форки читают
   `<org>/docs` как upstream-аналитику (`docs/README.md § Что docs отдаёт
   соседям`).

## Путь

```
0. Use this template → <org>/docs → клон
1. Бизнес заказчика → /business-deep-dive (аналитик)
                      ИЛИ /business-deep-dive-for-business («домашнее задание» заказчику)
2. Бизнес-проблемы  → /business-problem-deep-dive (SWOT + Карта гипотез)
                      ИЛИ /business-problem-deep-dive-for-business
   └─ /business-problem-audit — инварианты методологии (рой)
3. Продукты         → /project-deep-dive <slug> (vision + 7 kind)
                      ИЛИ /project-deep-dive-for-business
   ├─ /project-audit <slug>
   ├─ /interface-deep-dive <slug>  → /interface-audit <slug>
   ├─ /domain-deep-dive <slug> <ctx> (опц., DDD)
   └─ /screen-deep-dive <slug>      → /screen-audit <slug>
4. /cross-audit — сквозная семантика между слоями (рой)
5. /de-template — вычистить показной example/ и шаблон-нарратив
6. готовый docs-репо проекта
```

Полная лестница 11 шагов с порядком — в корневом `README.md § Воркфлоу`.

## 1. Бизнес заказчика — `docs/business/`

Самая верхняя точка. Без профиля бизнеса проблемы и продукты висят в воздухе.

- **`/business-deep-dive`** (аналитик) — приём материалов клиента (сайт, PDF,
  презентации, соцсети, интервью) + рой web-research рынка и конкурентов;
  ведёт через фазы intake → profile → market → structure → metrics → cohesion,
  заполняет `docs/business/{profile,segment,offering,channel,competitor,current-metric,material}.md`.
- **`/business-deep-dive-for-business`** — режим «домашнее задание» для самого
  заказчика/основателя: мягкий рассказ о своём бизнесе в бизнес-языке (без
  slug/kind), упаковка результата в единую ветку `client` для передачи
  аналитику.

## 2. Бизнес-проблемы — `docs/business-problem/`

Строгая методология LinkedSWOT + Карта гипотез. `frame` — таблица проблем
(одна строка = одна проблема). Слой **многопроблемный**: каждая запись 7 kind
несёт массив `problem` (M:N к строкам frame).

- **`/business-problem-deep-dive`** (аналитик) — от SWOT-факторов и ставок к
  цели, измеримой метрике, субъекту, гипотезе и задаче проверки. Ядро —
  метрика как **best-effort таргет** (не гарантия) с baseline, источником
  истины, атрибуцией и критерием приёмки.
- **`/business-problem-deep-dive-for-business`** — то же в бизнес-языке для
  заказчика.
- **`/business-problem-audit`** — рой агентов проверяет инварианты методологии
  по каждой проблеме (задача-сирота, «тогда» без метрики, метрика без влияния,
  ставка-висяк, …). Только отчёт, не правит.

## 3. Продукты — `docs/projects/<slug>/`

Корень решения: несколько продуктов под одним бизнесом, у каждого своя папка.
Все скиллы слоёв принимают `<project-slug>` первым аргументом (без него —
пикер по `docs/projects/`, исключая `_canon`).

- **`/project-deep-dive <slug>`** (аналитик) / **`/project-deep-dive-for-business`**
  — vision (+ `addresses-problem` M:N к проблемам) + 7 kind продукта
  (persona / capability / boundary / surface / integration / constraint / market).
  Новый проект заводит сам скилл (копирует форму из `_canon/project/`).
- **`/project-audit <slug>`** — узкий аудит внутри продуктового слоя.
- **`/interface-deep-dive <slug>`** → **`/interface-audit <slug>`** — UX-слой
  (who / stage / situation / zone / block / ux-substrate / data-items).
- **`/domain-deep-dive <slug> <ctx>`** — (опц.) DDD-артефакты бэкенда продукта.
  Завершается на stable-артефакте; Go-код по ним разворачивает соседний
  `<org>/backend`, не этот репо.
- **`/screen-deep-dive <slug>`** → **`/screen-audit <slug>`** — композиция и
  облик (flow / screen / block / shell) на инвентаре `@stit-design/ui`.

Каждый deep-dive ведёт сессию через `AskUserQuestion`, держит память в
`.claude/skills/<имя>/state/`, не выдумывает домен/craft, не повышает
`draft → stable` без явного подтверждения.

## 4. Сквозной аудит — `/cross-audit`

В конце или после крупных изменений. Рой агентов проверяет семантику между
слоями: business ↔ business-problem ↔ (по каждому проекту: project ↔ interface
↔ domain ↔ screen). Не slug-валидация — смысловая проверка («персона без
UX-покрытия», «проблема, которую не закрывает ни один проект», «метрика как
гарантия»). Только отчёт; деструктивные правки — через соответствующий
deep-dive.

## 5. `/de-template` — свой docs-репо

Когда аналитика проекта заполнена, `/de-template` превращает форк в docs-репо
проекта, не помнящий про шаблон: удаляет показной `docs/projects/example/`
(чужой продукт-витрина), переписывает шаблон-нарратив в `CLAUDE.md`/`README.md`
под идентичность проекта. **НЕ трогает** пустые скелеты-каноны
(`docs/projects/_canon/`, `docs/business/`, `docs/business-problem/`) — это
рабочая основа, не показуха. Движок skill-only, reviewable edits.

## Готово

Репо больше ничего не помнит про шаблон: свой бизнес, свои проблемы, свои
продукты, без `example/`. Дальше — обычный аналитический флоу по воркфлоу
(`README.md`), под git-ревью. Соседние форки `<org>/{backend,frontend,infra}`
читают stable-артефакты этого репо как upstream (`docs/README.md`).

## Когда что-то идёт не так

- **Артефакт не `stable`** → доведи через соответствующий deep-dive того же слоя.
- **Подозрение на рассинхрон внутри слоя** → узкий аудит
  (`/project-audit`, `/interface-audit`, `/screen-audit`, `/business-problem-audit`).
- **Подозрение на разрыв между слоями** → `/cross-audit`.
- **Заказчик ведёт сессию сам** → `*-for-business`-вариант скилла (бизнес-язык,
  эскалация «нужен аналитик», push в единую ветку `client`).
