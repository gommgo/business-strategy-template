# 15-tools-atlas — атлас моделей, каналов, сервисов и инструментов

Волна 3 · агент N · 24.09.2026. Что существует, почём, живо ли, доступно ли из РФ и где в базе описано. Атлас — справочник;
**маршрут** «задача → модель» — в `../13-routing-matrix/routing.yaml` v1 и `03-routing-matrix.md`, обновление — там же `04`.

## Файлы

| Файл | Строк | О чём |
|---|---|---|
| `01-models-and-providers.md` | 201 | каналы доступа (polza, RouterAI, Gen-API; KIE, fal, Replicate, Runware, Recraft, Runway — вне доступа), 24 модели картинок и 22 видео polza с ценами 24.09 и живостью, модели вне polza, 13 сервисов из роликов (API, доступ из РФ, решение), открытые веса и лицензии |
| `02-tools-libraries-cli.md` | 159 | 20+ утилит базы (версии, проверка, владелец), бинарники и CLI (ffmpeg 7.1.5, libavif 1.4.2, libjxl 0.12.0, libwebp 1.6.0, c2patool 0.27.22, exiftool 13.59, vtracer, potrace, Real-ESRGAN, RIFE, Chrome for Testing 153), venv и npm-пакеты с лицензиями, локальные модели (u2netp, isnet, Depth Anything V2 Small, PP-OCRv5), данные, инструменты по слоям конвейера |

## Выжимка на 10 строк

1. Рублёвые каналы — polza (один баланс на Media API, chat и `/v2/images`), RouterAI и Gen-API; остальное — иностранная оплата.
2. Второй канал нужен ради возможностей (Recraft-вектор, `background`, маска, FLUX.2 без переписчика), не ради цены.
3. Цены каналов меняются ежедневно с курсом (RouterAI +0,39 % за 23→24.09) — брать из снимка дня.
4. В polza 18 рабочих моделей картинок и 7 ключевых видео; снимаются `openai/gpt-5-image` (23.10), `gpt-image-1.5` (01.12), preview Omni (30.09); Sora 2 снят.
5. Новые за сутки: GA Omni 1.1 Flash (FLF полями), Grok Image 2.0, RouterAI Recraft V4.1 Flash (0,77 ₽) и Ming Design Layer — мини-стенд до маршрута.
6. Из 13 сервисов роликов по API годятся Quiver, Higgsfield, Flora, Bria, Topaz, Beeble — все за иностранную оплату; Weave, Pics, Lottie Prompt to Vector, HeroUI — только интерфейс.
7. Открытые веса: u2netp, BiRefNet, Depth Anything Small, Qwen-Image-Layered — да; Qwen-Image-2.1, RMBG-2.0, FLUX.2 dev/klein — нет.
8. Утилиты базы работают без сети и ключей; `--live` — только с заказчиком; тяжёлое — под `flock`.
9. Кодирование по метрике (SSIMULACRA2, `motion_keep`), провенанс — c2patool + exiftool + `provenance_check.py`.
10. GPL-инструменты (potrace, potracer, exiftool-сборка) — внешний шаг конвейера, не часть продукта клиента.

После атласа (24.09.2026, X): `../../scripts/maint/check_links.py` — проверка ссылок, разделов §, `[S#]`, `[V:id мм:сс]`, README папок и меток
`[проверено: …]` (7 проверок; описание — `../../scripts/ai-media/README.md`); самопроверки всех утилит повторены X — всё воспроизводится
(`mp_client.py` 35/36 и макет каналов 41/44 — из-за снимка RouterAI 24.09, клиент не сломан; `../99-raw/reports/wave4-X-audit.md` §1).
