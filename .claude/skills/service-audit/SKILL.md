---
name: service-audit
description: "Узкий аудит сервисного слоя проекта в `docs/projects/<slug>/services/`: папки вне реестра, контекст без владельца или в двух сервисах, рёбра зависимостей и событий в пустоту, непарные события, общая база нескольких сервисов, узлы свода вне реестров, runtime-механика в артефактах, ресурсы-сироты, поверхность без сервиса. Только отчёт, правки — через `/service-deep-dive`; сверку с поверхностями и размещением ведёт `/cross-audit`. Звать перед коммитом сервисов, по предложению `/service-deep-dive` или при подозрении на рассогласование топологии; без `<project-slug>` — пикер."
---

# service-audit

Аудит консистентности сервисного слоя **одного проекта** в
`docs/projects/<project-slug>/services/`:

- **реестр-хребет** `service.md` — сервисы (deploy-юниты); его slug'и —
  имена папок `services/<svc>/`.
- **реестр** `platform.md` — платформенные ресурсы проекта (брокер,
  api-gateway, CDN, object storage, IDP).
- **1 singleton** `architecture.md` — свод топологии + Decisions.
- **паспорта** `services/<svc>/README.md` (kind `service-passport`) — и
  папки `domains/<ctx>/` внутри доменных сервисов (для аудита — только
  структура владения и события; содержимое контекстов — не сюда).

Канон формы — `docs/projects/_template/services/README.md` (+ формы
`service.md` · `platform.md` · `architecture.md`). Сервис — структурная ось
слоя: slug реестра = имя папки. Аудит **читает и сообщает**, ничего не
правит: каскадные правки идут через `/service-deep-dive <project-slug>`
(сервисный уровень) и `/domain-deep-dive` (домены).

**Сквозную проверку** (services ↔ `interface`/`screens` поверхностей,
services ↔ `placement.md` периметра, integration-цепочки через `_shared/`)
делают `/cross-audit` (углы `service-placement` · `platform-shared` и
интеграционные) и `/infrastructure-audit`. Здесь — только внутрислойная, в
пределах `services/` одного проекта (плюс точечные структурные ссылки
наружу: `surface.md`, `integration.md` того же проекта и существование
записей `infrastructure/shared-platform.md` — листингом, без их аудита).

## Мультипроект: выбор проекта

Аудит **скоупится в один проект**. Первый позиционный аргумент —
`<project-slug>`. Без него скилл строит пикер через `AskUserQuestion` **по
именам** проектов (подкаталоги `docs/projects/`, исключая `_template` —
образец формы — и `infrastructure` — ИТ-периметр бизнеса; текст опции — имя
из `vision`, slug — деталь). Один прогон = один проект.

## Точки входа

| вызов | поведение |
|---|---|
| `/service-audit` | пикер проекта → полный прогон слоя выбранного |
| `/service-audit <project-slug>` | полный прогон `services/` проекта |
| `/service-audit <project-slug> <service-slug>` | один паспорт + строка реестра + 1-shell соседи по рёбрам |
| `/service-audit <project-slug> platform` | реестр `platform.md` + ссылающиеся паспорта |
| `/service-audit <project-slug> architecture` | свод `architecture.md` против паспортов и реестров |

Если первый аргумент совпал с папкой в `docs/projects/` (кроме `_template`
и `infrastructure`) — это `<project-slug>`. Иначе — пикер.

## Что делать при запуске

1. **Определить проект.** Разобрать первый аргумент как `<project-slug>`;
   если не задан или не совпал с папкой — пикер по именам проектов.
   Зафиксировать `<project-slug>` на прогон. Если слоя
   `docs/projects/<project-slug>/services/` нет — сообщить и предложить
   `/service-deep-dive <project-slug>` (bootstrap); прогон не идёт.
2. Прочитать `docs/projects/_template/services/README.md` — освежить канон
   (инварианты слоя, обязательные H2, anti-patterns).
3. Прочитать `references/rules.md` — реестр проверок с severity.
4. Прочитать файлы слоя (или подмножество по args):
   - реестры `service.md`, `platform.md` и singleton `architecture.md`;
   - паспорта: **листингом** каталогов `services/*/README.md`, не
     угадывая имена (расхождение листинга с реестром — R-STRUCT-002);
   - структуру доменов: листинг `services/*/domains/*/` и файлов
     `domains/<ctx>/events/*.md` (для владения контекстами и парности
     Messaging) — без чтения доменного содержимого;
   - точечные опоры вне слоя: `surface.md`, `integration.md` проекта;
     `docs/projects/infrastructure/shared-platform.md` (существование
     записей по `provided-by`); листинг `<P>/domains/` на корне проекта
     (контексты мимо сервиса — R-STRUCT-003).
5. Прочитать ветку state слоя в едином дереве оркестратора
   (`../entrypoint/state/projects/<project-slug>/services/`) — для проверок
   типа «stable с blocker-вопросами».
6. Прогнать правила по очереди. Собрать findings.
7. Сгруппировать по сущности (сервис / ресурс / architecture),
   отсортировать по severity внутри.
8. Вывести отчёт в чат.
9. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает топологию | Дубль `slug`; папка `services/<svc>/` вне реестра; контекст в двух сервисах или вовсе без владельца; `consumes` без парного `produces`; `Dependencies` на несуществующий юнит; `domains/` у `gateway`/`edge`/`bot`; узел `architecture.md` вне реестров; `provided-by: shared:<slug>` в пустоту; невалидный enum; пустой обязательный слот при `stable` |
| `warning` | Семантическое подозрение | Платформенный ресурс-сирота; `Messaging.broker` не `message-broker`; runtime-механика в артефактах (порты, реплики, версии, image, env, cron-выражения в `Workers.trigger`); `stable` при `**blocker**` в state; `Fronts` у не-gateway / gateway без `Fronts` |
| `hint` | Coverage / стиль, не ломает | Сервис без контекстов и без `Exposes` (пустой); поверхность реестра, которую не обслуживает ни один сервис; событие домена без публики (никто не `produces`/`consumes`) |

Подробный реестр — `references/rules.md`.

## Формат отчёта

В чат:

```
=== /service-audit <project-slug> ===
Проект: <project-slug>
Прочитано: 2 реестра + architecture.md + N паспортов; M контекстов, K записей.

[error] services/notifications/ → папки нет в реестре service.md.
  Что делать: завести строку реестра или удалить папку через
  /service-deep-dive <project-slug>.

[error] orders → Messaging: consumes (events-broker, billing-events,
  event:billing.InvoicePaid), но ни один сервис не publishes эту пару.
  Что делать: завести produces у владельца контекста billing или убрать
  consumes через /service-deep-dive <project-slug> orders.

[warning] platform:cdn-assets → ресурс не требует ни один паспорт
  (нет в Dependencies / Messaging.broker). Сирота.
  Что делать: подключить потребителя или удалить запись через
  /service-deep-dive <project-slug> platform.

[warning] billing → Resources: «postgres 16, 4Gb RAM» — runtime-механика
  в паспорте (anti-pattern канона).
  Что делать: оставить «потребность + технологию», операционка —
  <org>/infra. Поправить через /service-deep-dive <project-slug> billing.

[hint] surface `web-admin` (surface.md) не числится в surfaces ни одного
  сервиса — кто её обслуживает?

Сводка: 2 error / 2 warning / 1 hint.
```

Группировка — по сущности; внутри — `error → warning → hint`.

## `audit-state/<project-slug>/last-report.md`

Отчёт лежит **рядом со скиллом**, скоупится по проекту:

```
.claude/skills/service-audit/audit-state/<project-slug>/last-report.md
```

После каждого прогона перезаписывается одним файлом с reasoning-trace:
какие правила запускал, какие записи проверил, что нашёл, почему. Это не
журнал — следующий прогон по этому проекту перезатирает. Отчёты разных
проектов не сталкиваются. В git, чтобы команда могла читать.

Структура:

```markdown
---
project: <project-slug>
ran-on: <scope: all | <service-slug> | platform | architecture>
files-read: <2 реестра + architecture + N паспортов + структура domains>
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила структуры (R-STRUCT-*)
- R-STRUCT-001 «дубли slug»: ...
- R-STRUCT-002 «папки ↔ реестр»: ...
...

## Правила семантики (R-SEM-*)
- ...

## Правила coverage (R-COV-*)
- ...
```

## Что не делать

- **Только отчёт.** Правки сервисного уровня — через
  `/service-deep-dive <project-slug>`, доменные — через
  `/domain-deep-dive`; аудит их не запускает — это делает архитектор по
  выводу аудита.
- **Один проект.** `_template/` — не данные, `infrastructure/` аудитит
  `/infrastructure-audit`.
- **Не понижать `stable → draft`.** Максимум — error «несовместимо со
  stable» в отчёте, архитектор понизит руками.
- **Не выдумывать findings.** Правило не сработало — не писать «возможно,
  тут что-то не так на всякий случай».
- **Без suppressions.** Структурный аудит детерминирован — slug
  резолвится или нет, пара produces/consumes есть или нет. Ложных
  срабатываний не бывает, подавлять нечего.
- **Инструмент архитектора.** В клиент-режиме (`entrypoint-for-business`)
  `/service-audit` клиенту не предлагается.
