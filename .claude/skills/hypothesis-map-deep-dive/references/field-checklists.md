# Чек-листы полей по kind

Что заполнять при заведении/углублении каждого kind, что обязательно для
stable, и разумный порядок копания. Универсально обязательное в табличных
kinds: `slug`, `name`, `status` (+ `description`, кроме `hypothesis`). Для
всех 5 kind обязателен **непустой `business-problem`** — массив slug-рефов на строки
реестра проблем `docs/business/business-problem.md` (M:N): к какой
проблеме(ам) относится запись.

## goal

**Для stable:** `business-problem` (≥1 строка реестра проблем), `from-bet` (или `—`
при перепрыгивании), ≥1 метрика ссылается на эту цель.
**Порядок:** fundamentals → business-problem → from-bet → deadline.
Главная проверка: критерий успеха без цифр (не задача, не число). Цель
раскрывает проблему в проверяемый критерий — у каждой проблемы должна быть
≥1 цель. `from-bet` ссылается на `swot/bet.promoted-to`.

## metric

**Для stable:** `business-problem` (≥1 строка реестра, обычно те же, что у её цели),
`goal`, `current` (baseline+дата+окно, из `business/current-metric.md`),
`target`, `direction`, `kind`, `source`, `attribution`, `acceptance`. См.
`metric-spine.md`.
**Порядок:** business-problem → goal → current → target → direction → kind →
source → attribution → acceptance → evidence.
Главная проверка: не бинарна; baseline есть; источник назван; атрибуция
есть; у каждой целевой — guardrail **в пределах её проблемы**; метрика
**не подана как гарантия**.

## subject

**Для stable:** `business-problem` (≥1 строка реестра), `kind` (positive/negative),
`motivation` (боли/желания), `segments` (≥1 `ajtbd/segment` — обяз. для
`positive`; для `negative` опц., `—`).
**Порядок:** fundamentals → business-problem → kind → segments → motivation → users.
Главная проверка: носитель самодвижения (не исполнитель); мотивация
наблюдаема (питает «потому что» гипотез). Один субъект бизнеса часто
фигурирует в нескольких проблемах.
**Связь с AJTBD-сегментом (`segments` — обяз. для `positive`, опц. для
`negative`):** позитивный субъект семантически вырастает из `ajtbd/segment`
(группа клиентов по работам). Заглянуть в `docs/ajtbd/segment.md`
(read-only), через `AskUserQuestion` связать; мотивация опирается на его
success-criteria и трения (`segment-problem`), не выдумывается. Сегмент ≠
субъект (рынок vs чьё поведение двигаем). Негативный субъект (конкурент,
регулятор) сегмента не требует — `—`.
**Связь с пользователем (`users`, опц.):** на каких `projects/<slug>/user`
ложится субъект влияния (мягкая связь, ловит `/cross-audit`).

## hypothesis

**Обязательно:** `slug`, `name`, `status`, `business-problem` (≥1 строка реестра)
+ четыре части `if`, `then`, `because`, `so` (вместо `description`).
**Для stable:** `subject` (или `—` для бессубъектной), `metric` (на что
бьёт «тогда»), `priority`.
**Порядок:** business-problem → if → then → because → so → subject → metric →
jobs → priority.
Главная проверка: «если» — наш принцип; «то» — поведение субъекта;
«потому что» — на мотивации; «тогда» — на конкретную метрику **той же
проблемы**. `business-problem` обычно совпадает с проблемой метрики из `so`.
**Связь с работой (`jobs`, опц.):** на какую работу сегмента (`ajtbd/job`)
целит гипотеза (мягкая связь, ловит `/cross-audit`).

## task

**Для stable:** `business-problem` (≥1 строка реестра, обычно те же, что у её
гипотезы), `hypothesis` (привязка обязательна — сирота запрещена).
**Порядок:** fundamentals → business-problem → hypothesis.
Главная проверка: проверяет конкретную гипотезу; не инженерный тикет.

## Универсальные нюансы

- `slug` — kebab-case, английский, короткий, уникальный в файле, не
  меняется после заведения; **скилл выводит его из `name`** (транслит в
  kebab-case), у аналитика не спрашивается (см. `.claude/rules/naming.md`).
- `name` — человекочитаемое, русский по умолчанию.
- `description` — одно предложение, в языке бизнеса, без маркетинга.
- `priority` — целое, 1 = высший, без дублей.
- `business-problem` — массив slug-рефов на строки реестра проблем, питон-стиль с
  бэктиками (`` [`paid-outflow`, `slow-onboarding`] ``). Непустой у всех
  5 kind. M:N — одна сущность часто работает на несколько проблем.
- `segments` (у `subject`) / `jobs` (у `hypothesis`) / `users` (у
  `subject`) — питон-стиль массивы slug-рефов на сущности соседних слоёв.
- `status` — дефолт `draft`; повышение только через чек-лист; понижение
  руками аналитика.
