# Чек-лист `draft → stable`

После каждой правки — 5 пунктов. Все ✅ → предложить повышение через
`AskUserQuestion`. **Скилл не повышает сам.**

1. **Обязательные слоты заполнены** (см. `field-checklists.md`).
   Опциональные — `—`. `profile` — все четыре раздела.
2. **`Критерии <kind>` подтверждены** аналитиком через `AskUserQuestion`.
3. **`Что <kind> НЕ` не нарушены** — anti-patterns проверены, ❌.
4. **`Тест-критерий` ✅.**
5. **Факт прослежен до `material`** — для записей profile/segment/
   offering/channel/current-metric есть источник (material-ссылка в
   state или подтверждённый research). Нет `**blocker**` в state.

Все 5 ✅ → `AskUserQuestion`: «Повышаем `<kind>:<slug>` в stable?» По
«да» — `status: draft → stable`.

## Особое для этого слоя

- `current-metric` не stable без `as-of` и `source` (baseline без даты и
  источника бесполезен).
- `competitor` не stable без `url` и `sources`.
- Запись на основе **неподтверждённого** web-research остаётся `draft`,
  пока аналитик не подтвердил факт.

## Понижение

Скилл сам не понижает — подсвечивает и предлагает через `AskUserQuestion`.

## Когда нельзя пройти — нормально

Нужен ещё материал от клиента / ещё research → закрыть `draft`, оставить
`**blocker**`, предложить следующий шаг.
