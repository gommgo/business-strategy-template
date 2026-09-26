#!/usr/bin/env python3
"""build_pairs.py — собрать pairs.json и img/ страницы «Кадр против кадра» из кадров судьи предметов (оркестратор, сессия 2, 26.09.2026).

    python3 build_pairs.py --check      # только показать, каких кадров не хватает (ничего не пишет)
    python3 build_pairs.py              # собрать: img/pNN-1.jpg / pNN-2.jpg (+ .webm), pairs.json; старые пробные пары — pairs-test.json

Пары — таблица PAIRS ниже: вопрос (craft / page / motion), вид (image / video), два варианта (подпись + кандидаты путей относительно
15-showcase; берётся первый существующий). Слепо: имена в img/ нейтральные (номер пары), какой вариант слева — решает страница
(каждая пара в двух порядках), подписи вариантов видны только в итогах. Картинки пары сводятся к одному размеру (меньшему из двух,
с сохранением пропорций и полями цвета фона при разном аспекте) — якоря класса сняты 1024×640, наши кадры к ним уменьшаются так же.
Пара без обоих файлов пропускается и печатается в отчёте. Против якорей — два вопроса (идея concept и ремесло craft) для правила L2
плана «победа или ничья в ≥ 2 из 3 (concept, craft, motion)»; записей движения якорей нет (живые сайты без согласия не снимаем).
Правки по отсеву ИИ-судьи (vote/ai-screen.md, 26.09 06:40): у клавиатуры первые экраны B и C побайтно одинаковы (у C постер Cycles) —
пары k-first-bc/k-mob-bc/k-first-ac сняты, вместо них разборка A↔C и сцена набора B↔C; у «Сдано» A нет ряда приборов — пара
s-icons-ab спрашивает про блок страницы (page); у Velmora подписи страниц называют вариант — пара «первый экран» снята, запись
движения обрезана до области сцены (velmora/judge/vote/*-stage.webm, crop 872×740+568+60).
"""
import json
import os
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
SHOW = str(kbpaths.kb("blender", "15-showcase"))  # перенос: кадры испытания — kb
R = os.path.dirname(SHOW)
SITES = os.path.join(R, "99-raw", "experiments", "A", "sites")
OUT_IMG = os.path.join(HERE, "img")
MAXW = 1600

QUESTIONS = {
    "concept": "Где сильнее идея — что 3D показывает о продукте и зачем оно здесь?",
    "craft": "Какой кадр выглядит дороже, чётче и убедительнее?",
    "page": "Какой первый экран сильнее как сайт?",
    "motion": "Где движение лучше?",
}


def J(subject, name):
    return f"{subject}/judge/{name}"


def site(name):
    return os.path.relpath(os.path.join(SITES, name, "shot_0.jpg"), SHOW)


# (id, группа, вопрос, вид, (подпись A, [кандидаты A]), (подпись B, [кандидаты B]))
PAIRS = [
    # «Звено» — запуск продукта L2: A код v3, B Blender (предрендер), C гибрид; база v2; якорь hubtown
    ("z-hero-ab", "«Звено» · главный кадр", "craft", "image",
     ("A код", [J("zveno", "a-code__hero.png")]), ("B Blender", [J("zveno", "b-blender__hero.png")])),
    ("z-hero-bc", "«Звено» · главный кадр", "craft", "image",
     ("B Blender", [J("zveno", "b-blender__hero.png")]), ("C гибрид", [J("zveno", "c-hybrid__hero.png")])),
    ("z-hero-ac", "«Звено» · главный кадр", "craft", "image",
     ("A код", [J("zveno", "a-code__hero.png")]), ("C гибрид", [J("zveno", "c-hybrid__hero.png")])),
    ("z-v2-a", "«Звено» · главный кадр", "craft", "image",
     ("v2 база", [J("zveno", "v2-base__hero.png")]), ("A код", [J("zveno", "a-code__hero.png")])),
    ("z-scan-ab", "«Звено» · скан сустава", "craft", "image",
     ("A код", [J("zveno", "a-code__scan-half.png")]), ("B Blender", [J("zveno", "b-blender__scan-half.png")])),
    ("z-inside-ab", "«Звено» · сустав изнутри", "craft", "image",
     ("A код", [J("zveno", "a-code__inside.png")]), ("B Blender", [J("zveno", "b-blender__inside.png")])),
    ("z-exploded-ac", "«Звено» · разборка", "craft", "image",
     ("A код", [J("zveno", "a-code__exploded.png")]), ("C гибрид", [J("zveno", "c-hybrid__exploded.png")])),
    ("z-exploded-bc", "«Звено» · разборка", "craft", "image",
     ("B Blender", [J("zveno", "b-blender__exploded.png")]), ("C гибрид", [J("zveno", "c-hybrid__exploded.png")])),
    ("z-motion-bc", "«Звено» · движение 10 с", "motion", "video",
     ("B Blender", [J("zveno", "b-blender__scroll-10s.webm"), J("zveno", "b-blender__story-10s.webm")]),
     ("C гибрид", [J("zveno", "c-hybrid__ik-10s.webm")])),
    ("z-anchor", "«Звено» · первый экран", "concept", "image",
     ("наш лучший", [J("zveno", "c-hybrid__page-desk.jpg"), J("zveno", "a-code__page-desk.jpg"), J("zveno", "b-blender__page-desk.jpg")]),
     ("якорь hubtown", [site("hubtown")])),
    ("z-anchor-craft", "«Звено» · первый экран", "craft", "image",
     ("наш лучший", [J("zveno", "c-hybrid__page-desk.jpg"), J("zveno", "a-code__page-desk.jpg"), J("zveno", "b-blender__page-desk.jpg")]),
     ("якорь hubtown", [site("hubtown")])),
    # клавиатура «Ё» — новый продукт L1; якорь — страница продукта Apple
    ("k-first-ab", "Клавиатура «Ё» · первый экран", "page", "image",
     ("A код", [J("keyboard", "a-code__first-screen-desk.png")]), ("B Blender", [J("keyboard", "b-blender__first-screen-desk.png")])),
    ("k-exploded-ac", "Клавиатура «Ё» · разборка", "craft", "image",
     ("A код", [J("keyboard", "a-code__exploded.png")]), ("C гибрид", [J("keyboard", "c-hybrid__exploded.png")])),
    ("k-typing-bc-desk", "Клавиатура «Ё» · набор", "page", "image",
     ("B Blender", [J("keyboard", "b-blender__typing-desk.png")]), ("C гибрид", [J("keyboard", "c-hybrid__typing-desk.png")])),
    ("k-typing-bc-mob", "Клавиатура «Ё» · набор на телефоне", "page", "image",
     ("B Blender", [J("keyboard", "b-blender__typing-mob.png")]), ("C гибрид", [J("keyboard", "c-hybrid__typing-mob.png")])),
    ("k-colors-ac", "Клавиатура «Ё» · расцветка", "craft", "image",
     ("A код", [J("keyboard", "a-code__colorways-graphite.png"), J("keyboard", "a-code__colorways.png")]),
     ("C гибрид", [J("keyboard", "c-hybrid__colorways-graphite.png"), J("keyboard", "c-hybrid__colorways.png")])),
    ("k-exploded-bc", "Клавиатура «Ё» · разборка", "craft", "image",
     ("B Blender", [J("keyboard", "b-blender__exploded.png")]), ("C гибрид", [J("keyboard", "c-hybrid__exploded.png")])),
    ("k-typing-ac", "Клавиатура «Ё» · набор 10 с", "motion", "video",
     ("A код", [J("keyboard", "a-code__typing-10s.webm")]), ("C гибрид", [J("keyboard", "c-hybrid__typing-10s.webm")])),
    ("k-typing-bc", "Клавиатура «Ё» · набор 10 с", "motion", "video",
     ("B Blender", [J("keyboard", "b-blender__typing-10s.webm")]), ("C гибрид", [J("keyboard", "c-hybrid__typing-10s.webm")])),
    ("k-anchor", "Клавиатура «Ё» · первый экран", "concept", "image",
     ("наш лучший", [J("keyboard", "c-hybrid__first-screen-desk.png"), J("keyboard", "b-blender__first-screen-desk.png")]),
     ("якорь Apple AirPods Pro", [site("apple-airpods-pro")])),
    ("k-anchor-craft", "Клавиатура «Ё» · первый экран", "craft", "image",
     ("наш лучший", [J("keyboard", "c-hybrid__first-screen-desk.png"), J("keyboard", "b-blender__first-screen-desk.png")]),
     ("якорь Apple AirPods Pro", [site("apple-airpods-pro")])),
    # «Сдано» — услуга L0
    ("s-first-ab", "«Сдано» · первый экран", "page", "image",
     ("A SVG", [J("sdano", "a-code__first-screen-desk.png")]), ("B Blender", [J("sdano", "b-blender__first-screen-desk.png")])),
    ("s-beam-bc", "«Сдано» · план с дефектами", "page", "image",
     ("B Blender", [J("sdano", "b-blender__first-screen-desk.png")]),
     ("C фонарик", [J("sdano", "c-hybrid__beam-on.png"), J("sdano", "c-hybrid__first-screen-desk.png")])),
    ("s-mob-ab", "«Сдано» · телефон", "page", "image",
     ("A SVG", [J("sdano", "a-code__first-screen-mob.png")]), ("B Blender", [J("sdano", "b-blender__first-screen-mob.png")])),
    ("s-icons-ab", "«Сдано» · блок «что проверяет инженер»", "page", "image",
     ("A SVG", [J("sdano", "a-code__icons.png")]), ("B Blender", [J("sdano", "b-blender__icons.png")])),
    ("s-stamp-ab", "«Сдано» · акт со штампом", "craft", "image",
     ("A SVG", [J("sdano", "a-code__act-stamp.png")]), ("B Blender", [J("sdano", "b-blender__act-stamp.png")])),
    # дуэль Velmora — нейросеть (Kling) против Blender Cycles
    ("v-f000", "Velmora · кадр облёта 1", "craft", "image",
     ("нейросеть", [J("velmora", "ai__f000.png")]), ("Blender", [J("velmora", "b-blender__f000.png")])),
    ("v-f030", "Velmora · кадр облёта 2", "craft", "image",
     ("нейросеть", [J("velmora", "ai__f030.png")]), ("Blender", [J("velmora", "b-blender__f030.png")])),
    ("v-f060", "Velmora · кадр облёта 3", "craft", "image",
     ("нейросеть", [J("velmora", "ai__f060.png")]), ("Blender", [J("velmora", "b-blender__f060.png")])),
    ("v-motion", "Velmora · облёт мышью 10 с", "motion", "video",
     ("нейросеть", [J("velmora", "vote/ai__mouse-10s-stage.webm")]),
     ("Blender", [J("velmora", "vote/b-blender__mouse-10s-stage.webm")])),
    ("v-anchor", "Velmora · первый экран", "concept", "image",
     ("наш лучший", [J("velmora", "b-blender__first-screen-desk.png"), J("velmora", "b-blender__page-desk.png")]),
     ("якорь Shopify Editions", [site("shopify-editions")])),
    ("v-anchor-craft", "Velmora · первый экран", "craft", "image",
     ("наш лучший", [J("velmora", "b-blender__first-screen-desk.png"), J("velmora", "b-blender__page-desk.png")]),
     ("якорь Shopify Editions", [site("shopify-editions")])),
]


def first_existing(cands):
    for c in cands:
        p = os.path.normpath(os.path.join(SHOW, c))
        if os.path.exists(p):
            return p
    return None


def bg_of(im):
    """Цвет полей — медиана углов (чтобы поля при разном аспекте не бросались в глаза)."""
    w, h = im.size
    px = [im.getpixel((x, y)) for x, y in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3))]
    return tuple(sorted(c[i] for c in px)[1] for i in range(3))


def fit(im, size):
    """Вписать в size с полями цвета фона (аспект сохраняется)."""
    im = im.convert("RGB")
    W, H = size
    s = min(W / im.width, H / im.height)
    w, h = max(1, round(im.width * s)), max(1, round(im.height * s))
    out = Image.new("RGB", size, bg_of(im))
    out.paste(im.resize((w, h), Image.LANCZOS), ((W - w) // 2, (H - h) // 2))
    return out


def main():
    check = "--check" in sys.argv[1:]
    missing, pairs = [], []
    if not check:
        os.makedirs(OUT_IMG, exist_ok=True)
        pj = os.path.join(HERE, "pairs.json")
        if os.path.exists(pj) and not os.path.exists(os.path.join(HERE, "pairs-test.json")):
            shutil.copy(pj, os.path.join(HERE, "pairs-test.json"))
    skip = set(filter(None, os.environ.get("SKIP_PAIRS", "").split(",")))  # временно убрать пары (кадр на переделке)
    for n, (pid, group, q, kind, (va, ca), (vb, cb)) in enumerate(PAIRS, 1):
        if pid in skip:
            print(f"пропуск {pid} (SKIP_PAIRS)")
            continue
        pa, pb = first_existing(ca), first_existing(cb)
        if not pa or not pb:
            missing.append((pid, None if pa else ca[0], None if pb else cb[0]))
            continue
        tag = f"p{n:02d}"
        if check:
            print(f"ok   {pid:14s} {os.path.relpath(pa, SHOW)}  ↔  {os.path.relpath(pb, SHOW)}")
            continue
        if kind == "image":
            ia, ib = Image.open(pa), Image.open(pb)
            # общий размер: меньший по площади из двух, не шире MAXW; аспект — первого (оба кадра одного вида)
            ref = ia if ia.width * ia.height <= ib.width * ib.height else ib
            W, H = ref.size
            if W > MAXW:
                W, H = MAXW, round(H * MAXW / W)
            files = []
            for k, im in ((1, ia), (2, ib)):
                f = f"{tag}-{k}.jpg"
                fit(im, (W, H)).save(os.path.join(OUT_IMG, f), quality=88, optimize=True, progressive=True)
                files.append("img/" + f)
        else:
            files = []
            for k, p in ((1, pa), (2, pb)):
                f = f"{tag}-{k}.webm"
                shutil.copy(p, os.path.join(OUT_IMG, f))
                files.append("img/" + f)
        pairs.append({"id": pid, "group": group, "kind": kind, "q": q,
                      "a": {"src": files[0], "v": va, "from": os.path.relpath(pa, SHOW)},
                      "b": {"src": files[1], "v": vb, "from": os.path.relpath(pb, SHOW)}})
    for pid, a, b in missing:
        print(f"нет  {pid:14s} " + "; ".join(x for x in (a and f"A: {a}", b and f"B: {b}") if x))
    if check:
        print(f"готово пар: {len(PAIRS) - len(missing)} из {len(PAIRS)}")
        return 0
    doc = {"questions": QUESTIONS, "pairs": pairs,
           "note": "Сборка build_pairs.py; поле from — исходник кадра (для итогов, на странице не показывается)."}
    with open(os.path.join(HERE, "pairs.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f"pairs.json: {len(pairs)} пар (пропущено {len(missing)}); img/ — {len(os.listdir(OUT_IMG))} файлов")
    return 0


if __name__ == "__main__":
    sys.exit(main())
