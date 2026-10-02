# Пункты зон кода для текстов базы `creative`

Готовые строки из разделов «Для текстов» отчётов зон кода: вносит та зона, в чьём списке стоит файл пункта.
Пункт о файле вне списка зоны — не твой.

**К8а**
- `kb/creative/09-ai-execution-evaluation/02-motion-spec-storyboard-handoff.md`, п. 7 короткого списка, §1.6, чек-лист CRV-MS-05: «LCP-элемент: без анимации или вход по CRV-AL-09 — transform со сдвигом ≤ 24 px, clip-path или opacity от 0,01; не из opacity 0, не маской строк». Шаблон MOTION.md: «The LCP element named in MOTION.md never animates from opacity 0 or behind a line mask — transform (shift at most 24 px), clip-path or opacity from 0.01 only.»

**К8а**
- `kb/creative/01-creative-direction/03-ambition-levels.md`, таблица норм, строка CRV-AL-09: «LCP-элемент не анимируется из `opacity: 0`: только transform, clip-path или появление из 0,01». Там же таблица исключений свойств: `block-size` — `effect:details-accordion`; `clip-path` — `effect:mask-reveal`, `effect:button-expand-label`, `effect:expanding-columns`; `filter` — `effect:sticky-stack`; `--*` — `effect:mesh-gradient-css`.

**К8а**
- `kb/creative/01-creative-direction/02-art-direction-document.md`, поля документа: «`directions[].bans` — запреты направления до выбора; `directions[].notes` — на что смотреть на артборде; `treatment_variants[]` — варианты подачи выбранного направления (`id`, `shows`, `effects`, `chosen`, `chosen_by`)».

**К8а**
- `kb/creative/09-ai-execution-evaluation/01-presentation-spec-and-block-treatments.md`: «`viewer` — наложение-просмотр секции: `effect`, `target`, `note`»; «`page.treatment.peaks`, `accents`, `signature_sections` — необязательная сводка, выводится из секций».

**К8а**
- `kb/creative/06-effects-catalog/01-effects-catalog.md`: «свойства приёма (`motion.properties`) на его минимальном уровне сверяет `spec_check.py levels --check` (LV-03)».

**К8б**
- `kb/creative/06-effects-catalog/01-effects-catalog.md`: число записей 56 → 59; разделы трёх приёмов — `light-sweep` (семейство `image`), `expanding-columns`, `overlay-viewer` (семейство `micro`, §12); §10.1 и §10.3 — два класса движения у `mask-reveal` и `text-mask-media`; §5.1 — «длина закрепления — токены `motion.marketing.scroll.pin-l1-max-vh` и `pin-l2-max-vh`, шаги делят длину сцены».

**К8б**
- `kb/creative/06-effects-catalog/02-hero-video-background.md`, строка 42: «видео-петля 6–12 с» → длина петли по `ai-media/11-evaluation-qa/thresholds.yaml#thresholds.video`.

**К8б**
- `kb/creative/06-effects-catalog/README.md`: строка о `effects.yaml` — поле `motion.properties`.

**К8б**
- `kb/creative/04-visual-language/01-display-typography.md` §4: Science Gothic и Tektur — «д» и «л» по умолчанию нерусской формы, брать после проверки образца.

**К8б**
- `kb/creative/09-ai-execution-evaluation/01-presentation-spec-and-block-treatments.md` §3: поля варианта `level_max`, `roles`, `signature`; варианты `routes-scene`, `grid-quiet`; роль `calm` у семейства портфолио.

**К8б**
- `kb/creative/09-ai-execution-evaluation/02-motion-spec-storyboard-handoff.md`, строка 86: числа `pin-l1-max-vh 150, pin-l2-max-vh 400` — ссылкой на токены.

**К8б**
- `kb/creative/08-uniqueness-anti-slop/01-cliche-policy.md`: надзаголовок — предел ceil(N/3), N — секции с заголовком; доля капса — примета `caps-share`.

**К8б**
- `kb/creative/08-uniqueness-anti-slop/01-cliche-policy.md`, `02-uniqueness-and-variation.md`, `README.md`: реестр клише больше не называет прежнюю утилиту проверки и прежнего исполнителя макета — сверить упоминания в текстах; ключ `compat.k3_checks` реестра стал `compat.mockup_checks`.
