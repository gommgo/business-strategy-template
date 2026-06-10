# Канон проекта

Файл автоматически загружается в каждую сессию `Claude Code`. Здесь —
невыборочные правила, которые работают всегда.

Этот репозиторий — **шаблон бизнес-стратегии**. Поток сверху вниз: бизнес
заказчика (`docs/business/`) — самый верх; он же держит **реестр проблем
бизнеса** (`business-problem` — таблица проблем, по строке на проблему) и
**реестр стейкхолдеров** (`stakeholder` · `stakeholder-map` — конкретные
люди, принимающие решения в бизнесе, и карты их связей и вовлечения).
Под ним слой **AJTBD** (`docs/ajtbd/`) — кто наш сегмент по работам и его
граф работ (методология Advanced JTBD), питающий проблемы трениями
сегмента. По строгой методологии **LinkedSWOT** реестр проблем
разворачивается в слой `docs/swot/` (`factor` · `bet`), а по **Карте
гипотез** — в слой `docs/hypothesis-map/` (`goal` · `metric` · `subject` ·
`hypothesis` · `task`); оба — **многопроблемные**. Терминал стратегии —
**задача** (`task` Карты гипотез): исход проблемы бизнеса не обязан быть
IT-продуктом — её может закрыть отдельная задача (процесс, партнёрство, цена,
операционное действие). Когда стратегия требует продукта, под проблемы встают
**продукты** (опциональный downstream): несколько проектов под одним бизнесом, у
каждого своя папка `docs/projects/<slug>/`. Внутри
проекта **поверхность (surface) — ось**: реестр `surface.md` объявляет
поверхности, а их slug'и партиционируют возможности (`capability/<surface>.md`),
интерфейс (`interface/<surface>/` — UX над продуктом) и композицию: экраны
(`screens/<surface>/` — композиция/облик, по которой собирается кликабельный
hi-fi субстрат на библиотеке `@stit/ui`) либо — для поверхностей с
`type: bot` — диалоги телеграм-бота (`telegram-bot-flow/<surface>/` —
dialog · window · command · notification в понятиях aiogram_dialog;
читает форк `telegram-bot-template`). Кросс-поверхностные kind продукта
(`user` · `integration` · `boundary` · `constraint` · `market`) и `vision` —
плоско в корне проекта. Опционально бизнес-домены (`domains/`) —
**по bounded-context, surface-агностичны**. Точки стыка между продуктами
бизнеса — в `docs/projects/project-map.md`. Канон формы продуктовых слоёв —
один раз в `docs/projects/_template/`. См.:

- `README.md` — карта репозитория и воркфлоу.
- `docs/business/README.md` — канон 1 singleton + 5 kind бизнеса +
  реестр проблем `business-problem` + 2 строгих kind стейкхолдеров
  (`stakeholder` · `stakeholder-map`).
- `docs/ajtbd/README.md` — канон 5 kind AJTBD: `segment` · `job` ·
  `job-graph` · `solution` · `segment-problem`.
- `docs/swot/README.md` — канон LinkedSWOT: `factor` · `bet`; колонка-ссылка
  `business-problem` — массив, M:N к реестру проблем бизнеса.
- `docs/hypothesis-map/README.md` — канон Карты гипотез: `goal` ·
  `metric` · `subject` · `hypothesis` · `task`; `business-problem` — массив, M:N.
- `docs/projects/README.md` — как устроены проекты: `_template`, выбор
  проекта и поверхности, связь `addresses-problem` (M:N) с проблемами,
  межпроектная карта.
- `docs/projects/_template/project/README.md` — канон 1 vision +
  реестр-хребет `surface` + кросс-поверхностные kind + `capability/<surface>`.
- `docs/projects/_template/interface/README.md` — канон 7 артефактов
  интерфейса **одной поверхности** (`interface/<surface>/`).
- `docs/projects/_template/domains/README.md` — канон DDD-артефактов бэкенда
  (если есть; по bounded-context).
- `docs/projects/_template/screens/README.md` — канон 4 kind артефактов
  экранов **одной поверхности** (`screens/<surface>/`).
- `docs/projects/_template/telegram-bot-flow/README.md` — канон 4 kind
  диалогов **одной bot-поверхности** (`telegram-bot-flow/<surface>/`):
  dialog · window · command · notification.
- `docs/projects/project-map.md` — карта стыков между продуктами бизнеса
  (singleton: канон формы + данные в одном файле; бизнес-язык, без техники).

Артефакты — чистая аналитика; на FSD/компоненты напрямую не мапятся.
Превращение `docs/projects/<slug>/screens/` в wireframe и hi-fi — ручная
работа автора макета, не отдельный артефакт.

Карта документации и handoff-контракт соседям — `docs/README.md`. Путь
потребителя форка — `docs/getting-started.md`.

## Где это в экосистеме

Это один из **6 форкаемых шаблонов** под `stit-core/`:
`corp-infra-template` (корп control-plane), `go-backend-template`
(→ `<org>/backend`), `spa-frontend-template` (→ `<org>/frontend`),
`telegram-bot-template` (→ `<org>/<bot>`),
**`business-strategy-template`** (этот → `<org>/strategy`),
`project-infra-template-compose` (→ `<org>/infra`). Рядом — 2 общие библиотеки:
Go-lib `stit-core/golibinfra` и дизайн-система `@stit/ui` из репо
`stit-core/ui-lib`. Корп control-plane `corp-infra-template`: вендор-лока нет —
managed (инстанс на `*.stit.tech`) или self-hosted (ваш форк). Канон контрактов
(в т.ч. self-hosted) — `corp-infra-template/docs/ecosystem.md`.

**Роль репо — design-time SoT стратегии** (и проектирования продукта, когда он
нужен). Форкается **первым** (Gitea → `stit-core/business-strategy-template` →
**Use this template** → `<org>/strategy`), наполняется аналитикой, и — **когда
стратегия рождает продукт** — его stable-артефакты **читают** код-репо как
upstream (read-only, односторонне):

- `<org>/backend` ← `projects/<slug>/domains/<ctx>/` (scaffold доменов в Go;
  маппинг DDD → Go живёт у backend в `docs/reference/domain-mapping.md`);
- `<org>/frontend` ← `projects/<slug>/{interface,screens}/<surface>/` (fsd-deep-dive, по поверхности);
- `<org>/<bot>` ← `projects/<slug>/telegram-bot-flow/<surface>/` (+ `interface/<surface>/`,
  `domains/` — use-case'ы и события под действия и триггеры бота);
- `<org>/infra` ← `projects/<slug>/{vision,surface}` (init-project).

Контракт что docs отдаёт соседям — `docs/README.md § Что docs отдаёт
соседям`. Рекомендуемый вход — два оркестратора `/entrypoint` (аналитик)
и `/entrypoint-for-business` (клиент): принимают сырьё, классифицируют по
слоям и маршрутизируют к рою deep-dive/audit-исполнителей (прямой вызов
исполнителя тоже допустим — `docs/getting-started.md`).

## 1. Forward-only (никакой археологии)

Все артефакты — код, документация, комментарии, артефакты аналитики,
описания PR и коммитов — пишутся в режиме «что есть и куда идём».
**Без журналов прошлого**: без changelog'ов внутри prose, без следов миграций,
без ссылок на отменённые решения, без дат в комментариях, без «было X —
стало Y», без имён переходных фаз.

Когда эволюция вынесла факт — упоминание **удаляется**, не сопровождается
пометкой «устарело». История живёт в `git log`, не в тексте файлов.
Правило важнее, чем «не сломать кросс-ссылку»: ссылка на упразднённую
сущность удаляется вместе с упоминанием. Подробнее —
`.claude/rules/forward-only.md`.

## 2. Слои и терминология

Бизнес, его сегменты/работы и реестр его проблем — общие (top-level);
продуктовые слои — по проекту. Рекомендуемый вход во все слои —
оркестраторы `/entrypoint` (аналитик) и `/entrypoint-for-business`
(клиент): они классифицируют сырьё и маршрутизируют к исполнителям ниже
(прямой вызов исполнителя тоже допустим):

| слой | вопрос | вход |
|---|---|---|
| `docs/business/` | **кто этот бизнес заказчика, какие его проблемы решаем и кто в нём принимает решения** | `/business-deep-dive` (аналитик); клиент — `/entrypoint-for-business` |
| `docs/ajtbd/` | **кто наш сегмент по работам, его граф работ и трения** | `/segment-deep-dive` · `/job-graph-deep-dive` · `/jtbd-interview` (аналитик); клиент — `/entrypoint-for-business` |
| `docs/swot/` | **за счёт чего возможен следующий шаг** (факторы → ставки) | `/swot-deep-dive` |
| `docs/hypothesis-map/` | **под какие метрики целимся** (цель → метрика → субъект → гипотеза) | `/hypothesis-map-deep-dive` |
| `docs/projects/<slug>/` | **зачем продукт и для кого** (vision + реестр-хребет `surface` + kind + `capability/<surface>`) | `/project-deep-dive <slug>` (аналитик); клиент — `/entrypoint-for-business` |
| `docs/projects/<slug>/interface/<surface>/` | **как пользователь взаимодействует** (по поверхности) | `/interface-deep-dive <slug> [<surface>]` |
| `docs/projects/<slug>/domains/` | **какой бизнес-код бэкенда** (опц.; по bounded-context) | `/domain-deep-dive <slug> <ctx>` |
| `docs/projects/<slug>/screens/<surface>/` | **как это выглядит и компонуется** (по поверхности) | `/screen-deep-dive <slug> [<surface>]` |
| `docs/projects/<slug>/telegram-bot-flow/<surface>/` | **как бот ведёт диалог** (по bot-поверхности: диалоги · окна · команды · уведомления) | `/telegram-bot-flow-deep-dive <slug> [<surface>]` |
| `docs/projects/project-map.md` | **как продукты бизнеса стыкуются** | сводится из `integration`, сверяет `/cross-audit` |

Канон формы продуктовых слоёв
(project/interface/screens/telegram-bot-flow/domains/project-map)
живёт один раз в `docs/projects/_template/`; данные — в папках проектов. Скилы
этих слоёв принимают `<project-slug>` первым аргументом (без него — пикер **по
человекочитаемым именам** проектов, исключая `_template`); interface и screen
берут вторым аргументом поверхность (без неё — пикер по именам из `surface.md`).
Клиент-режим — дружелюбные пикеры «какой продукт обсуждаем» и «где он работает».

**Дружелюбие к аналитику (нейминг).** Жаргон (`slug`/`kind`/`draft`/`stable`)
аналитику виден, но он не обязан в нём *думать* или его *придумывать*: скилл
сам выводит `slug` из человекочитаемого `name` (транслит в kebab-case), пикеры
показывают имена, а `kind:slug` — лишь опциональный ускоритель. Канон —
`.claude/rules/naming.md` (аналитическая сторона клиентского
`entrypoint-for-business/references/business-language.md`).

Связи между слоями **семантические**, не slug-валидируемые: профиль и
конкуренты бизнеса (business) питают факторы SWOT (`swot/factor`),
текущая метрика (`business/current-metric`) становится baseline целевой
(`hypothesis-map/metric`); сегмент по работам (ajtbd) проявляется как
`subject` (hypothesis-map) и как `user` продукта, трение сегмента
(`ajtbd/segment-problem`) доказывает проблему бизнеса
(`business/business-problem`) и `vision.Problem`, Big/Core-работа целит в
`vision.Success`, механики ценности графа работ — кандидаты в
`capability`, нанятое решение (`ajtbd/solution`) сопоставляется с
`competitor`/`offering`; ставка SWOT (`swot/bet.promoted-to`)
дотягивается до цели/гипотезы Карты гипотез; проблема ↔ продукт — **M:N**
(`projects/<slug>/vision.addresses-problem`); цель/метрика/субъект
(hypothesis-map) проявляются как vision/user/capability в проекте; user
адресата проявляется как роль who (interface), `capability/<surface>`
реализуется через situation той же поверхности + domain; surface —
ось партиционирования interface/screens/capability; integration раскрывается
в функции (бизнес-каталог в `integration.md`), их конкретный клиент живёт в
`domains/_shared/integrations/<slug>/`, а use-case дёргает функции по `slug`
(transport-agnostic; стык продуктов бизнеса ведёт `project-map`); в
bot-поверхности окно (window) реализует блок interface, действие виджета и
источник данных окна ссылаются на use-case домена
(`use-case:<ctx>.<Operation>`), а уведомление (notification) триггерится
доменным событием (`event:<ctx>.<Event>`) — бот остаётся фронтендом без
собственных бизнес-правил.
Сквозные рёбра авторятся **снизу-вверх** (проектная/UX-сущность
ссылается на глобальную: `situation.jobs`/`capabilities`/`hypotheses`,
`capability.jobs`/`hypotheses`, `user.segments`, `subject.segments`);
обратную сторону и несостыковки сводит `/cross-audit` через рой агентов
(по каждому проекту).

**Юридическая рамка** (реестр проблем `business-problem` в слое business):
гарантируем **доставку проекта на 100% по scope**; метрики — **совместный
с бизнесом best-effort таргет**, не гарантия исхода (есть внешние
факторы). Граница «гарантируем / целимся / вне контроля» — в строке
`docs/business/business-problem.md` (реестр проблем, по строке на
проблему). Метрика **никогда** не подаётся как гарантия.

Каноны терминов — в README каждого слоя. Канон терминов компонентов
и craft — в библиотеке `@stit/ui`. Английский в backticks —
только для устоявшегося канона (`a11y`, DTCG, FSD-слои, `data-*`,
`aria-busy`, DDD-термины — `aggregate` · `value object` · `use-case` ·
`event` · `policy` · `bounded-context`, имена обязательных H2-секций
domains-шаблонов, которые парсит `<org>/backend`, а также структурные
идентификаторы telegram-bot-flow, которые читает `<org>/<bot>`:
`states-group` · `state` · `id` виджетов · ключи getter'а). Эти структурные
идентификаторы **не переименовываем** — они часть handoff-контракта. Всё
остальное — prose, пояснения, человекочитаемые поля — по-русски, без
полу-калек («пропсы», «варианты-проперти»).

Business-слой (нестрогая картина + строгие реестры): 1 singleton
`profile.md` + 5 табличных kind (`offering`, `channel`, `competitor`,
`current-metric`, `material`) + строгий реестр проблем `business-problem`
(таблица проблем + граница гарантии) + 2 строгих kind стейкхолдеров
(`stakeholder` · `stakeholder-map`). Источник истины — материалы клиента и
рой web-research, не проекция аналитика. Связи семантические. Питает
факторы `swot/factor` и baseline метрик `hypothesis-map/metric`. Сегменты
живут в слое AJTBD: `offering.for-segment` и `channel.serves-segment`
ссылаются на `ajtbd/segment`. Провенанс-поля `*.from-project` (у
`offering`, `current-metric`, `business-problem`) несут восходящий поток —
что проявил дозревший продукт.

Стейкхолдеры (строгие, **многоинициативные**): бизнес — это **люди,
принимающие решения**, а не абстракция. `stakeholder` — **конкретное лицо**
(или именованное «кресло») внутри заказчика или ближнего контура
(партнёр/регулятор/инвестор), с ролью в сделке (`lpr` · `budget-holder` ·
`lvr` · `recommender` · `gatekeeper` · `end-user` · `sponsor`), осями
власть/интерес (Mendelow), стойкой (`champion`…`blocker`), личными
драйверами/страхами, личным `win` (тот же B2B-инсайт «90% мотивации —
личное») и **стратегической стойкой** (`strategic-stance` — куда властное
лицо хочет/не хочет движения бизнеса; минимизация: ровно столько про
взгляды, чтобы сверить стратегию с людьми, не биография). `stakeholder-map`
— сборка по инициативе: сетка власть/интерес, **граф связей**
(`influence-edges`: влияние/союзы/конфликты/блок), **путь вовлечения** (кого
в каком порядке провести к «да»), стратегия и риски; несёт массив
`business-problem` (M:N). Это **единственное место**, где репозиторий пишет
конкретных лиц (намеренное исключение из «роль, не лицо»), и оно **вне
handoff-контракта** (`business/` не читает ни один код-репо — PII не
уезжает в backend/frontend/infra). `stakeholder` смотрит **внутрь**
заказчика (политика проекта) — в отличие от `segment`/`user`/`who`/`subject`,
смотрящих наружу; один человек обеими линзами — через `manifests-as`.
Методологические инварианты карты (без ЛПР/держателя бюджета, властный
блокер без митигации, разрыв пути вовлечения, цикл `reports-to`) держит
draft→stable-гейт `/business-deep-dive`; сверку `strategic-stance` со
ставками (`swot/bet`) и целями (`hypothesis-map/goal`), чтобы стратегия не
шла против ключевых лиц, ведёт рой `/cross-audit` (углы `stakeholder-*`).

AJTBD-слой (строгий, методология, **разведочный**): по Advanced JTBD
(Иван Замесин) — кто наш сегмент по работам, а не по демографии. 5
табличных kind: `segment` (бандл Core Jobs + 1 Big Job + критерии + Score),
`job` (работа когда/хочу/чтобы; `level` big|core|low; 6 типов работ),
`job-graph` (сборка дерева по сегменту: целевая работа, CPR, 11 механик
ценности → кандидаты в `capability`), `solution` (что «нанято» на работу:
satisfaction, цена↔ценность), `segment-problem` (трение сегмента с
решением: сила 1–10, драйверы, барьеры). Ядро: проблема **никогда** не
существует сама по себе — она следствие конкретного `solution`, нанятого
на `job`. Источник истины — многоволновой рой web-research (5–10 агентов
× 2–5 волн) и опц. JTBD-интервью (`/jtbd-interview`, собирает сырьё в ветку
`entrypoint/state/ajtbd/_interview/` → intake), не проекция аналитика. Связи семантические; инварианты
(сегмент без Big Job, разрыв «чтобы», трение без решения, Score без
компонентов, CPR с разрывом, ложная работа) ловит рой `/ajtbd-audit` — **в
пределах каждого сегмента**, не grep. Сегмент несёт `served` (`served` |
`prospective`) — проспективный сегмент описывает рынок, который бизнес ещё
не обслуживает. **`ajtbd/segment-problem` (проблема клиента) ≠
`business/business-problem` (проблема бизнеса)**: первое питает второе как
доказательство.

SWOT-слой (строгий, LinkedSWOT, **многопроблемный**): `docs/swot/` — 2
табличных kind `factor` (сильная/слабая сторона · тренд/угроза — само по
себе не действие) и `bet` (стратегическая ставка «`действие`, чтобы
`ценность`»; держится на ≥1 внутреннем + ≥1 внешнем факторе; `promoted-to`
доводит до `goal`/`hypothesis`). Каждая запись несёт массив `business-problem` (M:N
к строкам реестра `business/business-problem`). Связи семантические;
методологические инварианты (баланс факторов, ставка-висяк `promoted-to`,
фактор без ставки, приоритет без дублей) ловит рой `/swot-audit` — **в
пределах каждой проблемы**, не grep.

Карта-гипотез-слой (строгий, методология, **многопроблемный**):
`docs/hypothesis-map/` — 5 табличных kind `goal` · `metric` · `subject` ·
`hypothesis` · `task`, причинная цепь «воздействие → поведение субъекта →
метрика»: цель (критерий успеха без цифр) → метрика (best-effort таргет с
baseline, источником, атрибуцией, приёмкой) → субъект (носитель
самодвижения) → гипотеза → задача проверки. `hypothesis` — исключение:
вместо `description` четыре части `if`/`then`/`because`/`so`; «тогда» (so)
бьёт в метрику цели. Каждая запись несёт массив `business-problem` (M:N к строкам
реестра `business/business-problem`). Связи семантические;
методологические инварианты (задача-сирота, «тогда» без метрики, метрика
без влияния, целевая без guardrail, цель без метрики, исполнитель вместо
субъекта, проблема без цели) ловит рой `/hypothesis-map-audit` — **в
пределах каждой проблемы**, не grep.

Project-слой (по проекту), **ось — поверхность (surface)**: у каждого
проекта в `docs/projects/<slug>/` — 1 singleton `vision.md`, реестр-хребет
`surface.md` (объявляет поверхности; его slug'и партиционируют
capability/interface/screens), кросс-поверхностные табличные kind (`user`,
`integration`, `boundary`, `constraint`, `market`) и папка возможностей
`capability/<surface>.md` (по файлу на поверхность; связь capability →
surface структурная). Один проект (папка) = один продукт = один `vision.md`;
разные продукты — разные папки. `vision` несёт `addresses-problem` (массив,
M:N к строкам реестра `business/business-problem`), оси `audience` /
`intent` / `market-maturity` и `lifecycle` проекта — отдельно от `status`
зрелости записи; переход `lifecycle → stable` запускает восходящий поток к
business. `integration` несёт две таблицы — провайдеры (`surface`, `target`
`external` | `sibling-project`) и их функции (бизнес-каталог «что умеет»);
межпроектный стык авторится здесь и сводится в `docs/projects/project-map.md`
(бизнес-язык). Конкретный клиент функций — в `domains/_shared/integrations/`,
потребление — в use-case (колонка `functions`). Канон формы —
`docs/projects/_template/project/`. Связи внутри слоя семантические (кроме
структурной capability↔surface), валидируется `/project-audit <slug>`.
Vision — singleton с разделами `Problem`, `Success`, `Non-goals`; остальные
— таблицы. Без frontmatter (kind = имя файла); `status` — отдельная строка
в vision или последняя колонка в таблицах.

Interface-слой (по проекту, **по поверхности**):
`docs/projects/<slug>/interface/<surface>/` — папка на каждую поверхность из
реестра, внутри 7 плоских md-файлов, каждый — таблица сущностей одного типа
(`who`, `stage`, `situation`, `zone`, `block`, `ux-substrate`, `data-items`).
Все ссылки **внутри слоя** — через `slug` (валидируемо), **в пределах одной
поверхности**; `data-items` surface-локален (кросс-поверхностную сверку
датумов ведёт `/cross-audit`). Связь ситуаций и блоков — через
`ux-substrate.situation` + `block.ux-substrates` (M:N выводимо). Навигация:
внутри зоны блоки достижимы взаимно неявно; межзонные/нестандартные переходы
— через `block.transition-to-block` (исходящие) и `block.transition-from-zone`
(входящие). Вложенность зон — через `zone.parent-zone`.

## 3. Экспертиза — священна на всех слоях

Агент **не пишет** доменные / продуктовые / craft-формулировки из
своей головы.

- **Бизнес-проблемная** (business / swot / hypothesis-map): профиль и текущие
  числа бизнеса, факторы SWOT, ставки, цель, метрика (формула, источник
  истины, атрибуция, критерий приёмки), субъект и его мотивация,
  гипотезы — только от бизнеса / аналитика, через `AskUserQuestion`.
  Метрика — best-effort таргет, **не гарантия**. Факты о бизнесе — из
  материалов клиента / подтверждённого research, не из головы.
  Anti-patterns как опции — да; тексты — нет.
- **Стейкхолдерская** (business / stakeholder): имена и кресла, роль в
  сделке, власть/интерес, стойка, **личные драйверы/страхи и личный win**,
  связи между людьми (влияние/союзы/конфликты), путь вовлечения — только из
  материалов клиента / интервью, через `AskUserQuestion`. Психографику
  лица **не выдумывать**: «не отбить ROI» как страх CFO пишется, только
  если так сказал клиент. Anti-patterns как опции — да; тексты — нет.
- **AJTBD** (ajtbd): формулировки сегментов, работ (когда/хочу/чтобы),
  нанятых решений, трений, драйверов/барьеров и мотиваций — только от
  аналитика / из подтверждённого research / из транскриптов интервью,
  через `AskUserQuestion`. Работа доказывается **прошлым поведением**
  (затраты времени/денег), не гипотетикой. Anti-patterns как опции — да;
  тексты — нет.
- **Продуктовая** (project): vision, jobs, pains, value, why, source —
  только от бизнеса / аналитика, через `AskUserQuestion`. Anti-patterns
  как опции — да; тексты — нет.
- **UX-доменная** (interface): goal, action, when, using-what — только
  от аналитика, не от модели.
- **Бизнес-домен** (domains): инварианты, preconditions, business
  rules — только от архитектора.
- **Craft** (компоненты, цвет, пространство, типографика, движение,
  a11y): живёт в библиотеке `@stit/ui`, наполняется ответами
  owner. Облик в макете — из craft-экспертизы, не «на глаз».

Неоднозначность вне покрытия → вопрос человеку, не угадывание.

## 4. Авто-память отключена

Запись в `~/.claude/projects/*/memory/` запрещена детерминированно
(глобальные настройки). Не предлагать «сохранить в память». Каталог
памяти, если попал в контекст, — read-only артефакт.

Постоянное «помни между сессиями» — в репо: `CLAUDE.md`,
`.claude/rules/<topic>.md`, единый state оркестраторов
(`.claude/skills/entrypoint/state/` для аналитика,
`.claude/skills/entrypoint-for-business/state/` для клиента; исполнители
пишут в свои ветки этого дерева) — коммитятся, это shared проектная
память.

## 5. Авторизация правок

Правки артефактов делаются свободно. Уточнять — ТОЛЬКО если правка
способна:

- сломать накопленную продуктовую модель (vision/user/capability —
  основу остальных слоёв);
- сломать накопленную craft-экспертизу библиотеки;
- несовместимо раскатиться вширь (контракт артефактов всех слоёв,
  форма публичного API библиотеки, таксономия токенов).

Гейты прогонять всегда (`/swot-audit`, `/hypothesis-map-audit`,
`/ajtbd-audit`, `/project-audit <slug>`, `/interface-audit <slug>`,
`/screen-audit <slug>`, `/telegram-bot-flow-audit <slug>`, и/или
`/cross-audit` перед коммитом, если трогали
несколько слоёв). **Коммит / push — гейт человека.** Без явной просьбы
агент не коммитит.

## 6. Зоны правок

- **Артефакты бизнеса** (`docs/business/`) — через скилл
  `business-deep-dive` (аналитик); клиент-режим — оркестратор
  `entrypoint-for-business` ведёт сам через призму `business-profile.md`.
  Форма — по `docs/business/README.md`. Нестрогий слой: приём материалов
  клиента + рой web-research конкурентов (доступен и клиенту). Сквозная
  проверка — `cross-audit`.
- **Артефакты AJTBD** (`docs/ajtbd/`) — сегменты через скилл
  `segment-deep-dive`, граф работ, решения и трения через
  `job-graph-deep-dive` (аналитик); клиент-режим — оркестратор
  `entrypoint-for-business` ведёт сам (призмы `clients-segments.md` /
  `clients-jobs.md`), с эскалацией и push в единую ветку `client`. Форма —
  по `docs/ajtbd/README.md`. Строгая разведочная методология Advanced JTBD;
  наполняется многоволновым роем web-research и опц. JTBD-интервью
  (`jtbd-interview` — отдельный тяжёлый процесс по явному запросу, собирает
  сырьё в ветку `entrypoint/state/ajtbd/_interview/`, выход разбирается
  через intake). Семантический аудит
  инвариантов роем (по каждому сегменту) — `ajtbd-audit`. Трение сегмента
  (`segment-problem`) питает проблему бизнеса (`business/business-problem`),
  не подменяет её.
- **Реестр проблем бизнеса** (`business-problem` в `docs/business/`) —
  через скилл `business-deep-dive` (часть бизнес-слоя); таблица проблем +
  граница гарантии/таргета (`business-problem` — массив M:N, на который ссылаются
  swot / hypothesis-map / `vision.addresses-problem`).
- **Стейкхолдеры** (`stakeholder` · `stakeholder-map` в `docs/business/`)
  — через скилл `business-deep-dive` (фаза `stakeholders`, часть
  бизнес-слоя); клиент-режим — оркестратор `entrypoint-for-business` ведёт
  сам (призма `stakeholders.md`). Форма — по `docs/business/README.md`.
  Конкретные лица (намеренное исключение из «роль, не лицо»), вне
  handoff-контракта. Инварианты карт держит draft→stable-гейт
  `business-deep-dive`; сверку стратегической стойки со swot/hypothesis-map
  роем — `/cross-audit` (углы `stakeholder-*`). `stakeholder` (человек
  внутри заказчика) ≠ `segment`/`user`/`who`/`subject` (люди снаружи);
  связь — `manifests-as`.
- **Артефакты SWOT** (`docs/swot/`) — через скилл `swot-deep-dive`; форма
  — по `docs/swot/README.md`. Строгая многопроблемная методология
  LinkedSWOT (`factor` · `bet`). Семантический аудит инвариантов роем (по
  каждой проблеме) — `swot-audit`.
- **Артефакты Карты гипотез** (`docs/hypothesis-map/`) — через скилл
  `hypothesis-map-deep-dive`; форма — по `docs/hypothesis-map/README.md`.
  Строгая многопроблемная методология Карты гипотез (`goal` · `metric` ·
  `subject` · `hypothesis` · `task`). Семантический аудит инвариантов роем
  (по каждой проблеме) — `hypothesis-map-audit`. Метрика — best-effort
  таргет, не гарантия. В клиент-режиме SWOT и Карту гипотез — как и все
  темы — ведёт сам оркестратор `entrypoint-for-business` через свою призму
  (`swot-hypothesis-map.md`); отдельных клиентских под-скилов нет.
- **Артефакты продукта** (`docs/projects/<slug>/`) — через скилл
  `project-deep-dive <slug>` (аналитик); клиент-режим — оркестратор
  `entrypoint-for-business` ведёт сам (призма `product.md`), с эскалацией и
  push в единую ветку `client`; форма — по
  `docs/projects/_template/project/README.md`. Ось — поверхность
  (`surface.md` реестр; `capability/<surface>.md` по файлу на поверхность).
  `vision.addresses-problem` связывает продукт с проблемами (M:N);
  `integration` несёт `surface` + `target` (`external`|`sibling-project`).
  Узкий аудит — `project-audit <slug>`. Сквозная семантическая проверка со
  всеми слоями (business/ajtbd/swot/hypothesis-map/interface/domain/screen,
  по поверхности) + межпроектные стыки (`project-map`) — `cross-audit`
  (рой агентов, по каждому проекту).
- **Карта проектов** (`docs/projects/project-map.md`) — граф стыков между
  продуктами бизнеса на бизнес-языке; авторская сторона рёбер — `integration`
  с `target: sibling-project`; singleton (канон формы + данные в одном файле,
  без технических подробностей стыка); сверяет `cross-audit`.
- **Артефакты аналитики интерфейса** (`docs/projects/<slug>/interface/<surface>/`)
  — через скилл `interface-deep-dive <slug> [<surface>]`; форма — по
  `docs/projects/_template/interface/README.md` (канон слоя; форма одной
  папки поверхности — в подпапке `_template/`). Поиск тупиков, рассинхрона зеркал, битых ссылок и
  семантических подозрений — скилл `interface-audit <slug>`. Связь
  zone/situation с поверхностью теперь структурная (папка). При заведении
  ключевых сущностей (who, situation) скилл предлагает связь с продуктовыми
  артефактами того же проекта как контекст (см.
  `interface-deep-dive/references/project-context.md`).
- **Артефакты доменов** (`docs/projects/<slug>/domains/`, если
  присутствуют) — через скилл `domain-deep-dive <slug> <ctx>`; по
  bounded-context, surface-агностичны. При заведении контекста / use-case
  предлагается связь с `capability/<surface>` того же проекта; внешние и
  межпроектные интеграции — через конкретный клиент
  `domains/_shared/integrations/<slug>/` (kind `integration-client`:
  транспорт + функции) и потребление функций в use-case (колонки
  `integration` + `functions` в `Dependencies`); домен transport-agnostic.
- **Артефакты диалогов бота** (`docs/projects/<slug>/telegram-bot-flow/<surface>/`,
  для поверхностей с `type: bot` — вместо screens) — через скилл
  `telegram-bot-flow-deep-dive <slug> [<surface>]`; форма — по канону
  `docs/projects/_template/telegram-bot-flow/README.md` и README'ям kind
  (dialog/window — папки с `index.md`; command/notification — плоские
  реестры-таблицы). Окно зеркалит блок interface той же поверхности
  (`interface-block`, `ux-substrates`); действия и данные ссылаются на
  use-case домена, уведомления — на доменные события; структурные
  идентификаторы контракта (`states-group`, `state`, `id` виджетов,
  ключи getter'а) — английские, тексты сообщений — русские. Stable-артефакты
  читает форк `telegram-bot-template` (`<org>/<bot>`). Узкий аудит слоя
  (зеркала, граф, контракты данных, инварианты Telegram) —
  `telegram-bot-flow-audit <slug>`; сквозную сверку
  (interface ↔ диалоги ↔ domains) ведёт `/cross-audit` (углы
  `surface-botflow` · `botflow-domain`).
- **Артефакты экранов** (`docs/projects/<slug>/screens/<surface>/`) — через
  скилл `screen-deep-dive <slug> [<surface>]`; форма — по
  `docs/projects/_template/screens/README.md` (канон слоя; форма одной папки
  поверхности — в подпапке `_template/`) и README'ям 4 kind
  (flow/screen/block/shell). Визуальные референсы и ассеты
  живут в `docs/projects/<slug>/screens/<surface>/assets/<kind>/<slug>/`.
  Поиск тупиков, рассинхрона зеркал (внутри screens и с `interface/<surface>/`
  того же проекта), битых ссылок, нарушений slot-fills/accepts и
  семантических подозрений — скилл `screen-audit <slug>`. Связь flow/shell с
  поверхностью теперь структурная (папка).
- **Библиотека** — в отдельном репо `ui-lib` как `@stit/ui`;
  проект её потребляет, не правит.
- **Sweep'ы** (терминология, чистка): 1 агент = 1 непересекающаяся зона.

## 7. Клиент-режим (`entrypoint-for-business`)

Когда сессию ведёт **клиент / основатель / PO**, не аналитик — вход один:
клиентский оркестратор `/entrypoint-for-business` (зеркало `/entrypoint` в
бизнес-языке). Он принимает рассказ и материалы, раскладывает по темам и
**ведёт все темы сам через свою призму** — отдельных клиентских
под-скилов нет. Для каждой темы берёт призму-методичку в бизнес-языке
(`references/business-profile.md` · `stakeholders.md` · `clients-segments.md` ·
`clients-jobs.md` · `swot-hypothesis-map.md` · `product.md`) и read-only
сверяется со строгой подложкой обычного аналитического скила того же слоя
(обычные скилы в клиент-режиме **не активируются**). Клиенту доступен и рой
web-research (`references/research-business.md`). Особенности, которые
влияют на работу:

- **Бизнес-язык**: никакого `slug`, `kind`, `draft`, `stable`,
  `artifact` в чате. Видно только «закрыто / в работе». Продукт
  выбирается дружелюбным пикером «какой продукт обсуждаем», без папок и
  slug.
- **Anti-patterns из реальных провалов**, не из методичек (см.
  `entrypoint-for-business/references/anti-patterns-real.md`).
- **Метрика — не гарантия** (Карта гипотез): клиент-скилл никогда не
  помогает записать метрику как обещание-гарантию, только как цель;
  строгую измеримость (атрибуция, критерий приёмки) мягко откладывает
  аналитику.
- **Эскалация**: state-маркер `**жду аналитика**` + push в единую ветку
  `client` через `--share` с явного согласия клиента. Доступ к репозиторию
  (логин/пароль) скилл запрашивает один раз на устройстве и сохраняет —
  дальше push идёт молча. Уезжают: артефакты слоя (`docs/business/`,
  `docs/ajtbd/`, `docs/swot/`, `docs/hypothesis-map/` или выбранного
  продукта `docs/projects/<slug>/`),
  state клиента, `client-handoff/summary.md` (живой срез, держится
  актуальным и чистится от мусора), `client-handoff/transcripts/<YYYY-MM-DD>--<HH-MM>--<тема>.md`
  (человекочитаемое имя; полный лог сессии с предложенными вариантами).
- **Единый контекст (read-only)**: чтобы картина была общей и понятной,
  любой скилл read-only видит **оба дома** state — аналитический
  `entrypoint/state/` и клиентский `entrypoint-for-business/state/`;
  проектные ветки — только по текущему продукту (изоляция продуктов
  сохраняется). В чужой дом / чужую ветку **никто не пишет**. **Anti-leak (клиент-режим)**: прочитанное из кухни
  аналитика — тихий контекст; сырые открытые вопросы, черновые гипотезы,
  доменные решения и термины (`slug/draft/stable`) клиенту не зачитываются,
  только переводятся в бизнес-язык (видно по-прежнему «закрыто / в работе»).
- **Никакого `--no-verify`**. Если хук упал — спросить клиента, что
  делать.

## 8. Язык общения

Глобально — ответы только на русском (см. `~/.claude/CLAUDE.md`).
Технические идентификаторы (имена файлов / функций / переменных /
команд / флагов, содержимое коммитов и PR) — как есть. Комментарии в
коде — на языке окружающего кода.
