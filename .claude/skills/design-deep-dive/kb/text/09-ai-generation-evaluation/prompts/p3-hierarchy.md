# P3 · Иерархия сообщений под уровень осведомлённости

Волна 3 · агент I2 · 2026-09-24 · промт `p3-hierarchy@1` (RU и EN) · `[не проверено]` · живой тест — LT-07 (B1-4, новая
строка I-7) в `../live-test-plan.md` · опыт `99-raw/experiments/I/04-chain-manual/` (шаг S4)

Шаг S4 цепочки `../02-generation-pipeline.md`: `meaning.yaml` + один источник трафика → иерархия одной страницы по
`../../02-strategy-messaging/message-hierarchy.schema.yaml`. Правила уровней — B1 `02-awareness-hierarchy-objections.md`
§1.2 (тип первого экрана), §1.4 (порядок доказательств), §2 (иерархия); проекция таблиц — `{{AWARENESS_RULES}}`.

## Выжимка для агента

1. **Одна иерархия — один уровень осведомлённости и один сегмент;** под другой трафик — соседняя иерархия
   (`sibling_ids`), смысл тот же. `[проверено]` {landing, site-page} → §2
2. **Уровень задаёт вход, а не температура трафика:** осведомлённость и сила намерения — разные оси. `[практика: B1]` → §2
3. **Тип первого экрана — по таблице уровней:** problem-aware — ситуация и её цена, solution-aware — категория против
   привычных подходов, product-aware — имя и доказательство. `[практика: Шварц через B1 02 §1.2]` {landing} → §1
4. **Блокеры закрываются до финального призыва;** каждая опора несётся хотя бы одной секцией. `[стандарт базы: validate.py]` → §4
5. **Опора без факта остаётся `missing`** — её секция получит `[PLACEHOLDER]`; словами её не усиливают. `[проверено]` все → §2
6. **`not_said` и `must_not_say` пишутся явно** — иначе генератор текста допишет чужой уровень и запреты. `[практика]` → §2

## 1. Входы и выход

| Переменная | Откуда | Проекция |
|---|---|---|
| `{{MEANING_PROJECTION}}` | `meaning.yaml` | `audience[primary]`, `awareness.by_source`, `sophistication`, `positioning` (alternatives, unique_attributes, value_themes), `value_proposition.core`, `offer`, `objections`, `risk_reversal`, `boundaries` (`chain_inputs.py hierarchy-input`) |
| `{{FACTS_INDEX}}` | `facts.yaml` | `id`, `canonical`, `claim_class`; `missing[].id` |
| `{{PAGE_TYPE}}`, `{{TRAFFIC_SOURCES}}`, `{{AWARENESS}}`, `{{SOURCE_PROMISE}}` | план страниц (site) или решение оркестратора | один уровень на вызов |
| `{{SECTION_ROLES}}` | `99-raw/notes/temp-vocabulary-v0.yaml` | список id ролей секций |
| `{{AWARENESS_RULES}}` | B1 02 §1.2, §1.4 | таблица уровень → `hero_approach`, первый довод, порядок доказательств, глубина (в `chain_inputs.py`) |

Выход — иерархия (`hierarchy_version: 1`, `status: draft`) → `validate.py` B1 → скелет copy deck (`make_skeleton.py`).

## 2. Промт RU

```text
// модель: модель-кандидат 09/01 §2.1, t = 0,3 · 2026-09-24 · [не проверено]
// id: p3-hierarchy/ru@1 · выход: message-hierarchy (hierarchy_version 1) · проверка: validate.py B1
Ты — стратег. Построй иерархию сообщений одной страницы для одного уровня осведомлённости. Текстов страницы не пиши:
сообщения — внутренние формулировки для копирайтера.

ВХОД
<meaning>{{MEANING_PROJECTION}}</meaning>
<facts>{{FACTS_INDEX}}</facts>
<target>page_type: {{PAGE_TYPE}}; traffic_sources: {{TRAFFIC_SOURCES}}; awareness: {{AWARENESS}};
promise_of_source: "{{SOURCE_PROMISE}}"</target>
<roles>{{SECTION_ROLES}}</roles>
<levels>{{AWARENESS_RULES}}</levels>

ПРАВИЛА
1. Уровень осведомлённости — из <target>; не выводи его из температуры трафика. Сегмент — primary из <meaning>.
2. core_message.text — одна фраза, из которой выводятся первый экран и все опоры; hero_approach — по <levels>;
   value_theme_refs — id из meaning; proof_ids; must_not_say — из boundaries.not_promised, never_claim и того, что
   говорят другому уровню.
3. first_screen: what (категория словами клиента), for_whom, outcome, differentiator (с solution-aware и выше),
   next_step, proof_ids, message_match — как первый экран продолжает обещание источника трафика.
4. pillars — 3–5 опор: id, message, layer (clarity | relevance | value | differentiation | friction), proof_status
   (has-proof | missing), proof_ids, objection_ids, counter — чем опора отвечает на альтернативу.
5. sections по порядку: order, section_role из <roles>, question — вопрос посетителя его словами, message — ответ одной
   фразой, carries (id опор или core), proof_ids, objection_ids, next_step. Каждая опора несётся хотя бы одной секцией.
6. Первым идёт довод, нужный этому уровню (<levels>); proof_order — порядок доказательств на странице. Возражения с
   severity: blocker закрываются до секции final-cta.
7. not_said — что страница сознательно не говорит: доводы другого уровня, второе обещание в первом экране, сравнение
   с конкурентами по имени.
8. Опору без факта оставь с proof_status: missing и proof_ids "missing:<id>"; не усиливай её словами.
9. Ничего не выдумывай: числа, имена, сроки — только из <facts> и <meaning>.

ВЫХОД — один YAML-документ по схеме message-hierarchy: hierarchy_version: 1, date: "{{TODAY}}", status: draft,
id, site, meaning_ref, lang, page, core_message, first_screen, pillars, sections, proof_order, not_said.
Без пояснений до и после.
```

## 3. Промт EN

```text
// model: a candidate model from 09/01 §2.1, t = 0.3 · 2026-09-24 · [не проверено]
// id: p3-hierarchy/en@1 · output: message-hierarchy (hierarchy_version 1) · check: validate.py (B1)
You are a strategist. Build the message hierarchy of one page for one awareness level. Do not write page copy:
messages are internal statements for the copywriter.

INPUT
<meaning>{{MEANING_PROJECTION}}</meaning>
<facts>{{FACTS_INDEX}}</facts>
<target>page_type: {{PAGE_TYPE}}; traffic_sources: {{TRAFFIC_SOURCES}}; awareness: {{AWARENESS}};
promise_of_source: "{{SOURCE_PROMISE}}"</target>
<roles>{{SECTION_ROLES}}</roles>
<levels>{{AWARENESS_RULES}}</levels>

RULES
1. Take the awareness level from <target>; never derive it from traffic temperature. Segment — the primary one.
2. core_message.text — one sentence that the first screen and every pillar derive from; hero_approach per <levels>;
   value_theme_refs; proof_ids; must_not_say — from boundaries.not_promised, never_claim and other levels' messages.
3. first_screen: what (the category in the customer's words), for_whom, outcome, differentiator (solution-aware and
   above), next_step, proof_ids, message_match — how the first screen continues the traffic source's promise.
4. pillars — 3 to 5: id, message, layer (clarity | relevance | value | differentiation | friction), proof_status
   (has-proof | missing), proof_ids, objection_ids, counter — how the pillar answers the alternative.
5. sections in order: order, section_role from <roles>, question — the visitor's own question, message — a one-line
   answer, carries (pillar ids or core), proof_ids, objection_ids, next_step. Every pillar is carried by a section.
6. Lead with the argument this level needs (<levels>); proof_order — the order of proof on the page. Objections with
   severity: blocker are closed before the final-cta section.
7. not_said — what the page deliberately leaves out: other levels' arguments, a second promise on the first screen,
   named competitor comparisons.
8. A pillar without a fact keeps proof_status: missing with "missing:<id>"; do not inflate it with words.
9. Invent nothing: numbers, names, deadlines come only from <facts> and <meaning>.

OUTPUT — one YAML document following the message-hierarchy schema (hierarchy_version: 1, date: "{{TODAY}}",
status: draft, id, site, meaning_ref, lang, page, core_message, first_screen, pillars, sections, proof_order,
not_said). Nothing before or after it.
```

## 4. Выход и проверки после вызова

1. `validate.py` B1 — схема, ссылки на `meaning` и `facts`, блокеры до призыва, опора несётся секцией; предупреждение,
   если `hero_approach` не совпадает с уровнем.
2. **Сверка смысла до текста** (`chain_inputs.py meaning-claims`): `core_message`, `first_screen`, `sections[].message`
   → `claims_check.py`; числа и обещания без факта видны до генерации.
3. **Человек** (редактор или заказчик) — какую иерархию на какой источник трафика ставить; порядок секций утверждает
   site (`page-plan`), здесь он черновой.
4. Иерархия → скелет copy deck: `make_skeleton.py` переносит `section_role`, `question`, `message`, `carries`,
   `proof_ids` → `fact_ids` / `missing_ids` в секции copy deck J (`10-templates-recipes/copy-deck.schema.json`).

## Частые ошибки

1. **Одна иерархия на всех:** брендовому трафику объясняют проблему, проблемному — показывают рейтинг первым.
2. **Опора без секции:** «один прораб» в `pillars`, но ни одна секция его не несёт — текст потеряет отличие.
3. **Блокер после призыва:** страх «смета вырастет» закрыт в FAQ под формой.
4. **Секции-ярлыки:** `question: "Отзывы"` вместо вопроса посетителя — дальше заголовок станет ярлыком.
5. **Усиленная опора без факта:** «прозрачный контроль на каждом этапе» вместо `missing:photo-report-process`.

## Чек-лист

1. Один уровень и один сегмент на файл?
2. `hero_approach` совпадает с таблицей уровней?
3. Каждая опора несётся секцией, блокеры закрыты до `final-cta`?
4. У опор без факта `proof_status: missing`?
5. `not_said` и `must_not_say` заполнены?
6. `validate.py` — 0 ошибок?

## Открытые вопросы и противоречия

1. Определяет ли модель уровень по запросу так же, как человек (κ ≥ 0,6) — B1-4 в плане; здесь уровень задаётся на входе.
2. Порядок секций — у site (`page-plan`), число доводов — у иерархии (`argument_depth`): до S1 site порядок черновой.
3. Иерархия solution-aware «Отвеса» (Директ, 50 % трафика) в базе написана только в опыте I/04 (ai-self) — проверка
   моделью — строка I-7 плана.

## Источники

- B1 `../../02-strategy-messaging/02-awareness-hierarchy-objections.md` §1.2, §1.4, §2; `message-hierarchy.schema.yaml`;
  примеры `examples/hierarchy-otves-*.yaml`; опыт `99-raw/experiments/B1/02-two-hierarchies/`.
- Временный словарь ролей секций — `99-raw/notes/temp-vocabulary-v0.yaml`.
- Опыт I/04 — `99-raw/experiments/I/04-chain-manual/README.md` (шаг S4).
