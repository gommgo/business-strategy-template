---
name: infrastructure-audit
description: "Узкий аудит консистентности ИТ-периметра бизнеса в `docs/projects/infrastructure/` (server · runtime · shared-platform · job · placement) — слой один на бизнес, аргументов нет, один прогон = весь периметр. Структурные нарушения: `placement.unit` на несуществующий сервис (`service:<project>/<svc>` ↔ реестры `docs/projects/*/services/service.md`), несуществующий проектный ресурс (`platform:<project>/<slug>` ↔ `platform.md` проекта, причём `provided-by` обязан быть `own`) или несуществующий shared-ресурс; `placement.runtime` вне `runtime.md`; `runtime.servers` вне `server.md`; `placement.unit` `job:<slug>` вне `job.md`; `job.target` на неучтённую сущность; рассинхрон реестра job.md и файлов jobs/<slug>.md (включая обязательные секции и stable-джобу без Verify); потребность проекта `provided-by: shared:<slug>` без записи в `shared-platform.md`; дубли slug во всех реестрах; невалидные enum (`type`, `environment`, `status`). Семантические подозрения: IP/hostname/ОС/секреты/runtime-механика в файлах слоя; shared-ресурс-сирота (не потребляет ни один проект); два проекта с own-ресурсом одной технологии (напрашивается общий). Coverage: сервис проекта без prod-размещения; own-ресурс, используемый shared-ресурс или джоба периметра без placement; сервер без единого рантайма; runtime, в который ничего не размещено. Не правит артефакты, только отчёт; деструктивные правки — через `/infrastructure-deep-dive` (периметр) и `/service-deep-dive` (проектные services/). Сквозную сверку с проектными слоями ведёт `/cross-audit` (углы `service-placement` · `platform-shared`). Использовать перед коммитом артефактов периметра, когда `/infrastructure-deep-dive` предлагает прогон в конце сессии, перед `/cross-audit`, или когда архитектор подозревает рассогласование размещения."
---

# infrastructure-audit

Аудит консистентности **ИТ-периметра бизнеса** в
`docs/projects/infrastructure/`:

- **учёт серверов** `server.md` — железо/VPS;
- **рантаймы** `runtime.md` — k8s-кластеры и compose-хосты по окружениям;
- **общие платформенные ресурсы** `shared-platform.md`;
- **размещение** `placement.md` — единственное место «кто где живёт».

Канон формы — `docs/projects/infrastructure/README.md` (канон и данные —
в одних файлах, слой в `_template/` не шаблонируется). Аудит **читает и
сообщает**, ничего не правит: правки периметра идут через
`/infrastructure-deep-dive`, правки проектных `services/`
(`service.md` · `platform.md`) — через `/service-deep-dive <slug>`.

Слой **один на бизнес** — аргументов у скилла нет, один прогон = весь
периметр. Слой межпроектный, поэтому аудит read-only заглядывает в
реестры всех проектов (`docs/projects/*/services/service.md` +
`platform.md`, исключая `_template`) — но **только** чтобы резолвить
`placement.unit` и потребности `provided-by: shared:<slug>` и считать
coverage. Семантическую сверку проектных слоёв между собой ведёт
`/cross-audit` (углы `service-placement` · `platform-shared`), не этот
скилл.

## Точки входа

| вызов | поведение |
|---|---|
| `/infrastructure-audit` | полный прогон всех 4 реестров периметра |

## Что делать при запуске

1. Прочитать `docs/projects/infrastructure/README.md` — освежить канон и
   инварианты слоя.
2. Прочитать `references/rules.md` — реестр проверок с severity.
3. Прочитать 4 реестра слоя: `server.md`, `runtime.md`,
   `shared-platform.md`, `placement.md`.
4. Прочитать read-only межпроектный контекст: все
   `docs/projects/*/services/service.md` и
   `docs/projects/*/services/platform.md` (листингом каталогов, исключая
   `_template`) — юниты и потребности для резолва рефов и coverage.
5. Прочитать ветку state слоя в едином дереве оркестратора
   (`../entrypoint/state/infrastructure/`) — для проверки «stable со
   state-blocker'ами».
6. Прогнать правила по очереди. Собрать findings.
7. Сгруппировать по сущности, отсортировать по severity внутри.
8. Вывести отчёт в чат.
9. Перезаписать `audit-state/last-report.md` с reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | `placement.unit` на несуществующий сервис/ресурс; `placement.runtime` вне `runtime.md`; `runtime.servers` вне `server.md`; потребность `shared:<slug>` без записи `shared-platform.md`; дубль slug; невалидный enum |
| `warning` | Семантическое подозрение | IP/hostname/ОС/секрет/runtime-механика в файле слоя; shared-ресурс-сирота; два проекта с `own`-ресурсом одной технологии |
| `hint` | Coverage / стиль, не ломает | сервис без prod-размещения; размещаемый ресурс без placement; сервер без рантайма; runtime без единого размещения |

Подробный реестр — `references/rules.md`.

## Формат отчёта

В чат:

```
=== /infrastructure-audit ===
Прочитано: 4 реестра периметра + N реестров services/ по M проектам.

[error] placement:service:crm/orders → runtime `main-cluster` отсутствует
  в runtime.md.
  Что делать: завести рантайм или поправить строку через
  /infrastructure-deep-dive placement.

[error] проект shop → platform.md: `provided-by: shared:minio`, записи
  `minio` в shared-platform.md нет. Потребность без ответа периметра.
  Что делать: завести общий ресурс через
  /infrastructure-deep-dive shared-platform (или переключить проект на
  own через /service-deep-dive shop).

[warning] server:srv-prod-1 → в `purpose` упомянут hostname
  `prod1.example.com`. Адресация — зона <org>/infra.
  Что делать: убрать через /infrastructure-deep-dive server:srv-prod-1.

[hint] service:crm/ai-gateway → нет размещения в prod-рантайм
  (есть только dev-box).
  Что делать: разместить через /infrastructure-deep-dive placement.

Сводка: 2 error / 1 warning / 1 hint.
```

Группировка — по сущности; внутри — `error → warning → hint`.

## `audit-state/last-report.md`

Отчёт лежит **рядом со скиллом** (слой один — без под-папок):

```
.claude/skills/infrastructure-audit/audit-state/last-report.md
```

После каждого прогона перезаписывается одним файлом с reasoning-trace:
какие правила запускал, какие записи и реестры проектов проверил, что
нашёл, почему. Это не журнал — следующий прогон перезатирает. В git,
чтобы команда могла читать.

Структура:

```markdown
---
ran-on: all
files-read: <4 реестра периметра + N services-реестров (M проектов)>
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила структуры (R-STRUCT-*)
- R-STRUCT-001 «дубли slug»: ...
...

## Правила семантики (R-SEM-*)
- ...

## Правила coverage (R-COV-*)
- ...
```

## Что не делать

- **Не править артефакты.** Аудит — только отчёт. Периметр правится через
  `/infrastructure-deep-dive`; проектные `services/` — через
  `/service-deep-dive <slug>`.
- **Не читать `_template/`** как данные (это образец формы проектных
  слоёв; периметр в нём не шаблонируется).
- **Не лезть глубже реестров проектов.** Из проектов читаются только
  `services/service.md` и `services/platform.md` — для резолва рефов и
  coverage. Паспорта сервисов, домены, interface — зона `/service-audit`
  и `/cross-audit`.
- **Не понижать `stable → draft`.** Максимум — error в отчёте, архитектор
  понизит руками.
- **Не выдумывать findings.** Правило не сработало — не писать «возможно,
  тут что-то не так на всякий случай». Для `warning`-подозрений (два
  `own` одной технологии) приводить конкретные строки-доказательства.
- **Не аккумулировать историю** в `audit-state/` — перезаписывать
  `last-report.md` каждый прогон.
- **Не реализовывать suppressions** для структурных правил — они
  детерминированы (реф резолвится или нет). Семантические `warning`
  (own-дубль технологии) могут быть осознанным решением — аудит всё равно
  показывает их, а пометку «осознанная изоляция» читает из state-заметки
  записи и, найдя её, понижает finding до `hint` с цитатой решения.
- **Не запускать `/infrastructure-deep-dive`** автоматически из аудита —
  это делает архитектор руками по выводу.
- **Не предлагать клиенту запустить** `/infrastructure-audit`. Это
  инструмент архитектора; в клиент-режиме (`entrypoint-for-business`) он
  не упоминается.
