# J/08 — примеры copy deck RU и EN: сборка, все проверки, путь до пакета kimi, варианты и ворота

Агент J3 (волна 3, фаза 2 J), 2026-09-24. Бесплатно: модели не вызывались, Kimi не запускался (`build_package.py` — только
`build` и `check` в копии шаблонов). Тексты — `ai-self` (E3 для трёх основ, J3 для остального); факты — вымышленные наборы
B2, ДЕМО E и ДЕМО J3.

## Цель

Собрать примеры страниц `10-templates-recipes/examples/` (RU 6, EN 2), которые проходят все проверки базы с 0 error, и
проверить на них процесс `01-copy-deck-workflow.md`: статусы, утверждение, выгрузку в пакет kimi, варианты и слепой выбор.

## Файлы

| Файл | Что делает |
|---|---|
| `make_ru_from_e3.py` | три страницы E3 → `examples/ru-{otves-lead,okoshko-saas,kvarts-preorder}.yaml`: upgrade v0 → v1, пути от `examples/`, профиль голоса F, `authors` |
| `run_checks.py [файлы] [--md table.md]` | `claims_check.py --legal-category` → `copy_lint.py` → `copydeck.py check` → `validate` (+ jsonschema из venv-J); JSON — `out/<пример>.{claims,lint,check,validate,validate-jsonschema}.json`, сводка — `out/summary.json`, таблица — `out/table.md` |
| `run_case_package.sh` | `ru-otves-case`: `check --update --promote` → `approve` → `validate --final` → `export-kimi --strict` → `build_package.py build` и `check`; контроль отказов; выход — `out/case-path/` |
| `run_variants_and_gates.sh` | вебинар: `check --all-variants --update`, `export-variants`; «Отвес» лидогенерация: `--promote` и отказ `approve`; EN: `export-kimi` черновиков; выход — `out/gates/` |
| `stats.py` | секции, слоты, слоты с фактами, слова, ядро первого экрана, заглушки, альтернативы |
| `templates/` | копия `../kimi-research/07-brief-handoff/templates/` (md5 `build_package.py` 80510e28…, как в J/04) |

## Команды и версии

Из корня базы: `python3 ../../scripts/text/run_checks.py --md 99-raw/experiments/J/08-examples/out/table.md`
(≈ 32 с), `bash …/run_case_package.sh` (≈ 5 с), `bash …/run_variants_and_gates.sh` (≈ 15 с). `copydeck.py` 1.1 (1.0 +
правки J3; selftest 111 OK, venv-J 112), `claims_check.py` 1.0 (право H 2.0, 66 правил), `copy_lint.py` 0.9.3, Python 3.13, jsonschema
4.26.0 (venv-J), `--today 2026-09-24`.

## Результат

| Пример | claims | copy_lint | check | validate | + jsonschema |
|---|---|---|---|---|---|
| `ru-otves-lead` | 0 / 7 / 0 | 0 / 5 / 40 | 0 / 8 / 47 | 0 / 0 / 5 | 0 / 0 / 5 |
| `ru-okoshko-saas` | 0 / 6 / 0 | 0 / 1 / 40 | 0 / 8 / 51 | 0 / 1 / 7 | 0 / 1 / 7 |
| `ru-kvarts-preorder` | 0 / 4 / 0 | 0 / 5 / 37 | 0 / 9 / 45 | 0 / 0 / 7 | 0 / 0 / 7 |
| `ru-okoshko-webinar` | 0 / 7 / 0 | 0 / 3 / 19 | 0 / 8 / 18 | 0 / 0 / 3 | 0 / 0 / 3 |
| `ru-otves-case` | 0 / 10 / 0 | 0 / 2 / 18 | 0 / 10 / 22 | 0 / 0 / 3 | 0 / 0 / 3 |
| `ru-otves-article-faq` | 0 / 18 / 2 | 0 / 2 / 15 | 0 / 19 / 18 | 0 / 0 / 0 | 0 / 0 / 0 |
| `en-otves-case` | 0 / 5 / 0 | 0 / 0 / 0 | 0 / 5 / 5 | 0 / 0 / 4 | 0 / 0 / 4 |
| `en-okoshko-saas` | 0 / 0 / 0 | 0 / 1 / 4 | 0 / 3 / 10 | 0 / 1 / 5 | 0 / 1 / 5 |

(error / warning / info.) Путь `ru-otves-case`: 16 текстов checked → approved → `validate --final` 0 → `export-kimi --strict`
exit 0 (5 секций, 16 строк + head 4, 10 фактов, 11 строк Never claim) → `build` 0 → `check` 0 error, 2 warning (нет `.git`,
TASK.md 4 946 знаков). Вебинар: `--all-variants` — 0 error, 4 альтернативы, `variant.checks` у 33 вариантов, лист выбора — 4
слота. «Отвес» лидогенерация: 34 текста checked, `approve` — отказ (2 заглушки). EN-выгрузки — строка `Voice:` английская.

Правки ошибок по ходу сборки (первая версия ai-self → итог) — пары в `02` §7 и `03` §4, строки `before-after.tsv`
(источник `J3-examples`). Две правки утилиты, найденные на примерах: пути копии deck в другой папке (`rebase_refs`) и строка
голоса на языке deck (`adaptation.voice_line`) — `copydeck.py --selftest`.

## Выводы

1. Все шесть русских и две английские страницы проходят пять проверок с 0 error; остаток warning — формат `use` B2
   (56 × `COPY-F-USE`), заглушки пробелов, типичность отзыва и две длины E.
2. Путь «черновик → checked → approved → пакет kimi → `build_package.py check`» работает на одной странице целиком;
   ворота публикации держат страницы с заглушками реквизитов (отказ `approve`).
3. На английском главные ловушки — формат числа («9,800») и объект счёта словами факта; свой `facts.yaml` с теми же id
   обязателен.
