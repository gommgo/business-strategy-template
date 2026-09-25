---
name: cross-audit
description: "Сквозной семантический аудит консистентности между слоями документации роем агентов. Сверяет общие слои (business с реестром проблем и стейкхолдерами, ajtbd, swot, hypothesis-map) с каждым проектом `docs/projects/<slug>/`, а внутри проекта — продукт, interface, композицию поверхностей (screens, telegram-bot-flow, mobile), сервисы и домены; плюс межпроектные стыки `project-map.md` и ИТ-периметр `docs/projects/infrastructure/`. Углы раскрываются в агентов: верхнеуровневые — один раз, пары проект × угол, тройки проект × поверхность × угол; каждый агент сверяет два слоя смыслом, а не slug-валидацией, и ищет тупики вроде «пользователь без UX-покрытия поверхности», «метрика подана как гарантия», «механика ценности без capability», «проект бьёт в несуществующую проблему», «сервис не размещён в периметре». Артефакты не правит: сводный отчёт и решения аналитика по findings. Использовать перед релизом или коммитом правок в нескольких слоях, после крупного апдейта любого слоя и когда deep-dive-скиллы предлагают прогон; аргументы — `<slug>` (один проект), `<lens>` (один угол), `--quick`. Структуру внутри одного слоя проверяют узкие аудиты слоёв."
---

# cross-audit

Сквозной семантический аудит **между слоями** документации. Общие слои —
один экземпляр на бизнес; продуктовые — по проекту, каждый в своей папке
`docs/projects/<project-slug>/`:

- `docs/business/` — профиль бизнеса, реестр проблем `business-problem.md`
  (строка = проблема) и стейкхолдеры; общий.
- `docs/ajtbd/` — сегменты по работам и граф работ Advanced JTBD; общий.
- `docs/swot/` (factor · bet) и `docs/hypothesis-map/` (goal · metric ·
  subject · hypothesis · task) — многопроблемные; общие.
- `docs/projects/project-map.md` — граф межпроектных стыков; общий.
- `docs/projects/infrastructure/` — ИТ-периметр бизнеса (server · runtime ·
  shared-platform · job · placement); один на бизнес, может отсутствовать,
  пока у бизнеса нет сервисов.
- `docs/projects/<slug>/` — продукт: `vision.md`, реестр-хребет
  `surface.md`, корневые kind `user` · `integration` · `boundary` ·
  `constraint` · `market` и `capability/<surface>.md`.
- Внутри проекта, по поверхности: `interface/<surface>/` и композиция —
  `screens/<surface>/`, для `type: bot` — `telegram-bot-flow/<surface>/`,
  для `type: mobile` — `mobile/<surface>/`. Любая из этих папок может
  отсутствовать.
- Внутри проекта, если есть бэкенд: `services/` (реестры `service.md` ·
  `platform.md`, `architecture.md`, паспорта `services/<svc>/README.md`) и
  домены сервисов `services/<svc>/domains/<ctx>/` — по bounded-context,
  surface-агностичны.

`docs/projects/_template/` — канон формы, не данные проекта; в аудит не
входит.

**Поверхность (surface) — ось продукта.** Реестр `surface.md` объявляет
поверхности, их slug'и партиционируют `capability/<surface>.md`,
`interface/<surface>/` и композицию. Корневые kind продукта и домены
кросс-поверхностны. Поэтому угол раскрывается в одну из четырёх единиц:

- **верхнеуровневый** — один агент на прогон (общие слои, граф стыков,
  периметр, M:N продуктов с проблемами);
- **пара** `проект × lens` — цель угла корневая (`vision`, `user`,
  `integration`) или кросс-поверхностная (сервисы);
- **тройка** `проект × поверхность × lens` — source или destination угла
  лежит в папке поверхности;
- **один агент на проект по всем поверхностям** — `dataitems-crosssurface`.

Проблемы бизнеса и продукты связаны M:N через `vision.addresses-problem`,
поэтому углы business-problem ↔ продукт скоупятся к проблемам, которые
закрывает конкретный проект.

Аудит не валидирует slug между слоями: связи семантические
(`docs/projects/_template/project/README.md`), и агент решает смыслом,
соответствует ли запись одного слоя записи другого.

## Точки входа

| вызов | поведение |
|---|---|
| `/cross-audit` | полный прогон: верхнеуровневые углы один раз + пары и тройки по каждому проекту + `dataitems-crosssurface` |
| `/cross-audit <slug>` | один проект (его пары и тройки по его поверхностям) + верхнеуровневые углы один раз |
| `/cross-audit <lens>` | один угол: пара — по всем проектам, тройка — по всем проектам × их поверхностям; сузить до проекта — `/cross-audit <slug> <lens>` |
| `/cross-audit --quick` | быстрый прогон: три foundation-угла продукт ↔ interface (`user-who`, `capability-situation`, `surface-zone`) по каждому проекту × поверхности, `goal-vision` и `subject-user` по каждому проекту как быстрый upstream-чек, `addresses-problem-bizproblem` один раз |

## Углы и их скоуп

Карточка каждого угла (source, destination, «применим если», что искать,
промпт-добавка) и сводная карта углов — `references/angles.md`.

- **Верхнеуровневые** (15): `factor-business`, `currentmetric-metric`,
  `addresses-problem-bizproblem` (M:N над всеми проектами),
  `segmentproblem-bizproblem`, `segment-subject`, `solution-business`,
  `business-segment`, `prospective-consistency`, `provenance-upstream`,
  `stakeholder-subject`, `stakeholder-factor`, `stakeholder-strategy`,
  `projectmap-reciprocity`, `service-placement`, `platform-shared`.
- **Пары `проект × lens`** (7): `goal-vision`, `subject-user` (скоуп — к
  проблемам проекта), `segment-user`, `job-vision`, `segmentproblem-vision`,
  `integration-crossproject`, `service-capability`.
- **Тройки `проект × поверхность × lens`** (23): `surface-capability`,
  `mechanic-capability`, `bet-capability`, `capability-hypothesis`,
  `capability-job`, `user-who`, `capability-situation`, `situation-job`,
  `situation-hypothesis`, `surface-zone`, `surface-screen`,
  `surface-botflow`, `botflow-domain`, `botflow-service` (три последних —
  только `type: bot`), `surface-mobile`, `mobile-domain`, `mobile-service`,
  `mobile-web` (четыре последних — только `type: mobile`),
  `capability-domain`, `integration-domain`, `surface-service`,
  `constraint-surface`, `market-capability`.
- **Один агент на проект**: `dataitems-crosssurface` — только при ≥2
  поверхностях с `data-items.md`.

## Что делать при запуске

1. Освежить каноны формы: `docs/business/README.md`, `docs/ajtbd/README.md`,
   `docs/swot/README.md`, `docs/hypothesis-map/README.md`,
   `docs/projects/README.md`, `docs/projects/_template/project/README.md`,
   `docs/projects/_template/project/{surface,capability,integration}.md`,
   `docs/projects/project-map.md`, `docs/projects/_template/interface/README.md`
   и те из `docs/projects/_template/{services,screens,telegram-bot-flow,mobile}/README.md`
   и `docs/projects/infrastructure/README.md`, что существуют.
2. Прочитать `references/angles.md` — карточки углов.
3. **Перечислить проекты:** подкаталоги `docs/projects/`, кроме
   `_template` (канон формы) и `infrastructure/` (периметр бизнеса);
   `project-map.md` — файл, не проект. С аргументом `<slug>` — один проект.
4. **Перечислить поверхности** каждого проекта по строкам `surface.md`
   (slug и `type`).
5. **Проверить, какие слои есть:** `services/` с доменами,
   `screens/<surface>/`, `telegram-bot-flow/<surface>/`, `mobile/<surface>/`,
   `docs/projects/infrastructure/` — каждый может отсутствовать независимо.
6. **Раскрыть углы** по скоупу (по аргументам или полным прогоном):
   верхнеуровневый — один агент; пара — агент на `(проект × lens)`; тройка —
   агент на `(проект × поверхность × lens)` для каждой поверхности проекта;
   `dataitems-crosssurface` — агент на проект. Единица, для которой нет
   нужного слоя или папки поверхности либо угол не подходит к `type`
   поверхности (условие «Применим если» в карточке), пропускается с
   пометкой в отчёте, почему именно; у других проектов и поверхностей тот же
   угол отрабатывает.
7. **Спавнить агентов** — все в одном сообщении, параллельно (см. «Рой
   агентов»). Рой = верхнеуровневые + Σ по проектам (пары + поверхности ×
   тройки + `dataitems-crosssurface`).
8. Собрать ответы: у каждого агента — массив findings по схеме
   `references/findings-format.md` с проектом и, для троек, поверхностью.
9. Сгруппировать findings по `(проект, поверхность, угол)`, внутри —
   по severity; верхнеуровневые — отдельной группой «общие слои».
10. Пройти с аналитиком top-K findings через `AskUserQuestion` (см.
    «Решения аналитика»).
11. Перезаписать `audit-state/last-report.md` reasoning-trace'ом и решениями.

Формат чат-отчёта, шаблоны `audit-state/last-report.md` и
`audit-state/suppressions.md` — `references/output-formats.md`; прочитай его
перед шагами 9–11.

## Рой агентов

Спавн — через `Agent`, `subagent_type: general-purpose`: агенту нужны
`Read` для файлов слоёв, `Grep` для быстрых проверок упоминаний и, если
угол требует внешнего контекста, `WebSearch` (например, проверить, что
constraint типа `regulation` действительно применим к нише).

Каждый агент получает:

- проект (`<project-slug>`) — для пар и троек; для верхнеуровневых —
  пометку «общие слои»;
- поверхность (`<surface>`) — только для троек;
- пути к двум сверяемым слоям с уже подставленными `<project-slug>` и
  `<surface>` (например, `docs/projects/<slug>/capability/<surface>.md` и
  `docs/projects/<slug>/interface/<surface>/situation.md`);
- свой угол и промпт-добавку из его карточки в `references/angles.md`;
- схему findings из `references/findings-format.md`;
- для углов business-problem ↔ продукт — список проблем, которые закрывает
  проект (`vision.addresses-problem`), чтобы сопоставление шло по ним, а не
  по всему реестру;
- релевантные его единице suppressions (см. «Suppressions»).

### Промпт-каркас для агента

```
Lens: <name>
Project: <project-slug>   (для верхнеуровневых углов — «общие слои»)
Surface: <surface>        (только для троек; иначе «—»)
Source layer: <path-1>    (<project-slug> и <surface> уже подставлены)
Destination layer: <path-2>
Проблемы проекта (для углов swot/hypothesis-map ↔ продукт): [<business-problem-slug>, ...]

Задача: семантически сопоставить записи source и destination и найти
тупики, противоречия и потери покрытия. Это не slug-валидация: соответствует
ли запись X записи Y, решаешь по смыслу. Держись границ проекта
<project-slug>; для троек — поверхности <surface>, для углов
business-problem ↔ продукт — перечисленных проблем. Запись чужой поверхности
проверяет агент той поверхности, поэтому её отсутствие здесь — не дыра.

Прочитай:
- <файлы source>
- <файлы destination>
- ветку state этих слоёв в дереве `../entrypoint/state/`, если она есть:
  для пар — `projects/<project-slug>/project/`, для троек —
  `projects/<project-slug>/{interface,screens,telegram-bot-flow,mobile}/<surface>/`.

Что искать:
<промпт-добавка угла из angles.md>

<suppressions для этой единицы — блок из findings-format.md, если есть>

Работаешь только на чтение: артефакты не правишь. Ответ — JSON-массив
findings по приложенной схеме, без текста вокруг: ответы всех агентов
сводятся в один отчёт. Пустой массив [] — нормальный результат, если слои
согласованы; находки ради количества не нужны.
```

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Семантический тупик, ломает целостность | user без покрытия в `interface/<surface>/who.md`; поверхность реестра без возможностей (пустой `capability/<surface>.md`); поверхность без зон; интеграция к соседнему проекту без ребра в `project-map.md`; `integration.sibling-project` на несуществующий проект; `vision.addresses-problem` на несуществующую проблему |
| `warning` | Подозрительная несостыковка | возможность поверхности «впритык» по ситуациям в её `interface/<surface>/`; возможность в `capability/<surface>.md`, чьи `user` не входят в `surface.user`; ребро `project-map` без опорной integration; constraint не привязан ни к поверхности, ни к её интеграции |
| `hint` | Гипотеза / возможная новая capability | market показывает gap — у поверхности нет возможности на эту территорию; ситуация поверхности без capability-якоря; один бизнес-датум под разными slug на разных поверхностях; проблема в `business-problem`, которую не закрывает ни один проект |

## Решения аналитика

После отчёта — `AskUserQuestion` по каждому top-K finding, до 4 в раунде:

- «Принять как корректное» — finding записывается в last-report как
  принятый; его можно подавить на следующих прогонах (см. «Suppressions»).
- «Действительно нужно править» — finding идёт в next-actions: скилл
  называет, что запустить (`/project-deep-dive`, `/interface-deep-dive` и
  т. п.), а запускает аналитик.
- «False positive» — записывается в suppressions, и на следующих прогонах
  эта находка не всплывает.
- «Обсудить позже» — остаётся в last-report без решения.

## `audit-state/`

Отчёт один на прогон (проекты внутри него), поэтому лежит рядом со
скиллом: `.claude/skills/cross-audit/audit-state/last-report.md`. Каждый
прогон перезаписывает его reasoning-trace'ом и решениями аналитика.

## Suppressions

Findings с решением «false positive» сохраняются в
`.claude/skills/cross-audit/audit-state/suppressions.md` (формат записи —
`references/output-formats.md`). Запись несёт `project` (для
верхнеуровневых углов — `—`) и `surface` (для пар и верхнеуровневых — `—`),
чтобы подавление в одной поверхности или проекте не глушило тот же паттерн
в другой. На следующем прогоне агент получает suppressions своей единицы
`(проект, поверхность, lens)` и не генерирует подпадающие под них
findings — решает по смыслу, не строковым совпадением. Удалённая вручную
запись снова даёт находке всплыть.

## Границы

- **Территория — кросс-слойные рёбра.** Структуру внутри слоя держат узкие
  аудиты: `/project-audit` (в т.ч. файл `capability/<surface>.md` без
  поверхности в реестре и поверхность без файла возможностей),
  `/interface-audit` и `/screen-audit` (папка поверхности вне реестра,
  циклы зон, битые внутрислойные slug), `/telegram-bot-flow-audit`,
  `/mobile-audit`, `/service-audit` (дубли, папки вне реестра, парность
  produces/consumes), `/infrastructure-audit` (битые рефы placement).
  Методологию внутри слоя держат `/swot-audit` и `/hypothesis-map-audit` (в
  пределах проблемы) и `/ajtbd-audit` (в пределах сегмента). Cross-audit
  смотрит семантику между слоями: для кого поверхность, что чем покрыто,
  сходятся ли стороны стыка.
- **Поверхностная изоляция.** Агент тройки сопоставляет только в пределах
  своей `<surface>`; кросс-поверхностные вопросы ведут отдельные углы
  (`dataitems-crosssurface`, `mobile-web` и обратные стороны
  `mechanic-`/`bet-`/`capability-*` с пометкой «может нести другая
  поверхность»).
- **Только отчёт.** Аудит не правит артефакты и не вызывает другие скиллы:
  в next-actions — текст, что запустить. Пустой ответ агента — «0 findings»
  по этому углу, а не повод искать ещё.
- **Один рой за сессию.** Если findings много — проходить их постепенно;
  повторный прогон — в следующей сессии или явным вызовом `/cross-audit`.
- **Инструмент аналитика.** В клиент-режиме (`entrypoint-for-business`)
  `/cross-audit` клиенту не предлагается.
