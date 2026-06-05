# Реестр правил project-audit

Каждое правило: id, severity, описание, как обнаружить, что
рекомендовать.

## Структурные правила (R-STRUCT-*)

### R-STRUCT-001 — Дубликаты slug в одном файле

**Severity:** `error`.

**Где:** все 7 табличных файлов.

**Обнаружение:** в одном файле два разных ряда с одинаковым `slug`.

**Рекомендация:** «два ряда с slug X в файле Y — переименовать один
из них через `/project-deep-dive <project-slug> <kind>:<slug>` или
объединить вручную».

### R-STRUCT-002 — Обязательный слот пустой при `status: stable`

**Severity:** `error`.

**Где:** все 8 файлов.

**Обнаружение:** запись `stable`, но один из обязательных слотов
(по `field-checklists.md` аналитического скилла) `—` или пустой.

**Универсально обязательное:** `slug`, `name`, `description`, `status`.

Дополнительно по kinds (для stable):

| kind | обязательно при stable |
|---|---|
| `vision` | секции Problem, Success, Non-goals (Non-goals может быть `_нет_`, но секция должна быть) + непустой `addresses-problem` (≥1 slug-реф) |
| `user` | `context`, `jobs`, `pains`, `success` |
| `capability` | `value`, `user` (≥1 элемент) |
| `boundary` | `why` |
| `surface` | `type`, `lives-at`, `user` (≥1 элемент) |
| `integration` | `direction`, `owner`, `payload` |
| `constraint` | `kind`, `source` |
| `market` | `url`, `sources` (≥1 элемент) |

**Рекомендация:** «заполнить слот X или понизить запись в draft через
`/project-deep-dive <project-slug> <kind>:<slug>`».

### R-STRUCT-003 — Невалидное enum-значение

**Severity:** `error`.

**Где:** все 7 табличных файлов с enum-полями.

**Enum-поля:**

| поле | допустимо |
|---|---|
| `surface.type` | `web`, `mobile`, `api`, `admin`, `bot`, `desktop`, `embed`, `other` |
| `integration.direction` | `in`, `out`, `duplex` |
| `integration.owner` | `we`, `partner`, `both` |
| `constraint.kind` | `regulation`, `sla`, `contract`, `technical`, `other` |
| `<любой>.status` | `draft`, `stable` |

**Обнаружение:** значение не из списка (с учётом бэктиков и em-dash
для опциональных).

**Рекомендация:** «значение X не из enum — выбрать одно из {…}
через `/project-deep-dive <project-slug> <kind>:<slug>`».

### R-STRUCT-004 — Vision без обязательной секции

**Severity:** `error`.

**Где:** `vision.md`.

**Обнаружение:** отсутствует H2 раздел Problem, Success или Non-goals.

**Рекомендация:** «vision должен иметь все три раздела (Problem,
Success, Non-goals). Открыть через
`/project-deep-dive <project-slug> --phase discovery`».

### R-STRUCT-005 — Невалидный status

**Severity:** `error`.

**Где:** все 8 файлов.

**Обнаружение:** `status` не `draft` и не `stable`.

**Рекомендация:** «status должен быть `draft` или `stable`. Исправить
через `/project-deep-dive <project-slug> <kind>:<slug>`».

### R-STRUCT-006 — Stable со state-blocker

**Severity:** `error`.

**Где:** все 8 файлов + state обоих скиллов.

**Обнаружение:** запись `stable`, но в
`.claude/skills/project-deep-dive/state/<project-slug>/<kind>/<slug>.md`
или
`.claude/skills/project-deep-dive-for-business/state/<project-slug>/<kind>/<slug>.md`
есть строка с маркером `**blocker**` или `**жду аналитика**`.

**Рекомендация:** «status: stable несовместим с открытым blocker'ом в
state. Либо закрыть вопрос, либо понизить запись в draft».

## Семантические правила (R-SEM-*)

### R-SEM-001 — Capability без user

**Severity:** `warning` (если draft) / `error` (если stable, дублирует
R-STRUCT-002).

**Где:** `capability.md`.

**Обнаружение:** `user = —` или пустой массив.

**Рекомендация:** «capability без user — мёртвая. Связать или
удалить через `/project-deep-dive <project-slug> capability:<slug>`».

### R-SEM-002 — Surface без user

**Severity:** `warning` (если draft) / `error` (если stable, дублирует
R-STRUCT-002).

**Где:** `surface.md`.

**Обнаружение:** `user = —` или пустой массив.

**Рекомендация:** «surface без user — кому она нужна? Связать
или удалить».

### R-SEM-003 — Boundary с backlog-обоснованием

**Severity:** `warning`.

**Где:** `boundary.md`.

**Обнаружение:** в `why` встречается одно из:
- «нет времени», «не хватает ресурсов», «потом сделаем»,
  «когда-нибудь», «отложили», «в бэклоге», «v2», «ждём финансирования».

**Рекомендация:** «формулировка `why` похожа на backlog (anti-pattern
из boundary.md). Boundary — устойчивое "нет", не "потом".
Пересмотреть через `/project-deep-dive <project-slug> boundary:<slug>`».

### R-SEM-004 — Constraint без source

**Severity:** `warning` (если draft) / `error` (если stable, дублирует
R-STRUCT-002).

**Где:** `constraint.md`.

**Обнаружение:** `source = —` или пусто.

**Рекомендация:** «constraint без `source` — спекулятивен.
Назвать конкретный документ (закон + статья, контракт + пункт,
URL)».

### R-SEM-005 — Market без url или sources

**Severity:** `warning` (если draft) / `error` (если stable, дублирует
R-STRUCT-002).

**Где:** `market.md`.

**Обнаружение:** `url = —` или `sources = —` / пустой массив.

**Рекомендация:** «market-запись без url или sources — это слух.
Без подтверждённых источников запись не имеет ценности».

### R-SEM-006 — Integration с direction, но без owner

**Severity:** `warning`.

**Где:** `integration.md`.

**Обнаружение:** `direction` заполнен (`in` / `out` / `duplex`), а
`owner` = `—`.

**Рекомендация:** «direction указан, owner — нет. Уточнить, кто
инициирует обмен — мы, партнёр, или оба».

### R-SEM-007 — Description совпадает с name

**Severity:** `warning`.

**Где:** все 7 табличных файлов.

**Обнаружение:** `description` и `name` идентичны (по содержимому).

**Рекомендация:** «`description` дублирует `name`. Раскрыть смысл
записи в одном предложении».

### R-SEM-008 — Vision с маркетинговой копией

**Severity:** `warning`.

**Где:** `vision.md`.

**Обнаружение:** в Problem или Success встречается маркер
маркетинга: «революционн», «уникальн», «лучш в мире», «no.1»,
«next-gen», «цифровизаци», «инновационн».

**Рекомендация:** «vision звучит как маркетинговая копия. Vision
— внутренний документ аналитика, не сейлз-материал».

### R-SEM-009 — Vision без addresses-problem

**Severity:** `warning` (если draft) / `error` (если stable, дублирует
R-STRUCT-002).

**Где:** `vision.md`.

**Обнаружение:** строка `**addresses-problem:**` отсутствует, пустая
(`—`) или содержит пустой массив.

Проверка только структурная: что привязка **есть**. Совпадает ли slug со
строкой `docs/business-problem/frame.md` — это уже семантика, её ловит
`/cross-audit` (не валидируется здесь, чтобы не лезть за пределы проекта).

**Рекомендация:** «vision без `addresses-problem` — продукт не привязан
ни к одной бизнес-проблеме. Указать строки `frame.md`, которые продукт
закрывает, через `/project-deep-dive <project-slug> --phase discovery`».

## Coverage-правила (R-COV-*)

### R-COV-001 — User без жителей

**Severity:** `hint`.

**Где:** `user.md`, проверяется через сводку упоминаний в
`capability.md` и `surface.md`.

**Обнаружение:** user-slug не появляется ни в одном
`capability.user` и ни в одном `surface.user`.

**Рекомендация:** «user X не используется ни в capability, ни в
surface. Либо подключить, либо рассмотреть удаление».

### R-COV-002 — Vision stable при пустой user-таблице

**Severity:** `hint`.

**Где:** `vision.md` + `user.md`.

**Обнаружение:** `vision.md` имеет `**status:** \`stable\``, но в
`user.md` нет ни одной записи.

**Рекомендация:** «vision закрыт как stable, но ни одного user
не заведено. Обычно vision созревает после первой проработки
user. Возможно, рано закрыли — пересмотреть через
`/project-deep-dive <project-slug>`».

### R-COV-003 — Stable со ссылкой на draft

**Severity:** `hint`.

**Где:** все записи с массивами slug.

**Обнаружение:** stable-запись X ссылается на draft-запись Y.

**Рекомендация:** «stable X ссылается на draft Y. По канону это
допустимо (см. `docs/projects/_canon/project/README.md`), но напомним:
цепочка не зрелая, пока Y не stable».

### R-COV-004 — Запись с пустыми обязательными слотами и пустой
state-заметкой

**Severity:** `hint`.

**Где:** все 7 табличных файлов + state обоих скиллов.

**Обнаружение:** запись `draft` с пустыми обязательными слотами, но в
`state/<project-slug>/<kind>/<slug>.md` ни одной открытой пометки (или
файла нет вовсе).

**Рекомендация:** «запись X — draft с дырами, но в state нет
открытых вопросов. Возможно, запись забыта. Углубить через
`/project-deep-dive <project-slug> <kind>:<slug>` или удалить, если она
не нужна».

### R-COV-005 — Очень короткое description

**Severity:** `hint`.

**Где:** все 7 табличных файлов.

**Обнаружение:** `description` короче 10 символов (без бэктиков и
em-dash).

**Рекомендация:** «description у X слишком короткое — раскрыть смысл
записи в одном предложении».

## Что не делает project-audit

- Не сравнивает продукт с `<slug>/interface` / `<slug>/domains` /
  `<slug>/screens` и не проверяет `addresses-problem` против
  `business-problem/frame` — это `/cross-audit`.
- Не выходит за пределы одной папки проекта `docs/projects/<project-slug>/`.
- Не предлагает promotion `draft → stable` — это `/project-deep-dive`.
- Не вызывает `/project-deep-dive` сам — даёт текст, что запустить
  аналитику.
- Не понижает `stable → draft` — может только в `error`-отчёте
  сказать, что запись несовместима со stable.
