---
name: telegram-bot-flow-deep-dive
description: "Углублённая проработка артефактов композиции телеграм-бота в `docs/projects/<project-slug>/telegram-bot-flow/<surface>/` (dialog · window · use-case · command · notification) — по папке на bot-поверхность (`type: bot`) из реестра `surface.md`. Организующая ось внутри поверхности — фича (feature): один диалог + его окна + его use-case'ы бота в папке `features/<feature>/`; команды и уведомления — сквозными реестрами на корне. Ведёт сессию заполнения через структурированные вопросы (AskUserQuestion), синтезирует кандидатов из interface-слоя той же поверхности (зона → диалог/фича, блок → окно, атомы → виджеты), держит двухуровневый мост к доменам (виджет и getter окна ссылаются на use-case бота, а тот в зависимостях — на `use-case` домена; `event` — для уведомлений), фиксирует контекст в своей ветке единого дерева state оркестратора (`../entrypoint/state/projects/<project-slug>/telegram-bot-flow/<surface>/`), аккумулирует референсы в `docs/projects/<project-slug>/telegram-bot-flow/<surface>/features/<feature>/assets/<slug>/` и не выдумывает тексты сообщений. Использовать всегда, когда речь о слое телеграм-бота проекта, заполнении одного из 5 артефактных kind (dialog/window/use-case/command/notification) одной bot-поверхности, заведении или углублении фичи/диалога/окна/use-case'а бота/команды/уведомления, разборе сырья (скриншот чужого бота, описание сценария словами, транскрипт интервью), прокладке переходов между окнами и фичами, контракте данных окна (getter), оркестрации действия окна через use-case бота, переходе записи `status: draft → stable`, удалении с каскадом, или копании связей между сущностями telegram-bot-flow, interface той же поверхности и доменами проекта. Также — единственная точка входа в telegram-bot-flow-слой проекта: новые файлы и правки артефактов делаются через этот скилл."
---

# telegram-bot-flow-deep-dive

Углублённая проработка артефактов телеграм-бота **одного проекта**, в
контексте **одной bot-поверхности (surface)** —
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/`. Канон формы —
`docs/projects/_template/telegram-bot-flow/README.md` и каноны в подпапке
`_template/` (`features/README.md` — формы `dialog.md`, `window.md`,
`use-case.md`; `command.md`, `notification.md` — root-реестры). Скилл
ведёт сеанс через структурированные вопросы, фиксирует контекст в своей
ветке единого дерева state оркестратора
(`../entrypoint/state/projects/<project-slug>/telegram-bot-flow/<surface>/`),
не выдумывает тексты сообщений и не лезет в interface-слой того же
проекта своими руками.

Использовать как **единственную точку входа** в telegram-bot-flow-слой
проекта: заведение, углубление, разбор сырья, переход `draft → stable`,
удаление с каскадом.

Слой **партиционирован по поверхности**: каждая поверхность с
`type: bot` из реестра-хребта `docs/projects/<project-slug>/surface.md`
получает свою папку `telegram-bot-flow/<surface>/` — она встаёт на место
`screens/<surface>/` (web-поверхность получает экраны, бот — диалоги).
Внутри поверхности организующая ось — **фича (feature)**: один диалог +
его окна + его use-case'ы бота собраны в папку `features/<feature>/`
(`dialog.md` · `window.md` · `use-case.md`); slug фичи = slug её диалога.
Команды (command) и уведомления (notification) — сквозные реестры **на
корне поверхности**, вне фич. Скилл всегда работает **в контексте одного
проекта и одной bot-поверхности** (см. «Выбор проекта» и «Выбор
поверхности»). Дальше по тексту `<project-slug>` — выбранный проект,
`<surface>` — выбранная поверхность; слой бота —
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/`, interface-слой
той же поверхности —
`docs/projects/<project-slug>/interface/<surface>/`. **Изоляция
двухуровневая**: поверхности изолированы между собой, а внутри поверхности
изолированы и **фичи** — ссылки внутри `features/<feature>/` (окно ↔ диалог
↔ use-case) резолвятся в пределах своей фичи; между фичами — только
`start:<feature>` и сквозные реестры корня. Зеркала с `interface/<surface>/`
— в пределах одной поверхности.

## Выбор проекта

Скилл работает в контексте **одного** проекта. `<project-slug>` —
первый позиционный аргумент, `<surface>` — второй (см. «Выбор
поверхности»):

| вызов | проект |
|---|---|
| `/telegram-bot-flow-deep-dive <project-slug> [<surface>] …` | взять `<project-slug>` |
| `/telegram-bot-flow-deep-dive …` (без slug) | `AskUserQuestion`-пикер **по именам** проектов (исключая `_template`) |

Поскольку точки входа допускают `<kind>:<slug>` (например,
`telegram-bot-flow-deep-dive my-app client-bot feature:booking`),
`<project-slug>` отделяется от остатка как первый токен и/или по
совпадению с именем подпапки `docs/projects/`:

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
   `docs/projects/<project-slug>/telegram-bot-flow/<surface>/`,
   `docs/projects/<project-slug>/interface/<surface>/` (read-only),
   `docs/projects/<project-slug>/domains/` (read-only), ветка state
   `../entrypoint/state/projects/<project-slug>/telegram-bot-flow/<surface>/`.

## Выбор поверхности

Слой живёт **только на bot-поверхностях**. После проекта скилл
определяет `<surface>` — второй позиционный аргумент:

| вызов | поверхность |
|---|---|
| `/telegram-bot-flow-deep-dive <project-slug> <surface> …` | взять `<surface>`, если в реестре она `type: bot` |
| `/telegram-bot-flow-deep-dive <project-slug> …` (без surface) | `AskUserQuestion`-пикер **по именам** bot-поверхностей из реестра `surface.md` |

Алгоритм:

1. Прочитать реестр-хребет
   `docs/projects/<project-slug>/surface.md`; отобрать строки с
   `type: bot`.
2. Если следующий после `<project-slug>` токен совпадает со `slug`
   bot-поверхности из реестра — это `<surface>`; остаток args — точка
   входа. Если токен совпадает с поверхностью **другого типа** —
   сказать «поверхность `<surface>` имеет `type: <type>`; слой
   телеграм-бота живёт только на `type: bot` — для неё работает
   `screens/<surface>/` (`/screen-deep-dive`)», выйти.
3. Иначе — пикер **по именам** bot-поверхностей (опции — `name` из
   `surface.md`; slug и `lives-at` — деталь в описании опции). Аналитик
   slug не вводит — выбирает имя.
   - Если bot-поверхность одна — взять её без вопроса.
   - Если bot-поверхностей в реестре нет — сказать «в реестре
     `surface.md` нет поверхности с `type: bot`; заведи её через
     `/project-deep-dive <project-slug>` (реестр-хребет `surface.md`),
     потом возвращайся», выйти.
4. Если папки
   `docs/projects/<project-slug>/telegram-bot-flow/<surface>/` ещё нет —
   это первый заход на поверхность: scaffold (см. ниже).

Дальше весь сеанс идёт **в пределах одной поверхности**. Сменить
поверхность — это новый запуск скилла с другим `<surface>`.

## Scaffold первого захода

Каталоги руками не создаются в обход скила. При первом заходе на
bot-поверхность скилл создаёт форму папки из канона
`docs/projects/_template/telegram-bot-flow/_template/`: реестры корня
`command.md` и `notification.md` (копии канон-таблиц, очищенные от
строк-образцов — остаётся канон-проза + пустой заголовок таблицы) и
пустую папку `features/`. Папка фичи `features/<feature>/` с файлами
`dialog.md`, `window.md`, `use-case.md` (и `assets/`) создаётся при
заведении первой фичи (= её диалога), не на scaffold'е.

## Точки входа

После того как `<project-slug>` и `<surface>` определены, остаток args
задаёт режим:

| вызов | поведение |
|---|---|
| `/telegram-bot-flow-deep-dive <project-slug> <surface>` | сводка состояния поверхности + топ-3 кандидата на углубление |
| `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>` | завести новую сущность типа kind (режим A) |
| `/telegram-bot-flow-deep-dive <project-slug> <surface> <kind>:<slug>` | завести (если slug ещё не существует) либо углубить (если существует) |
| `/telegram-bot-flow-deep-dive <project-slug> <surface> <slug>` | найти slug; одиночный → C; конфликт kind → переспросить |
| `/telegram-bot-flow-deep-dive <project-slug> <surface> <свободный текст / приложение>` | сырьё → разбор (режим B) |

`kind` ∈ {`dialog`, `window`, `use-case`, `command`, `notification`}.

`dialog`, `window` и `use-case` живут **внутри фичи**
(`features/<feature>/`): диалог — файл `dialog.md`, окно — H2-секция
`## <window-slug>` в `window.md`, use-case бота — H2-секция
`## <uc-slug>` в `use-case.md`. Поскольку фича = один диалог, slug фичи =
slug её диалога. Резолв `window`/`use-case`-точки входа требует **контекста
фичи**: выбор диалога = выбор фичи. Если фича из `<kind>:<slug>` не
определена однозначно — скилл переспрашивает фичу `AskUserQuestion`-пикером
по именам диалогов; `command` и `notification` живут на **корне
поверхности**, вне фич, и контекста фичи не требуют.

Сырьё (режим B) — описание сценария бота словами, скриншот чужого
бота-референса, транскрипт интервью, либо любая их комбинация. Картинки
и URL — обычные content-блоки в сообщении пользователя.

## Что делать сразу при запуске

1. Определить `<project-slug>` (см. «Выбор проекта») и `<surface>` (см.
   «Выбор поверхности»), при первом заходе — scaffold.
2. Прочитать `docs/projects/_template/telegram-bot-flow/README.md` и
   каноны в подпапке `_template/` (`features/README.md` — формы
   `dialog.md`/`window.md`/`use-case.md`; `command.md`, `notification.md`)
   — освежить виджет-язык, контракт getter, форму use-case бота,
   инварианты модели Telegram, anti-patterns.
3. Прочитать `docs/projects/<project-slug>/vision.md`, реестр-хребет
   `surface.md`, файл возможностей поверхности
   `capability/<surface>.md` (если есть) и interface-слой поверхности
   `docs/projects/<project-slug>/interface/<surface>/` +
   `references/interface-context.md` — освежить источник синтеза.
4. Пробежать `docs/projects/<project-slug>/domains/` (если есть):
   контексты, `use-cases/`, `events/` + `references/domain-bridge.md`
   — освежить двухуровневый мост к доменам (use-case бота → доменный
   use-case).
5. Если остаток args пуст — сделать сводку (см. ниже) и через
   `AskUserQuestion` предложить выбор что копать.
6. Если остаток args указывает на сущность — определить kind и режим
   (A/B/C), применить порядок копания из
   `references/field-checklists.md`.

## Сводка состояния (без args)

1. Пройтись по фичам
   `docs/projects/<project-slug>/telegram-bot-flow/<surface>/features/*/`
   (`dialog.md` каждой фичи, секции `## <slug>` в `window.md` и
   `use-case.md`) и реестрам корня `command.md`, `notification.md`.
2. Подсчитать: сколько `draft` / `stable` по каждому kind.
3. Прочитать свою ветку
   `../entrypoint/state/projects/<project-slug>/telegram-bot-flow/<surface>/`
   (если есть) и собрать открытые вопросы — секции `## Открытые
   вопросы`; пометки `**blocker**` приоритетны.
4. Выявить топ-3 «горячих» кандидата по приоритету:
   - draft-записи с `**blocker**`-вопросами;
   - диалоги без `started-by`, окна-тупики, плейсхолдеры без ключа в
     `getter` / ключи без `fallback`, виджеты с `action` на
     несуществующий use-case бота фичи, use-case'ы без `Outputs`;
   - draft-записи, на которые ссылаются stable-соседи (например,
     `dialog.windows` указывает на draft-окно);
   - дыры синтеза: зоны/блоки interface поверхности, ещё не
     воплощённые фичами/окнами (см.
     `references/interface-context.md`).
5. Вывести сводку в чат (с указанием поверхности), предложить через
   `AskUserQuestion` выбрать.

## Три режима

Детали порядка копания по kind — `references/field-checklists.md`.

- **A. Новая сущность**. Args = `<kind>` или `<kind>:<новый-slug>`.
  Сначала — раунд синтеза из interface (для dialog/window: предложить
  кандидата-источник, см. `references/interface-context.md`), затем
  батч `AskUserQuestion` по чек-листам полей; опции — anti-patterns из
  секций `Что <kind> НЕ` соответствующих канонов; свободная форма через
  Other для значений (`name`, `description`, тексты сообщений, подписи
  кнопок). dialog — файл `features/<feature>/dialog.md` (заведение
  диалога заводит и папку фичи); window — H2-секция `## <slug>` в
  `features/<feature>/window.md`; use-case бота — H2-секция `## <slug>`
  в `features/<feature>/use-case.md` (заводится, когда виджету окна нужен
  `action`, см. «Мост к domains»); command и notification — новая строка
  таблицы реестра корня.
- **B. Сырьё**. Args = свободный текст, картинка, URL. Скилл
  анализирует, извлекает кандидатов, через чат показывает план,
  по подтверждению заводит stub'ы и погружается в каждый через
  режим C. Подробности — `references/raw-input.md`.
- **C. Углубление**. Args = `<kind>:<slug>` существующей записи или
  выбор из сводки. Точечные вопросы по дырам и подозрениям (пустые
  слоты, необеспеченные плейсхолдеры, тупики, рассинхрон зеркал, висячие
  доменные рефы); чек-лист `draft → stable` после каждой правки.

## Стиль вопросов

- **Всегда через `AskUserQuestion`**, до 4 вопросов в одном раунде.
- **Опции** только для:
  - anti-patterns из секций `Что <kind> НЕ` («это похоже на
    anti-pattern X — согласен?»);
  - теста-критерия (бинарный выбор ✅/❌ из секций `Тест-критерий`);
  - перечисления enum'ов из канона (`launch-mode`, `stack`, тип
    виджета, `transition: <window>|back|done|start:<feature>`,
    `getter.source: use-case|dialog-data|start-data|const`);
  - выбора существующего slug-соседа (по опции на каждый существующий
    + «нужен новый» через Other);
  - выбора блока/зоны/субстрата/ситуации/роли interface для синтеза и
    рёбер (`interface-block`, `ux-substrates`, `situations`, `who`);
  - выбора use-case бота фичи для `widget.action` / `getter.*.source`
    (`use-case:<uc-slug>`, опция на каждый существующий + «нужен новый
    bot UC») и выбора доменного `use-case:<ctx>.<Operation>` /
    `event:<ctx>.<Event>` из доменов проекта (см.
    `references/domain-bridge.md`).
- **Свободная форма** (через Other) — для **значения**: `name`,
  `description`, текст сообщения (`message.text`), подписи кнопок
  (`label`), тексты `content` и `errors`, условия переходов (`when` —
  формулировка исхода use-case), `payload`, `idempotency`,
  `dialog-data`-контракт, `fallback`.
- **Никогда** не предлагать конкретные тексты доменных значений
  (текст сообщения, подпись кнопки, условие перехода, текст
  уведомления) от себя. Anti-patterns — да. Сама формулировка — нет.

## Идентификаторы: выводит скилл, не аналитик

Аналитик говорит именами; жаргон скилл берёт на себя
(`.claude/rules/naming.md`):

- `slug` — из человекочитаемого `name` (транслит в kebab-case); при
  коллизии — числовой суффикс (slug фичи = slug её диалога; slug окна /
  use-case бота уникален **в пределах фичи**);
- `states-group` диалога (PascalCase, англ., уникален в поверхности) и
  `state` окна (UPPER_SNAKE, англ., уникален в группе) — скилл сам
  предлагает из `name` (смысловой английский корень);
- `operation` use-case бота (PascalCase, англ., из него код строит
  сервис/handler оркестрации) — скилл предлагает из `name`;
- `id` виджета (snake_case, уникален в окне) — из роли виджета.

Каждый идентификатор показывается **одной строкой для контроля**
(«завожу как `booking`, группа состояний — `Booking`, ок?»; для use-case
бота — «завожу `submit-booking`, операция — `SubmitBooking`, ок?»), не как
поле ввода; поправить можно через Other, но аналитик никогда не обязан
придумывать его сам. `slug`, `states-group`, `state` и `operation`
неизменяемы после заведения — их читает код-репо бота; переименование —
отдельный каскад через рефактор-режим оркестратора, не правка руками.

## Память: своя ветка единого дерева state

Скилл не держит своего `state/`. Per-kind заметки пишутся в **свою ветку**
единого дерева state оркестратора, не в
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/` и не в корне
проекта; ветка скоупится по проекту **и поверхности**:

```
../entrypoint/state/projects/<project-slug>/telegram-bot-flow/<surface>/<kind>/<slug>.md
```

Заметки фичевых kind (`dialog`/`window`/`use-case`) ведутся в подпапке
фичи: `…/<surface>/<feature>/<kind>/<slug>.md`; `command`/`notification`
— на корне ветки поверхности.

Формат заметки — канон `../entrypoint/references/state-model.md`. Кратко:

- Файл существует, пока в нём есть хоть одна секция с содержимым.
- Frontmatter: `kind` · `slug` · `ref` (путь к артефакту).
- Три возможные секции (любая может отсутствовать):
  - `## Открытые вопросы` (опц. префикс/суффикс `**blocker**` у вопроса,
    блокирующего stable),
  - `## Доменные решения` (неочевидные смысловые решения, не лезущие
    в `description`; сюда же — доменные требования вида «нужен
    `use-case:<ctx>.<Operation>` в `Dependencies` bot UC», когда домена
    ещё нет),
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
`projects/<project-slug>/telegram-bot-flow/<surface>/` — **rw**, всё
остальное дерево (включая ветки других поверхностей) и клиентский дом —
**read-only**: в чужое не писать. При чтении клиентского дома маркер
`**жду аналитика**` трактуется как blocker-кандидат.

## Ассеты

Референсы (скриншоты ботов-аналогов, мокапы сообщений) живут в папке
ассетов фичи
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/features/<feature>/assets/<slug>/`
(где `<slug>` — окно или use-case бота фичи); имена файлов —
человекочитаемые kebab-case (`competitor-bot-menu.png`,
`booking-confirm-mockup.png`). Папка сущности создаётся при первом ассете
и удаляется вместе с сущностью.

- Входящая картинка от аналитика → скилл анализирует, через
  `AskUserQuestion` решают вместе: (a) сохранить как референс к
  сущности, (b) использовать как сырьё (режим B) и не сохранять.
- Web-поиск референсов — **только по явной просьбе** («найди, как боты
  делают X»). Кандидатов показать через `AskUserQuestion`, выбранное —
  скачать в папку ассетов. Без просьбы скилл в web не лазит.
- Без согласия аналитика картинки в репо не сохраняются.

## Контракт `draft → stable`

См. `references/draft-stable.md`. Чек-лист после каждой правки (6
пунктов):

1. Обязательные слоты frontmatter / колонки таблицы заполнены
   (опциональные могут быть `—`).
2. Все `slug`-ссылки валидны: внутрифичевые рёбра
   (`dialog.windows`, `widget.transition`, `widget.action`,
   `getter.*.source`) — в пределах **своей фичи**
   `…/telegram-bot-flow/<surface>/features/<feature>/`; межфичевые/root
   (`start:<feature>`, `dialog.started-by`, `command.starts`,
   `notification.action`) — по реестрам корня и фичам поверхности;
   interface-рефы — в interface-слое **той же поверхности**
   `docs/projects/<project-slug>/interface/<surface>/`. Доменные рефы
   bot UC (`use-case.Dependencies` → `use-case:<ctx>.<Operation>`) и
   `notification.trigger` (`event:…`) — семантические: при отсутствующем
   домене фиксируются как требование в state, stable не блокируют.
3. Зеркала консистентны:
   - `window.ux-substrates` (мета-блок секции окна) ↔
     `block.ux-substrates` interface-блока `window.interface-block`;
   - `dialog.windows` ↔ множество секций `## <slug>` в `window.md` фичи;
   - `dialog.transitions` (сводка) ↔ поля `transition` на виджетах
     окон фичи;
   - `widget.action` / `getter.*.source` (`use-case:<uc-slug>`) ↔
     секция `## <uc-slug>` в `use-case.md` той же фичи.
4. Тест-критерий из канона соответствующего kind явно подтверждён
   аналитиком в этой сессии.
5. В state-заметке сущности
   (`…/telegram-bot-flow/<surface>/<feature>/<kind>/<slug>.md` для
   фичевых kind, `…/<surface>/<kind>/<slug>.md` для command/notification)
   нет `**blocker**`-вопросов.
6. Тело / строка полные и держат инварианты Telegram (см. ниже):
   `window` — каждый плейсхолдер `{…}` и `items` обеспечен ключом
   `getter` с `fallback`, `action` ссылается на use-case бота фичи или
   отсутствует, `errors` несёт канон-ключи, окно не тупик;
   `use-case` — мета-поля (`name`, `operation`, `who`, `status`) и
   H3-секции (`Actor`/`Inputs`/`Outputs`/`Dependencies`/`Steps`/`Errors`)
   полны, `Outputs` называет исходы для `when` окон, `Steps` без
   бизнес-правил; `dialog` — `dialog-data` описан, `transitions`-сводка
   сходится, из каждого окна есть путь к `done`; `command` — `/start` со
   `stack: reset`, deep-link несёт `payload`; `notification` —
   `trigger` объявлен, `idempotency` непуст, плейсхолдеры `content`
   обеспечены payload'ом триггера.

Если все 6 ✅ — предложить через `AskUserQuestion`: «Готов к stable,
повышаем?». По подтверждению — изменить `status: draft → stable`.
Скилл **не повышает сам**.

Понижение `stable → draft` — только аналитик руками. Скилл максимум
может предложить, не делать.

## Инварианты модели Telegram (держать в ведении)

Скилл проверяет их при каждой правке, а не только на гейте stable:

- **Одно окно = одно сообщение** — серия сообщений как «шаг» разбивается
  на окна или пагинацию внутри одного.
- **Каждый плейсхолдер обеспечен** — правка `message.text` или `items` →
  сразу сверить с `getter`; у каждого ключа обязателен `fallback` (окно
  не падает никогда).
- **`/start` — только `stack: reset`** — `/start` со `stack: push` не
  записывается.
- **`dialog-data` — только JSON-примитивы** — сущности домена и
  даты-объекты в контракт накопления не пишутся.
- **Между фичами — только `start:` / `done`** — `transition` на окно
  чужой фичи не записывается; предлагается `start:<feature>` (войти в
  диалог другой фичи) или пересборка состава окон этой фичи.
- **Уведомление — только с идемпотентностью** — строка без `idempotency`
  или с триггером «когда захотим» не заводится.

## Зеркала interface ↔ telegram-bot-flow

Зеркало `ux-substrates` (M:N) живёт в **двух** слоях **одной и той же
поверхности одного и того же проекта**:

- `docs/projects/<project-slug>/interface/<surface>/block.md` — взгляд
  бизнеса (блок собирает определённые субстраты ситуаций);
- мета-блок секции окна `## <window-slug>` в
  `docs/projects/<project-slug>/telegram-bot-flow/<surface>/features/<feature>/window.md`
  (`ux-substrates: [...]`) — взгляд композиции (окно реализует те же
  субстраты как текст и виджеты).

Канонического источника нет: оба слоя ведут разную работу. При
расхождении скилл **не правит молча**. Алгоритм:

1. После любой правки `ux-substrates` окна или после запуска C-режима
   на окне — сравнить с `block.md` interface (строка
   `window.interface-block`).
2. Если совпадает — ок.
3. Если различаются — через `AskUserQuestion` показать diff и
   спросить: «какой слой брать за источник правды для этого окна?»
   - «вариант бота» → предложить аналитику запустить
     `interface-deep-dive <project-slug> <surface> block:<slug>` и
     подровнять interface;
   - «interface-вариант» → подровнять окно (правка `ux-substrates` в
     мета-блоке его секции здесь) и сверить покрытие виджетами;
   - «оба нужны» → расхождение смысловое, state-заметка
     `**blocker**: ux-substrates расходятся, прояснить смысл окна`.

Скилл **не правит** interface-слой проекта своими руками — это домен
`interface-deep-dive`. Соответствие атомов виджетам (`команда` →
`button`, `ввод` → `text-input`, `выбор` →
`select`/`multiselect`/`calendar`, `инфо`/`список` → текст и `items`) —
`references/interface-context.md`.

### Зеркало transitions внутри слоя

Источник правды графа переходов — поля `transition` на виджетах окон
фичи; `dialog.transitions` — выводимая сводка. После правки переходов
любого окна фичи скилл пересчитывает сводку её диалога и предлагает
обновление (это механический пересчёт, не смысловое решение — но запись
делается явно, не молча).

## Мост к domains

См. `references/domain-bridge.md`. Мост **двухуровневый**: окно касается
домена не напрямую, а через **use-case бота** фичи.

- **Уровень 1 — окно → use-case бота (внутри фичи, slug-валидируемо)**:
  `widget.action` и `getter.*.source` — реф `use-case:<uc-slug>` (без
  точки) на секцию `## <uc-slug>` в `use-case.md` **той же фичи**, либо
  `—` (чистая навигация). Когда виджету окна нужен `action`, а
  подходящего use-case бота в фиче ещё нет — скилл предлагает завести
  его (`slug` + `operation`): опции из существующих bot UC фичи + «нужен
  новый bot UC». Bot UC и есть точка, где композиция мостится к домену.
- **Уровень 2 — use-case бота → доменный use-case (семантически)**: в
  своих `### Dependencies` bot UC ссылается на доменный
  `use-case:<ctx>.<Operation>` (**с точкой**) на
  `docs/projects/<project-slug>/domains/<ctx>/use-cases/`; при заведении
  bot UC — опции из существующих доменных use-case проекта + «нужна
  новая операция». Точка различает уровни: реф без точки — bot UC, с
  точкой — доменный.
- условие перехода `when` на виджете — **исход use-case бота** (его
  `### Outputs`/`### Errors`), не правило, придуманное окном; скилл
  показывает исходы как контекст, формулировку даёт аналитик.
- `notification.trigger` — `event:<ctx>.<Event>` из
  `domains/<ctx>/events/` (опции из существующих), `schedule: <по-русски>`
  или `integration:<slug>` из `integration.md` проекта (без изменений —
  уведомление триггерится доменным событием напрямую).
- Если доменного слоя нет (или нужного контекста/операции/события ещё
  нет) — доменная связь **семантическая** и фиксируется на уровне bot UC:
  имя пишется в `### Dependencies` как есть, а в state-заметке bot UC
  (`## Доменные решения`) — строка-требование «нужен
  `use-case:<ctx>.<Operation>` — для <зачем>» + предложение
  `/domain-deep-dive <project-slug> <ctx>`. Stable это не блокирует;
  несостыковки сводит `/cross-audit`.

Скилл **не пишет** в `domains/` — это домен `domain-deep-dive`.

## Stub-сущности

### Внутри telegram-bot-flow

Внутрифичевые рефы (окно в `dialog.windows`, use-case бота в
`widget.action` / `getter.*.source`) резолвятся **в пределах своей
фичи**; межфичевые/root (фича в `command.starts` или
`transition: start:<feature>`, команда в `notification.action`) — по
реестрам корня и фичам поверхности. Если копаемая сущность ссылается на
не существующий slug:

1. Завести stub:
   - окно — H2-секция `## <slug>` в `window.md` **той же фичи** с
     минимальным мета-блоком (`name` + `state` + `status: draft` +
     обязательные поля с `—` где допустимо);
   - use-case бота — H2-секция `## <slug>` в `use-case.md` **той же
     фичи** с минимальным мета-блоком (`name` + `operation` +
     `status: draft`) и пустыми/`—` H3-секциями;
   - фича/диалог (новый `start:<feature>`) — папка `features/<feature>/`
     с `dialog.md` (минимальный frontmatter `slug + name + description +
     status=draft` + обязательные поля с `—`) и пустыми `window.md` /
     `use-case.md`;
   - command/notification — строка таблицы реестра корня с `—` в
     незаполненных колонках.
2. В state-заметке stub'а — секция `## Открытые вопросы` с записью
   «Заведён как stub в контексте `<откуда сослались>` — докопать».
3. Возврат в исходную сущность, копание продолжается.

### Stub-зависимость на interface-slug

Если `window.interface-block` / `ux-substrates` / `situations` / `who` /
`getter.*.data` (`data:<slug>`) указывает на не существующий
interface-slug **той же поверхности**:

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
   - «удалить эту ссылку» (если поле допускает) → правка слоя бота;
   - «заменить на существующий slug» (показать варианты) → правка.

## Удаление сущности (каскад)

1. Прочитать все 5 kind поверхности (фичи
   `features/*/{dialog.md, window.md, use-case.md}` + реестры корня
   `command.md`, `notification.md`) + свою ветку state — найти все
   ссылки на удаляемый slug: `dialog.windows`, `started-by`,
   `widget.transition` (включая `start:<feature>`), `widget.action`,
   `getter.*.source`, `command.starts`, `notification.action`. Также
   проверить папку ассетов фичи
   `…/features/<feature>/assets/<slug>/`.
2. Показать каскад: «ссылаются X, Y, Z — вот что сломается». Удаление
   фичи/диалога тянет все её окна и use-case'ы (вся папка
   `features/<feature>/`) — показать их списком отдельно. Удаление
   use-case бота тянет `widget.action` / `getter.*.source`, которые на
   него ссылались.
3. Через `AskUserQuestion` по каждому месту — опции: «заменить на
   другой slug» / «поставить `—` (если поле допускает)» / «удалить
   ссылающуюся запись».
4. По подтверждению — выполнить все правки одним пакетом: удалить
   артефакт (папку `features/<feature>/` целиком — при удалении фичи;
   H2-секцию `## <slug>` в `window.md` / `use-case.md` — при удалении
   окна / use-case; строку таблицы реестра — при удалении
   command/notification), его папку ассетов и state-заметку, если
   существуют.
5. Пересчитать сводки `transitions` затронутых диалогов и зеркала
   `dialog.windows`.

## Завершение сессии

В конце:

1. Перечислить затронутые сущности (заведены / углублены / удалены).
2. Перечислить нерешённые открытые вопросы по сущностям (с указанием
   `**blocker**`-меток) и накопленные доменные требования (нужные
   доменные use-case в `Dependencies` bot UC / event уведомлений без
   домена).
3. Предложить через `AskUserQuestion`: «Прогнать
   `/telegram-bot-flow-audit <project-slug> <surface>`?» — это аудит
   консистентности слоя поверхности и зеркал с её interface. По «да»
   сказать пользователю «Запусти
   `/telegram-bot-flow-audit <project-slug> <surface>`» — сам не
   вызываю, это другой скилл.

## Запреты

- Не редактировать артефакты вслепую — всегда сначала `Read`.
- Не выдумывать значения доменных полей. Anti-patterns как опции — да;
  тексты сообщений, подписи кнопок, условия переходов, тексты
  уведомлений, `name`, `description` — нет.
- Не писать код в артефактах: имена python-файлов, классы виджетов,
  `.ftl`-ключи, callback-строки — забота код-репо.
- Не описывать облик: эмодзи-оформление, HTML/Markdown-разметка,
  «жирная кнопка» — забота кода и контента.
- Не класть бизнес-правила в `when` или в `Steps` use-case бота —
  условие перехода формулируется как исход use-case бота, а тот лишь
  оркеструет; ветвление по бизнес-правилу решает домен.
- Не давать `widget.action` работать мимо use-case бота («кнопка сама
  сохраняет в базу») — действие ссылается на `use-case:<uc-slug>` фичи
  или отсутствует; в домен ходит bot UC через свои `Dependencies`.
- Не путать уровни рефа: `use-case:<uc-slug>` без точки — use-case бота
  (внутри фичи), `use-case:<ctx>.<Operation>` с точкой — доменный (в
  `Dependencies` bot UC).
- Не нарушать инварианты модели Telegram (см. выше) — ни в заведении,
  ни в правке; исходящее сообщение — только через реестр корня
  `notification.md`.
- Не лезть в interface-слой проекта
  (`docs/projects/<project-slug>/interface/<surface>/`) и в `domains/`
  своими руками — только через предложение аналитику запустить
  `interface-deep-dive` / `domain-deep-dive`.
- Не создавать папку `telegram-bot-flow/<surface>/` для поверхности вне
  реестра `surface.md` или с `type` ≠ `bot` — хребет ведёт реестр.
- Не работать сразу с несколькими проектами или поверхностями в одной
  сессии — скилл скоупится в один `<project-slug>` и одну `<surface>`;
  ссылка из одной поверхности в сущность другой запрещена (поверхности
  изолированы). Смена поверхности — новый запуск.
- Не ссылаться из одной фичи в окно/use-case другой минуя
  `start:<feature>` / `command` — фичи изолированы так же, как
  поверхности; внутрифичевые рефы (окно ↔ диалог ↔ use-case) резолвятся
  только в пределах своей фичи.
- Не заводить несколько диалогов в одной фиче — вложенный сценарий
  выносится в отдельную фичу, вход через `start:<feature>`.
- Не просить аналитика придумывать `slug` / `states-group` / `state` /
  `operation` / `id` — идентификаторы выводит скилл, аналитик
  контролирует одной строкой.
- Не повышать `draft → stable` без явного подтверждения аналитика.
- Не понижать `stable → draft` сам — только подсветить и предложить.
- Не править `window.ux-substrates` молча при рассинхроне с interface —
  всегда переспрашивать источник правды.
- Не лазить в web без явной просьбы аналитика.
- Не сохранять входящие картинки в `assets/` без согласия аналитика.
- Не вызывать `telegram-bot-flow-audit` самостоятельно — только
  предложить.
- Не аккумулировать историю в своей ветке state — forward-only.
- Не создавать
  `../entrypoint/state/projects/<project-slug>/telegram-bot-flow/<surface>/<kind>/<slug>.md`,
  если все секции были бы пустыми — заметка появляется только когда есть
  что записать.
- Не писать в чужие ветки дерева `../entrypoint/state/` (включая ветки
  других поверхностей) и в клиентский дом
  `../entrypoint-for-business/state/` — только read-only; rw только своя
  ветка `projects/<project-slug>/telegram-bot-flow/<surface>/`.
