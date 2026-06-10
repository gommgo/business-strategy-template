<div align="center">

# business-strategy-template

### Понятый бизнес, рынок и стейкхолдеры → стратегия. Продукт — один из возможных исходов

Design-time источник истины **стратегии бизнеса**. Аналитик (или сам заказчик в
клиент-режиме) разбирает бизнес, его проблемы, рынок, спрос по работам и
стейкхолдеров — и строит стратегию: от факторов **SWOT** через **Карту гипотез**
до **задач проверки**. Исход не обязан быть IT-продуктом — проблему бизнеса может
закрыть и отдельная **задача** (`task`). Когда стратегия требует продукта,
открывается опциональная ветка проектирования (`docs/projects/<slug>/`), чьи
stable-артефакты потом **читают** код-репо.

[![License](https://img.shields.io/badge/license-Apache--2.0-2563eb)](LICENSE)
[![Часть stit](https://img.shields.io/badge/stit-открытые_шаблоны-6366f1)](https://git.stit.tech/stit-core/stit-public)
[![Method](https://img.shields.io/badge/method-LinkedSWOT_%2B_Карта_гипотез-0ea5e9)](#методология-в-двух-словах)
[![Process](https://img.shields.io/badge/process-AI--driven_скиллы-8b5cf6)](#воркфлоу)
[![SoT](https://img.shields.io/badge/role-design--time_SoT-22c55e)](#место-в-экосистеме)

</div>

---

## Что это

Шаблон импортируется **под бизнес** и форкается **первым**. Стратегия — всегда;
продукт — опциональный downstream, который заводится, только когда исход требует
его:

```
СТРАТЕГИЯ (всегда) — сверху вниз:

БИЗНЕС (+ реестр проблем + стейкхолдеры) →  AJTBD (спрос по работам) →  SWOT (ставки) →  КАРТА ГИПОТЕЗ
docs/business/                              docs/ajtbd/                 docs/swot/       docs/hypothesis-map/
profile · offering · channel ·              segment · job · job-graph · factor · bet     goal · metric · subject ·
competitor · current-metric ·               solution · segment-problem                  hypothesis · task
material · business-problem (реестр) ·
stakeholder · stakeholder-map

ИСХОД проблемы (по результату стратегии):
  • task — закрывает проблему без продукта (процесс, партнёрство, цена, операционное действие)
  • ПРОДУКТ (опционально, под ставку/гипотезу) — docs/projects/<slug>/
        vision + user / capability / boundary / surface / integration / constraint / market
        ├─ interface/          (UX: who / situation / zone)
        ├─ domains/            (опц. DDD-контексты)
        ├─ screens/            (flow / screen / block / shell)  →  wireframe → hi-fi на @stit/ui
        └─ telegram-bot-flow/  (фичи: dialog / window / use-case + сквозные command / notification — bot-поверхности)  →  код-репо читают
```

Артефакты — **чистая аналитика**, на код напрямую не мапятся. Сегменты по работам
живут в `docs/ajtbd/` (Advanced JTBD): трение сегмента (`segment-problem`)
доказывает проблему бизнеса (`business-problem`), а граф работ и механики ценности
питают и стратегию, и — если дело дошло до продукта — его возможности. Исход
проблемы может остаться **задачей** (`task` в Карте гипотез); продуктовый слой
заводится, только когда ставка/гипотеза требуют его. Связь «проблема ↔ продукт» —
M:N (`vision.addresses-problem`). Превращение `screens/` в макет — ручная работа
автора, не отдельный артефакт.

> **Юридическая рамка:** гарантируем доставку по scope (продукт или задача); метрики
> (Карта гипотез) — совместный с бизнесом **best-effort таргет**, не гарантия исхода.

## Методология в двух словах

- **business** (нестрогая картина + строгие реестры) — кто этот бизнес: профиль,
  оффер, каналы, конкуренты, текущие KPI, **реестр проблем бизнеса**
  (`business-problem` — граница гарантии scope и best-effort таргета) **и реестр
  стейкхолдеров** (`stakeholder` · `stakeholder-map` — конкретные люди-решатели,
  их роли/власть/стойка/драйверы и карты связей и вовлечения; единственное место
  с конкретными лицами, вне handoff; сверка стойки со swot/hypothesis-map —
  `/cross-audit` углы `stakeholder-*`). Источник — материалы клиента + рой
  web-research.
- **ajtbd** (строгий, Advanced JTBD) — кто наш сегмент **по работам**, а не по
  демографии: сегмент (бандл Core Jobs + 1 Big Job + Score), граф работ (CPR + 11
  механик ценности), нанятые решения и трения. Многоволновой рой web-research +
  опц. JTBD-интервью. Трение клиента (`segment-problem`) ≠ проблема бизнеса
  (`business-problem`); первое доказывает второе.
- **swot** (строгий, LinkedSWOT) — из сильных/слабых сторон и трендов/угроз бизнеса
  рождаются стратегические ставки (`factor` → `bet`), доводимые до цели/гипотезы.
- **hypothesis-map** (строгий, Карта гипотез) — по каждой проблеме: цель →
  измеримая метрика → субъект → гипотеза → задача проверки. Ядро — метрика как
  best-effort таргет, не гарантия. Терминал стратегии — **задача** (`task`):
  она может закрыть проблему сама либо развернуться в продукт.
- **projects/`<slug>`** (опционально) — когда исход стратегии — продукт под
  проблему(ы): vision + user / capability / boundary / surface / integration /
  constraint / market, плюс вложенные `interface/`, `domains/`, `screens/`
  (web-поверхности) или `telegram-bot-flow/` (bot-поверхности). Если
  проблему закрывает задача (`task`), продуктовый слой не заводится.

Каждый слой ведёт свой deep-dive-скилл через `AskUserQuestion`, пишет state в
свою ветку единого дерева оркестратора (`.claude/skills/entrypoint/state/`;
клиент-режим — `.claude/skills/entrypoint-for-business/state/`), не выдумывает
домен и не повышает `draft → stable` без подтверждения. Сквозную
консистентность ловит рой `/cross-audit`.

## Место в экосистеме

Это **design-time source of truth** стратегии (и проектирования продукта, когда он
нужен). Форкается первым (`Use this template` → `<org>/strategy`), наполняется
аналитикой — и, **когда стратегия рождает продукт**, его stable-артефакты
**читают** код-репо (read-only, односторонне):

| Соседний репо | Читает из этого репо |
|---|---|
| [`<org>/backend`](https://git.stit.tech/stit-core/go-backend-template) | `projects/<slug>/domains/<ctx>/` (scaffold доменов в Go) |
| [`<org>/frontend`](https://git.stit.tech/stit-core/spa-frontend-template) | `projects/<slug>/{interface,screens}/` (fsd-deep-dive) |
| [`<org>/<bot>`](https://git.stit.tech/stit-core/telegram-bot-template) | `projects/<slug>/telegram-bot-flow/<surface>/` (диалоги бота → код) |
| [`<org>/infra`](https://git.stit.tech/stit-core/project-infra-template-compose) | `projects/<slug>/{vision,surface}` (init-project) |

Облик собирается на дизайн-системе
[`@stit/ui`](https://git.stit.tech/stit-core/ui-lib) (потребляется, не правится).
Канон контрактов экосистемы —
[`corp-infra-template/docs/ecosystem.md`](https://git.stit.tech/stit-core/corp-infra-template/src/branch/main/docs/ecosystem.md).

## Путь форка

`Use this template` → `<org>/strategy` → откройте `claude` →
[`docs/getting-started.md`](docs/getting-started.md). Рекомендуемый вход — два
оркестратора `/entrypoint` (аналитик) и `/entrypoint-for-business` (клиент); под
ними рой deep-dive/audit-исполнителей, прямой вызов которых тоже допустим.

## Воркфлоу

Информация приходит **не линейно** — созвон на 3 часа, разрозненные заметки,
сигнал из жизни. Поэтому рекомендуемый вход — **оркестратор**, который сам
разложит сырьё по слоям и маршрутизирует к исполнителю:

- **`/entrypoint`** (аналитик) — принимает сырьё любого объёма, классифицирует
  по слоям/kind, предлагает маршрут и делегирует исполнителю. Пять режимов:
  наполнить · актуализировать · рефакторить · чистить · аудитить. Даёт срез
  «где мы во всём воркфлоу».
- **`/entrypoint-for-business`** (клиент) — то же в бизнес-языке, без жаргона;
  SWOT и Карту гипотез ведёт сам, эскалация «нужен аналитик», push в ветку
  `client`.

Семантический поток слоёв (зависимости сверху вниз) — опора маршрутизации:

```
business (профиль + реестр проблем + стейкхолдеры) → ajtbd (спрос по работам) → swot (ставки)
  → hypothesis-map (цель · метрика · task) → [опц.] projects/<slug> (продукт → interface / domains / screens / telegram-bot-flow)
```

Под оркестратором — рой исполнителей, прямой вызов которых тоже допустим:

| слой | исполнители | аудит |
|---|---|---|
| `business` (+ реестр `business-problem` + стейкхолдеры `stakeholder` · `stakeholder-map`) | `/business-deep-dive` | `/cross-audit` (своего узкого нет) |
| `ajtbd` | `/segment-deep-dive` · `/job-graph-deep-dive` · `/jtbd-interview` | `/ajtbd-audit` |
| `swot` | `/swot-deep-dive` | `/swot-audit` |
| `hypothesis-map` | `/hypothesis-map-deep-dive` | `/hypothesis-map-audit` |
| `projects/<slug>` (опц.) | `/project-deep-dive` · `/interface-deep-dive` · `/domain-deep-dive` · `/screen-deep-dive` · `/telegram-bot-flow-deep-dive` | `/project-audit` · `/interface-audit` · `/screen-audit` · `/telegram-bot-flow-audit` |

Сквозную семантику всех слоёв ловит рой `/cross-audit`. Когда дозревший продукт
(`vision.lifecycle → stable`) меняет реальность бизнеса, оркестратор ведёт
восходящую сверку `project → business` (новые оферы/метрики/проблемы с провенансом
`from-project`).

Клиент ведёт сессию сам через единый вход `/entrypoint-for-business` —
бизнес-язык без жаргона, эскалация «нужен аналитик», push в ветку `client`.

## Инварианты

- **Forward-only** — только «что есть и куда идём», без журналов прошлого.
- **Артефакты — source of truth**, всё остальное собирается по ним.
- **Канон формы продуктовых слоёв** — один раз в `docs/projects/_template/`; данные —
  в папках проектов.
- **Связи семантические**, не slug-валидируемые; рассинхрон ловит `/cross-audit`.
- **Сквозные рёбра — снизу-вверх**: проектная/UX-сущность ссылается на глобальную
  (`situation.jobs`, `capability.jobs`, `user.segments`, `subject.segments`),
  обратную сторону сводит `/cross-audit`.
- **AJTBD питает соседей**: трение сегмента доказывает проблему бизнеса, механики
  графа работ — кандидаты в возможности продукта.
- **Продукт — опциональный исход**: проблему может закрыть задача (`task`); слой
  `docs/projects/` заводится, только когда стратегия требует продукта.
- **Восходящий поток `project → business`**: дозревший продукт
  (`vision.lifecycle → stable`) питает business (оферы / метрики / реестр проблем)
  через провенанс `from-project`.
- **Метрика — best-effort таргет, не гарантия.**
- **Экспертиза священна** — домен/продукт/craft из ответов бизнеса и библиотеки,
  не из головы агента.
- **Коммит / push — гейт человека.**

Структура каталогов и каноны слоёв — [`docs/README.md`](docs/README.md) и
README каждого слоя; гайд для агента — [`CLAUDE.md`](CLAUDE.md).

## Часть экосистемы stit

Это один из открытых шаблонов stit (Apache-2.0) — фундамент «-1 уровня»,
берите бесплатно и владейте. Карта всех шаблонов и точка входа —
**[витрина stit](https://git.stit.tech/stit-core/stit-public)**. Нужна
команда аналитиков, методология или поддержка —
**[наш подход и контакты (vision)](https://git.stit.tech/stit/vision)**.

## Лицензия

**Apache-2.0** — см. [`LICENSE`](LICENSE).
