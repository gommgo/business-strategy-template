<!-- Сводка замера 24.09.2026, скопирована 26.09.2026: имена генератора, вендора и хостинга заменены метками (G, G0, «вендор G», «хостинг-G»), числа не менялись; легенда — README.md этой папки. -->
# E/03 — сводка ui_audit (пресет consumer) и impeccable detect


## По целям (десктоп 1440x900)

- `hn-impress-me`: OK 52 / FAIL 17 (блокеров 0: )
- `hn-macos27`: OK 62 / FAIL 7 (блокеров 0: )
- `hn-windows-xp`: OK 64 / FAIL 1 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g0-atelier-veil`: OK 43 / FAIL 26 (блокеров 2: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1, J5 Нет горизонтальной прокрутки документа)
- `g0-lipstick`: OK 48 / FAIL 20 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g-alba-rituals`: OK 38 / FAIL 30 (блокеров 2: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1, G2 Видимый индикатор фокуса при обходе Tab )
- `g-ceramics`: OK 39 / FAIL 29 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g-cocoa-hills`: OK 43 / FAIL 25 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g-elena-wei`: OK 51 / FAIL 17 (блокеров 2: F1 Цели меньше 24×24 без зазора 4 px, I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g-euro-rail`: OK 48 / FAIL 20 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g-fluid-studio`: OK 43 / FAIL 26 (блокеров 2: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1, G2 Видимый индикатор фокуса при обходе Tab )
- `g-hengmu-catalog`: OK 48 / FAIL 20 (блокеров 0: )
- `g-impressionism`: OK 50 / FAIL 19 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g-lume-archive`: OK 48 / FAIL 21 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g-nexus-auto`: OK 51 / FAIL 17 (блокеров 0: )
- `g-qingjian-paper`: OK 41 / FAIL 28 (блокеров 0: )
- `g-seaview-resort`: OK 46 / FAIL 23 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g-woven-fashion`: OK 39 / FAIL 29 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `g-yanxi-onsen`: OK 49 / FAIL 20 (блокеров 0: )
- `xx-multicurrency`: OK 48 / FAIL 20 (блокеров 1: I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)
- `xx-video-heroes`: OK 45 / FAIL 23 (блокеров 2: F1 Цели меньше 24×24 без зазора 4 px, I1 Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1)

## Частота FAIL по правилам среди образцов G (n = 15, десктоп)

| правило | формулировка | серьёзность | FAIL у G |
|---|---|---|---|
| C2 | Радиусы вне шкалы | полировка | 15/15 |
| C5 | Радиус ≤ 25 % меньшей стороны элемента | полировка | 15/15 |
| E1 | z-index вне шкалы | серьёзно | 15/15 |
| E2 | z-index больше 1500 | серьёзно | 15/15 |
| H2 | Кегли вне шкалы | серьёзно | 15/15 |
| H6 | Дробные line-height в px | полировка | 15/15 |
| A1 | Доля padding/margin/gap из шкалы | серьёзно | 14/15 |
| H10 | text-transform: uppercase / capitalize | полировка | 14/15 |
| B2 | Высоты вне ряда 24/32/36/40/44/48 | серьёзно | 13/15 |
| L2 | «Почти, но не совсем»: пары величин с разницей 1–3 px | полировка | 13/15 |
| L5 | Гарнитур в интерфейсе | полировка | 13/15 |
| G0 | Длительности вне шкалы | полировка | 12/15 |
| A5 | Уникальных значений отступа | полировка | 12/15 |
| H1 | Уникальных размеров шрифта (у элементов с собственным текстом) | серьёзно | 12/15 |
| A2 | Значения, кратные 5 и не кратные 4 («шкала десятками») | серьёзно | 10/15 |
| A3 | Уникальных значений gap | полировка | 10/15 |
| I1 | Контраст текста ≥ 4.5:1 (крупный ≥ 3.0:1) | блокер | 10/15 |
| L3 | Литералы цвета в inline-стилях | полировка | 10/15 |
| G3 | Толщина индикатора ≥ 2 px | серьёзно | 8/15 |
| A4 | Доля дробных значений отступа | полировка | 7/15 |
| K3 | Доля длительностей 300 ms | полировка | 7/15 |
| B5 | Размеры иконок из ряда [16, 20, 24] | полировка | 7/15 |
| H4 | Веса легче 400 | полировка | 6/15 |
| H7 | Интерлиньяж тела в коридоре 1.4–1.65 | полировка | 6/15 |
| I7 | Нейтраль одного семейства (разброс оттенка тонированных серых) | полировка | 5/15 |
| B1 | Уникальных высот контролов | серьёзно | 5/15 |
| K1 | transition: all | полировка | 5/15 |
| H5 | line-height: normal | полировка | 4/15 |
| G5 | Контраст кольца фокуса к элементу ≥ 3:1 | серьёзно | 4/15 |
| I4 | Уникальных цветов фона | полировка | 4/15 |
| B4 | Иконочные кнопки квадратные | полировка | 3/15 |
| B6 | Один набор иконок (один viewBox, одна толщина штриха) | полировка | 3/15 |
| H3 | Уникальных весов шрифта | полировка | 3/15 |
| D2 | Один источник света (одинаковое направление теней) | полировка | 2/15 |
| D4 | Свечения (тень с нулевым смещением и blur > 8) | серьёзно | 2/15 |
| G2 | Видимый индикатор фокуса при обходе Tab (12 остановок) | блокер | 2/15 |
| B3 | Одна высота контролов в горизонтальном ряду | серьёзно | 2/15 |
| H14 | Знак % слитно с числом | полировка | 2/15 |
| L1 | Эмодзи в интерфейсе | серьёзно | 2/15 |
| J2 | Сайдбар в коридоре 200–300 px | серьёзно | 2/15 |
| A6 | Внешний padding контейнера ≥ внутренних зазоров | полировка | 2/15 |
| B7 | Строки одного списка/таблицы одной высоты | полировка | 2/15 |
| J8 | Шапка страницы не выше 120 px | полировка | 2/15 |
| H13 | Английский формат разрядов (1,234) в русском тексте | полировка | 2/15 |
| D1 | Уникальных значений box-shadow | полировка | 1/15 |
| G4 | Индикатор не обрезан предком с overflow | серьёзно | 1/15 |
| F1 | Цели меньше 24×24 без зазора 4 px | блокер | 1/15 |
| H11 | text-align: justify | полировка | 1/15 |
| C1 | Уникальных значений border-radius | полировка | 1/15 |
| C3 | Вложенный радиус не больше внешнего | полировка | 1/15 |
| I1c | Отключённые элементы в коридоре APCA Lc 30–60 (WCAG 1.4.3 их не нормирует, но невидимая кнопка — тоже дефект) | полировка | 1/15 |
| I5 | Уникальных цветов границ | полировка | 1/15 |
| I3 | Уникальных цветов текста | полировка | 1/15 |

## impeccable detect: файлов 44

- `hn-impress-me_1440x900.json`: 9 находок; правила: all-caps-body, bounce-easing, buried-raster, hero-eyebrow-chip, italic-serif-display, layout-transition, undersized-ui-text
- `hn-impress-me_390x844.json`: 0 находок; правила: 
- `hn-macos27_1440x900.json`: 6 находок; правила: bounce-easing, clipped-overflow-container, layout-transition, low-contrast
- `hn-macos27_390x844.json`: 5 находок; правила: bounce-easing, clipped-overflow-container, layout-transition
- `hn-windows-xp_1440x900.json`: 0 находок; правила: 
- `hn-windows-xp_390x844.json`: 0 находок; правила: 
- `g0-atelier-veil_1440x900.json`: 30 находок; правила: bounce-easing, buried-raster, image-hover-transform, kicker-above-heading, low-contrast, overused-font, radial-spotlight-glow
- `g0-atelier-veil_390x844.json`: 32 находок; правила: bounce-easing, buried-raster, image-hover-transform, kicker-above-heading, low-contrast, overused-font, radial-spotlight-glow
- `g0-lipstick_1440x900.json`: 20 находок; правила: all-caps-body, buried-raster, content-hidden-at-rest, cramped-padding, image-hover-transform, low-contrast, overused-font
- `g0-lipstick_390x844.json`: 18 находок; правила: all-caps-body, buried-raster, content-hidden-at-rest, cramped-padding, image-hover-transform, low-contrast, overused-font
- `g-alba-rituals_1440x900.json`: 0 находок; правила: 
- `g-alba-rituals_390x844.json`: 0 находок; правила: 
- `g-ceramics_1440x900.json`: 86 находок; правила: clipped-overflow-container, cream-palette, image-hover-transform, kicker-above-heading, layout-transition, low-contrast, skipped-heading, undersized-ui-text, wide-tracking
- `g-ceramics_390x844.json`: 0 находок; правила: 
- `g-cocoa-hills_1440x900.json`: 50 находок; правила: clipped-overflow-container, cream-palette, image-hover-transform, kicker-above-heading, layout-transition, low-contrast
- `g-cocoa-hills_390x844.json`: 46 находок; правила: clipped-overflow-container, cream-palette, image-hover-transform, kicker-above-heading, layout-transition, low-contrast
- `g-elena-wei_1440x900.json`: 0 находок; правила: 
- `g-elena-wei_390x844.json`: 0 находок; правила: 
- `g-euro-rail_1440x900.json`: 0 находок; правила: 
- `g-euro-rail_390x844.json`: 30 находок; правила: body-text-viewport-edge, content-hidden-at-rest, cream-palette, dark-glow, kicker-above-heading, layout-transition, low-contrast, numbered-section-labels, overused-font
- `g-fluid-studio_1440x900.json`: 46 находок; правила: ai-color-palette, all-caps-body, em-dash-overuse, layout-transition, line-length, low-contrast, marquee, numbered-section-labels, undersized-ui-text, wide-tracking
- `g-fluid-studio_390x844.json`: 52 находок; правила: ai-color-palette, all-caps-body, em-dash-overuse, layout-transition, low-contrast, marquee, numbered-section-labels, tiny-text, undersized-ui-text, wide-tracking
- `g-hengmu-catalog_1440x900.json`: 22 находок; правила: cramped-padding, cream-palette, hero-eyebrow-chip, layout-transition, tiny-text, wide-tracking
- `g-hengmu-catalog_390x844.json`: 22 находок; правила: body-text-viewport-edge, cramped-padding, cream-palette, layout-transition, tiny-text, wide-tracking
- `g-impressionism_1440x900.json`: 0 находок; правила: 
- `g-impressionism_390x844.json`: 0 находок; правила: 
- `g-lume-archive_1440x900.json`: 0 находок; правила: 
- `g-lume-archive_390x844.json`: 7 находок; правила: all-caps-body, buried-raster, cream-palette, gpt-thin-border-wide-shadow, layout-transition, radial-halo
- `g-nexus-auto_1440x900.json`: 4 находок; правила: all-caps-body, layout-transition, overused-font
- `g-nexus-auto_390x844.json`: 7 находок; правила: all-caps-body, body-text-viewport-edge, edge-flush-cards, layout-transition, overused-font
- `g-qingjian-paper_1440x900.json`: 18 находок; правила: cream-palette, em-dash-overuse, layout-transition, low-contrast, organic-clip-path, text-occlusion
- `g-qingjian-paper_390x844.json`: 18 находок; правила: cream-palette, em-dash-overuse, layout-transition, low-contrast, organic-clip-path, text-occlusion
- `g-seaview-resort_1440x900.json`: 13 находок; правила: all-caps-body, hero-eyebrow-chip, kicker-above-heading, layout-transition, low-contrast, tight-leading, wide-tracking
- `g-seaview-resort_390x844.json`: 13 находок; правила: all-caps-body, kicker-above-heading, layout-transition, low-contrast, tight-leading, wide-tracking
- `g-woven-fashion_1440x900.json`: 47 находок; правила: clipped-overflow-container, codex-grid-background, cream-palette, em-dash-overuse, gpt-thin-border-wide-shadow, hero-eyebrow-chip, kicker-above-heading, layout-transition, line-length, low-contrast, marquee, skipped-heading, undersized-ui-text
- `g-woven-fashion_390x844.json`: 49 находок; правила: body-text-viewport-edge, clipped-overflow-container, codex-grid-background, cream-palette, em-dash-overuse, gpt-thin-border-wide-shadow, kicker-above-heading, layout-transition, low-contrast, marquee, skipped-heading, tiny-text, undersized-ui-text
- `g-yanxi-onsen_1440x900.json`: 19 находок; правила: cramped-padding, cream-palette, em-dash-overuse, hero-eyebrow-chip, kicker-above-heading, layout-transition, line-length, wide-tracking
- `g-yanxi-onsen_390x844.json`: 13 находок; правила: cramped-padding, cream-palette, em-dash-overuse, kicker-above-heading, layout-transition, wide-tracking
- `g-yue-studio_1440x900.json`: 3 находок; правила: layout-transition, low-contrast
- `g-yue-studio_390x844.json`: 3 находок; правила: layout-transition, low-contrast
- `xx-multicurrency_1440x900.json`: 31 находок; правила: clipped-overflow-container, em-dash-overuse, layout-transition, line-length, low-contrast, nested-cards, overused-font, skipped-heading, tiny-text, undersized-ui-text
- `xx-multicurrency_390x844.json`: 19 находок; правила: em-dash-overuse, layout-transition, low-contrast, nested-cards, overused-font, skipped-heading, tiny-text, undersized-ui-text
- `xx-video-heroes_1440x900.json`: 0 находок; правила: 
- `xx-video-heroes_390x844.json`: 7 находок; правила: kicker-above-heading, layout-transition, low-contrast

Файлов с разобранным JSON: 44

| правило impeccable | файлов |
|---|---|
| layout-transition | 27 |
| low-contrast | 22 |
| kicker-above-heading | 13 |
| cream-palette | 13 |
| all-caps-body | 10 |
| em-dash-overuse | 10 |
| overused-font | 9 |
| wide-tracking | 9 |
| undersized-ui-text | 8 |
| clipped-overflow-container | 8 |
| image-hover-transform | 7 |
| buried-raster | 6 |
| cramped-padding | 6 |
| tiny-text | 6 |
| hero-eyebrow-chip | 5 |
| bounce-easing | 5 |
| skipped-heading | 5 |
| body-text-viewport-edge | 4 |
| marquee | 4 |
| line-length | 4 |
| content-hidden-at-rest | 3 |
| numbered-section-labels | 3 |
| gpt-thin-border-wide-shadow | 3 |
| radial-spotlight-glow | 2 |
| ai-color-palette | 2 |
| text-occlusion | 2 |
| organic-clip-path | 2 |
| tight-leading | 2 |
| codex-grid-background | 2 |
| nested-cards | 2 |
| italic-serif-display | 1 |
| dark-glow | 1 |
| radial-halo | 1 |
| edge-flush-cards | 1 |
