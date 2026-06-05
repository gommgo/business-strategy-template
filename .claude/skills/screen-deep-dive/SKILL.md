---
name: screen-deep-dive
description: Углублённая проработка аналитических артефактов экранов проекта в `docs/projects/<project-slug>/screens/` (flow · screen · block · shell). Ведёт сессию заполнения через структурированные вопросы (AskUserQuestion), фиксирует контекст в собственной памяти `state/<project-slug>/`, аккумулирует визуальные референсы в `docs/projects/<project-slug>/screens/assets/<kind>/<slug>/`, ходит в web за UI-референсами по явной просьбе, опирается на инвентарь компонентов `@sftbmb/ui` и не выдумывает craft. Использовать всегда, когда речь о screens-слое проекта, заполнении одного из 4 артефактных kind (flow/screen/block/shell), заведении или углублении потока/экрана/блока/каркаса, разборе сырья (скриншот UI, описание макета, транскрипт интервью, ссылка на конкурента), переходе записи `status: draft → stable`, удалении с каскадом, прокладке композиции через семантическое дерево, или копании связей между сущностями screens и сущностями interface. Также — единственная точка входа в screens-слой проекта: новые файлы и правки артефактов делаются через этот скилл.
---

# screen-deep-dive

Углублённая проработка артефактов экранов **одного проекта** в
`docs/projects/<project-slug>/screens/`. Канон формы —
`docs/projects/_canon/screens/README.md` и README'ы по kind в его
подпапках. Скилл ведёт сеанс через структурированные вопросы, фиксирует
контекст в `state/<project-slug>/`, не выдумывает craft и не лезет в
interface-слой того же проекта своими руками.

Использовать как **единственную точку входа** в screens-слой проекта:
заведение, углубление, разбор сырья, переход `draft → stable`,
удаление с каскадом.

Скилл всегда работает **в контексте одного проекта** (см. «Выбор
проекта»). Дальше по тексту `<project-slug>` — выбранный проект;
screens-слой — `docs/projects/<project-slug>/screens/`, interface-слой
того же проекта — `docs/projects/<project-slug>/interface/`.

## Выбор проекта

Скилл работает в контексте **одного** проекта. `<project-slug>` —
первый позиционный аргумент:

| вызов | проект |
|---|---|
| `/screen-deep-dive <project-slug> …` | взять `<project-slug>` |
| `/screen-deep-dive …` (без slug) | `AskUserQuestion`-пикер по папкам `docs/projects/` (исключая `_canon`) |

Поскольку точки входа допускают `<kind>:<slug>` (например,
`screen-deep-dive my-app:login`), `<project-slug>` отделяется от
остатка как первый токен и/или по совпадению с именем подпапки
`docs/projects/`:

1. Если первый аргумент совпадает с именем подпапки `docs/projects/`
   (кроме `_canon`) — это `<project-slug>`; остаток args — точка входа.
2. Иначе — пикер по подпапкам `docs/projects/` (исключить `_canon`).
   Если проектов нет — сказать «сначала заведи проект через
   `/project-deep-dive`», выйти.
3. Все чтения/записи скоупятся в выбранный проект:
   `docs/projects/<project-slug>/screens/`,
   `docs/projects/<project-slug>/interface/`,
   `docs/projects/<project-slug>/screens/assets/`,
   `state/<project-slug>/`.

## Точки входа

После того как `<project-slug>` определён, остаток args задаёт режим:

| вызов | поведение |
|---|---|
| `/screen-deep-dive <project-slug>` | сводка состояния + топ-3 кандидата на углубление |
| `/screen-deep-dive <project-slug> <kind>` | завести новую сущность типа kind (режим A) |
| `/screen-deep-dive <project-slug> <kind>:<slug>` | завести (если slug ещё не существует) либо углубить (если существует) |
| `/screen-deep-dive <project-slug> <slug>` | найти slug; одиночный → C; конфликт kind → переспросить |
| `/screen-deep-dive <project-slug> <свободный текст / приложение>` | сырьё → разбор (режим B) |

`kind` ∈ {`flow`, `screen`, `block`, `shell`}.

Сырьё (режим B) — это: текстовое описание макета, скриншот UI,
ссылка на чужой продукт, выгрузка из Figma, транскрипт интервью с
дизайнером, либо любой комбинированный inputs. Картинки и URL —
обычные content-блоки в сообщении пользователя.

## Что делать сразу при запуске

1. Определить `<project-slug>` (см. «Выбор проекта»).
2. Прочитать `docs/projects/_canon/screens/README.md` и README'ы по
   4 kind в его подпапках — освежить канон композиции, layout-язык,
   имена `ui:*`/`block:*`/`data:*`, anti-patterns.
3. Прочитать `docs/projects/<project-slug>/vision.md` и продуктовые
   файлы (если есть) + `references/project-context.md` — освежить связи
   с продуктовым слоем **того же проекта** (flow ↔ surface,
   screen ↔ capability).
4. Если остаток args пуст — сделать сводку (см. ниже) и через
   `AskUserQuestion` предложить выбор что копать.
5. Если остаток args указывает на сущность — определить kind и режим
   (A/B/C), применить маршрут из `references/workflow-patterns.md`.

## Сводка состояния (без args)

1. Пройтись по
   `docs/projects/<project-slug>/screens/{flows,screens,blocks,shells}/*/index.md`.
2. Подсчитать: сколько `draft` / `stable` по каждому kind.
3. Прочитать `state/` (если есть) и собрать открытые вопросы — секции
   `## Открытые вопросы`; пометки `**blocker**` приоритетны.
4. Выявить топ-3 «горячих» кандидата по приоритету:
   - draft-записи с `**blocker**`-вопросами;
   - draft-записи с большим числом пустых обязательных слотов или
     дырами в дереве (`tree`/`slot-fills`);
   - draft-записи, на которые ссылаются stable-соседи (блокируют их
     корректность) — например, `screen.shell` ссылается на draft-shell.
5. Вывести сводку в чат, предложить через `AskUserQuestion` выбрать.

## Три режима

См. `references/workflow-patterns.md` — детали сценариев и примеры
вопросов.

- **A. Новая сущность**. Args = `<kind>` или `<kind>:<новый-slug>`.
  Батч `AskUserQuestion` по чек-листам полей из
  `references/field-checklists.md`; опции — anti-patterns из секций
  `Что <kind> НЕ` соответствующих README'ев; свободная форма через
  Other для значений (`name`, `description`, `route`, текст label и
  т.п.).
- **B. Сырьё**. Args = свободный текст, картинка, URL. Скилл
  анализирует, извлекает кандидатов, через чат показывает план,
  по подтверждению заводит stub-папки и погружается в каждую через
  режим C. Подробности — `references/raw-input.md`.
- **C. Углубление**. Args = `<kind>:<slug>` существующей записи или
  выбор из сводки. Точечные вопросы по дырам и подозрениям; вход в
  дерево (если просили глубоко); чек-лист `draft → stable` после
  каждой правки.

## Стиль вопросов

См. `references/workflow-patterns.md`.

- **Всегда через `AskUserQuestion`**, до 4 вопросов в одном раунде.
- **Опции** только для:
  - anti-patterns из секций `Что <kind> НЕ` («это похоже на
    anti-pattern X — согласен?»);
  - теста-критерия (бинарный выбор ✅/❌ из секций `Тест-критерий`);
  - перечисления enum'ов из канона (`viewport: desktop|mobile|any`,
    `accepts: block|tree|block | tree|block (modal/drawer)`,
    `behaviour: visible|drawer-via-burger|overlay|stacked|hidden`,
    `entrypoint: true|false`);
  - выбора существующего slug-соседа (по опции на каждый существующий
    + «нужен новый» через Other);
  - выбора `ui:Component` из инвентаря (см. ниже);
  - выбора `block:<slug>` для слота из существующих + «новый» (Other).
- **Свободная форма** (через Other) — для **значения**: `name`,
  `description`, `route`, тексты label/placeholder/title, slug новых
  сущностей, props со свободным значением (`placeholder='…'`).
- **Никогда** не предлагать конкретные тексты доменных значений
  (label кнопки, route, описание блока) от себя. Anti-patterns — да.
  Сама формулировка — нет.

## Память `state/<project-slug>/<kind>/<slug>.md`

Заметки лежат **рядом со скиллом**, не в
`docs/projects/<project-slug>/screens/` и не в корне проекта, и
скоупятся по проекту:

```
.claude/skills/screen-deep-dive/state/<project-slug>/<kind>/<slug>.md
```

Дальше по тексту скилла — короткое `state/`, это сокращение того же
пути (с учётом текущего `<project-slug>`).

См. `references/state-format.md`. Кратко:

- Файл существует, пока в нём есть хоть одна секция с содержимым.
- Три возможные секции (любая может отсутствовать):
  - `## Открытые вопросы` (опц. префикс `**blocker**` у вопроса,
    блокирующего stable),
  - `## Доменные решения` (неочевидные смысловые решения, не лезущие
    в `description`),
  - `## Что копать дальше` (включая «ui-lib gap: нужен ui:Foo» —
    обратная связь в библиотеку).
- Если все три пусты — заметку удалить.
- Заметка не журнал: не аккумулировать «было/стало», только текущее
  состояние знания. Forward-only.

## Ассеты

См. `references/assets-policy.md`. Кратко:

- Каталог: `docs/projects/<project-slug>/screens/assets/<kind>/<slug>/`.
  Имена файлов — человекочитаемые kebab-case
  (`master-detail-figma.png`, `competitor-linear-list.png`).
- Поле во frontmatter каждого kind: `assets: ['file1.png', 'file2.png']`
  (пути от `assets/<kind>/<slug>/`). Lint проверяет существование
  файла.
- Входящая картинка от аналитика → скилл анализирует, через
  `AskUserQuestion` решают вместе: (a) сохранить как референс с slug-ом,
  (b) использовать как сырьё (режим B) и не сохранять, (c) поискать
  лучшие референсы в web.
- Web-поиск — **только по явной просьбе** (`«найди референсы на X»`).
  Скилл вызывает `WebSearch`, показывает кандидатов через
  `AskUserQuestion`, аналитик выбирает один (или ни одного). Выбранный
  — `WebFetch`/скачивание в
  `assets/<kind>/<slug>/<имя>.<ext>` (от корня
  `docs/projects/<project-slug>/screens/assets/`). Без просьбы скилл не
  лазит в web.

## Инвентарь `ui:Component`

См. `references/ui-inventory.md`. Кратко:

- Источник правды — `manifest.json` пакета `@sftbmb/ui` (когда
  опубликован). Скилл ищет его по локальному пути установки пакета или
  в соседнем репо `ui-lib` (если доступен).
- Пока manifest'а нет — fallback на раздел «Топ-уровень компонентов»
  в `docs/projects/_canon/screens/README.md`. Это «выводимые
  требования», не окончательный реестр.
- В режиме углубления дерева скилл предлагает `ui:Component` как
  опции из инвентаря (по релевантной категории: layout-примитивы для
  обёрток, data-display для тел, feedback для states, и т.д.).
- Если в инвентаре нет подходящего — `AskUserQuestion`:
  «предложить новый `ui:Foo` как требование к ui-lib?». По «да» —
  компонент попадает в дерево, и в
  `state/<project-slug>/<kind>/<slug>.md` в секции
  `## Что копать дальше` появляется строка
  `ui-lib gap: нужен ui:Foo — для <зачем>`.

## Контракт `draft → stable`

См. `references/draft-stable.md`. Чек-лист после каждой правки (6
пунктов):

1. Обязательные слоты frontmatter заполнены (опциональные могут быть
   `—`).
2. Все `slug`-ссылки валидны (записи существуют — внутри
   `docs/projects/<project-slug>/screens/` и в interface-слое того же
   проекта `docs/projects/<project-slug>/interface/`).
3. Зеркала консистентны:
   - `block.ux-substrates` (screens) ↔ `block.ux-substrates`
     (interface, `docs/projects/<project-slug>/interface/block.md`);
   - `block.used-by-screens` ↔ ссылки `block:<slug>` в screens;
   - `screen.blocks` ↔ блоки в `slot-fills`/`states`.
4. Тест-критерий из README соответствующего kind (канон
   `docs/projects/_canon/screens/<kind>/README.md`) явно подтверждён
   аналитиком в этой сессии.
5. В `state/<project-slug>/<kind>/<slug>.md` нет `**blocker**`-вопросов.
6. Дерево в теле артефакта полное:
   - `screen.slot-fills` — все обязательные слоты shell заполнены;
     `states` покрывает минимум `loading`, `empty`, `error`,
     `permission-denied`, `offline`, `not-found` (override либо явное
     «здесь не применимо» через комментарий, но не пустота).
   - `block.tree` — минимум `block-body`; объявленные `ux-substrates`
     покрыты соответствующими узлами.
   - `shell.tree` — есть и `slots`, и `tree` с `(fills: $<slot>)`.
   - `flow` — без yaml-дерева, но обязательно непустые `desktop` и
     `mobile`, описаны `transitions` внутри mobile-серии (если в ней
     ≥2 экранов).

Если все 6 ✅ — предложить через `AskUserQuestion`: «Готов к stable,
повышаем?». По подтверждению — изменить `status: draft → stable`.
Скилл **не повышает сам**.

Понижение `stable → draft` — только аналитик руками. Скилл максимум
может предложить, не делать.

## Зеркала interface ↔ screens

Зеркало `block.ux-substrates` (M:N) живёт в **двух** слоях **одного и
того же проекта**:

- `docs/projects/<project-slug>/interface/block.md` — взгляд бизнеса
  (блок собирает определённые субстраты ситуаций);
- `docs/projects/<project-slug>/screens/blocks/<slug>/index.md`
  (frontmatter `ux-substrates: [...]`) — взгляд композиции (блок
  реализует те же субстраты как узлы дерева).

Канонического источника нет: оба слоя ведут разную работу. При
расхождении скилл **не правит молча**. Алгоритм:

1. После любой правки `ux-substrates` в screens-блоке или после
   запуска C-режима на блоке — сравнить с
   `docs/projects/<project-slug>/interface/block.md`.
2. Если совпадает — ок.
3. Если различаются — через `AskUserQuestion` показать diff и
   спросить: «какой слой брать за источник правды для этого блока?»
   - «screens-вариант» → предложить аналитику запустить
     `interface-deep-dive <project-slug> block:<slug>` и подровнять
     interface;
   - «interface-вариант» → подровнять screens-блок (правка
     `ux-substrates` в frontmatter здесь);
   - «оба нужны» → значит расхождение смысловое, оставить state-заметку
     `**blocker**: ux-substrates расходятся, прояснить смысл блока`.

Скилл **не правит** interface-слой проекта своими руками — это домен
`interface-deep-dive`.

## Stub-сущности

### Внутри screens

Если копаемая сущность ссылается на не существующий screens-slug:

1. Завести stub-папку
   `docs/projects/<project-slug>/screens/<kind>/<slug>/index.md` с
   минимальным frontmatter (`slug + name + description + status=draft`
   + обязательные опции с `—` где допустимо).
2. В `state/<project-slug>/<kind>/<slug>.md` — секция
   `## Открытые вопросы` с записью «Заведён как stub в контексте
   `<откуда сослались>` — докопать».
3. Возврат в исходную сущность, копание продолжается.

### В interface (зависимость на не существующий interface-slug)

Если `screen.situations` / `block.interface-block` / `data:<slug>` /
прочая ссылка указывает на не существующий interface-slug **того же
проекта**:

1. **Скилл не заводит ничего в
   `docs/projects/<project-slug>/interface/`** — это нарушение единой
   точки входа interface.
2. Через `AskUserQuestion` показать аналитику: «Ссылка на
   `<kind>:<slug>` в interface не валидна. Что делаем?»
   - «запустить `interface-deep-dive <project-slug> <kind>:<slug>`
     сейчас, я подожду» → скилл говорит «запусти
     `/interface-deep-dive <project-slug> <kind>:<slug>`», выходит из
     текущей сущности (state-заметка с `**blocker**`), ждёт
     возвращения аналитика;
   - «удалить эту ссылку» (если поле допускает) → правка screens;
   - «заменить на существующий slug» (показать варианты) → правка.

## Удаление сущности (каскад)

1. Прочитать все 4 kind-папки
   `docs/projects/<project-slug>/screens/` + `state/` — найти все
   ссылки на удаляемый slug. Также проверить
   `docs/projects/<project-slug>/screens/assets/<kind>/<slug>/`.
2. Показать каскад: «ссылаются X, Y, Z — вот что сломается».
3. Через `AskUserQuestion` по каждому месту — опции: «заменить на
   другой slug» / «поставить `—` (если поле допускает)» / «удалить
   ссылающуюся запись».
4. По подтверждению — выполнить все правки одним пакетом.
5. Удалить папку `docs/projects/<project-slug>/screens/<kind>/<slug>/`
   целиком (включая `index.md` и любые add-on файлы).
6. Удалить папку
   `docs/projects/<project-slug>/screens/assets/<kind>/<slug>/` целиком,
   если существует.
7. Удалить `state/<project-slug>/<kind>/<slug>.md`, если существует.
8. Пересчитать зеркала затронутых блоков (`used-by-screens`,
   `screen.blocks`).

## Завершение сессии

В конце:

1. Перечислить затронутые сущности (заведены / углублены / удалены).
2. Перечислить нерешённые открытые вопросы по сущностям (с указанием
   `**blocker**`-меток).
3. Предложить через `AskUserQuestion`: «Прогнать
   `/screen-audit <project-slug>`?» — это полный аудит консистентности
   screens-слоя проекта и зеркал с его interface. По «да» сказать
   пользователю «Запусти `/screen-audit <project-slug>`» — сам не
   вызываю, это другой скилл.

## Запреты

- Не редактировать артефакты вслепую — всегда сначала `Read`.
- Не выдумывать значения доменных полей. Anti-patterns как опции — да;
  тексты label, route, description, name — нет.
- Не выдумывать craft (облик, цвет, шрифт, пиксели, размер) — это
  библиотека `@sftbmb/ui`, не предмет скилла.
- Не упоминать FSD-имена (`widget`, `feature`, `pages/`) в дереве или
  в frontmatter — FSD-структура живёт в коде, который пишется по
  screens вручную, не в самих артефактах.
- Не помещать тематические оси (`density`/`brand`/`scheme`) ни в
  frontmatter, ни в узлы дерева — это data-* на корне приложения.
- Не помещать breakpoints в `slot-fills` или `block.tree` —
  облицовочный адаптив только в `shell.responsive`, структурный — в
  `flow`.
- Не лезть в interface-слой проекта
  (`docs/projects/<project-slug>/interface/`) своими руками — только
  через предложение аналитику запустить `interface-deep-dive`.
- Не работать сразу с несколькими проектами в одной сессии — скилл
  скоупится в один `<project-slug>`.
- Не повышать `draft → stable` без явного подтверждения аналитика.
- Не понижать `stable → draft` сам — только подсветить и предложить.
- Не править `block.ux-substrates` молча при рассинхроне с interface —
  всегда переспрашивать источник правды.
- Не лазить в web без явной просьбы аналитика.
- Не сохранять входящие картинки в `assets/` без согласия аналитика.
- Не вызывать `screen-audit` самостоятельно — только предложить.
- Не аккумулировать историю в `state/` — forward-only.
- Не создавать `state/<project-slug>/<kind>/<slug>.md`, если все
  секции были бы пустыми — заметка появляется только когда есть что
  записать.
