# Канон проекта

Файл автоматически загружается в каждую сессию `Claude Code`. Здесь —
невыборочные правила, которые работают всегда.

Этот репозиторий — **проектный шаблон**. Поток сверху вниз: бизнес
заказчика (`docs/business/`) — самый верх; он же держит **реестр проблем
бизнеса** (`business-problem` — таблица проблем, по строке на проблему).
Под ним слой **AJTBD** (`docs/ajtbd/`) — кто наш сегмент по работам и его
граф работ (методология Advanced JTBD), питающий проблемы трениями
сегмента. По строгой методологии **LinkedSWOT** реестр проблем
разворачивается в слой `docs/swot/` (`factor` · `bet`), а по **Карте
гипотез** — в слой `docs/hypothesis-map/` (`goal` · `metric` · `subject` ·
`hypothesis` · `task`); оба — **многопроблемные**. Под проблемы встают
**продукты**: несколько проектов под одним бизнесом, у каждого своя папка
`docs/projects/<slug>/` — корень решения. Внутри
проекта: продукт (`vision` + 7 kind), аналитика интерфейса (`interface/`)
— UX над продуктом, опционально бизнес-домены (`domains/`) и
композиция/облик (`screens/`), по которой собирается кликабельный hi-fi
субстрат на библиотеке `@sftbmb/ui`. Канон формы продуктовых слоёв —
один раз в `docs/projects/_canon/`. См.:

- `README.md` — карта репозитория и воркфлоу.
- `docs/business/README.md` — канон 1 singleton + 5 kind бизнеса +
  реестр проблем `business-problem`.
- `docs/ajtbd/README.md` — канон 5 kind AJTBD: `segment` · `job` ·
  `job-graph` · `solution` · `segment-problem`.
- `docs/swot/README.md` — канон LinkedSWOT: `factor` · `bet`; колонка-ссылка
  `business-problem` — массив, M:N к реестру проблем бизнеса.
- `docs/hypothesis-map/README.md` — канон Карты гипотез: `goal` ·
  `metric` · `subject` · `hypothesis` · `task`; `business-problem` — массив, M:N.
- `docs/projects/README.md` — как устроены проекты: `_canon`, выбор
  проекта, связь `addresses-problem` (M:N) с проблемами.
- `docs/projects/_canon/project/README.md` — канон 1 vision + 7
  артефактов продукта.
- `docs/projects/_canon/interface/README.md` — канон 7 артефактов
  интерфейса.
- `docs/projects/_canon/domains/README.md` — канон DDD-артефактов бэкенда
  (если есть).
- `docs/projects/_canon/screens/README.md` — канон 4 kind артефактов
  экранов.

Артефакты — чистая аналитика; на FSD/компоненты напрямую не мапятся.
Превращение `docs/projects/<slug>/screens/` в wireframe и hi-fi — ручная
работа автора макета, не отдельный артефакт.

Карта документации и handoff-контракт соседям — `docs/README.md`. Путь
потребителя форка — `docs/getting-started.md`.

## Где это в экосистеме

Это один из **5 форкаемых шаблонов** под `sftbmb-core/`:
`corp-infra-template` (корп control-plane), `go-backend-template`
(→ `<org>/backend`), `spa-frontend-template` (→ `<org>/frontend`),
**`project-docs-template`** (этот → `<org>/docs`),
`project-infra-template-compose` (→ `<org>/infra`). Рядом — 2 общие библиотеки:
Go-lib `sftbmb-core/golibinfra` и дизайн-система `@sftbmb/ui` из репо
`sftbmb-core/ui-lib`. Корп control-plane `corp-infra-template`: вендор-лока нет —
managed (инстанс на `*.sftbmb.ru`) или self-hosted (ваш форк). Канон контрактов
(в т.ч. self-hosted) — `corp-infra-template/docs/ecosystem.md`.

**Роль docs-репо — design-time SoT проекта.** Форкается **первым**
(Gitea → `sftbmb-core/project-docs-template` → **Use this template** →
`<org>/docs`), наполняется аналитикой, и только потом форкаются код-репо,
которые **читают** его stable-артефакты как upstream (read-only,
односторонне):

- `<org>/backend` ← `projects/<slug>/domains/<ctx>/` (scaffold доменов в Go;
  маппинг DDD → Go живёт у backend в `docs/reference/domain-mapping.md`);
- `<org>/frontend` ← `projects/<slug>/{interface,screens}/` (fsd-deep-dive);
- `<org>/infra` ← `projects/<slug>/{vision,surface}` (init-project).

Контракт что docs отдаёт соседям — `docs/README.md § Что docs отдаёт
соседям`. Рекомендуемый вход — два оркестратора `/entrypoint` (аналитик)
и `/entrypoint-for-business` (клиент): принимают сырьё, классифицируют по
слоям и маршрутизируют к рою deep-dive/audit-исполнителей (прямой вызов
исполнителя тоже допустим — `docs/getting-started.md`). Когда аналитика
заполнена, `/de-template` вычищает показной `docs/projects/example/` и
шаблон-нарратив под идентичность проекта.

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
| `docs/business/` | **кто этот бизнес заказчика и какие его проблемы решаем** | `/business-deep-dive` (аналитик); клиент — `/entrypoint-for-business` |
| `docs/ajtbd/` | **кто наш сегмент по работам, его граф работ и трения** | `/segment-deep-dive` · `/job-graph-deep-dive` · `/jtbd-interview` (аналитик); клиент — `/entrypoint-for-business` |
| `docs/swot/` | **за счёт чего возможен следующий шаг** (факторы → ставки) | `/swot-deep-dive` |
| `docs/hypothesis-map/` | **под какие метрики целимся** (цель → метрика → субъект → гипотеза) | `/hypothesis-map-deep-dive` |
| `docs/projects/<slug>/` | **зачем продукт и для кого** | `/project-deep-dive <slug>` (аналитик); клиент — `/entrypoint-for-business` |
| `docs/projects/<slug>/interface/` | **как пользователь взаимодействует** | `/interface-deep-dive <slug>` |
| `docs/projects/<slug>/domains/` | **какой бизнес-код бэкенда** (опц.) | `/domain-deep-dive <slug>` |
| `docs/projects/<slug>/screens/` | **как это выглядит и компонуется** | `/screen-deep-dive <slug>` |

Канон формы продуктовых слоёв (project/interface/screens/domains) живёт
один раз в `docs/projects/_canon/`; данные — в папках проектов. Скилы этих
слоёв принимают `<project-slug>` первым аргументом (без него — пикер по
`docs/projects/`, исключая `_canon`); клиент-режим — дружелюбный пикер
«какой продукт обсуждаем».

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
адресата проявляется как роль who (interface), capability реализуется
через situation + domain, surface несёт zones, integration — адаптеры в
domain. Сквозные рёбра авторятся **снизу-вверх** (проектная/UX-сущность
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
и craft — в библиотеке `@sftbmb/ui`. Английский в backticks —
только для устоявшегося канона (`a11y`, DTCG, FSD-слои, `data-*`,
`aria-busy`). Всё остальное — по-русски, без полу-калек («пропсы»,
«варианты-проперти»).

Business-слой (нестрогий): 1 singleton `profile.md` + 5 табличных kind
(`offering`, `channel`, `competitor`, `current-metric`, `material`) +
строгий реестр проблем `business-problem` (таблица проблем + граница
гарантии). Источник истины — материалы клиента и рой web-research, не
проекция аналитика. Связи семантические. Питает факторы `swot/factor` и
baseline метрик `hypothesis-map/metric`. Сегменты живут в слое AJTBD:
`offering.for-segment` и `channel.serves-segment` ссылаются на
`ajtbd/segment`. Провенанс-поля `*.from-project` (у `offering`,
`current-metric`, `business-problem`) несут восходящий поток — что проявил
дозревший продукт.

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

Project-слой (по проекту): у каждого проекта в `docs/projects/<slug>/` —
1 singleton `vision.md` + 7 табличных kind (`user`, `capability`,
`boundary`, `surface`, `integration`, `constraint`, `market`). Один
проект (папка) = один продукт = один `vision.md`; разные продукты —
разные папки. `vision` несёт `addresses-problem` (массив, M:N к строкам
реестра `business/business-problem`), оси `audience` / `intent` /
`market-maturity` (тип инициативы и зрелость рынка) и `lifecycle` проекта
— отдельно от `status` зрелости записи; переход `lifecycle → stable`
запускает восходящий поток к business. Канон формы —
`docs/projects/_canon/project/`. Связи внутри слоя семантические,
валидируется `/project-audit <slug>`. Vision —
singleton с разделами `Problem`, `Success`, `Non-goals`; остальные —
таблицы. Без frontmatter (kind = имя файла); `status` — отдельная строка
в vision или последняя колонка в таблицах.

Interface-слой (по проекту): `docs/projects/<slug>/interface/` — 7
плоских md-файлов, каждый — таблица сущностей одного типа (`who`,
`stage`, `situation`, `zone`, `block`, `ux-substrate`, `data-items`).
Все ссылки **внутри слоя** — через `slug` (валидируемо). Связь ситуаций
и блоков — через `ux-substrate.situation` + `block.ux-substrates` (M:N
выводимо). Навигация: внутри зоны блоки достижимы взаимно неявно;
межзонные/нестандартные переходы — через `block.transition-to-block`
(исходящие) и `block.transition-from-zone` (входящие). Вложенность зон —
через `zone.parent-zone`.

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
  a11y): живёт в библиотеке `@sftbmb/ui`, наполняется ответами
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
`/screen-audit <slug>`, и/или `/cross-audit` перед коммитом, если трогали
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
  `docs/projects/_canon/project/README.md`. `vision.addresses-problem`
  связывает продукт с проблемами (M:N). Узкий аудит — `project-audit
  <slug>`. Сквозная семантическая проверка со всеми слоями
  (business/ajtbd/swot/hypothesis-map/interface/domain/screen) —
  `cross-audit` (рой агентов, по каждому проекту).
- **Артефакты аналитики интерфейса** (`docs/projects/<slug>/interface/`)
  — через скилл `interface-deep-dive <slug>`; форма — по
  `docs/projects/_canon/interface/README.md`. Поиск тупиков, рассинхрона
  зеркал, битых ссылок и семантических подозрений — скилл
  `interface-audit <slug>`. При заведении ключевых сущностей (who,
  situation, zone) скилл предлагает связь с продуктовыми артефактами того
  же проекта как контекст (см.
  `interface-deep-dive/references/project-context.md`).
- **Артефакты доменов** (`docs/projects/<slug>/domains/`, если
  присутствуют) — через скилл `domain-deep-dive <slug>`; при заведении
  контекста / use-case предлагается связь с `capability` того же проекта,
  для адаптеров — с `integration`.
- **Артефакты экранов** (`docs/projects/<slug>/screens/`) — через скилл
  `screen-deep-dive <slug>`; форма — по
  `docs/projects/_canon/screens/README.md` и README'ям 4 kind
  (flow/screen/block/shell). Визуальные референсы и ассеты живут в
  `docs/projects/<slug>/screens/assets/<kind>/<slug>/`. Поиск тупиков,
  рассинхрона зеркал (внутри screens и с interface того же проекта),
  битых ссылок, нарушений slot-fills/accepts и семантических подозрений —
  скилл `screen-audit <slug>`. При заведении flow/shell скилл предлагает
  связь с `surface` того же проекта.
- **Библиотека** — в отдельном репо `ui-lib` как `@sftbmb/ui`;
  проект её потребляет, не правит.
- **Де-темплейтизация форка** — скилл `de-template`: один раз на свежем
  форке `<org>/docs` вычищает показной `docs/projects/example/` и
  шаблон-нарратив в `CLAUDE.md`/`README.md` под идентичность проекта. **Не
  трогает** пустые скелеты-каноны (`docs/projects/_canon/`, `docs/business/`,
  `docs/ajtbd/`, `docs/swot/`, `docs/hypothesis-map/`). На каноническом
  шаблоне не запускается (guard по origin).
- **Sweep'ы** (терминология, чистка): 1 агент = 1 непересекающаяся зона.

## 7. Клиент-режим (`entrypoint-for-business`)

Когда сессию ведёт **клиент / основатель / PO**, не аналитик — вход один:
клиентский оркестратор `/entrypoint-for-business` (зеркало `/entrypoint` в
бизнес-языке). Он принимает рассказ и материалы, раскладывает по темам и
**ведёт все темы сам через свою призму** — отдельных клиентских
под-скилов нет. Для каждой темы берёт призму-методичку в бизнес-языке
(`references/business-profile.md` · `clients-segments.md` ·
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
