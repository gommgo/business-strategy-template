# Рецепты hero: пара кадров, петля, парящий объект, синемаграф, два состояния, абстрактный фон

Волна 3 · агент M · 24.09.2026 · опора — файлы папок 01, 05, 06, 08, 09, 10, 11, 12, 13 и отчёты волн 1–3 (≈ 40 файлов и
разделов базы целиком, 9 дайджестов роликов через файлы соседей + дайджест Weave [V:I9xdmNZxIfA] целиком) · опытов 5
(`99-raw/experiments/M/01…03`, `09`, демо) · снимок каталога polza `2026-09-24` (к 23.09 17:45 изменился только
`output_format` у `google/gemini-3-pro-image-preview`).
Локальные шаги проверены на своих рендерах Blender и CC0; шаги генерации — `[не проверено]` до фазы 5, у каждого есть задание.
[поправка фазы 5, 25.09.2026: живые прогоны закрыли hero-кадр (F-04, E-08, MS-02), петлю (I-03, MS-03, MS-05) и облёт (SC-03);
M-01…M-03 не запускались — место демо занял лендинг сессии 4; итог по возможностям — `04-capability-map.md`]

## Выжимка для агента

1. **Каждый рецепт — одна цепочка из 10 звеньев**: слот плана → паспорт → спецификация → маршрут → компиляция → задание
   фазы 5 → проверка → постобработка → провенанс → доставка шаблоном J → приёмка страницы; звено без команды — не рецепт →
   §0 `[проверено: M/02–M/09 на демо]`.
2. **Hero — это два мастера, а не один**: 16:9 для десктопа и отдельный кадр 4:5 для телефона со своей зоной текста сверху;
   из 16:9 в 4:5 остаётся 45 % ширины → §1.1 `[проверено: M/02, демо; F/03]`.
3. **У `openai/gpt-image-2.5-sunburst` в polza нет 4:5** (есть 3:4, 2:3, 9:16, 9:8, 8:9, 16:27, 27:16) → телефонный мастер
   генерировать 3:4 и кадрировать до 4:5 (−6,25 % высоты по фокусу) → §1.2 `[документация: каталог 2026-09-24]`.
4. **Композицию выбирать на 1K, финал — 2K по выбранному кадру референсом** («keep the exact scene… re-render at higher
   detail»): 4 ₽ перебор + 7 ₽ финал вместо 7 ₽ × N; перенос раскладки референсом — гипотеза (E-16, M-01) → §1.3 `[не проверено]`
   [поправка фазы 5, 25.09.2026: подтверждено — проба 1K (4 ₽) → 2K с пробой-референсом (7 ₽) «почти копирует» одобренный кадр,
   без референса тот же промт даёт другой кадр — n = 1 → `99-raw/phase5/runs/MS-marea/MS-02-hero.log`; E-16 не запускался].
5. **Гладкий кадр сжимается ниже порога LCP**: наш hero 1536×864 — AVIF 3,2 КБ при SSIMULACRA2 ≥ 80 (0,02 бит/px < 0,05) →
   LCP на десктопе — H1 или видео-слой, на телефоне — картинка 4:5 (2,6 КБ, 80 мс) → §1.5 `[проверено: демо, page_accept]`.
6. **Постер кадра 0 — через `avif_pick.sh 80`, а не фиксированным Pillow `quality=50`**: у нас Pillow q50 дал SSIMULACRA2 79,5
   (`QA-ENCODE-QUALITY` fail), avifenc q35 — 80,1 при 3,4 КБ → §2.4 `[проверено: M/09]`.
7. **Тихая петля: `bytedance/seedance-1.5-pro` `images` [A, A] + `fixed_lens: "true"`, 480p 4 с — 5,25 ₽**; срез ровно одного
   дубля последнего кадра, шов — только на мезонине без потерь, живость — к i2v-контролю → §2 `[не проверено: I-02, I-03]`
   [поправка фазы 5, 25.09.2026: I-03 — шов 1,28, живость 0,83 (рябь, n = 1); крупная форма не замыкается (3,29–3,45) → RIFE-мост
   8 кадров 0,69–0,84, 1080p 8 с (45 ₽) + RIFE — 0,41 → `99-raw/phase5/runs/2.4-loops/I-03.loop.json`, `04-capability-map.md` §2.3].
8. **Шов меряют на мезонине без потерь** (x264 `-qp 0`): наш синемаграф — 1,04 на мезонине и 3,3–4,6 на финалах (пульс
   ключевого кадра) → `asset_audit` ставит финалу `needs_human`, а не `fail` → §2.3 `[проверено: M/03; K/03]`.
9. **CRF — по сохранению движения, у синемаграфа — в маске движения**: `motion_keep` целого кадра у синемаграфа врёт (AV1
   CRF 24 → 2,35: шум кодека в неподвижных 93 % кадра «двигается» сильнее медианы) → мерить `keep_in` в зоне пара: AV1 CRF 36
   — 0,84, CRF 40 — 0,71 → берём 36 → §4.4 `[проверено: M/03]`.
10. **Синемаграф дёшево и резко: 720p-видео + мастер 2K `maskedmerge`** — неподвижное из мастера, движущееся из видео; наш
    финал AV1 1536×864 5 с — 18,2 КБ, H.264 — 91,7 КБ → §4 `[проверено: M/03 на процедурном паре; генерация — M-03]`.
11. **Один очаг движения на синемаграф**, промт — только движение: «The steam above the coffee rises in thin wisps…» + всё
    прочее «stay perfectly still» → §4.2 `[документация D2; V:SLnGJ9iezYo 03:05]`.
12. **Видео hero — слой поверх `<picture>`-постера после `load`** (`js/hero-video.js` J): reduce, Save-Data, 2G → 0 байт видео;
    на телефоне видео не грузить совсем, если движение не несёт смысла (наш Pixel 7 — 50,9 КБ первого экрана) → §2.5
    `[проверено: демо; J/04]`.
13. **Постер ниже порога энтропии → LCP становится само видео-слоем** (у нас VIDEO 204 мс без троттлинга, 1052 мс с ним), при
    reduce — H1 (120 мс): это допустимо, но LCP теперь зависит от веса видео → держать петлю легкой → §1.5 `[проверено: демо]`.
14. **Кодировать с полными тегами BT.709 и метками вендора одной строкой**: `setparams=color_primaries=bt709:color_trc=bt709:
    colorspace=bt709:range=tv` + `-map_metadata 0 -movflags use_metadata_tags+faststart` → §2.4 `[проверено: J/02b; L/02; M/03]`.
15. **Бесконечная петля любой длины — кнопка паузы** (WCAG 2.2.2 про длительность движения): у демо кнопка 44 px, видео играет
    на 6-й секунде, `page_accept` — PASS → §2.5 `[проверено: демо]`.
16. **Парящий объект — две картинки из одной генерации + ключ по оттенку объекта**: золото, бронза, жёлтое, зелёное →
    `#FF00FF`; красное, розовое, фиолетовое → `#00B140`; товар с надписью i2v не отдавать (этикетку перерисует) → 2.5D из
    настоящего выреза → §3 `[проверено: I/03; не проверено: I-06, M-07]` [поправка фазы 5, 25.09.2026: было — «этикетку
    перерисует»; фаза 5: облёт Kling 3 std 5 с держит надпись в 11 из 11 кадров по OCR (придуманный продукт, n = 1) → i2v товара
    с надписью допустим с OCR по кадрам; на ключе и настоящий товар — не проверено → `99-raw/phase5/runs/SC-showcase/SC-03-frames/ocr.json`].
17. **Альфа-видео — stacked alpha AV1 → WebGL2**, движение ≤ 5 с и стоп на кадре 0 (без кнопки), статичный AVIF с альфой до
    первого кадра и при reduce → §3.4 `[проверено: J/05, страница 03]`.
18. **Два состояния — второе правкой от того же мастера, статикой**; видео верхнего слоя — только по взаимодействию (без наведения
    0 байт); прожектор — `mask-image: radial-gradient` + кнопка состояния для касаний → §5 `[проверено: J/08; не проверено: M-06]`
    [поправка фазы 5, 25.09.2026: прожектор честен только на совмещённых кадрах — концы одного FLF с `fixed_lens` совпадают до
    пикселя, две отдельные генерации — нет; правка «другой свет» (NB2 2K, 7,2 ₽) сгенерирована, сдвиг не мерен → демо
    `99-raw/phase5/showcase/demos/05-spotlight/`].
19. **Абстрактный фон — лестница дешевизны: CSS → SVG → шейдер → картинка → видео**; тёмный градиент — только CSS (Chromium
    дизерит CSS, не AVIF/AV1: ступень 0,04 против 0,35–0,55) → §6 `[проверено: J/03, H/05b]`.
20. **Текст hero — HTML поверх, цвет по зоне, скрим — по проверке F83 по буквам и по кадрам видео**: в демо #1C1B18 по светлой
    штукатурке 12,32 : 1 на худшем кадре — скрим только косметический (α ≤ 0,34) → §1.6 `[проверено: демо; F/02]`.
21. **Провенанс в каждом рецепте**: скан мастера как скачан → кодирование → `provenance_check.py stamp --dst trained|composite`
    → `asset_audit --stage web`; видимая иконка «AI» — только дипфейкам ЕС (строки 6, 8, 11–13 таблицы L) → §0.3
    `[документация L; проверено: L/01, L/02]`.
22. **`asset_audit.py` сам берёт `heavy.lock` под OCR, `page_accept.py` — `browser.lock`**: во внешний `flock` не оборачивать;
    до 24.09.2026 обёртка давала самоблокировку (у нас 10 минут простоя), теперь обе утилиты видят замок у процесса-предка и не
    ждут (X, X2) → §0.2 `[проверено: M/02; X2 — page_accept под flock 18 с]`.
23. **Финалы M в фазе 5 — 24,50 ₽ минимум** (M-01 7, M-02 7, M-03 10,5): hero-пара и синемаграф бренда, которых нет в чужих
    тестах; всё остальное демо берёт из E, F, G, H, I через `meta.inputs_from` → §0.5 `[документация: M-plan]`.
24. **Каркас — «машина бренда», а не набор промтов**: паспорт и описатель кэшируются по хэшу входов, новый месяц — смена двух
    входов (место, название), правка одного свойства — отдельный шаг с `edit_check`, видео — i2v от выбранного кадра, 3 прогона
    и выбор; текст — слоем шаблона с проверкой переполнения → §0.4 [V:I9xdmNZxIfA 19:40–35:03] `[практика]`.

## 0. Каркас рецепта (общий для 01–03)

### 0.1 Десять звеньев

| № | Звено | Инструмент | Вход → выход | Где правила |
|---|---|---|---|---|
| 1 | слот | план ассетов YAML (A `01/01` §8) | тип страницы → слот, ступень лестницы, `ai_fit` | `../01-web-assets-landscape/01-…` §2, §8 |
| 2 | паспорт | `vlm_to_dna.py from-tokens` → руками → `validate` | токены UI → `dna-*.json` | `../06-art-direction-consistency/01-…` §3, §6 |
| 3 | спецификация | `vlm_to_dna.py to-spec` | паспорт + сюжет → `*.spec.json` (asset-spec v0.2) | `../05-prompting/03-…`, схема |
| 4 | маршрут | `routing.v0.yaml` (v1 — N) по коду задачи | код → модель, параметры, цена | `../13-routing-matrix/` |
| 5 | компиляция | `prompt_compile.py compile/jobs/chain/ratios` | спецификация → промт диалекта + параметры + цена | `../05-prompting/04-…`, `05-…` |
| 6 | задание фазы 5 | `jobs --dialects <семейный> --repeats 1` → `polza.py estimate` | `99-raw/phase5/jobs/<агент>-NN-*.jsonl`, 0 ошибок | `../99-raw/phase5/README.md` |
| 7 | проверка | `asset_audit.py audit … --strict` (+ `edit_check`, `alpha_check`, `video_loop_check`, `tile_check`; шаблоны с текстом — DOM `layout_check.py` M/06 до OCR) | файл → `audit.json` с кодами `QA-*` | `../11-evaluation-qa/01-…`; `03` §6.1 |
| 8 | постобработка | H (картинки), I (видео), F (грейд `.cube`) | мастер → производные | `../08-…`, `../09-…` |
| 9 | провенанс | `provenance_check.py scan` → кодирование → `stamp` | мастер побайтно; производная с XMP | `../12-legal-provenance/02-…` §5 |
| 10 | доставка и приёмка | шаблон `../10-web-integration/pages/00-hero-summary.html` → `page_accept.py` | страница → PASS/FAIL | `../10-web-integration/04-…` |

### 0.2 Команды звеньев 2–7 (проверены на демо)

```bash
# prompt_compile.py 2.1 · vlm_to_dna.py · polza.py — [проверено: 14-recipes/examples/demo-landing/brand, 99-raw/phase5/jobs/M-0*]
T=99-raw/tools; V=$T/venv-D2/bin/python; B=14-recipes/examples/demo-landing/brand
python3 $T/vlm_to_dna.py from-tokens $B/tokens.json --out $B/dna.json --id forest-roast --adjectives "тёплый,ремесленный,спокойный"
$V $T/vlm_to_dna.py validate $B/dna.json                      # jsonschema + линт; «ok»: true обязательно
$V $T/vlm_to_dna.py to-spec $B/dna.json --kind photo --task IMG-HERO-PHOTO --slot hero --ratio 16:9 \
   --subject "a glazed off-white ceramic cup of black coffee on a pale oak table by a tall window in the morning" --out $B/specs/hero.spec.json
$V $T/prompt_compile.py compile $B/specs/hero.spec.json --model openai/gpt-image-2.5-sunburst      # прочитать промт глазами
$V $T/prompt_compile.py jobs $B/specs/hero.spec.json --models openai/gpt-image-2.5-sunburst --dialects sections \
   --repeats 1 --test M-01 --agent M --out 99-raw/phase5/jobs/M-01-hero-16x9-2k.jsonl                  # без --dialects — 3 плеча A/B
python3 $T/polza.py estimate 99-raw/phase5/jobs/M-01-hero-16x9-2k.jsonl                                # 0 ошибок, 7,00 ₽
python3 $T/asset_audit.py audit master.png --slot hero --text-zone 0,0,0.45,1 --dna $B/dna.json --out audit/ --strict
# НЕ оборачивать asset_audit.py в flock heavy.lock и page_accept.py в flock browser.lock — они берут блокировку сами
```

Ловушки стыка, найденные на демо: `focal_point` — объект `{"x", "y"}` (список ронял компилятор `TypeError` в `_inside`; с v2.1.1 —
ошибка схемы); соотношение OG в спецификации — `40:21` (шаблон `^[0-9]{1,2}:[0-9]{1,2}$` не принимает `1.91:1`); поверхность
зоны текста можно писать и со словом «empty» (v2.1.1 не повторяет «empty, uncluttered») `[поправка X2 24.09.2026: компилятор
v2.1.1, тесты `../../scripts/ai-media/tests/test_prompt_compile_x2.py` 15/15]`; `from-tokens` пишет в блок иллюстраций
«transparent background» — у моделей без альфы это приглашение нарисовать шахматку → «plain … background» и
`illustration.background: plate` `[проверено: M, 24.09.2026]`.

### 0.3 Провенанс (звено 9) — одинаково во всех рецептах

```bash
# provenance_check.py 0.1 · exiftool 13.59 · c2patool 0.27.22 — [проверено: L/01, L/02; скан демо — M/09]
python3 ../../scripts/ai-media/provenance_check.py scan <выход как скачан> --corners --trust --out prov/      # до любых правок
# … постобработка, финальное кодирование …
python3 ../../scripts/ai-media/provenance_check.py stamp web.avif web.avif --dst trained --system "gpt-image-2.5-sunburst via polza/mie"
python3 ../../scripts/ai-media/provenance_check.py stamp web.mp4 web.mp4 --dst trained                        # +2,9 КБ, moov впереди
python3 ../../scripts/ai-media/asset_audit.py audit web.avif --stage web --master master.png --slot hero --out audit_web/
```

`--dst composite` — реальный товар/кадр + ИИ-окружение (L `04` §2 строка 7); `trained` — сгенерировано целиком (строки 1, 3–5).
Видимая иконка ЕС — только строки 6, 8, 11–13 (реалистичное «место как настоящее», изменённое представление о товаре, люди).
Hero «чашка у окна» — строка 5: без видимой метки, XMP в файле, в подвале ссылка «Об ИИ-контенте» (Кодекс, Measure 2.1).

### 0.4 Каркас как «машина бренда» (граф Weave, Config 2026)

Тот же каркас показала Figma на демо-бренде: сетка бренд-картинок → LLM-описатель («expert brand visual analyst… visual
production brief») = наш паспорт → LLM пишет варианты промтов под переменную (место, сюжет) = наш компилятор со слотами →
итератор → модель → детерминированный грейд одной цепочкой для картинок и видео (цвет, уровни, кроп 16:9) = наш `.cube` →
шаблоны с входами «картинка» и «текст» (фреймы соцсетей, письма) = наши HTML-шаблоны J и OG → «следующий месяц = смена двух
входов», описатель не пересчитывается [V:I9xdmNZxIfA 19:40–35:03] `[практика; мнение вендора о самом инструменте]`. Отсюда
правила: кэш звеньев по хэшу входов (паспорт не пересобирать, если токены не менялись), правка одного свойства (свет) — отдельный
шаг с проверкой «вне свойства ничего не изменилось» (у Weave — нода Compare, у нас — `edit_check.py`), текст — всегда слоем
шаблона, проверка переполнения текста после подстановки (у Weave длинное название не влезло во фрейм
[V:I9xdmNZxIfA 30:58–33:02]; у нас — `nowrap` для диапазонов и `page_accept` F83) [V:I9xdmNZxIfA 06:24–07:26]
[V:I9xdmNZxIfA 14:34–15:34]. Видео в этой машине — i2v от выбранного кадра, 3 прогона и выбор лучшего («slow motion shot, camera
steady tracking shot»; у лучшего прогона всё равно дефект ноги) [V:I9xdmNZxIfA 11:31–12:32] [V:I9xdmNZxIfA 16:34] — у нас §2.2 и
best-of-N по `video_loop_check`. Промышленный аналог — конвейер Klarna «генерация → апскейл → вырез → проверка бренда»
(`99-raw/reports/wave1-A-report.md` §4 «M»; пресс-релиз Klarna 28.05.2024 — A `01/03` [S21]) `[документация компании]`: у нас
апскейл — до кодирования (A `01/01` §4.2), вырез — H `08/01`, проверка бренда — `asset_audit --dna` + глаз.

### 0.5 Финалы фазы 5 и переиспользование

M платит только за hero бренда (M-01…M-03, 24,50 ₽) и по воротам F-07 — за 3D-иконки (M-04, 12 ₽); расширенный уровень
(M-06 вечер, M-07 парящие зёрна, M-08 иллюстрации) — +23,25 ₽ (`99-raw/phase5/M-plan.md`). Остальные слоты демо — выходы
чужих тестов: F-04 (кадр B), E-10 #1 (банка на травертине), E-15 S14 (стена `#1F5E3B`), G-01…G-03 (метафоры иконок).

## 1. Hero-пара: 16:9 + отдельный телефонный кадр (`IMG-HERO-PHOTO`)

### 1.1 Когда и что

Слот hero, ступень «картинка» (A `01/01` §2.2); `ai_fit: conditional` — атмосфера и сцена без людей, не сам товар (L строка 5).
Два мастера: 16:9 (зона текста слева 40–45 %, объект в правой трети, `centroid_x` ≥ 0,62) и 4:5 (зона сверху 35 %, объект в
нижних 60 %). Арифметика кадра (F/03): из 16:9 в 4:5 остаётся 45 % ширины, в 9:16 — 31,6 % → кроп десктопного мастера на
телефон режет либо текстовую зону, либо объект; лидеры делают отдельный кадр у 8 из 10 (A).

### 1.2 Маршрут и параметры (routing v0 `IMG-HERO-PHOTO`, каталог 2026-09-24)

| Роль | Модель | Параметры | ₽ |
|---|---|---|---|
| перебор композиции | `openai/gpt-image-2.5-sunburst` | `image_resolution: "1K"`, `aspect_ratio: "16:9"` | 4,00 |
| финал десктопа | то же | `"2K"`, `"16:9"`, `images: [выбранный 1K]` | 7,00 |
| финал телефона | то же | `"2K"`, **`"3:4"`** (4:5 в каталоге нет) → кроп 4:5 | 7,00 |
| запас | `google/gemini-3.1-flash-image-preview` | `"2K"`, `"16:9"` | 7,20 |
| дёшево | `bytedance/seedream-4` | `"4K"`, `"21:9"` — если E-01 без видимого знака | 3,00 |

2K, а не 4K: у фотореализма 4K «слишком гладкий» (E-09 проверяет) `[мнение ×2, W1]`. `provider: {"only": ["mie"],
"allow_fallbacks": false}` — всегда (запасная ступень Sunburst = 11 ₽).
[поправка фазы 5, 25.09.2026: E-08 (интерьер × 6 моделей, голос заказчика вслепую, 1 чел.) — хорошо Sunburst, Flare, NB2; NB Pro
«слишком ровно»; Seedream 5 Pro «сразу минус»; FLUX.2 Pro «так себе»; F-04 — блок композиции 3 из 3 (центр масс x 0,81 против
0,30–0,39 без блока); Seedream 4 «4K» 21:9 = 2352×1008 (≈ 2,4K), видимой метки нет (E-01); Sunburst 4K — настоящие 3840×2160 за
11 ₽; E-09 (2K против 4K) не запускался → `99-raw/phase5/runs/2.5-stand/audit-F-04/audit.json`, `04-capability-map.md` §2.1]

### 1.3 Промт (компилятор, диалект `sections`)

```text
// openai/gpt-image-2.5-sunburst · polza 2026-09-24 · 2K 16:9 · images: [кадр F-04 плеча B] · [не проверено: M-01]
Series style (keep identical): Documentary still-life photograph of everyday objects of a small coffee roastery - glazed
off-white ceramics, pale oak, washed linen, kraft paper; soft morning window light from the right with long gentle shadows;
warm neutral colour: cream plaster, pale oak and off-white ceramics with one small deep forest-green accent; 35mm lens
slightly above table height, medium depth of field; fine natural film grain; unpolished, lived-in details: a few crumbs, a
folded napkin, a faint ring on the wood.
References: Follow the composition of Image 1: keep the exact scene, objects, camera angle, crop and light of this image;
re-render it at higher detail.
Subject: A glazed off-white ceramic cup of black coffee on a pale oak table by a tall window in the morning.
Composition: Medium shot, at eye level, main subject in the right third of the frame.
Composition rules: Off-center subject placed on a rule-of-thirds line, asymmetric composition, natural imperfections.
Negative space: The left 45 percent of the frame is an empty, uncluttered evenly lit cream plaster wall, even, low contrast,
creating clean negative space for a headline.
Lighting: Soft window, light from the right, early morning.
Requirements: No one in the frame, clean unmarked surfaces, plain black coffee seen from slightly above, medium depth of
field, the wall stays readable.
Constraints: No text.
```

Полный промт с палитрой — `99-raw/phase5/jobs/M-01-hero-16x9-2k.jsonl`; телефонный — `M-02` (референс роли `subject`:
«the same cup, table, napkin, window light and colours; compose them anew for a vertical frame», зона «top 35 percent»).
[поправка фазы 5, 25.09.2026: M-01 и M-02 не запускались; та же схема на другой сцене — MS-02: 2K по пробе-референсу и телефонный
3:4 (1536×2048, 7 ₽; `asset_audit` — warn `QA-COMP-CLUTTER`, ожидаемо) → `99-raw/phase5/runs/MS-marea/audit-MS-02/audit.md`]

### 1.4 Постобработка и доставка (проверено на демо)

```bash
# Pillow 11.3 · ffmpeg 7.1.5 lut3d · avifenc 1.4.2 · cwebp 1.6.0 · ssimulacra2 (libjxl 0.12.0) — [проверено: M/02 make_hero.py]
python3 ../../scripts/ai-media/vlm_to_dna.py lut brand/dna.json --out brand/brand.cube              # грейд из чисел паспорта
ffmpeg -threads 4 -i master_16x9.png -vf "lut3d=file=brand/brand.cube:interp=tetrahedral" graded_16x9.png
# лестница 640/960/1280/1536 (+1920/2560 для настоящего 2K) по SSIMULACRA2 ≥ 80 — make_hero.py или:
99-raw/tools/avif_pick.sh graded_16x9_1280.png hero-16x9-1280.avif 80
```

- Апскейл, если мастер меньше слота: только Lanczos (H/02: Real-ESRGAN хуже на 15–103 пункта SSIMULACRA2); наш рендер
  1024 → 1536 Lanczos ×1,5 прошёл глаз на 1440 CSS-px при DPR 1; на DPR 2 заметно мягче — финал 2K `[проверено: M/02]`.
- Порядок: апскейл → правки и композит → грейд → зерно (CSS поверх, 7 %, `soft-light`) → кодирование последним (H `08/04` §5).
- Разметка — шаблон J 00: `<source media="(max-width: 699px)" … width height>` для 4:5, `data-focal` c точкой спецификации
  (`focal.js`, формула F), `fetchpriority="high"`, без `loading="lazy"`; hero `calc(100svh − 64px)` — не на весь вьюпорт.

### 1.5 Числа демо и LCP

| Файл | Размер | AVIF / WebP при s2 ≥ 80 | LCP |
|---|---|---|---|
| 16:9 мастер 1536×864 (рендер + Lanczos + LUT) | 1536 | 3,2 / 9,3 КБ | не кандидат: 0,02 бит/px < 0,05 (J) |
| 4:5 мастер 820×1024 | 820 | 2,6 / 6,0 КБ | кандидат на Pixel 7: 80 мс (524 мс при CPU×4 + 1,6 Мбит/с) |

Гладкий рендер и гладкий ИИ-кадр (J/01: 3–4,8 КБ) выпадают из LCP на десктопе; LCP становится H1 (reduce: 120 мс) или
видео-слой, когда он есть (204 мс). Заглушку-цвет LQIP брать из среднего цвета мастера (у нас `#dcd2c6` / `#ddd4c8`)
`[проверено: демо, page_accept, asset_inventory]`.

### 1.6 Проверка и приёмка

- `asset_audit.py audit master.png --slot hero --text-zone 0,0,0.45,1 --dna …`: у демо — warn (`QA-PALETTE-OFF`: найдено 2 из 5
  цветов паспорта — в кадре нет лесного зелёного и тёмной обжарки), `centroid_x` 0,731, плотность краёв зоны 0,0, `#111111` —
  9,51 : 1 без скрима; `QA-COLOR-WARM` b* +6,7 — info, тёплый белый — стиль паспорта `[проверено: M/02]`.
- F83 на странице по буквам и кадрам: H1 12,32, лид 9,26, кикер 13 px 6,88 (телефон 11,24 / 8,41 / 6,41) → скрим оставлен
  косметическим (α 0,34 → 0 к 58 % ширины) `[проверено: демо]`.
- Ручная приёмка — `11-evaluation-qa/03` §3.1 (≈ 2 мин): 10–20 с взгляда на hero в слоте, зум 200 % по сетке 3×3.

### 1.7 Цена и время

Фаза 5: перебор F-04 (24 ₽ у F) + M-01 7 ₽ + M-02 7 ₽; локально: рендер 2 кадров 36–40 с (Cycles 64), `make_hero.py` 12 с.

## 2. Hero-петля (`VID-HERO-LOOP`)

### 2.1 Маршрут

| Роль | Модель · параметры | ₽ | Тест |
|---|---|---|---|
| дёшево и тихо | `bytedance/seedance-1.5-pro`, `images` [A, A], `fixed_lens: "true"`, `resolution: "480p"`, `duration: "4"`, `generate_audio: "false"`, `aspect_ratio: "16:9"` | 5,25 (720p — 10,50; 1080p — 22,50) | I-03 |
| контроль живости | то же, `images` [A] (без второго кадра) | 5,25 | I-01 |
| премиум | `kling/v3` [A, A] `mode: std`, 5 с, `sound: "false"`; GA `google/gemini-omni-1.1-flash` `first_frame_url` = `last_frame_url` (URL хранилища), 1080p = 48 ₽ | 50 / 48 | I-09, I-15 |

Ценовые параметры — явно: без них запасная ступень Seedance 1.5 Pro — 135 ₽. Звук у Veo, Omni, Wan, H3 Max параметром не
выключается → `-an` при нормализации (D2).
[поправка фазы 5, 25.09.2026: шов петли — Seedance 1.5 Pro [A,A] + `fixed_lens` 1,28 (I-03) против Kling 3 std 2,12 (I-09) и Omni
5,08 (I-15); Kling 3 pro 1080p [A,A] (48 ₽) — почти стоп-кадр, движение 0,024, шов 6,98 (VM-02) → премиум брать ради 1080p и
камеры, не ради петли; финал 1080p — Seedance 1.5 Pro 22,5 ₽ за 4 с, 45 ₽ за 8 с → `99-raw/phase5/runs/2.4-loops/`,
`99-raw/phase5/runs/6-video-models/VM-02-kling3pro-loop-1080p.loop.json`]

### 2.2 Промт (только движение, запреты последними)

```text
// bytedance/seedance-1.5-pro · polza 2026-09-24 · [A, A] · fixed_lens "true" · 480p 4 с · [не проверено: I-03]
Calm dawn over the lake. Small wind ripples drift slowly across the water from left to right, and the soft pastel reflections
shimmer gently. The thin branches of the dead trees sway very slightly. The far hills and the sky stay unchanged. The camera
remains completely still. One continuous shot, slow steady motion, no cuts.
```

«Что не названо — не движется» [V:OA4xB5EY02g 32:46]: перечислить движение каждого элемента фона; сцену не пересказывать (D2-07).
[поправка фазы 5, 25.09.2026: этот промт — дословно I-03: шов 1,28, живость 0,83 (n = 1); форма промта (JSON против прозы, D2-11)
живость и удержание кадра не меняет; пересказ сцены (D2-07) движение не снизил (1,69 против 1,61) — «только движение» оставлен
ради краткости → `99-raw/phase5/runs/3-prompt-form/README.md`]

### 2.3 Приёмка выхода и доводка

```bash
# video_loop_check.py 0.2.1 · ffmpeg 7.1.5 — [проверено: I/02; команды мезонина — M/03; trim без потерь — X2]
T=../../scripts/ai-media/video_loop_check.py
python3 $T loop out.mp4 --control control_i2v.mp4 > out.loop.json     # живость motion_vs_control ≥ 0,5, cut_ratio < 10
python3 $T trim out.mp4 loop_mezz.mp4 --auto                           # [A,A]: срез дубля последнего кадра, -r исходника, x264 -qp 0
python3 $T loop loop_mezz.mp4                                          # seam_ratio_local ≤ 1,5 — только здесь, до кодека
# до 24.09.2026 trim писал CRF 10 (ложный шов 0,96 → 2,12) и нужен был отдельный -qp 0; с 0.2.1 loop_mezz.mp4 уже без потерь (X2)
```

- Провалы и лечение (I `09/01` §2–§3): разрыв — кроссфейд хвоста 12 кадров (`blend … +0.5`); статичный коллапс — видно
  только к контролю; ползущая камера — не лечится маской, только `fixed_lens`; длинный мёртвый хвост — брак, перегенерация.
  [поправка фазы 5, 25.09.2026: было — «разрыв — кроссфейд хвоста»; фаза 5: на крупной форме кроссфейд 12–24 кадров даёт шов
  1,46–1,76, но «фантом» — двоение формы (голос заказчика) → разрыв лечить **RIFE-мостом 8 кадров** от последнего кадра к первому
  (`../../scripts/ai-media/loop_rife_bridge.py`: 0,69–0,84 без двоения) или пинг-понгом (0,66–0,74); кроссфейд — только для
  мелкой ряби → `99-raw/phase5/runs/MS-marea/loops/MS-03-nacre-loop-4s.report.json`]
- Выход модели на сайт как есть не годится: звук, `moov` в конце (H3), 1928×1072 (Kling → `crop=1920:1072`), HEVC 10 бит
  (Seedance 2.5) → нормализация I `09/03` §6. [поправка фазы 5, 25.09.2026: Kling 3 через polza отдал 1280×720 (std) и 1920×1080 (pro); выходы
  Seedance, Kling, Omni — без тегов цвета (Kling и Omni ближе к BT.601), звук у Grok и Omni — всегда → `04-capability-map.md` §2.3]

### 2.4 Кодирование и постер

```bash
# ffmpeg 7.1.5 · SVT-AV1 · x264 — [проверено: J/05 finalize_video; M/03 encode.py]
TAGS=setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv
ffmpeg -i loop_mezz.mp4 -map 0:v:0 -an -threads 4 -vf "$TAGS,format=yuv420p10le" -c:v libsvtav1 -preset 6 -crf 28 \
       -map_metadata 0 -movflags use_metadata_tags+faststart hero.av1.mp4
ffmpeg -i loop_mezz.mp4 -map 0:v:0 -an -threads 4 -vf "$TAGS,format=yuv420p" -c:v libx264 -preset slow -crf 20 \
       -map_metadata 0 -movflags use_metadata_tags+faststart hero.h264.mp4
ffmpeg -i hero.av1.mp4 -frames:v 1 poster.png && 99-raw/tools/avif_pick.sh poster.png hero-poster.avif 80
```

- CRF — по `motion_keep` ≥ 0,75 (J/05: тихая петля AV1 24–28, H.264 18–20; стартовые 36–42 у I «замораживают» рябь до 0,24–0,5).
- Постер — кадр 0 **финального** AV1, PNG ffmpeg → кодер картинок; не `ffmpeg … poster.jpg` (ΔE00 6,7–7,4, J/02c) и не
  фиксированный `quality` (наш Pillow q50 — s2 79,5 < 80).
- Проверка: `asset_audit.py audit hero.av1.mp4 --mode video-loop --stage web --master loop_mezz.mp4` → `motion_keep`, веса.

### 2.5 Доставка

Шаблон J 00 / 02: `<video muted loop playsinline preload="none" data-video>` с `<source data-src … data-media … type=
'video/mp4; codecs="av01.0.08M.10"'>` → H.264 `avc1.6400xx` (уровень из ffprobe: у демо 1536×864 — 40 → `avc1.640028`);
`hero-video.js` подставляет источники после `load` и простоя, по `requestVideoFrameCallback` показывает видео без мигания,
reduce/Save-Data/2G → 0 байт, пауза вне экрана, кнопка 44 px с `aria-pressed`. Бюджет: петля 1080p ≤ 1,5 МБ, телефон 720p
≤ 600 КБ (A); телефону видео не давать вовсе, если движение декоративно (демо: 50,9 КБ первого экрана).

## 3. Hero с парящим объектом (`VID-ALPHA`)

### 3.1 Когда

Объект (не товар с надписью) «парит» над подложкой: зёрна, листья, 3D-метафора. Товар с этикеткой — не через i2v (I-13 меряет,
как плывёт надпись): берите настоящий вырез и 2.5D-параллакс CSS (страница J 07) `[практика I; не проверено: I-13]`.

### 3.2 Цепочка

1. Кадр объекта на ровном ключе: генерацией (объект вымышленный — M-07a, Sunburst 1K, 4 ₽) или правкой «Change only the
   background to a flat, uniform chroma-key …» от кадра сцены (H-07 v3); подложка — удалением объекта по маске +≈ 9 % стороны
   и растушёвкой ≈ 3 % (H/03 «призрак») [V:BVMuRw8BgJg 00:33].
2. Цвет ключа по объекту (I/03): золото, бронза, жёлтое, зелёное → `#FF00FF`; красное, розовое, фиолетовое → `#00B140`;
   пурпурный прощает ошибку `similarity` (съедено 0,5 % золота против 71 % на зелёном).
3. i2v с `fixed_lens`, [B, B] для петли: «The beans turn slowly… No zoom. No spin. Do not reposition the subject. Do not move
   the camera.» (M-07b, 5,25 ₽; форма запретов — D2-08).
4. Приёмка ключа: `video_loop_check.py chroma out.mp4 --key auto` → ≥ 95 % фона в ΔE00 ≤ 5 во всех кадрах, дрейф центра
   ≤ 2 % ширины; кеинг `chromakey` (similarity 0,10–0,15, blend 0,08) + despill `geq` G ≤ max(R, B); `alpha_check.py halo`.
5. Альфа-видео: stacked (цвет сверху, альфа снизу) AV1 → WebGL2 (`stacked-alpha.js`), запас HEVC/H.264; движение ≤ 5 с, затем
   стоп на кадре 0 (WCAG 2.2.2 без кнопки), повтор по наведению/фокусу; параллакс подложки ≈ 40 % `animation-timeline: scroll()`.

### 3.3 Команды (I/03, J/05 make_alpha)

```bash
# ffmpeg 7.1.5 — stacked alpha из кадров с альфой · [проверено: I/03; J/05 — AV1 12,5 КБ за 2 с 160×272]
ffmpeg -framerate 24 -i keyed_%04d.png -filter_complex \
  "[0:v]format=pix_fmts=yuva444p[main];[main]split[main][alpha];[alpha]alphaextract[alpha];[main][alpha]vstack" \
  -pix_fmt yuv420p -c:v libsvtav1 -preset 8 -crf 40 -movflags +faststart -an obj_stacked_av1.mp4
```

### 3.4 Числа и доставка

Stacked AV1 12,5 КБ, HEVC 15,7, H.264 21,5, VP9-alpha 19,8 (Safari её не показывает); статичный AVIF с альфой 2,0–2,6 КБ при
любом `--qalpha` (J/05). Если фон секции однотонный — альфа не нужна: объект на цвете секции (обычное видео, 12 КБ, I/03) —
тот же принцип, что у 3D-иконок демо (`02` §4). Шаблон — `../10-web-integration/pages/03-alpha-object-hero.html`.

## 4. Синемаграф (`VID-CINEMAGRAPH`)

### 4.1 Цепочка (проверено на демо: процедурный пар вместо генерации)

Мастер 2K (M-01) → i2v 720p [H, H] + `fixed_lens` с одним очагом движения (M-03, 10,5 ₽) → маска зоны движения →
`maskedmerge`: неподвижное из мастера, движение из видео → петля по стыку → мезонин без потерь → CRF по движению в маске →
финалы → постер из кадра 0 → видео-слой J (только ≥ 700 px).
[поправка фазы 5, 25.09.2026: M-03 и живой синемаграф (MS-02 motion) отменены заказчиком — генерация синемаграфа остаётся
`[не проверено]`; маска по слову (SAM 3.1, Gen-API) — тоже не запускалась → `04-capability-map.md` §2.3]

### 4.2 Промт (компилятор, prose)

```text
// bytedance/seedance-1.5-pro · polza 2026-09-24 · [M-01, M-01] · fixed_lens "true" · 720p 4 с · звук false · [не проверено: M-03]
Locked camera. The camera remains still. The steam above the coffee rises in thin wisps, curls slowly and fades above the cup.
The cup, the table, the napkin, the window light and the plaster wall stay perfectly still. All movement is slow and gentle.
Do not move the camera. No zoom. Do not add new objects. One continuous shot, same set and geometry, no cuts. The camera
must start and end on the exact same frame to create a perfect loop. No text.
```

### 4.3 Склейка с мастером

```bash
# ffmpeg 7.1.5 · синемаграф: [0] видео 720p, [1] мастер 2K, [2] маска движения (белое — из видео, растушёвка 1–2 px)
# [проверено: M/03 — 720p (CRF 18) + мастер 1536 + маска: 120 кадров за 1,5 с, drift неподвижного 0,0 (ровно мастер);
#  seam_local 2,48 — пульс уже в 720p-исходнике → шов и кроссфейд зоны движения делать ДО склейки; схема — I/02 cinemagraph_mask.py]
ffmpeg -i steam_720p.mp4 -loop 1 -i master_1536.png -loop 1 -i motion_mask.png -filter_complex \
 "[0:v]scale=1536:864:flags=lanczos,format=yuv444p[v];[1:v]format=yuv444p[s];[2:v]format=gray[m];[s][v][m]maskedmerge,format=yuv420p[out]" \
 -map "[out]" -frames:v 96 -r 24 -an -c:v libx264 -qp 0 cinemagraph_mezz.mp4
```

Граница маски — по естественным краям (край чашки, стена), иначе заметен «шов» живого и замёрзшего (I `09/02` §3).
Экспозиция модели плывёт по ходу ролика (ΔE00 до 0,5 за 6 с) — для длинных роликов подгонять цвет зоны движения к мастеру
(`video_loop_check.py colormatch`).

### 4.4 Числа демо (M/03, 120 кадров 1536×864, 24 fps)

| Что | Мезонин `-qp 0` | AV1 CRF 36 (финал) | AV1 CRF 40 | H.264 CRF 23 (финал) |
|---|---|---|---|---|
| вес за 5 с | 1,43 МБ | **18,2 КБ** | 18,5 КБ¹ | **91,7 КБ** |
| `seam_ratio_local` | 1,04 | 4,62 (пульс) | — | 3,33 (пульс) |
| движение в маске пара (`keep_in`) | 1 | 0,84 | 0,71 | 0,975 |
| мерцание вне маски, уровни 0–255 | 0,0 | 0,006 | 0,014 | 0,0003 |
| `drift` неподвижных зон | 0,0 | — | — | — |

¹ CRF 40 — из прогона подбора (`results_masked_motion.json`, SVT-AV1 `-preset 8`), где CRF 36 весит 20,3 КБ (CRF 40 — −9 %);
финал CRF 36 закодирован `-preset 6` — 18,2 КБ (`results_steam.json`) `[поправка X2 24.09.2026: сверено с M/03 encode.py]`.

`motion_keep` целого кадра (J) у синемаграфа вводит в заблуждение: AV1 CRF 24 даёт 2,35, CRF 36 — 1,12 (кодек добавляет шум в
неподвижные 93 % кадра, медиана разниц — это шум) → считать `keep_in` в маске (`99-raw/experiments/M/03-cinemagraph/masked_motion.py`)
и мерцание вне её отдельно; предложение для `asset_audit --mode video-loop --mask` → раздел «Для K» заметок M `[проверено: M/03]`.

### 4.5 Доставка и приёмка

Демо: видео-слой только `data-media="(min-width: 700px)"`, телефон — статичный 4:5; постер 1536 AVIF 3,4 КБ (`avif_pick.sh 80`).
`page_accept`: десктоп PASS, первый экран 84,8 КБ (видео 18,5), LCP = VIDEO 204 мс, пауза есть, при reduce 0 КБ видео;
F83 по 4 кадрам: 12,32 / 9,26 / 6,88 `[проверено: демо]`.

## 5. Hero с двумя состояниями и прожектором

### 5.1 Цепочка

Мастер состояния 1 (M-01) → состояние 2 **правкой от того же мастера** (свет, время суток, цвет — одно изменение, `edit.changes[].op`,
цель числом «2700 K»; M-06, 7 ₽) → `edit_check.py check M-01 M-06` (без маски, правка света: `edges_iou` ≥ 0,9, чашка на месте) →
статикой или своей петлёй → страница J 04: нижний слой — состояние 1 (постер + петля), верхний — состояние 2 под
`mask-image: radial-gradient(circle var(--r) at var(--x) var(--y), #000 35%, transparent)`; `@property --r` + `transition` —
угасание; `(hover: none)` → кнопка «Показать вечер» с `aria-pressed`; видео верхнего слоя — только при первом взаимодействии
(без наведения 0 байт) [V:SLnGJ9iezYo] `[проверено: J/08; не проверено: M-06]`.

### 5.2 Промт правки (компилятор, prose; диалект правки всегда проза)

```text
// openai/gpt-image-2.5-sunburst · polza 2026-09-24 · 2K 16:9 · images: [M-01] · [не проверено: M-06]
Relight the scene: late-evening light: the window turns deep dusk blue and a small warm table lamp off-frame on the left
lights the cup and the wall (2700 K lamp light). After the change, the frame
shows the same table at dusk, lit by a warm lamp from the left, the wall still empty for the headline. Keep the cup, napkin
and table exactly as they are, camera angle and crop and empty plaster wall on the left 45 percent of the frame unchanged.
Keep all other aspects of the image unchanged. Maintain the original composition and subject. No text.
```

Компилятор v2.1 ставил «Keep its position and size exactly the same» и к правке света, а артикль в `keep` удваивал («Keep the the
cup») `[проверено: M, 24.09.2026]`; v2.1.1 — фраза только после замены объекта, артикль не удваивается (задание M-06 пересобрано,
592 → 547 символов) `[поправка X2 24.09.2026]`.

### 5.3 Проверка контраста обоих состояний

`page_accept.py page.html --click "[data-state-toggle]" --contrast ".hero h1" …` — оба состояния, десктоп и Pixel 7; у J после
исправлений F83 ≥ 5,1 в обоих; скрим состояния 2 свой (светлый/тёмный по зоне) `[проверено: J/06]`.

## 6. Абстрактный фон (`IMG-BG-ABSTRACT`, `VID-ABSTRACT`)

| Ступень | Когда | Вес | Цена | Ловушка |
|---|---|---|---|---|
| CSS-градиент / `radial-gradient` | цветовые поля, свечение, CTA | 0 байт | 0 | тёмные градиенты — только CSS: Chromium дизерит CSS (ступень 0,04), AVIF 8 бит 0,55, AVIF/AV1 10 бит 0,35–0,39 (J/03) |
| SVG / паттерн кодом | геометрия, линии, точки | 133–177 Б плитка | 0 | штрих через край плитки продлевать на период (G/04) |
| шейдер WebGL | живая бренд-абстракция (Stripe, Vercel) | JS 6–25 КБ + рантайм | 0 | canvas не бывает LCP; пауза и reduce как у видео |
| картинка | «материальная» абстракция: бумага, стекло, ткань, свет в объёме | AVIF 3–6 КБ на 1 Мп (гладкое) | FLUX.2 [pro] 1K 5 ₽ (hex документирован, промт переписывается); Flare 1K 4 ₽; 8:1 и 4:1 — только NB2 Lite 2,9 ₽ | порядок цветов модели не держат (0 из 29, GenAI Showdown) → бренд-цвет — ΔE-проверкой и CSS-слоем; пурпур 270–320° вне бренда — брак (IMG-M05) |
| видео | движение, которого не сделать кодом | 150–600 КБ | Seedance 2 Mini 480p 5 с 12,8 ₽; Grok 1.5 480p 8,1 ₽ | всё правило петли (§2) + пауза |

Проверка картинки: `asset_audit.py audit bg.png --dna …` (палитра паспорта ≥ 3 из 5 в ΔE OKLab ≤ 0,05; `purple_share`);
зерно — CSS поверх (SVG `feTurbulence` 280 Б), дизеринг до кодека съедается (H/05b) `[проверено: H/05b, J/03]`.
[поправка фазы 5, 25.09.2026: тёмный фон с переливом — Sunburst 2K (7 ₽), Flare 1K (4 ₽), NB2 1K (4,8 ₽) по одному промту
«материал, перелив только по краям, ≤ 20 % кадра»; AVIF при SSIMULACRA2 ≥ 80 — 91 / 40 / 20 КБ (зерно Sunburst дорого);
видео-абстракция: Seedance 1.5 Pro [A,A] + RIFE (§2), трансформация формы — Grok 1.5 720p 12,15 ₽; Seedance 2 Mini — референсы,
петлю не строит (I-08) → `99-raw/experiments/B/12-demo-assets/README.md`, `04-capability-map.md` §2.1, §2.3]

## Частые ошибки

- Один hero 16:9 «на все экраны» и обрезка под телефон — объект или зона текста уходят за край (F/03: 45 % ширины в 4:5).
- Просить у Sunburst `aspect_ratio: "4:5"` — такого значения в каталоге polza нет; компилятор с `--model` поймает, «память» — нет.
- Выход модели на страницу как есть: PNG 1–2,5 МБ, без лестницы и `<picture>` (A: Midjourney на своей главной).
- Мерить шов петли на H.264/AV1 финале (пульс ключевого кадра даёт 3,3–4,6) вместо мезонина без потерь.
- `motion_keep` целого кадра для синемаграфа — завышен шумом кодека (2,35 при CRF 24) → движение в маске.
- `trim …,setpts` без `-r` в MP4 — теряется последний кадр (ffmpeg 7.1.5, edit list).
- Постер `ffmpeg -i video … poster.jpg` или фиксированный `quality` Pillow — скачок цвета (6,7–7,4 ΔE00) или s2 < 80.
- `-colorspace bt709` вместо полных тегов `setparams` — ffmpeg 7.1 пишет только матрицу, ошибка 7,2–7,4 ΔE00 (J/02b).
- Два `-movflags` отдельными флагами — второй перетирает первый, `moov` уходит в конец, `AIGC` теряется (L/02).
- `loading="lazy"` на LCP-картинке, hero `100vh` (весь вьюпорт — не LCP), появление hero из `opacity: 0` (J/01).
- Экран-заставка «пока грузятся видео» — LCP уезжает к её концу (J 04).
- Парящий товар с надписью через i2v — этикетка «плывёт»; товар — только настоящим вырезом.
- Ключ `#00B140` для золотого/бронзового объекта — съедение 71 % при ошибке `similarity` (I/03).
- **Ошибки агентов**: `angle` солнца Blender в градусах (`size=1.2` → 69°, «туман» вместо тени — M/02); `focal_point` списком;
  `1.91:1` в `ratio`; обёртка `asset_audit.py`/`page_accept.py` во второй `flock` (до 24.09.2026 — самоблокировка); фоновый
  `http.server` в `&&`-цепочке (переменные не доходят до родителя, сервер остаётся жить — у нас дважды).

## Чек-лист

- [ ] Паспорт `validate` — `ok: true`; спецификация собрана `to-spec`, промт прочитан глазами после `compile`?
- [ ] Два мастера hero (16:9 и 4:5/3:4 → 4:5), у каждого своя зона текста и `focal_point {x, y}`?
- [ ] Задание фазы 5: ценовые параметры явно, `provider` c `allow_fallbacks: false`, `polza.py estimate` — 0 ошибок?
- [ ] `asset_audit` мастера без `fail`; `needs_human` просмотрен глазами на панели?
- [ ] Петля: шов на мезонине без потерь ≤ 1,5, живость к контролю ≥ 0,5, срез дубля сделан; синемаграф — движение в маске?
- [ ] Видео: полные теги BT.709, `-an`, флаги провенанса одной строкой, CRF по сохранению движения, постер из кадра 0 через `avif_pick.sh`?
- [ ] `provenance_check.py scan` мастера до правок и `stamp` на каждой производной?
- [ ] Шаблон J: `<picture><source media width height>`, `fetchpriority="high"`, видео-слой `data-src`, кнопка паузы?
- [ ] `page_accept.py` PASS на десктопе и Pixel 7 (+ троттлинг), F83 по кадрам ≥ 4,5 мелкого текста?

## Открытые вопросы и противоречия

1. Держит ли GPT Image 2.5 раскладку референса при переходе 1K → 2K (M-01, E-16) — если нет, финал hero = лучший из N в 2K
   сразу (7 ₽ × N) или Lanczos 1K → 2K (мягче; сравнить вслепую).
2. Резок ли пар 720p после `maskedmerge` на 1440 CSS-px (M-03; резерв M-05 1080p +12 ₽).
3. Порог `keep_in` 0,75 для синемаграфа взят по аналогии с J; калибровать голосами заказчика (K-08 — «видимость пульса»).
4. Видео-слой как LCP (когда постер ниже порога энтропии): поле (CrUX) может вести себя иначе, чем лаборатория (J-05).
5. ~~`prompt_compile.py ratios`: ложный «аутпейнт» 16:9 → 40:21, вариант 4:5 `generate` не выводится~~ — закрыто v2.1.1
   `[поправка X2 24.09.2026]`: причина — без `safe_zones` весь кадр считался неприкосновенным; теперь кроп по зоне текста и фокусу
   (не влезает — по фокусу с пометкой «в кадре N % зоны текста»), 40:21 — кроп −6,7 % высоты, варианты `output.variants` выводятся.
6. Видимость пульса ключевого кадра H.264 на тихом синемаграфе глазом — не проверена (K-08).

## Источники

Внутренние (прочитаны целиком или нужными разделами; первоисточники внешних фактов — в них):
- [S1] A `../01-web-assets-landscape/01-asset-slots-by-page-type.md` §2, §4, §6–§8 — слоты, бюджеты, YAML-план (волна 1).
- [S2] F `../06-art-direction-consistency/01-visual-dna-from-ui.md`, `03-composition-for-web.md` — паспорт, R1–R8, F83, арифметика кадра.
- [S3] D2 `../05-prompting/04-video-prompting.md`, `05-edit-reference-series.md`, `asset-spec.schema.json` v0.2, `dialects.yaml` v0.3.
- [S4] H `../08-image-post-processing/01…04` — вырез, правка и композит, тайлинг, бандинг, кодирование, C2PA.
- [S5] I `../09-video-pipeline/01…04` — петли, синемаграф, альфа, кодирование, протоколы i2v.
- [S6] J `../10-web-integration/01…04` и `pages/` (00, 03, 04, 07, 08) — доставка, LCP, постер, пауза, прожектор, `page_accept.py`.
- [S7] K `../11-evaluation-qa/01`, `03`, `thresholds.yaml` — `asset_audit.py`, пороги, ручная приёмка.
- [S8] L `../12-legal-provenance/02` §5, §7; `04` §2–§5 — провенанс производных, видимая метка, ворота.
- [S9] E `../13-routing-matrix/routing.v0.yaml` — маршруты по кодам задач (v1 — агент N, волна 3).
- [S10] B2 `../02-providers-platforms/07-multichannel-client.md` — каналы вне polza (`mp_client.py`).
- [S11] `99-raw/phase5/{E,F,H,I,D2,J,K,L,M}-plan.md` и задания — тесты, выходы которых берёт демо.
- [S12] Каталог polza `99-raw/cache/polza/2026-09-24/` через `polza.py show` — параметры Sunburst и Seedance 1.5 Pro.
- Дайджесты роликов (через файлы I, J, D2): [V:SLnGJ9iezYo] (hero с двумя состояниями, петля), [V:FvzFXrzgioc] (постобработка
  петли), [V:BVMuRw8BgJg] (парящий объект), [V:_Bc4g6fFMp0] (ключ по объекту), [V:OA4xB5EY02g] (фоновое движение).
- Прочитан целиком: дайджест [V:I9xdmNZxIfA] (Figma Weave, Config 2026: «машина бренда» — §0.4); конвейер Klarna — отчёт A
  волны 1 §4 и A `01/03` [S21].
- Опыты M: `99-raw/experiments/M/01-icon3d-forms`, `02-hero-pair`, `03-cinemagraph`, `09-demo-acceptance`; демо —
  `14-recipes/examples/demo-landing/` (README с замерами).
