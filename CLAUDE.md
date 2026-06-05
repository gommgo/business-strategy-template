# Канон проекта

Файл автоматически загружается в каждую сессию `Claude Code`. Здесь —
невыборочные правила, которые работают всегда.

Этот репозиторий — **проектный шаблон**. Поток сверху вниз: бизнес
заказчика (`docs/business/`) — самый верх; под ним слой **AJTBD**
(`docs/ajtbd/`) — кто наш сегмент по работам и его граф работ (методология
Advanced JTBD); его проблемы (`docs/business-problem/`) по строгой
методологии LinkedSWOT + Карта гипотез — слой **многопроблемный**
(`frame` — таблица проблем), питаемый трениями сегмента из AJTBD. Под
проблемы встают **продукты**: несколько проектов под одним бизнесом, у
каждого своя папка `docs/projects/<slug>/` — корень решения. Внутри
проекта: продукт (`vision` + 7 kind), аналитика интерфейса (`interface/`)
— UX над продуктом, опционально бизнес-домены (`domains/`) и
композиция/облик (`screens/`), по которой собирается кликабельный hi-fi
субстрат на библиотеке `@sftbmb/ui`. Канон формы продуктовых слоёв —
один раз в `docs/projects/_canon/`. См.:

- `README.md` — карта репозитория и воркфлоу.
- `docs/business/README.md` — канон 1 singleton + 5 артефактов бизнеса.
- `docs/ajtbd/README.md` — канон 5 kind AJTBD: `segment` · `job` ·
  `job-graph` · `solution` · `segment-problem`.
- `docs/business-problem/README.md` — канон: `frame` (таблица проблем) +
  7 артефактов (SWOT + Карта гипотез); `problem` — массив, M:N.
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
соседям`. Онбординг ведёт аналитик руками через рой deep-dive-скиллов —
оркестратора нет by design (`docs/getting-started.md`). Когда аналитика
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

Бизнес, его сегменты/работы и его проблемы — общие (top-level);
продуктовые слои — по проекту:

| слой | вопрос | вход |
|---|---|---|
| `docs/business/` | **кто этот бизнес заказчика** | `/business-deep-dive` (аналитик) или `/business-deep-dive-for-business` (клиент) |
| `docs/ajtbd/` | **кто наш сегмент по работам, его граф работ и трения** | `/segment-deep-dive` · `/job-graph-deep-dive` (+ `-for-business`) · `/jtbd-interview` |
| `docs/business-problem/` | **какие проблемы решаем и под какие метрики целимся** | `/business-problem-deep-dive` или `/business-problem-deep-dive-for-business` |
| `docs/projects/<slug>/` | **зачем продукт и для кого** | `/project-deep-dive <slug>` (аналитик) или `/project-deep-dive-for-business` (клиент) |
| `docs/projects/<slug>/interface/` | **как пользователь взаимодействует** | `/interface-deep-dive <slug>` |
| `docs/projects/<slug>/domains/` | **какой бизнес-код бэкенда** (опц.) | `/domain-deep-dive <slug>` |
| `docs/projects/<slug>/screens/` | **как это выглядит и компонуется** | `/screen-deep-dive <slug>` |

Канон формы продуктовых слоёв (project/interface/screens/domains) живёт
один раз в `docs/projects/_canon/`; данные — в папках проектов. Скилы этих
слоёв принимают `<project-slug>` первым аргументом (без него — пикер по
`docs/projects/`, исключая `_canon`); клиент-режим — дружелюбный пикер
«какой продукт обсуждаем».

Связи между слоями **семантические**, не slug-валидируемые: профиль и
конкуренты бизнеса (business) питают факторы SWOT (business-problem),
текущая метрика становится baseline целевой; сегмент по работам (ajtbd)
проявляется как `subject` (business-problem) и как `user` продукта,
трение сегмента (`ajtbd/segment-problem`) доказывает проблему бизнеса
(`frame`) и `vision.Problem`, Big/Core-работа целит в `vision.Success`,
механики ценности графа работ — кандидаты в `capability`, нанятое решение
(`ajtbd/solution`) сопоставляется с `competitor`/`offering`; проблема ↔
продукт — **M:N** (`projects/<slug>/vision.addresses-problem`);
цель/метрика/субъект (business-problem) проявляются как
vision/user/capability в проекте; user адресата проявляется как
роль who (interface), capability реализуется через situation + domain,
surface несёт zones, integration — адаптеры в domain. Несостыковки ловит
`/cross-audit` через рой агентов (по каждому проекту).

**Юридическая рамка** (слой business-problem): гарантируем **доставку
проекта на 100% по scope**; метрики — **совместный с бизнесом best-effort
таргет**, не гарантия исхода (есть внешние факторы). Граница «гарантируем
/ целимся / вне контроля» — в строке `docs/business-problem/frame.md`
(таблица проблем, по строке на проблему). Метрика **никогда** не подаётся
как гарантия.

Каноны терминов — в README каждого слоя. Канон терминов компонентов
и craft — в библиотеке `@sftbmb/ui`. Английский в backticks —
только для устоявшегося канона (`a11y`, DTCG, FSD-слои, `data-*`,
`aria-busy`). Всё остальное — по-русски, без полу-калек («пропсы»,
«варианты-проперти»).

Business-слой (нестрогий): 1 singleton `profile.md` + 5 табличных kind
(`offering`, `channel`, `competitor`, `current-metric`, `material`).
Источник истины — материалы клиента и рой web-research, не проекция
аналитика. Связи семантические. Питает SWOT-факторы и baseline метрик
слоя business-problem. Сегменты переехали в слой AJTBD: `offering.for-segment`
и `channel.serves-segment` ссылаются на `ajtbd/segment`.

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
× 2–5 волн) и опц. JTBD-интервью (`/jtbd-interview`, своё state/transcripts
→ intake), не проекция аналитика. Связи семантические; инварианты
(сегмент без Big Job, разрыв «чтобы», трение без решения, Score без
компонентов, CPR с разрывом, ложная работа) ловит рой `/ajtbd-audit` — **в
пределах каждого сегмента**, не grep. **`segment-problem` (проблема
клиента) ≠ `business-problem/frame` (проблема бизнеса)**: первое питает
второе как доказательство.

Business-problem-слой (строгий, методология, **многопроблемный**):
`frame.md` — таблица проблем (одна строка = одна проблема + граница
гарантии) + 7 табличных kind — SWOT-семья (`factor`, `bet`) и
Карта-гипотез-семья (`goal`, `metric`, `subject`, `hypothesis`, `task`).
Каждая запись 7 kind несёт массив `problem` (M:N к строкам `frame`).
`hypothesis` — исключение: вместо `description` четыре части
`if`/`then`/`because`/`so`; «тогда» бьёт в метрику цели. Связи
семантические; методологические инварианты (задача-сирота, «тогда» без
метрики, метрика без влияния, ставка-висяк, фактор без ставки, guardrail,
проблема без цели) ловит рой `/business-problem-audit` — **в пределах
каждой проблемы**, не grep.

Project-слой (по проекту): у каждого проекта в `docs/projects/<slug>/` —
1 singleton `vision.md` + 7 табличных kind (`user`, `capability`,
`boundary`, `surface`, `integration`, `constraint`, `market`). Один
проект (папка) = один продукт = один `vision.md`; разные продукты —
разные папки. `vision` несёт `addresses-problem` (массив, M:N к строкам
`frame`). Канон формы — `docs/projects/_canon/project/`. Связи внутри
слоя семантические, валидируется `/project-audit <slug>`. Vision —
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

- **Бизнес-проблемная** (business / business-problem): профиль и текущие
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
`.claude/rules/<topic>.md`, `state/` каждого скила (коммитятся —
это shared проектная память).

## 5. Авторизация правок

Правки артефактов делаются свободно. Уточнять — ТОЛЬКО если правка
способна:

- сломать накопленную продуктовую модель (vision/user/capability —
  основу остальных слоёв);
- сломать накопленную craft-экспертизу библиотеки;
- несовместимо раскатиться вширь (контракт артефактов всех слоёв,
  форма публичного API библиотеки, таксономия токенов).

Гейты прогонять всегда (`/project-audit <slug>`, `/interface-audit
<slug>`, `/screen-audit <slug>`, и/или `/cross-audit` перед коммитом,
если трогали несколько слоёв). **Коммит / push — гейт человека.** Без
явной просьбы агент не коммитит.

## 6. Зоны правок

- **Артефакты бизнеса** (`docs/business/`) — через скилл
  `business-deep-dive` (аналитик) или `business-deep-dive-for-business`
  (клиент-режим); форма — по `docs/business/README.md`. Нестрогий слой:
  приём материалов клиента + рой web-research конкурентов. Сквозная
  проверка — `cross-audit`.
- **Артефакты AJTBD** (`docs/ajtbd/`) — сегменты через скилл
  `segment-deep-dive` (аналитик) или `segment-deep-dive-for-business`
  (клиент-режим); граф работ, решения и трения через `job-graph-deep-dive`
  (аналитик) или `job-graph-deep-dive-for-business` (клиент-режим), оба с
  эскалацией и push в единую ветку `client`. Форма — по
  `docs/ajtbd/README.md`. Строгая разведочная методология Advanced JTBD;
  наполняется многоволновым роем web-research и опц. JTBD-интервью
  (`jtbd-interview` — отдельный тяжёлый процесс по явному запросу, своё
  state/transcripts, выход разбирается через intake). Семантический аудит
  инвариантов роем (по каждому сегменту) — `ajtbd-audit`. Трение сегмента
  (`segment-problem`) питает проблему бизнеса (`frame`), не подменяет её.
- **Артефакты бизнес-проблемы** (`docs/business-problem/`) — через скилл
  `business-problem-deep-dive` (аналитик) или
  `business-problem-deep-dive-for-business` (клиент-режим с эскалацией и
  push в единую ветку `client`); форма — по `docs/business-problem/README.md`.
  Строгая многопроблемная методология LinkedSWOT + Карта гипотез
  (`frame` — таблица проблем, `problem` — массив M:N). Семантический
  аудит инвариантов методологии роем (по каждой проблеме) —
  `business-problem-audit`. Метрика — best-effort таргет, не гарантия.
- **Артефакты продукта** (`docs/projects/<slug>/`) — через скилл
  `project-deep-dive <slug>` (аналитик) или
  `project-deep-dive-for-business` (клиент-режим с эскалацией и push в
  единую ветку `client`); форма — по
  `docs/projects/_canon/project/README.md`. `vision.addresses-problem`
  связывает продукт с проблемами (M:N). Узкий аудит — `project-audit
  <slug>`. Сквозная семантическая проверка с
  business-problem/interface/domain/screen — `cross-audit` (рой агентов,
  по каждому проекту).
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
  `docs/ajtbd/`, `docs/business-problem/`). На каноническом шаблоне не
  запускается (guard по origin).
- **Sweep'ы** (терминология, чистка): 1 агент = 1 непересекающаяся зона.

## 7. Клиент-режим (`*-for-business`)

Когда сессию ведёт **клиент / основатель / PO**, не аналитик —
включается `*-for-business`-вариант скила слоя:
`/business-deep-dive-for-business` (профиль бизнеса),
`/segment-deep-dive-for-business` (свои клиенты-сегменты),
`/job-graph-deep-dive-for-business` (работы/решения/трения клиентов),
`/business-problem-deep-dive-for-business` (проблемы, SWOT + гипотезы),
`/project-deep-dive-for-business` (продукт). Все следуют одним правилам
клиент-режима. Особенности, которые влияют на работу:

- **Бизнес-язык**: никакого `slug`, `kind`, `draft`, `stable`,
  `artifact` в чате. Видно только «закрыто / в работе». Продукт
  выбирается дружелюбным пикером «какой продукт обсуждаем», без папок и
  slug.
- **Anti-patterns из реальных провалов**, не из методичек (см.
  `<скил>-for-business/references/anti-patterns-real.md`).
- **Метрика — не гарантия** (business-problem): клиент-скилл никогда не
  помогает записать метрику как обещание-гарантию, только как цель;
  строгую измеримость (атрибуция, критерий приёмки) мягко откладывает
  аналитику.
- **Эскалация**: state-маркер `**жду аналитика**` + push в единую ветку
  `client` через `--share` с явного согласия клиента. Доступ к репозиторию
  (логин/пароль) скилл запрашивает один раз на устройстве и сохраняет —
  дальше push идёт молча. Уезжают: артефакты слоя (`docs/business/`,
  `docs/ajtbd/`, `docs/business-problem/` или выбранного продукта
  `docs/projects/<slug>/`),
  state клиента, `client-handoff/summary.md` (живой срез, держится
  актуальным и чистится от мусора), `client-handoff/transcripts/<YYYY-MM-DD>--<HH-MM>--<тема>.md`
  (человекочитаемое имя; полный лог сессии с предложенными вариантами).
- **Единый контекст (read-only)**: чтобы картина была общей и понятной,
  любой скилл (клиентский и аналитический) read-only подтягивает соседние
  `state/` — клиентские и аналитические слои; проектный слой — только по
  текущему продукту (изоляция продуктов сохраняется). В чужой state
  **никто не пишет**. **Anti-leak (клиент-режим)**: прочитанное из кухни
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
