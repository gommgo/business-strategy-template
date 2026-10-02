# Видео-промты: image-to-video «только движение», камера, петли и FLF, темп и звук, таймкоды, язык, правка видео

Волна 2 · агенты D2 и D2b · 2026-09-23 · опора: 43 источника вендоров (выжимка помощника D2 `99-raw/notes/wave2/D2-helper-video.md`:
Google Vertex и Gemini API, Runway, Kling, BytePlus Seedance и скиллы `sd2-pe`/`sd25-pe`, Alibaba Wan и `wan3-pe`, MiniMax
`h3-prompt-writing`, BFL FLUX 3), 13 дайджестов роликов (`D2-helper-digests.md`, 362 цитаты сверены), `01-vendor-prompt-guides.md`
§3, §6–§11, §12.2, §12.8 · опыты: компилятор v2.1 (`99-raw/experiments/D2/01-compiler-v2`, тесты 98/98), примеры
`99-raw/experiments/D2/03-phase5-jobs/video_examples.txt` (19 промтов) · снимок каталога polza **2026-09-23 17:45** · все промты —
`[не проверено]` генерацией до фазы 5 (тесты D2-07, D2-08)

## Выжимка для агента

1. **Image-to-video — только движение**: кадр уже задаёт сцену, свет и внешность; пересказ видимого сбивает модель («Redundant
   prompts confuse the model», Vertex; «Reiterating elements… can lead to reduced motion», Runway; «redescribing visible pixels
   invites re-imagination», BFL). Видимое пиши только для нового элемента, превращения или взаимодействия. → §1.1
   `[документация]` `[консенсус 5 вендоров]` (тест D2-07) [поправка фазы 5, 25.09.2026: у Seedance 1.5 Pro пересказ сцены движение
   не снизил (1,69 против 1,61) и кадр не перерисовал (SSIM кадра 0 — 0,814 у всех плеч); «одно событие» — +52 % движения; правило
   держим ради краткости (463 против 796 символов), n = 2 → `99-raw/phase5/runs/3-prompt-form/README.md`]
2. **Что не названо — не движется**: перечисли движение каждого элемента фона глаголом (рябь, отражения, ветви, туман); без
   перечня фон стоит, а событие «съедает» фон [V:OA4xB5EY02g 32:46]; Kling: «photos are prone to generating static videos». →
   §1.2 `[практика]` `[документация]`
3. **Перечисли неподвижное** («the tree trunks and the far shore stay perfectly still») — якорь против дрейфа; один элемент не
   может быть и в движении, и в неподвижном (компилятор — ошибка). → §1.3 `[практика]` `[не проверено]`
4. **Неподвижную камеру пиши фразой диалекта**: Runway/Grok «Locked camera. The camera remains still.», Veo «The camera remains
   static.», Wan «Fixed camera.», H3 «The camera holds a static shot.», Kling «The camera remains fixed on the lake.», Seedance
   1.5 — плюс `fixed_lens: "true"` (это приписка к промту, «actual result is not guaranteed»). → §2.2 `[документация]`
5. **Для фона запрещай движение камеры явно**: при двух одинаковых кадрах камера сама пошла вверх [V:OA4xB5EY02g 33:47]; BFL:
   «Camera lock is advisory… still permits parallax and drift» → сцена должна терпеть лёгкий дрейф. → §2.2 `[практика]`
   `[документация]`
6. **Запреты движения — по классу семейства**: предложением у Seedance, Omni, Kling, Wan, Veo («No zoom. No spin. Do not
   reposition the subject.»); утвердительно у Runway, Grok, H3 («The focal length stays fixed. The subject keeps its orientation.
   The subject stays in the same place in the frame.») — Runway: «Negative phrasing… may produce… opposite results». → §1.4
   `[спорно]` (тест D2-08) [поправка фазы 5, 25.09.2026: у Grok 1.5 запреты предложениями работают — дрейф объекта 8,1 % против
   19,1 % ширины без них (−58 %), масштаб ±1,2 %; без запретов объект ушёл из кадра в 1 из 2; Seedance 1.5 Pro на ключе наезжает
   (площадь ×1,8–2,1 в 3 из 4) при любой форме промта (D2-11), n = 2 → `99-raw/phase5/runs/3-prompt-form/README.md`]
7. **Одна камера и одно главное действие на клип**; камера = крупность + движение + амплитуда + скорость, «amplitude and speed
   only when they are meaningful» (MiniMax); у Seedance 2.0 — «only 1 type of camera movement» на отрезок. → §2.1 `[консенсус]`
8. **Направление в кадре — явно** («drifts to the left»): без него Veo дал зеркальный кадр [V:g3w9wemFlmw 09:18]; «locked-on»
   у BFL — камера едет с субъектом, штатив — locked-off / static / fixed. → §2.3 `[практика]` `[документация]`
9. **Петля [A,A] — один кадр на входах «первый» и «последний»** у моделей с последним кадром в polza: Seedance 1.5 Pro, Kling v3
   (только одноплановый), Veo FLF, H3 Max (строка FL2VA), GA Omni (`first_frame_url` + `last_frame_url`); у Wan, HappyHorse,
   Grok — только первый кадр → i2v, петля — постобработкой (I); документируют петлю только Omni, Runway и BFL — у остальных
   [A,A] наш перенос (I-02…I-15). → §3.1 `[документация]` `[не проверено]` [поправка фазы 5, 25.09.2026: [A,A] замкнула только
   Seedance 1.5 Pro + `fixed_lens` (шов 1,28 на ряби); Kling 3 std — 2,12, GA Omni (поля `*_frame_url` принимают URL хранилища polza) —
   5,08, Kling 3 pro 1080p — почти стоп-кадр; Seedance 2.x — референсы, петли нет; FLF [A, B] у Seedance: кадр 0 = A, последний = B →
   `99-raw/phase5/runs/2.4-loops/`]
10. **В петле — только циклическое движение** (рябь, покачивание, дрейф, мерцание) + «The camera must start and end on the exact
    same frame to create a perfect loop.» (Runway); однонаправленное событие (улетел, вошёл, взорвался) с [A,A] несовместимо. →
    §3.2 `[документация]` `[вывод]`
11. **Переход A → B — путь, а не два состояния**: «The body should not repeat two static image descriptions; instead, it should
    supply the motion path that connects them» (MiniMax); этапы по порядку и неподвижная камера (BFL); кадры как можно ближе —
    далёкие дают склейку (Kling). → §3.3 `[документация]`
12. **Длительность — по размаху движения**: мелкое событие — 4 с, длинная панорама или превращение — 8 с [V:OA4xB5EY02g 08:06];
    для фона — минимальная допустимая ступень модели (цена посекундная). → §4.2 `[практика]`
13. **Темп — наречиями** (slowly, gently, slightly): «Current large video models are not sensitive to numbers» (Kling); для фона
    — «slow, gentle, coherent subtle movements» (Seedance 2.0). → §4.1 `[документация]`
14. **Звук выключай параметром там, где он есть** (`generate_audio` Seedance и Wan 3.0, `sound` Kling); у Veo, Omni, Wan
    2.5/2.6, HappyHorse, Grok, H3 Max параметра в polza нет → дорожку снимает кодирование (`-an`); словами — только уточнения:
    Wan без описанных реплик «adds them freely». → §4.3 `[проверено: каталог polza 17:45]` `[документация]`
15. **Таймкоды — только у семейств, которые их держат, и в их грамматике**: Veo `[00:00-00:02]`, Omni `[0-3s]`, Seedance 2.5
    `[0s-3s]` целыми секундами без разрывов, Wan `Shot 1 [0–3 s]`, Kling «At the 4th second», H3 `At 00:03.500`; каждый отрезок
    — законченное предложение. → §5.1 `[документация]`
16. **Один план — явно**: Omni режет сцену по умолчанию → «In a single continuous shot. No scene cuts.»; Wan — «Generate a
    single-shot video» (2.6 — ещё `multi_shots: "false"`); короткий промт Omni дробит 10 с на планы [V:5T0yRNmNRi4 12:19]. →
    §5.2 `[документация]`
17. **Мульти-шот Kling**: `shot n, m, words;` — 1–6 планов, ≥ 1 с, сумма = длительность, план ≤ 512 символов, только стартовый
    кадр; параметра `multi_shots` в polza нет. → §5.3 `[документация]` `[не проверено]`
18. **Язык описания — английский**; Veo — `enableTranslation: "false"` для английского промта; Omni: другие языки «not
    evaluated»; у H3 разделы по-английски, реплики и надписи — на исходном языке. → §6.1 `[документация]`
19. **Слова качества не добавляй** («cinematic, 4K, masterpiece»): против — MiniMax, Runway, BFL, скиллы `sd25-pe` и `wan3-pe`;
    за — только Seedance 2.0 (`sd2-pe` требует «4K HD, rich details») → `[спорно]`, плечо W3-13; вместо слов — видимые детали. →
    §7.1 `[спорно]`
20. **Мотивы движения на стартовом кадре** (смаз, поза в движении, направляющие линии) спорят с промтом — убери их правкой
    картинки до i2v (Runway FAQ). → §1.5 `[документация]`
21. **Продукт в видео**: надёжнее всего — свет, скользящий по неподвижному предмету; несколько оборотов и вращение двух тел
    ломаются (BFL); где модель берёт референсы — референсы товара вместо стартового кадра, типографику не переописывать
    [V:XLHTLJhzDyQ 05:05]. → §1.6 `[мнение вендора]` `[документация]` [поправка фазы 5, 25.09.2026: облёт ≈ 25° с лёгким наездом
    у Kling 3 std 5 с — надпись держится в 11 из 11 кадров, если в промте «the label text … stays sharp and unchanged» (SC-03, n = 1);
    у референсных Seedance 2.x первый кадр держит только фраза роли «Use @Image1 as the first frame.» (2 Fast: SSIM кадра 0 — 0,85;
    2 Mini без фразы — 0,60) → `99-raw/phase5/runs/SC-showcase/SC-03-frames/ocr.json`]
22. **Правка видео — одна точная цель короткой фразой + «Keep everything else the same»**; Omni держит 2–4 хода
    [V:5T0yRNmNRi4 10:15]; у Seedance 2.x и Wan 3.0 в промте обязателен глагол правки (edit, add, remove, replace, change to). →
    §8 `[документация]` `[спорно]`

## 1. Image-to-video: только движение

### 1.1 Что писать и чего не писать

| Писать | Не писать |
|---|---|
| движение камеры одним термином или «камера неподвижна» [S1][S8] | внешность, фон, свет, стиль — их задаёт кадр [S1][S9][S31] |
| действие субъекта общими словами: «the subject», «the product», «the woman» [S1][S8] | имена и признаки, которые видны («the tall man with black hair…») [S8] |
| движение каждого элемента фона (§1.2) | два движения камеры или «locked camera» + «tracking» (01 §12.2) |
| неподвижные элементы (§1.3) и запреты движения (§1.4) | «взрывные» действия в 4–5 с: «avoid high-burst, large-dynamic actions» [S20] |
| новое — только если появляется: новый объект, превращение, взаимодействие двух элементов [S9] | описание, далёкое от кадра: «may cause a camera cut or transition» [S18] |

- Формулы: Kling «Subject + Movement, Background + Movement» [S18]; Wan «Motion + Camera movement» [S25]; H3 I2VA —
  «first-frame anchor → action onset → continuous development → result or reaction» [S29].
- **Противоречие**: пример i2v в Gemini API пересказывает сцену заново (01 §3.3), практик пишет «описание всей сцены», но на
  деле перечисляет элементы с глаголом движения, внешность не повторяя [V:OA4xB5EY02g 30:43] → позиция базы: движение каждого
  элемента, без внешности. Проверка — D2-07 (Seedance 1.5 Pro, кадр `I:A`, 480p 4 с: «только движение» / пересказ / одно
  событие × 2 = 31,5 ₽; метрики I: SSIM неподвижных зон и «живость»).

```text
// bytedance/seedance-1.5-pro · 480p, 4 с, generate_audio "false", fixed_lens "true", images [A-lake-dawn.png] · polza 2026-09-23 · [не проверено: D2-07 a]
Locked camera. The camera remains still. Small ripples on the water spread slowly from the right shore. Reflections of the
trees shimmer gently on the water. Thin branches of the dry trees sway slightly in a light breeze. The thin mist over the
water drifts slowly to the left. The tree trunks and the far shore stay perfectly still. All movement is slow and gentle. One
continuous shot, same set and geometry, no cuts. No subtitles. No background music. No text.
```

Антипример (плечо D2-07 b, `compile.i2v=full`): тот же текст с пересказом «A calm lake at dawn with bare dry trees… Photograph,
nature photography… Misty blue grey dominates…» — 796 символов вместо 463; по вендорам — меньше движения и перерисовка кадра.

### 1.2 Перечень фонового движения

- Без перечня «it does not move… it's not lively»; назвал озеро — «it understand lake moves» [V:OA4xB5EY02g 32:46]; яркое событие
  забирает внимание: «it will sort of like only concentrate on the volcano, not so much of the foreground» [32:46–33:47].
- Синемаграф — движение только в названных частях: «Голова и ноги без движения. Танцует только попа и хвост» [V:_Bc4g6fFMp0
  08:09–09:10]; BFL: «Cinemagraph — A still frame with one small looping motion» [S32].
- Форма строки: `<элемент> <глагол движения> <наречие темпа> [<направление>]` — «the thin mist over the water drifts slowly to the
  left». 2–5 элементов; больше 5 — модель выбирает сама, ради чего двигать кадр `[мнение]`.
- Поле спецификации: `motion.background_motion[]` {element, motion} (схема v0.2); без перечня у `kind: loop | cinemagraph`
  компилятор предупреждает.

### 1.3 Неподвижное

- `motion.still[]` → «The tree trunks and the far shore stay perfectly still.» — перечисляй крупные формы, которые должны
  остаться на месте кадр в кадр (стволы, линия горизонта, предмет, логотип); для персонажа — неподвижные части тела
  [V:_Bc4g6fFMp0 09:10].
- Сверка результата — маска неподвижных зон: `video_loop_check.py drift <ролик> --mask <маска>` (I, `../../scripts/ai-media/README.md`).

### 1.4 Запреты движения

| Запрет (`motion.forbid`) | Предложение (Seedance, Omni, Kling, Wan, Veo) | Утвердительно (Runway, Grok, H3) |
|---|---|---|
| `zoom` | No zoom. | The focal length stays fixed. |
| `spin` | No spin. | The subject keeps its orientation. |
| `reposition_subject` | Do not reposition the subject. | The subject stays in the same place in the frame. |
| `camera_move` | Do not move the camera. | The camera remains completely still. |
| `cuts` | No cuts. | One continuous shot. |
| `shake` | No camera shake. | The image stays perfectly stable. |
| `morph` | Do not change the shape of the subject. | The subject keeps its exact shape and proportions. |
| `new_objects` | Do not add new objects. | Only the elements already in the frame appear. |
| `fast_motion` | No fast or sudden movement. | All movement is slow and gentle. |

- Первоисточник приёма — практика: «I explicitly tell it not to zoom, spin, or reposition the subject, it does understand the
  task» (Veo 3.1) [V:BVMuRw8BgJg 02:02–03:09]; дословный промт не зачитан — наша строка — реконструкция `[практика]`.
- Вендоры пишут запреты сами: Omni — «Do not do X», «No scene cuts» [S7]; Wan — «with no camera movement» [S25]; BFL — «no cuts,
  transitions, frozen or repeated frames, or resets» [S31]; Runway — против любых отрицаний [S8][S11]. Скиллы `sd25-pe` и
  `wan3-pe` запрещают **навешивать** непрошенные запреты («Do not add unrequested constraints») [S23][S28] → запрет — только
  тот, что лечит наблюдённый брак (для продукта на хромакее — `zoom`, `spin`, `reposition_subject`).
- Тест D2-08: Grok 1.5 480p 4 с, продукт на `#00B140` (`I:P`), с запретами против без × 2 = 25,92 ₽; критерий — масштаб и дрейф
  центра масс по маске ключа ниже ≥ 30 % (метрики I).

```text
// grok-imagine-video-1-5 · 480p, 4 с, images [P-velmora-on-00B140.png] · polza 2026-09-23 · [не проверено: D2-08]
Locked camera. The camera remains still. The product floats gently up and down. The flat green background stays perfectly
still. No zoom. No spin. Do not reposition the subject. One continuous shot, same set and geometry, no cuts.
```

### 1.5 Кадр, который мешает движению

- Runway FAQ: мотивы движения, «запечённые» в картинку («motion blur, mid-action elements and poses, or directional lines»),
  спорят с промтом — «consider using Text/Image to Image to remove or minimize cues before generating» [S9].
- Kling: «photos are prone to generating static videos» — фото без мотива движения требует явного перечня (§1.2) [S18].
- Для петли кадр — «спокойное состояние» сцены: без людей в движении, без летящих объектов, без смаза.

### 1.6 Продукт (`VID-I2V-PRODUCT`)

- «Anchor motion at its endpoints. A generated clip is trustworthy at its first and last frame and inventive in between.»;
  проваливается «multiple revolutions, and rotation of two bodies at once»; надёжная замена вращению — «light moving across a
  static object, which is the most reliable motion in the system and the one that consistently looks alive»; «When an object
  must arrive in frame, generate it leaving and reverse the clip» [S31] `[мнение вендора]`.
- Seedance 1.5 Pro: «…keeping the appearance, proportions, and materials… accurate and consistent, with no unnecessary elements
  added» [S19] (01 §6.2).
- Референсы товара вместо стартового кадра: «instead of using a start image, we upload the same clean white studio references»;
  «keep the product identity consistent without redefining typography or altering branding» [V:XLHTLJhzDyQ 04:05–05:05]; в
  polza — Veo 3.1 Fast `REFERENCE_2_VIDEO` (≤ 3 картинки, 45 ₽; тест I-19), Omni `images` (≤ 7), Seedance 2.x `images`.
  Промт продукта из 7 блоков — `05-edit-reference-series.md` §5.

## 2. Камера

### 2.1 Грамматика камеры по семействам

| Семейство | Формула | Дословно у вендора |
|---|---|---|
| Veo / Vertex [S1][S5] | один термин крупности + одно движение; «Evolution (subtle for short clips)»; словарь — 01 §3.2 | «Slow dolly in on the subject.» |
| Runway [S9][S10] | «The camera [motion] as the subject [action]»; порядок в промте не важен [S12] | «The locked-off camera remains perfectly still.» |
| BFL FLUX 3 [S32] | «one framing term, one movement term, and one clear subject action» | «Usually start with the subject and action, then add framing, movement, and style» |
| MiniMax H3 [S29] | тип + амплитуда + скорость естественной фразой, не ярлыками в конце | «The camera pushes in with small amplitude at slow speed toward the folded letter in her hands.» |
| Seedance 1.5 [S19] | стартовая композиция + движение + амплитуда + конечная композиция; «Subject + Shot Size» | «Close-up of the man on the left» |
| Seedance 2.5 [S21][S23] | движение + цель + старт + направление + финиш; редкий термин — «[term + descriptive explanation]» | фокус, диафрагма и выдержка «cannot replace the final visible result» |
| Wan [S25] | смысл: push-in — близость, pull-out — масштаб, tracking — рядом, orbit — значимость (дуга < 45°), fixed — покой | «Use a camera pull-out to reveal» |
| Kling [S16] | простым языком, «names what the viewer will see» | «The camera slowly pushes toward the subject.» |

- Kling: 6 базовых движений и 4 «Master Shots» — ползунки интерфейса, не текст промта [S18].
- Термины оптики и носителя (35mm, anamorphic) — ярлыки стиля; «detailed camera specs may be interpreted loosely» (OpenAI,
  01 §12.8); у Seedance 2.5 значения объектива только дополняют видимый результат [S23].

### 2.2 Неподвижная камера: фразы и параметры

| Семейство polza | Фраза (компилятор, `dialects.yaml` → `camera.static`) | Параметр |
|---|---|---|
| Seedance 1.5 Pro | Locked camera. The camera remains still. | `fixed_lens: "true"` — «ModelArk will append the fixed camera instruction… actual result is not guaranteed», не с референсами [S22] |
| Veo 3.1 / Fast | The camera remains static. | Vertex `cameraControl: fixed` (только с картинкой) — в polza нет [S4] |
| Omni (preview, GA) | The camera stays locked. | — |
| Kling v3 | The camera remains fixed on {target} (`motion.camera.target`, иначе «the subject») | — |
| Wan, HappyHorse | Fixed camera. | — |
| H3 Max | The camera holds a static shot. | — (Hailuo 2.3: команда `[Static shot]`) |
| Grok Video 1.5, Runway | Locked camera. The camera remains still. | — |

- «The camera is entirely motionless for the duration of the scene, with movement only occurring from the subject» — Runway [S10];
  статичный широкий план модели даётся трудно: «Video models are designed to create immersive, high-fidelity motion» [S10].
- BFL: «Locked and deliberate by default; move only when it serves the event», но «Camera lock is advisory. "Locked camera, no
  push-in, no pan, no zoom" still permits parallax and drift. Design shots that tolerate a little movement» [S31] → для петли
  кадр без жёстких линий у края (дрейф 1–2 px на них виден), приёмка — `cam_shift_max_px` (I).

### 2.3 Направление и ловушки терминов

- Направление в кадре пиши словами: «drifts to the left», «enters from the right edge»; «I didn't really give it screen
  direction» → кадр вышел зеркальным [V:g3w9wemFlmw 09:18].
- **Locked-on** (BFL) — «Rig fixes the subject steady while the background blurs»: камера едет вместе с субъектом; для штатива —
  locked-off / static / fixed [S32]. **Zoom** ≠ **dolly**: «This is different from a dolly, as the camera itself doesn't move»
  [S1]. **Truck** — сдвиг вбок, **pan** — поворот на месте [S1].
- Полезные для веба термины BFL: Cinemagraph (одно малое петлевое движение), Boomerang (вперёд и назад), Tableau (статичный
  симметричный общий план) [S32].

## 3. Петли и первый + последний кадр (FLF)

Протоколы петли (шов, срез дубля, круговой стык, кодирование) — агент I: `../09-video-pipeline/01-seamless-loops.md`,
`04-i2v-protocols.md`, утилита `video_loop_check.py`. Здесь — только вход и текст промта.

### 3.1 Кто принимает последний кадр в polza (снимок 23.09.2026 17:45)

| Модель polza | Как передать кадры | Петля у вендора | Цена минимального ролика |
|---|---|---|---|
| `bytedance/seedance-1.5-pro` | `images: [A, A]` | не документирована | 5,25 ₽ (480p, 4 с, без звука) |
| `kling/v3` | `images: [A, A]` — только одноплановый («start frame (multi-shot)») | не документирована; далёкие кадры «may cause a lens switch» [S18] | 30 ₽ (std, 3 с) |
| `google/veo3_fast`, `google/veo3` | `generationType: FIRST_AND_LAST_FRAMES_2_VIDEO` + `images` | не документирована | 45 / 187,5 ₽ (8 с, 720p) |
| `minimax/hailuo-3-max` | `images: [A, A]` + строка FL2VA (§5.1) | не документирована; «FL2VA generally favors a single shot» [S29] | 47,30 ₽ (480p, 5 с) |
| `google/gemini-omni-1.1-flash` (GA, с 27.08.2026) | `first_frame_url` + `last_frame_url` — **URL**: `polza.py` загружает только `images`, `videos`, `mask_url` → сначала `polza.py upload <файл> --live` | документирована: одна картинка на двух концах — «creating a video that loops» [S7] | 48 ₽ (4 с; 360p = 720p = 1080p) |
| `gemini-omni-video` (preview, снимается 30.09.2026) | `images` + теги `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image1]` | та же; дойдут ли теги через KIE — `[не проверено]` | 35 ₽ (4 с, 720p) |
| `bytedance/seedance-2`, `-2-fast`, `-2-mini`, `-2-5` | `images` — «референсные»; роли кадров словами (§3.3) | — | Mini 2,565 ₽/с (480p) |
| `wan/2.5`, `wan/2.6`, `alibaba/wan-3.0*`, `alibaba/happyhorse-*`, `grok-imagine-video-1-5` | только первый кадр (`images` ≤ 1; у Grok FLF — только в API xAI) → i2v, петля — постобработкой (I) | — | Grok 1,62 ₽/с (480p); Wan 2.5 — 45 ₽ (720p, 5 с) |

- GA Omni: `last_frame_url` — «Только вместе с first_frame_url»; `first_frame_url` «не сочетается с images, videos, audio_ids
  и character_ids» (каталог) — референсы и кадры в одном вызове нельзя. Компилятор кладёт кадры в поля и помечает задание
  `meta.url_fields` + `meta.prepare`; тег `[# Sources…]` для GA не пишется (он — синтаксис preview).
- GA Omni у компилятора: при запросе 480p берётся 720p (та же цена), а не ближайшая 360p (`video_examples.txt` §1).

### 3.2 Текст петли

- Только циклическое или возвратное движение: рябь, покачивание, дрейф тумана, мерцание света; однонаправленное событие
  («UFO comes in», «the balloon drifts away») с [A,A] несовместимо — модели придётся вернуть объект или оборвать движение
  (коллапс в статику или склейка) `[вывод]` `[не проверено]`.
- Фраза петли Runway — «The camera must start and end on the exact same frame to create a perfect loop.» [S9]; у Omni preview —
  закрывающая «Use this image as the first frame and the last frame.» [S7]; BFL — «a loop that must return to where it began»
  [S32]. У остальных семейств фраза — наш перенос `[не проверено]`.
- Камера — неподвижная (§2.2), темп — медленный (§4.1), звук — выключен (§4.3), один план (§5.2).

```text
// minimax/hailuo-3-max · 480p, 5 с, images [A-lake-dawn.png, A-lake-dawn.png] · IR (скилл h3-prompt-writing) · polza 2026-09-23 · [не проверено]
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 5.00-second mark of the target video.
integrated_multimodal_description: [Shot 1] The camera holds a static shot. Small ripples on the water spread slowly from the right shore. Reflections of the trees shimmer gently on the water. Thin branches of the dry trees sway slightly in a light breeze. The thin mist over the water drifts slowly to the left. The tree trunks and the far shore stay perfectly still. All movement is slow and gentle. One continuous shot, same set and geometry, no cuts. The camera must start and end on the exact same frame to create a perfect loop.
overall_soundscape: N/A
non_diegetic_music: N/A
```

### 3.3 Переход A → B

- MiniMax FL2VA: «first-frame state → observable intermediate changes → progressively narrowing differences → last-frame state»;
  «The body should not repeat two static image descriptions» [S29].
- BFL keyframes: «describe the stages of the change in order and hold the camera still»; промежуточный кадр — «a deadline; say
  what the remaining seconds are for… Pin only what matters; extra anchors stiffen motion» [S31].
- Seedance 2.5 (`sd25-pe`): роли кадров — отдельными предложениями «Use @Image1 as the first frame.» / «Use @Image2 as the last
  frame.», не ослаблять до «reference»; кадры одного соотношения сторон; «Keyframes control stage order and visible states; they
  do not promise frame-by-frame replication» [S23]. В polza у Seedance 2.x `images` — «референсы» (тест B-6 фазы 0).
- Kling O1: «Take [@Image1] as the start frame, take [@Image2] as the end frame, [describe the changes…]»; «Generation with only
  an end frame is not supported» [S17]. Omni: «Provide two images… and describe the desired transition» [S7].
- Длительность перехода — по размаху: «if 4 seconds you'll be like all of a sudden… for a very long panning, zooming… I'll use a
  longer seconds» [V:OA4xB5EY02g 08:06]; эффект конечного кадра можно не расписывать — «Let it figure out» [42:57].

```text
// bytedance/seedance-1.5-pro · 480p, 4 с, images [A-lake-dawn.png, B-lake-sunrise.png] · шаблон базы · polza 2026-09-23 · [не проверено: I-05]
Locked camera. The mist over the water thins gradually as the sun rises behind the far trees; the light on the water warms
and a golden path slowly widens across the ripples; the ripples keep moving the whole time. The tree trunks and the far shore
stay perfectly still. All movement is slow and gentle. One continuous shot, same set and geometry, no cuts.
```

## 4. Темп, длительность, звук

### 4.1 Темп и амплитуда

- Наречия степени: «Use degree adverbs effectively» (Seedance 1.5), «quickly» / «slowly» (Wan i2v), «swaying violently» /
  «moving slowly» (Wan Advanced) [S19][S25]; Kling — «not sensitive to numbers» [S18]; BFL — качества движения «Slow, abrupt,
  weightless, chaotic, precise» [S32]; Vertex — «Evolution (subtle for short clips)» [S1].
- Для фона сайта — «slow and gentle» и малая амплитуда: Seedance 2.0 «Prioritize slow, gentle, coherent subtle movements» [S20];
  быстрое движение фона отвлекает от текста и увеличивает вес ролика (кодирование — I, `03-encoding-and-budgets.md`).
- Компилятор: `motion.tempo` → «All movement is slow and gentle.» / «Movement is steady and natural.» / «Movement is quick and
  energetic.»; амплитуда и скорость камеры — `motion.camera.amplitude|speed`.

### 4.2 Длительность

| Модель polza | Допустимо | Для фона-петли | Для сюжета |
|---|---|---|---|
| Seedance 1.5 Pro | 4 / 8 / 12 с | 4 с (5,25 ₽ при 480p) | 8 с |
| Kling v3 / v2.6 | 3–15 с / 5, 10 с | 3–5 с | 5–10 с; мульти-шот — сумма планов |
| Veo 3.1 / Fast | 8 с (параметра нет) | 8 с | 8 с; продление — операция `extend` |
| Omni preview / GA | 4 / 6 / 8 / 10 с | 4 с | 6–10 с |
| H3 Max | 5–15 с | 5 с | 5–10 с |
| Wan 2.5 / 2.6 / 3.0 | 5, 10 / 5, 10, 15 / 2–30 с | 5 / 5 / 2–4 с | 5–10 с; Wan 3.0 — 4–6 с на план [S26] |
| Grok Video 1.5 | 1–15 с (по умолчанию 8) | 4 с | 6–8 с |
| Seedance 2 / 2.5 | 4–15 / 4–30 с (по умолчанию 15 / 5 — задавать явно) | 4 с | 5–10 с |

- «duration is a tempo control, not a length estimate» (BFL product-ads) [S31]: то же движение за 8 с медленнее, чем за 4 с.
- Таймкоды отмеряют время на действие: «setting timestamps 00:00 through 00:00.5 wouldn't give enough time» (Runway) [S12];
  «секунды сильнее всего ограничивают» [V:5T0yRNmNRi4 13:21].

### 4.3 Звук

| Модель polza | По умолчанию | Выключить | Если параметра нет |
|---|---|---|---|
| Seedance 1.5 Pro | `false` в polza (у вендора `true`, «automatically generates background music» [S19]) | `generate_audio: "false"` | — |
| Seedance 2 / Fast / Mini / 2.5 | `"true"` | `generate_audio: "false"` | — |
| Kling v3, v2.6 | `"false"` (вендор: «Default to off» [S15]) | `sound: "false"` | — |
| Wan 3.0 / Prime | `"false"` в polza (вендор: «Enabled by default» [S26]) | `generate_audio: "false"` | — |
| Wan 2.5 / 2.6, HappyHorse | звук всегда: «Only wan2.2 and wan2.1 series models support silent video generation» [S27] | нет | `-an`; «No dialogue. No background music.» — без реплик в промте модель «adds them freely» [S25] |
| Veo 3.1 / Fast | всегда (Gemini API: «Always on» [S6]) | нет (в Vertex — `generateAudio` [S3]) | `-an` |
| Omni preview / GA | модель подбирает дорожку [S7] | нет | `-an`; «No dialogue. No extra sound effects.» |
| Grok Video 1.5 | включён (xAI) | нет в polza | `-an` |
| H3 Max | 32 кГц стерео [S29] | нет | `-an`; `overall_soundscape: N/A` — «only when the user explicitly requests complete silence» |

- Компилятор ставит параметр звука явно (`false`), а для моделей без параметра предупреждает «снимать при кодировании (`-an`)».
- `sd25-pe`: «Do not write aspect ratio, total duration, resolution, frame rate, or the sound toggle into the Prompt» [S23] —
  выключатель звука — параметром, а не словами.

## 5. Таймкоды и мульти-шот

### 5.1 Грамматика по семействам (шаблоны `dialects.yaml` → `video`)

| Семейство | Таймкод | Мульти-шот | Источник |
|---|---|---|---|
| Veo | `[00:00-00:02] steam starts to rise.` | одна сцена на клип | [S5] |
| Omni | `[0-3s] …`, «After 3 seconds, a woman enters the scene.» | `[0-4s] … [4-10s] …`; «Every 2s cut to a new frame» | [S7] |
| Seedance 2.5 | `[0s-3s] …`, «At the 2-second mark…»; единица 1 с, **без разрывов** | `[0s-4s] Shot 1: …` | [S21][S23] |
| Seedance 2.0 | нет: «precise timing… is unstable» (скилл `sd2-pe` сам пишет «0–3s, 3–10s») `[спорно]` | «Shot 1 / Shot 2 / Shot 3» | [S20][S24] |
| Seedance 1.5 | нет | «Shot 1: … Shot 2: Cut to …» | [S19] |
| Wan 2.6 / 3.0 | `Shot 1 [0–3 s] …` (пример вендора — с разрывами 0–3, 4–6, 7–10) | то же; 2.6 — `multi_shots: "true"` | [S25][S27] |
| Kling 3.0 | «At the 4th second, …» | `shot 1, 4, wide shot, …; shot 2, 6, close-up, …;` | [S14][S15] |
| H3 Max | «At 00:03.500, …»; **у первого плана без времени** | `[Shot 2] At 00:03.500, the camera cuts to …` | [S29] |
| Runway (вне polza) | `[00:01] X occurs. [00:03] Y occurs.` + обычная проза | API: 3–5 планов, сумма = длительность | [S9][S12] |

- Первая строка H3 при кадрах: I2VA — `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is
  fully referenced.`; FL2VA — `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the
  0.00-second mark… Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.` (S.SS — два знака) [S29].
- `sd25-pe`: отрезки — «event budgets, not frame-level edit points. Do not claim precision to 0.5 seconds»; если длительность
  задана только параметром — этапы «At the start / Main event / At the end» без чисел [S23]. Компилятор предупреждает о дробных
  границах и разрывах у Seedance 2.5.
- Каждый отрезок и план — законченное предложение с точкой (компилятор v2.1; у v2 отрезки сливались: «…cup [00:02-00:04] the…»).

### 5.2 Один план

| Модель | Как удержать один план |
|---|---|
| Omni | «In a single continuous shot. No scene cuts.» — по умолчанию режет [S7]; короткий промт дробит 10 с [V:5T0yRNmNRi4 12:19] |
| Wan 2.6 | `multi_shots: "false"` + «Generate a single-shot video» (API 2.7 [S27]; гайд: «Generate single shot.» [S25]) |
| Kling v3 | у вендора `multi_shot` по умолчанию `true` [S15]; в polza параметра нет, но описание `sound` — «Обязательно true при multi_shots=true» → у провайдера, вероятно, `false` `[вывод]`; в тексте — «one continuous shot» |
| остальные | «One continuous shot, same set and geometry, no cuts.» (контракт непрерывности BFL [S31]) |

### 5.3 Мульти-шот

- Kling API: «shot n, m, words;» — n = 1–6, m ≥ 1 с, сумма = длительность, words ≤ 512 символов [S15]; в мульти-шоте — только
  стартовый кадр (каталог polza); компилятор проверяет все три условия.
- Склейка должна нести новое: «A cut should introduce new information… If only the distance or a slight angle needs to change,
  prefer camera motion» (MiniMax) [S29]; «Consecutive shots must contrast hard (scale, location, color) or the cut blends into
  a continuous take» (BFL) [S32].
- Для сайта мульти-шот — только `VID-LONG` (сторителлинг); фон и петля — один план. Длинное — «stages», одно крупное изменение на
  этап (`sd25-pe`) [S23]; Wan 3.0 — 4–6 с на план [S26].

## 6. Язык, переписчики, длина

### 6.1 Язык

- Описание — по-английски: Veo «English (EN) is fully supported, but other languages have not been evaluated» [S6]; Omni — то
  же [S7]; в polza у Veo `enableTranslation` по умолчанию `"true"` → компилятор ставит `"false"` для английского (термины камеры
  не переводятся дважды), для кириллицы в промте — `"true"` с предупреждением.
- Реплики и надписи — на исходном языке у H3 («preserve dialogue, lyrics, and visible scene text in their original language»)
  [S29]; Kling переводит реплики вне 5 языков на английский (01 §8); Seedance 2.5 понимает ещё 9 языков промта [S21]. Для
  сайтов реплик нет — русский текст в видео не рисуем, он в HTML поверх (01 §12.7).

### 6.2 Переписчики до модели

| Модель | Переписчик | В polza |
|---|---|---|
| Veo 3.x | LLM-переписчик; Vertex `enhancePrompt` по умолчанию `true` («providing a seed won't guarantee consistent results») [S3] | не управляется → форма промта до генератора доходит частично |
| H3 Max | API: `prompt_expansion_mode` по умолчанию `balanced`; обёртка Runway: «disabled keeps the prompt as written» [S30] | параметра нет — IR может переписываться `[не проверено]` |
| Wan 2.5 | `enable_prompt_expansion` (у вендора `prompt_extend=true`) | компилятор ставит `"false"` |
| Seedance 2.0 / 2.5, Wan 3.0 | скиллы-переписчики `sd2-pe`, `sd25-pe`, `wan3-pe` (вне API; ставятся `npx skills add …`) [S23][S24][S28] | не запускаем (сеть, `npx`); их шаблоны — эталон диалекта |

- `wan3-pe`: «formats and clarifies the user's own instructions only, without enriching the story»; `sd2-pe` — интерактивный
  («No silent modification»); `sd25-pe` — «One Best Version», «Template First» [S23][S24][S28].

### 6.3 Лимиты длины (меньшее из каталога и документации)

| Модель | Лимит | Следствие |
|---|---|---|
| Wan 2.5 | 800 символов (+ `negative_prompt` ≤ 500) | петля с перечнем фона — только «движение»; пересказ сцены не влезет |
| Kling v3 | 2 500 (API — 3 072), план ≤ 512 | — |
| Seedance 1.5 Pro | 2 500 | — |
| Seedance 2 / Fast | 1 536 (документация) при 20 000 в каталоге | компилятор берёт 1 536 |
| Veo 3.1 | 2 000 (документация polza) при 60 000 в каталоге; Gemini API — 1 024 токена | компилятор берёт 2 000 |
| Grok Video 1.5 · H3 Max · Omni | 4 096 · нет в каталоге (API — 7 000) · 20 000 | — |

## 7. Слова качества, стиль, пометки на кадре

### 7.1 Позиции вендоров

| Против | За |
|---|---|
| MiniMax: «Prefer concrete visual and audio details over abstract words like "cinematic" or "beautiful"» [S29] | Seedance 2.0: «Image quality… HD, rich details, cinematic texture, natural colors» [S20] |
| Runway: «Words like "beautiful," "professional"… mean different things to different people» [S11] | `sd2-pe`: «Mandatory fallback… anti-distortion and high image quality constraints» («4K HD, rich details») [S24] |
| BFL: «"Vintage," "nostalgic," and "retro" are adjectives: nothing in the output can confirm or refute them» [S31] | Vertex: «shot on 8K camera», «cinematic film look» в словаре стилей [S1] |
| `sd25-pe`, `wan3-pe`: «Do not automatically add quality packs» [S23][S28] | примеры Kling: «8K detail, masterpiece cinematography» [S16] |
| практик: «cinematic, beautiful, high quality, 4K, masterpiece… you're not really going to get much» [V:WmC1nqz10Qk 00:00] | практик: «to make it a bit more nice… cinematic and 35 mm grain» [V:I9xdmNZxIfA 04:21] |

- Позиция базы: по умолчанию не добавлять (компилятор — предупреждение `quality_words`); у Seedance 2.0 — `[спорно]`
  (`dialects.yaml` → `seedance-2.quality_vendor`); плечо A/B — `compile.quality_words` (W3-13: Grok 480p, ≈ 19 ₽, описан в
  `99-raw/phase5/D2-plan.md`, не собран).

### 7.2 Что писать вместо

- Видимое вместо оценки: «a sunset with vibrant orange and pink clouds over the ocean», а не «a beautiful sunset» [S11];
  «swirling blue energy particles with an ethereal glow» вместо «magic» [S16].
- «Эпоха» — названием носителя: «A period look is requested by naming the machine that recorded it, not the feeling it should
  produce» (Super 8, VHS, 16mm, Hi8); «Name the degradation, not only the format» [S31].
- Антислоп: «A sharp anamorphic lens flare is one of the strongest signals of a modern synthetic image, and models reach for it
  by default» [S31] — блики и «кинематографичный» туман не просить.

### 7.3 Пометки на первом кадре (Veo)

- Приём Google Labs: стрелки и подписи на стартовом кадре + «follow the instructions on the image or something to that effect» —
  модель выполняет и «dissolve out the text»; цена — первые секунды ролика [V:g3w9wemFlmw 14:25–15:28]; Luma Ray3 — пометки
  на кадре штатно (01 §11.2). Для петель и фона не годится (кадр 0 испорчен). Компилятор: `motion.frame_annotations: true`.

## 8. Правка видео (v2v)

- **Omni** (preview 70 ₽, GA 126 ₽ за вход с видео; вход ≤ 10 с): «Simple prompts work best for video editing. Overly descriptive
  prompts can lead to unintended changes» + «Keep everything else the same» [S7]; команда Omni: «if you under specify what your
  edit is, the model will do more than you thought»; «2, 3, 4 turns pretty reliably» [V:5T0yRNmNRi4 10:15–11:16]; «Voice editing
  is not supported» [S7] → одна точная цель на ход одним предложением (что, где, во что) + закрывающая фраза; ≤ 3 хода, дальше —
  от исходника `[спорно]`.
- **Seedance 2.x / 2.5, Wan 3.0**: обязателен глагол правки — «Include at least one editing trigger… edit video, add, insert,
  remove, delete, modify, replace, change to» [S21][S26]; «Parts not mentioned remain unchanged by default» [S20]; шаблоны:
  «Remove [Element] from [Video N], keeping the rest of the video content unchanged.», «Replace [element] in [Video N] with
  [new element].» [S20]; «<Video_N>» напрямую, без «reference» [S20]; закрытие области дословно (`sd25-pe`): «Except for the
  objects explicitly modified above, all other visible characters, props, and background elements in @Video1 remain unchanged
  and are not to be replaced or removed.» [S23]; сложное — «Break the complex task into several simpler tasks» [S21].
- **BFL Video Edit** (вне polza): «An edit prompt describes a change, not a shot… the shortest prompt that names the change is
  usually the right one»; второй проход — от результата первого, «rather than combining both instructions» [S32].
- **Kling O1 / 3.0 Omni** (вне polza): «Remove [...] from [@Video]», «Change [@Video] to [...] style», «Change the background in
  [@Video] to a green screen, and keep [...]» [S17].
- Задания I-17 / I-20 (Omni V2V «сумерки») — у I; форма — эта.

```text
// google/gemini-omni-1.1-flash · videos [loop-A.mp4 ≤ 10 с] · правка V2V 126 ₽ · polza 2026-09-23 · [не проверено: I-20]
Change the light to late dusk: a deep blue sky with the last warm glow above the far trees, the water reflecting it. Keep
everything else the same.
```

## 9. Компилятор

Поля `motion` схемы v0.2 (`start_frame`, `end_frame`, `loop`, `camera.{move, amplitude, speed, target}`, `background_motion`,
`still`, `forbid`, `tempo`, `timeline`, `shots`, `audio`, `frame_annotations`) и опции плеч A/B (`compile.i2v`,
`compile.forbid_style`, `compile.quality_words`) дают фразы §1–§5; описание — `../../scripts/ai-media/README.md` (раздел D2).

```bash
# prompt_compile.py 2.1 · polza 2026-09-23 17:45 — [проверено]
P=99-raw/tools/venv-D2/bin/python; C=../../scripts/ai-media/prompt_compile.py
$P $C compile 99-raw/phase5/inputs/D2/briefs/V1.spec.json --model bytedance/seedance-1.5-pro          # i2v «только движение»
$P $C compile 99-raw/phase5/inputs/D2/briefs/V1.spec.json --model bytedance/seedance-1.5-pro --opt i2v=full
$P $C compile 99-raw/phase5/inputs/D2/briefs/V2.spec.json --model grok-imagine-video-1-5 --opt forbid_style=sentence
(cd 99-raw/experiments/D2/03-phase5-jobs && ../../../tools/venv-D2/bin/python video_examples.py)     # 19 примеров
```

## Частые ошибки

- Пересказывать стартовый кадр в i2v («A calm lake at dawn with bare trees…») — модель перерисовывает кадр и движется меньше.
- Назвать одно событие и ждать «живой» фон — всё, что не названо, стоит; или наоборот, 8 движений сразу — модель выберет сама.
- Писать «No camera movement. The camera doesn't move.» для Runway или Grok — отрицание «may produce… opposite results»; для
  них — «Locked camera. The camera remains still.»
- Путать locked-on (камера едет с субъектом) и locked-off (штатив); zoom и dolly; pan и truck.
- Давать [A,A] модели без последнего кадра (Wan 2.5/2.6/3.0, HappyHorse, Grok): второй кадр — ошибка 400 или игнор; петля —
  постобработкой (I).
- Отправлять GA Omni кадры в `images` или тегами preview: у GA — `first_frame_url`/`last_frame_url`, и это URL (`polza.py
  upload` до запуска); `first_frame_url` не сочетается с `images`.
- Вкладывать однонаправленное событие в петлю [A,A] («the balloon drifts away»).
- Писать таймкоды модели, которая их не держит (Seedance 1.5, 2.0), или с разрывами у Seedance 2.5; ставить время первому плану
  H3.
- Надеяться на «No music» у Veo, Omni, Wan 2.5/2.6, Grok, H3 — звук в polza не выключается, дорожку снимает кодирование.
- Доверять `fixed_lens` / «locked camera» как гарантии: «not guaranteed», «advisory» — приёмка по `cam_shift_max_px` (I).
- Стопка «cinematic, 4K, masterpiece» по памяти из картиночных промтов; «warm», «vintage» вместо источника света и носителя.
- Ошибки агентов: брать Kling `multi_shots`, Veo `duration`, `negative_prompt` у всех Wan «по памяти» — в polza их нет (кроме
  `negative_prompt` у `wan/2.5` и `multi_shots` у `wan/2.6`); считать `gemini-omni-video` актуальной после 30.09.2026.

## Чек-лист

- [ ] Режим определён: t2v / i2v / FLF / ref2v / v2v, и модель в polza принимает нужные входы (§3.1)?
- [ ] В i2v нет пересказа видимого; есть движение камеры (или неподвижность), действие субъекта и перечень фона?
- [ ] Перечислено неподвижное; ни один элемент не движется и не стоит одновременно?
- [ ] Фраза неподвижной камеры — из диалекта семейства; у Seedance 1.5 ещё `fixed_lens: "true"`?
- [ ] Запреты движения — в форме семейства и только те, что лечат наблюдённый брак?
- [ ] Одно движение камеры и одно главное действие; направление в кадре названо словами?
- [ ] Петля: один кадр на двух концах, движение циклическое, фраза петли, камера неподвижна, один план?
- [ ] Переход A → B описан как путь (этапы), а не как два состояния; кадры близки?
- [ ] Длительность — по размаху движения и минимальной ступени модели; темп — наречиями?
- [ ] Звук выключен параметром; для моделей без параметра — `-an` в плане кодирования?
- [ ] Таймкоды — только у семейств, которые их держат, в их грамматике, законченными предложениями?
- [ ] Один план удержан явно (Omni, Wan); мульти-шот Kling — ≤ 6 планов, ≤ 512 символов, только стартовый кадр?
- [ ] Промт по-английски; у Veo `enableTranslation: "false"`; длина — в лимите модели (Wan 2.5 — 800)?
- [ ] Нет слов качества и оценочных прилагательных; стиль — видимыми признаками и носителем?
- [ ] Правка видео: одна цель + «Keep everything else the same» (Omni) или глагол правки + закрытие области (Seedance, Wan)?

## Открытые вопросы и противоречия

1. **«Только движение» против пересказа** — консенсус Vertex, Runway, BFL, Wan, Kling против примера Gemini API и практика
   Rames; решает D2-07 (31,5 ₽).
2. **Запреты предложением против утвердительной формы** — Runway против отрицаний, Omni/Seedance пишут их сами, практик Veo
   хвалит запреты; D2-08 (Grok) меряет только одну модель.
3. **Петля [A,A] у Seedance, Kling, Veo, H3** не документирована вендорами; Kling предупреждает о склейке при разных кадрах —
   тесты I-02…I-15 (I).
4. **Kling multi-shot по умолчанию** у провайдера — вывод из описания `sound`, не проверено; при мульти-шоте звук обязателен →
   цена выше (фаза 0, кандидат в T-блок).
5. **Слова качества** — ByteDance противоречит сам себе (`sd2-pe` против `sd25-pe`); W3-13 не собран.
6. **Таймкоды Seedance 2.0** — гайд против собственного скилла; у Wan пример вендора с разрывами при запрете разрывов у Seedance
   2.5 — общий шаблон «без разрывов» не вендорский для Wan.
7. **Переписчики Veo и H3 Max в polza** не управляются — что доходит до генератора, неизвестно; форма промта у них — `[спорно]`.
8. **GA Omni**: принимает ли `first_frame_url` URL хранилища polza, data:URI или объект — T-блок фазы 0 (кандидат T9, I2);
   работает ли одиночный `first_frame_url` (i2v) — не проверено.
9. **Правка видео Omni**: документация «проще» против команды Omni «подробнее» — позиция базы «одна точная цель короткой фразой»
   `[спорно]`.
10. Лимит промта Omni (Gemini API), FLUX 3, Wan 2.7 i2v и выключатель звука H3 — не найдены (помощник D2, §10).

## Источники

Документация — прочитана помощником D2 целиком или по разделам 23.09.2026, кэш `99-raw/cache/` (файлы — в
`99-raw/notes/wave2/D2-helper-video.md` §0); цитаты сверены там же.

- [S1] Google Cloud — Vertex AI «Video generation prompt guide» — https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide — словари ракурсов, движений, оптики, времени; надёжно.
- [S2] Google Cloud — Vertex AI «Best practices for generating videos» — https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/best-practice — i2v «motion only»; надёжно.
- [S3] Google Cloud — REST `VideoGenerationModelParams` — https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest/Shared.Types/VideoGenerationModelParams — `enhancePrompt`, `generateAudio`, `negativePrompt`; надёжно.
- [S4] Google Cloud — REST `VideoGenerationModelInstance` — там же, `…/VideoGenerationModelInstance` — `cameraControl`, `maskMode`; надёжно.
- [S5] Google Cloud Blog — «Ultimate prompting guide for Veo 3.1», 2025-10-16 — https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1 — формула, таймкоды, FLF; вендор.
- [S6] Google — Gemini API «Generate videos with Veo 3.1» (таблицы «January 2026») — https://ai.google.dev/gemini-api/docs/veo — длительности, язык, звук «Always on», 1 024 токена; надёжно.
- [S7] Google — Gemini API «Gemini Omni Flash» — https://ai.google.dev/gemini-api/docs/omni — теги кадров, петля, один план, правка; надёжно.
- [S8] Runway — «Gen-4 Video Prompting Guide» — https://help.runwayml.com/hc/en-us/articles/39789879462419 — позитивные формулировки, «Locked camera»; надёжно.
- [S9] Runway — «Image to Video Prompting Guide» (Gen-4.5) — https://help.runwayml.com/hc/en-us/articles/48324313115155 — i2v, FAQ мотивов движения, фраза петли; надёжно.
- [S10] Runway — «Camera Terms, Prompts, & Examples» — https://help.runwayml.com/hc/en-us/articles/47313504791059 — словарь камеры; надёжно.
- [S11] Runway — «Introduction to Prompting» — https://help.runwayml.com/hc/en-us/articles/46182941379347 — против оценочных слов и отрицаний; надёжно.
- [S12] Runway — «Text to Video Prompting Guide» — https://help.runwayml.com/hc/en-us/articles/42460036199443 — таймкоды, порядок не важен; надёжно.
- [S13] Runway — «Creating with Edit Studio» (Aleph 2.0) — https://help.runwayml.com/hc/en-us/articles/51683104370451 — короткие промты правки; надёжно.
- [S14] Kling — «VIDEO 3.0 Model User Guide», 2026-02-06 — https://kling.ai/quickstart/klingai-video-3-model-user-guide — мульти-шот UI, «fixed on»; вендор.
- [S15] Kling API — «Kling 3.0 Image to Video» — https://kling.ai/document-api/apiReference/model/imageToVideo — `multi_shot` по умолчанию true, грамматика планов, `audio` off; надёжно.
- [S16] Kling Blog — «Kling AI Prompt Guide», 2026-08-07 — https://kling.ai/blog/kling-ai-prompt-guide — камера простым языком, темп; вендор.
- [S17] Kling — «VIDEO O1 User Guide», 2025-12-15 — https://kling.ai/quickstart/klingai-video-o1-user-guide — FLF и правка `@Video`; вендор.
- [S18] Kling — quickstart «Image-to-Video / Start and End Frames / Camera Movement», 2025-11-24 — https://kling.ai/quickstart/image-to-video-guide — «photos are prone to generating static videos», «not sensitive to numbers»; вендор.
- [S19] BytePlus — «Seedance-1.5-pro prompt guide», 2026-08-31 — https://docs.byteplus.com/en/docs/ModelArk/2168087 — формула, наречия, звук по умолчанию; надёжно.
- [S20] BytePlus — «Dreamina Seedance 2.0 series prompt guide», 2026-09-22 — https://docs.byteplus.com/en/docs/ModelArk/2222480 — медленное движение, правка, слова качества; надёжно.
- [S21] BytePlus — «Dreamina Seedance 2.5 prompt guide» 2026-09-22 и tutorial 2026-09-23 — https://docs.byteplus.com/en/docs/ModelArk/2607689 — таймкоды, языки, правка; надёжно.
- [S22] BytePlus API — «Create a video generation task», 2026-09-22 — https://docs.byteplus.com/en/docs/ModelArk/1520757 — `camera_fixed` «not guaranteed», `generate_audio`; надёжно.
- [S23] ByteDance — скилл `sd25-pe` 0.1.1 (SKILL.md, 996 строк; индекс agent-skills BytePlus) — шаблоны, роли кадров, «event budgets», запрет навешивать запреты; вендор, прочитан без установки.
- [S24] ByteDance — скилл `sd2-pe` (SKILL.md, 2026-09-20) — «only 1 type of camera movement», обязательные слова качества; вендор.
- [S25] Alibaba Cloud — «Text-to-video / image-to-video prompt guide» (Wan) — https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt — «fixed camera», смысл движений, звук словами; надёжно.
- [S26] Alibaba Cloud — «Wan 3.0 video generation guide» + API — https://www.alibabacloud.com/help/en/model-studio/wan3-video-generation-guide — звук, 4–6 с на план, правка; надёжно.
- [S27] Alibaba Cloud — «Wan 2.7 text-to-video API reference» (вкладки 2.6/2.5) и «Call the Wan image-to-video model» — https://www.alibabacloud.com/help/en/model-studio/text-to-video-api-reference — «Only wan2.2 and wan2.1… silent», «Generate a single-shot video»; надёжно.
- [S28] Alibaba — скилл `wan3-pe` 0.2.0 (SKILL.md, 347 строк, 2026-09-17) — «without enriching the story», запреты только по просьбе; вендор.
- [S29] MiniMax — скилл `h3-prompt-writing` (SKILL.md, base-en, ref-en) и README MiniMax-H3 — https://github.com/MiniMax-AI/MiniMax-H3 — IR, I2VA/FL2VA, камера «тип + амплитуда + скорость», против «cinematic»; надёжно.
- [S30] MiniMax — «Video Generation guide» и API video-generation-v2 — https://platform.minimax.io/docs/guides/video-generation — `prompt_expansion_mode` по умолчанию balanced; надёжно.
- [S31] Black Forest Labs — скиллы `flux-3-*` (prompt-doctor, cinematic-inserts, keyframes-continuation, audio-dialogue, product-ads, archival-formats) — https://github.com/black-forest-labs/skills — «Camera lock is advisory», продукт, архивные форматы, антислоп; вендор.
- [S32] Black Forest Labs — FLUX 3 video docs (overview, i2v, camera terms, editing, audio) и FLUX Video Edit — https://docs.bfl.ml/guides/prompting_video_overview — 119 терминов камеры, «locked-on», правка «describes a change, not a shot»; надёжно.
- [S33] polza — каталог `99-raw/cache/polza/2026-09-23_1745/api-v1-models.json` (снят оркестратором 23.09.2026 17:45) — параметры, лимиты, цены видео-моделей; первоисточник канала.
- [V:OA4xB5EY02g] Rames Harikrishnasamy — «AI Art Direction: From Frames to Motion» (Adobe Firefly, 2026) — перечень фона, длительность по размаху, FLF; практик, одна генерация на приём.
- [V:WmC1nqz10Qk] Tim Simmons — «Deep Dive into Cinematic AI Films with Kling 3.0 & 3.0 Omni» (2026-04) — слова качества, камера, действия по порядку; практик для канала вендора.
- [V:BVMuRw8BgJg] Ruben Stom — «Design an Animated Website Hero Using Framer and AI» (2026-01) — запреты zoom/spin/reposition в Veo 3.1; практик.
- [V:5T0yRNmNRi4] Google «Release Notes» — «Introducing Gemini Omni» (2026-05) — правка 2–4 хода, короткий промт дробит на планы; вендор.
- [V:g3w9wemFlmw] VP Land (Joey Daoud, Addy Ghani) — «We tested JSON prompting in Veo 3» (2025-07) — направление в кадре, пометки на кадре; практик, n = 2.
- [V:XLHTLJhzDyQ] Magnific Academy — «Keeping product text consistent with Nano Banana Pro and Kling 3.0 Omni» (2026-03) — референсы товара вместо стартового кадра; вендор площадки.
- [V:I9xdmNZxIfA] Figma — «Figma deep dive: Weave», Config 2026 — «cinematic, 35 mm grain», i2v-строка; практик.
- [V:_Bc4g6fFMp0] Макс Кукушкин (ЦЕХ) — «"3D" моушен графика в бесплатном Kling и Nano Banana Pro» (2026) — неподвижные части тела, «оберег»; практик.
- Своё: `99-raw/notes/wave2/D2-helper-video.md` (43 источника, расхождения со сводкой D), `99-raw/notes/wave2/D2-helper-digests.md`
  (13 дайджестов), `99-raw/experiments/D2/03-phase5-jobs/video_examples.txt`, `05-prompting/01-vendor-prompt-guides.md` §3, §6–§11, §12.2, §12.8.
