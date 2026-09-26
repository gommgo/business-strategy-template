# Утилиты creative-research

Все пути — от корня `kb/creative/` (от корня скилла). Утилиты скопированы архитектором 24.09.2026 в 05:50
командой `cp -p` **без изменений** (сверено `cmp` — байт в байт с источниками). Пути внутри считаются от расположения файла
(`ROOT = ../..` от этой папки), поэтому копии пишут в наши `99-raw/cache/`, `99-raw/youtube/`, `91-videos/`.

Машина (проверено 24.09.2026): Debian 13, 20 потоков, 15 ГБ ОЗУ (свободно обычно ≈ 5 ГБ — параллельно работают сессии других
баз), Intel Iris Xe без CUDA; Python 3.13.5; Playwright 1.63.0 с браузерами Chromium (1228, 1234, 1243), headless shell и
**WebKit 2359** (Firefox не установлен); Pillow 11.3.0, numpy 2.3.2; ffmpeg 7.1.5; yt-dlp 2026.08.18 (`~/.local/bin/yt-dlp`);
Node 24.21.0 (`node` из PATH или DDD_NODE).

## Скопировано

| Утилита | Откуда (файл источника от) | Что делает | Пример |
|---|---|---|---|
| `fetch.py` | `../kimi-research/99-raw/tools/` (23.09 19:29; исходно ai-media ← blender) | страница → читаемый Markdown в `99-raw/cache/`, PDF — через `pdftotext`; печатает путь | `python3 99-raw/tools/fetch.py "URL"` |
| `render_fetch.py` | там же (23.09 19:29) | то же через headless-браузер: SPA, документация на JS, галереи | `python3 99-raw/tools/render_fetch.py "URL" --scroll [--html]` |
| `site_probe.py` | там же (23.09 19:29; исходно blender, агент A) | замер живого сайта: байты по категориям и сигнатурам, LCP с элементом, TBT, контексты WebGL/WebGPU, draw calls, прокрутка колесом, библиотеки 3D; `--mobile` (Pixel 7), `--throttle`, `--reduced-motion` | `python3 ../blender/site_probe.py https://site out/ [--mobile] [--reduced-motion]` |
| `measure_ui.py` | там же (23.09 19:29; исходно ui-research, агент P) | computed styles видимых элементов → кегли, интерлиньяж, веса, цвета (hex, OKLCH), радиусы, тени, отступы, каркас, переходы, фокус; JSON в `99-raw/cache/measurements/`, скриншот в `99-raw/cache/screens/` | `python3 ../ui/measure_ui.py URL --viewport 390x844 --scroll --full-page` |
| `ui_audit.py` | там же (23.09 19:29; исходно ui-research, агент I) | визуальный QA по порогам ui-research: пресеты **только** `admin` и `consumer`; на лендинге даёт ложные «серьёзно» (A1, B1/B2, D3, D4, H1/H2, H10, J2, J6, J8, K2/K3, L5 — `UI-report.md` §4.3) → профиль `marketing` сделает K обёрткой `marketing_audit.py`, сам файл не менять | `python3 ../ui/ui_audit.py URL --preset consumer --viewport 1440x900` · `--selftest` |
| `color.py` | там же (23.09 19:29; исходно ui-research) | WCAG 2 и APCA, hex ↔ OKLCH, ΔE, композитинг альфы, симуляция дальтонизма; нужен `ui_audit.py` и `measure_ui.py` | `python3 ../lib/color.py selftest` |
| `yt_dl.py` | там же (23.09 19:29; способ ai-media V/01) | YouTube без HTTP 429: `meta` — метаданные; `subs` — одна дорожка на ролик; `comm` — 100 верхних комментариев; `pick` — показать выбор дорожки без сети; файлы — `99-raw/youtube/{meta,subs,comments}/`, журнал `99-raw/youtube/yt_dl.log` | `python3 99-raw/tools/yt_dl.py meta 99-raw/youtube/ids_p1.txt` |
| `vtt2md.py` | там же (23.09 19:29; пути исправлены ai-media 23.09) | транскрипты `91-videos/transcripts/<id>.md` из скачанных `.vtt` и метаданных; **список — только id по строке** | `python3 99-raw/tools/vtt2md.py 99-raw/youtube/ids_p1.txt` |
| `yt_transcript.py` | там же (23.09 19:29) | поиск по YouTube без API (`--search "запрос" -n 20`) — для V; субтитры им не качать (для этого `yt_dl.py`) | `python3 99-raw/tools/yt_transcript.py --search "scroll-driven animations" -n 20` |
| `yt_frames.py` | там же (23.09 19:32; kimi, оркестратор) | видео → кадры для просмотра глазами: `download ids.txt [--height 1080]` (без звука, ≤ 1080p, H.264, пауза 10 с) → `99-raw/youtube/video/<id>.mp4`; `frames ids.txt [--every 10] [--scene 0.30] [--min-gap 2] [--dedup 3.5]` → `91-videos/frames/<id>/` (кадры, `index.tsv`, листы 4×4); `at <id> 07:31 …`; `crop <id> 07:31 x y w h [--scale 2]` | `python3 99-raw/tools/yt_frames.py frames 99-raw/youtube/ids_p1.txt` |
| `transcribe_local.py` | `../blender-research/99-raw/tools/` (23.09 02:35) | локальное распознавание речи Qwen3-ASR-1.7B через `llama-mtmd-cli` на CPU (модель — `~/.cache/huggingface/hub/models--ggml-org--Qwen3-ASR-1.7B-GGUF/`, бинарник — `~/.local/bin/llama-mtmd-cli`; оба на месте 24.09); ≈ 0,43 реального времени при 16 потоках — **тяжёлый прогон**: только оркестратор, по одному, при ≥ 4 ГБ свободной памяти | `python3 99-raw/tools/transcribe_local.py <id> --threads 12` |
| `asset_inventory.py` | `../ai-media-research/99-raw/tools/` (23.09 10:53; агент A ai-media) | инвентарь визуальных ассетов страницы: картинки и `srcset`, CSS-фоны, видео (autoplay, пауза), SVG, Lottie, Rive, canvas, байты по CDP, LCP до прокрутки, CLS, TBT, движение в покое, og:image | `python3 ../ai-media/asset_inventory.py URL OUT [--mobile] [--reduced-motion] [--quick]` |
| `page_accept.py` | там же (23.09 20:58; агент J ai-media) | приёмка страницы: вес первого экрана (порог `--budget-first-kb`, по умолчанию 2500 — это норма L0, для L1 и L2 задавай свой), LCP, CLS, TBT, alt, пауза видео, reduce (0 байт видео, движение < 0,5 %), контраст текста на медиа по F83 «по буквам» и по кадрам видео; код выхода 0/1/2 | `python3 ../ai-media/page_accept.py PAGE.html --out DIR --contrast ".hero h1" --budget-first-kb 3500` |

## Оговорки к копиям (править не нужно; учесть при работе)

- Жёстких путей на чужие базы нет; абсолютные пути только машинные: Node (`yt_dl.py:21`, `yt_frames.py:30`), модель и бинарник
  ASR (`transcribe_local.py:22–28`).
- `page_accept.py:26` берёт блокировку **нашей** папки `99-raw/tools/.locks/browser.lock` — она не согласована с блокировками
  ai-media и сестёр. Все наши браузерные прогоны держат ту же блокировку (ниже); про общую нагрузку машины помнит оркестратор.
- `yt_frames.py frames` ищет видео как `99-raw/youtube/video/<id>.*` по любому id → запись прокрутки можно подать псевдо-id
  (например, `scroll-stripe-home-d.webm`); не проверено, что без `meta/<id>.info.json` (главы) команда не падает — проверит C.
- `ui_audit.py` и `measure_ui.py` не знают тип страницы «маркетинг» → профиль K. `site_probe.py` мерит 3D и не видит анимации
  DOM, библиотеки движения и типографику → `effects_probe.py` C.
- Firefox в Playwright не установлен (вопрос заказчику); WebKit Playwright — не Safari, но второй движок для проверки
  эффектов.

## YouTube без HTTP 429 (способ ai-media, опыт V/01: 110 загрузок подряд без 429)

1. Метаданные отдельно (`yt_dl.py meta`) — timedtext не трогается.
2. Ровно одна дорожка на ролик: ручные на языке оригинала → автоматические `<язык>-orig` → ручные en/ru; никаких масок `en.*`.
3. Ссылка на дорожку — из сохранённого `info.json`; истекла — метаданные заново.
4. Пауза 6 с между роликами; при 429 — 90 и 120 с с повтором; после трёх роликов подряд с 429 — остановка (перезапуск
   идемпотентен).
5. JS-рантайм yt-dlp: `--js-runtimes node:$(command -v node)`.

## Правила

- **Браузер — только под блокировкой**, одна команда на прогон, браузер закрывать сразу:
  `flock -w 900 $DDD_HOME/locks/creative/browser.lock python3 99-raw/tools/<утилита> …`;
  перед прогоном `free -g` — нужно ≥ 3 ГБ available, иначе ждать.
- ffmpeg — `-threads 4`, не больше двух кодирований одновременно; видео-записи удалять после нарезки кадров.
- Python-пакеты — только в venv внутри этой папки: `uv venv 99-raw/tools/venv-<буква>` и
  `uv pip install --python 99-raw/tools/venv-<буква>/bin/python <пакет>`; npm — в подпапке node этой папки (появляется при первой установке) или в папке опыта;
  `sudo` запрещён; глобально ничего не ставить.
- Клоны репозиториев — сначала `../kimi-research/99-raw/cache/repos/` (только чтение), свои — `99-raw/cache/repos/<org>__<repo>/`,
  `git clone --depth 1`.
- Учётные данные площадок — только `~/.config/<сервис>/` (каталог 700, файлы 600); утилиты их не печатают и не пишут в журналы;
  вход делает заказчик.

## Будут добавлены агентами

| Утилита | Кто, волна | Назначение (подробно — `PLAN.md` «Окружение и утилиты», задания агентов) |
|---|---|---|
| `effects_probe.py` | C, 1 | замер эффектного сайта: библиотеки движения и WebGL, анимации (`getAnimations`, GSAP), scroll-driven CSS, View Transitions, sticky и pin, курсор, бегущая строка, split-текст, типографика и display-кегли, палитра, вес, LCP, CLS, TBT, длинные кадры при прокрутке, reduced motion, плавная прокрутка → JSON и строка `03-live-sites-measured/sites.csv` |
| `scroll_record.py` | C, 1 | запись прокрутки (десктоп, телефон, reduce) → кадры и контактные листы; движение в покое по секциям |
| `refs_client.py` | B, 1 | клиент поиска референсов: `login` (только заказчик), `search`, `get`, библиотека, мудборд, выгрузка в Are.na; режимы «ассистент» и «поиск»; частоты и журнал |
| `effect_bench.py` | F, 2 | прогон лабораторных страниц эффектов в Chromium и WebKit → поля `cost` и `fallback` в `effects.yaml` |
| `marketing_audit.py` | K, 3 | обёртка `ui_audit.py` с профилем `marketing` + проверки движения страницы |
| `motion_check.py` | K, 3 | цикл проверки сборки: запись → кадры → метрики → сверка с `motion-spec` → отчёт |
| `check_links.py` | X, 4 | проверка ссылок `../../kb/creative/99-raw/`, `→ §`, `[V:]` — скопировать из `../kimi-research/99-raw/tools/` (появилась там 24.09) |

Каждый агент, написавший утилиту, добавляет сюда раздел: команды, выход, проверено на чём, ограничения.

## `refs_client.py` — клиент референсов (скелет login/status — оркестратор; остальное — агент B волны 1, 24.09.2026)

Полное описание — `../../kb/creative/02-references-moodboards/02-refs-client-and-library.md`; справка — `refs_client.py <команда> -h`.

| Команда | Что делает |
|---|---|
| `login <сервис> [--dry-run] [--engine brave\|chromium] [--finalize]` | **только заказчик**, в своём терминале: обычное окно Brave без автоматизации с профилем `~/.config/<сервис>/profile/`; Ctrl+C окно не закрывает (1-й — «я жду», 2-й — доводка без ожидания); `--finalize` — доделать шаги после прерванного входа (права, `login.json`, журнал) |
| `status [<сервис>]` | профиль, права, имена cookie и сроки (без значений), режим, страниц за сутки, пауза; сам доводит вход, если `login.json` нет |
| `search <сервис> "<запрос>" [--pages 1–5] [--opt k=v] [--board имя] [--dry-run]` | режим «поиск»: выдача → записи библиотеки (метаданные, превью ≤ 800 px, палитра OKLab, dHash) |
| `search <галерея> latest\|<раздел> [--pages N] [--max N] [--shots K]` | галереи без входа (продолжатель B2, опыт B/02): `awwwards` (sotd, sotm, soty), `cssda` (wotd, wotm, woty, kudos, home), `fwa`, `recent-design` (`recent`), `godly-design` (`godly`: websites, home, hero, cta, footer), `httpster` (стиль), `minimal-gallery` (`minimal`: тег), `landingfolio` (отрасль), `siteinspire` → записи **сайтов** `site-<домен>` с наградой и датой; картинки галереи не сохраняются; `--shots K` — наш снимок первого экрана K сайтов |
| `get <URL…> [--take …] [--dont-take …] [--role …] [--board имя]` · `enrich <файл>` | режим «ассистент»: ссылки заказчика → записи; файл — `URL \| take: …; … \| dont: … \| role: … \| board: …` |
| `arena pull <канал>` · `arena push <мудборд> --channel <slug>` | Are.na API v3: чтение канала (без токена — публичный); выгрузка — только в **private**-канал, токен `~/.config/arena/token` (600) |
| `lib list\|show\|tag\|dedup\|export` · `board <имя>` · `handoff <мудборд> --out DIR` | библиотека; мудборд (HTML + контактный лист JPG + `board.md`); папка `refs/` + `README.md` для K3 по шаблону kimi |
| `limits` · `resume <сервис>` · `mode <сервис> search\|assistant\|off [--clear-hold]` · `journal` · `selftest` | частоты и паузы; снять паузу; режим сервиса (решение заказчика); журнал; проверки без сети |

- **Слот браузера клиента** (решение оркестратора 24.09.2026 ≈ 15:55): `search`, `get`, `enrich` берут **не** общую
  блокировку тройки и не `99-raw/tools/.locks/browser.lock`, а отдельный слот `$DDD_HOME/locks/browser-refs.lock`
  — один браузер клиента на машину (клиент интерактивный, заказчик не ждёт очередь замеров). Другие утилиты и агенты этот
  слот **не берут**. Вместе с общим слотом в тройке одновременно не больше двух браузеров (контракт v2 §4). Проверка
  памяти ≥ 3 ГБ перед запуском и удержание ≤ 280 с на вызов или партию — как у всех.
- **Движок**: Brave 153 (`/opt/brave.com/brave/brave`) — и окно входа, и `launch_persistent_context(executable_path=Brave,
  headless=True)`; запасной — Chromium Playwright (`--engine chromium`, `REFS_ENGINE=chromium`). Вход через Google в
  сборку Chrome for Testing не проходит (24.09.2026). Основной профиль Brave заказчика `~/.config/BraveSoftware/` не
  трогается. В новом профиле Brave включены Shields (блок трекеров и рекламы) — выдаче Dribbble не мешают (опыт B/06).
- **Частоты**: ≥ 10 с + U(0; 6) с между загрузками страниц и порциями одного сервиса; порций на запрос 3 (≤ 5); страниц в
  сутки: dribbble 60, behance 40, dprofile 60, галереи 40; челлендж, капча, 401/403 → пауза 6 ч; 429 → Retry-After, ≥ 1 ч;
  повторов подряд нет. Галереи и сайты — только разрешённое `robots.txt` (разбор по RFC 9309).
- **Где что лежит**: сессии — `~/.config/<сервис>/profile/` (700/600), `login.json` без секретов; режимы —
  `~/.config/creative-refs/modes.json`; библиотека заказчика — `~/.local/share/creative-refs/` (`library.jsonl`,
  `previews/`, `boards/`; 700/600; `CREATIVE_REFS_HOME` или `--library`); журнал и частоты — `99-raw/cache/refs/journal.tsv`,
  `state.json` (без секретов).
- **Чего клиент не делает**: не читает и не печатает cookie и токены сервисов, не собирает своих запросов с заголовками
  авторизации (данные — DOM, серверный HTML, ответы, которые страница получает сама); не маскирует автоматизацию (без
  stealth, подмены UA, правки `navigator.webdriver`); не обходит антиботы; не публикует и не кладёт в базу чужие работы;
  не качает видео; не входит в сервисы (вход — только заказчик).
- **Режимы на 24.09.2026** (решения заказчика через оркестратора): Dribbble — «поиск» (≈ 15:00); Dprofile — «поиск»
  (16:24, риск п. 11.3 соглашения принят заказчиком); Behance — `off` («давай пока без беханса», 15:33; адаптер не проверен
  вживую). Для «сайтов» частоты и паузы — по хосту (`site:<домен>`).
- **Галереи** (продолжатель B2, 24.09.2026): запись — сам сайт (сайт из разных галерей — одна запись; награды и
  `site.galleries` копятся, снимок сайта не перетирает источник и название); реклама пропускается; без адреса сайта —
  временная запись `<галерея>-<id>`, которую `get <страница галереи>` заменяет записью сайта со снимком; `get` страницы
  списка галереи отклоняется; Land-book, Lapa Ninja, One Page Love — отказ с объяснением (только ссылки заказчика).
  «429 + Vercel Security Checkpoint» (SiteInspire) — как челлендж: ждём ≤ 20 с, пока браузер пройдёт сам, иначе пауза.
  robots.txt: сетевой сбой — один повтор через 3 с.
- Проверено: `selftest` (без сети, 48 проверок); опыты `99-raw/experiments/B/02` (адаптеры галерей: jsdom на серверном
  HTML, 222 записи, 0 ошибок схемы), `03` (dry-run входа, права), `04` (Brave), `05` (Ctrl+C), `06` (живые запросы
  Dribbble), `07` (живые запросы Dprofile).

## `effects_probe.py` и `scroll_record.py` (агент C, волна 1, 2026-09-24)

Обе — браузерные: запуск только под двумя блокировками, после `free -g` (≥ 3 ГБ available), одна страница и один режим
на блокировку. UA не подделывается (десктоп — HeadlessChrome по умолчанию Playwright; `--mobile` — дескриптор Pixel 7 с
заменой `Chrome/` → `HeadlessChrome/`), `AutomationControlled` не выключается — в отличие от `asset_inventory.py` и
`measure_ui.py`. Партии — `99-raw/experiments/C/run_batch.py` (память, блокировки на страницу, `timeout 420`, проверка
маршрута до и после: страна выхода и «видит ли Яндекс другой адрес», адреса не пишутся; колонка `net`).

**`effects_probe.py URL OUT_DIR [--mobile] [--throttle] [--reduced-motion] [--wait 8000] [--steps 24] [--timeout 180] [--locale en-US] [--slug S] [--no-scroll] [--no-gsap-hook]`**
→ `OUT_DIR/effects[_mobile][_thr][_rm].json`, `sheet….jpg` (4 кадра: первый экран, ⅓, ⅔, конец), строка JSON в stdout.
Сценарий: `load` → `--wait` → 2 с покоя (2 скриншота через 1 с: доля меняющихся пикселей и связные области) →
снимок анимаций (`getAnimations()` по типам и таймлайнам; GSAP) → разбор DOM и стилей → проверка бегущей строки (3 замера
за 0,7 с) → прокрутка колесом `--steps` шагов (инерция первого шага, частота кадров по rAF, LoAF, TBT, CLS при
прокрутке, число бегущих анимаций на шаге, сдвиг широких дорожек — горизонтальная прокрутка) → вес сессии → тест курсора
(после фиксации веса: наведение запускает префетч Next.js). Что собирает — докстринг утилиты; колонки — `../../kb/creative/03-live-sites-measured/README.md`.
- GSAP в бандле (ESM) не ставит `window.gsap` → перехват присваивания `vars` через акцессор `Object.prototype.vars`
  (init-скрипт до скриптов страницы): корневая линия (`vars.id === "root"`) и экземпляры ScrollTrigger (есть `scroller`
  и функция `scroll`); версия — `window.gsapVersions`. Выключить: `--no-gsap-hook` (побочный эффект: `'vars' in obj`
  становится true для всех объектов; на выборке сбоев не замечено — сверять с прогоном без перехвата, если сайт ломается).
- Вариативные оси — разбор таблицы `fvar` в WOFF2 (brotli), WOFF (zlib), TTF/OTF по телу ответа шрифта.
- С `--reduced-motion` ищет в OUT_DIR обычный прогон того же устройства и пишет `rm_pair` (yes / partial / no / n/a) с
  объяснением: движение первого экрана, бегущие анимации по времени, бесконечные, активные GSAP, играющие видео, вызовы
  WebGL в покое, бегущие строки.
- Проверено: лабораторная страница с известными признаками (`99-raw/experiments/C/02-probe-lab/`), пилот и сверка с
  `site_probe.py` (`03-pilot/`: байты за окно load + 8 с −0,1…+2,1 %).
- Ограничения: INP не измеряется; LCP лабораторный и шумный (Linear 2,2–7,0 с в соседних прогонах); FPS в headless упирается
  в 60; cookie-баннеры не закрываются (признак `cmp`); свой курсор ищется по элементам с `pointer-events: none` ≤ 220 px,
  догоняющим мышь за 0,7 с; «появление» — текст ниже первого экрана с `opacity < 0,05` до прокрутки и `> 0,5` после.

**`scroll_record.py URL OUT_DIR [--mobile] [--reduced-motion] [--steps 12] [--dwell 1.5] [--wait 6000] [--locale en-US] [--timeout 150] [--keep-video] [--tmpdir DIR]`**
→ `OUT_DIR/record[_mobile][_rm].json`, листы `sheet[_mobile][_rm]_NN.jpg` (4×4, подпись «время · scrollY · шаг»,
≤ ≈ 1 МБ на запись). Запись Playwright (десктоп 1440×900 → видео 960×600; телефон 412×839), синхровспышка 400 мс
(уточнение 25 кадров/с), после каждого шага колеса — ожидание успокоения прокрутки (≤ 1,6 с), пауза `--dwell`; по паузам —
доля меняющихся пикселей (порог 12/255, шум < 0,2 %), число одновременно движущихся областей (сетка 8×8 px), «непрерывность»
(≥ 60 % пар). Видео удаляется после нарезки. Проверено: `99-raw/experiments/C/05-scroll-record/` (reduce → 0 %).
`yt_frames.py frames` принимает запись как псевдо-id, но при шаге 0,5 с падает (имена кадров с точностью до секунды) и пишет в
`91-videos/frames/` → для записей прокрутки — только `scroll_record.py`.

## Утилиты оркестратора волн 2–4 (24.09.2026, вторая сессия)

- `orch_check.py [ПАПКА … | all] [--selftest-tools]` — приёмка агента: строки (норма 250–500), пять обязательных разделов,
  строка метаданных, остаток `<!-- ЧЕРНОВИК`, метки (незнакомые и число `[гипотеза]`), штампы «Стиля»; YAML (загрузка и
  поле `checked_at` / `date` / `checked`) и JSON (`$schema` у схем); README папок; самопроверки утилит, которые есть
  (`refs_client.py selftest`, у будущих `effect_bench.py`, `marketing_audit.py`, `motion_check.py`, `check_links.py` —
  `--selftest`). Адаптация `../maint/orch_check.py`. Код 1 — есть error.
- `check_links.py [--out ФАЙЛ] [--only а,б] [--quiet-info] [--selftest]` — перекрёстные ссылки (а — пути, б — `§N.M`,
  в — `[S<n>]`, г — `[V:<id> mm:ss]`, д — README против диска, е — обязательные разделы, ж — `[проверено: …]` → опыты).
  Копия `../maint/check_links.py` (md5 исходника 016af5c0d3e15c2bd1967a5a36ea42f6), адаптирована:
  соседи ux, ui, ai-media, blender, kimi, site, text; буквы агентов creative → папки; разделы дайджеста по
  `99-raw/prompts/_common-W-digests.md`. Самопроверка 27/27. Первый прогон 24.09 ≈ 20:54 по файлам волны 1: ERROR 29
  (19 путей, 6 разделов, 4 README) — вход аудитора X.
- `extract_for_audit.py [--out 99-raw/notes/wave4/extracts]` — извлечения для X и S: по папкам 01–10 (метаданные,
  «Выжимка», «Открытые вопросы», «Чек-лист», README целиком, YAML и JSON — строки и ключи), `reports.md` (противоречия,
  пробелы, «Что учесть», живая фаза, термины из отчётов), `videos.md` (индексы дайджестов), `_inventory.md`. Копия утилиты
  оркестратора text; пропускает `lab/`, `recordings/`, `node_modules/`.

## `effect_bench.py` — прогон лабораторных страниц эффектов (агент F, волна 2, 2026-09-24)

Полный метод — `../../kb/creative/06-effects-catalog/03-effects-lab-method.md`; справка — докстринг утилиты (`effect_bench.py -h`).

| Команда | Что делает |
|---|---|
| `run --pages id[?q],id*,…\|all [--modes desk,unl,rm,nogl,nojs,mob,wk,wkrm,wkmob] [--repeat N] --out DIR [--budget 240] [--scen-ms 4000]` | поднимает локальный сервер `06-effects-catalog/lab/` (Range, учёт отданных байт), гоняет страницы по режимам; `id*` — все варианты из `lab.json`; результат — строки `DIR/results.jsonl`, миниатюры `DIR/shots/`, `versions.json` |
| `summary --in DIR [--md FILE]` | медианы по повторам → `DIR/summary.json` и таблица Markdown |
| `apply --summary FILE --yaml FILE` | переносит числа в YAML (запасной путь; основной — `99-raw/experiments/F/07-yaml/build_effects.py`) |
| `--selftest` | без браузера: сервер и Range, учёт байт, статистика кадров, разбор всех `lab.json` (для `orch_check.py`) |

- Браузер — сам берёт **две блокировки** на партию (общая тройки, затем наша) блокирующим `flock` с тревогой 900 с (опрос
  `LOCK_NB` проигрывал очереди соседей), партия ≤ `--budget` с (≤ 300), перед партией ждёт MemAvailable ≥ 3 ГБ. Снаружи
  `flock` не нужен. UA не подделывается; `mob` — дескриптор Pixel 7 + CDP CPU ×4 (только Chromium); `wkmob` — iPhone 13 без троттлинга.
- Метрики: rAF-кадры, LoAF, CLS (всего, за сценарий, после `fonts.ready`), Event Timing клика-зонда `#lab-probe`, LCP, CDP
  `TaskDuration` в секунду, вызовы WebGL на кадр, `getAnimations()`, видео, движение в покое (два снимка через 1 с, порог 12/255),
  хвост прокрутки, вес (brotli q11 для текста).
- Ограничения: FPS при vsync почти всегда 60 — смотреть `TaskDuration_ms_per_s`, CLS, зонд; `unl` осмыслен только для кадров,
  которые рисует JS или WebGL; H.264 в Chromium Playwright не играет; WebKit 26.6 отдаёт LCP и Event Timing, но не LoAF и не CLS (проверено 2026-09-24).
- Проверено: `99-raw/experiments/F/01-pilot` (3 страницы × 8 режимов), `03-batch-A`, `05-batch-BG`, `06-unl`, `08-remeasure`.
- Продолжатель F2 (2026-09-24/25): `wkmob` — прокрутка через `scrollBy` (`mouse.wheel` в мобильном WebKit не поддерживается), `unl` у
  прокрутки — прокрутка из rAF страницы (колесом выходило 80–90 кадров/с у любой страницы), поле `scroll_method`; в сводке — `lcp_tag`.
  У статичной страницы без vsync rAF ≈ 60/с — цену кадра не писать (сборка берёт `unl` только при > 75 кадров/с). Атрибуция CLS —
  `99-raw/experiments/F/12-motion-toggle/cls_sources.py <страница?q> [--scroll] [--mode rm]` (узел, откуда и куда сдвинулся).
  Проверено: `F/11-wkmob` (36 страниц), `12-motion-toggle`, `13-unl`, `14-holo-look`, `15-hscroll-cls`, `16-micro`; `--selftest` 48/0.

## `marketing_audit.py` и `motion_check.py` — проверка сборки (агент K, волна 3, 2026-09-24/25)

Метод и пороги — `../../kb/creative/09-ai-execution-evaluation/03-verification-loop-and-gates.md`; ворота — `../../kb/creative/09-ai-execution-evaluation/effect-gates.yaml`.
Обе берут **две блокировки сами** (общая тройки, затем наша; блокирующий `flock` ≤ 900 с) на один адрес и режим и ждут
MemAvailable ≥ 3 ГБ; снаружи `flock` не нужен (`--no-lock` — только если блокировки держит вызывающий). Локальная страница
раздаётся встроенным сервером; корень — по самым длинным ссылкам `../../kb/creative/99-raw/` в HTML (лаборатория F: общие папки _shared и _vendor уровнем выше страницы) или `--root`.

**`marketing_audit.py URL|ФАЙЛ.html [--level L0|L1|L2] [--out DIR] [--name ИМЯ] [--allow cliche:a,cliche:b] [--no-mobile] [--no-reduced] [--tab 20] [--fail-on serious]`**
→ `DIR/<имя>.marketing.md`, `.marketing.json`, `.fix.txt` (по умолчанию DIR — папка audit в 99-raw/cache, создаётся при запуске). Импортирует `ui_audit.py`
(файл не меняется), один раз собирает computed styles на прогон (1440×900, 390×844 тач, reduce, ширина 360) и считает два набора
порогов на тех же данных: consumer (как есть) и marketing (`PROFILE` — 24 строки: перенастройка A1, A2, B1/B2, C1/C2/C5, D3, D4, D5,
E1/E2, H1/H2, H4, H8, H10, J2, J3 (узкие прогоны), J6, J8, K2, L5, M1 с основаниями) + свои проверки MKT-T1…T5 (clamp ≤ 2,5, строки H1,
трекинг и интерлиньяж кириллического display по `cyrillic-display-fonts.yaml`, висячие предлоги), MKT-C1/C2 (хроматические оттенки
по уровню, полоса 270–320°), MKT-M1…M6 (одинаковое появление у ≥ 5 блоков, анимация свойств раскладки, linear у перемещений, разовые
> 1200 мс, петли без кнопки паузы, ветка reduce в CSS), MKT-J1 (ширина 360) и 13 примет реестра клише `cliche:<id>` (`--allow` —
решение есть). `--selftest` (31 проверка в 0.1.1 без браузера на синтетическом лендинге), `--profile-md` (таблица профиля), `--batch TSV`.
**0.1.1 (S1, 2026-09-25, X-11)**: MKT-M2 считает и логические `block-size`/`inline-size`; аккордеон `<details>` (`::details-content`,
`interpolate-size: allow-keywords`) — исключение: UI-отклик по клику, не сцена (в записи анимации — поля `tag`, `pseudo`).

**`motion_check.py ЦЕЛЬ --level L0|L1|L2 [--out DIR] [--modes desk,mob,rm,nojs,nogl] [--spec motion-spec.yaml] [--f83 SEL …]`**
→ `DIR/results.json`, `gates.md` и `gates.json` (ворота: правило → найдено → порог → где), `fix.txt`, `sheet_<режим>_NN.jpg`,
`shot_<режим>.jpg`. Режимы: desk (1440×900, запись), mob (Pixel 7 + CPU ×4, запись), rm (reduce, запись всей страницы), nojs, nogl.
Метрики: сеть по фазам (первый экран = load + ≈ 5 с; сессия), br по файлу для локальных страниц, JS эффектов и 3D, видео, CDN;
LCP и «H1 выпал из LCP» (E/01), H1 в первом кадре, CLS загрузки и прокрутки, TBT, LoAF и rAF при прокрутке, хвост и путь колеса
(перехват), движение на 6-й секунде, петли в видимой зоне по паузам (объекты, не области), петли под читаемым текстом, скорость
бегущей строки, колебания 2,5–6 с, пульсация CTA, петли через 6 с после показа, кнопка паузы (нажать → стоит ли), WebGL (контексты,
отрисовка в покое), Tab-проход, вспышки WCAG 2.3.1 покадрово 25 к/с (площадь в окне 341×256 CSS px), «вау»-переходы; сверка
моментов motion-spec v1 I (цель → селектор по контракту `data-section`/`data-slot`/`data-moment`, выборка стилей цели: длительность,
свойства, конечное состояние в reduce). `report --in DIR [--level] [--gates]` — пересчёт ворот без браузера; `--selftest` (39 проверок в 0.1.2,
вспышки на синтетическом видео 10 Гц / 1 Гц); `--version`.
- **0.1.2 (продолжатель K2, 2026-09-25; ключи вывода прежние, новые добавлены)**: пауза записи — два снимка (сброс счётчика WebGL на
  +0,5 с, снимок на +1,2 с), кадры прокрутки и хвоста скраба больше не «петля в покое» (ложные S EG-A11Y-16/17 у J); зонд станций —
  якорь или доля `at` сцены, цель-группа (экземпляр в группе якоря), скрытая цель, холст/видео/fixed-слой — кадр без геометрии, трек
  цвета/opacity — счёт «изменено ↔ прошли линию», край по треку (scale — напротив `transform-origin`), reduce — конечное состояние;
  переключатель: радиогруппа и `select` «Движение», `[data-motion-toggle]`, `[data-motion-set]` — тест нажатием (`toggle_test`: desk
  «Меньше» → ≤ 0,3 %/с, 0 вызовов WebGL, 0 бесконечных, видео стоит; rm «Полное» → движение есть; EG-A11Y-24/25); EG-A11Y-11 не
  считает JS ≤ 3 КБ br и `script[data-motion-toggle]`; JS эффектов и 3D — и по содержимому (`__THREE__`, `GreenSock`, `pin-spacer`,
  `lenis-smooth`, `bodymovin`…; поле `net.sniffed`); CLS — `cls.load/scroll/total/window_max/top_sources` (узел, откуда → куда;
  EG-PERF-11); сверка с motion-spec — моменты на uniform/canvas и не замеченный скраб дают N/A, а не PASS. Ворота — v0.2.
- **0.1.3 (K2, после K/02)**: `--contrast SEL …` — худший контраст текста над живым фоном первого экрана (метод F2 `F/14 contrast.py`: текст
  прозрачен, 4 кадра по 0,45 с + 5 положений указателя на десктопе, 95-й/5-й перцентиль яркости под строками; `derived.contrast_live_min`,
  EG-A11Y-27); `--f83` исправлен — `page_accept.py` получает адрес сервера `motion_check` (у лаборатории F стили из общей папки _shared уровнем выше раньше не
  находились, F83 мерился без CSS), ключ `no_preference`, EG-A11Y-26 (B) автоматом; «петля под текстом» не считается при скриме (фон
  текста с альфой ≥ 0,6 или `backdrop-filter`); таблица станций `tip_offset_px`/`filled` в `gates.md`. Самопроверка — 45.
- Проверено: `99-raw/experiments/K/00-smoke/` (лаборатория F `marquee-logos`: все 5 режимов за 2 мин 54 с с очередью блокировок;
  пауза-тест 2 → 0 бесконечных анимаций; скорость строки 40 px/с = токен `loop.marquee-speed`).
- Ограничения: headless (rAF ≤ 60, эмуляция ≠ телефон), колесо, а не тач; INP не мерится; скринкаст ≤ 25 к/с — вспышки чаще 12 Гц не
  видны; GSAP без глобала в `getAnimations()` не виден (моменты — выборкой стилей цели); WebKit в v0.1 нет; LCP локальной страницы
  без троттлинга сети — зеркало, ворота LCP у site. Содержимое удалённых JS читается по CDP не больше чем у 30 файлов ≥ 20 КБ.

## `sources_collect.py` — сводная библиография `90-sources/` (продолжатель S1b, волна 4, 2026-09-25)

**`sources_collect.py [--check | --selftest | --stats | --unparsed] [--out ФАЙЛ] [--no-readme] [--root ПУТЬ]`** →
`90-sources/sources.tsv` (8 колонок: `url, title, author_org, year, type, used_in, reliability, notes`) и автоблок `90-sources/README.md`
между метками `<!-- sources_collect:begin -->` и `<!-- sources_collect:end -->` (ручные разделы README не трогает).
- Копия `../text-research/99-raw/tools/sources_collect.py` (S1b text, 2026-09-24), версия `1.0-creative`: соседи ux, ui, ai-media,
  blender, kimi, site, text — строки `neighbour`; агенты и приметы creative (включая «creative A:», опыты вида `G/02`, заметки,
  контракт тройки, демо-наборы) — внутренние; инициалы автора («K. Reinecke») — не код агента; внешний источник с упоминанием нашего
  опыта или кэша — внешний; путь соседа с `*` — общая папка; типы `award` и `gallery`, хосты темы в `TYPE_HOSTS`.
- Сбор 2026-09-25: 38 файлов (36 с разделом «Источники») + 18 дайджестов; 541 запись, 177 внутренних; **271 источник** (163 внешних,
  108 файлов соседей); `--selftest` — 28 проверок, `--check` — 0.
- `--unparsed` без `--stats` перезаписывает `90-sources/` (как запуск без ключей) — для просмотра брать `--stats --unparsed`.
