# Getting started — от шаблона к docs-репо проекта

**[META]** Этот файл — для потребителя шаблона. Описывает путь от форка до
docs-репо проекта, который ничего не помнит про шаблон. Удаляется на шаге
де-темплейтизации (`/de-template`).

Принцип: **аналитика первична.** Рекомендуемый вход — оркестратор `/entrypoint`
(аналитик) или `/entrypoint-for-business` (клиент): принимает сырьё любого объёма,
классифицирует по слоям и маршрутизирует к рою deep-dive-исполнителей (прямой
вызов исполнителя тоже допустим). Семантический поток сверху вниз: бизнес
заказчика (+ реестр проблем) → сегменты и граф работ → SWOT → Карта гипотез →
продукты → интерфейс / домены / экраны. Артефакты `docs/` — design-time source of
truth для соседних форков (`<org>/{backend,frontend,infra}`).

## 0. Форк

1. Gitea (`https://git.sftbmb.ru`) → `sftbmb-core/project-docs-template` →
   **Use this template** → `<org>/docs`.
2. `git clone git@git.sftbmb.ru:<org>/docs.git && cd docs`.
3. Форкается **первым** в экосистеме: backend/frontend/infra-форки читают
   `<org>/docs` как upstream-аналитику (`docs/README.md § Что docs отдаёт
   соседям`).

## Путь

```
0. Use this template → <org>/docs → клон
   Вход: /entrypoint (аналитик) · /entrypoint-for-business (клиент) — приносишь
   сырьё, оркестратор маршрутизирует. Прямой вызов исполнителей ниже тоже допустим.
1. Бизнес заказчика → /business-deep-dive (профиль + реестр проблем business-problem)
                      ИЛИ /business-deep-dive-for-business («домашнее задание» заказчику)
2. Сегменты и работы → /segment-deep-dive (сегменты по работам + Score, рой)
                      ИЛИ /segment-deep-dive-for-business
   ├─ /job-graph-deep-dive <segment> (граф работ, решения, трения)
   │  ИЛИ /job-graph-deep-dive-for-business
   ├─ /jtbd-interview (опц.: рекрут → скрипт → интервью → конспект)
   └─ /ajtbd-audit — инварианты графа работ (рой)
3. SWOT и Карта гипотез
   ├─ /swot-deep-dive (факторы → ставки)            → /swot-audit
   └─ /hypothesis-map-deep-dive (цель → метрика → субъект → гипотеза) → /hypothesis-map-audit
4. Продукты         → /project-deep-dive <slug> (vision + 7 kind)
                      ИЛИ /project-deep-dive-for-business
   ├─ /project-audit <slug>
   ├─ /interface-deep-dive <slug>  → /interface-audit <slug>
   ├─ /domain-deep-dive <slug> <ctx> (опц., DDD)
   └─ /screen-deep-dive <slug>      → /screen-audit <slug>
5. /cross-audit — сквозная семантика между слоями (рой)
6. /de-template — вычистить показной example/ и шаблон-нарратив
7. готовый docs-репо проекта
```

Это не жёсткая лестница: информация приходит не линейно, оркестратор ведёт по
слоям в нужном порядке. Семантический поток зависимостей и рой исполнителей — в
корневом `README.md § Воркфлоу`. SWOT и Карту гипотез в клиент-режиме ведёт сам
`/entrypoint-for-business` (отдельных `*-for-business`-скиллов для них нет).

## 1. Бизнес заказчика — `docs/business/`

Самая верхняя точка. Без профиля бизнеса проблемы и продукты висят в воздухе.

- **`/business-deep-dive`** (аналитик) — приём материалов клиента (сайт, PDF,
  презентации, соцсети, интервью) + рой web-research рынка и конкурентов;
  ведёт через фазы intake → profile → market → structure → metrics → problems →
  cohesion, заполняет `docs/business/{profile,offering,channel,competitor,current-metric,material,business-problem}.md`
  (включая реестр проблем бизнеса — граница гарантии scope и best-effort таргета).
- **`/business-deep-dive-for-business`** — режим «домашнее задание» для самого
  заказчика/основателя: мягкий рассказ о своём бизнесе в бизнес-языке (без
  slug/kind), упаковка результата в единую ветку `client` для передачи
  аналитику.

## 2. Сегменты и граф работ — `docs/ajtbd/`

Разведка по методологии Advanced JTBD: кто наш сегмент **по работам**, а не по
демографии, его граф работ и где он трётся с текущими решениями. 5 kind:
`segment` · `job` · `job-graph` · `solution` · `segment-problem`. Слой питает
проблемы бизнеса (трения доказывают проблему) и продукты (механики ценности →
возможности).

- **`/segment-deep-dive`** (аналитик) / **`/segment-deep-dive-for-business`** —
  поиск, кластеризация и скоринг сегментов (Score = важность × частотность ×
  размер × (10 − удовлетворённость)) через многоволновой рой web-research.
- **`/job-graph-deep-dive <segment>`** / **`-for-business`** — граф работ
  выбранного сегмента: целевая работа вверх/вниз/по последовательности, нанятые
  решения, трения, CPR и кандидаты-механики ценности.
- **`/jtbd-interview`** — опц. тяжёлый процесс живых JTBD-интервью (рекрут →
  скрипт → проведение → конспект), своё state/transcripts; выход разбирается
  через intake в скилы выше. Запускается по явному запросу.
- **`/ajtbd-audit`** — рой агентов проверяет инварианты графа работ по каждому
  сегменту. Только отчёт.

## 3. SWOT и Карта гипотез — `docs/swot/` · `docs/hypothesis-map/`

Реестр проблем бизнеса (`business-problem` в `docs/business/`) разворачивается в
два строгих многопроблемных слоя: каждая запись несёт массив `problem` (M:N к
строкам реестра).

- **`/swot-deep-dive`** (аналитик, `docs/swot/`) — из сильных/слабых сторон и
  трендов/угроз бизнеса (`factor`) рождаются стратегические ставки (`bet`),
  доводимые (`promoted-to`) до цели или гипотезы Карты гипотез.
- **`/swot-audit`** — рой агентов проверяет инварианты LinkedSWOT по каждой
  проблеме (баланс факторов, ставка-висяк, фактор без ставки, …).
- **`/hypothesis-map-deep-dive`** (аналитик, `docs/hypothesis-map/`) — причинная
  цепь цель → измеримая метрика → субъект → гипотеза → задача проверки. Ядро —
  метрика как **best-effort таргет** (не гарантия) с baseline, источником истины,
  атрибуцией и критерием приёмки.
- **`/hypothesis-map-audit`** — рой агентов проверяет инварианты Карты гипотез по
  каждой проблеме (задача-сирота, «тогда» без метрики, метрика без влияния,
  целевая без guardrail, …). Только отчёт, не правит.

В клиент-режиме SWOT и Карту гипотез ведёт сам `/entrypoint-for-business`
(отдельных `*-for-business`-скиллов для них нет).

## 4. Продукты — `docs/projects/<slug>/`

Корень решения: несколько продуктов под одним бизнесом, у каждого своя папка.
Все скиллы слоёв принимают `<project-slug>` первым аргументом (без него —
пикер по `docs/projects/`, исключая `_canon`).

- **`/project-deep-dive <slug>`** (аналитик) / **`/project-deep-dive-for-business`**
  — vision (+ `addresses-problem` M:N к проблемам) + 7 kind продукта
  (user / capability / boundary / surface / integration / constraint / market).
  Новый проект заводит сам скилл (копирует форму из `_canon/project/`).
- **`/project-audit <slug>`** — узкий аудит внутри продуктового слоя.
- **`/interface-deep-dive <slug>`** → **`/interface-audit <slug>`** — UX-слой
  (who / stage / situation / zone / block / ux-substrate / data-items).
- **`/domain-deep-dive <slug> <ctx>`** — (опц.) DDD-артефакты бэкенда продукта.
  Завершается на stable-артефакте; Go-код по ним разворачивает соседний
  `<org>/backend`, не этот репо.
- **`/screen-deep-dive <slug>`** → **`/screen-audit <slug>`** — композиция и
  облик (flow / screen / block / shell) на инвентаре `@sftbmb/ui`.

Каждый deep-dive ведёт сессию через `AskUserQuestion`, держит память в
`.claude/skills/<имя>/state/`, не выдумывает домен/craft, не повышает
`draft → stable` без явного подтверждения.

## 5. Сквозной аудит — `/cross-audit`

В конце или после крупных изменений. Рой агентов проверяет семантику между
слоями: business ↔ ajtbd ↔ swot ↔ hypothesis-map ↔ (по каждому проекту: project ↔
interface ↔ domain ↔ screen). Не slug-валидация — смысловая проверка («пользователь
без UX-покрытия», «сегмент без пользователя», «проблема бизнеса без единого
трения-доказательства», «проблема, которую не закрывает ни один проект»,
«метрика как гарантия»). Только отчёт; деструктивные правки — через
соответствующий deep-dive.

## 6. `/de-template` — свой docs-репо

Когда аналитика проекта заполнена, `/de-template` превращает форк в docs-репо
проекта, не помнящий про шаблон: удаляет показной `docs/projects/example/`
(чужой продукт-витрина), переписывает шаблон-нарратив в `CLAUDE.md`/`README.md`
под идентичность проекта. **НЕ трогает** пустые скелеты-каноны
(`docs/projects/_canon/`, `docs/business/`, `docs/ajtbd/`, `docs/swot/`,
`docs/hypothesis-map/`) — это рабочая основа, не показуха. Движок
skill-only, reviewable edits.

## Готово

Репо больше ничего не помнит про шаблон: свой бизнес, свои проблемы, свои
продукты, без `example/`. Дальше — обычный аналитический флоу по воркфлоу
(`README.md`), под git-ревью. Соседние форки `<org>/{backend,frontend,infra}`
читают stable-артефакты этого репо как upstream (`docs/README.md`).

## Когда что-то идёт не так

- **Артефакт не `stable`** → доведи через соответствующий deep-dive того же слоя.
- **Подозрение на рассинхрон внутри слоя** → узкий аудит
  (`/project-audit`, `/interface-audit`, `/screen-audit`, `/swot-audit`,
  `/hypothesis-map-audit`, `/ajtbd-audit`).
- **Подозрение на разрыв между слоями** → `/cross-audit`.
- **Заказчик ведёт сессию сам** → `*-for-business`-вариант скилла (бизнес-язык,
  эскалация «нужен аналитик», push в единую ветку `client`).
