# Артефакты бизнеса

Самый верхний слой документации: **кто этот бизнес заказчика** — до того,
как мы определили проблему и тем более решение. 1 singleton `profile.md`,
5 плоских md-файлов картины бизнеса, строгий реестр проблем
`business-problem.md` и 2 строгих файла стейкхолдеров (`stakeholder` ·
`stakeholder-map`) — людей, которые в этом бизнесе принимают решения, — в
`docs/business/`. Источник истины — **материалы клиента** (сайт, PDF,
презентации, соцсети, интервью) и **рой web-research**; не наша проекция и
не будущее IT-решение.

Слой **нестрогий**: жёсткой методологии нет, цель — сложить полную и
честную картину бизнеса. Эта картина питает соседние слои: сегменты по
работам, граф работ и трения живут в `docs/ajtbd/` (на `ajtbd/segment`
ссылаются `offering.for-segment` и `channel.serves-segment`); SWOT-факторы
(`docs/swot/`) растут из профиля и конкурентов, baseline целевых метрик
(`docs/hypothesis-map/`) — из `current-metric.md`. Реестр проблем бизнеса
(`business-problem.md`) живёт в этом слое.

Чистая бизнес-аналитика. На продукт / интерфейс / код не мапится — это
вход для `/business-deep-dive` (профиль + реестр проблем + стейкхолдеры) и
далее `/swot-deep-dive` и `/hypothesis-map-deep-dive`.

## Файлы

| файл | сущность | поля |
|---|---|---|
| [`profile.md`](profile.md) | singleton: чем бизнес занимается, как зарабатывает | четыре раздела + статус |
| [`offering.md`](offering.md) | продукт / услуга, которую бизнес продаёт | slug · name · description · kind · for-segment · from-project · status |
| [`channel.md`](channel.md) | как бизнес привлекает / продаёт / доставляет | slug · name · description · kind · serves-segment · status |
| [`competitor.md`](competitor.md) | игрок на рынке заказчика | slug · name · description · url · position · sources · status |
| [`current-metric.md`](current-metric.md) | текущий KPI бизнеса — baseline-кандидат | slug · name · description · value · as-of · source · from-project · status |
| [`material.md`](material.md) | источник, из которого сложен профиль | slug · name · kind · uri · status |
| [`business-problem.md`](business-problem.md) | реестр проблем бизнеса + граница гарантии и таргета | slug · name · problem · guarantee · target · out-of-control · scope · served · from-project · status |
| [`stakeholder.md`](stakeholder.md) | человек, принимающий решение в бизнесе заказчика (конкретное лицо) | slug · name · description · unit · deal-role · power · interest · attitude · motivation · win · strategic-stance · objections · reports-to · manifests-as · status |
| [`stakeholder-map.md`](stakeholder-map.md) | сборка по инициативе: сетка власть/интерес, граф связей, путь вовлечения | slug · name · scope · business-problem · members · grid · influence-edges · engagement-path · strategy · risks · status |

## Принципы оформления

Зеркалит канон `docs/projects/_template/project/`. Один файл — одна таблица
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

- `business.profile` / `competitor` → `swot.factor` —
  сильные/слабые стороны и тренды/угрозы вырастают из картины бизнеса.
- `business.current-metric` → `hypothesis-map.metric.current` — текущий
  KPI становится baseline целевой метрики.
- `business-problem` ← `swot` / `hypothesis-map` /
  `projects/<slug>/vision.addresses-problem` — реестр проблем, на который
  ссылаются SWOT, Карта гипотез и продукты (M:N через колонку `business-problem`).
- `business.offering` / `current-metric` / `business-problem` ← дозревший
  продукт (`*.from-project`) — провенанс восходящего потока.
- `business.offering` / `competitor` ↔ `ajtbd/solution` — собственный офер
  и игроки рынка часто и есть решения, нанятые сегментом на работу
  (`solution.maps-to`).
- `stakeholder` → `business-problem` — кто проблему **чувствует /
  приоритизирует** и кто согласовал границу гарантия/таргет
  (`stakeholder-map.business-problem` тегирует карту проблемой).
- `stakeholder` ↔ `hypothesis-map/subject` — внутр. субъект; властный
  `blocker` ≈ `negative`-субъект; мотивации согласованы (через
  `manifests-as`).
- `stakeholder` ↔ `projects/<slug>/user` · `interface/who` — стейкхолдер,
  ставший пользователем/актором продукта (через `manifests-as`).
- `stakeholder` → `swot/factor` — властный `champion` = сила, властный
  `skeptic`/`blocker` = слабость/угроза (человек-как-фактор).
- `stakeholder.strategic-stance` ↔ `swot/bet` · `hypothesis-map/goal` —
  стратегия не должна противоречить стойке властного лица; ставка/цель,
  бьющая в стойку, — стратегический риск (ловит `/cross-audit`
  `stakeholder-strategy`).
- `stakeholder` → `projects/<slug>/constraint` — вето `gatekeeper`/lvr
  (безопасник, юрист) рождает ограничение продукта.

Стейкхолдеры (`stakeholder` · `stakeholder-map`) — **строгие** kind (свои
методологические инварианты держит draft→stable-гейт `/business-deep-dive`,
а сквозную сверку со swot/hypothesis-map — `/cross-audit`, углы
`stakeholder-*`) и **намеренно вне handoff-контракта**: `business/` не
читает ни один код-репо, поэтому персональные данные людей-решателей не
уезжают в backend/frontend/infra. Это **единственное место**, где
репозиторий пишет конкретных лиц, а не роли (см. `stakeholder.md` §
«Намеренное исключение»).

## Workflow

```
/business-deep-dive             — единая точка входа аналитика (в т.ч. фаза stakeholders).
/entrypoint-for-business        — режим «домашнее задание» для клиента (единый вход на все темы).
/cross-audit                    — сквозная проверка с ajtbd / swot / hypothesis-map / project (углы stakeholder-*).
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
  и ниже; проблема бизнеса — реестр `business-problem.md` этого слоя.
  В профиле и картине бизнеса — только бизнес **как он есть**.
- ❌ Профиль «как должно быть» вместо «как есть». Слой описывает текущую
  реальность бизнеса, не желаемое будущее.
- ❌ Автозалив web-research в артефакты без подтверждения аналитика.
- ❌ Заводить сегменты здесь. Сегменты по работам живут в `docs/ajtbd/`
  (`/segment-deep-dive`); `business` лишь ссылается на них из
  `offering`/`channel`.
- ❌ Путать `stakeholder` (человек-решатель **внутри** заказчика) с
  `segment`/`user`/`who`/`subject` (люди **снаружи** — рынок, адресат,
  актор, носитель поведения). Один человек обеими линзами — `manifests-as`.
- ❌ Стейкхолдер как абстрактная роль («руководство») там, где лицо
  известно. Это единственное место для конкретных лиц.
- ❌ Журнал отношения стейкхолдера («был против, стал за»). Только текущее
  состояние, перезапись при сдвиге (forward-only).
- ❌ Выдуманные мотивации/страхи стейкхолдера. Только из материалов
  клиента / интервью — экспертиза священна.
