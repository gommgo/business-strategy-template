---
name: business-deep-dive
description: "Проработка верхнего слоя `docs/business/`: кто этот бизнес, какие его проблемы решаем и кто в нём принимает решения. Первый вход при онбординге заказчика; факты не выдумывает — берёт из его материалов и подтверждённого исследования рынка; реестр проблем держит границу «гарантируем доставку по scope / целимся в метрики». Звать, когда нужны разбор материалов клиента, профиль, конкуренты, baseline метрик, проблема бизнеса, стейкхолдеры или проблемы, которые проявил дозревший продукт; сегменты ведёт `/segment-deep-dive`."
---

# business-deep-dive

Профиль **бизнеса заказчика** и реестр его **проблем** — самый верхний
слой, до решения. Канон — `docs/business/README.md`. Источник истины —
**материалы клиента** и **рой web-research**, не проекция аналитика.

Слой **нестрогий по картине бизнесa** (profile · offering · channel ·
competitor · current-metric · material), но несёт **строгий реестр
проблем** `business-problem.md` — таблицу проблем бизнеса (одна строка =
одна проблема + граница «гарантируем доставку по scope / целимся в
метрики best-effort») — и **строгий реестр стейкхолдеров** (`stakeholder` ·
`stakeholder-map`) — конкретных людей, принимающих решения в бизнесе, и
карты их связей и вовлечения (фаза `stakeholders`). Бизнес — **один**
(этот слой общий), он питает
слои **SWOT** (`docs/swot/`) и **Карты гипотез** (`docs/hypothesis-map/`)
и мир из **множества проектов** (`docs/projects/<slug>/`): факторы SWOT
каждой проблемы растут из профиля и конкурентов, baseline целевых метрик —
из `current-metric.md`, а каждая запись SWOT / Карты гипотез тегируется
проблемой(ами) реестра через колонку `business-problem` (M:N).

## Реестр проблем `business-problem` (строгий kind)

`business-problem.md` — **таблица проблем бизнеса**: какую бизнес-боль (в
деньгах/времени/риске) решаем и — критично — **границу** между тем, что
гарантируем (доставка проекта по scope), и тем, на что целимся (метрики,
best-effort, **не гарантия**). Колонки: `slug · name · statement ·
guarantee · target · out-of-control · scope · served · from-project ·
status` (`statement` — текст-формулировка боли, не ссылка). `served` — `served` (бизнес уже обслуживает рынок проблемы) либо
`prospective` (разведка под будущую инициативу). `from-project` —
провенанс восходящего потока (какой дозревший продукт проявил/подтвердил
проблему; иначе `—`). На строки реестра ссылаются `swot.*.business-problem`,
`hypothesis-map.*.business-problem` и `projects/<slug>/vision.addresses-problem`
(M:N). Метрика в реестре — таргет, а не гарантия: подать её как обещание
результата значит нарушить юридическую рамку.

Сегменты клиента по работам живут в соседнем слое `docs/ajtbd/`
(скилл `/segment-deep-dive`). Этот скилл их **не заводит** — только
read-only читает `docs/ajtbd/segment.md`, чтобы привязать
`offering.for-segment` и `channel.serves-segment` к существующим
сегментам. Сегментов ещё нет — предложить запустить `/segment-deep-dive`.

## Точки входа

| вызов | поведение |
|---|---|
| `/business-deep-dive` | сводка по фазам + ходы на выбор |
| `/business-deep-dive <kind>` | завести новую сущность (режим A) |
| `/business-deep-dive <kind>:<slug>` | углубить запись (режим C) |
| `/business-deep-dive <свободный текст / ссылка / путь к материалу>` | сырьё → разбор (режим B / intake) |
| `/business-deep-dive --research <тема>` | запустить рой web-research |
| `/business-deep-dive --phase <name>` | работать в указанной фазе |

`kind` ∈ {`profile`, `offering`, `channel`, `competitor`,
`current-metric`, `material`, `business-problem`, `stakeholder`,
`stakeholder-map`}.

`phase` ∈ {`intake`, `profile`, `market`, `structure`, `metrics`,
`problems`, `stakeholders`, `cohesion`}.

## Что делать сразу при запуске

1. Прочитать `docs/business/README.md` — освежить канон.
2. Прочитать `references/phases.md` — карту фаз.
3. Если args = ссылка/путь/материал клиента — режим intake (см.
   `references/intake.md`).
4. Если args пустые — сводка по фазам + `AskUserQuestion`.
5. Если `--research` — `references/research-rays.md`.

Как говорить о ходе, словах и вариантах — `.claude/rules/guiding.md`;
условия работы, названные человеком, читаются до первого вопроса.

## Сводка состояния (без args)

1. Прочитать `profile.md` + табличные файлы картины (`offering` · `channel`
   · `competitor` · `current-metric` · `material`) + `business-problem.md` +
   стейкхолдеры (`stakeholder.md` · `stakeholder-map.md`) + свою ветку
   `../entrypoint/state/business/`.
2. Определить **текущую фазу**:
   - `material`-таблица пустая → `intake`;
   - `profile` нет/draft → `profile`;
   - `competitor` пустая → `market`;
   - `offering`/`channel` пустые → `structure`;
   - `current-metric` пустая → `metrics`;
   - `business-problem` пустая → `problems`;
   - `stakeholder`/`stakeholder-map` пустые → `stakeholders`;
   - всё заполнено, есть draft → `cohesion`.
3. Вывести карту фаз. Через `AskUserQuestion` предложить ходы дальше.

## Фазы

| фаза | цель | артефакты |
|---|---|---|
| `intake` | принять материалы клиента, завести реестр источников | `material.md` |
| `profile` | чем бизнес занимается, как зарабатывает | `profile.md` |
| `market` | конкуренты и рынок (рой web-research) | `competitor.md` |
| `structure` | оферы и каналы (сегменты — в `docs/ajtbd/`, `/segment-deep-dive`) | `offering.md`, `channel.md` |
| `metrics` | текущие KPI — baseline-кандидаты | `current-metric.md` |
| `problems` | реестр проблем бизнеса + граница гарантии/таргета | `business-problem.md` |
| `stakeholders` | конкретные лица-решатели + карты их связей и вовлечения | `stakeholder.md`, `stakeholder-map.md` |
| `cohesion` | целостность картины, передача в SWOT (`/swot-deep-dive`) и Карту гипотез (`/hypothesis-map-deep-dive`) | все |

Полная карта — `references/phases.md`. Порядок — рекомендация.

## Три режима

См. `references/workflow-patterns.md`; обязательные поля и порядок
заполнения по kind — `references/field-checklists.md` (открыть в раундах
по слотам):

- **A. Новая сущность.** Args = `<kind>`. Батч `AskUserQuestion` по
  критериям kind.
- **B / intake. Сырьё.** Args = материал клиента (текст/ссылка/файл).
  Завести `material`-запись (провенанс), извлечь кандидатов по слоям,
  по подтверждению — stub'ы. См. `references/intake.md`.
- **C. Углубление.** Args = `<kind>:<slug>`. Точечные вопросы по дырам.

## Приём восходящего потока (reconcile-up)

Этот слой — **принимающая сторона** восходящего потока `project →
business`: когда продукт дозревает (`vision.lifecycle → stable`),
оркестратор `entrypoint` ведёт сверку (`reconcile-up`) и **делегирует
сюда запись** того, что продукт проявил наверху. Сам слой сверку не ведёт
— он формализует пришедшие кандидаты своими режимами A/C через
`AskUserQuestion`.

Что приходит от оркестратора (чанк + предложенный `from-project = <slug>`):

- **офер** — новая/обновлённая `offering` с `from-project` (продукт стал
  услугой бизнеса);
- **профиль** — правка `profile.md`, если продукт сдвинул «как
  зарабатывает / кого обслуживает»;
- **метрика** — новый baseline в `current-metric` с `from-project`;
- **повышение `served`** — у строки `business-problem`: `prospective →
  served` с проставленным `from-project` (рынок проблемы стал
  обслуживаемым).

Приёмная часть:

- Проставлять `from-project = <slug>` на принятые offering/current-metric/
  business-problem (провенанс контура; иначе `—`).
- Повышение `business-problem.served` `prospective → served` — только
  когда рынок проблемы действительно стал обслуживаемым (не «на будущее»).
- **`segment.served` — не территория этого слоя**: повышение сегмента ведёт
  `/segment-deep-dive` (оркестратор делегирует туда отдельно).
- Кандидат вытекает из дозревшего продукта, но формулировку
  офера/проблемы/метрики добивает обычный чек-лист kind через
  `AskUserQuestion`, а не догадка скилла. Метрика и здесь остаётся
  best-effort таргетом, не гарантией.

## Стиль вопросов

- **Всегда `AskUserQuestion`**, до 4 вопросов в раунде.
- **Опции** — для enum (`offering.kind`, `channel.kind`,
  `competitor.position`, `material.kind`, `business-problem.served`),
  выбора существующего slug соседа (в т.ч. `from-project` — какой проект
  проявил запись), теста-критерия, promotion кандидата из research.
- **Other (значения)** — `name`, `description`, `value`, `position`,
  числа метрик, текст проблемы/границы (`statement`/`guarantee`/`target`/
  `out-of-control`/`scope`). Факты о бизнесе берутся из материалов клиента
  или подтверждённого research: слой — источник истины для всех нижних,
  и догадка скилла стала бы ложным фактом (`CLAUDE.md` §3).
- Метрика в `target` формулируется как best-effort таргет, а не гарантия:
  гарантируем только доставку по scope, и обещание результата нарушило бы
  юридическую рамку (детали измеримости — слой `docs/hypothesis-map/`).

## Web-research через рой агентов

См. `references/research-rays.md`. Основной для `competitor`, полезен для
`profile`-контекста и `current-metric` (отраслевые бенчмарки). Запуск —
по решению аналитика через `AskUserQuestion` (дефолт 5 агентов).
Кандидаты падают в `../entrypoint/state/business/research/<тема>-<ts>.md`,
а в артефакты попадают только через `AskUserQuestion`: веб-находка бывает
неточной, и без проверки аналитиком она стала бы фактом о бизнесе.

## Память (state)

Своя ветка единого дерева — `../entrypoint/state/business/`: per-kind
заметки `<kind>/<slug>.md` (+ `profile.md` singleton,
`business-problem/<slug>.md`, `research/<тема>-<ts>.md`). Формат и
жизненный цикл заметки (три секции, `**blocker**` блокирует stable,
forward-only, пустые удаляются) — единый канон
`../entrypoint/references/state-model.md`.

**Единый контекст (read-only):** для общей картины скилл подтягивает всё
дерево `../entrypoint/state/` (соседние слои business/ajtbd/swot/
hypothesis-map и проектные ветки) плюс клиентский дом
`../entrypoint-for-business/state/`. **Своя ветка `business/` — rw; чужие
ветки и клиентский дом — read-only**, туда не писать. При чтении
клиентского дома маркер `**жду аналитика**` — blocker-кандидат
(эквивалент `**blocker**`).

## Контракт `draft → stable`

См. `references/draft-stable.md`. Обязательные слоты заполнены · критерии
kind подтверждены · anti-patterns не нарушены · тест-критерий ✅ · факт
прослежен до `material` · нет `**blocker**`. Скилл **не повышает сам**.

## Удаление (каскад)

Найти упоминания slug (ссылки в profile, в material-провенансе), показать
каскад, через `AskUserQuestion` решить по каждому, применить пакетом,
удалить запись и state-заметку. Связи `offering.for-segment` /
`channel.serves-segment` указывают на сегменты соседнего слоя
`docs/ajtbd/` — их этот скилл не трогает. Удаление **строки
`business-problem`** затрагивает нижележащие слои: на неё через колонку
`business-problem` ссылаются записи `docs/swot/` и `docs/hypothesis-map/`, а через
`addresses-problem` — `vision` проектов. Семантические висяки после
удаления ловит `/cross-audit`; предупредить аналитика и предложить
пройтись по зависимым слоям.

## Завершение сессии

1. Перечислить затронутые сущности.
2. Назвать текущую фазу и ходы дальше — два-три, один рекомендован.
3. Через `AskUserQuestion` предложить: продолжить фазу /
   `/segment-deep-dive` (профиль готов → поиск сегментов клиента по
   работам в `docs/ajtbd/`) / `/swot-deep-dive` (реестр проблем готов →
   SWOT-факторы и ставки под проблемы) / `/hypothesis-map-deep-dive`
   (цели, метрики, субъекты, гипотезы под проблемы) / `/cross-audit`
   (стык с ajtbd / swot / hypothesis-map / проектами).

Как говорить о ходе, словах и вариантах — `.claude/rules/guiding.md`:
итог сессии, ходы дальше и строка «как продолжить» идут по нему.

## Границы

- Каждый факт слоя прослеживается до `material` или подтверждённого
  research; предположений скилла в артефактах нет.
- Сегменты по работам живут в `docs/ajtbd/` (`/segment-deep-dive`); здесь
  на них только ссылаются `offering.for-segment` и `channel.serves-segment`.
- Статус записи меняет аналитик: `draft → stable` — по его подтверждению,
  `stable → draft` скилл только подсвечивает.
- Пишет скилл в `docs/business/` и в свою ветку state; следующий скилл
  (`/segment-deep-dive`, `/swot-deep-dive` и др.) запускает аналитик.
