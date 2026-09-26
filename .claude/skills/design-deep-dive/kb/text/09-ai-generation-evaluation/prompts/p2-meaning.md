# P2 · Смысл по схеме `meaning` с основанием у каждого утверждения

Волна 3 · агент I2 · 2026-09-24 · промт `p2-meaning@1` (RU и EN) · `[не проверено]` · живой тест — LT-07 (B1-3), LT-02
(B1-2) в `../live-test-plan.md` · опыт `99-raw/experiments/I/04-chain-manual/` (шаг S3: выход — готовый смысл B1 и
проверки выхода)

Шаг S3 цепочки `../02-generation-pipeline.md`: бриф, разбор P1, ответы заказчика и `facts.yaml` → `meaning.yaml` по
`../../02-strategy-messaging/meaning.schema.yaml`. Процедура — B1 `01-positioning-value-proposition.md` §5.2, шаги 3–7.
Промт не заменяет сбор фактов: без анкеты смысл «Лесной обжарки» на 55 % состоит из допущений (B1/01).

## Выжимка для агента

1. **Запускай после ответов заказчика и `facts.yaml`, а не на голом брифе:** бриф даёт 6–24 % утверждений смысла,
   факты анкеты — ещё 27–31 %. `[проверено: B1/01]` все → §1
2. **У каждого утверждения — `basis`;** допущение — только с вопросом в `open_questions`. `[стандарт базы: B1]` все → §2
3. **`proof_ids` — только `fact:<id>` и `missing:<id>`;** свойство без факта — `needs-proof`, а не усиленная формулировка.
   `[стандарт базы]` все → §2
4. **Ядро и оффер — только на основаниях brief, customer, fact, voc** и не задевают `never_claim`: урок «Кварца» —
   обещание из допущения ушло в `product.goal`. `[проверено: B2/02]` {landing, site-page} → §2
5. **После вызова — `validate.py` B1 и сверка ядра с фактами** (`claims_check.py` на ядре, оффере и первом экране) до
   иерархии и текстов. `[проверено: I/04]` все → §4
6. **Доля `assumption` выше 30 % — стоп:** вернуться к анкете фактов, а не писать иерархию. `[мнение]` все → §4
7. **Проекция схемы в промт — только обязательные поля, enum и правило `basis`** (≈ 4,3 тыс. знаков, в 9 раз короче):
   полная схема (50 КБ ≈ 9–12 тыс. токенов [гипотеза: оценка по знакам]) со входами и выходом смысла занимает ≈ 20–29 тыс. из 32 тыс. токенов
   YandexGPT 5.1 Pro — без запаса. `[проверено: I/04]` все → §1

## 1. Входы и выход

| Переменная | Откуда | Проекция |
|---|---|---|
| `{{BRIEF_TEXT}}` | заказчик | дословно |
| `{{INTAKE_YAML}}` | выход P1 | целиком |
| `{{CUSTOMER_ANSWERS}}` | ответы на вопросы P1 | дословно, с датой |
| `{{FACTS_INDEX}}` | `facts.yaml` (B2) | `id`, `kind`, `claim_class`, `canonical`, `verification.status`; `missing[]`: `id`, `what` |
| `{{VOC_INDEX}}` | `voc.yaml` (B2), если есть | `id`, фраза, код |
| `{{NEVER_CLAIM}}` | `facts.yaml → never_claim` | `id`, `text` |
| `{{MEANING_SCHEMA_DIGEST}}` | `meaning.schema.yaml` | обязательные поля, enum, правило `basis` (скрипт `chain_inputs.py digest-meaning`) |

Выход — `meaning.yaml` (`meaning_version: 1`, `status: draft`). Следующий шаг — показ заказчику блока «Беру по
умолчанию» и вопросов (человек), затем P3.

## 2. Промт RU

```text
// модель: модель-кандидат 09/01 §2.1 с длинным контекстом, t = 0,3 · 2026-09-24 · [не проверено]
// id: p2-meaning/ru@1 · выход: meaning.yaml (meaning_version 1) · проверка: validate.py B1 + claims_check.py по ядру
Ты — стратег позиционирования. Собери смысл страницы до слов по схеме meaning. Текстов страницы не пиши:
формулировки смысла — внутренние, их читает копирайтер.

ВХОД
<brief>{{BRIEF_TEXT}}</brief>
<intake>{{INTAKE_YAML}}</intake>
<answers>{{CUSTOMER_ANSWERS}}</answers>
<facts>{{FACTS_INDEX}}</facts>
<voc>{{VOC_INDEX}}</voc>
<never_claim>{{NEVER_CLAIM}}</never_claim>
<schema>{{MEANING_SCHEMA_DIGEST}}</schema>

ПОРЯДОК
1. Альтернативы (не меньше двух, одна — статус-кво или «сделать самому») → уникальные свойства с proof_ids → темы
   ценности: цепочка свойство → выгода → ценность и мера клиента → кому это важнее всего → категория и стратегия.
2. Сегменты: ровно один primary; ситуация, работы («Когда…, хочу…, чтобы…»), боли, выгоды. Четыре силы: толчок,
   притяжение, тревога, привычка. Тревога и привычка становятся возражениями: text словами клиента, answer, proof_ids,
   where (section_role, slot_type), severity (blocker | major | minor), status.
3. Осведомлённость по источникам трафика (awareness.by_source) и искушённость рынка (stage 1–5, claims_heard — что
   обещают все).
4. value_proposition.core.text — одна фраза, не длиннее 240 знаков.

ОСНОВАНИЯ
5. У каждого утверждения — basis {kind, ref}. kind: brief | customer | voc | fact | public-page | research | inferred |
   assumption. fact — только ref "fact:<id>" из <facts>; voc — только id из <voc>; inferred — ref «из чего выведено».
6. kind: assumption — только с question_id вопроса в open_questions (не больше 10 вопросов; у каждого why, default,
   affects, priority 1–3).
7. proof_ids — только "fact:<id>" или "missing:<id>". Нет записи в <facts> — "missing:<id>" и предложение в
   x-missing-proposals {id, what, for}. Свойство без факта — proof_status: needs-proof.
8. value_proposition.core и offer.summary строятся только на утверждениях с basis brief, customer, fact или voc и не
   задевают <never_claim>. Запреты и обещания из допущений — в boundaries.not_promised с причиной.
9. Числа, имена, сроки, отзывы и «как именно работает» — только из <facts>, <answers>, <brief>. Не выдумывай.
10. status: draft; date: "{{TODAY}}"; даты — строкой в кавычках.

ВЫХОД — один YAML-документ по <schema> (meaning_version: 1), без пояснений до и после. Расширения — только ключи x-….
```

## 3. Промт EN

```text
// model: a long-context candidate model from 09/01 §2.1, t = 0.3 · 2026-09-24 · [не проверено]
// id: p2-meaning/en@1 · output: meaning.yaml (meaning_version 1) · checks: validate.py (B1) + claims_check.py on the core
You are a positioning strategist. Build the page's meaning before any words, following the meaning schema. Do not
write page copy: these statements are internal notes for the copywriter.

INPUT
<brief>{{BRIEF_TEXT}}</brief>
<intake>{{INTAKE_YAML}}</intake>
<answers>{{CUSTOMER_ANSWERS}}</answers>
<facts>{{FACTS_INDEX}}</facts>
<voc>{{VOC_INDEX}}</voc>
<never_claim>{{NEVER_CLAIM}}</never_claim>
<schema>{{MEANING_SCHEMA_DIGEST}}</schema>

ORDER
1. Alternatives (at least two, one of them the status quo or do-it-yourself) → unique attributes with proof_ids →
   value themes: attribute → benefit → value, with the customer's own measure → who cares most → category and strategy.
2. Segments: exactly one primary; situation, jobs ("When…, I want…, so I can…"), pains, gains. Four forces: push,
   pull, anxiety, habit. Anxiety and habit become objections: text in the customer's words, answer, proof_ids,
   where (section_role, slot_type), severity (blocker | major | minor), status.
3. Awareness by traffic source (awareness.by_source) and market sophistication (stage 1–5, claims_heard).
4. value_proposition.core.text — one sentence, at most 240 characters.

BASIS
5. Every statement has basis {kind, ref}. kind: brief | customer | voc | fact | public-page | research | inferred |
   assumption. fact — only ref "fact:<id>" from <facts>; voc — only ids from <voc>; inferred — ref says what from.
6. kind: assumption only with question_id pointing to open_questions (at most 10; each with why, default, affects,
   priority 1–3).
7. proof_ids — only "fact:<id>" or "missing:<id>". No record in <facts> → "missing:<id>" plus a proposal in
   x-missing-proposals {id, what, for}. An attribute without a fact → proof_status: needs-proof.
8. value_proposition.core and offer.summary rest only on statements with basis brief, customer, fact or voc and never
   touch <never_claim>. Bans and assumption-based promises go to boundaries.not_promised with the reason.
9. Numbers, names, deadlines, reviews and "how exactly it works" come only from <facts>, <answers>, <brief>.
10. status: draft; date: "{{TODAY}}"; dates as quoted strings.

OUTPUT — one YAML document following <schema> (meaning_version: 1), nothing before or after. Extensions — x-… keys only.
```

## 4. Выход и проверки после вызова

1. `99-raw/tools/venv-B1/bin/python ../../scripts/text/validate_meaning.py` — схема и смысловые проверки
   (один основной сегмент, ссылки внутри блока, допущения в `open_questions`, доказательства опор).
2. **Сверка смысла до текста** — `chain_inputs.py meaning-claims` собирает ядро, оффер, первый экран иерархии и
   сообщения секций в Markdown → `claims_check.py check … --facts facts.yaml`: `COPY-F-NEVER` и числа без факта ловятся
   до того, как попадут в заголовок (правило B1: ядро сверяется с `never_claim` до текста).
3. **Доли оснований:** счётчик `basis.kind`; `assumption` > 30 % → стоп и вопросы заказчику.
4. **Человек:** заказчик видит «Беру по умолчанию» и вопросы приоритета 1; после ответов — `status: approved`.

## Частые ошибки

1. **Смысл на голом брифе** — половина утверждений из догадок, а ядро держится на допущении.
2. **Свойство из отзыва:** «видят всё по фото» (один отзыв) записано как `has-proof`.
3. **`basis: inferred` без `ref`** — вывод, который нельзя перепроверить.
4. **Ядро с обещанием из `never_claim`** («смета не меняется») — потом его повторят hero и `product.goal` kimi.
5. **Все возражения `major`:** блокеры не отмечены — иерархия не поставит их до призыва.

## Чек-лист

1. Ответы заказчика и `facts.yaml` были на входе?
2. У каждого утверждения есть `basis`, у каждого допущения — вопрос?
3. `proof_ids` — только `fact:` и `missing:`?
4. Ядро ≤ 240 знаков и стоит на brief, customer, fact или voc?
5. `validate.py` — 0 ошибок, сверка ядра — 0 error?

## Открытые вопросы и противоречия

1. Заполняет ли модель схему без ошибок и сколько вопросов приоритета 1 задаёт — LT-07 (B1-3: 5 брифов × 2 модели).
2. Проекция схемы теряет смысловые проверки валидатора (они — в коде); модель может выдать схемно верный, но пустой
   смысл — ловит только человек и P3 (опора без доказательства).

## Источники

- B1: `../../02-strategy-messaging/meaning.schema.yaml` (`$defs/basis`, `$defs/question`, `x-kimi-map`);
  `01-positioning-value-proposition.md` §2, §4, §5; `02-awareness-hierarchy-objections.md` §1, §4; опыты B1/01, B1/03.
- B2: `../../02-strategy-messaging/03-proof-and-facts.md` §7; `facts.schema.yaml` (`never_claim`, `missing`).
- Цены и контекст моделей — `../01-models-for-copy.md` §3.2 (YandexGPT 5.1 Pro — 32 тыс. токенов в polza).
- Опыт I/04 — `99-raw/experiments/I/04-chain-manual/README.md` (шаг S3).
