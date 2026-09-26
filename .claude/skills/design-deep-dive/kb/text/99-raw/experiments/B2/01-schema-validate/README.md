# B2/01 — проверка схемы facts.yaml (и voc.schema.yaml, когда появится)

- **Цель:** схема `02-strategy-messaging/facts.schema.yaml` — валидная JSON Schema draft 2020-12; оба примера
  `examples/facts-*.yaml` проходят; типовые ошибки инвентаря ловятся валидатором.
- **Команда:** `99-raw/tools/venv-B2/bin/python ../../scripts/text/validate_facts.py`
- **Версии:** Python 3.13.5, PyYAML 6.0.3, jsonschema 4.26.0 (venv-B2, uv 0.11.19), 2026-09-24.
- **Что проверяется:** метасхема; поле `date`; `x-claim-classes` = enum классов (20); `x-kinds` = enum видов (22);
  классы запретов по умолчанию ⊆ enum; примеры валидны, id уникальны, ссылки `entities` и `related` существуют;
  14 отрицательных мутаций (факт без source, id не kebab-case, `source.type: model`, пустой verbatim, неизвестный класс,
  дата не ISO, placeholder без скобок, superlative без basis, health без legal.review, promo-deadline без valid.until,
  testimonial без attribution, rating без scale/count, лишнее поле, facts_version 2) — каждая даёт ошибку.
- **Результат (2026-09-24 07:28):** всё PASS, `validate: OK`. Дополнительно `claims_check.py lint-facts` на примерах:
  `facts-kvarts.yaml` — 0 находок; `facts-service-renovation.yaml` — 1 error (намеренно: отзыв с `permission: pending`).
  Утилита нашла две ошибки в моих собственных примерах, которые схема пропускает (исправлены): verbatim «Отгрузка первой
  партии» при выдержке «Отгрузка — декабрь 2026» и «54 м²» в кейсе без этого числа в выдержке договора.
- **Вывод:** схема держит структуру, но не смысл: соответствие факта своему основанию (`source.quote`) проверяет только
  `claims_check.py lint-facts` (COPY-F-INFERRED) — запускать оба.
