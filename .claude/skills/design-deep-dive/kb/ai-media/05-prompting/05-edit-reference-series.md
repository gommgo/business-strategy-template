# Правки, референсы с ролями, серии, продукт с текстом: формулы промта

Волна 2 · агенты D2 и D2b · 2026-09-23 · опора: 13 дайджестов роликов (`99-raw/notes/wave2/D2-helper-digests.md`, 362 цитаты
сверены с транскриптами), гайды вендоров из `01-vendor-prompt-guides.md` §2.3, §4.5–4.6, §5.6, §7.1–7.2, §12.3–§12.7, гайд
Recraft V4 (кэш `99-raw/cache/recraft-D/`), соседи: H2 (`08-image-post-processing/02` — процедура проверки правки), F2
(`06-art-direction-consistency/02`, `04` — метод серии и антислоп) · опыты: компилятор v2.1 (`99-raw/experiments/D2/01-compiler-v2`,
тесты 98/98; исправления по прогону F/07) · снимок каталога polza 2026-09-23 17:45 · промты — `[не проверено]` генерацией до
фазы 5 (D2-06; серии — F-01…F-04, продукт — E)

Граница: здесь — **форма промта** (формулы, фразы, поля спецификации). Проверка правки (композит, пиксельная разница, пороги) —
H2 (`../08-image-post-processing/02-upscale-outpaint-edit.md` §2); метод серии, число референсов, пороги дрейфа — F2
(`../06-art-direction-consistency/02-series-and-consistency.md`); выбор модели для правки — E и N (`../13-routing-matrix/`).

## Выжимка для агента

1. **Правка = операция + что + где + на что (целевым значением) + положение и размер + что видно после + что не трогать +
   «больше ничего»**: формула Jamey «replace the computer… keep the position and the size… exactly the same… only the left side
   and the keyboard is visible… don't change anything else» [V:2RD3FP5iWJY 36:34–37:34]. → §1.1 `[практика]` `[документация]`
2. **≤ 5 изменений за вызов** — правило базы: «If you had asked it to change six different things, the model would sometimes
   not do a great job» [V:H6ZXujE1qBA 15:16]; «five» у Google — пример, не порог [16:16]; составную правку выполняют частично
   («it would do maybe one of those things», Gamma, ≈ 550 отзывов) [V:hzPKb8bDvdY 13:19]. → §1.2 `[мнение вендора]` (тест D2-06)
   [поправка фазы 5, 25.09.2026: у NB2 1K не подтвердилось — 10 правок одним вызовом выполнены все (10 из 10, геометрия сохранена),
   цепочка 5 + 5 — тоже 10 из 10, но вдвое дороже (9,6 против 4,8 ₽) и копит дрейф тона (шаг 1: ΔE00 4,69); 1 образец; GPT Image 2.5 и
   Qwen — без данных → `99-raw/phase5/runs/3-prompt-form/D2-06-check/D2-06_sheet.jpg`]
3. **Nano Banana на составной правке меняет ракурс и крупность** — «единственный способ… упростить промт» [V:7-YIYlIhksM
   07:21–08:22] → где важны ракурс и лицо — одно изменение на вызов. → §1.2 `[практика]`
4. **Целевые значения вместо сравнительных**: «darker shade of green» дало «Almost look like nighttime» [V:8kM5aDD5gLI
   22:31–25:38] → «#1F5E3B», «2700 K», «reduce brightness of the wall by 20 %, keep hue»; компилятор предупреждает о darker /
   lighter / more без `value`. → §1.3 `[практика]`
5. **Закрывающая фраза вендора + суффикс**: Google «Keep everything else in the image exactly the same, preserving the original
   style, lighting, and composition»; OpenAI «Keep all other aspects of the image unchanged»; BFL «Change nothing else»; плюс
   «Maintain the original composition and subject.» (код фотобудки OpenAI [V:8kM5aDD5gLI 24:36]). → §1.1 `[документация]`
6. **«Оберег» — список неизменного** (поза, видимое лицо, ракурс, свет): «keep his face visible» [V:H6ZXujE1qBA 01:00], «keep
   this, change that» [V:AxV8TR3BdqI 43:01] → поле `edit.keep`. → §1.1 `[практика]`
7. **Смешанная правка — у каждого изменения свой глагол** (`edit.changes[].op`): «add a small potted fern on the window sill», а
   не «change the window sill to a small potted fern» (так модель заменит подоконник). → §1.4 `[проверено: компилятор]`
8. **Варианты — от мастера; накопление — с маской от мастера + композит**: каждая правка перерисовывает весь кадр, детали
   деградируют [V:SLnGJ9iezYo 02:02]; без маски — цепочка ≤ 2–3 шагов с `edit_check.py check --match-color` после каждого (дрейф
   ≤ 2, утечка ≤ 0,02 — H). → §1.5 `[спорно]` `[проверено]`
9. **Маска — подсказка, и её полярность в polza противоположна**: `qwen/image-2.1` — белое = менять; `openai/gpt-5-image` —
   чёрное = менять (выключение 23.10.2026); OpenAI и RouterAI — прозрачное; компилятор сам приводит файл к полярности модели. →
   §2.1 `[документация]`
10. **Безмасочное удаление — по одному объекту за вызов** («remove the text below the laptop», «remove the top bar»
    [V:8kM5aDD5gLI 41:11–42:13]); маска удаления — объект + тень + ≈ 9 % стороны (H/03). → §2.2 `[практика]` `[проверено]`
11. **Текст правкой**: «Replace the text "X" with "Y", keeping the same font, size, color and position.»; перевод — «Translate the
    text… Do not change any other aspect of the image.» (OpenAI); кириллица после правки — только с OCR (K). → §2.3
    `[документация]`
12. **Референс — по номеру и роли, одной фразой на группу**: «Image 1 is the style reference: match its line weight and palette
    only; the subject and scene come from this prompt.»; три одной роли — «Images 1-3 are style references from one shoot…», а не
    три повтора (у FLUX промт раздулся до 319 слов при норме 80–300, F/07). → §3.1 `[документация]` `[проверено: компилятор]`
13. **Синтаксис ссылки — диалект семейства**: «Image N» (Google, OpenAI, Seedream, Qwen, Wan), «image N» (FLUX.2), `<Image_N>` /
    «@Image N» + «Define … as Subject 1» (Seedance 2.0), `<IMAGE_REF_N>` с нуля (Omni), `@Name` (Kling), «the provided image»
    (Grok). → §3.2 `[документация]`
14. **«Только идентичность»**: «use the reference image only to preserve the subject identity. Create a completely new shot…»
    [V:I9xdmNZxIfA 08:27]; референс всегда несёт и стиль, и композицию [V:2RD3FP5iWJY 18:16] → доминанту кадрировать, а не
    «no X» (F). → §3.3 `[практика]`
15. **1–3 референса одной съёмки на вызов, порядок входов фиксирован** в паспорте и одинаков во всех кадрах серии (F2 `06/02`
    §2.1–2.2). → §3.1 `[исследование]`
16. **Серия — дословный `series.block` первым**, меняется только слот сюжета; перефразированный блок компилятор отклоняет
    (`jobs`), метку «Series style» не дублирует. → §4.1 `[документация]` `[проверено: компилятор]`
17. **«Шаблон эффекта»** — постоянный блок эффекта + переменные объект и фон: «if you have the effect, it's already in the prompt.
    You can just change some details» [V:nBd9JJuAT1Y 45:01] → `series.effect_block`. → §4.2 `[практика]`
18. **«Против среднего» — утвердительно и по содержанию**: вне центра и асимметрия всегда; «gaze turned away» — только если в кадре
    люди; «natural imperfections» — только у фото; вместе с «по центру» — ошибка спецификации. Метрики и пороги — F2 (`06/04`
    §1). → §4.3 `[практика]` `[проверено: компилятор]`
19. **Замена запрета — без предметов** («no one in the frame», «clean, text-free surfaces»): замена с предметом («an empty
    desk…») попадает в каждый кадр серии (F/07; правило F2 `06/01` п. 10). → §4.3 `[проверено]`
20. **LLM-писатель промтов серии получает system prompt: роль → замки → запреты → shot list → формат вывода** («no additional
    commentary… no special characters») [V:AxV8TR3BdqI 28:44–45:04]; запреты дописываются по мере брака [30:46]. → §4.4
    `[практика]`
21. **Продукт с текстом — 7 блоков по порядку**: «Composition first, exact identity, typography control, true color, lighting
    harmony, optical clarity, negative constraints» [V:XLHTLJhzDyQ 03:05]; типографика — отдельным блоком: точные слова, место,
    выравнивание, «no misspellings, no extra letters, and no warped glyphs» (у FLUX.2 — позитивно). → §5 `[мнение вендора]`
22. **В видео продукта — референсы товара вместо стартового кадра, типографику не переописывать** [V:XLHTLJhzDyQ 05:05]. → §5.3
    `[мнение вендора]`
23. **Формат из мастера — кадрированием, только если безопасная зона помещается**, иначе аутпейнт или отдельная генерация: у E1
    зона 9:16 шириной 0,35 не влезает в кадр 9:16 из 16:9 (0,316) — считает `prompt_compile.py ratios`. → §6 `[проверено: тесты]`
24. **Recraft V4 — «from global to local»**: 8 шагов для сцены, 6 пунктов для вектора (без фактуры), 8 пунктов для текста (всё
    в кавычках); запреты — фразами в тексте, поля негатива у V4 нет. → §7 `[документация]`

## 1. Правка картинки

### 1.1 Формула и закрывающие фразы

Порядок фразы: **глагол операции → что → где → на что (значение) → положение и размер → что видно после → что не трогать →
больше ничего → суффикс**. Поля спецификации — `edit.{operation, changes[], keep[], visible_after, preserve_suffix}`.

| Операция (`edit.operation` или `changes[].op`) | Фраза компилятора |
|---|---|
| `replace`, `recolor` | Change only the {target}{where} to {to} ({value}). Keep its position and size exactly the same. |
| `add` | Add {to} ({value}) {where}. |
| `remove` | Remove the {target}{where}; in its place the frame shows {to}. |
| `text_replace` | Replace the text "{target}" with "{to}", keeping the same font, size, color and position. |
| `translate_text` | Translate the {target} into {to}, keeping everything else the same. |
| `background_swap` | Replace the background with {to}; keep the subject, its edges and the lighting direction unchanged. |
| `relight` | Relight the scene: {to} ({value}). |
| `restyle` | Preserve the original composition of {источник} but render it as {to}. |
| `extend` | Extend the scene of {источник} to fill a {ratio} frame; keep the original image content unchanged… (Qwen — шаблон §2.4) |

| Семейство | Вступление | Закрытие |
|---|---|---|
| Nano Banana | «Using the provided image, change only…» | «Keep everything else in the image exactly the same, preserving the original style, lighting, and composition.» [01 S2] |
| GPT Image | «Change only…» | «Keep all other aspects of the image unchanged.» [01 S12] |
| FLUX.2, Seedream, Qwen, прочие | «Change only…» | «Change nothing else.» (BFL) [01 S15] |
| все | — | суффикс «Maintain the original composition and subject.» (`preserve_suffix`, по умолчанию да) [V:8kM5aDD5gLI 24:36] |

```text
// qwen/image-2.1 · 1K, enhance_prompt false, mask_url (белое = менять) · фикстура v2-edit · polza 2026-09-23 · [не проверено]
Change only these elements: the armchair upholstery in the right third to deep green velvet (#1F5E3B); the throw pillow to a
darker pillow. Keep their positions and sizes exactly the same. After the change, the frame shows the same room with a deep
green armchair. Keep the camera angle, window light and floor shadows unchanged. Change nothing else. Maintain the original
composition and subject. No text.
```

«a darker pillow» — намеренная ошибка фикстуры: компилятор предупреждает «сравнительная формулировка — задай целевое значение
value» (§1.3).

### 1.2 Сколько изменений за вызов

- Google: «If you had asked it to change six different things, the model would sometimes not do a great job of that»;
  «break down the complex prompt… and do edits one by one over different steps»; «with hundred details, we cannot do that»
  [V:H6ZXujE1qBA 15:16–17:18] `[мнение вендора]`.
- Gamma: «move this person to the left and change the background and then put a hat on him and it would do maybe one of those
  things» [V:hzPKb8bDvdY 13:19] `[данные слабые]`; VideoSmile: три изменения сразу — Nano Banana «изменила и ракурс, и крупность
  плана», «единственный способ… упростить промт» [V:7-YIYlIhksM 07:21–08:22] `[практика]`.
- Правило базы: **≤ 5 изменений за вызов** (`defaults.edit.max_changes: 5`); > 5 — компилятор даёт ошибку и режет цепочкой
  (`chain`); для кадров с лицом и точным ракурсом у Nano Banana — одно изменение. Тест D2-06: `google/gemini-3.1-flash-image-preview`
  1K, 10 изменений одним вызовом против 5 + 5 (14,40 ₽); критерий — доля выполненных ≥ +20 п. п. у порций.
  [поправка фазы 5, 25.09.2026: D2-06 — порции выигрыша не дали (10 из 10 в обоих плечах), цепочка копит дрейф (ΔE00 4,69, LEAK 0,28)
  → для NB2 все правки — одним вызовом; порог 5 в `defaults.edit.max_changes` — не подтверждён (1 образец) →
  `99-raw/phase5/runs/3-prompt-form/README.md`]

### 1.3 Целевые значения

- Антипример: «Make the background more green. And actually, just make it a darker shade of green… keep everything else the
  same.» → «Almost look like nighttime» [V:8kM5aDD5gLI 22:31–25:38].
- Значение — числом или точным названием: цвет — hex + название + объект («deep green velvet (#1F5E3B)»; hex — не гарантия, 01
  §12.5), свет — источник и температура («warm tungsten lamp, about 2700 K»), яркость — доля («reduce the brightness of the wall
  by 20 %, keep the hue» — H `08/02` §2.6), размер — габарит («a 45 cm tall lamp»).
- Одно свойство за шаг, когда меняется свет или цвет всего кадра: «Change the lighting to soft cloud filtered golden hour
  lighting… exact same image but with the light change» [V:I9xdmNZxIfA 07:26].

### 1.4 Смешанная правка

```text
// google/gemini-3.1-flash-image-preview · 1K · бриф E10, задание D2-06 (10 изменений одним вызовом) · polza 2026-09-23 · [не проверено]
Using the provided image, make only these changes: change the armchair upholstery to deep green velvet (#1F5E3B); change the
white ceramic mug to a terracotta mug; change the stack of books on the floor to a woven basket with two rolled blankets;
change the sheer linen curtain to a pale blue linen curtain; change the side table to a small round black metal side table;
add a single framed botanical print on the bare wall above the armchair; change the wooden floor to light grey herringbone
parquet; add a round jute rug on the floor near the window; add a small potted fern on the window sill; add a folded mustard
wool throw over the armchair armrest. Keep the position and size of every changed element exactly the same. Keep the camera
angle, window light and room layout unchanged. Keep everything else in the image exactly the same, preserving the original
style, lighting, and composition. Maintain the original composition and subject. No text.
```

- Явный `op` хотя бы у одного изменения включает формулу «make only these changes: change…; add…; remove…» — одинаковую во
  всех порциях цепочки (плечи D2-06 равны по форме). До D2b бриф E10 писал добавления как замены («the window sill to a small
  potted fern on the window sill») — исправлено.

### 1.5 Порции: от мастера или цепочкой

| Случай | Как | Почему |
|---|---|---|
| варианты (другой фон, другой свет) | каждый от мастера (`edit.chain: from_source`) | сравнимы между собой, ошибки не копятся [V:7-YIYlIhksM 05:18] |
| > 5 изменений, есть маски | каждая порция от мастера + композит по маске (H `08/02` §2.3) | пиксельно точно; модель меняет в 50–1400 раз больше пикселей, чем нужно (PaintBench, H) |
| > 5 изменений, без маски | цепочка ≤ 2–3 шагов (`sequential`), после каждого — `edit_check.py check --match-color` | правка перерисовывает весь кадр, детали деградируют [V:SLnGJ9iezYo 02:02]; дрейф ΔE00 3,3 за один шаг (H/03) |
| правка не удалась («NO_EDIT», «LEAK») | не «править правку»: другая модель или композит | H `08/02` §2.2, §2.7 |
| сцена не та | перегенерировать, а не править: «I don't think this is necessarily an image that I want to tweak» | [V:8kM5aDD5gLI 41:11] |
| вариант серии | правкой промта или спецификации, а не картинки: «help me edit it… similar scene but with vegetables» | [V:nBd9JJuAT1Y 30:43–31:45] |

- **Противоречие**: Google — шаги на результате прошлого [V:H6ZXujE1qBA 16:16], H2 — «всегда от утверждённого мастера»
  (`08/02` §2.6). Позиция базы — таблица выше `[спорно]`; D2-06 меряет выполнение (цепочка 5 + 5 без маски), дрейф — процедура H.

## 2. Маски, удаление, текст, аутпейнт

### 2.1 Маска и полярность

- Маска — «guidance… may not follow its exact shape» (OpenAI, 01 §4.5); Google — «will not always 100% work»
  [V:H6ZXujE1qBA 14:13]. Таблица полярностей и тест одной правкой (`edit_check.py polarity`) — H `08/02` §2.5.
- Компилятор: `edit.mask {src, polarity: white=change | black=change | alpha=change}` → `derive_mask` приводит файл к полярности
  модели из `dialects.yaml` (`mask` модели) и кладёт копию в `jobs/masks/`; модель без маски (NB2, GPT Image 2.5, Seedream,
  FLUX.2 в polza) — ошибка «маска не поддерживается» → безмасочная правка словами.
- Qwen 2.1: маска — только с одним референсом и несовместима с `background: transparent` (01 §12.3).

### 2.2 Удаление

- Безмасочно — по одному объекту за вызов: «remove the text below the laptop» → «this is using maskless editing… it edited it»;
  следующий шаг — «remove the top bar» [V:8kM5aDD5gLI 41:11–42:13].
- Описывай, что видно на месте, а не только что убрать: образец H-06 — «Remove the red can and the yellow ball completely. Fill
  the area with the same seamless light-gray studio backdrop and the same soft floor shading…» (H `08/02` §2.6); компилятор
  (`remove`) пишет «Remove the {target}; in its place the frame shows {to}.»
- С маской — объект + тень + дилатация ≈ 8–10 % стороны, растушёвка ≈ 3 % (иначе «призрак» контура) — H/03.

### 2.3 Текст правкой

- Замена слов: «Replace the text "Summer sale" with "Winter sale", keeping the same font, size, color and position.»
  (`text_replace`); перевод: OpenAI Cookbook «Translate the text in the infographic to Spanish. Do not change any other aspect of
  the image.» (01 §4.5); Nano Banana Pro — «translate it to Spanish and make it my 9 by 16» [V:y-RQ48sfPgM 06:15] (правка и
  формат одним ходом — `[мнение вендора]`).
- Перевод на русский правкой — тест W3-5 (E); результат — OCR (K); по умолчанию русский текст — HTML-слоем (01 §12.7).

### 2.4 Инпейнт и аутпейнт

```text
// qwen/image-2.1 · шаблоны переписчика Qwen (prompt_utils_2512) · polza 2026-09-23 · [документация] · [не проверено в polza]
Perform inpainting on this image. The original caption is: <описание исходника>
Extend the image beyond its boundaries using outpainting. The original caption is: <описание исходника>
```

- Остальные семейства: `extend` → «Extend the scene of the provided image to fill a 21:9 frame; keep the original image content
  unchanged and continue <caption> naturally at the new edges.» + новый `aspect_ratio`; модель перерисовывает и исходную часть →
  `edit_check.py outpaint` и вставка исходника (H `08/02` §4.2–4.3).

## 3. Референсы с ролями

### 3.1 Роль — фразой по номеру входа

| Роль (`references[].role`) | Фраза (`dialects.yaml` → `defaults.reference_roles`) |
|---|---|
| `style` | {ref} is the style reference: match its {note}; the subject and scene come from this prompt. |
| `identity` | {ref} shows the subject; use it only to preserve the subject's identity ({note}) and create a completely new shot. |
| `subject` / `character` | {ref} shows the subject: keep it recognizable ({note}) / Keep the character from {ref} identical: face, proportions and clothing ({note}). |
| `product` | {ref} is the product: keep its shape, proportions, materials, label and colors exactly as in the image ({note}). |
| `composition` / `layout` | Follow the composition of {ref}: {note}. / Strictly follow the layout of {ref}: {note}. |
| `palette` / `material` / `effect` / `pose` / `background` | Take only the color palette from {ref} ({note}). / Apply the material and surface finish from {ref} ({note}). / Apply the visual effect shown in {ref} ({note}) to the new subject. / Take the pose from {ref} ({note}). / Use {ref} as the background environment ({note}). |
| `video_motion` | Reference the motion and camera movement in {ref} ({note}). |

- **Группа одной роли** (`defaults.reference_group`, подряд идущие референсы с одной ролью и одной заметкой): «Images 1-3 are style
  references from one shoot: match their light, colour grading, lens and grain only; do not copy their scenes or composition; the
  subject and scene come from this prompt.» — так же пишет F-01 A. Промт FLUX спецификации F/07: 1 870 → 1 642 символа, без
  предупреждения «длиннее 300 слов».
- `note` — что именно взять («line weight and palette only»); без `note` — умолчание роли («rendering style, line weight and
  palette» у `style`).
- Порядок `images[]` = порядок ссылок в промте (у правки исходник — Image 1, референсы — с Image 2); у Qwen «Порядок — тот, на
  который ссылается промпт» (каталог polza).

### 3.2 Синтаксис по семействам

| Семейство | Ссылка | Пример вендора |
|---|---|---|
| Nano Banana | «Image 1», роли словами | «Use Image 1 for the character's pose, Image 2 for the art style» [01 S2] |
| GPT Image | «Image 1: …» | «Image 1: product photo. Image 2: style reference.»; «Reference each input by index and description» [01 S12] |
| FLUX.2 | «image 1» | «subject from image 1, style from image 2, background from image 3» [01 S18] |
| Seedream | «Image 1» | «replace the character in Image 2 with the character from Image 1, and generate the result in the style of Image 3» [01 S22] |
| Qwen Image 2.1 | «Image 1» | порядок — как в промте |
| Seedance 2.0 | `<Image_1>` или «@Image 1» + определение субъекта | «Define the woman… in Image 1 as Subject 1»; после ссылки — имя: «@Image 1 (Lee) stands up» (`sd2-pe`) |
| Seedance 2.5 | «Image 1», «Video 1» | точный референс — «Strictly refer to…», не пересказывать |
| Omni | `<IMAGE_REF_0>` (с нуля), `<VIDEO_REF_0>` | объявление `[# References …]` (01 §3.9) |
| Kling 3.0 | `@Name` (элементы) | имена не подстроки друг друга (01 §8) |
| Grok Image | «the provided image(s)» | ролей нет в документации |

### 3.3 Что несёт референс

- Референс переносит и стиль, и композицию, и черты: «the structure of an image and the composition kind of is the style»,
  «it's also kind of like mimicking her like bone structure» [V:2RD3FP5iWJY 18:16–19:17] → роль словами не отключает перенос;
  лишнее — кадрировать или убрать референс, «no X» почти не помогает («Most of the time it won't» [20:17]) — F2 `06/02` §2.4.
- Точное совпадение продукта — фразой: «the product must match the provided references exactly, including proportions,
  silhouette, stitching, panel geometry, sole curvature, and overall construction»; слабые исходники — «typography accuracy
  becomes much harder to control» [V:XLHTLJhzDyQ 00:00–01:01].
- Ракурсы важнее числа: «If you only have a front photo of yourself, then when you turn around, it might look a different
  person» [V:5T0yRNmNRi4 07:10]; лист ракурсов на белом — «like a mini LoRA» [V:AxV8TR3BdqI 38:59] (F2 `06/02` §3.2).
- Лимиты вендоров (NB Pro до 14, FLUX.2 до 10 [V:y-RQ48sfPgM 03:13] [V:x8Yb4RidLgM 05:18]) — «принимает», а не «держит»: 1–3
  на вызов (F2 `06/02` §2.1).

## 4. Серии

### 4.1 Промт серии

Структура: **блок серии (дословно) → референсы с ролью → блок эффекта → слот сюжета → композиция и «против среднего» → палитра
→ запреты**. Поля: `series.{id, block, effect_block, slots, index, of, locks, reference_ids, avoid_average}`.

```text
// gpt-image-2-5-flare · 4:3, 1K · фикстура v2-series (2-я из 6) · polza 2026-09-23 · [не проверено]
Series style (keep identical): Flat vector illustration for a product onboarding series: uniform 2 px deep navy outlines, flat solid fills, cream background.
References: Image 1 is the style reference: match its line weight and palette only; the subject and scene come from this prompt.
Subject: A paper plane flying above a neat stack of documents.
Composition: Medium shot, main subject in the right third of the frame.
Composition rules: Off-center subject placed on a rule-of-thirds line, asymmetric composition.
Color palette: Cream (#F6F1E7) dominates, filling most of the frame; coral (#FF6B5B) is used only on the paper plane.
Constraints: No text.
```

- Блок — дословно одинаковый во всех кадрах: «Copy and paste the entire, unchanged character description» (01 §12.4); компилятор
  в `jobs` сверяет блок по `series.id` и пропускает задание с перефразированным блоком.
- Блок, который сам начинается с «Series style…», метку не получает (исправление F/07); «no X» в блоке у моделей без негативов
  (FLUX, Gemini, Recraft V4) — переписать утвердительно (F2 `06/01`).
- Слоты и итератор: «all the part that you are seeing here will be fixed. And the only thing I will change is the new scene»
  [V:I9xdmNZxIfA 09:29]; «A text iterator allow us to take a few items and run them simultaneously» [10:29]; каждый пункт — проверить
  («It's not a low angle almost, but it is a side view» [12:32]).
- Набор одним вызовом согласованнее отдельных (F2 `06/02` §4.1): «transform this subject… in five different ways» — «It at least
  has that context of what it's already generated» [V:H6ZXujE1qBA 11:10].

### 4.2 Шаблон эффекта

- «It's quite a short prompt… instead of the girl, we want… an old old man with beard… change the background… blue gray
  gradient»; «if you have the effect, it's already in the prompt. You can just change some details» [V:nBd9JJuAT1Y 44:00–45:01]
  (демо Recraft, 4 объекта) `[практика]` → `series.effect_block` дословно + `subject` и `environment` как слоты.

### 4.3 Против «среднего» вида

- Практика: модель тянет к «very centerframed medium shot right in the middle looking right at the camera… perfectly symmetrical,
  perfectly centered, perfectly lit… That's what the average is right now» [V:AxV8TR3BdqI 31:49–32:51]; лечат правилами:
  «never looking at the camera», «subjects never be perfectly centered… Rule of thirds… cut off the hood… clip the end» [46:07].
- Компилятор (`series.avoid_average` или `compile.anti_average`): «Off-center subject placed on a rule-of-thirds line, asymmetric
  composition» + «gaze turned away from the camera» (только если в кадре люди) + «natural imperfections» (только фото); с
  `subject_region: center` — ошибка. Блок композиции целиком (правая треть, срез краем, 40–50 % пустоты, ≤ 3 предмета) и
  метрики — F2 `06/04` §1.3, тест F-04.
- Замены запретов (`exclusions[].replace_with`) — без предметов: «no one in the frame», «only real physical objects», «clean,
  text-free surfaces»; «an empty desk…» или «a laptop whose screen…» впишут стол и ноутбук в каждый кадр серии, включая
  иллюстрацию (F/07).

### 4.4 System prompt для LLM, который пишет промты серии

```text
// system prompt писателя промтов серии · по Rory Flynn [V:AxV8TR3BdqI 28:44–47:08] (сводка трёх промтов; дословно — «role», «locks», «shot list», «no additional commentary») · [практика]
Role: lead CGI technical director for the <brand> image series.
Locks (never change): the exact product from Image 1 (fidelity lock), material continuity, proportional lock, environment
anchor, lighting from the same direction and in the same conditions, colour grading, level of imperfection.
Prohibitions: subjects never perfectly centred; never looking at the camera; no polished stock look; no text, logos or
watermarks that are not on the real product.
Shot list: 1 full front; 2 full side; 3 rear; 4 3/4; 5 low-angle hero; 6 detail close-up.
Output format: one prompt per line, each ending with *; no additional commentary; no special characters.
```

- «we're always prompting what it should do… what's great now in system prompts is what it shouldn't do»; «you keep finding
  problems and you keep adding to the system prompt» [V:AxV8TR3BdqI 29:46–30:46]; замки переиспользуются, композиция — своя у
  бренда [49:09].
- Две роли LLM (Figma Weave): описатель бренда по сетке картинок — «precise visual production brief»; писатель промтов — по
  брифу и переменной места [V:I9xdmNZxIfA 24:48–25:49]; первую роль в базе закрывает `vlm_to_dna.py` (F2), вторую — компилятор
  (из паспорта и спецификаций, а не свободным текстом LLM).

## 5. Продукт с текстом — 7 блоков

### 5.1 Порядок и дословные фразы

«Composition first, exact identity, typography control, true color, lighting harmony, optical clarity, negative constraints.
It's not about writing more, it's about writing in the right order.» [V:XLHTLJhzDyQ 03:05]; «If you don't anchor the
composition first, the model prioritizes the object itself and the overall aesthetic can become unstable» [01:01].

| Блок | Поля спецификации | Фраза-образец |
|---|---|---|
| 1 композиция | `composition` | «An editorial still life with diagonal placement and controlled directional lighting.» |
| 2 идентичность | `product.identity`, `product.locks`, `references[role=product]` | «The product must match the provided references exactly, including proportions, silhouette…» |
| 3 типографика | `text.strings[]`, `text.strict_spelling: true` | «Typography: the exact words "…" appear <where>, <alignment>, <orientation>; no misspellings, no extra letters, and no warped glyphs.» |
| 4 цвет по деталям | `product.parts[] {part, color, hex}` | «Deep cobalt blue upper, neon lime laces, off-white mid-sole, and mint heel lining.» |
| 5 свет | `light` | «…so the environment supports the product instead of competing with it.» |
| 6 оптика | `camera` | «Shallow depth of field, tack-sharp focus on the shoe and its typography, refined tonal balance, and no oversaturation.» |
| 7 запреты | `exclusions` | «No extra logos, no duplicated text, no invented branding, and no distorted lettering.» |

- Типографика — «a dedicated typography block… Typography should not be casually mentioned inside the general product
  description. It needs to be treated as a priority anchor» [V:XLHTLJhzDyQ 01:01–02:02]; «Models tend to improvise, so you need
  to block that behavior directly» [03:05] `[мнение вендора]` (ролик площадки, 2 картинки + 1 видео).
- Габарит для масштаба — `product.dimensions` («Scale: the bottle is 18 cm tall.»); тест W5-10 (E).

### 5.2 Компиляция

```text
// openai/gpt-image-2.5-sunburst · 1K · compile.order=product7 · фикстура v2-product · polza 2026-09-23 · [не проверено]
Image 1 is the product: keep its shape, proportions, materials, label and colors exactly as in the image (label and cap
exactly). Close-up, at eye level, main subject in the center of the frame. A skincare bottle on a travertine block in soft
morning light. The product is a matte white 250 ml bottle with rounded shoulders and a black flip cap. Keep the label layout,
cap shape and proportions exactly as on the real product. Scale: the bottle is 18 cm tall. The label reads "CALM SERUM",
placed on the bottle label. Render each text exactly once, clearly and legibly. No misspellings, no extra letters, and no
warped glyphs. No extra text, no watermarks, no unrelated logos. The cap is black (#111111); the label text is charcoal.
Travertine beige (#E9E1D6) dominates, filling most of the frame; black (#111111) is used only on the cap. Soft window daylight,
light from the left. Shot as a studio product photo, 85mm lens, f/5.6. No watermark.
```

- У FLUX.2 (без негативов) строка орфографии — утвердительно: «Every letter is spelled exactly as written, crisp and
  undistorted.»; кавычки — одинарные (`dialects.yaml` → `flux2.text.quote`).
- Кириллица в продукте — тот же блок + «in Russian (Cyrillic script)» (01 §12.7); как третья форма в блоке кириллицы E («блок
  типографики» против «строки в кавычках» и «всего промта по-русски») — предложение для N.

### 5.3 Видео продукта и цвет при референсах

- «instead of using a start image, we upload the same clean white studio references»; «Our prompt remains structured and minimal.
  We describe the scene, the camera movement, and keep the product identity consistent without redefining typography or altering
  branding» [V:XLHTLJhzDyQ 04:05–05:05]; в polza — Veo 3.1 Fast `REFERENCE_2_VIDEO` (I-19), Omni `images`, Seedance 2.x (видео —
  `04-video-prompting.md` §1.6).
- **Противоречие**: цвет по деталям в тексте при референсах (Magnific) против «не описывать видимое» (Vertex, BFL); вопрос
  зрителя без ответа — «Is there a reason you're describing the color when it's in the reference images?» → позиция базы: в
  картинке — называть (референс мог быть снят в другом свете), в видео с референсами — не переописывать `[спорно]`.

## 6. Соотношения и варианты формата

- `output.aspect_ratios` + `composition.safe_zones[] {ratio, keep_rect}` + `focal_point` → `prompt_compile.py ratios SPEC`: для
  каждого формата — `generate` (мастер), `crop` (прямоугольник в долях мастера по фокусу, внутри безопасной зоны) или
  `outpaint`, если зона не помещается.

```bash
# prompt_compile.py 2.1 — [проверено: ../../scripts/ai-media/tests/test_prompt_compile.py, раздел 10]
99-raw/tools/venv-D2/bin/python ../../scripts/ai-media/prompt_compile.py ratios ../../scripts/ai-media/tests/fixtures/D02/E1.spec.json
# {"ratio": "16:9", "strategy": "generate"} · {"ratio": "4:5", "strategy": "crop", "crop_box": [0.5, 0.0, 0.95, 1.0]}
# {"ratio": "9:16", "strategy": "outpaint", "note": "безопасная зона не помещается в кадр — аутпейнт (агент H)"}
```

- 9:16 из 16:9 — полоса шириной 0,316 кадра: если субъект с полем шире — аутпейнт (H `08/02` §4) или отдельная генерация под
  формат; растягивать подложку дублированием — брак [V:BVMuRw8BgJg 07:28] (H). `object-position` по фокусу — F2 `06/03`.
- У серии — один набор форматов для всех кадров; аутпейнт — тем же блоком серии.

## 7. Recraft V4: порядок и текст (вне polza; каналы — RouterAI, Gen-API)

Гайд «Prompting with Recraft V4» (кэш `99-raw/cache/recraft-D/prompt-engineering-guide_prompting-with-recraft-v4.md`, стр.
115–124, 180–189, 461–476) `[документация]`; задания Recraft — у G, компилятор — семейство `recraft-v4`.

| Сцена — 8 шагов «from global to local» | Вектор, лого, иконки — 6 пунктов | Текст — 8 пунктов |
|---|---|---|
| 1 Core concept — subject(s) and scene | 1 Graphic type (logo, icon set, symbol system) | 1 Format type (menu, editorial, packaging, poster) |
| 2 Background and environment | 2 Shape logic (geometry, symmetry, silhouette clarity) | 2 Primary headline (size + placement) |
| 3 Primary subject framing and pose | 3 Color system (strict palette definition) | 3 Secondary hierarchy |
| 4 Physical attributes and identity details | 4 Line discipline (consistent stroke, no texture) | 4 Color blocking logic |
| 5 Secondary subjects and spatial relationships | 5 Layout structure (centered, grid-based, scalable) | 5 Print surface and material |
| 6 Lighting direction and behavior | 6 Constraints (no gradients, no shadows) | 6 Spatial placement |
| 7 Camera, depth, and contrast | «Avoid texture or material-focused language» | 7 Readability constraints |
| 8 Mood and compositional resolution | | 8 All required text in quotation marks |

- «Elements placed earlier in the prompt receive higher priority»; «Structured prompts don't make results "better." They make
  outcomes intentional, controllable, and repeatable.»; поиск — «3–6 word prompts», точный ассет — структура; «Define the
  typographic system — not just the phrase» `[документация]`.
- Запреты фразами в тексте: «Flat colors only — no gradients, shadows, or texture.», «No text. No clutter.»; поле negative prompt
  было у V2/V3 (существительные без «no»); у V4 — нет (C1).

## Частые ошибки

- Сравнительная правка («darker», «more green», «bigger») без целевого значения — модель уходит в крайность.
- 6–10 изменений одним вызовом «чтобы сэкономить» — выполняется часть; у Nano Banana меняется ракурс.
- «Change the window sill to a fern» вместо «add a fern on the window sill» — глагол операции решает, что тронет модель.
- Правка правки правки без проверки — дрейф цвета и деградация деталей копятся; варианты — от мастера.
- Маска «как в OpenAI» для Qwen или наоборот — полярность противоположна; маска удаления без тени — «призрак».
- Референс без роли или с ролью на каждую картинку отдельно — промт раздувается, модель копирует сцену референса.
- «no X» вместо кадрирования референса-доминанты; «no X» в блоке стиля у FLUX, Gemini, Recraft V4.
- Перефразированный блок серии («почти такой же») — серия расползается; меняется только слот.
- «Против среднего» вместе с «по центру», «gaze turned away» у предмета, «natural imperfections» у плоской иллюстрации.
- Замена запрета с предметом («an empty desk») — предмет появляется во всех кадрах серии.
- Типографика внутри общего описания продукта; орфография «No misspellings…» у FLUX.2 (без негативов) — утвердительно.
- Кадрирование 9:16 из 16:9 при безопасной зоне шире 0,316 — субъект режется; нужен аутпейнт.
- Ошибки агентов: ссылка «Image 1» у Omni (там `<IMAGE_REF_0>` с нуля); `mask_url` у NB2, GPT Image 2.5, FLUX.2 в polza (маски
  нет); `negative_prompt` у Recraft V4 (поля нет); повтор старой формулы v2 без `op` для смешанной правки.

## Чек-лист

- [ ] В правке названы операция, что, где, на что (значением), что не трогать и что видно после?
- [ ] Не больше 5 изменений за вызов (у Nano Banana с лицом — одно)? [поправка фазы 5: у NB2 без лица 10 из 10 одним вызовом — D2-06, 1 образец]
- [ ] У смешанной правки свой глагол у каждого изменения (`changes[].op`)?
- [ ] Закрывающая фраза семейства и суффикс «Maintain the original composition and subject.» на месте?
- [ ] Варианты — от мастера; накопление — с маской и композитом или цепочкой ≤ 2–3 шагов с `edit_check.py` после каждого?
- [ ] Полярность маски — модели (компилятор привёл файл); маска удаления — с тенью и дилатацией?
- [ ] Каждый референс — с ролью и `note`; одинаковые роли — одной фразой; 1–3 референса; порядок входов зафиксирован?
- [ ] Синтаксис ссылки — семейства (Omni с нуля, Kling `@Name`, Seedance 2.0 `<Image_N>`)?
- [ ] Блок серии дословно одинаков во всех спецификациях `series.id`; меняется только слот?
- [ ] «Против среднего» не спорит с композицией; замены запретов — без предметов?
- [ ] Продукт с текстом — 7 блоков по порядку, типографика отдельным блоком, орфография в форме семейства?
- [ ] Формат из мастера — кадрированием только если безопасная зона помещается (`ratios`)?

## Открытые вопросы и противоречия

1. **≤ 5 изменений** — порог базы, у Google «five» — пример; D2-06 (NB2) даст первую точку; для GPT Image 2.5 и Qwen — нет данных.
   [поправка фазы 5, 25.09.2026: первая точка — NB2 выполнил 10 из 10 одним вызовом; порог не подтверждён, но и не опровергнут на
   других моделях (n = 1)]
2. **Цепочка против «от мастера»** — Google против H2; для безмасочных моделей композит требует маски из разницы (`edit_check.py`
   её не строит автоматически) — задача K/H.
3. **Группа референсов** («Images 1-3 are…») не проверена генерацией против «по фразе на картинку» — плечо F-01 (F2).
4. **Цвет в тексте при референсах** — Magnific против Vertex/BFL; тест не заведён.
5. **Суффикс «Maintain the original composition and subject.»** — из кода демо OpenAI (gpt-image-1); на GPT Image 2.5 и NB2 не
   проверен (W2-7, 8 ₽ — в плане W, пересечение с H).
6. **Роли референсов у Grok Image 2.0** (правка до 5 картинок, снимок 17:45) не документированы — синтаксис «the provided
   images» — наш.
7. **Шаблоны инпейнта и аутпейнта Qwen** — из переписчика открытой модели; как их обрабатывает `mie` в polza — неизвестно.

## Источники

- [S1] Google — Gemini API «Nano Banana image generation» (01 [S2]) — https://ai.google.dev/gemini-api/docs/image-generation — формула правки «change only… Keep everything else…», роли референсов; надёжно.
- [S2] OpenAI — «Image prompting» и «Image generation» (01 [S12], [S14]) — https://developers.openai.com/api/docs/guides/image-generation — «replace ONLY», маска «guidance», «Reference each input by index»; надёжно.
- [S3] OpenAI Cookbook — «GPT Image Generation Models Prompting Guide», 04.2026 (01 [S13]) — перевод правкой, порядок сегментов; надёжно.
- [S4] Black Forest Labs — «Prompting Guide — FLUX.2», Image Editing, Multi-Reference (01 [S15], [S18]) — https://docs.bfl.ml/guides/prompting_guide_flux2 — «Change nothing else», «subject from image 1…»; надёжно.
- [S5] BytePlus — «Seedream 4.0–4.5 prompt guide», 2026-07-06 (01 [S22]) — роли референсов, правка по рамке; надёжно.
- [S6] QwenLM — `Qwen-Image` (README, `prompt_utils_2512.py`) (01 [S31]) — шаблоны инпейнта и аутпейнта, «Replace Y with X»; надёжно, открытая модель.
- [S7] Recraft — «Prompting with Recraft V4» (кэш `99-raw/cache/recraft-D/prompt-engineering-guide_prompting-with-recraft-v4.md`, 563 строки) — 8 / 6 / 8 пунктов, кавычки, длина; надёжно.
- [S8] polza — каталог `99-raw/cache/polza/2026-09-23_1745/api-v1-models.json` — маски (`qwen/image-2.1` белое = менять, `openai/gpt-5-image` чёрное), число картинок; первоисточник канала.
- [V:2RD3FP5iWJY] Jamey Gannon — «5 steps to generate consistent brand images with Midjourney» (2026-03) — формула правки, референс несёт стиль, кроп доминанты; практик.
- [V:H6ZXujE1qBA] Google (команда nano-banana) — «Behind the scenes of Google's state-of-the-art "nano-banana" image model» (2025-08) — порции правок, «keep his face visible», N вариантов; вендор.
- [V:8kM5aDD5gLI] OpenAI — «Build Hour: Image Gen» (2025-05) — антипример «darker green», суффикс, безмасочное удаление; вендор.
- [V:7-YIYlIhksM] VideoSmile — «GPT Image 2.5 — Обзор возможностей нейросети» (2026) — составная правка на NB меняет ракурс; практик, 1–3 примера.
- [V:hzPKb8bDvdY] Zach Leach (Gamma) — «How I AI» (2025) — провал многошаговых правок по ≈ 550 отзывам; практик, данные без методики.
- [V:SLnGJ9iezYo] Ruben Stom — «Design an Animated Website Hero with AI — Claude & Higgsfield» (2026) — деградация при повторных правках (через H2); практик.
- [V:_Bc4g6fFMp0] Макс Кукушкин (ЦЕХ) — «"3D" моушен графика в бесплатном Kling и Nano Banana Pro» (2026) — «оберег»; практик.
- [V:AxV8TR3BdqI] Rory Flynn — «Weavy Flow State #1» (2026-02) — system prompt серии, «keep this, change that», против «среднего»; практик.
- [V:I9xdmNZxIfA] Figma — «Figma deep dive: Weave», Config 2026 — блок + слоты + итератор, «only to preserve the subject identity»; практик.
- [V:nBd9JJuAT1Y] Recraft — «Session 2: overview of Recraft V4» (2026-02-25) — шаблон эффекта, вариант правкой промта; вендор.
- [V:XLHTLJhzDyQ] Magnific Academy — «Keeping product text consistent with Nano Banana Pro and Kling 3.0 Omni» (2026-03) — 7 блоков продукта; вендор площадки.
- [V:5T0yRNmNRi4] Google «Release Notes» — «Introducing Gemini Omni» (2026-05) — ракурсы референса; вендор.
- [V:y-RQ48sfPgM] Google — Nano Banana Pro (2025-11-20; из транскрипта) — перевод правкой, 14 референсов; вендор.
- [V:x8Yb4RidLgM] Black Forest Labs — FLUX.2 (из транскрипта) — до 10 референсов; вендор.
- Своё и соседи: `99-raw/notes/wave2/D2-helper-digests.md` (разделы C–F), `99-raw/experiments/D2/01-compiler-v2`,
  `99-raw/experiments/F/07-dna/README.md` (прогон «паспорт → промт», 5 ошибок стыка), `../08-image-post-processing/02-upscale-outpaint-edit.md`
  §2, §4 (H2), `../06-art-direction-consistency/02-series-and-consistency.md`, `04-slop-and-color-harmony.md` (F2),
  `01-vendor-prompt-guides.md` §12.3–§12.7.
