# Артефакты бизнеса

Самый верхний слой документации: **кто этот бизнес заказчика** — до того,
как мы определили проблему и тем более решение. 1 singleton `profile.md`
+ 5 плоских md-файлов в `docs/business/`. Источник истины — **материалы
клиента** (сайт, PDF, презентации, соцсети, интервью) и **рой
web-research**; не наша проекция и не будущее IT-решение.

Слой **нестрогий**: жёсткой методологии нет, цель — сложить полную и
честную картину бизнеса. Эта картина питает соседние слои: сегменты по
работам, граф работ и трения живут в `docs/ajtbd/` (на `ajtbd/segment`
ссылаются `offering.for-segment` и `channel.serves-segment`); SWOT-факторы
и baseline метрик питают `docs/business-problem/` (факторы — из профиля и
конкурентов, baseline целевых метрик — из `current-metric.md`).

Чистая бизнес-аналитика. На продукт / интерфейс / код не мапится — это
вход для `/business-deep-dive` и далее `/business-problem-deep-dive`.

## Файлы

| файл | сущность | поля |
|---|---|---|
| [`profile.md`](profile.md) | singleton: чем бизнес занимается, как зарабатывает | четыре раздела + статус |
| [`offering.md`](offering.md) | продукт / услуга, которую бизнес продаёт | slug · name · description · kind · for-segment · status |
| [`channel.md`](channel.md) | как бизнес привлекает / продаёт / доставляет | slug · name · description · kind · serves-segment · status |
| [`competitor.md`](competitor.md) | игрок на рынке заказчика | slug · name · description · url · position · sources · status |
| [`current-metric.md`](current-metric.md) | текущий KPI бизнеса — baseline-кандидат | slug · name · description · value · as-of · source · status |
| [`material.md`](material.md) | источник, из которого сложен профиль | slug · name · kind · uri · status |

## Принципы оформления

Зеркалит канон `docs/projects/_canon/project/`. Один файл — одна таблица
сущностей одного типа (`profile` исключение — singleton). H1 = имя файла = kind.
Frontmatter не нужен. Русское слово-перевод строгого термина
сопровождается его `slug` в скобках при каждом вхождении: «офер
(offering)», «канал (channel)».

### Форма ячеек

| тип значения | формат | пример |
|---|---|---|
| одиночный slug-реф | в бэктиках | `` `b2b-clinic` `` |
| массив slug-рефов | питон-стиль с бэктиками внутри | `` [`b2b-clinic`, `b2c`] `` |
| пустое опциональное поле | em-dash | `—` |
| enum (`kind`, `position`, `status`) | в бэктиках | `` `service` `` |
| свободный текст | без кавычек, одна строка | «онлайн-запись пациентов в сеть клиник» |

Первые три колонки везде — `slug` · `name` · `description` (кроме
`material`, где `description` заменён реестровыми `kind`+`uri`).
Последняя колонка — `status` (enum `draft` \| `stable`).

## Статус записи

- `draft` — заведена, но не прошла чек-лист зрелости (часть слотов
  пустая, источник не подтверждён, есть открытые вопросы в `state/`).
- `stable` — прошла критерии файла-канона, все обязательные слоты
  заполнены, факт прослежен до `material`.
- Дефолт — `draft`. Повышение в `stable` — через `/business-deep-dive`,
  по подтверждению аналитика. Понижение — аналитик руками.

## Связи (семантические)

Внутри слоя связи неформальные; всё свободно, жёстких slug-валидаций нет.
Межслойно `offering.for-segment` и `channel.serves-segment` ссылаются на
`ajtbd/segment.slug` (сегменты по работам живут в слое `docs/ajtbd/`).

Связь с соседними слоями (тоже семантическая, ловит `/cross-audit`):

- `business.profile` / `competitor` → `business-problem.factor` —
  сильные/слабые стороны и тренды/угрозы вырастают из картины бизнеса.
- `business.current-metric` → `business-problem.metric.current` — текущий
  KPI становится baseline целевой метрики.
- `business.offering` / `competitor` ↔ `ajtbd/solution` — собственный офер
  и игроки рынка часто и есть решения, нанятые сегментом на работу
  (`solution.maps-to`).

## Workflow

```
/business-deep-dive             — единая точка входа аналитика.
/business-deep-dive-for-business — режим «домашнее задание» для клиента.
/cross-audit                    — сквозная проверка с business-problem / project.
```

Слой наполняется приёмом материалов клиента и роем web-research. Рой
кладёт кандидатов в `state/research/`; promotion в `competitor.md` /
`current-metric.md` — только через `AskUserQuestion` аналитика. Авто-залив
из веба запрещён.

## Anti-patterns

- ❌ Frontmatter в файлах (kind определяется именем файла).
- ❌ Каталоги под kind (`segments/`, `offerings/`) — один файл = один
  kind, плоско.
- ❌ Несколько `profile.md` — один репо = один бизнес заказчика.
- ❌ Описание нашего будущего IT-решения здесь. Решение — слой `project`
  и ниже; бизнес-проблема — слой `business-problem`. Здесь только бизнес
  **как он есть**.
- ❌ Профиль «как должно быть» вместо «как есть». Слой описывает текущую
  реальность бизнеса, не желаемое будущее.
- ❌ Автозалив web-research в артефакты без подтверждения аналитика.
- ❌ Заводить сегменты здесь. Сегменты по работам живут в `docs/ajtbd/`
  (`/segment-deep-dive`); `business` лишь ссылается на них из
  `offering`/`channel`.
