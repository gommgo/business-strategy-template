# Единый state системы (аналитический дом)

Весь state аналитической стороны живёт в **одном дереве** —
`entrypoint/state/`. Это **единственный** канон формата: и оркестратор, и
все скиллы-исполнители читают/пишут сюда, своего `state/` не держат.
Клиентская сторона симметрично живёт в `entrypoint-for-business/state/`
(свой канон — `../../entrypoint-for-business/references/state-format-business.md`).

Forward-only: закрытое **удаляется**, история живёт в `git log`. Дерево и
файлы создаются **по требованию** — каталога нет, пока нечего записать.

## Владение по секциям дерева

Корень один, но у каждой ветки свой владелец (rw); остальные читают её
**read-only** (правила — `cross-read.md`):

```
.claude/skills/entrypoint/state/
├── index.md                 ← оркестратор: срез «где мы» по слоям
├── threads/<slug>.md        ← оркестратор: открытая нить (маршрут разбора)
├── business/                ← business-deep-dive
│   ├── profile.md
│   └── <kind>/<slug>.md         (offering · channel · competitor · current-metric · material · business-problem · stakeholder · stakeholder-map)
├── ajtbd/                   ← segment-deep-dive + job-graph-deep-dive
│   ├── <kind>/<slug>.md         (segment · job · job-graph · solution · segment-problem)
│   ├── hypotheses.md            (гипотезы работ до подтверждения)
│   ├── research/                (выгрузки роя web-research)
│   └── _interview/              ← jtbd-interview (сырьё интервью)
│       ├── prep.md · channels.md
│       ├── transcripts/<YYYY-MM-DD>--<HH-MM>--<тема>.md
│       └── candidates/<тема>-<ts>.md
├── swot/<kind>/<slug>.md    ← swot-deep-dive            (factor · bet)
├── hypothesis-map/<kind>/<slug>.md  ← hypothesis-map-deep-dive  (goal · metric · subject · hypothesis · task)
├── infrastructure/          ← infrastructure-deep-dive (ИТ-периметр бизнеса: server · runtime · shared-platform · job · placement)
└── projects/<project-slug>/ ← проектные исполнители (изоляция по продукту)
    ├── project/             ← project-deep-dive    (vision.md, <kind>/<slug>.md для surface · user · integration · boundary · constraint · market)
    │   └── capability/<surface>/<slug>.md          возможности по поверхности
    ├── interface/<surface>/<kind>/<slug>.md   ← interface-deep-dive
    ├── services/<kind>/<slug>.md              ← service-deep-dive (kind: service · platform · architecture)
    ├── domains/<context>/...                  ← domain-deep-dive (по bounded-context; ключ — контекст, не сервис)
    ├── screens/<surface>/<kind>/<slug>.md     ← screen-deep-dive
    ├── fsd/<surface>/<kind>/<slug>.md         ← fsd-deep-dive (по SPA-поверхности)
    ├── telegram-bot-flow/<surface>/...        ← telegram-bot-flow-deep-dive (по bot-поверхности)
    └── mobile/<surface>/<kind>/<slug>.md      ← mobile-deep-dive (по мобильной поверхности; рамка приложения — `_frame.md`)
```

Поверхность (`surface`) — ось продукта. Реестр-хребет `surface.md`
объявляет поверхности, а их slug'и партиционируют ветки `state/`:
возможности (`project/capability/<surface>/`), интерфейс
(`interface/<surface>/`) и композиция — экраны (`screens/<surface>/`),
диалоги бота (`telegram-bot-flow/<surface>/`) либо карта мобильного
приложения (`mobile/<surface>/`) — разнесены по поверхности. `vision` и кросс-поверхностные kind (`surface`-реестр · `user`
· `integration` · `boundary` · `constraint` · `market`) лежат плоско в
`project/`. Домены (ветка `domains/<context>/`) surface-агностичны — делятся по
bounded-context. Межпроектные стыки (`projects/project-map.md`) — авторская
сторона у `integration` инициатора (`target: sibling-project`); отдельной
state-ветки `project-map` не держим — заметки идут в ветку `project/`
инициатора.

Оркестратор владеет **только** `index.md` + `threads/` — это срез и
маршрут. Детальную per-kind проработку держат **исполнители** в своих
ветках; оркестратор их не дублирует, а в `index.md` лишь ссылается на
ветку слоя.

---

## `index.md` — срез по слоям (оркестратор)

Singleton-карта «где мы». По каждому слою (и каждому проекту для проектных
слоёв) — текущая фаза, счётчики draft/stable и ссылка на ветку слоя.

```markdown
# Срез по слоям

## business
- фаза: `cohesion` · profile stable · реестр проблем: 5 (4 stable, 1 draft)
- детально: `business/`

## ajtbd
- сегменты: 3 stable · граф работ собран по 2 из 3
- детально: `ajtbd/`

## swot
- факторы по 4 проблемам · проблема `slow-launch` без ставок
- детально: `swot/`

## hypothesis-map
- метрики по 3 проблемам · цель `retain-paid` без метрики
- детально: `hypothesis-map/`

## projects/clinic
- фаза: `surface` · vision stable · lifecycle: `mvp`
- поверхности: `web`, `bot` (реестр surface.md)
- capability: `web` 3 stable · `bot` 1 draft
- interface[`web`]: who/situation заполнены, zone пусто
- interface[`bot`]: —
- screens: —
- межпроектные стыки: `loyalty-sync` → `web-store` (project-map)
- детально: `projects/clinic/`
```

Срез проекта несёт **поверхностное измерение**: счётчики возможностей,
интерфейса и экранов даются **по поверхности** (`capability`/`interface`/
`screens` партиционированы по slug'ам реестра `surface.md`). Межпроектные
стыки (что течёт в соседний продукт) — отдельной строкой со ссылкой на
`projects/project-map.md`.

`index.md` — **рабочий срез, не журнал**: устаревшая строка
перезаписывается под актуальное состояние, а не дополняется «было/стало».
Если по слою ничего не начато — строки нет (отсутствие = не трогали).

Источник истины по числам — сами `docs/` и ветки исполнителей; `index.md`
— кэш для быстрой сводки. При расхождении верить `docs/` и перезаписать
срез.

## `threads/<slug>.md` — открытая нить (оркестратор)

Нить — **незавершённый разбор сырья** или **сквозная задача через
несколько слоёв**. Несёт маршрут: какие чанки куда направлены и какие ещё
**ждут**. Forward-only: закрытый чанк **удаляется**, нить без открытых
чанков **удаляется**.

```markdown
---
kind: thread
slug: sozvon-2026-06-06
opened-from: транскрипт созвона с клиникой, 2026-06-06
---

## Маршрут (ждут разбора)
- чанк «платные не возвращаются» → business / business-problem — ждёт
- чанк «отток 8% за Q1» → hypothesis-map / metric (baseline ← current-metric) — ждёт
- чанк «напоминания в боте» → projects/? / capability[поверхность `bot`?] — ждёт уточнения проекта и поверхности

## Открытые нити (смежные слои не потерять)
- субъект влияния (на кого целим возврат) — после metric завести в hypothesis-map/subject

## Что дальше
- начать с business-problem (корень), затем метрика поверх current-metric
```

Frontmatter: `kind: thread`, `slug`, `opened-from`. Секции (любая
опциональна):

- **`## Маршрут (ждут разбора)`** — строки `чанк → слой/kind/исполнитель →
  ждёт`. Делегированный и закрытый чанк — **убрать**.
- **`## Открытые нити`** — смежные слои, которые нельзя потерять.
- **`## Что дальше`** — порядок разбора.

---

## Per-kind заметка исполнителя

Каждый исполнитель пишет в свою ветку дерева (см. раскладку выше) рабочее
состояние знания об одной сущности. **Не журнал** — forward-only.

```markdown
---
kind: bet
slug: online-booking-push
ref: docs/swot/bet.md#online-booking-push
---

## Открытые вопросы
- (**blocker**) До какой цели доводим — удержание или конверсия? От этого
  зависит promoted-to.

## Доменные решения
- Баланс факторов = сильный бренд (strength) × спрос на онлайн (trend),
  потому что именно эта пара объясняет «за счёт чего шаг».

## Что копать дальше
- После заведения goal в Карте гипотез — проставить promoted-to.
```

Frontmatter: `kind` (имя слоевого kind), `slug` (= slug в таблице
артефакта), `ref` (путь к строке артефакта).

### Секции (все опциональны)

- **`## Открытые вопросы`** — незакрытые смысловые вопросы, по строке.
  Префикс/суффикс `**blocker**` блокирует переход `draft → stable`.
  Закрытый вопрос **удаляется** (не зачёркивается). Пусто → удалить секцию.
- **`## Доменные решения`** — неочевидные смысловые решения, не лезущие в
  таблицу. Форма «⟨что выбрано⟩ — ⟨почему⟩». Без «было/стало», без дат.
  Растворилось в записи → удалить.
- **`## Что копать дальше`** — локальные следующие шаги по сущности.
  Выполнен → удалить строку.

### Жизненный цикл заметки

- **Создаётся** только когда есть что записать (≥1 непустая секция).
- **Перезаписывается** свободно.
- **Удаляется**: все секции пусты → файл; запись удалена каскадом → файл.
- **Не аккумулировать** журнал (история — в `git log`).

### Особый случай: `_phase-jump.md`

`<слой>/<phase>/_phase-jump.md` фиксирует решение перепрыгнуть фазу (напр.
`swot/bet/_phase-jump.md` — «начали со ставки, факторы до-насытим позже»)
как доменное решение. Не блокер.

---

## Что НЕ хранить в state

- Дубликаты содержимого `docs/` (slug/name/status — в артефактах).
- Историю сессий, даты, «было/стало», «решено такого-то».
- Доменные формулировки «на всякий случай» (экспертиза — в артефакте через
  `AskUserQuestion`, `CLAUDE.md` §3).
- В `index.md`/`threads/` — детальные открытые вопросы по сущности (это
  per-kind ветка исполнителя).

## Перекрёстная видимость

Кто какую ветку видит и куда писать нельзя — `cross-read.md`. Базовое
правило: **своя ветка — rw, чужая — read-only**. При чтении клиентского
дома (`../../entrypoint-for-business/state/`) маркер `**жду аналитика**`
трактуй как **blocker-кандидат** — семантический эквивалент `**blocker**`.
