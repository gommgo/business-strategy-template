#!/usr/bin/env python3
"""kit_manifest — манифест кадров `kit.json` HTML-копий холста: копии × ширины приёмки × темы, класс экрана, границы ДС.

Набор ширин задаёт заказчик в одном месте — `kb/common/acceptance-widths.yaml` (NU-01); утилита его не повторяет, а
раскладывает по копиям поверхности (`references/claude-design.md § HTML-копии и kit`):
  - статичная копия артборда (`<Имя>.html`, перевод `dc_to_html.py`) — кадр на ширине и высоте своей рамки; её тема —
    та, что дали твики артборда (тёмная — при твике темы со значением dark);
  - адаптивная копия страницы или экрана (`<page-id>.html`, пишет агент после «Keep») — кадры на ширинах класса экрана
    в каждой теме ДС (`themes` файла ширин, тёмная — если она есть в токенах ДС), вылет на `overflow_only` и проверка
    перестроения на границах брейкпоинтов ДС ± 1 px (NU-05; числа случайных ширин внутри диапазонов — по цене прогона,
    их здесь нет);
  - класс экрана (NU-02): у кабинета — поле `viewport` экрана (`screens/<surface>/screens/<slug>/index.md`), у страницы
    сайта — `any`; `acceptance-widths.yaml#by_viewport`: `desktop` — ширины от первого брейкпоинта ДС, `mobile` — ниже
    него и вылет, `any` — все ширины и вылет;
  - брейкпоинты — токены `breakpoint.*` ДС продукта (`system.tokens.css` или DTCG); без них — эталон по маршруту:
    кабинет — эталонные токены ui (`kb/ui/14-recipes/examples/tokens.css`), сайт — соглашение `breakpoints` каталога
    блоков site (`kb/site/04-blocks/blocks.yaml`);
  - высота окна кадра адаптивной копии — параметр прогона, а не норма: 900 у широких окон, 844 у окон уже первого
    брейкпоинта (окна первого экрана site 1440×900 и 390×844).
`kit/shot.py <canvas/html> <кадры> --manifest kit.json` снимает кадры по списку `artboards` манифеста (поля file, w, h,
theme, title); поля `kind` (static · adaptive) и `check` (artboard · width · overflow · reflow) говорят, зачем кадр.
Манифест — производная: руками не правится, в нём нет даты — пересборка без изменений даёт те же байты.

Команды (файлы проекта — через lib/docpaths.py):
  kit_manifest.py build <slug> <surface> [--repo DIR] [--json]   пишет design/<surface>/canvas/html/kit.json
  kit_manifest.py check <slug> <surface> [--repo DIR] [--json]   R-FRESH-005: kit.json равен сборке из файла ширин
  kit_manifest.py make <папка копий> [--canvas ПАПКА] [--tokens ФАЙЛ …] [--route page|app] [--viewport КОПИЯ=КЛАСС …]
                       [--out ФАЙЛ] [--json]                     вне проекта; без --out — в stdout
  kit_manifest.py --selftest                                      на фикстуре canvas и примере базы, без сети
Коды выхода: 0 — готово, ошибок нет; 1 — есть находки error (check); 2 — ошибка вызова или окружения.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "lib"))
import kbpaths  # noqa: E402
import docpaths  # noqa: E402

kbpaths.use("claude-design")
import dc_to_html as DC  # noqa: E402
import literal_tokens as LT  # noqa: E402

kbpaths.use("project")
import findings as FND  # noqa: E402

RULE = "R-FRESH-005"
WIDTHS = kbpaths.kb(None, "common", "acceptance-widths.yaml")
REF_UI = kbpaths.kb("ui", "14-recipes", "examples", "tokens.css")
REF_SITE = kbpaths.kb("site", "04-blocks", "blocks.yaml")
VIEW_H_WIDE, VIEW_H_NARROW = 900, 844
NAME = "kit.json"
CLASSES = ("desktop", "mobile", "any")


class ToolError(RuntimeError):
    """Ошибка вызова или окружения — код выхода 2."""


def _yaml():
    import yaml
    return yaml


def acceptance():
    """Файл ширин приёмки: widths, artboards, overflow_only, themes, by_viewport."""
    text = WIDTHS.read_text(encoding="utf-8")
    d = _yaml().safe_load(text) or {}
    return {"widths": [int(w) for w in d.get("widths") or []], "artboards": [int(w) for w in d.get("artboards") or []],
            "overflow_only": int(d["overflow_only"]) if d.get("overflow_only") else None,
            "themes": [str(t) for t in d.get("themes") or []], "by_viewport": d.get("by_viewport") or {},
            "sha256_16": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]}


def reference_breakpoints(route):
    """Эталонные границы без ДС: кабинет — токены ui (`--bp-*`), страница — соглашение `breakpoints` блоков site."""
    if route == "app":
        vals = re.findall(r"--bp-[a-z-]+:\s*(\d+(?:\.\d+)?)px", REF_UI.read_text(encoding="utf-8"))
        return sorted(float(v) for v in vals), "эталонные токены ui (" + str(REF_UI.relative_to(kbpaths.kb())) + ")"
    d = _yaml().safe_load(REF_SITE.read_text(encoding="utf-8")) or {}
    rule = next((str(c.get("rule")) for c in _find_conventions(d.get("conventions")) if c.get("id") == "breakpoints"), "")
    vals = sorted(float(x) * 16.0 for x in re.findall(r"(\d+(?:\.\d+)?)rem", rule))
    return vals, "соглашение breakpoints каталога блоков site (" + str(REF_SITE.relative_to(kbpaths.kb())) + ")"


def _find_conventions(d):
    """Записи {id, rule} раздела соглашений каталога блоков."""
    if isinstance(d, dict):
        if "id" in d and "rule" in d:
            yield d
        for v in d.values():
            yield from _find_conventions(v)
    elif isinstance(d, list):
        for v in d:
            yield from _find_conventions(v)


def classes(widths, first_bp, overflow):
    """Ширины классов экрана по by_viewport: desktop — от первого брейкпоинта, mobile — ниже и вылет, any — все."""
    desk = [w for w in widths if w >= first_bp]
    mob = [w for w in widths if w < first_bp]
    return {"desktop": desk, "mobile": mob + ([overflow] if overflow else []),
            "any": list(widths) + ([overflow] if overflow else [])}


def theme_of_tweaks(copy_text):
    """Тема статичной копии по её твикам из строки происхождения: dark — при твике темы со значением dark."""
    m = re.search(r"твики: ([^>]*?) -->", copy_text or "")
    tw = dict(x.split("=", 1) for x in (m.group(1).split(", ") if m else []) if "=" in x)
    for k, v in tw.items():
        k, v = k.strip().lower(), v.strip().lower()
        if k in ("dark", "darkmode", "dark_mode", "dark-mode") and v == "true":
            return "dark"
        if k in ("theme", "mode", "scheme", "colorscheme", "color-scheme") and v in ("dark", "light"):
            return v
    return "light"


def frame_of(copy_text):
    m = re.search(r"рамка (\d+)×(\d+)", copy_text or "")
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def build_manifest(html_dir, canvas_dir=None, token_files=(), route="page", viewports=None, title="", rel=str):
    """Манифест kit по папке копий. viewports — {имя адаптивной копии: desktop | mobile | any}."""
    html_dir = Path(html_dir)
    aw = acceptance()
    ts = LT.load_tokens(token_files) if token_files else None
    bps = [int(round(b)) for b in (ts.breakpoints if ts else [])]
    bp_source = "токены ДС: " + ", ".join(rel(p) for p in token_files) if bps else ""
    if not bps:
        ref, bp_source = reference_breakpoints(route)
        bps = [int(round(b)) for b in ref]
    first_bp = min(bps) if bps else min(aw["artboards"] or [640])
    ds_themes = ts.themes if ts else ["light"]
    themes = [t for t in aw["themes"] if t in ds_themes] or ["light"]
    cls = classes(aw["widths"], first_bp, aw["overflow_only"])
    canvas = DC.load_canvas(canvas_dir) if canvas_dir and Path(canvas_dir).is_dir() else None
    statics, adaptive = [], []
    for p in sorted(html_dir.glob("*.html")):
        text = p.read_text(encoding="utf-8", errors="replace")
        src = DC.copy_source(text)
        if src:
            board = (canvas or {}).get("boards", {}).get(src) if canvas else None
            w, h = frame_of(text)
            statics.append({"file": p.name, "artboard": src, "w": w, "h": h, "theme": theme_of_tweaks(text),
                            "title": (board or {}).get("title") or src,
                            "stage": DC.stage_of(board, canvas) if canvas else None,
                            "order": canvas["order"].index(src) if canvas and src in canvas["order"] else 10 ** 6})
        else:
            vp = (viewports or {}).get(p.stem) or (viewports or {}).get(p.name) or "any"
            if vp not in CLASSES:
                raise ToolError(f"{p.name}: класс экрана {vp!r} не из {', '.join(CLASSES)}")
            adaptive.append({"file": p.name, "viewport": vp})
    statics.sort(key=lambda s: (s["order"], s["file"]))
    frames = []
    for s in statics:
        frames.append({"file": s["file"], "w": s["w"], "h": s["h"], "theme": s["theme"], "title": s["title"],
                       "kind": "static", "check": "artboard"})
    for a in adaptive:
        ws = cls[a["viewport"]]
        for th in themes:
            for w in ws:
                over = aw["overflow_only"] is not None and w == aw["overflow_only"] and w not in aw["widths"]
                if over and th != themes[0]:
                    continue
                frames.append({"file": a["file"], "w": w, "h": VIEW_H_WIDE if w >= first_bp else VIEW_H_NARROW,
                               "theme": th, "title": f"{Path(a['file']).stem} · {w} · {th}", "kind": "adaptive",
                               "check": "overflow" if over else "width"})
        lo = first_bp if a["viewport"] == "desktop" else 0
        hi = first_bp if a["viewport"] == "mobile" else 10 ** 6
        seen = {f["w"] for f in frames if f["file"] == a["file"]}
        for b in bps:
            for w in (b - 1, b + 1):
                if lo <= w < hi and w not in seen:
                    seen.add(w)
                    frames.append({"file": a["file"], "w": w, "h": VIEW_H_WIDE if w >= first_bp else VIEW_H_NARROW,
                                   "theme": themes[0], "title": f"{Path(a['file']).stem} · граница {b} ± 1 · {w}",
                                   "kind": "adaptive", "check": "reflow", "boundary": b})
    return {
        "title": (title or (canvas or {}).get("title") or html_dir.parent.name) + " — кадры kit",
        "source": {"acceptance_widths": "kb/common/acceptance-widths.yaml",
                   "acceptance_widths_sha256_16": aw["sha256_16"], "breakpoints": bp_source,
                   "themes": ("токены ДС" if ts else "нет токенов ДС — только светлая")},
        "widths": aw["widths"], "artboard_widths": aw["artboards"], "overflow_only": aw["overflow_only"],
        "themes": themes, "breakpoints": bps, "first_breakpoint": first_bp,
        "by_viewport": cls,
        "copies": {"static": [{k: s[k] for k in ("file", "artboard", "w", "h", "theme", "stage")} for s in statics],
                   "adaptive": adaptive},
        "artboards": frames,
    }


def dumps(man):
    return json.dumps(man, ensure_ascii=False, indent=1) + "\n"


# ------------------------------------------------------------------ проект

def screen_viewports(call):
    """Класс экрана адаптивных копий кабинета: поле viewport записи экрана (slug = имя копии)."""
    out = {}
    if not (call.surf and call.surf.app):
        return out
    base = docpaths.screens(call.slug, call.surface, "screens", repo=call.repo)
    for idx in sorted(base.glob("*/index.md")) if base.is_dir() else []:
        text = idx.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        if not m:
            continue
        try:
            fm = _yaml().safe_load(m.group(1)) or {}
        except Exception:  # noqa: BLE001 — запись с битым frontmatter разбирает аудит экранов
            continue
        vp = str(fm.get("viewport") or "").strip()
        if vp in CLASSES:
            out[idx.parent.name] = vp
    return out


def project_manifest(call):
    html_dir = docpaths.design(call.slug, "canvas-html", surface=call.surface, repo=call.repo)
    canvas_dir = docpaths.design(call.slug, "canvas-project", surface=call.surface, repo=call.repo)
    if not html_dir.is_dir():
        raise ToolError(f"нет HTML-копий: {docpaths.rel(html_dir, call.repo)} (dc_to_html build)")
    toks = []
    css = docpaths.design(call.slug, "tokens-css", repo=call.repo)
    dtcg = docpaths.design(call.slug, "tokens", repo=call.repo)
    art = docpaths.design(call.slug, "ds-project", repo=call.repo) / "tokens.json"
    toks = [css] if css.is_file() else [dtcg] if dtcg.is_file() else [art] if art.is_file() else []
    route = "app" if call.surf and call.surf.app else "page"
    man = build_manifest(html_dir, canvas_dir, toks, route, screen_viewports(call),
                         rel=lambda p: docpaths.rel(p, call.repo))
    return html_dir / NAME, man


def cmd_build(call):
    path, man = project_manifest(call)
    text = dumps(man)
    same = path.is_file() and path.read_text(encoding="utf-8") == text
    if not same:
        path.write_text(text, encoding="utf-8")
    res = {"path": docpaths.rel(path, call.repo), "written": not same, "frames": len(man["artboards"]),
           "themes": man["themes"], "breakpoints": man["breakpoints"]}
    print(json.dumps(res, ensure_ascii=False) if call.json else
          f"{res['path']}: {'записан' if not same else 'без изменений'}, кадров {res['frames']}, темы "
          f"{', '.join(res['themes'])}, границы {', '.join(str(b) for b in res['breakpoints'])}")
    return 0


def cmd_check(call):
    rep = FND.Report()
    html_dir = docpaths.design(call.slug, "canvas-html", surface=call.surface, repo=call.repo)
    if html_dir.is_dir() and any(html_dir.glob("*.html")):
        path, man = project_manifest(call)
        rel = docpaths.rel(path, call.repo)
        fix = f"kit_manifest build {call.slug} {call.surface} — манифест собирается из acceptance-widths.yaml"
        if not path.is_file():
            rep.add(RULE, "error", surface=call.surface, kind="kit", ref=NAME, path=rel,
                    message="нет манифеста kit.json у HTML-копий холста", fix=fix)
        elif path.read_text(encoding="utf-8") != dumps(man):
            rep.add(RULE, "error", surface=call.surface, kind="kit", ref=NAME, path=rel,
                    message="kit.json не равен сборке из acceptance-widths.yaml и копий: правлен руками или копии, "
                            "ширины либо токены ДС изменились", fix=fix)
    FND.print_findings(rep.items, as_json=call.json,
                       title=None if call.json else f"kit_manifest check {call.slug} {call.surface}")
    return rep.exit_code()


def cmd_make(a):
    vps = {}
    for it in a.viewport or []:
        k, sep, v = it.partition("=")
        if not sep:
            raise ToolError(f"--viewport: ожидается копия=класс, получено {it!r}")
        vps[k.strip()] = v.strip()
    man = build_manifest(a.html, a.canvas, a.tokens or [], a.route, vps)
    text = dumps(man)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(json.dumps({"path": a.out, "frames": len(man["artboards"])}, ensure_ascii=False) if a.json else a.out)
    else:
        sys.stdout.write(text)
    return 0


# ------------------------------------------------------------------ самопроверка

def selftest():
    import subprocess
    ok = True

    def check(name, got, want=True):
        nonlocal ok
        good = got == want
        ok &= good
        print(f"{'OK  ' if good else 'FAIL'} {name}" + ("" if good else f": {got!r} (ожидалось {want!r})"))

    aw = acceptance()
    check("ширины приёмки из файла", (aw["widths"], aw["artboards"], aw["overflow_only"]),
          ([1440, 1280, 1024, 768, 390, 360], [1440, 390], 320))
    check("классы экрана при первой границе 640", classes(aw["widths"], 640, 320),
          {"desktop": [1440, 1280, 1024, 768], "mobile": [390, 360, 320], "any": [1440, 1280, 1024, 768, 390, 360, 320]})
    check("эталон кабинета — токены ui", reference_breakpoints("app")[0], [640.0, 1024.0, 1440.0])
    check("эталон сайта — соглашение блоков site 40rem и 60rem", reference_breakpoints("page")[0], [640.0, 960.0])
    check("тема статичной копии по твику dark=true", theme_of_tweaks("· твики: dark=true -->"), "dark")
    check("тема без твика темы — светлая", theme_of_tweaks("· твики: accent=#2146D8, radius=6 -->"), "light")
    kbpaths.use("tests")
    import fixture_project
    with fixture_project.built("canvas") as fx:
        argv = [fx.slug, "promo", "--repo", str(fx.root)]
        dc = str(Path(DC.__file__))
        subprocess.run([sys.executable, dc, "build"] + argv, capture_output=True, text=True, check=True)
        html_dir = docpaths.design(fx.slug, "canvas-html", surface="promo", repo=fx.root)
        (html_dir / "home.html").write_text("<!doctype html><title>адаптивная копия</title>", encoding="utf-8")
        r = subprocess.run([sys.executable, __file__, "build"] + argv + ["--json"], capture_output=True, text=True)
        check("фикстура canvas: build — код 0", r.returncode, 0)
        man = json.loads((html_dir / NAME).read_text(encoding="utf-8"))
        st = [f for f in man["artboards"] if f["kind"] == "static"]
        check("восемь статичных кадров на ширине рамки", [(f["file"], f["w"]) for f in st][:3],
              [("Main.html", 1440), ("Landing-Phone.html", 390), ("Booking.html", 1440)])
        check("статичная Booking — тёмная по твику", next(f["theme"] for f in st if f["file"] == "Booking.html"), "dark")
        check("темы ДС артефакта: светлая и тёмная", man["themes"], ["light", "dark"])
        check("границы без токенов breakpoint — соглашение site", man["breakpoints"], [640, 960])
        ad = [f for f in man["artboards"] if f["kind"] == "adaptive"]
        widths = sorted({f["w"] for f in ad if f["check"] == "width"}, reverse=True)
        check("адаптивная копия: все ширины приёмки", widths, [1440, 1280, 1024, 768, 390, 360])
        check("адаптивная копия: вылет на 320 — один кадр", [f["w"] for f in ad if f["check"] == "overflow"], [320])
        check("адаптивная копия: темы на каждой ширине", len([f for f in ad if f["check"] == "width"]), 12)
        check("перестроение: границы ± 1 px", sorted(f["w"] for f in ad if f["check"] == "reflow"), [639, 641, 959, 961])
        check("высота окна: 900 широкое, 844 узкое", {f["w"]: f["h"] for f in ad if f["w"] in (1440, 390)},
              {1440: 900, 390: 844})
        r = subprocess.run([sys.executable, __file__, "check"] + argv + ["--json"], capture_output=True, text=True)
        check("check после build — 0 находок", (r.returncode, r.stdout), (0, ""))
        (html_dir / NAME).write_text((html_dir / NAME).read_text(encoding="utf-8").replace('"w": 1280', '"w": 1300'),
                                     encoding="utf-8")
        r = subprocess.run([sys.executable, __file__, "check"] + argv + ["--json"], capture_output=True, text=True)
        items = FND.parse_lines(r.stdout)
        check("правленый kit.json — R-FRESH-005 error", (r.returncode, [(f.rule, f.severity, f.ref) for f in items]),
              (1, [(RULE, "error", NAME)]))
        r1 = subprocess.run([sys.executable, __file__, "build"] + argv, capture_output=True, text=True)
        b1 = (html_dir / NAME).read_bytes()
        subprocess.run([sys.executable, __file__, "build"] + argv, capture_output=True, text=True)
        check("пересборка — те же байты", (r1.returncode, (html_dir / NAME).read_bytes() == b1), (0, True))
    with fixture_project.built("cabinet-ds") as fx:
        css = docpaths.design(fx.slug, "tokens-css", repo=fx.root)
        tmp = Path(fx.root) / "html"
        tmp.mkdir()
        (tmp / "requests-list.html").write_text("<!doctype html><title>экран</title>", encoding="utf-8")
        man = build_manifest(tmp, None, [css], "app", {"requests-list": "desktop"})
        ws = sorted({f["w"] for f in man["artboards"] if f["check"] == "width"}, reverse=True)
        check("кабинет, класс desktop: ширины от первой границы ДС 640", ws, [1440, 1280, 1024, 768])
        check("кабинет: границы из токенов breakpoint ДС", man["breakpoints"], [640, 1024, 1440])
        check("кабинет, desktop: перестроение только выше первой границы",
              sorted(f["w"] for f in man["artboards"] if f["check"] == "reflow"), [641, 1023, 1025, 1439, 1441])
        man_m = build_manifest(tmp, None, [css], "app", {"requests-list": "mobile"})
        check("кабинет, класс mobile: 390, 360 и вылет 320",
              sorted({f["w"] for f in man_m["artboards"] if f["check"] in ("width", "overflow")}, reverse=True),
              [390, 360, 320])
    print("selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------ вызов

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if argv[:1] == ["make"]:
            ap = argparse.ArgumentParser(prog="kit_manifest.py make", description="Манифест kit вне проекта.")
            ap.add_argument("cmd")
            ap.add_argument("html", help="папка HTML-копий")
            ap.add_argument("--canvas", help="папка исходников холста с canvas.json (подписи и порядок артбордов)")
            ap.add_argument("--tokens", action="append", help="токены ДС: брейкпоинты и темы; повтором")
            ap.add_argument("--route", choices=("page", "app"), default="page",
                            help="эталонные границы без токенов: page — блоки site, app — токены ui")
            ap.add_argument("--viewport", action="append", help="класс адаптивной копии: имя=desktop|mobile|any")
            ap.add_argument("--out")
            ap.add_argument("--json", action="store_true")
            return cmd_make(ap.parse_args(argv))
        ap = docpaths.parser("kit_manifest.py", __doc__, commands=("build", "check"), surface="required",
                             accept=lambda s: s.design)
        call = docpaths.parse(ap, argv)
        if call.selftest:
            return selftest()
        return {"build": cmd_build, "check": cmd_check}[call.command](call)
    except (ToolError, DC.ToolError, LT.ToolError) as e:
        print(f"kit_manifest: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
