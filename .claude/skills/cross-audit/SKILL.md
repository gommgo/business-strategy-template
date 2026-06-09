---
name: cross-audit
description: "Сквозной семантический аудит консистентности между слоями документации — business (профиль + реестр проблем business-problem) ↔ ajtbd ↔ swot ↔ hypothesis-map ↔ (множество проектов docs/projects/<slug>/: project ↔ interface ↔ domain ↔ screen, партиционированных по поверхности surface) + межпроектные стыки (project-map). Запускает рой агентов параллельно: верхнеуровневые углы один раз (factor ↔ business, current-metric ↔ metric, addresses-problem ↔ business-problem, ajtbd segment-problem ↔ business-problem, ajtbd segment ↔ subject, ajtbd solution ↔ competitor/offering, business offering/channel ↔ ajtbd segment, проспективная согласованность market-maturity ↔ served, провенанс from-project ↔ проект, стейкхолдер ↔ субъект/фактор/стратегическая стойка, осмысленность графа project-map projectmap-reciprocity); углы с корневыми целями (vision/user/integration) — ПАРАМИ по проекту (goal/metric ↔ vision, subject ↔ user, ajtbd segment ↔ user, job ↔ vision.Success, segment-problem ↔ vision.Problem, integration ↔ соседний проект через project-map); углы с per-surface источником/целью — ТРОЙКАМИ проект×поверхность×lens (surface ↔ capability, value-mechanics ↔ capability/<surface>, bet ↔ capability/<surface>, capability ↔ hypothesis/job, user ↔ who/<surface>, capability ↔ situation/<surface>, surface ↔ zone/<surface>, surface ↔ screen/<surface>, situation ↔ job/hypothesis, capability ↔ domain, integration ↔ domain-порт, constraint ↔ surface/integration, market ↔ capability/<surface>); консистентность словаря данных между поверхностями (dataitems-crosssurface) — один агент на проект. Читает слои + state, ищет семантические тупики — НЕ через slug-валидацию, а смыслом («пользователь без UX-покрытия поверхности», «метрика подана как гарантия», «субъект без пользователя», «механика ценности без capability», «поверхность без возможностей», «зона висит без поверхности», «интеграция к соседнему проекту без ребра в project-map», «проект бьёт в несуществующую проблему»). Не правит, только отчёт. Использовать перед релизом, после крупного апдейта любого слоя, или когда deep-dive-скилы предлагают прогон. Сводный отчёт + список findings; deep-dive по каждому — отдельный шаг руками аналитика."
---

# cross-audit

Сквозной семантический аудит **между слоями** документации. Два верхних
слоя — **общие для всех проектов**, ниже — **множество проектов**, каждый
в своей папке `docs/projects/<project-slug>/`:

- `docs/business/` (профиль бизнеса — profile/offering/channel/competitor/...)
  — общий, один.
- `docs/ajtbd/` (разведка спроса — segment/job/job-graph/solution/segment-problem;
  сегменты по работам + граф работ Advanced JTBD) — общий, один.
- `docs/business/business-problem.md` (**реестр проблем бизнеса** —
  одна строка = одна проблема) — общий, один.
- `docs/swot/` (LinkedSWOT — factor/bet) — общий, один.
- `docs/hypothesis-map/` (Карта гипотез —
  goal/metric/subject/hypothesis/task) — общий, один.
- `docs/projects/project-map.md` (граф межпроектных стыков —
  from-project/to-project/direction/payload/via) — общий, один.
- `docs/projects/<slug>/` (продукт: `vision.md` + реестр-хребет
  `surface.md` + корневые kind `user/integration/boundary/constraint/market`
  + папка возможностей `capability/<surface>.md` по файлу на поверхность)
  — **по одному на проект**.
- `docs/projects/<slug>/interface/<surface>/` (UX —
  who/stage/situation/zone/block/ux-substrate/data-items; **папка на
  поверхность** из реестра `surface.md`) — внутри проекта.
- `docs/projects/<slug>/domains/<ctx>/` (бизнес-домены бэкенда — если
  каталог есть; партиционированы по bounded-context, **surface-агностичны**)
  — внутри проекта.
- `docs/projects/<slug>/screens/<surface>/` (композиция экранов — если
  каталог есть; **папка на поверхность**) — внутри проекта.

**Поверхность (surface) — ось продукта.** Реестр-хребет
`docs/projects/<slug>/surface.md` объявляет поверхности, и их slug'и —
ключи партиционирования трёх слоёв: возможностей (`capability/<surface>.md`),
интерфейса (`interface/<surface>/`) и экранов (`screens/<surface>/`).
Корневые kind продукта (`vision`, `user`, `integration`, `boundary`,
`constraint`, `market`) — кросс-поверхностные, лежат в корне папки проекта;
домены surface-агностичны. Поэтому углы делятся на **пары** (проект × lens,
цель — корневой kind) и **тройки** (проект × поверхность × lens, источник
или цель — per-surface артефакт).

Папка `docs/projects/_template/` — **канон формы, не данные проекта**; в
аудит **не входит** (исключается из перечисления проектов).

Бизнес-проблемы — общий слой, питающий **много** проектов: проблему могут
закрывать несколько проектов, проект — несколько проблем (M:N через
`vision.addresses-problem`). Углы business-problem ↔ продукт скоупятся к
конкретному проекту и учитывают, какие проблемы этот проект закрывает.

Аудит **не валидирует slug** между слоями (связи семантические, см.
`docs/projects/_template/project/README.md`). Аудит читает оба слоя и
спрашивает агентов «в чём смысл сочетается, а в чём расходится» — это
требует LLM, не grep.

`/project-audit` ловит внутренние тупики **внутри одного project-слоя**.
`/interface-audit` — внутри interface. `/swot-audit` ловит
**методологические инварианты** LinkedSWOT (внутри `docs/swot/`),
`/hypothesis-map-audit` — инварианты Карты гипотез (внутри
`docs/hypothesis-map/`), оба в пределах каждой проблемы реестра.
`/ajtbd-audit` ловит
**методологические инварианты** Advanced JTBD (внутри ajtbd, в пределах
каждого сегмента — бандл работ, непрерывность «чтобы», CPR, трение без
решения). Cross-audit — **между слоями**: на содержимое SWOT / гипотез /
графа работ он не лезет, его территория — кросс-**слойные** рёбра.

## Точки входа

| вызов | поведение |
|---|---|
| `/cross-audit` | полный прогон: верхнеуровневые углы один раз + пары `проект × lens` + тройки `проект × поверхность × lens` по каждому проекту в `docs/projects/` (кроме `_template`) |
| `/cross-audit <slug>` | прогон только по одному проекту (его пары + тройки по его поверхностям) + верхнеуровневые углы один раз |
| `/cross-audit <lens>` | прогон одного угла; для пары — по всем проектам; для тройки — по всем проектам × их поверхностям (или сузить `<slug> <lens>`) |
| `/cross-audit --quick` | быстрый прогон: три foundation-угла продукт↔interface (`user-who`, `capability-situation`, `surface-zone` — per-surface, тройки) по каждому проекту × поверхности + `addresses-problem-bizproblem` один раз |

`lens` ∈ {`factor-business`, `currentmetric-metric`,
`addresses-problem-bizproblem`, `segmentproblem-bizproblem`, `segment-subject`,
`solution-business`, `business-segment`, `prospective-consistency`,
`provenance-upstream`, `stakeholder-subject`, `stakeholder-factor`,
`stakeholder-strategy`, `projectmap-reciprocity`,
`goal-vision`, `subject-user`, `segment-user`, `job-vision`,
`segmentproblem-vision`, `integration-crossproject`,
`surface-capability`, `mechanic-capability`, `bet-capability`,
`capability-hypothesis`, `capability-job`, `user-who`,
`capability-situation`, `situation-job`, `situation-hypothesis`,
`capability-domain`, `surface-zone`, `surface-screen`, `integration-domain`,
`constraint-surface`, `market-capability`, `dataitems-crosssurface`}.

**Скоуп углов** (подробнее — `references/angles.md`):

- **верхнеуровневые, прогон один раз** (общие слои business ↔ ajtbd ↔
  swot ↔ hypothesis-map + граф project-map, без проекта): `factor-business`,
  `currentmetric-metric`, `segmentproblem-bizproblem`, `segment-subject`,
  `solution-business`, `business-segment`, `prospective-consistency`,
  `provenance-upstream`, `stakeholder-subject` (лицо ↔ субъект через
  `manifests-as`), `stakeholder-factor` (властный champion/blocker как
  фактор), `stakeholder-strategy` (стойка властного лица ↔ bet/goal),
  `projectmap-reciprocity` (осмысленность рёбер графа стыков).
- **верхнеуровневый M:N, прогон один раз над всеми проектами**:
  `addresses-problem-bizproblem` — связывает все `vision.addresses-problem`
  со строками реестра `business-problem`, в обе стороны.
- **пары `проект × lens`** (цель — корневой kind продукта
  `vision`/`user`/`integration`, не per-surface):
  - swot/hypothesis-map ↔ vision/user (скоуп к проблемам проекта):
    `goal-vision`, `subject-user`.
  - ajtbd ↔ vision/user: `segment-user`, `job-vision`, `segmentproblem-vision`.
  - продукт ↔ соседние проекты (межпроектный): `integration-crossproject`.
- **тройки `проект × поверхность × lens`** (source ИЛИ destination —
  per-surface артефакт `capability/<surface>.md`, `interface/<surface>/*`,
  `screens/<surface>/*`): `surface-capability`, `mechanic-capability`,
  `bet-capability`, `capability-hypothesis`, `capability-job`, `user-who`,
  `capability-situation`, `situation-job`, `situation-hypothesis`,
  `surface-zone`, `surface-screen`, `capability-domain`, `integration-domain`,
  `constraint-surface`, `market-capability`.
- **один агент на проект, сразу по всем поверхностям**:
  `dataitems-crosssurface` (консистентность словаря данных между
  поверхностями; только при ≥2 поверхностях).

См. `references/angles.md`.

## Что делать при запуске

1. Прочитать `docs/business/README.md`, `docs/ajtbd/README.md`,
   `docs/swot/README.md`, `docs/hypothesis-map/README.md`,
   `docs/projects/README.md`, `docs/projects/_template/project/README.md`,
   `docs/projects/_template/project/{surface,capability,integration}.md`,
   `docs/projects/_template/project-map.md`,
   `docs/projects/_template/interface/README.md`, и (если есть)
   `docs/projects/_template/domains/README.md` /
   `docs/projects/_template/screens/README.md` — освежить каноны формы и
   ось поверхности.
2. Прочитать `references/angles.md` — список углов и контекста на
   каждый.
3. **Перечислить проекты.** Взять подкаталоги `docs/projects/`,
   **исключив `_template`** (это канон формы, не данные) и файл
   `project-map.md` (это singleton, не проект). Каждый оставшийся каталог
   `docs/projects/<slug>/` — отдельный проект. Если `<slug>` дан
   аргументом — список из одного проекта.
4. **Перечислить поверхности каждого проекта.** Прочитать реестр-хребет
   `docs/projects/<slug>/surface.md` — каждая строка `surface` даёт slug
   поверхности `<surface>`. Это ключи партиционирования: per-surface слои
   (`capability/<surface>.md`, `interface/<surface>/`, `screens/<surface>/`)
   живут под этими slug'ами. Тройки `(проект × поверхность × lens)`
   раскрываются по этому списку. Поверхность без папки нужного слоя —
   тройка для неё по этому lens пропускается (пометка в отчёте).
5. **Проверить наличие вложенных слоёв.** `docs/projects/<slug>/domains/`
   и `docs/projects/<slug>/screens/<surface>/` могут отсутствовать
   (продукт без backend, или поверхность ещё не дошла до экранов) —
   независимо. Углы, требующие отсутствующего слоя, пропускаются для этого
   проекта/поверхности с пометкой в отчёте.
6. Определить, какие углы применимы — по args или по полному прогону — и
   **раскрыть** их по скоупу:
   - **верхнеуровневые** (`factor-business`, `currentmetric-metric`,
     `addresses-problem-bizproblem`, `segmentproblem-bizproblem`,
     `segment-subject`, `solution-business`, `business-segment`,
     `prospective-consistency`, `provenance-upstream`,
     `stakeholder-subject`, `stakeholder-factor`, `stakeholder-strategy`,
     `projectmap-reciprocity`) — по одному агенту, без проекта;
   - **пары** (цель — корневой kind продукта): по агенту на
     `(проект × lens)`;
   - **тройки** (source ИЛИ destination — per-surface артефакт): по агенту
     на `(проект × поверхность × lens)` — для каждой поверхности из
     `surface.md` проекта;
   - **dataitems-crosssurface**: по одному агенту на проект (если у проекта
     ≥2 поверхностей с `data-items.md`).
7. **Спавнить агентов параллельно** (см. ниже). Рой широкий:
   `верхнеуровневые + Σ_проекты (пары + поверхности × тройки +
   dataitems-crosssurface)`.
8. Собрать ответы. Каждый агент возвращает findings в едином формате
   (с указанием проекта и — для троек — поверхности).
9. Сгруппировать findings по `(проект, поверхность, угол)`, отсортировать
   по severity. Верхнеуровневые — в отдельную группу «общие слои».
10. Через `AskUserQuestion` пройти по top-K findings — что делать с
    каждым: «принять как корректное», «нужна правка», «false positive».
11. Перезаписать `audit-state/last-report.md` с reasoning-trace и
    решениями аналитика.

## Рой агентов

Механизм: один lens = один агент, все в одном message-блоке параллельно. По
скоупу lens'а единица раскрытия разная: верхнеуровневый — один агент; пара —
агент на `(проект × lens)`; тройка — агент на `(проект × поверхность ×
lens)`. Перед спавном скилл подставляет конкретные `<project-slug>` и (для
троек) `<surface>` в шаблоны путей из `references/angles.md`.

**Как перечисляются поверхности и разворачиваются тройки.** Для каждого
проекта скилл читает `docs/projects/<slug>/surface.md` и берёт список slug'ов
поверхностей (по строке `surface` = одна поверхность). Затем на каждую
поверхность `<surface>` и каждый применимый тройка-lens спавнится отдельный
агент с подставленными путями (`capability/<surface>.md`,
`interface/<surface>/situation.md`, `screens/<surface>/`, …). Если папка
нужного слоя для поверхности отсутствует (например, `screens/<surface>/`
ещё не заведена), тройка по этому lens для этой поверхности пропускается с
пометкой в отчёте. Пара-lens'ы (`goal-vision`, `subject-user`,
`segment-user`, `job-vision`, `segmentproblem-vision`,
`integration-crossproject`) спавнятся **один раз на проект** — их цели
кросс-поверхностны (`vision.md`, `user.md`, `integration.md`).

Каждый агент получает:

- **проект** (`<project-slug>`) — для пар и троек; для верхнеуровневых —
  пометку «общие слои»;
- **поверхность** (`<surface>`) — только для троек;
- путь к двум слоям с **уже подставленными** `<project-slug>` и `<surface>`
  (например `docs/projects/<slug>/capability/<surface>.md`,
  `docs/projects/<slug>/interface/<surface>/situation.md`, `docs/business/`);
- свой lens;
- промпт-инструкцию из `references/angles.md` для этого lens;
- стандартный schema для findings (`references/findings-format.md`);
- для углов business-problem ↔ продукт — **список проблем, которые
  закрывает этот проект** (из `vision.addresses-problem`), чтобы агент
  скоупил сопоставление к ним, а не ко всем проблемам реестра.

Спавн — через `Agent` tool, **subagent_type: general-purpose**, чтобы
агент мог:

- `Read` файлы слоёв;
- `Grep` для быстрых проверок упоминаний;
- (опционально) `WebSearch` — если lens требует внешнего контекста
  (например, проверить, что constraint типа `regulation` действительно
  применима к описанной нише).

Все агенты спавнятся в **одном** message-блоке для параллельности.

### Промпт-каркас для агента

```
Lens: <name>
Project: <project-slug>   (или «общие слои» для верхнеуровневых углов)
Surface: <surface>        (только для троек проект×поверхность×lens; иначе «—»)
Source layer: <path-1>     (с уже подставленными <project-slug> и <surface>)
Destination layer: <path-2>
Проблемы этого проекта (для swot/hypothesis-map↔продукт): [<business-problem-slug>, ...]

Цель: семантически сопоставить записи в source и destination — найти
тупики, противоречия, потери покрытия. Не slug-валидация: связь
семантическая, агент сам решает, соответствует ли запись X записи Y.
Сопоставление держи в границах проекта <project-slug> (для троек — в
границах поверхности <surface>; для углов business-problem↔продукт — в
границах перечисленных проблем). Поверхности изолированы: запись чужой
поверхности — не твой материал (её ловит агент той поверхности).

Прочитай:
- <конкретные файлы из source-layer>
- <конкретные файлы из destination-layer>
- ветку state этих слоёв в едином дереве оркестратора
  `../entrypoint/state/` (по слою; для пар проекта —
  `../entrypoint/state/projects/<project-slug>/project/`; для троек
  per-surface слоёв — `../entrypoint/state/projects/<project-slug>/`
  `{interface,screens}/<surface>/`; если файлы есть).

Найди:
- <конкретные паттерны для этого lens из angles.md>

Верни ТОЛЬКО валидный JSON по схеме findings-format.md, без пояснений
и preamble. Каждый finding:
{
  "lens": "<lens>",
  "project": "<project-slug>",   (или null для верхнеуровневых углов)
  "surface": "<surface>",        (для троек; иначе null)
  "severity": "error" | "warning" | "hint",
  "title": "одна строка-заголовок",
  "evidence": "конкретные slug/файлы/места, где видно",
  "suggestion": "что аналитику дальше делать"
}

Если ничего не нашёл — пустой массив [].
Не выдумывай findings ради чисел.

Режим read-only: не вызывай Write/Edit (и любой мутирующий tool),
ничего не правь в артефактах. Возвращай ТОЛЬКО валидный JSON-массив findings.
```

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Семантический тупик, ломает целостность | user без покрытия в `interface/<surface>/who.md`; поверхность реестра без возможностей (пустой `capability/<surface>.md`); поверхность без зон; интеграция к соседнему проекту без ребра в `project-map.md`; `integration.sibling-project` на несуществующий проект; `vision.addresses-problem` ссылается на несуществующую проблему |
| `warning` | Подозрительная несостыковка | возможность поверхности «впритык» по ситуациям в её `interface/<surface>/`; возможность в `capability/<surface>.md`, чьи `user` не входят в `surface.user`; ребро `project-map` без опорной integration; constraint не привязан ни к поверхности, ни к её интеграции |
| `hint` | Гипотеза / возможная новая capability | market показывает gap, у нас нет возможности этой поверхности на эту территорию; ситуация поверхности без capability-якоря в `capability/<surface>.md`; один бизнес-датум под разными slug на разных поверхностях; проблема в `business-problem`, которую не закрывает ни один проект |

## Углы проверки (lenses)

Полный список — `references/angles.md`. `<slug>` = `<project-slug>`,
`<surface>` = slug поверхности из `surface.md` — подставляются на спавне.
Колонка «скоуп»: `★` — прогон один раз; `проект` — раскрывается в пары
`(проект × lens)`; `проект×поверхность` — раскрывается в тройки
`(проект × поверхность × lens)`. Краткая карта:

| lens | source | destination | скоуп | основной вопрос |
|---|---|---|---|---|
| `factor-business` | `docs/swot/factor.md` | `docs/business/` (profile, competitor) | ★ | каждый SWOT-фактор опирается на картину бизнеса? |
| `currentmetric-metric` | `docs/business/current-metric.md` | `docs/hypothesis-map/metric.md` | ★ | baseline целевой метрики (`current`) взят из текущего KPI бизнеса? |
| `addresses-problem-bizproblem` | `docs/projects/*/vision.md` (`addresses-problem`) | `docs/business/business-problem.md` | ★ | каждый ref проекта попадает в реальную проблему? есть ли проблема, в которую не бьёт ни один проект? (M:N, обе стороны) |
| `segmentproblem-bizproblem` | `docs/ajtbd/segment-problem.md` | `docs/business/business-problem.md` | ★ | трение клиента доказывает проблему бизнеса? есть ли проблема бизнеса без единого трения-доказательства? |
| `segment-subject` | `docs/ajtbd/segment.md` | `docs/hypothesis-map/subject.md` | ★ | субъект влияния вырастает из сегмента? есть ли позитивный субъект без сегмента (негативному не нужен)? |
| `solution-business` | `docs/ajtbd/solution.md` | `docs/business/` (competitor, offering) | ★ | нанятое решение (`maps-to`) сходится с игроком рынка / собственным офером? |
| `business-segment` | `docs/business/offering.md` (`for-segment`), `channel.md` (`serves-segment`) | `docs/ajtbd/segment.md` | ★ | межслойные ссылки оферов/каналов попадают в реальные сегменты и осмысленны? |
| `stakeholder-subject` | `docs/business/stakeholder.md` (`manifests-as`) | `docs/hypothesis-map/subject.md` | ★ | лицо-решатель и субъект — один человек (`manifests-as`)? властный блокер ≈ negative-субъект? |
| `stakeholder-factor` | `docs/business/stakeholder.md` (`attitude`, `power`) | `docs/swot/factor.md` | ★ | властный champion/blocker отражён SWOT-фактором (человек-как-фактор)? |
| `stakeholder-strategy` | `docs/business/stakeholder.md` (`strategic-stance`) | `docs/swot/bet.md`, `docs/hypothesis-map/goal.md` | ★ | ставка/цель не противоречит стойке властного лица? |
| `projectmap-reciprocity` | `docs/projects/project-map.md` | каталоги `docs/projects/` + `integration.md` проектов | ★ | рёбра графа стыков осмысленны (оба проекта есть, нет самоссылки, нет дубля вместо duplex, via резолвится)? |
| `goal-vision` | `docs/hypothesis-map/goal.md`, `metric.md` (по проблемам проекта) | `docs/projects/<slug>/vision.md` | проект | цель/метрика закрываемой проблемы отражены в vision.Success (как таргет, не гарантия)? |
| `subject-user` | `docs/hypothesis-map/subject.md` (по проблемам проекта) | `docs/projects/<slug>/user.md` | проект | субъект влияния соответствует user продукта? |
| `segment-user` | `docs/ajtbd/segment.md` | `docs/projects/<slug>/user.md` | проект | сегмент рынка соотносится с user продукта (разные сущности, но связаны)? сегмент без пользователя / пользователь без сегмента? |
| `job-vision` | `docs/ajtbd/job.md` (`big`/`core`) | `docs/projects/<slug>/vision.md` (Success) | проект | успех продукта целит в Big/Core Job сегмента? |
| `segmentproblem-vision` | `docs/ajtbd/segment-problem.md` | `docs/projects/<slug>/vision.md` (Problem) | проект | трение клиента отражено в vision.Problem продукта? |
| `integration-crossproject` | `docs/projects/<slug>/integration.md` (`target: sibling-project`) | `docs/projects/project-map.md` + `integration.md` соседа + `domains/<ctx>/use-cases/*` (порт) | проект | три стороны межпроектного стыка согласованы (integration ↔ project-map ↔ домен-порт ↔ обратная сторона соседа)? |
| `surface-capability` | `docs/projects/<slug>/surface.md` (строка `<surface>`) | `docs/projects/<slug>/capability/<surface>.md` | проект×поверхность | у поверхности есть возможности? возможности — тем user, кого поверхность обслуживает? |
| `mechanic-capability` | `docs/ajtbd/job-graph.md` (`value-mechanics`) | `docs/projects/<slug>/capability/<surface>.md` | проект×поверхность | механика ценности из графа реализована capability поверхности? механика без capability? |
| `bet-capability` | `docs/swot/bet.md`, `goal.md` (по проблемам проекта) | `docs/projects/<slug>/capability/<surface>.md` | проект×поверхность | ставка/цель реализуется хотя бы одной capability поверхности? |
| `capability-hypothesis` | `docs/projects/<slug>/capability/<surface>.md` (`hypotheses`) | `docs/hypothesis-map/hypothesis.md` (по проблемам проекта) | проект×поверхность | ребро capability→гипотеза резолвится? гипотеза проблемы без реализующей capability? |
| `capability-job` | `docs/projects/<slug>/capability/<surface>.md` (`jobs`) | `docs/ajtbd/job.md` | проект×поверхность | ребро capability→работа резолвится? Big/Core Job без прямо целящей capability? |
| `user-who` | `docs/projects/<slug>/user.md` | `docs/projects/<slug>/interface/<surface>/who.md` | проект×поверхность | who поверхности сводимо к user? user поверхности несёт хотя бы одно who? |
| `capability-situation` | `docs/projects/<slug>/capability/<surface>.md` | `docs/projects/<slug>/interface/<surface>/situation.md` | проект×поверхность | каждая capability поверхности реализуется ≥1 ситуацией той же поверхности? ситуация без capability-якоря? |
| `situation-job` | `docs/projects/<slug>/interface/<surface>/situation.md` (`jobs`) | `docs/ajtbd/job.md` | проект×поверхность | ребро situation→работа резолвится? |
| `situation-hypothesis` | `docs/projects/<slug>/interface/<surface>/situation.md` (`hypotheses`) | `docs/hypothesis-map/hypothesis.md` | проект×поверхность | ребро situation→гипотеза резолвится? |
| `surface-zone` | `docs/projects/<slug>/surface.md` (строка `<surface>`) | `docs/projects/<slug>/interface/<surface>/zone.md` | проект×поверхность | зоны поверхности образуют целостный UX для её user? |
| `surface-screen` | `docs/projects/<slug>/surface.md` + `interface/<surface>/` | `docs/projects/<slug>/screens/<surface>/` (если есть) | проект×поверхность | UX поверхности доведён до композиции экранов той же поверхности? |
| `capability-domain` | `docs/projects/<slug>/capability/<surface>.md` | `docs/projects/<slug>/domains/` (если есть) | проект×поверхность | у каждой capability поверхности есть бизнес-код в domain? |
| `integration-domain` | `docs/projects/<slug>/integration.md` (`surface` ∋ `<surface>`) | `docs/projects/<slug>/domains/` (порт в use-case `## Dependencies`) | проект×поверхность | у интеграции поверхности есть адаптер/порт в domain? |
| `constraint-surface` | `docs/projects/<slug>/constraint.md` | `docs/projects/<slug>/surface.md` (строка `<surface>`), `integration.md` (поверхности) | проект×поверхность | constraint поверхности привязан к ней или её интеграции? |
| `market-capability` | `docs/projects/<slug>/market.md` | `docs/projects/<slug>/capability/<surface>.md` | проект×поверхность | конкуренты покрывают возможности поверхности? gap, где конкурент умеет, а мы нет (signal к новой capability)? |
| `dataitems-crosssurface` | `docs/projects/<slug>/interface/*/data-items.md` (все поверхности) | (тот же набор) | проект (все поверхности) | один бизнес-датум на разных поверхностях под разными slug / с противоречивыми описаниями? (консистентность словаря) |

## Формат отчёта

```
=== /cross-audit ===
Слои: business (+ стейкхолдеры), ajtbd, business-problem, project-map (общие) + проекты: referral-network (поверхности: web-partner, tg-bot), loyalty-app (поверхности: mobile)
Проектов: 2 · агентов: 13 верхнеуровневых + (6 пар + 2 поверхности × 12 троек + 1 dataitems) по referral-network + (6 пар + 1 поверхность × 12 троек) по loyalty-app = …
Время: <duration>

— Общие слои —

[error] addresses-problem-bizproblem → проект loyalty-app бьёт в проблему
  `legacy-sync`, которой нет в docs/business/business-problem.md.
  Доказательство: projects/loyalty-app/vision.md addresses-problem =
    [`paid-churn`, `legacy-sync`]; business/business-problem.md → строки [`paid-churn`,
    `slot-utilization`] — `legacy-sync` отсутствует.
  Что делать: завести проблему `legacy-sync` через
  /business-deep-dive business-problem, либо убрать ref в /project-deep-dive
  loyalty-app.

[error] projectmap-reciprocity → ребро `loyalty-to-store` ссылается на
  to-project `web-store`, которого нет в docs/projects/.
  Доказательство: project-map.md:loyalty-to-store to-project=`web-store`;
    каталога docs/projects/web-store/ нет (есть referral-network, loyalty-app).
  Что делать: исправить to-project на реальный проект или удалить ребро
  через /project-deep-dive loyalty-app integration.

[warning] segmentproblem-bizproblem → проблему бизнеса `paid-churn` не
  доказывает ни одно трение клиента из docs/ajtbd/segment-problem.md.
  Доказательство: business/business-problem.md:paid-churn; в segment-problem.md нет ни одной
    записи с feeds-problem=`paid-churn` или семантически бьющей в эту
    проблему.
  Что делать: разведать трение клиента под эту проблему через
  /job-graph-deep-dive, либо зафиксировать другой источник доказательства.

— Проект referral-network · все поверхности —

[error] integration-crossproject → integration:loyalty-sync (target:
  sibling-project, sibling-project=`loyalty-app`) не сведена в project-map.
  Доказательство: integration.md:loyalty-sync target=sibling-project,
    sibling-project=`loyalty-app`; в project-map.md нет ребра с
    via=`integration:loyalty-sync` от referral-network.
  Что делать: завести ребро в project-map.md (через /project-deep-dive),
  или поправить target, если это внешняя система.

— Проект referral-network · поверхность web-partner —

[error] surface-capability → поверхность web-partner объявлена stable, но
  capability/web-partner.md пуст.
  Доказательство: surface.md:web-partner status=stable;
    projects/referral-network/capability/web-partner.md — 0 записей.
  Что делать: завести возможности через /project-deep-dive referral-network
  capability:web-partner, или понизить поверхность.

[error] user-who → user:doctor не несётся ни одним who поверхности
  web-partner.
  Доказательство: user:doctor.context = «врач инициирующей клиники»;
    surface:web-partner.user ∋ `doctor`; в interface/web-partner/who.md нет
    роли, выполняющей действия врача.
  Что делать: завести who:doctor через /interface-deep-dive referral-network
  web-partner who, либо пересмотреть, обслуживает ли web-partner врача.

[warning] capability-domain → capability:send-referral (web-partner) не имеет
  домена в projects/referral-network/domains/.
  Доказательство: capability/web-partner.md:send-referral.value = «один
    клик»; в domains/ есть только `auth`, `billing`, `inventory`.
  Что делать: добавить домен `referrals` через /domain-deep-dive, или
  пересмотреть capability.

— Проект referral-network · поверхность tg-bot —

[hint] capability-situation → ситуация confirm-via-bot в
  interface/tg-bot/situation.md не имеет capability-якоря в
  capability/tg-bot.md.
  Доказательство: situation:confirm-via-bot.action = «переподтвердить слот»;
    в capability/tg-bot.md нет возможности про переподтверждение.
  Что делать: завести capability на tg-bot или решить, что ситуация лишняя.

— Проект loyalty-app · поверхность mobile —

[hint] market-capability → конкурент klara-app покрывает push-кампании,
  у mobile нет такой возможности.
  Доказательство: market:klara-app.description = «push loyalty campaigns»;
    projects/loyalty-app/capability/mobile.md → нет записи про кампании.
  Что делать: рассмотреть через /project-deep-dive loyalty-app
  capability:mobile, или зафиксировать boundary.

Сводка: 4 error / 1 warning / 2 hint.
```

После отчёта — `AskUserQuestion` по каждому top-K finding (до 4 в
раунде):

- «Принять как корректное» — finding записывается в last-report как
  принятый, при следующем прогоне может игнорироваться (см.
  `references/angles.md` про suppressions).
- «Действительно нужно править» — finding идёт в next-actions,
  скилл предлагает запустить `/project-deep-dive` или
  `/interface-deep-dive` (но **не вызывает сам**).
- «False positive» — записывается, но игнорируется.
- «Обсудить позже» — оставить в last-report без решения.

## `audit-state/last-report.md`

Отчёт лежит **рядом со скиллом** (cross-audit не скоупится по одному
проекту — отчёт один на прогон, проекты внутри него):

```
.claude/skills/cross-audit/audit-state/last-report.md
```

Дальше по тексту скилла короткое `audit-state/` — сокращение этого пути.

```markdown
---
ran-on: <UTC-ts>
projects: [referral-network, loyalty-app]
surfaces:
  referral-network: [web-partner, tg-bot]
  loyalty-app: [mobile]
top-level-lenses-run: 13
pair-lens-runs: 12        # сумма по всем (проект × пара-lens)
triple-lens-runs: 36      # сумма по всем (проект × поверхность × тройка-lens)
dataitems-runs: 1         # один на мультиповерхностный проект
per-project-layers:
  referral-network: { project: yes, interface: yes, domain: yes, screen: no }
  loyalty-app:      { project: yes, interface: yes, domain: no,  screen: no }
findings: { error: X, warning: Y, hint: Z }
verdicts: { accepted: A, needs-fix: B, false-positive: C, deferred: D }
---

# Reasoning trace

## Общие слои

### Lens: addresses-problem-bizproblem
- agent-id: agent-1a
- duration: 12s
- findings: 2
- verdicts: [needs-fix, deferred]
- details:
  - finding-1 (error): project loyalty-app → проблема `legacy-sync` не
    в business-problem → verdict: needs-fix
  - finding-2 (hint): проблему `slot-utilization` не закрывает ни один
    проект → verdict: deferred

### Lens: projectmap-reciprocity
- agent-id: agent-1m
- findings: 1
- details:
  - finding-1 (error): ребро loyalty-to-store → to-project web-store не
    существует → verdict: needs-fix

## Проект: referral-network (пары)

### Lens: integration-crossproject
- agent-id: agent-5a
- findings: 1
- details:
  - finding-1 (error): integration:loyalty-sync без ребра в project-map →
    verdict: needs-fix

## Проект: referral-network · поверхность web-partner (тройки)

### Lens: user-who
- agent-id: agent-7c
- duration: 18s
- findings: 2
- verdicts: [needs-fix, accepted]
- details:
  - finding-1 (error): user:doctor без who поверхности web-partner →
    verdict: needs-fix
  - …

### Lens: capability-situation
- …

## Проект: referral-network · поверхность tg-bot (тройки)

### Lens: …
- …

## Проект: loyalty-app · поверхность mobile (тройки)

### Lens: …
- …

…
```

## Suppressions

Findings, помеченные «false positive», сохраняются **рядом со скиллом** в

```
.claude/skills/cross-audit/audit-state/suppressions.md
```

Формат записи:

```markdown
- lens: user-who; project: referral-network; surface: web-partner;
  pattern: "user:doctor without who"; reason: <от аналитика, через Other в
  AskUserQuestion>; suppressed-since: <ts>
```

Suppression несёт `project` (для верхнеуровневых углов — `project: —`) и
`surface` (для троек; для пар и верхнеуровневых — `surface: —`), чтобы
подавление в одной поверхности/проекте не глушило тот же паттерн в другой.
При следующем прогоне агент-lens получает relevant для его `(проект,
поверхность, lens)` suppressions как контекст и **не** генерирует те же
findings, если они подпадают под паттерн. Suppressions можно вручную
удалить из файла, чтобы заново всплыли.

## Что не делать

- **Не править артефакты.** Cross-audit — только отчёт и решения
  аналитика, что с findings делать.
- **Не вызывать другие скилы автоматически.** В next-actions — текст,
  что запустить.
- **Не выдумывать findings.** Если агент вернул пустой массив — так
  и пишем «0 findings» по этому lens.
- **Не включать `_template` в перечисление проектов и `project-map.md` в
  перечисление папок проектов.** `docs/projects/_template/` — канон формы;
  `docs/projects/project-map.md` — singleton графа стыков; в перечисление
  проектов не идут.
- **Не игнорировать отсутствующие слои/папки поверхностей.** Если у проекта
  нет `docs/projects/<slug>/domains/` — `capability-domain` и
  `integration-domain` пропускаются для этого проекта; если у поверхности
  нет папки `screens/<surface>/` — тройка `surface-screen` для этой
  поверхности пропускается. Везде — с явной пометкой «слой/папка не
  существует» в отчёте. У другого проекта/поверхности углы могут при этом
  отрабатывать.
- **Не дублировать структурные проверки `/project-audit` и
  `/interface-audit`/`/screen-audit`.** Файл `capability/<surface>.md` без
  поверхности в реестре, поверхность реестра без файла возможностей, папка
  поверхности вне реестра, циклы зон, битые внутрислойные slug — это
  **структура**, её держат узкие аудиты. Cross-audit — **семантика** между
  слоями (для кого поверхность, что чем покрыто), не grep структурной
  целостности.
- **Держать поверхностную изоляцию.** Агент тройки сопоставляет только в
  пределах своей `<surface>`; запись чужой поверхности — материал агента
  той поверхности, не повод флагать «дыру». Кросс-поверхностные вопросы
  ведут отдельные углы (`dataitems-crosssurface`, обратные стороны
  `mechanic-/bet-/capability-*` с пометкой «может нести другая поверхность»).
- **Не смешивать территорию с `/swot-audit`, `/hypothesis-map-audit` и
  `/ajtbd-audit`.** Методологию LinkedSWOT (фактор без ставки,
  ставка-висяк — в пределах проблемы) держит `/swot-audit`; Карту гипотез
  (задача-сирота, «тогда» без метрики, guardrail и т.п. — в пределах
  проблемы) держит `/hypothesis-map-audit`; методологию Advanced JTBD
  (бандл работ, непрерывность «чтобы», CPR, трение без решения — в пределах
  сегмента) держит `/ajtbd-audit`. Cross-audit — только кросс-**слойные**
  рёбра.
- **Не запускать рой повторно** для одной сессии. Если findings много —
  пройти по ним постепенно. Повторный прогон — следующая сессия или
  явный `/cross-audit` запуск.
- **Не предлагать клиенту запустить** `/cross-audit`. Это аналитический
  инструмент; в клиент-режиме (`entrypoint-for-business`) он не упоминается.
