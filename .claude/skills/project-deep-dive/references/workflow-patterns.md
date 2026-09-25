# Три режима ведения сеанса

`project-deep-dive` поддерживает три явно различающихся сценария входа.
Скилл выбирает режим по виду args при запуске и далее ведёт сеанс,
комбинируя точечные шаги. Зеркалит interface-deep-dive.

Все пути ниже **скоупятся в выбранный проект**. Данные пишутся в:

- vision — `docs/projects/<project-slug>/vision.md`;
- 6 плоских kind — `docs/projects/<project-slug>/<kind>.md`
  (`surface`, `user`, `integration`, `boundary`, `constraint`, `market`);
- capability — **файл на поверхность**:
  `docs/projects/<project-slug>/capability/<surface>.md`.

Форму (критерии / anti-patterns / тест-критерий) читаем из канона
`docs/projects/_template/project/<kind>.md`; для capability —
`docs/projects/_template/project/capability.md` (одна форма на все
поверхности).

## A. Новая сущность

**Сигнал**: args = `<project-slug> <kind>` или
`<project-slug> <kind>:<новый-slug>` (slug ещё не существует в файле
проекта).

### Шаги

1. Прочитать форму `docs/projects/_template/project/<kind>.md` целиком:
   секции `Критерии`, `Что НЕ`, `Тест-критерий`. Для capability форма —
   `_template/project/capability.md`.
2. Если kind = `capability` — **сначала определить поверхность**: из
   аргумента `capability:<surface>:<slug>` или пикером по реестру
   `surface.md` (по именам поверхностей). Без поверхности в реестре
   capability не заводится — предложить сперва завести `surface`.
3. Раунд 1 `AskUserQuestion` — фундамент: `name` и `description`
   (Other). `slug`, если он не дан аргументом, скилл выводит из `name` и
   показывает одной строкой для контроля (`.claude/rules/naming.md`).
4. Записать строку в файл данных:
   - 6 плоских kind → `docs/projects/<project-slug>/<kind>.md`;
   - capability → `docs/projects/<project-slug>/capability/<surface>.md`
     (если файла ещё нет — завести из формы
     `_template/project/capability.md`);
   - vision → `vision.md`, раздел Problem; на фазе discovery
     дополнительно добить `addresses-problem` (опции — строки
     `docs/business/business-problem.md`), оси `audience`/`intent`/
     `market-maturity` и `lifecycle` (enum).

   Новая строка — `slug + name + description + status=draft`, остальные
   ячейки `—`.
5. Раунд 2+ `AskUserQuestion` — батч по доменным слотам kind. См.
   `field-checklists.md`. До 4 вопросов в раунде; перемежать опции
   (anti-patterns / enums / соседи) и Other (значения). Для integration —
   среди слотов `surface` (массив slug-рефов в реестр), `target`
   (`external` / `sibling-project`) и `sibling-project` (slug соседа,
   обязателен iff `target: sibling-project`).
6. Если в поле нужна ссылка на ещё не существующую сущность — отработать
   **stub** (см. «Stub-сущности» ниже): создать stub-запись, записать
   state-заметку с открытым вопросом, продолжить текущую запись.
7. После всех слотов — раунд `AskUserQuestion` по `Тест-критерий`:
   варианты ✅/❌ из примеров md как опции. Аналитик подтверждает.
8. Применить чек-лист `draft-stable.md`. Если все 5 ✅ — предложить
   повышение в stable.
9. Записать state-заметку, если есть что (открытые вопросы, неочевидные
   доменные решения):
   `../entrypoint/state/projects/<project-slug>/project/<kind>/<slug>.md`;
   для capability — `…/project/capability/<surface>/<slug>.md`.
10. Если завели запись в `integration` с `target: sibling-project` —
    напомнить, что ребро межпроектного стыка сводится в
    `docs/projects/project-map.md`.
11. Предложить логичный следующий шаг по `phases.md`.

### Пример раунда (user, после фундамента)

Скилл предлагает четыре вопроса разом:

- **context** — Other (свободно: «где user живёт, под каким
  давлением»).
- **jobs** — Other (jobs-to-be-done в её языке, списком).
- **pains** — Other (наблюдаемые боли).
- **success vs vision.success** — две опции: «совпадает с vision.success»
  / «отличается, вот как» (Other).

## B. Сырьё

**Сигнал**: args = `<project-slug>` + свободный текст / транскрипт
интервью с бизнесом / заметки / письмо клиента.

### Шаги

1. Прочитать материал внимательно.
2. Извлечь кандидатов по слоям. **Не** угадывать значения доменных
   полей — только то, что **прямо названо** в материале:
   - user — кто упомянут как «пользователь / клиент / адресат»;
   - surface — где «работаем / пользуемся / на телефоне / в админке»
     (поверхность — ось; capability привязывается к ней);
   - capability — что «продукт / сервис / решение умеет/будет уметь»,
     **с привязкой к поверхности**: каждый кандидат идёт в файл своей
     поверхности `capability/<surface>.md`. Если поверхность из материала
     неясна — пометить кандидата «поверхность уточнить»;
   - integration — какие внешние «системы / провайдеры / партнёры»; если
     упомянут **другой продукт того же бизнеса** — это `target:
     sibling-project` (ребро в `project-map.md`);
   - constraint — какие «законы / договоры / обязательства»;
   - boundary — что «не делаем / не наш скоуп / отдаём наружу»;
   - market — кто упомянут как «конкурент / аналог / альтернатива».
3. Через чат показать план (capability — под поверхностями):

   ```
   Из материала вижу:
     user: nurse-partner, doctor (кандидаты)
     surface: web-partner, tg-bot
     capability:
       web-partner: send-referral, check-status
       tg-bot:      check-status (отдельное воплощение в боте)
     integration: clinic-mis (МИС партнёра, external);
                  loyalty-app (соседний продукт → sibling-project)
     boundary: no-insurance (явно сказано «страховку не считаем»)
   Так?
   ```

4. Раунд `AskUserQuestion` — подтвердить план / поправить через Other.
5. По подтверждению — завести **stub'ы** в файлах (минимум `slug + name
   + description + status=draft`); создать state-заметки с открытыми
   вопросами «извлечено из сырья — уточнить <что>».
6. Через `AskUserQuestion` — выбрать, какую сущность углубить первой
   (предложение по логике фаз).
7. Перейти в режим C на выбранной. Повторить для остальных.

### Границы режима B

- Извлечённое — кандидаты до подтверждения аналитика, а не
  зафиксированные записи.
- По сырью заполняются только `name` и `description`, максимально близко
  к языку аналитика или клиента; `jobs`, `pains`, `value`, `payload`,
  `source` добываются вопросами в режиме C, потому что догадка по сырью
  легла бы в артефакт как факт.
- Кандидат появляется, только если он прямо назван в материале; «обычно
  такое бывает» — не основание.
- Research-рой — отдельное решение аналитика; режим B его не запускает.

## C. Углубление

**Сигнал**: args = `<project-slug> <kind>:<slug>` существующей записи,
либо аналитик выбрал из сводки.

### Шаги

1. Прочитать строку из файла данных (для vision — `vision.md` целиком):
   - 6 плоских kind → `docs/projects/<project-slug>/<kind>.md`;
   - capability → `docs/projects/<project-slug>/capability/<surface>.md`
     (поверхность из аргумента `capability:<surface>:<slug>` или пикером).
2. Прочитать state-заметку, если есть:
   `../entrypoint/state/projects/<project-slug>/project/<kind>/<slug>.md`;
   для capability — `…/project/capability/<surface>/<slug>.md`.
3. Прочитать соседей семантически в пределах проекта: для `capability`
   — какие user упомянуты в её файле поверхности, есть ли они; для
   `surface` — какие user её обслуживают, есть ли у неё файл
   `capability/<surface>.md`; для `integration` — на какие поверхности
   реестра она ссылается (`surface`), не повис ли `sibling-project`,
   какие constraint могли бы быть применимы.
4. Применить секции формы `docs/projects/_template/project/<kind>.md`
   (для capability — `capability.md`) к строке. Найти:
   - пустые обязательные слоты (для integration — `surface`, `target`,
     и `sibling-project` при `target: sibling-project`);
   - подозрения по anti-patterns (capability похожа на фичу, boundary
     похож на backlog, constraint без source, соседний продукт как
     `target: external` вместо `sibling-project`);
   - семантические тупики (surface без user, market без sources,
     capability в файле поверхности вне реестра).
5. Раунд `AskUserQuestion` (до 4 вопросов) — точечно по найденному:
   - дыры — заполняем через Other;
   - anti-pattern-подозрения — опции «да, anti-pattern» / «нет, вот
     почему» (через Other);
   - семантические тупики — опции «связать с <варианты>» / «оставить
     как есть, потому что <Other>».
6. Применить ответы: правка строки, обновление state-заметки.
7. После раунда — повторно прогнать чек-лист `draft-stable.md`.
   Если все 5 ✅ — предложить повышение в stable.
8. Если осталась хотя бы одна дыра или подозрение — следующий раунд.

### Когда переходить от C к завершению

- Все 5 пунктов чек-листа ✅ → предложить stable, по подтверждению
  поменять status.
- Остался `**blocker**`-вопрос, на который аналитик сейчас ответить не
  может → зафиксировать в state-заметке, оставить `status: draft`,
  выйти из углубления этой сущности; предложить другую или сводку.

## Стиль вопросов

### Когда давать опции

| ситуация | формат |
|---|---|
| anti-pattern из `Что <kind> НЕ` | две опции: «соответствует anti-pattern» / «не соответствует» (объяснить почему через Other) |
| enum поле (`surface.type`, `integration.direction`, `integration.owner`, `integration.target`, `constraint.kind`) | по одной опции на каждое значение enum |
| тест-критерий из `Тест-критерий` | опции из примеров ✅/❌, аналитик соотносит свой случай |
| выбор существующего slug соседа | по опции на каждый существующий + «нужен новый» (Other) |
| поверхность для capability / `integration.surface` | по опции на каждую поверхность реестра `surface.md` (по именам) + «нужна новая поверхность» |
| `integration.sibling-project` (при `target: sibling-project`) | по опции на каждый существующий проект `docs/projects/<slug>/` (кроме текущего и `_template`) + «нужен новый проект» |
| перепрыгивание фазы | две-три опции «потому что X / Y / Other» |
| запуск research | «5 агентов» / «10 агентов» / «15 агентов» / «не запускать сейчас» |
| promotion кандидата из research в артефакт | «принять как `<kind>:<slug>`» / «отбросить» / «доработать через Other» |

### Когда не давать опции, только Other

| поле | почему |
|---|---|
| `name` | человекочитаемое имя — формулировка аналитика |
| `description` | смысл записи — слова аналитика |
| `value`, `jobs`, `pains`, `success` у user | доменная семантика, не угадывать |
| `why` у boundary | продуктовое решение в словах аналитика |
| `payload` у integration | бизнес-контракт, формулирует аналитик |
| `source` у constraint | конкретный документ, ищет аналитик |

`slug` новой записи не спрашивается ни опцией, ни через Other: скилл
выводит его из `name` (`.claude/rules/naming.md`).

### Чего избегать

- Образцов значений от себя («может быть, value такой?») и «правильных»
  формулировок из md в роли готовых опций: примеры в md иллюстрируют
  канон, а не предлагают варианты для текущего проекта, и такая опция
  подменяет формулировку аналитика.
- Больше 4 вопросов в одном `AskUserQuestion` — остальное следующим
  раундом.
- Закрытия сессии без чек-листа `draft-stable.md` хотя бы по одной
  правленой сущности.

## Stub-сущности

Если копаемая сущность ссылается семантически на ещё не существующий
slug (например, capability упомянула user, которой ещё нет):

1. В соответствующем файле проекта — новая строка: `slug + name +
   description + status=draft`, остальные ячейки `—`. Stub-capability
   заводится **в файле своей поверхности** `capability/<surface>.md`;
   если поверхности ещё нет в реестре — сначала stub-`surface`, потом
   `capability/<surface>.md` (хребет ведёт реестр).
2. В state-заметке — секция `## Открытые вопросы` с записью «Заведён как
   stub в контексте `<откуда сослались>` — докопать в фазе `<phase>`»
   (`../entrypoint/state/projects/<project-slug>/project/<kind>/<stub-slug>.md`;
   для capability — `…/project/capability/<surface>/<stub-slug>.md`).
3. Возврат в исходную сущность, копание продолжается.

## Удаление сущности (каскад)

1. Прочитать продуктовый слой проекта — vision + плоские kind-файлы
   (`surface.md`, `user.md`, `integration.md`, `boundary.md`,
   `constraint.md`, `market.md`) + все файлы папки `capability/` +
   `../entrypoint/state/projects/<project-slug>/project/` — найти все
   семантические упоминания удаляемого slug.
2. Показать каскад: «упоминается в `<files>` — вот что нужно поправить».
3. Через `AskUserQuestion` по каждому месту — опции: «заменить на
   другой slug» / «удалить упоминание» / «оставить как есть».
4. По подтверждению — выполнить все правки одним пакетом.
5. Удалить запись из её файла. Если удаляется **поверхность**
   (`surface`) — её файл возможностей `capability/<surface>.md` и
   ссылки `integration.surface` на неё повисают: показать каскад и решить
   судьбу capability-файла (перенести записи на другую поверхность /
   удалить). Папки `interface/<surface>/`, `screens/<surface>/`,
   `fsd/<surface>/`, `telegram-bot-flow/<surface>/`, `mobile/<surface>/`
   ведут свои скилы — здесь только предупредить, что они осиротеют.
6. Удалить state-заметку
   (`…/project/<kind>/<slug>.md`; для capability —
   `…/project/capability/<surface>/<slug>.md`).
7. Если удалена единственная user — спросить, не пора ли
   пересмотреть vision.
