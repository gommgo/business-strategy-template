# Контекст продуктового слоя проекта

Скилл `interface-deep-dive` живёт **на слой ниже** продуктового слоя
**того же проекта**. Продуктовый слой описывает **продукт**
(vision/user/capability/surface) и живёт в
`docs/projects/<project-slug>/` (vision + 7 файлов); interface —
**UX-аналитику** того же проекта (who/situation/zone/block) в
`docs/projects/<project-slug>/interface/`. Семантическая связь между
ними есть, но **slug-валидаций нет** — её ловит `/cross-audit`.

Когда заводишь ключевую сущность в interface, проверь продуктовый файл
того же проекта (`docs/projects/<project-slug>/<src>.md`) и предложи
аналитику **связь** как контекст, не как обязательную ссылку.

## Маппинг

| interface | продукт (`docs/projects/<project-slug>/`) | как использовать |
|---|---|---|
| `who` (роль) | `user` (сегмент адресатов продукта) | при заведении нового `who` через `AskUserQuestion` предложи опции = существующие user проекта; «нужен новый» (Other) — если ни одна не подходит. Записывается не в frontmatter, а опционально в `state/<project-slug>/who/<slug>.md` как «семантически принадлежит user:X» |
| `situation` (UX-ситуация) | `capability` (что продукт умеет) | при заведении situation предложи опции = существующие capability проекта; для системных ситуаций — `—` |
| `zone` (зона интерфейса) | `surface` (где продукт работает) | при заведении zone предложи опции = существующие surface проекта; zone обязан семантически принадлежать какой-то surface |

Все продуктовые сущности берутся из **того же проекта**
(`docs/projects/<project-slug>/user.md`, `…/capability.md`,
`…/surface.md`), не из глобального слоя.

## Когда показывать связь

### Заведение `who`

В режиме A (новая сущность):

1. После раунда фундамента (slug/name/description) — раунд связи:

   ```
   AskUserQuestion:
   header: "Связь с user"
   options:
     - "user:<slug-1>" (description = name)
     - "user:<slug-2>" (description = name)
     - "Системный актор (без user)"
     - Other (через текст: «не одна из перечисленных, опишу»)
   ```

2. По выбору — записать в `state/<project-slug>/who/<slug>.md` секцию
   `## Доменные решения`:

   ```markdown
   - Семантически принадлежит user:<user-slug>.
   ```

3. Если выбран «Системный актор» — записать «Намеренно без user —
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

Запись — в `state/<project-slug>/situation/<slug>.md`.

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

Запись — в `state/<project-slug>/zone/<slug>.md`. **Каждая zone должна
иметь surface** (в отличие от who и situation, где допустимо
«системное»).

## Что делать, если продуктовый слой проекта пуст

Если у проекта `docs/projects/<project-slug>/` нет нужного файла, или
он пуст, или нет ни одной записи нужного kind — раунд связи **не
задаётся**. Скилл продолжает обычный flow.

При закрытии сессии — `AskUserQuestion`:

> «Заметил, что у проекта `<project-slug>` нет соответствующих
> продуктовых записей. Это ОК для прототипа, но обычно interface
> растёт из продукта. Открыть `/project-deep-dive <project-slug>`?»

Опции: «Да, запустим» / «Нет, продолжим без продукта».

## Что делать, если уже есть запись в state с другой user

Если `who:doctor` в `state/<project-slug>/who/doctor.md` уже привязан
семантически к `user:doctor-clinic-owner`, а в новой сессии аналитик
хочет связать с `user:doctor-employee` — это **смена контекста**.
Скилл:

1. Не молча перезаписывает.
2. `AskUserQuestion`: «Уже было связано с user:X. Меняем на
   user:Y или who относится к обеим?»
3. По выбору — обновить state.

## Cross-audit

После каждой сессии скилл предлагает `/cross-audit --quick` (lens
`user-who`) — это поможет аналитику увидеть, не остались ли
who без user или user без who **в этом проекте**.

Скилл **сам** не запускает `/cross-audit` — это работа аналитика.
