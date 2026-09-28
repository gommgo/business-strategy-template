# Реестр правил `interface-audit`

У каждого правила — `id`, тяжесть, scope, что проверяет, как проверять, рекомендация и откуда норма: форма
`docs/projects/_template/interface/_template/<kind>.md`, канон слоя `docs/projects/_template/interface/README.md` или
адрес базы знаний скилла дизайна (короткий адрес «ux 02/01 §3.3» — `.claude/skills/design-deep-dive/kb/INDEX.md` §1).
Проверка — чтением файлов по форме, как у всех структурных аудитов шаблона; правило, которое требует суждения, помечено
«чтением» и приводит цитату записи.

Категории:

- **R-SURF** — хребет поверхностей: папка ↔ реестр `surface.md` и род поверхности.
- **R-XSURF** — изоляция поверхностей: ссылка не уходит наружу.
- **R-STRUCT** — структурная целостность: ссылки, перечисления, достижимость.
- **R-MIRROR** — синхронность зеркал ситуации.
- **R-SEM** — семантические подозрения.
- **R-COV** — покрытие и стиль.
- **R-SC** — сценарии.
- **R-IA** — информационная архитектура: зоны как разделы навигации.
- **R-CAP** — покрытие вверх: ситуация и возможность.

UX-слой партиционирован по поверхности: на каждую поверхность реестра `docs/projects/<project-slug>/surface.md` — папка
`docs/projects/<project-slug>/interface/<surface>/` с восемью файлами (`who`, `stage`, `situation`, `scenario`, `zone`,
`block`, `ux-substrate`, `data-items`). Сокращённо `<surface>/<file>.md` —
`docs/projects/<project-slug>/interface/<surface>/<file>.md`.

Правила R-STRUCT, R-MIRROR, R-SEM, R-COV, R-SC, R-IA, R-CAP применяются **в пределах одной поверхности**: ссылочные поля
разрешаются среди записей той же папки. R-SURF и R-XSURF — про границу между поверхностями. Кроме папки поверхности
аудит читает только то, что называют правила: `surface.md` (тип и род), `object.md` и файл возможностей
`capability/<surface>.md` того же проекта (R-STRUCT-009, R-SC-003, R-IA-005), поле `situations` экранов
`screens/<surface>/screens/<slug>/index.md` той же поверхности (R-SEM-006).

Кросс-поверхностная сверка — один бизнес-датум на web и в боте, общий пользователь — и смысл связей с продуктом (тот ли
объект, та ли возможность, сводится ли участник к пользователю) — вне scope, это `/cross-audit`. Правило «один датум,
один slug» (R-COV-007) считается внутри поверхности.

---

## R-SURF (хребет поверхностей)

### R-SURF-001 «папка поверхности вне реестра»

- **severity**: `error`.
- **scope**: подпапки `docs/projects/<project-slug>/interface/` ↔ `surface.md`.
- **проверка**: у каждой подпапки `interface/<X>/` есть строка `slug: X` в реестре — хребет ведёт реестр.
- **рекомендация**: «Завести строку `<X>` в `surface.md` через `/project-deep-dive <project-slug>` или удалить
  осиротевшую папку `interface/<X>/`».

### R-SURF-002 «поверхность реестра без папки interface»

- **severity**: `hint`.
- **scope**: `surface.md` ↔ подпапки `interface/`.
- **проверка**: у каждой строки реестра, кроме `web` рода `landing` и `site`, есть папка `interface/<slug>/`. Отсутствие
  — не ошибка модели, а непокрытая поверхность.
- **рекомендация**: «interface поверхности не начат — завести через `/interface-deep-dive <project-slug> <slug>`, у
  поверхности маршрута приложения — со сценариев хабов; либо это сознательно отложено».

### R-SURF-003 «папка interface у сайта или лендинга»

- **severity**: `error`.
- **scope**: подпапки `interface/` ↔ `surface.md`.
- **проверка**: папка `interface/<X>/` есть у поверхности `type: web` рода `landing` или `site`. У сайта и лендинга на
  месте interface, экранов и FSD-карты стоит слой страницы `site/<surface>/`.
- **норма**: `docs/projects/_template/interface/README.md` (вступление);
  `docs/projects/_template/project/README.md § Связи`.
- **рекомендация**: «Смысл и тексты страницы — в слой страницы (`/design-deep-dive <project-slug> <X>`); если
  поверхность на деле кабинет — род `app` через `/project-deep-dive <project-slug>`; папку разбирает
  `/interface-deep-dive <project-slug> <X>` по подтверждению аналитика».

---

## R-XSURF (изоляция поверхностей)

### R-XSURF-001 «ссылка из одной поверхности в другую»

- **severity**: `error`.
- **scope**: восемь файлов любой папки `<surface>/`.
- **проверка**: slug-значение ссылочного поля не найдено в своей поверхности, но найдено в другой — это пересечение
  границы, а не битая ссылка R-STRUCT-001. Так же — `situation.capabilities` или `scenario.capability`, названные по
  файлу возможностей другой поверхности.
- **рекомендация**: «Поверхности изолированы — завести запись в своей поверхности через
  `/interface-deep-dive <project-slug> <surface> <kind>` или убрать ссылку. Общее между поверхностями сводит
  `/cross-audit`, не межпапочная ссылка».

---

## R-STRUCT (структура)

### R-STRUCT-001 «валидность ссылок»

- **severity**: `error`.
- **scope**: восемь файлов одной папки `<surface>/`.
- **проверка**: каждое slug-значение ссылочного поля существует в соответствующем файле **той же поверхности**:
  - `situation.stage` → `<surface>/stage.md`; `situation.who` → `<surface>/who.md`;
  - `situation.entry-data`, `exit-data` → `<surface>/data-items.md`;
  - `situation.ux-substrate` (зеркало) → `<surface>/ux-substrate.md`; `situation.block` (зеркало) →
    `<surface>/block.md`;
  - `block.zone` → `<surface>/zone.md`; `block.who` → `<surface>/who.md`; `block.ux-substrates` →
    `<surface>/ux-substrate.md`; `block.transition-to-block` → `<surface>/block.md`; `block.transition-from-zone` →
    `<surface>/zone.md`;
  - `zone.parent-zone` → `<surface>/zone.md`; `ux-substrate.situation` → `<surface>/situation.md`.

  Ссылки сценария — R-SC-003; объекты глоссария — R-STRUCT-009.
- **рекомендация**: «Завести stub через `/interface-deep-dive <project-slug> <surface> <kind>:<missing-slug>` или
  заменить ссылку на существующий slug этой поверхности».

### R-STRUCT-002 «цикл parent-zone»

- **severity**: `error`.
- **scope**: `<surface>/zone.md`.
- **проверка**: путь по `parent-zone` вверх от каждой зоны возвращается к ней — цикл.
- **рекомендация**: «Пересмотреть иерархию через `/interface-deep-dive <project-slug> <surface> zone:<slug>`: у одной из
  зон цикла `parent-zone` — `—` или другой корень».

### R-STRUCT-003 «дубликат slug»

- **severity**: `error`.
- **scope**: каждый файл поверхности; у `scenario.md` — заголовки секций `## <slug>`.
- **проверка**: внутри файла все `slug` уникальны.
- **рекомендация**: «Переименовать дубликат через `/interface-deep-dive <project-slug> <surface>` (каскадно правит
  ссылки)».

### R-STRUCT-004 «явный переход внутри одной зоны»

- **severity**: `error`.
- **scope**: `<surface>/block.md`.
- **проверка**: цель `transition-to-block` лежит в той же `zone`, что исходный блок: внутри зоны блоки достижимы неявно,
  явно пишутся только межзонные переходы.
- **рекомендация**: «Удалить явный переход внутри зоны через
  `/interface-deep-dive <project-slug> <surface> block:<slug>`».

### R-STRUCT-005 «блок без `ux-substrates`»

- **severity**: `error`.
- **scope**: `<surface>/block.md`.
- **проверка**: `block.ux-substrates` непуст и не `—`.
- **рекомендация**: «Завести субстраты через `/interface-deep-dive <project-slug> <surface> ux-substrate` и связать с
  блоком, либо удалить блок».

### R-STRUCT-006 «блок без `who`»

- **severity**: `error`.
- **scope**: `<surface>/block.md`.
- **проверка**: `block.who` непуст и не `—`.
- **рекомендация**: «Дополнить `block.who` через `/interface-deep-dive <project-slug> <surface> block:<slug>`;
  универсальный блок — `[any]`».

### R-STRUCT-007 «status вне перечня»

- **severity**: `error`.
- **scope**: восемь файлов поверхности; у сценария — поле `status` мета-блока.
- **проверка**: `status` ∈ {`draft`, `stable`}.
- **рекомендация**: «Поправить status через `/interface-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-008 «значение вне перечня»

- **severity**: `error`.
- **scope**: поля-перечисления поверхности.
- **проверка**:

  | поле | допустимо |
  |---|---|
  | `ux-substrate.type` | `команда`, `ввод`, `выбор`, `инфо`, `список` |
  | `situation.frequency`, `scenario.frequency` | `hours-daily`, `daily`, `weekly`, `monthly`, `rare`, `once` |
  | `situation.refusals` | ключи из перечня колонки формы `situation.md` (группы «отказ» и «доступ и правила» словаря состояний экрана) или `—` |
  | `scenario.expertise` | `novice`, `intermediate`, `expert` |
  | `scenario.reversibility` | `undo`, `soft-delete`, `confirm`, `irreversible` |
  | `scenario.context-needed`, `block.entrypoint` | `true`, `false` |
  | `zone.order` | число или `—` |
  | исход «Конечных состояний» | `success`, `rejected`, `deferred`, `partial`, `cancelled` |

- **норма**: колонки форм `situation.md`, `scenario.md`, `zone.md`, `block.md`, `ux-substrate.md`; словарь состояний —
  `docs/projects/_template/screens/README.md § Состояния экрана`.
- **рекомендация**: «Выбрать значение из перечня через `/interface-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-009 «объект глоссария в пустоту»

- **severity**: `error`.
- **scope**: `<surface>/zone.md`, `<surface>/data-items.md` ↔ `object.md` проекта.
- **проверка**: `zone.object` (кроме `—`) называет объект таблицы «Объекты» `object.md`; `data-items.object` (кроме `—`)
  — объект (`<object>`) или атрибут (`<object>.<атрибут>`) таблицы «Атрибуты». Через `data-items.object` резолвится узел
  `data:` деревьев экранов. Существование проверяется здесь; тот ли это объект по смыслу — сверяет `/cross-audit`.
- **норма**: `zone.md`, `data-items.md` (колонка `object`, критерий 6); README interface § Связи и выводимые поля.
- **рекомендация**: «Завести объект или атрибут через `/project-deep-dive <project-slug> object` или поправить ссылку
  через `/interface-deep-dive <project-slug> <surface> <kind>:<slug>`».

### R-STRUCT-010 «блок недостижим от стартового»

- **severity**: `error` (stable-блок); у поверхности с блоками нет ни одного стартового — `error`.
- **scope**: `<surface>/block.md`, `<surface>/zone.md`.
- **проверка**: обход от блоков с `entrypoint: true`. Из достигнутого блока достижимы: блоки его зоны; цели его
  `transition-to-block`; блоки, у которых его зона стоит в `transition-from-zone`; блоки зон навигации — корневых зон с
  `order` и их дочерних зон с `order` (пункты навигации каркаса). Stable-блок, до которого обход не дошёл, — ошибка.
  Недостижимость draft-блока — предупреждение R-SEM-005.
- **норма**: README interface § Связи и выводимые поля («глобальный entrypoint»); `block.md`, критерий 1; `zone.md`
  (`order`); ux 05/02 §9.
- **рекомендация**: «Дать блоку вход: стартовый блок, входящая зона, переход из другого блока или зона в навигации —
  через `/interface-deep-dive <project-slug> <surface> block:<slug>`».

---

## R-MIRROR (зеркала)

### R-MIRROR-001 «situation.ux-substrate ↔ ux-substrate.situation»

- **severity**: `error`.
- **scope**: `<surface>/situation.md` ↔ `<surface>/ux-substrate.md`.
- **проверка**: у каждой ситуации S набор `S.ux-substrate` равен `{u.slug | u.situation == S.slug}`.
- **рекомендация**: «Пересчитать зеркало через `/interface-deep-dive <project-slug> <surface> situation:<slug>` — скилл
  синхронизирует автоматически».

### R-MIRROR-002 «situation.block ↔ join через субстраты»

- **severity**: `error`.
- **scope**: `<surface>/situation.md` ↔ `<surface>/block.md` через `<surface>/ux-substrate.md`.
- **проверка**: у каждой ситуации S набор `S.block` равен `{b.slug | b.ux-substrates ∩ S.ux-substrate ≠ ∅}`.
- **рекомендация**: «Пересчитать зеркало через `/interface-deep-dive <project-slug> <surface> situation:<slug>`».

---

## R-SEM (семантика)

### R-SEM-001 «`goal` похож на предусловие»

- **severity**: `warning`.
- **scope**: `<surface>/situation.md`.
- **проверка**: `goal` содержит маркеры предусловия: «чтобы продолжить», «чтобы войти», «чтобы получить доступ»,
  «авторизоваться чтобы», «чтобы перейти к», «чтобы открыть».
- **рекомендация**: «Цель объясняет смысл шага в объемлющей деятельности, а не «чтобы пройти дальше» — уточнить через
  `/interface-deep-dive <project-slug> <surface> situation:<slug>`».

### R-SEM-002 «`using-what` содержит облик»

- **severity**: `warning`.
- **scope**: `<surface>/situation.md`.
- **проверка**: `using-what` содержит маркеры облика: «primary», «secondary», размеры «md», «sm», «lg», «xl», «иконк»,
  «размер», «цвет», «hex», «#» с цифрами, имена компонентов `ui:*`.
- **норма**: `situation.md`, критерий 4; README interface, anti-pattern «облик в артефактах».
- **рекомендация**: «`using-what` — бизнес-средство, а не его вид: облика в interface нет, он живёт в слое дизайна
  `design/`. Уточнить через `/interface-deep-dive <project-slug> <surface> situation:<slug>`».

### R-SEM-003 «пустой обязательный слот»

- **severity**: `warning` (draft) / `error` (stable).
- **scope**: восемь файлов поверхности; обязательные слоты по kind —
  `.claude/skills/interface-deep-dive/references/field-checklists.md`.
- **проверка**: каждый обязательный слот непуст и не `—`. Особо: у ситуации при stable — `frequency`; у зоны — `order` и
  `object`, у данных — `object`: у этих трёх полей прочерк — решение и считается заполненным, пуста только ячейка без
  значения. Разделы сценария — R-SC-001, отказы ситуации экрана — R-SEM-006.
- **рекомендация**: «Заполнить через `/interface-deep-dive <project-slug> <surface> <kind>:<slug>`; у stable
  обязательные слоты не пусты».

### R-SEM-004 «`description` совпадает с `name`»

- **severity**: `warning`.
- **scope**: восемь файлов поверхности.
- **проверка**: `description` после обрезки пробелов и приведения регистра совпадает с `name` или целиком в нём
  содержится.
- **рекомендация**: «`description` поясняет что и зачем, а не повторяет `name`».

### R-SEM-005 «черновой блок без входа»

- **severity**: `warning`.
- **scope**: `<surface>/block.md`, draft-блоки.
- **проверка**: `entrypoint = false`, блок не цель ни одного `transition-to-block`, `transition-from-zone = —`, его зона
  не в навигации (`order: —`) и в ней нет других блоков — входа нет. У stable-блока недостижимость — ошибка
  R-STRUCT-010.
- **рекомендация**: «Сделать блок стартовым, добавить входящую зону или переход из другого блока через
  `/interface-deep-dive <project-slug> <surface> block:<slug>`».

### R-SEM-006 «у ситуации экрана не названы отказы»

- **severity**: `warning` (stable).
- **scope**: `<surface>/situation.md` ↔ поле `situations` экранов `screens/<surface>/screens/<slug>/index.md` той же
  поверхности.
- **проверка**: stable-ситуация стоит в `situations` хотя бы одного экрана, а ячейка `refusals` пуста — ни ключей
  отказов, ни `—` «отказов нет». Экранов у поверхности нет — правило не применяется.
- **норма**: `situation.md`, критерий 7, колонка `refusals`; отказы ситуаций входят в обязательный набор состояний
  экрана — `docs/projects/_template/screens/README.md § Обязательный набор`.
- **рекомендация**: «Назвать отказы шага (ключи состояний) или записать «отказов нет» через
  `/interface-deep-dive <project-slug> <surface> situation:<slug>`».

---

## R-COV (coverage и стиль)

### R-COV-001 «who без покрытия»

- **severity**: `hint`.
- **scope**: `<surface>/who.md`.
- **проверка**: у каждого участника есть ситуация с `situation.who` — он.
- **рекомендация**: «Завести ситуацию-инициатор через `/interface-deep-dive <project-slug> <surface> situation` или
  удалить участника (каскадно)».

### R-COV-002 «stage без покрытия»

- **severity**: `hint`.
- **scope**: `<surface>/stage.md`.
- **проверка**: у каждого этапа есть ситуация с `situation.stage` — он.
- **рекомендация**: «Завести ситуацию на этапе или удалить этап».

### R-COV-003 «zone без блоков»

- **severity**: `hint`.
- **scope**: `<surface>/zone.md`.
- **проверка**: у каждой зоны есть блок с `block.zone` — она.
- **рекомендация**: «Завести блок в зоне через `/interface-deep-dive <project-slug> <surface> block` или удалить зону».

### R-COV-004 «stable ссылается на draft»

- **severity**: `hint`.
- **scope**: все ссылочные поля поверхности, шаги и участники сценариев.
- **проверка**: запись `status: stable` ссылается на запись `status: draft`.
- **рекомендация**: «Не блокирует stable, но draft-соседа стоит докопать:
  `/interface-deep-dive <project-slug> <surface> <kind>:<slug-соседа>`».

### R-COV-005 «короткое `description`»

- **severity**: `hint`.
- **scope**: восемь файлов поверхности.
- **проверка**: `description` короче 10 символов.
- **рекомендация**: «`description` слишком короткое для смысловой ясности — уточнить».

### R-COV-006 «одинокий субстрат»

- **severity**: `hint`.
- **scope**: `<surface>/ux-substrate.md`.
- **проверка**: у ситуации субстрата U зеркало `situation.block` пусто — субстрат не показан ни одним блоком.
- **рекомендация**: «Собрать субстрат в блок через `/interface-deep-dive <project-slug> <surface> block`».

### R-COV-007 «один датум — один slug (в пределах поверхности)»

- **severity**: `hint`.
- **scope**: `<surface>/data-items.md`.
- **проверка**: один бизнес-датум не заведён двумя slug'ами в одной папке; признак — одинаковые `name` или один
  `object`.
- **рекомендация**: «Слить дубль через `/interface-deep-dive <project-slug> <surface> data-items:<slug>`. Один датум на
  двух поверхностях — две законные записи, их сверяет `/cross-audit`».

---

## R-SC (сценарии)

Сценарий — секция `## <slug>` файла `<surface>/scenario.md`: мета-блок YAML и подразделы. Форма и проверки —
`docs/projects/_template/interface/_template/scenario.md` (`§ Форма секции сценария`, `§ Проверки`).

### R-SC-001 «раздел сценария пуст при stable»

- **severity**: `error` (stable); шаг без строки «Ошибок» — `warning`.
- **scope**: `<surface>/scenario.md`.
- **проверка**: у stable-сценария заполнены обязательные поля мета-блока (`name`, `capability`, `who`, `goal`,
  `frequency`, `expertise`, `trigger`, `reversibility`, `status`) и непусты подразделы «Happy path», «Ветвления»,
  «Ошибки», «Конечные состояния», «Что меняется», «Приёмка». Шаг основного пути, у которого в «Ошибках» нет ни одной
  строки, — `warning`: ошибки описывают на каждом шаге.
- **норма**: `scenario.md`, критерии 3, 5, 8, `§ Проверки`; ux 05/02 §1.4.
- **рекомендация**: «Дописать раздел через `/interface-deep-dive <project-slug> <surface> scenario:<slug>`: сценарий,
  остановленный на основном пути, не описан».

### R-SC-002 «исход без «что дальше»»

- **severity**: `error`.
- **scope**: `<surface>/scenario.md`, «Конечные состояния».
- **проверка**: в таблице нет строки одного из пяти исходов (`success`, `rejected`, `deferred`, `partial`, `cancelled`)
  или у исхода в колонке «что дальше» нет ни двух-трёх действий, ни «не применимо: причина».
- **норма**: `scenario.md`, критерий 6; ux 05/02 §5.4.
- **рекомендация**: «Назвать, что человек может сделать после исхода, или записать, почему исход у сценария невозможен».

### R-SC-003 «шаг или ссылка сценария в пустоту»

- **severity**: `error`.
- **scope**: `<surface>/scenario.md` ↔ файлы поверхности, файл возможностей `capability/<surface>.md`, `object.md`.
- **проверка**:
  - `capability` — возможность файла **этой** поверхности (возможность другой поверхности — R-XSURF-001);
  - `who` — участники `<surface>/who.md`;
  - шаг «Happy path» — ситуация `<surface>/situation.md`;
  - строка «Ветвлений» — с условием и целью: ситуацией поверхности или номером существующего шага;
  - ключ в «Ошибках» — ключ словаря состояний экрана (`docs/projects/_template/screens/README.md § Состояния экрана`);
  - «Что меняется» — объект и статус из колонки `statuses` `object.md` (`<object>.<status>`).
- **норма**: `scenario.md`, критерии 1, 4, форма секции.
- **рекомендация**: «Завести stub-ситуацию или поправить ссылку через
  `/interface-deep-dive <project-slug> <surface> scenario:<slug>`; объект и возможность — через
  `/project-deep-dive <project-slug>`».

### R-SC-004 «два участника без «Чей ход»»

- **severity**: `warning`.
- **scope**: `<surface>/scenario.md`.
- **проверка**: в `who` два и больше участника, а подраздела «Чей ход» нет или он пуст.
- **норма**: `scenario.md`, критерий 7; ux 05/02 §8.
- **рекомендация**: «Описать для каждого шага, у кого объект, что видят остальные и что при бездействии».

### R-SC-005 «цель словами системы»

- **severity**: `hint`.
- **scope**: `<surface>/scenario.md`, поле `goal`.
- **проверка**: чтением — цель названа словами интерфейса или системы («заполнить форму», «нажать», «открыть экран»,
  «система сохраняет»), а не тем, что человек хочет получить.
- **норма**: `scenario.md`, критерий 2; ux 05/02 §1.4.
- **рекомендация**: «Сформулировать цель словами пользователя: «пациент попал на исследование», а не «заполнить форму
  направления»».

---

## R-IA (информационная архитектура)

Зона — раздел информационной архитектуры поверхности: корневые зоны с `order` — пункты навигации уровня 1, их дочерние
зоны с `order` — уровня 2 (README interface § Информационная архитектура).

### R-IA-001 «дерево зон глубже нормы»

- **severity**: `warning` / `error`.
- **scope**: `<surface>/zone.md`.
- **проверка**: глубина дерева по `parent-zone` (корневая зона — уровень 1) против таблицы «Сколько уровней» ux 02/01
  §3.3: глубже рабочего потолка приложения — `warning`, глубже предела каркаса — `error`.
- **норма**: `zone.md`, критерий 8; ux 02/01 §3.3.
- **рекомендация**: «Поднять уровни: вкладки объекта — внутри экрана, длинный список — группировать, а не углублять (ux
  02/01 §3.4)».

### R-IA-002 «корневых разделов больше нормы»

- **severity**: `warning`.
- **scope**: `<surface>/zone.md`.
- **проверка**: число корневых зон в навигации (`order` задан) попадает в строку «IA не доделана» таблицы ux 02/01 §3.2.
- **норма**: `zone.md`, критерий 8; ux 02/01 §3.2.
- **рекомендация**: «Найти разделы, которые на деле — фильтры или представления одного раздела, и свернуть их».

### R-IA-003 «имя-свалка»

- **severity**: `warning`.
- **scope**: `<surface>/zone.md`, `name`.
- **проверка**: имя зоны — из списка свалок формы: «Разное», «Прочее», «Другое», «Ещё», «More», «Hub», «Insights»,
  «Workspace».
- **норма**: `zone.md`, критерий 5; ux 02/01 §5.
- **рекомендация**: «Разложить содержимое по разделам с именами, которые человек узнает».

### R-IA-004 «раздел не существительное или категории пересекаются»

- **severity**: `warning`.
- **scope**: `<surface>/zone.md`.
- **проверка**: чтением — имя раздела не существительное и не объект; у соседних зон одного родителя категории
  пересекаются: одна вещь могла бы жить в обеих.
- **норма**: `zone.md`, критерий 5; ux 02/01 §5.
- **рекомендация**: «Переименовать раздел существительным и развести категории соседей».

### R-IA-005 «корневая зона без объекта и без хаба»

- **severity**: `hint`.
- **scope**: `<surface>/zone.md`, `<surface>/block.md`, `<surface>/situation.md` + файл возможностей поверхности.
- **проверка**: корневая зона в навигации с `object: —`, и ни одна ситуация её блоков не реализует возможность с
  `priority: hub`.
- **норма**: `zone.md`, критерий 7; ux 01/03 §15.
- **рекомендация**: «Проверить, зачем раздел: построить его вокруг объекта или хаба либо свернуть в соседний».

---

## R-CAP (покрытие вверх)

### R-CAP-001 «stable-ситуация без возможности»

- **severity**: `hint`.
- **scope**: `<surface>/situation.md`.
- **проверка**: у stable-ситуации `capabilities` = `—`. Либо возможности не хватает в реестре поверхности, либо шаг
  лишний; служебный шаг системного актора бывает без возможности — это решение аналитика.
- **норма**: `docs/projects/_template/project/capability.md § Покрытие`. Обратное направление — возможность без ситуаций
  и хаб без сценария — проверяет `/project-audit`.
- **рекомендация**: «Связать ситуацию с возможностью поверхности или завести возможность через
  `/project-deep-dive <project-slug> capability:<surface>`».
