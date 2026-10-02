#!/usr/bin/env python3
"""split_recraft.py — нарезка листа иконок SVG (Recraft) на отдельные файлы по ячейкам сетки.

Лист — плоский список <path/>: набор иконок одной генерацией; лист с группами <g> или другими фигурами — отказ. Сетку
и имена даёт задание: --grid — колонки и строки листа, --names — имена иконок из спецификации по ячейкам слева направо
и сверху вниз («-» — пустая ячейка). Путь относится к ячейке, в которую попал центр его рамки, поэтому части одной
иконки остаются вместе на любом расстоянии друг от друга. Фон — путь на весь лист — в иконки не идёт. У иконки свой
квадратный viewBox по рамке её путей с полем, имя файла — <префикс><имя>.svg. Мастер листа кладётся в
OUT_DIR/_source/: манифест происхождения из его <metadata> в иконки не копируется (подпись производной
недействительна), в каждой иконке — <desc> о происхождении. После записи — svgo --multipass, если он установлен.

Запись — только когда лист сошёлся с заданием: в каждой названной ячейке есть пути, в пустых путей нет. Файл с таким
именем уже есть — отказ без записи; --on-exists suffix — записать рядом с суффиксом -2, -3, …

  split_recraft.py SHEET.svg OUT_DIR --grid 4x2 --names home,search,cart,user,menu,close,-,back
                   [--prefix icon-] [--on-exists refuse|suffix] [--origin ТЕКСТ] [--no-svgo]
  split_recraft.py --selftest          самопроверка на вымышленном листе: без сети и без svgo

Нужен svgelements (Python окружения скилла); svgo — из $DDD_HOME/node.
Код выхода: 0 — нарезано, файлов столько же, сколько названных ячеек; 1 — лист не сошёлся с заданием, ничего не
записано; 2 — ошибка вызова или окружения; 3 — файл с таким именем уже есть, ничего не записано.
"""
import argparse
import contextlib
import html
import io
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))  # scripts/lib: kbpaths
import kbpaths  # noqa: E402

FIELD = 1.12            # сторона viewBox иконки к большей стороне рамки её путей: поле 6 % с каждой стороны
BG_SHARE = 0.9          # путь шире и выше этой доли листа — фон
ORIGIN = "ИИ-генерация (trainedAlgorithmicMedia)"
SVG_NS = 'xmlns="http://www.w3.org/2000/svg"'
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
PATH_RE = re.compile(r"<path\b[^>]*?(?:/>|>\s*</path>)", re.S)
EXIT_MISMATCH, EXIT_USAGE, EXIT_EXISTS = 1, 2, 3


class Refuse(Exception):
    """Отказ с кодом выхода: 1 — лист не сошёлся с заданием, 2 — вызов или окружение, 3 — имя файла занято."""

    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def parse_grid(s):
    """«4x2» → (колонок, строк); разделитель — латинская x, кириллическая х или знак ×."""
    m = re.fullmatch(r"\s*(\d+)\s*[xх×]\s*(\d+)\s*", str(s))
    if not m or not int(m.group(1)) or not int(m.group(2)):
        raise Refuse(EXIT_USAGE, f"--grid {s!r}: нужны колонки и строки листа, например 4x2")
    return int(m.group(1)), int(m.group(2))


def parse_names(s, cells):
    """Имена по ячейкам: имя на ячейку, «-» — пустая; имя — латиница, цифры, «.», «_», «-», без повторов."""
    names = [n.strip() for n in str(s).split(",")]
    if len(names) != cells:
        raise Refuse(EXIT_USAGE, f"--names: имён {len(names)}, ячеек сетки {cells} — имя на ячейку, «-» — пустая ячейка")
    used = [n for n in names if n != "-"]
    bad = [n for n in used if not NAME_RE.fullmatch(n)]
    if bad:
        raise Refuse(EXIT_USAGE, "--names: имя файла — латиница, цифры, «.», «_», «-»: " + ", ".join(repr(n) for n in bad))
    dup = sorted({n for n in used if used.count(n) > 1})
    if dup:
        raise Refuse(EXIT_USAGE, "--names: имя повторяется: " + ", ".join(dup))
    if not used:
        raise Refuse(EXIT_USAGE, "--names: все ячейки пустые — резать нечего")
    return names


def read_sheet(src):
    """Лист → (viewBox, атрибуты xmlns корня, блок <defs>, [(рамка, тег пути)]); рамки — в единицах viewBox, фон —
    путь на весь лист — отброшен."""
    try:
        from svgelements import SVG, Path as SvgPath
    except ImportError as e:
        raise Refuse(EXIT_USAGE, f"нет модуля svgelements ({e}) — запускайте Python окружения скилла")
    try:
        raw = Path(src).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise Refuse(EXIT_USAGE, f"лист не читается: {e}")
    root = re.search(r"<svg\b[^>]*>", raw)
    vbm = re.search(r'\bviewBox="([^"]+)"', root.group(0)) if root else None
    vb = [float(v) for v in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", vbm.group(1))] if vbm else []
    if len(vb) != 4 or vb[2] <= 0 or vb[3] <= 0:
        raise Refuse(EXIT_USAGE, f"{src}: у листа нет viewBox — сетку не к чему привязать")
    if re.search(r"<g\b", raw):
        raise Refuse(EXIT_USAGE, f"{src}: в листе группы <g> — нарезка рассчитана на плоский список <path/>: атрибуты "
                                 f"групп в иконки не попали бы")
    other = sorted(set(re.findall(r"<(circle|rect|ellipse|polygon|polyline|line|text|image|use)\b", raw)))
    if other:
        raise Refuse(EXIT_USAGE, f"{src}: в листе есть <{'>, <'.join(other)}> — нарезка берёт только <path/>: эти "
                                 f"фигуры в иконки не попали бы")
    tags = PATH_RE.findall(raw)
    # без viewBox и размеров корня svgelements не пересчитывает координаты во вьюпорт: рамки — в единицах тегов
    bare = raw.replace(root.group(0),
                       re.sub(r'\s(viewBox|width|height|preserveAspectRatio)="[^"]*"', "", root.group(0)), 1)
    try:
        paths = [e for e in SVG.parse(io.BytesIO(bare.encode("utf-8"))).elements() if isinstance(e, SvgPath)]
    except Exception as e:                              # noqa: BLE001 — разбор чужого файла: любая ошибка — отказ
        raise Refuse(EXIT_USAGE, f"{src}: SVG не разбирается: {e}")
    if len(paths) != len(tags):
        raise Refuse(EXIT_USAGE, f"{src}: путей в разборе {len(paths)}, тегов <path> {len(tags)} — лист не плоский "
                                 f"список путей")
    items = []
    for p, t in zip(paths, tags):
        bb = p.bbox()
        if bb is None:
            continue
        if bb[2] - bb[0] > BG_SHARE * vb[2] and bb[3] - bb[1] > BG_SHARE * vb[3]:
            continue                                    # фон: путь на весь лист
        items.append((bb, t))
    xmlns = " ".join(re.findall(r'xmlns(?::[\w-]+)?="[^"]*"', root.group(0))) or SVG_NS
    return vb, xmlns, "".join(re.findall(r"<defs\b.*?</defs>", raw, re.S)), items


def where(i, cols):
    return f"строка {i // cols + 1}, колонка {i % cols + 1}"


def cut(vb, items, cols, rows, names):
    """Пути по ячейкам сетки → ({номер ячейки: [(рамка, тег)]}, [расхождения листа с заданием]). Ячейка пути — по
    центру его рамки; номер — по строкам слева направо."""
    cw, ch = vb[2] / cols, vb[3] / rows
    cells = {}
    for bb, t in items:
        c = min(cols - 1, max(0, int(((bb[0] + bb[2]) / 2 - vb[0]) // cw)))
        r = min(rows - 1, max(0, int(((bb[1] + bb[3]) / 2 - vb[1]) // ch)))
        cells.setdefault(r * cols + c, []).append((bb, t))
    issues = []
    for i, n in enumerate(names):
        if n == "-" and cells.get(i):
            issues.append(f"в пустой ячейке ({where(i, cols)}) путей {len(cells[i])} — у задания здесь нет имени")
        elif n != "-" and not cells.get(i):
            issues.append(f"в ячейке «{n}» ({where(i, cols)}) нет путей")
    return cells, issues


def icon_svg(group, xmlns, defs, desc):
    """Иконка: квадратный viewBox по рамке путей группы с полем FIELD, <desc> о происхождении, теги путей как в листе."""
    x0, y0 = min(b[0] for b, _ in group), min(b[1] for b, _ in group)
    x1, y1 = max(b[2] for b, _ in group), max(b[3] for b, _ in group)
    side = max(x1 - x0, y1 - y0) * FIELD or 1.0
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return (f'<svg {xmlns} viewBox="{mx - side / 2:.1f} {my - side / 2:.1f} {side:.1f} {side:.1f}">'
            f"<desc>{html.escape(desc)}</desc>{defs}" + "".join(t for _, t in group) + "</svg>\n")


def free_name(path, taken=()):
    """Свободное имя рядом с занятым: <имя>-2, <имя>-3, …"""
    n = 2
    while True:
        cand = path.with_name(f"{path.stem}-{n}{path.suffix}")
        if not cand.exists() and cand not in taken:
            return cand
        n += 1


def run_svgo(path):
    """svgo --multipass поверх файла; svgo не установлен — файл остаётся как записан."""
    exe = kbpaths.node_modules(".bin", "svgo")
    if not exe.exists():
        return False
    r = subprocess.run([str(exe), str(path), "-o", str(path), "--multipass", "-q"], env=kbpaths.node_env(), check=False)
    return r.returncode == 0


def split(src, out, cols, rows, names, prefix="", on_exists="refuse", origin=ORIGIN, svgo=True):
    """Нарезать лист src в папку out. Возвращает записанные иконки [{name, file, cell, paths, bytes_raw, bytes}];
    отказ — Refuse с кодом выхода, до отказа ничего не записано."""
    src, out = Path(src), Path(out)
    vb, xmlns, defs, items = read_sheet(src)
    cells, issues = cut(vb, items, cols, rows, names)
    if issues:
        raise Refuse(EXIT_MISMATCH, "лист не сошёлся с заданием, ничего не записано:\n  " + "\n  ".join(issues))
    plan = [(i, n, out / f"{prefix}{n}.svg") for i, n in enumerate(names) if n != "-"]
    master = out / "_source" / src.name
    same_master = master.exists() and master.read_bytes() == src.read_bytes()
    busy = [p for _, _, p in plan if p.exists()] + ([master] if master.exists() and not same_master else [])
    if busy and on_exists != "suffix":
        raise Refuse(EXIT_EXISTS, "файл с таким именем уже есть, ничего не записано (--on-exists suffix — записать рядом "
                                  "с суффиксом):\n  " + "\n  ".join(str(p) for p in busy))
    taken = set()
    for k, (i, n, p) in enumerate(plan):
        p = free_name(p, taken) if p.exists() else p
        taken.add(p)
        plan[k] = (i, n, p)
    if not same_master:
        master = free_name(master) if master.exists() else master
        master.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, master)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for i, n, p in plan:
        desc = f"{origin}; иконка «{n}» — {where(i, cols)} листа {src.name}; мастер листа — _source/{master.name}"
        p.write_text(icon_svg(cells[i], xmlns, defs, desc), encoding="utf-8")
        raw = p.stat().st_size
        packed = run_svgo(p) if svgo else False
        written.append({"name": n, "file": str(p), "cell": [i // cols + 1, i % cols + 1], "paths": len(cells[i]),
                        "bytes_raw": raw, "bytes": p.stat().st_size, "svgo": packed})
    return written


# ================================================================ selftest

SELFTEST_SHEET = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="100 50 600 400" width="300" height="200">
<metadata>манифест происхождения листа</metadata>
<path d="M100 50h600v400h-600z" fill="#F4F1EA"/>
<path d="M110 60h20v20h-20z" fill="#1B2A3A"/>
<path d="M260 210h30v30h-30z" fill="#1B2A3A"/>
<path d="M0 0h40v40h-40z" transform="translate(380 130)" fill="#C2542D"/>
<path d="M310 60h10v10h-10z" fill="#1B2A3A"/>
<path d="M560 110l60 0 0 60 -60 0z" fill="#1B2A3A"/>
<path d="M350 300h100v100h-100z" fill="#1B2A3A"/>
<path d="M320 270h10v10h-10z" fill="#C2542D"></path>
<path d="M520 280h160v40h-160z" fill="#1B2A3A"/>
</svg>
"""                                                     # сетка 3×2, ячейка 200×200; строка 2, колонка 1 — пустая


def selftest():
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    def run(*argv):
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            try:
                rc = main(list(argv))
            except SystemExit as e:                     # argparse: ошибка вызова
                rc = e.code
        return rc, err.getvalue()

    def svgs(d):
        return sorted(p.name for p in Path(d).glob("*.svg")) if Path(d).is_dir() else []

    names = "home,search,cart,-,user,menu"
    with tempfile.TemporaryDirectory(prefix="split_recraft_") as td:
        t = Path(td)
        sheet = t / "sheet.svg"
        sheet.write_text(SELFTEST_SHEET, encoding="utf-8")
        base = [str(sheet), str(t / "icons"), "--grid", "3x2", "--no-svgo"]
        rc, _ = run(*base, "--names", names)
        files = svgs(t / "icons")
        check("лист 3×2 с одной пустой ячейкой: файлов столько же, сколько названных ячеек (5), имена — из задания",
              rc == 0 and files == ["cart.svg", "home.svg", "menu.svg", "search.svg", "user.svg"])
        text = {n: (t / "icons" / n).read_text(encoding="utf-8") for n in files}
        check("части иконки на расстоянии больше половины ячейки — в одном файле; фон листа в иконки не идёт",
              rc == 0 and text["home.svg"].count("<path") == 2 and "M260 210" in text["home.svg"]
              and not any("h600v400" in x for x in text.values()))
        check("путь с transform — в ячейке по рамке после преобразования; тег с закрывающим </path> взят целиком",
              rc == 0 and "translate(380 130)" in text["search.svg"] and text["search.svg"].count("<path") == 2
              and text["user.svg"].count("<path") == 2 and "</path>" in text["user.svg"])
        check("viewBox иконки — квадрат по рамке путей с полем, в единицах viewBox листа (размеры корня не влияют)",
              rc == 0 and 'viewBox="510.4 210.4 179.2 179.2"' in text["menu.svg"])
        check("в иконке — <desc> с именем, ячейкой и мастером; манифест листа не копируется, мастер — в _source/",
              rc == 0 and "иконка «menu» — строка 2, колонка 3 листа sheet.svg" in text["menu.svg"]
              and ORIGIN in text["menu.svg"] and "<metadata" not in text["menu.svg"]
              and (t / "icons" / "_source" / "sheet.svg").read_bytes() == sheet.read_bytes())
        (t / "icons" / "home.svg").write_text("занято", encoding="utf-8")
        rc, err = run(*base, "--names", names)
        check("повтор в ту же папку — отказ с кодом 3: ничего не записано, занятый файл цел",
              rc == EXIT_EXISTS and svgs(t / "icons") == files and "home.svg" in err
              and (t / "icons" / "home.svg").read_text(encoding="utf-8") == "занято")
        rc, _ = run(*base, "--names", names, "--on-exists", "suffix")
        check("--on-exists suffix — иконки рядом с суффиксом -2, занятые файлы целы, одинаковый мастер не дублируется",
              rc == 0 and svgs(t / "icons") == sorted(files + [n.replace(".svg", "-2.svg") for n in files])
              and (t / "icons" / "home.svg").read_text(encoding="utf-8") == "занято"
              and [p.name for p in (t / "icons" / "_source").iterdir()] == ["sheet.svg"])
        rc, err = run(str(sheet), str(t / "a"), "--grid", "3x2", "--no-svgo", "--names", "home,search,cart,extra,user,menu")
        check("названная ячейка без путей — код 1, ничего не записано", rc == EXIT_MISMATCH and not (t / "a").exists()
              and "extra" in err)
        rc, err = run(str(sheet), str(t / "b"), "--grid", "3x2", "--no-svgo", "--names", "home,-,cart,-,user,menu")
        check("пути в ячейке без имени — код 1, ничего не записано", rc == EXIT_MISMATCH and not (t / "b").exists()
              and "строка 1, колонка 2" in err)
        rc, _ = run(str(sheet), str(t / "c"), "--grid", "3x2", "--no-svgo", "--names", names, "--prefix", "icon-")
        check("--prefix — префикс имени файла", rc == 0 and "icon-home.svg" in svgs(t / "c") and len(svgs(t / "c")) == 5)
        codes = [run(str(sheet), str(t / "d"), "--grid", g, "--no-svgo", "--names", n)[0] for g, n in
                 (("3x2", "home,search"), ("0x2", names), ("3x2", "home,home,cart,-,user,menu"),
                  ("3x2", "home,../x,cart,-,user,menu"), ("3x2", "-,-,-,-,-,-"))]
        grouped = t / "grouped.svg"
        grouped.write_text(SELFTEST_SHEET.replace("<path d=\"M110", "<g fill=\"red\"><path d=\"M110", 1)
                           .replace("</svg>", "</g></svg>"), encoding="utf-8")
        shaped = t / "shaped.svg"
        shaped.write_text(SELFTEST_SHEET.replace("</svg>", '<circle cx="600" cy="150" r="20"/></svg>'), encoding="utf-8")
        codes += [run(str(grouped), str(t / "d"), "--grid", "3x2", "--no-svgo", "--names", names)[0],
                  run(str(shaped), str(t / "d"), "--grid", "3x2", "--no-svgo", "--names", names)[0],
                  run(str(t / "нет.svg"), str(t / "d"), "--grid", "3x2", "--no-svgo", "--names", names)[0],
                  run(str(sheet), str(t / "d"), "--grid", "3x2")[0]]
        check("ошибки вызова — код 2: число имён, сетка, повтор имени, имя с путём, все ячейки пустые, лист с группами, "
              f"лист с фигурой не <path>, нет листа, нет --names — {codes}",
              codes == [EXIT_USAGE] * 9 and not (t / "d").exists())
    print("split_recraft selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


# ================================================================ main

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet", help="лист иконок SVG")
    ap.add_argument("out", help="папка иконок; мастер листа — в OUT_DIR/_source/")
    ap.add_argument("--grid", required=True, help="сетка листа: КОЛОНКИxСТРОКИ, например 4x2")
    ap.add_argument("--names", required=True,
                    help="имена иконок по ячейкам слева направо и сверху вниз, через запятую; «-» — пустая ячейка")
    ap.add_argument("--prefix", default="", help="префикс имени файла")
    ap.add_argument("--on-exists", choices=["refuse", "suffix"], default="refuse",
                    help="файл с таким именем уже есть: refuse — отказ без записи, suffix — запись с суффиксом -2, -3, …")
    ap.add_argument("--origin", default=ORIGIN, help="происхождение листа для <desc> иконок: модель, канал")
    ap.add_argument("--no-svgo", action="store_true", help="не сжимать иконки svgo")
    a = ap.parse_args(argv)
    try:
        cols, rows = parse_grid(a.grid)
        names = parse_names(a.names, cols * rows)
        if a.prefix and not NAME_RE.fullmatch(a.prefix):
            raise Refuse(EXIT_USAGE, f"--prefix {a.prefix!r}: латиница, цифры, «.», «_», «-»")
        written = split(a.sheet, a.out, cols, rows, names, a.prefix, a.on_exists, a.origin, not a.no_svgo)
    except Refuse as e:
        print(str(e), file=sys.stderr)
        return e.code
    for w in written:
        size = f"{w['bytes_raw']} → {w['bytes']} Б" if w["svgo"] else f"{w['bytes']} Б"
        print(f"{Path(w['file']).name}: строка {w['cell'][0]}, колонка {w['cell'][1]}, путей {w['paths']}, {size}")
    if not a.no_svgo and not all(w["svgo"] for w in written):
        print("svgo не отработал — иконки записаны без сжатия", file=sys.stderr)
    print(f"нарезано: файлов {len(written)}, названных ячеек {len(written)} → {a.out}; мастер листа — в _source/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
