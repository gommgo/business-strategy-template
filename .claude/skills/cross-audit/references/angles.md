# Углы проверки cross-audit

Каталог углов: сводная карта и карточка на каждый угол. Один угол — один
агент на свою единицу раскрытия: верхнеуровневый угол — один агент на
прогон, пара — на `проект × lens`, тройка — на `проект × поверхность × lens`,
`dataitems-crosssurface` — на проект (единицы и порядок раскрытия — SKILL.md).

`<slug>` = `<project-slug>`, `<surface>` = slug поверхности из реестра
`docs/projects/<slug>/surface.md`; оба подставляются на спавне. Пути с
`<surface>` ведут в папку поверхности (`capability/<surface>.md`,
`interface/<surface>/…`, `screens/<surface>/…`, `site/<surface>/…`,
`telegram-bot-flow/<surface>/…`, `mobile/<surface>/…`,
`design/<surface>/…`). Корневые kind
продукта (`vision`, `user`, `object`, `action`, `integration`, `boundary`,
`constraint`, `market`), файлы уровня продукта (факты `facts.yaml`, голос
`voice*.yaml`), облик продукта `design/` и домены
`services/<svc>/domains/<ctx>/` (по bounded-context,
внутри сервиса-владельца из `services/service.md`) кросс-поверхностны.

Род веб-поверхности (колонка `web-kind` реестра) выбирает её композицию: у
`web` рода `landing` и `site` — слой страницы `site/<surface>/` (папок
`interface/`, `screens/`, `fsd/` у неё нет), у `web` рода `app` и у
`admin`, `desktop`, `embed` — interface и экраны. Углы `surface-*` читают
тип и род вместе.

Карточка угла:

- **Source / Destination** — какие слои читать;
- **Скоуп** — `один раз` (верхнеуровневый), `по проекту` (пара) или
  `по проекту × поверхность` (тройка);
- **Применим если** — какие слои и папки должны существовать; иначе
  единица пропускается с пометкой в отчёте;
- **Что искать** — семантические паттерны с severity;
- **Промпт-добавка** — вставляется в промпт-каркас агента из SKILL.md.

## Карта углов

Строки идут в порядке групп отчёта; спавнятся все агенты параллельно.
Скоуп: `★` — один раз; `проект` — пара; `проект×поверхность` — тройка.

| lens | source | destination | скоуп | основной вопрос |
|---|---|---|---|---|
| `factor-business` | `docs/swot/factor.md` | `docs/business/` (profile, competitor, current-metric) | ★ | каждый SWOT-фактор опирается на картину бизнеса? |
| `currentmetric-metric` | `docs/business/current-metric.md` | `docs/hypothesis-map/metric.md` | ★ | baseline целевой метрики (`current`) взят из текущего KPI бизнеса? |
| `addresses-problem-bizproblem` | `docs/projects/*/vision.md` (`addresses-problem`) | `docs/business/business-problem.md` | ★ | каждый ref проекта попадает в реальную проблему? есть ли проблема, в которую не бьёт ни один проект? (M:N, обе стороны) |
| `segmentproblem-bizproblem` | `docs/ajtbd/segment-problem.md` | `docs/business/business-problem.md` | ★ | трение клиента доказывает проблему бизнеса? есть ли проблема бизнеса без единого трения-доказательства? |
| `segment-subject` | `docs/ajtbd/segment.md` | `docs/hypothesis-map/subject.md` | ★ | субъект влияния вырастает из сегмента? есть ли позитивный субъект без сегмента (негативному не нужен)? |
| `solution-business` | `docs/ajtbd/solution.md` | `docs/business/` (competitor, offering) | ★ | нанятое решение (`maps-to`) сходится с игроком рынка / собственным офером? |
| `business-segment` | `docs/business/offering.md` (`for-segment`), `channel.md` (`serves-segment`) | `docs/ajtbd/segment.md` | ★ | межслойные ссылки оферов/каналов попадают в реальные сегменты и осмысленны? |
| `prospective-consistency` | `docs/projects/*/vision.md` (`market-maturity`, `addresses-problem`) | `docs/ajtbd/segment.md`, `docs/business/business-problem.md` (`served`) | ★ | market-maturity продукта согласован с `served` адресуемых проблем и сегментов? проспективная сущность без адресующего проекта? |
| `provenance-upstream` | `docs/business/{offering,current-metric,business-problem}.md`, `docs/ajtbd/segment.md` (`from-project`, `served`) | `docs/projects/*/vision.md` (`lifecycle`, `market-maturity`, `addresses-problem`) | ★ | `from-project` ведёт в существующий проект? контур market-maturity ↔ served ↔ from-project согласован и замкнут у stable-продуктов? |
| `stakeholder-subject` | `docs/business/stakeholder.md` (`manifests-as`) | `docs/hypothesis-map/subject.md` | ★ | лицо-решатель и субъект — один человек (`manifests-as`)? властный блокер ≈ negative-субъект? |
| `stakeholder-factor` | `docs/business/stakeholder.md` (`attitude`, `power`) | `docs/swot/factor.md` | ★ | властный champion/blocker отражён SWOT-фактором (человек-как-фактор)? |
| `stakeholder-strategy` | `docs/business/stakeholder.md` (`strategic-stance`) | `docs/swot/bet.md`, `docs/hypothesis-map/goal.md` | ★ | ставка/цель не противоречит стойке властного лица? |
| `projectmap-reciprocity` | `docs/projects/project-map.md` | каталоги `docs/projects/` + `integration.md` проектов | ★ | рёбра графа стыков осмысленны (оба проекта есть, нет самоссылки, нет дубля вместо duplex, via резолвится)? |
| `service-placement` | `docs/projects/*/services/service.md` + `platform.md` (`provided-by: own`) | `docs/projects/infrastructure/{placement,runtime,server}.md` | ★ | каждый сервис/own-ресурс размещён хотя бы в prod-рантайм? размещение осмысленно (назначение/ёмкость сервера vs роль юнита)? |
| `platform-shared` | `docs/projects/*/services/platform.md` (`provided-by: shared:<slug>`) | `docs/projects/infrastructure/shared-platform.md` + `placement.md` | ★ | каждая shared-потребность резолвится в общий ресурс? общий ресурс реально общий (≥1 потребитель) и размещён? технологии не противоречат (проект ждёт kafka — shared даёт nats)? |
| `goal-vision` | `docs/hypothesis-map/goal.md`, `metric.md` (по проблемам проекта) | `docs/projects/<slug>/vision.md` | проект | цель/метрика закрываемой проблемы отражены в vision.Success (как таргет, не гарантия)? |
| `subject-user` | `docs/hypothesis-map/subject.md` (по проблемам проекта) | `docs/projects/<slug>/user.md` | проект | субъект влияния соответствует user продукта? |
| `segment-user` | `docs/ajtbd/segment.md` | `docs/projects/<slug>/user.md` | проект | сегмент рынка соотносится с user продукта (разные сущности, но связаны)? сегмент без пользователя / пользователь без сегмента? |
| `job-vision` | `docs/ajtbd/job.md` (`big`/`core`) | `docs/projects/<slug>/vision.md` (Success) | проект | успех продукта целит в Big/Core Job сегмента? |
| `segmentproblem-vision` | `docs/ajtbd/segment-problem.md` | `docs/projects/<slug>/vision.md` (Problem) | проект | трение клиента отражено в vision.Problem продукта? |
| `integration-crossproject` | `docs/projects/<slug>/integration.md` (`target: sibling-project` + `## Функции`) | `docs/projects/project-map.md` + `<sibling>/` (integration + обслуживающие use-case) + наш клиент `_shared/` + use-case `functions` | проект | стык согласован в обе стороны (integration ↔ project-map ↔ клиент+функции ↔ обслуживающий use-case соседа); наш `out` имеет callee у соседа? |
| `service-capability` | `docs/projects/<slug>/services/service.md` + паспорта | `docs/projects/<slug>/capability/*.md` (все поверхности) | проект | каждый бизнес-сервис (`api`/`worker`) несёт хотя бы одну capability через свои контексты? сервис без продуктового якоря (для технических `gateway` — пометка, не finding)? |
| `facts-business` | `docs/projects/<slug>/facts.yaml` | `docs/business/` (profile, offering, current-metric, competitor, material) + `docs/projects/<slug>/market.md` | проект | факты страницы не спорят с тем, что бизнес записал о себе: числа, условия оффера, источники? |
| `promise-product` | `docs/projects/<slug>/site/<surface>/` поверхностей `web` рода `landing`, `site` (смысл, бриф, утверждённые тексты) | `docs/projects/<slug>/`: `vision.md`, `capability/<surface>.md` всех поверхностей, `boundary.md`, `user.md`, `market.md` | проект | страница обещает то, что продукт делает, и не подаёт цель гарантией? |
| `surface-capability` | `docs/projects/<slug>/surface.md` (строка `<surface>`) | `docs/projects/<slug>/capability/<surface>.md` | проект×поверхность | у поверхности есть возможности? возможности — тем user, кого поверхность обслуживает? |
| `mechanic-capability` | `docs/ajtbd/job-graph.md` (`value-mechanics`) | `docs/projects/<slug>/capability/<surface>.md` | проект×поверхность | механика ценности из графа реализована capability поверхности? механика без capability? |
| `bet-capability` | `docs/swot/bet.md`, `goal.md` (по проблемам проекта) | `docs/projects/<slug>/capability/<surface>.md` | проект×поверхность | ставка/цель реализуется хотя бы одной capability поверхности? |
| `capability-hypothesis` | `docs/projects/<slug>/capability/<surface>.md` (`trace`: `hypothesis:<slug>`) | `docs/hypothesis-map/hypothesis.md` (по проблемам проекта) | проект×поверхность | ребро capability→гипотеза резолвится? гипотеза проблемы без реализующей capability? |
| `capability-job` | `docs/projects/<slug>/capability/<surface>.md` (`trace`: `job:<slug>`) | `docs/ajtbd/job.md` | проект×поверхность | ребро capability→работа резолвится? Big/Core Job без прямо целящей capability? |
| `user-who` | `docs/projects/<slug>/user.md` | `docs/projects/<slug>/interface/<surface>/who.md` | проект×поверхность | who поверхности сводимо к user? user поверхности несёт хотя бы одно who? |
| `surface-zone` | `docs/projects/<slug>/surface.md` (строка `<surface>`) | `docs/projects/<slug>/interface/<surface>/zone.md` | проект×поверхность | зоны поверхности образуют целостный UX для её user? |
| `capability-situation` | `docs/projects/<slug>/capability/<surface>.md` | `docs/projects/<slug>/interface/<surface>/situation.md` | проект×поверхность | каждая capability поверхности реализуется ≥1 ситуацией той же поверхности? ситуация без capability-якоря? |
| `situation-job` | `docs/projects/<slug>/interface/<surface>/situation.md` (`jobs`) | `docs/ajtbd/job.md` | проект×поверхность | ребро situation→работа резолвится? |
| `situation-hypothesis` | `docs/projects/<slug>/interface/<surface>/situation.md` (`hypotheses`) | `docs/hypothesis-map/hypothesis.md` | проект×поверхность | ребро situation→гипотеза резолвится? |
| `market-capability` | `docs/projects/<slug>/market.md` | `docs/projects/<slug>/capability/<surface>.md` | проект×поверхность | конкуренты покрывают возможности поверхности? gap, где конкурент умеет, а мы нет (signal к новой capability)? |
| `constraint-surface` | `docs/projects/<slug>/constraint.md` | `docs/projects/<slug>/surface.md` (строка `<surface>`), `integration.md` (поверхности) | проект×поверхность | constraint поверхности привязан к ней или её интеграции? |
| `surface-service` | `docs/projects/<slug>/surface.md` (строка `<surface>`) | `docs/projects/<slug>/services/service.md` (колонка `surfaces`) + паспорта (`Exposes`) | проект×поверхность | поверхность обслуживается ≥1 сервисом? bot-поверхность — ровно одним `type: bot`? сервис обслуживает поверхность, которой по смыслу не своя? |
| `capability-domain` | `docs/projects/<slug>/capability/<surface>.md` | `docs/projects/<slug>/services/*/domains/` (если есть) | проект×поверхность | у каждой capability поверхности есть бизнес-код в domain? |
| `integration-domain` | `docs/projects/<slug>/integration.md` (`## Провайдеры` ∋ `<surface>` + `## Функции`) | `docs/projects/<slug>/services/` (клиент `_shared/integrations/` + use-case `functions` + `fronted-by` gateway) | проект×поверхность | цепочка функции цела: бизнес-каталог ↔ клиент `_shared/` ↔ потребление в use-case? при `fronted-by` остальные ходят через `Exposes` gateway'я? |
| `surface-screen` | `docs/projects/<slug>/surface.md` + `interface/<surface>/` | `docs/projects/<slug>/screens/<surface>/` (если есть) | проект×поверхность | UX поверхности доведён до композиции экранов той же поверхности? |
| `surface-botflow` | `docs/projects/<slug>/surface.md` (строка `<surface>`, `type: bot`) + `interface/<surface>/` | `docs/projects/<slug>/telegram-bot-flow/<surface>/` (если есть) | проект×поверхность | UX bot-поверхности доведён до диалогов? зеркала окно↔блок сходятся? есть `/start`? |
| `botflow-domain` | `docs/projects/<slug>/telegram-bot-flow/<surface>/features/*/use-case.md` (`### Dependencies` — рефы `use-case:<ctx>.<Operation>`) + `notification.md` (`trigger`/`content`) | `docs/projects/<slug>/services/*/domains/` (use-cases, events + Payload; если есть) | проект×поверхность | зависимости bot use-case опираются на доменные use-case? триггеры уведомлений — на события, payload покрывает плейсхолдеры? доменное решение не утекло в `when`/`Steps`? |
| `botflow-service` | `docs/projects/<slug>/telegram-bot-flow/<surface>/features/*/use-case.md` (рефы `use-case:<ctx>.<Operation>`) + `notification.md` (`trigger: event:<ctx>.<Event>`) | `docs/projects/<slug>/services/service.md` + паспорта сервисов-владельцев контекстов (`Exposes`, `Messaging`) | проект×поверхность | каждый контекст-зависимость бота имеет сервис-владелец и тот достижим боту? событие-триггер уведомления публикуется продюсером в `Messaging` (иначе бот его не получит)? бот заведён сервисом `type: bot`? |
| `surface-mobile` | `docs/projects/<slug>/surface.md` (строка `<surface>`, `type: mobile`) + `interface/<surface>/` + `capability/<surface>.md` | `docs/projects/<slug>/mobile/<surface>/` (если есть) | проект×поверхность | UX мобильной поверхности доведён до карты приложения (экраны, фичи, входы, системные действия, виджеты, фон)? слой стоит на месте `screens/` и `fsd/`? ценность «вне приложения» из capability получила воплощение? |
| `mobile-domain` | `docs/projects/<slug>/mobile/<surface>/` (`entities.source`/`domain-ref`/поля, `event:<ctx>.<Event>` в `entry-points.trigger` · `widgets.refresh` · `background-tasks.when`, описания фич) | `docs/projects/<slug>/services/*/domains/` (агрегаты, events + Payload; если есть) | проект×поверхность | сущности карты опираются на агрегаты и не расходятся с ними по полям? события-триггеры существуют? бизнес-правило не утекло в приложение? события для людей дошли до push/виджета? |
| `mobile-service` | `docs/projects/<slug>/mobile/<surface>/shared-api.md` (ресурсы, владелец, операции) + push-входы с `trigger: event:<ctx>.<Event>` | `docs/projects/<slug>/services/service.md` (колонка `surfaces`) + паспорта сервисов-владельцев (`Exposes`, `Messaging`, `Workers`) + `integration.md` проекта | проект×поверхность | владелец каждого ресурса существует и обслуживает поверхность? событие-триггер push публикуется в `Messaging`, и есть кому отправить уведомление (воркер + провайдер доставки в `integration`)? |
| `mobile-web` | `docs/projects/<slug>/mobile/<surface>/entry-points.md` (`kind: deep-link`, `pattern`, `target`) | web-поверхности того же проекта: `fsd/<web-surface>/pages.md` (`path`) и/или `screens/<web-surface>/` (`screen.route`); у рода `site` — `site/<web-surface>/site-map.yaml` (`pages[].url`, `collections[].url_pattern`) | проект×поверхность | пути ссылок в приложение совпадают с путями web-поверхности (одна ссылка открывается и в вебе, и в приложении)? целевые экран и страница — об одном? |
| `surface-design` | `docs/projects/<slug>/surface.md` (строка `<surface>`) + композиция `site/<surface>/` или `screens/<surface>/` | `docs/projects/<slug>/design/` (статус ДС) + `design/<surface>/` (приёмка `REVIEW.md`, `ready.yaml`) | проект×поверхность | у закрытой композиции есть принятый макет с совпавшим отпечатком? облик не спорит с назначением поверхности? |
| `dataitems-crosssurface` | `docs/projects/<slug>/interface/*/data-items.md` (все поверхности) | (тот же набор) | проект (все поверхности) | один бизнес-датум на разных поверхностях под разными slug / с противоречивыми описаниями? (консистентность словаря) |

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
проекта, кроме `_template` и `infrastructure`).
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
addresses-problem у каждого docs/projects/<slug>/vision.md (исключи
_template) и строки docs/business/business-problem.md.

Связь slug-явная по форме, но проверяй смыслом, а не строкой: ref
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
segment-problem — трение клиента с нанятым решением (слой ajtbd); business-problem —
проблема бизнеса заказчика (business-problem). Это разные сущности:
первое доказывает и питает второе (сильное трение при низкой
удовлетворённости → проблема бизнеса).

Прямая сторона: `feeds-problem` (если задан) должен указывать на реально
существующую строку business-problem — иначе error. Без `feeds-problem` сопоставляй
по смыслу: какая проблема бизнеса опирается на это трение.

Обратная сторона: для каждой строки business-problem — доказывает ли её хоть одно
трение клиента? Ни одного — warning (проблема бизнеса без трения-
доказательства).

Сильное трение, не питающее ни одну проблему бизнеса — hint (кандидат в
новую проблему). Слои не смешивай: segment-problem не подаётся как проблема
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
обычно вырастает из сегмента.

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
solution — то, что сегмент нанимает сейчас на работу (слой ajtbd);
competitor/offering — игроки рынка и собственный офер бизнеса (business).
Нанятое решение часто и есть конкурент или офер бизнеса (`maps-to`).

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
business в ajtbd/segment. Проверь, что каждая ссылка резолвится в
реальный сегмент (иначе error) и осмысленна (офер/канал по смыслу
подходит бандлу работ и критериям успеха сегмента — иначе warning).

Обратно: сегмент с served=served, который не обслуживает ни офер, ни
канал — hint (бизнес видит сегмент, но не работает с ним). Сегмент с
served=prospective без оферов/каналов — не finding (разведка рынка).
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

Отражает ли vision.Success целевые метрики его проблем (metric.md,
скоуп по колонке business-problem)? Метрика — best-effort таргет, не
гарантия: если в vision она подана как обещание результата — error.
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
пользователь продукта <slug>. Это разные сущности, но связанные: продукт
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
продукта должен целить в Big/Core Job сегмента, который он обслуживает.

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
segment-problem — трение клиента с нанятым решением (слой ajtbd);
vision.Problem — какую проблему решает продукт <slug>. Проблема продукта
выводится из разведанного трения клиента.

Скоупь трения к сегментам, которые продукт обслуживает (через пользователей
проекта ↔ сегменты).

Для vision.Problem: опирается ли она на конкретное трение клиента? Не
опирается — warning. Сильное трение обслуживаемого сегмента без
отражения в Problem — hint. Здесь сверяется проблема продукта, не проблема
бизнеса (business-problem).
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
кандидат в capability.

Скоупь механики к сегментам, которые продукт обслуживает (через пользователей
проекта ↔ сегменты графа). Сопоставляй только с возможностями этой
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

Ставку/цель проблемы могут реализовывать разные проекты и разные
поверхности одного проекта — воплощение в capability ищи на этой
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
поверхности <surface> (docs/projects/<slug>/interface/<surface>/who.md)
семантически. User — это "кто адресат боли продукта" (один на весь
проект). Who — "роль, выполняющая шаг бизнес-процесса на этой
поверхности". Связь не структурная: одна user может развернуться в
несколько who (например, user "медсестра партнёрской клиники" → who:
nurse-partner, nurse-partner-senior), и в несколько поверхностей.

User обслуживается этой поверхностью, если она названа в surface.user
поверхности <surface> или по jobs/context работает через неё. Для такой
user: несёт ли её хоть одно who этой поверхности? Если нет — warning
(поверхность для user без роли). User, работающая только через другую
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
Оба слоя — поверхности <surface> проекта <slug>:
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
**Destination:** `docs/projects/<slug>/services/*/domains/` (если есть;
surface-агностичны); для поверхности без своего сервиса —
`services/service.md` (колонка `surfaces`) и
`services/architecture.md § Decisions`.
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть `services/` с доменами; у проекта
есть поверхность `<surface>` с файлом возможностей.

**Что искать:**

- `error`: capability `stable` этой поверхности, под которую в доменах сервисов
  проекта нет бизнес-домена / агрегата. Capability не существует в коде.
  Исключение — поверхность `web` рода `landing` или `site` без своего
  сервиса (её нет ни в одной колонке `surfaces` реестра, а решение «у
  поверхности `<surface>` своего сервиса нет» записано в
  `architecture.md § Decisions`): её возможность домена не требует —
  ценность дают страница и внешняя система, куда уходят заявки (пометить без
  finding).
- `warning`: бизнес-домен в `services/*/domains/` проекта, у которого не находится
  capability-якорь ни на одной поверхности. Технический домен (auth,
  logging) — норма; бизнес-домен (referrals, billing) без якоря — пробел.
  (Поскольку домены surface-агностичны, обратную сторону — домен без
  capability — точнее видит агент любой поверхности; не дублируй её
  агрессивно, флагай только домен, который явно не покрыт capability этой
  поверхности и по смыслу должен бы.)

**Промпт-добавка:**

```
Source — capability/<surface>.md (умения поверхности <surface> проекта
<slug>); destination — docs/projects/<slug>/services/*/domains/ (бизнес-код,
общий для всех поверхностей: домены партиционируются по bounded-context,
не по surface).

Для каждой capability этой поверхности: есть ли в доменах сервисов проекта (services/*/domains/)
агрегат или use-case, реализующий бизнес-логику? Сопоставь по семантике,
не имени файла. Одна доменная модель обслуживает все поверхности — домен
может нести capability и этой поверхности, и других.

Технические домены (auth, audit, logging) могут не иметь capability-якоря
— отметь, не помечай ошибкой. Поверхность web рода landing или site без
своего сервиса (нет в колонках surfaces, решение «своего сервиса нет» —
в architecture.md § Decisions): её capability домена не требует — ценность
дают страница и внешняя система; верни пустой список с пометкой. В finding
указывай project и surface.
```

## surface-zone

**Source:** `docs/projects/<slug>/surface.md` (реестр, строка `<surface>`).
**Destination:** `docs/projects/<slug>/interface/<surface>/zone.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть поверхность `<surface>` с папкой
интерфейса (`interface/<surface>/`). У `web` рода `landing` и `site`
interface нет — композиция у них слой страницы, её сверяет
`surface-design`; такая единица пропускается с пометкой (папка
`interface/<surface>/` у них — структурная находка `/project-audit`).

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
/interface-audit и /project-audit). Здесь — семантика: образуют ли зоны
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
`screens/<surface>/` (у поверхностей с `type: bot` и `type: mobile`
композицию сверяют `surface-botflow` и `surface-mobile`). У `web` рода
`landing` и `site` экранов нет — композиция у них слой страницы
`site/<surface>/`, её сверяет `surface-design`; такая единица пропускается с
пометкой.

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
docs/projects/<slug>/screens/<surface>/ (композиция экранов и визуальные
референсы assets/ той же поверхности). Поверхности изолированы — сопоставляй
в пределах <surface>.

Папка screens/<surface>/ существует, но пуста при наполненном
interface/<surface>/ — error. Ключевые ситуации/блоки интерфейса
поверхности без композиции в screens этой поверхности — warning. По
смыслу — посмотри shell/flow/screen-описания. В finding указывай project и
surface.
```

## surface-botflow

**Source:** `docs/projects/<slug>/surface.md` (строка `<surface>` с
`type: bot`) + `docs/projects/<slug>/interface/<surface>/`.
**Destination:** `docs/projects/<slug>/telegram-bot-flow/<surface>/`
(если есть): `features/<feature>/{dialog.md, window.md, use-case.md}` +
`command.md`, `notification.md` корня.
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть поверхность `<surface>` с `type: bot` и
папка `telegram-bot-flow/<surface>/`.

**Что искать:**

- `error`: bot-поверхность `stable` с наполненным `interface/<surface>/`,
  у которой папка `telegram-bot-flow/<surface>/` существует, но `features/`
  пуста (нет ни одной фичи — ни диалога, ни окна, ни use-case'а бота) —
  UX бота без композиции диалогов.
- `error`: папка `telegram-bot-flow/<surface>/` у поверхности, чей `type`
  в реестре не `bot` (слой только для ботов; для web — `screens/`).
- `warning`: блок (block) или ситуация interface bot-поверхности без
  отражения ни в одном окне (window) какой-либо фичи — UX-точка не дошла
  до диалогов.
- `warning`: реестр `command.md` без команды `/start` при наполненных
  фичах — у бота нет объявленного входа.
- `warning`: зеркало разошлось — `window.ux-substrates` (мета-блок секции
  окна в `features/<feature>/window.md`) не совпадает с `ux-substrates` его
  `interface-block` в interface той же поверхности.
- `hint`: фича/диалог/окно, не соотносимое по смыслу ни с одной зоной/блоком
  interface поверхности (заведено не в той папке или UX-анализ отстал).

**Промпт-добавка:**

```
Source — строка <surface> (type: bot) реестра surface.md + UX той же
поверхности docs/projects/<slug>/interface/<surface>/; destination —
docs/projects/<slug>/telegram-bot-flow/<surface>/ (фичи в features/<feature>/:
диалоги, окна, use-case'ы бота; плюс команды и уведомления реестрами корня
той же поверхности). Поверхности изолированы — сопоставляй в пределах
<surface>.

features/ пуста (ни одной фичи) при наполненном interface — error; папка у
поверхности с type ≠ bot — error. Блок/ситуация interface без окна —
warning; command.md без /start — warning; рассинхрон window.ux-substrates
(секция окна в window.md) ↔ interface-block — warning. Смысловая рифма:
зона (zone) ≈ фича/диалог (feature/dialog), блок (block) ≈ окно (window) —
её разрывы флагай hint. В finding указывай project и surface.
```

## botflow-domain

**Source:** `docs/projects/<slug>/telegram-bot-flow/<surface>/`: use-case'ы
бота фич (`features/<feature>/use-case.md`, секция `### Dependencies` с
рефами `use-case:<ctx>.<Operation>` — с точкой); реестр `notification.md`
(`trigger` вида `event:<ctx>.<Event>`, плейсхолдеры `content`).
**Destination:** `docs/projects/<slug>/services/*/domains/` (если есть):
`<ctx>/use-cases/`, `<ctx>/events/` (секция `Payload`).
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть `services/` (с доменами) и папка
`telegram-bot-flow/<surface>/`.

Бот — фронтенд: мост к домену поднят на уровень **use-case бота**
(оркестратора). Каждая зависимость bot UC и каждый триггер уведомления
обязаны опираться на домен, а домен, рождающий события для людей, —
доходить до уведомлений. Связь `widget.action` → bot UC и
`getter.*.source` → bot UC — **внутри слоя** (slug-валидируема в пределах
фичи), её сверяет `telegram-bot-flow-audit`; здесь она **не** проверяется.

**Что искать:**

- `error`: реф `use-case:<ctx>.<Operation>` в секции `### Dependencies`
  use-case'а бота (`features/<feature>/use-case.md`) на доменный use-case,
  которого нет в `services/*/domains/<ctx>/use-cases/` — оркестратор бота опирается на
  несуществующий домен.
- `error`: `notification.trigger` со ссылкой `event:<ctx>.<Event>` на
  событие, которого нет в `services/*/domains/<ctx>/events/`.
- `warning`: плейсхолдер `{…}` в `notification.content`, отсутствующий в
  `Payload` события-триггера — текст просит данных, которых событие не несёт.
- `warning`: бизнес-правило («если сумма > 1000») в условии перехода `when`
  окна **или** в секции `### Steps` use-case'а бота, а не как исход
  доменного use-case — доменное решение утекло в бот.
- `warning`: use-case бота `stable` без секции `### Dependencies` на
  доменный use-case (ничего не оркеструет) — кандидат на чистую навигацию
  без use-case либо на пропущенный поход в домен.
- `hint`: доменное событие, по смыслу адресованное человеку (подтверждение,
  напоминание, смена статуса), без уведомления в `notification.md` —
  кандидат на исходящее.

**Промпт-добавка:**

```
Source — use-case'ы бота фич (features/<feature>/use-case.md) и
notification.md слоя telegram-bot-flow/<surface>/ проекта <slug>: собери
рефы use-case:<ctx>.<Operation> (с точкой — доменные) из секций
### Dependencies всех use-case.md фич + рефы event:<ctx>.<Event>
(notification.trigger). Destination — services/*/domains/ проекта: use-cases и events
соответствующих контекстов. widget.action → bot UC и getter.source → bot UC
— within-layer (их сверяет telegram-bot-flow-audit), здесь не проверяй.

Реф зависимости bot UC на несуществующий доменный use-case — error; триггер
на несуществующее событие — error. Плейсхолдер content вне Payload события —
warning. Бизнес-правило в when окна или в Steps bot UC вместо исхода
доменного use-case — warning. Bot UC stable без Dependencies на домен —
warning. Обратная сторона: события домена, по смыслу адресованные человеку,
без уведомления — hint. Связь семантическая: совпадение по смыслу имени
операции достаточно, точная орфография — вопрос к deep-dive, не error,
если сущность узнаваема. В finding указывай project и surface.
```

## integration-domain

**Source:** `docs/projects/<slug>/integration.md` (`## Провайдеры`, чья
колонка `surface` содержит `<surface>`; их `## Функции`).
**Destination:** `docs/projects/<slug>/services/*/domains/` (если есть;
surface-агностичны): use-case `## Dependencies` колонки `integration` +
`functions`; клиенты `_shared/integrations/<integration>/` (`## Functions`);
для поверхностей без своего сервиса — `services/service.md` (колонка
`surfaces`) и `services/architecture.md § Decisions`.
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть `services/` с доменами; у проекта
есть поверхность `<surface>`.

Сверяет **цепочку функции**: бизнес-каталог (`## Функции` integration.md) ↔
конкретный клиент (`_shared/integrations/<integration>/`) ↔ потребление
(use-case `functions`).

**Что искать:**

- `error`: integration `stable`, обслуживающая `<surface>`, под которую в
  `services/` нет клиента `_shared/integrations/<integration>/` и ни одного
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
- Без находки — интеграция, которая обслуживает только поверхности без
  своего сервиса (`web` рода `landing` или `site`: её нет ни в одной
  колонке `surfaces` реестра, решение «у поверхности `<surface>` своего
  сервиса нет» записано в `architecture.md § Decisions`). Заявки такой
  поверхности уходят во внешнюю систему напрямую, поэтому клиента
  `_shared/integrations/<integration>/` и use-case она не требует.

**Промпт-добавка:**

```
Source — integration.md проекта <slug> (## Провайдеры + ## Функции);
скоупь к провайдерам, чья `surface` содержит <surface>. Destination — services/ (клиент _shared/ + домены):
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
сигнатура протекла в use-case.Steps, это warning. Интеграция, которая
обслуживает только поверхности без своего сервиса (web рода landing или
site, нет в колонках surfaces, решение «своего сервиса нет» — в
architecture.md § Decisions), клиента _shared/ и use-case не требует:
заявки уходят во внешнюю систему напрямую — не флаг. В finding указывай
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
(закон / SLA / контракт). Скоупь к поверхности <surface>: строка <surface>
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
Capability/<surface>.md — умения поверхности <surface>. Сопоставляй
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
hint, не error. Проспективные сущности как «висяк» не флагай.
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
и адресуемому сегменту. Проспективную сущность без from-project не флагай
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
stakeholder — человек-решатель внутри заказчика; subject — носитель
поведения, двигающего метрику. Один человек может быть обоими (через
stakeholder.manifests-as = subject:<slug>); властный внутренний блокер ≈
negative-субъект.

Прямая сторона: каждый manifests-as subject:<slug> резолвится в реальный
subject? Нет — error. Согласованность мотиваций лица и субъекта — рассинхрон
warning. Властный blocker/skeptic стейкхолдер без negative-субъекта там,
где он двигает метрику, — hint. Это разные сущности, связь
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
Люди-решатели часто и есть внутренние факторы SWOT: властный champion —
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
противоречие со слабым лицом — не finding. Связь семантическая, не slug.
```

## capability-hypothesis

**Source:** `docs/projects/<slug>/capability/<surface>.md` (колонка
`trace`, элементы `hypothesis:<slug>`).
**Destination:** `docs/hypothesis-map/hypothesis.md` (по проблемам, которые
закрывает проект).
**Скоуп:** по проекту × поверхность.
**Применим если:** оба слоя существуют; у проекта непустой
`addresses-problem` и есть поверхность `<surface>` с файлом возможностей.

**Что искать:**
- `error`: элемент `hypothesis:<slug>` в `capability.trace` (в
  `capability/<surface>.md`) ссылается на гипотезу, которой нет в
  `docs/hypothesis-map/` (ребро бьёт в несуществующую сущность).
- `hint`: гипотеза проблемы, которую закрывает проект, не реализуемая ни
  одной capability ни на одной поверхности продукта (стратегия без
  продуктового воплощения — возможно, её несёт соседний проект).

**Промпт-добавка:**
```
capability.trace (колонка в capability/<surface>.md — возможностях
поверхности <surface> проекта <slug>) — авторское ребро продукт → вверх;
элементы hypothesis:<slug> — ребро в hypothesis-map: возможность реализует
гипотезу (элементы job:<slug> — угол capability-job). Скоупь гипотезы к
проблемам проекта (колонка `business-problem`).

Прямая сторона: каждый hypothesis:<slug> из trace этой поверхности
резолвится в реальную hypothesis? Нет — error. Обратная: гипотеза
проблемы проекта без реализующей capability на этой поверхности — hint
(может нести другая поверхность того же проекта или соседний проект; не
флагай агрессивно).
Связь семантическая. В finding указывай project и surface.
```

## capability-job

**Source:** `docs/projects/<slug>/capability/<surface>.md` (колонка
`trace`, элементы `job:<slug>`).
**Destination:** `docs/ajtbd/job.md`.
**Скоуп:** по проекту × поверхность.
**Применим если:** оба слоя существуют; у проекта есть поверхность
`<surface>` с файлом возможностей.

**Что искать:**
- `error`: элемент `job:<slug>` в `capability.trace` (в
  `capability/<surface>.md`) ссылается на работу, которой нет в
  `docs/ajtbd/job.md`.
- `hint`: Core/Big Job обслуживаемого сегмента без capability ни на одной
  поверхности, прямо в неё целящей (`job:<slug>` в `capability.trace`) —
  дополняет `mechanic-capability` (там через механики ценности, здесь —
  прямое ребро).

**Промпт-добавка:**
```
capability.trace (колонка в capability/<surface>.md — возможностях
поверхности <surface> проекта <slug>) — авторское ребро продукт → вверх;
элементы job:<slug> — прямое ребро в ajtbd: возможность целит в работу
сегмента (в дополнение к выводимому через job-graph.value-mechanics;
элементы hypothesis:<slug> — угол capability-hypothesis).

Прямая сторона: каждый job:<slug> из trace этой поверхности резолвится в
реальный job? Нет — error. Обратная: Big/Core Job обслуживаемого
сегмента без прямо целящей capability на этой поверхности — hint (может
нести другая поверхность; не флагай агрессивно). Связь семантическая. В
finding указывай project и surface.
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
кому её возможности на деле ценны. У `web` рода `landing` и `site` файл
возможностей по желанию — ценность такой поверхности дают страница и
оффер; файла нет — единица без находки.

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
`user`). Связь capability → поверхность структурная (файл лежит в своей
поверхности — это держит /project-audit); ты проверяешь смысл: совпадают
ли адресаты.

Файл capability/<surface>.md пуст при stable-поверхности — error
(поверхность без умений). Возможность, чьи user не пересекаются с
surface.user поверхности — warning (умение «не тем», кого поверхность
обслуживает). User из surface.user без единой ценной ему возможности —
hint. Связь семантическая (user сопоставляй по смыслу, не только по slug).
У поверхности web рода landing или site файл возможностей по желанию: нет
файла — верни пустой список с пометкой. В finding указывай project и
surface.
```

## integration-crossproject

**Source:** `docs/projects/<slug>/integration.md` (`## Провайдеры` с
`target: sibling-project` + их `## Функции`).
**Destination:** `docs/projects/project-map.md` (рёбра) +
`docs/projects/<sibling>/` (обратная сторона: его `integration.md` +
обслуживающие `services/*/domains/<ctx>/use-cases/*`) +
`docs/projects/<slug>/services/` (наш клиент `_shared/integrations/<integration>/` +
`functions` в use-case'ах доменов).
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
  `services/`).
- `warning`: техническая деталь (сигнатура функции, endpoint, имя use-case)
  просочилась в `project-map.md` — карта должна быть на бизнес-языке.

**Промпт-добавка:**
```
Межпроектный стык согласован в обе стороны: (1) авторская — integration.md
проекта <slug> (target: sibling-project + ## Функции); (2) граф — ребро в
docs/projects/project-map.md (бизнес-язык, via → integration:<integration>);
(3) наша техника — клиент services/_shared/integrations/<integration>/ +
functions в use-case; (4) сторона соседа <X> — обслуживающий use-case (наш
out ↔ его принимающий Actor) или его исходящая функция.

Прочитай integration.md проекта <slug> (фильтр target: sibling-project +
функции), docs/projects/project-map.md, перечень каталогов docs/projects/,
integration.md соседа <X> и его services/*/domains/*/use-cases/ (если есть),
services/ проекта <slug> (клиент _shared/ + functions в use-case).

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
осмысленность каждого ребра и пар рёбер:

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
Прочитай data-items.md всех папок поверхностей проекта <slug>
(docs/projects/<slug>/interface/*/data-items.md). Реестр data-items
surface-локален: один датум на разных поверхностях — это намеренно разные
записи (web и бот воплощают его по-разному), и сам факт раздельных записей
не флагай.

Ищи только смысловые расхождения словаря данных между поверхностями:
- один бизнес-датум под разными slug на разных поверхностях — hint
  (согласовать имена);
- один slug с противоречивыми description на разных поверхностях — hint
  (один датум — два смысла).

Всё — hint (консистентность словаря, не ошибка). В finding ставь project =
<slug>, surface не указывай (угол охватывает все поверхности сразу).
```

## surface-service

**Source:** `docs/projects/<slug>/surface.md` (строка `<surface>`: `type`,
`web-kind`).
**Destination:** `docs/projects/<slug>/services/service.md` (колонка
`surfaces`) + паспорта `services/<svc>/README.md` (`Exposes`); для
поверхности без своего сервиса — `services/architecture.md § Decisions` и
`docs/projects/<slug>/integration.md` (колонка `surface`).
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть `services/service.md`.

**Что искать:**

- `error`: поверхность реестра, которую не обслуживает ни один сервис
  (нет ни в одной колонке `surfaces`, и никакой `Exposes` не несёт
  `surface:<slug>`) — фронт без бэкенда.
  Исключение — мобильная поверхность, у которой все сущности карты
  `mobile/<surface>/entities.md` имеют `source: local` и `shared-api.md`
  пуст: приложение без бэкенда сервис не требует (пометить без finding).
  Исключение — поверхность `web` рода `landing` или `site`: лендинг и сайт
  живут без бэкенда, если получатели их заявок и событий — строки
  `integration.md` с этой поверхностью в колонке `surface`, а в
  `architecture.md § Decisions` записано решение «у поверхности `<surface>`
  своего сервиса нет» (пометить без finding).
- `warning`: поверхность `web` рода `landing` или `site` без сервиса, у
  которой решение не записано или получателей заявок в `integration.md` нет, —
  «лендинг без бэкенда без записанного решения». Это не `error`: своего
  бэкенда у лендинга может и не быть, но решение принимает архитектор.
- `error`: bot-поверхность (`type: bot`), у которой нет ровно одного
  сервиса `type: bot` (ноль или два).
- `warning`: сервис экспонирует поверхность, которой нет в реестре, или
  обслуживает поверхность, по смыслу не свою (admin-сервис в колонке
  `surfaces` клиентского web).

**Промпт-добавка:**

```
Source — строка поверхности <surface> реестра surface.md проекта <slug>;
destination — services/service.md (колонка surfaces) и Exposes паспортов.
Поверхность реальна, только если её кто-то обслуживает: найди сервисы с
<surface> в surfaces и функции Exposes с audience surface:<surface>.
Сопоставь смыслом: тот ли это сервис, который должен нести эту поверхность?
Поверхность web рода landing или site без сервиса — не error: без находки,
если получатели её заявок — строки integration.md с этой поверхностью в
surface и в architecture.md § Decisions записано «у поверхности <surface>
своего сервиса нет»; не хватает решения или получателей — warning
«лендинг без бэкенда без записанного решения». В finding указывай project
и surface.
```

## service-capability

**Source:** `docs/projects/<slug>/services/service.md` + паспорта
(`Owned Contexts`, `Exposes`).
**Destination:** `docs/projects/<slug>/capability/*.md` (все поверхности).
**Скоуп:** по проекту (один агент — сервисы кросс-поверхностны).
**Применим если:** у проекта есть `services/`.

**Что искать:**

- `warning`: бизнес-сервис (`type: api`/`worker`), чьи контексты не несут
  ни одной capability ни на одной поверхности — сервис без продуктового
  якоря («сервис ради сервиса»). Технические `gateway`/`edge`/`bot` —
  норма, пометить без finding.
- `hint`: capability `stable`, чьи домены живут в сервисе, который не
  обслуживает поверхность этой capability ни напрямую (`surfaces`), ни
  транзитом (через `Exposes` к edge/bot) — путь ценности до пользователя
  неочевиден.

**Промпт-добавка:**

```
Source — реестр сервисов и паспорта services/ проекта <slug>; destination —
capability/*.md всех поверхностей. Для каждого api/worker-сервиса: какие
capability реализуют его контексты (семантикой, не grep)? Сервис, чьи
домены не держат ни одну capability, — кандидат на лишнего. В finding
указывай project и сервис.
```

## botflow-service

**Source:** `docs/projects/<slug>/telegram-bot-flow/<surface>/features/*/use-case.md`
(рефы `use-case:<ctx>.<Operation>`) + `notification.md`
(`trigger: event:<ctx>.<Event>`).
**Destination:** `docs/projects/<slug>/services/service.md` + паспорта
сервисов-владельцев контекстов (`Exposes`, `Messaging`).
**Скоуп:** по проекту × поверхность (`type: bot`).
**Применим если:** у проекта есть `services/` и папка
`telegram-bot-flow/<surface>/`.

**Что искать:**

- `error`: контекст `<ctx>` из зависимостей бота не имеет сервиса-владельца
  (нет папки `services/*/domains/<ctx>/`).
- `error`: уведомление с `trigger: event:<ctx>.<Event>`, событие которого
  сервис-владелец не публикует в брокер (нет строки `produces` с этим
  `event` в его `Messaging`) — бот сигнал не получит.
- `warning`: в реестре сервисов нет сервиса `type: bot` при наличии
  bot-поверхности с диалогами (оркестратору бота негде жить).
- `hint`: операции, которые бот дёргает (`use-case:<ctx>.<Op>`), у
  сервиса-владельца не видны ни в `Exposes`, ни смыслом в `Owned
  Contexts` — стоит проверить достижимость.

**Промпт-добавка:**

```
Source — рефы use-case:<ctx>.<Operation> и event:<ctx>.<Event> слоя
telegram-bot-flow/<surface>/ проекта <slug>; destination — реестр
service.md и паспорта сервисов-владельцев этих контекстов (владелец =
сервис с папкой services/<svc>/domains/<ctx>/). Сверь: владелец существует;
событие-триггер каждого уведомления публикуется владельцем в Messaging
(produces, тот же event); бот заведён сервисом type: bot. Содержание
диалогов и зеркала окон не проверяй (это telegram-bot-flow-audit и
botflow-domain). В finding указывай project и surface.
```

## surface-mobile

**Source:** `docs/projects/<slug>/surface.md` (строка `<surface>` с
`type: mobile`) + `docs/projects/<slug>/interface/<surface>/` +
`docs/projects/<slug>/capability/<surface>.md`.
**Destination:** `docs/projects/<slug>/mobile/<surface>/` (если есть): 12
файлов карты приложения.
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть поверхность `<surface>` с `type: mobile`
и папка `mobile/<surface>/`.

**Что искать:**

- `error`: мобильная поверхность `stable` с наполненным
  `interface/<surface>/`, у которой папка `mobile/<surface>/` существует,
  но `screens.md` и `features.md` пусты — UX приложения без карты.
- `error`: папка `mobile/<surface>/` у поверхности, чей `type` в реестре не
  `mobile`; папка `screens/<surface>/` или `fsd/<surface>/` у мобильной
  поверхности (её место занимает `mobile/`).
- `warning`: ситуация или блок interface мобильной поверхности без носителя
  в карте — ни экрана, ни фичи, ни системного действия, ни виджета, ни
  фоновой задачи: UX-точка не дошла до приложения.
- `warning`: возможность `capability/<surface>.md`, чья ценность по смыслу
  живёт **вне экранов** (узнать вовремя, напомнить, увидеть на лету, сделать
  не открывая приложение, продолжить без сети), а в карте нет
  соответствующего воплощения (точка входа `push`, фоновая задача, виджет,
  системное действие, офлайн-политика оболочки).
- `hint`: экран, фича, виджет или фоновая задача, не соотносимые по смыслу
  ни с одной зоной/блоком/ситуацией interface поверхности (заведено не в
  той папке или UX-анализ отстал).

**Промпт-добавка:**

```
Source — строка <surface> (type: mobile) реестра surface.md + UX той же
поверхности docs/projects/<slug>/interface/<surface>/ + возможности
capability/<surface>.md; destination — docs/projects/<slug>/mobile/<surface>/
(карта приложения той же поверхности: entities, screens, flows, features,
shell, entry-points, permissions, system-actions, widgets, background-tasks,
shared-api, shared-lib). Поверхности изолированы — сопоставляй в пределах
<surface>.

Карта пуста (нет экранов и фич) при наполненном interface — error; папка
mobile/ у поверхности с type ≠ mobile либо screens/ / fsd/ у мобильной —
error. Ситуация/блок interface без носителя в карте — warning. Отдельно
пройди возможности: ценность «вне экранов» (вовремя узнать, напомнить,
увидеть на лету, сделать не открывая, работать без сети) должна иметь
воплощение в entry-points / background-tasks / widgets / system-actions /
shell#Offline — иначе warning. Смысловая рифма: зона ≈ группа экранов / таб,
блок ≈ экран, ситуация ≈ фича, шаг системного участника ≈ фоновая задача —
её разрывы флагай hint. Структуру слоя (битые рефы, enum'ы, зеркало
widgets.actions) не проверяй — это mobile-audit. В finding указывай project
и surface.
```

## mobile-domain

**Source:** `docs/projects/<slug>/mobile/<surface>/`: `entities.md`
(`source`, `domain-ref`, `ключевые поля`), рефы `event:<ctx>.<Event>` в
`entry-points.trigger`, `widgets.refresh`, `background-tasks.when`, описания
`features.md`, `system-actions.md`, `background-tasks.md`.
**Destination:** `docs/projects/<slug>/services/*/domains/` (если есть):
агрегаты (`Properties`), `<ctx>/events/` (секция `Payload`), `<ctx>/use-cases/`.
**Скоуп:** по проекту × поверхность.
**Применим если:** у проекта есть `services/` (с доменами) и папка
`mobile/<surface>/`.

Приложение — клиент домена: правила живут в домене, приложение показывает и
запускает. Сущности карты обязаны опираться на агрегаты, сигналы вне
экранов — на события, а события, адресованные человеку, — доходить до
приложения.

**Что искать:**

- `error`: `entities.domain-ref` на агрегат/сущность, которых нет в
  `services/*/domains/<ctx>/`.
- `error`: реф `event:<ctx>.<Event>` (push-вход, обновление виджета, фоновая
  задача `remote-event`) на событие, которого нет в
  `services/*/domains/<ctx>/events/`.
- `warning`: `ключевые поля` сущности называют поле, которого агрегат по
  смыслу не несёт (или теряют поле, без которого экран/виджет
  бессмысленны).
- `warning`: данные, которые показывает уведомление или виджет по смыслу
  записи, отсутствуют в `Payload` события-триггера.
- `warning`: бизнес-правило («если сумма > 1000», расчёт, право доступа) в
  описании фичи, системного действия или фоновой задачи вместо исхода
  доменного use-case — доменное решение утекло в приложение.
- `hint`: сущность `source: local`, у которой в домене есть агрегат того же
  смысла, — кандидат на дублирование источника правды.
- `hint`: доменное событие, по смыслу адресованное человеку (подтверждение,
  напоминание, смена статуса), без push-входа и без обновления виджета.

**Промпт-добавка:**

```
Source — карта приложения mobile/<surface>/ проекта <slug>: entities
(source, domain-ref, ключевые поля), все рефы event:<ctx>.<Event> из
entry-points.trigger, widgets.refresh, background-tasks.when, описания фич,
системных действий и фоновых задач. Destination — services/*/domains/
проекта: агрегаты, события (Payload), use-case'ы соответствующих контекстов.

domain-ref на несуществующий агрегат — error; event: на несуществующее
событие — error. Поля сущности против Properties агрегата и данные
уведомления/виджета против Payload события — warning при расхождении
смыслом. Бизнес-правило в описании фичи/действия/фоновой задачи вместо
исхода доменного use-case — warning. Обратная сторона: события домена для
людей без push-входа/виджета — hint; local-сущность при агрегате того же
смысла — hint. Связь семантическая: узнаваемость по смыслу достаточна,
орфография — вопрос к deep-dive. Приложение без бэкенда (все сущности
local, shared-api пуст) — угол неприменим, верни пустой список с пометкой.
В finding указывай project и surface.
```

## mobile-service

**Source:** `docs/projects/<slug>/mobile/<surface>/shared-api.md` (ресурсы:
`владелец`, `операции`) + push-входы `entry-points.md` с
`trigger: event:<ctx>.<Event>`.
**Destination:** `docs/projects/<slug>/services/service.md` (колонка
`surfaces`) + паспорта сервисов-владельцев (`Exposes`, `Messaging`,
`Workers`) + `docs/projects/<slug>/integration.md`.
**Скоуп:** по проекту × поверхность (`type: mobile`).
**Применим если:** у проекта есть `services/` и папка `mobile/<surface>/`.

**Что искать:**

- `error`: ресурс `shared-api` с владельцем, которого нет в реестре
  сервисов, либо контекст ресурса без сервиса-владельца (нет папки
  `services/*/domains/<ctx>/`).
- `error`: push-вход с `trigger: event:<ctx>.<Event>`, событие которого
  сервис-владелец не публикует в брокер (нет строки `produces` с этим
  `event` в его `Messaging`) — сигнал не покинет домен.
- `warning`: событие-триггер публикуется, но отправить уведомление некому:
  ни один воркер/сервис его не потребляет ради доставки, либо в
  `integration.md` проекта нет провайдера доставки уведомлений,
  обслуживающего эту поверхность.
- `warning`: сервис-владелец ресурса не несёт мобильную поверхность в
  колонке `surfaces` и не виден транзитом (edge/gateway) — приложению до
  него не дойти.
- `hint`: операции ресурса по смыслу не видны ни в `Exposes`, ни в `Owned
  Contexts` владельца — стоит проверить достижимость.

**Промпт-добавка:**

```
Source — shared-api.md (ресурсы, владельцы, операции) и push-входы
entry-points.md с trigger: event:<ctx>.<Event> слоя mobile/<surface>/
проекта <slug>; destination — реестр service.md (surfaces), паспорта
сервисов-владельцев (Exposes, Messaging, Workers) и integration.md проекта.
Сверь: владелец каждого ресурса существует и обслуживает мобильную
поверхность; событие-триггер каждого push публикуется владельцем
(produces, тот же event); есть кому довезти уведомление до устройства —
потребитель события (воркер) и провайдер доставки уведомлений в
integration.md с этой поверхностью в surface. Содержимое экранов и
внутрислойные рефы не проверяй (это mobile-audit), поля сущностей — это
mobile-domain. В finding указывай project и surface.
```

## mobile-web

**Source:** `docs/projects/<slug>/mobile/<surface>/entry-points.md` (строки
`kind: deep-link`: `pattern`, `target`) + `screens.md` целевых экранов.
**Destination:** web-поверхности того же проекта: `fsd/<web-surface>/pages.md`
(`path`) и/или `screens/<web-surface>/` (`screen.route`); у веб-поверхности
рода `site` адреса берутся из карты сайта `site/<web-surface>/site-map.yaml`
(`pages[].url`, `collections[].url_pattern`).
**Скоуп:** по проекту × поверхность (`type: mobile`).
**Применим если:** у проекта есть мобильная поверхность с deep link'ами и
хотя бы одна web-поверхность с `fsd/`, `screens/` или картой сайта.

Одна ссылка должна открываться и в вебе, и в приложении: путь — общий
идентификатор места продукта на двух поверхностях.

**Что искать:**

- `warning`: путь deep link, которому не соответствует ни одна страница
  web-поверхности, — в приложении ссылка откроется, в вебе ведёт в никуда.
- `warning`: путь совпадает, но целевой экран приложения и web-страница по
  смыслу о разном.
- `hint`: web-страница, по смыслу равная экрану приложения с входом по
  ссылке, но с другим путём — кандидат на общий путь.
- `hint`: ключевой экран приложения, у которого есть web-двойник, но нет
  входа `deep-link`.

**Промпт-добавка:**

```
Source — deep-link-входы mobile/<surface>/entry-points.md проекта <slug>
(pattern, target) + назначение целевых экранов из screens.md; destination —
web-поверхности того же проекта: fsd/<web-surface>/pages.md (path) и
screens/<web-surface>/ (screen.route), у веб-поверхности рода site — карта
сайта site/<web-surface>/site-map.yaml (pages[].url,
collections[].url_pattern). Это намеренно кросс-поверхностный
угол: сопоставляй пути и смысл «экран приложения ↔ web-страница».

Путь deep link без web-страницы — warning; совпавший путь при разном
смысле цели — warning. Web-страница-двойник с другим путём и экран с
web-двойником без входа по ссылке — hint. Хосты, схемы и отпечатки не
проверяй — это stack код-репо. В finding указывай project, в surface —
мобильную поверхность <surface>, а web-поверхность — в evidence и
destination-refs.
```

## service-placement

**Source:** реестры `docs/projects/*/services/service.md` + проектные
`platform.md` (строки `provided-by: own`).
**Destination:** `docs/projects/infrastructure/placement.md` +
`runtime.md` + `server.md`.
**Скоуп:** верхнеуровневый, прогон один раз (по всем проектам).
**Применим если:** существует `docs/projects/infrastructure/` и хотя бы у
одного проекта есть `services/`.

**Что искать:**

- `error`: сервис проекта без строки `placement` хотя бы в одном
  prod-рантайме (`runtime.environment: prod`).
- `error`: проектный платформенный ресурс `provided-by: own` без
  размещения.
- `warning`: размещение, противоречащее смыслу: prod-сервис на рантайме
  `environment: dev`; юнит на сервере, чьё `purpose` явно про другое;
  ёмкость сервера очевидно не бьётся с ролью юнита.
- `hint`: рантайм, в который ничего не размещено; сервер без рантаймов.

**Промпт-добавка:**

```
Source — реестры service.md и platform.md (own) всех проектов; destination
— infrastructure/{placement,runtime,server}.md. Это сверка полноты и
осмысленности размещения: каждый сервис и own-ресурс живёт где-то в prod?
размещение не противоречит назначению/ёмкости сервера? Битые рефы
placement (unit/runtime/servers) не ищи — это /infrastructure-audit;
здесь — семантика.
```

## platform-shared

**Source:** `docs/projects/*/services/platform.md` (строки
`provided-by: shared:<slug>`).
**Destination:** `docs/projects/infrastructure/shared-platform.md` +
`placement.md`.
**Скоуп:** верхнеуровневый, прогон один раз (по всем проектам).
**Применим если:** существует `docs/projects/infrastructure/`.

**Что искать:**

- `error`: потребность проекта `shared:<slug>` без записи в
  `shared-platform.md` (проект ждёт общий ресурс, которого у бизнеса нет).
- `error`: технологическое противоречие: проектная строка ждёт одну
  технологию (например `kafka`), а общий ресурс несёт другую (`nats`).
- `warning`: общий ресурс, который не потребляет ни один проект (сирота),
  или не размещён в `placement.md`.
- `hint`: два проекта держат `own`-ресурсы одной технологии и типа —
  напрашивается общий ресурс (осознанная изоляция допустима — отметить,
  не настаивать).

**Промпт-добавка:**

```
Source — строки provided-by: shared:<slug> в platform.md всех проектов;
destination — infrastructure/shared-platform.md и placement.md. Сверь
цепочку «потребность проекта → общий ресурс бизнеса → размещение» в обе
стороны: каждая потребность закрыта, каждый общий ресурс кому-то нужен и
где-то живёт, технологии совпадают.
```

## surface-design

**Source:** `docs/projects/<slug>/surface.md` (строка `<surface>`: `type`,
`web-kind`, `user`, `status`) + композиция поверхности: у `web` рода
`landing` и `site` — слой страницы (планы `site/<surface>/plans/`, тексты
`site/<surface>/copy/`, у рода `site` — карта `site/<surface>/site-map.yaml`),
у `web` рода `app` и у `admin`, `desktop`, `embed` — экраны
`screens/<surface>/` (статусы экранов, свод `map.md`).
**Destination:** `docs/projects/<slug>/design/` (статус ДС — карта решений
`system.yaml`; бриф на вид кабинета `app-brief.yaml`) +
`docs/projects/<slug>/design/<surface>/` (таблица «Приёмка»
`…/design/<surface>/review/REVIEW.md`, манифест `ready.yaml`; у сайта —
арт-дирекция `design/<surface>/art-direction.json`).
**Скоуп:** по проекту × поверхность.
**Применим если:** у поверхности маршрут дизайна (`type` — `web`, `admin`,
`desktop` или `embed`) и есть папка композиции (`site/<surface>/` или
`screens/<surface>/`). У `mobile`, `bot`, `api` и `other` своего макета
нет — облик мобильного приложения и бота — токены ДС и голос продукта;
единица пропускается с этой пометкой.

Макет страницы или экрана принят, когда в таблице «Приёмка» `REVIEW.md` у
него вердикт `accepted` или `accepted_with_notes`, а отпечаток одобрения
совпадает с текущими исходниками холста и входа, — тот же признак читают
`/design-audit` и репозиторий кода. Композиция закрыта: у сайта — планы
страниц `approved` (у рода `site` — всех страниц карты), у кабинета —
экраны `stable`. Форму, производные и свежесть файлов дизайна держит
`/design-audit`; здесь — ребро «закрытая композиция → принятый дизайн» и
смысл облика против назначения поверхности.

**Что искать:**

- `error`: папка `design/<surface>/` заведена, композиция закрыта, а
  принятого макета нет ни одного — дизайн начат и брошен (по образцу
  `surface-screen`).
- `warning`: закрытая страница или экран без принятого макета — одобрения
  нет или его отпечаток не совпадает с текущими исходниками.
- `warning`: облик поверхности противоречит её назначению по смыслу — бриф
  на вид кабинета или арт-дирекция сайта написаны для другой аудитории, чем
  `surface.user` (иллюстрация: рабочий кабинет бухгалтера с плотными
  таблицами описан как «праздничный, для подростков»).
- `hint`: строка приёмки страницы или экрана, которых больше нет в
  композиции (страницу убрали из карты или брифа, экран удалён).

Пример находки — иллюстрация, а не данные проекта:

```
[error] surface-design → у лендинга promo оба плана страниц утверждены и
  папка design/promo/ заведена, а в «Приёмке» REVIEW.md нет ни одной
  принятой страницы.
```

**Промпт-добавка:**

```
Source — строка <surface> реестра surface.md проекта <slug> (type,
web-kind, user, status) и композиция поверхности: у web рода landing и
site — слой страницы site/<surface>/ (планы plans/, тексты copy/, у рода
site — карта site-map.yaml), у web рода app и у admin, desktop, embed —
экраны screens/<surface>/ (статусы экранов, свод map.md). Destination —
design/ проекта (system.yaml — статус ДС, app-brief.yaml — бриф на вид
кабинета) и design/<surface>/ (review/REVIEW.md — таблица «Приёмка»,
ready.yaml; у сайта — art-direction.json).

Макет страницы или экрана принят, если в «Приёмке» вердикт accepted или
accepted_with_notes и отпечаток одобрения совпадает с текущими
исходниками холста и входа. Композиция закрыта: у сайта — планы страниц
approved (у рода site — все страницы карты), у кабинета — экраны stable.

design/<surface>/ заведена, композиция закрыта, а принятого макета нет ни
одного — error. Закрытая страница или экран без принятого макета или с
несовпавшим отпечатком — warning. Облик (бриф на вид, арт-дирекция) по
смыслу для другой аудитории, чем surface.user, — warning. Строка приёмки
страницы или экрана, которых нет в композиции, — hint. Схемы, покрытие
слотов, производные и свежесть файлов дизайна не проверяй — это
/design-audit. В finding указывай project и surface.
```

## facts-business

**Source:** `docs/projects/<slug>/facts.yaml` — факты продукта (второй язык
— `docs/projects/<slug>/facts.<lang>.yaml` с теми же id).
**Destination:** `docs/business/` (`profile.md`, `offering.md`,
`current-metric.md`, `competitor.md`, `material.md`) +
`docs/projects/<slug>/market.md`.
**Скоуп:** по проекту: факты — файл уровня продукта, один на все
поверхности.
**Применим если:** у проекта есть `facts.yaml`. Слоя бизнеса нет — единица
пропускается с пометкой: у продукта, начатого «просто сайтом», факты с
источником «сообщение заказчика» законны, и сверять их не с чем.

Факт — то, что страница утверждает от имени заказчика: его число, условие и
основание не должны спорить с тем, что бизнес записал о себе. Структуру
фактов — источник у каждого факта, схему, сроки, разрешения — проверяет
`/design-audit` (`claims_check.py lint-facts`); здесь — смысл факта против
бизнеса.

**Что искать:**

- `error`: факт по смыслу противоречит бизнесу — число расходится с
  `current-metric` той же величины, даты и охвата; условия оффера (цена,
  срок, что входит, гарантия) — с `offering`; сравнение с конкурентами — с
  `competitor` и `market.md`.
- `error`: источник факта — документ из `material.md` — не существует или о
  факте не говорит.
- `warning`: факт старше записи `current-metric` о той же величине — на
  странице прошлое число, в бизнесе уже свежее.
- `hint`: в бизнесе есть доказательство — награда, клиенты, сертификат,
  рейтинг, — которого нет в фактах.

Пример находки — иллюстрация, а не данные проекта:

```
[error] facts-business → факт «500 постоянных клиентов» (источник —
  сообщение заказчика) против current-metric «320 активных клиентов» той
  же даты и охвата.
```

**Промпт-добавка:**

```
Source — facts.yaml проекта <slug> (и facts.<lang>.yaml, если есть):
факты с числом, условием, основанием и источником (source: type,
document, date). Destination — docs/business/ (profile, offering,
current-metric, competitor, material) и market.md проекта.

Для каждого факта найди, что бизнес записал о той же величине, условии
или признании. Число против current-metric той же величины, даты и
охвата, условие оффера против offering, сравнение с конкурентами против
competitor и market — противоречие по смыслу — error. Документ-источник
ведёт в запись material.md, которой нет, или материал о факте не говорит
— error. Факт старше записи current-metric о той же величине — warning.
Доказательство в бизнесе (награда, клиенты, сертификат, рейтинг), которого
нет в фактах, — hint. Факт со слов заказчика без записи в бизнесе — не
находка: сверяй то, что есть с обеих сторон. Схему, наличие источника,
сроки и разрешения не проверяй — это /design-audit. В finding указывай
project.
```

## promise-product

**Source:** слой страницы поверхностей `web` рода `landing` и `site`:
смысл `site/<surface>/meaning.yaml` (ценностное предложение,
позиционирование, аудитория, границы), бриф `site/<surface>/site-brief.yaml`
(`offer`, `business.kpi`), утверждённые тексты страниц
`site/<surface>/copy/<page-id>.yaml` (заголовки, выгоды, обещания).
**Destination:** `docs/projects/<slug>/vision.md` (`Problem`, `Success`,
`Non-goals`, `Positioning`), `docs/projects/<slug>/capability/<surface>.md`
всех поверхностей, `boundary.md`, `user.md`, `market.md` проекта.
**Скоуп:** по проекту: обещания всех страниц продукта сверяются с одним
продуктом.
**Применим если:** у проекта есть поверхность `web` рода `landing` или
`site` со смыслом или планами страниц.

Продающий текст живёт только в текстах страницы, и он же — главный риск
маркетинговой копии: страница может пообещать то, чего продукт не делает.
`/project-audit` смотрит внутрь продукта, `/design-audit` — форму файлов
слоя страницы; обещание страницы против продукта сверяет этот угол.

**Что искать:**

- `error`: страница обещает то, что продукт намеренно не делает (`boundary`,
  vision `Non-goals`), или подаёт цель как гарантию результата — та же
  рамка, что у `goal-vision`: метрика — совместная цель, а не обещание.
- `warning`: выгода или обещание страницы без возможности ни на одной
  поверхности продукта. У продукта только из сайтов и лендингов файлов
  возможностей может не быть — тогда выгоды сверяются с vision (`Problem`,
  `Success`) и границами, а находки «без возможности» нет.
- `warning`: аудитория смысла (основной сегмент `meaning.audience`) не
  сходится с `user` продукта.
- `hint`: сильная боль пользователя (`user.pains`, vision `Problem`) без
  секции или сообщения страницы.
- `hint`: отличие из `market` не отражено в позиционировании.

Пример находки — иллюстрация, а не данные проекта:

```
[error] promise-product → заголовок первого экрана лендинга обещает
  «доставку за час», а boundary.md: «своей доставки нет — только
  самовывоз».
```

**Промпт-добавка:**

```
Source — слой страницы поверхностей web рода landing и site проекта
<slug>: meaning.yaml (value_proposition, positioning, audience,
boundaries), site-brief.yaml (offer, business.kpi), утверждённые тексты
страниц copy/<page-id>.yaml (заголовки, выгоды, обещания; черновые
варианты не сверяются). Destination — vision.md (Problem, Success,
Non-goals, Positioning), capability/<surface>.md всех поверхностей,
boundary.md, user.md, market.md.

Для каждого обещания страницы найди, что продукт делает на деле.
Обещание того, что продукт намеренно не делает (boundary, Non-goals), —
error. Цель или выгода, поданная как гарантия результата (иллюстрация:
«гарантируем рост заявок вдвое»), — error: метрика — совместная цель, не
обещание. Выгода без возможности ни на одной поверхности — warning; у
продукта без файлов возможностей (только сайт или лендинг) выгоды сверяй
с vision и boundary, находку «без возможности» не ставь. Аудитория смысла
не сходится с user продукта — warning. Сильная боль user или
vision.Problem без секции или сообщения страницы — hint; отличие из
market не отражено в позиционировании — hint. Факты против бизнеса —
угол facts-business, форма текстов и покрытие слотов — /design-audit. В
finding указывай project, а поверхность страницы — в evidence и
source-refs.
```
