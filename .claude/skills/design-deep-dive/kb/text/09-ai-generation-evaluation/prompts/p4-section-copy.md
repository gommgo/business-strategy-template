# P4 · Текст секции по слотам: факты, голос, «факт → ситуация клиента», варианты

Волна 3 · агент I2 · 2026-09-24 · промт `p4-section-copy@1` (RU и EN; режимы `write` и `adaptation`) · `[не проверено]` ·
живой тест — LT-01, LT-02 (B1-1, B2-1, H1, W2-4), LT-03 (C2, V1, W1-4) в `../live-test-plan.md` · опыт
`99-raw/experiments/I/04-chain-manual/` (шаги S6, S7)

Шаг S6 цепочки `../02-generation-pipeline.md`: одна секция copy deck за вызов — все её слоты сразу (заголовок, лид,
карточки, кнопка), чтобы заголовок и тело говорили одно. Правила слота — карточка из `../../04-copy-by-block/copy-slots.yaml`
(E), голос — `projections.prompt_brief` профиля F, факты — только проекция `facts.yaml` секции (B2), право — заголовки и
замены правил H из `copy-slots.yaml → legal_rules`. Вход собирает `chain_inputs.py section-input` (опыт I/04).

## Выжимка для агента

1. **Одна секция — один вызов, все слоты секции вместе;** заголовки предыдущих секций — на входе (сюжет заголовков).
   `[мнение]` {landing, site-page} → §1
2. **Факт — дословно `verbatim` или `canonical`, не шире;** условие `requires_nearby` — в том же предложении.
   `[проверено: B2/02, I/04]` все → §2
3. **Нет факта — `[PLACEHOLDER: что нужно]` и `missing_ids`, либо фраза без утверждения, либо слот не пишется** — по
   `fallback` пробела. `[стандарт базы]` все → §2
4. **Шаг «факт → ситуация клиента» — до текста, ситуация только из голоса клиента или `meaning` с id;** своя сцена =
   выдумка. `[практика: V _jwKQ6ZCeAI 22:30]` + `[не проверено]` (W2-4) {landing, site-page} → §2
5. **Заголовок секции — ответ на вопрос секции, не ярлык и не вопрос** (вопрос — в FAQ). `[практика: E 02 §1]` {landing} → §2
6. **Варианты — разного подхода и одной длины (± 20 %):** синонимы не дают выбора, длина покупает голоса. `[исследование:
   LC AlpacaEval, MT-Bench]` → §2
7. **Русский и английский промт различаются по делу:** RU — тире по грамматике, «ёлочки», кнопка — инфинитив СВ; EN —
   тире ≤ 1 на 100 слов, без «·» и надзаголовка над каждой секцией (приметы EN-ИИ, D2). `[проверено: D/03]` → §2, §3
8. **Второй язык — режим `adaptation`: писать из смысла и фактов с `translations.<lang>`, исходный текст — справка, не
   подлинник.** `[стандарт базы: решение заказчика п. 16]` + `[проверено: I/01 — 6 error без translations.en]` → §3
9. **Служебные поля `generated` (модель, канал, прогон, дата, параметры) пишет код,** модель — только `prompt_ref` и
   `technique`. `[стандарт базы: схема J]` → §4
10. **После вызова — `copydeck.py check`, находки — в P6;** перегенерация секции вместо правки — только при error в
    половине слотов. `[мнение]` все → §4

## 1. Входы и выход

| Переменная | Откуда | Проекция (скрипт `chain_inputs.py section-input`) |
|---|---|---|
| `{{PAGE_HEADER}}` | copy deck + иерархия | `lang`, `page_type`, `awareness`, `hero_approach`, `core_message`, `primary_action`, бренд |
| `{{SECTION}}` | иерархия → скелет | `section_id`, `section_role`, `question`, `message`, `carries`, `next_step`, возражения секции (text, answer) |
| `{{PREV_TITLES}}` | уже написанные секции | выбранные заголовки по порядку |
| `{{SLOT_CARDS}}` | `copy-slots.yaml` (E) | по слоту: `slot_id`, `slot_type`, `variants_n`, `purpose`, `structure`, длина основной единицы языка (min–target–max), `rules`, `bans`, `fact_required`, заголовки и `replacement` правил H |
| `{{FACTS}}` | `facts.yaml` (B2) | факты секции (`proof_ids`): `id`, `verbatim`, `canonical`, `requires_nearby`, `valid.until`, `permission.shows`; для EN — `translations.en` |
| `{{MISSING}}` | `facts.yaml → missing` | `id`, `placeholder`, `fallback` |
| `{{NEVER_CLAIM}}` | `facts.yaml → never_claim` + умолчания B2 | `id`, `text` |
| `{{VOICE_BRIEF}}` | `voice.yaml` (F) | `projections.prompt_brief`, `vocabulary.avoid[].term`, правила `tone_map` ситуации секции, 1–2 `samples` того же `slot_type` |
| `{{VOC}}` | `meaning` + `voc.yaml` | `situation`, `pains`, `jobs` с id; фразы клиентов с id |
| `{{MODE}}`, `{{SOURCE_SECTION}}`, `{{AUDIENCE_NOTE}}` | режим `adaptation` | выбранные тексты исходного deck, `meaning.languages[].audience_note`, `voice.languages[].adaptation_rules` |

Выход — YAML секции copy deck (`section` по `copy-deck.schema.json → $defs/section`).

## 2. Промт RU

```text
// модель: генератор из кандидатов 09/01 §2.1 (по умолчанию — лидер LT-01), t 0,7–1,0 для вариантов · 2026-09-24 · [не проверено]
// id: p4-section-copy/ru@1 · выход: YAML секции copy deck · проверка: copydeck.py check → правка P6
Ты — копирайтер сайта. Напиши тексты одной секции страницы по слотам — для людей, которые сканируют страницу.

ВХОД
<page>{{PAGE_HEADER}}</page>
<section>{{SECTION}}</section>
<story_so_far>{{PREV_TITLES}}</story_so_far>
<slots>{{SLOT_CARDS}}</slots>
<facts>{{FACTS}}</facts>
<gaps>{{MISSING}}</gaps>
<never>{{NEVER_CLAIM}}</never>
<voice>{{VOICE_BRIEF}}</voice>
<customer_words>{{VOC}}</customer_words>
<mode>{{MODE}}</mode>

ШАГ 1. ФАКТ → СИТУАЦИЯ. Для каждого факта секции запиши в notes слота одну строку: «<факт> → и что с того? →
<ситуация клиента> (<id из customer_words>)». Ситуацию бери только из <customer_words>; подходящей нет — пиши факт
без сцены. Свою ситуацию, отзыв или срок не придумывай.

ШАГ 2. ТЕКСТЫ
1. Каждое число, имя, дату, цитату, рейтинг, цену, срок, гарантию, «бесплатно» бери только из <facts>, в формулировке
   verbatim или canonical, не шире факта; id — в fact_ids слота. Условие из requires_nearby — в том же предложении.
2. Нет факта — по fallback пробела из <gaps>: placeholder — [PLACEHOLDER: что именно нужно] и id в missing_ids;
   rewrite-without — фраза без этого утверждения; omit-block — слот не пиши.
3. Ничего из <never> — ни прямо, ни пересказом («смета, которая не меняется» — то же, что «смета никогда не меняется»).
4. Отзыв — дословный verbatim из <facts> с подписью по permission.shows; не правь, не сокращай, не склеивай.
5. Заголовок секции — ответ на question секции одной фразой-утверждением, не ярлык («Наши преимущества», «Почему мы»,
   «Отзывы») и не вопрос; вопрос — только в FAQ. Вместе с <story_so_far> заголовки пересказывают страницу.
6. Механизм вместо прилагательного: «объект ведёт один прораб», а не «надёжно и прозрачно». Выводов за читателя
   («мы надёжные») не пиши — дай факт, из которого он сделает вывод сам.
7. Длина — по карточке слота: целься в target, не выходи за max. Кнопка — 1–4 слова, инфинитив совершенного вида +
   объект («Вызвать замерщика»); главное действие называется одинаково по всей странице. Строка у кнопки отвечает на
   один вопрос: что будет после нажатия, сколько стоит или что если передумаю.
8. Карточек и пунктов — столько, сколько фактов; длина — по содержанию, не под шаблон «ровно три».
9. Голос — по <voice>; слова «не говорим» не используй; обращение «вы» со строчной; без «!» и эмодзи.
10. Типографика: тире по грамматике — не убирай обязательное и не заменяй дефисом; кавычки «ёлочки»; числа — как в
    фактах; «₽» после числа.
11. Не пиши: «Откройте для себя», «В мире, где…», «индивидуальный подход», «качественно и в срок», «не просто X, а Y»,
    «X, который Y» без факта в Y, три прилагательных подряд, «уникальный», «лучший», «№ 1».
12. У слота с variants_n > 1 — варианты разного подхода (ситуация, механизм, результат-факт), а не синонимы; длина
    вариантов одного слота отличается не больше чем на 20 %.
13. Если <mode> = adaptation: пиши из <section>, <facts> и <customer_words> для аудитории <mode>.audience_note;
    исходный текст — справка о выбранном смысле, не текст для перевода.

ШАГ 3. САМОПРОВЕРКА (молча исправь, в выход не пиши): у каждого числа и имени есть fact_id; условие рядом с
«бесплатно», скидкой и ценой «от»; нет слов из <never> и «не говорим»; заголовок — утверждение; длины в пределах;
нет придуманных ситуаций, отзывов, сроков.

ВЫХОД — один YAML-документ без пояснений:
section:
  section_id: "…"
  section_role: "…"
  question: "…"
  message: "…"
  carries: ["…"]
  slots:
    - slot_id: "…"
      slot_type: "…"
      group: "card-1"                 # только у повторяемых элементов
      variants:
        - {id: a, text: "…", status: draft, source: model,
           generated: {prompt_ref: "09-ai-generation-evaluation/prompts/p4-section-copy.md#ru@1", technique: "fact-scenario"}}
      chosen: a                       # временно; выбирает человек (шаг S11)
      fact_ids: ["…"]
      missing_ids: ["…"]
      claim_flags: ["…"]              # claim_class фактов слота: guarantee, price-discount, rating…
      notes: "факт → ситуация: … (pain-…)"
```

## 3. Промт EN

```text
// model: a generator from the 09/01 §2.1 candidates (default — the LT-01 leader), t 0.7–1.0 for variants · 2026-09-24 · [не проверено]
// id: p4-section-copy/en@1 · output: YAML copy deck section · check: copydeck.py check → edit P6
You are a website copywriter. Write the copy of one page section, slot by slot, for people who scan pages.

INPUT
<page>{{PAGE_HEADER}}</page>
<section>{{SECTION}}</section>
<story_so_far>{{PREV_TITLES}}</story_so_far>
<slots>{{SLOT_CARDS}}</slots>
<facts>{{FACTS}}</facts>              — use translations.en when present
<gaps>{{MISSING}}</gaps>
<never>{{NEVER_CLAIM}}</never>
<voice>{{VOICE_BRIEF}}</voice>
<customer_words>{{VOC}}</customer_words>
<mode>{{MODE}}</mode>

STEP 1. FACT → SITUATION. For every fact in the section, add one line to the slot's notes: "<fact> → so what? →
<the customer's situation> (<id from customer_words>)". Take situations only from <customer_words>; if none fits,
state the fact without a scene. Never invent a situation, review or deadline.

STEP 2. COPY
1. Every number, name, date, quote, rating, price, deadline, warranty and "free" comes only from <facts>, worded as
   verbatim or canonical (translations.en first), never broader; ids go to fact_ids. Put the requires_nearby
   condition in the same sentence.
2. No fact → follow the gap's fallback in <gaps>: placeholder — [PLACEHOLDER: what exactly is needed] and the id in
   missing_ids; rewrite-without — a line without that claim; omit-block — skip the slot.
3. Nothing from <never>, directly or paraphrased.
4. Reviews — the exact verbatim with the attribution allowed by permission.shows; never edit, trim or merge them.
5. A section title answers the section question as a statement — not a label ("Our advantages", "Why us",
   "Testimonials") and not a question; questions belong in the FAQ. Together with <story_so_far> the titles tell the story.
6. Mechanism over adjectives: "one site manager runs the job", not "reliable and transparent". Do not draw
   conclusions for the reader ("we are reliable") — give the fact they can draw it from.
7. Length follows the slot card: aim at target, never beyond max. Buttons: 1–4 words, verb + object or first person
   ("Book a measuring visit", "Show me the estimate"); the main action has one name across the page. The line under
   the button answers one question: what happens after the click, what it costs, or what if I change my mind.
8. As many cards or list items as there are facts; length follows content, never a default of exactly three.
9. Voice per <voice>; no "avoid" words; contractions are fine where the voice allows them; no exclamation marks or emoji.
10. Typography: em dashes at most one per 100 words of prose and none in titles or buttons; never "·" as a separator;
    an eyebrow only when it adds information, never above every section; sentence case in titles.
11. Do not write: "Unlock", "Unleash", "Discover", "Where X meets Y", "seamless", "cutting-edge", "not just X, but Y",
    "X that Y" with an empty Y, three adjectives in a row, "unique", "best", "#1".
12. Slots with variants_n > 1 get variants with different approaches (situation, mechanism, result as a fact), not
    synonyms; variant lengths within one slot differ by at most 20 %.
13. If <mode> = adaptation: write from <section>, <facts> and <customer_words> for the audience in
    <mode>.audience_note; explain a local reality once, in a short insert ("Yandex Maps, the local maps and reviews
    app"); the source-language text shows what was chosen — do not translate it.

STEP 3. SELF-CHECK (fix silently, do not print): every number and name has a fact id; conditions sit next to "free",
discounts and "from" prices; no <never> or "avoid" words; titles are statements; lengths are within limits; no
invented situations, reviews or deadlines.

OUTPUT — one YAML document, same keys as the RU version; prompt_ref: "09-ai-generation-evaluation/prompts/p4-section-copy.md#en@1".
```

## 4. Выход и проверки после вызова

1. **Код дописывает** `generated` (`model`, `channel`, `run_id`, `date`, `params`), ставит `source: model`, собирает
   секции в copy deck (`lang`, `voice_ref`, `facts_ref`, `hierarchy_ref`, `awareness`) и перемешивает порядок вариантов
   перед показом человеку.
2. `python3 ../../scripts/text/copydeck.py check deck.yaml --facts facts.yaml --json run1.json --md run1.md` — claims →
   lint → validate (длины E, ядро первого экрана ≤ 40 слов, голос F, мета G); находки → P6.
3. **Судья P7** — только после 0 error сверки; **выбор между вариантами** — человек (`copydeck.py export-variants`).

## Частые ошибки

1. **Сцена без источника:** «Прораб каждый вечер присылает фото» — правило из одного отзыва (`never_claim` проекта).
2. **Факт шире записи:** «бесплатный замер в любом районе» при факте «в черте города».
3. **Ярлык или вопрос в заголовке секции:** «Отзывы», «Почему ремонты затягиваются?» вместо ответа.
4. **Варианты-синонимы и разной длины:** «Ремонт без хлопот» / «Ремонт без забот» — выбирать не из чего.
5. **Перевод вместо адаптации:** EN-текст из русского текста, а не из смысла; «двушка» → «two-room» в заголовке.
6. **Три карточки по шаблону и одинаковой длины** при двух фактах — третья карточка — вода.
7. **Кнопка с работой:** «Заполнить анкету на расчёт» вместо «Вызвать замерщика».

## Чек-лист

1. Факты секции — только из проекции, с `fact_ids`, условия рядом?
2. Пробелы — по `fallback`, заглушки перечислены в `missing_ids`?
3. У каждого факта есть строка «факт → ситуация» с id источника или честное «без сцены»?
4. Заголовок секции — утверждение, которое продолжает сюжет заголовков?
5. Варианты ключевых слотов разного подхода и близкой длины?
6. RU — тире по грамматике и «ёлочки»; EN — тире по порогу, без «·» и лишних надзаголовков?
7. Во втором языке — режим `adaptation` и факты с `translations.<lang>`?

## Открытые вопросы и противоречия

1. **Секция за вызов или слот за вызов:** секция держит сюжет, слот — дешевле при правке; сравнение не делалось (I-8 в
   плане). По умолчанию — секция.
2. **YAML-обёртка или голый текст:** структурированный вывод мог ухудшать генерацию (WebDev Arena через ux 11/02 §5.2) —
   I-3 в плане; до теста — YAML с блочными строками.
3. **Шаг «факт → ситуация»** повышает убедительность без роста выдумки — гипотеза W2-4; в I/04 ситуации нашлись в
   `meaning` у 4 из 10 фактов страницы, в текст вошли 2 («сумму узнаете до договора», «есть с кого спросить»), у
   остальных — текст без сцены.
4. **Правила права в промте (H1)** — заголовки и замены правил H в карточке слота; снижают ли они error права — LT-02.

## Источники

- E `../../04-copy-by-block/copy-slots.yaml` (69 типов, `length_rule`, `composites.hero-core`), `01-hero-and-cta.md`
  выжимка, `02-section-blocks.md` выжимка.
- F `../../05-voice-editorial/voice.schema.yaml` (`projections.prompt_brief`, `x-copy-deck-map`),
  `examples/voice-otves-warm.yaml`; `01-brand-voice.md` §8.3.
- B2 `../../02-strategy-messaging/facts.schema.yaml`, `03-proof-and-facts.md` §7; H `../../08-russian-legal-typography/claims-rules.yaml`.
- A `../../01-foundations/formulas.yaml` (`fact-scenario`, `three-questions-dry`); W2 `[V:_jwKQ6ZCeAI 22:30]`.
- D `../../03-corpus-measured/02-measurements.md` §9, §11 (приметы EN-ИИ, карточки одной длины); C
  `../../06-anti-slop/02-linter-spec-and-profiles.md` §9, §12.
- J `../../10-templates-recipes/copy-deck.schema.json` (`$defs/section`, `variant.generated`).
- Опыт I/04 — `99-raw/experiments/I/04-chain-manual/README.md` (шаги S6, S7).
