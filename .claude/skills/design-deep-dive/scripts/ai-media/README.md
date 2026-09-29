# Утилиты ai-media-research

Все пути — от корня `kb/ai-media/` (от корня скилла). Проверены оркестратором 23.09.2026 на этой
машине (Debian 13, 20 потоков, 15 ГБ ОЗУ, Intel Iris Xe без CUDA, Vulkan 1.4 через Mesa; Python 3.13, Node 24.21,
ffmpeg 7.1.5, Pillow 11.3 с AVIF/WebP, Playwright + Chromium, uv, pandoc 3.1, yt-dlp 2026.08.18).

## Веб и видео (скопированы из `../../kb/blender`, формат тот же)

| Утилита | Что делает | Пример |
|---|---|---|
| `fetch.py` | Скачивает страницу в читаемый Markdown в `99-raw/cache/`, PDF — через `pdftotext`; для w3.org подставляет UA curl | `python3 99-raw/tools/fetch.py "URL"` |
| `render_fetch.py` | То же через headless-браузер: SPA-документация, блоги на JS, арены | `python3 99-raw/tools/render_fetch.py "URL" --scroll [--html]` |
| `yt_transcript.py` | Поиск по YouTube без API, метаданные, субтитры с таймкодом раз в минуту → `91-videos/transcripts/<id>.md` | `--search "запрос" -n 20`, `--info URL`, `URL --comments 40` |
| `vtt2md.py` | Собирает транскрипты из уже скачанных `.vtt` и `.info.json` без обращения к YouTube | `python3 99-raw/tools/vtt2md.py ids.txt` |
| `site_probe.py` (`../blender/`) | Замер страницы с 3D: переданные байты по категориям и сигнатурам, LCP с элементом, TBT, контексты WebGL/WebGPU, прокрутка колесом, `--mobile` (Pixel 7), `--throttle`, `--reduced-motion`, `--no-3d`; ворота — `gate_check.py` | `../blender/site_probe.py https://site out/ [--mobile] [--throttle] [--reduced-motion]` |

## Субтитры YouTube без HTTP 429 (способ агента V, опыт `99-raw/experiments/V/01-video-catalog/`, 23.09.2026)

Проверено: **110 загрузок подряд — 110 успешных, 0 ответов 429** (09:06–09:59). В блендер-ресёрче накануне обычный
способ (`--sub-langs "en.*,ru.*"`, несколько дорожек за запрос) давал 0 файлов: YouTube считает лимит по запросам к
timedtext (каждая дорожка — отдельный запрос), а не по роликам.

Правила способа:
1. **Метаданные отдельно** — `yt-dlp --skip-download --write-info-json` (timedtext не трогается).
2. **Ровно одна дорожка на ролик**, выбранная по метаданным: ручные субтитры на языке оригинала → автоматические
   `<язык>-orig` → ручные en/ru. Никаких масок вида `en.*`.
3. **Ссылка на дорожку — из сохранённого `info.json`** (`--load-info-json`), а не новым запросом страницы; если ссылка
   истекла (`expire=` в URL) — метаданные перекачиваются.
4. **Пауза 6 с** между роликами; при 429 — пауза 90 с и 120 с с повтором; после трёх роликов подряд с 429 — остановка
   (перезапуск идемпотентен: готовое пропускается).
5. JS-рантайм yt-dlp: `--js-runtimes node:$(command -v node)`.

| Утилита | Что делает | Пример |
|---|---|---|
| `yt_dl.py` (копия V/01 `dl.py`, пути от расположения файла) | `meta` — только метаданные; `subs` — одна дорожка на ролик по правилам выше; `comm` — 100 верхних комментариев; `pick` — показать выбор дорожки без сети. Файлы — в `99-raw/youtube/{meta,subs,comments}/`, журнал — `99-raw/youtube/yt_dl.log` | `python3 99-raw/tools/yt_dl.py meta ids.txt && python3 99-raw/tools/yt_dl.py subs ids.txt` |
| `vtt2md.py` (пути исправлены оркестратором 23.09 — были жёстко на blender-research) | Транскрипты `91-videos/transcripts/<id>.md` из скачанных `.vtt` и метаданных, без обращения к YouTube | `python3 99-raw/tools/vtt2md.py 99-raw/youtube/ids_all.txt` |

Метаданные в `99-raw/youtube/meta/` ужаты (удалены временные ссылки на потоки и дорожки, 480 → 3,5 МБ): `yt_dl.py
subs` в этом случае сам перекачивает метаданные ролика перед загрузкой дорожки.

## Цвет (скопирован из `../../kb/ui`)

| Утилита | Что делает | Пример |
|---|---|---|
| `color.py` | WCAG 2 и APCA, hex ↔ OKLCH, ΔE, симуляция дальтонизма, композитинг альфы; `selftest` | `python3 ../lib/color.py selftest` |

## polza: клиент и каталог (агент B, волна 1, 2026-09-23)

Python 3.13, только стандартная библиотека. Проверено: макет polza — 30/30 сценариев
(`99-raw/experiments/B/01-mock-server`), калькулятор — 84 случая (`B/02`), валидатор — 51 ловушка (`B/04`).
**Против настоящего polza не запускались** (ключа нет до фазы 5). Подробно — `../../kb/ai-media/02-providers-platforms/01-polza-api.md` §12.

| Утилита | Что делает | Пример |
|---|---|---|
| `polza.py` | Клиент Media API: проверка задания по каталогу, приведение типов, явная подстановка ценовых default, оценка цены, **сухой прогон по умолчанию** (точный запрос, `--curl`), `--live` — отправка с `"async": true`, опрос, немедленное скачивание, паспорт `.passport.json`, журнал `99-raw/experiments/_ledger.jsonl`, кэш по хэшу запроса, лимиты (на задание, общий, на агента), предполётный `/v2/balance` + `/v1/key`, серия ≤ 3 параллельно, повтор POST только при 429 | `python3 polza.py run job.json` → `… --live` |
| | подкоманды: `models [--type] [--search] [--fresh]`, `show MODEL [--provider]`, `estimate JOB(.jsonl)`, `run JOB`, `batch JOBS.jsonl [--parallel 2]`, `status ID`, `download ID`, `upload FILE [--permanent]`, `ops ID extend\|upscale_1080p\|upscale_4k [--params]`, `ledger [--sum] [--agent]`, `balance`, `history ID` | `python3 polza.py ledger --sum` |
| `polza_catalog.py` | Снимок публичного каталога (`/v1/models`, `?include_providers=true`, `/v1/models/catalog`) в `99-raw/cache/polza/<дата>[_ЧЧММ]/` без перезаписи, нормализация медиа-моделей (`media-models.normalized.json`), Markdown-таблица, `diff` двух снимков, калькулятор цены и проверка входа (библиотека для `polza.py`), `selftest` (закреплён на снимке `2026-09-23`). 25.09.2026 (агент U): в перекрёстное правило `mie` (разрешения GPT Image 2.x по `aspect_ratio`) добавлен новый id Flare `openai/gpt-image-2.5-flare` (старый `gpt-image-2-5-flare` оставлен для старых снимков) + проверка правила в `selftest`: до правки 19/19, после — 20/20; `selftest --snapshot 2026-09-25_1411` — 18/20 (Wan 3.0 и H3 Max +0,69 % — курс долларового провайдера, не подгонялось) | `python3 polza_catalog.py snapshot && python3 polza_catalog.py diff 2026-09-23 latest` |

Задание: `{"model": "tongyi-mai/z-image", "input": {"prompt": "…", "aspect_ratio": "16:9"}, "tag": "t1", "agent": "E",
"notes": "…", "variant": 1, "max_rub": 2, "provider": {"only": ["mie"], "allow_fallbacks": false}}`; серия — JSONL.
Файлы в `images`/`videos`: URL, `data:`, локальный путь (≤ 4 МБ — base64, больше — загрузка в хранилище) или
`{type, data}`. Поля-ссылки `mask_url`, `first_frame_url`, `last_frame_url` (GA `google/gemini-omni-1.1-flash`): URL или
локальный путь **относительно файла задания** → перед отправкой `POST /v1/storage/upload` (TEMP_UPLOAD 24 ч), в теле — URL;
один файл в двух полях ([A,A]) грузится один раз; нет файла — ошибка задания (правка оркестратора 23.09.2026 19:10: раньше
`mask_url` искался от текущей папки и из корня проекта уходил в API строкой пути; проверено — макет B/01 30/30 и отдельный
живой прогон по макету из корня проекта: загрузка +1, в паспорте URL хранилища). Окружение: `POLZA_API_KEY` или `~/.config/polza/api_key` (600), `POLZA_BASE_URL`, `POLZA_CATALOG`,
`POLZA_LEDGER`, `POLZA_OUT_ROOT` (`99-raw/experiments/_polza/<агент>/<дата>/`), `POLZA_BUDGET_TOTAL` (2000),
`POLZA_BUDGET_AGENT`, `POLZA_MAX_JOB` (60). Коды выхода: 0 успех; 1 задание; 2 бюджет; 3 таймаут опроса; 4 failed;
5 HTTP; 6 скачивание. Ключ не печатается и не пишется в журнал и паспорта.

Быстрые справки без сети: `polza.py show kling/v3` (параметры, сетка цен, провайдеры, расхождения);
`polza_catalog.py price bytedance/seedance-2 resolution=480p duration=5` (цена с формулой);
`polza_catalog.py check qwen/image-2.1 background=transparent output_format=jpeg` (ошибки до отправки).

## Инвентарь визуальных ассетов сайта — `asset_inventory.py`

Python окружения скилла (`$DDD_HOME/venv`) + Playwright/Chromium + Pillow. Автоматизацию не маскирует: UA как есть
(десктоп — строка Playwright с `HeadlessChrome`, телефон — дескриптор Pixel 7 с `HeadlessChrome`), признак автоматизации
Blink не выключается, `navigator.webdriver` не трогается; вход, капча и антибот — отсев страницы, а не обход.

| Что | Как |
|---|---|
| Запуск | `python3 asset_inventory.py URL OUT_DIR [--mobile] [--reduced-motion] [--quick] [--throttle] [--wait 6000] [--timeout 90] [--steps N] [--wait-until load\|domcontentloaded\|commit] [--dpr 1] [--no-og] [--keep-shots]` |
| Самопроверка | `python3 asset_inventory.py --selftest` — локальная страница `file://`, без сети: UA и `navigator.webdriver` страницы, признаки GSAP, телефон |
| Сценарий | десктоп 1440×900 DPR 1 или `--mobile` = Pixel 7 (412×839, DPR 2,625); `load` → ожидание → 2 кадра (движение в покое) → прокрутка колесом с кадрами → наверх → DOM-инвентарь; `--quick` — без прокрутки |
| Результат | `<OUT_DIR>/inv<суффикс>.json` — суффикс по ключам: `_mobile`, `_thr`, `_rm`, `_quick` (в инвентаре `ua` и `webdriver` — как страница видит клиента), контактный лист `sheet<суффикс>.jpg` (JPEG, 4 кадра), JSON-сводка в stdout |
| Картинки | `<img>`/`<picture>`: currentSrc, `srcset` (число, w/x), `sizes`, `<source type/media>` (арт-дирекшн), `loading`, `fetchpriority`, `decoding`, `alt` (нет/пустой/текст), естественный и отрисованный размер, переотдача, первый экран, слот |
| CSS | `background-image`/`mask-image` элементов и `::before/::after` (url и крупные градиенты) |
| Видео | источники и `type`, `poster`, `autoplay muted loop playsinline preload controls`, играет ли, длительность, размер кадра, кнопка паузы рядом (эвристика по доступному имени) |
| SVG, Lottie, canvas | inline SVG (иконка / логотип / иллюстрация, байты разметки), Lottie (lottie-web, `lottie-player`, dotLottie, JSON), Rive, canvas с типом контекста (WebGL/WebGPU/2D), iframe-видео |
| Библиотеки | по рантайму: GSAP и ScrollTrigger — `window.gsapVersions`, свойство `_gsap` у элементов, `.pin-spacer` (бандл глобал `window.gsap` не ставит; метод — `../../kb/creative/03-live-sites-measured/01-effects-sites-measured.md` §1.1), поля `gsap_versions`, `gsap_targets`, `pin_spacers`; three.js, Lottie, Rive, Webflow, Framer, Next, Nuxt, Shopify |
| Сеть | байты «на проводе» — максимум из Playwright и **CDP Network** (Range-запросы видео, HLS/DASH/CMAF, `blob:`); формат по сигнатуре; размеры файла (Pillow); вес до и после прокрутки |
| Метрики | LCP **до прокрутки** с элементом и ассетом (`lazy`, `fetchpriority`), CLS, TBT (long tasks), движение в покое, og:image (скачивается), фавиконы, preload |

Разбор hero-видео (шов петли `seam_ratio`) — `video_loop_check.py`, метрики маркеров картинок — `image_metrics.py`.
Ограничения: HEVC в этом Chromium не играет; куки-баннеры не закрываются; антибот отдаёт заглушку (смотреть `title` и
контактный лист); один браузер за раз.

## Стенд моделей — `stand_run.py`

| Утилита | Что делает | Пример |
|---|---|---|
| `stand_run.py` (`selftest` — 12 проверок) | стенд моделей поверх `polza.py`: `build` (задачи `../../kb/ai-media/13-routing-matrix/stand/tasks.yaml` через компилятор промтов), `estimate`, `run`, `collect`, `metrics`, `sheet` (контактные листы), `page` — **страница слепого попарного голосования**: картинки из таблицы результатов или **текстовые карточки** из листа `copydeck.py export-variants` (`--text ЛИСТ.md --text-key КЛЮЧ.yaml`, пары — между вариантами одного слота); ключ — `<DIR>.key.json` рядом с папкой страницы; `tally` (доли побед, Уилсон, Брэдли–Терри, повторы, позиция; у текстовой страницы `--selection` — победы меток по слоту для `copydeck.py apply-selection --votes … --method human-pairwise`), `ministand` (прогон новой модели на регрессионном наборе) | `python3 stand_run.py page --text sheet.md --text-key key.yaml --out page/` → голоса → `stand_run.py tally votes.json --key page.key.json --selection votes.yaml` |
| `routing_check.py` (агент N, волна 3, 24.09.2026; v1.1 — агент U, 25.09.2026; 424 строки) | валидатор `../../kb/ai-media/13-routing-matrix/routing.yaml` v1/v2 по последним снимкам каталогов: id моделей есть в polza / RouterAI / Gen-API или помечены внешними, параметры проходят проверку каталога, цены совпадают с `polza_catalog.py price` (± 1 %), каналы, диалекты, рубрики `../../kb/ai-media/11-evaluation-qa/rubrics/`, флаги `legal` (Qwen 2.1 не финал; с 24.09 X2 — `minimax/*` только с `visible-vendor-mark`, строки политики 12–14 — флаг маршрута `people-consent`), тесты фазы 5; предупреждает об устаревающих моделях. 24.09: 33 маршрута, 124 варианта — 0 ошибок; отрицательный тест 9/9 (`99-raw/experiments/N/01-routing-check/`) + 2/2 новых правил (`99-raw/experiments/X/06-x2/routing_check_negative_x2.py`). Запускать после каждого снимка каталога и перед фазой 5 (`../../kb/ai-media/13-routing-matrix/04-update-procedure.md` §2). **v1.1 (агент U, сессия 5, 25.09.2026)**: `version` 1 или 2; коды тестов с цифрой в начале и трёхбуквенные (`3D-21`, `VAR-01`); `defaults.unavailable_<дата>` — выбывшая модель вариантом только с `final: false` или в `not`, у записи обязательны `model` и `error`; `defaults.not_routes` — у записи `what` и `why`. 25.09: `routing.yaml` v2 — 33 маршрута, 136 вариантов, 0 ошибок, 0 предупреждений (снимки `2026-09-25_1411`); v1 (`routing.v1.yaml`, снимки 24.09) — 0 ошибок; отрицательный тест v1.1 — 6 поломок → 7 ошибок, все пойманы (`99-raw/notes/session5/U-work/routing-negtest/`) | `python3 routing_check.py ../../kb/ai-media/13-routing-matrix/routing.yaml --md report.md --json report.json` |

## Будут добавлены агентами

- ~~`polza.py`, `polza_catalog.py` (агент B)~~ — готово, раздел «polza» выше.
- Компилятор промтов из спецификации ассета (агенты D и D2), `asset_audit.py` и VLM-критик (агент K, волна 3).
- Транскрипция на GPU-сервере (`asr_feed.py`, `asr_server.py`, `whisper2md.py`) — копируются из блендер-ресёрча
  **только после сигнала**, что его конвейер устаканился (решение заказчика 23.09.2026).

## Правила

- Python-пакеты — только в venv внутри `99-raw/tools/` (`uv venv 99-raw/tools/venv-<имя>`); npm — в
  `99-raw/tools/node`; бинарники — в `99-raw/tools/bin/`; `sudo` запрещён.
- Ключи API не хранить в репозитории и не печатать; ключ polza — в `~/.config/polza/api_key` (права 600), появится к
  фазе 5.
- Платных вызовов в волнах 1–4 нет (решение заказчика); бесплатен только `GET https://polza.ai/api/v1/models`.

## Локальные бинарники и окружение постобработки (помощники агента P, волна 1, 23.09.2026)

Поставлены без sudo, проверены агентом P на этой машине (подробности — `../../kb/ai-media/02-providers-platforms/05-open-weights-landscape.md`
и `99-raw/notes/wave1/P-notes.md`). Тяжёлые прогоны — по одному и после `free -g`: разовый BiRefNet занял 6,5 ГБ и ушёл
в своп.

| Путь | Что | Назначение |
|---|---|---|
| `99-raw/tools/bin/realesrgan-ncnn-vulkan/` | Real-ESRGAN (ncnn, Vulkan на Iris Xe) | апскейл картинок и кадров локально, альтернатива Topaz |
| `99-raw/tools/bin/rife-ncnn-vulkan/` | RIFE (ncnn, Vulkan) | интерполяция кадров (стык петли, плавность) |
| `99-raw/tools/bin/sd-cpp-vulkan/` | stable-diffusion.cpp (Vulkan) | проба локальной генерации — на этой машине для продакшна не годится (вывод P) |
| `99-raw/tools/venv-p10/` (506 МБ) | Python-окружение с ONNX-моделями постобработки (удаление фона, карта глубины) | опыты H и I волны 2 |

## Вектор и SVG (агент G, волна 2, 23.09.2026)

Поставлены без sudo, проверены агентом G на этой машине. npm-пакеты — общие в `99-raw/tools/node` (ставить под
`flock -w 600 99-raw/tools/.locks/npm.lock npm install --prefix 99-raw/tools/node …`, чтобы соседи не ставили одновременно).

| Путь | Версия | Что | Пример |
|---|---|---|---|
| `99-raw/tools/node/node_modules/@resvg/resvg-js` | 2.6.2 | рендер SVG → PNG без браузера (Rust resvg, точный, быстрый; без CSS-анимаций и `<foreignObject>`) | `node -e "…new Resvg(svg,{fitTo:{mode:'width',value:96}}).render().asPng()"` |
| `99-raw/tools/node/node_modules/.bin/svgo` | 4.1.0 | оптимизация SVG (пресет `preset-default`; в v4 `removeViewBox` и `removeTitle` выключены по умолчанию) | `99-raw/tools/node/node_modules/.bin/svgo in.svg -o out.svg` |
| `99-raw/tools/node/node_modules/lucide-static` | 1.47.0 (ISC) | эталонные иконки Lucide (SVG, `icon-nodes.json`, `tags.json`, спрайт) для сравнения с самодельными | `…/lucide-static/icons/<name>.svg` |
| `99-raw/tools/node/node_modules/lottie-web`, `@lottiefiles/dotlottie-web` | 5.13.0 / 0.80.0 | плееры Lottie — для замера веса и проверки LLM-написанного Lottie в Chromium (опыт G/05) | `…/lottie-web/build/player/lottie_light.min.js` (168 КБ, 46 КБ gzip) |
| `99-raw/tools/bin/vtracer-1.0.0a4/vtracer` | 1.0.0-alpha.4 (musl, 29.08.2026) | векторизация растра: `--palette '#hex,…'`, `--palette-file`, `--max-colors N`, `--simplify`, `--optimize 0-2`, `--preset bw|poster|photo`, `--clustering watershed` | `vtracer -i in.png -o out.svg --palette '#0f172a,#e2e8f0' --simplify 1.5 --optimize 2` |
| `99-raw/tools/bin/potrace-1.16/potrace` (+ `mkbitmap`) | 1.16 (GPL, официальная сборка) | трассировка ч/б растра (PBM/BMP) в SVG | `potrace in.pbm -s -o out.svg --turdsize 2 --alphamax 1 --opttolerance 0.2` |
| `99-raw/tools/venv-G/` (237 МБ, Python 3.12) | vtracer 0.6.15, potracer 0.0.4, svgelements 1.9.6, cairosvg 2.9.1, scikit-image 0.26, numpy 2.5, Pillow 12.3 | Python-обвязка векторизации, разбор путей SVG (bbox, узлы), метрики | `99-raw/tools/venv-G/bin/python script.py` |

Скрипты проверки иконок и векторизации — в `99-raw/experiments/G/` (описание — в README опытов и в `../../kb/ai-media/07-vector-svg-icons/`).

## Компилятор промтов и анализ A/B (агенты D2 и D2b, волна 2, 2026-09-23)

Окружение — `99-raw/tools/venv-D2/bin/python` (Python 3.13, jsonschema, PyYAML, Pillow, numpy, scipy); без jsonschema схема не
проверяется (предупреждение). Тесты: `venv-D2/bin/python tests/test_prompt_compile.py` — **98/98** (v2.1); тесты D
волны 1 — 30/30; регресс v1 → v2 — `99-raw/experiments/D2/01-compiler-v2` (850 случаев: 657 без изменений; 57 «чистых»
ожидаемых отличий, 122 — в недопустимых парах «картинка × видео-модель»; параметры — 100 %). **Снимок каталога — последний** (`polza_catalog.find_snapshot`, как у `polza.py`; на 23.09 — `2026-09-23_1745`);
закрепить старый — `POLZA_CATALOG=2026-09-23`.

| Утилита | Что делает | Пример |
|---|---|---|
| `prompt_compile.py` v2.1 | спецификация (`../../kb/ai-media/05-prompting/asset-spec.schema.json` v0.2) → промт в диалекте семейства (`dialects.yaml` v0.4 — с 25.09.2026: `ab_results` фазы 5, новый id Flare; тесты 98/98 и 15/15) + параметры; проверка входа `polza_catalog.validate` и цена `estimate` (одна точка истины с `polza.py`); ценовые параметры явно (`image_resolution`/`resolution` — самая дешёвая ступень, `mode` Kling, `quality` Seedream, `generationType` и `enableTranslation: "false"` Veo, звук `false`); правки порциями и маски с полярностью модели; референсы с ролями; серии; продукт из 7 блоков; видео: фоновое движение, неподвижное, запреты, темп, мульти-шот, IR H3; паспорт компиляции в `meta.compile`; задания polza.py и `.routerai.json` / `.genapi.json` | `compile SPEC --model qwen/image-2.1 [--opt order=product7]`; `jobs SPECS --models … --dialects sections,json --test D2-01 --agent D2 --out …`; `jobs … --channel genapi`; `chain SPEC --model …`; `ratios SPEC`; `matrix SPECS` |
| | совместимость: команды и функции v1 те же; текст промта спецификаций v0.1 не меняется, кроме исправлений (объявление референса E2, `series_block` в JSON, bbox Ideogram, фраза неподвижной камеры Wan); FLF только у семейств с документированным последним кадром (veo, omni, seedance-1.5, kling, minimax-h3), иначе i2v | |
| | **v2.1 (D2b, вечер 23.09)**: GA Omni `google/gemini-omni-1.1-flash` — кадры полями `first_frame_url`/`last_frame_url` (в задании — локальный путь + `meta.url_fields`, перед запуском `polza.py upload … --live`), без тегов preview; референсы одной роли — одной фразой («Images 1-3 are style references…»); без повтора позитивных замен; поверхность зоны без артикля; метка серии не дублируется (4 замечания F2); «против среднего» по частям (взгляд — только у людей, несовершенства — только у фото; «по центру» + правило — ошибка); смешанные правки `edit.changes[].op` (add / remove / replace / recolor); `motion.camera.target` (Kling «fixed on …»); предупреждения: звук без параметра (→ `-an`), Kling мульти-шот ≤ 6 планов и ≤ 512 символов, только стартовый кадр; таймкоды Seedance 2.5 — целые секунды без разрывов; фраза одного плана Wan «Generate a single-shot video»; планы и отрезки таймлайна — с точками; у видео запреты последними; при равной цене — ступень разрешения ≥ запрошенной (GA Omni 480p → 720p) | `compile SPEC --model google/gemini-omni-1.1-flash`; примеры видео — `99-raw/experiments/D2/03-phase5-jobs/video_examples.py` |
| | **v2.1.1 (X2, 24.09.2026)** — дефекты стыка из демо M: поверхность зоны без повторного «empty/uncluttered»; `edit.keep` без «the the»; `subject_motion`/`environment_motion` с заглавной; «Keep its position…» только после замены объекта (не у relight — задание M-06 пересобрано); `ratios`: без `safe_zones` — кроп по зоне текста и фокусу (раньше весь кадр неприкосновенен → ложный аутпейнт), соотношения из `output.variants`, потеря зоны текста — в `note`; `focal_point` списком — ошибка схемы вместо `TypeError`. Тесты: `tests/test_prompt_compile_x2.py` **15/15** (на v2.1 — 3/15), основные 98/98, D 30/30 (вывод побайтно тот же), регресс D2/01 — `regress_v1.txt` тот же, стенд E `build` — 17 файлов побайтно те же; регресс v2.1 → v2.1.1 по 2 490 случаям — `99-raw/experiments/X/06-x2/pc_regress_x2.py` (текст изменился только у M-06) | `venv-D2/bin/python tests/test_prompt_compile_x2.py -v` |
| | **Сессия 5 (25.09.2026, оркестратор)** — ошибка компиляции в CLI (модель канала вне `dialects.yaml` — Qwen Image 3, Krea 2, Recraft Pro Vector, Hunyuan Image V3 и др.) выводится одной строкой «ошибка компиляции: …», код выхода 2, без трассировки; описания этих моделей в `dialects.yaml` (`channels`) нет — задание для следующей сессии (список — корневой README «Что осталось»). Тесты 98/98 и 15/15 — те же | `prompt_compile.py compile SPEC --model qwen/qwen-image-3 --channel routerai` → код 2 |
| `ab_analyze.py` | A/B формы промта: `simulate` (мощность), `manifest` (паспорта polza.py → манифест), `judge-jobs` (судья вслепую, `.polza-chat.json`), `metrics` (ΔE палитры OKLab, пустота зоны текста), `analyze` (парные разности, бутстреп по брифам, правило ≥ 10 п. п. и ДИ > 0, разброс, YAML для `ab_results`), `selftest` **Поправка сессии 5 (25.09.2026, оркестратор)**: `decide` выносит «плечо хуже» только при Δ ≤ −10 п. п. **и верхней** границе ДИ < 0 (раньше проверялась нижняя — «хуже» выносилось при ДИ через 0); `selftest` + 4 случая правила. | `python3 99-raw/tools/ab_analyze.py selftest` |

## Видео: приёмка петель, синемаграфов и хромакея (агенты I и I2, волна 2, 23.09.2026)

Python 3.13 + numpy + scipy + Pillow (системные) + ffmpeg 7.1.5; ΔE00, SSIM и фазовая корреляция импортируются из
`edit_check.py` (агент H). Вход — видеофайл или папка кадров. Выход — JSON в stdout. `selftest` — PASS (синтетика, 11
случаев). Версия 0.2 (I2): локальный шов и локальная склейка, относительная неподвижность, детектор пинг-понга, цвет
неподвижных зон в `drift`, исправлена потеря последнего кадра в `trim` [проверено: `99-raw/experiments/I/02-loop-seam`].

| Утилита | Что делает | Пример |
|---|---|---|
| `video_loop_check.py` | `loop` — шов: `seam_ratio` (к медиане всех пар, как в A/02 и C2) и `seam_ratio_local` (к 3 парам у каждого конца — верен при неравномерном движении, например обороте); «живость» (`motion_med`, с `--control` — `motion_vs_control`, `curve_corr`); склейка — локальный пик `cut_ratio` (глобальный — `cut_ratio_global`); угасание (`head/tail_motion`, `collapse_suspect`); `static_frac` — доля пар < 0,25 медианы (`static_abs_frac` — прежняя абсолютная, < 0,5 уровня); `pingpong_suspect` (`mirror_ratio` < 0,25 — кадры симметричны во времени); дубль последнего кадра и мёртвые концы → срез и шов после среза; лучшая точка реза; сдвиг камеры; ΔE00 стыка. `trim --auto` — срез (без звука, мезонин без потерь x264 `-qp 0` в формате исходника — с 0.2.1, X2 24.09.2026: CRF 10 давал ложный шов чистой петли 0,96 → 2,12 (K/03 c08); `-r` исходника, faststart, `ok` = число кадров сошлось); `drift --mask` — дрейф неподвижных зон + `dE00_max/last` цвета зоны; `chroma` — однородность фона-ключа и дрейф объекта; `join` — стык клипов цепочки; `sheet` — контактный лист; `colormatch` — подгонка цвета конечного кадра FLF (OKLab) | `python3 video_loop_check.py loop clip.mp4 --control control.mp4` |

Пороги приёмки (предложение, калибровать в фазе 5): `seam_ratio_local` после среза ≤ 1,5; `cut_ratio` < 10;
`tail_motion` ≥ 0,5; `motion_vs_control` ≥ 0,5 (единственный признак равномерно слабого движения); `seam_ratio` ≈ 0 =
дубль кадра (микропауза), а не идеальный шов. **Мерить шов на мезонине до финального кодирования**: у тихой петли
(`motion_med` ≈ 0,1–0,2, уровень Notion/Seasats) H.264 даёт «пульс» ключевого кадра — `seam_ratio` идеальной петли
0,98 → 3,4 после CRF 12, дубль кадра после кодирования уже не виден (I/02, I/04). `cam_shift_max_px` на ровном фоне
(хромакей) показывает движение объекта, а не камеры — там смотреть `chroma`.

## Паспорт визуала — `vlm_to_dna.py`

Python окружения скилла (`numpy`, `Pillow`, `jsonschema`; без jsonschema — встроенный валидатор подмножества JSON Schema).
Схема — `../../kb/ai-media/06-art-direction-consistency/visual-dna.schema.json`, примеры —
`../../kb/ai-media/06-art-direction-consistency/examples/dna-*.json`. Разбор сетки бренда делает отдельная сессия Opus — агент
`design-judge` по пакету той же формы, что пакет судьи (`asset_audit.py judge-jobs`); утилита собирает пакет и читает
ответ, моделей сама не вызывает. Паспорт утверждает человек.

| Утилита | Что делает | Пример |
|---|---|---|
| `vlm_to_dna.py grid` / `build` | сетка бренд-картинок (белые желоба 10 px) → пакет формы judge-package/1 в `$DDD_HOME/out/ai-media/dna/<имя>/`: кадр сетки PNG, задание на прогон (`jobs/<id>.md` — рубрика брифа: характер, палитра, грейд, свет, камера, композиция, реквизит, блок стиля, запреты, канарейки), пустая `<имя>/answers/`; ключ с исходником сетки — рядом, `<имя>.key.json`; `--runs 2` — две сессии для сверки | `python3 vlm_to_dna.py build grid.jpg --name brand` |
| `parse` | ответы пакета (`answers/<id>.md`: первая строка и блок ```json) или файл ответа → черновик паспорта; по сетке из ключа — палитра, баланс белого и хрома, снятые с пикселей, критерий «≥ 3 из 5 hex в ΔE ≤ 0,05» и «придуманные» цвета (покрытие < 1/3 заявленной доли); два ответа и больше — сверка прогонов; `--art-direction` — ссылка на арт-дирекцию в происхождении | `… parse $DDD_HOME/out/ai-media/dna/brand --out dna.json` |
| `validate` | схема + линт: оттенки в запрещённых полосах, «no X» и оценочные слова в блоках стиля, «transparent background» в блоке, ярлык «Series style», замены запретов с предметами, объект и зона текста на одной стороне, референсы разных классов, p95 вместо p99,9, `icon3d` без ссылки на паспорт 3D-серии, повтор id и отсутствие списка метафор иллюстраций | `… validate dna.json` |
| `compare` | два прогона разбора: совпадение категорий грейда и света, симметричная ΔE палитр | `… compare run1.json run2.json` |
| `lut` | числа `grade` паспорта → 3D LUT `.cube` (`palette.parametric_grade`) | `… lut dna.json --out brand.cube` |
| `from-tokens` | токены DTCG (`color.bg.canvas`, `color.accent.solid`, `primitive.color.neutral.*`, радиус `radius` шага md) → скелет паспорта по правилам R1–R8; `icon3d` — материал и доля акцента, камера и свет — ссылкой на паспорт 3D-серии blender 06/02 §6 | `… from-tokens tokens.json --out dna.json --adjectives "строгий,плотный,технический"` |
| `to-spec` | паспорт → спецификация ассета (`../../kb/ai-media/05-prompting/asset-spec.schema.json`) для `prompt_compile.py`: блок стиля, палитра (сумма долей ≤ 1), свет, камера, зона текста, референсы одного класса, замены запретов | `… to-spec dna.json --kind photo --task IMG-HERO-PHOTO --subject "…" --out spec.json` |
| `selftest` | 33 проверки: пакет и разбор на синтетической сетке, примеры паспортов базы, сломанный паспорт, поля `icon3d` и иллюстраций, LUT, токены, спецификация (компиляция промта — при снимке каталога polza) | `python3 vlm_to_dna.py selftest` |

## Проверка правок и альфы, кодеры и C2PA (агент H, волна 2, 23.09.2026)

Системный Python 3.13 + numpy + scipy + Pillow (venv не нужен). Проверено на эталонных рендерах Blender
(`99-raw/experiments/H/00-reference-renders/`) и синтетике; самопроверка `edit_check.py selftest` — OK.
v0.2 (H2, 23.09.2026 17:50): исправлено грубое совмещение в `outpaint` (v0.1: масштаб 0,97 вместо 0,98 — до 15 px у края)
и заменён критерий резкости; имена `srgb_to_lab`, `de2000`, `ssim_map`, `phase_shift` не менялись (их импортирует
`video_loop_check.py`, его selftest — PASS). Удаление объекта с композитом — только широкая маска (+≈ 9 % стороны) и
`--feather` ≈ 3 % стороны, иначе «призрак» контура (`99-raw/experiments/H/03-edit-check/ghost_zone.py`).

| Утилита | Что делает | Пример |
|---|---|---|
| `edit_check.py check` | правка «на месте»: совмещение сдвигом (принимается, только если снижает ошибку вне цели), общий дрейф цвета (ΔE00 средних), карта ΔE00, `outside_leak_frac` (ΔE > 5 вне цели + полосы 6 px, после открытия 3×3; порог 0,02), `target_changed_frac`, SSIM зон, `edges_iou` (геометрия), `--protect` (товар: SSIM ≥ 0,9, ΔE медиана ≤ 5), `--match-color`, `--composite` (правка внутри маски, оригинал снаружи ровно) | `python3 edit_check.py check orig.png edited.png --mask target.png --mask-mode white --match-color --composite --out out/` |
| `edit_check.py polarity` | где реально менялось относительно маски → `white=edit` / `black=edit` | `… polarity orig.png edited.png mask.png` |
| `edit_check.py outpaint` (v0.2) | найти исходник в расширенном кадре: грубо на 256 px, затем масштаб шагом 0,05 % и субпиксельный сдвиг (ошибка ≤ 1–2 px на 1500 px); PASS = SSIM центра ≥ 0,9 **и** ΔE00 медиана ≤ 3 **и** `edge_sharpness` (Собель на сильных краях) ≥ 0,85, иначе REGENERATED — один SSIM перерисовку не ловит (0,993); `--composite` вставляет исходник обратно с субпиксельным сдвигом | `… outpaint hero_16x9.png extended_9x16.png --composite` |
| `alpha_check.py metrics` | альфа против эталона: IoU, MAE, ошибка в полосе края, ΔE00 композита на чёрном/белом | `python3 alpha_check.py metrics pred.png gt_alpha.png --rgb gt_rgba.png` |
| `alpha_check.py halo` / `fake` | ореол без эталона (порог 2 px); «нарисованная шахматка вместо прозрачности» | `… halo cutout.png --bg "#E8E8E8"`, `… fake out.png` |
| `tile_check.py` (H2) | бесшовность текстуры: `check` — `seam_ratio` (≤ 1,3 бесшовно, > 1,5 чинить), `cut --overlap 96` — тайл разрезом минимальной ошибки (органика), `preview` — сдвиг 50 % и плитка 2×2 | `python3 tile_check.py cut tex.png tile.png` |
| `avif_pick.sh` (H2) | минимальный AVIF (avifenc -s 6, 4:2:0), проходящий порог SSIMULACRA2: перебор q 35…85, декод, метрика; порог ≥ 80 hero, ≥ 70 второстепенные | `99-raw/tools/avif_pick.sh in.png out.avif 80` |

Бинарники (без sudo, `99-raw/tools/bin/`): `c2patool/c2patool` 0.27.22 (встроенный тестовый ES256; `--info`, `-p` родитель,
`-s` sidecar — файл не меняется; `-r URL` — ссылка в XMP `dcterms:provenance`, но манифест в 0.27.22 всё равно
встраивается (+14,5 КБ, H/04b)), `libjxl/tools/{cjxl,djxl,ssimulacra2,butteraugli_main,jxlinfo}` v0.12.0,
`libavif/{avifenc,avifdec}` 1.4.2 (aom 3.14.1 / dav1d), `libwebp/{cwebp,dwebp,webpmux,get_disto}` 1.6.0,
`exiftool/exiftool` 13.59 (perl). Модели (`99-raw/tools/models/`, 270 МБ): `rembg/u2netp.onnx`,
`rembg/isnet-general-use.onnx` (sha256 60920e99…), `depth/depth_anything_v2_small.onnx` (sha256 afb6a5c2…); для rembg —
`REMBG_HOME=99-raw/tools/models/rembg`, модель задавать явно (по умолчанию `bria-rmbg` — CC BY-NC). Тяжёлые прогоны — под
`heavy.lock`, `OMP_NUM_THREADS=4`. Генератор эталонных сцен (альфа, тень, подложка, глубина) —
`99-raw/experiments/H/00-reference-renders/make_refs.py` (только под `blender.lock`, всегда `--log` в свою папку: иначе
`blender_run.py` пишет журнал в `../../kb/blender/`).
Глубина (H/06): Depth Anything V2 Small ONNX на CPU — вход **518²** (кратно 14; 644² не точнее и в 2,2 раза дольше),
0,30 с и 0,48 ГБ на кадр, 4 потока; предобработка и метрики против эталона — `99-raw/experiments/H/06-depth/depth_eval.py`
(под `heavy.lock`).

## Каналы вне Media API polza — `mp_client.py`

Python 3.13, только стандартная библиотека (+ `polza_catalog.py` рядом). Исполняет задания генерации `<имя>.routerai.json(l)`,
`<имя>.genapi.json`, `<имя>.polza-chat.json`, `<имя>.polza-images.json` так же, как `polza.py` исполняет Media API: **сухой прогон по
умолчанию**, трата только с `--live`, проверка по каталогам и документации, оценка цены (ожидание и верх), лимиты, опрос,
немедленное скачивание, паспорт `<файл>.passport.json` рядом с файлом, **общий журнал** `$DDD_HOME/out/ai-media/_ledger.jsonl`
(поле `channel`). Правила и зонды первых вызовов — `../../kb/ai-media/02-providers-platforms/07-multichannel-client.md`.
Задание оценки по рубрике (`meta.judge: vlm` или `meta.rubric`) — ошибка задания: оценку делает сессия Opus по пакету
`asset_audit.py judge-jobs`. 3D-генераторы Gen-API (по имени сети или формату выхода каталога: glb, obj, fbx …) — ошибка
задания: 3D — Blender и код (`../../kb/blender/10-ai-3d-generation-assets/01-generators-landscape.md` §1).

| Канал | Что исполняет | Особенности клиента |
|---|---|---|
| `routerai` | `POST /api/v1/images` (синхронно, `b64_json`/`url`, SVG Recraft), `POST /api/v1/videos` (202 → опрос → `unsigned_urls` с ключом), `/api/v1/chat/completions` | проверка по каталогу RouterAI (`supported_*`, `max_image_*`), форма `input_references`/`mask`, passthrough против `allowed_passthrough_parameters` OpenRouter; цена: картинка / Мп / токены GPT Image / секунды видео |
| `genapi` | `POST /api/v1/networks/{slug}` → опрос `/api/v1/request/get/{id}`; `is_sync` | проверка по каталогу `networks?include=parameters` (`required`, `items`, типы `url_or_file`, `RGB`); `translate_input` явно (нет в задании → `false`); `recraft-v4` без `model`/`pro` — ошибка; 3D-сети — ошибка; цена по прайсу (flux-2 за Мп, recraft-v4 по варианту) или `cost` каталога |
| `polza-chat` | `POST /api/v1/chat/completions` | генерация (LLM → SVG); картинки на вход — data:URI; цена по токенам каталога; без `max_tokens` — потолок по `max_rub` (`--no-auto-cap`) |
| `polza-images` | `POST /api/v2/images/generations` (≤ 120 с синхронно, иначе опрос `/api/v1/media/{id}`) | схема OpenAPI; цена — ступень 1K каталога, верх — запасная ступень |

Подкоманды: `estimate JOBS… [--summary|--json]`, `run JOB [--pick TAG|N|/re/]`, `batch JOBS… [--parallel 2]`,
`status ID --channel C`, `download ID --channel C`, `ledger [--sum] [--channel C]`, `show MODEL --channel C`,
`snapshot [--channel routerai|genapi|all]` (публичные каталоги без ключа → `$DDD_HOME/cache/ai-media/{routerai,genapi}/<дата_время>/`),
`selftest`. Шаблоны `{{ИМЯ}}` / «<…>» — `--set ИМЯ=значение`, `--set-file ИМЯ=путь`; лимиты по верху (`--limit-by
high`) или ожиданию (`expected`).

Окружение: ключи `ROUTERAI_API_KEY` | `GENAPI_API_KEY` | `POLZA_API_KEY` или `~/.config/{routerai,genapi,polza}/api_key`
(600; читаются только при `--live`, `Authorization` — только своему хосту); базы `ROUTERAI_BASE_URL`, `GENAPI_BASE_URL`,
`POLZA_BASE_URL`; бюджеты `ROUTERAI_BUDGET_TOTAL`, `GENAPI_BUDGET_TOTAL` (**по умолчанию 0 — без явного лимита `--live`
не тратит**), `POLZA_BUDGET_TOTAL` (2000, общий с `polza.py`), `MP_BUDGET_AGENT`, `MP_MAX_JOB` (60); журнал `MP_LEDGER` |
`POLZA_LEDGER`; результаты `MP_OUT_ROOT` (`$DDD_HOME/out/ai-media/_mp/<агент>/<дата>/`). Коды выхода — как у `polza.py`
(0 успех; 1 задание, незаполненный шаблон, задание оценки или 3D-сеть; 2 бюджет; 3 таймаут опроса; 4 failed/error/expired;
5 HTTP; 6 скачивание).

Примеры: `python3 mp_client.py estimate jobs/*.routerai.json --summary`; `python3 mp_client.py run jobs/X.genapi.json` →
`… --live`; `python3 mp_client.py show recraft-v4 --channel genapi`; `python3 mp_client.py ledger --sum`.

## Провенанс: `provenance_check.py` (агент L, волна 3, 23.09.2026)

Бесплатная проверка меток ИИ в файле (0 ₽, без сети; `--trust` — локальный снимок списка доверия C2PA). Системный Python
3.13 + Pillow + numpy + scipy; внешние — `bin/c2patool/c2patool`, `bin/exiftool/exiftool`, `ffprobe`/`ffmpeg`.
Самопроверка `selftest` — 11/11 PASS за 3,6 с; корпус 70 файлов (H/04b, CC0-фото, SVG Recraft) —
`99-raw/experiments/L/01-provenance-check/`; видео — `…/L/02-video-metadata-survival/`.

| Команда | Что делает |
|---|---|
| `scan PATH… [--out DIR] [--corners] [--trust]` | C2PA (состояние Valid/Invalid/Trusted, генератор, подписант, `digitalSourceType`, ингредиенты, вес манифеста, sidecar `.c2pa`), IPTC/XMP (`DigitalSourceType`, `AISystemUsed`, `AIPromptInformation`, Credit, Software…), тег `AIGC` в MP4/WebM, `<recraft-signature>` в SVG, строки `SynthID`/`TC260` в байтах, паспорт polza рядом (`sha256_match`); `--corners` — `corners.jpg` (углы TL TR / BL BR) + подсказка «надпись в углу» (≈ 50 % на фото — смотреть глазами); вывод `provenance.md` + `provenance.json` |
| `stamp IN OUT --dst trained\|composite [--system S] [--system-version V] [--credit C]` | XMP `DigitalSourceType` (+ `AISystemUsed`) в производную: AVIF/WebP/JPEG/PNG/JXL/MP4/MOV — exiftool (+1–3 КБ), WebM/MKV — ремукс ffmpeg с тегом; файл с валидным C2PA не трогает без `--force` |
| `selftest [--keep DIR]` | подпись, потеря в AVIF, штамп, отказ править мастер, AIGC в MP4 и его судьба при ремуксе/`-an`/WebM, подпись Recraft, надпись в углу |

Пример: `python3 provenance_check.py scan 99-raw/experiments/_polza --corners --trust --out 99-raw/experiments/L/05-phase5-provenance/$(date +%F)`.
Правила — `../../kb/ai-media/12-legal-provenance/02-labeling-ai-act-provenance.md` §4–§6; план фазы 5 — `99-raw/phase5/L-plan.md`.

**0.1.1 (оркестратор, сессия 5, 25.09.2026)**: C2PA читается и в SVG (`c2pa_read` для `kind == svg`, счётчик
`c2pa_manifest_blocks`, совет про `removeMetadata`). Повод — SVG Recraft через RouterAI несут манифест C2PA в
`<metadata><c2pa:manifest>` (17,7 КБ = 17 700 байт, 30–79 % веса файла), а 0.1 искал только `<recraft-signature>` и писал «меток нет».
После чистки путей манифест `Invalid` (`dataHash.mismatch`), svgo `preset-default` удаляет его вместе с `<metadata>`.
`selftest` — PASS до и после; скан всех выходов фазы 5 (254 файла) — `99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md`.

## Приёмка ассетов — `asset_audit.py`

Python окружения скилла (`numpy`, `scipy`, `Pillow`, `PyYAML`, `rapidocr` для OCR) + ffmpeg; модели OCR —
`$DDD_HOME/models/ocr` (sha256 — `../../kb/ai-media/11-evaluation-qa/thresholds.yaml` → `ocr_models`). Объединяет вызовом и
импортом, не переписывая: `image_metrics`, `composition_metrics`, `text_zone`, `series_metrics` и `split_grid`,
`stand_run.text_check`, `edit_check` и `alpha_check`, `tile_check`, `video_loop_check`, `check_icons.py`,
`mp_client.svg_info`, `vlm_to_dna` (палитра, приёмка паспорта), `provenance_check.py scan --corners` (метка в углу →
`QA-PROV-VISIBLE-MARK`, лист `<файл>_corners.jpg`; ИИ-файл `--stage web` без машиночитаемой метки → `QA-PROV-NO-MARK`).
Пороги — `../../kb/ai-media/11-evaluation-qa/thresholds.yaml` (у каждого источник и статус). Тесты:
`python3 tests/test_asset_audit.py [--ocr] [-v]` — 76 проверок без OCR (входы журнала опытов и exiftool, которых нет, —
пропуск с пометкой); `asset_audit.py selftest` — те же тесты.

| Команда | Что делает | Пример |
|---|---|---|
| `audit PATH…` | файл, список или папка с паспортами polza.py / mp_client.py → `<OUT>/audit.json` (asset-audit/1: вердикт pass / warn / needs_human / fail, коды дефектов с порогом и источником, маркеры, что смотреть человеку), `<OUT>/audit.md`, панели `<файл>_panel.jpg`, листы углов `<файл>_corners.jpg`, `<OUT>/index_sheet.jpg`; `--strict` — код 1 при fail; `--stage web` — бюджеты веса, `--mobile` — телефонный кадр слота (`budget.image.hero_mobile_kb`, 80 КБ) | `python3 asset_audit.py audit gen/ --dna ../../kb/ai-media/06-art-direction-consistency/examples/dna-strict-saas.json --out out/` |
| режимы (`--mode auto` по паспорту, коду задачи, альфе, расширению) | `image`, `cutout`, `edit` (`--orig [--mask] [--protect]`; аутпейнт — по пропорции; без маски — маска из разницы), `texture`, `video-loop` (`--control`, `--mask` синемаграфа, `--mezzanine`; `--master` мезонин → `motion_keep` ≥ 0,75), `video-alpha` (`--key`), `svg-icon`, `og`; `--series` / `--grid 2x2` | `audit hero.png --slot hero --text-zone 0,0,0.42,1 --expect "Весенняя распродажа"` |
| `ocr IMG… [--expect]` | OCR кириллицы (det PP-OCRv6 small + rec eslav PP-OCRv5, «латинский нюх» en) под блокировкой heavy + сверка: пропуск, удвоение, латиница, ё, лишнее слово, GNED | `asset_audit.py ocr banner.png --expect "Скидки до −30 %"` |
| `thresholds [--check]` | пороги с источниками; `--check` — все ключи кода есть в YAML и у каждого источник | `asset_audit.py thresholds --check` |
| `judge-jobs` | **пакет судьи** для отдельных сессий Opus (агент `design-judge`, протокол `../../kb/common/judge.md`) в `$DDD_HOME/out/ai-media/judge/<имя>/`: `jobs/<id>.md` (вид вызова, задача, кадры, рубрика, формат ответа), `<имя>/frames/` (нейтральные имена по sha256; PNG без потерь или `--same-encoding`; кадры пары одной пропорции — к меньшему размеру), `<имя>/response.schema.json`, `<имя>/manifest.json`, `<имя>/README.md`, пустая `<имя>/answers/`; ключ слепоты — `<имя>.key.json` рядом, вне пакета. Входы: `--items` (рубрика по кадру — `--mode checklist|defects`, пары — `--mode pairwise`; без `--rubric` — вопросы рубрики владельца в каждой строке, так судят макет и страницу), `--from-stand-page` (те же пары и файлы, что у заказчика), `--calibration [--pairs …]` (пары `assets/calibration/index.yaml`, вопросы из поля `rubric`, разметка — в ключе); оба порядка пары и `--runs` прогонов (3; 5 — сортировка; 1 — черновик) — отдельные задания | `judge-jobs --rubric hero-photo --items pairs.jsonl --mode pairwise` |
| `judge-parse PACKAGE` | ответы `answers/<id>.md` (первая строка и блок ```json по схеме) + ключ → `<имя>.answers.jsonl` и сводка `<имя>.verdict.json` рядом с ключом: пара — совпадение обоих порядков в прогоне и большинство прогонов («неразличимы» без большинства), маркер и находка — не меньше чем в двух прогонах; «нет» без доказательства и «да» без места — «не уверен», выбор без причины — ничья; партия — доля позиции A, согласованность перестановки, доля «не уверен»; у калибровки — попадания в уровень | `judge-parse $DDD_HOME/out/ai-media/judge/<имя>` |
| `agree`, `calibrate` | согласие вердиктов пар с голосами заказчика по сессиям (`--votes` — файл на сессию), Уилсон, F1 находок против разметки (`--labels`), κ по вопросам → уровень доверия «мало данных / не использовать / только предфильтр / сортировать» и сигналы пересчёта — пороги группы `judge` `thresholds.yaml`; порог метрики по меткам человека (Юден, AUC) | `agree --answers <имя>.answers.jsonl --votes votes.json --key page.key.json` |

Моделей утилита не вызывает: оценку делает сессия Opus по пакету, код готовит пакет и разбирает ответы. OCR и тяжёлые шаги —
под блокировкой heavy; при < 1 ГБ свободной памяти OCR не запускается (ошибка в отчёте, вердикт needs_human). Блокировку
утилита берёт сама и внешним `flock` не оборачивается: если замок уже держит процесс-предок `flock`, повторно не берёт;
`page_accept.py` с замками тишины — то же правило.

## Приёмка страницы с ассетами — `page_accept.py`

Playwright (Chromium, `channel="chromium"`) + numpy, Pillow, scipy, PyYAML. Второе звено ворот после сборки: отчёт
`accept_<режим>.json` читает `page_gates.py --accept`. Код-репо запускает утилиту соседним чекаутом
`../strategy/…/scripts/ai-media/page_accept.py`; её же зовёт `motion_check.py --f83`.
Замки тишины (общий тяжёлый, браузера, ai-media — `page_gates.heavy_lock`) берёт сама; замок, который держит обёртка
(`slot_run.py`, `flock`), повторно не берёт; `--no-lock` — не брать вовсе. Локальный HTML раздаёт встроенным HTTP-сервером
(Range для видео) от корня `--root` или по ссылкам `../` страницы и закрывает его.

| Что | Как |
|---|---|
| Запуск | `page_accept.py PAGE.html\|URL --out DIR [--budget-profile <page_type>@L<n>] [--mobile] [--throttle] [--no-rm] [--root DIR] [--dark] [--click SEL …] [--contrast SEL …] [--wait МС] [--first-screen-only] [--loops 3] [--acceptance] [--no-lock]` · `--selftest` |
| Условия | `budgets.yaml` site `conditions`: окно первого экрана (load + `window_after_load_s`; `--wait` — своё), десктоп — окно и DPR `lab_desktop`, телефон — дескриптор и CPU `lab_mobile` (UA — HeadlessChrome), `--throttle` — сеть и CPU `lab_mobile`; с `--throttle` вес не сравнивается — вес меряет прогон без замедления (`lab_weight`) |
| Пороги | с `--budget-profile` — профиль site (`page_gates.py`): вес первого экрана выше профиля — WARN, LCP выше цели — WARN, выше «плохо» — FAIL, CLS так же; без профиля вес не сравнивается, LCP и CLS — по порогам, общим для всех уровней; reduce — порог ворот эффектов EG-A11Y-06 (`effect-gates.yaml`), «движется на 6-й секунде» — `limits.moving_pct_min` EG-A11Y-01; вылет на ширинах приёмки — `limits.overflow_px` строки SG-MOB-01 (`page-gates.yaml`), переотдача картинки первого экрана больше ×2 — WARN (строки ворот у неё нет) |
| Меряет | вес первого экрана по CDP, LCP (элемент, файл, время, lazy, `fetchpriority`), CLS, TBT, `alt`/`width`/`height`, переотдача, атрибуты видео; медиа первого экрана (`media_first`: видео и холсты, постер, бит на пиксель постера, доля площади под постером — SG-PERF-16); 2.2.2 — первый экран на 6-й секунде (`motion_6s`) и петли всей страницы (`loops`: каждая найденная петля — в экран и через 6 с; `--first-screen-only` — пометка «только первый экран»; механизм паузы узнаётся по подписям `page_gates.PAUSE_LABELS`, общим с `motion_check.py`); reduce записью всей страницы (`reduce.media_kb`, `reduce.motion`: первый экран и паузы прокрутки, % пикселей за 1 с); F83 по буквам (два снимка: с текстом и `color: transparent`), для видео — по кадрам 0/25/50/75 %; `--acceptance` — картинки и вылет на ширинах приёмки `kb/common/acceptance-widths.yaml` (`acceptance[]`: `width`, `overflow_px`, `over[]`, `no_wh[]`; на ширине `overflow_only` — только вылет; с `--dark` — в тёмной теме) |
| Выход | `accept_<режим>.json` (`device`, `throttle`, `profile`, `thresholds`, `window_after_load_s`, `no_preference`, `reduce`, `acceptance`, вердикт `pass`, `fail`, `warn`, `ok`), `shot_<режим>.jpg`, `shot_rm_<режим>.jpg`; код выхода 0 — FAIL нет, 1 — есть, 2 — ошибка вызова |
| Ограничения | лаборатория ≠ поле (CrUX не подключён); троттлинг DevTools не создаёт конкуренции; клик до LCP останавливает LCP; INP не меряется; Safari — нет; петли — анимации, видео и холсты WebGL, которые видит браузер (петля на canvas 2D без WebGL не видна) |

## Ссылки, метки и структура базы — `check_links.py` (агент X, волна 4, 24.09.2026)

Адаптация `../maint/check_links.py`; только стандартная библиотека, ≈ 6 с на всю базу, без сети. Семь
проверок: (а) пути к файлам и папкам (диапазоны `01–04`, `G-01…G-06`, соседние базы, пути от `../../kb/ai-media/99-raw/`); (б) ссылки `§N.M`
(буква агента + номер файла: «F `01`» = `06/01`); (в) `[S#]`; (г) `[V:<id> мм:сс]` — дайджест, транскрипт, каталог, таймкод ≤
длительности; (д) README папок в обе стороны; (е) обязательные разделы файлов и дайджестов; (ж) метки `[проверено: …]` →
папка опыта (`H/05a` — часть опыта `H/05-…`). Уровни ERROR / WARN / INFO, код 1 при ERROR. Прогоны 24.09 —
`99-raw/experiments/X/01-check-links/` (run1: 246 ERROR, в основном ложные → run6: 8 настоящих, исправлены или в реестре).

| Команда | Что |
|---|---|
| `python3 ../maint/check_links.py [--only а,б] [--json out.json] [--quiet-info] [--no-raw]` | отчёт в stdout; `--no-raw` — без `README.md` и `99-raw/phase5/*.md` |
