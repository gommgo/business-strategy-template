# Глоссарий базы ai-media-research

Волна 4 · агенты S и S2 (синтез) · 24.09.2026 · собран из разделов «Термины для глоссария» 26 отчётов волн 1–4
(`99-raw/reports/wave1-*`, `wave2-*`, `wave3-*`, `wave4-X-audit.md`: 722 записи, из них M — 33, X — 12) · после слияния
дублей терминов — **263** в 11 группах · каждое определение сверено с итоговыми файлами папок 01–15 (указатель → файл
§раздел) и порогами `11-evaluation-qa/thresholds.yaml`; реестр противоречий — `../CONTRADICTIONS.md`.

## Как пользоваться

- **Запись**: `**Термин** (English; синонимы) — определение с числом, порогом или условием → путь §раздел`. Путь — от этой
  папки; раздел — заголовок `## N.` или `### N.M` целевого файла. Там же — метка доказательности, источники и опыт.
- **Поиск**: по-русски — `grep -n '^\*\*Термин' 00-glossary/glossary.md`; по-английски — `grep -in 'term' 00-glossary/glossary.md`
  или указатель §13; не знаешь группу — указатель §14.
- **Омонимы и расхождения** (паспорт, ворота, живость, шов, резерв, двойник и близнец, GNED, мезонин) — §12: какие
  значения встречаются в файлах и какое принято в базе.
- **Скоропортящееся**: модели, цены, параметры и даты в определениях — на 23–24.09.2026 (снимки каталога polza
  `2026-09-23_1745` и `2026-09-24`); перед решением сверять с `13-routing-matrix/routing.yaml` и свежим снимком.
- Внутри группы термины идут по алфавиту: сначала кириллица, затем латиница и символы.

## Содержание

| № | Группа | Терминов |
|---|---|---|
| 1 | Генерация и модели | 13 |
| 2 | Промтинг | 22 |
| 3 | Арт-дирекшн, серии и антислоп | 31 |
| 4 | Видео: генерация, петли, движение | 26 |
| 5 | Вектор и иконки | 12 |
| 6 | Постобработка и кодирование | 30 |
| 7 | Доставка на страницу | 25 |
| 8 | Оценка и приёмка | 27 |
| 9 | Право и маркировка | 27 |
| 10 | Провайдеры, каналы и деньги | 25 |
| 11 | Маршрутизация, стенд и обновление | 25 |
| 12 | Омонимы и расхождения терминологии | 19 строк |
| 13 | Указатель EN → RU | — |
| 14 | Указатель RU | — |

## 1. Генерация и модели

**Ассет** (asset) — файл, заполняющий слот страницы: картинка, видео, SVG, Lottie, шейдер или CSS; у каждого — спецификация, паспорт генерации и приёмка. → `../01-web-assets-landscape/01-asset-slots-by-page-type.md` §1

**Гибридный продакшн** (hybrid AI production) — реальная съёмка или настоящий товар + ИИ-окружение и правки; допустимая форма там, где генерировать нельзя (люди, товар, команда). → `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §1.1; `../08-image-post-processing/02-upscale-outpaint-edit.md` §3

**Код задачи** (task code) — идентификатор типа задачи из таксономии базы (`IMG-HERO-PHOTO`, `VID-HERO-LOOP`, `VEC-ICON-LINE` …; 32 кода + предложенный `IMG-LAYERS`); по нему выбирается маршрут в `routing.yaml`. → `../13-routing-matrix/03-routing-matrix.md` §6, §1

**Лестница дешевизны** (cheapness ladder) — порядок выбора средства для слота: текст → SVG → CSS-градиент или шейдер → картинка → видео → 3D; берётся первая ступень, решающая задачу (тёмный градиент — только CSS). → `../01-web-assets-landscape/01-asset-slots-by-page-type.md` §1

**Лучший из N** (best-of-N; curation) — генерация N вариантов и отбор: автопроверки → VLM-рубрика (после калибровки) → человек; отдельный режим с отдельной ценой; отбор снижает узнаваемость ИИ на 4–31 п. п. → `../13-routing-matrix/01-stand-method.md` §4.3; `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §4

**Мульти-референс** (multi-reference) — несколько входных картинок в одном вызове; лимит вендора (NB Pro 14, GPT Image 16, FLUX.2 8) ≠ сколько модель держит: оптимум 1–3 на вызов. → `../06-art-direction-consistency/02-series-and-consistency.md` §2.1

**Открытые веса** (open weights; LoRA) — опубликованные параметры модели для запуска у себя; право на коммерцию задаёт только LICENSE (FLUX.2 [dev] — некоммерческая, Qwen Image 2.1 — исследовательская); генерация и дообучение LoRA здесь вне рамок (нет CUDA, GPU-сервер — только транскрипция). → `../02-providers-platforms/05-open-weights-landscape.md` §9; `../12-legal-provenance/01-licenses-by-vendor-and-channel.md` §4

**План ассетов** (asset plan) — YAML-список слотов страницы: варианты кадров, соотношения, бюджеты, движение, доставка, приёмка; вход спецификации ассета и маршрутизации. → `../01-web-assets-landscape/01-asset-slots-by-page-type.md` §8

**Референс** (reference image / video; omni reference) — входная картинка или видео — ориентир объекта, персонажа, стиля или движения, не обязательно кадр ролика: у Seedance 2.x `images` — референсы (омни-референс: картинки, видео, аудио), а не первый кадр. → `../05-prompting/05-edit-reference-series.md` §3; `../04-video-models/02-model-cards.md` §3.7

**Слот** (slot) — место на странице с ролью (hero, логотипы, фича, отзыв, OG, фавикон), которое заполняет ассет; слот задаёт соотношения, бюджет КБ, движение и место под текст. → `../01-web-assets-landscape/01-asset-slots-by-page-type.md` §2

**Ступени разрешения и качества** (resolution tier 1K/2K/4K; quality level) — цена картинки растёт ступенями разрешения (у NB Pro в polza 1K = 2K = 13,5 ₽) и уровнем `quality` (`low … max` у GPT Image: число токенов); фотореализм — в 2K, 4K и апскейл дают «пластик»; в polza у GPT Image 2.5 `quality` нет (плоские 4 ₽), в RouterAI есть (`high` 16:9 — 3,62 ₽). → `../08-image-post-processing/02-upscale-outpaint-edit.md` §1.1; `../02-providers-platforms/04-direct-apis-and-services.md` §2.2; `../13-routing-matrix/03-routing-matrix.md` §2

**Черновой режим** (draft mode; draft → final) — дешёвый прогон низкого разрешения с согласованным дорогим финалом (Seedance 2.5 Draft 480p → 1080p, MiniMax Regeneration 768P → 2K, Luma draft → master); в polza нет — черновик делают дешёвой моделью. → `../09-video-pipeline/04-i2v-protocols.md` §9; `../04-video-models/02-model-cards.md` §6.4

**Hero** (hero section, key visual) — первый экран с главным визуалом, H1 и CTA; мастер ≥ 2560 px (полноэкранный — 3840), отдельный кадр для телефона у 8 из 10 лидеров. → `../01-web-assets-landscape/01-asset-slots-by-page-type.md` §2.2

## 2. Промтинг

**Безмасочная правка** (maskless / semantic-mask editing) — модель сама находит область по тексту; сохранность «не на 100 %» — всегда проверять `edit_check.py` и маской из разницы. → `../05-prompting/05-edit-reference-series.md` §2.1; `../11-evaluation-qa/01-metrics-and-asset-audit.md` §3.3

**Диалект промта** (prompt dialect: prose, sections, JSON, IR) — форма и словарь промта, которые модель выполняет лучше: проза, проза по разделам с метками («Scene: …»), JSON, IR «ключ: проза» (MiniMax H3-Context-IR); умолчания по семействам — `dialects.yaml` v0.3. → `../05-prompting/03-asset-spec-and-dialects.md` §9; `../05-prompting/01-vendor-prompt-guides.md` §9

**Замки** (locks) — неизменяемые свойства в системном промте серии или правки — идентичность, материал, пропорции, один свет, окружение («keep this exact …»); гарантия неизменности — вклейка и `edit_check.py`, а не слова промта. → `../14-recipes/02-series-product-recipes.md` §5.3

**Класс входа модели** (model input class; LLM front-end) — как модель читает промт: A — LLM-фронт (Nano Banana, GPT Image, Gemini Omni, Veo 3.x: форма безразлична), B — языковой энкодер, C — T5/CLIP (чувствителен к порядку и «no X»), D — обучена на структуре (Ideogram 4, Bria FIBO, MiniMax H3); промт «вне распределения подписей обучения» выполняется хуже. → `../05-prompting/01-vendor-prompt-guides.md` §1.1; `../05-prompting/02-structured-json-prompting.md` §3

**Компилятор промтов** (prompt compiler, `prompt_compile.py` v2.1; compile passport) — переводит спецификацию в диалект модели и параметры канала с проверками до генерации (длина, негатив, число референсов, цена); пишет паспорт компиляции `meta.compile`: хэш спецификации, диалект, опции, версия, снимок каталога. → `../05-prompting/03-asset-spec-and-dialects.md` §12; `../05-prompting/04-video-prompting.md` §9; `../05-prompting/06-ab-protocol.md` §2

**Многоходовая правка** (multi-turn editing; iterative edit chain) — последовательные правки от предыдущего результата (`previous_response_id`); качество деградирует — порции правок от мастера, а не бесконечная цепочка. → `../05-prompting/05-edit-reference-series.md` §1.5

**Негативный промт** (negative prompt; CFG) — отдельное поле «чего не должно быть», действует через CFG (вычитается только при CFG > 1; у Z-Image Turbo guidance 0 — бесполезен); в polza — только `wan/2.5` (`negative_prompt` ≤ 500); у FLUX.2, Gemini, Recraft V4 поля нет. → `../05-prompting/01-vendor-prompt-guides.md` §12.1, §7.4

**Оберег** (preserve list; preservation suffix) — перечень того, что правка не трогает, + закрывающая фраза («Keep everything else unchanged», «Maintain the original composition and subject»). → `../05-prompting/05-edit-reference-series.md` §1.1

**Переписчик промта** (prompt rewriter / upsampler / enhancer; prompt expansion) — встроенная LLM переписывает промт до генерации (`prompt_upsampling` FLUX.2, `enhance_prompt` Veo, `prompt_extend` Wan, `prompt_optimizer` MiniMax); у FLUX.2 [pro] в polza не отключается (`disable_pup` не выставлен); «расширение промта» Google 2023 — другое: несколько промтов ради разнообразия. → `../05-prompting/02-structured-json-prompting.md` §6.1, §6.2; `../05-prompting/04-video-prompting.md` §6.2

**Плечо A/B** (A/B arm) — вариант формы промта при одинаковом содержании (опция компилятора); A/B ≤ 250 ₽ — только скрининг крупных эффектов: 10 пар → ± 15 п. п., ± 10 п. п. — от 30 пар. → `../05-prompting/06-ab-protocol.md` §2, §3

**Позитивная замена запрета** (positive exclusion replacement; semantic negative) — описание отсутствия без новых предметов («an empty, deserted street», «no one in the frame», «only real physical objects») — поле `exclusions[].replace_with`. → `../06-art-direction-consistency/01-visual-dna-from-ui.md` §4.3

**Правка по инструкции** (instruction-based editing; target value) — правка картинки текстом по формуле «что изменить → где → что не трогать»; ≤ 5 изменений за вызов; цель — точным значением («#1F5E3B», «2700 K»), а не «darker», «warmer». → `../05-prompting/05-edit-reference-series.md` §1.1, §1.2, §1.3

**Промт продукта из 7 блоков** (product seven-block prompt) — композиция → идентичность → типографика (точные слова в кавычках, место) → цвет → свет → оптика → запреты; товар с текстом. → `../05-prompting/05-edit-reference-series.md` §5.1

**Роль референса** (reference role) — назначение входной картинки фразой по номеру: «Image 2: style reference» — стиль, идентичность, продукт, палитра; отдельного поля роли нет ни у одного вендора. → `../05-prompting/05-edit-reference-series.md` §3.1; `../06-art-direction-consistency/02-series-and-consistency.md` §2.2

**Скилл вендора** (vendor prompt skill) — официальный шаблон «родного» промта для агентов (`sd25-pe`, `sd2-pe`, `wan3-pe`, `h3-prompt-writing`, `black-forest-labs/skills`); читать как первоисточник диалекта, лицензии проверять. → `../05-prompting/04-video-prompting.md` §6.2; `../12-legal-provenance/01-licenses-by-vendor-and-channel.md` §9

**Слова качества** (quality words / boosters) — «cinematic, 4K, masterpiece» — не описывают видимого; против — Runway, MiniMax, BFL, `wan3-pe`, `sd25-pe` (только `sd2-pe` требует); вместо них — оптика, свет, фактура. → `../05-prompting/04-video-prompting.md` §7

**Служебный запрет** (service exclusion) — запрет текста, водяного знака, логотипа, субтитров, музыки («No text.», «No other text appears in the image.»); ставится последним в промте. → `../05-prompting/03-asset-spec-and-dialects.md` §7; `../05-prompting/01-vendor-prompt-guides.md` §2.7

**Смешанная правка** (mixed-operation / multi-step edit) — несколько операций (замена, добавление, удаление) в одном вызове — у каждой свой глагол; > 5 изменений выполняется частично (≈ 550 отзывов Gamma). → `../05-prompting/05-edit-reference-series.md` §1.4

**Спецификация ассета** (asset spec) — JSON без привязки к модели (`asset-spec.schema.json` v0.2): сюжет, композиция, камера, свет, палитра, референсы, запреты, текст, выход, движение; внутренний контракт системы. → `../05-prompting/03-asset-spec-and-dialects.md` §2

**Шаблон эффекта** (effect template) — постоянный блок промта, задающий эффект, с переменными объектом и фоном — серия «один эффект на разных предметах». → `../05-prompting/05-edit-reference-series.md` §4.2

**JSON-промт** (JSON / structured prompt) — промт-объект с полями (scene, subjects, style, lighting, camera …); документирован у FLUX.2, Ideogram 4 обучен на JSON; для LLM-фронта форма не рычаг качества — в базе JSON только внутренний контракт. → `../05-prompting/02-structured-json-prompting.md` §8

**«No X» в прозе** (in-prompt negation; pink elephant effect) — запрет словами внутри промта; у энкодерных моделей (класс C) упоминание вызывает предмет; у Google допустимо только семантически, у FLUX.2 не писать. → `../05-prompting/01-vendor-prompt-guides.md` §12.1; `../06-art-direction-consistency/01-visual-dna-from-ui.md` §4.2

## 3. Арт-дирекшн, серии и антислоп

**Безопасная полоса** (safe band; safe crop zone) — часть мастера, видимая во всех соотношениях слота; из 16:9 в 9:16 остаётся 31,6 % ширины — зона текста слева телефон не переживает. → `../06-art-direction-consistency/03-composition-for-web.md` §3.3

**Блок против «среднего»** (anti-average composition) — вне центра, асимметрия, взгляд не в камеру, грязный передний план; фразу подбирать по содержанию кадра, а не вставлять всегда. → `../06-art-direction-consistency/04-slop-and-color-harmony.md` §1.3; `../05-prompting/05-edit-reference-series.md` §4.3

**Блок стиля серии** (series style block; block + slots + iterator) — дословно одинаковый абзац видимых признаков стиля, первый в промте каждого кадра серии; шаблон серии — блок + слоты сюжета + пакетный прогон, на масштабе — отбор входа, а не выхода. → `../06-art-direction-consistency/01-visual-dna-from-ui.md` §4.1; `../06-art-direction-consistency/02-series-and-consistency.md` §5.1; `../05-prompting/05-edit-reference-series.md` §4.1

**Гид пропорций** (proportion guide) — кадр или шаг, где товар стоит рядом с предметом известного размера на той же глубине (кружка 8–9 см, ладонь, книга); проверка — отношение высот по маскам против габаритов, допуск ± 15 % `[мнение M]`; масштаб чинят вырезом и вставкой, не перегенерацией. → `../14-recipes/02-series-product-recipes.md` §3.1

**Гиперреализм ИИ-лиц** (AI hyperrealism) — синтетические лица принимают за реальные чаще настоящих и считают надёжнее — поэтому людей, отзывы и команду не генерировать. → `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §1.3

**Грейд** (grade; parametric LUT, `.cube`) — цветовое решение серии: баланс белого, кривая светлоты, хрома, зерно; один параметрический `.cube` из чисел паспорта на картинки и видео (ffmpeg `lut3d`, ΔE 0,002); отделка, а не стиль. → `../06-art-direction-consistency/01-visual-dna-from-ui.md` §7.1, §7.2; `../06-art-direction-consistency/04-slop-and-color-harmony.md` §4.3

**Зона под текст** (text zone; negative space, copy space; edge density) — спокойная пустая область кадра под HTML-текст: плотность краёв (доля пикселей с перепадом яркости > 0,10) ≤ 0,06; просить описанием пустоты в композиции. → `../06-art-direction-consistency/03-composition-for-web.md` §1, §1.3

**Канарейки** (canary subjects) — 5 постоянных тестовых сюжетов разных классов для проверки паспорта и стиля на новой модели или версии (5 генераций × 4–5 ₽). → `../06-art-direction-consistency/01-visual-dna-from-ui.md` §8, §4.4

**Класс сюжетов референса** (reference subject class) — тип сцен, на которых собран референс; вне своего класса референс тянет чужое содержание — `to-spec --ref-class`. → `../06-art-direction-consistency/02-series-and-consistency.md` §2.5

**Кластер маркеров** (marker cluster) — ≥ 3 маркеров на ассете или ≥ 2 в ключевом слоте (hero, товар) — диагноз «слоп», ассет не публикуется. → `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §5.1; `../11-evaluation-qa/01-metrics-and-asset-audit.md` §3.9

**Клише «про ИИ»** (AI content clichés) — фиолетовая аврора, светящийся мозг, стеклянный тор, хромированный блоб, изометрический город, «команда радуется»; заменять сюжетом из предметной области. → `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §5.4; `../06-art-direction-consistency/01-visual-dna-from-ui.md` §4.4

**Лист ракурсов** (character / product sheet; turnaround; angle sheet) — один референс с несколькими ракурсами персонажа или продукта на белом; держит идентичность серии («mini LoRA»); недостающий ракурс — отражением; продукт-концепт — 9 ракурсов с замками, настоящий товар — 3–4 фото или рендера. → `../06-art-direction-consistency/02-series-and-consistency.md` §3.2; `../14-recipes/02-series-product-recipes.md` §2.1

**Маркер сгенерированности** (AI-tell marker, `IMG-Mxx`, `VID-Mxx`) — наблюдаемый признак ИИ-происхождения из каталога A: 25 маркеров картинок (пластиковая кожа, тёплый сдвиг b* > +4, пурпур, «строго по центру» …), 18 видео; маркеры датируются. → `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §5.2, §5.3

**Набор одним вызовом** (set-aware generation; 2×2 grid) — несколько кадров серии в одной генерации (сетка 2×2 → нарезка, `sequential_image_generation` у Seedream — вне polza); согласованнее, чем по одному. → `../06-art-direction-consistency/02-series-and-consistency.md` §4

**Паспорт визуала** (visual DNA passport) — машиночитаемые числа и правила изображений бренда из токенов UI и эталонов (`visual-dna.schema.json`): палитра, грейд, свет, камера, композиция, блоки стиля, запреты, приёмка; собирает машина, утверждает человек. → `../06-art-direction-consistency/01-visual-dna-from-ui.md` §2

**Перенос цвета** (colour transfer, Reinhard, MKL) — подгонка статистики цвета к эталону; годится только внутри класса сюжетов: с эталона другой сцены ΔE падает в 4 раза, картинка портится. → `../06-art-direction-consistency/04-slop-and-color-harmony.md` §4.2

**Пластиковость** (plasticky look, `IMG-M01`) — восковая кожа без пор, ткани и дерево без микрофактуры; растёт в 4K и после апскейла («too AI too smooth»). → `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §5.2; `../06-art-direction-consistency/04-slop-and-color-harmony.md` §2.4

**Плёночное зерно** (film grain) — мелкий шум фактуры против «пластика»; держится в 2K, исчезает в 4K; на странице накладывать поверх после декодирования (CSS-шум), в файл не запекать. → `../06-art-direction-consistency/01-visual-dna-from-ui.md` §7.3; `../10-web-integration/03-text-over-media-and-effects.md` §4.3

**Покрытие цвета** (colour coverage; invented colour) — доля пикселей в ΔE OKLab ≤ 0,05 от заявленного цвета; цвет паспорта найден, если покрыты ≥ 3 из 5 hex; «придуманный цвет» VLM — покрытие < 1/3 заявленной доли («golden yellow 30 %» — 0,1 %): палитру снимает код. → `../06-art-direction-consistency/01-visual-dna-from-ui.md` §6.2; `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §1.2

**Пороги серии** (series hue spread; palette ΔE; drift) — дрейф серии ловится бесплатно по цвету: круговой разброс среднего оттенка ≤ 10° и ΔE палитр OKLab ≤ 0,045 — одна серия; > 25° или > 0,06 — распад; смысл — судья. → `../06-art-direction-consistency/02-series-and-consistency.md` §6.1, §6.2

**Референс-«кубик»** (material swatch reference) — образец материала на простой форме; форма 3D-иконки — свой рендер или SVG, материал — отдельный референс-кубик. → `../06-art-direction-consistency/02-series-and-consistency.md` §3.3

**Референс-доминанта** (dominant reference element) — яркий признак одного референса, повторяющийся в выдаче; убирать кадрированием или заменой референса, а не «no X». → `../06-art-direction-consistency/02-series-and-consistency.md` §2.4

**Слоп** (AI slop; video slop) — усреднённый ИИ-визуал без решений автора, опознаваемый по кластеру маркеров; слоп — в содержании и композиции, а не в цвете; видео-слоп — «вайб» без сути: дрейф, статичность, нелогичный монтаж. → `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §5

**«Средний вид»** (average look; default aesthetic; saliency centroid) — эстетика модели без указаний: центр, симметрия, средний план, взгляд в камеру, идеальный свет; мера — центр масс значимости |x − 0,5| < 0,08. → `../06-art-direction-consistency/04-slop-and-color-harmony.md` §1, §1.1

**Стилевой референс** (style reference; style code, `style_id`, `--sref`; moodboard) — картинка, из которой модель берёт стиль, а не сюжет; стиль держат вместе блок стиля + палитра + 1–3 референса одной съёмки (мудборд из 8 разнородных усредняется в чужие признаки); стиль-код — Recraft `style_id` из 1–10 картинок, Midjourney `--sref` (вне polza, у Midjourney нет API). → `../06-art-direction-consistency/02-series-and-consistency.md` §2.3, §2.1, §1

**Фокусная точка** (focal point; percentage alignment) — точка кадра (x, y) в долях, которая остаётся в каждом кадрировании; задаётся автором и переводится формулой в CSS `object-position` (процентное выравнивание). → `../06-art-direction-consistency/03-composition-for-web.md` §3.1, §3.2

**Функциональный артефакт** (functional implausibility) — предмет в кадре не может работать так, как изображён (нерабочая ручка, лишний сустав); 58,7 % ИИ-картинок, замечают редко. → `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §4

**Цвет секции** (env colour, `palette.env_color`) — цвет фона секции страницы под ассетом: фон и рефлексы 3D-иконок, фон выреза и цвет контактной тени — иначе ореол и «наклеенность» (вставка не согласована по свету, тени, краю). → `../06-art-direction-consistency/01-visual-dna-from-ui.md` §2; `../08-image-post-processing/01-background-removal-matting.md` §6

**Эталон серии** (series anchor; anchor image) — утверждённый кадр, от которого строятся остальные кадры, ракурсы и видео («make the rest»). → `../06-art-direction-consistency/02-series-and-consistency.md` §3.1

**Эффект Instagram-фильтра** (Instagram-filter effect; overprocessing) — перенасыщенность, локальный «HDR», резкость, гладкая кожа; люди выбирают его, но он выдаёт ИИ: colorfulness > +50 % и `hdr_index` > +0,1 к эталону. → `../06-art-direction-consistency/04-slop-and-color-harmony.md` §2

**ΔE** (colour difference: ΔE00 (CIEDE2000), ΔE OKLab) — цветовое расстояние: ΔE00 — для сохранности, дрейфа и стыков (2 — порог дрейфа, 5 — «изменённый пиксель»), ΔE OKLab — для палитр (0,02–0,06). → `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.2; `../06-art-direction-consistency/02-series-and-consistency.md` §6.1

## 4. Видео: генерация, петли, движение

**Бесшовная петля** (seamless loop; native loop) — ролик, чей последний кадр переходит в первый без видимого стыка; приёмка — двумя числами сразу: `seam_ratio_local` ≤ 1,5 после среза и `motion_vs_control` ≥ 0,5; нативная петля параметром — только Luma Ray 3.2 (`loop: true`, вне polza). → `../09-video-pipeline/01-seamless-loops.md` §1.1; `../04-video-models/02-model-cards.md` §4.1

**Две половины** (two-halves loop) — клип 2 генерируется от последнего кадра клипа 1 обратно к первому кадру клипа 1; запасной путь, когда [A,A] даёт статичную петлю; цвет стыка ΔE00 < 2. → `../09-video-pipeline/01-seamless-loops.md` §3.5; `../09-video-pipeline/04-i2v-protocols.md` §4.2

**Движения камеры** (push-in, orbit, tracking, turntable) — наезд, облёт по дуге 180–360°, боковой проезд, оборот продукта 360°; у каждого семейства своя грамматика, в петле камера стоит. → `../05-prompting/04-video-prompting.md` §2.1; `../04-video-models/03-capabilities-by-task.md` §4

**«Живость»** (motion liveness, `motion_med`, `motion_vs_control`) — медиана MAD соседних кадров; `motion_vs_control` — к i2v-контролю того же кадра без второго кадра, ≥ 0,5; тихие петли лидеров — `motion_med` 0,13–0,2. → `../09-video-pipeline/01-seamless-loops.md` §1.1, §1.2

**Запрет движения** (motion constraint; restrained motion) — «No zoom. No spin.» или утвердительно «The focal length stays fixed.»; для элементов hero — без зума, вращения и смещения объекта; запреты — последними. → `../05-prompting/04-video-prompting.md` §1.4

**Интерполяция кадров** (frame interpolation, RIFE, FILM) — досчёт промежуточных кадров; RIFE v4.6 ncnn-Vulkan работает локально на Iris Xe; Topaz — платно. → `../09-video-pipeline/04-i2v-protocols.md` §8; `../02-providers-platforms/05-open-weights-landscape.md` §6.3

**Кроссфейд хвоста** (tail crossfade; gap bridging) — наложение последних L кадров на первые, когда петля не замкнулась: 12 кадров при 24 fps — шов 7,5–9,7 → 1,1–1,5 (ffmpeg `blend` с `+0.5`); мост RIFE — только 1–3 кадра текстурного движения, на этикетке ломает буквы. → `../09-video-pipeline/01-seamless-loops.md` §3.2, §3.4

**Мёртвый кадр** (dead frame; ring joint) — кадр на конце клипа, почти не отличающийся от соседнего (< 0,25 × медианы): ≤ 3 — срезать, > 3 — `collapse_suspect`; на круговом стыке цепочки клипов срезать оба мёртвых конца. → `../09-video-pipeline/01-seamless-loops.md` §3.1

**Мульти-шот** (multi-shot; single-shot; continuity contract) — несколько планов со склейками в одной генерации; у Kling 3 `multi_shot` по умолчанию включён — для петли выключать и писать контракт непрерывности «same set and geometry, no cuts»; склейку ловит `cut_ratio` > 10. → `../05-prompting/04-video-prompting.md` §5.3, §5.2; `../09-video-pipeline/01-seamless-loops.md` §2

**Неподвижная камера** (locked-off / static camera; `fixed_lens`) — штатив: камера не двигается; параметр только у Seedance 1.5 Pro (`fixed_lens`), у остальных фраза «Locked camera» — «advisory», дрейф возможен; «locked-on» у BFL — камера едет за субъектом. → `../05-prompting/04-video-prompting.md` §2.2, §2.3

**Нормализация выхода модели** (output normalization; MP4 edit list) — снятие звука (`-an`), `moov` вперёд (`+faststart`), стандартный размер и `yuv420p`, полные теги BT.709 — до мезонина; после `setpts` добавлять `-r`, иначе edit list MP4 срежет последний кадр (ffmpeg 7.1.5). → `../09-video-pipeline/03-encoding-and-budgets.md` §6; `../09-video-pipeline/01-seamless-loops.md` §3.1

**Первый и последний кадр** (first-last frame, FLF, FL2V, keyframes) — генерация ролика между двумя заданными кадрами — основа петли и перехода; в polza: Seedance 1.5 Pro, Kling 3, Veo 3.1, MiniMax H3 Max, GA `google/gemini-omni-1.1-flash` (`first_frame_url` + `last_frame_url`). → `../05-prompting/04-video-prompting.md` §3.1; `../09-video-pipeline/04-i2v-protocols.md` §2

**Перечень фонового движения** (background motion list; ambient motion) — движение каждого элемента фона глаголом (вода, облака, листва, свет): что не названо — не движется. → `../05-prompting/04-video-prompting.md` §1.2

**Петля [A,A]** (same-frame FLF loop; duplicate seam frame; quiet loop) — одна картинка в слотах первого и последнего кадра; последний кадр выхода — дубль A (микропауза раз в цикл, `dup_last`), его срезают по построению; дешёвый путь — `bytedance/seedance-1.5-pro` + `fixed_lens`, 5,25 ₽ за 480p 4 с. → `../09-video-pipeline/04-i2v-protocols.md` §2.1; `../09-video-pipeline/01-seamless-loops.md` §3.1; `../14-recipes/01-hero-recipes.md` §2.1

**Пинг-понг** (ping-pong, boomerang) — ролик вперёд и назад: шов 1,0 по построению, но вода и облака «текут назад»; только для симметричного движения (дыхание, покачивание, свет); ловит `pingpong_suspect`. → `../09-video-pipeline/01-seamless-loops.md` §3.3

**Ползущая камера** (camera creep) — медленный дрейф кадра в ИИ-видео: 0,1 px/кадр + экспозиция +3 % дают шов 45,5; маской не лечится, порог `cam_shift_max_px` < 1. → `../09-video-pipeline/01-seamless-loops.md` §2

**Продление** (extend) — генерация продолжения готового ролика: в polza — только Veo 3.1 `extend`, 45 ₽ за шаг (1080p продлить нельзя); Seedance 2.5 и Wan 3.0 дают до 30 с одной генерацией; для сайта длинное видео — секция-история, не петля hero. → `../02-providers-platforms/02-polza-models-params-prices.md` §2.7; `../09-video-pipeline/04-i2v-protocols.md` §4.5

**Промт «только движение»** (motion-only prompt) — i2v-промт описывает только движение; сцену, свет и внешность модель берёт из стартового кадра. → `../05-prompting/04-video-prompting.md` §1.1

**Пульс ключевого кадра** (keyframe pulse; loop pop) — скачок качества I-кадра в начале петли над последним кадром (H.264 CRF 23: +2,12 дБ); `-tune grain` уменьшает, но не убирает. → `../09-video-pipeline/03-encoding-and-budgets.md` §4

**Синемаграф** (cinemagraph; static mask; masked merge, `maskedmerge`) — движение в части кадра при неподвижной камере: неподвижное — стоп-кадр по маске неподвижных зон, движение — петлёй; склейка по маске — неподвижное из резкого мастера 2K, движущееся из 720p-видео (`maskedmerge`); `drift_max` < 1,0; CRF — по движению внутри маски (`keep_in`). → `../09-video-pipeline/02-cinemagraph-alpha.md` §3; `../14-recipes/01-hero-recipes.md` §4.3

**Статичный коллапс** (static collapse) — угасание или отсутствие движения при одинаковых первом и последнем кадрах — главный риск петли FLF; равномерно слабое движение ловит только `motion_vs_control`. → `../09-video-pipeline/01-seamless-loops.md` §2

**Таймкод-промтинг** (timestamp prompting) — разметка действий по отрезкам «[0s–3s] …»; поддерживается не всеми (у Seedance 2.0 запрещён, у 2.5 — да). → `../05-prompting/04-video-prompting.md` §5.1

**Цепочка клипов** (clip chaining; chain anchor) — последний кадр клипа N — первый кадр клипа N + 1; опора цепочки — извлечённый или исходный кадр (спор решает тест I-07); правленый конечный кадр подогнать по цвету до генерации. → `../09-video-pipeline/04-i2v-protocols.md` §4.2, §4.3

**Шов петли** (loop seam; `seam_ratio`, `seam_ratio_local`) — стык «последний кадр → первый»; `seam_ratio` = MAD(последний, первый) / `motion_med` — справочно, локальный — к медиане 3 пар у каждого конца, ≤ 1,5 после среза; ≈ 0 — дубль кадра, а не идеал; мерить на выходе модели или мезонине без потерь (H.264 CRF 23 превращает 0,98 в 4,74). → `../09-video-pipeline/01-seamless-loops.md` §1.1, §1.3

**All-intra** (all-intra encoding; GOP) — каждый кадр ключевой (`-g 1`): точная перемотка ценой веса ×9,3; для прокрутки база берёт GOP 8 (×3) или секвенцию кадров. GOP — группа кадров от ключевого до ключевого. → `../09-video-pipeline/03-encoding-and-budgets.md` §7

**t2v, i2v, v2v** (text- / image- / video-to-video) — генерация видео из текста, из картинки (первый кадр) или правка готового видео; для ассетов сайта основной режим — i2v от утверждённого кадра. → `../04-video-models/02-model-cards.md` §1; `../09-video-pipeline/04-i2v-protocols.md` §1

## 5. Вектор и иконки

**Векторизация** (vectorization, tracing, vtracer, potrace) — перевод растра в SVG; плоские картинки ≤ 8 цветов — почти без потерь (цвет контура — в палитру); путь «растр → векторизация» для плоских иллюстраций. → `../07-vector-svg-icons/02-vector-generators-and-tracing.md` §7

**Живая область** (live area) — часть холста иконки под рисунок: 20 из 24 у Material, 22 у Lucide. → `../07-vector-svg-icons/01-svg-by-llm.md` §2

**Маскируемая иконка** (maskable icon) — иконка PWA: значимое — в центральном круге 80 % (409 из 512 px); обычному сайту хватает 3 файлов фавикона ≈ 4 КБ. → `../07-vector-svg-icons/03-icon-sets-and-patterns.md` §5

**Нарисованное отверстие** (painted counter) — «дырка» в SVG, закрашенная цветом фона вместо вырезания; у «линейных» иконок Recraft (залитые контуры) под `currentColor` в тёмной теме — сплошное пятно. → `../07-vector-svg-icons/02-vector-generators-and-tracing.md` §4

**Оптический вес** (visual weight) — плотность «пятна» иконки при размытии рядом с эталонными кругом и квадратом; коридор Lucide 0,7–1,55 (`check_icons.py`). → `../07-vector-svg-icons/01-svg-by-llm.md` §3, §4

**Плитка паттерна** (pattern tile, `VEC-PATTERN`) — повторяемый фрагмент фона; геометрический паттерн — кодом (SVG или CSS), а не генерацией. → `../07-vector-svg-icons/03-icon-sets-and-patterns.md` §4

**Подпись провенанса SVG** (provenance signature, `<recraft-signature>`) — встроенная в SVG подпись вендора (Ed25519); svgo по умолчанию её удаляет, условия Recraft запрещают — 2 переопределения пресета. → `../07-vector-svg-icons/02-vector-generators-and-tracing.md` §4

**Узнаваемость метафоры** (recognizability) — понятна ли новая метафора без подписи: геометрию LLM проходит, узнаются 2 из 5 — проверяет VLM или человек. → `../07-vector-svg-icons/01-svg-by-llm.md` §5

**`currentColor`** (currentColor) — ключевое слово CSS: иконка наследует цвет текста — перекраска и тёмная тема без копий файла; поставка набора — спрайт `<symbol>` + `<use>`. → `../07-vector-svg-icons/03-icon-sets-and-patterns.md` §3; `../07-vector-svg-icons/01-svg-by-llm.md` §6

**Lottie** (Lottie, dotLottie) — JSON-анимация вектора — только для сложного движения (персонаж, морфинг): плеер `lottie-web` light 46 КБ gzip, dotLottie с WASM ≈ 530 КБ gzip; «уменьшить движение» её не останавливает — нужен код. → `../07-vector-svg-icons/04-animated-vector.md` §1, §2

**SMIL** (SMIL animation) — анимация внутри SVG; как и `<img>`-SVG, не реагирует на `prefers-reduced-motion` — для доступности брать CSS-анимацию inline SVG. → `../07-vector-svg-icons/04-animated-vector.md` §2

**SVG кодом** (LLM-generated SVG) — линейную иконку пишет LLM по спецификации сетки (24, штрих 2, живая область) и проверяется кодом; знакомые метафоры брать из набора (9 из 20 ≈ Lucide, сходство ≥ 0,92). → `../07-vector-svg-icons/01-svg-by-llm.md` §1

## 6. Постобработка и кодирование

**Апскейл** (upscale) — увеличение разрешения: Lanczos по умолчанию; Real-ESRGAN хуже Lanczos против эталона и дорисовывает чужую структуру — только графика; генеративный (Topaz) — после теста H-05. → `../08-image-post-processing/02-upscale-outpaint-edit.md` §1.2, §1.3

**Аутпейнт** (outpainting; format family) — дорисовка кадра за границы под новое соотношение; семейство форматов (16:9 → 21:9, 4:5, 9:16) из одного мастера — кадрирование по фокусу или аутпейнт с композитом центра. → `../08-image-post-processing/02-upscale-outpaint-edit.md` §4.1, §4.2

**Бандинг** (banding; dithering; CAMBI) — видимые ступени плавного градиента; мера для видео — CAMBI; AV1 10 бит в браузере — не решение; дизеринг в файле не переживает кодек — шум накладывать после декодирования (CSS), Chromium сам добавляет его к CSS-градиентам. → `../08-image-post-processing/03-color-tiling-depth-layers.md` §3; `../09-video-pipeline/03-encoding-and-budgets.md` §8; `../10-web-integration/03-text-over-media-and-effects.md` §4.3

**Бесшовная текстура** (seamless / tileable texture; latent tiling) — картинка без шва при повторении; в моделях polza параметра tile нет — только постобработкой; латентный тайлинг — вне polza (fal Z-Image tiling, Midjourney `--tile`). → `../08-image-post-processing/03-color-tiling-depth-layers.md` §2.1

**Деспилл** (despill; key reflection) — подавление цветного отсвета ключа на краях объекта; рефлекс ключа на глянце despill не убирает. → `../09-video-pipeline/02-cinemagraph-alpha.md` §1.4

**Дрейф цвета** (global colour drift; colour shift) — общий сдвиг цвета кадра после правки моделью (ΔE00 3,3 при утечке в норме) — без подгонки вклейка оригинала даёт шов; порог ≤ 2. → `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.3

**Карта глубины** (depth map; disparity; AbsRel, δ1) — монокулярная модель (Depth Anything V2 Small, 518²) выдаёт диспаритет — обратную глубину с точностью до масштаба; точность против Blender — AbsRel и δ1 (max(ẑ/z, z/ẑ) < 1,25). → `../08-image-post-processing/03-color-tiling-depth-layers.md` §4.1

**Кеер** (keyer, `colorkey`, `chromakey`, `hsvkey`; keying tolerance margin) — фильтр, превращающий цвет ключа в прозрачность; параметры — по MAE альфы с despill; запас по `similarity` — диапазон, при котором объект не «съедается» (пурпурный прощает ошибку настройки). → `../09-video-pipeline/02-cinemagraph-alpha.md` §1.3, §1.2

**Композит оригинала** (original composite, `--composite`) — вставка исходных пикселей вне цели поверх правки или исходника в центр аутпейнта; товар — всегда композитом с фото. → `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.3, §4.3

**Композит товара** (product composite) — настоящий товар (вырез фото или рендера) вклеивается по альфе поверх ИИ-сцены: растушёвка 4 px, тень слоем multiply, проверка `edit_check.py --protect` (SSIM ≥ 0,9, ΔE00 ≤ 5; демо — 0,968 и 0,88); модели сохраняют товар без дефектов лишь в 53–75 % случаев. → `../14-recipes/02-series-product-recipes.md` §2.3; `../13-routing-matrix/03-routing-matrix.md` §2

**Маска правки** (edit mask; inpainting) — картинка, задающая область изменения; у GPT Image маска — «guidance», а не трафарет — сохранность вне маски не гарантирована. → `../05-prompting/05-edit-reference-series.md` §2.1; `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.5

**Матирование** (alpha / video matting) — оценка полупрозрачной альфы нейросетью (по тримапу или без ключа, покадрово для видео); уступает хромакею на стекле и волосах. → `../09-video-pipeline/02-cinemagraph-alpha.md` §2; `../08-image-post-processing/01-background-removal-matting.md` §3

**Мезонин** (mezzanine, lossless; lossless mezzanine) — промежуточный мастер без потерь (x264 `-qp 0` 4:4:4, PNG), из которого кодируются веб-версии и на котором меряют шов и `motion_keep`; CRF 10 — не мезонин: чистая петля 0,96 → 2,08 (X22). → `../09-video-pipeline/03-encoding-and-budgets.md` §3; `../09-video-pipeline/01-seamless-loops.md` §1.3

**Ореол** (halo, fringe; colour decontamination) — светлая или цветная кайма выреза на контрастном фоне, порог ≤ 2 px (`alpha_check.py halo`); деконтаминация удаляет цвет исходного фона из полупрозрачной каймы (rembg `-dc`). → `../08-image-post-processing/01-background-removal-matting.md` §5, §3.1

**Параллакс слоёв** (layer parallax; 2.5D; scroll-driven animation) — разная скорость слоёв при прокрутке — глубина без 3D; на странице — `animation-timeline: scroll()` без JS. → `../08-image-post-processing/03-color-tiling-depth-layers.md` §5; `../10-web-integration/03-text-over-media-and-effects.md` §4.4

**Перерисовка исходника** (regeneration, `REGENERATED`; edge sharpness) — модель при аутпейнте или правке заново рисует неизменяемую часть; ловит резкость краёв: аутпейнт PASS = SSIM центра ≥ 0,9 И ΔE00 ≤ 3 И резкость ≥ 0,85, иначе вставка исходника. → `../08-image-post-processing/02-upscale-outpaint-edit.md` §4.3

**Подгонка цвета** (colour matching, `--match-color`) — линейная коррекция правки по каналам на неизменной зоне до сравнения и композита; то же для правленого конечного кадра перед видео. → `../08-image-post-processing/03-color-tiling-depth-layers.md` §1.2; `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.3

**Полярность маски** (mask polarity) — какой цвет маски значит «менять»: `qwen/image-2.1` — белое, `openai/gpt-5-image` — чёрное; проверять `edit_check.py polarity`. → `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.5; `../05-prompting/05-edit-reference-series.md` §2.1

**«Призрак» удаления** (removal ghost; mask dilation, feathering) — видимый контур маски после композита: удалённый объект менял свет вокруг; маска удаления включает тень, расширение 8–10 % стороны, растушёвка ≈ 3 %. → `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.4

**Прозрачный фон** (transparent background; alpha channel) — PNG/WebP с альфа-каналом; нативно в polza — только `qwen/image-2.1` (`background: transparent`, 3 ₽, исследовательская лицензия — только черновики), GPT Image — через RouterAI; «нарисованная шахматка» вместо альфы ловит `alpha_check.py`. → `../08-image-post-processing/01-background-removal-matting.md` §4.1, §5

**Разложение на слои** (layer decomposition, `IMG-LAYERS`) — картинка → фон + RGBA-слои объектов (Gen-API `qwen-image-layered` 12,5 ₽, Seedream 5 Pro Layer Decomposition); локально — вырез по альфе + глубина. → `../08-image-post-processing/03-color-tiling-depth-layers.md` §5; `../13-routing-matrix/03-routing-matrix.md` §2

**«Резиновая плёнка»** (depth edge bleeding; flying pixels) — промежуточная глубина на разрывах — контур тянется в параллаксе; слои резать по альфе, а не по порогу глубины. → `../08-image-post-processing/03-color-tiling-depth-layers.md` §4.2

**Удаление фона** (background removal; cutout; ground-truth alpha) — вырез объекта в RGBA; универсальной локальной модели нет (isnet: мех IoU 0,00, стекло все делают непрозрачным) — инструмент по типу объекта; мерить против эталонной альфы рендера Blender: IoU ≥ 0,95 твёрдое, ≥ 0,85 мех. → `../08-image-post-processing/01-background-removal-matting.md` §1.2, §5

**Утечка правки** (edit leakage; over-editing) — изменения вне цели: доля пикселей с ΔE00 > 5 вне маски и полосы допуска, порог ≤ 0,02 (`edit_check.py check`); переправка — норма моделей: меняют в 50–1400 раз больше пикселей, чем нужно (PaintBench). → `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.2, §2.1

**Хромакей** (chroma key; key colour) — ровный фон для выреза по цвету (зелёный `#00B140`, синий, пурпурный); цвет ключа — далёкий по оттенку от объекта: `#FF00FF` для золотых и зелёных, `#00B140` для красных и фиолетовых; блестящее — на цвете сцены; лучший край и полупрозрачность стекла. → `../08-image-post-processing/01-background-removal-matting.md` §2.2; `../09-video-pipeline/02-cinemagraph-alpha.md` §1.1; `../14-recipes/01-hero-recipes.md` §3.2

**Чистая подложка** (clean plate) — тот же кадр без объекта (удаление по маске); эталон удаления объекта и нижний слой 2.5D. → `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.4

**Шов текстуры** (texture seam ratio, `tile_check.py`; minimum error boundary cut) — разрыв на стыке по кругу к типичной разнице соседних столбцов после сдвига на 50 %: ≤ 1,3 — бесшовно, > 1,5 — чинить разрезом минимальной ошибки (quilting) или заделкой маской. → `../08-image-post-processing/03-color-tiling-depth-layers.md` §2.2, §2.3

**CRF** (constant rate factor) — параметр качества видеокодека; для петли выбирать по `motion_keep` ≥ 0,75, а не по привычке: AV1 24–28, H.264 18–20. → `../10-web-integration/02-video-delivery.md` §6.1; `../09-video-pipeline/03-encoding-and-budgets.md` §2

**JPEG XL** (JPEG XL, JXL) — формат картинок; в Chrome по умолчанию с 155 (стабильный 06.10.2026) — первым необязательным `<source>` перед AVIF и WebP; до этого 0 % полной поддержки. → `../08-image-post-processing/04-encoding-metadata.md` §2; `../10-web-integration/01-images-delivery.md` §1.3

**SSIMULACRA2** (SSIMULACRA2) — перцептуальная метрика сжатия: 90 — визуально без потерь, 80 — очень высоко, 70 — высоко; hero ≥ 80, второстепенное ≥ 70 (`avif_pick.sh`). → `../08-image-post-processing/04-encoding-metadata.md` §1.2

## 7. Доставка на страницу

**Арт-дирекшн адаптивных картинок** (art direction, `<picture media>`) — разные кадры для разных экранов; `media` у `<source>` — только для арт-дирекшна, не смешивать с условиями в `sizes`. → `../10-web-integration/01-images-delivery.md` §2.2, §3.1

**Бюджет движения** (motion budget, WCAG 2.2.2; pause control) — автодвижение ≤ 5 с без паузы или дольше — с видимой кнопкой (доступное имя, `aria-pressed`), останавливающей всё движение; бесконечная петля любой длины — пауза или стоп ≤ 5 с; проверяется поведением на 6-й секунде. → `../10-web-integration/02-video-delivery.md` §5, §5.1; `../10-web-integration/04-budgets-and-acceptance.md` §3.2

**Видео с альфой** (alpha video: VP9-alpha, HEVC-alpha, stacked alpha) — объект с прозрачностью поверх вёрстки: VP9-alpha (WebM `yuva420p`, Chromium), HEVC-alpha (Safari), stacked alpha — везде через WebGL2. → `../10-web-integration/02-video-delivery.md` §7.1

**Запасной источник** (fallback `<source>`) — второй формат для браузеров без поддержки первого: AV1 10 бит → H.264; для альфы — HEVC-alpha или stacked, не GIF. → `../10-web-integration/02-video-delivery.md` §1.2

**Кандидат LCP** (LCP candidate) — элемент, который может стать LCP: `<img>`, `<image>`, `<video>` (постер или первый кадр — что раньше), фон `url()`, блочный текст; `<canvas>` — нет. → `../10-web-integration/01-images-delivery.md` §4

**Картинка «на весь вьюпорт»** (viewport-covering image; effective visual size; viewport rule) — картинка, видимая часть которой ≥ площади вьюпорта: Chromium её в LCP не учитывает — LCP станет H1 (правило вьюпорта выполняется 12 из 12 живых hero, поправка X17); эффективная площадь уменьшается и при апскейле до натуральной. → `../10-web-integration/01-images-delivery.md` §4.1; `../CONTRADICTIONS.md`

**Карточка ссылки** (link preview; `og:image`; OG safe zone) — картинка превью в соцсетях и мессенджерах: 1200×630, PNG или JPEG ≤ 300 КБ, AVIF не ставить; ключевое — в безопасной зоне 1100×530 (X режет до 2:1); текст — HTML-шаблоном и рендером Playwright, не генерацией. → `../10-web-integration/01-images-delivery.md` §7; `../01-web-assets-landscape/01-asset-slots-by-page-type.md` §2.7; `../14-recipes/03-vector-text-og-recipes.md` §4.4

**Первый экран** (above the fold) — область страницы без прокрутки; бюджет ≤ 2,5 МБ десктоп и ≤ 1,5 МБ телефон вместе с автостартующим видео (медиана лидеров 4,2 МБ). → `../10-web-integration/04-budgets-and-acceptance.md` §1.1, §1.2

**Переотдача пикселей** (pixel over-delivery) — натуральная ширина файла / (CSS-ширина × DPR); > 1 — лишние пиксели, > 2 — WARN приёмки страницы. → `../10-web-integration/01-images-delivery.md` §2.1; `../10-web-integration/04-budgets-and-acceptance.md` §3.2

**Постер** (poster frame; video layer over poster) — кадр 0 финального видео, отданный картинкой (PNG ffmpeg → Pillow → AVIF) — кандидат LCP; `<video>` — слоем поверх `<picture>`-постера, включается после `load` по первому показанному кадру; гладкий постер ниже 0,05 бит/px выпадает из кандидатов — LCP становится видео-слой (демо: AVIF 3,2 КБ, LCP 204 мс; при reduce — H1); кодировать `avif_pick.sh 80`. → `../10-web-integration/02-video-delivery.md` §2.2, §3.1; `../09-video-pipeline/03-encoding-and-budgets.md` §5; `../14-recipes/01-hero-recipes.md` §1.5

**Приёмка страницы** (page acceptance, `page_accept.py`) — автоматическая проверка собранной страницы: вес по CDP, LCP, CLS, `alt` и размеры, переотдача, атрибуты видео, пауза, reduce, F83 по буквам и кадрам; код выхода 1 при провале; троттлинг DevTools режет каждый запрос отдельно — приоритеты так не проверить. → `../10-web-integration/04-budgets-and-acceptance.md` §3, §5

**Приоритет и ленивая загрузка** (`fetchpriority`; `loading="lazy"`; `sizes="auto"`) — `fetchpriority="high"` — на 1–2 картинки, претендующие на LCP; `loading="lazy"` на LCP-картинке — антипаттерн; у ленивых картинок `sizes="auto"` — ширину берёт браузер. → `../10-web-integration/01-images-delivery.md` §4.4, §2.3

**Прожектор** (spotlight mask reveal) — верхний слой под `mask-image: radial-gradient` за курсором открывает второе состояние сцены (две петли). → `../10-web-integration/03-text-over-media-and-effects.md` §4.1; `../10-web-integration/02-video-delivery.md` §8

**Серый оверлей 4:0:0** (grayscale AVIF overlay, `avifenc -y 400`) — фактура без цвета: монохромный AVIF-тайл поверх цвета секции в `mix-blend-mode: multiply`, цвет задаёт CSS; мешковина 256 px — 9,8 КБ против 49,6 КБ цветного WebP (бюджет ≤ 30 КБ). → `../14-recipes/03-vector-text-og-recipes.md` §3.4

**Скрим** (scrim; text-axis scrim) — затемняющий или осветляющий градиент под текстом вдоль оси колонки (горизонтальный на десктопе, сверху вниз на телефоне); порядок: спокойная зона → цвет текста → скрим; альфа > 0,55 — «серая коробка». → `../06-art-direction-consistency/03-composition-for-web.md` §2.5; `../10-web-integration/03-text-over-media-and-effects.md` §2.2

**Слой тени** (shadow layer, multiply) — отношение «кадр / чистая подложка» вне объекта, накладывается умножением — тень объекта на любом цвете секции; 3D-иконка на цвете секции без альфы легче в 2,3–4,7 раза. → `../10-web-integration/03-text-over-media-and-effects.md` §4.5; `../14-recipes/02-series-product-recipes.md` §4.3

**Сохранение движения** (`motion_keep`, motion retention; in-mask motion keep, `keep_in`) — `motion_med` финала / мезонина; < 0,75 — кодек «заморозил» петлю; CRF выбирать по нему (AV1 CRF 36 тихих петель — 0,24–0,77); `keep_in` — то же внутри маски движения синемаграфа (AV1 CRF 36 — 0,84). → `../10-web-integration/02-video-delivery.md` §6.1; `../14-recipes/01-hero-recipes.md` §4.4

**Теги цвета** (colour description: primaries, transfer, matrix, range; cICP) — метаданные видео о пространстве цвета (BT.709, `setparams=…`); без них браузер угадывает матрицу — ошибка BT.601/709 сдвигает насыщенные цвета на ΔE00 ≈ 7–8 и даёт скачок постер → видео; у PNG — чанк cICP. → `../10-web-integration/02-video-delivery.md` §2.1, §2.2

**Телефонный мастер** (phone master frame; hero pair) — отдельный кадр 4:5–9:16 со своей зоной текста, а не обрезка десктопного (из 16:9 в 9:16 остаётся 31,6 % ширины); hero-пара — два мастера, 16:9 и телефонный (у Sunburst в polza нет 4:5 → 3:4 с кропом). → `../10-web-integration/01-images-delivery.md` §3; `../06-art-direction-consistency/03-composition-for-web.md` §3.4; `../14-recipes/01-hero-recipes.md` §1.1

**Уменьшение движения** (`prefers-reduced-motion: reduce`; idle motion) — системная настройка: видео не грузить (0 байт `media`), показать постер, остановить CSS-анимации; движение в покое при reduce — < 0,5 % пикселей первого экрана за 1 с. → `../10-web-integration/02-video-delivery.md` §4.1; `../10-web-integration/04-budgets-and-acceptance.md` §3.2

**Энтропия картинки для LCP** (LCP image entropy, bpp) — байты файла × 8 / отображаемая площадь; < 0,05 — не кандидат LCP (Chromium 112+): гладкий ИИ-фон или постер может «выпасть». → `../10-web-integration/01-images-delivery.md` §4.2

**F83** (WCAG 2.2 failure technique F83; per-glyph, per-frame contrast) — контраст текста к худшему участку фона за каждой буквой (маска букв — двойным снимком: с текстом и с прозрачным текстом), у видео — худший кадр; соответствие — по F83, плотность скрима — по p99,9 яркости полосы текста (среднее даёт 17 ложных «проходит» из 31). → `../06-art-direction-consistency/03-composition-for-web.md` §2.3; `../10-web-integration/03-text-over-media-and-effects.md` §1.1, §1.2

**LCP** (Largest Contentful Paint) — время отрисовки крупнейшего элемента первого экрана; норма ≤ 2,5 с на p75 поля; кто станет LCP (картинка или H1) — решать заранее. → `../10-web-integration/01-images-delivery.md` §4; `../10-web-integration/04-budgets-and-acceptance.md` §2

**LQIP** (low-quality image placeholder; thumbhash) — средний цвет или 32-px картинка до прихода файла; LCP не «крадёт». → `../10-web-integration/01-images-delivery.md` §5

**Stacked alpha** (stacked alpha video; premultiplied alpha) — видео двойной высоты: сверху цвет, снизу альфа, сборка шейдером WebGL2 с премультиплицированной альфой (цвет заранее умножен на альфу); 460 КБ против 1,1 МБ VP9 и 3,4 МБ HEVC (Archibald). → `../10-web-integration/02-video-delivery.md` §7, §7.2; `../09-video-pipeline/02-cinemagraph-alpha.md` §4

## 8. Оценка и приёмка

**Арена** (image / video arena, AA, LMArena; leaderboard category; style control) — рейтинг по слепым попарным голосам (Elo / Брэдли–Терри) на английских промтах в настройках вендора — «что красивее», а не пригодность; срезы (Text Rendering, UI/UX …) меняют лидера; контроль стиля поправляет рейтинг на длину и насыщенность. → `../03-image-models/01-landscape-and-benchmarks.md` §2, §2.3; `../04-video-models/01-landscape-and-benchmarks.md` §2.2

**«Где» маркера** (grounding location) — место дефекта в кадре; без него ответ «да» в режиме `defects` не засчитывается. → `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §2.2

**Дословность** (verbatim accuracy) — совпадение строки с эталоном по кодовым точкам после нормализации; фильтр до голосования для задач с текстом. → `../13-routing-matrix/01-stand-method.md` §6.2; `../11-evaluation-qa/01-metrics-and-asset-audit.md` §4.2

**Калибровка судьи** (judge calibration; trust threshold; acceptance log) — сверка VLM со слепыми голосами заказчика по журналу приёмки (JSONL решений человека), ≥ 20 решающих голосов на пару; доверие ≥ 0,8 при нижней границе Уилсона ≥ 0,65 — сортировать best-of-N, 0,7–0,8 — только отсев брака, < 0,7 — не использовать. → `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §6; `../11-evaluation-qa/03-checklists-by-asset.md` §5

**Класс доказательств** (evidence class A / B / C) — A — независимые голоса или метрика с методикой на моделях 09.2026; B — методика есть, но один судья, старые версии или малая выборка; C — анекдот. → `../13-routing-matrix/02-existing-evidence.md` §3; `../13-routing-matrix/03-routing-matrix.md` §1

**Контактный лист** (contact sheet; corners sheet) — сетка кадров или вариантов в одной картинке для проверки глазами: 4 кадра страницы, «последний | первый | |Δ|×4» петли; лист углов — кропы 4 углов для поиска видимой метки генератора. → `../09-video-pipeline/01-seamless-loops.md` §5; `../01-web-assets-landscape/02-live-sites-measured.md` §1; `../11-evaluation-qa/01-metrics-and-asset-audit.md` §3.1

**Латинские двойники** (Latin homoglyph; near-homoglyph; non-homoglyph substitute) — двойник — буква, совпадающая начертанием с кириллической (A/А, P/Р), нужна сверка кодовых точек; «близнец» — почти неотличимая (u/и, n/п, r/г), OCR не видит; недвойник — явная замена (N вместо И, R вместо Я). → `../11-evaluation-qa/01-metrics-and-asset-audit.md` §4.3; `../13-routing-matrix/01-stand-method.md` §6.2

**«Латинский нюх»** (Latin sniff; OCR language-prior autocorrection) — второй, английский распознаватель по той же строке — ловит D, R, g вместо Д, Я, д: основной русский OCR по языковой «догадке» читает видимую латиницу как кириллицу. → `../11-evaluation-qa/01-metrics-and-asset-audit.md` §4.2, §4.3

**Локальный сдвиг** (local shift, `QA-EDIT-LOCAL-SHIFT`; difference-derived mask) — связная область вне цели (≥ 1 % площади), изменённая на ΔE00 > 3 после подгонки цвета; у безмасочной правки цель берут из маски разницы (ΔE00 + морфология, расширение 2 % стороны); вердикт утечки — по прогону без подгонки и по этому коду: глобальная подгонка растворяет утечку (LEAK 0,131 → PASS 0,0001, X23). → `../11-evaluation-qa/01-metrics-and-asset-audit.md` §3.3

**Метрики соответствия тексту** (CLIPScore, VQAScore, FID) — CLIPScore — «мешок слов», r с людьми 0,39–0,59; VQAScore — P(«да») VQA-модели, смещение к «да», попарная точность ≈ 63 %; FID — распределительная, чувствительна к JPEG; судьёй не использовать. → `../11-evaluation-qa/01-metrics-and-asset-audit.md` §1; `../13-routing-matrix/01-stand-method.md` §4.1; `../05-prompting/02-structured-json-prompting.md` §5

**Метрики сходства** (SSIM, PSNR, LPIPS, DINO, DreamSim, CSD) — SSIM и PSNR — для сохранности, шва и кодирования, но не для качества ИИ-картинки (по DreamSim ≈ случай); LPIPS — сохранность правки; CSD — стиль, DINOv2 — продукт по вырезке. → `../06-art-direction-consistency/02-series-and-consistency.md` §6.3; `../13-routing-matrix/02-existing-evidence.md` §2

**Модель Брэдли–Терри** (Bradley–Terry model; Elo; Wilson score interval) — рейтинг по попарным исходам (ничья = 0,5 победы) с интервалами — разброс мест; для доли побед при малом числе голосов — интервал Уилсона (14 из 20 = [0,48; 0,86]). → `../13-routing-matrix/01-stand-method.md` §4.4; `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §6.3

**Незаказанный текст** (unrequested text; pseudo-text) — надпись на картинке, которой нет в брифе (≥ 2 букв с уверенностью OCR ≥ 0,6). → `../11-evaluation-qa/01-metrics-and-asset-audit.md` §4.4

**Одинаковое кодирование** (encoding parity; compression bias) — варианты пары показываются судье и людям в одном формате и качестве: иначе выбирают по артефактам сжатия, а не по содержанию (`judge-jobs --same-encoding`). → `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §2.3

**Позиционный сдвиг** (position bias; swap consistency) — перевес выборов левой (или правой) стороны: доля «A» вне 0,35–0,65 — судья смещён; стороны случайны, 10 % повторов со сменой, согласованность повторов ≥ 0,8. → `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §2.3; `../13-routing-matrix/01-stand-method.md` §4.3

**Попарное сравнение** (pairwise preference) — выбор лучшего из двух вместо баллов (A / B / ничья / оба не годятся); устойчивее абсолютной шкалы (Google, Character.ai); измеряемое — метриками, эстетику — люди. → `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §2.3; `../13-routing-matrix/01-stand-method.md` §4.3

**Приёмка ассета** (asset acceptance / audit, `asset_audit.py`; verdict; defect code) — автоматическая и ручная проверка до публикации; режимы `image`, `cutout`, `edit`, `texture`, `series`, `video-loop`, `video-alpha`, `svg-icon`, `og`; вердикт pass / warn / needs_human / fail; дефекты — коды `QA-*` с порогом из `thresholds.yaml`. → `../11-evaluation-qa/01-metrics-and-asset-audit.md` §2, §5

**Профильный бенчмарк** (task-specific benchmark; benchmark saturation) — замер под конкретную задачу (правка, текст, цвет, вырез), а не общий Elo; академические таблицы часто насыщены (GenEval: топ ≥ 0,84, люди ставят ≥ 94,8 %). → `../13-routing-matrix/02-existing-evidence.md` §2.1; `../03-image-models/01-landscape-and-benchmarks.md` §4.1

**Рубрика** (rubric, `*.rubric.json`) — проверки, вопросы судьи, запреты и чек-лист человека для типа ассета; 12 рубрик в `11-evaluation-qa/rubrics/`. → `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §4

**Слой текста** (text layer render) — второй рендер HTML-шаблона со скрытым товаром или фото (`visibility:hidden`) — вход OCR без склейки строк с этикеткой: 7 из 7 строк, CER 0 против «ИСНЯ ОБЖА» на полном кадре. → `../14-recipes/03-vector-text-og-recipes.md` §6.1, §6.2

**Сохранность вне цели** (outside-target preservation) — неизменность пикселей вне маски правки (ΔE00, SSIM); «пиксельно точной» правки у моделей нет — проверять всегда. → `../08-image-post-processing/02-upscale-outpaint-edit.md` §2.1; `../13-routing-matrix/01-stand-method.md` §4.1

**Сфабрикованные негативы** (manufactured negatives) — заведомо испорченные образцы (разрыв, стоп-кадр, угасание, склейка, ползущая камера) для проверки метрик и судьи; метрики видео ловят 12 из 12. → `../11-evaluation-qa/01-metrics-and-asset-audit.md` §3.6

**Цветность** (colorfulness, Hasler–Süsstrunk) — метрика насыщенности и разнообразия цвета кадра; Q3 фото лидеров 54,5; «Instagram-фильтр» удваивает её. → `../01-web-assets-landscape/03-ai-fit-trust-and-slop.md` §6.1; `../06-art-direction-consistency/04-slop-and-color-harmony.md` §2.1

**DOM-проверка вёрстки** (DOM layout check, `layout_check.py`; nowrap flex item) — Playwright-проверка шаблона до OCR: пересечение строк с альфой товара, переполнение, `nowrap`-элемент прямым потомком флекс-контейнера (становится отдельным элементом с `gap` и не сжимается); вёрстку проверяет DOM, буквы — OCR по слою текста. → `../14-recipes/03-vector-text-og-recipes.md` §6.3, §6.1

**DSG** (Davidsonian Scene Graph; atomic question) — атомарные вопросы да/нет об одном признаке одного объекта с зависимостями: «нет» у родителя обнуляет дочерние; текст VQA-судья проверяет плохо (13,7 %) — только OCR. → `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §2.1

**GNED** (Global Normalized Edit Distance, TIIF-Bench) — нормированное расстояние правки строк текста на картинке с сопоставлением слов по Венгерскому алгоритму и штрафом за лишние; согласие с людьми 99 % против 83 % у OCR Recall. → `../05-prompting/02-structured-json-prompting.md` §5; `../11-evaluation-qa/01-metrics-and-asset-audit.md` §4.2

**VLM-судья** (VLM-as-a-judge; VLM critic; autorater; decide-only) — мультимодальная модель отвечает на вопросы рубрики (режимы `checklist`, `defects`, `pairwise`, `transcribe`), формат — «сразу вердикт» без рассуждения; допустим для пунктов брифа и крупных маркеров после калибровки; не для эстетики, точного цвета и артефактов видео (48,6 % против 86,4 % у людей). → `../11-evaluation-qa/02-vlm-critic-and-rubrics.md` §1, §2, §3

## 9. Право и маркировка

**Видимая метка** (disclosure, label; EU AI icon) — понятная человеку метка при первом показе; официальная иконка ЕС «AI», «AI GENERATED», «AI MODIFIED» + раскрываемый второй слой (что сгенерировано или изменено); раскрытие снижает доверие к рекламе — ставить, где обязательно. → `../12-legal-provenance/04-agent-policy.md` §3.1; `../12-legal-provenance/02-labeling-ai-act-provenance.md` §3.3, §7.1

**Видимый водяной знак** (visible watermark; copyright management information) — надпись от генератора на картинке: «AI-generated» справа внизу у Seedream в прямом API BytePlus (`watermark: true` по умолчанию), через `mie` — нет (тест E-01); чужие водяные знаки и сведения об авторе с референсов не удалять (ГК ст. 1300). → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §4.1; `../12-legal-provenance/03-people-brands-styles-russia.md` §6.3

**Ворота перед публикацией** (pre-publication gates) — вопросы L, без ответа на которые ассет не выходит: люди, чужие знаки, метки, лицензия, правдивость товара. → `../12-legal-provenance/04-agent-policy.md` §5

**Деплоер** (deployer, AI Act ст. 3(4)) — использует ИИ-систему под своей властью в профессиональной деятельности; отвечает за видимое раскрытие дипфейков (ст. 50(4)); система заказчика — и провайдер, и деплоер, клиент, лишь заказавший сайт, — не деплоер. → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §1.2

**Дипфейк** (deep fake, AI Act ст. 3(60)) — ИИ-изображение, видео или аудио, похожее на существующих людей, объекты, места, события и способное сойти за подлинное; раскрывать видимо. → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §2

**Изменённое изображение недвижимости** (digitally altered image, CA AB 723) — рекламное фото недвижимости, где редактор или ИИ добавил, убрал, изменил мебель, стены, вид из окна; в Калифорнии с 01.01.2026 — заметная пометка рядом и ссылка на оригинал. → `../12-legal-provenance/03-people-brands-styles-russia.md` §3

**Изображение гражданина** (image of a citizen, ГК РФ ст. 152.1) — фото, видео, рисунок человека; использование — с его согласия, в том числе узнаваемого сгенерированного двойника. → `../12-legal-provenance/03-people-brands-styles-russia.md` §1.1

**Индемнификация** (indemnification) — обязательство вендора защищать клиента от исков по интеллектуальной собственности (OpenAI, Google Cloud для GA-моделей); через polza, RouterAI, Gen-API до нас не доходит. → `../12-legal-provenance/01-licenses-by-vendor-and-channel.md` §7

**Исследовательская лицензия** (research license, Qwen Research License) — веса «только для исследований и оценки»; Qwen Image 2.1 через `mie` — только черновики, не финал (`final: false`). → `../12-legal-provenance/01-licenses-by-vendor-and-channel.md` §5

**Кодекс практики** (Code of Practice on Transparency of AI-generated Content) — добровольный кодекс ЕС (10.06.2026), признанный адекватным способом соблюдения ст. 50(2), 50(4), 50(5); ≈ 190 подписантов. → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §3

**Лицензии открытых весов** (non-commercial, territory-restricted, revenue-threshold licenses) — некоммерческая (FLUX NCL, CC BY-NC) — запрет ради выручки; территориальная (Tencent Hunyuan, MiniMax) — не действует в перечисленных странах; пороговая (LTX) — бесплатна до $10 млн выручки; права задаёт LICENSE, а не теги Hugging Face. → `../12-legal-provenance/01-licenses-by-vendor-and-channel.md` §4; `../02-providers-platforms/05-open-weights-landscape.md` §9

**Машиночитаемая маркировка** (machine-readable marking; non-removal) — метка в файле или пикселях, которую находит программа; Кодекс требует ≥ 2 слоёв (подписанные метаданные + невидимый водяной знак) и неудаления меток; ст. 50(2) — с 02.08.2026, для систем, выпущенных раньше, — до 02.12.2026. → `../12-legal-provenance/04-agent-policy.md` §3.2; `../12-legal-provenance/02-labeling-ai-act-provenance.md` §1.1, §3.1

**Метка AIGC** (implicit / explicit AIGC label, GB 45438-2025) — китайская неявная метка в метаданных (Label, ContentProducer, ProduceID; в MP4 Seedance, Kling, MiniMax) и явная видимая по мерам CAC; теряется при любом ffmpeg без `-map_metadata 0 -movflags use_metadata_tags` — в видео сохранять. → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §6

**Невидимый водяной знак** (imperceptible watermark, SynthID, Content Seal) — метка в пикселях или сэмплах, переживающая сжатие; SynthID ставит Google во все выходы, OpenAI с 19.05.2026 — C2PA + SynthID; в списке soft-binding C2PA SynthID нет. → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §4.1

**Отзыв-свидетельство** (testimonial, 16 CFR 465) — рекламное сообщение с именем, подписью или обликом человека о его опыте; ИИ-отзывы запрещены FTC — не генерировать никогда. → `../12-legal-provenance/03-people-brands-styles-russia.md` §1.3

**Привязка манифеста** (hard binding; soft binding) — жёсткая — хэш байтов в манифесте, ломается при любом перекодировании; мягкая — водяной знак или отпечаток, находящий манифест после перекодирования (в списке C2PA 28 алгоритмов). → `../08-image-post-processing/04-encoding-metadata.md` §4.1

**Провайдер ИИ-системы** (provider, AI Act ст. 3(3)) — разрабатывает ИИ-систему и вводит в эксплуатацию под своим именем, в том числе для себя; отвечает за машиночитаемую метку (ст. 50(2)); система генеративного дизайна заказчика — провайдер. → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §1.2

**Проверка сходства** (likeness / IP clearance check) — поиск сходства лиц, логотипов, персонажей с защищёнными перед публикацией; модель может подставить лицо знаменитости по рекламе товара. → `../12-legal-provenance/03-people-brands-styles-russia.md` §1.2; `../12-legal-provenance/04-agent-policy.md` §5

**Синтетический исполнитель** (synthetic performer, NY GBL § 396-b) — цифровой человек в рекламе, не узнаваемый как реальное лицо; в Нью-Йорке с 09.06.2026 требует раскрытия. → `../12-legal-provenance/03-people-brands-styles-russia.md` §1.3

**Стандартная правка** (standard editing) — сжатие, кроп, цвет, ресайз, вырез фона — подготовка без создания нового; не маркируется. → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §1.3

**Трансграничная передача ПДн** (cross-border transfer, 152-ФЗ ст. 12) — передача фото клиента с лицом в зарубежный сервис — персональные данные; до начала — уведомление РКН. → `../12-legal-provenance/03-people-brands-styles-russia.md` §2

**Цепочка прав** (chain of title) — договоры от вендора через канал до владельца сайта, по которым передаются права на выход; рвётся у посредников без явной передачи. → `../12-legal-provenance/01-licenses-by-vendor-and-channel.md` §1.1

**C2PA** (Content Credentials; manifest store; ingredient) — подписанный манифест происхождения внутри файла (ингредиенты — исходные файлы производной); теряется при любом перекодировании, правка одного поля XMP ломает подпись; переподписанный манифест — 57–116 КБ (74–95 % файла). → `../08-image-post-processing/04-encoding-metadata.md` §4; `../12-legal-provenance/02-labeling-ai-act-provenance.md` §4

**Digital Source Type** (IPTC Digital Source Type; derivative provenance) — поле происхождения XMP: `trainedAlgorithmicMedia` — создано ИИ, `compositeWithTrainedAlgorithmicMedia` — композит; провенанс производной — это поле на каждом закодированном файле (+1–3 КБ), ставит `provenance_check.py stamp`; C2PA мастера переживает только побайтное хранение. → `../08-image-post-processing/04-encoding-metadata.md` §3; `../12-legal-provenance/02-labeling-ai-act-provenance.md` §5.2; `../14-recipes/01-hero-recipes.md` §0.3

**Sidecar-манифест** (sidecar manifest, `.c2pa`) — манифест C2PA в отдельном файле рядом с картинкой; позиция базы: мастер хранить с подписью, производные — лёгкие с XMP-DST или sidecar. → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §5.1; `../08-image-post-processing/04-encoding-metadata.md` §4.3

**«Valid» и «Trusted»** (validation state; C2PA Trust List) — подпись цела / подпись цела и подписант в списке доверия C2PA (30 корней на 23.09.2026). → `../12-legal-provenance/02-labeling-ai-act-provenance.md` §4.4

**243-ФЗ** (Russian AI law, 26.07.2026; large foundation model) — закон «О поддержке развития технологий ИИ» в силе с 01.09.2026 (большая фундаментальная модель — ≥ 1 млрд параметров); обязательной маркировки ИИ-картинок на сайтах на 23.09.2026 нет, ст. 9 и 10 — с 01.03.2027. → `../12-legal-provenance/03-people-brands-styles-russia.md` §7

## 10. Провайдеры, каналы и деньги

**Агрегатор** (aggregator; reseller storefront) — сервис, продающий доступ к чужим моделям за рубли (polza, Gen-API); витрина — клон каталога OpenRouter (RouterAI, AITUNNEL, ProxyAPI). → `../02-providers-platforms/03-aggregators-and-platforms.md` §2

**Асинхронный режим и опрос** (async mode; polling; webhook) — создание возвращает id, результат — опросом `GET /v1/media/{id}` (3–5 с картинки, 5–10 с видео); синхронно отвечают картинки RouterAI и Gen-API `is_sync`; вебхук требует публичного HTTPS — в конвейере не используется. → `../02-providers-platforms/01-polza-api.md` §3.2; `../02-providers-platforms/07-multichannel-client.md` §1

**Верхняя оценка** (upper-bound estimate; auto cap; key spend limit) — худшая документированная цена задания — по ней проверяются лимиты `max_rub`, `max_tokens` клиент выводит из `max_rub`; второй предохранитель — лимит ключа за день, неделю, месяц. → `../02-providers-platforms/07-multichannel-client.md` §4.2; `../02-providers-platforms/01-polza-api.md` §8.4

**Двусмысленный сбой** (ambiguous failure; idempotency) — обрыв после отправки POST: списание неизвестно, повтор запрещён — сверка с историей генераций; ключа идемпотентности у polza нет. → `../02-providers-platforms/07-multichannel-client.md` §7.2; `../02-providers-platforms/01-polza-api.md` §9.3

**Единица цены** (per-second, token, megapixel pricing) — видео — ставка за секунду (`unitParam: duration`, `video_per_second`) × длительность; картинки OpenAI и Google — выходные токены (сетка качества GPT Image 16/24/48/64/96 патчей); FLUX.2 — площадь (1 Мп = 1024²). → `../02-providers-platforms/02-polza-models-params-prices.md` §2.3, §2.4, §2.5; `../02-providers-platforms/07-multichannel-client.md` §4.1

**Журнал затрат** (spend ledger) — append-only JSONL событий трат по `uid`, общий для клиентов; по нему считаются бюджеты каналов. → `../02-providers-platforms/01-polza-api.md` §12.5; `../02-providers-platforms/07-multichannel-client.md` §4.3

**Запасная ступень** (fallback tier, `[]`) — ступень без условий, берётся, если параметры не совпали; часто максимум: Seedance 2 «только промт» = 415 ₽. → `../02-providers-platforms/02-polza-models-params-prices.md` §2.9

**Зонд** (probe) — минимальный запрос, отвечающий на вопрос протокола (часто 0 ₽ через ответ 400); зонды B2 идут первыми в фазе 5. → `../02-providers-platforms/07-multichannel-client.md` §5

**Исполнитель** (upstream provider, `mie` ≈ KIE.ai) — сервис, реально генерирующий за агрегатором; у polza `mie` ≈ KIE.ai с наценкой 1,6–1,8× (37 из 44 медиа-моделей). → `../02-providers-platforms/03-aggregators-and-platforms.md` §1.2; `../02-providers-platforms/01-polza-api.md` §11.3

**Канал** (channel) — путь к модели с отдельным балансом и форматом заданий: polza Media API, `polza-chat`, `polza-images`, RouterAI, Gen-API; клиенты — `polza.py` и `mp_client.py`. → `../02-providers-platforms/07-multichannel-client.md` §1

**Конфигурация канала** (channel / provider configuration) — параметры, которые канал реально выставляет (у GPT Image 2.5 в polza нет `quality` и `background`); модели мерить и сравнивать в ней, а не в настройках вендора. → `../13-routing-matrix/03-routing-matrix.md` §1; `../02-providers-platforms/04-direct-apis-and-services.md` §2.2

**Макет сервера** (mock server; mock channel) — локальный HTTP-сервер, повторяющий API канала по документации, для проверки клиента без денег: `polza.py` 30/30, `mp_client.py` 44/44 (41/44 на снимке 24.09 — ожидания закреплены на ценах 23.09). → `../02-providers-platforms/01-polza-api.md` §12; `../02-providers-platforms/07-multichannel-client.md` §7.5

**Маршрутизация провайдера** (provider routing, объект `provider`; model alias) — выбор исполнителя полями `only`, `order`, `allow_fallbacks`; для медиа в polza не проверено — тест фазы 0; алиасы `model@key=value` работают только для chat, responses, messages. → `../02-providers-platforms/01-polza-api.md` §10.2, §10.1

**Паспорт генерации** (generation passport) — JSON рядом с файлом: запрос, ответ, ступень цены, `usage.cost_rub`, провайдер, время, sha256; по L — ещё промт, входы, права, метки, решение. → `../02-providers-platforms/01-polza-api.md` §12.5; `../12-legal-provenance/04-agent-policy.md` §4

**Перевод входа** (input translation, `translate_input`) — платный перевод текстовых параметров Gen-API моделью GPT-4.1; выключать — промт уже на нужном языке. → `../02-providers-platforms/07-multichannel-client.md` §3.3

**Плоский тариф** (flat rate) — одна цена при любом разрешении или длительности; polza берёт цену максимума (Wan 3.0 — 118 ₽ за 5 с против 33,7 ₽ у ProxyAPI). → `../02-providers-platforms/03-aggregators-and-platforms.md` §1.5

**Резерв** (reserved amount; reservation) — сумма, удерживаемая на время генерации: у polza на сервере (`reservedAmount`), в клиенте `mp_client.py` — оценка в бюджете до конечного события. → `../02-providers-platforms/01-polza-api.md` §8.3; `../02-providers-platforms/07-multichannel-client.md` §4.2

**Сквозной параметр** (passthrough parameter) — параметр вендора, который канал передаёт без изменений (`provider.options.<slug>` у OpenRouter-витрин); до зондов B2 не полагаться. → `../02-providers-platforms/07-multichannel-client.md` §1.1

**Срок жизни результата** (storage policy; result TTL) — polza хранит результат 7 дней (`TEMP_GENERATION`; загрузки `TEMP_UPLOAD` — 24 ч), Gen-API — 24 ч; скачивать сразу и класть в кэш по хэшу. → `../02-providers-platforms/01-polza-api.md` §6, §7

**Ступень цены** (pricing tier, `tiers[].conditions`) — строка тарифа каталога с условиями `ключ=значение` и ценой; ценовые параметры задавать явно. → `../02-providers-platforms/02-polza-models-params-prices.md` §2.2

**Сухой прогон** (dry run) — печать точного запроса, цены и лимитов без отправки — режим `polza.py` и `mp_client.py` по умолчанию; `--live` — только в фазе 5. → `../02-providers-platforms/01-polza-api.md` §12.3; `../02-providers-platforms/07-multichannel-client.md` §2.3

**Хэш запроса** (request hash) — sha256 канонического тела (файлы — по sha256 содержимого) — ключ кэша; новый `variant` — новый хэш без `--force`. → `../02-providers-platforms/01-polza-api.md` §12.2; `../02-providers-platforms/07-multichannel-client.md` §4.4

**Ценовой параметр** (price-affecting parameter) — параметр, от которого зависит ступень: разрешение, длительность, режим, звук, число картинок, видео-референс; всегда явно. → `../02-providers-platforms/01-polza-api.md` §8.2

**Эффективный курс** (effective FX rate) — ₽ за $ исходной цены: polza — 117,992; `mie` ≈ 150 ₽ к цене KIE (кредит KIE — $0,005); курс ЦБ 23.09.2026 — 84,0657. → `../02-providers-platforms/03-aggregators-and-platforms.md` §4.1; `../02-providers-platforms/01-polza-api.md` §8.7

**Content-эндпоинт** (content endpoint; unsigned URL) — адрес скачивания результата у самого канала (видео RouterAI) — ссылка без подписи, скачивать с ключом только на домен канала. → `../02-providers-platforms/07-multichannel-client.md` §1.2

## 11. Маршрутизация, стенд и обновление

**Атлас инструментов** (tools atlas; liveness) — справочник моделей, каналов, сервисов, утилит с версиями, лицензиями и «живостью» — активен ли сервис и до какой даты. → `../15-tools-atlas/01-models-and-providers.md` §1; `../15-tools-atlas/02-tools-libraries-cli.md` §1

**Валидатор маршрутов** (routing validator, `routing_check.py`) — сверка `routing.yaml` с каталогами, диалектами, рубриками и заданиями; 0 ошибок — условие правки маршрута. → `../13-routing-matrix/04-update-procedure.md` §2, §2.1

**Вариант маршрута** (route option; role; `final`; license flag) — модель или инструмент с ролью (`primary`, `alt`, `fallback`, `cheap`/`draft`, `premium`, `local`/`code`/`blender`), условиями и флагами лицензии (`research`, `nc-weights`, `no-automation`, `visible-vendor-mark`); `final: false` — нельзя в публикацию. → `../13-routing-matrix/03-routing-matrix.md` §1, §5

**Ворота** (gate) — условие — тест фазы 0 или 5, от которого зависит запуск задания или вариант маршрута (например, I-10 и I-11 не запускать, если прошли I-09 и I-15). → `../13-routing-matrix/03-routing-matrix.md` §8

**Задание фазы 5** (phase-5 job; `inputs_from`; draft job) — строка JSONL для `polza.py` (или `.routerai.json`, `.genapi.json`, `.polza-chat.json` для `mp_client.py`) с явными ценовыми параметрами, `max_rub` и `meta.compile`; `meta.inputs_from` подставляет выход чужого теста как вход (M-04 ← F-07); заготовка — задание вне `jobs/`, переносится после утверждения. → `../99-raw/phase5/README.md`; `../14-recipes/01-hero-recipes.md` §0.5

**Закреплённый фактор** (controlled factor; literal prompt) — условие, одинаковое для всех моделей стенда (бриф, компилятор, диалект, метод серии F); тексты, правки и эталоны — буквальной строкой для всех моделей. → `../13-routing-matrix/01-stand-method.md` §3

**Маршрут** (route, `routing.yaml` v1) — запись для одного кода задачи с вариантами и полями `check`, доставки и `legal`; v1 — 33 маршрута, 124 варианта. → `../13-routing-matrix/03-routing-matrix.md` §1

**Матрица маршрутизации** (routing matrix) — таблица «код задачи → модель, канал, параметры, цена, запас, проверка, доставка, право». → `../13-routing-matrix/03-routing-matrix.md` §1

**Машина бренда** (brand machine; Figma Weave graph) — граф «сетка бренд-картинок → VLM-бриф (= паспорт) → LLM-промты по слотам → генерация → детерминированный грейд `.cube` → шаблоны с текстом»; следующий месяц — смена входов, паспорт не пересобирается, пока не менялись токены (кэш звеньев по хэшу). → `../14-recipes/01-hero-recipes.md` §0.4

**Мини-стенд** (mini-stand; regression set) — регрессионный набор 11–12 задач (фото, продукт, иллюстрация, абстракция, кириллица, счёт, латиница, правка, анти-дефолт) для новой модели против текущего маршрута — «новая модель за час». → `../13-routing-matrix/01-stand-method.md` §7; `../13-routing-matrix/04-update-procedure.md` §4

**«Оба не годятся»** (both bad) — голос-сигнал, что задачу надо решать другим подходом (код, Blender, композит), а не другой моделью; решающие голоса — только A или B. → `../13-routing-matrix/01-stand-method.md` §4.3

**Правило решения** (decision rule) — фильтры → лидер по голосам (≥ 70 % выигранных пар; модели в интервале лидера равны) → из равных дешевле, быстрее, с запасным провайдером → вето «естественности»; запись в маршрут с меткой `[стенд]`, объёмом, судьёй и датой. → `../13-routing-matrix/01-stand-method.md` §5

**Проверка ссылок** (link check, `check_links.py`; false positive) — 7 проверок базы: пути, разделы §, `[S#]`, `[V:id мм:сс]` с таймкодом ≤ длительности ролика, README в обе стороны, разделы файла, метки `[проверено: …]` → папка опыта; ERROR чинить, WARN — эвристика (цель § угадывается по контексту строки, бывают ложные срабатывания). → `../../../scripts/ai-media/README.md`

**Регрессионные ворота** (regression gate) — обязательный мини-стенд перед сменой модели или версии в маршруте: новый чекпойнт молча ухудшает детали. → `../13-routing-matrix/04-update-procedure.md` §4; `../13-routing-matrix/01-stand-method.md` §7

**Реестр противоречий** (contradictions register; audit correction) — `CONTRADICTIONS.md`: 43 пункта X1–X43 со сторонами, данными, позицией базы и тестом фазы 5 (21 решён, 13 — позиция базы, 8 открыты); поправка аудита — правка устаревшего правила прямо в файле с пометкой `[поправка X 24.09.2026 …]` (55 правок). → `../CONTRADICTIONS.md`

**Рецепт исполнимый** (executable recipe; recipe YAML) — цепочка из 10 звеньев «слот → паспорт → спецификация → маршрут → компиляция → задание фазы 5 → проверка → постобработка → провенанс → доставка и приёмка» с командами, порогами и статусом каждого звена; машиночитаемо — 17 рецептов `14-recipes/recipes/*.yaml` по `recipe.schema.json`. → `../14-recipes/01-hero-recipes.md` §0.1, §0.2

**Самоблокировка утилиты** (self-deadlock) — процесс ждёт замок `flock`, который держит его же родитель: `asset_audit.py` (`heavy.lock`, `browser.lock`) и `page_accept.py` (`browser.lock`) берут замок сами и с 24.09 проверяют предка (правки X и X2); утилиты приёмки всё равно не оборачивать во внешний `flock`. → `../../../scripts/ai-media/README.md`

**Самопроверка** (selftest) — встроенный набор проверок утилиты на синтетике и заглушках; прогонять после правки утилиты и нового снимка каталога: `polza.py` макет 30/30, `asset_audit.py` 53/53, `vlm_to_dna.py` 23/23, `mp_client.py` 36/36 (35/36 на снимке 24.09 — сдвиг цен RouterAI, а не поломка). → `../15-tools-atlas/02-tools-libraries-cli.md` §1; `../99-raw/reports/wave4-X-audit.md`

**Слепая пара** (blind pairwise comparison; gold pair; sampling unit) — две картинки одной задачи без имён моделей, сторона случайна; контрольная пара с заведомо худшим вариантом проверяет внимательность; единица выборки — задача, а не голос. → `../13-routing-matrix/01-stand-method.md` §4.3, §4.4

**Снимок каталога** (catalog snapshot; catalog diff; normalized catalog) — сохранённый ответ публичного `GET /models` канала с датой (`99-raw/cache/polza/<дата>/`), разница снимков и нормализованный каталог (`media-models.normalized.json`); снимать перед каждой сессией — за сутки +4 модели и 2 сдвига цен. → `../13-routing-matrix/04-update-procedure.md` §2; `../02-providers-platforms/02-polza-models-params-prices.md` §1.1

**Стенд моделей** (model bake-off stand; model preset) — фиксированный набор задач (31 задача, 16 пресетов «модель + явные параметры цены и провайдер»), брифов и судей для сравнения моделей и повторных прогонов (`stand_run.py`). → `../13-routing-matrix/01-stand-method.md` §2

**Триаж новой модели** (new-model triage) — 5-минутная оценка: уникальная возможность, цена, доказательства, лицензия → мини-стенд или отказ. → `../13-routing-matrix/04-update-procedure.md` §4

**Уровень плана** (plan level; worst case; value per ruble; second sample) — набор тестов фазы 5 с суммой: 1 — polza 652 ₽; 2 (рекомендация) — 1 190 ₽ ожидаемо, 1 468 в худшем случае (все ворота и верхние оценки), RouterAI 95, Gen-API 87; 3 — 2 294 ₽, те же тесты вторым образцом (повтор с другим `variant` ради устойчивости вывода); при нехватке бюджета отсекать по ценности на рубль; после ≈ 2 400 ₽ тесты перестают менять решения. → `../99-raw/phase5/plan-summary.md`

**Фаза 5** (live phase; phase 0) — живые генерации вместе с заказчиком по готовым заданиям `99-raw/phase5/jobs/`; фаза 0 — протокольные тесты T0–T9 (≈ 15–29 ₽) в её начале. → `../99-raw/phase5/README.md`

**Фильтр до голосования** (hard-requirement gate) — автометрика, отсекающая модель по жёсткому требованию (дословность текста, альфа, ΔE) до слепых голосов. → `../13-routing-matrix/01-stand-method.md` §4.1

## 12. Омонимы и расхождения терминологии

Одно слово — разные вещи в разных папках, или отчёты определили термин по-разному. Колонка «Принято» — значение, которым
пользуется база; расхождения по существу (а не по словам) — в `../CONTRADICTIONS.md` (аудит X).

| Термин | Значения в базе | Принято |
|---|---|---|
| Паспорт | (1) паспорт визуала — правила изображений бренда (`06-art-direction-consistency/`, `visual-dna.schema.json`); (2) паспорт генерации — JSON рядом с файлом: запрос, цена, sha256, права, метки (`02-providers-platforms/01` §12.5, `12-legal-provenance/04` §4; формат `mp-passport/1` у `mp_client.py`); (3) паспорт компиляции `meta.compile` (`05-prompting/06` §2); (4) паспорт системы иллюстраций в `../../ui/07-iconography-imagery/02-illustration-system-avatars-images.md` — шаблон, из которого вырос паспорт визуала | всегда с уточнением: «паспорт визуала», «паспорт генерации», «паспорт компиляции» |
| Ворота | (1) условие запуска теста фазы 5 (`gate` в заданиях и `routing.yaml`, `13-routing-matrix/03` §8); (2) регрессионные ворота — мини-стенд перед сменой модели (`13-routing-matrix/04` §4); (3) ворота перед публикацией — вопросы права L (`12-legal-provenance/04` §5); (4) «фильтр до голосования» E по-английски назван hard-requirement gate | (1) — «ворота», (2) — «регрессионные ворота», (3) — «ворота перед публикацией», (4) — «фильтр до голосования» |
| Живость | (1) «живость» видео — `motion_med`, медиана межкадровой разницы (`09-video-pipeline/01` §1.1, отчёты C2, I); (2) живость сервиса или модели — активен ли и до какой даты (`15-tools-atlas/`, отчёт N) | видео — «живость» в кавычках и с полем `motion_med`; сервис — «живость (liveness)» только в атласе |
| Шов | (1) шов петли видео `seam_ratio` / `seam_ratio_local`, порог ≤ 1,5 после среза (`video_loop_check.py`); (2) шов текстуры `tile_check.py`, ≤ 1,3 бесшовно, > 1,5 чинить; (3) «шов» вклейки после правки — контур от дрейфа цвета или «призрак» | метрики не смешивать: пороги разные, считаются по-разному |
| Отношение шва у A и у I | A/02 и C2 мерили глобальный `seam_ratio` (≤ 1,5 — «шва нет»); I показал, что он пропускает дубль кадра (≈ 0) и завышает шов у оборота (8,84 при идеальной петле) | приёмка — `seam_ratio_local` ≤ 1,5 после среза + `motion_vs_control` ≥ 0,5; глобальный — справочно |
| Мезонин | H: промежуточный мастер высокого качества; I: файл CRF 10 для кодирования; K: для замеров шва и `motion_keep` — только без потерь (x264 `-qp 0`, PNG) | мезонин без потерь; битрейт < 15 Мбит/с — это уже финальный сжатый файл (`thresholds.yaml`) |
| Резерв | (1) `reservedAmount` polza — сумма, удержанная сервером на время генерации (B); (2) резерв в бюджете клиента `mp_client.py` — оценка до конечного события задачи (B2) | оба смысла допустимы, указывать чей: «резерв polza», «резерв клиента» |
| Двойник, близнец, недвойник | E: латинский двойник (A/А) и недвойник (N вместо И); K добавил «близнец» — почти неотличимая буква (u/и, n/п, r/г), которую OCR не видит | три разных случая; фильтр E «0 недвойников» близнецов не ловит — нужен «латинский нюх» и человек |
| GNED | TIIF-Bench (первоисточник метрики) — Global Normalized Edit Distance; WeGenBench — Generalized Normalized Edit Distance; отчёт D повторил «generalized» | база пользуется метрикой TIIF: «global» |
| Порог доверия VLM-судье | E (`13-routing-matrix/01` §4.2): 75–80 % согласия; K (`11-evaluation-qa/02` §6, `thresholds.yaml`): ≥ 0,8 и нижняя граница Уилсона ≥ 0,65 | K: ≥ 0,8 + Уилсон ≥ 0,65 — сортировать; 0,7–0,8 — только отсев |
| Контраст текста поверх фото | A — p95 яркости зоны; F — p99,9; WCAG — F83 (худший пиксель за буквами) | соответствие — F83; плотность скрима — p99,9; p95 не использовать (`06-art-direction-consistency/03` §2.3) |
| Лист ракурсов и контактный лист | W4 назвал лист ракурсов contact sheet; в базе контактный лист — сетка кадров или вариантов для проверки глазами (`asset_inventory.py`, `video_loop_check.py sheet`) | лист ракурсов — референс (turnaround); контактный лист — инструмент проверки |
| Правка «много за раз» | многоходовая — цепочка правок от предыдущего результата (W2, W3, W6 «цепочка правок»); многошаговая (W1) и смешанная (D2) — несколько операций в одном вызове | «многоходовая» — последовательность вызовов; «смешанная» — один вызов с несколькими операциями |
| Перенос и подгонка цвета | перенос цвета (F: Reinhard, MKL — к эталону другой картинки) и подгонка цвета (H: линейная коррекция правки к исходнику на неизменной зоне); оба по-английски color matching | перенос — только внутри класса сюжетов; подгонка — всегда перед композитом правки и перед FLF с правленым кадром |
| Переписчик и расширение промта | D различает переписчик (rewriter, upsampling, enhancer) и расширение (prompt expansion — несколько промтов ради разнообразия); у Wan и Gen-API параметр `enable_prompt_expansion` — это переписчик | «переписчик» — всё, что меняет промт до модели; «расширение» — только метод Google 2023 |
| Мини-стенд | E и N — регрессионный набор 11–12 задач стенда против текущего маршрута (`13-routing-matrix/01` §7); F — канарейки паспорта: 5 сюжетов × 4–5 ₽ (`06-art-direction-consistency/01` §8) | «мини-стенд» — модельный (E/N); проверка стиля на новой модели — «канарейки паспорта» |
| Референс против кадра | у Seedance 1.5 Pro, Kling 3 и Veo поле `images` — первый и последний кадр; у Seedance 2.x `images` — референсы, не кадры (тест I-08); у GA Omni 1.1 кадры — `first_frame_url` и `last_frame_url` | роль поля брать из карточки модели и `09-video-pipeline/04` §1, не по имени поля |
| Ступень | ступень цены (`tiers`), ступень разрешения (1K/2K/4K), ступень лестницы дешевизны | всегда с уточнением |
| Слот | слот страницы (A, место ассета) и слоты промта (F, переменные шаблона серии) | «слот» без уточнения — место на странице |

## 13. Указатель EN → RU

Английский термин или синоним → русский термин (номер группы). Сортировка по первому английскому слову.

**#**: 2.5D → Параллакс слоёв (6) · 2×2 grid → Набор одним вызовом (3)

**A**: A/B arm → Плечо A/B (2) · above the fold → Первый экран (7) · AbsRel, δ1 → Карта глубины (6) · acceptance log → Калибровка судьи (8) · aggregator → Агрегатор (10) · AI content clichés → Клише «про ИИ» (3) · AI hyperrealism → Гиперреализм ИИ-лиц (3) · AI slop → Слоп (3) · AI-tell marker (`IMG-Mxx`, `VID-Mxx`) → Маркер сгенерированности (3) · all-intra encoding → All-intra (4) · alpha / video matting → Матирование (6) · alpha channel → Прозрачный фон (6) · alpha video: VP9-alpha, HEVC-alpha, stacked alpha → Видео с альфой (7) · ambient motion → Перечень фонового движения (4) · ambiguous failure → Двусмысленный сбой (10) · anchor image → Эталон серии (3) · angle sheet → Лист ракурсов (3) · anti-average composition → Блок против «среднего» (3) · art direction (`<picture media>`) → Арт-дирекшн адаптивных картинок (7) · asset → Ассет (1) · asset acceptance / audit (`asset_audit.py`) → Приёмка ассета (8) · asset plan → План ассетов (1) · asset spec → Спецификация ассета (2) · async mode → Асинхронный режим и опрос (10) · atomic question → DSG (8) · audit correction → Реестр противоречий (11) · auto cap → Верхняя оценка (10) · autorater → VLM-судья (8) · average look → «Средний вид» (3)

**B**: background motion list → Перечень фонового движения (4) · background removal → Удаление фона (6) · banding → Бандинг (6) · benchmark saturation → Профильный бенчмарк (8) · best-of-N → Лучший из N (1) · blind pairwise comparison → Слепая пара (11) · block + slots + iterator → Блок стиля серии (3) · both bad → «Оба не годятся» (11) · Bradley–Terry model → Модель Брэдли–Терри (8) · brand machine → Машина бренда (11)

**C**: C2PA Trust List → «Valid» и «Trusted» (9) · CAMBI → Бандинг (6) · camera creep → Ползущая камера (4) · canary subjects → Канарейки (3) · catalog diff → Снимок каталога (11) · catalog snapshot → Снимок каталога (11) · CFG → Негативный промт (2) · chain anchor → Цепочка клипов (4) · chain of title → Цепочка прав (9) · channel → Канал (10) · channel / provider configuration → Конфигурация канала (10) · character / product sheet → Лист ракурсов (3) · cheapness ladder → Лестница дешевизны (1) · chroma key → Хромакей (6) · cICP → Теги цвета (7) · cinemagraph → Синемаграф (4) · clean plate → Чистая подложка (6) · clip chaining → Цепочка клипов (4) · CLIPScore, VQAScore, FID → Метрики соответствия тексту (8) · Code of Practice on Transparency of AI-generated Content → Кодекс практики (9) · colorfulness (Hasler–Süsstrunk) → Цветность (8) · colour coverage → Покрытие цвета (3) · colour decontamination → Ореол (6) · colour description: primaries, transfer, matrix, range → Теги цвета (7) · colour difference: ΔE00 (CIEDE2000), ΔE OKLab → ΔE (3) · colour matching (`--match-color`) → Подгонка цвета (6) · colour shift → Дрейф цвета (6) · colour transfer (Reinhard, MKL) → Перенос цвета (3) · compile passport → Компилятор промтов (2) · compression bias → Одинаковое кодирование (8) · constant rate factor → CRF (6) · contact sheet → Контактный лист (8) · Content Credentials → C2PA (9) · content endpoint → Content-эндпоинт (10) · continuity contract → Мульти-шот (4) · contradictions register → Реестр противоречий (11) · controlled factor → Закреплённый фактор (11) · copyright management information → Видимый водяной знак (9) · corners sheet → Контактный лист (8) · cross-border transfer (152-ФЗ ст. 12) → Трансграничная передача ПДн (9) · curation → Лучший из N (1) · currentColor → `currentColor` (5) · cutout → Удаление фона (6)

**D**: Davidsonian Scene Graph → DSG (8) · dead frame → Мёртвый кадр (4) · decide-only → VLM-судья (8) · decision rule → Правило решения (11) · deep fake (AI Act ст. 3(60)) → Дипфейк (9) · default aesthetic → «Средний вид» (3) · defect code → Приёмка ассета (8) · deployer (AI Act ст. 3(4)) → Деплоер (9) · depth edge bleeding → «Резиновая плёнка» (6) · depth map → Карта глубины (6) · derivative provenance → Digital Source Type (9) · despill → Деспилл (6) · difference-derived mask → Локальный сдвиг (8) · digitally altered image (CA AB 723) → Изменённое изображение недвижимости (9) · disclosure, label → Видимая метка (9) · disparity → Карта глубины (6) · dithering → Бандинг (6) · DOM layout check (`layout_check.py`) → DOM-проверка вёрстки (8) · dominant reference element → Референс-доминанта (3) · draft job → Задание фазы 5 (11) · draft mode → Черновой режим (1) · draft → final → Черновой режим (1) · drift → Пороги серии (3) · dry run → Сухой прогон (10) · duplicate seam frame → Петля [A,A] (4)

**E**: edge density → Зона под текст (3) · edge sharpness → Перерисовка исходника (6) · edit leakage → Утечка правки (6) · edit mask → Маска правки (6) · effect template → Шаблон эффекта (2) · effective FX rate → Эффективный курс (10) · effective visual size → Картинка «на весь вьюпорт» (7) · Elo → Модель Брэдли–Терри (8) · encoding parity → Одинаковое кодирование (8) · env colour (`palette.env_color`) → Цвет секции (3) · EU AI icon → Видимая метка (9) · evidence class A / B / C → Класс доказательств (8) · executable recipe → Рецепт исполнимый (11) · extend → Продление (4)

**F**: fallback `<source>` → Запасной источник (7) · fallback tier (`[]`) → Запасная ступень (10) · false positive → Проверка ссылок (11) · `fetchpriority` → Приоритет и ленивая загрузка (7) · Figma Weave graph → Машина бренда (11) · film grain → Плёночное зерно (3) · `final` → Вариант маршрута (11) · first-last frame (FLF, FL2V, keyframes) → Первый и последний кадр (4) · `fixed_lens` → Неподвижная камера (4) · flat rate → Плоский тариф (10) · flying pixels → «Резиновая плёнка» (6) · focal point → Фокусная точка (3) · format family → Аутпейнт (6) · frame interpolation (RIFE, FILM) → Интерполяция кадров (4) · functional implausibility → Функциональный артефакт (3)

**G**: gap bridging → Кроссфейд хвоста (4) · gate → Ворота (11) · generation passport → Паспорт генерации (10) · global colour drift → Дрейф цвета (6) · Global Normalized Edit Distance (TIIF-Bench) → GNED (8) · gold pair → Слепая пара (11) · GOP → All-intra (4) · grade → Грейд (3) · grayscale AVIF overlay (`avifenc -y 400`) → Серый оверлей 4:0:0 (7) · ground-truth alpha → Удаление фона (6) · grounding location → «Где» маркера (8)

**H**: halo, fringe → Ореол (6) · hard binding → Привязка манифеста (9) · hard-requirement gate → Фильтр до голосования (11) · hero pair → Телефонный мастер (7) · hero section, key visual → Hero (1) · hybrid AI production → Гибридный продакшн (1)

**I**: idempotency → Двусмысленный сбой (10) · idle motion → Уменьшение движения (7) · image / video arena (AA, LMArena) → Арена (8) · image of a citizen (ГК РФ ст. 152.1) → Изображение гражданина (9) · imperceptible watermark (SynthID, Content Seal) → Невидимый водяной знак (9) · implicit / explicit AIGC label (GB 45438-2025) → Метка AIGC (9) · in-mask motion keep (`keep_in`) → Сохранение движения (7) · in-prompt negation → «No X» в прозе (2) · indemnification → Индемнификация (9) · ingredient → C2PA (9) · inpainting → Маска правки (6) · input translation (`translate_input`) → Перевод входа (10) · `inputs_from` → Задание фазы 5 (11) · Instagram-filter effect → Эффект Instagram-фильтра (3) · instruction-based editing → Правка по инструкции (2) · invented colour → Покрытие цвета (3) · IPTC Digital Source Type → Digital Source Type (9) · iterative edit chain → Многоходовая правка (2)

**J**: JPEG XL (JXL) → JPEG XL (6) · JSON / structured prompt → JSON-промт (2) · judge calibration → Калибровка судьи (8)

**K**: key colour → Хромакей (6) · key reflection → Деспилл (6) · key spend limit → Верхняя оценка (10) · keyer (`colorkey`, `chromakey`, `hsvkey`) → Кеер (6) · keyframe pulse → Пульс ключевого кадра (4) · keying tolerance margin → Кеер (6)

**L**: large foundation model → 243-ФЗ (9) · Largest Contentful Paint → LCP (7) · latent tiling → Бесшовная текстура (6) · Latin homoglyph → Латинские двойники (8) · Latin sniff → «Латинский нюх» (8) · layer decomposition (`IMG-LAYERS`) → Разложение на слои (6) · layer parallax → Параллакс слоёв (6) · LCP candidate → Кандидат LCP (7) · LCP image entropy (bpp) → Энтропия картинки для LCP (7) · leaderboard category → Арена (8) · license flag → Вариант маршрута (11) · likeness / IP clearance check → Проверка сходства (9) · link check (`check_links.py`) → Проверка ссылок (11) · link preview → Карточка ссылки (7) · literal prompt → Закреплённый фактор (11) · live area → Живая область (5) · live phase → Фаза 5 (11) · liveness → Атлас инструментов (11) · LLM front-end → Класс входа модели (2) · LLM-generated SVG → SVG кодом (5) · `loading="lazy"` → Приоритет и ленивая загрузка (7) · local shift (`QA-EDIT-LOCAL-SHIFT`) → Локальный сдвиг (8) · locked-off / static camera → Неподвижная камера (4) · locks → Замки (2) · loop pop → Пульс ключевого кадра (4) · loop seam → Шов петли (4) · LoRA → Открытые веса (1) · lossless mezzanine → Мезонин (6) · Lottie, dotLottie → Lottie (5) · low-quality image placeholder → LQIP (7)

**M**: machine-readable marking → Машиночитаемая маркировка (9) · manifest store → C2PA (9) · manufactured negatives → Сфабрикованные негативы (8) · marker cluster → Кластер маркеров (3) · mask dilation, feathering → «Призрак» удаления (6) · mask polarity → Полярность маски (6) · maskable icon → Маскируемая иконка (5) · masked merge (`maskedmerge`) → Синемаграф (4) · maskless / semantic-mask editing → Безмасочная правка (2) · material swatch reference → Референс-«кубик» (3) · mezzanine (lossless) → Мезонин (6) · mini-stand → Мини-стенд (11) · minimum error boundary cut → Шов текстуры (6) · mixed-operation / multi-step edit → Смешанная правка (2) · mock channel → Макет сервера (10) · mock server → Макет сервера (10) · model alias → Маршрутизация провайдера (10) · model bake-off stand → Стенд моделей (11) · model input class → Класс входа модели (2) · model preset → Стенд моделей (11) · moodboard → Стилевой референс (3) · motion budget (WCAG 2.2.2) → Бюджет движения (7) · motion constraint → Запрет движения (4) · motion liveness (`motion_med`, `motion_vs_control`) → «Живость» (4) · motion-only prompt → Промт «только движение» (4) · `motion_keep` (motion retention) → Сохранение движения (7) · MP4 edit list → Нормализация выхода модели (4) · multi-reference → Мульти-референс (1) · multi-shot → Мульти-шот (4) · multi-turn editing → Многоходовая правка (2)

**N**: native loop → Бесшовная петля (4) · near-homoglyph → Латинские двойники (8) · negative prompt → Негативный промт (2) · negative space, copy space → Зона под текст (3) · new-model triage → Триаж новой модели (11) · non-commercial, territory-restricted, revenue-threshold licenses → Лицензии открытых весов (9) · non-homoglyph substitute → Латинские двойники (8) · non-removal → Машиночитаемая маркировка (9) · normalized catalog → Снимок каталога (11) · nowrap flex item → DOM-проверка вёрстки (8)

**O**: OCR language-prior autocorrection → «Латинский нюх» (8) · OG safe zone → Карточка ссылки (7) · `og:image` → Карточка ссылки (7) · omni reference → Референс (1) · open weights → Открытые веса (1) · original composite (`--composite`) → Композит оригинала (6) · outpainting → Аутпейнт (6) · output normalization → Нормализация выхода модели (4) · outside-target preservation → Сохранность вне цели (8) · over-editing → Утечка правки (6) · overprocessing → Эффект Instagram-фильтра (3)

**P**: page acceptance (`page_accept.py`) → Приёмка страницы (7) · painted counter → Нарисованное отверстие (5) · pairwise preference → Попарное сравнение (8) · palette ΔE → Пороги серии (3) · parametric LUT (`.cube`) → Грейд (3) · passthrough parameter → Сквозной параметр (10) · pattern tile (`VEC-PATTERN`) → Плитка паттерна (5) · pause control → Бюджет движения (7) · per-glyph, per-frame contrast → F83 (7) · per-second, token, megapixel pricing → Единица цены (10) · percentage alignment → Фокусная точка (3) · phase 0 → Фаза 5 (11) · phase-5 job → Задание фазы 5 (11) · phone master frame → Телефонный мастер (7) · ping-pong, boomerang → Пинг-понг (4) · pink elephant effect → «No X» в прозе (2) · pixel over-delivery → Переотдача пикселей (7) · plan level → Уровень плана (11) · plasticky look (`IMG-M01`) → Пластиковость (3) · polling → Асинхронный режим и опрос (10) · position bias → Позиционный сдвиг (8) · positive exclusion replacement → Позитивная замена запрета (2) · poster frame → Постер (7) · pre-publication gates → Ворота перед публикацией (9) · `prefers-reduced-motion: reduce` → Уменьшение движения (7) · premultiplied alpha → Stacked alpha (7) · preservation suffix → Оберег (2) · preserve list → Оберег (2) · price-affecting parameter → Ценовой параметр (10) · pricing tier (`tiers[].conditions`) → Ступень цены (10) · probe → Зонд (10) · product composite → Композит товара (6) · product seven-block prompt → Промт продукта из 7 блоков (2) · prompt compiler (`prompt_compile.py` v2.1) → Компилятор промтов (2) · prompt dialect: prose, sections, JSON, IR → Диалект промта (2) · prompt expansion → Переписчик промта (2) · prompt rewriter / upsampler / enhancer → Переписчик промта (2) · proportion guide → Гид пропорций (3) · provenance signature (`<recraft-signature>`) → Подпись провенанса SVG (5) · provider (AI Act ст. 3(3)) → Провайдер ИИ-системы (9) · provider routing (объект `provider`) → Маршрутизация провайдера (10) · pseudo-text → Незаказанный текст (8) · push-in, orbit, tracking, turntable → Движения камеры (4)

**Q**: quality level → Ступени разрешения и качества (1) · quality words / boosters → Слова качества (2) · quiet loop → Петля [A,A] (4)

**R**: recipe YAML → Рецепт исполнимый (11) · recognizability → Узнаваемость метафоры (5) · reference image / video → Референс (1) · reference role → Роль референса (2) · reference subject class → Класс сюжетов референса (3) · regeneration (`REGENERATED`) → Перерисовка исходника (6) · regression gate → Регрессионные ворота (11) · regression set → Мини-стенд (11) · removal ghost → «Призрак» удаления (6) · request hash → Хэш запроса (10) · research license (Qwen Research License) → Исследовательская лицензия (9) · reseller storefront → Агрегатор (10) · reservation → Резерв (10) · reserved amount → Резерв (10) · resolution tier 1K/2K/4K → Ступени разрешения и качества (1) · restrained motion → Запрет движения (4) · result TTL → Срок жизни результата (10) · ring joint → Мёртвый кадр (4) · role → Вариант маршрута (11) · route option → Вариант маршрута (11) · route (`routing.yaml` v1) → Маршрут (11) · routing matrix → Матрица маршрутизации (11) · routing validator (`routing_check.py`) → Валидатор маршрутов (11) · rubric (`*.rubric.json`) → Рубрика (8) · Russian AI law (26.07.2026) → 243-ФЗ (9)

**S**: safe band → Безопасная полоса (3) · safe crop zone → Безопасная полоса (3) · saliency centroid → «Средний вид» (3) · same-frame FLF loop → Петля [A,A] (4) · sampling unit → Слепая пара (11) · scrim → Скрим (7) · scroll-driven animation → Параллакс слоёв (6) · `seam_ratio`, `seam_ratio_local` → Шов петли (4) · seamless / tileable texture → Бесшовная текстура (6) · seamless loop → Бесшовная петля (4) · second sample → Уровень плана (11) · self-deadlock → Самоблокировка утилиты (11) · selftest → Самопроверка (11) · semantic negative → Позитивная замена запрета (2) · series anchor → Эталон серии (3) · series hue spread → Пороги серии (3) · series style block → Блок стиля серии (3) · service exclusion → Служебный запрет (2) · set-aware generation → Набор одним вызовом (3) · shadow layer (multiply) → Слой тени (7) · sidecar manifest (`.c2pa`) → Sidecar-манифест (9) · single-shot → Мульти-шот (4) · `sizes="auto"` → Приоритет и ленивая загрузка (7) · slot → Слот (1) · SMIL animation → SMIL (5) · soft binding → Привязка манифеста (9) · spend ledger → Журнал затрат (10) · spotlight mask reveal → Прожектор (7) · SSIM, PSNR, LPIPS, DINO, DreamSim, CSD → Метрики сходства (8) · SSIMULACRA2 → SSIMULACRA2 (6) · stacked alpha video → Stacked alpha (7) · standard editing → Стандартная правка (9) · static collapse → Статичный коллапс (4) · static mask → Синемаграф (4) · storage policy → Срок жизни результата (10) · style code (`style_id`, `--sref`) → Стилевой референс (3) · style control → Арена (8) · style reference → Стилевой референс (3) · swap consistency → Позиционный сдвиг (8) · synthetic performer (NY GBL § 396-b) → Синтетический исполнитель (9)

**T**: tail crossfade → Кроссфейд хвоста (4) · target value → Правка по инструкции (2) · task code → Код задачи (1) · task-specific benchmark → Профильный бенчмарк (8) · testimonial (16 CFR 465) → Отзыв-свидетельство (9) · text layer render → Слой текста (8) · text zone → Зона под текст (3) · text- / image- / video-to-video → t2v, i2v, v2v (4) · text-axis scrim → Скрим (7) · texture seam ratio (`tile_check.py`) → Шов текстуры (6) · thumbhash → LQIP (7) · timestamp prompting → Таймкод-промтинг (4) · tools atlas → Атлас инструментов (11) · transparent background → Прозрачный фон (6) · trust threshold → Калибровка судьи (8) · turnaround → Лист ракурсов (3) · two-halves loop → Две половины (4)

**U**: unrequested text → Незаказанный текст (8) · unsigned URL → Content-эндпоинт (10) · upper-bound estimate → Верхняя оценка (10) · upscale → Апскейл (6) · upstream provider (`mie` ≈ KIE.ai) → Исполнитель (10)

**V**: validation state → «Valid» и «Trusted» (9) · value per ruble → Уровень плана (11) · vectorization, tracing (vtracer, potrace) → Векторизация (5) · vendor prompt skill → Скилл вендора (2) · verbatim accuracy → Дословность (8) · verdict → Приёмка ассета (8) · video layer over poster → Постер (7) · video slop → Слоп (3) · viewport rule → Картинка «на весь вьюпорт» (7) · viewport-covering image → Картинка «на весь вьюпорт» (7) · visible watermark → Видимый водяной знак (9) · visual DNA passport → Паспорт визуала (3) · visual weight → Оптический вес (5) · VLM critic → VLM-судья (8) · VLM-as-a-judge → VLM-судья (8)

**W**: WCAG 2.2 failure technique F83 → F83 (7) · webhook → Асинхронный режим и опрос (10) · Wilson score interval → Модель Брэдли–Терри (8) · worst case → Уровень плана (11)

## 14. Указатель RU

Все термины по алфавиту с номером группы; «Синоним → Термин (N)» — понятие описано внутри записи «Термин».

**А**: Автооценщик → VLM-судья (8) · Автопотолок → Верхняя оценка (10) · Агрегатор (10) · Алиас модели → Маршрутизация провайдера (10) · Альфа-канал → Прозрачный фон (6) · Анимация по прокрутке → Параллакс слоёв (6) · Апсемплинг промта → Переписчик промта (2) · Апскейл (6) · Арена (8) · Арт-дирекшн адаптивных картинок (7) · Асинхронный режим и опрос (10) · Ассет (1) · Атлас инструментов (11) · Атомарный вопрос → DSG (8) · Аутпейнт (6)

**Б**: Бандинг (6) · Безмасочная правка (2) · Безопасная зона OG → Карточка ссылки (7) · Безопасная полоса (3) · Бесшовная петля (4) · Бесшовная текстура (6) · Блок + слоты + итератор → Блок стиля серии (3) · Блок против «среднего» (3) · Блок стиля серии (3) · Блок типографики → Промт продукта из 7 блоков (2) · Большая фундаментальная модель → 243-ФЗ (9) · Буквальный промт → Закреплённый фактор (11) · Бюджет движения (7)

**В**: Валидатор маршрутов (11) · Вариант маршрута (11) · Вебхук → Асинхронный режим и опрос (10) · Векторизация (5) · Вердикт приёмки → Приёмка ассета (8) · Верхняя оценка (10) · Видео двойной высоты → Stacked alpha (7) · Видео с альфой (7) · Видео-референс → Референс (1) · Видео-слой как LCP → Постер (7) · Видео-слой над постером → Постер (7) · Видео-слоп → Слоп (3) · Видимая метка (9) · Видимый водяной знак (9) · Визуальная ДНК → Паспорт визуала (3) · Витрина → Агрегатор (10) · Ворота (11) · Ворота перед публикацией (9) · Второй образец → Уровень плана (11) · Вырез → Удаление фона (6)

**Г**: «Где» маркера (8) · Гибридный продакшн (1) · Гид пропорций (3) · Гиперреализм ИИ-лиц (3) · Грейд (3) · Грязный передний план → Блок против «среднего» (3)

**Д**: Две половины (4) · Движение в маске → Сохранение движения (7) · Движение в покое → Уменьшение движения (7) · Движения камеры (4) · Двойной снимок → F83 (7) · Двусмысленный сбой (10) · Двухкадровая генерация → Первый и последний кадр (4) · Деконтаминация цвета → Ореол (6) · Деплоер (9) · Деспилл (6) · Диалект промта (2) · Дизеринг → Бандинг (6) · Дилатация маски → «Призрак» удаления (6) · Дипфейк (9) · Диспаритет → Карта глубины (6) · Дорисовка → Аутпейнт (6) · Дословность (8) · Дрейф серии → Пороги серии (3) · Дрейф цвета (6) · Дубль кадра на стыке → Петля [A,A] (4)

**Е**: Единица выборки → Слепая пара (11) · Единица цены (10)

**Ж**: Жёсткая привязка → Привязка манифеста (9) · Живая область (5) · «Живость» (4) · Журнал затрат (10) · Журнал приёмки → Калибровка судьи (8)

**З**: Заготовка задания → Задание фазы 5 (11) · Задание фазы 5 (11) · Закреплённый фактор (11) · Замки (2) · Замок в промте → Замки (2) · Запас по similarity → Кеер (6) · Запасная ступень (10) · Запасной источник (7) · Запрет движения (4) · Зона под текст (3) · Зонд (10)

**И**: Идемпотентность → Двусмысленный сбой (10) · Изменённое изображение недвижимости (9) · Изображение гражданина (9) · Иконка ЕС «AI» → Видимая метка (9) · Ингредиент → C2PA (9) · Индемнификация (9) · Инпейнт → Маска правки (6) · Интервал Уилсона → Модель Брэдли–Терри (8) · Интерполяция кадров (4) · Информация об авторском праве → Видимый водяной знак (9) · Исполнитель (10) · Исследовательская лицензия (9)

**К**: Кадр-постер → Постер (7) · Калибровка судьи (8) · Канал (10) · Канарейки (3) · Кандидат LCP (7) · Каркас рецепта → Рецепт исполнимый (11) · Карта глубины (6) · Картинка «на весь вьюпорт» (7) · Карточка ссылки (7) · Кеер (6) · Кеинг → Хромакей (6) · Класс входа модели (2) · Класс доказательств (8) · Класс сюжетов референса (3) · Кластер маркеров (3) · Клише «про ИИ» (3) · Ключ по оттенку объекта → Хромакей (6) · Кнопка паузы → Бюджет движения (7) · Код дефекта → Приёмка ассета (8) · Код задачи (1) · Код персонализации → Стилевой референс (3) · Кодекс практики (9) · Компилятор промтов (2) · Композит оригинала (6) · Композит товара (6) · Контактный лист (8) · Контракт непрерывности → Мульти-шот (4) · Контраст по кадрам → F83 (7) · Контроль стиля → Арена (8) · Контрольная пара → Слепая пара (11) · Конфигурация канала (10) · Кроссфейд хвоста (4) · Круговой стык → Мёртвый кадр (4) · Кураторство → Лучший из N (1)

**Л**: Латентный тайлинг → Бесшовная текстура (6) · Латинские двойники (8) · Латинский близнец → Латинские двойники (8) · Латинский двойник → Латинские двойники (8) · Латинский недвойник → Латинские двойники (8) · «Латинский нюх» (8) · Ленивая загрузка → Приоритет и ленивая загрузка (7) · Лестница дешевизны (1) · Лимит ключа → Верхняя оценка (10) · Лист персонажа → Лист ракурсов (3) · Лист ракурсов (3) · Лист углов → Контактный лист (8) · Лицензии открытых весов (9) · Ложное срабатывание → Проверка ссылок (11) · Локальный сдвиг (8) · Лучший из N (1)

**М**: Макет канала → Макет сервера (10) · Макет сервера (10) · Маркер сгенерированности (3) · Маршрут (11) · Маршрутизация провайдера (10) · Маска из разницы → Локальный сдвиг (8) · Маска неподвижных зон → Синемаграф (4) · Маска правки (6) · Маскируемая иконка (5) · Матирование (6) · Матрица маршрутизации (11) · Матрица цвета → Теги цвета (7) · Машина бренда (11) · Машиночитаемая маркировка (9) · Мегапиксельная цена → Единица цены (10) · Мезонин (6) · Мезонин без потерь → Мезонин (6) · Мёртвый кадр (4) · Метка AIGC (9) · Метрики соответствия тексту (8) · Метрики сходства (8) · Микропауза на стыке → Петля [A,A] (4) · Мини-стенд (11) · Многоходовая правка (2) · Многошаговая правка → Смешанная правка (2) · Модель Брэдли–Терри (8) · Монохромный оверлей → Серый оверлей 4:0:0 (7) · Мост через разрыв → Кроссфейд хвоста (4) · Мудборд → Стилевой референс (3) · Мульти-референс (1) · Мульти-шот (4) · Мягкая привязка → Привязка манифеста (9)

**Н**: Набор одним вызовом (3) · Наезд → Движения камеры (4) · Наклеенность → Цвет секции (3) · Нарисованная шахматка → Прозрачный фон (6) · Нарисованное отверстие (5) · Насыщение бенчмарка → Профильный бенчмарк (8) · Нативная петля → Бесшовная петля (4) · Невидимый водяной знак (9) · Негативный промт (2) · Незаказанный текст (8) · Некоммерческая лицензия → Лицензии открытых весов (9) · Неподвижная камера (4) · Неподписанная ссылка → Content-эндпоинт (10) · Неудаление меток → Машиночитаемая маркировка (9) · Нормализация выхода модели (4) · Нормализованный каталог → Снимок каталога (11)

**О**: «Оба не годятся» (11) · Оберег (2) · Облёт → Движения камеры (4) · Оборот продукта → Движения камеры (4) · Одинаковое кодирование (8) · Одноплановый режим → Мульти-шот (4) · Омни-референс → Референс (1) · Опора цепочки → Цепочка клипов (4) · Опрос → Асинхронный режим и опрос (10) · Оптический вес (5) · Ореол (6) · Отзыв-свидетельство (9) · Открытые веса (1) · Отношение шва → Шов петли (4)

**П**: Параллакс слоёв (6) · Параметрический LUT → Грейд (3) · Паспорт визуала (3) · Паспорт генерации (10) · Паспорт компиляции → Компилятор промтов (2) · Первый и последний кадр (4) · Первый экран (7) · Перевод входа (10) · Переиспользование выхода → Задание фазы 5 (11) · Перенос цвета (3) · Переобработка → Эффект Instagram-фильтра (3) · Переотдача пикселей (7) · Переписчик промта (2) · Переправка → Утечка правки (6) · Перерисовка исходника (6) · Перечень фонового движения (4) · Петля [A,A] (4) · Пиксельно точная правка → Сохранность вне цели (8) · Пинг-понг (4) · План ассетов (1) · Пластиковость (3) · Плёночное зерно (3) · Плечо A/B (2) · Плитка паттерна (5) · Плоский тариф (10) · Плотность краёв → Зона под текст (3) · Подгонка цвета (6) · Подпись провенанса SVG (5) · Позитивная замена запрета (2) · Позиционный сдвиг (8) · Покрытие цвета (3) · Ползущая камера (4) · Политика хранения → Срок жизни результата (10) · Полоса текста → F83 (7) · Полярность маски (6) · Попарное предпочтение → Попарное сравнение (8) · Попарное сравнение (8) · Поправка аудита → Реестр противоречий (11) · Порог доверия судье → Калибровка судьи (8) · Пороги серии (3) · Пороговая лицензия → Лицензии открытых весов (9) · Последовательная генерация → Набор одним вызовом (3) · Постер (7) · Правило асимметрии → Блок против «среднего» (3) · Правило вьюпорта → Картинка «на весь вьюпорт» (7) · Правило решения (11) · Правка по инструкции (2) · Премультиплицированная альфа → Stacked alpha (7) · Пресет модели → Стенд моделей (11) · Привязка манифеста (9) · Придуманный цвет → Покрытие цвета (3) · Приёмка ассета (8) · Приёмка страницы (7) · «Призрак» удаления (6) · Приоритет загрузки → Приоритет и ленивая загрузка (7) · Приоритет и ленивая загрузка (7) · Провайдер ИИ-системы (9) · Провайдер маршрута → Исполнитель (10) · Провенанс производной → Digital Source Type (9) · Проверка ссылок (11) · Проверка сходства (9) · Продление (4) · Прожектор (7) · Проза по разделам → Диалект промта (2) · Прозрачный фон (6) · Промт «только движение» (4) · Промт продукта из 7 блоков (2) · Профильный бенчмарк (8) · Пульс ключевого кадра (4)

**Р**: Разброс оттенка серии → Пороги серии (3) · Разложение на слои (6) · Разница снимков → Снимок каталога (11) · Разрез минимальной ошибки → Шов текстуры (6) · Раскрытие ИИ → Видимая метка (9) · Распределение подписей обучения → Класс входа модели (2) · Растушёвка → «Призрак» удаления (6) · Расширение промта → Переписчик промта (2) · Регенерация → Черновой режим (1) · Регрессионные ворота (11) · Регрессионный набор → Мини-стенд (11) · Реестр противоречий (11) · Резерв (10) · «Резиновая плёнка» (6) · Резкость краёв → Перерисовка исходника (6) · Референс (1) · Референс-«кубик» (3) · Референс-доминанта (3) · Рецепт → Рецепт исполнимый (11) · Рецепт исполнимый (11) · Решающий голос → «Оба не годятся» (11) · Роль референса (2) · Рубрика (8)

**С**: Самоблокировка утилиты (11) · Самоисправление OCR → «Латинский нюх» (8) · Самопроверка (11) · Сдержанное движение → Запрет движения (4) · Семантическая маска → Безмасочная правка (2) · Семантический негатив → Позитивная замена запрета (2) · Семейство форматов → Аутпейнт (6) · Серый оверлей 4:0:0 (7) · Сетка 2×2 → Набор одним вызовом (3) · Синемаграф (4) · Синтетический исполнитель (9) · Скачок постер → видео → Теги цвета (7) · Сквозной параметр (10) · Скилл вендора (2) · Склейка по маске → Синемаграф (4) · Скрим (7) · Слепая пара (11) · Слова качества (2) · Слой текста (8) · Слой тени (7) · Слоп (3) · Слот (1) · Слоты промта → Блок стиля серии (3) · Служебный запрет (2) · Смешанная правка (2) · Снимок каталога (11) · Согласованность повторов → Позиционный сдвиг (8) · Сохранение движения (7) · Сохранность вне цели (8) · Спецификация ассета (2) · Список правки MP4 → Нормализация выхода модели (4) · Сразу вердикт → VLM-судья (8) · «Средний вид» (3) · Срез арены → Арена (8) · Срок жизни результата (10) · Ставка за секунду → Единица цены (10) · Стандартная правка (9) · Статичный коллапс (4) · Стенд моделей (11) · Стилевой референс (3) · Стиль-код → Стилевой референс (3) · Стопка альфы → Stacked alpha (7) · Ступени разрешения и качества (1) · Ступень разрешения → Ступени разрешения и качества (1) · Ступень цены (10) · Суффикс сохранения → Оберег (2) · Сухой прогон (10) · Сфабрикованные негативы (8) · Сходство со знаменитостью → Проверка сходства (9)

**Т**: Таймкод-промтинг (4) · Теги цвета (7) · Телефонный мастер (7) · Тёплый сдвиг → Маркер сгенерированности (3) · Территориальная лицензия → Лицензии открытых весов (9) · Тихая петля → Петля [A,A] (4) · Токенная цена → Единица цены (10) · Трансграничная передача ПДн (9) · Трассировка → Векторизация (5) · Триаж новой модели (11) · Троттлинг на запрос → Приёмка страницы (7)

**У**: Удаление фона (6) · Узнаваемость метафоры (5) · Уменьшение движения (7) · Уровень качества → Ступени разрешения и качества (1) · Уровень плана (11) · Утечка правки (6)

**Ф**: Фаза 0 → Фаза 5 (11) · Фаза 5 (11) · Фильтр до голосования (11) · Финальный вариант → Вариант маршрута (11) · Флаг лицензии → Вариант маршрута (11) · Фокусная точка (3) · Фоновое движение → Перечень фонового движения (4) · Функциональный артефакт (3)

**Х**: Хромакей (6) · Худший случай → Уровень плана (11) · Хэш запроса (10)

**Ц**: Цвет ключа → Хромакей (6) · Цвет секции (3) · Цветность (8) · Цветовой сдвиг → Дрейф цвета (6) · Целевое значение → Правка по инструкции (2) · Ценность на рубль → Уровень плана (11) · Ценовой параметр (10) · Центр масс значимости → «Средний вид» (3) · Цепочка клипов (4) · Цепочка прав (9) · Цепочка правок → Многоходовая правка (2)

**Ч**: Чекпойнт → Регрессионные ворота (11) · Черновой режим (1) · Чистая подложка (6)

**Ш**: Шаблон эффекта (2) · Шов петли (4) · Шов текстуры (6)

**Э**: Эло → Модель Брэдли–Терри (8) · Энтропия картинки для LCP (7) · Эстетика по умолчанию → «Средний вид» (3) · Эталон серии (3) · Эталонная альфа → Удаление фона (6) · Эффект Instagram-фильтра (3) · Эффективный курс (10)

**Я**: Якорная картинка → Эталон серии (3)

**A–Z**: All-intra (4) · C2PA (9) · CFG → Негативный промт (2) · CLIPScore → Метрики соответствия тексту (8) · Content Credentials → C2PA (9) · Content-эндпоинт (10) · CRF (6) · `currentColor` (5) · Digital Source Type (9) · DOM-проверка вёрстки (8) · DSG (8) · F83 (7) · FID → Метрики соответствия тексту (8) · FLF → Первый и последний кадр (4) · GNED (8) · Hero (1) · Hero-пара → Телефонный мастер (7) · i2v-контроль → «Живость» (4) · IR MiniMax → Диалект промта (2) · JPEG XL (6) · JSON-промт (2) · LCP (7) · LLM-фронт → Класс входа модели (2) · LoRA → Открытые веса (1) · Lottie (5) · LQIP (7) · «No X» в прозе (2) · nowrap-флекс-элемент → DOM-проверка вёрстки (8) · OG-картинка → Карточка ссылки (7) · Sidecar-манифест (9) · SMIL (5) · SSIMULACRA2 (6) · Stacked alpha (7) · SVG кодом (5) · SVG-спрайт → `currentColor` (5) · SynthID → Невидимый водяной знак (9) · t2v, i2v, v2v (4) · «Valid» и «Trusted» (9) · VLM-судья (8) · VP9-alpha → Видео с альфой (7) · VQAScore → Метрики соответствия тексту (8)

**Прочее**: 2.5D → Параллакс слоёв (6) · 243-ФЗ (9) · ΔE (3) · ΔE палитр → Пороги серии (3)
