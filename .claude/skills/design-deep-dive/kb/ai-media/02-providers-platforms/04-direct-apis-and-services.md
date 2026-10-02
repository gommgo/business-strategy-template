# Прямые API вендоров и сервисы-инструменты: что дают сверх polza, почём и как достать

Волна 1 · агент P (помощник по файлу 04) · 23.09.2026 · снимок каталога polza 2026-09-23 · курс ЦБ на 23.09.2026:
84,0657 ₽/$, 96,5915 ₽/€ · источников 65 (35 прочитаны целиком или по всем разделам темы, 15 — фрагментами, 15 — через
заметки соседей P/C1/C2); новых URL снято 35 · опыты агента P (P/06, P/07, P/08) и C1 (C1/02) использованы как данные; собственных опытов у файла нет.

Файл отвечает на вопрос «что даёт прямой канал вендора (или сервис-инструмент) сверх polza, почём, как его достать из
России и когда он окупается». Возможности и качество моделей — в карточках C1/C2 (`../03-image-models/`,
`../04-video-models/`), агрегаторы как каналы — в `03-aggregators-and-platforms.md`, итог по ключам — в `06-gap-map.md`,
API polza — `01-polza-api.md`. Скоропортящееся (цены, id, сроки снятия) дано с датой; ₽ — по курсу ЦБ, без наценок.

## Выжимка для агента

1. Прежде чем идти к вендору за параметром, открой `top_provider.parameters` модели в каталоге polza: там видно, что
   polza реально пропускает; документация вендора этого не говорит. → §1.1 [проверено: каталог 2026-09-23]
2. Прозрачный фон GPT Image 2.5 (`background: "transparent"` + png/webp) через polza не передаётся. Для IMG-CUTOUT с
   GPT Image — прямой OpenAI, fal, AITUNNEL или Gen-API; внутри polza прозрачность есть только у `qwen/image-2.1`.
   → §2.2 [документация]
3. `quality` у GPT Image 2.5 меняет цену квадрата 1024² в 36 раз ($0,0059 low → $0,2107 max). polza берёт плоские
   4/7/11 ₽ без выбора качества; черновик `low` в прямом API — 0,50 ₽. → §2.3 [документация + C1/02]
4. OpenAI не обслуживает Россию и запрещает «offering access» вне списка стран; прямой ключ — только через юрлицо и
   карту страны из списка. Барьер — условия и оплата, не сеть. → §1.3 [документация]
5. Sora 2 и Videos API OpenAI удаляются 24.09.2026; `gpt-image-1` — 23.10.2026; `gpt-image-1.5` (есть в polza) —
   01.12.2026. → §2.1 [документация]
6. Imagen 4 мёртв: Vertex — 30.06.2026, Gemini API — 17.08.2026. «Imagen 4» в витринах KIE и VseGPT — устаревшая
   карточка или подмена. → §3.4 [документация]
7. polza отдаёт Nano Banana под preview-id, которые Google выключил 25.06.2026; какая модель отвечает на самом деле,
   проверяется результатом, не по id. → §3.1 [документация; спорно]
8. Сверх polza у NB2 в Gemini API: 0.5K (512 px, $0,045), `thinking_level: "high"`, поиск Google по картинкам,
   video-to-image, Batch −50 %; у NB Pro тариф Flex вдвое дешевле ($0,067 за 1–2K). → §3.2 [документация]
9. Veo 3.1 **с негативом и без звука** — Vertex (`negativePrompt`, `generateAudio: false`, плюс `sampleCount` 1–4 и
   `compressionQuality: "lossless"`), fal (`negative_prompt`, `generate_audio: false`) и Runway (`negativePrompt`,
   `audio: false`); Gemini API и polza этих полей не дают. У fal/Runway без звука дешевле (Fast $0,10 против $0,15/с со
   звуком; у Google напрямую Fast со звуком — $0,10); звук из ролика polza снимается `ffmpeg -an` бесплатно. → §3.5,
   §3.6 [документация]
10. `enhancePrompt` в Vertex Veo по умолчанию `true` — для воспроизводимости ставь `false`, иначе `seed` не держит
    результат. → §3.5 [документация]
11. У FLUX.2 [pro]/[max] переписывание промта (upsampling) включено по умолчанию; генерация «ровно по промту» —
    `disable_pup: true` в прямом API BFL; polza флаг не пропускает. → §4.2 [документация]
12. У FLUX.2 нет `negative_prompt` и прозрачного фона ни в одном канале; `guidance`/`steps` есть только у [flex] — в
    прямом API BFL (по умолч. 5 и 50), у fal (`guidance_scale` 3,5 и `num_inference_steps` 28 по умолч.) и в passthrough
    OpenRouter. Умолчания каналов разные — задавай явно. → §4.2 [документация]
13. Условия FLUX API разрешают BFL обучаться на входах и выходах: конфиденциальные референсы клиента (фото продукта до
    релиза) через BFL не отправлять. → §4.4 [документация]
14. Recraft — единственный массовый источник настоящего SVG. Для серии нужны `style_id` ($0,005 за стиль) и
    `controls.colors`; их пропускают прямой API и passthrough OpenRouter (закрыт для РФ), Gen-API и Replicate режут.
    → §5.4 [документация]
15. SVG Recraft V4 — только заливки без `stroke`, фон-прямоугольник первым путём, `preserveAspectRatio="none"`,
    подпись `<recraft-signature>`: постобработка обязательна. → §5.1
    [проверено]
16. Инструменты Recraft дешевле аналогов: vectorize $0,01, removeBackground $0,01 (SVG на входе → SVG на выходе), crisp
    upscale $0,004, erase region $0,002. → §5.3 [документация]
17. Ideogram 4.0 API — без `seed`, негатива и стиль-кодов; стиль-коды, негатив, character reference и кастомная модель
    живут только в v3-эндпоинтах. → §6.1 [документация]
18. Прозрачный фон вместе с текстом за один проход — `/v1/ideogram-v4/generate-transparent` (до 8K); layerize-text
    отдаёт текстовые блоки со шрифтом и фон без текста — кандидат для схемы «ИИ-фон + HTML-текст». → §6.1
    [документация; качество не проверено]
19. Условия Ideogram API требуют «Powered by Ideogram» и марки Ideogram на страницах приложения, где пользователь
    получает доступ к модели. → §6.3 [документация]
20. Официального API Midjourney нет (23.09.2026); ToS запрещает автоматизацию и перепродажу доступа. «MJ API»
    агрегаторов нарушают условия и останавливаются без предупреждения (useapi.net закрыл MJ 24.06.2026, GoAPI — тоже).
    В конвейер не включать. → §7 [документация]
21. Нативная бесшовная петля видео есть только у Luma Ray 3.2 (`video.loop: true`, 5 с, без end_frame и HDR). В polza,
    KIE, OpenRouter Luma нет; каналы — прямой API Luma, fal, Replicate. → §8.2 [документация]
22. `camera_control` у Kling был только в v1.x; у Kling 3 камера задаётся промтом. `multi_shot` в новом API Kling по
    умолчанию `true` — для фона ставить `false`. → §8.3 [документация]
23. Прямой Kling стоит как fal ($0,084/с 720p без звука), вход — пробный пакет $9,8–14 на 30 дней; polza берёт 10 ₽/с
    (×1,42 к прайсу). → §8.3 [документация]
24. Плоские тарифы polza на Wan 3.0 (23,6 ₽/с) и MiniMax H3 Max (9,44 ₽/с) равны тарифам вендора для 1080p/768p;
    черновик 480p напрямую дешевле в 2,2–5,6 раза по курсу ЦБ. → §8.4, §8.7 [вывод из цен]
25. Draft mode Seedance 2.5 (черновик 480p → согласованный финал 1080p), `camera_fixed` (документирован у 1.x, у 2.x не
    подтверждён), `mov` yuv444p — только прямой BytePlus; `seedance-1-5-pro` BytePlus снял, в polza он живёт через KIE до
    поры. → §8.6 [документация]
26. xAI Video 1.5: `last_frame`, `keyframes` ≤4 с привязкой ко времени, `generate_audio: false` — только прямой API xAI;
    polza даёт i2v 480/720p. → §8.5 [документация]
27. MiniMax: Video Regeneration 768P → 2K ($0,05/с) и команды камеры в скобках `[static]` — прямой API; через polza —
    только H3 Max без 2K. → §8.4 [документация]
28. Удаление фона: Recraft и Ideogram $0,01, Bria $0,018, Photoroom $0,02. remove.bg как отдельный сервис закрывается
    01.12.2026 — не встраивать. → §10 [документация]
29. Векторизация: Recraft vectorize $0,01 (без настроек) или локальный vtracer (агенты G/H); Vectorizer.ai (€0,045–0,18
    за картинку по подписке) — для сложных логотипов и форматов PDF/EPS/DXF. → §11 [документация]
30. Апскейл: Recraft crisp $0,004 для иллюстраций; Topaz Transparent Upscale сохраняет альфу; Magnific генеративный с
    `creativity`/`resemblance`, цена за вызов не опубликована в API-доках. → §12 [документация]
31. Результаты живут недолго: BFL — 10 мин, Veo в Gemini API — 2 дня, URL Seedance — 24 ч, Recraft — ~24 ч, Kling — 30
    дней. Скачивать сразу. → §1.4 [документация]
32. Прямой ключ окупается, когда (а) параметр решает задачу, которую polza не решает (SVG, прозрачность GPT Image, петля
    Luma, Veo без звука и с негативом), и (б) объём оправдывает минимальный пакет. Иначе — российский агрегатор-
    проводник с нужным параметром. → §13 [мнение P]

## 1. Рамка: как сверялось «сверх polza», курс, доступ из России, данные

### 1.1 Методика сверки параметров

- Параметры polza взяты из `99-raw/cache/polza/2026-09-23/api-v1-models.json`, поле `top_provider.parameters` (у
  модели с провайдером `mie` это набор KIE, у `openai`/`google-vertex` — набор без параметров в каталоге) [S1]. Набор
  вендора — из его API-справочника на 23.09.2026. Совпадение имени модели не значит совпадение параметров: у одной
  модели у разных провайдеров polza разные поля (`openai/gpt-5-image@mie` имеет `mask_url`, у `@openai` — нет) [S1].

| Модель в polza (провайдер) | Что polza пропускает | Чего нет в polza, но есть у вендора |
|---|---|---|
| `openai/gpt-image-2.5-sunburst`, `gpt-image-2-5-flare` (mie) | `prompt` ≤20 000, `aspect_ratio` 13 значений, `image_resolution` 1K/2K/4K, `images` ≤16 | `background`, `quality`, `output_format`, `output_compression`, `moderation`, `n`, маска, `partial_images`, произвольный `size` |
| `black-forest-labs/flux.2-pro`, `flux.2-flex` (mie) | `prompt` ≤5000, `aspect_ratio` 7 значений, 1K/2K, `images` ≤8 | `seed`, `width`/`height`, `disable_pup`/`prompt_upsampling`, `guidance`, `steps`, `safety_tolerance`, `output_format` |
| `google/gemini-3-pro-image-preview`, `…3.1-flash-image-preview` (mie) | `aspect_ratio`, 1K/2K/4K, `images` ≤8/≤14, у NB2 `output_format` | 0.5K, 1:4/4:1/1:8/8:1 у NB2, `thinking_level`, поиск Google, стиль-референсы Pro, Batch/Flex |
| `google/veo3`, `google/veo3_fast` (mie) | `aspect_ratio`, `seeds` 10000–99999, `watermark`, `images`, `generationType`, `enableTranslation` | `negativePrompt`, `generateAudio`, `durationSeconds`, `resolution`, `sampleCount`, `personGeneration`, `compressionQuality` |
| `kling/v3` (mie) | `duration` 3–15, `images` ≤2, `mode` std/pro/4K, `sound` | `multi_shot`/`multi_prompt`, элементы, `negative_prompt` (legacy API), `watermark_info` |
| `minimax/hailuo-3-max` (openrouter) | 480p/768p, 5–15 с, `images` ≤2 | H3 2K, Video Regeneration, `prompt_expansion_mode` |
| `grok-imagine-video-1-5` (mie) | 480p/720p, 1–15 с, `images` ≤7 | 1080p, `last_frame`, `keyframes`, `generate_audio` |
| `bytedance/seedance-2-5` (mie) | 480p/720p, 4–30 с, 30 картинок, 10 видео, `generate_audio` | 1080p, `draft`, `camera_fixed`, `return_last_frame`, `output_format: mov` |

- Нет в каталоге polza вовсе (23.09.2026): Recraft, Ideogram, Midjourney, Luma, Runway, FLUX.2 [max]/[klein], Kling O3,
  Veo 3.1 Lite, удаление фона, векторизация, Photoroom, Bria, Vectorizer.ai [S1].

### 1.2 Курс и цены

- Курс ЦБ РФ на 23.09.2026: 84,0657 ₽/$, 96,5915 ₽/€ (`99-raw/experiments/P/02-kie-vs-polza/cbr_2026-09-23.xml`) [S2].
  polza для токенных цен берёт 117,992 ₽/$ = ЦБ × 1,404 (данные агента B) [S2]. Все ₽ в этом файле — прайс вендора ×
  курс ЦБ, без комиссий банка, НДС и конвертации.
- Цены — на 23.09.2026 по страницам вендоров; где страница не отдала число — метка `[не проверено]` и вторичный
  источник рядом.

### 1.3 Доступ из России: три барьера

- **Сеть** — не барьер из этой среды: зарубежные API отвечают штатными 401/403 через VPN с раздельной маршрутизацией
  (литовский выход); таймауты бывают у fal и Recraft [проверено]. Для
  эксплуатации нужен стабильный зарубежный выход или проводник в РФ.
- **Условия** — два типа. Явный список стран без России: OpenAI [S7], Gemini API и AI Studio [S15]. Пункт о
  «комплексных санкциях США» (Restricted Territories): xAI [S49], fal [S64], BFL («U.S.-sanctioned jurisdiction») [S26],
  Luma, Replicate, Runway (эмбарго США) [S42][S64]. Россия как страна под «комплексные» санкции OFAC формально не
  подпадает (подпадают Крым, ДНР, ЛНР) [мнение P, не юридическое заключение], но ЕС/UK-формулировки fal шире —
  [спорно]; решать юристу (агент L).
- **Оплата** — главный практический барьер: Stripe/карты (Ideogram — Stripe [S33]; Vectorizer.ai — карты и PayPal
  [S57]; Topaz, Recraft, BFL, Kling — карты [не проверено: страницы биллинга не сняты]); российские карты за рубежом не
  работают. Google Cloud: «not accepting new Google Cloud customers in Russia» (заявление Google, 10.03.2022) [S21];
  отмены не найдено [не проверено на 2026].

| Вендор | Россия в условиях | Оплата | Сеть отсюда (P/08) | Вывод для системы |
|---|---|---|---|---|
| OpenAI | нет в списке стран; «offering access» вне списка → блок | карта страны из списка | 401, отвечает | только юрлицо/карта за рубежом или проводник |
| Google Gemini API | нет в available-regions | Google Payments | отвечает (1 раз 57 с) | то же |
| Google Vertex / Agent Platform | новые клиенты из РФ не принимаются (2022) | Google Cloud Billing | отвечает | то же |
| BFL | «not located… in a U.S.-sanctioned jurisdiction» | карта [не проверено] | то 401/403, то таймаут | возможен с иностранной картой; условия [спорно] |
| Recraft | санкционного пункта нет (поиск по ToS 11.08.2026) | карта [не проверено] | таймаут 1 из 3 | возможен с иностранной картой |
| Ideogram | пункта нет | Stripe, предоплата ≤$300 | 401 | возможен с иностранной картой |
| Runway, Luma, xAI, Replicate, fal | эмбарго/комплексные санкции США | карта | 401/403 | возможны с иностранной картой; [спорно] для fal (ЕС/UK) |
| Kling, MiniMax, BytePlus, Alibaba | пунктов не найдено / страницы не сняты | карта [не проверено] | 401/403 | [не проверено] |

### 1.4 Данные: обучение на входах и срок жизни результатов

| Вендор | Обучение на входах/выходах API | Хранение |
|---|---|---|
| OpenAI | нет («not used to train… unless you explicitly opt in») [S8] | логи злоупотреблений до 30 дней; `/v1/images/*` — без состояния, ZDR возможен по одобрению [S8] |
| Google Gemini API | Paid — нет; Free — «used to improve our products» [S11] | Veo: видео на сервере 2 дня [S13] |
| BFL | **да**: «may use Inputs and Outputs to train and improve its… models» [S26] | ссылка на результат 10 мин [S24][S25] |
| Recraft | нет: «API inputs and outputs are never used for model training… not stored» [S30] | результаты ~24 ч [S2] |
| Ideogram | нет, кроме нарушивших Usage Policies [S34] | ссылки истекают [S33] |
| Runway | **да**: «Inputs and Outputs may be used… to train» + бессрочная лицензия [S42] | URL временные [S41] |
| Luma | **да**: лицензия на Input для «create, test, improve, train» [S64] | — |
| xAI (Enterprise ToS) | нет: «will not use any User Content to train» [S49] | User Content удаляется ≤30 дней [S49] |
| Kling | [не проверено] | результаты 30 дней [S45] |
| BytePlus | [не проверено] | задачи 7 дней, URL видео 24 ч [S50] |
| Midjourney | бессрочная лицензия на Inputs и Assets; всё публично без Stealth [S37] | — |

→ Для конфиденциальных референсов клиента безопасные по тексту условий каналы: OpenAI, Gemini API (Paid), Recraft,
Ideogram, xAI. BFL, Runway, Luma — только с неконфиденциальными входами [документация].

## 2. OpenAI Images API — GPT Image 2.5

### 2.1 Модели и сроки жизни (23.09.2026)

| id | Статус | Что сказать агенту |
|---|---|---|
| `gpt-image-2.5-sunburst` (снапшот `-2026-09-08`) | выпущен 08.09.2026 [S5] | «most capable… editing precision» [мнение вендора] |
| `gpt-image-2.5-flare` (`-2026-09-08`) | выпущен 08.09.2026 [S5] | «fastest… everyday» [мнение вендора] |
| `gpt-image-2` (`-2026-04-21`) | действует; прозрачность — preview с 20.08.2026 [S5] | для новых интеграций вендор советует 2.5 [S3] |
| `gpt-image-1` | удаление 23.10.2026 [S6] | не использовать |
| `gpt-image-1-mini`, `gpt-image-1.5`, `chatgpt-image-latest` | удаление 01.12.2026 [S6] | `openai/gpt-image-1.5` в polza умрёт до конца года |
| `dall-e-2`, `dall-e-3` | удалены 12.05.2026 [S6] | не упоминать |
| Videos API, `sora-2`, `sora-2-pro` (все снапшоты) | **удаление 24.09.2026**, замены нет [S6] | «Sora 2» у Gen-API, AITUNNEL, Replicate — с 25.09 вероятно мёртв |

### 2.2 Параметры, которых нет в polza

| Параметр (Image API) | Значения | Что даёт сайту | polza (mie) |
|---|---|---|---|
| `background` | `transparent` / `opaque` / `auto`; transparent только с png/webp | IMG-CUTOUT, IMG-ICON3D без удаления фона | нет |
| `quality` | `low`, `medium`, `high`, `xhigh`, `max`, `auto` (у 2.5 по умолчанию `auto`) | дешёвый перебор IMG-DRAFT, дорогой финал | нет (плоская цена) |
| `size` | `WxH` кратно 16, 1:3…3:1, сторона ≤3840, 655 360…8 294 400 px; >2560×1440 — experimental | точный OG 1200×640, 21:9 hero 3840×1648 | только 13 соотношений × 1K/2K/4K |
| `output_format` + `output_compression` | png (по умолч.) / jpeg / webp; сжатие 0–100 для jpeg/webp | готовый WebP без перекодирования; jpeg быстрее png | нет |
| `n` | несколько картинок за запрос | перебор вариантов одним вызовом | нет |
| `partial_images` | 0–3, стрим; каждая частичная +100 выходных токенов | превью в интерфейсе генератора | нет |
| `moderation` | `auto` (по умолч.) / `low` | меньше ложных блокировок | нет |
| маска `mask` (edits) | PNG с альфой, тот же размер, <50 МБ; к первой картинке | IMG-EDIT по области | нет (маска есть только у `gpt-5-image@mie`) |

- Маска у GPT Image «entirely prompt-based… may not follow its exact shape» — для точной границы маска не гарантия
  [документация S3]. Пиксельно точная правка — FLUX Erase (§4.3) или Recraft eraseRegion (§5.3).
- `input_fidelity`: для `gpt-image-2` параметр запрещено передавать — входы всегда в высокой точности; для 2.5 гайд
  параметр не описывает → не передавать [документация S3; для 2.5 — вывод].
- Ответ Image API — base64; `/v1/images/edits` принимает и JSON (`images` + `mask` по `image_url`/`file_id`) [S5].

### 2.3 Цена за картинку: прямой API против polza

Формула калькулятора OpenAI (порт C1/02, сверен с опубликованной таблицей GPT Image 2 до цента): сетка качества 2.5 —
low 16, medium 24, high 48, xhigh 64, max 96; `tokens = ceil(gw·gh·(2e6 + W·H) / 4e6)`; цена = tokens × $30/1M
[проверено]. Входные токены (текст $5/1M, картинка $8/1M) не включены.

| Размер | low | medium | high | xhigh | max | polza (mie), плоско |
|---|---|---|---|---|---|---|
| 1024×1024 | $0,0059 · 0,50 ₽ | $0,0132 · 1,11 ₽ | $0,0527 · 4,43 ₽ | $0,0937 · 7,88 ₽ | $0,2107 · 17,71 ₽ | 4 ₽ (1K) |
| 1920×1088 (≈16:9) | $0,0044 · 0,37 ₽ | $0,0103 · 0,87 ₽ | $0,0398 · 3,35 ₽ | $0,0707 · 5,94 ₽ | $0,1590 · 13,37 ₽ | 7 ₽ (2K) |
| 2560×1440 | $0,0062 · 0,52 ₽ | $0,0143 · 1,20 ₽ | $0,0553 · 4,65 ₽ | $0,0983 · 8,26 ₽ | $0,2211 · 18,59 ₽ | 7 ₽ (2K) |
| 3840×2160 | $0,0111 · 0,93 ₽ | $0,0260 · 2,19 ₽ | $0,1001 · 8,41 ₽ | $0,1779 · 14,96 ₽ | $0,4003 · 33,65 ₽ | 11 ₽ (4K) |
| 1200×640 (OG) | $0,0030 · 0,25 ₽ | $0,0065 · 0,55 ₽ | $0,0259 · 2,18 ₽ | $0,0452 · 3,80 ₽ | $0,1017 · 8,55 ₽ | нет такого размера |

- Какое качество ставит `mie` за 4/7/11 ₽, в каталоге не сказано; по цене — между `medium` и `high` [спорно: C1/02].
  Проверка — тест P-1 (§14).
- Широкая картинка той же площади дешевле квадратной (1920×1088 high — 1325 токенов, 1024² high — 1756) [проверено:
  C1/02].
- Лимиты: Free — нет доступа; Tier 1 — 5 картинок/мин, Tier 2 — 20, Tier 3 — 50, Tier 4 — 150, Tier 5 — 250 [S4].
  Может потребоваться «API Organization Verification» [S3]. Латентность — до 2 мин на сложный промт [S3].
- Batch API −50 % объявлен для `gpt-image-2` и моделей 1.x [S5]; для 2.5 явно не сказано [не проверено].

### 2.4 Модерация и ошибки

- `error.type = "image_generation_user_error"`, `error.code = "moderation_blocked"`, `moderation_details.moderation_stage`
  = `input` | `output` | `unknown`, `categories` (например `harassment`, `violence`). Такие ошибки не ретраить без
  изменения промта или входа; ретраить только 429/5xx с бэкоффом [документация S3].

```python
# openai-python · Image API · gpt-image-2.5-flare · 2026-09-23 · [не проверено: ключа нет]
from openai import OpenAI
import base64
client = OpenAI()  # ключ из окружения, организация вне РФ
r = client.images.generate(
    model="gpt-image-2.5-flare",
    prompt="Matte ceramic coffee cup, three-quarter view, soft studio light, isolated object, no shadow",
    size="1024x1024", quality="medium",
    background="transparent", output_format="webp", output_compression=85,
    moderation="auto", n=2,
)
for i, d in enumerate(r.data):
    open(f"cup_{i}.webp", "wb").write(base64.b64decode(d.b64_json))
```

### 2.5 Каналы с полным набором параметров без прямого ключа

| Канал | Что пропускает | Оговорка |
|---|---|---|
| fal (`openai/gpt-image-2.5*`) | `quality` auto…max, `background`, `output_format` + `output_compression`, размеры ≤3840 | `quality` по умолчанию **high** — задавать явно; цена — токены OpenAI [S59] |
| AITUNNEL | `background: transparent`, `quality` low…max; ₽, «комиссия внутри», ≈170 ₽/$ | каталог = OpenRouter [S2] |
| Gen-API | уровни качества (1024² low 5 ₽ … max 57,5 ₽), прозрачность и маски по описанию | ≈250 ₽/$ [S2] |
| OpenRouter | `background`, `quality`, passthrough `moderation` | закрыт для российских аккаунтов и IP с 27.06.2026 [S62] |

### 2.6 Когда прямой OpenAI оправдан

- Оправдан: массовые черновики `low` (0,25–0,93 ₽ против 4–11 ₽ в polza), прозрачные вырезки в одном проходе, точные
  нестандартные размеры, конфиденциальные референсы (обучения нет, ZDR по одобрению) [S3][S8].
- Не оправдан без юрлица за рубежом: условия прямо запрещают доступ из России [S7]. Практичный путь — fal или
  AITUNNEL/Gen-API с `background` и `quality` [мнение P].

## 3. Google: Gemini API и Vertex AI (Gemini Enterprise Agent Platform)

Vertex AI документация больше не обновляется: «Vertex AI's services are now part of Gemini Enterprise Agent Platform»
[S16]. Ниже «Vertex» = Agent Platform, эндпоинт `https://us-central1-aiplatform.googleapis.com/v1/…:predictLongRunning`.

### 3.1 Nano Banana: какие id живы

| Модель | id Gemini API (GA) | Статус 23.09.2026 | id в polza |
|---|---|---|---|
| Nano Banana 2 | `gemini-3.1-flash-image` | GA с 28.05.2026 [S12] | `google/gemini-3.1-flash-image-preview` (mie), `google/gemini-3.1-flash-image` (google-vertex, токены) |
| Nano Banana Pro | `gemini-3-pro-image` | GA с 28.05.2026 [S12] | `google/gemini-3-pro-image-preview` (mie) |
| Nano Banana 2 Lite | `gemini-3.1-flash-lite-image` | GA с 30.06.2026 [S12] | `google/gemini-3.1-flash-lite-image` (mie) |
| Nano Banana (2.5) | `gemini-2.5-flash-image` | legacy; доступ к 2.5 ограничен с 18.09.2026 теми, кто ими пользовался [S12] | `google/gemini-2.5-flash-image` (mie) |

- `gemini-3.1-flash-image-preview` и `gemini-3-pro-image-preview` Google выключил 25.06.2026 [S12]; polza держит эти id
  у `mie` — на стороне KIE, видимо, перенаправление на GA [спорно; проверка — тест P-4].

### 3.2 Nano Banana: что даёт прямой API сверх polza

| Возможность | Модели | Что даёт сайту | Источник |
|---|---|---|---|
| `image_size` "512" (0.5K), 1K, 2K, 4K; **заглавная K обязательна**, `1k` отклоняется | 0.5K только NB2; Lite — только 1K | дешёвый эскиз 512 px за $0,045; превью | [S10] |
| Соотношения 1:4, 4:1, 1:8, 8:1 | NB2 (в Gemini API); в polza — только у Lite | вертикальные ленты, баннеры 8:1 (например 3072×384 в 1K) | [S10] |
| `thinking_level` `minimal` (по умолч.) / `high` | NB2 и NB2 Lite; у Pro мышление всегда включено | сложная компоновка, инфографика; до 2 промежуточных «thought images» не тарифицируются, токены мышления — да | [S10] |
| Grounding: `tools: [{"type": "google_search", "search_types": ["web_search", "image_search"]}]` | Pro (web), NB2 (web + image); Lite — нет | актуальные факты, карты, внешний вид реальных объектов; обязан показать `search_suggestions`; 5000 запросов/мес бесплатно, далее $14/1000 | [S10][S11] |
| Video-to-image (видео или YouTube URL как контекст) | NB2, NB2 Lite | постер и превью ролика | [S10][S12] |
| До 14 референсов: NB2 — 10 объектов + 4 персонажа; Pro — 6 объектов + 5 персонажей + **3 стиль-референса**; Lite — 14 объектов | все Gemini 3 | IMG-SERIES, продукт по фото | [S10] |
| Batch API (−50 %, до 24 ч), у Pro ещё **Flex** (−50 %) и Priority (×1,8) | все | ночные партии ассетов | [S11] |
| Мульти-ход правки (Interactions API) | все | итеративная доводка | [S10] |

- Нет у Nano Banana ни в одном канале: прозрачного фона, `negative_prompt`. `temperature`, `top_p`, `top_k` объявлены
  deprecated 21.07.2026 [S12]. Все картинки с SynthID; у NB2 Lite ещё C2PA [S10].
- Языки с лучшим качеством включают ru-RU [документация S10] — для IMG-TEXT-CYR это заявление, не замер (C1 §12).

### 3.3 Цены Nano Banana (Gemini API, Paid, 23.09.2026)

| Модель | Standard | Batch / Flex | polza (mie) |
|---|---|---|---|
| NB2, 0.5K | $0,045 · 3,78 ₽ | $0,022 · 1,85 ₽ | нет 0.5K |
| NB2, 1K / 2K / 4K | $0,067 / $0,101 / $0,151 · 5,63 / 8,49 / 12,69 ₽ | $0,034 / $0,050 / $0,076 · 2,86 / 4,20 / 6,39 ₽ | 4,8 / 7,2 / 10,8 ₽ |
| NB2 Lite, 1K | $0,0336 · 2,82 ₽ | $0,0168 · 1,41 ₽ | 2,9 ₽ |
| NB Pro, 1K–2K / 4K | $0,134 / $0,24 · 11,26 / 20,18 ₽ | $0,067 / $0,12 · 5,63 / 10,09 ₽ | 13,5 / 18 ₽ |
| NB (2.5) | $0,039 · 3,28 ₽ | $0,0195 · 1,64 ₽ | 2,9 ₽ |

Источник: таблицы страницы цен [S11]; токены вывода: NB2 $60/1M (0.5K 747, 1K 1120, 2K 1680, 4K 2520 токенов), NB Pro
$120/1M (1K–2K 1120, 4K 2000), Lite $30/1M [S10][S11]. Вывод: polza близка к прямому Standard (NB2 и NB 2.5 дешевле,
NB Pro 1–2K на 20 % дороже, 4K дешевле) и примерно вдвое дороже Batch/Flex; прямой канал оправдывают параметры (0.5K, 1:8,
поиск, стиль-референсы) и партии через Batch, а не разовая цена [вывод P].

### 3.4 Imagen 4 — снят везде

- Gemini API: `imagen-4.0-generate-001`, `-ultra-`, `-fast-` выключены 17.08.2026 (объявлено 15.06.2026); гайд: «Imagen is
  shut down and no longer available through the Gemini API» [S10][S12].
- Vertex: те же id в таблице «Discontinued endpoints», миграция на `gemini-2.5-flash-image`, «Discontinuation date:
  June 30, 2026» [S16]. Imagen 4 умел `negative_prompt`, маски, outpaint и до 4 картинок за запрос — эта ниша у Google
  закрыта, замена — Nano Banana без негатива [S16].

### 3.5 Veo 3.1: три набора параметров

| Параметр | Gemini API (`veo-3.1-*-preview`) [S13] | Vertex (`veo-3.1-*-001`) [S17][S18][S19][S20] | polza (`google/veo3*`, mie) [S1] |
|---|---|---|---|
| Статус модели | preview (Veo 2/3/3 Fast сняты 30.06.2026) | GA с 17.11.2025, retirement «17.11.2026 or later»; Lite — preview | id `veo3`, `veo3_fast` (набор KIE) |
| Первый + последний кадр | `image` + `lastFrame` (last только вместе с first) | то же | `FIRST_AND_LAST_FRAMES_2_VIDEO`, `images` ≤2 |
| Референсы | `referenceImages` ≤3 (asset), только 8 с; у Lite нет | до 3 asset или 1 style | Fast: `REFERENCE_2_VIDEO`, ≤3 |
| Длительность | `durationSeconds` 4/6/8; 8 обязательно для 1080p, 4k, референсов, продления | 4/6/8 | не выставлена (цена «за запрос») |
| Разрешение | 720p / 1080p / 4k (4k нет у Lite) | 720p / 1080p / 4k (4k — «Veo 3.1 Preview models only» в i2v-гайде) | не выставлено |
| Звук | всегда включён | **`generateAudio: false`** | не выставлен (звук, вероятно, всегда) |
| Негатив | **нет** | **`negativePrompt`** | нет |
| Несколько видео | 1 | **`sampleCount` 1–4** | 1 |
| `seed` | «slightly improves» детерминизм | uint32 0–4 294 967 295; при `enhancePrompt: true` не гарантирует | `seeds` 10000–99999 |
| Переписывание промта | — | `enhancePrompt`, **по умолчанию true** | `enableTranslation` (перевод, по умолч. true) |
| Сжатие | — | **`compressionQuality: "lossless"`** / `optimized` | — |
| Подгонка кадра | — | `resizeMode` `pad` / `crop` | — |
| Люди | `personGeneration` (i2v/FLF/референсы — только `allow_adult`; ЕС/UK/CH/MENA — только `allow_adult`) | `dont_allow` / `allow_adult` / `allowAll` | нет |
| Продление | `video` из прошлой генерации: +7 с до 20 раз, итог ≤148 с, только 720p | `task: "extend"`: вход 1–30 с, +7 с, итог ≤37 с | операция `extend` в API polza |
| Правка по маске | — | `mask` + `video`: вставка и удаление объектов, аутпейнт | — |
| Камера | промтом | в схеме есть `cameraControl` (`fixed`, `pan_left`, `push_in`, …) только с `image`; для 3.1 не документирован [не проверено] | промтом |
| Хранение | 2 дня на сервере | ответ байтами или `storageUri` в GCS | 7 дней (polza) |

- Для VID-HERO-LOOP и VID-CINEMAGRAPH значимы три отличия Vertex: звук выключается (не платишь за него), негатив
  «camera movement, cuts, text» и 1–4 варианта за вызов [документация; эффект не проверен]. Негатив и выключение звука
  есть и у fal (`fal-ai/veo3.1`, `…/veo3.1/fast/first-last-frame-to-video`, `…/veo3.1/lite`: `negative_prompt`,
  `generate_audio`, `seed`, 4/6/8 с, 720p/1080p/4k; `auto_fix` по умолчанию переписывает промт, не прошедший
  модерацию) [S59] и у Runway (§8.1).
- В Vertex карточке GA-моделей написано «Pay-as-you-go: Not supported; Fixed quota: Supported; Provisioned Throughput:
  Supported; Batch inference: Not supported»; регион — только `us-central1` [S17]. Как это соотносится с оплатой по
  факту, из карточки не ясно [не проверено].

### 3.6 Цены Veo 3.1 и Omni (Gemini API, за секунду, звук включён, 23.09.2026)

| Модель | 720p | 1080p | 4k | 8 с 720p | polza |
|---|---|---|---|---|---|
| Veo 3.1 Standard | $0,40 | $0,40 | $0,60 | $3,20 · 269,01 ₽ | Quality 187,5 ₽ за ролик |
| Veo 3.1 Fast | $0,10 | $0,12 | $0,30 | $0,80 · 67,25 ₽ | 45 ₽ за ролик |
| Veo 3.1 Lite | $0,05 | $0,08 | нет | $0,40 · 33,63 ₽ | нет |
| Gemini Omni Flash (`gemini-omni-1.1-flash`) | ≈$0,10 (5792 токена/с × $17,50/1M) | апскейл | апскейл | ≈$0,80 · 67,25 ₽ | `gemini-omni-video` 35–115 ₽ |

Источник: таблица цен Veo и Omni [S11]. polza (канал KIE) на Veo дешевле прямого Gemini API примерно на треть: 45 ₽
против 67,25 ₽ за Fast и 187,5 ₽ против 269 ₽ за Standard при 8 с 720p — если polza отдаёт 8 с [вывод P, S2; длительность
не проверена]. Прямой Google оправдан не ценой, а параметрами Vertex (§3.5). У fal и Runway Veo без звука дешевле, чем
со звуком: $0,20/с (Standard) и $0,10/с (Fast) против $0,40 и $0,15; fal Lite без звука — $0,03/с при 720p [S41][S59].
Fast со звуком у fal ($0,15) дороже прямого Google ($0,10) — наценка канала [вывод P].
Российские проводники с Veo без звука: AITUNNEL (Fast 720p 13,6 ₽/с) и Gen-API (25 ₽/с) — дороже polza (45 ₽ за 8 с со
звуком) [S2].

### 3.7 Gemini Omni Flash — коротко

- GA `gemini-omni-1.1-flash` с 27.08.2026, preview снимается 30.09.2026; Interactions API; продление, интерполяция
  первый+последний кадр (`image_to_video` ≤2 картинки), `resolution` 360p/720p/1080p/4k (1080p и 4k — апскейл) [S12].
- Петля документирована вендором через теги `<FIRST_FRAME>@Image1 <LAST_FRAME>@Image1`; по умолчанию модель делает
  несколько планов — писать «single continuous shot»; негатив-параметра нет (C2 §1) [S14]. Карточка — у C2.

### 3.8 Доступ и когда оправдан

- Доступ: России нет в списке стран Gemini API и AI Studio; страница советует прочим странам Agent Platform [S15], а
  Google Cloud новых клиентов из РФ не принимает [S21]. Оба канала — только через зарубежное юрлицо и карту [мнение P].
- Оправдан: Veo по 1–4 варианта за вызов, `lossless`, правка видео по маске (Vertex; негатив и выключение звука есть и у
  fal/Runway), NB 0.5K-эскизы и поиск по картинкам (Gemini API), партии через Batch/Flex. В остальном polza (KIE) дешевле и
  доступнее [вывод P].

## 4. Black Forest Labs — FLUX.2 и инструменты

### 4.1 Модели и эндпоинты (`https://api.bfl.ai`, заголовок `x-key`)

| Эндпоинт | Что это | В polza |
|---|---|---|
| `/v1/flux-2-pro` (+ `/v1/flux-2-pro-preview`) | «recommended default» | есть (`black-forest-labs/flux.2-pro`, урезанный набор) |
| `/v1/flux-2-max` | «Highest quality… strongest editing consistency», grounding search | нет |
| `/v1/flux-2-flex` | «Specialized for typography… preserving small details»; `guidance`, `steps` | есть (урезанный) |
| `/v1/flux-2-klein-4b`, `/v1/flux-2-klein-9b` | быстрые, открытые веса (4B Apache 2.0, 9B NCL) | нет |
| `/v1/flux-tools/erase-v1` | удаление объекта по маске | нет |
| `/v1/flux-tools/outpainting-v1` | расширение холста до 4 Мп | нет |
| `/v1/flux-tools/deblur-v1`, VTO v2 | резкость, примерка | нет |

Все вызовы асинхронные: ответ `id`, `polling_url`, `cost` (в кредитах), `input_mp`, `output_mp`; результат —
`GET /v1/get_result?id=`; вебхук `webhook_url` + `webhook_secret`; поле `user` — id конечного пользователя [S22].

### 4.2 Параметры сверх polza

| Параметр | Модели | Значения | Зачем |
|---|---|---|---|
| `seed` | все | целое | повтор варианта для серии и A/B |
| `width`, `height` | все | ≥64, кратно 16, ≤4 Мп («Recommended up to 2MP») | точный кадр под слот вместо 7 соотношений polza |
| `disable_pup` | pro, max | по умолч. `false` → upsampling включён | генерация ровно по промту (JSON-промты, тесты) |
| `prompt_upsampling` | flex | по умолч. `true` | то же для flex |
| `guidance` | flex | 1,5–10, по умолч. 5; выше — точнее промт, ниже реализм | типографика и мелкий текст |
| `steps` | flex | 1–50, по умолч. 50 | дешёвый быстрый черновик |
| `safety_tolerance` | все | 0–5, по умолч. 2 | меньше ложных блокировок |
| `output_format` | все | `jpeg` (по умолч.) / `png` / `webp` | PNG/WebP без перекодирования |
| `input_image`…`input_image_8` | pro, max, flex | до 8 в API (klein — до 4) | мульти-референс |

- Нет ни в одном канале: `negative_prompt` (гайд BFL: «No negative prompts»), прозрачного фона, маски в генерации
  [S22][S27]. fal пропускает `seed`, `safety_tolerance`, `output_format`, `image_size`, а у flex — `guidance_scale`
  (по умолч. 3,5) и `num_inference_steps` (по умолч. 28) — умолчания не совпадают с BFL (5 и 50); `disable_pup` у fal не
  выставлен [S59]. passthrough OpenRouter пропускает `steps`, `guidance`, `safety_tolerance`, но для РФ закрыт [S62].

### 4.3 FLUX Erase и FLUX Outpainting

```json
// BFL · POST /v1/flux-tools/erase-v1 · 2026-09-23 · [не проверено: ключа нет]
{"image": "<base64 или URL>", "mask": "<ч/б PNG того же размера: белое = удалить>",
 "dilate_pixels": 10, "output_format": "png"}
```

- Erase: промта нет (встроенная инструкция), «powered by FLUX.2 Klein 9B», обучена на ≈1 Мп в 9 соотношениях 1:2…2:1;
  для волос и дыма `dilate_pixels` 15–20; цена в доках не указана [S24] [не проверено].
- Outpainting: `input_image`, целевые `width`×`height` (холст ≤4 Мп, любое соотношение), `reference_offset_x/y` (None =
  по центру, отрицательные можно), `auto_crop`, `mode` `high` (по умолч.) | `fast` (только base64, соотношение
  референса ≤8:1, «typically lower cost»), `prompt` — экспериментально, `output_format` png по умолчанию [S25]. Это
  IMG-OUTPAINT «без промта»: картинка 16:9 → баннер 2730×1536 или 1024×4096 [документация; качество не проверено].

### 4.4 Цены, условия, доступ

- Цены (1 кредит = $0,01; одинаково для API и Playground): klein 4B от $0,014 (+$0,001/Мп) · 1,18 ₽; 9B от $0,015
  (+$0,002/Мп) · 1,26 ₽; pro от $0,03 (t2i) · 2,52 ₽ и от $0,045 (правка); max от $0,07 · 5,88 ₽; flex от $0,05 · 4,20 ₽;
  FLUX.1 Kontext pro $0,04, max $0,08; «batch» = цена × число картинок, без скидки [S23]. polza: pro 5/7 ₽, flex 14/24 ₽
  (1K/2K) — ×2,0–2,4 к прайсу BFL [S1].
- Ссылка `delivery.bfl.ai` живёт 10 минут — скачивать в том же обработчике [S24][S25].
- Условия: «the Company may use Inputs and Outputs to train and improve its artificial intelligence models» (FLUX API
  Service Terms); пользователь не должен находиться в «U.S.-sanctioned jurisdiction»; запрет обучать конкурирующие
  модели на Output; BFL может встраивать Content Credentials (C2PA) [S26].
- Когда оправдан: `seed` + точный размер + `disable_pup` для воспроизводимых серий и JSON-промтов; FLUX Erase/Outpainting
  как инструменты правки; [max] для самых сложных правок. Для конфиденциальных входов — нет (обучение) [мнение P].

## 5. Recraft — настоящий SVG и дешёвые инструменты

### 5.1 Что именно отдаёт Recraft V4 Vector (опыт P/07)

Разбор 8 публичных SVG `recraft-ai/recraft-v4-svg` (Replicate) [проверено]:

- только залитые контуры, **0 обводок** даже на промт «line icons… consistent stroke width» → `stroke-width` через CSS не
  поменять, перекраска — заменой `fill` (3–6 цветов у иконок);
- текст — контуры, `<text>` нет;
- корень: `width`/`height` в px, `preserveAspectRatio="none"`, цвета `rgb()`, координаты с 2–3 знаками в сетке 2048;
- у иконок и логотипа первый путь — фон на весь холст (`M 0 0 L 2048 0 … z`);
- набор иконок приходит одним файлом с подписями и полями → резать по bbox групп и нормализовать под сетку 24/20;
- `<metadata><recraft-signature>` (Ed25519, timestamp, identifier) — маркер происхождения; `svgo` с `removeMetadata` его
  удалит (решение — агент L);
- размер 11,6–282 КБ; округление до 0,1 — −14…17 %.

→ Recraft закрывает VEC-ILLUSTR и VEC-ICON-FILLED с обязательной постобработкой (агент G); для VEC-ICON-LINE по сетке и
штриху лучше SVG кодом от LLM [вывод P/07].

### 5.2 Модели и параметры API (`https://external.api.recraft.ai/v1`, совместим с OpenAI SDK)

- Модели (23.09.2026): V4.1 (май 2026; `recraftv4_1` — по умолчанию, `_vector`, `_pro`, `_pro_vector`, `_utility`,
  `_utility_vector`, `_utility_pro`, `_utility_pro_vector`), V4 Styles (август 2026; `recraftv4_styles`, `_vector`, `_pro`,
  `_pro_vector`), V4, V3 (`recraftv3`, `_vector`), V2 [S28][S2].
- Эндпоинты: `/images/generations` (+ `/raster` и `/vector` — сервер гарантирует тип), `/styles`, `/images/imageToImage`,
  inpaint, outpaint, replaceBackground, generateBackground (правка — только V3), `/images/vectorize`,
  `/images/removeBackground`, `/images/crispUpscale`, `/images/creativeUpscale`, `/images/eraseRegion`, remix, enhance
  prompt [S28].

| Параметр | Модели | Значение для сайта |
|---|---|---|
| `n` 1–6 | все | перебор за вызов |
| `size` WxH или w:h, 14 соотношений (V4 1K: 1024², 16:9 = 1344×768; Pro: 2048², 16:9 = 2688×1536) | все | под слот |
| `style_id` (создание `/styles` $0,005), `style_match` precise/flexible (V4), `style_references` 1–10 картинок ≤64 МБ | V4/V4.1/Styles | **серия в одном стиле** (IMG-SERIES, наборы иконок) |
| `controls.colors` ≤10 цветов (rgb + weight), `controls.background_color` | все | палитра бренда, фон |
| `random_seed` | все | повтор варианта |
| `negative_prompt` | **только V2/V3** | — |
| `artistic_level` 0–5, `no_text`, `text_layout` | **только V3** | `text_layout` из кириллицы допускает лишь гомоглифы латиницы «А В Е К М Н О Р С Т У Х» и «І» — настоящую кириллицу так не задать |
| `response_format` url / b64_json / multipart; `image_format` webp (по умолч., lossless) / png | все | — |
| промт ≤10 000 символов (V4/V4.1), ≤1000 (V2/V3) | — | длинные спецификации |

- Лимиты: 100 картинок/мин на пользователя, 5 запросов/с; результаты хранятся ~24 ч, URL подписанные [S2][S28].
- Vectorize: PNG/JPG/WEBP ≤10 МБ, ≤16 Мп, сторона 256–4096; параметров качества нет. removeBackground: то же + SVG на
  входе → SVG на выходе (SVG <256 px масштабируется, «unsafe SVGs» отклоняются), `image_format` webp/png. crispUpscale —
  от 32 px, creativeUpscale — от 256 px, «focus on refining small details and faces» [S28].

```python
# openai-python с base_url Recraft · recraftv4_1_vector · 2026-09-23 · [не проверено: ключа нет]
from openai import OpenAI
c = OpenAI(base_url="https://external.api.recraft.ai/v1", api_key="<RECRAFT_KEY>")
r = c.images.generate(
    model="recraftv4_1_vector",
    prompt="Single flat icon of a paper plane, geometric, no labels, centered, generous padding",
    size="1:1", n=2,
    extra_body={"style_id": "<uuid из POST /styles>", "random_seed": 42,
                "controls": {"colors": [{"rgb": [37, 99, 235]}, {"rgb": [15, 23, 42]}],
                             "background_color": {"rgb": [255, 255, 255]}}},
)
print([d.url for d in r.data])  # SVG; скачать в течение ~24 ч
```

### 5.3 Цены API (23.09.2026; $1 = 1000 units, пакеты не сгорают, невозвратны; ключ — только при балансе > 0)

| Операция | $ | ₽ (ЦБ) |
|---|---|---|
| Raster V4.1 / V4.1 Utility | 0,035 | 2,94 |
| **Vector V4.1 / V4.1 Utility / V4 Vector** | **0,08** | **6,73** |
| Vector V4.1 Pro / V4 Pro | 0,30 | 25,22 |
| Vector V4 Styles / Styles Pro | 0,05 / 0,12 | 4,20 / 10,09 |
| Raster V4.1 Pro / V4 Pro / V4 Styles Pro | 0,21 / 0,25 / 0,10 | 17,65 / 21,02 / 8,41 |
| V3 image-to-image, inpaint, outpaint, replace/generate background | 0,04 raster / 0,08 vector | 3,36 / 6,73 |
| Создание стиля | 0,005 | 0,42 |
| **Vectorize** | **0,01** | **0,84** |
| **Remove background** | **0,01** | **0,84** |
| Crisp upscale / Creative upscale | 0,004 / 0,25 | 0,34 / 21,02 |
| Erase region / Variate / Prompt enhancement | 0,002 / 0,04 / 0,01 | 0,17 / 3,36 / 0,84 |

Источник: страница цен API [S29]. В Studio (не API) вектор V4.1 — 4 кредита, Basic $12/мес за 1000 → ≈$0,048, но это
ручной интерфейс [S2].

### 5.4 Каналы Recraft: какие параметры доживают до модели

| Канал | Векторные модели | `style_id` / стили | `controls` (палитра) | Цена вектора V4.1 | Доступ из РФ |
|---|---|---|---|---|---|
| Прямой API | все | да | да | $0,08 · 6,73 ₽ | иностранная карта |
| Gen-API | V4 vector / Pro vector | **нет** | `colors`, `background_color` | 20 ₽ | ₽, без VPN |
| ProxyAPI | V4, V4.1, Styles, Pro, Utility | [не проверено] | [не проверено] | «₽ за 1М токенов» — непрозрачно | ₽, без VPN |
| RouterAI | V4/V4.1 vector, Styles vector | [не проверено] | [не проверено] | 8,74 ₽ (Styles vector 5,46 ₽) | ₽; каталог = OpenRouter |
| fal | V4.1 vector, Pro vector; стили — отдельные эндпоинты `recraft/v4/create-style`, `…/style/text-to-vector` | через отдельные эндпоинты | `colors`, `background_color` | $0,08 | карта; условия fal [спорно] |
| Replicate | `recraft-v4-svg`, `-pro-svg` | нет (только prompt, aspect_ratio, size) | нет | $0,08 | карта |
| OpenRouter | V4/V4.1 vector, Styles vector | passthrough `style_id`, `style_match` | `controls`, `random_seed` | $0,08 (+$0,005 за референс-стиль) | закрыт для РФ с 27.06.2026 |

Источники: [S2] (Gen-API, ProxyAPI, RouterAI, fal, Replicate, OpenRouter — снято агентом P 23.09.2026). → Для серии в одном
стиле через российский канал без иностранной карты — RouterAI (Styles vector) или fal-стили; проверить в фазе 5 (тест P-8).

### 5.5 Данные, права, когда оправдан

- «API inputs and outputs are never used for model training… not stored» [S30]. Платный план — полная собственность и
  коммерческое использование; Free-Tier — картинки принадлежат Recraft; при любом плане Assets нельзя использовать для
  обучения ИИ (ToS 11.08.2026) [S30]. Санкционного пункта в ToS нет [S30].
- Оправдан: VEC-ILLUSTR, VEC-ICON-FILLED, VEC-PATTERN (стили Seamless Digital / Seamless Vector есть в Studio; в
  API-справочнике параметра тайлинга нет [S28]), серии с `style_id`, дешёвые вспомогательные операции (vectorize,
  removeBackground, crisp upscale, erase). Главный кандидат на ключ среди прямых API — итог в `06-gap-map.md` [мнение P].

## 6. Ideogram — типографика, прозрачность, слои текста

### 6.1 Эндпоинты и параметры (`https://api.ideogram.ai`, заголовок `Api-Key`)

| Эндпоинт | Параметры | Что даёт |
|---|---|---|
| `POST /v1/ideogram-v4/generate` (+ `/v1/ideogram-v4/async/generate`, опрос `GET /v1/generations/{id}`, вебхук с подписью Ed25519) | `text_prompt` (включает magic prompt) **или** `json_prompt`; `resolution` из списка (1024²…2048², 2560×1440, 3328×1248 и др.); `rendering_speed` TURBO/DEFAULT/QUALITY (FLASH — «coming soon», сейчас 400); `enable_copyright_detection` (Hive: лица и логотипы) | генерация 4.0; **нет** `seed`, негатива, `num_images`, стиль-кодов |
| `POST /v1/ideogram-v4/generate-transparent` | то же + `aspect_ratio` AUTO, 1x4…4x1 (18 значений), **`output_resolution` 1K/2K/4K/8K** | PNG с альфой в один проход: IMG-CUTOUT с текстом, стикеры, логотипные знаки |
| `/v1/ideogram-v4/remix` (`image_weight`), `/v1/ideogram-v4/describe` (картинка → `json_prompt`), `/v1/ideogram-v4/magic-prompt` | — | обратная инженерия промта, перенос стиля |
| `POST /v1/ideogram-v3/generate` | `seed`, `negative_prompt` («prompt takes precedence»), `num_images`, `color_palette`, **`style_codes`** (8-символьные hex-коды; несовместимы со `style_reference_images` и `style_type`), `style_type`, `style_preset` (ART_DECO, BAUHAUS, C4D_CARTOON, 90S_NOSTALGIA…), `custom_model_uri`, `style_reference_images`, **`character_reference_images`** (+маски; отдельная цена) | серии, персонаж, кастомная модель |
| `/v1/ideogram-v3/inpaint`, `/replace-background`, `/reframe` | маска; промт фона; разрешения из списка | IMG-EDIT, IMG-OUTPAINT |
| **`/v1/ideogram-v3/layerize-text`** | `image`, опц. `prompt`, `seed` | текстовые блоки (позиция, текст, шрифт, стиль) + фон с вырезанным текстом |
| `/v1/remove-background`, `/v1/remove-object`, `/v1/layerize-logos`, `/v1/async/ad-resizer`, `/v2/tool/colorways`, `/v2/tool/material-swap`, `/upscale` | ≤25 МБ, JPEG/PNG/WebP | инструменты |
| Кастомная модель v3 | датасет 15–100 картинок | стиль бренда |

Источник: OpenAPI 3.1 разработчика (37 путей) и llms.txt [S32]. Структура `json_prompt` 4.0:
`high_level_description`, `style_description` (палитра до 16 hex), `compositional_deconstruction` (фон и элементы
`obj`/`text` с `bbox` 0–1000) — модель обучена на таких подписях (C1 §10) [S32]; промтинг — у агентов D/D2.

```json
// Ideogram 4.0 · POST /v1/ideogram-v4/generate-transparent · 2026-09-23 · [не проверено]
// multipart-поля: json_prompt (этот объект), aspect_ratio, output_resolution, rendering_speed
{"high_level_description": "Round sticker badge with the word \"SALE\" in bold geometric sans, flat vector look",
 "style_description": {"color_palette": ["#2563EB", "#FFFFFF"]},
 "compositional_deconstruction": {"elements": [{"type": "text", "text": "SALE", "bbox": [380, 250, 620, 750]}]}}
```

(Схема `V4StyleDescription` и `V4CompositionalDeconstruction` в OpenAPI шире примера; поля элементов сверять по [S32].)

### 6.2 Цены, биллинг, лимиты

- API отдельно от подписки; предоплата через **Stripe** $1–300 (баланс ≤$300), авто-пополнение; ключ активен только с
  картой и положительным балансом; лимит по умолчанию — **10 одновременных запросов**; ссылки на картинки истекают [S33].
- Таблица цен API грузится скриптом вкладки «API usage costs» (из этой сети не загрузилась, 23.09.2026) [не проверено].
  По вторичным: 4.0 Turbo $0,03 · 2,52 ₽, Default $0,06 · 5,04 ₽, Quality $0,10 · 8,41 ₽ (Artificial Analysis $60/$100 за
  1000; обзор puter.com) [консенсус вторичных S36]; remove background **$0,01** · 0,84 ₽ («20x cheaper than remove.bg
  ($0.01 per image versus $0.20)» — лендинг Ideogram) [мнение вендора S35]; layerize-text $0,09 · 7,57 ₽ (fal) [S59].
- Ideogram V3 у агрегаторов: fal и Replicate $0,03/0,06/0,09, KIE $0,0175/0,035/0,05, Gen-API 7,5/15/22,5 ₽, VseGPT 7,9 ₽
  [S2]. Ideogram 4.0 и generate-transparent v4 у агрегаторов — [не проверено].

### 6.3 Условия

- «the Company agrees that it shall not use any User Input or User Output to train the Ideogram AI Model», кроме
  нарушивших Usage Policies [S34].
- **П. 2.3.1**: разработчик обязан «clearly identify on the Developer Application that any User Output… was created by the
  Ideogram AI Model (e.g., via a "Powered by Ideogram" tagline), and to display the Company's Marks… on each page within
  the Developer Application where Developer enables access to the Ideogram AI Model» [S34]. Для системы генеративного
  дизайна это страница(ы) интерфейса, где пользователь запускает генерацию; для готового сайта с ассетами — вопрос к
  агенту L.
- П. 2.3.2: запрет иных способов доступа к модели, кроме выданного API [S34]. Санкционного пункта нет; право Делавэра.
- Открытые веса Ideogram 4 — некоммерческая лицензия (C1 §10).

### 6.4 Когда оправдан

- IMG-TEXT-LATIN с точной вёрсткой (JSON с `bbox` для текста), IMG-CUTOUT с надписью в один проход (transparent v4),
  разборка готового баннера на фон + текстовые слои (layerize-text) для перевода текста в HTML [документация; качество
  не проверено — тест P-6].
- Кириллица у Ideogram 4.0: вендор заявляет «best-in-class multilingual text rendering» без списка языков [мнение
  вендора, C1 §10] — до теста не маршрутизировать IMG-TEXT-CYR.

## 7. Midjourney — официального API нет

- На 23.09.2026 у Midjourney нет публичного API; есть только «Enterprise API Survey»: «We're starting to investigate
  opening up an Enterprise API…» (заявка через typeform) [S38].
- ToS (Version Effective Date: May 27, 2026): «You may not use automated tools to access, interact with, or generate
  Assets through the Services. You may not resell or redistribute the Services or access to the Service. Only one user
  may use the Services per registered account.» Компания с выручкой > $1 млн в год владеет ассетами только на Pro/Mega;
  MJ получает бессрочную лицензию на входы и ассеты; без Stealth всё публично [S37].

| «MJ API» | Как устроено | Статус и риск |
|---|---|---|
| Gen-API, id `midjourney` | посредник; средняя генерация ≈129 с; «translate input» | нарушение ToS MJ на стороне посредника; остановка без предупреждения [S40] |
| PiAPI (`piapi.ai/midjourney-api`), apiframe.ai | посредники; страницы — SPA без условий | то же [S39, просмотрено] |
| GoAPI (`goapi.ai/midjourney-api`) | BYOA — «We can host your Midjourney accounts» с «account banning prevention», $10/мес за место; PPU на своих аккаунтах | **«We no longer provide Midjourney API»**, отсылает к LegNext.ai (страница на 23.09.2026) [S39] |
| useapi.net (Discord-бот + «automated CAPTCHA solver», балансировка нескольких MJ-аккаунтов) | автоматизация аккаунтов | **«Midjourney support… discontinued» 24.06.2026**, причина не раскрыта [S39] |
| «Midjourney V7 через MiniMax (Hailuo)» — useapi.net, `model="midjourney-v7"`, 4 картинки за вызов ≈$0,09, без флагов `--` | автоматизация потребительского аккаунта Hailuo; в официальном API MiniMax такой модели не найдено | единичный источник; условия Hailuo не проверены [S39] |

→ Midjourney в автоматический конвейер не включать: юридический риск (прямой запрет автоматизации), операционный
(два прецедента закрытия: useapi.net и GoAPI), качество V8.x в независимых аренах не замерено (C1 §10). Для «MJ-эстетики» — стиль-референсы
Recraft (`style_id`) и Nano Banana Pro (3 стиль-референса) [мнение P].

## 8. Видео-вендоры напрямую

Почти все видеомодели polza идут через KIE (`mie`) с набором параметров KIE [S1][S2]. Прямой канал нужен ради
конкретных полей; карточки и качество — у C2 (`../04-video-models/`).

### 8.1 Runway Dev API — агрегатор с собственными моделями

- Кредит $0,01, покупается в developer portal организации, налог может добавиться [S41]. Каталог: `veo3.1`,
  `veo3.1_fast`, `wan3`, `wan3_prime`, `seedance2`/`_fast`/`_mini`, `seedance2_5`, `grok_imagine_1_5`, `h3_max`, `hailuo3`
  (= MiniMax H3 2K), `happyhorse_1_0`, `gemini_omni_flash`, `gemini_omni_flash_1.1`, свои `gen4.5`, `gen4_turbo`, `aleph2`;
  картинки `gpt_image_2_5_flare`/`_sunburst`, `gemini_image3_pro`, `grok_imagine_image_2`, `seedream5_pro`, `muse_image`;
  апскейл `magnific_precision_upscaler_v2` [S41].

| Что сверх polza | Параметры | Цена (кредиты = центы) |
|---|---|---|
| **Veo 3.1 без звука и с негативом** | `audio: false`, `negativePrompt` ≤1000, first + last (только last нельзя), 4/6/8 с | veo3.1 без звука 20/с ($1,60 за 8 с · 134,51 ₽), fast 10/с ($0,80 · 67,25 ₽) |
| Gen-4.5 форматы вывода | `outputFormat`: `prores` (4444; «alpha channel… fully opaque»), `png_sequence`, `sdr_rec709_10bit`, **`hdr10`/`hlg`**, EXR/ACES; звука нет | 12/с ($0,60 за 5 с · 50,44 ₽) |
| **Aleph 2 — правка видео (VID-V2V)** | вход ≤30 с, `keyframes` ≤5, **`targetAspectRatio` — аутпейнт видео под другое соотношение** | 28/с, минимум 56 |
| Omni 1.1 первый + последний кадр | `gemini_omni_flash_1.1`, 360p–4K | 10/с |
| H3 Max детерминизм | `promptExpansionMode` disabled/balanced/quality | 5/8 (480/768p) |
| GPT Image 2.5 с `quality` | 1K/2K: low 1, medium 5, high 16, xhigh 28, max 63; 4K: 2/11/19/34/76; **по умолчанию high** | дороже прямого OpenAI в 2–3 раза |
| Magnific Precision v2 | апскейл картинки | 25 ($0,25), 150 при выходе >4096 px |

- Условия: «Inputs and Outputs may be used by the Company to train and improve its AI models» + бессрочная лицензия
  (ToU 15.09.2026); экспорт в страны под эмбарго США и лицам из списков запрещён [S42]. «Moderated generations cost the
  same as successful ones»; входы авто-кадрируются под соотношение — «can silently change your composition» [S41].
- Оправдан: Aleph-аутпейнт и правка видео, HDR/ProRes/EXR для монтажа, Magnific с опубликованной ценой; Veo без звука и
  с негативом — наравне с fal. Картинки через Runway — нет (дороже OpenAI и fal) [вывод P].

### 8.2 Luma — Ray 3.2 и нативная петля

- Luma Agents API: `POST https://agents.lumalabs.ai/v1/generations`, `model: "ray-3.2"`, `type: "video"`; промт 1–6000
  символов; 9:16, 3:4, 1:1, 4:3, 16:9, 21:9; `video.resolution` 360p (draft) / 540p / 720p (по умолч.) / 1080p;
  `video.duration` 5s | 10s; 24 fps [S43].
- **`video.loop: true` — «generates a seamlessly looping video»**: только 5 с; несовместим с 10s, `hdr`, `end_frame`,
  keyframes; со `start_frame` — можно. Единственный найденный нативный параметр петли в API на 23.09.2026 [S43]. Прочее:
  `start_frame`/`end_frame`, 1–64 ключевых кадра (`keyframe_indexes` 0–120 для 5 с), продление вперёд/назад, `hdr`,
  `exr_export` (EXR ACES2065-1) [S43].
- Цены (PAYG, «No minimum spend, no contract»; 5 с SDR): 360p $0,06 · 5,04 ₽, 540p $0,15 · 12,61 ₽, 720p $0,30 · 25,22 ₽,
  1080p $1,20 · 100,88 ₽; 10 с — ×3; HDR ×2 [S43]. Картинки `uni-1` — $0,0404 за 2K, `uni-1-max` — $0,10 [S43].
- Legacy Dream Machine API (`ray-2`, `ray-flash-2`): `loop`, `keyframes.frame0/frame1`, `concepts` (камера: `dolly_zoom`,
  `handheld`) [S44].
- Каналы: fal `luma/agent/ray/v3.2/text-to-video` и `/image-to-video` ($0,10/0,20/0,40 за с при 540/720/1080p; `loop` —
  только 5 с, SDR) и Replicate `luma/ray-3.2` ($0,15/0,30/1,20 за 5 с) [S2]; Gen-API — только Ray 2 [S2]. В polza, KIE,
  OpenRouter, AITUNNEL, RouterAI Luma нет [S2].
- Условия: Luma вправе использовать Input для «create, test, improve, train» моделей; «Services are intended for visitors
  located within the United States»; эмбарго США [S64].
- Оправдан: VID-HERO-LOOP и VID-ABSTRACT, где шов должен быть незаметен без ручной склейки: 360p-черновик петли стоит
  5 ₽ [документация; шов не проверен — тест P-10].

### 8.3 Kling — прямой API

- Новый API: `POST https://api-singapore.klingai.com/image-to-video/kling-3.0`; `contents[]`: `prompt` ≤3072 (реком. ≤2500;
  «can include positive and negative descriptions»), `first_frame` (обязателен), `last_frame`, `element` ≤3; settings:
  **`multi_shot` по умолчанию `true`**, `audio` native|off (по умолч. off), `resolution` 720p/1080p/4k, `duration` 3–15;
  `watermark_info.enabled` по умолч. false; результаты хранятся 30 дней [S45].
- Legacy `/v1/videos/image2video` (`kling-v2-5-turbo`, `kling-v2-6`, `kling-v3`): `negative_prompt` ≤2500, `image_tail`,
  `multi_shot` (по умолч. false), `multi_prompt` ≤6, `element_list` ≤3, `mode` std/pro/4k. **`camera_control` — только у
  v1.x**, у v2.5+ и v3 его нет [S45].
- Цены (1 unit = $0,14; 23.09.2026): Kling 3.0 без звука 720p **$0,084/с · 7,06 ₽**, 1080p $0,112 · 9,42 ₽, 4K $0,42 ·
  35,31 ₽; со звуком 720p $0,126, 1080p $0,168; 3.0 Turbo (со звуком) $0,112/0,14; Motion Control $0,126/0,168;
  Kling Image 3.0 — $0,028 за 1K/2K [S46]. Вход: пробный пакет 100 units за $14 (−30 % на первую покупку → $9,8 ·
  823,84 ₽), 30 дней, 5 потоков; обычные пакеты — от $700 (5000 units, 180 дней, 20 потоков) [S46].
- polza `kling/v3`: 10/12/45 ₽/с (std/pro/4K без звука) — ×1,42 к прайсу; fal — $0,084/с = прайс вендора [S1][S2][S46].
- Оправдан: негатив (legacy), элементы и мульти-шот со своими промтами, 4K; при объёме меньше $14 в месяц проще polza или
  fal [вывод P]. Доступ из РФ и способ оплаты — [не проверено].

### 8.4 MiniMax — H3 2K и регенерация

- `POST https://api.minimax.io/v2/video_generation`; `MiniMax-H3` (768P/2K, 4–15 с) и `MiniMax-H3-Max` (совместно с fal.ai,
  480P/768P, без 2K); i2v — только первый, только последний или оба кадра; при i2v соотношение берётся по картинке; команды
  камеры в скобках (`[pan]`, `[zoom]`, `[static]`) прямо в промте; `extra.prompt_expansion_mode` (H3-Max) (C2 §7) [S47].
- **Video Regeneration**: ролик H3 768P → 2K той же генерацией, $0,05/с (входные материалы исходной задачи оплачиваются
  повторно) [S47].
- Цены: H3 768P $0,08/с · 6,73 ₽, 2K $0,13/с · 10,93 ₽; H3-Max 480P $0,05 · 4,20 ₽, 768P $0,08 [S47]. polza
  `minimax/hailuo-3-max` — 9,44 ₽/с при любом разрешении (= $0,08 × 117,992) [S2].
- Условия (ToS — SPA, текст не снят) и оплата из РФ — [не проверено].

### 8.5 xAI — keyframes и last_frame

- Видео `grok-imagine-video-1.5`: `POST https://api.x.ai/v1/videos/generations`; 1–15 с; 480p (по умолч.)/720p/1080p;
  **`last_frame`** (и один, и вместе с `image` — интерполяция), **`keyframes` ≤4 `{image, timestamp_s}`** с шагом 1/3 с,
  `reference_images` ≤7, **`generate_audio: false`**; при i2v заданный `aspect_ratio` растягивает картинку; правка
  `/v1/videos/edits` (≤8,7 с, ≤720p), продление `/v1/videos/extensions` (C2 §8) [S48].
- Цены: 480p $0,08/с · 6,73 ₽, 720p $0,14 · 11,77 ₽, 1080p $0,25; вход-картинка $0,01. polza `grok-imagine-video-1-5`
  480p 1,62 ₽/с — в ~4 раза ниже прайса xAI по курсу ЦБ (канал KIE с иной экономикой или иной вариант модели) [спорно;
  тест P-12].
- Картинки `grok-imagine-image-2.0`: $0,04–0,08 (1K–2K × low/medium), `n` 1–10, соотношения 2:1, 1:2, 5:2, 20:9, 21:9;
  polza отдаёт только базовый `grok-imagine-image` ($0,02) с 1:1/2:3/3:2 (C1 §5) [S48].
- Условия (Enterprise ToS 14.08.2026): «will not use any User Content to train»; User Content удаляется ≤30 дней;
  Restricted Persons — страны под комплексными санкциями США [S49]. Batch для картинок и видео — без скидки [S48].

### 8.6 BytePlus ModelArk — Seedance напрямую

- `POST https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks`: роли `first_frame`/`last_frame`/
  `reference_*`/`draft_task`, `generate_audio` (по умолч. true), `watermark` (по умолч. false), **`camera_fixed`**,
  **`return_last_frame`**, **`draft`** (только 2.5: черновик 480p, затем финал 1080p по `draft_task.id`, id живёт 7 дней),
  **`output_format: "mov"`** (H.264 + yuv444p + PCM), `seed`, `service_tier`, `callback_url`, `execution_expires_after`
  (C2 §5) [S50].
- Разрешения: 2.0 — до 4K (HEVC 10 бит), 2.5 — до 1080p (HEVC 10 бит), fast/mini — 480p/720p; 24 fps; URL видео — 24 ч,
  ≤100 скачиваний [S50].
- Цены (22.09.2026, за с): 2.5 — 480p $0,103 · 8,66 ₽, 720p $0,231, 1080p $0,569; 2.0 — 480p $0,07 · 5,88 ₽, 720p $0,15,
  1080p $0,37, 4K $0,78; Fast 480p $0,06 (−25 % до 07.10.2026); Mini 480p $0,04 · 3,36 ₽, 720p $0,08 (−60 % до 07.10.2026 ≈
  $0,03); платят только за успешные ролики [S50]. polza: Seedance 2 480p 12,83 ₽/с, Mini 2,57 ₽/с, 2.5 480p 18,9 ₽/с [S1].
- `seedance-1-5-pro-251215` — Retired у BytePlus (замена `dreamina-seedance-2-0-mini-260615`) [S50]; polza
  `bytedance/seedance-1.5-pro` через KIE — риск исчезновения [вывод].
- ToS BytePlus (23.08.2022) санкционного пункта по ключевым словам не содержит [S51]; оплата из РФ — [не проверено].

### 8.7 Alibaba Model Studio — Wan напрямую

- Wan 3.0 (`wan3.0-video`, GA 24.08.2026): $0,05/с 480P · 4,20 ₽, $0,10 720P · 8,41 ₽, $0,20 1080P · 16,81 ₽; до 30 с;
  входы — текст, картинки, аудио, видео, документы (C2 §6) [S52]. polza `alibaba/wan-3.0` — 23,6 ₽/с при любом разрешении
  (= $0,20 × 117,992): черновик 480p через polza дороже прямого в 5,6 раза по курсу ЦБ [вывод P, S1].
- Модели и режимы сверх polza: `wan2.7-i2v` (первый кадр, первый+последний, продолжение видео, «continuation with last
  frame control»), `wan2.2-kf2v-flash` (первый+последний кадр, 5 с), `wan2.7-videoedit`, `wan2.1-vace-plus` (маска,
  продление, аутпейнт кадра); 30 fps H.264; `watermark` в API по умолч. false [S52].
- Регион Model Studio (международный) — Сингапур и др.; регистрация и оплата из РФ — [не проверено]. polza уже ходит к
  Alibaba напрямую (провайдер `Alibaba`) [S1].

### 8.8 OpenAI Sora 2 — снимается 24.09.2026

- Videos API и все `sora-2*` удаляются 24.09.2026, замены нет [S6]. Предложения «Sora 2» у агрегаторов после этой даты не
  рассматривать.

### 8.9 Видео: что даёт прямой канал сверх polza

| Задача | Параметр | Где напрямую | Цена прямого | Через polza |
|---|---|---|---|---|
| VID-HERO-LOOP | `video.loop: true` | Luma Ray 3.2 (API, fal, Replicate) | 360p 5 с $0,06 · 5,04 ₽ | нет модели |
| VID-HERO-LOOP / CINEMAGRAPH | Veo без звука + негатив «camera movement» | Vertex, fal, Runway | fast без звука 8 с $0,80 · 67,25 ₽ (fal, Runway) | звук, без негатива |
| VID-CINEMAGRAPH | `camera_fixed` | BytePlus (в справочнике API есть; поддержка у 2.x — [не проверено]) | Seedance 2.0 480p $0,07/с | только `fixed_lens` у 1.5 Pro (снята у вендора) |
| VID-CAMERA / VID-LONG | `keyframes` ≤4 по времени | xAI | 480p $0,08/с | нет |
| VID-I2V-PRODUCT | `last_frame` без первого | xAI, MiniMax | $0,08/с | нет |
| VID-LONG | Draft → финал 1080p | BytePlus (Seedance 2.5) | 480p $0,103/с | нет |
| VID-V2V | аутпейнт видео `targetAspectRatio` | Runway Aleph 2 | $0,28/с, мин. $0,56 | нет |
| VID-UPSCALE | 768P → 2K регенерацией | MiniMax | $0,05/с | нет |
| Черновики | 480p по прайсу | Alibaba Wan 3.0, MiniMax H3 Max | $0,05/с | 23,6 и 9,44 ₽/с плоско |

## 9. Topaz — апскейл картинок и видео

- Картинки: кредит = 24 Мп выхода у Gigapixel (precision), Wonder — 4 Мп, Bloom — 2 Мп, **Transparent Image Upscale — 24
  Мп и сохраняет альфу**; видео (10 с 1080p30): Proteus 4 кредита, Starlight Fast 6 / Quality 12, Astra 40, интерполяция
  Fast 1 / Quality 2 [S53].
- Цена кредита: Developer $50/мес = 500 кредитов ($0,10 · 8,41 ₽), Scale $240/мес = 3000 ($0,08 · 6,73 ₽), Starter
  $0,12 — «coming soon» [S53]. Противоречие: developer-доки пишут «No subscriptions, no minimums, no expiration», а
  страница API — месячные планы; там же «1 API credit = 32MP» рядом с «up to 24 MP… 1 credit» [S53] [спорно].
- Каналы: fal `topaz/upscale/image/precision` $0,08 за начатые 24 Мп; **`topaz/upscale/image/transparent`** — всегда 4×,
  PNG с альфой, $0,08 за начатые 24 Мп (1024² → 4096², $0,08; 2000² → 8000², $0,24); видео precision $0,10/10 с 720p …
  $0,60 4K [S59]. polza `topaz/image-upscale` 7,5–30 ₽ (×1…×8, без выбора модели), `topaz/video-upscale` 6–10,5 ₽/с [S1].
- Оправдан: IMG-UPSCALE вырезок с альфой (Transparent), выбор модели Topaz под задачу; через polza — «чёрный ящик»
  [вывод P].

## 10. Сервисы удаления фона (IMG-CUTOUT)

| Сервис | Цена за картинку | ₽ (ЦБ) | Особенности | Статус и доступ |
|---|---|---|---|---|
| Recraft `removeBackground` | $0,01 | 0,84 | **SVG на входе → SVG на выходе**; 256–4096 px, ≤16 Мп; webp/png | карта [S28][S29] |
| Ideogram `/v1/remove-background` | $0,01 (вендор) | 0,84 | заявлены стекло, отражения, волосы — «outperforms remove.bg, Photoroom, BiRefNet» | [мнение вендора S35]; Stripe |
| Bria | $0,018 | 1,51 | «лицензированные данные обучения», indemnification; видео $0,0225/с; 100 бесплатно | карта [S55] |
| Photoroom Basic | $0,02 | 1,68 | до 6000 px, green screen despill, uncertainty scoring; Plus $0,10 — тени, AI-фоны, expand | sandbox 1000/мес с водяным знаком [S54] |
| fal BEN2 | $0,025/Мп | 2,10 за 1 Мп | открытая модель | карта [S59] |
| fal Bria RMBG 2.0 / Replicate | $0,018 | 1,51 | — | [S59][S60] |
| fal BiRefNet v2, rembg | по GPU-секундам («$0 per compute seconds» на странице) | [не проверено] | `operating_resolution`, `refine_foreground`, режим «только маска» | [S59] |
| remove.bg | PAYG €1 за кредит (3 за €3); подписка €9/мес за 40 (€0,225) | 96,59 / 21,73 | до 50 Мп, 500 Мп/мин; первые 50 вызовов/мес бесплатно | **сайт закрывается 01.12.2026 (уход в Canva, API — через Leonardo.ai)** [S56] |
| Clipdrop | — | — | «Clipdrop is part of Jasper now», API через продажи | вычеркнуть [S65] |

- В polza удаления фона нет [S1]. Российские проводники: Gen-API — Ideogram Background Removal 2,5 ₽, Pixelcut 4 ₽;
  KIE — Recraft Remove Background $0,005 [S2].
- Выбор: для прозрачных иконок и 3D-объектов лучше генерировать сразу с альфой (GPT Image `background`, Ideogram
  transparent, Qwen Image 2.1 в polza) и удалять фон только у готовых фото [мнение P]. Качество кромок сервисов на наших
  ассетах — тест P-7; локальные BiRefNet/BEN2 (ONNX) — агент H и файл `05-open-weights-landscape.md`.

## 11. Сервисы векторизации (VEC-TRACE)

| Сервис | Цена | Настройки | Форматы | Замечание |
|---|---|---|---|---|
| Recraft `/images/vectorize` | $0,01 · 0,84 ₽ | нет (только формат ответа) | SVG | вход 256–4096 px [S28][S29] |
| fal `image2svg` | $0,005 · 0,42 ₽ | `colormode` color/binary, иерархия stacked/cutout, `mode` spline/polygon, `filter_speckle`, итерации — набор vtracer | SVG | [S59]; по параметрам — хостинг vtracer [вывод] |
| fal VecGlypher image-to-svg | $0,005 | `max_tokens`, размер ≤512 px по умолч. | SVG | генеративная векторизация [S59] |
| fal OmniLottie image-to-lottie | $0,10 | — | Lottie | VEC-ANIM, качество не проверено [S2] |
| Vectorizer.ai | €8,99/мес за 50 (€0,18 · 17,39 ₽) … €129 за 1000 (€0,129 · 12,46 ₽) … €4499 за 100 000 (€0,045 · 4,35 ₽) | режимы и опции в API | SVG, PDF, EPS, DXF, PNG | карты и PayPal, без счетов; тест API бесплатно; неиспользованные кредиты сгорают при отмене; есть русский интерфейс [S57] |
| Gen-API Image2svg | 1 ₽ | [не проверено] | SVG | проводник в ₽ [S2] |
| vtracer локально | 0 ₽ | полный набор | SVG | агенты G/H, `99-raw/tools/` |

- Векторизация растровой иллюстрации не заменяет векторный генератор: трассировка даёт много мелких путей и тяжёлый
  файл; для иконок и плоских иллюстраций сначала Recraft Vector, трассировку — для логотипов клиента и рисунков
  [мнение P; сравнение — агент G].

## 12. Сервисы апскейла (IMG-UPSCALE, VID-UPSCALE)

| Сервис | Цена | Параметры | Когда |
|---|---|---|---|
| Recraft crisp upscale | $0,004 · 0,34 ₽ | нет | иллюстрации и плоская графика, от 32 px [S29] |
| Recraft creative upscale | $0,25 · 21,02 ₽ | нет | «small details and faces», от 256 px [S29] |
| Topaz Gigapixel / Wonder / Bloom / Transparent | $0,08–0,12 за кредит (24/4/2/24 Мп) | выбор модели | фото, альфа [S53] |
| Magnific (API `https://api.magnific.com/v1/ai/image-upscaler`, заголовок `x-magnific-api-key`) | кредиты тарифов Magnific (бывш. Freepik API) [не проверено]; через Runway — $0,25 за картинку, $1,50 при выходе >4096 px | `scale_factor` 2x/4x/8x/16x; `optimized_for` (standard, soft_portraits, hard_portraits, art_n_illustration, videogame_assets, nature_n_landscapes, films_n_photography, 3d_renders, science_fiction_n_horror); `prompt`; `creativity`, `hdr`, `resemblance`, `fractality` −10…10; `engine` automatic/magnific_illusio/sharpy/sparkle; `filter_nsfw`; выход ≤25,3 Мп | генеративная доводка hero [S58][S41] |
| fal SeedVR2 | $0,001/Мп (seamless $0,0025/Мп) | `upscale_factor` или цель `1080p` | дешёвый апскейл, бесшовные текстуры [S59] |
| Bria Increase Resolution | $0,02 | — | [S55] |
| fal ESRGAN | $0,00111/с GPU | — | классический SR [S2] |
| MiniMax Video Regeneration | $0,05/с | 768P → 2K | видео H3 [S47] |
| Runway magnific video upscaler | $0,007/кадр (720p) | `fpsBoost` | видео [S41] |
| polza Topaz | 7,5–30 ₽ картинка, 6–10,5 ₽/с видео | только `upscale_factor` | без ключа [S1] |

- «Unlimited» в веб-приложении Magnific на API не распространяется: «API calls always run on the credit model» [S58].
- Clarity Upscaler в кэше не найден — [не проверено].

## 13. Сводная таблица: вендор → что сверх polza → доступ → цена → когда оправдан

Цены на 23.09.2026, ₽ по ЦБ 84,0657 ₽/$ и 96,5915 ₽/€; «карта» = зарубежная карта; VPN — нужен выход вне РФ.

| Вендор / сервис | Что даёт сверх polza | Доступ из РФ (оплата · сеть · ToS) | Цена (прямой канал) | Когда оправдан |
|---|---|---|---|---|
| OpenAI Images API | `background` transparent, `quality` low…max, `size` WxH, `output_format` + сжатие, `n`, маска, `partial_images`, `moderation` | карта и юрлицо страны из списка · VPN · **Россия вне списка стран** | 1024²: $0,0059–0,2107 (0,50–17,71 ₽); 4K high $0,10 (8,41 ₽) | только при зарубежном юрлице; иначе fal/AITUNNEL/Gen-API с теми же полями |
| Google Gemini API | NB 0.5K, 1:8, `thinking_level`, поиск по картинкам, video-to-image, 3 стиль-референса Pro, Batch/Flex −50 % | Google Payments · VPN · **Россия вне списка стран** | NB2 $0,045–0,151; NB Pro $0,134/0,24 (Flex $0,067/0,12) | параметры и партии Batch/Flex; разовая цена близка к polza (NB Pro 1–2K в polza на 20 % дороже) |
| Google Vertex (Agent Platform) | Veo: `generateAudio: false`, `negativePrompt`, `sampleCount` 1–4, `lossless`, `resizeMode`, правка по маске | Google Cloud · VPN · **новые клиенты из РФ не принимаются (2022)** | Veo Fast $0,10/с, Standard $0,40/с [по Gemini API; Vertex — [не проверено]] | 1–4 варианта Veo, `lossless`, правка по маске — при зарубежном GCP; негатив и «без звука» проще через fal |
| BFL | `seed`, `width`/`height`, `disable_pup`, `guidance`/`steps` (flex), `safety_tolerance`, [max], [klein], Erase, Outpainting | карта [не проверено] · VPN (таймауты) · не в «U.S.-sanctioned jurisdiction» [спорно] | pro от $0,03 (2,52 ₽), max $0,07, flex от $0,05; outpaint через fal $0,03 + $0,015/Мп | воспроизводимые серии, FLUX Erase/Outpaint; **не для конфиденциальных входов** |
| Recraft | **SVG**, `style_id`, `controls.colors`, vectorize, removeBackground (SVG→SVG), crisp/creative upscale, erase | карта · VPN (таймаут 1/3) · санкционного пункта нет | вектор $0,08 (6,73 ₽); vectorize/removeBg $0,01; crisp $0,004 | VEC-ILLUSTR, VEC-ICON-FILLED, серии; главный кандидат на ключ |
| Ideogram | 4.0 JSON-промт с `bbox`, transparent v4 до 8K, layerize-text, v3: `seed`, негатив, `style_codes`, character refs | Stripe · VPN · пункта нет; **«Powered by Ideogram»** | 4.0 $0,03/0,06/0,10 [вторичные]; removeBg $0,01 | IMG-TEXT-LATIN, вырезки с текстом, разборка баннера на слои |
| Midjourney | — (API нет) | ToS запрещает автоматизацию и перепродажу | — | не использовать в конвейере |
| Runway Dev | Veo без звука + `negativePrompt`, Gen-4.5 HDR/ProRes/EXR, Aleph 2 (аутпейнт видео), Omni 1.1 FLF, Magnific | карта · VPN · эмбарго США; **обучение на входах** | кредит $0,01; Veo fast без звука $0,10/с; Aleph $0,28/с | Aleph-правка видео, HDR/EXR; Veo без звука — если нет ключа fal |
| Luma | **`video.loop`**, keyframes 1–64, HDR/EXR, 360p-черновик | карта · VPN · «intended for… United States», эмбарго; обучение на входах | 5 с: 360p $0,06 (5,04 ₽) … 1080p $1,20 | VID-HERO-LOOP с нативным швом |
| Kling | `multi_shot`/`multi_prompt`, элементы, `negative_prompt` (legacy), `watermark_info`, 4K | карта [не проверено] · VPN · [не проверено] | 720p без звука $0,084/с (7,06 ₽); пробный пакет $9,8–14 | негатив и мульти-шот под контролем; иначе polza/fal |
| MiniMax | H3 2K, Video Regeneration → 2K, `[static]`, last frame без first | [не проверено] | H3 768P $0,08/с, 2K $0,13; H3-Max 480P $0,05 | 2K-финалы, дешёвый 480p-перебор |
| xAI | `last_frame`, `keyframes` ≤4, `generate_audio: false`, 1080p; Image 2.0, `n` 1–10, 5:2 | карта · VPN · комплексные санкции США | 480p $0,08/с; Image 2.0 $0,04–0,08 | ключевые кадры во времени; Image 2.0 |
| BytePlus ModelArk | Seedance `draft`, `return_last_frame`, `mov` yuv444p, 1080p у 2.5, 4K у 2.0, `camera_fixed` [у 2.x не проверено] | [не проверено] | 2.5 480p $0,103/с; Mini 480p $0,04; 2.0 $0,07 | черновик → финал 2.5; mov для кеинга |
| Alibaba Model Studio | Wan 480p по прайсу, kf2v (FLF), videoedit, vace (маска, аутпейнт кадра) | [не проверено] | Wan 3.0 $0,05/0,10/0,20 за с | черновики 480p (polza берёт тариф 1080p) |
| Topaz | выбор модели (Gigapixel, Wonder, Bloom), **Transparent Upscale** с альфой, видео Proteus/Starlight | карта · подписка $50/мес [спорно] | $0,08–0,12 за кредит | апскейл вырезок с альфой (через fal — без подписки) |
| Photoroom | удаление фона $0,02, тени/AI-фоны $0,10, до 6000 px | карта [не проверено] | $0,02 (1,68 ₽) | e-commerce, тени |
| Bria | удаление фона $0,018, видео-фон $0,0225/с, indemnification | карта [не проверено] | $0,018 (1,51 ₽) | юридически чистые данные обучения |
| remove.bg | — | закрывается 01.12.2026 | €1 / €0,225 за кредит | не использовать |
| Vectorizer.ai | трассировка с настройками, SVG/PDF/EPS/DXF | карты, PayPal | €0,045–0,18 за картинку по подписке | сложные логотипы клиента |
| Magnific | генеративный апскейл 2x–16x с `creativity`/`resemblance`/`engine` | кредиты тарифа [не проверено]; через Runway $0,25 | $0,25 (Runway) | финальная доводка hero |
| Clipdrop | — | влит в Jasper | — | вычеркнуть |

→ Порядок ключей по пользе на рубль (вход для `06-gap-map.md`): (1) Recraft — закрывает SVG, которого нет нигде в polza,
пакет от $1 без срока; (2) fal — один ключ к GPT Image с `background`, Luma с `loop`, Topaz Transparent, Ideogram V3,
BiRefNet/BEN2, image2svg (см. `03-aggregators-and-platforms.md`); (3) Luma — только если петли станут массовыми; (4)
Runway — Veo без звука и Aleph; (5) Kling — пробный пакет при нужде в негативе/мульти-шоте. OpenAI и Google напрямую — не
раньше, чем появится зарубежное юрлицо [мнение P].

## 14. Что проверить в живой фазе (прямые каналы и сервисы)

Бюджет фазы 5 — 2000 ₽ на polza; тесты вне polza требуют ключей (в столбце «Модель и канал» — пометка «ключ …»). Цены —
по прайсу на 23.09.2026.

| № | Код | Гипотеза | Минимальный тест | Модель и канал | Цена | Критерий успеха | Ценность |
|---|---|---|---|---|---|---|---|
| P-1 | IMG-DRAFT | за 4 ₽ polza отдаёт GPT Image 2.5 уровня medium–high | 1 картинка 1K тем же промтом, что пример OpenAI | `openai/gpt-image-2.5-sunburst` (polza) | 4 ₽ | детализация ≥ опубликованных примеров `high`; фактический размер файла 1024² | 2 |
| P-2 | IMG-CUTOUT | прозрачный фон GPT Image 2.5 чище вырезки постфактум | 2 объекта (кружка, стеклянный флакон) | fal `openai/gpt-image-2.5-flare`, `background: transparent`, `quality: medium` (ключ fal) против `qwen/image-2.1` transparent (polza) | ≈2 ₽ + 6 ₽ | альфа без ореола на тёмном и светлом фоне; стекло полупрозрачное | 3 |
| P-3 | IMG-TEXT-CYR | `thinking_level: high` у NB2 улучшает кириллицу | 2 баннера с фразой «Скидка 30 % до пятницы» minimal/high | Gemini API `gemini-3.1-flash-image` 1K (ключ Google — только при зарубежном юрлице) | ≈11 ₽ | 0 ошибок в буквах при high против ≥1 при minimal | 1 |
| P-4 | IMG-SERIES | preview-id NB в polza отвечает GA-моделью | 1 картинка 1K + сверка ответа (`model`, провайдер, `usage`) | `google/gemini-3.1-flash-image-preview` (polza) | 4,8 ₽ | ответ без ошибки; поле модели/провайдера в ответе polza | 1 |
| P-5 | VEC-ICON-FILLED | Recraft vector через российский проводник держит палитру | 2 иконки с `colors` бренда + 1 постер с кириллицей «Скидка» | Gen-API `recraft-v4` vector или RouterAI V4.1 vector (без иностранной карты) | 26–60 ₽ (3 × 8,74 или 3 × 20 ₽) | SVG валиден, ΔE палитры <5 (`color.py`), кириллица без ошибок | 3 |
| P-6 | IMG-TEXT-LATIN | layerize-text отдаёт пригодные для HTML текстовые блоки | 1 баннер с 2 строками текста | fal `ideogram/v3/layerize-text` (ключ fal) | $0,09 · 7,6 ₽ | позиции ±2 % ширины, шрифт определён, фон без следов текста | 2 |
| P-7 | IMG-CUTOUT | кромки: Recraft ≈ Bria ≈ BEN2 на волосах и стекле | 3 фото × 3 сервиса | KIE Recraft Remove Background $0,005, fal Bria $0,018, fal BEN2 $0,025/Мп (ключи fal/KIE) | ≈12 ₽ | нет ореола на тёмном фоне; волосы не срезаны (глаз + гистограмма альфы) | 2 |
| P-8 | IMG-SERIES | `style_id` Recraft даёт серию в одном стиле | создать стиль по 3 референсам + 3 иконки | прямой Recraft (ключ) или fal `recraft/v4/create-style` + `style/text-to-vector` | ≈21 ₽ | 3 из 3 иконок в одном стиле (слепая оценка заказчика) | 2 |
| P-9 | VID-HERO-LOOP | Veo без звука + негатив даёт статичную камеру без склеек | 1 ролик 4 с 720p, первый = последний кадр, негатив «camera movement, cuts» | fal `fal-ai/veo3.1/fast/first-last-frame-to-video`, `generate_audio: false` (ключ fal) или Runway `veo3.1_fast`, `audio: false` | $0,40 · 33,6 ₽ | нет дорожки звука; нет склеек; шов первый/последний кадр ratio ≤1,2 (метрика P/06) | 2 |
| P-10 | VID-HERO-LOOP | `loop: true` у Luma даёт шов без ручной склейки | 1 ролик 5 с 360p i2v | Luma Ray 3.2 draft (ключ Luma) или fal 540p | $0,06–0,50 · 5–42 ₽ | ratio шва ≤1,2; нет скачка при повторе 3 раза подряд | 3 |
| P-11 | VEC-TRACE | fal image2svg (vtracer) не хуже Recraft vectorize | 2 растровые иконки | fal `image2svg` $0,005 и Recraft vectorize $0,01 (ключи) | ≈2,5 ₽ | путей меньше при ΔE <3 к оригиналу; вес ≤ Recraft | 2 |
| P-12 | VID-ABSTRACT | Grok Video 1.5 в polza — полноценная 1.5 | 1 ролик 3 с 480p | `grok-imagine-video-1-5` (polza) | 4,9 ₽ | ffprobe: 480p, 24 fps, наличие звука; визуально — без артефактов уровня 1.0 | 2 |
| P-13 | VID-HERO-LOOP | `kling/v3` в polza без параметра `multi_shots` не режет ролик на планы | 1 ролик 3 с std без звука | `kling/v3` (polza) | 30 ₽ | нет склеек | 2 |
| P-14 | IMG-UPSCALE | Topaz Transparent сохраняет альфу вырезки | 1 PNG 1024² с альфой | fal `topaz/upscale/image/transparent` (ключ fal) | $0,08 · 6,7 ₽ | альфа сохранена, края без ореола на 4096² | 1 |

→ Что даст ключ: **fal** — P-2, P-6, P-7, P-9, P-11, P-14 (≈62 ₽ суммарно) и запасной путь для P-10 (+42 ₽); **Recraft** —
P-5 полностью и P-8; **Runway** — P-9 (альтернатива fal); **Luma** — P-10 дешевле всего. Без ключей в polza — P-1, P-4,
P-12, P-13 (≈44 ₽) и P-5 через российский проводник.

## Частые ошибки

1. **`background: "transparent"` для GPT Image через polza** — поля нет в `parameters` polza; результат будет с фоном.
   Прозрачность в polza — только `qwen/image-2.1` [S1].
2. **Перенос уровней `quality` между версиями GPT Image**: `high` у 2.5 по токенам равен `medium` у GPT Image 2, `max` у
   2.5 — `high` у 2 [проверено].
3. **Поле `negative_prompt` там, где его нет**: FLUX.2 (все каналы), Nano Banana, Veo в Gemini API, Ideogram 4.0, Kling 3 в
   новом API, Omni. У Kling 3 и Omni нежелательное пишется прозой в промте («Do not…»), у FLUX.2 и Runway Gen-4 —
   описанием желаемого («Locked camera. The camera remains still.»). Поле есть у Vertex Veo, Runway Veo, Ideogram v3,
   Kling legacy, Wan 2.5, Recraft V2/V3 [S13][S18][S22][S32][S41][S45].
4. **«Imagen 4 жив»** — снят в Vertex 30.06.2026 и в Gemini API 17.08.2026 [S12][S16].
5. **«У Midjourney есть API»** — нет; «MJ API» агрегаторов нарушают ToS и закрываются без предупреждения [S37][S39].
6. **`camera_control` у Kling 3** — был только у v1.x; `cameraControl` Vertex (Veo, только с `image`) — другой параметр, для
   3.1 не документирован [S45][S19].
7. **Kling `multi_shot` по умолчанию `true`** в новом API → фоновый ролик неожиданно режется на планы [S45].
8. **Google preview-id считать живыми**: `gemini-3-pro-image-preview` и `gemini-3.1-flash-image-preview` выключены
   25.06.2026 [S12].
9. **`image_size: "1k"`** в Nano Banana — отклоняется; только `1K`, `2K`, `4K`, `512` [S10].
10. **«Veo без звука через Gemini API»** — звук «Always on»; выключается в Vertex (`generateAudio`), fal
    (`generate_audio`), Runway (`audio`) [S13][S18][S41][S59].
11. **`enhancePrompt` в Vertex оставить по умолчанию** — `true` ломает воспроизводимость по `seed` [S18].
12. **Имена параметров одного провайдера у другого**: `fixed_lens` (polza/KIE) = `camera_fixed` (BytePlus); `seeds`
    10000–99999 (KIE Veo) ≠ `seed` uint32 (Vertex); `sound` (polza Kling) ≠ `audio` (Kling API) ≠ `generate_audio`
    (BytePlus, xAI) ≠ `generateAudio` (Vertex) ≠ `audio` (Runway) [S1][S18][S41][S45][S48][S50].
13. **Ссылку на результат хранить «на потом»**: BFL — 10 мин, Seedance — 24 ч, Recraft — ~24 ч, Veo (Gemini API) — 2 дня
    [S13][S24][S28][S50].
14. **Конфиденциальные референсы в BFL, Runway, Luma** — их условия разрешают обучение на входах [S26][S42][S64].
15. **Цена fal = прайс вендора «всегда»**: у Kling и Recraft — да, у Seedance 2.0 fal вдвое дороже BytePlus [S2][S46][S50].
16. **H3 и H3 Max — одно и то же**: polza даёт H3 Max (fal-вариант, 480/768p), 2K только у `MiniMax-H3` напрямую [S47].
17. **`grok-imagine-image` = Image 2.0** — нет, в polza базовая модель; Image 2.0 — только напрямую или fal [S48].
18. **Толщина линии SVG Recraft через CSS `stroke-width`** — обводок нет, линии — заливка [проверено].
19. **Кириллица через `text_layout` Recraft V3** — допускаются только гомоглифы латиницы [S28].
20. **remove.bg в конвейере** — сайт закрывается 01.12.2026, кредиты сгорают [S56].
21. **Sora 2 в плане** — Videos API OpenAI удаляется 24.09.2026 [S6].
22. **Покупка крупного пакета ради теста**: Kling — есть пробный за $9,8–14; Topaz — через fal без подписки [S46][S59].
23. **Забыть «Powered by Ideogram»** в интерфейсе генератора на Ideogram API [S34].
24. **GPT Image через Runway «потому что уже есть ключ»** — в 2–3 раза дороже OpenAI и fal, `quality` по умолчанию high
    [S41].
25. **Считать сеть главным барьером**: отсюда зарубежные API отвечают через VPN; барьер — оплата и условия [проверено:
    P/08].
26. **Полагаться на умолчания канала**: FLUX.2 flex — `guidance` 5 и `steps` 50 у BFL, 3,5 и 28 у fal; `quality` GPT Image
    2.5 — `auto` у OpenAI, `high` у fal и Runway; Veo `auto_fix` у fal по умолчанию переписывает промт. Один промт даёт
    разные результаты и цену — параметры задавать явно [S3][S22][S41][S59].

## Чек-лист

- [ ] Параметр проверен в `top_provider.parameters` каталога polza на сегодняшнюю дату?
- [ ] Есть ли параметр у российского проводника (Gen-API, AITUNNEL, RouterAI, ProxyAPI) или у fal — до покупки прямого ключа?
- [ ] Страна и оплата: вендор не исключает Россию списком стран, есть зарубежная карта или юрлицо?
- [ ] Условия данных: можно ли отправлять эти референсы вендору, который обучается на входах (BFL, Runway, Luma)?
- [ ] Модель жива на дату (не `-preview`, выключенный вендором; не в списке deprecations)?
- [ ] Результат скачан в пределах срока хранения (10 мин / 24 ч / 2 дня)?
- [ ] Для SVG Recraft: удалён фон-прямоугольник, заменены `width/height` и `preserveAspectRatio`, набор разрезан, решено по
      `<recraft-signature>`?
- [ ] Для видео-фона: звук выключен, мульти-шот выключен, камера зафиксирована, первый кадр = последнему?
- [ ] Цена посчитана по курсу ЦБ и сравнена с polza на той же длительности и разрешении?
- [ ] Выполнены условия атрибуции (Ideogram — «Powered by Ideogram»)?
- [ ] Нет неофициальных «MJ API» в цепочке?
- [ ] Минимальный пакет (Kling $700, Topaz $50/мес, Vectorizer €8,99/мес) оправдан объёмом, или хватает пробного/поштучного?

## Открытые вопросы и противоречия

1. Какое `quality` ставит `mie` для GPT Image 2.5 за 4/7/11 ₽ — не указано; оценка «medium–high» по цене [спорно; тест
   P-1].
2. Какая модель отвечает на preview-id Nano Banana в polza после 25.06.2026 [спорно; тест P-4].
3. Карточка Vertex Veo 3.1: «Pay-as-you-go: Not supported; Fixed quota: Supported» — как это соотносится с оплатой по
   факту и ценой; прайс Vertex на Veo не снят [не проверено].
4. `cameraControl` есть в схеме `VideoGenerationModelInstance`, но в гайдах Veo 3.1 не упомянут — работает ли с 3.1 [не
   проверено].
5. Таблица цен Ideogram API не загрузилась (вкладка «API usage costs» — «Loading current pricing»); цены 4.0 — по
   вторичным источникам (AA, puter.com) [S36].
6. Ideogram remove-background: лимит 25 МБ (OpenAPI) против 10 МБ (лендинг) [S32][S35].
7. Topaz: доки «No subscriptions, no minimums, no expiration» против месячных планов на странице API; «1 API credit = 32MP»
   против «up to 24 MP… 1 credit» [S53].
8. Kling: прайс вендора $0,084/с (720p без звука) против $0,168/с у Artificial Analysis (C2 §19) — AA, вероятно, указал цену
   со звуком 1080p [спорно].
9. polza Grok Video 1.5 480p (1,62 ₽/с) в ~4 раза дешевле прайса xAI ($0,08/с) — та ли модель и то ли разрешение [спорно;
   тест P-12].
10. Цены FLUX Erase и FLUX Outpainting в доках BFL не опубликованы; ориентир — fal `flux-2-pro/outpaint` $0,03 + $0,015/Мп
    [S59] [не проверено для BFL напрямую].
11. Россия и Google Cloud в 2026 году — источник 2022 года; fal ссылается на санкции ЕС и UK — применимость к РФ [спорно;
    агент L].
12. «Imagen 4» у KIE и VseGPT при снятии у Google — устаревшие витрины или подмена модели [спорно].
13. `camera_fixed` у Seedance 2.x — поле есть в общем справочнике API, поддержка моделями 2.x не подтверждена [не проверено].
14. Цена Magnific за вызов в собственном API не снята; известна только цена через Runway ($0,25) [S41][S58].
15. `seedance-1-5-pro` снят у BytePlus, но есть в polza через KIE — сколько проживёт [не проверено].
16. «Midjourney V7 через MiniMax (Hailuo)» — официальное партнёрство или только в потребительском приложении; API MiniMax
    такой модели не показывает [единичный источник S39].
17. Условия MiniMax, Kling, Alibaba Model Studio по странам и данным не сняты (SPA или не найдены) [не проверено].
18. Шов нативной петли Luma не измерен ни на одном публичном образце [не проверено; тест P-10].
19. Developer Terms Recraft (приоритетнее ToS для API) не прочитаны — санкционный пункт возможен там [не проверено].
20. Batch API −50 % для GPT Image 2.5 — объявлен для GPT Image 2 и 1.x, для 2.5 явно не сказано [не проверено].
21. Таблица размеров NB2 в гайде Google для 21:9 при 512 px даёт 792×168 (≈4,7:1) — вероятная опечатка документации [S10].

## Источники

Снято 23.09.2026, если не указано иное. «Новый» — снят для этого файла (35 URL, из них 31 содержательный); остальное —
общий кэш `99-raw/cache/` и заметки соседей. Счёт: 65 позиций — 35 прочитаны целиком или по всем разделам темы, 15 —
фрагментами (ключевые пункты условий, SPA, таблицы), 15 — через заметки соседей (P, C1, C2) с выборочной сверкой.

- [S1] polza.ai — каталог `GET /api/v1/models`, снимок `99-raw/cache/polza/2026-09-23/api-v1-models.json` (поле
  `top_provider.parameters`) и опыт `99-raw/experiments/P/01-polza-providers/`. Первоисточник того, что пропускает polza.
- [S2] Агент P — заметки `99-raw/notes/wave1/P-notes.md` (§2 KIE, §3 курс, §4 Recraft, §5–§8 fal, §7 российские
  агрегаторы и OpenRouter, §10 Replicate, §12 Luma, §14 сервисы) и опыты P/02–P/05. Сводка первоисточников, собранная P.
- [S3] OpenAI — «Image generation», developers.openai.com/api/docs/guides/image-generation. Параметры 2.5, маски,
  модерация, ограничения; первоисточник.
- [S4] OpenAI — карточки моделей `gpt-image-2.5-sunburst`, `gpt-image-2.5-flare`, `gpt-image-2` (developers.openai.com/api/
  docs/models/…). Токенные цены, лимиты по тирам.
- [S5] OpenAI — API changelog (08.09.2026 — выпуск 2.5; 20.08.2026 — прозрачность у `gpt-image-2`; JSON в edits).
- [S6] OpenAI — Deprecations (Sora 2 и Videos API — 24.09.2026; `gpt-image-1` — 23.10.2026; 1.5/1-mini — 01.12.2026; DALL·E —
  12.05.2026).
- [S7] OpenAI — «Supported countries and territories», developers.openai.com/api/docs/supported-countries. Россия
  отсутствует.
- [S8] OpenAI — «Your data», developers.openai.com/api/docs/guides/your-data (новый). Обучение, 30 дней логов, ZDR.
- [S9] Агент C1 — опыт `99-raw/experiments/C1/02-gpt-image-token-cost/` (порт калькулятора OpenAI, сверен с таблицей до
  цента). [проверено]
- [S10] Google — «Nano Banana image generation», ai.google.dev/gemini-api/docs/image-generation. `image_size`, thinking,
  grounding, референсы, ограничения.
- [S11] Google — «Gemini Developer API pricing», ai.google.dev/gemini-api/docs/pricing (таблицы разобраны из HTML).
  Standard/Batch/Flex, Veo, Omni, Free vs Paid по данным.
- [S12] Google — Gemini API release notes, ai.google.dev/gemini-api/docs/changelog (GA NB 28.05.2026, снятие preview
  25.06.2026, Imagen 17.08.2026, Omni GA 27.08.2026, deprecated sampling 21.07.2026).
- [S13] Google — «Generate videos with Veo 3.1 in Gemini API», ai.google.dev/gemini-api/docs/veo (таблица параметров
  разобрана из HTML).
- [S14] Google — «Video generation in the Gemini API» (ai.google.dev/gemini-api/docs/video) и гайд Omni Flash через заметки
  C2 §1.
- [S15] Google — «Available regions for Google AI Studio and Gemini API», ai.google.dev/gemini-api/docs/available-regions
  (новый). Россия отсутствует.
- [S16] Google Cloud — «Imagen 4», docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate (таблицы
  из HTML): Discontinued endpoints, дата 30.06.2026.
- [S17] Google Cloud — «Veo 3.1», docs.cloud.google.com/gemini-enterprise-agent-platform/models/veo/3-1-generate (новый).
  GA-id, регион, способы потребления.
- [S18] Google Cloud — `VideoGenerationModelParams`, …/reference/rest/Shared.Types/VideoGenerationModelParams (новый).
- [S19] Google Cloud — `VideoGenerationModelInstance`, …/Shared.Types/VideoGenerationModelInstance (новый). `cameraControl`,
  `mask`, `referenceImages`.
- [S20] Google Cloud — «Generate videos from an image» и «Extend videos», …/gemini-enterprise-agent-platform/models/video/
  (новые; просмотрены разделы REST). `negativePrompt`, `sampleCount` 1–4, `seed` uint32, продление ≤37 с.
- [S21] TechCrunch (Ron Miller), «Amazon, Microsoft and Google have suspended cloud sales in Russia», 10.03.2022 (новый).
  Заявление Google Cloud; вторичный, но с прямой цитатой.
- [S22] Black Forest Labs — API reference FLUX.2 [pro]/[max]/[flex]/[klein] (OpenAPI, docs.bfl.ml/api-reference/…).
- [S23] BFL — «Pricing» (docs.bfl.ml/quick_start/pricing) и bfl.ai/pricing.
- [S24] BFL — «FLUX Erase», docs.bfl.ml/flux_tools/flux_erase.md (новый).
- [S25] BFL — «FLUX Outpainting», docs.bfl.ml/flux_tools/flux_outpainting.md (новый).
- [S26] BFL — FLUX API Service Terms и Developer Terms of Service (кэш `terms-2026-09-23/`).
- [S27] BFL — release notes (docs.bfl.ml/release-notes) и гайд промтов FLUX.2 («No negative prompts») через заметки C1 §3.
- [S28] Recraft — API reference: endpoints, models, image inputs (кэш `recraft-2026-09-23/`), «Seamless patterns» (Studio).
- [S29] Recraft — «Pricing» API, www.recraft.ai/docs/api-reference/pricing.md (новый).
- [S30] Recraft — «Data use and model training» и Terms of Service (11.08.2026).
- [S31] Агент P — опыт `99-raw/experiments/P/07-recraft-svg-structure/` (8 публичных SVG). [проверено]
- [S32] Ideogram — developer.ideogram.ai: llms.txt и OpenAPI 3.1 (`/openapi.json`, 37 путей; новый).
- [S33] Ideogram — «API Overview» и «API Setup» (developer.ideogram.ai/ideogram-api/*.md; новые); docs.ideogram.ai/
  plans-and-pricing/ideogram-api (новый).
- [S34] Ideogram — Developer API Agreement and Policy (кэш `terms-2026-09-23/ideogram_terms.html`): п. 2.2 обучение,
  2.3.1 атрибуция.
- [S35] Ideogram — лендинг «Remove backgrounds from images with AI», ideogram.ai/api-remove-background/ (новый). Заявления
  вендора.
- [S36] Artificial Analysis (через заметки C1 §10) и developer.puter.com/tutorials/ideogram-api-pricing (найден поиском,
  не открыт) — вторичные цены Ideogram 4.0. [просмотрено]
- [S37] Midjourney — Terms of Service, Version Effective Date 27.05.2026, docs.midjourney.com (через r.jina.ai; новый).
- [S38] Midjourney — «Enterprise API Survey», updates.midjourney.com/enterprise-api-survey/.
- [S39] useapi.net — «Midjourney API v3» docs, «Midjourney service notice» (24.06.2026), «MiniMax: Midjourney V7 Image
  Generation» (29.06.2026); goapi.ai/midjourney-api («We no longer provide Midjourney API») (новые); piapi.ai/midjourney-api
  и apiframe.ai — [просмотрено: SPA]. Неофициальные посредники.
- [S40] Gen-API — страница модели `midjourney`, gen-api.ru/model/midjourney.
- [S41] Runway — Dev API docs: api.md, guides/models.md, guides/pricing.md (кэш `runway-C2-2026-09-23/`) + заметки C2 §10.
- [S42] Runway — Terms of Use, обновлено 15.09.2026, runwayml.com/terms-of-use (новый).
- [S43] Luma — Luma Agents API: «Video generation», «Models», «Pricing» (docs.agents.lumalabs.ai) + заметки C2 §11.
- [S44] Luma — legacy Dream Machine API docs (docs.lumalabs.ai, обновлено 10.07.2026; кэш `tools-2026-09-23/luma_*`).
- [S45] Kling — API: imageToVideo (3.0/Omni), 2.6, legacy image2video, capability map (kling.ai/document-api/…) через
  заметки C2 §4.
- [S46] Kling — «API Service» pricing, klingai.com/global/dev/pricing (новый, Playwright): пакеты, пробный тариф, цены
  моделей.
- [S47] MiniMax — «Video Generation», «Create Video Generation Task», «Pay as You Go» (platform.minimax.io) + заметки C2 §7.
- [S48] xAI (SpaceXAI) — docs.x.ai: video generation, reference-to-video, images, pricing (обновлено 21.09.2026) + заметки
  C1 §5, C2 §8.
- [S49] xAI — Terms of Service — Enterprise, обновлено 14.08.2026, x.ai/legal/terms-of-service-enterprise (новый).
- [S50] BytePlus ModelArk — Create video generation task (22.09.2026), Seedance 2.0 и 2.5 tutorials, Pricing (22.09.2026),
  Model list (кэш `byteplus-C2/`) + заметки C2 §5.
- [S51] BytePlus — Terms of Service, 23.08.2022, docs.byteplus.com/en/docs/legal/docs-terms-of-service (новый).
- [S52] Alibaba Cloud — Model Studio «Video generation» и блоги Wan 3.0 (13.08 и 27.08.2026) через заметки C2 §6;
  alibabacloud.com/help/en/model-studio/regions (найден поиском) [просмотрено].
- [S53] Topaz Labs — developer.topazlabs.com «Model Pricing», «Individual Model Pricing», «Frame Interpolation»;
  www.topazlabs.com/api (планы).
- [S54] Photoroom — API pricing (кэш `tools-2026-09-23/photoroom_api_pricing.html`).
- [S55] Bria — AI Platform Pricing (кэш `tools-2026-09-23/bria_pricing.html`).
- [S56] remove.bg — www.remove.bg/pricing (новый, Playwright: закрытие 01.12.2026, переход в Canva) и API docs (кэш).
- [S57] Vectorizer.ai — Pricing (кэш `tools-2026-09-23/vectorizer_pricing.html`).
- [S58] Magnific API (бывш. Freepik API) — docs.freepik.com/pricing и «Upscaler Creative» reference (новые).
- [S59] fal.ai — страницы моделей `…/llms.txt` (кэш `fal-2026-09-23/models/`): GPT Image 2.5, Ideogram V3, Recraft, Luma
  Ray 3.2, Topaz, BiRefNet, BEN2, rembg, image2svg, VecGlypher, SeedVR2, FLUX.2 pro outpaint. Цены и схемы.
- [S60] Replicate — цены со страниц моделей (опыт P/05) и llms.txt `recraft-ai/recraft-v4-svg`.
- [S61] KIE.ai — docs.kie.ai и прайс-API (опыт P/02) — провайдер `mie` у polza.
- [S62] OpenRouter — закрытие для российских аккаунтов и IP (12.05 и 27.06.2026): через заметки P §7 (Хабр, Skillbox
  Media, nnets.ru, ProxyAPI). [консенсус]
- [S63] Агент P — опыт `99-raw/experiments/P/08-access-probe/` (31 хост без ключей). [проверено]
- [S64] Условия fal (AUP, Terms), Replicate (ToS), Luma (ToS, 14.05.2026) — кэш `terms-2026-09-23/`.
- [S65] Clipdrop — страница API (кэш `tools-2026-09-23/clipdrop_api.html`): «Clipdrop is part of Jasper now».
