# Тестовые страницы J — шаблоны доставки ИИ-ассетов (проверены в Chromium 153)

Агент J, волна 3, 23.09.2026. Каждая страница самодостаточна (относительные пути, без внешних зависимостей, системный шрифт),
открывается локально и проходит `../../scripts/ai-media/page_accept.py` на десктопе 1440×900 и Pixel 7 (кроме 02b — провал по WCAG 2.2.2
намеренно показан). Замеры — `99-raw/experiments/J/06-pages-measure/summary.md`. Материалы — CC0 (панорамы Poly Haven
`lakeside_dawn`, `lakeside_night` — Greg Zaal, Jarod Guest) и наши рендеры Blender (агенты H, I); сгенерированных моделью
ассетов здесь нет — в фазе 5 они подставляются 1:1 по именам файлов.

## Страницы

| Файл | Что показывает | Главные числа (J/06) |
|---|---|---|
| `00-hero-summary.html` | **канонический шаблон**: `<picture>` с телефонным кадром (постер = кадр 0 видео) → видео-слой после `load` → светлый скрим → зерно → кнопка паузы; lazy-карточки `sizes="auto"`, CTA-полоса CSS-градиентом, OG, фавиконы | LCP постер 144 / 108 мс; 619 / 310 КБ; reduce 0 КБ видео; F83 ≥ 6,2 |
| `01-image-hero.html` | картинка-hero: AVIF → WebP, `srcset` 640–2560, `<source media width height>` 4:5, `object-position` по фокусу (`js/focal.js`), LQIP (цвет + 32-px WebP) | LCP hero 104 / 88 мс; 129 / 117 КБ |
| `02-video-hero.html` | видео-hero: AV1 → H.264, телефону 4:5 720, reduce/Save-Data/2G → 0 байт, пауза (WCAG 2.2.2), пауза вне экрана (`js/hero-video.js`) | 594 / 253 КБ; постер↔кадр 0 ΔE00 1,0–1,2 |
| `02b-video-source-media.html` | вариант без JS: `<source media="(prefers-reduced-motion: no-preference) and …">` | reduce 0 байт, но FAIL: нет паузы, постер один |
| `03-alpha-object-hero.html` | парящий объект: stacked alpha (AV1/HEVC/H.264) → WebGL2 (`js/stacked-alpha.js`), статичный AVIF с альфой, параллакс слоёв `animation-timeline: scroll()`, движение ≤ 5 с | 115 / 98 КБ (видео 12,5 КБ) |
| `04-two-states-spotlight.html` | две петли (ночь/рассвет), прожектор `mask-image` за курсором, кнопка состояния для касаний, вторая петля — по взаимодействию (`js/spotlight.js`) | 598 / 226 КБ; F83 ≥ 5,1 в обоих состояниях |
| `05-scroll-sequence.html` | оборот товара по прокрутке: AVIF-секвенция → canvas или `?mode=video` (GOP 8, `&src=`) (`js/scroll-seq.js`); reduce — один кадр | 48 кадров 111 КБ |
| `07-effects-grain-layers.html` | зерно поверх (SVG 280 Б), тёмный градиент CSS-ом, 2.5D: объект с альфой + RGB-слой тени multiply на любом цвете секции | 77 КБ |
| `08-svg-icons-favicons.html` | спрайт `<symbol>` + `currentColor`, анимация inline SVG с reduce, `<picture>` статичной копии для SVG в `<img>`, паттерн `mask-image`, фавиконы 3 файла | 12 КБ |

## Модули

| Файл | Строк | Что делает |
|---|---|---|
| `css/base.css` | 72 | токены, hero (`calc(100svh − 64px)` — кандидат LCP), кнопка паузы 44 px, зерно, reduce |
| `js/hero-video.js` | 75 | видео-слой: выбор `data-src` по `data-media` и `canPlayType`, reduce/Save-Data/2G, подмена по `requestVideoFrameCallback`, пауза с памятью, вне экрана, reduce на лету |
| `js/focal.js` | 35 | `object-position` по фокусу (формула F), ключ по соотношению загруженного файла |
| `js/stacked-alpha.js` | 73 | stacked alpha → WebGL2 (премультипликация, LINEAR + полтекселя), бюджет движения ≤ 5 с, статичный запас |
| `js/spotlight.js` | 78 | прожектор, два состояния, вторая петля по взаимодействию, выравнивание петель, одна пауза |
| `js/scroll-seq.js` | 50 | прокрутка: секвенция на canvas или перемотка видео, статистика для замера |

## Ассеты (`assets/`)

| Папка | Что | Как получено |
|---|---|---|
| `hero/` | лестницы AVIF/WebP 16:9 (640–2560) и 4:5 (480–1080), рассвет и ночь, SSIMULACRA2 ≥ 80 | `99-raw/experiments/J/05-assets/make_images.py` |
| `video/` | петли 6 с 1080p и 4:5 720×900, AV1 10 бит и H.264, полные теги BT.709, постеры AVIF/WebP из кадра 0 AV1 | `make_video.py` → `sweep_crf.py` → `finalize_video.py` |
| `alpha/` | бутылка 160×272: stacked AV1/HEVC/H.264, VP9-alpha, статичные AVIF/WebP с альфой | `make_alpha.py` (плиты I/01) |
| `scroll/` | 48 AVIF-кадров оборота + видео GOP 1/8/96 (H.264, AV1) | `make_scroll.py` (I/01 turntable) |
| `layers/` | объект с альфой (деконтаминация края) + RGB-слой тени | `99-raw/experiments/J/07-shadow-layer/make_shadow.py --rgb` |
| `cards/` | 3 кадра 4:3 для lazy-карточек (480/720/960, s2 ≥ 70) | `make_cards.py` |
| `og/` | OG 1200×630 JPEG 102 КБ (HTML-шаблон → скриншот) | `make_og.py` + `og-template.html` |
| `svg/` | фавиконы (ico 32, svg с тёмной темой, apple 180), спрайт, шум, волна | вручную + resvg (`99-raw/experiments/G/svg2png.mjs`) |

## Как адаптировать под новый ИИ-ассет (для M)

1. Картинка: мастер ≥ 2560 (16:9) + отдельный мастер 4:5 → `make_images.py` (порог 80) → заменить файлы в `hero/`,
   `data-focal` — из спецификации ассета (`composition.focal_point`, F `06/03` §5).
2. Видео: выход модели → нормализация (I `09/03` §6) → мезонин → `sweep_crf.py` (`motion_keep ≥ 0,75`) → финалы с полными
   тегами BT.709 → постер из кадра 0 AV1 через Pillow; метки вендора — `-map_metadata 0 -movflags use_metadata_tags+faststart`.
3. Цвет текста и скрим — по зоне кадра, альфа — по проверке `page_accept.py --contrast …` (десктоп, Pixel 7, по кадрам видео).
4. Провенанс — `provenance_check.py stamp` на производных (L); видимая иконка ИИ — только дипфейкам (L `12/02` §7).
5. Приёмка: `run_all.py` / `page_accept.py` — все режимы PASS.

## Запуск локально

```bash
cd 10-web-integration/pages && python3 -m http.server 8080 --bind 127.0.0.1   # открыть http://127.0.0.1:8080/00-hero-summary.html; остановить Ctrl+C
```
(видео с Range: встроенный сервер Python Range не умеет — Chromium всё равно играет; для замеров — `page_accept.py`, у него свой сервер.)
