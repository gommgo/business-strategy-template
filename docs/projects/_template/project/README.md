# Артефакты продукта

Продуктовый слой проекта живёт в `docs/projects/<project-slug>/`. Этот файл
— **канон формы** (`_template/project/`); данные каждого проекта живут в его
папке. Состав слоя:

- **1 singleton** `vision.md` — корневой документ продукта.
- **реестр-хребет** `surface.md` — поверхности продукта. Его slug'и —
  **ключи партиционирования**: каждая поверхность получает свой файл
  возможностей `capability/<surface>.md`, свою папку интерфейса
  `interface/<surface>/` и свою папку композиции — экранов
  `screens/<surface>/` либо, при `type: bot`, диалогов
  `telegram-bot-flow/<surface>/`.
- **папка возможностей** `capability/<surface>.md` — таблица возможностей
  одной поверхности (по файлу на поверхность).
- **5 плоских кросс-поверхностных таблиц** `user.md`, `integration.md`,
  `boundary.md`, `constraint.md`, `market.md`.

Все связи между сущностями — через `slug`, но консистентность по слою —
**семантическая**, не структурная (см. `/cross-audit`). Единственная
структурная ось — поверхность (`surface`): её slug = имя файла/папки.

Чистая продуктовая аналитика. На код / FSD / компонент не мапится — это
вход для соседних слоёв того же проекта, **вложенных в его папку**:
`<slug>/interface/<surface>/` (UX по поверхности, `/interface-deep-dive`),
`<slug>/screens/<surface>/` (композиция экранов по поверхности,
`/screen-deep-dive`), `<slug>/telegram-bot-flow/<surface>/` (композиция
диалогов bot-поверхности), `<slug>/services/` (сервисная топология бэкенда,
`/service-deep-dive`; домены по bounded-context внутри сервисов —
surface-агностичны, `/domain-deep-dive`).

## Поверхность — хребет продукта

Продукт состоит из **поверхностей** (web, mobile, бот, API, админка …) —
точек, где он встречает пользователя. `surface.md` — реестр поверхностей.
Каждая поверхность описывается сверху вниз в трёх слоях, и все три
партиционируются по её slug:

```
docs/projects/<slug>/
├── vision.md                 singleton продукта
├── surface.md                РЕЕСТР-ХРЕБЕТ: объявляет поверхности
├── user.md  integration.md   плоские кросс-поверхностные таблицы
├── boundary.md  constraint.md  market.md
├── capability/
│   ├── <surface-1>.md        возможности поверхности 1
│   └── <surface-2>.md        возможности поверхности 2
├── interface/
│   ├── <surface-1>/          who · stage · situation · zone · block · ux-substrate · data-items
│   └── <surface-2>/
├── screens/
│   ├── <surface-1>/          flows · screens · blocks · shells · assets
│   └── <surface-2>/
├── telegram-bot-flow/
│   └── <bot-surface>/        command.md · notification.md · features/<feature>/{dialog.md,window.md,use-case.md}  (для type: bot — вместо screens)
└── services/                 service.md + platform.md + architecture.md + _shared/
                              + <service-slug>/ (паспорт + domains/<ctx>/)
```

Одна ценность, доступная на двух поверхностях («смотреть статус» на web и
в боте), описывается **двумя записями** — каждая в файле своей поверхности,
со своим воплощением. Дубль — осознанный: воплощение ценности на разных
поверхностях разное.

## Файлы

| файл | сущность | поля |
|---|---|---|
| [`vision.md`](vision.md) | singleton: проблема, успех, non-goals продукта | три раздела + оси (audience · intent · market-maturity · lifecycle) + addresses-problem + статус |
| [`surface.md`](surface.md) | реестр-хребет поверхностей продукта | slug · name · description · type · lives-at · user · status |
| [`capability.md`](capability.md) | форма одного файла `capability/<surface>.md` — возможности поверхности | slug · name · description · value · user · hypotheses · jobs · status |
| [`user.md`](user.md) | сегмент пользователей / клиентов | slug · name · description · context · jobs · pains · success · segments · status |
| [`integration.md`](integration.md) | внешняя система или соседний проект, с которым обмениваемся | slug · name · description · direction · payload · owner · surface · target · sibling-project · status |
| [`boundary.md`](boundary.md) | явный non-goal с обоснованием | slug · name · description · why · status |
| [`constraint.md`](constraint.md) | внешнее ограничение (регуляторика, SLA, контракт) | slug · name · description · kind · source · status |
| [`market.md`](market.md) | рыночный аналог / конкурент | slug · name · description · url · sources · status |

Карта межпроектных стыков всего бизнеса — отдельный артефакт уровнем выше:
[`../project-map.md`](../project-map.md).

## Принципы оформления

Зеркалит канон `docs/projects/_template/interface/`. Один файл — одна таблица
сущностей одного типа (vision исключение — singleton). Структура
табличного файла:

```markdown
# <имя файла>

> Одна-две фразы о сущности (что это в продукте, что чем ссылается).

## Критерии <kind>
…

## Что <kind> НЕ
…

## Тест-критерий
…

| slug | name | description | <relation columns> | status |
|---|---|---|---|---|
| `<slug>` | <имя> | <описание> | … | `draft` |
```

H1 = имя файла = kind. Frontmatter не нужен — kind определяется именем
файла. Файл возможностей берёт имя поверхности (`capability/<surface>.md`),
H1 внутри — `capability`. Русское слово, являющееся переводом строгого
термина, сопровождается его `slug` в скобках при каждом вхождении:
«пользователь (user)», «возможность (capability)», «поверхность (surface)».

### Форма ячеек (та же что в interface)

| тип значения | формат | пример |
|---|---|---|
| одиночный slug-реф | в бэктиках | `` `analyst` `` |
| массив slug-рефов | питон-стиль с бэктиками внутри | `` [`analyst`, `business-owner`] `` |
| пустое опциональное поле | em-dash | `—` |
| enum (`type`, `direction`, `kind`, `target`, `status`) | в бэктиках | `` `web` `` |
| свободный текст | без кавычек, одна строка | «снижение времени до первой ценности» |

Первые три колонки везде одни и те же: `slug` · `name` · `description`.
Последняя колонка — `status` (enum `draft` \| `stable`).

## Статус записи

- `draft` — заведена, но не прошла полный чек-лист зрелости (часть слотов
  пустая, есть открытые вопросы в `state/`, тест-критерий не подтверждён,
  ссылается на не существующие сущности).
- `stable` — прошла все критерии файла-канона (`Критерии <kind>`,
  `Что <kind> НЕ`, `Тест-критерий`), все обязательные слоты заполнены,
  все семантические связи внятные, открытых вопросов нет.
- Дефолт у новой записи — `draft`. Повышение в `stable` — через скилл
  `/project-deep-dive` (аналитик; в клиент-режиме продукт ведёт единый вход
  `/entrypoint-for-business`), по подтверждению аналитика.
- Понижение `stable → draft` — только аналитик руками, когда нашёл
  несостыковку.

## Связи (семантические, не структурные)

Жёстких slug-валидаций между записями нет — `/project-audit` ловит
тупики **в пределах project**, `/cross-audit` ловит несостыковки
**между слоями** через семантический разбор (рой агентов), не через
ссылочную целостность. Единственное структурное правило — поверхность:
файл `capability/<surface>.md` и папки `interface/<surface>/`,
`screens/<surface>/`, `telegram-bot-flow/<surface>/` обязаны
соответствовать поверхности из реестра `surface.md` (последняя — только
поверхности с `type: bot`).

Внутри `docs/projects/<slug>/` ожидаются неформальные связи:

- **user → surface**: user работает через одну+ поверхность
  (`surface.user` — кого она обслуживает).
- **user → capability**: user получает ценность от одной+
  возможности (`capability/<surface>.md` → колонка `user`).
- **capability → surface**: связь **структурная** — возможность лежит в
  файле своей поверхности. `/project-audit` ловит файл возможностей для
  поверхности вне реестра и поверхность реестра без файла возможностей.
- **integration → surface**: интеграция обслуживает одну+ поверхность
  (колонка `surface` — массив slug-рефов в реестр).
- **integration ↔ capability**: интеграция обычно обслуживает
  возможность (не фиксируется отдельным полем — `/cross-audit`).
- **integration → соседний проект**: при `target: sibling-project` —
  колонка `sibling-project` ссылается на slug соседнего проекта бизнеса
  (стык фиксируется здесь, сводится в `../project-map.md`).
- **constraint ↔ surface / integration**: ограничение часто привязано к
  поверхности или интеграции (152-ФЗ → web; SLA партнёра → integration).
  Не фиксируется полем.
- **market ↔ capability**: конкурент покрывает наши возможности — это
  смысл сопоставления, проверяет `/cross-audit`.

Связь с соседними слоями (тоже семантическая; соседи `interface`/
`screens`/`services` живут **в той же папке проекта**
`docs/projects/<slug>/`):

- `vision.addresses-problem` ↔ `business/business-problem` — какие проблемы
  закрывает продукт (M:N; авторская сторона связи — здесь).
- `user.segments` → `ajtbd/segment` — пользователь сводится к сегменту(ам)
  рынка (опц.; авторски здесь).
- `capability.hypotheses` → `hypothesis-map/hypothesis`, `capability.jobs`
  → `ajtbd/job` — возможность реализует гипотезу и целит в работу сегмента
  (опц.; авторски здесь).
- `user` ↔ `<slug>/interface/<surface>/who` — каждая роль в `interface`
  должна семантически соответствовать одной из user проекта (авторски
  `who.users`).
- `capability/<surface>` ↔ `<slug>/interface/<surface>/situation` /
  `<slug>/services/<svc>/domains/<область>` — возможность поверхности реализуется через
  ситуации той же поверхности (UX) + домены (бэкенд).
- `surface` ↔ `<slug>/interface/<surface>/zone` — зоны интерфейса живут в
  папке своей поверхности.
- `integration` ↔ `<slug>/services/` — внешняя интеграция в коде
  существует как доменный адаптер; межпроектная интеграция — как порт/клиент
  к соседнему проекту (клиент в `services/_shared/integrations/`,
  потребление — `services/_templates/use-case.md`); какой сервис ходит
  наружу — видно по паспорту (`Dependencies`/`Fronts`).

## Workflow

```
/project-deep-dive            — единая точка входа аналитика.
/entrypoint-for-business      — режим «домашнее задание» для клиента
                                (бизнес-язык, единый вход, эскалация в ветку).
/project-audit                — узкий аудит внутри project-слоя.
/cross-audit                  — сквозной семантический аудит
                                project ↔ interface ↔ services/domain ↔ screen
                                + межпроектные стыки (project-map).
```

Скилы заводят новые сущности, углубляют частичные, разбирают сырьё
(транскрипт интервью клиента, заметки, web-research), ведут переход
`draft → stable`. Прямой правки артефактов руками избегаем — скилл держит
state и предлагает переходы через `AskUserQuestion`.

## Anti-patterns

- ❌ Frontmatter в файлах (kind определяется именем файла — как в
  `interface/`).
- ❌ Каталоги-по-сущностям (`users/` с файлом на запись). Один табличный
  файл = один kind. Поверхность — единственная ось партиционирования:
  `capability/<surface>.md` — это таблица, не каталог записей.
- ❌ Файл возможностей или папка интерфейса/экранов/диалогов для
  поверхности, которой нет в реестре `surface.md`. Хребет ведёт реестр.
- ❌ Несколько vision в **одном проекте**. Один проект (папка
  `docs/projects/<slug>/`) = один продукт = один `vision.md`. Разные
  продукты — разные папки проектов.
- ❌ Перенос продукт-аналитики в `<slug>/interface/` (UX-слой) или в
  `<slug>/services/` (топология и бэкенд) — это разные слои. project = «зачем и для
  кого», interface = «как взаимодействует», domain = «какой бизнес-код».
- ❌ Жёсткие slug-валидации между project и соседями. Связи —
  семантические; ловит `/cross-audit`, а не grep.
- ❌ Авто-вписывание результатов web-research в артефакты. Рой агентов
  кладёт кандидатов в `state/research/` — promotion в `market.md` /
  `constraint.md` только через `AskUserQuestion` аналитика.
- ❌ Промоушн `stable` руками без чек-листа — это работа скилла.
