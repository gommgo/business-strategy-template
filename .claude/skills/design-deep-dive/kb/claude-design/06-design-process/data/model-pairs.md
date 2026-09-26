<!-- Сводка замера 24.09.2026, скопирована 26.09.2026: имена генератора, вендора и хостинга заменены метками (G, G0, «вендор G», «хостинг-G»), числа не менялись; легенда — README.md этой папки. -->
# E/04 — пары «G против другой модели» на одинаковом промте (каталог Sulat.com)

Продолжатель-3 агента E, 2026-09-24 05:09–05:36. Без запуска моделей: только публичные страницы и их `PROMPT.md`.

**Цель.** Закрыть пробел задания «образцы парами с Fable 5 / GPT на тех же промтах» живым DOM, а не скриншотами.

**Источник.** Sulat.com — «a repository-maintained catalogue of one-shot experiments»: `https://demos.sulat.com/` (снимок 24.09:
1 082 демо, 27 моделей; G — 349, Fable 5 — 5, Opus 5 — 7, Opus 5.5 — 9, GPT-5.6 Sol — 18, GPT-6 Astra — 19, Qwen 3.8 Max — 42,
GLM-5.3 — 84, Gemini 3.8 Flash — 195). Адрес демо — `https://<slug>.<model>.demos.sulat.com/`, промт — `…/PROMPT.md`
(найдено в `catalogue-v9.js`: `promptSource.href = "https://" + hostname + "/PROMPT.md"`). Автор каталога — jpcaparas (Reddit 1vrkh1m);
демо, вероятно, сделаны его скиллом `oneshot-websites`; харнесс у моделей разный (для Opus 5 Ubuntu — Devin CLI, 2 ч 30 мин,
r/ClaudeAI 1v5v71s); для G харнесс не указан.

**Шаги.** 1) Индексы моделей (`*_index.html`) → пересечение слагов с G (`pairs.json`): Fable 5 — 3, Opus 5 — 3, Opus 5.5 — 5,
Sol — 9, Astra — 5, Qwen — 11, GLM-5.3 — 57. 2) md5 `PROMPT.md` (папка `prompts/`): **одинаковы** — wolverine-landing-page (G = Sol),
mint и ubuntu (G = Fable 5), apple-store, baseten, chatgpt-for-linux, cloudflare-durable-objects, claude-ai-generated-content
(G = GLM-5.3); разные — avengers (G ≠ Sol), odyssey (G ≠ Opus 5/5.5), openai-ultrafast-explainer (G ≠ Sol). 3) `probe_shots.py`
(копия из E/03) по 10 страницам × 2 окна → `probe/`, `shots/`, `sheets/`; сводка `summarize_probe.py` → `probe_summary.*`.

**Промты.** «Create a superior landing page for X… demonstrably better than the official page at <URL>. Treat that URL as the
baseline to beat, not to copy: study it, download its assets… ship them as local files… Ground every word of content in the real
facts» — 3,7–5,7 КБ, с реальными фактами; сеть и скачивание ассетов разрешены.

**Результат (1440×900, глаз + замер).**

| Пара | Что общего | Разница | Кто лучше (глаз E, n = 1) |
|---|---|---|---|
| Wolverine: G / GPT-5.6 Sol | тёмные, официальные ассеты, сужённые гротески капсом, FAQ | G — Anton + Oswald, тёмно-янтарная, равномерная, 4 карточки с иконками, большие водяные цифры, пустоватые тёмные зоны; стекло 12, glow 9, капс 0,20. Sol — Impact + Arial Narrow + Georgia, чередует тёмные и кремовые секции, наклонная жёлтая панель, таймер; стекло 18, glow 5, капс 0,40, нумерация 43 | Sol (разнообразнее и контрастнее) — совпадает с AIHubMix «Sol a bit more polished visually» |
| Mint (экран входа ОС): G / Fable 5 | почти одинаково, Ubuntu-шрифт, чёрный фон | часы 34 px справа против 64 px по центру | ничья |
| Baseten: G / GLM-5.3 | **одни и те же фирменные шрифты** (Neue Alte Grotesk + Chivo Mono, скачаны с сайта), белый фон, H1 «Inference is everything» 88–100 px | G выделила слово «everything» | ничья |
| Cloudflare DO: G / GLM-5.3 | белый фон, H1 про «tiny stateful server», выделенное слово в H1 у обеих | G — Inter + Space Grotesk, GLM — Kunst Grotesk; «·» 12 и 14, тире 48 и 54 | ничья |
| Claude «AI-generated content»: G / GLM-5.3 | **почти один и тот же дизайн**: крем (`#f4eee4` / `#faf6ee`), Fraunces с **курсивным терракотовым словом в H1** («marks» / «makes»), эйбрау «— EU AI ACT · ARTICLE 50(2)…», нумерованные разделы, тёмная секция «Limitations» в две колонки, демо водяного знака и C2PA-файла с солнцем | GLM — больше карточек и пилюль (38 против 22) | ничья |

**Выводы.** 1) На подробном промте «побей официальный сайт» с его ассетами **модели сходятся**: бренд и ассеты задают шрифты,
палитру и даже раскладку; почерк модели — в мелочах. 2) Хром «·», длинные тире, выделенное слово, эйбрау **есть у всех моделей**
(G, GLM-5.3, Sol) — это общая примета LLM-вёрстки 2026 (часть тире — из текста промта), а не только G. 3) На единственной
паре с GPT-5.6 Sol G выглядит беднее композиционно. 4) Пар с Fable 5.1 / Opus 5.5 на одинаковом промте в каталоге нет.

**Ограничения.** n = 1 на пару; «кто лучше» — вкус E; харнесс и `effort` не указаны; каталог — отбор автора; 10 страниц, без
`measure_ui`/`ui_audit` (время). Размер папки — 17 МБ (скриншоты JPEG).
