# Выбор гарнитуры для интерфейса: классы, критерии, кириллица, загрузка

Волна 1, агент B, 22 сентября 2026. Источников прочитано целиком: 37. Сквозная нумерация источников по всей
папке `02-typography/`, полный список в `README.md`.

## Выжимка для агента

1. **Одна гарнитура на всё приложение плюс одна моноширинная.** Вторая текстовая гарнитура в приложении —
   маркер маркетинга. Apple: «Minimize the number of typefaces you use… Mixing too many different typefaces
   can obscure your information hierarchy» `[S4]`; Untitled UI: «limit your designs to using just one
   typeface… If you absolutely need to, use a maximum of two» `[S32]`. → §6 `[консенсус]`
2. **Если продукт русскоязычный, выбирай шрифт по качеству кириллицы, а не по популярности.** Эксперты
   type.today прямо не рекомендуют кириллицу Inter, Roboto, Manrope, Fira Sans, Source Sans 3, Open Sans
   (жирные веса), Overpass, Oswald, Arimo, Alumni Sans `[S13]`, `[S14]`. → §3 `[исследование]`
3. **Безопасный русский выбор: Golos Text, IBM Plex Sans, PT Sans, Commissioner.** У всех четырёх кириллицу
   эксперты оценили как пригодную `[S13]`, `[S14]`, все под OFL. → §3.3
4. **Нет кириллицы вообще** (проверено по метаданным Google Fonts `[S20]`): Poppins, Public Sans, Lato,
   DM Sans, Space Grotesk, Outfit, Sora, Figtree, Instrument Sans, Albert Sans, Schibsted Grotesk, Gabarito,
   Bricolage Grotesque. Plus Jakarta Sans и Hanken Grotesk имеют только `cyrillic-ext` без базового
   `cyrillic` — для русского не годятся. → §3.4 `[система]`
5. **Критерии пригодности для UI, по убыванию важности**: x-height ≥ 0.52 em, различимость `Il1` и `0O`,
   наличие весов 400/500/600, табличные цифры или фича `tnum`, поддержка кириллицы, переменный формат,
   лицензия OFL. → §2
6. **Проверяй `tnum` до того, как поставишь шрифт в таблицы.** У Commissioner и Wix Madefor Text цифры
   пропорциональные и фичи `tnum` нет — числа в столбце будут прыгать `[S24]`. → §2.4 `[исследование]`
7. **Системный стек — бесплатный и мгновенный вариант**, его выбрали Radix Themes, Ant Design, Mantine,
   Tailwind v4 `[S18]`, `[S35]`, `[S37]`, `[S9]`. Минус: интерфейс выглядит по-разному на Windows, macOS и
   Android, и вертикальные метрики гуляют. → §4 `[система]`
8. **Веб-шрифт подключай с `font-display: swap` и метрическим фолбэком** (`size-adjust`, `ascent-override`,
   `descent-override`, `line-gap-override`), иначе получишь скачок вёрстки при подмене `[S25]`. → §5.2 `[консенсус]`
9. **Сабсеть кириллицу отдельным `unicode-range`**: латиница и кириллица в одном файле удваивают вес.
   → §5.3 `[консенсус]`
10. **Переменный шрифт выгоден от трёх весов.** Один файл InterVariable заменяет 3–5 статических; плюс
    появляется доступ к промежуточным весам, чем пользуется Polaris (450/550/650) `[S6]`. → §2.6 `[система]`
11. **Моноширинный ставь на 1–2 px мельче основного текста** в той же строке: Radix задаёт
    `--code-font-size-adjust: 0.95` `[S18]`, Atlassian — инлайновый код ≈ 12.25 px при контейнере 14 px `[S10]`.
    → §7 `[консенсус]`
12. **Лигатуры в моноширинном для кода и идентификаторов выключай.** Geist Mono 1.7.0 специально вынес
    программистские лигатуры из `calt` в `ss11`, потому что они ломали моноширинность `[S19]`. → §7.2 `[система]`
13. **Serif в интерфейсе — только для «редакторского» режима**: тело статьи, заметки, длинное чтение.
    Butterick: «on today's screens, serif fonts look equally good» — довод «на экране только гротеск»
    устарел `[S26]`. → §6.3 `[мнение]`
14. **Не выбирай шрифт с весами 100–300 для интерфейса.** Apple: «avoid Ultralight, Thin, and Light font
    weights, which can be difficult to see, especially when text is small» `[S4]`. → §2.5 `[консенсус]`
15. **Проверь шрифт на строке `Шхуна «Ёж» ждёт: 0O Il1 — №5 ₽1 234,56`** — она вскрывает кириллицу, ё,
    кавычки-ёлочки, различимость знаков, тире, знак номера, рубль и разделители разрядов. → §3.5
16. **Слова Caption, Text, Subhead, Display в имени гарнитуры — это рекомендованный кегль, а не украшение.**
    «Display — это витрина, а не монитор» (Александра Королькова, ParaType) `[V15]`. → §8.1 `[мнение]`
17. **Узкий шрифт экономит около 6 % ёмкости набора, не больше** (эксперимент Корольковой `[V15]`): ширина
    гарнитуры влияет на настроение макета сильнее, чем на вместимость. → §8.1 `[исследование]`
18. **Число начертаний — косвенный признак качества гарнитуры**: 8 начертаний у Schoger `[V02]`, 5+ весов у
    Refactoring UI `[S40]` и Untitled UI `[S32]`. → §8.2 `[консенсус]`

---

## 1. Классификация гротесков для интерфейса

### 1.1. Три семейства и их поведение в UI

| класс | определение | представители | характер | мелкий текст | ширина |
|---|---|---|---|---|---|
| **Неогротеск** (neo-grotesque) | «closed-aperture sans serifs, heirs of the old grotesques… vertical axis, near-zero contrast, and oblique letterforms used as italics» `[S13]` | Inter, Roboto, Helvetica/Arial, SF Pro, Segoe UI, IBM Plex Sans, Geist, Golos Text | нейтральный, «никакой», не мешает данным | хорошо при высоком x-height | средняя, есть узкие варианты |
| **Гуманистический** (humanist) | «sans serifs that somehow inherit… dynamics and letterforms of the broad nib» `[S14]` | Open Sans, PT Sans, Fira Sans, Source Sans 3, Ubuntu, Noto Sans, Commissioner | теплее, «человечнее», заметнее | хорошо: открытая апертура | часто шире |
| **Геометрический** (geometric) | построен на круге и прямой, малая разница ширин | Poppins, Montserrat, Futura, Jost, Outfit, Manrope (наполовину) | декоративный, «маркетинговый» | плохо: `o`, `c`, `e` сливаются, узкие счётчики | широкий, «жрёт» место |

`[консенсус]`, определения дословно из `[S13]`, `[S14]`.

### 1.2. Что это значит для выбора

- **Неогротеск — дефолт для интерфейса.** Нейтральность здесь функциональна: type.today про Roboto прямо
  пишет, что дефекты рисунка «interfere with the typeface's neutrality, which is an important thing in UI»
  `[S13]`.
- **Гуманистический — когда продукт должен быть «мягче»** (сервисы для людей, а не для операторов), и когда
  много длинного текста: открытая апертура помогает.
- **Геометрический в интерфейсе — почти всегда ошибка.** Причины, подтверждаемые измерениями `[S24]`:
  Montserrat имеет среднюю ширину строчной 0.574 em (самая широкая из 22 проверенных шрифтов) против 0.505 у
  IBM Plex Sans, то есть строка длиннее на 14 %; при этом x-height 0.525 — не выше среднего. Для таблиц и
  плотных форм это прямой проигрыш.
  Исключение: заголовки в продуктах с выраженным брендом и короткими надписями.

### 1.3. Почему x-height важнее класса

Читаемость мелкого текста определяется прежде всего ростом строчных. type.today про Roboto: «today's screen
resolutions have turned a technical issue of legibility at small sizes into one of type design, making it
about metrics; here it is ensured by large x-height» `[S13]`. Untitled UI про Satoshi: «does have a slightly
lower x-height at 66 %… not specifically designed for legibility at very small sizes» `[S32]`.

Измеренные значения — в §2.1 и в `02-type-scale.md` §10.

---

## 2. Критерии пригодности гарнитуры для интерфейса

### 2.1. x-height (рост строчных)

Порог: **≥ 0.52 em** для интерфейса с базой 14 px, **≥ 0.50 em** при базе 16 px `[мнение]`, выведено из
измерений `[S24]` и из того, какие шрифты системы реально выбирают.

| шрифт | x-height / em | вывод |
|---|---|---|
| JetBrains Mono | 0.550 | моно с самым высоким ростом |
| Inter, Inter Tight | 0.546 | эталон для плотных интерфейсов |
| Manrope | 0.540 | высокий, но кириллица плохая `[S13]` |
| Noto Sans | 0.536 | высокий |
| Open Sans | 0.535 | высокий, но широкий |
| Geist, Golos Text | 0.530 | годится для 13–14 px |
| Roboto | 0.528 | годится |
| Fira Sans, Onest | 0.527 | годится |
| Montserrat | 0.525 | на грани, и очень широкий |
| Rubik | 0.520 | нижняя граница для базы 14 |
| Ubuntu Sans | 0.518 | на грани |
| IBM Plex Sans | 0.516 | для базы 14 требует внимания, для 16 норм |
| PT Sans | 0.500 | только база 16, плюс «выглядит светлым» `[S14]` |
| Commissioner | 0.496 | только база 16 |
| Wix Madefor Text | 0.492 | только база 16 |
| Nunito Sans, Source Sans 3 | 0.486 | мелкий текст читается плохо |

Отношение x-height к высоте прописных (x/cap) показывает «взрослость» пропорций: 0.74–0.76 у современных
UI-шрифтов (Inter 0.750, Fira Sans 0.765, Golos Text 0.757), 0.69–0.71 у более классических (Commissioner
0.696, Wix Madefor Text 0.688, Nunito Sans 0.689) `[S24]`.

### 2.2. Различимость знаков: Il1 и 0O

Обязательна там, где пользователь читает коды, id, номера, пароли, названия переменных.

Приёмы:
- **`zero` (перечёркнутый ноль)** — есть у Inter (полная версия с rsms.me), JetBrains Mono, IBM Plex Mono.
- **`ss02` «Disambiguation» у Inter** — набор глифов, «that increases visual difference between similar-looking
  characters», плюс отдельные варианты `cv05` (строчная l с хвостом), `cv08` (прописная I с засечками),
  `cv01` (альтернативная единица) `[S16]`.
- **Моноширинный шрифт** — радикальное решение для колонки с id.

Важно: **в субсетах Google Fonts фичи `ss*` и `cv*` вырезаны** `[S24]`. Если нужны стилистические наборы
Inter, подключай шрифт с `rsms.me/inter` или самостоятельно собранный файл, а не Google Fonts API.

### 2.3. Ширина и плотность

Средняя ширина строчной латиницы (доля em, измерено `[S24]`), от узких к широким:

Source Sans 3 0.475 · PT Sans 0.481 · Inter Tight 0.486 · Roboto 0.499 · IBM Plex Sans 0.505 ·
Ubuntu Sans 0.506 · Fira Sans 0.508 · Nunito Sans 0.508 · Commissioner 0.517 · Open Sans 0.522 ·
Manrope 0.523 · Onest 0.527 · Wix Madefor Text 0.529 · Rubik 0.531 · Geist 0.534 · Inter 0.536 ·
Golos Text 0.545 · **Montserrat 0.574**.

Разница между Inter Tight (0.486) и Montserrat (0.574) — **18 %**. В таблице на 10 колонок это разница
между «влезает» и «горизонтальный скролл».

Inter Tight отличается от Inter **только межбуквенным расстоянием** `[S13]` и даёт −9 % ширины строки при том
же рисунке и той же кириллице. Обратная сторона: Inter Tight «designed for display purposes» `[S13]`,
на мелких кеглях набор становится слишком плотным.

### 2.4. Цифры: табличные по умолчанию или через `tnum`

Проверено по файлам шрифтов, с учётом GSUB и GPOS `[S24]`:

| шрифт | цифры равной ширины по умолчанию | есть `tnum` | вывод для таблиц |
|---|---|---|---|
| Roboto, Noto Sans, Open Sans, Ubuntu Sans | да | да | безопасно |
| IBM Plex Sans, PT Sans, Nunito Sans, Source Sans 3 | да | нет | безопасно, `tnum` не нужен |
| Inter, Inter Tight, Golos Text, Onest, Geist, Manrope, Montserrat, Rubik, Fira Sans | нет | да | обязательно `font-variant-numeric: tabular-nums` |
| **Commissioner, Wix Madefor Text** | нет | **нет** | **в числовых таблицах не использовать** |
| JetBrains Mono, Geist Mono, IBM Plex Mono, Roboto Mono | да (моноширинные) | нет | безопасно |

Подробности про применение — в `05-numbers-rhythm-opentype.md` §1.

### 2.5. Веса

Нужный минимум для интерфейса: **400, 500, 600**. Желательно 700 для редких акцентов.

- Apple: «prefer Regular, Medium, Semibold, or Bold font weights, and avoid Ultralight, Thin, and Light font
  weights» `[S4]`.
- Carbon использует 300/400/600, и про 600: «ideal for section headers, but should not be used for long
  text» `[S1]`.
- Fluent 2 обходится без 500: «сильный» вариант каждой роли — сразу Semibold 600 `[S3]`.
- Mantine называет medium = **600**, а не 500 `[S37]`; Polaris — 450/550/650/700 из переменного шрифта `[S6]`.
- Untitled UI как признак качества: «A good font will come with at least four — usually light, regular,
  medium, semibold, and bold (with italic versions of each)» `[S32]`.

Ловушка: **у Golos Text нет весов легче 400** (переменная ось wght 400–900) `[S20]`. Если дизайн
предполагает Light — этот шрифт не подойдёт; для интерфейса это скорее плюс.

### 2.6. Переменный шрифт

Выгода `[система]`:
- один файл вместо 3–5 (меньше запросов, меньше суммарный вес при трёх и более весах);
- доступ к промежуточным весам: Polaris ставит regular = **450**, medium = 550, semibold = 650 `[S6]` —
  это «полступени» плотности, недостижимые со статическими файлами;
- ось `opsz` даёт автоматическую оптическую подгонку (`font-optical-sizing: auto`, см.
  `05-numbers-rhythm-opentype.md` §5).

Переменные оси у шрифтов с кириллицей (проверено по метаданным Google Fonts `[S20]`):

| шрифт | оси |
|---|---|
| Inter | `opsz` 14–32, `wght` 100–900 |
| Roboto Flex | 13 осей: `opsz` 8–144, `wght` 100–1000, `wdth` 25–151, `GRAD`, `XTRA`, `YOPQ`, `YTLC`, `YTUC`, `YTAS`, `YTDE`, `YTFI`, `XOPQ`, `slnt` |
| Roboto | `wdth` 75–100, `wght` 100–900 |
| IBM Plex Sans | `wdth` 75–100, `wght` 100–700 |
| Noto Sans | `wdth` 62.5–100, `wght` 100–900 |
| Nunito Sans | `opsz` 6–12, `wdth` 75–125, `YTLC`, `wght` 200–1000 |
| Commissioner | `FLAR` 0–100, `VOLM` 0–100, `slnt` −12–0, `wght` 100–900 |
| Golos Text | `wght` 400–900 |
| Onest, Geist, Geist Mono, Montserrat, Inter Tight | `wght` 100–900 |
| Manrope | `wght` 200–800 |
| Rubik | `wght` 300–900 |
| Wix Madefor Text / Display | `wght` 400–800 |
| JetBrains Mono | `wght` 100–800 |
| PT Sans, Fira Sans, IBM Plex Mono | **нет переменного файла** |

### 2.7. Лицензия

OFL (SIL Open Font License 1.1) — дефолт для генеративной системы: разрешает встраивание, самостоятельный
хостинг и сабсеттинг. Под OFL: Inter `[S16]`, Geist (`OFL.txt` в репозитории vercel/geist-font) `[S19]`,
Golos Text, Onest, IBM Plex Sans, PT Sans, Commissioner, Noto Sans, Rubik, JetBrains Mono, Wix Madefor,
Montserrat, Manrope (по метаданным Google Fonts, раздел `ofl/`) `[S20]`.

Не-OFL и требующие проверки: Söhne (Klim, платный, используется Stripe `[S32]`), Satoshi / Switzer /
General Sans / Supreme (Fontshare, собственная лицензия `[S32]`), Neue Haas Grotesk / Aktiv Grotesk /
Futura PT (Adobe Fonts, только по подписке `[S32]`), Segoe UI (лицензия Microsoft, веб-шрифтом
распространять нельзя), SF Pro (Apple: «don't embed system fonts in your app» `[S4]`).

### 2.8. Хинтинг и рендеринг на Windows

Прямых измерений у меня нет `[спорно]`. Что известно из источников:
- PT Sans «was originally adapted for low-resolution devices — which is helped by quite large lowercase and
  open aperture, as well as by very decent hinting» `[S14]`.
- Inter: «proper hinting» и умеренные инктрапы названы среди средств читаемости мелкого `[S13]`.
- Geist Mono с версии 1.5.0 включает символы псевдографики для терминалов `[S19]`.
- Apple советует для мокапов вручную подбирать трекинг, потому что «In a running app, the system font
  dynamically adjusts tracking at every point size» `[S4]` — то есть системные шрифты ведут себя иначе, чем
  веб-шрифты.

Практический вывод: перед выбором проверь шрифт на Windows без Retina при 100 % масштабе на размере 12–14 px.
Шрифты, специально заявленные как экранные (Inter, PT Sans, Golos Text, Onest, IBM Plex), безопаснее.

---

## 3. Кириллица

### 3.1. Как экспертиза оценивает качество кириллицы

Критерии Paratype `[S17]`: рисунок букв, их ширины, межбуквенные просветы, распределение толщин штриха.

Ключевые правила:
- **Не смешивать формы.** «If a typeface looks regular in weight and width and has "basic" letterforms, then
  different shapes should not be mixed — "б" always with a tail up, "р" always with a tail down» `[S17]`.
  Диагностика непрофессионализма: в латинице формы традиционные, а в кириллице смешанные.
- **Традиционные пропорции ширин**: «in both the narrowest and the widest typefaces the letter "ш" will be
  wider than the letter "н", and the letter "г" will be narrower than the letter "о"» `[S17]`.
- **Проблемные пары для кернинга**: «где» (дыра между «г» и «д»), «кл» и «дл» (внизу почти касаются, вверху
  дыра). «An experienced type designer is aware of "к" or "д" and "л" pairs and adjusts the shape of the
  letters to make the hole smaller» `[S17]`.
- **Болгарская кириллица** (буквы как «прямой курсив») для русского текста неуместна `[S17]`.

Типичные дефекты, названные экспертами type.today `[S13]`, `[S14]` — это готовый чек-лист:

| буква | что проверять |
|---|---|
| **б** | хвост не короткий, не светлый, не изломанный, не «шестёрка», не слипается с чашей; одна форма во всех весах |
| **д**, **л** | левый штрих не слишком толстый и не «динамичный»; нога Лл не прямая, не отставленная, не обрублена резко |
| **Д**, **Ц**, **Щ** | выносные элементы и ширины «плечиков» одинаковы у всех трёх букв и во всех весах |
| **И**, **К**, **У**, **М** | нет обратного контраста (восходящие диагонали толще нисходящих) |
| **ф** | одна из двух канонических форм, а не гибрид |
| **з** | не похожа на цифру 3 |
| **Ы**, **Ь**, **Ъ** | чаша не сплющена, правый штрих не отставлен |
| **й**, **Й** | бреве настроено отдельно для прописной, не слишком светлое и не слишком широкое |
| **ё**, **Ё** | точки на месте, не вылезают за строку |
| **ї**, **є**, **ґ**, **ә**, **ғ**, **қ** | если нужны украинский или казахский |

### 3.2. Вердикты экспертов по популярным шрифтам

Источник: экспертная рецензия Михаила Струкова, Ильи Рудермана и Юрия Остроменцкого (CSTM Fonts, type.today)
`[S13]` (неогротески, 19.03.2024), `[S14]` (гуманистические, 27.06.2024). `[исследование]` в смысле
профессиональной экспертизы, а не количественного теста.

| шрифт | вердикт | цитата / суть |
|---|---|---|
| **IBM Plex Sans** | **годится** | «a proper and balanced Cyrillic version, with well-applied forms and structures… can be used for a wide range of purposes». Кириллицу делала Александра Самуленкова |
| **Golos Text** | **годится** | «a functional typeface, well-suited for reading on screens and fitted with a decent Cyrillic extension». Оговорка: сербские ћђ слишком низкие |
| **Commissioner** | **годится** | «The quality of Cyrillic support is quite high: systematic solutions, designs that look natural» |
| **PT Sans** | **годится** | «Reasonable in quality, accurate in nature». Минусы: узкие круглые в курсиве, гибридная Фф, изломанный верх б |
| **Arsenal** | годится, но только для заголовков | «this Cyrillic is indeed very decent», но шрифт дисплейный |
| Noto Sans | оценка не даётся | кириллицу обновила в 2024 Jovana Jocić (автор кириллицы Roslindale и Forma DJR); эксперты отказались оценивать из-за конфликта интересов |
| Nunito | средне | «cannot boast a unique design, nor an exceptional quality of Cyrillic» |
| Finlandica, Ysabeau | с осторожностью | «not ideal, though generally usable» |
| Ubuntu | с осторожностью | у каждого начертания свои проблемы |
| **Inter** | **не рекомендуют** | «its Cyrillic extension lacks attention to details for achieving an acceptable standard, so it should not be used». Обновление 2023 года проблему не решило |
| **Roboto** | **не рекомендуют** | «the quality of this Cyrillic is questionable… If possible, we recommend using something else»; если приходится — брать средние веса |
| **Manrope** | **нельзя** | «unconvincing conceptually and of poor implementation — a bad choice no matter what your task is» |
| **Fira Sans** | **нельзя** | «stay away from Cyrillic, please — sad to say, it is a true failure» |
| **Source Sans 3** | **не рекомендуют** | «minor improvements in the new version still do not let us consider it high-quality» |
| Open Sans | не рекомендуют, особенно жирные | «you better avoid using its Cyrillic — especially in the bolder weights» |
| Arimo | нельзя для кириллицы | латиницей заменяет Arial, кириллицей нет |
| Oswald, Overpass, Alumni Sans, Exo 2, Istok Web, Andika, M Plus 1p, Ruda, Lunasima, Bellota Text | нельзя | у всех перечислены множественные ошибки |
| Alegreya Sans | с осторожностью; капители нельзя | |
| Carlito | не стоит брать вместо Calibri | |

Независимое подтверждение по Inter: Алексей Бурба `[S15]` — «у Inter-а странная кириллица… буквы „д“ и „л“
себя выдают. Как я понял, в команде не было русскоязычных дизайнеров». Тот же дефект, найденный независимо.

### 3.3. Список шрифтов с качественной кириллицей и лицензией OFL

Основной рабочий список для генеративной системы. Метрики — собственные измерения `[S24]`, поддержка и оси —
метаданные Google Fonts `[S20]`, оценка кириллицы — `[S13]`, `[S14]` где есть.

**1. Golos Text** (Paratype: Александра Королькова, Виталий Кузьмин; OFL)
Нейтральный закрытый гротеск, спроектирован для длительного чтения с экрана и для государственных и
социальных сервисов. x-height 0.530 em, cap 0.700, ширина строчной 0.545 em, кириллица шире латиницы в
1.128 раза (одна из самых экономных). Веса 400–900, переменная ось `wght` 400–900, **Light нет**, курсивов
нет. Есть `tnum` и `pnum`, lining и oldstyle цифры. Метрики строки 1.20. Вертикальные элементы в овалах
сделаны «for them to be better rendered on a pixel grid» `[S13]`. Свободный межбуквенный просвет: в плотной
таблице потребует чуть больше ширины колонки.
**Брать, когда**: продукт русскоязычный по умолчанию, нужна спокойная нейтральная подача, длинные тексты.

**2. Onest** (Simpals, Молдова: Dmitri Voloshin, Andrey Kudryavtsev, март 2023; OFL)
Смесь геометрического и гуманистического гротеска, позиционируется как бесплатная альтернатива SF Pro `[S32]`.
x-height 0.527, cap 0.707, ширина строчной 0.527, кир/лат 1.129. Веса 100–900 + переменная ось `wght`,
курсивов нет. Есть `tnum`, `pnum`, `calt`. Метрики строки 1.275, `usWinAscent+Descent` 1.546 — на Windows
может давать более высокие строки, проверяй.
**Брать, когда**: нужен современный «не-Inter» вид, компактность, кириллица как родной скрипт.
**Оговорка**: экспертной рецензии type.today на Onest нет `[спорно]`.

**3. IBM Plex Sans** (Mike Abbink, Bold Monday; кириллица — Александра Самуленкова; OFL)
Статический модернистский гротеск с характерными угловато-геометрическими деталями. x-height 0.516,
cap 0.698, ширина строчной 0.505 (узкий), **но кириллица шире латиницы в 1.173 раза** — русский набор
получается заметно шире английского. Веса 100–700 + оси `wdth` 75–100 и `wght`, есть настоящие курсивы.
**Цифры табличные по умолчанию**, `tnum` не нужен. Метрики строки 1.30. Семья включает Serif, Mono,
Condensed (у Condensed кириллицы нет `[S13]`).
**Брать, когда**: нужен технический, «инженерный» характер, корпоративная строгость, единый набор
sans + serif + mono.

**4. Commissioner** (Kostas Bartsokas; OFL)
Гуманистический гротеск ренессансных пропорций с переменными осями `FLAR` (0–100, «изысканность»),
`VOLM` (0–100, геометричность штриха), `slnt` −12–0, `wght` 100–900. x-height **0.496** (низкий),
cap 0.713, x/cap 0.696. Кир/лат 1.154.
**Критическое ограничение: цифры пропорциональные и фичи `tnum` нет** `[S24]` — для таблиц с числами не
годится без ручной подмены.
**Брать, когда**: контентный продукт с длинным текстом, база 16 px и больше, чисел немного.

**5. PT Sans** (Paratype: Александра Королькова, Ольга Умпелева, Владимир Ефимов; OFL)
Гуманистический гротеск, изначально адаптирован под низкое разрешение, «very decent hinting», инктрапы
`[S14]`. x-height 0.500, ширина строчной **0.481 — самая узкая из проверенных**, кир/лат **1.120 — самое
экономное отношение**. Цифры табличные по умолчанию. Настоящий курсив. Подсемейства PT Sans Narrow (плотный
набор) и PT Sans Caption (выше и шире строчные, крупнее инктрапы — для мелких кеглей).
**Ограничения**: только веса 400 и 700, **переменного файла нет**, «appears fairly light in typesetting —
and shall be balanced by enough white space» `[S14]`.
**Брать, когда**: нужен максимально компактный русский набор и хватает двух весов; или как Caption-вариант
для 11–12 px.

**6. Geist** (Vercel + Basement Studio; кириллица — Guido Ferreyra, версия 1.7.0 от 29.01.2026; OFL)
Швейцарский по духу геометризованный гротеск. x-height 0.530, cap 0.710, ширина строчной 0.534,
кир/лат 1.151. Веса 100–900 + переменная ось `wght`, курсивы с 1.5.0 (май 2025). Есть `tnum`, `pnum`.
Парный Geist Mono с той же метрикой и псевдографикой для терминалов.
**Брать, когда**: продукт для разработчиков, дашборды, нужен современный «вercel-вид» и единая пара
sans + mono.
**Оговорка**: кириллица очень молодая (январь 2026), экспертных рецензий нет `[спорно]`.

**7. Noto Sans** (Google; кириллица обновлена в 2024, Jovana Jocić; OFL)
Нейтральный гротеск с максимальным языковым покрытием. x-height 0.536, cap 0.714, ширина строчной 0.530,
кир/лат 1.156. Оси `wdth` 62.5–100, `wght` 100–900, курсивы. Цифры табличные по умолчанию, плюс `tnum`
и `pnum`.
**Брать, когда**: нужна поддержка многих языков одним семейством и нет требований к характеру.
**Оговорка**: эксперты type.today отказались оценивать из-за конфликта интересов `[S14]`.

**8. Rubik** (Hubert & Fischer; OFL)
Гротеск со слегка скруглёнными углами, мягкий характер. x-height 0.520, cap 0.700, ширина строчной 0.531,
кир/лат 1.136. Веса 300–900 + переменная ось, курсивы. Есть `tnum`.
**Брать, когда**: нужен дружелюбный, не-корпоративный тон (сервисы для людей, образование, медицина).
**Оговорка**: экспертной рецензии нет `[спорно]`.

**9. Wix Madefor Text** (Wix; OFL)
Текстовый гротеск с крупными прописными. x-height 0.492 (низкий), cap 0.715, x/cap 0.688,
ширина строчной 0.529, кир/лат 1.126 (экономная кириллица). Веса 400–800 + переменная ось, курсивы.
**Критическое ограничение: цифры пропорциональные, `tnum` нет** `[S24]`.
**Брать, когда**: контентные страницы кабинета, база 16 px, чисел немного.

**10. JetBrains Mono** (JetBrains; OFL) — моноширинный
x-height **0.550 — самый высокий из всех проверенных**, cap 0.730, ширина знака 0.600 em.
Веса 100–800 + переменная ось, курсивы, есть кириллица. Лигатуры для кода в `calt` (включены по умолчанию —
для таблиц и идентификаторов отключай).
**Брать, когда**: код, id, ключи, логи.

**11. IBM Plex Mono** (Bold Monday; OFL) — моноширинный
x-height 0.516, ширина знака 0.600 em, веса 100–700 + курсивы, кириллица есть, переменного файла нет.
Идеально парится с IBM Plex Sans (одинаковые метрики и рисунок).

**12. Geist Mono** (Vercel; OFL) — моноширинный
x-height 0.530, ширина знака 0.600 em, веса 100–900 + переменная ось, курсивы, кириллица с 1.7.0.
**Важно**: с версии 1.7.0 программистские лигатуры перенесены в `ss11` и по умолчанию выключены `[S19]` —
это ровно то поведение, которое нужно в таблицах.

Сводная таблица:

| шрифт | класс | x-h | кир/лат | веса | перем. | tnum | курсив | оценка кириллицы |
|---|---|---|---|---|---|---|---|---|
| Golos Text | неогротеск | 0.530 | 1.128 | 400–900 | да | да | нет | эксперты: годится `[S13]` |
| Onest | нео/геометр. | 0.527 | 1.129 | 100–900 | да | да | нет | не рецензирован |
| IBM Plex Sans | неогротеск | 0.516 | 1.173 | 100–700 | да | по умолчанию | да | эксперты: высокое качество `[S13]` |
| Commissioner | гуманист. | 0.496 | 1.154 | 100–900 | да | **нет** | да (не в GF) | эксперты: годится `[S14]` |
| PT Sans | гуманист. | 0.500 | 1.120 | 400, 700 | нет | по умолчанию | да | эксперты: годится `[S14]` |
| Geist | неогротеск | 0.530 | 1.151 | 100–900 | да | да | да | новая (01.2026), не рецензирована |
| Noto Sans | неогротеск | 0.536 | 1.156 | 100–900 | да | да | да | обновлена в 2024, не оценена |
| Rubik | неогротеск | 0.520 | 1.136 | 300–900 | да | да | да | не рецензирован |
| Wix Madefor Text | неогротеск | 0.492 | 1.126 | 400–800 | да | **нет** | да | не рецензирован |
| JetBrains Mono | моно | 0.550 | 1.000 | 100–800 | да | моно | да | не рецензирован |
| IBM Plex Mono | моно | 0.516 | 1.000 | 100–700 | нет | моно | да | пара к Plex Sans |
| Geist Mono | моно | 0.530 | 1.000 | 100–900 | да | моно | да | пара к Geist |

### 3.4. Шрифты без кириллицы (проверено в метаданных Google Fonts `[S20]`)

Не подойдут для русского интерфейса ни при каких условиях:
**Poppins, Public Sans, Lato, DM Sans, Space Grotesk, Outfit, Sora, Figtree, Instrument Sans, Albert Sans,
Schibsted Grotesk, Gabarito, Bricolage Grotesque.**

Отдельный случай: **Plus Jakarta Sans** и **Hanken Grotesk** отмечены как `cyrillic-ext`, но **без базового
`cyrillic`**. Базовый русский диапазон у них не покрыт, при наборе часть букв уйдёт в фолбэк — брать нельзя.

Отдельный случай: **Jost** — есть `cyrillic`, но нет `cyrillic-ext` (не покрыты расширенные знаки
украинского, казахского и др.).

Serif с кириллицей, если нужен «редакторский» режим: Merriweather (`opsz` 18–144, `wdth`, `wght` 300–900),
Literata (`opsz` 7–72, `wght` 200–900), Lora (`wght` 400–700), Vollkorn, Spectral, Piazzolla (`opsz` 8–30),
Cormorant. IBM Plex Serif — пара к Plex Sans `[S1]`.

### 3.5. Тестовая строка для проверки шрифта

```
Шхуна «Ёж» ждёт: 0O Il1 — №5 ₽1 234,56
Съешь ещё этих мягких французских булок да выпей чаю
где кл дл Ыъь Йй Щщ Цц Дд Фф Зз Ююя
```

Что она показывает:
- «Ёж», «ждёт» — есть ли **ё** и не вылезают ли точки;
- «Шхуна», «Щщ» — ширина многоэлементных букв;
- `«»` — есть ли ёлочки (а не только программистские кавычки);
- `0O Il1` — различимость;
- `—` — длинное тире (не дефис);
- `№` — знак номера (в латинских шрифтах часто отсутствует);
- `₽` — знак рубля (появился в Unicode в 2014, есть не везде; в Alumni Sans он есть, но нарисован с ошибкой
  `[S13]`);
- `1 234,56` — пробел разряда и запятая как десятичный разделитель;
- «где», «кл», «дл» — кернинг проблемных пар `[S17]`;
- «Ыъь», «Йй», «Дд», «Фф», «Зз» — дефекты из §3.1.

---

## 4. Системный стек против веб-шрифта

### 4.1. Что такое системный стек и кто его использует

| система | стек |
|---|---|
| Tailwind v4 `[S9]` | `ui-sans-serif, system-ui, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'` |
| Radix Themes `[S18]` | `-apple-system, BlinkMacSystemFont, 'Segoe UI (Custom)', Roboto, 'Helvetica Neue', 'Open Sans (Custom)', system-ui, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji'` |
| Ant Design 5 `[S35]` | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'` |
| Mantine `[S37]` | `-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji` |
| Polaris `[S6]` | `'Inter', -apple-system, BlinkMacSystemFont, 'San Francisco', 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif` (веб-шрифт + системный фолбэк) |
| Carbon `[S1]` | `'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif` |
| Fluent 2 `[S3]` | Segoe UI, «the system defaults to native system fonts» на других платформах |

### 4.2. Плюсы и минусы

| | системный стек | веб-шрифт |
|---|---|---|
| Скорость | мгновенно, ноль запросов, ноль CLS | 20–150 КБ на вес, риск FOUT/CLS |
| Вид | разный на macOS (SF Pro), Windows (Segoe UI), Android (Roboto), Linux (что нашлось) | одинаковый везде |
| Кириллица | зависит от ОС; на Windows Segoe UI, на macOS SF Pro — качество нормальное | контролируется |
| Метрики | разные: вертикальные метрики SF Pro, Segoe UI и Roboto не совпадают, строки «прыгают» | одни и те же |
| Цифры | SF Pro и Segoe UI — пропорциональные по умолчанию; `tnum` доступен | под контролем |
| Бренд | никакого | свой |
| Дизайн-контроль | шкалу приходится настраивать по худшему x-height | шкала настраивается точно |

### 4.3. Когда что

- **Системный стек**: внутренние админки без требований к бренду; прототипы; продукты, где критичны
  первый рендер и вес; интранет с плохим каналом.
- **Веб-шрифт**: любой продукт с брендом; любой продукт, где важны плотные таблицы (нужен предсказуемый
  x-height и `tnum`); любой русскоязычный продукт, где качество кириллицы важно (у системных шрифтов оно
  «какое есть»).
- **Гибрид** (как у Polaris): веб-шрифт первым, системный стек следом как фолбэк — рабочий дефолт.

### 4.4. `system-ui` и его ловушки

`system-ui` разрешается в системный UI-шрифт; на Windows это Segoe UI, на macOS — San Francisco, на Android —
Roboto. Tailwind v4 перешёл именно на `ui-sans-serif, system-ui` `[S9]`. Известная проблема: в старых сборках
Chrome на Linux и в некоторых локалях `system-ui` мог давать шрифт без кириллицы. Безопаснее писать
`system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`, как делают Ant Design и Mantine.

---

## 5. Загрузка шрифтов

### 5.1. `font-display`

| значение | поведение | когда |
|---|---|---|
| `swap` | текст сразу фолбэком, потом подменяется | дефолт для интерфейса при наличии метрического фолбэка |
| `optional` | браузер сам решает; при медленном канале шрифт не применится до следующей загрузки | когда нельзя допустить ни одного сдвига |
| `block` | до 3 с невидимый текст | почти никогда |
| `fallback` | 100 мс невидимый, затем фолбэк, окно подмены 3 с | компромисс |

`swap` без метрического фолбэка даёт заметный скачок вёрстки; Chrome называет это «the jarring effect» `[S25]`.

### 5.2. Метрические фолбэки: рецепт целиком

Источник: Chrome for Developers, Katie Hempenius `[S25]`.

Простой вариант (только overrides, значения из **веб-шрифта**, поэтому одинаковы для любого локального
фолбэка):

```
ascent-override   = ascent   / unitsPerEm
descent-override  = descent  / unitsPerEm
line-gap-override = line-gap / unitsPerEm
```

Точный вариант (полностью убирает сдвиг):

```
size-adjust       = avgCharacterWidth(веб-шрифт) / avgCharacterWidth(фолбэк)
ascent-override   = ascent   / (UPM × size-adjust)
descent-override  = descent  / (UPM × size-adjust)
line-gap-override = line-gap / (UPM × size-adjust)
```

`avgCharacterWidth` точно считается только для моноширинных; для остальных — средняя ширина `[a-z\s]`,
лучше взвешенная по частотности букв `[S25]`. **Для русского интерфейса усредняй по кириллице**: у неё
средняя ширина на 12–20 % больше `[S24]`, иначе фолбэк будет систематически уже.

Пример из источника (Poppins, UPM 1000, ascent 1050, descent 350, line-gap 100):

```css
body { font-family: "Poppins", poppins-fallback, poppins-fallback-android, sans-serif; }
@font-face {
  font-family: poppins-fallback;
  src: local("Arial");
  size-adjust: 60.85099821%;
  ascent-override: 164.3358416%;
  descent-override: 57.51754455%;
  line-gap-override: 16.43358416%;
}
@font-face {
  font-family: poppins-fallback-android;
  src: local("Roboto");
  size-adjust: 55.5193474%;
  ascent-override: 180.1173909%;
  descent-override: 63.04108683%;
  line-gap-override: 18.01173909%;
}
```

Какие фолбэки выбирать: **Arial для sans, Times New Roman для serif**; на Android их нет, там только Roboto,
поэтому объявляют два синтетических фолбэка плюс generic-семейство `[S25]`.

Какие метрики применяет браузер `[S25]`:

| | macOS | Windows |
|---|---|---|
| Chromium | `hhea` | `typo` при флаге `USE_TYPO_METRICS`, иначе `win` |
| Firefox | `typo` при флаге, иначе `hhea` | `typo` при флаге, иначе `win` |
| Safari | `hhea` | `typo` при флаге, иначе `win` |

Для ~90 % шрифтов Google Fonts значения overrides совпадают для всех трёх таблиц, поэтому разделять по ОС не
нужно `[S25]`.

Готовые инструменты: `next/font` (с Next 13 ставит overrides и `size-adjust` автоматически), `@nuxtjs/fontaine`,
`fontaine` (unjs), датасет метрик всех шрифтов Google Fonts (github.com/khempenius/font-fallbacks-dataset),
Capsize, fontkit, fontdrop.info `[S25]`.

**Почему это важно именно для русского**: измеренный разброс метрик строки (`line-height: normal`) —
от 1.172 (Roboto) до 1.424 (Source Sans 3) `[S24]`, а `usWinAscent + usWinDescent` доходит до 1.55–1.56
у Onest и Montserrat. Без overrides строки в таблице подпрыгнут на несколько пикселей в момент подмены.

### 5.3. Сабсеттинг кириллицы

Google Fonts делит шрифт на подмножества и отдаёт `@font-face` с `unicode-range`; браузер скачивает только
нужные диапазоны. При самостоятельном хостинге повторяй ту же схему:

```css
/* cyrillic */
@font-face {
  font-family: 'Golos Text';
  font-style: normal;
  font-weight: 400 900;
  font-display: swap;
  src: url('/fonts/golos-cyrillic.woff2') format('woff2-variations');
  unicode-range: U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116;
}
/* latin */
@font-face {
  font-family: 'Golos Text';
  font-style: normal;
  font-weight: 400 900;
  font-display: swap;
  src: url('/fonts/golos-latin.woff2') format('woff2-variations');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215;
}
```

Заметь: **U+2116 (№) входит в кириллический диапазон**, а `₽` (U+20BD) в стандартный латинский диапазон
Google Fonts не входит — при своём сабсеттинге его нужно включить явно.

Практика:
- порядок: `preconnect` → `preload` критического файла (обычно кириллический regular) → `@font-face`;
- переменный файл сабсетить по весам не нужно, он один;
- 2 подмножества (latin, cyrillic) достаточно; latin-ext нужен, только если в интерфейсе встречаются
  европейские имена с диакритикой.

### 5.4. Сколько весить

Ориентиры (woff2, подмножество cyrillic, переменный файл): 25–60 КБ на подмножество. Статические файлы:
15–30 КБ на вес и подмножество. **Четыре статических веса латиницы и кириллицы = 8 файлов, 120–240 КБ.**
Переменный файл в такой ситуации экономит примерно вдвое.

---

## 6. Пары гарнитур и вторая гарнитура

### 6.1. Обычный ответ: вторая гарнитура не нужна

- Apple: «Minimize the number of typefaces you use, even in a highly customized interface» `[S4]`.
- Untitled UI: «limit your designs to using just one typeface… If you absolutely need to, use a maximum of
  two. Often, modern fonts come with enough variable weights to effectively act as several fonts at once»
  `[S32]`.
- Все изученные дизайн-системы используют ровно одну текстовую гарнитуру плюс моноширинную: Carbon (Plex
  Sans + Plex Mono + Plex Serif для цитат), Atlassian (Atlassian Sans + Atlassian Mono), Polaris (Inter +
  системная моно), Fluent (Segoe UI), Material (Roboto).
- Исключение в документации: Atlassian держит **отдельный бренд-шрифт Charlie Sans только для маркетинга**,
  а в продукте — Atlassian Sans `[S10]`. Это и есть граница: вторая гарнитура живёт в маркетинге.

### 6.2. Когда вторая гарнитура всё-таки оправдана

- Заголовки в продукте с сильной айдентикой (страницы входа, онбординг, пустые состояния). Erik Kennedy:
  «Headers & subheads are the best place to add a second font» `[S12]` — но он пишет про сайты, а не про
  админки.
- Дисплейный шрифт для цифр KPI на дашборде — редко и с осторожностью.
- Парные семьи от одного автора: Mona Sans + Hubot Sans (GitHub, OFL) `[S32]`, IBM Plex Sans + Plex Serif +
  Plex Mono `[S1]`, Geist + Geist Mono `[S19]`. Такие пары безопасны, потому что у них общие метрики.

### 6.3. Serif в интерфейсе

Butterick `[S26]`: «On the web, body text can be in a sans serif or serif font. Sans serifs were once preferred
for screen text because they rendered better on the lower-resolution screens of the past… But on today's
screens, serif fonts look equally good.»

Где serif работает в вебсервисе `[мнение]`:
- тело документа в редакторе («notion-подобный» режим): длинное чтение и письмо;
- цитаты и отзывы (Carbon использует IBM Plex Serif именно для `fluid-quotation-01/02` `[S2]`);
- Radix Themes по умолчанию отдаёт `<Em>` и `<Quote>` в `'Times New Roman', Times, serif` с
  `--em-font-size-adjust: 1.18` `[S18]` — интересный приём: при подмене гарнитуры размер компенсируется
  коэффициентом.

Где serif не работает: таблицы, формы, плотные панели, навигация, кнопки.

Для русского serif подойдут Literata, Merriweather, Lora, Vollkorn, Spectral, IBM Plex Serif `[S20]`.

---

## 7. Моноширинные

### 7.1. Где нужны

| случай | почему |
|---|---|
| код и фрагменты команд | по определению |
| идентификаторы, ключи API, хеши, номера заказов | различимость `0O`, `Il1`, побуквенное сравнение |
| колонка с длинными числами, где нет `tnum` у основного шрифта | выравнивание разрядов |
| логи, diff, трассировки | выравнивание столбцов |
| маска ввода (телефон, карта) | символы не прыгают при наборе |

Где **не** нужны: обычные числа в таблице (хватает `tabular-nums` у основного шрифта), цены, даты, KPI.

### 7.2. Размер и настройки

- **На 1–2 px мельче основного** в той же строке: Radix `--code-font-size-adjust: 0.95` `[S18]`;
  Atlassian: `font.code` 12 px при теле 14 px, а инлайновый код относителен контейнеру и даёт 12.25 px `[S10]`;
  Carbon: `code-01` 12 px при `body-01` 14 px `[S2]`.
- Интерлиньяж: Carbon `code-01` 12/16 (1.33), Atlassian `font.code` 12/20 (1.67) — для блока кода просторнее,
  для инлайнового «line height is equal to the font size» `[S10]`.
- Трекинг: Radix задаёт `--code-letter-spacing: -0.007em` `[S18]`.
- **Лигатуры отключать**: `font-variant-ligatures: none` или `font-feature-settings: 'liga' 0, 'calt' 0`.
  Geist Mono 1.7.0 вынес программистские лигатуры в `ss11` именно потому, что в 1.7.0 они случайно
  активировались через `liga` и «broke monospace alignment in code» `[S19]`.

### 7.3. Варианты с кириллицей

JetBrains Mono (x-height 0.550), IBM Plex Mono (0.516), Geist Mono (0.530), Roboto Mono (0.528) — у всех
кириллица есть, ширина знака ровно 0.600 em `[S24]`, `[S20]`.
Системный моно-стек как фолбэк:
`ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace`
(так у Tailwind v4 `[S9]`, Polaris `[S6]`, Mantine `[S37]`).

---

## 8. Что говорят шрифтовой дизайнер и практики (видеоисточники)

Дайджесты лежат в `../91-videos/digests/`. Ссылки вида `[V15]` указывают на файл дайджеста, таймкоды — на
исходное видео.

### 8.1. Александра Королькова (ParaType, автор PT Sans, PT Serif, Circe, Golos), лекция 2025 `[V15]`

Единственный найденный источник, где типографика интерфейса разбирается с позиции шрифтового дизайнера и
на кириллице.

| правило | детали |
|---|---|
| **Не качай шрифты с агрегаторов «100 000 бесплатных шрифтов»** | причина не в лицензии, а в качестве: у большинства файлов сломан контур и разъехались межбуквенные расстояния `[01:00]` |
| **Читай подсказку в имени гарнитуры** | Caption, Text, Subhead, Headline, **Display** — это рекомендованный кегль применения. «Display — это витрина, а не монитор»: такой шрифт для крупного набора, а не для мелкого экранного `[07:11]` |
| **Оцени контур увеличением** | в мелком размере кривой и ровный шрифт неразличимы; при увеличении видно, что тонкие линии «гуляют» по толщине, контур ломается у петли, линия приплющена `[10:13]`, `[12:15]` |
| **Смотри на межбуквенные расстояния** | равные отступы у всех букв математически не работают: между прямыми и треугольными буквами дыры, между прямыми теснота. Расстояния ставятся глазами; по дырам видно, поленился ли автор `[14:17]` |
| **Параметры удобочитаемости регулярного начертания** | ширина примерно **65–95 %** для прописной и **65–75 %** для строчной (от высоты), плюс соотношение толщины штриха к высоте. Чем дальше от регулярного, тем хуже читается длинный мелкий текст `[27:35]` |
| **Для мелкого экранного текста нужны высокие строчные и большие межбуквенные расстояния** | кейс macOS: Lucida Grande работала лучше сменившей её Helvetica, у которой «очень плотное межбуквенное расстояние для интерфейсного шрифта»; San Francisco вернула и расстояния, и высоту строчных. «Разница в пределах пары-тройки процентов реально работает, когда речь о мелком размере или о большом объёме текста» `[30:39]`–`[33:42]` |
| **Узкий шрифт экономит меньше, чем кажется** | эксперимент автора: три гарнитуры, кегли подобраны так, чтобы строчная «н» занимала одинаковую площадь; разница в ёмкости набора — **около 6 %**. В интерфейсных подписях (меню, «О нас») разница не видна. Ширина влияет **на настроение**, а не на вместимость `[28:37]` |
| **Для кодов и промокодов нужен особый знаковый состав** | перечёркнутый ноль, тройка с плоским верхом, L с крючком, засечки у прописной I `[33:42]` |
| **Экспериментальные конструкции знаков и болгарскую кириллицу в текст не ставь** | болгарские формы (круглая «в» с верхним выносным, курсивные «й», «п», «т» в прямом начертании) в заголовке и логотипе допустимы, в тексте читатель спотыкается `[36:47]` |
| **Почему «непривычный» рисунок тормозит чтение** | большинство взрослых не-дизайнеров не помнит конструкции прямых строчных: учат прописные (при чтении) и рукописные (при письме) `[34:44]` |
| **Соседние начертания — это адаптация к условиям** | шире для мелкого с большого расстояния, уже для уплотнения, **жирнее для светлой темы, светлее для тёмной** `[40:53]` |
| **Вариативный шрифт меняет параметры на лету** | по ширине окна, по теме. «Нельзя просто сказать фронтендеру поставь вариативный шрифт»: с весом справляются, **с шириной — часто нет** `[41:54]` |
| **Если нужны все письменности — Noto, альтернатив по сути нет** | для отдельных письменностей варианты появляются `[1:02:25]` |
| **Кегль не равен высоте буквы: прописная ≈ 70 % кегля** | кегельная площадка досталась от металлического набора `[1:09:35]` |
| **Два шрифта в одной строке не встают на одну базовую линию** | у гарнитур разные вертикальные метрики и разное положение знака на площадке; автор проводила эксперименты и **не смогла объяснить поведение части гарнитур** `[1:10:37]` `[спорно]` |

Про сочетания гарнитур `[V15]` `[1:01:25]`–`[1:08:34]`:
1. самое простое — **акцидентный очень крупно + текстовый очень мелко**, «думать вообще не надо»;
2. сложнее — **заметная разница плюс общий признак**: один с засечками, другой без; один контрастный, другой
   нет; при этом оба узкие, или оба моноширинные, или из одной эпохи;
3. для текстовых пар классика — нейтральный гротеск + нейтральная антиква.
Главный критерий: сочетание не должно казаться случайным.

Сходится с измеренным в §2: «высокие строчные плюс большие межбуквенные расстояния для мелкого» — это ровно
связка x-height ≥ 0.52 em и неплотный набор; «разница ёмкости около 6 %» согласуется с тем, что у большинства
интерфейсных гротесков средняя ширина строчной укладывается в 0.50–0.55 em, и только крайние значения
(Source Sans 3 0.475, Montserrat 0.574) выходят за этот коридор.

### 8.2. Steve Schoger (Refactoring UI), доклады 2018 и 2019 `[V02]`, `[V01]`

| правило | детали |
|---|---|
| **Фильтр для Google Fonts** | sans-serif + сортировка по популярности + **наличие 8 начертаний** (regular, bold, light, semibold и курсивы к ним). «Огромный выбор, но большая часть плохо подходит для UI» `[V02 42:41]` |
| **Шрифты не взаимозаменяемы** | при замене надо подстраивать кегль и вес; пример: у Museo bold заметно тяжелее, чем у Proxima Nova `[V02 43:46]` |
| **Системный стек — нормальный выбор для приложения** | кастомный шрифт нужнее на маркетинговых страницах `[V01 36:01]` |
| **Как искать шрифт** | DevTools на понравившемся сайте → название → сайт словолитни (в докладах названы Hanken Design, Commercial Type, Klim Type Foundry) `[V01 36:01]` |

Критерий «8 начертаний» у Schoger, «5+ весов» у Refactoring UI `[S40]` и Untitled UI `[S32]` — три независимые
формулировки одного правила: число начертаний коррелирует с качеством проработки гарнитуры `[консенсус]`.
Совпадает и с измерением `[S24]`: у PT Sans всего два веса и нет переменного файла, и это его главное
ограничение при хорошем качестве рисунка.

---

## Частые ошибки

### Общие

1. **Шрифт выбран по картинке из дрибббла, без проверки кириллицы.** Половина «модных» гротесков её вообще
   не имеет (§3.4), у другой половины она плохая (§3.2).
2. **Три гарнитуры в одном приложении** (заголовки, текст, акценты). Apple прямо называет это причиной
   потери иерархии `[S4]`.
3. **Геометрический шрифт (Poppins, Montserrat) в таблице с числами.** Широкий, низкие счётчики, часто без
   настроенных цифр.
4. **Шрифт без `tnum` и без моноширинных цифр в финансовой таблице** (Commissioner, Wix Madefor Text) `[S24]`.
5. **Light/Thin в интерфейсе.** Apple: избегать `[S4]`.
6. **Веб-шрифт без `font-display` и без фолбэка.** 1–3 секунды невидимого текста.
7. **Веб-шрифт без метрического фолбэка.** Скачок вёрстки при подмене `[S25]`.
8. **Латиница и кириллица одним файлом без `unicode-range`.** Лишние 30–60 КБ для тех, кому кириллица не нужна.
9. **Шрифт с Google Fonts там, где нужны `ss*`/`cv*`** (различимость `Il1` у Inter): в субсетах их нет `[S24]`.
10. **Моноширинный того же кегля, что основной текст.** Выглядит крупнее из-за большей ширины знака.
11. **Лигатуры кода включены в таблице идентификаторов.** `!=`, `->`, `==` склеиваются `[S19]`.

### Характерные для нейросетей

12. **«Inter везде» как рефлекс.** Inter действительно хорош для интерфейса, но для русскоязычного продукта
    у него признанно слабая кириллица `[S13]`, `[S15]`. Правило проверки: если 80 % текста интерфейса русский,
    поставь Golos Text или IBM Plex Sans и сравни на тестовой строке (§3.5).
13. **Обратная крайность: экзотический шрифт «для уникальности».** Untitled UI: «you should ignore 99 % of
    these new fonts… 99 % of modern fonts are low-quality» `[S32]`.
14. **Poppins / Montserrat в заголовках приложения** — самый частый генеративный след. Оба геометрические,
    Poppins вообще без кириллицы `[S20]`.
15. **Стек `font-family: Inter, sans-serif` без подключённого `@font-face`.** Сгенерированная страница
    отрисуется системным гротеском, и вся настроенная шкала уедет (§10 в `02-type-scale.md`).
16. **Вторая гарнитура «для заголовков», взятая из маркетингового набора** (Playfair, Cormorant, Space Grotesk)
    в админке.
17. **Копирование font-stack из чужой системы вместе с названием шрифта, который не подключён.**
    Например `font-family: 'Atlassian Sans'` — этот шрифт раздаётся только внутри Atlassian Mosaic `[S10]`.

---

## Чек-лист

1. В приложении ровно одна текстовая гарнитура и, при необходимости, одна моноширинная? Да / нет.
2. У выбранного шрифта есть подмножество `cyrillic` (не только `cyrillic-ext`)? Да / нет.
3. Кириллица проверена на тестовой строке из §3.5: «б», «д», «л», «ф», «з», «Ы», «й», «ё», «№», «₽»? Да / нет.
4. x-height ≥ 0.52 em при базе 14 px (≥ 0.50 при базе 16)? Да / нет.
5. Есть веса 400, 500 (или 550/600) и 600 (или 650)? Да / нет.
6. Цифры табличные по умолчанию либо есть фича `tnum`? Да / нет.
7. Лицензия позволяет самостоятельный хостинг и сабсеттинг (OFL или эквивалент)? Да / нет.
8. Шрифт подключён с `font-display: swap` и метрическим фолбэком (`size-adjust` + `*-override`)? Да / нет.
9. Латиница и кириллица разведены по `unicode-range`? Да / нет.
10. Знаки `№` (U+2116) и `₽` (U+20BD) входят в собранное подмножество? Да / нет.
11. `0`, `O`, `I`, `l`, `1` различимы на 12 px? При необходимости включены `ss02`/`cv05`/`cv08`/`zero`? Да / нет.
12. Моноширинный на 1–2 px мельче основного, лигатуры кода выключены вне блоков кода? Да / нет.
13. Шрифт проверен на Windows без Retina при 100 % масштабе на кеглях 12 и 14 px? Да / нет.
14. Если шрифт переменный, подключён один файл с диапазоном весов, а не 5 статических? Да / нет.
15. Системный фолбэк в стеке покрывает macOS, Windows, Android? Да / нет.

---

## Открытые вопросы и противоречия

1. **Onest, Geist, Rubik, Wix Madefor Text не рецензированы шрифтовыми экспертами по кириллице.** Метрики я
   измерил, но качество рисунка оценить не могу. Для Geist кириллица вообще появилась только в январе 2026
   `[S19]`. Нужна отдельная экспертиза или хотя бы сравнение с эталоном.
2. **Montserrat**: в прочитанных статьях type.today его нет (вероятно, он в невыпущенном эпизоде о
   геометрических). Измерения показывают, что он самый широкий из проверенных (0.574 em), но это не оценка
   качества кириллицы. `[спорно]`
3. **PT Root UI и Golos UI** (Paratype) — по отзывам в русскоязычных обзорах у них «очень качественная
   кириллица» и униширинные начертания (Uniwidth: ширина строки не меняется при смене веса), но официальные
   страницы Paratype отдаются только как SPA, значения и условия лицензии я не проверил. Требует проверки.
4. **Yandex Sans / YS Text, SB Sans** — корпоративные шрифты, условия использования вне компании не проверены.
5. **Качество хинтинга на Windows** ни у одного источника не дано в измеримом виде. Все утверждения в §2.8 —
   пересказ формулировок авторов шрифтов. `[спорно]`
6. **Насколько `cyrillic-ext` без `cyrillic` ломает русский набор** — вывод логический (базовый диапазон
   U+0400-045F не покрыт), фактическую проверку рендеринга я не делал.
7. **Версия Inter на Google Fonts против версии с rsms.me.** Бурба в 2021 писал, что на Google лежит «крайне
   устаревшая версия» `[S15]`; на 2026 в метаданных Google уже есть ось `opsz` 14–32 (то есть Inter 4.x),
   но набор `ss*`/`cv*` в субсетах всё равно вырезан `[S24]`. Для полного набора фич подключай с rsms.me.
8. **Влияние ширины шрифта на реальную плотность таблиц** я оценил по средней ширине строчных; реальная
   ширина колонки зависит ещё от кернинга и от состава данных. Точный ответ даёт только верстка макета.

---

## Источники

- `[S1]` IBM Carbon. Typography — Overview. https://carbondesignsystem.com/elements/typography/overview/
- `[S2]` IBM Carbon. Typography — Type sets. https://carbondesignsystem.com/elements/typography/type-sets/
- `[S3]` Microsoft Fluent 2. Typography. https://fluent2.microsoft.design/typography
- `[S4]` Apple. HIG — Typography. https://developer.apple.com/design/human-interface-guidelines/typography
- `[S6]` Shopify Polaris tokens (`font.ts`, `text.ts`, `size.ts`). https://github.com/Shopify/polaris
- `[S9]` Tailwind CSS v4 `theme.css`. https://github.com/tailwindlabs/tailwindcss
- `[S10]` Atlassian Design System. Typography. https://atlassian.design/foundations/typography
- `[S12]` Erik D. Kennedy. The Responsive Website Font Size Guidelines, 2024. https://www.learnui.design/blog/mobile-desktop-website-font-size-guidelines.html
- `[S13]` type.today. Cyrillic on Google Fonts: Neo-Grotesques, 19.03.2024. Эксперты: М. Струков, И. Рудерман, Ю. Остроменцкий. https://type.today/en/journal/neo — экспертная рецензия качества кириллицы, самый авторитетный доступный разбор.
- `[S14]` type.today. Cyrillic on Google Fonts: Humanist Sans, 27.06.2024. https://type.today/en/journal/humanist
- `[S15]` Алексей Бурба. Шрифт Inter. http://burba.pro/inter-typeface/ — независимое подтверждение проблем «д» и «л»; мнение практика.
- `[S16]` Rasmus Andersson. Inter. https://rsms.me/inter/ — полный список OpenType-фич, рекомендации по подключению; первичный источник автора шрифта.
- `[S17]` Paratype. How to understand Cyrillic. https://info.paratype.com/how-to-understand-cyrillic/ — методика оценки качества кириллицы от шрифтовой студии.
- `[S18]` Radix Themes. Typography + `styles/tokens/typography.css`. https://www.radix-ui.com/themes/docs/theme/typography
- `[S19]` Vercel Geist: https://vercel.com/font и релизы https://github.com/vercel/geist-font/releases — дата появления кириллицы и история лигатур.
- `[S20]` Google Fonts metadata. https://fonts.google.com/metadata/fonts — первичные данные о подмножествах и переменных осях.
- `[S24]` Собственные измерения метрик 22 шрифтов (fontTools 4.65, TTF Google Fonts). Метод в `99-raw/notes/wave1/B-notes.md`, S24.
- `[S25]` Katie Hempenius. Improved font fallbacks. Chrome for Developers. https://developer.chrome.com/blog/font-fallbacks — формулы `size-adjust` и метрических overrides.
- `[S26]` Matthew Butterick. Practical Typography. https://practicaltypography.com
- `[S32]` Untitled UI. 31 Best Free Fonts for Modern UI Design in 2026. https://www.untitledui.com/blog/best-free-fonts
- `[S35]` Ant Design 5, `components/theme/themes/seed.ts`. https://github.com/ant-design/ant-design
- `[S40]` Sébastien Lavoie. Book summary: Refactoring UI. https://www.sglavoie.com/posts/2023/09/09/book-summary-refactoring-ui/ — конспект правил книги; вторичный источник.
- `[V01]` Дайджест: Steve Schoger, Refactoring UI (CSS Day 2019). `../91-videos/digests/01-schoger-refactoring-ui-css-day-2019.md`
- `[V02]` Дайджест: Steve Schoger, Little Details (Laracon 2018). `../91-videos/digests/02-schoger-little-details-laracon-2018.md`
- `[V15]` Дайджест: Александра Королькова, «Типографика в UX/UI-дизайне» (UPROCK, 2025, 1:13:44). `../91-videos/digests/15-korolkova-typography-cyrillic.md` — лекция шрифтового дизайнера ParaType; единственный найденный видеоисточник, где типографика интерфейса разбирается на кириллице.
- `[S37]` Mantine `default-theme.ts`. https://github.com/mantinedev/mantine
