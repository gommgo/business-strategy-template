# Чек-листы полей по kind

Какие слоты обязательны у каждого артефакта сервисного уровня и что
считается «заполнено». Source of truth канона — формы в
`docs/projects/_template/services/` (`service.md`, `platform.md`,
`architecture.md`, `_templates/service-readme.md`); этот файл — рабочая
шпаргалка скилла для подсчёта дыр в сводке и проверки перед stable.

Общие правила:

- «Заполнено» = непустое осмысленное значение, не placeholder из формы
  (`<slug>`, `<короткое имя>`, `<одно предложение>`, `<...>`).
- Легальная пустота — только **явная**: `—`, `_нет_`, `_N/A (…)_` с
  обоснованием, уместным типу сервиса. Молча отсутствующая секция или
  пустая таблица — дыра.
- Все enum-значения и заголовки таблиц — английские структурные
  идентификаторы handoff-контракта (их читают `<org>/backend` и
  `<org>/infra`); проза — по-русски.

## Строка реестра `service.md`

| слот | обязателен | заполнено, если |
|---|---|---|
| `slug` | да | kebab-case, уникален в файле, = имя папки `services/<slug>/` |
| `name` | да | человекочитаемое имя |
| `description` | да | одно предложение, какую часть продукта несёт |
| `type` | да | ровно одно из `api` \| `worker` \| `gateway` \| `edge` \| `bot` |
| `surfaces` | да | массив slug'ов из `surface.md` либо явное `—` (норма для `worker`/`gateway`) |
| `status` | да | `draft` \| `stable` |

## Строка реестра `platform.md`

| слот | обязателен | заполнено, если |
|---|---|---|
| `slug` | да | kebab-case, уникален в файле |
| `name` | да | человекочитаемое имя |
| `description` | да | зачем нужен проекту, бизнес-смыслом |
| `type` | да | одно из `message-broker` \| `api-gateway` \| `cdn` \| `object-storage` \| `idp` \| `other` |
| `technology` | да | осознанный выбор архитектора (свободный slug: `nats`, `traefik`, …) |
| `provided-by` | да | `own` либо `` `shared:<slug>` `` (реф в `docs/projects/infrastructure/shared-platform.md`) |
| `status` | да | `draft` \| `stable` |

## Паспорт сервиса (`<svc>/README.md`, kind `service-passport`)

Обязательные H2 (все 8 присутствуют всегда; «пусто» допустимо только явной
пометкой, уместной типу сервиса):

| H2 | заполнено, если | легальная пустота |
|---|---|---|
| `Purpose` | оба пункта: «что делаем» и «чего не делаем» | нет |
| `Exposes` | таблица функций: `slug` · `name` · `description` · `audience` (массив `surface:`/`service:`/`integration:`-рефов) · `backed-by` (`use-case:<ctx>.<Operation>` либо `—`) · `status` | `_N/A (worker — живёт на событиях и расписаниях)_` и аналоги |
| `Owned Contexts` | таблица: `context` (ссылка на `domains/<ctx>/README.md`) · «покрывает» · `brief` | `_N/A (no domains)_` — для `gateway`/`edge`/`bot` это норма, для `api` — подозрение |
| `Dependencies` | таблица: `ref` (`` `service:` ``/`` `platform:` ``/`` `integration:` ``) · `nature` (бизнес-смыслом) · `status` | `- _нет_` |
| `Resources` | таблица: `resource` · `type` (`database` \| `cache` \| `search-index` \| `vector-store` \| `object-storage` \| `other`) · `technology` · `purpose` · `status` — потребность + технология, без операционки | `_нет (stateless service)_` |
| `Messaging` | таблица: `direction` (`produces` \| `consumes`) · `broker` (`` `platform:<slug>` ``) · `topic` · `event` (`` `event:<ctx>.<Event>` ``) · `purpose` · `status` | `_N/A_` (не ходит в брокер) |
| `Fronts` | только `type: gateway`: `Integration` + `Client` + `Normalizes` | `_N/A_` — обязательное значение для всех остальных типов |
| `Notes` | список особенностей | `- _нет_` |

Дополнительно к H2:

- вводная фраза под заголовком — какую часть продукта несёт (из
  name/description реестра); `type` в паспорте **не дублируется**
  (single source — реестр);
- ни в одной секции нет runtime-механики: реплик, CPU/RAM, портов,
  версий, retention, helm-values, env-переменных, имён docker-образов,
  hostname'ов;
- `produces` пишет только сервис-владелец контекста события (файл
  `domains/<ctx>/events/<Event>.md` лежит в этом сервисе).

## Singleton `architecture.md`

| секция | обязательна | заполнено, если |
|---|---|---|
| `Topology` | да | одна mermaid-диаграмма `flowchart LR`; узлы — только slug'и из `service.md` / `platform.md` / `surface.md` / `integration.md`; сплошные стрелки = sync (есть в `Dependencies`), пунктирные = async (есть в `Messaging`); шаблонная диаграмма формы заменена на реальную |
| `Decisions` | да | нумерованный список falsifiable-решений разбиения (≥1), формулировки архитектора |
| `Flows` | нет | 3–7 однострочных потоков либо `_нет_` |

Здесь авторятся **только** `Decisions`; всё остальное — свод. Ребро на
диаграмме без авторской записи в паспорте/реестре — дыра свода, чинится в
паспорте.

## State-заметка (своя ветка дерева оркестратора)

`../entrypoint/state/projects/<project-slug>/services/<kind>/<slug>.md`,
`<kind>` ∈ {`service`, `platform`, `architecture`}:

- frontmatter: `kind` · `slug` · `ref` (путь к артефакту);
- секции (любая может отсутствовать): `## Открытые вопросы` (маркер
  `**blocker**` блокирует stable), `## Архитектурные решения`,
  `## Что копать дальше`;
- все секции пусты → файл удалить; forward-only.
