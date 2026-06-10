# Чек-листы полей по kind

По разделу на каждый из 4 артефактов telegram-bot-flow. В каждом разделе:

- **Поля** — что во frontmatter / колонках, что обязательно.
- **Тело** — какие секции yaml-блока обязательны (для dialog/window).
- **Ссылается на** — какие соседи (слой бота + interface + domains).
- **Кто ссылается на это** — обратные связи.
- **Главные anti-patterns** — короткий список из канона kind.
- **Порядок копания** — последовательность вопросов в режиме A/C.

Полные критерии — в каноне
`docs/projects/_template/telegram-bot-flow/_template/` (`dialogs/README.md`,
`windows/README.md`, `command.md`, `notification.md`). Данные поверхности
проекта живут в
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/`. Здесь —
выжимка для скилла.

Дальше `…/telegram-bot-flow/`, `…/interface/` и `…/domains/` — это слои
**текущей поверхности текущего проекта** (domains — surface-агностичный
слой того же проекта). Все slug-ссылки — в пределах одной поверхности;
доменные рефы — семантические (см. `domain-bridge.md`).

---

## dialog

**Frontmatter**: `slug`, `name`, `description`, `states-group`,
`windows`, `started-by`, `launch-mode`, `start-data`, `who`, `status`.

**Обязательные**: все, кроме `start-data` (может быть `—`).

**Тело**: yaml `dialog-data` (контракт накопления: ключ → что лежит,
JSON-примитивы) + `transitions` (сводное зеркало графа окон; источник
правды — `transition` виджетов).

**Ссылается на**:
- `windows` → `…/telegram-bot-flow/<surface>/windows/<slug>/`;
- `started-by` → `command:<slug>` (реестр `command.md`),
  `window:<slug>` (окно другого диалога с `transition: start:<этот>`),
  `notification:<slug>` (реестр `notification.md`);
- `who` → `…/interface/<surface>/who.md`.
**Кто ссылается**: `window.dialog`, `command.starts`,
`notification.action` (`dialog:<slug>`), `transition: start:<slug>` в
виджетах окон других диалогов.

**Anti-patterns**:
- window / command / zone interface / весь бот — не путать с dialog;
- диалог без `started-by` (недостижим);
- окно в `windows`, которого нет в `windows/` поверхности, или окно
  чужого диалога;
- несериализуемое в `dialog-data`;
- `transitions`, расходящийся с виджетами окон;
- два диалога с одним `states-group`;
- глубокая матрёшка `start:` без `done` на каждом уровне.

**Порядок копания**:

1. Синтез из interface: кандидат-зона (см. `interface-context.md`) —
   опции из `…/interface/<surface>/zone.md` + «без зоны-источника»
   (Other).
2. `name` (Other) → скилл выводит `slug` и предлагает `states-group`
   (PascalCase, англ.) одной строкой для контроля; `description`
   (Other).
3. `who`: мультивыбор из `…/interface/<surface>/who.md` + «нужен новый»
   (Other → запустить
   `interface-deep-dive <project-slug> <surface> who`).
4. `windows`: мультивыбор существующих окон без диалога-владельца +
   «нужно новое» (Other → A в window, по окну на шаг сценария). Порядок
   списка = порядок состояний — переспросить порядок явно.
5. `started-by`: опции из существующих `command.md` / окон с
   `start:`-потенциалом / `notification.md` + «нужна новая команда»
   (Other → A в command). Минимум один вход.
6. `launch-mode`: четыре опции enum `standard` / `root` / `single-top`
   / `exclusive` (root — для главного меню).
7. `start-data` (опц): Other — что передаётся при старте
   (JSON-примитивы), или `—`.
8. **Тело — `dialog-data`**: по ключу за раунд — имя ключа (скилл
   предлагает snake_case из смысла) + «что лежит» (Other, по-русски с
   JSON-формой). Проверка: только примитивы.
9. **Тело — `transitions`**: после того как окна диалога заведены —
   пересчитать сводку из `transition` виджетов, показать аналитику
   граф, спросить про дыры (окно без пути к `done` — тупик).
10. Anti-patterns раундом: «Это не один шаг (window)?» / «Это не весь
    бот?» (бинарные опции + Other).
11. Тест-критерий: «Завершённая задача участника из последовательности
    окон с явными входами и контрактом накопления?» — варианты ✅/❌
    из канона.

---

## window

**Frontmatter**: `slug`, `name`, `description`, `dialog`, `state`,
`interface-block`, `ux-substrates`, `situations`, `who`, `status`.

**Обязательные**: все.

**Тело**: yaml `message` (text + опц. media) + `widgets` (список сверху
вниз = порядок клавиатуры; `row:` группирует) + `getter` (контракт
данных) + `errors` (канон-ключи `backend-unavailable`, `invalid-input`).

**Ссылается на**:
- `dialog` → `…/telegram-bot-flow/<surface>/dialogs/<slug>/` (ровно
  один);
- `interface-block` → `…/interface/<surface>/block.md`;
- `ux-substrates` → `…/interface/<surface>/ux-substrate.md` (зеркало
  набора атомов блока-источника);
- `situations` → `…/interface/<surface>/situation.md`;
- `who` → `…/interface/<surface>/who.md`;
- `widget.transition` → окно того же диалога / `back` / `done` /
  `start:<dialog-slug>`;
- `widget.action`, `getter.*.source` → `use-case:<ctx>.<Operation>`
  (`…/domains/<ctx>/use-cases/`, семантически);
- `getter.*.data` → `data:<slug>` в `…/interface/<surface>/data-items.md`;
- `message.media` → `assets/windows/<slug>/…` или `data:<slug>.<поле>`.
**Кто ссылается**: `dialog.windows`, `transition` виджетов соседних
окон того же диалога.

**Anti-patterns**:
- dialog / block interface / notification / носитель бизнес-правил /
  код — не путать;
- плейсхолдер без ключа в `getter`, ключ без `fallback`;
- `action` мимо домена («кнопка сама сохраняет в базу»);
- бизнес-правило в `when` («если сумма > 1000 — скидка»);
- тупик (ни одного `transition` и окно не последнее перед `done`);
- `transition` на окно чужого диалога;
- дубль `id` виджета в одном окне;
- облик (эмодзи-оформление, HTML/Markdown, «жирная кнопка»);
- `ux-substrates`, расходящийся с блоком-источником;
- текст с inline-логикой («если X, показываем Y») — вариативность
  выражается ключами getter'а или разными окнами.

**Порядок копания**:

1. `dialog`: опции = существующие диалоги + «нужен новый» (Other → A в
   dialog). Без диалога окно не заводится.
2. Синтез из interface: `interface-block` — опции из
   `…/interface/<surface>/block.md` (приоритет — блоки зоны-источника
   диалога) + «нужен новый» (Other → предложить запустить
   `interface-deep-dive <project-slug> <surface> block:<slug>`).
3. `name` (Other) → скилл выводит `slug` и предлагает `state`
   (UPPER_SNAKE, англ.) одной строкой для контроля; `description`
   (Other).
4. `ux-substrates`: автоматически предложить весь список
   `ux-substrates` выбранного interface-блока по умолчанию (для
   зеркала). Аналитик может скорректировать; при несовпадении —
   политика зеркал (см. SKILL.md).
5. `situations`: мультивыбор из `…/interface/<surface>/situation.md`
   (приоритет — ситуации выбранных субстратов) + «нужна новая»
   (Other → запустить `interface-deep-dive`).
6. `who`: мультивыбор из `…/interface/<surface>/who.md`.
7. **Тело — `message`**: текст сообщения — Other (формулировка
   аналитика; скилл лишь подсказывает, какие плейсхолдеры `{…}`
   понадобятся под `инфо`/`список`-субстраты). `media` (опц) — референс
   из `assets/` или `data:<slug>.<поле>`, или `—`.
8. **Тело — `widgets`** (раунд за раундом, по виджету): скилл
   предлагает состав из соответствия атомам (`команда` → `button`,
   `ввод` → `text-input`, `выбор` → `select`/`multiselect`/`calendar` —
   см. `interface-context.md`); по каждому:
   - тип — опции виджет-языка;
   - `id` — скилл предлагает snake_case, контроль одной строкой;
   - `label` / `selected-label` / `validation` — Other (текст
     аналитика);
   - `action` — опции use-case из доменов + `—` (чистая навигация) +
     «нужен новый use-case» (см. `domain-bridge.md`);
   - `transition` — опции: окна диалога / `back` / `done` /
     `start:<dialog>` / «условный» (исходы use-case → список
     `{ to, when }`, формулировки `when` — Other);
   - группировка в `row:` — спросить, какие кнопки в один ряд.
9. **Тело — `getter`** (по ключу за раунд): для каждого плейсхолдера
   `{…}` и каждого `items`:
   - `source` — опции enum: `use-case:…` (выбор из доменов) /
     `dialog-data` / `start-data` / `const`;
   - `data` (опц) — выбор `data:<slug>` из
     `…/interface/<surface>/data-items.md`;
   - `fallback` — Other, обязателен («что показывает окно, когда
     источник недоступен»).
10. **Тело — `errors`**: тексты `backend-unavailable` и
    `invalid-input` — Other (или `—`, если ввода в окне нет).
11. Anti-patterns раундом.
12. Тест-критерий: «Один шаг диалога — одно сообщение с виджетами,
    данными и переходами?» — варианты ✅/❌ из канона.

**После правки `transition`** — пересчитать сводку
`dialog.transitions` диалога-владельца. **После правки
`ux-substrates`** — сравнить с `…/interface/<surface>/block.md`; при
расхождении — политика зеркал (см. SKILL.md).

---

## command

**Колонки**: `slug`, `name`, `description`, `command`, `starts`,
`stack`, `payload`, `who`, `status`. Все обязательны (`starts` и
`payload` могут быть `—`).

**Тело**: нет — плоская таблица `command.md`.

**Ссылается на**:
- `starts` → `dialog:<slug>` в `…/telegram-bot-flow/<surface>/dialogs/`
  (или `—` — статичный ответ);
- `who` → `…/interface/<surface>/who.md`.
**Кто ссылается**: `dialog.started-by` (`command:<slug>`),
`notification.action` (`command:<slug>`).

**Anti-patterns**:
- виджет `button` / dialog / notification / код — не путать;
- `/start` со `stack: push`;
- команда-шаг (`/next`, `/confirm`) — движение внутри сценария делают
  виджеты окон;
- `starts` на несуществующий диалог;
- payload без описания, что уезжает в `start-data`;
- deep-link, живущий только в тексте уведомления (не доехал до
  реестра).

**Порядок копания**:

1. `name` (Other) → скилл выводит `slug`; `description` (Other).
2. `command`: Other — slash-команда или форма deep-link (`/start`,
   `/start <param>`). Если `/start <param>` — это deep-link, спросить
   источник (уведомление, QR, реклама) для `description`.
3. `starts`: опции = существующие диалоги + `—` (статичный ответ) +
   «нужен новый» (Other → A в dialog).
4. `stack`: две опции `reset` / `push`. Для `/start` — только
   `reset`, без вопроса (инвариант).
5. `payload`: если deep-link — Other («что из параметра уезжает в
   `start-data`»), иначе `—`. Сверить со `start-data` целевого
   диалога.
6. `who`: мультивыбор из `…/interface/<surface>/who.md`.
7. Спросить про видимость в меню (служебный deep-link — пометка «в
   меню не выносится» в `description`).
8. Anti-patterns раундом + тест-критерий («Вход в бот извне,
   запускающий диалог или статичный ответ?») — варианты ✅/❌ из
   канона.

---

## notification

**Колонки**: `slug`, `name`, `description`, `trigger`, `to`,
`content`, `action`, `idempotency`, `status`. Все обязательны
(`action` может быть `—`).

**Тело**: нет — плоская таблица `notification.md`.

**Ссылается на**:
- `trigger` → `event:<ctx>.<Event>` (`…/domains/<ctx>/events/`,
  семантически) | `schedule: <по-русски>` | `integration:<slug>`
  (`integration.md` проекта);
- `to` → `…/interface/<surface>/who.md`;
- `action` → `command:<slug>` (реестр `command.md`) | `dialog:<slug>` |
  `—`.
**Кто ссылается**: `dialog.started-by` (`notification:<slug>`).

**Anti-patterns**:
- window / command / доменное событие / рассылка «по базе» / код —
  не путать;
- без `idempotency` или с триггером «когда захотим»;
- плейсхолдер `content`, которого нет в payload триггера;
- клавиатура-сценарий (больше одного действия — проектируй вход в
  диалог);
- `trigger: event:…` на событие, которого нет в `domains/` проекта
  (без зафиксированного требования);
- исходящее сообщение в обход реестра.

**Порядок копания**:

1. `name` (Other) → скилл выводит `slug`; `description` (Other —
   «зачем уведомление участнику»).
2. `trigger`: опции = существующие события из
   `…/domains/<ctx>/events/` + `schedule` (Other — по-русски) +
   `integration:<slug>` из `integration.md` + «нужно новое событие»
   (Other → требование в state, см. `domain-bridge.md`).
3. `to`: мультивыбор из `…/interface/<surface>/who.md` — адресат
   всегда роль, не «вся база».
4. `content`: Other — русский текст с плейсхолдерами `{…}`. Если
   `trigger: event:…` и событие существует — сверить плейсхолдеры с
   `## Payload` события, дыры показать.
5. `action`: опции = команды-deep-link из `command.md` + диалоги +
   `—`. Если действие нужно, а deep-link'а нет — A в command (deep-link
   обязан доехать до реестра).
6. `idempotency`: Other — ключ дедупликации («id события»,
   «booking_id + дата напоминания»). Без него строка не записывается.
7. Anti-patterns раундом + тест-критерий («Сообщение, которое бот
   отправляет сам по объявленному триггеру, с идемпотентностью и
   адресатом-ролью?») — варианты ✅/❌ из канона.
