# Утилиты ai-media

Утилиты картинок и видео сайта: спецификация ассета и промт в диалекте модели, задания и клиенты генерации (polza,
RouterAI, Gen-API) с сухим прогоном и оценкой цены, приёмка ассетов кодом и пакет судьи, провенанс и метки ИИ, выбор
заказчиком из вариантов на странице слепых пар, приёмка страницы с ассетами. Нормы и числа живут в базе `kb/ai-media/`
(маршруты — `kb/ai-media/13-routing-matrix/routing.yaml`, пороги приёмки —
`kb/ai-media/11-evaluation-qa/thresholds.yaml`, диалекты — `kb/ai-media/05-prompting/dialects.yaml`): утилиты их
читают, а не держат в коде. База, соседние утилиты, выходы, кэши, блокировки и бинарники находятся через
`../lib/kbpaths.py`; запуск — Python окружения скилла (`$DDD_HOME/venv/bin/python`, `../install.sh`). Выходы —
`$DDD_HOME/out/ai-media/…` или ключ `--out`; снимки каталогов моделей —
`$DDD_HOME/cache/ai-media/{polza,routerai,genapi}/` (`install.sh --catalogs`, бесплатные GET). Код-репо запускает
утилиты соседним чекаутом `../strategy/…/scripts/ai-media/…`. Ключи и форматы — `<утилита> --help` и шапка файла.

## Генерация по плану ассетов

Генерация — только по утверждённому заказчиком плану ассетов. Цепочка одного ассета:

1. **Спецификация** — `vlm_to_dna.py to-spec` из паспорта визуала или руками по схеме
   `kb/ai-media/05-prompting/asset-spec.schema.json`; модель и параметры — строка `routing.yaml` по коду задачи.
2. **Задание** — `prompt_compile.py jobs SPEC --models МОДЕЛЬ --out $DDD_HOME/out/ai-media/<ассет>.jsonl`: одно задание
   на спецификацию и модель (диалект семейства, один вариант, без seed); варианты плана — `--repeats N`, сравнение форм
   промта — `--dialects`, `--seeds` явно.
3. **Цена** — `polza.py estimate ФАЙЛ` (`mp_client.py estimate` — у RouterAI и Gen-API): без ошибок, сумма — против
   строки плана. Оценка называет снимок каталога, по которому считана, и его возраст: цена по давнему снимку — повод
   обновить его до «да». Перед платным вызовом — `estimate` без ошибок и «да» заказчика; `--live` — вместе с владельцем
   денег.
4. **Прогон** — `polza.py batch ФАЙЛ --live` → файлы и паспорта `<файл>.passport.json` в
   `$DDD_HOME/out/ai-media/_polza/<агент>/<дата>/`, трата — в журнале `$DDD_HOME/out/ai-media/_ledger.jsonl`. Обрыв
   сети — сначала `polza.py history ID`, потом повтор.
5. **Приёмка** — `asset_audit.py audit ПАПКА --strict` (+ утилита типа ассета), затем выбор заказчиком:
   `stand_run.py page ПАПКА --out СТРАНИЦА` → голоса → `stand_run.py tally`.

Снимки каталогов, `routing_check.py` и сверка баланса счёта с журналом — сигнал, не стоп: расхождение маршрута с
каталогом (модель выбыла, сменился id или цена) — повод сверить строку плана и `estimate`, а не запрет генерации.

| утилита | что делает | вызов | выход |
|---|---|---|---|
| `prompt_compile.py` | спецификация → промт в диалекте семейства и параметры задания; проверка входа и цена той же библиотекой, что у `polza.py`; до вызова — размер картинок входа против `min_input_px` модели и предупреждение о `resolution`, которого у модели нет | `validate SPEC [--model ID]`; `compile SPEC --model ID [--dialect D] [--json]`; `jobs SPEC… --models ID[,…] [--out F] [--repeats N] [--dialects D,…] [--seeds S,…] [--channel routerai\|genapi]`; `chain`, `ratios`, `matrix` | stdout или `--out`: JSONL для `polza.py`, список `<имя>.routerai.json` / `<имя>.genapi.json`; паспорт компиляции — `meta.compile` |
| `polza.py` | клиент Media API polza: сухой прогон по умолчанию, трата только с `--live`, оценка цены, лимиты, опрос, скачивание, паспорт, журнал затрат | `estimate JOB(.jsonl) [--ops OP[,OP…]]` — операции над готовым результатом строкой сметы; `run JOB [--live]`; `batch JOBS.jsonl [--parallel 2] [--live]`; `status`, `download`, `history ID`; `upload FILE`; `ops ID …` — результат сверяется с исходником: тот же id и тот же файл — операция не выполнена, код 5 и 0 ₽ в журнале; `models`, `show MODEL`; `ledger --sum`, `ledger --ops` — сверка записей операций с сохранёнными ответами, без сети, `ledger --balance [--baseline RUB]` — журнал против баланса канала; `balance` — чтение без `--live`; `selftest` | паспорт рядом с файлом — с полем `size`: заказанная ступень и фактический размер; журнал `_ledger.jsonl`; коды 0 · 1 задание или проверка · 2 вызов или окружение (нет снимка, файла, модели) · особые: 3 бюджет · 4 таймаут · 5 failed или операция не выполнена · 6 отказ канала (HTTP) · 7 файл не скачан |
| `mp_client.py` | те же правила для каналов RouterAI, Gen-API, polza-chat, polza-images | `estimate JOBS… [--summary]`; `run JOB [--live]`; `batch`; `status`, `download ID --channel C`; `show MODEL --channel C`; `ledger --sum`; `snapshot --channel all`; `balance --channel C [--path P]` — баланс и лимит ключа, чтение без `--live`; `selftest` | `$DDD_HOME/out/ai-media/_mp/<агент>/<дата>/`, общий журнал; коды — как у `polza.py`; отказ генерации или ответ без результата (код 5) — паспорт задания с телом и заголовками ответа канала (поле `response`) |
| `polza_catalog.py` | каталог polza как данные: снимок, нормализация медиа-моделей, таблица, сравнение снимков, цена и проверка входа | `snapshot` — файлы качаются во временную папку, готовый снимок встаёт на место переименованием: оборванный снимок последним не становится; `price MODEL k=v…`; `check MODEL k=v…`; `diff A B`; `table`; `normalize`; `selftest [--offline] [--snapshot SNAP]` — `--offline` — проверки без снимка каталога; цены сверяются с полями последнего снимка | снимок — `$DDD_HOME/cache/ai-media/polza/<дата>[_ЧЧММ]/`; stdout |
| `routing_check.py` | сверка `routing.yaml` с последними снимками каталогов: модели, провайдеры, параметры, цены, диалекты, рубрики, флаги права | `[ROUTING.yaml] [--polza SNAP] [--routerai SNAP] [--genapi SNAP] [--md F] [--json F]`; `--selftest` | таблица вариантов, «Ошибки» и «Предупреждения»; код 0 — расхождений нет, 1 — есть, 2 — нет снимка polza |
| `vlm_to_dna.py` | паспорт визуала бренда: пакет разбора сетки для сессии Opus, черновик из ответа, проверка, сверка прогонов, LUT, вывод из токенов UI, спецификация ассета | `build СЕТКА --name N`; `parse ПАКЕТ --out dna.json`; `validate ФАЙЛ… [--art-direction ФАЙЛ]`; `compare`; `lut`; `from-tokens`; `to-spec DNA --kind … --task … --subject … [--section S] [--slot L] [--edit КАДР --operation OP] --out SPEC`; `selftest` | пакет `$DDD_HOME/out/ai-media/dna/<имя>/`; JSON паспорта и спецификации |

## Приёмка ассетов — `asset_audit.py`

Объединяет проверки соседних утилит вызовом и импортом: цвет и «средний вид», зона текста и контраст, серия, правка и
альфа, текстура, петли видео, иконки, паспорт визуала, провенанс, OCR кириллицы. Пороги — `thresholds.yaml` (у
каждого источник и статус). Моделей утилита не вызывает: оценку по рубрике делает сессия Opus (агент `design-judge`,
протокол `kb/common/judge.md`) по пакету `judge-jobs`, код готовит пакет и разбирает ответы. OCR и тяжёлые шаги берут
блокировку heavy сами — внешним `flock` не оборачивать.

| команда | что делает | выход |
|---|---|---|
| `audit ПУТЬ… [--mode M] [--slot hero\|section\|product\|icon\|og] [--dna DNA] [--expect "строка"]… [--text-zone x0,y0,x1,y1] [--stage web] [--mobile] [--icon-set НАБОР] [--strict]` | файл, список или папка с паспортами `polza.py` / `mp_client.py`; режим — по паспорту, коду задачи, альфе и расширению (`image`, `cutout`, `edit`, `series`, `texture`, `video-loop`, `video-alpha`, `svg-icon`, `og`) | `<OUT>/audit.json` (asset-audit/1: вердикт `pass · warn · needs_human · fail`, коды `QA-*` с порогом и источником, что смотреть человеку, поле `env`), `<OUT>/audit.md`, панели и листы углов; `--strict` — код 1 при `fail` |
| `ocr IMG… [--expect …]` | OCR кириллицы и сверка со строками: пропуск, удвоение, латиница, ё, лишнее слово | JSON |
| `thresholds [--check]` | пороги с источниками; `--check` — ключи кода есть в YAML | stdout |
| `judge-jobs`, `judge-parse`, `agree`, `calibrate` | пакет судьи (`--items`, `--from-stand-page`, `--calibration`), разбор ответов, согласие с голосами заказчика, порог метрики по меткам | `$DDD_HOME/out/ai-media/judge/<имя>/`, ключ слепоты рядом |
| `selftest` | тесты `tests/test_asset_audit.py` (с `--ocr` — и OCR кириллицы) | stdout |

- **Иконки.** `--icon-set` — набор иконок продукта (`conventions.icons.set` карты решений `…/design/system.yaml`, по
  умолчанию `lucide`): шапка и штрих Lucide — брак только у набора Lucide, у другого набора — предупреждение; жёсткий
  цвет — брак у любого. Та же проверка отдельно — `check_icons.py ПАПКА [--ref ПАПКА] [--set НАБОР] [--json F]
  [--md F]`.
- **Метка вендора в углу** (`QA-PROV-VISIBLE-MARK`) — предупреждение с листом углов `<файл>_corners.jpg` и пунктом
  «человеку»: эвристика видимой метки ошибается, решает глаз.
- **Окружение.** Нет модели, пакета или программы (модели OCR, группа svg, `c2patool` и `exiftool`, `ssimulacra2`,
  `ffmpeg`) — проверка не запускается: в `errors` ассета и в разделе «Окружение» `<OUT>/audit.md` — строка «поставьте
  `scripts/install.sh …`», в JSON — поле `env`. Окружение этапа — до его начала: `install.sh --check`.

| утилита | что делает | вызов | выход |
|---|---|---|---|
| `check_icons.py` | линейные SVG-иконки кодом: шапка, цвет, поле, сетка, зазоры, вес, IoU с Lucide; уровень флага — по набору | `ПАПКА [--ref ПАПКА] [--set НАБОР] [--json F] [--md F] [--title T]` | таблица в stdout, `--json` (замеры, `flags`, `levels`), `--md`; без группы svg — строка с командой установки, код 2 |
| `palette.py` | палитра картинок: доминирующие цвета с долями, OKLCH, нейтрали (b > 0 — тёплые, b < 0 — холодные); модуль — ΔE к эталону, перенос цвета, LUT | `IMG… [--k 6] [--json]` | таблица или JSON `{k, images, all}` (`all` — у двух картинок и больше); код 2 — картинка не читается |
| `provenance_check.py` | метки ИИ в файле: C2PA, IPTC/XMP, AIGC в видео, подпись Recraft, строки-маркеры, видимая метка в углах; штамп производной | `scan PATH… [--out DIR] [--corners] [--trust]`; `stamp IN OUT --dst trained\|composite`; `selftest` | `<OUT>/provenance.md`, `<OUT>/provenance.json`, `<OUT>/corners.jpg`; код 0 · 1 самопроверка не прошла · 2 вызов или окружение (нет файла, сбой exiftool или ffmpeg, отказ штампа подписанного файла без `--force`) |
| `edit_check.py` | правка «на месте» и аутпейнт: совмещение, утечка вне цели, защищённая зона, композит оригинала | `check ORIG EDITED [--mask M] [--protect P] [--composite] --out DIR`; `polarity`; `outpaint ORIG EXTENDED`; `selftest` | JSON; в `--out` — карта разницы, композит, лист «оригинал · правка · разница · композит» |
| `alpha_check.py` | прозрачность: против эталона, ореол без эталона, нарисованная шахматка | `metrics PRED GT [--rgb GT_RGBA]`; `halo RGBA [--bg #hex]`; `fake IMG` | JSON |
| `tile_check.py` | бесшовность текстуры, тайл разрезом минимальной ошибки, превью | `check IMG`; `cut IMG OUT [--overlap 96]`; `preview IMG OUT` | JSON, картинка |
| `video_loop_check.py` | петля и видео: шов, живость, склейки, мёртвые концы, дрейф неподвижных зон, хромакей, стык клипов, лист | `loop VIDEO [--control V]`; `trim VIDEO OUT --auto`; `drift VIDEO --mask M`; `chroma`; `join A B`; `sheet`; `colormatch`; `selftest` | JSON; мезонин без потерь у `trim` |
| `loop_rife_bridge.py` | мост петли кадрами RIFE от последнего кадра к первому | `IN.mp4 OUT.mp4 [k=8]` | мезонин x264 `-qp 0`; нужен `rife-ncnn-vulkan` в `$DDD_HOME/bin` |
| `avif_pick.sh` | минимальный AVIF, проходящий порог SSIMULACRA2 | `<вход.png> <выход.avif> [порог=80]` | файл, строки q · байты · s2; нужны `avifenc`, `ssimulacra2` в `$DDD_HOME/bin` |
| `svg_sheet.py` | SVG (Recraft, LLM → SVG): метрики, гигиена с сохранением подписи, перекраска в палитру, листы на светлом и тёмном; `--current-color` — одноцветные иконки с `currentColor` цветом темы: без ключа на тёмном фоне они не видны | `sheet SVG… --out DIR [--palette …] [--mode icons\|illustration] [--current-color]`; `recolor SVG --palette … --out F`; `render SVG --png 1024 --out F`; `--selftest` | листы, JSON; нужны группа svg и `svgo` (`$DDD_HOME/node`) |
| `split_recraft.py` | нарезка листа иконок Recraft на отдельные SVG по ячейкам сетки | `<лист.svg> <папка> --grid 4x2 --names a,b,-,… [--prefix P] [--on-exists refuse\|suffix] [--no-svgo]`; `--selftest` | SVG на названную ячейку, мастер — в `<папка>/_source/`; код 0 · 1 лист не сошёлся с заданием · 2 вызов · 3 имя занято |
| `page_accept.py` | приёмка страницы с ассетами в Chromium: вес первого экрана, LCP, CLS, картинки, видео и постер, движение, reduce, F83, ширины приёмки | `PAGE.html\|URL --out DIR [--budget-profile P] [--mobile] [--throttle] [--acceptance] [--no-lock]`; `--selftest` — замок браузера утилита берёт сама, `--no-lock` снимает только тяжёлый замок тишины | `<DIR>/accept_<режим>.json` (его читает `page_gates.py --accept`), снимки; код 0 — замер выполнен (с `--strict` 1 — есть провалы) · 2 вызов |
| `layout_check.py` | вёрстка текстового шаблона по DOM до OCR: строки за холстом и на непрозрачной части товара, переполнения, nowrap-флекс; замок браузера берёт сама | `ШАБЛОН.html ВЫРЕЗ.png` (товар — элемент `.tin`); `page ФАЙЛ.html [1440x900 412x915]` | `$DDD_HOME/out/ai-media/layout_check/`; код 2 — нет входа |

Модули (импорт из соседних утилит; у каждого есть короткий CLI — шапка файла): `image_metrics.py` (цвет, «HDR»),
`composition_metrics.py` («средний вид» кадра), `text_zone.py` (контраст текста над картинкой и скрим),
`series_metrics.py` (согласованность серии), `split_grid.py` (сетка одной генерации → ячейки).

## Выбор из вариантов — `stand_run.py`

Страница слепых пар для заказчика: вход — папка выходов `polza.py` (паспорта), таблица `collect` или папка картинок
без паспортов (кадры 3D, снимки сборок). Задания плана (`prompt_compile.py jobs`) — группа на спецификацию, пары между
всеми её вариантами; папка картинок — группа на подпапку, вариант — имя файла. Ключ «картинка → вариант» лежит рядом с
папкой страницы (`<СТРАНИЦА>.key.json`), в саму страницу не попадает.

| команда | вызов | выход |
|---|---|---|
| `page` | `ВХОД --out СТРАНИЦА [--tests ГРУППА,…] [--repeat 0.1] [--seed 7]`; тексты — `--text ЛИСТ.md [--text-key КЛЮЧ.yaml]` (лист `copydeck.py export-variants`) | `<СТРАНИЦА>/index.html` и картинки пар, ключ рядом; повторы со сменой сторон, контрольные и одинаковые пары |
| `tally` | `VOTES.json… --key СТРАНИЦА.key.json [--out tally.md] [--selection OUT.yaml]` | доли побед с интервалом Уилсона, Брэдли–Терри, согласованность повторов, позиция A; `--selection` — победы меток для `copydeck.py apply-selection` |
| `collect` | `[--root DIR] [--agent A] [--out results.jsonl]`; корень по умолчанию — выходы `polza.py` (`POLZA_OUT_ROOT`, иначе `$DDD_HOME/out/ai-media/_polza`) | строка на файл результата; путь паспорта — от корня |
| `selftest` | — | нормализация строк, Уилсон, Брэдли–Терри, страницы текстов и картинок, сбор паспортов вне базы, кодирование картинок, папка заданий и имя агента, сборка стенда с моделью вне снимка, путь входа от папки заданий |

Пары на чёткость и мелкую деталь — `page ВХОД --out СТРАНИЦА --maxside 0 --lossless`: картинки страницы — PNG без
уменьшения и без потерь. Судья видит те же пары, что заказчик: `asset_audit.py judge-jobs --from-stand-page СТРАНИЦА`.

## Деньги и ключи

- Сухой прогон — по умолчанию у `polza.py` и `mp_client.py`: точный запрос и цена без траты; трата — только `--live`.
- Ключи — только у владельца денег, вне репозитория: переменные окружения `POLZA_API_KEY`, `ROUTERAI_API_KEY`,
  `GENAPI_API_KEY` или файлы `~/.config/{polza,routerai,genapi}/api_key` (права 600); читаются только при `--live`
  и при чтении баланса (`balance`, `ledger --balance`), в журнал и паспорта не пишутся.
- Коды выхода `polza.py` и `mp_client.py`: 0 — успех; 1 — ошибка задания или проверки; 2 — ошибка вызова или окружения
  (нет снимка каталога, файла, модели); особые: 3 — отказ по бюджету или цене, 4 — таймаут опроса (дожать `download ID
  --live`), 5 — генерация не удалась или операция не выполнена, 6 — отказ канала (HTTP), 7 — файл не скачан.
- Лимиты: `POLZA_BUDGET_TOTAL` (2000 ₽, общий журнал машины), `POLZA_MAX_JOB` (60 ₽ на задание), `POLZA_BUDGET_AGENT`;
  у RouterAI и Gen-API `ROUTERAI_BUDGET_TOTAL`, `GENAPI_BUDGET_TOTAL` по умолчанию 0 — без явного лимита `--live` не
  тратит. Лимит — страховка машины; сумму трат утверждает заказчик планом ассетов.

## Обслуживание базы

Стенд моделей и сверка каталогов — для обновления матрицы маршрутов и базы, этапы скилла их не зовут:
`stand_run.py build | estimate | run | metrics | sheet | ministand` (рецепты стенда — ключ `recipes` файла
`kb/ai-media/13-routing-matrix/stand/tasks.yaml` → `$DDD_HOME/out/ai-media/stand` или `--jobs-dir DIR`; имя агента в
заданиях — ключ `--agent`; модель рецепта вне снимка каталога — строка «ОШИБКА», остальные группы собираются, код 1;
вход рецепта без файла — строка «входа нет в скилле»; входы читаются от папки заданий — так их читают `polza.py` и
`metrics`), `routing_check.py` после нового снимка каталогов (процедура —
`kb/ai-media/13-routing-matrix/04-update-procedure.md`), `polza_catalog.py diff A B` и `channel_diff.py [--ra A B]
[--ga A B]` (что изменилось между снимками), `asset_inventory.py URL OUT_DIR [--mobile] [--quick]` (инвентарь
визуальных ассетов живой страницы; `--selftest`).

## Тесты и данные

- `tests/test_asset_audit.py [--ocr] [-v]` — тесты приёмки (они же `asset_audit.py selftest`);
  `tests/test_prompt_compile.py` и `tests/test_prompt_compile_x2.py` — компилятор, нужен снимок каталога polza;
  спецификации тестов — `tests/fixtures/`.
- `data/genapi_prices_2026-09-23.json` — прайс Gen-API для `mp_client.py`; `data/lucide-ref/` — эталонные иконки
  Lucide (ISC) для `check_icons.py`; `data/svgo.keep-signature.config.mjs` — конфиг `svgo`, сохраняющий подпись Recraft.
