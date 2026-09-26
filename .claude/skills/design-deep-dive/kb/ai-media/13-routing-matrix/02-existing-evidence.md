# Существующие сравнения моделей по задачам сайта: что уже известно и насколько этому верить

Волна 2 · агент E · 23.09.2026 · сводка по задачам поверх `../03-image-models/01-landscape-and-benchmarks.md` (арены AA и
LMArena, 30+ бенчмарков — не повторяется) + новые источники: GenAI Image Showdown, Rapidata Text-to-Image v1 и SVG v1,
практические «батлы» из дайджестов W · снимок каталога polza 2026-09-23. **Дополнено агентом N (волна 3, 24.09.2026)**:
влиты выписки помощника E `99-raw/notes/wave2/E-helper-evidence.md` (J1–J26, 32 источника: Design Arena, GDB, PaintBench,
GenColorBench, Pinterest Canvas, ProductConsistency, OCRGenBench, PosterBench, FEPBench, AIBench, Lucida, LiWi, MultiBind, VIBE,
Edit-Compass и др.) — правила 16–28 выжимки, таблица §2 (колонка «вывод» — v1), §2.1–§2.2, источники [S12]–[S33]; маршруты —
`routing.yaml` v1 и `03-routing-matrix.md` §2.1.

## Выжимка для агента

1. **Три независимые шкалы людей сходятся в топе**: AA, LMArena и Rapidata (963 380 матчей, 39 моделей) ставят №1–3
   Sunburst, Flare, GPT Image 2 — для общего качества спорить не о чем. → §1 [исследование]
2. **Сходятся и в «NB2 выше NB Pro»** (AA #6 против #10, LMArena #9 против #14, Rapidata #7 против #11; в иллюстрации
   Rapidata #7 против #24): NB Pro — только ради серий и ролей референсов. → §1 [исследование]
3. **Расходятся по Seedream 5 Pro**: LMArena Photoreal #9 и Portraits #8 против Rapidata Photorealism #33, общий #25 и
   Text Coherence #34 из 39 → в маршрут не ставить до E-08. → §2 [спорно]
4. **Расходятся по UI/UX**: AA — Flare №1, Rapidata — Sunburst №1, Flare #12 (±35) → для мокапов v0 — Sunburst. → §2 [спорно]
5. **«Красиво» ≠ «по брифу»**: Rapidata Preference (без промта) — №1 NB2, а Alignment — #7 и читаемость текста #15 → NB2 —
   дешёвый «красивый» вариант, но не для точного ТЗ и текста. → §2 [исследование]
6. **Читаемость латиницы — у Seedream 4.5**: Rapidata Text Coherence №1 (1223 ± 19) и WeGenBench Char F1 0,79 (лучший) —
   два независимых источника; в аренах Seedream 4.5 — середина → кандидат `IMG-TEXT-LATIN` рядом с GPT 2. → §2 [исследование]
7. **Следование промту — у GPT Image 2**: GenAI Showdown — 12/15 t2i и 98 % соблюдения за 41 попытку (NB Pro 10/15 за 104,
   FLUX.2 Pro 6/15 и 27 %); AA Text Rendering и Reasoning №1. → §2 [исследование, один судья]
8. **Слабость GPT в правке — «не тронуть лишнее»**: GenAI Showdown «Worm Sign» (провал GPT 2, 1.5, NB Pro) и GEditBench
   v2 (GPT 1.5 — выполнение 1260, согласованность 846) → правка GPT — только с композитом исходника вне цели. → §2 [исследование]
9. **NB2 в правке меняет цвета исходника** (GenAI Showdown «Paws»), а NB меняет ракурс на составной правке
   [V:7-YIYlIhksM 05:18–08:22] → одна правка за вызов и проверка ΔE вне цели. → §2 [мнение ×2]
10. **Порядок цветов и точная геометрия моделью не гарантируются**: «Red Next to Yellow» (5 полос по порядку) — 0 из 29
    моделей; «Nine-Pointed Star» — провал NB2, GPT 1.5, FLUX.2 Pro → бренд-палитру и геометрию задаёт код. → §2 [мнение, методика]
11. **Соотношение сторон меняет следование промту** (GenAI Showdown «Cubed⁵»: портрет заметно точнее) → мерить на целевом
    соотношении, а не на 1:1 арен. → §2 [мнение]
12. **Векторные иконки — у LLM, не у Recraft**: Rapidata SVG (59 моделей) — icons & ui №1–2 Claude Opus 5.5, Recraft
    V4.1 vector #39 → линейные и UI-иконки — LLM → SVG (G). → §2 [исследование]
13. **Кириллицу не мерит ни одна шкала**: все арены и Rapidata — английские промты (Rapidata переводит только текст для
    аннотатора); LingT2I — модели 2025 → единственный путь — E-02…E-04. → §2 [исследование]
14. **Z-Image для перебора хуже, чем кажется по цене**: мало разнообразия композиции, seed почти не меняет кадр (GenAI
    Showdown) → перебирать промтом, а не зерном. → §2 [мнение]
15. **Надёжность источника решает вес**: A — методика + независимость + модели сентября 2026 (AA, LMArena, Rapidata); B —
    методика есть, но один судья, подгонка промтов или старые модели (GenAI Showdown, академические); C — анекдот, N ≤ 4,
    партнёрский материал. → §3 [практика]
16. **Правка «сохранить остальное» — NB2 сильнее GPT**: вставка в макет LPIPS 0,078 против 0,327, удаление текста PSNR 30,22
    против 16,64 (GDB, NB2 против GPT-1.5); точная правка NB2 17,1 ≈ GPT 2 16,3 mIoU, но геометрия и обрезка — у GPT, цвет и
    градиент — у NB2 (PaintBench) → `IMG-EDIT` делится по типу правки. → §2, §2.1 [исследование: J13, J16]
17. **Все модели перерисовывают в 50–1400 раз больше пикселей, чем нужно** на мелких правках (PaintBench) → мелкая точная
    правка (hex, сдвиг на N px) — маска + композит или код, не модель. → §2.1 [исследование: J16, A]
18. **Товар без дефектов — лишь 53–75 %** (Pinterest Canvas: GPT-1.5 52,9 %, NB 74,6 %; 996 товаров × 2 оценщика); текст
    упаковки при перерисовке искажают все (CER до 1,19) → композит реального товара по умолчанию. → §2 [исследование: J14, J15]
19. **Hex попадает ≈ в половине случаев**: GPT-1.5 51,8 %, FLUX.2 48,7 %, Qwen 25,6 %, Z-Image 22,2 % (GenColorBench-Mini);
    перекраска в палитру картинкой — «All models fail», JSON → рендер 93–95 % (GDB) → палитра — кодом и грейдом. → §2
    [исследование: J11, J13]
20. **Адаптация баннера под формат — NB2**: элементы 1,0 против 0,23 у GPT-1.5 (GDB, 13 макетов) → `IMG-OUTPAINT`. → §2 [исследование: J13]
21. **Дословность латиницы — Seedream 4.5, три независимые линии**: Rapidata Text Coherence #1, OCRGenBench Poster AR 83,9
    (GPT-1.5 59,4, NB Pro 58,2), WeGenBench Char F1 0,79; вёрстка, логотип, типографика — GPT 2 (Design Arena Typography
    76,6 % на 5294 боях, Logo — 25 142 боя). → §2 [исследование: J2, J5, J8]
22. **Схемы «как это работает» — GPT 2** (FEPBench IF 0,664 против 0,629 у NB Pro, 1080 картинок × 3 эксперта); подписи
    теряют все (IF_t ≤ 0,39) → подписи кодом; AIBench ставит NB Pro выше, но без GPT 2.x. → §2 [исследование: J25, J26]
23. **Несколько реальных людей по референсам — не Seedream 4.5**: лица смешиваются в 53,7 % картинок против 24–25 % у NB Pro
    и GPT-1.5 (MultiBind). → §2 [исследование: J24]
24. **Одного лучшего выреза нет**: стекло — Ideogram remove-background (MAE 0,034), волосы — RMBG-2.0 (0,0045, но NC),
    тонкое — InSPyReNet; разложение Qwen на фото теряет альфу (IoU 0,61) → маршрут по типу объекта. → §2 [исследование: J9, J10]
25. **Генеративная реставрация нравится людям, но выдумывает**: NB2 ≈ PiSA-SR по PSNR, люди ставят №1, но галлюцинации,
    сдвиг цвета, нестабильность между прогонами → не для товара, лиц, текста. → §2 [исследование: J18]
26. **Design Arena — третья арена с тысячами боёв по срезам**: подтверждает GPT 2.x в Typography, Logo, Portrait; противоречит
    Rapidata по Seedream 5 Pro (Product #5 против #25 общий) → спор — в тест, не в маршрут. → §1, §2 [исследование: J5, B+]
27. **2 кандидата — основной прирост выхода**: 8 вместо 2 дают лишь 7 → 10 % (Pinterest); постеры — best-of-8 +2,4 балла
    (PosterBench) → best-of-2 для финала, best-of-4 для постеров. → §2 [исследование: J14, J7]
28. **Большинство 7–9 голосов ≈ 100 % на очевидных парах** (rapidata-vs-prolific, 300 вопросов) — ориентир числа голосующих
    для страницы слепых пар; VLM путают цвета (Qwen2-VL 49 %) и «есть ли объект» → цвет и наличие — кодом. → §3 [исследование: J4, J11, J19]

## 1. Общая картина (подробно — `../03-image-models/01-landscape-and-benchmarks.md` §2–§3)

| Шкала | Голоса и метод | Топ (23.09.2026) | Лучший не-OpenAI в polza | Ограничения |
|---|---|---|---|---|
| AA Image Arena | слепые пары, BT, якорь FLUX.2 [dev] = 1000; 20 + 18 срезов | Sunburst 1197, Flare 1191, GPT 2 1171 | NB2 #6 1122 | 1:1, английские промты, дефолты вендора (`max`) |
| LMArena | 6,26 млн голосов t2i; стиль-контроль | Sunburst 1423, Flare 1401, GPT 2 1381 | NB2 #9 1260; Seedream 5 Pro #10 | «Preliminary» у новых моделей |
| Rapidata T2I v1 | 963 380 матчей, ≥ 5 голосов на матч, BT + бутстрап; 4 вопроса; 25 категорий | Sunburst 1235 ± 13, Flare 1202, GPT 2 1168 | NB2 #7 1124 | 1024² даже при «16:9»; Text Coherence не проверяет дословность |
| GenAI Showdown | 15 t2i + 12 правок, pass/fail, 1 судья, попытки не фиксированы | GPT 2 12/15 (98 %), NB Pro и NB2 10/15 | те же | промты подгоняются под модель; нет GPT 2.5 и Seedream 4.5/5 |
| Design Arena (J5) | промты пользователей, турнир 4 моделей, BT, голоса без фильтра; image 3,19 млн, logo 1,05 млн, graphic design 0,47 млн, image-to-image 0,48 млн, SVG 0,18 млн | общий: Sunburst 1384, GPT 2 1367 (58 419 боёв), Flare 1366 | NB2 2K #12 1279; Seedream 5 Pro #13 1274 | CI не публикуются; у GPT 2.5 — сотни боёв в срезах; «latest versions» без уровня качества [B+] |

## 2. По задачам сайта

| Код | Что говорят сравнения | Надёжн. | Вывод для маршрута (v1, N 24.09) | Что проверить |
|---|---|---|---|---|
| `IMG-HERO-PHOTO` | Sunburst №1 AA Live-Action и Human Anatomy (1225 против 1135 у NB2), LMArena Photoreal/Portraits, Rapidata Photorealism #2 (Flare #1 1252 ± 33); Design Arena Portrait: GPT 2 1371 (15 519 боёв), Flare 1349, Sunburst 1348, NB2 2K #11 (J5); Seedream 5 Pro: LMArena #9 ↔ Rapidata #33 и People #28; у NB Pro — сдержанный бытовой реализм, NB2 задирает контраст и насыщенность [V:7-YIYlIhksM 01:02]; толпа + длинный заголовок — 0 из 29 (J1); GPT 2 без `quality high` теряет объект на сложной сцене (J19, n = 1) | A | Sunburst/Flare 2K; запас NB2; люди — GPT 2.x; Seedream 5 Pro и NB Pro — не для фото | E-08, E-09, E-01 |
| `IMG-PRODUCT` | AA Retail #1 Sunburst, LMArena Product #1; Rapidata Food & Drink: Sunburst 1308, Flare 1277, Seedream 4.5 #8; Design Arena Product: Sunburst 1369, GPT 2 1361, **Seedream 5 Pro #5** (J5) [спорно с Rapidata]; **Pinterest Canvas**: без дефектов товара GPT-1.5 52,9 %, Kontext 53,4 %, NB 2.5 74,6 % (996 товаров × 2 оценщика, J14); **ProductConsistency**: текст упаковки искажают все, CER NB 1,19, GPT-1 0,33 (J15); бенчмарка «товар по референсу» у моделей 2026 нет | A по сцене, B по сохранности | **композит** реального товара — по умолчанию; сцена — Sunburst; правка «вокруг реального» — NB2; этикетка — только фото | E-10, H-07 |
| `IMG-ILLUSTR` | AA Animation #1 Flare; LMArena Cartoon/Art #1 Sunburst, Seedream 5 Pro #9–10; Rapidata Illustration: Sunburst 1266, Flare 1216, NB2 #7, NB Pro #24; Design Arena Cartoon Seedream 5 Pro #9 (J5); «жёлтый фильтр» и «muddy fingerpainting» у GPT [мнение, J1]; **схемы**: FEPBench GPT 2 0,664 > NB Pro 0,629 > Seedream 5 Lite 0,575 ≫ Z-Image 0,390, подписи ≤ 0,39 (J25, A); AIBench NB Pro 77,8 > Seedream 5 Lite 73,2 > GPT-1.5 61,6 (J26, B) | A / спорно во 2-м месте | Flare или Sunburst; запас NB2; не NB Pro; схема — GPT 2, подписи — кодом | E-11 |
| `IMG-SERIES` | AA Identity Preserving #1 Sunburst; ViStoryBench и OmniRef-Bench — №1 NB Pro, №2 Seedream 4.5 (без GPT 2.x); MultiBanana — больше референсов хуже у старых моделей; «Not The Bees» (комикс 4 панели) — прошли GPT 2, NB2, NB Pro, провал FLUX.2 Pro (J1); **MultiBind**: смешение лиц Seedream 4.5 53,7 % против 24–25 % у NB Pro и GPT-1.5 (J24); Iconix: набор цепочкой «эталон → следующая» (J17, C) | спорно | Flare + эталон + метод F; запас NB Pro 2K; дёшево Seedream 4.5 — не для нескольких реальных людей | E-12, F-01, F-02 |
| `IMG-ICON3D` | LMArena 3D #1/#2 Sunburst/Flare; Rapidata 3D — 19 промтов, CI ± 60–118 (не различает, J2) | B | Sunburst сеткой 2×2; альфа — ровный фон + вырез (Qwen 2.1 — черновик) | E-14, F-07 |
| `IMG-CUTOUT` | замеров нативной альфы моделей нет; **Lucida** (203 картинки, эталонная альфа): стекло — Ideogram RB 0,034, волосы — RMBG-2.0 0,0045, тонкие — InSPyReNet 0,017; одного лучшего нет (J9); **LiWi**: разложение Qwen на фото IoU 0,61, на дизайне 0,87–0,92 (J10); H/01 — маршрут по типу объекта [проверено] | B | ровный фон + вырез по типу объекта; RouterAI GPT 2.5 transparent; Qwen 2.1 — только черновик (L) | H-01…H-04 |
| `IMG-BG-ABSTRACT` | hex документирован у FLUX.2 и Ideogram; **GenColorBench-Mini**: hex GPT-1.5 51,8 %, FLUX.2 48,7 %, Qwen 25,6 %, Z-Image 22,2 % (J11) — гипотеза «FLUX.2 = механизм hex» не подтверждена; **GDB**: перекраска в палитру картинкой — «All models fail», JSON → рендер 0,946 (J13); «Red Next to Yellow» — 0 из 29 (J1); Design Arena Abstract: Sunburst 1371, Flare 1352, FLUX.2 pro #31, NB2 Lite #39 (J5); PaintBench градиент NB2 13,0 против GPT 2 1,4 (J16) | B | фон-градиент и палитра — код; атмосфера — Flare; FLUX.2 — не «ради hex» | E-13 |
| `IMG-TEXTURE` | сравнений бесшовности нет; tile — только fal Z-Image tiling (шов 0,90–0,94 против 3,1 у контроля, P/06); NB Pro не тайлит (J12, C) | B (один опыт) | генерация + шов у H | H-09 |
| `IMG-TEXT-LATIN` | AA TR №1 GPT 2 (high), LMArena TR №1 Sunburst; Rapidata Text Coherence №1 Seedream 4.5 (1223 ± 19), #34 Seedream 5 Pro, NB2 #15; WeGenBench: Seedream 4.5 Char F1 0,79, NB2 precision 0,43; **OCRGenBench v4** Poster AR: Seedream 4.5 83,9, GPT-1.5 59,4, NB Pro 58,2 (J8); **Design Arena** Typography — GPT 2 1402 (76,6 %, 5294 боя), Logo — GPT 2 1366 (25 142 боя) (J5); PosterBench: best-of-8 +2,4 (J7); спецсимволы (`ĤΨ = EΨ`) — GPT 2, NB2, NB Pro, провал Ideogram 4 и FLUX.2 (J1); GDB: «1 in 4 strings rendered illegibly» (J13) | A | вёрстка/логотип — GPT 2; дословность — Seedream 4.5 (три линии); интерфейс — HTML | E-17 |
| `IMG-TEXT-CYR` | LingT2I (модели 2025): русский 0,29 против 0,67, «Nano Banana» 0,47 — читаемо, но не та строка; публичные тесты 2026 (N ≤ 4): GPT 2 4/4 дословно, NB2 2/4; W6: у NB Pro мелкий текст «still fails» [V:y-RQ48sfPgM 17:24]; новых источников с методикой нет (J, раздел IMG-TEXT-CYR) | C для 2026 | только HTML до E-02 | E-02…E-07 |
| `IMG-EDIT` | AA правка #1/#2 Sunburst/Flare; GenAI Showdown правка: GPT 2 10/12 (92 %), NB Pro 9/12, NB2 9/12; сохранность: провалы GPT и NB Pro («Worm Sign»), NB2 («Paws»); GEditBench v2: GPT 1.5 — выполнение 1260 / согласованность 846; **GDB**: вставка LPIPS NB2 0,078 против GPT-1.5 0,327, удаление текста PSNR 30,2 против 16,6 (J13); **PaintBench**: NB2 17,1 ≈ GPT 2 16,3 mIoU, геометрия — GPT, цвет/градиент — NB2, перерисовка лишнего 50–1400× (J16, A); Edit-Compass NB Pro 3,99 > NB2 3,74 > Seedream 4.5 3,22 (J23); VIBE удаление в рамке Seedream 4.5 95,8 (J22); Design Arena I2I: Sunburst 1393, Seedream 5 Pro Edit #11 (J5) | A по выполнению, B по сохранности | **по типу правки**: NB2 — «не трогать остальное»; Sunburst — сложная инструкция + композит; точные пиксели — не моделью | E-15, H-06, H-07 |
| `IMG-OUTPAINT` | AA Composition & Framing #1 Sunburst; **GDB** адаптация 9:16 → 1:1: GPT-1.5 TextAcc 1,0 / Recall 0,23, NB2 0,92 / 1,0 (13 макетов, ручная оценка, J13); Pinterest фон вокруг товара: NB 42,5 % без дефектов против 26,2 % (J14); PaintBench обрезка GPT 2 28,5 против NB2 19,1 (J16); «Cubed⁵»: портрет точнее (J1) | B | **NB2** + композит центра; точный кроп — кодом | H-08 |
| `IMG-MOCKUP` | AA UI/UX #1 Flare ↔ Rapidata UI/UX #1 Sunburst (Flare #12); GEBench — попадание по координате < 10 %; GDB — правки вылезают за маску (J13) | спорно | композит скриншота; сцена — Sunburst | позже |
| `IMG-UPSCALE` | сравнений апскейлеров с методикой на моделях 2026 нет; практики: апскейл фото «too smooth» [V:ttgNFJ25xfU 1:14:21]; **NB2 как реставратор** ≈ PiSA-SR по PSNR (22,5), люди — №1, но галлюцинации деталей, сдвиг цвета, нестабильность (J18, B+); H/02: Real-ESRGAN хуже Lanczos [проверено] | B | генерировать в целевом разрешении; Lanczos; генеративная доводка — только декор | H-05 |
| `IMG-DRAFT` | AA #13 NB2 Lite (+150 Elo к Z-Image); Design Arena общий NB2 Lite #18, Z-Image #64 (J5); Z-Image — однообразие композиции, compliance 38 % (J1), схемы IF 0,39 (J25), hex 12–22 % (J11); перенос черновика на финал не мерил никто | B | NB2 Lite; Z-Image — только композиция; перенос — референсом | E-16 |
| `VEC-ICON-LINE`, `-FILLED`, `-ILLUSTR` | Rapidata SVG v1 (59 моделей, 3 млн голосов): общий №1 quiver-arrow-2-telos 1485, Claude Opus 5.5 — №3–4 и №1 в icons & ui; Recraft V4.1 vector #31, pro-vector #28 (иконки #39/#37) (J3); Design Arena SVG: GPT-6 Astra 1482, Recraft V4.1 Vector Pro #23 (J5); GDB: image-to-SVG GPT-5.4 SSIM 0,918, валидность GPT/Claude ≈ 100 % (J13) | A для «чей SVG нравится людям» | иконки — LLM → SVG; Recraft — иллюстрации и цветной вектор | план G |

Практические оси (W5): «управляемость против вкусности» — GPT Image > Nano Banana > Seedream 4 по контролю и обратно по
фактуре [V:RIS8ckTfKAg 25:24–26:25] (ЦЕХ, 10.2025, модели прошлого поколения) → перебор выразительной моделью, финал
управляемой — гипотеза маршрута, стенд её не проверяет напрямую.

### 2.1 Профильные бенчмарки 2026 (выписки помощника E, J1–J26; влито N 24.09.2026)

Полные выписки, цитаты и методики — `99-raw/notes/wave2/E-helper-evidence.md` (журнал J#). Здесь — что они меняют в маршруте.

| J | Источник (дата) | Методика | Главные числа | Кл. | Что меняет в маршруте |
|---|---|---|---|---|---|
| J5 | Design Arena, image / logo / graphic design / image-to-image / SVG (23.09.2026) | турниры 4 моделей по промтам пользователей, BT | Typography GPT 2 1402 (76,6 %); Logo GPT 2 1366; Product Seedream 5 Pro #5; Abstract NB2 Lite #39; I2I — NB2 нет, FLUX.2 Pro Edit #29 | B+ | GPT 2 — типографика и логотип; Seedream 5 Pro — спорный кандидат товара; NB2 Lite — не для атмосферы |
| J7 | PosterReward / PosterBench (arXiv 2603.29855, 24.08.2026) | 250 промтов × 8 картинок; судья — своя reward-модель, проверена на 1740 парах людей | NB Pro 13,36; Seedream 4.5 12,03; Z-Image 7,65; best-of-8 +2,4 | B | постеры — отбор из ≥ 4 |
| J8 | OCRGenBench v4 (arXiv 2507.15085v4) | 1060 размеченных образцов, OCR PPOCRv5 + ручная правка, API по умолчанию | Poster AR Seedream 4.5 83,87; Z-Image 77,30; FLUX.2 dev 67,62; GPT-1.5 59,43; NB Pro 58,22 | B+ | Seedream 4.5 — дословный текст латиницей |
| J9 | Lucida (GitHub egeorcun, 08.2026) | 203 картинки с эталонной альфой, MAE/SAD/Grad | стекло Ideogram 0,0343; волосы RMBG-2.0 0,0045; тонкое InSPyReNet 0,0166; сумма lucida 0,0257 | B | вырез по классу объекта |
| J10 | LiWi (arXiv 2605.14552) | 1000 фото + 1972 шаблона, alpha soft IoU | Qwen-Image-Layered: фото 0,61, дизайн 0,87–0,92 | B | слои Qwen — для дизайна, не фото |
| J11 | GenColorBench (CVPR 2026, приложение S5) | 44 464 промта, пиксельный цвет по маске (CIEDE2000) | hex: GPT-1.5 51,8 / FLUX.2 48,7 / Qwen 25,6 / Z-Image 22,2 %; VLM Qwen2-VL — 49 % | B+ | hex — не гарантия; цвет — пикселями, не VLM |
| J12 | Training-Free Single-Image Diffusion (arXiv 2606.04299) | качественно | NB Pro «do not … achieve seamless tiling» | C | бесшовность — постобработкой |
| J13 | Graphic-Design-Bench / GDB (arXiv 2604.04192v2) | 49 задач на многослойных шаблонах, OCR, ΔE, LPIPS, ручные метрики | вставка LPIPS NB2 0,078 / GPT-1.5 0,327; удаление текста PSNR 30,22 / 16,64; адаптация Recall 1,0 / 0,23; палитра картинкой — все проваливаются, JSON → рендер 0,946 | B+ | `IMG-EDIT` (NB2 для сохранности), `IMG-OUTPAINT` (NB2), палитра — кодом |
| J14 | Pinterest Canvas (arXiv 2603.06453v2) | 996 товаров, 2 оценщика на картинку | без дефектов товара: GPT-1.5 52,9 %, Kontext 53,4 %, NB 2.5 74,6 %; 8 кандидатов вместо 2: 7 → 10 % | B+ | композит товара; best-of-2 |
| J15 | ProductConsistency (arXiv 2606.19103v1) | 870 правок, CER по OCR упаковки | CER: Kontext dev 0,149, GPT-1 0,33, NB 1,19 | B− | текст упаковки — только фото |
| J16 | PaintBench + TinyGrafixBench (arXiv 2606.00188) | 1920 задач с одним ответом, пиксельный IoU, бутстрап | NB2 17,1 ± 0,7; GPT 2 16,3 ± 0,7; геометрия GPT 11,1 / NB2 6,1; градиент NB2 13,0 / GPT 1,4; перерисовка 50–1400× | A | правка по типу; точные пиксели — не моделью |
| J17 | Iconix (CHI 2026) | исследование с пользователями против GPT-4o в чате | «significantly higher … across all seven measures» | C | набор иконок — цепочкой «эталон → следующая» |
| J18 | «Can Nano Banana 2 Replace … Restoration?» (arXiv 2604.03061v2) | 13 категорий, PSNR/LPIPS + 20 участников | NB2 PSNR 22,54 ≈ PiSA-SR 22,74; галлюцинации, сдвиг цвета | B+ | генеративная доводка — только декор |
| J19 | Simon Willison (21.04 и 30.06.2026) | 1 промт | GPT 2 по умолчанию теряет объект, с `quality high` — нет; VLM «видит» несуществующий объект | C | конфигурация polza — вопрос E-01/E-08 |
| J22 | VIBE (arXiv 2602.01851) | 1034 правки по пометкам на картинке, судья GPT-5.1 | NB Pro 65,15; Seedream 4.5 55,46; GPT-image-1 44,21; удаление в рамке Seedream 4.5 95,8 | B | «обвёл — убери» — Seedream 4.5 или NB Pro |
| J23 | Edit-Compass (arXiv 2605.13062) | 2388 примеров, 36 задач, судья Gemini-3.1-Pro | NB Pro 3,99; NB2 3,74; Seedream 4.5 3,22; FLUX.2 Dev 2,61 (без GPT) | B | порядок не-OpenAI: NB Pro ≥ NB2 > Seedream 4.5 |
| J24 | MultiBind (arXiv 2603.21937) | 508 примеров, 1527 людей | успех по лицу NB Pro 84,0 / GPT-1.5 82,3 / Seedream 4.5 58,6 %; смешение 25,3 / 24,4 / 53,7 % | B+ | серия с людьми — не Seedream 4.5 |
| J25 | FEPBench (arXiv 2606.05949v2) | 1300 иллюстраций, 1080 × 3 эксперта | IF GPT 2 0,664, NB Pro 0,629, Seedream 5 Lite 0,575, Z-Image 0,390; подписи ≤ 0,389 | A | схемы — GPT 2; подписи — кодом |
| J26 | AIBench (arXiv 2603.28068v2) | 300 статей, 5704 VQA-вопроса | NB Pro 77,77; Seedream 5 Lite 73,23; GPT-1.5 61,62 | B | блок-схемы: спор с FEPBench |

### 2.2 Галереи с одинаковыми промтами: слепое голосование без генераций

| Галерея | Что внутри | Лицензия | Годится? |
|---|---|---|---|
| Rapidata Text-to-Image v1 (benchmark.ai, J2) | 1514 англ. промтов × 39 моделей (Sunburst, Flare, GPT 2, NB2, NB Pro, Seedream 4.5/5, FLUX.2 pro, Qwen, Grok), 1024², публичный API образцов | не указана («All data and judgments are public») | **да, внутренне**: слепые пары Sunburst / NB2 / Seedream 4.5 по срезам UI/UX, Graphic Design, Logos, Infographics — до фазы 5 и бесплатно; оговорки: англ., дефолты вендора, 1:1 |
| Rapidata HF-наборы (J4) | пары + голоса по 3 вопросам (модели 2024–2025) | CDLA-Permissive-2.0 | для проверки страницы голосования и BT — да; для выбора модели — нет |
| Rapidata svg-benchmark (J3) | 500 промтов × 42 модели, SVG + PNG + голоса (≈ 44 ГБ) | промты CC-BY-4.0 | для G — частичной выборкой, внутренне |
| PaintBench (J16) | 1920 процедурных правок с эталоном | CC-BY-4.0 | как **бесплатный регрессионный набор** правки (пиксели), не для голосов |
| GenAI Showdown, Design Arena, VIBE, блоги | best-of-N автора / внутри приложения / CC-BY-NC | — | нет (только ссылки) |

## 3. Как оценивать надёжность сравнения

| Класс | Признаки | Примеры | Вес в маршруте |
|---|---|---|---|
| A | слепые голоса или метрика с методикой; независимость от оцениваемой модели; модели ≤ 1 мес. назад; CI | AA, LMArena, Rapidata (09.2026) | маршрут v0 без теста, если не вопрос конфигурации polza |
| B | методика есть, но один судья, подгонка промтов, старые модели, судья той же фирмы, малая категория | GenAI Showdown, T2I-CoReBench, ViStoryBench, OmniRef-Bench, WeGenBench | гипотеза маршрута, тест при споре |
| C | N ≤ 4, партнёрский материал, вендорская витрина, «первая генерация» | klerk.ru, Хабр/StudyAI, демо вендоров | только кандидаты для теста |

Проверки перед ссылкой: дата снимка и версия модели (заявления «№1» устаревают за 4 дня — MAI 04.09 → GPT 2.5 08.09);
режим модели (AA — `max`, LMArena — `medium`, Rapidata — «standard available configuration»); язык промтов (всюду
английский); соотношение (1:1 и 1024²); судья не той же фирмы, что лидер.

Добавлено N (24.09): конфигурация (GPT 2 по умолчанию и `quality high` — разный результат, J19); число голосов — большинство
7–9 независимых голосов даёт ≈ 100 % на «очевидных» парах (rapidata-vs-prolific, J4); судья-модель той же фирмы, что лидер
(Edit-Compass — Gemini при лидерах Google; ProductConsistency — GPT при исходниках GPT), — понижать класс на ступень.

## Частые ошибки

1. **Общий Elo вместо среза**: для текста — Text Rendering и Text Coherence, для правки — срезы правки, для UI — UI/UX.
2. **Одна шкала как истина**: Seedream 5 Pro — #9 в одной и #33 в другой; UI/UX — Flare №1 в одной и #12 в другой.
3. **«Красиво» за «точно»**: Preference без промта (NB2 №1) не говорит о соблюдении брифа (Alignment #7).
4. **Читаемость за дословность**: Rapidata Text Coherence спрашивает о «глитчах», не о тех ли словах.
5. **Сравнение с подогнанными промтами как модельное**: GenAI Showdown подбирает промт под модель и число попыток.
6. **Вывод о старой версии как о новой**: Pinterest (NB 2.5, GPT-1.5), ProductConsistency (GPT-1, NB без версии), VIBE
   (GPT-image-1) — модели 2025; переносить на 2026 только как гипотезу.
7. **«Нравится» за «верно»**: NB2 как реставратор — №1 у людей и галлюцинации деталей (J18); постеры — VIEScore высок у всех
   при низком OCR (J8).
8. **Цвет и наличие объекта — через VLM**: Qwen2-VL угадывает цвет в 49 % (J11), Claude «видел» несуществующего енота (J19)
   → пиксели и маски.
9. **Противоречия задач за противоречия моделей**: J14 (фон вокруг неподвижного товара — NB лучше) и J15 (перерисовка товара в
   новой сцене — NB хуже) мерят разные задачи; маршрут — композит в обоих случаях.

## Чек-лист

- Указаны шкала, срез, дата снимка и режим модели?
- Есть ли второй независимый источник или это единственный (помечено)?
- Сравнение делалось на задаче с тем же смыслом (срез, соотношение, язык)?
- Класс надёжности A/B/C записан рядом с выводом в `routing.yaml` v1 (поле `evidence[].class`)?

## Открытые вопросы и противоречия

1. Rapidata и LMArena противоречат по Seedream 5 Pro (фото, портреты) — разные наборы промтов и вопросы; E-08.
2. UI/UX: AA ↔ Rapidata — какой вывод переносится на мокапы сайтов, не известно (S21 отложен).
3. GenAI Showdown без GPT 2.5 и Seedream 4.5/5 — выводы о GPT 2 переносятся на 2.5 как гипотеза.
4. Прочитаны помощником E (J5, J6, J7, J20): Design Arena, imgsys (устарел, модели 2024), The Design Project (C),
   PosterBench; не открылись — Yupp (закрыт с 04.2026?), Medium James Palm (403), Datapoint AI (gated), parquet раунда
   Rapidata T2I v1 (не найден на HF).
5. Seedream 5 Pro: Design Arena Product #5 и Cartoon #9 против Rapidata #25 общий и Photorealism #33 — E-08, E-10, E-11.
6. Схемы: FEPBench (GPT 2 > NB Pro) против AIBench (NB Pro > Seedream 5 Lite > GPT-1.5; GPT 2.x нет) — стенд не мерит.
7. Нативная альфа GPT Image 2.5 / Qwen 2.1 против матирования — замеров с эталоном нет ни у кого → H-01…H-03.
8. Бесшовность, кириллица, 3D-иконки, мокапы с реальным скриншотом, апскейлеры моделей 2026 — независимых замеров с
   методикой не найдено (J, раздел «Главное» п. 12) → фаза 5.

## Источники

- [S1] Artificial Analysis. Image Arena t2i и правка, методика. 23.09.2026. https://artificialanalysis.ai/image/leaderboard/text-to-image — [A]; срезы — `99-raw/experiments/C1/03-aa-category-leaderboards/`.
- [S2] LMArena. Text-to-Image и Image Edit. снимок 21.09.2026. https://lmarena.ai/leaderboard/text-to-image — [A]; `99-raw/experiments/C1/04-…`.
- [S3] Rapidata. Text-to-Image v1 (benchmark.ai), методика и JSON API. 23.09.2026. https://www.benchmark.ai/image — 963 380 матчей, 39 моделей, 4 вопроса, 25 категорий [A]; выписки — `99-raw/notes/wave2/E-helper-evidence.md` J2.
- [S4] Rapidata. SVG Generation v1. 23.09.2026. https://www.benchmark.ai/svg ; HF `Rapidata/svg-benchmark` (CC-BY-4.0 промты) — 59 моделей [A]; J3.
- [S5] Pedicini S. GenAI Image Showdown (t2i и правка). журнал 20.09.2026. https://genai-showdown.specr.net/ — pass/fail, один судья, формула счёта из бандла [B]; J1.
- [S6] Jiang et al. GEditBench v2 (2026). https://arxiv.org/abs/2603.28547 — [B: без GPT 2.x].
- [S7] Tencent Weixin и др. WeGenBench (2026). https://arxiv.org/abs/2606.20100 — Char F1, precision [B: zh/en].
- [S8] RISys-Lab. LingT2I (ACM MM 2026). https://arxiv.org/abs/2608.11002 — [B: модели 2025].
- [S9] ViStoryBench (CVPR 2026), OmniRef-Bench (2026), MultiBanana (CVPR 2026) — по `../03-image-models/01-…` §7 [B].
- [S10] Дайджесты: [V:7-YIYlIhksM] (VideoSmile, GPT 2.5 против NB2/Pro, 09.2026), [V:RIS8ckTfKAg] (ЦЕХ), [V:y-RQ48sfPgM]
  (запуск NB Pro), [V:ttgNFJ25xfU] (PJ Ace) — `91-videos/digests/` [мнение].
- [S11] Публичные тесты кириллицы: klerk.ru / Genova AI (26.08.2026), Хабр / StudyAI (≈ 22.09.2026) — по C1 §5.2 [C].
- [S12] Design Arena. Image, Logo, Graphic Design, Image-to-Image, SVG leaderboards + About (методика). снимок 23.09.2026
  10:06–10:15 UTC. https://www.designarena.ai/leaderboard — BT без CI, промты пользователей [B+]; J5.
- [S13] Wang et al. PosterReward / PosterBench. arXiv 2603.29855 (версия 24.08.2026) — reward-модель, 8 картинок на промт [B]; J7.
- [S14] SCUT. OCRGenBench v4. arXiv 2507.15085v4 — OCR PPOCRv5 + ручная правка, 1060 образцов [B+]; J8.
- [S15] egeorcun. Lucida — benchmark.md. GitHub, 171★, push 05.08.2026. https://github.com/egeorcun/lucida — эталонная альфа, автор сравнивает свою модель [B]; J9.
- [S16] JD.com. LiWi: Layering in the Wild. arXiv 2605.14552 [B]; J10.
- [S17] Butt et al. GenColorBench (CVPR 2026) + supplementary S5. arXiv 2510.20586 [B+]; J11.
- [S18] U. Toronto. Efficient Training-Free Single-Image Diffusion. arXiv 2606.04299 — рис. S15 [C]; J12.
- [S19] LICA. Graphic-Design-Bench (GDB). arXiv 2604.04192v2, 31.03.2026 [B+]; J13.
- [S20] Pinterest. Canvas. arXiv 2603.06453v2 — 996 товаров × 2 оценщика [B+]; J14.
- [S21] Fractal Analytics. ProductConsistency. arXiv 2606.19103v1 [B−]; J15.
- [S22] Xu, Brown, …, Xie (NYU). PaintBench + TinyGrafixBench. arXiv 2606.00188; HF `PaintBench/PaintBench` (CC-BY-4.0) [A]; J16.
- [S23] Iconix (CHI 2026). arXiv 2602.00738 [C]; J17.
- [S24] SIAT/Fudan. Can Nano Banana 2 Replace Traditional Image Restoration Models? arXiv 2604.03061v2 [B+]; J18.
- [S25] Willison S. «Where's the raccoon with the ham radio?» (21.04.2026), «Nano Banana 2 Lite» (30.06.2026). simonwillison.net [C]; J19.
- [S26] The Design Project. Midjourney vs ChatGPT vs NanoBanana (YouTube `u4yfkr19NSY`, 19.12.2025) [C]; J20.
- [S27] Cupareanu D. Nano Banana 2 vs GPT Image 2: I Tested 10 Identical Prompts. Substack, 10.05.2026 [C]; J21.
- [S28] VIBE (UCAS/CASIA/Cambridge). arXiv 2602.01851; HF `VIBE-Benchmark` (CC-BY-NC-3.0) [B]; J22.
- [S29] Edit-Compass (HDU/PKU/Kling Team/CASIA). arXiv 2605.13062 [B]; J23.
- [S30] MultiBind (CASIA + ByteDance). arXiv 2603.21937 [B+]; J24.
- [S31] FEPBench (Shanghai AI Lab). arXiv 2606.05949v2 [A]; J25.
- [S32] AIBench (Tongyi Lab). arXiv 2603.28068v2 [B]; J26.
- [S33] Rapidata. rapidata-vs-prolific (HF, 04.08.2026, CC-BY-4.0), Bananamark, Face_Generation_Benchmark [B/C]; J4.
