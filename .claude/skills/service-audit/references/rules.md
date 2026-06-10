# Реестр правил service-audit

Каждое правило: id, severity, описание, как обнаружить, что рекомендовать.

## Состав слоя

Сервисный слой проекта `docs/projects/<project-slug>/services/`:

- **реестр-хребет** `service.md` — сервисы; их slug'и — имена папок
  `services/<svc>/`;
- **реестр** `platform.md` — платформенные ресурсы проекта;
- **1 singleton** `architecture.md` — свод топологии + Decisions;
- **паспорта** `services/<svc>/README.md` (H2: Purpose, Exposes, Owned
  Contexts, Dependencies, Resources, Messaging, Workers, Fronts, Notes);
- **папки доменов** `services/<svc>/domains/<ctx>/` — содержимое контекстов
  здесь не аудитится (только владение и существование событий);
- `_shared/` — территория `/domain-deep-dive`, в прогон не входит.

«Оба реестра» в правилах ниже = `service.md` + `platform.md`. Точечные
структурные опоры вне слоя: `surface.md` и `integration.md` того же
проекта, `docs/projects/infrastructure/shared-platform.md` — только на
резолв slug'ов.

## Структурные правила (R-STRUCT-*)

### R-STRUCT-001 — Дубль slug в реестре

**Severity:** `error`.

**Где:** оба реестра.

**Обнаружение:** в одном файле два разных ряда с одинаковым `slug`. Для
`service.md` дубль ломает структурную ось (slug = имя папки).

**Рекомендация:** «два ряда с slug X в файле Y — переименовать один или
объединить через `/service-deep-dive <project-slug>`».

### R-STRUCT-002 — Папка сервиса ↔ реестр

**Severity:** `error`.

**Где:** каталог `services/` + реестр `service.md`.

**Обнаружение:** листингом каталога (исключая `_shared/` и файлы
реестров/singleton'а):

- папка `services/<svc>/` существует, но строки `<svc>` в `service.md`
  нет — юнит вне хребта;
- строка `<svc>` в реестре есть, но папки с паспортом
  `services/<svc>/README.md` нет — объявлен и не открыт.

**Рекомендация:** «завести строку реестра / папку с паспортом или удалить
лишнее через `/service-deep-dive <project-slug>`».

### R-STRUCT-003 — Контекст без сервиса-владельца

**Severity:** `error`.

**Где:** дерево проекта `docs/projects/<project-slug>/`.

**Обнаружение:** папка bounded context живёт мимо сервиса:

- каталог `domains/` на **корне проекта** (`<P>/domains/<ctx>/`) — контексты
  обязаны жить в `services/<svc>/domains/<ctx>/`;
- папка `domains/<ctx>/` внутри `services/`, но вне какой-либо папки
  сервиса из реестра;
- контекст есть папкой в сервисе, но не перечислен в `Owned Contexts`
  его паспорта (и наоборот: строка `Owned Contexts` без папки).

**Рекомендация:** «контекст `<ctx>` не имеет сервиса-владельца / расходится
с паспортом. Раздать владельца через `/service-deep-dive <project-slug>`
(фаза partition)».

### R-STRUCT-004 — Контекст в двух сервисах

**Severity:** `error`.

**Где:** все папки `services/*/domains/*/`.

**Обнаружение:** один и тот же slug контекста встречается в `domains/`
двух разных сервисов (слаги контекстов уникальны в пределах проекта —
иначе рефы `use-case:<ctx>.<Operation>` / `event:<ctx>.<Event>` перестают
быть сервисо-агностичными).

**Рекомендация:** «контекст `<ctx>` размазан по `<svc1>` и `<svc2>` —
anti-pattern канона. Оставить одного владельца (перенос — режим миграции
`/service-deep-dive <project-slug>`); нужен «кусок» соседу — это
`Exposes`-функция или событие, не вторая папка».

### R-STRUCT-005 — Dependencies на несуществующий юнит

**Severity:** `error`.

**Где:** паспорта, таблица `Dependencies`.

**Обнаружение:** `ref` не резолвится:

- `` `service:<slug>` `` — нет строки в `service.md`;
- `` `platform:<slug>` `` — нет строки в `platform.md`;
- `` `integration:<slug>` `` — нет провайдера в `<P>/integration.md`;
- ref на сам себя (`service:<этот-svc>`) — тоже находка.

**Рекомендация:** «зависимость X паспорта `<svc>` ведёт в пустоту. Завести
юнит или поправить ref через `/service-deep-dive <project-slug> <svc>`;
провайдера интеграции — `/project-deep-dive`».

### R-STRUCT-006 — Exposes.audience вне реестров

**Severity:** `error`.

**Где:** паспорта, таблица `Exposes` + `surface.md` / `service.md` /
`integration.md`.

**Обнаружение:** элемент `audience` не резолвится: `surface:<slug>` — нет
в `surface.md`; `service:<slug>` — нет в `service.md`;
`integration:<slug>` — нет в `integration.md`. Сюда же — массив `surfaces`
строки реестра `service.md` со slug'ом вне `surface.md`.

**Рекомендация:** «функция `<fn-slug>` адресована `<audience>`, которого
нет. Поправить через `/service-deep-dive <project-slug> <svc>`; новую
поверхность — `/project-deep-dive`».

### R-STRUCT-007 — consumes без парного produces

**Severity:** `error`.

**Где:** таблицы `Messaging` всех паспортов.

**Обнаружение:** строка `consumes` с парой (`broker`, `topic`) и `event`,
для которой ни один паспорт не несёт `produces` с теми же `broker` +
`topic` + `event`. Сюда же — `produces` у сервиса, **не владеющего**
контекстом события (папка `domains/<ctx>/` лежит в другом сервисе).

**Рекомендация:** «consumes `<topic>`/`<event>` у `<svc>` без продюсера —
событие ниоткуда. Завести produces у владельца контекста или убрать
consumes через `/service-deep-dive <project-slug>`».

### R-STRUCT-008 — produces-событие без файла в domains

**Severity:** `error`.

**Где:** таблицы `Messaging` (строки `produces`) + папки
`services/<svc>/domains/<ctx>/events/`.

**Обнаружение:** `event:<ctx>.<Event>` в строке `produces`, но файла
`domains/<ctx>/events/<Event>.md` в этом сервисе нет — payload-контракт
не существует.

**Рекомендация:** «produces ссылается на событие `<ctx>.<Event>`, которого
нет в доменах сервиса. Завести событие через
`/domain-deep-dive <project-slug> <ctx>` или поправить Messaging».

### R-STRUCT-009 — Ресурс с одним именем у двух сервисов

**Severity:** `error`.

**Где:** таблицы `Resources` всех паспортов.

**Обнаружение:** одинаковое имя `resource` в `Resources` двух разных
паспортов — подозрение на shared database (ресурс принадлежит ровно одному
сервису; данные соседа — через `Exposes` или события).

**Рекомендация:** «ресурс `<resource>` числится у `<svc1>` и `<svc2>` —
shared database (anti-pattern). Оставить одного владельца, соседу — порт
или событие; общее хранилище — запись `platform.md`. Через
`/service-deep-dive <project-slug>`».

### R-STRUCT-010 — `domains/` у gateway / edge / bot

**Severity:** `error`.

**Где:** реестр `service.md` (колонка `type`) + папки сервисов.

**Обнаружение:** у сервиса с `type` ∈ {`gateway`, `edge`, `bot`} существует
непустая папка `domains/` (или `Owned Contexts` ≠ `_N/A (no domains)_`).
Бизнес-правила живут в доменах `api`/`worker`-сервисов.

**Рекомендация:** «у `<svc>` (type `<type>`) есть домены — бизнес-логика в
фасаде. Перенести контекст в `api`/`worker`-сервис (миграция через
`/service-deep-dive <project-slug>`) или пересмотреть type».

### R-STRUCT-011 — Узел architecture.md вне реестров

**Severity:** `error`.

**Где:** `architecture.md § Topology` (+ `§ Flows`).

**Обнаружение:** узел диаграммы не резолвится ни в `service.md`, ни в
`platform.md`, ни в `surface.md`, ни в `integration.md`. Сюда же — ребро
диаграммы, которого нет ни в одном паспорте (`Dependencies` для sync,
`Messaging` для async) и ни в одной колонке `surfaces`: диаграмма — свод,
рёбра в ней не авторятся. Обратная сторона (полнота свода) — `warning`:
сервис реестра / платформенный ресурс / интеграция проекта, **отсутствующие**
на диаграмме.

**Рекомендация:** «узел/ребро `<X>` в Topology не подтверждено
паспортами/реестрами. Канон — паспорта: дописать авторскую сторону или
пересвести диаграмму через `/service-deep-dive <project-slug> architecture`».

### R-STRUCT-012 — Невалидное enum-значение

**Severity:** `error`.

**Где:** оба реестра + паспорта.

**Enum-поля:**

| поле | допустимо |
|---|---|
| `service.type` | `api`, `worker`, `gateway`, `edge`, `bot` |
| `platform.type` | `message-broker`, `api-gateway`, `cdn`, `object-storage`, `idp`, `other` |
| `platform.provided-by` | `own`, `` `shared:<slug>` `` |
| `Messaging.direction` | `produces`, `consumes` |
| `Resources.type` | `database`, `cache`, `search-index`, `vector-store`, `object-storage`, `other` |
| `<любой>.status` | `draft`, `stable` |

**Обнаружение:** значение не из списка (с учётом бэктиков и em-dash для
опциональных).

**Рекомендация:** «значение X не из enum — выбрать одно из {…} через
`/service-deep-dive <project-slug>`».

### R-STRUCT-013 — `provided-by: shared:<slug>` в пустоту

**Severity:** `error`.

**Где:** `platform.md` + `docs/projects/infrastructure/shared-platform.md`.

**Обнаружение:** запись с `provided-by: shared:<slug>`, но строки `<slug>`
в `shared-platform.md` нет (или самого файла нет). Потребность в общем
ресурсе бизнеса заявлена, а общего ресурса не существует.

**Рекомендация:** «`platform:<slug>` ссылается на общий ресурс
`shared:<slug>`, которого нет в ИТ-периметре. Завести через
`/infrastructure-deep-dive` или перевести на `own`».

### R-STRUCT-014 — Обязательный слот/секция пуст при `status: stable`

**Severity:** `error`.

**Где:** оба реестра + паспорта + `architecture.md`.

**Обнаружение:** запись/паспорт `stable`, но обязательный слот пуст или
остался placeholder формы (`<slug>`, `<одно предложение>`, шаблонная
mermaid-диаграмма). Обязательные слоты и легальные явные пустоты
(`_N/A_` / `_нет_` по типу сервиса) — по
`../service-deep-dive/references/field-checklists.md`. Паспорт `stable`
при отсутствующем H2 — тоже сюда.

**Рекомендация:** «заполнить слот X или понизить запись в draft через
`/service-deep-dive <project-slug> <svc>`».

## Семантические правила (R-SEM-*)

### R-STRUCT-015 — Worker с topic-триггером без consumes

- **severity**: `error`
- **что ищем**: строка `## Workers` паспорта с `trigger: topic:<t>`, для
  которой в `## Messaging` того же паспорта нет строки `consumes` с тем же
  `topic` — воркер слушает топик, на который сервис не подписан.
- **как проверяем**: для каждого паспорта собрать пары
  (`Workers.trigger=topic:<t>` ↔ `Messaging.direction=consumes, topic=<t>`);
  непарный trigger — finding.
- **пример**: `notifier` с `trigger: topic:orders.paid`, а в Messaging
  только `produces`.

### R-STRUCT-016 — Workers.backed-by в пустоту

- **severity**: `error`
- **что ищем**: `backed-by: use-case:<ctx>.<Operation>` строки `## Workers`,
  для которого нет файла `services/*/domains/<ctx>/use-cases/<Operation>.md`.
- **как проверяем**: реф → скан доменов всех сервисов проекта. Дополнительно
  (`warning`, не отдельное правило): use-case найден в **чужом** сервисе —
  воркер исполняет чужой домен, обмен должен идти через события/Exposes.

### R-SEM-006 — Cron-выражение в Workers.trigger

- **severity**: `warning`
- **что ищем**: `trigger` строки `## Workers` с cron-синтаксисом
  (`*/5 * * * *` и подобное) вместо смысла словами («каждые 5 минут») —
  runtime-механика в design-time артефакте.
- **как проверяем**: regex на cron-подобные значения в колонке `trigger`.

### R-SEM-001 — Платформенный ресурс-сирота

**Severity:** `warning`.

**Где:** `platform.md` + таблицы `Dependencies` и `Messaging` всех
паспортов.

**Обнаружение:** запись `platform.md`, на которую не ссылается ни один
паспорт (ни `` `platform:<slug>` `` в `Dependencies`, ни `broker` в
`Messaging`). Реестр платформы — каталог потребностей; ресурс без
потребителя — сирота.

**Рекомендация:** «ресурс `<slug>` не требует ни один сервис. Подключить
потребителя или удалить запись через
`/service-deep-dive <project-slug> platform`».

### R-SEM-002 — Messaging.broker не брокер

**Severity:** `warning`.

**Где:** таблицы `Messaging` + `platform.md`.

**Обнаружение:** `broker` ссылается на запись `platform.md`, у которой
`type` ≠ `message-broker` (несуществующий slug — это R-STRUCT-005-класс,
`error` по строке Messaging).

**Рекомендация:** «`<svc>` ходит в `<slug>` как в брокер, но его type —
`<type>`. Поправить тип ресурса или ссылку через
`/service-deep-dive <project-slug>`».

### R-SEM-003 — Runtime-механика в артефактах

**Severity:** `warning`.

**Где:** все файлы слоя.

**Обнаружение:** маркеры операционки в прозе/таблицах: порты
(`:5432`, `port`), реплики (`replicas`, `2 экземпляра`), версии технологий
(`postgres 16`, `v1.2`), `image`/docker-образы, `env`/переменные окружения,
CPU/RAM/Gb, retention, helm-values, hostname/IP. Слой deployment-agnostic:
«нужен postgres под заказы», а не «postgres 16, 2 vCPU».

**Рекомендация:** «в `<X>` runtime-механика (`<маркер>`). Оставить
«потребность + технологию»; операционка — `<org>/infra`, размещение —
`infrastructure/placement.md`».

### R-SEM-004 — Stable со state-blocker

**Severity:** `warning`.

**Где:** все файлы слоя + ветка state
`../entrypoint/state/projects/<project-slug>/services/<kind>/<slug>.md`
(`<kind>` ∈ {`service`, `platform`, `architecture`}).

**Обнаружение:** запись/паспорт `stable`, а в state-заметке — строка с
маркером `**blocker**` или `**жду аналитика**`.

**Рекомендация:** «stable несовместим с открытым blocker'ом. Закрыть
вопрос или понизить в draft через `/service-deep-dive <project-slug>`».

### R-SEM-005 — Fronts не по типу

**Severity:** `warning`.

**Где:** паспорта (`Fronts`) + реестр (`type`).

**Обнаружение:**

- сервис `type` ≠ `gateway`, но `Fronts` заполнен (не `_N/A_`) — фасад к
  внешней системе у не-gateway;
- сервис `type: gateway`, но `Fronts` пуст / `_N/A_` — gateway без
  интеграции, которую фронтит (зачем он?).

**Рекомендация:** «согласовать `type` и `Fronts` через
`/service-deep-dive <project-slug> <svc>`: либо это gateway с явной
интеграцией, либо `Fronts: _N/A_`».

## Coverage-правила (R-COV-*)

### R-COV-001 — Пустой сервис

**Severity:** `hint`.

**Где:** реестр + паспорта.

**Обнаружение:** сервис без единого контекста (`Owned Contexts` =
`_N/A_` / пусто) **и** без функций (`Exposes` = `_N/A_` / пусто) **и**
без `Messaging` — юнит ничего не несёт. Для свежезаведённого draft —
норма жизни, но напомнить.

**Рекомендация:** «сервис `<svc>` пуст: ни контекстов, ни Exposes, ни
Messaging. Наполнить через `/service-deep-dive <project-slug> <svc>` /
`/domain-deep-dive`, или удалить, если он не нужен».

### R-COV-002 — Поверхность без обслуживающего сервиса

**Severity:** `hint`.

**Где:** `<P>/surface.md` + реестр `service.md`.

**Обнаружение:** slug поверхности из `surface.md` не встречается ни в
одной колонке `surfaces` реестра — кто её обслуживает? (Поверхность может
жить и без бэкенда — статический лендинг; поэтому hint, не error.)

**Рекомендация:** «поверхность `<surface>` не числится ни у одного
сервиса. Если у неё есть бэкенд — указать в `surfaces` через
`/service-deep-dive <project-slug>`».

### R-COV-003 — Событие домена без публики

**Severity:** `hint`.

**Где:** файлы `services/*/domains/<ctx>/events/*.md` + таблицы
`Messaging`.

**Обнаружение:** файл события существует, но `event:<ctx>.<Event>` не
встречается ни в одной строке `Messaging` (ни produces, ни consumes).
Подозрение, не нарушение: событие может жить внутрисервисно
(in-process подписчики того же сервиса) — но если оно задумывалось
межсервисным, привязка к topic'у потеряна.

**Рекомендация:** «событие `<ctx>.<Event>` никто не публикует в брокер и
не потребляет. Если оно межсервисное — добавить Messaging-строки через
`/service-deep-dive <project-slug>`; внутрисервисное — ок, пометить
осознанность можно в `Notes`».

## Что не делает service-audit

- Не читает содержимое доменных артефактов (секции агрегатов,
  use-case'ов, политик) — только структуру владения и существование
  файлов событий. Домены — чек-листы `/domain-deep-dive`.
- Не сверяет services с `interface/` / `screens/` / `telegram-bot-flow/`
  и с размещением `infrastructure/placement.md` — это `/cross-audit`
  (углы `service-placement` · `platform-shared`) и
  `/infrastructure-audit`.
- Не проверяет цепочки интеграций (use-case ↔ клиент `_shared/` ↔
  `integration.md` ↔ `project-map.md`) — `/cross-audit`.
- Не выходит за пределы проекта — кроме структурного резолва
  `provided-by: shared:<slug>` в `infrastructure/shared-platform.md`
  (листингом, без аудита периметра).
- Не предлагает promotion `draft → stable` — это `/service-deep-dive`.
- Не вызывает `/service-deep-dive` сам — даёт текст, что запустить.
- Не понижает `stable → draft` — может только сказать в `error`-отчёте,
  что запись несовместима со stable.
