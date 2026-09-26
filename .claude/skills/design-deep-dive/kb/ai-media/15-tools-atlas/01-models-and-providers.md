# Атлас: модели, каналы доступа, сервисы — что есть, почём, живо ли, доступно ли из РФ

Волна 3 · агент N · 24.09.2026 · снимки каталогов: polza `2026-09-24` 04:10 (46 медиа-моделей: 24 картинки, 22 видео),
RouterAI `2026-09-24_0424` (522 модели), Gen-API `2026-09-24_0424` (318 сетей) · полная таблица polza —
`99-raw/experiments/N/04-update-dryrun/polza_table_2026-09-24.md` · маршруты — `../13-routing-matrix/routing.yaml` v1 ·
новые источники — 10 официальных страниц сервисов (кэш `99-raw/cache/`, 24.09.2026), остальное — файлы базы.

## Выжимка для агента

1. **Доступ к моделям — три рублёвых канала**: polza (Media API + chat + `/v2/images`, один баланс — 2 000 ₽ фазы 5), RouterAI
   (Recraft-вектор, GPT Image с `quality`/`background`, клон API OpenRouter), Gen-API (Ideogram, удаление фона, слои, FLUX.2
   без переписчика, Bria FIBO); остальное — иностранная оплата. → §1 [документация] [поправка фазы 5, 25.09.2026: фаза 5 — polza 1 343,57 ₽ (205 генераций +
   190 чат-вызовов), RouterAI 212,68 ₽ (26), Gen-API 384 ₽ (30); у Gen-API цена ступенями — `cost` каталога минимум (Hunyuan3D 96 против
   32, TRELLIS.2 1024 — 75, Tripo Standard — 75, Hunyuan Image V3 — 45 против 22,5); у RouterAI новое в маршрутах — Qwen Image 3 (2K за
   3,31 ₽), Krea 2 (3,31), GPT Image 2.5 `medium` 0,93; FLUX.2 max — 11,04 ₽ при оценке 7,73 (+43 %, остановлен); видео — Seedance 1.5 Pro
   1080p 22,5 ₽ за 4 с / 45 за 8 с, Kling 3 pro 12 ₽/с (1920×1080) → `../13-routing-matrix/routing.yaml` v2]
2. **polza дешевле на большинстве моделей**, второй канал нужен ради возможностей, а не цены (исключения: Wan 3.0, H3 Max
   плоским тарифом; Seedream 4.5/5 Lite и GPT Image medium — у RouterAI). → §1 [документация: P/05]
3. **Исполнитель почти всех медиа-моделей polza — `mie` = KIE**; у NB-семейства есть Google-провайдеры (flex −41 % у NB Pro
   после T5), у H3 Max и Wan 3.0 Prime — `openrouter`, у Wan 3.0 и HappyHorse — Alibaba. → §1 [документация]
4. **Цены каналов плавают с курсом ежедневно**: RouterAI +0,39 % и polza-долларовые +0,2 % за 23→24.09 — цену брать из снимка
   дня, не из памяти. → §1 [проверено: N/04]
5. **Модели картинок — 18 рабочих id в polza**; 6 — устаревшие или нишевые (`openai/gpt-5-image` выкл. 23.10.2026,
   `openai/gpt-image-1.5` и `-mini` — 01.12.2026, `google/gemini-2.5-flash-image`, `qwen/image`, `qwen/image-2`,
   `x-ai/grok-imagine-image` — база, не 2.0; `flux.2-flex` — дубль pro ×2,8). → §2 [документация]
6. **Новые за сутки**: GA `google/gemini-omni-1.1-flash` (FLF полями, 48 ₽), `grok-imagine-image-2-0/text-to-image` (3 ₽),
   RouterAI `recraft/recraft-v4.1-flash` (0,77 ₽), `inclusionai/ming-image-0.1-design-layer` (слои, без цены). → §2–3
   [документация, 24.09]
7. **Видео через polza — 22 id**, для сайта важны 7: Seedance 1.5 Pro (петля, `fixed_lens`), Kling 3 (FLF, облёт), GA Omni
   1.1 (FLF 1080p, V2V), Veo 3.1 Fast (FLF 8 с, референсы), H3 Max (FLF), Grok 1.5 (перебор), Seedance 2 Mini (абстракция). → §3
8. **Снято и снимается**: API Sora 2 — 24.09.2026, preview `gemini-omni-video` — 30.09.2026, remove.bg — 01.12.2026; OpenRouter
   закрыт для РФ с 27.06.2026; Midjourney — без API и с запретом автоматизации. → §2–4 [документация]
9. **Вектор — только вне Media API polza**: Recraft V4.1 Vector (RouterAI 8,78 ₽, Gen-API 20 ₽), Quiver Arrow 2 (прямой API,
   $4 / $20 за 1 М токенов, иностранная оплата), LLM → SVG через polza-chat. → §2, §4 [документация]
10. **Из 13 сервисов роликов в конвейер годятся по API**: Quiver (SVG), Higgsfield (агрегатор 50+ моделей), Flora (API на
    платных тарифах), Bria (лицензированные данные, от $0,018), Topaz (Hyperion 2.5 SDR → HDR), Beeble SwitchX (бета) — все
    за иностранную оплату; Figma Weave, Google Pics, LottieFiles Prompt to Vector, HeroUI Studio, Lovart — только интерфейс;
    Kompa — UI-кит Framer, не генератор. → §4 [документация: страницы вендоров 24.09]
11. **Открытые веса ≠ коммерция**: Qwen Image 2.1 — research; FLUX.2 [dev]/[klein], RMBG-1.4/2.0, Depth Anything Base/Large,
    Ideogram 4 — NC; u2netp, BiRefNet, Depth Anything Small, Qwen-Image-Layered — да. → §5 [документация: L 12/01 §4]
12. **Строка атласа — не маршрут**: модель без теста и без уникальной возможности остаётся в атласе, в `routing.yaml` — только
    через `../13-routing-matrix/04-update-procedure.md` §4. → §6 [практика]

## 1. Каналы доступа

| Канал | Что даёт сверх остальных | Оплата и доступ из РФ | Ключ на 24.09 | Клиент в базе | Главные оговорки | Файл базы |
|---|---|---|---|---|---|---|
| **polza** — Media API | 46 медиа-моделей (KIE и Google/Alibaba/OpenRouter-провайдеры), асинхронно, хранилище 24 ч для входов | рубли, РФ | нет (заказчик заведёт к фазе 5) | `polza.py` (макет 30/30) | ценовые параметры — явно; `quality` у GPT 2.5 нет; `images` у Seedance 2.x — референсы; медиа хранится 7 дней | `02-providers-platforms/01`, `02` |
| polza — chat | LLM/VLM (Claude, GPT, Gemini, Qwen, DeepSeek) для SVG и судьи | тот же баланс | тот же | `mp_client.py` (`polza-chat`) | рассуждения — входят ли в `max_tokens` (B2-03) | `07-multichannel-client.md` |
| polza — `/v2/images/generations` | синхронная картинка по `size`; возможно `background` у GPT 2.5 (не документировано) | тот же баланс | тот же | `mp_client.py` (`polza-images`) | ступень цены по `size` не описана — верх 11 ₽ | `07` §3 |
| **RouterAI** (ООО «Интер») | Recraft V4/V4.1 (вектор, Utility, Styles, Flash), GPT Image 2.5/2 с `quality`, `background`, маской; FLUX.2 pro с `seed`; Seedream 4.5 | рубли, РФ; цены ≈ ×1,30 к ЦБ | нет | `mp_client.py` (`routerai`, макет 44/44) | passthrough `controls`/`disable_pup` не документирован (B2-01/02); видео ×1,4–5,4 к polza — не брать | `03-aggregators…` §2.3, `07` |
| **Gen-API** (ООО «ИНФИМУМ») | Ideogram (текст, альфа), удаление фона (Ideogram 2,5 ₽, Pixelcut 4 ₽), Qwen-Image-Layered 12,5 ₽, FLUX.2 [dev] без переписчика, Bria FIBO, Recraft V4 vector 20 ₽, Image2svg 1 ₽ | рубли, РФ; наценка ≈ ×3 к курсу | нет | `mp_client.py` (`genapi`) | `translate_input` по умолчанию `true` — выключать; результаты хранятся 24 ч; Midjourney там — нарушение ToS MJ | `03` §2.2, `06-gap-map` |
| AITUNNEL, ProxyAPI | тот же каталог OpenRouter (без Recraft-вектора у AITUNNEL) | рубли | — | нет | запасной вход, наценка ×2 | `03` §2.3 |
| VseGPT, BotHub, GPTunnel | — | рубли | — | нет | каталог медиа отстаёт / цены только по ключу | `03` §2.1 |
| KIE (исполнитель `mie`) | те же модели с параметрами, которых нет в polza (GPT `background`, Veo `duration`, Kling multi-shot) | карта, PayPal; вне РФ | не заводится | нет | не резервирует polza (тот же поставщик); политика данных пуста | `03` §3.1 |
| fal.ai | Luma Ray 3.2 `loop`, Z-Image tiling, Recraft, Ideogram, SeedVR2, BiRefNet video, OmniLottie | карта вне РФ; санкционные оговорки AUP | не заводится | нет | медиа публичны по умолчанию | `03` §3.2 |
| Replicate (Cloudflare) | Wan 3 вдвое дешевле fal, Luma Ray 3.2, Recraft SVG | карта вне РФ; эмбарго | не заводится | нет | — | `03` §3.3 |
| Runware | Luma `loop`, GPT 2.5 прозрачность, Recraft SVG, видео с альфой (Bria) | карта вне РФ | не заводится | нет | — | `06-gap-map` §2 |
| OpenRouter | эталон цен и passthrough | **закрыт для РФ с 27.06.2026** | — | — | — | `03` §3.4 |
| Runway Dev API | Aleph 2 (правка видео), Gen-4.5 HDR/ProRes/EXR, Veo без звука, Magnific | карта · VPN · эмбарго; обучение на входах | — | нет | кредит $0,01 | `04` §8.1 |
| Recraft напрямую | `/v1/styles`, `controls.colors`, vectorize, removeBackground (SVG → SVG), crisp/creative upscale | карта вне РФ; API units | не заводится | нет | хранение 24 ч | `04`, `06-gap-map` §2 |

## 2. Модели картинок

Цена — ₽ за картинку в polza (`mie`), 24.09.2026; «маршрут» — роль в `routing.yaml` v1; класс — главное доказательство.

| id (канал) | Семейство · диалект | Ступени и цена | Возможности | Сильное / слабое (класс) | Маршрут v1 | Живость |
|---|---|---|---|---|---|---|
| `openai/gpt-image-2.5-sunburst` | gpt-image · sections | 1K 4 / 2K 7 / 4K 11 | ≤ 16 реф., 13 соотношений (21:9, 27:16); без `quality` и `background` | №1 AA/LMArena/Rapidata; люди, товар-сцена, UI; «тёплый фильтр» (A) | primary: hero, товар, иконки 3D, правка-инструкция | активна |
| `gpt-image-2-5-flare` → с 25.09 `openai/gpt-image-2.5-flare` | gpt-image · sections | 1K 4 / 2K 7 / 4K 11 | как Sunburst; прежний id без `openai/` в снимке `2026-09-25_1411` отсутствует | AA Animation #1, Rapidata Photo #1; UI/UX #12 (A); фаза 5: E-08 «хорошо», E-12 — держит стиль серии | primary: иллюстрация, серия, абстракция | активна (новый id) |
| `openai/gpt-5.4-image-2` (GPT Image 2; `mie`, `openai`) | gpt-image · sections | 1K 4 / 2K 7 / 4K 11 | ≤ 16 реф. | Typography №1, Logo №1 (Design Arena), AA TR №1; схемы FEPBench №1 (A) | primary: декоративный текст латиницей, схемы | активна |
| `google/gemini-3.1-flash-image-preview` (NB2) | nano-banana · sections | 1K 4,8 / 2K 7,2 / 4K 10,8 | ≤ 14 реф., 21:9, `output_format` | «сохранить остальное» при правке, аутпейнт; Preference №1, Alignment #7, лишний текст (A/B) | primary: правка, аутпейнт; fallback: hero, иллюстрация | активна |
| `google/gemini-3-pro-image-preview` (NB Pro; `mie` + 6 Google-провайдеров) | nano-banana · sections | 1K = 2K 13,5 / 4K 18; flex ≈ 7,95 | ≤ 8 реф., `output_format` (с 24.09) | серии (ViStoryBench, OmniRef №1); иллюстрация #24; прозрачности нет (B) | fallback: серия | активна |
| `google/gemini-3.1-flash-lite-image` (NB2 Lite) | nano-banana · sections | 2,9 | ≤ 10 реф., **8:1, 4:1, 1:8** | AA #13; Design Arena #18; Abstract #39 (B) | primary: черновик; лента 8:1 | активна |
| `google/gemini-3.1-flash-image` | — | токены, ≈ 7,95 | параметры в каталоге не описаны | — | — | только Google-провайдеры |
| `bytedance/seedream-4` | seedream · prose | 3 (1K–4K одна цена) | ≤ 10 реф., `seed`, 21:9 | 4K по цене 1K; видимый знак вендора — до E-01 (B) | cheap: hero, фон, текстура | активна |
| `bytedance/seedream-4.5` | seedream · prose | basic 5 (2K) | ≤ 14 реф. | дословность латиницы (три линии); смешение лиц 53,7 % (B+) | fallback: латиница; cheap: серия, товар | активна |
| `bytedance/seedream-5-lite` | seedream · prose | basic 4 (2K) | ≤ 10 реф. | схемы AIBench #2; Text Coherence #4 (B) | — (кандидат схем) | активна |
| `seedream/5-pro-text-to-image` | seedream · prose | basic 5 / high 10 (+0,3 за реф.) | ≤ 10 реф. | LMArena #9 против Rapidata #33 — спор (B) | `not` до E-08/E-10 | активна |
| `qwen/image-2.1` | qwen-image · prose | 1K 3 / 2K 6 | ≤ 10 реф., `seed`, `mask_url`, **`background: transparent`**, `enhance_prompt` | единственная альфа и маска в Media API; **лицензия research** (L) | только `final: false` (черновик) | активна; веса 20.09.2026 |
| `black-forest-labs/flux.2-pro` | flux2 · prose | 1K 5 / 2K 7 | ≤ 8 реф.; переписчик не выключается | hex ≈ как у GPT; compliance 27 % (B) | alt: абстракция (E-13) | активна |
| `tongyi-mai/z-image` | z-image · prose | 1,4 | без референсов, ≤ 1000 символов | композиция без текста и цвета; однообразие (B) | cheap: черновик | активна |
| `grok-imagine-image-2-0/text-to-image` | grok-image · prose | 3 | ≤ 5 картинок правки; 1:1, 2:3, 3:2, 16:9, 9:16 | Rapidata Grok 2.0 Medium #5 общий — какая версия в polza, неизвестно | alt `final: false` → мини-стенд (33 ₽) | **новая 23.09** |
| `topaz/image-upscale` | — | ×2 7,5 / ×4 15 (до 30) | `upscale_factor`; модель Topaz не указана | — | alt после H-05 | активна |
| `openai/gpt-5-image` (= gpt-image-1) | gpt-image | 4,5 | маска (чёрное = менять), `isEnhance` | — | — | **выкл. 23.10.2026** |
| `openai/gpt-image-1.5`, `openai/gpt-5-image-mini` | gpt-image | medium 3 / high 16,5; токены ≈ 1 | — | — | — | **выкл. 01.12.2026** |
| `google/gemini-2.5-flash-image`, `qwen/image`, `qwen/image-2`, `x-ai/grok-imagine-image`, `black-forest-labs/flux.2-flex` | — | 2,25–24 | — | устаревшие / дубли | — | не брать |
| **вне polza**: RouterAI `recraft/recraft-v4.1-vector` / `-pro-vector` / `-utility` / `recraft-v4-styles(-vector)` / `recraft-v4.1-flash` | recraft-v4 · prose | 8,78 / 32,91 / 3,84 / 3,84 (5,49 вектор) / 0,77 | SVG (только заливки), стиль по референсам, `controls` — гипотеза | Rapidata SVG #28–31, icons #37–39 (A) | primary: цветной вектор; Flash — черновик | Flash — **новая 24.09** |
| RouterAI `openai/gpt-image-2.5-sunburst`/`-flare`, `openai/gpt-image-2` | gpt-image | medium 1024² ≈ 1,45; GPT 2 с маской ≈ 6,47 | `quality`, `background: transparent`, маска | — | alpha: вырез; mask: правка | активны |
| Gen-API `ideogram-*`, `bria-fibo`, `flux-2` ([dev]) | ideogram4 / bria-fibo / flux2 | 7,5–22,5 / 10 / 3 за Мп | Ideogram — текст, альфа; FIBO — JSON-нативная; FLUX.2 [dev] без переписчика | Ideogram 4: формула — провал, Alignment #36 (B) | D2-02 (A/B формы); Ideogram — после кириллицы в polza | активны |
| Midjourney V8.2 | midjourney | — | — | эстетика; **нет API, запрет автоматизации** | `no-automation` | не в конвейер |
| MAI-Image 2.6, Muse Image, Reve 2.1, Qwen-Image 3.0 Pro, Grok 2.0 Auto, Imagen 4 (выкл.) | — | нет в каналах РФ | — | Rapidata/Design Arena топ-10 (MAI, Reve, Muse) | — | вне доступа |

## 3. Модели видео

Цена — ₽ за ролик без звука в polza, 24.09.2026.

| id (провайдер) | Кадры | Камера | Звук по умолч. | Длительность / разрешение | Цена | Роль v1 | Живость |
|---|---|---|---|---|---|---|---|
| `bytedance/seedance-1.5-pro` (`mie`) | `images` 0–2 (FLF вероятен) | **`fixed_lens`** | выкл. | 4/8/12 с; 480p–1080p | 480p 4 с 5,25; 720p 10,5; 1080p 22,5 | primary: петля, синемаграф, альфа, переход | снята у BytePlus, живёт в polza через KIE |
| `kling/v3` (`mie`) | 0–2 start/end (single-shot) | проза | выкл. (`sound`) | 3–15 с; std 720p / pro 1080p / 4K | std 10 ₽/с (5 с — 50); pro 12 ₽/с | premium петли; облёт товара; камера | активна |
| `google/gemini-omni-1.1-flash` (`mie`) | **`first_frame_url` + `last_frame_url`** (только вместе) или ≤ 7 `images` | проза | всегда | 4/6/8/10 с; 360p = 720p = 1080p по цене | 4 с 48; V2V 126; 4k 111+ | premium петли 1080p, V2V, апскейл нативом | **GA 27.08, в polza 23.09** |
| `gemini-omni-video` (preview) | теги в промте | проза | всегда | 4–10 с | 4 с 35; V2V 70 | alt V2V до 30.09 | **снимается 30.09.2026** |
| `google/veo3_fast` (`mie`) | FLF или 0–3 референса (`REFERENCE_2_VIDEO`) | проза | всегда | 8 с 720p (не задаются) | 45; `extend` 45, `upscale_1080p` 10 | fallback петли; товар по референсам | активна |
| `google/veo3` | FLF | проза | всегда | 8 с 720p | 187,5 | — | активна |
| `minimax/hailuo-3-max` (`openrouter`) | ≤ 2 first/last | «[static]» | — | 5–15 с; 480p/768p (умолч. 21:9) | 9,46 ₽/с (480p 5 с — 47,30) | было: fallback петли | 25.09 — 2 × 503 «нет провайдеров», выбыла (`defaults.unavailable_2026_09_25`) |
| `grok-imagine-video-1-5` (`mie`) | `images` 0–7 | нет | есть (не выключается) | 1–15 с (умолч. 8); 480p/720p | 1,62 ₽/с (5 с — 8,10) | перебор движения, альфа-черновик | активна |
| `bytedance/seedance-2-mini` (`mie`) | `images` 0–9 — **референсы** | нет | **вкл.** | 4–15 с (умолч. 15); 480p/720p | 2,565 ₽/с (5 с — 12,83) | абстракция | активна |
| `bytedance/seedance-2`, `-2-fast`, `-2-5` (`mie`) | референсы (2.5 — до 30 картинок, 10 видео) | нет | вкл. | до 15 / 30 с | 2: 12,8–83,7 ₽/с (без `duration` — 415 ₽); 2.5 480p 18,9 ₽/с | длинный ролик (2.5) | активны |
| `alibaba/wan-3.0` (Alibaba), `-prime` (`openrouter`) | ≤ 1 | нет | `generate_audio` | 2–30 с | 23,65 / 33,11 ₽/с плоско (25.09 — 23,76) | `not` для петли | 25.09 — Wan 3.0: 503 «нет провайдеров», выбыла |
| `alibaba/happyhorse-1.0/1.1` | ≤ 1 | нет | нет параметра | 3–15 с | 20,03 / 15,11 ₽/с | — | активны |
| `kling/v3-motion-control`, `kling/v2.6(-motion-control)`, `wan/2.5`, `wan/2.6` | — | — | — | — | 14 ₽/с; 42–165; 45–236 | персонаж (motion control) | активны |
| `topaz/video-upscale` | `videos` 1 | — | — | ×2 / ×4 | 6 / 10,5 ₽/с | апскейл готового | 25.09 — 2 × `INTERNAL_ERROR`, выбыла; 1080p — нативно |
| **вне polza**: Luma Ray 3.2 `loop` (fal/Replicate/Runware) | — | — | — | 5 с 540p/720p | ≈ 12,6 / 25,2 ₽ по курсу | единственная нативная петля | иностранная оплата |
| Runway Aleph 2 / Gen-4.5; Veo 3.1 Lite (AITUNNEL 25,5 ₽ 5 с); Kling 3.0 Omni | — | — | — | — | — | правка видео, HDR/EXR; Omni-элементы | Kling 3 Omni в каналах РФ нет |
| Sora 2 | — | — | — | — | — | — | **API снят 24.09.2026** |

## 4. Сервисы и инструменты из роликов (V §4), проверено 24.09.2026

| Сервис | Что делает | API | Доступ из РФ | Живость (дата) | Решение для базы |
|---|---|---|---|---|---|
| **QuiverAI Arrow 2 / Telos** | генерация и векторизация SVG; Rapidata SVG №1–2 (1485) | да: предоплата, Arrow 2 $4 / $20 за 1 М токенов (вход/выход), Telos $6 / $30; Arrow 1.1 $0,20 за SVG, векторизация $0,15; мин. пополнение $10, кредиты сгорают через год | иностранная оплата | активен, 09.2026 | кандидат в ключ 2-й очереди для `VEC-ICON-*` при иностранной оплате; сейчас — LLM → SVG |
| **Higgsfield** | агрегатор 50+ моделей (Seedance, Kling, Wan, MiniMax, Recraft, Ideogram, свои Soul) + MCP | да, отдельный API-баланс; Seedance 2.5 $0,144/с (со скидкой) | иностранная оплата [не проверено] | активен; Series B 08.2026 (по сниппету) | не нужен: те же модели дешевле в polza |
| **Flora** | холст-граф 50+ моделей, «техники», ассистент FAUNA | да, API и MCP на тарифах от $18/место/мес | иностранная оплата | активен | не для конвейера (оркестрацию делаем сами) |
| **Figma Weave** (бывш. Weavy, куплен Figma 10.2025) | нодовый холст, Weave tools внутри Figma (Config 2026) | публичного API нет — по данным конкурента [мнение]; FAQ Figma об API молчит | иностранная оплата | активен | как образец графа ассетов, не канал |
| **Magnific** (бывш. Freepik API) | генеративный апскейл 2–16× (`creativity`, `resemblance`, `engine`) | да (`api.magnific.com`), кредиты; через Runway $0,25 | иностранная оплата | активен | доводка hero — после H-05 и только декор |
| **Topaz** (Hyperion 2.5) | SDR → HDR видео (ProRes 10 бит BT.2020 PQ / EXR 16 бит), `model: "hyp-2.5"`; апскейл | да, `api.topazlabs.com`, кредит $0,08–0,12; 1080p — 13 кадров/кредит | иностранная оплата; Topaz ×2/×4 — в polza | активен | HDR сайту не нужен; апскейл — `topaz/*` в polza |
| **Beeble SwitchX** | переосвещение и замена фона видео по референсу | бета REST (≤ 240 кадров, 720p/1080p) [по сниппету] | иностранная оплата | активен (04.2026) | вне задач сайта; кандидат для `VID-V2V` при заказах |
| **Bria** | генерация и правка на лицензированных данных, удаление фона, FIBO (JSON) | да: API/MCP/SDK, от $0,018; FIBO в Gen-API 10 ₽ | Gen-API — рубли (FIBO); остальное — иностранная | активен | FIBO — контроль JSON-формы (D2); RMBG-2.0 веса — NC |
| **LottieFiles Prompt to Vector** | промт → слоистый SVG → анимация dotLottie в Lottie Creator и Figma | в документации не описан (только интерфейс) | — | активен (док. 11.09.2026) | `VEC-ANIM` — кодом; LottieFiles — ручной инструмент |
| **HeroUI Studio** | нодовый редактор: SVG → анимированный SVG (Gemini 3.1 Pro), морфинг | нет (early access, 02.2026) | — | ранний доступ | приём «SVG + Gemini» повторяем LLM-ом в сессии |
| **Google Pics** | правка по объектам, перевод текста на картинке, апскейл 2K/4K; на Nano Banana | нет (приложение Workspace) | аккаунт Google | GA 01.09.2026 | ручной инструмент заказчика; в конвейере — NB2 через polza |
| **Lovart** | «AI design agent» (Nano Banana Pro внутри), кредиты | публичной цены API нет [не проверено] | — | активен | не нужен |
| **Kompa** | UI-кит Framer (850+ компонентов), разовая покупка | — | — | активен | не генератор; вне базы |

## 5. Открытые веса и локальные модели (решения L и H)

| Веса | Лицензия | Для сайтов клиента | Где в базе |
|---|---|---|---|
| u2netp | Apache 2.0 | да (вырез по умолчанию) | H `08/01`, `99-raw/tools/models/rembg/` |
| isnet-general-use | код Apache 2.0, веса без лицензии, DIS5K NC | черновики (`nc-weights-disputed`) | там же |
| RMBG-2.0 (по умолчанию в rembg 2.0.85), RMBG-1.4 | CC BY-NC / NC Bria | **нет** — модель задавать явно | L `12/01` §4 |
| BiRefNet | MIT | да (6,5 ГБ ОЗУ на CPU — хостинг) | H, P/10 |
| Depth Anything V2 Small / Base-Large | Apache 2.0 / CC BY-NC | Small — да; Base/Large — нет | H/06 |
| Qwen-Image 20B, -Edit-2509/2511, -2512, **-Layered** | Apache 2.0 | да | L §4 |
| **Qwen-Image-2.1** | Qwen Research License (20.09.2026) | **нет** (только черновики через `mie`) | L §5 |
| FLUX.2 [dev], [klein] 9B; Ideogram 4 | NC | нет self-host | P `05` §9 |
| OmniSVG, OmniLottie | заявлено Apache 2.0, база Qwen2.5-VL-3B research | нет до ясности | L §4 |
| Wan 2.1/2.2 | Apache 2.0 | да (локально не тянем — CUDA нет) | P `05` |
| PP-OCRv5 eslav rec, PP-OCRv6 det (RapidOCR 3.9.2) | Apache-2.0 | да (OCR кириллицы) | K `11/01` §4 |

Полная таблица 43 строк — `../02-providers-platforms/05-open-weights-landscape.md` §9.

## 6. Слот → коды задач (строки атласа)

Карта «слот страницы → коды → уместность ИИ → бюджет» — `../13-routing-matrix/03-routing-matrix.md` §6 (по A `01` §2.1
и L `04` §2); маршрут каждого кода — там же §2–§4 и `routing.yaml`.

## Частые ошибки

1. **Канал по имени модели**: «GPT Image 2.5 есть везде» — но `quality`/`background` есть у RouterAI и нет в Media API polza.
2. **Цена из прошлого снимка**: у RouterAI и долларовых провайдеров — ежедневный сдвиг.
3. **Агрегатор ради тех же моделей** (Higgsfield, Flora): дороже polza и без выигрыша возможностей.
4. **Лицензия по семейству**: Qwen-Image (Apache) ≠ Qwen-Image-2.1 (research); бейдж «commercial» у хостинга — не лицензия весов.
5. **Сервис из ролика как канал**: у Figma Weave, Google Pics, LottieFiles Prompt to Vector, HeroUI Studio нет API для конвейера.
6. **Sora 2, preview Omni, remove.bg в маршруте** — сняты или снимаются.

## Чек-лист

- Модель есть в снимке каталога дня, провайдер и параметры — из `polza.py show` / `mp_client.py show`?
- Канал выбран ради возможности, а не цены (или цена ниже ≥ 30 % при том же классе)?
- Лицензия весов и условия канала записаны (флаги `legal`)?
- Дата снятия модели > дата работы + 7 дней?
- Для сервиса вне каналов РФ — есть ли у заказчика законная иностранная оплата?

## Открытые вопросы и противоречия

1. Какую версию Grok Image 2.0 (Medium / Auto) отдаёт `mie` — мини-стенд.
2. Recraft V4.1 Flash — только описание вендора; качество и стиль — не проверены.
3. Цена `inclusionai/ming-image-0.1-design-layer` в каталоге RouterAI пустая.
4. Figma Weave API — «coming soon» по данным конкурента; официального подтверждения нет.
5. Higgsfield, Lovart, Beeble — доступ из РФ и способы оплаты не проверялись (страницы тарифов не читались целиком).

## Источники

- [S1] polza.ai. `GET /api/v1/models`, `?include_providers=true`, `/models/catalog` — снимок 24.09.2026 04:10
  (`99-raw/cache/polza/2026-09-24/`) [документация].
- [S2] RouterAI `GET /api/v1/models`, Gen-API `GET /api/v1/networks?include=parameters` — снимки 24.09.2026 04:24 [документация].
- [S3] `../02-providers-platforms/01–07` (B, P, B2), `06-gap-map.md`, опыты `99-raw/experiments/P/01–12`.
- [S4] `../03-image-models/02-model-cards.md`, `models/*.yaml` (C1); `../04-video-models/02`, `models/*.yaml` (C2); `../09-video-pipeline/04` §1 (I).
- [S5] `../12-legal-provenance/01` §2–§5 (L).
- [S6] QuiverAI. Pricing — docs.quiver.ai/api/pricing (кэш `docs.quiver.ai_api_pricing_e9764072.md`, 24.09.2026) [документация].
- [S7] Figma Weave FAQ — help.weavy.ai (кэш `help.weavy.ai_en_articles_12692387-figma-weave-faq_396a2702.md`) [документация].
- [S8] Higgsfield API — higgsfield.ai/higgsfield-api (кэш `higgsfield.ai_higgsfield-api_1415c606.md`) [документация].
- [S9] Topaz Labs. Hyperion 2.5 (SDR to HDR) — developer.topazlabs.com (кэш `developer.topazlabs.com_…hyperion-2.5…md`) [документация].
- [S10] LottieFiles. Prompt to Vector — docs.lottiefiles.com (обновлено 11.09.2026) [документация].
- [S11] Google Workspace Updates. Google Pics GA — 01.09.2026 [документация].
- [S12] FLORA pricing — flora.ai/pricing; Bria pricing — bria.ai/pricing; Beeble SwitchX — beeble.ai/research/switchx
  (кэш 24.09.2026) [документация]; HeroUI Studio, Lovart, Kompa — только результаты поиска [мнение].
- [S13] Отчёт V `99-raw/reports/wave1-V-report.md` §4 (список инструментов из роликов); дайджесты `I9xdmNZxIfA` (Weave),
  `2RD3FP5iWJY` (Flora, Higgsfield), `_Bc4g6fFMp0` (Lovart), транскрипт `N38wvyexMQg` (Quiver).
