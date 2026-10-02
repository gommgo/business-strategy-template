# Мультиканальный клиент фазы 5: RouterAI, Gen-API, polza-chat, polza-images

Волна 3 · агент B2 · 23.09.2026 · источников целиком 16, просмотрено 12 · опытов 2 (B2/01 макет каналов — 44/44
сценария; B2/02 `estimate` всех заданий каналов — 31 файл, 65 заданий, 0 ошибок) · снимки каталогов: polza
`2026-09-23_1745`, RouterAI и Gen-API `2026-09-23_1837` · клиент `../../scripts/ai-media/mp_client.py` 1.0 проверен только на
макете: ключей нет, платных вызовов не было.

## Выжимка для агента

1. Любое задание вне Media API polza (`*.routerai.json(l)`, `*.genapi.json`, `*.polza-chat.json`, `*.polza-images.json`)
   исполнять только через `mp_client.py`: сухой прогон по умолчанию, трата — только с `--live` → §2 [проверено: B2/01 №1].
2. Ключи — файлы `~/.config/routerai/api_key`, `~/.config/genapi/api_key`, `~/.config/polza/api_key` (права 600) или
   `ROUTERAI_API_KEY` / `GENAPI_API_KEY` / `POLZA_API_KEY`; клиент читает ключ только при `--live` и только нужного канала,
   `Authorization` уходит только на хост своего канала → §2.1, §7.3 [проверено: B2/01 №43].
3. `ROUTERAI_BUDGET_TOTAL` и `GENAPI_BUDGET_TOTAL` по умолчанию **0 — `--live` откажет**, пока заказчик не задаст лимит;
   polza-chat и polza-images считаются в общий `POLZA_BUDGET_TOTAL` вместе с `polza.py` (один журнал
   `99-raw/experiments/_ledger.jsonl`) → §4.3 [проверено: B2/01 №34, №36].
4. Порядок фазы 5: `snapshot` (бесплатный публичный GET каталогов) → `estimate` всех файлов → зонды §5 → серии
   `batch` → §2.2 [проверено: snapshot 23.09 19:07; estimate B2/02].
5. RouterAI картинки — синхронный `POST /api/v1/images`: ответ `data[].b64_json` (+ `media_type`), цена
   **`usage.cost` в рублях**, ссылок нет — файл пишется из ответа → §1.1 [документация S1; проверено: B2/01 №2].
6. `input_references` у RouterAI — массив **объектов** `{"type": "image_url", "image_url": {"url": …}}`, не строк; `mask`
   — только `openai/gpt-image-*` и только вместе с `input_references` → §3.2 [документация S1; B2/02 правка H-06].
7. Recraft Vector через RouterAI отдаёт SVG (`supported_output_formats: ["svg"]`, `media_type: image/svg+xml`); клиент
   сохраняет `.svg` по `media_type` или по сигнатуре и кладёт в паспорт корень, `viewBox`, число путей и цветов →
   §1.1 [документация S3, S4; форма ответа RouterAI — не проверено] [поправка фазы 5, 25.09.2026: SVG приходит, но в `<metadata>` — C2PA-манифест
   17,7 КБ (30–79 % веса), `<recraft-signature>` нет; после чистки путей манифест `Invalid` → мастер хранить побайтно →
   `99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md`].
8. Провайдерные параметры картинок RouterAI (`provider.options.recraft.controls`, `style`, `style_id`, `disable_pup` в
   корне) **не документированы** — это гипотезы тестов (записаны в `notes`), первым делом — зонд за 0 ₽: заведомо неверное
   значение → 400 без списания = параметр доходит → §5 [не проверено] [поправка фазы 5, 25.09.2026: B2-01 — неверный `controls` Recraft → HTTP 200
   без `data[]`, 0 ₽ (не 400), тот же промт без поля — картинка → поле доходит; валидная палитра параметром не проверялась].
9. RouterAI видео: `POST /api/v1/videos` → 202 `{id, polling_url}` → опрос → `unsigned_urls` скачивать **с ключом**;
   не больше 3 активных задач (иначе 429); `expired` — терминальный статус → §1.2 [документация S2; проверено: B2/01 №14–17].
10. Видео через RouterAI в 1,4–5,4 раза дороже polza на тех же моделях (одна цена за секунду без ступеней): Seedance 1.5
    Pro 4 с — 22,66 против 5,25 ₽ (480p без звука), Grok Imagine Video 1.5 4 с — 34,97 против 6,48 ₽ → видео фазы 5 через
    polza → §1.2 [документация S3, S13].
11. Gen-API: `POST /api/v1/networks/{slug}` → `request_id` → опрос `GET /api/v1/request/get/{id}` (processing →
    success | error); ссылки на файлы живут **24 ч** — скачивать сразу, полный результат — 14 дней → §1.3 [документация S6;
    проверено: B2/01 №19–25] [поправка фазы 5, 25.09.2026: 30 генераций, 384 ₽: `result` иногда приходит объектом `{"0": url, "structured_prompt": …}`
    (Bria FIBO — клиент починен); `data:URI` в `url_or_file`/`image_url` → 422 без списания — вход только публичным URL
    (выложен в хранилище polza); списание — по факту, сверка по балансу].
12. Параметры Gen-API брать из публичного каталога `GET /api/v1/networks?include=parameters` (типы, `required`, `default`,
    `items`, `cost`, `is_payment_upfront`), а не со страниц моделей — они расходятся → §1.3 [документация S7, S8]
    [поправка фазы 5, 25.09.2026: **цену** — наоборот, со страницы модели: `cost` каталога — минимальная ступень, списание зависит от параметров —
    Hunyuan3D с текстурой 96 ₽ (каталог 32), TRELLIS.2 1024 — 75 (62,5), Tripo Standard — 75 (50), Hunyuan Image V3 — 45 (22,5);
    `prompt` > 1 000 символов → 422 (Bria), пустой `negative_prompt` → 422 (Imagen 4), 402 — кончились деньги →
    `99-raw/experiments/3D/README.md`, `99-raw/experiments/_ledger.jsonl`].
13. `translate_input` у Gen-API: у `recraft-v4` по умолчанию **true** (платный перевод GPT-4.1, переводит и надписи), у
    `flux-2` и `qwen-image-layered` — false; клиент шлёт `false`, если задание молчит → §3.3 [документация S7; проверено:
    B2/01 №20].
14. Gen-API `recraft-v4`: `pro` по умолчанию true (**75 ₽** вместо 20 за вектор), `model` по умолчанию `image` — клиент
    требует оба явно → §3.3 [документация S7, S9].
15. polza-chat: цена по токенам каталога (`top_provider.pricing.*_per_million`, ₽); без `max_tokens` клиент ставит потолок
    по `max_rub` (F-05 → 16 662 ток.); рассуждения биллятся как выход → §3.4 [документация S10; проверено: B2/01 №27]
    [поправка фазы 5, 25.09.2026: рассуждения биллятся **сверх** `max_tokens` и могут съесть ответ: B2-03 — ≈ 121 токен при лимите 64, пустой ответ;
    G-03 (Claude Sonnet 5, `max_tokens` 8000) — пустой ответ «length» за 9,77 ₽; DeepSeek V4.1 Flash — 1,17 ₽ при оценке 0,17 (8 000 ток. = `max_tokens`, ставка провайдера ×3,6 к оценке);
    190 чат-вызовов фазы 5 — 17,06 ₽].
16. polza-images `POST /api/v2/images/generations`: синхронно до 120 с, иначе `{id, status: pending}` → опрос
    `GET /api/v1/media/{id}`; `background`, `output_format`, `n` описаны в `openapi.json` («для gpt-image-1»), в mdx их нет
    → §1.4 [документация S11, S12].
17. Как `/v2` выбирает ступень цены по `size`, не документировано: худший случай — запасная ступень каталога (GPT Image
    2.5 — 11 ₽ вместо 4); `openai/gpt-5.4-image-2` имеет запасную ступень 4 ₽ → тот же вопрос прозрачности за ≤ 4 ₽ → §4.2,
    §5 [документация S13; не проверено] [поправка фазы 5, 25.09.2026: H-02 (`/v2` с `background`) не прогонялся — отменено заказчиком 25.09].
18. GPT Image через RouterAI считается токенами по формуле OpenAI: 2.5 medium 1024² = 439 ток. = 1,44 ₽; **gpt-image-2
    medium = 1756 ток. = 5,76 ₽** — сетки качества у 2 и 2.5 разные → §4.1 [проверено: формула C1/02 = таблица OpenAI;
    B2/02 H-06] [поправка фазы 5, 25.09.2026: списание RouterAI = **только выходные токены** × 0,0033113 ₽: 16:9 medium — 280 ток. = 0,93 ₽, high — 1 078 =
    3,57 ₽, 1:1 medium — 439 = 1,45 ₽; входной текст (313–353 ток.) не списан → оценка `mp_client` выше факта на 0,18–0,21 ₽;
    выход 16:9 — 1536×864 → `99-raw/phase5/runs/S5-analysis/README.md` (N-01, H-03)].
19. Лимиты клиент считает по верхней оценке (`--limit-by high`); где верх — только худший документированный случай
    (ступень `/v2`, `quality: auto`), решать осознанно: поднять `max_rub` или `--limit-by expected` → §4.2 [практика].
20. Повтор POST — только при 429; 5xx и обрыв после отправки не повторяются (двойное списание); обрыв → событие
    `unknown` с резервом оценки → §7.2 [проверено: B2/01 №8–10] [поправка фазы 5, 25.09.2026: 5 обрывов вживую (RouterAI 4, Gen-API 1) разрешены
    сверкой: RouterAI — `usage` ключа = сумма журнала, Gen-API — баланс; не созданы → `NETWORK_RESOLVED`, повтор, двойных
    списаний 0].
21. Кэш по хэшу запроса (с учётом содержимого файлов): тот же запрос → 0 ₽; повтор — другой `variant` или `--force` →
    §4.4 [проверено: B2/01 №3–4].
22. Шаблоны `{{ИМЯ}}` (G-05) и «<…>» в полях файлов (D2-03): `estimate` — предупреждение и цена по `price_rub`,
    `--live` — отказ до `--set ИМЯ=значение` / `--set-file ИМЯ=путь` → §3.5 [проверено: B2/01 №30].
23. Результат ложится в `99-raw/experiments/_mp/<агент>/<дата>/<tag>__<модель>__<id>.<ext>` с паспортом
    `.passport.json` рядом: запрос без base64 и ключа, ответ, оценка против факта, время, sha256, разбор файла → §7.4
    [проверено].
24. Первые вызовы фазы 5 — зонды §5 (≈ 6,5–21 ₽ без Z4; из них 6,5–13,5 ₽ — сами тесты H-03, G-16, H-02): passthrough
    RouterAI, `quality` по `usage.cost`, форма SVG, протокол Gen-API, рассуждения против `max_tokens`, ступень `/v2` →
    §5 [не проверено] [поправка фазы 5, 25.09.2026: выполнены все, кроме `/v2` (H-02); итоги — пп. 7, 8, 11, 12, 15, 18, 20 и §6].
25. Не тратить RouterAI и Gen-API на модели, которые в polza дешевле (видео, Nano Banana, Seedream, Kling) — ключи этих
    каналов для Recraft, GPT Image с `quality`/`background`, FLUX.2 с `seed`, удаления фона, слоёв →
    `03-aggregators-and-platforms.md` §2.2, §4 [документация].

## 1. Каналы: что отдают и как

| Канал | Эндпоинт | Режим | Где результат | Срок жизни | Цена в ответе | Ошибки |
|---|---|---|---|---|---|---|
| `routerai` картинки | `POST https://routerai.ru/api/v1/images` | синхронно (GPT Image 2 high — до ≈ 94 с) | `data[].b64_json` + `media_type` | в ответе | `usage.cost`, ₽ | `{error: {code, message}}`; неудача — 502 без списания [S4] |
| `routerai` видео | `POST …/api/v1/videos` → `GET …/videos/{id}` | 202 + опрос | `unsigned_urls` → `…/videos/{id}/content?index=0` **с ключом** | до `expired` | `usage.cost`, ₽ | 429 при > 3 активных |
| `routerai` чат | `POST …/api/v1/chat/completions` | синхронно | `choices[0].message` (`images[]` у диалоговых) | в ответе | `usage.cost` | как у OpenRouter |
| `genapi` | `POST https://api.gen-api.ru/api/v1/networks/{slug}` → `GET …/request/get/{id}` | очередь; `is_sync: true` — в ответе | `result[]` / `full_response[].url` / `output` | файлы 24 ч, результат 14 дней | `cost`, ₽ | 400 `{error: true, errors_validation}`, 401 `{error: "…"}` |
| `polza-chat` | `POST https://polza.ai/api/v1/chat/completions` | синхронно | `choices[0].message.content` | в ответе | `usage.cost_rub` (= `cost`) | `{error: {code, message, trace_id}}` |
| `polza-images` | `POST https://polza.ai/api/v2/images/generations` | синхронно ≤ 120 с, иначе `pending` → `GET /api/v1/media/{id}` | `data[].url` (CDN) или `b64_json` | 7 дней (CDN polza) | `usage.cost_rub` | как polza-chat |

### 1.1. RouterAI: картинки

- Эндпоинт поддерживают модели с `image` в `output_modalities`; диалоговые (выход `text+image`: Gemini image,
  `gpt-5.4-image-2`) — через `/api/v1/chat/completions` с `modalities: ["image", "text"]` и `image_config` [S1].
- Параметры (документация): `model`, `prompt`, `n`, `aspect_ratio`, `resolution` (512/1K/2K/4K), `size` (`WxH`),
  `quality` (auto/low/medium/high; у GPT Image 2.5 в каталоге ещё xhigh, max), `background` (auto/transparent/opaque),
  `output_format` (png/jpeg/webp; svg — только векторные), `output_compression`, `seed`, `input_references`, `mask`,
  `input_fidelity` (только gpt-image-1/-mini; у gpt-image-2 — ошибка `invalid_input_fidelity_model`), `stream` [S1, S4].
- «Набор поддерживаемых параметров зависит от модели. **Неподдерживаемые значения модель игнорирует или нормализует**»
  [S1] → молчаливый отброс виден только по результату (цвет, альфа, цена), не по 400.
- Точный набор модели — в каталоге RouterAI: `supported_parameters`, `supported_aspect_ratios`, `supported_qualities`,
  `supported_backgrounds`, `supported_output_formats`, `max_image_count`, `max_image_references`, `image_seed`,
  `image_pricing[{unit, price}]` [S3]. Клиент проверяет по ним и предупреждает (`mp_client.py show MODEL --channel routerai`).
- Ключевые модели фазы 5 (каталог 23.09 18:37, цены — ₽):

| Модель | Цена | Параметры по каталогу | Замечание |
|---|---|---|---|
| `recraft/recraft-v4.1-vector` | 8,7428 за картинку | aspect_ratio, output_format (`svg`), n ≤ 6, input_references ≤ 1 | passthrough у OpenRouter: `style`, `controls`, `text_layout` [S5] |
| `recraft/recraft-v4.1-pro-vector` | 32,7856 | то же | ×3,75 к обычному |
| `recraft/recraft-v4-styles-vector` | 5,4643 + 0,5464 за референс-стиль | + input_references 1–10 | у OpenRouter: `style_id`, `style_match`, `controls`, `random_seed`; $0,005 за `input_reference` [S5] |
| `recraft/recraft-v4.1`, `-utility`, `recraft-v4-styles` | 3,825 | aspect_ratio, n, input_references | растр |
| `openai/gpt-image-2.5-sunburst` | 0,0032786 за вых. токен | aspect_ratio, quality (до `max`), background (с `transparent`), n ≤ 10, refs ≤ 16, output_compression | **нет `output_format`** в списке; вход: $5/M текст, $8/M картинка (OpenRouter) |
| `openai/gpt-image-2` | 0,0032786 за вых. токен; вход 0,000874 | aspect 1:1, 3:2, 2:3, auto; backgrounds **auto, opaque** (прозрачности нет) | маска — классический inpaint [S1, мнение агрегатора] |
| `black-forest-labs/flux.2-pro` | 3,2786 за Мп | aspect_ratio, output_format png/jpeg, n = 1, refs ≤ 8, **seed** | passthrough у OpenRouter: `steps`, `guidance`, `safety_tolerance`; `disable_pup` нет |

### 1.2. RouterAI: видео

- `POST /api/v1/videos` (`model`, `prompt` обязательны; `duration`, `resolution`, `aspect_ratio`, `size`, `frame_images`,
  `input_references`, `seed`, `generate_audio`, `negative_prompt`, `callback_url`) → **202** `{id, status: "pending",
  polling_url}` → `GET /api/v1/videos/{id}`: `pending` → `in_progress` → `completed` | `failed` | `cancelled` |
  `expired` → скачивание `unsigned_urls` (content-эндпоинт RouterAI, **с тем же ключом**) [S2].
- Провайдерные параметры видео — **в корне тела** (`watermark` у Seedance), у `heygen/avatar-iv` —
  `provider.options.heygen` [S2]. Для картинок такого правила в документации нет (§5, Z2).
- `frame_images[]`: `{"type": "image_url", "image_url": {"url"}, "frame_type": "first_frame" | "last_frame"}`; у Seedance
  2.x `frame_images` и `input_references` взаимоисключающие (400 или молчаливый i2v); продление с `video_url` — без
  `aspect_ratio`/`size` [S2].
- Лимит одновременных задач — 3 (+1 на каждые 1000 ₽ баланса, ≤ 50), превышение — `429 Too many active video
  generations`; клиент ждёт и повторяет POST (429 — единственный повтор POST) [S2; проверено: B2/01 №15].
- Цена — `pricing.seconds` (₽/с) × `duration`, одна на все разрешения; у части моделей `generate_audio` по умолчанию
  true (Wan) — клиент требует `duration` явно и предупреждает про звук [S2, S3].
- Сравнение с polza (4 с, каталоги 23.09): Seedance 1.5 Pro — RouterAI 5,6654 ₽/с × 4 = 22,66 ₽, polza 480p без звука
  5,25 ₽ (×4,3); Grok Imagine Video 1.5 — 8,7428 × 4 = 34,97 против 1,62 × 4 = 6,48 (×5,4); Kling v3 std — 13,77 против
  10 ₽/с (×1,4); Veo 3.1 Fast 8 с — 87,43 против 45 (×1,9) [S3, S13].
- Вебхук (`callback_url`, подпись HMAC-SHA256 от `sha256_hex(api_key)`) требует публичного HTTPS — клиенту не нужен,
  он опрашивает сам [S2].

### 1.3. Gen-API

- Создание: `POST https://api.gen-api.ru/api/v1/networks/{slug}` с `Authorization: Bearer …` → `{request_id, model,
  status: "processing"}`; результат: `GET /api/v1/request/get/{request_id}` → `{id, status, response_type, cost, progress,
  runtime, result[], full_response[], parameters, timestamp}`; статусы `processing` → `success` | `error` [S6].
- `is_sync: true` — ответ приходит после генерации (для быстрых задач); иначе очередь; `callback_url` — вебхук с
  повторами 10 с…24 ч [S6].
- Файлы: вход — base64 data URI, публичный URL или multipart; **ссылки на файлы результата живут 24 ч, полные результаты
  — 14 дней** [S6] (оферта Gen-API ред. 24.04.2026 п. 4.3 — «не более 24 ч», L `../12-legal-provenance/01-licenses-by-vendor-and-channel.md`
  §3 — планировать 24 ч; пометка X 24.09.2026) → клиент скачивает сразу; при истёкшей ссылке — `download ID --channel genapi --live` (повторный GET).
- Каталог сетей — публичный `GET /api/v1/networks?include=parameters` (без ключа, 60 запросов в минуту): 313 сетей 23.09;
  у параметра `title`, `type` (`url_or_file[:ext…]`, `files_array:…`, `RGB`, `RGB_background`, `boolean` c умолчанием
  `"0"`/`"1"`, `integer`, `numeric`, `string`, `url`), `required`, `default`, `items`; у сети `cost` (₽; `null` — зависит
  от параметров), `is_payment_upfront` [S7]. Страница модели `flux-2` показывает ответ `{"status": "starting", "output"}`,
  общая документация — `processing` и `result` → клиент понимает обе формы [S6, S8].
- Сети фазы 5 (каталог 18:37 + прайс P): `flux-2` 3 ₽ за Мп (standard; turbo 2, flash 1,25), `recraft-v4` vector 20 /
  image 10 / vector pro 75 / image pro 62,5, `image-2-svg` 1 ₽ (оплата по факту, `is_payment_upfront: false`),
  `ideogram-remove-background` 2,5, `pixelcut-background-removal` 4 (`output_format` rgba | alpha | zip),
  `qwen-image-layered` 12,5 (`num_layers` по умолчанию 4, `acceleration` regular) [S7, S9].
- OpenAI-совместимый вход Gen-API (`https://proxy.gen-api.ru/v1`) — только для текстовых моделей; клиентом не
  поддерживается (текст — через polza-chat) [S6].

### 1.4. polza-chat и polza-images

- Чат: `POST /api/v1/chat/completions` (`model`, `messages`; картинки — часть `{"type": "image_url", "image_url": {"url"}}`,
  URL или data URI); ответ `usage{prompt_tokens, completion_tokens, cost_rub, cost, completion_tokens_details
  .reasoning_tokens}`; «reasoning tokens учитываются как output tokens для биллинга» [S10].
- Цены — каталог polza `top_provider.pricing` (₽ за 1М токенов): gemini-3.8-flash 44,35 / 221,73; gemini-3.1-flash-lite
  14,78 / 88,69; gemini-3-flash-preview 29,56 / 177,39; gpt-5.6-sol 118,26 / 591,29; claude-sonnet-5 236,52 / 1182,58;
  deepseek-v4.1-flash 13,24 / 39,73 (снимок 17:45; к утреннему +0,2 %) [S13].
- Картинки на входе: Gemini ≈ 258 токенов на плитку 768×768 (F-05: сетка 1940×424 → 774), Gemini 3 с высоким
  `media_resolution` — до 1120 на картинку; Claude ≈ w·h/750; OpenAI 85 + 170 на плитку 512 [документация вендоров; оценка
  клиента, не проверено на polza].
- `/v2/images/generations` (OpenAI-совместимый): `model`, `prompt`, `n` 1–10, `size` (auto, 256², 512², 1024², 1536×1024,
  1024×1536, 1792×1024, 1024×1792), `quality` (auto/low/medium/high/standard/hd), `response_format` url | b64_json,
  `style`, `output_format`, `background`, `output_compression`, `user` — последние четыре только в `openapi.json`
  [S11, S12]. Какие модели отдаются этим путём — поле `endpoints` каталога: 24 картинки 23.09, в том числе
  `openai/gpt-image-2.5-sunburst`, `gpt-5.4-image-2`, `qwen/image-2.1`, `flux.2-pro` [S13].

## 2. Как запускать фазу 5 по каналам

### 2.1. Подготовка (заказчик)

1. Ключи: `mkdir -p ~/.config/routerai && install -m 600 /dev/null ~/.config/routerai/api_key` и вписать ключ (так же
   `genapi`, `polza`); либо
   переменные окружения. Клиент предупреждает, если права шире 600, и никогда не печатает ключ.
2. Лимиты на сессию: `export ROUTERAI_BUDGET_TOTAL=150 GENAPI_BUDGET_TOTAL=120` (по плану N; без них `--live` откажет),
   `POLZA_BUDGET_TOTAL=2000` (общий с `polza.py`), `MP_MAX_JOB=60` (потолок одного задания).
3. Свежие каталоги: `python3 ../../scripts/ai-media/mp_client.py snapshot` → `99-raw/cache/{routerai,genapi}/<дата_время>/`
   (бесплатно, без ключа; клиент берёт последний снимок); для polza — `polza_catalog.py snapshot`.

### 2.2. Порядок

```bash
# mp_client.py 1.0 — [проверено: 99-raw/experiments/B2/01-mock, 02-estimate-all]
T=../../scripts/ai-media/mp_client.py; J=99-raw/phase5/jobs
python3 $T estimate $J/*.routerai.json* $J/*.genapi.json $J/*.polza-chat.json $J/*.polza-images.json --summary
python3 $T run $J/G-16-genapi-image2svg.genapi.json                 # сухой прогон: точный запрос и цена
python3 $T run $J/G-16-genapi-image2svg.genapi.json --live          # зонд Z5 (1 ₽)
python3 $T batch $J/G-07-recraft-icons-controls.routerai.json $J/G-08-recraft-icons-words.routerai.json --live --parallel 2
python3 $T run $J/G-05-llm-svg-repair.polza-chat.json --live --set BEST_MODEL_FROM_G01_G04=google/gemini-3.8-flash \
    --set-file ROUND1_JSON=out/G-02.json --set CHECK_FLAGS="…" --set UNRECOGNIZED="…"
python3 $T ledger --sum                                             # траты по каналам и агентам (+ события polza.py)
python3 $T download <id> --channel genapi --live                    # дожать: истёкшая ссылка, таймаут опроса
```

### 2.3. Команды

| Команда | Что делает | Сеть |
|---|---|---|
| `estimate JOBS… [--summary] [--json] [--pick]` | проверка по каталогам и документации, цена (ожидание и верх), лимиты, кэш | нет |
| `run JOB [--pick TAG\|N\|/re/]` | одно задание: сухой прогон или `--live` | только с `--live` |
| `batch JOBS… [--parallel 2] [--skip-bad]` | серии и несколько файлов, ≤ 3 параллельно; 401/402/403 останавливает канал | только с `--live` |
| `status ID --channel C` | статус: видео RouterAI, задача Gen-API, `/v1/media` polza, история чата | с `--live` |
| `download ID --channel C` | скачать готовый результат, паспорт, закрыть запись журнала | с `--live` |
| `ledger [--sum] [--channel] [--agent]` | общий журнал (включая события `polza.py`, канал `polza-media`) | нет |
| `show MODEL --channel C` | параметры, значения, цены, passthrough модели или сети | нет |
| `snapshot [--channel routerai\|genapi\|all]` | публичные каталоги без ключа в `99-raw/cache/` | публичный GET |
| `selftest` | 36 проверок без сети (формулы, сигнатуры, журнал против `polza.py`) | нет |

Ключевые флаги: `--limit-by high|expected`, `--force` (мимо кэша), `--curl` (печать curl с `$ROUTERAI_API_KEY`),
`--set`/`--set-file` (шаблоны), `--no-auto-cap` (чат без потолка), `--sync-timeout` (синхронные POST), `--poll-interval`,
`--max-wait`, `--no-validate` (отправить вопреки ошибкам проверки — для зондов). Коды выхода — как у `polza.py`: 0, 1
задание, 2 бюджет, 3 таймаут опроса, 4 failed/error/expired, 5 HTTP, 6 скачивание.

## 3. Задание: формат и ловушки по каналам

### 3.1. Общие поля

Формат — `99-raw/phase5/README.md` («Задание вне Media API polza»): `channel`, `method: "POST"`, `path` (`/api/v1/…` или
`/v1/…` — клиент понимает оба), `body` — точное тело по документации, `tag`, `agent`, `variant`, `max_rub`,
`price_rub`, `price_source`, `docs`, `notes` (гипотеза), `meta`. Файл — объект, **массив** (D2-02, D2-10) или `.jsonl`;
`channel` можно вывести из имени файла. Локальные пути в полях файлов — от папки задания; клиент кодирует их в
`data:<mime>;base64,…` (> 4 МБ — предупреждение, > 20 МБ — ошибка: нужен URL).

### 3.2. RouterAI

```json
// recraft/recraft-v4.1-vector · RouterAI 2026-09-23 · [не проверено: passthrough]
{"channel": "routerai", "method": "POST", "path": "/api/v1/images",
 "body": {"model": "recraft/recraft-v4.1-vector", "prompt": "…", "aspect_ratio": "1:1", "n": 1, "output_format": "svg",
          "provider": {"options": {"recraft": {"controls": {"colors": [{"rgb": [15, 23, 42], "weight": 0.5}],
                                                            "background_color": {"rgb": [248, 250, 252]}}}}}},
 "tag": "G-07-…", "agent": "G", "variant": 1, "max_rub": 10.6, "price_rub": 8.74,
 "notes": "passthrough provider.options.recraft.controls у RouterAI не документирован — гипотеза"}
```

```json
// openai/gpt-image-2 правка по маске · RouterAI 2026-09-23 · [документация S1]
{"body": {"model": "openai/gpt-image-2", "prompt": "Remove …", "quality": "medium", "n": 1,
          "input_references": [{"type": "image_url", "image_url": {"url": "../inputs/H/product_1024.png"}}],
          "mask": {"image_url": {"url": "../inputs/H/mask_product_alpha.png"}}}}
```

- `quality` задавать всегда: без него (auto) клиент оценивает по medium, а лимит считает по high.
- `background: "transparent"` — только png/webp; у `gpt-image-2` прозрачности нет (`supported_backgrounds`: auto, opaque).
- Recraft Styles: `style_id` через RouterAI не получить (нет эндпоинта создания стиля) — стиль передаётся картинками
  `input_references` в каждом вызове (+0,55 ₽ за референс-стиль) [S5; F-06, G-11].
- Видео: `duration` явно (цена), `generate_audio` явно, первый/последний кадр — `frame_images` с `frame_type`.

### 3.3. Gen-API

```json
// recraft-v4 vector · Gen-API 2026-09-23 · [документация S7] — все три ловушки заданы явно
{"channel": "genapi", "method": "POST", "path": "/api/v1/networks/recraft-v4",
 "body": {"model": "vector", "pro": false, "translate_input": false, "is_sync": false, "aspect_ratio": "1:1",
          "prompt": "…", "colors": [{"r": 15, "g": 23, "b": 42}], "background_color": {"r": 248, "g": 250, "b": 252}}}
```

- Проверка клиента по каталогу сети: неизвестный параметр — предупреждение (строгость Gen-API к лишним полям не
  документирована), `required` без значения и значение вне `items` — ошибка; `url_or_file` — URL, data URI или путь.
- `translate_input`: если в каталоге сети есть и задание молчит — клиент шлёт `false`; `true` — предупреждение (перевод
  GPT-4.1, отдельная транзакция, переводит и текст надписей — вредно для кириллицы в картинке) [S6].
- `recraft-v4`: `model` и `pro` — ошибка, если не заданы; палитра `colors` — без весов (в отличие от Recraft API) [S7].
- Вход-файл удаления фона и слоёв — data URI (документированный способ 1); multipart клиент не использует.

### 3.4. polza-chat

- Всегда `max_tokens` (потолок цены): без него клиент ставит `floor((max_rub − вход) / цена выхода)` и пишет это в
  сухом прогоне; `--no-auto-cap` — худший случай по `max_completion_tokens` модели (у Gemini 65 536).
- Ответ JSON (`response_format: json_object`) → `.json` (с проверкой валидности), голый SVG → `.svg`, прочее → `.md`;
  `finish_reason: length` — предупреждение «ответ обрезан».
- Параметры вне `supported_parameters` провайдера модели — предупреждение (например, `temperature` у `gpt-5.6-sol` нет).

### 3.5. polza-images и шаблоны

- `/v2`: `size` из перечня OpenAPI; `background`/`output_format` — гипотеза (дойдут ли до `mie`); цена — §4.2.
- Шаблон — строка `{{ИМЯ}}` в теле или «<…>» в поле файла. `--set ИМЯ=значение` подставляет строку, `--set-file` —
  содержимое файла (ответ первого раунда G-05). Пока подстановки нет, `--live` отвечает кодом 1.

## 4. Деньги

### 4.1. Как клиент считает цену

| Канал / единица | Формула клиента | Источник |
|---|---|---|
| RouterAI `image` | `price × n` (+ $0,005 × курс за референс-стиль у V4 Styles) | `image_pricing` каталога, OpenRouter endpoints |
| RouterAI `megapixel` (FLUX.2) | `price × Мп × n`; Мп = `size` / 1 048 576 или тир `resolution` (1K ≈ 1 Мп, верх +10 %) | каталог; BFL: «cost scales with output resolution» [S16] |
| RouterAI `token` (GPT Image) | вых. токены по формуле OpenAI (сетка качества, размер по `aspect_ratio`) × 0,0032786 + вход (текст ≈ символы/4, картинки по vision-формуле) | C1/02 [S14]; каталог; OpenRouter |
| RouterAI видео | `pricing.seconds × duration` | каталог |
| Gen-API | прайс сети (flux-2: 3 ₽ × max(1, Мп), верх — по целым Мп; recraft-v4: по `model` × `pro`) или `cost` каталога | S7, S9 |
| polza-chat, RouterAI чат | вход (текст + картинки) × цена входа; верх = вход + `max_tokens` × max(выход, рассуждения); ожидание = `price_rub` задания | каталог [S13] |
| polza-images | ступень 1K каталога Media API × `n`; верх — запасная ступень `[]` | каталог; отображение `size` → ступень [не проверено] |

Курс RouterAI к OpenRouter — 109,285 ₽/$ по всем моделям (3,825 ₽ / $0,035; 8,7428 / $0,08; 0,0032786 / $0,00003) [S3, S5].

### 4.2. Ожидание, верх и лимиты

- Лимиты (`max_rub` задания ∧ `MP_MAX_JOB` ∧ бюджет канала ∧ `MP_BUDGET_AGENT`) по умолчанию проверяются по **верху**.
  Отказ печатается в сухом прогоне заранее: «ОТКАЗ при --live: …; ожидаемая X ₽ — --limit-by expected».
- `H-02` (`/v2`, GPT Image 2.5): ожидание 4 ₽ (1K), верх 11 ₽ (запасная ступень) > `max_rub` 6 → отказ. Варианты: поднять
  `max_rub` до 11; запустить с `--limit-by expected`; заменить модель на `openai/gpt-5.4-image-2` (запасная ступень 4 ₽;
  W2-3 задаёт тот же вопрос) [документация S13].
- `H-06` (RouterAI `gpt-image-2` medium + маска): 6,47–7,81 ₽ против заявленных 1,5 → отказ при `max_rub` 6; нужно
  `max_rub` ≈ 8 или `quality: "low"` (196 ток. = 0,64 ₽ + вход) — решение агента H/N.

### 4.3. Журнал и общий бюджет

- Один файл `99-raw/experiments/_ledger.jsonl` (`MP_LEDGER` или `POLZA_LEDGER`), события как у `polza.py`: `submit`
  (резерв по верху) → `created` (id) → `completed` (факт `cost_rub`, файлы, паспорт) | `failed` (со `status`: error,
  expired…) | `cancelled` | `timeout` | `unknown` | `http_error` | `cache_hit`; поле `channel` и `client: mp_client`.
- Граница бюджета — `base_url` канала: для polza-chat и polza-images это база `polza.py` (`https://polza.ai/api`), поэтому
  `POLZA_BUDGET_TOTAL` общий в обе стороны: `polza.py` видит траты polza-chat, а `mp_client.py` — траты Media API
  [проверено: B2/01 №36 — `polza.py ledger --sum` показал 312,05 ₽ из событий обоих клиентов].
- Резерв снимается только терминальным событием: `timeout` и `unknown` держат оценку в журнале до `download`/`status`.

### 4.4. Кэш

Хэш — sha256 от `{channel, path, body, variant}`, где data URI заменены sha256 содержимого (локальный путь и тот же
файл base64 дают один хэш). Готовая запись с существующими файлами → `cache_hit`, 0 ₽. Автоподстановки клиента
(`translate_input: false`, потолок `max_tokens`) входят в хэш.

### 4.5. Оценка всех заданий каналов (B2/02, 23.09 19:08)

31 файл, 65 заданий, **0 ошибок** (после 5 правок формата: H-06 `input_references` и `mask` — в объектную форму
документации; гипотеза passthrough дописана в `notes` G-10, G-12 ×2, G-14), 2 шаблона. Ожидание 292,43 ₽: RouterAI 162,40,
Gen-API 106,50, polza-chat 19,53, polza-images 4,00. Таблица по файлам — `99-raw/experiments/B2/02-estimate-all/RESULTS.md`.

## 5. Первые вызовы фазы 5: зонды

| № | Что проверяем | Запрос | ₽ | Критерий | Что меняет |
|---|---|---|---|---|---|
| Z0 | свежие каталоги и цены | `mp_client.py snapshot` | 0 | `estimate` по новым снимкам без ошибок | цены плана N |
| Z1 | доходит ли `provider.options` до Recraft через RouterAI | `phase5/jobs/B2-01-probe-options-controls.routerai.json`: тело G-09 v1 (`recraft-v4.1`, растр) + `provider.options.recraft.controls.colors: "__probe_invalid__"` (неверный тип) | 0 или 3,82 | 400 с упоминанием `controls`/`colors` = доходит (не тарифицируется); 200 = отброшен (картинка годится как G-09 v1) | запускать ли G-07, G-10, G-12, G-14 с `controls` или только словами (G-08) и Gen-API G-15 |
| Z2 | провайдерные параметры в корне тела (как у видео) | `B2-02-probe-root-controls.routerai.json`: то же с `controls` в корне тела | 0 или 3,82 | 400 / 200 | форма `disable_pup` в D2-10 №11 |
| Z3 | доходят ли `quality` и `background` у GPT Image 2.5 | H-03 glass как есть | 1,46 | `usage.cost` ≈ 1,44 (medium применён; 5,76 — high/auto); PNG RGBA с частичной альфой | лимиты `quality`, маршрут `IMG-CUTOUT` |
| Z4 | форма SVG в ответе RouterAI | первый векторный тест (G-08 или G-07) | 8,74 | `data[0].b64_json` с SVG и `media_type: image/svg+xml` (или URL) | ничего в клиенте (понимает обе формы) — запись в базу |
| Z5 | протокол Gen-API | G-16 Image2svg | 1 | `request_id`, статусы, `result[]`, `cost` = 1; повторный GET через час — те же ли ссылки | `download` для истёкших ссылок |
| Z6 | входят ли рассуждения в `max_tokens` у polza | `B2-03-probe-reasoning-cap.polza-chat.json`: `google/gemini-3.8-flash`, `max_tokens: 64`, `reasoning.effort: low`, вопрос на 3 предложения | ≈ 0,015 | `completion_tokens + reasoning_tokens ≤ 64` → входят; больше → нет | верх оценки чатов (+0,08…2,4 ₽ на G-01…G-06) |
| Z7 | ступень `/v2` и прозрачность через `/v2` | H-02 как есть **или** на `gpt-5.4-image-2` | 4–11 или 4 | `usage.cost_rub` = 4 (1K) / 11 (запасная); альфа в PNG | лимит H-02; маршрут прозрачности в polza |

Сумма зондов без Z4 ≈ 6,5–21 ₽; Z3, Z4, Z5, Z7 — это сами тесты H-03, G-07/G-08, G-16, H-02 (без Z4 — 6,5–13,5 ₽),
чистая добавка — Z1, Z2, Z6 (0–7,7 ₽; задания `B2-01…03`, план — `99-raw/phase5/B2-plan.md`). Почему неверный тип, а не
неизвестный `style`: `style` у V4.1 Recraft может молча игнорировать (он для V2/V3), и 200 стал бы двусмысленным; ошибка типа
в `controls.colors` отклоняется валидацией провайдера наверняка. Протокол Media API polza (T1–T8 агента B, фаза 0) эти зонды не повторяют.

## 6. Известные неизвестные

| Вопрос | Что делает клиент сейчас | Чем закрыть |
|---|---|---|
| RouterAI пропускает `provider.options` / параметры в корне для картинок | отправляет как есть; предупреждает; требует гипотезу в `notes` | Z1, Z2 |
| форма SVG у RouterAI (base64 или URL), есть ли `media_type` | понимает `b64_json`, `url`, data URL; тип — по `media_type` или сигнатуре | Z4 |
| id генерации RouterAI для картинок | берёт заголовок `X-Generation-Id` (открыт в CORS routerai.ru), иначе свой uid | первый вызов |
| баланс и лимит ключа RouterAI и Gen-API до траты | предполётной проверки нет (эндпоинты в кэше не описаны) — только бюджет по журналу | документация кабинета |
| Gen-API: возврат `is_payment_upfront` при `error`; свежие ли ссылки при повторном GET | пишет `cost` из ответа как факт; `download` делает повторный GET | Z5 + первая ошибка |
| Gen-API строгость к лишним полям | предупреждение, не ошибка | первый 400 `errors_validation` |
| рассуждения внутри `max_tokens` у провайдеров polza | верх — `max_tokens` × max(выход, рассуждения) + предупреждение о возможной добавке | Z6 |
| ступень цены `/v2` и `background` у `mie` | верх — запасная ступень; `background` — гипотеза | Z7 |
| цена FLUX.2 у RouterAI за Мп: дробная или по целым, считаются ли входные референсы | Мп тира 1K, верх +10 %; предупреждение про референсы | D2-10 первый вызов (`usage.cost`) |
| видео RouterAI: цена одна для 480p–1080p и со звуком | `seconds × duration` | не тратить на видео (дороже polza) |

**Закрыто фазой 5 (25.09.2026)**: `provider.options.recraft.controls` доходит (B2-01, 0 ₽); SVG — `b64_json` с `media_type`
`image/svg+xml` и C2PA в `<metadata>`; строгость Gen-API — 422 `errors_validation` на неверный тип (`data:URI`), на длину `prompt` и
на пустой `negative_prompt`, без списания; рассуждения — сверх `max_tokens`; `/v2` (Z7) и возврат `is_payment_upfront` при `error`
(ошибки фазы 5 — 0 ₽) — не проверены `[проверено]`.

## 7. Устройство клиента и проверка

### 7.1. Виды заданий

`ra-image` (синхронно), `ra-video` (202 + опрос), `ra-chat`, `ga-task` (очередь) / `ga-sync` (`is_sync`), `chat`
(polza-chat), `pz-image` (`/v2`, с переходом в опрос `/v1/media`). Опрос: 4 с картинки, 8 с видео, ±15 % дрожания;
таймауты 900 / 1800 с; синхронный POST ждёт 300 с (RouterAI картинки, чат), 150 с (`/v2`), 330 с (`is_sync`).

### 7.2. Повторы и ошибки

GET — до 5 попыток при 429, 5xx и сетевых сбоях (пауза `Retry-After` или 2 → 30 с). POST — только при 429 (видео RouterAI
— до 7 попыток от 10 с); 4xx/5xx — `http_error`, 0 ₽; обрыв после отправки — `unknown` с резервом; 401/402/403 в серии
останавливают канал. Сбой опроса после создания — `unknown` (резерв), дожать `download`.

### 7.3. Ключи и хосты

Ключ канала читается лениво (только `--live`, только при запросе к своему хосту) и регистрируется как секрет: все
выводы, журнал и паспорта проходят замену на `***`. `Authorization` добавляется как «unredirected» заголовок только при
совпадении origin с базой канала: CDN Gen-API и polza, чужие `url` в ответе RouterAI получают запрос без ключа;
content-эндпоинт видео RouterAI — с ключом. Файлы ключей в сухом прогоне не открываются (печатается только «есть/нет»
и права).

### 7.4. Файлы и паспорт

Скачивание — атомарно через `.part`, sha256, тип по сигнатуре (PNG, JPEG, WebP, AVIF, GIF, SVG, MP4, WebM, MOV, ZIP,
JSON). Паспорт `mp-passport/1`: канал, вид, uid, хэш, задание (tag, agent, notes, meta, price_rub, max_rub, файл и номер),
модель, промт, запрос (base64 сокращён до длины и sha256), ответы создания и финальный, оценка с формулой и
предупреждениями, входные файлы (sha256, размеры), время, `cost` (факт, ожидание, лимит, разница), файлы с разбором:
SVG — корень, `viewBox`, пути, цвета (до 16), `<text>`/`<image>`, подпись Recraft; PNG — режим, `alpha_used`; видео —
ffprobe; JSON — валидность.

### 7.5. Проверка на макете (B2/01)

Четыре локальных сервера (RouterAI, Gen-API, polza, CDN) по документации из кэша; 44 сценария за 47 с: сухой прогон,
SVG и PNG RouterAI, `url`-ответ без ключа, 429/500/обрыв, пустой `data`, зонд passthrough (400 → 0 ₽), V4 Styles с
локальным референсом, видео 202 → content с ключом, 429 активных задач, `expired`, таймаут и `download`, кадры
first/last, Gen-API очередь / `is_sync` / `error` / истёкшая ссылка / 400 `errors_validation`, `translate_input` явно,
polza-chat JSON / SVG / картинка base64 / 402, `/v2` sync / pending / b64, бюджеты (0 по умолчанию, лимит H-06, общий
с `polza.py`), параллельность 2 и 3, 401 со стопом серии, `status`, 12 настоящих файлов фазы 5 одной серией, утечки ключей
— 0 [проверено].

## Частые ошибки

- Считать `usage.cost` RouterAI долларами (как у OpenRouter): у RouterAI это **рубли**; у Gen-API `cost` — рубли, у polza
  — `cost_rub`.
- Передавать `input_references` строками или локальными путями без кодирования: документированная форма — объекты
  `image_url`, файл — data URI.
- Слать `mask` без `input_references` или модели не `gpt-image-*` — маска молча игнорируется.
- Ждать 400 на неподдерживаемый параметр RouterAI: он «игнорирует или нормализует» — проверять результат и `usage.cost`.
- Переносить сетку качества GPT Image 2.5 на GPT Image 2 (medium у 2 = high у 2.5 по токенам; цена ×4) — ошибка H-06.
- Оставлять Gen-API умолчания: `translate_input: true` (платный перевод и порча кириллицы), `pro: true` у Recraft (75 ₽),
  `model: image` вместо `vector`.
- Верить странице модели Gen-API больше, чем каталогу `networks?include=parameters` (разные статусы, поля, умолчания).
- Запускать видео через RouterAI «потому что есть ключ»: те же модели в polza в 1,4–5,4 раза дешевле.
- Чат без `max_tokens`: у Gemini потолок 65 536 токенов (до 14,5 ₽ за ответ у gemini-3.8-flash).
- Скачивать ссылки Gen-API «потом»: файлы живут 24 ч.
- Подставлять `{{ИМЯ}}` руками в общий файл задания — `--set` и `--set-file` не трогают файл и видны в паспорте.
- Ошибки агентов-нейросетей: брать `style_id` у RouterAI (эндпоинта создания стиля нет), путать `/v1/images/generations`
  и `/v2/images/generations` polza (документирован `/v2`), слать ключ в URL CDN, повторять POST при 500.

## Чек-лист

- Заданы ли `ROUTERAI_BUDGET_TOTAL` и `GENAPI_BUDGET_TOTAL` на эту сессию, а `POLZA_BUDGET_TOTAL` учитывает траты `polza.py`?
- Свежие ли снимки каталогов (`snapshot` сегодня) и даёт ли `estimate` 0 ошибок по всем файлам?
- В каждом задании есть `max_rub`, `price_rub`, гипотеза в `notes`, а ценовые параметры (`quality`, `duration`, `pro`,
  `model`, `max_tokens`) заданы явно?
- Нет ли в сухом прогоне строки «ОТКАЗ при --live» — и если есть, решено ли, поднимать `max_rub` или нет?
- Пройдены ли зонды Z1, Z2 до серий с `controls`, а Z6 — до чатов G-01…G-05?
- Шаблоны (G-05, D2-03) заполнены `--set` / `--set-file`?
- После серии: `ledger --sum` сходится с балансом каналов, файлы и паспорта на месте, нет записей `timeout`/`unknown`?

## Открытые вопросы и противоречия

- Документация RouterAI: `output_format` — png/jpeg/webp; каталог RouterAI и OpenRouter — `svg` у векторных Recraft
  [S1 против S3, S4]. Клиент принимает `svg` (без предупреждения только у моделей с `supported_output_formats: ["svg"]`).
- RouterAI «неподдерживаемые значения игнорирует или нормализует» [S1]; OpenRouter — `size` + несовпадающие
  `resolution`/`aspect_ratio` → 400 [S4]. Какое поведение у витрины — неизвестно.
- Gen-API: общая документация — статусы `processing/success/error` и поле `result` [S6]; страница модели — `starting` и
  `output` [S8]; пример ответа в документации показывает `translate_input: true` у flux-2, каталог — умолчание 0 [S6, S7].
- polza `/v2`: mdx без `background`/`output_format`/`n` [S11], `openapi.json` — с ними [S12]; описание ответа 200 в
  OpenAPI предлагает опрос `GET /v2/media/{id}`, путь в схеме только `/v1/media/{id}` — клиент опрашивает `/v1`.
- P: «V4 Styles vector 5,46 ₽ с `style_id`» (`03` §2.2, `06` стр. 13) — у RouterAI нет эндпоинта создания стиля, `style_id`
  получить нельзя; серия держится только референсами в каждом вызове (F-06, G-11) [S3, S5].
- `H-02` notes: «в документации `/v2` нет `background` и `output_format`» — верно для mdx, неверно для OpenAPI; гипотеза
  сужается до «доходит ли до GPT Image 2.5 у `mie`».
- Цена RouterAI видео — одно число за секунду [S3]; соответствует ли оно 480p без звука или максимуму — неизвестно.
- Токены входных картинок GPT Image 2 («всегда high fidelity») и маски — оценка клиента ×2 без источника [не проверено].

## Источники

- [S1] RouterAI. «Генерация изображений» — https://routerai.ru/docs/guides/overview/multimodal/image-generation, снято
  23.09.2026 09:32, `99-raw/cache/routerai.ru_docs_guides_overview_multimodal_image-generation_753f42c7.md` — эндпоинт,
  параметры, формат ответа (cost в ₽), маска; первоисточник, целиком.
- [S2] RouterAI. «Генерация видео» — …/video-generation, снято 23.09.2026, `…video-generation_56f99671.md` (920 строк) —
  жизненный цикл, статусы, content с ключом, лимит 3, вебхук; целиком шаги 1–4, таблица моделей — выборочно.
- [S3] RouterAI. Публичный каталог `GET https://routerai.ru/api/v1/models` — снимок 23.09.2026 18:37,
  `99-raw/cache/routerai/2026-09-23_1837/` (517 моделей; сверка с выгрузкой P 09:34 — цены использованных моделей те же).
- [S4] OpenRouter. «Image Generation» — https://openrouter.ai/docs/guides/overview/multimodal/image-generation, снято
  23.09.2026, `99-raw/cache/openrouter-2026-09-23/docs_guides_overview_multimodal_image-generation.md` — `media_type`,
  SVG, `provider.options`, биллинг «всё или ничего»; витрина-клон повторяет не всё.
- [S5] OpenRouter. Эндпоинты моделей `/api/v1/images/models/<id>/endpoints` — 16 файлов
  `99-raw/cache/openrouter-2026-09-23/img_endpoints/` — `allowed_passthrough_parameters`, строки цены.
- [S6] Gen-API. Документация: quick-start, generation, queue, synchronous-requests, translating-parameters, webhooks,
  working-with-files, getting-the-result, ai-request, networks-list, openai-format — https://gen-api.ru/docs/…, снято
  23.09.2026 (`99-raw/cache/gen-api.ru_docs_*`), целиком.
- [S7] Gen-API. Публичный каталог `GET https://api.gen-api.ru/api/v1/networks?include=parameters` — снимок 23.09.2026
  18:37, `99-raw/cache/genapi/2026-09-23_1837/` (313 сетей) — параметры, умолчания, цены.
- [S8] Gen-API. «Flux 2 API» — https://gen-api.ru/model/flux-2/api, `…flux-2_api_51030861_r.md` — пример ответа
  `starting`/`output`.
- [S9] Агент P. Прайс Gen-API 23.09.2026 — `../../scripts/ai-media/data/genapi_prices_2026-09-23.json`.
- [S10] polza. `api-reference/chat/completions.mdx`, `osobennosti/reasoning-tokens.mdx`, `osobennosti/usage.mdx` —
  `99-raw/cache/polza/2026-09-23/docs-repo/`.
- [S11] polza. `api-reference/images/generations.mdx` — `/v2`, 120 с, переход в `pending`.
- [S12] polza. `openapi.json` (снимок 23.09.2026) — схема `/v2/images/generations` с `background`, `output_format`, `n`.
- [S13] polza. Каталог `GET /api/v1/models` — снимок 23.09.2026 17:45 (`99-raw/cache/polza/2026-09-23_1745/`).
- [S14] Агент C1. Порт калькулятора токенов GPT Image OpenAI — `99-raw/experiments/C1/02-gpt-image-token-cost/`
  (сверка с опубликованной таблицей OpenAI до цента).
- [S15] Агент B. `../../scripts/ai-media/polza.py` и макет `99-raw/experiments/B/01-mock-server` — образец клиента, журнала, паспорта.
- [S16] Black Forest Labs. Pricing — https://docs.bfl.ml/quick_start/pricing, кэш `docs.bfl.ml_quick_start_pricing_1ebd4076.md`
  — цена FLUX.2 за мегапиксель.
- Смежные файлы базы: `03-aggregators-and-platforms.md` §2.2–§2.3, §4 (что брать в каналах, цены); `06-gap-map.md`
  (рейтинг ключей); `01-polza-api.md` §5, §12–§13 (`/v2`, клиент `polza.py`, фаза 0); `99-raw/phase5/README.md` (формат).
