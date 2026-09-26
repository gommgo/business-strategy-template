#!/usr/bin/env python3
"""Русский против английского на Opus 5.5: одни и те же фрагменты базы в оригинале и в переводе.

Берёт 5 типичных фрагментов (выжимки ux и ui, чек-лист text, README папки site, кусок теории ux),
переводит их Opus 5.5 на английский и меряет токены обоих вариантов тем же способом, что
calibrate.py (разница usage с пустым прогоном). Переводы — в ru_vs_en/ для проверки глазами.

  python3 ru_vs_en.py
"""
import json
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor

from calibrate import MODEL, input_tokens
from count_tokens import HERE, ROOT, research_dirs, thematic_files
from layers import SECTIONS, sections

LIMIT = 8000
TR_SYSTEM = ("You are a professional technical translator. Translate the Russian text from stdin into English "
             "faithfully and completely. Preserve markdown structure, numbers, units, ids, code, paths and links "
             "exactly. Do not summarize, omit, explain or add anything. Output only the translation.")
TRANSLATE = ["claude", "-p", "Translate the text from stdin into English.", "--model", MODEL,
             "--output-format", "json", "--tools", "", "--system-prompt", TR_SYSTEM,
             "--no-session-persistence", "--strict-mcp-config", "--disable-slash-commands", "--effort", "low"]


def clip(text, start=0, limit=LIMIT):
    """Кусок до limit символов, по границам строк."""
    if start:
        start = text.find("\n", start) + 1
    end = start + limit
    return text[start:] if end >= len(text) else text[start:text.rfind("\n", start, end)]


def pick(rng):
    md = {r.name: [p for s, p in thematic_files(r) if p.suffix == ".md" and s != "(root)"] for r in research_dirs()}
    picks = []

    def section_from(research, key, label):
        files = md[research][:]
        rng.shuffle(files)
        for path in files:
            part = sections(path.read_text(errors="replace"), SECTIONS[key])
            if len(part) > 2500:
                picks.append((label, path, clip(part)))
                return

    section_from("ux-research", "digest", "выжимка ux")
    section_from("ui-research", "digest", "выжимка ui")
    section_from("text-research", "checklist", "чек-лист text")
    readme = rng.choice([p for p in md["site-research"] if p.name == "README.md"])
    picks.append(("README папки site", readme, clip(readme.read_text())))
    theory = rng.choice([p for p in md["ux-research"] if p.parent.name == "01-foundations" and p.name != "README.md"])
    text = theory.read_text()
    picks.append(("теория ux", theory, clip(text, start=len(text) // 2)))
    return picks


def translate(text):
    proc = subprocess.run(TRANSLATE, input=text, capture_output=True, text=True, timeout=900, cwd=HERE)
    data = json.loads(proc.stdout)
    if data.get("is_error") or set(data.get("modelUsage", {})) != {MODEL}:
        raise RuntimeError(f"перевод не удался: {proc.stdout[:300]} {proc.stderr[:300]}")
    return data["result"]


def main():
    picks = pick(random.Random(11))
    with ThreadPoolExecutor(5) as executor:
        english = list(executor.map(translate, [text for _, _, text in picks]))
    texts = [""] + [text for _, _, text in picks] + english
    with ThreadPoolExecutor(4) as executor:
        base, *counts = executor.map(input_tokens, texts)
    ru_tokens = [c - base for c in counts[:len(picks)]]
    en_tokens = [c - base for c in counts[len(picks):]]

    out = HERE / "ru_vs_en"
    out.mkdir(exist_ok=True)
    print(f"{'фрагмент':<20}{'RU симв':>9}{'EN симв':>9}{'RU ток':>8}{'EN ток':>8}{'EN/RU ток':>11}  файл")
    for i, ((label, path, text), en, rt, et) in enumerate(zip(picks, english, ru_tokens, en_tokens), 1):
        (out / f"{i}-ru.md").write_text(text)
        (out / f"{i}-en.md").write_text(en)
        print(f"{label:<20}{len(text):>9}{len(en):>9}{rt:>8}{et:>8}{et / rt:>10.2f}×  {path.relative_to(ROOT)}")
    ru_sum, en_sum = sum(ru_tokens), sum(en_tokens)
    print(f"{'ИТОГО':<20}{sum(len(t) for _, _, t in picks):>9}{sum(len(e) for e in english):>9}"
          f"{ru_sum:>8}{en_sum:>8}{en_sum / ru_sum:>10.2f}×")
    print(f"Английский экономит {100 * (1 - en_sum / ru_sum):.0f}% токенов на этих фрагментах. Тексты: {out}")


if __name__ == "__main__":
    main()
