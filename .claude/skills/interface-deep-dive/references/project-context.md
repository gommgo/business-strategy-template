# Контекст продуктового слоя проекта

Скилл `interface-deep-dive` живёт **на слой ниже** продуктового слоя
**того же проекта** и работает **в контексте одной поверхности (surface)**.
Продуктовый слой описывает **продукт** (vision + реестр-хребет
поверхностей `surface.md` + кросс-поверхностные kind + возможности по
поверхности `capability/<surface>.md`) и живёт в
`docs/projects/<project-slug>/`; interface — **UX-аналитику** одной
поверхности (who/situation/zone/block) в
`docs/projects/<project-slug>/interface/<surface>/`. Семантическая связь
между слоями есть, но **slug-валидаций нет** — её ловит `/cross-audit`.

Связь зоны/ситуации с поверхностью теперь **структурная**: сущность лежит
в папке своей поверхности (`interface/<surface>/`). Поверхность уже задана
выбором папки на старте — отдельно её **не спрашивать**.

Когда заводишь ключевую сущность в interface, проверь продуктовый файл
того же проекта и предложи аналитику **связь** как контекст, не как
обязательную ссылку.

## Маппинг

| interface | сосед | поле / как использовать |
|---|---|---|
| `who` (роль) | `user` (адресат продукта, **корневой** `user.md` проекта, кросс-поверхностный) | авторское поле `who.users` (опц., массив). При заведении `who` через `AskUserQuestion` предложи опции = существующие user из корневого `docs/projects/<project-slug>/user.md`; «системный актор» → `—`. Результат пишется **в колонку `users`** записи who; «почему» — опц. в `state/<project-slug>/interface/<surface>/who/<slug>.md` |
| `situation` (UX-ситуация) | `capability` (что продукт умеет **на этой поверхности**) | авторское поле `situation.capabilities` (опц., массив). Опции = существующие capability **той же поверхности** из `docs/projects/<project-slug>/capability/<surface>.md`; системное действие → `—` |
| `situation` (UX-ситуация) | `job` (`docs/ajtbd/job`, глобальный) | авторское поле `situation.jobs` (опц.). Какие работы сегмента обслуживает шаг |
| `situation` (UX-ситуация) | `hypothesis` (`docs/hypothesis-map/hypothesis`, глоб.) | авторское поле `situation.hypotheses` (опц.). Какие гипотезы проверяет/обслуживает шаг |
| `zone` (зона интерфейса) | `surface` (поверхность папки) | связь **структурная** — зона лежит в `interface/<surface>/`, отдельным вопросом surface не задаётся |

Пользователь (`user`) берётся из **корневого** `user.md` проекта
(`docs/projects/<project-slug>/user.md`) — он кросс-поверхностный;
возможность (`capability`) — из файла **той же поверхности**
`docs/projects/<project-slug>/capability/<surface>.md`; `job` и
`hypothesis` — из **глобальных** слоёв `docs/ajtbd/` и
`docs/hypothesis-map/`. Все рёбра — **семантические** (slug-валидаций нет),
ловит `/cross-audit`.

## Когда показывать связь

### Заведение `who`

В режиме A (новая сущность):

1. После раунда фундамента (slug/name/description) — раунд связи. Опции —
   user из **корневого** `docs/projects/<project-slug>/user.md`
   (кросс-поверхностный):

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
   опционально в `state/<project-slug>/interface/<surface>/who/<slug>.md`
   секцию `## Доменные решения`.

3. Если выбран «Системный актор» — `users = —`; в state записать
   «Намеренно без user — системный интерес X».

4. Если выбран Other — записать ответ аналитика дословно в state.

### Заведение `situation`

В режиме A, после фундамента — раунды связи (сквозные рёбра, все опц.,
multiSelect, прочерк допустим). Возможности берутся **только из файла той
же поверхности** `capability/<surface>.md`:

```
AskUserQuestion (header: "Связь с capability") → колонка situation.capabilities
options: capability:<slug-i> из docs/projects/<project-slug>/capability/<surface>.md / «Системное действие (без capability)» / Other

AskUserQuestion (header: "Работа сегмента") → колонка situation.jobs
options: job:<slug-i> из docs/ajtbd/job.md / «нет» / Other

AskUserQuestion (header: "Гипотеза") → колонка situation.hypotheses
options: hypothesis:<slug-i> из docs/hypothesis-map/hypothesis.md / «нет» / Other
```

Результат пишется **в соответствующие колонки** записи situation; «почему»
— опц. в `state/<project-slug>/interface/<surface>/situation/<slug>.md`.

### Заведение `zone`

Связь зоны с поверхностью **структурная** — зона лежит в папке своей
поверхности `interface/<surface>/`, поверхность уже задана выбором папки
на старте сессии. **Отдельного раунда про surface нет** — не спрашивать,
какой поверхности принадлежит зона. Раунд связи у zone сводится к
`parent-zone` (родительская зона **той же поверхности**), см.
`field-checklists.md`.

## Что делать, если продуктовый слой проекта пуст

Если у проекта нет нужного источника (корневой `user.md` пуст / нет файла
возможностей `capability/<surface>.md` поверхности / нет ни одной записи
нужного kind) — раунд связи **не задаётся**. Скилл продолжает обычный
flow.

При закрытии сессии — `AskUserQuestion`:

> «Заметил, что у проекта `<project-slug>` нет соответствующих
> продуктовых записей. Это ОК для прототипа, но обычно interface
> растёт из продукта. Открыть `/project-deep-dive <project-slug>`?»

Опции: «Да, запустим» / «Нет, продолжим без продукта».

## Что делать, если уже есть запись в state с другой user

Если `who:doctor` в
`state/<project-slug>/interface/<surface>/who/doctor.md` уже привязан
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
