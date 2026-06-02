# Чек-листы полей по kind

По разделу на каждый из 4 артефактов screens. В каждом разделе:

- **Поля** — что во frontmatter, что обязательно, что опционально.
- **Тело** — нужно ли yaml-дерево и какие узлы обязательны.
- **Ссылается на** — какие соседи (screens + interface).
- **Кто ссылается на это** — обратные связи.
- **Главные anti-patterns** — короткий список из README'а kind.
- **Порядок копания** — последовательность вопросов в режиме A/C.

Полные критерии — в каноне
`docs/projects/_canon/screens/<kind>/README.md` (форма-образец, общая
для всех проектов). Данные проекта живут в
`docs/projects/<project-slug>/screens/<kind>/<slug>/index.md`. Здесь —
выжимка для скилла.

Дальше `…/screens/` и `…/interface/` — это слои **текущего проекта**:
`docs/projects/<project-slug>/screens/` и
`docs/projects/<project-slug>/interface/` соответственно.

---

## flow

**Frontmatter**: `slug`, `name`, `description`, `desktop`, `mobile`,
`transitions`, `who`, `assets`, `status`.

**Обязательные**: `slug`, `name`, `description`, `desktop` (непустой
массив), `mobile` (непустой массив, обычно ≥2), `status`.
**Опциональные**: `transitions`, `who`, `assets`.

**Тело**: yaml-дерева нет. Тело — markdown-прозa с пояснением, что
именно объединяет flow.

**Ссылается на**:
- `desktop` / `mobile` → `…/screens/screens/<slug>/` (screens);
- `transitions[].{from,to}` → screens той же mobile-серии;
- `who` → `…/interface/who.md` (interface).
**Кто ссылается**: `screen.mobile-of` (для screen, входящих в
mobile-серию потока).

**Anti-patterns**:
- screen / shell / situation / route / state — не путать с flow;
- пустой `desktop` или пустой `mobile`;
- один screen-slug в обоих списках (это разные viewport → должны быть
  разные screen);
- transitions между desktop- и mobile-screen;
- flow с одним screen и в `desktop`, и в `mobile` (это просто screen
  с `viewport: any`).

**Порядок копания**:

1. `slug`, `name`, `description` (Other).
2. `desktop`: мультивыбор существующих screens с `viewport: desktop`
   или «нужен новый» (Other → A в screen).
3. `mobile`: мультивыбор существующих screens с `viewport: mobile`
   или «нужен новый» (Other → A в screen). Минимум 2 в режиме
   flow — иначе anti-pattern.
4. `transitions` (опц): для каждой пары `from→to` в mobile-серии
   собрать `{from, to, trigger}`. Триггер — Other (`tap row`,
   `apply / close`, `back`).
5. `who` (опц): мультивыбор из `…/interface/who.md` + «нужен
   новый» (Other → запустить `interface-deep-dive who`).
6. `assets` (опц): см. `assets-policy.md`.
7. Anti-patterns раундом: «Это просто screen?» / «Это
   sidebar→drawer?» (бинарные опции + Other).
8. Тест-критерий: «Это объединение N screen-slug разных viewport
   вокруг одной задачи?» — варианты ✅/❌ из README.

---

## screen

**Frontmatter**: `slug`, `name`, `description`, `shell`, `blocks`,
`situations`, `who`, `route`, `viewport`, `entrypoint`,
`transitions-to-screen`, `mobile-of`, `role`, `assets`, `status`.

**Обязательные**: `slug`, `name`, `description`, `shell`, `blocks`,
`situations`, `who`, `route`, `viewport`, `status`.
**Опциональные**: `entrypoint`, `transitions-to-screen`, `mobile-of`,
`role`, `assets`.

**Тело**: yaml `slot-fills` + `states`.
- `slot-fills`: каждый слот из shell заполнен (`block:<slug>`, либо
  inline-дерево, либо `—` если опционален).
- `states`: delta-overrides слотов для нештатных состояний. Канон:
  `loading`, `empty`, `error`, `permission-denied`, `offline`,
  `not-found`. Stable требует покрытия всех 6 (явный override либо
  явное «здесь не применимо»).

**Ссылается на**:
- `shell` → `…/screens/shells/<slug>/`;
- `blocks` → `…/screens/blocks/<slug>/`;
- `situations` → `…/interface/situation.md`;
- `who` → `…/interface/who.md`;
- `transitions-to-screen` → screens;
- `mobile-of` → flow;
- `block:<slug>` внутри `slot-fills`/`states` → screens-blocks;
- `data:<slug>` внутри inline-деревьев → `…/interface/data-items.md`.
**Кто ссылается**: `flow.desktop`, `flow.mobile`,
`block.used-by-screens` (зеркало), `screen.transitions-to-screen`
(другие screens).

**Anti-patterns**:
- block / shell / flow / route / data-слой — не путать;
- облик в `slot-fills` (цвета, пиксели, шрифты);
- тематические оси (`density`, `brand`, `scheme`) как props
  компонентов;
- breakpoints в `slot-fills`;
- FSD-имена (`widget`, `feature`) в дереве или frontmatter;
- `state` без явного override (пустая секция);
- расхождение `screen.blocks` и реально использованных `block:` в
  `slot-fills`/`states`;
- `screen.situations`, не покрывающий ситуации, чьи ux-substrates
  есть на этом экране (через `block.ux-substrates`).

**Порядок копания**:

1. `slug`, `name`, `description` (Other).
2. `shell`: опции = существующие shell-slug'и + «нужен новый»
   (Other → A в shell).
3. `viewport`: три опции enum `desktop` / `mobile` / `any`.
4. `route`: Other (URL `/foo` или именованный view
   `modal:archive-confirm`).
5. `who`: мультивыбор из `…/interface/who.md` + «нужен новый»
   (Other → запустить `interface-deep-dive who`).
6. `situations`: мультивыбор из `…/interface/situation.md` +
   «нужна новая» (Other → запустить
   `interface-deep-dive situation`).
7. `blocks`: мультивыбор из существующих screens-blocks + «новый»
   (Other → A в block). Должен включать всё, что появится в
   `slot-fills`/`states`.
8. `entrypoint` (опц): два варианта `true` / `false`.
9. `mobile-of` (опц): если `viewport: mobile` — выбор flow, в
   который входит. Иначе `—`.
10. `role` (опц): для участников flow — `master` / `detail` /
    `filters` / Other.
11. `transitions-to-screen` (опц): мультивыбор существующих screens
    + Other.
12. **Тело — `slot-fills`** (раунд за раундом, по одному слоту):
    - для каждого слота shell из соседнего файла:
      - опции: «`block:<slug>` из существующих» / «inline-дерево»
        (Other) / «оставить `—`» (если слот опционален в shell);
      - если inline-дерево — углубление по узлам через ui-инвентарь.
13. **Тело — `states`** (раунд за раундом по каждому из 6 канон-
    состояний):
    - опции: «использовать ui-feedback (`ui:Skeleton` для loading,
      `ui:EmptyState`/`ui:ErrorState`/… для остальных)» / «inline-
      дерево» (Other) / «здесь не применимо» (с пометкой в state-
      заметке).
14. `assets` (опц): см. `assets-policy.md`.
15. Anti-patterns раундом.
16. Тест-критерий: «Одна точка маршрута / view с заполненными слотами
    shell и описанными нештатными состояниями?» — варианты ✅/❌
    из README.

**После правки `slot-fills`** — пересчитать `screen.blocks` (должен
содержать все `block:<slug>` из слотов и states).

---

## block

**Frontmatter**: `slug`, `name`, `description`, `interface-block`,
`ux-substrates`, `data`, `slots`, `used-by-screens`, `assets`,
`status`.

**Обязательные**: `slug`, `name`, `description`, `interface-block`,
`ux-substrates` (непустой), `status`.
**Опциональные**: `data`, `slots`, `used-by-screens`, `assets`.

**Тело**: yaml `tree` с internal-zones (`block-header`, `block-body`,
`block-footer`, `block-aside`). Минимум — `block-body`.

**Ссылается на**:
- `interface-block` → `…/interface/block.md` (тот же slug,
  ровно один);
- `ux-substrates` → `…/interface/ux-substrate.md` (зеркало
  `interface/block.md.ux-substrates`);
- `data: { <param>: data:<slug> }` → `…/interface/data-items.md`;
- `used-by-screens` → screens (зеркало; источник — реальные ссылки
  `block:<slug>` в screens);
- `block:<slug>` внутри `tree` через `slots` → другие screens-
  blocks (если блок-контейнер);
- `data:<slug>` внутри `tree` → `…/interface/data-items.md`.
**Кто ссылается**: `screen.blocks`, `screen.slot-fills`,
`screen.states`.

**Anti-patterns**:
- screen / shell / один компонент / data-слой / FSD-узел — не путать;
- расхождение `ux-substrates` с зеркалом в `interface/block.md`;
- дерево без `block-body`;
- облик в дереве (цвет, тень, шрифт, пиксели);
- тематические props (`density`/`brand`/`scheme`) в узлах;
- breakpoints в дереве;
- один и тот же `data:<slug>` под разными именованными слотами;
- inline-состояния (loading/empty) в дереве блока — это слой screen.

**Порядок копания**:

1. `slug`, `name`, `description` (Other).
2. `interface-block`: опции = существующие interface-block-slug'и
   (читать из `…/interface/block.md`) + «нужен новый» (Other →
   предложить запустить `interface-deep-dive block:<slug>`).
   **По канону slug в screens совпадает с slug в interface.**
3. `ux-substrates`: автоматически предложить весь список
   `ux-substrates` выбранного interface-block по умолчанию (для
   зеркала). Аналитик может скорректировать; при несовпадении —
   обработать через политику зеркал (см. SKILL.md).
4. `data` (опц): мультивыбор data-items из interface + Other для
   нового; формат `{ <param>: data:<slug> }`. Anti-pattern: один
   data: под разными `<param>`.
5. `slots` (опц): нужны ли именованные слоты под вложение `block:`
   (контейнер блок). Опции «нет» / «да» (Other → перечислить имена).
6. `used-by-screens` (опц): зеркало; в режиме A заполняется по мере
   того, как screens начинают на него ссылаться. Скилл предлагает
   текущий список (выводимо из screens), аналитик подтверждает.
7. **Тело — `tree`** (раунд за раундом, по зонам):
   - Начать с `block-body` (обязательная) — пройтись по узлам:
     выбор `ui:Component` из релевантной категории инвентаря
     (data-display, layout-примитивы, forms) + props enum + Other
     для свободных значений.
   - Затем `block-header` (опц): обычно `ui:Row` / `ui:Sticky` с
     поиском/кнопками.
   - Затем `block-footer` (опц): обычно `ui:Pagination` /
     `ui:Row` с действиями.
   - Затем `block-aside` (опц): для боковых дорожек блока.
   - Проверка покрытия: каждый объявленный `ux-substrate` должен
     быть представлен узлом дерева (через имя `ui:Component` +
     назначение).
8. `assets` (опц): см. `assets-policy.md`.
9. Anti-patterns раундом.
10. Тест-критерий: «Раскрытие одного interface-block в композицию
    компонентов — не экран, не каркас, не один компонент?» —
    варианты ✅/❌ из README.

**После правки `ux-substrates`** — сравнить с
`…/interface/block.md`; при расхождении — политика зеркал (см.
SKILL.md).

---

## shell

**Frontmatter**: `slug`, `name`, `description`, `slots`, `responsive`,
`assets`, `status`.

**Обязательные**: `slug`, `name`, `description`, `slots` (непустой
объект), `status`.
**Опциональные**: `responsive`, `assets`.

**Тело**: yaml `tree` — каркас (header / sidebar / main / detail /
overlay / footer и т.п.) с пометками `(fills: $<slot>)` для каждого
слота из `slots`.

**Ссылается на**: ничего наружу. Это самостоятельная капсула.
**Кто ссылается**: `screen.shell`.

**Anti-patterns**:
- screen / block / layout-примитив / sitemap — не путать;
- содержимое в shell-tree (конкретный блок, конкретный текст
  кнопки);
- тематические props (`density`/`brand`/`scheme`) на узлах shell;
- пиксели / raw-CSS в `tree` или `responsive`;
- слот без `accepts` или без `required`;
- `responsive`-behaviour, не покрытое допустимыми значениями;
- структурный адаптив через `responsive` (когда меняется число
  экранов, а не облик слота) — это `flow`;
- shell без `slots`.

**Порядок копания**:

1. `slug`, `name`, `description` (Other).
2. `slots` (раунд за раундом, по одному слоту):
   - имя слота (Other, kebab-case);
   - `required`: опции `true` / `false`;
   - `accepts`: опции `block` / `tree` / `block | tree` /
     `block (modal/drawer)`.
   - повторять до «всё, больше слотов нет» (Other).
3. `responsive` (опц): по каждому breakpoint (`xs` / `sm` / `md` /
   `lg` / `xl`) — поведения слотов из enum (`visible` /
   `drawer-via-burger` / `overlay` / `stacked` / `hidden`). Спросить:
   «Меняется ли что-то на этом breakpoint?»
4. **Тело — `tree`**: ui:AppShell / ui:Header / ui:Sidebar /
   ui:Main / ui:Detail / ui:OverlayLayer / ui:Footer (из инвентаря
   shell-каркасов). Каждый узел, обёртывающий слот, получает
   `(fills: $<slot>)`. **Слотовые узлы — пустые** (без содержимого).
5. `assets` (опц): см. `assets-policy.md`.
6. Anti-patterns раундом.
7. Тест-критерий: «Объявление набора слотов + responsive-поведение
   — не сам route с контентом, не блок и не layout-примитив?» —
   варианты ✅/❌ из README.
