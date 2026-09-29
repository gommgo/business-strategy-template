# Утилиты text-research

Все пути — от корня `kb/text/` (от корня скилла). Скопированы и проверены архитектором 24.09.2026 на
этой машине: Debian 13, 20 потоков, 15 ГБ ОЗУ (свободно около 5 ГБ — параллельно работают сессии других баз), Intel Iris
Xe без CUDA; Python 3.13, Node 24.21 (`node` из PATH или DDD_NODE), Playwright + Chromium, yt-dlp
2026.08.18 (`~/.local/bin/yt-dlp`), ffmpeg 7.1.5, uv; модель Qwen3-ASR-1.7B Q8_0 в кэше Hugging Face и
`~/.local/bin/llama-mtmd-cli`.

## Скопировано без изменений (24.09.2026, побайтно равны источникам — сверено `md5sum`)

| Утилита | Откуда | Что делает | Пример |
|---|---|---|---|
| `fetch.py` | `../kimi-research/99-raw/tools/` (там — из ai-media) | страница → читаемый Markdown в `99-raw/cache/`, PDF — через `pdftotext`; печатает путь | `python3 99-raw/tools/fetch.py "URL"` |
| `render_fetch.py` | `../kimi-research/99-raw/tools/` | то же через headless-браузер: лендинги на JS, SPA-документация | `python3 99-raw/tools/render_fetch.py "URL" --scroll [--html]` |
| `site_probe.py` | `../kimi-research/99-raw/tools/` (исходно — агент A blender) | замер живой страницы: байты по категориям, LCP с элементом, TBT, WebGL, прокрутка, `--mobile`, `--throttle`, `--reduced-motion` | `python3 ../blender/site_probe.py https://site out/ [--mobile]` |
| `yt_dl.py` | `../kimi-research/99-raw/tools/` (исходно — V/01 ai-media) | YouTube без HTTP 429: `meta` (только метаданные), `subs` (одна дорожка на ролик), `comm` (100 верхних комментариев), `pick` (выбор дорожки без сети); файлы — `99-raw/youtube/{meta,subs,comments}/`, журнал `99-raw/youtube/yt_dl.log` | `python3 99-raw/tools/yt_dl.py meta ids.txt && python3 99-raw/tools/yt_dl.py subs ids.txt` |
| `vtt2md.py` | `../kimi-research/99-raw/tools/` (исходно — blender, пути исправлены в ai-media 23.09) | транскрипты `91-videos/transcripts/<id>.md` из скачанных `.vtt` и `info.json`: главы, описание, топ-комментарии, текст с таймкодом раз в минуту; **список — только id по строке** | `python3 99-raw/tools/vtt2md.py 99-raw/youtube/ids_catalog.txt` |
| `yt_transcript.py` | `../kimi-research/99-raw/tools/` | поиск по YouTube без API (`--search "запрос" -n 20`), метаданные; субтитры этим способом не качать — только `yt_dl.py` | `python3 99-raw/tools/yt_transcript.py --search "April Dunford positioning" -n 10` |
| `transcribe_local.py` | `../blender-research/99-raw/tools/` | локальное распознавание речи для роликов без субтитров: Qwen3-ASR-1.7B Q8_0 через `llama-mtmd-cli`, CPU, ≈ 0,43 реального времени при 16 потоках, резка по паузам, докачка после обрыва → `91-videos/transcripts/<id>.md` | `python3 99-raw/tools/transcribe_local.py <id> [--threads 12]` |

**Проверка путей (задание архитектора).** Ни одна копия не привязана к чужой базе: каталоги считаются от расположения
файла (`HERE`, `ROOT` = `../../kb/text/99-raw/..`), значит копии пишут в папки этой базы. Машинные зависимости общие для
машины и не требуют правки: `yt_dl.py` — `node:$(command -v node)` и `~/.local/bin/yt-dlp`;
`transcribe_local.py` — снимок модели `~/.cache/huggingface/hub/models--ggml-org--Qwen3-ASR-1.7B-GGUF/snapshots/36a6786…`,
`llama-mtmd-cli` и node (все есть, проверено 24.09). Упоминания других баз в комментариях (`yt_transcript.py` — «формат
как в ux и ui», `vtt2md.py` — «копия из blender», докстринг `site_probe.py` — ссылка на `web_view.py`, которого здесь нет)
на работу не влияют; `site_probe.py` работает без `web_view.py`. `transcribe_local.py` грузит CPU на 12–16 потоков:
**один процесс на машину**, запускает оркестратор, не агент волны.

## Субтитры YouTube без HTTP 429 (способ ai-media, проверен 110 загрузками подряд)

1. Метаданные отдельно (`yt_dl.py meta`) — timedtext не трогается.
2. Ровно одна дорожка на ролик по метаданным: ручные на языке оригинала → автоматические `<язык>-orig` → ручные en/ru.
3. Ссылка на дорожку — из сохранённого `info.json`; истекла — метаданные заново.
4. Пауза 6 с между роликами; при 429 — 90 и 120 с с повтором; после трёх роликов подряд с 429 — остановка (перезапуск
   идемпотентен).
5. На длинных русских запросах поиск `yt_transcript.py --search` выдаёт мусор или пустоту (разведка 24.09) — короткие
   запросы и поиск по каналу: `~/.local/bin/yt-dlp --flat-playlist --print "%(id)s\t%(title)s\t%(view_count)s\t%(duration_string)s" "<url канала>/videos"`.

## Линтер UX и другие чужие проверки текста (где лежит код)

- **Линтер `ux 07/06` — не скрипт.** Это спецификация в Markdown: `../../kb/ux/07-ux-writing/06-banned-words-and-patterns.md`
  — словари §1–§6 (регулярные выражения ECMAScript с флагами `giu`, границы слова для кириллицы
  `(?<![А-Яа-яЁё])…(?![А-Яа-яЁё])`), формат правила §7.1 (`id, level, lang, pattern, flags, appliesTo, excludes,
  message, replacement, examples, source`), закрытый список ролей узлов §7.2 (в том числе `marketing`), анализаторы без
  регулярок §7.3, порядок §7.4, действия агента §7.5, чего не ловит §8, блок запретов для промта §9. Каталог автопроверок —
  `../../kb/ux/12-evaluation-checklists/03-automated-checks.md` AC-TXT-01…23. Наш `copy_lint.py` (агент C) — первая
  исполнимая реализация этого формата плюс жанровые профили; словари ux читаются конвертером или копируются с полем
  `source`.
- Маркеры антислопа UI — JS-скрипт внутри `../../kb/ui/11-styles-trends/04-anti-slop-ui.md` §3 (маркеры 7, 30, 34 —
  выделенное слово, eyebrow, стрелка в CTA).
- humanizer-ru (`github.com/smixs/humanizer-ru`, MIT, 172 звезды, обновлён 23.09.2026): `scripts/lint.py`, `references/patterns.md`,
  `evals/evals.json` — клонирует агент C в `99-raw/cache/repos/smixs__humanizer-ru/` (глубина 1).

## Кандидаты на переиспользование (не копировались; брать по мере надобности, с указанием источника)

| Что | Где | Кому | Зачем |
|---|---|---|---|
| `before_after_build.py` | `../ux-research/99-raw/tools/` | J | сборка `before-after.tsv` (колонки `before, after, rule_ref, lang, why`); пути жёстко на `07-ux-writing/` — адаптировать, добавить `genre` |
| `k3_checks.py` (HON-NUMBERS, HON-COPY, HON-QUOTE, HON-FILLER) | `../kimi-research/99-raw/tools/` | B2, J | идеи и код извлечения чисел и цитат для `claims_check.py`; проверка текста собранной страницы против `copy.md` |
| `build_package.py check` | `../kimi-research/07-brief-handoff/templates/` | J | проверка экспорта copy deck в формат пакета kimi (без запуска Kimi) |
| `asset_inventory.py` | `../ai-media-research/99-raw/tools/` | D | идеи разбора DOM и первого экрана для `copy_extract.py` |
| `stand_run.py page` / `tally`; страница вариантов G/05 | `../ai-media-research/99-raw/tools/`; `../kimi-research/99-raw/experiments/G/05-variants-page/` | I | слепой попарный выбор текстов заказчиком в живой фазе (Брэдли — Терри, Уилсон) |
| `asset_audit.py` (`judge-jobs`, `agree`, `calibrate`) | `../ai-media-research/99-raw/tools/` | I | калибровка судьи по голосам человека |
| `check_links.py` | `../kimi-research/99-raw/tools/`, `../ai-media-research/99-raw/tools/` | X | проверка ссылок, `→ §`, `[V:<id>]` — **взят и адаптирован X2** (копия ai-media), раздел «Утилиты волны 4» ниже |
| `sources_collect.py` | `../ux-research/99-raw/tools/` | S | сводная библиография `90-sources/` — **написан S1b по образцу ux**, раздел «Утилиты волны 4» ниже |
| `checklist_export.py` | `../ux-research/99-raw/tools/` | I | экспорт чек-листа Markdown → YAML |

## Будут написаны агентами

| Утилита | Назначение | Агент · волна |
|---|---|---|
| `copy_lint.py` | линтер текстов по жанру и роли строки: жанры сайта и `interface` (реестр `texts.md`, роль — вход), правила из `../../kb/text/06-anti-slop/lexicon/` со словарём ux 07/06, профили, межстрочные проверки ux 07/06 §7.3; JSON и Markdown; `--selftest` | раздел ниже |
| `ux_dict_to_yaml.py` | ux 07/06 §1–§6 и ux 07/01 §12 → производный `../../kb/text/06-anti-slop/lexicon/ux-07-06.yaml`; `--check`, `--selftest` | раздел ниже |
| `copy_extract.py` | страница → структурированный текст по слотам: секции, hero, CTA, отзывы, FAQ, мета, OG, текст JSON-LD | раздел ниже |
| `claims_check.py` | сверка copy deck, `pages/<page-id>/copy.md` входа холста или страницы с `facts.yaml`: числа (и словами), имена, даты, цитаты, логотипы, рейтинги, цены, гарантии, `never_claim`, места `use`, демо-данные, `[PLACEHOLDER]`; правовые правила из `../../kb/text/08-russian-legal-typography/claims-rules.yaml` | раздел ниже |
| `copydeck.py` | каркас из плана страницы, `validate`, `claims`, `lint`, `check`, выбор вариантов, `approve`, выгрузка `pages/<page-id>/copy.md` и `<вход>/facts.md` во вход холста, приём правок текста с холста, `verify-page` | раздел ниже |
| `before_after_build.py` (адаптация) | `../../kb/text/10-templates-recipes/before-after.tsv` из таблиц «было / стало» базы | J · 3 |

Каждый автор добавляет в этот файл свой раздел: запуск, вход и выход, на чём проверено (опыт), ограничения.

## Правила

- Python-пакеты — только в venv внутри `99-raw/tools/` (`uv venv 99-raw/tools/venv-<буква>`); `sudo` запрещён; глобально
  ничего не ставить; npm — в папке опыта.
- Браузер — один на агента, под блокировкой: `mkdir -p 99-raw/tools/.locks && flock -w 900 99-raw/tools/.locks/browser.lock <команда>`;
  перед браузером `free -g` (меньше 2 ГБ свободно — подождать).
- Клоны репозиториев — `99-raw/cache/repos/<org>__<repo>/`, `git clone --depth 1`; клоны внешних скиллов уже есть в
  `../kimi-research/99-raw/cache/repos/` — читать оттуда.
- Платных вызовов нет: API Главреда (`glvrd.ru/api`, платный, ключ через автора), API «Тургенева» (ключ, около 0,30 ₽ за
  проверку — по стороннему описанию), Wordstat API (`api.wordstat.yandex.net`, OAuth через поддержку Яндекс Директа),
  вызовы моделей — только в живой фазе с заказчиком. Ключи не печатать и не копировать.

## `claims_check.py` — сверка текстов с `facts.yaml`

Ядро «контура честности»: любое число, имя, дата, цитата, логотип, рейтинг, цена, гарантия текста сверяется с белым
списком фактов (`../../kb/text/02-strategy-messaging/facts.schema.yaml`). Спецификация и правила — `../../kb/text/02-strategy-messaging/03-proof-and-facts.md`
§7. Зависимости: Python 3.10+ и PyYAML; сеть и модели не нужны. Полная справка — шапка файла (`python3 claims_check.py -h`).

| Команда | Что делает | Выход |
|---|---|---|
| `python3 claims_check.py [check] <вход> --facts facts.yaml [--today ГГГГ-ММ-ДД] [--json out.json] [--md out.md]` | сверка copy deck (YAML), `pages/<page-id>/copy.md` входа холста (`## <section_id>`, `[<slot_id>] <статус>: текст` — синтаксис `copydeck.py`), Markdown, текста, HTML; `--final` — ворота публикации (демо-данные `example: true` — error, без ключа — info); `--all-variants`, `--strict`, `--verbose`, `--rules <файл>`, `--no-external-rules`, `--no-default-never`, `--format` | 0 — нет error, 2 — есть, 1 — ошибка входа |
| `claims_check.py inventory <страница>` | утверждения по классам без фактов и «виден ли источник» (метрика доли утверждений с видимым источником) | 0 |
| `claims_check.py lint-facts facts.yaml [--final]` | сам инвентарь: вывод без основания (`source.quote`), истёкшие, без разрешения, места `use` не из словаря site, демо-данные | 0 / 2 |
| `claims_check.py rules-schema` | JSON Schema формата правовых правил | 0 |
| `claims_check.py --selftest` | офлайн-тесты: извлечение, сопоставление, «Кварц», отзывы, сроки, правовые правила, нейтральные фразы, калибровки К17–К27 (разделитель тысяч по языку, числительные словами, «рядом» у выбранного варианта, `requires_nearby` демо-фактов, подпись отзыва против разрешения, прогнозы, вопросы FAQ, имена в падежах, переводы фактов и запретов, места `use` на 8 примерах copy deck, демо-данные) | 0 / 1 |

**Правила находок** — префикс `COPY-F-`: `NUM`, `NUM-MISMATCH`, `NUM-WORDS`, `DATE`, `RATING`, `QUOTE`, `QUOTE-EDIT`,
`QUOTE-RECUT`, `CLASS`, `EXTENDS`, `PROPERTY`, `NEVER`, `TYPICALITY`, `PERMISSION`, `INFERRED`, `EXPIRED`, `STALE`,
`LEGAL`, `UNVERIFIED`, `REF`, `USE`, `NEARBY`, `NAME`, `EXAMPLE`, `PLACEHOLDER`, `PLACEHOLDER-UNLISTED`, `FLAGS`,
`UNSUPPORTED` (`--strict`), `VOCAB` (`lint-facts`). Уровни и условия — `03-proof-and-facts.md` §7.2. Места `use` факта —
ориентир: вне их — `COPY-F-USE` warning, запрет `use.not_in` — error; места `x-use-always` схемы фактов (мета, FAQ,
статья, подвал, форма) законны всегда. Число словами в утверждении («пять лет») сверяется как цифрами и получает
`COPY-F-NUM-WORDS` (пишите цифрами); счёт без утверждения («два шага») — без находок. Вопрос (FAQ, предложение с «?»)
утверждением не считается.

**Правовые правила.** Файл `../../kb/text/08-russian-legal-typography/claims-rules.yaml` подхватывается сам, если есть;
дополнительные — `--rules`. Формат (`rules-schema`): `version: 1`, `date`, `rules[]` с полями `id` (рекомендуется
`COPY-L-…`), `level`, `claim_class[]` и/или `patterns[]` (Python re, регистр не важен), `genres`, `slot_types`,
`jurisdiction`, `forbid` (любое срабатывание — находка), `requires` (`fact`, `fact_fields` вроде `basis.criterion`,
`nearby` — регулярки оговорки или источника в той же единице или секции, `legal_review: approved`), `message`, `fix`,
`source`. Классы маркеров берутся из `x-claim-classes` схемы фактов; набор запретов по умолчанию — `x-never-claim-defaults`.

**Ограничения:** свойства без словарных слов и утверждения без чисел и маркеров ловит только `--strict` (с шумом);
смысл между фразами не сравнивается; эвристика имён по заглавным буквам шумит на служебных файлах (сверять copy deck, а
не служебные заметки); `inventory` на Markdown переоценивает число утверждений (цены опций, нумерация) и плохо видит
источники в картинках и сносках — для корпуса нужен разбор DOM (`copy_extract.py`).

## `copy_lint.py` и `ux_dict_to_yaml.py` — линтер текстов по жанру и роли строки

Исполнимая реализация формата ux 07/06 §7 с жанровыми профилями. Спецификация —
`../../kb/text/06-anti-slop/02-linter-spec-and-profiles.md`, каталог маркеров —
`../../kb/text/06-anti-slop/01-text-slop-markers-by-genre.md`, правила — `../../kb/text/06-anti-slop/lexicon/*.yaml` (свои
словари и производный словарь ux `ux-07-06.yaml`), профили жанров — `../../kb/text/06-anti-slop/profiles.yaml`, пороги жанров
сайта по замеру корпуса — `../../kb/text/03-corpus-measured/thresholds.yaml` (подхватываются сами), внешние правила мета,
GEO, права и набора — `profiles.yaml → external_rules`. Id типов слотов и страниц — словарь site
`../../kb/site/02-site-types/vocabulary.yaml`; роль ux, жанры и `lint_as` типа слота —
`../../kb/text/04-copy-by-block/copy-slots.yaml` (слот без своих правил проверяется правилами типа `lint_as`).

**Жанры.** Шесть жанров сайта — `landing`, `site-page`, `article`, `meta`, `geo`, `email-form`; жанр copy deck — `genre`
типа страницы в словаре site. `interface` — тексты продукта за входом: кабинет, приложение, бот, транзакционные письма,
СМС, push. В нём правила ux 07/06 действуют с уровнями канона: поправки сайта — `overrides` с полем `genres` в
`../../kb/text/06-anti-slop/lexicon/marketing-role.yaml` (без поля — жанры сайта); из словарей text — артефакты, данные и
набор (пробелы у знаков препинания — error), право рекламы выключено; проза — роли `body`, `help`, `email`.

**Роль строки — вход.** Ключ `--role`, поле `role` строки реестра и короткой формы copy deck, роль части компонента
(`--component`, поле `component`; `../../kb/common/components.yaml#text_roles`: «Field.Error» → `error`). Закрытый список —
ux 07/06 §7.2 и `body` (раздел `roles` производного словаря) и внутренняя `meta` мета-полей. Неизвестная роль, тип слота или
часть компонента, роль не из ролей части — ошибка вызова (код 1); в жанре `interface` строка без роли — `body`.

**Реестр текстов интерфейса** `docs/projects/<slug>/screens/<surface>/texts.md` (форма —
`../../../../../docs/projects/_template/screens/_template/texts.md`) — вход целиком, жанр `interface`, место находки — строка
файла. Межстрочные проверки ux 07/06 §7.3:

| Проверка | Что сверяет | Уровень |
|---|---|---|
| имя действия по потоку (`an-ui-action-name`, `an-ui-action-synonym`) | строка с `action` называет действие корнем `verb` или `past` словаря `action.md`; синоним из `banned` — в строке действия и в строке объекта действия | warning; синоним — error |
| синонимы объекта (`an-ui-object-alias`) | слова из `aliases` глоссария `object.md` с падежными окончаниями, во всех строках | error |
| формы группы (`an-ui-group-form`) | строки одного `group` (меню, статусы объекта) закрывают один вопрос: «что?», «какая?» или действие; нужна морфология | warning |
| дубли на экране (`an-ui-duplicate`) | одинаковый текст двух строк с содержанием на одном экране (ключ `раздел.экран`) | warning |
| `maxlen` (`an-ui-maxlen`) | знаков без подстановок ICU больше предела строки | error |
| длина по роли (`an-ui-role-length`) | слова, предложения и знаки по роли — `ux-07-06.yaml#role_lengths` (ux 07/01 §12); предложение ≤ 15 слов, в пояснениях ≤ 20 | warning |
| форматы (`an-ui-formats`) | число литералом вместо подстановки; диапазон — тире без пробелов, один знак на продукт; пробел разрядов — неразрывный, один на продукт | warning |
| ICU (`an-ui-icu`) | скобки, ветка `other`; `=1` вместо `one`, у русского plural — `one`, `few`, `many` | error; ветки — warning |
| «ё» и «е» (`an-ui-yo-mix`), US и UK (`an-ui-us-uk`) | одно слово в двух написаниях | warning |
| уровень чтения (`an-reading-level`) | роли `body`, `help`, `email` от 30 слов: слогов в слове больше 2,5; индекс Оборневой (206,835) — в метриках | info |

`object.md` и `action.md` ищутся в папке проекта реестра (`--objects`, `--actions` — другие пути); нет файла — проверка
пропускается с заметкой. Заголовок против содержимого и стили пары «согласие / отказ» — судья и проверка макета.

| Команда | Что делает |
|---|---|
| `copy_lint.py page.md --genre landing` | отчёт для терминала. Текст целой страницы без copy deck — аудит страницы: пороги замера сняты по слотам, поэтому находки анализаторов не выше warning и вердикт «переписать» — сигнал «проверить»; ворота — copy deck (`summary.mode: page-audit`) |
| `… deck.yaml --json` | copy deck (`copy_deck.pages[].sections[].slots[]`: `slot_type`, `variants[].text`, `fact_ids`, `lint_allow`) или короткая форма `slots: [{slot_type \| role \| component, text}]`; проверяется выбранный вариант (без выбора — все живые), `--all-variants` — все живые, `status: rejected` — никогда; мета — с `meta.fact_ids` и `lint_allow` страницы |
| `… docs/projects/<slug>/screens/<surface>/texts.md` | реестр текстов интерфейса: жанр `interface`, межстрочные проверки |
| `echo "Сохранить" \| … - --genre interface --role action` | одна строка интерфейса; `--component Field.Error` — роль части компонента |
| `… page.html --genre site-page --md` | HTML: title, мета, OG, заголовки, абзацы, кнопки, отзывы, alt; отчёт Markdown-таблицей |
| `cat t.txt \| … - --genre article --metrics-only --json` | только метрики |
| `… deck.yaml --final` | перед публикацией: `[PLACEHOLDER]` — error |
| `… deck.yaml --voice voice.yaml --customer-words voc.yaml` | профиль голоса: словарь «не говорим» (`voice-avoid-NN`, входит в плотность маркеров), единые написания (`voice-spelling-NN`), обращение для проверки «ты» и «вы»; слова клиента (`customer_words` голоса клиента проекта `docs/projects/<slug>/voc.yaml` или смысла страницы) — их повтор не находка |
| `… page.md --rules extra.yaml --profiles my.yaml --profile landing-brand --thresholds th.yaml` | внешние правила, свой профиль, свои пороги |
| `… --morph on\|off` | морфология pymorphy3 (по умолчанию — если установлена): деепричастные хвосты, родительные, пассив, повтор глагола, деление тире, формы групп строк |
| `copy_lint.py --selftest` | словари и пары «плохо / хорошо», сводка правил по уровням для каждого жанра, жанр `interface` и роли, реестр на фикстурах `cabinet-texts` (0 находок) и `cabinet-texts-defects` (четыре посеянных дефекта), межстрочные анализаторы, калибровки К1–К16 и К28 базы |
| `ux_dict_to_yaml.py [--check \| --selftest]` | собрать производный словарь; `--check` — сверка байт в байт без записи (код 3 — устарел); `--selftest` — разбор, роли, длины, переносимость шаблонов на кириллице в Python и Node |

**Производный словарь ux** `../../kb/text/06-anti-slop/lexicon/ux-07-06.yaml` собирает `ux_dict_to_yaml.py` из ux 07/06 и
ux 07/01 §12 — руками не правится. В нём: закрытый список ролей (`roles`), правила таблиц §1–§6 (`rules`: уровень, роли,
исключения; шаблоны переносимы между Python и ECMAScript с флагом `u` — `\w`, `\b`, `\d` раскрыты в классы с кириллицей,
«Ё» в классах, флаг `i` снят у классов из заглавных; ячейка с оговоркой, которую шаблон канона не выражает, — шаблон или
роли с оговоркой и `note`), строки §6.5 о пробелах — ссылкой на правила набора H (`delegated`), длины по ролям
(`role_lengths`). После правки канона: `ux_dict_to_yaml.py` → `--check` → `copy_lint.py --selftest`.

**Выход.** JSON `{"tool", "version", "date", "results": [{input, thresholds, summary, metrics, findings, notes?}]}`:
находка — `id`, `marker_id`, `level`, `group`, `message`, `fragment`, `context`, `position` (`line`, `col` — у Markdown,
текста и реестра), `replacement`, `example`, `source`, `evidence`, `slot` (`slot_type`, `role`, `lint_as`, `key`, место в copy
deck); `summary.verdict` — `clean`, `review`, `rewrite`, `fail`, `overcorrected`; `summary.mode` — `slots`, `registry`,
`page-audit`. Коды выхода: 0 — нет error, 2 — есть error, 1 — ошибка вызова, входа или словаря. API:
`kbpaths.use("text"); from copy_lint import lint_text, text_metrics, dash_classes` — `lint_text(text, genre, lang,
slot_type, profile, fmt, metrics_only, role, component)`. Интерфейс меняется только добавлением ключей.

**Интерпретатор** — `$DDD_HOME/venv/bin/python` (PyYAML, pymorphy3; лицензии: pymorphy3 — MIT, словари pymorphy3-dicts-ru
— код MIT, данные OpenCorpora). Без pymorphy3 работают регулярные приближения не выше warning, проверка форм групп строк
пропускается с заметкой.

**Ограничения.** Нет синтаксического разбора: висячие деепричастия, длинное подлежащее и прилагательное-сказуемое в
делении тире; имена собственные — по заглавной букве; разбор HTML упрощён (страница по слотам — `copy_extract.py`); корень
действия — по началу слова, чередования основы («отметить» — «отмечен») ловятся общим началом `verb` и `past`; уровни
«Подробнее» и ярлыков на сайте, длины слотов `lint_as` — до калибровки на пилотах. Смысл, правдивость, тон и структуру
страницы линтер не проверяет (спецификация §12).

## `claims_check.py` — правовой модуль

Право формулировок — в той же утилите и том же отчёте, что сверка с фактами. Правила —
`../../kb/text/08-russian-legal-typography/claims-rules.yaml` (68 правил `COPY-L-…`, подхватываются сами), нормы и практика —
`../../kb/text/08-russian-legal-typography/01-advertising-law-claims.md`. Не юридическое заключение: находка показывает, где нужна
оговорка, факт или юрист.

| Команда | Что делает |
|---|---|
| `python3 claims_check.py page.md --facts facts.yaml` | сверка с фактами + право РФ (по умолчанию `ru`, отрасль `general`) |
| `… --legal-category medical` (`finance`, `dietary-supplements`, `alcohol`, `education`, `real-estate`, `other`, `general`; через запятую) | отраслевые правила: противопоказания, БАД, ПСК, ДДУ, алкоголь; по умолчанию — `legal_category` из шапки copy deck или `general` |
| `… --jurisdiction eu` (`us`) | профиль ЕС (цена до скидки — наименьшая за 30 дней, экологические заявления, «проверенные отзывы») или США (FTC); по умолчанию — `jurisdiction` из facts.yaml или `ru` |
| `… --legal-only --json out.json` | в отчёте только находки права; в JSON блок `legal` (модуль, юрисдикция, отрасль, число правил и находок); у находки — `law` (норма и редакция) |
| `python3 claims_check.py rules-schema` | JSON Schema правил (поля права и поля формата линтера) |

**Как работает правило.** Срабатывание — `pattern` (синтаксис copy_lint: макросы `%B%` `%E%` `%W%`) по «мягкому» тексту
(нижний регистр, ё→е, тире→«-», NBSP→пробел); `unless` в том же предложении снимает срабатывание. Фильтры: `genres`,
`slot_types`/`exclude_slot_types` (шаблоны fnmatch), `lang` (ru/en по буквам единицы), `jurisdiction`, `legal_category` /
`legal_category_except`, `page_types` / `page_types_except` (тип страницы copy deck: правило вакансий — только на
`careers-page`, правило оферты — не на страницах услуг). Условия снятия (`requires`): `nearby` (хотя бы одна регулярка) и `nearby_all`
(все) в единице, секции или на странице (`nearby_scope`); `fact_fields` — поля найденного факта (`basis.criterion`,
`valid.from`…); `fact_conditions` — условия факта (`values[].qualifier`, `legal.disclaimer`) должны стоять рядом; `fact`,
`legal_review` — как у сверки фактов. `forbid: true` — запрет; правило без `requires` и `forbid` — сигнал. `once: page` —
одна находка на страницу (обязательные оговорки). `defaults` файла сливаются в правила. Факты для `requires` — найденные
числом, датой, цитатой, именем, `fact_ids` и маркером класса.

**Файл правил общий с copy_lint.py.** Линтер подключает `claims-rules.yaml` через `profiles.yaml → external_rules`:
у каждого правила `pattern`, пара `examples` строками, `group: EXT`, `count_as_marker: false`, `priority: 60`; блок
`overrides` в конце файла делает право в линтере сигналом (info; 6 правил — warning: превосходная степень, лечебные
свойства, гарантия результата, согласие ПДн с рекламой, цена только в валюте), отраслевые и ЕС/США — `off` (отрасль и
юрисдикцию знает только claims_check). Порядок в конвейере: `claims_check.py` → `copy_lint.py`.

**Набор (типографика) — в `copy_lint.py`, не здесь.** `../../kb/text/08-russian-legal-typography/typography-rules.yaml` — 27 правил
`typo-…` (маркеры `COPY-T-01…27`: тире и диапазоны, минус, проценты, валюта, разряды, неразрывные пробелы, кавычки,
знаки, двойные пробелы, английский набор); линтер подключает файл через `profiles.yaml → external_rules`, разово —
`python3 copy_lint.py page.md --rules ../../kb/text/08-russian-legal-typography/typography-rules.yaml`. Автотипограф
typograf 7.8.0 (MIT) и его настройка — `02-typography-for-marketing.md` §8.

**Самопроверка** (`--selftest`, общая с ядром): механика требований на встроенных правилах, все пары «плохо / хорошо» из
claims-rules.yaml, нейтральные фразы без error и warning права, CLI `--legal-only`, калибровки права К26 и К27
(«бесплатно в черте города», возврат, оферта, вакансии).

**Ограничения.** Регулярки не видят смысла: «лучший способ проверить» и похожие исключения перечислены вручную; отрицание
учтено только там, где оно вписано в регулярку; размер оговорки (5–10 % площади) и шрифт не проверяются — это вёрстка
(site, creative); судебная и ФАС-практика меняется — у каждого правила `law[].checked`.

## `copy_extract.py` — текст страницы по слотам

Метод — `../../kb/text/03-corpus-measured/01-corpus-method.md` §4, числа корпуса — `../../kb/text/03-corpus-measured/02-measurements.md`.
Зависимости: Playwright и Chromium (только для снятия страниц), PyYAML; метрики одного текста — `copy_lint.py
--metrics-only` (API `text_metrics`).

| Команда | Что делает |
|---|---|
| `copy_extract.py URL -o out.json --md out.md --txt out.txt --shot s.jpg --save-blocks --lock [--genre landing\|site-page\|article] [--lang ru\|en]` | страница → JSON: `page` (URL, итоговый URL, HTTP, дата, хэш текста, отсев), `meta` (title, description, og:*, twitter:*, canonical), `hero` (надзаголовок, заголовок, H1-тег, подзаголовок, кнопки, микродоказательство), `sections[]` (заголовок, уровень, роль секции), `units[]` (`slot_type`, текст, секция, в первом экране ли), `testimonials`, `faq` (и из JSON-LD), `jsonld`, `stats` (`vocab_unknown` — id вне словаря site); `--lock` — две блокировки браузера (общая и своя) и ожидание `MemAvailable` ≥ 2 ГБ |
| `… --batch targets.tsv --outdir DIR --lock --shots [--skip-existing]` | партия (`id, url, genre, lang, page_type`), браузер открывается и закрывается на каждую страницу |
| `… --html saved.html` / `file://` URL | сохранённая страница через тот же браузер |
| `… --reclassify out.blocks.json -o out.json` | перерасчёт классификации без браузера по сохранённым блокам |
| `copy_extract.py --selftest` | классификация лендинга, статьи и первого экрана с меню и плитками; id слотов и ролей в коде и в выходе — из словаря site |

**Чужие сайты.** Автоматизация не маскируется: окно 1440×900, user agent браузера как есть (`HeadlessChrome`), без
`--disable-blink-features=AutomationControlled`; вход, капча и антибот — отсев (`page.blocked`), а не обход
(`../../kb/creative/02-references-moodboards/02-refs-client-and-library.md` §8). Cookie-баннеры не нажимаются.

**Первый экран.** Меню и ряды ссылок — навигация (`nav-label`), а не кнопки: ряд из трёх и больше коротких ссылок на одной
высоте, повтор одной подписи ссылки у плиток («Подробнее»), плитки-ссылки, когда простых коротких ссылок шесть и больше.
Кнопка с фоном остаётся кнопкой, если её подпись не повторяется.

**Id.** Слоты и роли секций — словаря site; внутренние метки разбора — `form-field` (подписи полей формы, микрокопи ux
07/02), `number-label` (номера шагов, звёзды), роли `nav`, `menu`, `decor`, `quote`.

**Ограничения.** Классификация — эвристики по кеглю, тегам и ориентирам; хуже всего на конструкторах со «всё в
div» (Тильда-подобные шаблоны), боковых меню в первом экране, калькуляторах и слайдерах во весь экран; статья без тега H1
теряет заголовок. Точность извлечения по ручной проверке 25 страниц (`01-corpus-method.md` §4.4): заголовок первого
экрана 80 %, подзаголовок 84 %, главная кнопка 82 %, тип слота случайной единицы 75 %.

## `copydeck.py` — copy deck: каркас, проверки, статусы, выгрузка во вход холста

Единственный путь текста страницы во вход холста: copy deck строится каркасом из плана страницы, проверяется, получает
статусы и выгружается во вход холста (`design/<surface>/input/pages/<page-id>/copy.md` и
`design/<surface>/input/facts.md`, протокол — `references/claude-design.md § 6`); руками эти файлы не пишутся. Правки текста с холста
возвращаются в copy deck вариантами `source: customer`. Формат — `../../kb/text/10-templates-recipes/copy-deck.schema.json`
(JSON Schema 2020-12; поля и статусы v0 на месте, статус `assumed`, стык с планом — `x-site-map`, выгрузка — `x-canvas-map`),
процесс — `../../kb/text/10-templates-recipes/01-copy-deck-workflow.md`, поля и потоки — `../../kb/text/10-templates-recipes/README.md`.
Зависимости: Python 3.10+ и PyYAML; `jsonschema` — по желанию (Python окружения скилла). Сеть и модели не нужны; браузер —
только у `verify-page --browser` и `--url`. `claims_check.py` вызывается процессом, `copy_lint.py` — через API `lint_text`.
Полная справка — шапка файла (`python3 copydeck.py -h`).

**Статусы текста.** `draft` — каркас или текст в работе, владельцу не предложен; `assumed` — черновик агента
«допущением» из утверждённых смысла, фактов и голоса: предложен владельцу и идёт на вайрфрейм; `checked` — 0 error у
`claims_check.py` и `copy_lint.py` (записи `lint` и `claims` с `text_hash`); `approved` — утверждён человеком;
`rejected` — отклонён с причиной. Этап холста берёт тексты по `x-canvas-map` (`copy_md.stage_statuses`): направления —
заголовок и кнопку первого экрана, вайрфрейм — `assumed` · `checked` · `approved`, макет — только `approved`.
Юридические тексты (согласие формы, реквизиты в подвале) и подпись автора статьи агент «допущением» не пишет: до юриста
заказчика или человека они остаются `draft`, а в выгрузке становятся пробелом этапа.

| Команда | Что делает |
|---|---|
| `python3 copydeck.py skeleton PLAN -o DECK [--facts-ref F] [--voice-ref V]` | каркас из плана страницы: секции (`section_id` = `site_section_id` плана, роль, блок), текстовые слоты (id, тип, анатомия, группа), `fact_ids` и `missing_ids` из `binds` слотов данных, мета из `page_slots`, `page_plan_ref`; тексты пусты, статус `draft`. Страница без плана — `make_skeleton.py` |
| `… validate DECK [--facts F] [--plan PLAN] [--final] [--no-jsonschema]` | схема; id и ссылки; статусы (`x-status-rules`); словарь site v1 (типы страниц, роли секций, слоты); `block` против `blocks.yaml`; стык с планом (`page_plan_ref` или `--plan`); факты (есть, не пробел, не истёк, публикуем, демо-данные); пробелы (`missing_ids`, `fallback` → `COPY-D-FALLBACK`); обещание и ядро первого экрана (секция `hero`, без неё — первая после шапки); строки в картинках; второй язык; файлы правил текста (ниже). `--final` — ворота публикации: страница `approved`, 0 `[PLACEHOLDER]`, 0 демо-фактов |
| `… check DECK [--facts F] [--today ГГГГ-ММ-ДД] [--final] [--strict] [--all-variants] [--update OUT --promote]` | `claims` → `lint` → `validate`; `--update OUT --promote` пишет копию deck с записями `lint` и `claims` (`text_hash`, дата, версии утилит) и переводит `draft` и `assumed` → `checked` у текстов с 0 error; `--all-variants` — живые альтернативы «как выбранные» (`variant.checks`) |
| `… claims DECK [--facts F] [--strict] [--all-variants] [--final]` | `claims_check.py check` на плоской копии: обещание — `__promise`, мета и OG — `__head`; `--all-variants` — каждая живая альтернатива копией страницы с одной заменой: отклонённые не сверяются, соседний вариант не закрывает `requires_nearby` |
| `… lint DECK [--final] [--all-variants] [--no-page-pass]` | `lint_text` на каждый текст со своим `slot_type` и жанром + проход страницы по Markdown-проекции; `lint_allow` и `--final` — по семантике линтера; `meta.fact_ids` учитываются |
| `… export DECK --page ID --stage directions\|wireframe\|mockup [--out DIR] [--facts-scope all\|used]` | выгрузка во вход холста: `DIR/pages/<page-id>/copy.md` (тексты статуса этапа) и `<DIR>/facts.md` («Факты» — публикуемые дословно, с источником и местами, демо-данные помечены; «Нет» — пробелы `[PLACEHOLDER: что]`; «Нельзя утверждать» — запреты без снимающего факта); слот без текста статуса этапа — `COPY-D-STAGE`, факты не `confirmed` — `COPY-D-FACTS-STATUS` (на макете — error, раньше — warning) |
| `… import-copy COPY.md --deck DECK --page ID -o OUT [--choose]` | правки текста с холста (`pages/<page-id>/copy.md` из разбора исходников холста или правленая выгрузка): изменённый текст слота — новый вариант `source: customer` в статусе `draft` (дальше — `check` и утверждение); `--choose` — сразу выбран, утверждённая страница возвращается в `draft`; текст без секции или слота плана — находка «перенести в план?» |
| `… export-variants DECK -o SHEET.md --key KEY.yaml [--seed N] [--include-failed]` | лист слепого выбора: слоты, обещание и мета, метки A, B, C; модели и авторы скрыты; варианты с error в `variant.checks` сняты |
| `… apply-selection DECK --key KEY.yaml (--votes VOTES.yaml \| --sheet SHEET.md) --by КТО -o OUT` | голоса слепого выбора → `chosen` и `selection {method, by, at, compared, tally, ref}`; у мета — выбранный текст в `meta.<поле>` |
| `… approve DECK --page ID --by КТО -o OUT` | утверждение человеком: тексты `checked` (0 error, актуальный `text_hash`, без `[PLACEHOLDER]`) → `approved`, `review {by, at}` и `approval` страницы; журнал процесса (`edit_log`, отклонённые варианты) уходит, `selection.compared` остаётся |
| `… verify-page DECK --page ID (--extract PAGE.json \| --html PAGE.html [--browser] \| --url URL)` | собранная страница против copy deck: блоки не из copy deck > 10 % — error, число вне фактов и текстов — error, потерянные слоты, мета, обещание |
| `… export-assets DECK [--page ID] [-o OUT]` | alt, подписи, строки в картинках (`text.mode: in_image`, ≤ 3 строк по ≤ 40 знаков), OG → фрагмент плана ассетов |
| `… upgrade DECK -o OUT` | copy deck v0 → v1 |
| `… before-after [--write \| --check]` | пустой `why` в `../../kb/text/10-templates-recipes/before-after.tsv` — из `rule_ref` (заголовок раздела нормы) |
| `python3 copydeck.py --selftest` | 146 проверок: схема и статусы (`assumed`), факты и пробелы, словарь site и блоки, каркас из плана и стык, ядро первого экрана, файлы правил текста, мета, альтернативы, выгрузка и приём copy.md, facts.md, слепой выбор и `apply-selection`, `approve` без журнала процесса, `verify-page`, `before-after` |

**Синтаксис copy.md** (владелец формата — эта утилита, `parse_copy_md` и `render_copy_md`; тот же формат пишет разбор
исходников холста, читают `claims_check.py --format copy-md` и сборщик входа; правило — `x-canvas-map` ключ `copy_md`):
строка `# …` — заголовок или комментарий; `## <section_id>` — секция плана, `## ?` или `## ? <подпись>` — тексты холста
без секции плана; `[<slot_id>] <статус>: <текст>` — слот (статус пишет выгрузка; у текстов из исходников холста его нет:
`[<slot_id>]: <текст>`); `[?]: <текст>` или `[? <подпись>]: <текст>` — текст холста без слота плана; текст — всё после
первого «: » до конца строки, дословно; абзацы — строками продолжения, начатыми двумя пробелами; пустые строки и
`<!-- … -->` пропускаются.

```
# Тексты страницы home — Отвес (ru), этап wireframe
# Тексты — дословно: не переводить, не сокращать, не дописывать. Строка слота: [<slot_id>] <статус>: текст.

## hero
[h1] assumed: Ремонт квартир под ключ в Нижнем Новгороде с 2014 года
[cta] checked: Позвать замерщика

## guarantee
[text] approved: Гарантия 3 года на работы — пункт 7.2 договора.
  Отошла плитка — звоните: гарантия действует с даты акта.
```

**Выход.** Терминал (`--verbose` — с info, `--quiet` — без вывода); `--json OUT` — `{tool, version, date, command, input,
today, summary{error, warning, info}, tools{claims, lint, validate}, findings[{tool, level, rule, where, message, fix,
fragment, fact_ids, variant}], notes, slots{<путь>: {claims, lint[, variants]}}}`, у `export` ещё `export{…}`; `--md OUT` —
таблица находок. Коды выхода: 0 — нет error, 2 — есть error, 1 — ошибка входа. Правила: свои `COPY-D-…`; `COPY-F-…` и
`COPY-L-…` — из `claims_check.py`, id линтера — из `copy_lint.py`, `meta-x-…` — проверки мета вне линтера. Копия deck,
записанная в другую папку (`check --update`, `approve -o`, `upgrade -o`, `import-copy -o`, `apply-selection -o`), получает
относительные пути (`facts_ref`, `voice_ref`, `copy_slots_ref`, `meaning_ref`, `source_ref`, `page_plan_ref`,
`hierarchy_ref`) от своей папки.

**Файлы правил текста**: есть — проверка работает; нет — warning `COPY-D-RULES-MISSING`; формат не распознан —
`COPY-D-RULES-FORMAT`; ничего не падает. `copy-slots.yaml` — длины (`COPY-D-LEN`), `fact_required` (`COPY-D-FACT-REQUIRED`),
ядро первого экрана > 40 слов (`COPY-D-HERO-CORE`), роль секции (`COPY-D-SLOT-ROLE`); голос проекта (`docs/projects/<slug>/voice.yaml`) — обращение и
`vocabulary.avoid` (`COPY-D-VOICE`); `meta-rules.yaml` — длины мета и `meta-x-…`; `claims-rules.yaml` — `claim_flags`
сверяются с id правил (`COPY-D-FLAGS`).

**Ограничения.**
- `lint_text` не принимает `fact_ids` слота и `lint_allow`: `copydeck.py lint` повторяет режим copy deck линтера поверх API
  (правила `requires_no_fact`, `an-number-without-fact`, `lint_allow` — fnmatch по id, ART и CNT не снимаются, `--final`).
- `lint_allow` не снимает находки сверки (`COPY-F-…`, `COPY-L-…`) и формата (`COPY-D-…`): ложное срабатывание сверки
  лечится правкой текста или `facts.yaml`.
- Два пути линтера: прямой `copy_lint.py` на copy deck не читает `meta.fact_ids` (число в title — ложный
  `an-number-without-fact`), не видит обещание и OG-шаблон и линтует отклонённые варианты; `copydeck.py lint` —
  наоборот. Ворота — `copydeck.py check`; расхождение по мете — в `parity_copy_lint`.
- Загрузка правил линтера запоминается внутри процесса copydeck: правили словари линтера — перезапустите.
- `claims` — процессом на плоской копии; `meta.fact_ids` в сверку не передаются (один список на все поля давал ложные
  `COPY-F-USE`); свои `fact_ids` варианта мета — передаются.

## Цепочка смысла, голоса и каркаса: проверки и входы промтов

Утилиты шагов цепочки текста (`../../kb/text/09-ai-generation-evaluation/02-generation-pipeline.md`): смысл и иерархия,
факты, голос бренда и продукта, каркас copy deck без плана, входы промтов P1–P7 и прогон примеров. Сеть и модели не
нужны: входы собирает код, тексты пишет агент сессии.

| Команда | Что делает | Выход |
|---|---|---|
| `python3 validate_meaning.py [--quiet] [--no-negative]` | схемы смысла и иерархии сообщений (метасхема), примеры базы, смысловые проверки (допущение без вопроса, ссылки на альтернативы и доказательства, `never_claim` с `lift: never` в обещаниях, блокеры до `final-cta`), отрицательные случаи; обещание из допущения — предупреждения: свойство или опора `has-proof` с `missing:` в `proof_ids`, `never_claim` с `lift: with-fact` без снимающего проверенного факта того же класса, главное сообщение или ядро ценностного предложения на свойстве без доказательства (К30) | 0 / 1 |
| `python3 validate_any.py FILE.yaml […]` | те же проверки на meaning или иерархии проекта (выход промтов P2, P3) | 0 / 1 |
| `python3 validate_voice.py [voice.yaml …]` | схема голоса, перечень `slot-type` — слоты вида text словаря site; профили бренда и голоса продукта (`docs/projects/<slug>/voice.product.yaml`: все поверхности `voice: product`, жанр `interface`, юмора нет в `service-error`, `destructive-action`, `money`, `security`, образцы по роли строки); отрицательные мутации бренда и голоса продукта; итог — `$DDD_HOME/out/text/validate_voice.last-run.txt` | 0 / 1 |
| `python3 validate_facts.py` | схемы фактов и голоса клиента, примеры text и site (`example: true` у демо-наборов), ссылки `entities` и `related`, отрицательные случаи (`example`, переводы, язык запретов) | 0 / 1 |
| `python3 check_intake.py INTAKE.yaml --brief BRIEF.txt` · `--selftest` | выход промта P1 (разбор брифа): цитаты — подстроки брифа, числа только из цитат, вопросов ≤ 7, допущения с вопросами | 0 / 2 / 1 |
| `python3 make_skeleton.py HIERARCHY.yaml --facts F --voice V --meaning M --page-id ID -o DECK [--force]` · `--selftest` | каркас copy deck из иерархии, когда плана страницы нет; есть план (`../plans/<page-id>.yaml` рядом с папкой иерархии) — отказ с кодом 2 и подсказкой `copydeck.py skeleton`, `--force` — всё равно | 0 / 2 |
| `python3 chain_inputs.py <команда>` · `--selftest` | входы промтов P2–P7 и код между шагами: `digest-meaning`, `meaning-claims`, `hierarchy-input`, `section-input`, `edit-input`, `judge-input`, `judge-score`, `assemble` и `apply-edits` (тексты агента — `assumed`), `canvas-texts` (выгрузка во вход холста — `copydeck.py export`) | 0 / 1 / 2 |
| `python3 run_checks.py [пример.yaml …] [--md table.md]` | все проверки примеров copy deck базы: `claims_check.py` → `copy_lint.py` → `copydeck.py check` → `validate` (+ jsonschema) → `export` этапа wireframe; JSON и выгрузки — `$DDD_HOME/out/text/run_checks/` | 0 / 2 |

## `before_after_build.py` — пары «до / после» по маркетинговым жанрам (J, волна 3, 2026-09-24)

Адаптация `../ux-research/99-raw/tools/before_after_build.py` (колонки ux `before, after, rule_ref, lang, why`) под эту
базу: пути папок 01–10, колонки `genre`, `marker_id` и (1.1, J3) `evidence` — доказательность пары. Версия 1.1; Python 3.10+,
PyYAML.

| Команда | Что делает |
|---|---|
| `python3 99-raw/tools/before_after_build.py [--out PATH] [--sources e3,f05,decks,md,rules,pairs,digests]` | собирает TSV (по умолчанию `../../kb/text/10-templates-recipes/before-after.tsv`) и печатает сводку по источникам, жанрам, языкам, маркерам, доказательности |
| `… --stats` | только сводка |
| `… --min-sim 0.35` | строгий режим для примеров правил (похожие строки или ≥ 2 общих значимых слова) |
| `… --exclude FILE.tsv` | своя курация: «файл-источник<TAB>начало before» |
| `python3 99-raw/tools/before_after_build.py --selftest` | 18 проверок: Markdown-таблицы (заголовки в любом порядке, «Пример «наивно»»), примеры правил, пары A/02, дайджесты, доказательность (метка, `[кейс]` с числом, «антипример», метка файла), источники `e3`, `f05`, `decks`, колонки TSV |

**Источники.** `e3` — правка страниц E/04 (`draft1-deck-*` → `deck-*-v0`: изменённые тексты с причиной из `notes`, снятые
слоты с причиной протокола README E/04); `f05` — пары F/05 (`pairs.yaml`) с итогами проверок до и после из `results.md` §3;
`decks` — отклонённые варианты copy deck (`status: rejected` + `reason`) → выбранный текст (`../../kb/text/10-templates-recipes/examples/`,
I/04 deck-v4); `md` — Markdown-таблицы «было / стало» в папках 01–10; `rules` — `examples {bad, good}` правил C, G, H;
`pairs` — контрольные пары A/02; `digests` — дайджесты `91-videos/digests/`. `e3`, `f05`, `decks` идут первыми: при дубле
остаётся строка с итогом проверок. Доказательность: метка в строке (`[кейс]` — с числом эффекта, `[проверено: …]`,
`[исследование]` …) → «антипример» (колонка «антипример») → итог проверок источника → метка файла (`FILE_EVIDENCE`: тексты
прошли сверку и линтер автора) → «эффект не доказан».

**Проверено** (J/06, J/08): 540 пар на базе 24.09 (RU 412, EN 128; `marker_id` — 281; доказательность: пример правила 272,
`[проверено …]` 177, «эффект не доказан» 89, `[кейс]` с числом 2). Выборка 40 до курации — 34 пары; сняты 6 строк
(`EXCLUDE`) и правило «после: то же…» — не пара; выборка 40 после — 39 пар и 1 частичная (`99-raw/experiments/J/08-examples/before-after-curation.md`).

**Ограничения.** Пара берётся по форме таблицы, смысл не проверяется: новые таблицы приёмов попадают в выход, пока их не
внесли в `EXCLUDE` (выборка — перед каждой сборкой); жанр `all` (лексика C) широк — потребитель фильтрует по `marker_id` и
`lang`; «эффект не доказан» у большинства пар — честно: пары показывают правило, а не рост конверсии.

## Утилиты волны 4: `check_links.py` (X2) и `sources_collect.py` (S1b), 2026-09-24

Проверка базы и сводная библиография. Ключи, проверки и порядок пересборки — в шапке каждого файла (`sed -n 1,62p`);
отчёты авторов — `99-raw/reports/wave4-X2-checks.md` §1 и `99-raw/reports/wave4-S1b-sources-handoff.md`.

| Команда | Что делает | Выход |
|---|---|---|
| `python3 ../maint/check_links.py [--quiet-info] [--only а,б] [--out ФАЙЛ] [--json ФАЙЛ] [--selftest]` | ссылки в `.md` папок 00–10, 90, 91 и корня: (а) пути к файлам и папкам, в том числе соседних баз; (б) `§N.M`; (в) `[S<n>]`; (г) `[V:<id> mm:ss]`; (д) README папок против диска; (е) обязательные разделы; (ж) `[проверено: …]` → папки опытов. Копия ai-media, адаптирована X2 | сводка по проверкам и категориям, строки ERROR / WARN / INFO; код 1 при ERROR |
| `python3 99-raw/tools/sources_collect.py [--check \| --selftest \| --stats \| --unparsed]` | «## Источники» `.md` папок 01–10 и шапки дайджестов → `90-sources/sources.tsv` (8 колонок: `url, title, author_org, year, type, used_in, reliability, notes`) и автоблок `90-sources/README.md`; дедупликация по нормализованному URL, законы без URL — по обозначению; руками TSV не править | `--check`: 0 — совпадает со сборкой, 1 — нет |

Проверено: 24.09 21:38 — `check_links.py --selftest` 27 из 27, полный прогон `--quiet-info` — ERROR 0, WARN 0 (после
S1a и S1b); `sources_collect.py --selftest` — 28 проверок, `--check` — 0 (355 записей, автоблок совпадает). Файл
передачи `../../kb/text/99-raw/handoff-to-neighbours.md` `check_links.py` не обходит (папка `../../kb/text/99-raw/`) — его 448 ссылок S1b сверил
своим скриптом (отчёт S1b §4).

## Утилиты оркестратора: `orch_check.py`, `extract_for_audit.py`, `ctx_watch.py` (оркестратор волн, 2026-09-24)

Не часть конвейера текста: приёмка агентов, извлечения для аудита, контроль контекста. Описание и ключи — в шапке
каждого файла (`python3 <утилита> -h` или `sed -n 1,30p`).

| Команда | Что делает | Выход |
|---|---|---|
| `python3 ../maint/orch_check.py <папка\|all> [--selftest-tools] [--md]` | приёмка: обязательные разделы содержательных `.md`, строка метаданных, пометка ЧЕРНОВИК, метки (известные — таблица PLAN «Метки доказательности», с 17:48 — и `[стандарт базы]`, `[решение базы]`), штампы; YAML и JSON загружаются, у YAML есть `date`; README в папках; с `--selftest-tools` — `--selftest` утилит агентов | строки `[ok\|warn\|ERROR] файл (вид, строк)`; код 1 при error. Виды: `content`, `readme`, `video` (всё в `91-videos/`), `glossary` (`../../kb/text/00-glossary/`: свой формат, без обязательных разделов; с 17:49) |
| `python3 99-raw/tools/extract_for_audit.py [--out DIR]` | извлечения для аудитора и синтезатора: по папкам 01–10 — метаданные, «Выжимка», «Открытые вопросы», «Чек-лист», README целиком, ключи YAML; `reports.md` — разделы отчётов волн; `videos.md`; `_inventory.md` | `99-raw/notes/wave4/extracts/` (прогон 24.09 15:26: 13 файлов, `reports.md` 287 КБ) |
| `python3 99-raw/tools/ctx_watch.py status` · `watch --wrap 800000 --hard 900000 --every 60` | точный размер контекста агентов по `usage` транскрипта; события WRAP (800 тыс. — «ЗАКРУГЛЯЙСЯ СЕЙЧАС»), HARD, COMPACT (новое автосжатие) для Monitor | реестр агентов — `99-raw/notes/agents-running.tsv` (метка, id, `running \| stopping \| done`) |

Проверено: `orch_check.py all --selftest-tools` 24.09 17:48 — 131 файл, 0 ошибок (1 warning у глоссария до вида
`glossary`; после — 0).
