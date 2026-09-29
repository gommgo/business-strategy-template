# Утилиты site-research

Все пути — от корня `kb/site/` (от корня скилла). Утилиты скопированы архитектором 24.09.2026 (05:46)
**без изменений** — совпадение с источником проверено побайтно (`cmp`); смоук-тест в этой базе: `py_compile` 12/12,
`color.py selftest` — OK, `ui_audit.py --selftest` — OK (пресеты `admin`, `consumer`; 14 групп проверок),
`page_accept.py --help`, `asset_inventory.py --help` — OK. Машина: Debian 13, 20 потоков, 15 ГБ ОЗУ (в 05:47 свободно ≈ 5 ГБ:
параллельно работают сессии других баз), Intel Iris Xe без CUDA; Python 3.13 (Playwright + Chromium, Pillow, numpy, scipy,
PyYAML), Node 24.21 (`node` из PATH или DDD_NODE), yt-dlp 2026.08.18.122307 (`~/.local/bin/yt-dlp`),
llama.cpp `~/.local/bin/llama-mtmd-cli` с моделью Qwen3-ASR-1.7B-Q8_0 (`~/.cache/huggingface/hub/models--ggml-org--Qwen3-ASR-1.7B-GGUF/`),
ffmpeg 7.1.5.

**Пути.** Все скопированные утилиты считают пути от своего расположения (`HERE`/`ROOT`) — копии пишут в эту базу; жёстких
путей к чужим базам нет (урок ai-media: `vtt2md.py` когда-то писал в blender-research — в этой копии исправлено). Абсолютные
пути только к окружению: Node (`yt_dl.py`, `transcribe_local.py`), yt-dlp, llama.cpp и модель распознавания — всё на месте.
Докстринг `site_probe.py` упоминает `web_view.py` — он не нужен и не импортируется.

## Скопировано

| Утилита | Откуда (дата файла) | Зачем здесь | Запуск |
|---|---|---|---|
| `fetch.py` | `../kimi-research/99-raw/tools/` (23.09 19:29; исходно ai-media) | Страница → Markdown в `99-raw/cache/`, PDF — через `pdftotext`; печатает путь | `python3 99-raw/tools/fetch.py "URL"` |
| `render_fetch.py` | там же (23.09 19:29) | То же через headless-браузер: SPA, документация на JS | `python3 99-raw/tools/render_fetch.py "URL" --scroll [--html]` |
| `site_probe.py` | `../blender/` | Замер страницы с 3D: байты по категориям, LCP с элементом, TBT, WebGL, прокрутка, `--mobile`, `--throttle`, `--reduced-motion`, `--no-3d` (прогон «постер без 3D» для вклада 3D); ворота — `gate_check.py` | `../blender/site_probe.py https://site out/ [--mobile] [--throttle] [--no-3d]` |
| `measure_ui.py` | там же (23.09 19:29; исходно ui-research) | `getComputedStyle` видимых элементов: кегли, цвета, отступы, каркас; скриншоты; здесь — для структурных признаков (смена фона секций) | `python3 ../ui/measure_ui.py URL [--viewport 390x844] [--full-page]` |
| `ui_audit.py` | там же (23.09 19:29; исходно ui-research) | Визуальный QA по порогам ui-research. **На лендинге даёт ложные находки** (J2 «сайдбар», J8 `<header>` ≤ 120 px, H1–H2 кегли, A1 шкала до 96, B2 высоты кнопок, L5 гарнитуры — аудит UI §4.3, аудит KIMI §4 п.14): здесь только сырой замер; маркетинговый визуальный профиль — creative | `python3 ../ui/ui_audit.py URL --preset consumer --viewport 1440x900` · `--selftest` |
| `color.py` | там же (23.09 19:29; исходно ui-research) | WCAG 2 и APCA, hex ↔ OKLCH, ΔE, композитинг альфы; импортируется `measure_ui.py` и `ui_audit.py` | `python3 ../lib/color.py selftest` |
| `yt_dl.py` | там же (23.09 19:29; способ агента V ai-media) | Субтитры без HTTP 429: `meta` — метаданные; `subs` — **одна дорожка на ролик** (ручные на языке оригинала → автоматические `<язык>-orig` → ручные en/ru), ссылка из сохранённого `info.json`, пауза 6 с, при 429 — 90 и 120 с, после трёх роликов подряд с 429 — остановка; `comm` — 100 верхних комментариев; `pick` — показать выбор дорожки без сети. Файлы — `99-raw/youtube/{meta,subs,comments}/`, журнал `99-raw/youtube/yt_dl.log`. Список: id, после TAB — что угодно, `#` — комментарий | `python3 99-raw/tools/yt_dl.py meta ids.txt && python3 99-raw/tools/yt_dl.py subs ids.txt` |
| `vtt2md.py` | там же (23.09 19:29; пути исправлены оркестратором ai-media 23.09) | Транскрипты `91-videos/transcripts/<id>.md` из скачанных `.vtt` и метаданных без обращения к YouTube. **Список — только id по строке** | `python3 99-raw/tools/vtt2md.py 99-raw/youtube/ids_p1.txt` |
| `yt_transcript.py` | там же (23.09 19:29) | Поиск по YouTube без API (`--search "запрос" -n 20`) — для V; старый способ субтитров не использовать (есть `yt_dl.py`) | `python3 99-raw/tools/yt_transcript.py --search "запрос" -n 20` |
| `transcribe_local.py` | `../blender-research/99-raw/tools/` (23.09 02:35) | Локальное распознавание речи роликов без субтитров: Qwen3-ASR-1.7B Q8_0 через `llama-mtmd-cli` на CPU (около 0,43 реального времени: час речи — около 26 минут), нарезка по паузам на куски около 4 минут, докачка после обрыва; промежуточное — `99-raw/youtube/audio/<id>/`. Запускать по одному ролику, при `free -g` ≥ 3 ГБ | `python3 99-raw/tools/transcribe_local.py URL` |
| `asset_inventory.py` | `../ai-media-research/99-raw/tools/` (23.09 10:53; агент A ai-media) | Инвентарь визуальных ассетов живой страницы (картинки, CSS-фоны, видео, SVG, Lottie, canvas; сеть через CDP; LCP до прокрутки, CLS, TBT, og:image, фавиконы); десктоп 1440×900 или Pixel 7. Ограничения: cookie-баннеры не закрывает, антибот, один браузер за раз. Основа `page_anatomy.py` | `python3 ../ai-media/asset_inventory.py URL OUT_DIR [--mobile] [--quick] [--throttle]` |
| `page_accept.py` | `../ai-media/` | Приёмка страницы: вес первого экрана (CDP), LCP, CLS, TBT, `alt`/`width`/`height`, постер видео, движение на 6-й секунде и петли всей страницы, reduce записью всей страницы, контраст F83; пороги — профиль `--budget-profile` из `budgets.yaml` (вес — WARN), замки тишины берёт сама. INP не меряет, Safari нет | `../ai-media/page_accept.py PAGE.html\|URL --out DIR --budget-profile <page_type>@L<n> [--mobile] [--throttle]` |

## Будут добавлены агентами

Каждый агент дописывает **свой раздел в конец этого файла** (запуск, флаги, что меряет, ограничения, чем проверено) —
единственное общее место, куда пишут несколько агентов; чужие разделы не менять.

| Утилита | Назначение | Агент, волна |
|---|---|---|
| `page_anatomy.py` | Структура живой страницы: секции и их классы по словарю, призывы, формы и согласия, шапка и подвал, заголовки, мета, OG, JSON-LD, аналитика и cookie-баннер (закрытие «Отклонить»), LCP, CLS, TBT, лабораторный INP по сценарию (web-vitals `onINP`), поле CrUX (PageSpeed Insights API без ключа), доля текста без JS, телефон | M, 1 |
| `vocab_lint.py` | Идентификаторы в YAML и JSON — только из `../../kb/site/02-site-types/vocabulary.yaml` | B, 1 |
| `ia_probe.py` | Структура многостраничника: `robots.txt`, `sitemap.xml`, типы URL, глубина, шапка и подвал, крошки, `hreflang`, 404 (≤ 1 запроса в секунду, ≤ 200 адресов из sitemap) | G, 2 |
| `geo_probe.py` | Доступность для ИИ: правила `robots.txt` для ботов из `crawlers.yaml`, `llms.txt`, доля смыслового текста без JS, JSON-LD, `robots` и `X-Robots-Tag`, canonical, OG | H, 2 |
| `page_gates.py` | Ворота собранной страницы по профилю из `budgets.yaml` и `page-gates.yaml` поверх `page_anatomy.py`, `page_accept.py`, `motion_check.py`, `gate_check.py`, `geo_probe.py`, `ia_probe.py`, axe — раздел ниже | P, 2; K, 3 |
| `ab_plan.py` | Размер выборки и длительность A/B, проверка SRM | P, 2 |
| `checklist_export.py` | `../../kb/site/09-ai-generation-evaluation/site-checklist.yaml` из Markdown чек-листа | K, 3 |
| `site_validate.py` | Схемы и перекрёстные ссылки: блоки плана есть в `blocks.yaml`, слоты разрешены блоку, id фактов есть в брифе, действия и события — в словарях, у страниц карты есть планы | J, 3 |
| `plan_to_assets.py` | План ассетов страницы: каркас из медиа- и 3D-слотов плана страницы и проверка по схеме `../../kb/ai-media/05-prompting/asset-plan.schema.json` (формат — `../../kb/ai-media/01-web-assets-landscape/01-asset-slots-by-page-type.md` §8) — раздел ниже | J, 3 |
| `check_links.py` | Ссылки `→ §`, `../../kb/site/99-raw/`, `[S<n>]`, `[V:<id>]`, README папок, разделы формата, метки опытов — копия версии text, адаптированная оркестратором перед аудитом (не копия kimi, как планировалось); раздел ниже | оркестратор; правки X2, S1 — 4 |
| `sources_collect.py` | `90-sources/sources.tsv` и автоблок `90-sources/README.md` из разделов «Источники» и шапок дайджестов (копия версии text) | S1, 4 (v1.1 — S1b) |

Не скопированы намеренно: `yt_frames.py` (kimi; кадры видео — ролики трека вербальные; если W понадобятся слайды с
числами, оркестратор копирует утилиту и создаёт `91-videos/frames/`); `k3_checks.py`, `kimi_run.py`, `build_package.py`
(kimi) — используются на месте только для чтения и сухой проверки проекций.

## Правила

- Python-пакеты — только в venv внутри `99-raw/tools/` (`uv venv 99-raw/tools/venv-<буква>`); npm — в `99-raw/tools/node`
  или в папке опыта; `sudo` запрещён; глобально ничего не ставить.
- Браузер — один за раз и через блокировку: утилиты замера времени (`page_anatomy.py`, `page_accept.py`, `motion_check.py`,
  `site_probe.py`, `web_view.py`) берут замки тишины сами (общий тяжёлый, браузера, домена — `page_gates.heavy_lock`),
  остальные — `flock -w 900 $DDD_HOME/locks/browser.lock <команда>`; перед тяжёлым прогоном `free -g` ≥ 3 ГБ; фоновых
  процессов не оставлять.
- Клоны репозиториев — `99-raw/cache/repos/<org>__<repo>/` (`git clone --depth 1`); клоны kimi в
  `../kimi-research/99-raw/cache/repos/` — только читать.
- Ключи и токены не заводить и не печатать; PageSpeed Insights API — без ключа; платных вызовов нет; Kimi не запускать.
- При замерах: рекламу не кликать, формы не отправлять и в поля чужих сайтов ничего не вводить (для лабораторного INP —
  только фокус в поле; ввод символов — на своей тестовой странице), на cookie-баннере — «Отклонить», если есть.

## `ctx_watch.py` — сторож контекста агентов (оркестратор волн site, 24.09.2026)

Копия утилиты оркестратора волн text-research (`../text-research/99-raw/tools/ctx_watch.py`, 24.09.2026 11:21); изменён
только путь к транскриптам агентов: переменная окружения `CTX_WATCH_TASKS` или папка задач сессии оркестратора волн site.
Реализует правило заказчика «до автосжатия доводить не надо никогда» (`PLAN.md`, решение 17): контекст агента считается
точно по полю `usage` последнего ответа модели (`input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens`).
Реестр — `99-raw/notes/agents-running.tsv` (метка, id агента, статус `running | stopping | done`; ведёт оркестратор).

- `python3 99-raw/tools/ctx_watch.py status` — таблица: агент, контекст, время последнего ответа, число сжатий, пометка об
  ошибке API;
- `python3 99-raw/tools/ctx_watch.py watch --wrap 800000 --hard 900000 --every 60` — строка-событие при первом пересечении
  порога каждым агентом (WRAP — «ЗАКРУГЛЯЙСЯ СЕЙЧАС», HARD — жёсткая граница) и при новом автосжатии (COMPACT); для Monitor.

Агентам не нужен: им команды присылает оркестратор.
Путь по умолчанию в коде — папка задач сессии 1; сессия 2 (24–25.09) задаёт
`CTX_WATCH_TASKS=/tmp/claude-1000/<проект>/<id сессии>/tasks` (журнал оркестратора, 2026-09-24).

## `vocab_lint.py` — идентификаторы вне словаря и таблица соответствий

Проверяет YAML, JSON и Markdown на id, которых нет в `kb/site/02-site-types/vocabulary.yaml` (пространства `site_type`,
`page_type`, `section_role`, `block_family`, `block`, `slot_kind`, `slot`, `macrostructure`, `first_screen_policy`,
`action`, `awareness`, `traffic_temperature`, `traffic_source`, `jurisdiction`, `ambition_level`, `conversion_channel`,
`procedure_step`), и таблицу соответствий словарей `kb/site/02-site-types/crosswalk.tsv`. Только стандартная библиотека и
PyYAML; сеть и браузер не нужны.

- Запуск: `python3 scripts/site/vocab_lint.py kb/site/04-blocks/blocks.yaml kb/site/10-playbooks-contracts/examples/*/plans/*.yaml`
  · `--check-crosswalk` · `--selftest`.
- Что ловит: (1) значения ключей из карты по умолчанию (`page_type`, `site_type`, `role`/`section_role`/`serves`, `block`,
  `family`, `slot`, `slot_kind`, `macrostructure`, `action`/`primary_action`/`secondary_actions`, `awareness`,
  `temperature`, `traffic_source(s)`, `jurisdiction`, `ambition_level`) на любой глубине, строка или список; (2) ссылки с
  префиксом в любой строке и в Markdown (`block:`, `slot:`, `section-role:`, `page-type:`, `site-type:`, `action:`,
  `macrostructure:` …; чужие `effect:`, `fact:`, `task:`, `recipe:`, `copy-rule:` пропускаются); (3) ключи-id
  (`--keys-as-ids blocks=block`); (4) статусы: `deprecated` и `out-of-scope` — предупреждение (с заменой), `measurement-only`
  — ошибка (кроме `--allow-measurement`), `proposed` — сведение (`--show-info`); (5) `--check-crosswalk` — таблица
  соответствий: колонки строго по формату, `relation` из перечня `equal` · `narrower` · `broader` · `related` · `none`,
  `our_id` — id словаря своего пространства, у `none` — пустой `our_id` и причина в `note`; `deprecated` и повтор строки —
  предупреждение. Новый id — сначала словарь, затем строка таблицы; другой файл таблицы — `--crosswalk`.
- Карта: `--map KEY=NAMESPACE` (много раз); ключ с точкой — суффикс пути (`--map site.sections.id=section_role`);
  `--no-default-map` — для чужих форматов, где `role`, `family`, `id` значат другое.
- Подсказки: ближайший id при опечатке (`difflib`, порог 0,75); с `--crosswalk kb/site/02-site-types/crosswalk.tsv` — наш id
  для чужого термина (приоритет equal → narrower → related → broader; `--source-base` ограничивает базу); `--stats` —
  сводка mapped / none / absent.
- Выход: `путь:строка: уровень пространство 'id' — сообщение`, сводка; код 1 при ошибках. Номера строк — из узлов PyYAML
  (JSON разбирается тем же парсером).
- Ограничения: не проверяет, что слот разрешён блоку и что факт существует (это `site_validate.py`); строки чужих
  форматов без карты дают ложные ошибки — для них `--no-default-map`.

## `page_anatomy.py` — анатомия собранной или живой страницы

Структура и техника страницы за один прогон «страница × устройство»: секции с ролью (`section_role`) и блоком (`block`) по
словарю site, призывы, формы и согласия, шапка и подвал, заголовки, мета, Open Graph, JSON-LD, платформа, сторонние домены по
категориям, cookie-баннер и трекинг до выбора, LCP, CLS, TBT, FCP, TTFB, показ H1 во времени (`h1_paint`), лабораторный INP
по сценарию, текст без JS, контактный лист секций. Первое звено ворот после сборки: `anatomy_<устройство>.json` читает
`page_gates.py --anatomy`. Условия лаборатории — `budgets.yaml` `conditions` (через `page_gates.py`): окно первого экрана
(load + `window_after_load_s`), телефон — дескриптор Pixel 7 и CPU ×4, десктоп 1440×900; UA — как у браузера
(HeadlessChrome), признак автоматизации не выключается — сайт видит, что его меряет утилита. web-vitals — из npm-зависимостей
окружения (`$DDD_HOME/node`, ставит `install.sh`).

| Запуск | Что делает |
|---|---|
| `page_anatomy.py URL OUT [--mobile] [--inp] [--label PAGE_TYPE] [--id ID] [--market ru\|intl]` | одна страница; сама берёт замки тишины (общий тяжёлый, браузера, site — `page_gates.heavy_lock`), `--no-lock` — обёртка их уже держит; `--quick` — без прокрутки и листа; `--no-cmp-close` — баннер не трогать; `--timeout` (с), `--wait` (мс, по умолчанию — окно `budgets.yaml`), `--cpu N`; `--crux` — PSI (ключ только из `PSI_API_KEY`) |
| `page_anatomy.py --batch pages.tsv --out DIR [--devices desktop,mobile] [--inp] [--only a,b] [--skip-done]` | партия: замки тишины на каждую страницу × устройство (не дольше `--page-timeout` 270 с), ждёт `MemAvailable` ≥ 3 ГБ, журнал `<DIR>/batch.log` |
| `--reclassify DIR` · `--csv DIR --pages pages.tsv > pages.csv` · `--net-of HOST…` · `--crux-batch pages.tsv --out DIR` · `--selftest` | пересчёт классов без браузера; сводная таблица; страна и AS сервера (IP не печатается); поле CrUX; самопроверка — тестовые страницы во временной папке, без сети (32 проверки, в том числе честный UA и показ H1 из прозрачности) |

Выход: `OUT/anatomy_<desktop|mobile>.json` (поля `dom` — сырые признаки; `classes` — роли и блоки с top-3 и причинами;
`summary` — строка CSV; `network`, `cmp`, `inp`, `nojs`, `first_screen`, `h1_paint` — `first_op`, `t_first`, `t_visible`,
`t_opaque`, `in_first_screen`; `ua`, `webdriver`), `sheet_<устройство>.jpg` (контактный лист с границами и подписями секций),
`cmp_<устройство>.jpg` (кадр с баннером). Правила замера: рекламу не кликать, формы не отправлять и ничего не вводить (для
INP — только фокус), на баннере — «Отклонить», если есть; **«Принять» утилита не нажимает**.

**Точность классификатора** (опыт M/04, ручная разметка): границы секций верны у 84–85 % сегментов; роль верна у **62 %**
секций отложенной выборки, блок — у 36 %; при `conf` ≥ 0,5 роль верна в 86–92 %. Надёжны `hero`, `footer`, `faq`,
`pricing`, `testimonials`; размыты `benefits`, `related`, `seo-text`, `guarantee`, `contacts`. Для частот и
последовательностей брать роли с `conf` ≥ 0,5, остальные — подсказка.

Ограничения: лаборатория ≠ поле (сеть без замедления, телефон — эмуляция с CPU ×4); проба маршрута через эхо-сервисы
ненадёжна; PSI API без ключа — квота 0; INP — ≤ 4 взаимодействия после загрузки (занижает INP во время загрузки); антибот и
заглушки — `blocked`; сегментация срывается, когда подвал или общая обёртка проглатывают страницу (`seg_flag=fail`); слайды
hero на y = 0 и группы FAQ дают лишние секции; «умная» шапка, появляющаяся при прокрутке вверх, не ловится; страницы шире
экрана телефона расширяют область Chrome; сертификат НУЦ Минцифры (Russian Trusted CA) Chromium не принимает.

**Правка оркестратора волн site в `vocab_lint.py` (24.09.2026 15:25).** В карту ключей добавлены пути без id словаря
(значение `None` — ключ пропускается, строка только сканируется на префиксные ссылки): `references.role` (роль референса у
creative — `rhythm`, `composition` …; замечание creative в точке C1), `audience.role`, `languages.role`, `questions.block`
(поля `site-brief`, давшие 13 ложных ошибок на `01-foundations/site-brief.example.yaml`). Самопроверка — OK; пример брифа —
0 ошибок; `../../kb/site/04-blocks/` — без изменений (1 ошибка `block:service-area` — новый id для J); файлы C1 creative — 0 ошибок. 15:33 — добавлен `versions.role` (роль языковой версии в `site-map` G — ложная ошибка на примерах G).

## `page_gates.py` — ворота собранной страницы по профилю

Вердикт `accepted` / `accepted_with_notes` / `blocked` по `../../kb/site/07-seo-geo-performance-analytics/page-gates.yaml` с порогами
профиля `<page_type>@L<n>` из `budgets.yaml`; умолчание уровня по типу страницы и правило лидогенерации услуг (доля горячего
мобильного трафика и полосы цены) — поля `../../kb/creative/01-creative-direction/ambition-levels.yaml`. Браузер не запускает:
сводит JSON утилит ворот после сборки. Метрику страницы воротами ставит только он; те же метрики, измеренные соседями
(`motion_check.py`, зонд 3D), идут в отчёт зеркалом D и на вердикт не влияют; ворота эффектов и 3D — слоями отчёта
(`layers`). Числа строк без профиля — поле `limits` строки `page-gates.yaml`. Код-репо запускает утилиту соседним чекаутом
`../strategy/…/scripts/site/page_gates.py`; цепочка фазы `build`: `page_anatomy.py` →
`page_accept.py --budget-profile …` → `page_gates.py --profile … --anatomy … --accept …` (+ `--motion`, `--gate3d`, `--geo`,
`--ia`, `--axe`, `--plan`, `--html`).

| Запуск | Что делает |
|---|---|
| `page_gates.py --profile landing-lead-services@L1 --anatomy DIR [--accept DIR] [--motion DIR] [--gate3d FILE …] [--jurisdiction ru\|eu\|none] [--json]` | вердикт, строки PASS/FAIL/SKIP с порогом, серьёзностью и источником; код 1 при B, 2 — ошибка вызова |
| `page_gates.py --resolve landing-lead-services [--site-level L1] [--hot-mobile-share 0.6 --price-band mid]` | профиль (JSON: `id`, `level`, `page_type`, `outcome`, `weight`, `all_levels`, `log`) — его читает сборщик входа холста |
| `page_gates.py --conditions` | условия замера `budgets.yaml` для утилит: окно первого экрана, телефон, десктоп, замок тишины |
| `page_gates.py --selftest` | 105 проверок: строки и `limits` ворот, профиль и правило лидогенерации из данных, контракты JSON соседей, зеркала |

| Флаг | Что читает | Какие ворота |
|---|---|---|
| `--anatomy DIR` | `anatomy_<устройство>.json` `page_anatomy.py` | SG-PERF-01…06 (LCP-элемент, H1 в LCP с признаком показа H1), 09; SG-WEIGHT-01…07, 09 (видео — только D); SG-SEO-02, 03; SG-GEO-01; SG-MOB-01, 02; SG-CONTENT-07; SG-LEGAL-01…05, 07 |
| `--accept DIR` | `accept_<режим>.json` `page_accept.py`: поля `device`, `throttle`, `no_preference` (`lcp`, `first_screen_total_kb`, `weight_measured`, `dom.imgs`, `media_first`, `motion_6s`, `loops`, `console`), `reduce` (`media_kb`, `motion.fail`) | SG-PERF-01/02 (LCP с троттлингом), SG-PERF-06 (lazy, fetchpriority), SG-PERF-14, SG-PERF-16 (энтропия и площадь постера), SG-WEIGHT-01 без анатомии (прогон без замедления), SG-A11Y-03, SG-A11Y-07, SG-CONTENT-04 |
| `--motion DIR` | `<DIR>/results.json` (`<режим>.derived`, `vitals`, `cls`, `net`) и `<DIR>/gates.json` (`rows`) `motion_check.py` | SG-A11Y-03 (петли всей страницы), SG-A11Y-04 (вспышки), SG-A11Y-07 (EG-A11Y-05…07); зеркала LCP, TBT, CLS, веса и шрифтов; слой эффектов |
| `--gate3d FILE …` | JSON `gate_check.py --json` (`rows`: `id`, `check`, `value`, `limit`, `severity`, `status`, `mirror`) | SG-WEIGHT-08 (D), SG-CONTENT-04 (зонд), зеркала LCP, CLS, TBT и веса; слой 3D |
| `--geo FILE` | JSON `geo_probe.py` (флаги `head-kit.yaml checks`) | SG-SEO-01…05, SG-GEO-01…02 (строка `device: raw`) |
| `--ia FILE` | `<id>/ia.json` `ia_probe.py` | SG-SEO-01 (мягкая 404), SG-SEO-06, SG-SEO-08, SG-NAV-01, SG-NAV-02 |
| `--axe FILE` | узлы с адресами `run_axe_targets.py` или `axe.run` | SG-A11Y-01 (контраст ключевых узлов — B, прочих — S; без адресов — S, которое исключение не снимает), SG-A11Y-02 |
| `--plan FILE` | page-plan: `first_screen_policy`, `seo.indexable`, `seo.structured_data`, `x-gate-exception[{id, why, who, until}]` | SG-CONTENT-07; условия SEO; исключения (S снимается до `until`, B — никогда) |
| `--html FILE`, `--css FILE …` | сохранённый HTML и CSS | SG-CONTENT-05, SG-CONTENT-06, признаки невидимого H1 (SG-PERF-06), SG-A11Y-08 (clamp кеглей) |
| `--ai-bots-policy`, `--ads-google` | условия брифа для флагов ботов | закрытые ИИ-боты при `deny-all` — не дефект; AdsBot — B только для посадочной под Google Ads |

Замер без троттлинга сети (анатомия телефона) для SG-PERF-01 помечается `lab-unthrottled` — диагностика, не приёмка; для
приёмки — `page_accept.py --mobile --throttle`. Ограничения: сторонние КБ первого экрана — верхняя оценка (КБ домена за
сессию); INP-сценарий после загрузки занижен; классы узлов контраста и распознавание призыва — эвристики, ключевой провал
подтверждать кадром. Модуль для утилит замера: `resolve_profile()`, `profile_value()`, `conditions()`, `cdp_network()`,
`mobile_device()`, `heavy_lock()` — одно место условий лаборатории и тишины машины.

## `ab_plan.py` — план и проверка A/B (агент P, волна 2, 2026-09-24)

Только стандартная библиотека. Подкоманды: `size` (выборка на вариант: точная формула без объединения дисперсий и правило
16σ²/δ²; Бонферрони для A/B/n; при `--visits-per-day` — полные недели и вердикт ok / long / infeasible), `duration`, `mde`
(обнаружимый эффект за N недель), `srm` (хи-квадрат, порог ExP p < 0,0005; код 2 при SRM), `fpr` (риск ложной победы по доле
успешных идей; α для FPR 5 %), `analyze` (SRM → z-тест двух долей, интервалы, FPR, флаги: план не набран, Твиман > +30 %,
0,01 < p < 0,05 → повтор), `peeking` (ложные при k просмотрах и порог Pocock симуляцией). `--json` — машинный вывод.

- Примеры: `python3 ab_plan.py size --base 0.03 --mde-rel 0.2 --visits-per-day 300`;
  `python3 ab_plan.py srm 5104 4893`; `python3 ab_plan.py peeking --looks 14`.
- Проверено: `--selftest` 35/35 — опыт A/04 (4 строки), Kohavi–Deng–Vermeer 2022 (16σ²/δ² = 41 642; 15 значений FPR; α 0,0016;
  пост-хок 74 %), Fabijan 2019 (χ² 22,77, p 1,8·10⁻⁶), пороги Pocock / Evan Miller для 2–11 анализов, Монте-Карло мощности и
  ложных; опыт `99-raw/experiments/P/01-ab-plan-selftest/`.
- Ограничения: доли (конверсии), не средние выручки; последовательные always-valid методы не реализованы; биномиальная
  выборка в самопроверке — нормальное приближение.

## `ia_probe.py` — структура многостраничника по HTTP

Меряет устройство сайта целиком, без браузера: robots.txt → sitemap.xml (индексы, gzip, `hreflang` и `lastmod` в sitemap,
относительные `<loc>`) → адреса (шаблоны путей, тип раздела по сегменту — русский транслит и английский, глубина, языковые
префиксы и поддомены, гигиена: параметры, слэш, регистр) → страницы только из sitemap плюс корень: шапка (пункты верхнего
уровня, подменю, признаки мега-меню, поиск, телефон, вход, переключатель языка, кнопки), подвал (ссылки, группы,
юридические ссылки, реквизиты, соцсети, «Карта сайта»), крошки (HTML и BreadcrumbList в JSON-LD, microdata, RDFa),
`hreflang` в `<head>`, canonical, title, H1, контекстные ссылки и блоки «читайте также» → ответ на несуществующий адрес
(честная 404, мягкая 404, редирект на главную). Python 3.13, только стандартная библиотека. Код-репо запускает утилиту
соседним чекаутом (`../strategy/…/scripts/site/ia_probe.py`); выход без `--out` —
`$DDD_HOME/out/site/ia_probe/`; `<id>/ia.json` читает `page_gates.py --ia`.

| Запуск | Что делает |
|---|---|
| `python3 ia_probe.py https://example.ru --out DIR [--id ID] [--sample 14]` | один сайт → `DIR/<id>/ia.json`, `ia.md`, `pages/NN.html.gz`, `sitemap_urls.txt.gz`; коротко — в stdout |
| `python3 ia_probe.py --batch sites.tsv --out DIR [--skip-done]` | партия по TSV `id, url, site_type, market, note`; `--skip-done` пропускает сайты с готовым `ia.json` |
| `python3 ia_probe.py --summary DIR > DIR/summary.tsv` | сводная таблица по всем `ia.json` (44 колонки) |
| `python3 ia_probe.py --reanalyse DIR` | пересчёт разбора по сохранённому HTML без сети (после правки эвристик) |
| `python3 ia_probe.py --selftest` | 26 проверок на локальном сервере с фикстурами |

Флаги: `--delay` (с, не меньше 1), `--budget` (запросов на сайт, не больше 200), `--sample` (страниц из sitemap, по умолчанию
14), `--max-sitemaps` (файлов sitemap, по умолчанию 12), `--timeout` (с, по умолчанию 20; проба 404 — 30), `--no-save-html`.

- **Вежливость** (условие задания G): ≤ 1 запроса в секунду на хост, каждый редирект — отдельный запрос с паузой; ≤ 200
  запросов на сайт (robots, sitemap, страницы, проба 404; на 20 сайтах G/01 — 5–36); страницы — только адреса из sitemap и
  корень, по ссылкам не ходит; robots.txt по RFC 9309: 4xx — ограничений нет, 5xx или недоступен — страницы не
  запрашиваются; `Crawl-delay` соблюдается до 10 с; адреса под `Disallow` пропускаются; антибот (ответ 401, 403, 429, 503 или
  заглушка Cloudflare, DDoS-Guard, Qrator при малом числе ссылок и слов) — отметка `blocked` и остановка без обхода; после
  сетевой ошибки — один повтор через 5 с. User-Agent называет утилиту и её правила.
- **Выборка** детерминированная: по странице из крупнейших шаблонов пути (середина отсортированного списка), затем вторые
  и третьи, плюс самая глубокая страница — не больше 3 страниц с шаблона; при одном шаблоне в sitemap выборка мала (croc в
  G/01 — 5 страниц).
- **Выход**: `ia.json` — `robots`, `sitemap` (файлы, число URL, `lastmod`, `hreflang`, `relative_locs`), `urls` (хосты,
  глубина, шаблоны с примерами, типы разделов, языковые префиксы, гигиена), `pages` (по странице: шапка, подвал, крошки,
  поиск, язык, `hreflang`, canonical, title, H1, ссылки), `not_found`, `summary`, `request_log`, `politeness`; `ia.md` —
  коротко для человека.
- **Сводка** (`--summary`): `robots`, `sm_declared`, `sm_files`, `urls`, `main_host_share`, `depth_med`, `depth_p90`,
  `depth_max`, `templates`, `lang_prefixes`, `sm_hreflang_urls`, `hreflang_pages`, `header_method` (`header-tag`, `class`,
  `none`), `header_top`, `dropdown`, `mega`, `max_sub`, `search_any`, `search_in_header`, `phone`, `login`, `lang_switch`,
  `footer_links`, `footer_groups`, `footer_legal`, `requisites`, `sitemap_link`, `crumbs_inner_pct`, `crumbs_deep_pct`
  (доля страниц глубины ≥ 2 с крошками в HTML или BreadcrumbList), `bc_ld_pct`, `related_pages`, `content_links_med`,
  `tpl_from_home_pct` (доля шаблонов пути со ссылкой прямо с главной), `home_links_not_in_sm`, `header_semantic_issue`,
  `sm_relative_locs`, `sampled_redirecting`, `sampled_errors`, `not_found`, `blocked`, `requests`. Шапка, подвал, телефон
  и поиск в шапке — по главной; крошки, поиск, язык, `hreflang` — по всей выборке.
- **Проверено**: `--selftest` 26/26 (опыт `99-raw/experiments/G/00-selftest/`, повтор 24.09 16:22); пилот на 3 сайтах нашёл
  6 дефектов разбора — исправлены; 20 многостраничников, 13 русских (опыт `99-raw/experiments/G/01-ia-probe/`);
  предварительная сверка с браузерным замером M (`../../kb/site/02-site-types/pages.csv`) на 4 общих доменах.
- **Ограничения**: без браузера не видит меню, панели и телефон, которые вставляет скрипт (браузер M видит мега-меню у
  kontur и practicum и телефон в шапке у stamus, которых нет в исходном HTML), и видимость элементов на телефоне; счёт
  пунктов шапки включает утилиты и списки языков; подвал без `<footer>` и узнаваемого класса не находит; реквизиты и
  подписи — эвристики; у сайтов с уникальными путями шаблоны дробятся (artlebedev — 716 шаблонов на 6815 URL); уникальность
  содержимого серий не проверяет. Годится как автопроверка собранного сайта (ссылки навигации в исходном HTML, код 404,
  sitemap с абсолютными каноническими URL, крошки по глубине) — предложение K и J.

## `geo_probe.py` — доступность страницы для поисковых и ИИ-ботов

Что видит бот без исполнения JS: для каждого бота из `../../kb/site/07-seo-geo-performance-analytics/crawlers.yaml` — разрешён ли URL в
robots.txt (RFC 9309 + особенности платформ: цепочки групп «YandexBot → Yandex → *», «Applebot → Googlebot → *»,
AdsBot-Google и YandexAdditional без группы `*`); код, размер, BOM, `Sitemap`, `Content-Signal`, `Content-Usage`, блок
Cloudflare Managed в robots.txt; `/llms.txt` и `/llms-full.txt` (Markdown по llmstxt.org или HTML-заглушка); страница —
код, редиректы, `X-Robots-Tag`, CDN и антибот-заглушка, несжатый размер HTML и смещения `</head>`, первого H1 и последнего
`og:*`; head (title, description, robots для `robots`/`googlebot`/`yandex`/`bingbot`/`applebot`, canonical, hreflang, lang,
OG, Twitter); текст без JS (определения как у M `nojs_compare`: слова вне `script, style, noscript, template, svg, iframe,
object, head, canvas`), H1, цены, призывы, признаки SPA и платформы; JSON-LD (разбор, `@type` с `@graph`, базовые
обязательные свойства по документации Google, `sameAs`, `@id`) и микроразметка. Python 3.13 + requests 2.32 + PyYAML 6.0;
для `--render` — Playwright 1.63 + Chromium. Код-репо запускает утилиту соседним чекаутом
(`../strategy/…/scripts/site/geo_probe.py`); выход партии без `--out` —
`$DDD_HOME/out/site/geo_probe/`; JSON читает `page_gates.py --geo`.

| Запуск | Что делает |
|---|---|
| `python3 geo_probe.py URL [--out DIR] [--id ID]` | одна страница, только HTTP; печатает флаги и решения robots.txt по ботам, JSON — в `DIR/<id>.json` |
| `… URL --render` | + Chromium без взаимодействия: доля слов без JS, H1 и главный призыв в сыром HTML, цены, JSON-LD только из JS; сам берёт обе блокировки браузера и ждёт `MemAvailable` ≥ 3 ГБ |
| `… URL --ua-probe` | + запросы с UA Googlebot, YandexBot, OAI-SearchBot, GPTBot, PerplexityBot, ClaudeBot: код и объём против браузерного UA (только сигнал: WAF законно режет поддельный UA с чужого IP) |
| `… --batch pages.tsv --out DIR [--render] [--ua-probe] [--only a,b] [--skip-done] [--insecure-retry]` | партия; `pages.tsv` — колонки `id` и `url` (остальные — в `meta`), журнал `DIR/batch.log`; `--insecure-retry` читает страницу с недоверенной цепочкой TLS (сертификат НУЦ «Russian Trusted Sub CA») без проверки и ставит флаг `tls-untrusted-chain` |
| `… --summary DIR > summary.tsv` · `--revalidate DIR` · `--crawlers PATH` · `--selftest` | сводная таблица (57 колонок); пересчёт JSON-LD и решений robots.txt по сохранённым данным без сети; другой каталог ботов; самопроверка |

Флаги (`flags` в JSON; серьёзность B/S/D — `head-kit.yaml` `checks`, сведения — `info_flags`; строки ворот — SG-SEO-01…04,
SG-GEO-01…02 в `page-gates.yaml`): `page-status-<код>`, `antibot-challenge`, `tls-untrusted-chain`, `html-over-2mb`,
`og-after-1mb`, `noindex`, `nosnippet`, `noarchive-or-nocache`, `no-title`, `no-description`, `no-canonical`,
`multiple-canonical`, `canonical-elsewhere`, `no-lang`, `no-og-image`, `og-image-relative`, `no-h1-in-raw`, `multiple-h1`,
`raw-text-under-50-words`, `raw-text-under-200-words`, `csr-shell`, `no-jsonld`, `jsonld-parse-error`,
`jsonld-missing-required`, `robots-5xx-or-unreachable`, `robots-is-html`, `robots-star-disallow-all`, `blocked-<id бота>`
(Googlebot, YandexBot, YandexAdditional, OAI-SearchBot, PerplexityBot, Claude-SearchBot, bingbot, AdsBot), `content-signal`,
`cloudflare-managed-robots`, `llms-txt`; с `--render` — `nojs-ratio-under-0.5`, `h1-js-only`, `cta-js-only`,
`prices-js-only`, `jsonld-js-only`; с `--ua-probe` — `ua-<бот>-status-<код>`, `ua-<бот>-text-differs`.

Правила: ≤ 1 запроса в секунду на хост, повтор при сетевом сбое через 5 с; формы не отправляет, ничего не вводит, по рекламе не
ходит; браузер — только с `--render`. Ограничения: без `--render` не видит текст, меню и телефон, которые вставляет скрипт
(для них — `page_anatomy.py` M); `--ua-probe` не заменяет «Проверку URL» Search Console и «Проверку ответа сервера»
Вебмастера — настоящих IP ботов у утилиты нет; что видят зарубежные боты на российских сайтах (TLS, антибот) — только с
зарубежного адреса; сопоставление групп Яндекса — по цепочке токенов из `crawlers.yaml`, а не по любой подстроке «Yandex»;
при robots.txt длиннее 4 000 символов `--revalidate` решения по ботам не пересчитывает (в JSON хранится начало файла);
распознавание антибот-заглушек и CTA — эвристики (регулярные выражения). Проверено: `--selftest` 33/33 (разбор групп,
самое длинное совпадение, `$` и `*`, регистр токена, цепочки Яндекса и Apple, AdsBot без `*`, JSON-LD с `@graph`, вложенные
отзывы, FAQPage, `llms.txt` против HTML-заглушки); опыты `99-raw/experiments/H/01-geo-probe-corpus-d/` (116 страниц корпуса
text D) и `H/02-geo-probe-sample-m/` (52 посадочные M; пересчёт X2 на итоговой выборке — 70, ответили 69) — без браузера.

## `checklist_export.py` — чек-лист site в YAML

**`checklist_export.py`** — `../../kb/site/09-ai-generation-evaluation/site-checklist.yaml` из `02-site-checklist.md` (образец —
`../ux/checklist_export.py`). Разбирает строки `| SITE-<БЛОК>-<NN> | … | B|S|D | способы | источник |`
и каталог `| DEF-<NN> | … | step:… | ловят | маркер |`; поля пункта: `block`, `text`, `severity`, `check_method`,
`check_method_class`, `auto_gate` (false у JDG и HUM), `source_file` (пути от корня базы; чужие базы — `../<база>/…`),
`source_section`, `evidence_level`, `videos`, `related_ids` (UX-, AC-, COPY-, CRV-, SG-, LR-, AIL-, DEF-, SITE-). Проверки
целостности: повтор id, блок строки = раздел, способы из словаря, номера подряд, ссылки DEF → SITE, ссылки AIL → `ai-landing-markers.yaml`,
существование файлов-источников. Запуск: `python3 checklist_export.py` (запись и сводка) · `--check` (YAML
совпадает с Markdown, код 1 — нет) · `--selftest` (16 проверок разбора) · `--md FILE --out FILE`. Только стандартная
библиотека (PyYAML — если есть — для проверки валидности).

## `site_validate.py` — схемы и перекрёстные ссылки контрактов сайта

Проверяет бриф (`site-brief`), план страницы (`page-plan`), карту сайта (`site-map`), каталог блоков и наборы форм по схемам
v1 `kb/site/10-playbooks-contracts/schemas/` и связи между ними; файл другой версии — ошибка схемы. Коды находок —
`kb/site/10-playbooks-contracts/01-procedure-brief-to-pages.md` §12. Нужны PyYAML, jsonschema и referencing: в системном
python без них утилита перезапускается Python окружения скилла. Сеть и браузер не нужны.

| Запуск | Что делает |
|---|---|
| `python3 scripts/site/site_validate.py PATH… [--today ГГГГ-ММ-ДД] [--json OUT] [--quiet]` | тип файла по ключам: бриф (SB-*), план (PL-*), карта (SM-*), каталог (BL-*), формы (LF-*); папка поверхности — бриф, факты, карта и планы `plans/<page-id>.yaml` (PJ-*); код 1 при error |
| `python3 scripts/site/site_validate.py --all` | каталог блоков, наборы форм и примеры `kb/site/10-playbooks-contracts/examples/` |
| `python3 scripts/site/site_validate.py --selftest` | пример `lead-services-otves` проходит; посеянные дефекты падают каждый своим кодом |

- **Бриф.** Бренд продукта — ссылкой `brand.ref` на `docs/projects/<slug>/design/brand.yaml` (путь от брифа): файла
  нет — SB-B01, файл не проходит схему `kb/common/brand.schema.yaml` — SB-B02. Темы `themes`: две темы без переключателя
  (`switcher: true`) — SB-C01; тёмная или «по системе» без второй темы — SB-C02; при двух темах умолчание не по системе —
  SB-C03 (ui 11/03 §6.4).
  Правило лидогенерации услуг (SB-A03) — поля `levels[id=L0].appropriate_for.lead_services` файла
  `kb/creative/01-creative-direction/ambition-levels.yaml`: тип страницы, порог доли горячего трафика с телефонов, полосы
  цены, уровень без данных о трафике и уровень, когда порог не достигнут.
- **План.** Умолчания уровня по типу страницы (PL-P02) — `defaults_by_page_type` того же файла вместе с разделом
  `proposed`. Подача (PL-C01) — находки `scripts/creative/spec_check.py plan` (нормы подачи ведёт creative): уровень
  секции, конверсия, пики, акценты, фирменные приёмы, референсы, петли, плавная прокрутка; проверяется, когда в плане
  заполнены контейнеры `treatment`. Уровни эффектов секций и переходов страниц (PL-C02) — `x-effect-levels` подсхемы
  `treatment` и `limits.library_level_min` эффекта `page-transition` (`kb/creative/06-effects-catalog/effects.yaml`):
  нативный кросс-документный переход — с L1, библиотеки и JS-переходы — L2. 3D-слот: рецепт `recipe:<id>` есть в
  `kb/blender/12-recipes/` (PL-D02); ниже первого экрана загрузка по намерению `on-interaction`, `on-visible` — риск длинных
  кадров прокрутки (EG-PERF-01), `after-lcp` — предупреждение (PL-D03).
- **Ограничения:** длины текстов — text; порядок ролей из осведомлённости — человек и судья.
- Схемы v0 и v0.9 (`kb/site/01-foundations/site-brief.schema.json`, `kb/site/04-blocks/page-plan.schema.json`,
  `kb/site/04-blocks/blocks.schema.json`, `kb/site/06-multipage-ia/site-map.schema.json`) утилиты скилла не читают.

## `plan_to_assets.py` — план ассетов страницы: каркас и проверка

План ассетов — файл `docs/projects/<slug>/design/<surface>/assets/plans/<page-id>.yaml` в формате ai-media 01/01 §8, схема —
`../../kb/ai-media/05-prompting/asset-plan.schema.json`; канон слоя — `docs/projects/_template/design/README.md § Ассеты`.
Id — словарь site: `page.page_type`, `slots[].slot`, `slots[].section` — id секции плана страницы; класс ai-media
`page.media_class` — проекция по строке §8 `../../kb/site/02-site-types/crosswalk.tsv`. Утверждает заказчик до генерации:
`status: approved` и `approval`.

| Запуск | Что делает |
|---|---|
| `plan_to_assets.py PAGE_PLAN [--out F]` | каркас из файла плана страницы: строка на медиа- и 3D-слот (`<секция>-<id>`), `source` (постер 3D-слота — `render`), `key` у визуала и фона первого экрана и постера 3D, `alt_ref`, `three_d`, бюджеты профиля; размер, форматы, вес, предмет и дорога 3D — заглушки `TODO` |
| `plan_to_assets.py --check FILE … [--plan PAGE_PLAN] [--json]` | проверка плана ассетов — находки контракта `../project/findings.py`: форма по схеме и id словаря (R-STRUCT-005), поля утверждённого плана (R-MAT-002), покрытие слотов плана страницы, подлинность и постеры (R-COV-004), ссылки (R-REF-001) |
| `plan_to_assets.py build <slug> [<surface>] [--page ID] [--out DIR] [--write]` | каркасы страниц поверхности со слоем страницы: в `$DDD_HOME/out/site/plan_to_assets/<slug>/` или `--out`; `--write` — в проект, только на пустое место |
| `plan_to_assets.py check <slug> [<surface>] [--json]` | планы ассетов проекта: всё из `--check`, план ассетов у страницы с медиа- и 3D-слотами, `refs.asset_plan` плана страницы, утверждённое на неутверждённом (R-MAT-001) |
| `plan_to_assets.py --spec-role FILE SLOT` | блок `role` спецификации ассета (`asset-spec.schema.json`): `page_type` словаря и проекция `page_class` |
| `plan_to_assets.py --types [new\|all]` | каркас на каждый тип страницы словаря (new — типы v1) из плана-образца и его проверка |
| `plan_to_assets.py --selftest` | примеры баз (пересборка байт в байт), посеянные дефекты, 3D, типы страниц, фикстура `asset-plan` сборщика `../tests/fixture_project.py` |

Корень данных — `--repo`, переменная `DDD_REPO` или репозиторий скилла; код выхода 0 — нет `error`, 1 — есть, 2 — вызов или
окружение.

## `build_profile.py` — маркетинговый профиль UX-чек-листа

Решение по каждому пункту `UX-*` сводного чек-листа ux для страниц сайта — `keep`, `modify`, `off` или `replaced` с
заменой `SITE-*`, `CRV-*`, `COPY-*`, причиной и основанием: `kb/site/09-ai-generation-evaluation/ux-marketing-profile.tsv`;
рядом — наследование автопроверок `AC-*` (`kb/site/99-raw/experiments/K/02-ux-profile/ac-profile.tsv`) и сводка в
`$DDD_HOME/out/site/build_profile/`. Решения — по блокам с точечными исключениями в коде утилиты: профиль — производный
файл, правится решением в утилите и пересборкой. Только стандартная библиотека и PyYAML.

| Запуск | Что делает |
|---|---|
| `python3 scripts/site/build_profile.py` | пересобрать профиль, `ac-profile.tsv` и сводку |
| `python3 scripts/site/build_profile.py --check` | профиль на диске совпадает с решениями, версия чек-листа ux сверена; ничего не пишет; код 1 — нет |
| `python3 scripts/site/build_profile.py --selftest` | сверка версии, число строк, замены и основания — на подложенных данных |

- **Сверка с версией чек-листа ux.** Решения сверены с версией `CHECKLIST_REVIEWED` (поле `source_sha256_16`
  `kb/ux/12-evaluation-checklists/master-checklist.yaml`). Новая версия — запись и `--check` отказывают со списком новых,
  снятых и изменённых пунктов против профиля на диске: новый пункт без точечного решения получает умолчание блока,
  изменённый пункт с точечным решением — на пересмотр. После сверки версия записывается в `CHECKLIST_REVIEWED`, профиль
  пересобирается отдельным коммитом.
- **Проверки строк:** число строк — `items_count` чек-листа; у `replaced` есть замена; `SITE-*` — в `site-checklist.yaml`,
  `COPY-*` — в чек-листе или рубрике text, `CRV-*` — в определениях creative; путь-основание в колонке `source` (от
  `kb/site/`) ведёт в существующий файл или папку; пункты, которые аудит UX назвал спорными для лендинга, — не `keep`.

## `sources_collect.py` — сводная библиография (агент S1, волна 4, 2026-09-25; v1.1 — продолжатель S1b)

Собирает `90-sources/sources.tsv` (8 колонок: `url, title, author_org, year, type, used_in, reliability, notes`) и автоблок
сводки `90-sources/README.md` (текст между `<!-- sources_collect:begin -->` и `<!-- sources_collect:end -->`) из разделов
«## Источники» содержательных файлов папок 01–10 и шапок дайджестов `91-videos/digests/`. Копия
`../text-research/99-raw/tools/sources_collect.py` (S1b text, 2026-09-24; её образец — ux), адаптированная скриптом
`99-raw/experiments/S1/sources/adapt_from_text.py` (30 проверенных замен: соседи и сёстры site, буквы агентов site без
точки — «J. Wiebe» не агент J, демо-наборы «Отвес», «Окошко», «Сталькон», домены стандартов, надзоров, данных, вендоров
CRO и конструкторов, директивы ЕС вида `2005/29/EC`). Только стандартная библиотека; сеть и браузер не нужны; файлы базы
и соседей только читает, пишет только `90-sources/` (или `--out`).

| Запуск | Что делает |
|---|---|
| `python3 99-raw/tools/sources_collect.py` (или `--write`) | пересобрать `sources.tsv` и автоблок README; ручные разделы README не трогает |
| `python3 99-raw/tools/sources_collect.py --check` | собрать во временную папку и сравнить: код 0 — TSV и автоблок (без даты сборки) совпадают, 1 — нет (до 5 строк расхождения) |
| `python3 99-raw/tools/sources_collect.py --selftest` | офлайн-тест на мини-базе во временной папке: 32 проверки (нормализация URL, деление записей, слияние законов, ролики, соседи, кэш, README, ручная таблица типов) |
| `… --stats` · `… --unparsed` | сводка без записи; внутренние записи, пути соседей не на диске, снятые таблицей и оставшиеся `web` — с ключами записей |
| `--out ФАЙЛ` · `--no-readme` · `--root ПУТЬ` | TSV в другой файл; без автоблока; другой корень базы |

- Метод, колонки, типы, уровни надёжности, не открывшиеся источники и ограничения — ручные разделы `90-sources/README.md`.
- **v1.1 (S1b):** таблица `TYPE_OVERRIDES` — ключ записи → тип или None («не источник»): 22 записи с типом `web` размечены
  (research 8, vendor 6, media 7, practice 1), 3 ссылки на файлы базы, принятые за внешнюю работу, сняты; ключ таблицы без
  записи — строка «ВНИМАНИЕ» в сводке; `--write` — псевдоним пересборки. Прежняя версия —
  `99-raw/experiments/S1/sources/sources_collect.before-S1b.py`; журнал — `99-raw/experiments/S1/journal.tsv`.
- Проверено (2026-09-25): `--selftest` 32/32; `--check` — совпадает: 389 источников (607 записей 30 файлов и 16 дайджестов;
  внутренних 91, влито 22, снято таблицей 3). Коды выхода: 0 — готово или совпадает; 1 — расхождение или падение самотеста;
  2 — ошибка входа.
- Ограничения: название, автор, год и тип — эвристики версии text, для site не калибровались (огрехи названий — README
  `90-sources/`); надёжность — по меткам и словам-пометкам записи, а не повторная проверка; один источник под разными
  адресами — несколько строк.

## `check_links.py` — перекрёстные ссылки и структура базы (оркестратор волн site, 24.09.2026; правки X2 и S1 — волна 4)

Копия `../maint/check_links.py` (версия X2 text, 24.09.2026; md5 исходника в докстринге), адаптированная
оркестратором перед аудитом волны 4: соседи ux, ui, ai-media, blender, kimi и сёстры text и creative (text — только как
«text-research» или «text NN»: слово text в базе ещё и `slot_kind`), буквы агентов site → папки 01–10 и 91, `schemas/` среди
подпапок, самопроверка на мини-базе site. Обходит `.md` папок 00–10, 90, 91 и корня (`README.md`, `PLAN.md`), а этот
README — только для проверок (а) и (ж). Только стандартная библиотека.

Проверки: (а) относительные пути к файлам и папкам, в том числе соседей (многоточие — префикс, `*` — глоб, диапазон `01–04` —
оба конца); (б) ссылки на разделы `§N.M` — есть ли заголовок в целевом файле; (в) `[S<n>]` — определён ли номер в
«Источниках»; (г) `[V:<id> mm:ss]` — дайджест, транскрипт или строка каталога, таймкод не больше длительности; (д) README
папок против диска и заявленное в таблице число строк; (е) обязательные разделы содержательных файлов и дайджестов (формат
W site); (ж) метки опытов → папки опытов (свои, соседей, сестёр). Уровни ERROR, WARN, INFO; код 1 при ERROR.

| Запуск | Что делает |
|---|---|
| `python3 ../maint/check_links.py [--quiet-info]` | отчёт в stdout: сводка по проверкам (а)–(ж) и находки |
| `… --out ФАЙЛ` · `--json ФАЙЛ` · `--only а,б` · `--no-raw` · `--root ПУТЬ` | отчёт в файл; находки в JSON; только названные проверки; без этого README; другой корень |
| `python3 ../maint/check_links.py --selftest` | офлайн-тест на временной мини-базе |

- Правки X2 (8; в коде — «X2 site»; копия до правок — `99-raw/experiments/X2/check_links.orig.py`; подробно —
  `99-raw/reports/wave4-X2-checks.md`): «аудит MEDIA / KIMI / UI / BLENDER §N» — заметки аудита соседей; буква агента со
  скобкой перед номером файла — папка агента; «→» в конце строки и «§N» на следующей — свой файл; «§N этого файла»; пустое
  `[V:]` — формат, не ссылка; разделы дайджеста — по формату W site; опыт соседа по пути `../../<база>/99-raw/experiments/…`;
  префикс базы действует на перечень опытов через «,» и «и». X2b утилиту не правил. Правка S1: метка опыта сестры вида
  «проверено: text A/01» (копия до правки — `99-raw/experiments/S1/check_links.before.py`; журнал S1).
- Проверено: самопроверка 27/27 (оркестратор) → 37/37 (X2) → **39/39** (S1); по базе 2026-09-25 — ERROR 0, WARN 0.
- Ограничения: ссылки на внешние документы (законы, WCAG, условия вендоров), на отчёты и заметки агентов («отчёт A §4») и на
  источники вида «S1 §14» не проверяются (INFO); путь от корня базы внутри подпапки принимается (INFO).

## `orch_check.py` и `extract_for_audit.py` — приёмка и извлечения для аудита (оркестратор волн site, 24.09.2026)

**`orch_check.py`** — приёмочная проверка файлов (основа — утилита оркестратора волн text; списки папок, меток и утилит — site).
Python 3.13 + PyYAML.

- Запуск: `python3 ../maint/orch_check.py all` (папки 00–10, 90, 91) или по папкам:
  `python3 ../maint/orch_check.py 03-page-structure 90-sources`; `--selftest-tools` — ещё `--selftest` утилит агентов
  (`vocab_lint.py`, `page_anatomy.py`, `ia_probe.py`, `geo_probe.py`, `page_gates.py`, `ab_plan.py`, `checklist_export.py`,
  `site_validate.py`, `site_brief_to_kimi.py`, `plan_to_assets.py`; тайм-аут 600 с на утилиту). Ключ `--md` есть в справке,
  но не реализован. Код 1 — есть error.
- Содержательный `.md` (не README и не `91-videos/`): пять обязательных разделов формата (warning), строка метаданных, число
  строк (info: меньше 150 или больше 700), пометка `<!-- ЧЕРНОВИК` (первой строкой — error); у любого `.md` — метки
  доказательности (известные и незнакомые: слово кириллицей в квадратных скобках вне таблицы меток), штампы стиля
  («является», «данный», «важно отметить» и др.), ссылки `](../…)`, `](NN-…)` и `../…` в обратных кавычках (warning, если
  цели нет ни от файла, ни от корня); YAML — загрузка (error) и поле `date` (info); JSON — загрузка (error), у
  `*.schema.json` — `$schema`; README в папке с файлами (кроме 00, 90, 91).
- Правка сессии 2: скобки внутри кода в обратных кавычках — не метки (перед поиском незнакомых меток код вырезается).
- Проверено (2026-09-25): `all` — 131 файл, 0 ошибок. Ограничения: акты приёмки примеров J
  (`10-playbooks-contracts/examples/*/acceptance-site.home.md`) проверяются как содержательные файлы — 3 ложных
  предупреждения о разделах формата (отмечено X2); ссылки на разделы `§` не проверяет (это `check_links.py`).

**`extract_for_audit.py`** — компактные извлечения базы для аудитора X и синтезатора S (основа — утилита оркестратора волн
text; урок ux и text: аудитор гибнет на чтении больших файлов). Только стандартная библиотека; сеть и браузер не нужны; базу
только читает.

- Запуск: `python3 99-raw/tools/extract_for_audit.py [--out 99-raw/notes/wave4/extracts] [--only 09-ai-generation-evaluation]`;
  перезаписывает файлы в `--out` (извлечения волны 4 — `99-raw/notes/wave4/extracts/`, их готовит оркестратор: перед X и
  после правок X2 — перед S).
- Выход: `<папка>.md` для 01–10 (у содержательных файлов — заголовок, метаданные, «Выжимка», «Открытые вопросы», «Чек-лист»;
  README — целиком; YAML и JSON — строки, ключи, `version`, `status`, `checked` или `date`; TSV и CSV — строки и шапка);
  `reports-wave<N>.md` (из отчётов волны: находки, противоречия и слабые места, «что учесть», живая фаза, предложения,
  пробелы, термины, «не удалось»); `amendments.md` (строки «Поправка к …» и таблица поправок `PLAN.md`); `labels.md`
  (перепись меток и прочих пометок в квадратных скобках); `sync.md` (README пакетов `99-raw/notes/sync/*/`); `videos.md`;
  `_inventory.md` (файлы с числом строк).
- Ограничения: разделы выбираются по заголовкам (регулярные выражения `KEEP_CONTENT`, `KEEP_REPORT`) — раздел с другим
  заголовком в извлечение не попадёт; числа и ссылки сверять по файлу базы.
