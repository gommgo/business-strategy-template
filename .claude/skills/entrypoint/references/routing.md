# Маршрутизация: сигнал → слой → kind → исполнитель → режим

Таблица, по которой оркестратор сопоставляет чанк сырья (или намерение
аналитика) со слоем, kind, скиллом-исполнителем и режимом. Связи между
слоями **семантические** (не slug-валидируемые) — оркестратор опирается на
**смысл** сигнала, не на grep.

## Слои и исполнители (полная карта)

| слой | kinds | исполнитель | аудит |
|---|---|---|---|
| `docs/business/` | `profile` · `offering` · `channel` · `competitor` · `current-metric` · `material` · `business-problem` | `/business-deep-dive` | `/cross-audit` (своего узкого нет) |
| `docs/business/` (стейкхолдеры) | `stakeholder` · `stakeholder-map` | `/business-deep-dive` (фаза `stakeholders`) | `/cross-audit` (углы `stakeholder-*`; своего узкого нет) |
| `docs/ajtbd/` (сегменты) | `segment` | `/segment-deep-dive` | `/ajtbd-audit` |
| `docs/ajtbd/` (граф работ) | `job` · `job-graph` · `solution` · `segment-problem` | `/job-graph-deep-dive` | `/ajtbd-audit` |
| `docs/ajtbd/` (живые интервью) | сырьё-кандидаты | `/jtbd-interview` (опц., тяжёлый, по явному запросу) | — |
| `docs/swot/` | `factor` · `bet` | `/swot-deep-dive` | `/swot-audit` |
| `docs/hypothesis-map/` | `goal` · `metric` · `subject` · `hypothesis` · `task` | `/hypothesis-map-deep-dive` | `/hypothesis-map-audit` |
| `docs/projects/<slug>/` (vision + хребет + кросс-поверхностные kind) | `vision` · `surface` · `user` · `integration` · `boundary` · `constraint` · `market` | `/project-deep-dive <slug>` | `/project-audit <slug>` |
| `docs/projects/<slug>/capability/<surface>.md` (возможности по поверхности) | `capability` (по файлу на поверхность) | `/project-deep-dive <slug>` | `/project-audit <slug>` |
| `docs/projects/<slug>/interface/<surface>/` | `who` · `stage` · `situation` · `zone` · `block` · `ux-substrate` · `data-items` | `/interface-deep-dive <slug> [<surface>]` | `/interface-audit <slug>` |
| `docs/projects/<slug>/services/` (топология: реестр сервисов + паспорта + платформа + architecture) | сервисы/паспорта/брокер/ресурсы | `/service-deep-dive <slug>` | `/service-audit <slug>` + `/cross-audit` |
| `docs/projects/<slug>/services/<svc>/domains/<ctx>/` (по bounded-context, внутри сервиса-владельца, surface-агностичны) | агрегаты/события/use-case/… | `/domain-deep-dive <slug> <ctx>` | `/service-audit <slug>` + `/cross-audit` |
| `docs/projects/infrastructure/` (ИТ-периметр бизнеса: сервера · рантаймы · общие ресурсы · джобы · размещение) | server/runtime/shared-platform/job/placement | `/infrastructure-deep-dive` | `/infrastructure-audit` + `/cross-audit` |
| `docs/projects/<slug>/screens/<surface>/` | `flow` · `screen` · `block` · `shell` | `/screen-deep-dive <slug> [<surface>]` | `/screen-audit <slug>` |
| `docs/projects/<slug>/telegram-bot-flow/<surface>/` (bot-поверхности) | фичи `features/<feature>/` (`dialog` · `window` · `use-case` бота) + сквозные `command` · `notification` | `/telegram-bot-flow-deep-dive <slug> [<surface>]` | `/telegram-bot-flow-audit <slug>` |
| `docs/projects/project-map.md` (межпроектные стыки) | `project-map` (singleton-граф рёбер) | `/project-deep-dive <slug>` (авторская сторона ребра — `integration` инициатора) | `/cross-audit` |
| сквозная консистентность | — | — | `/cross-audit` |

Проектные исполнители берут `<project-slug>` **первым аргументом**;
оркестратор обязан определить проект до делегирования (из сырья или
вопросом). Поверхность (`surface`) — ось продукта: реестр-хребет
`surface.md` объявляет поверхности, а их slug'и партиционируют возможности
(`capability/<surface>.md`), интерфейс (`interface/<surface>/`) и
композицию — экраны (`screens/<surface>/`) либо диалоги бота
(`telegram-bot-flow/<surface>/` при `type: bot`). Скилы
`interface`/`screen`/`telegram-bot-flow` берут поверхность
**вторым аргументом** `[<surface>]`; без него — пикер поверхностей по
`surface.name` (после пикера проекта). Домены (`services/<svc>/domains/<ctx>/`) —
surface-агностичны, делятся по bounded-context. Межпроектные стыки сводит
`docs/projects/project-map.md` — авторская сторона каждого ребра живёт в
`integration` проекта-инициатора (`target: sibling-project`).

## Сигнал → слой (классификация чанка)

| сигнал в чанке / намерении | слой → kind |
|---|---|
| «чем бизнес занимается, как зарабатывает, позиционирование» | `business` / `profile` |
| «что продаём» / «через какие каналы привлекаем-доставляем» | `business` / `offering` · `channel` |
| «кого считаем конкурентом» / «кто на рынке» | `business` / `competitor` |
| «текущие KPI, числа бизнеса сейчас» (с датой/источником) | `business` / `current-metric` |
| «вот документ / сайт / выгрузка» (источник) | `business` / `material` (провенанс) |
| «какую боль бизнеса решаем, граница гарантии/таргета» | `business` / `business-problem` (реестр проблем) |
| «кто в бизнесе принимает решение / спонсор / держит бюджет / блокирует / на кого влияет» | `business` / `stakeholder` · `stakeholder-map` |
| «кто наши клиенты — группа по общим работам, не демография» | `ajtbd` / `segment` |
| «что клиент пытается сделать / зачем / чем пользуется сейчас / где тяжело» | `ajtbd` / граф работ (`job` · `solution` · `segment-problem` · `job-graph`) |
| «нужны живые интервью с клиентами» | `ajtbd` / `/jtbd-interview` |
| «сильные/слабые стороны, тренды/угрозы» | `swot` / `factor` |
| «за счёт чего сделаем шаг — стратегическая ставка» | `swot` / `bet` |
| «к чему стремимся (без цифр)» | `hypothesis-map` / `goal` |
| «по какому числу поймём, baseline → target, атрибуция, приёмка» | `hypothesis-map` / `metric` |
| «на чьё поведение влияем, чья мотивация» | `hypothesis-map` / `subject` |
| «если сделаем X — то Y, потому что Z, и тогда метрика» | `hypothesis-map` / `hypothesis` |
| «как проверим ставку — эксперимент/замер» | `hypothesis-map` / `task` |
| «зачем продукт и для кого, что НЕ делаем» | `projects/<slug>` / `vision` (`addresses-problem`) |
| «через какие поверхности продукт встречает пользователя (web, бот, API …)» | `projects/<slug>` / `surface` (реестр-хребет) |
| «кто пользователь продукта» | `projects/<slug>` / `user` |
| «что продукт умеет на этой поверхности (бизнес-возможность)» | `projects/<slug>` / `capability` (файл `capability/<surface>.md` — на какой поверхности?) |
| «где торчит наружу / с чем интегрируется внешняя система / какие правила-SLA / аналоги» | `projects/<slug>` / `surface` · `integration` · `constraint` · `market` |
| «продукт обменивается с **соседним продуктом** того же бизнеса» | `projects/<slug>` / `integration` (`target: sibling-project`, `sibling-project: <slug-соседа>`) → ребро в `projects/project-map` |
| «как пользователь взаимодействует, ситуации, зоны, блоки» (на какой поверхности?) | `projects/<slug>/interface/<surface>` / `who` · `situation` · `zone` · `block` · … |
| «как это выглядит, экраны, композиция» (на какой поверхности?) | `projects/<slug>/screens/<surface>` / `flow` · `screen` · `block` · `shell` |
| «как бот ведёт диалог: окна, кнопки, команды, уведомления, оркестрация действий» (какая bot-поверхность?) | `projects/<slug>/telegram-bot-flow/<surface>` / фичи `features/<feature>/` (`dialog` · `window` · `use-case` бота) + `command` · `notification` |
| «бизнес-код бэкенда, агрегаты, инварианты» (какой bounded-context?) | `projects/<slug>/services/<svc>/domains/<ctx>` |
| «архитектура приложения: из каких сервисов состоит, монолит/микросервисы, брокер/очередь, gateway, где какая БД, кто продюсер/консьюмер событий» | `projects/<slug>/services` |
| «сервера, хостинг, кубер vs compose, где будет жить сервис, общий брокер/traefik на все проекты, учёт VPS» | `projects/infrastructure` |

Граничные пары (снимает именование, не путать):

- **трение клиента** (`ajtbd/segment-problem`) ≠ **проблема бизнеса**
  (`business/business-problem`): первое **питает доказательством** второе.
  Сигнал «клиенту тяжело с X» → ajtbd; «бизнес теряет деньги/время на Y» →
  business-problem.
- **четвёрка адресатов**: `who` (участник системы, interface) ≠ `user`
  (пользователь продукта, project) ≠ `segment` (рынок по работам, ajtbd) ≠
  `subject` (носитель самодвижения, hypothesis-map) — все смотрят **наружу**
  (рынок / адресат решения). `stakeholder` (business) — пятый, смотрит
  **внутрь** заказчика: человек-решатель в политике проекта, не рыночное
  лицо. Сигнал «человек, влияющий на судьбу проекта внутри заказчика» →
  `stakeholder`; один человек обеими линзами — `manifests-as`.

## Режим → как маршрутизировать

| режим | сигнал намерения | действие оркестратора |
|---|---|---|
| `наполнить` | «вот сырьё / заведём новое / тут пусто» | делегировать `*-deep-dive` (режим A «новая сущность» или B «сырьё») |
| `актуализировать` | «появились новые данные / сверим с тем, что было» | делегировать `*-deep-dive` (режим B/C на существующих записях) |
| `рефакторить` | «переименовать / перенести / слить slug» | делегировать `*-deep-dive` его процедурой каскад-правки (исполнитель показывает каскад внутри слоя); сквозные ссылки между слоями ловит `/cross-audit` |
| `чистить` | «удалить сущность» | делегировать `*-deep-dive` его процедурой удаления (каскад ссылок + подтверждение) |
| `аудитить` | «проверь / перед коммитом / что-то рассинхронилось» | запустить нужный аудит-рой (ниже) |

### Выбор аудита (режим `аудитить`)

| что проверяем | аудит |
|---|---|
| инварианты LinkedSWOT (по каждой проблеме) | `/swot-audit` |
| инварианты Карты гипотез (по каждой проблеме) | `/hypothesis-map-audit` |
| инварианты AJTBD (по каждому сегменту) | `/ajtbd-audit` |
| стыки стейкхолдеров со swot / hypothesis-map | `/cross-audit` (углы `stakeholder-subject` · `stakeholder-factor` · `stakeholder-strategy`) |
| внутрипроектная консистентность продукта | `/project-audit <slug>` |
| консистентность interface проекта | `/interface-audit <slug>` |
| консистентность screens проекта | `/screen-audit <slug>` |
| **сквозная** консистентность между всеми слоями и проектами | `/cross-audit` |

Тронули несколько слоёв → в конце предложить `/cross-audit` (он
разворачивает рой по верхнеуровневым углам один раз и по каждому проекту
отдельно).

## Многослойный чанк

Один чанк может тянуть в несколько слоёв (типичное «хотим, чтобы клиенты
возвращались» — это и `goal`, и косвенно `segment`/`subject`). Не дробить
насильно: вести в **первичный** слой через его исполнителя; смежные связи
(`subject.segments`, `hypothesis.jobs`, `capability.jobs` и т.п.) исполнитель
заводит **авторски снизу-вверх** на своей стороне. Оркестратор лишь следит,
чтобы смежный слой не потерялся — фиксирует его открытой нитью.

## Выбор поверхности (interface / screens / telegram-bot-flow / capability)

Слои `interface`, `screens` и `telegram-bot-flow` партиционированы по
поверхности — путь делегирования несёт **и проект, и поверхность**:
`/interface-deep-dive <slug> [<surface>]`,
`/screen-deep-dive <slug> [<surface>]`,
`/telegram-bot-flow-deep-dive <slug> [<surface>]` (только поверхности с
`type: bot` — композиция бота вместо экранов). Возможности (`capability`)
тоже живут по поверхности (`capability/<surface>.md`), но входом остаётся
`/project-deep-dive <slug>` — там поверхность выбирается внутри.

Оркестратор определяет поверхность так же, как проект: из сырья (явно
названа web / бот / API) или вопросом. Если поверхность неясна —
передать без второго аргумента, исполнитель сам предложит пикер
поверхностей по `surface.name` (после пикера проекта). Поверхность, которой
нет в реестре `surface.md`, сперва заводится через `/project-deep-dive
<slug>` (kind `surface`) — каталоги `interface/<surface>/`,
`screens/<surface>/`, `telegram-bot-flow/<surface>/`,
`capability/<surface>.md` руками не создаём, их
заводят их скилы при первом заходе.

## Чего оркестратор не делает в маршрутизации

- Не выбирает слой/проект за аналитика при неоднозначности — спрашивает.
- Не выдумывает доменный текст — это исполнитель через свой `AskUserQuestion`.
- Не правит артефакты напрямую — только через исполнителя.
- Не зовёт `/jtbd-interview` без явного запроса (тяжёлый опциональный
  процесс).
