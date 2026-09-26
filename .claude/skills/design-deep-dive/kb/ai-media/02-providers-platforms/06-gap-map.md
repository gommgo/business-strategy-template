# Карта разрывов polza: что взять вне polza, где, почём и какие ключи заводить

Волна 1 · агент P · 2026-09-23 · основание: файлы `03-aggregators-and-platforms.md`, `04-direct-apis-and-services.md`,
`05-open-weights-landscape.md`, опыты `99-raw/experiments/P/01…12` · снимок каталога polza 2026-09-23 · курс ЦБ 84,0657 ₽/$.

Файл — итог волны 1 по вопросу заказчика «любые провайдеры, если доказуемо решают задачу». Коды задач — из таксономии
`99-raw/prompts/_common.md`. Цены — за единицу, по публичным прайсам на 23.09.2026; все генеративные утверждения о
качестве — `[не проверено]` до фазы 5.

## Выжимка для агента

1. **Recraft — номер один по пользе, но ключ к нему — российская витрина, а не Recraft напрямую**: вектор V4/V4.1 у RouterAI
   8,74 ₽ (passthrough `style`, `controls`, `text_layout`; V4 Styles vector 5,46 ₽ с `style_id`), у Gen-API 20 ₽ (без
   `style_id`); прямой ключ Recraft нужен, только если витрина режет стили/палитру или нужны `/v1/styles`, `vectorize`,
   `removeBackground` для SVG → §2, §3 [вывод P; passthrough — не проверено].
2. **Recraft не решает линейные UI-иконки**: его SVG — залитые контуры без `stroke`, с фоном-прямоугольником → для
   VEC-ICON-LINE — LLM-SVG через текстовые модели polza (агент G) → §1 [проверено: P/07, 8 образцов].
3. **Прозрачный фон GPT Image 2.5 в polza по каталогу недоступен**; первым тестом фазы 5 проверить `background:
   transparent` в `/v2/images/generations` polza (4 ₽), при неудаче — RouterAI/AITUNNEL (1,4–9 ₽) → §1, §4 [не проверено].
4. **Бесшовная текстура и нативная петля видео — только за рубежом**: fal `z-image/turbo/tiling` ($0,02/Мп) и Luma Ray 3.2
   `loop` (fal/Replicate/Runware, $0,15–0,30 за 5 с; черновик 360p напрямую у Luma $0,06); в рублях аналога нет → постобработка (H, I) или иностранная оплата → §1 [документация;
   шов тайла проверен на 1 образце, P/06].
5. **Разложение на слои (цепочка 6)**: Qwen Image Layered (Gen-API 12,5 ₽; fal $0,05), Seedream 5 Pro Layer Decomposition (KIE
   $0,035; fal $0,034 за слой) — в polza нет → Gen-API для теста в рублях → §1 [документация].
6. **Ideogram (типографика, стиль-коды, прозрачность)** — в рублях только Gen-API (7,5/15/22,5 ₽) и VseGPT (7,9 ₽); тест —
   после кириллицы в polza (C1), не раньше → §1 [документация].
7. **Удаление фона в polza отсутствует**: в рублях — Gen-API (Ideogram 2,5 ₽, Pixelcut 4 ₽), за рубежом — KIE Recraft $0,005,
   fal Bria $0,018, Photoroom $0,02; локально — rembg `u2netp`/`isnet-general-use` (0,1–0,6 с на CPU; модель задавать явно — по умолчанию некоммерческая RMBG-2.0), BiRefNet-lite ONNX — 6,5 ГБ ОЗУ (агент H, файл 05 §10) → §1 [документация; локально — проверено P/10].
8. **Ради цены второй провайдер не нужен**: polza дешевле всех российских каналов на видео KIE-линейки и на большинстве
   картинок; исключения — Wan 3.0/H3 Max (плоский тариф), Seedream 4.5/5 Lite и GPT Image `medium` (RouterAI) → §4
   [вывод P по прайсам].
9. **Зарубежные ключи (fal, KIE, Recraft, Replicate) — только если у заказчика есть законный способ зарубежной оплаты**:
   условия fal/Replicate/BFL содержат санкционные оговорки; OpenRouter для РФ закрыт с 27.06.2026 → §3, §5 [документация].
10. **Midjourney не заводить**: официального API нет; неофициальные прокладки нарушают условия MJ → §5 [документация C1].

## 1. Карта разрывов: задача → чего нет в polza → варианты → доступ → цена → проверка → рекомендация

| Код | Разрыв в polza (23.09.2026) | Лучшие варианты вне polza | Доступ из РФ | Цена за единицу | Проверка в фазе 5 | Рекомендация |
|---|---|---|---|---|---|---|
| VEC-ILLUSTR | нет генератора настоящего SVG | Recraft V4.1 Vector / Pro Vector; V4 Styles Vector | RouterAI, Gen-API, ProxyAPI — рубли; fal, Replicate, Recraft — иностр. оплата | RouterAI 8,74 ₽ (Pro 32,8); Gen-API 20 (Pro 75); $0,08 / $0,30 | 1 иллюстрация + 1 серия из 3 с `style_id` через RouterAI | **ключ RouterAI**; запас Gen-API |
| VEC-ICON-FILLED | то же | Recraft V4.1 Vector; V4 Styles Vector (`style_id`) | как выше | 5,46–8,74 ₽ | набор 4 иконок в одном стиле; нарезка по bbox; `controls.colors` | ключ RouterAI |
| VEC-ICON-LINE | — | LLM пишет SVG со `stroke` (текстовые модели polza) | polza | копейки за вызов LLM | G: рендер + сверка сетки 24/20 | **без нового ключа** (Recraft не подходит: P/07) |
| VEC-TRACE | нет векторизации | Recraft vectorize (fal, Recraft API), Vectorizer.ai (€0,13–0,18), Gen-API Image2svg (1 ₽), fal image2svg / vecglypher ($0,005); локально vtracer | Gen-API — рубли; остальное — иностр. | 1 ₽ (Gen-API) … $0,01–0,18 | 3 растра → SVG, число путей, ΔE, вес | сначала локально (vtracer, агенты G/H), затем Gen-API Image2svg |
| VEC-ANIM | нет | OmniLottie image-to-lottie (fal $0,10); LLM → SVG+CSS | fal — иностр. | $0,10 | 1 иконка → Lottie | не заводить; LLM-путь (G) |
| IMG-CUTOUT | нет `background` у GPT Image 2.5 (есть у Qwen Image 2.1, но веса 2.1 — Qwen Research License, некоммерческая; есть ли у KIE коммерческая лицензия — не раскрыто, к L) и нет удаления фона | GPT Image 2.5 `background: transparent` (RouterAI, AITUNNEL, Gen-API, OpenAI, KIE); удаление фона: Gen-API (Ideogram 2,5 ₽, Pixelcut 4 ₽), KIE Recraft $0,005, fal Bria $0,018 / BiRefNet, Photoroom $0,02; Topaz Transparent Upscale (fal) | RouterAI/AITUNNEL/Gen-API — рубли | GPT 1K medium 1,4 ₽ (RouterAI) — 7,5 ₽ (Gen-API); удаление фона 2,5–4 ₽ в рублях | 1) polza `/v2/images/generations` + `background`; 2) RouterAI GPT Image 2.5 transparent; 3) Gen-API Ideogram RMBG на 3 снимках | сначала polza (тест 1); иначе RouterAI |
| IMG-TEXTURE | нет параметра tile | fal `z-image/turbo/tiling` ($0,02/Мп, `tiling_mode`); SeedVR2 seamless upscale ($0,0025/Мп); Midjourney `--tile` (без API) | fal — иностр. | ≈1,7 ₽ за 1 Мп | 2 текстуры 2 Мп, метрика шва ratio ≤ 1,2 (P/06) | fal — если есть иностр. оплата; иначе постобработка (H) |
| IMG-SERIES | мульти-референсы есть, стилевой идентичности нет | Recraft V4 Styles (`style_id`, 1–10 референсов, `style_match`); Ideogram style codes / Character | RouterAI (Styles 3,82–13,1 ₽); Gen-API (без style_id) | 3,82 ₽ растр, 5,46 ₽ вектор | серия 4 картинки по 1 стилю, попарный VLM + ΔE | в тест RouterAI |
| IMG-TEXT-LATIN / CYR | есть сильные (GPT Image 2.5, NB Pro — C1) | Ideogram V3/4.0 (Gen-API, KIE, fal); Recraft `text_layout` (только V3, латиница + гомоглифы) | Gen-API — рубли | 7,5–22,5 ₽ | 3 надписи (лат/кир) в Ideogram против лидера polza по OCR | только если лидеры polza проиграют по кириллице |
| IMG-EDIT (слои) | нет разложения на слои | Qwen Image Layered (Gen-API 12,5 ₽; fal $0,05); Seedream 5 Pro Layer Decomposition (KIE $0,035; fal $0,034/слой); Ideogram layerize-text (fal $0,09); Bria Ad Delayer | Gen-API — рубли | 4–12,5 ₽ | 1 hero → слои RGBA → параллакс | Gen-API (1 тест) |
| IMG-OUTPAINT | есть через правку моделей | FLUX Outpainting (BFL/fal `flux-2-pro/outpaint`), Ideogram Reframe, Recraft outpaint, Bria Expansion $0,02 | иностр.; Gen-API Reframe | $0,02–0,09 | 1 кадр 16:9 → 9:16 | не заводить до теста polza (C1) |
| IMG-UPSCALE | Topaz без выбора модели | Recraft Crisp (KIE $0,0025; Gen-API 0,8 ₽), SeedVR2 (fal $0,001/Мп; Gen-API 0,25 ₽/Мп), Topaz Wonder/Bloom/Transparent (Topaz API, fal); локально Real-ESRGAN ncnn | Gen-API — рубли | 0,25–0,8 ₽ | 2 картинки: polza Topaz ×2 против SeedVR2 | без ключа (polza + локально, агент H) |
| VID-HERO-LOOP | нет флага петли; кадры first/last — у Kling 3 и Veo 3.1 FLF | Luma Ray 3.2 `loop` (fal/Replicate); Seedance 2/2.5 first=last (KIE, BytePlus, витрины OpenRouter с `frame_images`); PixVerse V6 Transition (KIE, fal, Gen-API) | Luma — иностр.; PixVerse — Gen-API | Luma i2v 540p $0,15 (12,6 ₽); PixVerse 720p 11,25 ₽/с (Gen-API) | 1) polza Kling 3 first=last (C2/I); 2) Luma loop 540p; SSIM шва | сначала polza; Luma — если шов не держится и есть иностр. оплата |
| VID-CINEMAGRAPH | `fixed_lens` только у Seedance 1.5 Pro (снята у BytePlus) | Seedance 2 `camera_fixed` (BytePlus), Luma concepts (legacy API) | иностр. | — | (агенты C2/I) | без ключа до теста polza |
| VID-CAMERA | нет camera_control | Kling `camera_control` только у v1.x; Luma `concepts` (ray-2) | иностр. | — | словарь камеры в промте (D2) | не заводить |
| VID-LONG | в polza есть (Seedance 2.5 до 30 с, Veo extend) | Kling 3 multi-shot (KIE, Kling API), PixVerse extend | иностр. | — | — | не заводить |
| VID-ALPHA | нет нативной альфы нигде (ProRes 4444 у Runway — непрозрачная) | матирование: fal BiRefNet video, Bria VRMBG 3.0 (fal); локально RVM/MatAnyone (лицензии — файл 05) | иностр.; локально | — | агент I | без ключа (локально) |
| VID-UPSCALE | есть Topaz ×2/×4 | Topaz interpolate (fal), RIFE (fal / локально ncnn) | polza, локально | — | агент I | без ключа |
| Дешёвый перебор видео | есть (Grok 1.5 1,62 ₽/с) | Veo 3.1 Lite (AITUNNEL 5,1 ₽/с 720p, RouterAI, fal $0,03/с) | рубли | 25,5 ₽ за 5 с | — | не нужно: Grok 1.5 в polza дешевле |

[вывод P; источники — файлы 03–05 и их списки источников]

## 2. Рейтинг кандидатов на ключи после волны 1 (польза на рубль)

| Место | Ключ | Что открывает (коды задач) | Оплата | Стоимость минимального теста | Польза на рубль | Риски |
|---|---|---|---|---|---|---|
| 1 | **RouterAI** (рубли) | Recraft V4/V4.1 Vector и V4 Styles (VEC-ILLUSTR, VEC-ICON-FILLED, IMG-SERIES); GPT Image 2.5 с `background`/`quality` (IMG-CUTOUT, IMG-DRAFT по `low`); Veo 3.1 Lite; Seedance с кадрами first/last (VID-HERO-LOOP) — если passthrough работает | рубли, без VPN | ≈35–60 ₽ (4 вектора + 2 GPT transparent + 1 Styles-серия) | высокая: единственный рублёвый путь к Recraft-вектору по цене ≈ вендора ×1,3 | зависимость от цепочки OpenRouter (закрыт для РФ); passthrough не проверен; ООО «Интер» — оферта без описания поставщиков |
| 2 | **Gen-API** (рубли) | Ideogram V3 (текст, прозрачность), удаление фона (Ideogram, Pixelcut), Qwen Image Layered, SeedVR2, Image2svg, PixVerse V6 Transition, Luma Ray 2 modify; запасной путь к Recraft vector (без `style_id`) | рубли | ≈40–60 ₽ (2 удаления фона + 1 слои + 1 Ideogram + 1 Image2svg) | средняя: широкая экзотика, но наценка ≈3× к курсу | дорого на пересечениях с polza; `translate_input` по умолчанию; Midjourney неофиц. |
| 3 | **fal или Runware** (иностранная оплата) | Luma Ray 3.2 `loop` (VID-HERO-LOOP), Z-Image tiling (IMG-TEXTURE), Recraft вектор/Styles/vectorize, Ideogram transparent, слои, Topaz transparent, видео-матирование, OmniLottie; у Runware — те же Luma `loop`, прозрачность GPT Image 2.5, Recraft SVG/vectorize, видео с альфой (Bria, WEBM/MOV) по ценам вендоров | карта вне РФ | ≈$1 (Luma 540p ×2, tiling ×2, vectorize ×2) | высокая по возможностям, низкая по доступности | AUP: санкционные территории; кредиты сгорают за 365 дней; медиа публичны по умолчанию |
| 4 | **Recraft** напрямую (иностранная оплата) | полный API: `/v1/styles`, палитра `controls.colors`, vectorize, removeBackground (SVG→SVG), crisp/creative upscale, inpaint/outpaint; данные не идут в обучение | карта вне РФ; API units заранее | $1 = 1000 единиц (≈12 векторов) | средняя: нужен, если витрины режут параметры | санкционные оговорки (проверить ToS Recraft); хранение 24 ч |
| 5 | **KIE** напрямую (иностранная оплата) | те же модели, что в polza, но с недоступными в polza параметрами (GPT Image `background`, Veo `duration`/Lite, Seedance first/last, Kling multi-shot) + Recraft remove bg, Ideogram, Runway, PixVerse | карта, PayPal | ≈$1 | средняя: дёшево, но не даёт резервирования (тот же поставщик, что у polza) | «стабильность ниже официальной»; политика данных пуста |
| 6 | **AITUNNEL** (рубли) | запасной рублёвый вход в каталог OpenRouter (GPT Image 2.5 transparent, Veo 3.1 Lite, Seedance 2.0 1080p) — без Recraft-вектора | рубли | ≈30 ₽ | низкая, если есть RouterAI | наценка ×2; вектора нет |
| 7 | **Replicate** (иностранная оплата) | Wan 3 вдвое дешевле fal, Luma Ray 3.2, Recraft SVG (урезанные параметры) | карта вне РФ | ≈$0,5 | низкая | эмбарго-оговорки |
| — | не заводить | OpenRouter (закрыт для РФ), Midjourney-прокладки (нет официального API), VseGPT (каталог медиа отстаёт), BotHub/GPTunnel (цены только по ключу — сначала сравнить), Clipdrop (влит в Jasper) | — | — | — | — |

Ответ на гипотезу оркестратора «номер один — Recraft для SVG»: **подтверждается по модели, уточняется по каналу** —
нужен именно векторный Recraft (другого массового генератора настоящего SVG нет; LLM-SVG закрывает только линейные
иконки и паттерны), но первым ключом разумнее взять российскую витрину с Recraft (RouterAI), а прямой ключ Recraft
держать как вариант 2-й очереди — если в фазе 5 выяснится, что витрина не пропускает `style_id`/`controls` или нужны
`vectorize`/`removeBackground` с SVG [вывод P].

## 3. Что ключ даёт системе (маршрутизация после ключей)

```yaml
# routing-hints · агент P · 2026-09-23 · [не проверено] до фазы 5
VEC-ILLUSTR:      {primary: "routerai: recraft/recraft-v4.1-vector", fallback: "gen-api: recraft-v4 (model=vector)", post: "удалить фон-прямоугольник, width/height, preserveAspectRatio; svgo без removeMetadata или осознанно"}
VEC-ICON-FILLED:  {primary: "routerai: recraft/recraft-v4-styles-vector + style_id", fallback: "routerai: recraft/recraft-v4.1-vector", post: "нарезка набора по bbox, нормализация в 24×24"}
VEC-ICON-LINE:    {primary: "polza: текстовая LLM → SVG со stroke", note: "Recraft отдаёт только заливки (P/07)"}
IMG-CUTOUT:       {primary: "polza: qwen/image-2.1 background=transparent (C1); лицензия весов 2.1 — research, до решения L только черновики", candidate: "polza /v2/images/generations gpt-image-2.5 background=transparent — проверить", fallback: "routerai: openai/gpt-image-2.5-flare background=transparent", post_alt: "gen-api: ideogram background removal"}
IMG-TEXTURE:      {primary: "fal: fal-ai/z-image/turbo/tiling (если есть оплата)", fallback: "генерация + дорисовка шва (агент H), метрика ratio ≤ 1,2"}
VID-HERO-LOOP:    {primary: "polza: kling/v3 images=[A, A] (C2/I проверяют)", fallback: "fal: luma/agent/ray/v3.2/image-to-video loop=true 540p"}
IMG-EDIT:         {scope: "разложение на слои RGBA (цепочка 6); предложен код IMG-LAYERS — в отчёте P", primary: "gen-api: qwen-image-layered", alt: "kie/fal: seedream 5 pro layer decomposition"}
```

## 4. Цена разрыва: сколько стоит закрыть его в рублях

| Разрыв | Самый дешёвый рублёвый путь | ₽ за единицу | Зарубежный путь | ₽ по курсу ЦБ |
|---|---|---|---|---|
| Настоящий SVG (Recraft V4.1 Vector) | RouterAI | 8,74 | Recraft/fal/Replicate $0,08 | 6,73 |
| SVG серии по стилю (V4 Styles Vector) | RouterAI | 5,46 (+0,55 за референс-стиль) | Recraft $0,05 + $0,005 | 4,62 |
| Прозрачный объект GPT Image 2.5 1K medium | RouterAI | ≈1,4 | OpenAI $0,0132 | 1,11 |
| Удаление фона | Gen-API (Ideogram) | 2,5 | KIE Recraft $0,005 | 0,42 |
| Слои RGBA из картинки | Gen-API Qwen Image Layered | 12,5 | KIE Seedream Layer Decomposition $0,035 | 2,94 |
| Бесшовная текстура 1 Мп | — | — | fal $0,02 | 1,68 |
| Петля 5 с 540p (Luma loop) | — | — | fal/Replicate $0,15 | 12,6 |
| Ideogram V3 Balanced | Gen-API | 15 | KIE $0,035 | 2,94 |
| Veo 3.1 Lite 720p 5 с | AITUNNEL | 25,5 | fal $0,15 | 12,6 |

[вывод P по прайсам 23.09.2026; `03-aggregators-and-platforms.md` §4]

## 5. Чего не делать

- Не заводить ключ ради цены моделей, которые есть в polza: выигрыш на бюджете фазы 5 — сотни рублей, а риск второго
  контракта и второй точки отказа — постоянный.
- Не заводить Midjourney через неофициальные API (ToS MJ от 27.05.2026 запрещает автоматизацию; useapi.net и GoAPI
  прекратили MJ-доступ — файл 04).
- Не строить конвейер на Sora 2 (API удаляется 24.09.2026), remove.bg (закрывается 01.12.2026) и Clipdrop (влит в Jasper).
- Не брать OpenRouter напрямую (закрыт для РФ).
- Не отправлять фото клиентов в BFL/Luma без согласия (обучение на входах по их условиям).
- Не считать витрину OpenRouter (RouterAI, AITUNNEL, ProxyAPI) равной OpenRouter по параметрам — проверить passthrough.

## Частые ошибки

1. «Recraft = иконки для UI» — Recraft даёт залитые контуры; линейные иконки по сетке делает LLM (P/07).
2. «Нужен прямой ключ вендора» — часто хватает рублёвой витрины с тем же каталогом.
3. «Второй провайдер = дешевле» — для видео KIE-линейки polza уже дешевле всех рублёвых каналов.
4. «Нет в polza = нет в России» — Recraft, Ideogram, Veo Lite, удаление фона, слои доступны за рубли (RouterAI, Gen-API,
   AITUNNEL).
5. Ошибка ИИ-агента: предлагать `--tile` Midjourney, `camera_control` Kling 3, Imagen 4 или OpenRouter как рабочие
   варианты для РФ в сентябре 2026.

## Чек-лист

- [ ] Разрыв подтверждён по каталогу polza (параметра/модели действительно нет)?
- [ ] Есть рублёвый путь (RouterAI/Gen-API/AITUNNEL) и его цена?
- [ ] Минимальный тест фазы 5 стоит ≤ 60 ₽ и различает гипотезы?
- [ ] Для зарубежного пути у заказчика есть законная оплата и приемлемы условия (санкции, данные)?
- [ ] После ключа маршрут записан в `routing.yaml` с меткой и датой (агент N)?

## Открытые вопросы и противоречия

1. Пропускают ли RouterAI/AITUNNEL/ProxyAPI параметры `style_id`, `controls`, `background`, `quality`, `frame_images` —
   ключевой вопрос для места №1 [не проверено].
2. RouterAI — ООО «Интер» (ОГРН 1147017006950, ИНН 7017351722), лицензионная оферта (routerai.ru/terms, 23.09.2026); способы оплаты (карта, СБП, счёт) и минимальное пополнение на странице не указаны — уточнить при заведении ключа.
3. Качество векторов Recraft на кириллице и на наших сюжетах — только живой тест.
4. Нужна ли система в целом fal (иностранная оплата) ради двух возможностей (Luma loop, tiling) — решение заказчика после
   тестов polza Kling-петли (C2/I) и постобработки текстур (H).

## Источники

См. `03-aggregators-and-platforms.md` (S1–S29), `04-direct-apis-and-services.md`, `05-open-weights-landscape.md`; опыты
`99-raw/experiments/P/06-tiling-seam-check`, `07-recraft-svg-structure`, `08-access-probe`, `12-status-pages`.
