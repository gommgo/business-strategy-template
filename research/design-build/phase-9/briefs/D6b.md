# ДФ9, зона D6b — приёмка ассетов (пара 1)

Прочитай первыми: общий бриф кода `research/design-build/phase-8/briefs/COMMON.md`, поправки ДФ9
`research/design-build/phase-9/briefs/COMMON-DF9.md` (они старше общего брифа) и цепочку `phase-9/CHAIN.md` целиком.
План — `phase-9/DF9-PLAN.md`: §2 «D6b» (твоя зона — делай по нему), §4, §5. Находки — строки `phase-9/DF9-ZONES.tsv` с
`D6b`: OE3-05, OE3-06, OE3-16, OE3-21 и часть OE3-17 (мёртвые ветки) — записи в `phase-9/prep/OE-3.md`, раздел 2.
Пути ниже — от `.claude/skills/design-deep-dive/`.

Рядом работает агент зоны D1 (вход холста, `scripts/project/`) — у него свои файлы.

## Файлы зоны
- `scripts/ai-media/asset_audit.py` (3 262 строки — читай по функциям и подкомандам), `scripts/ai-media/tests/
  test_asset_audit.py`, `scripts/ai-media/check_icons.py`, `scripts/ai-media/palette.py`.
- Не твои: списки смоука, README ai-media, указатель `scripts/README.md`. Строку `palette.py` в
  `scripts/tests/smoke/ai-media.tsv` (`import-only` → `help`) и README ai-media правит зона D6a в паре 4 — что нужно,
  опиши в «Для текстов». Файлов зона не снимает.
Маски — строка «Маски файлов» раздела D6b плана.

## Что сделать
1. Правила шапки и штриха Lucide (24×24, `stroke` 2, `round`) — только у набора Lucide: ключ набора у `audit` (по
   умолчанию Lucide) и у `check_icons.py`; у другого набора эти проверки — `warn`, находка остаётся с правилом и
   советом. Эталон и штрих параметром — Ф10, не делай.
2. `QA-PROV-VISIBLE-MARK` — `warn` с листом углов (кадр для глаза), а не `needs_human`.
3. Нет моделей OCR или бинарника — одна строка «поставьте `install.sh --groups ocr --models`» (или `--bin …`) вместо
   хвоста трассировки.
4. `palette.py` — командная строка: картинки → палитра JSON (`--k`, `--json`), `--help`; модульный вызов не меняется
   (кто его зовёт — найди поиском до правки).
5. Мёртвые ветки `asset_audit.py`: путь `EXP / "L"` и модуль `ab_analyze` (файла нет) — снять; до снятия — поиск по
   `.claude/`.
6. Справка своих файлов — о текущем поведении, forward-only.

## Ожидаемое
- `asset_audit.py selftest` и `scripts/ai-media/tests/test_asset_audit.py` — зелёные: прежние 76 проверок и новые —
  Heroicons «home» при наборе не Lucide — `warn`, не fail; Lucide — как было.
- `audit --slot hero --ocr off` на кадрах калибровочного набора `assets/calibration/` 17-f04 и 19-e08 — без
  `needs_human` от метки в углу. Набор только читается (решение заказчика Р109): в его папку ничего не пиши, выходы —
  `$DDD_HOME/out/…` или `--out` вне репозитория.
- `palette.py <картинка> --json` — палитра JSON; `palette.py --help` — справка.
- `python3 scripts/tests/smoke.py --only scripts/ai-media` — 0 FAIL (XFAIL — прежние два, с причиной); `--validate`,
  `--uncovered` — чисто.

## Отчёт
`research/design-build/phase-9/reports/D6b.md` — форма общего брифа с поправками ДФ9, плюс разделы:
- «Для текстов» — указатель `scripts/README.md` (строки `asset_audit`, `check_icons`, `palette`), README ai-media (правит
  D6a), `phases.md` (`assets`, `passport-icons`, `design-system` — палитра ассетов командой `palette.py`), строка смоука
  `palette.py` (для D6a); что было и что стало по смыслу;
- «Для ключа» — «не меняется», если так.
