#!/usr/bin/env python3
"""color — расчёты цвета для интерфейсов без внешних зависимостей: OKLCH, контраст WCAG 2 и APCA, цвет глазами людей с
нарушением цветового зрения, ΔE в OKLab, наложение с альфой.

Функции:
    hex2rgb, hex2oklch(hex) -> (L 0..1, C, H°), oklch2hex(L, C, H), in_gamut, max_chroma(L, H), relL,
    wcag(fg, bg) -> отношение контраста WCAG 2, apca(fg, bg) -> Lc (APCA 0.1.9, знак = полярность),
    sim_cvd(hex, 'protan'|'deutan'|'tritan'), dE_oklab(a, b), composite(fg, alpha, bg).

Подключение в утилите `scripts/<домен>/<утилита>.py` — модуль лежит в `scripts/lib/` рядом с kbpaths:

    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
    from color import wcag, apca, hex2oklch

Командная строка (путь — от папки скилла):
    python3 scripts/lib/color.py contrast "#1f2937" "#ffffff"      -> {"wcag": …, "apca_Lc": …}
    python3 scripts/lib/color.py oklch "#2563eb"                     -> L, C, H
    python3 scripts/lib/color.py hex 0.62 0.19 260                   -> hex (с отображением в гамут sRGB)
    python3 scripts/lib/color.py maxchroma 0.62 260                  -> максимальная хрома для L и H в sRGB
    python3 scripts/lib/color.py cvd "#e5484d" deutan                -> цвет глазами дейтеранопа
    python3 scripts/lib/color.py de "#e5484d" "#30a46c"              -> ΔE в OKLab
    python3 scripts/lib/color.py composite "#000000" 0.08 "#ffffff"  -> результат наложения с альфой
    python3 scripts/lib/color.py selftest                            -> контрольные точки
    python3 scripts/lib/color.py --help | <команда> --help           -> эта справка, код 0

Коды выхода: 0 — расчёт выполнен, справка или самопроверка прошла; 1 — неизвестная команда, не то число аргументов
или самопроверка не прошла.

Контрольные точки сверены с калькулятором APCA: apca(#000,#fff)=106.0, apca(#fff,#000)=-107.9, apca(#888,#fff)=63.1,
wcag(#000,#fff)=21.0, wcag(#767676,#fff)=4.54. Алгоритмы — kb/ui/01-color/01-color-models-and-scales.md и
kb/ui/01-color/03-contrast.md.
"""
import math, sys

def hex2rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3: h = ''.join(c*2 for c in h)
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))

def srgb2lin(c):
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def lin2srgb(c):
    return c*12.92 if c <= 0.0031308 else 1.055*(c**(1/2.4))-0.055

def rgb2oklab(r,g,b):
    r,g,b = srgb2lin(r), srgb2lin(g), srgb2lin(b)
    l = 0.4122214708*r + 0.5363325363*g + 0.0514459929*b
    m = 0.2119034982*r + 0.6806995451*g + 0.1073969566*b
    s = 0.0883024619*r + 0.2817188376*g + 0.6299787005*b
    l_,m_,s_ = l**(1/3) if l>=0 else -(-l)**(1/3), m**(1/3) if m>=0 else -(-m)**(1/3), s**(1/3) if s>=0 else -(-s)**(1/3)
    return (0.2104542553*l_ + 0.7936177850*m_ - 0.0040720468*s_,
            1.9779984951*l_ - 2.4285922050*m_ + 0.4505937099*s_,
            0.0259040371*l_ + 0.7827717662*m_ - 0.8086757660*s_)

def oklab2rgb(L,a,b):
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l,m,s = l_**3, m_**3, s_**3
    r = +4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bb= -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    return tuple(lin2srgb(x) for x in (r,g,bb))

def hex2oklch(h):
    L,a,b = rgb2oklab(*hex2rgb(h))
    C = math.hypot(a,b); H = math.degrees(math.atan2(b,a)) % 360
    return L, C, H

def oklch2hex(L,C,H, clip=True):
    a = C*math.cos(math.radians(H)); b = C*math.sin(math.radians(H))
    r,g,bb = oklab2rgb(L,a,b)
    if clip: r,g,bb = (min(1,max(0,x)) for x in (r,g,bb))
    return '#%02x%02x%02x' % tuple(round(x*255) for x in (r,g,bb))

def in_gamut(L,C,H, eps=1e-4):
    a = C*math.cos(math.radians(H)); b = C*math.sin(math.radians(H))
    return all(-eps <= x <= 1+eps for x in oklab2rgb(L,a,b))

def max_chroma(L,H,hi=0.4):
    lo=0.0
    for _ in range(40):
        mid=(lo+hi)/2
        if in_gamut(L,mid,H): lo=mid
        else: hi=mid
    return lo

def relL(h):
    r,g,b = hex2rgb(h)
    return 0.2126*srgb2lin(r)+0.7152*srgb2lin(g)+0.0722*srgb2lin(b)

def wcag(h1,h2):
    a,b = relL(h1), relL(h2)
    if a<b: a,b=b,a
    return (a+0.05)/(b+0.05)

# APCA 0.1.9 (W3 / Myndex) — exponents from the published algorithm
def apca_Y(h):
    r,g,b = hex2rgb(h)
    return 0.2126729*(r**2.4)+0.7151522*(g**2.4)+0.0721750*(b**2.4)

def apca(text_hex, bg_hex):
    Ytxt, Ybg = apca_Y(text_hex), apca_Y(bg_hex)
    Bclip, Bthrsh = 1.414, 0.022
    def clampY(Y):
        return Y if Y > Bthrsh else Y + (Bthrsh - Y)**Bclip
    Ytxt, Ybg = clampY(Ytxt), clampY(Ybg)
    Wscale, Woffset = 1.14, 0.027
    if abs(Ybg - Ytxt) < 0.0005: return 0.0
    if Ybg > Ytxt:  # normal polarity: dark text on light bg
        S = (Ybg**0.56 - Ytxt**0.57) * Wscale
        out = 0.0 if S < 0.1 else S - Woffset
    else:           # reverse polarity: light text on dark bg
        S = (Ybg**0.65 - Ytxt**0.62) * Wscale
        out = 0.0 if S > -0.1 else S + Woffset
    return round(out*100, 1)

# ---- Дальтонизм (Viénot, Brettel & Mollon 1999), ΔE в OKLab, композитинг альфы ----

def sim_cvd(hexc, kind):
    """kind: 'protan' | 'deutan' | 'tritan'. Возвращает hex, как цвет видит человек с этим типом дальтонизма."""
    r, g, b = [srgb2lin(x) for x in hex2rgb(hexc)]
    L = 17.8824*r + 43.5161*g + 4.11935*b
    M = 3.45565*r + 27.1554*g + 3.86714*b
    S = 0.0299566*r + 0.184309*g + 1.46709*b
    if kind == 'protan':
        L2 = 2.02344*M - 2.52581*S; M2, S2 = M, S
    elif kind == 'deutan':
        M2 = 0.494207*L + 1.24827*S; L2, S2 = L, S
    else:
        S2 = -0.395913*L + 0.801109*M; L2, M2 = L, M
    r2 =  0.080944*L2 - 0.130504*M2 + 0.116721*S2
    g2 = -0.0102485*L2 + 0.0540194*M2 - 0.113615*S2
    b2 = -0.000365294*L2 - 0.00412163*M2 + 0.693513*S2
    return '#%02x%02x%02x' % tuple(
        max(0, min(255, round(lin2srgb(max(0, min(1, x))) * 255))) for x in (r2, g2, b2))


def dE_oklab(a, b):
    """Евклидово расстояние в OKLab между двумя hex-цветами (0.02 — едва заметно, 0.05 — уверенно различимо)."""
    La, Aa, Ba = rgb2oklab(*hex2rgb(a))
    Lb, Ab, Bb = rgb2oklab(*hex2rgb(b))
    return math.sqrt((La-Lb)**2 + (Aa-Ab)**2 + (Ba-Bb)**2)


def composite(fg_hex, alpha, bg_hex):
    """Цвет, который получится, если положить fg с прозрачностью alpha на непрозрачный bg."""
    f, b = hex2rgb(fg_hex), hex2rgb(bg_hex)
    return '#%02x%02x%02x' % tuple(round(255*(f[i]*alpha + b[i]*(1-alpha))) for i in range(3))


def wants_help(args):
    """Справку просят вызовом без аргументов и ключом -h или --help в любом месте, в том числе после подкоманды."""
    return not args or any(x in ("-h", "--help") for x in args)


if __name__ == "__main__":
    import json
    a = sys.argv[1:]
    if wants_help(a):
        print(__doc__); sys.exit(0)
    cmd = a[0]
    if cmd == "contrast" and len(a) == 3:
        print(json.dumps({"fg": a[1], "bg": a[2], "wcag": round(wcag(a[1], a[2]), 2), "apca_Lc": round(apca(a[1], a[2]), 1)}))
    elif cmd == "oklch" and len(a) == 2:
        L, C, H = hex2oklch(a[1]); print(json.dumps({"hex": a[1], "L": round(L, 4), "C": round(C, 4), "H": round(H, 1)}))
    elif cmd == "hex" and len(a) == 4:
        print(oklch2hex(float(a[1]), float(a[2]), float(a[3])))
    elif cmd == "cvd" and len(a) == 3:
        print(sim_cvd(a[1], a[2]))
    elif cmd == "de" and len(a) == 3:
        print(round(dE_oklab(a[1], a[2]), 4))
    elif cmd == "maxchroma" and len(a) == 3:
        print(round(max_chroma(float(a[1]), float(a[2])), 4))
    elif cmd == "composite" and len(a) == 4:
        print(composite(a[1], float(a[2]), a[3]))
    elif cmd == "selftest":
        checks = [("apca #000 on #fff", round(apca("#000000", "#ffffff"), 1), 106.0),
                  ("apca #fff on #000", round(apca("#ffffff", "#000000"), 1), -107.9),
                  ("apca #888 on #fff", round(apca("#888888", "#ffffff"), 1), 63.1),
                  ("wcag #000 on #fff", round(wcag("#000000", "#ffffff"), 2), 21.0),
                  ("wcag #767676 on #fff", round(wcag("#767676", "#ffffff"), 2), 4.54)]
        ok = True
        for name, got, want in checks:
            flag = abs(got - want) < 0.06
            ok &= flag
            print(f"{'OK ' if flag else 'FAIL'} {name}: {got} (ожидалось {want})")
        for name, got, want in [("справка у подкоманды: contrast --help", wants_help(["contrast", "--help"]), True),
                                ("справка ключом -h после аргумента", wants_help(["oklch", "#2563eb", "-h"]), True),
                                ("расчёт — не справка", wants_help(["contrast", "#000000", "#ffffff"]), False)]:
            ok &= got == want
            print(f"{'OK ' if got == want else 'FAIL'} {name}")
        sys.exit(0 if ok else 1)
    else:
        print(__doc__); sys.exit(1)
