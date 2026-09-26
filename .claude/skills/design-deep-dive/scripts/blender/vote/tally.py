#!/usr/bin/env python3
"""tally.py — итоги слепого голосования «Кадр против кадра» → results.json, results.md и блок в вердикте (оркестратор, сессия 2).

    python3 tally.py                  # голоса из votes/*.json (пробные votes-test/ не берутся)
    python3 tally.py --json FILE ...  # + голоса, скопированные со страницы кнопкой «Скопировать результаты (JSON)»

Счёт пары у одного судьи — как на странице: победа, только если оба порядка согласны; иначе ничья; «оба слабо» в обоих — отдельно.
Сводки: по предметам (какая дорога выигрывает), доля побед гибрида над кодом (C против A: победа 1, ничья 0,5) с правилом плана —
≥ 0,75 «Blender обязателен», 0,4–0,75 «по бюджету», < 0,4 «не нужен» (для продукта L1/L2); якоря класса; дуэль нейросеть ↔ Blender.
Если в ../VERDICT.md или ../verdict/index.html есть метки <!-- VOTE:BEGIN --> … <!-- VOTE:END -->, блок между ними заменяется.
"""
import glob
import html
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
SHOW = str(kbpaths.kb("blender", "15-showcase"))  # перенос: VERDICT.md испытания — kb


def pref(ans):
    if not ans:
        return None
    c = ans.get("c")
    if c == "equal":
        return "="
    if c == "both_bad":
        return "x"
    left_is_a = not ans.get("flip")
    return "A" if (c == "left") == left_is_a else "B"


def pair_result(answers, pid):
    x, y = pref(answers.get(pid + ":0")), pref(answers.get(pid + ":1"))
    if x is None or y is None:
        return None
    if x == "x" and y == "x":
        return "bad"
    if x == y and x in ("A", "B"):
        return x
    return "tie"


def load_votes(extra):
    docs = []
    for f in sorted(glob.glob(os.path.join(HERE, "votes", "*.json"))):
        try:
            docs.append(json.load(open(f, encoding="utf-8")))
        except Exception as e:  # noqa: BLE001
            print("! не читается", f, e)
    for f in extra:
        d = json.load(open(f, encoding="utf-8"))
        docs.append(d.get("doc", d))
    return [d for d in docs if isinstance(d, dict) and d.get("answers")]


def main():
    a = sys.argv[1:]
    extra = a[a.index("--json") + 1:] if "--json" in a else []
    pairs = json.load(open(os.path.join(HERE, "pairs.json"), encoding="utf-8"))["pairs"]
    docs = load_votes(extra)
    per = {}
    for p in pairs:
        c = defaultdict(int)
        for d in docs:
            r = pair_result(d["answers"], p["id"])
            if r:
                c[r] += 1
        per[p["id"]] = {"id": p["id"], "group": p.get("group"), "q": p.get("q"), "a": p["a"]["v"], "b": p["b"]["v"],
                        "A": c["A"], "B": c["B"], "tie": c["tie"], "bad": c["bad"], "n": sum(c.values())}

    def side_score(r, label_pred):
        """(очки стороны, всего) — победа 1, ничья 0,5; «оба слабо» — 0 и в счёт."""
        if label_pred(r["a"]):
            return r["A"] + 0.5 * r["tie"], r["n"]
        if label_pred(r["b"]):
            return r["B"] + 0.5 * r["tie"], r["n"]
        return 0, 0

    # гибрид против кода (A код ↔ C гибрид)
    hc = [r for r in per.values() if {r["a"].split()[0], r["b"].split()[0]} == {"A", "C"}]
    s, n = 0.0, 0
    for r in hc:
        x, m = side_score(r, lambda v: v.startswith("C"))
        s, n = s + x, n + m
    share = s / n if n else None
    rule = (None if share is None else "Blender обязателен" if share >= 0.75 else "по бюджету" if share >= 0.4 else "Blender не нужен")
    # дуэль
    duel = [r for r in per.values() if r["id"].startswith("v-") and "якорь" not in r["b"]]
    ds, dn = 0.0, 0
    for r in duel:
        x, m = side_score(r, lambda v: v.startswith("Blender"))
        ds, dn = ds + x, dn + m
    anchors = [r for r in per.values() if "якорь" in r["b"] or "якорь" in r["a"]]
    # правило L2 плана против якорей: победа или ничья (доля ≥ 0,5) в ≥ 2 из 3 критериев; motion у якорей не снят
    l2 = {}
    for r in anchors:
        subj = r["id"].split("-")[0]
        if r["n"]:
            share_ours = (r["A"] + 0.5 * r["tie"]) / r["n"]
            l2.setdefault(subj, {})[r["q"]] = share_ours
    l2_rule = {s: {"criteria": v, "pass": sum(1 for x in v.values() if x >= 0.5) >= 2} for s, v in l2.items()}
    res = {"voters": len(docs), "pairs": list(per.values()),
           "hybrid_vs_code": {"pairs": [r["id"] for r in hc], "share": share, "votes": n, "rule": rule},
           "duel_blender_share": (ds / dn if dn else None), "duel_votes": dn,
           "anchors": [{"id": r["id"], "q": r["q"], "ours": r["a"], "anchor": r["b"], "win": r["A"], "tie": r["tie"], "loss": r["B"], "n": r["n"]}
                       for r in anchors],
           "l2_vs_anchors": l2_rule}
    json.dump(res, open(os.path.join(HERE, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def fmt(x):
        return "—" if x is None else f"{x:.2f}".replace(".", ",")
    md = [f"**Слепое голосование заказчика**: судей {len(docs)}, пар {len(pairs)} (каждая в двух порядках; расхождение порядков = ничья).", "",
          "| Пара | Вопрос | A | B | A сильнее | B сильнее | ничья | оба слабо |", "|---|---|---|---|---|---|---|---|"]
    for r in per.values():
        md.append(f"| {r['group']} (`{r['id']}`) | {r['q']} | {r['a']} | {r['b']} | {r['A']} | {r['B']} | {r['tie']} | {r['bad']} |")
    md += ["", f"- Гибрид (C) против кода (A), продукт: доля побед C = **{fmt(share)}** по {n} голосам пар ({', '.join(r['id'] for r in hc) or 'нет пар'}) → правило плана: **{rule or 'нет данных'}**.",
           f"- Дуэль: доля побед Blender над нейросетью = **{fmt(res['duel_blender_share'])}** по {dn} голосам пар.",
           "- Якоря класса: " + ("; ".join(f"{r['id']} ({r['q']}): наш {r['A']} / ничья {r['tie']} / якорь {r['B']}" for r in anchors) or "нет пар") + ".",
           "- Правило L2 против якорей (победа или ничья в ≥ 2 из 3 критериев; motion у якорей не снят): "
           + ("; ".join(f"{s}: " + ", ".join(f"{k} {fmt(v)}" for k, v in d["criteria"].items()) + (" → **проходит**" if d["pass"] else " → не проходит")
                        for s, d in l2_rule.items()) or "нет данных") + "."]
    text = "\n".join(md) + "\n"
    open(os.path.join(HERE, "results.md"), "w", encoding="utf-8").write(text)
    print(text)

    for target in (os.path.join(SHOW, "VERDICT.md"), os.path.join(SHOW, "verdict", "index.html")):
        if not os.path.exists(target):
            continue
        s0 = open(target, encoding="utf-8").read()
        if "<!-- VOTE:BEGIN -->" not in s0:
            continue
        block = text if target.endswith(".md") else md_to_html(text)
        s1 = re.sub(r"<!-- VOTE:BEGIN -->.*?<!-- VOTE:END -->", "<!-- VOTE:BEGIN -->\n" + block + "<!-- VOTE:END -->", s0, flags=re.S)
        open(target, "w", encoding="utf-8").write(s1)
        print("блок итогов обновлён:", os.path.relpath(target, SHOW))
    return 0


def md_to_html(text):
    """Минимальный перевод блока итогов (абзац, таблица, список) в HTML для страницы вердикта."""
    out, rows = [], []
    for line in text.splitlines():
        if line.startswith("|"):
            if set(line.replace("|", "").strip()) <= set("-: "):
                continue
            rows.append([html.escape(c.strip()) for c in line.strip("|").split("|")])
            continue
        if rows:
            head, body = rows[0], rows[1:]
            out.append("<table><thead><tr>" + "".join(f"<th>{c}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table>")
            rows = []
        if line.startswith("- "):
            out.append("<p>" + re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(line[2:])) + "</p>")
        elif line.strip():
            out.append("<p>" + re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html.escape(line)) + "</p>")
    if rows:
        head, body = rows[0], rows[1:]
        out.append("<table><thead><tr>" + "".join(f"<th>{c}</th>" for c in head) + "</tr></thead><tbody>"
                   + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.exit(main())
