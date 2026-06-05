<div align="center">

# project-docs-template

### Сначала понятый бизнес и спроектированный продукт — потом код

Design-time источник истины проекта. Аналитик (или сам заказчик в клиент-режиме)
ведёт цепочку **бизнес → проблемы → продукт → интерфейс → экраны** через рой
AI deep-dive-скиллов. Код-репо потом **читают** эти артефакты — код собирается по
спроектированному, а не наоборот.

[![License](https://img.shields.io/badge/license-Apache--2.0-2563eb)](LICENSE)
[![Часть sftbmb](https://img.shields.io/badge/sftbmb-открытые_шаблоны-6366f1)](https://git.sftbmb.ru/sftbmb-core/sftbmb-public)
[![Method](https://img.shields.io/badge/method-LinkedSWOT_%2B_Карта_гипотез-0ea5e9)](#методология-в-двух-словах)
[![Process](https://img.shields.io/badge/process-AI--driven_скиллы-8b5cf6)](#воркфлоу)
[![SoT](https://img.shields.io/badge/role-design--time_SoT-22c55e)](#место-в-экосистеме)

</div>

---

## Что это

Шаблон импортируется **под бизнес** и форкается **первым**. Поток сверху вниз:

```
БИЗНЕС (+ реестр проблем) →  AJTBD (спрос по работам) →  SWOT (ставки) →  КАРТА ГИПОТЕЗ        →  ПРОДУКТЫ (несколько под бизнес)
docs/business/               docs/ajtbd/                 docs/swot/       docs/hypothesis-map/    docs/projects/<slug>/
profile · offering ·         segment · job ·             factor · bet     goal · metric ·         vision + user / capability /
channel · competitor ·       job-graph · solution ·                       subject ·               boundary / surface / ...
current-metric · material ·  segment-problem                              hypothesis · task          │
business-problem (реестр)                                                                            ├─ interface/  (UX: who/situation/zone)
                                                                                                     ├─ domains/    (опц. DDD-контексты)
                                                                                                     └─ screens/    (flow/screen/block/shell)
                                                                                                            │
                                                                                                            ▼  ручная работа автора макета
                                                                                                       wireframe → hi-fi на @sftbmb/ui
```

Артефакты — **чистая аналитика**, на код напрямую не мапятся. Сегменты по работам
живут в `docs/ajtbd/` (Advanced JTBD): трение сегмента (`segment-problem`)
доказывает проблему бизнеса (`business-problem`), а граф работ и механики ценности
подсказывают возможности продукта. Связь «проблема ↔ продукт» — M:N
(`vision.addresses-problem`). Превращение `screens/` в макет — ручная работа
автора, не отдельный артефакт.

> **Юридическая рамка:** гарантируем доставку проекта по scope; метрики (Карта
> гипотез) — совместный с бизнесом **best-effort таргет**, не гарантия исхода.

## Методология в двух словах

- **business** (нестрогий) — кто этот бизнес: профиль, оффер, каналы, конкуренты,
  текущие KPI **и реестр проблем бизнеса** (`business-problem` — граница гарантии
  scope и best-effort таргета). Источник — материалы клиента + рой web-research.
- **ajtbd** (строгий, Advanced JTBD) — кто наш сегмент **по работам**, а не по
  демографии: сегмент (бандл Core Jobs + 1 Big Job + Score), граф работ (CPR + 11
  механик ценности), нанятые решения и трения. Многоволновой рой web-research +
  опц. JTBD-интервью. Трение клиента (`segment-problem`) ≠ проблема бизнеса
  (`business-problem`); первое доказывает второе.
- **swot** (строгий, LinkedSWOT) — из сильных/слабых сторон и трендов/угроз бизнеса
  рождаются стратегические ставки (`factor` → `bet`), доводимые до цели/гипотезы.
- **hypothesis-map** (строгий, Карта гипотез) — по каждой проблеме: цель →
  измеримая метрика → субъект → гипотеза → задача проверки. Ядро — метрика как
  best-effort таргет, не гарантия.
- **projects/`<slug>`** — продукт под проблему(ы): vision + user / capability /
  boundary / surface / integration / constraint / market, плюс вложенные
  `interface/`, `domains/`, `screens/`.

Каждый слой ведёт свой deep-dive-скилл через `AskUserQuestion`, держит state в
`.claude/skills/<имя>/state/`, не выдумывает домен и не повышает `draft → stable`
без подтверждения. Сквозную консистентность ловит рой `/cross-audit`.

## Место в экосистеме

Это **design-time source of truth** проекта. Форкается первым (`Use this template`
→ `<org>/docs`), наполняется аналитикой — и только потом форкаются код-репо,
которые **читают** его stable-артефакты (read-only, односторонне):

| Соседний репо | Читает из этого репо |
|---|---|
| [`<org>/backend`](https://git.sftbmb.ru/sftbmb-core/go-backend-template) | `projects/<slug>/domains/<ctx>/` (scaffold доменов в Go) |
| [`<org>/frontend`](https://git.sftbmb.ru/sftbmb-core/spa-frontend-template) | `projects/<slug>/{interface,screens}/` (fsd-deep-dive) |
| [`<org>/infra`](https://git.sftbmb.ru/sftbmb-core/project-infra-template-compose) | `projects/<slug>/{vision,surface}` (init-project) |

Облик собирается на дизайн-системе
[`@sftbmb/ui`](https://git.sftbmb.ru/sftbmb-core/ui-lib) (потребляется, не правится).
Канон контрактов экосистемы —
[`corp-infra-template/docs/ecosystem.md`](https://git.sftbmb.ru/sftbmb-core/corp-infra-template/src/branch/main/docs/ecosystem.md).

## Путь форка

`Use this template` → `<org>/docs` → откройте `claude` →
[`docs/getting-started.md`](docs/getting-started.md). Рекомендуемый вход — два
оркестратора `/entrypoint` (аналитик) и `/entrypoint-for-business` (клиент); под
ними рой deep-dive/audit-исполнителей, прямой вызов которых тоже допустим. Когда
аналитика заполнена — `/de-template` вычищает показной `docs/projects/example/`
и шаблон-нарратив под идентичность проекта.

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
business (профиль + реестр проблем) → ajtbd (спрос по работам) → swot (ставки)
  → hypothesis-map (цель · метрика) → projects/<slug> (продукт → interface / domains / screens)
```

Под оркестратором — рой исполнителей, прямой вызов которых тоже допустим:

| слой | исполнители | аудит |
|---|---|---|
| `business` (+ реестр `business-problem`) | `/business-deep-dive` | — |
| `ajtbd` | `/segment-deep-dive` · `/job-graph-deep-dive` · `/jtbd-interview` | `/ajtbd-audit` |
| `swot` | `/swot-deep-dive` | `/swot-audit` |
| `hypothesis-map` | `/hypothesis-map-deep-dive` | `/hypothesis-map-audit` |
| `projects/<slug>` | `/project-deep-dive` · `/interface-deep-dive` · `/domain-deep-dive` · `/screen-deep-dive` | `/project-audit` · `/interface-audit` · `/screen-audit` |

Сквозную семантику всех слоёв ловит рой `/cross-audit`. Когда дозревший продукт
(`vision.lifecycle → stable`) меняет реальность бизнеса, оркестратор ведёт
восходящую сверку `project → business` (новые оферы/метрики/проблемы с провенансом
`from-project`).

Суффикс `-for-business` у исполнителей — клиент-режим: бизнес-язык без жаргона,
эскалация «нужен аналитик», push в ветку `client`.

## Инварианты

- **Forward-only** — только «что есть и куда идём», без журналов прошлого.
- **Артефакты — source of truth**, всё остальное собирается по ним.
- **Канон формы продуктовых слоёв** — один раз в `docs/projects/_canon/`; данные —
  в папках проектов.
- **Связи семантические**, не slug-валидируемые; рассинхрон ловит `/cross-audit`.
- **Сквозные рёбра — снизу-вверх**: проектная/UX-сущность ссылается на глобальную
  (`situation.jobs`, `capability.jobs`, `user.segments`, `subject.segments`),
  обратную сторону сводит `/cross-audit`.
- **AJTBD питает соседей**: трение сегмента доказывает проблему бизнеса, механики
  графа работ — кандидаты в возможности продукта.
- **Восходящий поток `project → business`**: дозревший продукт
  (`vision.lifecycle → stable`) питает business (оферы / метрики / реестр проблем)
  через провенанс `from-project`.
- **Метрика — best-effort таргет, не гарантия.**
- **Экспертиза священна** — домен/продукт/craft из ответов бизнеса и библиотеки,
  не из головы агента.
- **Коммит / push — гейт человека.**

Структура каталогов и каноны слоёв — [`docs/README.md`](docs/README.md) и
README каждого слоя; гайд для агента — [`CLAUDE.md`](CLAUDE.md).

## Часть экосистемы sftbmb

Это один из открытых шаблонов sftbmb (Apache-2.0) — фундамент «-1 уровня»,
берите бесплатно и владейте. Карта всех шаблонов и точка входа —
**[витрина sftbmb](https://git.sftbmb.ru/sftbmb-core/sftbmb-public)**. Нужна
команда аналитиков, методология или поддержка —
**[наш подход и контакты (vision)](https://git.sftbmb.ru/sftbmb/vision)**.

## Лицензия

**Apache-2.0** — см. [`LICENSE`](LICENSE).
