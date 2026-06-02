# Углы проверки cross-audit

Каждый lens — отдельный угол семантической проверки. Один lens = один
агент (для project-скоупленного — один агент на пару `проект × lens`).
Запускаются параллельно.

`<slug>` = `<project-slug>` — подставляется на спавне. Пути с `<slug>`
указывают на папку конкретного проекта `docs/projects/<slug>/`.

Структура каждого пункта:

- **Source / Destination** — какие слои читать (с `<slug>` где project-скоуп).
- **Скоуп** — `один раз` (верхнеуровневый, без проекта) или
  `по проекту` (раскрывается в пары `проект × lens`).
- **Применим если** — какие слои/каталоги должны существовать.
- **Что искать** — конкретные семантические паттерны.
- **Промпт для агента** — добавка к каркасу из SKILL.md.

## Скоуп углов

- **Верхнеуровневые, прогон один раз** (общие слои business ↔
  business-problem, без проекта): `factor-business`,
  `currentmetric-metric`.
- **Верхнеуровневый M:N, прогон один раз над всеми проектами**:
  `addresses-problem-frame`.
- **По каждому проекту** (общий слой business-problem ↔ продукт проекта;
  скоупится к проблемам, которые проект закрывает через
  `vision.addresses-problem`): `goal-vision`, `subject-persona`,
  `segment-persona`, `bet-capability`.
- **По каждому проекту** (внутри папки проекта): `persona-who`,
  `capability-situation`, `capability-domain`, `surface-zone`,
  `surface-screen`, `integration-domain`, `constraint-surface`,
  `market-capability`.

## factor-business

**Source:** `docs/business-problem/factor.md`.
**Destination:** `docs/business/` (`profile.md`, `competitor.md`,
`current-metric.md`).
**Скоуп:** один раз (общие слои, без проекта).
**Применим если:** оба слоя существуют.

**Что искать:**
- `warning`: SWOT-фактор, не опирающийся на картину бизнеса (сила/слабость
  без подтверждения в profile; тренд/угроза без следа в competitor/рынке).
- `hint`: заметный факт бизнеса (сильный конкурент, проседающий KPI), не
  отражённый ни в одном факторе.

**Промпт-добавка:**
```
factor (SWOT) должен опираться на реальную картину бизнеса. Для каждого
фактора: подтверждается ли он в business.profile/competitor? Для заметных
фактов бизнеса: есть ли соответствующий фактор? Сила/слабость — про
устройство бизнеса; тренд/угроза — про рынок (ищи в competitor).
```

## currentmetric-metric

**Source:** `docs/business/current-metric.md`.
**Destination:** `docs/business-problem/metric.md`.
**Скоуп:** один раз (общие слои, без проекта).
**Применим если:** оба наполнены.

**Что искать:**
- `warning`: целевая метрика, чей `current` (baseline) не соответствует ни
  одному текущему KPI бизнеса (baseline выдуман, а не взят из данных).
- `hint`: текущий KPI бизнеса, не ставший ни одной целевой метрикой
  (возможный кандидат в цель).

**Промпт-добавка:**
```
baseline целевой метрики (metric.current) должен браться из реального
текущего KPI бизнеса (business.current-metric), с датой и источником. Для
каждой целевой метрики: есть ли соответствующий current-metric? Сходятся
ли число, дата, источник?
```

## addresses-problem-frame

**Source:** `docs/projects/*/vision.md` (поле `addresses-problem` каждого
проекта, кроме `_canon`).
**Destination:** `docs/business-problem/frame.md` (таблица проблем).
**Скоуп:** один раз, **над всеми проектами** (M:N, обе стороны).
**Применим если:** есть хотя бы один проект и непустой `frame.md`.

**Что искать:**
- `error`: проект объявляет `addresses-problem` ref, который **не
  резолвится** ни в одну строку `frame` (проект бьёт в несуществующую
  проблему — опечатка slug или проблема не заведена).
- `hint`: строка `frame` (проблема), которую **не закрывает ни один
  проект** (висящая проблема — нужен проект, или она вне scope).
- `warning`: проект с **пустым** `addresses-problem` при наполненном
  vision (продукт без явной привязки к проблеме бизнеса).

**Промпт-добавка:**
```
Это единственный M:N-угол через много проектов. Прочитай
addresses-problem у КАЖДОГО docs/projects/<slug>/vision.md (исключи
_canon) и строки docs/business-problem/frame.md.

Связь slug-явная по форме, но проверяй СМЫСЛОВО, а не строкой: ref
проекта должен указывать на реально существующую проблему frame.

Прямая сторона: для каждого ref каждого проекта — есть ли такая строка
frame? Нет — error (укажи проект и нерезолвящийся ref).

Обратная сторона: для каждой строки frame — закрывает ли её хоть один
проект? Ни один — hint (проблема висит).

Проект с непустым vision, но пустым addresses-problem — warning.

Поле project в каждом finding ставь = slug проекта-источника (для
hint про висящую проблему — project: null).
```

## goal-vision

**Source:** `docs/business-problem/goal.md`, `metric.md` (только строки,
относящиеся к проблемам, которые закрывает проект).
**Destination:** `docs/projects/<slug>/vision.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют; у проекта непустой
`addresses-problem`.

**Что искать:**
- `error`: vision.Success не отражает ни одной целевой метрики проблем,
  которые проект закрывает (продукт не целит в свою задачу бизнеса).
- `error`: метрика подана в vision как **гарантия** (нарушение юр-рамки —
  метрика best-effort таргет).
- `warning`: цель закрываемой проблемы (goal) без отражения в
  vision.Problem/Success.

**Промпт-добавка:**
```
vision проекта <slug> должен решать проблемы, которые он закрывает
(см. список проблем проекта). Скоупь goal/metric к этим проблемам
через колонку `problem` — не тащи цели чужих проблем.

Отражает ли vision.Success целевые метрики его проблем
(business-problem.metric)? ВАЖНО: метрика — best-effort таргет, НЕ
гарантия; если в vision она подана как обещание результата — error.
Каждая цель (goal) закрываемой проблемы должна просматриваться в vision.
```

## subject-persona

**Source:** `docs/business-problem/subject.md` (только субъекты проблем,
которые закрывает проект).
**Destination:** `docs/projects/<slug>/persona.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют; у проекта непустой
`addresses-problem`.

**Что искать:**
- `error`: субъект влияния (positive) проблемы, которую закрывает проект,
  не ставший ни одной persona продукта (на чьё поведение целимся — но
  продукт не для него).
- `warning`: мотивация субъекта (боли/желания) не отражена в
  persona.jobs/pains.

**Промпт-добавка:**
```
subject — тот, чьё поведение двигает метрику; persona — адресат боли
продукта <slug>. Скоупь субъекты к проблемам этого проекта (колонка
`problem`).

Положительный субъект обычно становится persona. Для каждого positive-
субъекта закрываемой проблемы: есть ли соответствующая persona в
docs/projects/<slug>/persona.md? Перенесена ли его мотивация в
jobs/pains? Негативный субъект persona не требует.
```

## segment-persona

**Source:** `docs/business/segment.md`.
**Destination:** `docs/projects/<slug>/persona.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют.

**Что искать:**
- `hint`: сегмент бизнеса без соответствующей persona в этом проекте
  (продукт не обслуживает часть клиентов бизнеса — намеренно или
  пропуск?).
- `hint`: persona проекта, не сводимая ни к сегменту бизнеса, ни к
  субъекту (откуда она?).

**Промпт-добавка:**
```
segment — клиент бизнеса заказчика (общий слой); persona — пользователь
продукта <slug>. Это РАЗНЫЕ сущности, но связанные: продукт часто
делается для части клиентов бизнеса.

Сегмент без persona в этом проекте и persona без сегмента/субъекта —
hint, не error (один проект может намеренно сужать охват сегментов; их
закрывает другой проект).
```

## bet-capability

**Source:** `docs/business-problem/bet.md`, `goal.md` (только ставки/цели
проблем, которые закрывает проект).
**Destination:** `docs/projects/<slug>/capability.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют; у проекта непустой
`addresses-problem`.

**Что искать:**
- `warning`: ставка/цель (доведённая до карты) проблемы, которую
  закрывает проект, не реализуемая ни одной capability этого продукта
  (стратегия без продуктового воплощения).
- `hint`: capability проекта без связи с какой-либо ставкой/целью его
  проблем (продукт умеет то, что не служит закрываемой проблеме).

**Промпт-добавка:**
```
bet/goal — стратегический шаг; capability — что продукт <slug> умеет.
Скоупь ставки/цели к проблемам этого проекта (колонка `problem`).

ВАЖНО: ставку/цель проблемы могут реализовывать РАЗНЫЕ проекты — её
воплощение в capability ищи в ЭТОМ проекте; отсутствие здесь не error,
а warning (возможно, её несёт соседний проект, закрывающий ту же
проблему). Для каждой capability проекта: какой ставке/цели его проблем
она служит? Не служит ни одной — hint.
```

## persona-who

**Source:** `docs/projects/<slug>/persona.md`.
**Destination:** `docs/projects/<slug>/interface/who.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют в папке проекта.

**Что искать:**

- `error`: persona, под которую в `who.md` **нет ни одной роли**,
  семантически соответствующей. Не slug — смысл («persona:nurse-partner»
  → ищем who, выполняющую действия медсестры партнёрской клиники).
- `error`: who, который не соответствует **ни одной** persona проекта
  (включая системных акторов в who.md — они допустимы как «намеренное
  исключение», но всё равно должны иметь связь с интересами какой-то
  persona).
- `warning`: persona, под которую who покрывает только **часть**
  jobs-to-be-done. Если у persona 3 jobs, а who участвует только в
  одном — это намёк, что нужны ещё роли.

**Промпт-добавка:**

```
Сопоставь persona и who проекта <slug> семантически — оба слоя живут в
docs/projects/<slug>/. Persona — это "кто адресат боли продукта". Who —
"роль, выполняющая шаг бизнес-процесса". Связь не структурная: одна
persona может развернуться в несколько who (например, persona "медсестра
партнёрской клиники" → who: nurse-partner, nurse-partner-senior).

Для каждой persona: какие who её "несут" (выполняют её jobs)? Если ни
одного — error.

Для каждого who: какой persona он принадлежит? Системные акторы (scheduler,
external-svc) — допустимо без persona, но обоснуй почему именно этот
системный интерес.

Используй persona.jobs / pains / context и who.description / соседние
situation.action для сопоставления.
```

## capability-situation

**Source:** `docs/projects/<slug>/capability.md`.
**Destination:** `docs/projects/<slug>/interface/situation.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют в папке проекта.

**Что искать:**

- `error`: capability `stable`, под которую в interface проекта **нет ни
  одной ситуации**, реализующей действие. Capability — это «что продукт
  умеет», situation — конкретное UX-проявление этого умения.
- `warning`: capability имеет один-два, в то время как ожидается
  больше (capability сложная, например «согласовать слот» — обычно
  это 3-5 ситуаций).
- `hint`: ситуация в interface, у которой нет ясной capability-якоря
  в project проекта. Возможно, нужна capability, либо ситуация не нужна.

**Промпт-добавка:**

```
Оба слоя — внутри docs/projects/<slug>/. Capability — устойчивое умение
продукта в языке persona. Situation — конкретная UX-точка, где это
умение реализуется (кто/когда/что/ради чего/с какими данными).

Для каждой capability: какие situation её реализуют? Сопоставь по
смыслу действий и goal.

Для каждой situation: к какой capability она относится? Если ни к
одной — hint (либо новая capability, либо ситуация не нужна).
```

## capability-domain

**Source:** `docs/projects/<slug>/capability.md`.
**Destination:** `docs/projects/<slug>/domains/` (если есть).
**Скоуп:** по проекту.
**Применим если:** `docs/projects/<slug>/domains/` существует.

**Что искать:**

- `error`: capability `stable`, под которую в `domains/` проекта нет
  бизнес-домена / агрегата. Capability не существует в коде.
- `warning`: domain в `domains/` проекта, у которого не находится
  capability-якорь в project. Возможно, технический домен (auth,
  logging) — это норма; но если бизнес-домен (referrals, billing) —
  это пробел.

**Промпт-добавка:**

```
Оба слоя — внутри docs/projects/<slug>/. Capability — продуктовое умение.
Domain в docs/projects/<slug>/domains/ — бизнес-код, несущий это умение.

Для каждой capability: есть ли в domains/ проекта агрегат или сервис,
реализующий бизнес-логику? Сопоставь по семантике, не имени файла.

Технические домены (auth, audit, logging) могут не иметь
capability-якоря — отметь, но не помечай ошибкой.
```

## surface-zone

**Source:** `docs/projects/<slug>/surface.md`.
**Destination:** `docs/projects/<slug>/interface/zone.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют в папке проекта.

**Что искать:**

- `error`: surface `stable`, у которой нет **ни одной** зоны в
  interface проекта, принадлежащей этой поверхности (по смыслу).
- `error`: zone в interface проекта, не привязанная ни к одной surface
  (zone «висит в воздухе»).
- `warning`: zone, которая по смыслу принадлежит сразу нескольким
  surface (например, общая навигация для web и mobile). Это норма, но
  важно явно зафиксировать.

**Промпт-добавка:**

```
Оба слоя — внутри docs/projects/<slug>/. Surface — поверхность продукта
(web/mobile/api/admin/bot/...). Zone — зона интерфейса (логический
контейнер блоков).

Для каждой surface: какие zone в неё попадают? Связь семантическая —
смотри на surface.type, surface.lives-at, и zone.description /
parent-zone.

Для каждой zone: какой surface она принадлежит? Если ни одной —
error.
```

## surface-screen

**Source:** `docs/projects/<slug>/surface.md`.
**Destination:** `docs/projects/<slug>/screens/` (если есть).
**Скоуп:** по проекту.
**Применим если:** `docs/projects/<slug>/screens/` существует.

**Что искать:**

- `error`: surface `stable`, у которой нет ни одного screen или flow
  в `screens/` проекта.
- `warning`: screen / flow в `screens/` проекта, не привязанный к
  surface этого проекта (по смыслу).

**Промпт-добавка:**

```
Оба слоя — внутри docs/projects/<slug>/. Surface — где продукт работает.
Screen / flow в docs/projects/<slug>/screens/ — композиция UX, ассеты,
hi-fi-материал.

Для каждой surface: есть ли в screens/ проекта хотя бы один артефакт
этой поверхности? По смыслу — посмотри shell/flow/screen-описания.
```

## integration-domain

**Source:** `docs/projects/<slug>/integration.md`.
**Destination:** `docs/projects/<slug>/domains/` (если есть).
**Скоуп:** по проекту.
**Применим если:** `docs/projects/<slug>/domains/` существует.

**Что искать:**

- `error`: integration `stable`, под которую в `domains/` проекта нет
  адаптера / клиента.
- `warning`: адаптер в `domains/` проекта, у которого нет integration в
  project (возможно, технический адаптер — http-клиент, redis-клиент
  — это норма; бизнес-адаптер без integration — пробел).

**Промпт-добавка:**

```
Оба слоя — внутри docs/projects/<slug>/. Integration — внешняя система,
с которой обмениваемся. Domain в docs/projects/<slug>/domains/ может
содержать адаптер для интеграции.

Для каждой integration: есть ли адаптер / клиент в domains/ проекта?
Сопоставь по семантике.

Технические адаптеры (http-client, db-client) могут не иметь
integration-якоря — отметь, не error.
```

## constraint-surface

**Source:** `docs/projects/<slug>/constraint.md`.
**Destination:** `docs/projects/<slug>/surface.md`,
`docs/projects/<slug>/integration.md`.
**Скоуп:** по проекту (cross-внутри-project).
**Применим если:** product-слой проекта существует.

**Что искать:**

- `warning`: constraint, который семантически касается surface или
  integration, но эта связь нигде не упомянута (в `description`
  constraint, surface или integration). Например, constraint
  `pdn-consent` (152-ФЗ) должен быть связан с web-поверхностью, где
  есть PII.
- `hint`: surface с persona, обрабатывающая PII / финансы / здоровье,
  но без constraint. Возможно, пропустили.

**Промпт-добавка:**

```
Все три файла — внутри одного docs/projects/<slug>/. Constraint —
обязательное правило (закон / SLA / контракт). Обычно constraint
касается surface (где это применимо) или integration (с чем
обмениваемся под этим правилом).

Для каждого constraint: какая surface или integration его несёт? Найди
в description упоминания или сопоставь по смыслу (152-ФЗ → surface с
PII; PCI-DSS → integration с платежами; HIPAA → surface с
медданными).

Если связь не видна нигде — warning.

Дополнительно: surface, обрабатывающая PII / финансы / здоровье, без
относящегося constraint — hint.
```

## market-capability

**Source:** `docs/projects/<slug>/market.md`.
**Destination:** `docs/projects/<slug>/capability.md`.
**Скоуп:** по проекту.
**Применим если:** оба наполнены в папке проекта.

**Что искать:**

- `hint`: market-аналог покрывает capability, которой у нас **нет**.
  Это сигнал: либо нам нужна эта capability, либо явно decide, что
  это вне scope.
- `hint`: market-аналог не покрывает наши capabilities (мы делаем то,
  чего конкурент не умеет). Полезно для позиционирования.
- `warning`: market.description упоминает «direct competitor», но
  пересечение capabilities — почти полное. Возможно, недо-дифференциация.

**Промпт-добавка:**

```
Оба слоя — внутри docs/projects/<slug>/. Market — рыночные аналоги
этого продукта. Capability — умения этого продукта.

Для каждого market-аналога: что он покрывает из наших capabilities?
Что у него есть, чего у нас нет (гэп для нас)? Что у нас есть, чего у
него нет (наша дифференциация)?

Возвращай как findings hints / warnings — это материал для аналитика,
не error.
```

## Порядок lens-ов

Все агенты спавнятся в одном message-блоке параллельно — порядок ниже
лишь логический (как раскладывать findings в отчёте), не очередь
исполнения.

**Верхнеуровневые (прогон один раз):**

1. `factor-business` (бизнес → проблема)
2. `currentmetric-metric` (бизнес → проблема)
3. `addresses-problem-frame` (продукты ↔ проблемы, M:N над всеми
   проектами)

**По каждому проекту** (для каждого `<slug>` из `docs/projects/`, кроме
`_canon`; раскрывается в пары `проект × lens`):

4. `goal-vision` (проблема → продукт; скоуп к проблемам проекта)
5. `subject-persona` (проблема → продукт; скоуп к проблемам проекта)
6. `segment-persona` (бизнес → продукт)
7. `bet-capability` (проблема → продукт; скоуп к проблемам проекта)
8. `persona-who` (foundation, продукт → interface проекта)
9. `surface-zone` (foundation)
10. `capability-situation` (foundation)
11. `capability-domain` (если у проекта есть `domains/`)
12. `integration-domain` (если у проекта есть `domains/`)
13. `surface-screen` (если у проекта есть `screens/`)
14. `constraint-surface` (cross-внутри-project)
15. `market-capability` (часто даёт hints, не error)

Полный рой = `3 верхнеуровневых + Σ по проектам (применимые
project-углы)`.

`--quick` запускает по каждому проекту три foundation-угла
продукт↔interface (`persona-who`, `capability-situation`, `surface-zone`)
плюс `addresses-problem-frame` один раз. Для верхних слоёв —
`goal-vision`, `subject-persona` (по проекту) как быстрый upstream-чек.
