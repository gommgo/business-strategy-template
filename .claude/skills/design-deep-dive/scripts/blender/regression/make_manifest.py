# Сборка manifest.json регрессионного набора из готовых экспериментов (без новых рендеров). Пути — от корня базы.
import json, os
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib")); import kbpaths  # перенос
ROOT = str(kbpaths.kb("blender"))
E = "99-raw/experiments/"
C12 = E + "C1/12-protocol-objects/"
P = json.load(open(os.path.join(ROOT, E + "J/01-calibration/passports.json")))
BRIEF = {"mug": "кофейная кружка Ø 82 × 95 мм с ручкой, керамика, терракота", "phone": "смартфон 71,5 × 147 × 7,8 мм, экран светится",
         "tree": "низкополигональное дерево на островке земли", "rocket": "мультяшная ракета: корпус, нос, 3 стабилизатора, иллюминатор, сопло",
         "sculpture": "абстрактная скульптура-узел на цоколе, перламутр", "laptop": "открытый ноутбук 13\" 304 × 212 мм, крышка 110°",
         "logo": "3D-логотип «NOVA», лицом к камере, стоит на z = 0", "room": "изометрическая комнатка 3 × 3 м: диван, стол, полка, лампа, окно"}
entries = []
for k in ("mug", "phone", "tree", "rocket", "sculpture", "laptop", "logo", "room"):
    entries.append({"id": "c1-" + k, "tier": "core", "archetype": "hero-объект (протокол C1)", "source": "C1/12",
                    "brief": BRIEF[k], "passport": P[k],
                    "build": [C12 + "proto_lib.py", C12 + k + ".py"], "build_cmd": f"python3 99-raw/tools/blender_run.py {C12}run_proto.py -- {C12}{k}.py OUT {k}",
                    "blend": C12 + f"out/{k}.blend", "glb": C12 + f"out/{k}.glb",
                    "ref_images": [C12 + f"out/views_{k}/sheet.png", C12 + f"out/{k}_camera.png"]})
D1 = E + "D1/"
for eid, arch, exp, glb, img, brief in (
        ("d1-phone-mockup", "мокап устройства со скриншотом", "02-phone-mockup", "phone.glb", "t_rules_25.png", "телефон-мокап с текстурой экрана, фаски по правилам"),
        ("d1-product-case", "hero-продукт: корпус с петлёй и решёткой", "03-product-hinge-grille", "case.glb", "t_case_open.png", "кейс с крышкой на петле и решёткой"),
        ("d1-clay-icon-bell", "3D-иконка серии (глина)", "04-clay-icons", "icon_bell.glb", "t_bell.png", "иконка «колокольчик», глина, серия с chat/folder"),
        ("d1-sculpture-ribbon", "абстрактный фон/скульптура", "06-sculpture", "sculpt_ribbon.glb", "t_ribbon.png", "лента с закрутом по узлу, 26 тыс. треуг."),
        ("d1-lowpoly-island", "low-poly сцена с инстансами", "07-lowpoly-gn-data", "island_instances.glb", None, "low-poly островок, инстансы GN → EXT_mesh_gpu_instancing")):
    entries.append({"id": eid, "tier": "core", "archetype": arch, "source": "D1/" + exp, "brief": brief, "passport": None,
                    "build": [D1 + exp + "/exp" + exp[:2] + ".py", D1 + "_lib/d1lib.py"], "blend": None, "glb": D1 + exp + "/out/" + glb,
                    "ref_images": [D1 + exp + "/out/" + img] if img else [D1 + exp + "/sheet.png"]})
entries.append({"id": "d2-icon-series", "tier": "core", "archetype": "серия 3D-иконок (свет по паспорту стиля)", "source": "D2/04",
                "brief": "4 иконки (chat, lock, pill, star) одним паспортом света", "passport": None,
                "build": [E + "D2/04-light-icons/"], "blend": None, "glb": None,
                "ref_images": [E + f"D2/04-light-icons/out/icon_passport_{n}.png" for n in ("chat", "lock", "pill", "star")],
                "metrics": E + "D2/04-light-icons/out/icons_metrics.json"})
H = E + "H/"
entries.append({"id": "h-turntable", "tier": "core", "archetype": "турнтейбл продукта", "source": "H/10", "brief": "вращение 360° за 4 с, LINEAR, сэмплы",
                "passport": None, "build": [H + "10-turntable/make.py"], "blend": None, "glb": H + "10-turntable/out/a_linear_2keys_sampled.glb",
                "anim_check": H + "10-turntable/check_rot.js", "anim_expect": {"quarters": [45, 135, 225, 315]}, "ref_images": []})
entries.append({"id": "h-reveal-parts", "tier": "core", "archetype": "раскрытие частей (одно действие со слотами)", "source": "H/12",
                "brief": "части разъезжаются одним клипом Reveal", "passport": None, "build": [H + "12-reveal-parts/make.py"], "blend": None,
                "glb": H + "12-reveal-parts/out/reveal_A_merge_action.glb", "ref_images": [H + "12-reveal-parts/diff_A/anim_diff_sheet.png"]})
entries.append({"id": "h-logo-motion", "tier": "core", "archetype": "анимированный логотип", "source": "H/16", "brief": "логотип: появление по таймлайну",
                "passport": None, "build": [H + "16-logo-motion/make.py"], "blend": None, "glb": H + "16-logo-motion/out/logo_anim_meshopt.glb",
                "ref_images": [H + "16-logo-motion/logo_frames_sheet.png"]})
X = "09-web-runtime/examples/"
for eid, d, arch in (("f1-hero-lazy", "hero-lazy", "страница: постер → 3D после LCP"), ("f2-camera-path", "camera-path-scroll", "страница: камера на прокрутке"),
                     ("f2-shader-bg", "shader-background", "страница: шейдерный фон")):
    entries.append({"id": eid, "tier": "page", "archetype": arch, "source": X + d, "page": X + d, "brief": arch, "passport": None,
                    "glb": None, "blend": None, "build": [X + d], "ref_images": []})
K = "12-recipes/examples/"
for d, glb in (("01-hero-product", "case.glb"), ("02-icon-series", "icon_bell.glb"), ("03-device-mockup", "phone.glb"),
               ("04-abstract-sculpture", "sculpture_pearl_23.glb"), ("05-scroll-showcase", "case_reveal.glb"), ("06-logo-3d-particles", "logo.glb"),
               ("07-lowpoly-diorama", "island.glb"), ("09-glass-product", "glass.glb"), ("10-instance-field", "field.glb")):
    entries.append({"id": "k-" + d, "tier": "k-recipes (в работе у K на 23.09 18:15)", "archetype": d[3:], "source": K + d, "brief": "см. " + K + d + "/numbers.json",
                    "passport": None, "build": [K + d + "/build.py"], "blend": None, "glb": K + d + "/" + glb, "numbers": K + d + "/numbers.json",
                    "page": K + d if os.path.exists(os.path.join(ROOT, K + d, "index.html")) else None, "ref_images": []})
NEG = E + "C1/11-naive-first-try/out/"
for eid, blend, key, expect in (("neg-sonnet-laptop", NEG + "sonnet/sonnet_laptop.blend", "laptop", ["dims_mismatch", "floating_part"]),
                                ("neg-opus-mug", NEG + "opus/opus_mug.blend", "mug", ["dims_mismatch"]),
                                ("neg-haiku-tree", NEG + "haiku/haiku_tree.blend", "tree", ["not_in_frame"])):
    pp = dict(P[key]); pp.pop("touch", None)
    entries.append({"id": eid, "tier": "negative", "archetype": "отрицательный контроль (первая попытка C1/11)", "source": "C1/11",
                    "brief": BRIEF[key], "passport": pp, "build": [E + "C1/11-naive-first-try/" + blend.split("/")[-2] + "/" + key + ".py"],
                    "blend": blend, "glb": None, "expect_codes": expect, "ref_images": [NEG + blend.split("/")[-2] + f"/views_{key}/sheet.png"]})
entries.append({"id": "neg-turntable-reverse", "tier": "negative", "archetype": "отрицательный контроль: турнтейбл без сэмплов", "source": "H/10",
                "brief": "3 ключа 0/180/360° без сэмплирования", "passport": None, "build": [H + "10-turntable/make.py"], "blend": None,
                "glb": H + "10-turntable/out/f_linear_3keys_curves_180.glb", "anim_check": H + "10-turntable/check_rot.js",
                "anim_expect": {"quarters": [45, 135, 225, 315]}, "expect_fail": True, "ref_images": []})
missing = []
for e in entries:
    for k in ("blend", "glb", "page", "anim_check", "metrics", "numbers"):
        if e.get(k) and not os.path.exists(os.path.join(ROOT, e[k])):
            missing.append((e["id"], k, e[k]))
    e["ref_images"] = [p for p in e["ref_images"] if os.path.exists(os.path.join(ROOT, p))]
json.dump({"version": "2026-09-23", "root": ROOT, "entries": entries}, open("manifest.json", "w"), ensure_ascii=False, indent=1)
print(len(entries), "entries;", "missing:", missing)
from collections import Counter
print(Counter(e["tier"] for e in entries))
