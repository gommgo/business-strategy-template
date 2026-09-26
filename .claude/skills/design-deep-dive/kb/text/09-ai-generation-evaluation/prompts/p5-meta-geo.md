# P5 · Мета, OG и GEO-слой (FAQ, ответ первым)

Волна 3 · агент I2 · 2026-09-24 · промт `p5-meta-geo@1` (RU и EN) · `[не проверено]` · живой тест — LT-09 (G4) и LT-02
(G3) в `../live-test-plan.md` · опыт `99-raw/experiments/I/04-chain-manual/` (шаг S7)

Шаг S7 цепочки `../02-generation-pipeline.md`: после текстов секций — `title`, `description`, OG и ответы FAQ. Правила —
G: шаблоны `templates` 18 типов страниц и длины `limits` из `../../07-seo-geo-copy/meta-rules.yaml`, пункты
`../../07-seo-geo-copy/geo-checklist.yaml` (28, из них 8 вопросов судье). Техника SEO и GEO (разметка, индексация) —
site. GEO здесь — не «текст для нейросетей», а слой страницы, который можно взять в ответ без искажения.

## Выжимка для агента

1. **`title` по шаблону типа страницы: предмет и город — в первых 55 знаках, бренд — в конце;** «title = бренд» —
   типичный провал модели. `[документация: G]` {meta} → §2
2. **2–3 варианта `title` с разным отличием-фактом** и планом теста в `meta.test_plan`. `[практика: G 02 §4.3; W2]` {meta} → §2
3. **`description` ≠ `title`:** что делаете и где + 1–2 факта + снятие риска; RU 110–180 знаков. `[документация: G]` {meta} → §2
4. **Ответ FAQ — первым предложением** (да / нет, число, условие), 1–3 предложения, абзац понятен без страницы.
   `[практика: G COPY-GEO-08, 09, 14]` {landing, geo} → §2
5. **Вопросы FAQ — только из голоса клиента и возражений иерархии** (`where: faq`), не «Почему выбирают нас?».
   `[практика: E 02 §9]` {landing, site-page} → §2
6. **Никакой «добавленной статистики», экспертов и второй «версии для ИИ»:** «+40 % GEO» получено на выдумке, Google
   просит не дробить текст ради моделей. `[исследование: Aggarwal 2024 с разбором G]` + `[документация: Google]` {geo} → §2
7. **Скоропортящийся факт — с датой «на …» в том же предложении.** `[стандарт базы: COPY-GEO-03]` {geo, meta} → §2

## 1. Входы и выход

| Переменная | Откуда | Проекция |
|---|---|---|
| `{{PAGE_HEADER}}` | copy deck | `page_type`, `lang`, `awareness`, бренд (`product_name`), главный запрос (`article.main_query`, если есть), выбранные H1 и подзаголовок |
| `{{META_TEMPLATE}}` | `meta-rules.yaml → templates[page_type]` | `title`, `description`, `example_ru`, `facts` |
| `{{META_LIMITS}}` | `meta-rules.yaml → limits` | `write`, `key_phrase_within`, `key_info_within` для языка |
| `{{FACTS}}` | `facts.yaml` | факты шаблона и секции FAQ: `id`, `verbatim`, `canonical`, `requires_nearby`, даты |
| `{{NEVER_CLAIM}}` | `facts.yaml` | `id`, `text` |
| `{{FAQ_QUESTIONS}}` | иерархия + `meaning.objections` + `voc.yaml` | вопросы с источником: `obj-…` с `where: faq`, `voc:…` |

Выход — `page.meta` и секция `faq` copy deck (`copy-deck.schema.json → $defs/meta`, `$defs/section`).

## 2. Промт RU

```text
// модель: генератор из кандидатов 09/01 §2.1, t 0,7 для вариантов title · 2026-09-24 · [не проверено]
// id: p5-meta-geo/ru@1 · выход: YAML meta + секция faq · проверка: copydeck.py check (meta-*, geo-*, meta-x-*)
Ты — редактор поисковых текстов. Напиши мета страницы и ответы FAQ так, чтобы их можно было взять в сниппет и в ответ
поисковика с ИИ без искажения смысла.

ВХОД
<page>{{PAGE_HEADER}}</page>
<template>{{META_TEMPLATE}}</template>
<limits>{{META_LIMITS}}</limits>
<facts>{{FACTS}}</facts>
<never>{{NEVER_CLAIM}}</never>
<faq_questions>{{FAQ_QUESTIONS}}</faq_questions>

МЕТА
1. title — по <template>: услуга, где, отличие-факт, бренд в конце. Предмет и город — в первых 55 знаках; длина — в
   пределах <limits>. Напиши 2–3 варианта с разным отличием (гарантия, срок, цена «от»).
2. description — что делаете и где, 1–2 факта, снятие риска первого шага; не повторяет title и не начинается с него.
3. og_title — как title без бренда или короче; og_description — одно предложение: что человек получит, открыв ссылку.
4. Числа и условия — только из <facts>, их id — в meta.fact_ids; год — только год самого факта.
5. Нельзя: title из одного бренда или «Главная»; слово запроса больше двух раз; перечень городов; кликбейт;
   «лучший», «№ 1», «самый».

FAQ
6. Вопросы — только из <faq_questions>, словами клиента; у ответа в notes — id источника вопроса.
7. Первое предложение ответа отвечает: да или нет, число, условие, выбор. Дальше — 1–2 предложения деталей.
8. Абзац понятен без остальной страницы: предмет назван, без «как сказано выше» и местоимения в начале.
9. Факт — формулировкой canonical или verbatim; цена, рейтинг, срок акции — с датой «на …» в том же предложении.
10. Нет факта — [PLACEHOLDER: что нужно] и id в missing_ids; не пиши «зависит от многих факторов».
11. Не делай второй «версии для ИИ»: блоков, которые повторяют страницу короткими кусками; не добавляй статистику,
    цитаты экспертов и источники, которых нет в <facts>.

ВЫХОД — один YAML-документ без пояснений:
meta:
  title: "…"                          # вариант a
  description: "…"
  og_title: "…"
  og_description: "…"
  fact_ids: ["…"]
  variants:
    title:
      - {id: a, text: "…", status: draft, source: model}
      - {id: b, text: "…", status: draft, source: model}
  test_plan: "варианты title — Вебмастер и Search Console, 4 недели, CTR"
  review_by: "ГГГГ-ММ-ДД"             # через 12 месяцев
faq_section:
  section_id: faq
  section_role: faq
  question: "…"
  slots:
    - {slot_id: q1, slot_type: faq-q, group: q1, variants: [{id: a, text: "…", status: draft, source: model}], chosen: a, fact_ids: []}
    - {slot_id: a1, slot_type: faq-a, group: q1, variants: [{id: a, text: "…", status: draft, source: model}], chosen: a,
       fact_ids: ["…"], missing_ids: ["…"], notes: "источник вопроса: obj-…"}
```

## 3. Промт EN

```text
// model: a generator from the 09/01 §2.1 candidates, t 0.7 for title variants · 2026-09-24 · [не проверено]
// id: p5-meta-geo/en@1 · output: YAML meta + faq section · check: copydeck.py check (meta-*, geo-*, meta-x-*)
You are a search copy editor. Write the page's meta and FAQ answers so that a snippet or an AI search answer can quote
them without changing their meaning.

INPUT
<page>{{PAGE_HEADER}}</page>
<template>{{META_TEMPLATE}}</template>
<limits>{{META_LIMITS}}</limits>
<facts>{{FACTS}}</facts>              — use translations.en when present
<never>{{NEVER_CLAIM}}</never>
<faq_questions>{{FAQ_QUESTIONS}}</faq_questions>

META
1. title — per <template>: service, place, a fact-based difference, brand at the end. Subject and city within the
   first 55 characters; length within <limits> (EN 35–60). Write 2–3 variants with different differences.
2. description — what you do and where, 1–2 facts, what removes the risk of the first step; it neither repeats nor
   starts with the title.
3. og_title — the title without the brand or shorter; og_description — one sentence: what the reader gets by opening it.
4. Numbers and conditions only from <facts>; their ids go to meta.fact_ids; a year only if it is the fact's year.
5. Never: a brand-only or "Home" title; the query phrase more than twice; lists of cities; clickbait; best, #1.

FAQ
6. Questions only from <faq_questions>, in the customer's words; the answer's notes cite the question source id.
7. The first sentence answers: yes or no, a number, a condition, a choice. Then 1–2 sentences of detail.
8. The paragraph stands alone: the subject is named, no "as mentioned above", no pronoun at the start.
9. Facts in canonical or verbatim wording; prices, ratings and offer deadlines carry an "as of" date in the same sentence.
10. No fact → [PLACEHOLDER: what is needed] and the id in missing_ids; never "it depends on many factors".
11. No second "version for AI": no blocks that repeat the page in short chunks; no statistics, expert quotes or
    sources that are not in <facts>.

OUTPUT — one YAML document, same keys as the RU version.
```

## 4. Выход и проверки после вызова

1. Код переносит `meta` в `page.meta`, секцию `faq_section` — в `page.sections` (перед `final-cta`), дописывает
   `generated` у вариантов.
2. `copydeck.py check`: правила `meta-*` (линтер C через `external_rules`), `COPY-D-META-LEN`, `meta-x-missing`,
   `meta-x-desc-equals-title` (validate J), сверка чисел мета (`claims_check.py`, псевдосекция `__head`).
3. Судья P7 — вопросы G `COPY-GEO-08, 09, 11` на ответах FAQ (сигнал до калибровки, COPY-C-22).
4. Человек выбирает `title` (или оставляет варианты для теста CTR, LT-09 W2-6).

## Частые ошибки

1. **«Отвес — ремонт квартир» и «Главная»:** бренд впереди предмета, запроса нет.
2. **description = title с хвостом** — Яндекс считает это дублем.
3. **FAQ «Почему выбирают нас?»** — вопрос не клиента, ответ — реклама.
4. **Ответ с разгоном:** «Стоимость ремонта рассчитывается индивидуально…» — пример naive из `geo-checklist.yaml`.
5. **Производное число без записи:** «двушка 54 м² — от 529 200 ₽» — сверка его не подтвердит (G 03-geo-rewrite).

## Чек-лист

1. `title` по шаблону, предмет и город в первых 55 знаках, 2–3 варианта?
2. `description` не повторяет `title` и несёт 1–2 факта?
3. Вопросы FAQ — из голоса клиента или возражений, с id источника?
4. Первое предложение каждого ответа — ответ?
5. Все числа мета и FAQ — с `fact_ids`, скоропортящиеся — с датой?

## Открытые вопросы и противоречия

1. Промт по шаблонам G против промта без шаблонов (G4): уходит ли «title = бренд» — LT-09, ≈ 40 тыс. токенов.
2. Ширина выдачи не документирована: 55 знаков — оценка G по пикселям, `[мнение вендора]`; проверка — G6.
3. Факты `use` B2 не разрешают мета (`COPY-F-USE` на законных местах — находка J/01); до правки B2 — предупреждения.

## Источники

- G `../../07-seo-geo-copy/meta-rules.yaml` (`templates`, `limits`, `checks_outside_linter`), `geo-checklist.yaml`
  (COPY-GEO-01…28, пример `faq-a`), `02-seo-pages-articles-meta.md` §4, `03-geo-copy.md`.
- E `../../04-copy-by-block/02-section-blocks.md` §9 (FAQ — остаток после секций).
- J `../../10-templates-recipes/copy-deck.schema.json` (`$defs/meta`, `variants.title`, `test_plan`, `review_by`).
- W2 — дайджесты Google Search Off the Record и Яндекса (через `99-raw/reports/wave2-W2-report.md` §2).
- Опыт I/04 — `99-raw/experiments/I/04-chain-manual/README.md` (шаг S7).
