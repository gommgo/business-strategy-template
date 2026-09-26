# Серии и консистентность: референсы, эталон, набор одним вызовом, дрейф

Волна 2 · агент F (продолжатель F2) · 23.09.2026 · опора: выжимка помощника `99-raw/notes/wave2/F-src-series.md` (17 источников:
документация OpenAI, Google, BFL, BytePlus, Qwen, Recraft, Ideogram, Midjourney; бенчмарки ViStoryBench, MultiBanana, MultiRef,
T2IS, OmniRef-Bench, DreamBench++, MICON-Bench, CSD, DreamSim), 9 дайджестов роликов, отчёты W1–W5 · опыты
`99-raw/experiments/F/06-series-metrics`, `F/05-color`, `F/07-dna`, `F/08-icon3d-inputs` · каталог polza 2026-09-23 · тесты фазы 5
`99-raw/phase5/F-plan.md` (F-01…F-07). Модель для серии выбирает стенд E (`../13-routing-matrix/`); здесь — **метод**.

## Выжимка для агента

1. **1–3 референса на вызов**, одной съёмки, с ролью: лимит вендора (8–16) — «принимает», а не «держит». MultiBanana:
   Nano Banana 5,27 → 3,85, GPT-Image-1 5,78 → 4,05 при росте 3 → 8 референсов; MICON: открытые модели 88,5 → 75,1 уже на 4
   → §2.1 `[исследование]`.
2. **Смешанные референсы сталкиваются, а не усредняются**: модель «lifts details, objects, and motifs from each one and
   stitches them together» (Recraft); разнородный мудборд усредняется в чужие признаки [V:2RD3FP5iWJY 08:07–09:07] →
   §2.1 `[документация; консенсус практиков; тест F-01 C]` [поправка фазы 5, 25.09.2026: F-01 — мудборд из 8 + роль + блок дал ΔE
   палитры 0,035–0,041 (утечки мотивов не видно), 3 референса одной съёмки — 0,031–0,035 (3 из 3 ≤ 0,05), только блок — 0,042–0,058
   (2 из 3 > 0,05) → `99-raw/phase5/runs/2.3-series/F-01_sheet.jpg`]
3. **Сомневаешься — один референс**: «One reference is the safe move»; повторяющийся результат лечить подробным промтом, а не
   новым референсом (Recraft) → §2.1 `[мнение вендора]`.
4. **Роль — текстом по номеру входа**; поля роли нет ни у одного вендора; порядок входов зафиксировать в паспорте и не
   менять между кадрами → §2.2 `[документация: OpenAI, Google, BFL, BytePlus, Qwen]`.
5. **Стиль по картинке — слабейшая ось**: OmniRef-Bench стиль — NB Pro 0,46 / 8,37, Seedream 4.5 0,34 / 6,27, FLUX.2 [klein]
   0,21 / 2,18 → стиль держать тремя средствами: блок стиля + палитра с названиями + 1–3 стилевых референса; проверять
   утечку содержания → §2.3 `[исследование]`.
6. **Референс-доминанта** (яркая деталь одного референса повторяется в выдаче) → кадрировать или убрать референс, а не
   «no X» [V:2RD3FP5iWJY 09:07, 18:16–20:17] → §2.4 `[консенсус практиков; тест F-03]`.
7. **Референс работает на классе сюжетов, на котором собран** → в паспорте у референса `class`; для нового класса — блок и
   палитра без референсов, затем свой эталон → §2.5 [V:2RD3FP5iWJY 31:28–33:30].
8. **Эталон → остальные от эталона, не от соседа**; список неизменного повторять на каждой итерации; пиксельную
   неизменность — композитом, а не промтом → §3.1 `[документация: OpenAI; консенсус]`.
9. **Лист персонажа или продукта — один референс**: 16:9 крупный план + фигура целиком без головы [V:ttgNFJ25xfU 19:25];
   продукт на белом → 9 ракурсов с «замками» → лист как референс («mini LoRA») [V:AxV8TR3BdqI 33:51–39:59] → §3.2.
10. **Ракурсы референса важнее их числа**: только анфас → при повороте «другой человек» [V:5T0yRNmNRi4 07:10, 18:27] → §3.2.
11. **3D-серия иконок**: форма — рендер или скрин, материал — референс-«кубик», один ракурс и свет на всю серию
    [V:RIS8ckTfKAg 13:22–16:16] → §3.3 `[тест F-07]` [поправка фазы 5, 25.09.2026: F-07 — IoU силуэта 0,95 и 0,92 (Sunburst 1K),
    n = 2 → `99-raw/phase5/runs/2.3-series/F-07_sheet.jpg`]
12. **Набор одним вызовом согласованнее отдельных вызовов**: общий «consistency prompt» + свой промт на кадр — 0,241 → 0,376
    (T2IS); сетка 2×2 лучше полосы 1×5 → §4.1 `[исследование]` [поправка фазы 5, 25.09.2026: F-02 — сетка 2×2 Sunburst 2K (7 ₽
    за 4 клетки 1152×768) дала ΔE 0,031–0,036 и единый свет — наравне с отдельными кадрами F-01 A, не лучше (n = 1)]
13. **Сетка 2×2 → нарезка**: `split_grid.py` режет с желобами и без пиксельно точно; ячейка ≥ 1000 px → сетка 2K → §4.2
    `[проверено: F/06; тест F-02]`.
14. **Seedream 4.0 / 4.5 / 5.0 lite — серия нативно**: `sequential_image_generation: "auto"` + `max_images` 1–15; у 5.0
    pro/flash нет; число картинок решает модель; референсы + выходы ≤ 15 → §4.3 `[документация: BytePlus]`.
15. **Промт серии = дословный блок стиля + слоты + итератор**; вариант серии — правка поля спецификации, не картинки →
    §5.1 [V:I9xdmNZxIfA 09:29–10:29] [V:nBd9JJuAT1Y 29:40].
16. **Скрытые переписчики промта — выключить или логировать**: FLUX.2 [pro]/[max] апсемплинг (в polza не управляется), Qwen
    `prompt_extend`, OpenAI `revised_prompt`, Seedream `optimize_prompt_options` → §5.2 `[документация]`.
17. **Seed ≠ стиль**: у OpenAI, Gemini, Seedream 4.5+ его нет; Midjourney: seed «can't capture or bookmark a specific style»
    — seed только для повтора одного запроса → §5.3 `[документация]`.
18. **Пороги серии (фото)**: разброс оттенка ≤ 10°, ΔE палитр ≤ 0,045 (макс ≤ 0,06), σ светлоты ≤ 0,04; распад — > 25° или
    > 0,06; pHash < 10 из 64 — дубль сюжета → §6.1 `[проверено: F/06]`.
19. **Метрики цвета не видят стиль**: второй судья — голоса и бинарные VLM-вопросы, ≥ 2 прогона, проходит единогласное «да»
    → §6.2 `[исследование: MICON, T2IS; практика BFL]`.
20. **Согласованность без копирования**: копия референса даёт рекордные метрики сходства (CIDS 0,911 при соответствии
    сюжету 0,91 из 4) → приёмка = согласованность + соответствие брифу + сторож копирования → §6.3 `[исследование: ViStoryBench]`.
21. **Recraft V4 Styles — единственный сохраняемый стиль-объект в API** (`style_id` из 1–10 картинок, палитра внутри стиля,
    $0,005); через RouterAI `style_id` не возвращается — стиль заново в каждом вызове по `input_references` → §1, §7 `[тест F-06]`.
22. **Модель для серии выбирает стенд E**: публичных измерений серий у GPT Image 2/2.5, NB2, Seedream 4.5/5, FLUX.2 [pro]/[max]
    нет (ViStoryBench и MultiBanana тестировали поколение 2025 года) → §1 `[исследование]` [поправка фазы 5, 25.09.2026: E-12 (2 сюжета
    × 4 модели по эталону NB2) — стиль держит Flare (контур, палитра в обоих сюжетах); NB2, NB Pro, Seedream 4.5 сменили палитру —
    «домашнего» преимущества семейства эталона нет, n = 1 → `99-raw/phase5/runs/2.3-series/E-12_blind_sheet.jpg`]

## 1. Механизмы по моделям (документация на 23.09.2026)

| Модель | Референсов: вендор / polza | Роли | Seed | Инструмент серии | Рецепт вендора |
|---|---|---|---|---|---|
| GPT Image 2.5 Sunburst / Flare (`openai/gpt-image-2.5-sunburst`) | не указан («one or more») / 16 | текстом: «Image 1: product photo… Image 2: style reference…»; маска — к первой картинке | нет | `n`, правки с эталоном на входе | «character anchor»: эталон → правка с блоком «Character Consistency» + «Do not redesign the character»; повторять список неизменного [S1] |
| Nano Banana Pro (`google/gemini-3-pro-image-preview`) | 14 (≤ 6 объектов, ≤ 5 персонажей, ≤ 3 стилевых) / 8 | «Use Image A for the character's pose, Image B for the art style…» | нет | многоходовый чат | «generate… one at a time»; при дрейфе — новый диалог с подробным описанием [S2] |
| Nano Banana 2 (`google/gemini-3.1-flash-image`) | 14 (≤ 10 объектов + ≤ 4 персонажа) / 14 | как Pro | нет | чат | «Excelling at multiple reference image processing and consistency» [S2] |
| NB2 Lite (`google/gemini-3.1-flash-lite-image`) | «up to 14», но «Not optimized for multiple reference inputs» / 10 | как Pro | нет | — | для серий по референсам вендор не рекомендует [S2] |
| FLUX.2 [pro]/[max] (`black-forest-labs/flux.2-pro`) | 8 (9 МП на вход и выход) / 8 | «image 1», «image 2»… в тексте | да (в API BFL) | — | [max] создаёт референс персонажа → [pro] вариации; hex 3–5 с привязкой; апсемплинг выключать `disable_pup` [S3] |
| Seedream 4.0 / 4.5 / 5.0 lite (`bytedance/seedream-4.5`) | 14 (5.0 pro/flash — 10) / 4.5 — 14, 4 — 10 | «Image 1/2/3»; «Reference Target» + «Generated Scene Description» | BytePlus — нет; polza — у `seedream-4` | `sequential_image_generation` | «a series», «a set» или число в тексте запускают серию [S4] |
| Qwen Image 2.1 (`qwen/image-2.1`) | 10 / 10 | «image 1», «[image 1]», `<image1>` | да | маска, правка | лист «three-view character reference» → раскадровка (витрина); веса — некоммерческие [S5] |
| Recraft V4 Styles (RouterAI `recraft/recraft-v4-styles`) | 1–10 картинок на стиль | роли нет: стиль — объект `style_id` | да (`random_seed`) | `style_id` на весь набор, `match: precise/flexible` | «similar references sharpen the match, varied references widen the range» [S6] |
| Ideogram 4 (API, вне polza) | 0 в `generate`; `remix-v4` — 1 | неизменный `style_description` в JSON | в запросе нет | `describe-v4`: картинка → JSON-стиль | палитра ≤ 16 hex, «soft color bias» [S7] |
| Midjourney V8.2 (API нет) | `--sref` несколько, Edit Model — 4 | `--sref URL1::2 URL2::1`, `--sw` 0–1000 | `--seed` | коды стиля, мудборды | «combine your characters into a single reference image» [S8] |

Что известно о качестве серий `[исследование]`: ViStoryBench-Lite (CVPR 2026, 20 историй) — лучшее соответствие сценарию у NB Pro
(3,37 из 4, CIDS к референсу 0,581), худшая идентичность у Seedream 4.0 (0,280); по стилю NB Pro — 14-е место [S9].
OmniRef-Bench (июнь 2026, 395 примеров): NB Pro 8,50 (VLM, 0–10), Seedream 4.5 8,13 — идентичность субъекта у Seedream выше
(8,77), стиль ниже (6,27 против 8,37) [S12]. MICON-Bench: GPT-Image 91,51 против Nano Banana 89,25 (версии 2025 года) [S14].
Recraft: Precise-режим выиграл 91,6 % парных сравнений на 159 стилях против GPT Image 2 High, NB Pro, Seedream 5.0 Pro, FLUX 2
Max — тест вендора, методика «по запросу» [S6] `[мнение вендора]`. Серий у GPT Image 2/2.5, NB2, Seedream 4.5/5, FLUX.2
[pro]/[max] не мерил никто — решает стенд E на методе F.

## 2. Референсы: сколько, какие, с какой ролью

### 2.1. Число и однородность

| Источник | Что намерено | Число |
|---|---|---|
| MultiBanana (CVPR 2026) [S10] | «X Objects», среднее двух VLM-судей, 0–10 | Nano Banana 3 → 8 реф.: 5,27 → 3,85; GPT-Image-1: 5,78 → 4,05; Qwen-Edit-2509: 4,37 → 1,65 уже на 5 |
| MICON-Bench [S14] | композиция объектов, открытые модели | BAGEL 88,50 (2) → 84,37 (3) → 75,11 (4) → 66,36 (5) |
| Qwen-Image-Edit-2509 [S5] | документация | «Optimal performance is currently achieved with 1 to 3 input images» |
| Recraft V4 Styles guide [S6] | документация | «One reference is the safe move»; несколько — только «from the same visual world» |

Два режима отказа (MultiBanana): закрытые модели включают все субъекты, но «generate globally inconsistent or distorted
scenes due to overfitting to fine-grained reference details»; открытые — теряют субъекты, но дают чистый кадр. Разные домены
(фото + рисунок) — «all models tend to distort individual reference attributes» [S10]. Практики: мудборд из ~30 удачных
кадров — для отбора, в вызов идут 3–5 отобранных; «18 srefs — too busy» [V:2RD3FP5iWJY 29:25–31:28, 46:44].

### 2.2. Роль — текстом

```text
// openai/gpt-image-2.5-sunburst · polza 2026-09-23 · [не проверено; = F-01 A]
Series style (keep identical across the series): documentary outdoor photograph of a quiet city park in early autumn; …
References: Images 1-3 are style references from one photo shoot. Match their light, colour grading, lens and grain;
do not copy their scenes or composition.
Subject: a weathered wooden park bench under a birch tree, a few fallen yellow leaves on the seat.
Composition: website feature card, 3:2; the main subject sits in the right half, calm grass and sky on the left.
Constraints: No people. No text. No watermark.
```

- Синтаксис: OpenAI — «Reference each input by index and description… describe how they interact» [S1]; Google — «clearly
  define the role of each» [S2]; BFL — «subject from image 1, style from image 2, background from image 3» [S3]; BytePlus —
  «Reference Target» и «Generated Scene Description» [S4]; Qwen — «[image 1]» [S5].
- «Только идентичность» (продукт, персонаж): «use the reference image only to preserve the subject identity. Create a
  completely new shot from…» [V:I9xdmNZxIfA 08:27–10:29] — вариант промта в продуктовом тесте E (W4-7).
- «Identity locking» у Google: «Keep the person's facial features exactly the same as Image 1» + описывать изменение позы
  или эмоции [S2] `[мнение вендора]`.
- Формулировки ролей для компилятора — `../05-prompting/05-edit-reference-series.md` (D2b) и `asset-spec` `references[].role`.

### 2.3. Стиль держат три средства

Перенос стиля по картинке — слабейшая ось даже у лидеров (§1); у Seedream 4.5 стиль-референс держится хуже идентичности
[S12]. Поэтому: (1) блок стиля дословно первым абзацем; (2) палитра — 3–5 цветов названием и hex с привязкой к объекту;
(3) 1–3 стилевых референса одной съёмки. Проверять **утечку содержания**: объективная метрика света OmniRef дала 0,883 кадру,
где модель скопировала из референса человека, попугая и стол, — поймал только VLM [S12]. Вопрос судье: «Есть ли в кадре
предметы или места из референсов, которых нет в брифе?»

### 2.4. Референс-доминанта: убрать или кадрировать, а не «no X»

Яркая деталь одного референса расползается по серии: зелёная тень у глаза на одном референсе → зелёный каст всей выдачи;
референс убрали — каст ушёл; пузырь жвачки срезали кадрированием — «Changing the visual input worked better than adding
another negative instruction» [V:2RD3FP5iWJY 09:07, 18:16–20:17] [S8 — практика Jamey Gannon] `[консенсус практиков]`.
«no X» у энкодерных моделей провоцирует объект (D `05/03`). Тест F-03: кафе с красно-жёлтыми подушками — полный референс,
полный + «Do not include…», кроп без подушек; критерий — доля насыщенных красно-жёлтых пикселей (OKLCH C > 0,12, h 20–100°)
и VLM «есть подушки?» (`99-raw/phase5/jobs/F-03-dominant-crop.jsonl`, 24 ₽).

### 2.5. Класс сюжетов

Референс, собранный на одном классе сюжетов, тянет его в другой: стиль, отлаженный на черепахах, на «sexy lady» ломается
[V:2RD3FP5iWJY 31:28–33:30]; перенос цвета с эталона парка на площадь и пляж даёт горчичную площадь и фальшивый закат
(F/05). → У референса в паспорте `class`; `to-spec --ref-class` берёт только свой класс; тестовые сюжеты-канарейки разных
классов [V:2RD3FP5iWJY 11:09–12:10] ловят, где стиль перестал держаться.

## 3. Протокол эталона

### 3.1. Эталон → серия

1. Направления — в «силосах», якорная картинка на направление [V:ttgNFJ25xfU 14:20]; N ≥ 4 дешёвых вариантов → отбор по
   ручному протоколу A (5 с взгляд, зум 200 %, список предметов) → **один утверждённый эталон**.
2. Остальные кадры: эталон на входе с ролью + тот же блок стиля + слот сюжета («make the rest» в том же контексте)
   [V:bH2nP-aCFjk 25:48–27:53].
3. Каждый кадр — **от эталона, не от соседа**: цепочка «кадр из кадра» копит дрейф (цвет «запекается», «seven stomachs
   later») [V:ttgNFJ25xfU 1:01:07]; OpenAI: «Repeated edits can still change details you intended to preserve. Restate those
   constraints… If a region must remain pixel-identical, composite the approved edit into the original image» [S1].
4. Дрейф лечится: OpenAI — повтором списка неизменного; Google — новым диалогом с подробным описанием; BFL — сверкой всего
   пакета с каноническим эталоном по «named, falsifiable features» [S1][S2][S3]; повторы одного промта начали
   «галлюцинировать» → фиксировать удачный первый [V:RIS8ckTfKAg 19:17–20:18].
5. Пиксельная защита продукта — композит оригинала и проверка `edit_check.py --protect` (H, `../08-image-post-processing/02-…`).

### 3.2. Лист персонажа и продукта

- Персонаж: лист 16:9 — чёткий крупный план + фигура целиком **без головы** [V:ttgNFJ25xfU 19:25]; баланс референсов:
  общий план — плывёт лицо, крупный — одежда [V:ttgNFJ25xfU 58:03]; ракурсы важнее числа [V:5T0yRNmNRi4 07:10, 18:27].
  «Character sheet» как единый референс — сквозной приём вендоров (Qwen 2.1 «three-view character reference», Recraft V4.1
  front/profile/back/¾, Midjourney «combine your characters into a single reference image», BFL «Provide multiple angles»)
  [S3][S5][S6][S8] `[документация; не измерен ни одним бенчмарком]`.
- Продукт: белый студийный фон → лучше перенос; 9 ракурсов с «замками» (fidelity, material continuity, proportional lock,
  environment anchor, same lighting) → лист = «mini LoRA»; гид пропорций отдельным референсом; недостающий ракурс — отражением
  [V:AxV8TR3BdqI 33:51–42:01]. Товар в интерьере сверять со спецификацией: масштаб, цветовая температура по техкарте (4000 K)
  [V:5dnNUB27HBQ 21:30–26:35]. BFL product-ads: ракурсы из реального фото с `input_image` и seed; 14 пластин → 13 совпали,
  одну «off-model» сигнальные проверки пропустили [S3] `[практика вендора]`.
- Люди-доказательства (команда, отзывы, клиенты) не генерируются: «реальный человек + ИИ-окружение» (A `01/03` §1–§2).

### 3.3. 3D-иконки

Форма — рендер или скрин (SVG → выдавливание → скрин) [V:RIS8ckTfKAg 14:13]; материал — отдельный референс-«кубик»
[V:RIS8ckTfKAg 15:15]; все элементы под одним углом, свет с одной стороны [V:RIS8ckTfKAg 13:22]; материал — главный
стилеобразующий элемент пака [V:RIS8ckTfKAg 06:24]. Входы F-07 готовы: Blender 5.2.2 — формы «коробка» и «кольцо» в серой
глине, «кубик» рифлёного стекла, маски силуэтов (`99-raw/experiments/F/08-icon3d-inputs/`); критерий — IoU силуэта ≥ 0,9,
светлая сторона сверху-слева, один материал на обеих формах. Поля паспорта — `icon3d` (`01-visual-dna-from-ui.md` §2).

## 4. Набор одним вызовом

### 4.1. Что намерено

T2IS (2025, 596 инструкций, судья Qwen2.5-VL-7B по логитам «Yes/No», Pearson 0,78 с людьми): общий «consistency prompt» на
набор + отдельный промт на каждый кадр — согласованность 0,376 против 0,241 без него; без генерации «с учётом набора» —
0,318 и падение качества 0,520 → 0,326; «the 2×2 grid configuration achieves superior results… the 1×5 arrangement tends to
introduce consistency mismatches between the first and last images»; наборы > 5 — скользящее окно 4 с шагом 2; группа
«Design Style» (постеры, упаковка, бренд-материалы) — самая трудная: style 0,391 [S11] `[исследование; 512 px, модели 2025]`.
Практики: сетка 2×2 одной генерацией → «split and upscale» [V:ttgNFJ25xfU 26:30, 28:31]; контакт-лист 3×3 одним промтом
[V:AxV8TR3BdqI 44:02]. **Противоречие**: Google советует «generate… one at a time» в одном чате [S2], ViStoryBench гоняет
модели покадрово с предыдущим кадром в истории [S9] — различает тест F-02.

### 4.2. Сетка 2×2 → нарезка

```bash
# split_grid.py (Python 3.13, Pillow, numpy) — [проверено: 99-raw/experiments/F/06-series-metrics, повтор F2 17:55]
python3 ../../scripts/ai-media/split_grid.py grid.png cells/ 2 2
# желоб ищется как полоса с σ < 4 из 255 у каждой границы, иначе равное деление;
# синтетика 2×2 из 800×533 с желобами 16 px и без: 4 ячейки ровно 800×533, max |Δ| = 0
```

Правила: сетку просить с «thin white gutters about 1 percent of the width» и «In every cell the main subject sits in the right
half of the cell» (F-02); ячейка ≥ 1000 px → сетка 2K (GPT Image 2.5 Sunburst 2K — 7 ₽ против 4 × 4 ₽ за четыре 1K,
polza 2026-09-23); проверять, не сливаются ли ячейки (общие объекты через границу).

### 4.3. Seedream: серия нативно

`sequential_image_generation: "auto"` + `sequential_image_generation_options.max_images` (1–15, по умолчанию 15) — у 5.0 lite,
4.5, 4.0; у 5.0 pro/flash «not currently supported». «auto: The model determines whether to return multiple images and how
many images to return based on the prompt» — `max_images` лишь потолок; референсы + выходы ≤ 15; триггер — «a series», «a set»
или число [S4] `[документация]`. Передаёт ли polza эти поля — проверить в фазе 0 (протокол B).

## 5. Промт серии

### 5.1. Блок + слоты + итератор

- Постоянный блок стиля дословно + слоты (сцена, место, продукт) + итератор по списку сцен [V:I9xdmNZxIfA 09:29–10:29];
  пункт промта не выполнен → чек-лист по пунктам [V:I9xdmNZxIfA 12:32].
- «Шаблон эффекта»: постоянный блок эффекта + переменные объект и фон [V:nBd9JJuAT1Y 42:58–47:10]; вариант серии — правка
  промта или спецификации, а не картинки [V:nBd9JJuAT1Y 29:40–31:45]; многошаговые правки проваливаются [V:hzPKb8bDvdY 13:19].
- На масштабе — шаблон со случайными слотами и **отбор входа, а не выхода**; стиль, терпимый к дефектам (эмбиент, а не
  изометрия) [V:oDok8FcX6rM 13:13, 14:14–15:15, 34:40].
- Ограничивать число элементов: модель как «overeager student» перегружает кадр [V:KLDdXOw6jIc 38:41].
- Поля компилятора: `series.block`, `series.effect_block`, `series.slots`, `series.avoid_average`; одинаковый блок во всех
  спецификациях серии проверяет компилятор — `../05-prompting/05-edit-reference-series.md` (D2b).

### 5.2. Скрытые переписчики промта

| Модель | Переписчик | Для серии |
|---|---|---|
| FLUX.2 [pro]/[max] | апсемплинг по умолчанию, `disable_pup: true` | в polza не управляется → вариативность; прямой ключ BFL не заводится |
| FLUX.2 [flex] | `prompt_upsampling` по умолчанию true | выключить (Gen-API — тест D2) |
| Qwen Image (Model Studio) | `prompt_extend` по умолчанию true; PE-модели | фиксировать переписанный текст, повторять его |
| OpenAI Responses | главная модель пишет `revised_prompt` | логировать |
| Seedream | `optimize_prompt_options.mode` standard/fast | логировать |
| Ideogram 4 | `text_prompt` → magic prompt | для серии — `json_prompt` |

### 5.3. Seed

Seed есть у FLUX.2 (API BFL), Qwen 2.1, Recraft, Ideogram (веса, v3), Midjourney; в polza — `qwen/image-2.1` и
`bytedance/seedream-4`; нет у OpenAI, Gemini, Seedream 4.5+ [S1–S8]. Midjourney: «Seeds can't capture or bookmark a specific
style, character, or appearance across different prompts… if you take a break and come back later, your seed may no longer
work as expected» [S8]. Seed — только для повтора одного запроса (A/B, перегенерация).

## 6. Дрейф: как ловить

### 6.1. Пороги на цвете (бесплатно)

```bash
# series_metrics.py (Python 3.13, numpy, Pillow) — [проверено: 99-raw/experiments/F/06-series-metrics]
python3 ../../scripts/ai-media/series_metrics.py s1.png s2.png s3.png --ref ref1.jpg ref2.jpg ref3.jpg
```

| Набор (калибровка F/06) | σ L | σ C | разброс оттенка | ΔE палитр средн / макс | pHash мин |
|---|---|---|---|---|---|
| одна съёмка (3 кадра) | 0,032 | 0,002 | **5,7°** | **0,038** / 0,044 | 19 |
| две локации (2 + 2) | 0,036 | 0,007 | 27,8° | 0,048 / 0,064 | 22 |
| четыре локации | 0,117 | 0,026 | **104°** | **0,091** / 0,152 | 26 |

→ «Одна серия» (фото): оттенок ≤ 10°, ΔE палитр ≤ 0,045 средн и ≤ 0,06 макс, σ L ≤ 0,04, σ C ≤ 0,005; распад — > 25° или
> 0,06; ΔE палитры кадра к эталону: 0,006 у кадра той же съёмки против 0,071–0,115 у чужих `[проверено]`. Пороги — для фото
одной съёмки; у плоских иллюстраций ΔE ниже — калибровать на эталоне паспорта.

### 6.2. Судья смысла

- Бинарные фальсифицируемые утверждения с номером кадра: «Check identity across the pack, not one still at a time… compare
  each of the others to it on named, falsifiable features»; «Run every sheet at least twice and fold harshly. Only unanimous
  PASS passes»; «A false PASS from a thin assertion set is more dangerous than having no semantic gate at all» (BFL skill) [S3].
- Надёжность судьи растёт с узостью вопроса: бинарные чекпойнты MICON — отклонение от людей +0,67 балла, ранги совпали, 5
  прогонов ±0,04 [S14]; «да/нет» по логитам T2IS — r 0,78 [S11]; шкала 0–4 с критериями DreamBench++ — 79–84 % согласия
  человек-человек, few-shot вредит (до −0,155 α), убрать критерии — −0,09…−0,23 [S13]; свободные 1–10 — r 0,55–0,69
  (MultiBanana) [S10] `[исследование]`.
- Человек: серия рядом в одном размере + размытие — одинаковы ли пятна по весу (A `01/03` §6.3 п. 5; ui 07/02 §11.2); «explain
  why these top four aren't in the same style» — LLM как второй взгляд [V:2RD3FP5iWJY 07:06]; голоса попарно бок о бок
  [V:KLDdXOw6jIc 42:47].

### 6.3. Какие метрики для чего

| Метрика | Что ловит | Согласие с людьми | Применение |
|---|---|---|---|
| CSD (стилевой CLIP) | единство стиля | Self-CSD ↔ люди ρ 0,565 (ViStoryBench) | основная метрика стиля (K); на тонких фирменных различиях не калибрована [S15] |
| CIDS (вырезка + ArcFace/CLIP) | идентичность персонажа | ρ 0,676, r 0,796 | персонаж, маскот; продукт — DINOv2/CLIP по вырезке |
| DINOv2 / DreamSim | близость картинок | DreamSim 96,2 % на близких вариантах; DINO 50,7 % на сохранении концепта | **сторож копирования**: слишком высокая близость разных сюжетов или к референсу [S13][S16] |
| ΔE палитры, σ L/C, оттенок | дрейф цвета | прямой валидации нет | жёсткий сторож палитры (F/06) |
| pHash | дубли | — | Хэмминг < 10 — дубль |
| SSIM / PSNR | пиксельная близость | 57 % ≈ случай (DreamSim) | для серий бесполезны; только «неизменные зоны не тронуты» |

Согласованность ↔ разнообразие и следование брифу — компромисс: «A clear trade-off exists between consistency and diversity»
(ViStoryBench) [S9]; копия референса даёт CIDS к референсу 0,911 и CSD 0,735 при соответствии сюжету 0,91 из 4 — метрики
сходства без проверки брифа поощряют копирование [S9] `[исследование]`.

## 7. Тесты фазы 5 (метод; модели — у E)

| Тест | Что различает | Генераций, ₽ | Ценность |
|---|---|---|---|
| F-01 | 3 референса одной съёмки + роль + блок / только блок / мудборд из 8 + роль + блок; 3 сюжета | 9, 36 | 3 |
| F-02 | сетка 2×2 одной генерацией (2K) против трёх отдельных 1K (F-01 A) | 1, 7 | 3 |
| F-03 | референс-доминанта: полный / «Do not include…» / кроп | 6, 24 | 2 |
| F-06 | Recraft V4 Styles через RouterAI по трём референсам (`input_references`) против F-01 A | 1–3, 4,37–13,11 (RouterAI) | 2 |
| F-07 | форма (рендер) + материал-«кубик» → 3D-иконки; IoU силуэта ≥ 0,9 | 2, 8 | 3 |

[поправка фазы 5, 25.09.2026: прогнаны F-01 (36 ₽), F-02 (7 ₽), F-07 (8 ₽) — итоги в пунктах 2, 11–13, 22 выжимки; F-03 и F-06 не
запускались (отменено заказчиком); Recraft V4 Styles по своей иконке (CM-03) переносит палитру и вес, но не состав набора →
`99-raw/phase5/runs/5-vector/analysis/illustrations/metrics.md`]

Метод как постоянный фактор стенда E: «3 референса одной съёмки с ролью + дословный блок стиля + слот сюжета» (входы —
`99-raw/phase5/inputs/F/style_autumn_1..3.jpg`, блок — `examples/dna-warm-consumer.json` → `style_blocks.photo`).
Сведённые тесты отчётов: W4-1, W4-2, W1-2, W1-6, W2-10, V-5, W5-4 — в F-01…F-07; W4-7 → вариант промта у E; W1-3, W2-9 покрыты
F-01 (`99-raw/phase5/F-plan.md`).

## Частые ошибки

- Отдать модели 8–14 референсов «потому что лимит позволяет»; смешать фото и рисованные референсы в одном вызове.
- Мудборд вместо отбора: модель тащит море, плитку и интерьер из чужих кадров в парк.
- Бороться с деталью референса словами «no X» вместо кадрирования референса.
- Генерировать кадр серии из соседнего кадра (дрейф копится) вместо эталона.
- Считать seed механизмом стиля; переносить `--sref`, `style_id`, `sequential_image_generation` на модели без них.
- Принимать серию по ΔE и pHash без судьи смысла — или по близости DINO, которая награждает копию референса.
- **Ошибки нейросетей-агентов**: лимиты референсов «по памяти» (16 — это polza для GPT Image, у OpenAI лимит не назван);
  роль референса отдельным полем JSON (его нет ни у одного вендора); «character reference» Ideogram 3 или Omni Reference
  Midjourney (заменён Edit Model в V8.2) как доступные через polza; `input_fidelity` у GPT Image 2 (не принимает; RouterAI
  отвечает ошибкой `invalid_input_fidelity_model`).

## Чек-лист

- [ ] 1–3 референса одной съёмки и одного класса, роль — текстом по номеру, порядок входов зафиксирован?
- [ ] Блок стиля дословно первым абзацем; палитра — названием и hex с привязкой?
- [ ] Яркая деталь референса, которой не должно быть в серии, срезана кадрированием?
- [ ] Есть утверждённый эталон; все кадры — от эталона?
- [ ] Для персонажа или продукта — лист ракурсов одним референсом?
- [ ] Сетка 2×2 или `sequential_image_generation` рассмотрены для набора ≤ 4–5 кадров?
- [ ] Переписчик промта выключен или его текст залогирован?
- [ ] Серия проверена `series_metrics.py` (≤ 10°, ≤ 0,045) и бинарными вопросами судьи в двух прогонах?
- [ ] Есть сторож копирования (близость между разными сюжетами и к референсу)?

## Открытые вопросы и противоречия

- «Один вызов» (T2IS, сетка 2×2) против «по одному в чате» (Google) — различает F-02; в T2IS генерация 512 px и модели 2025.
- Роль `images` у GPT Image 2.5 в polza и передача `sequential_image_generation` Seedream — фаза 0 (B, T-тесты).
- Пропускает ли RouterAI passthrough `style_id` и `style_match` к Recraft (`provider.options`) — зонд в G-12, тест F-06.
- Пороги F/06 откалиброваны на 3–4 фото одной съёмки; для иллюстраций и 3D — нет; людьми ΔE и pHash серий не проверялись.
- CSD обучен на «стилях художников» — тонкие фирменные различия (одна палитра, разный свет и зерно) не калиброваны.
- Лимиты референсов расходятся: NB Pro «5 images with high fidelity» против «6 objects»; FLUX.2 8 / 10 / «8–10» на разных
  страницах BFL; Seedream 5.0 lite 14 (BytePlus) против 10 (polza); seed у Seedream 4 есть в polza, нет у BytePlus.
- ViStoryBench v5: числа приложения B расходятся с таблицей 2 — доверять таблицам.

## Источники

- [S1] OpenAI — Image generation, Image prompting guide, cookbook «image-gen-models-prompting-guide» (снимки 08.09.2026), https://developers.openai.com/api/docs/guides/image-generation — роли, «character anchor», дрейф при итерациях; официально, без чисел.
- [S2] Google — Gemini API image generation (снимок 23.09.2026), https://ai.google.dev/gemini-api/docs/image-generation + блоги Nano Banana Pro — лимиты по типам, роли, «one at a time»; внутренние противоречия (Lite).
- [S3] Black Forest Labs — FLUX.2 prompting guide, image editing, skills `flux-image-best-practices`, `flux-3-product-ads` v1.3.0, https://docs.bfl.ml/guides/prompting_guide_flux2 — синтаксис image N, 8 входов, апсемплинг, VLM-гейт пакета.
- [S4] BytePlus ModelArk — Seedream image generation tutorial (22.09.2026), prompt guide (06.07.2026), https://docs.byteplus.com/en/docs/ModelArk/1824121 — `sequential_image_generation`, лимиты.
- [S5] Alibaba Qwen — Qwen-Image-2.1 README (20.09.2026), https://github.com/QwenLM/Qwen-Image-2.1; Qwen-Image-Edit-2509 — 10 референсов, «1 to 3» оптимально, некоммерческие веса.
- [S6] Recraft — V4 Styles API и V4 Styles Creation Guide, https://www.recraft.ai/docs/v4-styles-creation-guide.md (август–сентябрь 2026) — `style_id`, precise/flexible, «Mixed references don't blend, they collide», тест 91,6 % (вендор).
- [S7] Ideogram — `ideogram-oss/ideogram-4` docs/prompting.md, API generate-v4, describe-v4 (03.06.2026) — стиль JSON-блоком, картинок-референсов в generate нет.
- [S8] Midjourney docs V8.2 — Style Reference, Seed, Edit Model (через r.jina.ai, 23.09.2026); практика Jamey Gannon (How I AI, chatprd.ai) — seed не хранит стиль; кроп доминанты.
- [S9] ViStoryBench, arXiv 2505.24862 v5 (CVPR 2026) + лидерборд vistorybench.github.io (23.09.2026) — согласованность серий, CIDS/CSD, trade-off, базовая линия копии.
- [S10] MultiBanana, arXiv 2511.22989 v2 (CVPR 2026) — число референсов → качество; модели 2025 года.
- [S11] T2IS «Why Settle for One?», arXiv 2506.23275 v2 — набор одним вызовом, consistency prompt, сетка 2×2 против 1×5.
- [S12] OmniRef-Bench / DyRef, arXiv 2606.26947 v1 (июнь 2026) — NB Pro и Seedream 4.5 по 5 типам референсов, утечка содержания.
- [S13] DreamBench++, arXiv 2406.16855 v2 (ICLR 2025) — устройство VLM-судьи, DINO/CLIP против людей.
- [S14] MICON-Bench, arXiv 2602.19497 v1 (23.02.2026) — бинарные чекпойнты, обрыв после 3 референсов.
- [S15] CSD «Measuring Style Similarity in Diffusion Models», arXiv 2404.01292 — стилевой эмбеддинг.
- [S16] DreamSim, arXiv 2306.09344 (NeurIPS 2023) — близость картинок, SSIM/PSNR ≈ случай.
- [S17] MultiRef-bench, arXiv 2508.06905 v3 (ACM MM 2025) — совместимость референсов, согласие VLM-судьи с людьми 0,43–0,66.
- Опыты: `99-raw/experiments/F/05-color`, `F/06-series-metrics`, `F/07-dna`, `F/08-icon3d-inputs`; задания `99-raw/phase5/jobs/F-01…F-07`.
- Ролики (`91-videos/digests/`): 2RD3FP5iWJY, AxV8TR3BdqI, I9xdmNZxIfA, hzPKb8bDvdY, oDok8FcX6rM, ttgNFJ25xfU, RIS8ckTfKAg, AO46uxbfpUU, 5dnNUB27HBQ, KLDdXOw6jIc, nBd9JJuAT1Y, bH2nP-aCFjk, 5T0yRNmNRi4.
