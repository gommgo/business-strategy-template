#!/usr/bin/env python3
"""vocab_lint.py — идентификаторы вне словаря site в YAML, JSON и Markdown; проверка таблицы соответствий словарей.

Словарь: kb/site/02-site-types/vocabulary.yaml (пространства имён site_type, page_type, section_role, block_family,
block, slot_kind, slot, macrostructure, first_screen_policy, action, awareness, traffic_temperature, traffic_source,
jurisdiction, ambition_level, conversion_channel, procedure_step).

Что проверяет:
  1. значения ключей из карты «ключ → пространство» (по умолчанию — ключи blocks.yaml, page-plan, site-map, site-brief,
     чек-листа: page_type, role, block, slot, action, awareness …) на любой глубине; значение — строка или список строк;
     у copy deck сверяются slot_type, section_role, block и page_type — локальный slot_id и действие страницы словами
     в карту не входят; у facts.yaml и голоса клиента — места use (типы страниц, роли секций, типы слотов), а роли
     людей (owner, responsible, attribution) — нет; у смысла — тип слота места ответа на возражение
     (where.slot_type), у голоса — тип слота образца (samples.slot_type); у плана ассетов и манифеста ассетов роль
     ассета (slots.role, assets.role: informational, decorative) — не роль секции и в карту не входит;
  2. ссылки с префиксом пространства в любой строке и в Markdown: block:hero-media, slot:headline, section-role:faq,
     page-type:…, site-type:…, action:…, macrostructure:… (чужие префиксы effect:, fact:, task:, recipe:, copy-rule: —
     пропускаются: их словари ведут владельцы);
  3. ключи-идентификаторы (--keys-as-ids blocks=block: дочерние ключи словаря blocks — id блоков);
  4. статусы: deprecated — предупреждение с заменой; out-of-scope — предупреждение; measurement-only — ошибка (кроме
     --allow-measurement); proposed — сведение;
  5. --check-crosswalk — таблица соответствий kb/site/02-site-types/crosswalk.tsv (другой файл — --crosswalk): колонки
     строго по формату, отношение relation из перечня equal · narrower · broader · related · none, наш id our_id есть в
     словаре своего пространства, у none — our_id пуст и причина в note; deprecated и повтор строки — предупреждение.
Выход: строки «путь:строка: уровень пространство 'id' — сообщение»; сводка; код 1 при ошибках, 0 — без ошибок.
Подсказки: ближайший id (опечатка) и, с --crosswalk, строка таблицы соответствия (чужой термин → наш id).

Примеры (от корня скилла):
  python3 scripts/site/vocab_lint.py kb/site/04-blocks/blocks.yaml kb/site/10-playbooks-contracts/examples/*/plans/*.yaml
  python3 scripts/site/vocab_lint.py plan.yaml --map section=section_role --crosswalk kb/site/02-site-types/crosswalk.tsv --stats
  python3 scripts/site/vocab_lint.py --check-crosswalk
  python3 scripts/site/vocab_lint.py --selftest
"""
import argparse
import csv
import difflib
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("site")
DEFAULT_VOCAB = ROOT / "02-site-types" / "vocabulary.yaml"
DEFAULT_CROSSWALK = ROOT / "02-site-types" / "crosswalk.tsv"
CROSSWALK_COLS = ("source_base", "source_file", "source_section", "source_vocab", "source_term", "namespace", "our_id",
                  "relation", "note")
RELATIONS = ("equal", "narrower", "broader", "related", "none")

DEFAULT_MAP = {
    "site_type": "site_type", "site_types": "site_type",
    "page_type": "page_type", "page_types": "page_type",
    "role": "section_role", "section_role": "section_role", "section_roles": "section_role", "serves": "section_role",
    "block": "block", "blocks_allowed": "block", "block_family": "block_family", "family": "block_family",
    "slot": "slot", "slot_kind": "slot_kind",
    "macrostructure": "macrostructure", "first_screen_policy": "first_screen_policy",
    "action": "action", "actions": "action", "primary_action": "action", "secondary_actions": "action",
    "awareness": "awareness",
    "temperature": "traffic_temperature", "traffic_temperature": "traffic_temperature",
    "traffic_source": "traffic_source", "traffic_sources": "traffic_source",
    "jurisdiction": "jurisdiction", "ambition_level": "ambition_level", "ambition": "ambition_level",
    # None — ключ не несёт id словаря site: роль референса references[].role (rhythm, composition, color …) —
    # не section_role
    "references.role": None,
    # поля site-brief, одноимённые ключам плана, но не id словаря: роль в аудитории и языке, раздел брифа у вопроса
    "audience.role": None, "languages.role": None, "questions.block": None, "versions.role": None,
    # copy deck: тип слота словаря — slot_type слота секции, а slot_id — локальный id слота плана и в карту не входит;
    # действие страницы записано словами страницы, role у текста в кадре — его место в кадре
    "slots.slot_type": "slot", "pages.primary_action": None, "in_image.role": None,
    # facts.yaml: роль владельца инвентаря, ответственного за факт и автора отзыва — должность словами
    "owner.role": None, "responsible.role": None, "attribution.role": None,
    # план ассетов (slots[].role) и манифест ассетов (assets[].role): роль ассета — informational или decorative,
    # а не роль секции
    "slots.role": None, "assets.role": None,
    # типы слотов вне плана и copy deck: места use фактов и голоса клиента, место ответа на возражение в смысле,
    # образец строки в голосе
    "use.slot_types": "slot", "where.slot_type": "slot", "samples.slot_type": "slot",
}
PREFIX_RE = re.compile(r"(?<![\w/.-])(site-type|page-type|section-role|block-family|block|slot-kind|slot|macrostructure|first-screen-policy|"
                       r"action|awareness|traffic-temperature|traffic-source|jurisdiction|ambition):([A-Za-z0-9][A-Za-z0-9-]*)")


class Vocab:
    def __init__(self, data):
        self.data = data
        self.prefixes = dict(data.get("ref_prefixes") or {})
        self.ids, self.status, self.replaced = {}, {}, {}
        for ns, body in (data.get("namespaces") or {}).items():
            self.ids[ns] = set()
            for v in body.get("values") or []:
                i = str(v["id"])
                self.ids[ns].add(i)
                self.status[(ns, i)] = v.get("status", "active")
                if v.get("replaced_by"):
                    self.replaced[(ns, i)] = v["replaced_by"]

    @classmethod
    def load(cls, path):
        return cls(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


class Crosswalk:
    ORDER = {"equal": 0, "narrower": 1, "related": 2, "broader": 3}

    def __init__(self, path=None, bases=None):
        self.by_term = defaultdict(list)
        if path:
            with open(path, encoding="utf-8") as fh:
                for r in csv.DictReader(fh, delimiter="\t"):
                    if bases and r["source_base"] not in bases:
                        continue
                    self.by_term[r["source_term"].strip().lower()].append(r)

    def hint(self, term):
        rows = self.by_term.get(str(term).strip().lower(), [])
        if not rows:
            return None, "absent"
        mapped = sorted((r for r in rows if r["relation"] != "none"), key=lambda r: self.ORDER.get(r["relation"], 9))
        if mapped:
            r = mapped[0]
            more = f" (+ ещё {len(mapped) - 1})" if len(mapped) > 1 else ""
            return (f"crosswalk: {r['source_base']} «{term}» → {r['namespace']}:{r['our_id']} ({r['relation']}){more}",
                    "mapped")
        return f"crosswalk: «{term}» — соответствия нет ({rows[0]['note'][:80]})", "none"


class Finding:
    def __init__(self, path, line, level, ns, value, msg):
        self.path, self.line, self.level, self.ns, self.value, self.msg = path, line, level, ns, value, msg

    def __str__(self):
        return f"{self.path}:{self.line}: {self.level} {self.ns} '{self.value}' — {self.msg}"


class Linter:
    def __init__(self, vocab, keymap, keys_as_ids=None, allow_measurement=False, crosswalk=None):
        self.v, self.keymap, self.kai = vocab, keymap, keys_as_ids or {}
        self.allow_measurement, self.cw = allow_measurement, crosswalk or Crosswalk()
        self.findings, self.checked = [], Counter()
        self.cw_stats = Counter()

    def check_id(self, path, line, ns, value, how):
        value = str(value).strip()
        if not value:
            return
        self.checked[ns] += 1
        if ns not in self.v.ids:
            self.findings.append(Finding(path, line, "error", ns, value, f"неизвестное пространство ({how})"))
            return
        if value in self.v.ids[ns]:
            st = self.v.status.get((ns, value), "active")
            if st == "deprecated":
                rep = self.v.replaced.get((ns, value))
                self.findings.append(Finding(path, line, "warn", ns, value, f"deprecated — замените на {rep}" if rep else "deprecated"))
            elif st == "out-of-scope":
                self.findings.append(Finding(path, line, "warn", ns, value, "вне рамок базы (out-of-scope)"))
            elif st == "measurement-only" and not self.allow_measurement:
                self.findings.append(Finding(path, line, "error", ns, value, "только для замеров (measurement-only) — в плане запрещён"))
            elif st == "proposed":
                self.findings.append(Finding(path, line, "info", ns, value, "proposed — ждёт подтверждения владельца"))
            return
        msg = f"нет в словаре ({how})"
        near = difflib.get_close_matches(value, sorted(self.v.ids[ns]), n=1, cutoff=0.75)
        if near:
            msg += f"; возможно, {near[0]}"
        hint, kind = self.cw.hint(value)
        self.cw_stats[kind] += 1
        if hint:
            msg += f"; {hint}"
        self.findings.append(Finding(path, line, "error", ns, value, msg))

    def scan_string(self, path, line, text):
        for m in PREFIX_RE.finditer(text):
            ns = self.v.prefixes.get(m.group(1))
            if ns:
                self.check_id(path, line, ns, m.group(2), f"ссылка {m.group(1)}:")

    def ns_for(self, keys):
        """Пространство для пути ключей: сначала самый длинный суффикс с точками (site.sections.id), потом имя ключа."""
        best, best_len = None, 0
        for k, ns in self.keymap.items():
            parts = k.split(".")
            if len(parts) <= len(keys) and keys[-len(parts):] == parts and len(parts) > best_len:
                best, best_len = (k, ns), len(parts)
        return best

    def walk(self, path, node, keys=()):
        if isinstance(node, yaml.MappingNode):
            for knode, vnode in node.value:
                k = knode.value if isinstance(knode, yaml.ScalarNode) else None
                kk = keys + (k,)
                hit = self.kai.get(k) or self.kai.get(".".join(kk[-2:]))
                if hit and isinstance(vnode, yaml.MappingNode):
                    for ck, _ in vnode.value:
                        if isinstance(ck, yaml.ScalarNode):
                            self.check_id(path, ck.start_mark.line + 1, hit, ck.value, f"ключ-id в «{k}»")
                self.walk(path, vnode, kk)
        elif isinstance(node, yaml.SequenceNode):
            for item in node.value:
                self.walk(path, item, keys)
        elif isinstance(node, yaml.ScalarNode):
            line = node.start_mark.line + 1
            hit = self.ns_for(list(keys)) if keys else None
            if hit and hit[1] is None:
                self.scan_string(path, line, node.value)
            elif hit and node.tag.endswith(":str") and node.value not in ("", "~", "null"):
                self.check_id(path, line, hit[1], node.value, f"ключ «{hit[0]}»")
            elif isinstance(node.value, str):
                self.scan_string(path, line, node.value)

    def lint_file(self, path):
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        if p.suffix.lower() in (".md", ".markdown", ".txt"):
            for n, line in enumerate(text.splitlines(), 1):
                self.scan_string(str(path), n, line)
            return
        try:
            for doc in yaml.compose_all(text, Loader=yaml.SafeLoader):
                if doc is not None:
                    self.walk(str(path), doc)
        except yaml.YAMLError as exc:
            self.findings.append(Finding(str(path), getattr(getattr(exc, "problem_mark", None), "line", -1) + 1,
                                         "error", "-", "-", f"не разбирается как YAML или JSON: {exc}".splitlines()[0]))

    def lint_crosswalk(self, path):
        """Таблица соответствий: колонки строго, relation из перечня, our_id — id словаря своего пространства; у none
        our_id пуст, причина — в note. Чужой термин без нашего id — только строкой none."""
        p = str(path)
        with open(path, encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh, delimiter="\t"))
        if not rows or tuple(c.strip() for c in rows[0]) != CROSSWALK_COLS:
            self.findings.append(Finding(p, 1, "error", "-", "-", f"колонки {rows[0] if rows else []} — нужны строго: "
                                                                   f"{', '.join(CROSSWALK_COLS)}"))
            return
        seen = {}
        for n, row in enumerate(rows[1:], 2):
            if not any(c.strip() for c in row):
                continue
            if len(row) != len(CROSSWALK_COLS):
                self.findings.append(Finding(p, n, "error", "-", "-", f"полей {len(row)} вместо {len(CROSSWALK_COLS)}"))
                continue
            r = dict(zip(CROSSWALK_COLS, (c.strip() for c in row)))
            ns, oid, rel, term = r["namespace"], r["our_id"], r["relation"], r["source_term"]
            self.checked["crosswalk"] += 1
            key = (r["source_base"], r["source_file"], r["source_vocab"], term, ns, oid)
            if key in seen:
                self.findings.append(Finding(p, n, "warn", ns or "-", term or "-", f"повтор строки {seen[key]}"))
            seen.setdefault(key, n)
            if not term:
                self.findings.append(Finding(p, n, "error", ns or "-", "-", "пустой source_term"))
            if rel not in RELATIONS:
                self.findings.append(Finding(p, n, "error", ns or "-", oid or term or "-",
                                             f"relation {rel!r} не из перечня: {', '.join(RELATIONS)}"))
                continue
            if rel == "none":
                if oid:
                    self.findings.append(Finding(p, n, "error", ns or "-", oid, "relation none — our_id пуст"))
                if not r["note"]:
                    self.findings.append(Finding(p, n, "warn", ns or "-", term, "relation none без причины в note"))
                continue
            if ns not in self.v.ids:
                self.findings.append(Finding(p, n, "error", ns or "-", oid or "-", "неизвестное пространство словаря"))
                continue
            if not oid:
                self.findings.append(Finding(p, n, "error", ns, term, f"relation {rel} без our_id"))
                continue
            if oid not in self.v.ids[ns]:
                near = difflib.get_close_matches(oid, sorted(self.v.ids[ns]), n=1, cutoff=0.75)
                self.findings.append(Finding(p, n, "error", ns, oid, "нет в словаре" + (f"; возможно, {near[0]}" if near else "")))
                continue
            if self.v.status.get((ns, oid)) == "deprecated":
                rep = self.v.replaced.get((ns, oid))
                self.findings.append(Finding(p, n, "warn", ns, oid, f"deprecated — замените на {rep}" if rep else "deprecated"))


def build_keymap(args):
    km = {} if args.no_default_map else dict(DEFAULT_MAP)
    for pair in args.map or []:
        k, _, ns = pair.partition("=")
        km[k.strip()] = ns.strip()
    return km


def run(files, vocab, keymap, kai, allow_measurement=False, crosswalk=None):
    lin = Linter(vocab, keymap, kai, allow_measurement, crosswalk)
    for f in files:
        lin.lint_file(f)
    return lin


def report(lin, quiet_info=True, stats=False):
    shown = [f for f in lin.findings if not (quiet_info and f.level == "info")]
    for f in sorted(shown, key=lambda x: (x.path, x.line)):
        print(f)
    c = Counter(f.level for f in lin.findings)
    print(f"-- проверено id: {sum(lin.checked.values())} ({dict(lin.checked)}); ошибок {c['error']}, "
          f"предупреждений {c['warn']}, proposed {c['info']}")
    if stats and lin.cw_stats:
        print(f"-- crosswalk по неизвестным id: {dict(lin.cw_stats)} (mapped — есть наш id; none — соответствия нет; "
              f"absent — термина нет в таблице)")
    return 1 if c["error"] else 0


def selftest():
    voc = Vocab({
        "ref_prefixes": {"block": "block", "slot": "slot", "section-role": "section_role", "page-type": "page_type"},
        "namespaces": {
            "block": {"values": [{"id": "hero-media"}, {"id": "logo-wall"}, {"id": "other", "status": "measurement-only"},
                                 {"id": "hero-old", "status": "deprecated", "replaced_by": "hero-media"}]},
            "slot": {"values": [{"id": "headline"}, {"id": "cta-primary"}, {"id": "hero-visual"},
                                {"id": "price-old", "status": "proposed"}]},
            "section_role": {"values": [{"id": "hero"}, {"id": "faq"}]},
            "page_type": {"values": [{"id": "landing-saas"}, {"id": "ecommerce-product-page", "status": "out-of-scope"}]},
            "action": {"values": [{"id": "lead-request"}]},
        }})
    cases = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "ok.yaml").write_text("page_type: landing-saas\nsections:\n  - role: hero\n    block: hero-media\n"
                                    "    slots: [{slot: headline}, {slot: cta-primary, action: lead-request}]\n"
                                    "    note: \"см. block:logo-wall и effect:glow\"\n", encoding="utf-8")
        cases.append(("ok.yaml — чисто", ["ok.yaml"], {}, 0, 0))
        (td / "typo.yaml").write_text("sections:\n  - role: hero\n    block: hero-medai\n", encoding="utf-8")
        cases.append(("опечатка в id блока ловится", ["typo.yaml"], {}, 1, 1))
        (td / "status.yaml").write_text("page_type: ecommerce-product-page\nsections:\n  - block: hero-old\n"
                                        "  - block: other\n  - slots: [{slot: price-old}]\n", encoding="utf-8")
        cases.append(("deprecated и out-of-scope — warn, measurement-only — error", ["status.yaml"], {}, 1, 1))
        (td / "ref.md").write_text("Пункт SITE-X: `block:logo-wal` и `section-role:faq`, `fact:f-01` — чужое.\n",
                                   encoding="utf-8")
        cases.append(("префиксная ссылка в Markdown", ["ref.md"], {}, 1, 1))
        (td / "plan.json").write_text(json.dumps({"page_type": "landing-sass", "blocks": {"hero-media": {}, "logo-walll": {}}},
                                                 indent=2), encoding="utf-8")
        cases.append(("JSON: page_type и ключи-id", ["plan.json"], {"blocks": "block"}, 1, 2))
        (td / "list.yaml").write_text("actions: [lead-request, lead-requst]\n", encoding="utf-8")
        cases.append(("список значений", ["list.yaml"], {}, 1, 1))
        (td / "dotted.yaml").write_text("site:\n  sections:\n    - {id: hero}\n    - {id: final_cta}\n"
                                        "facts:\n  - {id: F1}\n", encoding="utf-8")
        cases.append(("ключ с точкой: только site.sections.id", ["dotted.yaml"], {}, 1, 1))
        (td / "deck.yaml").write_text(
            "copy_deck:\n  pages:\n    - page_id: home\n      page_type: landing-saas\n      primary_action: Записаться на замер\n"
            "      sections:\n        - section_id: hero\n          section_role: hero\n          block: hero-media\n"
            "          slots:\n            - {slot_id: main-title, slot_type: headline}\n"
            "            - {slot_id: note, slot_type: headlin}\n"
            "            - {slot_id: banner, slot_type: cta-primary, in_image: [{role: sign, text: Открыто}]}\n",
            encoding="utf-8")
        cases.append(("copy deck: slot_type сверяется; slot_id, действие словами и role текста в кадре — нет",
                      ["deck.yaml"], {}, 1, 1))
        (td / "facts.yaml").write_text(
            "owner: {role: маркетолог}\nfacts:\n  - id: f1\n    responsible: {role: юрист}\n"
            "    attribution: {role: владелец кофейни}\n"
            "    use: {page_types: [landing-saas], section_roles: [hero, heroo]}\n", encoding="utf-8")
        cases.append(("facts.yaml: места use сверяются, роли людей — нет", ["facts.yaml"], {}, 1, 1))
        (td / "assets.yaml").write_text(
            "page: {page_type: landing-saas}\nslots:\n"
            "  - {id: hero-shot, section: hero, slot: hero-visual, role: informational}\n"
            "  - {id: backdrop, section: hero, slot: hero-visul, role: decorative}\n"
            "assets:\n  - {file: hero-shot.webp, role: informational}\n", encoding="utf-8")
        cases.append(("план и манифест ассетов: роль ассета — не роль секции, вид слота сверяется",
                      ["assets.yaml"], {}, 1, 1))
        (td / "slot-types.yaml").write_text(
            "meaning:\n  objections:\n    - id: o1\n"
            "      where: [{section_role: faq, slot_type: headline}, {section_role: hero, slot_type: headlne}]\n"
            "voice:\n  samples:\n    - {id: s1, slot_type: cta-primary, lang: ru, text: Записаться}\n"
            "    - {id: s2, slot_type: cta-primry, lang: ru, text: Узнать}\n"
            "facts:\n  - id: f1\n    use: {slot_types: [headline, hedline]}\n", encoding="utf-8")
        cases.append(("типы слотов в смысле, голосе и местах use сверяются", ["slot-types.yaml"], {}, 1, 3))
        ok = True
        for name, files, kai, code_exp, err_exp in cases:
            km = dict(DEFAULT_MAP)
            if name.startswith("ключ с точкой"):
                km = {"sections.id": "section_role"}
            lin = run([td / f for f in files], voc, km, kai)
            errs = [f for f in lin.findings if f.level == "error"]
            code = 1 if errs else 0
            good = code == code_exp and len(errs) == err_exp
            if name.startswith("опечатка"):
                good = good and "возможно, hero-media" in errs[0].msg and errs[0].line == 3
            if name.startswith("deprecated"):
                warns = [f for f in lin.findings if f.level == "warn"]
                good = good and len(warns) == 2 and any("замените на hero-media" in w.msg for w in warns)
            if name.startswith("JSON"):
                good = good and all(e.line > 0 for e in errs)
            if name.startswith("ключ с точкой"):
                good = good and errs[0].value == "final_cta"
            if name.startswith("copy deck"):
                good = good and errs[0].value == "headlin" and "возможно, headline" in errs[0].msg
            if name.startswith("facts.yaml"):
                good = good and errs[0].value == "heroo"
            if name.startswith("план и манифест ассетов"):
                good = good and errs[0].value == "hero-visul" and errs[0].ns == "slot"
            if name.startswith("типы слотов"):
                good = good and sorted(e.value for e in errs) == ["cta-primry", "headlne", "hedline"]
            ok &= good
            print(("PASS " if good else "FAIL ") + name + f" (код {code}, ошибок {len(errs)})")
        # приоритет relation в подсказке crosswalk
        cwf = td / "cw.tsv"
        cwf.write_text("source_base\tsource_file\tsource_section\tsource_vocab\tsource_term\tnamespace\tour_id\trelation\tnote\n"
                       "x\tf\ts\tv\tsaas-landing\tpage_type\tcomparison-page\tbroader\t\n"
                       "x\tf\ts\tv\tsaas-landing\tpage_type\tlanding-saas\tequal\t\n", encoding="utf-8")
        h, kind = Crosswalk(cwf).hint("saas-landing")
        good = kind == "mapped" and "landing-saas (equal)" in h
        ok &= good
        print(("PASS " if good else "FAIL ") + "подсказка crosswalk: equal раньше broader")
        # таблица соответствий: колонки, relation из перечня, наш id в словаре, у none — пустой our_id и причина
        rows = [("saas-landing", "page_type", "landing-saas", "equal", ""),      # 2 — чисто
                ("hero-big", "block", "hero-medai", "equal", ""),               # 3 — нет в словаре
                ("faq-page", "section_role", "faq", "same", ""),                # 4 — relation не из перечня
                ("shop", "page_type", "landing-saas", "none", "вне рамок"),     # 5 — none с our_id
                ("thing", "mystery", "thing", "equal", ""),                     # 6 — неизвестное пространство
                ("price", "slot", "", "none", ""),                              # 7 — none без причины: warn
                ("saas-landing", "page_type", "landing-saas", "equal", ""),     # 8 — повтор строки 2: warn
                ("old", "block", "hero-old", "equal", "")]                      # 9 — deprecated: warn
        (td / "cw-check.tsv").write_text("\t".join(CROSSWALK_COLS) + "\n" + "".join(
            f"x\tf\ts\tv\t{t}\t{ns}\t{oid}\t{rel}\t{note}\n" for t, ns, oid, rel, note in rows), encoding="utf-8")
        lin = Linter(voc, {})
        lin.lint_crosswalk(td / "cw-check.tsv")
        errs = sorted(f.line for f in lin.findings if f.level == "error")
        warns = sorted(f.line for f in lin.findings if f.level == "warn")
        good = (errs == [3, 4, 5, 6] and warns == [7, 8, 9]
                and any("возможно, hero-media" in f.msg for f in lin.findings if f.line == 3))
        ok &= good
        print(("PASS " if good else "FAIL ") + f"таблица соответствий: ошибки в строках {errs}, предупреждения {warns}")
        (td / "cw-head.tsv").write_text("source\tterm\n", encoding="utf-8")
        lin = Linter(voc, {})
        lin.lint_crosswalk(td / "cw-head.tsv")
        good = [f.line for f in lin.findings if f.level == "error"] == [1]
        ok &= good
        print(("PASS " if good else "FAIL ") + "таблица соответствий: колонки не по формату — ошибка")
    # проверка на настоящем словаре: все id проходят свои же шаблоны
    real = Vocab.load(DEFAULT_VOCAB)
    pat = re.compile(real.data["id_pattern"])
    exc = {k: re.compile(v) for k, v in (real.data.get("id_pattern_exceptions") or {}).items()}
    bad = [(ns, i) for ns, s in real.ids.items() for i in s if not (exc.get(ns) or pat).match(i)]
    good = not bad
    ok &= good
    print(("PASS " if good else "FAIL ") + f"настоящий словарь: {sum(len(s) for s in real.ids.values())} id, "
          f"шаблон id нарушен у {len(bad)}")
    lin = Linter(real, {})
    lin.lint_crosswalk(DEFAULT_CROSSWALK)
    errs = [f for f in lin.findings if f.level == "error"]
    good = not errs and lin.checked["crosswalk"] > 0
    ok &= good
    print(("PASS " if good else "FAIL ") + f"настоящая таблица соответствий: строк {lin.checked['crosswalk']}, ошибок {len(errs)}"
          + (f" (первая: {errs[0]})" if errs else ""))
    print("SELFTEST", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*")
    ap.add_argument("--vocab", default=str(DEFAULT_VOCAB))
    ap.add_argument("--map", action="append", metavar="KEY=NAMESPACE", help="доп. ключ → пространство (можно много раз)")
    ap.add_argument("--no-default-map", action="store_true", help="не использовать карту по умолчанию")
    ap.add_argument("--keys-as-ids", action="append", metavar="KEY=NAMESPACE", help="дочерние ключи словаря KEY — id")
    ap.add_argument("--allow-measurement", action="store_true", help="разрешить id со статусом measurement-only (замеры)")
    ap.add_argument("--crosswalk", help="crosswalk.tsv: подсказать наш id для чужого термина")
    ap.add_argument("--source-base", action="append", help="брать подсказки только из строк этой базы (source_base)")
    ap.add_argument("--stats", action="store_true", help="сводка по crosswalk для неизвестных id")
    ap.add_argument("--check-crosswalk", action="store_true",
                    help="проверить таблицу соответствий (файл — --crosswalk, по умолчанию 02-site-types/crosswalk.tsv)")
    ap.add_argument("--show-info", action="store_true", help="показывать proposed")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.files and not a.check_crosswalk:
        ap.error("нужны файлы, --check-crosswalk или --selftest")
    kai = {}
    for pair in a.keys_as_ids or []:
        k, _, ns = pair.partition("=")
        kai[k.strip()] = ns.strip()
    cw = Crosswalk(a.crosswalk, set(a.source_base) if a.source_base else None)
    lin = run(a.files, Vocab.load(a.vocab), build_keymap(a), kai, a.allow_measurement, cw)
    if a.check_crosswalk:
        lin.lint_crosswalk(a.crosswalk or DEFAULT_CROSSWALK)
    sys.exit(report(lin, quiet_info=not a.show_info, stats=a.stats))


if __name__ == "__main__":
    main()
