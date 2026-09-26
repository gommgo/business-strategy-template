# Copy deck: от черновика до утверждения и пакета исполнителя

Волна 3 · агент J (фаза 2 — J3) · 2026-09-24 · внешних источников 0 (процесс собран по файлам базы и соседей: I 02–03,
`copy-checklist.yaml`, B2, C, E, F, G, H, kimi, ai-media) · опыты `99-raw/experiments/J/01–08` · формат —
`copy-deck.schema.json` v1.1 · утилита — `../../scripts/text/copydeck.py`.

Copy deck — единственное место текста страницы. Статус слота — статус выбранного варианта; статус меняют только
утилита (`draft → checked`) и человек (`checked → approved`, выбор варианта, отказ). Руками `copy.md`, `facts.md`,
`checked` и `approved` не пишутся.

## Выжимка для агента

1. **Факты до текста**: сначала `facts.yaml` (B2, анкета `proof-intake`), потом тексты; у каждого числа, имени, даты,
   цитаты, рейтинга, цены и гарантии — `fact_ids`; факта нет — `[PLACEHOLDER: что именно]` + `missing_ids`. `[проверено: J/02, I/04]` все → §1
2. **Пробел действует по `fallback`**: `placeholder` — заглушка на странице; `rewrite-without` — текст без утверждения;
   `omit-block` — слот или секцию снять до ответа. Заглушка при `omit-block` — `COPY-D-FALLBACK`. `[проверено: E/04, J/07]` все → §1.3
3. **Порядок проверок — claims → lint → validate** (решение оркестратора): стиль не правят в тексте, который ещё изменится
   из-за фактов; `copydeck.py check` делает все три в этом порядке. `[практика]` все → §2
4. **`draft → checked` ставит только утилита**: `check --update OUT --promote` при 0 error сверки и линтера; в записи
   `lint` и `claims` — `text_hash` проверенного текста. `[проверено: J/01, J/03]` все → §1.2
5. **Правка после проверки снимает статус**: другой `text_hash` → `COPY-D-HASH` error; перепроверьте или верните `draft`. `[проверено: J/03]` все → §1.2
6. **`checked → approved` — только человек**: `approve --page ID --by <роль или имя>`; `review.by` со словом «copydeck»
   утверждением не считается; с заглушкой, без мета или с устаревшей записью — отказ. `[проверено: J/01]` все → §3
7. **Судья статус не меняет** (COPY-C-20): рубрика — сигнал для человека, голос и «интересно» — только человек. `[исследование: I 03]` все → §3
8. **Код ловит числа и условия, судья и человек — утверждения без чисел**: «Срок и смета — в договоре» прошло сверку,
   поймал вопрос COPY-R-03 q1. `[проверено: I/04]` все → §3
9. **Отказ — с причиной**: отклонённый вариант остаётся в deck со `status: rejected` и `reason` — это пары «до / после»
   и вход правки промтов I. `[практика]` все → §4
10. **Варианты сверяются «как выбранные»**: `check --all-variants` сверяет каждый живой невыбранный вариант копией
    страницы с одной заменой; отклонённые не сверяются; итоги варианта не трогают статус выбранного. `[проверено: J/07]` все → §4.2
11. **У варианта свои факты — `variant.fact_ids`** (v1.1): список заменяет факты слота; при `check --update` факты
    выбранного варианта переносятся в слот. `[проверено: J/07]` все → §4.1
12. **Выбирает человек вслепую**: `export-variants` — лист A/B/C без моделей и авторов (мета — тоже), варианты с error в
    `checks` на лист не идут; итог — `chosen` + `selection {method, by, at, compared, tally, ref}`. `[практика: I 02 §3.2]` {landing, meta} → §4.3
13. **Правка по находкам — кластерами**: ≤ 5 кластеров на 300 слов прозы за проход, ≤ 3 прохода, после каждого —
    `check`; каждое изменение — новый вариант, старый `rejected` с причиной, запись `edit_log`. `[практика: C §9; проверено: I/04]` все → §5
14. **`lint_allow` снимает только находки линтера** C, с причиной; ART и CNT не снимаются; находки сверки (`COPY-F-…`,
    `COPY-L-…`) и формата (`COPY-D-…`) — только правкой текста или `facts.yaml`. `[проверено: I/04]` все → §5.2
15. **Два пути линтера расходятся на мета**: `copy_lint.py` на copy deck не читает `meta.fact_ids` (число в title —
    ложный `an-number-without-fact`), `copydeck.py lint` читает и пишет, сколько таких находок снял. Ворота — `copydeck.py check`. `[проверено: J/05, J/07]` {meta} → §2.2
16. **Длина — сигнал, не ворота**: `COPY-D-LEN` (E) и ядро первого экрана > 40 слов (`COPY-D-HERO-CORE`) — warning;
    чаще это слот не того типа (число и подпись в одном `stat-value`). `[проверено: J/01]` {landing} → §2.1
17. **Обещание первого экрана — текст страницы**: поле `promise` (свои варианты или `from` на слот) уходит в
    `product.goal` kimi → «Promise:» в TASK.md; сверяется как подзаголовок hero. Без обещания лендинг не выгружается. `[проверено: J/02]` {landing} → §7
18. **Поля брифа — тоже текст**: `goal`, `primary_action`, `description`, `cta.label` сверяются как страница (error);
    jobs секций и `target_user` — сигнал (warning). `[проверено: J/01, J/02]` {landing} → §7
19. **Второй язык — отдельный copy deck** с `lang`, `source_lang`, `source_ref`, `adaptation.mode: adaptation` и своим
    `facts.yaml` на языке страницы с теми же id; перевод русского факта в `translations.en` сверку не спасает (объект
    счёта остаётся русским). `[проверено: E/03, I/04, J/08]` все → §6
20. **Пакет kimi — только `export-kimi --strict`** из утверждённой страницы; затем `build_package.py build` и `check`;
    «no em dashes» kimi для русского не переносится — строка «Typography is final…». `[проверено: J/04, J/08]` {landing} → §7
21. **Проверка `fact-source` в kimi слепа к id B2**: строка `| rating-… |` с пустым источником проходит `build_package.py
    check`; ворота честности — в copy deck. `[проверено: J/04]` {landing} → §7
22. **Тексты при картинках — слоты с `asset_ref`**: `image-alt`, `image-caption`, `in-image-text` (≤ 40 знаков, ≤ 3 строки
    на ассет); `export-assets` отдаёт их в план ассетов ai-media, в `copy.md` строки в картинке не идут (норма ai-media —
    `../../ai-media/05-prompting/03-asset-spec-and-dialects.md` §7) все → §8
23. **Собранную страницу сверяют с copy deck**: доля блоков не из `copy.md` > 10 % или число вне `facts.md ∪ copy.md` —
    стоп (образец — `k3_checks.py` F-COPY, F-NUMBERS); команды `verify-page` пока нет. `[не проверено]` {landing, site-page} → §9
24. **Перед публикацией** — `validate --final` (0 заглушек, страница `approved`, мета заполнена), флаги права высокого
    риска прочитаны юристом (COPY-C-34), ключевые слоты — в макете на 1440 и 390 px (COPY-C-33). все → §3

## 1. Статусы и переходы

### 1.1. Таблица переходов

| Переход | Кто | Команда | Обязательно до перехода | Что блокирует |
|---|---|---|---|---|
| — → `draft` | модель (P4, P5 цепочки I), агент ai-self, редактор, импорт | `import-kimi`, `upgrade` (v0 → v1), скелет I `make_skeleton.py` | `slot_id`, `slot_type`, `variants[{id, text, status}]`; при 2+ вариантах — `chosen` | — |
| `draft → checked` | утилита | `check DECK --update OUT --promote` | 0 error claims и lint у текста; записи `lint`, `claims` с `text_hash`; факты находятся и публикуемы | error сверки (факты, право), error линтера, `COPY-D-FACT-REQUIRED` у checked |
| `checked → approved` | человек (заказчик, редактор) | `approve DECK --page ID --by КТО -o OUT` | все выбранные тексты checked, актуальный `text_hash`, 0 `[PLACEHOLDER]`, `meta.title` и `description` | заглушка, устаревшая запись, пустая мета |
| вариант → `rejected` | человек или правка по находкам (код I `apply-edits`) | правка YAML (`status: rejected`, `reason`) | `reason` (v1: без него — error `COPY-D-REJECTED`) | выбранный отклонённый вариант — error |
| страница → `rejected` | человек | правка YAML | `reason` | страница не проверяется и не выгружается |
| `approved → draft` | правка текста | правка YAML | — | `COPY-D-HASH` до перепроверки |

Статус страницы не выше статуса её слотов (`COPY-D-STATUS`). `checked` на странице ставит человек или процесс после того,
как все её тексты checked; `approved` — `approve` сам (страница + все тексты + `approval {by, at}`).

### 1.2. Что держит статус

- `text_hash` — sha1 нормализованного текста (пробелы, NBSP), 12 знаков; пишется в `lint` и `claims` слота при
  `--update`. Текст правили — хэш не совпал — статус недействителен (`COPY-D-HASH`, error у v1, warning у v0).
- Запись проверки устарела (в файле 0 error, свежая сверка даёт 2) — info `COPY-D-RECORD`; перед `approve` —
  `check --update` заново.
- `review` у варианта: при `--promote` — `{by: "copydeck.py check --promote", at}`; при `approve` — роль или имя
  человека. Утилита не может утвердить: validate отличает эти записи.

### 1.3. Пробелы и fallback (B2)

| `fallback` пробела | До ответа заказчика | Что ловит |
|---|---|---|
| `placeholder` | `[PLACEHOLDER: …]` дословно как `missing[].placeholder` + `missing_ids` слота | `COPY-F-PLACEHOLDER-UNLISTED` (claims), `art-placeholder-marker` (lint, с `--final` — error), `COPY-D-PLACEHOLDER` (approve, `--final`) |
| `rewrite-without` | текст без этого утверждения (не заглушка) | `COPY-D-FALLBACK` warning |
| `omit-block` | слот или секция сняты | `COPY-D-FALLBACK` warning |

Пробел решает объём страницы: в I/04 `rewrite-without` и `omit-block` сняли «один прораб» из первого экрана, карточку
«ход работ виден» и 3 из 5 вопросов FAQ; расширить страницу может только ответ заказчика. До правки J3 `check` не
показывал `COPY-D-FALLBACK` (его видел только `validate`, E3) — исправлено: пробелы проверяются при любом прогоне. `[проверено: J/07]`

## 2. Проверки на каждом переходе

### 2.1. Что ловит каждая

| Шаг | Утилита | Ловит | Не ловит |
|---|---|---|---|
| 1. claims | `claims_check.py` (B2 + право H: 66 правил `COPY-L-…`), через `copydeck.py claims` на плоской копии | число без факта или шире факта, имя, цитата без разрешения, истёкший факт, вывод вместо факта, `never_claim`, класс утверждения без факта, условие «рядом» (`requires_nearby`), «лучший» без критерия, «бесплатно» без условия, сроки возврата против ЗоЗПП | утверждения без чисел и маркеров («смета в договоре») — только `--strict` (шумно) и судья |
| 2. lint | `copy_lint.py` (C, 336 правил) через `lint_text` по слоту + проход страницы | штампы, пустые эпитеты, артефакты чат-бота, «не X, а Y», ритм, плотность тире и маркеров, надзаголовки, `an-number-without-fact` без `fact_ids`, правила мета и GEO G | факты, право, смысл |
| 3. validate | `copydeck.py validate` | схема, id, статусы и `text_hash`, словарь, пробелы и `fallback`, обещание, главная кнопка, мета (G `meta-x-…`), длины и `fact_required` (E), голос (F `vocabulary.avoid`, обращение), флаги права (H), язык, ассеты | качество текста |

Коды выхода всех команд: 0 — нет error, 2 — есть error, 1 — ошибка входа. Уровни: error — ворота; warning — прочитать и
решить; info — справка.

### 2.2. Два пути до одного результата

Порядок E для примеров и цепочки I: `claims_check.py --legal-category <отрасль>` → `copy_lint.py` → `copydeck.py check`
и `validate`. Результаты сходятся, кроме трёх мест (J/05, J/07):

| Место | `claims_check.py` / `copy_lint.py` на copy deck | `copydeck.py` |
|---|---|---|
| `meta.fact_ids` | линтер не читает: число в title — `an-number-without-fact` (6 находок у «Отвеса» v1 в J/05, 7 на трёх примерах J/08) | читает; в `tools.lint.parity_copy_lint` — сколько снято (7 у «Отвеса» v1) |
| обещание `promise`, OG-шаблон, `og_image_alt` | не видят | сверяет и линтует |
| свои `fact_ids` варианта | не читают (только слот) | читает; `check --update` переносит факты выбранного в слот |

Ворота — `copydeck.py check`; прямые прогоны нужны как контроль и для страниц без copy deck. Предложение C: параметры
`fact_ids` и `allow` у `lint_text`, чтение `meta.fact_ids` в режиме copy deck.

## 3. Точки человека (цепочка I: S1–S11)

| Точка I | Что решает человек | Где в copy deck | Пункты `copy-checklist.yaml` |
|---|---|---|---|
| S2 анкета фактов | ответы, документы, разрешения, что нельзя обещать | `facts.yaml` (`source.quote`, `permission`, `never_claim`), `missing[].fallback` | C-35 |
| S3–S4 смысл, иерархия | «беру по умолчанию»; какая иерархия под какой трафик | `page.hierarchy_ref`, `awareness`, `section.message`, `question` | — |
| S8 проверки → `checked` | ничего: код | записи `lint`, `claims`; `--promote` | C-01, 02, 03, 05, 06, 08, 13; C-07 длина — сигнал |
| S9 правка | остаток после 3 проходов: пробелы, типичность отзыва, спорное право | `notes` слота, `edit_log`, `lint_allow` с причиной | C-17 |
| S10 судья | читает ответы судьи с цитатами; статус не меняет | `variant.checks.rubric` | C-20…24 (сигнал) |
| S11 выбор | заголовок, оффер, кнопка, title — слепо, 2–4 варианта | `chosen`, `selection` | C-32 |
| утверждение | голос, естественность, «интересно»; нет warning в headline, subheadline, cta-label, мета | `approve --by` → `approval`, `review` | C-11, C-30, C-31 |
| публикация | 0 заглушек; флаги права высокого риска — юрист; макет 1440 и 390 px | `validate --final`; `export-kimi --strict`; сверка собранной страницы (§9) | C-04, C-33, C-34 |

Люди из аудитории (5-секундный тест, cloze, тест сообщения — C-40…42) и A/B (C-43) — живая фаза, после публикации.

## 4. Варианты и слепой выбор

### 4.1. Сколько вариантов и откуда

- По I: headline и subheadline — 3, cta-label — 2, meta-title — 3 (G 07/02 §4.3: 2–3 варианта title с планом теста),
  остальное — 1. Каждый вариант — `source` (`ai-self`, `model`, `human`, `customer`, `voc`, `fact`) и для `model` —
  `generated {model, channel, prompt_ref, run_id, date, params, technique}`.
- Вариант опирается на другие факты, чем слот («Смета до договора — бесплатно…» против «гарантия 3 года») — свои
  `fact_ids` у варианта. Без них сверка даёт `COPY-F-EXTENDS` «шире факта» (I/04, вариант `hero/lead c`). `[проверено: J/07]`
- Альтернативы мета — `meta.variants.<поле>[]`, выбранный текст — строкой в `meta.<поле>`; `test_plan` обязателен при 2+
  вариантах title (info `COPY-D-META-VARIANTS`).

### 4.2. Проверка вариантов до выбора

`check DECK --all-variants --update OUT`: выбранные тексты — как обычно (записи слота, статусы); каждый живой
невыбранный вариант и альтернатива мета сверяются копией страницы с одной заменой (соседний вариант не закрывает
`requires_nearby`, отклонённые не сверяются), итоги — в `variant.checks {claims, lint}` того варианта. До правки J3
режим сверял отклонённые варианты и суммировал их находки в статус выбранного (I/04: 4 error, из них 3 — на `rejected`);
после — 1 error на варианте с чужими фактами, 0 — с `variant.fact_ids`. `[проверено: J/07]`

### 4.3. Слепой выбор и запись выбора

1. `export-variants OUT.yaml -o sheet.md --key key.yaml --seed N` — слоты с ≥ 2 живыми вариантами, метки A, B, C в
   воспроизводимом случайном порядке; модели, `source` и `generated` скрыты; мета — под своим путём (`<page>/meta/title`,
   выбранный сейчас текст без варианта — id `meta`); варианты с error в `checks` сняты (в ключе — комментарием;
   `--include-failed` — показать).
2. Человек выбирает (заказчик — COPY-C-32; попарно — порядок меняется между показами). Судья после калибровки — только
   сигнал (C-22: согласие с заказчиком ≥ 0,8).
3. Запись — правкой YAML: `chosen: <id>`, `selection {method: customer | human-pairwise | editor | judge-pairwise,
   by, at, compared: [ids], tally: {id: голоса}, ref: <путь к листу и ключу>, rationale}`; для мета — выбранный текст в
   `meta.<поле>`. Команды, которая вернёт голоса в deck, нет (пробел `apply-selection`).
4. Невыбранные варианты остаются `draft` (можно вернуться); `rejected` — только с причиной («проиграл слепой выбор 1:5»).
5. После выбора — `check --update --promote`: выбор сменил текст слота, прежние записи недействительны (`COPY-D-HASH`).

## 5. Правка по находкам

### 5.1. Протокол (C §9, I 02 §4)

1. Проход 1 — все error: число без факта → `fact_ids` и формулировка факта или `[PLACEHOLDER]` + вопрос заказчику;
   другое число не подставляется. Итерации до 0 error.
2. Проходы 2–3 — warning кластерами (слот и предложение; семья правил с наибольшим числом находок): ≤ 5 кластеров на
   300 слов прозы; у короткого слота (заголовок, кнопка, строка у кнопки, мета) — одна правка за проход.
3. Порядок: удалить → заменить фактом → сказать проще. Синоним из того же ряда и двоеточие вместо каждого тире — не правка.
4. Стоп: `clean` или `review` без warning в headline, subheadline, cta-label и мета; после прохода 3 остаток — человеку.
5. Новый текст — новый вариант (`chosen` на него), старый — `rejected` с `reason: "правка по находкам: <правила>"`,
   запись `edit_log {pass, rules, clusters, by, date, from_variant, to_variant}`.

I/04: черновик по промтам — 3 error, 20 warning; проход 1 — 4 правки (одна склеила два факта в OG → новая
`COPY-F-EXTENDS`); проход 2 — 0 правок текста. E/04: 2–4 прохода на страницу, стилевых находок линтера — 0 (тексты из
проверенных образцов E). `[проверено: I/04, E/04]`

### 5.2. Ложные находки

- Линтер — `lint_allow: [{rule, reason}]` в слоте (страницы — у страницы): находка уходит в `notes` и в счёт
  `suppressed`; ART (артефакты) и CNT (данные) не снимаются.
- Сверка и право — правкой: «аренда и ипотека идут одновременно» (голос клиента) → `COPY-F-CLASS` income-finance;
  снимается переформулировкой без слова-маркера или уходит человеку с минимальным примером для B2.
- Системные warning B2, которые текстом не правятся: `COPY-F-USE` на мета, OG, FAQ, how-it-works (в `use` фактов нет
  этих мест — 14 из 18 оставшихся warning I/04), `COPY-F-TYPICALITY` у отзыва о сроке (нужны данные «как обычно»).
  Их читают, но не лечат.

## 6. Второй язык

- Отдельный copy deck: `lang: en`, `source_lang: ru`, `source_ref: <путь к RU deck>`, `adaptation {mode: adaptation,
  audience_note}`; `page_id`, `section_id`, `slot_id` — те же, что в исходнике (creative и site ссылаются на пути).
  `adaptation.mode: translation` — warning (решение заказчика п. 16).
- Свой `facts.yaml` на языке страницы с теми же id фактов и пробелов (`lang: en`, `verbatim`, `values[].what`,
  `qualifier`, `use.requires_nearby` по-английски), пометка ДЕМО у демо-наборов. Почему не `translations.en` в русском
  файле: сверка сравнивает объект счёта с русским `values.what` (I3: «1,146 apartments…» → `COPY-F-NUM-MISMATCH` и с
  `translations.en.canonical`), «1,380» читается как 1,38, `requires_nearby` — одноязычный (E/03, F/05, I/04).
- Голос: тот же профиль F (`voice_ref`); английский словарь «не говорим» — оверлей F (`99-raw/experiments/F/04-voice-samples/en-overlays/`);
  без него английские приметы бренда проверяет человек (F: «человек обязателен для английских страниц»).
- Адаптация, а не перевод: реалия объясняется одной вставкой («Yandex Maps, the local maps and reviews app»), цены —
  в рублях у российской компании (38-ФЗ ст. 5 ч. 7.1, H), обращение — «you» без «dear customer»; длины — по EN-колонкам E.
- Выгрузка: `export-kimi` пишет `Voice:` из профиля, Never claim — английские строки умолчаний B2 (`NEVER_EN`, ai-self J);
  строки «Typography is final…» для EN нет.

## 7. Выгрузка в пакет kimi

1. `approve` → `validate --final` (0 error) → `export-kimi DECK --page ID --strict --out pkg/ [--merge-into brief.yaml]
   [--meaning meaning.yaml] [--facts-scope used]`.
2. Ворота выгрузки: `validate` всей deck + `validate --final` выгружаемой страницы (при `--strict`) + сверка claims
   страницы и обещания + сверка полей брифа (`goal`, `primary_action`, `description`, `cta.label` — error; jobs и
   `target_user` — warning). Без обещания — отказ (`COPY-D-PROMISE`).
3. Что куда: `copy.md` — секции `## <section_id>`, ключи `[slot_id]: текст`, блок `## head` с мета; alt и подписи файлов
   `assets/…` — в `brief.yaml assets[]`; строки в картинке — только в план ассетов; `facts.md` — публикуемые факты (по
   `x-kimi-map` B2), пробелы, Never claim строками (снятие по классу опубликованного факта); `brief-fragment.yaml` —
   `product.goal` ← `promise`, `primary_action`, `site.cta.label`, `site.sections[{id, job}]` (job = «вопрос → сообщение»;
   id фактов — только `--job-facts`), `content.*_source`; с `--meaning` — `target_user`, `description`, отвеченные вопросы.
4. Пакет: `build_package.py build <brief.yaml> <папка> --templates <копия templates>` и `check <папка> --brief <brief.yaml>`
   в копии шаблонов kimi (Kimi не запускается). J/04: оба пакета — 0 разрывов покрытия, 0 error; warning — длина
   TASK.md 5 093–5 887 знаков. Слепое пятно kimi: `fact-source` проверяет только id вида `F1`. `[проверено: J/04, J/08]`

## 8. Строки для плана ассетов

`export-assets DECK --page ID -o plan.yaml` → фрагмент плана ai-media (01/01 §8): `slots[{id: asset_ref, alt, caption,
text: {mode: in_image, strings[{text, language, script, role}], fallback: html_overlay, ocr_check: true}}]`, `og {alt,
template_text {kicker, title}}`. Правила текста: строка в картинке ≤ 40 знаков, 1–4 слова, ≤ 3 строки на ассет
(ai-media 05/03 §7) — `COPY-D-IN-IMAGE`; кириллица в картинке — info и OCR-проверка; alt без «фото / изображение»,
декоративная картинка — `alt: ""` с пометкой в `notes` (10/01 §8); подпись без ассета — `COPY-D-ASSET`. Факты в alt и
подписи — только из `facts.yaml` (подпись «Порт USB-C в основании» — утверждение свойства).

## 9. Проверка собранной страницы (спецификация `verify-page`, команды нет)

Вопрос 4 фазы 1 и пункт COPY-C-33 I ссылаются на сверку «страница против copy deck». Спецификация:

1. Вход: URL или сохранённый HTML собранной страницы, copy deck, `--page`, `facts.yaml`.
2. Текст страницы по блокам — `copy_extract.py` D (`-o page.json`, `--html` для файла; браузер — под блокировками базы).
3. Сопоставление: блок страницы ↔ выбранный текст слота по нормализованной строке (пробелы, NBSP, типографика) и
   подстроке; слот не найден — «потерян»; блок без слота — «добавлен исполнителем».
4. Ворота (образец — `../kimi-research/99-raw/tools/k3_checks.py`, только чтение): доля блоков не из `copy.md` > 10 % —
   error (F-COPY); число на странице вне `facts.md ∪ copy.md` — error (F-NUMBERS); мета страницы ≠ `## head` — warning;
   обещание не в первом экране — warning (ACCEPTANCE A3 kimi).
5. Выход — `--json` в формате `copydeck.py` (находки `COPY-D-VERIFY-…` по путям слотов) → вход COPY-C-33 и живого
   теста J-1 (≥ 95 % блоков из `copy.md`).

До команды: сверка глазами по `copy.md` и шоту kimi `shot.py` (1440 и 390 px).

## 10. Сквозной пример — одна страница

```bash
# из корня базы; страница — пример кейса, факты — набор B2 «Отвес»; копии deck в out/ — пути переписываются сами
T=../../scripts/text/copydeck.py; D=10-templates-recipes/examples/ru-otves-case.yaml; P=case-sormovo-54; O=out
F=02-strategy-messaging/examples/facts-service-renovation.yaml
python3 ../../scripts/text/claims_check.py check $D --facts $F --legal-category general --today 2026-09-24   # 1. факты и право
python3 ../../scripts/text/copy_lint.py $D                                                                    # 2. стиль (контроль)
python3 $T check $D --today 2026-09-24 --update $O/d.checked.yaml --promote                            # 3. всё + draft → checked
python3 $T check $D --all-variants --update $O/d.variants.yaml                                          # варианты с checks
python3 $T export-variants $O/d.variants.yaml -o $O/sheet.md --key $O/key.yaml --seed 1                 # лист выбора
python3 $T approve $O/d.checked.yaml --page $P --by "заказчик" -o $O/d.approved.yaml                   # человек
python3 $T validate $O/d.approved.yaml --final                                                          # перед публикацией
python3 $T export-kimi $O/d.approved.yaml --page $P --strict --out $O/pkg --merge-into brief.yaml      # пакет
python3 $T export-assets $O/d.approved.yaml --page $P -o $O/assets-plan.yaml                            # ассеты
```

Настоящие прогоны примеров — `02-examples-ru.md` §3–§6 и `03-examples-en.md` §4–§5; пакет kimi — опыт J/08
(`run_case_package.sh`).

## Частые ошибки

- **Выдуманная конкретика**: модель ставит «12 лет» (вывод из «с 2014 года»), «сотни клиентов», «за 2 недели» — число без
  записи `facts.yaml`. Лечение: `fact_ids` или `[PLACEHOLDER]`, никогда другое число.
- **Заглушка там, где пробел велит молчать**: `[PLACEHOLDER]` при `fallback: omit-block` — страница показывает дыру вместо
  того, чтобы снять блок (`COPY-D-FALLBACK`).
- **Статус руками**: `status: checked` без записей `lint` и `claims` — `COPY-D-STATUS`; `approved` от имени агента —
  утверждением не считается.
- **Правка без перепроверки**: текст поменяли после `approve` — `COPY-D-HASH`; страница снова требует `check` и человека.
- **Сверка всех вариантов одним списком фактов**: вариант с другими фактами получает «шире факта» — нужны `variant.fact_ids`.
- **`lint_allow` на находку сверки**: не работает и не должен; ложную находку сверки правят текстом или передают B2.
- **Медианный текст после правки**: «синоним из того же ряда» и двоеточие вместо тире — сверхкоррекция; правка —
  удалить, заменить фактом, сказать проще.
- **Правило чужого жанра**: «hero ≤ 7 слов» kimi — про заголовок первого экрана лендинга, не про статью; «no em dashes» —
  правило английского текста.
- **Калька при втором языке**: перевод русского deck дословно с русскими фактами — ложные `NUM-MISMATCH`, «dear
  customer», реалии без объяснения.
- **Мета без фактов**: число в title без `meta.fact_ids` — `an-number-without-fact`; один title без вариантов у страницы
  из поиска — info G.

## Чек-лист

- [ ] У каждого числа, имени, даты, цитаты, рейтинга, цены, гарантии — `fact_ids` (или свой список у варианта)?
- [ ] Каждый `[PLACEHOLDER]` совпадает с `missing[].placeholder`, а пробелы с `rewrite-without` и `omit-block` не стоят заглушкой?
- [ ] `copydeck.py check` — 0 error; прямые `claims_check.py --legal-category` и `copy_lint.py` прочитаны?
- [ ] `checked` поставлен `check --update --promote`, а не руками; `text_hash` актуален?
- [ ] Отклонённые варианты — с `reason`, выбор — с `selection`?
- [ ] Варианты сверены `check --all-variants`, на листе выбора нет вариантов с error?
- [ ] В headline, subheadline, cta-label и мета нет warning линтера (C-11)?
- [ ] Голос, естественность и «интересно» подтвердил человек (C-30, C-31)?
- [ ] `approve --by` — человек; `validate --final` — 0 error?
- [ ] Обещание (`promise`) и поля брифа прошли сверку при выгрузке?
- [ ] Второй язык — свой deck и свой `facts.yaml` с теми же id, `adaptation.mode: adaptation`?
- [ ] Пакет kimi собран `export-kimi --strict` → `build_package.py build` и `check` — 0 error?
- [ ] Строки в картинках ≤ 40 знаков и ≤ 3 на ассет, ушли через `export-assets`?
- [ ] Собранная страница сверена с copy deck (≥ 95 % блоков из `copy.md`, числа только из фактов)?

## Открытые вопросы и противоречия

- **`verify-page` не написана** (§9) — COPY-C-33 I ссылается на неё; до команды сверка глазами.
- **Команды выбора нет**: голоса слепого выбора переносятся в `chosen` и `selection` правкой YAML (пробел `apply-selection`).
- **`COPY-F-USE` на мета, OG, FAQ, how-it-works** — формат `use` фактов B2 не знает этих мест: warning остаются на
  законных текстах (I/04 — 14 из 18, E/04 — 4–7 на страницу). Предложение B2: места мета и FAQ в `use`.
- **`claims_check.py --all-variants` у B2** по-прежнему сверяет отклонённые варианты и считает соседние варианты текстом
  «рядом»; `copydeck.py` обходит это копиями страницы, прямой прогон — нет (предложение B2).
- **Длины E на законных формах** (`case-title` 15–17 слов, тариф «Сеть» 4 знака) дают `COPY-D-LEN` — сигнал, не ворота;
  граница уточнится с корпусом D.
- **`fact-source` kimi** не видит пустой источник у id B2 — ворота честности держит copy deck (предложение kimi).
- **Судья и человек**: I относит «сюжет заголовков» (COPY-R-07) к судье, E — «ярлыки-конвенции» не штрафовать; в процессе
  это сигнал до калибровки (LT-04 живой фазы).

## Источники

- [S1] I (волна 3), `09-ai-generation-evaluation/02-generation-pipeline.md` §1, §3–§5 — цепочка S1–S11, точки человека,
  протокол правки, числа I/04; `03-evaluation.md` §2.2–2.3; `copy-checklist.yaml` v1.1 (32 пункта). Опыт, ai-self.
- [S2] B2 (волна 1), `02-strategy-messaging/facts.schema.yaml` (`missing[].fallback`, `x-kimi-map`, `x-never-claim-defaults`),
  `proof-intake.md` — факты, пробелы, публикуемость.
- [S3] C (волна 1), `06-anti-slop/02-linter-spec-and-profiles.md` §9 (правка кластерами, `lint_allow`), `copy_lint.py` 0.9.3.
- [S4] E (волна 2), `04-copy-by-block/copy-slots.yaml` (длины, `fact_required`, `hero-core`), опыт E/04 (три страницы, протокол правки).
- [S5] F (волна 2), `05-voice-editorial/voice.schema.yaml`, профили `examples/voice-*.yaml`, EN-оверлеи F/04.
- [S6] G (волна 2), `07-seo-geo-copy/meta-rules.yaml` (лимиты, шаблоны, `checks_outside_linter`), 07/02 §4.3 (варианты title).
- [S7] H (волна 2), `08-russian-legal-typography/claims-rules.yaml` (66 правил), 01 §6 и §8 (оговорки, продавец).
- [S8] kimi, `../kimi-research/07-brief-handoff/templates/` (`copy.md`, `facts.md`, `brief.yaml`, `build_package.py`),
  `../kimi-research/99-raw/tools/k3_checks.py` (F-COPY, F-NUMBERS) — только чтение.
- [S9] ai-media, `../ai-media/05-prompting/03-asset-spec-and-dialects.md` §7, `10-web-integration/01-images-delivery.md` §7–8,
  `01-web-assets-landscape/01-asset-slots-by-page-type.md` §8.
- [S10] D (волна 1), `copy_extract.py` — текст страницы по блокам (основа `verify-page`).
- [S11] Опыты J: `99-raw/experiments/J/01…08` (README у каждого); E/04; I/04.
