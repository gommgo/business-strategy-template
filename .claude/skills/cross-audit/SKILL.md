---
name: cross-audit
description: Сквозной семантический аудит консистентности между слоями документации — business (профиль + реестр проблем business-problem) ↔ ajtbd ↔ swot ↔ hypothesis-map ↔ (множество проектов docs/projects/<slug>/: project ↔ interface ↔ domain ↔ screen). Запускает рой агентов параллельно: верхнеуровневые углы один раз (factor ↔ business, current-metric ↔ metric, addresses-problem ↔ business-problem, ajtbd segment-problem ↔ business-problem, ajtbd segment ↔ subject, ajtbd solution ↔ competitor/offering, business offering/channel ↔ ajtbd segment, проспективная согласованность market-maturity ↔ served, провенанс восходящего потока from-project ↔ проект), а углы swot/hypothesis-map ↔ продукт, ajtbd ↔ продукт и углы внутри проекта — ПО КАЖДОМУ проекту, с путями, заскоупленными в папку проекта (goal/metric ↔ vision, subject ↔ user, ajtbd segment ↔ user, ajtbd job ↔ vision.Success, ajtbd segment-problem ↔ vision.Problem, ajtbd job-graph value-mechanics ↔ capability, bet ↔ capability, capability ↔ hypothesis/job, user ↔ who, capability ↔ situation/domain, situation ↔ job/hypothesis, surface ↔ zone/screen, integration ↔ domain, constraint ↔ surface/integration, market ↔ capability). Читает оба слоя + state, ищет семантические тупики и противоречия — НЕ через slug-валидацию, а через смысловую проверку («пользователь без UX-покрытия», «метрика подана как гарантия», «субъект без пользователя», «сегмент без пользователя», «пользователь без сегмента», «проблема бизнеса без единого трения-доказательства», «субъект без сегмента», «механика ценности без capability», «зона висит без поверхности», «проект бьёт в несуществующую проблему», «проблема, которую не закрывает ни один проект»). Не правит, только отчёт. Использовать перед релизом, после крупного апдейта любого слоя, или когда deep-dive-скилы предлагают прогон. Сводный отчёт + список findings; deep-dive по каждому — отдельный шаг руками аналитика.
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
- `docs/projects/<slug>/` (vision + 7 kind продукта — user/capability/...)
  — **по одному на проект**.
- `docs/projects/<slug>/interface/` (UX — who/stage/situation/zone/block/...)
  — внутри проекта.
- `docs/projects/<slug>/domains/` (бизнес-домены бэкенда — если каталог есть)
  — внутри проекта.
- `docs/projects/<slug>/screens/` (композиция экранов — если каталог есть)
  — внутри проекта.

Папка `docs/projects/_canon/` — **канон формы, не данные проекта**; в
аудит **не входит** (исключается из перечисления проектов).

Бизнес-проблемы — общий слой, питающий **много** проектов: проблему могут
закрывать несколько проектов, проект — несколько проблем (M:N через
`vision.addresses-problem`). Углы business-problem ↔ продукт скоупятся к
конкретному проекту и учитывают, какие проблемы этот проект закрывает.

Аудит **не валидирует slug** между слоями (связи семантические, см.
`docs/projects/_canon/project/README.md`). Аудит читает оба слоя и
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
| `/cross-audit` | полный прогон: верхнеуровневые углы один раз + project-скоупленные углы по каждому проекту в `docs/projects/` (кроме `_canon`) |
| `/cross-audit <slug>` | прогон только по одному проекту (его project-скоупленные углы) + верхнеуровневые углы один раз |
| `/cross-audit <lens>` | прогон одного угла; для project-скоупленного — по всем проектам (или по `<slug> <lens>`) |
| `/cross-audit --quick` | быстрый прогон с 3 самыми важными углами (user↔who, capability↔situation, surface↔zone) по каждому проекту + addresses-problem↔business-problem один раз |

`lens` ∈ {`factor-business`, `currentmetric-metric`,
`addresses-problem-bizproblem`, `segmentproblem-bizproblem`, `segment-subject`,
`solution-business`, `business-segment`, `prospective-consistency`,
`provenance-upstream`,
`goal-vision`, `subject-user`, `segment-user`, `job-vision`,
`segmentproblem-vision`, `mechanic-capability`, `bet-capability`,
`capability-hypothesis`, `capability-job`, `user-who`,
`capability-situation`, `situation-job`, `situation-hypothesis`,
`capability-domain`, `surface-zone`, `surface-screen`, `integration-domain`,
`constraint-surface`, `market-capability`}.

**Скоуп углов** (подробнее — `references/angles.md`):

- **верхнеуровневые, прогон один раз** (общие слои business ↔ ajtbd ↔
  swot ↔ hypothesis-map, без проекта): `factor-business`,
  `currentmetric-metric`, `segmentproblem-bizproblem`, `segment-subject`,
  `solution-business`, `business-segment`, `prospective-consistency`,
  `provenance-upstream`.
- **верхнеуровневый M:N, прогон один раз над всеми проектами**:
  `addresses-problem-bizproblem` — связывает все `vision.addresses-problem`
  со строками реестра `business-problem`, в обе стороны.
- **по каждому проекту** (swot/hypothesis-map ↔ продукт проекта;
  скоупится к проблемам, которые проект закрывает): `goal-vision`,
  `subject-user`, `bet-capability`, `capability-hypothesis`.
- **по каждому проекту** (ajtbd ↔ продукт проекта): `segment-user`,
  `job-vision`, `segmentproblem-vision`, `mechanic-capability`,
  `capability-job`.
- **по каждому проекту** (внутри папки проекта + сквозные рёбра interface):
  `user-who`, `capability-situation`, `situation-job`,
  `situation-hypothesis`, `capability-domain`, `surface-zone`,
  `surface-screen`, `integration-domain`, `constraint-surface`,
  `market-capability`.

См. `references/angles.md`.

## Что делать при запуске

1. Прочитать `docs/business/README.md`, `docs/ajtbd/README.md`,
   `docs/swot/README.md`, `docs/hypothesis-map/README.md`,
   `docs/projects/README.md`, `docs/projects/_canon/project/README.md`,
   `docs/projects/_canon/interface/README.md`, и (если есть)
   `docs/projects/_canon/domains/README.md` /
   `docs/projects/_canon/screens/README.md` — освежить каноны формы.
2. Прочитать `references/angles.md` — список углов и контекста на
   каждый.
3. **Перечислить проекты.** Взять подкаталоги `docs/projects/`,
   **исключив `_canon`** (это канон формы, не данные). Каждый
   оставшийся каталог `docs/projects/<slug>/` — отдельный проект.
   Если `<slug>` дан аргументом — список из одного проекта.
4. **Проверить наличие вложенных слоёв на каждый проект.**
   `docs/projects/<slug>/domains/` и `docs/projects/<slug>/screens/`
   могут отсутствовать (продукт без backend, или ещё не дошли) —
   независимо в каждом проекте. Углы, требующие отсутствующего слоя,
   пропускаются для этого проекта с пометкой в отчёте.
5. Определить, какие углы применимы — по args или по полному прогону —
   и **раскрыть** project-скоупленные углы в пары `(проект × lens)`:
   один агент на каждую пару. Верхнеуровневые углы (`factor-business`,
   `currentmetric-metric`, `addresses-problem-bizproblem`,
   `segmentproblem-bizproblem`, `segment-subject`, `solution-business`,
   `business-segment`, `prospective-consistency`, `provenance-upstream`) —
   по одному агенту, без проекта.
6. **Спавнить агентов параллельно** (см. ниже). При множестве проектов
   рой широкий: `(число проектов × project-углы) + верхнеуровневые`.
7. Собрать ответы. Каждый агент возвращает findings в едином формате
   (с указанием проекта, к которому относится).
8. Сгруппировать findings по `(проект, угол)`, отсортировать по
   severity. Верхнеуровневые — в отдельную группу «общие слои».
9. Через `AskUserQuestion` пройти по top-K findings — что делать с
   каждым: «принять как корректное», «нужна правка», «false positive».
10. Перезаписать `audit-state/last-report.md` с reasoning-trace и
    решениями аналитика.

## Рой агентов

Механизм неизменный: один lens (для project-скоупленного — одна пара
`проект × lens`) = один агент, все в одном message-блоке параллельно.
Меняется только то, что **пути параметризованы `<project-slug>`**: перед
спавном скилл подставляет конкретный slug в шаблоны путей из
`references/angles.md`.

Каждый агент получает:

- **проект** (`<project-slug>`), к которому относится прогон — для
  project-скоупленных углов; для верхнеуровневых — пометку «общие слои».
- путь к двум каталогам слоёв с **уже подставленным** `<project-slug>`
  (например `docs/projects/<slug>/user.md`, `docs/business/`);
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
Source layer: <path-1>     (с уже подставленным <project-slug>)
Destination layer: <path-2>
Проблемы этого проекта (для swot/hypothesis-map↔продукт): [<problem-slug>, ...]

Цель: семантически сопоставить записи в source и destination — найти
тупики, противоречия, потери покрытия. Не slug-валидация: связь
семантическая, агент сам решает, соответствует ли запись X записи Y.
Сопоставление держи в границах проекта <project-slug> (для углов
business-problem↔продукт — в границах перечисленных проблем).

Прочитай:
- <конкретные файлы из source-layer>
- <конкретные файлы из destination-layer>
- state скилла, обслуживающего эти слои (для project-скоупленных —
  state, относящийся к <project-slug>; если файлы есть).

Найди:
- <конкретные паттерны для этого lens из angles.md>

Верни ТОЛЬКО валидный JSON по схеме findings-format.md, без пояснений
и preamble. Каждый finding:
{
  "lens": "<lens>",
  "project": "<project-slug>",   (или null для верхнеуровневых углов)
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
| `error` | Семантический тупик, ломает целостность | user без покрытия в interface.who; surface без зон; integration без бизнес-домена; `vision.addresses-problem` ссылается на несуществующую проблему |
| `warning` | Подозрительная несостыковка | capability упомянута, но в interface ситуаций под неё «впритык»; market покрывает capability, которой у нас нет; constraint не привязан ни к surface, ни к integration |
| `hint` | Гипотеза / возможная новая capability | market показывает gap, у нас нет capability на эту территорию; в interface есть ситуация, которая не имеет capability-якоря в project; проблема в `business-problem`, которую не закрывает ни один проект |

## Углы проверки (lenses)

Полный список — `references/angles.md`. `<slug>` = `<project-slug>`,
подставляется на спавне. Колонка «скоуп» отмечает: `★` — прогон один
раз; `по проекту` — раскрывается в пары `(проект × lens)`. Краткая карта:

| lens | source | destination | скоуп | основной вопрос |
|---|---|---|---|---|
| `factor-business` | `docs/swot/factor.md` | `docs/business/` (profile, competitor) | ★ | каждый SWOT-фактор опирается на картину бизнеса? |
| `currentmetric-metric` | `docs/business/current-metric.md` | `docs/hypothesis-map/metric.md` | ★ | baseline целевой метрики (`current`) взят из текущего KPI бизнеса? |
| `addresses-problem-bizproblem` | `docs/projects/*/vision.md` (`addresses-problem`) | `docs/business/business-problem.md` | ★ | каждый ref проекта попадает в реальную проблему? есть ли проблема, в которую не бьёт ни один проект? (M:N, обе стороны) |
| `segmentproblem-bizproblem` | `docs/ajtbd/segment-problem.md` | `docs/business/business-problem.md` | ★ | трение клиента доказывает проблему бизнеса? есть ли проблема бизнеса без единого трения-доказательства? |
| `segment-subject` | `docs/ajtbd/segment.md` | `docs/hypothesis-map/subject.md` | ★ | субъект влияния вырастает из сегмента? есть ли субъект без сегмента? |
| `solution-business` | `docs/ajtbd/solution.md` | `docs/business/` (competitor, offering) | ★ | нанятое решение (`maps-to`) сходится с игроком рынка / собственным офером? |
| `business-segment` | `docs/business/offering.md` (`for-segment`), `channel.md` (`serves-segment`) | `docs/ajtbd/segment.md` | ★ | межслойные ссылки оферов/каналов попадают в реальные сегменты и осмысленны? |
| `goal-vision` | `docs/hypothesis-map/goal.md`, `metric.md` (по проблемам проекта) | `docs/projects/<slug>/vision.md` | по проекту | цель/метрика закрываемой проблемы отражены в vision.Success (как таргет, не гарантия)? |
| `subject-user` | `docs/hypothesis-map/subject.md` (по проблемам проекта) | `docs/projects/<slug>/user.md` | по проекту | субъект влияния соответствует user продукта? |
| `segment-user` | `docs/ajtbd/segment.md` | `docs/projects/<slug>/user.md` | по проекту | сегмент рынка соотносится с user продукта (разные сущности, но связаны)? сегмент без пользователя / пользователь без сегмента? |
| `job-vision` | `docs/ajtbd/job.md` (`big`/`core`) | `docs/projects/<slug>/vision.md` (Success) | по проекту | успех продукта целит в Big/Core Job сегмента? |
| `segmentproblem-vision` | `docs/ajtbd/segment-problem.md` | `docs/projects/<slug>/vision.md` (Problem) | по проекту | трение клиента отражено в vision.Problem продукта? |
| `mechanic-capability` | `docs/ajtbd/job-graph.md` (`value-mechanics`) | `docs/projects/<slug>/capability.md` | по проекту | механика ценности из графа реализована capability? механика без capability? |
| `bet-capability` | `docs/swot/bet.md`, `goal.md` (по проблемам проекта) | `docs/projects/<slug>/capability.md` | по проекту | ставка/цель реализуется хотя бы одной capability проекта? |
| `user-who` | `docs/projects/<slug>/user.md` | `docs/projects/<slug>/interface/who.md` | по проекту | каждый user имеет хотя бы одно who-покрытие? каждое who сводимо к одному user? |
| `capability-situation` | `docs/projects/<slug>/capability.md` | `docs/projects/<slug>/interface/situation.md` | по проекту | каждая capability реализуется ≥1 ситуацией? есть ли ситуации без capability-якоря? |
| `capability-domain` | `docs/projects/<slug>/capability.md` | `docs/projects/<slug>/domains/` (если есть) | по проекту | у каждой capability есть бизнес-код в domain? |
| `surface-zone` | `docs/projects/<slug>/surface.md` | `docs/projects/<slug>/interface/zone.md` | по проекту | каждая surface имеет ≥1 зону? каждая зона принадлежит surface? |
| `surface-screen` | `docs/projects/<slug>/surface.md` | `docs/projects/<slug>/screens/` (если есть) | по проекту | каждая surface имеет ≥1 screen-композицию? |
| `integration-domain` | `docs/projects/<slug>/integration.md` | `docs/projects/<slug>/domains/` (если есть) | по проекту | каждая integration имеет адаптер в domain? |
| `constraint-surface` | `docs/projects/<slug>/constraint.md` | `docs/projects/<slug>/surface.md`, `docs/projects/<slug>/integration.md` | по проекту | каждый constraint привязан семантически к surface или integration? |
| `market-capability` | `docs/projects/<slug>/market.md` | `docs/projects/<slug>/capability.md` | по проекту | конкуренты покрывают наши capabilities? есть ли gap, где конкурент умеет, а мы нет (signal к новой capability)? |

## Формат отчёта

```
=== /cross-audit ===
Слои: business, ajtbd, business-problem (общие) + проекты: referral-network, partner-portal
Проектов: 2 · углы: 7 верхнеуровневых + 15 по referral-network + 12 по partner-portal = 34 запущено, 34 ответили
Время: <duration> · агентов: 34

— Общие слои —

[error] addresses-problem-bizproblem → проект partner-portal бьёт в проблему
  `legacy-sync`, которой нет в docs/business/business-problem.md.
  Доказательство: projects/partner-portal/vision.md addresses-problem =
    [`paid-churn`, `legacy-sync`]; business/business-problem.md → строки [`paid-churn`,
    `slot-utilization`] — `legacy-sync` отсутствует.
  Что делать: завести проблему `legacy-sync` через
  /business-deep-dive business-problem, либо убрать ref в /project-deep-dive
  partner-portal.

[hint] addresses-problem-bizproblem → проблему `slot-utilization` не
  закрывает ни один проект.
  Доказательство: business/business-problem.md:slot-utilization; ни один
    projects/*/vision.md не содержит её в addresses-problem.
  Что делать: решить — нужен ли проект под неё, или проблема пока вне
  scope (зафиксировать).

[warning] segmentproblem-bizproblem → проблему бизнеса `paid-churn` не
  доказывает ни одно трение клиента из docs/ajtbd/segment-problem.md.
  Доказательство: business/business-problem.md:paid-churn; в segment-problem.md нет ни одной
    записи с feeds-problem=`paid-churn` или семантически бьющей в эту
    проблему.
  Что делать: разведать трение клиента под эту проблему через
  /job-graph-deep-dive, либо зафиксировать, что проблема опирается на
  другой источник доказательства.

[hint] segment-subject → субъект `partner-admin` (business-problem) не
  выводится ни из одного сегмента docs/ajtbd/segment.md.
  Доказательство: subject.md:partner-admin; в segment.md нет сегмента,
    чей бандл работ соответствует этому субъекту.
  Что делать: проверить через /segment-deep-dive, есть ли сегмент под
  этого субъекта, или субъект задан вне разведки спроса.

— Проект referral-network —

[error] user-who → user:doctor не имеет соответствия в
  projects/referral-network/interface/who.md (нет роли, выполняющей
  действия персонажа).
  Доказательство: user:doctor.context = «врач инициирующей клиники»;
    в who.md нет ни одной записи с инициирующей ролью.
  Что делать: либо завести who:doctor через /interface-deep-dive
  referral-network who, либо пересмотреть user в /project-deep-dive
  referral-network user:doctor.

[error] surface-zone → surface:web-partner не имеет ни одной зоны в
  projects/referral-network/interface/zone.md (упоминает только
  админ-зоны).
  Доказательство: surface:web-partner.type=web; zone.md →
    [`admin-overview`, `study-card`] — все принадлежат admin-поверхности.
  Что делать: завести зоны для web-partner через /interface-deep-dive
  referral-network zone, или пересмотреть surface.

[warning] capability-domain → capability:send-referral не имеет явного
  домена в projects/referral-network/domains/.
  Доказательство: capability:send-referral.value = «один клик»; в
    domains/ есть только `auth`, `billing`, `inventory`.
  Что делать: добавить домен `referrals` через /domain-deep-dive,
  или пересмотреть, действительно ли capability нужна.

— Проект partner-portal —

[hint] market-capability → конкурент klara-app покрывает «mobile-первый
  опыт», у нас нет capability на mobile.
  Доказательство: market:klara-app.description = «mobile-first
    referrals»; projects/partner-portal/capability.md → нет записи про
    mobile.
  Что делать: рассмотреть, нужно ли это вам — открыть
  /project-deep-dive partner-portal capability для обсуждения.

Сводка: 3 error / 1 warning / 2 hint.
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
projects: [referral-network, partner-portal]
top-level-lenses-run: 7
project-lens-runs: 27   # сумма по всем (проект × lens)
per-project-layers:
  referral-network: { project: yes, interface: yes, domain: yes, screen: no }
  partner-portal:   { project: yes, interface: yes, domain: no,  screen: no }
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
  - finding-1 (error): project partner-portal → проблема `legacy-sync` не
    в business-problem → verdict: needs-fix
  - finding-2 (hint): проблему `slot-utilization` не закрывает ни один
    проект → verdict: deferred

## Проект: referral-network

### Lens: user-who
- agent-id: agent-7c
- duration: 18s
- findings: 3
- verdicts: [accepted, needs-fix, accepted]
- details:
  - finding-1 (error): … → verdict: needs-fix
  - finding-2 (warning): … → verdict: accepted
  - …

### Lens: capability-situation
- …

## Проект: partner-portal

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
- lens: user-who; project: referral-network; pattern: "user:doctor
  without who"; reason: <от аналитика, через Other в AskUserQuestion>;
  suppressed-since: <ts>
```

Suppression несёт `project` (для верхнеуровневых углов — `project: —`),
чтобы подавление в одном проекте не глушило тот же паттерн в другом. При
следующем прогоне агент-lens получает relevant для его `(проект, lens)`
suppressions как контекст и **не** генерирует те же findings, если они
подпадают под паттерн. Suppressions можно вручную удалить из файла, чтобы
заново всплыли.

## Что не делать

- **Не править артефакты.** Cross-audit — только отчёт и решения
  аналитика, что с findings делать.
- **Не вызывать другие скилы автоматически.** В next-actions — текст,
  что запустить.
- **Не выдумывать findings.** Если агент вернул пустой массив — так
  и пишем «0 findings» по этому lens.
- **Не включать `_canon` в перечисление проектов.** `docs/projects/_canon/`
  — канон формы, не данные; его записи в аудит не идут.
- **Не игнорировать отсутствующие слои.** Если у проекта нет
  `docs/projects/<slug>/domains/` — lens `capability-domain` и
  `integration-domain` пропускаются **для этого проекта** с явной
  пометкой «слой не существует» в отчёте. У другого проекта они могут
  при этом отрабатывать.
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
  инструмент; в `project-deep-dive-for-business` он не упоминается.
