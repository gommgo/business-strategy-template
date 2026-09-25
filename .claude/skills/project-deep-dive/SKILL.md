---
name: project-deep-dive
description: "Углублённая проработка продуктового слоя одного проекта в `docs/projects/<project-slug>/` (vision · реестр поверхностей surface · user · capability по поверхности · boundary · integration · constraint · market) и заведение нового проекта. Принимает `<project-slug>` первым аргументом; без него — пикер по именам проектов или новый проект. Ведёт аналитика по 8 фазам вижн-мейкинга через `AskUserQuestion`, по его решению запускает рой web-research конкурентов и регуляторики, домен не выдумывает и маркетинговую копию не пишет; заметки — в ветке `../entrypoint/state/projects/<project-slug>/project/`. Использовать для любой работы с продуктовым слоем проекта: вижн продукта, разбор интервью с бизнесом, пользователи, поверхности, возможности, интеграции и стыки с соседними проектами, ограничения, рыночные аналоги, границы продукта, переход записи draft → stable. Единственная точка входа аналитика в продуктовый слой проекта; interface, screens, services и другие слои проекта ведут свои скиллы."
---

# project-deep-dive

Углублённая проработка продуктовых артефактов **одного проекта** в
`docs/projects/<project-slug>/`. Канон формы —
`docs/projects/_template/project/README.md` (форма живёт один раз в
`_template/`; данные каждого проекта — в его папке). Скилл ведёт сеанс
через 8 фаз вижн-мейкинга, структурированные вопросы
(`AskUserQuestion`), фиксирует контекст в своей ветке единого дерева
state оркестратора (`../entrypoint/state/projects/<project-slug>/project/`),
не выдумывает домен и не пишет маркетинговую копию.

**Поверхность (surface) — ось продукта.** Реестр-хребет `surface.md`
объявляет поверхности (web, mobile, бот, API, админка …), и их slug'и —
ключи партиционирования: каждая поверхность получает свой файл
возможностей `capability/<surface>.md`. Возможность (capability) живёт
**не плоским файлом**, а в папке `capability/`, по файлу на поверхность;
связь capability → surface **структурная** (файл = поверхность).
Остальные kind — плоские кросс-поверхностные таблицы в корне проекта.

Использовать как **единственную точку входа** в продуктовый слой
проекта для аналитика: выбор/заведение проекта, заведение, углубление,
разбор сырья, фаз-навигация, переход `draft → stable`, удаление с
каскадом, market/constraint research через рой агентов.

## Мультипроект: выбор контекста

Шаблон держит **несколько проектов** под одним бизнесом, каждый — папка
`docs/projects/<project-slug>/` (см. `docs/projects/README.md`). Все
чтения и записи скилла **скоупятся в один выбранный проект**.

- `/project-deep-dive <project-slug> …` — первый аргумент задаёт
  проект; остальные args — kind / slug / сырьё / флаги.
- Без `<project-slug>` — скилл строит пикер через `AskUserQuestion` по
  существующим проектам, **исключая `_template`** (это образец формы, не
  проект). Опции — **человекочитаемые имена** проектов (заголовок из
  `vision`; slug — мелкой деталью в описании) + «Завести новый проект».
  slug аналитик не вводит (см. `.claude/rules/naming.md`).
- Если переданный slug не существует среди папок — переспросить через
  `AskUserQuestion`: «Проекта `<slug>` нет. Завести новый / выбрать из
  существующих?».

Внутри сессии выбранный `<project-slug>` фиксируется и подставляется во
все пути: `docs/projects/<project-slug>/vision.md`,
`docs/projects/<project-slug>/surface.md`,
`docs/projects/<project-slug>/user.md`,
`docs/projects/<project-slug>/capability/<surface>.md`, … и в ветку state
(`../entrypoint/state/projects/<project-slug>/project/…`).

### Заведение нового проекта

Новый проект = **копия формы** из `docs/projects/_template/project/` в
новую папку `docs/projects/<new-slug>/`. Каталоги руками не плодим —
скаффолдит скилл:

1. Спросить **человекочитаемое имя** продукта (свободный текст). `slug`
   вывести самому из имени (транслит в kebab-case, при коллизии — суффикс)
   и показать одной строкой для контроля — аналитик kebab-case не
   придумывает (см. `.claude/rules/naming.md`).
2. Скопировать форму из `docs/projects/_template/project/` в
   `docs/projects/<new-slug>/`:
   - `vision.md` (singleton);
   - 6 плоских кросс-поверхностных kind-файлов: `surface.md`, `user.md`,
     `integration.md`, `boundary.md`, `constraint.md`, `market.md`.
   - `capability` **не плоский файл**: создаётся **папка** `capability/`.
     Сам файл `capability/<surface>.md` заводится **под каждую
     поверхность** из формы `_template/project/capability.md` позже — в
     фазах `surface`/`capability`, когда реестр `surface.md` уже знает
     поверхность. На скаффолде capability-файлов ещё нет (нет поверхностей).
   - Канон-README **не** копируется — форма живёт один раз в `_template/`.
3. Зайти в фазу `discovery` на свежем `vision.md` нового проекта.

Соседние слои (`<new-slug>/interface/`, `<new-slug>/screens/` — либо, по
`type` поверхности, `telegram-bot-flow/` и `mobile/`, —
`<new-slug>/services/` — топология сервисов через `/service-deep-dive`,
домены внутри сервисов через `/domain-deep-dive <slug> <ctx>`) заводят
свои скилы по мере надобности — этот
скилл их не создаёт.

## Вышестоящий вход (реестр проблем, SWOT, Карта гипотез)

Продукт — **не корень всего**, а решение под уже формализованную
бизнес-проблему. Над папками проектов лежат `docs/business/` (профиль
бизнеса + реестр проблем `business-problem.md`), `docs/swot/` (LinkedSWOT)
и `docs/hypothesis-map/` (Карта гипотез) — **общие для всех проектов**
верхние слои. Якоря для discovery приходят оттуда (связь семантическая,
не slug):

- `vision.Problem` ← `docs/business/business-problem.md` (строки-проблемы)
  + `hypothesis-map/goal`;
- `vision.Success` ← `docs/hypothesis-map/metric` (целевые метрики —
  best-effort таргет, **не** гарантия; не копировать как обещание);
- `user` ← `docs/hypothesis-map/subject` (субъект влияния) и
  `docs/ajtbd/segment` (сегмент по работам Advanced JTBD);
- `capability` реализует `docs/swot/bet` / `hypothesis-map/goal`;
  авторски `capability.hypotheses` (→ `hypothesis-map`) и `capability.jobs`
  (→ `ajtbd`) ведутся здесь, на стороне продукта.

Если эти слои есть — на фазе `discovery` сначала прочитать
`docs/business/business-problem.md` + `hypothesis-map/goal.md` +
`hypothesis-map/metric.md` и предложить аналитику опереть vision на них.
Их нет — discovery идёт как обычно. Несостыковки ловит `/cross-audit`.

### `addresses-problem` — какие проблемы закрывает продукт

`docs/business/business-problem.md` — реестр проблем (одна строка = одна
проблема), **общий** для всех проектов. Каждый проект объявляет, какие из
них закрывает, полем `addresses-problem` в своём `vision.md` (массив
slug-рефов на строки реестра; связь M:N — проблему могут бить несколько
проектов, проект — несколько проблем). Авторская сторона связи — здесь;
обратную сводит `/cross-audit`.

На фазе `discovery` скилл добивает `addresses-problem` (см.
`references/phases.md`, фаза 1, и `references/field-checklists.md`):
без привязки продукт висит в воздухе, а `success` не во что целить.
Привязка приходит **от аналитика** через `AskUserQuestion` — скилл
показывает существующие строки реестра `business-problem.md` как опции и
проблемы не придумывает.

## Точки входа

Первый позиционный аргумент — **всегда `<project-slug>`** (контекст
проекта). Дальше — kind / slug / сырьё / флаги.

| вызов | поведение |
|---|---|
| `/project-deep-dive` | пикер проекта → затем сводка состояния по фазам |
| `/project-deep-dive <slug>` | если `<slug>` — папка проекта: сводка по фазам; иначе — пикер с предложением завести новый |
| `/project-deep-dive <project-slug> <kind>` | завести новую сущность типа kind (режим A) |
| `/project-deep-dive <project-slug> <kind>:<entity-slug>` | углубить существующую запись (режим C) |
| `/project-deep-dive <project-slug> capability:<surface>:<entity-slug>` | возможность в файле поверхности `<surface>` (режим A/C) |
| `/project-deep-dive <project-slug> <entity-slug>` | найти entity-slug; одиночный → C; конфликт kind → переспросить |
| `/project-deep-dive <project-slug> <свободный текст / транскрипт>` | сырьё → разбор (режим B) |
| `/project-deep-dive <project-slug> --phase <name>` | принудительно работать в указанной фазе |
| `/project-deep-dive <project-slug> --research <kind>:<query>` | запустить рой агентов на тему |
| `/project-deep-dive --new` | завести новый проект из формы `_template/project/` (спросит имя, slug выведет сам) |

`kind` ∈ {`vision`, `surface`, `user`, `capability`, `integration`,
`boundary`, `constraint`, `market`}. `vision` — singleton; `surface`,
`user`, `integration`, `boundary`, `constraint`, `market` — 6 плоских
кросс-поверхностных таблиц в корне проекта; `capability` — **папка**
`capability/`, файл на поверхность (`capability/<surface>.md`). Для
capability нужна поверхность: без явного `<surface>` скилл показывает
пикер по реестру `surface.md`.

`phase` ∈ {`discovery`, `user`, `surface`, `capability`,
`integration`, `constraint`, `market`, `cohesion`}. Порядок неслучаен:
`surface` идёт **перед** `capability` — хребет вперёд, возможности
партиционируются по поверхностям.

Если первый аргумент совпал с именем папки в `docs/projects/` (кроме
`_template`) — это `<project-slug>`. Если нет — скилл показывает пикер
проекта (см. «Мультипроект»), а уже выбранный проект применяет к
остальным args.

## Что делать сразу при запуске

1. **Определить проект.** Разобрать первый аргумент как `<project-slug>`;
   если не задан или не совпал с папкой — пикер **по именам** проектов
   (исключая `_template`) + опция «Завести новый». Зафиксировать выбранный
   `<project-slug>` на всю сессию.
2. Прочитать `docs/projects/_template/project/README.md` — освежить канон
   (vision + реестр-хребет `surface.md` + 5 плоских kind +
   папка `capability/<surface>.md`) и связи (форма-образец).
3. Прочитать `references/phases.md` — карту 8 фаз.
4. Если за `<project-slug>` нет других args — сделать **сводку по
   фазам** для этого проекта (см. ниже) и через `AskUserQuestion`
   предложить выбор: продолжить текущую фазу / перепрыгнуть / разобрать
   сырьё / запустить research.
5. Если args указывают на сущность — определить kind и режим (A/B/C),
   применить маршрут из `references/workflow-patterns.md`.
6. Если `--research` — перейти к `references/research-rays.md`.
7. Если `--phase` — открыть карту фазы из `references/phases.md`.
8. Если `--new` или выбрана опция «Завести новый» — скаффолд нового
   проекта (см. «Заведение нового проекта»), затем фаза `discovery`.

## Сводка состояния (без args)

Скилл всегда даёт аналитику **карту, где он находится в воркфлоу**, а не
просто список draft-записей.

1. Прочитать `docs/projects/<project-slug>/vision.md` + плоские
   kind-файлы (`surface.md`, `user.md`, `integration.md`, `boundary.md`,
   `constraint.md`, `market.md`) + все файлы папки `capability/` (по
   файлу на поверхность).
2. Подсчитать: `draft` / `stable` по каждому kind, плюс существует ли
   vision (если нет — текущая фаза = `discovery`). Для capability считать
   **по поверхностям**: какие поверхности реестра уже имеют файл
   `capability/<surface>.md` и сколько в нём записей, у каких файла ещё нет.
3. Прочитать свою ветку
   `../entrypoint/state/projects/<project-slug>/project/` (rw) + read-only
   всё дерево `../entrypoint/state/` (проектные ветки — только по текущему
   `<project-slug>`) и клиентский дом `../entrypoint-for-business/state/`,
   если каталоги существуют — см. «Единый контекст» — собрать открытые
   вопросы, особенно `**blocker**`.
4. Определить **текущую фазу** по дереву:
   - vision не существует или status:draft → `discovery`;
   - user-таблица пустая → `user`;
   - surface-реестр пустой → `surface`;
   - реестр surface непустой, но есть поверхность без файла
     `capability/<surface>.md` или этот файл пуст → `capability`;
   - integration пустая → `integration`;
   - constraint пустая → `constraint`;
   - market пустая → `market`;
   - все заполнены, но есть draft-записи или blocker-вопросы → `cohesion`.

   Фаза `capability` **не стартует без `surface`**: если реестр пуст,
   текущая фаза — `surface`, а не `capability` (нет поверхностей —
   некуда партиционировать возможности).
5. Вывести сводку в чат (capability — построчно по поверхностям реестра):

   ```
   Проект: <project-slug>
   Текущая фаза: <name> (<n>/<N>)
   docs/projects/<project-slug>/ покрытие:
     vision         [draft]  (addresses-problem: 1)
     user        3 stable, 1 draft
     surface        2 (web-partner, tg-bot)
     capability/
       web-partner  2 draft
       tg-bot       — (файла ещё нет)
     integration    —
     constraint     —
     market         —
     boundary       1 stable
   Открытых blocker-вопросов: 2
   Готов клиент-черновик в ветке: client  (если есть)
   ```

6. Через `AskUserQuestion` (до 4 опций) предложить:
   - продолжить фазу `<name>` — что копать первым;
   - перепрыгнуть в фазу `<other>` (с обоснованием);
   - разобрать сырьё (вставит свободным текстом / транскриптом);
   - запустить research-рой по теме.

## Фазы проработки

Скилл проактивно ведёт через 8 фаз. Полная карта фаз —
`references/phases.md`. Кратко, по порядку:

| фаза | цель | артефакты на выходе |
|---|---|---|
| `discovery` | vision.md draft → stable; первое касание проблемы и успеха | `vision.md` |
| `user` | сегменты пользователей/клиентов | `user.md` |
| `surface` | где продукт «торчит наружу» — реестр-хребет | `surface.md` |
| `capability` | бизнес-возможности верхнего уровня, **по каждой поверхности** | `capability/<surface>.md` (по файлу на поверхность реестра) |
| `integration` | внешние системы и стыки с соседями: провайдеры + их функции (бизнес-каталог) | `integration.md` (`## Провайдеры` + `## Функции`) |
| `constraint` | регуляторика / SLA / контракты | `constraint.md` |
| `market` | конкуренты и аналоги (с роем агентов) | `market.md` |
| `cohesion` | boundary + сквозная проверка, что слой целостен | `boundary.md`, повышение `draft → stable` |

`surface` идёт **перед** `capability`: реестр-хребет — ось, а
возможности партиционируются по поверхностям (`capability/<surface>.md` —
по файлу на каждую поверхность реестра). Без поверхностей capability-фаза
не стартует.

Порядок — рекомендация, не закон: аналитик может перепрыгнуть. В начале
каждой сессии скилл напоминает, какая фаза сейчас и почему, а после
каждого артефакта предлагает логичный следующий шаг с обоснованием (см.
`references/phases.md`, переходы).

## Три режима

Детали сценариев, примеры вопросов, stub-сущности и удаление с каскадом —
`references/workflow-patterns.md`. Режимы зеркалят interface-deep-dive:

- **A. Новая сущность**. Args = `<project-slug> <kind>` или
  `<project-slug> <kind>:<новый-slug>`. Батч `AskUserQuestion` по
  `Критерии <kind>` из соответствующего md-файла канона; опции —
  anti-patterns из `Что <kind> НЕ`; свободная форма через Other для
  значений.
- **B. Сырьё**. Args = `<project-slug>` + свободный текст или транскрипт
  интервью с бизнесом. Извлечь кандидатов по слоям (user / surface /
  capability с привязкой к поверхности / integration / constraint /
  market), показать план, по подтверждению завести stub-строки (capability
  — в файл своей поверхности), погрузиться в каждую через C.
- **C. Углубление**. Args = `<project-slug> <kind>:<slug>` или выбран из
  сводки. Точечные вопросы по дырам и подозрениям; чек-лист
  `draft → stable` после каждой правки.

Ссылка на ещё не заведённую сущность (capability упомянула user, которой
нет) отрабатывается stub-записью в её файле и открытым вопросом в
state-заметке; удаление сущности — каскадом по всем её семантическим
упоминаниям в слое. Оба сценария — в `references/workflow-patterns.md`,
разделы «Stub-сущности» и «Удаление сущности (каскад)»; открой их, когда
до них дошло.

## Стиль вопросов

См. `references/workflow-patterns.md` (раздел «Стиль вопросов»). Краткий
канон:

- **Всегда через `AskUserQuestion`**, до 4 вопросов в одном раунде.
- **Опции** только для:
  - anti-patterns из секции `Что <kind> НЕ` («это похоже на anti-pattern
    X — согласен?»);
  - теста-критерия (бинарный выбор ✅/❌ из секции `Тест-критерий`);
  - структурного перечисления (enum типа `surface.type`,
    `integration.direction`, `constraint.kind`);
  - выбора существующего slug соседа («связать с user X / Y / нужен
    новый»).
- **Свободная форма** (через Other) — для **значения**: `name`,
  `description`, `value`, `jobs`, `pains`, `why`, `payload`, `source`,
  имена ключевых ролей и систем.
- Тексты доменных полей скилл не предлагает от себя: их даёт аналитик, а
  догаданная формулировка стала бы ложным фактом для всех, кто читает
  продуктовый слой (`CLAUDE.md` §3). Anti-patterns опциями — да, сама
  формулировка — нет.

## Память: своя ветка единого дерева state

Скилл не держит своего `state/`. Per-kind заметки пишутся в **свою ветку**
единого дерева state оркестратора:

```
../entrypoint/state/projects/<project-slug>/project/<kind>/<slug>.md
```

Для `vision` — singleton:
`../entrypoint/state/projects/<project-slug>/project/vision.md`.

Для `capability` заметки скоупятся **по поверхности** (capability —
папка по surface), чтобы возможности разных поверхностей не сталкивались:
`../entrypoint/state/projects/<project-slug>/project/capability/<surface>/<slug>.md`.

Дополнительный каталог
`../entrypoint/state/projects/<project-slug>/project/research/` — для
отчётов роя агентов (см. `references/research-rays.md`).

Скоуп по проекту не даёт state разных продуктов сталкиваться: каждый
проект — своя ветка `projects/<project-slug>/` в дереве (изоляция
продуктов сохраняется).

Формат заметки — канон `../entrypoint/references/state-model.md`. Кратко:

- Файл существует, пока в нём есть хоть одна секция с содержимым.
- Frontmatter: `kind` · `slug` · `ref` (путь к строке артефакта).
- Три возможные секции (любая может отсутствовать):
  - `## Открытые вопросы` (опц. префикс/суффикс `**blocker**` — блокирует
    переход `draft → stable`);
  - `## Доменные решения` (неочевидные смысловые решения, не лезущие в
    `description`);
  - `## Что копать дальше`.
- Forward-only: не аккумулировать «было/стало».
- Если все секции пустые — заметку удалить.

### Единый контекст: read-only видимость дерева

Для единой картины скилл **read-only** подтягивает всё дерево state
оркестратора `../entrypoint/state/` (срез `index.md`, открытые нити
`threads/`, верхнеуровневые слои `business/`, `ajtbd/`, `swot/`,
`hypothesis-map/`) и клиентский дом
`../entrypoint-for-business/state/` (что клиент наработал в режиме
«домашнее задание»). Проектные ветки `projects/<…>/` читаются **только по
текущему `<project-slug>`** (изоляция продуктов сохраняется).

Своя ветка — **rw**, всё остальное дерево и клиентский дом — **read-only**:
в чужое не писать. При чтении клиентского дома маркер `**жду аналитика**`
трактуется как blocker-кандидат. Если клиент прислал черновик через push в
единую ветку `client` — этот state появляется в файловой системе после
merge / fetch, обычная git-механика.

## Семантические связи (без жёстких slug-валидаций)

В отличие от `<project-slug>/interface/<surface>/`, продуктовый слой
**не валидирует** slug-ссылки между записями — кроме **одной структурной
оси**: поверхность. Файл `capability/<surface>.md` обязан соответствовать
строке реестра `surface.md` (имя файла = slug поверхности), а
`integration.surface` ссылается на поверхности реестра. Остальные связи
семантические:

- `user.slug` упоминается в `surface.user` и в `capability/<surface>.md`
  → колонка `user` — но и без явного поля-связи запись может быть валидна;
- `capability` без user — не ошибка, но подозрительно (повод
  поднять при cohesion);
- `surface` без user — мёртвая, повод задать вопрос;
- `integration → surface`: интеграция обслуживает поверхности (массив
  slug-рефов в реестр); `integration → соседний проект` при
  `target: sibling-project` (поле `sibling-project`); `функция → провайдер`:
  каждая строка `## Функции` несёт `integration` существующего провайдера;
- `функция → клиент/потребление`: `slug` функции встречается в клиенте
  `services/_shared/integrations/<integration>/` и в `functions` use-case'а
  (семантически, ловит `/cross-audit`);
- `constraint` обычно привязан к surface или integration в `description`,
  не отдельным полем.

`/project-audit <project-slug>` ловит **внутрипроектные** тупики
(пустые обязательные слоты, draft без якоря, структурный разрыв хребта:
`capability/<surface>.md` для поверхности вне реестра, поверхность
реестра без файла возможностей). `/cross-audit` ловит **между-слойные**
несостыковки (user без покрытия в `<slug>/interface/<surface>/who` и т.п.,
продукт против `addresses-problem`, межпроектные стыки против
`project-map.md`). Сам project-deep-dive — **не аудитор**; в конце сессии
предложит запустить один из них.

## Контракт `draft → stable`

См. `references/draft-stable.md`. Чек-лист после каждой правки:

1. Обязательные слоты заполнены (опциональные могут быть `—`).
2. `Критерии <kind>` пройдены — аналитик подтвердил в этой сессии через
   `AskUserQuestion`.
3. `Что <kind> НЕ` — не нарушены (anti-patterns исключены).
4. `Тест-критерий` ✅ — аналитик явно подтвердил пример своего случая.
5. В соответствующей state-заметке нет `**blocker**`-вопросов
   (`../entrypoint/state/projects/<project-slug>/project/<kind>/<slug>.md`;
   для capability — `…/project/capability/<surface>/<slug>.md`).

Если все 5 ✅ — предложить через `AskUserQuestion`: «Готов к stable,
повышаем?». По подтверждению — изменить `status: draft → stable`. Скилл
**не повышает сам**. Понижение `stable → draft` — только аналитик
руками.

## Web-research через рой агентов

Основной источник кандидатов для `market` и `constraint`, подспорье для
`integration` и `surface`. Запускается только по решению аналитика через
`AskUserQuestion` (дефолт — 5 агентов, аналитик может поменять): рой
параллельных агентов с WebSearch/WebFetch смотрит тему под разными
углами, скилл сводит отчёты в
`../entrypoint/state/projects/<project-slug>/project/research/<query-slug>-<UTC-ts>.md`
и раскладывает кандидатов по kind. В `docs/projects/<project-slug>/`
кандидат попадает только после решения аналитика в `AskUserQuestion`:
находки веба бывают неточными или выдуманными, и без проверки они стали бы
фактами продукта. Углы, промпт агента и формат сводки —
`references/research-rays.md`.

## Завершение сессии

В конце:

1. Перечислить затронутые сущности (заведены / углублены / удалены /
   повышены в stable).
2. Перечислить нерешённые открытые вопросы.
3. Назвать текущую фазу и логичный следующий шаг.
4. Предложить через `AskUserQuestion`:
   - «Прогнать `/project-audit <project-slug>`?» (внутрипроектная
     консистентность);
   - «Прогнать `/cross-audit`?» (сквозная проверка продукта с
     `<slug>/interface/<surface>`/`<slug>/services`/`<slug>/screens/<surface>`,
     привязкой `addresses-problem` и межпроектными стыками `project-map.md`);
   - «Передать клиенту через `/entrypoint-for-business` блок
     <X>?» (если фаза подходит под бизнес-домашку).

Скилл **сам не вызывает** другие скилы — это разные точки входа.
Аналитик запускает.

## Границы

- Один проект за сессию: пути и ветка state скоупятся в выбранный
  `<project-slug>`, поэтому артефакты и заметки разных продуктов не
  смешиваются.
- Значения доменных полей (`description`, `value`, `jobs`, `pains`, `why`,
  `payload`, `source`) и привязку `addresses-problem` даёт аналитик
  (`CLAUDE.md` §3); скилл спрашивает и предлагает anti-patterns опциями.
- Возможности живут только в `capability/<surface>.md` поверхностей из
  реестра `surface.md`: плоского `capability.md` в данных проекта нет, а
  файл для поверхности вне реестра не заводится — хребет ведёт реестр.
- Статус записи меняет аналитик: `draft → stable` — по его подтверждению
  после чек-листа, `stable → draft` скилл только подсвечивает.
- Пишет скилл в `docs/projects/<project-slug>/` и в свою ветку state;
  находки research-роя попадают в артефакты только через
  `AskUserQuestion`.
