# Карточки моделей картинок: 23 модели polza и 11 вне polza (сентябрь 2026)

Волна 1 · агент C1 · 2026-09-23 · прочитано целиком или существенно ≈ 60 источников, опытов 6 (`99-raw/experiments/C1/01–06`) ·
каталог polza: снимок 2026-09-23 и живой каталог с провайдерами (08:45) · машиночитаемо: `models/<slug>.yaml` (34 файла,
`checked: 2026-09-23`, генерируются `99-raw/experiments/C1/06-model-cards-build/build_cards.py`).

## Выжимка для агента

1. Id модели брать только из каталога polza (`GET /api/v1/models?type=image&include_providers=true`), не по памяти:
   у Flare id без префикса вендора (`gpt-image-2-5-flare`), у Seedream 5.0 Pro — `seedream/5-pro-text-to-image`, у Nano
   Banana Pro и Nano Banana 2 — устаревшие имена `…-preview`. → §1.3 [документация] [поправка фазы 5, 25.09.2026: с 25.09 id Flare в polza —
   `openai/gpt-image-2.5-flare` (снимок `2026-09-25_1411`, параметры и цены те же, старого id нет) → `../13-routing-matrix/routing.yaml`
   `defaults.deprecated`]
2. Модель по умолчанию для финальных веб-ассетов в polza — `gpt-image-2-5-flare` (4/7/11 ₽ за 1K/2K/4K): №1 AA в UI/UX,
   Marketing, Animation & Gaming; цена та же, что у Sunburst. `openai/gpt-image-2.5-sunburst` — если Flare не прошла
   критерий (люди, правка с сохранением деталей, e-commerce). → §2.1–2.2 [исследование] [поправка фазы 5, 25.09.2026: E-08 (голос заказчика вслепую,
   1 чел.) — Sunburst, Flare и NB2 «хорошо», равны → маршрут: Sunburst основной, Flare — равный запасной (X32); серия по эталону
   (E-12) — стиль держит только Flare → `../99-raw/phase5/runs/2.5-stand/E-08_blind_sheet.jpg`]
3. В polza у GPT Image 2.5 нет `quality`, `background`, маски и `seed`; арены мерили режим `max` — место polza-версии в
   рейтинге не гарантировано (тест 3 фазы 5). → §2.1 [не проверено] [поправка фазы 5, 25.09.2026: в polza Sunburst «хорошо» глазом заказчика (E-08);
   N-01 — через RouterAI `medium` ≈ `high` ≈ polza 1K на глаз и метриках (n = 2 брифа)]
4. Лучший не-OpenAI в polza — Nano Banana 2 (`google/gemini-3.1-flash-image-preview`, 4,8 ₽ за 1K): AA t2i #6, правка
   текста #5. Nano Banana Pro в 2,8 раза дороже и ниже NB2 в текстовых срезах обеих арен — брать для серий и
   мульти-референса (ViStoryBench и OmniRef-Bench №1, но без GPT 2.x в сравнении; роли: до 5 персонажей + 3 стиля), поиска
   с рассуждением и UI-состояний. → §2.7–2.8 [исследование] [поправка фазы 5, 25.09.2026: NB2 — «хорошо» в E-08, но в увеличении предметы
   ломаются («не стул»); NB Pro — «слишком ровно» (E-08) и в серии по эталону уводит палитру (E-12) → для серий не брать]
5. Прозрачный PNG внутри polza — только `qwen/image-2.1` (`background: transparent` + png/webp + шаблон «This is an
   RGBA image with transparency…»); веса под некоммерческой Qwen Research License — вопрос к L. У GPT Image 2.5/2
   прозрачность есть только в прямом API OpenAI. → §1.4, §2.18 [документация] [поправка фазы 5, 25.09.2026: T2 — альфа Qwen 2.1 настоящая (64 %
   прозрачных); GPT Image 2.5 `transparent` есть и через RouterAI (1,45 ₽): мех — годен, стекло — облако фона (H-03)]
6. Маска-картинка в polza — только `qwen/image-2.1` (`mask_url`: белое = менять) и `openai/gpt-5-image` у mie (чёрное =
   менять; модель выключается у OpenAI 23.10.2026). Полярности противоположные — проверять по результату. → §1.4, §2.5,
   §2.18 [документация]
7. Негатив-параметра нет ни у одной из 23 моделей polza; FLUX.2 — «No negative prompts», Google — «semantic negative
   prompts». Запрет формулировать описанием желаемого состояния. → §1.4 [документация]
8. `seed` в polza — только `qwen/image-2.1` и `bytedance/seedream-4` (у провайдеров Google `seed` есть лишь в списке
   chat-параметров). Воспроизводимые серии и A/B — на этих двух или через прямые API. → §1.4 [документация]
9. 8:1, 1:8, 4:1, 1:4 в polza — только Nano Banana 2 Lite (2,9 ₽, только 1K). 21:9 — у GPT 2.5, Nano Banana, Seedream
   4/4.5/5 Lite; у FLUX.2, Seedream 5.0 Pro, Qwen, Z-Image, Grok в polza 21:9 нет. → §1.4 [документация]
10. 4K в polza: GPT 2.5 (кроме 1:1) и GPT Image 2 у mie — 11 ₽; Nano Banana 2 — 10,8 ₽; Nano Banana Pro — 18 ₽;
    Seedream 4.5 (`quality: high`) — 5 ₽; Seedream 4.0 — 3 ₽. → §1.4, §1.6 [документация] [поправка фазы 5, 25.09.2026: E-01 — 4K у Sunburst
    настоящий (3840×2160, 11 ₽), «4K» Seedream 4 через mie — 2352×1008 при 21:9 (≈ 2,4K)]
11. Устаревшие в polza: `openai/gpt-5-image` (gpt-image-1, выключение у OpenAI 23.10.2026), `openai/gpt-image-1.5` и
    `openai/gpt-5-image-mini` (01.12.2026), `google/gemini-2.5-flash-image` (legacy), `qwen/image`, `qwen/image-2`. На
    них не строить конвейеры. → §1.3 [документация]
12. Дубли: `google/gemini-3.1-flash-image-preview` и `google/gemini-3.1-flash-image` — одна модель под двумя id с разными
    провайдерами и ценами; `black-forest-labs/flux.2-flex` в polza — дубль `flux.2-pro` без своих параметров (steps и
    guidance не выставлены) за 2,8× цену. → §1.3 [документация]
13. `x-ai/grok-imagine-image` в polza — базовая модель января 2026 ($0.02), не Grok Imagine Image 2.0 (#4 AA): оценки 2.0
    на неё не переносить. → §2.22, §3.5 [документация]
14. Seedream в прямом API ставит видимый знак «AI-generated» (`watermark: true` по умолчанию); что делает провайдер mie —
    неизвестно. Тест 2 (3 ₽) — до любых серий на Seedream. → §1.5 [документация] [поправка фазы 5, 25.09.2026: через mie видимой метки нет — E-01
    (Seedream 4) и углы 7 кадров Seedream 4.5 / 5 Pro; C2PA Valid]
15. Google Nano Banana — SynthID всегда + C2PA; OpenAI GPT Image — C2PA (Conforming Generator) + SynthID с 19.05.2026;
    Meta Muse — Content Seal; у BFL, Qwen, xAI, ByteDance C2PA в прочитанной документации не описан → проверять файлы
    `c2patool`/`exiftool` (тест 7, 0 ₽). → §1.5 [документация] [поправка X 24.09.2026 по L `12/02` §4.1: было «у OpenAI… не описан»]
    [поправка фазы 5, 25.09.2026: по 254 выходам — OpenAI через polza C2PA Trusted 71 из 73; Google через mie — через раз (NB2 8 из 19, NB Pro 1 из 5,
    NB2 Lite 19 из 21); Seedream, FLUX.2 — Valid; Z-Image, Qwen 2.1 — ничего; Qwen Image 3 (RouterAI) — строка TC260 →
    `../99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md`]
16. Imagen 4 выключен (Vertex 30.06.2026, Gemini API 17.08.2026); Midjourney V8.2 без официального API; Muse Image —
    только продукты Meta в США; HunyuanImage 3.0 — лицензия не действует в ЕС, UK и Южной Корее. Не предлагать для
    конвейера. → §3.1, §3.8, §3.10, §3.11 [документация]
17. Кириллицу заявляют Google (ru-RU в списке языков), Seedream 5.0 Pro (русский промт), Qwen-Image-3.0-Pro («12 languages»
    без списка); OpenAI языки не перечисляет. Независимо: генерацию русского текста мерит только LingT2I (08.2026) на
    моделях 2025 года (русский 0.29 против 0.67 у английского в среднем; «Nano Banana» 0.47 против 0.68); правку —
    MultiTextEdit (№1 Nano Banana 2); публичные тесты: дословно 4/4 у GPT Image 2 и Grok 2.0, 2/4 у NB2. Модели 2026 года
    на русском никто не мерил → тест 1. → `03-capabilities-by-task.md` §17 [исследование] [поправка фазы 5, 25.09.2026: E-02 — баннер из 3 строк
    дословно у 6 из 9 моделей polza (Flare, GPT Image 2, NB2, NB Pro, Seedream 5 Pro, Seedream 4.5), ошибки — Qwen 2.1 и FLUX.2
    Pro, Sunburst — «– 30»; Recraft V4.1 (RouterAI) — 3 из 3; 1 образец → `../99-raw/phase5/runs/2.1-cyrillic/E-02.ocr.txt`]
18. Nano Banana 2 добавляет непрошеный текст и перефразирует (WeGenBench: precision 0.43; klerk): в промте «только этот
    текст, дословно, без другого текста» и проверка OCR. → §2.8 [исследование]
19. FLUX.2 [pro]/[max] переписывают промт по умолчанию (`disable_pup: false`), в polza выключить нельзя: A/B «JSON против
    прозы» — только через прямой API BFL. → §2.12 [документация]
20. Самый дешёвый черновик — `tongyi-mai/z-image` 1,4 ₽ (промт ≤ 1000 символов, без референсов, AA #74); лучший дешёвый
    по аренам — `google/gemini-3.1-flash-lite-image` 2,9 ₽ (AA #13). Переносимость черновика на дорогую модель никто не
    мерил → тест 9. → §2.10, §2.21 [исследование]
21. Токенные провайдеры polza: ₽ = $ вендора × 117,992. Nano Banana Pro через Google flex ≈ 7,9 ₽ за 1K — дешевле плоских
    13,5 ₽ у mie/bananalab, если media-эндпоинт даёт выбрать провайдера (не подтверждено). → §1.6 [проверено]
22. Параметры одной модели у провайдеров polza различаются: `openai/gpt-5.4-image-2` — mie (4K, 6 соотношений, 16 реф.)
    против openai (до 2K, 10 соотношений с 21:9, 10 реф.); Nano Banana Pro — 8 (mie), 14 (bananalab), 10 (Google)
    референсов. Читать `providers[].parameters`, а не общее описание. → §1.3 [проверено]
23. Прямой API OpenAI: цена GPT Image 2.5 зависит от `quality` — 1024² low $0.006, high $0.053, max $0.211; 16:9 4K high
    $0.100. Названия уровней между версиями не переносятся: `high` у 2.5 = `medium` у GPT Image 2. → §2.1 [проверено]
24. FLUX.2 [flex] в polza (14/24 ₽) ради текста не брать: AA Text Rendering #22, ниже GPT и Nano Banana. → §2.13
    [исследование]
25. Seedream 5.0 Pro — второй голос для фото, портретов, 3D (LMArena #8–9), но в polza только 1K/2K и без 21:9; Seedream
    5.0 Lite — дешёвая доводка (AA Enhancement #11 за 4 ₽). → §2.14–2.15 [исследование]
26. Сильнейшие вне polza: Grok Imagine Image 2.0 (AA #4, Knowledge #1), MAI-Image-2.6 (AA #5 при $0.039), Muse Image
    (AA #7), Qwen-Image-3.0-Pro (Layout #5). Доступ — задача P. → §3 [исследование]
27. Числа арен — английские промты, 1:1, дефолты вендора; разница < 20 Elo внутри одного диапазона мест — не различие.
    → §1.2 [документация]

## 1. Как читать карточки

### 1.1 Поля карточки и YAML

| Поле YAML | Что внутри | Откуда |
|---|---|---|
| `slug`, `name`, `vendor`, `family`, `status`, `status_note` | имя, статус: `current`, `current-previous`, `legacy`, `deprecated`, `dead`, `no-api` | документация вендора, deprecations |
| `polza_id`, `ids` | id в polza; имя в прямом API; имена в аренах | каталог [S1], вендор |
| `release` | дата релиза у вендора; `polza_added` — дата появления в polza (не релиз!) | changelog вендора, каталог |
| `access`, `input`, `output`, `sizes`, `quality`, `params_*` | провайдеры, лимиты промта, референсы, маска, форматы, альфа, соотношения, разрешения | каталог + документация |
| `text.latin` / `text.cyrillic` | `claims` — заявления вендора; `independent` — арены, бенчмарки, публичные тесты | раздельно, с метками |
| `editing`, `series` | правка, референсы, стиль-коды, seed | документация, арены |
| `prompt_dialect` | ссылка на гайд, формат, негатив, JSON, hex, язык, 5–9 правил | гайд вендора (метод — у D) |
| `tasks` | `IMG-*` → [оценка, метка, доказательство] | арены, бенчмарки, документация |
| `price`, `speed` | ₽ polza и $ прямого API на 23.09.2026; секунды (AA, медиана) | каталог, прайсы, AA |
| `provenance` | видимый знак, невидимый (SynthID и т. п.), C2PA | документация |
| `license`, `defects`, `routing`, `phase5` | ограничения, типичные дефекты, маршрутизация, номера тестов фазы 5 | — |
| `arenas` | места и баллы по срезам AA (t2i 20, правка 18) и LMArena (t2i 8, правка 5) | [проверено] |
| `polza` | нормализованный блок каталога: провайдеры, параметры с описаниями, цены (плоские, по условиям, токенные с оценкой ₽ за картинку) | [проверено] |
| `checked`, `sources` | дата проверки; URL | — |

### 1.2 Метки, арены, числа

- Метки доказательности — как в `PLAN.md`. `[исследование]` у арен означает слепые попарные голоса людей, а не проверку
  задачи: арена не отвечает на вопросы «бесшовно ли», «держит ли кириллицу», «попал ли в hex».
- AA [S36–S38]: Bradley-Terry → Elo, якорь FLUX.2 [dev] = 1000; генерация с дефолтами API вендора, 1:1, seed 42,
  английские промты, негатив пустой; GPT Image 2.5 — в режиме `max`, GPT Image 2 — `high`. CI ±7…±12 Elo.
- LMArena [S39–S40]: снимок 21.09.2026; `gpt-image-2 (medium)`, `grok-imagine-image-2.0 (low)`, `gemini-3-pro-image-2k` —
  режимы арены; «предв.» — предварительный рейтинг (мало голосов). В правке надёжны 5 срезов (Overall, Cartoon,
  Photorealistic, Portraits, Text Rendering).
- Строка «Арены» в карточке: `AA t2i «имя»: All #1 1197, Text #4 1161…` = место и Elo в срезе. Полные таблицы —
  YAML (`arenas`) и `99-raw/experiments/C1/03-…`, `04-…`.

### 1.3 Дубли, версии и устаревшие id в polza (ответ на вопрос 2)

| Группа | id polza | Что это на самом деле | Вывод |
|---|---|---|---|
| GPT Image 2.5 | `openai/gpt-image-2.5-sunburst`, `gpt-image-2-5-flare` | две модели 08.09.2026: база (качество) и малая (скорость) | не дубли; цена одна → по умолчанию Flare |
| GPT Image 2 | `openai/gpt-5.4-image-2` | GPT Image 2 (21.04.2026), имя по схеме OpenRouter | предыдущий флагман; нужен ради AA Text Rendering #1 и 21:9 у провайдера openai |
| GPT Image 1.x | `openai/gpt-image-1.5`, `openai/gpt-5-image`, `openai/gpt-5-image-mini` | gpt-image-1.5, gpt-image-1, gpt-image-1-mini | **устаревшие**: выключение у OpenAI 01.12.2026 / 23.10.2026 / 01.12.2026 [S8] |
| Nano Banana 2 | `google/gemini-3.1-flash-image-preview` ≡ `google/gemini-3.1-flash-image` | одна модель; preview-имя выключено в Gemini API 25.06.2026 | **дубль**: плоские 4,8 ₽ (mie/bananalab) — у preview-id; GA-id — только Google, параметры не описаны |
| Nano Banana Pro | `google/gemini-3-pro-image-preview` | `gemini-3-pro-image` (GA 28.05.2026) под старым именем | не дубль, но имя устарело; что вызывают mie/bananalab — [не проверено] |
| Nano Banana Lite / 1 | `google/gemini-3.1-flash-lite-image`, `google/gemini-2.5-flash-image` | Lite (30.06.2026) и legacy 2.5 Flash Image | 2.5 **устарела**: Google советует Lite; Lite выше на 107 Elo при той же цене 2,9 ₽ |
| FLUX.2 | `black-forest-labs/flux.2-pro`, `black-forest-labs/flux.2-flex` | одна линейка; у flex в прямом API steps/guidance | flex в polza — **дубль без преимущества**, 14 против 5 ₽ |
| Seedream | `seedream/5-pro-text-to-image`, `bytedance/seedream-5-lite`, `bytedance/seedream-4.5`, `bytedance/seedream-4` | четыре поколения/уровня одной линейки | не дубли: у 4.0 — seed и 4K за 3 ₽, у 4.5 — 14 реф. и 4K за 5 ₽, у 5 Pro — качество и русский промт |
| Qwen-Image | `qwen/image-2.1`, `qwen/image-2`, `qwen/image` | 2.1 (20.09.2026), ≈ qwen-image-2.0 (03.2026), ≈ Qwen-Image 20B (08.2025) | 2.0 и исходная — **устаревшие** (AA #68 и #101) |
| Grok | `x-ai/grok-imagine-image` | базовая `grok-imagine-image` (01.2026) | не 2.0; 2.0 в polza нет |
| Прочие | `tongyi-mai/z-image`, `topaz/image-upscale` | Z-Image (Turbo или Base — не указано); Topaz (модель не указана) | уникальны в polza |

### 1.4 Кто что умеет: прозрачность, маска, референсы, seed, негатив, соотношения, 4K (ответ на вопрос 3)

«polza» — что выставлено в каталоге [S1]; «прямой» — только в API вендора. Референсы — максимум у провайдеров polza.

| Модель | Прозрачный фон | Маска | Референсы polza / вендор | seed | Негатив | 21:9 | 8:1 | 4K |
|---|---|---|---|---|---|---|---|---|
| GPT Image 2.5 Sunburst / Flare | прямой (`background: transparent`) | прямой (альфа-маска, «guidance») | 16 / несколько | нет | нет (проза) | polza да (+27:16, 9:8) | нет (прямой до 3:1) | polza да (не 1:1) |
| GPT Image 2 (`gpt-5.4-image-2`) | прямой (preview с 20.08.2026) | прямой | mie 16, openai 10 | нет | нет | только провайдер openai | нет | mie да |
| GPT Image 1.5 / 1 / 1-mini | прямой (1 и 1.5) | **polza: `gpt-5-image@mie` `mask_url`** | 1.5: 16; 1: mie 5, openai 10; 1-mini: 10 | нет | нет | у 1 — провайдер openai | нет | нет |
| Nano Banana Pro | нет | нет (семантическая) | mie 8, bananalab 14, Google 10 / 14 (6 объектов + 5 персонажей + 3 стиля) | chat-параметр у Google | нет (семантический) | да | нет (Vertex: 8:1 указан [спорно]) | да |
| Nano Banana 2 (оба id) | нет | нет | 14 / 14 (10 объектов + 4 персонажа) | chat-параметр у Google | нет | да | прямой да, polza нет | да |
| Nano Banana 2 Lite | нет | нет | 10 / «до 14», но «not optimized» | chat-параметр у Google | нет | да | **polza да** (1:8, 4:1, 1:4) | нет (1K) |
| Nano Banana (2.5) | нет | нет | 8–14 / лучше до 3 | chat-параметр у Google | нет | да | нет | нет |
| FLUX.2 [pro] / [flex] | нет | нет (FLUX Erase — вне polza) | 8 / 8 (10 в playground) | прямой | нет («No negative prompts») | нет | нет | нет (до 4 МП) |
| Seedream 5.0 Pro | прямой: только i2i из входа с альфой; слои PNG (до 16) | нет (координаты, рамки, стрелки) | 10 / 10 | нет | нет | нет в polza (прямой 1/16…16) | прямой | нет (до 2K) |
| Seedream 5.0 Lite | нет | нет | 10 / 14 | нет | нет | да | прямой | прямой 4K; polza до 3K |
| Seedream 4.5 | нет | нет | 14 / 14 | нет | нет | да | прямой | **polza да (high)** |
| Seedream 4.0 | нет | нет | 10 / 14 | **polza да** | нет | да | прямой | **polza да** |
| Qwen-Image-2.1 | **polza да** | **polza да** (белое = менять) | 10 / 10 | **polza да** | нет | нет | нет | нет (2K) |
| Qwen-Image 2.0 / исходная | нет | нет | 3 / 1 | нет | прямой (Model Studio, 2.0) | нет | нет | нет |
| Z-Image | нет | нет | 0 | нет | Base — CFG (веса) | нет | нет | нет |
| Grok Imagine (база) | нет | нет | 1 | нет | нет | прямой [не проверено] | нет | нет |
| Topaz Upscale | прямой (Transparent Image Upscale); polza — ? | — | 1 вход | — | — | — | — | ×2…×8 |
| Вне polza: Ideogram 4.0 | прямой (Transparent Background v4) | инструменты | Remix | — | — | до 6:1 | нет | нет (2048) |
| Вне polza: Recraft V4.x | прямой (`removeBackground`) | inpaint — только V3; у V4.x — erase region [поправка X 24.09.2026 по G] | `style_id` из ≤ 10 | `random_seed` | только V2/V3 | до 2:1 [частично] | нет | Pro 2K |
| Вне polza: Grok Imagine 2.0 | продукт, не API | продукт (magic wand) | 5 | — | нет | да (+2:1, 5:2) | нет | нет (2k) |
| Вне polza: Qwen-Image-3.0-Pro | нет | нет | 1–3 | — | — | да | **да (1:8…8:1)** | нет (2K) |
| Вне polza: Midjourney V8.2 | нет | редактор | sref, moodboards | `--seed` | `--no` | да | да (до 14:1) | HD 2048 |

Выводы: прозрачность в polza — одна модель (Qwen 2.1); маска — две; негатив — ни одной; `--tile` (бесшовность) есть
только у Midjourney без API — во всех остальных бесшовность делается постобработкой (у H).

### 1.5 Водяные знаки и происхождение (ответ на вопрос 5)

| Модель / семейство | Видимый знак | Невидимый | C2PA | Источник |
|---|---|---|---|---|
| Google Nano Banana (Pro, 2, 2 Lite, 2.5) | нет | SynthID, всегда | да | [S14], [S11] |
| Imagen 4 (выключена) | нет | «Digital watermarking and verification» — Supported | Not supported | [S15] |
| Seedream (прямой API BytePlus) | **«AI-generated» справа внизу по умолчанию** (`watermark: true`) | не описано | не описано | [S21] |
| Seedream через polza (mie) | неизвестно — тест 2 | — | — | — |
| Qwen-Image 2.0 (Model Studio) | параметр `watermark` (в примерах false) | не описано | не описано | [S24] |
| Meta Muse Image | нет | Content Seal (устойчив к кропу и сжатию) | не описано | [S33] |
| OpenAI GPT Image 2.5/2/1.x | нет | **SynthID** с 19.05.2026 (партнёрство с Google) | **да** — «C2PA Conforming Generator» с 19.05.2026 | L `../12-legal-provenance/02-labeling-ai-act-provenance.md` §4.1 [S9 там] [поправка X 24.09.2026: было «не описано / не упомянут; openai.com — 403»] |
| FLUX.2, Qwen 2.1, Z-Image, Grok, Recraft, Ideogram, MAI, Midjourney, Hunyuan | не описано | не описано | не описано | — |

Тест 7 фазы 5: `exiftool -a -G1` и `c2patool` на каждом файле тестов 1–16 — 0 ₽, закрывает вопрос по всем моделям,
вызванным через polza (провайдер может снимать метаданные при перекодировании).

### 1.6 Цены на 23.09.2026 (полная сводка и калькулятор — у B)

| Модель | polza, ₽ за картинку | Прямой API, $ | AA, $ за 1000 (1024²) |
|---|---|---|---|
| GPT Image 2.5 Sunburst / Flare | 4 / 7 / 11 (1K/2K/4K) | $30/1M вых. токенов: 1024² low 0.006 · high 0.053 · max 0.211 | 210,7 (max) |
| GPT Image 2 (`gpt-5.4-image-2`) | mie 4 / 7 / 11; openai — токены ($30/1M) | 1024² low 0.006 · medium 0.053 · high 0.211 | 211 (high) |
| GPT Image 1.5 | medium 3 · high 16,5 | 1024² 0.009 / 0.034 / 0.133 | 133 (high) |
| GPT-5 Image / Mini (gpt-image-1 / -mini) | mie 4,5; openai $40/1M · $8/1M | — | 167 / 11 |
| Nano Banana Pro | 13,5 / 13,5 / 18 (mie, bananalab); Google ≈ 15,86 / 15,86 / 28,32; flex ≈ 7,93 / 7,93 / 14,16 | 1K–2K 0.134 · 4K 0.24 | 134 |
| Nano Banana 2 | preview-id: 4,8 / 7,2 / 10,8; Google ≈ 7,93 / 11,89 / 17,84; Vertex flex ≈ 3,96 / 5,95 / 8,92 | 0.5K 0.045 · 1K 0.067 · 2K 0.101 · 4K 0.151 | 67 |
| Nano Banana 2 Lite | 2,9 (mie); Google ≈ 3,96 (только 1K) | 1K 0.0336 | 33,6 |
| Nano Banana (2.5) | 2,9 (mie) · 3 (bananalab); Google ≈ 4,57 | 0.039 | 39 |
| FLUX.2 [pro] / [flex] | 5 / 7 · 14 / 24 (1K/2K) | от 0.03 · от 0.05 (0.06/МП) | 30 · 60 |
| Seedream 5.0 Pro | basic 5 · high 10 (+0,3 за реф. со 2-го) | — | 90 |
| Seedream 5.0 Lite / 4.5 / 4.0 | 4 / 5 / 3 (любое качество) | — | 35 / 40 / 30 |
| Qwen-Image-2.1 / 2.0 / исходная | 3 / 6 (1K/2K) · 4 · 2,25–3 | — (2.1 — веса) | — · 35 · 20 |
| Z-Image | 1,4 | — | 5 (Turbo) |
| Grok Imagine (база) | 2,5 | 0.02 | 20 |
| Topaz Upscale | 7,5 (×1, ×2) · 15 (×4) · 30 (×8) | — | — |
| Вне polza: Grok 2.0 · MAI-2.6 · Muse · Qwen-3.0-Pro | — | 0.04–0.08 · — · — · 0.04 / 0.075 | 60 · 38,9 · 10 · 40 |
| Вне polza: Recraft V4.1 · Ideogram 4.0 · FLUX.2 [max] | — | 0.035 (Pro 0.21, Vector 0.08) · — · от 0.07 | 35 · 100 (Quality) · 70 |

Правило пересчёта токенных провайдеров polza: ₽ = $ × 117,992 (все пары каталога, [проверено]). Токены на
картинку у Google: Pro 1120 (1K/2K) и 2000 (4K); 3.1 Flash 747 / 1120 / 1680 / 2520 (0.5K/1K/2K/4K); 2.5 Flash 1290 [S12].
Оценки «≈» — только картинка-выход, без входных токенов и токенов рассуждения.

## 2. Модели polza (23)

### 2.1 GPT Image 2.5 Sunburst · `openai/gpt-image-2.5-sunburst`

- **Статус:** `current` — флагман OpenAI («Default»; «Our most capable model for image generation and editing»). Вендор: OpenAI. Релиз: 2026-09-08; в polza с 2026-09-10.
- **Идентификаторы:** прямой API: gpt-image-2.5-sunburst; gpt-image-2.5-sunburst-2026-09-08.
- **Доступ:** polza: mie; 4/7/11 ₽ за 1K/2K/4K; без quality, background, маски, seed; прямой API: OpenAI Image API (/v1/images/generations, /v1/images/edits) и Responses API tool image_generation; может потребоваться API Organization Verification.
- **Вход:** промт: 20000; референсы: polza: 16; прямой API: несколько (пример гайда — 4); лимит для 2.5 в гайде не указан; маска: polza: нет; прямой API: PNG с альфа-каналом того же размера, «entirely prompt-based… may not follow its exact shape»; применяется к первой картинке.
- **Выход:** форматы (прямой API): png; jpeg; webp; альфа: прямой API: background: transparent (png/webp); polza: не выставлено; сжатие: output_compression 0–100 для jpeg/webp; потоковая выдача: partial_images 0–3 (+100 токенов за каждую).
- **Размеры и соотношения:** polza: разрешения: 1K; 2K; 4K; соотношения: auto; 1:1; 3:2; 2:3; 4:3; 3:4; 16:9; 9:16; 21:9; 27:16; 16:27; 9:8; 8:9; примечание: auto — только 1K; для 1:1 нет 4K; прямой API: любой WxH кратно 16; соотношение до 3:1; 655 360–8 294 400 px; сторона ≤ 3840; выше 2560×1440 — experimental.
- **Параметры:** качество: прямой API: low; medium; high; xhigh; max; auto; polza: не выставлено — какой уровень отдаёт mie, неизвестно [не проверено].
- **Текст латиницей:** заявления — гайд: «can still struggle with precise text placement and clarity» (Limitations); независимо — AA Text Rendering #4, 1161 Elo (max) [исследование 2026-09-23]; LMArena Text Rendering #1, 1466 [исследование 2026-09-21].
- **Текст кириллицей:** заявления — языки не перечислены; независимо — Хабр/StudyAI (≈ 22.09.2026, N=1; вариант 2.5 не указан): без заметных ошибок [мнение]; LingT2I и MultiTextEdit GPT Image 2.5 не содержат.
- **Правка:** AA editing #1 в 16 из 18 срезов (All 1179; Text or Symbol 1191; Identity 1209; Composition & Framing 1218) [исследование]; LMArena Image Edit #1, 1526 [исследование]; маска в прямом API — подсказка, а не граница; пиксельная неизменность — композитингом (гайд).
- **Серия:** до 16 референсов в polza; роли по номерам; официально: консистентность персонажа — через повтор эталона и описания; «may occasionally struggle to maintain visual consistency» (Limitations).
- **Диалект промта** (гайд: https://developers.openai.com/api/docs/guides/image-prompting): формат: проза или разделы scene/subject/details/constraints; JSON допустим без особого статуса («Choose the format that makes the requirements easiest to read and update rather than relying on special syntax»); негатив-параметр: нет; негатив прозой: работает: «No extra text, no watermarks, no unrelated logos» в официальных примерах; hex: не документирован как механизм; цвета — словами и hex как пожелание [не проверено]; язык: языки не перечислены; русский текст в опубликованных тестах верен (см. 05-cyrillic); длина: 20 000 символов в polza (mie); 32 000 у провайдера openai для GPT-5.4 Image 2.
  1. Начать с результата и назначения: «product photograph / advertisement / diagram», композиция, соотношение, ограничения размещения.
  2. Сложный бриф — разделами с метками: scene, subject, details, constraints.
  3. Видимое описывать материалом, светом, цветом, медиумом; «photorealistic»/«real photograph» явно; камера — «cue, not a guarantee».
  4. Точный текст — в кавычках, с позицией и типографикой; редкие слова по буквам; «Render the tagline exactly once»; «No extra text».
  5. Правка: «change only X» + перечень сохраняемого (лицо, геометрия, раскладка, свет, надписи) + исключения.
  6. Референсы — по номеру и роли: «image 1 — subject, image 2 — style»; объяснить, что куда переносится.
  7. Итерации по одной правке; повторять ограничения; пиксельную неизменность дать композитингом, а не промтом.
  8. Параметры (quality, size, background) — не в промте, а в API; xhigh/max — только если high не проходит критерий.
- **По задачам:** `IMG-HERO-PHOTO` — лидер [исследование] (AA All #1 1197; Live-Action #1 1227; Human Anatomy #1 1225; Lighting #1; LMArena Photoreal #1); `IMG-PRODUCT` — лидер [исследование] (AA Retail & E-commerce #1 1200; LMArena Product/Branding #1); `IMG-ILLUSTR` — лидер [исследование] (AA Animation & Gaming #3; LMArena Cartoon #1, Art #1); `IMG-SERIES` — сильная [исследование] (AA Identity Preserving #1; консистентность серии как таковая аренами не мерится); `IMG-ICON3D` — лидер [исследование] (LMArena 3D Imaging #1 1414); `IMG-CUTOUT` — сильная (прямой API) [документация] (background: transparent в прямом API; в polza не выставлено); `IMG-BG-ABSTRACT` — сильная [не проверено] (специальных данных нет); `IMG-TEXTURE` — нет параметра tile [документация] (бесшовность — постобработкой); `IMG-TEXT-LATIN` — лидер [исследование] (AA TR #4; LMArena TR #1); `IMG-TEXT-CYR` — сильная [мнение] (N=1 (Хабр); проверить в фазе 5, тест 1); `IMG-EDIT` — лидер [исследование] (AA/LMArena editing #1); `IMG-OUTPAINT` — сильная [исследование] (AA Composition & Framing #1 1218; отдельного outpaint-эндпоинта нет — через edit + новый size); `IMG-MOCKUP` — сильная [исследование] (AA UI/UX #2 1220; реальный скриншот — вставлять композитингом/Blender); `IMG-UPSCALE` — нет [документация] (не апскейлер; 4K-вывод в polza); `IMG-DRAFT` — дорого для перебора [документация] (в polza нет low; в прямом API low 1024² = $0.0059).
- **Цена (23.09.2026):** polza, ₽: 1K: 4; 2K: 7; 4K: 11; прямой API, $: картинка-выход $30/1M токенов; вход-картинка $8/1M (кэш $2); текст $5/1M (кэш $1.25). 1024² high $0.053, max $0.211; 3840×2160 high $0.100, max $0.400 [проверено]; AA: $210.7 за 1000 (max, 1024²).
- **Скорость:** AA медиана ≈ 108 с на картинку в режиме max (1024²) [исследование; значение снято с графика]; гайд: «Complex prompts may take up to 2 minutes».
- **Водяные знаки и происхождение:** видимый: нет; невидимый: в прочитанной документации (image-generation, image-prompting, страницы моделей) не описано; C2PA: в прочитанной документации не упомянут; openai.com (справка) не открылась (403) — проверить c2patool в тесте 7 [не проверено].
- **Модерация:** moderation: auto|low в прямом API; ошибки image_generation_user_error / moderation_blocked с moderation_stage.
- **Типичные дефекты:** мелкий придуманный текст; точное размещение элементов по координатам; повторяющиеся персонажи между генерациями; задержка до 2 мин на max.
- **Маршрутизация:** Финальный hero/продукт/иллюстрация, где важен результат с первой попытки. Сначала Flare на тех же промтах: если проходит — брать Flare (быстрее при той же цене в polza). Прозрачность и маска — только прямой API OpenAI (в polza нет).
- **Фаза 5:** тест 3 (Sunburst против Flare в polza: фактические пиксели, время, детализация); тест 7 (метаданные: C2PA/EXIF, поля ответа polza) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Арены (место · балл):** AA t2i «GPT Image 2.5 Sunburst (max)»: All #1 1197, Text #4 1161, UI/UX #2 1220, Retail #1 1200, Live-Action #1 1227, Animation #3 1177, Layout #1 1244; AA правка «GPT Image 2.5 Sunburst (max)»: All #1 1179, Text/Symbol #1 1191, Identity #1 1209, Composition #1 1218; LMArena t2i «gpt-image-2.5-sunburst»: Overall #1 1423 предв., Text #1 1466 предв., Photoreal #1 1427 предв., Product #1 1415 предв., 3D #1 1414 предв.; LMArena правка «gpt-image-2.5-sunburst»: Overall #1 1526 предв., Text #1 1583 предв.
- **Источники:** [S1], [S5], [S6], [S4], [S7], [S36], [S39], [S67], [S48], [S41], [S37], [S40]; YAML: `models/gpt-image-2-5-sunburst.yaml`.

### 2.2 GPT Image 2.5 Flare · `gpt-image-2-5-flare`

[поправка фазы 5, 25.09.2026: с 25.09 id в polza — `openai/gpt-image-2.5-flare`; фаза 5: 16 генераций (4–7 ₽), E-08 «хорошо», E-12 —
единственная из 4 держит стиль серии, E-02 — кириллица дословно, C2PA Trusted 16 из 16]

- **Статус:** `current` — «Fast, high-quality everyday image generation»; «small model… image quality comparable to GPT Image 2». Вендор: OpenAI. Релиз: 2026-09-08; в polza с 2026-09-10.
- **Идентификаторы:** прямой API: gpt-image-2.5-flare; gpt-image-2.5-flare-2026-09-08; примечание: id в polza без префикса вендора.
- **Доступ:** polza: mie; 4/7/11 ₽ (как Sunburst); прямой API: OpenAI Image API и Responses tool.
- **Вход:** промт: 20000; референсы: polza: 16; маска: polza: нет; прямой API: как у Sunburst.
- **Выход:** форматы (прямой API): png; jpeg; webp; альфа: прямой API: background: transparent; polza: не выставлено.
- **Размеры и соотношения:** polza: разрешения: 1K; 2K; 4K; соотношения: auto; 1:1; 9:16; 16:9; 4:3; 3:4; 3:2; 2:3; 21:9; 27:16; 16:27; 9:8; 8:9; примечание: auto — только 1K; для 1:1 нет 4K; прямой API: как у Sunburst.
- **Параметры:** качество: прямой API: low; medium; high; xhigh; max; auto; polza: не выставлено.
- **Текст латиницей:** заявления — нет; независимо — AA Text Rendering #2, 1179 [исследование]; LMArena Text Rendering #2, 1436.
- **Текст кириллицей:** заявления — нет; независимо — Хабр/StudyAI (≈ 22.09.2026, N=1; вариант 2.5 не указан): без заметных ошибок [мнение]; GPT Image 2 — 4/4 дословно (klerk, 26.08.2026, проверено глазами) [мнение].
- **Правка:** AA editing #2 1159; LMArena edit #2 1482 [исследование].
- **Серия:** как Sunburst.
- **Диалект промта** (гайд: https://developers.openai.com/api/docs/guides/image-prompting): формат: проза или разделы scene/subject/details/constraints; JSON допустим без особого статуса («Choose the format that makes the requirements easiest to read and update rather than relying on special syntax»); негатив-параметр: нет; негатив прозой: работает: «No extra text, no watermarks, no unrelated logos» в официальных примерах; hex: не документирован как механизм; цвета — словами и hex как пожелание [не проверено]; язык: языки не перечислены; русский текст в опубликованных тестах верен (см. 05-cyrillic); длина: 20 000 символов в polza (mie); 32 000 у провайдера openai для GPT-5.4 Image 2.
  1. Начать с результата и назначения: «product photograph / advertisement / diagram», композиция, соотношение, ограничения размещения.
  2. Сложный бриф — разделами с метками: scene, subject, details, constraints.
  3. Видимое описывать материалом, светом, цветом, медиумом; «photorealistic»/«real photograph» явно; камера — «cue, not a guarantee».
  4. Точный текст — в кавычках, с позицией и типографикой; редкие слова по буквам; «Render the tagline exactly once»; «No extra text».
  5. Правка: «change only X» + перечень сохраняемого (лицо, геометрия, раскладка, свет, надписи) + исключения.
  6. Референсы — по номеру и роли: «image 1 — subject, image 2 — style»; объяснить, что куда переносится.
  7. Итерации по одной правке; повторять ограничения; пиксельную неизменность дать композитингом, а не промтом.
  8. Параметры (quality, size, background) — не в промте, а в API; xhigh/max — только если high не проходит критерий.
- **По задачам:** `IMG-HERO-PHOTO` — лидер [исследование] (AA All #2 1191; Live-Action #3; Human Anatomy #2); `IMG-PRODUCT` — лидер [исследование] (AA Retail #2 1171); `IMG-ILLUSTR` — лидер [исследование] (AA Animation & Gaming #1 1211); `IMG-MOCKUP` — лидер [исследование] (AA UI/UX Design #1 1229); `IMG-TEXT-LATIN` — лидер [исследование] (AA TR #2; Marketing & Advertising #1 1175); `IMG-TEXT-CYR` — вероятно сильная [не проверено] (тест 1 фазы 5); `IMG-EDIT` — лидер [исследование] (AA editing #2); `IMG-SERIES` — сильная [исследование] (AA Identity Preserving #2 1199); `IMG-DRAFT` — годится как «дешёвый финал» [документация] (та же цена, что Sunburst, в polza; быстрее в прямом API (AA ≈ 56 с на max)).
- **Цена (23.09.2026):** polza, ₽: 1K: 4; 2K: 7; 4K: 11; прямой API, $: те же ставки, что Sunburst; токенов на картинку может быть иначе («Equal token rates don't mean equal cost per image»).
- **Скорость:** AA медиана ≈ 56 с (max, 1024²) [исследование; с графика].
- **Водяные знаки и происхождение:** видимый: нет; невидимый: не описано; C2PA: не упомянут в прочитанной документации — тест 7 [не проверено].
- **Типичные дефекты:** как у Sunburst.
- **Маршрутизация:** Модель по умолчанию для веб-ассетов в polza: цена = Sunburst, скорость выше, в UI/UX и Marketing — №1 AA. Sunburst — если Flare не прошла критерий (правка с сохранением деталей, фотореализм людей).
- **Фаза 5:** тест 1 (кириллица); тест 3; тест 5 (серия); тест 6 (продукт); тест 8 (hex); тест 9 (черновик → Flare); тест 10 (аутпейнт); тест 13 (текстура); тест 15 (латиница); тест 16 (мокап) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Арены (место · балл):** AA t2i «GPT Image 2.5 Flare (max)»: All #2 1191, Text #2 1179, UI/UX #1 1229, Retail #2 1171, Live-Action #3 1192, Animation #1 1211, Layout #3 1215; AA правка «GPT Image 2.5 Flare (max)»: All #2 1159, Text/Symbol #2 1159, Identity #2 1199, Composition #2 1189; LMArena t2i «gpt-image-2.5-flare»: Overall #2 1401 предв., Text #2 1436 предв., Photoreal #2 1417 предв., Product #2 1395 предв., 3D #2 1384 предв.; LMArena правка «gpt-image-2.5-flare»: Overall #2 1482 предв., Text #2 1530 предв.
- **Источники:** [S1], [S6], [S4], [S48], [S47], [S36], [S37], [S39], [S40]; YAML: `models/gpt-image-2-5-flare.yaml`.

### 2.3 GPT Image 2 (в polza — «OpenAI: GPT-5.4 Image 2») · `openai/gpt-5.4-image-2`

- **Статус:** `current-previous` — предыдущий флагман (21.04.2026); OpenAI советует новым интеграциям GPT Image 2.5. Вендор: OpenAI. Релиз: 2026-04-21; в polza с 2026-04-22.
- **Идентификаторы:** прямой API: gpt-image-2; gpt-image-2-2026-04-21; примечание: название в polza по схеме OpenRouter (GPT-5.4 + gpt-image-2) [предположение по названию].
- **Доступ:** polza: два провайдера: mie (1K/2K/4K, 6 соотношений, 16 реф., 4/7/11 ₽) и openai (1K/2K, 10 соотношений до 21:9, 10 реф., токены: картинка-выход $30/1M); прямой API: Image API, Batch API −50 %.
- **Вход:** промт: mie: 20000; openai: 32000; референсы: mie: 16; openai: 10; маска: polza: нет; прямой API: как у 2.5; input_fidelity: не передавать — всегда high.
- **Выход:** форматы (прямой API): png; jpeg; webp; альфа: прямой API: background: transparent (preview с 20.08.2026); polza: не выставлено.
- **Размеры и соотношения:** polza: mie: разрешения: 1K; 2K; 4K; соотношения: auto; 1:1; 9:16; 16:9; 4:3; 3:4; openai: разрешения: 1K; 2K; соотношения: 1:1; 2:3; 3:2; 3:4; 4:3; 4:5; 5:4; 9:16; 16:9; 21:9; прямой API: как у 2.5; популярные 2048×2048, 2048×1152, 3840×2160, 2160×3840.
- **Параметры:** качество: прямой API: low; medium; high; auto; polza: не выставлено.
- **Текст латиницей:** заявления — нет; независимо — **AA Text Rendering #1, 1195 (high)** [исследование]; LMArena TR #3 1423 (medium); WeGenBench (zh/en): Char F1 0.56, семантика QA 0.97 — лучшая [исследование, 2606.20100].
- **Текст кириллицей:** заявления — нет; независимо — klerk/Genova (26.08.2026): 4/4 макета дословно, без орфографических ошибок; мелкий текст на экране ноутбука верен (проверено глазами, N=4) [мнение].
- **Правка:** AA editing #5 1121; LMArena edit #3 1461.
- **Серия:** до 16 реф. (mie).
- **Диалект промта** (гайд: https://developers.openai.com/api/docs/guides/image-prompting): формат: проза или разделы scene/subject/details/constraints; JSON допустим без особого статуса («Choose the format that makes the requirements easiest to read and update rather than relying on special syntax»); негатив-параметр: нет; негатив прозой: работает: «No extra text, no watermarks, no unrelated logos» в официальных примерах; hex: не документирован как механизм; цвета — словами и hex как пожелание [не проверено]; язык: языки не перечислены; русский текст в опубликованных тестах верен (см. 05-cyrillic); длина: 20 000 символов в polza (mie); 32 000 у провайдера openai для GPT-5.4 Image 2.
  1. Начать с результата и назначения: «product photograph / advertisement / diagram», композиция, соотношение, ограничения размещения.
  2. Сложный бриф — разделами с метками: scene, subject, details, constraints.
  3. Видимое описывать материалом, светом, цветом, медиумом; «photorealistic»/«real photograph» явно; камера — «cue, not a guarantee».
  4. Точный текст — в кавычках, с позицией и типографикой; редкие слова по буквам; «Render the tagline exactly once»; «No extra text».
  5. Правка: «change only X» + перечень сохраняемого (лицо, геометрия, раскладка, свет, надписи) + исключения.
  6. Референсы — по номеру и роли: «image 1 — subject, image 2 — style»; объяснить, что куда переносится.
  7. Итерации по одной правке; повторять ограничения; пиксельную неизменность дать композитингом, а не промтом.
  8. Параметры (quality, size, background) — не в промте, а в API; xhigh/max — только если high не проходит критерий.
- **По задачам:** `IMG-TEXT-LATIN` — лидер [исследование] (AA TR #1; Productivity & Knowledge #1 1229; Reasoning #1); `IMG-TEXT-CYR` — сильная [мнение] (klerk N=4, дословно); `IMG-HERO-PHOTO` — сильная [исследование] (AA #3); `IMG-MOCKUP` — сильная [исследование] (AA UI/UX #3 1204); `IMG-EDIT` — сильная [исследование] (AA editing #5).
- **Цена (23.09.2026):** polza, ₽: mie: 1K: 4; 2K: 7; 4K: 11; openai: токены: вход 943,94 ₽/1M ($8), текст-выход 1769,88 ₽/1M ($15), картинка-выход 3539,76 ₽/1M ($30); прямой API, $: 1024² low/medium/high = $0.006/$0.053/$0.211 (таблица OpenAI; порт формулы совпал).
- **Водяные знаки и происхождение:** видимый: нет; невидимый: не описано; C2PA: не упомянут в прочитанной документации [не проверено].
- **Маршрутизация:** Текст латиницей, инфографика, слайды — по AA №1 в Text Rendering и Productivity; цена в polza та же, что у 2.5. Для 21:9 выбрать провайдера openai (у mie нет 21:9) — как выбрать провайдера для /v1/media, не подтверждено (вопрос B).
- **Фаза 5:** тест 1 (кириллица) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Бенчмарки (вне арен):** RISEBench (правка с рассуждением, лидерборд 23.04.2026): GPT-Image-2 49,4 % — #2 [исследование]; Qwen-Image-Bench (05.2026, бенчмарк команды Qwen): GPT Image 2 65.23 [исследование вендора]; WeGenBench (06.2026, zh/en): QA 0.97, COT 8.95, AM 2.84 — лучшие; Char F1 0.56 [исследование].
- **Арены (место · балл):** AA t2i «GPT Image 2 (high)»: All #3 1171, Text #1 1195, UI/UX #3 1204, Retail #4 1142, Live-Action #2 1196, Animation #4 1174, Layout #2 1219; AA правка «GPT Image 2 (high)»: All #5 1121, Text/Symbol #8 1128, Identity #3 1167, Composition #3 1146; LMArena t2i «gpt-image-2»: Overall #3 1381, Text #3 1423, Photoreal #3 1380, Product #3 1387, 3D #3 1362; LMArena правка «gpt-image-2»: Overall #3 1461, Text #3 1526.
- **Источники:** [S1], [S4], [S6], [S47], [S42], [S64], [S66], [S36], [S37], [S39], [S40]; YAML: `models/gpt-5-4-image-2.yaml`.

### 2.4 GPT Image 1.5 · `openai/gpt-image-1.5`

- **Статус:** `deprecated` — OpenAI: shutdown 01.12.2026 (уведомление 02.06.2026), замена — gpt-image-2. Вендор: OpenAI. Релиз: 2025-12-16; в polza с 2026-02-20.
- **Идентификаторы:** прямой API: gpt-image-1.5; gpt-image-1.5-2025-12-16.
- **Доступ:** polza: mie; medium 3 ₽ / high 16,5 ₽; aspect_ratio обязателен (1:1, 2:3, 3:2).
- **Вход:** референсы: polza: 16; маска: polza: нет; input_fidelity: low|high (прямой API).
- **Выход:** альфа: прямой API: background: transparent; polza: нет.
- **Размеры и соотношения:** polza: соотношения: 1:1; 2:3; 3:2; прямой API: 1024², 1024×1536, 1536×1024, auto.
- **Параметры:** качество: polza: medium; high; прямой API: low; medium; high; auto.
- **Текст латиницей:** заявления — нет; независимо — AA TR #6 1111.
- **Текст кириллицей:** заявления — нет; независимо — MultiTextEdit (правка, 12 языков): SemAvg 3.577, разрыв EN/не-EN 0.517 — второй после NB2 [исследование].
- **Диалект промта** (гайд: https://developers.openai.com/api/docs/guides/image-prompting): формат: проза или разделы scene/subject/details/constraints; JSON допустим без особого статуса («Choose the format that makes the requirements easiest to read and update rather than relying on special syntax»); негатив-параметр: нет; негатив прозой: работает: «No extra text, no watermarks, no unrelated logos» в официальных примерах; hex: не документирован как механизм; цвета — словами и hex как пожелание [не проверено]; язык: языки не перечислены; русский текст в опубликованных тестах верен (см. 05-cyrillic); длина: 20 000 символов в polza (mie); 32 000 у провайдера openai для GPT-5.4 Image 2.
  1. Начать с результата и назначения: «product photograph / advertisement / diagram», композиция, соотношение, ограничения размещения.
  2. Сложный бриф — разделами с метками: scene, subject, details, constraints.
  3. Видимое описывать материалом, светом, цветом, медиумом; «photorealistic»/«real photograph» явно; камера — «cue, not a guarantee».
  4. Точный текст — в кавычках, с позицией и типографикой; редкие слова по буквам; «Render the tagline exactly once»; «No extra text».
  5. Правка: «change only X» + перечень сохраняемого (лицо, геометрия, раскладка, свет, надписи) + исключения.
  6. Референсы — по номеру и роли: «image 1 — subject, image 2 — style»; объяснить, что куда переносится.
  7. Итерации по одной правке; повторять ограничения; пиксельную неизменность дать композитингом, а не промтом.
  8. Параметры (quality, size, background) — не в промте, а в API; xhigh/max — только если high не проходит критерий.
  9. Отличия 1.5: `input_fidelity` low|high; размеры только 1024², 1024×1536, 1536×1024, auto; в polza — только 1:1, 2:3, 3:2 и quality medium|high.
- **По задачам:** `IMG-EDIT` — сильная [исследование] (AA editing #12; MultiTextEdit #2); `IMG-DRAFT` — годится [документация] (medium 3 ₽ — дешёвый вход в линейку OpenAI, но уходит 01.12.2026).
- **Цена (23.09.2026):** polza, ₽: medium: 3; high: 16.5; прямой API, $: картинка-выход $32/1M; 1024² low/medium/high $0.009/$0.034/$0.133.
- **Водяные знаки и происхождение:** видимый: нет; C2PA: не упомянут в прочитанной документации [не проверено].
- **Маршрутизация:** Не закладывать в долгие конвейеры: выключение у OpenAI 01.12.2026.
- **Бенчмарки (вне арен):** RISEBench (23.04.2026): GPT-Image-1.5 51,4 % — №1 [исследование]; GEditBench v2 (03.2026): 1071 — #3; выполнение инструкции 1260 (лучшее), согласованность 846 (худшая) [исследование]; WISE_Verified (26.06.2026): 0.825 — #4; T2I-CoReBench: 78.2 [исследование]; MultiTextEdit (05.2026): SemAvg 3.577, разрыв EN/не-EN 0.517 [исследование].
- **Арены (место · балл):** AA t2i «GPT Image 1.5 (high)»: All #8 1103, Text #6 1111, UI/UX #12 1118, Retail #8 1098, Live-Action #9 1108, Animation #10 1133, Layout #14 1128; AA правка «GPT Image 1.5 (high)»: All #12 1102, Text/Symbol #13 1096, Identity #6 1150, Composition #13 1092; LMArena t2i «gpt-image-1.5-high-fidelity»: Overall #15 1239, Text #17 1253, Photoreal #15 1248, Product #14 1240, 3D #15 1215; LMArena правка «gpt-image-1.5-high-fidelity»: Overall #15 1370, Text #14 1392.
- **Источники:** [S1], [S8], [S4], [S41], [S64], [S63], [S55], [S65], [S36], [S37], [S39], [S40]; YAML: `models/gpt-image-1-5.yaml`.

### 2.5 OpenAI: GPT-5 Image (на базе gpt-image-1) · `openai/gpt-5-image`

- **Статус:** `deprecated` — по названию (схема OpenRouter) — GPT-5 + gpt-image-1 [предположение]; gpt-image-1 выключается у OpenAI 23.10.2026. Вендор: OpenAI. Релиз: —; в polza с 2026-01-28.
- **Идентификаторы:** прямой API: gpt-image-1.
- **Доступ:** polza: mie 4,5 ₽ за запрос (prompt ≤ 4000, 1:1/3:2/2:3, ≤ 5 реф., mask_url, isEnhance) и openai (токены: картинка-выход $40/1M; 10 соотношений; ≤ 10 реф.; prompt ≤ 32 000).
- **Вход:** маска: polza: mask_url у mie: «Чёрные области = менять, белые = оставить» — полярность противоположна qwen/image-2.1 [документация polza].
- **Текст латиницей:** заявления — нет; независимо — AA GPT Image 1 (high) #37 1008; CVTG-2K 0.8569, LongText EN 0.956 (техотчёт Z-Image) [исследование].
- **Диалект промта** (гайд: https://developers.openai.com/api/docs/guides/image-prompting): формат: проза или разделы scene/subject/details/constraints; JSON допустим без особого статуса («Choose the format that makes the requirements easiest to read and update rather than relying on special syntax»); негатив-параметр: нет; негатив прозой: работает: «No extra text, no watermarks, no unrelated logos» в официальных примерах; hex: не документирован как механизм; цвета — словами и hex как пожелание [не проверено]; язык: языки не перечислены; русский текст в опубликованных тестах верен (см. 05-cyrillic); длина: 20 000 символов в polza (mie); 32 000 у провайдера openai для GPT-5.4 Image 2.
  1. Начать с результата и назначения: «product photograph / advertisement / diagram», композиция, соотношение, ограничения размещения.
  2. Сложный бриф — разделами с метками: scene, subject, details, constraints.
  3. Видимое описывать материалом, светом, цветом, медиумом; «photorealistic»/«real photograph» явно; камера — «cue, not a guarantee».
  4. Точный текст — в кавычках, с позицией и типографикой; редкие слова по буквам; «Render the tagline exactly once»; «No extra text».
  5. Правка: «change only X» + перечень сохраняемого (лицо, геометрия, раскладка, свет, надписи) + исключения.
  6. Референсы — по номеру и роли: «image 1 — subject, image 2 — style»; объяснить, что куда переносится.
  7. Итерации по одной правке; повторять ограничения; пиксельную неизменность дать композитингом, а не промтом.
  8. Параметры (quality, size, background) — не в промте, а в API; xhigh/max — только если high не проходит критерий.
  9. Отличия GPT Image 1: `input_fidelity` low|high; размеры 1024², 1024×1536, 1536×1024; у mie промт ≤ 4000 символов и `isEnhance` (переписывание).
- **По задачам:** `IMG-EDIT` — средняя [исследование] (единственная (кроме Qwen 2.1) модель polza с маской — у mie).
- **Цена (23.09.2026):** polza, ₽: mie: 4.5.
- **Водяные знаки и происхождение:** видимый: нет; C2PA: не упомянут в прочитанной документации [не проверено].
- **Маршрутизация:** Использовать только ради маски до 23.10.2026, дальше — qwen/image-2.1 + mask_url. Полярность маски у mie («чёрное = менять») противоположна Qwen 2.1 («белое = менять»). Прямой API OpenAI требует маску с альфа-каналом (пример гайда кладёт ч/б маску в альфу: чёрное → прозрачное); какая область правится, в прочитанном тексте явно не сказано [не проверено].
- **Бенчмарки (вне арен):** MultiBanana: GPT-Image-1 при 2 референсах 6.585 против 4.891 у Nano Banana [исследование]; KRIS-Bench (06.05.2026): GPT-4o / GPT-Image-1 80.09 — №1 [исследование]; R2I-Bench: gpt-image-1 0.77 — №1; T2I-ReasonBench (ACL): GPT-Image-1 86.3 — #2 [исследование]; ImgEdit 4.20; GEdit-Bench EN 7.53; CVTG-2K 0.8569; LongText EN 0.956 (техотчёт Z-Image, 2025) [исследование].
- **Арены (место · балл):** AA t2i «GPT Image 1 (high)»: All #37 1008, Text #32 991, UI/UX #41 1000, Retail #25 1016, Animation #45 1000, Layout #43 1010; AA правка «GPT Image 1 (high)»: All #49 978, Text/Symbol #41 977, Identity #48 995, Composition #40 969; LMArena t2i «gpt-image-1»: Overall #47 1115, Text #49 1115, Photoreal #52 1115, Product #48 1115, 3D #48 1114; LMArena правка «gpt-image-1»: Overall #51 1139.
- **Источники:** [S1], [S8], [S72], [S60], [S57], [S56], [S26], [S36], [S37], [S39], [S40]; YAML: `models/gpt-5-image.yaml`.

### 2.6 OpenAI: GPT-5 Image Mini (на базе gpt-image-1-mini) · `openai/gpt-5-image-mini`

- **Статус:** `deprecated` — gpt-image-1-mini — shutdown 01.12.2026; в polza только провайдер openai с токенной ценой. Вендор: OpenAI. Релиз: —; в polza с 2026-01-28.
- **Доступ:** polza: openai; токены: вход $2.5/1M, текст-выход $2/1M, картинка-выход $8/1M; параметров только prompt ≤ 32 000 и images ≤ 10.
- **Текст латиницей:** заявления — нет; независимо — AA GPT Image 1 Mini (medium) #86 915.
- **Диалект промта** (гайд: https://developers.openai.com/api/docs/guides/image-prompting): формат: проза или разделы scene/subject/details/constraints; JSON допустим без особого статуса («Choose the format that makes the requirements easiest to read and update rather than relying on special syntax»); негатив-параметр: нет; негатив прозой: работает: «No extra text, no watermarks, no unrelated logos» в официальных примерах; hex: не документирован как механизм; цвета — словами и hex как пожелание [не проверено]; язык: языки не перечислены; русский текст в опубликованных тестах верен (см. 05-cyrillic); длина: 20 000 символов в polza (mie); 32 000 у провайдера openai для GPT-5.4 Image 2.
  1. Начать с результата и назначения: «product photograph / advertisement / diagram», композиция, соотношение, ограничения размещения.
  2. Сложный бриф — разделами с метками: scene, subject, details, constraints.
  3. Видимое описывать материалом, светом, цветом, медиумом; «photorealistic»/«real photograph» явно; камера — «cue, not a guarantee».
  4. Точный текст — в кавычках, с позицией и типографикой; редкие слова по буквам; «Render the tagline exactly once»; «No extra text».
  5. Правка: «change only X» + перечень сохраняемого (лицо, геометрия, раскладка, свет, надписи) + исключения.
  6. Референсы — по номеру и роли: «image 1 — subject, image 2 — style»; объяснить, что куда переносится.
  7. Итерации по одной правке; повторять ограничения; пиксельную неизменность дать композитингом, а не промтом.
  8. Параметры (quality, size, background) — не в промте, а в API; xhigh/max — только если high не проходит критерий.
- **По задачам:** `IMG-DRAFT` — слабая [исследование] (AA #86; дешевле и лучше — nano-banana-2-lite / z-image).
- **Цена (23.09.2026):** polza, ₽: токены провайдера openai: вход 294,98 ₽/1M ($2.5), текст-выход 235,98 ₽/1M ($2), картинка-выход 943,94 ₽/1M ($8); AA: $11 за 1000 (medium, 1024²).
- **Водяные знаки и происхождение:** видимый: нет; C2PA: не упомянут в прочитанной документации [не проверено].
- **Маршрутизация:** Не использовать: устаревает, качество ниже дешёвых альтернатив.
- **Арены (место · балл):** AA t2i «GPT Image 1 Mini (medium)»: All #86 915, Live-Action #70 935, Animation #84 908; AA правка «GPT Image 1 Mini (medium)»: All #62 921, Text/Symbol #57 861, Identity #58 921, Composition #46 928; LMArena t2i «gpt-image-1-mini»: Overall #51 1109, Text #53 1104, Photoreal #53 1114, Product #53 1109, 3D #51 1109; LMArena правка «gpt-image-1-mini»: Overall #53 1124, Text #40 1167.
- **Источники:** [S1], [S8], [S36], [S37], [S39], [S40]; YAML: `models/gpt-5-image-mini.yaml`.

### 2.7 Nano Banana Pro (Gemini 3 Pro Image) · `google/gemini-3-pro-image-preview`

- **Статус:** `current` — GA `gemini-3-pro-image` с 28.05.2026; id в polza `…-preview` — устаревшее имя (preview выключен в Gemini API 25.06.2026) — что реально вызывается у mie/bananalab, не проверено. Вендор: Google. Релиз: preview 2025-11-20; GA 2026-05-28; в polza с 2026-01-28.
- **Идентификаторы:** прямой API: gemini-3-pro-image; устаревшие id: gemini-3-pro-image-preview (выключен 25.06.2026); в аренах: AA: Nano Banana Pro (Gemini 3 Pro Image); LMArena: gemini-3-pro-image-2k, gemini-3-pro-image-preview.
- **Доступ:** polza: mie (8 реф.), bananalab (14 реф.) — 13,5 ₽ за 1K/2K, 18 ₽ за 4K; Google Vertex / AI Studio (global и /flex) — токены; cloud-ru — только текст в каталоге; прямой API: Gemini API (Interactions API, `response_format{type:image, aspect_ratio, image_size}`), Vertex AI → Gemini Enterprise Agent Platform (retirement «May 28, 2027 or later»); Batch — да.
- **Вход:** промт: 20 000 (mie/bananalab), 16 000 (Google); контекст 65 536 токенов; референсы: Google: до 14 всего — до 6 объектов + до 5 персонажей + до 3 стилевых; «supports 5 images with high fidelity»; polza: mie 8, bananalab 14, Google 10; маска: нет (только «semantic masking» текстом); прочее: Search grounding — да; thinking — всегда (до 2 «thought images», тарифицируются).
- **Выход:** форматы: картинка + текст в одном ответе; альфа: нет.
- **Размеры и соотношения:** polza: 1K/2K/4K; 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 (+auto у mie/bananalab); прямой API: 1K и 2K = 1120 токенов, 4K = 2000 (16:9 4K = 5504×3072); на Vertex для Pro перечислены и 1:4, 4:1, 1:8, 8:1, в Gemini API — только у 3.1 Flash [спорно].
- **Параметры:** качество: уровня качества нет; thinking всегда включён.
- **Текст латиницей:** заявления — «highest level of world knowledge, advanced localization, accurate brand consistency, and precision creative control» (страница модели); polza changelog: «NanoBanana Pro (до 4K с точным текстом)»; независимо — AA Text Rendering #11 1081 — ниже Nano Banana 2 (#8) [исследование 23.09.2026]; LMArena Text Rendering #13 (2k) 1270 / #16 (preview) 1254 [исследование 21.09.2026]; UniGenBench++: «Nano Banana Pro and Seedream-4.0 excel in Chinese text rendering» [исследование].
- **Текст кириллицей:** заявления — Gemini API Limitations: «For best performance, use the following languages: EN, ar-EG, de-DE, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN»; независимо — отдельных замеров русского текста у Pro не найдено.
- **Правка:** AA editing #13 1096; Reasoning-Based Edit #5 1137; Productivity edit #5 1166 [исследование]; LMArena Image Edit #9 (2k) 1390, #13 (preview) 1385.
- **Серия:** до 5 персонажей и 3 стилевых референсов — самый развитый набор ролей референсов среди моделей polza [документация]; AA Identity Preserving #9 1140; ViStoryBench (серии, 29.08.2026): №1; OmniRef-Bench (2–7 реф.): 8.50 — №1; GPT Image 2/2.5 в этих бенчмарках нет [исследование].
- **Диалект промта** (гайд: https://ai.google.dev/gemini-api/docs/image-generation ; https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana): формат: естественный язык; формулы гайда Cloud: t2i «[Subject]+[Action]+[Location/context]+[Composition]+[Style]»; с референсами «[Reference images]+[Relationship instruction]+[New scenario]»; с поиском «[Source/Search request]+[Analytical task]+[Visual translation]»; негатив-параметр: нет; негатив прозой: «semantic negative prompts»: описывать желаемое состояние («an empty, deserted street with no signs of traffic» вместо «no cars»); JSON: особого статуса в гайдах нет [документация: не упомянут]; hex: не документирован [не проверено]; язык: лучшее качество — 15 языков, включая ru-RU (Limitations гайда); «Write your prompt in one language and specify a target language» для локализации.
  1. Гипер-конкретно: объект, действие, место, композиция, стиль; начинать с сильного глагола.
  2. Указывать назначение и контекст картинки (для сайта — где будет текст, какой отступ).
  3. Для фона под текст — шаблон «Minimalist & negative space design»: объект в углу, «vast, empty … canvas … negative space for text».
  4. Текст — в кавычках; шрифт описанием или названием («Century Gothic 12px»); сначала сгенерировать текст, потом просить картинку с ним («text-first hack»).
  5. Негатив — только семантически, позитивным описанием; «no X» работает хуже.
  6. Референсы: роль каждой картинки и отношение между ними; для Pro — до 6 объектов + 5 персонажей + 3 стилевых.
  7. Язык камеры (объектив, ракурс, глубина резкости) — для фотореализма.
  8. Правка — пошаговыми инструкциями в диалоге; маски-картинки нет, только «semantic masking» текстом.
  9. Число картинок в ответе не гарантировано («won't always follow the exact number of image outputs»).
- **По задачам:** `IMG-HERO-PHOTO` — сильная [исследование] (AA Live-Action #7 1114; LMArena Photoreal #12 1259); `IMG-PRODUCT` — средняя [исследование] (AA Retail #15 1068 — ниже NB2 (#7) и дороже в 2,8 раза в polza); `IMG-SERIES` — лидер специализированных бенчмарков [исследование] (ViStoryBench №1, OmniRef-Bench №1 (без GPT 2.x); роли референсов; AA Identity #9); `IMG-TEXT-LATIN` — средняя (вопреки позиционированию) [исследование] (AA TR #11, LMArena TR #13); `IMG-TEXT-CYR` — вероятно сильная [мнение вендора] (ru-RU в списке; независимых данных нет); `IMG-MOCKUP` — сильная для UI-состояний [исследование] (GEBench (UI-состояния): NB Pro 69.62/61.20 (CN/EN) — №1; AA UI/UX #8 1137); `IMG-EDIT` — сильная [исследование] (AA editing #13, Reasoning edit #5); `IMG-DRAFT` — нет [документация] (13,5 ₽ — самая дорогая «плоская» цена в polza).
- **Цена (23.09.2026):** polza, ₽: mie/bananalab: 13,5 (1K/2K) / 18 (4K); Google: ≈15,86 (1K/2K) / ≈28,32 (4K); Google flex: ≈7,93 / ≈14,16 (картинка-выход × токены на картинку; без входа и thinking); прямой API, $: $120/1M картинка-выход: 1K–2K $0.134, 4K $0.24; вход-картинка 560 ток. ≈ $0.0011; AA $134/1k.
- **Скорость:** AA медиана 17,0 с (1024²) [исследование; с графика].
- **Водяные знаки и происхождение:** видимый: нет; невидимый: SynthID (всегда); C2PA: да — «All generated images include C2PA Content Credentials and a SynthID watermark» (Google Cloud Blog); у Lite на странице модели «SynthID watermarking (Always On) + C2PA» [документация].
- **Типичные дефекты:** thinking-картинки и токены рассуждения тарифицируются; число выходных картинок не гарантировано; преимущество «лучший текст» арены не подтверждают.
- **Маршрутизация:** Не брать по умолчанию: по аренам ниже Nano Banana 2 при цене ×2,8 (polza). Брать для серий с персонажем/продуктом и мульти-референса (ViStoryBench и OmniRef-Bench №1; роли: до 5 персонажей + 3 стиля), для заземления поиском с рассуждением (инфографика по фактам), для UI-состояний (GEBench). В polza дешевле всего через провайдера Google flex (≈7,9 ₽ за 1K/2K), если media-эндпоинт позволяет выбрать провайдера [не проверено].
- **Фаза 5:** тест 1 (кириллица); тест 5 (серия: лидер ViStoryBench и OmniRef-Bench против GPT 2.5); тест 7 (какой провайдер и модель реально ответили на `…-preview`; SynthID/C2PA) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Бенчмарки (вне арен):** ViStoryBench (серии с персонажами, Lite, лидерборд 29.08.2026): №1 — CIDS 0.581/0.653, PA 3.37 [исследование]; OmniRef-Bench (06.2026, 2–7 референсов): 8.50 — №1 [исследование]; GEditBench v2 (03.2026): 1096 — №1 [исследование]; WISE_Verified (26.06.2026): 0.876 — #2; T2I-CoReBench: 85.0 — #2 [исследование]; RISEBench (23.04.2026): 48,3 % — #3 [исследование]; GEBench (UI-состояния): 69.62 / 61.20 (CN/EN) — №1 (по соседнему файлу ui-research).
- **Арены (место · балл):** AA t2i «Nano Banana Pro (Gemini 3 Pro Image)»: All #10 1100, Text #11 1081, UI/UX #8 1137, Retail #15 1068, Live-Action #7 1114, Animation #14 1092, Layout #11 1137; AA правка «Nano Banana Pro (Gemini 3 Pro Image)»: All #13 1096, Text/Symbol #10 1112, Identity #9 1140, Composition #19 1053; LMArena t2i «gemini-3-pro-image-2k»: Overall #14 1246, Text #13 1270, Photoreal #12 1259, Product #13 1245, 3D #12 1230; LMArena t2i «gemini-3-pro-image-preview»: Overall #16 1232, Text #16 1254, Photoreal #16 1243, Product #15 1237, 3D #16 1209; LMArena правка «gemini-3-pro-image-2k»: Overall #9 1390, Text #9 1429; LMArena правка «gemini-3-pro-image-preview»: Overall #13 1385.
- **Источники:** [S1], [S10], [S11], [S12], [S13], [S14], [S70], [S71], [S63], [S55], [S65], [S64], [S49], [S36], [S37], [S39], [S40]; YAML: `models/nano-banana-pro.yaml`.

### 2.8 Nano Banana 2 (Gemini 3.1 Flash Image) — id preview в polza · `google/gemini-3.1-flash-image-preview`

- **Статус:** `current (устаревший id)` — preview-имя; GA `gemini-3.1-flash-image` с 28.05.2026, preview выключен в Gemini API 25.06.2026. В polza под этим id — плоские цены mie/bananalab и токены Google. Вендор: Google. Релиз: preview 2026-02-26; GA 2026-05-28; в polza с 2026-02-26.
- **Идентификаторы:** прямой API: gemini-3.1-flash-image; устаревшие id: gemini-3.1-flash-image-preview; в аренах: AA: Nano Banana 2 (Gemini 3.1 Flash Image); LMArena: gemini-3.1-flash-image (nano-banana-2) [web-search].
- **Доступ:** polza: mie и bananalab — 4,8/7,2/10,8 ₽ (1K/2K/4K), до 14 реф.; Google AI Studio / Vertex — токены $60/1M (Vertex flex $30/1M), до 10 реф.; cloud-ru; прямой API: Gemini API / Vertex (регионы global, us, eu).
- **Вход:** промт: 20 000 (mie/bananalab), 16 000 (Google); контекст 131 072 (Vertex) / 65 536 (AI Studio); референсы: Google: до 10 объектов + до 4 персонажей (всего 14); polza: mie/bananalab 14, Google 10; маска: нет (semantic masking); прочее: вход также видео и PDF (видео→картинка); Image Search Grounding (веб + картинки); thinking_level minimal (по умолч.) | high.
- **Выход:** форматы: polza mie: `output_format` png|jpeg; альфа: нет.
- **Размеры и соотношения:** polza: 1K/2K/4K; 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 (+auto у mie/bananalab); 1:4…8:1 в polza НЕ выставлены; прямой API: 0.5K 747 ток. / 1K 1120 / 2K 1680 / 4K 2520; соотношения вкл. 1:4, 4:1, 1:8, 8:1, 21:9 (21:9 1K = 1584×672; 8:1 4K = 12288×1536); «K» — заглавная.
- **Текст латиницей:** заявления — «reliable text rendering», «Improved i18n text rendering» (страница модели); polza: «точной типографики и сохранения консистентности объектов»; независимо — AA Text Rendering #8 1106 — лучший Google [исследование]; LMArena TR #9 1293; edit TR #6 1443; WeGenBench (zh/en): Char F1 0.49, precision 0.43 — «massive hallucinations and typographical noise»; сложная вёрстка 0.61 [исследование].
- **Текст кириллицей:** заявления — Gemini API Limitations: «For best performance, use the following languages: EN, ar-EG, de-DE, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN»; независимо — MultiTextEdit (правка текста, 12 языков вкл. русский): SemAvg 4.006 — №1, разрыв EN/не-EN 0.100 — минимальный [исследование, arXiv 2605.08163]; klerk/Genova (26.08.2026; 4 макета, первая генерация, проверено глазами): заданный русский текст без орфографических ошибок 4/4, но дословно только 2/4 (перефразирует: «ЗАРЕГИСТРИРОВАТЬСЯ» вместо «Записаться»); добавляет латинский псевдотекст и чужой бренд [мнение, партнёрский тест]; Хабр/StudyAI (≈ 22.09.2026, N=1): «хорошо» [мнение].
- **Правка:** AA editing #9 1105; Text or Symbol Edits #5 1143 — лучший не-OpenAI в polza; Object-Level #4 1126; Reasoning edit #4 1143 [исследование]; LMArena edit #12 1388.
- **Серия:** до 14 реф. у mie/bananalab; «multiple reference image processing and consistency» [мнение вендора]; AA Identity Preserving #11 1132.
- **Диалект промта** (гайд: https://ai.google.dev/gemini-api/docs/image-generation ; https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana): формат: естественный язык; формулы гайда Cloud: t2i «[Subject]+[Action]+[Location/context]+[Composition]+[Style]»; с референсами «[Reference images]+[Relationship instruction]+[New scenario]»; с поиском «[Source/Search request]+[Analytical task]+[Visual translation]»; негатив-параметр: нет; негатив прозой: «semantic negative prompts»: описывать желаемое состояние («an empty, deserted street with no signs of traffic» вместо «no cars»); JSON: особого статуса в гайдах нет [документация: не упомянут]; hex: не документирован [не проверено]; язык: лучшее качество — 15 языков, включая ru-RU (Limitations гайда); «Write your prompt in one language and specify a target language» для локализации.
  1. Гипер-конкретно: объект, действие, место, композиция, стиль; начинать с сильного глагола.
  2. Указывать назначение и контекст картинки (для сайта — где будет текст, какой отступ).
  3. Для фона под текст — шаблон «Minimalist & negative space design»: объект в углу, «vast, empty … canvas … negative space for text».
  4. Текст — в кавычках; шрифт описанием или названием («Century Gothic 12px»); сначала сгенерировать текст, потом просить картинку с ним («text-first hack»).
  5. Негатив — только семантически, позитивным описанием; «no X» работает хуже.
  6. Референсы: роль каждой картинки и отношение между ними; для Pro — до 6 объектов + 5 персонажей + 3 стилевых.
  7. Язык камеры (объектив, ракурс, глубина резкости) — для фотореализма.
  8. Правка — пошаговыми инструкциями в диалоге; маски-картинки нет, только «semantic masking» текстом.
  9. Число картинок в ответе не гарантировано («won't always follow the exact number of image outputs»).
- **По задачам:** `IMG-HERO-PHOTO` — сильная [исследование] (AA All #6 1122 — лучший из не-OpenAI в polza; Human Anatomy #6); `IMG-PRODUCT` — сильная [исследование] (AA Retail #7 1101; LMArena Product #8 1269); `IMG-ILLUSTR` — сильная [исследование] (AA Animation & Gaming #7 1139); `IMG-ICON3D` — сильная [исследование] (LMArena 3D #7 1255); `IMG-TEXT-LATIN` — сильная [исследование] (AA TR #8, LMArena TR #9; но лишний текст (WeGenBench)); `IMG-TEXT-CYR` — сильная (правка), генерация — N=4 [исследование] (MultiTextEdit №1; klerk — верно, но не дословно); `IMG-EDIT` — сильная [исследование] (AA Text/Symbol edit #5); `IMG-OUTPAINT` — сильная [исследование] (AA Composition & Framing #8 1109); `IMG-MOCKUP` — сильная [исследование] (AA UI/UX #6 1167); `IMG-BG-ABSTRACT` — сильная [документация] (шаблон negative space гайда); `IMG-DRAFT` — годится [документация] (4,8 ₽ за 1K; быстрый (AA 8,9 с)).
- **Цена (23.09.2026):** polza, ₽: mie/bananalab: 4,8 / 7,2 / 10,8 (1K/2K/4K); Google: ≈7,93 / 11,89 / 17,84; Vertex flex: ≈3,96 / 5,95 / 8,92; прямой API, $: $60/1M картинка-выход: 0.5K $0.045, 1K $0.067, 2K $0.101, 4K $0.151; AA $67/1k.
- **Скорость:** AA медиана 8,9 с [исследование; с графика]; polza: «до 4K с задержкой 4–6 секунд» [мнение вендора/агрегатора].
- **Водяные знаки и происхождение:** видимый: нет; невидимый: SynthID (всегда); C2PA: да — «All generated images include C2PA Content Credentials and a SynthID watermark» (Google Cloud Blog); у Lite на странице модели «SynthID watermarking (Always On) + C2PA» [документация].
- **Типичные дефекты:** добавляет непрошеный текст и латинский псевдотекст (WeGenBench, klerk); перефразирует заданный текст; может нарисовать реальный бренд (klerk: «SONY» на наушниках).
- **Маршрутизация:** Лучший не-OpenAI вариант в polza для фото, продукта, UI и правки текста; вдвое дешевле Pro. Запрещать лишний текст явно и проверять OCR: «только этот текст, дословно». 8:1 и 1:4 в polza — только у Nano Banana 2 Lite (у этого id не выставлены).
- **Фаза 5:** тест 1; тест 6 (продукт по референсу); тест 8 (hex); тест 10 (аутпейнт); тест 13 (текстура); тест 15 (латиница); тест 16 (мокап); тест 7 (провайдер, SynthID/C2PA) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Бенчмарки (вне арен):** T2I-CoReBench (ICLR 2026): 85.3 — №1 [исследование]; MultiTextEdit (05.2026, 12 языков вкл. русский): SemAvg 4.006 — №1 [исследование]; WeGenBench (06.2026, zh/en): Char F1 0.49, precision 0.43 [исследование].
- **Арены (место · балл):** AA t2i «Nano Banana 2 (Gemini 3.1 Flash Image)»: All #6 1122, Text #8 1106, UI/UX #6 1167, Retail #7 1101, Live-Action #6 1122, Animation #7 1139, Layout #10 1142; AA правка «Nano Banana 2 (Gemini 3.1 Flash Image)»: All #9 1105, Text/Symbol #5 1143, Identity #11 1132, Composition #8 1109; LMArena t2i «gemini-3.1-flash-image»: Overall #9 1260, Text #9 1293, Photoreal #10 1266, Product #8 1269, 3D #7 1255; LMArena правка «gemini-3.1-flash-image»: Overall #12 1388, Text #6 1443.
- **Источники:** [S1], [S10], [S11], [S12], [S13], [S41], [S42], [S47], [S48], [S65], [S36], [S37], [S39], [S40]; YAML: `models/nano-banana-2-preview.yaml`.

### 2.9 Nano Banana 2 (Gemini 3.1 Flash Image) — GA id · `google/gemini-3.1-flash-image`

- **Статус:** `current` — та же модель, что `google/gemini-3.1-flash-image-preview`, но под GA-именем и только у провайдеров Google; `parameters` в каталоге = null — какие параметры принимает /v1/media, не описано. Вендор: Google. Релиз: GA 2026-05-28; в polza с 2026-06-24.
- **Идентификаторы:** прямой API: gemini-3.1-flash-image.
- **Доступ:** polza: google-vertex/global и google-ai-studio — токены: вход $0.50/1M, текст-выход $3/1M, картинка-выход $60/1M (58,996 / 353,976 / 7079,52 ₽ за 1M); прямой API: Gemini API / Vertex.
- **Вход:** референсы: по документации Google — до 14 (10 объектов + 4 персонажа); в каталоге polza параметры не описаны; маска: нет.
- **Выход:** альфа: нет.
- **Размеры и соотношения:** polza: в каталоге не описаны (parameters: null); прямой API: как у preview-id: 0.5K–4K, до 8:1.
- **Текст латиницей:** заявления — нет; независимо — см. nano-banana-2-preview.
- **Текст кириллицей:** заявления — нет; независимо — см. nano-banana-2-preview.
- **Диалект промта** (гайд: https://ai.google.dev/gemini-api/docs/image-generation ; https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana): формат: естественный язык; формулы гайда Cloud: t2i «[Subject]+[Action]+[Location/context]+[Composition]+[Style]»; с референсами «[Reference images]+[Relationship instruction]+[New scenario]»; с поиском «[Source/Search request]+[Analytical task]+[Visual translation]»; негатив-параметр: нет; негатив прозой: «semantic negative prompts»: описывать желаемое состояние («an empty, deserted street with no signs of traffic» вместо «no cars»); JSON: особого статуса в гайдах нет [документация: не упомянут]; hex: не документирован [не проверено]; язык: лучшее качество — 15 языков, включая ru-RU (Limitations гайда); «Write your prompt in one language and specify a target language» для локализации.
  1. Гипер-конкретно: объект, действие, место, композиция, стиль; начинать с сильного глагола.
  2. Указывать назначение и контекст картинки (для сайта — где будет текст, какой отступ).
  3. Для фона под текст — шаблон «Minimalist & negative space design»: объект в углу, «vast, empty … canvas … negative space for text».
  4. Текст — в кавычках; шрифт описанием или названием («Century Gothic 12px»); сначала сгенерировать текст, потом просить картинку с ним («text-first hack»).
  5. Негатив — только семантически, позитивным описанием; «no X» работает хуже.
  6. Референсы: роль каждой картинки и отношение между ними; для Pro — до 6 объектов + 5 персонажей + 3 стилевых.
  7. Язык камеры (объектив, ракурс, глубина резкости) — для фотореализма.
  8. Правка — пошаговыми инструкциями в диалоге; маски-картинки нет, только «semantic masking» текстом.
  9. Число картинок в ответе не гарантировано («won't always follow the exact number of image outputs»).
- **По задачам:** `IMG-*` — как nano-banana-2-preview [исследование] (одна модель).
- **Цена (23.09.2026):** polza, ₽: ≈7,93 / 11,89 / 17,84 за 1K/2K/4K (только картинка-выход); прямой API, $: как у preview-id.
- **Водяные знаки и происхождение:** видимый: нет; невидимый: SynthID (всегда); C2PA: да — «All generated images include C2PA Content Credentials and a SynthID watermark» (Google Cloud Blog); у Lite на странице модели «SynthID watermarking (Always On) + C2PA» [документация].
- **Маршрутизация:** Дубль `google/gemini-3.1-flash-image-preview`: для плоской цены 4,8 ₽ использовать preview-id (mie/bananalab); GA-id — если нужен именно провайдер Google (и его параметры подтверждены).
- **Бенчмарки (вне арен):** см. nano-banana-2-preview: T2I-CoReBench 85.3 — №1; MultiTextEdit №1 [исследование].
- **Арены (место · балл):** AA t2i «Nano Banana 2 (Gemini 3.1 Flash Image)»: All #6 1122, Text #8 1106, UI/UX #6 1167, Retail #7 1101, Live-Action #6 1122, Animation #7 1139, Layout #10 1142; AA правка «Nano Banana 2 (Gemini 3.1 Flash Image)»: All #9 1105, Text/Symbol #5 1143, Identity #11 1132, Composition #8 1109; LMArena t2i «gemini-3.1-flash-image»: Overall #9 1260, Text #9 1293, Photoreal #10 1266, Product #8 1269, 3D #7 1255; LMArena правка «gemini-3.1-flash-image»: Overall #12 1388, Text #6 1443.
- **Источники:** [S1], [S11], [S65], [S41], [S36], [S37], [S39], [S40]; YAML: `models/nano-banana-2.yaml`.

### 2.10 Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image) · `google/gemini-3.1-flash-lite-image`

- **Статус:** `current` — «fastest and cheapest»; GA 30.06.2026. Вендор: Google. Релиз: 2026-06-30; в polza с 2026-06-30.
- **Идентификаторы:** прямой API: gemini-3.1-flash-lite-image; в аренах: AA: Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image); LMArena: gemini-3.1-flash-lite-image (nano-banana-2-lite).
- **Доступ:** polza: mie 2,9 ₽ за запрос; Google Vertex / AI Studio — токены $30/1M (≈3,96 ₽ за 1K); прямой API: Gemini API / Vertex.
- **Вход:** промт: 20 000 (mie), 16 000 (Google); референсы: polza 10; Google: «до 14 объектов», но «Not optimized for multiple reference inputs or multi-turn sequential editing» [спорно]; маска: нет; прочее: Search grounding — НЕТ; thinking minimal|high; выход до 4096 токенов.
- **Выход:** альфа: нет.
- **Размеры и соотношения:** polza: только 1K; 15 соотношений: 1:1, 1:4, 4:1, 1:8, 8:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, auto — единственная модель polza с 8:1/1:8; прямой API: только 1K (1120 ток.).
- **Текст латиницей:** заявления — нет; независимо — AA TR #14 1071; LMArena TR #12 1275 [исследование].
- **Текст кириллицей:** заявления — Gemini API Limitations: «For best performance, use the following languages: EN, ar-EG, de-DE, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN»; независимо — нет данных.
- **Правка:** AA editing #23 1041; LMArena edit #21 1314 — заметно слабее NB2 в правке.
- **Серия:** вендор: не оптимизирована для мульти-референса.
- **Диалект промта** (гайд: https://ai.google.dev/gemini-api/docs/image-generation ; https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana): формат: естественный язык; формулы гайда Cloud: t2i «[Subject]+[Action]+[Location/context]+[Composition]+[Style]»; с референсами «[Reference images]+[Relationship instruction]+[New scenario]»; с поиском «[Source/Search request]+[Analytical task]+[Visual translation]»; негатив-параметр: нет; негатив прозой: «semantic negative prompts»: описывать желаемое состояние («an empty, deserted street with no signs of traffic» вместо «no cars»); JSON: особого статуса в гайдах нет [документация: не упомянут]; hex: не документирован [не проверено]; язык: лучшее качество — 15 языков, включая ru-RU (Limitations гайда); «Write your prompt in one language and specify a target language» для локализации.
  1. Гипер-конкретно: объект, действие, место, композиция, стиль; начинать с сильного глагола.
  2. Указывать назначение и контекст картинки (для сайта — где будет текст, какой отступ).
  3. Для фона под текст — шаблон «Minimalist & negative space design»: объект в углу, «vast, empty … canvas … negative space for text».
  4. Текст — в кавычках; шрифт описанием или названием («Century Gothic 12px»); сначала сгенерировать текст, потом просить картинку с ним («text-first hack»).
  5. Негатив — только семантически, позитивным описанием; «no X» работает хуже.
  6. Референсы: роль каждой картинки и отношение между ними; для Pro — до 6 объектов + 5 персонажей + 3 стилевых.
  7. Язык камеры (объектив, ракурс, глубина резкости) — для фотореализма.
  8. Правка — пошаговыми инструкциями в диалоге; маски-картинки нет, только «semantic masking» текстом.
  9. Число картинок в ответе не гарантировано («won't always follow the exact number of image outputs»).
- **По задачам:** `IMG-DRAFT` — лидер по цене/качеству [исследование] (AA t2i #13 1092 при $33.6/1k; Marketing #9 — выше NB Pro (#13); AA 3,1 с); `IMG-BG-ABSTRACT` — сильная для лент 8:1 [документация] (единственная в polza с 8:1/1:8); `IMG-HERO-PHOTO` — средняя [исследование] (AA Live-Action #12); `IMG-SERIES` — слабая [мнение вендора] («Not optimized for multiple reference inputs»); `IMG-EDIT` — слабая [исследование] (AA editing #23).
- **Цена (23.09.2026):** polza, ₽: mie 2,9; Google ≈3,96 (1K); прямой API, $: $30/1M: 1K $0.0336; AA $33.6/1k.
- **Скорость:** AA медиана 3,1 с [исследование]; вендор: «Sub-2 second end-to-end latency» [мнение вендора].
- **Водяные знаки и происхождение:** видимый: нет; невидимый: SynthID (всегда); C2PA: да — «All generated images include C2PA Content Credentials and a SynthID watermark» (Google Cloud Blog); у Lite на странице модели «SynthID watermarking (Always On) + C2PA» [документация].
- **Типичные дефекты:** только 1K — для hero нужен апскейл; мульти-референс и многошаговая правка — слабые.
- **Маршрутизация:** Перебор направлений и широкие ленты (8:1, 4:1) дешевле всех, кроме Z-Image. Финал — не выше 1K: для hero нужен апскейл или перегенерация на NB2/GPT.
- **Фаза 5:** тест 9 (черновик → перенос на Flare); тест 11 (лента 8:1) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Арены (место · балл):** AA t2i «Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)»: All #13 1092, Text #14 1071, UI/UX #11 1119, Retail #13 1080, Live-Action #12 1081, Animation #11 1122, Layout #15 1114; AA правка «Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)»: All #23 1041, Text/Symbol #17 1084, Identity #21 1069, Composition #22 1041; LMArena t2i «gemini-3.1-flash-lite-image»: Overall #13 1250, Text #12 1275, Photoreal #11 1260, Product #12 1251, 3D #13 1226; LMArena правка «gemini-3.1-flash-lite-image»: Overall #21 1314, Text #18 1358.
- **Источники:** [S1], [S11], [S12], [S36], [S37], [S39], [S40]; YAML: `models/nano-banana-2-lite.yaml`.

### 2.11 Nano Banana (Gemini 2.5 Flash Image) · `google/gemini-2.5-flash-image`

- **Статус:** `legacy` — Google: «legacy… strongly recommend… transition to Nano Banana 2 Lite». Вендор: Google. Релиз: preview 2025-08-26; GA 2025-10-02; в polza с 2026-01-28.
- **Идентификаторы:** прямой API: gemini-2.5-flash-image; в аренах: AA: Nano Banana (Gemini 2.5 Flash Image); LMArena: gemini-2.5-flash-image-preview (nano-banana).
- **Доступ:** polza: mie 2,9 ₽ (8 реф.), bananalab 3 ₽ (14 реф.), Google ($30/1M; AI Studio flex $15/1M, priority $54/1M; Vertex flex $15/1M), cloud-ru.
- **Вход:** референсы: «works best with up to 3 images as input»; polza 8/14/10; маска: нет; прочее: thinking нет; knowledge cutoff June 2025.
- **Выход:** альфа: нет.
- **Размеры и соотношения:** polza: 10 соотношений 1:1…21:9 (вкл. 4:5, 5:4); разрешения не выставлены; прямой API: 1290 ток.; 16:9 = 1344×768, 21:9 = 1536×672.
- **Текст латиницей:** заявления — нет; независимо — AA TR #46 964; LMArena TR #32 1153; PRISM-Bench текст-трек 78.5 (техотчёт Z-Image, 2025).
- **Текст кириллицей:** заявления — Gemini API Limitations: «For best performance, use the following languages: EN, ar-EG, de-DE, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN»; независимо — LingT2I (08.2026): «Nano Banana» (версия не указана) — русский 0.47 против английского 0.68; ошибки — читаемый, но не тот текст [исследование].
- **Правка:** AA editing #46 986; LMArena edit #28 1293 (11,2 млн голосов — самая «проголосованная» модель правки).
- **Диалект промта** (гайд: https://ai.google.dev/gemini-api/docs/image-generation ; https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana): формат: естественный язык; формулы гайда Cloud: t2i «[Subject]+[Action]+[Location/context]+[Composition]+[Style]»; с референсами «[Reference images]+[Relationship instruction]+[New scenario]»; с поиском «[Source/Search request]+[Analytical task]+[Visual translation]»; негатив-параметр: нет; негатив прозой: «semantic negative prompts»: описывать желаемое состояние («an empty, deserted street with no signs of traffic» вместо «no cars»); JSON: особого статуса в гайдах нет [документация: не упомянут]; hex: не документирован [не проверено]; язык: лучшее качество — 15 языков, включая ru-RU (Limitations гайда); «Write your prompt in one language and specify a target language» для локализации.
  1. Гипер-конкретно: объект, действие, место, композиция, стиль; начинать с сильного глагола.
  2. Указывать назначение и контекст картинки (для сайта — где будет текст, какой отступ).
  3. Для фона под текст — шаблон «Minimalist & negative space design»: объект в углу, «vast, empty … canvas … negative space for text».
  4. Текст — в кавычках; шрифт описанием или названием («Century Gothic 12px»); сначала сгенерировать текст, потом просить картинку с ним («text-first hack»).
  5. Негатив — только семантически, позитивным описанием; «no X» работает хуже.
  6. Референсы: роль каждой картинки и отношение между ними; для Pro — до 6 объектов + 5 персонажей + 3 стилевых.
  7. Язык камеры (объектив, ракурс, глубина резкости) — для фотореализма.
  8. Правка — пошаговыми инструкциями в диалоге; маски-картинки нет, только «semantic masking» текстом.
  9. Число картинок в ответе не гарантировано («won't always follow the exact number of image outputs»).
- **По задачам:** `IMG-DRAFT` — устарела [исследование] (AA #51 985 — ниже NB2 Lite (#13) при той же цене 2,9 ₽).
- **Цена (23.09.2026):** polza, ₽: mie 2,9; bananalab 3; Google ≈4,57 (1290 ток. × $30/1M); прямой API, $: $0.039 (batch/flex $0.0195, priority $0.0702).
- **Водяные знаки и происхождение:** видимый: нет; невидимый: SynthID (всегда); C2PA: да — «All generated images include C2PA Content Credentials and a SynthID watermark» (Google Cloud Blog); у Lite на странице модели «SynthID watermarking (Always On) + C2PA» [документация].
- **Маршрутизация:** Не использовать: за ту же цену Nano Banana 2 Lite выше на 107 Elo (AA).
- **Бенчмарки (вне арен):** ViStoryBench (Lite, 29.08.2026): Nano Banana — #2 [исследование]; LingT2I (08.2026): Nano Banana (версия не указана) — русский 0.47 против английского 0.68; читаемо, но не та строка [исследование]; MultiBanana (CVPR 2026): 1 референс 7.817 ≈ GPT-Image-1; 2 референса 4.891 против 6.585 у GPT-Image-1 [исследование]; OmniContext: Gemini 2.5 Flash Image 7.84 [исследование]; GenEval 2 (12.2025): Gemini 2.5 Flash Image 44.6 (люди 31.0) — №1 из 8 [исследование]; T2I-ReasonBench (ACL 2026): Nano-Banana 89.5 — №1; RISEBench: 33,9 % [исследование]; OneIG (лидерборд 19.09.2025): 0.878 соответствие; текст ZH 0.276 [исследование].
- **Арены (место · балл):** AA t2i «Nano Banana (Gemini 2.5 Flash Image)»: All #51 985, Text #46 964, Retail #33 1000, Live-Action #32 1022, Animation #49 995, Layout #56 969; AA правка «Nano Banana (Gemini 2.5 Flash Image)»: All #46 986, Text/Symbol #32 1014, Identity #42 1010, Composition #37 980; LMArena t2i «gemini-2.5-flash-image-preview»: Overall #33 1150, Text #32 1153, Photoreal #29 1156, Product #33 1151, 3D #38 1142; LMArena правка «gemini-2.5-flash-image-preview»: Overall #28 1293, Text #25 1284.
- **Источники:** [S1], [S10], [S13], [S12], [S67], [S70], [S72], [S73], [S53], [S64], [S56], [S58], [S36], [S37], [S39], [S40]; YAML: `models/nano-banana.yaml`.

### 2.12 FLUX.2 [pro] · `black-forest-labs/flux.2-pro`

- **Статус:** `current` — «recommended default» у BFL; FLUX 3 для картинок ещё не выпущен (анонс 23.07.2026, сначала видео). Вендор: Black Forest Labs. Релиз: 2025-11-25; ×2 быстрее и `-preview` — 2026-03-03; в polza с 2026-02-20.
- **Идентификаторы:** прямой API: /v1/flux-2-pro (фиксированный снимок); /v1/flux-2-pro-preview (последняя версия); в аренах: AA: FLUX.2 [pro]; LMArena: flux-2-pro.
- **Доступ:** polza: mie; 5 ₽ (1K) / 7 ₽ (2K); прямой API: api.bfl.ai (асинхронно, webhook; результат по подписанной ссылке 10 минут); MCP mcp.bfl.ai.
- **Вход:** промт: 5000 (polza); референсы: до 8 (polza и API; 10 в playground); лимит 9 МП вход+выход; маска: нет (маска — отдельный инструмент FLUX Erase вне polza).
- **Выход:** форматы: API: jpeg (по умолч.) | png | webp; polza: не выставлено; альфа: нет.
- **Размеры и соотношения:** polza: 1K/2K; 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3; прямой API: width/height ≥ 64, кратно 16, до 4 МП.
- **Параметры:** прямой API: seed, safety_tolerance 0–5 (2), disable_pup, output_format, webhook — в polza ничего из этого нет.
- **Текст латиницей:** заявления — гайд: текст в кавычках с hex-цветом; независимо — AA TR #41 975 [исследование]; LMArena TR #30 1156.
- **Текст кириллицей:** заявления — гайд: промт на родном языке допустим; независимо — Хабр/studyai (N=1): «можжевельник» с пропущенной буквой [мнение].
- **Правка:** AA editing #37 1006; LMArena edit #33 1245 — в правке слабее, чем в генерации.
- **Серия:** до 8 референсов; seed в API (не в polza).
- **Диалект промта** (гайд: https://docs.bfl.ml/guides/prompting_guide_flux2): формат: проза или JSON — «FLUX.2 understands both formats equally well»; JSON-схема: scene, subjects[description, position, action], style, color_palette, lighting, mood, background, composition, camera{angle, lens, depth_of_field}; негатив-параметр: нет; негатив прозой: «No negative prompts» — описывать желаемое, а не запреты; JSON: да, рекомендован для автоматизации и сложных сцен; проза — для поиска направления; hex: да: со словом «color»/«hex» и привязкой к объекту («The car is #FF0000» лучше «use red #FF0000»); градиенты — начальный и конечный цвет; язык: «Prompt in your native language for more culturally authentic results».
  1. Порядок: Subject + Action + Style + Context; главное — в начало («pays more attention to what comes first»).
  2. Длина 30–80 слов обычно идеальна (10–30 — быстрые пробы, 80+ — сложные сцены).
  3. Негативов нет: вместо «no people» — «empty street at dawn».
  4. Фотостиль — названием камеры/плёнки («shot on Sony A7IV», «Kodak Portra 400»).
  5. Текст — в кавычках + место + стиль + размер + hex-цвет.
  6. Hex — с привязкой к объекту; бренд-палитра — полем color_palette в JSON.
  7. Мульти-референс — ссылаться на картинки по номеру; [pro] при 1 МП — до 8 входов, при 2 МП — до 7 (лимит 9 МП вход+выход).
  8. Разрешение кратно 16, до 4 МП, рекомендовано до 2 МП.
  9. Prompt upsampling у [pro]/[max] включён по умолчанию (`disable_pup: true` — ровно по промту); в polza параметра нет → промт, вероятно, переписывается [не проверено].
- **По задачам:** `IMG-BG-ABSTRACT` — сильная (управление цветом) [документация] (hex и color_palette в JSON — единственный из polza с документированным hex); `IMG-ILLUSTR` — средняя [исследование] (AA Animation & Gaming #40); `IMG-HERO-PHOTO` — средняя [исследование] (AA All #39 1002; Live-Action #31); `IMG-TEXT-LATIN` — слабая [исследование] (AA TR #41); `IMG-TEXT-CYR` — слабая [мнение] (N=1); `IMG-EDIT` — слабая [исследование] (AA editing #37).
- **Цена (23.09.2026):** polza, ₽: 5 (1K) / 7 (2K); прямой API, $: от $0.03 t2i, от $0.045 правка (1 кредит = $0.01); AA $30/1k.
- **Скорость:** AA медиана 10,9 с [исследование; с графика].
- **Водяные знаки и происхождение:** видимый: нет; невидимый: в прочитанной документации BFL не описано; C2PA: в прочитанной документации BFL не описано — проверить c2patool (тест 7) [не проверено].
- **Типичные дефекты:** промт переписывается (upsampling) — дословность и JSON-эксперименты искажены; текст и правка — середина таблиц.
- **Маршрутизация:** Брать ради hex/JSON-палитры и предсказуемого «дизайнерского» стиля за 5 ₽; не брать для текста и правки. Для чистого A/B «JSON против прозы» нужен прямой API с `disable_pup: true`.
- **Фаза 5:** тест 1 (кириллица); тест 8 (hex) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Арены (место · балл):** AA t2i «FLUX.2 [pro]»: All #39 1002, Text #41 975, UI/UX #43 997, Retail #36 995, Live-Action #31 1023, Animation #40 1007, Layout #45 1001; AA правка «FLUX.2 [pro]»: All #37 1006, Text/Symbol #33 1013, Identity #39 1013, Composition #36 985; LMArena t2i «flux-2-pro»: Overall #29 1154, Text #30 1156, Photoreal #33 1152, Product #29 1156, 3D #33 1148; LMArena правка «flux-2-pro»: Overall #33 1245, Text #29 1257.
- **Источники:** [S1], [S16], [S17], [S18], [S19], [S48], [S36], [S37], [S39], [S40]; YAML: `models/flux-2-pro.yaml`.

### 2.13 FLUX.2 [flex] · `black-forest-labs/flux.2-flex`

- **Статус:** `current` — «Specialized for typography… Best for text rendering and preserving small details» [мнение вендора]. Вендор: Black Forest Labs. Релиз: 2025-11-25; ×3 быстрее — 2026-01-29; в polza с 2026-02-20.
- **Идентификаторы:** прямой API: /v1/flux-2-flex; в аренах: AA: FLUX.2 [flex]; LMArena: flux-2-flex.
- **Доступ:** polza: mie; 14 ₽ (1K) / 24 ₽ (2K); прямой API: api.bfl.ai.
- **Вход:** промт: 5000 (polza); референсы: до 8; маска: нет.
- **Выход:** форматы: API: jpeg|png|webp; альфа: нет.
- **Размеры и соотношения:** polza: 1K/2K; 7 соотношений (как у pro); прямой API: до 4 МП, кратно 16.
- **Параметры:** прямой API: steps 1–50 (50), guidance 1.5–10 (5), prompt_upsampling (true), seed — в polza ничего из этого нет, т. е. главное отличие [flex] недоступно.
- **Текст латиницей:** заявления — «Best for text rendering»; независимо — AA TR #22 1006 — лучше [pro] (#41), но далеко за GPT/NB [исследование]; LMArena TR #26 1172.
- **Текст кириллицей:** заявления — нет; независимо — нет данных.
- **Правка:** AA editing #38 1005 ($120/1k); LMArena edit #39 1225.
- **Диалект промта** (гайд: https://docs.bfl.ml/guides/prompting_guide_flux2): формат: проза или JSON — «FLUX.2 understands both formats equally well»; JSON-схема: scene, subjects[description, position, action], style, color_palette, lighting, mood, background, composition, camera{angle, lens, depth_of_field}; негатив-параметр: нет; негатив прозой: «No negative prompts» — описывать желаемое, а не запреты; JSON: да, рекомендован для автоматизации и сложных сцен; проза — для поиска направления; hex: да: со словом «color»/«hex» и привязкой к объекту («The car is #FF0000» лучше «use red #FF0000»); градиенты — начальный и конечный цвет; язык: «Prompt in your native language for more culturally authentic results».
  1. Порядок: Subject + Action + Style + Context; главное — в начало («pays more attention to what comes first»).
  2. Длина 30–80 слов обычно идеальна (10–30 — быстрые пробы, 80+ — сложные сцены).
  3. Негативов нет: вместо «no people» — «empty street at dawn».
  4. Фотостиль — названием камеры/плёнки («shot on Sony A7IV», «Kodak Portra 400»).
  5. Текст — в кавычках + место + стиль + размер + hex-цвет.
  6. Hex — с привязкой к объекту; бренд-палитра — полем color_palette в JSON.
  7. Мульти-референс — ссылаться на картинки по номеру; [pro] при 1 МП — до 8 входов, при 2 МП — до 7 (лимит 9 МП вход+выход).
  8. Разрешение кратно 16, до 4 МП, рекомендовано до 2 МП.
  9. Prompt upsampling у [pro]/[max] включён по умолчанию (`disable_pup: true` — ровно по промту); в polza параметра нет → промт, вероятно, переписывается [не проверено].
- **По задачам:** `IMG-TEXT-LATIN` — средняя [исследование] (AA TR #22 при цене 14 ₽); `IMG-MOCKUP` — средняя [исследование] (AA UI/UX #20 1065); `IMG-HERO-PHOTO` — средняя [исследование] (AA All #20 1026; Physics #14 1060).
- **Цена (23.09.2026):** polza, ₽: 14 (1K) / 24 (2K) — ≈ $0.12/$0.20 по курсу polza; прямой API, $: от $0.05 (обзор: $0.06/МП); AA $60/1k.
- **Водяные знаки и происхождение:** видимый: нет; невидимый: в прочитанной документации BFL не описано; C2PA: в прочитанной документации BFL не описано — проверить c2patool (тест 7) [не проверено].
- **Маршрутизация:** В polza не брать: в 2,8 раза дороже [pro], а steps/guidance не выставлены; для текста дешевле и лучше GPT Image 2.5/NB2.
- **Арены (место · балл):** AA t2i «FLUX.2 [flex]»: All #20 1026, Text #22 1006, UI/UX #20 1065, Retail #20 1041, Live-Action #34 1016, Animation #27 1039, Layout #23 1045; AA правка «FLUX.2 [flex]»: All #38 1005, Text/Symbol #31 1015, Identity #36 1027, Composition #35 997; LMArena t2i «flux-2-flex»: Overall #28 1157, Text #26 1172, Photoreal #37 1147, Product #25 1173, 3D #25 1172; LMArena правка «flux-2-flex»: Overall #39 1225, Text #28 1257.
- **Источники:** [S1], [S17], [S19], [S36], [S37], [S39], [S40]; YAML: `models/flux-2-flex.yaml`.

### 2.14 Seedream 5.0 Pro · `seedream/5-pro-text-to-image`

- **Статус:** `current` — флагман ByteDance (08.07.2026); в polza с префиксом `seedream/`, а не `bytedance/`. Вендор: ByteDance Seed (BytePlus ModelArk). Релиз: 2026-07-08; в polza с 2026-07-14.
- **Идентификаторы:** прямой API: Seedream 5.0 pro (пример Model ID в документации: seedream-5-0-pro-260628); в аренах: AA: Seedream 5.0 Pro; LMArena: seedream-5.0-pro.
- **Доступ:** polza: mie; basic 5 ₽ («1K»), high 10 ₽ («2K»); +0,3 ₽ за каждый референс после первого (10 реф.: 7,7 / 12,7 ₽); прямой API: BytePlus ModelArk (Model ID активируется в консоли).
- **Вход:** промт: polza — без лимита в каталоге; API — рекомендация ≤ 300 иероглифов / 600 англ. слов; референсы: polza 10; API 2–10; маска: нет маски-картинки; интерактивная правка координатами, рамками, стрелками (API).
- **Выход:** форматы: polza png|jpeg (png по умолч.); API png|jpeg (jpeg по умолч.), url 24 ч | b64_json; альфа: API: `background: transparent` только image-to-image с одним входом, у которого уже есть альфа; `layer_decomposition` → база + до 16 слоёв PNG с альфой; в polza — нет.
- **Размеры и соотношения:** polza: aspect_ratio обязателен: 1:1, 4:3, 3:4, 16:9, 9:16, 2:3, 3:2 (21:9 нет); quality basic = 1K, high = 2K; прямой API: 1K | 1.5K | 2K (по умолч. 2K; «1.5K has the same price as 1K… better quality») или W×H 921 600…4 624 220 px; соотношение 1/16…16.
- **Текст латиницей:** заявления — инфографика, UI-примеры (e-commerce hero 16:9, SaaS hero из скетча) в блоге; независимо — AA TR #16 1039; LMArena TR #15 1255 [исследование].
- **Текст кириллицей:** заявления — API: русский в списке языков промта (только 5.0 pro/flash); блог: «over ten commonly used languages… Russian», рендер «adapts to the typographic rules of different languages»; независимо — Хабр/studyai (N=1): «СОСТАД» вместо «СОСТАВ» [мнение]; блог вендора: «still room to improve in finer-grained text rendering».
- **Правка:** AA editing #8 1105; Identity Preserving #8 1146; Social Media edit #4; Enhancement #9 [исследование]; LMArena edit #8 1394.
- **Серия:** до 10 референсов; последовательной генерации серии нет (есть у 5.0 lite/4.5/4.0).
- **Диалект промта** (гайд: https://docs.byteplus.com/en/docs/ModelArk/1829186 (Seedream 4.0–4.5, обновлён 06.07.2026); API: https://docs.byteplus.com/en/docs/ModelArk/1541523): формат: естественный язык: «subject + action + environment» + стиль, цвет, свет, композиция; назначение картинки; негатив-параметр: нет; JSON: не документирован; hex: в блоге 5.0 Pro — hex и палитра-образец в правке [мнение вендора]; в API отдельного поля нет; язык: все модели — китайский и английский; Seedream 5.0 pro и 5.0 flash — ещё русский и 13 других языков (API).
  1. Промт ≤ 300 китайских иероглифов или 600 английских слов; для 4.x «concise and precise» лучше нагромождения эпитетов.
  2. Текст на картинке — в двойных кавычках.
  3. Стиль — ключевыми словами или референсом; назвать назначение (постер, e-commerce hero, UI).
  4. Правка — коротко, без местоимений, явно перечислить, что не менять; области можно указать стрелками, рамками, каракулями на входной картинке (5.0 pro/flash — ещё координатами).
  5. Несколько входов — «Image 1 / Image 2 / Image 3».
  6. Серия — «a series», «a set» или число картинок + `sequential_image_generation: auto` (5.0 lite, 4.5, 4.0; в polza не выставлено).
  7. `optimize_prompt_options.mode` standard | fast (переписывание промта; fast — только 5.0 pro).
- **По задачам:** `IMG-HERO-PHOTO` — сильная [исследование] (LMArena Photoreal #9 1278, Portraits #8 1293; AA Lighting #11, Material #11); `IMG-ICON3D` — сильная [исследование] (LMArena 3D #8 1253); `IMG-PRODUCT` — средняя [исследование] (AA Retail #14 1069; правка Retail #8); `IMG-EDIT` — сильная [исследование] (AA editing #8 — выше обоих Nano Banana Pro/2 в All); `IMG-TEXT-CYR` — заявлена [мнение вендора] (единственная в polza с русским в официальном списке языков промта (кроме Google)); `IMG-CUTOUT` — только прямой API и только из входа с альфой / слои [документация] (t2i с прозрачностью нет).
- **Цена (23.09.2026):** polza, ₽: basic 5 / high 10 (+0,3 за реф. со 2-го); прямой API, $: AA $90/1k (1024²).
- **Водяные знаки и происхождение:** видимый: ДА по умолчанию в прямом API: `watermark` default true — «Adds an "AI-generated" watermark to the lower-right corner»; что передаёт провайдер mie в polza — неизвестно (тест 2) [не проверено]; невидимый: не описано; C2PA: не описано; у BytePlus есть «GetArkOfficialResult — Obtain ModelArk artifact verification result» (проверка происхождения на стороне ModelArk) [документация, детали не изучены].
- **Типичные дефекты:** видимый знак «AI-generated» по умолчанию в прямом API; ошибки в словах (N=1).
- **Маршрутизация:** Сильный второй голос для фото, портретов и 3D после GPT 2.5; в polza только 1K/2K без 21:9. Прежде чем использовать в конвейере — тест 2 (видимый водяной знак).
- **Фаза 5:** тест 2 (водяной знак — первым); тест 1 (кириллица); тест 6 (продукт); тест 15 (латиница) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Арены (место · балл):** AA t2i «Seedream 5.0 Pro»: All #15 1079, Text #16 1039, UI/UX #13 1099, Retail #14 1069, Live-Action #10 1107, Animation #17 1060, Layout #16 1103; AA правка «Seedream 5.0 Pro»: All #8 1105, Text/Symbol #11 1110, Identity #8 1146, Composition #10 1105; LMArena t2i «seedream-5.0-pro»: Overall #10 1256, Text #15 1255, Photoreal #9 1278, Product #16 1236, 3D #8 1253; LMArena правка «seedream-5.0-pro»: Overall #8 1394, Text #13 1411.
- **Источники:** [S1], [S20], [S21], [S22], [S48], [S36], [S37], [S39], [S40]; YAML: `models/seedream-5-pro.yaml`.

### 2.15 Seedream 5.0 Lite · `bytedance/seedream-5-lite`

- **Статус:** `current` — дешёвая линия 5.0; промт только zh/en. Вендор: ByteDance Seed. Релиз: 2026-02 (AA: Feb 2026); в polza с 2026-02-27.
- **Идентификаторы:** в аренах: AA: Seedream 5.0 Lite; LMArena: seedream-5.0-lite.
- **Доступ:** polza: mie; 4 ₽ за любое quality; прямой API: BytePlus ModelArk.
- **Вход:** промт: 2996 (polza); референсы: polza 10; API 2–14 (вход + выход ≤ 15); маска: нет.
- **Выход:** форматы: API png|jpeg; альфа: нет.
- **Размеры и соотношения:** polza: aspect_ratio обязателен: 1:1, 4:3, 3:4, 16:9, 9:16, 2:3, 3:2, 21:9; quality basic = 2K, high = 3K (одна цена); прямой API: 2K | 3K | 4K или W×H 3 686 400…16 777 216 px; 1/16…16.
- **Текст латиницей:** заявления — нет; независимо — AA TR #42 974; LMArena TR #41 1135.
- **Текст кириллицей:** заявления — промт — только китайский и английский (API); независимо — нет данных.
- **Правка:** AA editing #20 1054; Enhancement & Restoration #11 1043 — выше NB2 (#19) и NB Pro (#22) [исследование]; LMArena edit #27 1294.
- **Серия:** API: `sequential_image_generation: auto`, `max_images` до 15 — серия за один запрос (в polza не выставлено).
- **Диалект промта** (гайд: https://docs.byteplus.com/en/docs/ModelArk/1829186 (Seedream 4.0–4.5, обновлён 06.07.2026); API: https://docs.byteplus.com/en/docs/ModelArk/1541523): формат: естественный язык: «subject + action + environment» + стиль, цвет, свет, композиция; назначение картинки; негатив-параметр: нет; JSON: не документирован; hex: в блоге 5.0 Pro — hex и палитра-образец в правке [мнение вендора]; в API отдельного поля нет; язык: все модели — китайский и английский; Seedream 5.0 pro и 5.0 flash — ещё русский и 13 других языков (API).
  1. Промт ≤ 300 китайских иероглифов или 600 английских слов; для 4.x «concise and precise» лучше нагромождения эпитетов.
  2. Текст на картинке — в двойных кавычках.
  3. Стиль — ключевыми словами или референсом; назвать назначение (постер, e-commerce hero, UI).
  4. Правка — коротко, без местоимений, явно перечислить, что не менять; области можно указать стрелками, рамками, каракулями на входной картинке (5.0 pro/flash — ещё координатами).
  5. Несколько входов — «Image 1 / Image 2 / Image 3».
  6. Серия — «a series», «a set» или число картинок + `sequential_image_generation: auto` (5.0 lite, 4.5, 4.0; в polza не выставлено).
  7. `optimize_prompt_options.mode` standard | fast (переписывание промта; fast — только 5.0 pro).
- **По задачам:** `IMG-UPSCALE` — кандидат для «доводки» правкой [исследование] (AA Enhancement #11 при 4 ₽); `IMG-DRAFT` — годится для 2K-черновиков [документация] (4 ₽ за 2K/3K); `IMG-HERO-PHOTO` — слабая [исследование] (AA All #36 1008).
- **Цена (23.09.2026):** polza, ₽: 4 (basic 2K и high 3K); прямой API, $: AA $35/1k.
- **Водяные знаки и происхождение:** видимый: ДА по умолчанию в прямом API: `watermark` default true — «Adds an "AI-generated" watermark to the lower-right corner»; что передаёт провайдер mie в polza — неизвестно (тест 2) [не проверено]; невидимый: не описано; C2PA: не описано; у BytePlus есть «GetArkOfficialResult — Obtain ModelArk artifact verification result» (проверка происхождения на стороне ModelArk) [документация, детали не изучены].
- **Маршрутизация:** Дешёвые 2K–3K кадры и восстановление/улучшение (Enhancement); не для текста.
- **Арены (место · балл):** AA t2i «Seedream 5.0 Lite»: All #36 1008, Text #42 974, Retail #27 1013, Live-Action #38 1003, Animation #26 1045, Layout #40 1013; AA правка «Seedream 5.0 Lite»: All #20 1054, Text/Symbol #24 1053, Identity #23 1063, Composition #26 1035; LMArena t2i «seedream-5.0-lite»: Overall #38 1138, Text #41 1135, Photoreal #30 1156, Product #40 1131, 3D #37 1143; LMArena правка «seedream-5.0-lite»: Overall #27 1294, Text #24 1284.
- **Источники:** [S1], [S20], [S21], [S36], [S37], [S39], [S40]; YAML: `models/seedream-5-lite.yaml`.

### 2.16 Seedream 4.5 · `bytedance/seedream-4.5`

- **Статус:** `current-previous` — предыдущее поколение; лучший текст в WeGenBench (zh/en). Вендор: ByteDance Seed. Релиз: 2025-12 (AA: Dec 2025); в polza с 2026-02-20.
- **Идентификаторы:** в аренах: AA: Seedream 4.5; LMArena: seedream-4.5.
- **Доступ:** polza: mie; 5 ₽ за любое quality; прямой API: BytePlus ModelArk.
- **Вход:** промт: 3000 (polza); референсы: polza 14; API 2–14; маска: нет.
- **Выход:** форматы: API png|jpeg; альфа: нет.
- **Размеры и соотношения:** polza: 1:1, 4:3, 3:4, 3:2, 2:3, 16:9, 9:16, 21:9; quality basic = 2K, high = 4K (одна цена); прямой API: 2K | 4K (≥ 3 686 400 px); 1/16…16.
- **Текст латиницей:** заявления — нет; независимо — WeGenBench (zh/en): лучший текст — Char F1 0.79, Sim_edit 0.74, рукописный 0.86, сложная вёрстка 0.82, двуязычный 0.82; QA 0.96, AM 2.81 [исследование]; но AA TR #30 991, LMArena TR #38 1143 — арены и WeGenBench расходятся [спорно]; GEBench (UI-состояния): 55.91/50.01 (CN/EN).
- **Текст кириллицей:** заявления — промт — только китайский и английский; независимо — нет данных.
- **Правка:** AA editing #28 1035; LMArena edit #25 1302 (1,15 млн голосов).
- **Серия:** до 14 реф.; `sequential_image_generation` в API (не в polza).
- **Диалект промта** (гайд: https://docs.byteplus.com/en/docs/ModelArk/1829186 (Seedream 4.0–4.5, обновлён 06.07.2026); API: https://docs.byteplus.com/en/docs/ModelArk/1541523): формат: естественный язык: «subject + action + environment» + стиль, цвет, свет, композиция; назначение картинки; негатив-параметр: нет; JSON: не документирован; hex: в блоге 5.0 Pro — hex и палитра-образец в правке [мнение вендора]; в API отдельного поля нет; язык: все модели — китайский и английский; Seedream 5.0 pro и 5.0 flash — ещё русский и 13 других языков (API).
  1. Промт ≤ 300 китайских иероглифов или 600 английских слов; для 4.x «concise and precise» лучше нагромождения эпитетов.
  2. Текст на картинке — в двойных кавычках.
  3. Стиль — ключевыми словами или референсом; назвать назначение (постер, e-commerce hero, UI).
  4. Правка — коротко, без местоимений, явно перечислить, что не менять; области можно указать стрелками, рамками, каракулями на входной картинке (5.0 pro/flash — ещё координатами).
  5. Несколько входов — «Image 1 / Image 2 / Image 3».
  6. Серия — «a series», «a set» или число картинок + `sequential_image_generation: auto` (5.0 lite, 4.5, 4.0; в polza не выставлено).
  7. `optimize_prompt_options.mode` standard | fast (переписывание промта; fast — только 5.0 pro).
- **По задачам:** `IMG-SERIES` — кандидат [исследование] (OmniRef-Bench 8.13 — #2 после NB Pro; 14 реф. в polza по 5 ₽); `IMG-TEXT-LATIN` — спорно [исследование] (WeGenBench №1, арены — середина); `IMG-HERO-PHOTO` — средняя [исследование] (AA All #25).
- **Цена (23.09.2026):** polza, ₽: 5 (2K и 4K); прямой API, $: AA $40/1k.
- **Водяные знаки и происхождение:** видимый: ДА по умолчанию в прямом API: `watermark` default true — «Adds an "AI-generated" watermark to the lower-right corner»; что передаёт провайдер mie в polza — неизвестно (тест 2) [не проверено]; невидимый: не описано; C2PA: не описано; у BytePlus есть «GetArkOfficialResult — Obtain ModelArk artifact verification result» (проверка происхождения на стороне ModelArk) [документация, детали не изучены].
- **Маршрутизация:** 4K за 5 ₽ и 14 референсов — дешёвый вариант для серий и больших фонов; текст — проверять.
- **Фаза 5:** тест 1 (кириллица при английском промте); тест 5 (серия) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Бенчмарки (вне арен):** OmniRef-Bench (06.2026): 8.13 — #2 после NB Pro [исследование]; GEditBench v2 (03.2026): 1089 — #2 [исследование]; T2I-CoReBench: 77.0 [исследование]; WeGenBench (zh/en): лучший текст — Char F1 0.79 [исследование].
- **Арены (место · балл):** AA t2i «Seedream 4.5»: All #25 1021, Text #30 991, UI/UX #26 1022, Retail #22 1033, Live-Action #26 1031, Animation #29 1035, Layout #29 1035; AA правка «Seedream 4.5»: All #28 1035, Text/Symbol #22 1060, Identity #32 1037, Composition #24 1036; LMArena t2i «seedream-4.5»: Overall #35 1147, Text #38 1143, Photoreal #26 1166, Product #36 1142, 3D #34 1147; LMArena правка «seedream-4.5»: Overall #25 1302, Text #21 1310.
- **Источники:** [S1], [S20], [S21], [S42], [S71], [S63], [S65], [S36], [S37], [S39], [S40]; YAML: `models/seedream-4-5.yaml`.

### 2.17 Seedream 4.0 · `bytedance/seedream-4`

- **Статус:** `legacy` — сентябрь 2025; в polza единственная Seedream с seed и 1K. Вендор: ByteDance Seed. Релиз: 2025-09 (AA: Sep 2025); в polza с 2026-02-20.
- **Идентификаторы:** в аренах: AA: Seedream 4.0; LMArena: seedream-4-2k / seedream-4-fal / seedream-4-high-res-fal.
- **Доступ:** polza: mie; 3 ₽; прямой API: BytePlus ModelArk.
- **Вход:** промт: 5000 (polza); референсы: polza 10; API 2–14; маска: нет; seed: polza: 1…4294967295.
- **Выход:** форматы: API png|jpeg; альфа: нет.
- **Размеры и соотношения:** polza: 1K/2K/4K; 1:1, 4:3, 3:4, 3:2, 2:3, 16:9, 9:16, 21:9; прямой API: 1K | 2K | 4K (≥ 921 600 px); 1/16…16.
- **Текст латиницей:** заявления — нет; независимо — AA TR #35 984; UniGenBench++: «Seedream-4.0 excel[s] in Chinese text rendering»; Alibaba AI Arena (конец 2025): 1039 — №3 (из техотчёта Z-Image).
- **Текст кириллицей:** заявления — промт — только zh/en; независимо — нет данных.
- **Правка:** AA editing #33 1012.
- **Серия:** seed + 10 реф. в polza; sequential в API.
- **Диалект промта** (гайд: https://docs.byteplus.com/en/docs/ModelArk/1829186 (Seedream 4.0–4.5, обновлён 06.07.2026); API: https://docs.byteplus.com/en/docs/ModelArk/1541523): формат: естественный язык: «subject + action + environment» + стиль, цвет, свет, композиция; назначение картинки; негатив-параметр: нет; JSON: не документирован; hex: в блоге 5.0 Pro — hex и палитра-образец в правке [мнение вендора]; в API отдельного поля нет; язык: все модели — китайский и английский; Seedream 5.0 pro и 5.0 flash — ещё русский и 13 других языков (API).
  1. Промт ≤ 300 китайских иероглифов или 600 английских слов; для 4.x «concise and precise» лучше нагромождения эпитетов.
  2. Текст на картинке — в двойных кавычках.
  3. Стиль — ключевыми словами или референсом; назвать назначение (постер, e-commerce hero, UI).
  4. Правка — коротко, без местоимений, явно перечислить, что не менять; области можно указать стрелками, рамками, каракулями на входной картинке (5.0 pro/flash — ещё координатами).
  5. Несколько входов — «Image 1 / Image 2 / Image 3».
  6. Серия — «a series», «a set» или число картинок + `sequential_image_generation: auto` (5.0 lite, 4.5, 4.0; в polza не выставлено).
  7. `optimize_prompt_options.mode` standard | fast (переписывание промта; fast — только 5.0 pro).
- **По задачам:** `IMG-TEXTURE` — кандидат [документация] (4K за 3 ₽ и seed — дешёвые большие поверхности (бесшовность — постобработкой)); `IMG-DRAFT` — годится [документация] (3 ₽, seed для воспроизводимости); `IMG-HERO-PHOTO` — средняя [исследование] (AA All #21 1026 — выше 4.5 (#25)).
- **Цена (23.09.2026):** polza, ₽: 3 (1K/2K/4K); прямой API, $: AA $30/1k.
- **Водяные знаки и происхождение:** видимый: ДА по умолчанию в прямом API: `watermark` default true — «Adds an "AI-generated" watermark to the lower-right corner»; что передаёт провайдер mie в polza — неизвестно (тест 2) [не проверено]; невидимый: не описано; C2PA: не описано; у BytePlus есть «GetArkOfficialResult — Obtain ModelArk artifact verification result» (проверка происхождения на стороне ModelArk) [документация, детали не изучены].
- **Маршрутизация:** Самый дешёвый 4K в polza (3 ₽) и единственный Seedream с seed; для фонов, текстур, черновиков.
- **Фаза 5:** тест 2 (водяной знак); тест 13 (текстура) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Бенчмарки (вне арен):** ViStoryBench (Lite, 29.08.2026): #17 [исследование]; OneIG (лидерборд 19.09.2025): №1 — 0.894 соответствие, текст ZH 0.982 [исследование]; RISEBench (23.04.2026): 12,2 % [исследование].
- **Арены (место · балл):** AA t2i «Seedream 4.0»: All #21 1026, Text #35 984, UI/UX #52 958, Live-Action #24 1039, Animation #22 1052, Layout #37 1028; AA правка «Seedream 4.0»: All #33 1012, Text/Symbol #30 1022, Identity #34 1035; LMArena t2i «seedream-4-2k»: Overall #37 1140, Text #39 1143, Photoreal #34 1151, Product #39 1134, 3D #30 1150; LMArena t2i «seedream-4-fal»: Overall #45 1116, Text #44 1124, Photoreal #48 1121, Product #45 1128, 3D #40 1139; LMArena t2i «seedream-4-high-res-fal»: Overall #49 1113, Text #52 1110, Photoreal #43 1130, Product #50 1113, 3D #47 1121; LMArena правка «seedream-4-2k»: Overall #29 1271; LMArena правка «seedream-4-fal»: Overall #43 1210; LMArena правка «seedream-4-high-res-fal»: Overall #41 1217, Text #35 1203.
- **Источники:** [S1], [S21], [S43], [S70], [S58], [S64], [S36], [S37], [S39], [S40]; YAML: `models/seedream-4.yaml`.

### 2.18 Qwen-Image-2.1 · `qwen/image-2.1`

- **Статус:** `current` — веса 20.09.2026 (7B генератор, 32 single-stream DiT); t2i и правка в одних весах; в polza с 21.09.2026. Вендор: Alibaba Qwen. Релиз: 2026-09-20; в polza с 2026-09-21.
- **Идентификаторы:** веса: Qwen/Qwen-Image-2.1 (HF); в аренах: LMArena: qwen-image-2.1 (qwen-research) — предварительно; AA: ещё нет.
- **Доступ:** polza: mie; 3 ₽ (1K) / 6 ₽ (2K); прямой API: открытые веса (Qwen Research License — некоммерческая); API Model Studio для 2.1 — не найден.
- **Вход:** промт: 5000 (polza), «любой язык»; референсы: до 10 (polza и README); маска: polza `mask_url`: белое — менять, чёрное — оставить; только с одним референсом; несовместимо с `background: transparent`.
- **Выход:** форматы: png | webp | jpeg (png по умолч.); альфа: ДА — `background: transparent` (png/webp) — единственная модель polza с нативной прозрачностью.
- **Размеры и соотношения:** polza: 1K/2K; 1:1, 4:3, 3:4, 3:2, 2:3, 16:9, 9:16; прямой API: нативно 2K (2048² и т. п.).
- **Параметры:** polza: seed, enhance_prompt, background, mask_url, output_format.
- **Текст латиницей:** заявления — нет; независимо — LMArena TR #14 1264 (предварительно); edit TR #15 1390 [исследование].
- **Текст кириллицей:** заявления — polza: промт на любом языке; независимо — для 2.1 данных нет; витрина Model Studio (Qwen-Image) со словом «Виолета» верна — отобрана вендором [мнение вендора].
- **Правка:** LMArena edit #16 1367 (предварительно, 4841 голос); сохранение личности людей и продуктов (README) [мнение вендора].
- **Серия:** до 10 реф.; seed.
- **Диалект промта** (гайд: https://huggingface.co/Qwen/Qwen-Image-2.1 (README; рерайтеры PE-T2I/PE-I2I)): формат: естественный язык; polza: «любой язык», до 5000 символов; негатив-параметр: в polza не выставлен; JSON: не документирован; hex: не документирован; язык: polza: «любой язык» [документация polza]; вендорский список языков для 2.1 не найден.
  1. Прозрачность: `background: transparent` + png/webp + шаблон «This is an RGBA image with transparency. <описание>. The image has alpha channel and the background is transparent.»
  2. Референсы (до 10) — в порядке, в котором промт на них ссылается («Image 1 …»).
  3. Локальная правка: круг/пометка на входной картинке или `mask_url` (белое — менять, чёрное — оставить; только с одним референсом; несовместимо с прозрачностью).
  4. `enhance_prompt: true` — переписывание промта (+10–30 с; вероятно, рерайтер PE); для точного текста — выключать [не проверено].
  5. `seed` — для воспроизводимости серий и A/B.
  6. Нативно 2K: 1:1 2048², 16:9 2752×1536, 4:3 2400×1792, 3:2 2528×1696.
- **По задачам:** `IMG-CUTOUT` — лидер в polza (единственная) [документация] (нативный RGBA из текста, правка прозрачных слоёв, извлечение объекта из фото); `IMG-EDIT` — сильная по цене [исследование] (маска + 10 реф. + seed за 3 ₽; LMArena edit #16); `IMG-ILLUSTR` — средняя [исследование] (LMArena Art #14 1238); `IMG-HERO-PHOTO` — средняя [исследование] (LMArena t2i #17 1228; Photoreal #17); `IMG-DRAFT` — годится [документация] (3 ₽ за 1K, seed).
- **Цена (23.09.2026):** polza, ₽: 3 (1K) / 6 (2K).
- **Водяные знаки и происхождение:** видимый: не описано; невидимый: не описано; C2PA: не описано — тест 7.
- **Лицензия:** Qwen Research License (20.09.2026): «research or evaluation purposes only»; коммерция — отдельная лицензия (model-business@notice.qwencloud.com). Лицензия на веса; права на результат при вызове через mie — [спорно], вопрос L.
- **Типичные дефекты:** арена — предварительная (≈ 2,8–4,8 тыс. голосов); противоположная полярность маски у `openai/gpt-5-image@mie`.
- **Маршрутизация:** Единственный путь к прозрачному PNG внутри polza; альтернатива — генерация + удаление фона (H). Маска + seed делают её рабочей моделью для точечной правки за 3 ₽. Юридически: коммерческое использование результата — уточнить у L до продакшена.
- **Фаза 5:** тест 4 (прозрачность); тест 12 (маска); тест 1 (кириллица); тест 6 (продукт) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Арены (место · балл):** LMArena t2i «qwen-image-2.1»: Overall #17 1228 предв., Text #14 1264 предв., Photoreal #17 1234 предв., Product #17 1234 предв., 3D #17 1205 предв.; LMArena правка «qwen-image-2.1»: Overall #16 1367 предв., Text #15 1390 предв.
- **Источники:** [S1], [S23], [S36], [S37], [S39], [S40]; YAML: `models/qwen-image-2-1.yaml`.

### 2.19 Qwen-Image 2.0 (предположительно qwen-image-2.0, снимок 2026-03-03) · `qwen/image-2`

- **Статус:** `legacy` — сопоставление с qwen-image-2.0 — по цене (4 ₽ ≈ $0.034; AA $35/1k) и дате [предположение]. Вендор: Alibaba Qwen. Релиз: 2026-03-03 (снимок Model Studio); в polza с 2026-03-17.
- **Идентификаторы:** прямой API: qwen-image-2.0 (Model Studio) — предположительно; в аренах: AA: Qwen Image 2.0 (2026-03-03).
- **Доступ:** polza: mie; 4 ₽; прямой API: Alibaba Model Studio.
- **Вход:** промт: 5000 (polza); Model Studio — до 1300 токенов; референсы: до 3; маска: нет.
- **Выход:** форматы: png | jpeg; альфа: нет.
- **Размеры и соотношения:** polza: 1:1, 3:4, 4:3, 9:16, 16:9 (разрешение не выставлено); прямой API: 512²…2048², по умолч. 2048².
- **Текст латиницей:** заявления — Model Studio: промт «Supports Chinese and English»; независимо — AA t2i #68 960.
- **Текст кириллицей:** заявления — промт — только zh/en; независимо — нет данных.
- **Диалект промта** (гайд: https://www.alibabacloud.com/help/en/model-studio/qwen-image-api): негатив-параметр: Model Studio: `negative_prompt` до 500 символов; в polza не выставлен.
  1. промт zh/en, до 1300 токенов
  2. `watermark` — параметр API (в примерах false); в polza не выставлен
- **По задачам:** `IMG-*` — устарела [исследование] (AA #68; Qwen 2.1 дешевле (3 ₽) и сильнее).
- **Цена (23.09.2026):** polza, ₽: 4; прямой API, $: AA $35/1k.
- **Водяные знаки и происхождение:** видимый: Model Studio: параметр `watermark` (в примерах false) — что передаёт mie, неизвестно; C2PA: не описано.
- **Маршрутизация:** Не использовать: заменяется `qwen/image-2.1`.
- **Бенчмарки (вне арен):** WISE_Verified (26.06.2026): Qwen-Image-2.0 0.795 — #5 [исследование].
- **Арены (место · балл):** AA t2i «Qwen Image 2.0 (2026-03-03)»: All #68 960, Animation #67 949; AA правка «Qwen Image 2.0 (2026-03-03)»: All #54 961, Identity #53 961.
- **Источники:** [S1], [S24], [S55], [S36], [S37], [S39], [S40]; YAML: `models/qwen-image-2.yaml`.

### 2.20 Qwen-Image (исходная 20B, август 2025) · `qwen/image`

- **Статус:** `legacy` — предположительно исходные открытые веса Qwen-Image 20B (Apache 2.0) — по параметрам strength/guidance_scale [предположение]. Вендор: Alibaba Qwen. Релиз: 2025-08-02; в polza с 2026-02-23.
- **Идентификаторы:** веса: Qwen/Qwen-Image (20B, Apache 2.0); в аренах: AA: Qwen Image Open Weights; LMArena: qwen-image.
- **Доступ:** polza: mie; 2,25–3 ₽ по соотношению.
- **Вход:** референсы: 1 (image-to-image со `strength` 0–1, 0,8); маска: нет.
- **Выход:** форматы: png | jpeg; альфа: нет.
- **Размеры и соотношения:** polza: 1:1 (3 ₽), 3:4/4:3 (2,5 ₽), 9:16/16:9 (2,25 ₽).
- **Параметры:** polza: strength 0–1 (0,8), guidance_scale 0–20 (2,5).
- **Текст латиницей:** заявления — нет; независимо — техотчёт Z-Image (2025): CVTG-2K 0.8288; LongText EN/ZH 0.943/0.946; OneIG-ZH 0.548 (лучший); GenEval 0.87 (лучший); DPG 88.32 (лучший); AA #101 886; LMArena #63 1057.
- **Текст кириллицей:** заявления — нет; независимо — LingT2I (08.2026): русский 0.32 против английского 0.69 [исследование].
- **Диалект промта** (гайд: https://huggingface.co/Qwen/Qwen-Image): —.
  1. гайд не изучался; в polza: strength и guidance_scale
- **По задачам:** `IMG-*` — устарела [исследование] (академические лидеры 2025 ≠ арены 2026).
- **Цена (23.09.2026):** polza, ₽: 2,25 / 2,5 / 3.
- **Водяные знаки и происхождение:** видимый: не описано.
- **Маршрутизация:** Не использовать: пример того, как лидер GenEval/DPG 2025 оказывается #101 в арене 2026.
- **Бенчмарки (вне арен):** LingT2I (08.2026): Qwen-Image — русский 0.32 против английского 0.69 [исследование]; GenEval 2: 33.8 (люди 26.8) — #2; с переписыванием промта (люди) 35.8 — №1 [исследование]; OneIG (19.09.2025): 0.882 соответствие — #2; T2I-ReasonBench 67.5 [исследование]; техотчёт Z-Image: GenEval 0.87, DPG 88.32 — лучшие в 2025 [исследование].
- **Арены (место · балл):** AA t2i «Qwen Image Open Weights»: All #101 886, Live-Action #92 890, Animation #69 943; LMArena t2i «qwen-image»: Overall #63 1057, Text #63 1048, Photoreal #63 1062, Product #61 1069, 3D #61 1064.
- **Источники:** [S1], [S26], [S67], [S53], [S56], [S58], [S36], [S37], [S39], [S40]; YAML: `models/qwen-image.yaml`.

### 2.21 Z-Image (Tongyi-MAI) — Turbo или Base · `tongyi-mai/z-image`

- **Статус:** `current (open weights)` — какой вариант (Turbo или Base) отдаёт polza — не указано [не проверено]. Вендор: Alibaba Tongyi-MAI. Релиз: Turbo 2025-11-26; Base 2026-01-27; в polza с 2026-02-20.
- **Идентификаторы:** веса: Tongyi-MAI/Z-Image-Turbo (26.11.2025); Tongyi-MAI/Z-Image (база, 27.01.2026); в аренах: AA: Z-Image Turbo Open Weights, Z-Image Base; LMArena: z-image-turbo.
- **Доступ:** polza: mie; 1,4 ₽ — самая дешёвая модель polza; прямой API: веса Apache-2.0; хостинги (fal и др.).
- **Вход:** промт: 1000 символов (polza) — самый короткий лимит; референсы: нет (только t2i); маска: нет.
- **Выход:** альфа: нет.
- **Размеры и соотношения:** polza: 1:1, 4:3, 3:4, 16:9, 9:16; прямой API: 512²…2048².
- **Параметры:** прямой API: Turbo: 8 NFE (9 шагов), guidance 0; Base: 50 шагов, CFG, «effective negative prompting».
- **Текст латиницей:** заявления — «bilingual text rendering (English & Chinese)»; независимо — техотчёт вендора (2025): CVTG-2K 0.8671 (Base) / 0.8585 (Turbo); LongText 0.935/0.936; OneIG-EN 0.546 (Text 0.987) [исследование вендора]; AA TR #56 927.
- **Текст кириллицей:** заявления — не заявлена (только en/zh); независимо — нет данных.
- **Диалект промта** (гайд: https://github.com/Tongyi-MAI/Z-Image): негатив-параметр: Base — да (CFG); Turbo — guidance 0, негатив не действует [вывод из параметров].
  1. промт ≤ 1000 символов в polza — короткие описательные промты, без JSON-спецификаций
  2. текст — только латиница/китайский
- **По задачам:** `IMG-DRAFT` — лидер по цене [исследование] (1,4 ₽; AA 2,1 с (Turbo, fal); но AA #74 942 — ниже NB2 Lite (#13)); `IMG-HERO-PHOTO` — слабая [исследование] (AA #74; LMArena #56).
- **Цена (23.09.2026):** polza, ₽: 1,4; прямой API, $: AA $5/1k (Turbo), $10/1k (Base).
- **Скорость:** AA медиана 2,1 с (Turbo, fal).
- **Водяные знаки и происхождение:** видимый: не описано; C2PA: не описано.
- **Маршрутизация:** Черновики и перебор композиции за 1,4 ₽; переносимость на дорогую модель — тест 9.
- **Фаза 5:** тест 9 (черновик → Flare) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Бенчмарки (вне арен):** WISE_Verified: Z-Image 0.453 [исследование]; CVTG-2K 0.8671 (Base), OneIG-EN 0.546 — техотчёт вендора [исследование вендора].
- **Арены (место · балл):** AA t2i «Z-Image Turbo Open Weights»: All #74 942, Text #56 927, UI/UX #54 948, Retail #56 962, Live-Action #66 938, Animation #79 922, Layout #64 931; AA t2i «Z-Image Base»: All #109 874, Live-Action #86 913, Animation #98 868; LMArena t2i «z-image-turbo»: Overall #56 1083, Text #59 1058, Photoreal #50 1117, Product #63 1061, 3D #60 1066.
- **Источники:** [S1], [S25], [S26], [S55], [S58], [S36], [S37], [S39], [S40]; YAML: `models/z-image.yaml`.

### 2.22 Grok Imagine Image (базовая, январь 2026) — в polza «Grok Image» · `x-ai/grok-imagine-image`

- **Статус:** `current-previous` — в polza — базовая `grok-imagine-image` ($0.02), НЕ Image 2.0 (2,5 ₽ ≈ $0.021 по курсу polza; 3 соотношения, 1 референс). Вендор: xAI (в документации и аренах — SpaceXAI). Релиз: 2026-01 (AA: Jan 2026); в polza с 2026-02-20.
- **Идентификаторы:** прямой API: grok-imagine-image; в аренах: AA: grok-imagine-image; LMArena: grok-imagine-image.
- **Доступ:** polza: mie; 2,5 ₽; прямой API: xAI API `/v1/images/generations` (OpenAI-совместимо).
- **Вход:** промт: 5000 (polza); референсы: 1 (polza); маска: нет.
- **Выход:** альфа: нет.
- **Размеры и соотношения:** polza: 1:1, 2:3, 3:2; прямой API: общий список xAI: auto, 1:1, 16:9/9:16, 4:3/3:4, 3:2/2:3, 2:1/1:2, 19.5:9, 20:9, 21:9, 5:2; 1k | 2k [документация; для базовой модели не проверено].
- **Текст латиницей:** заявления — нет; независимо — AA TR #20 1017; LMArena TR #23 1184.
- **Текст кириллицей:** заявления — нет; независимо — нет данных для базовой.
- **Правка:** AA editing #17 1068; Composition & Framing #14 1080; LMArena edit #19 1329.
- **Диалект промта** (гайд: https://docs.x.ai/developers/model-capabilities/images/generation): —.
  1. официального гайда по промтам не найдено; параметры — через API
- **По задачам:** `IMG-DRAFT` — годится [исследование] (2,5 ₽; AA #28 1019 — ниже NB2 Lite); `IMG-*` — середина [исследование] (AA All #28).
- **Цена (23.09.2026):** polza, ₽: 2,5; прямой API, $: $0.02 (1K и 2K), вход-картинка $0.002.
- **Водяные знаки и происхождение:** C2PA: не описано.
- **Маршрутизация:** Не путать с Grok Imagine Image 2.0 (#4 AA) — её в polza нет. Для черновиков выгоднее NB2 Lite (выше в аренах, 8:1, 10 реф.).
- **Арены (место · балл):** AA t2i «grok-imagine-image»: All #28 1019, Text #20 1017, UI/UX #24 1042, Retail #28 1012, Live-Action #45 997, Animation #39 1013, Layout #22 1054; AA правка «grok-imagine-image»: All #17 1068, Text/Symbol #23 1059, Identity #24 1062, Composition #14 1080; LMArena t2i «grok-imagine-image»: Overall #23 1171, Text #23 1184, Photoreal #24 1179, Product #24 1174, 3D #22 1177; LMArena правка «grok-imagine-image»: Overall #19 1329, Text #17 1367.
- **Источники:** [S1], [S27], [S36], [S37], [S39], [S40]; YAML: `models/grok-imagine-image.yaml`.

### 2.23 Topaz Upscale (в polza — модель Topaz не указана) · `topaz/image-upscale`

- **Статус:** `current` — polza выставляет только `upscale_factor`; какая модель Topaz внутри (Standard / High Fidelity / Bloom / Wonder…) и сохраняется ли альфа — неизвестно. Вендор: Topaz Labs. Релиз: —; в polza с 2026-02-23.
- **Идентификаторы:** прямой API: Topaz API: Gigapixel (Standard 2, High Fidelity 2/3, Low Resolution 2, Art & CGI, Transparent Image Upscale, Text & Shapes, Recover Faces), Wonder 3/3.5, Bloom 2, Redefine, Denoise, Removal & Cleanup.
- **Доступ:** polza: mie; ×1/×2 7,5 ₽, ×4 15 ₽, ×8 30 ₽.
- **Вход:** референсы: 1 картинка (обязательна).
- **Выход:** альфа: в API Topaz есть «Transparent Image Upscale — Preserve Alpha Transparency»; в polza — неизвестно (тест 14).
- **Текст латиницей:** заявления — нет; независимо — апскейлер не рисует текст; сохранность мелкого текста при ×2–×8 — не измерена (в API Topaz есть модель Text & Shapes).
- **Текст кириллицей:** заявления — нет; независимо — не измерено.
- **Диалект промта** (гайд: —): формат: промта нет: только `images` (1 картинка) и `upscale_factor` 1 | 2 | 4 | 8.
- **По задачам:** `IMG-UPSCALE` — единственный апскейлер polza [документация] (без выбора модели Topaz).
- **Цена (23.09.2026):** polza, ₽: 7,5 (×1, ×2) / 15 (×4) / 30 (×8).
- **Водяные знаки и происхождение:** видимый: не описано; C2PA: сохраняются ли метаданные исходника (SynthID/C2PA) после апскейла — не описано; тест 7 на файле теста 14.
- **Маршрутизация:** Для hero из 1K-моделей (NB2 Lite, Z-Image) — ×2; для картинок с альфой — сначала тест 14.
- **Фаза 5:** тест 14 (×2 с альфой) (таблица — `99-raw/reports/wave1-C1-report.md` §5).
- **Источники:** [S1], [S29]; YAML: `models/topaz-image-upscale.yaml`.

## 3. Модели вне polza (11)

### 3.1 Imagen 4 (Standard / Fast / Ultra) — выключена · вне polza

- **Статус:** `dead` — Vertex AI: Discontinuation date 30.06.2026; Gemini API: deprecated 15.06.2026, shutdown 17.08.2026 («Imagen is shut down and no longer available through the Gemini API»). Вендор: Google. Релиз: 2025-08-14 (Vertex GA).
- **Идентификаторы:** прямой API: imagen-4.0-generate-001; imagen-4.0-fast-generate-001; imagen-4.0-ultra-generate-001.
- **Доступ:** прямой API: нет (выключена).
- **Выход:** форматы: image/png, image/jpeg; до 4 картинок на промт; альфа: нет.
- **Размеры и соотношения:** прямой API: 1:1, 3:4, 4:3, 9:16, 16:9; 1024²…2816×1536 (2K).
- **Текст латиницей:** заявления — нет; независимо — OneIG-EN 0.515 (техотчёт Z-Image, 2025).
- **Текст кириллицей:** заявления — языки промта: English + preview zh, hi, ja, ko, pt, es — русского нет (Vertex); независимо — нет данных.
- **Диалект промта** (гайд: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate): негатив-параметр: Negative prompting — Not supported (Vertex).
  1. модель выключена — правила не приводятся
- **По задачам:** `IMG-*` — не использовать [документация] (модель выключена).
- **Цена (23.09.2026):** прямой API, $: AA (архив): Ultra $60/1k, Standard $40/1k, Fast $20/1k.
- **Водяные знаки и происхождение:** видимый: нет; невидимый: «Digital watermarking and verification» — Supported (Vertex, таблица возможностей); C2PA: «Content Credentials (C2PA)» — Not supported (Vertex).
- **Маршрутизация:** Не предлагать: агенты «по памяти» советуют Imagen 4 — модель выключена в обоих API Google.
- **Арены (место · балл):** AA t2i «Imagen 4 Ultra»: All #43 997; AA t2i «Imagen 4 Standard»: All #91 910; AA t2i «Imagen 4 Fast»: All #103 883; LMArena t2i «imagen-ultra-4.0-generate-001»: Overall #34 1148, Text #35 1148, Photoreal #31 1156, Product #34 1151, 3D #39 1141; LMArena t2i «imagen-4.0-generate-001»: Overall #41 1129, Text #45 1124, Photoreal #40 1136, Product #41 1129, 3D #45 1123.
- **Источники:** [S13], [S15], [S36], [S37], [S39], [S40]; YAML: `models/imagen-4.yaml`.

### 3.2 FLUX.2 [max] · вне polza

- **Статус:** `current` — «Highest quality… strongest editing consistency and prompt following»; grounding search. Вендор: Black Forest Labs. Релиз: 2025-12-16.
- **Идентификаторы:** прямой API: /v1/flux-2-max; в аренах: AA: FLUX.2 [max]; LMArena: flux-2-max.
- **Доступ:** прямой API: api.bfl.ai; в polza нет (доступ — у P).
- **Вход:** референсы: до 8 в API (release notes: до 10 входов) [спорно]; маска: нет; прочее: grounding search.
- **Выход:** форматы: jpeg|png|webp; альфа: нет.
- **Параметры:** прямой API: seed, disable_pup (upsampling по умолч.), safety_tolerance, output_format.
- **Текст латиницей:** заявления — нет; независимо — AA TR #25 997; LMArena TR #27 1167 [исследование].
- **Текст кириллицей:** заявления — нет; независимо — нет данных.
- **Правка:** AA editing #45 995 ($140/1k); LMArena edit #30 1262 — вопреки «strongest editing consistency».
- **Диалект промта** (гайд: https://docs.bfl.ml/guides/prompting_guide_flux2): формат: проза или JSON — «FLUX.2 understands both formats equally well»; JSON-схема: scene, subjects[description, position, action], style, color_palette, lighting, mood, background, composition, camera{angle, lens, depth_of_field}; негатив-параметр: нет; негатив прозой: «No negative prompts» — описывать желаемое, а не запреты; JSON: да, рекомендован для автоматизации и сложных сцен; проза — для поиска направления; hex: да: со словом «color»/«hex» и привязкой к объекту («The car is #FF0000» лучше «use red #FF0000»); градиенты — начальный и конечный цвет; язык: «Prompt in your native language for more culturally authentic results».
  1. Порядок: Subject + Action + Style + Context; главное — в начало («pays more attention to what comes first»).
  2. Длина 30–80 слов обычно идеальна (10–30 — быстрые пробы, 80+ — сложные сцены).
  3. Негативов нет: вместо «no people» — «empty street at dawn».
  4. Фотостиль — названием камеры/плёнки («shot on Sony A7IV», «Kodak Portra 400»).
  5. Текст — в кавычках + место + стиль + размер + hex-цвет.
  6. Hex — с привязкой к объекту; бренд-палитра — полем color_palette в JSON.
  7. Мульти-референс — ссылаться на картинки по номеру; [pro] при 1 МП — до 8 входов, при 2 МП — до 7 (лимит 9 МП вход+выход).
  8. Разрешение кратно 16, до 4 МП, рекомендовано до 2 МП.
  9. Prompt upsampling у [pro]/[max] включён по умолчанию (`disable_pup: true` — ровно по промту); в polza параметра нет → промт, вероятно, переписывается [не проверено].
- **По задачам:** `IMG-HERO-PHOTO` — средняя [исследование] (AA All #24 1022; LMArena #26 1162); `IMG-EDIT` — средняя [исследование] (заявление вендора арены не подтверждают).
- **Цена (23.09.2026):** прямой API, $: от $0.07; AA $70/1k (t2i), $140/1k (правка).
- **Скорость:** AA медиана 24,8 с.
- **Водяные знаки и происхождение:** видимый: нет; невидимый: в прочитанной документации BFL не описано; C2PA: в прочитанной документации BFL не описано — проверить c2patool (тест 7) [не проверено].
- **Маршрутизация:** Не добавлять ради качества: по аренам ниже NB2 Lite и Seedream 5 Pro при большей цене.
- **Арены (место · балл):** AA t2i «FLUX.2 [max]»: All #24 1022, Text #25 997, UI/UX #21 1053, Retail #24 1022, Live-Action #33 1021, Animation #31 1033, Layout #32 1033; AA правка «FLUX.2 [max]»: All #45 995, Text/Symbol #37 998, Identity #31 1037, Composition #38 975; LMArena t2i «flux-2-max»: Overall #26 1162, Text #27 1167, Photoreal #28 1161, Product #28 1165, 3D #29 1162; LMArena правка «flux-2-max»: Overall #30 1262, Text #26 1282.
- **Источники:** [S17], [S18], [S36], [S37], [S39], [S40]; YAML: `models/flux-2-max.yaml`.

### 3.3 FLUX.2 [klein] 4B/9B и FLUX.2 [dev] — открытые веса · вне polza

- **Статус:** `current (open weights)` — [klein] 4B — Apache 2.0; [klein] 9B и [dev] — некоммерческие лицензии FLUX (NCL); [dev] — якорь AA (1000 Elo). Вендор: Black Forest Labs. Релиз: [dev] 2025-11 (AA); [klein] 2026-01-15; LoRA-инференс klein (beta) 2026-04-23.
- **Идентификаторы:** прямой API: /v1/flux-2-klein-4b; /v1/flux-2-klein-9b; /v1/flux-2-klein-9b-preview; в аренах: AA: FLUX.2 [klein] 9B / 4B Open Weights, FLUX.2 [dev] Open Weights; LMArena: flux-2-klein-9b, flux-2-klein-4b, flux-2-dev.
- **Доступ:** прямой API: api.bfl.ai ([klein]); локально — веса ([klein] 9B: текстовый энкодер Qwen3 8B, ≥ 13 ГБ VRAM); [dev] — «только локально, некоммерческая» (BFL pricing).
- **Вход:** референсы: [klein] — до 4; [dev] — ~6; маска: нет.
- **Выход:** форматы: jpeg|png|webp (API); альфа: нет.
- **Параметры:** прямой API: [klein]: без prompt upsampling; seed, safety_tolerance, output_format.
- **Текст латиницей:** заявления — нет; независимо — AA TR: [dev] #24 1000.
- **Текст кириллицей:** заявления — нет; независимо — нет данных.
- **Диалект промта** (гайд: https://docs.bfl.ml/guides/prompting_guide_flux2): формат: проза или JSON — «FLUX.2 understands both formats equally well»; JSON-схема: scene, subjects[description, position, action], style, color_palette, lighting, mood, background, composition, camera{angle, lens, depth_of_field}; негатив-параметр: нет; негатив прозой: «No negative prompts» — описывать желаемое, а не запреты; JSON: да, рекомендован для автоматизации и сложных сцен; проза — для поиска направления; hex: да: со словом «color»/«hex» и привязкой к объекту («The car is #FF0000» лучше «use red #FF0000»); градиенты — начальный и конечный цвет; язык: «Prompt in your native language for more culturally authentic results».
  1. Порядок: Subject + Action + Style + Context; главное — в начало («pays more attention to what comes first»).
  2. Длина 30–80 слов обычно идеальна (10–30 — быстрые пробы, 80+ — сложные сцены).
  3. Негативов нет: вместо «no people» — «empty street at dawn».
  4. Фотостиль — названием камеры/плёнки («shot on Sony A7IV», «Kodak Portra 400»).
  5. Текст — в кавычках + место + стиль + размер + hex-цвет.
  6. Hex — с привязкой к объекту; бренд-палитра — полем color_palette в JSON.
  7. Мульти-референс — ссылаться на картинки по номеру; [pro] при 1 МП — до 8 входов, при 2 МП — до 7 (лимит 9 МП вход+выход).
  8. Разрешение кратно 16, до 4 МП, рекомендовано до 2 МП.
  9. Prompt upsampling у [pro]/[max] включён по умолчанию (`disable_pup: true` — ровно по промту); в polza параметра нет → промт, вероятно, переписывается [не проверено].
- **По задачам:** `IMG-DRAFT` — годится локально [исследование] (klein 4B 3,4 с, 9B 4,0 с (AA); AA klein 9B #76 940); `IMG-*` — ниже платных моделей polza [исследование] (LMArena klein-9b #59 1070, klein-4b #67 1030, dev #36 1145).
- **Цена (23.09.2026):** прямой API, $: [klein] 4B от $0.014 (+$0.001/МП), 9B от $0.015 (+$0.002/МП); AA [dev] $12/1k (сторонние хостинги).
- **Скорость:** AA: klein 4B 3,4 с, 9B 4,0 с, [dev] (fal) 15,8 с.
- **Водяные знаки и происхождение:** видимый: нет; невидимый: локально — нет (зависит от пайплайна); C2PA: нет.
- **Маршрутизация:** Кандидат для локального конвейера (P/H): [klein] 4B — единственная из FLUX.2 с коммерчески свободной лицензией (Apache 2.0). В волне 1 GPU-сервер не используется — только справка.
- **Бенчмарки (вне арен):** OmniRef-Bench: FLUX.2 [klein] 6.49; DreamBench++ (новый прогон): klein 9B 0.56 [исследование]; WISE_Verified: FLUX.2-dev 0.565 [исследование]; GEditBench v2: FLUX.2 [klein] 9B 1039 — #4 [исследование].
- **Арены (место · балл):** AA t2i «FLUX.2 [klein] 9B Open Weights»: All #76 940, Text #57 904, UI/UX #57 910, Retail #61 936, Live-Action #56 961, Animation #66 950, Layout #61 936; AA t2i «FLUX.2 [klein] 4B Open Weights»: All #118 863, Text #65 816, UI/UX #65 779, Retail #62 876, Live-Action #83 921, Animation #99 868, Layout #66 833; AA t2i «FLUX.2 [dev] Open Weights»: All #40 1000, Text #24 1000, UI/UX #40 1000, Retail #34 1000, Live-Action #41 1000, Animation #46 1000, Layout #47 1000; AA правка «FLUX.2 [klein] 9B Open Weights»: All #32 1013, Text/Symbol #40 987, Identity #29 1044, Composition #33 998; AA правка «FLUX.2 [klein] 4B Open Weights»: All #57 947, Text/Symbol #58 858, Identity #51 966, Composition #42 948; AA правка «FLUX.2 [dev] Open Weights»: All #41 1000, Text/Symbol #36 1000, Identity #45 1000, Composition #32 1000; LMArena t2i «flux-2-klein-9b»: Overall #59 1070, Text #60 1057, Photoreal #58 1090, Product #60 1070, 3D #59 1079; LMArena t2i «flux-2-klein-4b»: Overall #67 1030, Text #70 1015, Photoreal #66 1047, Product #70 1027, 3D #67 1031; LMArena t2i «flux-2-dev»: Overall #36 1145, Text #29 1158, Photoreal #39 1143, Product #31 1154, 3D #31 1149; LMArena правка «flux-2-klein-9b»: Overall #40 1225, Text #37 1200; LMArena правка «flux-2-klein-4b»: Overall #46 1188, Text #41 1161; LMArena правка «flux-2-dev»: Overall #38 1226, Text #27 1259.
- **Источники:** [S17], [S18], [S19], [S71], [S74], [S55], [S63], [S36], [S37], [S39], [S40]; YAML: `models/flux-2-klein-dev.yaml`.

### 3.4 Qwen-Image-3.0-Pro · вне polza

- **Статус:** `current` — июль 2026; сильнейшая модель Alibaba в аренах; лидер по Layout среди не-OpenAI. Вендор: Alibaba (Model Studio). Релиз: 2026-07.
- **Идентификаторы:** прямой API: qwen-image-3.0-pro (Model Studio); в аренах: AA: Qwen-Image-3.0-Pro; LMArena: qwen-image-3.0-pro.
- **Доступ:** прямой API: Alibaba Cloud Model Studio (Singapore): 5 RPM; в polza нет.
- **Вход:** промт: «up to 4.5k tokens»; референсы: правка по 1–3 референсам; маска: нет.
- **Выход:** альфа: нет.
- **Размеры и соотношения:** прямой API: 512²…2048²; соотношения 1:8…8:1.
- **Параметры:** прямой API: `prompt_extend` (по умолч. true; режимы direct | agent).
- **Текст латиницей:** заявления — «text as small as 10px»; «realistic simulation of mainstream interfaces such as web pages»; независимо — AA TR #10 1082; Layout #5 1175; Complex Compositions #7; editing Text/Symbol #6 1133; LMArena TR #10 1284 [исследование].
- **Текст кириллицей:** заявления — «native rendering of 12 languages and multiple fonts» — список языков не найден; независимо — витрина Model Studio (Qwen-Image): «Виолета» верно — отбор вендора [мнение вендора].
- **Правка:** AA editing #16 1074.
- **Диалект промта** (гайд: https://www.alibabacloud.com/help/en/model-studio/qwen-image-3-0-pro): —.
  1. `prompt_extend: false` (direct) — для дословного текста [не проверено]
  2. интерфейсы и мелкий текст — сильная сторона по заявлению вендора
- **По задачам:** `IMG-MOCKUP` — сильная [исследование] (AA Layout #5, «web pages» в заявлении); `IMG-TEXT-LATIN` — сильная [исследование] (AA TR #10, LMArena TR #10); `IMG-TEXT-CYR` — заявлена [мнение вендора] (12 языков без списка).
- **Цена (23.09.2026):** прямой API, $: $0.04 (1K) / $0.075 (2K), вход $0.003 (Singapore); AA $40/1k.
- **Водяные знаки и происхождение:** C2PA: не описано.
- **Маршрутизация:** Кандидат вне polza для UI-макетов и мелкого текста; доступ — задача P.
- **Арены (место · балл):** AA t2i «Qwen-Image-3.0-Pro»: All #14 1089, Text #10 1082, UI/UX #15 1092, Retail #12 1085, Live-Action #14 1077, Animation #13 1110, Layout #5 1175; AA правка «Qwen-Image-3.0-Pro»: All #16 1074, Text/Symbol #6 1133, Identity #15 1104, Composition #17 1064; LMArena t2i «qwen-image-3.0-pro»: Overall #11 1254, Text #10 1284, Photoreal #13 1259, Product #11 1257, 3D #9 1249.
- **Источники:** [S24], [S36], [S37], [S39], [S40]; YAML: `models/qwen-image-3-0-pro.yaml`.

### 3.5 Grok Imagine Image 2.0 · вне polza

- **Статус:** `current` — 07.08.2026; «Quality Mode» в grok.com; №4 AA t2i и №1 AA Knowledge. Вендор: xAI / SpaceXAI. Релиз: 2026-08-07.
- **Идентификаторы:** прямой API: grok-imagine-image-2.0; в аренах: AA: Grok Imagine Image 2.0; LMArena: grok-imagine-image-2.0 (low).
- **Доступ:** прямой API: xAI API: регионы us-east-1, us-west-2; 6 RPS; Batch API; в polza нет.
- **Вход:** референсы: правка: `image_url` (URL, data URI, file_id), до 5 исходных картинок; JSON-запрос (multipart images.edit() OpenAI SDK не поддерживается); маска: нет в API (magic wand — в продукте).
- **Выход:** форматы: url (временный) | b64_json; альфа: в продукте — «Background removal … exports any subject with a transparent background»; в API параметра нет [не подтверждено для API].
- **Размеры и соотношения:** прямой API: `aspect_ratio` auto | 1:1 | 16:9 | 9:16 | 4:3 | 3:4 | 3:2 | 2:3 | 2:1 | 1:2 | 19.5:9 | 9:19.5 | 20:9 | 9:20 | 21:9 | 5:2; `resolution` 1k | 2k; `n` 1–10.
- **Параметры:** качество: low | medium | auto («Auto currently uses low for image generation and medium for image editing») — только у 2.0.
- **Текст латиницей:** заявления — «plans typography and layout the way a designer would… small text comes out sharp»; независимо — AA TR #3 1167; LMArena TR #5 1344; edit TR #4 1464 [исследование].
- **Текст кириллицей:** заявления — нет; независимо — klerk/Genova (26.08.2026; 4 макета, проверено глазами): заданный русский текст дословно 4/4; ошибки — в мелких подписях, добавленных моделью («Прибыл», «Прибль», «Динокь») [мнение]; Хабр/StudyAI (≈ 22.09.2026, N=1): «хорошо» [мнение].
- **Правка:** AA editing #11 1104; LMArena edit #4 1430; Smart resize — перекомпоновка 1:2…2:1 (в продукте).
- **Серия:** «preserves what you put in across generations and edits» [мнение вендора]; multi-ref до 5.
- **Диалект промта** (гайд: https://docs.x.ai/developers/model-capabilities/images/generation): —.
  1. официального гайда по промтам не найдено
  2. `quality: medium` для правки и мелкого текста; low по умолчанию для генерации
- **По задачам:** `IMG-TEXT-LATIN` — лидер вне OpenAI [исследование] (AA TR #3); `IMG-ILLUSTR` — лидер вне OpenAI [исследование] (AA Animation & Gaming #2 1186); `IMG-HERO-PHOTO` — сильная [исследование] (LMArena Portraits #4 1352); `IMG-TEXT-CYR` — средняя [мнение] (мелкий текст с ошибками).
- **Цена (23.09.2026):** прямой API, $: 1K·low $0.04, 1.5K·low $0.05, 2K·low $0.06, 1K·medium $0.06, 1.5K·medium $0.07, 2K·medium $0.08; вход $0.01; AA $60/1k.
- **Водяные знаки и происхождение:** C2PA: не описано.
- **Маршрутизация:** Лучшая альтернатива OpenAI вне polza для иллюстраций, знаний (инфографика по фактам) и латинского текста; доступ — задача P.
- **Арены (место · балл):** AA t2i «Grok Imagine Image 2.0»: All #4 1150, Text #3 1167, UI/UX #4 1181, Retail #5 1135, Live-Action #5 1125, Animation #2 1186, Layout #6 1174; AA правка «Grok Imagine Image 2.0»: All #11 1104, Text/Symbol #14 1096, Identity #10 1134, Composition #7 1111; LMArena t2i «grok-imagine-image-2.0»: Overall #5 1302, Text #5 1344, Photoreal #5 1312, Product #6 1303, 3D #6 1269; LMArena правка «grok-imagine-image-2.0»: Overall #4 1430, Text #4 1464.
- **Источники:** [S28], [S27], [S48], [S47], [S36], [S37], [S39], [S40]; YAML: `models/grok-imagine-image-2-0.yaml`.

### 3.6 Recraft V4.1 (+ V4, V4 Styles, Utility, Vector) · вне polza

- **Статус:** `current` — V4.1 — 14.05.2026 (по умолч. в API); V4 Styles — август 2026; сильная сторона — вектор, style_id, палитра в API, а не «красота». Вендор: Recraft. Релиз: V4 — 2026-02; V4.1 — 2026-05-14; V4 Styles — 2026-08.
- **Идентификаторы:** прямой API: `recraftv4_1`, `recraftv4_1_vector`, `recraftv4_1_pro(_vector)`, `recraftv4_1_utility(_pro)(_vector)`, `recraftv4(_pro)(_vector)`, `recraftv4_styles(_pro)(_vector)` — через подчёркивание, не точку (external.api.recraft.ai) [поправка X 24.09.2026 по G `07/02` и docs Recraft: было «recraftv4.1»]; в аренах: AA: Recraft V4.1 Utility, Recraft V4.1, Recraft V4; LMArena: recraft-v4.1-utility-pro, recraft-v4.1-pro, recraft-v4.
- **Доступ:** прямой API: Recraft API; MCP-сервер; в polza нет.
- **Вход:** промт: 10 000 символов у V4.x (1000 у V3/V2); референсы: `style_reference_urls` ≤ 10 картинок → приватный стиль и `style_id` (без обучения); маска: inpaint-эндпоинт — только V3 (`recraftv3`, `recraftv3_vector`); у V4.x маски нет, кроме инструмента erase region [поправка X 24.09.2026 по G].
- **Выход:** форматы: webp (по умолч.) | png; SVG у Vector-моделей; альфа: `removeBackground` (растр или SVG) — отдельный эндпоинт.
- **Размеры и соотношения:** прямой API: V4.x: 1:1 1024², 2:1 1536×768, 16:9 1344×768, 9:16, 4:5, 14:10, 6:10…; Pro — вдвое (16:9 2688×1536).
- **Параметры:** прямой API: `n` 1–6; `style_id`, `style_match` precise|flexible (V4 Styles); библиотека `style` — только V2/V3; `controls.colors` (до 10 RGB; вес — «relative preference», не доля площади: всем цветам или никому, сумма ≤ 1), `background_color` («partially» у V4/V4.1); `negative_prompt` — только V2/V3; `text_layout` (слово + bbox) — только V3; `random_seed`.
- **Текст латиницей:** заявления — V4: «works with text predictably, including multi-language text»; независимо — AA TR: V4.1 Utility Pro #27 996, V4.1 Utility #38 982, V4.1 Pro #48 962, V4.1 #52 955 [исследование].
- **Текст кириллицей:** заявления — нет; независимо — V3: набор символов содержит из кириллицы только «І А В Е К М Н О Р С Т У Х» (совпадающие с латиницей) — русские слова V3 не напишет [документация]; V4/V4.1 — «multi-language» без списка языков [мнение вендора].
- **Правка:** эндпоинты: image-to-image, erase region, remix, vectorize, crisp/creative upscale; inpaint, outpaint, replace/generate background только V3 (`recraftv3`, `recraftv3_vector`) [поправка X 24.09.2026 по G: было «inpaint, outpaint (только V3), replace/generate background» «…, replace/generate background, erase region, …»].
- **Серия:** V4 Styles: стиль из 1–10 референсов → `style_id` — повторяемый стиль серии без обучения.
- **Диалект промта** (гайд: https://www.recraft.ai/docs/prompt-engineering-guide/prompting-with-recraft-v4): негатив-параметр: только V2/V3; hex: не в промте, а `controls.colors` (RGB с весами) — единственный из изученных API с явной палитрой (кроме Wan 2.7 `color_palette`).
  1. текст — в кавычках
  2. стиль серии — `style_id` из референсов, а не описанием
  3. Utility — «for mockups and product listing photos» (плоский свет, фронтальная композиция)
- **По задачам:** `IMG-SERIES` — сильная по инструменту [документация] (style_id из 1–10 картинок); `IMG-ILLUSTR` — сильная (вектор) [документация] (SVG-вывод; см. G); `IMG-TEXT-CYR` — V3 — нет; V4 — не проверено [документация] (набор символов V3); `IMG-HERO-PHOTO` — слабая [исследование] (AA V4.1 #47 990).
- **Цена (23.09.2026):** прямой API, $: V4.1 1K $0.035 (6,5 с), Pro 2K $0.21, Vector $0.08, Pro Vector $0.30; V4.1 Flash — в прямом API нет (G, 23.09), на RouterAI `recraft/recraft-v4.1-flash` 0,768 ₽ с 24.09 (N/04); V4 Styles $0.035 / vector $0.05; V3 $0.04.
- **Водяные знаки и происхождение:** C2PA: не описано.
- **Лицензия:** Free-план — результаты принадлежат Recraft, коммерция запрещена; платный — полное владение; запрет обучать ИИ на результатах.
- **Маршрутизация:** Для SVG, иконок и повторяемого стиля (style_id) — вне polza, у G. Не для русского текста до проверки V4.
- **Арены (место · балл):** AA t2i «Recraft V4.1»: All #47 990, Text #52 955, UI/UX #28 1020, Retail #45 979, Live-Action #47 997, Animation #50 994, Layout #48 997; AA t2i «Recraft V4.1 Utility»: All #27 1021, Text #38 982, UI/UX #34 1011, Retail #38 994, Live-Action #36 1011, Animation #20 1054, Layout #25 1041; AA t2i «Recraft V4.1 Pro»: All #58 982, Text #48 962, UI/UX #38 1004, Retail #50 975, Live-Action #39 1002, Animation #57 977, Layout #41 1010; AA t2i «Recraft V4.1 Utility Pro»: All #29 1018, Text #27 996, UI/UX #25 1031, Retail #39 991, Live-Action #35 1012, Animation #30 1034, Layout #21 1063; AA t2i «Recraft V4»: All #56 983, Text #54 936, UI/UX #30 1017, Live-Action #48 996, Animation #65 952, Layout #39 1022; LMArena t2i «recraft-v4.1-utility-pro»: Overall #24 1169, Text #28 1162, Photoreal #23 1180, Product #27 1167, 3D #32 1148; LMArena t2i «recraft-v4.1-pro»: Overall #40 1131, Text #31 1156, Photoreal #38 1143, Product #37 1138, 3D #50 1112; LMArena t2i «recraft-v4»: Overall #48 1114, Text #40 1138, Photoreal #49 1119, Product #46 1127, 3D #56 1080.
- **Источники:** [S30], [S36], [S37], [S39], [S40]; YAML: `models/recraft-v4-1.yaml`.

### 3.7 Ideogram 4.0 (открытые веса 9.3B + API) · вне polza

- **Статус:** `current` — июнь 2026; обучена только на структурных JSON-подписях; веса — «Ideogram 4 Non-Commercial», коммерция — через API. Вендор: Ideogram. Релиз: 2026-06.
- **Идентификаторы:** прямой API: Generate v4, Transparent Background v4, Remix v4, Describe v4, Magic Prompt v4 (developer.ideogram.ai); веса: ideogram-oss/ideogram-4; в аренах: AA: Ideogram 4.0 (Quality) Open Weights, Ideogram 4.0 Open Weights; LMArena: ideogram-4.0-quality.
- **Доступ:** прямой API: Ideogram API; веса (nf4 — 24 ГБ GPU); хостинги (fal: Fast, Instant).
- **Вход:** референсы: Remix v4; маска: инструменты: remove/replace background, remove objects/logos, reframe, resize ads, recolor, swap materials, upscale, layerize text.
- **Выход:** альфа: ДА — отдельный эндпоинт Transparent Background v4.
- **Размеры и соотношения:** прямой API: 256–2048 px, кратно 16; соотношения до 6:1 (баннер 1584×396).
- **Текст латиницей:** заявления — «best-in-class multilingual text rendering»; X-Omni EN OCR 0.97 (вендор); независимо — AA TR #33 988; LMArena TR #18 1238 [исследование].
- **Текст кириллицей:** заявления — «multilingual» без списка языков; независимо — нет данных.
- **Диалект промта** (гайд: https://github.com/ideogram-oss/ideogram-4 (docs/prompting.md)): JSON: родной формат: high_level_description; style_description (aesthetics, lighting, photo|art_style, medium, color_palette ≤ 16 hex); compositional_deconstruction (background + elements: obj или text с bbox [y_min, x_min, y_max, x_max] 0–1000 и палитрой ≤ 5 hex); hex: да — в color_palette (до 16) и на элемент (до 5).
  1. `json_prompt` — напрямую; `text_prompt` — через magic prompt (проза → JSON)
  2. текст — элементом `text` с bbox: координатное размещение надписей
  3. референсный пайплайн валидирует JSON по схеме
- **По задачам:** `IMG-TEXT-LATIN` — сильная по инструменту (bbox) [документация] (но AA TR #33); `IMG-CUTOUT` — да (API) [документация] (Transparent Background v4); `IMG-BG-ABSTRACT` — сильная (палитра hex) [документация] (color_palette); `IMG-MOCKUP` — средняя [исследование] (AA UI/UX #22 1051).
- **Цена (23.09.2026):** прямой API, $: AA: 4.0 Quality $100/1k, 4.0 $60/1k; fal: Fast $10.5–17.5/1k, Instant $7.5/1k.
- **Водяные знаки и происхождение:** C2PA: не описано; прочее: `enable_copyright_detection` (Hive) — проверка на совпадение с защищёнными работами.
- **Маршрутизация:** Чистый контроль для D2 (JSON-нативная модель) и точное размещение текста bbox; вне polza.
- **Арены (место · балл):** AA t2i «Ideogram 4.0 (Quality) Open Weights»: All #33 1011, Text #33 988, UI/UX #22 1051, Retail #31 1002, Live-Action #42 1000, Animation #41 1004, Layout #20 1066; AA t2i «Ideogram 4.0 Open Weights»: All #38 1003, Text #28 995, UI/UX #31 1017, Retail #43 983, Live-Action #43 999, Animation #35 1018, Layout #30 1034; LMArena t2i «ideogram-4.0-quality»: Overall #18 1204, Text #18 1238, Photoreal #20 1202, Product #18 1224, 3D #21 1179.
- **Источники:** [S31], [S36], [S37], [S39], [S40]; YAML: `models/ideogram-4-0.yaml`.

### 3.8 Midjourney V8.2 — официального API нет · вне polza

- **Статус:** `no-api` — по умолчанию с 24.07.2026; официального API нет — только «Enterprise API Survey» (заявка); сторонние «Midjourney API» — неофициальные. Вендор: Midjourney. Релиз: V8.2 — 2026-07-24; V8.1 — 2026-04-14; V8.0 alpha — 2026-03-17; Niji 7 — 2026-01-09.
- **Идентификаторы:** прочее: веб и Discord; параметр --v 8.2; в аренах: AA: только Midjourney v7 Alpha (#108, «No API available»); LMArena: нет.
- **Доступ:** прямой API: нет API; ручная работа в веб-интерфейсе.
- **Вход:** референсы: Style Reference + коды + `--sw`; Moodboards; Image Prompts + вес; Edit Model (заменил Omni Reference, Character Reference, Retexture); маска: инпейнт/аутпейнт в редакторе (на HD понижают до SD).
- **Размеры и соотношения:** прямой API: до 14:1 (4:1 в HD); HD 2048 px.
- **Параметры:** прямой API: `--ar`, `--no`, `--tile`, `--sref`/`--sw`, `--seed` («99% identical»), персонализация; нет: `--q`, Draft, Turbo, Multi-Prompting.
- **Текст латиницей:** заявления — нет; независимо — в аренах V8.x нет.
- **Текст кириллицей:** заявления — нет; независимо — Хабр/studyai (N=1): «руны» вместо кириллицы [мнение].
- **Диалект промта** (гайд: https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version): негатив-параметр: `--no`.
  1. стиль — `--sref` + код и `--sw`
  2. бесшовная текстура — `--tile` (единственная из изученных с параметром tile)
  3. `--seed` воспроизводит «99%»
- **По задачам:** `IMG-TEXTURE` — единственная с `--tile` [документация] (но нет API — не для конвейера); `IMG-ILLUSTR` — не измерено [не проверено] (арен для V8.x нет); `IMG-TEXT-CYR` — слабая [мнение] (N=1).
- **Цена (23.09.2026):** прямой API, $: подписка; HD = 1,3 мин GPU против 0,8 SD.
- **Водяные знаки и происхождение:** C2PA: не описано.
- **Маршрутизация:** Не включать в автоматический конвейер: нет официального API; неофициальные обёртки — риск нарушения условий (P, L).
- **Арены (место · балл):** AA t2i «Midjourney v7 Alpha»: All #108 878.
- **Источники:** [S34], [S50], [S48], [S36], [S37], [S39], [S40]; YAML: `models/midjourney-v8-2.yaml`.

### 3.9 MAI-Image-2.6 и 2.6-Flash (Microsoft AI) · вне polza

- **Статус:** `current (public preview)` — анонс 10.08.2026; Public Preview в Microsoft Foundry 04.09.2026 вместе с 2.6-Flash. Вендор: Microsoft AI. Релиз: 2026-08-10 (анонс); 2026-09-04 (Foundry preview).
- **Идентификаторы:** прямой API: MAI-Image-2.6, MAI-Image-2.6-Flash (Microsoft Foundry); в аренах: AA: MAI-Image-2.6, MAI-Image-2.6-Flash; LMArena: mai-image-2.6.
- **Доступ:** прямой API: Microsoft Foundry (public preview); в polza нет.
- **Вход:** референсы: multi-reference editing; маска: не описано.
- **Размеры и соотношения:** прямой API: «dynamic aspect ratios», до 1.5K.
- **Текст латиницей:** заявления — «+79 Elo к 2.5, текст +91 Elo»; независимо — AA TR #5 1141; LMArena TR #4 1370 [исследование].
- **Текст кириллицей:** заявления — нет; независимо — нет данных.
- **Правка:** AA editing #3 1131 (2.6-Flash #4 1123); LMArena edit #5 1429; вендор 04.09: «No. 1 for image editing» — устарело после GPT Image 2.5 (08.09).
- **Диалект промта** (гайд: —): —.
  1. гайд по промтам не найден
- **По задачам:** `IMG-HERO-PHOTO` — сильная [исследование] (AA #5 1147; Retail #3, Lighting #3, Material #3); `IMG-EDIT` — сильная [исследование] (AA editing #3); `IMG-PRODUCT` — сильная [исследование] (AA Retail #3 1148).
- **Цена (23.09.2026):** прямой API, $: AA: 2.6 $38.9/1k, 2.6-Flash $19.5/1k («2.8x faster than GPT-Image-2-Medium»).
- **Водяные знаки и происхождение:** C2PA: не описано в прочитанном.
- **Маршрутизация:** Самый сильный кандидат вне polza по соотношению цена/качество (AA #5 за $0.039); ограничение — до 1.5K; доступ — P.
- **Арены (место · балл):** AA t2i «MAI-Image-2.6»: All #5 1147, Text #5 1141, UI/UX #5 1169, Retail #3 1148, Live-Action #4 1142, Animation #5 1166, Layout #4 1182; AA t2i «MAI-Image-2.6-Flash»: All #11 1100, Text #7 1109, UI/UX #7 1148, Retail #6 1115, Live-Action #15 1071, Animation #8 1138, Layout #7 1161; AA правка «MAI-Image-2.6»: All #3 1131, Text/Symbol #3 1153, Identity #7 1147, Composition #4 1135; AA правка «MAI-Image-2.6-Flash»: All #4 1123, Text/Symbol #4 1145, Identity #5 1152, Composition #5 1124; LMArena t2i «mai-image-2.6»: Overall #4 1334, Text #4 1370, Photoreal #4 1328, Product #4 1342, 3D #4 1327; LMArena правка «mai-image-2.6»: Overall #5 1429, Text #7 1442.
- **Источники:** [S32], [S36], [S37], [S39], [S40]; YAML: `models/mai-image-2-6.yaml`.

### 3.10 Muse Image (Meta Superintelligence Labs) · вне polza

- **Статус:** `current (consumer)` — 07.07.2026; агентная модель (вызывает код для графиков и QR, поиск; самопроверка); доступ — Meta AI app, meta.ai, Instagram Stories, только США. Вендор: Meta. Релиз: 2026-07-07.
- **Идентификаторы:** в аренах: AA: Muse Image (провайдер Meta, $10/1k); LMArena: muse-image.
- **Доступ:** прямой API: публичный API в анонсе не упомянут, но AA показывает провайдера Meta с ценой $10/1k [спорно].
- **Текст латиницей:** заявления — нет; независимо — AA TR #15 1071; LMArena TR #7 1300.
- **Текст кириллицей:** заявления — нет; независимо — нет данных.
- **Правка:** AA editing #6 1115; Scene & Style Edit #3; LMArena edit #6 1402.
- **Диалект промта** (гайд: —): —.
  1. гайд по промтам не опубликован; модель агентная — сама вызывает код (графики, QR) и поиск, проверяет результат [мнение вендора]
- **По задачам:** `IMG-HERO-PHOTO` — сильная [исследование] (AA #7 1113 при $10/1k); `IMG-SERIES` — сильная [исследование] (AA Identity Preserving #4 1154).
- **Цена (23.09.2026):** прямой API, $: AA $10/1k (18,6 с).
- **Водяные знаки и происхождение:** видимый: нет; невидимый: Content Seal — невидимый знак, устойчивый к кропу и сжатию; проверка на meta.ai/identification; C2PA: не описано.
- **Маршрутизация:** Не планировать: нет подтверждённого API вне США/продуктов Meta.
- **Арены (место · балл):** AA t2i «Muse Image»: All #7 1113, Text #15 1071, UI/UX #9 1133, Retail #10 1094, Live-Action #8 1112, Animation #9 1136, Layout #12 1133; AA правка «Muse Image»: All #6 1115, Text/Symbol #9 1115, Identity #4 1154, Composition #6 1123; LMArena t2i «muse-image»: Overall #7 1276, Text #7 1300, Photoreal #7 1285, Product #9 1265, 3D #11 1245; LMArena правка «muse-image»: Overall #6 1402, Text #8 1432.
- **Источники:** [S33], [S36], [S37], [S39], [S40]; YAML: `models/muse-image.yaml`.

### 3.11 HunyuanImage 3.0 / Instruct (Tencent) · вне polza

- **Статус:** `current (open weights)` — 80B MoE (64 эксперта, 13B активных); лицензия не действует в ЕС, Великобритании и Южной Корее. Вендор: Tencent Hunyuan. Релиз: 2025-09-28; Instruct и Distil — 2026-01-26.
- **Идентификаторы:** веса: tencent/HunyuanImage-3.0; …-Instruct; …-Instruct-Distil (8 шагов); в аренах: AA: HunyuanImage 3.0 Instruct (Fal); LMArena: hunyuan-image-3.0, hunyuan-image-3.0-instruct.
- **Доступ:** прямой API: веса; хостинги (fal); VRAM: t2i ≥ 3×80 ГБ, Instruct ≥ 8×80 ГБ — на видеокарта 24 ГБ не запустить.
- **Вход:** референсы: Instruct: i2i, правка, мульти-фьюжн; маска: не описано.
- **Текст латиницей:** заявления — нет; независимо — AA TR #55 933.
- **Текст кириллицей:** заявления — нет; независимо — нет данных.
- **Правка:** AA editing #29 1026; LMArena edit (Instruct) #23 1302.
- **Диалект промта** (гайд: https://github.com/Tencent-Hunyuan/HunyuanImage-3.0): —.
  1. отдельный гайд по промтам не изучался; Instruct рассуждает перед генерацией (i2i, правка, мульти-фьюжн)
- **По задачам:** `IMG-*` — середина [исследование] (AA t2i Instruct #66 964; LMArena #32 1151).
- **Цена (23.09.2026):** прямой API, $: AA $90/1k (Instruct, fal).
- **Водяные знаки и происхождение:** C2PA: не описано.
- **Лицензия:** Tencent Hunyuan Community: не действует в ЕС, UK, Южной Корее; «must not use… Output… outside the Territory»; > 100 млн MAU — отдельная лицензия.
- **Маршрутизация:** Не использовать для сайтов с аудиторией ЕС (лицензия); по качеству ниже моделей polza.
- **Бенчмарки (вне арен):** WISE_Verified: HunyuanImage-3.0 0.435 [исследование].
- **Арены (место · балл):** AA t2i «HunyuanImage 3.0 Instruct (Fal) Open Weights»: All #66 964, Text #55 933, UI/UX #36 1007, Retail #53 974, Animation #53 981, Layout #49 995; AA t2i «HunyuanImage 3.0 (Fal) Open Weights»: All #71 945, Text #59 897, UI/UX #50 964, Retail #55 966, Live-Action #79 926, Animation #60 964, Layout #59 951; AA правка «HunyuanImage 3.0 Instruct (Fal) Open Weights»: All #29 1026, Text/Symbol #34 1009, Identity #27 1054, Composition #29 1015; LMArena t2i «hunyuan-image-3.0»: Overall #32 1151, Text #33 1150, Photoreal #32 1152, Product #32 1153, 3D #27 1167; LMArena правка «hunyuan-image-3.0-instruct»: Overall #23 1302, Text #23 1286.
- **Источники:** [S35], [S55], [S36], [S37], [S39], [S40]; YAML: `models/hunyuanimage-3-0.yaml`.

## Частые ошибки

1. **Id «по памяти».** `openai/gpt-image-2.5-flare`, `google/gemini-3-pro-image`, `bytedance/seedream-5-pro` в polza не
   существуют; правильные: `gpt-image-2-5-flare`, `google/gemini-3-pro-image-preview`, `seedream/5-pro-text-to-image`
   (каталог 23.09.2026) [S1]. [поправка фазы 5, 25.09.2026: было: Flare — `gpt-image-2-5-flare`; с 25.09 в polza наоборот — `openai/gpt-image-2.5-flare`,
   старого id нет: id берётся из снимка дня, не из этой строки]
2. **Устаревшие модели «по памяти».** Imagen 4, DALL·E 3, gpt-image-1 предлагаются агентами как «надёжные» — первые две
   выключены, третья выключается 23.10.2026 [S8], [S13], [S15].
3. **Параметры одного провайдера на другого.** 4K и 16 референсов у `openai/gpt-5.4-image-2@mie` ≠ провайдер `openai`
   (до 2K, 10 реф.); 14 референсов Nano Banana Pro у bananalab ≠ 8 у mie [S1].
4. **Параметры прямого API в polza.** `quality`, `background`, `input_fidelity`, `n` для GPT Image 2.5, `steps`/`guidance`
   для FLUX.2 [flex], `disable_pup`, `watermark` для Seedream в каталоге polza не описаны — передавать их бессмысленно
   (игнор или ошибка — [не проверено]).
5. **«high = 4K» у Seedream.** У 5.0 Pro `high` = 2K, у 5.0 Lite — 3K, у 4.5 — 4K; у 4.0 — отдельный `image_resolution` [S1].
6. **`auto` и 1:1 у GPT 2.5 в polza.** При `aspect_ratio: auto` доступно только 1K; для 1:1 нет 4K (описания параметров
   каталога) [S1].
7. **Негатив там, где его нет.** Поле `negative_prompt` ни у одной модели polza; у FLUX.2 «No negative prompts» — перечень
   запретов в промте работает против цели; у Google — формулировать желаемое («пустая улица», а не «без машин») [S10], [S16].
8. **Hex как гарантия цвета.** Hex документирован как механизм только у FLUX.2 (в промте/JSON) и Ideogram 4.0
   (`color_palette`); у Recraft — `controls.colors` в API; у остальных — пожелание. Проверять ΔE2000 (тест 8) [S16], [S31], [S30].
9. **Шахматка вместо альфы.** «A drawn checkerboard is not transparency» (OpenAI): проверять наличие альфа-канала и
   полупрозрачность на волосах, стекле, тенях [S6].
10. **Маска «наоборот».** Qwen 2.1 в polza: белое = менять; GPT-5 Image у mie: чёрное = менять [S1].
11. **Арена как истина для polza.** Места GPT 2.5 — в режиме `max`; какой уровень отдаёт mie, не описано; промты арен —
    английские, кириллицу не проверяют [S38].
12. **«Pro лучше в тексте».** Заявление Google о Nano Banana Pro арены не подтверждают: AA TR #11 против #8 у NB2;
    LMArena TR #13 против #9 [S36], [S39].
13. **Grok в polza = Grok 2.0.** `x-ai/grok-imagine-image` — базовая модель (AA #28), не 2.0 (AA #4) [S27], [S36].
14. **Длинный промт в Z-Image.** Лимит 1000 символов в polza — JSON-спецификации и длинные брифы не помещаются [S1].
15. **Алиас `@provider` для media.** Документация polza: «Alias-формат работает только для chat/responses/messages»;
    гайд GPT-5.4 Image 2 советует `…@mie` — противоречие, проверять у B [S2].
16. **Коммерция на Qwen 2.1 без решения L.** Веса — «research or evaluation purposes only» [S23].
17. **Счёт референсов по гайду polza.** Гайды polza пишут «до 8» для Nano Banana 2/Pro, каталог у mie/bananalab — 14;
    верить каталогу провайдера [S1], [S2].

## Чек-лист

- Id модели скопирован из каталога polza 23.09.2026 (или свежего), а не из памяти?
- Параметры взяты из `providers[<провайдер>].parameters` того провайдера, который реально отвечает?
- Модель не в списке устаревших (§1.3) и не выключается в ближайшие 3 месяца?
- Для прозрачного фона выбрана модель с альфой (Qwen 2.1 в polza или прямой API), а не «прозрачный фон» словами?
- Для текста на картинке: строка в кавычках, «только этот текст, дословно», и есть OCR-проверка по кодовым точкам?
- Для кириллицы: модель из кандидатов с данными (GPT 2.x, Nano Banana 2, Seedream 5.0 Pro, Qwen 2.1) и есть фолбэк «текст кодом»?
- Негатив сформулирован описанием желаемого, без `no …`-списков для FLUX.2?
- Hex-цвета проверяются ΔE после генерации?
- Для Seedream проверено отсутствие видимого «AI-generated» (тест 2)?
- Для серии зафиксированы seed (где есть) и эталонный референс?
- Для 21:9 и 8:1 выбрана модель, у которой это соотношение есть в каталоге (§1.4)?
- Для 4K посчитана цена: 11 ₽ (GPT 2.5) против 10,8 ₽ (NB2) против 5 ₽ (Seedream 4.5) против 3 ₽ (Seedream 4.0)?
- Метаданные происхождения (C2PA, SynthID) учтены в политике страницы (у L/J)?

## Открытые вопросы и противоречия

1. **Что отдаёт mie под GPT Image 2.5:** уровень `quality`, фактические пиксели 2K/4K, формат; от этого зависит перенос
   аренных мест на polza (тест 3).
2. **Какая модель под `google/…-preview` у mie/bananalab** после выключения preview-эндпоинтов Google 25.06.2026 (тест 7:
   поля ответа `model`, провайдер).
3. **Google против Google:** на странице Nano Banana Pro «Flex inference Not supported», в прайсе и в polza — flex есть;
   соотношения 1:4…8:1 для Pro указаны на Vertex, но не в Gemini API [S11], [S12], [S15].
4. **polza против polza:** маски противоположной полярности; `openai/gpt-5-image` — гайд 32 000 символов и 10 картинок,
   каталог mie — 4000 и 5; «по умолчанию» у GPT-5.4 Image 2 — openai (гайд) или mie (`top_provider`) [S1], [S2].
5. **Вендор против арен:** Google «Pro — лучшая типографика» vs NB2 выше в обеих аренах; BFL «[max] — strongest editing
   consistency» vs AA правка #45; Microsoft «№1 в правке на AA» (04.09) устарело после GPT 2.5 (08.09) [S32], [S36], [S37].
6. **WeGenBench против арен:** Seedream 4.5 — лучший текст (Char F1 0.79), в аренах — середина (AA TR #30); NB2 — высоко в
   аренах, но precision 0.43 в WeGenBench. Разные метрики: арена — «что нравится», WeGenBench — посимвольная точность без
   лишнего текста (zh/en) [S42].
7. **Muse Image API:** анонс Meta API не упоминает, AA показывает провайдера Meta и $10/1k [S33], [S36].
8. **Z-Image в polza — Turbo или Base?** От этого зависит, работает ли негатив (CFG) и сколько шагов [S25].
9. **Topaz в polza — какая модель** (Standard, High Fidelity, Bloom…) и сохраняется ли альфа (тест 14) [S29].
10. **Права на результат Qwen 2.1 через mie** при некоммерческой лицензии весов — к L [S23].
11. **C2PA у OpenAI, BFL, ByteDance, xAI** — в прочитанной документации нет; справка openai.com не открылась (403) → тест 7.
12. **Референсы FLUX.2 [max]:** release notes — «до 10 входов», API reference — до 8 (`input_image_8`) [S17], [S18].
13. **Qwen-Image-3.0-Pro «12 languages»** — список не найден; есть ли русский, неизвестно [S24].
14. **Серии: специализированные бенчмарки против арен.** ViStoryBench (29.08.2026) и OmniRef-Bench (06.2026) ставят Nano
    Banana Pro №1, но GPT Image 1.5/2/2.5 и Nano Banana 2 в них не участвуют; AA Identity Preserving — №1 GPT 2.5. Прямое
    сравнение — тест 5 (Flare против NB Pro против Seedream 4.5) [S70], [S71], [S37].
15. **LingT2I:** «Nano Banana» без версии; OCR выполняет Gemini 2.5 Flash при оценке модели Google — возможный перекос [S67].

## Источники

Нумерация [S#] общая для всех файлов `03-image-models/` (реестр — `99-raw/experiments/C1/06-model-cards-build/sources.py`).

- [S1] polza.ai. Каталог моделей API (type=image, с провайдерами). снят 2026-09-23 08:45. https://polza.ai/api/v1/models?type=image&include_providers=true — первичные данные: id, провайдеры, параметры с описаниями, цены ₽; бесплатный эндпоинт [проверено].
- [S2] polza.ai. Документация polza (gaidy/*.mdx, changelog.mdx, provider-selection.mdx). снимок 2026-09-23. https://github.com/polza-ai/docs — гайды по моделям местами расходятся с каталогом (10 противоречий, §0 заметок C1).
- [S4] OpenAI. Страницы моделей gpt-image-2.5-sunburst, -flare, gpt-image-2, gpt-image-1.5. 2026-09-23. https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst — снимки, цены токенов, статус Deprecated у 1.5.
- [S5] OpenAI. Image generation guide (+ калькулятор токенов GptImageTokenCalculator). 2026-09-23. https://developers.openai.com/api/docs/guides/image-generation — параметры, размеры, маска, прозрачность, формула токенов [проверено].
- [S6] OpenAI. Image prompting guide (вкладки 2.5 / 2 / 1.5 / 1). 2026-09-23. https://developers.openai.com/api/docs/guides/image-prompting — канонический гайд по промтам GPT Image; заменил cookbook-гайд.
- [S7] OpenAI. API changelog. 2026-09-23. https://developers.openai.com/api/docs/changelog — даты: 21.04.2026 GPT Image 2, 20.08.2026 прозрачность, 08.09.2026 GPT Image 2.5.
- [S8] OpenAI. Deprecations. 2026-09-23. https://developers.openai.com/api/docs/deprecations — gpt-image-1 → 23.10.2026; gpt-image-1.5, gpt-image-1-mini → 01.12.2026.
- [S10] Google. Gemini API — Image generation (Nano Banana). 2026-09-23. https://ai.google.dev/gemini-api/docs/image-generation — модели, размеры, токены, референсы, языки (ru-RU), лучшие практики.
- [S11] Google. Страницы моделей gemini-3-pro-image, gemini-3.1-flash-image, gemini-3.1-flash-lite-image. 2026-09-23. https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image — возможности, SynthID+C2PA у Lite, латентность.
- [S12] Google. Gemini Developer API pricing. 2026-09-23. https://ai.google.dev/gemini-api/docs/pricing — $/1M токенов и $ за картинку по размерам.
- [S13] Google. Gemini API changelog. 2026-09-23. https://ai.google.dev/gemini-api/docs/changelog — GA 28.05.2026; preview выключены 25.06.2026; Imagen выключен 17.08.2026.
- [S14] Google Cloud (K. Davaajav, H. Chinoy). Ultimate prompting guide for Nano Banana. 2026-03-06. https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana — формулы промтов, текст, C2PA + SynthID.
- [S15] Google Cloud. Vertex AI: Imagen 4; Gemini 3 Pro Image; deprecations. 2026-09-23. https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate — Imagen 4 Discontinuation 30.06.2026, C2PA Not supported; Vertex → Gemini Enterprise Agent Platform.
- [S16] Black Forest Labs. FLUX.2 prompting guide. 2026-09-23. https://docs.bfl.ml/guides/prompting_guide_flux2 — No negative prompts, порядок слов, JSON, hex.
- [S17] Black Forest Labs. API reference: flux2-pro, -max, -flex, -klein-9b, outpainting, erase (OpenAPI). 2026-09-23. https://docs.bfl.ml/api-reference/models/generate-or-edit-an-image-with-flux2-pro — параметры: disable_pup, steps, guidance, input_image_1…8, output_format.
- [S18] Black Forest Labs. Release notes. 2026-09-23. https://docs.bfl.ml/release-notes — даты FLUX.2, Tools, FLUX 3 (только видео).
- [S19] Black Forest Labs. Pricing + FLUX.2 overview. 2026-09-23. https://docs.bfl.ml/quick_start/pricing — кредиты $0.01; роли pro/max/flex/klein.
- [S20] ByteDance Seed. Seedream 5.0 Pro — блог + страницы 5.0 Pro, 5.0 Lite, 4.5. 2026-07-08. https://seed.bytedance.com/en/blog/beyond-generation-it-understands-design-introducing-seedream-5-0-pro — заявления вендора: языки, инфографика, слои; ограничения текста.
- [S21] BytePlus ModelArk. Image generation API (Seedream 5.0 pro/flash/lite, 4.5, 4.0). 2026-09-23. https://docs.byteplus.com/en/docs/ModelArk/1541523 — языки промта, size, watermark default true, background, layers, sequential.
- [S22] BytePlus ModelArk. Seedream 4.0–4.5 prompt guide. обновлён 2026-07-06. https://docs.byteplus.com/en/docs/ModelArk/1829186 — диалект: кавычки для текста, правка, серии.
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
- [S47] Genova AI (блог на Клерк.ру). Сравнение генераторов на русских промтах (4 макета × 3 модели, первая генерация). 2026-08-26. https://www.klerk.ru/blogs/genova-ai/706310/ — партнёрский материал агрегатора; картинки проверены глазами [мнение].
- [S48] StudyAI (Хабр). Сравнение 6 моделей на одном русском рекламном задании, N=1. ≈ 2026-09-22. https://habr.com/ru/companies/studyai/articles/1085264/ — корпоративный блог агрегатора [мнение].
- [S49] ui-research (соседняя база). Модели картинок для UI (22.09.2026), GEBench. 2026-09-22. ../../ui/12-ai-generated-ui/01-image-models-for-ui.md — GEBench (arXiv 2602.09007) — числа по соседнему файлу, первоисточник не перечитан.
- [S50] Midjourney. Enterprise API Survey. 2026-09-23. https://updates.midjourney.com/enterprise-api-survey/ — подтверждает отсутствие публичного API.
- [S53] Meta FAIR / UW. GenEval 2 (Soft-TIFA); GitHub facebookresearch/GenEval2 91★. 2025-12-18. https://arxiv.org/abs/2512.16853 — 800 промтов, судья Qwen3-VL-8B; аудит насыщения GenEval.
- [S55] PKU-YuanGroup. WISE (ICML 2026) + лидерборд WISE_Verified (GitHub PKU-YuanGroup/WISE 220★). обновлён 2026-06-26. https://arxiv.org/abs/2503.07265 — знание мира; Verified — судья Qwen3.5-35B-A3B, 29 моделей.
- [S56] Sun et al. T2I-ReasonBench (ACL 2026 Findings). 2026. https://arxiv.org/abs/2508.17472 — 800 промтов, судья Gemini-2.5-pro; близок к потолку.
- [S57] PLUM-Lab. R2I-Bench (EMNLP 2025). 2025. https://arxiv.org/abs/2505.23493 — 3068 промтов; модели ≤ 04.2025.
- [S58] OneIG-Bench authors. OneIG-Bench (NeurIPS 2025 D&B) + лидерборд oneig-bench.github.io. лидерборд 2025-09-19. https://arxiv.org/abs/2506.07977 — 5 измерений EN/ZH; заморожен.
- [S60] Wu et al. KRIS-Bench (NeurIPS 2025) + живой лидерборд. обновлён 2026-05-06. https://arxiv.org/abs/2505.16707 — правка, требующая знаний; судья GPT-4o.
- [S63] Jiang et al. GEditBench v2 (попарный Elo). 2026-03. https://arxiv.org/abs/2603.28547 — 1200 запросов, 23 задачи; ρ = 0.929 с Arena.
- [S64] RISEBench authors. RISEBench (NeurIPS 2025 D&B Oral) + живой лидерборд (GitHub PhoenixZ810/RISEBench 154★). обновлён 2026-04-23. https://arxiv.org/abs/2504.02826 — правка с рассуждением; 360 примеров; судья GPT-4.1.
- [S65] T2I-CoReBench authors. T2I-CoReBench (ICLR 2026) — лидерборд. 2026. https://t2i-corebench.github.io/ — судья Gemini 2.5 Flash; есть Nano Banana 2/Pro, Seedream 4.5.
- [S66] Qwen team. Qwen-Image-Bench. 2026-05. https://arxiv.org/abs/2605.28091 — бенчмарк вендора; GPT Image 2 65.23.
- [S67] RISys-Lab. LingT2I: многоязычный рендер текста в генерации (ACM MM 2026), 10 языков вкл. русский. 2026-08-11. https://arxiv.org/abs/2608.11002 — единственный найденный независимый бенчмарк генерации русского текста; модели 2025 года; OCR — Gemini 2.5 Flash.
- [S70] ViStoryBench authors. ViStoryBench (CVPR 2026) + живой лидерборд vistorybench.github.io. обновлён 2026-08-29. https://arxiv.org/abs/2505.24862 — серии кадров с персонажами; NB Pro №1 в Lite.
- [S71] —. OmniRef-Bench (DyRef). 2026-06-25. https://arxiv.org/abs/2606.26947 — 2–7 референсов (субъект, фон, стиль, свет, поза); судья Gemini 3 Flash.
- [S72] Matsuo Lab. MultiBanana (CVPR 2026). 2025-11 / 2026. https://arxiv.org/abs/2511.22989 — до 8 референсов; NB против GPT-Image-1.
- [S73] VectorSpaceLab. OmniGen2 / OmniContext. 2026-04 (v4). https://arxiv.org/abs/2506.18871 — 400 примеров; судья GPT-4.1; результаты плохо воспроизводятся.
- [S74] —. DreamBench++ (ICLR 2025). 2025. https://arxiv.org/abs/2406.16855 — персонализация по одному референсу; модели эпохи SDXL.
