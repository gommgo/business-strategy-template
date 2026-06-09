---
name: interface-audit
description: "Аудит консистентности аналитических артефактов интерфейса проекта в `docs/projects/<project-slug>/interface/<surface>/` — по папке на поверхность из реестра `surface.md`. Невалидные ссылки на slug (в пределах одной поверхности), циклы parent-zone, рассинхрон зеркал ситуации, тупики (зона без блоков, блок без субстратов или участников), пустые обязательные слоты в stable-записях, семантические подозрения (goal как предусловие, using-what с обликом), coverage-дыры (who/stage без покрытия ситуациями), папка поверхности вне реестра, ссылка из одной поверхности в другую. Не правит артефакты, только указывает; деструктивные правки — через `interface-deep-dive`. Использовать перед коммитом артефактов, когда `interface-deep-dive` предлагает прогон в конце сессии, или когда аналитик подозревает рассогласование между файлами. Принимает `<project-slug>` первым аргументом; без него — пикер по проектам. Без `<surface>` — прогон по всем папкам поверхностей; с `<surface>` — одна поверхность. Полный прогон по 7 файлам — без kind-аргумента; узкий — `<kind>` или `<kind>:<slug>`."
---

# interface-audit

Аудит консистентности 7 артефактных файлов интерфейса **одной
поверхности** проекта в `docs/projects/<project-slug>/interface/<surface>/`.
Канон формы — `docs/projects/_template/interface/README.md`. Аудит
**читает и сообщает**, ничего не правит: каскадные правки идут через
`interface-deep-dive`.

UX-слой **партиционируется по поверхности (surface)**: на каждую
поверхность из реестра `docs/projects/<project-slug>/surface.md` — своя
папка `interface/<surface>/` с 7 файлами. Все ссылочные проверки идут
**в пределах одной поверхности**: who/stage/situation/zone/block/
ux-substrate/data-items одной папки ссылаются только друг на друга.
Аудит итерирует **по каждой папке поверхности** независимо.

Аудит работает **в контексте одного проекта** (см. «Выбор проекта и
поверхности»). Дальше по тексту `<project-slug>` — выбранный проект,
`<surface>` — поверхность (одна или все).

## Выбор проекта и поверхности

Аргументы позиционны — `<project-slug>` первый, `<surface>` второй
(опционален):

| вызов | проект · поверхность |
|---|---|
| `/interface-audit <project-slug> <surface> …` | взять `<project-slug>` и `<surface>` |
| `/interface-audit <project-slug> …` (без surface) | проект задан; **все** папки поверхностей проекта |
| `/interface-audit …` (без slug) | `AskUserQuestion`-пикер **по именам** проектов (исключая `_template`); затем все поверхности |

1. Если первый аргумент совпадает с именем подпапки `docs/projects/`
   (кроме `_template`) — это `<project-slug>`. Иначе — пикер **по
   именам** проектов (исключить `_template`). Если проектов нет —
   сказать «нечего аудитить», выйти.
2. Прочитать реестр `docs/projects/<project-slug>/surface.md`. Если
   следующий аргумент совпадает со `slug` строки реестра — это
   `<surface>` (одна поверхность), остаток args — scope. Если аргумента
   нет — поверхностей **все**: аудит проходит по каждой папке
   `interface/<surface>/` отдельно, отчёт группируется по поверхности.
3. Все чтения скоупятся в `docs/projects/<project-slug>/interface/<surface>/`
   (одну или каждую) и `audit-state/<project-slug>/`.

## Точки входа

После того как `<project-slug>` и (опц.) `<surface>` определены, остаток
args задаёт scope:

| вызов | поведение |
|---|---|
| `/interface-audit <project-slug>` | полный прогон всех 7 файлов в каждой папке поверхности |
| `/interface-audit <project-slug> <surface>` | полный прогон всех 7 файлов одной поверхности |
| `/interface-audit <project-slug> <surface> <kind>` | прогон одного файла поверхности + перекрёстные ссылки внутри неё |
| `/interface-audit <project-slug> <surface> <kind>:<slug>` | одна запись + 1-shell соседи по ссылкам внутри поверхности |

`kind` ∈ {`who`, `stage`, `situation`, `zone`, `block`, `ux-substrate`, `data-items`}.
`<kind>` и `<kind>:<slug>` требуют заданной `<surface>` (kind живёт в
конкретной поверхности).

## Что делать при запуске

1. Определить `<project-slug>` и (опц.) `<surface>` (см. «Выбор проекта
   и поверхности»).
2. Прочитать `docs/projects/_template/interface/README.md` — освежить
   канон формы.
3. Прочитать `references/rules.md` — реестр проверок с тяжестью.
4. Прочитать реестр `docs/projects/<project-slug>/surface.md` —
   перечень поверхностей. Сверить с подпапками
   `docs/projects/<project-slug>/interface/`: папка вне реестра — error
   (R-SURF-001), поверхность реестра без папки — hint (R-SURF-002).
5. Для каждой папки поверхности из scope (одна заданная `<surface>` или
   все) прочитать её 7 файлов
   `docs/projects/<project-slug>/interface/<surface>/` (или подмножество
   по args). Прогнать правила **в пределах этой поверхности**, собрать
   findings.
6. Сгруппировать по поверхности, внутри — по сущности; отсортировать по
   severity внутри.
7. Вывести отчёт в чат.
8. Перезаписать `audit-state/<project-slug>/last-report.md` с
   reasoning-trace.

## Уровни тяжести

| severity | смысл | пример |
|---|---|---|
| `error` | Структурное нарушение, ломает модель | Невалидная ссылка; цикл `parent-zone`; дубликат `slug` в одном файле; рассинхрон зеркал; `block` без `ux-substrates` или без `who`; явный `transition-to-block` внутри одной зоны; папка поверхности вне реестра `surface.md`; ссылка из папки одной поверхности в сущность другой |
| `warning` | Семантическое подозрение, рискует смыслом | Пустой обязательный слот; `goal` похож на предусловие; `using-what` содержит облик; `block` без хотя бы одного входа; `description` совпадает с `name` |
| `hint` | Coverage / стиль, не ломает | Stable со ссылкой на draft; `who` или `stage` без покрытия ситуациями; `zone` без блоков; очень короткое `description`; поверхность реестра без папки interface |

Подробный реестр — `references/rules.md`.

## Формат отчёта

В чат:

```
=== /interface-audit <project-slug> ===
Поверхностей в scope: K (web-clinic, tg-bot). Прочитано: 7 файлов × K, N записей.

[error] web-clinic / папка интерфейса не имеет поверхности в реестре surface.md.
  Что делать: завести строку в surface.md через /project-deep-dive <project-slug>,
  либо удалить папку interface/<surface>/.

[error] web-clinic / situation:submit-referral → невалидная ссылка situation.who = `doctor` (нет в who.md этой поверхности).
  Что делать: завести `doctor` через /interface-deep-dive <project-slug> web-clinic who, или
  заменить на существующий who-slug этой поверхности.

[error] web-clinic / zone:study-card → цикл parent-zone: study-card → studies → study-card.
  Что делать: пересмотреть иерархию через /interface-deep-dive <project-slug> web-clinic zone:study-card.

[warning] web-clinic / situation:submit-referral → goal «авторизуется, чтобы продолжить работу»
  похож на предусловие следующего шага (anti-pattern из situation.md).
  Что делать: уточнить «зачем именно так» в /interface-deep-dive <project-slug> web-clinic situation:submit-referral.

[hint] tg-bot / who:doctor → нет ни одной ситуации с who = doctor.
  Что делать: либо завести ситуацию-инициатор, либо удалить who:doctor
  через /interface-deep-dive <project-slug> tg-bot (каскадно).

Сводка: 3 error / 1 warning / 1 hint.
```

Группировка — по поверхности, внутри — по сущности; в пределах сущности
— `error → warning → hint`.

## `audit-state/<project-slug>/last-report.md`

Отчёт лежит **рядом со скиллом**, не в
`docs/projects/<project-slug>/interface/` и не в корне проекта, и
скоупится по проекту:

```
.claude/skills/interface-audit/audit-state/<project-slug>/last-report.md
```

Дальше по тексту скилла — короткое `audit-state/`, это сокращение
того же пути (с учётом текущего `<project-slug>`).

После каждого прогона перезаписывается одним файлом с reasoning-trace:
какие правила запускал, какие записи проверил, что нашёл, почему. Это
не журнал — следующий прогон перезатирает. В git, чтобы команда могла
читать.

Структура:

```markdown
---
project: <project-slug>
ran-on: <scope: all-surfaces | surface | surface kind | surface kind:slug>
surfaces: [<surface-1>, <surface-2>]
files-read: 7 × surfaces
records-checked: N
totals: { error: X, warning: Y, hint: Z }
---

# Reasoning trace

## Правила хребта (R-SURF-*)
- R-SURF-001 «папка поверхности вне реестра»: сверил подпапки interface/
  с surface.md — нашёл K лишних.
- R-SURF-002 «поверхность реестра без папки interface»: ...

## Поверхность <surface-1>

### Правила структуры (R-STRUCT-*)
- R-STRUCT-001 «валидность ссылок»: проверил M ссылок, нашёл K битых.
  - situation:submit-referral.who = `doctor` → нет в who.md → error.
- R-STRUCT-002 «цикл parent-zone»: ...
...

### Правила зеркал (R-MIRROR-*)
- ...

### Правила семантики (R-SEM-*)
- ...

### Правила coverage (R-COV-*)
- ...

## Поверхность <surface-2>
- ...
```

## Что не делать

- **Не править артефакты.** Аудит — только отчёт. Все правки — через
  `interface-deep-dive`.
- **Не понижать `stable → draft`.** Максимум — hint «возможно,
  понизить?» в отчёте.
- **Не выдумывать findings.** Если правило не сработало — не писать
  «возможно, тут что-то не так на всякий случай».
- **Не аккумулировать историю** в `audit-state/`. Перезаписывать
  `last-report.md` каждый прогон.
- **Не реализовывать suppressions.** В отличие от `/cross-audit`,
  `/swot-audit` и `/hypothesis-map-audit` (семантические findings, бывают
  ложные), структурный аудит детерминирован — зеркало синхронно или нет,
  ссылка существует или нет. Ложных срабатываний не бывает, подавлять
  нечего.
- **Не смешивать проекты.** Аудит скоупится в один `<project-slug>`;
  межпроектные несостыковки — предмет `/cross-audit`, не этот скилл.
- **Не смешивать поверхности.** Каждая папка `interface/<surface>/`
  аудитится в своих границах: все ссылки разрешаются только внутри той же
  поверхности, ссылка наружу — error (R-XSURF-001). Кросс-поверхностную
  сверку «один датум на web и в боте — это один датум» делает
  `/cross-audit`, не этот скилл: правило «один датум, один slug» здесь
  действует **в пределах поверхности**, дубль датума между поверхностями
  — не предмет interface-audit.
- **Не запускать `interface-deep-dive`** автоматически из аудита. Это
  делает аналитик руками по выводу аудита.
