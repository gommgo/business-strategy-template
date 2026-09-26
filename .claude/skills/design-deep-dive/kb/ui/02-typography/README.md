# 02-typography — типографика интерфейсов веб-сервисов

Волна 1, агент B, 22 сентября 2026. Прочитано целиком: 39 внешних источников + 7 видео-дайджестов из
`../91-videos/digests/` + собственное измерение метрик 22 шрифтов. Сырые заметки: `../99-raw/notes/wave1/B-notes.md`. Отчёт: `../99-raw/reports/wave1-B-report.md`.

## Выжимка папки

1. **База 14 px для админок и бэк-офиса, 16 px для клиентских сервисов.** Carbon разделяет прямо: productive
   14 px, expressive 16 px. Polaris опускается до 13 px, GOV.UK поднимается до 19 px.
2. **Готовые пресеты шкалы лежат в `02-type-scale.md` §7 и §8** — бери целиком, с размером, интерлиньяжем,
   весом, трекингом и назначением каждой роли.
3. **Размеров 5–7, ролей 8–15.** Ряд для интерфейса: 11, 12, 13, 14, 16, 18, 20, 24, 28, 32 px. Всё крупнее
   40 px в приложении не нужно.
4. **Интерлиньяж: тело 1.4–1.5, заголовки 1.1–1.3, однострочные лейблы 1.0–1.25.** Простейшая формула —
   `line-height(px) = кегль + 6…8 px`, округление к 4 px.
5. **Трекинг: 0 на теле, −0.01…−0.02 em на заголовках от 20 px, +0.01…+0.02 em на подписях 11–12 px.**
   Значения не переносятся между гарнитурами.
6. **Длина строки 45–75 знаков, потолок 80 (WCAG 1.4.8).** `max-width: 65ch`.
7. **Три веса: 400, 500, 600.** Light и Thin в интерфейсе не используются. Заголовки от 28 px не тяжелее 600.
8. **Для русского интерфейса выбирай шрифт по качеству кириллицы**: безопасны Golos Text, IBM Plex Sans,
   PT Sans, Commissioner; эксперты не рекомендуют кириллицу Inter, Roboto, Manrope, Fira Sans, Source Sans 3.
   Совсем без кириллицы: Poppins, Public Sans, DM Sans, Space Grotesk, Outfit, Figtree и ещё 7 популярных.
9. **Короткие надписи при переводе EN → RU растут по ширине в 1.4–1.5 раза, абзацы — на 13–18 %** (измерено).
   Ширины кнопок и колонок проектируй по русскому тексту.
10. **Только Sentence case, «ёлочки», длинное тире, неразрывные пробелы, `1 234 567,89 ₽`,
    `font-variant-numeric: tabular-nums` во всех числовых колонках.**

Дополнительно из видео: предел отрицательного трекинга проверяется словом «ухо» `[V15]`; узкий шрифт экономит
около 6 % ёмкости, а не «много» `[V15]`; в тёмной теме берётся начертание на ступень легче `[V15]`; иерархию
первым делом задаёт пространство, а не шрифт `[V05]`; отступ между заголовком и его текстом 1×, до предыдущего
блока 2× `[V07]`.

## Карта файлов

| файл | о чём | строк |
|---|---|---|
| `01-font-selection.md` | классы гротесков, критерии пригодности для UI (x-height, различимость, `tnum`, веса, переменность, лицензия), кириллица и её экспертная оценка, список 12 шрифтов с качественной кириллицей и OFL, системный стек против веб-шрифта, загрузка и метрические фолбэки, пары гарнитур, моноширинные | 860 |
| `02-type-scale.md` | **основной файл**: полные шкалы 12 дизайн-систем, база 14 против 16, роли, модульные шкалы против ручных, минимумы и доступность, токены и единицы, **два готовых пресета (плотная админка и клиентский сервис)**, адаптация к экрану, пересчёт шкалы при смене гарнитуры, сопоставление Refactoring UI и Practical UI с Material 3 и Carbon | 1119 |
| `03-leading-tracking-measure.md` | интерлиньяж по ролям и системам, кривая обратной зависимости, формулы, трекинг (включая таблицы Apple и тест «ухо»), длина строки и поправка на русский, абзацный отбив, отступы вокруг заголовков, выравнивание, переносы | 742 |
| `04-weight-hierarchy-color.md` | веса и что чем набирать, вес против размера, тёмная тема и сглаживание, четыре инструмента иерархии, правило двух уровней, уровни цвета текста и пороги контраста, заголовки и регистр, капс, усечение и минимальные ширины колонок | 568 |
| `05-numbers-rhythm-opentype.md` | табличные цифры и какие шрифты их имеют, формат чисел в русской локали, KPI на дашбордах, вертикальный ритм и кратность 4 px, `text-box-trim`, `text-wrap: balance / pretty / stable`, `hanging-punctuation`, `font-optical-sizing`, OpenType-фичи для UI, сглаживание | 735 |
| `06-localization-and-ai-errors.md` | измеренное расширение текста EN → RU, кириллица шире латиницы, проектирование под расширение, `lang` и `Intl`, русские типографские нормы (кавычки, тире, ё, неразрывные пробелы), 15 типичных ошибок нейросетей с правилами проверки, набор автоматических проверок | 618 |
| `glossary.md` | термины типографики RU/EN с определениями и примерами значений | 162 |

Связи с другими папками: цвет текста и контрасты — `../01-color/`; отступы вокруг текста, высоты контролов и
плотность — `../03-spacing-sizing/`; ширины контейнеров и колонок — `../05-layout-grid/` (волна 2);
типографика конкретных компонентов — `../06-components-visual/` (волна 2); запись в токены —
`../09-design-tokens/` (волна 2); ошибки генерации — `../12-ai-generated-ui/` (волна 3); проверки —
`../13-evaluation-checklists/` (волна 3). UX-часть (тексты интерфейса, микрокопи, локализация как процесс) —
в `../../ux/07-ux-writing/`.

## Сводный список источников

Сквозная нумерация для всей папки. В отдельных файлах перечислены только те, на которые они ссылаются.

### Документация и исходники дизайн-систем

- `[S1]` IBM Carbon Design System. Typography — Overview. https://carbondesignsystem.com/elements/typography/overview/ — гарнитура IBM Plex, формула шкалы (y₀ = 12), веса 300/400/600, правила цвета текста. Первичная документация.
- `[S2]` IBM Carbon Design System. Typography — Type sets. https://carbondesignsystem.com/elements/typography/type-sets/ — полные значения productive и expressive токенов, база 14 и 16 px. Первичная документация, самый подробный набор значений из всех систем.
- `[S3]` Microsoft. Fluent 2 — Typography. https://fluent2.microsoft.design/typography — рампы для web/Windows/macOS/iOS/Android, регистр, выравнивание, пороги контраста. Первичная документация.
- `[S4]` Apple. Human Interface Guidelines — Typography (обновлено 16.12.2025). https://developer.apple.com/design/human-interface-guidelines/typography — минимумы платформ, Dynamic Type, таблицы трекинга SF Pro / SF Pro Rounded / New York, macOS text styles. Текст получен из JSON-API документации. Первичный источник.
- `[S5]` Google. Material 3 type scale tokens. Исходник `material-web` v0.192: `tokens/versions/v0_192/_md-sys-typescale.scss`, `_md-ref-typeface.scss`. https://github.com/material-components/material-web — значения из кода; документация m3.material.io не отдаётся скриптом (SPA).
- `[S6]` Shopify Polaris tokens: `polaris-tokens/src/themes/base/font.ts`, `text.ts`, `src/size.ts`. https://github.com/Shopify/polaris — база 13 px, веса 450/550/650/700. Исходники, первичный источник.
- `[S7]` GitHub Primer primitives: `src/tokens/base/typography/typography.json5`. https://github.com/primer/primitives — 6 размеров на продукт, официальные описания ролей интерлиньяжа.
- `[S8]` GOV.UK Design System. Type scale (Frontend v6.0.0+). https://design-system.service.gov.uk/styles/type-scale/ — база 19 px, кратность 5 px, адаптивная шкала. Первичная документация.
- `[S9]` Tailwind CSS v4, `packages/tailwindcss/theme.css` (тег v4.1.11). https://github.com/tailwindlabs/tailwindcss — размеры, веса, трекинг, интерлиньяж, шрифтовые стеки.
- `[S10]` Atlassian Design System. Typography. https://atlassian.design/foundations/typography — токены heading/body/metric/code, paragraph spacing, правила применения размеров, rem вместо px. Первичная документация.
- `[S18]` Radix Themes. Typography + исходник `packages/radix-ui-themes/src/styles/tokens/typography.css`. https://www.radix-ui.com/themes/docs/theme/typography — 9-шаговая шкала с непрерывным трекингом, отдельный интерлиньяж заголовков, токены leading-trim.
- `[S19]` Vercel Geist: https://vercel.com/font и релизы https://github.com/vercel/geist-font/releases — лицензия OFL, дата появления кириллицы (1.7.0, 29.01.2026), история программистских лигатур.
- `[S35]` Ant Design 5: `components/theme/themes/seed.ts`, `shared/genFontSizes.ts`, `shared/genFontMapToken.ts`. https://github.com/ant-design/ant-design — формула шкалы `base × e^(i/5)` и правило `line-height = (fontSize + 8)/fontSize`.
- `[S36]` MUI, `packages/mui-material/src/styles/createTypography.js`. https://github.com/mui/material-ui — дефолтная шкала Material 2, предупреждение о непереносимости трекинга между гарнитурами.
- `[S37]` Mantine, `packages/@mantine/core/src/core/MantineProvider/default-theme.ts`. https://github.com/mantinedev/mantine — fontSizes, lineHeights (растущие с кеглем), headings, fontWeights, fontSmoothing.

### Шрифты и кириллица

- `[S13]` type.today. Cyrillic on Google Fonts: Neo-Grotesques, 19.03.2024. Эксперты: Михаил Струков, Илья Рудерман, Юрий Остроменцкий (CSTM Fonts). https://type.today/en/journal/neo — экспертная оценка качества кириллицы Roboto, Inter, IBM Plex Sans, Golos Text, Manrope, Nunito, Oswald, Arimo, Alumni Sans, Overpass. Самый авторитетный доступный разбор.
- `[S14]` type.today. Cyrillic on Google Fonts: Humanist Sans, 27.06.2024. https://type.today/en/journal/humanist — PT Sans, Open Sans, Fira Sans, Source Sans 3, Commissioner, Noto Sans, Ubuntu и ещё 13 шрифтов.
- `[S15]` Алексей Бурба. Шрифт Inter // Typeface Inter. http://burba.pro/inter-typeface/ — независимое подтверждение проблем «д» и «л» в кириллице Inter. Мнение практика.
- `[S16]` Rasmus Andersson. Inter. https://rsms.me/inter/ — полный список OpenType-фич (`ss01`–`ss08`, `cv01`–`cv13`, `tnum`, `zero`, `case`), оптические размеры, рекомендуемое подключение. Первичный источник автора шрифта.
- `[S17]` Paratype. How to understand Cyrillic. https://info.paratype.com/how-to-understand-cyrillic/ — методика оценки качества кириллицы: рисунок, ширины, просветы, распределение толщин; проблемные пары «где», «кл», «дл».
- `[S20]` Google Fonts metadata. https://fonts.google.com/metadata/fonts — первичные данные о подмножествах (`cyrillic`, `cyrillic-ext`), переменных осях и доступных весах для 60 проверенных семейств.
- `[S24]` Собственные измерения: метрики 22 шрифтов (x-height, cap height, ширины латиницы и кириллицы, вертикальные метрики, наличие `tnum`/`kern`/`pnum`) через fontTools 4.65 по TTF из Google Fonts; ширина 20 пар интерфейсных надписей и 4 пар предложений EN/RU. Метод, скрипты и полные таблицы — в `../99-raw/notes/wave1/B-notes.md`, раздел S24.

### Книги и практики

- `[S11]` Matthew Butterick. Typography in ten minutes. https://practicaltypography.com/typography-in-ten-minutes.html — пять базовых правил: тело первым, 15–25 px в вебе, 120–145 %, 45–90 знаков, выбор шрифта.
- `[S26]` Matthew Butterick. Practical Typography: body text, point size, line spacing, line length. https://practicaltypography.com — развёрнутые главы; критика огромных заголовков в вебе, метод подбора кегля при смене гарнитуры.
- `[S12]` Erik D. Kennedy (Learn UI Design). The Responsive Website Font Size Guidelines, обновлено 30.05.2024. https://www.learnui.design/blog/mobile-desktop-website-font-size-guidelines.html — 14–20 px для interaction-heavy и 18–24 px для text-heavy, правило ≥ 16 px для полей ввода, «не больше 4 размеров».
- `[S31]` Adham Dannaway. Practical UI. https://www.practical-ui.com/ (страница книги с полным текстом одного правила) + конспект читателя https://bryananthonio.com/blog/takeaways-practical-ui-book/ — длина строки 40–80 знаков с обоснованием, типографическая шкала вместо произвольных кеглей, ограниченный набор отступов. Книга платная, полный текст не открывался.
- `[S39]` Adam Wathan, Steve Schoger. Refactoring UI — полное оглавление книги. https://www.refactoringui.com/ — названия глав разделов «Designing Text» (8 глав) и «Hierarchy is Everything» (8 глав); сами главы формулируют правила.
- `[S40]` Sébastien Lavoie. Book summary: Refactoring UI, 09.09.2023. https://www.sglavoie.com/posts/2023/09/09/book-summary-refactoring-ui/ — подробный конспект правил книги, включая раздел Text целиком. Вторичный источник: сама книга платная и не открывалась.
- `[S41]` Andrew Nisbet. Takeaways from Refactoring UI. https://www.ajnisbet.com/blog/refactoring-ui — конспект читателя с примерами применения; вторичный источник.
- `[S32]` Untitled UI. 31 Best Free Fonts for Modern UI Design in 2026. https://www.untitledui.com/blog/best-free-fonts — база 16 px, интерлиньяж тела 1.5–2.0 и display 1.0–1.25, критерий «не менее 4–5 весов», одна гарнитура на проект, лицензии 31 шрифта.
- `[S33]` Артемий Лебедев. Ководство, § 62 «Экранная типографика» (17.12.2000) и § 104 «Кавычки» (17.05.2004). https://www.artlebedev.ru/kovodstvo/sections/62/ , https://www.artlebedev.ru/kovodstvo/sections/104/ — канонический свод правил русского экранного набора: кавычки, тире, неразрывные пробелы, спецзнаки.
- `[S34]` Habr. Title case против Sentence case, 25.06.2024. https://habr.com/ru/articles/824548/ — **низкая надёжность** (метка Recovery Mode, проценты без ссылок на первоисточники). Использовано только как фиксация расхождения Apple (Title Case) и Google (Sentence case).

### Стандарты, спецификации, исследования

- `[S21]` MDN. `font-variant-numeric`. https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant-numeric — Baseline «Widely available» с января 2020.
- `[S22]` MDN. `text-box-trim`. https://developer.mozilla.org/en-US/docs/Web/CSS/text-box-trim — **Baseline 2026, «Newly available» с августа 2026**; работает в паре с `text-box-edge`.
- `[S27]` MDN. `size-adjust` (`@font-face`). https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/size-adjust — Baseline с сентября 2023.
- `[S28]` MDN. `text-wrap-style` (`balance`, `pretty`, `stable`). https://developer.mozilla.org/en-US/docs/Web/CSS/text-wrap-style — Baseline 2024 с октября 2024; лимиты 6 строк (Chromium) и 10 строк (Firefox) для `balance`; предупреждение о производительности `pretty`.
- `[S29]` MDN. `hanging-punctuation`. https://developer.mozilla.org/en-US/docs/Web/CSS/hanging-punctuation — «Limited availability», не Baseline.
- `[S30]` MDN. `font-optical-sizing`. https://developer.mozilla.org/en-US/docs/Web/CSS/font-optical-sizing — Baseline с марта 2020.
- `[S23]` Baymard Institute, Edward Scott. Readability: The Optimal Line Length, 10.05.2022. https://baymard.com/blog/line-length-readability — 50–75 знаков по итогам юзабилити-тестов, WCAG 1.4.8 (≤ 80 знаков) и 1.4.12 (Text Spacing), рекомендация `max-width: 70ch`.
- `[S25]` Katie Hempenius. Improved font fallbacks. Chrome for Developers. https://developer.chrome.com/blog/font-fallbacks — формулы `size-adjust` и метрических overrides, таблица применяемых метрик по браузерам и ОС, инструменты.

### Видео (дайджесты в `../91-videos/digests/`)

- `[V01]` Steve Schoger. Refactoring UI, CSS Day 2019. `01-schoger-refactoring-ui-css-day-2019.md` — uppercase-лейблы в таблицах, `font-feature-settings: "tnum"`, системный стек против кастомного шрифта, поиск шрифта через DevTools.
- `[V02]` Steve Schoger. Little Details, Laracon 2018. `02-schoger-little-details-laracon-2018.md` — шкала кеглей с поправками (20 вместо 21, добавленный 30), три серых для текста, вес вместо кегля, интерлиньяж 16/1.5, uppercase всегда с трекингом, фильтр Google Fonts по 8 начертаниям, невзаимозаменяемость шрифтов.
- `[V05]` Sajid. The 80 % of UI Design — Typography, 2024 (354 тыс. просмотров). `05-sajid-typography-80-percent.md` — «трёх кеглей достаточно», база 14 или 16 px с шагом ±2 px, `rem`, `line-height` как отступ, стиль против тега, светлота 90/70/60 % на тёмном.
- `[V07]` Tim Gabe. Типографика, воздух и сетка 8pt, 2022 (два видео, 1 млн просмотров у первого). `07-tim-gabe-type-space-8pt-grid.md` — измеренные интерлиньяжи Google, Dropbox, Uber; трекинг заголовков −1…−2 %; длина строки 50–75 знаков ≈ 600 px при 18 px; правило отступов 1×/2×; границы применимости сетки 4/8.
- `[V09]` Kole Jain. Дашборды и «AI slop». `09-kole-jain-dashboard-and-ai-slop.md` — у дашборда кегли мельче и шаги шкалы плотнее, чем у лендинга.
- `[V14]` Илья Бирман. Эстетика в интерфейсе. `14-birman-aesthetics-in-ui.md` — «16 текстовых стилей в верхней части экрана» как антипример; норма «три размера шрифта»; не увеличивать отступ под заголовком вслед за кеглем.
- `[V15]` **Александра Королькова (ParaType), «Типографика в UX/UI-дизайне», 2025, 1:13:44.** `15-korolkova-typography-cyrillic.md` — **главный источник по кириллице**: критерии оценки контура и расстояний, оптические размеры и тест «ухо», параметры удобочитаемости 65–95 % и 65–75 %, эксперимент про ёмкость (~6 %), кейс Lucida Grande → Helvetica → San Francisco, болгарская кириллица, начертания как адаптация к теме, кегль ≠ высота буквы, вертикальные метрики и базовая линия, сочетания гарнитур.

### Проверено и отброшено

- `[S38]` Бюро Горбунова, совет https://bureau.ru/soviet/20090511/ — разбор интерфейса без типографических значений, в итоговые файлы не вошёл.
- Не открылись и потому не использованы: `m3.material.io` (SPA, значения взяты из исходников), `spectrum.adobe.com` (SPA), `ant.design/docs/spec/font` (SPA, значения из исходников), `polaris-react.shopify.com/design/typography` и `primer.style/product/foundations/typography` (редирект на общие страницы, значения из исходников), `web.dev/articles/font-best-practices` и `anthonyhobday.com` (сеть недоступна), `w3.org/International/*` и `ibm.com/docs/*` (403 и 404), `paratype.ru` (JS-рендер).
