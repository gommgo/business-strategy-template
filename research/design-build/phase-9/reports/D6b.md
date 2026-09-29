# D6b — приёмка ассетов: отчёт ДФ9

Пути `scripts/…`, `kb/…`, `references/…`, `assets/…` — от `.claude/skills/design-deep-dive/`. База — `7e6d57e` (файлы зоны
в `461e3a1` те же).

## 1. Файлы

| файл | новый / правка | строк (+/−) | что внутри (функции, подкоманды, ключи, разделы) |
|---|---|---|---|
| `scripts/ai-media/asset_audit.py` | правка | 3 356 (+134/−40) | справка (строка окружения, `svg-icon`, `--icon-set`); константы `ICON_SET`, `INSTALL`; сняты `EXP` и строка псевдонимов папок опытов; `mod()` без `ab_analyze`; `env_hint`, `last_line`; `Report.env`, `Report.no_env`, поле `env` в `to_dict`; `OCR_INSTALL`, `ocr_missing`; `run_ocr` (проверка моделей до запуска, одна строка при падении обработчика); `cmd_ocr_worker` (нет пакета или модели не загрузились — строка с командой); `apply_text` (ошибка окружения → `no_env`); `provenance` (без ветки `EXP / "L"`, поле `missing`); `check_ssimulacra` (нет мастера, `ssimulacra2` или декодера — строка вместо тихого пропуска); `audit_svg` → `check_icons(R, path, icon_set)`; `is_lucide`, `check_icons` (ключ `--set`, уровень из `levels`, совет у шапки другого набора, строка окружения группы svg); `audit_paths` (нет `ffmpeg`/`ffprobe` или бинарника `$DDD_HOME/bin` — строка; `QA-PROV-VISIBLE-MARK` — `warn` с листом углов и пунктом «человеку»; строки провенанса без `c2patool`/`exiftool`; `env` сводки); `audit_md` (строки «Окружение неполное»); подкоманда `audit`: ключ `--icon-set НАБОР` |
| `scripts/ai-media/check_icons.py` | правка | 273 (+74/−15) | справка о текущем поведении (без «G ·», `99-raw/tools/venv-G`, `ui-research`); импорт пакетов группы svg под `try` → `DEPS_ERROR`; `LUCIDE`, `HARD_FLAGS`, `LUCIDE_FLAGS`, `is_lucide`, `flag_levels`, `deps_hint`; `header_check` — атрибут `width` не находит хвост `stroke-width`; `check_dir(d, ref, icon_set)` — поля `set`, `levels`; `flags_md`; командная строка: описание и справка ключей, `--set НАБОР` (умолчание `lucide`), нет пакетов — одна строка и код 2 |
| `scripts/ai-media/palette.py` | правка | 134 (+68/−4) | справка о текущем поведении (без «F/05» и пути в `99-raw`); `palette()` — цветов меньше k: палитра короче вместо `ValueError`; `oklch`, `measure`, `to_text`, `main` — командная строка `IMG… [--k 6] [--json]`; модульные функции и их вызовы те же |
| `scripts/ai-media/tests/test_asset_audit.py` | правка | 803 (+152/−4) | справка; `t_provenance` — метка в углу `warn`, лист углов, пункт «человеку»; `HEROICONS_HOME`, `svg_ready`, `t_icon_set` (5 проверок), `t_env` (5), `t_palette_cli` (3); `run()` — новые тесты |
| `research/design-build/phase-9/reports/D6b.md` | новый | — | этот отчёт |

Файлов зона не снимает (§2 плана).

## 2. Находки

| id | что сделано и где (файл: функция / подкоманда / ключ / раздел) | как проверено |
|---|---|---|
| OE3-05 | `check_icons.py`: ключ `--set НАБОР` (умолчание `lucide`; Lucide — имя с «lucide» в начале, без учёта регистра), `flag_levels` → поле `levels` записи: «цвет» — `fail` у любого набора, «шапка» (шапка и штрих Lucide: 24×24, `stroke-width` 2, `round`) — `fail` только у набора Lucide, у другого — `warn`, остальные флаги — `warn`; таблица помечает брак и пишет совет у шапки другого набора. `asset_audit.py`: `audit --icon-set НАБОР` (умолчание `lucide`) → `check_icons(R, path, icon_set)` передаёт `--set`, уровень берёт из `levels`; находка `QA-SVG-HEADER` у другого набора — `warn` с правилом Lucide и советом «сверить шапку и штрих со спецификацией набора, иконки под Lucide не подгонять». Эталон и штрих параметром — не делал (Ф10) | тесты `t_icon_set`: Heroicons outline «home» при наборе по умолчанию — `QA-SVG-HEADER` `fail`, вердикт `fail` (как было); при `--icon-set heroicons` — вердикт `warn`, `levels.шапка` = `warn`, в сообщении правило и совет; жёсткий цвет при heroicons — `QA-SVG-COLOR` `fail`; Lucide `search.svg` — без флага шапки. Прогон `check_icons.py` на трёх иконках прогона OE-3 (Heroicons home, Material filled home, Lucide house): `--set lucide` — шапка `fail` у Heroicons и Material, `--set heroicons` — `warn`, Lucide — «ок» |
| OE3-06 | `asset_audit.py` `audit_paths`: `QA-PROV-VISIBLE-MARK` — `warn` (было `needs_human`), в сообщении и `evidence` — лист углов `<файл>_corners.jpg`; пункт «человеку»: «Лист углов …: есть ли видимая метка вендора?» (коды `QA-PROV-VISIBLE-MARK`). `QA-COLOR-WARM` без `--dna` — не трогал (замер Ф9) | `t_provenance`: надпись в углу → `warn` с листом углов, пункт «человеку»; чистый кадр — без находки. Калибровочный набор (§5): 17-f04 и 19-e08 — `warn`, `needs_human` от метки в углу нет |
| OE3-16 | `palette.py`: `main` — `palette.py IMG… [--k 6] [--json]`: на картинку — палитра (hex, доля, OKLCH), нейтрали (доля, средние a, b OKLab у пикселей с хромой < 0,03, медиана хромы), у двух картинок и больше — общая палитра `all`; без `--json` — таблица; картинка не читается — одна строка и код 2; `--help`. Модульный вызов не менялся — вызывающие найдены до правки: `series_metrics.py` (`load`, `to_oklab`, `palette`, `adherence`), `vlm_to_dna.py` (`load`, `palette`, `to_oklab`, `hexs`; `parametric_grade`, `write_cube`) | `t_palette_cli`: два цвета `--k 2 --json` — доли 0,7 / 0,3, hex ±1, OKLCH; `--k 6` на двухцветной картинке — палитра из 2 без падения, `all` у двух картинок; `--help` — код 0, нет файла — код 2 и одна строка. Прогон на 19-e08 и паре 17-f04 + 19-e08 (§5). Смоук: `vlm_to_dna.py selftest`, `series_metrics.py` — PASS |
| OE3-17 (часть D6b) | `asset_audit.py`: сняты `EXP = ROOT / "99-raw" / "experiments"` и ветка `provenance()` к `EXP / "L"` (`provenance_check.py` — рядом, в `scripts/ai-media`), строка `"ab_analyze"` в `mod()` (файла нет, вызовов нет); той же уборкой — строка псевдонимов папок опытов `A04 = F02 = F04 = F05 = F06 = G_EXP = TOOLS` (все равны `TOOLS`; `mod()` и `check_icons()` зовут от `TOOLS`) | поиск до снятия по `.claude/` и `docs/`: `EXP`, `G_EXP`, `A04`, `F02`–`F06` — только `asset_audit.py`; `ab_analyze` в коде — только строка `mod()`, в текстах — README ai-media стр. 166 (D6a) и проза `kb/` (Ф10); после — `grep` по файлам зоны: 0; тесты 90/90, смоук 0 FAIL |
| OE3-21 | `asset_audit.py`: `ocr_missing` — модели набора проверяются до запуска OCR → «нет моделей OCR (…) — поставьте `scripts/install.sh --groups ocr --models`» (обработчик не стартует); `cmd_ocr_worker` — нет пакета → «нет пакета rapidocr (группа ocr) — поставьте …», модели не загрузились → одна строка с той же командой; падение обработчика — последняя строка вывода, не 400 знаков трассировки; `check_icons` без группы svg → «нет пакета cairosvg (группа svg …) — поставьте `scripts/install.sh --groups svg`»; провенанс без `c2patool`/`exiftool` → «… не найден (провенанс: метки … не прочитаны) — поставьте `scripts/install.sh --bin`» (сведения, вердикт не меняют); `--master` без `ssimulacra2` или декодера → `--bin`; видео без `ffmpeg`/`ffprobe` → `--ffmpeg`. Строка проверки, которая не запущена, — в `errors` ассета («OCR не запущен: …»; вердикт `needs_human`, как было), все строки — в поле `env` ассета и сводки и в строках «Окружение неполное» `audit.md`. Чек-лист окружения пилота — Ш0 (оркестратор) | `t_env`: нет моделей OCR — одна строка без запуска OCR; `audit --ocr on` — одна строка в `errors`, `env` сводки, строка в `audit.md`; `check_icons.py` с заглушкой cairosvg — код 2 и одна строка; `asset_audit` — «check_icons не запущен: …»; без `c2patool` — строка `--bin` в «Окружение», в `errors` её нет. Прогоны §5: пустой `DDD_HOME`, системный `python3`, видео без `ffprobe` в `PATH` |

## 3. Отступления от плана и спецификации

1. **OE3-21 шире двух случаев брифа.** Кроме моделей OCR и бинарников провенанса ту же строку «чего нет — поставьте
   `scripts/install.sh …`» получили группа svg (`check_icons`), `ssimulacra2` и декодеры AVIF, WebP, JXL у `--master` и
   `ffmpeg`/`ffprobe` видео: это все места, где утилита падала трассировкой или молчала из-за окружения. Тихий пропуск
   снят: `--master` без `ssimulacra2` или без файла мастера раньше молча не проверялся (вердикт мог выйти `pass`),
   теперь — строка в `errors` и вердикт `needs_human`. Варианты: оставить (предлагаю: запрошенная проверка не выполнилась —
   урок Ф8 о тихих пропусках) или вернуть пропуск для `--master` — решает оркестратор.
2. **Провенанс без бинарников не повышает вердикт.** `c2patool` и `exiftool` не найдены — строка только в `env` и
   «Окружение»: остальная проверка работает (углы, байтовые маркеры), а `needs_human` на каждом кадре был бы новым шумом.
   `QA-PROV-NO-MARK` в этом случае дописывает «метки прочитаны не целиком: нет …».
3. **`QA-PROV-VISIBLE-MARK` — ещё и пункт «человеку»** с листом углов: решение по метке — глазом; столбец «Человеку»
   `audit.md` у кадров с подозрением — на 1 больше.
4. **Поле `env` в asset-audit/1** (ассет и сводка) и строки «Окружение неполное» в `audit.md` — расширение формата
   совместимое: потребителей `audit.json` в коде нет (поиск по `.claude/`).
5. **`check_icons.py` `header_check`** — `\b` перед `width` находил хвост `stroke-width`: у Heroicons в `header_bad` было
   «width=1.5» вместо «width=нет». Исправлено границей `(?<![\w:-])`; флаги не меняются (шапка и так отличалась), меняется
   текст замечания. У Lucide `width` идёт раньше `stroke-width` — результат прежний.
6. **`palette()`** — при числе цветов меньше k раньше падала `ValueError` (NaN в вероятностях k-means++), теперь палитра
   короче. Для обычных картинок результат тот же: разрыв цикла срабатывает только там, где раньше было падение, порядок
   вызовов генератора случайных чисел не меняется. Интерфейс модуля тот же.
7. **Строка псевдонимов папок опытов** снята вместе с `EXP` (см. OE3-17): в брифе названы только `EXP / "L"` и
   `ab_analyze`, строка — та же раскладка лаборатории, вызывающих вне файла нет.

## 4. Для следующих зон

- **Ключ набора иконок:** `asset_audit.py audit … --icon-set НАБОР` (умолчание `lucide`; значение — `conventions.icons.set`
  карты решений `…/design/system.yaml`; набор Lucide — любое имя, начинающееся с «lucide», без учёта регистра).
  `check_icons.py ПАПКА [--ref ПАПКА] [--set НАБОР] [--json F] [--md F] [--title T]`; запись JSON иконки — прежние поля и
  `set`, `levels` (`{первое слово флага: fail | warn}`); без пакетов группы svg — одна строка в stderr и код 2.
- **`palette.py`:** `palette.py IMG… [--k 6] [--json]` → `{k, images: [{file, palette: [{hex, share, oklch: [L, C, h]}],
  neutral: {share, a, b, chroma_median}}], all?}` (`all` — у двух картинок и больше); код 2 — картинка не читается.
- **asset-audit/1:** у ассета и в сводке — `env` (список строк «чего нет — поставьте `scripts/install.sh …`», только если
  есть); в `errors` — «<проверка> не запущен: <строка>» (`OCR`, `check_icons`, `SSIMULACRA2`, `режим <m>`).
- **D6a (пара 4):** строки смоука и README ai-media — «Для текстов» п. 2 и 6.
- **Оркестратор, Ш0:** строки окружения — готовый вход чек-листа пилота: `install.sh --check` с группами `svg`, `ocr`,
  `--bin`, `--models`, `--ffmpeg`.

## 5. Тесты и прогоны

- **До правок:** `asset_audit.py selftest` — 76/76; `audit --slot hero --ocr off` на кадрах 16-f04, 17-f04, 18-e08, 19-e08
  (`$DDD_HOME/out/ai-media/D6b/base`) — `needs_human` у 16, 17, 19 (`QA-PROV-VISIBLE-MARK`), `warn` у 18 — как в OE3-06;
  пустой `DDD_HOME` — в `errors` хвост трассировки `FileNotFoundError: …/models/ocr/eslav_PP-OCRv5_rec_mobile.onnx does not
  exists.`, провенанс — «c2patool не найден» — как в OE3-21.
- **Тесты и самопроверка:** `asset_audit.py selftest` — **90/90 OK** (76 прежних, одна прежняя проверка провенанса теперь
  ждёт находку любого уровня; новые 14: провенанс 1, набор иконок 5, окружение 5, `palette.py` 3);
  `tests/test_asset_audit.py -v` — 90/90; `tests/test_asset_audit.py --ocr` — 92/92 (живой OCR под блокировкой heavy —
  путь OCR после правки `run_ocr` рабочий); `asset_audit.py thresholds --check` — `ok`, 99 ключей.
- **Калибровочный набор** (только чтение; выход `$DDD_HOME/out/ai-media/D6b/after`, `after4`):
  `audit --slot hero --ocr off` — ожидание брифа «17-f04 и 19-e08 без `needs_human` от метки в углу» — **совпало**:
  17-f04 — `warn` (`QA-COLOR-WARM`, `QA-PROV-VISIBLE-MARK` `warn`), 19-e08 — `warn` (то же); на четырёх кадрах — `warn`
  4 из 4 (16-f04: `QA-COLOR-HDR`, метка `warn`; 18-e08: `QA-COLOR-WARM`). Листы углов — в папке выхода. `git status` по
  `assets/` — пусто, в папку набора ничего не записано.
- **`palette.py`:** `--help` — код 0; `19-e08 --json` — 6 цветов (#a99787 0,397 …), нейтрали; `17-f04 19-e08 --k 4` —
  таблицы и «все картинки»; нет файла — код 2, одна строка.
- **`check_icons.py`:** три иконки прогона OE-3 — см. OE3-05 в §2; `--help` системным `python3` без группы svg — код 0;
  запуск без cairosvg — одна строка, код 2.
- **Окружение (OE3-21):** пустой `DDD_HOME`, Python окружения — «Окружение неполное»: `c2patool не найден (провенанс:
  метки C2PA не прочитаны) — поставьте scripts/install.sh --bin`, то же `exiftool`, `нет моделей OCR
  (eslav_PP-OCRv5_rec_mobile.onnx, en_PP-OCRv5_rec_mobile.onnx) — поставьте scripts/install.sh --groups ocr --models`;
  системный `python3` с моделями — «нет пакета rapidocr (группа ocr) — …»; без группы svg — «нет пакета cairosvg (группа
  svg: …) — поставьте scripts/install.sh --groups svg»; видео без `ffprobe` в `PATH` — «режим video-loop не запущен:
  ffprobe не найден — поставьте scripts/install.sh --ffmpeg». Трассировок в `errors` нет.
- **Смоук:** `python3 scripts/tests/smoke.py --only scripts/ai-media` — PASS 54, **FAIL 0**, XFAIL 2 (`mp_client.py run
  selftest`, `polza_catalog.py run selftest` — прежние, с причиной в колонке `xfail`), XPASS 6; `--validate` — 18 списков,
  218 строк, ошибок 0; `--uncovered` — 0.
- **`sync_check.py all`:** 16 OK, 1 FAIL `fixtures` — «fixture_gen: canvas_input build не записал INPUT.md»: рядом идут
  правки зоны D1 (`scripts/project/canvas_input.py`, `contract.py` в рабочем дереве); файлы D6b в
  `scripts/maint/data/sync.yaml` и `fixtures.yaml` не названы, фикстур с собранными файлами зона не трогает.
- Машина: Blender, браузер и видеокарта не нужны; OCR — один прогон `--ocr` (память ≥ 4 ГБ свободна).

## 6. Строки смоука

- Не менялись (список `scripts/tests/smoke/ai-media.tsv` — зоны D6a). Что нужно — «Для текстов» п. 6.

## 7. Проверка

- `research/design-build/tools/refcheck.py --strict` по этому отчёту: ссылок 116, «битых» 26 — имена выходов и команд
  (`audit.md`, `audit.json`, строки указателя `ai-media/…`, пути от `kb/ai-media/` и от корня скилла, образцы `.claude/`,
  `docs/`, снятое `99-raw/tools/venv-G`), а не ссылки; следов журнала 34 — отчёт лежит в журнале сборки, там они по
  назначению (`accept.py` md из `research/` не сверяет). Других md зона не правила.
- Разбор: `ast.parse` и `compile` четырёх `.py` — ошибок нет.
- Следы журнала в коде зоны: правила `TRACE_PATTERNS` журнального `phase-8/tools/accept.py` по четырём файлам — 0;
  `grep -niE 'kimi|\bK3\b|gemini|qwen|gpt-|\bР[0-9]+\b|\bФ[0-9]+\b'` — 0; `99-raw` — только входы тестов журнала опытов
  (`t_edit`, `t_video`, `t_svg_series` — пропуск, если их нет; §8). Ключей нет, сети и трат нет.
- Прочитано глазами: `asset_audit.py` — справка, константы, `mod`, `Report`, OCR (`ocr_worker`, `run_ocr`,
  `cmd_ocr_worker`), `provenance`, `check_ssimulacra`, `audit_svg`, `check_icons`, `apply_text`, `HUMAN_DEFAULT`, `finish`,
  `contact_panel`, `audit_paths`, `audit_md`, `cmd_audit`, `build_parser`; `check_icons.py`, `palette.py` — целиком;
  тесты — `audit`, `codes`, `calm_photo`, `t_svg_series`, `t_provenance`, `t_ocr`, `run`; вызывающие: `provenance_check.py`
  (`c2pa_read`, `exif_read`, `summarize`, `scan_file`), `vlm_to_dna.measure_image`, импорт `series_metrics.py`,
  `video_loop_check.py` (вызов `ffprobe`/`ffmpeg` по имени), `smoke.py`, `install.sh` (ключи, таблицы бинарников и
  моделей), `requirements.txt` (группы), `kbpaths.py` (`python`, `models`, `find`, `which`).

## 8. Открыто и не прочитано

- **Открыто:**
  - вердикт на калибровочном наборе по-прежнему не отделяет годное от брака: 4 из 4 — `warn`, `QA-COLOR-WARM` без `--dna`
    на тёплых кадрах — замер Ф9 (OE3-06); метку в углу до `info` — Ф10 (OE3-06);
  - эталон и штрих параметром — Ф10 (бриф): шапка сверяется с Lucide 24/2; продукт на Lucide со штрихом 1,5
    (`conventions.icons.stroke: 1.5`, как в фикстуре `cabinet-ds`) получит `QA-SVG-HEADER` `fail`;
  - шапка проверяется только по корню `<svg>`: у Heroicons `round` — на контуре, замечание «stroke-linecap=нет» у другого
    набора — предупреждение; остальные пороги `check_icons` (центр, сетка, вес) откалиброваны на Lucide — `warn`, Ф10;
  - запасной путь `provenance()` через `exiftool` + `c2patool` (когда рядом нет `provenance_check.py`) достижим только при
    повреждённой установке — не снят (зона называет только `EXP / "L"`), Ф10; `VENV_K`/`VENV_G` — имена окружений
    лаборатории, оба равны `kbpaths.python()`, их проверка `.exists()` всегда истинна — Ф10;
  - тесты `t_edit`, `t_video`, `t_svg_series` берут входы из `kb/ai-media/99-raw/…`, которых в скилле нет: 3 проверки из
    90 — пропуски с пометкой, серия не проверяется вовсе — Ф10 (свои фикстуры);
  - `sync_check` `fixtures` — у зоны D1 (§5);
  - чек-лист окружения пилота — Ш0 (оркестратор).
- **Не прочитано:** `asset_audit.py` целиком (≈ 3,4 тыс. строк) — подкоманды судьи (`judge-*`, `agree`, `calibrate`),
  режимы `cutout`, `edit`, `texture`, `video` читались только в местах вызова окружения; проза `kb/` — только строки
  поиска по `check_icons`, `QA-PROV-VISIBLE-MARK`, `ab_analyze`, `palette`.

## Для текстов

Что меняется по смыслу; формулировки — текстовые зоны по SKILL-MAP §7.

1. **Указатель `scripts/README.md`** (D9):
   - строка `ai-media/asset_audit.py`: вход — добавить `[--icon-set НАБОР]` (набор иконок продукта — `conventions.icons.set`).
     Было: шапка Lucide — брак у любого набора, метка в углу — `needs_human`, нет окружения — трассировка в JSON; стало:
     шапка и штрих Lucide — брак только у набора Lucide, метка в углу — предупреждение с листом углов, нет окружения —
     строка «поставьте `scripts/install.sh …`» в `errors` и в «Окружение» `audit.md`;
   - строка `ai-media/check_icons.py`: было «module · G · проверка SVG-иконки по нормам ui-research 07/01 … · `--help`»;
     стало — утилита: «проверка линейных SVG-иконок кодом, без глаз: нормы ui 07/01 и спецификация Lucide», вход
     `ПАПКА [--ref ПАПКА] [--set НАБОР] [--json F] [--md F]`, выход — таблица в stdout, `--json` (замеры, `flags`,
     `levels`), `--md`; без группы svg — строка с командой установки, код 2;
   - строка `ai-media/palette.py`: было «module · F/05 palette.py — … · модуль / без `--help`»; стало — утилита и модуль:
     `IMG… [--k 6] [--json]` → палитра JSON (hex, доля, OKLCH, нейтрали; `all` у нескольких картинок), модульный вызов
     тот же (`series_metrics`, `vlm_to_dna`).
2. **README ai-media `scripts/ai-media/README.md`** (D6a, пара 4): раздел «Приёмка ассетов — `asset_audit.py`» — тесты
   76 → 90 (92 с `--ocr`); `QA-PROV-VISIBLE-MARK` — предупреждение с листом углов и пунктом «человеку» (было —
   `needs_human`); строки окружения и поле `env`; в таблице команд у `audit` — `--icon-set`; строка о командной строке
   `palette.py`; строка `ab_analyze.py` в таблице утилит (стр. 166) — файла нет, код его больше не называет.
3. **`references/phases.md`** (D8):
   - `assets` (стр. 669, «Проверка»): `check_icons.py --set <набор>` и `asset_audit.py --icon-set <набор>` — набор из
     `conventions.icons.set`; шапка и штрих Lucide — брак только у набора Lucide, у другого — предупреждение, набор под
     Lucide не подгонять; метка в углу — предупреждение с листом углов, решает глаз; нет моделей или бинарников —
     строка с командой установки (окружение — до этапа, `install.sh --check`);
   - `passport-icons` (стр. 743) и `ds-components` (стр. 761): `check_icons.py` — с набором продукта (`--set`),
     `asset_audit.py` — `--icon-set`;
   - `design-system` (стр. 651 и 782): «палитра ассетов замерена кодом (`palette.py`)» — теперь команда
     `palette.py <ключевые ассеты> --json`: hex, доля, OKLCH на цвет, нейтрали (b > 0 — тёплые, b < 0 — холодные), `all` —
     общая палитра; однострочник с `sys.path` и пакет судьи для замера не нужны.
4. **`.claude/skills/design-audit/references/rules.md`** стр. 152 (D9): «иконки — `check_icons.py`» — с набором продукта
   (`--set` из `conventions.icons.set`).
5. **Проза `kb/`** (список Ф10; строк `kb/` зона не называет): `kb/ai-media/11-evaluation-qa/01-metrics-and-asset-audit.md`
   стр. 43 и 275, 371 (шапка — `fail` у любого набора), стр. 61–64 и 375 (`QA-PROV-VISIBLE-MARK` — `needs_human`);
   `kb/ai-media/14-recipes/03-vector-text-og-recipes.md` стр. 100 (шапка — `fail`); `kb/ai-media/14-recipes/00-cheatsheet.md`
   стр. 61 («флаги `check_icons` — 0»: у другого набора шапка — предупреждение); `ab_analyze` — `05-prompting/06-ab-protocol.md`,
   `15-tools-atlas/02-tools-libraries-cli.md`, `11-evaluation-qa/01-metrics-and-asset-audit.md`,
   `11-evaluation-qa/02-vlm-critic-and-rubrics.md`, `05-prompting/README.md`, `PLAN.md` базы.
6. **Смоук `scripts/tests/smoke/ai-media.tsv`** (D6a, пара 4): `scripts/ai-media/palette.py` — `module · import-only` →
   `utility · help`; `scripts/ai-media/check_icons.py` — справка работает без группы svg: xfail «help: нужны cairosvg …»
   больше не нужен, вид — `utility`.

## Для ключа

Не меняется: сценарии 1–4B и 14 посевов `asset_audit.py`, `check_icons.py`, `palette.py` не вызывают (поиск по
`phase-8/check/KEY.md`, `KEY-seeded.md`, `phase-8/tools/` — 0; `design_audit.py` приёмку ассетов не запускает — R-STRUCT-005
и R-COV-009 чтением).

## 9. Запись для CHAIN

```
## <NN>. D6b — приёмка ассетов (29.09, ≈ <мин> мин, в уведомлении — <тыс.> токенов)
- Сделано: правлены scripts/ai-media/asset_audit.py (+134/−40), check_icons.py (+74/−15), palette.py (+68/−4),
  tests/test_asset_audit.py (+152/−4); снятых файлов нет. OE3-05 — ключ набора `audit --icon-set` и `check_icons.py --set`
  (умолчание lucide), поле `levels`: шапка и штрих Lucide — fail только у Lucide, у другого набора — warn с советом; цвет —
  fail всегда. OE3-06 — QA-PROV-VISIBLE-MARK warn с листом углов и пунктом «человеку». OE3-16 — `palette.py IMG… [--k]
  [--json]`, модуль тот же. OE3-17 (часть) — сняты EXP / "L", ab_analyze, псевдонимы папок опытов. OE3-21 — нет модели,
  пакета или программы окружения: одна строка «поставьте `scripts/install.sh …`» (ocr, svg, --bin, --ffmpeg) в errors и
  в «Окружение» audit.md, поле env.
- Тесты: selftest 90/90 (76 + 14), с --ocr 92/92; калибровочный набор 17-f04, 19-e08 — warn без needs_human от метки;
  смоук --only scripts/ai-media — PASS 54, FAIL 0, XFAIL 2 (прежние), XPASS 6; --validate, --uncovered — чисто;
  sync_check all — FAIL fixtures у D1 (canvas_input в работе), не зоны D6b.
- Отступления: строки окружения шире брифа (svg, ssimulacra2 и декодеры, ffmpeg); `--master` без ssimulacra2 или мастера —
  строка в errors вместо тихого пропуска; header_check — width не хвост stroke-width; palette() — цветов меньше k без
  падения; env — новое поле asset-audit/1.
- Стыки: `--icon-set НАБОР` = conventions.icons.set; check_icons JSON + set, levels; palette JSON {k, images, all};
  D6a — смоук palette (import-only → help), check_icons help без xfail, README ai-media; D8, D9 — «Для текстов».
- Открыто: эталон и штрих параметром, метка в углу до info — Ф10; QA-COLOR-WARM без --dna и различение годного и брака —
  замер Ф9; входы тестов из 99-raw (3 пропуска) — Ф10; чек-лист окружения — Ш0.
- Не прочитано: подкоманды судьи и режимы cutout, edit, texture, video asset_audit.py — вне мест правки; проза kb.
```
