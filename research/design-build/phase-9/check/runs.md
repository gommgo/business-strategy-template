# Проверка по сценариям (CT) — ответы агента

Рабочая сессия `design-deep-dive` на копиях форка. Утилиты — Python окружения
`~/.cache/design-deep-dive/venv/bin/python`, путь утилиты — от `.claude/skills/design-deep-dive/scripts/`. Демо-проект
указан утилитам ключом `--repo <папка>` (`scripts/README.md § project`: «Корень данных — ключ `--repo DIR`, переменная
`DDD_REPO` или репозиторий скилла»). Выход `design_audit` — в scratchpad сессии через `--out` (по умолчанию он пишет в
`$DDD_HOME/out/project/design_audit/<slug>/`). В шаблоне и демо-проектах ничего не правилось: писали только команды
`build`.

## 1. Лендинг — вход холста для вайрфрейма (`<S1>`)

### Путь

- `SKILL.md § Что где читать`: `references/phases.md` — «контракт каждого этапа»; `§ Утилиты и запасной путь`: «Какую
  утилиту зовёт этап — строка «Проверка» его контракта в `references/phases.md`».
- `phases.md § 1. Маршруты`, таблица «Лендинг и многостраничник», строка 13: «`canvas-input` → `wireframe` | план
  `approved`, copy deck `assumed` или `checked`». План `home` — `approved`, тексты copy deck — `assumed` (два — `draft`):
  вход готов.
- `phases.md § 6. Холст`, контракт `canvas-input`: «Вход собирает `canvas_input build <slug> <surface> --stage <вид
  входа> [--page ID,… | --screen SLUG,…]` партией… без ключа — все единицы поверхности»; «Проверка входа —
  `canvas_input check <slug> <surface> [--stage …]`… `design_audit check` — вход свежий и руками не правлен»; «с
  `error` этап холста не публикуется». Контракт `wireframe`: «Вход холста этапа `wireframe` без `error` для партии…
  предупреждения входа — доклад заказчику».
- `claude-design.md § 6. Вход холста` — раскладка входа и таблица «держит этап — `error` / доклад — `warning`».
- `scripts/README.md § project` — вызов и `--repo`; `canvas_input.py --help`, `design_audit.py --help`.
- Для чтения находок аудита: `.claude/skills/design-audit/SKILL.md § Уровни тяжести`,
  `.claude/skills/design-audit/references/rules.md` (R-COV-002, R-REF-003), `docs/projects/_template/site/README.md §
  Тексты` («Ворота»), `§ Связь copy deck с планом`.

Этап — `canvas-input` (вид входа `wireframe`), дальше — `wireframe`.

### Команды

```
python project/canvas_input.py build otves-remont-nn promo --stage wireframe --repo <S1>      # код 0
python project/canvas_input.py check otves-remont-nn promo --repo <S1>                        # код 0
python project/canvas_input.py check otves-remont-nn promo --repo <S1> --json                 # код 0
python project/design_audit.py check otves-remont-nn promo --repo <S1> --out <scratchpad>     # код 1
python project/ds_build.py check otves-remont-nn --repo <S1>                                  # код 1 (сверка, находка 5)
```

### Результат

**Сборка.** Партия — `home` («все единицы поверхности»). Записаны `design/promo/input/`: `INPUT.md`, `brief.yaml`,
`facts.md`, `ACCEPTANCE.md` (группы A–H, блоки I–L, V), `pages/home/page.yaml`, `copy.md`, `assets.md` — раскладка
совпадает с `claude-design.md § 6`. `INPUT.md`: `stage: wireframe`, `units: [home]`, `built_by: canvas_input`, итог
«0 error · 4 warning · 6 hint — вход без ошибок: этап можно публиковать». «Going with» пуст: у каждого поля есть
источник.

**Проверка входа** (`canvas_input check`, партия из `units`): **0 error · 4 warning · 6 hint**, код 0; R-FRESH-002/003
нет — вход свежий и руками не правлен.

| тяжесть | правило | что | путь |
|---|---|---|---|
| warning | R-MAT-003 | факты в статусе `draft`, а вход берёт `confirmed` | `facts.yaml` |
| warning | R-COV-002 | 52 текстовых слота утверждённого плана без текста (`announcement-bar/text`, `header/cta-label`, `hero/cta-secondary-label`, `offer/*` …) — на артборде `[PLACEHOLDER]` | `site/promo/copy/home.yaml` |
| warning | R-MAT-003 | 2 текста в `draft`: `lead-form/consent`, `footer/legal` | там же |
| warning | R-REF-003 | 8 слотов copy deck вне плана (`hero/proof-source`, `testimonials/author`, `…/frame`, `…/quote`, `guarantee/people`, `pricing/promo` …) — идут в `copy.md` без места в `page.yaml` | там же |
| hint | R-DEBT-002 | 10 демо-фактов во входе | `facts.yaml` |
| hint | R-COV-001 ×5 | страницы брифа без плана: `consent`, `guide`, `not-found`, `privacy`, `spasibo` — во вход не идут | `site/promo/plans` |

**Структурный прогон** (`design_audit check`, тот же переход этапа): **28 error · 17 warning · 10 hint**, код 1, этап
поверхности `input_stage: wireframe`. Ошибки: R-REF-001 ×13 — ссылки в пустоту (`facts_ref`, `meaning_ref`,
`voice_ref`, `hierarchy_ref` copy deck; `refs.facts`, `refs.treatment` плана; `proof_ref` смысла; `meaning.proof_ref`,
`proof.facts_ref` брифа; `meaning_ref` иерархий; `brand.facts_ref`, `brand.meaning_ref` голоса); R-REF-003 ×14 — стык copy deck с планом (слоты
вне плана, `group faq-1` против `qa-1`, `slot_type section-title` против `form-title` и др.); R-COV-002 ×1 — «53
текстовых слота… без текста (страница передана в дизайн: в партии входа холста)». Предупреждения: R-COV-005 ×5 (нет
компонентов `Checkbox`, `Link`; не нарисованы состояния `Button`, `Field`), R-STRUCT-003 ×5, R-MAT-001 ×2 (план
`approved` при брифе и смысле `proposed`; ДС `approved` на открытом), R-MAT-003 ×2, R-COV-007, R-COV-008, R-STRUCT-002.

**Заказчику.** Вход вайрфрейма главной собран и проверен: ошибок входа нет, вайрфрейм можно публиковать после блока
вопросов холста (`claude-design.md § Вопросы до макета`). Доклад, решает заказчик: факты не подтверждены (на вайрфрейме
допустимо), 52 слота без текста выйдут заглушками, согласие в форме и юридическая строка подвала — черновики (юрист
заказчика), 8 текстов не имеют места в плане, пять страниц брифа ещё без плана, факты демо. Отдельно — дефекты файлов из
структурного прогона (не решение заказчика, их исправляют): стык copy deck с планом и слоты без текста — этап `copy`
(`/design-deep-dive otves-remont-nn promo copy`, каркас недостающих — `copydeck.py skeleton`), ссылки в пустоту — этапы
`meaning`, `brief`, `page-plan` и `copy`; после правок — пересборка входа. Исполнитель — `/design-deep-dive`.

### Находки о текстах

1. **R-COV-002 на вайрфрейме: `warning` у входа, `error` у аудита — на одних данных.** `claude-design.md § 6`, таблица
   проверки входа: `error` — «на макете у единиц партии: … текстовый слот плана без текста»; справка `canvas_input`:
   «R-COV-002 warning текстовый слот плана без текста этапа на вайрфрейме». Реестр `design-audit/references/rules.md`,
   R-COV-002: «`error` — страница передана в дизайн (она в партии действующего входа холста — поле `units`…)»; так же
   `site/README.md § Тексты`: «черновик по слотам — после утверждённого плана и до вайрфрейма». Сам `claude-design.md §
   6` («Проверка входа») требует: «у каждого текстового слота утверждённого плана — текст нужного этапу статуса,
   `[PLACEHOLDER]` — только из «Нет»», а `INPUT.md` пишет о 52 слотах без текста: «на артборде — [PLACEHOLDER]». Итог:
   сама сборка входа вайрфрейма превращает доклад в ошибку аудита.
2. **R-REF-003: одна находка — две тяжести.** Справка `canvas_input`: «R-REF-003 warning секция или слот copy deck вне
   плана страницы»; реестр: «R-REF-003 «стык copy deck с планом» · `error`». `canvas_input` — 1 warning, `design_audit`
   — 14 error. В таблице проверки входа `claude-design.md § 6` правила нет вовсе.
3. **«0 error» во входе и «28 error» в прогоне на одном переходе.** Публикацию держит итог манифеста («Итог — в
   манифесте: с `error` этап не публикуется», `claude-design.md § 6`); в строке «Проверка» контракта `canvas-input`
   `design_audit check` назван только ради свежести («вход свежий и руками не правлен»), а `§ Принципы всех этапов` велит
   гонять на переходе весь структурный прогон и называет такие `error` «дефектом», который «исправляют». Ждёт ли
   публикация вайрфрейма исправления 28 ошибок, из которых R-COV-002 — прямо о странице партии, тексты не говорят.
4. **Счёт слотов без текста расходится:** `canvas_input` — 52, `design_audit` — 53 на одном состоянии (в голове списка
   аудита есть `hero/alt` и `offer/title`, которых нет в показанных позициях входа).
5. **ДС без токенов DTCG прогон не видит.** В `<S1>` нет `design/system.tokens.json` и `system.tokens.css`, есть только
   `tokens.json` и README артефакта; `ds_build check` — error R-STRUCT-006 «нет токенов DTCG, а производные ДС есть»,
   а `design_audit` `ds_build` не вызвал и заметки «не проверялось» не дал (подробно — задача 4, находка 1). На
   вайрфрейм это не влияет: облика на нём нет.

## 2. Кабинет — экраны и вход холста для макета (`<S2>`)

### Путь

- `SKILL.md § Этапы`, «Кабинет»: «Дизайн входит в маршрут дважды — после сценариев и после stable-экранов; полноту
  второго входа проверяет блок PRE».
- `phases.md § 1. Маршруты`, таблица «SaaS и кабинет»: строка 12 `screens` (ведёт `/screen-deep-dive`), строка 16
  «`canvas-input` → `mockup` … | тексты `approved`, покрытие компонентов».
- `phases.md § 4. Слой проекта SaaS`, строка `screens`: «проверка — утилиты `tree`, `states`, `screen_map`
  (`scripts/README.md § project`); `/screen-audit`» — это и привело к трём утилитам экранов; `§ Второй вход дизайна
  кабинета`: «Когда. После stable-экранов и свода `map.md` без расхождений»; блок PRE считает `contract.py check`,
  «`canvas_input check` кабинета показывает их по экранам партии входа».
- `phases.md § 6`, `canvas-input` (сборка `--stage mockup`, «У кабинета в той же проверке — блок PRE (§4) и перед
  макетом покрытие ДС (`ds_coverage`)… тип без компонента ДС — `error`») и `mockup` («С середины… вход `mockup` с
  текстами не `approved` — у кабинета в строках `texts.md` — не публикуется (R-MAT-012 `error`)»).
- `claude-design.md § 6. Вход холста`, абзац «Кабинет» и таблица проверки входа; `scripts/README.md § project` (строки
  `tree`, `states`, `screen_map`, `ds_coverage`, `canvas_input`); `--help` каждой утилиты.

Этапы: проверка готовности второго входа (утилиты слоя экранов, только чтением) → `canvas-input` (вид входа `mockup`).

### Команды

```
python project/tree.py check otves-office office --repo <S2>                                  # код 0
python project/states.py check otves-office office --repo <S2>                                # код 0
python project/screen_map.py check otves-office office --repo <S2>                            # код 0
python project/canvas_input.py build otves-office office --stage mockup --repo <S2>           # код 1
python project/canvas_input.py check otves-office office --repo <S2>                          # код 1
python project/ds_coverage.py check otves-office office --stage mockup --repo <S2>            # код 0
python project/design_audit.py check otves-office office --repo <S2> --out <scratchpad>       # код 1
```

### Результат

**Экраны.** `tree check`, `states check`, `screen_map check` — по **0 error · 0 warning · 0 hint**: деревья по
грамматике, наборы состояний покрыты, свод `map.md` совпадает с экранами. Все пять экранов, каркас, четыре блока и
`map.md` — `stable`: второй вход дизайна кабинета готов.

**Вход холста для макета** (`build --stage mockup`): партия — все пять экранов (`not-found`, `plan-dashboard`,
`request-card`, `request-new`, `requests-list`). Записаны `INPUT.md`, `brief.yaml`, `contract.md` (десять разделов и
раздел на экран), `copy.md`, `demo-data.json`, `assets.md`, `ACCEPTANCE.md` (A–H, N, S, V). Итог — **1 error · 1 warning
· 0 hint**, код 1; «Блок PRE ux 12/02 §2: без незаполненных пунктов»; покрытие ДС на макете — 0 находок.

| тяжесть | правило | что | путь | что делать |
|---|---|---|---|---|
| error | R-MAT-012 | этап `mockup` берёт только `approved`: 45 строк `checked` (из 53; `approved` — 8) — на артборде `[PLACEHOLDER: текст на утверждении]` | `screens/office/texts.md` | `/screen-deep-dive otves-office office texts` — утверждает владелец продукта |
| warning | R-COV-007 | профиля голоса с каналом `product-ui` нет — строки тона во входе нет | `voice.yaml` (файла нет) | `/design-deep-dive otves-office` — `meaning` (голос) |

`design_audit check`: **2 error · 3 warning · 0 hint**, код 1 — тот же R-MAT-012; R-REF-001 — `brand.yaml#voice_ref`
ведёт в несуществующий `../voice.yaml`; R-COV-007 — `voice.yaml` нет; R-MAT-010 — бриф на вид закрыт, а vision, `user.md`,
`surface.md`, `object.md`, `action.md`, `capability/office.md` — `draft`; R-MAT-001 — ДС `approved`, а карточка стиля
не выбрана (`style_tiles: []`).

**Заказчику.** Экраны кабинета в порядке. Вход для макета собран, но **макет рисовать нельзя** — гейт 2 «чистовой макет
— только на утверждённых текстах»: 45 строк интерфейса проверены, но не утверждены. Дальше: владелец продукта
утверждает строки — `/screen-deep-dive otves-office office texts` (этап `ui-texts`), затем пересборка входа
`--stage mockup`; либо сначала вайрфрейм — ему хватает `checked` (`canvas_input build … --stage wireframe`). Вход
`mockup` по контракту ещё ждёт принятого вайрфрейма или записи его пропуска в заметке пропусков («структура
принимается на макете»): вайрфрейма нет, поэтому заход сразу в макет — вопрос «почему сейчас?» (`phases.md § 10`).
Доклад: голоса продукта нет, хотя `phases.md § 1` требует его до ДС и текстов интерфейса (`/design-deep-dive
otves-office`, `meaning`); ссылка бренда на голос битая; бриф на вид и ДС закрыты на открытых источниках.

### Находки о текстах

1. **Гейт 2 и раскладка входа не оговаривают кабинет.** `claude-design.md § 6`, `error` — «на макете факты не
   `confirmed`, факт без источника, фактов нет»; справка `canvas_input` (R-MAT-012 `error`) — то же без оговорки о
   роде; раскладка входа: `facts.md` — «wireframe, mockup», `refs.md` — «mockup», тоже без рода. У кабинета без
   `facts.yaml` сборка `mockup` фактов не требует, `facts.md` и `refs.md` не пишет (референсов в брифе на вид нет —
   `references: []`), а «Пробелы» `INPUT.md` об этом молчат. По смыслу числа кабинета — демо-набор, но тексты этого не
   говорят: строка таблицы читается как ошибка «фактов нет».

Замечаний к пути нет: строка `screens` `phases.md § 4` прямо называет три утилиты экранов, а справка `canvas_input` —
кто закрывает R-MAT-012 (`/screen-deep-dive … texts`); такой вход есть в `screen-deep-dive/SKILL.md`.

## 3. ДС — свежесть производных, покрытие для макета, правка заказчика (`<S3>`, `<LIVE>`)

### Путь

- `SKILL.md § Холст и артефакты claude.ai`: «правка заказчика на холсте поднимается в источник по роду правки —
  токены… (`references/claude-design.md § Правки заказчика`)»; `§ Утилиты и запасной путь`: производные ДС и покрытие
  компонентов — утилиты `scripts/README.md § project`.
- `phases.md § 5`, контракт `design-system`: «Проверка. `ds_build check <slug>` — формат токенов DTCG схемой
  (R-STRUCT-006) и производные равны сборке (R-FRESH-001)»; «Правка заказчика в артефакте ДС или на холсте поднимается
  в токены DTCG (`ds_sync`)… — `claude-design.md § Правки заказчика`». Контракт `ds-components`: «Покрытие —
  `ds_coverage check <slug> <surface> --stage ds-components`… тип без ключа или компонента закрывают до макета — на
  макете кабинета он `error`»; `canvas-input`: «перед макетом покрытие ДС (`ds_coverage`)». Ключ «для макета» —
  `--stage mockup` — назвала справка `ds_coverage` («error только у поверхности кабинета на макете — … или вызов
  `--stage mockup`»).
- `claude-design.md § 5`, таблица: «облик системный: акцент… → `…/design/system.tokens.json` — § Правки токенов»;
  `§ Правки токенов`, шаг 1: «Живой `tokens.json` артефакта… сверяется со сборкой из DTCG — `ds_sync check <slug> --live
  ФАЙЛ`; `ds_sync build <slug> --live ФАЙЛ` предлагает правки путей DTCG, `--write` записывает их по месту… Токен-алиас
  (`{primitive.…}`) — развилка для заказчика»; шаг 3 — контраст, `ds_build build`, публикация.
- `scripts/README.md § project` (строки `ds_build`, `ds_coverage`, `ds_sync`); `--help` утилит.

Этапы: `design-system` (свежесть производных, правка заказчика в ДС) и проверка покрытия перед `mockup` (`ds-components`
закрыт).

### Команды

```
python project/ds_build.py check otves-office --repo <S3>                                     # код 0
python project/ds_coverage.py check otves-office office --stage mockup --repo <S3>            # код 0
python project/ds_coverage.py show otves-office office --repo <S3>                            # код 0
python project/ds_sync.py check otves-office --live <LIVE> --repo <S3>                        # код 1
python project/ds_sync.py build otves-office --live <LIVE> --repo <S3>                        # код 0, без --write
python project/ds_build.py show otves-office --repo <S3>                                      # роли акцента и фоны
python lib/color.py contrast "#ffffff" "#1e40af"   (и пары на фонах)                           # код 0
python project/design_audit.py check otves-office --repo <S3> --out <scratchpad>              # код 1
```

### Результат

- **Производные ДС свежие:** `ds_build check` — 0 находок: `system.tokens.css`, передняя часть `DESIGN.md`,
  `tokens.json` и README артефакта равны сборке, формат DTCG в порядке.
- **Покрытие для макета:** `ds_coverage check --stage mockup` — 0 находок; `show` — 18 типов `ui:` пяти stable-экранов
  (`AddressMap` — расширение, `Alert` и `Banner` → `Callout`, `Button`, `Table`, `Sidebar`, `TopBar` …), у каждого ключ
  карты решений и компонент артефакта, итог `ok`.
- **Сверка живого `tokens.json`:** `ds_sync check` — **1 error** R-FRESH-001: `--color-accent-solid`, тема `light`:
  сборка `#1d4ed8` → на странице `#1e40af`; в DTCG это алиас `{primitive.color.accent.700}`, на тот же примитив
  ссылается `color.accent.text`. Тёмная тема не задета (`#60a5fa`).
- **Предложение скилла** (`ds_sync build` без `--write`): `/color/accent/solid/$value = {"colorSpace": "srgb",
  "components": [0.1176, 0.251, 0.6863], "hex": "#1e40af"}` и развилка владельцу:
  1. **только главное действие** — литерал в роль `color.accent.solid` (`ds_sync build otves-office --live <файл>
     --write`); ссылка на примитив рвётся, `color.accent.text` (текст-акцент, ссылки) остаётся `#1d4ed8`;
  2. **весь акцент** — значение `primitive.color.accent.700` = `#1e40af` руками в `system.tokens.json` (команды нет); за
     ним меняется и `color.accent.text`; `ds_sync check` сойдётся после публикации ДС.

  После любой дороги — пересчёт контраста, `ds_build build otves-office`, публикация ДС по «прочитать → слить →
  опубликовать», обновление копии ДС в холстах. Предварительный контраст (правка не записана): белый на `#1e40af` —
  8,72 : 1 (сейчас на `#1d4ed8` — 6,7 : 1); `#1e40af` на `color.bg.canvas` / `surface` / `selected` — 8,34 / 8,72 /
  8,01: слабых пар правка не даёт.
- **Структурный прогон:** 1 error · 3 warning · 1 hint — R-REF-001 `brand.yaml#voice_ref` → нет `../voice.yaml`;
  R-COV-007 голоса нет; R-MAT-010 бриф на вид закрыт на `draft`-источниках; R-MAT-001 ДС `approved` без выбранной
  карточки стиля; R-SURF-007 у `office` нет `design/office/`.

**Заказчику.** Дизайн-система в порядке и готова к макету: производные совпадают с токенами, все 18 компонентов экранов
есть. Правка цвета главного действия на странице ДС в репозиторий ещё не поднята — без подъёма её сотрёт следующая
сборка. Решите: темнее только главная кнопка (дорога 1) или весь акцент продукта вместе с текстом-ссылками (дорога 2).
Контраст станет лучше при любой дороге. Принятых макетов нет, поэтому повторной приёмки правка не потребует. Исполнитель
— `/design-deep-dive otves-office`, этап `design-system` (`claude-design.md § Правки токенов`); запись — только по слову
владельца продукта.

### Находки о текстах

1. **Адреса ДС нет, а никто этого не говорит.** В `<S3>` нет `design/ARTIFACTS.md`, хотя ДС `approved`: контракт
   `design-system` велит «опубликован приватно…, адрес — в `ARTIFACTS.md` продукта», а шаг 1 синхронизации — «`read`
   артефакта по адресу из `ARTIFACTS.md`». `ds_build`, `ds_sync`, `design_audit` об этом молчат: R-MAT-006 проверяет
   поля строк таблицы «Артефакты», а не наличие файла у утверждённой ДС.

Остальное сходится: справка `ds_sync`, указатель, протокол и сама находка одинаково называют обе дороги, соседа по
алиасу и шаги после правки. Ключ отдельного прогона покрытия «для макета» (`--stage mockup`) `phases.md` не называет,
но указатель `scripts/README.md` и справка `ds_coverage` ведут к нему однозначно. Задача говорит «поправил на холсте»,
а по протоколу правка холста — шаг 2 (`literal_tokens.py`); живой файл здесь — `tokens.json` артефакта ДС, поэтому
шаг 1, исходников холста в `<S3>` нет.

## 4. Пакет — манифест готовности (`<S4A>`) и структурный аудит двух проектов (`<S4B>`)

### Путь

- `SKILL.md § Завершение сессии`, п. 4: «Закрыт этап `package` — назвать манифест `…/design/<surface>/ready.yaml` и
  строку для хаба»; `§ Утилиты и запасной путь` — «манифест готовности, структурный прогон аудита».
- `phases.md § 7`, контракт `package`: «Выход. Манифест `…/design/<surface>/ready.yaml`… — собирает `ready build <slug>
  <surface>`»; «Единица готова, когда её композиция закрыта (план `approved`…), тексты `approved`, факты публикуемы
  или пробел назван, а макет принят с совпавшим отпечатком»; «Проверка. `ready check <slug> <surface>` — …
  (R-FRESH-006)»; «Вход… прогон `design_audit check` поверхности (§0): его находки — доклад заказчику… жёстко пакет
  держит только гейт 4».
- Аудит: `SKILL.md § Деньги, ключи…, коммиты` — «перед коммитом — структурный прогон `design_audit check <slug>`»;
  `.claude/skills/design-audit/SKILL.md § Два прогона`, `§ Уровни тяжести`; `rules.md` (R-COV-007, R-DEBT-002 и правила
  находок); `scripts/README.md § project`; `ready.py --help`, `design_audit.py --help`.

Этап — `package`; аудит — структурный прогон `design_audit check` (без поверхности — весь проект).

### Команды

```
python project/ready.py build otves-remont-nn promo --repo <S4A>                              # код 0
python project/ready.py check otves-remont-nn promo --repo <S4A>                              # код 0
python project/ready.py show otves-remont-nn promo --repo <S4A>                               # код 0
python project/design_audit.py check otves-remont-nn promo --repo <S4A> --out <scratchpad>    # код 0
python project/design_audit.py check otves-remont-nn --repo <S4A> --out <scratchpad>          # код 0
python project/ds_build.py check otves-remont-nn --repo <S4A>                                 # код 1 (сверка, см. находку 1)
python project/design_audit.py check otves-remont-nn --repo <S4B> --out <scratchpad>          # код 1
python project/design_audit.py check otves-office --repo <S4B> --out <scratchpad>             # код 1
```

### Результат — манифест готовности `<S4A>`

`ready build` записал `design/promo/ready.yaml`: **`status: not-ready`**, единиц 2, готовых 0, источников 10,
`consumer: <org>/site`; `ready check` — 0 находок (манифест равен сборке); `ready show` — одобрений нет, отпечатков нет.

| единица | композиция | тексты | макет | почему не готова |
|---|---|---|---|---|
| `home` | план `proposed` | нет copy deck (`none`) | `none` | план не утверждён; текстов нет; макета нет — ни строки «Приёмка» в `REVIEW.md`, ни решения «макет пропущен»; `open` — 9 демо-фактов |
| `spasibo` | план `approved` | copy deck `draft` | `none` | тексты не утверждены; макета нет |

`after_build` пуст у обеих: входа холста и `ACCEPTANCE.md` нет. Структурный прогон поверхности — 0 error · 17 warning ·
8 hint (компонентов `Checkbox`, `Link` нет, состояния `Button`, `Field` не нарисованы; план `spasibo` утверждён на
открытых брифе и смысле; у `footer/legal` нет обязательного факта; уведомление РКН не выяснено; CRM и телефония без
строки `integration.md`; голоса интерфейса `cabinet` нет; 4 страницы без плана; `open` манифеста — 9).

**Заказчику.** Лендинг к сборке **не готов**: ни одна страница не прошла приёмку макета, а без принятого макета с
совпавшим отпечатком пакет не собирается (гейт 4). У главной ещё не утверждён план и нет текстов, у «Спасибо» тексты —
черновик. Дальше: главная — `page-plan` → `copy` → `copy-audit`; «Спасибо» — `copy-audit`; обе — `canvas-input` →
`wireframe` → `mockup` → `acceptance`, затем `ready build` заново. Собрать страницу без макета можно только решением
заказчика «макет пропущен: сборка по ДС и плану» в заметке пропусков поверхности. На главной 9 демо-фактов: в публикацию
их не пустит `copydeck.py validate --final` (гейт 3). Строки для хаба «готово к сборке» нет — готовых единиц нет.
Исполнитель — `/design-deep-dive otves-remont-nn promo`.

**Чего аудит не сказал.** У ДС `otves-remont-nn` в `<S4A>` нет токенов DTCG `design/system.tokens.json` и
`system.tokens.css`, есть только `tokens.json` и README артефакта. Утилита `ds_build check` даёт **error R-STRUCT-006**
«нет токенов DTCG, а производные ДС есть: tokens.json, README.md», а `design_audit` её не вызывал (в `called` нет
`ds_build`) и показал 0 error без заметки «не проверялось». `ready.yaml` токенов в источниках не называет, хотя
репозиторий кода читает `system.tokens.css`. Та же картина — в `<S1>` (задача 1).

### Результат — структурный аудит `<S4B>`

**`otves-remont-nn`: 9 error · 18 warning · 11 hint**, код 1; заметка сводки: «ds_build: R-FRESH-001 не проверялось —
токены не собираются, пока есть ошибки формата».

| правило | путь | что | что делать |
|---|---|---|---|
| R-SURF-001 | `site/old-promo` | папка поверхности `old-promo`, которой нет в `surface.md` | строка поверхности — `/project-deep-dive otves-remont-nn`; осиротевшая папка — `/design-deep-dive otves-remont-nn`, удаление с каскадом |
| R-STRUCT-006 | `design/system.tokens.json` | алиас `color.text.default` → `{primitive.color.neutral.950}` ведёт в пустоту | правка токена в `system.tokens.json`, затем `ds_build build otves-remont-nn` |
| R-SURF-004 | `screens/promo` | у лендинга есть папка экранов — её место занимает слой страницы | нужное — в слой страницы `/design-deep-dive otves-remont-nn promo`; папку убирает исполнитель соседнего слоя |
| R-REF-003 | `site/promo/copy/spasibo.yaml` | слота `confirmation/reschedule` нет среди текстовых слотов плана `spasibo` | `/design-deep-dive otves-remont-nn promo copy-deck:spasibo` — стык с планом |
| R-REF-001 | `site/promo/site-brief.yaml` | `brand.ref` → несуществующий `../../design/brand-old.yaml` | `/design-deep-dive otves-remont-nn promo`, этап `brief` |
| R-COV-002 | `site/promo/copy/spasibo.yaml` | слот `footer/privacy-label` утверждённого плана без текста при закрытом copy deck | этап `copy`, copy deck `spasibo` |
| R-COV-003 | `site/promo/plans/spasibo.yaml` | PL-F01: `fact:legal-details` нет в `facts.yaml` (секция `footer`) | `/design-deep-dive otves-remont-nn promo page-plan:spasibo` |
| R-FRESH-006 | `design/promo/ready.yaml` | манифест отстал: новые источники (манифест ассетов, `system.tokens.json`), отпечатки copy deck, плана, брифа и ещё 4 | `ready build otves-remont-nn promo` на этапе `package` после отчёта `/design-audit` |
| R-MAT-008 | `design/promo/assets/logo.svg` | ассет слота `header-logo` (`generate`) есть, а план ассетов `spasibo` — `draft` без `approval` (гейт 1) | `/design-deep-dive otves-remont-nn promo`, `asset-plan` — утверждение |

**`otves-office`: 5 error · 5 warning · 0 hint**, код 1.

| правило | путь | что | что делать |
|---|---|---|---|
| R-FRESH-001 | `design/DESIGN.md` | передняя часть отстала: `color-accent-solid` `#1d4ed8`, в сборке `#1e40af` | `ds_build build otves-office` — производные руками не правят |
| R-FRESH-001 | `design/_design-system/project/tokens.json` | `tokens.json` артефакта отстал (то же значение) | то же |
| R-FRESH-001 | `design/system.tokens.css` | `--primitive-color-accent-700` `#1d4ed8`, в сборке `#1e40af` | то же |
| R-COV-005 | `design/system.yaml` | `ui:Pagination` (экран `requests-list`) без ключа карты решений — `error`: кабинет на макете | `/design-deep-dive otves-office office`, этап `ds-components` |
| R-FRESH-003 | `design/office/input/copy.md` | вход правлен руками: отпечаток не равен манифесту | правку — в источник, затем `canvas_input build otves-office office --stage mockup` |

Предупреждения `otves-office`: R-FRESH-002 ×2 (токены и карта решений изменились после сборки входа), R-COV-007,
R-MAT-010, R-MAT-001.

**Голос продукта.** Оба проекта — `warning` R-COV-007, ошибок нет: у `otves-remont-nn` «канал product-ui есть, а
профиля голоса продукта `voice.product.yaml` нет (интерфейс: cabinet)» → «/design-deep-dive otves-remont-nn — голос
продукта»; у `otves-office` «профиля голоса `voice.yaml` нет: поверхностям office не на что опереть тексты» →
«/design-deep-dive otves-office — meaning (голос)». Для заказчика: голос бренда лендинга есть, голоса интерфейса нет ни
у одного кабинета — тексты интерфейса и бриф холста не на что опереть, строки тона во входе холста нет.

**Демо-факты.** Только `otves-remont-nn`, только `hint` R-DEBT-002 — макет на них допустим, публикацию держит
`copydeck.py validate --final` (гейт 3): факты продукта — демо (`example: true`); `open` манифеста готовности — 9 у
`home`; в закрытом copy deck `spasibo` — демо-факт `company-since-2014`. Рядом — `warning` R-MAT-001 («copy deck
`spasibo` approved на открытом: факты draft») и `error` R-COV-003 о факте `legal-details`, которого нет вовсе. У
`otves-office` о демо-фактах аудит молчит: фактов у кабинета нет, демо-набор — пример по построению.

### Находки о текстах

1. **Структурный прогон молча пропускает ДС без токенов DTCG.** Справка `design_audit`: «Какие утилиты зовутся: …
   утилиты project/ — ds_build (check)…»; `rules.md` R-FRESH-001: «Сверку ведёт… `ds_build check` (вызовом
   `design_audit`)», а что не проверено — «заметка сводки»; `design-audit/SKILL.md § Два прогона`: «то, что утилита не
   проверила, проверяется чтением или называется в отчёте непроверенным, чтобы счёт `error` не читался как полный». В
   `<S4A>` и `<S1>` `ds_build` не вызван, заметки нет, итог — 0 error; отдельный `ds_build check` — error R-STRUCT-006.
   Этап `package` опирается на этот прогон. Манифест готовности тоже молчит: по справке `ready` источники сайта — «ДС
   (статус токенов, CSS и прозы — статус system.yaml)», а в `<S4A>` в `sources` — только `design/system.yaml`, без
   блокера и строки `open`, хотя код сайта читает «ДС (токены с CSS-переменными, прозу, карту решений)»
   (`design/README.md § Пакет для кода`).
2. **Кто решает об `error` перед пакетом — два ответа.** `phases.md § Принципы всех этапов`: «Кроме гейтов, `error`
   дают поломки самого файла… Это не решение заказчика, а дефект, и его исправляют». Контракт `package`: «прогон
   `design_audit check`…: его находки — доклад заказчику, закрыть их до пакета или собрать с ними — решение
   заказчика»; так же `docs/projects/_template/design/README.md § Пакет для кода` («его находки закрывает или принимает
   заказчик»), `design-audit/SKILL.md § Формат отчёта` и совет R-FRESH-006 («его error закрывает или принимает
   заказчик»). По первому тексту битый алиас токена или вход, правленный руками, заказчик не принимает, по второму —
   принимает.
3. **Какой аудит перед `ready build`.** Контракт `package` и `design/README.md § Пакет для кода`: после «структурного
   прогона `design_audit check`»; совет R-FRESH-006: «на этапе package, после отчёта /design-audit» — то есть скилл
   целиком, с правилами чтением и `last-report.md`.
4. **Совет R-COV-007 без этапа.** `design-audit/SKILL.md § Формат отчёта`: «В каждой находке — id правила и шаг: этап
   или запись `/design-deep-dive`». У `otves-remont-nn` совет — «/design-deep-dive otves-remont-nn — голос продукта»:
   этапа с таким id нет; у соседней находки того же правила — «meaning (голос)».

## Сводка находок о текстах

| # | задача | находка | где расходится | вес |
|---|---|---|---|---|
| 1 | 1 | R-COV-002 на вайрфрейме: во входе `warning`, в аудите `error` на тех же слотах; вход кладёт `[PLACEHOLDER]` на слоты без текста | `claude-design.md § 6` (таблица проверки входа; «`[PLACEHOLDER]` — только из «Нет»»), справка `canvas_input` ↔ `design-audit/references/rules.md` R-COV-002, `site/README.md § Тексты` | высокий |
| 2 | 1 | R-REF-003: во входе `warning` и только «слоты вне плана» (8), в аудите `error` ×14 (ещё `group`, `slot_type`); в таблице входа правила нет | справка `canvas_input` ↔ `rules.md` R-REF-003 | средний |
| 3 | 1 | «0 error» в `INPUT.md` и «28 error» в прогоне на одном переходе; ждёт ли публикация вайрфрейма исправления дефектов, не сказано | `phases.md § 6` (`canvas-input`, «Проверка») ↔ `§ Принципы всех этапов` | средний |
| 4 | 1 | счёт слотов без текста: 52 у входа, 53 у аудита | вывод `canvas_input` ↔ `design_audit` | низкий |
| 5 | 2 | гейт 2 («фактов нет») и раскладка входа (`facts.md`, `refs.md`) без оговорки о кабинете; сборка кабинета их молча не пишет | `claude-design.md § 6`, справка `canvas_input` ↔ вывод сборки | низкий |
| 6 | 3 | ДС `approved` без `ARTIFACTS.md` (адреса артефакта нет) — ни одна утилита этого не называет | контракт `design-system`, `claude-design.md § Синхронизация` ↔ R-MAT-006 и вывод утилит | средний |
| 7 | 4 (и 1) | `design_audit` не зовёт `ds_build`, когда нет токенов DTCG, и даёт 0 error без заметки «не проверялось»; `ds_build check` — error R-STRUCT-006; `ready` токены не называет | справка `design_audit`, `rules.md` R-FRESH-001, `design-audit/SKILL.md § Два прогона`, справка `ready`, `design/README.md § Пакет для кода` ↔ вывод | высокий |
| 8 | 4 | кто решает об `error` перед пакетом: «дефект, не решение заказчика» против «закрыть или собрать с ними — решение заказчика» | `phases.md § Принципы всех этапов` ↔ контракт `package`, `design/README.md § Пакет для кода`, `design-audit/SKILL.md § Формат отчёта`, совет R-FRESH-006 | высокий |
| 9 | 4 | перед `ready build` — утилита `design_audit check` или отчёт скилла `/design-audit` | контракт `package`, `design/README.md` ↔ совет R-FRESH-006 | низкий |
| 10 | 4 | совет R-COV-007 «— голос продукта» не называет этап (у соседней находки — «meaning (голос)») | `design-audit/SKILL.md § Формат отчёта` ↔ вывод `design_audit` | низкий |

Общий корень находок 1–3 и 8: у одной находки две шкалы — «держит ли этап» (итог входа холста, где `error` дают только
гейт 2 и целостность входа) и «дефект ли файл» (реестр аудита и `§ Принципы всех этапов`). По тексту так же двоится
R-FRESH-001: в таблице входа — `warning` «производные ДС отстали», в `§ Принципы` и реестре — `error`. Тексты нигде не
называют эту двойственность и не говорят, как докладывать её заказчику.

Путь к утилитам тексты дали однозначно во всех четырёх задачах: строка «Проверка» или «Выход» контракта → указатель
`scripts/README.md § project` → `--help`; другой репозиторий — ключ `--repo DIR` из указателя и справок.
