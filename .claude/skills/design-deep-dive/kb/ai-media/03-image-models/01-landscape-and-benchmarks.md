# Модели картинок: ландшафт на сентябрь 2026 и что меряют независимые оценки

Волна 1 · агент C1 · 2026-09-23 · прочитано целиком или существенно ≈ 60 источников + 26 статей и лидербордов бенчмарков
(сверены по первоисточникам помощниками C1), опытов 6
(`99-raw/experiments/C1/01–06`; арены сняты целиком по всем категориям — C1/03, C1/04) · снимок каталога polza 2026-09-23.
Карточки моделей — `02-model-cards.md` и `models/*.yaml`; выбор по задачам — `03-capabilities-by-task.md`.

## Выжимка для агента

1. Модель под задачу выбирать по **категорийным срезам** арен (AA: 20 срезов t2i и 18 правки; LMArena: 8 и 5), а не по
   общему рейтингу: лидер меняется (UI/UX и Marketing — Flare, Text Rendering и Productivity — GPT Image 2, Knowledge —
   Grok Imagine Image 2.0, Layout #5 — Qwen-Image-3.0-Pro). → §2.3 [исследование]
2. На 21–23.09.2026 обе арены сходятся: №1–3 почти во всех срезах — GPT Image 2.5 Sunburst, GPT Image 2.5 Flare (обе от
   08.09.2026) и GPT Image 2; отрыв Sunburst от лучшей не-OpenAI — 47 Elo в AA (1197 против 1150) и 89 в LMArena (1423 против
   1334). → §2.2, §3.2 [исследование]
3. Второй эшелон (нет в polza): Grok Imagine Image 2.0, MAI-Image-2.6, Muse Image, Qwen-Image-3.0-Pro, Reve 2.1. Лучший
   не-OpenAI из polza — Nano Banana 2 (AA #6); в LMArena по портретам, фото, Cartoon и Art его обходит Seedream 5.0 Pro.
   → §2.3, §3.2 [исследование]
4. Арена = слепое предпочтение людей на **английских** промтах 1:1 при дефолтах API вендора. Она не отвечает, держит ли
   модель кириллицу, бесшовность, hex, прозрачность, дословность текста. → §2.1, §2.4 [документация]
5. Арена меряет конфигурацию вендора, а не polza: GPT Image 2.5 — режим `max` ($0.211 за 1024²), у polza уровень качества
   не выставлен. Перенос мест на polza — гипотеза до теста 3 фазы 5. → §2.4 [не проверено]
6. Разница < 20 Elo внутри одного диапазона мест (CI ±7…±12) — не различие; «Preliminary» у LMArena (< 10 тыс. голосов у
   Sunburst/Flare, 2,8 тыс. у qwen-image-2.1) — осторожно. → §2.1, §3.1 [документация]
7. Академические бенчмарки 2023–2025 (GenEval, DPG-Bench, OneIG, T2I-CompBench++, TIIF) **отстают на 6–12 месяцев** и частично
   насыщены (GenEval: люди дают топу ≥ 94,8 %); модели 2026 года есть только в живых лидербордах WISE_Verified, T2I-CoReBench
   (генерация), RISEBench, GEditBench v2 (правка); GPT Image 2.5 и Qwen-Image-3.0 — ни в одном. → §4.3, §6.2 [исследование]
8. Лидер академических таблиц 2025 ≠ выбор 2026: Qwen-Image (GenEval 0.87, DPG 88.32 — лучшие) — AA #101, LMArena #63. → §4.2
   [исследование]
9. Текст латиницей: AA Text Rendering — №1 GPT Image 2 (high); LMArena — №1 Sunburst; Nano Banana 2 выше Nano Banana Pro в
   обеих; «текстовые» Ideogram 4.0 и Recraft V4.1 — AA TR #33 и #27–52. → §5.1 [исследование]
10. Посимвольная точность ≠ предпочтение: WeGenBench (zh/en) — лучший текст у Seedream 4.5 (Char F1 0.79), Nano Banana 2 —
    precision 0.43 из-за лишнего текста, хотя в аренах NB2 выше Seedream 4.5 на ~100 Elo. → §5.2, §9 [исследование]
11. Кириллица: генерацию русского текста независимо мерит только LingT2I (ACM MM 2026; модели 2025 года): русский 0.29 против
    0.67 у английского в среднем, «Nano Banana» 0.47 против 0.68 — текст читаемый, но не тот. Правку — MultiTextEdit
    (12 языков): №1 Nano Banana 2 (SemAvg 4.006, разрыв EN/не-EN 0.100). Модели 2026 года на русском никто не мерил → тест 1
    фазы 5. → §5.2 [исследование]
12. OCR путает кириллицу с латинскими двойниками (MDPBench, ScriptMoE) → кириллицу мерить посимвольно по кодовым точкам после
    OCR с языком ru или VLM-судьёй с трассировкой (как LSF в MultiTextEdit). → §5.3 [исследование]
13. Правка: топ AA и LMArena совпадает (Sunburst, Flare, затем MAI-2.6 / Grok 2.0); FLUX.2 в правке заметно слабее, чем в
    генерации (AA правка #37–45). Лучший не-OpenAI из polza в правке — Seedream 5.0 Pro (AA #8) и Nano Banana 2 (#9; правка
    текста #5). → §6 [исследование]
14. GEditBench v2 разделяет «выполнил» и «не тронул лишнее»: GPT Image 1.5 — лучший в первом (1260) и худший во втором (846);
    пиксельную сохранность давать маской или композитингом. → §6.2 [исследование]
15. Серии: ViStoryBench (живой, 29.08.2026) — Nano Banana Pro №1, Nano Banana №2, GPT-4o #9, Seedream 4.0 #17; OmniRef-Bench
    (2–7 референсов) — NB Pro 8.50 > Seedream 4.5 8.13 > FLUX.2 [klein] 6.49. GPT Image 1.5/2/2.5 и NB2 в них нет; в арене
    (AA Identity Preserving) №1 — GPT 2.5 → прямое сравнение — тест 5. → §7 [исследование]
16. UI-состояния: GEBench — Nano Banana Pro №1 (69.62 CN / 61.20 EN), попадание по координате < 10 % у большинства моделей
    → геометрию UI задавать кодом, не промтом. → §8 [исследование]
17. Заявления «№1» устаревают за дни: Microsoft (04.09.2026) «No. 1 for image editing» — через 4 дня GPT Image 2.5; xAI
    «second in the world» (07.08.2026) — сейчас #4–5. Всегда смотреть дату снимка. → §9 [исследование]
18. Арены хранят мёртвые модели: Imagen 4 Ultra (AA #43, LMArena #34) выключена в Google API 17.08.2026; Midjourney V8.x в
    аренах нет вообще («No API available»). → §1.1, §9 [документация]
19. За 12 месяцев сменились все флагманы: GPT Image 1 → 1.5 → 2 → 2.5; Nano Banana → Pro → 2 → 2 Lite; Seedream 4.0 → 4.5 →
    5.0 Lite → 5.0 Pro; FLUX.1 → FLUX.2; Qwen-Image → 2.0 → 3.0 → 2.1 (веса); Imagen 4 закрыт. Знания агента «по памяти»
    устарели — проверять по §1.2. → §1.2 [документация]

## 1. Ландшафт на 23.09.2026

### 1.1 Вендоры и актуальные модели

| Вендор | Актуальные модели картинок | В polza (id) | Статус / примечание |
|---|---|---|---|
| OpenAI | GPT Image 2.5 Sunburst, 2.5 Flare (08.09.2026); GPT Image 2 (21.04.2026) | `openai/gpt-image-2.5-sunburst`, `gpt-image-2-5-flare`, `openai/gpt-5.4-image-2` | лидеры обеих арен; 1.5 / 1 / 1-mini выключаются 01.12 / 23.10 / 01.12.2026 [S7], [S8] |
| Google | Nano Banana Pro (`gemini-3-pro-image`), Nano Banana 2 (`gemini-3.1-flash-image`), 2 Lite (30.06.2026) | `google/gemini-3-pro-image-preview`, `…3.1-flash-image(-preview)`, `…3.1-flash-lite-image`, `…2.5-flash-image` | GA 28.05.2026; preview-имена выключены 25.06.2026; Imagen 4 выключен [S13], [S15] |
| ByteDance Seed | Seedream 5.0 Pro (08.07.2026), 5.0 flash, 5.0 Lite, 4.5, 4.0 | 5.0 Pro, 5.0 Lite, 4.5, 4.0 | 5.0 flash в polza нет [S20], [S21] |
| Black Forest Labs | FLUX.2 [pro], [flex], [max], [klein] 4B/9B, [dev]; Tools (Outpainting, Erase, Deblur, VTO) | `flux.2-pro`, `flux.2-flex` | FLUX 3 анонсирован 23.07.2026, выпущено только видео [S18] |
| Alibaba | Qwen-Image-3.0 / 3.0-Pro (07.2026, API), Qwen-Image-2.1 (веса 20.09.2026), Wan 2.7 image; Z-Image (Tongyi-MAI) | `qwen/image-2.1`, `qwen/image-2`, `qwen/image`, `tongyi-mai/z-image` | 3.0-Pro в polza нет [S23], [S24], [S25] |
| xAI (SpaceXAI) | Grok Imagine Image 2.0 (07.08.2026), grok-imagine-image-quality (05.2026), grok-imagine-image (01.2026) | `x-ai/grok-imagine-image` (базовая) | 2.0 в polza нет [S27], [S28] |
| Microsoft AI | MAI-Image-2.6 и 2.6-Flash (Foundry preview 04.09.2026) | — | AA #5 при $38.9/1k [S32] |
| Meta | Muse Image (07.07.2026) | — | только продукты Meta в США; Content Seal [S33] |
| Recraft | V4.1 (14.05.2026), V4 Styles (08.2026), V4 | — | вектор, `style_id`, палитра в API [S30] |
| Ideogram | 4.0 (06.2026; открытые веса 9.3B + API) | — | JSON-нативная, bbox для текста [S31] |
| Midjourney | V8.2 (по умолчанию с 24.07.2026), Niji 7 | — | официального API нет [S34], [S50] |
| Tencent | HunyuanImage 3.0 / Instruct | — | лицензия не действует в ЕС, UK, Южной Корее [S35] |
| Topaz Labs | Gigapixel, Wonder, Bloom и др. (апскейл) | `topaz/image-upscale` | модель внутри polza не указана [S29] |
| Reve | Reve 2.0, 2.1 | — | LMArena #6 и #8; первоисточники не изучались |

### 1.2 Хронология: что изменилось за 12 месяцев (сентябрь 2025 → сентябрь 2026)

| Дата | Событие | Источник |
|---|---|---|
| 2025-09 | Seedream 4.0; 22.09 — Qwen-Image-Edit-2509; 28.09 — HunyuanImage 3.0 (веса) | [S36], [S23], [S35] |
| 2025-10-02 | Gemini 2.5 Flash Image (Nano Banana) GA; 10.2025 — GPT Image 1 Mini | [S13], [S36] |
| 2025-11-20 | Nano Banana Pro (`gemini-3-pro-image-preview`) | [S13] |
| 2025-11-25 / 26 | FLUX.2 [pro] и [flex] (+ [dev]); Z-Image-Turbo (Apache 2.0) | [S18], [S25] |
| 2025-12 | Seedream 4.5; 16.12 — GPT Image 1.5 и FLUX.2 [max]; 17.12 — Qwen-Image-Layered, Edit-2511; 30.12 — Qwen-Image-2512 | [S36], [S4], [S18], [S23] |
| 2026-01 | grok-imagine-image; 15.01 — FLUX.2 [klein] 4B/9B; 26.01 — HunyuanImage 3.0 Instruct; 27.01 — Z-Image (база) | [S36], [S18], [S35], [S25] |
| 2026-02 | Recraft V4; Seedream 5.0 Lite; 26.02 — Nano Banana 2 (`gemini-3.1-flash-image-preview`) | [S30], [S20], [S13] |
| 2026-03 | 03.03 — qwen-image-2.0 и 2.0-pro; MAI-Image-2; 17.03 — Midjourney V8.0 alpha | [S24], [S32], [S34] |
| 2026-04 | 14.04 — Midjourney V8.1 (HD 2K); **21.04 — GPT Image 2** (гибкие размеры, токенная цена, Batch −50 %) | [S34], [S7] |
| 2026-05 | grok-imagine-image-quality; 14.05 — Recraft V4.1 и BFL Outpainting; 21.05 — FLUX Erase; **28.05 — GA Nano Banana Pro и 2** | [S36], [S30], [S18], [S13] |
| 2026-06 | MAI-Image-2.5; Ideogram 4.0 (открытые веса); 15.06 — Imagen 4 объявлен устаревшим; **25.06 — выключены preview-модели Gemini image**; 30.06 — Nano Banana 2 Lite; Vertex прекращает Imagen 4 | [S32], [S31], [S13], [S15] |
| 2026-07 | 07.07 — Muse Image (Meta); **08.07 — Seedream 5.0 Pro**; Qwen-Image-3.0 и 3.0-Pro; MAI-Image-2.5-Pro; 23.07 — анонс FLUX 3 (сначала видео); 24.07 — Midjourney V8.2 по умолчанию | [S33], [S20], [S24], [S18], [S34] |
| 2026-08 | **07.08 — Grok Imagine Image 2.0**; 10.08 — MAI-Image-2.6; **17.08 — Imagen выключен в Gemini API**; 20.08 — прозрачный фон у GPT Image 2 (preview); Recraft V4 Styles | [S28], [S32], [S13], [S7], [S30] |
| 2026-09 | 04.09 — MAI-Image-2.6 и 2.6-Flash в Foundry; **08.09 — GPT Image 2.5 Sunburst и Flare**; 10.09 — они в polza; 11.09 — cookbook-гайд GPT Image 2 архивирован; **20.09 — Qwen-Image-2.1 (веса)**, 21.09 — в polza | [S32], [S7], [S1], [S9], [S23] |
| впереди | 23.10.2026 — выключение gpt-image-1 (`openai/gpt-5-image`); 01.12.2026 — gpt-image-1.5 и gpt-image-1-mini | [S8] |

Выводы по хронологии:
- Средний срок жизни флагмана — 3–5 месяцев (GPT Image 1.5 → 2 — 4 месяца; 2 → 2.5 — 4,5 месяца; Nano Banana Pro → 2 —
  3 месяца). Карточка без даты проверки устаревает за квартал.
- Предпросмотровые id исчезают: Google выключил `-preview` через 4 недели после GA; в polza старые имена остались.
- Открытые веса догоняют закрытые медленно: лучшие открытые в AA t2i — Ideogram 4.0 (Quality) #33, FLUX.2 [dev] #40,
  Qwen Image Max 2512 #42; Z-Image Turbo #74, FLUX.2 [klein] 9B #76; Qwen-Image-2.1 в LMArena — #17 (предварительно), в AA
  ещё нет.

### 1.3 Эшелоны на 23.09.2026 (по двум аренам)

| Эшелон | Модели | AA t2i (Elo) | LMArena t2i |
|---|---|---|---|
| 1 | GPT Image 2.5 Sunburst, 2.5 Flare, GPT Image 2 | 1197 / 1191 / 1171 | 1423 / 1401 / 1381 |
| 2 (вне polza) | Grok Imagine Image 2.0, MAI-Image-2.6, Muse Image, Reve 2.1 | 1150 / 1147 / 1113 / — | 1302 / 1334 / 1276 / 1301 |
| 2–3 (polza) | Nano Banana 2, GPT Image 1.5, Nano Banana Pro, Nano Banana 2 Lite, Seedream 5.0 Pro | 1122 / 1103 / 1100 / 1092 / 1079 | 1260 / 1239 / 1246 / 1250 / 1256 |
| 3 | Qwen-Image-3.0-Pro, FLUX.2 [flex]/[max]/[pro], Seedream 4.0/4.5, Recraft V4.1 Utility, grok-imagine-image, Ideogram 4.0 | 1089 … 1002 | 1254 … 1147 |
| 4 | Seedream 5.0 Lite, Nano Banana (2.5), Qwen Image 2.0, Z-Image Turbo, FLUX.2 [klein], Qwen-Image, Midjourney v7 | 1008 … 878 | 1138 … 1057 |

## 2. Artificial Analysis Image Arena

### 2.1 Что меряет и как [S38]

- Слепые попарные сравнения людей по одному промту; Bradley-Terry → шкала Elo; якорь FLUX.2 [dev] = 1000.
- Генерация с **дефолтами API вендора**, 1:1, seed 42, одна картинка, в максимальном поддерживаемом разрешении с уменьшением
  до 1024×1024. Промты — **только английские**, «plain natural language, a single positive prompt with the negative-prompt
  field left empty». Промты ротируются ежемесячно.
- Таксономия t2i: 10 use case (Marketing & Advertising, Retail & E-commerce, Live-Action Film, Animation & Gaming,
  Architecture & Real Estate, Productivity & Knowledge Work, UI/UX Design, Consumer, Social Media & Creator Content, Frontier)
  × 9 capability (Reasoning, Knowledge, Text Rendering, Layout, Complex Compositions, Lighting, Material, Physics, Human
  Anatomy). Правка: те же use case + 7 действий (Object-Level, Scene & Style, Enhancement & Restoration, Composition &
  Framing, Identity Preserving, Text or Symbol, Reasoning-Based).
- Цена в таблице — «cost to generate 1,000 images on the model creator's API at 1024x1024 with the model's default settings»;
  время — медиана за 3 дня (us-central1), водяные знаки и safety выключены, где можно.
- Снимок: 23.09.2026, 160 моделей в t2i и 76 в правке; категории — отдельные наборы промтов (20–140 моделей в срезе)
  [проверено].

### 2.2 Общий рейтинг (23.09.2026)

| # | t2i (Elo · $/1k) | # | Правка (Elo) |
|---|---|---|---|
| 1 | GPT Image 2.5 Sunburst (max) 1197 · 210,7 | 1 | GPT Image 2.5 Sunburst (max) 1179 |
| 2 | GPT Image 2.5 Flare (max) 1191 · 210,7 | 2 | GPT Image 2.5 Flare (max) 1159 |
| 3 | GPT Image 2 (high) 1171 · 211 | 3 | MAI-Image-2.6 1131 |
| 4 | Grok Imagine Image 2.0 1150 · 60 | 4 | MAI-Image-2.6-Flash 1123 |
| 5 | MAI-Image-2.6 1147 · 38,9 | 5 | GPT Image 2 (high) 1121 |
| 6 | Nano Banana 2 1122 · 67 | 6 | Muse Image 1115 |
| 7 | Muse Image 1113 · 10 | 7 | MAI-Image-2.5 1112 |
| 8 | GPT Image 1.5 (high) 1103 · 133 | 8 | Seedream 5.0 Pro 1105 |
| 9 | MAI-Image-2.5 1103 · 48,1 | 9 | Nano Banana 2 1105 |
| 10 | Nano Banana Pro 1100 · 134 | 11 | Grok Imagine Image 2.0 1104 |
| 13 | Nano Banana 2 Lite 1092 · 33,6 | 12 | GPT Image 1.5 (high) 1102 |
| 14 | Qwen-Image-3.0-Pro 1089 · 40 | 13 | Nano Banana Pro 1096 |
| 15 | Seedream 5.0 Pro 1079 · 90 | 16 | Qwen-Image-3.0-Pro 1074 |
| 20 / 21 | FLUX.2 [flex] 1026 · 60 / Seedream 4.0 1026 · 30 | 17 | grok-imagine-image 1068 |
| 24 / 25 | FLUX.2 [max] 1022 · 70 / Seedream 4.5 1021 · 40 | 20 | Seedream 5.0 Lite 1054 |
| 27 / 28 | Recraft V4.1 Utility 1021 · 35 / grok-imagine-image 1019 · 20 | 23 | Nano Banana 2 Lite 1041 |
| 33 / 36 | Ideogram 4.0 (Quality) 1011 · 100 / Seedream 5.0 Lite 1008 · 35 | 28 | Seedream 4.5 1035 |
| 39 / 40 | FLUX.2 [pro] 1002 · 30 / FLUX.2 [dev] 1000 | 33 | Seedream 4.0 1012 |
| 43 / 51 | Imagen 4 Ultra 997 (выключена) / Nano Banana (2.5) 985 | 37 / 38 | FLUX.2 [pro] 1006 / [flex] 1005 |
| 68 / 74 | Qwen Image 2.0 960 / Z-Image Turbo 942 · 5 | 45 / 46 | FLUX.2 [max] 995 / Nano Banana (2.5) 986 |
| 101 / 108 | Qwen Image (исходная) 886 / Midjourney v7 Alpha 878 | 54 | Qwen Image 2.0 961 |

Время (медиана, 1024²): Z-Image Turbo 2,1 с; Nano Banana 2 Lite 3,1 с; klein 4B 3,4 с; Nano Banana 2 8,9 с; FLUX.2 [pro]
10,9 с; Nano Banana Pro 17,0 с; Muse 18,6 с; FLUX.2 [max] 24,8 с; Flare (max) ≈ 56 с; Sunburst (max) ≈ 108 с (числа сняты с
графика по порядку сортировки — [исследование], перепроверять при переиспользовании).

### 2.3 Категории: где меняется лидер

Полные таблицы — `99-raw/experiments/C1/03-…/analyze-output.txt`, сводка — `06-…/category-leaders.txt`.

| Срез AA | №1 | Лучший не-OpenAI | Лучший не-OpenAI из polza | Что важно для сайтов |
|---|---|---|---|---|
| All t2i | Sunburst 1197 | Grok 2.0 #4 1150 | Nano Banana 2 #6 1122 | — |
| UI/UX Design | **Flare 1229** | Grok 2.0 #4 1181 | NB2 #6 1167 | мокапы интерфейсов: Flare > Sunburst |
| Marketing & Advertising | **Flare 1175** | MAI-2.6 #4 1162 | NB2 #6 1112 | NB2 Lite #9 выше NB Pro #13 |
| Retail & E-commerce | Sunburst 1200 | MAI-2.6 #3 1148 | NB2 #7 1101 | продукт: GPT 2.5, затем MAI |
| Live-Action Film | Sunburst 1227 | MAI-2.6 #4 1142 | NB2 #6 1122 | фото hero |
| Animation & Gaming | **Flare 1211** | **Grok 2.0 #2 1186** | NB2 #7 1139 | иллюстрация |
| Productivity & Knowledge | **GPT Image 2 (high) 1229** | Grok 2.0 #2 1199 | **NB Pro #6 1154** | инфографика, слайды |
| Text Rendering | **GPT Image 2 (high) 1195** | Grok 2.0 #3 1167 | NB2 #8 1106 | Sunburst лишь #4 |
| Layout | Sunburst 1244 | MAI-2.6 #4 1182; **Qwen-3.0-Pro #5 1175** | NB2 #10 1142 | вёрстка на картинке |
| Knowledge | **Grok Imagine Image 2.0 1204** | — | NB Pro #7 1127 | единственный срез без OpenAI на №1 |
| Reasoning | GPT Image 2 (high) 1202 | Grok 2.0 #4 1163 | NB2 #7 1141 | — |
| Lighting / Material | Sunburst 1176 / 1179 | MAI-2.6 #3 | NB2 #8 / #6 | Seedream 5.0 Pro #11 — выше NB Pro |
| Human Anatomy | Sunburst 1225 | Grok 2.0 #4 1149 | NB2 #6 1135 | люди на hero |
| Правка All | Sunburst 1179 | MAI-2.6 #3 1131 | **Seedream 5.0 Pro #8 1105** | NB2 #9 1105 — вровень |
| Text or Symbol Edits | Sunburst 1191 | MAI-2.6 #3 1153 | **NB2 #5 1143** | Qwen-3.0-Pro #6 1133 |
| Identity Preserving Edit | Sunburst 1209 | Muse #4 1154 | Seedream 5.0 Pro #8 1146 | серии с персонажем/продуктом |
| Composition & Framing | Sunburst 1218 | MAI-2.6 #4 1135 | NB2 #8 1109 | ≈ аутпейнт и рекадрирование |
| Enhancement & Restoration | Sunburst 1115 | MAI-2.6 #2 1097 | Seedream 5.0 Pro #9 1047 | **Seedream 5.0 Lite #11 1043 (4 ₽) выше NB2 #19 и NB Pro #22** |
| Scene & Style Edit | Sunburst 1164 | Muse #3 1137 | NB Pro #10 1113 | Wan 2.7 Pro #7 |

### 2.4 Ограничения AA для задач сайта

1. Только английские промты → **о кириллице ничего** [S38].
2. Дефолты вендора и максимальный режим (GPT 2.5 — `max`, $0.211 за картинку) ≠ конфигурация polza (уровень не выставлен).
3. 1:1 и уменьшение до 1024² → не видно поведения на 21:9, 8:1, 4K и мелкого текста в 4K.
4. Голос «что лучше» не проверяет дословность текста, попадание в hex, прозрачность, бесшовность, повторяемость серии.
5. Цены — у вендора; у polza свои (плоские для mie).
6. Reference-to-Image (мульти-референс) — «upcoming», сейчас не меряется [S38].

## 3. LMArena (Text-to-Image и Image Edit)

### 3.1 Что меряет [S39], [S40]

- Слепые пары, голосуют посетители; рейтинг с CI; «Preliminary» — мало голосов. Стиль-контроль включён по умолчанию.
- t2i: 6 258 152 голоса, 79 моделей, снимок 21.09.2026; 8 категорий (Overall; Product, Branding & Commercial Design; 3D
  Imaging & Modeling; Cartoon, Anime & Fantasy; Photorealistic & Cinematic Imagery; Art; Portraits; Text Rendering).
- Правка: 29 902 508 голосов, 56 моделей; надёжно снято 5 срезов (Overall, Cartoon, Photorealistic, Portraits, Text
  Rendering) — Product, 3D, Art, Multi Image Edit при съёмке не обновились [проверено].
- Модели участвуют в конкретных режимах: `gpt-image-2 (medium)`, `grok-imagine-image-2.0 (low)`, `gemini-3-pro-image-2k`,
  `gemini-3.1-flash-image [web-search]`; методика промтов не опубликована так подробно, как у AA.

### 3.2 Результаты

| Срез LMArena | №1 | Лучший не-OpenAI | Лучший не-OpenAI из polza |
|---|---|---|---|
| Overall t2i | Sunburst 1423 | MAI-2.6 #4 1334 | Nano Banana 2 #9 1260 |
| Product, Branding & Commercial | Sunburst 1415 | MAI-2.6 #4 1342 | NB2 #8 1269 |
| 3D Imaging & Modeling | Sunburst 1414 | MAI-2.6 #4 1327 | NB2 #7 1255 (Seedream 5.0 Pro #8 1253) |
| Cartoon, Anime & Fantasy | Sunburst 1443 | MAI-2.6 #4 1349 | **Seedream 5.0 Pro #10 1271** |
| Photorealistic & Cinematic | Sunburst 1427 | MAI-2.6 #4 1328 | **Seedream 5.0 Pro #9 1278** |
| Art | Sunburst 1384 | MAI-2.6 #4 1336 | **Seedream 5.0 Pro #9 1265** |
| Portraits | Sunburst 1459 | Grok 2.0 #4 1352 | **Seedream 5.0 Pro #8 1293** |
| Text Rendering | Sunburst 1466 | MAI-2.6 #4 1370 | NB2 #9 1293 |
| Правка Overall | Sunburst 1526 | Grok 2.0 #4 1430 | Seedream 5.0 Pro #8 1394 |
| Правка Text Rendering | Sunburst 1583 | Grok 2.0 #4 1464 | NB2 #6 1443 |

Прочее из LMArena: Reve 2.1 — #6 (1301), Reve 2.0 — #8; Ideogram 4.0 quality — #18 (1204); Recraft V4.1 Utility Pro — #24;
FLUX.2 [max]/[flex]/[pro] — #26/#28/#29 (1162/1157/1154); HunyuanImage 3.0 — #32; Imagen 4 Ultra — #34; Z-Image Turbo — #56;
Qwen-Image-2.1 — #17 (1228, предв., 2843 голоса); Midjourney — нет.

### 3.3 Сверка двух арен

| Вывод | AA | LMArena | Итог |
|---|---|---|---|
| Топ-3 — OpenAI | да | да | **сходится** |
| Sunburst ≥ Flare | да (1197/1191, в пределах CI) | да (1423/1401) | сходится; в UI/UX, Marketing, Animation AA ставит Flare выше |
| Текст: GPT Image 2 против 2.5 | GPT 2 (high) №1, Sunburst #4 | Sunburst №1, GPT 2 (medium) #3 | **расходится** (разные режимы и наборы промтов) |
| NB2 выше NB Pro | да (#6 против #10; TR #8 против #11) | да (#9 против #14; TR #9 против #13) | **сходится**, вопреки позиционированию Google |
| Seedream 5.0 Pro | #15 t2i, #8 правка | #10 t2i; #8–9 в фото, портретах, Art | сильнее в LMArena-категориях «красоты», чем в AA |
| Reve 2.x | нет в текущей когорте AA | #6, #8 | только LMArena |
| MAI-Image-2.6 | #5 | #4 | сходится |

## 4. Академические бенчмарки следования промту и композиции

### 4.1 Что есть и насколько свежо

Числа ниже — из техотчёта Z-Image (Tongyi-MAI, arXiv 2511.22699) [S26]: таблицы вендора, модели 2025 года. Моделей
2026 года (GPT Image 2/2.5, Nano Banana 2/Pro, Seedream 4.5/5, FLUX.2) в этих таблицах нет.

| Бенчмарк | Что меряет | Лидеры (2025) | Ограничение |
|---|---|---|---|
| GenEval | объекты, счёт, цвет, позиция, атрибуты (детектор) | Qwen-Image 0.87; Z-Image, Seedream 3.0, GPT Image 1 — 0.84; FLUX.1 dev 0.66 | **насыщен**: топ ≥ 0.84 |
| DPG-Bench | плотные длинные промты | Qwen-Image 88.32; Seedream 3.0 88.27; Z-Image 88.14; GPT Image 1 85.15 | близко к потолку |
| OneIG-Bench (EN / ZH) | alignment, text, reasoning, style, diversity | EN: Z-Image 0.546, Qwen-Image 0.539, GPT Image 1 0.533, Seedream 3.0 0.530, Imagen 4 0.515, Recraft V3 0.502; ZH: Qwen-Image 0.548 | модели 2025; GPT Image 1 лучший в reasoning 0.345 и style 0.462 |
| TIIF-Bench testmini | следование инструкциям, короткие/длинные | GPT Image 1 89.15; Qwen-Image 86.14; Seedream 3.0 86.02; Z-Image 80.20 | v2 (ECCV 2026) — таблица лидерборда не извлеклась [S46] |
| PRISM-Bench | 7 треков, судья Qwen2.5-VL-72B | GPT-Image-1 80.7; Gemini 2.5 Flash Image 80.4; Z-Image-Turbo 77.4 | судья — VLM |
| Alibaba AI Arena (конец 2025) | Elo голосов | Imagen 4 Ultra Preview 1048; gemini-2.5-flash-image-preview 1046; Seedream 4.0 1039; Z-Image-Turbo 1025 | снимок вендора отчёта |

### 4.2 Почему не выбирать модель по академическим таблицам

- Отставание 6–12 месяцев: к моменту публикации лидеры сменились (§1.2).
- Насыщение: GenEval/DPG почти не различают топ.
- Инверсия: Qwen-Image — лучший GenEval/DPG/OneIG-ZH 2025 года — в AA 2026 #101 (886), в LMArena #63.
- Таблицы часто в отчёте вендора сравниваемой модели (Z-Image) — [исследование], но не независимое.

### 4.3 Преемники и живые лидерборды (сверено по первоисточникам 23.09.2026)

| Бенчмарк | Год · выборка · судья | Что меряет | Лидеры (дата) | Модели 2026? | Ограничения |
|---|---|---|---|---|---|
| T2I-CompBench++ [S51] | TPAMI 2025 · 8000 промтов (2400 test), EN · BLIP-VQA, UniDet (+глубина), CLIPScore, GPT-4V | привязка цвета, формы, текстуры; 2D/3D-расположение; отношения; счёт; сложные сцены | SD3 (color 0.8132, texture 0.7334, 3D 0.4084), DALL·E 3 (shape 0.6205, complex 0.3773), FLUX.1-schnell (numeracy 0.6185) | нет (≤ 2024) | судьи устарели; общего балла нет; лидерборд не ведётся |
| GenEval [S52] | NeurIPS 2023 · 553 промта × 4 · Mask2Former + CLIP | объекты, счёт, цвет, позиция, привязка цвета | 2025: Qwen-Image 0.87; топ ≥ 0.84 | нет | **насыщен**: люди ставят сильнейшим ≥ 94,8 %, автооценка занижает до 17,7 п.п. (аудит GenEval 2) |
| GenEval 2 [S53] | 12.2025 · 800 промтов (3–10 «атомов») · Soft-TIFA, судья Qwen3-VL-8B | композиционная сложность | Gemini 2.5 Flash Image 44.6 (люди 31.0); Qwen-Image 33.8 (26.8); с переписыванием промта (люди) Qwen-Image 35.8 | нет | 8 моделей; не насыщен |
| GenEval++ [S54] | 08.2025 · 280 промтов · GPT-4.1 | чек-лист «всё или ничего» | GPT-4o 0.739; Echo-4o 0.679 | нет | бенчмарк авторов модели |
| WISE → WISE_Verified [S55] | ICML 2026 · 1000 промтов (культура 400) · Verified: судья Qwen3.5-35B-A3B, 29 моделей | знание мира: объект описан косвенно | 26.06.2026: Qwen-Image-Agent 0.902; Nano Banana Pro 0.876; SenseNova-U1 (CoT) 0.834; GPT-Image-1.5 0.825; Qwen-Image-2.0 0.795; FLUX.2-dev 0.565; Qwen-Image-2512 0.499; Z-Image 0.453; HunyuanImage-3.0 0.435 | частично | нет GPT Image 2/2.5, NB2, Seedream; старые баллы (GPT-4o-судья) и Verified несопоставимы |
| T2I-ReasonBench [S56] | ACL 2026 Findings · 800 промтов · Gemini-2.5-pro | идиомы, дизайн картинок с текстом, сущности, наука | Nano Banana 89.5; GPT-Image-1 86.3; Qwen-Image 67.5 | нет | близок к потолку; версии с разными судьями несопоставимы |
| R2I-Bench [S57] | EMNLP 2025 · 3068 промтов · GPT-4o | рассуждение, 7 категорий | gpt-image-1 0.77; DALL·E 3 0.71 | нет | только EN; модели ≤ 04.2025 |
| OneIG-Bench [S58] | NeurIPS 2025 · EN 1120 / ZH 1320 · GPT-4o + Qwen2.5-VL-7B | соответствие, текст, рассуждение, стиль, разнообразие | 19.09.2025: Seedream 4.0 0.894 / текст 0.981; Qwen-Image 0.882 / 0.891; Nano Banana 0.878 / 0.894; текст ZH: Seedream 4.0 0.982, Nano Banana 0.276 | нет | заморожен с 19.09.2025; метрика текста у потолка |
| DPG-Bench [S59] | 2024 · 1065 плотных промтов (≈ 67 слов) · mPLUG-large | длинные плотные промты | статья: DALL·E 3 83.50; 2025: Qwen-Image 88.32 | нет | потолок ≈ 88 |
| **T2I-CoReBench** [S65] | ICLR 2026 · судья Gemini 2.5 Flash | композиция и рассуждение | **Nano Banana 2 85.3; Nano Banana Pro 85.0; GPT-Image-1.5 78.2; Seedream 4.5 77.0** | **да** | нет GPT Image 2/2.5; судья — модель Google (возможный перекос [мнение]) |
| Qwen-Image-Bench [S66] | 05.2026 · VLM-оценщик команды Qwen | общее качество | GPT Image 2 65.23 | да | бенчмарк вендора |

Выводы:
- Модели 2026 года есть только в **живых** лидербордах: WISE_Verified и T2I-CoReBench (генерация), RISEBench и GEditBench v2
  (правка, §6.2). GPT Image 2.5 и Qwen-Image-3.0 не найдены ни в одном академическом бенчмарке.
- Где есть обе стороны, картина согласуется с аренами: NB2 и NB Pro выше GPT-Image-1.5 (T2I-CoReBench 85.3 / 85.0 против
  78.2; WISE_Verified 0.876 против 0.825); сравнения с GPT Image 2/2.5 нет.
- Смена судьи (GPT-4o → Qwen3.5, Gemini 2.5) делает версии одного бенчмарка несопоставимыми — цитировать с версией и датой.
- Для ориентира в 2026 году: WISE_Verified и T2I-CoReBench (генерация), RISEBench и GEditBench v2 (правка) — но все без
  флагманов OpenAI сентября 2026.

## 5. Текст в картинке

### 5.1 Латиница

| Источник | Лидеры | Замечания |
|---|---|---|
| AA Text Rendering (65 моделей) | GPT Image 2 (high) 1195; Flare 1179; Grok 2.0 1167; Sunburst 1161; MAI-2.6 1141; GPT 1.5 1111; MAI-2.6-Flash 1109; NB2 1106 | NB Pro #11 1081; Qwen-3.0-Pro #10 1082; FLUX.2 [flex] #22 1006; Ideogram 4.0 #33 988; Recraft V4.1 Utility Pro #27 996; FLUX.2 [pro] #41 975 |
| LMArena Text Rendering | Sunburst 1466; Flare 1436; GPT 2 1423; MAI-2.6 1370; Grok 2.0 1344 | NB2 #9 1293; Qwen-3.0-Pro #10 1284; NB Pro 2k #13 1270; qwen-image-2.1 #14 1264; Ideogram 4.0 #18 1238 |
| CVTG-2K (2–5 областей текста, Word Accuracy) [S26] | Z-Image 0.8671; Z-Image-Turbo 0.8585; GPT Image 1 0.8569; Qwen-Image 0.8288 | модели 2025 |
| LongText-Bench EN / ZH [S26] | GPT Image 1 0.956 / 0.619; Qwen-Image 0.943 / 0.946; Z-Image 0.935 / 0.936 | GPT Image 1 — лучший EN, слабый ZH |
| WeGenBench Text (zh/en) [S42] | Seedream 4.5 Char F1 0.79; GPT-Image-2 0.56; NB2 0.49 | лишний текст штрафуется |
| Ideogram 4.0 (вендор) [S31] | X-Omni EN OCR 0.97 | [мнение вендора] |

### 5.2 Многоязычный текст и кириллица

**MultiTextEdit** (Cheng et al., HIT; arXiv 2605.08163 v2, май 2026) [S41] — один из двух найденных бенчмарков с русским
(второй — LingT2I, ниже; MultiTextEdit — правка): 3600 примеров = 300 постеров Canva × 12 языков (ar, bn, zh, nl, en, he, ja, ko, **ru**, es, vi, yo), 5 доменов,
7 операций правки текста; судья — LVM (5 измерений 0–5 + Language/Script Fidelity; QWK 0.76 с носителями).
- Итог SemAvg: **Nano Banana 2 4.006** (EN 4.098 / не-EN 3.997, разрыв 0.100 — минимальный среди сильных); GPT-image-1.5
  3.577 (разрыв 0.517); Qwen-Image-Edit-2511 3.214; FireRed-Image-Edit-1.1 3.204; Step1X-Edit 2.802; FLUX.1-Kontext-dev 2.401.
- Русский (среднее по 12 моделям): SemAvg 2.440, ΔSem 0.542, ΔTA 0.716, **ΔLSF 1.038** — на уровне корейского; хуже только
  иврит, арабский, бенгали; испанский и голландский теряют ~0.18.
- Ограничения: только **правка** (не генерация с нуля); из закрытых — лишь GPT-image-1.5 и NB2; нет GPT Image 2/2.5,
  Seedream, Qwen 3.0.

**LingT2I** (ACM MM 2026; arXiv 2608.11002 v1, 11.08.2026; RISys-Lab/LingT2I) [S67] — единственный найденный независимый
бенчмарк **генерации** текста с русским: 10 языков (EN, ZH, HI, ES, AR, FR, PT, **RU**, JA, KO), 3000 промтов (300 на язык),
короткие строки (≈ 3 токена) внутри английского описания сцены; перевод — Gemini 2.5 Pro (5 % проверено носителями, 98 %
совпадения); метрика — среднее посимвольной и пословной нормированной редакционной дистанции и точного совпадения; OCR —
Gemini 2.5 Flash; одна картинка на промт, seed 42.

| Модель (2025) | RU | EN |
|---|---|---|
| EasyText (специализированная) | 0.59 | 0.87 |
| «Nano Banana» (версия не указана) | **0.47** | 0.68 |
| Qwen-Image | 0.32 | 0.69 |
| AnyText2 | 0.14 | 0.56 |
| FLUX.1-Krea | 0.09 | 0.65 |
| Среднее общих моделей | 0.29 | 0.67 |

- Типичная ошибка на русском — **читаемый, но не тот текст**: у Nano Banana точность 0.48 при оценке качества текста 0.94;
  в 50 % ошибок (по всем языкам) модель пишет другое слово.
- Нет GPT Image (любой версии), Nano Banana Pro/2, Seedream, FLUX.2, Ideogram, Recraft. Оговорки: машинный перевод, короткие
  строки, один seed, OCR моделью Google при оценке модели Google.
- Устаревшее: Glyph-ByT5-v2 / VisualParagraphy (2024; 100 промтов × 10 языков вкл. русский; своя модель 85–92 % OCR на
  русском; DALL·E 3 и Ideogram 1.0 — лишь примеры) [S69].
- Проверены и **без русского**: OCRGenBench (EN/ZH), STRICT (EN/FR/ZH), MultiBanana (EN/ZH/JA), StyleTextGen (ZH/EN),
  Qwen-Image-Bench (ZH/EN), EasyText v2; RusCode — культурное содержание, не текст на картинке (сверено помощником C1-B).

**WeGenBench** (Tencent Weixin + UESTC + DLUT; arXiv 2606.20100, июнь 2026) [S42]: 4000 промтов (2000 General + 2000 Text),
поровну zh/en; судья Qwen3.5-397B; текстовые метрики Sim_edit, Acc_sen, Score_qua, GNED, Char F1 (VLM «TextPecker» и OCR).
- GPT-Image-2: QA 0.97, COT 8.95, AM 2.84 (лучшие семантика и эстетика), Char F1 0.56.
- Seedream-4.5: QA 0.96, AM 2.81; текст Sim_edit 0.74, **Char F1 0.79** (лучший), рукописный 0.86, сложная вёрстка 0.82,
  двуязычный 0.82.
- Nano-banana-2: QA 0.97, AM 2.77; Sim_edit 0.38, Char F1 0.49, precision 0.43 — «massive hallucinations and typographical
  noise»; сложная вёрстка 0.61.
- Авторы: «Automatic Prompt Enhancement may introduce unprompted text elements… particularly prevalent in closed-source
  commercial models». Отказы API: GPT-Image-2 39 из 2000, Seedream 7, NB2 36 (General). Только zh/en.

**UniGenBench++** (arXiv 2510.18701) [S43]: многоязычность = zh/en; «Nano Banana Pro and Seedream-4.0 excel in Chinese text
rendering». Прочитан частично.

**Заявления вендоров о русском:** Google — ru-RU в списке языков лучшего качества [S10]; Seedream 5.0 Pro/flash — русский
в списке языков промта API и в блоге [S20], [S21]; Qwen-Image-3.0-Pro — «native rendering of 12 languages» без списка [S24];
Ideogram 4.0 — «best-in-class multilingual» без списка [S31]; Recraft V4 — «multi-language» без списка, V3 кириллицу не
рендерит (набор символов) [S30]; Z-Image — en/zh [S25]; Imagen 4 — без русского [S15]; OpenAI — языки не перечислены.

**Публичные русскоязычные тесты** (свидетельства, не истина; оба автора продают доступ к моделям): klerk.ru / Genova AI
(26.08.2026; 4 бизнес-макета, один русский промт, первая генерация, 12 картинок проверены глазами —
`99-raw/experiments/C1/05-cyrillic-public-samples/`) — заданный текст без орфографических ошибок у GPT Image 2, Nano Banana 2 и
Grok Imagine 2.0 (по 4/4), дословно — GPT Image 2 и Grok 4/4, NB2 2/4 (перефразирует, добавляет латинский псевдотекст);
ошибки NB2 и Grok — в мелком тексте, добавленном моделью [S47]. Хабр / StudyAI (≈ 22.09.2026; одно задание, 6 моделей):
GPT Image 2.5 — без заметных ошибок; NB2 и Grok — хорошо; FLUX.2 — пропуск буквы («можжевельник»); Seedream 5.0 — «СОСТАД»;
Midjourney — без кириллицы [S48].

### 5.3 Как мерить кириллицу (для K и фазы 5)

- OCR путает кириллицу с латинскими двойниками: MDPBench §3 — «misclassifying the Cyrillic … as their Latin counterparts»
  [S44]; ScriptMoE/TextMuSS — «Latin-Cyrillic homoglyph confusion is alleviated but not fully solved» [S45].
- При этом OCR кириллицы в целом близок к латинице у ряда моделей (GlotOCR Bench — «comparatively stronger» среди
  нелатинских письменностей) [S68]: OCR-оценка русского пригодна, но с выборочной ручной проверкой и контролем двойников.
- Метрика: OCR с принудительным языком `ru` → нормализация (NFC) → посимвольное сравнение по кодовым точкам с эталоном;
  отдельный флаг «латинская буква внутри русского слова» (А/A, В/B, Е/E, К/K, М/M, Н/H, О/O, Р/P, С/C, Т/T, У/Y, Х/X).
  Альтернатива — VLM-судья с трассировкой (LSF из MultiTextEdit).
- Две метрики, а не одна: точность заданных строк и отсутствие лишнего текста (как precision в WeGenBench).

## 6. Правка

### 6.1 Академические (из техотчёта Z-Image, модели 2025) [S26]

| Бенчмарк | Что меряет | Лидеры |
|---|---|---|
| ImgEdit (9 типов правки, 1–5) | качество выполнения инструкции | UniWorld-V2 4.49; Qwen-Image-Edit-2509 4.35; Z-Image-Edit 4.30; GPT-Image-1 4.20; FLUX.1 Kontext Pro 4.00 |
| GEdit-Bench EN / CN (G_O) | правка по инструкции, судья VLM | EN: UniWorld-V2 7.83; Qwen-Image-Edit-2509 7.54; GPT-Image-1 7.53. CN: FLUX.1 Kontext Pro 1.23 — не понимает китайских инструкций |

### 6.2 KRIS-Bench, GEditBench v2, RISEBench и первоисточники ImgEdit/GEdit

| Бенчмарк | Год · выборка · судья | Что меряет | Лидеры (дата) | Модели 2026? | Ограничения |
|---|---|---|---|---|---|
| KRIS-Bench [S60] | NeurIPS 2025 · 1267 примеров, 22 задачи, 7 измерений · GPT-4o + проверка 12 экспертами | правка, требующая знаний (согласованность, качество, выполнение, правдоподобие) | живой, 06.05.2026: GPT-4o / GPT-Image-1 80.09; Step Image Edit 2 66.16; JoyAI-Image-Edit 63.44; Gemini 2.0 62.41; Qwen-Image-Edit-2511 62.04 | почти нет | нет GPT-Image-1.5/2, Nano Banana, Seedream 4.x, FLUX.2; модели с одним входом получают 0 за задачи «время» |
| ImgEdit-Bench [S61] | NeurIPS 2025 · 811 (734 базовых, 9 задач; 47 сложных; многоходовые) · GPT-4o, 1–5 | выполнение правок | статья: GPT-4o-Image 4.70 (сложные); 2025: UniWorld-V2 4.49 | нет | верх сжат; ImgEdit-Judge совпадает с людьми ≈ 70 % (±1); обновлений 2026 нет |
| GEdit-Bench [S62] | 2025 · 606 реальных запросов, 11 категорий, EN и CN · VIEScore (GPT-4.1, Qwen2.5-VL-72B) | правка по реальным запросам | статья: GPT-4o 7.494; Doubao 6.983; 2025: UniWorld-V2 7.83 | нет | верх в пределах 0,3 балла |
| **GEditBench v2** [S63] | 03.2026 · 1200 запросов, 23 задачи · попарный Elo | правка: выполнение + согласованность | **Nano Banana Pro 1096; Seedream 4.5 1089; GPT Image 1.5 1071** (выполнение 1260 — лучшее, согласованность 846 — худшая); FLUX.2 [klein] 9B 1039; Qwen-Image-Edit-2511 1038 | да | нет GPT Image 2/2.5, NB2; корреляция с Arena ρ = 0.929 |
| **RISEBench** [S64] | NeurIPS 2025 Oral · 360 (время 85, причинность 90, пространство 100, логика 85) · GPT-4.1, только 5/5/5 | правка с рассуждением | живой, 23.04.2026: **GPT-Image-1.5 51,4 %; GPT-Image-2 49,4 %; Nano Banana Pro 48,3 %**; Nano Banana 33,9 %; Seedream 4.0 12,2 % | да | маленький; строгий порог; закрытый судья |

Выводы для правки:
- GEditBench v2 разделяет «выполнил инструкцию» и «не тронул лишнее»: GPT Image 1.5 — лучший в первом и худший во втором
  (1260 против 846). Для правок, где остальное должно остаться неизменным, нужен композитинг или маска, а не только промт
  (совпадает с гайдом OpenAI [S6]).
- В правке с рассуждением (RISEBench) GPT-Image-1.5, GPT-Image-2 и Nano Banana Pro — вровень (48–51 %), Seedream 4.0 — 12 %.
- KRIS-Bench и ImgEdit/GEdit v1 не содержат моделей 2026 года — для выбора сейчас не пригодны.

### 6.3 Арены правки — главное

- AA правка: Sunburst 1179, Flare 1159, MAI-2.6 1131, MAI-2.6-Flash 1123, GPT 2 1121; из polza не-OpenAI — Seedream 5.0 Pro
  #8 и NB2 #9 (1105 оба); FLUX.2 [pro] #37, [flex] #38, [max] #45 — вопреки заявлению BFL о «strongest editing consistency»
  у [max] [S37], [S19].
- Правка текста (Text or Symbol): NB2 #5 1143 — лучший не-OpenAI в polza; Qwen-3.0-Pro #6 1133 (вне polza).
- Сохранение идентичности: Sunburst 1209, Flare 1199, GPT 2 1167, Muse 1154; Seedream 5.0 Pro #8 1146, NB Pro #9 1140, NB2 #11.
- LMArena правка: Sunburst 1526, Flare 1482, GPT 2 1461, Grok 2.0 1430, MAI-2.6 1429; Seedream 5.0 Pro #8, NB Pro 2k #9,
  NB2 #12, qwen-image-2.1 #16 (предв.).

## 7. Серии и консистентность

### 7.1 Что есть на 23.09.2026

- Арены: AA Identity Preserving Edit (69 моделей) — прокси «тот же персонаж/продукт в новой сцене»: Sunburst, Flare, GPT 2,
  Muse, MAI-2.6-Flash, GPT 1.5, MAI-2.6, Seedream 5.0 Pro (#8 1146), NB Pro (#9 1140) [S37].
- AA: отдельный Reference-to-Image бенчмарк — «upcoming» [S38].
- Вендорские инструменты серий: Seedream `sequential_image_generation` (до 15 связанных картинок; 5.0 Lite, 4.5, 4.0 — в
  polza не выставлено) [S21]; Wan 2.7 `enable_sequential` (до 12) [S24]; Recraft V4 Styles `style_id` из 1–10 картинок [S30];
  Nano Banana Pro — до 5 персонажей и 3 стилевых референсов [S10]; Midjourney `--sref` + коды, Moodboards [S34].

### 7.2 Бенчмарки консистентности и мульти-референса (сверено по первоисточникам 23.09.2026)

| Бенчмарк | Год · выборка · судья | Что меряет | Лидеры | Модели 2026? | Ограничения |
|---|---|---|---|---|---|
| **ViStoryBench** [S70] | CVPR 2026 · 80 историй, 344 персонажа, 509 референсов, 1317 кадров, 10 стилей; Lite — 20 историй · 12 метрик (CIDS, CSD, Prompt Alignment — судья Gemini-3-Pro); люди: 20 разметчиков, корреляция self-CIDS 0.80 | серия кадров с персонажами по референсам: сходство персонажа с эталоном и внутри серии, стиль, соответствие | живой, 29.08.2026 (Lite, среднее мест): **1 Nano Banana Pro** (CIDS 0.581/0.653, PA 3.37), **2 Nano Banana**, 3 AIbrm, 4 Doubao, 5 StoryDiffusion; GPT-4o #9; Seedream 4.0 #17 | частично (NB Pro) | нет GPT-Image-1.5/2/2.5, NB2, Seedream 4.5/5, FLUX.2; только персонажи историй; «overall» — среднее мест |
| **OmniRef-Bench** [S71] | 06.2026 · 395 экспертных случаев, 2–7 референсов · судья Gemini 3 Flash + метрики; 40 экспертов (корр. 0.89) | субъект, фон, стиль, свет, поза из разных референсов | **Nano Banana Pro 8.50; Seedream 4.5 8.13**; FLUX.2 [klein] 6.49; Qwen-Image-Edit-2511 4.97 | да | GPT-Image не тестировался; судья — модель Google |
| MultiBanana [S72] | CVPR 2026 · 3769 задач, до 8 референсов · Gemini 2.5 и GPT-5 | мульти-референсная генерация | 1 реф.: Nano Banana 7.817 ≈ GPT-Image-1 7.804; **2 реф.: GPT-Image-1 6.585 против NB 4.891**; Qwen-Image-Edit-2509 разваливается после 3 | нет (версии на 01.2026) | лидерборд — картинка, не читался |
| OmniContext [S73] | 2025–2026 (OmniGen2) · 400 примеров, 8 подзадач · GPT-4.1 | генерация по 1–N референсам (персонажи, объекты, сцены) | GPT-4o 8.80; OmniGen2 7.95; Gemini 2.5 Flash Image 7.84 | нет | результаты не воспроизводятся (OmniGen2: 7.95 / 7.18 / 7.54 в разных статьях) |
| DreamBench++ [S74] | ICLR 2025 · 150 × 9 промтов · GPT-4o | персонализация по одному референсу | официально — модели эпохи SDXL; новый прогон: FLUX.2 [klein] 9B 0.56 | нет | один референс |
| MultiRef-Bench [S75] | ACM MM 2025 · 1990 задач | мульти-референс | Claude/Gemini + SD3.5 | нет | устарел |
| T2IS-Bench [S76] | 2025 · 596 инструкций, 26 подкатегорий (постеры, упаковка, бренд) · Qwen2.5-VL-7B | согласованные наборы 2–8 картинок | Gemini 2.0 Flash 0.509; GPT-4o 0.501 | нет | устарел |

Выводы для серий:
- Для серии с персонажем или продуктом лучший независимый ориентир — ViStoryBench и OmniRef-Bench: обе ставят Nano Banana
  Pro №1; Seedream 4.5 — второй в OmniRef-Bench (8.13) при цене 5 ₽ в polza.
- Флагманов OpenAI 2025–2026 в этих бенчмарках нет, а в арене (AA Identity Preserving) №1 — GPT 2.5 → прямое сравнение
  Flare, NB Pro и Seedream 4.5 — тест 5 фазы 5.
- MultiBanana: качество старых моделей падает с ростом числа референсов (NB при 2 референсах — 4.891 против 7.817 при одном)
  → для серий давать 1 эталон и повторять определяющие детали словами, а не накидывать много референсов [исследование].
- Бенчмарков «стиль серии иллюстраций/иконок» (не персонаж) с моделями 2026 года не найдено.

## 8. UI и макеты

- GEBench (arXiv 2602.09007; по соседнему файлу [S49]): генерация UI-состояний — Nano Banana Pro 69.62/61.20 (CN/EN),
  GPT-image-1.5 63.22/63.16, FLUX.2 [pro] 57.54/51.18, Seedream 4.5 55.91/50.01, Qwen-Image-Edit 33.72/33.01; попадание
  по координате — NB Pro 23,9 %, у большинства < 10 %.
- AA UI/UX Design: Flare 1229, Sunburst 1220, GPT 2 1204, Grok 2.0 1181, MAI-2.6 1169, NB2 1167; AA Layout: Sunburst 1244,
  GPT 2 1219, Flare 1215, MAI-2.6 1182, Qwen-3.0-Pro 1175.
- Вывод: картинка интерфейса — эскиз; реальный UI и настоящий скриншот в мокапе — кодом и композитингом (`03-capabilities-by-task.md` §14).

## 9. Противоречия между рейтингами и заявлениями

| № | Утверждение A | Утверждение B | Как читать |
|---|---|---|---|
| 1 | Google: Nano Banana Pro — «precision creative control», polza — «до 4K с точным текстом» | AA TR: NB2 #8 > NB Pro #11; LMArena TR: #9 > #13 | вендор против двух арен; Pro — ради ролей референсов и знаний, не текста |
| 2 | AA: GPT Image 2 (high) — №1 в тексте | LMArena: Sunburst №1, GPT 2 (medium) #3 | разные режимы и промты; для текста брать GPT 2 или 2.5 — различие в пределах 1–2 мест |
| 3 | Арены: NB2 ≫ Seedream 4.5 | WeGenBench: Seedream 4.5 — лучший текст (Char F1 0.79), NB2 0.49 | предпочтение ≠ посимвольная точность; NB2 штрафуется за лишний текст |
| 4 | BFL: FLUX.2 [max] — «strongest editing consistency» | AA правка #45, LMArena #30 | заявление не подтверждено |
| 5 | Microsoft (04.09): MAI-2.6 «No. 1 for image editing» на AA | с 08.09 №1 — GPT 2.5; MAI-2.6 #3 | заявление устарело через 4 дня |
| 6 | xAI (07.08): Image 2.0 «ranks second in the world» | 23.09: AA #4, LMArena #5 | устарело после GPT 2.5 и MAI-2.6 |
| 7 | AA Animation & Gaming: NB2 #7, Seedream 5.0 Pro #17 | LMArena Cartoon/Art: Seedream 5.0 Pro #9–10 выше NB2 #12–13 | разные наборы промтов; для иллюстраций проверить обе |
| 8 | Academic 2025: Qwen-Image — №1 GenEval/DPG | AA 2026 #101, LMArena #63 | академическое лидерство не переносится |
| 9 | Google Gemini API: 1:4…8:1 только у 3.1 Flash | Vertex: у Pro тоже 1:4…8:1 | документации Google расходятся |
| 10 | Seedream 4.5 (WeGenBench) — лучший текст zh/en | AA TR #30, LMArena TR #38 | см. № 3 |
| 11 | Muse Image — «только продукты Meta в США», API не упомянут | AA — провайдер Meta, $10/1k | [спорно] |
| 12 | AA Identity Preserving: №1 GPT Image 2.5 | ViStoryBench и OmniRef-Bench: №1 Nano Banana Pro | не противоречие, а пробел: GPT 1.5/2/2.5 в специализированных бенчмарках нет → тест 5 |
| 13 | klerk (NB2): русский текст без орфографических ошибок 4/4 | LingT2I («Nano Banana»): русский 0.47; klerk: дословно лишь 2/4 | согласуется: модель пишет читаемо, но не ту строку — мерить дословность, а не «грамотность» |
| 14 | T2I-CoReBench, WISE_Verified: Nano Banana 2/Pro выше GPT-Image-1.5 | AA t2i: GPT 1.5 (1103) ≈ NB Pro (1100) < NB2 (1122) | согласуется в целом; GPT 2/2.5 в этих бенчмарках нет |

## 10. Как пользоваться оценками при выборе модели

1. Сузить по задаче: срез AA/LMArena, ближайший к `IMG-*` (карта — `03-capabilities-by-task.md`).
2. Отсечь недоступное: нет в polza и нет API у P → исключить (Midjourney, Muse).
3. Проверить статус и дату (§1.2): не выключается ли модель в ближайший квартал.
4. Проверить параметры в каталоге polza у конкретного провайдера (прозрачность, маска, соотношения, 4K).
5. Для вопросов, которые арены не меряют (кириллица, hex, альфа, бесшовность, серия), — минимальный тест фазы 5.
6. Пересматривать ежемесячно: AA ротирует промты, лидеры меняются раз в 3–5 месяцев.

## Частые ошибки

1. **Общий Elo как ответ на задачу.** «Лучшая модель» по All t2i ≠ лучшая для текста (Text Rendering), UI (UI/UX), продукта
   (Retail) и правки текста (Text or Symbol).
2. **Академические таблицы 2025 года как рейтинг 2026.** GenEval/DPG/OneIG/TIIF в техотчётах не содержат текущих
   закрытых моделей.
3. **Английская арена как доказательство кириллицы.** Ни AA, ни LMArena русских промтов не содержат.
4. **Предварительный рейтинг как факт.** qwen-image-2.1 #17 — 2843 голоса; Sunburst/Flare — «Preliminary» в LMArena.
5. **Вендорское «№1» без даты.** Заявления MAI и xAI устарели за дни.
6. **Мёртвая модель из арены.** Imagen 4 и DALL·E 3 стоят в таблицах, но недоступны или устарели.
7. **Перенос режима.** Место `GPT Image 2.5 (max)` не описывает polza без `quality`; `gpt-image-2 (medium)` в LMArena ≠
   `high` в AA.
8. **Одна метрика текста.** Без штрафа за лишний текст NB2 выглядит лучше, чем есть (WeGenBench precision 0.43).
9. **OCR без языка.** Латинская «А» вместо кириллической проходит визуально и ломает поиск/копирование — сравнивать кодовые
   точки.
10. **Средние по моделям как свойство модели.** В MultiTextEdit ΔLSF 1.038 — среднее по 12 моделям; у NB2 разрыв 0.100.

## Чек-лист

- Использован срез арены, соответствующий задаче, и указана дата снимка?
- Разница между кандидатами больше CI (≥ 20 Elo) и не «Preliminary»?
- Проверено, что модель жива (не Imagen 4, не preview-id у Google API, не gpt-image-1 после 23.10.2026)?
- Для текста учтены и арена (предпочтение), и посимвольная точность (WeGenBench/OCR)?
- Для кириллицы есть собственный тест (арены её не меряют; LingT2I — только модели 2025 года)?
- Для правки использованы срезы правки (AA 18, LMArena 5), а не t2i?
- Заявление вендора отмечено `[мнение вендора]` и сверено с ареной на ту же дату?

## Открытые вопросы и противоречия

1. Какой уровень качества GPT Image 2.5 отдаёт polza (mie) и насколько место в арене переносится (тест 3).
2. Генерацию кириллицы независимо мерит только LingT2I — на моделях 2025 года («Nano Banana» без версии, Qwen-Image, FLUX.1);
   MultiTextEdit — только правка, без GPT 2.x, Seedream, Qwen 3.0. Для моделей 2026 года — только тест 1 фазы 5.
3. LingT2I использует Gemini 2.5 Flash как OCR при оценке модели Google — возможный перекос в пользу Nano Banana [S67].
4. TIIF-Bench v2 (ECCV 2026) — таблица лидерборда не извлеклась (JS) [S46]; лидерборд ImgEdit — картинка, не читался [S61].
5. Reve 2.0/2.1 (LMArena #6, #8) — первоисточники не изучались; доступ и цена неизвестны.
6. Muse Image — есть ли публичный API вне США (AA показывает $10/1k).
7. GEBench — числа по соседнему файлу [S49], первоисточник не перечитан.
8. Время генерации AA снято с графика по порядку сортировки; точное соответствие Flare/Sunburst 56/108 с — перепроверить.
9. Судьи-модели Google (T2I-CoReBench — Gemini 2.5 Flash, ViStoryBench PA — Gemini-3-Pro, OmniRef-Bench — Gemini 3 Flash)
   оценивают модели Google на первых местах — возможный перекос [мнение]; арены (люди) этот перекос не имеют.

## Источники

Нумерация [S#] общая для `03-image-models/` (реестр — `99-raw/experiments/C1/06-model-cards-build/sources.py`).

- [S1] polza.ai. Каталог моделей API (type=image, с провайдерами). снят 2026-09-23 08:45. https://polza.ai/api/v1/models?type=image&include_providers=true — первичные данные: id, провайдеры, параметры с описаниями, цены ₽; бесплатный эндпоинт [проверено].
- [S4] OpenAI. Страницы моделей gpt-image-2.5-sunburst, -flare, gpt-image-2, gpt-image-1.5. 2026-09-23. https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst — снимки, цены токенов, статус Deprecated у 1.5.
- [S6] OpenAI. Image prompting guide (вкладки 2.5 / 2 / 1.5 / 1). 2026-09-23. https://developers.openai.com/api/docs/guides/image-prompting — канонический гайд по промтам GPT Image; заменил cookbook-гайд.
- [S7] OpenAI. API changelog. 2026-09-23. https://developers.openai.com/api/docs/changelog — даты: 21.04.2026 GPT Image 2, 20.08.2026 прозрачность, 08.09.2026 GPT Image 2.5.
- [S8] OpenAI. Deprecations. 2026-09-23. https://developers.openai.com/api/docs/deprecations — gpt-image-1 → 23.10.2026; gpt-image-1.5, gpt-image-1-mini → 01.12.2026.
- [S9] OpenAI. Cookbook PR #3084 — архивирование гайда по промтам GPT Image 2. 2026-09-11. https://github.com/openai/openai-cookbook/pull/3084 — канон переехал в S6.
- [S10] Google. Gemini API — Image generation (Nano Banana). 2026-09-23. https://ai.google.dev/gemini-api/docs/image-generation — модели, размеры, токены, референсы, языки (ru-RU), лучшие практики.
- [S13] Google. Gemini API changelog. 2026-09-23. https://ai.google.dev/gemini-api/docs/changelog — GA 28.05.2026; preview выключены 25.06.2026; Imagen выключен 17.08.2026.
- [S15] Google Cloud. Vertex AI: Imagen 4; Gemini 3 Pro Image; deprecations. 2026-09-23. https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate — Imagen 4 Discontinuation 30.06.2026, C2PA Not supported; Vertex → Gemini Enterprise Agent Platform.
- [S18] Black Forest Labs. Release notes. 2026-09-23. https://docs.bfl.ml/release-notes — даты FLUX.2, Tools, FLUX 3 (только видео).
- [S19] Black Forest Labs. Pricing + FLUX.2 overview. 2026-09-23. https://docs.bfl.ml/quick_start/pricing — кредиты $0.01; роли pro/max/flex/klein.
- [S20] ByteDance Seed. Seedream 5.0 Pro — блог + страницы 5.0 Pro, 5.0 Lite, 4.5. 2026-07-08. https://seed.bytedance.com/en/blog/beyond-generation-it-understands-design-introducing-seedream-5-0-pro — заявления вендора: языки, инфографика, слои; ограничения текста.
- [S21] BytePlus ModelArk. Image generation API (Seedream 5.0 pro/flash/lite, 4.5, 4.0). 2026-09-23. https://docs.byteplus.com/en/docs/ModelArk/1541523 — языки промта, size, watermark default true, background, layers, sequential.
- [S23] Alibaba Qwen. Qwen-Image-2.1 README (HF + GitHub QwenLM/Qwen-Image-2.1, 1282★, push 2026-09-20) и LICENSE. 2026-09-20. https://huggingface.co/Qwen/Qwen-Image-2.1 — RGBA, 10 реф., маска; Qwen Research License (некоммерческая).
- [S24] Alibaba Cloud Model Studio. Qwen-Image-3.0-Pro; image generation & editing API reference; text-to-image; qwen-image API. 2026-09-23. https://www.alibabacloud.com/help/en/model-studio/qwen-image-3-0-pro — 12 языков (без списка), 1:8…8:1, цены; витрина «Виолета»; Wan 2.7 color_palette.
- [S25] Tongyi-MAI (Alibaba). Z-Image README (12 044★, push 2026-02-09). 2026-09-23. https://github.com/Tongyi-MAI/Z-Image — Turbo/Base, en/zh текст, Apache-2.0.
- [S26] Tongyi-MAI. Z-Image technical report (таблицы CVTG-2K, LongText, OneIG, GenEval, DPG, TIIF, PRISM, ImgEdit, GEdit, AI Arena). 2025-11. https://arxiv.org/abs/2511.22699 — бенчмарки в отчёте вендора; модели 2025 года.
- [S27] xAI (SpaceXAI). Images: generation, editing; models; grok-imagine-image-2.0; pricing. обновлено 2026-08-29. https://docs.x.ai/developers/model-capabilities/images/generation — параметры и цены Grok Imagine Image.
- [S28] xAI. Grok Imagine Image 2.0. 2026-08-07. https://x.ai/news/grok-imagine-image-2 — заявления вендора: типографика, фон, Smart resize.
- [S29] Topaz Labs. Topaz API — список моделей (+ www.topazlabs.com/api). 2026-09-23. https://developer.topazlabs.com/llms.txt — Gigapixel, Wonder, Bloom, Transparent Image Upscale.
- [S30] Recraft. Recraft docs: V4.1, V4 Styles, API endpoints, текст и набор символов, права. 2026-09-23 (кэш соседей). https://www.recraft.ai/docs/recraft-models/recraft-v4-1 — style_id, controls.colors, SVG; V3 без кириллицы.
- [S31] Ideogram. Ideogram 4.0 — блог + GitHub ideogram-oss/ideogram-4 (README, docs/prompting.md) + API Generate v4. 2026-06 / 2026-09-23. https://ideogram.ai/blog/4.0 — JSON-подписи, bbox, палитра, лицензия весов.
- [S32] Microsoft AI. MAI-Image-2.6 (10.08.2026) и Foundry public preview + 2.6-Flash (04.09.2026). 2026-09-04. https://microsoft.ai/news/pushing-the-quality-cost-frontier-with-mai-image-2-6/ — заявления вендора; устарело «№1 editing».
- [S33] Meta Superintelligence Labs. Introducing Muse Image and Muse Video. 2026-07-07. https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/ — прочитано через WebFetch (прямой fetch — 400); Content Seal.
- [S34] Midjourney. Version (V8.2, V8.1) + Enterprise API Survey. 2026-09-23 (через r.jina.ai; прямой — 403). https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version — параметры V8.x; официального API нет.
- [S35] Tencent Hunyuan. HunyuanImage-3.0 README + LICENSE (3271★, push 2026-06-23). 2026-09-23. https://github.com/Tencent-Hunyuan/HunyuanImage-3.0 — 80B MoE, VRAM, территориальные ограничения лицензии.
- [S36] Artificial Analysis. Image Arena: text-to-image (20 срезов). снято 2026-09-23 08:59. https://artificialanalysis.ai/image/leaderboard/text-to-image — слепые пары, Elo; английские промты [проверено].
- [S37] Artificial Analysis. Image Arena: editing (18 срезов). снято 2026-09-23 09:01. https://artificialanalysis.ai/image/leaderboard/editing — [проверено].
- [S38] Artificial Analysis. Image methodology. 2026-09-23. https://artificialanalysis.ai/image/methodology — дефолты вендора, 1:1, seed 42, английские промты, цена за 1000.
- [S39] LMArena. Text-to-Image leaderboard (8 категорий). снимок 2026-09-21. https://lmarena.ai/leaderboard/text-to-image — 6,26 млн голосов, 79 моделей [проверено].
- [S40] LMArena. Image Edit leaderboard. снимок 2026-09-21. https://lmarena.ai/leaderboard/image-edit — 29,9 млн голосов, 56 моделей; 4 категории устарели при съёмке [проверено].
- [S41] Cheng et al. (HIT). MultiTextEdit: многоязычная правка текста в картинках, 12 языков. 2026-05 (v2). https://arxiv.org/abs/2605.08163 — правка текста, 12 языков вкл. русский; из закрытых — только GPT-image-1.5 и NB2.
- [S42] Tencent Weixin, UESTC, DLUT. WeGenBench. 2026-06. https://arxiv.org/abs/2606.20100 — 4000 промтов zh/en; текст: Char F1, precision; судья Qwen3.5-397B.
- [S43] —. UniGenBench++. 2025-10. https://arxiv.org/abs/2510.18701 — многоязычность = zh/en; прочитано частично.
- [S44] —. MDPBench (§3: путаница кириллицы с латиницей в OCR). 2026-03. https://arxiv.org/abs/2603.28130 — для метрики фазы 5.
- [S45] —. ScriptMoE / TextMuSS (Latin-Cyrillic homoglyph confusion). 2026-09. https://arxiv.org/abs/2609.24058 — прочитано частично.
- [S46] TIIF-Bench authors. TIIF-Bench (v2, ECCV 2026) — страница проекта. 2026-06. https://a113n-w3i.github.io/TIIF_Bench/ — таблица лидерборда не извлеклась (JS).
- [S47] Genova AI (блог на Клерк.ру). Сравнение генераторов на русских промтах (4 макета × 3 модели, первая генерация). 2026-08-26. https://www.klerk.ru/blogs/genova-ai/706310/ — партнёрский материал агрегатора; картинки проверены глазами [мнение].
- [S48] StudyAI (Хабр). Сравнение 6 моделей на одном русском рекламном задании, N=1. ≈ 2026-09-22. https://habr.com/ru/companies/studyai/articles/1085264/ — корпоративный блог агрегатора [мнение].
- [S49] ui-research (соседняя база). Модели картинок для UI (22.09.2026), GEBench. 2026-09-22. ../../ui/12-ai-generated-ui/01-image-models-for-ui.md — GEBench (arXiv 2602.09007) — числа по соседнему файлу, первоисточник не перечитан.
- [S50] Midjourney. Enterprise API Survey. 2026-09-23. https://updates.midjourney.com/enterprise-api-survey/ — подтверждает отсутствие публичного API.
- [S51] Huang et al. T2I-CompBench++ (IEEE TPAMI 47(5), 2025); GitHub Karine-Huang/T2I-CompBench 347★, коммит 2026-09-04. 2025. https://arxiv.org/abs/2307.06350 — 8 подкатегорий композиции; модели ≤ 2024; судьи устарели.
- [S52] Ghosh et al. GenEval (NeurIPS 2023 D&B); GitHub djghosh13/geneval 484★. 2023. https://arxiv.org/abs/2310.11513 — насыщен; детектор Mask2Former + CLIP.
- [S53] Meta FAIR / UW. GenEval 2 (Soft-TIFA); GitHub facebookresearch/GenEval2 91★. 2025-12-18. https://arxiv.org/abs/2512.16853 — 800 промтов, судья Qwen3-VL-8B; аудит насыщения GenEval.
- [S54] авторы Echo-4o. GenEval++ (в статье Echo-4o). 2025-08. https://arxiv.org/abs/2508.09987 — 280 промтов, GPT-4.1; бенчмарк авторов модели.
- [S55] PKU-YuanGroup. WISE (ICML 2026) + лидерборд WISE_Verified (GitHub PKU-YuanGroup/WISE 220★). обновлён 2026-06-26. https://arxiv.org/abs/2503.07265 — знание мира; Verified — судья Qwen3.5-35B-A3B, 29 моделей.
- [S56] Sun et al. T2I-ReasonBench (ACL 2026 Findings). 2026. https://arxiv.org/abs/2508.17472 — 800 промтов, судья Gemini-2.5-pro; близок к потолку.
- [S57] PLUM-Lab. R2I-Bench (EMNLP 2025). 2025. https://arxiv.org/abs/2505.23493 — 3068 промтов; модели ≤ 04.2025.
- [S58] OneIG-Bench authors. OneIG-Bench (NeurIPS 2025 D&B) + лидерборд oneig-bench.github.io. лидерборд 2025-09-19. https://arxiv.org/abs/2506.07977 — 5 измерений EN/ZH; заморожен.
- [S59] Tencent (ELLA). DPG-Bench (в статье ELLA). 2024. https://arxiv.org/abs/2403.05135 — 1065 плотных промтов; потолок ≈ 88.
- [S60] Wu et al. KRIS-Bench (NeurIPS 2025) + живой лидерборд. обновлён 2026-05-06. https://arxiv.org/abs/2505.16707 — правка, требующая знаний; судья GPT-4o.
- [S61] PKU-YuanGroup. ImgEdit / ImgEdit-Bench (NeurIPS 2025 D&B); GitHub 338★. 2025. https://arxiv.org/abs/2505.20275 — 811 примеров; судья GPT-4o; обновлений 2026 нет.
- [S62] StepFun. Step1X-Edit / GEdit-Bench; GitHub stepfun-ai/Step1X-Edit 2264★. 2025. https://arxiv.org/abs/2504.17761 — 606 реальных запросов EN+CN; VIEScore.
- [S63] Jiang et al. GEditBench v2 (попарный Elo). 2026-03. https://arxiv.org/abs/2603.28547 — 1200 запросов, 23 задачи; ρ = 0.929 с Arena.
- [S64] RISEBench authors. RISEBench (NeurIPS 2025 D&B Oral) + живой лидерборд (GitHub PhoenixZ810/RISEBench 154★). обновлён 2026-04-23. https://arxiv.org/abs/2504.02826 — правка с рассуждением; 360 примеров; судья GPT-4.1.
- [S65] T2I-CoReBench authors. T2I-CoReBench (ICLR 2026) — лидерборд. 2026. https://t2i-corebench.github.io/ — судья Gemini 2.5 Flash; есть Nano Banana 2/Pro, Seedream 4.5.
- [S66] Qwen team. Qwen-Image-Bench. 2026-05. https://arxiv.org/abs/2605.28091 — бенчмарк вендора; GPT Image 2 65.23.
- [S67] RISys-Lab. LingT2I: многоязычный рендер текста в генерации (ACM MM 2026), 10 языков вкл. русский. 2026-08-11. https://arxiv.org/abs/2608.11002 — единственный найденный независимый бенчмарк генерации русского текста; модели 2025 года; OCR — Gemini 2.5 Flash.
- [S68] —. GlotOCR Bench. 2026-04. https://arxiv.org/abs/2604.12978 — OCR кириллицы близок к латинице у ряда моделей.
- [S69] —. Glyph-ByT5-v2 (VisualParagraphy, 10 языков вкл. русский). 2024. https://arxiv.org/abs/2406.10208 — устарело; своя модель 85–92 % OCR на русском.
- [S70] ViStoryBench authors. ViStoryBench (CVPR 2026) + живой лидерборд vistorybench.github.io. обновлён 2026-08-29. https://arxiv.org/abs/2505.24862 — серии кадров с персонажами; NB Pro №1 в Lite.
- [S71] —. OmniRef-Bench (DyRef). 2026-06-25. https://arxiv.org/abs/2606.26947 — 2–7 референсов (субъект, фон, стиль, свет, поза); судья Gemini 3 Flash.
- [S72] Matsuo Lab. MultiBanana (CVPR 2026). 2025-11 / 2026. https://arxiv.org/abs/2511.22989 — до 8 референсов; NB против GPT-Image-1.
- [S73] VectorSpaceLab. OmniGen2 / OmniContext. 2026-04 (v4). https://arxiv.org/abs/2506.18871 — 400 примеров; судья GPT-4.1; результаты плохо воспроизводятся.
- [S74] —. DreamBench++ (ICLR 2025). 2025. https://arxiv.org/abs/2406.16855 — персонализация по одному референсу; модели эпохи SDXL.
- [S75] —. MultiRef-Bench (ACM MM 2025). 2025. https://arxiv.org/abs/2508.06905 — 1990 задач; без моделей 2026 года.
- [S76] —. T2IS-Bench (наборы согласованных картинок). 2025. https://arxiv.org/abs/2506.23275 — 596 инструкций; модели 2025 года.
