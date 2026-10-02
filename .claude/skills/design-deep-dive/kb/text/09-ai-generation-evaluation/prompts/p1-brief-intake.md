# P1 · Разбор брифа и вопросы заказчику

Волна 3 · агент I2 · 2026-09-24 · промт `p1-brief-intake@1` (RU и EN) · `[не проверено]`: модели не вызывались ·
живой тест — LT-07 (B1-3) в `../live-test-plan.md` · опыт `99-raw/experiments/I/04-chain-manual/` (шаг S1, ai-self)

Первый шаг цепочки `../02-generation-pipeline.md` (S1): бриф заказчика → четыре списка (заказано, факты, ограничения,
пробелы), допущения, вопросы одним сообщением, пробелы для анкеты фактов. Текстов страницы шаг не пишет. Дизайн,
структуру и пакет исполнителя разбирает kimi (`../../../kimi-research/07-brief-handoff/01-from-app-description-to-brief.md`
§2–4); здесь — только смысл и факты.

## Выжимка для агента

1. **Факт из брифа — только с дословной цитатой** (`quote`); вывод без цитаты — допущение `inferred` или `assumption`.
   `[проверено: B1/01 — бриф даёт 6–24 % утверждений смысла]` все → §1
2. **Не больше 7 вопросов одним сообщением**, у каждого — зачем, умолчание, какие поля закрывает. `[практика: kimi 07/01 §4.1]` все → §2
3. **Факты спрашивай свободным ответом, решения — вариантами**; варианты фактов не выдумывай. `[практика: B2 proof-intake §0]` все → §2
4. **Пробелы ищи по десяти темам смысла** (B1 01 §5.3): альтернативы, механизм отличия, лучшие клиенты, риски клиента в
   договоре, продавец, трафик, границы, доказательства, кто решает, второй язык. `[практика]` {landing, site-page} → §2
5. **Пробел, который закрывается документом, — запись `missing`** с `fallback`; до ответа на странице будет
   `[PLACEHOLDER]`. `[стандарт базы]` все → §4
6. **Кандидаты `never_claim` — сразу:** правило из одного отзыва, «лучший», гарантия результата. `[проверено]` все → §4
7. **Проверка выхода — кодом:** цитаты — подстроки брифа, вопросов ≤ 7, у допущения — вопрос. `[проверено]` все → §4

## 1. Входы и выход

| Переменная | Откуда | Проекция |
|---|---|---|
| `{{BRIEF_TEXT}}` | сообщение заказчика | дословно, без пересказа |
| `{{FACTS_INDEX}}` | `facts.yaml`, если уже есть | `id`, `canonical`, `verification.status`; `missing[].id` |
| `{{PAGE_TYPE}}` | тип страницы из брифа или умолчание | id временного словаря (`99-raw/notes/temp-vocabulary-v0.yaml`) |
| `{{LANG}}`, `{{TODAY}}` | задача | `ru` или `en`; дата ГГГГ-ММ-ДД |

Выход — YAML `intake` (§4). Следующий шаг: `message_to_customer` → ответы заказчика → `facts.yaml` по анкете B2
(`../../02-strategy-messaging/proof-intake.md` §5, человек) → P2.

## 2. Промт RU

```text
// модель: любая модель-кандидат 09/01 §2.1, t = 0,3 · 2026-09-24 · [не проверено]
// id: p1-brief-intake/ru@1 · выход: YAML intake · проверка: check_intake.py (опыт I/04)
Ты — редактор-стратег. Разбери бриф заказчика до текстов: что известно, чего нет, что спросить.
Текстов страницы не пиши.

ВХОД
<brief>{{BRIEF_TEXT}}</brief>
<known_facts>{{FACTS_INDEX}}</known_facts>
<page>тип страницы: {{PAGE_TYPE}}; язык: {{LANG}}; сегодня: {{TODAY}}</page>

ПРАВИЛА
1. Разложи бриф на четыре списка: заказано, факты, ограничения, пробелы. Факт — только то, что заказчик написал сам;
   в поле quote — дословная цитата из <brief>. Обобщение, вывод, округление — не факт.
2. Каждое допущение пометь: kind: inferred (выведено — укажи из чего) или kind: assumption (догадка — нужен вопрос,
   question_id). Все допущения повтори в going_with — умолчаниями, которые заказчик отменит одной строкой.
3. Пробелы ищи по темам: с кем сравнивают и куда уходят; почему выбирают и чем это подтверждено (как именно работает
   отличие); лучшие клиенты и что у них случилось; риски клиента в договоре (цена и её изменение, срок, оплата, возврат,
   гарантия); кто продавец (юрлицо); откуда приходят посетители; чего нельзя обещать и кому не подходите; отзывы, кейсы,
   числа и разрешения на публикацию; кто принимает решение о покупке; второй язык.
4. Вопросы: не больше 7, одним сообщением, по убыванию priority (1 — без ответа нельзя писать главное сообщение).
   У каждого: why — одна строка; options — 2–4 варианта для решений, для фактов пусто (свободный ответ, варианты не
   выдумывай); default — что будет, если заказчик не ответит; affects — какие поля смысла закрывает ответ.
   Не спрашивай то, что есть в брифе или выводится; не спрашивай «аудиторию, задачу, тон», если бриф их называет.
5. Пробел, который закрывается документом (договор, прайс, выгрузка, разрешение), — запись missing: id в kebab-case,
   what, kind, question, who, fallback: placeholder | omit-block | rewrite-without.
6. never_claim_candidates: обещания, которые из брифа легко вывести, но нельзя утверждать: превосходная степень без
   критерия, гарантия результата, правило компании, выведенное из одного отзыва, обещание, которого нет в договоре.
7. Числа, имена, даты и цены пиши только в facts_from_brief с цитатой. Ничего не добавляй от себя.

ВЫХОД — один документ YAML, без пояснений до и после:
intake:
  lang: "{{LANG}}"
  page_type: "{{PAGE_TYPE}}"
  ordered: ["что заказано"]
  domain: "одна фраза"
  facts_from_brief:
    - {text: "…", quote: "дословно из брифа", kind: price|offer-terms|guarantee|metric|rating|company|property|testimonial|other}
  constraints: ["…"]
  gaps:
    - {id: gap-…, what: "…", affects: ["positioning.alternatives"], proof_intake_block: 4}
  assumptions:
    - {id: as-…, text: "…", kind: inferred|assumption, from: "из чего выведено", question_id: q-…}
  questions:
    - {id: q-…, q: "…", why: "…", options: [], default: "…", affects: ["…"], priority: 1}
  missing:
    - {id: …, what: "…", kind: …, question: "…", who: "…", fallback: placeholder}
  never_claim_candidates:
    - {text: "…", claim_class: superlative|guarantee|forecast|fact-property|…, why: "…"}
  going_with: ["…"]
  message_to_customer: |
    Сообщение заказчику: вопросы по порядку, у каждого — «если не ответите — …»; в конце строка «Беру по умолчанию: …».
```

## 3. Промт EN

```text
// model: any candidate model from 09/01 §2.1, t = 0.3 · 2026-09-24 · [не проверено]
// id: p1-brief-intake/en@1 · output: YAML intake · check: check_intake.py (experiment I/04)
You are a strategy editor. Take the client's brief apart before any copy is written: what is known, what is missing,
what to ask. Do not write page copy.

INPUT
<brief>{{BRIEF_TEXT}}</brief>
<known_facts>{{FACTS_INDEX}}</known_facts>
<page>page type: {{PAGE_TYPE}}; language: {{LANG}}; today: {{TODAY}}</page>

RULES
1. Split the brief into four lists: requested, facts, constraints, gaps. A fact is only what the client wrote; put the
   exact words from <brief> in quote. A generalisation, conclusion or rounding is not a fact.
2. Mark every assumption: kind: inferred (derived — say from what) or kind: assumption (a guess — needs a question,
   question_id). Repeat all assumptions in going_with as defaults the client can cancel in one line.
3. Look for gaps on these topics: what customers compare you with and where they go instead; why they choose you and
   what proves it (how exactly the difference works); best customers and what happened to them; the customer's risks
   in the contract (price and price changes, deadline, payment, refunds, warranty); who the seller is (legal entity);
   where visitors come from; what must not be promised and who you are not for; reviews, cases, numbers and permission
   to publish them; who makes the buying decision; a second language.
4. Questions: at most 7, in one message, sorted by priority (1 = the core message cannot be written without it). Each
   has why (one line); options — 2–4 for decisions, empty for facts (free answer, never invent options); default —
   what happens if the client does not answer; affects — which meaning fields the answer closes. Do not ask what the
   brief already says or what can be derived.
5. A gap closed by a document (contract, price list, CRM export, permission) becomes a missing entry: kebab-case id,
   what, kind, question, who, fallback: placeholder | omit-block | rewrite-without.
6. never_claim_candidates: promises that are easy to derive from the brief but must not be stated: a superlative
   without a criterion, a guaranteed result, a company rule inferred from one review, a promise the contract lacks.
7. Numbers, names, dates and prices go only into facts_from_brief with a quote. Add nothing of your own.

OUTPUT — one YAML document, nothing before or after it (same keys as the RU version):
intake: {lang, page_type, ordered, domain, facts_from_brief, constraints, gaps, assumptions, questions, missing,
         never_claim_candidates, going_with, message_to_customer}
message_to_customer ends with "Going with: …" — the defaults you will use unless the client objects.
```

## 4. Выход и проверки после вызова

- **Код** (`../../scripts/text/check_intake.py`): YAML читается; каждая `quote` — подстрока брифа
  после нормализации пробелов, кавычек и тире; вопросов ≤ 7; у `assumption` есть `question_id` из `questions`; id — в
  kebab-case и уникальны; у вопросов есть `why`, `default`, `affects`; в `facts_from_brief` нет числа вне цитаты.
- **Человек:** отправляет `message_to_customer` (или правит); ответы → `facts.yaml` по `proof-intake.md` §5 с
  `source.quote` → `claims_check.py lint-facts` (факты не генерирует модель: выдумка живёт и в самих фактах — «сборка в
  Казани», B2/02).
- **Запись:** `intake.yaml` рядом с брифом; вопросы с ответами переходят в `meaning.open_questions` (P2).

## Частые ошибки

1. **Вывод записан фактом:** «12 лет на рынке» из «с 2014 года» без цитаты — число, которого заказчик не писал.
2. **Правило из отзыва:** «клиенты хвалят, что видят всё по фото» → «присылаем фото каждый вечер» — это `assumption`
   и кандидат `never_claim`, а не свойство.
3. **Анкета вместо вопросов:** 15 вопросов «про аудиторию и тон» — заказчик не ответит; нужны ≤ 7 по приоритету.
4. **Варианты для фактов:** «Гарантия: 1 год / 2 года / 3 года?» — модель подсовывает ответ; факт — свободным ответом.
5. **Вопрос без умолчания:** работа встаёт, пока заказчик молчит; с `default` цепочка идёт дальше с пометкой.

## Чек-лист

1. У каждого факта из брифа есть дословная цитата?
2. Каждое допущение помечено и есть в `going_with`?
3. Вопросов не больше 7, у каждого есть зачем, умолчание, поля?
4. Факты спрашиваются свободным ответом?
5. Пробелы, которые закрываются документом, записаны в `missing` с `fallback`?
6. Кандидаты `never_claim` выписаны?

## Открытые вопросы и противоречия

1. Сколько пробелов модель находит сама и сколько вопросов приоритета 1 теряет — не измерено (LT-07, B1-3); в I/04 шаг
   выполнил тот же агент, что знает ответы B1 (верхняя граница).
2. Kimi разбирает бриф шире (дизайн, ассеты, стек); два разбора одного брифа могут задать заказчику пересекающиеся
   вопросы — сводить в одно сообщение (≤ 7) должен оркестратор.

## Источники

- B1 `../../02-strategy-messaging/01-positioning-value-proposition.md` §5.1–5.3 (поля брифа, шаги, 10 вопросов);
  опыт `99-raw/experiments/B1/01-briefs-to-meaning/` (доли оснований).
- B2 `../../02-strategy-messaging/proof-intake.md` §0, §5; `facts.schema.yaml` (`missing[]`).
- kimi `../../../kimi-research/07-brief-handoff/01-from-app-description-to-brief.md` §2.1 (четыре списка), §3 (Going
  with), §4.1 (≤ 7 вопросов, умолчания, свободный ответ для фактов).
- Опыт I/04 — `99-raw/experiments/I/04-chain-manual/README.md` (шаг S1 на брифе «Отвеса»).
