# _shared — кросс-контекстные VO и клиенты интеграций

Форма-образец роллапа платформенных артефактов `_shared/`. Здесь, в каноне (`docs/projects/_template/services/_shared/`), живёт только эта форма; данные `_shared/` каждого проекта (этот README, VO-файлы, папка `integrations/`) живут в его папке `docs/projects/<project-slug>/services/_shared/`.

`_shared/` — общее **между сервисами** проекта; держит два рода платформенных артефактов:

- **cross-context VO** (`<Name>.md`, `kind: vo`) — платформенные значения, разделяемые между bounded contexts (возможно, живущими в разных сервисах);
- **клиенты интеграций** (`integrations/<integration-slug>/README.md`, `kind: integration-client`) — конкретное воплощение интеграции (транспорт + функции с `slug`), к которой обращаются домены, оставаясь transport-agnostic.

VO заводим **только когда реально нужно** (DDD-предпочтение — каждый контекст типизирует своё). В `_shared/` VO попадает только то, что:

1. структурно идентично между ≥2 контекстами (в одном сервисе или в разных),
2. не несёт доменной семантики (не относится к ubiquitous language конкретного контекста),
3. в Go-коде ляжет в платформенный слой, а не в код домена; как код шарится между сервисами (библиотека или копия) — решает `<org>/backend`, design-time этого не фиксирует.

## Purpose

- _что делаем_: даём bounded contexts общий VO-словарь для платформенных значений (ссылки на хранилище, медиа-метаданные и т. п.) и единое design-time описание клиентов интеграций.
- _чего не делаем_: не помещаем сюда доменные VO (например, `Phone` живёт внутри `iam.User`, а `OrderTotal` — внутри `billing.Order`: это бизнес-семантика контекста). Не моделируем здесь кросс-контекстные **агрегаты** или **события**.

## Ubiquitous Language

Cross-domain словарь — узкий список терминов, использующихся в ≥2 контекстах с одинаковым смыслом.

| Бизнес-термин | В коде | Не путать с |
|---|---|---|
| _нет_ | — | — |

## Value Objects

| VO | Файл | Используется в |
|---|---|---|
| _нет_ | — | — |

> Когда заводишь cross-context VO — `cp docs/projects/_template/services/_templates/vo-shared.md docs/projects/<project-slug>/services/_shared/<Name>.md`, заполни секции, добавь строку в таблицу выше.

## Integration clients

Конкретные клиенты внешних систем и соседних проектов. Каждый — папка
`integrations/<integration-slug>/` с `README.md` (`kind: integration-client`):
транспорт, таблица функций с `slug`, ошибки. `integration` в его frontmatter
ссылается на провайдера в продуктовом `integration.md`; `fronted-by` — на
gateway-сервис, который хостит клиента в коде (`—`, если выделенного gateway
нет и клиента вендорит каждый потребляющий сервис).

| Клиент | Папка | Провайдер (`integration.md`) | fronted-by |
|---|---|---|---|
| _нет_ | — | — | — |

> Когда домен обращается к внешней системе / соседу — `cp docs/projects/_template/services/_templates/integration-client.md docs/projects/<project-slug>/services/_shared/integrations/<integration-slug>/README.md`, заполни транспорт и функции, добавь строку в таблицу выше.
