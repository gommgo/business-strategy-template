# Углы проверки cross-audit

Каждый lens — отдельный угол семантической проверки. Один lens = один
агент (для project-скоупленного — один агент на пару `проект × lens`; для
project×surface-скоупленного — один агент на тройку `проект × поверхность ×
lens`). Запускаются параллельно.

`<slug>` = `<project-slug>` — подставляется на спавне. `<surface>` = slug
поверхности из реестра `docs/projects/<slug>/surface.md` — подставляется на
спавне для project×surface-углов. Пути с `<slug>` указывают на папку
конкретного проекта `docs/projects/<slug>/`; пути с `<surface>` — на
per-surface артефакт (`capability/<surface>.md`, `interface/<surface>/...`,
`screens/<surface>/...`).

Структура каждого пункта:

- **Source / Destination** — какие слои читать (с `<slug>`/`<surface>` где
  project/surface-скоуп).
- **Скоуп** — `один раз` (верхнеуровневый, без проекта), `по проекту`
  (раскрывается в пары `проект × lens`) или `по проекту × поверхность`
  (раскрывается в тройки `проект × поверхность × lens`).
- **Применим если** — какие слои/каталоги должны существовать.
- **Что искать** — конкретные семантические паттерны.
- **Промпт для агента** — добавка к каркасу из SKILL.md.

## Поверхность (surface) — ось партиционирования

Продуктовый слой партиционирован по поверхности: реестр-хребет
`docs/projects/<slug>/surface.md` объявляет поверхности, и их slug'и —
ключи трёх per-surface слоёв: возможности (`capability/<surface>.md`),
интерфейс (`interface/<surface>/...`) и экраны (`screens/<surface>/...`).
Кросс-поверхностные kind продукта (`vision`, `user`, `integration`,
`boundary`, `constraint`, `market`) лежат в корне папки проекта. Домены
(`domains/<ctx>/`) **surface-агностичны** — партиционируются по
bounded-context, не по поверхности.

Поэтому lens, чей source ИЛИ destination — per-surface артефакт,
раскрывается в **тройки** `проект × поверхность × lens`: на каждую
поверхность реестра — свой агент. Lens с проектными (корневыми, не
per-surface) целями раскрывается в **пары** `проект × lens`. Верхнеуровневые —
один агент.

## Скоуп углов

- **Верхнеуровневые, прогон один раз** (общие слои business ↔ ajtbd ↔
  swot ↔ hypothesis-map, без проекта): `factor-business`,
  `currentmetric-metric`, `segmentproblem-bizproblem`, `segment-subject`,
  `solution-business`, `business-segment`, `prospective-consistency`,
  `provenance-upstream`, `stakeholder-subject`, `stakeholder-factor`,
  `stakeholder-strategy`, `projectmap-reciprocity`.
- **Верхнеуровневый M:N, прогон один раз над всеми проектами**:
  `addresses-problem-bizproblem`.
- **По каждому проекту** (пары `проект × lens`; цели — корневые kind
  продукта `vision`/`user`/`integration`, не per-surface):
  - swot/hypothesis-map ↔ продукт (скоупится к проблемам, которые проект
    закрывает через `vision.addresses-problem`): `goal-vision`,
    `subject-user`.
  - ajtbd ↔ продукт: `segment-user`, `job-vision`, `segmentproblem-vision`.
  - продукт ↔ соседние проекты (межпроектный): `integration-crossproject`.
- **По каждому проекту × поверхность** (тройки `проект × поверхность × lens`;
  source ИЛИ destination — per-surface артефакт `capability/<surface>.md`,
  `interface/<surface>/*`, `screens/<surface>/*`):
  - swot/hypothesis-map ↔ возможности поверхности (скоупится к проблемам
    проекта): `bet-capability`, `capability-hypothesis`.
  - ajtbd ↔ возможности поверхности: `mechanic-capability`, `capability-job`.
  - продукт ↔ интерфейс/экраны поверхности: `user-who`,
    `capability-situation`, `surface-zone`, `surface-screen`,
    `surface-capability`.
  - возможности поверхности ↔ домены проекта: `capability-domain`.
  - сквозные рёбра интерфейса поверхности: `situation-job`,
    `situation-hypothesis`.
  - интеграция ↔ домены (по поверхностям интеграции): `integration-domain`.
  - ограничение ↔ поверхность/интеграция (по поверхностям): `constraint-surface`.
  - рынок ↔ возможности поверхности: `market-capability`.
- **По проекту, сразу по всем поверхностям** (один агент на проект,
  читает `data-items.md` всех папок поверхностей): `dataitems-crosssurface`.

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
проекта, кроме `_template`).
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
_template) и строки docs/business/business-problem.md.

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
- `warning`: **позитивный** субъект влияния (`subject`, `kind: positive`),
  не выводимый ни из одного сегмента (откуда он взялся — субъект без
  сегмента). Негативный субъект (`kind: negative`) сегмента не требует.
- `hint`: сегмент с высоким Score, не ставший ни одним субъектом влияния
  (возможный кандидат, на чьё поведение целиться).

**Промпт-добавка:**
```
segment — группа клиентов по бандлу работ (слой ajtbd); subject — тот,
чьё поведение двигает метрику бизнеса (business-problem). Субъект влияния
обычно ВЫРАСТАЕТ из сегмента.

Для каждого позитивного subject (kind: positive): из какого сегмента он
выводится (бандл работ / who-context совпадает по смыслу)? Если ни из
одного — warning (субъект без сегмента). Негативный субъект (kind:
negative — конкурент, регулятор) сегмента не требует, не флагуем.

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
через колонку `business-problem` — не тащи цели чужих проблем.

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
`business-problem`).

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
**Destination:** `docs/projects/<slug>/capability/<surface>.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** оба слоя существуют; у проекта есть поверхность
`<surface>` в реестре с файлом возможностей.

**Что искать:**
- `warning`: механика ценности (`value-mechanics`) графа сегмента,
  обслуживаемого продуктом, не реализованная ни одной capability
  этой поверхности («механика без capability» — выведенный из графа
  кандидат ценности не дошёл до поверхности).
- `hint`: capability поверхности, не выводимая ни из одной механики
  ценности (продукт умеет то, что не подсказано разведкой — проверить
  обоснованность).

**Промпт-добавка:**
```
value-mechanics — какие из 11 механик создания ценности граф работ
открывает (кандидаты ценности, слой ajtbd); capability/<surface>.md — что
поверхность <surface> продукта <slug> умеет. Механика ценности — это
КАНДИДАТ в capability.

Скоупь механики к сегментам, которые продукт обслуживает (через пользователей
проекта ↔ сегменты графа). Сопоставляй только с возможностями ЭТОЙ
поверхности; та же механика может быть реализована на другой поверхности —
её ловит агент той поверхности.

Для каждой механики: реализована ли она хотя бы одной capability этой
поверхности? Не реализована ни на одной поверхности — warning («механика
без capability»; не флагай, если механика очевидно относится к другой
поверхности). Capability без механики-якоря — hint (возможно, обоснована
иначе; не error).
```

## bet-capability

**Source:** `docs/swot/bet.md`, `goal.md` (только ставки/цели
проблем, которые закрывает проект).
**Destination:** `docs/projects/<slug>/capability/<surface>.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** оба слоя существуют; у проекта непустой
`addresses-problem` и есть поверхность `<surface>` с файлом возможностей.

**Что искать:**
- `warning`: ставка/цель (доведённая до карты) проблемы, которую
  закрывает проект, не реализуемая ни одной capability ни на одной
  поверхности этого продукта (стратегия без продуктового воплощения).
- `hint`: capability поверхности без связи с какой-либо ставкой/целью
  проблем проекта (продукт умеет то, что не служит закрываемой проблеме).

**Промпт-добавка:**
```
bet/goal — стратегический шаг; capability/<surface>.md — что поверхность
<surface> продукта <slug> умеет. Скоупь ставки/цели к проблемам этого
проекта (колонка `business-problem`).

ВАЖНО: ставку/цель проблемы могут реализовывать РАЗНЫЕ проекты И разные
поверхности одного проекта — воплощение в capability ищи на ЭТОЙ
поверхности; отсутствие здесь не error, а warning (возможно, её несёт
другая поверхность того же проекта или соседний проект, закрывающий ту же
проблему — не флагай, если очевидно покрыто другой поверхностью). Для
каждой capability этой поверхности: какой ставке/цели его проблем она
служит? Не служит ни одной — hint.
```

## user-who

**Source:** `docs/projects/<slug>/user.md` (корневой, кросс-поверхностный).
**Destination:** `docs/projects/<slug>/interface/<surface>/who.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** оба слоя существуют; у проекта есть поверхность
`<surface>` с папкой интерфейса.

**Что искать:**

- `error`: who **этой поверхности**, который не соответствует **ни одной**
  user проекта (включая системных акторов в who.md — они допустимы как
  «намеренное исключение», но всё равно должны иметь связь с интересами
  какой-то user).
- `warning`: user, которую `interface/<surface>/who.md` не несёт ни одной
  ролью, хотя по jobs/context она явно работает через эту поверхность
  (поверхность обслуживает user, а роли под него нет). Если user работает
  через другую поверхность — это норма, не флагать.
- `warning`: user, под которую who этой поверхности покрывает только
  **часть** jobs-to-be-done. Если у user на этой поверхности 3 jobs, а who
  участвует только в одном — намёк, что нужны ещё роли.

**Промпт-добавка:**

```
Сопоставь user (корневой файл проекта <slug>, кросс-поверхностный) и who
ПОВЕРХНОСТИ <surface> (docs/projects/<slug>/interface/<surface>/who.md)
семантически. User — это "кто адресат боли продукта" (один на весь
проект). Who — "роль, выполняющая шаг бизнес-процесса НА ЭТОЙ
поверхности". Связь не структурная: одна user может развернуться в
несколько who (например, user "медсестра партнёрской клиники" → who:
nurse-partner, nurse-partner-senior), и в несколько поверхностей.

User обслуживается этой поверхностью, если она названа в surface.user
поверхности <surface> ИЛИ по jobs/context работает через неё. Для такой
user: несёт ли её хоть одно who этой поверхности? Если нет — warning
(поверхность для user без роли). User, работающая только через ДРУГУЮ
поверхность, — не флаг: её несёт who той поверхности (свой агент).

Для каждого who этой поверхности: какой user он принадлежит? Нет ни одной
— error. Системные акторы (scheduler, external-svc) — допустимо без user,
но обоснуй системный интерес.

Используй user.jobs / pains / context и who.description / соседние
situation.action для сопоставления. В finding указывай project и surface.
```

## capability-situation

**Source:** `docs/projects/<slug>/capability/<surface>.md`.
**Destination:** `docs/projects/<slug>/interface/<surface>/situation.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть поверхность `<surface>` с файлом
возможностей и папкой интерфейса.

**Что искать:**

- `error`: capability `stable` этой поверхности, под которую в
  `interface/<surface>/` **нет ни одной ситуации**, реализующей действие.
  Capability — это «что продукт умеет», situation — конкретное UX-проявление
  этого умения **на той же поверхности**.
- `warning`: capability имеет одну-две ситуации, в то время как ожидается
  больше (capability сложная, например «согласовать слот» — обычно
  3-5 ситуаций).
- `hint`: ситуация в `interface/<surface>/`, у которой нет ясной
  capability-якоря в `capability/<surface>.md`. Возможно, нужна
  capability, либо ситуация не нужна.

**Промпт-добавка:**

```
Оба слоя — ПОВЕРХНОСТИ <surface> проекта <slug>:
capability/<surface>.md и interface/<surface>/situation.md. Capability —
устойчивое умение продукта на этой поверхности в языке user. Situation —
конкретная UX-точка той же поверхности, где умение реализуется
(кто/когда/что/ради чего/с какими данными). Поверхности изолированы:
сопоставляй только в пределах <surface>.

Для каждой capability этой поверхности: какие situation её реализуют?
Сопоставь по смыслу действий и goal.

Для каждой situation: к какой capability той же поверхности она
относится? Если ни к одной — hint (либо новая capability, либо ситуация
не нужна). В finding указывай project и surface.
```

## capability-domain

**Source:** `docs/projects/<slug>/capability/<surface>.md`.
**Destination:** `docs/projects/<slug>/domains/` (если есть;
surface-агностичны).
**Скоуп:** по проекту × поверхность.
**Применим если:** `docs/projects/<slug>/domains/` существует; у проекта
есть поверхность `<surface>` с файлом возможностей.

**Что искать:**

- `error`: capability `stable` этой поверхности, под которую в `domains/`
  проекта нет бизнес-домена / агрегата. Capability не существует в коде.
- `warning`: бизнес-домен в `domains/` проекта, у которого не находится
  capability-якорь ни на одной поверхности. Технический домен (auth,
  logging) — норма; бизнес-домен (referrals, billing) без якоря — пробел.
  (Поскольку домены surface-агностичны, обратную сторону — домен без
  capability — точнее видит агент любой поверхности; не дублируй её
  агрессивно, флагай только домен, который явно не покрыт capability этой
  поверхности и по смыслу должен бы.)

**Промпт-добавка:**

```
Source — capability/<surface>.md (умения поверхности <surface> проекта
<slug>); destination — docs/projects/<slug>/domains/ (бизнес-код,
ОБЩИЙ для всех поверхностей: домены партиционируются по bounded-context,
не по surface).

Для каждой capability этой поверхности: есть ли в domains/ проекта
агрегат или use-case, реализующий бизнес-логику? Сопоставь по семантике,
не имени файла. Одна доменная модель обслуживает все поверхности — домен
может нести capability и этой поверхности, и других.

Технические домены (auth, audit, logging) могут не иметь capability-якоря
— отметь, не помечай ошибкой. В finding указывай project и surface.
```

## surface-zone

**Source:** `docs/projects/<slug>/surface.md` (реестр, строка `<surface>`).
**Destination:** `docs/projects/<slug>/interface/<surface>/zone.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть поверхность `<surface>` с папкой
интерфейса (`interface/<surface>/`).

**Что искать:**

- `error`: surface `stable`, у которой папка `interface/<surface>/`
  существует, но `zone.md` **пуст** — поверхность без единой зоны (мёртвый
  интерфейс).
- `warning`: зоны поверхности по смыслу не покрывают её user или
  основной job-to-be-done (поверхность объявлена, но зоны не образуют
  целостного UX для того, кого она обслуживает).
- `hint`: зона, чьё `description` по смыслу относится к другой поверхности
  (зона заведена «не в той» папке поверхности).

**Промпт-добавка:**

```
Source — строка <surface> реестра surface.md проекта <slug>;
destination — docs/projects/<slug>/interface/<surface>/zone.md. Структурная
привязка зон к поверхности уже даёт папка (за неё отвечает
/interface-audit и /project-audit). Здесь — СЕМАНТИКА: образуют ли зоны
этой поверхности целостный UX для user, которого surface.user обслуживает.

Surface существует и stable, но zone.md этой поверхности пуст — error.
Зоны не покрывают user/основной job поверхности — warning. Зона, по
description явно относящаяся к другой поверхности (заведена не в той
папке), — hint. В finding указывай project и surface.
```

## surface-screen

**Source:** `docs/projects/<slug>/surface.md` (реестр, строка `<surface>`)
+ `docs/projects/<slug>/interface/<surface>/`.
**Destination:** `docs/projects/<slug>/screens/<surface>/` (если есть).
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть поверхность `<surface>` и папка
`screens/<surface>/`.

**Что искать:**

- `error`: surface `stable` с наполненным `interface/<surface>/`, у которой
  папка `screens/<surface>/` существует, но пуста (нет ни одного flow /
  screen) — поверхность с UX, но без композиции экранов.
- `warning`: ситуации/блоки `interface/<surface>/` без отражения в
  `screens/<surface>/` (UX-точки поверхности не дошли до композиции экранов).
- `hint`: screen / flow в `screens/<surface>/`, не привязанный по смыслу к
  поверхности (заведён не в той папке).

**Промпт-добавка:**

```
Source — строка <surface> реестра surface.md + UX той же поверхности
docs/projects/<slug>/interface/<surface>/; destination —
docs/projects/<slug>/screens/<surface>/ (композиция UX, ассеты,
hi-fi-материал ТОЙ ЖЕ поверхности). Поверхности изолированы — сопоставляй
в пределах <surface>.

Папка screens/<surface>/ существует, но пуста при наполненном
interface/<surface>/ — error. Ключевые ситуации/блоки интерфейса
поверхности без композиции в screens этой поверхности — warning. По
смыслу — посмотри shell/flow/screen-описания. В finding указывай project и
surface.
```

## integration-domain

**Source:** `docs/projects/<slug>/integration.md` (`## Провайдеры`, чья
колонка `surface` содержит `<surface>`; их `## Функции`).
**Destination:** `docs/projects/<slug>/domains/` (если есть;
surface-агностичны): use-case `## Dependencies` колонки `integration` +
`functions`; клиенты `_shared/integrations/<integration>/` (`## Functions`).
**Скоуп:** по проекту × поверхность.
**Применим если:** `docs/projects/<slug>/domains/` существует; у проекта
есть поверхность `<surface>`.

Сверяет **цепочку функции**: бизнес-каталог (`## Функции` integration.md) ↔
конкретный клиент (`_shared/integrations/<integration>/`) ↔ потребление
(use-case `functions`).

**Что искать:**

- `error`: integration `stable`, обслуживающая `<surface>`, под которую в
  `domains/` нет клиента `_shared/integrations/<integration>/` и ни одного
  use-case с этим `integration` в `## Dependencies`. Интеграция объявлена, но
  в коде её нет.
- `error`: функция `## Функции` с `direction: out`, у которой **нет пары** в
  `## Functions` клиента `_shared/integrations/<integration>/` (тот же
  `slug`). Бизнес объявил функцию, но клиент её не реализует.
- `error`: `functions`-запись в use-case (`<integration>.<fn-slug>`), которой
  **нет** ни в `## Функции` провайдера, ни в `## Functions` клиента —
  висячее потребление.
- `warning`: функция клиента (`out`) без потребителя — ни один use-case не
  держит её в `functions` (мёртвая функция клиента).
- `warning`: функция `## Функции` с `direction: in` без **обслуживающего**
  use-case (нет use-case с подходящим `Actor`, принимающего этот вызов).
- `warning`: порт use-case с непустым `integration`, чья запись в
  integration.md не несёт ни одну поверхность в `surface` (рассинхрон).

**Промпт-добавка:**

```
Source — integration.md проекта <slug> (## Провайдеры + ## Функции), СКОУПЬ
к провайдерам, чья `surface` содержит <surface>. Destination — domains/:
клиенты _shared/integrations/<integration>/ (## Functions) и use-case
`## Dependencies` (колонки `integration` + `functions`).

Сверяй цепочку каждой функции (общий slug на трёх высотах):
- функция ## Функции (out) без пары в ## Functions клиента — error;
- функция-потребление в use-case (functions = <integration>.<fn-slug>) без
  строки в ## Функции провайдера или в клиенте — error;
- функция клиента (out) без потребителя (ни один use-case не держит её в
  functions) — warning;
- функция ## Функции (in) без обслуживающего use-case (Actor принимает) —
  warning;
- провайдер, обслуживающий <surface>, без клиента и без use-case — error.

Внутренняя инфра (integration = `—`, functions = `—`) — норма, не флаг.
Транспорт (HTTP/endpoint) держит клиент _shared/, не use-case — если
сигнатура протекла в use-case.Steps, это warning. В finding указывай
project и surface.
```

## constraint-surface

**Source:** `docs/projects/<slug>/constraint.md` (корневой).
**Destination:** `docs/projects/<slug>/surface.md` (строка `<surface>`),
`docs/projects/<slug>/integration.md` (интеграции, чей `surface` содержит
`<surface>`).
**Скоуп:** по проекту × поверхность.
**Применим если:** product-слой проекта существует; у проекта есть
поверхность `<surface>`.

**Что искать:**

- `warning`: constraint, который семантически касается поверхности
  `<surface>` (или интеграции, обслуживающей её), но эта связь нигде не
  упомянута. Например, `pdn-consent` (152-ФЗ) должен быть связан с
  web-поверхностью, где есть PII.
- `hint`: поверхность `<surface>` с user, обрабатывающая PII / финансы /
  здоровье, но без относящегося constraint. Возможно, пропустили.

**Промпт-добавка:**

```
Constraint (корневой constraint.md проекта <slug>) — обязательное правило
(закон / SLA / контракт). Скоупь к ПОВЕРХНОСТИ <surface>: строка <surface>
реестра surface.md + интеграции, чья колонка `surface` содержит <surface>.

Для каждого constraint, по смыслу касающегося этой поверхности или её
интеграций: видна ли связь (в description constraint / surface /
integration)? Не видна — warning (152-ФЗ → web с PII; PCI-DSS →
integration с платежами на этой поверхности; HIPAA → surface с
медданными).

Поверхность <surface> с user, обрабатывающая PII / финансы / здоровье,
без относящегося constraint — hint. Не флагай constraint, относящийся к
другой поверхности (его ловит её агент). В finding указывай project и
surface.
```

## market-capability

**Source:** `docs/projects/<slug>/market.md` (корневой,
кросс-поверхностный).
**Destination:** `docs/projects/<slug>/capability/<surface>.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** оба наполнены; у проекта есть поверхность `<surface>`
с файлом возможностей.

**Что искать:**

- `hint`: market-аналог покрывает возможность, которой у нас **нет** на
  этой поверхности. Сигнал: либо нужна эта capability, либо явно decide,
  что вне scope.
- `hint`: возможности этой поверхности, которых market-аналог не покрывает
  (мы делаем то, чего конкурент не умеет). Полезно для позиционирования.
- `warning`: market.description упоминает «direct competitor», но
  пересечение с capabilities этой поверхности — почти полное. Возможно,
  недо-дифференциация.

**Промпт-добавка:**

```
Market (корневой market.md проекта <slug>) — рыночные аналоги продукта.
Capability/<surface>.md — умения ПОВЕРХНОСТИ <surface>. Сопоставляй
рыночные аналоги с возможностями именно этой поверхности (mobile-аналог —
с capability mobile-поверхности, и т.д.).

Для каждого market-аналога: что он покрывает из возможностей этой
поверхности? Что у него есть, чего у нас на этой поверхности нет (гэп)?
Что у нас на этой поверхности есть, чего у него нет (дифференциация)?

Возвращай hints / warnings — материал для аналитика, не error. В finding
указывай project и surface.
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

## stakeholder-subject

**Source:** `docs/business/stakeholder.md` (`manifests-as`, `attitude`,
`motivation`).
**Destination:** `docs/hypothesis-map/subject.md`.
**Скоуп:** один раз (business ↔ hypothesis-map).
**Применим если:** оба наполнены.

**Что искать:**
- `error`: `stakeholder.manifests-as` с префиксом `subject:` указывает на
  субъекта, которого нет в `subject.md`.
- `warning`: лицо и его субъект (через `manifests-as`) несут **рассинхрон
  мотиваций** — один человек, два разных портрета.
- `hint`: властный внутренний `blocker`/`skeptic` стейкхолдер, по смыслу
  противодействующий, не отражённый как `negative`-субъект там, где его
  поведение двигает метрику (кандидат в `subject.kind: negative`).

**Промпт-добавка:**
```
stakeholder — человек-решатель ВНУТРИ заказчика; subject — носитель
поведения, двигающего метрику. Один человек может быть обоими (через
stakeholder.manifests-as = subject:<slug>); властный внутренний блокер ≈
negative-субъект.

Прямая сторона: каждый manifests-as subject:<slug> резолвится в реальный
subject? Нет — error. Согласованность мотиваций лица и субъекта — рассинхрон
warning. Властный blocker/skeptic стейкхолдер без negative-субъекта там,
где он двигает метрику, — hint. НЕ путай: это РАЗНЫЕ сущности, связь
семантическая.
```

## stakeholder-factor

**Source:** `docs/business/stakeholder.md` (`attitude`, `power`).
**Destination:** `docs/swot/factor.md`.
**Скоуп:** один раз (business ↔ swot).
**Применим если:** оба наполнены.

**Что искать:**
- `hint`: властный `champion` (`power: high`, `attitude: champion`), не
  отражённый ни одним SWOT-фактором — сильный внутренний союзник как
  сила-фактор.
- `hint`: властный `blocker`/`skeptic` (`power: high`), не отражённый ни
  одним фактором — внутреннее сопротивление как слабость/угроза-фактор.

**Промпт-добавка:**
```
Люди-решатели часто И ЕСТЬ внутренние факторы SWOT: властный champion —
сила, властный blocker/skeptic — слабость/угроза. Для властных
стейкхолдеров (power=high) с выраженной стойкой: отражён ли каждый
соответствующим factor? Не отражён — hint (кандидат в фактор). Связь
семантическая, не slug; это материал для аналитика, не error.
```

## stakeholder-strategy

**Source:** `docs/business/stakeholder.md` (`strategic-stance`, `power`).
**Destination:** `docs/swot/bet.md`, `docs/hypothesis-map/goal.md`.
**Скоуп:** один раз (business ↔ swot/hypothesis-map).
**Применим если:** есть стейкхолдеры со `strategic-stance` и есть ставки/цели.

**Что искать:**
- `warning`: `bet`/`goal`, **противоречащий** стратегической стойке
  властного стейкхолдера (`power: high`) — стратегия идёт против ключевого
  лица, которое будет её санкционировать/финансировать (стратегический риск:
  стратегия в вакууме от людей).
- `hint`: властный стейкхолдер, чью стойку **не несёт ни одна** ставка/цель
  — незадействованная опора (мог бы стать чемпионом, но стратегия мимо его
  взглядов).

**Промпт-добавка:**
```
strategic-stance — куда властное лицо хочет/не хочет движения бизнеса; bet
(SWOT) и goal (Карта гипотез) — стратегические шаги. Стратегия не должна
противоречить стойке тех, кто её санкционирует/финансирует, иначе она
мертва на старте.

Для каждой ставки/цели: не бьёт ли она в стойку какого-либо властного
(power: high) стейкхолдера (по смыслу — противоречит тому, что он
поддержал бы)? Бьёт — warning (стратегия против ключевого лица).

Обратно: властный стейкхолдер со strategic-stance, чью линию не несёт ни
одна ставка/цель — hint (незадействованная опора). Скоупь к властным лицам;
противоречие со слабым лицом — НЕ finding. Связь семантическая, не slug.
```

## capability-hypothesis

**Source:** `docs/projects/<slug>/capability/<surface>.md` (поле
`hypotheses`).
**Destination:** `docs/hypothesis-map/hypothesis.md` (по проблемам, которые
закрывает проект).
**Скоуп:** по проекту × поверхность.
**Применим если:** оба слоя существуют; у проекта непустой
`addresses-problem` и есть поверхность `<surface>` с файлом возможностей.

**Что искать:**
- `error`: `capability.hypotheses` (в `capability/<surface>.md`) ссылается
  на гипотезу, которой нет в `docs/hypothesis-map/` (ребро бьёт в
  несуществующую сущность).
- `hint`: гипотеза проблемы, которую закрывает проект, не реализуемая ни
  одной capability ни на одной поверхности продукта (стратегия без
  продуктового воплощения — возможно, её несёт соседний проект).

**Промпт-добавка:**
```
capability.hypotheses (поле в capability/<surface>.md — возможностях
поверхности <surface> проекта <slug>) — авторское ребро продукт →
hypothesis-map: возможность реализует гипотезу. Скоупь гипотезы к проблемам
проекта (колонка `business-problem`).

Прямая сторона: каждый ref hypotheses этой поверхности резолвится в
реальную hypothesis? Нет — error. Обратная: гипотеза проблемы проекта без
реализующей capability на ЭТОЙ поверхности — hint (может нести другая
поверхность того же проекта или соседний проект; не флагай агрессивно).
Связь семантическая. В finding указывай project и surface.
```

## capability-job

**Source:** `docs/projects/<slug>/capability/<surface>.md` (поле `jobs`).
**Destination:** `docs/ajtbd/job.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** оба слоя существуют; у проекта есть поверхность
`<surface>` с файлом возможностей.

**Что искать:**
- `error`: `capability.jobs` (в `capability/<surface>.md`) ссылается на
  работу, которой нет в `docs/ajtbd/job.md`.
- `hint`: Core/Big Job обслуживаемого сегмента без capability ни на одной
  поверхности, прямо в неё целящей (`capability.jobs`) — дополняет
  `mechanic-capability` (там через механики ценности, здесь — прямое ребро).

**Промпт-добавка:**
```
capability.jobs (поле в capability/<surface>.md — возможностях поверхности
<surface> проекта <slug>) — прямое авторское ребро продукт → ajtbd:
возможность целит в работу сегмента (в дополнение к выводимому через
job-graph.value-mechanics).

Прямая сторона: каждый ref jobs этой поверхности резолвится в реальный
job? Нет — error. Обратная: Big/Core Job обслуживаемого сегмента без
прямо целящей capability на ЭТОЙ поверхности — hint (может нести другая
поверхность; не флагай агрессивно). Связь семантическая. В finding указывай
project и surface.
```

## situation-job

**Source:** `docs/projects/<slug>/interface/<surface>/situation.md` (поле
`jobs`).
**Destination:** `docs/ajtbd/job.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** оба слоя существуют; у проекта есть поверхность
`<surface>` с папкой интерфейса.

**Что искать:**
- `error`: `situation.jobs` (в `interface/<surface>/situation.md`)
  ссылается на работу, которой нет в `docs/ajtbd/job.md`.
- `hint`: UX-ситуация поверхности, обслуживающая работу сегмента, без
  проставленного `jobs` (связь полезна, но не обязательна).

**Промпт-добавка:**
```
situation.jobs (поле в interface/<surface>/situation.md поверхности
<surface> проекта <slug>) — авторское ребро interface → ajtbd: UX-шаг
обслуживает работу сегмента. Прямая сторона: каждый ref резолвится в
реальный job? Нет — error. Мягкое ребро (опц.), прочерк — норма; не требуй
его. В finding укажи project и surface.
```

## situation-hypothesis

**Source:** `docs/projects/<slug>/interface/<surface>/situation.md` (поле
`hypotheses`).
**Destination:** `docs/hypothesis-map/hypothesis.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** оба слоя существуют; у проекта есть поверхность
`<surface>` с папкой интерфейса.

**Что искать:**
- `error`: `situation.hypotheses` (в `interface/<surface>/situation.md`)
  ссылается на гипотезу, которой нет в `docs/hypothesis-map/`.
- `hint`: UX-ситуация поверхности, которая по смыслу проверяет/обслуживает
  гипотезу, без проставленного `hypotheses`.

**Промпт-добавка:**
```
situation.hypotheses (поле в interface/<surface>/situation.md поверхности
<surface> проекта <slug>) — авторское ребро interface → hypothesis-map:
UX-шаг проверяет/обслуживает гипотезу. Прямая сторона: каждый ref
резолвится в реальную hypothesis? Нет — error. Мягкое ребро (опц.),
прочерк — норма. В finding укажи project и surface.
```

## surface-capability

**Source:** `docs/projects/<slug>/surface.md` (реестр, строка `<surface>`).
**Destination:** `docs/projects/<slug>/capability/<surface>.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть поверхность `<surface>` в реестре.

Структурную часть хребта (файл `capability/<surface>.md` без поверхности в
реестре; поверхность реестра без файла возможностей) уже ловит
`/project-audit`. Здесь — **семантика**: для кого поверхность объявлена и
кому её возможности на деле ценны.

**Что искать:**
- `error`: поверхность реестра `stable`, чей файл `capability/<surface>.md`
  существует, но **пуст** (нет ни одной возможности) — поверхность без
  единого умения для своего user.
- `warning`: возможность в `capability/<surface>.md`, чьи `user` **не
  входят** в `surface.user` этой поверхности (возможность даётся не тем,
  кого поверхность обслуживает).
- `hint`: user из `surface.user`, которому на этой поверхности не ценна ни
  одна возможность (поверхность объявлена для user, но умений под него
  нет).

**Промпт-добавка:**
```
Source — строка <surface> реестра surface.md проекта <slug> (с колонкой
`user` — кого поверхность обслуживает); destination —
capability/<surface>.md (возможности этой поверхности, у каждой колонка
`user`). Связь capability → поверхность СТРУКТУРНАЯ (файл лежит в своей
поверхности — это держит /project-audit); ты проверяешь СМЫСЛ: совпадают
ли адресаты.

Файл capability/<surface>.md пуст при stable-поверхности — error
(поверхность без умений). Возможность, чьи user не пересекаются с
surface.user поверхности — warning (умение «не тем», кого поверхность
обслуживает). User из surface.user без единой ценной ему возможности —
hint. Связь семантическая (user сопоставляй по смыслу, не только по slug).
В finding указывай project и surface.
```

## integration-crossproject

**Source:** `docs/projects/<slug>/integration.md` (`## Провайдеры` с
`target: sibling-project` + их `## Функции`).
**Destination:** `docs/projects/project-map.md` (рёбра) +
`docs/projects/<sibling>/` (обратная сторона: его `integration.md` +
обслуживающие `domains/<ctx>/use-cases/*`) +
`docs/projects/<slug>/domains/` (наш клиент `_shared/integrations/<slug>/` +
use-case `functions`).
**Скоуп:** по проекту (пара `проект × lens`; межпроектный).
**Применим если:** у проекта есть хотя бы одна `integration` с
`target: sibling-project`, **или** в `project-map.md` есть ребро с
`from-project = <slug>`.

Сверяет межпроектный стык **в обе стороны**: продуктовая интеграция
(`integration.md`, авторская сторона) ↔ граф стыков (`project-map.md`,
бизнес-язык) ↔ наше техническое воплощение (клиент `_shared/` + функции в
use-case) ↔ **обслуживающая сторона у соседа** (его use-case, принимающий
наш вызов, или его исходящая функция). Дополняет `projectmap-reciprocity`.

**Что искать:**
- `error`: `integration` с `target: sibling-project = <X>`, для которой в
  `project-map.md` **нет ребра** — стык объявлен, но не сведён в карту.
- `error`: `integration.sibling-project` указывает на проект, у которого
  **нет каталога** `docs/projects/<X>/`.
- `error`: наша `out`-функция к соседу (`## Функции` `direction: out`,
  провайдер `target: sibling-project`) без **обслуживающего use-case у
  соседа** `<X>` — мы зовём функцию, которую сосед не обслуживает
  (caller есть, callee нет).
- `warning`: ребро `project-map.md` (`from-project = <slug>`) **без опорной**
  `integration` с `target: sibling-project` — карта без авторской стороны.
- `warning`: у соседа `<X>` **нет обратной** интеграции/функции на этот
  проект при `duplex`/входящем направлении ребра (асимметрия стыка).
- `warning`: `integration` с `target: sibling-project` без клиента
  `_shared/` и без use-case с её функциями (стык без воплощения, если есть
  `domains/`).
- `warning`: техническая деталь (сигнатура функции, endpoint, имя use-case)
  просочилась в `project-map.md` — карта должна быть на бизнес-языке.

**Промпт-добавка:**
```
Межпроектный стык согласован В ОБЕ СТОРОНЫ: (1) авторская — integration.md
проекта <slug> (target: sibling-project + ## Функции); (2) граф — ребро в
docs/projects/project-map.md (бизнес-язык, via → integration:<slug>); (3)
наша техника — клиент _shared/integrations/<slug>/ + use-case functions; (4)
сторона соседа <X> — обслуживающий use-case (наш out ↔ его принимающий
Actor) или его исходящая функция.

Прочитай integration.md проекта <slug> (фильтр target: sibling-project +
функции), docs/projects/project-map.md, перечень каталогов docs/projects/,
integration.md соседа <X> и его domains/use-cases (если есть), domains/
проекта <slug> (клиент _shared/ + functions в use-case).

Найди рассинхрон сторон:
- integration target: sibling-project без ребра в project-map — error;
- sibling-project на несуществующий проект — error;
- наша out-функция к соседу без обслуживающего use-case у соседа — error
  (caller без callee);
- ребро project-map (from=<slug>) без опорной integration — warning;
- у соседа нет обратной интеграции/функции при duplex/входящем — warning;
- integration sibling-project без клиента _shared/ и потребления — warning;
- техническая деталь (сигнатура/endpoint/use-case) в project-map — warning
  (карта на бизнес-языке).

Связь семантическая, не только slug-матч. В finding ставь project = <slug>
(проект-инициатор), business-problem = null.
```

## projectmap-reciprocity

**Source:** `docs/projects/project-map.md` (все рёбра).
**Destination:** перечень каталогов `docs/projects/` (какие проекты
существуют) + `integration.md` каждого упомянутого проекта.
**Скоуп:** один раз (верхнеуровневый, над всей картой стыков).
**Применим если:** `docs/projects/project-map.md` непуст.

Проверяет **осмысленность графа стыков как целого** — в отличие от
`integration-crossproject`, который скоупится к одному проекту-инициатору.

**Что искать:**
- `error`: ребро, чей `from-project` или `to-project` — slug
  несуществующего проекта (нет каталога `docs/projects/<slug>/`, либо это
  `_template`).
- `error`: ребро-самоссылка (`from-project == to-project`).
- `warning`: **встречная пара рёбер** вместо `duplex` — два ребра
  `A→B` (`out`) и `B→A` (`out`/`in`) по одному и тому же payload, которые
  должны быть одним ребром `direction: duplex` (дубль-встречное ребро).
- `hint`: ребро с `via`, не резолвящимся ни в одну реальную
  `integration`/`event`/`domain-port` проекта-инициатора (карта ссылается
  «в пустоту»).

**Промпт-добавка:**
```
project-map.md — граф стыков между продуктами одного бизнеса. Проверь
осмысленность КАЖДОГО ребра и пар рёбер:

- from-project / to-project — реальные каталоги docs/projects/<slug>/ (не
  _template)? Нет — error.
- from-project == to-project (самоссылка)? error.
- есть ли встречная пара A→B и B→A по одному payload, которая должна быть
  одним duplex-ребром? warning (дубль вместо duplex).
- via резолвится в реальную integration / event / domain-port
  проекта-инициатора? Нет — hint.

Это верхнеуровневый угол: project = null в findings, business-problem =
null. Согласованность ребра с конкретной integration проекта-инициатора
глубже проверяет integration-crossproject (по проекту) — здесь не дублируй
её, держись уровня графа.
```

## dataitems-crosssurface

**Source / Destination:** `docs/projects/<slug>/interface/<surface>/data-items.md`
**всех** поверхностей проекта (один агент читает их все сразу).
**Скоуп:** по проекту (один агент на проект, сразу по всем поверхностям).
**Применим если:** у проекта ≥2 папки поверхностей с `data-items.md`.

Реестр `data-items` **surface-локален** (правило «один датум — один slug»
действует в пределах поверхности): один и тот же бизнес-датум на web и в
боте — **намеренно** две записи в разных папках. Этот угол ищет не сам
факт дубля (он ожидаем), а **смысловые расхождения** словаря данных между
поверхностями.

**Что искать:**
- `hint`: один и тот же бизнес-датум в `data-items.md` разных поверхностей
  под **разными slug** (словарь данных расходится между поверхностями —
  стоит согласовать имена).
- `hint`: один и тот же датум под одним slug, но с **рассогласованными
  описаниями** на разных поверхностях (один датум — два разных смысла).

**Промпт-добавка:**
```
Прочитай data-items.md ВСЕХ папок поверхностей проекта <slug>
(docs/projects/<slug>/interface/*/data-items.md). Реестр data-items
surface-локален: один датум на разных поверхностях — это НАМЕРЕННО разные
записи (web и бот воплощают его по-разному). НЕ флагай сам факт раздельных
записей.

Ищи только СМЫСЛОВЫЕ расхождения словаря данных между поверхностями:
- один бизнес-датум под разными slug на разных поверхностях — hint
  (согласовать имена);
- один slug с противоречивыми description на разных поверхностях — hint
  (один датум — два смысла).

Всё — hint (консистентность словаря, не ошибка). В finding ставь project =
<slug>, surface не указывай (угол охватывает все поверхности сразу).
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
10. `stakeholder-subject` (business → hypothesis-map: лицо ↔ субъект через
    manifests-as; властный блокер ≈ negative-субъект)
11. `stakeholder-factor` (business → swot: властный champion/blocker как
    фактор)
12. `stakeholder-strategy` (business → swot/hypothesis-map: стойка властного
    лица ↔ bet/goal — стратегия не против ключевого человека)
13. `projectmap-reciprocity` (граф стыков: осмысленность рёбер project-map)

**По каждому проекту, пары `проект × lens`** (для каждого `<slug>` из
`docs/projects/`, кроме `_template`; цели — корневые kind продукта
`vision`/`user`/`integration`):

14. `goal-vision` (проблема → продукт; скоуп к проблемам проекта)
15. `subject-user` (проблема → продукт; скоуп к проблемам проекта)
16. `segment-user` (ajtbd → продукт)
17. `job-vision` (ajtbd → продукт: Big/Core Job ↔ vision.Success)
18. `segmentproblem-vision` (ajtbd → продукт: трение ↔ vision.Problem)
19. `integration-crossproject` (межпроектный: integration ↔ project-map ↔
    domains-порт ↔ обратная сторона соседа; если у проекта есть стыки
    `target: sibling-project` или ребро в project-map)

**По каждому проекту, тройки `проект × поверхность × lens`** (для каждого
`<slug>` и каждой поверхности `<surface>` из его `surface.md`; source ИЛИ
destination — per-surface артефакт):

20. `surface-capability` (foundation: реестр поверхности ↔ её возможности)
21. `mechanic-capability` (ajtbd → продукт: механика ценности ↔ capability
    поверхности)
22. `bet-capability` (проблема → продукт; скоуп к проблемам проекта)
23. `capability-hypothesis` (продукт → hypothesis-map: capability.hypotheses)
24. `capability-job` (продукт → ajtbd: capability.jobs)
25. `user-who` (foundation, продукт → interface поверхности)
26. `surface-zone` (foundation: реестр поверхности ↔ её зоны)
27. `capability-situation` (foundation: возможности ↔ ситуации поверхности)
28. `situation-job` (interface поверхности → ajtbd: situation.jobs)
29. `situation-hypothesis` (interface поверхности → hypothesis-map:
    situation.hypotheses)
30. `market-capability` (рынок ↔ возможности поверхности; часто hints)
31. `constraint-surface` (ограничение ↔ поверхность/её интеграции)
32. `capability-domain` (если у проекта есть `domains/`; возможности
    поверхности ↔ домены)
33. `integration-domain` (если у проекта есть `domains/`; интеграции
    поверхности ↔ домены-порты)
34. `surface-screen` (если у проекта есть `screens/<surface>/`)

**По каждому проекту, один агент на проект сразу по всем поверхностям:**

35. `dataitems-crosssurface` (консистентность словаря данных между
    поверхностями; только если у проекта ≥2 поверхностей)

Полный рой = `13 верхнеуровневых + Σ по проектам (пары проект×lens +
тройки проект×поверхность×lens применимых углов + dataitems-crosssurface
для мультиповерхностных проектов)`.

`--quick` запускает по каждому проекту **× каждой поверхности** три
foundation-угла продукт↔interface (`user-who`, `capability-situation`,
`surface-zone` — все per-surface, раскрываются в тройки), плюс
`addresses-problem-bizproblem` один раз. Для верхних слоёв — `goal-vision`,
`subject-user` (пары по проекту) как быстрый upstream-чек.
