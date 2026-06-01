# Контекст project-слоя

Скилл `interface-deep-dive` живёт **на слой ниже** `docs/project/`.
Project-слой описывает **продукт** (vision/persona/capability/surface),
interface — **UX-аналитику** (who/situation/zone/block). Семантическая
связь между ними есть, но **slug-валидаций нет** — её ловит
`/cross-audit`.

Когда заводишь ключевую сущность в interface, проверь
`docs/project/<src>.md` и предложи аналитику **связь** как контекст,
не как обязательную ссылку.

## Маппинг

| interface | project | как использовать |
|---|---|---|
| `who` (роль) | `persona` (сегмент адресатов продукта) | при заведении нового `who` через `AskUserQuestion` предложи опции = существующие persona; «нужен новый» (Other) — если ни одна не подходит. Записывается не в frontmatter, а опционально в `state/who/<slug>.md` как «семантически принадлежит persona:X» |
| `situation` (UX-ситуация) | `capability` (что продукт умеет) | при заведении situation предложи опции = существующие capability; для системных ситуаций — `—` |
| `zone` (зона интерфейса) | `surface` (где продукт работает) | при заведении zone предложи опции = существующие surface; zone обязан семантически принадлежать какой-то surface |

## Когда показывать связь

### Заведение `who`

В режиме A (новая сущность):

1. После раунда фундамента (slug/name/description) — раунд связи:

   ```
   AskUserQuestion:
   header: "Связь с persona"
   options:
     - "persona:<slug-1>" (description = name)
     - "persona:<slug-2>" (description = name)
     - "Системный актор (без persona)"
     - Other (через текст: «не одна из перечисленных, опишу»)
   ```

2. По выбору — записать в `state/who/<slug>.md` секцию `## Доменные
   решения`:

   ```markdown
   - Семантически принадлежит persona:<persona-slug>.
   ```

3. Если выбран «Системный актор» — записать «Намеренно без persona —
   системный интерес X (см. README канона who)».

4. Если выбран Other — записать ответ аналитика дословно.

**НЕ записывать** в frontmatter записи who.md как slug-ссылку — это
семантика, не структура.

### Заведение `situation`

В режиме A, после фундамента — раунд связи:

```
AskUserQuestion:
header: "Связь с capability"
options:
  - "capability:<slug-1>"
  - "capability:<slug-2>"
  - "Системное действие (без capability)"
  - Other
```

Запись — в `state/situation/<slug>.md`.

### Заведение `zone`

В режиме A — раунд связи:

```
AskUserQuestion:
header: "Какой surface принадлежит"
options:
  - "surface:<slug-1>" (type)
  - "surface:<slug-2>" (type)
  - Other
```

Запись — в `state/zone/<slug>.md`. **Каждая zone должна иметь surface**
(в отличие от who и situation, где допустимо «системное»).

## Что делать, если project-слой пуст

Если `docs/project/` не существует, или соответствующий файл пуст,
или нет ни одной записи нужного kind — раунд связи **не задаётся**.
Скилл продолжает обычный flow.

При закрытии сессии — `AskUserQuestion`:

> «Заметил, что в `docs/project/` нет соответствующих записей. Это
> ОК для прототипа, но обычно interface растёт из project. Открыть
> `/project-deep-dive`?»

Опции: «Да, запустим» / «Нет, продолжим без project».

## Что делать, если уже есть запись в state с другой persona

Если `who:doctor` в `state/who/doctor.md` уже привязан семантически к
`persona:doctor-clinic-owner`, а в новой сессии аналитик хочет связать
с `persona:doctor-employee` — это **смена контекста**. Скилл:

1. Не молча перезаписывает.
2. `AskUserQuestion`: «Уже было связано с persona:X. Меняем на
   persona:Y или who относится к обеим?»
3. По выбору — обновить state.

## Cross-audit

После каждой сессии скилл предлагает `/cross-audit --quick` (lens
`persona-who`) — это поможет аналитику увидеть, не остались ли
who без persona или persona без who.

Скилл **сам** не запускает `/cross-audit` — это работа аналитика.
