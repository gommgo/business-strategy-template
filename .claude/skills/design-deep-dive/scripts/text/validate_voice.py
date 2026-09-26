#!/usr/bin/env python3
"""validate_voice.py — проверка voice.schema.yaml (F) и профилей голоса: схема, смысловые проверки, отрицательные мутации.

Запуск (venv-F: jsonschema 4.26.0, PyYAML 6.0.3):
    99-raw/tools/venv-F/bin/python 99-raw/experiments/F/03-schema-lint/validate_voice.py [voice.yaml …]
Без аргументов — три примера базы 05-voice-editorial/examples/voice-*.yaml (для них ≥ 8 типов слотов на язык).

Проверки:
  1. метасхема Draft 2020-12; поле date; enum slot-type совпадает с временным словарём (+ 4 предложения B2 и J);
  2. каждый профиль валиден по схеме;
  3. смысловые (схема их не видит): образцы против обращения («ты» при ru_form: vy; «Вы» в середине фразы), эмодзи,
     восклицаний, словаря «не говорим»; ссылки fact:/missing: разрешаются в facts_ref; adaptation_of указывает на
     русский образец; use ∩ avoid = ∅; tone_of_voice называет обращение; у принципа есть проверяемое исполнение
     (число или «цитата» хотя бы в одном правиле); пустые принципы-прилагательные («честные», «надёжные») — предупреждение;
  4. отрицательные мутации: каждая обязана дать ошибку схемы или смысловую ошибку.
Выход: 0 — всё прошло; 1 — есть ошибки. Итог печатается и пишется в last-run.txt рядом.
"""
import copy
import re
import sys
from pathlib import Path

import yaml

try:
    import jsonschema
except ImportError:  # pragma: no cover
    sys.exit("нужен jsonschema: 99-raw/tools/venv-F/bin/python")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("text")
SCHEMA = ROOT / "05-voice-editorial" / "voice.schema.yaml"
EXAMPLES = sorted((ROOT / "05-voice-editorial" / "examples").glob("voice-*.yaml"))
VOCAB = ROOT / "99-raw" / "notes" / "temp-vocabulary-v0.yaml"
PROPOSED_SLOTS = {"spec-row", "price-old", "stat-source", "image-caption"}

TY_RE = re.compile(r"(?<![А-Яа-яЁё])(ты|тебя|тебе|тобой|твой|твоя|твоё|твое|твои|твоего|твоей|твоему|твоим|твоими|твоих|твою|"
                   r"закажи|узнай|получи|попробуй|начни|выбери|оставь|запишись|подпишись|скачай|жми|нажми|купи|"
                   r"забронируй|позвони|напиши|приходи|успей|звони|пиши|бери|возьми|оформи)(?![А-Яа-яЁё])", re.I)
CAP_VY_RE = re.compile(r"(?<=[а-яёa-z0-9,;:—–)»]\s)(Вы|Вас|Вам|Вами|Ваш[а-яё]*)(?![А-Яа-яЁё])")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿⭐⭕]")
QUOTE_RE = re.compile(r"«[^«»]*»|“[^“”]*”|\"[^\"]*\"")
GENERIC = re.compile(r"^(человечн|дружелюбн|честн|надёжн|надежн|профессиональн|инновационн|современн|открыт|экспертн|"
                     r"уникальн|качественн|клиентоориентированн|тёпл|тепл|аккуратн|сво[ией])\w*$", re.I)


def words_regex(term: str) -> re.Pattern:
    """Как words_to_pattern в copy_lint.py: «*» — продолжение основы, «ё» = [её], пробелы — \\s+."""
    parts = []
    for p in term.strip().split():
        e = re.escape(p).replace("ё", "[её]").replace("Ё", "[ЕЁ]")  # сначала «ё», потом класс продолжения основы
        e = e.replace(r"\*", r"[A-Za-zА-Яа-яЁё0-9_]*")
        parts.append(e)
    return re.compile(r"(?<![A-Za-zА-Яа-яЁё0-9_])" + r"\s+".join(parts) + r"(?![A-Za-zА-Яа-яЁё0-9_])", re.I)


def load(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def facts_ids(voice: dict, voice_path: Path) -> tuple[set, set, str]:
    ref = (voice.get("brand") or {}).get("facts_ref")
    if not ref:
        return set(), set(), "нет facts_ref"
    fp = (voice_path.parent / ref).resolve()
    if not fp.exists():
        return set(), set(), f"facts_ref не найден: {ref}"
    d = load(fp)
    return {f["id"] for f in d.get("facts", [])}, {m["id"] for m in d.get("missing", [])}, ""


def semantic(voice: dict, voice_path: Path, base_example: bool) -> tuple[list, list]:
    errs, warns = [], []
    samples = voice.get("samples") or []
    addr = voice.get("address") or {}
    punct = voice.get("punctuation") or {}
    avoid = [(t["term"], words_regex(t["term"]), t.get("lang", "ru")) for t in (voice.get("vocabulary") or {}).get("avoid") or []]
    ids = {s["id"] for s in samples}
    fids, mids, ferr = facts_ids(voice, voice_path)
    if ferr:
        errs.append(ferr)
    # 1. типы слотов по языкам
    by_lang: dict = {}
    for s in samples:
        by_lang.setdefault(s["lang"][:2], set()).add(s["slot_type"])
    if base_example:
        for lg in ("ru", "en"):
            n = len(by_lang.get(lg, set()))
            if n < 8:
                errs.append(f"образцов {lg}: {n} типов слотов, нужно ≥ 8 (задание F)")
    for s in samples:
        t = s["text"]
        plain = QUOTE_RE.sub(" ", t)
        # 2. ссылки на факты
        for ref in s.get("fact_ids") or []:
            if ":" not in ref:
                errs.append(f"{s['id']}: ссылка «{ref}» без префикса fact:/missing:")
                continue
            kind, fid = ref.split(":", 1)
            if kind == "fact" and fid not in fids:
                errs.append(f"{s['id']}: {ref} нет в facts.yaml")
            if kind == "missing" and fid not in mids:
                errs.append(f"{s['id']}: {ref} нет в missing[]")
        if any(r.startswith("missing:") for r in s.get("fact_ids") or []) and "[PLACEHOLDER" not in t:
            errs.append(f"{s['id']}: missing:… без [PLACEHOLDER] в тексте")
        # 3. адаптация
        if s["lang"].startswith("en"):
            a = s.get("adaptation_of")
            if a and a not in ids:
                errs.append(f"{s['id']}: adaptation_of → {a} не найден")
            if not a:
                warns.append(f"{s['id']}: английский образец без adaptation_of")
        # 4. обращение
        if s["lang"].startswith("ru"):
            if addr.get("ru_form") == "vy" and TY_RE.search(plain):
                errs.append(f"{s['id']}: формы на «ты» при ru_form: vy — «{TY_RE.search(plain).group(0)}»")
            if addr.get("capital_vy") is False and CAP_VY_RE.search(plain):
                errs.append(f"{s['id']}: «Вы» с заглавной в середине фразы")
        # 5. эмодзи
        em = EMOJI_RE.findall(t)
        pol = (punct.get("emoji") or {}).get("policy")
        if em and pol == "never":
            errs.append(f"{s['id']}: эмодзи при policy: never")
        if em and pol in ("rare", "allowed"):
            allowed = set((punct.get("emoji") or {}).get("allowed_slot_types") or [])
            if allowed and s["slot_type"] not in allowed:
                errs.append(f"{s['id']}: эмодзи в слоте {s['slot_type']} вне allowed_slot_types")
            mx = (punct.get("emoji") or {}).get("max_per_block")
            if mx is not None and len(em) > mx:
                errs.append(f"{s['id']}: эмодзи {len(em)} > max_per_block {mx}")
        # 6. восклицания
        ex = punct.get("exclamation") or {}
        if "!" in plain:
            if ex.get("policy") == "never":
                errs.append(f"{s['id']}: «!» при policy: never")
            if s.get("situation") in (ex.get("never_in") or []):
                errs.append(f"{s['id']}: «!» в ситуации {s['situation']} (never_in)")
        # 7. словарь «не говорим»
        for term, rx, lang in avoid:
            if lang in ("any", s["lang"][:2]) and rx.search(plain):
                errs.append(f"{s['id']}: слово из vocabulary.avoid «{term}»")
    # 8. use ∩ avoid
    use_terms = {u["term"].lower() for u in (voice.get("vocabulary") or {}).get("use") or []}
    for term, rx, _ in avoid:
        for u in use_terms:
            if rx.search(u):
                errs.append(f"vocabulary: «{u}» одновременно в use и avoid («{term}»)")
    # 9. проекция называет обращение
    tov = (voice.get("projections") or {}).get("tone_of_voice", "")
    form = {"vy": "«вы»", "ty": "«ты»"}.get(addr.get("ru_form"), "")
    if form and form not in tov:
        warns.append(f"projections.tone_of_voice не называет обращение {form}")
    # 10. принципы: проверяемое исполнение и пустые имена
    for p in voice.get("principles") or []:
        ex_text = " ".join(p.get("execution") or [])
        if not re.search(r"\d|«[^»]+»", ex_text):
            warns.append(f"принцип {p['id']}: в исполнении нет ни числа, ни «примера» — проверяемо ли оно?")
        words = [w for w in re.split(r"[\s,;]+", p["name"].strip().lower()) if w]
        if words and all(GENERIC.match(w) or w in ("и", "но", "мы") for w in words):
            warns.append(f"принцип {p['id']}: имя из пустых прилагательных «{p['name']}» (Ross: «what brand isn't?»)")
    return errs, warns


MUTATIONS = [
    ("принцип без execution", lambda v: v["principles"][0].pop("execution")),
    ("execution из одного правила", lambda v: v["principles"][0].__setitem__("execution", ["Короткие фразы до 12 слов"])),
    ("принцип без is_not", lambda v: v["principles"][0].pop("is_not")),
    ("один принцип", lambda v: v.__setitem__("principles", v["principles"][:1])),
    ("шесть принципов", lambda v: v.__setitem__("principles", (v["principles"] * 3)[:6])),
    ("одна пара «мы / мы не»", lambda v: v.__setitem__("pairs", v["pairs"][:1])),
    ("точка оси 6", lambda v: v["axes"]["formality"].__setitem__("point", 6)),
    ("нет оси enthusiasm", lambda v: v["axes"].pop("enthusiasm")),
    ("неизвестное слово тона", lambda v: v.setdefault("tone_words", {}).__setitem__("do", ["lovely"])),
    ("ru_form «Ты»", lambda v: v["address"].__setitem__("ru_form", "Ты")),
    ("юмор разрешён в праве (нет legal в never_in)", lambda v: v["humor"].__setitem__("never_in", [x for x in v["humor"]["never_in"] if x != "legal"])),
    ("tone_of_voice длиннее 240", lambda v: v["projections"].__setitem__("tone_of_voice", "На «вы». " + "очень " * 60)),
    ("неизвестный slot_type", lambda v: v["samples"][0].__setitem__("slot_type", "hero-title")),
    ("fact_id без префикса", lambda v: v["samples"][1].__setitem__("fact_ids", ["flats-completed"])),
    ("лишнее поле верхнего уровня", lambda v: v.__setitem__("mood", "тёплый")),
    ("допущение без вопроса", lambda v: v["derived_from"]["basis"].append({"kind": "assumption", "ref": "x"})),
    ("словарь avoid из двух слов", lambda v: v["vocabulary"].__setitem__("avoid", v["vocabulary"]["avoid"][:2])),
    ("образец на «ты» при «вы» (смысл)", lambda v: v["samples"][0].__setitem__("text", "Закажи замер сегодня")),
    ("эмодзи при never (смысл)", lambda v: v["punctuation"].__setitem__("emoji", {"policy": "never"}) or v["samples"][0].__setitem__("text", v["samples"][0]["text"] + " 🔥")),
    ("слово из avoid в образце (смысл)", lambda v: v["samples"][0].__setitem__("text", "Уникальная команда профессионалов")),
    ("факт, которого нет (смысл)", lambda v: v["samples"][0].__setitem__("fact_ids", ["fact:no-such-fact"])),
    ("adaptation_of в никуда (смысл)", lambda v: [s.__setitem__("adaptation_of", "ru-nowhere") for s in v["samples"] if s["lang"] == "en"]),
]


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    out = []
    ok = True

    def say(s=""):
        out.append(s)
        print(s)

    schema = load(SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    say(f"метасхема: OK ({SCHEMA.relative_to(ROOT)}, date {schema.get('date')})")
    vocab = {s["id"] for s in load(VOCAB)["slot_types"]}
    enum = set(schema["$defs"]["slot-type"]["enum"])
    if enum != vocab | PROPOSED_SLOTS:
        ok = False
        say(f"FAIL enum slot-type ≠ временный словарь: лишние {sorted(enum - vocab - PROPOSED_SLOTS)}, нет {sorted(vocab - enum)}")
    else:
        say(f"enum slot-type = временный словарь ({len(vocab)}) + предложения ({len(PROPOSED_SLOTS)}): OK")
    validator = jsonschema.Draft202012Validator(schema)
    paths = [Path(a) for a in argv] or EXAMPLES
    for p in paths:
        v = load(p)
        errs = sorted(validator.iter_errors(v), key=lambda e: list(e.path))
        base = p.resolve() in [e.resolve() for e in EXAMPLES]
        serr, swarn = semantic(v, p, base)
        status = "OK" if not errs and not serr else "FAIL"
        ok &= status == "OK"
        n_ru = len({s["slot_type"] for s in v.get("samples", []) if s["lang"].startswith("ru")})
        n_en = len({s["slot_type"] for s in v.get("samples", []) if s["lang"].startswith("en")})
        say(f"{status} {p.name}: схема {len(errs)} ошибок, смысл {len(serr)} ошибок, {len(swarn)} предупр.; "
            f"образцов {len(v.get('samples', []))} (слотов ru {n_ru}, en {n_en})")
        for e in errs[:10]:
            say(f"   схема: {'/'.join(map(str, e.path))}: {e.message[:160]}")
        for e in serr:
            say(f"   смысл: {e}")
        for w in swarn:
            say(f"   предупреждение: {w}")
    # мутации — на первом примере
    base_path = EXAMPLES[0]
    base_voice = load(base_path)
    caught = 0
    say(f"\nотрицательные мутации на {base_path.name}:")
    for name, fn in MUTATIONS:
        v = copy.deepcopy(base_voice)
        fn(v)
        errs = list(validator.iter_errors(v))
        serr, _ = semantic(v, base_path, True)
        hit = bool(errs or serr)
        caught += hit
        say(f"  {'пойман ' if hit else 'ПРОПУЩЕН'} {name}: схема {len(errs)}, смысл {len(serr)}")
    say(f"мутаций поймано: {caught} из {len(MUTATIONS)}")
    ok &= caught == len(MUTATIONS)
    say("validate_voice: " + ("OK" if ok else "FAIL"))
    (HERE / "last-run.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
