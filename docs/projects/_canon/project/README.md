# Артефакты продукта

Продуктовый слой проекта: 1 singleton + 7 плоских md-файлов в
`docs/projects/<project-slug>/`. Этот файл — **канон формы**
(`_canon/project/`); данные каждого проекта живут в его папке. Vision —
корневой документ продукта; остальные 7 — таблицы сущностей одного типа.
Все связи между сущностями — через `slug`, но консистентность по слою —
**семантическая**, не структурная (см. `/cross-audit`).

Чистая продуктовая аналитика. На код / FSD / компонент не мапится — это
вход для соседних слоёв того же проекта, **вложенных в его папку**:
`<slug>/interface/` (UX, `/interface-deep-dive`), `<slug>/domains/`
(домены бэкенда, `/domain-deep-dive`), `<slug>/screens/` (композиция
экранов, `/screen-deep-dive`).

## Файлы

| файл | сущность | поля |
|---|---|---|
| [`vision.md`](vision.md) | singleton: проблема, успех, non-goals продукта | три раздела + оси (audience · intent · market-maturity · lifecycle) + addresses-problem + статус |
| [`user.md`](user.md) | сегмент пользователей / клиентов | slug · name · description · context · jobs · pains · success · segments · status |
| [`capability.md`](capability.md) | бизнес-возможность продукта верхнего уровня | slug · name · description · value · user · hypotheses · jobs · status |
| [`boundary.md`](boundary.md) | явный non-goal с обоснованием | slug · name · description · why · status |
| [`surface.md`](surface.md) | поверхность, куда продукт «торчит наружу» | slug · name · description · type · lives-at · user · status |
| [`integration.md`](integration.md) | внешняя система, с которой обмениваемся | slug · name · description · direction · payload · owner · status |
| [`constraint.md`](constraint.md) | внешнее ограничение (регуляторика, SLA, контракт) | slug · name · description · kind · source · status |
| [`market.md`](market.md) | рыночный аналог / конкурент | slug · name · description · url · sources · status |

## Принципы оформления

Зеркалит канон `docs/projects/_canon/interface/`. Один файл — одна таблица
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
файла. Русское слово, являющееся переводом строгого термина, сопровождается
его `slug` в скобках при каждом вхождении: «пользователь (user)»,
«возможность (capability)», «поверхность (surface)».

### Форма ячеек (та же что в interface)

| тип значения | формат | пример |
|---|---|---|
| одиночный slug-реф | в бэктиках | `` `analyst` `` |
| массив slug-рефов | питон-стиль с бэктиками внутри | `` [`analyst`, `business-owner`] `` |
| пустое опциональное поле | em-dash | `—` |
| enum (`type`, `direction`, `kind`, `status`) | в бэктиках | `` `web` `` |
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
ссылочную целостность.

Внутри `docs/projects/<slug>/` ожидаются неформальные связи:

- **user → surface**: user работает через одну+ поверхность
  (`surface.user` — кого она обслуживает).
- **user → capability**: user получает ценность от одной+
  возможности (`capability.user`).
- **capability → surface**: возможность реализуется на одной+
  поверхности (выводимо через user; явная связь — у `/cross-audit` на
  совести).
- **integration ↔ capability**: интеграция обычно обслуживает
  возможность (не фиксируется отдельным полем — `/cross-audit`).
- **constraint ↔ surface / integration**: ограничение часто привязано к
  поверхности или интеграции (152-ФЗ → web; SLA партнёра → integration).
  Не фиксируется полем.
- **market ↔ capability**: конкурент покрывает наши возможности — это
  смысл сопоставления, проверяет `/cross-audit`.

Связь с соседними слоями (тоже семантическая; соседи `interface`/
`domains`/`screens` живут **в той же папке проекта**
`docs/projects/<slug>/`):

- `vision.addresses-problem` ↔ `business/business-problem` — какие проблемы
  закрывает продукт (M:N; авторская сторона связи — здесь).
- `user.segments` → `ajtbd/segment` — пользователь сводится к сегменту(ам)
  рынка (опц.; авторски здесь).
- `capability.hypotheses` → `hypothesis-map/hypothesis`, `capability.jobs`
  → `ajtbd/job` — возможность реализует гипотезу и целит в работу сегмента
  (опц.; авторски здесь).
- `user` ↔ `<slug>/interface/who` — каждая роль в `interface` должна
  семантически соответствовать одной из user проекта (авторски `who.users`).
- `capability` ↔ `<slug>/interface/situation` / `<slug>/domains/<область>`
  — возможность реализуется через ситуации (UX) + домены (бэкенд).
- `surface` ↔ `<slug>/interface/zone` — зона интерфейса принадлежит
  поверхности.
- `integration` ↔ `<slug>/domains/<адаптер>` — внешняя интеграция в коде
  существует как доменный адаптер.

## Workflow

```
/project-deep-dive            — единая точка входа аналитика.
/entrypoint-for-business      — режим «домашнее задание» для клиента
                                (бизнес-язык, единый вход, эскалация в ветку).
/project-audit                — узкий аудит внутри project-слоя.
/cross-audit                  — сквозной семантический аудит
                                project ↔ interface ↔ domain ↔ screen.
```

Скилы заводят новые сущности, углубляют частичные, разбирают сырьё
(транскрипт интервью клиента, заметки, web-research), ведут переход
`draft → stable`. Прямой правки артефактов руками избегаем — скилл держит
state и предлагает переходы через `AskUserQuestion`.

## Anti-patterns

- ❌ Frontmatter в файлах (kind определяется именем файла — как в
  `interface/`).
- ❌ Каталоги под kind (`users/`, `capabilities/` …) — один файл =
  один kind, плоско.
- ❌ Несколько vision в **одном проекте**. Один проект (папка
  `docs/projects/<slug>/`) = один продукт = один `vision.md`. Разные
  продукты — разные папки проектов.
- ❌ Перенос продукт-аналитики в `<slug>/interface/` (UX-слой) или в
  `<slug>/domains/` (бэкенд) — это разные слои. project = «зачем и для
  кого», interface = «как взаимодействует», domain = «какой бизнес-код».
- ❌ Жёсткие slug-валидации между project и соседями. Связи —
  семантические; ловит `/cross-audit`, а не grep.
- ❌ Авто-вписывание результатов web-research в артефакты. Рой агентов
  кладёт кандидатов в `state/research/` — promotion в `market.md` /
  `constraint.md` только через `AskUserQuestion` аналитика.
- ❌ Промоушн `stable` руками без чек-листа — это работа скилла.
