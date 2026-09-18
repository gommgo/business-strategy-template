---
name: mobile-audit
description: "Аудит консистентности карты мобильного приложения проекта в `docs/projects/<project-slug>/mobile/<surface>/` — по папке на поверхность с `type: mobile` из реестра `surface.md` (12 kind: entities · screens · flows · features · shell · entry-points · permissions · system-actions · widgets · background-tasks · shared-api · shared-lib). Невалидные ссылки на источники (ситуации interface той же поверхности, агрегаты и события доменов сервисов), битые внутрислойные ссылки, невалидные enum и словари состояний, регистр структурных идентификаторов (`key` PascalCase, push-категория UPPER_SNAKE), достижимость и носители (экран-сирота, фича без экрана/входа/системного действия/фоновой задачи, сущность без потребителя, разрешение без использования), cross-feature, пара «вход `widget` ↔ виджет» и зеркало `widgets.actions` ↔ `system-actions.channels`, инварианты вне экранов (голосовое действие без фраз, `opens-app` без экрана, действие без ответа; виджет без базовых состояний; фоновая задача без `fallback`, `exact` без уведомления, `continuous` без разрешения, офлайн-правки без синхронизации), покрытие `shared-api`, обязательные сценарии `app-start`/`login` и вход `demo`, платформенная механика и код в ячейках (интервалы, планировщики, имена API и файлов), пустые обязательные слоты в stable-записях, папка поверхности вне реестра или для `type ≠ mobile`, `screens/`/`fsd/` у мобильной поверхности, ссылка из одной поверхности в другую. Не правит артефакты, только указывает; деструктивные правки — через `mobile-deep-dive`. Использовать перед коммитом артефактов слоя, когда `mobile-deep-dive` предлагает прогон в конце сессии, перед `/cross-audit`, если трогали мобильную поверхность, или при подозрении на рассогласование. Принимает `<project-slug>` первым аргументом; без него — пикер по проектам. Без `<surface>` — прогон по всем мобильным поверхностям; узкий scope — `<kind>` или `<kind>:<slug>`."
---

# mobile-audit

Аудит консистентности 12 артефактных файлов карты **одной мобильной
поверхности** проекта в `docs/projects/<project-slug>/mobile/<surface>/`.
Канон формы — `docs/projects/_template/mobile/README.md` и формы в подпапке
`_template/`. Аудит **читает и сообщает**, ничего не правит: каскадные
правки идут через `mobile-deep-dive`.

Слой партиционирован по поверхности: на каждую поверхность с `type: mobile`
из реестра `docs/projects/<project-slug>/surface.md` — своя папка
`mobile/<surface>/` (она встаёт на место `screens/<surface>/`; `fsd/` у
мобильной поверхности нет). Внутрислойные ссылки проверяются **в пределах
одной поверхности**, ссылки на источники — в `interface/<surface>/` и
`services/*/domains/` **того же проекта**. Аудит итерирует по каждой папке
поверхности независимо.

## Выбор проекта и поверхности

Аргументы позиционны — `<project-slug>` первый, `<surface>` второй (опц.):

| вызов | проект · поверхность |
|---|---|
| `/mobile-audit <project-slug> <surface> …` | взять `<project-slug>` и `<surface>` |
| `/mobile-audit <project-slug> …` (без surface) | проект задан; **все** мобильные поверхности проекта |
| `/mobile-audit …` (без slug) | `AskUserQuestion`-пикер **по именам** проектов (исключая `_template`); затем все мобильные поверхности |

1. Первый аргумент — подпапка `docs/projects/` (кроме `_template`) →
   `<project-slug>`; иначе пикер по именам проектов. Проектов нет — «нечего
   аудитить», выйти.
2. Прочитать `surface.md`. Следующий аргумент — slug строки реестра → одна
   поверхность; нет аргумента → все строки с `type: mobile` **плюс** каждая
   существующая папка `mobile/<X>/` (даже если `X` нет в реестре или `type`
   не `mobile` — ради R-SURF).
3. Узкий scope: `<kind>` (один файл + перекрёстные ссылки) или
   `<kind>:<slug>` (одна запись + 1-shell соседи); требуют заданной
   `<surface>`. `kind` ∈ {`entities`, `screens`, `flows`, `features`,
   `shell`, `entry-points`, `permissions`, `system-actions`, `widgets`,
   `background-tasks`, `shared-api`, `shared-lib`}; для экрана `<slug>` —
   его `key`.

## Что аудит читает

- Рабочая зона: 12 файлов `docs/projects/<project-slug>/mobile/<surface>/`.
- Реестр-хребет `surface.md` — перечень поверхностей и их `type`; листинг
  папок `screens/`, `fsd/` проекта (для R-SURF-004).
- Источники **той же поверхности**:
  `interface/<surface>/{situation,block,zone,who,data-items}.md`.
- Read-only контекст: `services/service.md` и
  `services/*/domains/<ctx>/` (агрегаты, `events/`) — существует ли адресат
  доменного рефа. Домена может ещё не быть — это подозрение, не ошибка
  модели.
- Ветку state `../entrypoint/state/projects/<project-slug>/mobile/<surface>/`
  — только для проверки «stable с blocker'ом» и рамки приложения
  (`_frame.md`: есть ли вход, публикуется ли в магазинах, платформы).
- Advisory: если рядом доступен checkout бэкенда
  (`../backend/api/openapi.yaml`) — сверка операций `shared-api.md`;
  недоступен — правило пропускается без находки.

**Чего аудит не читает:** другие проекты; другие поверхности при разрешении
ссылок (ссылка в чужую поверхность — error); `_template/` как данные; код
форка `<org>/mobile` и его `docs/stack/`. Глубину сверки с доменами,
сервисами и web-поверхностью ведёт `/cross-audit` (углы `surface-mobile` ·
`mobile-domain` · `mobile-service` · `mobile-web`).

## Что делать при запуске

1. Определить `<project-slug>` и (опц.) `<surface>`.
2. Прочитать канон `docs/projects/_template/mobile/README.md` и формы
   `_template/*.md` — освежить колонки, enum'ы, словари состояний,
   инварианты, anti-patterns.
3. Прочитать `references/rules.md` — реестр проверок с тяжестью.
4. Прочитать рабочую зону и источники (или подмножество по scope).
5. Прогнать правила по очереди, собрать findings.
6. Сгруппировать: поверхность → запись → `error → warning → hint`.
7. Вывести отчёт в чат.
8. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель или контракт с `<org>/mobile` | битый реф; enum вне канона; `key` не PascalCase; экран-сирота; фича без носителя; cross-feature; вход `widget` без виджета; рассинхрон зеркала `widgets.actions`; `voice` без `phrases`; `exact` без уведомления; `continuous` без разрешения; фоновая задача без `fallback`; пустой обязательный слот в stable; папка для `type ≠ mobile`; `screens/` или `fsd/` у мобильной поверхности |
| `warning` | Семантическое подозрение | платформенная механика или код в ячейке; обещание точного времени исполнения в фоне; запись «на всякий случай» без внятной ситуации; `live`-виджет без длящегося события; разрешение с запросом на первом экране; доменный реф на отсутствующее событие/агрегат |
| `hint` | Coverage / стиль | ситуация interface без носителя в приложении; сущность без потребителя; офлайн `full` без задачи синхронизации; stable со ссылкой на draft; мобильная поверхность реестра без папки слоя; операции `shared-api` вне спецификации бэкенда |

Подробный реестр — `references/rules.md`.

## Формат отчёта

```
=== /mobile-audit <project-slug> [<surface>] ===
Проект: <project-slug>
Поверхности: <surface-1>, <surface-2>
Прочитано: 12 файлов × N поверхностей, M записей.

— Поверхность <surface> —

[error] screens:TodoDetail → экран недостижим: нет в shell, flows,
  entry-points и target системных действий (R-REACH-001).
  Что делать: /mobile-deep-dive <project-slug> <surface> screens:TodoDetail —
  дать вход или удалить экран.

[error] background-tasks:due-reminder → timing: exact, но в result нет
  notification:<slug> (R-INV-006).
  Что делать: /mobile-deep-dive … background-tasks:due-reminder — связать с
  push-входом или ослабить timing.

[warning] widgets:today-tasks → в freshness «каждые 15 минут» — механика
  обновления, а не требование смыслом (R-SEM-001).
  Что делать: переформулировать требование свежести словами пользователя.

[hint] situation:glance-today (interface) не дошла ни до экрана, ни до
  виджета (R-COV-001).

Сводка: 2 error / 1 warning / 1 hint. Вердикт: есть errors.
```

Группировка — по поверхности, внутри — по записи, внутри записи —
`error → warning → hint`. В каждом finding — id правила и конкретный шаг
через `/mobile-deep-dive`.

## `audit-state/<project-slug>/last-report.md`

Отчёт лежит рядом со скиллом, скоупится по проекту:
`.claude/skills/mobile-audit/audit-state/<project-slug>/last-report.md`.
После каждого прогона перезаписывается одним файлом с reasoning-trace:
какие правила запускал, какие записи проверил, что нашёл, почему. Не
журнал — следующий прогон перезатирает.

```markdown
---
project: <project-slug>
surfaces: [<surface>, …]
ran-on: <scope: all | kind | kind:slug>
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace
## R-SURF / R-XSURF
## R-STRUCT
## R-SRC
## R-REF / R-MIRROR
## R-REACH
## R-INV
## R-SEM
## R-MAT / R-COV
```

## Что не делать

- **Не править артефакты и state.** Только отчёт; правки — через
  `/mobile-deep-dive <project-slug> <surface>`.
- **Не выдумывать «правильные» значения** — рекомендация ведёт в
  `mobile-deep-dive`, не подменяет аналитика.
- **Не выдумывать findings.** Правило не сработало — не писать «возможно,
  тут что-то не так».
- **Не смешивать проекты и поверхности** при разрешении ссылок.
- **Не делать кросс-слойную семантику** (payload событий, сервис-владелец
  в `Messaging`, общий путь с web) — это `/cross-audit`.
- **Не расширять scope** сверх заданного аргументами.
- **Не аккумулировать историю** в `audit-state/` — перезаписывать
  `last-report.md`.
- **Не понижать `stable → draft`** и не запускать `/mobile-deep-dive` сам.

Помни: stable-записи читает `/scaffold` форка `<org>/mobile` — errors в
stable материализуются в код на двух платформах.
