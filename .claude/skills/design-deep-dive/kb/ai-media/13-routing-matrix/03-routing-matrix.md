# Матрица маршрутизации: задача → модель → параметры → цена → запас → чем проверять

Волна 3 · агент N · 24.09.2026 · машиночитаемая часть — `routing.yaml` v1 (33 маршрута: 32 кода таксономии + предложение
`IMG-LAYERS`; 124 варианта; `../../scripts/ai-media/routing_check.py` — 0 ошибок) · снимки каталогов: polza `2026-09-24` 04:10,
RouterAI и Gen-API `2026-09-24_0424` · доказательства — `02-existing-evidence.md` (классы A/B/C, J1–J26) · прочитано
целиком ≈ 40 файлов базы и отчётов, 3 опыта (`99-raw/experiments/N/01–03`).
**v2 — агент U, сессия 5, 25.09.2026**: итоги фазы 5 вписаны в `routing.yaml` v2 (33 маршрута, 136 вариантов, `routing_check.py`
1.1 — 0 ошибок, 0 предупреждений, снимки `2026-09-25_1411`); что изменилось и почему — §2.2, итог ворот — §8; таблицы §2–§4 ниже —
состояние v1 с точечными поправками фазы 5; при расхождении прав `routing.yaml` v2. История — `routing.v1.yaml`.

## Выжимка для агента

1. **Маршрут берётся из `routing.yaml`, а не из памяти**: id модели, провайдер, ценовые параметры и цена — оттуда; после
   нового снимка каталога — `routing_check.py` (0 ошибок) до первого вызова. → §1, `04-update-procedure.md` [проверено]
2. **Сначала код, потом модель**: градиент, паттерн, текст, схема, линейная иконка, бренд-палитра — CSS/SVG/HTML (0 ₽);
   модель — только атмосфера, свет, материал, сцена. → §7 [консенсус]
3. **Фото-hero — `openai/gpt-image-2.5-sunburst` 2K 16:9 за 7 ₽** (Flare — та же цена, решает E-08); запас — NB2 2K 7,2 ₽;
   люди и руки — только GPT 2.x. → §2 [исследование; для polza — не проверено] [поправка фазы 5, 25.09.2026: E-08 — «хорошо»
   Sunburst, Flare, NB2 (голос заказчика вслепую, 1 чел.) → основной без изменений, Flare и NB2 — равные запасные; id Flare —
   `openai/gpt-image-2.5-flare` → §2.2]
4. **Не брать Seedream 5 Pro и NB Pro для фото**: Rapidata Photorealism #33 и #12 — против LMArena; NB Pro — только серии и
   роли референсов (13,5 ₽; flex 7,95 после T5). → §2 [исследование, спорно] [поправка фазы 5, 25.09.2026: было «NB Pro — серии»;
   фаза 5: E-08 — NB Pro «слишком ровно», Seedream 5 Pro «минус»; E-12 — NB Pro и в серии не держит стиль эталона → оба в `not` → §2.2]
5. **Товар — только настоящий, композитом**: сцена — Sunburst, товар — вырез с фото + `edit_check --protect` (SSIM ≥ 0,9,
   ΔE00 ≤ 5); модели сохраняют товар без дефектов лишь в 53–75 %. → §2 [исследование: Pinterest]
6. **Правка делится по типу**: «не трогать остальное» (фон, удаление, вставка, цвет, градиент, убрать текст) — NB2 1K 4,8 ₽;
   сложная инструкция, геометрия, обрезка — Sunburst + композит; точные пиксели (hex, сдвиг на N px) — не моделью. → §2
   [исследование: GDB, PaintBench] [поправка фазы 5, 25.09.2026: E-15 — «не трогать остальное» не держит ни одна модель (утечки и
   сдвиги у 3 из 4) → композит обязателен; удаление — Seedream 5 Pro PASS (1 образец); D2-06 — 10 правок одним вызовом NB2 → §2.2]
7. **Аутпейнт баннера — NB2** (элементы 1,0 против 0,23 у GPT); проверка тремя критериями `edit_check.py outpaint`. → §2
   [исследование] [поправка фазы 5, 25.09.2026: H-08 — у NB2 и Sunburst центр перерисован (резкость 0,56 / 0,14 < 0,85) → композит
   всегда; телефону — свой мастер по референсу]
8. **Латиница: вёрстка и логотип — GPT Image 2 (`openai/gpt-5.4-image-2`), дословность — Seedream 4.5** (три независимые
   линии); интерфейсный текст — HTML всегда. → §2 [исследование]
9. **Кириллица — HTML-слоем до E-02…E-04**; модель разрешается только для ≤ 4 слов крупно, если лидер дал 3 из 3 дословно,
   с OCR и вычиткой человеком (OCR не видит латинских «близнецов»). → §2 [не проверено] [поправка фазы 5, 25.09.2026: E-02 — 6 из 9
   моделей пишут короткий баннер дословно (1 образец; ошибаются Qwen 2.1 и FLUX.2 Pro), Recraft V4.1 — 3 из 3 глазом; K-05 — OCR
   15/24, VLM 11/24 → HTML основной, надпись ≤ 4 слов моделью — с OCR и чтением человеком → §2.2]
10. **Бренд-цвет — не hex-промтом**: hex попадает ≈ в половине случаев у GPT и FLUX.2; палитра — грейдом `.cube` и ΔE к
    паспорту, раскладка цветов — кодом. → §2 [исследование: GenColorBench, GDB]
11. **Прозрачность в финал — не Qwen 2.1** (исследовательская лицензия): ровный фон + локальный вырез по типу объекта или
    GPT Image 2.5 `background: transparent` через RouterAI (1,45 ₽). → §2 [документация; проверено: H/01] [поправка фазы 5,
    25.09.2026: T2 — у Qwen 2.1 альфа настоящая (64 % прозрачных), лицензия прежняя; H-03 — у RouterAI GPT 2.5 мех годен, стекло —
    нет (облако фона с блочной маской 16 px, серый ореол на тёмном); Riverflow `transparent` — пусто ×2]
12. **Бесшовности у моделей нет**: генерация + `tile_check.py cut` (шов ≤ 1,3); геометрия — SVG/CSS. → §2 [документация]
13. **Апскейл фото — не Real-ESRGAN**: генерировать в целевой ступени 2K/4K; Lanczos по умолчанию; Topaz — после H-05. → §2
    [проверено] [фаза 5, 25.09.2026: E-01 — 4K у Sunburst настоящий (3840×2160, 11 ₽), «4K» Seedream 4 через mie — 2352×1008;
    H-05 не прогонялся]
14. **Черновик — NB2 Lite 2,9 ₽; Z-Image 1,4 ₽ — только композиция без текста и цвета**; новые Grok Image 2.0 (3 ₽) и
    Recraft V4.1 Flash (0,77 ₽) — через мини-стенд. → §2 [исследование] [поправка фазы 5, 25.09.2026: CM-09 — Flash даёт синий
    сдвиг (1 образец); мини-стенды E-16, N-03 не прогонялись]
15. **Тихая петля — `bytedance/seedance-1.5-pro` [A, A] + `fixed_lens` 720p 4 с за 10,5 ₽** (черновик 480p — 5,25);
    премиум — GA Omni 1.1 Flash 1080p 48 ₽ (кадры полями `*_frame_url`) и Kling 3 std 50 ₽. → §3 [не проверено] [поправка фазы 5,
    25.09.2026: I-03 — шов 1,28, живость 0,83 (проходит); премиум хуже по шву — Kling 3 std 2,12, GA Omni 5,08, Kling 3 pro 1080p —
    почти стоп-кадр → премиумов петли нет; 1080p — тот же Seedance (8 с 45 ₽); крупная форма — RIFE-мост на стыке → §2.2, §3]
16. **Seedance 2.x петлю не строит**: `images` — «референсы», не кадры (проверяет I-08). → §3 [документация] [фаза 5, 25.09.2026:
    подтверждено — I-08 SSIM кадра 0 к A 0,60, шов 7,21; с фразой «Use @Image1 as the first frame.» Seedance 2 Fast кадр держит (0,85)]
17. **Приёмка петли — шов И живость**: `seam_ratio_local` ≤ 1,5 на мезонине без потерь после `trim`, `motion_vs_control`
    ≥ 0,5; VLM видео не судит. → §3 [проверено]
18. **Звук — параметром там, где он есть** (`generate_audio`/`sound` = `"false"`); у Veo, Omni, Wan 2.5/2.6, Grok, H3 — `-an`
    при кодировании. → §5 [документация]
19. **Альфа-видео — хромакей с неподвижной камерой → кеинг → stacked alpha**; пурпурный ключ для зелёных и золотых объектов;
    нативной альфы нет ни у одной видео-модели. → §3 [практика; проверено: I/03] [фаза 5, 25.09.2026: D2-08 — у Grok 1.5 запреты
    движения снижают дрейф на 58 %, Seedance на ключе наезжает (×1,8–2,1 в 3 из 4); живой ключ (I-06) не прогонялся]
20. **Видео по рейтингу не выбирать**: лидеры арен (Omni, Wan 3.0, H3, Seedance 2.x) — маршрут по возможностям polza (FLF,
    `fixed_lens`, цена); Wan 3.0 петлю не строит. → §3 [консенсус] [фаза 5, 25.09.2026: H3 Max (2 × 503), Wan 3.0 (503) и Topaz видео
    (2 × INTERNAL_ERROR) выбыли — `routing.yaml` `defaults.unavailable_2026_09_25`]
21. **Линейные иконки — набор (Lucide) или LLM → SVG** (Claude в сессии, 0 ₽; Recraft — только заливки). → §4 [исследование]
22. **Цветной SVG — RouterAI `recraft/recraft-v4.1-vector` 8,78 ₽** (24.09); палитра словами, пока B2-01/G-07 не доказали
    `controls`; запас — Gen-API `recraft-v4` vector 20 ₽. → §4 [документация] [поправка фазы 5, 25.09.2026: наборы иконок — Recraft
    V4.1 Pro Vector 33,11 ₽ (CM-01: 8 из 8, путей −44 %), Vector 8,83 ₽ — черновики и фоны; `controls` доходит (B2-01); палитра словами —
    только тон → точная — перекраской SVG → §2.2]
23. **У каждого маршрута три сквозных поля**: `check` (режим `asset_audit` + рубрика K), `delivery` (AVIF/WebP/JXL; AV1 10 бит +
    H.264; stacked alpha; svgo), `legal` (флаги `research`, `nc-weights`, `no-automation`, `visible-vendor-mark`,
    `vendor-mark-keep`, `people-consent`, `product-real-only`). → §5 [документация]
24. **Слот сначала фильтрует уместность ИИ**: отзывы, команда, логотипы, товар «как есть» — не генерировать вовсе. → §6
    [документация: L 04 §2, A 01 §2.1]
25. **Задачи нет в таблице — алгоритм §7**: разложить на коды → код раньше модели → возможности канала → класс
    доказательств → самый дешёвый в интервале лидера → проверка тем же `check`. → §7 [практика]
26. **Модели в интервале лидера равны — берётся дешевле**; «лучшая» по одному голосованию 60/40 не доказывается. → §1
    [исследование: `01-stand-method.md` §4.4]
27. **Ценовые параметры и `provider` — всегда явно**: запасная ступень = максимум (Kling `mode` не из списка → 225 ₽ вместо
    60 — поймано валидатором). → §1 [проверено]
28. **`[не проверено]` меняется на `[стенд: N задач × моделей × повторов, судья, дата]`** только по правилу
    `01-stand-method.md` §5 после фазы 5. → §8 [практика] [фаза 5, 25.09.2026: правило стенда не выполнено ни разу (1–2 образца
    на модель, голос одного заказчика) → живые прогоны помечены `[проверено: путь]` с n, `[стенд]` не поставлен → §2.2]

## 1. Как читать матрицу

- **Роли вариантов** (`options[].role` в `routing.yaml`): `primary` — по умолчанию; `alt` — равноценный кандидат (решает
  тест); `fallback` — при провале или отказе модерации; `cheap`/`draft` — перебор; `premium` — дорогой финал; `alpha`,
  `mask`, `scheme`, `ultrawide`, `regen`, `exact` — специальные случаи; `local`/`code`/`blender` — без модели (0 ₽).
- **`final: false`** — нельзя в опубликованный ассет (черновик, исследовательские веса, не проверено); **`gate`** — условие
  (тест фазы 5 или фазы 0); **`until`** — дата снятия модели.
- **Каналы**: `polza` (Media API, баланс 2 000 ₽), `polza-chat`, `polza-images` (тот же баланс), `routerai`, `genapi`
  (отдельные балансы, по умолчанию 0 ₽ в клиенте), `local`, `code`, `blender`, `external` (вне доступа: fal, Luma, Recraft
  напрямую, KIE, Midjourney). Провайдер polza — `mie`, кроме H3 Max (`openrouter`) и NB Pro flex (`google-vertex/global/flex`).
- **Цена** — ₽ за один результат по снимку 24.09.2026 (для видео — за ролик с указанной длительностью, звук выключен);
  совпадает с `polza_catalog.py price` (± 1 %) — проверено валидатором для всех 77 вариантов polza.
- **Метка** — как в PLAN.md; «в конфигурации polza — `[не проверено]`» означает: арены мерили настройки вендора (GPT Image
  2.5 — `quality: max`), а polza `quality` не выставляет.
- **Класс доказательств** (`02` §3): A — независимые голоса/метрика с методикой на моделях 09.2026; B — методика есть, но
  один судья, старые версии или малая выборка; C — анекдот.

## 2. Картинки (`IMG-*`)

Цены — polza `mie`, ₽ за картинку, 24.09.2026. «ворота E-01» — вариант допускается, только если E-01 не нашёл видимого знака Seedream через `mie`.

| Код | Основная (параметры, ₽) | Запас / альтернатива | Дёшево, черновик | Диалект | Постобработка | Чем проверять (`asset_audit` · рубрика) | Метка | Фаза 5 решит |
|---|---|---|---|---|---|---|---|---|
| `IMG-HERO-PHOTO` | `openai/gpt-image-2.5-sunburst` 2K 16:9 — 7 | `gpt-image-2-5-flare` 2K — 7 (alt); `google/gemini-3.1-flash-image-preview` 2K — 7,2; RouterAI Sunburst `quality: high` 16:9 (1536×864) — 3,62 (ворота N-01) [поправка фазы 5, 25.09.2026: N-01 — `medium` 0,93 ₽ ≈ `high` 3,57 ₽ (по паспортам; списываются только выходные токены × 0,0033113 ₽) ≈ polza 1K 4 ₽, n = 2 брифа → в v2 вариант `medium` 0,93 → `99-raw/phase5/runs/S5-analysis/N-01_metrics.json`] | `bytedance/seedream-4` 4K 21:9 — 3 (ворота E-01); NB2 Lite — 2,9 | gpt-image · sections | best-of-2; 2K не 4K; грейд `.cube`; скрим F83; кадр 4:5 телефону | `image --slot hero --text-zone --dna` · `hero-photo`; K-06 | [исследование]; polza — [не проверено] | E-08, E-09, E-01, F-04, D2-04, N-01 |
| `IMG-PRODUCT` | композит: вырез товара + сцена `openai/gpt-image-2.5-sunburst` 2K 4:3 — 7 | NB2 1K — 4,8 (правка «вокруг реального»: 74,6 % без дефектов) | `bytedance/seedream-4.5` basic — 5 (ворота E-01); Qwen 2.1 — 3 (черновик) | gpt-image · sections; 7 блоков продукта | композит, растушёвка 4 px, тень multiply, 2 кандидата | `edit --orig --mask --protect` · `product`; OCR этикетки | [исследование]; перенос — [не проверено] | E-10, H-07 |
| `IMG-ILLUSTR` | `gpt-image-2-5-flare` 1K 1:1 — 4 | Sunburst 1K — 4 (alt); NB2 1K — 4,8; схемы — `openai/gpt-5.4-image-2` 1K — 4 | Grok Image 2.0 — 3 (мини-стенд) | gpt-image · sections | проверка тёплого сдвига, грейд; подписи схем — кодом | `image --dna` · `illustration` | [исследование] | E-11, D2-01 |
| `IMG-SERIES` | метод F + `gpt-image-2-5-flare` 1K 3:2 + 3 референса — 4 | `google/gemini-3-pro-image-preview` 2K — 13,5 (flex 7,95 после T5); RouterAI `recraft/recraft-v4-styles` — 3,84 | `bytedance/seedream-4.5` — 5 (ворота E-01; не с несколькими людьми) | gpt-image · sections, `reference_group` | палитра к паспорту (ΔE OKLab ≤ 0,045, оттенок ≤ 10°) | `series --ref --grid 2x2` · `series` | [спорно] | E-12, F-01, F-02, F-06, G-11, G-12 |
| `IMG-ICON3D` | `openai/gpt-image-2.5-sunburst` 1K 1:1, сетка 2×2, форма-рендер + кубик материала — 4 | NB2 1K — 4,8; Blender — точный набор | Qwen 2.1 transparent — 3 (черновик) | gpt-image · sections | вырез: ровный фон → u2netp/isnet по краю | `cutout --grid 2x2 --series` · `icon3d` | [исследование]; набор — [не проверено] | E-14, F-07, G-17, G-18 |
| `IMG-CUTOUT` | ровный светлый фон → rembg `u2netp` (явно) + decontaminate — 0 | RouterAI GPT 2.5 `background: transparent` medium — 1,45; polza `/v2` — 4 (H-02); Gen-API Ideogram RB — 2,5, Pixelcut — 4 | Qwen 2.1 transparent — 3 (черновик) | gpt-image · sections | по типу объекта (мех — matting/ключ; стекло — ключ или нативная альфа); поле ≥ 2 %; тень слоем | `cutout` · `cutout` (ореол ≤ 2 px) | [проверено] локально; модели — [не проверено] | H-01…H-04, T2 |
| `IMG-BG-ABSTRACT` | код: CSS/SVG/шейдер 6–25 КБ — 0; атмосфера — `gpt-image-2-5-flare` 1K 16:9 — 4 | `black-forest-labs/flux.2-pro` 1K — 5 (hex не лучше GPT, pup не выключается) | Seedream 4 4K 21:9 — 3 (ворота E-01); лента 8:1 — NB2 Lite 2,9 | gpt-image · sections | палитра грейдом, не hex; зерно SVG/CSS; градиенты — CSS | `image --dna` · `bg-abstract` | [исследование]; бренд-цвет — [не проверено] | E-13, E-01, D2-04 |
| `IMG-TEXTURE` | `bytedance/seedream-4` 2K 1:1 seed 101 — 3 (ворота E-01) + `tile_check.py cut --overlap 96` | Flare 1K — 4; геометрия — SVG/CSS 130–180 байт | — | seedream · prose | сдвиг 50 % → шов ≤ 1,3 → cut96 или заделка маской | `texture` · `bg-abstract` | [документация] + [проверено] | H-09 |
| `IMG-TEXT-LATIN` | HTML/CSS-шаблон → Playwright — 0; декоративная надпись — `openai/gpt-5.4-image-2` 1K — 4 | `bytedance/seedream-4.5` — 5 (дословность, ворота E-01); Sunburst — 4 (текст в сцене) | — | gpt-image · sections, `Text (EXACT, verbatim)` | best-of-4 для постеров; OCR → откат на HTML | `og --expect` · `text-image` + вычитка | [исследование] | E-17, E-02 |
| `IMG-TEXT-CYR` | HTML/CSS поверх ИИ-фона — 0 | после E-02…E-04: лидер (Sunburst / GPT 2 / …) ≤ 4 слов крупно; RouterAI Recraft V4.1 — 3,84 (E-07, G-09) | — | gpt-image · sections; 3-я форма — блок типографики `product7` | OCR → NFC → двойники → кодовые точки | `og` + `ocr --expect` · `text-image` + вычитка | [не проверено] | E-02…E-07, G-09, K-05 |
| `IMG-EDIT` | «не трогать остальное» — NB2 1K — 4,8; сложная инструкция — Sunburst 1K + композит — 4 | «обвёл — убери» — Seedream 4.5 — 5 (ворота E-01); маска — RouterAI `openai/gpt-image-2` medium ≈ 6,47 | Qwen 2.1 + `mask_url` (белое = менять) — 3 (черновик) | nano-banana · sections; ≤ 5 изменений, целевые значения | `edit_check.py --match-color --composite`; удаление: маска + 9 %, растушёвка 3 % | `edit --orig [--mask] [--protect]` · `edit` | [исследование]; сохранность в polza — [спорно] | E-15, H-06, H-07, D2-06 |
| `IMG-OUTPAINT` | NB2 1K с целевым `aspect_ratio` — 4,8 (+ композит центра) | Sunburst 1K — 4 (2K — 7); точный кроп по фокусу — код | — | nano-banana · sections | `edit_check.py outpaint`: SSIM центра ≥ 0,9 И ΔE00 ≤ 3 И резкость ≥ 0,85 → иначе `--composite` | `edit` · `edit` | [исследование]; в polza — [не проверено] | H-08 |
| `IMG-MOCKUP` | композит скриншота (Blender / CSS 3D) — 0 | сцена и устройство — Sunburst 2K — 7 | — | gpt-image · sections | скриншот поверх, OCR до/после | `edit --protect` · `edit` | [исследование] + [документация] | не тестируется (S21) |
| `IMG-UPSCALE` | генерировать в целевой ступени (Sunburst 2K — 7); Lanczos — 0 | `topaz/image-upscale` ×2 — 7,5 (после H-05) | Seedream 4 4K перегенерацией — 3 (ворота E-01) | без промта | Real-ESRGAN — только графика; генеративная доводка — только декор | `image` (SSIMULACRA2 к мастеру) · `hero-photo` | [проверено] локально | H-05 |
| `IMG-DRAFT` | `google/gemini-3.1-flash-lite-image` — 2,9 | Grok Image 2.0 — 3; RouterAI Recraft V4.1 Flash — 0,77 (новые, мини-стенд) | `tongyi-mai/z-image` — 1,4 (композиция без текста и цвета) | nano-banana · sections | черновик → финал референсом «keep composition of image 1» | `image` (pHash разнообразия) | [исследование]; перенос — [не проверено] | E-16 |
| `IMG-LAYERS` (предложение H) | Gen-API `qwen-image-layered` 4 слоя — 12,5 | вырез по альфе + Depth Anything V2 Small 518² — 0; RouterAI Ming Image Design Layer (цена не указана) | — | без промта | сумма слоёв ≈ исходник (SSIM ≥ 0,95) | `cutout` · `cutout` | [не проверено] | H-10 |

### 2.1 Что изменилось относительно `routing.v0.yaml` (и почему)

| Код | v0 (E, 23.09) | v1 (N, 24.09) | Основание |
|---|---|---|---|
| `IMG-EDIT` | Sunburst primary, NB2 fallback | **по типу правки**: NB2 — «сохранить остальное», Sunburst — сложная инструкция + композит | GDB: вставка LPIPS 0,078 против 0,327, удаление текста PSNR 30,2 против 16,6 (J13); PaintBench: NB2 ≈ GPT 2, специализации разные (J16) |
| `IMG-OUTPAINT` | Flare 2K primary | **NB2** + композит центра | GDB адаптация 9:16 → 1:1: Recall 1,0 против 0,23 (J13) |
| `IMG-BG-ABSTRACT` | FLUX.2 Pro primary «ради hex» | **код**, затем Flare; FLUX.2 — alt | GenColorBench: hex ≈ 50 % у GPT и 43–49 % у FLUX.2 (J11); Design Arena Abstract FLUX.2 #31 (J5) |
| `IMG-TEXT-LATIN` | GPT 2 + Seedream 4.5 запасом | то же, **Seedream 4.5 — «дословность» с тремя линиями** | Rapidata Text Coherence #1, OCRGenBench Poster AR 83,9, WeGenBench Char F1 0,79 (J2, J8) |
| `IMG-PRODUCT` | Sunburst primary, NB2 fallback | **композит** primary; NB2 — правка «вокруг реального товара» | Pinterest: без дефектов товара 74,6 % (NB) против 52,9 % (GPT-1.5) (J14); текст упаковки искажают все (J15) |
| `IMG-CUTOUT`, `IMG-ICON3D` (альфа), `IMG-EDIT` (маска), `IMG-PRODUCT` (дёшево) | Qwen 2.1 primary / вариант | **Qwen 2.1 — только `final: false`, флаг `research`** | L 12/01 §5: Qwen Research License 20.09.2026 |
| `IMG-CUTOUT` | Qwen 2.1 → удаление фона | **маршрут по типу объекта** (H/01) + RouterAI GPT 2.5 transparent 1,45 ₽ | H/01 (эталонная альфа), Lucida (J9) |
| `IMG-UPSCALE` | Real-ESRGAN «консервативный» | **Lanczos по умолчанию**, Real-ESRGAN — только графика | H/02: хуже Lanczos на 15–103 пункта, выдумывает структуру |
| `IMG-SERIES` | Flare + эталон | + метод F постоянным фактором; RouterAI Recraft V4 Styles | F 06/02; F-06 |
| `IMG-DRAFT`, `IMG-ILLUSTR` | NB2 Lite, Z-Image | + Grok Image 2.0 (3 ₽, polza 23.09 17:45), Recraft V4.1 Flash (0,77 ₽, RouterAI 24.09) | новые модели → мини-стенд (`04` §4) |
| все | цены 23.09, диалект строкой | + `check`, `delivery`, `legal`, `inputs`, `final`, `gate`; цены 24.09 | K, J, L; RouterAI +0,39 % за ночь |

### 2.2 Что изменилось в v2 (фаза 5, 25.09.2026)

Живые прогоны 25.09.2026 (заходы 1–3: 261 медиа-генерация и 190 чат-вызовов; polza 1 343,57 ₽, RouterAI 212,68 ₽, Gen-API 384 ₽ —
`99-raw/phase5/runs/README.md`). Каждый тест — 1–2 образца на модель: метрика кодом и/или голос заказчика вслепую (1 чел.); правило
стенда (`04-update-procedure.md` §3) не выполнено ни разу → метки `[проверено: путь]` с n, `[стенд]` нет. Коды маршрутов не менялись.

| Код | v1 (24.09) | v2 (25.09) | Основание: тест, число, путь |
|---|---|---|---|
| все картинки GPT 2.5 | `gpt-image-2-5-flare` | **`openai/gpt-image-2.5-flare`** (цены 4/7/11 те же), старый id — `defaults.deprecated` | снимок polza `2026-09-25_1411`: старого id нет, с ним валидатор — 5 ошибок |
| `IMG-HERO-PHOTO` | Sunburst 2K 7 — основной; Flare, NB2 — запас; Seedream 4 с воротами E-01; RouterAI Sunburst `high` 3,62 (ворота N-01); `[не проверено]` в polza | основной тот же; Flare и NB2 — равные запасные; Seedream 4 без ворот («4K» = 2352×1008); RouterAI Sunburst `medium` 0,93 вместо `high`; `not` + FLUX.2 Pro, FLUX.2 max; RouterAI Qwen Image 3 и Krea 2 (3,31) — `final: false` | E-08 (голос вслепую, 1 чел.): хорошо Sunburst, Flare, NB2; NB Pro «слишком ровно», Seedream 5 Pro «минус», FLUX.2 Pro «так себе»; F-04 3 из 3; N-01: medium ≈ high ≈ polza 1K; CM-09 — `99-raw/phase5/runs/2.5-stand/E-08_blind_sheet.jpg` |
| `IMG-PRODUCT` | композит + сцена Sunburst; перенос товара `[не проверено]` | основной тот же; Seedream 5 Pro — `final: false` (концепт) | E-10: этикетка во фронте — 4 из 4, сбоку — 1 из 4 (Sunburst); SC-02 — придуманный продукт — `99-raw/phase5/runs/2.5-stand/E-10_sheet.jpg` |
| `IMG-ILLUSTR` | Flare 1K | тот же, метка `[проверено]` | E-11: «все по-своему хороши», Seedream 5 Pro темнит — `99-raw/phase5/runs/2.3-series/E-11-blind/` |
| `IMG-SERIES` | Flare; запас NB Pro 13,5 (flex 7,95); Seedream 4.5 дёшево; `[спорно]` | Flare; запас — Sunburst по методу F; сетка 2×2 Sunburst 2K — alt; NB Pro и Seedream 4.5 → `not` | E-12: стиль держит только Flare; F-01: ΔE OKLab 0,031–0,035 (3 из 3); F-02: сетка = по одному — `99-raw/phase5/runs/2.3-series/F-01_sheet.jpg` |
| `IMG-ICON3D` | Sunburst, форма + кубик; `[исследование]` | тот же; метод — `[проверено]` | F-07: IoU 0,95 и 0,92 — `99-raw/phase5/runs/2.3-series/F-07_sheet.jpg` |
| `IMG-CUTOUT` | ровный фон + u2netp; альфа моделей `[не проверено]` | тот же; Riverflow → `not`; RouterAI GPT 2.5 `transparent` — мех да, стекло нет (стекло — хромакей или Ideogram) | T2: 64 % прозрачных; H-03: мех — мягкая кайма, стекло — облако фона, маска блоками 16 px; CM-05: пусто ×2 — `99-raw/phase5/runs/S5-analysis/H-03_alpha.json` |
| `IMG-BG-ABSTRACT` | код; Flare 1K; FLUX.2 alt | + Sunburst 2K (крупная форма), + RouterAI Recraft Vector (векторный фон) | SC-01, MS-01…MS-02, CM-01…CM-02, D2-04 — `99-raw/phase5/runs/MS-marea/audit-MS-01/` |
| Seedream (7 вариантов) | флаг `visible-vendor-mark`, ворота E-01 | флаг и ворота сняты | E-01 (Seedream 4) + углы 7 кадров Seedream 4.5 / 5 Pro — меток нет, C2PA Valid — `99-raw/notes/session5/U-work/prov-seedream/provenance.md` |
| `IMG-TEXT-CYR` | HTML; модели `final: false` до лесенки E-02…E-04 | HTML основной; RouterAI Recraft V4.1 — `final: true` для ≤ 4 слов с OCR и чтением; Flare, GPT Image 2, NB2, Seedream 4.5 — `final: false`; Qwen 2.1, FLUX.2 Pro, Sunburst → `not` | E-02: 6 из 9 дословно; K-05: OCR 15/24, VLM 11/24; E-07/G-09: 3 из 3 глазом — `99-raw/phase5/runs/2.1-cyrillic/` |
| `IMG-EDIT` | NB2 / Sunburst по типу; ≤ 5 изменений за вызов | + Seedream 5 Pro (удаление); композит обязателен; до 10 изменений одним вызовом | E-15: утечки и сдвиги у 3 из 4; D2-06: 10 из 10 одним вызовом — `99-raw/phase5/runs/4-edits/E-15-check/` |
| `IMG-OUTPAINT` | NB2 + композит при REGENERATED | композит всегда; телефону — свой мастер | H-08: резкость 0,14 / 0,56 < 0,85 у обеих — `99-raw/phase5/runs/4-edits/H-08-check/` |
| `VID-HERO-LOOP` | Seedance 1.5 Pro A,A 720p 10,5; премиум Omni 48, Kling std 50; запас Veo, H3; кроссфейд хвоста; `[не проверено]` | Seedance 1.5 Pro 720p 10,5 + premium 1080p 8 с 45; Omni, Kling std, Kling pro, H3 → `not`; стык — RIFE-мост 8 кадров | I-03 шов 1,28; I-09 2,12; I-15 5,08; I-08 7,21; MS-03 3,29 → RIFE 0,69, 8 с 0,84, MS-05 1080p 0,41; VM-02 движение 0,024 — `99-raw/phase5/runs/2.4-loops/`, `99-raw/phase5/runs/MS-marea/loops/` |
| `VID-CINEMAGRAPH` | Seedance A fixed_lens; `[документация]` | без изменений; форма промта — `[проверено]` | D2-07: движение 1,61 / 1,69 / 2,45, SSIM0 0,814; MS-03: сдвиг камеры до 36,5 px — `99-raw/phase5/runs/3-prompt-form/video/D2-07/` |
| `VID-I2V-PRODUCT` | Kling 3 std 50; `[мнение вендора]` | тот же + Seedance FLF по кадрам 3D (10,5) | SC-03: OCR 11 из 11; 3D-21: силуэт 0,82–0,90 — `99-raw/phase5/runs/SC-showcase/SC-03-frames/` |
| `VID-ABSTRACT` | Seedance 2 Mini 12,83 | **Seedance 1.5 Pro i2v по кадру 10,5**; 2 Mini — без кадра; 2 Fast — `final: false`; Grok — переходы | VM-01, решение заказчика п. 14 («картинка → видео») — `99-raw/phase5/runs/6-video-models/sheets/` |
| `VID-CAMERA` | Kling 3 pro 5 с 60; `[не проверено]` | **Seedance 1.5 Pro наезд 720p 10,5 / 1080p 22,5**; Kling 3 pro 3 с 36 — alt | VM-01, VM-02, MS-05: «все красивые, зависит от задачи»; Seedance дешевле в 1,6–3,4 раза |
| `VID-V2V` | Omni 126; preview 70 до 30.09 | не маршрут (решение заказчика п. 12), `final: false`; preview → `not` | I-17, I-20 не запускались |
| `VID-ALPHA` | Seedance на ключе; Grok `final: false` | Grok 1.5 с запретами → alt `final: true` | D2-08: дрейф −58 %; D2-11: Seedance наезжает ×1,8–2,1 |
| `VID-SCROLL` | FLF A → B; `[не проверено]` | + наезд 1080p; доставка — секвенция против короткого GOP | SC-04: кадр 0 = A, последний = B — `99-raw/phase5/runs/SC-showcase/SC-04_endpoints.jpg`; B/10 |
| `VID-UPSCALE` | Omni 1080p 48; Topaz 24 | **Seedance 1.5 Pro 1080p 22,5**; Omni — alt; Topaz → `not` | MS-05; VM-05: 2 × INTERNAL_ERROR |
| `VEC-ICON-LINE` | Lucide / LLM в сессии; polza-chat 0,92 / 2,46 | тот же; цены 0,84 / 3,43; Sonnet 5, DeepSeek → `not` | G-02, G-01; G-03 пустой ответ 9,77 ₽; G-04 ×6,9 к оценке; разбор V: поле и зазор 4 из 6 у обеих (Claude в сессии — 6 из 6) — `99-raw/phase5/runs/S5-analysis/G-llm-svg/nearest-lucide.json` |
| `VEC-ICON-FILLED` | Recraft V4.1 Vector 8,78 | **Pro Vector 33,11** (наборы); Vector 8,83 — черновики; палитра — перекраской; на страницу — SVG без `<metadata>` | CM-01: 8 из 8, путей −44 %, без манифеста 6,7 против 10,1 КБ; B2-01; CM-03; провенанс — `99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md` |
| `VEC-ILLUSTR` | Vector 8,78 | Vector 8,83 — фоны и иллюстрации; Pro 33,11 — спот; фото → вектор (image-to-image) | CM-01 spot/bg, CM-02 — `99-raw/phase5/runs/5-vector/analysis/illustrations/metrics.md` |
| `defaults` | `deprecated` | + `unavailable_2026_09_25` (H3 Max, Topaz video, Wan 3.0), `not_routes` (3D по картинке, V2V, альфа Riverflow), `channel_rules`; класс доказательств `run` | журнал `99-raw/experiments/_ledger.jsonl`; `99-raw/experiments/3D/README.md` |

Без изменений маршрута (тест не прогонялся — отменено заказчиком 25.09, п. 15–16): `IMG-TEXTURE` (H-09), `IMG-TEXT-LATIN` (E-17),
`IMG-MOCKUP`, `IMG-UPSCALE` (H-05), `IMG-DRAFT` (E-16, N-03), `IMG-LAYERS` (H-10), `VID-CHARACTER`, `VID-LONG` (I-05 закрыт SC-04, I-07,
I-14, I-18 — нет), `VEC-PATTERN`, `VEC-ANIM`, `VEC-TRACE` (G-13, G-16).

## 3. Видео (`VID-*`)

Цены — polza, ₽ за ролик без звука, 24.09.2026. Маршрут — по возможностям канала (первый и последний кадр, неподвижная
камера, цена), а не по месту на арене. Все вызовы — `[не проверено]` до фазы 5; порядок и ворота — `99-raw/phase5/plan.md`.

| Код | Основная (параметры, ₽) | Запас / премиум | Черновик | Диалект | Постобработка | Чем проверять | Метка | Фаза 5 решит |
|---|---|---|---|---|---|---|---|---|
| `VID-HERO-LOOP` | `bytedance/seedance-1.5-pro` [A, A] 720p 4 с `fixed_lens: "true"`, `generate_audio: "false"` — 10,5 | премиум: `google/gemini-omni-1.1-flash` 1080p 4 с, `first_frame_url` = `last_frame_url` — 48; `kling/v3` std 5 с [A, A] — 50; запас при провале обоих: `google/veo3_fast` FLF — 45, `minimax/hailuo-3-max` 480p 5 с (`openrouter`) — 47,30 | то же 480p — 5,25 | seedance-1-5 · prose: только движение + перечень фона + неподвижное + запреты | `trim --auto` (дубль последнего кадра); было: кроссфейд хвоста 12 кадров; **фаза 5: на крупной форме кроссфейд даёт «фантом» (двоение, шов 1,46–1,76) → стык — RIFE-мост 8 кадров (3,29 → 0,69; 8 с 3,45 → 0,84; 1080p 0,41), пинг-понг — чистый шов 0,66–0,74, но движение назад** [поправка фазы 5, 25.09.2026 → §2.2]; «две половины» | `video-loop --control --mezzanine` (`seam_ratio_local` ≤ 1,5, `motion_vs_control` ≥ 0,5, `cut_ratio` < 10) · `video-loop` | было [не проверено]; фаза 5 — [проверено: 99-raw/phase5/runs/2.4-loops/I-03.loop.json, шов 1,28, 1 образец] | I-01…I-03, I-09, I-15, T9; ворота I-10, I-11 — не покупались |
| `VID-CINEMAGRAPH` | Seedance 1.5 Pro [A] 720p 4 с `fixed_lens` — 10,5 | `kling/v3` std 5 с + «The camera remains fixed on …» — 50; маска `maskedmerge` — 0 | 480p — 5,25 | seedance-1-5 · prose; «что не названо — не движется» | `drift --mask` < 0,5 от контроля; убрать «подсказки движения» из кадра | `video-loop --mask` · `video-loop` | [документация]; держит ли — [не проверено] | D2-07 (закрывает I-04) |
| `VID-I2V-PRODUCT` | `kling/v3` std 5 с [P] — 50 | `google/veo3_fast` `REFERENCE_2_VIDEO` 3 референса — 45 | Seedance 1.5 Pro 480p — 5,25 | kling · prose; сначала камера и свет; «No zoom. No spin.» | OCR надписи по кадрам; ΔE00 цвета бренда ≤ 5 | `video-loop` · `video-product` | [мнение вендора] | I-13, I-19, D2-08 |
| `VID-ABSTRACT` | шейдер кодом 6–25 КБ — 0; модель — `bytedance/seedance-2-mini` 480p 5 с — 12,83 | — | `grok-imagine-video-1-5` 480p 5 с — 8,10; Seedance 1.5 480p — 5,25 | seedance-2 · prose | петля — как `VID-HERO-LOOP` (FLF только у Seedance 1.5, Kling, Veo, H3, Omni) | `video-loop` · `video-loop` | [исследование] | I-08, I-12 |
| `VID-CAMERA` | `kling/v3` pro 5 с — 60 (std — 50) | `google/veo3_fast` FLF — 45 | Grok 1.5 480p — 8,10 | kling · prose; одно движение, словарь кино, орбита ≤ 45° | — | `video-loop --camera-move` · `video-loop` | [не проверено]; бенчмарка нет | не тестируется |
| `VID-CHARACTER` | `kling/v3-motion-control` 720p, видео движения 5 с — 70 | `kling/v3` std 5 с — 50 | — | kling · prose | — | `video-loop` · `video-loop` | [не проверено] | не тестируется |
| `VID-LONG` | цепочка Seedance 1.5 Pro 720p по последнему кадру / «две половины» — 10,5 за клип | `bytedance/seedance-2-5` 480p 15 с — 283,50; Veo Fast + `extend` — 45 + 45 за шаг | — | seedance-2-5 · sections (таймкоды — целые секунды) | `join`: ΔE00 < 2, `join_ratio` ≤ 1,5; правленый конечный кадр — `colormatch` до генерации | `video-loop` · `video-loop` | [документация] | I-05, I-07, I-14, I-18 |
| `VID-V2V` | `google/gemini-omni-1.1-flash` с `videos` 720p 4 с — 126 | preview `gemini-omni-video` — 70, только до 30.09.2026 | — | omni · prose | шов не хуже входа + 0,3; `curve_corr` ≥ 0,8 | `video-loop` · `video-loop` | [не проверено] | I-17 / I-20 |
| `VID-ALPHA` | Seedance 1.5 Pro [объект на ключе] 720p `fixed_lens` — 10,5 → `chromakey` + despill → stacked alpha | Grok 1.5 с запретами движения — 8,10 | 480p — 5,25 | seedance-1-5 · prose | ключ по оттенку объекта (#00B140 или пурпурный); despill `geq` | `video-alpha --key` · `video-product` | [практика]; ровный ключ — [не проверено] | I-06, I-14, D2-08 |
| `VID-SCROLL` | FLF A → B Seedance 1.5 Pro 720p — 10,5 | `kling/v3` std [A, B] — 50 | 480p — 5,25 | seedance-1-5 · prose | кадры → GOP 8 (×3), не all-intra (×9,3) | `video-loop` (SSIM кадр 0 ↔ A, последний ↔ B ≥ 0,9) | [не проверено] | I-05 |
| `VID-UPSCALE` | нативно в целевом разрешении: GA Omni 1080p = 720p по цене — 48 | `topaz/video-upscale` ×2 — 6 ₽/с (4 с — 24); Veo `upscale_1080p` — 10 (только Veo) | RIFE локально — 0 (не для текста) | без промта | — | `video-loop` | [документация] | I-16 (резерв) |

**Не маршруты**: Seedance 2.x для петли (`images` — референсы; I-08), Wan 3.0/3.0 Prime (один кадр, 23,65–33,11 ₽/с),
Sora 2 (API снят 24.09.2026), preview `gemini-omni-video` после 30.09.2026, видео через RouterAI (×1,4–5,4 к polza, B2), Luma
Ray 3.2 `loop` (единственная нативная петля — вне доступа, иностранная оплата).

**Поправка фазы 5 (25.09.2026)** [проверено: 99-raw/phase5/runs/2.4-loops/, 99-raw/phase5/runs/MS-marea/loops/, по 1 образцу]:
премиумы петли хуже дешёвой по шву — Kling 3 std [A, A] 2,12, GA Omni 1.1 FLF 5,08 (+ звук всегда), Kling 3 pro 1080p — почти
стоп-кадр (движение 0,024); Seedance 2 Mini — 7,21 → в v2 премиумов петли нет, 1080p — тот же Seedance 1.5 Pro (8 с — 45 ₽).
Наезд камеры — Seedance 1.5 Pro 720p 10,5 / 1080p 22,5 (основной `VID-CAMERA` вместо Kling 3 pro); переход раздела — Grok 1.5
(трансформация формы). Выбыли 25.09: MiniMax H3 Max (2 × 503 «нет провайдеров»), Topaz video (2 × INTERNAL_ERROR), Wan 3.0 (503);
V2V — не маршрут по решению заказчика (п. 12). Таблица выше — v1; полная v2 — `routing.yaml`, изменения — §2.2.

## 4. Вектор (`VEC-*`)

| Код | Основная | Запас / альтернатива | Цена | Постобработка | Чем проверять | Метка | Фаза 5 решит |
|---|---|---|---|---|---|---|---|
| `VEC-ICON-LINE` | готовый набор (Lucide ISC, `lucide-static` 1.47.0); новые метафоры — LLM → SVG в сессии по спецификации 24/2 + `check_icons.py` | polza-chat: `google/gemini-3.8-flash` (≈ 0,92 ₽), `openai/gpt-5.6-sol` (≈ 2,46 ₽) | 0 / токены | svgo, спрайт `<symbol>`, `currentColor`, тёмная тема | `svg-icon` · `svg-icon`; узнаваемость — VLM без подсказки (G-06) | [исследование] + [проверено] | G-01…G-06 |
| `VEC-ICON-FILLED` | RouterAI `recraft/recraft-v4.1-vector`, палитра словами | RouterAI `recraft/recraft-v4-styles-vector` (набор по стилю); Gen-API `recraft-v4` vector `pro: false` (colors документирован); растр Sunburst 2×2 → vtracer | 8,78 / 5,49 / 20 / 4 | удалить фон-прямоугольник до svgo; `keep-signature`; отверстия цветом фона → potrace | `svg-icon` · `svg-icon` (ΔE00 заливок ≤ 3) | [документация]; палитра через RouterAI — [не проверено] | B2-01, G-07, G-08, G-13, G-14, G-15, G-17, G-18 |
| `VEC-ILLUSTR` | RouterAI `recraft/recraft-v4.1-vector` | Utility (растр) → vtracer; Gen-API `recraft-v4` vector; растр Flare → vtracer `--palette` | 8,78 / 3,84 / 20 / 4 | чистка SVG; 68–123 КБ → `<img>`, не inline | `svg-icon` · `illustration` (≤ 5 заливок, ≤ 40 КБ) | [исследование]; уровень студии — [не проверено] | G-10, G-11, G-12, G-16 |
| `VEC-PATTERN` | SVG/CSS кодом (130–180 байт); `mask-image` + `var(--brand)` | — | 0 | штрих через край плитки | `svg-icon` | [проверено: G] | не нужен |
| `VEC-ANIM` | inline SVG + CSS с `prefers-reduced-motion` | Lottie/dotLottie кодом (lottie_light 46 КБ gzip) | 0 | SMIL, SVG в `<img>`, Lottie reduce не слушают | `svg-icon` + `page_accept.py` (reduce) | [проверено] | не нужен |
| `VEC-TRACE` | vtracer 1.0.0-alpha.4 `--palette` (≤ 8 цветов, SSIM 0,985); ч/б — potrace 1.16 | Gen-API `image-2-svg` | 0 / 1 | палитра с цветом контура; svgo | `svg-icon` (SSIM ≥ 0,95, ≤ 5 КБ) | [проверено] | G-13, G-16 |

## 5. Сквозные поля маршрута: проверка, доставка, право

| Поле `routing.yaml` | Значение по умолчанию (`defaults`) | Кто владеет |
|---|---|---|
| `check.audit_mode` + `check.rubric` | `asset_audit.py audit <файл|папка> --mode <режим> --strict`; рубрика `11-evaluation-qa/rubrics/<имя>.rubric.json` (12 рубрик); VLM — только смысл, видео не судит; кириллицу и латиницу читает OCR + человек | K (`11/01–03`) |
| `delivery: image` | AVIF по SSIMULACRA2 ≥ 80 (hero) / ≥ 70 (`avif_pick.sh`) + WebP ≤ 1920 в `<picture type>`; JPEG XL — первым необязательным `<source>` с 06.10.2026; телефону — мастер 4:5; LCP без lazy, `fetchpriority="high"`, ≤ 150/80 КБ | J (`10/01`), H (`08/04`) |
| `delivery: video` | AV1 10 бит + H.264 (CRF по `motion_keep` ≥ 0,75: AV1 24–28, H.264 18–20), полные теги BT.709, `-an`, `-map_metadata 0 -movflags use_metadata_tags+faststart`, постер = кадр 0 финального AV1 → AVIF, reduce → 0 байт, пауза при движении > 5 с | J (`10/02`), I (`09/03`) |
| `delivery: video_alpha` | stacked alpha + WebGL2 (≈ 12,5 КБ на 2 с); HEVC-alpha — только Safari; VP9-alpha 16–30 КБ | J, I (`09/02`) |
| `delivery: svg` / `og` | svgo с `keep-signature`, спрайт, `currentColor`; OG — HTML/CSS → Playwright 1200×630 ≤ 300 КБ | G (`07`), J |
| `legal.flags` | `research` (Qwen 2.1 — не финал), `nc-weights` (RMBG-2.0 по умолчанию в rembg, Depth Anything Base/Large, FLUX.2 dev/klein), `nc-weights-disputed` (isnet), `no-automation` (Midjourney), `visible-vendor-mark` (Seedream — до E-01; MiniMax H3 — метка в контенте по ToS, ворота I-10/I-11 `[поправка X2 24.09.2026]`), `vendor-mark-keep` (C2PA, SynthID, `AIGC`, `<recraft-signature>` не удалять), `people-consent` (маршруты со строками 12–14 политики: `IMG-HERO-PHOTO`, `IMG-SERIES`, `IMG-EDIT`, `VID-CHARACTER` — `routing_check.py` проверяет), `product-real-only` | L (`12/01`, `12/04` §2) |
| провенанс | мастер побайтно → кодирование → `provenance_check.py stamp --dst trained|composite` (+1–3 КБ) → `asset_audit --stage web`; видимая иконка ЕС «AI» — для дипфейков на сайте с аудиторией ЕС | L (`12/02` §5–7) |
| промт | компилятор `prompt_compile.py` v2.1 → диалект семейства `dialects.yaml` v0.3; усилители выключены; описание по-английски; **запреты последними — у видео да, у картинок нет** (решение N до фазы 5: 146 заданий, сопоставимость плеч D2-01/09) | D2 (`05/04–06`) |

## 6. Слот → код → бюджет: фильтр до маршрута

Слот страницы сначала решает, генерировать ли вообще (A `01` §2.1, L `04` §2), затем даёт код и ограничение веса.

| Слот | Коды | ИИ уместен? | Бюджет (десктоп / телефон) | Не генерировать |
|---|---|---|---|---|
| Hero | `IMG-HERO-PHOTO`, `IMG-PRODUCT`, `IMG-BG-ABSTRACT`, `VID-HERO-LOOP`, `VID-CINEMAGRAPH`, `IMG-MOCKUP` | ⚠️ атмосфера, сцена без людей, фон под UI | картинка ≤ 150 / 80 КБ; петля ≤ 1,5 МБ / 600 КБ | сам товар, люди-«клиенты», скриншот |
| Фичи (3–6 блоков) | `IMG-ILLUSTR`, `IMG-SERIES`, `VEC-ICON-LINE`, `IMG-ICON3D`, `IMG-MOCKUP` | ⚠️ иллюстрации и фоны | ≤ 120 / 70 КБ на картинку | скриншот интерфейса |
| «Как это работает» | `VEC-ILLUSTR`, `VEC-ICON-FILLED`, схема `IMG-ILLUSTR` (эскиз) | ⚠️ эскиз; итог — вектор | ≤ 20 КБ SVG | подписи моделью |
| CTA, фоны секций | `IMG-BG-ABSTRACT`, `IMG-TEXTURE`, `VEC-PATTERN`, `VID-ABSTRACT` | ✅ | ≤ 60 КБ; текстура ≤ 30 КБ плитка | — |
| OG и баннеры | `IMG-TEXT-LATIN`, `IMG-TEXT-CYR` (текст — HTML), `IMG-BG-ABSTRACT` | ✅ фон | ≤ 300 КБ, 1200×630 | текст моделью |
| Галерея товара (PDP) | `IMG-PRODUCT`, `IMG-CUTOUT`, `VID-I2V-PRODUCT`, `IMG-EDIT` | ⚠️ фон вокруг реального товара | ≤ 150 КБ на кадр | товар «как есть» |
| Пустые состояния, 404, онбординг | `IMG-ILLUSTR`, `VEC-ILLUSTR`, `IMG-SERIES` | ✅ по паспорту | ≤ 40 КБ (SVG/WebP) | — |
| Инфографика маркетплейса (RU) | `IMG-TEXT-CYR` (шаблон), `IMG-CUTOUT`, `IMG-BG-ABSTRACT` | ⚠️ фон | ≤ 150 КБ | кириллица моделью |
| Обложки блога | `IMG-ILLUSTR`, `IMG-SERIES`, `IMG-HERO-PHOTO` | ✅ мнения, объяснения | ≤ 120 КБ | новостные фото |
| Отзывы, команда, логотипы клиентов, фавиконы (знак) | — | ❌ | — | всё: только реальные фото и файлы клиента |

## 7. Как выбирать, если задачи нет в таблице

1. **Разложить на коды таксономии**: «баннер с товаром и надписью» = `IMG-PRODUCT` (сцена) + `IMG-CUTOUT` (товар) +
   `IMG-TEXT-*` (надпись HTML) — маршрут у каждой части свой, склейка — композит и HTML.
2. **Проверить уместность по слоту** (§6, L `04` §2): «не делаю» — стоп; «спросить» — вопрос заказчику до генерации.
3. **Код раньше модели**: геометрия, текст, палитра, схема, паттерн, иконка из набора — код (0 ₽, детерминированно).
4. **Возможности канала, а не рейтинг**: нужен ли последний кадр, альфа, маска, seed, референсы (сколько), соотношение 8:1,
   неподвижная камера, звук — смотреть `polza.py show <id>` (параметры и ступени цены у своего провайдера) и
   `dialects.yaml`; нужного параметра нет в polza — `02-providers-platforms/06-gap-map.md` (RouterAI, Gen-API) или
   постобработка H/I.
5. **Класс доказательств по задаче**: срез арены по смыслу (Text Rendering, UI/UX, Retail, правка), профильный бенчмарк
   (PaintBench, GDB, FEPBench, OCRGenBench), не общий Elo (`02` §3); расходятся — `[спорно]` и тест.
6. **Из кандидатов в интервале лидера — самый дешёвый**, затем быстрее, затем с запасным провайдером (`01` §5); ценовые
   параметры и `provider` — явно; `polza.py estimate` до вызова.
7. **Проверка — тем же `check` ближайшего кода** (`asset_audit` режим + рубрика) и тем же `delivery`; новая комбинация —
   `[не проверено]` и строка в журнал решений заказчика.
8. **Если повторяется ≥ 3 раз** — предложить новый код (как `IMG-LAYERS`) в отчёте и маршрут в `routing.yaml` через
   `04-update-procedure.md`.

Примеры: «иконка с кириллической подписью» → `VEC-ICON-LINE` + текст HTML; «видео с продуктом на прозрачном фоне» →
`VID-ALPHA` (ключ) + `VID-I2V-PRODUCT` (облёт ≤ 45°) — одна генерация на ключе; «сезонная перекраска hero» → `IMG-EDIT`
(NB2, «не трогать остальное») + грейд `.cube`; «лента-разделитель 8:1» → `IMG-BG-ABSTRACT` ultrawide (NB2 Lite) или CSS.

## 8. Что меняет фаза 5 в маршрутах (ворота)

Колонка «Итог фазы 5» — по живым прогонам 25.09.2026 (1–2 образца на модель; пути — `routing.yaml` v2, `evidence` класса `run`).

| Тест | Если да | Если нет | Итог фазы 5 (25.09.2026) |
|---|---|---|---|
| N-01 (RouterAI, 9,70 ₽; списано 8,99 — журнал): polza отдаёт GPT 2.5 ниже `high` | финалы фото — RouterAI Sunburst `high` (16:9 — 3,62 ₽, дешевле polza 1K) | polza остаётся основным каналом GPT 2.5 | нет (разбор V, n = 2 брифа): medium 0,93 ₽ ≈ high 3,57 ₽ ≈ polza 1K 4 ₽ на глаз и метриках → polza остаётся основным; RouterAI `medium` — тот же класс за четверть цены, но 1536×864 |
| T5 (фаза 0): `provider.only` работает | NB Pro через `google-vertex/global/flex` 7,95 ₽ вместо 13,5 во всех маршрутах | NB Pro только `mie` 13,5; серия — Flare | `provider` работает (NB2 Lite через Google AI Studio 4,06 ₽ против 2,90 у `mie`), но NB Pro выбыл по качеству (E-08, E-12) → flex не нужен |
| T9 (фаза 0): GA Omni принимает URL хранилища в `*_frame_url` | GA Omni 1.1 — премиальная петля (I-15) | премиум — только Kling 3 | принимает, но петли нет (I-15: шов 5,08) → премиумов петли нет |
| E-01: видимый «AI-generated» у Seedream через `mie` | Seedream убирается из `cheap` в 7 маршрутах (флаг `visible-vendor-mark` → вопрос заказчику) | Seedream 4 4K 3 ₽ — дешёвый hero, фон, текстура | метки нет (Seedream 4 + углы 7 кадров 4.5 / 5 Pro), C2PA Valid → флаг снят; но «4K» Seedream 4 = 2352×1008 |
| E-02…E-04: лидер пишет кириллицу 3 из 3 | `IMG-TEXT-CYR` — модель для ≤ 4 слов крупно с OCR и вычиткой | правило «кириллица только HTML» → `[стенд]` | E-02 — 6 из 9 моделей 1 из 1; E-03…E-04 не прогонялись; Recraft V4.1 — 3 из 3 глазом → HTML основной, Recraft — для ≤ 4 слов с OCR и чтением |
| E-08, E-09 | лидер фото-hero и ступень 2K/4K → `[стенд: 2 задачи × 6 моделей × 1, голоса + A/04, дата]` | v1 остаётся с `[не проверено]` | E-08: хорошо Sunburst, Flare, NB2 (голос вслепую, 1 чел.) → `[проверено]`, не `[стенд]`; E-09 не прогонялся |
| E-15, H-06, H-07 | разбиение `IMG-EDIT` по типу правки подтверждено или поменяно | — | E-15: разбиение в силе, неизменность — только композит; удаление — Seedream 5 Pro; H-06, H-07 не прогонялись |
| I-08: Seedance 2.x `images` — кадры | дешёвая петля Seedance 2 Mini (10,26 ₽) становится вариантом | Seedance 2.x остаётся в `not` | нет: SSIM кадра 0 — 0,60, шов 7,21 → в `not`; с фразой роли Seedance 2 Fast кадр держит (0,85), но 41,85 ₽ за 480p |
| I-02/I-03 проходят, I-09/I-15 не лучше на глаз | премиум не нужен: I-10, I-11 не запускать (−92,3 ₽) | запас H3 Max / Veo Fast | I-03 проходит (1,28), I-09 2,12, I-15 5,08 → I-10/I-11 не покупались; H3 Max всё равно выбыл (2 × 503) |
| B2-01 / G-07: `controls` доходят через RouterAI | палитра Recraft параметром | палитра словами; запас — Gen-API `colors` | доходит (неверный `controls` ломает запрос, 0 ₽); точность палитры параметром (G-07) не проверена → точная палитра — перекраской SVG |
| D2-01/02: эффект формы ≥ 10 п. п. и ДИ > 0 | новое умолчание в `dialects.yaml` → `ab_results` | умолчания не меняются | D2-01: +2,8 п. п., ДИ [−2,7; +9,1] → умолчания не меняются; D2-02 — глазом, судья не прогонялся (решение заказчика п. 16) |
| K-01: судья совпадает с голосами ≥ 0,8 | VLM сортирует best-of-N | только отсев брака или не использовать | не прогонялся (голоса заказчика по слепым парам не собраны); судья D2-03 — согласие на повторах 100 % (n = 4); K-03 (разбор V): временные дефекты видео по листу кадров — 2 и 3 из 14 (Gemini, Qwen) → видео только метриками; K-04: смещения к сжатию нет (96 из 96, фильтр грубый) — `99-raw/phase5/runs/S5-analysis/K/K-03_eval.json` |
| L-01/L-02: метки канала | колонка «метки» в паспорте по факту | — | 254 выхода: OpenAI через polza — C2PA Trusted 71 из 73; Google через `mie` — через раз (NB2 8 из 19, NB Pro 1 из 5, NB2 Lite 19 из 21); Seedream, FLUX.2, Grok — Valid; Kling 3 — AIGC в тегах MP4; Qwen Image 3 — TC260; Seedance 1.5 Pro, Z-Image, Qwen 2.1, Krea 2 — меток нет; Recraft SVG — C2PA в `<metadata>` (после чистки Invalid) — `99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md` |
| (новое) 3D-модель по картинке | — | — | Gen-API TRELLIS 4 ₽ … Hunyuan3D 96 ₽: органика — после доводки, стекло и надписи теряются; вердикт заказчика — «так себе, лишнее» → `defaults.not_routes` (кроме управляемого поворота и ракурсов для FLF) |

## Частые ошибки

1. **Место на арене как маршрут**: «Wan 3.0 — лидер видео» → но через polza он без последнего кадра и петлю не строит.
2. **Общий Elo вместо среза по задаче**: NB2 — №1 по «красоте без промта», но #7 по следованию и #15 по читаемости текста.
3. **Qwen 2.1 в финал** «потому что только у него альфа» — исследовательская лицензия; финал — ровный фон + вырез или
   RouterAI GPT 2.5 `background: transparent`.
4. **hex в промте как гарантия бренд-цвета** — попадание ≈ 50 %; цвет — грейдом и ΔE к паспорту.
5. **Одна модель на все правки** — GPT выполняет сложное, но перерисовывает лишнее; NB2 сохраняет, но меняет цвета на
   составной правке; мелкие точные правки — вообще не моделью.
6. **Цена без ценового параметра** — Kling `mode` вне списка → запасная ступень 45 ₽/с (225 вместо 60); Seedance 2 без
   `duration` — 415 ₽.
7. **Устаревшие id по памяти**: `openai/gpt-5-image` (выкл. 23.10), `flux.2-flex` (дубль ×2,8), `x-ai/grok-imagine-image`
   (база, не 2.0), `gemini-omni-video` (до 30.09), Sora 2 (снят).
8. **Seedance 2.x для петли** — `images` у 2.x «референсы», первый кадр не гарантирован.
9. **Видео на VLM-приёмку** — судья не видит стоп-кадров и шва; только метрики I и глаз.
10. **Звук «выключен», а модель без параметра** (Veo, Omni, Wan 2.5/2.6, Grok, H3) — дорожка есть; `-an` при кодировании.
11. **RouterAI для видео** — в 1,4–5,4 раза дороже polza.
12. **Real-ESRGAN как «безопасный апскейл» фото** — хуже Lanczos, выдумывает структуру.
13. **Текст интерфейса в пикселях** — «1 из 4 строк нечитаема» даже у лучших; HTML.
14. **rembg без явной модели** — по умолчанию некоммерческая RMBG-2.0.

## Чек-лист

- Код задачи определён (или задача разложена на коды по §7)?
- Слот разрешает ИИ (§6, L `04` §2); для «спросить» есть ответ заказчика?
- Можно ли решить кодом (CSS/SVG/HTML) — проверено до выбора модели?
- Вариант взят из `routing.yaml`: id, провайдер, ценовые параметры, цена по снимку, `final: true`?
- `polza.py estimate` / `mp_client.py estimate` — 0 ошибок, цена совпала?
- Диалект — из `dialects.yaml`, промт собран компилятором, усилители выключены?
- Звук выключен параметром или `-an` при кодировании?
- После генерации — `asset_audit.py --strict` с режимом и рубрикой маршрута; правка — `edit_check.py`; петля — на мезонине?
- Доставка по `delivery` маршрута; провенанс — `stamp` производной, мастер побайтно?
- Флаги `legal` пусты для финала (нет `research`, `nc-weights`, `no-automation`)?
- После фазы 5 метка заменена на `[стенд: …]` по `01-stand-method.md` §5 и валидатор прогнан?

## Открытые вопросы и противоречия

1. **Seedream 5 Pro**: Rapidata #25/#33 (фото) против LMArena #9 и Design Arena Product #5 — в маршрутах только в `not` до E-08
   и E-10. [поправка фазы 5, 25.09.2026: решено для фото — E-08 «сразу минус» (голос вслепую, 1 чел.); в товаре фронт дословен (E-10),
   удаление предмета — PASS (E-15) → варианты `IMG-PRODUCT` (концепт) и `IMG-EDIT` (удаление)]
2. **UI/UX**: Rapidata — Sunburst №1, Flare #12; AA — Flare №1. Мокап — композит, поэтому спор не блокирует маршрут.
3. **Схемы**: FEPBench (GPT 2 > NB Pro) против AIBench (NB Pro > Seedream 5 Lite > GPT-1.5, без GPT 2.x) — `scheme` отдан
   GPT 2 как единственному проверенному на обоих поколениях; стенд задачу «схема процесса» не мерит.
4. **Что отдаёт polza без `quality`** у GPT Image 2.5/2 — неизвестно (Simon Willison: GPT 2 по умолчанию теряет объект на
   сложной сцене); E-01, E-08. [фаза 5, 25.09.2026: E-08 — Sunburst в polza «хорошо» глазом заказчика; N-01 (RouterAI high/medium)
   разобран V (n = 2 брифа): `medium` 0,93 ₽ ≈ `high` 3,57 ₽ ≈ polza 1K 4 ₽ — «polza отдаёт ниже `high`» не подтверждено → `99-raw/phase5/runs/S5-analysis/N-01_metrics.json`]
5. **Grok Image 2.0 в polza** — какая версия (Medium / Auto) — неизвестно; Rapidata ставит Grok 2.0 Medium #5 общий (выше NB2)
   → мини-стенд, пока — только черновик. [фаза 5: N-03 не прогонялся — вопрос открыт]
6. **Recraft V4.1 Flash** (RouterAI, 24.09): карточка вендора без замеров; `final: false` до мини-стенда вне polza. [фаза 5: CM-09 —
   фото-черновик с синим сдвигом, линейная иконка растром — чистая (1 образец)]
7. **`controls` Recraft через RouterAI** не документирован для `/api/v1/images` (есть у OpenRouter); B2-01 — 0 ₽ при 400.
   [поправка фазы 5: B2-01 — неверный `controls` доходит до Recraft и даёт 200 без `data[]` (0 ₽) → поле проходит; точность палитры
   параметром не проверена]
8. **Запреты последними у картинок** — порядок v1 оставлен; решить после D2-09.
9. **IMG-LAYERS** — код предложен H, в таксономию не введён; решение — S (синтез).

## Источники

- [S1] `13-routing-matrix/routing.yaml` v1 (этот маршрут, 24.09.2026) и `../../scripts/ai-media/routing_check.py` — [проверено:
  99-raw/experiments/N/01-routing-check].
- [S2] `13-routing-matrix/02-existing-evidence.md` (E + вливание J1–J26, N 24.09) — классы A/B/C по задачам.
- [S3] `13-routing-matrix/routing.v0.yaml`, `01-stand-method.md` (E, 23.09) — правило решения §5, мини-стенд §7.
- [S4] `99-raw/notes/wave2/E-helper-evidence.md` — 32 источника (Rapidata T2I и SVG, Design Arena, GDB, PaintBench,
  GenColorBench, Pinterest, OCRGenBench, FEPBench, AIBench, Lucida, LiWi, MultiBind, VIBE, Edit-Compass, GenAI Showdown).
- [S5] `03-image-models/03-capabilities-by-task.md` §1 (C1), `04-video-models/03-capabilities-by-task.md` §1 (C2).
- [S6] `02-providers-platforms/02` §7, §11 (B), `06-gap-map.md` §1–§3 (P), `07-multichannel-client.md` (B2).
- [S7] `05-prompting/dialects.yaml` v0.3, `04-video-prompting.md`, `05-edit-reference-series.md`, `06-ab-protocol.md` (D2, D2b).
- [S8] `06-art-direction-consistency/01–04` (F), `07-vector-svg-icons/01–04` (G), `08-image-post-processing/01–04` (H),
  `09-video-pipeline/01–04` (I).
- [S9] `10-web-integration/01–04` (J), `11-evaluation-qa/01–03`, `thresholds.yaml`, `rubrics/` (K), `12-legal-provenance/01–04` (L).
- [S10] `01-web-assets-landscape/01` §2.1, `03` §1 (A).
- [S11] Снимки каталогов: `99-raw/cache/polza/2026-09-24/`, `99-raw/cache/routerai/2026-09-24_0424/`,
  `99-raw/cache/genapi/2026-09-24_0424/` (публичные GET, 24.09.2026 04:10–04:24).
- [S12] Отчёты `99-raw/reports/wave1-*`, `wave2-*`, `wave3-{B2,J,K,L}-report.md` (раздел 4 «N»); планы `99-raw/phase5/*-plan.md`.
- [S13] Фаза 5 (25.09.2026): `99-raw/phase5/runs/README.md` (заходы 1–3), разборы `99-raw/phase5/runs/*/`, журнал
  `99-raw/experiments/_ledger.jsonl`, отчёты `99-raw/reports/session4-{A,B,C}-report.md`, провенанс
  `99-raw/experiments/L/05-phase5-provenance/2026-09-25/provenance.md`; снимки `99-raw/cache/{polza,routerai,genapi}/2026-09-25_1411/` —
  [проверено].
