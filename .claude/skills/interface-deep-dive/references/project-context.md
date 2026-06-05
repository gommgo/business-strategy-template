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

| interface | сосед | поле / как использовать |
|---|---|---|
| `who` (роль) | `user` (адресат продукта, тот же проект) | авторское поле `who.users` (опц., массив). При заведении `who` через `AskUserQuestion` предложи опции = существующие user проекта; «системный актор» → `—`. Результат пишется **в колонку `users`** записи who; «почему» — опц. в `state/<project-slug>/who/<slug>.md` |
| `situation` (UX-ситуация) | `capability` (что продукт умеет, тот же проект) | авторское поле `situation.capabilities` (опц., массив). Опции = существующие capability проекта; системное действие → `—` |
| `situation` (UX-ситуация) | `job` (`docs/ajtbd/job`, глобальный) | авторское поле `situation.jobs` (опц.). Какие работы сегмента обслуживает шаг |
| `situation` (UX-ситуация) | `hypothesis` (`docs/hypothesis-map/hypothesis`, глоб.) | авторское поле `situation.hypotheses` (опц.). Какие гипотезы проверяет/обслуживает шаг |
| `zone` (зона интерфейса) | `surface` (где продукт работает, тот же проект) | при заведении zone предложи опции = существующие surface проекта; zone обязан семантически принадлежать какой-то surface (хранится в `state`, не в колонке) |

Продуктовые сущности (`user`, `capability`, `surface`) берутся из **того
же проекта** (`docs/projects/<project-slug>/`); `job` и `hypothesis` — из
**глобальных** слоёв `docs/ajtbd/` и `docs/hypothesis-map/`. Все рёбра —
**семантические** (slug-валидаций нет), ловит `/cross-audit`.

## Когда показывать связь

### Заведение `who`

В режиме A (новая сущность):

1. После раунда фундамента (slug/name/description) — раунд связи:

   ```
   AskUserQuestion:
   header: "Связь с user"
   multiSelect: true
   options:
     - "user:<slug-1>" (description = name)
     - "user:<slug-2>" (description = name)
     - "Системный актор (без user)"
     - Other (через текст: «не одна из перечисленных, опишу»)
   ```

2. По выбору — записать slug(и) **в колонку `users`** записи who
   (питон-стиль массив, или `—` для системного актора). «Почему» —
   опционально в `state/<project-slug>/who/<slug>.md` секцию
   `## Доменные решения`.

3. Если выбран «Системный актор» — `users = —`; в state записать
   «Намеренно без user — системный интерес X».

4. Если выбран Other — записать ответ аналитика дословно в state.

### Заведение `situation`

В режиме A, после фундамента — раунды связи (сквозные рёбра, все опц.,
multiSelect, прочерк допустим):

```
AskUserQuestion (header: "Связь с capability") → колонка situation.capabilities
options: capability:<slug-i> того же проекта / «Системное действие (без capability)» / Other

AskUserQuestion (header: "Работа сегмента") → колонка situation.jobs
options: job:<slug-i> из docs/ajtbd/job.md / «нет» / Other

AskUserQuestion (header: "Гипотеза") → колонка situation.hypotheses
options: hypothesis:<slug-i> из docs/hypothesis-map/hypothesis.md / «нет» / Other
```

Результат пишется **в соответствующие колонки** записи situation; «почему»
— опц. в `state/<project-slug>/situation/<slug>.md`.

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
