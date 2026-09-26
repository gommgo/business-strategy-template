# M/06 — OG 1200×630 и инфографика маркетплейса 900×1200 шаблонами (кириллица — HTML)

- **Цель**: рецепты «OG с кириллицей» и «инфографика маркетплейса» без генерации: шаблон → Playwright → JPEG/WebP → OCR K.
- **Команды**: `flock -w 900 99-raw/tools/.locks/browser.lock python3 render.py` (Chromium 153 CfT, Playwright 1.63, < 5 с);
  `flock … python3 layout_check.py` (DOM до/после + слой текста) и `layout_check.py page <html> 1440x900 412x915 360x800`;
  `asset_audit.py audit marketplace_master.png --slot product --expect … --allow-text … --out audit_mp`; OCR строк —
  `asset_audit.py ocr marketplace_master.png`.
- **Результат** (`results_og_mp.json`, повтор 06:03 после правки шаблона): OG JPEG q86 — 46,4 КБ; карточка WebP q85 — 48,8 КБ
  (s2 80,5), превью 450 — 19,0 КБ; шрифты — Noto Serif Display / Noto Sans.
- **Ошибка первой версии (05:12) и как её нашли**: в `li{display:flex;gap:18px}` голый текст «Доставка за » и
  `<span style="white-space:nowrap">1–2 дня</span>` стали двумя флекс-элементами → «1–2 дн[я]» уехало на этикетку банки, «за»
  — строкой ниже. OCR прочитал это честно («о Доставка 1-2 дн ЛЕСНАЯ ОБЖАРКА» + «за»), а я сначала записал это как «склейку
  строк OCR». Заметил глазом в 06:00 (разрыв «Доставка   1–2 дня» на листе `asset_inventory`, затем «1–2 дн» на банке в
  `marketplace_master.png`); DOM-проверка `layout_check.py` подтвердила и измерила (`results_layout.json`): before — fail (пересечение с альфой банки
  1 588 px², переполнения `li` 325 > 290 и `span` 107 > 72, nowrap-флекс 1); after (подпись — один `<span>`, `li>span{min-width:0}`)
  — pass. Та же проверка на демо-странице нашла ту же ошибку в полосе иконок (до правки — `results_layout_page_before.json`:
  `li` 170 > 158 px на 1440, 170 > 151 на 360, nowrap-флекс на всех ширинах; после — `results_layout_page.json`, pass на
  1440/412/360); страницы J 00–08 — pass на 1440 и 412 (`results_layout_J_pages.json`); OG — текст в безопасной зоне 1100×530
  (рамка текста 78–666 × 172–455, `results_layout_og.json`).
- **OCR**: карточка с банкой — детектор склеивает строку колонки «Доставка за» с этикеткой на той же высоте («ИСНЯ ОБЖА», 0,40) →
  `omission/substitution`, needs_human (`audit_mp/`); **слой текста без банки** (`marketplace_textlayer.png`, снимок
  `layout_check.py`) — 7 из 7 строк, CER 0, точность слов 1,0 (`audit_mp_textlayer/`); угловая эвристика L — needs_human по
  дизайну.
- **Ловушки**: «1–2 дня» рвётся на тире → `white-space: nowrap` внутри элемента подписи (не прямым потомком флекс-контейнера);
  выдуманный домен в OG заменён текстом «Демо-бренд».
