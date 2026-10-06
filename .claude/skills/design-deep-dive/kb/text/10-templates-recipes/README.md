# 10-templates-recipes — формат copy deck, процесс, примеры страниц RU и EN, пары «до / после»

Волна 3 · агент J (фаза 1 — J и J2, фаза 2 — J3) · 2026-09-24 · итог обеих фаз · опыты `99-raw/experiments/J/01–08`.

Вопрос базы 15 (`PLAN.md`): как выглядит copy deck, как он проходит проверки и утверждение и как стыкуется с `page-plan` и
`blocks.yaml` site, пакетом kimi и планом ассетов ai-media. Copy deck — единственное место текста страницы: из него
собираются пакет kimi, строки ассетов и лист слепого выбора; руками `copy.md`, `facts.md`, `checked` и `approved` не пишутся.

## Файлы

| Файл | Что внутри |
|---|---|
| `copy-deck.schema.json` | JSON Schema 2020-12 (`urn:app-design:text:copy-deck:1`, `date`, `x-status` v1.1): все поля черновика v0 из PLAN + поля v1 и v1.1; `x-v0-fields` (страж T2), `x-status-rules`, `x-kimi-map`, `x-asset-map`, `x-claims-map`, `x-site-map`, `x-vocabulary-proposals`, пример |
| `01-copy-deck-workflow.md` | процесс от черновика до пакета: статусы и переходы, проверки на каждом, два пути линтера, точки человека (цепочка I S1–S11, пункты `COPY-C-…`), варианты и слепой выбор, правка по находкам, второй язык, выгрузка в kimi, ассеты, спецификация `verify-page` |
| `02-examples-ru.md` | шесть русских страниц: набор, как собраны, результаты пяти проверок, путь страницы кейса до пакета kimi, варианты вебинара, ворота черновика, пары «до / после» сборки |
| `03-examples-en.md` | две английские адаптации: свои факты с теми же id, что адаптировано, проверки, выгрузка |
| `examples/ru-*.yaml`, `examples/en-*.yaml` | 8 copy deck v1.1: `ru-otves-lead`, `ru-okoshko-saas`, `ru-kvarts-preorder` (основы E3), `ru-okoshko-webinar`, `ru-otves-case`, `ru-otves-article-faq`, `en-otves-case`, `en-okoshko-saas`; все — 0 error в пяти проверках |
| `examples/facts/` | ДЕМО-факты вебинара (J3), английская адаптация фактов «Отвеса» (J3), копии ДЕМО-фактов E «Окошко» RU и EN (с md5 источника) |
| `before-after.tsv` | 540 пар «до / после»: колонки ux `before, after, rule_ref, lang, why` + `genre`, `marker_id`, `evidence` (доказательность) |
| `README.md` | этот файл |

Утилита — `scripts/text/copydeck.py`: copy deck и пустой `why` в `before-after.tsv` (`before-after`); описание — `scripts/text/README.md`.

## Выжимка (10 строк)

1. Корень `copy_deck`; поля v0 не удаляются и не переименовываются (T2); путь к тексту — `<page>/<section>/<slot>`, из других
   баз — `copy:<путь>`; у второго языка пути те же.
2. Статус слота = статус выбранного варианта: `checked` ставит `check --update --promote` (0 error сверки и линтера,
   `text_hash`), `approved` — только человек (`approve --by`); правка после проверки снимает статус (`COPY-D-HASH`).
3. Порядок проверок: `claims_check.py` (факты B2 + право H) → `copy_lint.py` (стиль) → `validate` (формат, статусы, пробелы,
   файлы волны 2); `copydeck.py check` делает всё сразу, пробелы и `fallback` B2 — при любом прогоне.
4. Каждое число, имя, дата, цитата, рейтинг, цена, гарантия — `fact_ids` (у варианта со своими фактами — `variant.fact_ids`);
   пробел — `[PLACEHOLDER: …]` + `missing_ids`, а при `fallback: omit-block | rewrite-without` — снять блок или переписать.
5. Обещание первого экрана — `promise` (свои варианты или `from` на слот) → `product.goal` kimi; поля брифа сверяются как
   текст страницы (урок «Кварца»).
6. Варианты сверяются «как выбранные» (`check --all-variants`: копия страницы с одной заменой, отклонённые не сверяются),
   итоги — в отчёте; выбирает человек: `select` открыто или вслепую по листу `export-variants` (мета тоже).
7. `lint_allow` снимает только находки линтера C (с причиной); находки сверки и формата — правкой текста или фактов.
8. Второй язык — отдельный deck с `source_lang`, `adaptation {mode, audience_note, voice_line}` и своим `facts.yaml` с теми же
   id; числа — без запятой тысяч с пометкой: ограничение сверки B2, не норма языка (норма EN — «9,800», H `08/02` §7).
9. Пакет kimi — только `export-kimi --strict` из утверждённой страницы → `build_package.py build` и `check`; ворота
   честности — в copy deck (проверка kimi не видит пустой источник у id B2).
10. Примеры — 8 страниц, 0 error во всех проверках; остаток warning — формат `use` B2 (`COPY-F-USE` на мета, FAQ, статье),
    заглушки пробелов, типичность отзыва; пары «до / после» — 540, у каждой доказательность.

## Поля v1 и v1.1 сверх v0

| Уровень | Поля (все необязательные) | Зачем |
|---|---|---|
| deck | `product_name`, `source_ref`, `adaptation {mode, audience_note, voice_line (v1.1)}`, `meaning_ref`, `copy_slots_ref`, `page_plan_ref`, `jurisdiction`, `legal_category`, `authors`, `notes` | заголовки пакета kimi, второй язык, право H, связь со смыслом B1 |
| page | `site_page_id`, `genre`, `status`, `approval`, `reason`, `hierarchy_ref`, `awareness`, `promise`, `cta_primary`, `primary_action`, `article`, `og_template`, `lint_allow`, `notes` | статус страницы, обещание и действие для kimi, бриф статьи G, OG |
| meta | `og_image_alt`, `fact_ids`, `variants`, `test_plan`, `review_by`, `notes` | предложения G и ai-media |
| section | `section_role`, `site_section_id`, `genre`, `question`, `carries`, `notes` | роль для claims_check, вопрос посетителя и опоры B1 |
| slot | `site_slot_id`, `group`, `asset_ref`, `in_image`, `selection`, `missing_ids`, `claims`, `lint_allow`, `edit_log` | повторяемые блоки, ассеты, выбор (I), записи проверок, протокол правки C |
| variant | `source`, `generated`, `review`, `checks`, `reason`, `notes`, `fact_ids` (v1.1) | откуда текст, итоги проверок варианта, причина отказа, свои факты варианта |

## Статусы

| Статус | Слот (выбранный вариант) | Страница |
|---|---|---|
| `draft` | `slot_id`, `slot_type`, `variants[{id, text, status}]`; `chosen` при 2+ вариантах — когда вариант вышел из `draft` | `page_id`, `page_type`, `sections` |
| `checked` | + `chosen`, `fact_ids`, `claim_flags`, записи `lint` и `claims` с 0 error и актуальным `text_hash`; факты находятся и публикуемы | + `meta`; все выбранные тексты ≥ checked |
| `approved` | + `review {by, at}` человека (не утилиты) или `approval` страницы; 0 `[PLACEHOLDER]` | + `approval {by, at}`; все тексты approved; title и description заполнены |
| `rejected` | вариант с `reason`; выбранным быть не может | страница с `reason`; не проверяется и не выгружается |

Для copy deck v0 требования статусов v1 — предупреждения (`upgrade` переводит v0 → v1). Переходы, проверки и точки
человека — `01-copy-deck-workflow.md` §1–§3.

## Куда уходят поля

| Потребитель | Что получает | Команда |
|---|---|---|
| пакет kimi (`../kimi-research/07-brief-handoff/templates/`) | `copy.md` (+ `## head`, строка `Voice:` из профиля F или `adaptation.voice_line`), `facts.md`, `brief-fragment.yaml` (`product.goal/name/locale/primary_action`, `site.cta.label`, `site.sections[{id, job}]`, `content.*_source`, `assets[]`; по `--meaning` — `target_user`, `description`, отвеченные `questions`) | `export-kimi [--merge-into brief.yaml] [--strict]` |
| план ассетов ai-media | `slots[{id, alt, caption, text: {mode: in_image, strings[…]}}]`, `og {alt, template_text}` | `export-assets` |
| claims_check (B2, H) | плоская копия v0 (мета и OG — `__head`, обещание — `__promise`; с `--all-variants` — копии страницы на альтернативы) | `claims`, `check` |
| copy_lint (C) | `lint_text` на каждый текст + Markdown-проекция страницы; `meta.fact_ids` учитываются (прямой `copy_lint.py` на deck — нет) | `lint`, `check` |
| слепой выбор (I, живая фаза) | лист вариантов A, B, C без моделей (слоты, обещание, мета) + ключ; варианты с error в `checks` сняты | `export-variants` |
| creative, site | стабильные пути `copy:<page>/<section>/<slot>`, `group`, `slot_type`; поля `site_*` — после S0 и S1 | — |

## Команды

```bash
T=../../scripts/text/copydeck.py
python3 $T check DECK --update OUT.yaml --promote          # claims → lint → validate; записи и draft → checked
python3 $T check DECK --all-variants                      # варианты «как выбранные» — отчётом
python3 $T export-variants OUT.yaml -o sheet.md --key key.yaml --seed N
python3 $T approve OUT.yaml --page ID --by "заказчик" -o APPROVED.yaml
python3 $T validate APPROVED.yaml --final
python3 $T export-kimi APPROVED.yaml --page ID --strict --out pkg/ --merge-into brief.yaml --meaning meaning.yaml
python3 $T --selftest                                      # 111 проверок (112 с jsonschema: venv-J)
python3 $T before-after --check                           # пустой why в before-after.tsv — из rule_ref (--write — заполнить)
python3 ../../scripts/text/run_checks.py     # пять проверок всех примеров
```

## Что проверено

- **Фаза 1 (J, J2):** J/01 «Отвес» (deck B1 v0 → v1 → checked → approved → пакет); J/02 «Кварц» (импорт `copy.md` kimi:
  3 из 3 эталонных провалов пойманы до выгрузки); J/03 — 31 из 31 отрицательного случая; J/04 — оба пакета kimi проходят
  `build_package.py check`; J/05 — линтер через `lint_text` = линтер C на copy deck; J/06 — сухой прогон пар (398).
- **Фаза 2 (J3):** J/07 — правки `copydeck.py` по находкам E3 и I3: `check` теряет `COPY-D-FALLBACK` (0 → 2 находки),
  `--all-variants` сверял отклонённые варианты (4 error → 1 → 0 с `variant.fact_ids`), лист выбора без мета (3 → 4 слота);
  J/08 — 8 примеров, 0 error в пяти проверках, страница кейса — до `build_package.py check` (0 error), вебинар —
  `--all-variants` и лист выбора, черновик лидогенерации — отказ `approve` на заглушках; две правки по ходу (пути копии deck
  в другой папке, строка голоса на языке deck); `before-after.tsv` — 540 пар, выборка 40 после курации — 39 пар + 1 частичная.

## Границы

Процедура всего сайта — site; движение текста и подача — creative (поля v0 сохраняются); пакет исполнителя — kimi
(предложения — в отчёте J); цепочка генерации и промты — I; правила текста слотов — E (`copy-slots.yaml` читает `validate`);
мета и GEO — G; право — H (`claims-rules.yaml` читает `claims_check.py`); голос — F (`voice.yaml` читает `validate`, строка
`Voice:` — `export-kimi`).
