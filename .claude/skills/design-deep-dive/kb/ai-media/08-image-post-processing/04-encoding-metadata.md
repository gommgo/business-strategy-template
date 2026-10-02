# Кодирование картинок и метаданные: AVIF/WebP/JPEG XL, качество против веса, EXIF/XMP/ICC, C2PA при оптимизации

Волна 2 · агент H (итоговые файлы — продолжатель H2) · 23.09.2026 · опыты: H/04a (4 кодера × 4–5 уровней × 3 картинки,
SSIMULACRA2), H/04b (C2PA, XMP, EXIF, ICC после 17 операций), H/05b (бандинг — `03-…` §3) · источников: 24 (≈ 20 — через
выжимку помощника H по кодированию и C2PA, первоисточники в `99-raw/cache/`; chromestatus, chromiumdash и caniuse сверены
H2) · каталог polza 2026-09-23. Доставка на страницу (`<picture>`, `srcset`, LCP) — J (`../10-web-integration/`); право и
маркировка — L (`../12-legal-provenance/`).

## Выжимка для агента

1. **Выход модели никогда не публиковать как есть**: PNG 1024² гладкого рендера 662 КБ → AVIF q40 4,6 КБ при SSIMULACRA2
   80,7 (в 144 раза меньше) → §1.1 [проверено: 99-raw/experiments/H/04-encoding-metadata; A `01/02` §6.1].
2. **Качество задавать порогом метрики, а не числом `quality`**: SSIMULACRA2 ≥ 80 — hero и крупные фото (искажения не видны
   при сравнении рядом), ≥ 70 — второстепенные; подбор — `../../scripts/ai-media/avif_pick.sh` → §1.2 [документация SSIMULACRA2;
   проверено: утилита].
3. **Шкалы `quality` у кодеров несовместимы**: Pillow AVIF q60 = 4,5 КБ / 80,7 на рендере, но 179 КБ / 79,6 на ткани (avifenc
   q60: 7,2 / 84,2 и 143 / 77,3) → не переносить «q=60» между инструментами → §1.2 [проверено].
4. **Гладкий ИИ-рендер и фон — AVIF q40–50 (≈ 5–6 КБ на 1 Мп)**; WebP q80–90 как запасной (9–17 КБ); JPEG — только
   последний запасной → §1.1 [проверено].
5. **На ВЧ-фактуре (ткань, листва, волосы) выигрыш форматов почти исчезает** (±15 % при ≥ 70); **WebP на высоком качестве
   хуже JPEG** (358 против 238 КБ при ≥ 80) → для фактур AVIF q60–70 или JPEG, не WebP q90 → §1.1 [проверено].
6. **Для «без потерь на глаз» (≥ 90) — только JPEG XL d ≤ 0,5 или PNG**: AVIF 4:2:0 упирается в 84–88 (q80), WebP и JPEG
   при q90 — 83–88 → §1.1 [проверено].
7. **avifenc из PNG по умолчанию кодирует 4:4:4** (`-y auto`) — для веба на фото задавать `-y 420` явно (H/04a), для графики
   с цветными тонкими краями — 4:4:4 → §1.3 [документация avifenc].
8. **JPEG XL включается в Chrome 155 по умолчанию** (chromestatus: «Will ship enabled for all users», M155 на десктопе,
   Android, WebView; стабильный Chrome 155 — **06.10.2026**); сегодня полная поддержка 0 %, частичная 15 % (Safari 17+) →
   правило A «JPEG XL не использовать» устаревает через 2 недели → §2 [документация, 23.09.2026].
9. **JXL — только первым необязательным `<source>`**, никогда единственным форматом; выгоден на волосах и фактурах (40 против
   51 КБ AVIF при ≥ 80) и для ≥ 90 → §2 [проверено: H/04a; документация].
10. **C2PA теряется при любом перекодировании и ресайзе** (Pillow, cwebp даже с `-metadata all`, avifenc, cjxl, ffmpeg) —
    жёсткая привязка по спецификации не переживает производные → §4.1 [проверено: H/04b; документация C2PA 2.4].
11. **Правка одного поля XMP ломает подпись** (`assertion.dataHash.mismatch`) — метаданные подписанного мастера не трогать
    → §4.1 [проверено].
12. **Правильная производная — новый манифест с исходником-ингредиентом** (`c2patool -p`, действие `c2pa.transcoded`) —
    Valid, но манифест весит 56–113 КБ — в 3–20 раз больше самой веб-картинки → встроенный манифест на страницу не тащить → §4.2
    [проверено].
13. **Мастер с манифестом вендора хранить побайтно**; на страницу — производные без встроенного манифеста или с sidecar
    `.c2pa` (файл картинки не меняется, манифест 13,8 КБ отдельно) → §4.3 [проверено: H/04b; решение — L].
14. **`c2patool -r URL` не делает файл лёгким**: пишет ссылку в XMP и всё равно встраивает манифест (+14,5 КБ) → §4.2
    [проверено: H/04b, c2patool 0.27.22].
15. **CDN, которые переносят C2PA сами**: Cloudflare Images «Preserve Content Credentials» (дописывает и подписывает действия;
    выключено → «always discarded»), Fastly IO `metadata=c2pa` (все форматы, кроме JPEG XL); imgix — удаляет → §4.4
    [документация].
16. **IPTC `DigitalSourceType` в XMP — лёгкая машиночитаемая пометка ИИ** (≈ 1 КБ): `trainedAlgorithmicMedia` — создано ИИ,
    `compositeWithTrainedAlgorithmicMedia` — правка ИИ; сохраняют avifenc, cjxl, `cwebp -metadata all`; Pillow и ffmpeg —
    теряют → §3 [документация IPTC; проверено: H/04b].
17. **Pillow пишет EXIF и ICC только если передать `exif=` и `icc_profile=`**; WebP через Pillow теряет ICC; cjxl кодирует
    цвет перечислением (exiftool показывает «нет ICC», цвет при этом верен) → §3 [проверено].
18. **Кодирование — последним шагом**: генерация → (апскейл) → правки → грейд → лестница размеров → кодирование →
    метаданные/C2PA → §5 [практика; A `01/01` §4.2].
19. **Дизеринг до сжатия бандинг не лечит** — шум поверх после декодирования → `03-color-tiling-depth-layers.md` §3
    [проверено].

## 1. Формат и качество

### 1.1 Замер H/04a: минимальный вес для порога SSIMULACRA2 (КБ)

| Картинка (PNG) | Порог | JPEG (Pillow) | WebP (cwebp -m 6 -sharp_yuv) | AVIF (avifenc -s 6, 4:2:0) | JPEG XL (cjxl -e 7) |
|---|---|---|---|---|---|
| рендер 1024², гладкие градиенты (662 КБ) | ≥ 70 | 17 | 7 | **5** | 10 |
| | ≥ 80 | 25 | 17 | **5** | 10 |
| | ≥ 90 | — (q90: 86,1) | — (q90: 82,9) | — (q80: 85,3) | — (d0,5: 89,9 / 35,7 КБ) |
| мешковина 1024², ВЧ-фактура (1 932 КБ) | ≥ 70 | 158 | 136 | 143 | **132** |
| | ≥ 80 | 238 | **358** | **212** | 231 |
| | ≥ 90 | — | — | — | **459** |
| волосы 640² (540 КБ) | ≥ 70 | 37 | 29 | 27 | **24** |
| | ≥ 80 | 75 | 56 | 51 | **40** |
| | ≥ 90 | — | — | — | **95** |

- Кодирование ≤ 0,4 с на 1 Мп у всех кодеров (`-j 4`) [проверено].
- Web Almanac 2024 (медианы bpp): GIF 6,7, PNG 3,8, JPEG 2,0, AVIF 1,4, WebP 1,3; доли картинок: JPEG 32,4 %, PNG 28,4 %,
  WebP 12 %, AVIF 1,0 % [документация: Web Almanac 2024 Media]; у лидеров PNG — 54 % байт картинок из-за ИИ-продуктов, AVIF — у
  19 из 43 сайтов, у русских — 0 из 5 [проверено: A `01-web-assets-landscape/02-live-sites-measured.md` §6.1].

### 1.2 Порог и подбор качества

| SSIMULACRA2 | Смысл (README cloudinary/ssimulacra2) | Где на сайте |
|---|---|---|
| 90 | визуально без потерь (flicker test) | мастер, скачиваемые файлы, товар для зума |
| 85 | отлично: не видно при сравнении на месте | hero-продукт, крупный товар |
| **80** | очень высоко: не видно при сравнении рядом | **hero, крупные фото (позиция H)** |
| **70** | высоко: артефакты заметны рядом, но не раздражают | **второстепенные, карточки, фоны секций** |
| 50 | средне | превью, заглушки LQIP |

```bash
# avif_pick.sh · avifenc 1.4.2 + ssimulacra2 (libjxl 0.12.0) · [проверено: рендер 1024² → q40, 4,7 КБ, 80,7; волосы 640² → q75, 43 КБ, 81,5]
99-raw/tools/avif_pick.sh in.png out.avif 80      # перебор q 35…85, первый q с s2 ≥ порога
```

- Качество выбирать на **классе** картинок (рендер, фото-фактура, волосы, иллюстрация) по таблице §1.1, для hero — подбором
  по конкретному файлу; Squoosh по умолчанию: AVIF q50, WebP q75, JXL q75 [документация Squoosh].
- `quality` Pillow ≠ `-q` avifenc: на рендере Pillow q60 ≈ avifenc q40, на ткани Pillow q60 ≈ avifenc q65 — калибровать
  своим инструментом [проверено].

### 1.3 Команды (проверены в H/04a)

```bash
# avifenc 1.4.2 (aom 3.14.1) · cwebp 1.6.0 · cjxl 0.12.0 · Pillow 11.3 · [проверено]
B=99-raw/tools/bin
$B/libavif/avifenc -q 50 -s 6 -y 420 -j 4 in.png out.avif          # фото, рендер; -y auto из PNG = 4:4:4 (тяжелее)
$B/libwebp/cwebp -q 80 -m 6 -sharp_yuv in.png -o out.webp          # запасной; по умолчанию -q 75 -m 4 -metadata none
$B/libjxl/tools/cjxl in.png out.jxl -d 1 -e 7 --num_threads 4      # -d 1 ≈ визуально без потерь; -d 2 — «for web» (man cjxl)
python3 -c "from PIL import Image; Image.open('in.png').save('out.avif', quality=60, speed=6)"   # Pillow AVIF: своя шкала
```

- Прозрачность: AVIF и WebP с альфой; качество альфы у avifenc — отдельный `--qalpha` [документация avifenc]; замер альфы по
  весу и ореолу — не делался (вопрос J).
- avifenc 1.4.x: скорость по умолчанию 6; `tune=iq` (с 1.4.0) — режим под метрики качества картинки [документация libavif
  CHANGELOG; не проверено].

## 2. JPEG XL: статус на 23.09.2026

| Источник | Что говорит |
|---|---|
| chromestatus 5114042131808256 (обновлено 31.08.2026) | «JPEG XL decoding support (image/jxl) in blink» через jxl-rs (Rust); отгрузка **M155** на десктопе, Android, WebView; «Will ship enabled for all users»; флаг `enable-jxl-image-format`; статус Proposed |
| chromiumdash, расписание M155 | ранний стабильный — 23.09.2026, **стабильный — 06.10.2026** |
| caniuse `jpegxl` (снят 23.09.2026) | полная поддержка 0 %, частичная 15,02 %: Safari 17+ и iOS 17+ (без прогрессивного декодирования и анимации); Chrome 145–148 — за флагом; Firefox — флаг `image.jxl.enabled` (в Nightly по умолчанию) |
| Fastly IO (04.08.2026) | C2PA-проброс для всех форматов, **кроме JPEG XL** |

- Правило A (`../01-web-assets-landscape/01-asset-slots-by-page-type.md` §4.3: «JPEG XL — не использовать, 0 % полной
  поддержки») верно на 23.09.2026 и **устаревает с 06.10.2026** — поправка для аудитора X и синтезатора S, файл A здесь не
  правится.
- Позиция H с 06.10.2026: `<picture>` — `image/jxl` (необязательно, первым) → `image/avif` → `image/webp` → JPEG; JXL — где он
  выигрывает по H/04a (волосы, фактуры, ≥ 90), не везде; единственным форматом — никогда (Firefox, старые Chrome).
- JPEG → JXL без потерь (`cjxl` по умолчанию для JPEG-входа) обратим побайтно (`djxl` восстанавливает исходный JPEG — даже
  C2PA снова Valid), но в самом JXL c2patool манифест не видит [проверено].

## 3. EXIF, XMP, ICC: что выживает

| Операция (H/04b) | C2PA | XMP DigitalSourceType | EXIF | ICC |
|---|---|---|---|---|
| Pillow: JPEG → JPEG, → WebP, ресайз | нет | нет | нет | нет |
| Pillow с `exif=`, `icc_profile=` | нет | нет | да | да |
| Pillow → AVIF | нет | нет | нет | да |
| cwebp по умолчанию / `-metadata all` | нет / нет | нет / да | нет / да | нет / да |
| avifenc (из PNG или JPEG) | нет | да | да | да |
| cjxl `-d 1` / JPEG → JXL без потерь | нет | да | да | нет (цвет — перечислением) |
| exiftool `-all=` | нет | нет | нет | нет |
| ffmpeg → JPEG / → WebP | нет | нет | нет | да / нет |

- IPTC Digital Source Type: `http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia` («Created using
  Generative AI»), `…/compositeWithTrainedAlgorithmicMedia` («Edited using Generative AI»); IPTC 2025.1 добавил поля
  `AISystemUsed`, `AIPromptInformation`; значение `digitalArt` выведено IPTC из употребления 17.09.2024 — а пример манифеста
  c2patool его использует → брать `trainedAlgorithmicMedia` [документация IPTC; противоречие].
- Записать пометку в производную (0 ₽, ≈ 1 КБ): `exiftool -XMP-iptcExt:DigitalSourceType=http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia out.avif`
  [проверено: H/04b — так размечен исходник опыта].
- ICC: у 87,7 % картинок веба ICC нет [Web Almanac 2024]; ИИ-выход — sRGB → профиль не обязателен, но Pillow → WebP его молча
  теряет: для не-sRGB мастеров (Display P3) передавать `icc_profile=` явно.
- EXIF со служебными полями генератора (Software, промт) — вопрос приватности и провенанса одновременно → политика — L.

## 4. C2PA при оптимизации

### 4.1 Почему манифест не переживает производные

- Жёсткая привязка (hard binding): хэш данных картинки «can match only this asset… not even renditions» → любой ресайз или
  перекодирование = `*Hash.mismatch` [документация C2PA 2.4].
- Где манифест лежит: JPEG — APP11 (JUMBF, сегменты ≤ 64 КБ); PNG — чанк `caBX` до IDAT; WebP — RIFF-чанк `C2PA`; AVIF/HEIF —
  бокс `uuid` после `ftyp`; JPEG XL — бокс `jumb` (в «голый» codestream нельзя); SVG — `<metadata>` (предпочтителен внешний)
  [документация C2PA 2.4].
- Guidance 2.2 §4.2.1: платформы «routinely» удаляют манифест у производных [документация].
- Мягкая привязка (soft binding, водяной знак) — реестр из 28 алгоритмов (TrustMark, Digimarc, InvisMark…); **SynthID в
  реестре нет** [документация: C2PA soft-binding list].

### 4.2 Опыт H/04b: подпись и производные (c2patool 0.27.22, тестовый сертификат)

| Файл 512² | Вес | Статус |
|---|---|---|
| JPEG без манифеста / с манифестом | 19,2 / 75,0 КБ (+55,9 КБ, 74 % файла) | Valid (`signingCredential.untrusted` — тестовый сертификат) |
| AVIF-производная без манифеста | 5,7 КБ | манифеста нет |
| AVIF + новый манифест с родителем `-p` | 119,1 КБ (+113 КБ, 95 % файла) | Valid, 1 ингредиент |
| AVIF + sidecar `-s` | 5,7 КБ + `side.c2pa` 13,8 КБ | Valid (c2patool находит файл рядом); картинка не изменилась ни на байт |
| AVIF + `-r URL` | 20,3 КБ | ссылка в XMP `dcterms:provenance` **и** встроенный манифест |

```bash
# c2patool 0.27.22 (99-raw/tools/bin/c2patool/) · тестовый ES256 встроен — для продакшна нужен свой сертификат · [проверено]
C2=99-raw/tools/bin/c2patool/c2patool
$C2 master.png -c manifest.json --create trainedAlgorithmicMedia -o master_signed.png -f   # подписать мастер (created)
$C2 page.avif -c transcoded.json -p master_signed.png -o page_signed.avif -f               # производная: ингредиент-родитель
$C2 page.avif -c transcoded.json -p master_signed.png -s -o page.avif -f                   # sidecar page.c2pa, AVIF не меняется
$C2 page_signed.avif                                                                         # чтение: JSON, validation_state
```

`manifest.json` — `{"claim_generator_info":[{"name":"…","version":"…"}],"title":"…","assertions":[{"label":"c2pa.actions",
"data":{"actions":[{"action":"c2pa.created","digitalSourceType":"http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"}]}}]}`;
для производной — действие `c2pa.transcoded` (или `c2pa.resized`, `c2pa.edited`) без `digitalSourceType`.

### 4.3 Что делать на сайте (позиция H; обязательность — L: `../12-legal-provenance/02-labeling-ai-act-provenance.md` §5)

1. Выход модели с манифестом вендора — **хранить побайтно** как мастер (не открывать и не пересохранять Pillow).
2. Правки, грейд, апскейл — делать с копии; если нужна своя цепочка провенанса — подписать новый мастер с исходником вендора
   как ингредиентом.
3. На страницу — производные лестницы `srcset` **без встроенного манифеста** (вес) + XMP `DigitalSourceType` (≈ 1 КБ) +
   видимая маркировка, если требует L; манифест — sidecar `.c2pa` рядом с мастером или производной, ссылкой из разметки.
4. Если CDN умеет переносить C2PA (Cloudflare, Fastly) — отдавать ему подписанный мастер и включить сохранение: CDN сам
   допишет и подпишет действия трансформации.
5. [поправка фазы 5, 25.09.2026: метка вендора — не константа канала: из 254 выходов фазы 5 OpenAI через polza — C2PA Trusted 71 из 73
   (2 без метки — кадры 2736×1536 при «2K»), Google через `mie` — через раз (NB2 8 из 19, NB Pro 1 из 5), Seedance 1.5 Pro, Z-Image,
   Qwen 2.1, Krea 2 — ничего → XMP `DigitalSourceType` на каждую производную обязателен; SVG Recraft через RouterAI несёт C2PA в
   `<metadata>` (17,7 КБ), после чистки путей — `Invalid`, svgo `preset-default` удаляет → мастер SVG — побайтно, на страницу — без
   `<metadata>`, провенанс — паспорт → `99-raw/experiments/L/05-phase5-provenance/2026-09-25-all/README.md`]

### 4.4 Кто подписывает и кто сохраняет (выжимка помощника H, первоисточники в кэше)

| Кто | Что делает | Дата |
|---|---|---|
| OpenAI API (GPT Image) | C2PA + SynthID; «Conforming Generator» | 19.05.2026 |
| Google (NB Pro, NB2 Lite) | SynthID всегда + C2PA | с 20.11.2025 (NB Pro) |
| BFL API (FLUX.2) | подписанный C2PA | [документация] |
| Adobe Firefly | Content Credentials при 100 % сгенерированных пикселях | [документация] |
| Midjourney | только IPTC DigitalSourceType | [вторичный источник] |
| Cloudflare Images | «Preserve Content Credentials»: сохраняет, дописывает действия и подписывает; выключено — «always discarded» | 03.02.2025 |
| Fastly Image Optimizer | `metadata=c2pa`: проброс и переподпись для всех форматов, кроме JPEG XL, спецификация 2.4, бесплатно | 04.08.2026 |
| Cloudinary | `fl_c2pa` — бета по запросу | 12.03.2026 |
| imgix | «strip most metadata» — C2PA нет | — |
| Adobe AEM Dynamic Media | переподпись производной с оригиналом-ингредиентом | 26.08.2026 |

- Любой ffmpeg выбрасывает C2PA Google и из видео [проверено] — то же для картинок (H/04b); для видео — I и L.

## 5. Порядок конвейера

генерация (ступень разрешения под слот) → сохранить оригинал вендора побайтно (C2PA, SynthID) → (апскейл Lanczos/генеративный,
`02-…` §1) → правки + `edit_check.py` + композит → грейд одним `.cube` (`03-…` §1) → мастер PNG/16 бит → лестница ширин
`srcset` (640 … 3840, A `01/01` §4.2) → AVIF (+ WebP; + JXL после 06.10.2026) с порогом SSIMULACRA2 → XMP `DigitalSourceType`
→ C2PA: sidecar или CDN с сохранением (решение L) → зерно/шум — CSS поверх, не в файле.

## Частые ошибки

- Публиковать PNG модели (1–9 МБ) в слот 400 px; «4K-обои» NB Pro 8,7 МБ без перекодирования [V:y-RQ48sfPgM 32:36].
- Одно число `quality` для всех картинок и всех кодеров.
- WebP q90 для фактур «ради качества» — тяжелее JPEG.
- Подложка JPEG 60 % вместо AVIF [V:BVMuRw8BgJg 02:02] — вдвое тяжелее при том же качестве.
- Пересохранить подписанный файл Pillow «для оптимизации» и считать, что маркировка на месте.
- Поправить XMP подписанного мастера (Title, ключевые слова) — подпись недействительна.
- Удалить видимую маркировку кропом [V:ttgNFJ25xfU 50:58] — у Google SynthID + C2PA остаются в пикселях и манифесте.
- **Ошибки нейросетей-агентов**: «JPEG XL не поддерживается браузерами» после 06.10.2026 (и «поддерживается везде» — до);
  «cwebp `-metadata all` сохраняет C2PA» (нет); «`-r URL` — лёгкий удалённый манифест» (встраивает); `digitalArt` для
  ИИ-картинок (устарел; `trainedAlgorithmicMedia`); перенос шкалы `quality` Pillow на avifenc; «SynthID — часть C2PA».

## Чек-лист

- [ ] Выход модели перекодирован; формат по классу картинки (§1.1), качество — порогом SSIMULACRA2 (≥ 80 hero, ≥ 70 прочее)?
- [ ] avifenc: `-y 420` для фото задан явно (или осознанно 4:4:4 для графики)?
- [ ] JXL — только первым необязательным `<source>` и только после 06.10.2026?
- [ ] Оригинал вендора с C2PA сохранён побайтно?
- [ ] На производной есть XMP `DigitalSourceType` (`trainedAlgorithmicMedia` / `compositeWithTrainedAlgorithmicMedia`)?
- [ ] Встроенный манифест не раздувает веб-картинку (sidecar или CDN с сохранением)?
- [ ] Для не-sRGB мастеров ICC передан явно?

## Открытые вопросы и противоречия

- Что обязательно по ст. 50 AI Act для картинок сайта: встроенный C2PA, sidecar, XMP или видимая пометка — решено L
  (`../12-legal-provenance/02-labeling-ai-act-provenance.md` §5.1: мастер побайтно; производные — XMP `DigitalSourceType`;
  ЕС + дипфейк — видимая метка + sidecar или CDN с Content Credentials) [поправка X 24.09.2026].
- Настоящие манифесты вендоров (OpenAI, Google, BFL) на наших файлах не проверялись (нет генераций) — фаза 5: на каждом
  выходе `c2patool` + `exiftool` (K, L).
- Fastly не пробрасывает C2PA в JPEG XL — провенанс и JXL пока конфликтуют.
- Вес и ореол AVIF/WebP с альфой (`--qalpha`) — не мерили (J).
- `tune=iq` avifenc 1.4 — выигрыш по SSIMULACRA2 на ИИ-рендерах не мерили.
- Мерцание качества при перекодировании производной из уже сжатой (AVIF → AVIF) — не мерили; правило — всегда из мастера.

## Источники

- [S1] H/04 — `99-raw/experiments/H/04-encoding-metadata/` (README, `curves.md`, `encode_results.json`, `c2pa_table.md`,
  `c2pa_results.json`, `work_c2pa/`) — качество против веса и выживание метаданных.
- [S2] cloudinary/ssimulacra2 — README (кэш `raw.githubusercontent.com_cloudinary_ssimulacra2_main_README.md_9174d02b.md`) —
  шкала 10/30/50/70/80/85/90 с соответствием cjxl и libjpeg.
- [S3] HTTP Archive, Web Almanac 2024 Media (кэш `almanac.httparchive.org_en_2024_media_9b3000a3.md`) — доли форматов, bpp,
  ICC, `sizes`.
- [S4] caniuse `jpegxl.json` (снят 23.09.2026, кэш `…features-json_jpegxl.json_fresh_2026-09-23H_9b692f08.md`) — поддержка
  0 % / 15,02 %, примечания о флагах.
- [S5] chromestatus.com, фича 5114042131808256 (кэш `chromestatus.com_api_v0_features_5114042131808256_cc9c719d.md`, обновлено
  31.08.2026) — отгрузка JPEG XL в M155.
- [S6] chromiumdash, `fetch_milestone_schedule?mstone=155` (снят H2 23.09.2026, кэш
  `99-raw/cache/chromiumdash.appspot.com_fetch_milestone_schedule_mstone155_2026-09-23.json`) — стабильный 06.10.2026.
- [S7] libavif — `doc/avifenc.1.md` и CHANGELOG (кэш) — `-y auto` = 4:4:4 для PNG, `--qalpha`, скорость 6, `tune=iq`.
- [S8] Google — cwebp docs (кэш `developers.google.com_speed_webp_docs_cwebp_49b25afd.md`) — `-m` 4, `-sharp_yuv`,
  `-metadata`.
- [S9] libjxl — `doc/man/cjxl.txt` (кэш) — `-d 1` визуально без потерь, `-d 2` для веба, `-e 7` по умолчанию.
- [S10] GoogleChromeLabs/squoosh — умолчания кодеров (кэш `…squoosh_dev_src_features_encoders_*`).
- [S11] C2PA Specification 2.4 (кэш `spec.c2pa.org_specifications_specifications_2.4_specs_C2PA_Specification.html_6c099c78.md`)
  — места встраивания, hard binding, ингредиенты и действия.
- [S12] C2PA Guidance 2.2 (кэш `spec.c2pa.org_…_2.2_guidance_Guidance.html_457a4e88.md`) — удаление манифестов у производных.
- [S13] C2PA soft-binding algorithm list (кэш `spec.c2pa.org_softbinding-alg-list_…json`) — 28 алгоритмов, SynthID нет.
- [S14] contentauth/c2patool — README, docs usage/manifest (кэш `raw.githubusercontent.com_contentauth_c2patool_main_*`);
  v0.28.0 вышла 22.09.2026 в отдельном репозитории, у нас 0.27.22 из c2pa-rs.
- [S15] Cloudflare — «Preserve Content Credentials» (кэш `developers.cloudflare.com_images_optimization_transformations_preserve-content-credentials_79a6fe3b.md`).
- [S16] Fastly — блог «Trust at scale… C2PA» и сообщество «C2PA support enhancements…» 04.08.2026 (кэш `www.fastly.com_blog_*`,
  `community.fastly.com_t_c2pa-support-*`).
- [S17] Cloudinary — Content provenance docs (кэш `cloudinary.com_documentation_content_provenance_and_authenticity_6b60e286.md`).
- [S18] imgix rendering overview; Adobe AEM Dynamic Media Content Credentials (кэш `docs.imgix.com_*`,
  `experienceleague.adobe.com_*`).
- [S19] IPTC NewsCodes Digital Source Type и Photo Metadata Standard 2025.1 (кэш `cv.iptc.org_newscodes_digitalsourcetype_*`,
  `iptc.org_std_photometadata_specification_IPTC-PhotoMetadata_fc9eba85.md`).
- [S20] OpenAI Help «C2PA in ChatGPT Images» (кэш `help.openai.com_en_articles_8912793-c2pa-in-chatgpt-images_01fc244e_r.md`);
  Google SynthID (кэш `ai.google.dev_responsible_docs_safeguards_synthid_635d306f.md`); Adobe Firefly Content Credentials (кэш
  `helpx.adobe.com_*`).
- [S21] C2/02 — `99-raw/experiments/C2/02-vendor-output-ffprobe/` — ffmpeg выбрасывает C2PA Google из видео.
- [S22] A — `../01-web-assets-landscape/01-asset-slots-by-page-type.md` §4, `02-live-sites-measured.md` §6.1 — форматы и замеры
  лидеров.
- [S23] Google — jpegli (кэш `opensource.googleblog.com_2024_04_introducing-jpegli-…`) — +35 % сжатия JPEG на высоком качестве,
  10+ бит; в опытах не использовался.
- [S24] Netflix CAMBI — `03-color-tiling-depth-layers.md` §3.
- Дайджесты: [V:y-RQ48sfPgM 32:36] 4K-обои 8,7 МБ; [V:BVMuRw8BgJg 02:02] подложка JPEG 60 %; [V:ttgNFJ25xfU 50:58] удаление
  знака кропом.
