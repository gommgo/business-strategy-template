#!/usr/bin/env python3
"""validate_voice.py — проверка профилей голоса бренда (voice.yaml) и продукта (voice.product.yaml) по
voice.schema.yaml: схема и смысловые проверки.

Запуск (Python окружения скилла, нужны jsonschema и PyYAML):
    python3 scripts/text/validate_voice.py voice.yaml […]   профили проекта — печатаются только их находки
    python3 scripts/text/validate_voice.py                  схема и три примера базы 05-voice-editorial/examples/voice-*.yaml
                                                           (для них ≥ 8 типов слотов на язык)
    python3 scripts/text/validate_voice.py --selftest       то же и отрицательные мутации: профиль бренда из первого
                                                           примера и голос продукта, собранный из него в памяти

Проверки:
  1. метасхема Draft 2020-12; поле date; enum slot-type входит в слоты вида text словаря site
     (kb/site/02-site-types/vocabulary.yaml); слот словаря, которого нет в enum, — справка, не ошибка (строки схемы —
     без файлов и в самопроверке; с файлами проекта схема проверяется молча, сбой — ошибка запуска);
  2. каждый профиль валиден по схеме;
  3. смысловые (схема их не видит): образцы против обращения («ты» при ru_form: vy; «Вы» в середине фразы), эмодзи,
     восклицаний, словаря «не говорим»; ссылки fact:/missing: разрешаются в facts_ref; adaptation_of указывает на
     русский образец; use ∩ avoid = ∅; tone_of_voice называет обращение; у принципа есть проверяемое исполнение
     (число или «цитата» хотя бы в одном правиле); пустые принципы-прилагательные («честные», «надёжные») — предупреждение;
  4. голос продукта — профиль, у которого все scope.surfaces[].voice — product: жанр interface; юмора нет в ситуациях
     service-error, destructive-action, money, security; образцы — по роли строки интерфейса (role), не по slot_type;
     «!» нет в success-routine и destructive-action; карта тона без service-error, destructive-action или money и
     ситуации только сайта в ней — предупреждения. У профиля бренда образец только с role — предупреждение;
  5. отрицательные мутации (только --selftest; профиль бренда и голос продукта): каждая обязана дать ошибку схемы или
     смысловую ошибку.
Выход: 0 — всё прошло; 1 — есть ошибки. Итог печатается и пишется в $DDD_HOME/out/text/validate_voice.last-run.txt.
"""
import copy
import re
import sys
from pathlib import Path

import yaml

try:
    import jsonschema
except ImportError:  # pragma: no cover
    sys.exit("нужен jsonschema: запускайте Python окружения скилла")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("text")
SCHEMA = ROOT / "05-voice-editorial" / "voice.schema.yaml"
EXAMPLES = sorted((ROOT / "05-voice-editorial" / "examples").glob("voice-*.yaml"))
VOCAB = kbpaths.kb("site", "02-site-types", "vocabulary.yaml")   # словарь id системы: слоты вида text
# голос продукта: ситуации интерфейса, где юмора нет (x-situations схемы), и ситуации без «!»
PRODUCT_NO_HUMOR = ("service-error", "destructive-action", "money", "security")
PRODUCT_NO_EXCLAMATION = ("success-routine", "destructive-action")
PRODUCT_TONE_MAP = ("service-error", "destructive-action", "money")
SITE_ONLY_SITUATIONS = {"hero", "benefits", "how-it-works", "proof", "testimonials", "case", "pricing", "objections", "faq",
                        "about", "careers", "article", "meta", "campaign-slogan", "footer"}

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


def is_product(voice: dict) -> bool:
    """Голос продукта — все поверхности профиля с voice: product."""
    surf = (voice.get("scope") or {}).get("surfaces") or []
    return bool(surf) and all(s.get("voice") == "product" for s in surf)


def semantic_product(voice: dict) -> tuple[list, list]:
    """Проверки голоса продукта (интерфейс за входом, письма и уведомления продукта)."""
    errs, warns = [], []
    if "interface" not in ((voice.get("scope") or {}).get("genres") or []):
        errs.append("голос продукта: в scope.genres нет interface")
    never = set((voice.get("humor") or {}).get("never_in") or [])
    miss = [x for x in PRODUCT_NO_HUMOR if x not in never]
    if miss:
        errs.append(f"голос продукта: юмор не запрещён в {', '.join(miss)} (humor.never_in)")
    for s in voice.get("samples") or []:
        if not s.get("role"):
            errs.append(f"{s['id']}: образец голоса продукта — по роли строки интерфейса (role), а не по slot_type")
        if s.get("situation") in PRODUCT_NO_EXCLAMATION and "!" in QUOTE_RE.sub(" ", s.get("text", "")):
            errs.append(f"{s['id']}: «!» в ситуации {s['situation']} — у голоса продукта сухой тон")
    tm = [t.get("situation") for t in voice.get("tone_map") or []]
    for x in PRODUCT_TONE_MAP:
        if x not in tm:
            warns.append(f"голос продукта: в карте тона нет ситуации {x}")
    site_only = sorted({x for x in tm if x in SITE_ONLY_SITUATIONS})
    if site_only:
        warns.append(f"голос продукта: в карте тона ситуации сайта {', '.join(site_only)} — их тон задаёт профиль бренда")
    return errs, warns


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
    product = is_product(voice)
    # 1. типы слотов (у голоса продукта — роли строк) по языкам
    by_lang: dict = {}
    for s in samples:
        by_lang.setdefault(s["lang"][:2], set()).add(s.get("role") if product else s.get("slot_type"))
    if base_example:
        for lg in ("ru", "en"):
            n = len(by_lang.get(lg, set()) - {None})
            if n < 8:
                errs.append(f"образцов {lg}: {n} {'ролей строк' if product else 'типов слотов'}, нужно ≥ 8 (образец базы)")
    if product:
        perr, pwarn = semantic_product(voice)
        errs += perr
        warns += pwarn
    else:
        for s in samples:
            if s.get("role") and not s.get("slot_type"):
                warns.append(f"{s['id']}: образец по роли строки интерфейса в профиле бренда — его место в голосе продукта")
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
            if allowed and s.get("slot_type") not in allowed:
                errs.append(f"{s['id']}: эмодзи в слоте {s.get('slot_type') or s.get('role')} вне allowed_slot_types")
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

# роль строки интерфейса для образца бренда, из которого в памяти собирается голос продукта
SLOT_TO_ROLE = {"headline": "title", "subheadline": "subtitle", "hero-proof": "caption", "cta-label": "action",
                "cta-secondary-label": "link", "cta-note": "hint", "card-title": "title", "card-body": "caption",
                "section-title": "section-title", "form-title": "title", "form-success": "toast", "form-consent": "checkbox-label",
                "faq-q": "help", "faq-a": "help", "email-subject": "email", "email-body": "email", "guarantee-text": "inline-message",
                "pricing-price-note": "hint", "nav-label": "nav", "badge": "badge", "image-alt": "alt"}


def product_variant(brand: dict) -> dict:
    """Голос продукта в памяти из профиля бренда: поверхности продукта, жанр interface, юмора нет в ситуациях
    интерфейса с риском, карта тона по ситуациям интерфейса, образцы — по ролям строк."""
    v = copy.deepcopy(brand)
    v["voice_id"] = v["voice_id"] + "-product"
    v["scope"] = {"genres": ["interface"],
                  "surfaces": [{"surface": "product-ui", "voice": "product"}, {"surface": "transactional-emails", "voice": "product"}]}
    never = list(v["humor"].get("never_in") or [])
    v["humor"]["never_in"] = never + [x for x in PRODUCT_NO_HUMOR if x not in never]
    v["humor"]["allowed_in"] = [x for x in v["humor"].get("allowed_in") or [] if x not in PRODUCT_NO_HUMOR and x not in SITE_ONLY_SITUATIONS]
    v["tone_map"] = [{"situation": "service-error", "rules": ["Признаём сбой прямо: что случилось, что уже делаем, что сделать сейчас"]},
                     {"situation": "destructive-action", "rules": ["Называем, что удалится и можно ли вернуть; без «Вы уверены?»"]},
                     {"situation": "money", "rules": ["Сумма полностью, с валютой и сроком списания"]},
                     {"situation": "empty-first-use", "rules": ["Одна строка, что здесь появится, и одно действие"]}]
    for s in v["samples"]:
        s["role"] = SLOT_TO_ROLE.get(s.pop("slot_type"), "caption")
        if s.get("situation") in SITE_ONLY_SITUATIONS:
            s.pop("situation")
    return v


PRODUCT_MUTATIONS = [
    ("голос продукта: юмор не запрещён в service-error", lambda v: v["humor"].__setitem__("never_in", [x for x in v["humor"]["never_in"] if x != "service-error"])),
    ("голос продукта: нет жанра interface", lambda v: v["scope"].__setitem__("genres", ["landing"])),
    ("голос продукта: образец по slot_type без role", lambda v: v["samples"][0].pop("role") and v["samples"][0].__setitem__("slot_type", "headline")),
    ("голос продукта: «!» в деструктивном действии", lambda v: v["samples"][0].update(situation="destructive-action", text="Удалить проект!")),
    ("голос продукта: неизвестная роль строки", lambda v: v["samples"][0].__setitem__("role", "hero-title")),
    ("голос продукта: неизвестная ситуация", lambda v: v["tone_map"][0].__setitem__("situation", "checkout")),
]


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__.strip())
        return 0
    selftest = "--selftest" in argv
    files = [] if selftest else [Path(a) for a in argv]   # файлы проекта — только их находки
    out = []
    ok = True

    def say(s=""):
        out.append(s)
        print(s)

    schema = load(SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    if not files:
        say(f"метасхема: OK ({SCHEMA.relative_to(ROOT)}, date {schema.get('date')})")
        slots = ((load(VOCAB).get("namespaces") or {}).get("slot") or {}).get("values") or []
        vocab = {s["id"] for s in slots if isinstance(s, dict) and s.get("kind") == "text"}
        enum = set(schema["$defs"]["slot-type"]["enum"])
        if enum - vocab:
            ok = False
            say(f"FAIL enum slot-type вне словаря site (слоты вида text): {sorted(enum - vocab)}")
        else:
            say(f"enum slot-type ({len(enum)}) — слоты вида text словаря site ({len(vocab)}): OK")
        if vocab - enum:
            say(f"справка: слоты вида text словаря site без образцов голоса в enum — {', '.join(sorted(vocab - enum))}")
    validator = jsonschema.Draft202012Validator(schema)
    paths = files or EXAMPLES
    for p in paths:
        v = load(p)
        errs = sorted(validator.iter_errors(v), key=lambda e: list(e.path))
        base = p.resolve() in [e.resolve() for e in EXAMPLES]
        serr, swarn = semantic(v, p, base)
        status = "OK" if not errs and not serr else "FAIL"
        ok &= status == "OK"
        kind = "role" if is_product(v) else "slot_type"
        n_ru = len({s.get(kind) for s in v.get("samples", []) if s["lang"].startswith("ru")})
        n_en = len({s.get(kind) for s in v.get("samples", []) if s["lang"].startswith("en")})
        say(f"{status} {p.name}{' (голос продукта)' if kind == 'role' else ''}: схема {len(errs)} ошибок, смысл {len(serr)} ошибок, "
            f"{len(swarn)} предупр.; образцов {len(v.get('samples', []))} ({'ролей' if kind == 'role' else 'слотов'} ru {n_ru}, en {n_en})")
        for e in errs[:10]:
            say(f"   схема: {'/'.join(map(str, e.path))}: {e.message[:160]}")
        for e in serr:
            say(f"   смысл: {e}")
        for w in swarn:
            say(f"   предупреждение: {w}")
    if selftest:
        ok &= mutations(validator, say)
    say("validate_voice: " + ("OK" if ok else "FAIL"))
    (kbpaths.out("text") / "validate_voice.last-run.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    return 0 if ok else 1


def mutations(validator, say) -> bool:
    """Самопроверка: отрицательные мутации профиля бренда (первый пример базы) и голоса продукта, собранного из него в
    памяти, — каждая обязана дать ошибку; чистый голос продукта проходит."""
    ok = True
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
    # голос продукта в памяти: чистый профиль проходит, мутации ловятся
    prod = product_variant(base_voice)
    perrs = list(validator.iter_errors(prod))
    pserr, pswarn = semantic(prod, base_path, True)
    pok = not perrs and not pserr
    ok &= pok
    say(f"\n{'OK' if pok else 'FAIL'} голос продукта из {base_path.name} (в памяти): схема {len(perrs)} ошибок, смысл {len(pserr)} ошибок, "
        f"{len(pswarn)} предупр.")
    for e in perrs[:10]:
        say(f"   схема: {'/'.join(map(str, e.path))}: {e.message[:160]}")
    for e in pserr + [f"предупреждение: {w}" for w in pswarn]:
        say(f"   {e}")
    pcaught = 0
    for name, fn in PRODUCT_MUTATIONS:
        v = copy.deepcopy(prod)
        fn(v)
        errs = list(validator.iter_errors(v))
        serr, _ = semantic(v, base_path, True)
        hit = bool(errs or serr)
        pcaught += hit
        say(f"  {'пойман ' if hit else 'ПРОПУЩЕН'} {name}: схема {len(errs)}, смысл {len(serr)}")
    v = copy.deepcopy(prod)
    v["tone_map"] = [t for t in v["tone_map"] if t["situation"] != "money"] + [{"situation": "hero", "rules": ["Коротко"]}]
    _, w = semantic(v, base_path, True)
    wok = any("money" in x for x in w) and any("ситуации сайта hero" in x for x in w)
    pcaught += wok
    say(f"  {'пойман ' if wok else 'ПРОПУЩЕН'} голос продукта: карта тона без money и с ситуацией сайта — предупреждения")
    say(f"мутаций голоса продукта поймано: {pcaught} из {len(PRODUCT_MUTATIONS) + 1}")
    ok &= pcaught == len(PRODUCT_MUTATIONS) + 1
    return ok


if __name__ == "__main__":
    sys.exit(main())
