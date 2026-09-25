---
name: screen-deep-dive
description: "Углублённая проработка экранов проекта в `docs/projects/<project-slug>/screens/<surface>/` (flow · screen · block · shell) — единственная точка входа в screens-слой одной поверхности из реестра `surface.md`: новые файлы и правки идут через этот скилл. Ведёт сессию структурированными вопросами (AskUserQuestion), собирает композицию семантическим деревом (`ui:` · `layout:` · `icon:` · `block:` · `data:`), держит зеркала с interface той же поверхности, копит визуальные референсы в `assets/`, фиксирует контекст в своей ветке единого дерева state оркестратора (`../entrypoint/state/projects/<project-slug>/screens/<surface>/`); облик (craft) и тексты не выдумывает. Использовать всегда, когда речь о screens-слое: завести или углубить поток, экран, блок или каркас; разобрать сырьё (скриншот UI, описание макета, транскрипт, ссылку на конкурента); перевести запись `draft → stable`; удалить с каскадом; проследить связи экранов с interface."
---

# screen-deep-dive

Углублённая проработка артефактов экранов **одного проекта**, в контексте
**одной поверхности (surface)** —
`docs/projects/<project-slug>/screens/<surface>/`. Канон формы —
`docs/projects/_template/screens/README.md` и файлы-формы по kind в подпапке
`_template/`. Скилл ведёт сеанс через структурированные вопросы, фиксирует
контекст в своей ветке единого дерева state оркестратора
(`../entrypoint/state/projects/<project-slug>/screens/<surface>/`), не
выдумывает craft и не лезет в interface-слой того же проекта своими
руками.

Использовать как **единственную точку входа** в screens-слой проекта:
заведение, углубление, разбор сырья, переход `draft → stable`,
удаление с каскадом.

Screens-слой **партиционирован по поверхности**: каждая поверхность из
реестра-хребта `docs/projects/<project-slug>/surface.md` получает свою
папку `screens/<surface>/`. Скилл всегда работает **в контексте одного
проекта и одной поверхности** (см. «Выбор проекта» и «Выбор поверхности»).
Дальше по тексту `<project-slug>` — выбранный проект, `<surface>` —
выбранная поверхность; screens-слой —
`docs/projects/<project-slug>/screens/<surface>/`, interface-слой той же
поверхности того же проекта —
`docs/projects/<project-slug>/interface/<surface>/`. Поверхности
изолированы: ссылки внутри `screens/<surface>/` и зеркала с
`interface/<surface>/` — в пределах одной поверхности.

## Выбор проекта

Скилл работает в контексте **одного** проекта. `<project-slug>` —
первый позиционный аргумент, `<surface>` — второй (см. «Выбор
поверхности»):

| вызов | проект |
|---|---|
| `/screen-deep-dive <project-slug> [<surface>] …` | взять `<project-slug>` |
| `/screen-deep-dive …` (без slug) | `AskUserQuestion`-пикер **по именам** проектов (исключая `_template`) |

Поскольку точки входа допускают `<kind>:<slug>` (например,
`screen-deep-dive my-app web login`), `<project-slug>` отделяется от
остатка как первый токен и/или по совпадению с именем подпапки
`docs/projects/`:

1. Если первый аргумент совпадает с именем подпапки `docs/projects/`
   (кроме `_template`) — это `<project-slug>`; остаток args идёт на
   выбор поверхности и точку входа.
2. Иначе — пикер **по именам** проектов (подпапки `docs/projects/`,
   исключить `_template`; опции — имена из `vision`, slug — деталь).
   Если проектов нет — сказать «сначала заведи проект через
   `/project-deep-dive`», выйти.
3. После того как проект определён — определить поверхность (см.
   «Выбор поверхности»).
4. Все чтения/записи скоупятся в выбранный проект **и поверхность**:
   `docs/projects/<project-slug>/screens/<surface>/`,
   `docs/projects/<project-slug>/interface/<surface>/`,
   `docs/projects/<project-slug>/screens/<surface>/assets/`,
   ветка state
   `../entrypoint/state/projects/<project-slug>/screens/<surface>/`.

## Выбор поверхности

Screens-слой партиционирован по поверхности. После проекта скилл
определяет `<surface>` — второй позиционный аргумент:

| вызов | поверхность |
|---|---|
| `/screen-deep-dive <project-slug> <surface> …` | взять `<surface>` |
| `/screen-deep-dive <project-slug> …` (без surface) | `AskUserQuestion`-пикер **по именам** поверхностей из реестра `surface.md` |

Алгоритм:

1. Прочитать реестр-хребет
   `docs/projects/<project-slug>/surface.md` — список поверхностей.
   Кандидаты — поверхности, чья композиция живёт в экранах: для
   `type: bot` слой — `telegram-bot-flow/<surface>/`
   (`/telegram-bot-flow-deep-dive`), для `type: mobile` —
   `mobile/<surface>/` (`/mobile-deep-dive`); такие поверхности в пикер не
   попадают, а переданные аргументом — отклоняются с подсказкой нужного
   скилла.
2. Если следующий после `<project-slug>` токен совпадает со `slug`
   поверхности из реестра — это `<surface>`; остаток args — точка входа.
3. Иначе — пикер **по именам** поверхностей (опции — `name` из
   `surface.md`; `type` и `slug` — деталь в описании опции). Аналитик
   slug не вводит — выбирает имя.
   - Если в реестре одна поверхность — взять её без вопроса.
   - Если реестр пуст (нет `surface.md` или нет строк) — сказать
     «сначала заведи поверхность через `/project-deep-dive
     <project-slug>` (реестр-хребет `surface.md`)», выйти.
4. Если папки `docs/projects/<project-slug>/screens/<surface>/` ещё
   нет — она появится при заведении первой сущности (режим A/B); это
   нормально для свежей поверхности.

Дальше весь сеанс идёт **в пределах одной поверхности**. Сменить
поверхность — это новый запуск скилла с другим `<surface>`.

## Точки входа

После того как `<project-slug>` и `<surface>` определены, остаток args
задаёт режим:

| вызов | поведение |
|---|---|
| `/screen-deep-dive <project-slug> <surface>` | сводка состояния поверхности + топ-3 кандидата на углубление |
| `/screen-deep-dive <project-slug> <surface> <kind>` | завести новую сущность типа kind (режим A) |
| `/screen-deep-dive <project-slug> <surface> <kind>:<slug>` | завести (если slug ещё не существует) либо углубить (если существует) |
| `/screen-deep-dive <project-slug> <surface> <slug>` | найти slug; одиночный → C; конфликт kind → переспросить |
| `/screen-deep-dive <project-slug> <surface> <свободный текст / приложение>` | сырьё → разбор (режим B) |

`kind` ∈ {`flow`, `screen`, `block`, `shell`}. Папки сущностей в
`screens/<surface>/` — во множественном числе (`flows/`, `screens/`,
`blocks/`, `shells/`): путь `…/<kind>/<slug>/` артефакта означает такую
папку. В `assets/<kind>/<slug>/` и в ветке state kind пишется в
единственном числе (`assets/flow/<slug>/`).

Сырьё (режим B) — это: текстовое описание макета, скриншот UI,
ссылка на чужой продукт, выгрузка из Figma, транскрипт интервью с
дизайнером, либо любая их комбинация. Картинки и URL — обычные
content-блоки в сообщении пользователя.

## Что делать сразу при запуске

1. Определить `<project-slug>` (см. «Выбор проекта») и `<surface>` (см.
   «Выбор поверхности»).
2. Прочитать `docs/projects/_template/screens/README.md` и файлы-формы по
   4 kind в подпапке `_template/` — освежить канон композиции, layout-язык,
   имена `ui:*`/`layout:*`/`icon:*`/`block:*`/`data:*`, anti-patterns.
3. Прочитать `docs/projects/<project-slug>/vision.md`,
   реестр-хребет `docs/projects/<project-slug>/surface.md`, файл
   возможностей выбранной поверхности
   `docs/projects/<project-slug>/capability/<surface>.md` (если есть) +
   `references/project-context.md` — освежить связи с продуктовым слоем
   **того же проекта** (flow/shell живут на `<surface>` структурно,
   screen ↔ `capability/<surface>`).
4. Если остаток args пуст — сделать сводку (см. ниже) и через
   `AskUserQuestion` предложить выбор что копать.
5. Если остаток args указывает на сущность — определить kind и режим
   (A/B/C), применить маршрут из `references/workflow-patterns.md`.

## Сводка состояния (без args)

1. Пройтись по
   `docs/projects/<project-slug>/screens/<surface>/{flows,screens,blocks,shells}/*/index.md`.
2. Подсчитать: сколько `draft` / `stable` по каждому kind.
3. Прочитать свою ветку
   `../entrypoint/state/projects/<project-slug>/screens/<surface>/`
   (если есть) и собрать открытые вопросы — секции `## Открытые
   вопросы`; пометки `**blocker**` приоритетны.
4. Выявить топ-3 «горячих» кандидата по приоритету:
   - draft-записи с `**blocker**`-вопросами;
   - draft-записи с большим числом пустых обязательных слотов или
     дырами в дереве (`tree`/`slot-fills`);
   - draft-записи, на которые ссылаются stable-соседи (блокируют их
     корректность) — например, `screen.shell` ссылается на draft-shell.
5. Вывести сводку в чат (с указанием поверхности), предложить через
   `AskUserQuestion` выбрать.

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

- Вопросы — через `AskUserQuestion`, до 4 в одном раунде (лимит
  инструмента; больше — следующим раундом).
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
  - выбора имени `ui:*` из уже использованных в поверхности (см. «Нотация
    дерева»);
  - выбора `block:<slug>` для слота из существующих + «новый» (Other).
- **Свободная форма** (через Other) — для **значения**: `name`,
  `description`, `route`, тексты label/placeholder/title, атрибуты узлов
  со свободным значением.
- Тексты доменных значений (label кнопки, route, описание блока)
  формулирует аналитик: это его экспертиза (`CLAUDE.md` §3). Поэтому
  опциями идут anti-patterns и enum'ы, а сами формулировки скилл не
  подсказывает.

## Память: своя ветка единого дерева state

Скилл не держит своего `state/`. Per-kind заметки пишутся в **свою ветку**
единого дерева state оркестратора, не в
`docs/projects/<project-slug>/screens/<surface>/` и не в корне проекта;
ветка скоупится по проекту **и поверхности**:

```
../entrypoint/state/projects/<project-slug>/screens/<surface>/<kind>/<slug>.md
```

Формат заметки — канон `../entrypoint/references/state-model.md`. Кратко:

- Файл существует, пока в нём есть хоть одна секция с содержимым.
- Frontmatter: `kind` · `slug` · `ref` (путь к артефакту).
- Три возможные секции (любая может отсутствовать):
  - `## Открытые вопросы` (опц. префикс/суффикс `**blocker**` у вопроса,
    блокирующего stable),
  - `## Доменные решения` (неочевидные смысловые решения, не лезущие
    в `description`),
  - `## Что копать дальше`.
- Если все секции пусты — заметку удалить.
- Заметка не журнал: не аккумулировать «было/стало», только текущее
  состояние знания. Forward-only.

### Единый контекст: read-only видимость дерева

Для единой картины скилл **read-only** подтягивает всё дерево state
оркестратора `../entrypoint/state/` (срез `index.md`, открытые нити
`threads/`, верхнеуровневые слои `business/`, `ajtbd/`, `swot/`,
`hypothesis-map/`) и клиентский дом `../entrypoint-for-business/state/`.
Проектные ветки `projects/<…>/` читаются **только по текущему
`<project-slug>`** (изоляция продуктов сохраняется). Своя ветка
`projects/<project-slug>/screens/<surface>/` — **rw**, всё остальное
дерево (включая ветки других поверхностей `screens/<other-surface>/`) и
клиентский дом — **read-only**: в чужое не писать. При чтении клиентского
дома маркер `**жду аналитика**` трактуется как blocker-кандидат.

## Ассеты

См. `references/assets-policy.md`. Кратко:

- Каталог:
  `docs/projects/<project-slug>/screens/<surface>/assets/<kind>/<slug>/`.
  Имена файлов — человекочитаемые kebab-case
  (`master-detail-figma.png`, `competitor-linear-list.png`).
- Поле во frontmatter каждого kind: `assets: ['file1.png', 'file2.png']`
  (пути от `<surface>/assets/<kind>/<slug>/`). Существование файлов
  проверяет `/screen-audit` (R-COV-006).
- Входящая картинка от аналитика → скилл анализирует, через
  `AskUserQuestion` решают вместе: (a) сохранить как референс с slug-ом,
  (b) использовать как сырьё (режим B) и не сохранять, (c) поискать
  лучшие референсы в web.
- Web-поиск — только по явной просьбе аналитика (`«найди референсы на
  X»`). Скилл вызывает `WebSearch`, показывает кандидатов через
  `AskUserQuestion`, аналитик выбирает один (или ни одного). Выбранный
  — `WebFetch`/скачивание в
  `<surface>/assets/<kind>/<slug>/<имя>.<ext>` (от корня
  `docs/projects/<project-slug>/screens/<surface>/assets/`).

## Нотация дерева

Дерево (`slot-fills`, `states`, `tree`) пишется семантической нотацией
канона слоя; как вести по ней аналитика — `references/tree-notation.md`
(читать перед углублением дерева). Кратко:

- `ui:<Name>` — интерфейсный примитив проекта: в коде его реализует
  проектный компонент, у фронтовой поверхности — слайс `shared-ui` FSD-карты.
  Один примитив — одно имя в пределах поверхности; имя нового примитива
  скилл выводит из слов аналитика.
- `layout:` — раскладка, `icon:<name>` — иконка, `block:` / `data:` —
  рефы на блоки поверхности и датумы interface; текст и иконки — дети
  узла.
- Атрибуты узлов (`variant=accent`) — свободные смысловые пометки автора
  без внешней проверки.
- Облик (цвет, типографика, пространство, движение) в дерево не пишется:
  wireframe и hi-fi собирает автор макета вручную, craft скилл не
  выдумывает.

## Контракт `draft → stable`

См. `references/draft-stable.md`. Чек-лист после каждой правки (6
пунктов):

1. Обязательные слоты frontmatter заполнены (опциональные могут быть
   `—`).
2. Все `slug`-ссылки валидны (записи существуют — внутри
   `docs/projects/<project-slug>/screens/<surface>/` и в interface-слое
   **той же поверхности** того же проекта
   `docs/projects/<project-slug>/interface/<surface>/`).
3. Зеркала консистентны:
   - `block.ux-substrates` (screens) ↔ `block.ux-substrates`
     (interface,
     `docs/projects/<project-slug>/interface/<surface>/block.md`);
   - `block.used-by-screens` ↔ ссылки `block:<slug>` в screens;
   - `screen.blocks` ↔ блоки в `slot-fills`/`states`.
4. Тест-критерий из README соответствующего kind (канон
   `docs/projects/_template/screens/_template/<kind>.md`) явно подтверждён
   аналитиком в этой сессии.
5. В
   `../entrypoint/state/projects/<project-slug>/screens/<surface>/<kind>/<slug>.md`
   нет `**blocker**`-вопросов.
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

Зеркало `block.ux-substrates` (M:N) живёт в **двух** слоях **одной и той
же поверхности одного и того же проекта**:

- `docs/projects/<project-slug>/interface/<surface>/block.md` — взгляд
  бизнеса (блок собирает определённые субстраты ситуаций);
- `docs/projects/<project-slug>/screens/<surface>/blocks/<slug>/index.md`
  (frontmatter `ux-substrates: [...]`) — взгляд композиции (блок
  реализует те же субстраты как узлы дерева).

Канонического источника нет: оба слоя ведут разную работу. При
расхождении скилл **не правит молча**. Алгоритм:

1. После любой правки `ux-substrates` в screens-блоке или после
   запуска C-режима на блоке — сравнить с
   `docs/projects/<project-slug>/interface/<surface>/block.md`.
2. Если совпадает — ок.
3. Если различаются — через `AskUserQuestion` показать diff и
   спросить: «какой слой брать за источник правды для этого блока?»
   - «screens-вариант» → предложить аналитику запустить
     `interface-deep-dive <project-slug> <surface> block:<slug>` и
     подровнять interface;
   - «interface-вариант» → подровнять screens-блок (правка
     `ux-substrates` в frontmatter здесь);
   - «оба нужны» → значит расхождение смысловое, оставить state-заметку
     `**blocker**: ux-substrates расходятся, прояснить смысл блока`.

Скилл **не правит** interface-слой проекта своими руками — это домен
`interface-deep-dive`.

## Stub-сущности

### Внутри screens

Если копаемая сущность ссылается на не существующий screens-slug **той
же поверхности**:

1. Завести stub-папку
   `docs/projects/<project-slug>/screens/<surface>/<kind>/<slug>/index.md`
   с минимальным frontmatter (`slug + name + description + status=draft`
   + обязательные опции с `—` где допустимо).
2. В
   `../entrypoint/state/projects/<project-slug>/screens/<surface>/<kind>/<slug>.md`
   — секция `## Открытые вопросы` с записью «Заведён как stub в контексте
   `<откуда сослались>` — докопать».
3. Возврат в исходную сущность, копание продолжается.

### Stub-зависимость на interface-slug

Если `screen.situations` / `block.interface-block` / `data:<slug>` /
прочая ссылка указывает на не существующий interface-slug **той же
поверхности того же проекта**:

1. **Скилл не заводит ничего в
   `docs/projects/<project-slug>/interface/<surface>/`** — это нарушение
   единой точки входа interface.
2. Через `AskUserQuestion` показать аналитику: «Ссылка на
   `<kind>:<slug>` в interface не валидна. Что делаем?»
   - «запустить `interface-deep-dive <project-slug> <surface>
     <kind>:<slug>` сейчас, я подожду» → скилл говорит «запусти
     `/interface-deep-dive <project-slug> <surface> <kind>:<slug>`»,
     выходит из текущей сущности (state-заметка с `**blocker**`), ждёт
     возвращения аналитика;
   - «удалить эту ссылку» (если поле допускает) → правка screens;
   - «заменить на существующий slug» (показать варианты) → правка.

## Удаление сущности (каскад)

1. Прочитать все 4 kind-папки
   `docs/projects/<project-slug>/screens/<surface>/` + свою ветку
   `../entrypoint/state/projects/<project-slug>/screens/<surface>/` —
   найти все ссылки на удаляемый slug (в пределах поверхности). Также
   проверить
   `docs/projects/<project-slug>/screens/<surface>/assets/<kind>/<slug>/`.
2. Показать каскад: «ссылаются X, Y, Z — вот что сломается».
3. Через `AskUserQuestion` по каждому месту — опции: «заменить на
   другой slug» / «поставить `—` (если поле допускает)» / «удалить
   ссылающуюся запись».
4. По подтверждению — выполнить все правки одним пакетом.
5. Удалить папку
   `docs/projects/<project-slug>/screens/<surface>/<kind>/<slug>/`
   целиком (включая `index.md` и любые add-on файлы).
6. Удалить папку
   `docs/projects/<project-slug>/screens/<surface>/assets/<kind>/<slug>/`
   целиком, если существует.
7. Удалить
   `../entrypoint/state/projects/<project-slug>/screens/<surface>/<kind>/<slug>.md`,
   если существует.
8. Пересчитать зеркала затронутых блоков (`used-by-screens`,
   `screen.blocks`).

## Завершение сессии

В конце:

1. Перечислить затронутые сущности (заведены / углублены / удалены).
2. Перечислить нерешённые открытые вопросы по сущностям (с указанием
   `**blocker**`-меток).
3. Предложить через `AskUserQuestion`: «Прогнать
   `/screen-audit <project-slug> <surface>`?» — это аудит консистентности
   screens-слоя поверхности и зеркал с её interface. По «да» сказать
   пользователю «Запусти `/screen-audit <project-slug> <surface>`» — сам
   не вызываю, это другой скилл.

## Границы

Артефакты screens несут только композицию. Три вещи живут в других
местах, поэтому ни в дерево, ни во frontmatter не пишутся:

- FSD-имена (`widget`, `feature`, `pages/`) — карта слайсов ведётся в
  `fsd/<surface>/` (`/fsd-deep-dive`);
- оси контекста приложения (тема, бренд, плотность, направление письма)
  — их задаёт корень приложения в коде, а не узел дерева;
- breakpoints в `slot-fills` и `block.tree` — облицовочный адаптив
  описывает `shell.responsive`, структурный — `flow`.

Итог ключевого: формулировки и решения приходят от аналитика, в stable
запись поднимается только по его подтверждению, а interface и чужие ветки
state скилл не правит; другие скиллы, включая аудит, он не запускает —
только предлагает.
