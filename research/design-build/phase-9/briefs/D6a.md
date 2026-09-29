# ДФ9, зона D6a — генерация (пара 4)

Прочитай первыми: общий бриф кода `research/design-build/phase-8/briefs/COMMON.md`, поправки ДФ9
`research/design-build/phase-9/briefs/COMMON-DF9.md` (они старше общего брифа) и цепочку `phase-9/CHAIN.md` целиком.
План — `phase-9/DF9-PLAN.md`: §2 «D6a» (твоя зона — делай по нему), §4, §5. Находки — строки `phase-9/DF9-ZONES.tsv` с
`D6a`: OE3-01, OE3-02, OE3-04 (README ai-media), OE3-10, OE3-15, OE3-17, OE3-23, OV-4, OV-7 (часть) — записи в
`phase-9/prep/OE-3.md`, раздел 2; OV-4, OV-7 — `phase-9/prep/OVERENG.md` §2, п. 4 и 7. Что зона D6b (приёмка ассетов,
принята) оставила тебе — её отчёт `phase-9/reports/D6b.md`, разделы «Для текстов» п. 2 и 6 и §4. Пути ниже — от
`.claude/skills/design-deep-dive/`.

Рядом работает агент зоны D7 (`scripts/blender/`, `scripts/install.sh`, `scripts/maint/`, строки `kb/common/judge.md` и
`kb/blender/README.md`) — у него свои файлы.

## Файлы зоны
- `scripts/ai-media/routing_check.py` (426 строк), `prompt_compile.py` (2 113 — читай по подкомандам),
  `tests/test_prompt_compile*.py`, `stand_run.py` (1 049), `scripts/ai-media/README.md` (351);
- снятие (`git rm -q`): `scripts/ai-media/vm_sheet.py`, `validate_recipes.py`;
- строки `kb/`: `kb/ai-media/README.md` (стр. 38–42), `kb/ai-media/14-recipes/00-cheatsheet.md` («Перед работой»,
  стр. 9–17, и чек-лист, стр. 106–113), `14-recipes/01-hero-recipes.md` (стр. 96–108), `14-recipes/04-capability-map.md`
  (стр. 367);
- список смоука `scripts/tests/smoke/ai-media.tsv`.
Маски — строка «Маски файлов» раздела D6a плана. Фикстуры зона не задевает.

## Что сделать — план §2 D6a
1. **`routing_check`:** снимки каталогов по умолчанию — последние в `$DDD_HOME/cache/ai-media`; проверка ссылок на опыты
   (`phase5_test`) снята; справка — о текущем. Код 0 — или только настоящие расхождения моделей и цен.
2. **`prompt_compile`:** снимок каталога читается только командами, которым он нужен (`--help`, `ratios`, `validate` без
   `--model` отвечают без снимка); `jobs` по умолчанию — одно задание (диалект семейства, 1 повтор, без сидов, тега и
   агента опыта), A/B — явными ключами.
3. **`stand_run collect`:** путь паспорта — от корня выходов (`relative_to`), `--root` без папки агента E; страница
   картинок `page` — из выхода `polza.py`.
4. **Строки `kb/`** (они останавливают пилот): «Перед работой» и чек-лист шпаргалки 14/00, README ai-media (стр. 38–42),
   карта 14/04 (стр. 367) — «перед платным вызовом — `estimate` без ошибок и «да» заказчика; снимки, `routing_check` и
   сверка баланса — сигнал»; рецепт hero 14/01 (стр. 96–108) — вызовы `$DDD_HOME/venv/bin/python scripts/ai-media/…`,
   `jobs … --out $DDD_HOME/out/…`, без `99-raw/tools`, `venv-D2` и `99-raw/phase5/jobs`. Правь только эти строки, по
   месту; остальная проза `kb/` — Ф10.
5. **README ai-media** — о текущем: утилита → вызов → выход, за ключами — `--help`; журнальные разделы (агенты и волны,
   «Будут добавлены», правила фаз, `99-raw/tools`, `venv-D2`, `venv-G`, `ab_analyze.py`, `fetch.py`, `yt_dl.py`) — сняты;
   правки D6b (отчёт D6b «Для текстов» п. 2): 90 проверок приёмки (92 с `--ocr`), `QA-PROV-VISIBLE-MARK` — предупреждение
   с листом углов, строки окружения и поле `env`, ключ `audit --icon-set`, командная строка `palette.py`.
6. **Смоук `ai-media.tsv`:** `palette.py` — `utility · help` (было `module · import-only`); у `check_icons.py` справка
   работает без группы svg — xfail «help: нужны cairosvg …» снять, вид — `utility` (отчёт D6b п. 6); строки снятых
   `vm_sheet.py`, `validate_recipes.py` — снять.
7. **Снятие** `vm_sheet.py`, `validate_recipes.py`: до снятия — поиск по `.claude/` и `docs/` (ожидается: код, этапы,
   аудит, фикстуры не зовут; указатель — D9; `kb` — список Ф10). Утилиты обслуживания матрицы маршрутов и сценариев из
   `note` OE3-17 остаются до Ф10 — не трогай.
8. Справка тронутых файлов — о текущем поведении, forward-only. Платных вызовов и `--live` нет.

## Ожидаемое (план §2 D6a «Проверка»)
- `routing_check.py` без аргументов — на последних снимках в `$DDD_HOME` без ошибок `phase5_test`; код 0 или только
  настоящие расхождения моделей и цен — списком в отчёт (до правки — «снимок не найден»; со снимками 29.09 — 137 ошибок
  у 29 из 33 маршрутов, настоящих — 0; сними сам).
- `prompt_compile.py --help` при пустом `DDD_HOME` — справка; `jobs <спецификация> --models <модель>` без ключей — 1
  задание; `polza.py estimate` — цена одного задания (до правки — 6 заданий: 24 ₽ вместо 4 ₽); тесты
  `tests/test_prompt_compile.py` (98) и `tests/test_prompt_compile_x2.py` (15) — зелёные.
- `stand_run.py selftest` — OK; `collect --root <папка паспортов вне kb>` — без трассировки.
- `python3 scripts/tests/smoke.py --only scripts/ai-media` — 0 FAIL (XFAIL — прежние два, с причиной); `--validate`,
  `--uncovered` — чисто; `scripts/maint/sync_check.py all` — 0.

## Отчёт
`research/design-build/phase-9/reports/D6a.md` — форма общего брифа с поправками ДФ9, плюс разделы:
- «Для текстов» — `kb/INDEX.md` (стр. 223–224) и `phases.md` (`asset-plan`, `assets`) — D8; указатель
  `scripts/README.md` (строки ai-media, снятые утилиты, «Подробный README домена») — D9; что было и что стало по смыслу;
- «Для ключа» — «не меняется», если так.
