#!/usr/bin/env python3
"""lang_check.py — проверка языка готовой вёрстки русскоязычной страницы: HTML-копии артбордов, сборка (без модели и сети).

Ищет: иероглифы и кану в коде и тексте (страховка от подмешанных чужих систем письма); `lang` у <html> не ru; латинскую
«рыбу» (lorem, placeholder, TODO, «Your …»; маркер [PLACEHOLDER: …] рыбой не считается, подпись «placeholder» пустого
слота — считается); строки copy.md входа холста, которых нет в видимом тексте; прямые кавычки "…" в русском тексте; число
и единицу без неразрывного пробела.
Запуск:  python3 lang_check.py <папка_сборки_или_html> [--copy copy.md] [--json]
copy.md — синтаксис выгрузки текстов (`copydeck.py export`): строки слотов `[<slot_id>] <статус>: текст` сверяются по
тексту после двоеточия; заголовки, комментарии и строки секций пропускаются.
Код возврата: 0 — чисто, 1 — есть находки, 2 — нет аргумента. Только стандартная библиотека Python 3.
Где описан: claude-design/06-design-process/04-checks.md (§3 D, честность текста).
"""
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
            vis_nomarker = re.sub(r"\[PLACEHOLDER[^\]]*\]", " ", vis, flags=re.I)  # маркер пропуска факта — не «рыба»
            for m in LATIN_FILLER.finditer(vis_nomarker): out["latin_filler"].append(f"{f}: …{vis_nomarker[max(0,m.start()-30):m.end()+30]}…")
            for m in STRAIGHT_QUOTES_RU.finditer(vis): out["straight_quotes"].append(f"{f}: {m.group(0)[:60]}")
            for m in NUM_UNIT_NO_NBSP.finditer(" ".join(p.parts)): out["num_unit_space"].append(f"{f}: «{m.group(0)}» — нужен неразрывный пробел")
    if copy:
        joined = " ".join(visible_all)
        for line in open(copy, encoding="utf-8"):
            raw = line.strip()
            if raw.startswith(("#", "<!--")): continue  # заголовок, комментарий, строка секции «## <section_id>»
            m = re.match(r"^\[[^\]]*\](?:\s+[a-z]+)?:\s?(.*)$", raw)  # «[slot_id] статус: текст» → текст
            if m: raw = m.group(1)
            s = norm(re.sub(r"^\s*[>*-]+\s*", "", raw))
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
