# Проверка по сценариям (агент CT) — ответы

Агент рабочей сессии `design-deep-dive`, первый вход в форк. Пути к демо-папкам — как в задании оркестратора:
`<S1>`, `<S2>`, `<S3>`, `<LIVE>`, `<S4A>`, `<S4B>`; `<skill>` = `.claude/skills/design-deep-dive`;
`$PY` = `~/.cache/design-deep-dive/venv/bin/python`.

## Задача 1. Лендинг — вход холста для вайрфрейма

**Итог: дошёл.** Вход собран и проходит проверку перед публикацией: 0 error, публиковать можно.

### Путь

- `<skill>/SKILL.md § Утилиты и запасной путь`: «Какую утилиту зовёт этап — строка „Проверка“ его контракта в
  `references/phases.md`»; `§ Что делать сразу при запуске`, п. 2 — `phases.md` читать по оглавлению.
- `references/phases.md § 1. Маршруты`, таблица «Лендинг и многостраничник», строка 13: «`canvas-input` → `wireframe` |
  план `approved`, copy deck `assumed` или `checked`». Вход готов: план `approved`, варианты copy deck `assumed`.
- `references/phases.md § 6. Холст → canvas-input`, «Выход»: «Вход собирает
  `canvas_input build <slug> <surface> --stage <вид входа>`»; «Проверка»: «Проверка входа —
  `canvas_input check <slug> <surface> [--stage …]`, 0 `error`, иначе этап холста не публикуется».
- `references/claude-design.md § 6. Вход холста`, «Кто собирает» — та же пара команд, раскладка `input/`.
- Демо-папка вместо корня шаблона: `scripts/README.md § project`: «Корень данных — ключ `--repo DIR`, переменная
  `DDD_REPO` или репозиторий скилла»; то же в `canvas_input.py --help` (`--repo DIR`).
- Этапы: `canvas-input` (вид входа `wireframe`), дальше `wireframe`.

### Команды

```
$PY <skill>/scripts/project/canvas_input.py --help                                                    # код 0
$PY <skill>/scripts/project/canvas_input.py build otves-remont-nn promo --stage wireframe --repo <S1> # код 0
$PY <skill>/scripts/project/canvas_input.py check otves-remont-nn promo --stage wireframe --repo <S1> # код 0
```

### Результат

Сборка записала 7 файлов в `<S1>/docs/projects/otves-remont-nn/design/promo/input/`: `INPUT.md`, `brief.yaml`,
`facts.md`, `ACCEPTANCE.md`, `pages/home/page.yaml`, `pages/home/copy.md` и `pages/home/assets.md`. Проверка после
сборки дала итог **0 error · 4 warning · 6 hint**. Манифест `INPUT.md` пишет: «этап можно публиковать». Находок
свежести и ручной правки (R-FRESH-002/003/004) нет.

| тяжесть | правило | где | что |
|---|---|---|---|
| warning | R-MAT-003 | `facts.yaml` | файл фактов в статусе `draft`, заказчик его ещё не подтвердил (`confirmed`) → этап `meaning` |
| warning | R-COV-002 | `site/promo/copy/home.yaml` | 52 текстовых слота плана без текста (`announcement-bar/text`, `header/cta-label`, `hero/cta-secondary-label` и др.) → этап `copy` |
| warning | R-MAT-003 | там же | 2 текста в `draft`: `lead-form/consent` и `footer/legal` (оба юридические) → `copy`, утверждает владелец |
| warning | R-REF-003 | там же | 8 слотов copy deck нет в плане (`hero/proof-source`, `testimonials/author`, `…/frame`, `…/quote`, `guarantee/people`, `pricing/promo` и ещё 2); в `copy.md` они идут без места в `page.yaml` → стык copy deck с планом |
| hint | R-DEBT-002 | `facts.yaml` | во входе 10 демо-фактов: на макете допустимы, в публикацию не идут |
| hint | R-COV-001 ×5 | `site/promo/plans` | у страниц `consent`, `guide`, `not-found`, `privacy` и `spasibo` нет плана, во вход они не идут |

**Как прочитать заказчику.** Каркас главной страницы лендинга можно выкладывать на холст: ошибок нет. На вайрфрейме
будут видны пробелы:

- 52 места текста без черновика и два юридических текста (согласие в форме, реквизиты в подвале) — там будут серые
  заглушки `[PLACEHOLDER]`;
- восемь готовых текстов (источник доказательства в первом экране, блок отзывов, люди у гарантии, акция у цен) не
  попадают ни в одну секцию плана;
- все цифры, отзывы и цены — демонстрационные, заказчик их не подтвердил: на вайрфрейме это допустимо, но опубликовать
  сайт с ними нельзя;
- страницы «спасибо», «политика» и «согласие», а также `guide` и `not-found` в этот вход не входят: для них нет плана.

**Что дальше.**

1. Блок вопросов холста (`phases.md § canvas-input`, «Вопросы до макета») не нужен: «Условия холста» и строка «Проверки
   макета» уже есть в `ARTIFACTS.md`.
2. Этап `wireframe` исполнителя `/design-deep-dive otves-remont-nn promo` (он же исполнитель дизайна):
   - публикация в `canvas:promo` по протоколу «прочитать → слить → опубликовать» (`claude-design.md § 4`);
   - задание — по `claude-design.md § 7`;
   - копии — `dc_to_html.py build`;
   - заказчик говорит «структура принята».
3. Параллельно — долги слоя страницы:
   - `copy`: тексты 52 слотов и стык 8 лишних слотов;
   - `meaning`: подтверждение фактов заказчиком (нужно до макета);
   - юридические тексты даёт юрист заказчика.

Наблюдение по данным демо (утилиты его не ловят): ссылки ведут на примеры базы, а не на файлы проекта. В плане это
`hierarchy` и `art_direction_ref` (`../../../../../text/02-strategy-messaging/examples/…`), в copy deck — `voice_ref`,
`facts_ref`, `meaning_ref` и `hierarchy_ref` (`../../02-strategy-messaging/examples/…`, `../../05-voice-editorial/…`). Осведомлённость тоже расходится: у плана `solution-aware`, у copy deck `product-aware`, а
манифест записал источником иерархию `home-problem-aware.yaml`.

### Находки о текстах

1. **Путь однозначен** (подтверждение, в счёт не входит). Цепочка SKILL.md → `phases.md § canvas-input` →
   `claude-design.md § 6` → `scripts/README.md § project` → `--help` ведёт к одной утилите с одной парой команд.
   `--repo` описан только в README и `--help`, а контракт и протокол показывают вызов без него. Это не тупик: SKILL.md
   прямо отсылает к README.
2. **Счёт в сообщении R-DEBT-002 не совпадает со списком.** Сообщение: «демо-факты во входе: 10 (flats-completed,
   rating-yandex-maps, review-anna-k, case-two-room-47-days, guarantee-3-years, price-from-per-m2)». Названо 6 id,
   хвоста «и ещё 4» нет. Остальные находки хвост пишут: R-COV-002 — «и ещё 46», R-REF-003 — «и ещё 2». По `facts.md`
   входа демо-фактов 10: не названы `estimate-free`, `promo-october-10`, `foreman-lapin`, `company-since-2014`.
   Читатель не видит, что список обрезан.
3. **Находка и манифест называют пробел по-разному.** R-COV-002 говорит «текстовые слоты плана без текста». Раздел
   «Пробелы» `INPUT.md` говорит «52 текстовых слотов плана без слота copy deck»: это другое утверждение — нет слота, а
   не нет текста. Там же падежи: «52 текстовых слотов», «2 текст(ов)».
4. **Совет находки R-COV-002 не подходит, когда copy deck уже есть.** Совет: «→ … этап copy (каркас из плана —
   copydeck.py skeleton)». Справка `copydeck.py`: «skeleton PLAN -o DECK — каркас copy deck из плана …; тексты пусты,
   статус draft». Режима дополнения нет. Здесь в deck уже 32 текста `assumed`: совет, выполненный буквально, затрёт их.
   Как добавить недостающие слоты в существующий deck, не сказано ни в `phases.md § copy`, ни в справке.
5. **Коды выхода утилит расходятся (мелочь).** У `copydeck.py`, к которому ведёт R-DEBT-002 («copydeck.py validate
   --final»): «0 — нет error, 2 — есть error, 1 — ошибка входа». У утилит `project/` (`scripts/README.md § project`):
   «1 — есть error; 2 — ошибка вызова». Сессия, привыкшая к `project/`, прочитает код 2 у `copydeck.py` наоборот.

## Задача 2. Кабинет — деревья экранов, состояния, свод, вход холста

**Итог: дошёл.**

- Слой экранов чистый.
- Вход под макет собран, проверка входа — 0 error.
- Но 45 из 53 строк интерфейса не утверждены, и вайрфрейма у поверхности ещё не было. Макет на таком входе — это
  макет на заглушках. Тексты дают это прочитать по-разному (находка 1).

### Путь

- `SKILL.md § Выбор проекта и поверхности`, таблица: «`web` рода `app` … | дизайн кабинета — первый вход после
  сценариев, второй — после stable-экранов». Строка `surface.md`: `office` — `web` рода `app`.
- `phases.md § 4. Слой проекта SaaS`, строка `screens`, колонка «проверка»: «утилиты `tree`, `states`, `screen_map`
  (`scripts/README.md § project`); `/screen-audit`». Это три проверки из задачи.
- `phases.md § 4 → Второй вход дизайна кабинета`:
  - «Когда. После stable-экранов поверхности и свода `map.md` без расхождений»;
  - «Тексты по этапу. `assumed` и `checked` — вайрфрейм, `approved` — чистовой макет»;
  - «Пункты [PRE] считает `contract.py check` … их же показывает `canvas_input check` кабинета».
- `phases.md § 6 → canvas-input`:
  - «Вход собирает `canvas_input build <slug> <surface> --stage <вид входа>`»;
  - «У кабинета — блок PRE (§4) и перед макетом покрытие ДС (`ds_coverage`) в той же проверке».
  - Вид входа — `mockup`: так в задаче («для макета»), `phases.md § 6 → mockup`.
- `docs/projects/_template/screens/README.md § Что слой отдаёт макету`: «во вход холста их кладёт
  `canvas_input.py build <slug> <surface> --stage wireframe|mockup`».
- `scripts/README.md § project`, строки `tree`, `states`, `screen_map`, `canvas_input`, и `--help` каждой: вызовы
  `check <slug> [<surface>] --repo DIR` однозначны.
- Этапы: проверка этапа `screens` (ведёт `/screen-deep-dive`), затем `canvas-input` с видом входа `mockup`.

### Команды

```
$PY <skill>/scripts/project/tree.py --help ; states.py --help ; screen_map.py --help               # код 0
$PY <skill>/scripts/project/tree.py       check otves-office office --repo <S2>                    # код 0
$PY <skill>/scripts/project/states.py     check otves-office office --repo <S2>                    # код 0
$PY <skill>/scripts/project/screen_map.py check otves-office office --repo <S2>                    # код 0
$PY <skill>/scripts/project/states.py     show  otves-office office --repo <S2>                    # код 0 (чтобы 0 находок не был пустым прогоном)
$PY <skill>/scripts/project/tree.py       show  otves-office office --repo <S2>                    # код 0
$PY <skill>/scripts/project/canvas_input.py build otves-office office --stage mockup --repo <S2>   # код 0
$PY <skill>/scripts/project/canvas_input.py check otves-office office --stage mockup --repo <S2>   # код 0
# сверка составных проверок входа кабинета, все — код 0:
$PY <skill>/scripts/project/contract.py    check otves-office office --stage mockup --repo <S2>
$PY <skill>/scripts/project/ds_coverage.py check otves-office office --stage mockup --repo <S2>
$PY <skill>/scripts/project/ds_build.py    check otves-office --repo <S2>
$PY <skill>/scripts/project/demo_data.py   check otves-office office --repo <S2>
```

### Результат

**Экраны.** `tree`, `states` и `screen_map` дали по **0 error · 0 warning · 0 hint**. Разбор `show` показывает, что
прогон не пустой:

- экранов 5, все `stable`: `requests-list`, `request-card`, `request-new`, `plan-dashboard`, `not-found`;
- ещё 4 блока `stable` и каркас `app-shell`;
- свод `map.md` — `stable`;
- каждое обязательное состояние набора покрыто дельтой или помечено «не применимо: причина».

**Вход холста `mockup`.** Сборка записала 7 файлов в `<S2>/docs/projects/otves-office/design/office/input/`:
`INPUT.md`, `brief.yaml`, `contract.md`, `copy.md`, `demo-data.json`, `assets.md`, `ACCEPTANCE.md`. Итог — **0 error ·
1 warning · 1 hint**. Манифест пишет «этап можно публиковать» и «Блок PRE ux 12/02 §2: без незаполненных пунктов».
Прямые прогоны это подтверждают:

- `contract` — только тот же warning;
- `ds_coverage --stage mockup`, `ds_build` и `demo_data` — по 0 находок.

| тяжесть | правило | где | что | что делать |
|---|---|---|---|---|
| warning | R-MAT-003 | `screens/office/texts.md` | 45 строк `checked` не утверждены (`app.shell.help.link`, баннеры каркаса, пустые состояния, кнопки и заголовки карточки …); утверждены 8 из 53 — пять заголовков колонок списка заявок и три подписи полей формы новой заявки; в `copy.md` входа эти 45 строк стоят как `[PLACEHOLDER: текст на утверждении]` | `/screen-deep-dive otves-office office texts`, утверждает владелец продукта; аргумент `texts` есть в `screen-deep-dive/SKILL.md`, стр. 119 |
| hint | R-COV-007 | `voice.product.yaml` (нет) | нет профиля голоса с каналом `product-ui`, поле `design_system.tone_of_voice` во входе пусто; по `design-audit/references/rules.md` это `warning` (задача 4, находка 2) | `/design-deep-dive otves-office`, этап `meaning` (голос продукта) |

Пробел манифеста без находки: манифеста ассетов поверхности нет, поэтому у пустых состояний иллюстраций мест не будет.
Их даёт выход `ds-components` («иллюстрации мест … по паспорту»). Продуктового паспорта в демо тоже нет.

**Как прочитать заказчику.**

- Экраны кабинета согласованы: все пять экранов, их блоки и карта экранов проходят проверки, обязательные состояния на
  месте.
- Материал для холста собран без ошибок. Но для чистового макета рано: 45 из 53 надписей интерфейса ждут утверждения
  владельцем продукта. На макете вместо них будут серые заглушки, а принять макет без утверждённых текстов нельзя.
- Голоса продукта нет, иллюстраций для пустых экранов нет.
- Вайрфрейма кабинета ещё не было: в `design/office/` нет `review/`, а для вайрфрейма хватает текущих `checked`-текстов.

**Что дальше.**

1. `/screen-deep-dive otves-office office texts`: владелец продукта утверждает 45 строк.
2. Голос продукта: `/design-deep-dive otves-office`, этап `meaning`. По `phases.md § 1` он «нужен до этапов 9 и 13»,
   то есть до ДС и текстов интерфейса. Здесь ДС уже `approved`, а тексты уже `checked`, так что их стоит сверить с
   голосом.
3. По маршруту (`phases.md § 1`, строки 15–16; `§ 6 → mockup`, «Вход. Принятый вайрфрейм или его пропуск в заметке
   пропусков»):
   - сначала `canvas_input build otves-office office --stage wireframe` и этап `wireframe`;
   - макет — после утверждения текстов;
   - прямо сейчас к макету — только ответом на «почему сейчас?» и записью в `<state>/design/office/_phase-jump.md`
     (`phases.md § 10`).

   В демо-папке нет дерева state (`.claude/skills/entrypoint/state/`), так что заметку пропусков прочитать было негде.

### Находки о текстах

1. **Главная: утверждённые тексты для макета кабинета — ворота или предупреждение?** Одни места читаются как стоп:
   - `phases.md § 0 → Принципы всех этапов`: «Жёстко работу останавливают пять гейтов: … чистовой макет — только на
     утверждённых текстах и подтверждённых фактах»;
   - `§ 1`, «SaaS и кабинет», строка 16: вход готов — «тексты `approved`, покрытие компонентов»;
   - `§ 4 → Второй вход`: «`approved` — чистовой макет»;
   - `§ 6 → canvas-input`, «Вход»: «`mockup` — ещё тексты `approved` (copy deck или строки `texts.md`)»;
   - `screens/README.md § Что слой отдаёт макету`: «только `approved` — чистовой макет»;
   - `canvas_input --help`: «R-MAT-012 error … на макете — тексты не approved», без оговорки «у сайта».

   Утилита же даёт кабинету только warning R-MAT-003, пишет «0 error … — этап можно публиковать» и ставит 45 из 53
   строк заглушками. Объяснение есть в одном месте — `§ 6 → mockup`, «С середины»: «у сайта вход `mockup` с текстами не
   `approved` проверку не проходит (R-MAT-012), у кабинета строка не того статуса — видимая заглушка `[PLACEHOLDER: текст
   на утверждении]`, а приёмка ждёт `approved`». В справке — полстроки у R-MAT-003: «у кабинета — строки texts.md
   (contract)». Агент, который шёл по § 1 и `canvas-input`, ждёт стопа, а видит «можно публиковать». Чтобы понять
   расхождение, надо найти исключение в «С середины» другого этапа.

2. **«Этап можно публиковать» обещает больше, чем проверено.** `INPUT.md` так пишет про этап `mockup`. Но в «Вход»
   этапа `mockup` (`phases.md § 6`) есть и «Принятый вайрфрейм или его пропуск в заметке пропусков», и «ДС установлена в
   холст». Проверка входа их не видит и не называет. Здесь вайрфрейма не было, а вывод об этом молчит. Точнее было бы
   «вход без ошибок; порядок этапов — за исполнителем».

3. **Пробел про голос противоречит сам себе.** `INPUT.md`, «Пробелы»: «голоса поверхности нет: строки тона во входе нет
   — тексты во входе уже в голосе, исполнитель их не пишет». Профиля голоса нет, поэтому «тексты уже в голосе» проверить
   нечем. При этом `phases.md § 1` требует голос «до этапов 9 и 13», а здесь ДС уже `approved` и тексты уже `checked`.
   Утилита выносит это только в hint R-COV-007 и не говорит, что нарушен порядок.

4. **Хвост списка оформлен по-разному (мелочь).** У кабинета — «… (+40)» (R-MAT-003), у сайта — «и ещё 46» (R-COV-002).
   Один формат находок (`scripts/README.md § project`: «один формат находок»), а хвост списка — в двух видах.

## Задача 3. ДС — производные, покрытие, живой `tokens.json`

**Итог: дошёл.**

- Производные ДС равны сборке из токенов.
- Покрытие под макет полное: 18 типов из 18.
- Живой артефакт расходится со сборкой в одном значении — это правка заказчика.
- Предложение правки получено, в файлы ничего не записано.

### Путь

- `phases.md § 5 → design-system`:
  - «Проверка»: «`ds_build check <slug>` — формат токенов DTCG схемой (R-STRUCT-006) и производные равны сборке
    (R-FRESH-001)»;
  - «Правка заказчика в артефакте ДС или на холсте поднимается в токены DTCG (`ds_sync`) … — `claude-design.md § Правки
    заказчика`».
- `phases.md § 6 → canvas-input`, «Проверка»: «перед макетом покрытие ДС (`ds_coverage`)».
- `docs/projects/_template/design/README.md § Покрытие компонентов`: `ds_coverage check <slug> [<surface>] --stage
  ds-components`. Для макета нужен `--stage mockup`, это сказано в `ds_coverage --help`: «error — у поверхности есть
  вход холста этапа mockup … или вызов `--stage mockup`». Там же `§ Производные`: производные ДС — утилита `ds_build`.
- `claude-design.md § 5. Правки заказчика`:
  - таблица: «облик системный: акцент … → `…/design/system.tokens.json` | § Правки токенов»;
  - «Правки токенов», шаг 1: «`ds_sync check <slug> --live ФАЙЛ`; `ds_sync build <slug> --live ФАЙЛ` предлагает правки
    путей DTCG, `--write` записывает их по месту».
- `scripts/README.md § project`, строки `ds_build`, `ds_coverage`, `ds_sync` («без ключа — предложение») и `--help`
  каждой.
- Этапы: `design-system` (проверка производных), `ds-components`/`canvas-input` (покрытие перед макетом), «Правки
  токенов» протокола холста (`fix-round` — слияние правок заказчика).

### Команды

```
$PY <skill>/scripts/project/ds_build.py --help ; ds_coverage.py --help ; ds_sync.py --help           # код 0
$PY <skill>/scripts/project/ds_build.py    check otves-office --repo <S3>                           # код 0
$PY <skill>/scripts/project/ds_coverage.py check otves-office office --stage mockup --repo <S3>     # код 0
$PY <skill>/scripts/project/ds_coverage.py show  otves-office office --repo <S3>                    # код 0
$PY <skill>/scripts/project/ds_sync.py     check otves-office --live <LIVE> --repo <S3>             # код 1 (1 расхождение)
$PY <skill>/scripts/project/ds_sync.py     build otves-office --live <LIVE> --repo <S3>             # код 0, без --write: только предложение
$PY <skill>/scripts/project/ds_build.py    show  otves-office --repo <S3>                           # код 0 (алиасы и тёмная тема акцента)
$PY <skill>/scripts/project/ds_sync.py     show  otves-office --live <LIVE> --repo <S3>             # код 0
$PY <skill>/scripts/lib/color.py contrast "#ffffff" "#1d4ed8" | "#1e40af"                           # контраст до и после
```

Что файл токенов не изменился, сверено отпечатком `md5` до и после `ds_sync build`. Прямой `diff` живого `tokens.json`
с производным `_design-system/project/tokens.json` дал одну строку: `"light": "#1d4ed8"` → `"#1e40af"`.

### Результат

- **Производные ДС свежие.** `ds_build check`: 0 · 0 · 0. `system.tokens.css`, передняя часть `DESIGN.md`, `tokens.json`
  и `README.md` артефакта равны сборке из `system.tokens.json`, формат DTCG верен.
- **Покрытие под макет полное.** `ds_coverage check --stage mockup`: 0 · 0 · 0. `show` перечисляет 18 типов
  stable-экранов, у всех `ok`: AddressMap (расширение), Alert и Banner → Callout, Button, DescriptionList, EmptyState,
  Field, KpiTile, Link, Pagination, Progress, SearchInput, Select, Sidebar, Skeleton, Table, TextInput, TopBar.
- **Живой артефакт расходится со сборкой.** `ds_sync check`: **1 error R-FRESH-001**, код 1.
  - `--color-accent-solid`, светлая тема: в сборке `#1d4ed8`, на странице артефакта `#1e40af`.
  - Вывод утилиты: «был алиас {primitive.color.accent.700}: литерал рвёт ссылку; на него же ссылаются color.accent.text
    — если правка у всех, правьте примитив».
  - Тёмную тему заказчик не трогал: там `#60a5fa`.

**Какую правку предлагает скилл** (`ds_sync build` без `--write`). Основная:

```
/color/accent/solid/$value = {"colorSpace": "srgb", "components": [0.1176, 0.251, 0.6863], "hex": "#1e40af"}
```

Это подъём правки в путь DTCG роли `color.accent.solid`, светлая тема, по протоколу («изменилось значение известного
имени — правка его пути в DTCG с темой»). Утилита называет цену: роль получает литерал, и ссылка на примитив
`primitive.color.accent.700` (`#1d4ed8`) рвётся. Альтернатива, которую она тоже называет: если новый цвет нужен всему
акценту, править примитив, и тогда вслед за ним поменяется `color.accent.text`. Выбор за владельцем продукта.
Примитива со значением `#1e40af` в ДС нет: шкала accent — 50, 400, 600, 700.

**Как прочитать заказчику.**

- Дизайн-система в репозитории цела: производные совпадают с исходником, компоненты есть на все 18 типов экранов,
  собирать макет по ней можно.
- Правка на холсте видна одна: кнопка главного действия стала темнее, `#1d4ed8` → `#1e40af`.
- Чтобы правка не пропала при следующей сборке, её нужно поднять в токены. Вариантов два:
  - только кнопка — акцентный текст (`color.accent.text`) останется прежнего синего;
  - весь акцент светлой темы — вместе с кнопкой изменится и акцентный текст.
- Белый текст на новой кнопке читается лучше: контраст WCAG 6,70 → 8,72.
- Тёмная тема не менялась.

**Что дальше** (исполнитель — `/design-deep-dive otves-office`, «Правки токенов» протокола):

1. Владелец выбирает «роль» или «примитив».
2. Запись правки: `ds_sync build … --write` — или правка примитива в `system.tokens.json`; для неё команды нет, см.
   находку 2.
3. Контраст всех пар — `build_reference_tokens.py` / `color.py`.
4. `ds_build build otves-office`.
5. Публикация ДС по § Синхронизация, обновление копии ДС в каждом холсте продукта.

Принятых макетов в демо нет, так что шаг 5 «Правок токенов» («принятые макеты проходят приёмку заново») не
срабатывает. В демо нет и `ARTIFACTS.md`: адреса артефакта ДС для шага «прочитать» у проекта нет, живой файл дал
заказчик.

### Находки о текстах

1. **Путь однозначен** (подтверждение, в счёт не входит). SKILL.md → `phases.md § design-system` → `claude-design.md §
   Правки токенов` → `ds_sync --help`. «Без ключа — предложение» из справки работает, как обещано: код 0, «без записи:
   --write — по месту, --out DIR — в копию», файл не тронут.
2. **У альтернативы «правьте примитив» нет команды.** Утилита предлагает её сама, но записать умеет только литерал
   роли: `--write` пишет путь из предложения. Совет находки ведёт сразу к записи роли: «→ поднять в color.accent.solid:
   ds_sync build otves-office --live FILE --write, затем ds_build build otves-office». Как записать правку примитива, не
   сказано ни в справке, ни в «Правках токенов»: руками в `system.tokens.json`? По логике сверки после неё `ds_sync
   check` покажет новое расхождение — `color.accent.text` на живой странице ещё старый, пока ДС не переопубликована.
3. **Совет находки пропускает шаг протокола.** «Правки токенов», шаг 3: «После правки DTCG контраст всех пар
   пересчитывается … Затем пересборка производных ДС — `ds_build build`». Совет `ds_sync check` — «`--write`, затем
   `ds_build build`», без контраста. Справка `ds_sync` его упоминает («После подъёма — контраст пар и пересборка
   производных»), а совет в выводе — нет.
4. **Правка заказчика названа ошибкой свежести.** `ds_sync check` помечает законную правку как «error R-FRESH-001», код
   1. Так сказано в справке, но R-FRESH-001 у `ds_build` и в `/design-audit` означает «производные не равны сборке».
   Заказчику «ошибка» читается как брак, а это правка, которую надо поднять. Мелочь, но в отчёте аудита формулировка
   путает.
5. **В таблице `ds_coverage show` нет заголовка, а колонки не такие, как в справке.** Справка: «таблица покрытия: тип,
   где стоит, ключ, компонент». Вывод: `office  AddressMap  extensions  AddressMap  ok` — поверхность, тип, вид ключа,
   компонент, итог. Экранов, «где стоит» тип, в таблице нет.
6. **В справке `lib/color.py` мёртвый путь и история.** Утилита названа в `phases.md § design-system` («`color.py`»).
   В справке: «(написано агентом A волны 1, проверено по калькулятору APCA)» и «импорт: `from color import *` при
   `sys.path.insert(0, ".../99-raw/tools")`». Папки `…/99-raw/tools` в скилле нет: папки `kb/<база>/99-raw/` есть, но
   `tools` ни в одной из них нет, а модуль лежит в `scripts/lib/`. «Агент A волны 1» — след истории сборки
   (`.claude/rules/forward-only.md`).

## Задача 4. Пакет — манифест готовности и структурный аудит

**Итог: дошёл по обеим частям.**

- A: манифест собран, поверхность `not-ready`, готовых единиц 0 из 2.
- B: аудит дал 9 error у `otves-remont-nn` и 5 error у `otves-office`. Голос продукта — warning R-COV-007 у обоих
  проектов. Демо-факты — долг (hint R-DEBT-002), а не ошибка.

### Путь

- `phases.md § 7 → package`, «Выход»: «Манифест `…/design/<surface>/ready.yaml` … — собирает `ready build <slug>
  <surface>`»; «Проверка»: «`ready check <slug> <surface>` — манифест равен сборке». Правило «Единица готова …» и
  «жёстко пакет держит только принятый макет с совпавшим отпечатком».
- `docs/projects/_template/design/README.md § Пакет для кода` (то же правило готовности; «на этапе `package` после
  отчёта `/design-audit` (его `error` закрывает или принимает заказчик)»), `scripts/README.md § project` (строка
  `ready`), `ready.py --help` (что собирается, `blockers`, коды).
- Аудит: `SKILL.md § Проверки` и `§ Завершение сессии` → `/design-audit`. В `.claude/skills/design-audit/SKILL.md § Два
  прогона`: «Прогон ведёт утилита `design_audit` … `design_audit check <project-slug> [<surface>] --json`»; дальше
  `scripts/README.md § project` (строка `design_audit`) и `design_audit.py --help`. Тяжесть и смысл правил сверены по
  `.claude/skills/design-audit/references/rules.md` (R-STRUCT-003, R-COV-007).
- Этапы: `package` (часть A); аудит — не этап исполнителя, а `/design-audit`, который по контракту запускает человек
  (`phases.md § 0`, «`/design-audit` в цепочке»). Здесь его прогнал я — по задаче заказчика.

### Команды

```
$PY <skill>/scripts/project/ready.py --help                                                   # код 0
$PY <skill>/scripts/project/ready.py build otves-remont-nn promo --repo <S4A>                 # код 0 — записан ready.yaml
$PY <skill>/scripts/project/ready.py show  otves-remont-nn promo --repo <S4A>                 # код 0
$PY <skill>/scripts/project/ready.py check otves-remont-nn promo --repo <S4A>                 # код 0 — манифест равен сборке
$PY <skill>/scripts/project/design_audit.py --help                                            # код 0
$PY <skill>/scripts/project/design_audit.py check otves-remont-nn --repo <S4B>                # код 1
$PY <skill>/scripts/project/design_audit.py check otves-remont-nn --repo <S4B> --json         # код 1; 37 строк; путь к summary.json — в stderr
$PY <skill>/scripts/project/design_audit.py check otves-office --repo <S4B>                   # код 1
# сверка находки, которой нет в отчёте:
$PY <skill>/scripts/text/claims_check.py lint-facts <S4B>/docs/projects/otves-remont-nn/facts.yaml   # код 2: 1 ERROR, 1 WARNING
```

Файлы результата аудита — `$DDD_HOME/out/project/design_audit/<slug>/` (`findings.jsonl`, `summary.json`). Отчёт
`last-report.md` (`design-audit/SKILL.md`, шаг 7) я не писал: он лежит в шаблоне
(`.claude/skills/design-audit/audit-state/`), а правки шаблона задача запрещает.

### Результат A — манифест готовности `promo` (`<S4A>`)

`<S4A>/docs/projects/otves-remont-nn/design/promo/ready.yaml`:

- `status: not-ready`, единиц 2, готовых 0, источников 10;
- `consumer: <org>/site`;
- `frontend_design: {surface: landing, ambition: L1, motion_cap: expressive}`;
- `ready check` — 0 находок.

| единица | композиция | тексты | макет | профиль бюджета | `open` |
|---|---|---|---|---|---|
| `home` | план `proposed` | `none` — copy deck нет | `none` | `landing-lead-services@L1` | 9 демо-фактов: `case-two-room-47-days`, `company-since-2014`, `estimate-free`, `foreman-lapin`, `guarantee-3-years`, `price-from-per-m2`, `promo-october-10`, `rating-yandex-maps`, `review-anna-k` |
| `spasibo` | план `approved` | `draft` | `none` | `thank-you-page@L0` | — |

`blockers`:

- «home: план proposed»;
- «home: текстов нет»;
- «home: макета нет: строки в REVIEW.md и решения «макет пропущен» нет»;
- «spasibo: тексты draft»;
- «spasibo: макета нет …».

Источники: `system.yaml` — `approved`, `facts.yaml` и `voice.yaml` — `draft`, `brand.yaml` — `none`, арт-дирекция и
спецификация движения — `proposed`, бриф — `proposed`.

**Готова ли поверхность — нет**, и отдать в код нечего. По правилу `phases.md § 7` («Единица готова, когда её композиция
и тексты закрыты, макет принят с совпавшим отпечатком, факты подтверждены или пробел назван, ДС утверждена») у каждой
страницы не выполнено сразу несколько условий:

- **`home`**: план не утверждён, текстов нет, макета нет. Цифры, отзывы, цены и акция на странице — демонстрационные
  (9 в `open`); `facts.yaml` — `draft`, заказчик его не подтверждал.
- **`spasibo`**: план утверждён, но тексты в черновике и макета нет.

Главный стоп — жёсткий гейт `package`: «только принятый макет с совпавшим отпечатком». Принятого макета нет ни у одной
страницы. Решения «макет пропущен» тоже нет.

Строки для хаба «готово к сборке: …» нет.

Для заказчика: лендинг к сборке не готов; сначала — утверждённые план и тексты главной, тексты «спасибо», макеты обеих
страниц и настоящие факты.

**Что дальше** (`/design-deep-dive otves-remont-nn promo`):

1. `home`: `page-plan` — заказчик выбирает форму страницы, владелец утверждает план → `copy` → `copy-audit`
   (утверждение).
2. `spasibo`: `copy-audit`.
3. Обе страницы: холст — `canvas-input` → `wireframe` → `mockup` → `acceptance`.
4. Факты: `meaning` — подтверждение заказчиком.
5. Затем человек запускает `/design-audit otves-remont-nn promo`, и на этапе `package` манифест пересобирается.

По контракту `package` манифест собирают после отчёта аудита. Здесь он собран по просьбе как срез: готовности это не
меняет.

Наблюдение по данным S4A: у ДС нет `design/system.tokens.json`, `system.tokens.css` и `DESIGN.md`, есть только
`system.yaml` (`approved`) и файлы артефакта. Манифест берёт статус ДС из `system.yaml`, как и обещает справка («статус
токенов, CSS и прозы — статус system.yaml»). Поэтому то, что код-репо нечего читать как CSS-переменные, в `blockers` не
попадает.

### Результат B — структурный аудит `<S4B>`

**`otves-remont-nn`: 9 error / 17 warning / 11 hint, код 1.** Поверхности: `promo` (landing) и `cabinet` (app).
Заметки сводки:

- «copydeck.py: правила не загружены: copy-slots.yaml нет — длины слотов и обязательность фактов не проверены»;
- «ds_build: R-FRESH-001 не проверялось — … пока есть ошибки формата».

| # | правило | путь (от `docs/projects/otves-remont-nn/`) | что не так | что делать |
|---|---|---|---|---|
| 1 | R-SURF-001 | `site/old-promo/` | папка поверхности `old-promo`, которой нет в `surface.md` | нужна поверхность — строка реестра через `/project-deep-dive otves-remont-nn`; не нужна — удаление с каскадом через `/design-deep-dive otves-remont-nn` |
| 2 | R-STRUCT-006 | `design/system.tokens.json` | `color.text.default` — алиас `{primitive.color.neutral.950}` ведёт в пустоту; из-за этого свежесть производных ДС не проверялась | правка токена (этап `design-system`), затем `ds_build build otves-remont-nn` |
| 3 | R-SURF-004 | `screens/promo/` | у лендинга есть папка экранов, а её место занимает слой страницы `site/promo/` | нужное — в слой страницы (`/design-deep-dive otves-remont-nn promo`); папку убирает исполнитель экранов (`/screen-deep-dive`) |
| 4 | R-REF-003 | `site/promo/copy/spasibo.yaml` | слота `confirmation/reschedule` из copy deck нет в плане `spasibo` | стык copy deck с планом: `/design-deep-dive otves-remont-nn promo copy-deck:spasibo` |
| 5 | R-REF-001 | `site/promo/site-brief.yaml` | `brand.ref` → `../../design/brand-old.yaml`, такого файла нет | этап `brief` |
| 6 | R-COV-002 | `site/promo/copy/spasibo.yaml` | у слота `footer/privacy-label` утверждённого плана нет текста, а copy deck уже закрыт | этап `copy`, copy deck `spasibo` |
| 7 | R-COV-003 | `site/promo/plans/spasibo.yaml` (`footer`) | PL-F01: `fact:legal-details` нет в `facts.yaml`. В `facts.yaml` это пробел `missing` (стр. 246); у `home` ссылка верная — `missing:legal-details` | `/design-deep-dive otves-remont-nn promo` (этап в совете не назван); реквизиты даёт заказчик — без них страница не публикуется |
| 8 | R-FRESH-006 | `design/promo/ready.yaml` | манифест отстал: новые источники — манифест ассетов и `system.tokens.json`, не совпадают `copy/spasibo`, `plans/spasibo`, `site-brief` и ещё 4 | `ready build otves-remont-nn promo` на этапе `package` |
| 9 | R-MAT-008 | `design/promo/assets/logo.svg` | ассет слота `header-logo` (источник `generate`) уже есть, а план ассетов `spasibo` — `draft` без утверждения; это один из пяти гейтов: генерация — только по утверждённому плану | этап `asset-plan`: утверждение плана заказчиком (траты) |

**`otves-office`: 5 error / 6 warning / 0 hint, код 1.** Поверхность `office` (app), вход холста — `mockup`.

| # | правило | путь (от `docs/projects/otves-office/`) | что не так | что делать |
|---|---|---|---|---|
| 1 | R-FRESH-001 | `design/DESIGN.md` (передняя часть) | отстала от сборки: `color-accent-solid` в файле `#1d4ed8`, в сборке `#1e40af` | `ds_build build otves-office` (производные руками не правят) |
| 2 | R-FRESH-001 | `design/_design-system/project/tokens.json` | то же в `tokens.json` артефакта | то же |
| 3 | R-FRESH-001 | `design/system.tokens.css` | `--primitive-color-accent-700: #1d4ed8`, а в сборке `#1e40af` | то же. По смыслу это продолжение задачи 3: в DTCG уже правлен примитив, а производные не пересобраны и ДС не переопубликована |
| 4 | R-COV-005 | `design/system.yaml` | у `ui:Pagination` (экран `requests-list`) нет компонента ДС: ключа нет в `components` и `extensions`; `error`, потому что есть вход `mockup` | этап `ds-components`: `/design-deep-dive otves-office office` |
| 5 | R-FRESH-003 | `design/office/input/copy.md` | вход правлен руками: отпечаток не равен манифесту | правку — в источник (`texts.md` ведёт `/screen-deep-dive`), затем `canvas_input build otves-office office --stage mockup` |

Warning `otves-office` для полноты:

- R-COV-007 — голос, см. ниже;
- R-MAT-010 — бриф на вид закрыт, а источники первого входа (vision, user, surface, object, action, capability) —
  `draft`;
- R-MAT-001 — ДС `approved`, но карточка стиля не выбрана;
- R-FRESH-002 ×2 — вход устарел после правки `system.tokens.json` и `system.yaml`;
- R-MAT-003 — 45 строк текстов `checked`.

**Голос продукта.**

- `otves-remont-nn`: warning R-COV-007 на уровне продукта — «канал product-ui есть, а профиля голоса продукта
  voice.product.yaml нет (интерфейс: cabinet)» → `/design-deep-dive otves-remont-nn` — голос продукта. Голос бренда
  лендинга (`voice.yaml`, `draft`) прошёл `validate_voice.py` без находок.
- `otves-office`: warning R-COV-007 — «профиля голоса voice.yaml нет: поверхностям office не на что опереть тексты» →
  `/design-deep-dive otves-office` — `meaning` (голос).
- Правило чтением R-SEM-003 («свой текст голоса вместо проекции») утилита оставляет скиллу.
- Для заказчика: у кабинетов обоих продуктов нет голоса, на который опираются тексты интерфейса и проза ДС. Это
  предупреждение, а не стоп.

**Демо-факты.**

- `otves-remont-nn` — только долг, hint R-DEBT-002, три находки:
  - файл фактов продукта целиком демонстрационный (`example: true`): «макет на них допустим, перед публикацией —
    copydeck.py validate --final (0 демо-фактов)» → `meaning`, факты заказчика;
  - в `open` устаревшего манифеста у `home` 9 демо-фактов;
  - в закрытом copy deck `spasibo` есть демо-факт `company-since-2014`.
- Рядом warning R-MAT-001: copy deck `spasibo` `approved`, а факты `draft` («confirmed ставит заказчик»).
- Так и задумано: `design-audit/SKILL.md`, таблица тяжести — «hint … демо-факты»; гейт «в публикацию не уходят
  демо-факты» стоит на публикации сайта (`phases.md § 0`, `§ copy-audit` — `copydeck.py validate --final`), а не на
  аудите.
- **Не путать:** warning R-COV-003 «SB-P03: желательный вид «demo»: допущенных фактов нет — блок не строится» — это вид
  доказательства `demo` из `proof.wanted_kinds` брифа (демонстрация продукта), а не демо-данные.
- `claims_check.py lint-facts` на этих фактах даёт ERROR COPY-F-PERMISSION (`review-igor-pending`: разрешение
  `pending`), но в отчёт он не попадает. Это по замыслу: `rules.md`, R-STRUCT-003 — «публикуемость факта (разрешение,
  срок, проверка) — не дефект формы файла фактов: её сверяет R-COV-003 там, где факт стоит». Отзыв Игоря записан
  фактом с `permission: pending`, и его заметка сама предупреждает: «До письменного разрешения не публикуется: сверка
  даёт error COPY-F-PERMISSION». Ссылается на него только смысл (`meaning.yaml`), а планы и copy deck — нет, поэтому
  R-COV-003 молчит.
- `otves-office`: о демо-фактах аудит молчит — файла фактов у продукта нет. Демо-набор входа (`demo-data.json`,
  `example: true`) производный и находкой не считается.

### Находки о текстах

1. **Совет R-FRESH-006 противоречит контракту пакета.** Совет: «ready build otves-remont-nn promo — после /design-audit
   без error (этап package)». А контракт говорит иначе:
   - `phases.md § 7 → package`, «Вход»: «отчёт `/design-audit` …: его `error` — доклад заказчику, закрыть их до пакета
     или собрать с ними — решение заказчика …; жёстко пакет держит только принятый макет»;
   - `design/README.md § Пакет для кода`: «после отчёта `/design-audit` (его `error` закрывает или принимает
     заказчик)»;
   - `design-audit/SKILL.md § Формат отчёта`: «закрыть или собрать пакет с ними решает он».

   Совет делает «0 error» условием сборки манифеста. По контракту это решение заказчика.
2. **R-COV-007: одно правило — две тяжести.** `rules.md`: «R-COV-007 … `warning` — нет нужного канала или профиля
   голоса продукта». `design_audit` так и даёт — warning у обоих проектов. `canvas_input --help`: «R-COV-007 hint нет
   профиля голоса с каналом поверхности». В задаче 2 на той же ситуации (у `otves-office` нет голоса) `canvas_input`
   выдал hint. Путь в находках тоже разный: `canvas_input` — `voice.product.yaml`, `design_audit` — `voice.yaml`.
   Справка `scripts/README.md § project` обещает «один формат находок», а `rule` — это id правила аудита. Тяжесть
   расходится.
3. **Поле `ready` в `summary.json` читается как «поверхность готова».** В сводке аудита у `promo` — `"ready": true`, а
   сам `ready.yaml` пишет `status: not-ready`, обе единицы `ready: false`. У `office`, где манифеста нет, — `false`: по
   всей видимости, ключ значит «манифест есть». Ни `design-audit/SKILL.md` (состав сводки: «счёт, какие утилиты
   запускались и с каким итогом, этапы поверхностей, правила чтением …, заметки»), ни `--help` этот ключ не описывают.
4. **«Код 2» у валидатора в сводке без пояснения.** `summary.json` → `called`: `"text/claims_check.py": ["код 2"]`. В
   отчёте от него ни находки, ни заметки. У утилит `project/` код 2 значит «ошибка вызова или окружения», у текстовых
   утилит — «есть error» (так у `copydeck.py`). Справка `claims_check.py` кодов не называет вовсе. Что здесь это
   законно отброшенная ошибка публикуемости, видно только из `rules.md` (R-STRUCT-003). А `design_audit --help`
   обещает: «у находки валидатора — его уровень (error → error …)», исключения не называя.
5. **У части советов нет этапа.** `design-audit/SKILL.md § Формат отчёта` обещает: «В каждой находке — id правила и
   шаг: этап или запись `/design-deep-dive`». Без этапа:
   - error R-COV-003 (PL-F01) — только «/design-deep-dive otves-remont-nn promo»;
   - warnings R-STRUCT-002 (SB-L03) и R-COV-003 (SB-P03) — так же;
   - R-MAT-010 — «поле ядра без источника — вопрос questions[] … и долг в заметке пропусков», без исполнителя.
6. **Правила текстов в аудите молча не загружены.** Заметка «copydeck.py: правила не загружены: copy-slots.yaml нет —
   длины слотов и обязательность фактов не проверены» стоит только в конце отчёта и в `summary.json`. На вердикт и счёт
   она не влияет. Заказчик видит «9 error», не зная, что длины и обязательные факты copy deck не проверялись.
   Причина — ссылка copy deck `spasibo`, стр. 10: `copy_slots_ref: ../../04-copy-by-block/copy-slots.yaml` — путь от
   папки базы, из папки проекта он не разрешается (`voice_ref`, `facts_ref`, `meaning_ref` рядом — пути проекта).
   Битая `brand.ref` брифа — error R-REF-001, а битая `copy_slots_ref` — только заметка. Что сессии с этим делать,
   `design-audit/SKILL.md` не говорит: такой заметки нет среди «утилиты не запускались».
7. **`blockers` манифеста молчат о фактах (вопрос к тексту).** По канону (`phases.md § 7`, `design/README.md § Пакет
   для кода`) «факты подтверждены или пробел назван» — условие готовности единицы. Справка `ready`: «blockers — строка
   на причину, по которой единица … не готова». В манифесте S4A и в `ready.yaml` S4B демо-факты `home` — только в
   `open`, строки в `blockers` нет, хотя `facts.yaml` — `draft`. По выводу нельзя понять, станет ли `home` готовой с
   демо-фактами, когда план, тексты и макет закроются.
8. **Отчёт аудита чужого репозитория некуда положить.** `design-audit/SKILL.md § Что делать при запуске`, п. 7:
   «перезаписать `audit-state/<project-slug>/last-report.md`» — папка рядом со скиллом. О прогоне проекта из другого
   репозитория (`design_audit --repo`) SKILL.md не говорит: отчёт чужого проекта лёг бы в папку скилла этого
   репозитория. Здесь отчёт не писался по условию задачи.

## Сводная таблица находок о текстах

Тяжесть — для проверки текстов:

- **высокая** — тексты ведут к разным действиям;
- **средняя** — тупик или вывод обещает не то;
- **низкая** — форма вывода и справки.

Подтверждения без расхождений (путь однозначен в задачах 1 и 3, `--repo` найден в `scripts/README.md § project` и
`--help`) в счёт не входят.

| # | задача | где | что расходится | тяжесть |
|---|---|---|---|---|
| 1 | 2 | `phases.md § 0` (пять гейтов), `§ 1` строка 16, `§ 4 → Второй вход`, `§ 6 → canvas-input` «Вход», `screens/README.md § Что слой отдаёт макету`, `canvas_input --help` (R-MAT-012) ↔ `§ 6 → mockup` «С середины», R-MAT-003 | утверждённые тексты для макета кабинета: одни места пишут «вход готов: тексты `approved`» и называют это гейтом, а утилита даёт warning и «этап можно публиковать» при 45 из 53 строк-заглушек; исключение для кабинета описано только в «С середины» этапа `mockup` | высокая |
| 2 | 4 | совет R-FRESH-006 ↔ `phases.md § 7 → package`, `design/README.md § Пакет для кода`, `design-audit/SKILL.md § Формат отчёта` | «ready build … — после /design-audit без error» против «`error` закрывает или принимает заказчик»; жёсткий гейт — только принятый макет | высокая |
| 3 | 1 | совет R-COV-002 ↔ `copydeck.py --help` (`skeleton`) | «каркас из плана — copydeck.py skeleton» при существующем deck: `skeleton … -o DECK` пишет пустой каркас и затирает 32 текста; способа дополнить deck нет ни в справке, ни в `phases.md § copy` | средняя |
| 4 | 2 | `INPUT.md` «Итог проверки» ↔ `phases.md § 6 → mockup` «Вход» | «этап можно публиковать» при не принятом вайрфрейме: проверка входа не видит «принятый вайрфрейм или его пропуск» и «ДС установлена в холст», но итог сформулирован как допуск этапа | средняя |
| 5 | 2 | `INPUT.md` «Пробелы» ↔ `phases.md § 1` («голос … нужен до этапов 9 и 13») | «голоса поверхности нет … — тексты во входе уже в голосе» — противоречие; нарушенный порядок (ДС `approved` и тексты `checked` без голоса) виден только как hint | средняя |
| 6 | 3 | вывод `ds_sync check`/`build` ↔ `claude-design.md § Правки токенов` | альтернатива «если правка у всех, правьте примитив» не имеет команды: `--write` пишет только литерал роли, а совет находки ведёт сразу к `--write` | средняя |
| 7 | 3 | совет `ds_sync check` ↔ «Правки токенов», шаг 3 | «`--write`, затем `ds_build build`» без пересчёта контраста пар, обязательного по протоколу между подъёмом и пересборкой | средняя |
| 8 | 4 | `canvas_input --help` (R-COV-007 hint) ↔ `design-audit/references/rules.md` R-COV-007 (`warning` — «нет … профиля голоса продукта»), вывод `design_audit` | одно правило, две тяжести: на одной и той же ситуации «у кабинета нет голоса» `canvas_input` даёт hint, аудит — warning; путь в находке тоже разный (`voice.product.yaml` / `voice.yaml`) | средняя |
| 9 | 4 | `summary.json` аудита ↔ `ready.yaml` | `"ready": true` у `promo`, чей манифест `not-ready`; ключ не описан ни в `design-audit/SKILL.md`, ни в `--help` | средняя |
| 10 | 4 | `summary.json` → `called` ↔ `design_audit --help` («у находки валидатора — его уровень») | `claims_check.py: код 2` без находки и заметки: ошибка COPY-F-PERMISSION отброшена по `rules.md` R-STRUCT-003, но справка исключения не называет, а «код 2» у текстовых и `project/` утилит значит разное | средняя |
| 11 | 4 | заметка сводки ↔ `design-audit/SKILL.md § Два прогона` | «copydeck.py: правила не загружены: copy-slots.yaml нет» — из-за неразрешимой `copy_slots_ref` длины и обязательные факты не проверены, но это не находка (битая `brand.ref` — error R-REF-001), на вердикт не влияет, что делать — не сказано | средняя |
| 12 | 1 | сообщение R-DEBT-002 (`canvas_input`) | «демо-факты во входе: 10 (…)» — названо 6, без «и ещё 4»; соседние находки хвост пишут | низкая |
| 13 | 1 | R-COV-002 ↔ `INPUT.md` «Пробелы» | «слоты плана без текста» против «слотов плана без слота copy deck» — разные утверждения; «52 текстовых слотов», «2 текст(ов)» | низкая |
| 14 | 1 | `copydeck.py --help` ↔ `scripts/README.md § project` | коды выхода: у `copydeck.py` 2 — «есть error», 1 — «ошибка входа»; у утилит `project/` — наоборот | низкая |
| 15 | 2 | вывод `canvas_input`/`contract` ↔ `canvas_input` сайта | хвост списка в двух видах: «… (+40)» и «и ещё 46» при «одном формате находок» | низкая |
| 16 | 3 | вывод `ds_sync check` ↔ смысл R-FRESH-001 у `ds_build`/аудита | законная правка заказчика названа «error R-FRESH-001» — тем же id, что брак «производные не равны сборке» | низкая |
| 17 | 3 | `ds_coverage show` ↔ его `--help` | нет строки заголовка, колонки не те, что в справке («тип, где стоит, ключ, компонент»); экранов «где стоит» нет | низкая |
| 18 | 3 | `lib/color.py --help` (утилита из `phases.md § design-system`) | мёртвый путь «`sys.path.insert(0, ".../99-raw/tools")`» и след истории «написано агентом A волны 1» | низкая |
| 19 | 4 | советы находок ↔ `design-audit/SKILL.md § Формат отчёта` («шаг: этап или запись») | без этапа: error R-COV-003 (PL-F01), warnings R-STRUCT-002 (SB-L03), R-COV-003 (SB-P03); R-MAT-010 — без исполнителя | низкая |
| 20 | 4 | `ready --help` («blockers — строка на причину … не готова») ↔ `phases.md § 7` («факты подтверждены или пробел назван») | демо-факты `home` — только в `open`, в `blockers` о фактах ни строки при `facts.yaml` `draft`; по выводу не понять, держат ли они готовность | низкая (вопрос) |
| 21 | 4 | `design-audit/SKILL.md § Что делать при запуске`, п. 7, ↔ `design_audit --repo` | отчёт `last-report.md` пишется рядом со скиллом (`audit-state/<slug>/`), а о проекте в другом репозитории (`--repo`) SKILL.md молчит: отчёт чужого проекта лёг бы в папку скилла этого репозитория | низкая |

**Итого находок о текстах: 21**: высоких — 2, средних — 9, низких — 10.

Отдельно — наблюдения по данным демо: утилиты их не ловят, в счёт они не входят.

- S1: `hierarchy`, `art_direction_ref` плана и `*_ref` copy deck ведут на примеры базы; осведомлённость в плане,
  copy deck и манифесте входа не совпадает.
- S4A: у ДС нет `system.tokens.json`, `system.tokens.css` и `DESIGN.md`.
- S4B: футер плана `spasibo` ссылается на пробел `legal-details` как на факт (`fact:`, а не `missing:`).
