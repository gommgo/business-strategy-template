---
name: project-audit
description: "Узкий аудит консистентности продуктового слоя одного проекта в `docs/projects/<project-slug>/` (vision, реестр поверхностей surface, user, integration, boundary, constraint, market и `capability/<surface>.md`): структура — enum, дубли slug, обязательные слоты и blocker'ы у stable-записей, vision без addresses-problem, разрыв хребта surface ↔ capability, `integration.surface` и `sibling-project` в пустоту; семантические подозрения внутри проекта (capability или surface без user, boundary с backlog-обоснованием, constraint без source, market без источников) и coverage. Принимает `<project-slug>` первым аргументом; без него — пикер по проектам. Артефакты не правит, только отчёт; правки — через `/project-deep-dive`. Использовать перед коммитом артефактов проекта, когда `/project-deep-dive` предлагает прогон в конце сессии, перед `/cross-audit` или при подозрении на рассогласование внутри продуктового слоя. Сквозную проверку с другими слоями и привязку к проблемам бизнеса делает `/cross-audit`."
---

# project-audit

Аудит консистентности продуктового слоя **одного проекта** в
`docs/projects/<project-slug>/`:

- **1 singleton** `vision.md`.
- **реестр-хребет** `surface.md` — поверхности продукта; его slug'и —
  ключи партиционирования.
- **папка возможностей** `capability/` — по файлу на поверхность
  (`capability/<surface>.md`).
- **5 плоских кросс-поверхностных таблиц** `user.md`, `integration.md`,
  `boundary.md`, `constraint.md`, `market.md`.

Канон формы — `docs/projects/_template/project/README.md`. Поверхность
(`surface`) — единственная **структурная** ось: её slug = имя файла
`capability/<surface>.md`. Аудит **читает и сообщает**, ничего не правит:
каскадные правки идут через `/project-deep-dive <project-slug>`.

**Сквозную проверку** (продукт ↔ `<slug>/interface` ↔ `<slug>/services` ↔
`<slug>/screens`, продукт ↔ `addresses-problem`) делает `/cross-audit`.
Здесь — только внутрипроектная, в пределах одной папки проекта.

## Мультипроект: выбор проекта

Аудит **скоупится в один проект**. Первый позиционный аргумент —
`<project-slug>`. Без него скилл строит пикер через `AskUserQuestion` **по
именам** проектов (подкаталоги `docs/projects/`, исключая `_template` — это
образец формы, не проект; текст опции — имя из `vision`, slug — деталь).
Один прогон = один проект.

## Точки входа

| вызов | поведение |
|---|---|
| `/project-audit` | пикер проекта → полный прогон всех файлов выбранного |
| `/project-audit <project-slug>` | полный прогон всех файлов проекта |
| `/project-audit <project-slug> <kind>` | прогон одного kind + ссылающихся соседей |
| `/project-audit <project-slug> capability` | прогон **всех** файлов `capability/*.md` + соседей |
| `/project-audit <project-slug> capability:<surface>` | один файл `capability/<surface>.md` |
| `/project-audit <project-slug> <kind>:<slug>` | одна запись + 1-shell соседи |

`kind` ∈ {`vision`, `surface`, `capability`, `user`, `integration`,
`boundary`, `constraint`, `market`}.

`capability` — **папка**: один файл на поверхность (`capability/<surface>.md`).
Без уточнения `capability` берёт все файлы `capability/*.md`;
`capability:<surface>` сужает до файла одной поверхности (`<surface>` —
slug поверхности из реестра `surface.md`). `capability:<slug>` (где `<slug>`
— это slug записи внутри файла) тоже допустим — скилл находит файл, в
котором лежит запись.

Если первый аргумент совпал с папкой в `docs/projects/` (кроме
`_template`) — это `<project-slug>`. Иначе — пикер.

## Что делать при запуске

1. **Определить проект.** Разобрать первый аргумент как `<project-slug>`;
   если не задан или не совпал с папкой — пикер по именам проектов
   (исключая `_template`). Зафиксировать `<project-slug>` на прогон.
2. Прочитать `docs/projects/_template/project/README.md` — освежить канон
   формы.
3. Прочитать `references/rules.md` — реестр проверок с severity.
4. Прочитать все файлы проекта `docs/projects/<project-slug>/` (или
   подмножество по args):
   - корневые: `vision.md`, `surface.md`, `user.md`, `integration.md`,
     `boundary.md`, `constraint.md`, `market.md`;
   - папка возможностей: **все** файлы `capability/*.md` (по одному на
     поверхность). Перечисляй их листингом каталога `capability/`, не
     угадывай имена — имя каждого файла должно быть slug'ом поверхности из
     реестра `surface.md` (это проверяет R-STRUCT-007).
5. Прочитать ветку state проекта в едином дереве оркестратора
   (`../entrypoint/state/projects/<project-slug>/project/`) — для
   проверок типа «stable с blocker-вопросами».
6. Прогнать правила по очереди. Собрать findings.
7. Сгруппировать по сущности, отсортировать по severity внутри.
8. Вывести отчёт в чат.
9. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | Дубликат `slug`; невалидное enum-значение; пустой обязательный слот в `stable`; vision без Problem или Success; stable со `**blocker**` в state; файл `capability/<surface>.md` для поверхности вне реестра `surface.md`; `integration.surface` на несуществующую поверхность; `integration.sibling-project` на несуществующий проект; функция `## Функции` на несуществующего провайдера |
| `warning` | Семантическое подозрение | capability без user в массиве; surface без user; boundary с backlog-обоснованием в `why` («нет ресурсов»); constraint без `source`; market без `url`/`sources`; integration с `direction` но без `owner`; `integration.sibling-project` указан на сам текущий проект |
| `hint` | Coverage / стиль, не ломает | user без жителей в capability/surface; поверхность реестра без файла `capability/<surface>.md`; vision stable при пустой user-таблице; stable со ссылкой на draft; очень короткое `description` |

Подробный реестр — `references/rules.md`.

## Формат отчёта

В чат:

```
=== /project-audit <project-slug> ===
Проект: <project-slug>
Прочитано: 7 корневых + M файлов capability/ (поверхностей), N записей.

[error] vision → раздел Success пустой. status: stable.
  Что делать: дописать Success или понизить до draft через
  /project-deep-dive <project-slug>.

[error] capability/web-partner.md:send-referral → status: stable, но `user = —`.
  Что делать: связать с user через
  /project-deep-dive <project-slug> capability:send-referral.

[error] capability/tg-bot.md — поверхность `tg-bot` отсутствует в реестре
  surface.md. Файл возможностей висит без хребта.
  Что делать: завести поверхность в surface.md или удалить файл через
  /project-deep-dive <project-slug>.

[warning] boundary:no-mobile → why = «не делаем мобильное приложение, нет ресурсов».
  Похоже на backlog в маскировке (anti-pattern из boundary.md).
  Что делать: пересмотреть формулировку через
  /project-deep-dive <project-slug> boundary:no-mobile.

[hint] user:doctor → ни одна capability и ни одна surface не
  ссылается на этого пользователя.
  Что делать: либо подключить к capability/surface, либо рассмотреть
  удаление через /project-deep-dive <project-slug>.

Сводка: 2 error / 1 warning / 1 hint.
```

Группировка — по сущности; внутри — `error → warning → hint`.

## `audit-state/<project-slug>/last-report.md`

Отчёт лежит **рядом со скиллом**, скоупится по проекту:

```
.claude/skills/project-audit/audit-state/<project-slug>/last-report.md
```

После каждого прогона перезаписывается одним файлом с reasoning-trace:
какие правила запускал, какие записи проверил, что нашёл, почему. Это
не журнал — следующий прогон по этому проекту перезатирает. Отчёты разных
проектов не сталкиваются. В git, чтобы команда могла читать.

Структура:

```markdown
---
project: <project-slug>
ran-on: <scope: all | kind | kind:slug | capability:<surface>>
files-read: <7 корневых + M файлов capability/>
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила структуры (R-STRUCT-*)
- R-STRUCT-001 «дубликаты slug»: ...
- R-STRUCT-002 «обязательные слоты в stable»: ...
...

## Правила семантики (R-SEM-*)
- ...

## Правила coverage (R-COV-*)
- ...
```

## Границы

- **Только отчёт.** Артефакты правит `/project-deep-dive <project-slug>`,
  и запускает его аналитик по выводу аудита. `stable → draft` аудит не
  понижает: сообщает error «обязательный слот пустой при stable», понижает
  аналитик.
- **Один проект за прогон.** `_template/` — образец формы, не данные
  проекта; чужой проект — отдельный прогон.
- **Finding — только по сработавшему правилу** из `references/rules.md`;
  «возможно, тут что-то не так» без правила в отчёт не идёт.
- **Кросс-слойные проверки** (продукт ↔ `<slug>/interface` /
  `<slug>/services` / `<slug>/screens`, продукт ↔ `addresses-problem`) —
  территория `/cross-audit`.
- **Без suppressions.** Правила проверяют форму записей — слот пустой или
  нет, ссылка существует или нет, маркер в тексте есть или нет, — поэтому
  находка повторяется, пока запись не поправлена. Эвристику R-SEM, которая
  не подходит к случаю, аналитик разбирает по отчёту.
- **Инструмент аналитика.** В клиент-режиме (`entrypoint-for-business`)
  `/project-audit` клиенту не предлагается.
