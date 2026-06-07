# Чек-лист `draft → stable`

После каждой правки — 5 пунктов. Все ✅ → предложить повышение через
`AskUserQuestion`. **Скилл не повышает сам.**

1. **Обязательные слоты заполнены** (см. `field-checklists.md`).
   Опциональные — `—`. `profile` — все четыре раздела.
2. **`Критерии <kind>` подтверждены** аналитиком через `AskUserQuestion`.
3. **`Что <kind> НЕ` не нарушены** — anti-patterns проверены, ❌.
4. **`Тест-критерий` ✅.**
5. **Факт прослежен до `material`** — для записей profile/offering/
   channel/current-metric/stakeholder есть источник (material-ссылка в
   state, транскрипт или подтверждённый research). Нет `**blocker**` в state.

Все 5 ✅ → `AskUserQuestion`: «Повышаем `<kind>:<slug>` в stable?» По
«да» — `status: draft → stable`.

## Особое для этого слоя

- `current-metric` не stable без `as-of` и `source` (baseline без даты и
  источника бесполезен).
- `competitor` не stable без `url` и `sources`.
- `business-problem` не stable без явной **границы** `guarantee` (доставка
  по scope) vs `target` (метрики best-effort), без `out-of-control` и без
  `served`. Не становится stable, если метрика где-то подана как гарантия
  (нарушение юр-рамки) или `target` смешан с `guarantee`.
- `stakeholder` не stable без `deal-role`, `power`/`interest`, `attitude`
  и `motivation`/`win`; имена и психографика — только от клиента/интервью,
  не выдуманы (минимизация: берётся ровно нужное, без биографии).
  `stakeholder-map` не stable без ЛПР и держателя бюджета среди `members`,
  без графа связей (`influence-edges`) и пути вовлечения (`engagement-path`
  без разрыва к ЛПР; властный блокер с митигацией в `risks`).
- Запись на основе **неподтверждённого** web-research остаётся `draft`,
  пока аналитик не подтвердил факт.

## Понижение

Скилл сам не понижает — подсвечивает и предлагает через `AskUserQuestion`.

## Когда нельзя пройти — нормально

Нужен ещё материал от клиента / ещё research → закрыть `draft`, оставить
`**blocker**`, предложить следующий шаг.
