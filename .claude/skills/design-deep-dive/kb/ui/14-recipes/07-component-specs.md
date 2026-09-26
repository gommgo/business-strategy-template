# Рецепт 07. Визуальная спецификация компонента из токенов

Волна 3 · агент I · 22 сентября 2026 · собрано из `06-components-visual/`, проверено на примерах `examples/`

Вход: набор токенов (рецепты 01–05). Выход: CSS пяти базовых компонентов без единого литерала, с полной
матрицей состояний. Время: 30 минут на пять компонентов.

**Правило рецепта: компонент не задаёт собственных значений.** Всё берётся из семантического слоя; если
нужного токена нет, сначала заводится токен, потом пишется компонент. Компонентные токены заводят, когда
значение понадобилось **трём и более** компонентам.

---

## Шаг 0. Общие правила для всех компонентов

1. **Высота выводится формулой**, а не подбирается: `height = line-height + 2 × padding-block + 2 × border`.
   Практичнее задать `height: var(--size-control-md)` и `padding-block: 0`, иначе браузерный дефолт
   `padding: 1px` у `button` и `input` уводит значения из шкалы.
2. **Одна высота на горизонтальный ряд.**
3. **Обязательный минимум состояний**: rest, hover, active, focus-visible, disabled. Для списков, таблиц,
   вкладок и чипов добавляется selected (и selected + hover). Для форм — invalid и readonly.
4. **Дельты состояний**: ΔL hover 2–6 п.п. светлоты (альфа 4–5 %), active 5–9 п.п. (8 %), selected заметнее
   hover и обязательно продублирован вторым признаком. В тёмной теме направление разворачивается и коридор
   шире (до 12 п.п., потому что шаг между поверхностями больше).
5. **Фокус**: `outline: 2px` + `outline-offset: 2px`, только `:focus-visible`, контраст ≥ 3:1 к фону вокруг
   (при положительном offset) или к самому элементу (при отрицательном).
6. **Переходы 70–150 мс** на фон, границу и цвет; `:active` без перехода; фокус не анимируется.
7. **Не больше трёх одновременно меняющихся свойств**: фон + граница + текст.
8. **Disabled — отдельные токены, не `opacity` на контейнере.** `opacity: 0.5` поверх вторичного текста даёт
   ≈ 2.4:1 и Lc < 30.

---

## Кнопка

```css
.btn {
  display: inline-flex; align-items: center; justify-content: center;
  gap: var(--space-xs);                       /* 8, при мелком тексте 4–6 */
  height: var(--size-control-md);             /* 32 админка, 40 клиент */
  padding-block: 0;
  padding-inline: var(--space-inset-control-x); /* 12; практика: 8 компактно, 16 просторно */
  border: 1px solid transparent;
  border-radius: var(--corner-md);
  font: var(--type-button-weight) var(--type-button-size)/var(--type-button-leading) var(--type-button-family);
  transition: background-color var(--motion-hover), border-color var(--motion-hover), color var(--motion-hover);
}
.btn--primary   { background: var(--accent-solid); color: var(--fg-on-accent); }
.btn--primary:hover  { background: var(--accent-solid-hover); }
.btn--default   { background: var(--bg-surface); color: var(--fg-primary); border-color: var(--border-default); }
.btn--default:hover  { background: var(--bg-component); }
.btn--ghost     { background: transparent; color: var(--fg-primary); }
.btn--ghost:hover    { background: var(--bg-component); }
.btn--danger    { background: var(--danger-solid); color: var(--danger-on-solid); }
.btn[disabled]  { color: var(--fg-disabled); cursor: default; }
.btn--icon      { width: var(--size-control-md); padding-inline: 0; }
```

Числа и правила:

- **Иконка отстаёт от кнопки на шаг**: 16 px при тексте 14, 20 при 16. В практике 16 × 16 доминирует.
- **Горизонтальный padding уменьшается на 2–4 px**, когда внутри есть иконка.
- **Одна сплошная акцентная кнопка на экран или секцию.** Вторичная отличается способом заливки, а не
  оттенком.
- **Белый текст на зелёной и янтарной заливке шага 600 не проходит 4.5:1** (3.22 и 3.20). Нужен шаг 700 или
  тёмный текст.
- **Loading не меняет ширину**: текст прячется (`visibility: hidden`), спиннер 16 ставится в ту же ячейку.
- **`min-width` 72–96** в диалогах; в плотных тулбарах не применять.
- Русская надпись длиннее английской в 1.3–1.5 раза: проектировать по `min-width`, `max-width: 320`.
- Деструктивное действие: красный **текст** в списке, красная **заливка** в подтверждении.

## Поле ввода

```css
.input {
  height: var(--size-control-md);
  padding-block: 0;
  padding-inline: var(--space-inset-control-x);
  border: 1px solid var(--border-strong);     /* 4.76:1 к белому — проходит 1.4.11 */
  border-radius: var(--corner-md);
  background: var(--bg-surface);
  color: var(--fg-primary);
  font: var(--type-body-weight) var(--type-body-size)/var(--type-body-leading) var(--type-body-family);
  transition: border-color var(--motion-hover), background-color var(--motion-hover);
}
.input::placeholder { color: var(--fg-tertiary); }   /* не fg-disabled: плейсхолдер — текст */
.input:hover        { background: var(--bg-surface-hover); }
.input[aria-invalid="true"] { border-color: var(--danger-solid); }
.input[disabled]    { background: var(--bg-component); color: var(--fg-disabled); }
```

- **Граница поля — два режима.** «Как требует 1.4.11»: ≥ 3:1 (на белом `#959595`). «Как в практике»:
  1.2–1.5:1 с компенсацией заливкой и контрастным фокусом (медиана 24 продуктов 1.30). Выбрать один и
  записать в токен с комментарием, чтобы команда не «чинила» это случайно.
- **Лейбл снаружи поля, сверху**, 12–14/500, отступ 4–6. Плавающий лейбл не берём: исследование Google,
  на которое ссылается Material, сравнивало только два варианта с плавающим лейблом и не включало
  классическое поле.
- **Ошибка = граница + иконка + текст**, не только красная рамка. Место под текст ошибки резервируется,
  иначе форма прыгает при валидации (`min-height` у строки подсказки).
- **Кегль поля 16 px на ширинах < 768**, иначе iOS Safari зумит страницу при фокусе.
- **Readonly ≠ disabled**: текст остаётся вторичным, фон приглушён, граница прозрачная, значение копируется.
- Префикс и суффикс живут внутри границы поля; шеврон селекта 16 справа с `padding-right` 32–36; иконка
  поиска 16 слева с `padding-left` 32–36.
- Textarea: `min-height` 64–120, вертикальный ресайз, `field-sizing: content` для авторосте.

## Строка таблицы

```css
thead th {
  position: sticky; top: var(--size-panel-topbar); z-index: var(--z-raised);
  height: var(--size-row-table);
  padding: 0 var(--space-inset-table-cell-x);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  text-align: left; text-transform: none;
  font: var(--type-label-weight) var(--type-label-size)/var(--type-label-leading) var(--type-label-family);
  color: var(--fg-secondary);
}
tbody td { height: var(--size-row-table); padding: 0 var(--space-inset-table-cell-x);
           border-top: 1px solid var(--border-subtle);
           font: var(--type-body-compact-weight) var(--type-body-compact-size)/var(--type-body-compact-leading) var(--type-body-compact-family); }
tbody tr { transition: background-color var(--motion-hover); }
tbody tr:hover { background: var(--bg-surface-hover); }
tbody tr[aria-selected="true"] { background: var(--bg-selected); }
tbody tr[aria-selected="true"]:hover { outline: 1px solid var(--accent-border); outline-offset: -1px; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
```

- **Кегль не меняется с плотностью**, меняются отступы: Ant держит `cellFontSize = 14` во всех трёх
  размерах, меняя padding 16 → 12 → 8.
- **Шапка без uppercase.** Во всех девяти измеренных таблицах `text-transform: none`; капс-шапки в живой
  практике 2026 года не встретились.
- **Только горизонтальные разделители 1 px.** Вертикальные — в плотных финансовых таблицах и матрицах.
- **Зебра = фон на 1.5–3 п.п. светлоты темнее базового** (`#fafafa` ΔL 1.5, `#f6f8fa` 2.2). Больше 4 п.п.
  читается как выделение. В эксперименте на 2276 сессиях зебра дала значимо более точный ответ в 3 вопросах
  из 8 и ни в одном не ухудшила.
- **Верхняя невидимая граница строки** (`border-block-start: 1px solid $layer` у Carbon) не даёт раскладке
  прыгать при подсветке.
- **Selected + hover — отдельное состояние.** В эталонной схеме под него нет роли фона, поэтому второй
  признак даётся кольцом. Это открытый вопрос схемы, а не обход.
- Колонка чекбоксов 32–48, колонка действий справа шириной в высоту строки; кнопки действий видимы на тач.
- Пустая ячейка — «—» цветом `text-muted`.
- На 1440 × 900 при строке 36 помещается ≈ 19 строк, при 48 — ≈ 13.

## Карточка

```css
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--corner-lg);
  padding: var(--space-inset-card);            /* 16 админка, 24 клиент */
}
```

- **Карточка в плотной админке — граница 1 px без тени.** У Primer 0 из 62 карточек с тенью, у Mantine
  0 из 18, у Grafana 0 из 10.
- **Карточка в клиентском сервисе** — padding 24, радиус 10–14, `0 1px 2px rgb(0 0 0 / .05)` + граница.
- Заголовок карточки 14–16/600, отступ до содержимого 12–16.
- **Внутренний радиус = внешний − padding.** Карточка 8 с padding 16 даёт внутреннему элементу 0…4.
- **Секции внутри карточки разделяются отступом, потом линией; две линии подряд запрещены.**
- Глубина вложенности поверхностей ≤ 2: «карточка в карточке» — маркер генерации.

## Модалка

```css
.scrim { position: fixed; inset: 0; z-index: var(--z-modal); background: var(--overlay-scrim); }
.modal {
  width: var(--size-modal-form);               /* 400 / 560 / 880 */
  max-width: calc(100vw - var(--space-xl));
  max-height: 85vh; overflow: auto;
  background: var(--bg-surface-raised);
  border-radius: var(--corner-lg);
  box-shadow: var(--elevation-overlay);
}
.modal-head, .modal-body, .modal-foot { padding: var(--space-inset-card); }
.modal-head { border-bottom: 1px solid var(--border-subtle); }
.modal-foot { border-top: 1px solid var(--border-subtle); display: flex; justify-content: flex-end; gap: var(--space-xs); }
```

- Ширины: **400** подтверждение, **520–640** форма, **800–960** крупная. Padding 24, заголовок 18–20/600,
  крестик 32 (иконка 16) в 16 px от угла.
- `max-height: min(600px, 85vh)`, шапка и футер липкие, скроллится только тело.
- Скрим 32–50 % чёрного в светлой теме, 60–75 % в тёмной; чёрный, не цветной.
- Главное действие справа в вебе; на мобильном стопка в обратном порядке.
- На ширине < 640 модалка становится листом.
- **Третичный текст на приподнятой поверхности не проходит 4.5:1 в тёмной теме** (`#90a1b9` на `#314158` =
  3.94). Внутри модалки подсказки берут вторичный цвет.

> Разрешение противоречия [C13] (22.09.2026): в эталонной схеме третичный текст тёмной темы переведён на neutral-350 `#aebccf` — 5.37:1 на `bg.surface-raised`; подсказки в модалке могут снова брать `fg.tertiary`. См. `../CONTRADICTIONS.md`.

---

## Проверки

Прогон `ui_audit.py` закрывает большую часть матрицы состояний:

| Что | Проверка |
|---|---|
| Одна высота на ряд, высоты из ряда | B1, B2, B3 |
| Иконочная кнопка квадратная | B4 |
| Иконки из ряда, один набор | B5, B6 |
| Вложенный радиус | C3 |
| Граница 1 px | C4 |
| Тень только там, где нужно; вложенность теней ≤ 1 | D5, D6 |
| Контраст текста и границы во всех состояниях и темах | I1, I2, `--scheme both` |
| Disabled в коридоре APCA Lc 30–60 | I1c |
| У каждого интерактивного элемента есть hover, ΔL в коридоре | `--hover`, S1, S2 |
| Видимый индикатор фокуса на каждой остановке Tab, ≥ 2 px, не обрезан, ≥ 3:1 | `--tab 24`, G2–G5 |
| `tabular-nums` в числовых ячейках | H12 |
| Длительности из шкалы, нет `transition: all` | K1, K2 |

Псевдокод полной матрицы состояний — `../06-components-visual/07-states-matrix.md` §12 (11 утверждений).

---

## Типичные ошибки

1. **`px-4 py-2 rounded-lg` у всех кнопок подряд**: получается 40 px и радиус 8 даже в плотном тулбаре.
2. **`h-10 px-4 rounded-lg` у всех полей** независимо от плотности продукта.
3. **Лейбл 16/400 при поле 14** — подпись крупнее содержимого.
4. **`focus:ring-2 ring-blue-500` без `focus-visible`** — кольцо появляется при клике мышью.
5. **`hover:opacity-80`** вместо смены фона: элемент просвечивает, ломаются тень и граница.
6. **`disabled:opacity-50 disabled:cursor-not-allowed`** без проверки итогового контраста.
7. **`px-6 py-4` в каждой ячейке** (дефолт примеров Tailwind): строка 56 px в плотной админке.
8. **`uppercase tracking-wider text-xs text-gray-500` у шапки таблицы** — приём из шаблонов 2019 года.
9. **Зебра `odd:bg-gray-50` вместе с `hover:bg-gray-50`** — hover невидим на каждой второй строке.
10. **`divide-y` плюс `border` у каждой ячейки** — двойные линии.
11. **`p-6 rounded-2xl shadow-lg` у каждой карточки** — маркетинговая подача внутри рабочего интерфейса.
12. **Чекбокс нарисован `div` без размеров** и растягивается флексом в прямоугольник.
13. **Переключатель 48 × 28 рядом с полем 32** — разная визуальная масса.
14. **Модалка с `top-1/2 left-1/2 -translate-1/2` без `max-height`**: на ноутбуке 900 px не помещается.
15. **`z-50` у всех слоёв подряд** — порядок определяется случайным порядком в DOM.
16. **Оверлей без портала** внутри контейнера с `overflow: hidden`.
17. **Состояния заданы только у кнопки**, а у строк, пунктов меню и чипов — нет.
18. **`transition: all`** — анимируются все свойства, включая размеры и тени.

---

## Ссылки на базу

- Кнопки: `../06-components-visual/01-buttons-and-actions.md`
- Поля и формы: `../06-components-visual/02-forms-and-inputs.md`
- Таблицы и списки: `../06-components-visual/03-tables-and-lists.md`
- Навигация и поверхности: `../06-components-visual/04-navigation-and-surfaces.md`
- Обратная связь и оверлеи: `../06-components-visual/05-feedback-and-overlays.md`
- Данные и мелочь: `../06-components-visual/06-data-display-and-misc.md`
- Матрица состояний и проверки: `../06-components-visual/07-states-matrix.md`
- Сводная таблица по 12 системам: `../06-components-visual/08-values-by-system-table.md`
- Рабочие примеры на токенах: `examples/` (семь экранов, прогнаны `ui_audit.py`)
