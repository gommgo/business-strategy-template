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

- **Верхнеуровневые, прогон один раз** (общие слои business ↔ ajtbd ↔
  swot ↔ hypothesis-map, без проекта): `factor-business`,
  `currentmetric-metric`, `segmentproblem-bizproblem`, `segment-subject`,
  `solution-business`, `business-segment`, `prospective-consistency`,
  `provenance-upstream`.
- **Верхнеуровневый M:N, прогон один раз над всеми проектами**:
  `addresses-problem-bizproblem`.
- **По каждому проекту** (общие слои swot/hypothesis-map ↔ продукт проекта;
  скоупится к проблемам, которые проект закрывает через
  `vision.addresses-problem`): `goal-vision`, `subject-user`,
  `bet-capability`, `capability-hypothesis`.
- **По каждому проекту** (общий слой ajtbd ↔ продукт проекта):
  `segment-user`, `job-vision`, `segmentproblem-vision`,
  `mechanic-capability`, `capability-job`.
- **По каждому проекту** (внутри папки проекта + сквозные рёбра interface):
  `user-who`, `capability-situation`, `situation-job`,
  `situation-hypothesis`, `capability-domain`, `surface-zone`,
  `surface-screen`, `integration-domain`, `constraint-surface`,
  `market-capability`.

## factor-business

**Source:** `docs/swot/factor.md`.
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
**Destination:** `docs/hypothesis-map/metric.md`.
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

## addresses-problem-bizproblem

**Source:** `docs/projects/*/vision.md` (поле `addresses-problem` каждого
проекта, кроме `_canon`).
**Destination:** `docs/business/business-problem.md` (таблица проблем).
**Скоуп:** один раз, **над всеми проектами** (M:N, обе стороны).
**Применим если:** есть хотя бы один проект и непустой `business/business-problem.md`.

**Что искать:**
- `error`: проект объявляет `addresses-problem` ref, который **не
  резолвится** ни в одну строку `business-problem` (проект бьёт в несуществующую
  проблему — опечатка slug или проблема не заведена).
- `hint`: строка `business-problem` (проблема), которую **не закрывает ни один
  проект** (висящая проблема — нужен проект, или она вне scope).
- `warning`: проект с **пустым** `addresses-problem` при наполненном
  vision (продукт без явной привязки к проблеме бизнеса).

**Промпт-добавка:**
```
Это единственный M:N-угол через много проектов. Прочитай
addresses-problem у КАЖДОГО docs/projects/<slug>/vision.md (исключи
_canon) и строки docs/business/business-problem.md.

Связь slug-явная по форме, но проверяй СМЫСЛОВО, а не строкой: ref
проекта должен указывать на реально существующую проблему business-problem.

Прямая сторона: для каждого ref каждого проекта — есть ли такая строка
business-problem? Нет — error (укажи проект и нерезолвящийся ref).

Обратная сторона: для каждой строки business-problem — закрывает ли её хоть один
проект? Ни один — hint (проблема висит).

Проект с непустым vision, но пустым addresses-problem — warning.

Поле project в каждом finding ставь = slug проекта-источника (для
hint про висящую проблему — project: null).
```

## segmentproblem-bizproblem

**Source:** `docs/ajtbd/segment-problem.md`.
**Destination:** `docs/business/business-problem.md` (таблица проблем).
**Скоуп:** один раз (общие слои ajtbd ↔ business-problem, без проекта).
**Применим если:** оба слоя наполнены.

**Что искать:**
- `warning`: строка `business-problem` (проблема бизнеса), которую не доказывает ни
  одно трение клиента (`segment-problem`) — проблема бизнеса без единого
  трения-доказательства (по ядру AJTBD проблема бизнеса опирается на
  трение клиента).
- `hint`: сильное трение клиента (`strength` высок, низкая
  удовлетворённость нанятого решения), не работающее ни на одну проблему
  бизнеса (`feeds-problem: —` и нет семантической пары) — кандидат в
  новую проблему `business-problem`.
- `error`: `segment-problem.feeds-problem` указывает на строку `business-problem`,
  которой нет (трение бьёт в несуществующую проблему бизнеса — опечатка
  slug или проблема не заведена).

**Промпт-добавка:**
```
segment-problem — трение КЛИЕНТА с нанятым решением (слой ajtbd); business-problem —
проблема БИЗНЕСА заказчика (business-problem). Это РАЗНЫЕ сущности:
первое доказывает и питает второе (сильное трение при низкой
удовлетворённости → проблема бизнеса).

Прямая сторона: `feeds-problem` (если задан) должен указывать на реально
существующую строку business-problem — иначе error. Без `feeds-problem` сопоставляй
СМЫСЛОВО: какая проблема бизнеса опирается на это трение.

Обратная сторона: для каждой строки business-problem — доказывает ли её хоть одно
трение клиента? Ни одного — warning (проблема бизнеса без трения-
доказательства).

Сильное трение, не питающее ни одну проблему бизнеса — hint (кандидат в
новую проблему). НЕ путай слои: segment-problem не подаётся как проблема
бизнеса напрямую, он её питает.
```

## segment-subject

**Source:** `docs/ajtbd/segment.md`.
**Destination:** `docs/hypothesis-map/subject.md`.
**Скоуп:** один раз (общие слои ajtbd ↔ business-problem, без проекта).
**Применим если:** оба слоя наполнены.

**Что искать:**
- `warning`: субъект влияния (`subject`), не выводимый ни из одного
  сегмента (откуда он взялся — субъект без сегмента).
- `hint`: сегмент с высоким Score, не ставший ни одним субъектом влияния
  (возможный кандидат, на чьё поведение целиться).

**Промпт-добавка:**
```
segment — группа клиентов по бандлу работ (слой ajtbd); subject — тот,
чьё поведение двигает метрику бизнеса (business-problem). Субъект влияния
обычно ВЫРАСТАЕТ из сегмента.

Для каждого subject: из какого сегмента он выводится (бандл работ /
who-context совпадает по смыслу)? Если ни из одного — warning (субъект
без сегмента).

Для сегмента с заметным Score, не ставшего ни одним субъектом — hint.
Связь семантическая: сопоставляй по работам и контексту, не по slug.
```

## solution-business

**Source:** `docs/ajtbd/solution.md`.
**Destination:** `docs/business/` (`competitor.md`, `offering.md`).
**Скоуп:** один раз (общие слои ajtbd ↔ business, без проекта).
**Применим если:** оба слоя наполнены.

**Что искать:**
- `warning`: `solution.maps-to` указывает на `competitor`/`offering`,
  которого нет в `docs/business/` (нанятое решение бьёт в несуществующего
  игрока рынка / офер — опечатка slug или сущность не заведена).
- `hint`: игрок рынка (`competitor`) или собственный офер (`offering`)
  бизнеса, не нанятый сегментом ни на одну работу (нет `solution` с
  `maps-to` на него) — возможно, разведка решений неполна.
- `hint`: нанятое решение типа `product`/`service` с `maps-to: —`,
  которое по смыслу совпадает с известным конкурентом / офером бизнеса
  (связь не проставлена).

**Промпт-добавка:**
```
solution — то, что сегмент НАНИМАЕТ сейчас на работу (слой ajtbd);
competitor/offering — игроки рынка и собственный офер бизнеса (business).
Нанятое решение часто И ЕСТЬ конкурент или офер бизнеса (`maps-to`).

Прямая сторона: каждый `maps-to` должен резолвиться в реальный
competitor или offering — иначе warning.

Обратная сторона: каждый competitor / offering — нанят ли он сегментом
(есть ли solution с maps-to на него)? Нет — hint (разведка решений
неполна).

DIY / субститут / бездействие закономерно идут с `maps-to: —` — это
норма, не finding. Но product/service с пустым maps-to, совпадающий по
смыслу с известным игроком, — hint (проставить связь).
```

## business-segment

**Source:** `docs/business/offering.md` (`for-segment`), `channel.md`
(`serves-segment`).
**Destination:** `docs/ajtbd/segment.md`.
**Скоуп:** один раз (общие слои business ↔ ajtbd, без проекта).
**Применим если:** оба слоя наполнены.

**Что искать:**
- `error`: `offering.for-segment` или `channel.serves-segment` указывает
  на сегмент, которого нет в `docs/ajtbd/segment.md` (межслойная ссылка
  не резолвится — опечатка slug или сегмент не заведён).
- `warning`: офер, чей `for-segment` по смыслу не соответствует бандлу
  работ названного сегмента (офер продаётся «не тому» сегменту —
  подозрение на ошибочную привязку).
- `hint`: сегмент в ajtbd с `served=served`, который не обслуживает ни
  один офер (`for-segment`) и ни один канал (`serves-segment`) — бизнес
  знает о сегменте по разведке, но ничего ему не продаёт/не достаёт.
  **Проспективный сегмент** (`served=prospective`) без оферов/каналов —
  **норма**, не finding (разведка рынка, который бизнес ещё не обслуживает).

**Промпт-добавка:**
```
offering.for-segment и channel.serves-segment — межслойные ссылки из
business в ajtbd/segment. Проверь, что каждая ссылка РЕЗОЛВИТСЯ в
реальный сегмент (иначе error) и ОСМЫСЛЕННА (офер/канал по смыслу
подходит бандлу работ и критериям успеха сегмента — иначе warning).

Обратно: сегмент с served=served, который не обслуживает ни офер, ни
канал — hint (бизнес видит сегмент, но не работает с ним). Сегмент с
served=prospective без оферов/каналов — НЕ finding (разведка рынка).
Связь по форме slug-явная, но проверяй смыслом, а не строкой.
```

## goal-vision

**Source:** `docs/hypothesis-map/goal.md`, `metric.md` (только строки,
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

## subject-user

**Source:** `docs/hypothesis-map/subject.md` (только субъекты проблем,
которые закрывает проект).
**Destination:** `docs/projects/<slug>/user.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют; у проекта непустой
`addresses-problem`.

**Что искать:**
- `error`: субъект влияния (positive) проблемы, которую закрывает проект,
  не ставший ни одним user продукта (на чьё поведение целимся — но
  продукт не для него).
- `warning`: мотивация субъекта (боли/желания) не отражена в
  user.jobs/pains.

**Промпт-добавка:**
```
subject — тот, чьё поведение двигает метрику; user — адресат боли
продукта <slug>. Скоупь субъекты к проблемам этого проекта (колонка
`problem`).

Положительный субъект обычно становится user. Для каждого positive-
субъекта закрываемой проблемы: есть ли соответствующий user в
docs/projects/<slug>/user.md? Перенесена ли его мотивация в
jobs/pains? Негативный субъект user не требует.
```

## segment-user

**Source:** `docs/ajtbd/segment.md`.
**Destination:** `docs/projects/<slug>/user.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют.

**Что искать:**
- `hint`: сегмент рынка (`ajtbd/segment`) без соответствующего user в
  этом проекте (продукт не обслуживает этот сегмент — намеренно или
  пропуск? — «сегмент без пользователя»).
- `hint`: user проекта, не сводимый ни к одному сегменту, ни к
  субъекту (откуда он? — «пользователь без сегмента»).

**Промпт-добавка:**
```
segment — группа клиентов рынка по бандлу работ (слой ajtbd); user —
пользователь продукта <slug>. Это РАЗНЫЕ сущности, но связанные: продукт
часто делается для части сегментов рынка.

Сопоставляй по смыслу: бандл работ / who-context / критерии успеха
сегмента ↔ jobs / pains / context пользователя.

Сегмент без user в этом проекте («сегмент без пользователя») и user без
сегмента/субъекта («пользователь без сегмента») — hint, не error (один проект
может намеренно сужать охват сегментов; их закрывает другой проект).
```

## job-vision

**Source:** `docs/ajtbd/job.md` (работы уровня `big` / `core`).
**Destination:** `docs/projects/<slug>/vision.md` (раздел `Success`).
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют.

**Что искать:**
- `warning`: `vision.Success` не целит ни в одну Big/Core Job сегментов,
  которые продукт обслуживает (успех продукта оторван от верхней работы
  клиента).
- `hint`: Core Job сегмента, обслуживаемого продуктом, не отражённая в
  `vision.Success` (возможный пробел — продукт не помогает с этой
  работой).

**Промпт-добавка:**
```
job уровня big/core — верхняя мотивация и то, за что сегмент платит
(слой ajtbd); vision.Success — каким продукт <slug> видит успех. Успех
продукта должен ЦЕЛИТЬ в Big/Core Job сегмента, который он обслуживает.

Скоупь работы к сегментам, которые продукт обслуживает (через пользователей
проекта ↔ сегменты). Низкоуровневые работы (`low`) — UX-шаги, не цель;
их в Success не ждём.

Для vision.Success: видна ли за ней Big/Core Job? Не видна — warning.
Для Core Job обслуживаемого сегмента без отражения в Success — hint.
```

## segmentproblem-vision

**Source:** `docs/ajtbd/segment-problem.md`.
**Destination:** `docs/projects/<slug>/vision.md` (раздел `Problem`).
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют.

**Что искать:**
- `warning`: `vision.Problem` не опирается ни на одно трение клиента
  (`segment-problem`) сегментов, которые продукт обслуживает (проблема
  продукта выдумана, а не выведена из разведанного трения).
- `hint`: сильное трение клиента обслуживаемого сегмента, не отражённое
  в `vision.Problem` (продукт мог бы его закрыть).

**Промпт-добавка:**
```
segment-problem — трение КЛИЕНТА с нанятым решением (слой ajtbd);
vision.Problem — какую проблему решает продукт <slug>. Проблема продукта
выводится из разведанного трения клиента.

Скоупь трения к сегментам, которые продукт обслуживает (через пользователей
проекта ↔ сегменты).

Для vision.Problem: опирается ли она на конкретное трение клиента? Не
опирается — warning. Сильное трение обслуживаемого сегмента без
отражения в Problem — hint. НЕ путай с проблемой бизнеса (business-problem) — здесь
проблема ПРОДУКТА.
```

## mechanic-capability

**Source:** `docs/ajtbd/job-graph.md` (поле `value-mechanics`).
**Destination:** `docs/projects/<slug>/capability.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют.

**Что искать:**
- `warning`: механика ценности (`value-mechanics`) графа сегмента,
  обслуживаемого продуктом, не реализованная ни одной capability
  продукта («механика без capability» — выведенный из графа кандидат
  ценности не дошёл до продукта).
- `hint`: capability продукта, не выводимая ни из одной механики ценности
  (продукт умеет то, что не подсказано разведкой — проверить
  обоснованность).

**Промпт-добавка:**
```
value-mechanics — какие из 11 механик создания ценности граф работ
открывает (кандидаты ценности, слой ajtbd); capability — что продукт
<slug> умеет. Механика ценности — это КАНДИДАТ в capability.

Скоупь механики к сегментам, которые продукт обслуживает (через пользователей
проекта ↔ сегменты графа).

Для каждой механики: реализована ли она хотя бы одной capability? Не
реализована — warning («механика без capability»). Capability без
механики-якоря — hint (возможно, обоснована иначе; не error).
```

## bet-capability

**Source:** `docs/swot/bet.md`, `goal.md` (только ставки/цели
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

## user-who

**Source:** `docs/projects/<slug>/user.md`.
**Destination:** `docs/projects/<slug>/interface/who.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют в папке проекта.

**Что искать:**

- `error`: user, под которую в `who.md` **нет ни одной роли**,
  семантически соответствующей. Не slug — смысл («user:nurse-partner»
  → ищем who, выполняющую действия медсестры партнёрской клиники).
- `error`: who, который не соответствует **ни одной** user проекта
  (включая системных акторов в who.md — они допустимы как «намеренное
  исключение», но всё равно должны иметь связь с интересами какой-то
  user).
- `warning`: user, под которую who покрывает только **часть**
  jobs-to-be-done. Если у user 3 jobs, а who участвует только в
  одном — это намёк, что нужны ещё роли.

**Промпт-добавка:**

```
Сопоставь user и who проекта <slug> семантически — оба слоя живут в
docs/projects/<slug>/. User — это "кто адресат боли продукта". Who —
"роль, выполняющая шаг бизнес-процесса". Связь не структурная: одна
user может развернуться в несколько who (например, user "медсестра
партнёрской клиники" → who: nurse-partner, nurse-partner-senior).

Для каждого user: какие who его "несут" (выполняют его jobs)? Если ни
одного — error.

Для каждого who: какой user он принадлежит? Системные акторы (scheduler,
external-svc) — допустимо без user, но обоснуй почему именно этот
системный интерес.

Используй user.jobs / pains / context и who.description / соседние
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
продукта в языке user. Situation — конкретная UX-точка, где это
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
- `hint`: surface с user, обрабатывающая PII / финансы / здоровье,
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

## prospective-consistency

**Source:** `docs/projects/*/vision.md` (`market-maturity`,
`addresses-problem`).
**Destination:** `docs/ajtbd/segment.md` (`served`),
`docs/business/business-problem.md` (`served`).
**Скоуп:** один раз, над всеми проектами.
**Применим если:** есть хотя бы один проект и проспективные сущности
(`served=prospective`) наверху.

**Что искать:**
- `warning`: проект с `vision.market-maturity=prospective`, чьи
  `addresses-problem` указывают только на `served`-проблемы (рассинхрон:
  продукт-разведка целит в уже обслуживаемый рынок) — или наоборот, проект
  с `market-maturity=served`, адресующий `prospective`-проблему.
- `hint`: проспективный сегмент/проблема (`served=prospective`), который
  не адресует ни один проект (разведка без инициативы — нормально, но
  стоит знать).

**Промпт-добавка:**
```
market-maturity на vision описывает, целит ли продукт в обслуживаемый
рынок (served) или разведывает новый (prospective). Проспективный продукт
должен адресовать проспективные сущности наверху (ajtbd/segment.served=
prospective, business/business-problem.served=prospective). Проверь
согласованность: market-maturity проекта ↔ served его addresses-problem
(и связанных сегментов). Проспективная сущность без адресующего проекта —
hint, не error. НЕ флагай проспективные сущности как «висяк».
```

## provenance-upstream

**Source:** `docs/business/offering.md`, `docs/business/current-metric.md`,
`docs/business/business-problem.md`, `docs/ajtbd/segment.md` (поле
`from-project` + `served`).
**Destination:** `docs/projects/*/vision.md` (`lifecycle`,
`market-maturity`, `addresses-problem`).
**Скоуп:** один раз, над всеми проектами.
**Применим если:** есть хотя бы один проект; наверху есть записи с
непустым `from-project` **или** проект на `lifecycle: stable`.

Обратная сторона восходящего потока (reconcile-up): `from-project`
делает контур наблюдаемым — этот угол проверяет провенанс с двух концов
(ссылка верна, контур замкнут, `market-maturity ↔ served ↔ from-project`
согласованы). Дополняет `prospective-consistency` (там — `market-maturity ↔
served`; здесь — измерение провенанса `from-project`).

**Что искать:**
- `error`: `*.from-project` ссылается на проект, которого нет (нет каталога
  `docs/projects/<slug>/`) — провенанс бьёт в несуществующий проект.
- `warning`: рассинхрон `market-maturity ↔ served ↔ from-project`:
  - запись наверху с `from-project = <slug>`, но `served = prospective`
    (продукт проявил/подтвердил, а рынок не повышен — контур не доведён);
  - `served = served` с `from-project = <slug>`, но `vision` проекта
    `<slug>` не `market-maturity: served` и/или не адресует связанную
    проблему (провенанс не подтверждается продуктом).
- `hint`: **обратная сторона** — проект на `lifecycle: stable` (особенно
  `market-maturity: prospective`), у которого связанные сущности наверху
  (offering / current-metric / адресуемые business-problem / сегменты) **не
  несут** `from-project = <slug>` и не повышены до `served` — контур не
  замкнут, повод прогнать `/entrypoint --upstream <slug>`.

**Промпт-добавка:**
```
from-project на offering/current-metric/business-problem/segment — провенанс
восходящего потока: какой дозревший продукт проявил/подтвердил запись.
Триггер потока — vision.lifecycle → stable.

Прямая сторона: каждый from-project резолвится в реальный
docs/projects/<slug>/? Нет — error.

Согласованность market-maturity ↔ served ↔ from-project:
- from-project проставлен, но served=prospective — warning (контур не
  доведён до served);
- served=served + from-project=<slug>, но vision проекта <slug> не
  market-maturity: served и/или не адресует связанную проблему — warning.

Обратная сторона (замкнут ли контур): для каждого проекта на
lifecycle: stable — несут ли связанные сущности наверху его from-project и
повышены ли до served? Нет — hint (повод запустить reconcile-up). Связь
семантическая (не grep): «связанная сущность» — по vision.addresses-problem
и адресуемому сегменту. Проспективную сущность без from-project НЕ флагай
как «висяк». В finding указывай проект-провенанс.
```

## capability-hypothesis

**Source:** `docs/projects/<slug>/capability.md` (поле `hypotheses`).
**Destination:** `docs/hypothesis-map/hypothesis.md` (по проблемам, которые
закрывает проект).
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют; у проекта непустой
`addresses-problem`.

**Что искать:**
- `error`: `capability.hypotheses` ссылается на гипотезу, которой нет в
  `docs/hypothesis-map/` (ребро бьёт в несуществующую сущность).
- `hint`: гипотеза проблемы, которую закрывает проект, не реализуемая ни
  одной capability этого продукта (стратегия без продуктового воплощения —
  возможно, её несёт соседний проект).

**Промпт-добавка:**
```
capability.hypotheses — авторское ребро продукт → hypothesis-map:
возможность реализует гипотезу. Скоупь гипотезы к проблемам проекта
(колонка `problem`). Прямая сторона: каждый ref резолвится в реальную
hypothesis? Нет — error. Обратная: гипотеза проблемы проекта без
реализующей capability — hint (может нести соседний проект). Связь
семантическая.
```

## capability-job

**Source:** `docs/projects/<slug>/capability.md` (поле `jobs`).
**Destination:** `docs/ajtbd/job.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют.

**Что искать:**
- `error`: `capability.jobs` ссылается на работу, которой нет в
  `docs/ajtbd/job.md`.
- `hint`: Core/Big Job обслуживаемого сегмента без capability, прямо в неё
  целящей (`capability.jobs`) — дополняет `mechanic-capability` (там через
  механики ценности, здесь — прямое ребро).

**Промпт-добавка:**
```
capability.jobs — прямое авторское ребро продукт → ajtbd: возможность
целит в работу сегмента (в дополнение к выводимому через
job-graph.value-mechanics). Прямая сторона: каждый ref резолвится в
реальный job? Нет — error. Обратная: Big/Core Job обслуживаемого сегмента
без прямо целящей capability — hint. Связь семантическая.
```

## situation-job

**Source:** `docs/projects/<slug>/interface/situation.md` (поле `jobs`).
**Destination:** `docs/ajtbd/job.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют.

**Что искать:**
- `error`: `situation.jobs` ссылается на работу, которой нет в
  `docs/ajtbd/job.md`.
- `hint`: UX-ситуация, обслуживающая работу сегмента, без проставленного
  `jobs` (связь полезна, но не обязательна).

**Промпт-добавка:**
```
situation.jobs — авторское ребро interface → ajtbd: UX-шаг обслуживает
работу сегмента. Прямая сторона: каждый ref резолвится в реальный job?
Нет — error. Это мягкое ребро (опц.), прочерк — норма; не требуй его.
В finding укажи project.
```

## situation-hypothesis

**Source:** `docs/projects/<slug>/interface/situation.md` (поле
`hypotheses`).
**Destination:** `docs/hypothesis-map/hypothesis.md`.
**Скоуп:** по проекту.
**Применим если:** оба слоя существуют.

**Что искать:**
- `error`: `situation.hypotheses` ссылается на гипотезу, которой нет в
  `docs/hypothesis-map/`.
- `hint`: UX-ситуация, которая по смыслу проверяет/обслуживает гипотезу,
  без проставленного `hypotheses`.

**Промпт-добавка:**
```
situation.hypotheses — авторское ребро interface → hypothesis-map: UX-шаг
проверяет/обслуживает гипотезу. Прямая сторона: каждый ref резолвится в
реальную hypothesis? Нет — error. Мягкое ребро (опц.), прочерк — норма.
В finding укажи project.
```

## Порядок lens-ов

Все агенты спавнятся в одном message-блоке параллельно — порядок ниже
лишь логический (как раскладывать findings в отчёте), не очередь
исполнения.

**Верхнеуровневые (прогон один раз):**

1. `factor-business` (бизнес → проблема)
2. `currentmetric-metric` (бизнес → проблема)
3. `addresses-problem-bizproblem` (продукты ↔ проблемы, M:N над всеми
   проектами)
4. `segmentproblem-bizproblem` (ajtbd → проблема: трение клиента доказывает
   проблему бизнеса)
5. `segment-subject` (ajtbd → проблема: субъект вырастает из сегмента)
6. `solution-business` (ajtbd → бизнес: нанятое решение ↔ конкурент/офер)
7. `business-segment` (бизнес → ajtbd: оферы/каналы обслуживают сегменты)
8. `prospective-consistency` (market-maturity ↔ served сущностей наверху)
9. `provenance-upstream` (from-project ↔ проект: обратная сторона
   восходящего потока, согласованность market-maturity ↔ served ↔ from-project)

**По каждому проекту** (для каждого `<slug>` из `docs/projects/`, кроме
`_canon`; раскрывается в пары `проект × lens`):

10. `goal-vision` (проблема → продукт; скоуп к проблемам проекта)
11. `subject-user` (проблема → продукт; скоуп к проблемам проекта)
12. `segment-user` (ajtbd → продукт)
13. `job-vision` (ajtbd → продукт: Big/Core Job ↔ vision.Success)
14. `segmentproblem-vision` (ajtbd → продукт: трение ↔ vision.Problem)
15. `mechanic-capability` (ajtbd → продукт: механика ценности ↔ capability)
16. `bet-capability` (проблема → продукт; скоуп к проблемам проекта)
17. `capability-hypothesis` (продукт → hypothesis-map: capability.hypotheses)
18. `capability-job` (продукт → ajtbd: capability.jobs)
19. `user-who` (foundation, продукт → interface проекта)
20. `surface-zone` (foundation)
21. `capability-situation` (foundation)
22. `situation-job` (interface → ajtbd: situation.jobs)
23. `situation-hypothesis` (interface → hypothesis-map: situation.hypotheses)
24. `capability-domain` (если у проекта есть `domains/`)
25. `integration-domain` (если у проекта есть `domains/`)
26. `surface-screen` (если у проекта есть `screens/`)
27. `constraint-surface` (cross-внутри-project)
28. `market-capability` (часто даёт hints, не error)

Полный рой = `9 верхнеуровневых + Σ по проектам (применимые
project-углы)`.

`--quick` запускает по каждому проекту три foundation-угла
продукт↔interface (`user-who`, `capability-situation`, `surface-zone`)
плюс `addresses-problem-bizproblem` один раз. Для верхних слоёв —
`goal-vision`, `subject-user` (по проекту) как быстрый upstream-чек.
