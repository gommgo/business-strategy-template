---
name: business-deep-dive
description: Углублённая проработка верхнего слоя — профиля бизнеса заказчика и реестра его проблем в `docs/business/` (profile · offering · channel · competitor · current-metric · material · business-problem). Самая первая точка входа: складывает полную картину бизнеса заказчика и формализует, какие проблемы бизнеса решаем (реестр `business-problem` — граница между гарантией доставки по scope и best-effort таргетом метрик). Принимает материалы клиента (сайт, PDF, презентации, соцсети, интервью), запускает рой агентов для web-research рынка и конкурентов, ведёт аналитика через фазы intake → profile → market → structure → metrics → problems → cohesion, заполняет артефакты через структурированные вопросы (AskUserQuestion), фиксирует контекст в собственной памяти `state/`, не выдумывает факты о бизнесе. Сегментацию клиентов передаёт в `/segment-deep-dive` (слой `docs/ajtbd/`); SWOT-факторы и Карту гипотез под реестр проблем — в `/swot-deep-dive` и `/hypothesis-map-deep-dive`. Несёт провенанс восходящего потока (`from-project` у offering/current-metric/business-problem — что проявил дозревший продукт). Использовать всегда, когда речь о docs/business/, онбординге нового заказчика, разборе его материалов, исследовании рынка и конкурентов, фиксации текущих бизнес-метрик (baseline), заведении или границе проблемы бизнеса, или подготовке почвы для SWOT и Карты гипотез. Единственная точка входа в docs/business/ для аналитика.
---

# business-deep-dive

Профиль **бизнеса заказчика** и реестр его **проблем** — самый верхний
слой, до решения. Канон — `docs/business/README.md`. Источник истины —
**материалы клиента** и **рой web-research**, не проекция аналитика.

Слой **нестрогий по картине бизнесa** (profile · offering · channel ·
competitor · current-metric · material), но несёт **строгий реестр
проблем** `business-problem.md` — таблицу проблем бизнеса (одна строка =
одна проблема + граница «гарантируем доставку по scope / целимся в
метрики best-effort»). Бизнес — **один** (этот слой общий), он питает
слои **SWOT** (`docs/swot/`) и **Карты гипотез** (`docs/hypothesis-map/`)
и мир из **множества проектов** (`docs/projects/<slug>/`): факторы SWOT
каждой проблемы растут из профиля и конкурентов, baseline целевых метрик —
из `current-metric.md`, а каждая запись SWOT / Карты гипотез тегируется
проблемой(ами) реестра через колонку `problem` (M:N).

## Реестр проблем `business-problem` (строгий kind)

`business-problem.md` — **таблица проблем бизнеса**: какую бизнес-боль (в
деньгах/времени/риске) решаем и — критично — **границу** между тем, что
гарантируем (доставка проекта по scope), и тем, на что целимся (метрики,
best-effort, **не гарантия**). Колонки: `slug · name · problem ·
guarantee · target · out-of-control · scope · served · from-project ·
status`. `served` — `served` (бизнес уже обслуживает рынок проблемы) либо
`prospective` (разведка под будущую инициативу). `from-project` —
провенанс восходящего потока (какой дозревший продукт проявил/подтвердил
проблему; иначе `—`). На строки реестра ссылаются `swot.*.problem`,
`hypothesis-map.*.problem` и `projects/<slug>/vision.addresses-problem`
(M:N). **Метрику никогда не подавать как гарантию** — это нарушение
юр-рамки.

Сегменты клиента по работам живут в соседнем слое `docs/ajtbd/`
(скилл `/segment-deep-dive`). Этот скилл их **не заводит** — только
read-only читает `docs/ajtbd/segment.md`, чтобы привязать
`offering.for-segment` и `channel.serves-segment` к существующим
сегментам. Сегментов ещё нет — предложить запустить `/segment-deep-dive`.

## Точки входа

| вызов | поведение |
|---|---|
| `/business-deep-dive` | сводка по фазам + предложение следующего шага |
| `/business-deep-dive <kind>` | завести новую сущность (режим A) |
| `/business-deep-dive <kind>:<slug>` | углубить запись (режим C) |
| `/business-deep-dive <свободный текст / ссылка / путь к материалу>` | сырьё → разбор (режим B / intake) |
| `/business-deep-dive --research <тема>` | запустить рой web-research |
| `/business-deep-dive --phase <name>` | работать в указанной фазе |

`kind` ∈ {`profile`, `offering`, `channel`, `competitor`,
`current-metric`, `material`, `business-problem`}.

`phase` ∈ {`intake`, `profile`, `market`, `structure`, `metrics`,
`problems`, `cohesion`}.

## Что делать сразу при запуске

1. Прочитать `docs/business/README.md` — освежить канон.
2. Прочитать `references/phases.md` — карту фаз.
3. Если args = ссылка/путь/материал клиента — режим intake (см.
   `references/intake.md`).
4. Если args пустые — сводка по фазам + `AskUserQuestion`.
5. Если `--research` — `references/research-rays.md`.

## Сводка состояния (без args)

1. Прочитать `profile.md` + 6 табличных файлов + `business-problem.md` +
   `state/`.
2. Определить **текущую фазу**:
   - `material`-таблица пустая → `intake`;
   - `profile` нет/draft → `profile`;
   - `competitor` пустая → `market`;
   - `offering`/`channel` пустые → `structure`;
   - `current-metric` пустая → `metrics`;
   - `business-problem` пустая → `problems`;
   - всё заполнено, есть draft → `cohesion`.
3. Вывести карту фаз. Через `AskUserQuestion` предложить следующий шаг.

## Фазы

| фаза | цель | артефакты |
|---|---|---|
| `intake` | принять материалы клиента, завести реестр источников | `material.md` |
| `profile` | чем бизнес занимается, как зарабатывает | `profile.md` |
| `market` | конкуренты и рынок (рой web-research) | `competitor.md` |
| `structure` | оферы и каналы (сегменты — в `docs/ajtbd/`, `/segment-deep-dive`) | `offering.md`, `channel.md` |
| `metrics` | текущие KPI — baseline-кандидаты | `current-metric.md` |
| `problems` | реестр проблем бизнеса + граница гарантии/таргета | `business-problem.md` |
| `cohesion` | целостность картины, передача в SWOT (`/swot-deep-dive`) и Карту гипотез (`/hypothesis-map-deep-dive`) | все |

Полная карта — `references/phases.md`. Порядок — рекомендация.

## Три режима

См. `references/workflow-patterns.md`:

- **A. Новая сущность.** Args = `<kind>`. Батч `AskUserQuestion` по
  критериям kind.
- **B / intake. Сырьё.** Args = материал клиента (текст/ссылка/файл).
  Завести `material`-запись (провенанс), извлечь кандидатов по слоям,
  по подтверждению — stub'ы. См. `references/intake.md`.
- **C. Углубление.** Args = `<kind>:<slug>`. Точечные вопросы по дырам.

## Стиль вопросов

- **Всегда `AskUserQuestion`**, до 4 вопросов в раунде.
- **Опции** — для enum (`offering.kind`, `channel.kind`,
  `competitor.position`, `material.kind`, `business-problem.served`),
  выбора существующего slug соседа (в т.ч. `from-project` — какой проект
  проявил запись), теста-критерия, promotion кандидата из research.
- **Other (значения)** — `name`, `description`, `value`, `position`,
  числа метрик, текст проблемы/границы (`problem`/`guarantee`/`target`/
  `out-of-control`/`scope`). Факты о бизнесе **не выдумывать** — брать из
  материалов клиента или подтверждённого research. **Метрику в `target`
  никогда не формулировать как гарантию** — только best-effort таргет
  (детали измеримости — слой `docs/hypothesis-map/`).

## Web-research через рой агентов

См. `references/research-rays.md`. Основной для `competitor`, полезен для
`profile`-контекста и `current-metric` (отраслевые бенчмарки). Запуск —
только по решению аналитика через `AskUserQuestion` (дефолт 5 агентов).
Кандидаты падают в `state/research/<тема>-<ts>.md`; **авто-вписывание в
артефакты запрещено** — promotion через `AskUserQuestion`.

## Память `state/`

`.claude/skills/business-deep-dive/state/<kind>/<slug>.md` (+
`state/profile.md` singleton, `state/business-problem/<slug>.md`,
`state/research/`). Формат — см. `references/state-format.md`. Три секции,
forward-only, пустые удаляются. Единый контекст: read-only видимость
соседних `state/` — клиентский режим
(`../business-deep-dive-for-business/state/`) и нижележащие слои
(`../swot-deep-dive/state/`, `../hypothesis-map-deep-dive/state/`,
`../project-deep-dive*/state/<slug>/` — проектный по текущему продукту).
В чужой state не писать.

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
`problem` ссылаются записи `docs/swot/` и `docs/hypothesis-map/`, а через
`addresses-problem` — `vision` проектов. Семантические висяки после
удаления ловит `/cross-audit`; предупредить аналитика и предложить
пройтись по зависимым слоям.

## Завершение сессии

1. Перечислить затронутые сущности.
2. Назвать текущую фазу и следующий шаг.
3. Через `AskUserQuestion` предложить: продолжить фазу /
   `/segment-deep-dive` (профиль готов → поиск сегментов клиента по
   работам в `docs/ajtbd/`) / `/swot-deep-dive` (реестр проблем готов →
   SWOT-факторы и ставки под проблемы) / `/hypothesis-map-deep-dive`
   (цели, метрики, субъекты, гипотезы под проблемы) / `/cross-audit`
   (стык с ajtbd / swot / hypothesis-map / проектами).

## Запреты

- Не редактировать `profile.md` и таблицы вслепую — сначала `Read`.
- Не выдумывать факты о бизнесе. Только из материалов / подтверждённого
  research.
- Не авто-вписывать research в артефакты — promotion через
  `AskUserQuestion`.
- Не повышать `draft → stable` без подтверждения; не понижать сам.
- Не заводить сегменты здесь — сегменты по работам живут в `docs/ajtbd/`
  (`/segment-deep-dive`); скилл только read-only на них ссылается.
- Не аккумулировать историю в `state/` — forward-only.
- Не пушить и не коммитить. Не вызывать другие скилы.
