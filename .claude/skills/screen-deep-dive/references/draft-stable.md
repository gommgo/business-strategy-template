# Контракт `draft → stable`

Запись становится `stable`, когда **все 6 пунктов одновременно** ✅.
Скилл проверяет, аналитик подтверждает, скилл применяет.

## Чек-лист

### 1. Обязательные слоты frontmatter заполнены

Опциональные могут быть `—` или отсутствовать. Остальные —
обязательно с непустым значением (для slug-полей — реф; для
свободного текста — фраза).

См. `field-checklists.md` — там по каждому из 4 kind: какие слоты
обязательны и какие опциональны.

### 2. Все ссылки валидны

Каждый `slug` существует:

**Внутри screens** (все пути — в папке текущего проекта
`docs/projects/<project-slug>/screens/`):
- `flow.desktop` / `flow.mobile` / `flow.transitions[].{from,to}` →
  существуют как папки `…/screens/screens/<slug>/`;
- `screen.shell` → `…/screens/shells/<slug>/`;
- `screen.blocks` / `block:<slug>` в `slot-fills`/`states` →
  `…/screens/blocks/<slug>/`;
- `screen.transitions-to-screen` → `…/screens/screens/<slug>/`;
- `screen.mobile-of` → `…/screens/flows/<slug>/`;
- `block.used-by-screens` → `…/screens/screens/<slug>/`.

**В interface** (interface-слой того же проекта,
`docs/projects/<project-slug>/interface/`):
- `screen.situations` → строка `<slug>` в `…/interface/situation.md`;
- `screen.who` / `flow.who` → строка `<slug>` в `…/interface/who.md`;
- `block.interface-block` → строка `<slug>` в `…/interface/block.md`;
- `block.ux-substrates[*]` → строка `<slug>` в
  `…/interface/ux-substrate.md`;
- `data:<slug>` внутри `tree`/`slot-fills` → строка `<slug>` в
  `…/interface/data-items.md`.

**Assets**: каждый путь в `assets: [...]` ссылается на
существующий файл в
`docs/projects/<project-slug>/screens/assets/<kind>/<slug>/`.

**Inventory**: каждое имя `ui:<Component>` есть в инвентаре (см.
`ui-inventory.md`); либо имя — «ui-lib gap», зарегистрированный в
state-заметке.

`stable` может ссылаться на `draft` — это допустимо. Аудит подсветит
hint, но не блокирует stable.

### 3. Зеркала консистентны

- `block.ux-substrates` (screens, frontmatter) **равен**
  `block.ux-substrates` (interface,
  `docs/projects/<project-slug>/interface/block.md`, строка с тем же
  slug). При расхождении — `**blocker**` в state, не stable.
- `block.used-by-screens` **равен** множеству screen-slug'ов, в
  чьих `slot-fills`/`states` встречается `block:<slug>`. Скилл
  пересчитывает автоматически.
- `screen.blocks` **равен** множеству block-slug'ов, на которые
  ссылается `block:<slug>` внутри `slot-fills`/`states` экрана.
  Скилл пересчитывает автоматически.

### 4. Тест-критерий явно подтверждён

В README соответствующего kind (канон
`docs/projects/_template/screens/<kind>/README.md`) есть секция
`Тест-критерий` с примерами ✅/❌. Через `AskUserQuestion` скилл
предъявляет аналитику примеры и спрашивает: «какой из этих образцов
ближе всего к вашей записи?».

Запись проходит, когда аналитик соотносит её с ✅-примером и
эксплицитно подтверждает «да, это так».

### 5. State-заметка чиста по `**blocker**`-вопросам

`state/<project-slug>/<kind>/<slug>.md`:

- Не содержит секцию `## Открытые вопросы` ИЛИ
- Содержит, но в ней нет вопросов с префиксом/суффиксом `**blocker**`.

Не-blocker открытые вопросы при stable допустимы (они описывают
«хорошо бы узнать», не «здесь смысл сломан»).

Секция `## Доменные решения` и `## Что копать дальше` (включая
ui-lib gaps) к stable не относятся — они могут быть.

### 6. Дерево в теле полное

**flow**: тело — markdown-прозa без yaml-дерева. Этот пункт для
flow всегда ✅, если frontmatter полный.

**screen**:
- `slot-fills` покрывает все слоты, объявленные в shell как
  `required: true`. Опциональные слоты могут быть `—`, но не пусты.
- `states` покрывает 6 канон-состояний: `loading`, `empty`,
  `error`, `permission-denied`, `offline`, `not-found`. Каждое —
  либо явный override (хотя бы один слот переопределён), либо
  явное «здесь не применимо» с пояснением в комментарии.

**block**:
- `tree` содержит как минимум `block-body`.
- Каждый объявленный `ux-substrate` представлен узлом в дереве
  (по имени `ui:Component` + назначению считается покрытым;
  спорные — `AskUserQuestion`).
- Никаких inline-cтейтов (loading/empty/error) в дереве блока —
  это слой screen.

**shell**:
- `slots` объявлены и для каждого указаны `required` + `accepts`.
- `tree` содержит каркасный узел (`ui:AppShell` / `ui:Header` / …)
  с `(fills: $<slot>)` для каждого объявленного слота.
- Слотовые узлы пустые (без содержимого).

## Алгоритм проверки скиллом

После любой правки сущности:

1. Прочитать `docs/projects/<project-slug>/screens/<kind>/<slug>/index.md`.
2. Прочитать `state/<project-slug>/<kind>/<slug>.md`, если есть.
3. Прочитать соседей (см. `field-checklists.md`).
4. Прогнать пункты 1, 2, 3, 5, 6 (программно проверяемые).
5. Если все 5 ✅ — раунд `AskUserQuestion` по тест-критерию
   (пункт 4).
6. Если и пункт 4 ✅ — раунд `AskUserQuestion`: «Готов к stable,
   повышаем?» с опциями «Да, повысить» / «Нет, ещё не уверен»
   (через Other — что именно смущает).
7. При «Да» — `Edit`'ом поменять `status: draft → stable` в
   frontmatter.

## Что НЕ делать

- **Не повышать сам**, без подтверждения аналитика. Даже если все
  6 пунктов ✅ — спросить.
- **Не понижать `stable → draft` сам** при обнаружении проблемы —
  это смысловое решение аналитика. Можно подсветить и предложить.
- **Не считать пункт 4 пройденным «по умолчанию»**, потому что
  слоты заполнены. Тест-критерий — отдельное смысловое
  подтверждение.
- **Не игнорировать `**blocker**`-вопросы** — они должны быть
  закрыты или удалены (если стали неактуальны) до stable.
- **Не считать пункт 3 пройденным**, если зеркало
  `block.ux-substrates` расходится с interface — даже если аналитик
  сказал «потом разберёмся».
