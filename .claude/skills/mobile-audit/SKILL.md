---
name: mobile-audit
description: "Аудит консистентности карты мобильного приложения проекта в `docs/projects/<project-slug>/mobile/<surface>/` (12 kind: entities · screens · flows · features · shell · entry-points · permissions · system-actions · widgets · background-tasks · shared-api · shared-lib) — по папке на поверхность с `type: mobile` из реестра `surface.md`. Ловит битые ссылки на источники (ситуации interface, агрегаты и события доменов) и внутри слоя, невалидные enum, словари и регистр идентификаторов, недостижимые экраны и записи без носителя, рассинхрон зеркал, нарушения инвариантов вне экранов (голос, виджеты, фоновые задачи, офлайн), дыры покрытия и обязательных заготовок, платформенную механику и код в ячейках, пустые слоты stable-записей и выход ссылки за границу поверхности. Только отчёт; правки — через `mobile-deep-dive`. Использовать перед коммитом артефактов слоя, по предложению `mobile-deep-dive` в конце сессии, перед `/cross-audit` или при подозрении на рассогласование. Аргументы: `<project-slug>` (без него — пикер по проектам), опционально `<surface>` (без неё — все мобильные поверхности), узкий scope — `<kind>` или `<kind>:<slug>`."
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

- **Только отчёт.** Артефакты и state правит
  `/mobile-deep-dive <project-slug> <surface>`; аудит его не запускает и
  не понижает `stable → draft`.
- **Не выдумывать «правильные» значения** — рекомендация ведёт в
  `mobile-deep-dive`, не подменяет аналитика.
- **Не выдумывать findings.** Правило не сработало — не писать «возможно,
  тут что-то не так».
- **Не расширять scope** сверх заданного аргументами.

Stable-записи читает `/scaffold` форка `<org>/mobile`, поэтому errors в
stable материализуются в код на двух платформах.
