#!/usr/bin/env python3
"""gate_check.py — общий модуль ворот качества страницы с 3D по отчёту site_probe.py (агент U, волна 4 — перенос
рекомендации X §12: один модуль вместо кода F1 `09-web-runtime/05-performance-a11y-fallbacks.md` §7.2 и копии K
`99-raw/experiments/K/02-hero-page/gates.py`; импортируется `qa_pipeline.py page` вместо собственной копии).

  from gate_check import gate_check
  rows = gate_check("probe_quick.json", mode="desktop", reduced=False)   # [(проверка, значение, порог, прошла ли), …]
  python3 gate_check.py probe_quick.json [mobile|desktop] [--reduced]    # CLI для разовой проверки

Правки волны 4 (U, по решению аудита X §12):
  - «3D-ассеты, КБ» (`kb3d`) теперь считает и категорию site_probe.py "bin", не только "model3d"+"texture3d":
    glTF-буферы .bin, отданные отдельно от .glb, site_probe.py относит к "model3d" только если путь запроса
    содержит models/meshes/geometr/gltf/glb/3d — иначе они попадают в общую "bin" (там же .dat/.raw/.bytes/.gz/.br)
    и раньше не входили в бюджет 3D (находка K/04: страница частиц — 412 КБ .bin вне подсчёта при 805 КБ страницы).
  - TBT (десктоп) — решение R20 аудита X: без компрессированных 3D-текстур (KTX2 и т. п., категория "texture3d")
    порог остаётся 150 мс; если на странице были запросы категории "texture3d" (транскодер KTX2 разжимал текстуры
    на CPU) — порог мягче, 200 мс (эталон hero-lazy: 172 мс проходит только с этой поправкой; F1 `09/05 §7.2`,
    J/03, K/02). Телефон — 300 мс при CPU×4, без изменений.
"""
import json
import sys

LIMITS = {"mobile": dict(lcp=2500, tbt=300, kb=3072, kb3d=820, dc=30, dpr=1.5),
          "desktop": dict(lcp=1000, tbt=150, kb=7168, kb3d=1536, dc=60, dpr=2.0)}
TBT_DESKTOP_KTX2 = 200        # R20: десктоп с транскодером KTX2 — мягче порог, чем базовые 150 мс


def gate_check(probe_path, mode="mobile", reduced=False):
    """Список (проверка, значение, порог, прошла ли) по probe*.json из site_probe.py."""
    st = json.load(open(probe_path)); lim = LIMITS[mode]
    v = st.get("vitals_pre_scroll") or {}; lcp = v.get("lcp") or {}; net = st.get("network") or {}
    cat = net.get("by_category") or {}; idle = st.get("idle") or {}
    kb3d = sum((cat.get(k) or {}).get("transfer_kb", 0) for k in ("model3d", "texture3d", "bin"))
    canv = [c for c in (st.get("detected") or {}).get("canvases", []) if c.get("vis") and c.get("css", [0])[0]]
    dpr = max((c["w"] / c["css"][0] for c in canv), default=0)
    rows = [("LCP-элемент не canvas", lcp.get("tag"), "не CANVAS", lcp.get("tag") not in (None, "CANVAS")),
            ("LCP, мс", lcp.get("t"), lim["lcp"], (lcp.get("t") or 1e9) <= lim["lcp"]),
            ("CLS", v.get("cls"), 0.1, (v.get("cls") or 0) <= 0.1),
            ("ошибки консоли", st.get("console_errors"), 0, st.get("console_errors") == 0)]
    if reduced:
        rows.append(("reduce: вызовов в покое", idle.get("dc_median"), 0, idle.get("dc_median") == 0))
        rows.append(("reduce: движение в покое, %", st.get("idle_motion_pct"), 0.05, (st.get("idle_motion_pct") or 0) <= 0.05))
    else:
        ktx2 = (cat.get("texture3d") or {}).get("n", 0) > 0
        tbt_limit = TBT_DESKTOP_KTX2 if (mode == "desktop" and ktx2) else lim["tbt"]
        rows += [("TBT, мс", v.get("tbt_ms"), tbt_limit, (v.get("tbt_ms") or 0) <= tbt_limit),
                 ("передано, КБ", net.get("transfer_kb"), lim["kb"], (net.get("transfer_kb") or 0) <= lim["kb"]),
                 ("3D-ассеты, КБ", round(kb3d, 1), lim["kb3d"], kb3d <= lim["kb3d"]),
                 ("вызовов в кадре", idle.get("dc_median"), lim["dc"], (idle.get("dc_median") or 0) <= lim["dc"]),
                 ("DPR canvas", round(dpr, 2), lim["dpr"], dpr <= lim["dpr"] + 0.01)]
    return rows


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); sys.exit(0)
    mode = a[1] if len(a) > 1 and a[1] in LIMITS else "mobile"
    reduced = "--reduced" in a
    rows = gate_check(a[0], mode, reduced)
    for name, val, limit, ok in rows:
        print("OK  " if ok else "FAIL", name, val, limit)
    sys.exit(0 if all(r[3] for r in rows) else 1)


if __name__ == "__main__":
    main()
