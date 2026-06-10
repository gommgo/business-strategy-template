# Чек-листы полей по kind

По разделу на каждый из 5 артефактов telegram-bot-flow. В каждом разделе:

- **Поля** — что во frontmatter / мета-блоке секции / колонках, что
  обязательно.
- **Тело** — какие секции обязательны (для dialog/window/use-case).
- **Ссылается на** — какие соседи (слой бота + interface + domains).
- **Кто ссылается на это** — обратные связи.
- **Главные anti-patterns** — короткий список из канона kind.
- **Порядок копания** — последовательность вопросов в режиме A/C.

Полные критерии — в каноне
`docs/projects/_template/telegram-bot-flow/_template/`
(`features/README.md` — формы `dialog.md` / `window.md` / `use-case.md`;
`command.md`, `notification.md` — root-реестры). Данные поверхности
проекта живут в
`docs/projects/<project-slug>/telegram-bot-flow/<surface>/`: фичи —
`features/<feature>/` (диалог — `dialog.md`, окна — секции `## <slug>` в
`window.md`, use-case'ы бота — секции `## <slug>` в `use-case.md`); команды
и уведомления — реестрами корня. Здесь — выжимка для скилла.

Дальше `…/telegram-bot-flow/`, `…/interface/` и `…/domains/` — это слои
**текущей поверхности текущего проекта** (domains — surface-агностичный
слой того же проекта). Изоляция двухуровневая: поверхности и фичи. Рёбра
внутри фичи (окно ↔ диалог ↔ use-case бота) — slug-валидируемы в пределах
**своей фичи**; interface-рефы — в пределах поверхности; доменные рефы bot
UC и триггеры уведомлений — семантические (см. `domain-bridge.md`).

---

## dialog

**Frontmatter**: `slug`, `name`, `description`, `states-group`,
`windows`, `started-by`, `launch-mode`, `start-data`, `who`, `status`.

**Обязательные**: все, кроме `start-data` (может быть `—`).

**Тело**: yaml `dialog-data` (контракт накопления: ключ → что лежит,
JSON-примитивы) + `transitions` (сводное зеркало графа окон; источник
правды — `transition` виджетов).

**Ссылается на**:
- `windows` → секции `## <slug>` в `window.md` **этой фичи**;
- `started-by` → `command:<slug>` (реестр корня `command.md`),
  `notification:<slug>` (реестр корня `notification.md`),
  `feature:<slug>` (другая фича, входящая через `start:<эта-фича>`);
- `who` → `…/interface/<surface>/who.md`.
**Кто ссылается**: окна этой фичи (принадлежат диалогу структурно —
лежат в `window.md` фичи), `command.starts` (`feature:<slug>`),
`notification.action` (`feature:<slug>`), `transition: start:<feature>`
в виджетах окон других фич.

**Anti-patterns**:
- window / command / zone interface / весь бот — не путать с dialog;
- несколько диалогов в одной фиче (вложенный сценарий — отдельная фича,
  вход через `start:<feature>`);
- диалог без `started-by` (недостижим);
- окно в `windows`, которого нет секцией в `window.md` фичи;
- несериализуемое в `dialog-data`;
- `transitions`, расходящийся с виджетами окон;
- два диалога с одним `states-group`;
- глубокая матрёшка `start:<feature>` без `done` на каждом уровне.

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
4. `windows`: мультивыбор существующих окон **этой фичи** (секции в
   `window.md`) + «нужно новое» (Other → A в window, по окну на шаг
   сценария — секция в `window.md` фичи). Порядок списка = порядок
   состояний — переспросить порядок явно.
5. `started-by`: опции из существующих `command.md` / `notification.md`
   корня / других фич с `start:`-потенциалом (`feature:<slug>`) + «нужна
   новая команда» (Other → A в command). Минимум один вход.
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

Живёт **секцией** `## <window-slug>` в `window.md` своей фичи
(`features/<feature>/window.md`); принадлежность диалогу — структурная
(файл фичи), не поле.

**Мета-блок секции**: `name`, `state`, `interface-block`,
`ux-substrates`, `situations`, `who`, `status` (`slug` — заголовок H2).

**Обязательные**: все.

**Тело**: yaml `message` (text + опц. media) + `widgets` (список сверху
вниз = порядок клавиатуры; `row:` группирует) + `getter` (контракт
данных) + `errors` (канон-ключи `backend-unavailable`, `invalid-input`).

**Ссылается на**:
- (структурно — диалог своей фичи: окно лежит в `window.md` фичи);
- `interface-block` → `…/interface/<surface>/block.md`;
- `ux-substrates` → `…/interface/<surface>/ux-substrate.md` (зеркало
  набора атомов блока-источника);
- `situations` → `…/interface/<surface>/situation.md`;
- `who` → `…/interface/<surface>/who.md`;
- `widget.transition` → окно **этой фичи** / `back` / `done` /
  `start:<feature>`;
- `widget.action`, `getter.*.source` → use-case бота **этой фичи**
  (`use-case:<uc-slug>`, секция в `use-case.md` фичи, slug-валидируемо;
  `action` может быть `—` — чистая навигация);
- `getter.*.data` → `data:<slug>` в `…/interface/<surface>/data-items.md`;
- `message.media` → `assets/<window-slug>/…` (папка ассетов фичи) или
  `data:<slug>.<поле>`.
**Кто ссылается**: `dialog.windows`, `transition` виджетов соседних
окон **этой же фичи**.

**Anti-patterns**:
- dialog / block interface / notification / носитель бизнес-правил /
  код — не путать;
- плейсхолдер без ключа в `getter`, ключ без `fallback`;
- `action` мимо use-case бота («кнопка сама сохраняет в базу») или
  `action` на доменный use-case напрямую (с точкой) — действие ходит в
  домен только через use-case бота фичи;
- бизнес-правило в `when` («если сумма > 1000 — скидка») — `when` —
  исход use-case бота;
- тупик (ни одного `transition` и окно не последнее перед `done`);
- `transition` на окно чужой фичи (между фичами — только
  `start:<feature>`);
- дубль `id` виджета в одном окне;
- облик (эмодзи-оформление, HTML/Markdown, «жирная кнопка»);
- `ux-substrates`, расходящийся с блоком-источником;
- текст с inline-логикой («если X, показываем Y») — вариативность
  выражается ключами getter'а или разными окнами.

**Порядок копания**:

1. Фича-владелец: окно — секция в `window.md` фичи. Опции = существующие
   фичи (по именам их диалогов) + «нужна новая фича» (Other → A в dialog,
   что заводит папку фичи). Без фичи (диалога) окно не заводится.
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
   - `action` — опции use-case бота **этой фичи** + `—` (чистая
     навигация) + «нужен новый bot UC» (см. `domain-bridge.md` «Окно →
     bot UC»; bot UC мостится к домену в своих `Dependencies`);
   - `transition` — опции: окна **этой фичи** / `back` / `done` /
     `start:<feature>` / «условный» (исходы use-case бота → список
     `{ to, when }`, формулировки `when` — Other);
   - группировка в `row:` — спросить, какие кнопки в один ряд.
9. **Тело — `getter`** (по ключу за раунд): для каждого плейсхолдера
   `{…}` и каждого `items`:
   - `source` — опции enum: `use-case:<uc-slug>` (use-case бота этой
     фичи) / `dialog-data` / `start-data` / `const`;
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

## use-case

Use-case бота — **оркестратор** одного действия окна. Живёт **секцией**
`## <uc-slug>` в `use-case.md` своей фичи
(`features/<feature>/use-case.md`). Бизнес-правил не держит — собирает
ввод, дёргает доменный use-case, разбирает исход, апдейтит `dialog-data`,
возвращает исход окну. Заводится, когда виджету окна нужен `action`.

**Мета-блок секции**: `name`, `operation` (PascalCase, англ. —
структурный идентификатор для кода), `who`, `status` (`slug` —
заголовок H2).

**Обязательные**: все четыре мета-поля.

**Тело** — H3-секции (зеркало доменного use-case
`domains/_templates/use-case.md` без доменных-only секций):
`### Actor` · `### Inputs` · `### Outputs` · `### Dependencies` ·
`### Steps` · `### Errors`. `### Outputs` обязателен — называет исходы,
на которые смотрят `when` переходов окон.

**Ссылается на**:
- `### Dependencies` → доменные use-case `use-case:<ctx>.<Operation>`
  (`…/domains/<ctx>/use-cases/`, **семантически**; домен опционален) +
  строки стейта `dialog-data:<key>` (read | write, JSON-примитивы);
- `### Inputs` — источники ввода: `widget:<id>` / `dialog-data:<key>` /
  `start-data:<key>`.
**Кто ссылается**: `widget.action` и `getter.*.source`
(`use-case:<uc-slug>`) окон **этой же фичи** (slug-валидируемо в фиче).

**Anti-patterns**:
- носитель бизнес-правил (инвариант, бизнес-валидация, policy) — это в
  `domains/`; bot UC их **вызывает**, не повторяет;
- бизнес-правило в `### Steps` («если сумма > 1000») — решает домен;
- реф на доменный use-case без точки или на bot UC с точкой — точка
  различает уровни (без точки — bot UC, с точкой — доменный);
- путать с окном (UC обрабатывает действие и возвращает исход, показ —
  окно) или с доменным use-case;
- код (класс сервиса, метод API-клиента, формат запроса, ретраи).

**Порядок копания**:

1. Заводится из потребности виджета окна в `action` (см. window-порядок,
   п. 8) — смысл действия называет аналитик.
2. `name` (Other) → скилл выводит `slug` и предлагает `operation`
   (PascalCase, англ.) одной строкой для контроля.
3. `who`: мультивыбор из `…/interface/<surface>/who.md`.
4. **`### Actor`**: роль + триггер (виджет `<id>` окна `<window-slug>`
   фичи / вход диалога / system).
5. **`### Inputs`**: по полю — источник (`widget:<id>` / `dialog-data` /
   `start-data`), обязательность, смысл (Other).
6. **`### Dependencies`** — доменные use-case: опции существующих
   `use-case:<ctx>.<Operation>` из доменов + «нужна новая операция»
   (см. `domain-bridge.md` «Заведение Dependencies bot UC»); плюс строки
   `dialog-data:<key>` (read/write) — что bot UC читает/пишет в стейт.
7. **`### Steps`**: оркестрация (валидация формата → вызов домена →
   маппинг исхода → апдейт `dialog-data` → возврат исхода). Скилл следит,
   чтобы бизнес-правило не утекло в шаг.
8. **`### Outputs`**: исходы (на них смотрят `when` окон) — формулировки
   аналитика (Other).
9. **`### Errors`**: исход → когда → реакция окна
   (`backend-unavailable` → `errors.backend-unavailable` и т. п.).
10. Anti-patterns раундом + тест-критерий: «Оркестрация бота — собрать
    ввод, дёрнуть доменный use-case, разрулить исход и стейт?» — варианты
    ✅/❌ из канона.

**После заведения/правки `### Outputs`** — сверить с `when` переходов
окон фичи, которые ссылаются на этот UC: каждая ветка `when` должна
соответствовать объявленному исходу.

---

## command

**Колонки**: `slug`, `name`, `description`, `command`, `starts`,
`stack`, `payload`, `who`, `status`. Все обязательны (`starts` и
`payload` могут быть `—`).

**Тело**: нет — плоская таблица `command.md` **на корне поверхности**,
вне фич.

**Ссылается на**:
- `starts` → `feature:<slug>` (запускает диалог фичи) или `—` (статичный
  ответ);
- `who` → `…/interface/<surface>/who.md`.
**Кто ссылается**: `dialog.started-by` (`command:<slug>`),
`notification.action` (`command:<slug>`).

**Anti-patterns**:
- виджет `button` / dialog / notification / код — не путать;
- `/start` со `stack: push`;
- команда-шаг (`/next`, `/confirm`) — движение внутри сценария делают
  виджеты окон;
- `starts` на несуществующую фичу;
- payload без описания, что уезжает в `start-data`;
- deep-link, живущий только в тексте уведомления (не доехал до
  реестра).

**Порядок копания**:

1. `name` (Other) → скилл выводит `slug`; `description` (Other).
2. `command`: Other — slash-команда или форма deep-link (`/start`,
   `/start <param>`). Если `/start <param>` — это deep-link, спросить
   источник (уведомление, QR, реклама) для `description`.
3. `starts`: опции = существующие фичи (`feature:<slug>`, по именам
   диалогов) + `—` (статичный ответ) + «нужна новая фича» (Other → A в
   dialog).
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

**Тело**: нет — плоская таблица `notification.md` **на корне
поверхности**, вне фич.

**Ссылается на**:
- `trigger` → `event:<ctx>.<Event>` (`…/domains/<ctx>/events/`,
  семантически — напрямую, минуя use-case бота) | `schedule: <по-русски>`
  | `integration:<slug>` (`integration.md` проекта);
- `to` → `…/interface/<surface>/who.md`;
- `action` → `command:<slug>` (реестр корня `command.md`) |
  `feature:<slug>` (диалог фичи) | `—`.
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
5. `action`: опции = команды-deep-link из `command.md` корня + фичи
   (`feature:<slug>`) + `—`. Если действие нужно, а deep-link'а нет — A
   в command (deep-link обязан доехать до реестра).
6. `idempotency`: Other — ключ дедупликации («id события»,
   «booking_id + дата напоминания»). Без него строка не записывается.
7. Anti-patterns раундом + тест-критерий («Сообщение, которое бот
   отправляет сам по объявленному триггеру, с идемпотентностью и
   адресатом-ролью?») — варианты ✅/❌ из канона.
