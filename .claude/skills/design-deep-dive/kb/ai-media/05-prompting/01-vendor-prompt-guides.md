# Официальные гайды вендоров по промтам: диалекты моделей картинок и видео

Волна 1 · агент D · 2026-09-23 · прочитано целиком или по существу ≈ 95 источников (гайды и документация 17 вендоров,
документация и каталог polza, 20 статей) · опытов 3 (`99-raw/experiments/D/01…03`) · снимок каталога polza 2026-09-23

## Выжимка для агента

1. **Сначала класс модели, потом формулировка.** Модели с LLM-фронтом (Nano Banana, GPT Image, Omni; Veo — через
   переписчик) выполняют прозу, прозу по разделам и JSON почти одинаково; диффузионные с языковым энкодером (FLUX.2,
   Seedream, Qwen, Z-Image, Wan, Kling, Seedance) — связную прозу с главным в начале; Ideogram 4 — только JSON по
   схеме; MiniMax H3 — «ключ: проза». → §1.1 `[документация]` `[исследование]`
2. **Главное — в начало промта**: субъект → действие → стиль → контекст → детали. «FLUX.2 pays more attention to what
   comes first»; Recraft — «from global to local». → §5.1, §11.3 `[документация]`
3. **Длина для картинки — 30–80 слов**, 80–300 — только сложная сцена; Seedream — меньше 600 английских слов; Z-Image
   в polza — не больше 1 000 символов. «More words do not automatically mean better results» (BFL). → §5.1, §6.1
   `[документация]`
4. **Описывай сцену связным текстом, а не списком тегов** («A narrative, descriptive paragraph will almost always
   produce a better… image than a simple list», Google). Исключение — Midjourney: коротко. → §2.1, §11.5
   `[документация]`
5. **Лимит длины промта бери из каталога polza, а не из документации polza**: они расходятся (Veo 2 000 против 60 000,
   GPT-5 Image 32 000 против 4 000). → §1.2 `[проверено: 99-raw/experiments/D/01-catalog-prompt-limits]`
6. **Поле негатива в polza есть только у `wan/2.5`** (`negative_prompt` ≤ 500 символов). У остальных 43 медиа-моделей
   его нет — не отправляй `negative_prompt` вслепую. → §12.1 `[проверено: 99-raw/experiments/D/01-catalog-prompt-limits]`
7. **«no X» в прозе у FLUX.2, Runway, Midjourney, Ideogram не пиши — заменяй описанием того, что там есть** («empty
   street», «clean unmarked surfaces», «Locked camera. The camera remains still.»). У моделей с LLM-фронтом служебные
   запреты «No text. No watermark. No subtitles. No dialogue.» допустимы — так пишут сами Google, OpenAI, ByteDance,
   Alibaba. → §12.1 `[документация]` `[спорно]`
8. **В поле негатива — существительные без «no»**: «wall, frame», «apples», а не «no apples» (Vertex, Recraft V2/V3 и
   Studio, Ideogram; у Recraft V4/V4.1 в API поля негатива нет — запреты прозой). → §12.1, §11.3 `[документация]`
   [поправка X 24.09.2026 по G `../07-vector-svg-icons/02-vector-generators-and-tracing.md` п. 5]
9. **Текст в картинке — в двойных кавычках, дословно, с местом, шрифтом (словами), размером и цветом**; 1–4 слова —
   надёжно, абзац — не в картинку. → §12.7 `[документация]` `[консенсус]`
10. **Кириллица: описание по-английски, строка — по-русски в кавычках + «in Russian (Cyrillic script)»**; по
    умолчанию текст кладётся HTML-слоем поверх картинки; в картинке — только с проверкой OCR. → §12.7
    `[исследование]` `[документация]`
11. **Язык описания — английский.** Veo и Omni: «other languages have not been evaluated»; Ideogram, H3 и переписчик
    Qwen-2512 сами переводят на английский. Русское описание терпят Nano Banana (`ru-RU` в списке языков) и
    Qwen-Image. → §12.7 `[документация]` `[исследование]`
12. **Культурный контекст задавай словами, а не языком промта** («Russian provincial town, Cyrillic shop signs»):
    явная метка в английском промте дала 75 % «своей» культуры против 32.5 % у промта на родном языке (LingT2I). →
    §12.7 `[исследование]`
13. **hex-цвета документированы только у FLUX.2 и Ideogram 4**: «color #RRGGBB (название)», привязка к объекту,
    3–5 цветов. У остальных — название цвета и роль; точный бренд-цвет — постобработкой или параметром Recraft
    `controls.colors`. → §12.5 `[документация]` `[не проверено]`
14. **Долю площади цвета пиши словами** («deep navy dominates about 60 % of the frame, coral only on the mug»); числом
    её не задаёт никто: `weight` в `controls.colors` Recraft — «relative preference», а не доля площади. → §12.5
    `[не проверено]` [поправка X 24.09.2026 по G `07/02` п. 6: было «параметром доли задаёт только Recraft»]
15. **Место под текст — по шаблону Google «Minimalist & negative space»**: «a single [subject] positioned in the
    [right third]… The background is a vast, empty [color] canvas, creating significant negative space for text» +
    сторона и доля кадра; у Ideogram — слова «minimal, sparse, negative space». → §12.6 `[документация]`
    `[не проверено]`
16. **Референсы — по номеру и роли**: «Image 1: product photo. Image 2: style reference» (OpenAI, BFL, Google,
    Seedream); Seedance 2 — `<Image_1>` / «@Image 1»; Kling 3 — `@Name`; Omni — `<IMAGE_REF_0>`. → §12.3, §13
    `[документация]`
17. **Правка = что изменить + где + что сохранить**: «change only X… Keep everything else exactly the same»; одна
    правка за шаг; пиксельную неизменность даёт только композитинг. → §12.3 `[документация]` `[консенсус]`
18. **Маски в polza противоположны**: `openai/gpt-5-image` — чёрное меняется, белое остаётся; `qwen/image-2.1` —
    белое меняется, чёрное остаётся (и только с одним референсом). → §4.5, §7.6, §12.3 `[документация]` `[не проверено]`
19. **Серия — постоянный блок стиля и персонажа, дословно одинаковый в каждом промте**, плюс эталон референсом;
    меняется только сюжетная часть. → §12.4 `[документация]` `[консенсус]`
20. **Image-to-video — только движение**: камера, действие субъекта, движение среды; сцену, свет и внешность не
    пересказывай (Vertex, Wan, Runway, BFL). → §12.2 `[документация]` `[спорно]`
21. **Одна камера и одно действие на короткий клип** (BFL, ByteDance, Vertex, Runway); камера — один физический
    контракт: крупность, ракурс, движение, фокус. → §12.2, §5.8 `[консенсус]`
22. **Неподвижную камеру задавай утвердительно**: «Locked camera. The camera remains still.»; у Wan — «fixed camera»,
    у Seedance 1.5 Pro — ещё и `fixed_lens`. Не смешивай с «tracking», «orbit». → §12.2 `[документация]`
23. **Петля — один и тот же кадр на входах «первый» и «последний»** + «The camera must start and end on the exact same
    frame» (Runway); в preview Omni — `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]`, в GA `gemini-omni-1.1-flash` —
    поля `first_frame_url` + `last_frame_url`. Петлю документируют только Omni, Runway и BFL; у Seedance 1.5, Kling, Veo, H3
    [A,A] — наш перенос. → §3.9, §11.1, `04-video-prompting.md` §3.1 `[документация]` `[не проверено]` [поправка X 24.09.2026
    по D2b]
24. **Таймкоды «[0–3s] …» — только у моделей, которые их держат** (Veo, Omni, Seedance 2.5, Wan 2.6/3.0, Kling 3,
    FLUX 3); у Seedance 2.0 — «Shot 1 / Shot 2» без секунд (гайд), хотя скилл вендора `sd2-pe` сам пишет «0–3s, 3–10s»
    `[спорно]`. → §6.3, §13, `04-video-prompting.md` §5.1 `[документация]` [поправка X 24.09.2026 по D2b]
25. **Omni по умолчанию режет сцену на планы** — для одного плана пиши «In a single continuous shot. No scene cuts.»
    → §3.9 `[документация]`
26. **Звук выключай параметром, где он есть**: у Seedance 2 / Fast / Mini / 2.5 `generate_audio` по умолчанию `"true"`;
    у Veo, Omni, Wan 2.5/2.6, HappyHorse, Grok, H3 Max параметра в polza нет — дорожку снимает кодирование (`-an`);
    словами — только уточнения («No dialogue. No background music.» у Wan и Seedance 2.5). → §6.5, §12.1,
    `04-video-prompting.md` §4.3 `[документация]` [поправка X 24.09.2026 по D2b]
27. **Усилители в polza по умолчанию выключены** (`enhance_prompt`, `enable_prompt_expansion`, `isEnhance`), а
    автоперевод Veo `enableTranslation` включён (`"true"`). Усилитель включай для коротких промтов и правок Qwen. →
    §7.2, §3.8 `[документация]` `[не проверено]`
28. **Veo 3.x читает промт через LLM-переписчик** (у veo-3.0 он не отключался) — форма промта до генератора не
    доходит; пиши ясную прозу по формуле. → §3.8 `[документация]`
29. **Qwen-Image: описание по-английски, надпись в кавычках с указанием языка, в конце «No other text appears in the
    image.»** Язык надписи — явно: модель смещена к китайскому. → §7.1–7.2 `[документация]` `[не проверено]`
30. **FLUX.2: прямой JSON документирован, но скилл BFL сплющивает JSON в прозу.** По умолчанию отправляй прозу по
    разделам, прямой JSON — плечо A/B. → §5.2 `[документация]` `[спорно]`
31. **Ideogram 4 — только JSON по схеме**: фиксированный порядок ключей, `bbox` 0–1000, палитра ≤ 16 hex; прозу —
    через Magic Prompt. → §11.4 `[документация]`
32. **Стиль — видимыми признаками, а не оценочными словами**: «vintage» → формат плёнки, зерно, практический свет;
    без «stunning, vibrant, luminous» (Ideogram, BFL). → §11.4, §5.9 `[мнение вендора]`
33. **Словарь камеры — по одному термину на крупность, движение и объектив**; MiniMax — тип + амплитуда + скорость
    или команды `[Pan left]`; Seedance — «Subject + Shot Size». → §12.8 `[документация]`
34. **За итерацию меняй один элемент**; после двух похожих промахов меняй метод или концепцию, а не прилагательные
    (BFL). → §5.9, §4.1 `[документация]`

## 1. Модель диалектов: как модель читает промт

### 1.1 Четыре класса входа

Форма промта важна настолько, насколько модель видела такую форму в подписях обучения. DALL-E 3: «Generative models
are known to produce poor results when sampled out of their training distribution» — поэтому OpenAI расширяет промт
LLM до стиля подписей [S60]. Отсюда четыре класса (по документации вендоров и статьям):

| Класс | Кто | Как читает | Что это значит для промта |
|---|---|---|---|
| A. LLM-фронт | Nano Banana / NB2 / NB2 Lite / NB Pro (thinking-модели Gemini 3), GPT Image 2.5 / 2 / 1.5, GPT-5 Image, Gemini Omni, Veo 3.x (LLM-переписчик) | промт читает языковая модель, которая может рассуждать и переписывать | проза, разделы и JSON — почти одинаково; TIIF-Bench: NB-Pro 93.1 (короткий) / 93.3 (длинный) [S58] |
| B. Диффузия с языковым энкодером | FLUX.2 (до 32K токенов), Seedream 4–5, Qwen-Image (VLM-энкодер), Z-Image (Qwen3-4B), Wan, Kling, Seedance | энкодер превращает текст в векторы, без рассуждения | связная проза, главное в начале; структуру модель понимает, если видела её в подписях (Qwen-Image — да [S65]) |
| C. Классическая диффузия с T5/CLIP | SD 3.5, FLUX.1, SDXL, PixArt (в polza нет; открытые веса — агент P) | T5 до 512 токенов, CLIP — «мешок слов» [S56] | коротко, по-английски; русский промт: FLUX.1-Krea 0.44 против 0.77 на английском [S63] |
| D. Обучены на структуре | Ideogram 4 (JSON), Bria FIBO (JSON), MiniMax H3 (IR «ключ: проза») | вход модели = формат подписей обучения | структура обязательна; прозу превращает в структуру вендорский LLM (Magic Prompt, H3-Context-IR) [S45][S38][S54] |

Встроенный переписчик переводит модель из B в A: у FLUX.2 [pro]/[max] апсемплинг промта включён по умолчанию
(выключается `disable_pup: true`), у [flex] — `prompt_upsampling: true` [S18]; Qwen/Wan — `prompt_extend`, Seedream с `optimize_prompt_options`, MiniMax с `prompt_optimizer`. В polza эти переключатели
почти не выставлены (§1.2), а что делает исполнитель `mie` (≈ KIE.ai, 37 из 44 медиа-моделей —
`../02-providers-platforms/01-polza-api.md` §11.3), неизвестно `[не проверено]`.

### 1.2 Модели polza: промт-ограничения по каталогу

Данные — каталог polza 2026-09-23, извлечены скриптом `[проверено: 99-raw/experiments/D/01-catalog-prompt-limits]`
(машиночитаемо: `prompt_limits.json`). Класс — по §1.1; «?» — данных нет.

| id в polza | Модель | Класс | Промт ≤ симв. | Негатив | Референсы | Усилитель в polza (default) | Как модель читает промт | Раздел |
|---|---|---|---|---|---|---|---|---|
| `google/gemini-2.5-flash-image` | Nano Banana (Gemini 2.5 Flash Image) | A | 20000 | нет | images ≤ 8 | — | LLM-модель, рисует сама | §2 |
| `google/gemini-3.1-flash-lite-image` | Nano Banana 2 Lite | A | 20000 | нет | images ≤ 10 | — | thinking-модель (minimal) | §2 |
| `google/gemini-3.1-flash-image-preview` | Nano Banana 2 | A | 20000 | нет | images ≤ 14 | — | thinking-модель | §2 |
| `google/gemini-3.1-flash-image` | Nano Banana 2 (Vertex, токены) | A | не указан | нет | 0 | — | thinking-модель | §2 |
| `google/gemini-3-pro-image-preview` | Nano Banana Pro | A | 20000 | нет | images ≤ 8 | — | thinking-модель | §2 |
| `openai/gpt-image-2.5-sunburst` | GPT Image 2.5 Sunburst | A | 20000 | нет | images ≤ 16 | — | мультимодальная LLM; в Responses — `revised_prompt` | §4 |
| `openai/gpt-image-2.5-flare` (до 25.09.2026 — `gpt-image-2-5-flare`) | GPT Image 2.5 Flare | A | 20000 | нет | images ≤ 16 | — | то же | §4 |
| `openai/gpt-5.4-image-2` | GPT Image 2 (через GPT-5.4) | A | 20000 | нет | images ≤ 16 | — | то же | §4 |
| `openai/gpt-image-1.5` | GPT Image 1.5 (закрытие 2026-12-01) | A | не указан | нет | images ≤ 16 | — | то же | §4 |
| `openai/gpt-5-image` | GPT-5 Image | A | 4000 | нет | images ≤ 5 | `isEnhance` (false) | то же; `isEnhance` | §4 |
| `openai/gpt-5-image-mini` | GPT-5 Image Mini | A | 32000 | нет | images ≤ 10 | — | то же | §4 |
| `black-forest-labs/flux.2-pro` | FLUX.2 [pro] | B | 5000 | нет | images ≤ 8 | — | энкодер до 32K токенов; в API BFL апсемплинг по умолчанию включён (`disable_pup=false`), в polza не управляется | §5 |
| `black-forest-labs/flux.2-flex` | FLUX.2 [flex] | B | 5000 | нет | images ≤ 8 | — | `prompt_upsampling=true` по умолчанию в API BFL; в polza нет steps/guidance | §5 |
| `bytedance/seedream-4` | Seedream 4.0 | B | 5000 | нет | images ≤ 10 | — | `optimize_prompt_options` в BytePlus; в polza нет | §6.1 |
| `bytedance/seedream-4.5` | Seedream 4.5 | B | 3000 | нет | images ≤ 14 | — | то же | §6.1 |
| `bytedance/seedream-5-lite` | Seedream 5 Lite | B | 2996 | нет | images ≤ 10 | — | то же | §6.1 |
| `seedream/5-pro-text-to-image` | Seedream 5 Pro | B | не указан | нет | images ≤ 10 | — | то же | §6.1 |
| `qwen/image` | Qwen Image | B | не указан | нет | images ≤ 1 | — | VLM-энкодер; `prompt_extend` в Model Studio | §7.1 |
| `qwen/image-2` | Qwen Image 2 | B | 5000 | нет | images ≤ 3 | — | то же | §7.1 |
| `qwen/image-2.1` | Qwen Image 2.1 | B | 5000 | нет | images ≤ 10 | `enhance_prompt` (False) | то же; в polza `enhance_prompt` | §7.1 |
| `tongyi-mai/z-image` | Z-Image | B | 1000 | нет | 0 | — | энкодер Qwen3-4B, выровнен на усилитель PE | §7.4 |
| `x-ai/grok-imagine-image` | Grok Imagine Image | ? | 5000 | нет | images ≤ 1 | — | нет данных | §10 |
| `google/veo3` | Veo 3.1 Quality | A | 60000 | нет | images ≤ 2 | `enableTranslation` (true) | LLM-переписчик (у veo-3.0 не отключался) | §3 |
| `google/veo3_fast` | Veo 3.1 Fast | A | 60000 | нет | images ≤ 3 | `enableTranslation` (true) | то же; `enableTranslation` | §3 |
| `gemini-omni-video` | Gemini Omni Flash | A | 20000 | нет | images ≤ 7, videos ≤ 1, audio_ids ≤ 3, character_ids ≤ 3 | — | LLM-модель; теги ролей медиа | §3.9 |
| `bytedance/seedance-1.5-pro` | Seedance 1.5 Pro | B | 2500 | нет | images ≤ 2 | — | нет данных о переписчике | §6.2 |
| `bytedance/seedance-2` | Seedance 2.0 | B | 20000 | нет | images ≤ 5, videos ≤ 1 | — | то же | §6.3 |
| `bytedance/seedance-2-fast` | Seedance 2.0 Fast | B | 20000 | нет | images ≤ 5, videos ≤ 1 | — | то же | §6.3 |
| `bytedance/seedance-2-mini` | Seedance 2.0 Mini | B | 20000 | нет | images ≤ 9, videos ≤ 3 | — | то же | §6.3 |
| `bytedance/seedance-2-5` | Seedance 2.5 | B | 30000 | нет | images ≤ 30, videos ≤ 10 | — | вендорский скилл-оптимизатор sd25-pe (вне API) | §6.4 |
| `kling/v3` | Kling 3.0 | B | 2500 | нет | images ≤ 2 | — | нет данных | §8 |
| `kling/v2.6` | Kling 2.6 | B | не указан | нет | images ≤ 1 | — | нет данных | §8 |
| `kling/v3-motion-control` | Kling 3.0 Motion Control | — | 2500 | нет | images ≤ 1, videos ≤ 1 | — | движение из видео; промт вторичен | §8 |
| `kling/v2.6-motion-control` | Kling 2.6 Motion Control | — | 2500 | нет | images ≤ 1, videos ≤ 1 | — | то же | §8 |
| `wan/2.5` | Wan 2.5 | B | 800 | `negative_prompt` ≤ 500 | images ≤ 1 | `enable_prompt_expansion` (false) | `prompt_extend` в Model Studio; в polza `enable_prompt_expansion` | §7.3 |
| `wan/2.6` | Wan 2.6 | B | 5000 | нет | images ≤ 1 | — | `prompt_extend` в Model Studio | §7.3 |
| `alibaba/wan-3.0` | Wan 3.0 | B | не указан | нет | images ≤ 1 | — | то же | §7.3 |
| `alibaba/wan-3.0-prime` | Wan 3.0 Prime | B | не указан | нет | images ≤ 1 | — | то же | §7.3 |
| `alibaba/happyhorse-1.0` | HappyHorse 1.0 | ? | не указан | нет | images ≤ 1 | — | гайда нет | §7.4 |
| `alibaba/happyhorse-1.1` | HappyHorse 1.1 | ? | не указан | нет | images ≤ 1 | — | гайда нет | §7.4 |
| `minimax/hailuo-3-max` | MiniMax H3 Max (fal.ai) | D | не указан | нет | images ≤ 2 | — | H3 обучен на IR «ключ: проза»; применяет ли провайдер IR — неизвестно | §9 |
| `grok-imagine-video-1-5` | Grok Imagine Video 1.5 | ? | 4096 | нет | images ≤ 7 | — | t2v = t2i + i2v внутри | §10 |

Не в таблице: `topaz/image-upscale`, `topaz/video-upscale` — промта нет. Расхождения документации polza и каталога:
Veo — 2 000 символов в гайде против 60 000 в каталоге (в Gemini API — 1 024 токена [S7]); `openai/gpt-5-image` —
32 000 символов и 10 картинок в гайде против 4 000 и 5 в каталоге; `openai/gpt-5.4-image-2` — 5 000 против 20 000;
Nano Banana 2 — 8 референсов в гайде против 14 в каталоге; Seedance 2 — «до 1536 символов» в описании против
`max_length` 20 000 [S66][S67]. Правило: отправляй не больше меньшего из двух чисел, пока фаза 5 не покажет обратное.

### 1.3 Как читать разделы вендоров

Каждый раздел: формула и порядок → длина → референсы → правки → текст и язык → камера и свет → негатив → примеры
дословно → особенности polza. Примеры — дословные цитаты гайдов (статус `[документация]` означает «так пишет вендор»,
не «проверено нами»). Карточки моделей (возможности, цены, бенчмарки) — у агентов C1 и C2:
`../03-image-models/`, `../04-video-models/`.

## 2. Google — Nano Banana, Nano Banana 2 / 2 Lite, Nano Banana Pro

Семейство Gemini Image: `gemini-2.5-flash-image` (Nano Banana), `gemini-3.1-flash-image` (NB2),
`gemini-3.1-flash-lite-image` (NB2 Lite), `gemini-3-pro-image` (NB Pro). Модели Gemini 3 — **thinking-модели**:
до двух промежуточных «thought images», рассуждение в API не выключается, у 3.1 Flash / Flash Lite `thinking_level`
`minimal` (по умолчанию) или `high` [S2]. Промт читает языковая модель — класс A (§1.1).

### 2.1 Формула, порядок, длина

- **Связный текст вместо тегов.** «A simple list of keywords won't cut it; you need to describe the scene
  narratively» [S1]; «Describe the scene, don't just list keywords… A narrative, descriptive paragraph will almost
  always produce a better, more coherent image than a simple list of disconnected words» [S3]; DevRel Google:
  «stop using "tag soups" (e.g., dog, park, 4k, realistic) and start acting like a Creative Director» [S5]
  `[документация]`.
- **Формула без референсов:** `[Subject] + [Action] + [Location/context] + [Composition] + [Style]` [S1]. Элементы
  в блоге Google: Subject, Composition, Action, Location, Style, Editing Instructions [S4].
- **Начинать с глагола операции**: «start a prompt with a strong verb that tells the model the primary operation»
  [S1]; **контекст и назначение**: «Create a logo for a high-end, minimalist skincare brand» [S2]; «for a Brazilian
  high-end gourmet cookbook» [S5].
- **Сложная сцена — по шагам**: «First, create a background of… Then, in the foreground, add… Finally, place…» [S2].
- **Длина:** жёсткого совета нет; Google показывает пары «меньше / больше деталей», где подробный промт лучше [S2][S3].
  Контекст входа: NB2 — 131 072 токена, NB Pro — 65 536 [S1]; в polza — до 20 000 символов (§1.2).
- **Разделы с жирными метками — практика DevRel Google** для NB Pro: «**Face Consistency:** … **Action:** …
  **Subject:** … **Graphics:** … **Text:** … **Background:** …», «**Layout:** … **Style:** … **Quality:** …» [S5].
  Официальные гайды — проза; разделы — допустимая вторая форма `[практика]`.

### 2.2 Референсы

- **Формула с референсами:** `[Reference images] + [Relationship instruction] + [New scenario]` [S1].
- **Роли по номеру или букве:** «Use Image A for the character's pose, Image B for the art style, and Image C for the
  background environment» [S4]; «Keep the person's facial features exactly the same as Image 1» [S5].
- **Сколько и каких** (Gemini API): NB Pro — до 6 объектов + до 5 персонажей + **до 3 style references**; NB2 — до 10
  объектов + до 4 персонажей; NB2 Lite — до 14 объектов, «Not optimized for multiple reference inputs or multi-turn
  sequential editing»; Nano Banana (2.5) — «works best with up to 3 images as input» [S2]. DevRel: 14 референсов,
  «6 with high fidelity» [S5].
- **Структура из референса**: скетч, вайрфрейм или сетка задают композицию — «Keep the exact layout of the bottle and
  text placement», «strictly adhere to the button placement and grid structure» [S5].
- **Соотношение сторон при правке**: сохраняется как у входа; при нескольких входах разных пропорций берётся
  пропорция **последнего** изображения; нужный формат — дать референс нужных пропорций или «Do not change the input
  aspect ratio.» [S3]. Без входа по умолчанию 1:1 [S2]. В polza есть параметр `aspect_ratio` — задавай его явно.

### 2.3 Правки

- «Focus on what is changing and what is staying the same»; «Be explicit about what to keep exactly the same» [S1].
- Шаблон семантической маски (инпейнт текстом) — §2.8, пример 3 [S2]; перенос стиля — «Preserve the original
  composition but render it with…»; перенос элемента — «Take the [element from image 1] and place it with/on the
  [element from image 2]»; сохранение деталей — «describe them in great detail along with your edit request… Ensure
  that the features of [element from image 1] remain completely unchanged» [S2].
- **Править, а не перегенерировать**: «Edit, Don't Re-roll» — если результат верен на 80 %, просить точечную правку
  [S5]; при дрейфе персонажа в длинном диалоге — начать новый разговор с подробным описанием [S3].

### 2.4 Текст в картинке и язык

- Текст — в кавычках, шрифт — названием или описанием («bold, white, sans-serif font», «Century Gothic 12px font»)
  [S1]; «The headline 'URBAN EXPLORER' rendered in bold, white, sans-serif font at the top» [S4].
- **Сначала текст, потом картинка**: «When generating text for an image, Gemini works best if you first generate the
  text and then ask for an image with the text» [S2]; «Text-first hack» [S1].
- **Локализация**: «Write your prompt in one language and specify a target language for the text output» [S1];
  «translate all the English text on the three yellow and blue cans into Korean, while keeping everything else the
  same» [S4].
- **Языки** (Gemini API, ограничения): «For best performance, use the following languages: EN, ar-EG, de-DE, es-MX,
  fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN» [S2] — **русский в списке**
  `[документация]`. Оговорка: «Multilingual text generation may make grammar mistakes or miss specific cultural
  nuances» [S4].
- Независимые данные: в MULTITEXTEDIT у NB2 самый малый разрыв «английский — прочие языки» (4.098 против 3.997) [S53];
  в LingT2I рендер надписи у Nano Banana — 0.68 на английском против 0.47 на русском [S63] `[исследование]`.

### 2.5 Камера, свет, материалы

Словарь «креативного директора» из гайдов Google [S1][S3]:

| Ось | Формулировки Google |
|---|---|
| Свет | «three-point softbox setup», «Chiaroscuro lighting with harsh, high contrast», «Golden hour backlighting creating long shadows» |
| Камера | GoPro, Fujifilm, disposable camera; «low-angle shot with a shallow depth of field (f/1.8)», wide-angle, macro |
| Грейд и плёнка | «as if on 1980s color film, slightly grainy», «Cinematic color grading with muted teal tones» |
| Материалы | «navy blue tweed», «ornate elven plate armor…» |
| Формат | «A 9:16 vertical poster», «A cinematic 21:9 wide shot» [S4] |

### 2.6 Место под текст

Единственный официальный шаблон «фон для текста» у крупных вендоров — **Minimalist & negative space design** [S2][S3]:
«Excellent for creating backgrounds for websites, presentations, or marketing materials where text will be
overlaid» [S2]. Пример — §2.8, пример 1. Для спецификации ассета (`03-asset-spec-and-dialects.md` §3) из него берутся
три элемента: положение субъекта («in the bottom-right of the frame»), пустой фон одним цветом («a vast, empty
[color] canvas»), назначение («creating significant negative space for text»).

### 2.7 Негатив

- Поля негатива нет ни в Gemini API, ни в polza.
- Совет: «Use positive framing ("empty street" instead of "no cars")» [S1]; «Use "semantic negative prompts": Instead
  of saying "no cars," describe the intended scene positively: "an empty, deserted street with no signs of
  traffic."» [S2]. Рекомендованная фраза сама содержит «no signs of traffic» — Google запрещает голое «no X», но не
  отрицание внутри описания сцены.
- Собственные примеры Google заканчиваются служебными запретами: «…tactile 3D style. No text.», «No other text.» [S2]
  `[документация]`. Позиция базы: «No text / No other text / No watermark» — можно; предметы убирать описанием
  пустоты `[спорно]`.

### 2.8 Примеры из гайдов (дословно)

```text
// google/gemini-3.1-flash-lite-image · шаблон Gemini API [S2] · polza 2026-09-23 · [документация]
A minimalist composition featuring a single [subject] positioned in the [bottom-right/top-left/etc.] of the frame.
The background is a vast, empty [color] canvas, creating significant negative space. Soft, subtle lighting.
[Aspect ratio].
```

```text
// google/gemini-2.5-flash-image · шаблон Google Developers Blog [S3] · polza 2026-09-23 · [документация]
A photorealistic [shot type] of [subject], [action or expression], set in [environment]. The scene is illuminated
by [lighting description], creating a [mood] atmosphere. Captured with a [camera/lens details], emphasizing [key
textures and details]. The image should be in a [aspect ratio] format.
```

```text
// google/gemini-3-pro-image-preview · шаблон правки Gemini API [S2] · polza 2026-09-23 · [документация]
Using the provided image of [subject], change only the [specific element] to [new element/description]. Keep
everything else in the image exactly the same, preserving the original style, lighting, and composition.
```

```text
// google/gemini-3-pro-image-preview · формула с референсами, Google Cloud Blog [S1] · polza 2026-09-23 · [документация]
Using the attached napkin sketch as the structure and the attached fabric sample as the texture, transform this
into a high-fidelity 3D armchair render. Place it in a sun-drenched, minimalist living room.
```

```text
// google/gemini-3-pro-image-preview · перевод надписей, блог Google [S4] · polza 2026-09-23 · [документация]
translate all the English text on the three yellow and blue cans into Korean, while keeping everything else the same
```

### 2.9 В polza

| id | Цена ₽ (2026-09-23) | Референсы | Соотношения | Заметки |
|---|---|---|---|---|
| `google/gemini-2.5-flash-image` | 2,90 | ≤ 8 | 10, до 21:9 | лучше всего до 3 входов [S2] |
| `google/gemini-3.1-flash-lite-image` | 2,90 | ≤ 10 | 15, включая 1:4, 4:1, 1:8, 8:1 | ленты-баннеры; не для мульти-референса |
| `google/gemini-3.1-flash-image-preview` | 4,80 / 7,20 / 10,80 (1K / 2K / 4K) | ≤ 14 (в гайде polza — 8) | 11 + `auto` | `output_format` |
| `google/gemini-3.1-flash-image` | по токенам (google-vertex) | — | — | параметры в каталоге не описаны |
| `google/gemini-3-pro-image-preview` | 13,50 / 13,50 / 18 | ≤ 8 | 11 + `auto` | до 3 style references в прямом API [S2] |

`thinking_level` в polza не выставлен. Гайды polza показывают русские промты правок («Измени фон на закат над морем»)
[S66]. На все картинки Google ставит C2PA и SynthID [S1] — правовые следствия у агента L.

## 3. Google — Veo 3.1 и Gemini Omni Flash (видео)

Veo 3.1 (`veo-3.1-generate-preview`, `-fast-`, `-lite-`) и Gemini Omni Flash (`gemini-omni-1.1-flash`) — в Gemini
API Omni названа моделью видео по умолчанию, Veo 3.1 оставлен для продления, последнего кадра и легаси [S8].
Гайд Vertex по промтам общий для обеих моделей [S9].

### 3.1 Формула, порядок, длина

- **Формула Veo:** `[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]` [S6]. Gemini API:
  Subject, Action, Style + (необязательно) Camera positioning and motion, Composition, Focus and lens effects,
  Ambiance [S7]. Vertex добавляет Temporal (slow-motion, time-lapse, «Evolution (subtle for short clips)»), Audio и
  монтажные термины (match cut, jump cut, montage) [S9].
- **Одна сцена на короткий клип**: «Focus short videos on a single scene» — цепочка «A, затем B, затем C» даёт кашу;
  делить на клипы [S10].
- **Ясно и конкретно**: антипример Vertex — «I envision a scene where, like…» [S10]. Подробный промт лучше короткого
  (пары «Less detail / More detail» в Gemini API) [S7].
- **Лица**: «Enhance the facial details… using the word portrait» [S7].
- **Длина:** Gemini API — **1 024 токена** на текст [S7]; polza — 60 000 символов в каталоге, 2 000 в гайде polza
  (§1.2).

### 3.2 Словарь камеры, объектива, времени (Vertex [S9], Cloud Blog [S6])

| Ось | Термины |
|---|---|
| Ракурс и крупность | eye-level, low-angle, high-angle, bird's-eye / top-down, worm's-eye, dutch angle, extreme close-up, close-up, medium shot, full / long shot, wide / establishing shot, over-the-shoulder, POV, two-shot |
| Движение камеры | static / fixed, pan, tilt, dolly in / out, truck, pedestal, zoom, crane, aerial / drone, handheld, whip pan, arc |
| Объектив и фокус | wide-angle, telephoto, shallow / deep depth of field, soft focus, macro, lens flare, rack focus, fisheye, dolly zoom |
| Время | slow-motion, time-lapse; «The camera remains static as…» |
| Стиль | свет, тон, художественный стиль, атмосфера; палитра — словами («muted earthy tones», «cool blue and silver futuristic palette») |

Оговорка Vertex: «Some advanced camera angles are not officially supported» (и часть оптических эффектов) [S9].

### 3.3 Image-to-video

- **Vertex — только движение**: «Prompt for motion only. Your source image already provides the subject, scene, and
  style… Not recommended: Re-describe the character, the background, or the lighting depicted in the image.
  Redundant prompts confuse the model and lead to poor results» [S10]. Персонажа называть общо: «the subject», «the
  woman», «he».
- **Три типа движения** [S10]: движение камеры — самое надёжное («Slow dolly in on the subject.»); анимация субъекта
  («hair and clothes flutter gently in the wind»); анимация среды («Fog rolls in slowly across the landscape»).
- **Противоречие**: пример i2v в Gemini API описывает сцену заново и добавляет движение — «A surreal, cinematic macro
  video. Tiny surfers ride perpetual, rolling waves inside a stone bathroom sink… The camera slowly pans across the
  whimsical, sunlit scene…» [S7]. Позиция базы — движение плюс минимум якорей (§12.2) `[спорно]`.
- «Veo uses the input image as the initial frame» [S7].

### 3.4 Первый и последний кадр, референсы, продление

- **Два кадра**: Nano Banana делает начальный и конечный кадр, Veo строит переход («smooth 180-degree arc shot») [S6].
  В polza — `generationType: FIRST_AND_LAST_FRAMES_2_VIDEO`.
- **Ингредиенты**: «Using the provided images for the detective, the woman, and the office setting, create…» [S6];
  в Gemini API — до 3 референсов (`referenceType: asset`), только 8 с [S7]; в polza `REFERENCE_2_VIDEO` — только у
  `google/veo3_fast`, до 3 картинок.
- **Продление** (Gemini API): +7 с до 20 раз, до 148 с, только 720p; промт продления — продолжение действия:
  «Extend this video with the paraglider slowly descending» [S7]. В polza — операция `extend` (45 ₽,
  `../02-providers-platforms/01-polza-api.md` §4).
- Петля «тот же кадр в начале и в конце» у Veo не документирована; у Omni — документирована (§3.9).

### 3.5 Звук и реплики

- Реплики — в кавычках; эффекты — «SFX: thunder cracks in the distance»; фон — «Ambient noise: the quiet hum of a
  starship bridge» [S6].
- **Противоречие**: Vertex советует реплики без кавычек — «Avoid quotation marks: To prevent the model from rendering
  text in the video, use a colon (:) after the speaker's action… A woman says: My name is Clara.» [S10]. Для
  фоновых видео сайта реплик нет — вопрос снимается.
- Звук в Gemini API включён всегда [S7]; в polza у Veo параметра звука нет — немое видео получают при кодировании
  (агент I).

### 3.6 Таймкоды

- «Timestamp prompting»: `[00:00-00:02] …` — шаги по 2 с в 8-секундном ролике [S6].
- Omni: естественным языком («After 3 seconds, a woman enters») или `[0-3s] …` [S8].

### 3.7 Негатив

- **Поле `negativePrompt` есть в Vertex REST** («A string value that describes content that you want to prevent the
  model from generating») [S57]; в Gemini API и в polza — нет.
- Как заполнять поле: «Not recommended: using instructive language or words such as "no" or "don't"… Recommended:
  Describe what you don't want to see. For example, "wall, frame"» [S9].
- В тексте промта: «specify "a desolate landscape with no buildings or roads" instead of "no man-made structures"»
  [S6] — отрицание допускается внутри описания сцены.

### 3.8 Язык, переписчик, зерно

- **Язык**: «English (EN) is fully supported, but other languages have not been evaluated, so they may work but
  results can vary» [S7]. В polza `enableTranslation` по умолчанию `"true"` («Автоматический перевод промпта на
  английский») [S67] — русский промт переведёт агрегатор; точный английский надёжнее `[не проверено]`.
- **Переписчик** (Vertex, архив 2025-09-07): «Veo offers an LLM-based prompt enhancement tool, also known as a prompt
  rewriter… add video description, camera motions, transcription, and sound effects… You can't disable the prompt
  rewriter when using veo-3.0-generate-001 or veo-3.0-fast-generate-001. A rewritten prompt is delivered by API
  response only if the original prompt is fewer than 30 words long» [S11]. Для Veo 3.1 текущая документация статус
  переписчика не называет (открытый вопрос). Следствие: JSON или разделы у Veo переписываются LLM до генератора —
  спорить о форме бессмысленно, важны полнота и ясность.
- Cloud Blog советует прогонять промт через Gemini для обогащения («Prompt enhancement with Gemini») [S6].
- `seed` «doesn't guarantee determinism, but slightly improves it» [S7]; в polza — `seeds` 10000–99999.

### 3.9 Gemini Omni Flash: особенности диалекта

- **Негатив** — не поддерживается как поле: «negative prompts are not supported (you can put your negatives in the
  regular prompt: e.g., "Do not do X")» [S8]. Для лишнего: «No dialogue, No embellishments, No extra sound effects».
- **По умолчанию несколько планов**: для одного плана — «In a single unbroken scene / In a single continuous shot /
  No scene cuts» [S8].
- **Правки видео**: «Simple prompts work best for video editing. Overly descriptive prompts can lead to unintended
  changes» + «Keep everything else the same» [S8].
- **Музыку описывать явно**; текст в кадре — что написано на вывесках; «One word on the screen at a time…» [S8].
- **Мета-промтинг**: «Consider micro-detail, expression and timing…» [S8].
- **Продление**: +10 с до 40 с, контекст — последние 10 с [S8].
- **Теги ролей медиа** [S8]: `<FIRST_FRAME>`, `<LAST_FRAME>` (только вместе с `<FIRST_FRAME>`), `<IMAGE_REF_N>`
  (с нуля), `<VIDEO_REF_N>`; объявления `[# Sources …]` и `[# References …]`; закрывающие фразы «Use this image as
  the first frame and the last frame.», «Use the given image(s) as references for video generation. The images
  should not be used as literal initial frames.». Одна картинка на обоих концах — «creating a video that loops».
- В polza (`gemini-omni-video`, исполнитель `mie`) — дойдут ли теги до модели через обёртку KIE `[не проверено]`
  (фаза 5, отчёт D). **Поправка X 24.09.2026 (D2b):** preview `gemini-omni-video` снимается 30.09.2026; GA
  `google/gemini-omni-1.1-flash` (в polza с 23.09 17:45) принимает кадры полями `first_frame_url` + `last_frame_url` (URL
  хранилища; вопрос T9 фазы 0), теги ролей — синтаксис preview; референсы и кадры в одном вызове нельзя →
  `04-video-prompting.md` §3.1.

### 3.10 Примеры (дословно)

```text
// google/veo3_fast · пример Google Cloud Blog [S6] · polza 2026-09-23 · [документация]
Medium shot, a tired corporate worker, rubbing his temples in exhaustion, in front of a bulky 1980s computer in a
cluttered office late at night. The scene is lit by the harsh fluorescent overhead lights and the green glow of the
monochrome monitor. Retro aesthetic, shot as if on 1980s color film, slightly grainy.
```

```text
// Vertex AI Veo, поле negativePrompt · пример Vertex [S9] · нет в polza · [документация]
urban background, man-made structures, dark, stormy, or threatening atmosphere
```

```text
// gemini-omni-video · синтаксис петли Gemini API [S8] · polza 2026-09-23 · [документация] · в polza [не проверено]
[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]
Slow drifting fog moves across the still lake while the camera stays locked. In a single continuous shot. No scene
cuts. No dialogue.
Use this image as the first frame and the last frame.
```

Во втором и третьем абзаце третьего примера — формулировки Omni-гайда [S8], сюжет — наш.

### 3.11 В polza

| id | Цена ₽ | Режимы (`generationType`) | Картинки | Прочее |
|---|---|---|---|---|
| `google/veo3` | 187,50 за запрос | TEXT_2_VIDEO, FIRST_AND_LAST_FRAMES_2_VIDEO | ≤ 2 | `seeds`, `watermark`, `enableTranslation="true"` |
| `google/veo3_fast` | 45 за запрос | + REFERENCE_2_VIDEO (≤ 3) | ≤ 3 | то же |
| `gemini-omni-video` | 35–60 (720p, 4–10 с), 4k — 70 | t2v, i2v, reference, edit | ≤ 7 (картинки + видео × 2 + персонажи) | `audio_ids`, `character_ids`, `seed`; 16:9 и 9:16 |

Гайд polza по Omni: без описания движения «модель может выдать статичную сцену» [S66].

## 4. OpenAI — GPT Image 2.5 Sunburst / Flare, GPT Image 2, GPT Image 1.5, GPT-5 Image

GPT Image 2.5 Flare — малая модель (скорость, качество около GPT Image 2), Sunburst — базовая (качество выше GPT Image
2). `gpt-image-1.5` закрывается 2026-12-01, `gpt-image-1` — 2026-10-23 [S12]. Класс A (§1.1).

### 4.1 Восемь принципов OpenAI [S12]

1. **Определи результат**; «For complex requests, organize the prompt as scene, subject, details, and constraints,
   using labeled sections».
2. **Формат — удобный для поддержки** (§4.2).
3. **Видимые детали вместо настроения**; «Request "photorealistic" or "real photograph" explicitly»; «Treat camera
   specifications as cues for appearance, not a guarantee of exact physical simulation»; для широких, ночных и
   неоновых сцен — масштаб, атмосфера, цвет, а не только слова настроения.
4. **Люди**: «full body visible, feet included», «looking down at the open book», «hands naturally gripping…».
5. **Текст**: «Put required wording in quotes and describe its position and typography. Spell unusual words or brand
   names letter by letter when needed. Ask for no extra text, then check spelling and legibility.»
6. **Правки**: «say "change only X" and list the details to preserve… State exclusions such as unwanted text, logos,
   or watermarks.»
7. **Референсы**: «Identify each input by number and purpose: subject, style, clothing, or background.»
8. **Итерации**: одна правка за шаг, список сохраняемого повторять; «If a region must remain pixel-identical,
   composite the approved edit into the original image instead of relying on prompting alone.»

### 4.2 Формат промта: официальная позиция OpenAI

- «**Choose a maintainable format.** Short prompts, descriptive paragraphs, JSON-like structures, instructions, and
  tags can all express the same intent. Choose the format that makes the requirements easiest to read and update
  rather than relying on special syntax» [S12].
- Cookbook: «Minimal prompts, descriptive paragraphs, JSON-like structures, instruction-style prompts, and tag-based
  prompts can all work well as long as the intent and constraints are clear. **For production systems, prioritize a
  skimmable template over clever prompt syntax**» [S13].
- Порядок: «background/scene → subject → key details → constraints» + назначение («ad, UI mock, infographic»); для
  сложного — «short labeled segments or line breaks instead of one long paragraph» [S13].
- Реклама — «written like a creative brief rather than a purely technical image spec… let the model make
  taste-driven creative decisions inside those boundaries»; слайды и схемы — «written like an artifact spec» [S13][S12].
- Вывод для базы: у GPT Image JSON — законная форма, но без преимущества; компилятор отдаёт прозу по разделам
  (Scene / Subject / Style / Constraints) `[документация]`.

### 4.3 Композиция и место под текст

«If layout matters, call out placement (e.g., "logo top-right," "subject centered with negative space on left")»
[S13]. Ограничение из документации: «Composition Control: … difficulty placing elements precisely in structured or
layout-sensitive compositions»; «still struggle with precise text placement» [S14].

### 4.4 Текст в картинке

- «Put literal text in quotes or ALL CAPS… spell them out letter-by-letter» [S13]; ровно один раз — «Render the
  tagline exactly once, clearly and legibly» [S12]; «Include ONLY this card text (verbatim): "…"» [S13].
- Качество `medium`/`high` для мелкого текста [S12] — в polza у GPT Image 2.5 параметра `quality` нет (§4.9).
- Перевод: «Translate the text in the infographic to Spanish. Do not change any other aspect of the image.» [S13]
- Кириллица в MULTITEXTEDIT: GPT-image-1.5 теряет на неанглийских языках 0.517 балла (NB2 — 0.100) [S53]
  `[исследование]`; данных по GPT Image 2.5 нет.

### 4.5 Правки и маски

- «Masking with GPT Image is entirely prompt-based. The model uses the mask as guidance, but may not follow its exact
  shape with complete precision»; маска — PNG с альфой (прозрачное = заменить), при нескольких входах относится к
  первому; промт описывает **всю итоговую сцену** («a sunlit indoor lounge area with a pool containing a flamingo»)
  [S14].
- **В polza семантика другая**: `openai/gpt-5-image` `mask_url` — «Чёрные области = менять, белые = оставить» [S67];
  у `qwen/image-2.1` — наоборот (§7.6). Проверка полярности — в фазе 5 `[не проверено]`.
- Проверка результата: текст, сохранность формы и лица, «Did the edit change only what you requested?», альфа [S12].

### 4.6 Серия и референсы

Официальный пример серии персонажа — проза по разделам с повторяемым блоком «Character Consistency» (§4.8, пример
5) [S12]. Мульти-вход: «Image 1: product photo… Image 2: style reference…» [S13].

### 4.7 Переписывание промта

«When using the image generation tool in the Responses API, the mainline model (for example, gpt-5.5) will
automatically revise your prompt for improved performance» — поле `revised_prompt` [S14]. В Image API
(`images.generate`) о переписывании не сказано. Как вызывает polza (исполнитель `mie`) — неизвестно (открытый
вопрос). `openai/gpt-5-image` в polza имеет `isEnhance` («Улучшение промпта для 3D рендеринга и т.д.», по умолчанию
`false`) [S67].

### 4.8 Примеры (дословно, [S12])

```text
// openai/gpt-image-2.5-sunburst · пример OpenAI [S12] · polza 2026-09-23 · [документация]
Create a photorealistic candid photograph of an elderly sailor standing on a small fishing boat.
He has weathered skin with visible wrinkles, pores, and sun texture, and a few faded traditional sailor tattoos on his arms.
He is calmly adjusting a net while his dog sits nearby on the deck. Shot like a 35mm film photograph, medium close-up at eye level, using a 50mm lens.
Soft coastal daylight, shallow depth of field, subtle film grain, natural color balance.
The image should feel honest and unposed, with real skin texture, worn materials, and everyday detail. No glamorization, no heavy retouching.
```

```text
// gpt-image-2-5-flare · пример OpenAI [S12] · polza 2026-09-23 · [документация]
Give me a cool in culture ad / fashion shot for a brand called Thread.
It's a hip young street brand. The ad shows a group of friends hanging out together with the tagline "Yours to Create."
Make it feel like a polished campaign image for a youth streetwear audience: stylish, contemporary, energetic, and tasteful.
Use clean composition, strong color direction, natural poses, and premium fashion photography cues.
Render the tagline exactly once, clearly and legibly, integrated into the ad layout.
No extra text, no watermarks, no unrelated logos.
```

```text
// openai/gpt-image-2.5-sunburst · правка с референсом, пример OpenAI [S12] · polza 2026-09-23 · [документация]
Create a realistic billboard mockup of the shampoo on a highway scene during sunset.
Billboard text (EXACT, verbatim, no extra characters):
"Fresh and clean"
Typography: bold sans-serif, high contrast, centered, clean kerning.
Ensure text appears once and is perfectly legible.
No watermarks, no logos.
```

```text
// openai/gpt-image-2.5-sunburst · точечная правка, пример OpenAI [S12] · polza 2026-09-23 · [документация]
In this room photo, replace ONLY the white chairs with chairs made of wood.
Preserve camera angle, room lighting, floor shadows, and surrounding objects.
Keep all other aspects of the image unchanged.
Photorealistic contact shadows and fabric texture.
```

```text
// gpt-image-2-5-flare · продолжение серии, пример OpenAI [S12] · polza 2026-09-23 · [документация]
Continue the children's book story using the same character.

Scene:
The same young forest hero is gently helping a frightened squirrel
out of a fallen tree after a winter storm.
The character kneels beside the squirrel, offering reassurance.

Character Consistency:
- Same green hooded tunic
- Same facial features, proportions, and color palette
- Same gentle, heroic personality

Style:
Children's book watercolor illustration,
soft lighting, snowy forest environment,
warm and comforting mood.

Constraints:
- Do not redesign the character
- No text
- No watermarks
```

Прозрачный логотип у OpenAI требует и слов, и параметра: «Fully transparent background. Deliver a single centered
logo with generous padding, clean alpha edges, and no solid backdrop, scenery, checkerboard, or watermark» +
`background="transparent"`; «A drawn checkerboard is not transparency» [S12]. В polza параметра `background` у GPT
Image нет — прозрачность через polza даёт только `qwen/image-2.1` (§7.6).

### 4.9 В polza

| id | Цена ₽ (1K / 2K / 4K) | Референсы | Соотношения | Параметры кроме промта |
|---|---|---|---|---|
| `openai/gpt-image-2.5-sunburst` | 4 / 7 / 11 | ≤ 16 | 12 + `auto` (21:9, 27:16, 16:27, 9:8…) | `aspect_ratio`, `image_resolution`, `images` |
| `openai/gpt-image-2.5-flare` (до 25.09.2026 — `gpt-image-2-5-flare` без префикса) | 4 / 7 / 11 | ≤ 16 | то же | то же |
| `openai/gpt-5.4-image-2` | 4 / 7 / 11 | ≤ 16 | 5 + `auto` | то же |
| `openai/gpt-image-1.5` | `quality` medium 3 / high 16,5 | ≤ 16 | 1:1, 2:3, 3:2 | `quality` |
| `openai/gpt-5-image` | 4,50 | ≤ 5 | 1:1, 3:2, 2:3 | `mask_url`, `isEnhance` |
| `openai/gpt-5-image-mini` | по токенам (провайдер `openai`) | ≤ 10 | — | — |

Ни у одной модели OpenAI в polza нет `quality` (кроме 1.5), `background`, `moderation`, `input_fidelity` — параметры
прямого API OpenAI на polza не переносятся.

## 5. Black Forest Labs — FLUX.2 [pro] / [flex] / [max] / [klein] и FLUX 3

FLUX.2 принимает промт до 32K токенов [S16] (у FLUX.1 T5 — 512) — энкодер LLM-класса, класс B (§1.1). [klein] — 4B и
9B с открытыми весами; [max] — поиск в вебе для актуальных сюжетов; [flex] — «Specialized for typography» [S18].
FLUX 3 (единая модель картинки, видео и звука; вышла 2026-07-23, видео — ранний доступ) в polza на 2026-09-23 нет.

### 5.1 Формула, порядок, длина

- **Формула:** `Subject + Action + Style + Context`; «FLUX.2 pays more attention to what comes first»; приоритет:
  главный субъект → ключевое действие → критичный стиль → необходимый контекст → второстепенные детали [S15].
  Скилл BFL: `[Subject] + [Action/Pose] + [Style/Medium] + [Context/Setting] + [Lighting] + [Camera/Technical]` [S20].
- **Длина:** 10–30 слов — эскиз и стиль; 30–80 — «usually ideal»; 80–300+ — сложная сцена [S15][S16]. «Start
  short. Add only what changes the image. More words do not automatically mean better results» [S16].
- **Порядок меняет кадр**: «Person standing inside a forest fire…, close-up» получается шире, чем «Person with a
  strong determined expression, forest fire in the background, close-up shot» [S16].
- **Мусор вредит**: «Use one or two strong effects»; «Avoid stacking too many generic quality terms»; «Specific
  detail helps. Filler hurts» [S16]. Шаблон «[SUBJECT], [LOCATION], [STYLE], [CAMERA SETTINGS], [LIGHTING],
  [COLORS], [EFFECT], [ADDITIONAL ELEMENTS]» — «a prompt-building aid, not a rule» [S16].
- **Проза**: «Use natural language — Prose/narrative style works best» [S20].
- **Свет — главный рычаг**: «Lighting has the biggest impact on quality» [S20]; описывать источник, качество,
  направление, температуру, взаимодействие с поверхностями [S16].
- **Фото**: «Shot on Hasselblad X2D, 80mm lens, f/2.8, natural lighting»; «"Shot on Fujifilm X-T5, 35mm f/1.4"
  produces more authentic results than just "professional photo."» Эпохи: Modern Digital, 2000s Digicam, 80s
  Vintage, Analog Film (Kodak Portra 400) [S15][S16].
- **Метки стиля в конце**: «[Scene description]. Style: Country chic meets luxury lifestyle editorial. Mood: Serene,
  romantic, grounded.» [S16]

### 5.2 JSON: документировано, но с оговоркой

- «For complex scenes and production workflows, FLUX.2 interprets structured JSON prompts»; JSON — для продакшена,
  автоматизации, нескольких субъектов, независимой правки элементов; проза — для быстрых итераций, одного
  субъекта, творческих задач; «**FLUX.2 understands both formats equally well**—choose based on your workflow
  needs»; «You can include the JSON directly in your prompt, or flatten it into natural language» [S15][S17].
- **Базовая схема** [S15]: `scene`, `subjects[{description, position, action}]`, `style`, `color_palette[hex]`,
  `lighting`, `mood`, `background`, `composition`, `camera{angle, lens, depth_of_field}`; в примерах BFL ещё
  `camera{distance, focus, lens-mm, f-number, ISO}`, `subjects[].pose`, `subjects[].color_palette`,
  `color_match: "exact"`, `detail_preservation: "high"`; шаблон инфографики (`type`, `title`, `sections[]`,
  `color_scheme`).
- **Противоречие внутри BFL**: скилл `json-structured-prompting` — «**Flatten for Execution** — Convert to natural
  language before sending to model» (с примером перевода JSON в прозу) [S20]. Позиция базы: JSON — контракт системы,
  в FLUX.2 по умолчанию уходит проза по разделам, прямой JSON — плечо A/B `[спорно]`
  (`02-structured-json-prompting.md` §9).

### 5.3 HEX-цвета

- «Hex codes work best when clearly associated with specific objects. Vague references like "use #FF0000 somewhere"
  may produce inconsistent results»; сигнальные слова `color` / `hex` + код [S15].
- **С названием и не больше 3–5 цветов**: «Always Pair with Description: #FF6B6B (coral pink)», «Never use hex codes
  alone», «3-5 colors typically work best. Too many can confuse the model» [S20].
- **Градиенты**: начальный и конечный цвет; радиальный (центр и края); зоны неба (верх, середина, горизонт) [S15].
- **Перетекание цвета** → «the LEFT chair in #color»; удержание — «maintaining exact color #XXXXXX» [S20].
- Обещание вендора: «Specify brand colors via hex codes with precision matching. No approximation—get the exact colors
  you need» [S18] `[мнение вендора]`; независимой проверки нет — ΔE в фазе 5 (отчёт D, тест 7) `[не проверено]`.

### 5.4 Негатив: поля нет, «no X» не писать

- «**No negative prompts**: FLUX.2 does not support negative prompts. Focus on describing what you want… Instead of
  "no blur," say "sharp focus throughout." Instead of "no people," describe an "empty scene."» [S15]
- «writing "a person without glasses" causes the model to focus on "glasses" and often generate exactly what you were
  trying to avoid» [S16]; «Negative prompts can actually make models focus MORE on unwanted elements» [S20].
  Стратегия: найти нежелательное → спросить, что на его месте → описать это [S16].

| Вместо | Писать (таблицы BFL [S16][S20]) |
|---|---|
| no people | empty, deserted, solitary |
| no text | clean surfaces, unmarked, blank, text-free |
| no watermark / no logos | pristine image / unbranded |
| no blur | sharp focus throughout, tack-sharp |
| no clutter | organized, minimal |
| nothing in background | solid background, isolated subject, clean backdrop |
| no background distractions | smooth gradient background transitioning from deep blue to black |
| no bright colors | neutral tones, earth tones |
| not cartoonish / no CGI look | realistic, lifelike / photorealistic, authentic |
| not many | few, single, minimal |

- **Исключение у самого BFL — инструкции правки**: «Replace the DJ with a polar bear without headphones», «Keep only
  the original stone structure with no plants no moss no algae no green tint», «Change nothing else» [S18]; в видео
  FLUX 3 — «No on-screen text, no subtitles.» [S19] `[спорно]`.

### 5.5 Текст

- Кавычки, место, стиль шрифта словами, размер (large headline / small body copy), цвет hex: «The text 'OPEN' appears
  in red neon letters above the door»; «The logo text 'ACME' in color #FF5733» [S15].
- «Front-Load Text»; «Keep text short (1-4 words work best)»; «Use common words»; «Repeat the exact text in the
  prompt»; для чистой типографики — [flex] с 50 шагами и guidance 7 [S20] (в polza у `flux.2-flex` этих параметров
  нет).
- Текст как часть среды: «carved directly into the ancient stone wall» [S16]; в рекламной правке — «Add the text
  'Black Friday hasta -50%' on the right side, making sure it does not overlay the clothes» [S18].

### 5.6 Правки и мульти-референс

- **Коротко и конкретно**: «Change it to Night», «Change this to Winter»; хорошо — «Change the shirt color to red»,
  плохо — «Make it better / Improve the lighting / Make it more professional / Fix the image» [S18]; «Make it look
  better» → «Increase contrast, add warm color grading, sharpen details» [S20].
- **Явное сохранение**: «…while keeping the subject's pose, clothing, and expression exactly the same» [S20].
- **Сложную правку — цепочкой** из нескольких простых [S20].
- **Роли референсов по номеру**: «subject from image 1, style from image 2, background from image 3» [S15]; «Image 1:
  face/identity reference; Image 2: pose/body; Image 3: style/aesthetic; Image 4: environment/background»; «Apply only
  the color palette from image 2 to image 1, keeping all other aspects… unchanged»; дрейф лица → «maintaining exact
  likeness» [S20].
- **Лимиты**: [klein] до 4; [pro]/[max]/[flex] до 8 в API и 10 в песочнице; [pro] — 9 МП на вход и выход вместе (при
  выходе 1 МП — до 8 референсов, 2 МП — до 7) [S15][S18].

### 5.7 Апсемплинг и язык

- «FLUX.2 [pro], [max], and [flex] automatically enhance short prompts…» «On FLUX.2 [klein], what you write is what
  you get» [S16]; [klein] — «No prompt upsampling — be descriptive yourself», 40–70 слов [S20].
- **API BFL**: у [pro] и [max] — «apply prompt upsampling by default; set this to true to generate from your prompt
  exactly as written» (параметр `disable_pup`, по умолчанию `false`); у [flex] — `prompt_upsampling`, по умолчанию
  `true` [S18]. Значит, по умолчанию JSON или проза у FLUX.2 [pro] проходит через переписчик. В polza ни
  `disable_pup`, ни `prompt_upsampling` нет — если исполнитель передаёт умолчания BFL, апсемплинг включён
  (открытый вопрос); для A/B это означает «модель + переписчик» (`02-structured-json-prompting.md` §9).
- **Родной язык** для культурной достоверности: «more culturally authentic… than with translated English prompts»
  (примеры FR, TH, KO, IT, ES, DE; русского нет) [S17] `[мнение вендора]`. Независимо: у FLUX.1-Krea русский промт
  проваливается (0.44 против 0.77) [S63]; для FLUX.2 данных нет — тест 5 фазы 5.

### 5.8 FLUX 3 — видео (вне polza; образец диалекта)

- Четыре формы [S19]: однострочник «[camera] shot of [subject] [action] in [environment]. [supporting visual and
  motion details]» — «The best default»; поля с метками; таймлайн; YAML-схема для нескольких планов (Core summary /
  Scene / Subject description — «fixed, identical across shots» / Dynamic narrative по планам с секундами / Audio /
  Style and color) — «just one format, not a requirement».
- **Короткий против длинного**: короткий — свобода и «happy accidents», длинный — точность, но «Over-stuffing can
  make motion less coherent» [S19].
- **Камера**: «Start with one framing term, one movement term, and one clear subject action… "low tracking shot" is
  clear. "low aerial handheld orbit push-in" usually is not»; камеру можно не указывать [S19].
- **I2V**: стартовый кадр — самый буквальный режим; старт + конец — «a loop that must return to where it began»,
  «Keep the two frames related… The wider the gap… the more… unpredictability»; ключевые кадры — вехи [S19].

```text
// FLUX 3 video · поля с метками, пример BFL [S19] · нет в polza · [документация]
Camera shot: wide shot, low angle
Subject + action: a lone rider crosses a shallow desert river
Depth of field: shallow (sharp on subject, blurred background)
Lighting + palette: warm backlight with soft rim — amber, cream, walnut
Motion: water splashes around the horse's legs, orange dust hangs in the light
Style: epic western realism
```

```text
// FLUX 3 video · таймлайн, пример BFL [S19] · нет в polza · [документация]
0.0–1.5s — locked wide of a still harbor at dawn, boats motionless on glassy water
1.5–3.0s — a slow push-in begins as gulls lift off the water
3.0–5.0s — the sun breaks the horizon, warm light spreads and the camera settles
```

### 5.9 Скиллы BFL для агентов: бриф до промта и валидация

Репозиторий `black-forest-labs/skills` [S20][S21] — единственный найденный вендорский набор правил **для агентов**:

- **prompt-doctor**: «Resolve the decisions that change routing, payload, or production method before a brief becomes
  a prompt. Ask only blocking questions… Preserve the user's product names, exact copy, source roles, and hard
  constraints verbatim»; вердикт READY / NEEDS INFO / REVISE; бюджет действия — «one subject action and one camera
  move per short clip».
- **Противоречия, которые ловит валидатор** (дословно): «locked-off camera plus tracking; extreme close-up plus
  establishing view; exact frame preservation plus major geometric change; one continuous shot plus hard cuts;
  production-critical generated typography with no post fallback; guaranteed speaker identity across separate
  generations» → правила компилятора (`03-asset-spec-and-dialects.md` §12).
- **Точное — в постобработку**: «Reserve for deterministic post when exactness is a success condition: typography,
  subtitles, logos; frame-accurate sync; final mixing» — вендор подтверждает принцип базы «текст — кодом».
- **Шаблон брифа** `brief.md`: Outcome (Use, Audience/surface, Visible success condition) / Route / Shot (Subject,
  One required action, Environment, Opening frame, Payoff/closing frame, Shot structure, Continuity invariants) /
  Camera and Look / Timing / Audio / **Text: Strategy — absent / spoken / physical in-scene / generated /
  deterministic post; Exact copy; When and where** / Production Boundaries (**First iteration variable**).
- **cinematic-inserts**: «Camera is one physical contract: framing, angle, movement, focus. A locked-off camera cannot
  track; an extreme close-up cannot establish. Locked and deliberate by default»; «**Style must be visible**: "tense"
  becomes rigid posture…; "vintage" becomes a named capture format, grain structure, and practical light»; «After
  two structurally similar misses, change the concept or the production method, not the adjectives»; порядок
  промта: Opening frame → Visible cause → Physical response → Payoff → Continuity contract («same set and geometry;
  no cuts, transitions, frozen or repeated frames, or resets») → Audio intent.
- **keyframes-continuation**: «One keyframe: the image opens the clip. Prompt what moves; **redescribing visible
  pixels invites re-imagination**.» «Two keyframes: opening and closing are pinned, so describe the stages of the
  change in order and hold the camera still. Keep the two ends related enough for a plausible path; large jumps
  invite drift»; продолжение — «write from the ending… do not recap completed action».
- **field-guide** — в «парковку» (не делать генерацией): «graphic sans-serif overlays and late-shot text», «CJK text
  as featured legible copy».

### 5.10 Примеры (дословно)

```text
// black-forest-labs/flux.2-pro · hex, пример BFL [S18] · polza 2026-09-23 · [документация]
A vase on a table in living room, the color of the vase is a gradient of color, starting with color #02eb3c and
finishing with color #edfa3c. The flowers inside the vase have the color #ff0088
```

```text
// black-forest-labs/flux.2-pro · hex по местам, пример BFL [S18] · polza 2026-09-23 · [документация]
Luxury eyeshadow palette with 6 pans: top row #B76E79, #E8D5B7, #8B4789; bottom row #CD7F32, #F8F6F0, #800020
```

```json
// black-forest-labs/flux.2-pro · структурированный промт, пример BFL [S18] · polza 2026-09-23 · [документация]
{
  "subject": "Mona Lisa painting by Leonardo da Vinci",
  "background": "museum gallery wall, ornate gold frame",
  "lighting": "soft gallery lighting, warm spotlights",
  "style": "digital art, high contrast",
  "camera_angle": "eye level view",
  "composition": "centered, portrait orientation"
}
```

```text
// black-forest-labs/flux.2-pro · 6 референсов, пример BFL [S18] · polza 2026-09-23 · [документация]
Create a house for the chickens from image 1 using materials from images 2, 3, 4, and 5. Use the wood from image 5
for the base, the materials from images 2 and 4 for the walls and floor, and the material from image 3 for a small
pillow nest. Place the chickens from image 1 in their new home, sitting on the pillow nest. Next to them, include
the eggs from image 6. Apply the style of image 1 to the entire new scene.
```

```text
// black-forest-labs/flux.2-pro · правка цвета hex, пример BFL [S18] · polza 2026-09-23 · [документация]
Change the cow's white fur to the color #8bc4bb and its black spots to #de4528
```

### 5.11 В polza

| id | Цена ₽ (1K / 2K) | Референсы | Соотношения | Нет в polza (есть в API BFL) |
|---|---|---|---|---|
| `black-forest-labs/flux.2-pro` | 5 / 7 | ≤ 8 | 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3 | `seed`, `disable_pup` (апсемплинг включён по умолчанию), `safety_tolerance`, `output_format` |
| `black-forest-labs/flux.2-flex` | 14 / 24 | ≤ 8 | то же | `seed`, `prompt_upsampling` (по умолчанию `true`), `steps`, `guidance`, `safety_tolerance`, `output_format` |

При правке без `aspect_ratio` выход берёт пропорции исходника [S66]. [max] и [klein] в polza нет.

## 6. ByteDance — Seedream 4 / 4.5 / 5 и Seedance 1.5 Pro / 2.0 / 2.5

Гайды BytePlus ModelArk (сняты 2026-09-23, обновления Seedance 2.0/2.5 — 2026-09-22) [S22]–[S26], [S59].

### 6.1 Seedream 4.0 / 4.5 / 5.0 (картинки)

- **Связный язык: субъект + действие + среда**, для эстетики — стиль, цвет, свет, композиция [S22]. Рекомендовано:
  «A girl in a lavish dress walking under a parasol along a tree-lined path, in the style of a Monet oil painting.»
  Не рекомендовано: «Girl, umbrella, tree-lined street, oil painting texture.»
- **Назначение** в промте: «Design a logo for a gaming company… The company name "PITBULL" is written on it.» [S22]
- **Кратко и точно**: 4.x понимает лучше 3.0, поэтому «using concise and precise prompts is usually better than
  repeatedly stacking ornate and complex vocabulary» [S22]; «Keep text prompts under 600 English words. Very long
  prompts may scatter the information» [S23]. Сложные сцены вендор описывает перечнем мест («Top shelf: On the
  left… Middle shelf…») [S22].
- **Текст — в двойных кавычках**: «Use double quotation marks for the text that needs to appear»; не рекомендовано:
  «Generate a poster titled Seedream 4.5.» [S22]
- **Правки — однозначно и с сохранением**: «Dress the tallest panda in pink Peking Opera costume and headgear, keeping
  its pose unchanged.» Не рекомендовано: «Put that one in pink clothes.» (расплывчатые местоимения) [S22].
- **Правка визуальными метками** (стрелки, рамки, каракули на входной картинке): «Insert a TV where the red area is
  marked and a sofa where the blue area is marked. Keep the original wooden style.»; «Enlarge the title to match the
  red box» [S22] — альтернатива маске.
- **Референсы**: «Reference Target» (что взять) + описание новой сцены; «replace the character in Image 2 with the
  character from Image 1, and generate the result in the style of Image 3»; «Apply the style of Image 2 to Image 1.»
  [S22]
- **Скетч → чистовик**: «Generate based on the text in the image»; «The room layout and furniture placement should
  exactly match the reference»; «Do not include any text or hand-drawn edges from the original sketch.» [S22] — вендор
  сам пишет «Do not include».
- **Серия**: «trigger series generation with phrases like "a series", "a set", or by specifying the number of
  images» [S22]; в API BytePlus — `sequential_image_generation: auto` + `max_images`; **в polza этих параметров
  нет** — одна картинка на запрос.
- **Серия иконок по стилю**: «Referencing the linear minimalist style of icons, design 9 application icons… while
  maintaining a consistent color scheme.» [S22]
- **Встроенный оптимизатор**: `optimize_prompt_options.mode` — `standard` (по умолчанию) или `fast` [S23]; в polza
  параметра нет, применяет ли его исполнитель — неизвестно.

### 6.2 Seedance 1.5 Pro (и 1.0)

- Язык промта: «Support Chinese and English» [S24][S59].
- **Формула**: `Subject + Movement + Environment (opt) + Camera movement (opt) + Aesthetic description (opt) + Sound
  (opt)`; наречия степени («slowly», «gently»); один субъект — одними и теми же признаками [S24].
- **Грамматика крупности**: «Subject + Shot Size (e.g., Close-up of the man on the left)»; **формула движения камеры**:
  «Starting frame composition description + Shot movement + Shot movement amplitude + Ending frame composition
  description»; движения dolly-in / out, pan, track, follow, rise, fall, whirl, rotate, surround, zoom; комбинации
  (Hitchcock = dolly + zoom) [S24]. Seedance 1.0 «can accurately respond to camera movement prompt, such as Tracking
  Shot, Pan Left/Right, Truck Left/Right»; в примере с движением камеры — `--camerafixed false` [S59].
- **Звук** (если включён): реплики в кавычках с эмоцией, тоном и темпом; языки — китайский с диалектами, английский,
  японский, корейский, испанский, индонезийский — **русского нет**; «By default, Seedance 1.5 Pro automatically
  generates background music» [S24].
- **Несколько планов**: «The shot begins with… The scene cuts to… The camera then cuts back to…» или «Shot 1: …
  Shot 2: Cut to…» [S24].
- **i2v продукта**: «Generate a video based on the input lipstick product keyframe image, keeping the appearance,
  proportions, and materials… accurate and consistent, with no unnecessary elements added.» [S24]
- Устаревшие флаги в тексте промта (`--rs 720p --rt 16:9 --dur 5 --seed 11 --cf false --wm true`) заменены
  параметрами тела [S24]; в polza — `fixed_lens`, `generate_audio`, `resolution`, `duration`.

### 6.3 Seedance 2.0 (2 / Fast / Mini)

- **Ссылки на ассеты**: `<Image_N>` или «@Image 1»; «Reference <Subject_N> in <Image_N>…», «Reference
  <Action/Camera_movement/Style/Sound_effect> in <Video_N>…», «Reference the timbre in <Audio_N>…»; для правки и
  продления — «<Video_N>» напрямую, без «reference», иначе задача распознаётся как референсная [S25].
- **Определение субъекта**: «Define the woman wearing a red dress and a straw hat in Image 1 as Subject 1» — 2–3
  устойчивых признака, дальше та же метка [S25].
- **Расширенная формула**: точный субъект + детали действия + сцена + свет и тон + движение камеры + визуальный
  стиль + качество + ограничения — «engineering-style instruction» [S25].
- **Таймкоды не держит**: «The model's support for precise timing (such as 0–3 seconds) is unstable, and forcibly
  limiting duration may lead to abnormal generation results» — только «Shot 1 / Shot 2 / Shot 3» [S25]; скилл вендора
  `sd2-pe` при этом сам пишет «0–3s, 3–10s» → `[спорно]` (`04-video-prompting.md` §5.1) [поправка X 24.09.2026 по D2b].
- **Движение**: «Prioritize slow, gentle, continuous small movements… avoid high-burst, large-dynamic actions»; «Try to
  specify only 1 type of camera movement in a single shot»; эмоции — через физические детали [S25].
- **Ограничения словами** (вендор рекомендует отрицания): «keep it subtitle-free», «avoid generating any text or
  subtitles», «do not generate a logo», «do not generate a watermark»; субтитры на 100 % не убираются;
  **горизонтальный формат снижает вероятность субтитров**; текст из референсов убирать заранее [S25].
- **Скобки по типу звука и текста**: музыка `（…）`, звуковой эффект `<…>`, реплика `{…}`, субтитры `【…】`; не
  смешивать языки в одной реплике [S25].
- **Ассетов 4–5**: «It is not recommended to use the full asset limit»; лицо — отдельный крупный план + полный рост,
  мульти-ракурс не советуют (дрейф лица) [S25].
- **Стыки продления**: отрезать 6 последних кадров предыдущего и 1 первый кадр следующего [S25].
- **Текст в кадре**: «[Text Content] + [Timing] + [Positioning] + [Entrance/Appearance Style], [Visual Attributes]»;
  «prioritize common characters and avoid rare characters» [S25].

### 6.4 Seedance 2.5

- Вендор: «We strongly recommend using the Seedance 2.5 Skill to optimize your prompts» (`sd25-pe`, вне API) [S26].
- **Структура промта**: Asset Referencing → One-Sentence Summary (субъект + место + событие + жанр/стиль + движение
  камеры) → Detailed Plot (Shot N или таймкоды) → Additional Notes (постоянные элементы) [S26].
- **Таймкоды держит**: единица 1 с, без разрывов; «0-3 seconds… 3-7 seconds…», «[1s-4s]…», «At the 2-second mark…»,
  «After 3 seconds…»; не дробить таймкодами частые действия [S26]. 2.0 и 2.5 различаются эстетикой — в одной серии не
  смешивать [S26].
- **Негатив**: «Use positive descriptions whenever possible. Negative constraints are supported for subtitles and
  audio control, such as "no subtitles" and "no BGM."» Если «no BGM» нарушается — перечислить все синонимы (music,
  background music, BGM, score, instrumental, melody…) и повторить запрет в начале и в конце [S26].
- **Разделы в скобках** в примере вендора: `[Subject settings]` / `[Overall style]` / `[Strictly exclude]`
  («Black-and-white, monochrome… plastic CG, glossy overexposed CG.») / `[Shot list]` [S26].
- **Не пересказывать точный референс**: «When the reference asset itself is sufficiently accurate, simply state that
  it should be referenced and avoid repeatedly describing the scene» — «Strictly refer to the actions and camera
  movements in Video 1» [S26].
- **Правка видео**: «Change the man's action from drinking coffee to mopping the floor from 4-6 seconds in Video 1,
  and leave the rest of the content unchanged.» [S26]
- **Камера**: базовые термины напрямую, редкие — «[term + descriptive explanation]» [S26].
- **Орфография текста**: разбить слово на буквы, появляющиеся по очереди, или «Prepare the text that must be rendered
  accurately as an image and provide it as a reference asset» [S26] — приём для кириллицы `[не проверено]`.
- **Прочее**: убрать из промта «water, waves, echoes» против звуковых артефактов; AI-референсы высокого разрешения
  дают «fingerprint-like textures» — уменьшать вход до разрешения выхода; сложное — дробить [S26].

### 6.5 В polza

| id | Цена ₽ | Промт ≤ | Референсы | Важно |
|---|---|---|---|---|
| `bytedance/seedream-4` | 3 | 5 000 | ≤ 10 | `seed`; 1K / 2K / 4K |
| `bytedance/seedream-4.5` | 5 | 3 000 | ≤ 14 | `quality` basic (2K) / high (4K) |
| `bytedance/seedream-5-lite` | 4 | 2 996 | ≤ 10 | `quality` basic 2K / high 3K |
| `seedream/5-pro-text-to-image` | 5 (basic) / 10 (high); +0,3 за доп. референс | не указан | ≤ 10 | `output_format` |
| `bytedance/seedance-1.5-pro` | 5,25 (480p, 4 с, без звука) … 135 (без параметров) | 2 500 | ≤ 2 (первый/последний) | `fixed_lens`; `generate_audio` по умолчанию `false` |
| `bytedance/seedance-2` | 12,825 ₽/с (480p) … 83,7 ₽/с | 20 000 | ≤ 5 + видео 1 | `generate_audio` по умолчанию `"true"`, длительность по умолчанию 15 с |
| `bytedance/seedance-2-fast` | 10,46 ₽/с (480p) / 22,28 (720p) | 20 000 | ≤ 5 + видео 1 | то же |
| `bytedance/seedance-2-mini` | 2,565 ₽/с (480p) … 6,75 | 20 000 | ≤ 9 + видео 3 | то же |
| `bytedance/seedance-2-5` | 18,9 ₽/с (480p) … 51,3 | 30 000 | ≤ 30 + видео 10 | то же |

Полные цены и ловушка «запрос только с промтом у Seedance 2 = 415 ₽» — `../02-providers-platforms/01-polza-api.md`
§8.2. Роли `first_frame` / `last_frame` из API BytePlus в polza не выставлены — какой из двух `images` станет
последним кадром, проверять `[не проверено]`.

## 7. Alibaba — Qwen-Image, Wan, Z-Image, HappyHorse

### 7.1 Qwen-Image 2 / 2.1 (картинки)

- **Язык**: «Supports Chinese and English» (Model Studio) [S29]; в каталоге polza у `qwen/image-2.1` — «Любой язык, до
  5000 символов» [S67]. У Model Studio лимит 800 токенов (qwen-image-2.0 — 1 300) [S29] — в polza больше.
- **Обучение** (техотчёт): подписи трёх видов — сырые короткие («robustness in handling short text inputs»),
  переписанные Qwen-VL («more descriptive and structured annotations») и смешанные; разметчик «concurrently describes
  visual content and generates detailed information in a structured format, such as JSON»; 27 % данных — дизайн
  (постеры, UI, слайды); синтетика по шаблонам PPT и UI — «to follow complex, structured prompts involving
  layout-sensitive content» [S65]. Модель видела и короткие, и длинные, и структурные описания — устойчива к форме
  `[исследование]`.
- **Негатив** в Model Studio есть (`negative_prompt` ≤ 500 символов), в polza у Qwen — нет. Пример вендора — §7.5.
- **Смещение к китайскому**: примеры вендора сами запрещают иероглифы — «All on-image text must be in English only,
  with no Chinese characters, no misspellings»; «No Chinese characters, no Chinese painting style, no seals, no
  stamps… no illegible glyphs, no random letters» [S29]. Для кириллицы — явно «All on-image text is in Russian
  (Cyrillic script)» `[не проверено]`.
- **Текст**: README — «exceptional performance in text rendering, especially for Chinese»; «магический» хвост
  `, Ultra HD, 4K, cinematic composition.` и `negative_prompt = " "` в примерах кода [S31].
- **Qwen Image 3.0** — флагман Model Studio 2026; в polza нет.

### 7.2 Переписчики Qwen: что они делают с промтом

- **`prompt_extend`** в Model Studio включён по умолчанию («smart prompt rewriting… Disable it if you need tighter
  control», +3–5 с); переписчик сам дописывает «Style: ultra-realistic photography… Canon EOS R5, f/1.2… No text or
  overlays.» [S29]. В polza — `enhance_prompt`, по умолчанию `false`, +10–30 с [S67].
- **Правки без переписчика нестабильны**: «We have observed that editing results may become unstable if prompt
  rewriting is not used. Therefore, we strongly recommend applying prompt rewriting to improve the stability of editing
  tasks» (Qwen-Image-Edit) [S31] → для правок в polza кандидат `enhance_prompt: true` `[не проверено]`.
- **Системные промты переписчиков** (открыты в репозитории [S31]) — это и есть «родной» диалект модели:
  - `prompt_utils.py`: язык определяется по наличию иероглифов, иначе — английская ветка (русский промт пойдёт туда);
    текст в кавычках с местом и стилем, «This text should remain unaltered and not translated»; до 200 слов.
    Китайская ветка, правило 8: «改写之后的prompt中不应该出现任何否定词» — в переписанном промте не должно быть
    отрицаний: если пользователь пишет «без палочек», палочки не упоминаются вовсе; правило 9 — без лишнего текста.
  - `prompt_utils_2512.py` (Qwen-Image-2512, новее): **всегда переписывает на английский**; «Use fluent, natural
    descriptive language… Strictly avoid formal Markdown lists…, numbered items, or headings»; весь текст — в двойных
    кавычках с позицией, направлением, шрифтом, цветом, размером и способом (printed, neon…); «For non-English text…
    retain the original text and specify the language»; без текста — «The image contains no recognizable text.»;
    примеры заканчиваются «No other text appears in the image.»; сцена — по планам (передний, средний, дальний),
    свет, фактуры; портрет ~200 слов. В примерах есть отрицания («No people, animals, or man-made structures beyond
    the trail markers are present.») — позиция вендора сменилась между версиями `[спорно]`.
  - Переписчик правок (Qwen-VL-Max): «Replace Y with X» + признаки X; надпись — в двойных кавычках, язык и регистр
    сохраняются; сохранение личности — «keep smile, short hair, and gray jacket unchanged»; фиксированные шаблоны
    реставрации, инпейнта и аутпейнта (§7.5).
- **Вывод**: родной диалект Qwen-Image — английская проза без Markdown, надпись в кавычках с указанием языка, финальная
  фраза «No other text appears in the image.»; разделы с метками — не его форма `[документация]`.

### 7.3 Wan 2.5 / 2.6 / 3.0 (видео)

- **Формула**: базовая Entity + Scene + Motion; расширенная — + Aesthetic control + Stylization: «Most weak prompts
  cover entity and motion but skip aesthetic control and stylization — producing a static camera in an undefined
  void» [S27].
- **Смысл движений камеры** [S27]: push-in — близость и напряжение; pull-out — масштаб и одиночество; tracking —
  зритель рядом; orbit — значимость; fixed — неподвижность и фокус. Облёт: «Keep the arc under 45 degrees — wider
  orbits risk spatial distortion».
- **Image-to-video — движение и камера**: «The image defines the entity, scene, and style. Your prompt should focus on
  motion and camera movements»; промт = Motion + Camera movement; «To keep the camera still, use "fixed camera."»
  [S27].
- **Звук** (Wan 3.0/2.7/2.6/2.5): голос = реплика + эмоция + тон + темп + тембр + акцент; эффект = источник + действие
  + фон; музыка = музыка + стиль [S27].
- **Несколько планов** (3.0/2.7/2.6): общее описание + номер плана + таймкод + содержание («Shot 1 [0–3 s] …», «Hard
  cut transition, fixed camera position…»); у Wan 2.7 без `shot_type` — «To generate a single-shot video, write
  'Generate single shot.'» [S27]. В polza у `wan/2.6` есть `multi_shots` (по умолчанию `"false"`).
- **Референсы** (3.0/2.7): «Image n» / «Video n» — по-английски с заглавной и пробелом, нумерация по порядку загрузки,
  картинки и видео отдельно; «To suppress lines entirely, write 'No dialogue.'» «To suppress background music, write
  'No background music.'» [S27].
- **Что не писать**: имена реальных людей; быструю смену сцен в одном клипе; точную читаемость текста («Text renders
  approximately»); длинную хореографию; синхрон губ со словами [S27].
- **Эстетический контроль** (примеры Wan 2.2): голова из тегов + проза — «Rim light, low contrast, medium close-up,
  daylight, left-heavy composition, clean single shot, warm tones, soft light, … A young girl sits…»; словарь:
  источник (daylight, firelight, overcast), тип света (soft, hard, side, high contrast), крупность, композиция
  (center, left-heavy), объектив (long-focus, fisheye), ракурс (OTS, high-angle, aerial), тип плана (clean single
  shot, two-shot, establishing), тон (warm, low saturation) [S27].
- **Wan 3.0 — проза по разделам** в официальных примерах [S28]: «Story Synopsis / Scene Description and Lighting
  Aesthetics (… Color aesthetics: Strictly follows a bright "teal-orange" color scheme…) / Characters and Scene /
  Camera Movement Style Description / Shot-by-shot Description (0s - 8s: …)»; i2v — «(0:00 - 0:03) Camera: Medium
  shot. Scene: … Action: … Atmosphere: …»; первый + последний кадр — заголовок в скобках «[One continuous take, slow
  aesthetic camera movement, no cuts, 15-second long shot, …]» + «Global setting:» + «Audio and sound effects:» +
  «[0-3s: A water drop] …». Во всех примерах `prompt_extend=True`.
- **Wan t2i** (V2): Subject + Setting + Style (+ Camera + Atmosphere + Detail modifiers), примеры — списки тегов;
  `prompt_extend` по умолчанию `true` — «Keep the default for best results» [S30].

### 7.4 Z-Image (Tongyi-MAI) и HappyHorse

- **Z-Image** — официального гайда по промтам нет; первичные источники — техотчёт [S32] и README [S64]. Подписи
  обучения пяти типов (длинные, средние, короткие, теги, «симулированные промты пользователя»); длинные — «plain and
  objective linguistic style… strictly confining them to factual information observable in the image»; энкодер —
  Qwen3-4B. **Модель выровнена на свой усилитель**: «we process all input prompts… through our PE model during the
  SFT stage» [S32] — в polza усилителя нет, значит плотное фактическое описание пишем сами (≤ 1 000 символов).
- Многоязычие — «initially emerged» [S32]; надписи — «Accurate Bilingual Text Rendering» (китайский и английский)
  [S64]; кириллицу в картинке у Z-Image не просить `[не проверено]`.
- Негатив: у Turbo `guidance_scale=0.0` («Guidance should be 0 for the Turbo models») — CFG выключен, негатив не
  действует; у базовой модели негатив «Strongly recommended» [S64]. В polza поля нет, какой вариант отдаёт
  исполнитель — неизвестно.
- **HappyHorse 1.0 / 1.1** — гайда не найдено; у исполнителя «Exactly one image is required» (первый кадр, данные
  агента C2). Писать по правилам i2v Wan (§7.3) `[мнение]`.

### 7.5 Примеры (дословно)

```text
// Qwen-Image, поле negative_prompt · пример Model Studio [S29] · в polza поля нет · [документация]
Low resolution, low quality, distorted limbs, malformed fingers, oversaturated colors, wax-like appearance, no facial
details, overly smooth surfaces, AI-generated look. Chaotic composition. Blurry or distorted text.
```

```text
// qwen/image-2.1 · шаблоны переписчика правок Qwen [S31] · polza 2026-09-23 · [документация]
Perform inpainting on this image. The original caption is: <описание исходной картинки>
Extend the image beyond its boundaries using outpainting. The original caption is: <описание исходной картинки>
Restore and colorize the photo.
```

```text
// qwen/image-2.1 · концовки переписчика Qwen-Image-2512 [S31] · polza 2026-09-23 · [документация]
The image contains no recognizable text.
No other text appears in the image.
```

### 7.6 В polza

| id | Цена ₽ | Промт ≤ | Референсы | Важно |
|---|---|---|---|---|
| `qwen/image` | 2,25–3 (по соотношению) | не указан | ≤ 1 | `guidance_scale` 0–20 (2,5), `strength` 0–1 (0,8) |
| `qwen/image-2` | 4 | 5 000 | ≤ 3 | — |
| `qwen/image-2.1` | 3 (1K) / 6 (2K) | 5 000 | ≤ 10, «Порядок — тот, на который ссылается промпт» | `mask_url` «белое — менять, чёрное — оставить» (только с одним референсом, несовместима с прозрачностью); `background: transparent`; `enhance_prompt` (`false`); `seed` |
| `tongyi-mai/z-image` | 1,40 | 1 000 | 0 | 5 соотношений |
| `wan/2.5` | 45–150 | 800 | ≤ 1 | **`negative_prompt` ≤ 500** — единственный в каталоге; `enable_prompt_expansion` (`"false"`); `seed` |
| `wan/2.6` | 52,5–236 | 5 000 | ≤ 1 | `multi_shots` (`"false"`) |
| `alibaba/wan-3.0` / `-prime` | 23,6 / 33,0 ₽/с | не указан | ≤ 1 | `generate_audio` (`"false"`), `seed`, 2–30 с |
| `alibaba/happyhorse-1.0` / `-1.1` | 20,0 / 15,1 ₽/с | не указан | ≤ 1 | `seed`, 3–15 с |

## 8. Kuaishou — Kling 3.0 / 2.6

- **Гайд Kling VIDEO 3.0** (2026-02-06) [S33]: 3–15 с; авто-мульти-шот и Custom Multi-Shot (планы с длительностью);
  элементы-референсы (2–4 картинки или видео 3–8 с с голосом); реплики на 5 языках — «If dialogue is entered in a
  language other than those listed above, the model will translate it into English» → **русская реплика станет
  английской**; надписи исходной картинки сохраняются («native-level text»).
- **Примеры вендора — плотная проза с точками времени**: «At the 4th second… At the 8th second… In the final 3
  seconds…», «one continuous long take without any cuts», «The camera remains fixed on the word "KLING" emblazoned on
  the baseball bat»; Custom Multi-Shot — «shot 1, profile shot of…, cinematic handheld. Shot 2, …» [S33].
- **API 3.0** [S34]: вход `contents` (`prompt`, `first_frame`, `last_frame`, `element`); **«The prompt can include
  positive and negative descriptions»** — отдельного поля негатива в 3.0 нет; текст до 3 072 символов, рекомендовано
  ≤ 2 500; мульти-шот в тексте — «shot n, m, words; shot n, m, words;» (n = 1–6, m — секунды ≥ 1, сумма = длительность,
  words ≤ 512 символов); элементы — `@Name` (имена не должны быть подстроками друг друга).
- **Omni-гайд** [S62]: «@Boxer A…», «Shot 1 (2s): Wide shot, …», ссылка на картинку — «@Image».
- **Блог Kling** (2026-08-07) [S35]: Subject / Action / Scene / Camera / Lighting and Mood; движение — видимое
  («smoke drifting upward»); «[Shot 1: Wide shot] …»; текст — «write the exact words, placement, surface, and camera
  distance. Keep the text short when readability matters»; вариации — от одного базового промта по одной оси.
- **Kling IMAGE 3.0** (нет в polza): до 10 референсов; шаблоны правок «Generate [view] of the subject.», «Change the
  shooting angle to [ ]», «Change the shot size to [ ]», «Change the lighting and shadow to [ ]», «Change the color tone
  to [ ]» [S33].
- **В polza**: `kling/v3` — промт ≤ 2 500, `images` 0–2 («Start/end frame (single-shot) или start frame
  (multi-shot)»), `mode` std / pro / 4K, `sound` обязателен (по умолчанию `"false"`), 10–45 ₽/с; параметра
  `multi_shots` в каталоге нет (упомянут только в описании `sound`); у вендора `multi_shot` по умолчанию `true`, в polza
  с двумя кадрами — одноплановый режим («start frame (multi-shot)» — только стартовый), для фона — «one continuous shot»
  (`04-video-prompting.md` §5.2; одноплановость по умолчанию — вопрос T9) [поправка X 24.09.2026 по D2b]; `kling/v2.6` — 5 / 10 с, 42–165 ₽;
  `kling/v3-motion-control`, `kling/v2.6-motion-control` — движение переносится из видео. **Kling 2.5 Turbo с
  `negative_prompt` и `cfg_scale` описан в документации polza, но в каталоге 2026-09-23 его нет** [S66][S67].

## 9. MiniMax — Hailuo 2.3 и H3 / H3 Max

- **Команды камеры** (API Hailuo 2.3 / 02, I2V-01-Director) [S36]: 15 команд в квадратных скобках — `[Truck left]`,
  `[Truck right]`, `[Pan left]`, `[Pan right]`, `[Push in]`, `[Pull out]`, `[Pedestal up]`, `[Pedestal down]`, `[Tilt
  up]`, `[Tilt down]`, `[Zoom in]`, `[Zoom out]`, `[Shake]`, `[Tracking shot]`, `[Static shot]`; одновременные — в одних
  скобках `[Pan left,Pedestal up]` (рекомендовано ≤ 3); последовательные — «…[Push in], then…[Push out]»; «Free-form
  descriptions also work, but explicit commands yield more accurate results». Промт ≤ 2 000 символов;
  **`prompt_optimizer` по умолчанию `true`** — «Set to false for more precise control» [S36].
- **H3 / H3 Max** (гайд MiniMax) [S37]: H3 — 768P / 2K, 4–15 с; H3 Max — 480P / 768P, 5–15 с; первый и последний кадр
  (0–2 картинки), референсы ≤ 9 картинок, ≤ 3 видео, ≤ 3 аудио; промт ≤ 7 000 символов; t2v — «add camera motion
  instructions (e.g., [pan], [zoom], [static]) directly after key descriptions».
- **H3-Context-IR** — вендорский препроцессор: «deeply interprets multimodal context… and produces a structured
  representation with richer semantic detail while preserving the user's original intent» [S37]. README открытой H3:
  «**H3-Context-IR is critical to the quality of the final output**, so we strongly recommend incorporating it into
  your generation pipeline or following the "Prompting Guidance" to build your own context-processing system» [S38].
  Формат IR — текст с полями в snake_case: `integrated_multimodal_description: [Shot 1] … [Shot 2] At 00:04.500, the
  camera cuts to…`, `overall_soundscape:`, `non_diegetic_music:`; для референсов — `subject_definitions:`, `summary:`,
  `retention_analysis:`, `detailed_description:`; IR раздувает промт до 5 650–33 323 токенов в примерах [S38]. Класс D
  (§1.1): проза без IR — вход «не того формата».
- **Скилл `h3-prompt-writing`** [S38]: режимы T2VA / I2VA / FL2VA / L2VA; фиксированные первые строки — I2VA: «For the
  target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.»; FL2VA: «How
  the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of
  the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.» (S.SS — ровно два
  знака). «FL2VA generally favors a single shot»; тело FL2VA — «first-frame state → observable intermediate changes →
  progressively narrowing differences → last-frame state», без повтора двух статичных описаний.
- **Камера = тип + амплитуда + скорость** [S38]: Zoom In/Out, Push In/Pull Out, Pan, Truck, Tilt, Pedestal, Arc Shot,
  Tracking, Static, Shake Slightly/Strongly, POV, Roll; «The camera pushes in with small amplitude at slow speed
  toward…», «The camera holds a static shot as…».
- **Текст и звук** [S38]: надпись на экране — в английских двойных кавычках, дословно, без перевода («A red neon sign
  reading "营业中"»); реплика — `(S1)` + `<d>[English] …</d>` на исходном языке; музыки нет — `non_diegetic_music: N/A`;
  разделы — по-английски; «Prefer concrete visual and audio details over abstract words like "cinematic" or
  "beautiful"».
- **В polza**: `minimax/hailuo-3-max` (провайдер openrouter; «post-trained by fal.ai on MiniMax H3») — 9,44 ₽/с,
  480p / 768p, 5–15 с, `images` ≤ 2 (первый и последний кадр); **лимита длины и `prompt_optimizer` в каталоге нет** —
  применяет ли провайдер IR, неизвестно (открытый вопрос). Кандидат для A/B «проза против IR-разделов» (фаза 5,
  дорого — по остатку бюджета).

## 10. xAI — Grok Imagine (картинки и видео 1.5)

- Отдельного гайда по промтам нет — только API-страницы [S39]. Картинки: до 10 за запрос, правка — до 5 исходных
  картинок, «Edit images with natural language» (пример «Render this as a pencil sketch with detailed shading»).
- **Видео 1.5 — t2v через первый кадр**: «text-to-video uses text-to-image then image-to-video under the hood: the
  model generates a first frame from your prompt, then animates it» [S39] → t2v-промт должен описывать и кадр
  (сцену, свет, композицию), и движение.
- i2v: картинка — первый кадр, промт необязателен («Generate a slow and serene time-lapse», «Make the water crash down
  and slowly pan out the camera»); первый + последний кадр (`last_frame`); до 4 ключевых кадров `{image,
  timestamp_s}` на сетке 1/3 с; правка; продление; референсы с голосами `<AUDIO_0>`. **Звук включён по умолчанию —
  `generate_audio=False` для тихого видео** [S39]; в polza параметра нет (открытый вопрос).
- **В polza**: `x-ai/grok-imagine-image` — 2,50 ₽, промт ≤ 5 000, 1 референс, 1:1 / 2:3 / 3:2;
  `grok-imagine-video-1-5` — 1,62 ₽/с (480p) / 3,04 ₽/с (720p), промт ≤ 4 096, до 7 картинок — самый дешёвый
  видео-перебор.

## 11. Вне polza: Runway, Luma, Recraft, Ideogram, Midjourney

### 11.1 Runway Gen-4 / Gen-4.5

- **Гайд Gen-4** [S40]: сила простоты; хороший входной кадр; «focus on describing motion»; **«Use positive phrasing
  and avoid negative prompts»**; «Refer to subjects in general terms, like "the subject"»; добавлять по одному: движение
  субъекта → камеры → сцены → стиль. «Gen-4 is designed to interpret prompts that describe what should happen…
  **Negative phrasing is not supported and may produce unpredictable or even opposite results**.»

| Не так (Runway [S40]) | Так |
|---|---|
| «No camera movement. The camera doesn't move. NO MOVEMENT» | «Locked camera. The camera remains still.» |
| «embodies the essence of joyful greeting» | «The woman smiles and waves.» |
| «The tall man with black hair wearing a blue business suit…» (пересказ картинки) | «The man extends his arm to shake hands, then nods politely.» |
| «can you please add my dog» | «A dog excitedly runs into the scene from off-camera» |
| кот → дракон → подлодка в одном клипе | одна сцена |

- **Гайд Image to Video (Gen-4.5)** [S41]: «Effective image to video prompts focus almost exclusively on motion»;
  видимое описывать только при новом элементе, резком изменении, трансформации, взаимодействии; структура «The camera
  [motion description] as the subject [action]. [Additional descriptions]»; «Structure and order are far less
  important than clearly conveying an idea»; последовательность — «X occurs, then Y occurs. Finally, Z occurs.» или
  «[00:01] X occurs. [00:03] Y occurs.».
- **FAQ** [S41]: движение, «запечённое» во входной картинке (смаз, пыль), спорит с промтом — убрать правкой
  картинки; нежелательная склейка → длиннее ролик + «Continuous, seamless shot»; минимальное движение камеры — «The
  locked-off camera remains perfectly still.», «**The camera must start and end on the exact same frame to create a
  perfect loop.**», «Minimal subject motion only.» + стабилизация; петля — одна картинка на обоих входах (Animate
  Frames).
- **Камера** [S42]: «The camera is entirely motionless for the duration of the scene, with movement only occurring
  from the subject»; статичные широкие планы трудны — «Video models are designed to create immersive, high-fidelity
  motion».

### 11.2 Luma Ray3

Текстовый гайд по промтам в справке Luma закрыт логином — не прочитан. Руководство Ray3 [S43] описывает функции,
влияющие на промт: **визуальные пометки прямо на стартовом кадре** (направления движения), режим рассуждения
(«think deeply about prompts… plan sophisticated event sequences»), Draft Mode (до 5 раз быстрее, затем «master» в
4K HDR без смены композиции), HDR EXR, ключевые кадры, **Extend и Loop** («Loop ensures consistent infinite
playback»).

### 11.3 Recraft V4

- **Два режима** [S44]: короткий промт → «Interpretive Mode» (модель дизайнит сама), структурированный → «Architectural
  Control». «**Structured prompts don't make results "better." They make outcomes intentional, controllable, and
  repeatable.**»
- **Порядок «from global to local»**: концепт → фон и среда → кадр и поза → атрибуты → второстепенные субъекты и связи
  → свет → камера, глубина, контраст → настроение и композиция; раньше в промте — выше приоритет; «Avoid stacking
  dramatic or evaluative adjectives»; 3–6 слов — для разведки вариантов [S44].
- **Вектор и логотип**: тип графики, логика формы, **цветовая система (строгая палитра)**, дисциплина линии,
  раскладка, ограничения («no gradients, no shadows» — вендор пишет отрицания в прозе); «Avoid texture or
  material-focused language». Постер: формат → слой A → слой B → типографская иерархия → место текста → контраст слоёв
  [S44].
- **Текст**: «Place all required text in quotation marks»; «Define the typographic system — not just the phrase» [S44].
- **Негатив** (Studio, V2/V3) [S61]: отдельное поле (в API у V4/V4.1 поля `negative_prompt` нет — запреты прозой, G
  `../07-vector-svg-icons/02-vector-generators-and-tracing.md` п. 5 [поправка X 24.09.2026]); «avoid double negation… write "apples" in the negative prompt, not "no
  apples". Using "no" can confuse the model and lead to the opposite effect»; переключатель «Avoid text in image».
- **Палитра параметром** [S61]: `controls.colors` — до 10 цветов `{rgb: [r, g, b], weight 0..1}`, сумма весов ≤ 1,
  плюс `background_color`; вес — **«relative preference», а не доля площади** (docs Recraft; G
  `../07-vector-svg-icons/02-vector-generators-and-tracing.md` п. 6), поэтому прямого соответствия полю `share` спецификации
  (`03-asset-spec-and-dialects.md` §5) нет — долю дублировать словами [поправка X 24.09.2026: было «единственный API, где
  доли площади задаются числом»].
- **Кириллица**: у V3 `text_layout` допускает только кириллические буквы, совпадающие с латиницей по виду («А В Е К М
  Н О Р С Т У Х» и «І»), — «Characters not listed in this character set will not render» [S61]; русские слова V3 не
  пишет. Для V4 / V4.1 таблицы символов нет (открытый вопрос). Лимит промта: V4 — 10 000 символов, V3 — 1 000 [S61].

### 11.4 Ideogram 4 — модель, обученная на JSON

- «Ideogram 4 is **trained exclusively on structured JSON captions**… Providing a JSON object that follows the caption
  schema is required for good results… Passing in plain-text prompts directly to the model will not work and will
  likely trigger a safety warning» [S45]. На хостинге прозу спасает Magic Prompt («Natural language prompts still work
  well»), для JSON он выключается автоматически [S46].
- **Схема** [S45]: `high_level_description` (1–2 предложения, ≤ 50 слов) → `style_description` {`aesthetics`,
  `lighting`, `photo` | `art_style`, `medium`, `color_palette` ≤ 16 hex в верхнем регистре} →
  `compositional_deconstruction` {`background`, `elements[{type: "obj" | "text", bbox [y_min, x_min, y_max, x_max]
  0–1000, text, desc, color_palette ≤ 5}]`}. «The model was trained on JSON with a consistent key order, so
  maintaining it improves generation quality»; сериализация без пробелов и без `\uXXXX` (кириллица как есть).
- **Когда JSON** (таблица вендора [S46]): дизайн, постеры, бренд-графика, точное место текста, заданная палитра,
  повторяемые раскладки → JSON; быстрая разведка и фотореализм без жёсткой раскладки → проза. «Two runs from the same
  JSON prompt stay close to each other in composition».
- **Magic Prompt** — открытый системный промт (LLM → JSON) [S45]: «Leave nothing for the model to invent or choose»;
  запрет хеджей («such as», «various», «e.g.»), альтернатив («oak or walnut»); **«Avoid luminous, radiant, vibrant,
  lush, dynamic, glowing, gorgeous, stunning, breathtaking, mesmerizing»**; фотореализм по умолчанию — эстетика
  iPhone, «AVOID DSLR-magazine markers (creamy bokeh, telephoto compression, dramatic rim lighting, cinematic grade) —
  those signal AI-generation»; «**The word "warm"… is BANNED as a grading adjective** — it triggers the amber/golden AI
  look»; нецентральная композиция; разреженный бриф наполняется по планам, но слова «minimal, sparse, empty… negative
  space, alone, single subject» **отключают наполнение** — для фонов сайта их писать обязательно
  `[мнение вендора]`.
- **Текст** [S45]: поле `text` дословно, диакритика и регистр сохраняются; стилизованные заголовки переносить `\n` по
  словам — «long single-line stylized titles produce typos and dropped letters»; **«Language scoping: scene /
  elements / description… are always in ENGLISH regardless of the user's brief language. Only the literal text field
  characters follow the user's brief language»**; «Preserve non-ASCII characters as-is (CJK, Cyrillic…)».
- **Негатив** [S46]: «Ideogram, like many text-to-image AIs, struggles with understanding negation… "a man without a
  beard" may result in an image of a man with a beard… they don't inherently grasp the concept of absence»; вопрос
  «If this thing wasn't there, what would I see instead?»; поле негатива — списком («green, green color, green
  candies»), «The content of the regular prompt will always be favored over the negative prompt».
- **Сбои текста** [S46]: «Text in foreign language or non-Latin characters», слишком поздний текст в промте, большой
  объём; «For long copy, add it later in a third party editor».
- Независимое слепое сравнение типографики (ContraLabs, 10 дизайнеров): Ideogram 4 — 47,9 % побед, NB2 — 30,0 %,
  FLUX.2 [max] — 15,5 % (приведено вендором в README) [S45] `[мнение вендора]`.

### 11.5 Midjourney V8.2

- «**Short and simple prompts typically generate the best images with Midjourney**… Avoid making long lists or
  detailed instructions; these can confuse the process» [S47]; не так: «Show me a picture of lots of blooming California
  poppies, make them bright…» так: «Colored pencil illustration of bright orange California poppies».
- «Describe what you do want instead of what you don't. If you mention a party with "no cake," a cake might still
  appear» [S47]; исключение — параметр: не так: «still life gouache painting without any fruit», так: «still life gouache
  painting --no fruit, apple, pear»; модерация читает каждое слово отдельно («--no modern clothing» → «clothing»);
  `--no X` ≡ вес `X::-0.5` [S47].
- Мульти-промты `::` и веса работают **только в версиях 1–6.1**, не в V7 / V8 [S47].
- Диалект Midjourney противоположен Gemini и GPT Image: коротко, без инструкций, негатив — только параметром.

## 12. Сквозные правила: ответы на пять вопросов

### 12.1 Негатив и «no X» по моделям polza

**Механизм.** (1) Поле негатива работает через CFG-вычитание: у негатива «запаздывающий эффект» — он начинает
действовать после того, как позитив «нарисовал» объект, и удаляет его взаимным гашением предсказаний; если внимание к
области приходит поздно, удаление не срабатывает [S50] `[исследование]`. (2) «no X» внутри позитивного промта — не
вычитание, а упоминание X: подписи с явным отрицанием составляют около 0,4 % в MS COCO, 1,63 % в CC3M, ~2,5 % в CC12M,
~0,6 % в LAION-400M — модель учится «слово → объект» [S51]; энкодеры класса CLIP понимают отрицание на уровне
случайного угадывания [S52] `[исследование]`. (3) У моделей с LLM-фронтом «no» понимает языковая модель — вендоры
пишут служебные запреты сами; доходит ли запрет до генератора без утечки, данных нет → тест 4 фазы 5 `[спорно]`.

| Модель polza | Поле негатива | «no X» по документации вендора | Как писать |
|---|---|---|---|
| Nano Banana / NB2 / Lite / Pro | нет | «positive framing», но в примерах «No text.», «No other text.» [S1][S2] | предмет — описанием пустоты; служебное — «No text. No watermark.» |
| GPT Image 2.5 / 2 / 1.5, GPT-5 Image | нет | «No extra text, no watermarks, no unrelated logos» [S12] | служебные запреты в блоке Constraints |
| FLUX.2 [pro] / [flex] | нет | «No negative prompts… describe what you want» [S15] | только позитивные замены (§5.4) |
| Seedream 4 / 4.5 / 5 | нет | «Do not include any text or hand-drawn edges…» в правке [S22] | служебное — можно; предметы — позитивом `[не проверено]` |
| Qwen Image 2 / 2.1 | нет (в Model Studio — есть) | старый переписчик вычищает отрицания; новый пишет «No other text appears in the image.» [S31] | «No other text appears in the image.»; предметы — позитивом |
| Z-Image | нет | данных нет; у Turbo CFG = 0 [S64] | только позитив |
| Grok Imagine Image / Video | нет | данных нет | только позитив |
| Veo 3.1 | нет (в Vertex — `negativePrompt`) | «a desolate landscape with no buildings or roads» [S6] | позитив + отрицание внутри описания |
| Gemini Omni | нет | «Do not do X»; «No dialogue, No embellishments, No extra sound effects» [S8] | служебные запреты предложениями |
| Seedance 1.5 Pro | нет | «with no unnecessary elements added» [S24] | служебное — можно |
| Seedance 2.0 / Fast / Mini | нет | «keep it subtitle-free», «do not generate a logo / watermark» [S25] | так и писать; горизонтальный кадр против субтитров |
| Seedance 2.5 | нет | «Negative constraints are supported for subtitles and audio control» [S26] | «no subtitles», «no BGM» + синонимы в начале и в конце |
| Kling 3.0 / 2.6 | нет (у 2.5 Turbo было) | «The prompt can include positive and negative descriptions» [S34] | служебное — можно |
| Wan 2.5 | **`negative_prompt` ≤ 500** | в тексте — «No dialogue.», «No background music.» [S27] | в поле — существительные через запятую без «no» |
| Wan 2.6 / 3.0, HappyHorse | нет | то же [S27] | служебное — предложениями |
| MiniMax H3 Max | нет | в IR — `non_diegetic_music: N/A` [S38] | позитив; отсутствие музыки — «N/A» в разделе звука |

**Правило базы.** Отсутствие предмета — описание того, что на его месте («an empty, deserted street»; «bare oak
desk with only a laptop»). Служебные запреты (текст, водяной знак, логотип, субтитры, музыка) — коротким предложением в
конце у моделей класса A и у видео-моделей ByteDance, Alibaba, Kling, Omni; у FLUX.2 — «clean unmarked surfaces»,
«text-free». В поле негатива (`wan/2.5`, Vertex, Recraft, Ideogram) — существительные без «no» [S9][S61][S46].

### 12.2 Image-to-video: что писать и чего не писать

| Писать | Не писать |
|---|---|
| одно движение камеры с амплитудой и скоростью («slow dolly in», «pushes in with small amplitude at slow speed») [S10][S38] | пересказ того, что уже на картинке: внешность, фон, свет [S10][S21][S41] |
| одно действие субъекта, общими словами («the subject», «the woman») [S10][S40] | два движения камеры или «locked camera» + «tracking» [S21][S25] |
| движение среды («Fog rolls in slowly across the landscape») [S10] | резкие, быстрые, «взрывные» действия для коротких клипов [S25] |
| новое — только если появляется в кадре (новый объект, трансформация) [S41] | движение, противоречащее картинке (смаз и пыль на входе при «static») — чинить картинку [S41] |
| контракт непрерывности: «same set and geometry; no cuts» [S21]; для Omni — «In a single continuous shot» [S8] | переход между несвязанными первым и последним кадром («large jumps invite drift») [S21] |

- **Неподвижная камера** — утвердительно: «Locked camera. The camera remains still.» [S40]; «The camera is entirely
  motionless for the duration of the scene, with movement only occurring from the subject» [S42]; Wan — «fixed camera»
  [S27]; MiniMax — `[Static shot]` [S36] или «The camera holds a static shot as…» [S38]; Seedance 1.5 Pro —
  `fixed_lens: "true"` в polza.
- **Петля** (`VID-HERO-LOOP`): один кадр на входах первый и последний (Veo `FIRST_AND_LAST_FRAMES_2_VIDEO`, Kling
  `images` 0–2, Seedance 1.5 Pro, H3 Max, Omni preview `<FIRST_FRAME>@Image1 <LAST_FRAME>@Image1`, GA Omni —
  `first_frame_url` + `last_frame_url`) + «The camera must start and end on the exact same frame to create a perfect loop.»
  [S41] + минимальное движение. Петлю документируют только Omni, Runway и BFL — у Kling, Seedance, Veo, H3 [A,A] — наш
  перенос `[не проверено]` (I-02…I-15) → `04-video-prompting.md` §3.1–3.2 [поправка X 24.09.2026 по D2b]. Проверка шва —
  агент I.
- **Продукт** (`VID-I2V-PRODUCT`): «keeping the appearance, proportions, and materials… accurate and consistent, with
  no unnecessary elements added» [S24].
- **Исключения**: t2v у Grok Imagine Video 1.5 строится через первый кадр — описывать и сцену [S39]; пример i2v в
  Gemini API пересказывает сцену [S7] `[спорно]`.

```text
// bytedance/seedance-1.5-pro (fixed_lens="true", generate_audio="false") · шаблон базы · polza 2026-09-23 · [не проверено]
The camera stays locked on a tripod. Steam rises slowly from the cup and drifts to the left; the linen curtain behind
sways gently in a light breeze. The subject stays still. Same set and geometry throughout, one continuous shot, no cuts.
```

### 12.3 Правки: что, где, что не трогать

**Формула**: глагол операции + что + где + на что + что сохранить (+ «Change nothing else»). Одна правка за шаг;
сложное — цепочкой [S20]; пиксельная неизменность — только композитингом [S12].

| Вендор | Формулировка сохранения |
|---|---|
| Google | «change only the [specific element] to [new]. Keep everything else in the image exactly the same, preserving the original style, lighting, and composition» [S2] |
| OpenAI | «replace ONLY the white chairs… Preserve camera angle, room lighting, floor shadows… Keep all other aspects of the image unchanged» [S12] |
| BFL | «…while keeping the subject's pose, clothing, and expression exactly the same»; «Change nothing else» [S20][S18] |
| ByteDance | «…, keeping its pose unchanged»; правка по красной рамке на входе [S22] |
| Qwen | «Replace Y with X» + признаки X; «keep smile, short hair, and gray jacket unchanged»; шаблоны инпейнта и аутпейнта [S31] |
| Omni (видео) | коротко + «Keep everything else the same» [S8] |
| Seedance 2.5 (видео) | «…from 4-6 seconds in Video 1, and leave the rest of the content unchanged» [S26] |

**Маски в polza** (полярность противоположна):

| Модель | Меняется | Остаётся | Ограничения |
|---|---|---|---|
| `openai/gpt-5-image` (`mask_url`) | чёрное | белое | маска — ориентир, не точная форма [S14] |
| `qwen/image-2.1` (`mask_url`) | белое | чёрное | только с одним референсом; несовместима с `background: transparent` |
| прямой API OpenAI | прозрачное (альфа) | непрозрачное | маска к первой картинке [S14] |

### 12.4 Серия: постоянный блок стиля

- **Дословное повторение**: «Copy and paste the entire, unchanged character description into your prompt for every
  new scene» [S10]; «Repeat the appearance constraints so the character stays consistent» + блок «Character
  Consistency» [S12]; «Subject description (fixed, identical across shots)» [S19]; «Define … in Image 1 as Subject 1»
  [S25].
- **Структура промта серии**: `[STYLE — неизменно] + [SUBJECT — неизменно] + [SCENE — меняется] + [CONSTRAINTS —
  неизменно]`; утверждённый первый кадр — референсом с ролью («Image 1: style reference; keep line weight, palette
  and lighting») [S12][S20]; то же зерно, где есть `seed` (`bytedance/seedream-4`, `qwen/image-2.1`).
- **Фразы серии** Seedream («a series», «a set», число картинок) в polza не работают — нет `sequential_image_generation`
  [S22]; серия = N отдельных запросов с одним блоком.
- **Не смешивать версии** моделей в серии (Seedance 2.0 и 2.5 различаются эстетикой [S26]).
- Согласованность серии и её проверка — агенты F и K (`../06-art-direction-consistency/`).

### 12.5 Палитра

| Уровень | Как | У кого документировано |
|---|---|---|
| 1. Название + роль | «deep navy background, coral accent on the mug» | все |
| 2. hex + название + объект | «the wall in color #1F3A5F (deep navy)» | FLUX.2 [S15][S20], Ideogram 4 (`color_palette` ≤ 16) [S45]; у остальных `[не проверено]` |
| 3. Параметр с весами | `controls.colors [{rgb, weight}]`, сумма ≤ 1; вес — относительное предпочтение, не доля площади [поправка X 24.09.2026 по G] | Recraft [S61] |
| 4. Постобработка | перекраска, градинг, LUT под паспорт; проверка ΔE OKLab | агенты H и K |

- **Доли площади** — как колонка «Frequency» в `../../ui/12-ai-generated-ui/04-steering-brief-prompts-pipeline.md`
  §2.2 [S55]: доминирующий (~60 %), вторичный (~30 %), акцент (~10 %). Словами: «[color] fills most of the frame»,
  «[color] only on [small object]». Числа процентов в промте — `[не проверено]` (тест 7).
- **3–5 цветов**, не больше [S20]; градиенты — «starting with color #… and finishing with color #…» [S15]; «Strictly
  follows a bright "teal-orange" color scheme» — палитра словами у Wan 3.0 [S28].
- **Не грейдить словом «warm»** — «triggers the amber/golden AI look» [S45]; не складывать vibrant + bright +
  saturated [S45] `[мнение вендора]`.
- hex — не гарантия: обещание BFL «No approximation» не проверено независимо; бренд-цвет, который обязан совпасть, —
  кодом поверх или постобработкой.

### 12.6 Место под текст

- **Официальные формулировки**: Google — «positioned in the [bottom-right/top-left/etc.] of the frame. The background
  is a vast, empty [color] canvas, creating significant negative space» [S2]; OpenAI — «subject centered with negative
  space on left» [S13]; Ideogram — «minimal, sparse, empty… negative space, alone, single subject» [S45]; Seedream —
  рамка на входной картинке [S22]; NB Pro — вайрфрейм или сетка референсом («strictly adhere to the button placement
  and grid structure») [S5]; FLUX.2 JSON — `subjects[].position`, `composition` [S15]; Ideogram JSON — `bbox`
  0–1000 [S45].
- «copy space» — жаргон фотостоков; в гайдах вендоров не встречается; работает ли — `[не проверено]`.
- **Формула базы** (сторона + доля + пустая поверхность + назначение + ровный тон):

```text
// google/gemini-3.1-flash-lite-image · формула места под текст · polza 2026-09-23 · [не проверено]
A ceramic coffee cup on a pale oak table, positioned in the right third of the frame. The left 40 percent of the frame
is a vast, empty, evenly lit warm-grey plaster wall, creating significant negative space for a headline. Soft window
light from the right, low contrast in the empty area. 16:9.
```

  Для FLUX.2 и Ideogram — без отрицаний: «empty, uncluttered, plain» вместо «no objects». Проверка зоны (плотность
  границ, контраст по худшему пикселю) — агент K; безопасные зоны кадрирования — `03-asset-spec-and-dialects.md` §3.

### 12.7 Текст в картинке, кириллица, язык промта

- **Текст по умолчанию — HTML-слоем** поверх картинки: так велит принцип базы (`PLAN.md`), и так же вендоры — «Reserve
  for deterministic post when exactness is a success condition: typography, subtitles, logos» [S21]; «Text renders
  approximately» [S27]; «For long copy, add it later in a third party editor» [S46].
- **Если текст в картинке** (декоративный, часть сцены): двойные кавычки, дословно, место, шрифт словами, размер,
  цвет; «exactly once»; «No other text»; 1–4 слова [S20]; редкие слова — по буквам [S12]; длинный заголовок — по
  строкам [S45].
- **Кириллица** — хуже латиницы у всех измеренных моделей: MULTITEXTEDIT (12 языков, 12 систем) — русский теряет
  ΔSem 0,542, ΔLSF 1,038 (пятое место по тяжести из 12) [S53]; LingT2I — рендер русской надписи: Nano Banana 0,47
  (англ. 0,68), Qwen-Image 0,32 (0,69), FLUX.1-Krea 0,09 (0,65) [S63] `[исследование]`. Recraft V3 русские буквы не
  рисует [S61]; Z-Image — только EN/ZH [S64]; у Qwen смещение к иероглифам [S29].
- **Формула просьбы о кириллице**: описание по-английски + «The headline reads "Весенняя распродажа" in Russian
  (Cyrillic script), bold sans-serif, white, centered at the top. No other text.»; у Ideogram — русский только в поле
  `text`, остальное по-английски [S45]; у Seedance 2.5 — надпись картинкой-референсом [S26]; результат — OCR с
  точным сравнением (агент K).
- **Язык описания**: английский по умолчанию — Veo и Omni оценены только на EN [S7][S8]; Ideogram, H3 и Qwen-2512
  переписывают на английский [S45][S38][S31]; в LingT2I у моделей с T5/CLIP русский промт проваливается (SDXL 0,34,
  SD3.5 0,42, FLUX.1-Krea 0,44 против 0,77–0,79), у Qwen-Image почти нет потерь (0,78 против 0,82); фрагментация
  токенов языка связана с потерей качества (ρ = −0,89) [S63]. Русское описание допустимо у Nano Banana (`ru-RU` в
  списке [S2]) и Qwen-Image; у Veo в polza его переведёт `enableTranslation`.
- **Культурный контекст — явно**: у Qwen-Image доля «своей» культуры — 32,5 % при промте на родном языке, 75 % при
  английском промте с явной меткой, 0 % при нейтральном английском [S63] → «Russian provincial town, Cyrillic shop
  signs, Soviet-era apartment blocks», а не перевод промта на русский.

### 12.8 Минимальный общий словарь камеры и света

Один термин на ось; редкие термины — с пояснением («[term + descriptive explanation]» [S26]); не складывать
несколько движений в одну фразу [S19].

| Ось | Термины (переносятся между вендорами) | Избегать |
|---|---|---|
| Крупность | extreme close-up, close-up, medium shot, medium-wide, wide / establishing | «epic shot» |
| Ракурс | eye-level, low-angle, high-angle, top-down, over-the-shoulder | несколько ракурсов в одном кадре |
| Объектив и глубина | 24mm wide, 35mm, 50mm, 85mm, macro; shallow depth of field (f/1.8) / deep focus | стопку «8k, masterpiece, ultra-detailed» [S16] |
| Движение (видео) | static / locked, slow dolly in / out, pan left / right, tilt up / down, truck, pedestal, orbit (< 45° [S27]), tracking, crane | «low aerial handheld orbit push-in» [S19] |
| Амплитуда и скорость | small / large amplitude, slow / fast speed [S38] | «dynamic», «epic» |
| Свет | источник (window daylight, overcast sky, golden-hour sun, practical lamp, softbox), качество (soft / hard), направление (from the left, backlight, top light), взаимодействие (long shadows, specular highlights) [S16] | «warm» как грейд [S45]; «cinematic» без конкретики [S38] |
| Носитель | 35mm film photograph, Kodak Portra 400, medium-format, smartphone photo [S12][S15][S45] | маркеры «журнального DSLR» ради «естественности» [S45] |

## 13. Сводная таблица диалектов

Машиночитаемая версия — `dialects.yaml`; правила компиляции — `03-asset-spec-and-dialects.md` §9–§10. Лимиты — каталог
polza 2026-09-23.

| Семейство (id polza) | Форма по умолчанию | Порядок | Длина | Язык описания | Негатив | Референсы | Текст в кадре | Время и камера (видео) | Встроенный усилитель |
|---|---|---|---|---|---|---|---|---|---|
| Nano Banana / NB2 / NB2 Lite / NB Pro (`google/gemini-*`) | проза; разделы с метками — допустимо | глагол операции → субъект → действие → место → композиция → стиль | подробно; ≤ 20 000 | EN, `ru-RU` допустим | поля нет; позитив + «No text.» | «Image A/1» + роль; ≤ 8–14 | кавычки + шрифт + место; сначала текст | — | thinking (в polza не управляется) |
| GPT Image 2.5 / 2 / 1.5, GPT-5 Image (`openai/*`, `gpt-image-2-5-flare`) | разделы Scene / Subject / Details / Constraints | сцена → субъект → детали → ограничения + назначение | ≤ 20 000 (GPT-5 Image — 4 000) | EN | поля нет; «No extra text, no watermarks» | «Image 1: …, Image 2: …»; ≤ 16 | «EXACT, verbatim», по буквам, «exactly once» | — | `revised_prompt` в Responses; `isEnhance` у GPT-5 Image |
| FLUX.2 [pro] / [flex] (`black-forest-labs/*`) | проза, главное в начале; JSON — допустим | субъект → действие → стиль → контекст → свет → камера | 30–80 слов; ≤ 5 000 | EN (родной язык — «аутентичнее» по BFL) | нет; только позитивные замены | «image 1, image 2» + роли; ≤ 8 | кавычки, цвет hex, 1–4 слова | — | апсемплинг включён по умолчанию в API BFL |
| Seedream 4 / 4.5 / 5 Lite / 5 Pro (`bytedance/seedream-*`, `seedream/5-pro-*`) | связная проза + назначение | субъект → действие → среда → стиль | кратко, < 600 слов; ≤ 2 996–5 000 | EN / ZH | поля нет; «Do not include…» в правках | «Image 1/2/3», «Reference Target»; ≤ 10–14 | двойные кавычки | — | `optimize_prompt_options` (BytePlus) |
| Qwen Image / 2 / 2.1 (`qwen/*`) | английская проза без Markdown | передний → средний → дальний план, свет, фактуры | ≤ 200 слов у переписчика; ≤ 5 000 | EN; язык надписи — явно | поля нет; «No other text appears in the image.» | «Image 1…» в порядке промта; ≤ 10 | кавычки + язык + место + шрифт | — | `enhance_prompt` (`false`) |
| Z-Image (`tongyi-mai/z-image`) | плотное фактическое описание | субъект → детали → фон | ≤ 1 000 символов | EN (ZH) | нет (Turbo: CFG 0) | нет | только EN / ZH | — | PE вендора (нет в polza) |
| Grok Imagine Image (`x-ai/grok-imagine-image`) | проза | — | ≤ 5 000 | EN | нет данных | 1 | нет данных | — | нет данных |
| Veo 3.1 (`google/veo3`, `google/veo3_fast`) | проза по формуле | камера → субъект → действие → контекст → стиль; звук отдельными предложениями | 1 024 токена в API; ≤ 60 000 в каталоге | EN (`enableTranslation="true"`) | нет в polza (Vertex: `negativePrompt` существительными) | первый + последний; ≤ 3 ингредиента (Fast) | вывески словами | `[00:00-00:02]`; одна сцена | переписчик Gemini |
| Gemini Omni (`gemini-omni-video` — preview до 30.09.2026; GA `google/gemini-omni-1.1-flash` — кадры полями, §3.9) | проза + теги ролей (preview) | — | ≤ 20 000 | EN | «Do not do X», «No dialogue» | `<FIRST_FRAME>`, `<IMAGE_REF_N>`, `[# Sources …]`; ≤ 7 | «One word on the screen at a time» | `[0-3s]`; «In a single continuous shot» | — |
| Seedance 1.5 Pro (`bytedance/seedance-1.5-pro`) | Subject + Movement + Environment + Camera + Aesthetic + Sound | как в формуле | ≤ 2 500 | EN / ZH | нет; «with no unnecessary elements added» | первый / последний (2) | — | Shot 1 / 2; формула движения камеры; `fixed_lens` | — |
| Seedance 2.0 / Fast / Mini (`bytedance/seedance-2*`) | «engineering-style instruction» | ассеты → субъект → действие → сцена → свет → камера → стиль → качество → ограничения | ≤ 20 000 (в описании — 1 536) | EN / ZH | «keep it subtitle-free», «do not generate a watermark» | `<Image_N>`, «@Image 1», «Subject 1»; ≤ 5–9 | формула текста; частые символы | Shot 1 / 2 / 3 без секунд; 1 движение камеры | — |
| Seedance 2.5 (`bytedance/seedance-2-5`) | разделы: ассеты → одно предложение → план → заметки | как в формуле | ≤ 30 000 | EN / ZH | «no subtitles», «no BGM» + синонимы | «Image 1», «Video 1»; ≤ 30 + 10 | по буквам или картинкой-референсом | `[1s-4s]`, целые секунды | скилл `sd25-pe` (вне API) |
| Wan 2.5 / 2.6 / 3.0, HappyHorse (`wan/*`, `alibaba/*`) | сущность + сцена + движение + эстетика + стиль; у 3.0 — разделы | как в формуле | 2.5: ≤ 800; 2.6: ≤ 5 000 | EN / ZH | 2.5: `negative_prompt` ≤ 500; «No dialogue.», «No background music.» | «Image 1», «Video 1»; ≤ 1 | «Text renders approximately» | «Shot 1 [0–3 s]»; «fixed camera»; дуга < 45° | `enable_prompt_expansion` (2.5, `"false"`) |
| Kling 3.0 / 2.6 (`kling/*`) | плотная проза с точками времени | Subject → Action → Scene → Camera → Lighting and Mood | ≤ 2 500 | EN (реплики: 5 языков, прочие → EN) | позитив и негатив в тексте | первый / последний (2); `@Name` | точные слова, место, поверхность | «shot n, m, words;», «At the 4th second…» | — |
| MiniMax H3 Max (`minimax/hailuo-3-max`) | IR «ключ: проза» (snake_case) | `integrated_multimodal_description` → звук → музыка | не указан (API H3 — 7 000) | EN; реплики и надписи — на исходном | `N/A` в разделе | первый / последний (2) | «"…"» дословно | тип + амплитуда + скорость; `[Pan left]` у Hailuo | H3-Context-IR / `prompt_optimizer` |
| Grok Imagine Video 1.5 (`grok-imagine-video-1-5`) | проза: кадр + движение | сцена → движение | ≤ 4 096 | EN | нет данных | ≤ 7; ключевые кадры | — | ключевые кадры по 1/3 с (API xAI) | — |
| Runway Gen-4 / 4.5 (вне polza) | простая проза о движении | «The camera [motion] as the subject [action]» | коротко | EN | не поддерживается — «opposite results» | первый / последний | — | «[00:01] X occurs» | — |
| Recraft V4 (вне polza) | от общего к частному; структура — для контроля | концепт → фон → кадр → атрибуты → свет → камера → настроение | ≤ 10 000 | EN | поле — только V2/V3 и Studio (существительные без «no»); у V4 в API — запреты прозой [поправка X 24.09.2026] | стиль (`style_id`) | кавычки + типографская система | — | — |
| Ideogram 4 (вне polza) | JSON по схеме, порядок ключей фиксирован | HLD → style → composition | HLD ≤ 50 слов | EN, кроме `text` | поле списком | — | `text` + `bbox` 0–1000 | — | Magic Prompt |
| Midjourney V8.2 (вне polza) | коротко, без инструкций | носитель + субъект + среда; параметры в конце | коротко | EN | `--no` | — | — | — | — |

## Частые ошибки

1. **Параметры «по памяти»** (ошибка агентов): `negative_prompt`, `seed`, `guidance`, `steps` для FLUX.2 в polza;
   `quality`, `background` для GPT Image 2.5 в polza; `thinking_level` для Nano Banana — их нет в каталоге. Источник
   правды — `parameters` модели в каталоге (§1.2).
2. **Устаревшие и неверные идентификаторы**: Imagen (закрыт), `gpt-image-1` (закрывается 2026-10-23), Kling 2.5 Turbo
   (в каталоге нет), «Veo 3» вместо Veo 3.1; `openai/gpt-image-2.5-flare` — такого id нет, верный —
   `gpt-image-2-5-flare`. [поправка фазы 5, 25.09.2026: было — «верный `gpt-image-2-5-flare`»; в снимке каталога
   `2026-09-25_1411` id сменился на `openai/gpt-image-2.5-flare` (параметры и цены 4 / 7 / 11 ₽ те же), старого id нет — с ним
   `routing_check.py` даёт ошибки → `99-raw/cache/polza/2026-09-25_1411/`]
3. **Перенос параметров вендора на агрегатор**: `disable_pup`, `prompt_extend`, `sequential_image_generation`,
   `optimize_prompt_options`, `negativePrompt` Vertex, `prompt_optimizer` MiniMax — в polza не выставлены.
4. **Негатив в модель без негатива**: «no people» в FLUX.2; поле `negative_prompt` в запросе к Veo через polza.
5. **«no X» ради отсутствия предмета** → предмет появляется (FLUX.2, Ideogram, Midjourney, Runway — «opposite results»).
6. **hex как гарантия цвета** — документировано только у FLUX.2 и Ideogram, и то без независимой проверки.
7. **JSON «потому что точнее»**: у моделей с LLM-фронтом выигрыша не показано; у Ideogram 4 — наоборот, без JSON
   модель не работает; у Veo и FLUX.2 [pro] промт всё равно переписывается.
8. **Пересказ картинки в image-to-video** → модель «перерисовывает» кадр.
9. **Две камеры в одном клипе**, «locked camera» вместе с «orbit» или «tracking».
10. **Таймкоды в Seedance 2.0** («0–3 seconds» нестабильно по словам вендора).
11. **Кириллица в картинке без OCR-проверки**; русская надпись у Qwen без указания языка → иероглифы.
12. **Русское описание для моделей с T5/CLIP** (открытые FLUX.1, SD 3.5) → провал следования.
13. **Звук не выключен** у Seedance 2.x (`generate_audio` по умолчанию `"true"`) → музыка и переплата.
14. **Маска не той полярности**: `openai/gpt-5-image` меняет чёрное, `qwen/image-2.1` — белое.
15. **Стопка оценочных слов** («stunning, vibrant, 8k, masterpiece») и «warm» как грейд → «нейрослоп».
16. **Промт длиннее лимита**: Z-Image — 1 000, Wan 2.5 — 800, Kling 3.0 — 2 500 символов.
17. **Перефразированный «постоянный» блок серии** в каждом промте → дрейф стиля.
18. **Omni без «single continuous shot»** → нарезка на планы.
19. **«a series of 4 images» в Seedream через polza** → одна картинка (параметра серии нет).
20. **Чужой пример как проверенный**: дословный пример вендора — `[документация]`, а не `[проверено]`.

## Чек-лист

- [ ] Класс модели (A / B / C / D) определён?
- [ ] Параметры взяты из `parameters` каталога polza, а не из памяти или API вендора?
- [ ] Длина промта не больше меньшего из лимитов (каталог, документация)?
- [ ] Главное — в первых 10–15 словах?
- [ ] Нет оценочных слов без видимого содержания?
- [ ] Каждое «не надо» переписано позитивом (кроме служебных запретов у моделей, где так пишет вендор)?
- [ ] В поле негатива — только существительные?
- [ ] Референсы пронумерованы, у каждого роль?
- [ ] Правка: что, где, что сохранить; одна правка за шаг?
- [ ] Серия: блок стиля и субъекта совпадает с эталоном дословно?
- [ ] Палитра: 3–5 цветов, у каждого роль и доля; hex — только с названием?
- [ ] Место под текст: сторона, доля кадра, пустая поверхность, назначение?
- [ ] Текст действительно нужен в картинке, а не HTML-слоем?
- [ ] Если текст в картинке: кавычки, место, шрифт, язык, «No other text», OCR после генерации?
- [ ] Image-to-video: только движение, одна камера, одно действие?
- [ ] Видео: звук выключен параметром, неподвижная камера задана утвердительно (и `fixed_lens`, где есть)?
- [ ] Таймкоды — только у моделей, которые их держат?
- [ ] Описание по-английски, культурный контекст назван явно?
- [ ] Маска — полярность сверена с описанием каталога?
- [ ] Усилитель промта включён или выключен осознанно?

## Открытые вопросы и противоречия

1. **Документация polza против каталога**: Veo — 2 000 против 60 000 символов; GPT-5 Image — 32 000 и 10 картинок
   против 4 000 и 5; GPT-5.4 Image 2 — 5 000 против 20 000; NB2 — 8 против 14 референсов; Seedance 2 — «до 1536»
   против 20 000. Правило до фазы 5 — меньшее число.
2. **BFL**: документация — «JSON напрямую или проза — одинаково», скилл — «Flatten for Execution».
3. **Апсемплинг FLUX.2** включён по умолчанию в API BFL; в polza не управляется — включён ли у исполнителя?
4. **Google против Google**: «positive framing» против «No text.» в примерах; реплики в кавычках (Cloud Blog, Gemini
   API) против двоеточия (Vertex); i2v с пересказом сцены (Gemini API) против «motion only» (Vertex).
5. **Переписчик Veo 3.1** — для 3.0 неотключаем, для 3.1 статус в текущей документации не найден.
6. **Теги ролей Omni** через обёртку KIE — доходят ли до модели.
7. **MiniMax H3 Max в polza** — применяет ли провайдер H3-Context-IR и `prompt_optimizer`.
8. **Qwen**: старый переписчик запрещает отрицания, новый (2512) пишет «No other text appears in the image.» — какая
   позиция актуальна для Qwen Image 2.1.
9. **Seedance в polza**: какая из двух картинок станет последним кадром (роли `first_frame` / `last_frame` не
   выставлены).
10. **Recraft V4 / V4.1** — набор символов для кириллицы не опубликован.
11. **Z-Image в polza** — Turbo или база (от этого зависит, работает ли негатив в принципе).
12. **Нет официальных гайдов** по промтам у Z-Image, HappyHorse, Grok Imagine; гайд Luma закрыт логином; статья
    302.AI на medium не открылась (403).
13. **«copy space»** — работает ли жаргон фотостоков; в гайдах вендоров его нет.
14. **hex у моделей кроме FLUX.2 и Ideogram** — не документирован и не измерен.
15. **Сниппет поиска про Seedance 1.0** («not fixed camera») в тексте гайда не найден — в базу не взят.

## Источники

Документация снята 2026-09-23, если не указано иное; кэш — `99-raw/cache/` и заметки `99-raw/notes/wave1/D-notes.md`.

- [S1] Google Cloud (A. Davaajav, H. Chinoy). «The ultimate Nano Banana prompting guide», 2026-03-06.
  https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana — официальный
  гайд по NB2 и NB Pro; формулы, свет, камера, текст; высокая надёжность.
- [S2] Google AI for Developers. «Nano Banana image generation» (Gemini API). https://ai.google.dev/gemini-api/docs/image-generation
  — модели, референсы по ролям, языки, шаблоны, ограничения; первоисточник.
- [S3] Google Developers Blog (P. Schmid, L. Kilpatrick, A. Fortin). «How to prompt Gemini 2.5 Flash Image Generation for
  the best results», 2025-08-28. https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/
  — шаблоны, соотношение сторон при правке; высокая.
- [S4] Google (B. Alessio, Google DeepMind). «7 tips to get the most out of Nano Banana Pro», 2025-11-20.
  https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/ — элементы промта,
  ограничения по языкам; высокая.
- [S5] Google AI DevRel (G. Vernade). «Nano-Banana Pro: Prompting Guide & Strategies», 2025-11/12.
  https://dev.to/googleai/nano-banana-pro-prompting-guide-strategies-1h9n — практика DevRel: разделы с метками,
  идентичность, структура из референса; средняя (блог сотрудника).
- [S6] Google Cloud (A. Davaajav, H. Chinoy). «The ultimate prompting guide for Veo 3.1», 2025-10-16.
  https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 — формула,
  словарь, звук, таймкоды, первый/последний кадр; высокая.
- [S7] Google AI for Developers. «Generate videos with Veo 3.1». https://ai.google.dev/gemini-api/docs/veo — лимит
  1 024 токена, языки, i2v, продление; первоисточник.
- [S8] Google AI for Developers. «Gemini Omni Flash». https://ai.google.dev/gemini-api/docs/omni — теги ролей, петля,
  правки, ограничения; первоисточник.
- [S9] Google Cloud Vertex AI. «Video generation prompt guide».
  https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide — словарь камеры, поле
  негатива; первоисточник.
- [S10] Google Cloud Vertex AI. «Video generation best practices».
  https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/best-practice — «motion only» для i2v, одна сцена,
  персонаж; первоисточник.
- [S11] Google Cloud Vertex AI. «Turn off Veo on Vertex AI's prompt rewriter», копия Wayback 2025-09-07
  (https://web.archive.org/web/2025/https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/turn-the-prompt-rewriter-off)
  — переписчик Veo 3.0 неотключаем; страница сейчас переадресована; средняя (архив).
- [S12] OpenAI. «Image prompting» (вкладки GPT Image 2.5 / 2 / 1.5 / 1).
  https://developers.openai.com/api/docs/guides/image-prompting — принципы, формат, примеры, серия; первоисточник.
- [S13] OpenAI Cookbook. «GPT Image Generation Models Prompting Guide», апрель 2026 (архивирован, PR #3084).
  https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide — формат, композиция,
  текст; высокая, но для gpt-image-2.
- [S14] OpenAI. «Image generation». https://developers.openai.com/api/docs/guides/image-generation — `revised_prompt`,
  маски, ограничения; первоисточник.
- [S15] Black Forest Labs. «Prompting Guide — FLUX.2». https://docs.bfl.ml/guides/prompting_guide_flux2 — формула,
  JSON, hex, текст, негатив; первоисточник.
- [S16] Black Forest Labs. «FLUX Prompting Guide»: Building a Good Prompt, Technical Parameters, Style.
  https://docs.bfl.ml/guides/prompting_unified_building (и `…_technical`, `…_style`) — 32K токенов, длина, негатив,
  апсемплинг; первоисточник.
- [S17] Black Forest Labs. Use cases: JSON Structured Prompting, HEX Color Prompting, Multi-Language, Typography.
  https://docs.bfl.ml/guides/usecases_t2i_json_prompting (и соседние) — первоисточник.
- [S18] Black Forest Labs. FLUX.2 Overview, FLUX.2 Image Editing, Single/Multi-Reference Editing, API reference FLUX.2
  [pro] / [flex]. https://docs.bfl.ml/flux_2/flux2_overview — hex, JSON, лимиты референсов, `disable_pup`,
  `prompt_upsampling`; первоисточник.
- [S19] Black Forest Labs. FLUX 3 video prompting: Text-to-Video, Image-to-Video, Camera terms.
  https://docs.bfl.ml/guides/prompting_video_text_to_video — формы промта, таймлайн, камера; первоисточник.
- [S20] Black Forest Labs. GitHub `black-forest-labs/skills`, скилл `flux-image-best-practices` v1.0.0 (MIT; 119★;
  последний push 2026-09-09). https://github.com/black-forest-labs/skills — правила для агентов: негатив, hex, JSON,
  правки; высокая (вендор).
- [S21] Black Forest Labs. GitHub `black-forest-labs/skills`: `flux-3-prompt-doctor`, `flux-3-cinematic-inserts`,
  `flux-3-keyframes-continuation` (те же звёзды и дата) — бриф, валидация противоречий, i2v; высокая.
- [S22] BytePlus ModelArk. «Seedream 4.0-4.5 prompt guide», обновл. 2026-07-06.
  https://docs.byteplus.com/en/docs/ModelArk/1829186 — формула, текст, правки, метки, серия; первоисточник.
- [S23] BytePlus ModelArk. «Seedream 4.0-5.0 tutorial». https://docs.byteplus.com/en/docs/ModelArk/1824121 — лимит
  600 слов, `optimize_prompt_options`; первоисточник.
- [S24] BytePlus ModelArk. «Seedance-1.5-pro prompt guide», обновл. 2026-08-31.
  https://docs.byteplus.com/en/docs/ModelArk/2168087 — формула, грамматика камеры, звук; первоисточник.
- [S25] BytePlus ModelArk. «Dreamina Seedance 2.0 series prompt guide», обновл. 2026-09-22.
  https://docs.byteplus.com/en/docs/ModelArk/2222480 — ассеты, субъекты, запрет таймкодов, ограничения; первоисточник.
- [S26] BytePlus ModelArk. «Dreamina Seedance 2.5 prompt guide», обновл. 2026-09-22.
  https://docs.byteplus.com/en/docs/ModelArk/2607689 — структура, таймкоды, негатив для субтитров и музыки;
  первоисточник.
- [S27] Alibaba Cloud Model Studio. «Text-to-video / image-to-video prompt guide (Wan)».
  https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt — формулы, i2v, звук, мульти-шот;
  первоисточник.
- [S28] Alibaba Cloud Model Studio. «Wan 3.0 video generation guide».
  https://www.alibabacloud.com/help/en/model-studio/wan3-video-generation-guide — примеры по разделам; первоисточник.
- [S29] Alibaba Cloud Model Studio. «Qwen-Image API». https://www.alibabacloud.com/help/en/model-studio/qwen-image-api
  — язык, негатив, `prompt_extend`, примеры с отрицаниями; первоисточник.
- [S30] Alibaba Cloud Model Studio. «Text-to-image prompt guide (Wan)».
  https://www.alibabacloud.com/help/en/model-studio/text-to-image-prompt — формула t2i, `prompt_extend`; первоисточник.
- [S31] QwenLM. GitHub `QwenLM/Qwen-Image`: README, `prompt_utils.py`, `prompt_utils_2512.py` (Apache-2.0; 8 363★;
  последний push 2026-02-10). https://github.com/QwenLM/Qwen-Image — системные промты переписчиков; высокая.
- [S32] Z-Image Team (Tongyi-MAI). «Z-Image: An Efficient Image Generation Foundation Model with Single-Stream
  Diffusion Transformer», arXiv 2511.22699. https://arxiv.org/abs/2511.22699 — подписи обучения, усилитель PE;
  техотчёт вендора.
- [S33] Kuaishou. «Kling VIDEO 3.0 Model User Guide», 2026-02-06 (+ Kling IMAGE 3.0 User Guide).
  https://kling.ai/quickstart/klingai-video-3-model-user-guide — мульти-шот, языки реплик, примеры; первоисточник.
- [S34] Kuaishou. Kling API, Kling 3.0. https://kling.ai/document-api — `contents`, лимит 3 072 / 2 500, формат
  мульти-шота; первоисточник.
- [S35] Kuaishou. «Kling AI Prompt Guide», 2026-08-07. https://kling.ai/blog/kling-ai-prompt-guide — структура,
  текст, вариации; средняя (блог вендора).
- [S36] MiniMax. API «Video Generation» (Hailuo 2.3 / 02). https://platform.minimax.io/docs/api-reference/video-generation-v2-create
  — 15 команд камеры, `prompt_optimizer`; первоисточник.
- [S37] MiniMax. «Video Generation» guide (H3 / H3 Max, H3-Context-IR).
  https://platform.minimax.io/docs/guides/video-generation — лимиты, IR; первоисточник.
- [S38] MiniMax. GitHub `MiniMax-AI/MiniMax-H3` README + скилл `h3-prompt-writing` (9 116★; последний push 2026-08-15).
  https://github.com/MiniMax-AI/MiniMax-H3 — формат IR, камера, режимы FL2VA; высокая.
- [S39] xAI. Документация Grok Imagine: images/generation, images/editing, video/generation, video/image-to-video,
  video/reference-to-video. https://docs.x.ai/developers/model-capabilities/video/generation — t2v через первый кадр,
  звук по умолчанию; первоисточник, гайда по промтам нет.
- [S40] Runway. «Gen-4 Video Prompting Guide». https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide
  — позитивные формулировки, движение; первоисточник.
- [S41] Runway. «Image to Video Prompting Guide» (Gen-4.5).
  https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide — «almost exclusively on
  motion», петля; первоисточник.
- [S42] Runway. «Camera Terms, Prompts, & Examples». https://help.runwayml.com/hc/en-us/articles/47313504791059 —
  статичная камера; первоисточник.
- [S43] Luma. «Ray3 user guide». https://lumalabs.ai/learning-hub/ray3-user-guide — функции (пометки на кадре, Loop);
  гайд по промтам не прочитан (логин).
- [S44] Recraft. «Prompting with Recraft V4» и «Prompt engineering guide».
  https://www.recraft.ai/docs/prompt-engineering-guide/prompting-with-recraft-v4 — порядок, структура, вектор;
  первоисточник.
- [S45] Ideogram. GitHub `ideogram-oss/ideogram4`: `docs/prompting.md`, системный промт Magic Prompt v1, README
  (Apache-2.0 код, веса некоммерческие; 2 849★; последний push 2026-06-30). https://github.com/ideogram-oss/ideogram4 —
  JSON-схема, антислоп-правила; высокая (вендор).
- [S46] Ideogram. Docs: «4. JSON Prompting (Ideogram 4.0)», «4. Handling Negatives», «8. Troubleshooting», «Magic
  Prompt», «Negative prompt». https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/4.-json-prompting-ideogram-4.0
  — первоисточник.
- [S47] Midjourney. Docs: «Prompt Basics», «No», «Multi-Prompts & Weights».
  https://docs.midjourney.com/hc/en-us/articles/32023408776205-Prompt-Basics — первоисточник (для сравнения).
- [S48] fofr (Google DeepMind). «Prompting Nano Banana Pro with JSON», ~12.2025. https://www.fofr.ai/prompting-with-json
  — практика JSON; `[практика]`, без контролируемого теста.
- [S49] C. Jarvis. «Does JSON Prompting Actually Work? Tested with Nano Banana», 12.2025.
  https://chasejarvis.com/blog/does-json-prompting-actually-work-tested-with-nano-banana/ — n = 2 на плечо, без метрики;
  `[мнение]`.
- [S50] Y. Ban et al. «Understanding the Impact of Negative Prompts: When and How Do They Take Effect?», ECCV 2024,
  arXiv 2406.02965. https://arxiv.org/abs/2406.02965 — механизм негатива в CFG; `[исследование]`.
- [S51] M. Vatsa, A. Bharati, R. Singh. «Right Looks, Wrong Reasons: Compositional Fidelity in Text-to-Image
  Generation», arXiv 2511.10136. https://arxiv.org/abs/2511.10136 — обзор; доля отрицаний в подписях; `[исследование]`.
- [S52] K. Alhamoud et al. «Vision-Language Models Do Not Understand Negation» (NegBench), CVPR 2025, arXiv 2501.09425.
  https://arxiv.org/abs/2501.09425 — CLIP-подобные модели и отрицание; `[исследование]`.
- [S53] Cheng et al. «MULTITEXTEDIT», arXiv 2605.08163 (2026-05-18). https://arxiv.org/abs/2605.08163 — 12 языков,
  правка текста на картинке, русский; `[исследование]`.
- [S54] Bria AI (Gutflaish et al.). «Generating an Image From 1,000 Words: Enhancing Text-to-Image With Structured
  Captions» (FIBO), arXiv 2511.06876. https://arxiv.org/abs/2511.06876 — модель, обученная на JSON; `[исследование]`.
- [S55] База `ui`. `12-ai-generated-ui/04-steering-brief-prompts-pipeline.md` §2.2 (колонка «Frequency»
  палитры). `../../ui/12-ai-generated-ui/04-steering-brief-prompts-pipeline.md` — соседняя база.
- [S56] Z. Lin et al. «Evaluating Text-to-Visual Generation with Image-to-Text Generation» (VQAScore), ECCV 2024, arXiv
  2404.01291. https://arxiv.org/abs/2404.01291 — CLIP как «мешок слов»; `[исследование]`.
- [S57] Google Cloud Vertex AI. «Generate videos from an image» (REST, `negativePrompt`).
  https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-an-image — первоисточник.
- [S58] X. Wei et al. «TIIF-Bench», arXiv 2506.02161 v3. https://arxiv.org/abs/2506.02161 — короткие и длинные
  промты, устойчивость топ-моделей; `[исследование]`.
- [S59] BytePlus ModelArk. «Seedance-1.0-pro&pro-fast prompt guide». https://docs.byteplus.com/en/docs/ModelArk/1631633
  — языки, движения камеры; прочитан частично.
- [S60] J. Betker et al. (OpenAI). «Improving Image Generation with Better Captions» (DALL-E 3), 2023.
  https://cdn.openai.com/papers/dall-e-3.pdf — распределение подписей, апсемплинг промтов; `[исследование]`.
- [S61] Recraft. API reference (`controls.colors`, `text_layout`, лимиты) и Studio «Negative prompts», «Adding text to an
  image». https://www.recraft.ai/docs/api-reference/endpoints — первоисточник.
- [S62] Kuaishou. «Kling VIDEO 3.0 Omni Model User Guide».
  https://kling.ai/quickstart/klingai-video-3-omni-model-user-guide — ссылки `@`, планы; первоисточник.
- [S63] Zhang et al. «LingT2I», arXiv 2608.11002 (08.2026). https://arxiv.org/abs/2608.11002 — 10 языков включая
  русский, генерация и рендер текста, культура; `[исследование]`.
- [S64] Tongyi-MAI. GitHub `Tongyi-MAI/Z-Image` README (Apache-2.0; 12 044★; последний push 2026-02-09).
  https://github.com/Tongyi-MAI/Z-Image — guidance 0 у Turbo, двуязычный текст; высокая.
- [S65] Qwen Team. «Qwen-Image Technical Report», arXiv 2508.02324. https://arxiv.org/abs/2508.02324 — подписи
  обучения, структурная разметка; техотчёт вендора.
- [S66] polza.ai. Репозиторий документации `polza-ai/docs`, гайды медиа-моделей (`gaidy/*.mdx`), снимок 2026-09-23
  (`99-raw/cache/polza/2026-09-23/docs-repo/`). https://github.com/polza-ai/docs — первоисточник агрегатора; с
  расхождениями с каталогом.
- [S67] polza.ai. Каталог `GET https://polza.ai/api/v1/models`, снимок 2026-09-23
  (`99-raw/cache/polza/2026-09-23/api-v1-models.json`) — параметры и цены; первоисточник.
