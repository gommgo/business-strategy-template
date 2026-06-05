# Roadmap — фундаментальный рефакторинг системы проектирования

> **Статус документа.** Это рабочий план миграции, а не канонический
> артефакт. Он по природе описывает переход «текущее → целевое», поэтому
> на него **не распространяется** forward-only (который запрещает «было/
> стало» в _артефактах_). После реализации файл удаляется — история
> переходов остаётся в `git log`. Все артефакты, которые план порождает,
> пишутся уже строго forward-only (без следов переименований).

Документ — единственный источник правды по этому рефакторингу: что
делаем, почему, в каком порядке. Реализация — отдельными фазами, каждая —
reviewable-батч под git-ревью. Коммит/push — гейт человека.

---

## 1. Зачем (цели рефакторинга)

Текущая система — строгий DAG сверху вниз (`business → ajtbd →
business-problem → projects`), с линейной лестницей 14 шагов и ~25
скиллами, каждый из которых аналитик выбирает руками. На практике
информация приходит **не линейно** (созвон на 3 часа, разрозненные
заметки, сигнал из жизни), а наполнение/актуализация/рефакторинг/очистка/
аудит требуют входа «не думая, в какой слой». Плюс накопились
терминологические и структурные долги.

Цели:

1. **Два скилла-оркестратора** как единственные точки входа и ведения
   state — аналитический и клиентский, перекрёстно видящие друг друга.
2. **Чистая послойная структура**: `persona→user`; SWOT и Карта гипотез —
   самостоятельные слои; `frame` переименован в `business-problem` и
   переехал в `business`; папка `docs/business-problem/` исчезает.
3. **Сквозная связующая ткань** между слоями (`situation ↔ job ↔
   capability ↔ hypothesis`, четвёрка `who/user/segment/subject`) —
   списками, с прочерками, авторски снизу-вверх.
4. **Восходящий поток** `project → business` по жизненному циклу проекта
   (на `stable` продукт меняет реальность бизнеса), с провенанс-ссылками.
5. **Готовность к любому типу инициативы** (b2b/b2c, внутр./внешн., новая/
   улучшаемая услуга) через три оси на `vision` + проспективные сегменты/
   проблемы.
6. **Синтез методички** `ajtbd-knowledge/` в references профильных
   скиллов; сырьё-папка удаляется.

---

## 2. Принятые решения (decision log)

Зафиксировано в интерактивной проработке — переспрашивать не нужно:

| # | Решение | Выбор |
|---|---|---|
| D1 | Форма энтрипоинта | **Два скилла-оркестратора** (аналитик + клиент), единый state каждый, перекрёстная read-only видимость, сами классифицируют сырьё и маршрутизируют под-скиллы. Существующие скиллы — исполнители. |
| D2 | Слой interface | Структуру **не трогаем**; `situation` получает связи с `job`, `capability`, `hypothesis`. Понятие «КРИ» **не вводим** — ни в каталогах, ни в нарративе. |
| D3 | Восходящий поток | **Процесс-нудж + провенанс-ссылки** (`*.from-project`). |
| D4 | Новый рынок / b2c | **Проспективные сегменты/проблемы + три оси на `vision`** (`audience` + `intent` + `market-maturity`). |
| D5 | `frame` | **Переименован в `business-problem`** (kind), переезжает в `docs/business/`. Папка `docs/business-problem/` исчезает. |
| D6 | SWOT / Карта гипотез | **Два самостоятельных слоя**: `docs/swot/` (`factor`, `bet`) и `docs/hypothesis-map/` (`goal`, `metric`, `subject`, `hypothesis`, `task`). |
| D7 | `persona` | **Переименован в `user`** (kind + все ссылки). |
| D8 | Авторская сторона сквозных связей | **Снизу-вверх**: проектная сущность ссылается на глобальную; обратное выводит `cross-audit`. Значения — списки, прочерк допустим. |
| D9 | `subject ↔ segment` | Авторски на `subject` (`subject.segments`). |
| D10 | Синтез `ajtbd-knowledge/` | **Дистилляция** в references профильных скиллов; демо-графы — короткие примеры; папка удаляется. |

**Дефолты, принятые планом (поправить здесь, если не так):**

- Новые каталоги: `docs/swot/`, `docs/hypothesis-map/`.
- `business-problem.md` (бывш. `frame.md`) лежит прямо в `docs/business/`.
- Жизненный цикл проекта (`draft→accepted→build→mvp→beta-testing→stable→
  updating`) — отдельная ось `lifecycle:` в `vision.md`, **сосуществует**
  с per-record `status: draft|stable` (зрелость записи, не путать).
- Имена оркестраторов: **`entrypoint`** (аналитик) и
  **`entrypoint-for-business`** (клиент).

---

## 3. Целевая архитектура

### 3.1 Слои (сверху вниз)

| каталог | роль | глоб./проект | kinds |
|---|---|---|---|
| `docs/business/` | кто бизнес + **его проблемы** | глобальный | `profile` (singleton) · `offering` · `channel` · `competitor` · `current-metric` · `material` · **`business-problem`** (бывш. `frame`) |
| `docs/ajtbd/` | сегменты по работам + граф работ | глобальный | `segment` · `job` · `job-graph` · `solution` · `segment-problem` |
| `docs/swot/` | LinkedSWOT | глобальный | `factor` · `bet` |
| `docs/hypothesis-map/` | Карта гипотез | глобальный | `goal` · `metric` · `subject` · `hypothesis` · `task` |
| `docs/projects/<slug>/` | продукт | по проекту | `vision` (singleton) + 7 kind (`user` (бывш. `persona`) · `capability` · `boundary` · `surface` · `integration` · `constraint` · `market`) |
| `docs/projects/<slug>/interface/` | UX (как взаимодействует) | по проекту | `who` · `stage` · `situation` · `zone` · `block` · `ux-substrate` · `data-items` |
| `docs/projects/<slug>/domains/` | DDD (опц.) | по проекту | агрегаты/события/use-case/… |
| `docs/projects/<slug>/screens/` | композиция | по проекту | `flow` · `screen` · `block` · `shell` |
| `docs/projects/_canon/` | канон формы | образец | read-only |

Поток семантики прежний (`business → ajtbd → swot → hypothesis-map →
projects`), но **обогащён сквозными рёбрами** (§3.3) и **восходящим
контуром** (§6). «Проблема бизнеса» теперь живёт в `business` как
`business-problem`; на неё ссылаются SWOT, Карта гипотез и `vision`
(`addresses-problem`).

### 3.2 Терминологическая чистка (параллель имён)

- `segment-problem` (трение **клиента** с решением, `ajtbd`) ↔
  `business-problem` (боль **бизнеса**, `business`). Чистая пара,
  путаницу снимает именование.
- `user` (пользователь нашего продукта, `project`) ↔ `who` (участник
  системы, `interface`) ↔ `segment` (рынок/клиент по работам, `ajtbd`) ↔
  `subject` (носитель самодвижения, чьё поведение двигаем, `hypothesis-map`).
  Четыре разные сущности, **мягко** связанные (§3.3).

### 3.3 Сквозная связующая ткань (новое)

Все рёбра — **семантические** (не slug-валидируемые), значения —
**списки** slug-рефов, **прочерк `—` допустим** (вытекает не всегда).
Авторская сторона — **снизу-вверх** (D8): хранит ссылку более конкретная/
проектная сущность; обратную сторону выводит `/cross-audit`. Глобальные
слои (`job`, `segment`, `subject`, `hypothesis`) остаются чистыми и не
знают про конкретные проекты.

**Группа A — поток ценности `situation ↔ capability ↔ hypothesis ↔ job`:**

| ребро | авторское поле (новое) | откуда → куда |
|---|---|---|
| situation → job | `situation.jobs` | interface (проект) → ajtbd (глоб.) |
| situation → capability | `situation.capabilities` | interface → project (тот же проект) |
| situation → hypothesis | `situation.hypotheses` | interface → hypothesis-map (глоб.) |
| capability → hypothesis | `capability.hypotheses` | project → hypothesis-map (глоб.) |
| capability → job | `capability.jobs` | project → ajtbd (глоб.) |
| hypothesis → job | `hypothesis.jobs` | hypothesis-map → ajtbd (глоб.) |

> Прямое ребро `capability.jobs` **вводим явно** (а не только выводим
> через `job-graph.value-mechanics`): возможность продукта прямо целит в
> работу(ы) сегмента. Все рёбра группы — списки с прочерком.

**Группа B — четвёрка адресатов `who/user/segment/subject`:**

| ребро | авторское поле (новое) | откуда → куда | обяз.? |
|---|---|---|---|
| who → user | `who.users` | interface → project | опц. |
| user → segment | `user.segments` | project → ajtbd | опц. |
| subject → segment | `subject.segments` | hypothesis-map → ajtbd | **да** (D9) |
| subject → user | `subject.users` | hypothesis-map → project | опц. |

Все четыре связываются минимум через `segment` (who→user→segment,
subject→segment). Это «по возможности», не инвариант — `cross-audit`
поднимает как hint, не как блок.

### 3.4 Два оркестратора (D1)

| | `entrypoint` (аналитик) | `entrypoint-for-business` (клиент) |
|---|---|---|
| вход | единственная точка входа аналитика по всем слоям | единственная точка входа клиента/основателя |
| охват | `business`/`ajtbd`/`swot`/`hypothesis-map`/`projects` + аудиты | те же слои в бизнес-языке |
| режимы | наполнить · актуализировать · рефакторить · чистить · аудитить | то же, упрощённо («закрыто / в работе») |
| сырьё | принимает любой объём (3-часовой транскрипт, заметки, ссылки), сам классифицирует по слоям и маршрутизирует | то же, без жаргона |
| state | **единая точка ведения** (`.claude/skills/entrypoint/state/`) — индекс/маршрутный журнал/открытые нити; детальный per-kind state ведут скиллы-исполнители | `.claude/skills/entrypoint-for-business/state/` + эскалация в ветку `client` |
| перекрёстность | read-only видит state клиентского | read-only видит state аналитического |
| исполнители | вызывает существующие `*-deep-dive`/`*-audit` | `*-for-business`-исполнители + SWOT/Карту гипотез ведёт **сам** (отдельных `*-for-business`-скиллов для них нет, D-O4) |

Оркестратор **сам решает**, какой под-скилл активировать и куда писать.
Существующие скиллы не выбрасываются — становятся исполнителями за
единым фасадом. «Энтрипоинт на всё» = `entrypoint`
(+ `entrypoint-for-business` для клиента).

---

## 4. Изменения по слоям (data-model, по полям)

> Везде: H1 = имя файла = kind, без frontmatter; первые колонки `slug ·
> name · …`; последняя — `status` (`draft|stable`, зрелость записи). Новые
> поля — списки slug-рефов с прочерком, если не сказано иначе.

### 4.1 `docs/business/`

- **Новый kind `business-problem.md`** (перенос+переименование `frame.md`):
  колонки `slug · name · problem · guarantee · target · out-of-control ·
  scope · served · from-project · status`.
  - `served` — enum `served | prospective` (D4): обслуживается ли бизнесом
    рынок этой проблемы, или это разведка под будущую инициативу.
  - `from-project` — провенанс (D3): какой проект «проявил/подтвердил» эту
    проблему (slug | `—`).
- **`offering.md`** +`from-project` (slug | `—`) — провенанс восходящего
  потока: офер, родившийся из дозревшего продукта.
- **`current-metric.md`** +`from-project` (slug | `—`) — новые baseline,
  привнесённые продуктом.
- **`profile.md`** — без новых полей; но в каноне отметить, что профиль
  актуализируется восходящим потоком (продукт меняет «как бизнес
  зарабатывает»).
- `offering.for-segment` / `channel.serves-segment` — без изменений
  (ссылаются на `ajtbd/segment`, которые теперь могут быть `prospective`).

### 4.2 `docs/ajtbd/`

- **`segment.md`** +`served` (enum `served | prospective`) +`from-project`
  (slug | `—`). Проспективный сегмент — известная work-карта рынка,
  который бизнес ещё не обслуживает.
- `job` / `job-graph` / `solution` / `segment-problem` — **без новых
  авторских полей** (сквозные рёбра авторятся снизу, на проектной/
  hypothesis-map стороне). `segment-problem.feeds-problem` теперь
  ссылается на `business/business-problem` (бывш. `frame`).
- Методологические инварианты `ajtbd-audit` — без изменений; добавить
  правило «проспективный сегмент допускается без `offering`».

### 4.3 `docs/swot/` (новый слой из SWOT-семьи)

- Переносим `factor.md`, `bet.md` из `business-problem/`.
- Колонка `problem` в обоих → ссылается на `business/business-problem`.
- README слоя (`docs/swot/README.md`) — выжимка LinkedSWOT (из бывш.
  `business-problem/README.md` + `business-problem-deep-dive/references/
  methodology.md`).
- Инварианты («фактор без ставки», «ставка-висяк `bet.promoted-to`») →
  свой аудит (§7).

### 4.4 `docs/hypothesis-map/` (новый слой из Карты-гипотез-семьи)

- Переносим `goal.md`, `metric.md`, `subject.md`, `hypothesis.md`,
  `task.md`.
- Колонка `problem` везде → ссылается на `business/business-problem`.
- **`subject.md`** +`segments` (D9, авторски: subject→ajtbd) +`users`
  (опц.). `subject.motivation` остаётся опорой `hypothesis.because`.
- **`hypothesis.md`** +`jobs` (авторски: hypothesis→ajtbd). Структура
  `if/then/because/so` сохраняется; `so` по-прежнему бьёт в `metric`.
- README + инварианты Карты гипотез («задача-сирота», «тогда без метрики»,
  «метрика без влияния», «целевая без guardrail») → свой аудит (§7).

### 4.5 `docs/projects/<slug>/` (продукт)

- **`persona.md` → `user.md`** (D7). H1 `user`. Колонки без изменений по
  смыслу: `slug · name · description · context · jobs · pains · success ·
  status` +`segments` (B-ребро user→segment, опц.).
  - Все ссылки `capability.persona → capability.user`,
    `surface.persona → surface.user`.
- **`capability.md`** `persona → user`; +`hypotheses` (A-ребро
  capability→hypothesis-map) +`jobs` (A-ребро capability→ajtbd).
- **`surface.md`** `persona → user`.
- **`vision.md`** (singleton):
  - +`audience` — enum `b2b | b2c | b2b2c | internal | gov` (полный
    набор, D4/O3).
  - +`intent` — enum `new-service | improve-service | internal-problem |
    client-problem` (полный набор, D4/O3).
  - +`market-maturity` — enum `prospective | served` (D4): целит ли продукт
    в обслуживаемый рынок или разведывает новый.
  - +`lifecycle` — enum `draft | accepted | build | mvp | beta-testing |
    stable | updating` (жизненный цикл проекта; отдельно от `status`
    зрелости записи). Триггер восходящего потока — переход в `stable` (§6).
  - `addresses-problem` — теперь ссылается на `business/business-problem`
    (бывш. `frame`).

### 4.6 `docs/projects/<slug>/interface/` (D2)

- Структура и 6 из 7 сущностей — **без изменений**. Каталог `interface/`
  не переименовываем; понятие «КРИ» **не вводим** (O5).
- **`situation.md`** +`jobs` (→ ajtbd) +`capabilities` (→ project)
  +`hypotheses` (→ hypothesis-map) — A-рёбра, авторски на situation.
- **`who.md`** +`users` (→ project) — B-ребро, опц.
- README `interface` — добавить только описание новых связей `situation`/
  `who` в раздел «Связи»; нарратив слоя не меняем.

### 4.7 Сводка новых полей (чек-лист реализации)

```
business/business-problem.md   : served, from-project          (+перенос frame)
business/offering.md           : from-project
business/current-metric.md     : from-project
ajtbd/segment.md               : served, from-project
hypothesis-map/subject.md      : segments, users
hypothesis-map/hypothesis.md   : jobs
projects/_canon/project/user.md      : segments                (+rename persona)
projects/_canon/project/capability.md: hypotheses, jobs, user(rename)
projects/_canon/project/surface.md   : user(rename)
projects/_canon/project/vision.md    : audience, intent, market-maturity, lifecycle
projects/_canon/interface/situation.md: jobs, capabilities, hypotheses
projects/_canon/interface/who.md     : users
```

---

## 5. Оркестраторы — устройство

### 5.1 `entrypoint` (аналитик)

Структура как у прочих скиллов: `SKILL.md` + `references/` + `state/`.

- **SKILL.md** — точки входа, режимы, карта маршрутизации, контракт
  делегирования.
- **references/**:
  - `intake.md` — конвейер приёма сырья: ingest → сегментация по темам →
    классификация чанка к слою/kind → предложение маршрута (какой
    скилл-исполнитель + какая сущность) → по подтверждению `AskUserQuestion`
    делегирование. Рассчитан на «3-часовой транскрипт, бог знает что».
  - `routing.md` — таблица «сигнал → слой → скилл-исполнитель» по всем
    слоям и режимам (наполнить/актуализировать/рефакторить/чистить/аудит).
  - `state-model.md` — формат единого state: маршрутный журнал, открытые
    нити, срез по слоям, ссылки на детальный per-kind state исполнителей;
    forward-only.
  - `cross-read.md` — правила read-only видимости клиентского state и
    anti-leak.
  - `lifecycle-upstream.md` — процедура восходящего потока (§6).
- **Режимы (намерения):**
  - `наполнить` — новые/частичные сущности (делегирует `*-deep-dive`).
  - `актуализировать` — сверить с новым сырьём, обновить.
  - `рефакторить` — переименования/переносы/слияния slug с каскадом.
  - `чистить` — удаления с показом каскада ссылок.
  - `аудитить` — запустить нужный аудит-рой (`*-audit`/`cross-audit`).

### 5.2 `entrypoint-for-business` (клиент)

Зеркало `entrypoint` в бизнес-языке: те же режимы, но «закрыто / в
работе», anti-leak, эскалация `**жду аналитика**` + push в ветку
`client`. Принимает сырьё клиента так же. Перекрёстно read-only видит
state `entrypoint`. **SWOT и Карту гипотез в клиент-режиме ведёт сам**
(отдельных `swot-*-for-business`/`hypothesis-map-*-for-business` скиллов
нет — D-O4); под бизнес-, ajtbd- и project-слои зовёт существующие
`*-for-business`-исполнители.

### 5.3 Соотношение со старыми скиллами

Старые `*-deep-dive`/`*-audit`/`*-for-business` **остаются** как
исполнители; их прямой вызов из чата допустим, но рекомендуемый вход —
оркестратор. `getting-started`/`README` переписывают воркфлоу вокруг двух
энтрипоинтов (§10).

---

## 6. Восходящий поток `project → business` (D3)

**Триггер.** Оркестратор `entrypoint` замечает переход `vision.lifecycle →
stable` (или ручной запрос «сверить продукт с бизнесом»).

**Процедура `lifecycle-upstream` (reconcile-up) в `entrypoint`, всё через
`AskUserQuestion`, без авто-записи:**

1. Продукт как **офер**: предложить новую/обновлённую запись
   `business/offering` с `from-project = <slug>`.
2. **Профиль**: если продукт сменил «как бизнес зарабатывает/кого
   обслуживает» — предложить правку `profile.md`.
3. **Метрики**: новые baseline продукта → кандидаты в
   `business/current-metric` с `from-project`.
4. **Проспективное → обслуживаемое**: если продукт целил в
   `market-maturity: prospective`, предложить повысить связанные
   `ajtbd/segment.served` и `business/business-problem.served` →
   `served`, проставив `from-project`.

Провенанс-поля (`*.from-project`) делают контур наблюдаемым; обратную
сторону (какой продукт что породил) сводит `cross-audit`. Контур —
**процессный**, не ломает «downstream read-only» для соседних форков
(они по-прежнему только читают `docs/`).

---

## 7. Любой тип инициативы (D4)

- Три оси на `vision` (§4.5) описывают b2b/b2c/внутр., новизну и зрелость
  рынка.
- **Проспективные сущности**: `ajtbd/segment.served=prospective` и
  `business/business-problem.served=prospective` позволяют завести
  разведку рынка, которого бизнес ещё **не** обслуживает (классика:
  b2b-бизнес делает b2c). Проект с `vision.market-maturity=prospective`
  адресует их; на `stable` восходящий поток (§6) повышает их до `served`.
- Инварианты аудита допускают проспективные сущности без обслуживающих
  оферов/каналов (не флагать как «висяк»).

---

## 8. Реорганизация скиллов

### 8.1 Сплиты и переносы (из-за D5/D6)

| было | стало |
|---|---|
| `business-problem-deep-dive` (frame+SWOT+гипотезы) | `business-problem` kind → в `business-deep-dive`; SWOT → новый `swot-deep-dive`; Карта гипотез → новый `hypothesis-map-deep-dive` |
| `business-problem-audit` | `swot-audit` + `hypothesis-map-audit` |
| `business-problem-deep-dive-for-business` | **поглощается** `entrypoint-for-business` — SWOT и Карту гипотез в клиент-режиме ведёт оркестратор; отдельных `swot-*-for-business`/`hypothesis-map-*-for-business` скиллов не заводим (D-O4) |

`business-deep-dive` дорабатывается: новый kind `business-problem`
(реестр проблем) + провенанс-поля + участие в восходящем потоке.

### 8.2 Точечные правки существующих скиллов

- `project-deep-dive` / `project-audit` / `project-deep-dive-for-business`:
  `persona→user`, новые оси `vision`, `lifecycle`, `capability.hypotheses`,
  `user.segments`.
- `interface-deep-dive` / `interface-audit`: `situation.{jobs,capabilities,
  hypotheses}`, `who.users` (нарратив слоя не меняем).
- `segment-deep-dive` / `ajtbd-audit`: `segment.served/from-project`,
  правило проспективности.
- `cross-audit`: новые сквозные рёбра (§3.3), проспективные проверки,
  провенанс восходящего потока, переименования путей.
- `de-template`: guard и список не-трогаемых скелетов обновить под новую
  структуру каталогов (`swot/`, `hypothesis-map/`, `business-problem` в
  `business/`).
- `jtbd-interview`, `domain-deep-dive`, `screen-deep-dive`/`screen-audit`:
  правки путей/имён там, где ссылаются на `persona`/`frame`/
  `business-problem`-слой.

### 8.3 Новые скиллы

- `entrypoint` + `references/` + `state/`.
- `entrypoint-for-business` + `references/` + `state/` (ведёт SWOT/Карту
  гипотез в клиент-режиме сам).
- `swot-deep-dive`, `swot-audit`, `hypothesis-map-deep-dive`,
  `hypothesis-map-audit` (только аналитические; for-business-вариантов
  для них нет — D-O4).

### 8.4 Охват правок (замер)

`persona` — 42 файла / 263 вхождения; `frame` — 53 файла;
`business-problem` — 63 файла; 29 скиллов ссылаются на business-problem-
скиллы. → массовые правки идут **sweep-фазами**, 1 проход = 1
непересекающаяся зона (CLAUDE.md §6). Агентов не используем (по запросу) —
sweep'ы выполняются вручную, пакетно, под ревью.

---

## 9. Синтез `ajtbd-knowledge/` (D10)

- Дистиллировать ~5400 строк в **курированные** references:
  - принципы создания ценности, типы работ, Score, CPR, 11 механик →
    `segment-deep-dive/references/methodology.md` и
    `job-graph-deep-dive/references/methodology.md` (дополнить, не дублить).
  - глубинные интервью, B2B/B2C-специфика, скрипты →
    `jtbd-interview/references/` (`conduct.md`/`scripts.md`/`interpret.md`).
  - демо-графы (аренда квартиры и пр.) → **короткие** примеры в
    `job-graph-deep-dive/references/` (выжимка, не целиком).
- После переноса — **удалить** папку `ajtbd-knowledge/` (18 файлов) из
  git. Это не «археология» (методичка не была артефактом и нигде не была
  зашита), а консолидация знания в систему.

---

## 10. Документация и нарратив

Синхронизировать под новую структуру (forward-only, без «было/стало»):

- `CLAUDE.md` — карта слоёв, таблица «слой/вопрос/вход» (два энтрипоинта),
  зоны правок, терминология (`user`, `business-problem`, `swot`,
  `hypothesis-map`), восходящий поток, проспективность.
- `README.md` — воркфлоу **переписать из линейной лестницы в
  не-линейный** вокруг `entrypoint`/`entrypoint-for-business`; инварианты дополнить
  (сквозные рёбра, восходящий контур).
- `docs/README.md` — таблица слоёв, аудиты, handoff-контракт (пути
  `swot/`, `hypothesis-map/`, `business/business-problem`).
- `docs/getting-started.md` — путь форка через оркестраторы.
- README каждого затронутого слоя + `_canon/*/README.md` + файлы-каноны
  kind (критерии/что-НЕ/тест-критерий/форма ячеек/связи).

---

## 11. План реализации по фазам

Каждая фаза — отдельный reviewable-батч; внутри фазы правки атомарны.
Порядок дептенденси-аware: сначала data-model и каноны, потом скиллы,
потом оркестраторы и нарратив.

- **Фаза 0 — План.** Этот `roadmap.md` + утверждение открытых вопросов.
- **Фаза 1 — Каркас слоёв.**
  1. Создать `docs/swot/` и `docs/hypothesis-map/`, перенести kind-файлы
     из `business-problem/` (git mv), починить колонки `problem` →
     `business/business-problem`.
  2. `frame.md → business/business-problem.md` (git mv + переименовать
     H1/термины + добавить `served`, `from-project`).
  3. Удалить пустую `docs/business-problem/`.
  4. README новых слоёв (`swot`, `hypothesis-map`).
- **Фаза 2 — Переименование `persona → user`.** Канон `user.md`,
  `capability.user`, `surface.user`, sweep по 42 файлам (скиллы/доки),
  включая семантические ссылки `subject↔user`, `who↔user`.
- **Фаза 3 — Новые поля и сквозные рёбра.** §4.7 чек-лист: `vision`
  (3 оси + lifecycle), провенанс-поля, проспективность, A/B-рёбра в
  каноне-форме; обновить «Связи» в каждом README.
- **Фаза 4 — Реорг скиллов-исполнителей.** Сплит business-problem-deep-
  dive → `business-deep-dive`(+business-problem) / `swot-deep-dive` /
  `hypothesis-map-deep-dive`; сплит аудитов; правки project/interface/
  ajtbd/cross-audit/de-template (§8.2).
- **Фаза 5 — Оркестраторы.** `entrypoint` + `entrypoint-for-business`
  (SKILL + references + state), маршрутизация на исполнителей из Фазы 4;
  клиентский оркестратор ведёт SWOT/Карту гипотез сам.
- **Фаза 6 — Восходящий поток.** `lifecycle-upstream` в `entrypoint`,
  reconcile-up через business-скилл, проверки в `cross-audit` (§6).
- **Фаза 7 — Синтез знания.** Дистилляция `ajtbd-knowledge/` в references,
  удаление папки (§9).
- **Фаза 8 — Нарратив.** `CLAUDE.md`/`README.md`/`docs/README.md`/
  `getting-started` + README слоёв под не-линейный воркфлоу (§10).
- **Фаза 9 — Сквозная сверка.** Прогон `cross-audit` (мысленно/руками) на
  консистентность; финальная вычитка forward-only.

> Можно перегруппировать в более крупные коммиты, но **Фаза 1 → 2 → 3**
> должны идти строго до Фаз 4–5 (скиллы ссылаются на финальные пути/имена).

---

## 12. Риски и принципы

- **Forward-only в результатах**: ни один порождённый артефакт не несёт
  следов переименований/переноса. История — в `git log`. Сам `roadmap.md`
  удаляется в конце.
- **Большой охват ссылок** (persona/frame/business-problem): идём
  sweep-фазами, после каждой — grep на остаточные старые имена/пути.
- **Семантика, не slug-валидация**: новые рёбра не вводят жёстких
  валидаторов; рассинхрон ловит `cross-audit`.
- **Экспертиза священна** (CLAUDE.md §3): enum-значения осей `vision`,
  формулировки методологий SWOT/гипотез/AJTBD — из ответов владельца/
  аналитика и дистиллированной методички, не из головы агента.
- **Гейт человека**: коммит/push только по явной просьбе; необратимые
  удаления (`business-problem/`, `ajtbd-knowledge/`) — после показа
  каскада и подтверждения.
- **Изоляция продуктов** при сквозных рёбрах сохраняется: проектные поля
  ссылаются на глобальные, не на чужие проекты.

---

## 13. Резолюция открытых вопросов

Все развилки закрыты:

- **O1 → решено.** Оркестраторы: **`entrypoint`** (аналитик) и
  **`entrypoint-for-business`** (клиент).
- **O2 → решено.** Прямое ребро `capability.jobs` **вводим** (§3.3, A).
- **O3 → решено.** Берём **полные наборы** enum осей `vision`: `audience =
  b2b|b2c|b2b2c|internal|gov`, `intent = new-service|improve-service|
  internal-problem|client-problem`, `market-maturity = prospective|served`.
- **O4 → решено.** SWOT и Карту гипотез в клиент-режиме ведёт **сам
  `entrypoint-for-business`**; отдельных `*-for-business`-скиллов для них
  нет.
- **O5 → решено.** Понятие **«КРИ» не вводим**; `interface` остаётся как
  есть, меняются только связи `situation`/`who`.
