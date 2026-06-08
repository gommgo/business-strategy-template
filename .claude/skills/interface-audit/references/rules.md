# Реестр правил `interface-audit`

Каждое правило: `id`, `severity`, `scope`, что проверяет, как проверять,
рекомендация в отчёт.

Категории:

- **R-STRUCT** — структурная целостность (ошибки модели).
- **R-MIRROR** — синхронность зеркал ситуации.
- **R-SEM** — семантические подозрения.
- **R-COV** — coverage и стиль.

---

## R-STRUCT (структура)

### R-STRUCT-001 «валидность ссылок»

- **severity**: `error`.
- **scope**: все 7 файлов.
- **проверка**: каждое slug-значение в ссылочном поле существует как
  `slug` строки в соответствующем файле:
  - `situation.stage` → `stage.md`
  - `situation.who` → `who.md`
  - `situation.entry-data` / `exit-data` (массивы) → `data-items.md`
  - `situation.ux-substrate` (массив, зеркало) → `ux-substrate.md`
  - `situation.block` (массив, зеркало) → `block.md`
  - `block.zone` → `zone.md`
  - `block.who` (массив) → `who.md`
  - `block.ux-substrates` (массив) → `ux-substrate.md`
  - `block.transition-to-block` (массив) → `block.md`
  - `block.transition-from-zone` (массив) → `zone.md`
  - `zone.parent-zone` → `zone.md`
  - `ux-substrate.situation` → `situation.md`
- **рекомендация**: «Завести stub через `/interface-deep-dive
  <kind>:<missing-slug>` или заменить ссылку на существующий slug».

### R-STRUCT-002 «цикл parent-zone»

- **severity**: `error`.
- **scope**: `zone.md`.
- **проверка**: пройти по `parent-zone` от каждой zone вверх; если
  возвращается к стартовой — цикл.
- **рекомендация**: «Пересмотреть иерархию через `/interface-deep-dive
  zone:<slug>`; одной из зон в цикле должен быть `parent-zone = —` или
  другой корень».

### R-STRUCT-003 «дубликат slug»

- **severity**: `error`.
- **scope**: каждый файл независимо.
- **проверка**: внутри одного файла все `slug` уникальны.
- **рекомендация**: «Переименовать дубликат через
  `/interface-deep-dive` (каскадно правит ссылки)».

### R-STRUCT-004 «явный переход внутри одной зоны»

- **severity**: `error`.
- **scope**: `block.md`.
- **проверка**: для каждого `block.transition-to-block` — целевой блок
  не находится в той же `zone`, что исходный. Внутри одной зоны блоки
  достижимы неявно — явные переходы пишутся только межзонные.
- **рекомендация**: «Удалить явный transition внутри зоны через
  `/interface-deep-dive block:<slug>` (внутризонная связность по
  умолчанию)».

### R-STRUCT-005 «block без `ux-substrates`»

- **severity**: `error`.
- **scope**: `block.md`.
- **проверка**: `block.ux-substrates` непуст и не `—`.
- **рекомендация**: «Завести субстраты через `/interface-deep-dive
  ux-substrate` и связать с этим блоком, либо удалить блок».

### R-STRUCT-006 «block без `who`»

- **severity**: `error`.
- **scope**: `block.md`.
- **проверка**: `block.who` непуст и не `—`.
- **рекомендация**: «Дополнить `block.who` через `/interface-deep-dive
  block:<slug>`; для универсального — `[any]`».

### R-STRUCT-007 «status вне enum»

- **severity**: `error`.
- **scope**: все 7 файлов.
- **проверка**: `status` ∈ {`draft`, `stable`}.
- **рекомендация**: «Поправить status через `/interface-deep-dive
  <kind>:<slug>`».

### R-STRUCT-008 «`ux-substrate.type` вне enum»

- **severity**: `error`.
- **scope**: `ux-substrate.md`.
- **проверка**: `type` ∈ {`команда`, `ввод`, `выбор`, `инфо`, `список`}.
- **рекомендация**: «Поправить type через `/interface-deep-dive
  ux-substrate:<slug>`».

---

## R-MIRROR (зеркала)

### R-MIRROR-001 «situation.ux-substrate ↔ ux-substrate.situation»

- **severity**: `error`.
- **scope**: `situation.md` ↔ `ux-substrate.md`.
- **проверка**: для каждой ситуации S набор `S.ux-substrate` равен
  множеству `{u.slug | u ∈ ux-substrate.md, u.situation == S.slug}`.
- **рекомендация**: «Пересчитать зеркало через `/interface-deep-dive
  situation:<slug>` (скилл синхронизирует автоматически)».

### R-MIRROR-002 «situation.block ↔ join через субстраты»

- **severity**: `error`.
- **scope**: `situation.md` ↔ `block.md` через `ux-substrate.md`.
- **проверка**: для каждой ситуации S набор `S.block` равен множеству
  `{b.slug | b ∈ block.md, b.ux-substrates ∩ S.ux-substrate ≠ ∅}`.
- **рекомендация**: «Пересчитать зеркало через `/interface-deep-dive
  situation:<slug>`».

---

## R-SEM (семантика)

### R-SEM-001 «`goal` похож на предусловие»

- **severity**: `warning`.
- **scope**: `situation.md`.
- **проверка**: `goal` содержит маркеры предусловия: «чтобы продолжить»,
  «чтобы войти», «чтобы получить доступ», «авторизоваться чтобы»,
  «чтобы перейти к», «чтобы открыть».
- **рекомендация**: «`goal` подменён предусловием следующего шага —
  уточнить через `/interface-deep-dive situation:<slug>`, цель должна
  объяснять смысл шага в объемлющей деятельности, не "чтобы пройти
  дальше"».

### R-SEM-002 «`using-what` содержит облик»

- **severity**: `warning`.
- **scope**: `situation.md`.
- **проверка**: `using-what` содержит маркеры craft: «primary»,
  «secondary», «md», «sm», «lg», «xl», «иконк», «размер», «цвет»,
  «hex», «#» с цифрами, упоминания компонентов из библиотеки.
- **рекомендация**: «`using-what` — бизнес-средство, не облик. Уточнить
  через `/interface-deep-dive situation:<slug>`; облик — craft в
  `@stit/ui`».

### R-SEM-003 «пустой обязательный слот»

- **severity**: `warning` (если `status: draft`), `error` (если
  `status: stable`).
- **scope**: все 7 файлов; список обязательных слотов по kind — в
  `interface-deep-dive/references/field-checklists.md`.
- **проверка**: для каждой записи — каждый обязательный слот непуст и
  не `—`.
- **рекомендация**: «Заполнить через `/interface-deep-dive
  <kind>:<slug>`; для stable обязательные слоты не могут быть пусты».

### R-SEM-004 «`description` совпадает с `name`»

- **severity**: `warning`.
- **scope**: все 7 файлов.
- **проверка**: `description` после трима/lowercase = `name` или
  содержится в `name` целиком, не добавляя смысла.
- **рекомендация**: «`description` должен пояснять что/зачем, а не
  повторять `name`».

### R-SEM-005 «block без входа»

- **severity**: `warning`.
- **scope**: `block.md`.
- **проверка**: `entrypoint = false` И блок не таргет ни одного
  `transition-to-block` И `transition-from-zone = —` И в `block.zone`
  есть другие блоки (внутризонная неявная связность спасает только
  тогда, когда в зоне ≥2 блоков). Если ни одно условие не даёт входа —
  блок недостижим.
- **рекомендация**: «Сделать `entrypoint=true`, добавить
  `transition-from-zone`, или сделать целью `transition-to-block`
  другого блока через `/interface-deep-dive block:<slug>`».

---

## R-COV (coverage и стиль)

### R-COV-001 «who без покрытия»

- **severity**: `hint`.
- **scope**: `who.md`.
- **проверка**: для каждого `who.slug` есть хотя бы одна ситуация с
  `situation.who == slug`.
- **рекомендация**: «Завести ситуацию-инициатор через
  `/interface-deep-dive situation`, или удалить участника через
  `/interface-deep-dive who:<slug>` (каскадно)».

### R-COV-002 «stage без покрытия»

- **severity**: `hint`.
- **scope**: `stage.md`.
- **проверка**: для каждого `stage.slug` есть хотя бы одна ситуация с
  `situation.stage == slug`.
- **рекомендация**: «Завести ситуацию на этом этапе через
  `/interface-deep-dive situation`, или удалить этап».

### R-COV-003 «zone без блоков»

- **severity**: `hint`.
- **scope**: `zone.md`.
- **проверка**: для каждой `zone.slug` есть хотя бы один блок с
  `block.zone == slug`.
- **рекомендация**: «Завести блок в зоне через `/interface-deep-dive
  block`, или удалить зону».

### R-COV-004 «stable ссылается на draft»

- **severity**: `hint`.
- **scope**: все ссылочные поля.
- **проверка**: запись со `status: stable` имеет ссылку на запись с
  `status: draft`.
- **рекомендация**: «Не блокирует stable, но стоит докопать draft-
  соседа: `/interface-deep-dive <kind>:<slug-соседа>`».

### R-COV-005 «короткое `description`»

- **severity**: `hint`.
- **scope**: все 7 файлов.
- **проверка**: длина `description` меньше 10 символов.
- **рекомендация**: «`description` слишком короткое для смысловой
  ясности; уточнить через `/interface-deep-dive <kind>:<slug>`».

### R-COV-006 «одинокий субстрат»

- **severity**: `hint`.
- **scope**: `ux-substrate.md`.
- **проверка**: для каждого ux-substrate U — ситуация U.situation
  должна иметь хотя бы один блок в зеркале `situation.block`. Если её
  блоков 0 — субстрат «висит в воздухе» (без блока, который бы его
  показал).
- **рекомендация**: «Собрать субстрат в блок через
  `/interface-deep-dive block`».
