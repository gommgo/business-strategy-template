# Чек-листы полей по kind

Универсально обязательное: `slug`, `name`, `status` (+ `description`,
кроме `material`).

## profile (singleton)

**Обязательно:** разделы `Бизнес`, `Модель`, `Позиционирование`,
`Контекст`.
**Порядок:** Бизнес → Модель → Позиционирование → Контекст.
Главная проверка: «как есть» (не про наше решение, не «как должно быть»).

## offering

**Для stable:** `kind` (enum), `for-segment`.
**Порядок:** fundamentals → kind → for-segment → from-project.
Проверка: источник выручки/ценности; `for-segment` указывает на
существующий `ajtbd/segment` (сегменты — в `docs/ajtbd/`,
`/segment-deep-dive`). `from-project` — провенанс восходящего потока: если
офер родился из дозревшего продукта, его slug; иначе `—`.

## channel

**Для stable:** `kind` (enum), `serves-segment`.
**Порядок:** fundamentals → kind → serves-segment.
Проверка: путь между бизнесом и клиентом (≠ наш surface);
`serves-segment` указывает на существующий `ajtbd/segment`.

## competitor

**Для stable:** `url`, `position` (enum), `sources`.
**Поток:** в основном через рой (`research-rays.md`) — кандидаты приходят
с url/sources/position; аналитик подтверждает.
Проверка: позиция на рынке заказчика; источники реальные; давление
наблюдаемо.

## current-metric

**Для stable:** `value`, `as-of` (дата), `source`.
**Порядок:** fundamentals → value → as-of → source → from-project.
Проверка: число + дата + источник; бизнес-метрика; не бинарна; годится
как baseline. `from-project` — провенанс восходящего потока: новый
baseline, привнесённый дозревшим продуктом (slug); иначе `—`.

## material

**Обязательно:** `slug`, `name`, `kind` (enum), `uri`, `status`.
Проверка: по записи можно вернуться к первоисточнику факта.

## business-problem (строгий реестр проблем)

`business-problem.md` — **таблица проблем бизнеса** (одна строка = одна
проблема). Колонки: `slug · name · statement · guarantee · target ·
out-of-control · scope · served · from-project · status`.
**Для stable:** `statement` (бизнес-боль в деньгах/времени/риске, не в
терминах фич), `guarantee` (что гарантируем — доставка по scope), `target`
(на какие метрики целимся, best-effort, **не гарантия**), `out-of-control`
(внешние факторы вне контроля), `scope` (in/out), `served` (enum).
**Порядок:** statement → guarantee/target (**граница** — главная проверка) →
out-of-control → scope → served → from-project.
**Главная проверка:** граница «гарантия (доставка по scope) vs таргет
(метрики best-effort)»; метрика **никогда** не подана как гарантия.
**`served`:** `served` — бизнес уже обслуживает рынок проблемы;
`prospective` — разведка под будущую инициативу (рынок ещё не обслуживается;
допускается без обслуживающих оферов/каналов — не «висяк»).
**`from-project`:** какой дозревший продукт проявил/подтвердил проблему
(slug | `—`) — провенанс восходящего потока.
**Опора на доказательства:** строка — проблема **бизнеса**, не трение
клиента; агрегированные трения клиента из `ajtbd/segment-problem` (read-only)
служат ей доказательством. Перенос смысла трения в формулировку — через
`AskUserQuestion`, не выдумывать.
**Дополнительный инвариант (ловит `/hypothesis-map-audit`):** у каждой
строки `business-problem` есть ≥1 `goal` в `docs/hypothesis-map/` —
иначе проблема повисла.

## stakeholder (строгий kind, конкретные лица)

Колонки: `slug · name · description · unit · deal-role · power · interest ·
attitude · motivation · win · strategic-stance · objections · reports-to ·
manifests-as · status`.
**Для stable:** `unit`, `deal-role` (enum), `power`/`interest` (enum),
`attitude` (enum), `motivation` (личные драйверы/страхи), `win` (личная
победа).
**`strategic-stance` (опц., минимизация):** куда лицо хочет/не хочет
движения **бизнеса** — что поддержит/чему воспротивится на уровне
стратегии. Отлично от `motivation` (психология) и `win` (личный успех).
Ровно необходимое про взгляды (не биография, не вкусы) — чтобы сверить
стратегию с людьми. Заполняется для **властных** лиц (`power: high`);
сверяется с `swot/bet` / `hypothesis-map/goal` (`/cross-audit`
`stakeholder-strategy`).
**Порядок:** идентичность (name/кресло/unit) → роль (deal-role) → позиция
(power/interest/attitude) → драйверы (motivation/win/objections) → связи
(reports-to/manifests-as).
**Главная проверка:** конкретное лицо (не абстрактная роль там, где лицо
известно); `deal-role` (формальная позиция) ≠ `attitude` (стойка) — «ЛПР со
skeptic» валиден; влияние на судьбу проекта наблюдаемо.
**Экспертиза священна:** имена и психографику — только из материалов
клиента / интервью, **не выдумывать**. Anti-patterns как опции — да;
тексты — нет.
**`deal-role`:** `lpr` · `budget-holder` · `lvr` · `recommender` ·
`gatekeeper` · `end-user` · `sponsor`. **`attitude`:** `champion` ·
`supporter` · `neutral` · `skeptic` · `blocker`.
**`manifests-as`:** тот же человек в соседних слоях с префиксом kind
(`subject:`/`user:`/`who:`) — связь авторская (business → соседний слой),
не дублировать портрет.
**Forward-only:** только текущее состояние стойки; «был против — стал за»
— перезапись, не журнал.

## stakeholder-map (строгий kind, сборка)

Колонки: `slug · name · scope · business-problem · members · grid ·
influence-edges · engagement-path · strategy · risks · status`.
**Для stable:** `scope`, `business-problem` (≥1), `members` (≥2), `grid`
(раскладка по 4 квадрантам), `influence-edges` (граф связей),
`engagement-path` (упорядочен, к ЛПР), `strategy`, `risks` (митигация
властных блокеров).
**Порядок:** scope/business-problem → members → grid → influence-edges →
engagement-path → strategy/risks.
**Главная проверка:** среди `members` есть `lpr` И `budget-holder` (некому
санкционировать/финансировать иначе); `influence-edges` ссылается только на
`members`; `engagement-path` без разрыва ведёт к ЛПР; властный
`blocker`/`skeptic` имеет митигацию в `risks`.
**`influence-edges`-тип:** `influences` · `allies` · `conflicts` ·
`sponsors` · `blocks` · `delegates` (направленное `from → to : kind`).
**Не дубль `stakeholder.md`:** здесь синтез по инициативе, не повтор
атрибутов; формальная иерархия — `stakeholder.reports-to`, не `edges`.

## Универсальные нюансы

- `slug` — kebab-case, английский, уникальный в файле, не меняется;
  **скилл выводит его из `name`** (транслит в kebab-case), у аналитика не
  спрашивается (см. `.claude/rules/naming.md`).
- `description` — одно предложение, язык бизнеса, без маркетинга.
- `value` (метрики) — число + единица; обязательно с `as-of` и `source`.
- `status` — дефолт `draft`; повышение через чек-лист; понижение руками.
