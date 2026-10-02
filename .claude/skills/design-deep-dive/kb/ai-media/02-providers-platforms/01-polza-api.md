# polza.ai как рабочая среда: Media API, файлы, деньги, клиент `polza.py`

Волна 1 · агент B · 2026-09-23 · прочитано целиком ≈ 80 источников (документация polza `docs-repo` 67 файлов от
18.09.2026, публичная OpenAPI 1.0, 3 выгрузки каталога, 9 страниц документации KIE, прайсы Google, OpenAI, OpenRouter,
KIE, курс ЦБ) · опытов 5 (`99-raw/experiments/B/01…05`) · снимки каталога polza `2026-09-23` (08:20 МСК) и
`2026-09-23_0921` · **ни одного платного вызова: всё про живое поведение — `[не проверено]` до фазы 5.**

Соседние файлы: параметры и цены всех 44 медиа-моделей — [`02-polza-models-params-prices.md`](02-polza-models-params-prices.md);
другие провайдеры и где дешевле — файлы агента P в этой папке; утилиты — `../../scripts/ai-media/README.md` §polza.

## Выжимка для агента

1. **Генерация = `POST https://polza.ai/api/v1/media` → `GET /v1/media/{id}` до `completed` → скачать URL из
   ответа сразу.** Всегда шли `"async": true` явно: в OpenAPI `async` по умолчанию `false` (синхронное ожидание до
   120 с). → §2.2 `[документация]`
2. **Не делай вызовов руками — только `../../scripts/ai-media/polza.py`**: сухой прогон по умолчанию, трата только с `--live`,
   проверка по каталогу, оценка цены, журнал, кэш, паспорт. → §12 `[проверено]`
3. **Параметры бери из каталога модели (`parameters` в `GET /v1/models`), а не из OpenAPI `ImageInputDto`/`VideoInputDto`**:
   спека — устаревший «суперсет» без `mask_url`, `background`, `fixed_lens`, `seeds`, `generationType`,
   `negative_prompt`. → §2.5 `[документация]`
4. **Значения — в представлении каталога**: булевы у видео строками `"true"`/`"false"` (Seedance, Kling, Wan, Veo
   `enableTranslation`), `duration` строкой (`"5"`), `seed`/`seeds` числом. OpenAPI местами ждёт boolean — спорно. →
   §2.5 `[документация]` `[спорно]` [поправка фазы 5, 25.09.2026: T4 — строки `"true"`/`"false"` у Seedance 1.5 Pro приняты, ступень без
   звука 5,25 ₽, дорожки нет → `[проверено]`]
5. **Задавай явно все параметры, от которых зависит цена** (разрешение, длительность, звук, режим): при пропуске
   polza может взять запасную ступень `[]` — у 13 моделей это максимум (Seedance 1.5 Pro 135 ₽ вместо 5,25). → §8.2
   `[не проверено]` [поправка фазы 5, 25.09.2026: T8 — Sunburst без `image_resolution` взял ступень каталога 1K 4 ₽, не запасную 11; проверена
   одна модель, правило «явно» в силе]
6. **Seedance 2 / Fast / Mini: `duration` по умолчанию 15 с и `generate_audio` по умолчанию `"true"`** — запрос
   «только промт» у Seedance 2 стоит 415,125 ₽. → §8.2, файл 02 §3 `[проверено: расчёт B/02]`
7. **Результаты живут 7 дней (`TEMP_GENERATION`)** на CDN polza — скачивай в момент `completed`, храни у себя;
   ссылка из `data` — не архив. → §7 `[документация]`
8. **Не повторяй `POST /v1/media` после таймаута сети или 5xx** — генерация могла создаться, повтор = второе
   списание. Повтор безопасен только при 429 (запрос отклонён). → §9.3 `[практика]` `[проверено: макет B/01]` [поправка фазы 5, 25.09.2026: правило
   сработало вживую — 12 обрывов сети на POST к polza (из 17 по трём каналам) разрешены по `GET /v1/history/generations`: не
   созданы → запись `NETWORK_RESOLVED` и повтор, двойных списаний 0 → `99-raw/phase5/runs/README.md`]
9. **Опрос: картинки раз в 3–5 с, видео раз в 5–10 с**; общий таймаут платформы 600 с; видео Veo 4K-апскейл —
   5–10 мин. → §3.2 `[документация]`
10. **Разбирай результат из трёх форм**: `data.url` (объект), `data[].url` (массив, Lyria), `output.url` (гайд Nano
    Banana 2); плюс `warnings[]` и `content` (текст модели). → §3.3 `[документация]`
11. **Цена факта — `usage.cost_rub` в ответе `completed`** («готовая стоимость, уже списанная»); сверяй с оценкой
    каталога, журнал ведёт `polza.py`. → §8.1 `[документация]`
12. **Баланс — `GET /v2/balance`, поле `available`** (остаток минус резерв под идущие генерации, не больше лимитов
    ключа); v1 для ключа участника показывает остаток личного лимита. → §8.3 `[документация]`
13. **Ключ с лимитом расходов заводит заказчик в консоли** (лимит на ключ day/week/month, белый список моделей
    `modelAccessMode: allow`) — второй предохранитель к лимитам клиента; `GET /v1/key` показывает остаток. → §8.4
    `[документация]`
14. **Алиасы `model@provider=…` для медиа не работают** (`aliases.mdx`: только chat, responses, messages); выбор
    провайдера в Media API — объект `provider` в теле (`only`, `order`, `allow_fallbacks: false`), работает ли —
    `[не проверено]`. → §10 `[документация]` `[спорно]` [поправка фазы 5, 25.09.2026: T5 — `provider: {only: ["google-ai-studio"]}` работает: NB2 Lite
    через Google AI Studio 4,06 ₽ против 2,90 у `mie`, в паспорте `provider_actual` — Google AI Studio]
15. **У одной модели параметры и цена зависят от провайдера**: `openai/gpt-5-image` у `mie` — маска и 4,50 ₽, у
    `openai` — без маски, токены; Nano Banana Pro у `google-vertex/global/flex` ≈ 7,93 ₽ против 13,50 у `mie`. → §10.3
    `[документация]`
16. **Файлы на вход — `{"type": "url"|"base64", "data": …}`**; локальный файл до ~4 МБ — base64, больше — сначала
    `POST /v1/storage/upload` (`TEMP_UPLOAD` 24 ч) и URL. → §2.4, §6 `[документация]`
17. **Все 44 медиа-модели: `is_fz152_compliant=false`, `stores_data_in_russia=false`,
    `is_hosted_on_polza_infrastructure=false`** — фото клиента и людей не загружай без согласия заказчика. → §11
    `[документация]`
18. **У 37 из 44 медиа-моделей (21 картинка, 16 видео) исполнитель `mie` ≈ KIE.ai** (улики в каталоге, OpenAPI и ценах;
    хранение у KIE 14 дней, лимит 20 задач/10 с) — его ограничения переносятся на polza. → §11.3 `[документация]` `[спорно]`
19. **`is_moderated=false` у всех медиа-моделей не значит «без фильтров»**: провайдер (KIE/Google/OpenAI) может
    отклонить запрос (`failed`, `metadata.raw`). → §11.2 `[не проверено]`
20. **Операции только у Veo 3.1**: `extend` 45 ₽ (асинхронно, новый id), `upscale_1080p` 10 ₽ (синхронно),
    `upscale_4k` 90 ₽ (асинхронно по каталогу, «синхронная» по документации). → §4 `[документация]` `[спорно]`
21. **Каталог меняется внутри дня** (23.09 08:20 → 09:21 сменился провайдер и цена у текстовой модели) — перед серией
    `polza_catalog.py snapshot` + `diff`. → §12.6 `[проверено]`
22. **Лимит частоты публичного каталога — 30 запросов на окно 1 с** (`x-ratelimit-*`); лимиты `/v1/media` не
    описаны — клиент держит не больше 3 генераций параллельно. → §9.4 `[проверено: заголовки 23.09]`
23. **Первый живой вызов — по плану §13 (≈ 16 ₽)**: Z-Image, Qwen 2.1 с прозрачностью, Grok Video 1 с, Seedance 1.5
    Pro со строковыми булевыми, провайдер Google у Nano Banana 2 Lite, заведомо неверный запрос. → §13 `[не проверено]`
    [поправка фазы 5, 25.09.2026: выполнено 25.09 09:07–09:50 (T0–T8 и B2-03 — 20,76 ₽): всё сошлось с каталогом; итоги — §13; лишние поля
    списываются (T7), рассуждения чата биллятся сверх `max_tokens` → `99-raw/experiments/_polza/phase5/2026-09-25/`]

## 1. Карта API

### 1.1 База, авторизация, ключ

- База: `https://polza.ai/api`, пути — `/v1/…`, `/v2/…` (полный URL `https://polza.ai/api/v1/media`) [S1]. В
  `osobennosti/reasoning-tokens.mdx` встречается другой хост `https://api.polza.ai/v1/models/<id>` [S28] — клиент
  его не использует `[не проверено]`.
- Авторизация: `Authorization: Bearer <ключ>`; ключи вида `pza_…`, маска в ответах `pza_abc1••••xyz789` [S1][S7][S19].
  Ключ показывается один раз при создании в `polza.ai/dashboard/api-keys` [S16].
- Ключ в проекте: только `~/.config/polza/api_key` (права 600) или `POLZA_API_KEY`; не в заданиях, заметках, чате
  (решение заказчика 23.09.2026). `polza.py` маскирует его в выводе, журнале и паспортах.
- MCP-сервер polza — только аккаунт: профиль, организации, ключи, биллинг, история («метаданные генераций, без
  промптов»); генерации через него нет. Скоуп `billing.danger` — «списание с карты без подтверждения»: агенту не
  выдавать [S16].
- Публично, без ключа: `GET /v1/models`, `GET /v1/models/catalog`, `GET /v1/models/{id}`, спецификация
  `https://polza.ai/api/openapi.json` (OpenAPI 3.0.0, `info.version` 1.0, `cache-control: public, max-age=3600`) [S19][S20].

### 1.2 Эндпоинты для медиа

| Метод и путь | Назначение | Режим | Деньги |
|---|---|---|---|
| `POST /v1/media` | создать генерацию картинки/видео/музыки | `async: true` → сразу `{id, status: "pending"}`; `false` (по умолчанию в OpenAPI) — ждать | по каталогу модели |
| `GET /v1/media/{id}` | статус и результат | опрос | 0 |
| `POST /v1/media/{id}/operations` | `extend`, `upscale_1080p`, `upscale_4k` над готовым видео (только Veo 3.1) | по операции | 45 / 10 / 90 ₽ |
| `POST /v1/media/nanobanano-2` | отдельный путь только для `google/gemini-3.1-flash-image-preview` | как `/v1/media` | как NB2 |
| `POST /v2/images/generations` | OpenAI-совместимая генерация картинок | синхронно до 120 с, дольше — `pending` + опрос | по каталогу |
| `POST /v1/images/generations`, `/v1/videos/generations`, `/v1/videos/extend`, `/v1/upscale/generations` | устаревшие (legacy) пути без схем в спеке | — | — |
| `POST /v1/storage/upload` | загрузить файл (multipart или base64 JSON) | синхронно | 0 (место в хранилище) |
| `GET /v1/storage/files`, `GET/DELETE /v1/storage/files/{id}`, `PATCH /v1/storage/files/{id}/keep` | список, файл, удаление, перевод в постоянное хранение | синхронно | 0 |
| `GET /v1/history/generations[/{id}[/log\|/children]]` | история: провайдер, `clientCost`, попытки | синхронно | 0 |
| `GET /v2/balance`, `GET /v1/balance`, `GET /v1/key` | баланс, резерв, лимиты ключа | синхронно | 0 |
| `GET /v1/models[?type=&include_providers=true]`, `/v1/models/catalog`, `/v1/models/{id}` | каталог (публичный) | синхронно | 0 |

Источник: OpenAPI (58 путей) [S19], `api-reference/*` [S1–S9]. В каталоге у всех картинок поле `endpoints` —
`/api/v1/media` и `/api/v1/images/generations` (v1, не v2), у всех видео — `/api/v1/media` и
`/api/v1/media/:id/operations`, хотя операции есть только у Veo [S20].

## 2. Создание генерации: `POST /v1/media`

### 2.1 Тело запроса

| Поле | Тип | Смысл | Источник |
|---|---|---|---|
| `model` | string, обязательно | id из каталога (`google/veo3_fast`, `gpt-image-2-5-flare` — без префикса у части моделей) | [S2][S20] |
| `input` | object, обязательно | параметры модели — **только из `parameters` каталога этой модели/провайдера** | [S2][S20] |
| `async` | boolean, по умолчанию `false` | `true` — сразу id для опроса | [S19] |
| `provider` | object | маршрутизация: `order`, `only`, `ignore`, `sort`, `max_price`, `allow_fallbacks`, `require_parameters` | [S19][S11] |
| `user` | string | id конечного пользователя (антиабьюз) | [S2][S19] |
| `callBackUrl` | string | URL уведомления о завершении: гайд Lyria — на верхнем уровне тела; OpenAPI — внутри `input` (`ImageInputDto`, `VideoInputDto`, `MusicInputDto`); `polza.py` колбэки не использует | [S18][S19] |

```json
// POST https://polza.ai/api/v1/media · tongyi-mai/z-image · polza 2026-09-23 · [не проверено]
{
  "model": "tongyi-mai/z-image",
  "input": {"prompt": "soft morning light over a misty lake, film grain", "aspect_ratio": "16:9"},
  "async": true
}
```

Ответ 200 (не 201, как в `introduction.mdx` [S1]; в OpenAPI у `POST /v1/media` успешный код 200 [S19]):

```json
{"id": "aig_abc123", "object": "media.generation", "status": "pending", "created": 1703001234, "model": "tongyi-mai/z-image"}
```

Префикс id: `aig_` в `media/create.mdx` и `status.mdx` [S2][S3]; `gen_…` в примере OpenAPI `MediaStatusPresenter`,
у Lyria и в истории [S19][S18][S7] — клиент не полагается на префикс. [поправка фазы 5, 25.09.2026: живые id — `gen_…` (T1), история
`/v1/history/generations` принимает их]

### 2.2 `async`: всегда `true`

- OpenAPI `MediaRequestDto.async`: `default: false`, «При true возвращается taskId для опроса статуса» [S19].
- `media/operations.mdx`: «`async: false` (по умолчанию) — ждёт до 120 с» [S4]; Lyria — по умолчанию синхронно [S18];
  гайд Gemini Omni Video — «по умолчанию true» и «обязателен для всех запросов» [S18] — противоречие со спекой.
- Все cURL в гайдах медиа-моделей шлют `"async": true` [S18].
- Changelog: «Исправлен возврат средств при разрыве соединения» (v1.4.1, v1.4.7) [S14] — синхронное ожидание
  по одному соединению рискованнее. Вывод: **`"async": true` в каждом запросе** (так делает `polza.py`).

### 2.3 Проверка перед отправкой

`polza.py` до отправки: приводит типы к каталогу, явно подставляет default ценовых и обязательных параметров,
проверяет `values`, `min`/`max`, `max_length`, число файлов, перекрёстные правила из описаний (1:1 без 4K у GPT Image
2.5; прозрачность только png/webp у Qwen 2.1; квота файлов Gemini Omni) — 51 ловушка
`[проверено]`. Сервер polza, по гайду Lyria, отвечает 400 на лишние
параметры [S18]; строгость у других моделей неизвестна (гайд Seedance 2 шлёт `multi_shots`, которого нет в
каталоге Seedance 2) `[спорно]`. [поправка фазы 5, 25.09.2026: T7 — Z-Image с лишним `negative_prompt` принят и **списан** (1,40 ₽), ошибки нет →
лишнее поле — трата без эффекта, клиент по-прежнему отказывает до отправки; неверное значение (`aspect_ratio: "21:9"` у
Z-Image, T6) — 400 `BAD_REQUEST` без списания]

### 2.4 Файлы на вход

- Формат OpenAPI `MediaFileDto`: `{"type": "url" | "base64", "data": "<URL или base64>"}`, оба поля обязательны [S19].
- base64 — с data URI (`data:image/png;base64,…`) или без; «если провайдер не поддерживает base64 напрямую, файл
  автоматически загружается в хранилище и передаётся как URL» [S2].
- Гайды Kling Motion Control 3.0/2.6 и GPT-5.4 Image 2 показывают массив строк-URL (`"images": ["https://…"]`) [S18] —
  не по спеке; клиент шлёт объекты `[не проверено: принимаются ли строки]`.
- Лимиты: файл 50 МБ, картинка в хранилище 50 МБ [S1]. Хранилище принимает только изображения, видео и аудио;
  «для файлов больше нескольких МБ загружайте их в хранилище» [S17]. Тело запроса слишком большое → 413
  `PAYLOAD_TOO_LARGE` [S19] (порог не опубликован).
- Политика `polza.py`: локальный файл ≤ 4 МБ → base64 в теле; больше → `POST /v1/storage/upload` (`TEMP_UPLOAD`,
  24 ч) и `{"type": "url"}`; длина локального видео берётся `ffprobe` для оценки цены (Motion Control, Topaz Video,
  Seedance 2.5 `duration: -1`) `[проверено: B/01, сценарии 18a/18b]`.
- Чужие URL (не polza) как вход — только публичные и долгоживущие: исполнитель (KIE) скачивает их сам; ссылки
  загрузок KIE живут 24 ч, ссылки скачивания KIE — 20 минут [S21].

### 2.5 Типы значений: каталог против OpenAPI

| Параметр | Каталог (`values`/`default`) | Гайды | OpenAPI | `polza.py` шлёт |
|---|---|---|---|---|
| `generate_audio`, `sound`, `fixed_lens`, `multi_shots`, `enable_prompt_expansion`, `enableTranslation` | `["true","false"]`, default `"false"`/`"true"` строкой | `"false"` строкой | `boolean` (для `generate_audio`: «строки "true"/"false" приводятся к boolean»); `fixed_lens`, `enableTranslation` в DTO нет | строку из `values` |
| `duration` | Seedance 1.5 Pro, Wan, Kling 2.6, Omni, Wan 3.0 — строки в `values`; Seedance 2/2.5, Grok, Kling 3 — `min`/`max`, default числом | `"10"`, `"8"` строкой | `string` | строку |
| `seed`, `seeds` | `min`/`max` | `42`, `12345` числом | `number` (`seeds` в DTO нет) | число |
| `strength`, `guidance_scale` (Qwen Image) | `min`/`max`, default `0.8`, `2.5` числом | `"0.8"`, `"2.5"` строкой | `number` | число |
| `upscale_factor` | `["1","2","4","8"]` | `"8"` строкой | `string` enum | строку |
| `enhance_prompt` (Qwen 2.1) | default `false` (boolean) | — | в DTO нет | boolean |
| `isEnhance` (GPT-5 Image) | default `"false"` (строка) | — | `boolean` | строку |
| `output_format` | `png`/`jpeg`/`webp` | — | «jpg автоматически → jpeg» | из `values` |

Спека `ImageInputDto`/`VideoInputDto` — «общий superset провайдеров; конкретная модель принимает своё подмножество,
оно проверяется по каталогу модели» (описание `image_resolution` и `resolution` в OpenAPI) [S19]. Поля каталога,
которых нет в DTO: `mask_url`, `background`, `enhance_prompt`, `n`, `fixed_lens`, `negative_prompt`,
`enable_prompt_expansion`, `generationType`, `enableTranslation`, `seeds` — если polza валидирует тело по DTO со
строгим белым списком, они вернут 400 `[не проверено]` → план §13, тест T3.

## 3. Опрос и результат: `GET /v1/media/{id}`

### 3.1 Статусы

`pending` → `processing` → `completed` | `failed` | `cancelled` [S3][S19]. `cancelled` описан у Lyria и в enum
OpenAPI [S18][S19]; changelog v1.4.9 (22.04.2026): «Исправлены неправильные списания при отмене генерации» [S14]
(эндпоинта отмены в спеке нет).

### 3.2 Частота и таймауты

- Документация: картинки — раз в 3–5 с, видео — раз в 5–10 с; пример опроса `interval=5`, `max_wait=300` [S3].
- Общий таймаут платформы — 600 с [S1]; `/v2/images/generations` и синхронные операции — 120 с [S5][S4].
- KIE: 4K-апскейл Veo — 5–10 минут, `extend` — «от нескольких минут до десяти с лишним» [S21].
- `polza.py`: 4 с для картинок, 8 с для видео (±15 % разброса), потолок 600 с / 1800 с (`--max-wait`); при
  таймауте — код выхода 3 и запись `timeout` в журнале, дожать — `polza.py download <id> --live`
  `[проверено: B/01, сценарий 08]`.

### 3.3 Формы ответа `completed`

```json
// status.mdx [S3] — одна картинка
{"id": "aig_abc123", "object": "media.generation", "status": "completed", "created": 1703001234,
 "model": "google/gemini-2.5-flash-image", "completed_at": 1703001244,
 "data": {"url": "https://s3.polza.ai/f/205141/2026/03/aig_abc123.jpg"},
 "usage": {"output_units": 1, "cost_rub": 5.00, "cost": 5.00}}
```

| Форма | Где описана | Разбор в `polza.py` |
|---|---|---|
| `data: {url}` | `status.mdx` [S3] | да |
| `data: [{url, thumbnail_url, title, duration}]` | `google-lyria-3.mdx` [S18] | да (миниатюры отдельно) |
| `output: {url}` | `nanobanano-2.mdx`: «URL результата в поле `output.url`» [S18] | да |
| несколько файлов (`n` у GPT-5.4 Image 2, 1–4) | гайд [S18]; форма не описана | да (все `url` по порядку, файлы `_1`, `_2`) |

Схемы `MediaImageDataPresenter`/`MediaVideoDataPresenter` в спеке объявлены, но отсутствуют [S19]. Прочие поля
`MediaStatusPresenter`: `usage` (`input_units`, `output_units`, `duration_seconds`, токены, `cost_rub`, `cost`),
`error`, `content` («текстовый ответ модели, если вернула текст вместо/вместе с изображением»),
`reasoning_summary`, `warnings[]` (пример: «Параметр isEnhance не поддерживается OpenRouter и будет
проигнорирован») [S19]. Разбор всех форм — `[проверено: B/01, сценарии 12a–c]` на макете; настоящие формы у каждой
модели — `[не проверено]`.

### 3.4 Ошибка в `failed`

`error: {code, message, metadata}`; `code` — `FORBIDDEN`, `BAD_GATEWAY`, `REQUEST_TIMEOUT` и др.; `message` на
русском; `metadata` — «исходное сообщение провайдера (raw) и его имя», пример `{"raw": "content policy violation",
"provider_name": "kie"}` [S19]. Для STT при опросе просроченного результата описан код `RESULT_EXPIRED` [S27] —
вероятно, он же для медиа после 7 дней `[не проверено]`. Списывается ли что-то за `failed` — смотреть
`usage.cost_rub` и `attempts[].wasBilled` в истории (§8.5); в макете — 0 ₽.

## 4. Операции над видео: `POST /v1/media/{id}/operations`

Есть только у `google/veo3` (Quality) и `google/veo3_fast` (Fast) — поле `operations` каталога [S20].

| Операция | Каталог: `async`, цена | Параметры (каталог) | Документация [S4] | KIE (исполнитель) [S21] |
|---|---|---|---|---|
| `extend` | `true`, **45 ₽** у обеих моделей | `prompt` (обяз., ≤ 16 000), `seeds` 10000–99999, `watermark` ≤ 50, `model`: `fast`\|`quality` (default: `quality` у `google/veo3`, `fast` у `google/veo3_fast`) | асинхронная, «создаёт новую генерацию с новым ID»; параметры в тексте: `prompt`, `seeds`, `duration` 3–10 с | только для видео Veo 3.1 API; «Videos generated in 1080P cannot be extended»; от минут до 10+ мин; Extend Quality — 250 кредитов ($1,25), Fast — 60 ($0,30) |
| `upscale_1080p` | `false`, **10 ₽** | `index` (≥ 0, «если несколько») | синхронная, результат сразу в `data` | Get 1080P, 5 кредитов; ответ 400 «1080P is processing… 1–2 minutes» |
| `upscale_4k` | `true`, **90 ₽** | `index` | «синхронная» | Get 4K, 120 кредитов, 5–10 мин, повтор ≥ 30 с, «records within 14 days» |

```json
// POST https://polza.ai/api/v1/media/aig_…/operations · google/veo3_fast · polza 2026-09-23 · [не проверено]
{"operation": "extend", "params": {"prompt": "camera keeps drifting over the fog", "seeds": 23456, "model": "fast"}, "async": true}
```

- `MediaOperationRequestDto.async` — по умолчанию `false`; «результат получить через `GET /v2/media/:id`» — такого
  пути в спеке нет, опрашивать `GET /v1/media/{новый id}` [S19].
- Пример синхронного апскейла в `operations.mdx` содержит `model: google/gemini-2.5-flash-image` и `.mp4` — ошибка
  копипаста в документации [S4].
- **Цена `extend` у `google/veo3` с default `model: "quality"`** в каталоге 45 ₽, а у KIE продление Quality в 4 раза
  дороже Fast — фактическое списание `[не проверено]`; до проверки ставь `"model": "fast"` явно.
- `polza.py ops <id> extend --params '{"prompt": "…", "model": "fast"}' --live` проверяет параметры операции по
  каталогу (`prompt` обязателен, `seeds` ≥ 10000), берёт `async` из каталога, ждёт синхронную до 150 с
  `[проверено: B/01, сценарий 19]`.

## 5. OpenAI-совместимый `POST /v2/images/generations`

- Обязательные `model`, `prompt`; `n` 1–10; `size` (`auto`, `256x256` … `1792x1024`); `quality` (`auto`, `low`,
  `medium`, `high`, `standard`, `hd`); `response_format` `url`|`b64_json`; `style` (DALL-E 3); `output_format`;
  `background` `transparent`|`opaque`|`auto`; `output_compression` 0–100; `user` [S5][S19].
- Синхронно до 120 с; дольше — ответ `{id: "gen_…", status: "pending"}` и опрос `GET /v1/media/{id}` (спека пишет
  `/v2/media/{id}` — нет в путях) [S5][S19]. `usage` с `cost_rub`; `data[].url`/`b64_json`, `revised_prompt`.
- С OpenAI SDK и `base_url="https://polza.ai/api/v1"` «запросы автоматически направляются на правильный путь» [S5].
- Как `size`/`quality`/`background` сопоставляются параметрам каталога модели (`image_resolution`, `aspect_ratio`) —
  не описано `[не проверено]`; у GPT Image 2.5 в каталоге polza параметра прозрачности нет вовсе. **Для работы базы —
  только `/v1/media` с параметрами каталога**; v2 — для совместимости с чужим кодом.
- FAQ называет пути `/api/v1/images/generations` и `/api/v1/videos/generations` [S13]; это legacy-пути без схем [S19].

## 6. Хранилище (storage)

| Политика | Срок | Как появляется | Источник |
|---|---|---|---|
| `TEMP_UPLOAD` | 24 ч | загрузка по умолчанию | [S6] |
| `PERMANENT` | бессрочно, в лимите хранилища организации | `storagePolicy: "PERMANENT"` при загрузке или `PATCH /v1/storage/files/{id}/keep` | [S6] |
| `TEMP_GENERATION` | 7 дней | результаты Media API, «вручную задать нельзя» | [S6][S2] |

```bash
# polza docs 18.09.2026 — загрузка файла (multipart); [не проверено] вживую, [проверено: макет B/01]
curl -sS -X POST https://polza.ai/api/v1/storage/upload \
  -H "Authorization: Bearer $POLZA_API_KEY" \
  -F file=@ref.png -F storagePolicy=TEMP_UPLOAD -F externalUserId=site-42
# или JSON: {"base64": "data:image/png;base64,…", "mimeType": "image/png", "storagePolicy": "TEMP_UPLOAD"}
```

- Ответ `StorageFilePresenter`: `id` (`file_…`), `fileType` `IMAGE`|`VIDEO`|`AUDIO`, `mimeType`, `source`
  `USER_UPLOAD`|`AI_GENERATION`, `storagePolicy`, `url` (`https://cdn.polza.ai/files/…` в доке; `s3.polza.ai` в
  примере спеки), `size`, `externalUserId` (≤ 128), `expiresAt`, `createdAt`, `updatedAt` [S6][S19].
- `GET /v1/storage/files`: `page`, `limit` 1–100, `fileType`, `source`, `storagePolicy`, `externalUserId`, `sortBy`
  (`createdAt`|`size`|`expiresAt`|`externalUserId`), `sortOrder`, `scope` (`all`|`mine`|`others`); документация —
  ответ `{data, meta{page, limit, total, totalPages}}`, спека — массив `[не проверено]` [S6][S19].
- `DELETE /v1/storage/files/{id}` → `{success: true}`, необратимо, с CDN [S6]. `GET /v1/storage/stats` — только
  admin с JWT консоли, API-ключ не подойдёт [S6].
- Хранилище принимает только изображения, видео и аудио [S17]. Хосты в примерах: `s3.polza.ai`, `cdn.polza.ai`,
  `storage.polza.ai` [S3][S6][S4].
- Результаты генераций лежат в том же хранилище (`source: AI_GENERATION`); перевести результат в `PERMANENT` через
  `keep` — логично, но не описано `[не проверено]`.

## 7. Результаты: срок жизни, скачивание, приватность

1. polza скачивает результат у провайдера на своё хранилище, хранит **7 дней**, отдаёт через CDN «внутри России»
   [S2]. У KIE (исполнитель `mie`) сгенерированные файлы живут 14 дней, логи — 2 месяца [S21].
2. **Скачивай в момент `completed`** — `polza.py` делает это сам: файл `<тег>__<модель>__<id>.<ext>`, sha256, размер,
   для картинок ширина/высота/альфа (Pillow), для видео длительность/кадры/кодек/звук (ffprobe), рядом
   `.passport.json` `[проверено]`. Архив по умолчанию — `99-raw/experiments/_polza/<агент>/<дата>/`.
3. Если скачивание упало (сеть, 404) — у тебя 7 дней: `polza.py download <id> --live`; после — ссылка мертва, id в
   `/v1/history` живёт 30 дней (changelog v1.4.0: «история запросов ограничена 30 днями») [S14].
4. polza «не хранит запросы и ответы» — только статистику и медиафайлы результатов 7 дней; логирование запросов
   включается на ключе (30 дней, `GET /v1/history/generations/{id}/log`) [S12][S13][S7]. Промт остаётся у
   исполнителя (KIE: логи 2 месяца) [S21].
5. Входные файлы (`TEMP_UPLOAD`) удаляются через 24 ч; удалить сразу — `DELETE /v1/storage/files/{id}`.
6. **Лица, фото клиента, персональные данные** — ни один медиа-провайдер polza не отмечен как соответствующий 152-ФЗ
   и хранящий данные в РФ (§11); без согласия заказчика не загружать. Соблюдение — тема агента L (`12-legal-provenance/`).

## 8. Деньги

### 8.1 Где цена

| Где | Что | Источник |
|---|---|---|
| `GET /v1/models` → `top_provider.pricing`, `providers[].pricing` | ставки в ₽: `per_request`, `tiers[{conditions, cost_rub}]` (+ `unitParam: duration` — за секунду), `video_per_second`, токены `*_per_million` | [S20][S9] |
| ответ `completed` → `usage.cost_rub` (= `usage.cost`) | «готовая стоимость в рублях, уже списанная» | [S15][S19] |
| `GET /v1/history/generations/{id}` | `clientCost` (₽), `providerCost` ($), `exchangeRate`, `attempts[].wasBilled` | [S7][S19] |
| `GET /v2/balance` | `reservedAmount` — резерв под идущие запросы | [S8] |

Формулы по видам тарифа, сетки цен всех 44 моделей и таблица «задача → цена» — файл 02 §2–§4
`[проверено: расчёт 99-raw/experiments/B/02-price-calculator]`.

### 8.2 Параметры, влияющие на цену: всегда явно

- Условия ступеней (`image_resolution=2K`, `resolution=720p`, `sound=false`, `mode=pro`, `has_video=true`,
  `input_images_count=3`, `duration=8`, `upscale_factor=4`, `aspect_ratio=16:9`, `quality=high`) сравниваются со
  значениями `input`. Как polza поступает с неуказанным параметром — берёт `default` каталога или запасную
  ступень `[]` — не описано `[не проверено]`.
- Запасная ступень `[]` равна **максимуму** у 13 моделей (Seedance 1.5 Pro 135 ₽ за ролик; Kling 3.0 45 ₽/с = 4K;
  Seedance 2 83,70 ₽/с; GPT Image 2.5 11 ₽ = 4K) и минимуму у 13 [B/02 README].
- `polza.py` подставляет default каталога явно и отказывает, если у ценового параметра default нет (Seedance 1.5 Pro
  `resolution`/`duration`, Kling 3.0 `duration`) `[проверено]`.
- Ловушки умолчаний каталога: Seedance 2 / Fast / Mini `duration` 15 с + звук `"true"`; Seedance 2.5 5 с + звук;
  Grok Video 8 с; MiniMax H3 Max 21:9; Kling 3.0 1:1; Wan 3.0 — 2 с; HappyHorse — 3 с (файл 02 §4.2, §8).

### 8.3 Баланс и резерв

- `GET /v2/balance` → `amount` (кошелёк организации всегда), **`available`** («сколько можно потратить»: остаток за
  вычетом резерва под выполняющиеся запросы, не больше остатков лимитов ключа и участника), `reservedAmount`,
  `spentAmount` (опускаются, если у участника личный лимит), `updatedAt`; строки с 8 знаками; кэш 1 с [S8][S19].
- `GET /v1/balance` — `amount` = остаток личного лимита для ключа участника; «для нового кода используйте v2» [S8].
- Резерв на время генерации — polza держит сумму до завершения; равен ли резерв оценке каталога — `[не проверено]`
  (тест: `/v2/balance` во время генерации).
- `polza.py` перед первой тратой в процессе вызывает `/v2/balance` и `/v1/key` и отказывает, если `available` или
  остаток лимита ключа меньше оценки (`--no-preflight` — отключить) `[проверено: B/01, сценарий 09a]`.

### 8.4 Лимиты ключа — второй предохранитель

- С v1.4.0 (26.03.2026): роли owner/admin/member/chat, **лимиты расходов на организацию и на пользователя для
  API-ключей** [S14].
- `PATCH /v1/api-keys/{keyId}`: `name`, `limitAmount` + `limitPeriod` (`day`|`week`|`month`), `enableS3Logging`,
  **`modelAccessMode: allow|deny` + `modelAccessSlugs`** (белый список моделей ключа); в спеке без bearer-security —
  вероятно, через консоль (JWT) [S19].
- `GET /v1/key`: `label`, `limit`, `limit_remaining`, `limit_reset` (`daily`|`weekly`|`monthly`|`never`), `usage`,
  `usage_daily`/`weekly`/`monthly`, `creator_user_id` [S19].
- Для фазы 5 (предложение): ключ «phase5» с лимитом на весь бюджет (2000 ₽, период `never` или месяц) и белым списком
  моделей плана; клиент поверх держит `--budget-total 2000`, `--max-job` по заданию.

### 8.5 История генераций — сверка журнала

- `GET /v1/history/generations`: `page`, `limit` 1–100, `dateFrom`, `dateTo`, `requestType` (`chat`|`image`|`video`|
  `audio`), `status`, `sortBy` (`createdAt`|`clientCost`); ключ видит только свои генерации [S7].
- `GET /v1/history/generations/{id}`: `model`, `modelDisplayName`, `provider`, `status`, `cost`, `usage`,
  `generationTimeMs`, `apiKeyName`, `unifiedModelId`, `apiType` (`media`), `responseMode` (`async`), `finalEndpointSlug`
  (фактический провайдер), `clientCost`, `latencyMs`, `queueTimeMs`, `isCancelled`, `attemptsCount`, `files[]`,
  `hasLog`; в спеке ещё `providerCost` ($), `profitAmount`, `exchangeRate`, `attempts[]` (`providerName`, `status`
  `pending|success|failed|timeout`, `wasBilled`, `httpStatus`, `errorCode`), `failedAttemptsCount` [S7][S19].
- `/{id}/log` — тело запроса и ответа, если логирование включено; `/{id}/children` — шаги server tools [S19].
- `polza.py` после `completed` берёт `/v1/history/generations/{id}` для паспорта (`provider_actual`); принимает ли
  история id вида `aig_…` — `[не проверено]` (при ошибке паспорт пишется без неё).

### 8.6 Возвраты и отмены

- Возврат неиспользованных средств — в течение 24 ч после оплаты [S13]; оплата картами, СБП, счётом для юрлиц [S13].
- Changelog: исправлены «неправильные списания при отмене генерации» (v1.4.9), «возврат средств при разрыве
  соединения» (v1.4.1, v1.4.7), «расчёт стоимости в fallback-цепочке» и «надёжность retry и cleanup в
  media-генерациях» (v1.2.2) [S14] — зоны, где раньше терялись деньги.

### 8.7 Курс и «где дешевле» (кратко; сравнение ведёт агент P)

- Долларовые провайдеры (`openai`, `google-*`, `openrouter`, `Alibaba`) пересчитываются по **117,992 ₽/$** — это
  ×1,404 к курсу ЦБ 84,0657 ₽/$ на 23.09.2026 [S20][S23]; документация обещает «без наценки» и «никакой конвертации
  валют и скрытых комиссий» [S13] `[мнение вендора]`.
- Цены `mie` — кредиты KIE × 0,6–1,75 ₽ (чаще 0,675–0,75) ≈ ×1,6–1,8 к прайсу KIE по курсу ЦБ
  `[проверено: расчёт 99-raw/experiments/B/05-polza-vs-kie-fx]`.
- Внутри polza у Nano Banana Pro/2/2.5 провайдеры `…/flex` Google дешевле `mie` на 17–41 % (файл 02 §5) — если
  маршрутизация `provider` в Media API работает `[не проверено]`.

## 9. Ошибки, повторы, лимиты частоты

### 9.1 Коды ответа

| HTTP | `error.code` | Смысл (описание OpenAPI) | Что делать | Повтор |
|---|---|---|---|---|
| 200 | — | успех; у `POST /v1/media` — тоже 200 (introduction.mdx обещает 201 для async) | — | — |
| 400 | `BAD_REQUEST` | «Некорректный запрос. Проверьте параметры и тело»; `details` — уточняющие поля (только 4xx) | исправить по `details` | нет |
| 401 | `UNAUTHORIZED`, `api_key_revoked` | ключ | остановить серию | нет |
| 402 | `INSUFFICIENT_BALANCE` | «Недостаточно средств **или достигнут лимит**»; в systemone — `detail.error_type: insufficient_balance` | пополнить / поднять лимит ключа; остановить серию | нет |
| 403 | `FORBIDDEN` | права ключа (белый список моделей?) | проверить ключ | нет |
| 404 | `NOT_FOUND` | модель или id | исправить | нет |
| 408 | `REQUEST_TIMEOUT` | «Истекло время ожидания ответа. Повторите запрос» | для POST — сначала история | осторожно |
| 409 | `CONFLICT` | «Конфликт состояния. Перечитайте ресурс» | перечитать статус | после чтения |
| 413 | `PAYLOAD_TOO_LARGE` | тело больше предела | файл — через хранилище | после правки |
| 429 | `TOO_MANY_REQUESTS` | «Слишком много запросов»; `metadata.attempts[].reason: RATE_LIMIT` у провайдера | ждать `Retry-After` / `x-ratelimit-reset` | да |
| 500 | `INTERNAL_ERROR` | ошибка сервера | POST — не повторять вслепую | GET — да |
| 502 | `BAD_GATEWAY` | «поставщик вернул некорректный ответ» | POST — история; GET — повтор | GET — да |
| 503 | `SERVICE_UNAVAILABLE` | нет доступных провайдеров (`metadata.reason: noProvidersForModel`) | другая модель / позже | позже |

Источники: [S1][S19][S27]. Коды 409 и 413 есть только в спеке.

```json
// ApiErrorPresenter (OpenAPI 1.0, 23.09.2026) [S19]
{"error": {"code": "BAD_REQUEST", "message": "Недопустимое значение параметра", "trace_id": "550e8400-…",
           "details": {"…": "…"},
           "metadata": {"reason": "noProvidersForModel", "raw": "The parameter `duration` specified in the request is not valid",
                        "provider_name": "openrouter", "attempts": [{"provider": "OpenRouter", "reason": "RATE_LIMIT"}]}},
 "trace_id": "550e8400-…"}
```

`introduction.mdx` показывает короткую форму `{"error": {"code": "NOT_FOUND", "message": "…"}}` [S1]; `trace_id` есть и
в заголовке `x-trace-id` [S20] — сохраняй его для обращений в поддержку.

### 9.2 Ошибки внутри генерации

`HTTP 200` + `status: "failed"` + `error {code, message, metadata {raw, provider_name}}` (§3.4). Типичные причины по
KIE: модерация контента, «Only English prompts are supported» у Veo без перевода, неверные кадры, таймаут
провайдера [S21]. `polza.py` возвращает код 4 и пишет в журнал `failed` с `usage.cost_rub` (0, если его нет).

### 9.3 Повторы и идемпотентность

- Ключа идемпотентности в API нет (ни в документации, ни в спеке) [S1][S19] — **повтор `POST /v1/media` может
  создать вторую платную генерацию.**
- Правило `polza.py`: `POST` повторяется только при 429 (до 3 раз, пауза по `Retry-After`); при 5xx и сетевом
  таймауте — без повтора, событие `unknown` с резервом суммы по оценке в журнале и подсказкой «проверьте history»;
  `GET` повторяется при 429/5xx/сети до 5 раз с удвоением паузы (2 → 30 с) `[проверено: B/01, сценарии 07, 10, 11]`.
- Перед ручным повтором после `unknown`: `GET /v1/history/generations?dateFrom=<время>&requestType=image|video` —
  нет ли уже созданной генерации.

### 9.4 Лимиты частоты

- Публичный каталог: `x-ratelimit-limit: 30`, `x-ratelimit-remaining`, `x-ratelimit-reset: 1` (секунда), сервер
  `ycalb` (Yandex Cloud ALB), `x-cache HIT|MISS` — снято 23.09.2026 [S20]. Для `/v1/media` и опроса лимиты не
  опубликованы `[не проверено]`; systemone.mdx: «429 — SDK повторяют сами» [S27].
- Исполнитель KIE: 20 новых задач за 10 с на аккаунт, 429 без постановки в очередь, до 100+ одновременных [S21];
  аккаунт polza у KIE общий для всех клиентов polza — очередь и 429 провайдера возможны без вашей вины `[спорно]`.
- `polza.py batch`: `--parallel` 2 по умолчанию, жёсткий потолок 3; пауза при `x-ratelimit-remaining: 0`
  `[проверено: B/01, сценарии 16, 16b]`.

## 10. Выбор провайдера и алиасы

### 10.1 Алиасы `model@…` — не для медиа

- Формат `<model>@<key>=<value>&…`, ключи только `provider`, `reasoning_effort`, `allow_fallbacks`; работают в
  `/v1/chat/completions`, `/v1/responses`, `/v1/messages`; **Media API, Audio, Embeddings — нет** (таблица
  `aliases.mdx`); конфликт алиаса и тела, неизвестный ключ, повтор, пустое значение → 400 [S10].
- Противоречие: гайд `gpt-5-4-image-2.mdx` — «для выбора провайдера используйте @-синтаксис:
  `openai/gpt-5.4-image-2@mie`» [S18] (и не в формате `key=value`). PLAN.md базы тоже пишет «выбор провайдера —
  `model@provider`». Позиция: **в Media API — объект `provider` в теле**; алиас — только как тест в фазе 5
  `[спорно]`.

### 10.2 Объект `provider`

```json
// ProviderDto (OpenAPI 1.0) — для Media API не проверено
{"provider": {"only": ["google-vertex/global/flex"], "allow_fallbacks": false,
              "max_price": {"image": 10, "request": 10, "video_per_second": 20}}}
```

- Поля: `order[]`, `only[]`, `ignore[]`, `sort` (`price`|`throughput`|`latency`), `allow_fallbacks`,
  `require_parameters` («требовать от OpenRouter поддержку всех переданных параметров»), `max_price` {`prompt`,
  `completion` (₽/1M), `image` (₽/шт), `audio`, `request` (₽/запрос), `video_per_second` (₽/с), `stt_per_minute`,
  `tts_per_million_characters`} [S19][S11]. По умолчанию — автоматический выбор; все примеры гайда — для chat [S11].
- Имена провайдеров — из `providers[].name` (`GET /v1/models?include_providers=true`): `mie`, `bananalab`, `openai`,
  `google-vertex/global`, `google-vertex/global/flex`, `google-ai-studio`, `google-ai-studio/global`,
  `google-ai-studio/flex`, `google-ai-studio/global/flex`, `google-ai-studio/priority`, `cloud-ru`, `Alibaba`,
  `openrouter` [S20]. **Не путать** со слагами фильтра `/v1/models/catalog` (`meta.availableProviders`: `google`,
  `gpt-image`, `flux-2`, `qwen2-1`, `kling-3.0`, `mie`…) — это бренды для витрины [S20].
- Порядок в `providers[]` не равен приоритету: у Nano Banana 2 Lite первым идёт `google-vertex/global`, а
  `top_provider` — `mie` [S20]. Какой провайдер выбирается по умолчанию для медиа — предположительно `top_provider`
  `[не проверено]`.
- `polza.py` оценивает цену по провайдеру из `provider.only` (один) или `order[0]` и предупреждает, если не задано
  `"allow_fallbacks": false` (иначе фактический провайдер и цена могут отличаться).

### 10.3 Модели с несколькими провайдерами (снимок 23.09.2026 09:21)

| Модель | Провайдеры (top — первым) | Главные различия |
|---|---|---|
| `google/gemini-3-pro-image-preview` (Nano Banana Pro) | **mie** 13,5/13,5/18 ₽; bananalab (то же); google-vertex/global и google-ai-studio/global (токены, вых. картинка 14 159,04 ₽/1M); …/flex (7079,52 ₽/1M); cloud-ru (только текст) | референсов: mie 8, bananalab 14, Google 10; промт: Google ≤ 16 000; `aspect_ratio` у Google без `auto` |
| `google/gemini-3.1-flash-image-preview` (Nano Banana 2) | **mie** 4,8/7,2/10,8; bananalab (без `output_format`); google-ai-studio, google-vertex/global (7079,52); google-vertex/global/flex (3539,76); cloud-ru | референсов: mie 14, Google 10; у Google нет `output_format` |
| `google/gemini-2.5-flash-image` (Nano Banana) | **mie** 2,90; bananalab 3,00 (реф. 14); google-vertex/global, google-ai-studio (3539,76); …/flex (1769,88); google-ai-studio/priority (6371,568); cloud-ru | реф.: mie 8, Google 10; промт Google ≤ 16 000 |
| `google/gemini-3.1-flash-lite-image` (NB2 Lite) | **mie** 2,90; google-vertex/global, google-ai-studio (3539,76) | у Google `image_resolution` только 1K, промт ≤ 16 000 |
| `google/gemini-3.1-flash-image` (NB2 GA) | **google-vertex/global**, google-ai-studio (7079,52) | `parameters` нет ни у одного — вызов через `/v1/media` не документирован |
| `openai/gpt-5.4-image-2` | **mie** 4/7/11; openai (токены: вход 943,936, выход 1769,88, вых. картинка 3539,76 ₽/1M) | mie: `auto`, 6 соотношений, 1K/2K/4K, реф. 16, промт 20 000; openai: 10 соотношений (с 21:9, 4:5, 5:4), 1K/2K, реф. 10, промт 32 000 |
| `openai/gpt-5-image` | **mie** 4,50; openai (1179,92 / 1179,92 / 4719,68) | mie: `mask_url`, `isEnhance`, 3 соотношения, реф. 5, промт 4000; openai: без маски, 10 соотношений, реф. 10, промт 32 000 |

Цены токенных провайдеров в рублях за картинку — файл 02 §2.5. Остальные 37 медиа-моделей — один провайдер (у
`minimax/hailuo-3-max` и `alibaba/wan-3.0-prime` массив `providers[]` пуст, `top_provider` = `openrouter`) [S20].

## 11. Модерация, данные, исполнитель

### 11.1 Флаги каталога

У **всех 44 медиа-моделей и у всех их провайдеров** (включая `cloud-ru`): `is_fz152_compliant: false`,
`stores_data_in_russia: false`, `is_hosted_on_polza_infrastructure: false`, `is_moderated: false` (снимки 08:20 и
09:21) [S20]. Changelog v1.4.5: в каталоге появился фильтр «Данные в РФ» [S14] — для медиа он пуст.

### 11.2 Модерация

`is_moderated` — «модерируется ли контент провайдером» [S9]. `false` у всех медиа — но фильтры исполнителя остаются:
пример ошибки OpenAPI — `"raw": "content policy violation", "provider_name": "kie"` [S19]; у KIE `nsfw_checker` по
умолчанию выключен, у Google/OpenAI собственные фильтры безопасности; `personGeneration` у Veo polza не выставляет
[S21]. Ожидай `failed` на людях, брендах, насилии `[не проверено]`; правила «что генерировать без вопроса заказчику» —
агент L.

### 11.3 Кто исполняет: `mie` ≈ KIE.ai

Улики: (1) описания параметров каталога — «auto передаётся в KIE как adaptive» (Seedance 2.5, Seedance 2 Mini),
«1080p — по документации KIE для Seedance 2», «Будет передано в KIE как video_list» (Gemini Omni) [S20];
(2) пример `MediaErrorPresenter.metadata.provider_name: "kie"` [S19]; (3) id моделей polza = слаги KIE
(`gpt-image-2-5-flare`, `seedream/5-pro-text-to-image`, `veo3_fast`), набор параметров Veo = старый Veo API KIE
(`generationType`, `seeds` 10000–99999, `enableTranslation`, `watermark`) [S21]; (4) цены `mie` = кредиты KIE ×
фиксированный множитель в рублях (B/05) [S22]. Следствия: хранение у KIE 14 дней, логи 2 месяца; загрузки 24 ч;
20 задач/10 с; «стабильность может быть ниже официальных провайдеров» (слова KIE) [S21]. `mie`/KIE нет ни в одной
категории `privacy.mdx` [S12]. `bananalab` — провайдер Nano Banana (changelog v1.2.2); `fal.ai` (v1.5.0) на
23.09 обслуживает только TTS (данные агента P) [S14].

### 11.4 Приватность по документации polza

- polza не хранит тексты запросов и ответов; хранит статистику и медиа-результаты 7 дней; логирование — по
  желанию на ключе, 30 дней [S12][S13].
- Категории провайдеров `privacy.mdx`: «безопасные» (Azure, Groq, Bedrock, DeepInfra, Fireworks, Together, Cerebras,
  SambaNova, Featherless), «временное хранение до 30 дней» (OpenAI, Anthropic, Cohere, Google Vertex, Mistral, xAI…),
  «потенциально небезопасные» (DeepSeek, OpenInference) [S12].
- Enterprise: «152-ФЗ соответствие», zero-logging, SLA 99,97 % [S13] — к медиа-провайдерам из каталога не относится.

## 12. Клиент `polza.py` и `polza_catalog.py`

Файлы: `../../scripts/ai-media/polza.py`, `../../scripts/ai-media/polza_catalog.py` (Python 3.13, только стандартная библиотека). Проверка:
30/30 сценариев на локальном макете `[проверено]`, калькулятор — 75 ручных и 9
токенных случаев `[проверено]`, валидатор — 51 ловушка `[проверено]`. **Против настоящего polza не
запускался.**

### 12.1 Подготовка (заказчик, к фазе 5)

```bash
# ключ — только в файл с правами 600; в чат, задания и заметки не вставлять
mkdir -p ~/.config/polza && install -m 600 /dev/null ~/.config/polza/api_key && nano ~/.config/polza/api_key
python3 ../../scripts/ai-media/polza.py balance --live        # /v2/balance + /v1/key: ключ жив, лимит виден (0 ₽)
python3 ../../scripts/ai-media/polza_catalog.py snapshot && python3 ../../scripts/ai-media/polza_catalog.py diff 2026-09-23 latest
```

Окружение: `POLZA_API_KEY` / `~/.config/polza/api_key`; `POLZA_BASE_URL` (по умолчанию `https://polza.ai/api`);
`POLZA_CATALOG` (снимок; по умолчанию последний); `POLZA_LEDGER` (`99-raw/experiments/_ledger.jsonl`);
`POLZA_OUT_ROOT` (`99-raw/experiments/_polza`); `POLZA_BUDGET_TOTAL` (2000); `POLZA_BUDGET_AGENT`; `POLZA_MAX_JOB` (60).

### 12.2 Задание

```json
// 99-raw/phase5/jobs/t1-zimage.json · tongyi-mai/z-image · polza 2026-09-23 · [не проверено]
{"model": "tongyi-mai/z-image",
 "input": {"prompt": "soft morning light over a misty lake, film grain, empty space on the left for a headline",
           "aspect_ratio": "16:9"},
 "tag": "t1-zimage", "agent": "phase5", "notes": "первый живой вызов: протокол и форма ответа",
 "variant": 1, "max_rub": 2}
```

Необязательные поля: `provider` (объект §10.2), `variant` (новый хэш для best-of-N без `--force`), `max_rub` (лимит
на задание), `out_dir`, `meta.ref_video_seconds` (цена Motion Control / Topaz Video, если видео не локальное),
`user`. Серия — JSONL, строка на задание; `#` и `//` — комментарии. Файлы в `images`/`videos`: URL, `data:`URI,
локальный путь (относительно файла задания) или `{type, data}`.

### 12.3 Команды

| Команда | Что делает | Сеть и деньги |
|---|---|---|
| `models [--type image\|video] [--search S] [--fresh]` | список медиа-моделей с ценой | снимок; `--fresh` — бесплатный GET |
| `show MODEL [--provider P] [--json]` | параметры, сетка цен, операции, провайдеры, заметки и расхождения | нет |
| `estimate JOB.json\|JOBS.jsonl [-v]` | проверка по каталогу + цена + бюджет + кэш | нет |
| `run JOB.json` | сухой прогон: точный запрос (с `--curl` — команда curl), оценка, проверки | нет |
| `run JOB.json --live` | `/v2/balance` + `/v1/key` → POST → опрос → скачивание → паспорт → журнал | **да** |
| `batch JOBS.jsonl --live [--parallel 2]` | серия; вся сумма проверяется до старта; стоп после 401/402/403 | **да** |
| `status ID --live`, `download ID --live` | статус; дожать и скачать (7 дней), закрыть запись журнала | 0 ₽ |
| `upload FILE [--permanent] --live` | multipart в хранилище (`TEMP_UPLOAD` 24 ч / `PERMANENT`) | 0 ₽ |
| `ops ID extend\|upscale_1080p\|upscale_4k [--params JSON] --live` | операция Veo | **да** |
| `ledger [--sum] [--agent X] [--tail N]` | журнал: суммы по агентам, резерв неоднозначных | нет |
| `balance --live`, `history ID --live` | баланс и лимит ключа; история генерации | 0 ₽ |

Коды выхода: 0 — успех; 1 — ошибка задания/проверки; 2 — отказ бюджета/цены; 3 — таймаут опроса (дожать `download`);
4 — `failed`/`cancelled`; 5 — HTTP-ошибка; 6 — ошибка скачивания.

### 12.4 Что делает `run --live`

1. Проверка по каталогу (снимок), приведение типов, явная подстановка default ценовых параметров, оценка цены.
2. Кэш: тот же хэш запроса (модель + input с sha256 локальных файлов + provider + variant) уже `completed` и файлы на
   месте → 0 ₽, событие `cache_hit`; обход — `--force`.
3. Лимиты: оценка ≤ `max_rub`/`--max-job`; журнал + оценка ≤ `--budget-total` и `--budget-agent`; неизвестная цена →
   отказ (`--allow-unknown-price`); `/v2/balance.available` и `/v1/key.limit_remaining` ≥ оценки.
4. Событие `submit` в журнал **до** отправки (резерв), загрузка крупных файлов в хранилище, `POST /v1/media` с
   `"async": true`, событие `created`.
5. Опрос 4/8 с с разбросом, печать смены статусов; `timeout` → код 3.
6. `completed` → скачивание всех URL (атомарно, sha256), `/v1/history/generations/{id}` для провайдера, паспорт,
   событие `completed` с `usage.cost_rub`.

### 12.5 Журнал, паспорт, бюджет

- Журнал `99-raw/experiments/_ledger.jsonl` — append-only события (`submit`, `created`, `completed`, `failed`,
  `cancelled`, `timeout`, `unknown`, `http_error`, `cache_hit`, `upload`) с `uid`, `agent`, `tag`, `model`, `id`,
  `estimate_rub`, `cost_rub`, `files`, `passport`, `base_url`; запись под `flock`. Потрачено = факт `cost_rub` у
  завершённых + оценка у незавершённых (`submit`/`created`/`timeout`/`unknown`) — консервативно. Бюджет считается
  только по записям с тем же `base_url` (прогоны макета не съедают бюджет polza).
- Паспорт `<файл>.passport.json`: задание (тег, агент, заметки, вариант), промт, зерно, тело запроса (base64 заменён
  длиной и sha256), снимок каталога и оценка со ступенью и источниками значений (`input`/`default`), подставленные
  default и замечания проверки, ответы создания и финала, история (провайдер, `clientCost`), тайминги (отправка,
  завершение, секунды, число опросов), цена (`usage`, оценка, разница), файлы (путь, URL, байты, sha256, MIME,
  ширина/высота/альфа или длительность/fps/кодек/звук). Пути — относительно корня проекта.
- Ключ не печатается и не пишется (проверено grep по выводам, журналу, паспортам и телам запросов в B/01).

### 12.6 `polza_catalog.py`

| Команда | Что делает |
|---|---|
| `snapshot [--with-openapi]` | `GET /v1/models`, `?include_providers=true`, `/v1/models/catalog?type=image|video&limit=100` → `99-raw/cache/polza/<дата>[_ЧЧММ]/` + `snapshot.meta.json` (время, sha256, заголовки) + нормализация; чужие снимки не перезаписывает |
| `normalize [SNAP] [--providers SNAP2]` | `media-models.normalized.json`: единые поля (`unified`), типы, умолчания, цена (вид, ценовые параметры, мин/макс, запасная ступень, цена с умолчаниями), сетка цен, операции, провайдеры с отличиями параметров, заметки и расхождения с документацией |
| `table [SNAP] [--type] [--out]` | Markdown-таблица медиа-моделей |
| `diff A B [--all-types] [--json]` | новые/удалённые модели, изменения ступеней цен, параметров (поля), провайдера, флагов, `providers[]` |
| `price MODEL k=v …`, `check MODEL k=v …` | быстрая оценка и проверка без файла задания |
| `selftest` | 19 встроенных проверок |

### 12.7 Ограничения клиента

- Нет отмены генерации (эндпоинта нет в спеке); нет колбэков (`callBackUrl` не используется — опрос).
- Цена по провайдеру без `allow_fallbacks: false` может не совпасть; токенная цена — оценка по таблицам вендоров
  (NB2 1K = 1120 токенов и т. п.), фактическая — `usage.cost_rub`.
- Строки против булевых, строгость лишних полей, форма `data` у конкретной модели, id истории для `aig_…` — проверяются
  в §13; при расхождении правится `coerce_value` в `polza_catalog.py` (одно место).

## 13. План первого живого вызова (фаза 5, ≤ 30 ₽)

Задания и сухой прогон — `99-raw/experiments/B/06-phase5-smoke-plan/` (`jobs/`, `dry-run.txt`): T1–T5 по каталогу
**15,41 ₽**, весь план в худшем случае **29,21 ₽** `[проверено: сухой прогон B/06]`; живое поведение — `[не проверено]`.

| № | Модель и параметры | ₽ | Что решает |
|---|---|---|---|
| T0 | `balance --live`, `status aig_x --live` | 0 | ключ и лимит, формы баланса и ошибки 404 |
| T1 | `tongyi-mai/z-image`, 16:9 | 1,40 | протокол: код POST, id, статусы, форма `data`, `usage.cost_rub`, хост CDN, заголовки лимитов, история по `aig_…`; повтор — кэш (0 ₽) |
| T2 | `qwen/image-2.1`, 1:1, 1K, `background: transparent`, `output_format: png` | 3,00 | принимаются ли поля вне OpenAPI DTO; есть ли альфа |
| T3 | `grok-imagine-video-1-5`, 480p, `duration: "1"` | 1,62 | видео-цикл и цена за секунду |
| T4 | `bytedance/seedance-1.5-pro`, 480p, `duration: "4"`, `generate_audio: "false"`, `fixed_lens: "true"` | 5,25 | строковые булевы; ступень `sound=false`; звука нет |
| T5 | `google/gemini-3.1-flash-lite-image` + `provider: {only: ["google-ai-studio"], allow_fallbacks: false}` | ≈ 3,97 | работает ли выбор провайдера в Media API (2,90 ₽ → проигнорирован) |
| T6 | Z-Image `aspect_ratio: "21:9"` (`--no-validate`) | 0 | серверная проверка значений (400 + `details`) |
| T7 | Z-Image + `negative_prompt` (`--allow-unknown`) | 0 / 1,40 | строгость к лишним полям |
| T8 | `openai/gpt-image-2.5-sunburst` без `image_resolution` (`--no-fill`) | 4 / 11 | default каталога или запасная ступень `[]` |

После серии — `polza.py ledger --sum` против `/v2/balance.spentAmount` и `/v1/history/generations`. Если T8 даст
11 ₽, правило «ценовые параметры — всегда явно» становится обязательным для всех агентов (клиент уже так делает).

**Итог 25.09.2026** (заход 1 фазы 5, 09:07–09:50; протокол — 20,76 ₽ с B2-03) `[проверено]`:
T0 — ключ и баланс отвечают; T1 — id `gen_…`, `usage.cost_rub` 1,40, история по `gen_…` работает; T2 — `background: transparent`
принят, альфа настоящая (64 % прозрачных, мягкий край; лист `99-raw/phase5/runs/0-protocol/t2-qwen-alpha_on-white-dark-checker.jpg`);
T3 — Grok 1 с — 1,62 ₽; T4 — строки-булевы приняты, 5,25 ₽, звука нет; T5 — `provider` работает (4,06 ₽ через Google AI Studio);
T6 — 400 без списания; T7 — лишнее поле принято и списано; T8 — ступень каталога 1K (4 ₽); T9 (заход 2) — `first_frame_url` и
`last_frame_url` GA Omni принимают URL хранилища polza; B2-03 (чат) — рассуждения биллятся сверх `max_tokens` (≈ 121 токен при лимите
64) и могут съесть ответ (позже G-03 — пустой ответ «length» за 9,77 ₽). Сверка: `spentAmount` − 147,70 (до фазы 5) = журнал до
копейки (338,11 = 147,70 + 190,41).

## 14. Проверить в фазе 5 (уровень API; модельные вопросы — файл 02 §9)

| № | Вопрос | Тест | ₽ | Критерий | Ценность |
|---|---|---|---|---|---|
| 1 | Код ответа `POST /v1/media` (200 или 201), префикс id | T1 | 1,40 | записать | 2 |
| 2 | Форма `data` у картинки и видео; `output.url`? | T1, T3 | — | разобран без правки клиента | 3 |
| 3 | Строки `"true"`/`"false"` там, где OpenAPI ждёт boolean | T4 | 5,25 | 200 и цена 5,25 | 3 |
| 4 | Поля каталога вне DTO (`background`, `mask_url`, `seeds`, `generationType`) | T2 (+ Veo в стенде) | 3,00 | приняты и работают | 3 |
| 5 | Строгость к лишним полям | T7 | 0–1,40 | 400 или `warnings[]` | 2 |
| 6 | Какая ступень без ценового параметра | T8 | 4–11 | 4 = default, 11 = `[]` | 3 |
| 7 | `provider` в Media API и имена провайдеров | T5 | ≈ 4 | цена и `finalEndpointSlug` Google | 3 (от этого зависит экономия flex) |
| 8 | Алиас `openai/gpt-5.4-image-2@mie` в Media API | отдельный запрос 1K | 4 | 400 или принят | 1 |
| 9 | `/v1/history/generations/{aig_…}`: провайдер, `clientCost`, `exchangeRate` | T1 | 0 | ответ 200 | 2 |
| 10 | Резерв в `/v2/balance.reservedAmount` во время генерации = оценке? | T3 (опрос баланса вручную) | 0 | совпадает | 1 |
| 11 | Лимиты частоты `/v1/media` и опроса (`x-ratelimit-*`) | T1 | 0 | записать заголовки | 2 |
| 12 | Срок жизни ссылки результата (7 дней) и код после истечения (`RESULT_EXPIRED`?) | повторный `download` T1 через 8 дней | 0 | 404/410 и код | 1 |
| 13 | `PATCH /v1/storage/files/{id}/keep` для результата генерации | файл T1 | 0 | `PERMANENT` | 1 |
| 14 | Списание за `failed` (модерация) | естественный отказ в стенде | 0 | `cost_rub` 0 | 2 |
| 15 | `upscale_4k` синхронно или асинхронно; цена `extend` с `model: quality` | стенд Veo (если в плане) | 45–90 | записать | 1 |
| 16 | Время до результата по моделям | все паспорта | 0 | записать в `13-routing-matrix` | 2 |

**Ответы фазы 5 (25.09.2026)**: №1 — id `gen_…`; №3 — да (5,25 ₽); №4 — да (`background` у Qwen 2.1 работает); №5 — лишние поля
принимаются и списываются; №6 — 4 ₽ (default каталога); №7 — работает (Google AI Studio 4,06 ₽); №9 — история отвечает по `gen_…`
(ею разрешены 12 обрывов POST); №14 — `failed` провайдера (`INTERNAL_ERROR`, 503 «нет провайдеров») — 0 ₽; №16 — время в журнале
(`wall_s`: 156 картинок — 6–485 с, медиана 67 с; 46 видео — 26–845 с, медиана 52 с). Остальные (№2 форма `output.url`, №8, №10–13,
№15) — не проверялись `[проверено]`.

## Частые ошибки

1. **`model@provider` в Media API** (из PLAN.md или гайда GPT-5.4 Image 2) — по `aliases.mdx` для медиа не работает;
   нужен объект `provider` в теле.
2. **Параметры «по памяти» или из OpenAPI** (`seed` у Veo, `negative_prompt` у Kling 3, `duration` у Veo,
   `background` у GPT Image 2.5, `quality` у Nano Banana) — только `parameters` каталога этой модели и этого провайдера.
3. **Перенос параметров одного провайдера на другого**: маска `openai/gpt-5-image` есть у `mie`, нет у `openai`; 4K у
   GPT-5.4 Image 2 есть у `mie`, нет у `openai`; референсов у NB Pro 8 (`mie`) против 14 (`bananalab`).
4. **Без `"async": true`** — синхронное ожидание до 120 с, разрыв соединения = спор о списании.
5. **Повтор POST после таймаута или 500** — возможное двойное списание; сначала история.
6. **Пропуск длительности у Seedance 2** — 15 с по умолчанию (415 ₽ за 720p); у Seedance 1.5 Pro без
   `resolution`/`duration` — запасная ступень 135 ₽.
7. **`generate_audio` не задан** — у Seedance 2/Fast/Mini/2.5 звук включён по умолчанию; фоновым петлям он не нужен.
8. **Ссылка из `data` вместо файла** — через 7 дней мертва; скачивать сразу и хранить sha256.
9. **Разбор только `data.url`** — ломается на `data[]` и `output.url`.
10. **`/v1/balance` вместо `/v2/balance`** — для ключа участника это остаток личного лимита, не кошелёк; резерв не
    учтён.
11. **Слаги `availableProviders` из `/v1/models/catalog` как имена провайдера** (`google` вместо
    `google-vertex/global/flex`).
12. **«`is_moderated: false` — значит можно всё»** — фильтры исполнителя (KIE, Google, OpenAI) остаются.
13. **«Данные остаются в России»** — CDN результатов в РФ, но все исполнители медиа — зарубежные, флаги 152-ФЗ `false`.
14. **Ключ в задании, заметке или выводе** — только файл `~/.config/polza/api_key` (600) или переменная окружения.
15. **`TEMP_UPLOAD`-ссылка как референс через сутки** — файл удалён; для серий на несколько дней — `PERMANENT`.
16. **Хост `api.polza.ai`** из одного гайда вместо `https://polza.ai/api`.
17. **Путь `/v2/media/{id}` из описаний спеки** — такого пути нет; опрос — `GET /v1/media/{id}`.

## Чек-лист

- [ ] Задание идёт через `polza.py` (сухой прогон просмотрен, оценка цены устраивает)?
- [ ] Все параметры — из каталога этой модели и этого провайдера (`polza.py show MODEL [--provider P]`)?
- [ ] Ценовые параметры (разрешение, длительность, звук, режим, `upscale_factor`) заданы явно?
- [ ] `generate_audio`/`sound` = `"false"` для фоновых видео?
- [ ] `"async": true`?
- [ ] Для конкретного провайдера — `provider.only` + `"allow_fallbacks": false`?
- [ ] Референсы — URL, доступные исполнителю, или загружены в хранилище (≤ 24 ч до использования)?
- [ ] Нет фото людей и персональных данных без согласия заказчика?
- [ ] Лимит на задание (`max_rub`), общий и агента не превышены (`polza.py ledger --sum`)?
- [ ] Для серии — снимок каталога свежий (`snapshot` + `diff` за сегодня)?
- [ ] Результат скачан, sha256 и паспорт на месте, запись `completed` в журнале?
- [ ] `usage.cost_rub` совпал с оценкой (иначе — записать расхождение в заметки)?
- [ ] После ошибки POST — проверена история перед повтором?
- [ ] Для Veo: `generationType` задан явно, `seeds` (не `seed`) 10000–99999, `enableTranslation` осознанно?

## Открытые вопросы и противоречия

| № | Противоречие / пробел | Стороны | Позиция базы |
|---|---|---|---|
| 1 | Код успеха создания | `introduction.mdx`: 201 для async; OpenAPI: 200 | клиент принимает оба; T1 |
| 2 | `async` по умолчанию | OpenAPI и `operations.mdx`: `false`; гайд Gemini Omni: `true`, «обязателен» | всегда `true` явно |
| 3 | Тип булевых параметров | каталог и гайды — строки; OpenAPI — boolean (`generate_audio` приводит строки) | строки; T4 |
| 4 | Набор полей input | OpenAPI DTO без `mask_url`, `background`, `fixed_lens`, `seeds`, `generationType`…; каталог их содержит | каталог; T2 |
| 5 | Строгость к лишним полям | Lyria — 400 на лишние; гайд Seedance 2 шлёт `multi_shots` вне каталога | клиент отказывает; T7 |
| 6 | Выбор провайдера для медиа | `aliases.mdx`: алиасы не для Media API; гайд GPT-5.4 Image 2: `@mie`; PLAN.md: `model@provider` | объект `provider`; T5 |
| 7 | `upscale_4k` | каталог: `async: true`; `operations.mdx`: синхронная | как в каталоге |
| 8 | Параметры `extend` | каталог: `prompt`, `seeds`, `watermark`, `model`; `operations.mdx`: `prompt`, `seeds`, `duration` 3–10 с | каталог |
| 9 | Цена `extend` с `model: quality` | каталог 45 ₽ у обеих моделей; KIE Quality в 4 раза дороже Fast | ставить `fast` явно до проверки |
| 10 | Путь опроса операций и v2-картинок | спека: `GET /v2/media/:id` (пути нет) | `GET /v1/media/{id}` |
| 11 | Форма списка файлов хранилища | документация `{data, meta}`, спека — массив | клиент не использует |
| 12 | Форма `data` результата | `data{url}`, `data[]`, `output.url`; схемы в спеке отсутствуют | разбирать все формы |
| 13 | Срок хранения | polza 7 дней; KIE 14 дней | скачивать сразу |
| 14 | «Без наценки», «никакой конвертации валют» | курс 117,992 ₽/$ = ×1,40 к ЦБ; `mie` ≈ ×1,6–1,8 к KIE | `[мнение вендора]`; P сравнивает |
| 15 | Кто такой `mie` | нигде не назван; улики — KIE | `[спорно]`, вероятно KIE |
| 16 | Лимиты частоты `/v1/media` | не описаны; каталог — 30/с; KIE — 20 задач/10 с | ≤ 3 параллельно |
| 17 | Хост API | `polza.ai/api` везде, `api.polza.ai` в `reasoning-tokens.mdx` | `polza.ai/api` |
| 18 | FAQ: `/api/v1/images/generations`, `/api/v1/videos/generations` | legacy без схем; основной — `/v2/images/generations` и `/v1/media` | `/v1/media` |
| 19 | Сортировка `/v1/models/catalog` | док: `sortBy created_at`, `sortOrder` по умолчанию `desc`; спека: `createdAt`, `asc`, ещё `sort` | не используем сортировку |
| 20 | Changelog | последняя запись v1.5.3 от 25.04.2026 при каталоге от 23.09 — отстаёт на 5 месяцев | каталог — источник истины по моделям |
| 21 | NB2 GA `google/gemini-3.1-flash-image` | в каталоге без `parameters`; как вызывать через `/v1/media` — нет в документации (возможно, через chat `modalities`) | не использовать до проверки |
| 22 | Место `callBackUrl` | гайд Lyria — верхний уровень тела; OpenAPI — поле `input` | не использовать, опрос |

## Источники

Документация polza — открытый репозиторий `github.com/polza-ai/docs` (обновлён 18.09.2026), копия
`99-raw/cache/polza/2026-09-23/docs-repo/`; сайт `https://polza.ai/docs` собирается из него (Mintlify, `docs.json`
ссылается на `https://polza.ai/api/openapi.json`). Надёжность документации — официальная, но с копипастом и
отставанием от каталога (см. «Противоречия»).

- [S1] polza · `api-reference/introduction.mdx` — база `https://polza.ai/api`, авторизация, коды ответа, формат
  ошибки, лимиты (файл 50 МБ, таймаут 600 с). Официально, кратко.
- [S2] polza · `api-reference/media/create.mdx` — `POST /v1/media`: поля, файлы `{type, data}`, автозагрузка base64,
  хранение 7 дней на CDN в РФ.
- [S3] polza · `api-reference/media/status.mdx` — статусы, интервалы опроса 3–5/5–10 с, форма `completed`.
- [S4] polza · `api-reference/media/operations.mdx` — `extend`, `upscale_1080p`, `upscale_4k`; пример с копипастом.
- [S5] polza · `api-reference/images/generations.mdx` — OpenAI-совместимый `/v2/images/generations`, 120 с.
- [S6] polza · `api-reference/storage/{upload,list-files,get-file,delete-file,keep,stats}.mdx` — хранилище и политики.
- [S7] polza · `api-reference/history/generations.mdx` — история, поля деталей, 30 дней.
- [S8] polza · `api-reference/other/balance.mdx`, `balance-v2.mdx` — v1 и v2, `available`, резерв.
- [S9] polza · `api-reference/models/list.mdx`, `models/catalog.mdx`, `gaidy/models.mdx` — каталог, поля, цены.
- [S10] polza · `osobennosti/aliases.mdx` — алиасы `model@key=value`, эндпоинты, где они работают.
- [S11] polza · `gaidy/provider-selection.mdx` — объект `provider`, `max_price`; примеры только для chat.
- [S12] polza · `osobennosti/privacy.mdx` — что хранится, категории провайдеров.
- [S13] polza · `glavnoe/faq.mdx`, `glavnoe/enterprise.mdx`, `glavnoe/principles.mdx` — оплата, возвраты, 152-ФЗ в
  Enterprise, «без наценки» (маркетинг).
- [S14] polza · `changelog.mdx` (v1.2.2 12.03 — v1.5.3 25.04.2026) — лимиты ключей, история 30 дней, исправления
  списаний. Отстаёт от каталога.
- [S15] polza · `osobennosti/usage.mdx` — `usage.cost_rub` «уже списанная».
- [S16] polza · `gaidy/mcp.mdx`, `gaidy/getting-started.mdx` — MCP (аккаунт, без генерации), ключи.
- [S17] polza · `gaidy/media-input.mdx` — вход файлов в chat-модели, хранилище только для медиа.
- [S18] polza · 28 гайдов медиа-моделей `gaidy/*.mdx` (Veo 3.1, Seedance 1.5/2, Kling 3/2.5/Motion Control, Wan
  2.5/2.6, Gemini Omni, Seedream 3/4/4.5/5 Lite, FLUX.2 Pro/Flex, Nano Banana/Pro/2, GPT Image 1.5, GPT-5 Image/Mini,
  GPT-5.4 Image 2, Grok, Qwen, Topaz, Suno, Lyria 3) — примеры тел, `async`, типы значений, формы ответа.
- [S19] polza · публичная OpenAPI `https://polza.ai/api/openapi.json` (OpenAPI 3.0.0, `info.version` 1.0, 355 675 Б,
  снята 23.09.2026 08:49; копия `99-raw/cache/polza/2026-09-23/openapi.json`) — схемы DTO и ответов, коды, ключи.
  Самый точный источник по форме, но DTO медиа отстают от каталога.
- [S20] polza · `GET /v1/models`, `?include_providers=true`, `/v1/models/catalog` — снимки `99-raw/cache/polza/2026-09-23/`
  (08:20 МСК) и `2026-09-23_0921/` (09:21), заголовки ответа в `snapshot.meta.json`. Источник истины по моделям.
- [S21] KIE.ai · docs.kie.ai: Getting Started, File Upload API, Common API (download-url), Veo 3.1 (generate, Get
  1080P, Get 4K, Extend), Kling 3.0, Seedance 2, Seedance 1.5 Pro — снято агентом P 23.09.2026, кэш
  `99-raw/cache/kie-2026-09-23/`. Документация исполнителя `mie` (вероятного).
- [S22] KIE.ai · публичный прайс `https://api.kie.ai/client/v1/model-pricing/page` (489 строк, 23.09.2026) — опыт
  агента P `99-raw/experiments/P/02-kie-vs-polza/`; сопоставление — B/05.
- [S23] Банк России · курсы валют на 23.09.2026 (`XML_daily`, USD 84,0657) — `99-raw/experiments/P/02-kie-vs-polza/cbr_2026-09-23.xml`.
- [S24] OpenRouter · `https://openrouter.ai/api/v1/models` (23.09.2026) — цены GPT-5 Image/Mini, GPT-5.4 Image 2, Gemini
  Image = цены провайдера `openai`/Google в polza ÷ 117,992.
- [S25] Google · Gemini API pricing `ai.google.dev/gemini-api/docs/pricing` (23.09.2026) — токены на картинку по
  разрешениям (NB2 1K 1120, 2K 1680, 4K 2520; NB Pro 1–2K 1120, 4K 2000).
- [S26] OpenAI · image generation guide (developers.openai.com, 23.09.2026) — токены gpt-image-1 (1024² low 272 /
  medium 1056 / high 4160).
- [S27] polza · `api-reference/audio/transcriptions.mdx` (код `RESULT_EXPIRED`), `api-reference/systemone/create.mdx`
  (`trace_id`, `detail.error_type`, «429 SDK повторяют сами»).
- [S28] polza · `osobennosti/reasoning-tokens.mdx` — хост `api.polza.ai` в примере.
- [S29] polza · `api-reference/chat/completions.mdx`, `responses/create.mdx` — `modalities`, `image_config`
  (картинки через chat/responses; для NB2 GA — гипотеза).
- [S30] Опыты агента B: `99-raw/experiments/B/01-mock-server` (макет, 30/30), `02-price-calculator`,
  `03-catalog-snapshot-diff`, `04-job-validation`, `05-polza-vs-kie-fx`, `06-phase5-smoke-plan`.
