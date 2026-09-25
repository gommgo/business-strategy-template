---
name: interface-audit
description: "Аудит консистентности интерфейса проекта в `docs/projects/<project-slug>/interface/<surface>/` (who · stage · situation · zone · block · ux-substrate · data-items) — по папке на поверхность из реестра `surface.md`. Ловит битые slug-рефы и циклы `parent-zone`, рассинхрон зеркал ситуации, тупики навигации, пустые обязательные слоты в stable, семантические подозрения (goal как предусловие, облик в using-what), coverage-дыры и выход ссылки за границу поверхности. Только отчёт; правки — через `interface-deep-dive`. Использовать перед коммитом артефактов interface, по предложению `interface-deep-dive` в конце сессии или при подозрении на рассогласование между файлами. Аргументы: `<project-slug>` (без него — пикер по проектам), опционально `<surface>` (без неё — все поверхности), узкий scope — `<kind>` или `<kind>:<slug>`."
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

- **Только отчёт.** Артефакты правит `interface-deep-dive`; аудит его не
  запускает — это делает аналитик по выводу аудита.
- **Не понижать `stable → draft`.** Максимум — hint «возможно,
  понизить?» в отчёте.
- **Не выдумывать findings.** Если правило не сработало — не писать
  «возможно, тут что-то не так на всякий случай».
- **Без suppressions.** Структурные правила детерминированы — зеркало
  синхронно или нет, ссылка существует или нет. Подозрения R-SEM
  аналитик может объяснить в диалоге, и ответ снимает их в этом прогоне,
  но отчёт их не подавляет: следующий прогон вправе сработать снова (в
  отличие от `/cross-audit`, `/swot-audit` и `/hypothesis-map-audit`,
  которые ведут suppressions).
- **Один проект; каждая поверхность — в своих границах.** Межпроектные
  несостыковки — предмет `/cross-audit`. Ссылка из папки поверхности
  наружу — error (R-XSURF-001); правило «один датум, один slug» действует
  в пределах поверхности, а один датум на web и в боте сверяет
  `/cross-audit`.
