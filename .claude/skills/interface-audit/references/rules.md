# Реестр правил `interface-audit`

Каждое правило: `id`, `severity`, `scope`, что проверяет, как проверять,
рекомендация в отчёт.

Категории:

- **R-SURF** — целостность хребта поверхностей (папка ↔ реестр `surface.md`).
- **R-XSURF** — изоляция поверхностей (ссылка не уходит наружу).
- **R-STRUCT** — структурная целостность (ошибки модели).
- **R-MIRROR** — синхронность зеркал ситуации.
- **R-SEM** — семантические подозрения.
- **R-COV** — coverage и стиль.

UX-слой партиционирован по поверхности (surface): на каждую поверхность
из реестра `docs/projects/<project-slug>/surface.md` — папка
`docs/projects/<project-slug>/interface/<surface>/` с 7 файлами. Все пути
ниже — внутри одной папки поверхности. Сокращённо `<surface>/<file>.md` —
`docs/projects/<project-slug>/interface/<surface>/<file>.md`.

Правила R-STRUCT/R-MIRROR/R-SEM/R-COV применяются **в пределах одной
поверхности**: ссылочные поля разрешаются только среди записей той же
папки `<surface>/`. Аудит итерирует по каждой папке поверхности из scope
отдельно. R-SURF/R-XSURF — про границу между поверхностями.

Кросс-поверхностная сверка (один и тот же бизнес-датум на web и в боте —
две записи в разных папках; общий `who`/`user`) — **вне scope этого
аудита**, её делает `/cross-audit`. Правило «один датум, один slug»
(R-COV-007) считается **внутри поверхности**.

---

## R-SURF (хребет поверхностей)

### R-SURF-001 «папка поверхности вне реестра»

- **severity**: `error`.
- **scope**: подпапки `docs/projects/<project-slug>/interface/` ↔
  `surface.md`.
- **проверка**: каждая подпапка `interface/<X>/` имеет строку `slug: X`
  в реестре `docs/projects/<project-slug>/surface.md`. Хребет ведёт
  реестр — папки интерфейса для поверхности вне реестра быть не должно.
- **рекомендация**: «Завести строку `<X>` в `surface.md` через
  `/project-deep-dive <project-slug>`, либо удалить папку
  `interface/<X>/` (она осиротела относительно хребта)».

### R-SURF-002 «поверхность реестра без папки interface»

- **severity**: `hint` (coverage).
- **scope**: `surface.md` ↔ подпапки `interface/`.
- **проверка**: для каждой строки реестра `surface.md` существует папка
  `interface/<slug>/`. Отсутствие — не ошибка модели, а непокрытая
  поверхность (интерфейс ещё не заводили).
- **рекомендация**: «Поверхность объявлена в `surface.md`, но её
  interface ещё не начат — завести через `/interface-deep-dive
  <project-slug> <slug>`, либо это сознательно отложено».

---

## R-XSURF (изоляция поверхностей)

### R-XSURF-001 «ссылка из одной поверхности в другую»

- **severity**: `error`.
- **scope**: все 7 файлов любой папки `<surface>/`.
- **проверка**: каждое slug-значение в ссылочном поле разрешается среди
  записей **той же** папки `<surface>/`. Если slug не найден в своей
  поверхности, но найден в другой — это пересечение границы (а не просто
  битая ссылка R-STRUCT-001): поверхности изолированы.
- **рекомендация**: «Поверхности изолированы — ссылка не должна уходить в
  чужую папку. Завести сущность в своей поверхности через
  `/interface-deep-dive <project-slug> <surface> <kind>`, либо убрать
  ссылку. Общее между поверхностями (один user, один датум на web и в
  боте) сводит `/cross-audit`, не межпапочной ссылкой».

---

## R-STRUCT (структура)

### R-STRUCT-001 «валидность ссылок»

- **severity**: `error`.
- **scope**: все 7 файлов одной папки `<surface>/`.
- **проверка**: каждое slug-значение в ссылочном поле существует как
  `slug` строки в соответствующем файле **той же поверхности**:
  - `situation.stage` → `<surface>/stage.md`
  - `situation.who` → `<surface>/who.md`
  - `situation.entry-data` / `exit-data` (массивы) → `<surface>/data-items.md`
  - `situation.ux-substrate` (массив, зеркало) → `<surface>/ux-substrate.md`
  - `situation.block` (массив, зеркало) → `<surface>/block.md`
  - `block.zone` → `<surface>/zone.md`
  - `block.who` (массив) → `<surface>/who.md`
  - `block.ux-substrates` (массив) → `<surface>/ux-substrate.md`
  - `block.transition-to-block` (массив) → `<surface>/block.md`
  - `block.transition-from-zone` (массив) → `<surface>/zone.md`
  - `zone.parent-zone` → `<surface>/zone.md`
  - `ux-substrate.situation` → `<surface>/situation.md`
- **рекомендация**: «Завести stub через `/interface-deep-dive
  <project-slug> <surface> <kind>:<missing-slug>` или заменить ссылку на
  существующий slug этой поверхности».
- **примечание**: если slug отсутствует в своей поверхности, но есть в
  другой — это R-XSURF-001 (пересечение границы), а не битая ссылка.

### R-STRUCT-002 «цикл parent-zone»

- **severity**: `error`.
- **scope**: `<surface>/zone.md`.
- **проверка**: пройти по `parent-zone` от каждой zone вверх; если
  возвращается к стартовой — цикл.
- **рекомендация**: «Пересмотреть иерархию через `/interface-deep-dive
  <project-slug> <surface> zone:<slug>`; одной из зон в цикле должен быть
  `parent-zone = —` или другой корень».

### R-STRUCT-003 «дубликат slug»

- **severity**: `error`.
- **scope**: каждый файл поверхности независимо.
- **проверка**: внутри одного файла `<surface>/<kind>.md` все `slug`
  уникальны.
- **рекомендация**: «Переименовать дубликат через `/interface-deep-dive
  <project-slug> <surface>` (каскадно правит ссылки)».

### R-STRUCT-004 «явный переход внутри одной зоны»

- **severity**: `error`.
- **scope**: `<surface>/block.md`.
- **проверка**: для каждого `block.transition-to-block` — целевой блок
  не находится в той же `zone`, что исходный. Внутри одной зоны блоки
  достижимы неявно — явные переходы пишутся только межзонные.
- **рекомендация**: «Удалить явный transition внутри зоны через
  `/interface-deep-dive <project-slug> <surface> block:<slug>`
  (внутризонная связность по умолчанию)».

### R-STRUCT-005 «block без `ux-substrates`»

- **severity**: `error`.
- **scope**: `<surface>/block.md`.
- **проверка**: `block.ux-substrates` непуст и не `—`.
- **рекомендация**: «Завести субстраты через `/interface-deep-dive
  <project-slug> <surface> ux-substrate` и связать с этим блоком, либо
  удалить блок».

### R-STRUCT-006 «block без `who`»

- **severity**: `error`.
- **scope**: `<surface>/block.md`.
- **проверка**: `block.who` непуст и не `—`.
- **рекомендация**: «Дополнить `block.who` через `/interface-deep-dive
  <project-slug> <surface> block:<slug>`; для универсального — `[any]`».

### R-STRUCT-007 «status вне enum»

- **severity**: `error`.
- **scope**: все 7 файлов поверхности.
- **проверка**: `status` ∈ {`draft`, `stable`}.
- **рекомендация**: «Поправить status через `/interface-deep-dive
  <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-008 «`ux-substrate.type` вне enum»

- **severity**: `error`.
- **scope**: `<surface>/ux-substrate.md`.
- **проверка**: `type` ∈ {`команда`, `ввод`, `выбор`, `инфо`, `список`}.
- **рекомендация**: «Поправить type через `/interface-deep-dive
  <project-slug> <surface> ux-substrate:<slug>`».

---

## R-MIRROR (зеркала)

### R-MIRROR-001 «situation.ux-substrate ↔ ux-substrate.situation»

- **severity**: `error`.
- **scope**: `<surface>/situation.md` ↔ `<surface>/ux-substrate.md`.
- **проверка**: для каждой ситуации S набор `S.ux-substrate` равен
  множеству `{u.slug | u ∈ <surface>/ux-substrate.md, u.situation == S.slug}`.
- **рекомендация**: «Пересчитать зеркало через `/interface-deep-dive
  <project-slug> <surface> situation:<slug>` (скилл синхронизирует
  автоматически)».

### R-MIRROR-002 «situation.block ↔ join через субстраты»

- **severity**: `error`.
- **scope**: `<surface>/situation.md` ↔ `<surface>/block.md` через
  `<surface>/ux-substrate.md`.
- **проверка**: для каждой ситуации S набор `S.block` равен множеству
  `{b.slug | b ∈ <surface>/block.md, b.ux-substrates ∩ S.ux-substrate ≠ ∅}`.
- **рекомендация**: «Пересчитать зеркало через `/interface-deep-dive
  <project-slug> <surface> situation:<slug>`».

---

## R-SEM (семантика)

### R-SEM-001 «`goal` похож на предусловие»

- **severity**: `warning`.
- **scope**: `<surface>/situation.md`.
- **проверка**: `goal` содержит маркеры предусловия: «чтобы продолжить»,
  «чтобы войти», «чтобы получить доступ», «авторизоваться чтобы»,
  «чтобы перейти к», «чтобы открыть».
- **рекомендация**: «`goal` подменён предусловием следующего шага —
  уточнить через `/interface-deep-dive <project-slug> <surface>
  situation:<slug>`, цель должна объяснять смысл шага в объемлющей
  деятельности, не "чтобы пройти дальше"».

### R-SEM-002 «`using-what` содержит облик»

- **severity**: `warning`.
- **scope**: `<surface>/situation.md`.
- **проверка**: `using-what` содержит маркеры craft: «primary»,
  «secondary», «md», «sm», «lg», «xl», «иконк», «размер», «цвет»,
  «hex», «#» с цифрами, упоминания компонентов из библиотеки.
- **рекомендация**: «`using-what` — бизнес-средство, не облик. Уточнить
  через `/interface-deep-dive <project-slug> <surface> situation:<slug>`;
  облик — craft в `@stit/ui`».

### R-SEM-003 «пустой обязательный слот»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: все 7 файлов поверхности; список обязательных слотов по
  kind — в `interface-deep-dive/references/field-checklists.md`.
- **проверка**: для каждой записи — каждый обязательный слот непуст и
  не `—`.
- **рекомендация**: «Заполнить через `/interface-deep-dive <project-slug>
  <surface> <kind>:<slug>`; для stable обязательные слоты не могут быть
  пусты».

### R-SEM-004 «`description` совпадает с `name`»

- **severity**: `warning`.
- **scope**: все 7 файлов поверхности.
- **проверка**: `description` после трима/lowercase = `name` или
  содержится в `name` целиком, не добавляя смысла.
- **рекомендация**: «`description` должен пояснять что/зачем, а не
  повторять `name`».

### R-SEM-005 «block без входа»

- **severity**: `warning`.
- **scope**: `<surface>/block.md`.
- **проверка**: `entrypoint = false` И блок не таргет ни одного
  `transition-to-block` И `transition-from-zone = —` И в `block.zone`
  есть другие блоки (внутризонная неявная связность спасает только
  тогда, когда в зоне ≥2 блоков). Если ни одно условие не даёт входа —
  блок недостижим.
- **рекомендация**: «Сделать `entrypoint=true`, добавить
  `transition-from-zone`, или сделать целью `transition-to-block`
  другого блока через `/interface-deep-dive <project-slug> <surface>
  block:<slug>`».

---

## R-COV (coverage и стиль)

### R-COV-001 «who без покрытия»

- **severity**: `hint`.
- **scope**: `<surface>/who.md`.
- **проверка**: для каждого `who.slug` есть хотя бы одна ситуация с
  `situation.who == slug`.
- **рекомендация**: «Завести ситуацию-инициатор через
  `/interface-deep-dive <project-slug> <surface> situation`, или удалить
  участника через `/interface-deep-dive <project-slug> <surface>
  who:<slug>` (каскадно)».

### R-COV-002 «stage без покрытия»

- **severity**: `hint`.
- **scope**: `<surface>/stage.md`.
- **проверка**: для каждого `stage.slug` есть хотя бы одна ситуация с
  `situation.stage == slug`.
- **рекомендация**: «Завести ситуацию на этом этапе через
  `/interface-deep-dive <project-slug> <surface> situation`, или удалить
  этап».

### R-COV-003 «zone без блоков»

- **severity**: `hint`.
- **scope**: `<surface>/zone.md`.
- **проверка**: для каждой `zone.slug` есть хотя бы один блок с
  `block.zone == slug`.
- **рекомендация**: «Завести блок в зоне через `/interface-deep-dive
  <project-slug> <surface> block`, или удалить зону».

### R-COV-004 «stable ссылается на draft»

- **severity**: `hint`.
- **scope**: все ссылочные поля поверхности.
- **проверка**: запись со `status: stable` имеет ссылку на запись с
  `status: draft`.
- **рекомендация**: «Не блокирует stable, но стоит докопать draft-
  соседа: `/interface-deep-dive <project-slug> <surface>
  <kind>:<slug-соседа>`».

### R-COV-005 «короткое `description`»

- **severity**: `hint`.
- **scope**: все 7 файлов поверхности.
- **проверка**: длина `description` меньше 10 символов.
- **рекомендация**: «`description` слишком короткое для смысловой
  ясности; уточнить через `/interface-deep-dive <project-slug> <surface>
  <kind>:<slug>`».

### R-COV-006 «одинокий субстрат»

- **severity**: `hint`.
- **scope**: `<surface>/ux-substrate.md`.
- **проверка**: для каждого ux-substrate U — ситуация U.situation
  должна иметь хотя бы один блок в зеркале `situation.block`. Если её
  блоков 0 — субстрат «висит в воздухе» (без блока, который бы его
  показал).
- **рекомендация**: «Собрать субстрат в блок через `/interface-deep-dive
  <project-slug> <surface> block`».

### R-COV-007 «один датум — один slug (в пределах поверхности)»

- **severity**: `hint`.
- **scope**: `<surface>/data-items.md`.
- **проверка**: внутри `<surface>/data-items.md` один и тот же
  бизнес-датум не заведён двумя разными slug. Реестр датумов сквозной
  **в пределах поверхности** — дубль внутри одной папки нарушает канон.
- **рекомендация**: «Слить дубль через `/interface-deep-dive
  <project-slug> <surface> data-items:<slug>`. Один и тот же датум на
  разных поверхностях (web и бот) — две законные записи в разных папках,
  их сверяет `/cross-audit`, не этот аудит».
