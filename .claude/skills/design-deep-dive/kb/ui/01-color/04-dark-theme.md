# Тёмная тема

Волна 1 · агент A · 22.09.2026 · источников прочитано целиком: 34

Как выпустить тёмную тему, которая не является инверсией светлой: какие значения фона, как показывать слои без
теней, что делать с акцентами и статусами, и алгоритм автоматического вывода.

---

## Выжимка для агента

1. **Тёмная тема — не инверсия.** Проверено мной на Radix: шаг 9 в светлой и тёмной теме ОДИНАКОВ (blue9 #0090ff
   в обеих), шаги 1–8 уходят вниз, 10–12 вверх, и величина сдвига по светлоте меняется от −80 до +58 п.п. → §3.1
   `[система]`
2. **Фон не чёрный.** Material #121212 (OKLCH L 18.2 %), Radix slate1 #111113 (17.9 %), Primer #0D1117 (17.6 %),
   Ant #141414 (19.1 %), shadcn #0a0a0a (14.5 %), Tailwind gray-950 #030712 (13.0 %).
   **Рабочий коридор: OKLCH L 13–19 %.** → §2.1 `[консенсус]`
3. **Светлая тема по умолчанию для широкой аудитории, переключатель обязателен.** «In users with normal vision,
   light mode leads to better performance most of the time», но тёмная лучше при помутнении хрусталика
   (катаракта) [S25]. → §1 `[исследование]`
4. **Слои показываются светлотой, а не тенями.** Material: белый оверлей 0 % при 0 dp … 16 % при 24 dp; в кодлабе
   Google карточка = 2 %, нижняя панель = 12 % [S29]. → §4.1 `[система]`
5. **Шаг между поверхностями в тёмной теме больше, чем в светлой.** Material: светлая 90/92/94/96/98/100 (шаг 2
   тона), тёмная 4/10/12/17/22 (шаг 2–6 тонов) [S10]. → §4.2 `[система]`
6. **Границы через альфу белого 6–15 %.** shadcn: `--border: oklch(1 0 0 / 10%)`, `--input: oklch(1 0 0 / 15%)`
   [S15]. Одна альфа автоматически работает на любой поверхности. Цена: контраст границы 1.26–1.48:1. → §4.3
   `[система]`
7. **Текст не чистый белый.** Material: high emphasis 87 %, medium 60 %, disabled 38 % белого [S29]. Radix dark
   slate12 = #edeef0 (не #fff). Причина: избыточная яркость даёт галацию. → §5.1 `[консенсус]`
8. **Проверяй тёмную тему по APCA, не по WCAG.** Проверено мной: #9198A1 на #0D1117 даёт WCAG 6.50:1 (отлично),
   но APCA Lc −45.8 — ниже минимума Lc 60. → §5.2 `[исследование]`
9. **Акцент в тёмной теме светлее, чем в светлой.** Material: primary = тон 40 в светлой, тон 80 в тёмной; текст
   на нём — белый (тон 100) в светлой, тёмный (тон 20) в тёмной [S10]. → §6.1 `[система]`
10. **Hover в тёмной теме идёт ВВЕРХ по светлоте.** Radix: light blue10 (#0588f0) темнее blue9, dark blue10
    (#3b9eff) светлее blue9 [S3]. → §6.2 `[система]`
11. **Статусы в тёмной теме десатурируются и светлеют.** Radix dark red11 = #ff9592 (пастельный), тогда как light
    red11 = #ce2c31 [S3]. Fluent: «In dark mode, the colors of the shared palette shift in saturation and
    brightness to reduce eye strain» [S: Fluent 2]. → §6.3 `[система]`
12. **Насыщенные чистые цвета на тёмном фоне «вибрируют».** Снижай хрому у больших площадей; оставляй высокую
    только для мелких акцентов. → §6.3, §5.3 `[мнение]`
13. **Иллюстрации и изображения меняются, а не фильтруются.** Carbon: «Whenever possible, switch out assets
    entirely between modes»; если нельзя — прозрачный фон и подложка по теме. → §7 `[система]`
14. **Алгоритм вывода тёмной темы из светлой — в §8.** Пересчитываются поверхности, границы и текст; шаг 9
    (сплошной акцент) сохраняется; 10–12 зеркалируются с коррекцией.
15. **`color-scheme: light dark` обязателен**, иначе `light-dark()` не работает и системные контролы
    (скроллбары, чекбоксы по умолчанию) останутся светлыми [S20]. → §9.1 `[консенсус]`
16. **forced-colors — отдельный режим, не «третья тема».** Браузер выбрасывает `box-shadow`, `text-shadow` и
    не-url-овые `background-image`; элементы, различавшиеся только фоном, сливаются [S34]. → §9.3 `[консенсус]`
17. **Не делай только тёмную тему.** Исследования: светлая лучше для остроты и корректуры, особенно при мелком
    шрифте; ночью разница больше [S25]. → §1
18. **Тени в тёмной теме почти не работают** и не заменяют слои: тёмная тень на тёмном фоне невидима. Используй
    светлоту поверхности + границу. → §4.4 `[консенсус]`

---

## 1. Что говорят исследования

Обзор NN/g (Raluca Budiu, 02.02.2020) — обзор академической литературы, не собственное исследование NN/g [S25]:

| Исследование | Участники и задача | Результат |
|---|---|---|
| Piepenbrock et al., *Ergonomics*, 2013 | 18–33 и 60–85 лет, без болезней глаз; острота (Landolt C) и корректура | «Light mode won across all dimensions». У пожилых преимущество меньше в задаче на остроту. Метрики усталости (eyestrain, headache, muscle strain) — без значимой разницы |
| Piepenbrock et al., *Human Factors*, 2013 | корректура при разных размерах шрифта | «The positive-polarity advantage increased linearly as the font size was decreased». Участники разницы **не ощущали** |
| Dobres et al., *Applied Ergonomics*, 2017 (MIT AgeLab) | лексическое решение, дневное и ночное освещение, шрифт 3 и 4 мм | Днём разницы полярности нет; **ночью светлая тема быстрее**, особенно на мелком шрифте |
| Aleman, Wang, Schaeffel, *Scientific Reports*, 2018 | n = 7, чтение по часу | При светлой теме хориоидея истончается (маркер риска миопии), при тёмной утолщается. Малая выборка |
| Legge et al., 1985 | n = 7 с помутнением оптических сред (катаракта) | Все читали быстрее в тёмной теме. У людей с поражением центрального зрения полярность не влияла. Оговорка: ЭЛТ-мониторы |

Вывод NN/g дословно: «in users with normal vision, light mode leads to better performance most of the time»;
переключатель тёмной темы обязателен по трём причинам: возможные долгосрочные эффекты светлой темы, польза для
части людей с нарушениями зрения, просто предпочтения. «Applications meant for long-form reading… should offer a
dark-mode feature.» Использовать системное API (`prefers-color-scheme`) [S25].

Механизм преимущества светлой темы: при большем количестве света зрачок сужается → меньше сферических аберраций,
больше глубина резкости, меньше усилий на фокусировку [S25].

Carbon ссылается на тот же обзор NN/g и добавляет свою позицию: тёмный режим в IBM «not required as an IBM product
but is highly encouraged» [S: Carbon color usage].

---

## 2. Фон

### 2.1. Реальные значения

> Разрешение противоречия [C27]: коридор L 13–19 % подтверждён измерением (6 продуктов из 8 в 14–18 %); чистый чёрный — только осознанное решение под OLED, записанное в брифе. См. `../CONTRADICTIONS.md`.

Посчитано мной:

| Система | Фон | OKLCH L | Хрома | Белый текст: WCAG / APCA |
|---|---|---|---|---|
| Tailwind gray-950 | #030712 | 13.0 % | 0.027 | 20.13:1 / −107.8 |
| shadcn `.dark` background | #0a0a0a | 14.5 % | 0.000 | 19.80:1 / −107.7 |
| Tailwind zinc-950 | #09090b | 14.1 % | 0.004 | 19.90:1 / −107.8 |
| Primer dark neutral.1 | #0D1117 | 17.6 % | 0.014 | 18.92:1 / −107.4 |
| Radix gray dark 1 | #111111 | 17.8 % | 0.000 | 18.88:1 / −107.4 |
| Radix slate dark 1 | #111113 | 17.9 % | 0.004 | 18.86:1 / −107.4 |
| Material 2 | #121212 | 18.2 % | 0.000 | 18.73:1 / −107.3 |
| Ant Design | #141414 | 19.1 % | 0.000 | 18.42:1 / −107.1 |
| (антипример) чистый чёрный | #000000 | 0 % | 0.000 | 21.00:1 / −107.9 |

**Коридор: OKLCH L 13–19 %.** Разброс по WCAG между всеми этими фонами — всего 18.4–20.1:1, то есть практически
не важен. Важно другое: у чистого чёрного L = 0, и это выпадает из ряда.

Почему не чёрный:
- «Excess contrast is nearly always due to excess brightness. When something is so contrasty that it seems to have
  "halos", the first thing to try is to make the lightest element a little darker» [S19];
- Datawrapper: «don't go full black — keep your lightness between 10 % and 25 %» (в HSB) [S23];
- на OLED чистый чёрный даёт «smearing» при прокрутке (пиксели выключаются и включаются с задержкой) — часто
  упоминаемый аргумент, но подтверждения в прочитанных мной источниках я **не нашёл**; помечаю как непроверенное.

### 2.2. Тонировка фона

| Система | Хрома фона | Оттенок |
|---|---|---|
| Material #121212, Ant #141414, Radix gray | 0 | — |
| Radix slate dark 1 | 0.004 | синеватый |
| Primer dark neutral.1 | 0.014 | синеватый (#0D1117) |
| Tailwind gray-950 | 0.027 | синеватый (H 262°) |
| Tailwind stone-950 | 0.004 | тёплый (H 49°) |

Тонированный тёмный фон встречается чаще, чем тонированный светлый: на тёмном хрома заметна слабее, поэтому её
можно взять выше. Практический диапазон — **C 0.004–0.03**, то есть примерно вдвое больше, чем в светлой теме.

---

## 3. Почему тёмная тема не инверсия

### 3.1. Прямое доказательство на Radix

Посчитано мной, шкала blue, светлая и тёмная версии из исходников [S3]:

| Шаг | Роль | Light | L | Dark | L | ΔL |
|---|---|---|---|---|---|---|
| 1 | фон приложения | #fbfdff | 99.3 % | #0d1520 | 19.4 % | −79.9 |
| 2 | мягкий фон | #f4faff | 98.2 % | #111927 | 21.3 % | −76.9 |
| 3 | фон компонента | #e6f4fe | 96.0 % | #0d2847 | 27.4 % | −68.5 |
| 4 | hover | #d5efff | 93.8 % | #003362 | 32.0 % | −61.8 |
| 5 | active/selected | #c2e5ff | 90.5 % | #004074 | 36.7 % | −53.8 |
| 6 | слабая граница | #acd8fc | 86.3 % | #104d87 | 41.6 % | −44.7 |
| 7 | граница компонента | #8ec8f6 | 81.0 % | #205d9e | 47.4 % | −33.6 |
| 8 | сильная граница | #5eb1ef | 73.4 % | #2870bd | 54.1 % | −19.3 |
| **9** | **сплошной фон** | **#0090ff** | **64.9 %** | **#0090ff** | **64.9 %** | **0.0** |
| 10 | hover сплошного | #0588f0 | 62.2 % | #3b9eff | 68.8 % | **+6.6** |
| 11 | низкоконтрастный текст | #0d74ce | 55.6 % | #70b8ff | 76.4 % | +20.8 |
| 12 | высококонтрастный текст | #113264 | 32.4 % | #c2e6ff | 90.7 % | +58.3 |

Читается так:
- **Шаг 9 идентичен в обеих темах** — и это верно для всех акцентных шкал Radix: red9 #e5484d, green9 #30a46c,
  amber9 #ffc53d, yellow9 #ffe629, orange9 #f76b15. Цвет бренда не «плавает» при смене темы.
- **Инверсии нет**: при инверсии dark1 должен был бы равняться light12 (L 32.4 %), а он L 19.4 %.
- **Направление шага 10 меняется на противоположное**: в светлой теме hover темнее, в тёмной — светлее.
- **Величина ΔL монотонно растёт** от −80 к +58, то есть трансформация нелинейная и разная для каждого шага.

### 3.2. Что говорят системы

- Radix: тёмные шкалы — отдельные наборы значений в `src/dark.ts`, а не производные от светлых [S3].
- Ant Design: тёмная тема строится подмешиванием СВЕТЛЫХ шагов к почти-чёрному фону по таблице
  `darkColorMap = [(7,15%), (6,25%), (5,30%), (5,45%), (5,65%), (5,85%), (4,90%), (3,95%), (2,97%), (1,98%)]`
  на фоне #141414 [S21]. То есть тёмный шаг 1 = светлый шаг 7, подмешанный на 15 % к фону.
- Material: мапится на другие тоны, а не на зеркальные. Светлая: primary = тон 40, surface = neutral98. Тёмная:
  primary = тон 80, surface = neutral6 [S10]. Зеркало дало бы 60 и 2.
- Primer: отдельные значения `base/color/dark/dark.json5`, и хроматические шкалы там тоже другие: light blue.5
  #0969da, dark blue.5 #1f6feb [S8].
- Polaris: четыре отдельные темы (White, Gray 10, Gray 90, Gray 100), каждая со своими значениями.

---

## 4. Слои и глубина

### 4.1. Оверлеи высоты (Material)

Из кодлаба Google «Design a dark theme with Material and Figma» [S29], дословно:
- «In Material dark themes, the bottom-most layer of the interface is typically a dark gray with the hex value
  **#121212**.»
- карточки писем: белый **#FFFFFF при 2 %** поверх #121212;
- нижняя аппбар-панель: белый **#FFFFFF при 12 %**;
- «The more elevated the surface is, the stronger and brighter the overlay becomes. This is a way of communicating
  elevation and hierarchy when the background is too dark to reliably portray dark shadows.»

Диапазон по документации M2: **0 % при 0 dp … 16 % при 24 dp** (подтверждено поиском по документации; сама
страница m2.material.io — SPA и текст не отдаёт).

Посчитано мной, белый оверлей на #121212:

| Альфа | Итоговый цвет | OKLCH L | WCAG к фону |
|---|---|---|---|
| 0 % | #121212 | 18.2 % | 1.00:1 |
| 2 % | #171717 | 20.5 % | 1.04:1 |
| 3 % | #191919 | 21.3 % | 1.07:1 |
| 4 % | #1b1b1b | 22.2 % | 1.09:1 |
| 5 % | #1e1e1e | 23.5 % | 1.12:1 |
| 6 % | #202020 | 24.4 % | 1.15:1 |
| 8 % | #252525 | 26.4 % | 1.22:1 |
| 9 % | #272727 | 27.3 % | 1.25:1 |
| 11 % | #2c2c2c | 29.3 % | 1.34:1 |
| 12 % | #2e2e2e | 30.1 % | 1.38:1 |
| 16 % | #383838 | 34.1 % | 1.60:1 |

Вариант с брендированной поверхностью: вместо белого — тёмный фирменный цвет при 48 %, карточки — светлый
брендовый при 4 % [S29]. Это даёт «более фирменную» тёмную тему ценой падения контраста.

### 4.2. Слои через отдельные токены (Material 3, Carbon, Polaris)

Material 3 отказался от альфа-оверлеев в пользу явных токенов поверхностей [S10]:

| Роль | Светлая (тон neutral) | Тёмная (тон neutral) | Шаг в тёмной |
|---|---|---|---|
| `surface-container-lowest` | 100 | 4 | — |
| `surface` / `background` | 98 | 6 | +2 |
| `surface-container-low` | 96 | 10 | +4 |
| `surface-container` | 94 | 12 | +2 |
| `surface-container-high` | 92 | 17 | +5 |
| `surface-container-highest` | 90 | 22 | +5 |
| `surface-bright` | 98 | 24 | — |
| `surface-dim` | 87 | 6 | — |

**Шаг между уровнями в тёмной теме 2–5 тонов против 2 в светлой.** Причина: в тёмной зоне разница светлот
различается хуже, поэтому шаг приходится увеличивать.

Radix даёт тот же эффект шагами 1–5: dark slate 1 (L 17.9 %) → 2 (21.3 %) → 3 (25.2 %) → 4 (28.3 %) → 5 (31.2 %),
шаг 3–4 п.п. светлоты.

Practical: **минимум три уровня** — фон приложения, поверхность (карточка/панель), всплывающее (меню/поповер),
и каждый на 3–5 п.п. светлее предыдущего.

### 4.3. Границы через альфу

shadcn `.dark` [S15]:
```css
--border: oklch(1 0 0 / 10%);   /* белый 10 % */
--input:  oklch(1 0 0 / 15%);   /* белый 15 % */
```

Посчитано мной: над фоном #0a0a0a белый 10 % даёт **#232323** (1.26:1); над карточкой #171717 — **#2e2e2e**
(1.32:1); белый 15 % над фоном — **#2f2f2f** (1.48:1).

Плюс подхода: **один токен работает на всех поверхностях**, не нужно заводить `border-on-surface-1`,
`border-on-surface-2` и т. д.
Минус: контраст границы 1.26–1.48:1, то есть требование 3:1 для границ контролов НЕ выполняется. Для полей ввода и
чекбоксов в тёмной теме нужен отдельный, более сильный токен.

Polaris и Primer используют альфа-шкалы как отдельные наборы: Polaris `whiteAlpha` 1–16, Primer `*A` варианты,
Radix `*A` варианты для каждой шкалы (`slateA`, `blueA` и т. д.) [S3][S8][S24].

Практика Linear: дизайнер прототипировал тему «opacities of black and white», а потом это переводили в
переменные [S30]. То есть альфа — хороший инструмент проектирования, но в выпуск идут вычисленные значения.

### 4.4. Тени

> Разрешение противоречия [C5]: тени в тёмной теме не выключать — ни один из 8 измеренных продуктов этого не делает; те же токены с альфой в 1.5–2 раза выше и белым кольцом 0.10, глубину несут светлота и кольцо. См. `../CONTRADICTIONS.md`.

В тёмной теме тень на тёмном фоне почти не видна. Material прямо формулирует альтернативу: оверлеи «communicate
elevation and hierarchy when the background is too dark to reliably portray dark shadows» [S29].

Что работает вместо теней:
1. светлота поверхности (§4.1, §4.2) — основной инструмент;
2. граница через альфу белого (§4.3);
3. усиленная тень с бóльшим радиусом и прозрачностью (работает слабо, но добавляет «мягкость» краю);
4. тонкая светлая линия по верхнему краю (имитация подсветки сверху) — приём встречается у Linear и Vercel, в
   прочитанных мной источниках численно не задокументирован, помечаю как `[мнение]`.

Детали теней и elevation — тема агента C волны 1 (`04-shape-elevation/`).

Отдельно: **в forced-colors `box-shadow` принудительно `none`** [S34], поэтому интерфейс, где глубина держится
только на тенях, в высококонтрастном режиме разваливается в обеих темах.

---

## 5. Текст в тёмной теме

### 5.1. Не чистый белый

Material задаёт иерархию альфами белого [S29]:
- high emphasis — **87 %**
- medium emphasis — **60 %**
- disabled — **38 %**

Посчитано мной на фоне #121212:

| Альфа | Цвет | WCAG | APCA Lc |
|---|---|---|---|
| 38 % | #6c6c6c | 3.57:1 | −25.1 |
| 60 % | #a0a0a0 | 7.16:1 | −50.3 |
| 87 % | #e0e0e0 | 14.19:1 | −87.3 |
| 100 % | #ffffff | 18.73:1 | −107.3 |

Обрати внимание: **medium emphasis 60 % даёт APCA Lc −50.3, то есть ниже минимума Lc 60 для читаемого текста.**
Схема Material 2 по этому параметру устарела.

Реальные значения текста в тёмной теме у современных систем:

| Система | Основной текст | WCAG к фону | APCA | Вторичный | WCAG | APCA |
|---|---|---|---|---|---|---|
| Primer (фон #0D1117) | #F0F6FC | 17.39:1 | −100.9 | #9198A1 | 6.50:1 | **−45.8** |
| Radix slate dark (фон #111113) | #edeef0 (12) | 16.25:1 | −96.2 | #b0b4ba (11) | 9.06:1 | −61.0 |
| shadcn (фон #0a0a0a) | #fafafa | 18.97:1 | −104.4 | #a1a1a1 | 7.66:1 | −51.2 |

**Radix единственный, кто держит вторичный текст выше APCA Lc 60.** Primer и shadcn — нет.

Практическое правило: **вторичный текст в тёмной теме = OKLCH L 0.75–0.78** (Radix slate dark 11 = L 76.9 %),
а не L 0.68–0.71, как подсказывает WCAG.

### 5.2. Почему WCAG обманывает в тёмной теме

Подробно — `03-contrast.md` §4.1. Короткая версия: проверено мной, #777777 на чёрном даёт WCAG 4.69:1 (проходит
AA) при APCA Lc −30.6 (уровень «плейсхолдер»). Формулировка Myndex: «WCAG 2.x contrast cannot provide useful
guidance when designing dark mode» [S7].

### 5.3. Галация

«Excess contrast is nearly always due to excess brightness. When something is so contrasty that it seems to have
"halos", the first thing to try is to make the lightest element a little darker» [S19].

Практика: белый #ffffff на #121212 даёт APCA Lc −107.3, при рекомендуемом максимуме −90 для крупных шрифтов.
Radix берёт #edeef0 (Lc −96.2), Primer #F0F6FC (−100.9). **Для крупных заголовков в тёмной теме приглушай текст
до L 0.90–0.95, а не оставляй чистый белый.**

Про физиологию: «pupil… when it's dark, it dilates to allow more light to get in… Too small pupil sizes mean that
too little light enters the eye» и «as we get older, we become more susceptible to glare» [S25]. Галация — это
рассеяние света в оптических средах глаза, усиливается с возрастом.

---

## 6. Акценты и статусы

### 6.1. Акцент в тёмной теме светлее

Material [S10]:

| Роль | Светлая | Тёмная |
|---|---|---|
| `primary` | тон 40 | тон 80 |
| `on-primary` | тон 100 (белый) | тон 20 (тёмный) |
| `primary-container` | тон 90 | тон 30 |
| `on-primary-container` | тон 10 | тон 90 |
| `inverse-primary` | тон 80 | тон 40 |

То есть **основная кнопка в тёмной теме светлая с тёмным текстом**, а не тёмная с белым.

shadcn делает то же радикальнее: `.dark { --primary: oklch(0.922 0 0); --primary-foreground: oklch(0.205 0 0) }` —
основная кнопка в тёмной теме почти белая [S15].

Radix решает иначе: шаг 9 не меняется вовсе (blue9 #0090ff в обеих темах), меняются только шаги вокруг него.
Оба подхода рабочие; выбор зависит от того, насколько важно сохранить фирменный цвет.

### 6.2. Направление hover меняется

Radix, шаг 10 (hover для сплошного фона) [S3]:
- светлая тема: blue9 #0090ff → blue10 #0588f0, светлота падает с 64.9 % до 62.2 % (**темнее**);
- тёмная тема: blue9 #0090ff → blue10 #3b9eff, светлота растёт с 64.9 % до 68.8 % (**светлее**).

Fluent 2 формулирует то же словами: «Generally, a component will get darker as someone interacts with it, from
the lightest rest state, to a darker hover, all the way to the darkest selected state», и отдельно: «Windows
interaction states currently treat color in reverse; controls will get lighter as a person interacts with them»
[S: Fluent 2 Color].

Правило: **направление изменения при hover определяется полярностью темы, а не абсолютной светлотой цвета.**
В тёмной теме hover светлее, в светлой темнее. Подробнее — `05-states-and-interaction.md`, §2.

### 6.3. Статусы

Значения из исходников Radix [S3] (шаг 11, низкоконтрастный текст):

| Статус | Светлая | Тёмная | Что изменилось |
|---|---|---|---|
| red | #ce2c31 | #ff9592 | из насыщенного в пастельный |
| green | #218358 | #3dd68c | светлее и ярче |
| amber | #ab6400 | #ffca16 | из коричневого в жёлтый |
| orange | #cc4e00 | #ffa057 | светлее |
| blue | #0d74ce | #70b8ff | значительно светлее |

Шаг 12 (высококонтрастный текст) в тёмной теме — почти пастель: red12 #ffd1d9, green12 #b1f1cb, amber12 #ffe7b3.

Fluent: «In dark mode, the colors of the shared palette shift in saturation and brightness to reduce eye strain
and accommodate visual accessibility needs» [S: Fluent 2 Color].

Отдельный запрет: **красный на чёрном** — для протанопии контраст «greatly diminished», пара запрещена для текста
и смысловой графики [S19]. Поэтому статус «ошибка» в тёмной теме — не #ff0000 и не насыщенный красный, а
светло-розовый (Radix red dark 11 = #ff9592, Primer dark red.3 = #ff7b72).

Проверено мной: #ff7b72 на #0D1117 даёт WCAG 7.51:1 и APCA Lc −52.6.

---

## 7. Изображения и иллюстрации

Carbon даёт наиболее подробные правила [S: Carbon color usage]:
- «Whenever possible, switch out assets entirely between modes to reflect the theme either by using tokens in the
  svg code or manually swapping out a png.»
- «When not possible, a low effort way to design images for modes is to use transparent backgrounds» и менять
  цвет контейнера под тему.
- Антипаттерн: «Don't use images with colored backgrounds when switching between modes because they will appear
  broken and in high contrast in the opposite mode.»

Про фотографии: приглушение яркости фильтром (`filter: brightness(0.8)`) — встречающаяся практика, но в
прочитанных мной источниках численно не задокументирована. `[мнение]`.

`light-dark()` принимает и изображения: `light-dark(url("light-icon.png"), url("dark-icon.png"))` и градиенты
[S20] — это готовый механизм подмены ассетов без JS.

---

## 8. Алгоритм: тёмная тема из светлой

### 8.1. Если шкала ролевая (Radix, Geist)

Самый простой случай: роли шагов не меняются, меняются значения.

```
FUNCTION derive_dark_scale(light_scale, hue, chroma_base):
    # light_scale: шаги 1..12 с ролями Radix
    # Опорные светлоты тёмной шкалы (среднее по Radix dark, OKLCH L)
    L_DARK = {1:0.179, 2:0.213, 3:0.252, 4:0.283, 5:0.312, 6:0.347, 7:0.399,
              8:0.489, 9:null, 10:null, 11:0.769, 12:0.949}
    # для хроматических шкал шаги 9..12 считаются от шага 9
    dark = {}

    # 1. Шаг 9 не меняется: сплошной цвет бренда сохраняется
    dark[9] = light_scale[9]
    (L9, C9, H9) = hex_to_oklch(dark[9])

    # 2. Шаги 1..8: лестница вверх от фона, хрома растёт к 8
    FOR k IN 1..8:
        L = L_DARK[k]
        C = C9 * (0.15 + 0.85 * (k - 1) / 7) * 0.9     # от 15 % до 100 % хромы шага 9
        C = min(C, max_chroma(L, H9))
        dark[k] = oklch_to_hex(L, C, H9)

    # 3. Шаг 10: hover, в тёмной теме СВЕТЛЕЕ шага 9
    dark[10] = oklch_to_hex(min(L9 + 0.04, 0.95), C9, H9)

    # 4. Шаги 11, 12: текст, светлее и менее насыщенные
    dark[11] = oklch_to_hex(0.769, min(C9 * 0.70, max_chroma(0.769, H9)), H9)
    dark[12] = oklch_to_hex(0.949, min(C9 * 0.35, max_chroma(0.949, H9)), H9)

    # 5. Коррекция контраста к шагу 1
    ENSURE apca(dark[11], dark[1]) <= -60      # низкоконтрастный текст
    ENSURE apca(dark[12], dark[1]) <= -90      # высококонтрастный текст
    ENSURE wcag(dark[11], dark[1]) >= 4.5
    RETURN dark
```

Проверка на Radix blue: мой алгоритм даст для шага 11 L 76.9 % — Radix даёт #70b8ff (L 76.4 %). Совпадает.

### 8.2. Если шкала по светлоте (Tailwind, Primer, Polaris)

Здесь роли перемапливаются, а значения берутся из той же шкалы.

```
FUNCTION map_roles_to_dark(scale):
    # scale: шаги 50..950, построенные для светлой темы
    RETURN {
        # ПОВЕРХНОСТИ: зеркалирование, но не полное
        bg_canvas          : scale[950],          # НЕ чёрный
        bg_surface         : lighten(scale[950], +0.035),   # +3.5 п.п. светлоты
        bg_surface_raised  : lighten(scale[950], +0.070),
        bg_subtle          : scale[900],

        # ГРАНИЦЫ: альфа белого вместо шагов шкалы
        border_subtle      : white / 8%,
        border_default     : white / 12%,
        border_strong      : scale[700],          # для полей ввода нужен сплошной, 3:1

        # ТЕКСТ: НЕ зеркало, а отдельные светлоты
        text_primary       : scale[50],           # L ≈ 0.95..0.97, не чистый белый
        text_secondary     : scale[300],          # L ≈ 0.77..0.84, проверить APCA Lc 60
        text_tertiary      : scale[400],
        text_disabled      : scale[600],

        # АКЦЕНТ: светлее, чем в светлой теме
        accent_solid       : accent[500],         # в светлой было accent[600]
        accent_solid_hover : accent[400],         # СВЕТЛЕЕ, а не темнее
        accent_text        : accent[300],         # в светлой было accent[700]
        accent_bg          : accent[950],         # тёмная плашка
        accent_border      : accent[800],
        text_on_accent     : scale[950],          # ТЁМНЫЙ текст на светлом акценте
    }
```

Полный алгоритм с проверками:

```
FUNCTION derive_dark_theme(light_theme, neutral_scale, accent_scale):
    dark = {}

    # ШАГ 1. Фон. Не чёрный, целевая светлота OKLCH L 0.13..0.19
    L_bg = 0.16
    dark.bg_canvas = oklch(L_bg, chroma_of(neutral_scale) * 1.5, hue_of(neutral_scale))
    #   хрому можно взять вдвое больше, чем в светлой теме: на тёмном она заметна слабее

    # ШАГ 2. Поверхности. Шаг 3..5 п.п. светлоты, минимум три уровня
    dark.bg_surface        = shift_L(dark.bg_canvas, +0.035)
    dark.bg_surface_raised = shift_L(dark.bg_canvas, +0.070)
    dark.bg_subtle         = shift_L(dark.bg_canvas, +0.018)

    # ШАГ 3. Границы. Альфа белого; для контролов — сплошной цвет с контрастом 3:1
    dark.border_subtle  = rgba(255,255,255, 0.08)
    dark.border_default = rgba(255,255,255, 0.12)
    dark.border_strong  = find_L_for_wcag(target=3.0, bg=dark.bg_surface, hue=neutral_hue)

    # ШАГ 4. Текст. Проверяем по APCA, не по WCAG
    dark.text_primary   = find_L_for_apca(target=-90,  bg=dark.bg_canvas)   # ≈ L 0.93..0.96
    dark.text_secondary = find_L_for_apca(target=-62,  bg=dark.bg_canvas)   # ≈ L 0.76..0.78
    dark.text_tertiary  = find_L_for_apca(target=-45,  bg=dark.bg_canvas)   # ≈ L 0.64..0.68
    dark.text_disabled  = find_L_for_apca(target=-30,  bg=dark.bg_canvas)   # ≈ L 0.52..0.56

    # ШАГ 5. Акцент. Светлее на 0.06..0.12 L, хрома −10..−20 %
    (La, Ca, Ha) = hex_to_oklch(light_theme.accent_solid)
    dark.accent_solid = oklch(clamp(La + 0.09, 0, 0.85), Ca * 0.9, Ha)
    dark.accent_solid_hover = shift_L(dark.accent_solid, +0.05)      # СВЕТЛЕЕ
    dark.accent_text  = oklch(0.76, min(Ca * 0.75, max_chroma(0.76, Ha)), Ha)
    dark.accent_bg    = oklch(0.27, min(Ca * 0.55, max_chroma(0.27, Ha)), Ha)
    dark.text_on_accent = (L(dark.accent_solid) > 0.70) ? dark.bg_canvas : "#ffffff"

    # ШАГ 6. Статусы. Тот же приём, что для акцента, плюс десатурация
    FOR status IN [success, warning, danger, info]:
        (Ls, Cs, Hs) = hex_to_oklch(light_theme[status].text)
        dark[status].text   = oklch(0.76, min(Cs * 0.75, max_chroma(0.76, Hs)), Hs)
        dark[status].bg     = oklch(0.26, min(Cs * 0.50, max_chroma(0.26, Hs)), Hs)
        dark[status].border = oklch(0.42, min(Cs * 0.65, max_chroma(0.42, Hs)), Hs)
        dark[status].solid  = oklch(min(Ls + 0.08, 0.85), Cs * 0.9, Hs)

    # ШАГ 7. Скрим и оверлеи
    dark.scrim = rgba(0,0,0, 0.70)        # в тёмной теме скрим сильнее, чем в светлой (0.32..0.50)

    # ШАГ 8. Проверки
    ASSERT L(dark.bg_canvas) IN [0.13, 0.19]
    ASSERT L(dark.bg_surface) - L(dark.bg_canvas) >= 0.025
    ASSERT |apca(dark.text_secondary, dark.bg_canvas)| >= 60
    ASSERT wcag(dark.border_strong, dark.bg_surface) >= 3.0
    ASSERT нет пары «насыщенный красный на фоне темнее L 0.25»
    RETURN dark
```

Вспомогательная функция:
```
FUNCTION find_L_for_apca(target, bg, hue = 0, chroma = 0):
    lo, hi = 0.0, 1.0
    REPEAT 30 TIMES:
        mid = (lo + hi) / 2
        c = oklch(mid, min(chroma, max_chroma(mid, hue)), hue)
        IF |apca(c, bg)| < |target|: lo = mid       # для светлого текста на тёмном фоне
        ELSE: hi = mid
    RETURN oklch(hi, ...)
```

### 8.3. Что НЕ надо делать

- **`filter: invert(1)` на всю страницу.** Ломает фотографии, ломает бренд, ломает семантику (красный становится
  голубым).
- **Просто поменять местами шаги** (`gray-50` ↔ `gray-950`). Даёт чистый чёрный фон и чистый белый текст, оба
  за пределами рекомендуемых коридоров.
- **Оставить те же акцентные шаги.** Синий 600 на тёмном фоне читается как тёмно-синий на тёмном.
- **Оставить тени.** Невидимы; глубина пропадает.
- **Проверять контраст только по WCAG.** См. §5.2.

---

## 9. Режимы и переключение

### 9.1. `color-scheme` и `light-dark()`

```css
:root {
  color-scheme: light dark;   /* ОБЯЗАТЕЛЬНО, иначе light-dark() не работает */
}
body {
  color: light-dark(#333b3c, #efefec);
  background-color: light-dark(#efedea, #223a2c);
}
```

Факты из MDN [S20]:
- `light-dark()` — **Baseline с мая 2024**, работает во всех актуальных браузерах;
- работает только при `color-scheme` со значением, включающим обе схемы (обычно на `:root`);
- возвращает первое значение при схеме `light` **или когда предпочтение не задано**, второе — при `dark`;
- принимает не только цвета, но и `<image>`: `light-dark(url("light-icon.png"), url("dark-icon.png"))`, а также
  градиенты.

`color-scheme` также переключает нативные контролы (скроллбары, дефолтные чекбоксы, поля ввода) — без него
системные элементы останутся светлыми на тёмной странице.

### 9.2. Переключатель

Три состояния: `light`, `dark`, `system` (по умолчанию). Реализация через класс/атрибут на `html`:
```css
:root { color-scheme: light dark; }             /* system */
[data-theme="light"] { color-scheme: light; }
[data-theme="dark"]  { color-scheme: dark; }
```
shadcn использует `@custom-variant dark (&:is(.dark *))` и переопределяет те же токены внутри `.dark` [S15].

Carbon: «you'll need to add a control somewhere in your product for the user to make a theme mode selection. This
is commonly done in a display setting, user profile, or account area» [S: Carbon color usage]. В IBM Cloud это
ссылка «Change theme» в панели профиля.

Смешение тем на одной странице (Carbon «inline theming»): шелл и боковые панели в тёмной теме при светлой
основной. «Only use inline theming for major shifts in color, like high contrast moments.» И отдельно: «smaller
components built with an inverse token (like tooltip) should remain high contrast when switching modes».

### 9.3. forced-colors (Windows High Contrast)

Кратко, детали — тема агента F волны 2 (`09-design-tokens/`).

Факты из MDN [S34]:
- медиафича `@media (forced-colors: active)`;
- принудительно подменяются: `color`, `background-color`, `text-decoration-color`, `text-emphasis-color`,
  `border-color`, `outline-color`, `column-rule-color`, `-webkit-tap-highlight-color`, SVG `fill` и `stroke`;
- **`box-shadow` принудительно `none`**, **`text-shadow` принудительно `none`**, `background-image` принудительно
  `none` для всех значений кроме `url()`, `color-scheme` принудительно `light dark`, `scrollbar-color`
  принудительно `auto`;
- браузер выбирает системный цвет по КОНТЕКСТУ элемента: `color` у кнопки → `ButtonText`, у обычного текста →
  `CanvasText`. «User agents choose system colors based on native element semantics, not on added ARIA roles» —
  `role="button"` на `div` цвет кнопки не даст;
- браузер рисует «backplates» под текстом, чтобы сохранить контраст поверх изображений;
- `forced-color-adjust: none` отключает подмену для элемента И отключает backplate;
- позиция MDN: «web authors should not be using the forced-colors media feature to create a separate design…
  its intended usage is to make small tweaks to improve usability or legibility»;
- браузер сам выставляет `prefers-color-scheme` по светлоте системного `Canvas`.

Что ломается на практике: **элементы, различавшиеся только фоном** (выбранная строка таблицы, активный пункт
меню, заполненный прогресс-бар), сливаются. Лечится дублированием состояния границей, иконкой или жирностью.

Смежная фича: `prefers-contrast: no-preference | more | less | custom`.

---

## Частые ошибки

1. **Чистый чёрный фон.** Выпадает из коридора L 13–19 %, даёт галацию и избыточный контраст.
2. **Чистый белый текст крупным кеглем.** APCA Lc −107.9 при максимуме −90. Приглушать до L 0.93–0.96.
3. **Инверсия светлой темы.** Расхождение с реальными системами доказано в §3.1.
4. **Проверка контраста только по WCAG.** См. §5.2 и `03-contrast.md` §4.1.
5. **Вторичный текст скопирован из светлой темы по номеру шага.** `gray-500` на светлом = 4.84:1, на тёмном —
   намного хуже по APCA.
6. **Только два уровня поверхностей.** Поповер поверх модалки сливается. Минимум три, шаг 3–5 п.п. светлоты.
7. **Границы 1 px сплошным светлым цветом.** Выглядят как «обводка», а не как граница. Альфа 8–15 % мягче.
8. **Тени оставлены как в светлой теме.** Невидимы, но продолжают раздувать CSS.
9. **Акцент того же шага, что в светлой теме.** Тёмно-синяя кнопка на тёмно-сером фоне.
10. **Hover идёт в ту же сторону, что в светлой теме.** В тёмной надо светлеть.
11. **Насыщенный красный статус на тёмном фоне.** Проблема для протанопии [S19].
12. **Иллюстрации со светлым фоном на тёмной теме.** «They will appear broken and in high contrast in the opposite
    mode» [S: Carbon].
13. **Нет `color-scheme: light dark`.** Скроллбары и нативные контролы остаются светлыми.
14. **Тёмная тема по умолчанию для массового продукта.** Исследования против [S25].

### Ошибки, типичные для нейросетей

15. **`dark:bg-gray-900 dark:text-white` на всё подряд.** Один уровень поверхности, чистый белый текст, границы
    не переопределены.
16. **Инверсия через `filter: invert(1)`** или через свап `50` ↔ `950` по всем токенам.
17. **Тёмная тема сгенерирована, но статусные цвета оставлены из светлой.** Тёмно-зелёный `success` на тёмном
    фоне нечитаем.
18. **`dark:border-gray-800` при `dark:bg-gray-900`.** Разница светлот 6 п.п., граница почти не видна — и при этом
    выглядит сплошной, а не мягкой.
19. **Переключатель темы без состояния «системная».** Пользователь теряет синхронизацию с ОС.
20. **Два набора токенов, в которых тёмный набор неполный:** часть компонентов наследует светлые значения и
    вспыхивает белым при переключении.

---

## Чек-лист

- [ ] Фон тёмной темы в коридоре OKLCH L 13–19 %, не чистый чёрный?
- [ ] Поверхностей минимум три, шаг между ними 3–5 п.п. светлоты?
- [ ] Основной текст — не чистый белый (L 0.93–0.96), APCA |Lc| ≥ 90?
- [ ] Вторичный текст даёт APCA |Lc| ≥ 60 (примерно OKLCH L 0.75–0.78)?
- [ ] Отключённый текст в коридоре APCA |Lc| 30–45?
- [ ] Границы полей ввода и чекбоксов дают ≥ 3:1 к своей поверхности (альфы 10 % недостаточно)?
- [ ] Акцент в тёмной теме светлее, чем в светлой, на 0.06–0.12 L?
- [ ] Текст на акценте переключён: если L акцента > 0.70, текст тёмный?
- [ ] Hover в тёмной теме идёт вверх по светлоте, а не вниз?
- [ ] Статусы десатурированы и подняты по светлоте; насыщенного красного на тёмном нет?
- [ ] Тени заменены светлотой поверхностей и границами?
- [ ] Иллюстрации и иконки подменяются, а не просто ставятся на тёмный фон?
- [ ] Есть `color-scheme: light dark` на `:root`?
- [ ] Переключатель имеет три состояния (светлая, тёмная, системная), по умолчанию системная?
- [ ] Ни один компонент не наследует светлые значения при включённой тёмной теме?
- [ ] Проверено в `forced-colors: active`: состояния, различавшиеся только фоном, продублированы?
- [ ] Скрим модалки в тёмной теме усилен (≈ 0.6–0.75 против 0.32–0.50 в светлой)?

---

## Открытые вопросы и противоречия

1. **Material 2 против Material 3.** M2 задаёт альфа-оверлеи (0 % при 0 dp … 16 % при 24 dp) и текст альфами
   87/60/38 %; M3 отказался от этого в пользу явных токенов поверхностей. Значения M2 всё ещё широко цитируются,
   но устарели. `[спорно]`
2. **Medium emphasis 60 % белого** по Material 2 даёт APCA Lc −50.3, что ниже порога читаемости Lc 60. Старая
   схема не проходит современную проверку.
3. **Сохранять ли шаг 9 при смене темы.** Radix сохраняет (бренд-цвет одинаков), Material и shadcn меняют
   (акцент светлеет). Оба подхода в продакшене. `[спорно]`
4. **Страницы Material (m2.material.io, m3.material.io) — SPA и текст не отдают.** Значения #121212, 2 %, 12 %
   взяты из кодлаба Google [S29]; диапазон 0–16 % подтверждён только веб-поиском по документации, **не прочитан в
   первоисточнике целиком**.
5. **Apple HIG (Color, Dark Mode) не открылся** — страницы отдают пустой ответ. Рекомендации Apple по тёмной теме
   (системные динамические цвета, elevated/base levels) в этот файл не вошли. Пробел для волны 2.
6. **Аргумент «чистый чёрный вызывает smearing на OLED»** встречается повсеместно, но в прочитанных мной
   источниках не подтверждён. НЕ ПРОВЕРЕНО.
7. **Приглушение изображений фильтром** в тёмной теме (типичное `brightness(0.8)`) численно нигде не
   задокументировано. `[мнение]`
8. **Долгосрочный эффект светлой темы на миопию** [S25] основан на исследовании с n = 7. Слабая доказательность.

---

## Источники

- [S3] Radix Colors, исходники. https://github.com/radix-ui/colors (`src/light.ts`, `src/dark.ts`) — сравнение светлой и тёмной шкал по шагам; первичный источник.
- [S7] A. Somers (Myndex). APCA. https://git.apcacontrast.com/documentation/APCAeasyIntro.html — непригодность WCAG 2 для тёмной темы.
- [S8] GitHub Primer, исходники. https://github.com/primer/primitives (`src/tokens/base/color/dark/dark.json5`).
- [S10] Material Design 3, исходники токенов. https://github.com/material-components/material-web/blob/main/tokens/versions/v0_192/_md-sys-color.scss — маппинг ролей на тоны в обеих темах.
- [S15] shadcn/ui. Theming. https://ui.shadcn.com/docs/theming — полный `.dark`-блок, границы через альфу белого.
- [S19] A. Somers. The Realities And Myths Of Contrast And Color. Smashing Magazine, 09.2022. https://www.smashingmagazine.com/2022/09/realities-myths-contrast-color/ — галация, избыточный контраст, красный на чёрном.
- [S20] MDN. `light-dark()`. https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark — Baseline 2024, требование `color-scheme`, поддержка изображений.
- [S21] Ant Design, алгоритм. https://github.com/ant-design/ant-design-colors/blob/master/src/generate.ts — `darkColorMap`, фон #141414.
- [S23] Datawrapper. https://blog.datawrapper.de/beautifulcolors/ — «don't go full black, keep lightness 10–25 %».
- [S24] Shopify Polaris, исходники. https://github.com/Shopify/polaris — четыре темы, альфа-шкалы.
- [S25] R. Budiu (NN/g). Dark Mode vs. Light Mode: Which Is Better? 02.02.2020. https://www.nngroup.com/articles/dark-mode/ — обзор пяти исследований с выводами; обзор литературы, не собственный эксперимент.
- [S29] Google Codelabs. Design a dark theme with Material and Figma. https://codelabs.developers.google.com/codelabs/design-material-darktheme — #121212, оверлеи 2 % и 12 %, эмфазис 87/60/38 %.
- [S30] Linear. How we redesigned the Linear UI. https://linear.app/now/how-we-redesigned-the-linear-ui — прототипирование альфами, LCH и elevation.
- [S34] MDN. `forced-colors`. https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors — полный список подменяемых свойств, backplates, `forced-color-adjust`.
- Carbon Design System. Color: usage. https://carbondesignsystem.com/elements/color/usage/ — light/dark mode, inline theming, правила для иллюстраций.
- Microsoft Fluent 2. Color. https://fluent2.microsoft.design/color — сдвиг насыщенности и яркости shared-палитры в тёмном режиме, направление состояний.
