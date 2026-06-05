# Чек-листы полей по kind

Что заполнять при заведении/углублении каждого kind, что обязательно для
stable, и разумный порядок копания. Скилл владеет 4 kind: `job`,
`job-graph`, `solution`, `segment-problem`. Сегмент (`segment.md`) —
у `/segment-deep-dive`; здесь он только **выбирается** и наследуется
записями.

Универсально обязательное: `slug`, `name`, `status`, привязка к **сегменту**
(`segment` / `by-segment`), `description` (кроме `job-graph`, где
описание — короткое имя графа). Поля и формы — дословно из
`docs/ajtbd/<kind>.md`.

## job

Колонки: `slug` · `name` · `when` · `want` · `success-criteria` ·
`so-that` · `level` · `type` · `segment` · `parent-job` · `prev-jobs` ·
`frequency` · `importance` · `status`.

**Для stable:** шаблон **целиком** (`when` = контекст+триггер+опыт+
особенности; `want` = понятный результат; `success-criteria` = критерий
«достаточно»; `so-that` = работа выше + эмоция), `level` (enum), `type`
(enum), `segment`, и **непрерывность «чтобы»** (если есть `parent-job`:
`so-that` = `want` родителя). Доказана прошлым **поведением**.

**Порядок:** segment → when → want + success-criteria → so-that →
level → type → parent-job (проверить непрерывность) → prev-jobs →
frequency/importance.

**Главная проверка:** ведёт ли `want` через `so-that` вверх (до Big Job),
доказана ли действиями. Уровень осознан (не шаг как core, не «быть
счастливым» как big). Тип размечен. Ложная работа проверена вопросом.

## solution

Колонки: `slug` · `name` · `description` · `hired-for` · `by-segment` ·
`kind` · `satisfaction` · `price` · `price-value-fit` · `maps-to` ·
`status`.

**Для stable:** `hired-for` (≥1 работа — без неё не решение), `by-segment`,
`kind` (enum product/service/diy/substitute/inaction), `satisfaction`
(X/10), `price-value-fit` (X/10) **из research/интервью**, `price` если
известна, `maps-to` (конкурент/офер или `—`).

**Порядок:** by-segment → hired-for → kind → satisfaction → price →
price-value-fit → maps-to.

**Главная проверка:** нанято на конкретную работу; оценки наблюдаемы (не
на глаз); взяты **все** решения, включая DIY/субститут/бездействие, не
только прямые конкуренты; это решение **сейчас**, не наш будущий продукт.

## segment-problem

Колонки: `slug` · `name` · `description` · `solution` · `job` · `segment`
· `strength` · `drivers` · `barriers` · `feeds-problem` · `status`.

**Для stable:** **`solution` + `job` оба** (трение — следствие пары,
без них нарушение ядра), `segment`, `strength` (1–10 с обоснованием из
research/интервью), `drivers` (что держит на текущем), `barriers` (что
мешает уйти — пожиратели ценности). `feeds-problem` опционально (на какую
`business-problem/frame`).

**Порядок:** segment → solution + job (пара!) → strength → drivers →
barriers → feeds-problem.

**Главная проверка:** привязана к реальной паре решение+работа; сила
обоснована действиями; не «pain»/«боль», а недостижимый результат +
негативная эмоция; не наша будущая фича.

## job-graph

Колонки: `slug` · `name` · `segment` · `target-job` · `cpr` ·
`job-types` · `value-mechanics` · `status`.

**Для stable:** `segment`, `target-job` (Core-работа, вокруг которой
собран граф), `cpr` (упорядоченный must-do путь к Big Job, **без
разрывов**), `job-types` (разметка типов работ графа), `value-mechanics`
(кандидаты из 11 механик → `capability`, не реализация).

**Порядок:** segment → target-job → cpr (порядок значим) → job-types →
value-mechanics.

**Главная проверка:** виден критический путь к Big Job, где он рвётся
(= место ценности), какие механики это открывает; не дубликат `job.md`,
не список фич, не граф без CPR/типов, не оторван от сегмента.

## Универсальные нюансы

- `slug` — kebab-case, английский, короткий, уникальный в файле, не
  меняется после заведения.
- `name` — человекочитаемое, русский по умолчанию.
- `description` — одно предложение, в языке сегмента, без маркетинга.
- одиночный slug-реф — в бэктиках (`` `dacha-owner` ``); массив — питон-
  стиль с бэктиками (`` [`buy-gear`, `plan-trip`] ``); `cpr` — питон-стиль,
  **порядок значим**.
- оценки 1–10 — целое; пустое опциональное — `—`; enum — в бэктиках.
- `segment` (и `by-segment`) — непустой у **всех** записей этого слоя:
  граф собирается внутри сегмента.
- `status` — дефолт `draft`; повышение только через чек-лист; понижение
  руками аналитика.
