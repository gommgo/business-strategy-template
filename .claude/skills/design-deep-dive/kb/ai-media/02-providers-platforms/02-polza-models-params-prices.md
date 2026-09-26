# Медиа-модели polza как данные: параметры, провайдеры, формулы цены, расхождения

Волна 1 · агент B · 2026-09-23 · данные: снимок каталога polza `99-raw/cache/polza/2026-09-23/` (08:20 МСК; 23 картинки,
21 видео), `providers[]` — снимок `2026-09-23_0921`; нормализованные данные
`99-raw/cache/polza/2026-09-23/media-models.normalized.json` · источники: каталог, 28 гайдов polza, OpenAPI,
документация KIE, прайсы KIE/Google/OpenAI/OpenRouter (≈ 45 целиком) · опыты `99-raw/experiments/B/02`, `04`, `05`,
`07` · **цены — по каталогу; фактическое списание и работа функций — `[не проверено]` до фазы 5.**

API, деньги, клиент, первый живой вызов — [`01-polza-api.md`](01-polza-api.md). Возможности и качество моделей —
`../03-image-models/`, `../04-video-models/` (агенты C1, C2); промты — `../05-prompting/` (агент D); другие каналы и
где дешевле — файлы агента P в этой папке.

## Выжимка для агента

1. **Параметры и цены — только из каталога на дату** (`polza.py show MODEL`, `media-models.normalized.json`), не по
   памяти и не из OpenAPI: у 44 моделей 29 разных имён параметров, и они меняются. → §1 `[документация]`
2. **Одно понятие — разные имена**: разрешение — `image_resolution` (картинки), `resolution` (видео), `quality`
   (Seedream 4.5/5 Lite/5 Pro), `mode` (Kling 3.0, Motion Control); зерно — `seed`, у Veo — `seeds`; звук —
   `generate_audio` или `sound`. → §1.2 `[документация]`
3. **`quality` у Seedream означает разное разрешение**: 4.5 — basic 2K / high 4K; 5 Lite — 2K / 3K; 5 Pro — 1K / 2K.
   → §3.1 `[документация]`
4. **Цена считается пятью способами**: за запрос; по ступени с условиями; ступень × секунды (`unitParam: duration`);
   ставка × секунды (`video_per_second`); токены. Калькулятор — `polza_catalog.py price`. → §2
   `[проверено: 99-raw/experiments/B/02-price-calculator]`
5. **Ступень = самая точная подходящая; `[]` — запасная** и у 13 моделей равна максимуму (Seedance 1.5 Pro 135 ₽,
   Kling 3.0 45 ₽/с) → ценовые параметры всегда явно. → §2.2, §2.9 `[не проверено: какую ступень берёт polza]`
6. **Seedance 2 / 2 Fast / 2 Mini: `duration` по умолчанию 15 с, `generate_audio` — `"true"`**; «только промт» у
   Seedance 2 = 415,125 ₽, у Fast — 334,125 ₽. Ставь `duration` 4–5 и `generate_audio: "false"`. → §4.2, §6
   `[проверено: расчёт]`
7. **Звук влияет на цену только у Kling 3.0 (+40–50 %, у 4K — нет), Kling 2.6 (≈ ×2) и Seedance 1.5 Pro (×2)**; у Seedance 2/2.5/Mini/
   Fast и Wan 3.0 звук на цену не влияет, но включён по умолчанию у Seedance. → §2.6 `[документация]`
8. **Видео-референс дорожает**: Seedance 2 ×1,20–1,22, Mini ×1,22–1,26, 2.5 ×1,21; Gemini Omni v2v — 70 ₽ (720p/1080p) и
   115 ₽ (4k) за ролик независимо от длительности. → §2.6 `[документация]`
9. **Картинки-референсы бесплатны везде, кроме Seedream 5 Pro** (+0,30 ₽ за каждую сверх первой). → §2.6 `[документация]`
10. **Veo 3.1 в polza — цена за ролик без выбора длительности и разрешения** (Fast 45 ₽, Quality 187,5 ₽); у KIE по
    умолчанию 8 с, 720p, звук не отключается. → §4.2, §9 `[документация]` `[не проверено]`
11. **Плоские ставки за секунду** — Wan 3.0 (23,60 ₽/с), Wan 3.0 Prime (33,04), HappyHorse 1.0/1.1 (19,99/15,08),
    MiniMax H3 Max (9,44): 480p и 1080p стоят одинаково → для них бери максимум разрешения. → §2.4 `[документация]`
12. **Ценовые парадоксы каталога**: Seedream 4 — 3 ₽ и в 4K; Seedream 4.5 — 5 ₽ и в 4K; Nano Banana Pro 2K = 1K;
    Gemini Omni 1080p = 720p; Kling 3.0 4K со звуком = без; Qwen Image 16:9 (2,25) дешевле 1:1 (3,00). → §6
    `[документация]`
13. **Самый дешёвый валидный вызов каждой модели** — от ≈ 1 ₽ (GPT-5 Image Mini, токены, оценка) и 1,40 ₽ (Z-Image) до 187,50 ₽ (Veo Quality); все 44 тела
    проверены валидатором. → §11 `[проверено: 99-raw/experiments/B/07-model-cards]`
14. **Прозрачный фон в polza — только `qwen/image-2.1`** (`background: "transparent"` + `png`/`webp`); у GPT Image
    2.5 прозрачности в polza нет (у KIE есть). → §3.2, §10 `[документация]`
15. **Маски противоположны**: `qwen/image-2.1` — белое меняется; `openai/gpt-5-image` у `mie` — чёрное меняется;
    у провайдера `openai` маски нет. → §3.2 `[документация]`
16. **Негатив-промт в polza — только у `wan/2.5`** (≤ 500 символов); у FLUX.2, Kling 3.0, Veo — нет. → §4.2 `[документация]`
17. **Неподвижная камера параметром — только `bytedance/seedance-1.5-pro` `fixed_lens: "true"`**. → §4.2 `[документация]`
18. **Первый и последний кадр**: Veo `FIRST_AND_LAST_FRAMES_2_VIDEO` (1–2 картинки), Kling 3.0 (`images` 0–2,
    start/end), Seedance 1.5 Pro (0–2), MiniMax H3 Max (до 2); у Wan 3.0, HappyHorse — только первый кадр (`images`
    ≤ 1); у Seedance 2 массив `images` — кадры или референсы, не описано. → §4.3 `[спорно]`
19. **Kling 3.0: `aspect_ratio` по умолчанию 1:1 и игнорируется при стартовом кадре; `duration`, `mode`, `sound` —
    обязательные**; `mode` = разрешение (std 720p, pro 1080p, 4K 2160p). → §4.2 `[документация]`
20. **Одна модель у разных провайдеров — разные параметры и цены**: Nano Banana Pro у `google-vertex/global/flex` ≈
    7,94 ₽ (1–2K) против 13,50 у `mie`; NB2 flex 3,97/5,95/8,92 против 4,80/7,20/10,80. → §5
    `[документация]` `[не проверено: маршрутизация]`
21. **Токенные модели**: NB2 GA `google/gemini-3.1-flash-image` ≈ 7,93/11,89/17,84 ₽ (1K/2K/4K) и без `parameters`;
    GPT-5 Image Mini ≈ 1,00 ₽ (medium 1024²). Оценка по таблицам вендоров. → §2.5 `[не проверено]`
22. **Лимиты промта** — от 800 (Wan 2.5) и 1000 (Z-Image) до 60 000 (Veo); у Seedance 2 описание говорит «до 1536»
    при `max_length` 20 000. → §3.1, §4.1, §8 `[спорно]`
23. **Документация отстаёт от каталога**: гайды на Kling 2.5 Turbo и Seedream 3.0 — моделей нет; нет гайдов на 17
    моделей каталога; 21 расхождение — §8. Верь каталогу, спорное проверяй в фазе 5. → §8 `[документация]`
24. **Типовая задача**: hero 2K — 7 ₽ (GPT Image 2.5) / 13,50 (NB Pro) / 7,94 (NB Pro flex); петля 5 с без звука —
    10,50 (Seedance 1.5 Pro 720p 4 с) / 45 (Veo Fast) / 50 (Kling 3.0 std). → §7 `[проверено: расчёт]`

## 1. Данные

### 1.1 Файлы и команды

| Что | Где | Как обновить |
|---|---|---|
| Сырой каталог (все 411 моделей) | `99-raw/cache/polza/<дата>/api-v1-models.json` | `python3 ../../scripts/ai-media/polza_catalog.py snapshot` |
| Провайдеры каждой модели (параметры, цены) | `…/api-v1-models.providers.json` (2 МБ) | там же |
| Нормализованные медиа-модели | `…/media-models.normalized.json` (схема `polza-media-normalized/1`) | `snapshot` делает сам; `normalize SNAP [--providers SNAP2]` |
| Таблица медиа-моделей | `polza_catalog.py table SNAP` | — |
| Что изменилось | `polza_catalog.py diff 2026-09-23 latest` | перед каждой серией |
| Параметры, сетка цен, провайдеры одной модели | `python3 ../../scripts/ai-media/polza.py show MODEL [--provider P]` | — |
| Цена и проверка без файла задания | `polza_catalog.py price MODEL k=v …`, `check MODEL k=v …` | — |

Поля записи в `media-models.normalized.json`: `id`, `name`, `type`, `created`, `provider` (top), `endpoints`,
`flags` (152-ФЗ, РФ, инфраструктура polza, модерация), `unified` (единые поля §1.2 с исходным именем и типом),
`params` (как в каталоге), `param_types` (`bool_string`, `enum_string`, `number`, `file_list`, `id_list`, `url`,
`string`), `required`, `defaults`, `pricing` (`kind`, `price_params`, `rate_min`/`rate_max`, `fallback`,
`with_defaults_rub`/`rate`, сырой тариф), `price_grid` (цены по всем значениям ценовых параметров), `operations`,
`notes` (опасные умолчания, условия цены без параметра, описание против `max_length`), `doc_vs_catalog`
(кураторские расхождения с документацией), `providers` (для каждого: цена, флаги, отличия параметров от top,
пример ₽ за 1K/2K/4K). В корне: `checked`, `snapshot_fetched_at`, `source_sha256`, `fx_usd_rub_polza` (117,992),
`tier_semantics`.

### 1.2 Единые поля → параметры polza (снимок 2026-09-23)

| единое поле | параметры polza | у каких моделей |
|---|---|---|
| `prompt` | `prompt` | все, кроме: `google/gemini-3.1-flash-image`, `topaz/image-upscale`, `topaz/video-upscale` |
| `negative_prompt` | `negative_prompt` | `negative_prompt`: `wan/2.5` |
| `ref_images` | `images` | все, кроме: `google/gemini-3.1-flash-image` |
| `ref_videos` | `videos` | `videos`: `bytedance/seedance-2`, `bytedance/seedance-2-5`, `bytedance/seedance-2-fast`, `bytedance/seedance-2-mini`, `gemini-omni-video`, `kling/v2.6-motion-control`, `kling/v3-motion-control`, `topaz/video-upscale` |
| `mask` | `mask_url` | `mask_url`: `openai/gpt-5-image`, `qwen/image-2.1` |
| `aspect_ratio` | `aspect_ratio` | все, кроме: `google/gemini-3.1-flash-image`, `openai/gpt-5-image-mini`, `topaz/image-upscale`, `kling/v2.6-motion-control`, `kling/v3-motion-control`, `topaz/video-upscale`, `wan/2.6` |
| `resolution` | `image_resolution`, `resolution` | `image_resolution`: `black-forest-labs/flux.2-flex`, `black-forest-labs/flux.2-pro`, `bytedance/seedream-4`, `google/gemini-3-pro-image-preview`, `google/gemini-3.1-flash-image-preview`, `gpt-image-2-5-flare`, `openai/gpt-5.4-image-2`, `openai/gpt-image-2.5-sunburst`, `qwen/image-2.1`; `resolution`: `alibaba/happyhorse-1.0`, `alibaba/happyhorse-1.1`, `alibaba/wan-3.0`, `alibaba/wan-3.0-prime`, `bytedance/seedance-1.5-pro`, `bytedance/seedance-2`, `bytedance/seedance-2-5`, `bytedance/seedance-2-fast`, `bytedance/seedance-2-mini`, `gemini-omni-video`, `grok-imagine-video-1-5`, `minimax/hailuo-3-max`, `wan/2.5`, `wan/2.6` |
| `quality` | `quality` | `quality`: `bytedance/seedream-4.5`, `bytedance/seedream-5-lite`, `openai/gpt-image-1.5`, `seedream/5-pro-text-to-image` |
| `mode` | `mode` | `mode`: `kling/v2.6-motion-control`, `kling/v3`, `kling/v3-motion-control` |
| `duration` | `duration` | `duration`: `alibaba/happyhorse-1.0`, `alibaba/happyhorse-1.1`, `alibaba/wan-3.0`, `alibaba/wan-3.0-prime`, `bytedance/seedance-1.5-pro`, `bytedance/seedance-2`, `bytedance/seedance-2-5`, `bytedance/seedance-2-fast`, `bytedance/seedance-2-mini`, `gemini-omni-video`, `grok-imagine-video-1-5`, `kling/v2.6`, `kling/v3`, `minimax/hailuo-3-max`, `wan/2.5`, `wan/2.6` |
| `seed` | `seed`, `seeds` | `seed`: `bytedance/seedream-4`, `qwen/image-2.1`, `alibaba/happyhorse-1.0`, `alibaba/happyhorse-1.1`, `alibaba/wan-3.0`, `alibaba/wan-3.0-prime`, `gemini-omni-video`, `wan/2.5`; `seeds`: `google/veo3`, `google/veo3_fast` |
| `audio` | `generate_audio`, `sound` | `generate_audio`: `alibaba/wan-3.0`, `alibaba/wan-3.0-prime`, `bytedance/seedance-1.5-pro`, `bytedance/seedance-2`, `bytedance/seedance-2-5`, `bytedance/seedance-2-fast`, `bytedance/seedance-2-mini`; `sound`: `kling/v2.6`, `kling/v3` |
| `fixed_camera` | `fixed_lens` | `fixed_lens`: `bytedance/seedance-1.5-pro` |
| `multi_shot` | `multi_shots` | `multi_shots`: `wan/2.6` |
| `generation_type` | `generationType`, `character_orientation` | `generationType`: `google/veo3`, `google/veo3_fast`; `character_orientation`: `kling/v2.6-motion-control`, `kling/v3-motion-control` |
| `output_format` | `output_format` | `output_format`: `google/gemini-3.1-flash-image-preview`, `qwen/image`, `qwen/image-2`, `qwen/image-2.1`, `seedream/5-pro-text-to-image` |
| `background` | `background` | `background`: `qwen/image-2.1` |
| `prompt_enhance` | `isEnhance`, `enhance_prompt`, `enable_prompt_expansion` | `isEnhance`: `openai/gpt-5-image`; `enhance_prompt`: `qwen/image-2.1`; `enable_prompt_expansion`: `wan/2.5` |
| `prompt_translate` | `enableTranslation` | `enableTranslation`: `google/veo3`, `google/veo3_fast` |
| `watermark` | `watermark` | `watermark`: `google/veo3`, `google/veo3_fast` |
| `upscale_factor` | `upscale_factor` | `upscale_factor`: `topaz/image-upscale`, `topaz/video-upscale` |
| `guidance_scale` | `guidance_scale` | `guidance_scale`: `qwen/image` |
| `strength` | `strength` | `strength`: `qwen/image` |
| `audio_ids` | `audio_ids` | `audio_ids`: `gemini-omni-video` |
| `character_ids` | `character_ids` | `character_ids`: `gemini-omni-video` |

Смысл «разрешения», скрытого за другим именем: Seedream 4.5 `quality` basic = 2K, high = 4K; Seedream 5 Lite — 2K /
3K; Seedream 5 Pro — 1K / 2K (описания параметров каталога); Kling 3.0 `mode` std = 720p (1280×720), pro = 1080p,
4K = 2160p (документация KIE Kling 3.0) [S1][S5]; Motion Control `mode` = 720p/1080p напрямую.

Представление значений (§2.5 файла 01): `bool_string` → `"true"`/`"false"`; `duration` → строка; `number` → число.
`polza.py` приводит сам.

## 2. Формулы цены

Все цены — рубли каталога (`top_provider.pricing` или `providers[].pricing`, поле `currency: "RUB"`). Калькулятор —
`polza_catalog.estimate()` (его вызывают `polza.py estimate/run` и `polza_catalog.py price`); проверен на 75 ручных
и 9 токенных случаях `[проверено: 99-raw/experiments/B/02-price-calculator]`. Фактическое списание —
`usage.cost_rub` (файл 01 §8).

### 2.1 За запрос — `per_request` (11 моделей)

`цена = per_request`. Z-Image 1,40; Grok Image 2,50; Nano Banana 2,90; NB2 Lite 2,90; Seedream 4 3,00; Qwen Image 2
4,00; Seedream 5 Lite 4,00; GPT-5 Image 4,50; Seedream 4.5 5,00; Veo 3.1 Fast 45,00 и Quality 187,50 **за ролик**.
Разрешение и качество на цену не влияют: Seedream 4 в 4K — 3 ₽, Seedream 4.5 `quality: high` (4K) — 5 ₽.

### 2.2 Ступени с условиями — `tiers` без `unitParam` (15 моделей)

```json
// google/gemini-3-pro-image-preview · top_provider.pricing · polza 2026-09-23
{"tiers": [{"conditions": [], "cost_rub": "13.50000000"},
           {"conditions": ["image_resolution=1K"], "cost_rub": "13.50000000"},
           {"conditions": ["image_resolution=2K"], "cost_rub": "13.50000000"},
           {"conditions": ["image_resolution=4K"], "cost_rub": "18.00000000"}], "currency": "RUB"}
```

- `conditions` — строки `ключ=значение`; ключ — параметр `input` или производный признак (§2.6). Спека:
  `ClientTierPresenter` «Условия применения уровня цены» [S3]. Как polza выбирает ступень, не описано; калькулятор
  берёт **ступень, все условия которой выполнены, с наибольшим числом условий**; при равенстве — дороже; если ни
  одна — ступень `[]` `[не проверено: семантика выведена из каталога]`.
- Значения условий — строки: `sound=false`, `duration=8`, `upscale_factor=4`, `resolution=4k` (строчная у Omni),
  `mode=4K` (прописная у Kling) — регистр важен.
- Модели: GPT Image 2.5 Sunburst/Flare, GPT-5.4 Image 2, Nano Banana 2 (preview), Nano Banana Pro, FLUX.2 Pro/Flex,
  Qwen Image 2.1 (по `image_resolution`); GPT Image 1.5, Seedream 5 Pro (по `quality`, у 5 Pro ещё
  `input_images_count`); Qwen Image (по `aspect_ratio`); Topaz Upscale (по `upscale_factor`); Seedance 1.5 Pro
  (`resolution` + `duration` + `sound`), Wan 2.5/2.6 (`resolution` + `duration`), Kling 2.6 (`duration` + `sound`),
  Gemini Omni Video (`resolution` + `duration` + `has_video`) — у последних пяти цена **за ролик**, длительность — одно
  из условий.

### 2.3 Ступень × секунды — `tiers` + `unitParam: "duration"` (10 моделей)

`цена = cost_rub(ступени) × duration`. OpenAPI: «Если задан, cost_rub в tiers — ставка за единицу этого параметра» [S3].

| Модель | Условия ступени | Ставка, ₽/с | Пример |
|---|---|---|---|
| `kling/v3` | `mode` × `sound` | std 10 / 14; pro 12 / 18; 4K 45 / 45 (без / со звуком) | std, без звука, 5 с = 50 |
| `bytedance/seedance-2` | `resolution` × `has_video` | 480p 12,825 / 15,39; 720p 27,675 / 33,75; 1080p 68,85 / 83,70 | 480p, 5 с = 64,125 |
| `bytedance/seedance-2-fast` | `resolution` | 480p 10,4625; 720p 22,275 | 480p, 5 с = 52,3125 |
| `bytedance/seedance-2-mini` | `resolution` × `has_video` | 480p 2,565 / 3,24; 720p 5,535 / 6,75 | 480p, 5 с = 12,825 |
| `bytedance/seedance-2-5` | `resolution` × `has_video` | 480p 18,90 / 22,95; 720p 42,525 / 51,30 | 480p, 5 с = 94,50 |
| `grok-imagine-video-1-5` | `resolution` | 480p 1,62; 720p 3,0375 | 480p, 1 с = 1,62 |
| `kling/v3-motion-control` | `mode` | 720p 14; 1080p 19 | 7 с видео движения, 720p = 98 |
| `kling/v2.6-motion-control` | `mode` | 720p 8,25; 1080p 13,50 | 10 с, 720p = 82,50 |
| `topaz/video-upscale` | `upscale_factor` | ×1/×2 6; ×4 10,50 | 10 с, ×4 = 105 |

У Motion Control и Topaz Video параметра `duration` нет: секунды = **длина входного видео** (`polza.py` берёт её
`ffprobe` у локального файла или из `meta.ref_video_seconds`; Motion Control без длины — оценка по потолку 10 с
при `character_orientation: image` и 30 с при `video`). Округляет ли polza секунды вверх — `[не проверено]`.

### 2.4 Ставка × секунды — `video_per_second` (5 моделей)

`цена = video_per_second × duration`; разрешение и звук на цену **не влияют**.

| Модель | Провайдер | ₽/с | $/с (÷ 117,992) | `duration` (по умолч.) | 5 с |
|---|---|---|---|---|---|
| `minimax/hailuo-3-max` | openrouter | 9,43936 | 0,08 | 5–15 (5) | 47,20 |
| `alibaba/happyhorse-1.1` | Alibaba | 15,0793776 | 0,1278 | 3–15 (3) | 75,40 |
| `alibaba/happyhorse-1.0` | Alibaba | 19,9878448 | 0,1694 | 3–15 (3) | 99,94 |
| `alibaba/wan-3.0` | Alibaba | 23,5984 | 0,20 | 2–30 (2) | 117,99 |
| `alibaba/wan-3.0-prime` | openrouter | 33,03776 | 0,28 | 2–30 (2) | 165,19 |

У KIE Wan 3.0 стоит по разрешениям: 480p $0,04/с, 720p $0,09, 1080p $0,16 (данные агента P) — через polza 480p в 7 раз
дороже KIE, 1080p — в 1,75 раза (B/05) [S7].

### 2.5 Токены (2 модели + провайдеры Google и OpenAI у 5 моделей)

`цена ≈ входные токены × prompt_per_million/1e6 + выходные image-токены × image_output_per_million/1e6 (+ текст и
рассуждение × completion_per_million/1e6)`. Выходные image-токены на картинку — из прайсов вендоров [S9][S10]:

| Модель (вендор) | Токены на картинку | Ставка polza, ₽/1M вых. картинки | ₽ за картинку |
|---|---|---|---|
| `google/gemini-3.1-flash-image` (NB2 GA; google-vertex/global, google-ai-studio) | 0.5K 747 / 1K 1120 / 2K 1680 / 4K 2520 | 7 079,52 ($60) | 5,29 / 7,93 / 11,89 / 17,84 |
| NB2 preview через `google-vertex/global/flex` | те же | 3 539,76 ($30) | 1K 3,96 / 2K 5,95 / 4K 8,92 |
| `google/gemini-3-pro-image-preview` (NB Pro) через Google | 1K–2K 1120 / 4K 2000 | 14 159,04 ($120); flex 7 079,52 | 15,86 / 28,32; flex 7,93 / 14,16 |
| `google/gemini-2.5-flash-image` через Google | 1290 | 3 539,76; flex 1 769,88; priority 6 371,568 | 4,57; flex 2,28; priority 8,22 |
| `google/gemini-3.1-flash-lite-image` через Google | 1K 1120 | 3 539,76 | 3,96 |
| `openai/gpt-5-image-mini` (openai) | 1024²: low 272 / medium 1056 / high 4160 (gpt-image-1) | 943,936 ($8) | 0,26 / 1,00 / 3,93 |
| `openai/gpt-5-image` через `openai` | те же | 4 719,68 ($40) | 1,28 / 4,98 / 19,63 |
| `openai/gpt-5.4-image-2` через `openai` | не опубликовано в доступных источниках | 3 539,76 ($30) | н/д |

Вход: промт ~ 3 символа на токен (грубо, `[практика]`), картинка-референс у NB Pro — 560 токенов (≈ 0,13 ₽ по
235,984 ₽/1M) [S9]. Какой тир качества polza даёт `openai/gpt-5-image(-mini)` (параметра `quality` у провайдера нет) —
`[не проверено]`. У `cloud-ru` (провайдер NB/NB Pro/NB2) нет `image_output_per_million` — только текст; для картинок
не годится. Курс: 117,992 ₽/$ (ставки polza делятся ровно), курс ЦБ 23.09.2026 — 84,0657 [S7][S8].

### 2.6 Производные условия: видео-референс, число картинок, звук

| Условие | Откуда | Модели | Эффект |
|---|---|---|---|
| `has_video=true/false` | непустой `videos` | Seedance 2, 2 Mini, 2.5; Gemini Omni | Seedance 2: ×1,20–1,22; Mini: ×1,22–1,26; 2.5: ×1,21; Omni: ролик 70 ₽ (720p/1080p), 115 ₽ (4k) при любой длительности |
| `input_images_count=N` | длина `images` | Seedream 5 Pro | первая картинка бесплатно, каждая следующая +0,30 ₽ (до 10: basic 7,70, high 12,70) |
| `sound=…` | `sound` (Kling) или **`generate_audio`** (Seedance 1.5 Pro: условие `sound`, параметр `generate_audio`) | Kling 3.0, Kling 2.6, Seedance 1.5 Pro | Kling 3.0 std +40 %, pro +50 %, 4K без разницы; Kling 2.6 ≈ ×2; Seedance 1.5 Pro ×2 |

Звук в каталоге есть и у Seedance 2/2 Fast/2 Mini/2.5 (`generate_audio`, по умолчанию `"true"`), Wan 3.0/Prime
(`"false"`) — на цену не влияет [S1].

### 2.7 Операции (только Veo 3.1)

`extend` 45 ₽, `upscale_1080p` 10 ₽, `upscale_4k` 90 ₽ — `operations[].pricing.per_request` [S1]. Цена `extend` с
`model: "quality"` (по умолчанию у `google/veo3`) — вопрос: у KIE продление Quality в 4 раза дороже Fast (файл 01 §4).

### 2.8 Длительность по референсу

`bytedance/seedance-2-5`: `duration: -1` (`auto_value`) — длительность и цена берутся из референсного видео
(«доступно только вместе с videos, оно же определяет цену»); сумма видео-референсов ≤ 30 с → цена ≤ 30 × ставка [S1].

### 2.9 Запасная ступень `[]` и неуказанные параметры

| `[]` = | Модели и цена `[]` |
|---|---|
| **максимуму** (13) | Seedance 1.5 Pro 135; Seedance 2 83,70 ₽/с; Seedance 2 Fast 22,275 ₽/с; Seedance 2.5 51,30 ₽/с; Seedance 2 Mini 6,75 ₽/с; Grok Video 3,0375 ₽/с; Kling 3.0 45 ₽/с; Kling 3.0 Motion Control 19 ₽/с; Kling 2.6 Motion Control 13,50 ₽/с; GPT Image 2.5 Sunburst и Flare 11; Qwen Image 2.1 6; Qwen Image 3 |
| **минимуму** (13) | GPT-5.4 Image 2 4; Nano Banana 2 4,80; Nano Banana Pro 13,50; FLUX.2 Pro 5 и Flex 14; Seedream 5 Pro 5; GPT Image 1.5 3; Topaz 7,50 и 6 ₽/с; Gemini Omni 35; Kling 2.6 42; Wan 2.5 45 и 2.6 52,50 |

Если ценовой параметр не передан, polza может применить `default` каталога (дешёвый путь) или `[]` (у 13 моделей —
максимум). Проверка — тест T8 в файле 01 §13 (GPT Image 2.5 без `image_resolution`: 4 или 11 ₽). До проверки:
**каждый ценовой параметр — явно**; `polza.py` подставляет default сам и отказывает, если его нет (Seedance 1.5 Pro
`resolution`/`duration`, Kling 3.0 `duration`) `[проверено: B/04]`.

## 3. Картинки: 23 модели

### 3.1 Сводная таблица (снимок 2026-09-23; в скобках — default каталога)

| id | пров. | цена, ₽ | промт ≤ | реф. | соотношения | разрешение / качество | прочее |
|---|---|---|---|---|---|---|---|
| `black-forest-labs/flux.2-flex` | mie | 14,00–24,00 по image_resolution | 5000 | 8 | 1:1/4:3/3:4/16:9/9:16/3:2/2:3 | 1K/2K | — |
| `black-forest-labs/flux.2-pro` | mie | 5,00–7,00 по image_resolution | 5000 | 8 | 1:1/4:3/3:4/16:9/9:16/3:2/2:3 | 1K/2K | — |
| `bytedance/seedream-4` | mie | 3,00/запрос | 5000 | 10 | 1:1/4:3/3:4/3:2/2:3/16:9/9:16/21:9 | 1K/2K/4K | `seed` |
| `bytedance/seedream-4.5` | mie | 5,00/запрос | 3000 | 14 | 1:1/4:3/3:4/3:2/2:3/16:9/9:16/21:9 (1:1) | basic/high (basic) = basic 2K, high 4K | — |
| `bytedance/seedream-5-lite` | mie | 4,00/запрос | 2996 | 10 | 1:1/4:3/3:4/16:9/9:16/2:3/3:2/21:9 (1:1) | basic/high (basic) = basic 2K, high 3K | — |
| `google/gemini-2.5-flash-image` | mie | 2,90/запрос | 20000 | 8 | 1:1/9:16/16:9/3:4/4:3/3:2/2:3/5:4/4:5/21:9 | — | — |
| `google/gemini-3-pro-image-preview` | mie | 13,50–18,00 по image_resolution | 20000 | 8 | 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9/auto | 1K/2K/4K | — |
| `google/gemini-3.1-flash-image` | google-vertex/global | токены: вых. картинка 7 079,52/1M | — | — | — | — | — |
| `google/gemini-3.1-flash-image-preview` | mie | 4,80–10,80 по image_resolution | 20000 | 14 | 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9/auto | 1K/2K/4K | `output_format` |
| `google/gemini-3.1-flash-lite-image` | mie | 2,90/запрос | 20000 | 10 | 1:1/1:4/4:1/1:8/8:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9/… | — | — |
| `gpt-image-2-5-flare` | mie | 4,00–11,00 по image_resolution | 20000 | 16 | auto/1:1/9:16/16:9/4:3/3:4/3:2/2:3/21:9/27:16/16:27/9:8/8:9 (auto) | 1K/2K/4K (1K) | — |
| `openai/gpt-5-image` | mie | 4,50/запрос | 4000 | 5 | 1:1/3:2/2:3 (1:1) | — | `mask_url`, `isEnhance` |
| `openai/gpt-5-image-mini` | openai | токены: вых. картинка 943,936/1M | 32000 | 10 | — | — | — |
| `openai/gpt-5.4-image-2` | mie | 4,00–11,00 по image_resolution | 20000 | 16 | auto/1:1/9:16/16:9/4:3/3:4 (auto) | 1K/2K/4K (1K) | — |
| `openai/gpt-image-1.5` | mie | 3,00–16,50 по quality | — | 16 | 1:1/2:3/3:2 | medium/high (medium) | — |
| `openai/gpt-image-2.5-sunburst` | mie | 4,00–11,00 по image_resolution | 20000 | 16 | auto/1:1/3:2/2:3/4:3/3:4/16:9/9:16/21:9/27:16/16:27/9:8/8:9 (auto) | 1K/2K/4K (1K) | — |
| `qwen/image` | mie | 2,25–3,00 по aspect_ratio | — | 1 | 1:1/3:4/4:3/9:16/16:9 | — | `output_format`, `strength`, `guidance_scale` |
| `qwen/image-2` | mie | 4,00/запрос | 5000 | 3 | 1:1/3:4/4:3/9:16/16:9 | — | `output_format` |
| `qwen/image-2.1` | mie | 3,00–6,00 по image_resolution | 5000 | 10 | 1:1/4:3/3:4/3:2/2:3/16:9/9:16 | 1K/2K (1K) | `output_format`, `seed`, `mask_url`, `background`, `enhance_prompt` |
| `seedream/5-pro-text-to-image` | mie | 5,00–12,70 по quality, images | — | 10 | 1:1/4:3/3:4/16:9/9:16/2:3/3:2 (1:1) | basic/high (basic) = basic 1K, high 2K | `output_format` |
| `tongyi-mai/z-image` | mie | 1,40/запрос | 1000 | 0 | 1:1/4:3/3:4/16:9/9:16 (1:1) | — | — |
| `topaz/image-upscale` | mie | 7,50–30,00 по upscale_factor | — | 1 | — | — | `upscale_factor` |
| `x-ai/grok-imagine-image` | mie | 2,50/запрос | 5000 | 1 | 1:1/2:3/3:2 | — | — |

Провайдер у 21 модели — `mie` (≈ KIE); у `google/gemini-3.1-flash-image` — `google-vertex/global`, у
`openai/gpt-5-image-mini` — `openai` (токены). Цены за 1K/2K/4K — §6.1; разные провайдеры одной модели — §5.

### 3.2 Как вызвать и где ломается (по каталогу, описаниям параметров и гайдам)

- **`qwen/image-2.1`** (21.09.2026, гайда нет): единственная модель с прозрачностью — `background: "transparent"`
  только с `output_format` `png`/`webp` («Альфа-канал есть у png и webp»); `mask_url` — «белое — менять, чёрное —
  оставить», только с одним референсом и не с прозрачностью; без `aspect_ratio` — 1:1 при генерации и «пропорции
  первого референса при редактировании»; `images` ≤ 10, «порядок — тот, на который ссылается промпт»;
  `enhance_prompt` (boolean, `false`) «добавляет 10–30 секунд»; промт на любом языке ≤ 5000. У KIE есть 21:9 и 9:21,
  `enhance_prompt` по умолчанию `true`; скорость 1K ≈ 7–12 с, 2K ≈ 30–55 с (данные агента P) [S1][S11].
- **`openai/gpt-image-2.5-sunburst`, `gpt-image-2-5-flare`** (10.09, гайдов нет): у Flare id **без префикса
  `openai/`**; `aspect_ratio` по умолчанию `auto` → только 1K; «для 1:1 недоступен 4K»; 27:16, 16:27, 9:8, 8:9 у KIE —
  только 1K; `images` ≤ 16 (правка); **нет `background`, `quality`, `n`, маски** — у KIE `background` есть [S1][S11].
- **`seedream/5-pro-text-to-image`** (14.07): id — слаг KIE; `aspect_ratio` и `quality` обязательны (`basic` = 1K,
  `high` = 2K); `images` ≤ 10, первый бесплатно, далее +0,30 ₽; `output_format` png/jpeg; `max_length` промта нет [S1].
- **`google/gemini-3.1-flash-lite-image`** (Nano Banana 2 Lite, 30.06): крайние соотношения 1:4, 4:1, 1:8, 8:1 и
  `auto`; размер не задаётся (у Google — только 1K); `images` ≤ 10; 2,90 ₽ у `mie`, 3,96 у Google [S1][S2].
- **`google/gemini-3.1-flash-image`** (Nano Banana 2 GA, 24.06): **`parameters` нет** ни у одного провайдера, цена в
  токенах — через `/v1/media` не вызывать до проверки; для NB2 — preview-версия ниже [S1][S2].
- **`openai/gpt-5.4-image-2`** (22.04): у `mie` — `auto` + 5 соотношений, 1K/2K/4K, `images` ≤ 16; у `openai` —
  10 соотношений (с 21:9, 4:5, 5:4), 1K/2K, `images` ≤ 10, токены. Гайд: «`openai` по умолчанию», «@-синтаксис
  `@mie`», `"n": 1` (1–4) и массив строк-URL — **`n` в каталоге нет** (валидатор отклонит) [S1][S4].
- **`qwen/image-2`** (17.03, гайда нет): 5 соотношений без default, `output_format` png/jpeg, `images` ≤ 3, 4 ₽.
- **`bytedance/seedream-5-lite`** (27.02): `aspect_ratio` и `quality` обязательны (`basic` = 2K, `high` = 3K), промт
  ≤ 2996, `images` ≤ 10 (гайд: до 10 МБ, jpeg/png/webp); 4 ₽ за любой `quality` [S1][S4].
- **`google/gemini-3.1-flash-image-preview`** (Nano Banana 2): `image_resolution` без default (запасная ступень = 1K,
  4,80); `images` ≤ 14 у `mie` (гайд — «до 8», отдельный путь `/v1/media/nanobanano-2` с `images` ≤ 8 в спеке; у Google —
  10); `output_format` png/jpeg есть только у `mie`; гайд — результат «в поле `output.url`» [S1][S3][S4].
- **`topaz/image-upscale`**: `images` ровно 1 и `upscale_factor` обязательны; значения строками `"1"`/`"2"`/`"4"`/`"8"`
  (default `"2"`); `prompt` в каталоге нет, гайд шлёт `"prompt": ""` (`polza.py` добавляет сам); у KIE — 1/2/4 (2K/4K) [S1][S4][S11].
- **`qwen/image`** (Qwen Image): цена по соотношению (16:9 и 9:16 — 2,25; 3:4 и 4:3 — 2,50; 1:1 — 3); `strength` 0–1
  (0,8; только image-to-image) и `guidance_scale` 0–20 (2,5) — числа (гайд пишет строками `"0.8"`); `images` ≤ 1 [S1][S4].
- **`tongyi-mai/z-image`**: `aspect_ratio` обязателен (5 значений), промт ≤ 1000, **референсов нет** (`images` max 0);
  1,40 ₽ — самая дешёвая картинка [S1].
- **`x-ai/grok-imagine-image`**: только 1:1, 2:3, 3:2 (нет 16:9); `images` ≤ 1; у KIE «4 кредита за 2 картинки» —
  может вернуть 2 файла `[не проверено]` (клиент скачивает все URL) [S1][S11].
- **`black-forest-labs/flux.2-pro`** / **`flux.2-flex`**: 7 соотношений без default («при i2i без указания
  сохраняются пропорции исходника» — гайд), `image_resolution` 1K/2K без default, `images` ≤ 8; **нет `seed`,
  `steps`, `guidance`, `output_format`, негатива** (нет и у KIE); Flex в 2,8–3,4 раза дороже Pro; JSON-промты — по
  гайду BFL (агент D) [S1][S4][S11].
- **`bytedance/seedream-4.5`**: `aspect_ratio` и `quality` обязательны (`basic` = 2K, `high` = 4K — одна цена 5 ₽),
  промт ≤ 3000, `images` ≤ 14 [S1][S4].
- **`bytedance/seedream-4`**: `image_resolution` 1K/2K/4K по одной цене 3 ₽ (бери 4K), `seed` 1–4 294 967 295,
  `images` ≤ 10; последний cURL гайда — неверный id `bytedance/seedream-v4` [S1][S4].
- **`openai/gpt-image-1.5`**: `aspect_ratio` (только 1:1, 2:3, 3:2) и `quality` обязательны; `high` в 5,5 раза дороже
  `medium` (16,50 против 3); `images` ≤ 16 URL [S1][S4].
- **`openai/gpt-5-image-mini`**: только провайдер `openai`, токены (≈ 1 ₽ при medium 1024²); промт ≤ 32 000
  (необязателен), `images` ≤ 10; соотношения и размер не задаются [S1][S2][S4].
- **`openai/gpt-5-image`**: у `mie` — `mask_url` («чёрные области = менять, белые = оставить» — наоборот к Qwen 2.1),
  `isEnhance` (`"false"`, «улучшение промпта для 3D рендеринга»), 1:1/3:2/2:3, `images` ≤ 5, промт ≤ 4000 и обязателен
  без `images`; у KIE этот набор — «4o Image API» (GPT-4o image) `[спорно]`; у `openai` — без маски, 10 соотношений [S1][S2][S11].
- **`google/gemini-3-pro-image-preview`** (Nano Banana Pro): `image_resolution` без default (запасная = 13,50 = 1K);
  **2K по цене 1K**; `images` ≤ 8 у `mie` (у `bananalab` и Google API — 14, у провайдеров Google в polza — 10); гайд
  перечисляет `output_format` png/jpeg — **в каталоге его нет** [S1][S2][S4].
- **`google/gemini-2.5-flash-image`** (Nano Banana): 10 соотношений без `auto`, размер не задаётся, `images` ≤ 8;
  гайд перечисляет `output_format` — в каталоге нет; через `google-*/flex` дешевле (2,28 ₽) [S1][S2][S4].

Минимальные тела запросов всех 23 моделей, проверенные валидатором, — §11.

## 4. Видео: 21 модель

### 4.1 Сводная таблица (снимок 2026-09-23; в скобках — default каталога)

| id | пров. | цена | длительность, с | разрешение / режим | карт. / видео | звук | соотношения | прочее |
|---|---|---|---|---|---|---|---|---|
| `alibaba/happyhorse-1.0` | Alibaba | 19,9878 ₽/с | 3–15 (3) | 720p/1080p (720p) | 1 / 0 | — | 16:9/9:16/1:1/4:3/3:4/21:9/9:21 (16:9) | `seed` |
| `alibaba/happyhorse-1.1` | Alibaba | 15,0794 ₽/с | 3–15 (3) | 720p/1080p (720p) | 1 / 0 | — | 16:9/9:16/1:1/4:3/3:4/21:9/9:21 (16:9) | `seed` |
| `alibaba/wan-3.0` | Alibaba | 23,5984 ₽/с | 2–30 (2) | 480p/720p/1080p (480p) | 1 / 0 | `generate_audio` true/false (false) | 16:9/4:3/1:1/3:4/9:16 (16:9) | `seed` |
| `alibaba/wan-3.0-prime` | openrouter | 33,0378 ₽/с | 2–30 (2) | 480p/720p/1080p (480p) | 1 / 0 | `generate_audio` true/false (false) | 16:9/4:3/1:1/3:4/9:16 (16:9) | `seed` |
| `bytedance/seedance-1.5-pro` | mie | 5,25–135,00 ₽ по resolution, duration, generate_audio | 4/8/12 | 480p/720p/1080p | 2 / 0 | `generate_audio` true/false (false) | 1:1/21:9/4:3/3:4/16:9/9:16 | `fixed_lens` |
| `bytedance/seedance-2` | mie | 12,825–83,70 ₽/с по resolution, videos | 4–15 (15) | 480p/720p/1080p (720p) | 5 / 1 | `generate_audio` true/false (true) | 16:9/4:3/1:1/3:4/9:16/21:9 (16:9) | — |
| `bytedance/seedance-2-5` | mie | 18,90–51,30 ₽/с по resolution, videos | 4–30 (5) | 480p/720p (720p) | 30 / 10 | `generate_audio` true/false (true) | 16:9/4:3/1:1/3:4/9:16/21:9/auto (auto) | — |
| `bytedance/seedance-2-fast` | mie | 10,4625–22,275 ₽/с по resolution | 4–15 (15) | 480p/720p (720p) | 5 / 1 | `generate_audio` true/false (true) | 16:9/4:3/1:1/3:4/9:16/21:9 (16:9) | — |
| `bytedance/seedance-2-mini` | mie | 2,565–6,75 ₽/с по resolution, videos | 4–15 (15) | 480p/720p (720p) | 9 / 3 | `generate_audio` true/false (true) | 16:9/4:3/1:1/3:4/9:16/21:9/auto (16:9) | — |
| `gemini-omni-video` | mie | 35,00–115,00 ₽ по duration, videos, resolution | 4/6/8/10 (4) | 720p/1080p/4k (720p) | 7 / 1 | — | 16:9/9:16 (16:9) | `seed`, `audio_ids`, `character_ids` |
| `google/veo3` | mie | 187,50 ₽/запрос | — | — | 2 / 0 | — | 16:9/9:16/Auto (16:9) | `seeds`, `watermark`, `generationType`, `enableTranslation` |
| `google/veo3_fast` | mie | 45,00 ₽/запрос | — | — | 3 / 0 | — | 16:9/9:16/Auto (16:9) | `seeds`, `watermark`, `generationType`, `enableTranslation` |
| `grok-imagine-video-1-5` | mie | 1,62–3,0375 ₽/с по resolution | 1–15 (8) | 480p/720p (480p) | 7 / 0 | — | 1:1/16:9/9:16/3:2/2:3/auto (auto) | — |
| `kling/v2.6` | mie | 42,00–165,00 ₽ по duration, sound | 5/10 (5) | — | 1 / 0 | `sound` true/false (false) | 1:1/16:9/9:16 | — |
| `kling/v2.6-motion-control` | mie | 8,25–13,50 ₽/с по mode | — | 720p/1080p (720p) | 1 / 1 | — | — | `character_orientation` |
| `kling/v3` | mie | 10,00–45,00 ₽/с по mode, sound | 3–15 | std/pro/4K (std) = std 720p, pro 1080p, 4K 2160p | 2 / 0 | `sound` true/false (false) | 16:9/9:16/1:1 (1:1) | — |
| `kling/v3-motion-control` | mie | 14,00–19,00 ₽/с по mode | — | 720p/1080p (720p) | 1 / 1 | — | — | `character_orientation` |
| `minimax/hailuo-3-max` | openrouter | 9,4394 ₽/с | 5–15 (5) | 768p/480p (768p) | 2 / 0 | — | 21:9/16:9/4:3/1:1/3:4/9:16 (21:9) | — |
| `topaz/video-upscale` | mie | 6,00–10,50 ₽/с по upscale_factor | — | — | 0 / 1 | — | — | `upscale_factor` |
| `wan/2.5` | mie | 45,00–150,00 ₽ по resolution, duration | 5/10 | 720p/1080p | 1 / 0 | — | 16:9/9:16/1:1 | `seed`, `negative_prompt`, `enable_prompt_expansion` |
| `wan/2.6` | mie | 52,50–236,25 ₽ по resolution, duration | 5/10/15 | 720p/1080p | 1 / 0 | — | — | `multi_shots` |

Провайдер: `mie` — 16 моделей; `Alibaba` — Wan 3.0, HappyHorse 1.0/1.1; `openrouter` — Wan 3.0 Prime, MiniMax H3 Max
(у обеих `providers[]` пуст). Запасных провайдеров у видео нет [S2].

### 4.2 Как вызвать и где ломается

- **`google/veo3_fast`** (Veo 3.1 Fast, 45 ₽) и **`google/veo3`** (Quality, 187,50 ₽): **ни длительности, ни
  разрешения, ни звука в параметрах** — по KIE ролик 8 с, 720p, «все видео со звуком по умолчанию» [S11];
  `generationType` задавай явно: `TEXT_2_VIDEO` (0 картинок), `FIRST_AND_LAST_FRAMES_2_VIDEO` (1–2: одна — «видео
  разворачивается вокруг картинки», две — первый и последний кадр), `REFERENCE_2_VIDEO` (1–3, только Fast; у KIE —
  только 8 с и 16:9); `seeds` (не `seed`) 10000–99999; `watermark` ≤ 50; `aspect_ratio` 16:9/9:16/`Auto` (Auto —
  центр-кроп по картинке, KIE); `enableTranslation` по умолчанию `"true"` — промт переводится на английский, при
  `"false"` KIE отвечает «Only English prompts are supported»; промт ≤ 60 000 по каталогу (гайд — 2000); операции
  `extend`/`upscale_1080p`/`upscale_4k` (файл 01 §4); в cURL гайда id без префикса (`veo3_fast`) [S1][S4][S11].
- **`kling/v3`** (Kling 3.0): `duration` (3–15), `mode` (`std`/`pro`/`4K`), `sound` — **обязательны**; `aspect_ratio`
  по умолчанию **1:1** (у KIE 16:9) и «игнорируется при наличии start frame»; `images` 0–2 — стартовый и конечный
  кадр; «`sound` обязательно true при `multi_shots`», но `multi_shots`, `multi_prompt`, `kling_elements` polza не
  выставляет — мульти-шот недоступен; нет `negative_prompt`, `cfg_scale`, `seed` [S1][S4][S11].
- **`kling/v2.6`**: `aspect_ratio` (1:1/16:9/9:16) **обязателен без default** и игнорируется при картинке; `duration`
  `"5"`/`"10"`; `sound` обязателен (≈ ×2 к цене); `images` ≤ 1; гайда нет (есть гайд на снятый Kling 2.5 Turbo) [S1].
- **`kling/v3-motion-control`**, **`kling/v2.6-motion-control`**: `images` ровно 1 (персонаж) и `videos` ровно 1
  (движение); `mode` 720p/1080p; `character_orientation`: `image` (видео ≤ 10 с) или `video` (≤ 30 с) — у 2.6 оба
  обязательны; цена — за секунду **видео движения**; гайды показывают массивы строк-URL [S1][S4].
- **`bytedance/seedance-1.5-pro`**: `resolution` и `duration` (`"4"`/`"8"`/`"12"`) **без default** — пропуск = запасная
  ступень 135 ₽; `fixed_lens: "true"` — «статичная камера без движения» (единственный такой параметр в polza);
  `generate_audio` (`"false"`) удваивает цену, в ступенях называется `sound`; `images` 0–2; промт 3–2500 [S1][S4].
- **`bytedance/seedance-2`** / **`-2-fast`** / **`-2-mini`**: `duration` по умолчанию **15** и `generate_audio`
  **`"true"`** — задавай оба; Seedance 2 — 480p/720p/1080p («1080p — по документации KIE»), Fast и Mini — до 720p;
  `images` ≤ 5 (Mini ≤ 9), `videos` ≤ 1 (Mini ≤ 3, сумма ≤ 15 с); описание промта «до 1536 символов» при `max_length`
  20 000; `auto` у Mini «передаётся в KIE как adaptive». У KIE сценарии «первый/последний кадр» и «референсы»
  **взаимоисключающие** и задаются разными полями (`first_frame_url`/`last_frame_url` против
  `reference_image_urls`), у polza — один массив `images`: что он означает — неизвестно, для петли «первый = последний
  кадр» не полагаться без теста [S1][S11]. Гайд шлёт `multi_shots`, которого нет в каталоге [S4].
- **`bytedance/seedance-2-5`**: до 30 с (default 5), 480p/720p («1080p у Seedance 2.5 нет»), `images` ≤ 30, `videos`
  ≤ 10 (сумма ≤ 30 с), `duration: -1` — по длине референса (только с `videos`); `aspect_ratio` по умолчанию `auto`;
  звук `"true"` по умолчанию; промт ≤ 30 000 [S1].
- **`grok-imagine-video-1-5`** (id без префикса): 1–15 с (default **8**), 480p/720p, `images` ≤ 7, звука и seed нет;
  самый дешёвый перебор — 1,62 ₽/с при 480p [S1].
- **`gemini-omni-video`** (id без префикса): `duration` обязателен `"4"`/`"6"`/`"8"`/`"10"`; `resolution`
  `720p`/`1080p`/`4k` (строчная; OpenAPI принимает и `2160p`); квота `images + 2×videos + character_ids ≤ 7`; `videos`
  ≤ 1 («будет передано в KIE как `video_list`»; OpenAPI ещё знает `video_list[{url, start, ends}]`, `video_start`,
  `video_end` — в каталоге их нет); `audio_ids`/`character_ids` — из моделей `gemini-omni-audio`/`gemini-omni-character`
  (в медиа-каталоге их нет); `seed` 0–2 147 483 647; гайд: async «обязателен», совет — тест на 720p и 4 с [S1][S3][S4].
- **`wan/2.5`**: промт ≤ **800**; **единственный `negative_prompt`** в polza (≤ 500); `seed` −1…2 147 483 647;
  `enable_prompt_expansion` (`"false"`); 720p/1080p и `"5"`/`"10"` без default [S1][S4].
- **`wan/2.6`**: **нет `aspect_ratio`**; `multi_shots` (`"false"`) — «мульти-шотовая композиция с переходами»;
  `resolution`/`duration` (`"5"`/`"10"`/`"15"`) без default; цена за ролик (1080p 15 с — 236,25 ₽) [S1][S4].
- **`alibaba/wan-3.0`**, **`alibaba/wan-3.0-prime`**: 2–30 с (default **2**), 480p/720p/1080p по одной цене,
  `images` ≤ 1 (описание «first/last frame», но максимум 1 — только первый кадр), `seed`, `generate_audio`
  (`"false"`, на цену не влияет); гайдов нет [S1].
- **`alibaba/happyhorse-1.0`**, **`-1.1`**: 3–15 с (default **3**), 720p/1080p по одной цене, 7 соотношений с 21:9 и
  9:21, `images` ≤ 1, `seed`; 1.1 дешевле 1.0 (15,08 против 19,99 ₽/с); гайдов нет [S1].
- **`minimax/hailuo-3-max`** (H3 Max): `aspect_ratio` по умолчанию **21:9**; 768p/480p по одной цене; 5–15 с;
  `images` ≤ 2 («опорные кадры first/last frame»); у KIE есть ещё 2K (данные P); гайда нет [S1][S11].
- **`topaz/video-upscale`**: `videos` ровно 1, `upscale_factor` `"1"`/`"2"`/`"4"` (default `"2"`), цена — за секунду
  входного видео; `prompt` нет в каталоге (клиент шлёт `""`) [S1].

### 4.3 Матрица возможностей видео (по параметрам каталога; качество — у агента C2)

| Модель | t2v | 1-й кадр | 1-й + последний | реф. карт. | видео на вход | неподв. камера | звук | негатив | зерно | мульти-шот | макс. с | макс. разрешение |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `google/veo3_fast` | да | да (1 карт.) | да (2 карт.) | 1–3 (`REFERENCE_2_VIDEO`) | нет | промтом | всегда (KIE) | нет | `seeds` | нет; `extend` | 8 (KIE) | 720p (+ апскейл 1080p/4K) |
| `google/veo3` | да | да | да | нет | нет | промтом | всегда (KIE) | нет | `seeds` | нет; `extend` | 8 (KIE) | 720p (+ апскейл) |
| `kling/v3` | да | да | да (`images` 2) | нет | нет | промтом | `sound` | нет | нет | не выставлен | 15 | 4K (2160p) |
| `kling/v2.6` | да | да | нет | нет | нет | промтом | `sound` | нет | нет | нет | 10 | — (не задаётся) |
| `bytedance/seedance-1.5-pro` | да | да | вероятно (`images` 2) `[не проверено]` | нет | нет | **`fixed_lens`** | `generate_audio` | нет | нет | нет | 12 | 1080p |
| `bytedance/seedance-2` | да | ? | ? (`images` ≤ 5: кадры или референсы) | ? | 1 | промтом | вкл. по умолч. | нет | нет | нет | 15 | 1080p |
| `bytedance/seedance-2-fast` | да | ? | ? | ? (≤ 5) | 1 | промтом | вкл. по умолч. | нет | нет | нет | 15 | 720p |
| `bytedance/seedance-2-mini` | да | ? | ? | ? (≤ 9) | до 3 | промтом | вкл. по умолч. | нет | нет | нет | 15 | 720p |
| `bytedance/seedance-2-5` | да | ? | ? | до 30 | до 10 | промтом | вкл. по умолч. | нет | нет | нет | 30 | 720p |
| `wan/2.5` | да | да | нет | нет | нет | промтом | нет | **да** | `seed` | нет | 10 | 1080p |
| `wan/2.6` | да | да | нет | нет | нет | промтом | нет | нет | нет | `multi_shots` | 15 | 1080p |
| `alibaba/wan-3.0`, `-prime` | да | да | нет (≤ 1) | нет | нет | промтом | `generate_audio` | нет | `seed` | нет | 30 | 1080p |
| `alibaba/happyhorse-1.0`, `-1.1` | да | да | нет (≤ 1) | нет | нет | промтом | нет | нет | `seed` | нет | 15 | 1080p |
| `minimax/hailuo-3-max` | да | да | да (≤ 2) | нет | нет | промтом | нет | нет | нет | нет | 15 | 768p |
| `grok-imagine-video-1-5` | да | да | ? (≤ 7) | ? | нет | промтом | нет | нет | нет | нет | 15 | 720p |
| `gemini-omni-video` | да | ? | ? | до 7 | 1 (v2v) | промтом | нет | нет | `seed` | нет | 10 | 4k |
| `kling/v3-motion-control`, `v2.6-…` | нет | персонаж | — | — | видео движения | — | нет | нет | нет | нет | 10 / 30 | 1080p |
| `topaz/video-upscale` | нет | — | — | — | 1 (апскейл) | — | — | — | — | — | длина входа | ×4 |

«?» — каталог не говорит, как модель трактует картинки; «промтом» — отдельного параметра нет. Для петли hero
(`VID-HERO-LOOP`: первый = последний кадр) документированы Veo (`FIRST_AND_LAST_FRAMES_2_VIDEO`), Kling 3.0 (два
кадра) и MiniMax H3 Max; Seedance 1.5 Pro — вероятно; проверка — фаза 5 (агенты C2, I).

## 5. Одна модель — разные провайдеры (снимок 2026-09-23 09:21)

Цена за 1 картинку, промт 300 символов, без референсов; токенные — оценка по таблицам вендоров (§2.5).
Провайдер выбирается объектом `provider` в теле (`only` + `allow_fallbacks: false`) — работает ли для Media API,
`[не проверено]` (тест T5, файл 01 §13).

| модель | провайдер | вид цены | 1K | 2K | 4K | отличия параметров от top |
|---|---|---|---|---|---|---|
| `gemini-2.5-flash-image` | `mie` (top) | per_request | 2,90 | — | — | — |
| `gemini-2.5-flash-image` | `bananalab` | tiers | 3,00 | — | — | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤14 |
| `gemini-2.5-flash-image` | `cloud-ru` | tokens | н/д | — | — | нет `aspect_ratio`; нет `images`; нет `prompt` |
| `gemini-2.5-flash-image` | `google-ai-studio` | tokens | 4,5698 | — | — | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; `prompt` ≤16000 |
| `gemini-2.5-flash-image` | `google-ai-studio/flex` | tokens | 2,2849 | — | — | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; `prompt` ≤16000 |
| `gemini-2.5-flash-image` | `google-ai-studio/priority` | tokens | 8,2257 | — | — | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; `prompt` ≤16000 |
| `gemini-2.5-flash-image` | `google-vertex/global` | tokens | 4,5698 | — | — | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; `prompt` ≤16000 |
| `gemini-2.5-flash-image` | `google-vertex/global/flex` | tokens | 2,2849 | — | — | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; `prompt` ≤16000 |
| `gemini-3-pro-image-preview` | `mie` (top) | tiers | 13,50 | 13,50 | 18,00 | — |
| `gemini-3-pro-image-preview` | `bananalab` | tiers | 13,50 | 13,50 | 18,00 | `images` ≤14 |
| `gemini-3-pro-image-preview` | `cloud-ru` | tokens | н/д | н/д | н/д | нет `aspect_ratio`; нет `image_resolution`; нет `images`; нет `prompt` |
| `gemini-3-pro-image-preview` | `google-ai-studio/global` | tokens | 15,8817 | 15,8817 | 28,3417 | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; `prompt` ≤16000 |
| `gemini-3-pro-image-preview` | `google-ai-studio/global/flex` | tokens | 7,9409 | 7,9409 | 14,1708 | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; `prompt` ≤16000 |
| `gemini-3-pro-image-preview` | `google-vertex/global` | tokens | 15,8817 | 15,8817 | 28,3417 | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; `prompt` ≤16000 |
| `gemini-3-pro-image-preview` | `google-vertex/global/flex` | tokens | 7,9409 | 7,9409 | 14,1708 | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; `prompt` ≤16000 |
| `gemini-3.1-flash-image` | `google-vertex/global` (top) | tokens | 7,935 | 11,8995 | 17,8463 | — |
| `gemini-3.1-flash-image` | `google-ai-studio` | tokens | 7,935 | 11,8995 | 17,8463 | — |
| `gemini-3.1-flash-image-preview` | `mie` (top) | tiers | 4,80 | 7,20 | 10,80 | — |
| `gemini-3.1-flash-image-preview` | `bananalab` | tiers | 4,80 | 7,20 | 10,80 | нет `output_format` |
| `gemini-3.1-flash-image-preview` | `cloud-ru` | tokens | н/д | н/д | н/д | нет `aspect_ratio`; нет `image_resolution`; нет `images`; нет `output_format`; нет `prompt` |
| `gemini-3.1-flash-image-preview` | `google-ai-studio` | tokens | 7,935 | 11,8995 | 17,8463 | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; нет `output_format`; `prompt` ≤16000 |
| `gemini-3.1-flash-image-preview` | `google-vertex/global` | tokens | 7,935 | 11,8995 | 17,8463 | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; нет `output_format`; `prompt` ≤16000 |
| `gemini-3.1-flash-image-preview` | `google-vertex/global/flex` | tokens | 3,9675 | 5,9497 | 8,9231 | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; нет `output_format`; `prompt` ≤16000 |
| `gemini-3.1-flash-lite-image` | `mie` (top) | per_request | 2,90 | — | — | — |
| `gemini-3.1-flash-lite-image` | `google-ai-studio` | tokens | 3,9675 | — | — | +`image_resolution`; `prompt` ≤16000 |
| `gemini-3.1-flash-lite-image` | `google-vertex/global` | tokens | 3,9675 | — | — | +`image_resolution`; `prompt` ≤16000 |
| `gpt-5-image` | `mie` (top) | per_request | 4,50 | — | — | — |
| `gpt-5-image` | `openai` | tokens | 5,102 | — | — | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `images` ≤10; нет `isEnhance`; нет `mask_url`; `prompt` ≤32000 |
| `gpt-5.4-image-2` | `mie` (top) | tiers | 4,00 | 7,00 | 11,00 | — |
| `gpt-5.4-image-2` | `openai` | tokens | н/д | н/д | — | `aspect_ratio`: 1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9; `image_resolution`: 1K/2K; `images` ≤10; `prompt` ≤32000 |

Выводы: (1) **Nano Banana Pro через `google-vertex/global/flex` или `google-ai-studio/global/flex` — 7,94 ₽ за 1–2K
против 13,50 у `mie` (−41 %), 4K — 14,17 против 18 (−21 %)**; (2) NB2 preview через `google-vertex/global/flex` —
3,97/5,95/8,92 против 4,80/7,20/10,80 (−17 %); (3) Nano Banana через `…/flex` — 2,28 против 2,90; (4) обычные
(не flex) Google-провайдеры дороже `mie`; (5) у Google-провайдеров меньше референсов (10), промт ≤ 16 000, нет
`output_format` и `auto`; (6) `cloud-ru` цены за картинку не имеет — не провайдер генерации; (7) GPT-5 Image через
`openai` при medium ≈ 5,10 ₽ дороже `mie` (4,50) и без маски. Что такое flex у Google (приоритет, задержка) и
держит ли polza его для медиа — вопрос для фазы 5 и агента P.

## 6. Примеры расчёта

### 6.1 Картинка 1K / 2K / 4K

| модель | 1K | 2K | 4K | как задаётся |
|---|---|---|---|---|
| `black-forest-labs/flux.2-flex` | 14,00 | 24,00 | — | `image_resolution` |
| `black-forest-labs/flux.2-pro` | 5,00 | 7,00 | — | `image_resolution` |
| `bytedance/seedream-4` | 3,00 | 3,00 | 3,00 | `image_resolution` 1K/2K/4K — одна цена |
| `bytedance/seedream-4.5` | — | 5,00 | 5,00 | `quality` basic=2K/high=4K |
| `bytedance/seedream-5-lite` | — | 4,00 | — | `quality` basic=2K/high=3K |
| `google/gemini-2.5-flash-image` | 2,90 | — | — | не задаётся (размер выбирает модель) |
| `google/gemini-3-pro-image-preview` | 13,50 | 13,50 | 18,00 | `image_resolution` |
| `google/gemini-3.1-flash-image` | 7,9291 | 11,8936 | 17,8404 | токены (оценка) |
| `google/gemini-3.1-flash-image-preview` | 4,80 | 7,20 | 10,80 | `image_resolution` |
| `google/gemini-3.1-flash-lite-image` | 2,90 | — | — | не задаётся (размер выбирает модель) |
| `gpt-image-2-5-flare` | 4,00 | 7,00 | 11,00 | `image_resolution` |
| `openai/gpt-5-image` | 4,50 | — | — | не задаётся (размер выбирает модель) |
| `openai/gpt-5-image-mini` | 0,9968 | — | — | токены (провайдер openai): 1024² low 0,2568 / medium 0,9968 / high 3,9268 — оценка по таблице gpt-image-1 |
| `openai/gpt-5.4-image-2` | 4,00 | 7,00 | 11,00 | `image_resolution` |
| `openai/gpt-image-1.5` | — | — | — | `quality` medium 3 / high 16,50; размер не задаётся |
| `openai/gpt-image-2.5-sunburst` | 4,00 | 7,00 | 11,00 | `image_resolution` |
| `qwen/image` | — | — | — | `aspect_ratio`: 1:1 3 / 3:4, 4:3 2,50 / 16:9, 9:16 2,25 |
| `qwen/image-2` | 4,00 | — | — | не задаётся (размер выбирает модель) |
| `qwen/image-2.1` | 3,00 | 6,00 | — | `image_resolution` |
| `seedream/5-pro-text-to-image` | 5,00 | 10,00 | — | `quality` basic=1K/high=2K |
| `tongyi-mai/z-image` | 1,40 | — | — | не задаётся (размер выбирает модель) |
| `topaz/image-upscale` | — | — | — | `upscale_factor` 1, 2 → 7,50; 4 → 15; 8 → 30 |
| `x-ai/grok-imagine-image` | 2,50 | — | — | не задаётся (размер выбирает модель) |

Где «—» в 1K/2K/4K: разрешение у модели не задаётся (выбирает модель) или такого значения нет. Картинка 2K: самая
дешёвая — Seedream 4 (3 ₽, и 4K по той же цене), затем Seedream 5 Lite (4 ₽ = 2K), Seedream 4.5 (5 ₽ = 2K, и 4K),
Qwen 2.1 (6), GPT Image 2.5 / GPT-5.4 Image 2 / FLUX.2 Pro (7), NB2 (7,20), Seedream 5 Pro (10), NB Pro (13,50),
FLUX.2 Flex (24).

### 6.2 Видео 5 с: 480p / 720p / 1080p, со звуком и без (₽ за ролик)

| модель | 480p без звука | 480p со звуком | 720p без | 720p со звуком | 1080p без | 1080p со звуком | примечание |
|---|---|---|---|---|---|---|---|
| `alibaba/happyhorse-1.0` | — | — | 99,9392 | — | 99,9392 | — | длительность 5 с; звука в параметрах нет; ставка не зависит от разрешения и звука |
| `alibaba/happyhorse-1.1` | — | — | 75,3969 | — | 75,3969 | — | длительность 5 с; звука в параметрах нет; ставка не зависит от разрешения и звука |
| `alibaba/wan-3.0` | 117,992 | 117,992 | 117,992 | 117,992 | 117,992 | 117,992 | длительность 5 с; ставка не зависит от разрешения и звука |
| `alibaba/wan-3.0-prime` | 165,1888 | 165,1888 | 165,1888 | 165,1888 | 165,1888 | 165,1888 | длительность 5 с; ставка не зависит от разрешения и звука |
| `bytedance/seedance-1.5-pro` | 5,25 | 10,50 | 10,50 | 21,00 | 22,50 | 45,00 | длительность 4 с |
| `bytedance/seedance-2` | 64,125 | 64,125 | 138,375 | 138,375 | 344,25 | 344,25 | длительность 5 с |
| `bytedance/seedance-2-5` | 94,50 | 94,50 | 212,625 | 212,625 | — | — | длительность 5 с |
| `bytedance/seedance-2-fast` | 52,3125 | 52,3125 | 111,375 | 111,375 | — | — | длительность 5 с |
| `bytedance/seedance-2-mini` | 12,825 | 12,825 | 27,675 | 27,675 | — | — | длительность 5 с |
| `gemini-omni-video` | — | — | 35,00 | — | 35,00 | — | длительность 4 с; звука в параметрах нет; 4k: 70 ₽ (4 с) — 95 ₽ (10 с) |
| `google/veo3` | — | — | 187,50 | — | — | — | за ролик; длительность и разрешение не выставлены (KIE: 8 с, 720p, со звуком); звука в параметрах нет |
| `google/veo3_fast` | — | — | 45,00 | — | — | — | за ролик; длительность и разрешение не выставлены (KIE: 8 с, 720p, со звуком); звука в параметрах нет |
| `grok-imagine-video-1-5` | 8,10 | — | 15,1875 | — | — | — | длительность 5 с; звука в параметрах нет |
| `kling/v2.6` | — | — | 42,00 | 82,50 | — | — | длительность 5 с |
| `kling/v2.6-motion-control` | — | — | 41,25 | — | 67,50 | — | секунды = длина входного видео (взято 5 с); звука в параметрах нет |
| `kling/v3` | — | — | 50,00 | 70,00 | 60,00 | 90,00 | длительность 5 с; 720p = mode std, 1080p = pro; 4K 225 ₽ |
| `kling/v3-motion-control` | — | — | 70,00 | — | 95,00 | — | секунды = длина входного видео (взято 5 с); звука в параметрах нет |
| `minimax/hailuo-3-max` | 47,1968 | — | — | — | — | — | длительность 5 с; звука в параметрах нет; ставка не зависит от разрешения и звука |
| `topaz/video-upscale` | — | — | 30,00 | — | — | — | секунды = длина входного видео (взято 5 с); звука в параметрах нет |
| `wan/2.5` | — | — | 45,00 | — | 75,00 | — | длительность 5 с; звука в параметрах нет |
| `wan/2.6` | — | — | 52,50 | — | 78,38 | — | длительность 5 с; звука в параметрах нет |

Где «—»: такого разрешения у модели нет или звук не параметр. 5 с без звука, самое дешёвое: 480p — Seedance 1.5 Pro
4 с (5,25), Grok Video (8,10), Seedance 2 Mini (12,83), MiniMax H3 Max 480p/768p (47,20 — одна цена); 720p — Seedance
1.5 Pro 4 с (10,50), Grok (15,19), Seedance 2 Mini (27,68), Gemini Omni 4 с (35), Wan 2.5 (45), Veo Fast (45, 8 с);
1080p — Seedance 1.5 Pro 4 с (22,50), Omni (35), Kling 3.0 pro (60), Wan 2.5 (75).

## 7. Сколько стоит типовая задача (таксономия `_common.md`)

Цена за 1 результат по каталогу; перебор N вариантов = × N. Качество и пригодность — у C1/C2/E; «[не проверено]» —
функция по документации. Полная таблица с формулами — `99-raw/experiments/B/02-price-calculator/typical_tasks.md`.

| код | что | кандидаты: цена за 1 результат |
|---|---|---|
| `IMG-HERO-PHOTO` | hero 16:9 2K | `gpt-image-2.5-sunburst` image_resolution=2K — **7,00**; `gemini-3-pro-image-preview` image_resolution=2K — **13,50** (mie); `gemini-3-pro-image-preview (google-vertex/global/flex)` image_resolution=2K — **7,9291** (flex [не проверено]); `5-pro-text-to-image` quality=high — **10,00** (high = 2K); `flux.2-pro` image_resolution=2K — **7,00** |
| `IMG-PRODUCT` | сцена по 1 фото товара, 2K | `gpt-image-2.5-sunburst` image_resolution=2K — **7,00**; `gemini-3-pro-image-preview` image_resolution=2K — **13,50**; `seedream-4.5` quality=basic — **5,00** (basic = 2K); `flux.2-pro` image_resolution=2K — **7,00** |
| `IMG-ILLUSTR` | 2D-иллюстрация 1:1 | `seedream-4.5` quality=basic — **5,00** (2K); `gpt-image-2.5-sunburst` image_resolution=1K — **4,00**; `gemini-3.1-flash-image-preview` image_resolution=1K — **4,80** |
| `IMG-SERIES` | 1 картинка серии по 3 референсам (×N) | `seedream-4.5` quality=basic — **5,00** (до 14 реф.); `gpt-image-2.5-sunburst` image_resolution=1K — **4,00** (до 16 реф.); `gemini-3.1-flash-image-preview` image_resolution=1K — **4,80** (до 14 реф.); `5-pro-text-to-image` quality=basic — **5,60** (+0,3 ₽ за реф. сверх первого) |
| `IMG-ICON3D` | объёмная иконка 1:1 1K | `gpt-image-2.5-sunburst` image_resolution=1K — **4,00**; `image-2.1` image_resolution=1K — **3,00** (сразу с альфой [не проверено]); `gemini-3.1-flash-image-preview` image_resolution=1K — **4,80** |
| `IMG-CUTOUT` | объект с прозрачным фоном | `image-2.1` image_resolution=1K — **3,00** (единственная с background в polza); `image-2.1` image_resolution=2K — **6,00** (2K) |
| `IMG-BG-ABSTRACT` | фон 16:9 | `z-image`  — **1,40**; `seedream-4` image_resolution=4K — **3,00** (4K по цене 1K); `flux.2-pro` image_resolution=2K — **7,00** |
| `IMG-TEXTURE` | текстура 1:1 (шов — постобработкой) | `seedream-4` image_resolution=2K — **3,00**; `z-image`  — **1,40**; `flux.2-pro` image_resolution=1K — **5,00** |
| `IMG-TEXT-LATIN` | баннер с текстом 2K | `gemini-3-pro-image-preview` image_resolution=2K — **13,50**; `gpt-image-2.5-sunburst` image_resolution=2K — **7,00**; `seedream-4.5` quality=basic — **5,00** |
| `IMG-TEXT-CYR` | баннер с кириллицей 2K | `gpt-image-2.5-sunburst` image_resolution=2K — **7,00**; `gemini-3-pro-image-preview` image_resolution=2K — **13,50**; `image-2.1` image_resolution=2K — **6,00** |
| `IMG-EDIT` | правка по инструкции / маске | `image-2.1` image_resolution=1K — **3,00** (маска: белое = менять); `gpt-5-image`  — **4,50** (маска: чёрное = менять); `gpt-image-2.5-sunburst` image_resolution=1K — **4,00** (без маски); `gemini-3.1-flash-image-preview` image_resolution=1K — **4,80** (без маски) |
| `IMG-OUTPAINT` | расширение до 21:9 2K по исходнику | `gpt-image-2.5-sunburst` image_resolution=2K — **7,00**; `gemini-3.1-flash-image-preview` image_resolution=2K — **7,20**; `seedream-4` image_resolution=4K — **3,00** |
| `IMG-MOCKUP` | мокап с настоящим скриншотом 2K | `gemini-3-pro-image-preview` image_resolution=2K — **13,50**; `gpt-image-2.5-sunburst` image_resolution=2K — **7,00** |
| `IMG-UPSCALE` | апскейл картинки | `image-upscale` upscale_factor=2 — **7,50** (×2); `image-upscale` upscale_factor=4 — **15,00** (×4); `seedream-4` image_resolution=4K — **3,00** (перегенерация в 4K по референсу) |
| `IMG-DRAFT` | эскиз для перебора | `z-image`  — **1,40**; `image`  — **2,25** (16:9 дешевле 1:1); `grok-imagine-image`  — **2,50**; `gemini-2.5-flash-image`  — **2,90** |
| `VID-HERO-LOOP` | петля 16:9 по 1–2 кадрам, без звука | `v3` mode=std, duration=5 — **50,00** (start = end кадр [не проверено]); `veo3_fast`  — **45,00** (8 с 720p у KIE; звук не отключается); `seedance-1.5-pro` resolution=720p, duration=4 — **10,50**; `hailuo-3-max` resolution=768p, duration=6 — **56,6362** |
| `VID-CINEMAGRAPH` | неподвижная камера, 4–5 с | `seedance-1.5-pro` resolution=720p, duration=4 — **10,50** (fixed_lens); `seedance-1.5-pro` resolution=1080p, duration=4 — **22,50** (1080p); `v3` mode=std, duration=5 — **50,00** (камера — только промтом) |
| `VID-I2V-PRODUCT` | оживление продукта 5–8 с | `veo3_fast`  — **45,00**; `v3` mode=pro, duration=5 — **60,00** (1080p); `seedance-2` resolution=720p, duration=5 — **138,375**; `gemini-omni-video` resolution=720p, duration=4 — **35,00** |
| `VID-ABSTRACT` | абстрактный фон 5 с | `grok-imagine-video-1-5` resolution=480p, duration=5 — **8,10**; `seedance-2-mini` resolution=480p, duration=5 — **12,825**; `wan-3.0` resolution=480p, duration=5 — **117,992** (плоская цена за секунду) |
| `VID-CAMERA` | пролёт камеры 5–8 с | `veo3_fast`  — **45,00**; `v3` mode=pro, duration=5 — **60,00**; `seedance-2` resolution=720p, duration=5 — **138,375** |
| `VID-CHARACTER` | маскот 5 с | `v3` mode=std, duration=5 — **50,00**; `v3-motion-control` mode=720p — **70,00** (по видео движения 5 с); `seedance-2` resolution=480p, duration=5 — **64,125** |
| `VID-LONG` | ролик ~15 с | `veo3_fast`  — **45,00** (+ extend 45 ₽ за шаг); `seedance-2-5` resolution=480p, duration=15 — **283,50**; `2.6` resolution=720p, duration=15 — **157,13** (за ролик); `wan-3.0` resolution=720p, duration=15 — **353,976** |
| `VID-V2V` | правка готового видео | `gemini-omni-video` resolution=720p, duration=4 — **70,00** (v2v); `seedance-2-mini` resolution=480p, duration=5 — **16,20** (видео-референс); `seedance-2` resolution=720p, duration=5 — **168,75** (видео-референс) |
| `VID-UPSCALE` | апскейл видео 5 с | `video-upscale` upscale_factor=2 — **30,00** (5 с входа); `video-upscale` upscale_factor=4 — **52,50** (5 с входа) |

Векторные задачи (`VEC-*`) медиа-моделями polza не решаются (SVG нет, Recraft нет): SVG пишет LLM через chat-модели
polza (токены), см. `../07-vector-svg-icons/` (агент G). `VID-ALPHA` и `VID-SCROLL` — генерация обычного ролика
(цены `VID-*` выше) + постобработка (`../09-video-pipeline/`).

## 8. Что ломает наивный код (сверено по гайдам и каталогу)

| № | Особенность | Где (модели) | Каталог | Гайд | OpenAPI | Что делать |
|---|---|---|---|---|---|---|
| 1 | Булевы — строки `"true"`/`"false"` | Seedance 1.5/2/2 Fast/2 Mini/2.5 (`generate_audio`, `fixed_lens`), Kling 3.0/2.6 (`sound`), Wan 2.5 (`enable_prompt_expansion`), Wan 2.6 (`multi_shots`), Wan 3.0/Prime (`generate_audio`), Veo (`enableTranslation`) | `values: ["true","false"]` | `"false"` строкой (seedance-1-5-pro, kling-3, wan-2-5, wan-2-6, seedance-2, veo-3-1) | `boolean`; для `generate_audio` строки приводятся | строки; исключения — `enhance_prompt` Qwen 2.1 (boolean), `isEnhance` GPT-5 Image (строка без `values`) |
| 2 | Длительность строкой | все видео с `duration` | строки в `values` у Seedance 1.5, Wan, Kling 2.6, Omni, Wan 3.0, HappyHorse, MiniMax; числа `min`/`max` у Seedance 2/2.5/Mini/Fast, Grok, Kling 3.0 | `"10"`, `"8"`, `"6"` | `duration: string` | строка всегда |
| 3 | `seeds`, а не `seed` | Veo 3.1 | `seeds` 10000–99999 | `"seeds": 12345` | в DTO только `seed` | `seeds` в диапазоне |
| 4 | Режим генерации явно | Veo 3.1 | `generationType` «авто-определяется по наличию изображений» | три режима с числом картинок | нет в DTO | задавать явно (`TEXT_2_VIDEO`, `FIRST_AND_LAST_FRAMES_2_VIDEO`, `REFERENCE_2_VIDEO` — только Fast) |
| 5 | Соотношение игнорируется при стартовом кадре | Kling 3.0, Kling 2.6 | «Игнорируется при наличии start frame» / «…изображения» | Kling 3: «игнорируется при start frame» | — | кадрировать картинку под нужное соотношение до вызова |
| 6 | Умолчание 1:1 у видео | Kling 3.0 (у KIE 16:9); MiniMax H3 Max — 21:9 | `default` | Kling 3: «по умолчанию 1:1» | — | `aspect_ratio` явно |
| 7 | Обязательные без default | Kling 3.0 `duration`; Kling 2.6 `aspect_ratio`; Seedance 1.5 Pro (цена) `resolution`/`duration`; Wan 2.5/2.6 (цена) | `required`, нет `default` | — | — | задавать; `polza.py` откажет |
| 8 | Id без префикса и слаги KIE | `gpt-image-2-5-flare`, `grok-imagine-video-1-5`, `gemini-omni-video`, `seedream/5-pro-text-to-image`; в cURL гайда Veo — `veo3`, `veo3_fast` | id каталога | `veo3` в примере | — | id только из каталога |
| 9 | Файлы — объекты, в гайдах — строки | Kling Motion Control 3/2.6, GPT-5.4 Image 2 | число файлов `min`/`max` | `"images": ["https://…"]` | `MediaFileDto {type, data}` | объекты; строки — тест |
| 10 | Три формы результата | все | — | `data.url`, `data[].url` (Lyria), `output.url` (NB2) | схемы отсутствуют | разбирать все (`polza.py` умеет) |
| 11 | Регистр значений | `mode: "4K"` (Kling), `image_resolution: "4K"`, но `resolution: "4k"` (Omni); `Auto` у Veo, `auto` у прочих | `values` | — | enum видео: `4k`, `2160p` | значение ровно из `values` |
| 12 | Условие цены ≠ имя параметра | Seedance 1.5 Pro: ступени `sound=…`, параметр `generate_audio` | `tiers` | — | — | калькулятор сопоставляет |
| 13 | `jpg` против `jpeg` | `output_format` | `values: png/jpeg/(webp)` | — | «jpg автоматически → jpeg» | `jpeg` |
| 14 | Противоположные маски | Qwen 2.1 (белое — менять) и GPT-5 Image у `mie` (чёрное — менять) | описания | — | нет `mask_url` в DTO | инвертировать маску под модель |
| 15 | Модели без `prompt` | Topaz Upscale (картинка, видео) | нет `prompt` | `"prompt": ""` | `prompt` обязателен в DTO | слать `""` (`polza.py` добавляет) |
| 16 | Лимит промта в описании ≠ `max_length` | Seedance 2 и 2 Fast («до 1536» / 20 000) | оба | 3–20 000 | — | держать ≤ 1536, пока не проверено |
| 17 | Дорогие умолчания | Seedance 2/Fast/Mini 15 с + звук; Seedance 2.5 5 с + звук; Grok 8 с | `default` | в cURL — явные значения | — | длительность и звук явно |
| 18 | Параметр из гайда, которого нет в каталоге | GPT-5.4 Image 2 `n`; Seedance 2 `multi_shots`; NB/NB Pro `output_format` | нет | есть | — | не слать до проверки (T7) |
| 19 | «Авто» вне диапазона | Seedance 2.5 `duration: -1` | `auto_value: -1` | — | «значение вне [min, max]» | только вместе с `videos` |
| 20 | Цена по длине входного видео | Kling Motion Control, Topaz Video | `unitParam: duration` без параметра `duration` | — | — | знать длину видео до вызова (`ffprobe`) |
| 21 | Перевод промта | Veo `enableTranslation: "true"` по умолчанию | `default` | «автоматический перевод на английский» | — | для текста в кадре на русском — `"false"` и проверка (KIE может отказать не-английскому промту) |

Все пункты ловит `polza.py` до отправки (кроме 10 и 21 — поведение ответа) `[проверено: B/04 — 51 ловушка]`.

## 9. Расхождения документации и каталога

| Модель | Документация (гайд `docs-repo/gaidy/…`, 18.09.2026) | Каталог (23.09.2026) | Позиция |
|---|---|---|---|
| `google/veo3`, `veo3_fast` | промт «до 2 000 символов»; `extend` — `prompt`, `seeds`, `duration` 3–10 с; `upscale_4k` синхронный; id `veo3` в cURL | `max_length` 60 000; `extend` — `prompt` ≤ 16 000, `seeds`, `watermark`, `model`; `upscale_4k` `async: true` | каталог; промт короче 2000 на всякий случай |
| `bytedance/seedance-2` | 480p/720p; промт 3–20 000; шлёт `multi_shots` | ещё 1080p («по документации KIE»); описание «до 1536»; `multi_shots` нет | каталог; `multi_shots` не слать |
| `bytedance/seedance-2-fast` | — | описание «до 1536», `max_length` 20 000 | ≤ 1536 |
| `bytedance/seedance-1.5-pro` | `generate_audio` | ступени по `sound` | сопоставлять |
| `kling/v3` | «`sound` обязательно true при `multi_shots`»; по умолчанию 1:1 | `multi_shots` нет; default 1:1 (у KIE 16:9) | мульти-шот недоступен |
| `google/gemini-3-pro-image-preview` | `output_format` png/jpeg; до 8 референсов (у Google до 14) | `output_format` нет; `images` ≤ 8 (`mie`), 14 (`bananalab`), 10 (Google) | каталог провайдера |
| `google/gemini-2.5-flash-image` | `output_format` png/jpeg | нет | не слать |
| `google/gemini-3.1-flash-image-preview` | «до 8 референсов»; путь `/v1/media/nanobanano-2`; результат `output.url` | `images` ≤ 14 (`mie`) | 14 по каталогу; разбор `output.url` |
| `google/gemini-3.1-flash-image` | гайда нет | `parameters` нет | не использовать до проверки |
| `openai/gpt-5.4-image-2` | провайдер `openai` «по умолчанию»; `@mie`; `n` 1–4; строки-URL | top — `mie`; `n` нет | `provider` объектом; без `n` |
| `openai/gpt-5-image` / `qwen/image-2.1` | — | маски противоположны | инвертировать |
| `topaz/image-upscale` | `"prompt": ""`, `upscale_factor` `"8"` | фактор 1/2/4/8 (у KIE 1/2/4 — данные P) | ×8 — проверить |
| `bytedance/seedream-4` | последний cURL — `bytedance/seedream-v4` | id `bytedance/seedream-4` | каталог |
| `qwen/image` | `strength: "0.8"`, `guidance_scale: "2.5"` строками | числа | числа |
| `gemini-omni-video` | `async` «по умолчанию true», «обязателен» | — (OpenAPI: `false`) | всегда `true` |
| `alibaba/wan-3.0`, `happyhorse-*` | гайдов нет | `images` «first/last frame», но `max: 1` | только первый кадр |
| `bytedance/seedance-2-5` | гайда нет | «1080p у Seedance 2.5 нет»; у KIE 1080p в enum (данные P) | каталог |
| Kling 2.5 Turbo, Seedream 3.0 | гайды есть | моделей нет (сняты) | не использовать гайды |
| 17 моделей | гайдов нет: GPT Image 2.5 Sunburst/Flare, Seedream 5 Pro, NB2 Lite, NB2 GA, Qwen Image 2/2.1, Z-Image; MiniMax H3 Max, Wan 3.0/Prime, HappyHorse 1.0/1.1, Seedance 2.5, Grok Video 1.5, Kling 2.6, Topaz Video | только каталог | каталог + описания параметров |

Кураторский список расхождений лежит и в данных: поле `doc_vs_catalog` в `media-models.normalized.json`.

## 10. Параметры вендоров и исполнителя, которых polza не выставляет

По документации KIE (исполнитель `mie`), снятой агентом P, и его заметкам [S11]; сверять с файлами агента P.

| Модель polza | Есть у KIE / вендора, нет в polza | Чем грозит |
|---|---|---|
| GPT Image 2.5 Sunburst/Flare | `background` `transparent`/`opaque`/`auto` (KIE) | прозрачный объект — только Qwen 2.1 или удаление фона после |
| Veo 3.1 Fast/Quality | `resolution` 720p/1080p/4k, `duration` 4/6/8 (default 8), модель `veo3_lite`; у Google — `negativePrompt`, `personGeneration`, `generateAudio` | нельзя короче/дешевле; звук всегда; 1080p/4K — только операциями апскейла |
| Seedance 2 | `first_frame_url`/`last_frame_url` (отдельно от референсов), `return_last_frame`, `reference_audio_urls`, 4k, `web_search`, `nsfw_checker`; до 9 картинок и 3 видео | смысл `images` в polza неясен — петли «первый = последний кадр» под вопросом |
| Seedance 2.5 | `first_frame_url`/`last_frame_url`, `output_format` mp4/mov, `return_last_frame`, 1080p (спорно) | то же |
| Kling 3.0 | `multi_shots` + `multi_prompt` (до 5 шотов по 1–12 с), `kling_elements` (`@element`, 2–4 картинки, видео, аудио) | мульти-шот и элементы недоступны |
| MiniMax H3 Max | `first_frame_url`/`last_frame_url`, разрешение 2K | потолок 768p |
| Qwen Image 2.1 | 21:9, 9:21; `enhance_prompt` по умолчанию `true` | нет широких баннеров |
| FLUX.2 Pro/Flex | у BFL API — `seed`, `steps`, `guidance`, `safety_tolerance`, `output_format` (у KIE их тоже нет) | нет повторяемости по зерну |
| Nano Banana (все) | у Gemini API — `seed`, `temperature`; у NB Pro до 14 референсов | серия без зерна; меньше референсов у `mie` |
| Topaz Upscale | — (у polza даже больше: ×8) | — |
| Все модели KIE | `nsfw_checker` (по умолчанию выключен), `callBackUrl` с подписью | — |

Чего нет в polza вовсе, но есть у KIE (Recraft Remove Background и Crisp Upscale, Ideogram V3, Imagen 4, Seedream 5
Pro Layer Decomposition, Grok Imagine Image 2.0, Qwen Image 3.0, Runway Gen-4/Aleph, PixVerse V6 с «First & Last
Frame Transition», Veo 3.1 Lite, Hailuo 02/2.3 и др.) — список и цены у агента P (`P-notes.md` §2).

## 11. Карточки вызова всех 44 моделей

Сгенерированы `99-raw/experiments/B/07-model-cards/gen_model_cards.py` (снимок 2026-09-23): обязательные и ценовые
параметры, все значения, заметки нормализатора («!»), расхождения с документацией («≠»), провайдеры, **самый дешёвый
валидный вызов** (проверен `polza_catalog.validate`; живой — `[не проверено]`). Все 44 тела — в
`minimal_jobs.jsonl` (сумма 1 086 ₽, целиком не запускать). Ссылки `example.com` — заглушки референсов.

#### `black-forest-labs/flux.2-flex` — Flux-2 Flex

Тип image · провайдер `mie` · добавлена 2026-02-20 · цена: 14,00–24,00 ₽ по image_resolution
- Обязательные: `prompt`; ценовые: `image_resolution`
- Параметры: `prompt` ≤5000; `aspect_ratio`=1:1/4:3/3:4/16:9/9:16/3:2/2:3; `image_resolution`=1K/2K; `images` 0–8
- Самый дешёвый валидный вызов — **14,00 ₽** (14,00 ₽ (ступень image_resolution=1K)):

```json
// black-forest-labs/flux.2-flex · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "black-forest-labs/flux.2-flex", "input": {"prompt": "test", "image_resolution": "1K"}, "async": true}
```

#### `black-forest-labs/flux.2-pro` — Flux-2 Pro

Тип image · провайдер `mie` · добавлена 2026-02-20 · цена: 5,00–7,00 ₽ по image_resolution
- Обязательные: `prompt`; ценовые: `image_resolution`
- Параметры: `prompt` ≤5000; `aspect_ratio`=1:1/4:3/3:4/16:9/9:16/3:2/2:3; `image_resolution`=1K/2K; `images` 0–8
- Самый дешёвый валидный вызов — **5,00 ₽** (5,00 ₽ (ступень image_resolution=1K)):

```json
// black-forest-labs/flux.2-pro · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "black-forest-labs/flux.2-pro", "input": {"prompt": "test", "image_resolution": "1K"}, "async": true}
```

#### `bytedance/seedream-4` — Seedream 4.0

Тип image · провайдер `mie` · добавлена 2026-02-20 · цена: 3,00 ₽/запрос
- Обязательные: `prompt`; ценовые: —
- Параметры: `prompt` ≤5000; `aspect_ratio`=1:1/4:3/3:4/3:2/2:3/16:9/9:16/21:9; `image_resolution`=1K/2K/4K; `images` 0–10; `seed` 1–4294967295
- ≠ последний cURL гайда использует id bytedance/seedream-v4 (ошибка)
- Самый дешёвый валидный вызов — **3,00 ₽** (3,00 ₽ за запрос):

```json
// bytedance/seedream-4 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "bytedance/seedream-4", "input": {"prompt": "test"}, "async": true}
```

#### `bytedance/seedream-4.5` — Seedream 4.5

Тип image · провайдер `mie` · добавлена 2026-02-20 · цена: 5,00 ₽/запрос
- Обязательные: `prompt`, `aspect_ratio`, `quality`; ценовые: —
- Параметры: `prompt` ≤3000; `aspect_ratio`=1:1/4:3/3:4/3:2/2:3/16:9/9:16/21:9 (умолч. 1:1); `images` 0–14; `quality`=basic/high (умолч. basic)
- Самый дешёвый валидный вызов — **5,00 ₽** (5,00 ₽ за запрос):

```json
// bytedance/seedream-4.5 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "bytedance/seedream-4.5", "input": {"prompt": "test", "aspect_ratio": "16:9", "quality": "basic"}, "async": true}
```

#### `bytedance/seedream-5-lite` — Seedream 5.0 Lite

Тип image · провайдер `mie` · добавлена 2026-02-27 · цена: 4,00 ₽/запрос
- Обязательные: `prompt`, `aspect_ratio`, `quality`; ценовые: —
- Параметры: `prompt` ≤2996; `aspect_ratio`=1:1/4:3/3:4/16:9/9:16/2:3/3:2/21:9 (умолч. 1:1); `images` 0–10; `quality`=basic/high (умолч. basic)
- Самый дешёвый валидный вызов — **4,00 ₽** (4,00 ₽ за запрос):

```json
// bytedance/seedream-5-lite · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "bytedance/seedream-5-lite", "input": {"prompt": "test", "aspect_ratio": "16:9", "quality": "basic"}, "async": true}
```

#### `google/gemini-2.5-flash-image` — Google: Gemini 2.5 Flash Image (Nano Banana)

Тип image · провайдер `mie` · добавлена 2026-01-28 · цена: 2,90 ₽/запрос
- Обязательные: `prompt`; ценовые: —
- Параметры: `prompt` ≤20000; `aspect_ratio`=1:1/9:16/16:9/3:4/4:3/3:2/2:3/5:4/4:5/21:9; `images` 0–8
- Провайдеры: `mie` (top) per_request 2,90/2,90/2,90 ₽ (1K/2K/4K); `bananalab` tiers 3,00/3,00/3,00 ₽ (1K/2K/4K); `google-vertex/global` tokens 4,5698/4,5698/4,5698 ₽ (1K/2K/4K); `google-ai-studio` tokens 4,5698/4,5698/4,5698 ₽ (1K/2K/4K); `google-ai-studio/flex` tokens 2,2849/2,2849/2,2849 ₽ (1K/2K/4K); `google-ai-studio/priority` tokens 8,2257/8,2257/8,2257 ₽ (1K/2K/4K); `google-vertex/global/flex` tokens 2,2849/2,2849/2,2849 ₽ (1K/2K/4K); `cloud-ru` tokens 0,0083/0,0083/0,0083 ₽ (1K/2K/4K)
- Самый дешёвый валидный вызов — **2,90 ₽** (2,90 ₽ за запрос):

```json
// google/gemini-2.5-flash-image · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "google/gemini-2.5-flash-image", "input": {"prompt": "test"}, "async": true}
```

#### `google/gemini-3-pro-image-preview` — Google: Nano Banana Pro (Gemini 3 Pro Image Preview)

Тип image · провайдер `mie` · добавлена 2026-01-28 · цена: 13,50–18,00 ₽ по image_resolution
- Обязательные: `prompt`; ценовые: `image_resolution`
- Параметры: `prompt` ≤20000; `aspect_ratio`=1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9/auto; `image_resolution`=1K/2K/4K; `images` 0–8
- ≠ images: у mie max 8, у bananalab 14, у Google (Gemini API) до 14
- Провайдеры: `mie` (top) tiers 13,50/13,50/18,00 ₽ (1K/2K/4K); `bananalab` tiers 13,50/13,50/18,00 ₽ (1K/2K/4K); `google-vertex/global` tokens 15,8817/15,8817/28,3417 ₽ (1K/2K/4K); `google-ai-studio/global` tokens 15,8817/15,8817/28,3417 ₽ (1K/2K/4K); `google-vertex/global/flex` tokens 7,9409/7,9409/14,1708 ₽ (1K/2K/4K); `google-ai-studio/global/flex` tokens 7,9409/7,9409/14,1708 ₽ (1K/2K/4K); `cloud-ru` tokens 0,055/0,055/0,055 ₽ (1K/2K/4K)
- Самый дешёвый валидный вызов — **13,50 ₽** (13,50 ₽ (ступень image_resolution=1K)):

```json
// google/gemini-3-pro-image-preview · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "google/gemini-3-pro-image-preview", "input": {"prompt": "test", "image_resolution": "1K"}, "async": true}
```

#### `google/gemini-3.1-flash-image` — Google: Nano Banana 2 (Gemini 3.1 Flash Image)

Тип image · провайдер `google-vertex/global` · добавлена 2026-06-24 · цена: токены: вых. картинка 7 079,52 ₽/1M
- Обязательные: —; ценовые: —
- Параметры: **нет в каталоге**
- ≠ нет parameters ни у одного провайдера — как вызывать через /v1/media, неизвестно
- Провайдеры: `google-vertex/global` (top) tokens 7,935/11,8995/17,8463 ₽ (1K/2K/4K); `google-ai-studio` tokens 7,935/11,8995/17,8463 ₽ (1K/2K/4K)
- Самый дешёвый валидный вызов — **7,9291 ₽** (0 вх. ток. × 58,996 ₽/1M + 1120 вых. image-ток. (1K) × 7 079,52 ₽/1M ≈ 7,9291 ₽ (+ текст/рассуждение модели: до 8,283 ₽)):

```json
// google/gemini-3.1-flash-image · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "google/gemini-3.1-flash-image", "input": {"prompt": ""}, "async": true}
```

#### `google/gemini-3.1-flash-image-preview` — Google: Nano Banana 2 (Gemini 3.1 Flash Image Preview)

Тип image · провайдер `mie` · добавлена 2026-02-26 · цена: 4,80–10,80 ₽ по image_resolution
- Обязательные: `prompt`; ценовые: `image_resolution`
- Параметры: `prompt` ≤20000; `aspect_ratio`=1:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9/auto; `image_resolution`=1K/2K/4K; `output_format`=png/jpeg; `images` 0–14
- ≠ гайд nanobanano-2.mdx: «до 8 референсов» и путь /v1/media/nanobanano-2; каталог mie — 14
- ≠ результат по гайду — output.url (в status.mdx — data.url)
- Провайдеры: `mie` (top) tiers 4,80/7,20/10,80 ₽ (1K/2K/4K); `bananalab` tiers 4,80/7,20/10,80 ₽ (1K/2K/4K); `google-ai-studio` tokens 7,935/11,8995/17,8463 ₽ (1K/2K/4K); `google-vertex/global` tokens 7,935/11,8995/17,8463 ₽ (1K/2K/4K); `google-vertex/global/flex` tokens 3,9675/5,9497/8,9231 ₽ (1K/2K/4K); `cloud-ru` tokens 0,0137/0,0137/0,0137 ₽ (1K/2K/4K)
- Самый дешёвый валидный вызов — **4,80 ₽** (4,80 ₽ (ступень image_resolution=1K)):

```json
// google/gemini-3.1-flash-image-preview · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "google/gemini-3.1-flash-image-preview", "input": {"prompt": "test", "image_resolution": "1K"}, "async": true}
```

#### `google/gemini-3.1-flash-lite-image` — Google: Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)

Тип image · провайдер `mie` · добавлена 2026-06-30 · цена: 2,90 ₽/запрос
- Обязательные: `prompt`; ценовые: —
- Параметры: `prompt` ≤20000; `aspect_ratio`=1:1/1:4/4:1/1:8/8:1/2:3/3:2/3:4/4:3/4:5/5:4/9:16/16:9/21:9/auto; `images` 0–10
- Провайдеры: `google-vertex/global` tokens 3,9675/3,9675/3,9675 ₽ (1K/2K/4K); `google-ai-studio` tokens 3,9675/3,9675/3,9675 ₽ (1K/2K/4K); `mie` (top) per_request 2,90/2,90/2,90 ₽ (1K/2K/4K)
- Самый дешёвый валидный вызов — **2,90 ₽** (2,90 ₽ за запрос):

```json
// google/gemini-3.1-flash-lite-image · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "google/gemini-3.1-flash-lite-image", "input": {"prompt": "test"}, "async": true}
```

#### `gpt-image-2-5-flare` — GPT Image 2.5 Flare

Тип image · провайдер `mie` · добавлена 2026-09-10 · цена: 4,00–11,00 ₽ по image_resolution
- Обязательные: `prompt`; ценовые: `image_resolution`
- Параметры: `prompt` ≤20000; `aspect_ratio`=auto/1:1/9:16/16:9/4:3/3:4/3:2/2:3/21:9/27:16/16:27/9:8/8:9 (умолч. auto); `image_resolution`=1K/2K/4K (умолч. 1K); `images` 0–16
- ! запасная ступень [] = максимум (11 ₽) — передавайте ценовые параметры явно
- Самый дешёвый валидный вызов — **4,00 ₽** (4,00 ₽ (ступень image_resolution=1K)):

```json
// gpt-image-2-5-flare · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "gpt-image-2-5-flare", "input": {"prompt": "test", "image_resolution": "1K"}, "async": true}
```

#### `openai/gpt-5-image` — OpenAI: GPT-5 Image

Тип image · провайдер `mie` · добавлена 2026-01-28 · цена: 4,50 ₽/запрос
- Обязательные: —; ценовые: —
- Параметры: `prompt` ≤4000; `aspect_ratio`=1:1/3:2/2:3 (умолч. 1:1); `images` 0–5; `mask_url`; `isEnhance` (умолч. false)
- ≠ mask_url «чёрные = менять, белые = оставить» — противоположно qwen/image-2.1
- Провайдеры: `mie` (top) per_request 4,50/4,50/4,50 ₽ (1K/2K/4K); `openai` tokens 5,102/5,102/5,102 ₽ (1K/2K/4K)
- Самый дешёвый валидный вызов — **4,50 ₽** (4,50 ₽ за запрос):

```json
// openai/gpt-5-image · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "openai/gpt-5-image", "input": {"prompt": "test", "aspect_ratio": "1:1"}, "async": true}
```

#### `openai/gpt-5-image-mini` — OpenAI: GPT-5 Image Mini

Тип image · провайдер `openai` · добавлена 2026-01-28 · цена: токены: вых. картинка 943,936 ₽/1M
- Обязательные: —; ценовые: —
- Параметры: `prompt` ≤32000; `images` 0–10
- Самый дешёвый валидный вызов — **0,9974 ₽** (2 вх. ток. × 294,98 ₽/1M + 1056 вых. image-ток. (medium) × 943,936 ₽/1M ≈ 0,9974 ₽ (+ текст/рассуждение модели: до 4,1633 ₽)):

```json
// openai/gpt-5-image-mini · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "openai/gpt-5-image-mini", "input": {"prompt": "test"}, "async": true}
```

#### `openai/gpt-5.4-image-2` — OpenAI: GPT-5.4 Image 2

Тип image · провайдер `mie` · добавлена 2026-04-22 · цена: 4,00–11,00 ₽ по image_resolution
- Обязательные: `prompt`; ценовые: `image_resolution`
- Параметры: `prompt` ≤20000; `aspect_ratio`=auto/1:1/9:16/16:9/4:3/3:4 (умолч. auto); `image_resolution`=1K/2K/4K (умолч. 1K); `images` 0–16
- ≠ гайд: провайдер openai «по умолчанию», каталог: top_provider = mie
- ≠ гайд: выбор провайдера @-синтаксисом openai/gpt-5.4-image-2@mie, aliases.mdx: для Media API алиасы не работают
- Провайдеры: `mie` (top) tiers 4,00/7,00/11,00 ₽ (1K/2K/4K); `openai` tokens  ₽ (1K/2K/4K)
- Самый дешёвый валидный вызов — **4,00 ₽** (4,00 ₽ (ступень image_resolution=1K)):

```json
// openai/gpt-5.4-image-2 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "openai/gpt-5.4-image-2", "input": {"prompt": "test", "image_resolution": "1K"}, "async": true}
```

#### `openai/gpt-image-1.5` — GPT Image 1.5

Тип image · провайдер `mie` · добавлена 2026-02-20 · цена: 3,00–16,50 ₽ по quality
- Обязательные: `prompt`, `aspect_ratio`, `quality`; ценовые: `quality`
- Параметры: `prompt`; `aspect_ratio`=1:1/2:3/3:2; `images` 0–16; `quality`=medium/high (умолч. medium)
- Самый дешёвый валидный вызов — **3,00 ₽** (3,00 ₽ (ступень quality=medium)):

```json
// openai/gpt-image-1.5 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "openai/gpt-image-1.5", "input": {"prompt": "test", "quality": "medium", "aspect_ratio": "1:1"}, "async": true}
```

#### `openai/gpt-image-2.5-sunburst` — GPT Image 2.5 Sunburst

Тип image · провайдер `mie` · добавлена 2026-09-10 · цена: 4,00–11,00 ₽ по image_resolution
- Обязательные: `prompt`; ценовые: `image_resolution`
- Параметры: `prompt` ≤20000; `aspect_ratio`=auto/1:1/3:2/2:3/4:3/3:4/16:9/9:16/21:9/27:16/16:27/9:8/8:9 (умолч. auto); `image_resolution`=1K/2K/4K (умолч. 1K); `images` 0–16
- ! запасная ступень [] = максимум (11 ₽) — передавайте ценовые параметры явно
- Самый дешёвый валидный вызов — **4,00 ₽** (4,00 ₽ (ступень image_resolution=1K)):

```json
// openai/gpt-image-2.5-sunburst · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "openai/gpt-image-2.5-sunburst", "input": {"prompt": "test", "image_resolution": "1K"}, "async": true}
```

#### `qwen/image` — Qwen Image

Тип image · провайдер `mie` · добавлена 2026-02-23 · цена: 2,25–3,00 ₽ по aspect_ratio
- Обязательные: `prompt`; ценовые: `aspect_ratio`
- Параметры: `prompt`; `aspect_ratio`=1:1/3:4/4:3/9:16/16:9; `output_format`=png/jpeg; `images` 0–1; `strength` 0–1 (умолч. 0.8); `guidance_scale` 0–20 (умолч. 2.5)
- ! запасная ступень [] = максимум (3 ₽) — передавайте ценовые параметры явно
- Самый дешёвый валидный вызов — **2,25 ₽** (2,25 ₽ (ступень aspect_ratio=9:16)):

```json
// qwen/image · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "qwen/image", "input": {"prompt": "test", "aspect_ratio": "9:16"}, "async": true}
```

#### `qwen/image-2` — Qwen Image 2

Тип image · провайдер `mie` · добавлена 2026-03-17 · цена: 4,00 ₽/запрос
- Обязательные: `prompt`; ценовые: —
- Параметры: `prompt` ≤5000; `aspect_ratio`=1:1/3:4/4:3/9:16/16:9; `output_format`=png/jpeg; `images` 0–3
- Самый дешёвый валидный вызов — **4,00 ₽** (4,00 ₽ за запрос):

```json
// qwen/image-2 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "qwen/image-2", "input": {"prompt": "test"}, "async": true}
```

#### `qwen/image-2.1` — Qwen Image 2.1

Тип image · провайдер `mie` · добавлена 2026-09-21 · цена: 3,00–6,00 ₽ по image_resolution
- Обязательные: `prompt`; ценовые: `image_resolution`
- Параметры: `prompt` ≤5000; `aspect_ratio`=1:1/4:3/3:4/3:2/2:3/16:9/9:16; `image_resolution`=1K/2K (умолч. 1K); `output_format`=png/webp/jpeg (умолч. png); `images` 0–10; `seed`; `mask_url`; `background`=opaque/transparent (умолч. opaque); `enhance_prompt` (умолч. False)
- ! запасная ступень [] = максимум (6 ₽) — передавайте ценовые параметры явно
- ≠ mask_url «белое — менять, чёрное — оставить» — противоположно openai/gpt-5-image
- Самый дешёвый валидный вызов — **3,00 ₽** (3,00 ₽ (ступень image_resolution=1K)):

```json
// qwen/image-2.1 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "qwen/image-2.1", "input": {"prompt": "test", "image_resolution": "1K"}, "async": true}
```

#### `seedream/5-pro-text-to-image` — Seedream 5.0 Pro

Тип image · провайдер `mie` · добавлена 2026-07-14 · цена: 5,00–12,70 ₽ по quality, images
- Обязательные: `prompt`, `aspect_ratio`, `quality`; ценовые: `quality`, `images`
- Параметры: `prompt`; `aspect_ratio`=1:1/4:3/3:4/16:9/9:16/2:3/3:2 (умолч. 1:1); `output_format`=png/jpeg (умолч. png); `images` 0–10; `quality`=basic/high (умолч. basic)
- Самый дешёвый валидный вызов — **5,00 ₽** (5,00 ₽ (ступень quality=basic)):

```json
// seedream/5-pro-text-to-image · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "seedream/5-pro-text-to-image", "input": {"prompt": "test", "quality": "basic", "aspect_ratio": "16:9"}, "async": true}
```

#### `tongyi-mai/z-image` — Z-Image

Тип image · провайдер `mie` · добавлена 2026-02-20 · цена: 1,40 ₽/запрос
- Обязательные: `prompt`, `aspect_ratio`; ценовые: —
- Параметры: `prompt` ≤1000; `aspect_ratio`=1:1/4:3/3:4/16:9/9:16 (умолч. 1:1); `images` 0–0
- Самый дешёвый валидный вызов — **1,40 ₽** (1,40 ₽ за запрос):

```json
// tongyi-mai/z-image · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "tongyi-mai/z-image", "input": {"prompt": "test", "aspect_ratio": "16:9"}, "async": true}
```

#### `topaz/image-upscale` — Topaz Upscale

Тип image · провайдер `mie` · добавлена 2026-02-23 · цена: 7,50–30,00 ₽ по upscale_factor
- Обязательные: `images`, `upscale_factor`; ценовые: `upscale_factor`
- Параметры: `images` 1–1; `upscale_factor`=1/2/4/8 (умолч. 2)
- ≠ upscale_factor 8 есть в каталоге; у KIE — 1/2/4 (агент P)
- Самый дешёвый валидный вызов — **7,50 ₽** (7,50 ₽ (ступень upscale_factor=1)):

```json
// topaz/image-upscale · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "topaz/image-upscale", "input": {"images": ["https://example.com/ref.png"], "upscale_factor": "1", "prompt": ""}, "async": true}
```

#### `x-ai/grok-imagine-image` — Grok Image

Тип image · провайдер `mie` · добавлена 2026-02-20 · цена: 2,50 ₽/запрос
- Обязательные: `prompt`; ценовые: —
- Параметры: `prompt` ≤5000; `aspect_ratio`=1:1/2:3/3:2; `images` 0–1
- Самый дешёвый валидный вызов — **2,50 ₽** (2,50 ₽ за запрос):

```json
// x-ai/grok-imagine-image · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "x-ai/grok-imagine-image", "input": {"prompt": "test"}, "async": true}
```

#### `alibaba/happyhorse-1.0` — Alibaba: HappyHorse 1.0

Тип video · провайдер `Alibaba` · добавлена 2026-06-24 · цена: 19,9878 ₽/с
- Обязательные: `prompt`; ценовые: `duration`
- Параметры: `prompt`; `aspect_ratio`=16:9/9:16/1:1/4:3/3:4/21:9/9:21 (умолч. 16:9); `resolution`=720p/1080p (умолч. 720p); `duration`=3/4/5/6/7/8/9/10/11/12/13/14/15 (умолч. 3); `images` –1; `seed`
- Самый дешёвый валидный вызов — **59,9635 ₽** (19,9878 ₽/с × 3 с = 59,9635 ₽):

```json
// alibaba/happyhorse-1.0 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "alibaba/happyhorse-1.0", "input": {"prompt": "test", "duration": "3", "aspect_ratio": "16:9"}, "async": true}
```

#### `alibaba/happyhorse-1.1` — Alibaba: HappyHorse 1.1

Тип video · провайдер `Alibaba` · добавлена 2026-06-24 · цена: 15,0794 ₽/с
- Обязательные: `prompt`; ценовые: `duration`
- Параметры: `prompt`; `aspect_ratio`=16:9/9:16/1:1/4:3/3:4/21:9/9:21 (умолч. 16:9); `resolution`=720p/1080p (умолч. 720p); `duration`=3/4/5/6/7/8/9/10/11/12/13/14/15 (умолч. 3); `images` –1; `seed`
- Самый дешёвый валидный вызов — **45,2381 ₽** (15,0794 ₽/с × 3 с = 45,2381 ₽):

```json
// alibaba/happyhorse-1.1 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "alibaba/happyhorse-1.1", "input": {"prompt": "test", "duration": "3", "aspect_ratio": "16:9"}, "async": true}
```

#### `alibaba/wan-3.0` — Alibaba: Wan 3.0

Тип video · провайдер `Alibaba` · добавлена 2026-08-25 · цена: 23,5984 ₽/с
- Обязательные: `prompt`; ценовые: `duration`
- Параметры: `prompt`; `aspect_ratio`=16:9/4:3/1:1/3:4/9:16 (умолч. 16:9); `resolution`=480p/720p/1080p (умолч. 480p); `duration`=2/3/4/5/6/7/8/9/10/11/12/13/14/15/16/17/18/19/20/21/22/23/24/25/26/27/28/29/30 (умолч. 2); `images` –1; `seed`; `generate_audio`=true/false (умолч. false)
- Самый дешёвый валидный вызов — **47,1968 ₽** (23,5984 ₽/с × 2 с = 47,1968 ₽):

```json
// alibaba/wan-3.0 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "alibaba/wan-3.0", "input": {"prompt": "test", "generate_audio": "false", "duration": "2", "aspect_ratio": "16:9"}, "async": true}
```

#### `alibaba/wan-3.0-prime` — Alibaba: Wan 3.0 Prime

Тип video · провайдер `openrouter` · добавлена 2026-08-27 · цена: 33,0378 ₽/с
- Обязательные: `prompt`; ценовые: `duration`
- Параметры: `prompt`; `aspect_ratio`=16:9/4:3/1:1/3:4/9:16 (умолч. 16:9); `resolution`=480p/720p/1080p (умолч. 480p); `duration`=2/3/4/5/6/7/8/9/10/11/12/13/14/15/16/17/18/19/20/21/22/23/24/25/26/27/28/29/30 (умолч. 2); `images` –1; `seed`; `generate_audio`=true/false (умолч. false)
- Самый дешёвый валидный вызов — **66,0755 ₽** (33,0378 ₽/с × 2 с = 66,0755 ₽):

```json
// alibaba/wan-3.0-prime · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "alibaba/wan-3.0-prime", "input": {"prompt": "test", "generate_audio": "false", "duration": "2", "aspect_ratio": "16:9"}, "async": true}
```

#### `bytedance/seedance-1.5-pro` — Seedance 1.5 Pro

Тип video · провайдер `mie` · добавлена 2026-02-20 · цена: 5,25–135,00 ₽ по resolution, duration, generate_audio
- Обязательные: `prompt`; ценовые: `resolution`, `duration`, `generate_audio`
- Параметры: `prompt` ≤2500; `aspect_ratio`=1:1/21:9/4:3/3:4/16:9/9:16; `resolution`=480p/720p/1080p; `duration`=4/8/12; `images` 0–2; `fixed_lens`=true/false (умолч. false); `generate_audio`=true/false (умолч. false)
- ! запасная ступень [] = максимум (135 ₽) — передавайте ценовые параметры явно
- ! цена: условие sound=…, параметр generate_audio (калькулятор сопоставляет)
- ≠ цена: условие ступени sound=…, а параметр называется generate_audio
- Самый дешёвый валидный вызов — **5,25 ₽** (5,25 ₽ (ступень resolution=480p, duration=4, sound=false)):

```json
// bytedance/seedance-1.5-pro · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "bytedance/seedance-1.5-pro", "input": {"prompt": "test", "generate_audio": "false", "duration": "4", "resolution": "480p", "aspect_ratio": "16:9"}, "async": true}
```

#### `bytedance/seedance-2` — Seedance 2

Тип video · провайдер `mie` · добавлена 2026-04-15 · цена: 12,825–83,70 ₽/с по resolution, videos
- Обязательные: `prompt`; ценовые: `resolution`, `videos`, `duration`
- Параметры: `prompt` ≤20000; `aspect_ratio`=16:9/4:3/1:1/3:4/9:16/21:9 (умолч. 16:9); `resolution`=480p/720p/1080p (умолч. 720p); `duration` 4–15 (умолч. 15); `images` 0–5; `videos` 0–1; `generate_audio`=true/false (умолч. true)
- ! generate_audio: default true — звук включён по умолчанию
- ! duration: default 15 с (дорого при цене за секунду)
- ! запасная ступень [] = максимум (83.7 ₽) — передавайте ценовые параметры явно
- ! prompt: описание «до 1536 символов», max_length 20000
- ≠ prompt: описание «до 1536 символов», max_length 20000; гайд — 3–20000
- ≠ resolution: гайд 480p/720p, каталог ещё 1080p («по документации KIE»)
- ≠ гайд шлёт multi_shots, которого нет в параметрах каталога
- Самый дешёвый валидный вызов — **51,30 ₽** (12,825 ₽/с × 4 с = 51,30 ₽ (ступень resolution=480p, has_video=false)):

```json
// bytedance/seedance-2 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "bytedance/seedance-2", "input": {"prompt": "test", "generate_audio": "false", "duration": "4", "resolution": "480p", "aspect_ratio": "16:9"}, "async": true}
```

#### `bytedance/seedance-2-5` — Seedance 2.5

Тип video · провайдер `mie` · добавлена 2026-08-25 · цена: 18,90–51,30 ₽/с по resolution, videos
- Обязательные: `prompt`; ценовые: `resolution`, `videos`, `duration`
- Параметры: `prompt` ≤30000; `aspect_ratio`=16:9/4:3/1:1/3:4/9:16/21:9/auto (умолч. auto); `resolution`=480p/720p (умолч. 720p); `duration` 4–30 (умолч. 5) (auto -1); `images` 0–30; `videos` 0–10; `generate_audio`=true/false (умолч. true)
- ! generate_audio: default true — звук включён по умолчанию
- ! duration: auto_value -1 — длительность по референсу
- ! запасная ступень [] = максимум (51.3 ₽) — передавайте ценовые параметры явно
- Самый дешёвый валидный вызов — **75,60 ₽** (18,90 ₽/с × 4 с = 75,60 ₽ (ступень resolution=480p, has_video=false)):

```json
// bytedance/seedance-2-5 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "bytedance/seedance-2-5", "input": {"prompt": "test", "generate_audio": "false", "duration": "4", "resolution": "480p", "aspect_ratio": "16:9"}, "async": true}
```

#### `bytedance/seedance-2-fast` — Seedance 2 Fast

Тип video · провайдер `mie` · добавлена 2026-04-15 · цена: 10,4625–22,275 ₽/с по resolution
- Обязательные: `prompt`; ценовые: `resolution`, `duration`
- Параметры: `prompt` ≤20000; `aspect_ratio`=16:9/4:3/1:1/3:4/9:16/21:9 (умолч. 16:9); `resolution`=480p/720p (умолч. 720p); `duration` 4–15 (умолч. 15); `images` 0–5; `videos` 0–1; `generate_audio`=true/false (умолч. true)
- ! generate_audio: default true — звук включён по умолчанию
- ! duration: default 15 с (дорого при цене за секунду)
- ! запасная ступень [] = максимум (22.275 ₽) — передавайте ценовые параметры явно
- ! prompt: описание «до 1536 символов», max_length 20000
- ≠ prompt: описание «до 1536 символов», max_length 20000
- Самый дешёвый валидный вызов — **41,85 ₽** (10,4625 ₽/с × 4 с = 41,85 ₽ (ступень resolution=480p)):

```json
// bytedance/seedance-2-fast · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "bytedance/seedance-2-fast", "input": {"prompt": "test", "generate_audio": "false", "duration": "4", "resolution": "480p", "aspect_ratio": "16:9"}, "async": true}
```

#### `bytedance/seedance-2-mini` — Seedance 2 Mini

Тип video · провайдер `mie` · добавлена 2026-07-01 · цена: 2,565–6,75 ₽/с по resolution, videos
- Обязательные: `prompt`; ценовые: `resolution`, `videos`, `duration`
- Параметры: `prompt` ≤20000; `aspect_ratio`=16:9/4:3/1:1/3:4/9:16/21:9/auto (умолч. 16:9); `resolution`=480p/720p (умолч. 720p); `duration` 4–15 (умолч. 15); `images` 0–9; `videos` 0–3; `generate_audio`=true/false (умолч. true)
- ! generate_audio: default true — звук включён по умолчанию
- ! duration: default 15 с (дорого при цене за секунду)
- ! запасная ступень [] = максимум (6.75 ₽) — передавайте ценовые параметры явно
- Самый дешёвый валидный вызов — **10,26 ₽** (2,565 ₽/с × 4 с = 10,26 ₽ (ступень resolution=480p, has_video=false)):

```json
// bytedance/seedance-2-mini · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "bytedance/seedance-2-mini", "input": {"prompt": "test", "generate_audio": "false", "duration": "4", "resolution": "480p", "aspect_ratio": "16:9"}, "async": true}
```

#### `gemini-omni-video` — Gemini Omni Video

Тип video · провайдер `mie` · добавлена 2026-06-08 · цена: 35,00–115,00 ₽ по duration, videos, resolution
- Обязательные: `prompt`, `duration`; ценовые: `duration`, `videos`, `resolution`
- Параметры: `prompt` ≤20000; `aspect_ratio`=16:9/9:16 (умолч. 16:9); `resolution`=720p/1080p/4k (умолч. 720p); `duration`=4/6/8/10 (умолч. 4); `images` 0–7; `videos` 0–1; `seed` 0–2147483647; `audio_ids` 0–3; `character_ids` 0–3
- ≠ гайд: async «по умолчанию true» и «обязателен»; OpenAPI MediaRequestDto: async default false
- Самый дешёвый валидный вызов — **35,00 ₽** (35,00 ₽ (ступень resolution=720p, duration=4, has_video=false)):

```json
// gemini-omni-video · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "gemini-omni-video", "input": {"prompt": "test", "duration": "4", "resolution": "720p", "aspect_ratio": "16:9"}, "async": true}
```

#### `google/veo3` — Veo 3.1 Quality

Тип video · провайдер `mie` · добавлена 2026-02-20 · цена: 187,50 ₽/запрос · операции: extend 45,00 ₽, upscale_1080p 10,00 ₽, upscale_4k 90,00 ₽
- Обязательные: `prompt`; ценовые: —
- Параметры: `prompt` ≤60000; `aspect_ratio`=16:9/9:16/Auto (умолч. 16:9); `seeds` 10000–99999; `watermark` ≤50; `images` 0–2; `generationType`=TEXT_2_VIDEO/FIRST_AND_LAST_FRAMES_2_VIDEO; `enableTranslation`=true/false (умолч. true)
- ≠ prompt: гайд veo-3-1.mdx «до 2 000 символов», каталог max_length 60000
- ≠ images: каталог max 2 (FIRST_AND_LAST_FRAMES_2_VIDEO); гайд: Quality до 2, Fast до 3
- ≠ длительности и разрешения нет в параметрах; у KIE Veo 3.1 есть duration 4/6/8 и resolution 720p/1080p/4k — polza их не выставляет
- ≠ operations: upscale_4k в каталоге async=true, в media/operations.mdx — «синхронная»
- ≠ extend: каталог prompt max_length 16000 + seeds/watermark/model; operations.mdx — prompt, seeds, duration 3–10 с
- Самый дешёвый валидный вызов — **187,50 ₽** (187,50 ₽ за запрос):

```json
// google/veo3 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "google/veo3", "input": {"prompt": "test", "aspect_ratio": "16:9", "generationType": "TEXT_2_VIDEO"}, "async": true}
```

#### `google/veo3_fast` — Veo 3.1 Fast

Тип video · провайдер `mie` · добавлена 2026-02-20 · цена: 45,00 ₽/запрос · операции: extend 45,00 ₽, upscale_1080p 10,00 ₽, upscale_4k 90,00 ₽
- Обязательные: `prompt`; ценовые: —
- Параметры: `prompt` ≤60000; `aspect_ratio`=16:9/9:16/Auto (умолч. 16:9); `seeds` 10000–99999; `watermark` ≤50; `images` 0–3; `generationType`=TEXT_2_VIDEO/FIRST_AND_LAST_FRAMES_2_VIDEO/REFERENCE_2_VIDEO; `enableTranslation`=true/false (умолч. true)
- ≠ prompt: гайд «до 2 000 символов», каталог max_length 60000
- ≠ REFERENCE_2_VIDEO — только Fast (values каталога совпадают с гайдом)
- ≠ в cURL гайда id без префикса: veo3 / veo3_fast
- Самый дешёвый валидный вызов — **45,00 ₽** (45,00 ₽ за запрос):

```json
// google/veo3_fast · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "google/veo3_fast", "input": {"prompt": "test", "aspect_ratio": "16:9", "generationType": "TEXT_2_VIDEO"}, "async": true}
```

#### `grok-imagine-video-1-5` — Grok Imagine Video 1.5 Preview

Тип video · провайдер `mie` · добавлена 2026-08-24 · цена: 1,62–3,0375 ₽/с по resolution
- Обязательные: `prompt`; ценовые: `resolution`, `duration`
- Параметры: `prompt` ≤4096; `aspect_ratio`=1:1/16:9/9:16/3:2/2:3/auto (умолч. auto); `resolution`=480p/720p (умолч. 480p); `duration` 1–15 (умолч. 8); `images` 0–7
- ! duration: default 8 с (дорого при цене за секунду)
- ! запасная ступень [] = максимум (3.0375 ₽) — передавайте ценовые параметры явно
- Самый дешёвый валидный вызов — **1,62 ₽** (1,62 ₽/с × 1 с = 1,62 ₽ (ступень resolution=480p)):

```json
// grok-imagine-video-1-5 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "grok-imagine-video-1-5", "input": {"prompt": "test", "duration": "1", "resolution": "480p", "aspect_ratio": "16:9"}, "async": true}
```

#### `kling/v2.6` — Kling 2.6

Тип video · провайдер `mie` · добавлена 2026-02-20 · цена: 42,00–165,00 ₽ по duration, sound
- Обязательные: `prompt`, `aspect_ratio`, `duration`, `sound`; ценовые: `duration`, `sound`
- Параметры: `prompt`; `aspect_ratio`=1:1/16:9/9:16; `duration`=5/10 (умолч. 5); `images` 0–1; `sound`=true/false (умолч. false)
- Самый дешёвый валидный вызов — **42,00 ₽** (42,00 ₽ (ступень duration=5, sound=false)):

```json
// kling/v2.6 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "kling/v2.6", "input": {"prompt": "test", "sound": "false", "duration": "5", "aspect_ratio": "16:9"}, "async": true}
```

#### `kling/v2.6-motion-control` — Kling 2.6 Motion Control

Тип video · провайдер `mie` · добавлена 2026-02-20 · цена: 8,25–13,50 ₽/с по mode
- Обязательные: `images`, `videos`, `mode`, `character_orientation`; ценовые: `mode`
- Параметры: `prompt` ≤2500; `images` 1–1; `videos` 1–1; `mode`=720p/1080p (умолч. 720p); `character_orientation`=image/video
- ! запасная ступень [] = максимум (13.5 ₽) — передавайте ценовые параметры явно
- Самый дешёвый валидный вызов — **24,75 ₽** (8,25 ₽/с × 3 с = 24,75 ₽ (ступень mode=720p)):

```json
// kling/v2.6-motion-control · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "kling/v2.6-motion-control", "input": {"prompt": "test", "images": ["https://example.com/ref.png"], "videos": ["https://example.com/ref.mp4"], "mode": "720p", "character_orientation": "image"}, "async": true}
```

#### `kling/v3` — Kling 3.0

Тип video · провайдер `mie` · добавлена 2026-02-20 · цена: 10,00–45,00 ₽/с по mode, sound
- Обязательные: `prompt`, `duration`, `mode`, `sound`; ценовые: `mode`, `sound`, `duration`
- Параметры: `prompt` ≤2500; `aspect_ratio`=16:9/9:16/1:1 (умолч. 1:1); `duration` 3–15; `images` 0–2; `mode`=std/pro/4K (умолч. std); `sound`=true/false (умолч. false)
- ! aspect_ratio: default 1:1
- ! запасная ступень [] = максимум (45 ₽) — передавайте ценовые параметры явно
- ≠ sound: «обязательно true при multi_shots», но multi_shots нет в параметрах каталога
- ≠ aspect_ratio: default 1:1 (у KIE — 16:9); игнорируется при start frame
- Самый дешёвый валидный вызов — **30,00 ₽** (10,00 ₽/с × 3 с = 30,00 ₽ (ступень mode=std, sound=false)):

```json
// kling/v3 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "kling/v3", "input": {"prompt": "test", "sound": "false", "duration": "3", "mode": "std", "aspect_ratio": "16:9"}, "async": true}
```

#### `kling/v3-motion-control` — Kling 3.0 Motion Control

Тип video · провайдер `mie` · добавлена 2026-03-12 · цена: 14,00–19,00 ₽/с по mode
- Обязательные: `images`, `videos`; ценовые: `mode`
- Параметры: `prompt` ≤2500; `images` 1–1; `videos` 1–1; `mode`=720p/1080p (умолч. 720p); `character_orientation`=image/video
- ! запасная ступень [] = максимум (19 ₽) — передавайте ценовые параметры явно
- Самый дешёвый валидный вызов — **42,00 ₽** (14,00 ₽/с × 3 с = 42,00 ₽ (ступень mode=720p)):

```json
// kling/v3-motion-control · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "kling/v3-motion-control", "input": {"prompt": "test", "images": ["https://example.com/ref.png"], "videos": ["https://example.com/ref.mp4"], "mode": "720p", "character_orientation": "image"}, "async": true}
```

#### `minimax/hailuo-3-max` — MiniMax: H3 Max

Тип video · провайдер `openrouter` · добавлена 2026-09-02 · цена: 9,4394 ₽/с
- Обязательные: `prompt`; ценовые: `duration`
- Параметры: `prompt`; `aspect_ratio`=21:9/16:9/4:3/1:1/3:4/9:16 (умолч. 21:9); `resolution`=768p/480p (умолч. 768p); `duration`=5/6/7/8/9/10/11/12/13/14/15 (умолч. 5); `images` –2
- ! aspect_ratio: default 21:9
- Самый дешёвый валидный вызов — **47,1968 ₽** (9,4394 ₽/с × 5 с = 47,1968 ₽):

```json
// minimax/hailuo-3-max · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "minimax/hailuo-3-max", "input": {"prompt": "test", "duration": "5", "aspect_ratio": "16:9"}, "async": true}
```

#### `topaz/video-upscale` — Topaz Video Upscale

Тип video · провайдер `mie` · добавлена 2026-02-23 · цена: 6,00–10,50 ₽/с по upscale_factor
- Обязательные: `videos`; ценовые: `upscale_factor`
- Параметры: `images` 0–0; `videos` 1–1; `upscale_factor`=1/2/4 (умолч. 2)
- Самый дешёвый валидный вызов — **18,00 ₽** (6,00 ₽/с × 3 с = 18,00 ₽ (ступень upscale_factor=1)):

```json
// topaz/video-upscale · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "topaz/video-upscale", "input": {"videos": ["https://example.com/ref.mp4"], "upscale_factor": "1", "prompt": ""}, "async": true}
```

#### `wan/2.5` — Wan 2.5

Тип video · провайдер `mie` · добавлена 2026-02-20 · цена: 45,00–150,00 ₽ по resolution, duration
- Обязательные: `prompt`; ценовые: `resolution`, `duration`
- Параметры: `prompt` ≤800; `aspect_ratio`=16:9/9:16/1:1; `resolution`=720p/1080p; `duration`=5/10; `images` 0–1; `seed` -1–2147483647; `negative_prompt` ≤500; `enable_prompt_expansion`=true/false (умолч. false)
- Самый дешёвый валидный вызов — **45,00 ₽** (45,00 ₽ (ступень resolution=720p, duration=5)):

```json
// wan/2.5 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "wan/2.5", "input": {"prompt": "test", "duration": "5", "resolution": "720p", "aspect_ratio": "16:9"}, "async": true}
```

#### `wan/2.6` — Wan 2.6

Тип video · провайдер `mie` · добавлена 2026-02-20 · цена: 52,50–236,25 ₽ по resolution, duration
- Обязательные: `prompt`; ценовые: `resolution`, `duration`
- Параметры: `prompt` ≤5000; `resolution`=720p/1080p; `duration`=5/10/15; `images` 0–1; `multi_shots`=true/false (умолч. false)
- Самый дешёвый валидный вызов — **52,50 ₽** (52,50 ₽ (ступень resolution=720p, duration=5)):

```json
// wan/2.6 · polza 2026-09-23 · [проверено: валидатор B/07] · живой вызов [не проверено]
{"model": "wan/2.6", "input": {"prompt": "test", "duration": "5", "resolution": "720p"}, "async": true}
```


## 12. Проверить в фазе 5 (уровень моделей и цен; уровень API — файл 01 §14)

| № | Код | Гипотеза | Минимальный тест | Модель и параметры | ₽ | Успех | Ценность |
|---|---|---|---|---|---|---|---|
| 1 | — | polza берёт default каталога, а не `[]`, если ценовой параметр не передан | 1 картинка без `image_resolution` | `openai/gpt-image-2.5-sunburst`, 4:3 (`--no-fill`) | 4 / 11 | `cost_rub` = 4 | 3 |
| 2 | `VID-HERO-LOOP` | `images` у Seedance 2 — первый/последний кадр, а не референсы | 2 одинаковые картинки, 4 с, без звука | `bytedance/seedance-2-mini`, 480p, `duration: "4"`, `generate_audio: "false"` | 10,26 | первый и последний кадр ≈ входу (SSIM ≥ 0,9) | 3 |
| 3 | `VID-HERO-LOOP` | Veo Fast `FIRST_AND_LAST_FRAMES_2_VIDEO` с одинаковыми кадрами даёт петлю; ролик 8 с, 720p, со звуком | 1 ролик | `google/veo3_fast`, 2 одинаковые картинки, `seeds` | 45 | шов SSIM ≥ 0,9; ffprobe: длительность, разрешение, звук | 3 |
| 4 | `VID-HERO-LOOP` | Kling 3.0 std: start = end кадр | 1 ролик 3 с | `kling/v3`, `mode: "std"`, `sound: "false"`, `duration: "3"`, 2 одинаковые картинки | 30 | шов SSIM ≥ 0,9 | 2 |
| 5 | `VID-CINEMAGRAPH` | `fixed_lens: "true"` у Seedance 1.5 Pro держит камеру | 1 ролик 4 с | `bytedance/seedance-1.5-pro`, 480p (T4 файла 01) | 5,25 | дрейф фона по оптическому потоку < 1 px/кадр | 3 |
| 6 | `IMG-CUTOUT` | Qwen 2.1 `background: "transparent"` даёт настоящую альфу | 1 картинка (T2) | `qwen/image-2.1`, 1K, png | 3 | альфа-канал, чистый край | 3 |
| 7 | `IMG-HERO-PHOTO` | NB Pro через `google-vertex/global/flex` = тот же результат дешевле | 1 картинка 1K | `google/gemini-3-pro-image-preview` + `provider.only` flex | ≈ 7,94 | `cost_rub` ≈ 7,9; время приемлемо | 2 |
| 8 | `IMG-HERO-PHOTO` | GPT Image 2.5 4K при 16:9 — реальные 4K пикселей | 1 картинка | `openai/gpt-image-2.5-sunburst`, 16:9, 4K | 11 | ширина ≥ 3800 px | 2 |
| 9 | `IMG-BG-ABSTRACT` | Seedream 4 в 4K за 3 ₽ — действительно 4K | 1 картинка | `bytedance/seedream-4`, 21:9, 4K | 3 | ширина ≥ 3800 px | 2 |
| 10 | `IMG-EDIT` | маски: Qwen 2.1 — белое меняется, GPT-5 Image — чёрное | по 1 правке с одной маской | `qwen/image-2.1` 1K; `openai/gpt-5-image` | 7,50 | изменения только в своей зоне (пиксельная разница) | 2 |
| 11 | — | Grok Image возвращает 1 или 2 файла | 1 запрос | `x-ai/grok-imagine-image`, 3:2 | 2,50 | число URL | 1 |
| 12 | `VID-ABSTRACT` | у Wan 3.0 1080p по цене 480p — реальные 1080p | 1 ролик 2 с | `alibaba/wan-3.0`, 1080p, `duration: "2"` | 47,20 | ffprobe 1920×1080 | 1 |

Сумма всех 12 — ≈ 177–184 ₽ (с T1–T8 файла 01 пересекаются № 1, 5, 6). Качество картинок и видео оценивают стенд E и
агенты C1/C2/I; здесь — только «принят ли параметр, сколько списано, что вернулось».

## Частые ошибки

1. **Параметры «по памяти»**: `seed` у Veo (нужно `seeds`), `negative_prompt` у Kling 3.0, `quality: "hd"` у GPT Image,
   `duration` у Veo, `output_format` у Nano Banana Pro — каталог их не знает.
2. **Параметры одного провайдера у другого**: маска GPT-5 Image у `openai`; 4K GPT-5.4 Image 2 у `openai`; 14
   референсов Nano Banana Pro у `mie` (там 8).
3. **Разрешение там, где его нет**: у Seedream 4.5/5 разрешение — `quality`; у Kling 3.0 — `mode`; у Nano Banana,
   NB2 Lite, Z-Image, Grok Image, Qwen Image/2, GPT-5 Image — не задаётся вовсе.
4. **`high` у Seedream «значит 4K»** — только у 4.5; у 5 Lite 3K, у 5 Pro 2K.
5. **Длительность и звук Seedance 2 по умолчанию** — 15 с и звук: 415 ₽ вместо 51.
6. **Kling 3.0 без `aspect_ratio`** — 1:1; со стартовым кадром — соотношение картинки.
7. **Veo как «10 секунд 1080p»** — длительность и разрешение не выставлены; 1080p/4K — только апскейлом (10/90 ₽).
8. **Wan 3.0 в 480p «ради экономии»** — цена та же, что у 1080p.
9. **Seedream 5 Pro с 10 референсами «бесплатно»** — +2,70 ₽ к каждой картинке.
10. **Одна маска на две модели** — у Qwen 2.1 и GPT-5 Image цвета противоположны.
11. **Негатив в модели без негатива** — в polza негатив есть только у Wan 2.5; в остальных — описывать в позитиве.
12. **Нативные булевы `true`/`false` в видео** — каталог и гайды шлют строки; не проверено, примет ли polza bool.
13. **Цена токенных провайдеров как фиксированная** — это оценка; фактическая — `usage.cost_rub`.
14. **Гайд важнее каталога** — гайды отстают (Kling 2.5 Turbo, Seedream 3.0 сняты; `output_format`, `n`, `multi_shots`
    в гайдах, но не в каталоге).
15. **Цена из старого снимка** — перед серией `snapshot` + `diff`; цены Kling 3.0 уже менялись (changelog 14.03.2026:
    std без звука 15 → 10 ₽/с, pro 20,25 → 12, Motion Control 720p 8 → 14 ₽/с).

## Чек-лист

- [ ] Модель и её параметры взяты из снимка каталога не старше недели (`polza.py show MODEL`)?
- [ ] Для выбранного провайдера проверены его параметры (`--provider`)?
- [ ] Все ценовые параметры из `price_params` модели заданы явно?
- [ ] Для видео: длительность задана, звук `"false"`, соотношение явно?
- [ ] Для Veo: `generationType`, `seeds`, `enableTranslation` осознанно?
- [ ] Разрешение задано правильным параметром (`image_resolution` / `resolution` / `quality` / `mode`)?
- [ ] Число референсов не больше лимита этой модели у этого провайдера?
- [ ] Маска подготовлена в соглашении этой модели?
- [ ] Оценка `polza.py estimate` совпадает с ожиданием по таблицам §6–§7?
- [ ] Для серии — выбрана самая дешёвая модель, решающая задачу (§7), и перебор идёт в 480p/1K?
- [ ] Расхождения гайда и каталога для этой модели (§9) учтены?

## Открытые вопросы и противоречия

1. Семантика ступеней: какую ступень polza применяет при неуказанном параметре (default или `[]`) — тест №1 §12.
2. Смысл `images` у Seedance 2 / Fast / Mini / 2.5 и Grok Video (кадры или референсы) — тест №2.
3. Реальные длительность, разрешение и звук Veo 3.1 через polza — тест №3.
4. Цена `extend` Veo с `model: "quality"` (45 ₽ в каталоге при 4-кратной разнице у KIE).
5. Округление секунд у цены за секунду (Motion Control, Topaz Video) и минимальная длительность входа.
6. Токены на картинку у `openai/gpt-5.4-image-2` (провайдер `openai`) и тир качества у `openai/gpt-5-image(-mini)` —
   не опубликованы.
7. `google/gemini-3.1-flash-image` (NB2 GA) без `parameters` — как вызывать (chat `modalities`?).
8. Topaz ×8: у KIE фактора 8 нет — отдаёт ли polza реально ×8.
9. Ценовые аномалии Seedance «с видео» (у KIE дешевле, у polza дороже — ×3,2 к KIE) и Gemini Omni (почти цена KIE) —
   ошибки тарифа или устаревшие ставки `[спорно]`.
10. Почему у Wan 3.0 (Alibaba) одна ставка на 480p–1080p, а у KIE ставки различаются в 4 раза.
11. `alibaba/wan-3.0`/HappyHorse: описание `images` «first/last frame» при `max: 1`.
12. Grok Image: 1 или 2 картинки за запрос (у KIE — «за 2 картинки»).
13. Скорость генерации моделей в polza (для маршрутизации): нет данных до фазы 5 (паспорта `polza.py` пишут время).

## Источники

- [S1] polza · `GET https://polza.ai/api/v1/models` — снимок `99-raw/cache/polza/2026-09-23/api-v1-models.json`
  (23.09.2026 08:20 МСК, 535 640 Б, sha256 `ced8639f…`): параметры с описаниями, `default`, `values`, цены, операции.
  Источник истины по моделям; описания местами противоречат `max_length`.
- [S2] polza · `GET …/v1/models?include_providers=true` — снимок `99-raw/cache/polza/2026-09-23_0921/api-v1-models.providers.json`
  (09:21, 2 085 225 Б): провайдеры каждой модели, их параметры и цены.
- [S3] polza · публичная OpenAPI `https://polza.ai/api/openapi.json` (1.0, 23.09.2026): `ClientTierPresenter`,
  `unitParam`, `ModelParameterConstraintPresenter` (`auto_value`), DTO медиа.
- [S4] polza · гайды медиа-моделей `docs-repo/gaidy/*.mdx` (28 шт., репозиторий `github.com/polza-ai/docs`,
  18.09.2026): примеры тел, типы значений, ограничения; отстают от каталога.
- [S5] KIE.ai · документация Kling 3.0 (`docs.kie.ai`, market `kling-3.0/video`, снято агентом P 23.09.2026):
  std = 1280×720, pro = 1920×1080, 4K = 3840×2160; `multi_prompt`, `kling_elements`.
- [S6] polza · `docs-repo/changelog.mdx` (до v1.5.3, 25.04.2026): изменения цен Kling 3.0 с 18.03.2026.
- [S7] KIE.ai · публичный прайс (`api.kie.ai/client/v1/model-pricing/page`, 23.09.2026) из опыта P
  `99-raw/experiments/P/02-kie-vs-polza/`; сопоставление ступеней — `99-raw/experiments/B/05-polza-vs-kie-fx/`.
- [S8] Банк России · курс USD на 23.09.2026 — 84,0657 ₽ (из опыта P).
- [S9] Google · Gemini API pricing (`ai.google.dev/gemini-api/docs/pricing`, 23.09.2026): токены на картинку NB2,
  NB2 Lite, NB Pro, Nano Banana; вход картинки 560 токенов.
- [S10] OpenAI · image generation guide (`developers.openai.com`, 23.09.2026): токены gpt-image-1 по качеству и размеру.
- [S11] KIE.ai · документация моделей (Veo 3.1, Seedance 2, Seedance 1.5 Pro, Kling 3.0, Qwen Image 2.1, GPT Image 2.5,
  MiniMax H3, Topaz), кэш `99-raw/cache/kie-2026-09-23/`, и заметки агента P `99-raw/notes/wave1/P-notes.md` §2 —
  параметры исполнителя, которых нет в polza.
- [S12] OpenRouter · `https://openrouter.ai/api/v1/models` (23.09.2026): цены GPT-5 Image/Mini, GPT-5.4 Image 2,
  Gemini Image = цены провайдеров polza ÷ 117,992.
- [S13] Опыты агента B: `99-raw/experiments/B/02-price-calculator` (формулы, 84 случая), `04-job-validation`
  (51 ловушка), `05-polza-vs-kie-fx`, `07-model-cards` (карточки, минимальные вызовы, таблицы).
