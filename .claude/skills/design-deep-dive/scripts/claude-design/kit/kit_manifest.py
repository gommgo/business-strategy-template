#!/usr/bin/env python3
"""kit_manifest — манифест кадров `kit.json` статичных копий артбордов холста: кадр на копию, ряды — по ширинам.

Оригинал макета — холст в claude.ai. Статичные копии артбордов (`<Имя>.html`, перевод `dc_to_html.py`) и манифест
нужны скриптам проверок макета и собираются, когда заказчик попросил проверки (строка «Проверки макета: разрешены» в
ARTIFACTS.md; `references/claude-design.md § HTML-копии и kit`). Все ширины приёмки — артборды холста
(`kb/common/acceptance-widths.yaml#artboards`, набор задаёт заказчик в одном месте, NU-01), поэтому кадр — сама копия:
  - кадр статичной копии — на ширине и высоте её рамки, в теме её твиков (тёмная — при твике темы со значением dark), с
    подписью и этапом страницы холста из canvas.json;
  - `widths` манифеста — ширины артбордов из файла ширин: по ним `kit/canvas.html` раскладывает кадры рядами;
  - HTML без строки происхождения dc_to_html — не копия: кадра у него нет;
  - вылет на `overflow_only`, ресайз и зум проверяются на собранной странице в репозитории кода: кадров для них нет.
`kit/shot.py <canvas/html> <кадры> --manifest kit.json` снимает кадры по списку `artboards` манифеста (поля file, w, h,
theme, title). Манифест — производная: руками не правится, в нём нет даты — пересборка без изменений даёт те же байты.
Из Python (их читает вход холста): `classes(widths, first_bp, overflow)` — ширины классов экрана по `by_viewport` (NU-02:
`desktop` — от первого брейкпоинта ДС, `mobile` — ниже него и вылет, `any` — все и вылет; без overflow — без вылета),
`reference_breakpoints(route)` — эталонные границы без токенов ДС: кабинет — эталонные токены ui
(`kb/ui/14-recipes/examples/tokens.css`), сайт — соглашение `breakpoints` каталога блоков site
(`kb/site/04-blocks/blocks.yaml`).

Команды (файлы проекта — через lib/docpaths.py):
  kit_manifest.py build <slug> <surface> [--repo DIR] [--json]   пишет design/<surface>/canvas/html/kit.json
  kit_manifest.py check <slug> <surface> [--repo DIR] [--json]   R-FRESH-005: kit.json равен сборке из копий и ширин
  kit_manifest.py make <папка копий> [--canvas ПАПКА] [--out ФАЙЛ] [--json]   вне проекта; без --out — в stdout
  kit_manifest.py --selftest                                      на фикстуре canvas (пример базы), без сети
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

kbpaths.use("project")
import findings as FND  # noqa: E402

RULE = "R-FRESH-005"
WIDTHS = kbpaths.kb(None, "common", "acceptance-widths.yaml")
REF_UI = kbpaths.kb("ui", "14-recipes", "examples", "tokens.css")
REF_SITE = kbpaths.kb("site", "04-blocks", "blocks.yaml")
NAME = "kit.json"


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


def build_manifest(html_dir, canvas_dir=None, title=""):
    """Манифест kit по папке копий: кадр на статичную копию артборда в порядке canvas.json (без него — по имени)."""
    html_dir = Path(html_dir)
    aw = acceptance()
    canvas = DC.load_canvas(canvas_dir) if canvas_dir and Path(canvas_dir).is_dir() else None
    statics = []
    for p in sorted(html_dir.glob("*.html")):
        text = p.read_text(encoding="utf-8", errors="replace")
        src = DC.copy_source(text)
        if not src:
            continue
        board = (canvas or {}).get("boards", {}).get(src) if canvas else None
        w, h = frame_of(text)
        statics.append({"file": p.name, "artboard": src, "w": w, "h": h, "theme": theme_of_tweaks(text),
                        "title": (board or {}).get("title") or src,
                        "stage": DC.stage_of(board, canvas) if canvas else None,
                        "order": canvas["order"].index(src) if canvas and src in canvas["order"] else 10 ** 6})
    statics.sort(key=lambda s: (s["order"], s["file"]))
    return {
        "title": (title or (canvas or {}).get("title") or html_dir.parent.name) + " — кадры kit",
        "source": {"acceptance_widths": "kb/common/acceptance-widths.yaml",
                   "acceptance_widths_sha256_16": aw["sha256_16"]},
        "widths": aw["artboards"],
        "artboards": [{k: s[k] for k in ("file", "artboard", "w", "h", "theme", "title", "stage")} for s in statics],
    }


def dumps(man):
    return json.dumps(man, ensure_ascii=False, indent=1) + "\n"


# ------------------------------------------------------------------ проект

def project_manifest(call):
    html_dir = docpaths.design(call.slug, "canvas-html", surface=call.surface, repo=call.repo)
    canvas_dir = docpaths.design(call.slug, "canvas-project", surface=call.surface, repo=call.repo)
    if not html_dir.is_dir():
        raise ToolError(f"нет HTML-копий: {docpaths.rel(html_dir, call.repo)} (dc_to_html build)")
    return html_dir / NAME, build_manifest(html_dir, canvas_dir)


def has_copies(html_dir):
    """В папке есть статичные копии артбордов (строка происхождения dc_to_html)."""
    return html_dir.is_dir() and any(DC.copy_source(p.read_text(encoding="utf-8", errors="replace"))
                                     for p in html_dir.glob("*.html"))


def cmd_build(call):
    path, man = project_manifest(call)
    text = dumps(man)
    same = path.is_file() and path.read_text(encoding="utf-8") == text
    if not same:
        path.write_text(text, encoding="utf-8")
    res = {"path": docpaths.rel(path, call.repo), "written": not same, "frames": len(man["artboards"]),
           "widths": man["widths"]}
    print(json.dumps(res, ensure_ascii=False) if call.json else
          f"{res['path']}: {'записан' if not same else 'без изменений'}, кадров {res['frames']}, ширины артбордов "
          f"{', '.join(str(w) for w in res['widths'])}")
    return 0


def cmd_check(call):
    rep = FND.Report()
    html_dir = docpaths.design(call.slug, "canvas-html", surface=call.surface, repo=call.repo)
    if has_copies(html_dir):
        path, man = project_manifest(call)
        rel = docpaths.rel(path, call.repo)
        fix = f"kit_manifest build {call.slug} {call.surface} — манифест собирается из копий и acceptance-widths.yaml"
        if not path.is_file():
            rep.add(RULE, "error", surface=call.surface, kind="kit", ref=NAME, path=rel,
                    message="нет манифеста kit.json у статичных копий артбордов", fix=fix)
        elif path.read_text(encoding="utf-8") != dumps(man):
            rep.add(RULE, "error", surface=call.surface, kind="kit", ref=NAME, path=rel,
                    message="kit.json не равен сборке из копий и acceptance-widths.yaml: правлен руками или копии либо "
                            "файл ширин изменились", fix=fix)
    FND.print_findings(rep.items, as_json=call.json,
                       title=None if call.json else f"kit_manifest check {call.slug} {call.surface}")
    return rep.exit_code()


def cmd_make(a):
    man = build_manifest(a.html, a.canvas)
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
    six = [1440, 1280, 1024, 768, 390, 360]
    check("ширины приёмки из файла: артборды — все ширины приёмки, вылет на 320",
          (aw["widths"], aw["artboards"], aw["overflow_only"]), (six, six, 320))
    check("классы экрана при первой границе 640 без вылета — артборды класса (вход холста)",
          classes(aw["artboards"], 640, None),
          {"desktop": [1440, 1280, 1024, 768], "mobile": [390, 360], "any": six})
    check("классы экрана с вылетом на 320", classes(aw["widths"], 640, 320),
          {"desktop": [1440, 1280, 1024, 768], "mobile": [390, 360, 320], "any": six + [320]})
    check("эталон кабинета — токены ui", reference_breakpoints("app")[0], [640.0, 1024.0, 1440.0])
    check("эталон сайта — соглашение блоков site 40rem и 60rem", reference_breakpoints("page")[0], [640.0, 960.0])
    check("тема статичной копии по твику dark=true", theme_of_tweaks("· твики: dark=true -->"), "dark")
    check("тема без твика темы — светлая", theme_of_tweaks("· твики: accent=#2146D8, radius=6 -->"), "light")
    kbpaths.use("tests")
    import fixture_project
    with fixture_project.built("canvas") as fx:
        argv = [fx.slug, "promo", "--repo", str(fx.root)]
        html_dir = docpaths.design(fx.slug, "canvas-html", surface="promo", repo=fx.root)
        r = subprocess.run([sys.executable, __file__, "check"] + argv + ["--json"], capture_output=True, text=True)
        check("копий нет — check без находок: манифест нужен только копиям", (r.returncode, r.stdout), (0, ""))
        dc = str(Path(DC.__file__))
        subprocess.run([sys.executable, dc, "build"] + argv, capture_output=True, text=True, check=True)
        (html_dir / "home.html").write_text("<!doctype html><title>страница</title>", encoding="utf-8")
        r = subprocess.run([sys.executable, __file__, "build"] + argv + ["--json"], capture_output=True, text=True)
        check("фикстура canvas: build — код 0", r.returncode, 0)
        man = json.loads((html_dir / NAME).read_text(encoding="utf-8"))
        fr = man["artboards"]
        check("манифест — заголовок, источник, ширины артбордов и кадры; полей кадров вылета и классов нет",
              sorted(man), ["artboards", "source", "title", "widths"])
        check("ширины манифеста — артборды файла ширин (ряды canvas.html)", man["widths"], aw["artboards"])
        check("кадры — восемь статичных копий в порядке canvas.json, на ширине рамки",
              (len(fr), [(f["file"], f["w"]) for f in fr][:3]),
              (8, [("Main.html", 1440), ("Landing-Phone.html", 390), ("Booking.html", 1440)]))
        check("HTML без строки происхождения — не кадр", any(f["file"] == "home.html" for f in fr), False)
        check("вылета на 320 нет: ширины кадров — ширины рамок копий", sorted({f["w"] for f in fr}), [390, 880, 1440])
        check("статичная Booking — тёмная по твику", next(f["theme"] for f in fr if f["file"] == "Booking.html"), "dark")
        check("этап и артборд кадра — из canvas.json и строки происхождения",
              {f["file"]: (f["artboard"], f["stage"]) for f in fr if f["file"] in ("Dir-Paper.html", "Main.html")},
              {"Dir-Paper.html": ("Dir-Paper.dc.html", "directions"), "Main.html": ("Main.dc.html", "mockup")})
        r = subprocess.run([sys.executable, __file__, "check"] + argv + ["--json"], capture_output=True, text=True)
        check("check после build — 0 находок", (r.returncode, r.stdout), (0, ""))
        (html_dir / NAME).write_text((html_dir / NAME).read_text(encoding="utf-8").replace('"w": 390', '"w": 400'),
                                     encoding="utf-8")
        r = subprocess.run([sys.executable, __file__, "check"] + argv + ["--json"], capture_output=True, text=True)
        items = FND.parse_lines(r.stdout)
        check("правленый kit.json — R-FRESH-005 error", (r.returncode, [(f.rule, f.severity, f.ref) for f in items]),
              (1, [(RULE, "error", NAME)]))
        r1 = subprocess.run([sys.executable, __file__, "build"] + argv, capture_output=True, text=True)
        b1 = (html_dir / NAME).read_bytes()
        subprocess.run([sys.executable, __file__, "build"] + argv, capture_output=True, text=True)
        check("пересборка — те же байты", (r1.returncode, (html_dir / NAME).read_bytes() == b1), (0, True))
        canvas_dir = docpaths.design(fx.slug, "canvas-project", surface="promo", repo=fx.root)
        r = subprocess.run([sys.executable, __file__, "make", str(html_dir), "--canvas", str(canvas_dir)],
                           capture_output=True, text=True)
        check("make вне проекта — тот же манифест в stdout", (r.returncode, r.stdout),
              (0, (html_dir / NAME).read_text(encoding="utf-8")))
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
            ap.add_argument("--out")
            ap.add_argument("--json", action="store_true")
            return cmd_make(ap.parse_args(argv))
        ap = docpaths.parser("kit_manifest.py", __doc__, commands=("build", "check"), surface="required",
                             accept=lambda s: s.design)
        call = docpaths.parse(ap, argv)
        if call.selftest:
            return selftest()
        return {"build": cmd_build, "check": cmd_check}[call.command](call)
    except (ToolError, DC.ToolError) as e:
        print(f"kit_manifest: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
