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
БИЗНЕС заказчика     →  AJTBD (спрос по работам)  →  ПРОБЛЕМЫ (многопроблемный)   →  ПРОДУКТЫ (несколько под бизнес)
docs/business/          docs/ajtbd/                   docs/business-problem/           docs/projects/<slug>/
profile · offering ·    segment · job · job-graph ·   frame (таблица проблем) ·        vision + user / capability /
channel · competitor    solution · segment-problem    SWOT (factor · bet) ·            boundary / surface / ...
· metric                                              Карта гипотез (goal · metric ·     │
                                                       subject · hypothesis · task)      ├─ interface/  (UX: who/situation/zone)
                                                                                         ├─ domains/    (опц. DDD-контексты)
                                                                                         └─ screens/    (flow/screen/block/shell)
                                                                                                │
                                                                                                ▼  ручная работа автора макета
                                                                                           wireframe → hi-fi на @sftbmb/ui
```

Артефакты — **чистая аналитика**, на код напрямую не мапятся. Сегменты по работам
живут в `docs/ajtbd/` (Advanced JTBD): трение сегмента (`segment-problem`)
доказывает проблему бизнеса (`frame`), а граф работ и механики ценности подсказывают
возможности продукта. Связь «проблема ↔ продукт» — M:N (`vision.addresses-problem`).
Превращение `screens/` в макет — ручная работа автора, не отдельный артефакт.

> **Юридическая рамка:** гарантируем доставку проекта по scope; метрики слоя
> `business-problem` — совместный с бизнесом **best-effort таргет**, не гарантия
> исхода.

## Методология в двух словах

- **business** (нестрогий) — кто этот бизнес: профиль, оффер, каналы, конкуренты,
  текущие KPI. Источник — материалы клиента + рой web-research.
- **ajtbd** (строгий, Advanced JTBD) — кто наш сегмент **по работам**, а не по
  демографии: сегмент (бандл Core Jobs + 1 Big Job + Score), граф работ (CPR + 11
  механик ценности), нанятые решения и трения. Многоволновой рой web-research +
  опц. JTBD-интервью. Трение клиента (`segment-problem`) ≠ проблема бизнеса
  (`frame`); первое доказывает второе.
- **business-problem** (строгий, LinkedSWOT + Карта гипотез) — `frame` как таблица
  проблем; по каждой проблеме: SWOT-факторы → ставки → цель → измеримая метрика →
  субъект → гипотеза → задача проверки. Ядро — метрика как best-effort таргет.
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
[`docs/getting-started.md`](docs/getting-started.md). Онбординг ведёт аналитик
руками через рой deep-dive-скиллов (оркестратора нет by design). Когда аналитика
заполнена — `/de-template` вычищает показной `docs/projects/example/` и
шаблон-нарратив под идентичность проекта.

## Воркфлоу

Начинаем с бизнеса заказчика — без него проблемы и продукты висят в воздухе.
Слои `project / interface / domain / screen` — по проекту (скилл принимает
`<project-slug>`; без него — пикер). Сквозной аудит — в конце.

```
1.  /business-deep-dive[-for-business]          профиль бизнеса + рой web-research
2.  /segment-deep-dive[-for-business]           AJTBD: сегменты по работам + Score (рой)
3.  /job-graph-deep-dive <segment>[-for-business] граф работ: решения, трения, CPR, механики
       /jtbd-interview                          (опц.) живые JTBD-интервью → intake
4.  /ajtbd-audit                                инварианты графа работ по сегменту (рой)
5.  /business-problem-deep-dive[-for-business]  SWOT + Карта гипотез по каждой проблеме
6.  /business-problem-audit                     инварианты методологии (рой)
7.  /project-deep-dive <slug>[-for-business]    продукт: vision / user / capability
8.  /project-audit <slug>                       аудит внутри продукта
9.  /interface-deep-dive <slug>                 UX: who / situation / zone
10. /interface-audit <slug>
11. /domain-deep-dive <slug> <ctx>              (опц.) бизнес-домены бэкенда
12. /screen-deep-dive <slug>                    flows / screens / blocks / shells
13. /screen-audit <slug>
14. /cross-audit                                сквозная семантика всех слоёв (рой)
```

Суффикс `-for-business` — клиент-режим: бизнес-язык без жаргона, эскалация «нужен
аналитик», push в ветку `client`.

## Инварианты

- **Forward-only** — только «что есть и куда идём», без журналов прошлого.
- **Артефакты — source of truth**, всё остальное собирается по ним.
- **Канон формы продуктовых слоёв** — один раз в `docs/projects/_canon/`; данные —
  в папках проектов.
- **Связи семантические**, не slug-валидируемые; рассинхрон ловит `/cross-audit`.
- **AJTBD питает соседей**: трение сегмента доказывает проблему бизнеса, механики
  графа работ — кандидаты в возможности продукта.
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
