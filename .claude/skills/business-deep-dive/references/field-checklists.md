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
**Порядок:** fundamentals → kind → for-segment.
Проверка: источник выручки/ценности; `for-segment` указывает на
существующий `ajtbd/segment` (сегменты — в `docs/ajtbd/`,
`/segment-deep-dive`).

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
**Порядок:** fundamentals → value → as-of → source.
Проверка: число + дата + источник; бизнес-метрика; не бинарна; годится
как baseline.

## material

**Обязательно:** `slug`, `name`, `kind` (enum), `uri`, `status`.
Проверка: по записи можно вернуться к первоисточнику факта.

## Универсальные нюансы

- `slug` — kebab-case, английский, уникальный в файле, не меняется.
- `description` — одно предложение, язык бизнеса, без маркетинга.
- `value` (метрики) — число + единица; обязательно с `as-of` и `source`.
- `status` — дефолт `draft`; повышение через чек-лист; понижение руками.
