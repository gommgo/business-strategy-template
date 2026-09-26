#!/usr/bin/env python3
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# lang_check.py — копия БЕЗ ПРАВОК КОДА (26.09.2026) проверки языка готовой вёрстки, версия с патчем v1 (md5 53aae9fcd072e971fbd8a1110e7e06ea;
# исходник без патча — md5 007b868f6fe74729a1b43ac7273b0474).
# Назначение: русскоязычная страница, сборка или HTML-копии артбордов без модели и сети: иероглифы и кана в тексте и коде;
#   <html lang> не ru; латинская «рыба» (lorem, placeholder, TODO, «Your …»; маркер [PLACEHOLDER: …] рыбой не считается);
#   строки текстов (copy deck), которых нет в видимом тексте; прямые кавычки в русском тексте; число + единица без
#   неразрывного пробела. Запуск: python3 lang_check.py <папка|html> [--copy <файл текстов>] [--json]; код 1 — есть находки.
# Что убрать при адаптации:
#   1. Разбор файла текстов заточен под markdown-формат старого пакета (шапка «# COPY…», «Voice:», «Keys in square brackets…»,
#      строки «[ключ]: текст»): для copy deck text — читать её формат (YAML) или выгрузку в текст.
#   2. Ссылки докстринга на опыты и патч старой базы (Z/04, «P-патч»).
#   3. Язык задан жёстко (ru, ru-ru) — вынести в параметр, если понадобятся другие локали.
#   4. Проверка иероглифов появилась против подмешивания CJK другой моделью; для Claude — дешёвая страховка, оставить.
# Где описан: claude-design-research/06-design-process/04-checks.md (§3 D, честность текста). Только стандартная библиотека.
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
"""Z/04 lang_check: проверка языка готовой вёрстки русскоязычного сайта (без модели, без сети).
Ищет: иероглифы и кану в коде/тексте, `lang` у <html>, латинские «рыбы» (lorem, placeholder, TODO, Your …), строки copy.md,
которых нет в видимом тексте, прямые кавычки "…" в русском тексте, число+единица без неразрывного пробела.
Запуск:  python3 lang_check.py <папка_сборки_или_html> [--copy copy.md] [--json]
Код возврата: 0 — чисто, 1 — есть находки. Только стандартная библиотека Python 3.
P-патч v1 (kimi-research P, 2026-09-24; оригинал — 99-raw/experiments/Z/04-lang-check/lang_check.py): понимает формат
copy.md сборщика F — строки «[ключ]: текст» сверяются по тексту после двоеточия, шапка «# COPY…», «Voice:», «Keys in square
brackets…» пропускается; маркер [PLACEHOLDER: …] не считается латинской «рыбой» (подписи «placeholder» пустых слотов — считаются)."""
import html, json, os, re, sys
from html.parser import HTMLParser

CJK = re.compile(r"[぀-ヿ㐀-䶿一-鿿豈-﫿＀-￯]")
LATIN_FILLER = re.compile(r"\b(lorem ipsum|lorem|dolor sit|placeholder|todo|tbd|your (company|name|title|text)|sample text|coming soon)\b", re.I)
STRAIGHT_QUOTES_RU = re.compile(r'"[А-Яа-яЁё][^"]{0,80}"')
NUM_UNIT_NO_NBSP = re.compile(r"\d[ ](₽|руб\.?|мин|ч|час|часа|часов|занятий|км|м|кг|%)(?![А-Яа-яЁёA-Za-z])")
TEXT_EXT = (".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".css", ".json", ".md", ".vue", ".svelte", ".astro")

class Visible(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []; self.html_lang = None
    def handle_starttag(self, tag, attrs):
        if tag == "html": self.html_lang = dict(attrs).get("lang")
        if tag in ("script", "style", "noscript", "template"): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template") and self.skip: self.skip -= 1
    def handle_data(self, d):
        if not self.skip and d.strip(): self.parts.append(d)

def files(root):
    if os.path.isfile(root):
        yield root; return
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ("node_modules", ".git", ".next", ".cache")]
        for f in fn:
            if f.endswith(TEXT_EXT): yield os.path.join(dp, f)

def norm(s):
    return re.sub(r"\s+", " ", html.unescape(s).replace(" ", " ").replace(" ", " ")).strip()

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    root = sys.argv[1]
    copy = sys.argv[sys.argv.index("--copy") + 1] if "--copy" in sys.argv else None
    out = {"cjk": [], "html_lang": [], "latin_filler": [], "missing_copy": [], "straight_quotes": [], "num_unit_space": []}
    visible_all = []
    for f in files(root):
        try: txt = open(f, encoding="utf-8", errors="replace").read()
        except Exception: continue
        for i, line in enumerate(txt.splitlines(), 1):
            if CJK.search(line): out["cjk"].append(f"{f}:{i}: {line.strip()[:120]}")
        if f.endswith((".html", ".htm")):
            p = Visible(); p.feed(txt)
            if (p.html_lang or "").lower() not in ("ru", "ru-ru"):
                out["html_lang"].append(f"{f}: <html lang={p.html_lang!r}>")
            vis = norm(" ".join(p.parts)); visible_all.append(vis)
            vis_nomarker = re.sub(r"\[PLACEHOLDER[^\]]*\]", " ", vis, flags=re.I)  # P-патч: маркер пропуска F — не «рыба»
            for m in LATIN_FILLER.finditer(vis_nomarker): out["latin_filler"].append(f"{f}: …{vis_nomarker[max(0,m.start()-30):m.end()+30]}…")
            for m in STRAIGHT_QUOTES_RU.finditer(vis): out["straight_quotes"].append(f"{f}: {m.group(0)[:60]}")
            for m in NUM_UNIT_NO_NBSP.finditer(" ".join(p.parts)): out["num_unit_space"].append(f"{f}: «{m.group(0)}» — нужен неразрывный пробел")
    if copy:
        joined = " ".join(visible_all)
        for line in open(copy, encoding="utf-8"):
            raw = line.strip()
            if raw.startswith(("# COPY", "Voice:", "Keys in square brackets")): continue  # P-патч: шапка copy.md F
            raw = re.sub(r"^\[[^\]]+\]:\s*", "", raw)  # P-патч: «[ключ]: текст» → текст
            s = norm(re.sub(r"^\s*[#>*-]+\s*", "", raw))
            if len(s) >= 12 and s not in joined:
                out["missing_copy"].append(s[:100])
    n = sum(len(v) for v in out.values())
    if "--json" in sys.argv: print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        for k, v in out.items():
            print(f"[{k}] {len(v)}"); [print("  ", x) for x in v[:20]]
        print("ИТОГО находок:", n)
    sys.exit(1 if n else 0)

if __name__ == "__main__":
    main()
