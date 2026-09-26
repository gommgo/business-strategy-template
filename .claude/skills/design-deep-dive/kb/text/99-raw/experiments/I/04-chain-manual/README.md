# Опыт I/04 — цепочка вручную на брифе «Отвеса»: P1 → смысл → иерархия → copy deck → проверки → правка → судья → выбор

Агент I3 (волна 3, фаза 2), 2026-09-24, 12:09–12:50. Бесплатно: все шаги цепочки выполнил сам агент по промтам
`09-ai-generation-evaluation/prompts/p1…p7` (метка **ai-self**, модель Claude Opus 5.5 — та же, что писала промты); модели
и сервисы не вызывались. Промты остаются `[не проверено]`: опыт проверяет форматы, скрипты-проекции, проверки и протокол,
а не качество генерации модели.

## Цель

1. Пройти цепочку `09-ai-generation-evaluation/02-generation-pipeline.md` на одном брифе (S1–S11) и выполнить обязательства
   промтов: `check_intake.py` (P1), `chain_inputs.py` (`digest-meaning`, `meaning-claims`, `hierarchy-input`,
   `section-input`, `edit-input`, `judge-input`, `judge-score`, `assemble`, `apply-edits`), `make_skeleton.py` (P3 §4),
   иерархия solution-aware (P3, строка I-7 плана).
2. Посчитать, сколько находок снимает каждый шаг, и записать протокол ошибок.
3. Сравнить итог с copy deck B1 (`99-raw/experiments/B1/02-two-hierarchies/deck-otves-ai-self.yaml`, страница problem-aware).

## Вход, версии, команды

- Бриф — `s0-brief.txt` (сообщение заказчика из B1/01, сверено побайтно); смысл — `02-strategy-messaging/examples/meaning-otves.yaml`
  (B1), факты — `facts-service-renovation.yaml` (B2), иерархии — `hierarchy-otves-problem-aware.yaml`, `…-product-aware.yaml`
  (B1), голос — `05-voice-editorial/examples/voice-otves-warm.yaml` (F), слоты — `04-copy-by-block/copy-slots.yaml` (E),
  мета — `07-seo-geo-copy/meta-rules.yaml` (G), право — `08-russian-legal-typography/claims-rules.yaml` (H), рубрика —
  `09-ai-generation-evaluation/copy-rubric.yaml` v1.1.
- Утилиты: `copydeck.py` 1.0 (J), `claims_check.py` 1.0 + правовой модуль 2.0 (H, 66 правил), `copy_lint.py` 0.9.3 (C),
  `validate.py` B1 (через `validate_any.py`, venv B1); Python 3.13.5, PyYAML 6.0.2; `--today 2026-09-24`.
- Свои скрипты (системный `python3`): `check_intake.py` (самотест 7/7), `chain_inputs.py` (самотест 11/11: 8 примеров
  `judge_scoring` рубрики, большинство прогонов, проекция схемы, перенос правки), `make_skeleton.py`, `validate_any.py`.

```bash
E=99-raw/experiments/I/04-chain-manual; EX=02-strategy-messaging/examples; T=../../scripts/text/copydeck.py
python3 $E/check_intake.py $E/s1-intake/intake-otves.yaml --brief $E/s0-brief.txt                         # S1
python3 ../../scripts/text/claims_check.py lint-facts $EX/facts-service-renovation.yaml                          # S2
python3 $E/chain_inputs.py digest-meaning -o $E/s3-meaning/meaning-schema-digest.txt --meaning $EX/meaning-otves.yaml \
  --call-inputs $E/s0-brief.txt $E/s1-intake/intake-otves.yaml                                              # S3
python3 $E/chain_inputs.py hierarchy-input --meaning $EX/meaning-otves.yaml --awareness solution-aware --traffic paid-search \
  -o $E/s4-hierarchy/hierarchy-input-solution-aware.yaml                                                    # S4 (вход P3)
99-raw/tools/venv-B1/bin/python $E/validate_any.py $E/s4-hierarchy/hierarchy-otves-solution-aware.yaml $EX/meaning-otves.yaml
python3 $E/chain_inputs.py meaning-claims --meaning $EX/meaning-otves.yaml --hierarchy $EX/hierarchy-otves-problem-aware.yaml \
  $EX/hierarchy-otves-product-aware.yaml $E/s4-hierarchy/hierarchy-otves-solution-aware.yaml -o $E/s3-meaning/meaning-claims.yaml
python3 $T claims $E/s3-meaning/meaning-claims.yaml --today 2026-09-24 --json $E/s3-meaning/meaning-claims-check.json   # сверка до текста
python3 $E/make_skeleton.py $EX/hierarchy-otves-problem-aware.yaml --facts $EX/facts-service-renovation.yaml \
  --voice 05-voice-editorial/examples/voice-otves-warm.yaml --meaning $EX/meaning-otves.yaml --page-id otves-problem-aware \
  --product-name "Отвес" -o $E/s5-skeleton/skeleton-problem-aware.yaml                                     # S5
python3 $E/chain_inputs.py section-input --deck $E/s5-skeleton/skeleton-problem-aware.yaml --page otves-problem-aware \
  --section hero --hierarchy $EX/hierarchy-otves-problem-aware.yaml --meaning $EX/meaning-otves.yaml \
  --voice 05-voice-editorial/examples/voice-otves-warm.yaml -o $E/s6-deck/inputs/in-hero.yaml             # S6 (по секции)
python3 $E/chain_inputs.py assemble --skeleton $E/s5-skeleton/skeleton-problem-aware.yaml \
  --parts $E/s6-deck/p4-out-sections.yaml $E/s6-deck/p5-out-meta-faq.yaml --by "…" -o $E/s6-deck/deck-v1.yaml   # S6–S7
python3 $T check $E/s6-deck/deck-v1.yaml --today 2026-09-24 --json $E/s8-checks/run1-check.json          # S8
python3 $E/chain_inputs.py edit-input --deck $E/s6-deck/deck-v1.yaml --check $E/s8-checks/run1-check.json --pass 1 -o …   # S9
python3 $E/chain_inputs.py apply-edits --deck $E/s6-deck/deck-v1.yaml --edits $E/s9-edit/p6-pass1-edits.yaml --pass 1 --by "…" -o $E/s6-deck/deck-v2.yaml
python3 $E/chain_inputs.py judge-score --answers $E/s10-judge/answers-i04.json $E/s10-judge/pairwise-headline-i04.json -o $E/s10-judge/scores-i04.yaml   # S10
python3 $T export-variants $E/s6-deck/deck-v4.yaml -o $E/s11-blind/variants-sheet.md --key $E/s11-blind/variants-key.yaml --seed 7   # S11
```

## Результат по шагам: что нашёл каждый шаг

| Шаг | Что сделано (файл) | Находки | Кто нашёл |
|---|---|---|---|
| S1 P1 | `s1-intake/intake-otves.v1.yaml` → `intake-otves.yaml` v2 | v1: 0 error, 2 warning — 7 вопросов + 3 просьбы документов = 10 просьб (W1); допущение о фото не в `going_with` (W2). v2: 0/0. При сверке с B1/B2 — пробел «пункт о гарантии» привязан к вопросу, в тексте которого гарантии нет | код (2), человек (1) |
| S2 анкета | факты B2 как ответы заказчика | `lint-facts`: 1 error — отзыв Игоря с разрешением `pending` (задумано B2) | код |
| S3 P2 | смысл B1 как выход шага | `validate.py` 0/0; доли оснований: brief 11, fact 12, inferred 14, assumption 8 (18 % < 30 % — идти дальше); проекция схемы 4 277 знаков против 39 605 | код |
| S3–S4 сверка смысла до текста | `s3-meaning/meaning-claims*.{yaml,json}`: смысл + 3 иерархии, 68 слотов | 10 error: «12 лет» ×4 (вывод из «с 2014 года»; 2 — в `core_message` и hero product-aware), отзыв без разрешения в ответе на возражение, «бесплатно» без «в черте города» — верные (6); «не обещать „смета никогда не меняется“» (NEVER + QUOTE) и служебное «без таймеров» — ложные (3); «доплаты» в сообщении problem — спорно (1). Warning: условия не рядом (NEARBY, FREE-01) — 33, `use` фактов вне ролей проекции — 54 (шум проекции) | код |
| S4 P3 | `s4-hierarchy/hierarchy-otves-solution-aware.yaml` (ai-self) | `validate.py` 0/0 (9 секций, 5 опор, 56 ссылок); сверка до текста — 0 error, 1 NEARBY (дата рейтинга не в дословной форме B2) против 2 error и 13 NEARBY/FREE у иерархий B1 | код |
| S5 скелет | `s5-skeleton/skeleton-problem-aware.yaml` | 10 секций, 50 слотов, 56 вариантов к написанию; сообщение hero «объект ведёт один прораб» без `missing:foreman-per-object` в доказательствах hero — противоречие иерархии B1 | человек (при письме) |
| S6–S7 P4, P5 | `s6-deck/p4-out-sections.yaml`, `p5-out-meta-faq.yaml` → `deck-v1.yaml` | входы P4 — 9–17 тыс. знаков на секцию (≈ 2,1–6,0 тыс. токенов [оценка]); FAQ сократился до 2 вопросов из 5: fallback пробелов `omit-block` и `rewrite-without` | — |
| S8 check | `s8-checks/run1-check.json` | 3 error: «срок работ» в договоре по одному кейсу (EXTENDS) и «до гарантии» в OG без срока (CLASS) — верные; «ипотека» в ситуации клиента (CLASS income-finance) — ложная; 20 warning: `use` 15, типичность отзыва 1, заглушки 3, `ux-1-11` 1 (ложная); 71 info (типографика, неразрывные пробелы) | код |
| S9 P6 проход 1 | `s9-edit/p6-pass1-edits.yaml`, `p6-pass1b-edits.yaml` | 3 правки → run2: 1 error — правка OG породила новую (EXTENDS: два факта в одной фразе); итерация 1b → run3: 0 error | код |
| S9 P6 проход 2 | `s9-edit/p6-pass2-edits.yaml` | 0 правок текста; 1 `lint_allow` (ложная `ux-1-11`); 4 записи человеку (типичность отзыва, 3 заглушки, формат `use` B2) → run4: 0 / 18 / 69. Проход 3 не понадобился | P6 + код |
| S10 P7 | `s10-judge/answers-*.json`, `scores-*.yaml` | судья нашёл, чего не видит код: «Срок и смета — в договоре» без записи фактов (COPY-R-03 q1); блокер «смета вырастет по ходу» без ответа (COPY-R-08 q1); ответ FAQ про предоплату не отвечает первым предложением (COPY-GEO-08); попарно заголовки: b > a > c, доля «A» 0,5 | судья (ai-self) |
| S11 выбор | `s11-blind/variants-sheet.md`, `variants-key.yaml` | лист на 3 слота (заголовок, подзаголовок, кнопка) без авторов; варианты title мета в лист не попали | — |

Проход проверок с `--all-variants` (`s8-checks/run5-check-all-variants.json`): 4 error, из них 3 — на **отклонённых**
вариантах (сверка `claims_check.py` в этом режиме их не пропускает, линтер пропускает) и 1 — на невыбранном варианте
подзаголовка c: `fact_ids` у слота общие, вариант с другим фактом (estimate-free) получает EXTENDS и FREE-01.

## Протокол ошибок (что было не так и чем исправлено)

| № | Шаг | Ошибка | Поймал | Исправление | Вид сбоя |
|---|---|---|---|---|---|
| 1 | S1 | 10 просьб к заказчику при лимите 7 (документы отдельным абзацем) | `check_intake.py` W1 | документы — внутри тематических вопросов (B2 proof-intake §4) | анкета вместо вопросов |
| 2 | S1 | допущение «фото получает каждый клиент» не в `going_with` | `check_intake.py` W2 | строка в `going_with` | допущение без умолчания |
| 3 | S1 | пробел «пункт о гарантии» привязан к вопросу без слова «гарантия» | человек (сверка с B2) | дописано в вопрос | формальная связь |
| 4 | S3 (B1) | «12 лет» в опоре и главном сообщении (вывод из «с 2014 года») | `meaning-claims` → claims | в solution-aware не писал; строка в `must_not_say` | выдуманная конкретика (производное число) |
| 5 | S3 (B1) | ответ на возражение опирается на отзыв без разрешения | `meaning-claims` → claims | в тексте отзыв Игоря не использован | факт без разрешения |
| 6 | S5 (B1) | сообщение hero сильнее своих доказательств («один прораб») | человек при письме | писал «за мастерами следит прораб» без «одного на весь ремонт» | опора без факта в первом экране |
| 7 | S6 | «В договор записываем срок работ» — обобщение одного кейса | claims EXTENDS | утверждение снято (`rewrite-without`) | шире факта |
| 8 | S7 | «до гарантии» в OG без срока и предмета | claims CLASS | «до гарантии 3 года на работы» | условие факта не рядом |
| 9 | S9 | правка 8 склеила два факта в одной фразе → новая error | claims EXTENDS | бесплатность убрана из OG | правка порождает находку |
| 10 | S10 | «Срок и смета — в договоре» (hero, FAQ) — записи фактов нет | судья COPY-R-03 q1 | человеку: нужен факт о типовом договоре | утверждение смысла без факта |
| 11 | S10 | блокер «смета вырастет по ходу» без ответа | судья COPY-R-08 q1 | человеку: пункт договора (estimate-change-policy) | пробел фактов |

Ложные находки: «ипотека» (CLASS income-finance, снята правкой — `lint_allow` находки сверки не снимает), `ux-1-11` на
«решение о договоре» (`lint_allow`), NEVER + QUOTE на цитате запрета в смысле, EXTENDS на служебном «без таймеров».

## Сравнение с copy deck B1 (страница problem-aware, те же иерархия, факты и утилиты)

| Показатель | deck B1 (wave 1, без P4) | deck I/04 (P4, P5, P6) |
|---|---|---|
| секций / слотов / вариантов | 7 / 15 / 15 | 10 / 50 / 55 живых + 2 отклонённых |
| мета и FAQ | нет | title (3 варианта), description, OG; FAQ — 2 вопроса |
| слов на странице | 165 | 462 |
| `copydeck.py check` | 0 error, 15 warning, 37 info | 0 error, 18 warning, 69 info (первый черновик — 3 error) |
| утверждений / с фактом | 17 / 17 | 52 / 51 (одно — «предоплату» в вопросе FAQ) |
| условие факта не рядом (NEARBY, FREE-01) | 4 | 0 |
| заглушки | 2 (правило прораба, формат отчёта) | 3 (оплата ×2, реквизиты) — пробелы с `placeholder`; с `rewrite-without` — текст без утверждения |
| длина вне p10–p90 или грубой границы E | 7 warning `COPY-D-LEN` | 0 warning, 2 info |
| маркеры слопа на 100 слов / конкретика | 0,61 / 5,9 | 0,22 / 10,3 |
| судья (ai-self), баллы 01–09 | 5, 3, 1, 3, 4, 3, 5, 2, 5 (сумма 31) | 5, 3, 1, 5, 5, 3, 5, 2, 5 (сумма 34) |

Разница по судье — в позиции и альтернативе (COPY-R-04 q3: B1 не называет подход, от которого уводит), глубине
аргумента (COPY-R-05 q4) и условиях факта (COPY-R-03 q3, COPY-R-08 q2 — «бесплатно» без «в черте города» у B1). COPY-R-03
у обоих — 1: потолок `cap_if_no: 1` вопроса q1 срабатывает на одном несопоставимом утверждении («Срок и смета — в
договоре» есть у обоих) и прячет разницу по условиям — она видна только в ответах.

## Вывод

1. **Сверка смысла до текста окупается:** 6 верных error на смысле и иерархиях B1 (производное «12 лет» ×4, отзыв без
   разрешения, «бесплатно» без условия) нашлись до того, как попали в заголовки; иерархия, написанная после этой сверки,
   дала 0 error.
2. **Код ловит числа и условия, судья — утверждения без чисел:** «Срок и смета — в договоре» прошло сверку везде, где у
   слота не был объявлен факт, и поймано только вопросом судьи COPY-R-03 q1; поэтому порядок «код → судья → человек» нужен
   весь.
3. **Fallback пробела решает объём страницы:** `rewrite-without` и `omit-block` сняли карточку «ход работ виден», три
   вопроса FAQ и «один прораб» из первого экрана — страница честнее, но беднее; расширить её может только ответ
   заказчика (6 записей `left_for_human`).
4. **Правка по находкам сходится за два прохода**, если промт текста уже несёт правила: проход 1 — 4 правки (одна
   породила новую error), проход 2 — ни одной правки текста. Стилевых warning на первом черновике — 1 (и та ложная).
5. **Ограничения:** исполнитель знает смысл, факты и рубрику (верхняя граница качества, а не замер модели); судья — та же
   модель, что писала (самопредпочтение, порядок в попарном режиме не мог повлиять); один бриф, одна страница; прогоны
   не повторялись. Проверка моделями — строки плана LT-01…LT-04, I-7, I-8, I-9.

## Находки для соседей (в заметки «Для J», «Для B2», «Для B1»)

- **J:** `check --all-variants` сверяет и отклонённые варианты (claims), а линтер — нет; `fact_ids` — на слот, а варианты
  опираются на разные факты (предложение: `variant.fact_ids`); `export-variants` не выносит `meta.variants.title`.
- **B2:** `use` фактов не называет how-it-works, faq, testimonials и мета — 14 warning на законных местах (как J/01 №1);
  COPY-F-CLASS «ипотека» в ситуации клиента (income-finance) — ложное срабатывание, которое нельзя снять `lint_allow`.
- **B1:** `proof_status: has-proof` у опоры с `missing:` в доказательствах (pl-contract) — частичное доказательство
  выглядит полным; `core_message` problem-aware утверждает «один прораб» без `missing:foreman-per-object`; «12 лет» в
  `core_message` product-aware — числа нет в фактах.
- **G:** пример `landing-lead-services` в `meta-rules.yaml`: description начинается с тех же 42 знаков, что title.
