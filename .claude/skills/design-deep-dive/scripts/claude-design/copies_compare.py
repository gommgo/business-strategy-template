#!/usr/bin/env python3
"""copies_compare — сверка адаптивной копии страницы или экрана со статичными копиями её артбордов.

Адаптивную копию (`<page-id>.html` на `system.tokens.css`) агент пишет по принятым артбордам после «Keep»; на ней
проверяются остальные ширины приёмки, вылет, ресайз, зум и среда, она уходит в пакет для кода. Поэтому на ширине каждого
артборда она должна совпадать со статичной копией этого артборда (`references/claude-design.md § HTML-копии и kit`):
  - тексты — дословно: видимые тексты обеих копий на ширине артборда равны как мультимножества (пробелы
    нормализуются, остальное — как есть); лишний и пропавший текст — находка error;
  - геометрия — в допуске: у каждого текстового элемента, найденного в обеих копиях (по тексту и номеру повтора),
    сравниваются левый край, ширина, высота и вертикальный зазор до предыдущего найденного элемента — сдвиг блока
    даёт одну находку, а не каскад по всей странице; расхождение больше допуска — находка warning; высота страниц
    — тоже с допуском.
Допуск (--tol, по умолчанию 8 px) — параметр сверки, а не норма базы: одна вёрстка в одном браузере даёт те же
координаты, небольшой разброс даёт другая запись того же макета (сетка, clamp, max-width).
Кадры снимает Chromium Playwright: окно — ширина рамки артборда, высота 900 (844 уже 640), вся страница; шрифты
дожидаются `document.fonts.ready`; браузер один за раз (`kbpaths.lock("browser")`), свободной памяти нужно ≥ 2 ГБ.
Без браузера (--no-geometry) сверяются только тексты DOM, без видимости и координат.

Какие статичные копии к какой адаптивной: ключ --pairs (`home=Main.html,Landing-Phone.html`), иначе — по текстам: к
адаптивной копии идут статичные копии артбордов страниц макета (canvas.json), половина различных текстов которых есть в
ней; копии «Направлений» и «Вайрфрейма» в пары не идут. Артборды страницы «Состояния» тоже вне автоматических пар:
состояние экрана (пусто, ошибка, нет доступа) делит с экраном каркас и заголовок, а адаптивная копия показывает одно
состояние, и пара по текстам была бы ложной; такой артборд сверяется только ключом --pairs, а `check` без ключа
называет его заметкой.

Команды (файлы проекта — через lib/docpaths.py):
  copies_compare.py check <slug> <surface> [--pairs PAGE=A.html,B.html …] [--tol PX] [--no-geometry] [--repo DIR] [--json]
      design/<surface>/canvas/html/: адаптивные копии против статичных (строка происхождения dc_to_html отличает их).
  copies_compare.py pair <адаптивная.html> <статичная.html …> [--tol PX] [--no-geometry] [--json]
  copies_compare.py --selftest [--browser]   сравнение по синтетическим кадрам; --browser — ещё прогон Chromium
                                             на копиях примера claude-design (правка текста и сдвиг блока)
Находки — строки JSON {rule, severity, surface, kind, ref, path, message, fix}; правило — R-VIS-001 `design-audit`
(копии не проходят автопроверки). Коды выхода: 0 — ошибок нет; 1 — есть находки error; 2 — ошибка вызова или
окружения (нет копий, браузера, памяти).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import kbpaths  # noqa: E402
import docpaths  # noqa: E402
import dc_to_html as DC  # noqa: E402

kbpaths.use("project")
import findings as FND  # noqa: E402

RULE = "R-VIS-001"
TOL = 8.0
HEIGHT_TOL = 0.02                                      # доля высоты страницы
VIEW_H_WIDE, VIEW_H_NARROW, NARROW_BELOW = 900, 844, 640
MIN_FREE_GB = 2.0
OVERLAP = 0.5
MAX_GEOM = 12
STATES_RX = re.compile(r"состояни|\bstates?\b", re.I)   # страница холста «Состояния» (кабинет) по id и имени

COLLECT_JS = r"""
() => {
  const clean = (t) => (t || '').replace(/\s+/g, ' ').trim();
  const vis = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return false;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity || '1') < 0.05) return false;
    }
    return true;
  };
  const out = [], seen = new Set();
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const t = w.currentNode;
    if (!clean(t.textContent)) continue;
    const el = t.parentElement;
    if (!el || seen.has(el) || el.closest('script, style, svg, noscript, template')) continue;
    seen.add(el);
    if (!vis(el)) continue;
    const own = clean(Array.from(el.childNodes).filter((n) => n.nodeType === 3).map((n) => n.textContent).join(' '));
    if (!own) continue;
    const r = el.getBoundingClientRect();
    out.push({text: own, tag: el.tagName.toLowerCase(), x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height});
  }
  for (const el of document.querySelectorAll('input[placeholder], textarea[placeholder]')) {
    if (!vis(el)) continue;
    const r = el.getBoundingClientRect();
    out.push({text: clean(el.getAttribute('placeholder')), tag: 'placeholder', x: r.left + scrollX, y: r.top + scrollY,
              w: r.width, h: r.height});
  }
  out.sort((a, b) => (a.y - b.y) || (a.x - b.x));
  return {leaves: out, height: document.documentElement.scrollHeight, width: document.documentElement.scrollWidth};
}
"""


class ToolError(RuntimeError):
    """Ошибка вызова или окружения — код выхода 2."""


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip()


# ------------------------------------------------------------------ тексты и геометрия

def dom_texts(path):
    """Тексты DOM без браузера: собственный текст элементов и подсказки полей (как собирает браузер)."""
    root, _notes = DC.parse(Path(path).read_text(encoding="utf-8", errors="replace"))
    body = DC.find(root, lambda e: e.tag == "body") or root
    out = []

    def rec(node):
        for ch in node.children:
            if not isinstance(ch, DC.El) or ch.tag in ("script", "style", "svg", "noscript", "template"):
                continue
            own = norm(html.unescape(" ".join(c.raw for c in ch.children if isinstance(c, DC.Tx) and c.kind == "text")))
            if own:
                out.append(own)
            if ch.tag in ("input", "textarea") and ch.attrs.get("placeholder"):
                out.append(norm(html.unescape(ch.attrs["placeholder"])))
            rec(ch)
    rec(body)
    return out


def text_diff(static_texts, adaptive_texts):
    """(нет в адаптивной, лишнее в адаптивной) — мультимножества нормализованных текстов."""
    s, a = Counter(norm(t) for t in static_texts if norm(t)), Counter(norm(t) for t in adaptive_texts if norm(t))
    return sorted((s - a).elements()), sorted((a - s).elements())


def keyed(leaves):
    """Элементы по ключу (текст, номер повтора) в порядке страницы."""
    seen, out = Counter(), []
    for lf in leaves:
        t = norm(lf["text"])
        seen[t] += 1
        out.append(((t, seen[t]), lf))
    return out


def geometry(static_leaves, adaptive_leaves, tol=TOL):
    """Расхождения геометрии сверх допуска: [(ключ, {dx, dw, dh, dgap}, статичный, адаптивный)] по убыванию."""
    amap = dict(keyed(adaptive_leaves))
    out, prev = [], None
    for key, s in keyed(static_leaves):
        a = amap.get(key)
        if a is None:
            continue
        d = {"dx": a["x"] - s["x"], "dw": a["w"] - s["w"], "dh": a["h"] - s["h"],
             "dgap": 0.0 if prev is None else (a["y"] - prev[1]["y"]) - (s["y"] - prev[0]["y"])}
        if max(abs(v) for v in d.values()) > tol:
            out.append((key, {k: round(v, 1) for k, v in d.items()}, s, a))
        prev = (s, a)
    return sorted(out, key=lambda x: -max(abs(v) for v in x[1].values()))


def describe(d):
    names = {"dx": "левый край", "dw": "ширина", "dh": "высота", "dgap": "зазор сверху"}
    return ", ".join(f"{names[k]} {v:+g} px" for k, v in d.items() if abs(v) > 0.05)


# ------------------------------------------------------------------ браузер

def free_gb():
    try:
        for line in open("/proc/meminfo", encoding="ascii"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024 / 1024
    except OSError:
        pass
    return None


def render_leaves(jobs):
    """[(файл, ширина)] → {(файл, ширина): {leaves, height, width}} — один браузер на все кадры."""
    gb = free_gb()
    if gb is not None and gb < MIN_FREE_GB:
        raise ToolError(f"свободной памяти {gb:.1f} ГБ < {MIN_FREE_GB:g} ГБ — браузер не запускается")
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError as e:
        raise ToolError("нет Playwright: окружение скилла ставит install.sh ($DDD_HOME/venv)") from e
    out = {}
    with kbpaths.lock("browser"), sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for path, w in jobs:
                h = VIEW_H_WIDE if w >= NARROW_BELOW else VIEW_H_NARROW
                ctx = browser.new_context(viewport={"width": int(w), "height": h}, device_scale_factor=1,
                                          reduced_motion="reduce")
                page = ctx.new_page()
                try:
                    page.goto(Path(path).resolve().as_uri(), wait_until="load", timeout=30000)
                except PWTimeout:
                    pass                                # внешние шрифты не пришли вовремя — сверяется то, что отрисовано
                try:
                    page.wait_for_function("!document.fonts || document.fonts.status === 'loaded'", timeout=10000)
                except Exception:  # noqa: BLE001 — страница без API шрифтов или шрифт не пришёл: сверяется как есть
                    pass
                page.wait_for_timeout(150)
                out[(str(path), int(w))] = page.evaluate(COLLECT_JS)
                ctx.close()
        finally:
            browser.close()
    return out


# ------------------------------------------------------------------ пары и сверка

def static_info(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"рамка (\d+)×(\d+)", text)
    return DC.copy_source(text), (int(m.group(1)) if m else None)


def static_stages(canvas_dir, statics):
    """Этап страницы холста у артборда каждой статичной копии (canvas.json): directions · wireframe · mockup; артборд
    страницы «Состояния» — states."""
    canvas = DC.load_canvas(canvas_dir) if canvas_dir and Path(canvas_dir).is_dir() else None
    out = {}
    for s in statics:
        src, _w = static_info(s)
        board = (canvas or {}).get("boards", {}).get(src)
        stage = DC.stage_of(board, canvas) if canvas else "mockup"
        if stage == "mockup" and board:
            pid = str(board.get("page") or "")
            if STATES_RX.search(f"{pid} {canvas['pages'].get(pid, '')}"):
                stage = "states"
        out[Path(s).name] = stage
    return out


def infer_pairs(statics, adaptives, stages=None):
    """Адаптивная копия ← статичные копии артбордов макета, половина различных текстов которых есть в ней; артборды
    «Направлений», «Вайрфрейма» и «Состояний» в пары не идут."""
    at = {a: set(dom_texts(a)) for a in adaptives}
    pairs = {a: [] for a in adaptives}
    for s in statics:
        if stages and stages.get(Path(s).name, "mockup") != "mockup":
            continue
        st = set(dom_texts(s))
        if not st:
            continue
        best = max(adaptives, key=lambda a: len(st & at[a]) / len(st), default=None)
        if best is not None and len(st & at[best]) / len(st) >= OVERLAP:
            pairs[best].append(s)
    return {a: v for a, v in pairs.items() if v}


def compare(adaptive, statics, tol=TOL, geometry_on=True, surface=None, rel=str):
    """Находки R-VIS-001 одной адаптивной копии против её статичных копий."""
    rep = FND.Report()
    aname = Path(adaptive).name
    fix = ("адаптивная копия повторяет принятые артборды на их ширинах: тексты — дословно, раскладка — как на артборде "
           "(раунд «промежуточные ширины», references/claude-design.md § HTML-копии и kit)")
    jobs, info = [], {}
    for s in statics:
        src, w = static_info(s)
        if not w:
            raise ToolError(f"{s}: не статичная копия dc_to_html (нет строки происхождения с рамкой)")
        info[s] = (src, w)
        jobs += [(s, w), (adaptive, w)]
    shots = render_leaves(jobs) if geometry_on else {}
    for s in statics:
        src, w = info[s]
        ref = f"{aname}@{w}"
        if geometry_on:
            S, A = shots[(str(s), w)], shots[(str(adaptive), w)]
            st, at = [x["text"] for x in S["leaves"]], [x["text"] for x in A["leaves"]]
        else:
            S = A = None
            st, at = dom_texts(s), dom_texts(adaptive)
        miss, extra = text_diff(st, at)
        where = f"на ширине {w}" if geometry_on else f"в DOM без браузера (артборд {w} px)"
        if miss:
            rep.add(RULE, "error", surface=surface, kind="copy", ref=ref, path=rel(adaptive),
                    message=f"{where}: {len(miss)} текст(ов) артборда {src} нет в адаптивной копии: "
                            + "; ".join(f"«{t[:60]}»" for t in miss[:6]), fix=fix)
        if extra:
            rep.add(RULE, "error", surface=surface, kind="copy", ref=ref, path=rel(adaptive),
                    message=f"{where}: {len(extra)} текст(ов) адаптивной копии нет на артборде {src}: "
                            + "; ".join(f"«{t[:60]}»" for t in extra[:6]), fix=fix)
        if not geometry_on:
            continue
        for key, d, sl, al in geometry(S["leaves"], A["leaves"], tol)[:MAX_GEOM]:
            rep.add(RULE, "warning", surface=surface, kind="copy", ref=f"{ref}#{key[0][:40]}", path=rel(adaptive),
                    message=f"на ширине {w}: «{key[0][:50]}» ({sl['tag']}) расходится с артбордом {src} сверх допуска "
                            f"{tol:g} px — {describe(d)}", fix=fix)
        dh = A["height"] - S["height"]
        if abs(dh) > max(tol, HEIGHT_TOL * S["height"]):
            rep.add(RULE, "warning", surface=surface, kind="copy", ref=f"{ref}#height", path=rel(adaptive),
                    message=f"на ширине {w}: высота страницы {A['height']} px против {S['height']} px артборда {src} "
                            f"({dh:+d} px)", fix=fix)
    return rep


def cmd_check(call):
    a = call.args
    html_dir = docpaths.design(call.slug, "canvas-html", surface=call.surface, repo=call.repo)
    if not html_dir.is_dir():
        raise ToolError(f"нет HTML-копий: {docpaths.rel(html_dir, call.repo)} (dc_to_html build)")
    statics, adaptives = [], []
    for p in sorted(html_dir.glob("*.html")):
        (statics if DC.copy_source(p.read_text(encoding="utf-8", errors="replace")) else adaptives).append(p)
    if a.pairs:
        pairs = {}
        for it in a.pairs:
            k, sep, v = it.partition("=")
            if not sep:
                raise ToolError(f"--pairs: ожидается страница=A.html,B.html, получено {it!r}")
            ad = html_dir / (k.strip() if k.strip().endswith(".html") else k.strip() + ".html")
            pairs[ad] = [html_dir / x.strip() for x in v.split(",") if x.strip()]
            for p in [ad] + pairs[ad]:
                if not p.is_file():
                    raise ToolError(f"нет копии: {docpaths.rel(p, call.repo)}")
    else:
        canvas_dir = docpaths.design(call.slug, "canvas-project", surface=call.surface, repo=call.repo)
        stages = static_stages(canvas_dir, statics)
        pairs = infer_pairs(statics, adaptives, stages)
    rep = FND.Report()
    states = [] if a.pairs else sorted(n for n, st in stages.items() if st == "states")
    if states:
        rep.add(RULE, "hint", surface=call.surface, kind="copy", ref="states",
                path=docpaths.rel(html_dir, call.repo),
                message=f"артборды страницы «Состояния» в автоматические пары не идут ({len(states)}: "
                        + ", ".join(states[:6]) + (" …" if len(states) > 6 else "") + ")",
                fix="сверка состояния с адаптивной копией — ключ --pairs <страница>=<артборд>.html")
    for ad, sts in pairs.items():
        rep.extend(compare(ad, sts, a.tol, not a.no_geometry, call.surface,
                           rel=lambda p: docpaths.rel(p, call.repo)).items)
    for ad in adaptives:
        if ad not in pairs:
            rep.add(RULE, "hint", surface=call.surface, kind="copy", ref=ad.name, path=docpaths.rel(ad, call.repo),
                    message="адаптивной копии не нашлась ни одна статичная копия артборда (по текстам)",
                    fix="--pairs <страница>=<артборд>.html,… или dc_to_html build")
    FND.print_findings(rep.items, as_json=call.json,
                       title=None if call.json else f"copies_compare check {call.slug} {call.surface}")
    return rep.exit_code()


def cmd_pair(a):
    for p in [a.adaptive] + a.statics:
        if not Path(p).is_file():
            raise ToolError(f"нет файла: {p}")
    rep = compare(Path(a.adaptive), [Path(s) for s in a.statics], a.tol, not a.no_geometry)
    FND.print_findings(rep.items, as_json=a.json, title=None if a.json else "copies_compare pair")
    return rep.exit_code()


# ------------------------------------------------------------------ самопроверка

def selftest(browser=False):
    import tempfile
    ok = True

    def check(name, got, want=True):
        nonlocal ok
        good = got == want
        ok &= good
        print(f"{'OK  ' if good else 'FAIL'} {name}" + ("" if good else f": {got!r} (ожидалось {want!r})"))

    def leaf(t, x, y, w=300, h=24, tag="p"):
        return {"text": t, "tag": tag, "x": x, "y": y, "w": w, "h": h}

    base = [leaf("Заголовок", 120, 100, 600, 60, "h1"), leaf("Подводка", 120, 180), leaf("Кнопка", 120, 240, 160, 48, "a"),
            leaf("Секция", 120, 400, 600, 40, "h2"), leaf("Текст секции", 120, 460), leaf("Кнопка", 120, 520, 160, 48, "a")]
    check("копия против себя — 0 расхождений", (text_diff([x["text"] for x in base], [x["text"] for x in base]),
                                               geometry(base, base)), (([], []), []))
    edited = [dict(x, text="Подводка правленая") if x["text"] == "Подводка" else x for x in base]
    miss, extra = text_diff([x["text"] for x in base], [x["text"] for x in edited])
    check("правленый текст — пропал и лишний", (miss, extra), (["Подводка"], ["Подводка правленая"]))
    shifted = [dict(x, y=x["y"] + 40) if x["y"] >= 400 else x for x in base]
    g = geometry(base, shifted)
    check("сдвиг блока на 40 px — одна находка, без каскада", [(k[0], d["dgap"]) for k, d, _s, _a in g],
          [("Секция", 40.0)])
    small = [dict(x, y=x["y"] + 5) if x["y"] >= 400 else x for x in base]
    check("сдвиг 5 px в допуске 8 px — 0 находок", geometry(base, small), [])
    wide = [dict(x, w=x["w"] + 30) if x["text"] == "Текст секции" else x for x in base]
    check("ширина элемента +30 px — находка", [(k[0], d["dw"]) for k, d, _s, _a in geometry(base, wide)],
          [("Текст секции", 30.0)])
    check("повтор текста различается номером", [k for k, _ in keyed(base) if k[0] == "Кнопка"],
          [("Кнопка", 1), ("Кнопка", 2)])
    src = DC.EXAMPLE / "canvas" / "project"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for _ab, name, text, _b, _n in DC.build_copies(src):
            (td / name).write_text(text, encoding="utf-8")
        adapt = td / "home.html"
        adapt.write_text(re.sub(r"<!-- dc_to_html:[^\n]*-->\n", "", (td / "Main.html").read_text(encoding="utf-8")),
                         encoding="utf-8")
        statics = sorted(p for p in td.glob("*.html") if p.name != "home.html")
        pairs = infer_pairs(statics, [adapt], static_stages(src, statics))
        check("пары по текстам: home ← Main и Landing-Phone (макет), не «Направления» и «Вайрфрейм»",
              sorted(p.name for p in pairs.get(adapt, [])), ["Landing-Phone.html", "Main.html"])
        cj = json.loads((src / "canvas.json").read_text(encoding="utf-8"))
        cj["pages"].append({"id": "states", "name": "4 · Состояния"})
        cj["boards"]["Landing-Phone.dc.html"]["page"] = "states"
        (td / "states").mkdir()
        (td / "states" / "canvas.json").write_text(json.dumps(cj, ensure_ascii=False), encoding="utf-8")
        st = static_stages(td / "states", statics)
        check("артборд страницы «Состояния» — этап states", st.get("Landing-Phone.html"), "states")
        pairs = infer_pairs(statics, [adapt], st)
        check("«Состояния» — вне автоматических пар: home ← только Main",
              sorted(p.name for p in pairs.get(adapt, [])), ["Main.html"])
        rep = compare(adapt, [td / "Main.html"], geometry_on=False)
        check("без браузера: копия против себя — 0 находок", rep.items, [])
        adapt.write_text(adapt.read_text(encoding="utf-8").replace("Что делаем", "Чем занимаемся"), encoding="utf-8")
        rep = compare(adapt, [td / "Main.html"], geometry_on=False)
        check("без браузера: правленый текст — две находки error", [(f.severity, f.rule) for f in rep.items],
              [("error", RULE), ("error", RULE)])
        if browser:
            adapt.write_text(re.sub(r"<!-- dc_to_html:[^\n]*-->\n", "", (td / "Main.html").read_text(encoding="utf-8")),
                             encoding="utf-8")
            rep = compare(adapt, [td / "Main.html"])
            check("браузер: копия против себя — 0 находок", [(f.severity, f.message[:60]) for f in rep.items], [])
            txt = adapt.read_text(encoding="utf-8")
            adapt.write_text(txt.replace('<section id="how" style="', '<section id="how" style="margin-top: 40px; ', 1)
                             .replace("Три шага, без очереди у стойки.", "Три шага без очереди."), encoding="utf-8")
            rep = compare(adapt, [td / "Main.html"])
            sev = Counter(f.severity for f in rep.items)
            check("браузер: сдвиг блока и правка текста — находки", (sev["error"] >= 2, sev["warning"] >= 1), (True, True))
            check("браузер: сдвиг назван у заголовка секции",
                  any("Как это работает" in f.message and "зазор сверху +40" in f.message for f in rep.items), True)
    print("selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------ вызов

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if "--selftest" in argv:
            return selftest(browser="--browser" in argv)
        if argv[:1] == ["pair"]:
            ap = argparse.ArgumentParser(prog="copies_compare.py pair", description="Адаптивная копия против статичных.")
            ap.add_argument("cmd")
            ap.add_argument("adaptive")
            ap.add_argument("statics", nargs="+")
            ap.add_argument("--tol", type=float, default=TOL, help=f"допуск геометрии, px (по умолчанию {TOL:g})")
            ap.add_argument("--no-geometry", action="store_true", help="только тексты DOM, без браузера")
            ap.add_argument("--json", action="store_true")
            return cmd_pair(ap.parse_args(argv))
        ap = docpaths.parser("copies_compare.py", __doc__, commands=("check",), surface="required",
                             accept=lambda s: s.design)
        ap.add_argument("--pairs", action="append", help="страница=A.html,B.html — статичные копии адаптивной; повтором")
        ap.add_argument("--tol", type=float, default=TOL, help=f"допуск геометрии, px (по умолчанию {TOL:g})")
        ap.add_argument("--no-geometry", action="store_true", help="только тексты DOM, без браузера")
        ap.add_argument("--browser", action="store_true", help=argparse.SUPPRESS)
        call = docpaths.parse(ap, argv)
        return cmd_check(call)
    except (ToolError, DC.ToolError) as e:
        print(f"copies_compare: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
