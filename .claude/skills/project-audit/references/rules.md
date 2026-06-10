# Реестр правил project-audit

Каждое правило: id, severity, описание, как обнаружить, что
рекомендовать.

## Состав слоя

Продуктовый слой проекта `docs/projects/<project-slug>/`:

- **1 singleton** `vision.md`;
- **реестр-хребет** `surface.md` (поверхности; их slug'и — ключи
  партиционирования);
- **папка возможностей** `capability/` — по файлу на поверхность
  (`capability/<surface>.md`, имя файла = slug поверхности из `surface.md`);
- **5 плоских кросс-поверхностных таблиц** `user.md`, `integration.md`,
  `boundary.md`, `constraint.md`, `market.md`.

«Все табличные файлы» в правилах ниже = `surface.md` + `user.md` +
`integration.md` + `boundary.md` + `constraint.md` + `market.md` + каждый
файл `capability/*.md`. `vision.md` — singleton, не таблица.

## Структурные правила (R-STRUCT-*)

### R-STRUCT-001 — Дубликаты slug в одном файле

**Severity:** `error`.

**Где:** все табличные файлы (включая каждый `capability/*.md`).

**Обнаружение:** в одном файле два разных ряда с одинаковым `slug`.
Для `capability` область уникальности — **один файл поверхности**
(`capability/<surface>.md`): один slug возможности может повторяться в
разных файлах-поверхностях (это разные воплощения одной ценности),
дубликатом считается только повтор **внутри одного файла**.

**Рекомендация:** «два ряда с slug X в файле Y — переименовать один
из них через `/project-deep-dive <project-slug> <kind>:<slug>` или
объединить вручную».

### R-STRUCT-002 — Обязательный слот пустой при `status: stable`

**Severity:** `error`.

**Где:** все файлы (singleton + табличные, включая каждый `capability/*.md`).

**Обнаружение:** запись `stable`, но один из обязательных слотов
(по `field-checklists.md` аналитического скилла) `—` или пустой.

**Универсально обязательное:** `slug`, `name`, `description`, `status`.

Дополнительно по kinds (для stable):

| kind | обязательно при stable |
|---|---|
| `vision` | секции Problem, Success, Non-goals (Non-goals может быть `_нет_`, но секция должна быть) + непустой `addresses-problem` (≥1 slug-реф) + оси `audience`/`intent`/`market-maturity`/`lifecycle` (валидные enum) |
| `surface` | `type`, `lives-at`, `user` (≥1 элемент) |
| `capability` | `value`, `user` (≥1 элемент) |
| `user` | `context`, `jobs`, `pains`, `success` |
| `integration` (провайдер) | `direction`, `owner`, `payload`, `surface` (≥1 элемент), `target` (валидный enum); `sibling-project` — обязателен **iff** `target: sibling-project` (тогда непустой slug), иначе обязан быть `—` |
| `integration` (функция, `## Функции`) | `integration` (slug провайдера), `name`, `description`, `direction` (валидный enum `out`/`in`) |
| `boundary` | `why` |
| `constraint` | `kind`, `source` |
| `market` | `url`, `sources` (≥1 элемент) |

`integration.sibling-project` без `target: sibling-project` (заполнен при
`target: external`) — тоже нарушение слота: при `external` поле обязано
быть `—`. Проверку структурную (поле есть/пусто) делает это правило;
существование самой поверхности/проекта по ссылке — R-SEM-010/R-SEM-011.

**Рекомендация:** «заполнить слот X или понизить запись в draft через
`/project-deep-dive <project-slug> <kind>:<slug>`».

### R-STRUCT-003 — Невалидное enum-значение

**Severity:** `error`.

**Где:** все файлы с enum-полями (singleton `vision.md` + табличные,
включая каждый `capability/*.md`).

**Enum-поля:**

| поле | допустимо |
|---|---|
| `vision.audience` | `b2b`, `b2c`, `b2b2c`, `internal`, `gov` |
| `vision.intent` | `new-service`, `improve-service`, `internal-problem`, `client-problem` |
| `vision.market-maturity` | `prospective`, `served` |
| `vision.lifecycle` | `draft`, `accepted`, `build`, `mvp`, `beta-testing`, `stable`, `updating` |
| `surface.type` | `web`, `mobile`, `api`, `admin`, `bot`, `desktop`, `embed`, `other` |
| `integration.direction` (провайдер) | `in`, `out`, `duplex` |
| `integration.owner` | `we`, `partner`, `both` |
| `integration.target` | `external`, `sibling-project` |
| `integration` функция `.direction` (`## Функции`) | `out`, `in` |
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

**Где:** все файлы (singleton + табличные, включая каждый `capability/*.md`).

**Обнаружение:** `status` не `draft` и не `stable`.

**Рекомендация:** «status должен быть `draft` или `stable`. Исправить
через `/project-deep-dive <project-slug> <kind>:<slug>`».

### R-STRUCT-006 — Stable со state-blocker

**Severity:** `error`.

**Где:** все файлы + ветка state проекта в едином дереве оркестратора.

**Обнаружение:** запись `stable`, но в state-заметке записи есть строка с
маркером `**blocker**` или `**жду аналитика**`. Заметка лежит в
`../entrypoint/state/projects/<project-slug>/project/<kind>/<slug>.md`; для
возможности поверхности путь несёт поверхность —
`../entrypoint/state/projects/<project-slug>/project/capability/<surface>/<slug>.md`.

**Рекомендация:** «status: stable несовместим с открытым blocker'ом в
state. Либо закрыть вопрос, либо понизить запись в draft».

### R-STRUCT-007 — Файл `capability/<surface>.md` для поверхности вне реестра

**Severity:** `error`.

**Где:** папка `capability/` + реестр `surface.md`.

**Обнаружение:** в каталоге `capability/` лежит файл `<surface>.md`, имя
которого (без `.md`) не совпадает ни с одним `slug` из `surface.md`. Связь
capability → surface **структурная**: имя файла обязано быть slug'ом
поверхности из хребта.

**Рекомендация:** «файл возможностей `capability/<surface>.md` висит без
поверхности в реестре. Завести поверхность в `surface.md` или
переименовать/удалить файл через `/project-deep-dive <project-slug>`».

### R-STRUCT-008 — Поверхность реестра без файла возможностей

**Severity:** `hint` (coverage).

**Где:** реестр `surface.md` + папка `capability/`.

**Обнаружение:** в `surface.md` есть поверхность `<surface>`, но файла
`capability/<surface>.md` нет. Хребет объявил поверхность, а слой
возможностей под неё не открыт.

**Рекомендация:** «поверхность `<surface>` из реестра не имеет файла
`capability/<surface>.md`. Если поверхность живая — завести возможности
через `/project-deep-dive <project-slug> capability:<surface>`; иначе
проверить, нужна ли поверхность».

## Семантические правила (R-SEM-*)

### R-SEM-001 — Capability без user

**Severity:** `warning` (если draft) / `error` (если stable, дублирует
R-STRUCT-002).

**Где:** каждый файл `capability/*.md`.

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

**Где:** все табличные файлы (включая каждый `capability/*.md`).

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
строкой `docs/business/business-problem.md` — это уже семантика, её ловит
`/cross-audit` (не валидируется здесь, чтобы не лезть за пределы проекта).

**Рекомендация:** «vision без `addresses-problem` — продукт не привязан
ни к одной бизнес-проблеме. Указать строки реестра `business-problem.md`,
которые продукт закрывает, через `/project-deep-dive <project-slug>
--phase discovery`».

### R-SEM-010 — `integration.surface` на несуществующую поверхность

**Severity:** `error`.

**Где:** `integration.md` + реестр `surface.md`.

**Обнаружение:** в массиве `integration.surface` есть slug, которого нет
ни в одной строке `surface.md`. Поверхность — структурная ось внутри
проекта, ссылка валидируется на целостность (в отличие от семантических
рёбер вверх по слоям).

**Рекомендация:** «`integration:<slug>` обслуживает поверхность `<surface>`,
которой нет в реестре `surface.md`. Завести поверхность или поправить
ссылку через `/project-deep-dive <project-slug> integration:<slug>`».

### R-SEM-011 — `integration.sibling-project` на несуществующий или текущий проект

**Severity:** `error` (проект не существует) / `warning` (ссылка на сам
текущий проект).

**Где:** `integration.md` + каталог `docs/projects/`.

**Обнаружение:** при `target: sibling-project` значение `sibling-project`:

- не совпадает ни с одной папкой `docs/projects/<slug>/` (исключая
  `_template`) → `error` — стык ведёт в пустоту;
- совпадает с **текущим** `<project-slug>` → `warning` — соседний проект
  не может быть самим собой (это внутренний обмен, не межпроектный стык).

**Рекомендация:** «`integration:<slug>` стыкуется с соседним проектом
`<sibling-project>`, которого нет / который равен текущему. Поправить slug
соседнего проекта или сменить `target` на `external` через
`/project-deep-dive <project-slug> integration:<slug>`. Сам стык сводится в
`docs/projects/project-map.md`».

### R-SEM-012 — функция `## Функции` на несуществующего провайдера

**Severity:** `error`.

**Где:** `integration.md` (таблицы `## Провайдеры` + `## Функции`).

**Обнаружение:** в строке `## Функции` колонка `integration` ссылается на
slug, которого нет ни в одной строке `## Провайдеры`. Функция без провайдера
— сирота (связь функция → провайдер структурная, в пределах файла).

**Рекомендация:** «функция `<fn-slug>` ссылается на провайдера
`<integration>`, которого нет в `## Провайдеры`. Завести провайдера или
поправить ссылку через `/project-deep-dive <project-slug> integration`».

> Соответствие функции её клиенту `services/_shared/integrations/<integration>/`
> и потреблению в use-case (`functions`) — **семантическое**, в пределах
> проекта его не валидируем: это зона `/cross-audit` (угол `integration-domain`).

## Coverage-правила (R-COV-*)

### R-COV-001 — User без жителей

**Severity:** `hint`.

**Где:** `user.md`, проверяется через сводку упоминаний во **всех** файлах
`capability/*.md` и в `surface.md`.

**Обнаружение:** user-slug не появляется ни в одном `capability.user`
(по всем файлам поверхностей) и ни в одном `surface.user`.

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
допустимо (см. `docs/projects/_template/project/README.md`), но напомним:
цепочка не зрелая, пока Y не stable».

### R-COV-004 — Запись с пустыми обязательными слотами и пустой
state-заметкой

**Severity:** `hint`.

**Где:** все табличные файлы (включая каждый `capability/*.md`) + ветка
state проекта в едином дереве оркестратора.

**Обнаружение:** запись `draft` с пустыми обязательными слотами, но в
state-заметке записи ни одной открытой пометки (или файла нет вовсе).
Заметка — `../entrypoint/state/projects/<project-slug>/project/<kind>/<slug>.md`;
для возможности поверхности —
`../entrypoint/state/projects/<project-slug>/project/capability/<surface>/<slug>.md`.

**Рекомендация:** «запись X — draft с дырами, но в state нет
открытых вопросов. Возможно, запись забыта. Углубить через
`/project-deep-dive <project-slug> <kind>:<slug>` или удалить, если она
не нужна».

### R-COV-005 — Очень короткое description

**Severity:** `hint`.

**Где:** все табличные файлы (включая каждый `capability/*.md`).

**Обнаружение:** `description` короче 10 символов (без бэктиков и
em-dash).

**Рекомендация:** «description у X слишком короткое — раскрыть смысл
записи в одном предложении».

## Что не делает project-audit

- Не сравнивает продукт с `<slug>/interface` / `<slug>/services` /
  `<slug>/screens` и не проверяет `addresses-problem` против реестра
  `business/business-problem` — это `/cross-audit`.
- Не выходит за пределы одной папки проекта `docs/projects/<project-slug>/`
  — кроме одного структурного исключения: проверки **существования** папки
  соседнего проекта по `integration.sibling-project` (R-SEM-011) только
  листингом `docs/projects/`, без чтения его артефактов. Согласованность
  трёх сторон стыка (integration ↔ project-map ↔ порт в доменах
  сервисов) — у `/cross-audit` (угол `integration-domain`).
- Не предлагает promotion `draft → stable` — это `/project-deep-dive`.
- Не вызывает `/project-deep-dive` сам — даёт текст, что запустить
  аналитику.
- Не понижает `stable → draft` — может только в `error`-отчёте
  сказать, что запись несовместима со stable.
