# P7 · Судья: вопросы рубрики и попарное сравнение

Волна 3 · агент I2 · 2026-09-24 · промты `p7-judge-checklist@1` и `p7-judge-pairwise@1` (RU и EN) · `[не проверено]` ·
калибровка — LT-04 (I-4, I-5, I-6, B2-2, W1-3, G5) в `../live-test-plan.md` · опыт `99-raw/experiments/I/04-chain-manual/`
(шаг S10: формат ответа и подсчёт баллов, оценщик — сам агент)

Шаг S10 цепочки `../02-generation-pipeline.md`, только после 0 error сверки фактов. Вопросы, правила чтения `read` и
потолки `cap_if_no` — из `../copy-rubric.yaml` v1.1 (критерии COPY-R-01…09; 10–12 — только человек); протокол вызова и
калибровка — `../03-evaluation.md` §4.3–4.5; вопросы G — `../../07-seo-geo-copy/geo-checklist.yaml` (`judge_question`).
Судья — сигнал: статус слота он не меняет (COPY-C-20), сортирует варианты только после калибровки (COPY-C-22).

## Выжимка для агента

1. **Судья другого вендора, чем генератор; имена моделей скрыты.** `[исследование: самопредпочтение, MT-Bench]` все → §1
2. **Судья отвечает на вопросы, балл считает код** (`judge_scoring`: доля «да», потолки `cap_if_no`). `[практика: ai-media
   11/02]` + `[проверено: I/01]` все → §4
3. **Каждое «нет» — с дословной цитатой из текста; без цитаты — «не уверен».** `[стандарт базы: рубрика]` все → §2
4. **Правило чтения `read` передаётся вместе с вопросом и входит в версию промта.** `[проверено: I/03 — без read тот же
   оценщик сменил 10 % ответов]` все → §2
5. **Попарно — два вызова со сменой сторон; победа только при совпадении;** доля «A» вне 0,35–0,65 — судья смещён.
   `[данные: lechmazur 2026 — медиана переворотов 41,3 %]` все → §3
6. **t = 0, 3 повтора, спорное — до 11 или человеку.** `[исследование: arXiv 2606.13685]` все → §4
7. **У вопросов G с обратной полярностью (COPY-GEO-10, 18, 26) «да» — плохо;** полярность знает код, судья отвечает на
   вопрос как есть. `[стандарт базы]` {geo, landing} → §4
8. **Голос, естественность, «интересно» и предсказание A/B судье не отдаются.** `[исследование: POLLUX, JUDGE-BENCH,
   arXiv 2608.07517]` все → §2

## 1. Входы и выход

| Переменная | Откуда | Проекция (скрипт `chain_inputs.py judge-input`) |
|---|---|---|
| `{{TEXT}}`, `{{PATH}}`, `{{SCOPE}}` | copy deck | слот; для COPY-R-01, 09 — весь первый экран; для COPY-R-05 — страница (q4 о глубине аргумента по первому экрану не ответить, I/04); для COPY-R-07 — заголовки секций подряд; для 08 — строки у кнопок, гарантия, FAQ |
| `{{CRITERION}}` | `copy-rubric.yaml` | `id`, `name`, `questions[{id, ru|en, read}]` — без `cap_if_no` и якорей |
| `{{FACTS}}` | `facts.yaml` | для COPY-R-03, 08: `id`, `canonical`, `requires_nearby`; иначе пусто |
| `{{MEANING_EXCERPT}}` | `meaning.yaml` | для COPY-R-02, 04: `alternatives`, `unique_attributes`, `claims_heard` |
| `{{HIERARCHY_EXCERPT}}` | иерархия | для COPY-R-01, 05, 07, 08: `core_message`, `hero_approach`, `first_screen`, `sections[].question`, `objection_ids` блокеров, `not_said`, `must_not_say`, `argument_depth` |
| `{{TEXT_A}}`, `{{TEXT_B}}`, `{{SLOT_TYPE}}`, `{{SLOT_PURPOSE}}` | попарный режим | два варианта одного слота в случайном порядке; назначение слота из E |

Выход — JSON: ответы на вопросы (режим checklist) или вердикт пары (режим pairwise). Запись — `variant.checks.rubric`
(форма — `../copy-rubric.yaml → record_example`).

## 2. Промт RU — вопросы рубрики

```text
// модель: судья другого вендора, чем генератор (кандидаты — 09/01 §2.1, LT-04), t = 0, 3 прогона · 2026-09-24 · [не проверено]
// id: p7-judge-checklist/ru@1 · рубрика copy-rubric.yaml v1.1 · выход: JSON · балл считает код
Ты — проверяющий. Ответь на вопросы о тексте строго по тексту и приложенным данным. Не оценивай в целом, не ставь
баллов, не переписывай текст.

ВХОД
<text path="{{PATH}}" scope="{{SCOPE}}">{{TEXT}}</text>
<criterion>{{CRITERION}}</criterion>
<facts>{{FACTS}}</facts>
<meaning>{{MEANING_EXCERPT}}</meaning>
<hierarchy>{{HIERARCHY_EXCERPT}}</hierarchy>

ПРАВИЛА
1. На каждый вопрос <criterion> ответь "yes", "no", "unsure" или "n/a". "n/a" — только если нужного блока входа нет
   (он пуст).
2. Если у вопроса есть read — понимай вопрос именно так.
3. Каждый ответ "no" — с дословной цитатой из <text> в поле where. Нет цитаты — ответ "unsure".
4. Не додумывай: чего нет в <facts>, того у компании нет; эталонного текста нет — не ссылайся на него.
5. Язык, интерес и голос не оценивай — это решает человек.

ВЫХОД — только JSON, без пояснений:
{"rubric_version": "1.1", "criterion": "<id>", "path": "{{PATH}}",
 "answers": [{"id": "q1", "answer": "yes", "where": null, "note": ""},
             {"id": "q2", "answer": "no", "where": "дословная цитата", "note": "чего не хватает"}]}
```

## 3. Промт RU — попарное сравнение

```text
// модель: судья другого вендора; t = 0; каждая пара — два вызова со сменой сторон · 2026-09-24 · [не проверено]
// id: p7-judge-pairwise/ru@1 · для отсева брака или для сортировки после калибровки (COPY-C-22) · выход: JSON
Сравни два варианта одного слота страницы. Авторы вариантов неизвестны и не важны.

ВХОД
<slot>тип: {{SLOT_TYPE}}; задача слота: {{SLOT_PURPOSE}}; вопрос секции: {{SECTION_QUESTION}}</slot>
<page>{{PAGE_HEADER}}</page>
<facts>{{FACTS}}</facts>
<A>{{TEXT_A}}</A>
<B>{{TEXT_B}}</B>

ПРАВИЛА
1. Вопрос один: какой вариант лучше решает задачу слота для этой страницы и этого посетителя?
2. Вариант с утверждением, которого нет в <facts>, проигрывает, как бы хорошо он ни звучал.
3. Длина — не достоинство: при равном смысле лучше короткий.
4. Разница только во вкусе — "tie"; оба не решают задачу — "neither".
5. Причина — 1–2 строки с дословными цитатами из обоих вариантов.

ВЫХОД — только JSON: {"winner": "A" | "B" | "tie" | "neither", "reason": "…", "quotes": {"A": "…", "B": "…"}}
```

## 4. Промты EN и подсчёт

```text
// model: a judge from a different vendor than the generator (candidates — 09/01 §2.1, LT-04), t = 0, 3 runs · 2026-09-24 · [не проверено]
// id: p7-judge-checklist/en@1 · rubric copy-rubric.yaml v1.1 · output: JSON · scores are computed by code
You are a reviewer. Answer the questions about the text strictly from the text and the attached data. Do not give an
overall verdict, do not score, do not rewrite.

INPUT
<text path="{{PATH}}" scope="{{SCOPE}}">{{TEXT}}</text>
<criterion>{{CRITERION}}</criterion>     — questions in English (field en) with read rules
<facts>{{FACTS}}</facts>
<meaning>{{MEANING_EXCERPT}}</meaning>
<hierarchy>{{HIERARCHY_EXCERPT}}</hierarchy>

RULES
1. Answer every question with "yes", "no", "unsure" or "n/a"; "n/a" only when the needed input block is empty.
2. If a question has a read rule, interpret the question exactly that way.
3. Every "no" carries a verbatim quote from <text> in where. No quote — answer "unsure".
4. Do not assume: what is not in <facts> does not exist; there is no reference text to cite.
5. Do not judge language quality, interest or voice — a human decides those.

OUTPUT — JSON only: {"rubric_version": "1.1", "criterion": "<id>", "path": "{{PATH}}", "answers": [{"id": "q1", "answer": "yes", "where": null, "note": ""}]}
```

```text
// model: a judge from a different vendor; t = 0; each pair — two calls with sides swapped · 2026-09-24 · [не проверено]
// id: p7-judge-pairwise/en@1 · for defect screening, or sorting after calibration (COPY-C-22) · output: JSON
Compare two variants of one page slot. Who wrote them is unknown and irrelevant.
INPUT: <slot>type: {{SLOT_TYPE}}; the slot's job: {{SLOT_PURPOSE}}; section question: {{SECTION_QUESTION}}</slot>
<page>{{PAGE_HEADER}}</page> <facts>{{FACTS}}</facts> <A>{{TEXT_A}}</A> <B>{{TEXT_B}}</B>
RULES: 1. One question: which variant does the slot's job better for this page and this visitor? 2. A variant with a
claim that is not in <facts> loses, however good it sounds. 3. Length is not a merit: with equal meaning, shorter
wins. 4. Only a matter of taste — "tie"; neither does the job — "neither". 5. Reason — 1–2 lines with verbatim quotes
from both variants.
OUTPUT — JSON only: {"winner": "A" | "B" | "tie" | "neither", "reason": "…", "quotes": {"A": "…", "B": "…"}}
```

**Подсчёт (код, `chain_inputs.py judge-score`).**
- Балл критерия — формула `judge_scoring` рубрики: `share = yes / answered` («не уверен» = «нет» без потолка, `n/a` вне
  знаменателя), `score = min(max(1, round_half_up(5 × share)), наименьший cap_if_no среди «нет»)`; меньше двух ответов —
  `null`, слот — человеку. Три прогона: ответ вопроса — большинство; расхождение прогонов по вопросу — «не уверен».
- Вопросы G — критерий `COPY-GEO-<nn>` с одним вопросом; `pass_if: "no"` у COPY-GEO-10 («блоки-повторы есть?»),
  COPY-GEO-18 («конкурент мог бы подписать?»), COPY-GEO-26 («повторяет ответ нейросети?»), у остальных — `"yes"`.
- Попарно: вызов A-B и вызов B-A; победа — только при совпадении, иначе «ничья»; доля «A» по всем парам вне
  0,35–0,65 — судья смещён, его результат не используется (COPY-C-23).
- Запись — `variant.checks.rubric: {version: "1.1", judge: {model, runs, both_orders, prompt_version}, scores:
  {COPY-R-01: {judge, judge_no: [{q, where}]}}}`.

## Частые ошибки

1. **Судья той же семьи, что генератор** — самопредпочтение; в опыте I/04 так и было (оценщик — сам агент) — это
   проверка формата, не качества.
2. **Общий балл «1–10» вместо вопросов** — завышен и не объясняет, что править.
3. **Один порядок пары** — выигрывает показанный первым (64,3 % у 36 моделей).
4. **Рубрика до сверки фактов** — награда за выдуманную конкретику (демо K3 — 5,0 из 5, I/03).
5. **Вопрос без `read`** — тот же судья понимает «сцену клиента» по-разному в двух прогонах.

## Чек-лист

1. Судья другого вендора, имена моделей скрыты?
2. Вопросы переданы с `read`, без якорей и потолков?
3. Каждое «нет» с цитатой, баллы посчитал код?
4. Три прогона, попарно — оба порядка, доля «A» в 0,35–0,65?
5. Версии рубрики и промта записаны в `checks.rubric`?
6. Критерии 10–12 и прогноз A/B судье не отдавались?

## Открытые вопросы и противоречия

1. Какие критерии получат `trust: sort` — только после LT-04 (≥ 0,8 согласия с заказчиком, Уилсон ≥ 0,65, n ≥ 20).
2. Попарный режим до калибровки годится только для отсева брака; поточечная шкала POLLUX точнее и без позиции —
   развилка ролей сохраняется (`../03-evaluation.md` §4.1).
3. Судья EN-промтом на русском тексте или RU-промтом — не проверено; по умолчанию язык промта = язык текста.

## Источники

- `../copy-rubric.yaml` v1.1 (`judge_scoring`, `read`, `record_example`, DR-1…6); `../copy-checklist.yaml` (COPY-C-20…24);
  `../03-evaluation.md` §3.2, §4.2–4.5.
- G `../../07-seo-geo-copy/geo-checklist.yaml` (8 `judge_question`).
- ai-media `../../../ai-media/11-evaluation-qa/02-vlm-critic-and-rubrics.md` §2, §6 (атомарные вопросы, стороны,
  калибровка); ux `../../../ux/11-ai-generated-ui/02-research-and-benchmarks.md` §4.3.
- lechmazur/position_bias (2026, README снят 2026-09-24); arXiv 2606.13685 (через ux 11/02); POLLUX arXiv 2505.24616.
- Опыт I/04 — `99-raw/experiments/I/04-chain-manual/README.md` (шаг S10).
