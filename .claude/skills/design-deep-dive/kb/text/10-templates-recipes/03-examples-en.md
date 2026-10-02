# Примеры copy deck на английском: две адаптации русских страниц

Волна 3 · агент J (фаза 2 — J3) · 2026-09-24 · внешних источников 0 · тексты `ai-self` J3 · факты вымышленные или ДЕМО ·
опыт `99-raw/experiments/J/08-examples/` · формат — `copy-deck.schema.json` v1.1.

Второй язык — адаптация, а не перевод (решение заказчика п. 16): отдельный copy deck с `source_lang: ru`, `source_ref`,
`adaptation {mode, audience_note, voice_line}` и свой `facts.yaml` на английском с теми же id. Обе страницы — 0 error во
всех пяти проверках; выгрузка в `copy.md` — со строкой голоса на английском.

## Выжимка для агента

1. **Свой английский `facts.yaml` с теми же id**, а не `translations.en` в русском файле: сверка сравнивает объект счёта
   (`values[].what`), условие «рядом» и цитаты на языке факта; русский `what` даёт `COPY-F-NUM-MISMATCH` на верном английском
   тексте (I/04, E/03). `[проверено]` все → §2
2. **`source.quote` не переводится**: основание факта — русские слова заказчика; английский `verbatim` — адаптация с
   заметкой в `notes`. `[практика: B2]` все → §2
3. **Ограничение сверки B2 (не норма языка): число без запятой тысяч с пометкой** — до разбора разделителя по `lang`
   «₽9,800» сверка и `lint-facts` читают как 9,8 (`COPY-F-INFERRED` — «слова факта не подтверждены выдержкой»); «₽9800»
   проходит. У «Окошка» E «2,490 ₽» проходит, потому что и выдержка источника английская с той же запятой. Норма EN —
   «9,800» (H `../08-russian-legal-typography/02-typography-for-marketing.md` §7). `[проверено]` все → §2
4. **id страниц, секций и слотов — как в исходнике**: пути `copy:<page>/<section>/<slot>` общие для языков; лишнее для
   аудитории снимается, новое не выдумывается. `[практика: J]` все → §1
5. **Реалию объясняет одна вставка**: «Sormovo, a district of Nizhny Novgorod», «9:00 to 21:00 Moscow time». `[практика: I 02 §6]` все → §3
6. **Цены российской компании — в рублях** и на английской странице (38-ФЗ ст. 5 ч. 7.1, H). `[стандарт]` {landing, site-page} → §3
7. **Перевод цитаты помечен рядом**: «Anna K., Nizhny Novgorod (translated from Russian)» (B2 §5.1); цена пометки —
   подпись длиннее границы E (warning, provisional). `[проверено]` {landing, site-page} → §3
8. **Число — формой факта и на английском**: «The contract set 50 working days; we handed the flat over in 47» →
   `COPY-F-NUM-MISMATCH`; «It took 47 working days against the 50 set in the contract» проходит. `[проверено]` все → §4
9. **Объект счёта — словами факта**: «For a team of up to 5» → `NUM-MISMATCH` («объект счёта другой»); «For up to 5 stylists» проходит. `[проверено]` все → §4
10. **Длина — по английским колонкам E** (основная единица — слова; грубая граница знаков тоже срабатывает): строка у
    цены 13 слов / 85 знаков → `COPY-D-LEN`; «Labour only, materials not included.» — в границах. `[проверено]` {landing} → §4
11. **Строка «Voice:» на языке страницы**: у профилей F проекция `tone_of_voice` только русская — без
    `adaptation.voice_line` выгрузка даёт warning `COPY-D-LANG` (новое поле v1.1). `[проверено: J/08, selftest]` все → §5
12. **Never claim в `facts.md` — по-английски**: строки проекта — из английского `facts.yaml`, умолчания B2 — английская
    адаптация J (`NEVER_EN`); строки «Typography is final…» для EN нет. `[проверено]` {landing} → §5

## 1. Набор

| Файл | Исходник | Тип страницы | Факты (EN, те же id) | Голос F | Что сделано при адаптации |
|---|---|---|---|---|---|
| `examples/en-otves-case.yaml` | `ru-otves-case.yaml` | `case-page` | `examples/facts/facts-otves-en.yaml` (J3: 6 фактов B2 на английском; verbatim цены, сметы, гарантии — оверлей F/04) | `voice-otves-warm` + `voice_line` EN | аудитория — англоязычные жители Нижнего Новгорода, впервые нанимающие подрядчика; «замерщик» → site visit; район объяснён; перевод цитаты помечен |
| `examples/en-okoshko-saas.yaml` | `ru-okoshko-saas.yaml` (E3) | `landing-saas` | `examples/facts/facts-demo-saas-okoshko-en.yaml` (копия ДЕМО E) | `voice-grafa-b2b`* + `voice_line` EN | аудитория — англоязычные владельцы салонов в городах РФ; сняты тариф «Сеть», SMS, годовая скидка и FAQ; время поддержки — Moscow time |

\* Своего профиля голоса у «Окошка» нет — профиль F «Графа» как ближайший (решение J3, как у русской страницы).

| Пример | Секций | Слотов | С `fact_ids` | Слов | Ядро первого экрана, слов | Заглушек |
|---|---|---|---|---|---|---|
| `en-otves-case` | 5 | 16 | 10 | 214 | — (нет секции hero) | 0 |
| `en-okoshko-saas` | 7 | 32 | 26 | 309 | 35 | 1 (реквизиты) |

Английский текст кейса длиннее русского на 23 % по словам (214 против 174): артикли и вставки-объяснения; у «Окошка»
— короче (309 против 367) за счёт снятых слотов.

## 2. Факты второго языка

`facts-otves-en.yaml` собран скриптом из `facts-service-renovation.yaml` B2: те же id, `lang: en`, английские `verbatim`,
`canonical`, `values[].what` и `requires_nearby`; `source`, `verification`, `permission`, `use` — как у исходника;
`translations` сняты; сущности — английскими именами (Otves, Nizhny Novgorod, Sormovo, Anna K.); `never_claim` проекта —
с английскими шаблонами («best renovation in the city», «the estimate never changes»). Проверки: `claims_check.py
lint-facts` — 0; схема B2 (jsonschema) — 0; проба сверки на трёх строках — 0 error.

Одна находка при сборке — формат числа: `lint-facts` дал `COPY-F-INFERRED` на «₽9,800» (выдержка источника — «от 9 800
руб.», запятая читается как десятичная). Исправлено формой «₽9800» во всех английских текстах и фактах.

## 3. Как адаптировано (а не переведено)

| Место | Русский исходник | Английская адаптация | Почему |
|---|---|---|---|
| действие | «Вызвать замерщика» | «Book a site visit» | «замерщик» — местная роль; английский покупатель ищет визит на объект |
| место | «в Сормове» | «in Sormovo, a district of Nizhny Novgorod» | реалия — одной вставкой |
| отзыв | «Анна К., Нижний Новгород» | «Anna K., Nizhny Novgorod (translated from Russian)» | перевод цитаты помечается рядом (B2 §5.1) |
| время | «с 9:00 до 21:00 по Москве» | «9:00 to 21:00 Moscow time» | часовой пояс явно |
| цена | «от 9 800 ₽ за м²» | «from ₽9800 per m²» | рубли остаются (H); форма числа — под сверку |
| объём | 40 слотов «Окошка» | 32 слота | аудитории не нужны SMS-тариф, годовая скидка, сетевой тариф |

## 4. Результаты проверок

`python3 ../../scripts/text/run_checks.py` — error / warning / info:

| Пример | `claims_check.py --legal-category general` | `copy_lint.py` | `copydeck.py check` | `copydeck.py validate` | `validate` + jsonschema |
|---|---|---|---|---|---|
| `en-otves-case` | 0 / 5 / 0 | 0 / 0 / 0 | 0 / 5 / 5 | 0 / 0 / 4 | 0 / 0 / 4 |
| `en-okoshko-saas` | 0 / 0 / 0 | 0 / 1 / 4 | 0 / 3 / 10 | 0 / 1 / 5 | 0 / 1 / 5 |

Остаток warning: `COPY-F-USE` в мета (5 + 1 — формат `use` B2), заглушка реквизитов у «Окошка», `COPY-D-LEN` у подписи
отзыва с пометкой перевода (57 знаков > 55, граница provisional).

Пары «до / после» английской сборки (строки — в `before-after.tsv`, источник `J3-examples`):

| До | После | Что поймало |
|---|---|---|
| «The contract set 50 working days; we handed the flat over in 47…» | «It took 47 working days against the 50 set in the contract…» | `COPY-F-NUM-MISMATCH` |
| «For a team of up to 5: online booking and Telegram reminders for everyone» | «For up to 5 stylists: online booking and Telegram reminders for each of them» | `COPY-F-NUM-MISMATCH` (объект счёта) |
| «Labour only, materials not included. The estimate shows the total for your apartment.» | «Labour only, materials not included.» | `COPY-D-LEN` (13 слов / 85 знаков) |

## 5. Выгрузка английской страницы

`export-kimi` черновиков (без `--strict`: у «Окошка» заглушка реквизитов) — exit 0 у обеих: в `copy.md` — заголовок
`# COPY — all texts of Otves, verbatim (en)`, строка `Voice:` из `adaptation.voice_line`, без строки о русской типографике;
в `facts.md` — английские verbatim фактов и Never claim на английском (проект — из английского `facts.yaml`, умолчания B2 —
`NEVER_EN`). Без `voice_line` строка голоса была бы русской (проекция F) — теперь это warning `COPY-D-LANG` при выгрузке.

## Частые ошибки

- **Перевод русского deck с русскими фактами**: верный английский текст получает `NUM-MISMATCH` и `NAME` — нужен свой
  `facts.yaml` с теми же id.
- **Запятая тысяч**: «1,146», «9,800» сверка читает как десятичную дробь.
- **Калька голоса**: «dear customer», «we are happy to offer», восклицания — не голос F; строка голоса — `voice_line`.
- **Реалия без объяснения** («Sormovo» без «a district of Nizhny Novgorod») или объяснение абзацем вместо вставки.
- **Перевод цитаты без пометки** — цитата выглядит как слова клиента на английском.
- **Новые обещания при адаптации**: английская страница не получает фактов, которых нет в исходнике.

## Чек-лист

- [ ] `source_lang`, `source_ref`, `adaptation.mode: adaptation`, `audience_note`, `voice_line` заполнены?
- [ ] Свой английский `facts.yaml` с теми же id, `lint-facts` — 0?
- [ ] Числа без запятой тысяч или с той же запятой в выдержке источника?
- [ ] id страниц, секций и слотов совпадают с исходником?
- [ ] Цены — в рублях, время — с часовым поясом, реалии — одной вставкой?
- [ ] Переведённые цитаты помечены рядом?
- [ ] Все пять проверок — 0 error; `export-kimi` — строка Voice на английском?

## Открытые вопросы и противоречия

- **Проекция голоса F одноязычная** — `adaptation.voice_line` закрывает выгрузку, но не проверку: английский словарь
  «не говорим» есть только в оверлеях F/04. Предложение F: `projections.tone_of_voice` и `vocabulary.avoid` по языкам.
- **Формат числа** — ограничение сверки B2, а не правило английского: «9,800» — норма языка. Предложение B2: разбирать
  запятую тысяч по `lang` факта.
- **Кто проверяет английский голос**: F — «человек обязателен для английских страниц»; носитель в живой фазе.

## Источники

- [S1] E (волна 2): `99-raw/experiments/E/facts-demo-saas-okoshko-en.yaml` (копия — `examples/facts/`), опыт E/03 (EN-сверка).
- [S2] F (волна 2): `99-raw/experiments/F/04-voice-samples/en-overlays/otves-remont-nn.yaml`; `05-voice-editorial/voice.schema.yaml` (проекции).
- [S3] B2 (волна 1): `facts.schema.yaml` (`translations`, §5.1 — перевод цитаты), `../02-strategy-messaging/examples/facts-service-renovation.yaml`.
- [S4] I (волна 3): `09-ai-generation-evaluation/02-generation-pipeline.md` §6; заметки I «Для J» (EN-сверка, I/01, I/04).
- [S5] H (волна 2): 38-ФЗ ст. 5 ч. 7.1 — цены в рублях (`08-russian-legal-typography/01` §4).
- [S6] Опыт J/08: `run_checks.py`, `run_variants_and_gates.sh` (выгрузка EN), `stats.py`.
