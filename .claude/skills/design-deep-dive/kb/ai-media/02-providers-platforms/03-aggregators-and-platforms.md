# Агрегаторы и платформы: каналы доступа к мировым медиа-моделям помимо polza

Волна 1 · агент P · 2026-09-23 · источников: прочитано целиком ≈70, просмотрено ≈120 · опытов: P/01–P/12 · снимок каталога
polza 2026-09-23 · курс ЦБ РФ на 23.09.2026: 84,0657 ₽/$, 96,5915 ₽/€ (`99-raw/experiments/P/02-kie-vs-polza/cbr_2026-09-23.xml`).

Файл отвечает на вопрос «где ещё взять ту же мировую модель или то, чего нет в polza, почём и с какими рисками».
API и клиент polza — `01-polza-api.md`, параметры и цены polza как данные — `02-polza-models-params-prices.md` (агент B);
прямые API вендоров и сервисы-инструменты — `04-direct-apis-and-services.md`; открытые веса — `05-open-weights-landscape.md`;
итог «разрыв → вариант → ключ» — `06-gap-map.md`. Возможности моделей — `../03-image-models/`, `../04-video-models/`.

## Выжимка для агента

1. **Считай polza фасадом KIE.ai** для 37 из 44 медиа-моделей (провайдер `mie`): у всех 21 видео запасного провайдера
   нет, сбой или изменение у KIE = сбой у polza → §1.1–1.2 [документация: каталог polza `include_providers`, описания
   параметров с упоминанием KIE].
2. **Не переносить параметры вендора на polza**: у тех же моделей polza не выставляет `background: transparent` (GPT Image
   2.5), `resolution`/`duration` 4 с и Veo 3.1 Lite (Veo), `first_frame`/`last_frame` и `return_last_frame` (Seedance 2/2.5),
   `multi_shots`/elements (Kling 3), 2K (MiniMax H3), `seed`/`steps`/`guidance` (FLUX.2) — сверяй поле `parameters`
   каталога → §1.4 [документация].
3. **Плоский тариф = цена максимального разрешения**: Wan 3.0 (23,6 ₽/с), Wan 3.0 Prime (33,0), MiniMax H3 Max (9,44),
   HappyHorse 1.0/1.1 у polza стоят как 1080p/768p даже на 480p — дешёвые тесты этих моделей вести через каналы с
   разбивкой по разрешению или не вести → §1.5 [вывод P по каталогам; проверить `usage.cost_rub` в фазе 5].
4. **polza ≈ цена KIE × 1,4–1,8** (в ₽ по курсу ЦБ) на пересекающихся моделях; Z-Image ×4,2, FLUX.2 ×2,4 — за наценку
   платишь рублями, СБП, счётом и одним API → §1.3, §4 [вывод P по прайсам KIE и polza].
5. **Модель есть у OpenRouter, но нет в polza** — первым проверяй российские перепродавцы его каталога: RouterAI
   (≈ цена OpenRouter × 109 ₽/$), AITUNNEL (× 170 ₽/$), ProxyAPI (видео × 137–145, картинки OpenAI × 303 ₽/$) → §2
   [документация: публичные каталоги, эмпирика P].
6. **Recraft Vector за рубли**: RouterAI 8,74 ₽ (V4/V4.1 vector, passthrough `style`, `controls`, `text_layout`; V4 Styles
   vector 5,46 ₽ с `style_id`), Gen-API 20 ₽ (без `style_id`, Pro vector 75 ₽), ProxyAPI (цена «за 1М токенов» —
   непрозрачна); у AITUNNEL вектора Recraft нет → §2 [документация].
7. **Gen-API — для экзотики, не для основных моделей**: даёт Ideogram V3, удаление фона (Pixelcut 4 ₽, Ideogram 2,5 ₽),
   Qwen Image Layered 12,5 ₽, SeedVR2, Luma Ray 2 modify, Sora 2 (снята 24.09.2026), PixVerse Transition, GPT Image 2.5 с `quality` и
   прозрачностью, но на пересечениях с polza дороже в 2–4 раза (≈ цена fal × 250 ₽/$); выключай `translate_input`
   (по умолчанию `true`, перевод платный) → §2.1 [документация].
8. **OpenRouter для РФ закрыт**: платежи — с 12.05.2026, аккаунты и IP — с 27.06.2026; используй его публичные
   каталоги (`/api/v1/images/models`, `/api/v1/videos/models`) как эталон цен и параметров, но не как канал → §3.4
   [консенсус: 3 независимых источника].
9. **KIE напрямую** — самый дешёвый широкий каталог (Recraft Remove Background $0,005, Crisp Upscale $0,0025, Ideogram V3
   $0,0175–0,05, Veo 3.1 Lite $0,15 за 8 с, Seedream 5 Pro Layer Decomposition $0,035), но оплата зарубежная, «stability may
   be slightly lower than official providers» (сам KIE), 14 дней хранения → §3.1 [документация KIE].
10. **fal** — самый широкий каталог (1239 эндпоинтов, 23.09.2026): Recraft V4/V4.1/Styles vector, Luma Ray 3.2 с `loop`,
    Z-Image Turbo Seamless Tiling, Ideogram Transparent, Qwen Image Layered, Seedream Layerize, BiRefNet/BEN2/Bria,
    Topaz (включая Transparent Upscale), SeedVR2, OmniLottie; новый аккаунт — 2 одновременных запроса; медиа по
    умолчанию публичны; кредиты сгорают через 365 дней → §3.2 [документация fal].
11. **Replicate** продаёт официальные модели по прайсу, иногда дешевле fal (Wan 3 480p $0,025/с против $0,05), иногда
    дороже вдвое (Kling v3 std $0,168/с против $0,084; Seedance 2, PixVerse v6) — сравнивай по позиции → §3.3, §4.
12. **Seedance дешевле всего у BytePlus напрямую** ($0,07/с 480p для 2.0; $0,012/с для 1.5 Pro 480p без звука); fal
    берёт ×2, KIE ×1,3–1,4 от BytePlus → §4 [документация BytePlus по заметкам C2, прайсы fal/KIE].
13. **Нативная видео-петля вне polza — только Luma Ray 3.2** (`loop: true`, 5 с, SDR, i2v 540p $0,15 / 720p $0,30 за
    ролик) через fal, Replicate или Runware (`settings.loop`; черновик 360p напрямую у Luma $0,06 за 5 с — файл 04); у WaveSpeed
    Luma без `loop`; у polza, KIE, OpenRouter и российских агрегаторов Luma нет → §3.2 [документация fal].
14. **Бесшовная текстура — моделью**: fal `fal-ai/z-image/turbo/tiling` ($0,02/Мп, `tiling_mode` both|horizontal|vertical);
    шов публичного примера не отличим от внутренней структуры → §3.2 [проверено: 99-raw/experiments/P/06-tiling-seam-check,
    1 образец вендора].
15. **Скачивай результат сразу**: Recraft ~24 ч, Gen-API ссылки 24 ч, KIE ссылки на скачивание 20 мин и файлы 14 дней,
    fal ≥ 7 дней (заголовок `X-Fal-Object-Lifecycle-Preference`), BFL ссылка 10 мин, polza 7 дней → §5 [документация].
16. **Без VPN и иностранной карты** доступны только российские агрегаторы: polza, Gen-API, ProxyAPI, AITUNNEL, RouterAI,
    VseGPT, BotHub, GPTunnel; KIE, fal, Replicate и вендоры — зарубежная оплата и санкционные оговорки → §6.
17. **Сеть из среды заказчика — не барьер**: зарубежные API отвечают через VPN с раздельной маршрутизацией (видят LT),
    российские — напрямую; барьер — оплата и условия → §6 [проверено: 99-raw/experiments/P/08-access-probe].
18. **Держи второй канал на ключевые модели** с другим поставщиком внизу цепочки: polza (KIE) + RouterAI/AITUNNEL
    (цепочка OpenRouter) или Gen-API (цепочка fal) → §7 [мнение P].
19. **Не отправляй фото клиентов в BFL API и Luma без согласия**: их условия разрешают обучение на входах; Ideogram и
    Recraft API — не обучаются; KIE молчит → §8 [документация ToS].
20. **Для 152-ФЗ**: ни одна медиа-модель polza не хранит данные в РФ (`stores_data_in_russia=false`), фото уходят за
    рубеж по цепочке polza → KIE → вендор → §8 [документация каталога].
21. **Midjourney через API — только неофициально** (Gen-API id `midjourney` и т. п.): у MJ официального API нет, риск
    нарушения условий и внезапной блокировки → §2.1, §8 [документация MJ по заметкам C1].
22. **BotHub и GPTunnel не включать в маршрутизацию до проверки**: медиа-каталог и цены отдаются только по ключу → §2
    [документация].
23. **VseGPT — не основной канал медиа**: каталог отстаёт (новейшая картинная модель — GPT Image 2 от 22.04.2026) → §2.
24. **Сравнивай цены в одной единице**: картинка 1K/2K/4K при явном качестве; видео — 5 с без звука 480p/720p/1080p; у
    polza Veo 3.1 — «за запрос» (8 с, звук включён у KIE по умолчанию) → §4.
25. **Id моделей проверяй по дате**: у Google preview-модели Nano Banana выключены 25.06.2026, а в polza остались id
    `google/gemini-3-pro-image-preview` и `…-3.1-flash-image-preview` — что реально вызывается, [не проверено] → §1.6.

## 1. Канал polza изнутри: кто реально генерирует

### 1.1. Провайдеры за медиа-моделями (каталог `GET /api/v1/models?include_providers=true`, 2026-09-23 08:47)

| Группа | Провайдер (`providers[].name`) | Модели | Запасные провайдеры |
|---|---|---|---|
| Видео (21) | `mie` | 16: Veo 3.1 Fast/Quality, Kling 3 и 2.6, Motion Control 3/2.6, Seedance 1.5 Pro/2/2 Fast/2 Mini/2.5, Wan 2.5/2.6, Grok Imagine Video 1.5, Gemini Omni Video, Topaz Video | нет |
| Видео | `Alibaba` | Wan 3.0, HappyHorse 1.0/1.1 | нет |
| Видео | `openrouter` | MiniMax H3 Max, Wan 3.0 Prime (`providers: []`) | нет |
| Картинки (23) | `mie` | 21 модель: GPT Image 2.5, GPT-5.4 Image 2, GPT Image 1.5, GPT-5 Image, FLUX.2 Pro/Flex, Seedream 4/4.5/5 Lite/5 Pro, Qwen Image/2/2.1, Z-Image, Grok Image, Nano Banana 2.5/2/2 Lite/Pro, Topaz | у Nano Banana: `bananalab`, Google (`google-vertex/global`, `google-ai-studio`, `…/flex`, `…/priority`), `cloud-ru`; у GPT-5.4 Image 2 и GPT-5 Image — `openai` (токены) |
| Картинки | `google-vertex/global` | Nano Banana 2 GA (`google/gemini-3.1-flash-image`) | `google-ai-studio`; `parameters` пусты у обоих |
| Картинки | `openai` | GPT-5 Image Mini | нет |

- `fal`: в changelog polza v1.5.0 (23.04.2026) «Провайдер fal.ai — медиа-генерация через fal.ai», но на 23.09.2026 через
  `falai` идут только 2 TTS (`minimax/speech-2.8-hd`, `…-turbo`) [документация: каталог; опыт `99-raw/experiments/P/01-polza-providers`].
- `bananalab` (v1.2.2, 12.03.2026) — второй источник Nano Banana с той же ценой, что у `mie`, и до 14 референсов у NB Pro
  (у `mie` — 8) [документация].
- `cloud-ru` у Nano Banana — только текстовые токены, без параметров картинки → генерации картинки через него, вероятно,
  нет [не проверено].
- Все 44 медиа-модели и все их провайдеры: `is_fz152_compliant=false`, `stores_data_in_russia=false`,
  `is_hosted_on_polza_infrastructure=false` [документация, заметки B §3].

### 1.2. `mie` = KIE.ai: доказательства

1. Описания параметров в каталоге polza прямо называют KIE: `bytedance/seedance-2-5`, `…-2-mini` — «auto передаётся в KIE
   как adaptive»; `bytedance/seedance-2` — «1080p — по документации KIE для Seedance 2»; `gemini-omni-video` — «Будет
   передано в KIE как video_list» [документация]. В OpenAPI polza пример ошибки медиа — `provider_name: "kie"` (заметки B §3).
2. Id моделей polza совпадают со slug'ами KIE: `seedream/5-pro-text-to-image`, `gpt-image-2-5-flare`, `gemini-omni-video`,
   `grok-imagine-video-1-5` ↔ «Grok Imagine Video 1.5 Preview» [документация docs.kie.ai, `99-raw/cache/kie-2026-09-23/llms.txt`].
3. Набор параметров Veo 3.1 у polza (`generationType` TEXT_2_VIDEO | FIRST_AND_LAST_FRAMES_2_VIDEO | REFERENCE_2_VIDEO,
   `enableTranslation`, `watermark`, `seeds` 10000–99999, id `veo3`/`veo3_fast`) = старый Veo API KIE
   `POST /api/v1/veo/generate` (`model` veo3 | veo3_fast | veo3_lite) [документация `old-model_veo3-api_generate-veo-3-video.md`].
4. `openai/gpt-5-image@mie` (соотношения 1:1/3:2/2:3, до 5 файлов, `isEnhance`, `mask_url`) = «4o Image API» KIE
   (`size` 1:1/3:2/2:3, до 5 `files_url`, `isEnhance`) → под именем «GPT-5 Image» у `mie`, вероятно, модель GPT-4o image
   [спорно: маски в текущих доках KIE нет].

Вывод: `mie` — KIE.ai напрямую или через посредника; официального подтверждения polza нет [спорно, улики сильные].

### 1.3. Что следует из цепочки polza → KIE → вендор

- **Наценка**: цены polza ≈ цены KIE в $ × 120–150 ₽ (× 1,4–1,8 к курсу ЦБ): GPT Image 2.5 1K/2K/4K 4/7/11 ₽ против
  $0,03/0,05/0,08 (2,52/4,20/6,73 ₽); NB Pro 13,5/18 ₽ против $0,09/0,12; NB2 4,8/7,2/10,8 против $0,04/0,06/0,09; Seedream
  4.5 5 против $0,0325; Qwen 2.1 3/6 против $0,02/0,04; Topaz 2K/4K 7,5/15 против $0,05/0,10; Veo 3.1 Fast 45 против $0,30
  (8 с 720p); Veo 3.1 Quality 187,5 против $1,25; Kling 3 std/pro/4K без звука 10/12/45 ₽/с против $0,07/0,09/0,335;
  выбросы — Z-Image 1,4 против $0,004 (×4,2), FLUX.2 Pro/Flex ×2,38 [вывод P: `99-raw/experiments/P/02-kie-vs-polza/kie_pricing_2026-09-23.json`
  и каталог polza]. Для токенных провайдеров polza переводит $ по 117,992 ₽/$ (= ЦБ × 1,40; заметки B §3).
- **Параметры**: polza выставляет подмножество параметров KIE (иногда из старой версии API KIE) — §1.4.
- **Надёжность**: KIE сам предупреждает «We are not perfect… Our overall stability may be slightly lower than official
  providers» [документация `docs.kie.ai`, Getting Started §10]; лимит 20 новых задач за 10 с на аккаунт, 429 без очереди.
- **Данные**: политика конфиденциальности KIE описывает только хранение e-mail; об обучении на входах и выходах — ничего;
  в классификации провайдеров polza (`osobennosti/privacy.mdx`) медиа-провайдеров (`mie`, `bananalab`, `falai`) нет [документация].
- **Хранение**: KIE хранит сгенерированные файлы 14 дней, логи 2 месяца, загрузки 24 ч; polza копирует результат к себе на
  7 дней [документация KIE, заметки B].

### 1.4. Параметры, которые есть у KIE или вендора и не выставлены polza (на тех же моделях)

| Модель polza | Чего нет в polza | Где есть | Зачем сайту |
|---|---|---|---|
| `openai/gpt-image-2.5-sunburst`, `gpt-image-2-5-flare` | `background` transparent/opaque/auto; `quality` low…max; `output_format`/`output_compression` | KIE (`background`), OpenAI, fal, OpenRouter, AITUNNEL, Gen-API | IMG-CUTOUT без удаления фона; дешёвый `low` для черновиков ($0,006 за 1024²) |
| `google/veo3`, `google/veo3_fast` | `resolution` 720p/1080p/4k, `duration` 4/6/8, модель Lite, `negativePrompt`, `personGeneration` | KIE (новый API), Google, fal, OpenRouter, AITUNNEL | ролик 4 с дешевле, Lite для перебора ($0,03/с 720p без звука у fal) |
| `bytedance/seedance-2`, `-2-fast`, `-2-mini`, `-2-5` | `first_frame_url` + `last_frame_url`, `return_last_frame`, `reference_audio_urls`, 4K у 2.0, `output_format` mov у 2.5, Draft mode 2.5 | KIE, BytePlus, OpenRouter (`frame_images` first/last), fal | VID-HERO-LOOP (первый = последний кадр), склейка роликов по последнему кадру |
| `kling/v3` | `multi_shots` + `multi_prompt` (до 5 шотов), `kling_elements` (`@element`) | KIE, Kling API; `negative_prompt`, `cfg_scale` — OpenRouter/AITUNNEL passthrough | VID-LONG, консистентность объекта |
| `minimax/hailuo-3-max` | 2K; `aigc_watermark` | KIE (MiniMax H3 2K $0,065/с), OpenRouter (`minimax/hailuo-3` 2K $0,13/с) | hero-видео выше 768p |
| `black-forest-labs/flux.2-pro`, `-flex` | `seed`, `steps`, `guidance`, `safety_tolerance`, `output_format`, `disable_pup` | BFL, fal, OpenRouter/AITUNNEL passthrough (`steps`, `guidance`, `safety_tolerance`); у KIE тоже нет | воспроизводимость серии, точность промта без «апсэмплинга» |
| `qwen/image-2.1` | соотношения 21:9 и 9:21; `enhance_prompt` по умолчанию true у KIE (у polza false) | KIE | баннер-лента 21:9 |
| `google/gemini-3-pro-image-preview` | до 14 референсов (у `mie` 8), `output_format` | `bananalab` (14), Google | серия по мульти-референсу |
| `topaz/image-upscale` | выбор модели Topaz (Standard, High Fidelity, Wonder, Bloom, Transparent) | Topaz API, fal | прозрачный апскейл, «креативный» апскейл |

[документация: каталог polza, доки KIE (`99-raw/cache/kie-2026-09-23/`), fal (`99-raw/cache/fal-2026-09-23/models/`), OpenRouter]

### 1.5. Скрытая наценка плоских тарифов polza

| Модель polza | Тариф polza, ₽/с | = OpenRouter × 117,992 | Цена OpenRouter по разрешениям, $/с | Переплата на 480p |
|---|---|---|---|---|
| `alibaba/wan-3.0` | 23,5984 | $0,20 (1080p) | 480p 0,05 / 720p 0,10 / 1080p 0,20 | ×4 |
| `alibaba/wan-3.0-prime` | 33,0378 | $0,28 (1080p) | 0,068 / 0,14 / 0,28 | ×4,1 |
| `minimax/hailuo-3-max` | 9,43936 | $0,08 (768p) | 480p 0,05 / 768p 0,08 | ×1,6 |
| `alibaba/happyhorse-1.1` | 15,0794 | $0,1278 (1080p) | 720p 0,0988 / 1080p 0,1278 | ×1,3 (720p) |
| `alibaba/happyhorse-1.0` | 19,9878 | $0,1694 (1080p) | 720p 0,0988 / 1080p 0,1694 | ×1,7 (720p) |

[вывод P: каталог polza + `99-raw/cache/openrouter-2026-09-23/videos_models.json`; реальное списание — проверить
`usage.cost_rub` в фазе 5]. У Wan 3.0 минимальная длительность у polza — 2 с, значит дешёвый тест 480p стоит 47,2 ₽ вместо ≈12.

### 1.6. Устаревшие имена и расхождения

- Google выключил preview-модели Nano Banana 25.06.2026 и перевёл Gemini API на GA-имена (`gemini-3-pro-image`,
  `gemini-3.1-flash-image`); в polza основными остаются `…-preview` через `mie`/`bananalab` [документация Google по
  заметкам C1; что вызывается на деле — не проверено].
- Imagen 4 снят в Gemini API 17.08.2026, а KIE и VseGPT ещё продают «Imagen 4» → проверять, не уходит ли запрос на
  другую модель [документация C1; спорно].
- Topaz Image Upscale: у polza `upscale_factor` 1/2/4/8, в доках KIE — только 1/2/4 [спорно, проверить в фазе 5].
- Seedance 2.5: polza «1080p нет», KIE перечисляет 1080p в enum (описание — только 480p/720p), BytePlus 2.5 даёт 1080p
  10 бит HEVC [спорно].

## 2. Российские агрегаторы как каналы к мировым моделям

Отбор — по фактам с их собственных страниц и документации (рейтинги «ТОП-16 агрегаторов» — только список кандидатов).

### 2.1. Сводка

| Канал | Юрлицо, оплата | Медиа-API | Откуда модели (вывод по ценам и id) | Наценка к источнику | Уникальное против polza | Цены без регистрации |
|---|---|---|---|---|---|---|
| **polza** | ООО, карты РФ, СБП, счёт с НДС; возврат неиспользованного 24 ч | `POST /api/v1/media`, async, опрос, 7 дней хранения | KIE (`mie`), Google, OpenAI, Alibaba, OpenRouter | ×1,4–1,8 к KIE | — | да, публичный каталог |
| **Gen-API** (gen-api.ru) | оплата картой РФ; «специальная цена» при объёме | задача → `processing|success|error`; long-polling или `callback_url`; `is_sync`; ссылки на файлы 24 ч; результаты: документация API — 14 дней, оферта (ред. 24.04.2026, п. 4.3) — «не более 24 ч» → планировать 24 ч [поправка X 24.09.2026 по L `../12-legal-provenance/01-licenses-by-vendor-and-channel.md` §3; было «результаты 14 дней»] | fal и прямые API (цены ≈ fal × 250 ₽/$) | ×≈3 к курсу ЦБ | Recraft V4 (vector 20 ₽, Pro vector 75), Ideogram V3 7,5/15/22,5, удаление фона Pixelcut 4 ₽ и Ideogram 2,5 ₽, Image2svg 1 ₽, Qwen Image Layered 12,5, SeedVR2 0,25 ₽/Мп, Recraft Crisp 0,8 / Creative 50, GPT Image 2.5 с `quality` и прозрачностью, Veo 3.1 Lite, Luma Ray 2, Runway Gen-4/Aleph, Sora 2 (снята 24.09.2026), PixVerse v6 Transition, SAM 3.1, Midjourney (неофиц.) | да, `gen-api.ru/pricing` |
| **ProxyAPI** (proxyapi.ru) | ИП Баринбойм А. Н. (ИНН 341003016406); карта РФ; счёт юрлицам (УПД при безнале); цены с НДС 5 % | OpenAI-совместимый `https://api.proxyapi.ru/v1`: `/images/generations`, `/videos` | каталог OpenRouter (Recraft V3–V4.1/Styles, FLUX.2, Seedream, Seedance, Kling, Veo 3.1, Wan, Hailuo, GPT Image 2.5) | видео ×137–145 ₽/$; картинки OpenAI ×303 ₽/$ | Recraft (включая vector и Styles), Veo 3.1 Lite, Seedance 2.0 4K, Kling с first+last | да, `proxyapi.ru/models/browse`; у картинок Recraft/FLUX цена «за 1М токенов» — непрозрачна |
| **AITUNNEL** (aitunnel.ru) | «комиссия уже внутри» | `/images/generations`, асинхронный `/videos` (t2v, i2v, reference, v2v) | каталог OpenRouter | ≈ ×170 ₽/$ (Wan ×144,5) | GPT Image 2.5 с `background` transparent и `quality`, Veo 3.1 Lite, Seedance 2.0 1080p, Grok Video 1.5 1080p, Sora 2 Pro (снята: API удаляется 24.09.2026), Gen-4.5, Aleph 2, Recraft V4.1 (растр) | да, `api.aitunnel.ru/public/aitunnel/models` без ключа |
| **RouterAI** (routerai.ru) | ООО «Интер» (ОГРН 1147017006950, ИНН 7017351722), публичная оферта; безналичная оплата пополнением баланса | клон API OpenRouter: `POST /api/v1/videos` → 202 + `polling_url`, `callback_url`, `frame_images` | каталог OpenRouter | ≈ ×109,3 ₽/$ (картинки) | Recraft V4/V4.1 vector 8,74 ₽, V4 Styles vector 5,46, GPT Image 2.5, Seedream 5, Qwen Image 3, Veo 3.1 Lite, Sora 2 Pro (снята: API удаляется 24.09.2026) | да, `routerai.ru/api/v1/models`; у видео одно число «seconds» без разбивки |
| **VseGPT** (vsegpt.ru) | — | txt2img, img2img, video | fal/прямые | — | Recraft V3 9,9 ₽, Ideogram V3 7,9, Kling O3, LTX 2.3, Sora 2 (снята 24.09.2026) | да; каталог медиа отстаёт (нет GPT Image 2.5, Seedream 5) |
| **BotHub** (bothub.chat) | «капсы» (внутренняя валюта) | `/v1/images/generations`, `/v1/images/edits`, шлюз к Replicate `/replicate/v1/images/generations`; `POST /openai/v1/videos/generations` (`negative_prompt`, `seed`, `generate_audio`) | Replicate и др. | ? | flux-2-max, veo-3.1, kling-v2.6… | нет — каталог моделей 401 без ключа |
| **GPTunnel** (gptunnel.ru) | — | Creative Lab: `GET /api/v2/media/models`, `POST /api/v2/media/price` (оценка без запуска), вебхуки; `deprecation_redirect_to` | ? | пример из доков: `kling-v3` 1080p 5 с = 210 ₽ (42 ₽/с) | ? | нет — только по ключу |

[документация: страницы цен и доков агрегаторов, 23.09.2026; файлы в `99-raw/experiments/P/04-ru-aggregators/` и
`99-raw/cache/{gen-api.ru,proxyapi.ru,aitunnel.ru,routerai.ru,bothub.chat,docs.gptunnel.ru}_*`]

### 2.2. Gen-API: что брать и чего избегать

- Брать: то, чего нет в polza и нет в рублях дешевле — Ideogram V3 (TURBO 7,5 ₽), удаление фона (Ideogram 2,5 ₽,
  Pixelcut 4 ₽), Qwen Image Layered (12,5 ₽), SeedVR2 апскейл (0,25 ₽/Мп), Image2svg (1 ₽), PixVerse v6 Transition
  (720p без звука 11,25 ₽/с), Veo 3.1 Lite (720p без звука 7,5 ₽/с) [документация `genapi_prices_2026-09-23.txt`].
- Не брать: модели, которые есть в polza, — Nano Banana Pro 37,5 ₽ (polza 13,5), NB2 1K 20 ₽ (4,8), Seedream 4.5 10 ₽ (5),
  Kling V3 std 42 ₽/с (10), Veo 3.1 Fast 25 ₽/с (polza 45 ₽ за 8 с), Grok Video 1.5 480p 20 ₽/с (1,62) [документация].
- Параметры: у Recraft V4 — `model` image|vector, `pro`, `aspect_ratio`, `colors`, `background_color`; **нет `style_id`**
  (серии по стилю через Gen-API не собрать) [документация `gen-api.ru/model/recraft-v4/api`].
- `translate_input: true` по умолчанию — промт переводится на английский моделью GPT-4.1 за отдельные деньги; для
  кириллицы в картинке перевод вреден (надпись переведётся) → выключать [документация, вывод P].
- Midjourney (`midjourney`): неофициальный доступ, у MJ нет API → только для исследований, не для продакшена [спорно].

### 2.3. RouterAI, AITUNNEL, ProxyAPI: три витрины одного каталога

- Каталоги трёх каналов совпадают с медиа-каталогом OpenRouter по id и составу (Recraft, Seedream 5, Qwen Image 3, Grok
  Image 2.0, Kling v3 std/pro, Veo 3.1/Fast/Lite, Seedance 1.5 Pro/2.0/Fast/Mini/2.5, Wan 3.0/Prime, Hailuo 3/3 Max,
  HappyHorse, Sora 2 Pro (снята: API удаляется 24.09.2026), Gen-4.5, Aleph 2, FLUX 3 Video) [документация: публичные каталоги, 23.09.2026].
- Соотношение цен к OpenRouter устойчиво по моделям: RouterAI 109,285 ₽/$ (Recraft V4.1 3,82 ₽ = $0,035; vector 8,74 = $0,08;
  Seedream 4.5 4,37 = $0,04; GPT Image 2.5 0,0032786 ₽ за выходной токен = $30/1М), AITUNNEL 170 ₽/$ (Recraft V4.1 5,95 ₽;
  Veo 3.1 Fast 720p без звука 13,6 ₽/с = $0,08; Kling v3 std 14,28 = $0,084), ProxyAPI 137–145 ₽/$ на видео (Veo 3.1 Fast
  720p 11,58 ₽/с; Kling v3 std 11,58) и 303 ₽/$ на токенах GPT Image 2.5 (9100 ₽/1М выходных) [вывод P].
- Риск цепочки: OpenRouter закрыт для российских аккаунтов с 27.06.2026 (§3.4), значит эти витрины работают через
  иностранного посредника или напрямую с поставщиками — внезапная недоступность вероятнее, чем у прямого канала [мнение P].
- Параметры проходят как у OpenRouter: у Recraft passthrough `style`, `controls`, `text_layout`, у V4 Styles — `style_id`,
  `style_match`, `controls`, `random_seed`; у FLUX.2 — `steps`, `guidance`, `safety_tolerance`; у Kling v3 — `negative_prompt`,
  `cfg_scale`; у Veo — `personGeneration`, `negativePrompt`, `conditioningScale`, `enhancePrompt` [документация OpenRouter
  `…/images/models/<id>/endpoints`, `…/videos/models`; пропускают ли витрины passthrough — не проверено].

## 3. Зарубежные платформы как каналы

### 3.1. KIE.ai (kie.ai, docs.kie.ai) — поставщик polza

- API: всё асинхронно; `POST https://api.kie.ai/api/v1/jobs/createTask` (`model`, `callBackUrl`, `input`) → `taskId`;
  `GET /api/v1/jobs/recordInfo?taskId=`; вебхук с проверкой подписи; старые отдельные API для Veo 3.1, 4o Image, Runway,
  Suno, Flux Kontext. Загрузка файлов — `kieai.redpandaai.co/api/file-{url,stream,base64}-upload` (хранение 24 ч); ссылки
  на скачивание (`/api/v1/common/download-url`) живут **20 минут** [документация].
- Лимиты: 20 новых задач за 10 с на аккаунт (≈100+ одновременно), при превышении 429 без очереди; лимиты на ключ
  (час/день/всего) и белый список IP [документация].
- Цены: 1 кредит = $0,005; публичный прайс `POST https://api.kie.ai/client/v1/model-pricing/page` (489 строк: чат 83,
  видео 269, картинки 110, музыка 27; `pageSize` ≤ 100) — в прайсе есть столбец «falPrice» (цена fal по данным KIE,
  справочно) [документация, `99-raw/experiments/P/02-kie-vs-polza/kie_pricing_2026-09-23.json`].
- Уникальное против polza: Recraft Remove Background ($0,005; вход ≤ 5 МБ, 16 Мп, сторона 256–4096) и Crisp Upscale
  ($0,0025); Ideogram V3 (t2i, edit с маской, remix, reframe; `style` AUTO|GENERAL|REALISTIC|DESIGN, `negative_prompt`,
  `seed`, TURBO/BALANCED/QUALITY $0,0175/0,035/0,05) и Character; Imagen 4 Fast/Standard/Ultra $0,02/0,04/0,06 (статус
  модели у Google — снята в Gemini API); Seedream 5 Pro Layer Decomposition (база + PNG-слои, промт и `<bbox>`; 1K/1.5K
  $0,035, 2K $0,07); Grok Imagine Image 2.0 segment map/edit; Qwen Image 3/3 Pro; Wan 2.7 Image; Runway Gen-4 (5 с 720p
  $0,06) и Aleph ($0,55); PixVerse V6 (First & Last Frame Transition, extend; 1–15 с, 360p–1080p, `seed`); Wan 2.7 Video
  Edit (с `negative_prompt`); Kling 3.0 Omni, Kling V3 Turbo; Hailuo 2.3/02; Veo 3.1 Lite (720p 8 с $0,15), Get 1080P
  ($0,025), Get 4K ($0,60) [документация docs.kie.ai, прайс].
- Не везде «на 30–50 % дешевле официальных»: Seedance 2 у KIE 480p $0,095/с, 720p $0,205/с против BytePlus $0,07/$0,15;
  Veo 3.1 — «25 % официальной цены» (Fast 720p 8 с $0,30 против $0,80–1,20 у Google/fal) [вывод P].
- `nsfw_checker` по умолчанию false (фильтр KIE выключен, фильтр вендора остаётся) — для сайта это не проблема, но
  модерацию входа своих пользователей делать самим [документация].
- Оплата: карты Visa/MasterCard, PayPal, WeChat, счета (по данным страницы биллинга); криптовалюты не найдено
  [документация частично, `…/kie_pricing_raw/…billing.json`].

### 3.2. fal.ai — самый широкий каталог

- API: очередь `POST https://queue.fal.run/<endpoint-id>` (`Authorization: Key …`) → статус, результат, отмена; вебхуки;
  синхронно `https://fal.run/<id>`; стриминг, WebSocket; резервные домены `falrun.com`, `queue.falrun.com`; автоповторы
  до 10 раз (503/504/429/сеть), фолбэк на эквивалентный эндпоинт после 5 неудач (`x-app-fal-disable-fallback`);
  `X-Fal-Request-Timeout`, `X-Fal-No-Retry` [документация `fal.ai/docs`, кэш `99-raw/cache/fal-2026-09-23/`].
- Для агента: схема и цена любой модели — `https://fal.ai/models/<endpoint-id>/llms.txt`; поиск моделей без ключа —
  `GET https://api.fal.ai/v1/models?q=…`; цена по API — `GET https://api.fal.ai/v1/models/pricing?endpoint_id=` (с ключом)
  [документация «Agent-Readable Surfaces»].
- Параллельность: новый аккаунт — 2 одновременных запроса, растёт от суммы оплат за 4 недели до 40; очередь не
  отклоняет [документация].
- Уникальное против polza (id эндпоинтов, 23.09.2026): `fal-ai/recraft/v4.1/text-to-vector` ($0,08), `…/pro/text-to-vector`
  ($0,30), `recraft/v4/create-style` + `recraft/v4/style/text-to-vector` (V4 Styles), `fal-ai/recraft/vectorize`,
  `fal-ai/recraft/upscale/crisp` ($0,004); `fal-ai/ideogram/v3` и `…/generate-transparent` ($0,03/0,06/0,09),
  `…/layerize-text` ($0,09), `fal-ai/ideogram/remove-background` ($0,01); `fal-ai/qwen-image-layered` ($0,05);
  `bytedance/seedream/v5/pro/layerize` ($0,03375 за слой); `fal-ai/z-image/turbo/tiling` ($0,02/Мп); `openai/gpt-image-2.5/
  {sunburst,flare}/…` с `background`, `quality` до `max` (по умолчанию `high`!), `output_compression`; `luma/agent/ray/v3.2/
  {text,image}-to-video` с `loop`; `fal-ai/veo3.1/lite` (720p без звука $0,03/с); `fal-ai/pixverse/v6/transition`;
  удаление фона `fal-ai/birefnet/v2` (+ `/video`), `fal-ai/ben/v2/image` ($0,025/Мп), `fal-ai/bria/background/remove`
  ($0,018), `bria/video/background-removal/v3`; `fal-ai/sam-3/image` ($0,005); апскейл `topaz/upscale/image/{precision,
  transparent,…}` ($0,08 за начатые 24 Мп; transparent — ×4 с альфой), `fal-ai/seedvr/upscale/image` ($0,001/Мп),
  `…/seamless` ($0,0025/Мп); видео-апскейл Topaz ($0,10–0,60 за 10 с), интерполяция `topaz/interpolate/video`,
  `fal-ai/rife/video` ($0,0013/с GPU), `fal-ai/film/video`; `fal-ai/depth-anything-video` ($0,04/с); вектор и анимация
  `fal-ai/vecglypher/image-to-svg` ($0,005), `fal-ai/omnilottie/image-to-lottie` ($0,10) [документация per-model llms.txt].
- Лицензии: у каждой модели бейдж `commercial` или `research` (в каталоге 1189 commercial, 2 research, 48 без пометки);
  «Partner API» — модели партнёров [документация, `99-raw/experiments/P/03-fal-catalog/fal_models_2026-09-23.json`].

### 3.3. Replicate (часть Cloudflare с конца 2025)

- Cloudflare объявил покупку Replicate 17.11.2025 (закрытие ~2 месяца); сайт Replicate ссылается на «Replicate and
  Cloudflare» [консенсус: пресс-релиз Cloudflare, блог Cloudflare, SiliconANGLE].
- Для агента: `https://replicate.com/<owner>/<model>/llms.txt` — входы, примеры, лицензия (без цены); цена — JSON
  `billingConfig` в HTML страницы модели [документация, опыт `99-raw/experiments/P/05-price-compare/replicate_prices2.py`].
- Recraft через Replicate урезан: `recraft-ai/recraft-v4-svg` принимает только `prompt`, `aspect_ratio`, `size` (без
  `style_id`, `colors`, `random_seed`) [документация llms.txt модели].
- Где Replicate дешевле fal/OpenRouter: Wan 3 (480p $0,025/с против $0,05), Luma Ray 3.2 i2v (одинаково $0,15/0,30/1,20 за
  5 с); где дороже: Kling v3 std $0,168/с (fal/OpenRouter $0,084), Seedance 2.0 480p $0,08/с (BytePlus $0,07), PixVerse v6
  720p $0,09/с (fal $0,045) [документация страниц моделей, 23.09.2026].

### 3.4. OpenRouter — эталон цен, но не канал для РФ

- 11.05.2026 пользователи из РФ получили письмо: «OpenRouter does not support usage, billing, or payment methods associated
  with your geography… we will no longer support payment processing for your account under our compliance policies»;
  платежи картами и криптой (Coinbase) закрыты с 12.05.2026, возврат — через Stripe в окно рефанда; с **27.06.2026**
  обслуживание российских аккаунтов и IP прекращено [консенсус: Хабр 12.05.2026, Skillbox Media 19.05.2026, nnets.ru
  25.06.2026; ProxyAPI /openrouter — заинтересованный источник].
- Полезно без аккаунта: `GET https://openrouter.ai/api/v1/images/models` (53 модели), `/api/v1/videos/models` (29, с
  ценами по разрешениям и `allowed_passthrough_parameters`), `/api/v1/images/models/<id>/endpoints` (цены картинок) —
  публично [документация, кэш `99-raw/cache/openrouter-2026-09-23/`].
- ToS OpenRouter: «Restricted Models» — провайдеры моделей могут запрещать доступ из отдельных стран [документация].
- В polza через провайдера `openrouter` идут MiniMax H3 Max и Wan 3.0 Prime — зависимость от канала, закрытого для РФ
  напрямую (polza, вероятно, работает через нероссийское юрлицо) [мнение P].

### 3.5. Runway Dev API как агрегатор

- В 2026 Runway Dev API продаёт не только Gen-4.5/Aleph 2, но и Veo 3.1/Fast, Wan 3/Prime, Seedance 2/2.5/Fast/Mini, Grok
  Imagine 1.5, MiniMax H3 Max, Hailuo 3, HappyHorse, Gemini Omni Flash; кредит $0,01; центы/с: veo3.1 40 (со звуком) / 20,
  veo3.1_fast 15/10, wan3 5/10/20 (480/720/1080p), seedance2 36 (480/720p), 40 (1080p), 150 (4K), seedance2_mini 16 (мин. 64),
  h3_max 5/8, grok_imagine_1_5 10/16/29, gen4.5 12, aleph2 28 (мин. 56) [документация Runway по заметкам C2 §10].
- Нормализованный API кадров (`promptImage[].position` first/last): Veo 3.1 — first+last, `negativePrompt` ≤ 1000; ProRes
  4444 у Gen-4.5 — альфа «полностью непрозрачная» (VID-ALPHA нативно не решается) [документация, C2].

### 3.6. WaveSpeed, Runware, Together, Freepik API

- **WaveSpeedAI** (Сингапур/Гонконг; wavespeed.ai): 1056 моделей; без ключа каталог API отвечает 401, но цены вшиты в
  публичные страницы (снято 44). Есть GPT Image 2.5 без `background`, NB Pro/2, FLUX.2, Seedream 5 Pro и Layer
  Decomposition ($0,765 — подозрительно дорого), Recraft V4/V4.1 SVG $0,08 (Styles со `style_id` $0,055), Ideogram V3 с
  прозрачностью; видео Kling 3 (`negative_prompt`, `cfg_scale`), Veo 3.1, Seedance 2/2.5, Wan 3.0, Grok 1.5; Luma Ray 3.2/2
  **без `loop`**; Midjourney v8.1 (неофициально). API async + sync (~120 с), вебхук HMAC-SHA256 с 3 повторами, файлы до
  200 МБ, хранение 7 дней. ToS п. 11.5 — «collect and analyze Customer Data… to improve». Статус (Better Stack): 99,96 % за
  90 дней (~81 мин простоя). Оплата: Stripe, PayPal, WeChat Pay, Alipay, Naver Pay.
- **Runware** (Великобритания; runware.ai): цены машиночитаемо без ключа (`/docs/models/<id>/schema.json`) на уровне
  вендоров (Seedance 2.0 480p $0,07/с = BytePlus); GPT Image 2.5 с `settings.background`; Recraft V4 Vector/Styles/Pro,
  Recraft Vectorize $0,01; BiRefNet ≈$0,0006; удаление фона у видео (Bria) → WEBM/MOV с альфой, $0,05/с; **Luma Ray 3.2 с
  `settings.loop`**. Один POST или WebSocket, sync/async; вебхук без подписи (токен в URL); хранение 7 дней (`ttl`);
  неудачные генерации не списываются. Statuspage (история с 01.07.2026): 24 инцидента за 90 дней, 2 major. Оплата: карты
  Visa/MC/Amex/Discover/JCB/UnionPay.
- **Together AI** (США): медиа вторично — нет GPT Image 2.5, Seedream 5 Pro, Recraft, Kling 3, Wan 3.0, Grok, Luma; видео
  асинхронно без вебхуков; «per video» в прайсе = ставка за секунду при минимальном разрешении; промты хранятся по
  умолчанию, обучение — по согласию; ToS запрещает бенчмаркинг; пополнение от $5.
- **Magnific** (бывший Freepik API; docs.magnific.com, `api.magnific.com`, `x-magnific-api-key`): оплата по факту прекращена
  30.06.2026, Premium $20/мес за 240 тыс. кредитов/год (≈$0,001 за кредит); GPT Image 2.5 с `background: transparent`,
  Kling 3 с `negative_prompt`, Veo 3.1, Seedance 2.5 (`camera_motion`), апскейлеры Magnific, **SVG-иконки `text-to-icon`**;
  ссылки на результат живут 5 мин–24 ч; «Powered by Magnific» для собственных моделей; бенчмаркинг запрещён; на входах не
  обучается; magnific.com отдаёт 403 VPN-адресу машины.
- Итог: все четыре — только зарубежная оплата (крипту не принимает никто); по возможностям полезнее всех Runware (петля
  Luma, прозрачность GPT Image 2.5, Recraft SVG и vectorize, видео с альфой) при ценах уровня вендоров; Kling 3 у WaveSpeed
  и Runware — 35 ₽ (720p std, 5 с) против 50 ₽ у polza; Wan 3.0 480p — 21 ₽ против 118 [документация по заметкам помощника
  `99-raw/notes/wave1/P-notes-platforms.md`, `99-raw/experiments/P/11-other-platforms/`, 23.09.2026].

## 4. Цены: где дешевле те же модели

Полная таблица (≈35 позиций × 11 каналов, курс ЦБ 84,0657 ₽/$, единицы: картинка 1K/2K/4K при явном качестве; видео —
5 с без звука) — `99-raw/experiments/P/05-price-compare/price_table_2026-09-23.md` (скрипт `prices.py`, JSON рядом).
Ключевые строки и выводы — ниже.

### 4.1. Ключевые позиции (₽ за единицу; $ → ₽ по 84,0657; «—» — модели нет в канале)

Картинки (за 1 шт.):

| Позиция | polza | KIE | прямой API | fal | Replicate | RouterAI | AITUNNEL | Gen-API | Дешевле всего за рубли |
|---|---|---|---|---|---|---|---|---|---|
| GPT Image 2.5 Sunburst 1024², medium / high | 4 (качество не выбрать) | 2,52 (1K) | 1,11 / 4,43 (OpenAI) | = OpenAI (по умолч. `high`) | — | 1,44 / 5,76 (токены) | 2,24 / 8,96 | 7,5 / 17,5 | RouterAI (если пропускает `quality`) |
| GPT Image 2.5 3840×2160, medium / high | 11 | 6,73 (4K) | 2,19 / 8,41 | = OpenAI | — | 2,84 / 10,94 | 4,41 / 17,0 | 10 / 30 | RouterAI |
| Nano Banana Pro 1–2K / 4K | 13,5 / 18 | 7,57 / 10,09 | 11,26 / 20,18 (Google) | 12,61 / 25,22 | 12,61 / 25,22 | ≈14,7 / ≈26,2 (токены) | 11,9–22,1 | 37,5 / 75 | polza / AITUNNEL |
| Nano Banana 2 1K / 4K | 4,8 / 10,8 | 3,36 / 7,57 | 5,63 / 12,69 | 6,73 / 13,45 | 5,63 / 12,69 | ≈7,3 / — | 5,1…22,1 | 20 / 40 | polza |
| Nano Banana 2 Lite 1K | 2,9 | 1,68 | 2,82 | ≈3,5 (токены $37,5/1М) | — | ≈3,7 | 2,89 | 10,75 (Lite?) | polza ≈ AITUNNEL |
| FLUX.2 Pro 1 Мп | 5 | 2,10 | 2,52 (BFL) | 2,52 | 2,52 | ? (единицы) | 5,44 | 7,5 | polza |
| FLUX.2 Flex 1 Мп | 14 | 5,88 | 5,04 (BFL $0,06/Мп) | 4,20 ($0,05/Мп) | 5,04 | ? | 10,71 | 15 | AITUNNEL |
| Seedream 4.5 | 5 | 2,73 | 3,36 (BytePlus, по OpenRouter) | 3,36 | 3,36 | 4,37 | 6,8 | 10 | RouterAI |
| Seedream 5 Pro 1K / 2K | 5 / 10 | 2,94 / 5,88 | 3,78 / 7,57 (OpenRouter) | 5,67 / 11,35 | — | 4,92 | 7,65…22,44 | 16,9 / 33,8 | RouterAI / polza |
| Seedream 5 Lite | 4 | 2,31 | 2,94 | 2,94 | 2,94 | 3,82 | 5,95 | 8,75 | RouterAI |
| Z-Image Turbo 1 Мп | 1,4 | 0,34 | — | 0,42 | 0,42 | — | — | 1,25 | Gen-API ≈ polza |
| Qwen Image 2.1 1K / 2K | 3 / 6 | 1,68 / 3,36 | — | — | — | — | — | — | polza |
| Topaz апскейл ×2 (≈2K) / ×4 | 7,5 / 15 | 4,20 / 8,41 | ≈6,7 (Topaz, 1 кредит) | 6,73 (≤24 Мп) | — | — | — | — | polza |
| **Recraft V4.1 Vector** | — | — | 6,73 (Recraft) | 6,73 | 6,73 | **8,74** | — | 20 | **RouterAI** |
| **Ideogram V3 Balanced** | — | 2,94 | ≈5,04 | 5,04 | 5,04 | — | — | 15 | Gen-API (единственный в ₽) |
| **Удаление фона** | — | 0,42 (Recraft) | 1,51 (Bria), 1,68 (Photoroom) | 0,84 (Ideogram), 1,51 (Bria) | 1,51 (Bria) | — | — | 2,5 (Ideogram), 4 (Pixelcut) | Gen-API |

Видео (5 с без звука, ₽):

| Позиция | polza | KIE | прямой API | fal | Replicate | OpenRouter (справочно) | AITUNNEL | Gen-API | Дешевле всего за рубли |
|---|---|---|---|---|---|---|---|---|---|
| Veo 3.1 Fast 720p | 45 за ролик 8 с со звуком | 25,2 за 8 с | 42,0 (Google/Runway $0,10/с) | 42,0 | 42,0 | 33,6 | 68 | 125 | **polza** |
| Veo 3.1 Quality 720p | 187,5 за 8 с | 105,1 за 8 с | 84,1 ($0,20/с) | — | 84,1 | 84,1 | 170 | 250 | AITUNNEL (за 5 с) |
| Veo 3.1 Lite 720p | — | 12,6 за 8 с | — | 12,6 | — | 12,6 | 25,5 | 37,5 | AITUNNEL |
| Kling 3 std 720p | 50 | 29,4 | ≈ (кредиты 6/с) | 35,3 | 70,6 | 35,3 | 71,4 | 210 | **polza** |
| Kling 3 pro 1080p | 60 | 37,8 | ≈ (8/с) | 47,1 | 94,2 | 47,1 | 95,2 (720p) | 280 | **polza** |
| Seedance 1.5 Pro 480p / 720p | 6,6 / 13,1 (шаг 4 с) | — | 5,0 / 10,9 (BytePlus) | ≈4,8 / ≈10,9 | 5,5 / 10,9 | 4,8 / 10,9 | 9,8 / 22,0 | — | polza |
| Seedance 2 480p / 720p / 1080p | 64,1 / 138,4 / 344 | 39,9 / 86,2 / 214 | 29,4 / 63,0 / 155,5 (BytePlus) | 56,5 / 127,5 / 286 | 33,6 / 75,7 / 189 | 28,3 / 63,5 / 162 | 57,2 / 128,5 / 289 | ≈170 / ≈380 / — | AITUNNEL ≈ polza |
| Seedance 2 Mini 480p / 720p | 12,8 / 27,7 | 8,0 / 17,2 | 16,8 / 33,6 (промо −60 % → 12,6 на 720p) | 30,3 / 65,0 | — | 14,7 / 29,4 | 28,6 / 64,3 | ≈90 / ≈195 | **polza** |
| Seedance 2.5 480p / 720p | 94,5 / 212,6 | 58,8 / 132,4 | 43,3 / 97,1 (BytePlus) | 92,7 / 198,8 | — | — | 87,4 / 196,5 | ≈275 / ≈590 | AITUNNEL ≈ polza |
| Wan 3.0 480p / 720p / 1080p | **118 / 118 / 118** (плоско) | 16,8 / 37,8 / 67,3 | 21,0 / 42,0 / 84,1 (Runway) | 21,0 / 42,0 / 84,1 | **10,5 / 21,0 / 42,0** | 21,0 / 42,0 / 84,1 | 36,1 / — / 144,5 | 62,5 / 125 / 250 | AITUNNEL / Gen-API |
| MiniMax H3 Max 480p / 768p | 47,2 / 47,2 (плоско) | — | 21,0 / 33,6 (Runway) | — | — | 21,0 / 33,6 | 42,5 / 68 | 62,5 / 100 | AITUNNEL (480p) / polza (768p) |
| Grok Imagine Video 1.5 480p / 720p | **8,1 / 15,2** | 5,0 / 9,5 | 33,6 / 58,8 (Runway 42/67) | 33,6 / 58,8 | 33,6 | 33,6 / 58,8 | 68 / 119 | 100 / 175 | **polza** (×4–8 дешевле всех) |
| HappyHorse 1.1 720p | 75,4 (плоско) | 47,3 | — | — | — | 41,5 | 84,0 | 175 | polza |
| Topaz video ×2 (5 с) | 30 | 16,8 | — | 8,4 (1080p) | — | — | — | 100 | polza |
| **Luma Ray 3.2 i2v loop 540p / 720p** | — | — | — | 12,6 / 25,2 (за ролик 5 с) | 12,6 / 25,2 | — | — | — | нет в рублях |

[вывод P по прайсам 23.09.2026: каталог polza, `kie_pricing_2026-09-23.json`, fal llms.txt, `replicate_prices_2026-09-23.txt`,
`openrouter-2026-09-23/`, `aitunnel_{images,videos}.json`, `routerai_models.json`, `genapi_prices_2026-09-23.txt`, BytePlus и
Runway — по заметкам C2; токенные цены GPT Image 2.5 — формула C1; Seedance токены — (Ш×В×24×с)/1024]. Детальная таблица с
Replicate/ProxyAPI/VseGPT и каналами — `99-raw/experiments/P/05-price-compare/price_table_2026-09-23.md` (50 строк, 222 числа сверены с исходными
файлами). Первая оценка колонки «Дешевле всего за рубли» уточнена по полной таблице — §4.3.

### 4.2. Выводы

- **В рублях polza — самый дешёвый канал для большей части видео KIE-линейки** (Kling 3, Seedance 1.5 и 2 Mini, Grok Video
  1.5, Veo 3.1 Fast, Topaz) и для большинства картинок; у Seedance 2 / 2 Fast / 2.5 AITUNNEL и ProxyAPI на 7–40 % дешевле
  (§4.3) — разница в десятки рублей за ролик, второй российский провайдер ради цены не нужен [вывод P].
- **Исключения, где polza дороже альтернатив в рублях**: Wan 3.0 и Wan 3.0 Prime (плоский тариф 1080p: 480p у AITUNNEL
  36 ₽ за 5 с против 118), MiniMax H3 Max 480p, Seedream 4.5/5 Lite (RouterAI дешевле на 10–15 %), FLUX.2 Flex (AITUNNEL
  10,7 против 14), GPT Image 2.5 на `medium` (RouterAI 1,4 ₽ против 4 ₽ плоских) [вывод P].
- **Второй провайдер нужен ради возможностей, а не цены**: Recraft Vector (RouterAI 8,74 ₽), GPT Image 2.5 с
  `background: transparent` и `quality` (RouterAI/AITUNNEL/Gen-API), Veo 3.1 Lite и Veo с `duration` 4 с (AITUNNEL/RouterAI),
  Ideogram V3 и удаление фона (Gen-API), Luma Ray 3.2 `loop` и Z-Image tiling (только fal/Replicate — зарубежная оплата)
  [вывод P; см. `06-gap-map.md`].
- **Зарубежные каналы дешевле в 1,5–4 раза** (KIE, BytePlus, Replicate для Wan), но требуют иностранной карты и
  согласия с санкционными оговорками; экономия на бюджете фазы 5 (2000 ₽) — сотни рублей, не повод менять канал [мнение P].

### 4.3. Поправки по полной таблице (P/05) и скрытые наценки

- Veo 3.1 Fast 720p: polza 28,1 ₽ за 5 с в пересчёте (фактически 45 ₽ за 8 с со звуком) — минимум в рублях (ProxyAPI 57,9,
  AITUNNEL 68). Veo 3.1 Quality: в пересчёте на 5 с дешевле всех в рублях polza (117 ₽); по фактическому платежу — ProxyAPI
  (164 ₽ за 6 с против 187,5 ₽ за 8 с). Veo 3.1 Lite 720p: ProxyAPI 20,6 ₽ < AITUNNEL 25,5.
- FLUX.2 Pro / Flex 1 Мп: RouterAI 3,28 / 6,56 ₽ (4096 токенов = 1 Мп) дешевле polza 5 / 14. Nano Banana Pro: минимум в
  рублях — polza 13,5 (у AITUNNEL только диапазон).
- Seedance 2.0 480p: ProxyAPI ≈45,5 (оценка по токенам) < AITUNNEL 57,2 < polza 64,1; Seedance 2 Fast 480p: ProxyAPI ≈27,3
  < AITUNNEL 34,3 < polza 52,3; вне рублей BytePlus ≈ в 2,2 раза дешевле polza; цены Fast на витринах — промо BytePlus
  −25 % до 07.10.2026.
- Wan 3.0 480p: ProxyAPI 33,7 < AITUNNEL 36,1 < polza 118 (вне рублей Replicate 10,5); HappyHorse 1.1 720p: ProxyAPI 68,4 <
  polza 75,4; MiniMax H3 Max 480p: AITUNNEL 42,5 < polza 47,2 (fal — промо 10,5 до 30.09.2026).
- Seedream 5 Pro, прямой прайс — BytePlus $0,045 / $0,09; Topaz прямой API — цена кредита не опубликована; Ideogram V3
  Balanced в рублях — VseGPT 14,9 / Gen-API 15; удаление фона в рублях — Gen-API 1,2 ₽ (rembg).
- Скрытые наценки: плоские тарифы polza (Wan 480p ×3,5 к самому дешёвому рублёвому каналу); Veo 1080p у polza —
  отдельная операция +10 ₽ при $0,025 у KIE (×4,8); Gen-API ≈250 ₽/$ + платный перевод промта (`translate_input=true`);
  ProxyAPI на картинках OpenAI и Google 303 ₽/$; VseGPT 250–360 ₽/$ + подписка 399 ₽ за 30 дней; AITUNNEL 170 ₽/$ и резерв
  максимальной цены на балансе до ответа; fal ставит `quality: high` у GPT Image 2.5 по умолчанию (×4 к medium), NB2 Lite у
  fal +25 % к Google; Replicate Kling ×2 к fal.
- Вывод: второй провайдер ради экономии — точечно (1–8 ₽ за картинку, 5–85 ₽ за 5 с видео); как резерв и ради
  возможностей — AITUNNEL для видео (цены по разрешению и звуку, пополнение от 500 ₽, СБП и счёт юрлицу) и RouterAI для
  картинок (курс ×1,30 к ЦБ) [вывод P/05: `99-raw/experiments/P/05-price-compare/price_table_2026-09-23.md`].

## 5. Стиль API и обращение с файлами

| Канал | Вызов | Ожидание результата | Вебхук | Вход файлов | Хранение результата |
|---|---|---|---|---|---|
| polza | `POST /api/v1/media` (`async`), OpenAI-совместимый `/v2/images/generations` (до 120 с) | опрос `GET /api/v1/media/{id}` | `callBackUrl` (описан у Lyria) | `{type: url|base64, data}`; хранилище `TEMP_UPLOAD` 24 ч | 7 дней |
| KIE | `POST /api/v1/jobs/createTask` | `GET /api/v1/jobs/recordInfo` | `callBackUrl` + подпись | загрузка URL/поток/base64, 24 ч | 14 дней; ссылка на скачивание 20 мин |
| fal | очередь `queue.fal.run/<id>`, синхронно `fal.run/<id>`, стрим, WebSocket | статус/результат очереди | да | CDN fal (`fal_client.upload_file`), URL, data URI | ≥ 7 дней, настраивается заголовком; JSON запросов 30 дней (`X-Fal-Store-IO: 0`) |
| Replicate | `POST /v1/predictions` (`Prefer: wait` — синхронно) | опрос | да, с подписью | URL, data URI, загрузка файлов | ограниченно (см. docs «Data retention») |
| Gen-API | задача → `processing|success|error`; `is_sync` | long-polling | `callback_url` | URL | ссылки 24 ч; результаты — 14 дней по документации API, ≤ 24 ч по оферте (ред. 24.04.2026, п. 4.3) → планировать 24 ч [поправка X 24.09.2026] |
| RouterAI | `POST /api/v1/videos` → 202 + `polling_url` | опрос `GET /api/v1/videos/{id}` | `callback_url` | `frame_images` | не указано |
| AITUNNEL | `/v1/images/generations`, асинхронный `/v1/videos` | опрос | не указано | URL/base64 | не указано |
| ProxyAPI | `/v1/images/generations`, `/v1/videos` (OpenAI-совместимые) | зависит от модели | не указано | как у OpenAI | не указано |
| Recraft | `POST /v1/images/generations` (+ `/raster`, `/vector`), синхронно | ответ сразу | нет | multipart или JSON (URL / data URL) | ~24 ч; лимит 100 картинок/мин, 5 запросов/с |

[документация каналов, 23.09.2026]. Правило: результат скачивать в момент готовности и класть рядом «паспорт генерации»
(клиент `polza.py` агента B делает это для polza; для остальных каналов — тот же контракт).

## 6. Доступ из России: оплата, VPN, условия

| Канал | Оплата из РФ | Нужен VPN | Оговорки условий |
|---|---|---|---|
| polza, Gen-API, ProxyAPI, AITUNNEL, RouterAI, VseGPT, BotHub, GPTunnel | карты РФ, СБП (polza), счёт юрлицам (polza, ProxyAPI с УПД) | нет | ProxyAPI — ИП, «доступ к прокси-серверу»; данные уходят зарубежным поставщикам |
| KIE | карты Visa/MasterCard, PayPal, WeChat, счёт | сеть отвечала через VPN (P/08) | ToS не найден; политика данных минимальна |
| fal | предоплата картой (Stripe) | через VPN отвечает | AUP: нельзя из территорий под комплексными санкциями OFAC/Госдепа, ЕС, HM Treasury; ToS: не в стране под эмбарго США |
| Replicate | карта (Stripe) | через VPN отвечает | экспорт запрещён в страны под эмбарго США и лицам из SDN |
| OpenRouter | закрыто для РФ с 12.05.2026 (платежи), 27.06.2026 (аккаунты, IP) | — | — |
| OpenAI | — | — | России нет в списке поддерживаемых стран API (developers.openai.com, 23.09.2026) |
| BFL, Luma, Ideogram, Recraft, Runway | иностранная карта | через VPN отвечают | BFL: не «U.S.-sanctioned jurisdiction»; Luma, Replicate — эмбарго США |

[документация: страницы оплаты и ToS, `99-raw/cache/terms-2026-09-23/`; проверено: `99-raw/experiments/P/08-access-probe`].
Россия формально не под «комплексными» санкциями OFAC (в отличие от Крыма, ДНР, ЛНР), но широкие формулировки ЕС/UK
и блок платёжных систем делают прямую оплату нереальной без иностранного юрлица или карты [спорно, юридическая оценка — L].

## 7. Надёжность

- Поставщик polza по видео один (KIE); KIE прямо пишет, что его стабильность может быть ниже официальной; у polza
  заявлены «автоматический failover» и SLA 99,97 % (для Enterprise от 100 000 ₽/мес) — к медиа-моделям без запасного
  провайдера failover неприменим [документация polza, KIE].
- fal: очередь, автоповторы до 10 раз, фолбэк на эквивалентный эндпоинт, резервные домены; в пробе P/08 таймаутили то
  основной, то резервный домен → клиент должен переключать домен сам [документация; проверено P/08].
- Инциденты за 90 дней (Statuspage): Runway 6 (1 critical), BFL 9 (2 major, сбой кластера EU 19.08.2026), Ideogram 4
  (3 critical: v3 04.09, Reframe v3 29.08, 3.1 27.07) [проверено: `99-raw/experiments/P/12-status-pages`]. fal, Replicate,
  Recraft, Luma — не Statuspage, OpenRouter/OpenAI — таймаут; счёт несопоставим между провайдерами.
- WaveSpeed: доступность API 99,96 % за 90 дней (~81 мин простоя, Better Stack); Runware: 24 инцидента за 90 дней, 2 major
  (Statuspage с 01.07.2026) [документация, P/11].
- Правило: на ключевую модель держать второй канал с другим поставщиком внизу цепочки и единый контракт клиента
  (задача → id → опрос/вебхук → скачивание → паспорт) [мнение P].

## 8. Данные и права

| Канал | Хранение входов/выходов | Обучение на входах | Публичность URL |
|---|---|---|---|
| polza | не хранит запросы; медиа 7 дней; логи по флагу ключа 30 дней | — (зависит от поставщика) | URL на `s3.polza.ai`/`cdn.polza.ai` |
| KIE | медиа 14 дней, логи 2 мес., загрузки 24 ч | не описано | ссылки на скачивание 20 мин |
| fal | JSON 30 дней (отключается), медиа ≥ 7 дней | не заявлено в изученных доках | **публичны по умолчанию** (ACL — опция) |
| Recraft API | не хранит, «never used for model training» | нет | подписанные URL ~24 ч |
| BFL API | окно выдачи, видео удаляются после | **да** («may use Inputs and Outputs to train») | подписанная ссылка 10 мин |
| Ideogram API | — | нет (кроме нарушивших Usage Policies) | — |
| Luma | — | **да** (лицензия на Input «to… train… models») | — |
| OpenAI | до 30 дней (классификация polza) | нет по умолчанию для API | base64 в ответе |

[документация ToS и доков, 23.09.2026]. Лицензии результатов по вендорам подробно — агент L (`../12-legal-provenance/`).
Модели на открытых весах в каналах (Qwen Image 2.1, Z-Image, Wan 2.2, FLUX.2 [dev]) несут лицензию весов: у Qwen Image 2.1
и FLUX.2 [dev] она некоммерческая; бейдж `commercial` в каталоге fal — условия fal, а не лицензия весов (файл 05 §9, §11).
Recraft SVG несёт подпись происхождения `<recraft-signature>` (Ed25519) в `<metadata>` — svgo по умолчанию её удалит
[проверено: `99-raw/experiments/P/07-recraft-svg-structure`]. BFL оставляет за собой право встраивать Content Credentials.

## 9. Коммерческие условия

- polza: пополнение в ₽, возврат неиспользованных средств в течение 24 ч после оплаты, скидок за объём нет (индивидуально),
  лимиты расходов на ключ и участника (v1.4.0) [документация].
- fal: предоплатные кредиты, **сгорают через 365 дней**; 5xx не списываются, 422 может списаться; нет оплаты за очередь и
  холодный старт; аккаунт блокируется при балансе ниже порога [документация].
- Recraft API: API units покупаются заранее ($1 = 1000 единиц); ключ создаётся только при положительном балансе [документация].
- KIE: 1 кредит = $0,005; ключи с лимитами и белым списком IP [документация].
- ProxyAPI: цены с НДС 5 %; закрывающие документы только при безналичной оплате по счёту [документация].
- Gen-API: «специальная цена» при больших объёмах; перевод промта тарифицируется отдельно [документация].
- Минимальное пополнение: polza 100 ₽, AITUNNEL 500 ₽ (СБП, счёт юрлицу), Together $5, Ideogram от $1; у остальных
  российских агрегаторов на их страницах не указано [документация, P/05].
- remove.bg закрывается 01.12.2026, Clipdrop влит в Jasper — не строить на них конвейер (файл 04).

## Частые ошибки

1. Считать `mie` «ещё одним провайдером polza» — это KIE, и замена провайдера внутри polza для видео невозможна (§1).
2. Передавать в polza параметры KIE или вендора (`background`, `duration`, `resolution`, `first_frame_url`, `multi_prompt`,
   `seed` у FLUX.2) — polza их не выставляет; строгая валидация вернёт 400 или параметр молча потеряется (§1.4).
3. Оценивать цену Wan 3.0/H3 Max/HappyHorse в polza по разрешению — тариф плоский по максимуму (§1.5).
4. Сравнивать цены «за картинку» без качества (GPT Image 2.5 `low` и `max` различаются в 36 раз) и видео «за ролик» без
   длительности и звука (§4).
5. Считать OpenRouter рабочим каналом из РФ — закрыт с 27.06.2026 (§3.4).
6. Брать «Midjourney API» у агрегатора как официальный — у MJ API нет (§2.2).
7. Верить «на 30–50 % дешевле официальных» (KIE) без сверки: у Seedance 2 KIE дороже BytePlus (§3.1).
8. Оставлять результаты в облаке провайдера «на потом» — сроки от 10 минут (BFL) до 14 дней (§5).
9. Держать ссылки fal как приватные — по умолчанию они публичны (§8).
10. Отправлять фото клиентов в BFL/Luma без согласия — условия разрешают обучение (§8).
11. Для кириллицы в картинке через Gen-API оставлять `translate_input: true` — надпись переведётся (§2.2).
12. Прогонять svgo по SVG Recraft «как есть» — удалится подпись происхождения; фон-прямоугольник и
    `preserveAspectRatio="none"` останутся (§8, P/07).
13. Ошибка ИИ-агента: по памяти называть id моделей и цены (Imagen 4 «жив», `gpt-image-1` «актуален», Seedance 1.5 Pro «у
    BytePlus есть») — сверяй каталоги с датой (§1.6).

## Чек-лист

- [ ] Модель вызывается через polza и её параметры есть в `parameters` каталога polza?
- [ ] Если параметра нет — есть ли он у второго канала (KIE/RouterAI/AITUNNEL/fal) и оправдан ли второй ключ?
- [ ] Цена сравнена в одной единице (1K/2K/4K + качество; видео 5 с без звука, разрешение)?
- [ ] Для Wan 3.0 / H3 Max / HappyHorse учтён плоский тариф polza?
- [ ] Канал доступен без иностранной карты и не закрыт для РФ (OpenRouter — нет)?
- [ ] Результат скачивается сразу, срок хранения канала известен?
- [ ] Для фото клиента выбран канал без обучения на входах и есть согласие?
- [ ] Для ключевой модели есть второй канал с другим поставщиком внизу цепочки?
- [ ] Для Recraft SVG учтены фон-прямоугольник, подпись и отсутствие обводок?
- [ ] Неофициальные прокладки (Midjourney) не используются в продакшене?

## Открытые вопросы и противоречия

1. `mie` = KIE — по уликам; официального подтверждения polza нет. Какой качество-уровень GPT Image 2.5 ставит KIE/polza
   (цена 4/7/11 ₽ между `medium` и `high` прямого API) — [не проверено].
2. Пропускают ли RouterAI, AITUNNEL и ProxyAPI passthrough-параметры OpenRouter (`style_id`, `controls`, `quality`,
   `background`, `negativePrompt`) — [не проверено].
3. Цены RouterAI на видео — одно число «seconds» без разбивки по звуку и разрешению; ProxyAPI у картинок — «за 1М
   токенов» без пересчёта в картинку — непрозрачно.
4. BotHub, GPTunnel — цены медиа только по ключу; минимальные пополнения Gen-API, RouterAI, ProxyAPI на их страницах не
   указаны (AITUNNEL — от 500 ₽, polza — от 100 ₽, §9).
5. Seedance 2.5 1080p (polza «нет», KIE enum «есть», BytePlus «есть») и Topaz ×8 (polza есть, KIE нет) — расхождения.
6. KIE: условия использования (ToS) и политика обучения на данных не найдены (только privacy policy).
7. Проба доступности не дала чистого замера с российского IP (VPN с раздельной маршрутизацией) — повторить в фазе 5.
8. WaveSpeed: Layer Decomposition $0,765 против $0,035 у KIE — ошибка витрины или другой продукт; Magnific: в справке
   противоречие, доступен ли API на Premium; помогут ли UnionPay/Alipay резидентам РФ (Runware, WaveSpeed) — не проверено.
9. Qwen Image 2.1 в polza (`mie` = KIE): веса 2.1 — Qwen Research License (некоммерческая, 20.09.2026), в Alibaba Model
   Studio модели 2.1 нет → KIE, вероятно, запускает открытые веса; есть ли у KIE коммерческая лицензия Alibaba — не
   раскрыто → агент L (файл 05 §1.3, заметки C1 §8) [спорно].

## Источники

- [S1] polza.ai — каталог `GET /api/v1/models` (`include_providers=true`, `/models/catalog`), 23.09.2026, `99-raw/cache/polza/2026-09-23/`, `99-raw/experiments/P/01-polza-providers/` — первоисточник цен и параметров, высокая надёжность.
- [S2] polza docs (github.com/polza-ai/docs, 18.09.2026): `glavnoe/providers.mdx`, `gaidy/provider-selection.mdx`, `changelog.mdx`, `osobennosti/privacy.mdx`, `glavnoe/faq.mdx`, `glavnoe/enterprise.mdx` — официальная документация.
- [S3] KIE.ai — docs.kie.ai (`llms.txt`, Getting Started, Market quickstart, 40 страниц моделей в .md), 23.09.2026, `99-raw/cache/kie-2026-09-23/` — документация вендора.
- [S4] KIE.ai — публичный прайс `api.kie.ai/client/v1/model-pricing/page` (489 строк), 23.09.2026, `99-raw/experiments/P/02-kie-vs-polza/kie_pricing_2026-09-23.json`.
- [S5] KIE.ai — privacy policy, 23.09.2026, `99-raw/cache/kie.ai_privacy-policy_*.md`.
- [S6] fal.ai — документация (media expiration, pricing, queue, webhooks, concurrency, FAQ, reliability, agent surfaces), 23.09.2026, `99-raw/cache/fal-2026-09-23/`.
- [S7] fal.ai — поиск моделей `api.fal.ai/v1/models` и per-model llms.txt (80 эндпоинтов), 23.09.2026, `99-raw/experiments/P/03-fal-catalog/`, `99-raw/cache/fal-2026-09-23/models/`.
- [S8] fal.ai — Terms и Acceptable Use Policy, 23.09.2026, `99-raw/cache/terms-2026-09-23/fal_*.html`.
- [S9] Replicate — docs llms.txt, data retention, rate limits, страницы 45 моделей (billingConfig), terms, 23.09.2026, `99-raw/cache/replicate-2026-09-23/`.
- [S10] Cloudflare — пресс-релиз и блог «Replicate is joining Cloudflare», 17.11.2025; SiliconANGLE 17.11.2025 — подтверждение сделки.
- [S11] OpenRouter — `/api/v1/images/models`, `/api/v1/videos/models`, `/images/models/<id>/endpoints`, docs video/image generation, terms, 23.09.2026, `99-raw/cache/openrouter-2026-09-23/`.
- [S12] Хабр, Aule, «OpenRouter перестал принимать платежи для учеток с регионом Россия», 12.05.2026 — цитаты письма OpenRouter.
- [S13] Skillbox Media, 19.05.2026 — подтверждение блокировки платежей OpenRouter.
- [S14] nnets.ru, 25.06.2026 — прекращение обслуживания российских аккаунтов OpenRouter с 27.06.2026.
- [S15] ProxyAPI — каталог `proxyapi.ru/models/browse`, страницы моделей, docs, terms, /openrouter, 23.09.2026 — документация канала (страница /openrouter — заинтересованный источник).
- [S16] Gen-API — `gen-api.ru/pricing` (279 блоков цен), `/docs`, `/docs/generation`, страницы моделей, 23.09.2026, `99-raw/experiments/P/04-ru-aggregators/genapi_prices_2026-09-23.txt`.
- [S17] AITUNNEL — `aitunnel.ru/docs/{models,images,videos}`, публичный каталог `api.aitunnel.ru/public/aitunnel/models`, 23.09.2026.
- [S18] RouterAI — `routerai.ru/api/v1/models` (513 моделей), docs video/image generation, 23.09.2026.
- [S19] VseGPT — `vsegpt.ru/Docs/Models/{Txt2Img,Img2Img,Video}`, 23.09.2026.
- [S20] BotHub — API documentation (image, video generation), 23.09.2026.
- [S21] GPTunnel — docs Creative Lab (models, price), 23.09.2026.
- [S22] Recraft — docs API (getting started, endpoints, appendix, models, styles, data use, commercial rights, credits), 23.09.2026, `99-raw/cache/recraft-2026-09-23/`.
- [S23] OpenAI — supported countries, image generation guide, модель GPT Image 2.5 Sunburst, 23.09.2026 (кэш C1 и P).
- [S24] BFL — Terms of Service, FLUX API Service Terms, Developer Terms, 01.08.2026 ред., `99-raw/cache/terms-2026-09-23/bfl_*`.
- [S25] Ideogram — API ToS; Luma — ToS; Runway, BFL, Ideogram — статус-страницы, 23.09.2026, `99-raw/cache/terms-2026-09-23/`, `99-raw/experiments/P/12-status-pages/`.
- [S26] Luma — docs.lumalabs.ai (video generation, create generation, rate limits), обновлено 10.07.2026, `99-raw/cache/tools-2026-09-23/luma_*`.
- [S27] ЦБ РФ — официальные курсы на 23.09.2026 (XML_daily).
- [S28] Заметки соседей: B (цены polza, OpenAPI, курс 117,992), C1 (формула токенов GPT Image 2.5, Google, BFL, Ideogram, Midjourney), C2 (BytePlus, Runway Dev API, Kling API) — `99-raw/notes/wave1/{B,C1,C2}-notes.md`.
- [S29] Опыты P/06–P/08, P/12 — `99-raw/experiments/P/`.
