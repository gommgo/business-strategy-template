# Реестр правил infrastructure-audit

Каждое правило: id, severity, описание, как обнаружить, что
рекомендовать.

## Состав слоя

ИТ-периметр бизнеса `docs/projects/infrastructure/` — 5 реестров (канон
формы + данные в одних файлах):

- `server.md` — учёт серверов (железо/VPS);
- `runtime.md` — среды исполнения (`kubernetes` | `compose`, по
  окружениям);
- `shared-platform.md` — общие платформенные ресурсы бизнеса;
- `job.md` — реестр-хребет джоб периметра; полные описания — файлы
  `jobs/<slug>.md`;
- `placement.md` — размещение юнитов (`unit → runtime`).

Read-only контекст резолва (исключая `_template`):

- `docs/projects/<project>/services/service.md` — сервисы-юниты;
- `docs/projects/<project>/services/platform.md` — проектные ресурсы
  (`provided-by: own` — размещаемые юниты; `provided-by: shared:<slug>` —
  потребности общих ресурсов);
- `docs/projects/<project>/services/*/README.md` — **только** секции
  `## Resources` (stateful-ресурсы для R-COV-006) и `## Messaging`
  (продюсеры топиков для R-SEM-005); остальное содержимое паспортов —
  зона `/service-audit`.

Синтаксис `placement.unit`: `` `service:<project>/<svc>` `` |
`` `platform:<project>/<slug>` `` | `` `shared-platform:<slug>` `` |
`` `job:<slug>` ``.

## Структурные правила (R-STRUCT-*)

### R-STRUCT-001 — Дубли slug в реестрах

**Severity:** `error`.

**Где:** все 5 реестров слоя.

**Обнаружение:** в одном реестре два ряда с одинаковым `slug`
(`server.md`, `runtime.md`, `shared-platform.md`, `job.md`); в `placement.md` —
два ряда с одинаковой парой `unit` + `runtime` (один юнит в один рантайм
дважды).

**Рекомендация:** «два ряда с slug X в файле Y — переименовать/объединить
через `/infrastructure-deep-dive <kind>:<slug>`».

### R-STRUCT-002 — Невалидное enum-значение

**Severity:** `error`.

**Enum-поля слоя:**

| поле | допустимо |
|---|---|
| `runtime.type` | `kubernetes`, `compose` |
| `runtime.environment` | `prod`, `staging`, `dev` |
| `shared-platform.type` | `message-broker`, `api-gateway`, `cdn`, `object-storage`, `idp`, `registry`, `monitoring`, `secret-store`, `other` |
| `placement.unit` (префикс) | `service:`, `platform:`, `shared-platform:`, `job:` |
| `<любой>.status` | `draft`, `stable` |

**Обнаружение:** значение не из списка (с учётом бэктиков); `unit` без
валидного префикса.

**Рекомендация:** «значение X не из enum — выбрать одно из {…} через
`/infrastructure-deep-dive <kind>:<slug>`».

### R-STRUCT-003 — `runtime.servers` вне `server.md`

**Severity:** `error`.

**Где:** `runtime.md` + `server.md`.

**Обнаружение:** в массиве `runtime.servers` есть slug, которого нет ни
в одной строке `server.md` (включая пустой массив — рантайм без серверов
недоказан).

**Рекомендация:** «рантайм X стоит на сервере Y, которого нет в учёте.
Завести сервер или поправить ссылку через
`/infrastructure-deep-dive runtime:<slug>`».

### R-STRUCT-004 — `placement.runtime` вне `runtime.md`

**Severity:** `error`.

**Где:** `placement.md` + `runtime.md`.

**Обнаружение:** колонка `runtime` строки размещения не совпадает ни с
одним `slug` из `runtime.md`.

**Рекомендация:** «юнит X размещён в рантайм Y, которого нет. Завести
рантайм или поправить строку через
`/infrastructure-deep-dive placement`».

### R-STRUCT-005 — `placement.unit` на несуществующий сервис

**Severity:** `error`.

**Где:** `placement.md` + реестры `docs/projects/*/services/service.md`.

**Обнаружение:** `unit = service:<project>/<svc>`, и либо папки проекта
`docs/projects/<project>/` нет (или это `_template`), либо в его
`services/service.md` нет строки со slug `<svc>`.

**Рекомендация:** «размещение указывает на сервис `<project>/<svc>`,
которого нет в реестре проекта. Поправить unit через
`/infrastructure-deep-dive placement` или завести сервис через
`/service-deep-dive <project>`».

### R-STRUCT-006 — `placement.unit` на несуществующий или не-`own` проектный ресурс

**Severity:** `error`.

**Где:** `placement.md` + `docs/projects/*/services/platform.md`.

**Обнаружение:** `unit = platform:<project>/<slug>`, и выполняется одно
из:

- в `services/platform.md` проекта нет строки со slug `<slug>` (или нет
  самого файла/проекта) — реф в пустоту;
- строка есть, но `provided-by` ≠ `own` — ресурс с `shared:<slug>`
  размещается как `shared-platform:<slug>`, не от имени проекта (иначе
  один ресурс размещён дважды под разными именами).

**Рекомендация:** «размещение `platform:<project>/<slug>` не резолвится
в `own`-ресурс проекта. Поправить unit через
`/infrastructure-deep-dive placement` (для shared-ресурса — строка
`shared-platform:<slug>`) или поправить `provided-by` через
`/service-deep-dive <project>`».

### R-STRUCT-007 — `placement.unit` на несуществующий shared-ресурс

**Severity:** `error`.

**Где:** `placement.md` + `shared-platform.md`.

**Обнаружение:** `unit = shared-platform:<slug>`, а строки со slug
`<slug>` в `shared-platform.md` нет.

**Рекомендация:** «размещение указывает на общий ресурс `<slug>`,
которого нет в `shared-platform.md`. Завести ресурс или поправить unit
через `/infrastructure-deep-dive`».

### R-STRUCT-008 — Потребность `shared:<slug>` без записи в `shared-platform.md`

**Severity:** `error`.

**Где:** `docs/projects/*/services/platform.md` + `shared-platform.md`.

**Обнаружение:** в `platform.md` какого-либо проекта строка с
`provided-by: shared:<slug>`, а записи `<slug>` в `shared-platform.md`
нет. Проект объявил потребность — периметр не ответил.

**Рекомендация:** «проект `<project>` ждёт общий ресурс `<slug>`,
которого нет в периметре. Завести через
`/infrastructure-deep-dive shared-platform` (или переключить проект на
`own` через `/service-deep-dive <project>`)».

### R-STRUCT-009 — Stable со state-blocker

**Severity:** `error`.

**Где:** все реестры слоя + ветка
`../entrypoint/state/infrastructure/<kind>/<slug>.md`.

**Обнаружение:** запись `stable`, а в её state-заметке есть пометка
`**blocker**` или `**жду аналитика**` (для placement ключ заметки —
нормализованный `unit`, `:` и `/` → `--`).

**Рекомендация:** «stable несовместим с открытым blocker'ом. Закрыть
вопрос или понизить запись в draft через `/infrastructure-deep-dive`».

### R-STRUCT-010 — `placement.unit` `job:` или `job.target` в пустоту

**Severity:** `error`.

**Где:** `placement.md` + `job.md` + реестры периметра и проектов.

**Обнаружение:** (а) строка `placement.md` с `unit: job:<slug>`, которого
нет в `job.md`; (б) реф `job.target` (`server:` / `runtime:` /
`shared-platform:` / `service:<project>/<svc>`), который не резолвится в
соответствующий реестр. Проверка: собрать slug'и `job.md`; каждый
`job:`-unit placement и каждый реф колонки `target` сверить с реестрами
периметра и проектов. Пример: `pg-backup` с
`target: [service:crm/orders]`, а проекта `crm` нет.

**Рекомендация:** «реф X не резолвится. Завести джобу/сущность или
поправить строку через `/infrastructure-deep-dive`».

### R-STRUCT-011 — Джоба: рассинхрон реестра и файлов

**Severity:** `error`.

**Где:** `job.md` + файлы `jobs/<slug>.md`.

**Обнаружение:** строка реестра `job.md` без файла `jobs/<slug>.md`; файл
в `jobs/` без строки реестра; отсутствие обязательных секций файла
(`Trigger`, `Does`, `Target`, `Retention`, `Verify`, `On failure`,
`Notes`) или `kind: job` во frontmatter; рассинхрон `trigger`/`target`
между реестром и файлом. Проверка: slug'и реестра ↔ листинг `jobs/*.md`;
по каждому файлу — frontmatter, набор H2, сверка trigger/target с
реестром.

**Рекомендация:** «реестр `job.md` и файлы `jobs/` разошлись на X —
выровнять через `/infrastructure-deep-dive job:<slug>`».

## Семантические правила (R-SEM-*)

### R-SEM-001 — IP / hostname / ОС / секреты / runtime-механика в файлах слоя

**Severity:** `warning`.

**Где:** все 5 реестров слоя + файлы `jobs/*.md` (любые колонки и prose).

**Обнаружение:** в тексте встречается:

- IPv4/IPv6-адрес, hostname/FQDN (`prod1.example.com`), URL доступа;
- имя/версия ОС, реквизиты SSH, пароль, токен, ключ;
- runtime-механика: реплики, версия k8s/helm, CNI, ingress-контроллер,
  retention, affinity, размеры подов, имена манифестов.

Контракт слоя: смысл и ёмкость — здесь, адресация/доступы/механика — в
`<org>/infra`.

**Рекомендация:** «в записи X чувствительное/летучее значение Y — убрать
через `/infrastructure-deep-dive <kind>:<slug>`; место этой информации —
`<org>/infra`». Секрет (пароль/токен/ключ) — отметить **первой строкой
отчёта**: он уже в git-истории, ротация — забота владельца.

### R-SEM-002 — Shared-ресурс-сирота

**Severity:** `warning`.

**Где:** `shared-platform.md` + `docs/projects/*/services/platform.md`.

**Обнаружение:** запись `shared-platform.md`, на которую не ссылается
ни одна строка `provided-by: shared:<slug>` ни в одном проекте. Общий
ресурс без единого потребителя.

Если в state-заметке записи есть явное решение «заведён на вырост» с
названными будущими потребителями — понизить finding до `hint` с цитатой.

**Рекомендация:** «общий ресурс X не потребляет ни один проект. Либо
подключить потребителей (`provided-by: shared:X` — через
`/service-deep-dive <project>`), либо рассмотреть удаление через
`/infrastructure-deep-dive shared-platform:X`».

### R-SEM-003 — Два проекта с `own`-ресурсом одной технологии

**Severity:** `warning` (подозрение, не ошибка).

**Где:** `docs/projects/*/services/platform.md` (колонки `technology` +
`provided-by`).

**Обнаружение:** в ≥2 разных проектах строки с `provided-by: own` и
одинаковой `technology` (две независимые NATS, два traefik). Напрашивается
общий ресурс — но осознанная изоляция допустима.

Если state-заметки соответствующих записей несут решение «осознанная
изоляция, потому что …» — понизить до `hint` с цитатой решения.

**Рекомендация:** «проекты A и B поднимают свой `<technology>` каждый.
Если изоляция не осознанна — кандидат в `shared-platform.md` (завести
через `/infrastructure-deep-dive shared-platform`, переключить проекты
через `/service-deep-dive`); если осознанна — зафиксировать „почему“ в
state».

### R-SEM-004 — Stable-джоба с пустым Verify

**Severity:** `warning`.

**Где:** файлы `jobs/<slug>.md`.

**Обнаружение:** файл джобы со `status: stable`, у которого `Verify` —
`_N/A_`/`—`/пустой: никак не проверяется, что джоба реально работает
(бэкап без restore-теста — вера, не гарантия). Проверка: для stable-джоб
секция `Verify` непуста содержательно.

**Рекомендация:** «stable-джоба X не несёт проверки успеха. Заполнить
`Verify` или понизить запись в draft через
`/infrastructure-deep-dive job:<slug>`».

### R-SEM-005 — Topic-триггер джобы без продюсера

**Severity:** `warning`.

**Где:** `job.md` + файлы `jobs/*.md` + секции `## Messaging` паспортов
`docs/projects/*/services/*/README.md`.

**Обнаружение:** джоба с `trigger: topic:<topic>`, при этом ни один
паспорт сервиса не несёт строку `produces` с этим `topic` — джоба слушает
топик, в который никто не публикует, и не исполнится никогда. Проверка:
собрать топики topic-триггеров; каждый найти среди `produces` секций
`## Messaging` (читаются только эти секции паспортов).

**Рекомендация:** «джоба X триггерится топиком `<topic>`, продюсера
которого нет ни в одном `## Messaging`. Поправить триггер через
`/infrastructure-deep-dive job:<slug>` или завести produces у
сервиса-владельца через `/service-deep-dive <project>`».

## Coverage-правила (R-COV-*)

### R-COV-001 — Сервис проекта без prod-размещения

**Severity:** `hint`.

**Где:** реестры `docs/projects/*/services/service.md` + `placement.md` +
`runtime.md`.

**Обнаружение:** для строки `service.md` какого-либо проекта нет ни одной
строки `placement.md` с `unit = service:<project>/<svc>` и рантаймом
`environment: prod` (нет placement вовсе — тоже сюда).

**Рекомендация:** «сервис `<project>/<svc>` не размещён в prod — он
„живёт нигде“. Разместить через `/infrastructure-deep-dive placement`».

### R-COV-002 — Размещаемый ресурс без placement

**Severity:** `hint`.

**Где:** `docs/projects/*/services/platform.md` (строки `own`) +
`shared-platform.md` + `placement.md`.

**Обнаружение:**

- проектный ресурс `provided-by: own` без строки
  `placement.md` `unit = platform:<project>/<slug>`;
- запись `shared-platform.md`, которую потребляет ≥1 проект, без строки
  `unit = shared-platform:<slug>`.

**Рекомендация:** «ресурс X используется, но не размещён. Разместить
через `/infrastructure-deep-dive placement`».

### R-COV-003 — Сервер без единого рантайма

**Severity:** `hint`.

**Где:** `server.md` + `runtime.md`.

**Обнаружение:** slug сервера не появляется ни в одном `runtime.servers`.
Машина оплачивается, но в периметре на ней ничего не развёрнуто.

**Рекомендация:** «сервер X не несёт ни одного рантайма. Завести рантайм
через `/infrastructure-deep-dive runtime` или проверить, нужна ли
машина».

### R-COV-004 — Runtime, в который ничего не размещено

**Severity:** `hint`.

**Где:** `runtime.md` + `placement.md`.

**Обнаружение:** slug рантайма не появляется ни в одной строке
`placement.md`. Среда есть, жителей нет.

**Рекомендация:** «в рантайм X ничего не размещено. Либо разместить
юниты через `/infrastructure-deep-dive placement`, либо проверить, нужен
ли рантайм».

### R-COV-005 — Джоба периметра без placement

**Severity:** `hint`.

**Где:** `job.md` + `placement.md`.

**Обнаружение:** строка `job.md`, для которой нет строки `placement.md` с
`unit: job:<slug>` — джоба заведена, но нигде не исполняется. Проверка:
каждый slug `job.md` ↔ юниты placement.

**Рекомендация:** «джоба X не размещена. Разместить через
`/infrastructure-deep-dive placement`».

### R-COV-006 — Stateful-ресурс без бэкап-джобы

**Severity:** `hint`.

**Где:** секции `## Resources` паспортов `docs/projects/*/services/*/README.md`
+ `docs/projects/*/services/platform.md` (строки `own`) +
`shared-platform.md` + `job.md`.

**Обнаружение:** ресурс, несущий данные, не входит ни в один `job.target`
— ни напрямую, ни через владельца. Что считать stateful — суждение по
технологии: БД (`postgres`/`mysql`/`mongo`/…) и persistent-хранилища из
`## Resources` (покрытие — через `target: service:<project>/<svc>`
владельца), объектные хранилища и registry (`shared-platform` / `own`
типов `object-storage`/`registry`), durable-стримы брокера (jetstream,
kafka). Эфемерное (кэш, чистый pub/sub) не считается. Если state-заметка
ресурса/джобы несёт явное решение «не бэкапим, потому что …» — findings
нет, решение цитируется в reasoning-trace.

**Рекомендация:** «ресурс X несёт данные, но не входит ни в один
`job.target` — бэкапов нет. Завести джобу через
`/infrastructure-deep-dive job` или зафиксировать осознанное решение в
state».

## Что не делает infrastructure-audit

- Не сверяет паспорта сервисов по существу, домены, interface, screens —
  из проектов читаются реестры `services/service.md` и
  `services/platform.md` (резолв `placement.unit` и потребностей
  `shared:`) плюс **только** секции `## Resources` / `## Messaging`
  паспортов (R-COV-006 / R-SEM-005). Внутренности
  проектных слоёв — `/service-audit <slug>` и `/cross-audit` (углы
  `service-placement` · `platform-shared`).
- Не правит ни периметр, ни проектные файлы — только отчёт.
- Не предлагает promotion `draft → stable` — это
  `/infrastructure-deep-dive`.
- Не понижает `stable → draft` — может только сказать в `error`-отчёте,
  что запись несовместима со stable.
- Не запускает другие скилы — даёт текст, что запустить архитектору.
