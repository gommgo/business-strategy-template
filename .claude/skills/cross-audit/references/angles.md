# Углы проверки cross-audit

Каждый lens — отдельный угол семантической проверки. Один lens = один
агент. Запускаются параллельно.

Структура каждого пункта:

- **Source / Destination** — какие слои читать.
- **Применим если** — какие слои должны существовать.
- **Что искать** — конкретные семантические паттерны.
- **Промпт для агента** — добавка к каркасу из SKILL.md.

## factor-business

**Source:** `docs/business-problem/factor.md`.
**Destination:** `docs/business/` (`profile.md`, `competitor.md`,
`current-metric.md`).
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

## goal-vision

**Source:** `docs/business-problem/goal.md`, `metric.md`.
**Destination:** `docs/project/vision.md`.
**Применим если:** оба слоя существуют.

**Что искать:**
- `error`: vision.Success не отражает ни одной целевой метрики проблемы
  (продукт не целит в задачу бизнеса).
- `error`: метрика подана в vision как **гарантия** (нарушение юр-рамки —
  метрика best-effort таргет).
- `warning`: цель проблемы (goal) без отражения в vision.Problem/Success.

**Промпт-добавка:**
```
vision продукта должен решать сформулированную бизнес-проблему. Отражает
ли vision.Success целевые метрики (business-problem.metric)? ВАЖНО:
метрика — best-effort таргет, НЕ гарантия; если в vision она подана как
обещание результата — error. Каждая цель (goal) должна просматриваться в
vision.
```

## subject-persona

**Source:** `docs/business-problem/subject.md`.
**Destination:** `docs/project/persona.md`.
**Применим если:** оба слоя существуют.

**Что искать:**
- `error`: субъект влияния (positive), не ставший ни одной persona
  продукта (на чьё поведение целимся — но продукт не для него).
- `warning`: мотивация субъекта (боли/желания) не отражена в
  persona.jobs/pains.

**Промпт-добавка:**
```
subject — тот, чьё поведение двигает метрику; persona — адресат боли
продукта. Положительный субъект обычно становится persona. Для каждого
positive-субъекта: есть ли соответствующая persona? Перенесена ли его
мотивация в jobs/pains? Негативный субъект persona не требует.
```

## segment-persona

**Source:** `docs/business/segment.md`.
**Destination:** `docs/project/persona.md`.
**Применим если:** оба слоя существуют.

**Что искать:**
- `hint`: сегмент бизнеса без соответствующей persona (продукт не
  обслуживает часть клиентов бизнеса — намеренно или пропуск?).
- `hint`: persona, не сводимая ни к сегменту бизнеса, ни к субъекту
  (откуда она?).

**Промпт-добавка:**
```
segment — клиент бизнеса заказчика; persona — пользователь продукта. Это
РАЗНЫЕ сущности, но связанные: продукт часто делается для части клиентов
бизнеса. Сегмент без persona и persona без сегмента/субъекта — hint, не
error (продукт может намеренно сужать).
```

## bet-capability

**Source:** `docs/business-problem/bet.md`, `goal.md`.
**Destination:** `docs/project/capability.md`.
**Применим если:** оба слоя существуют.

**Что искать:**
- `warning`: ставка/цель (доведённая до карты), не реализуемая ни одной
  capability продукта (стратегия без продуктового воплощения).
- `hint`: capability без связи с какой-либо ставкой/целью (продукт умеет
  то, что не служит проблеме).

**Промпт-добавка:**
```
bet/goal — стратегический шаг; capability — что продукт умеет. Каждая
доведённая ставка/цель должна реализовываться хотя бы одной capability.
Для каждой capability: какой ставке/цели она служит? Не служит ни одной —
hint (возможно, лишняя для этой проблемы).
```

## persona-who

**Source:** `docs/project/persona.md`.
**Destination:** `docs/interface/who.md`.
**Применим если:** оба слоя существуют.

**Что искать:**

- `error`: persona, под которую в `who.md` **нет ни одной роли**,
  семантически соответствующей. Не slug — смысл («persona:nurse-partner»
  → ищем who, выполняющую действия медсестры партнёрской клиники).
- `error`: who, который не соответствует **ни одной** persona в project
  (включая системных акторов в who.md — они допустимы как «намеренное
  исключение», но всё равно должны иметь связь с интересами какой-то
  persona).
- `warning`: persona, под которую who покрывает только **часть**
  jobs-to-be-done. Если у persona 3 jobs, а who участвует только в
  одном — это намёк, что нужны ещё роли.

**Промпт-добавка:**

```
Сопоставь project.persona и interface.who семантически. Persona — это
"кто адресат боли продукта". Who — "роль, выполняющая шаг бизнес-процесса".
Связь не структурная: одна persona может развернуться в несколько who
(например, persona "медсестра партнёрской клиники" → who: nurse-partner,
nurse-partner-senior).

Для каждой persona: какие who её "несут" (выполняют её jobs)? Если ни
одного — error.

Для каждого who: какой persona он принадлежит? Системные акторы (scheduler,
external-svc) — допустимо без persona, но обоснуй почему именно этот
системный интерес.

Используй persona.jobs / pains / context и who.description / соседние
situation.action для сопоставления.
```

## capability-situation

**Source:** `docs/project/capability.md`.
**Destination:** `docs/interface/situation.md`.
**Применим если:** оба слоя существуют.

**Что искать:**

- `error`: capability `stable`, под которую в interface **нет ни одной
  ситуации**, реализующей действие. Capability — это «что продукт
  умеет», situation — конкретное UX-проявление этого умения.
- `warning`: capability имеет один-два, в то время как ожидается
  больше (capability сложная, например «согласовать слот» — обычно
  это 3-5 ситуаций).
- `hint`: ситуация в interface, у которой нет ясной capability-якоря
  в project. Возможно, нужна capability, либо ситуация не нужна.

**Промпт-добавка:**

```
Capability — устойчивое умение продукта в языке persona. Situation —
конкретная UX-точка, где это умение реализуется (кто/когда/что/ради
чего/с какими данными).

Для каждой capability: какие situation её реализуют? Сопоставь по
смыслу действий и goal.

Для каждой situation: к какой capability она относится? Если ни к
одной — hint (либо новая capability, либо ситуация не нужна).
```

## capability-domain

**Source:** `docs/project/capability.md`.
**Destination:** `docs/domains/` (если есть).
**Применим если:** `docs/domains/` существует.

**Что искать:**

- `error`: capability `stable`, под которую в `docs/domains/` нет
  бизнес-домена / агрегата. Capability не существует в коде.
- `warning`: domain в `docs/domains/`, у которого не находится
  capability-якорь в project. Возможно, технический домен (auth,
  logging) — это норма; но если бизнес-домен (referrals, billing) —
  это пробел.

**Промпт-добавка:**

```
Capability — продуктовое умение. Domain в docs/domains/ — бизнес-код,
несущий это умение.

Для каждой capability: есть ли в docs/domains/ агрегат или сервис,
реализующий бизнес-логику? Сопоставь по семантике, не имени файла.

Технические домены (auth, audit, logging) могут не иметь
capability-якоря — отметь, но не помечай ошибкой.
```

## surface-zone

**Source:** `docs/project/surface.md`.
**Destination:** `docs/interface/zone.md`.
**Применим если:** оба слоя существуют.

**Что искать:**

- `error`: surface `stable`, у которой нет **ни одной** зоны в
  interface, принадлежащей этой поверхности (по смыслу).
- `error`: zone в interface, не привязанная ни к одной surface (zone
  «висит в воздухе»).
- `warning`: zone, которая по смыслу принадлежит сразу нескольким
  surface (например, общая навигация для web и mobile). Это норма, но
  важно явно зафиксировать.

**Промпт-добавка:**

```
Surface — поверхность продукта (web/mobile/api/admin/bot/...). Zone —
зона интерфейса (логический контейнер блоков).

Для каждой surface: какие zone в неё попадают? Связь семантическая —
смотри на surface.type, surface.lives-at, и zone.description /
parent-zone.

Для каждой zone: какой surface она принадлежит? Если ни одной —
error.
```

## surface-screen

**Source:** `docs/project/surface.md`.
**Destination:** `docs/screens/` (если есть).
**Применим если:** `docs/screens/` существует.

**Что искать:**

- `error`: surface `stable`, у которой нет ни одного screen или flow
  в `docs/screens/`.
- `warning`: screen / flow в `docs/screens/`, не привязанный к
  surface проекта (по смыслу).

**Промпт-добавка:**

```
Surface — где продукт работает. Screen / flow в docs/screens/ —
композиция UX, ассеты, hi-fi-материал.

Для каждой surface: есть ли в docs/screens/ хотя бы один артефакт
этой поверхности? По смыслу — посмотри shell/flow/screen-описания.
```

## integration-domain

**Source:** `docs/project/integration.md`.
**Destination:** `docs/domains/` (если есть).
**Применим если:** `docs/domains/` существует.

**Что искать:**

- `error`: integration `stable`, под которую в `docs/domains/` нет
  адаптера / клиента.
- `warning`: адаптер в `docs/domains/`, у которого нет integration в
  project (возможно, технический адаптер — http-клиент, redis-клиент
  — это норма; бизнес-адаптер без integration — пробел).

**Промпт-добавка:**

```
Integration — внешняя система, с которой обмениваемся. Domain в
docs/domains/ может содержать адаптер для интеграции.

Для каждой integration: есть ли адаптер / клиент в docs/domains/?
Сопоставь по семантике.

Технические адаптеры (http-client, db-client) могут не иметь
integration-якоря — отметь, не error.
```

## constraint-surface

**Source:** `docs/project/constraint.md`.
**Destination:** `docs/project/surface.md`, `docs/project/integration.md`.
**Применим если:** project-слой существует.

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
Constraint — обязательное правило (закон / SLA / контракт). Обычно
constraint касается surface (где это применимо) или integration (с
чем обмениваемся под этим правилом).

Для каждого constraint: какая surface или integration его несёт? Найди
в description упоминания или сопоставь по смыслу (152-ФЗ → surface с
PII; PCI-DSS → integration с платежами; HIPAA → surface с
медданными).

Если связь не видна нигде — warning.

Дополнительно: surface, обрабатывающая PII / финансы / здоровье, без
относящегося constraint — hint.
```

## market-capability

**Source:** `docs/project/market.md`.
**Destination:** `docs/project/capability.md`.
**Применим если:** оба наполнены.

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
Market — рыночные аналоги. Capability — наши умения.

Для каждого market-аналога: что он покрывает из наших capabilities?
Что у него есть, чего у нас нет (гэп для нас)? Что у нас есть, чего у
него нет (наша дифференциация)?

Возвращай как findings hints / warnings — это материал для аналитика,
не error.
```

## Порядок lens-ов

При полном прогоне порядок сверху вниз по слоям:

1. `factor-business` (бизнес → проблема)
2. `currentmetric-metric` (бизнес → проблема)
3. `goal-vision` (проблема → продукт)
4. `subject-persona` (проблема → продукт)
5. `segment-persona` (бизнес → продукт)
6. `bet-capability` (проблема → продукт)
7. `persona-who` (foundation, продукт → interface)
8. `surface-zone` (foundation)
9. `capability-situation` (foundation)
10. `capability-domain` (если есть)
11. `integration-domain` (если есть)
12. `surface-screen` (если есть)
13. `constraint-surface` (cross-внутри-project)
14. `market-capability` (последний — он часто даёт hints, не error)

`--quick` запускает три foundation-угла продукт↔interface (`persona-who`,
`capability-situation`, `surface-zone`). Для верхних слоёв —
`goal-vision`, `subject-persona` как быстрый upstream-чек.
