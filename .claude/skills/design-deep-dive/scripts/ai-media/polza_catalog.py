#!/usr/bin/env python3
"""polza_catalog.py — каталог polza.ai как данные: снимки, нормализация медиа-моделей, таблица, сравнение
снимков, калькулятор цены и валидатор входа по каталогу (библиотека для polza.py).

Агент B, волна 1 ai-media-research, 2026-09-23. Python 3.13, только стандартная библиотека.
Сеть: только бесплатные публичные GET https://polza.ai/api/v1/models (с include_providers) и /v1/models/catalog;
флаг --with-openapi дополнительно берёт публичную спецификацию https://polza.ai/api/openapi.json.

Команды:
  snapshot [--root DIR] [--with-openapi] [--no-providers]   снимок в $DDD_HOME/cache/ai-media/polza/<дата>[_ЧЧММ]/ (не
                                                             перезаписывает): файлы качаются во временную папку,
                                                             готовый снимок встаёт на место переименованием — при
                                                             обрыве последним остаётся прежний снимок, код выхода 1
  normalize [SNAP] [--providers SNAP2] [--out FILE]          media-models.normalized.json (картинки и видео)
  table [SNAP] [--type image|video] [--out FILE]             Markdown-таблица медиа-моделей
  diff A B [--all-types] [--json]                            что изменилось между снимками (модели, цены, параметры, провайдеры)
  price MODEL [k=v ...] [--provider NAME] [--ref-seconds S]  быстрая оценка цены (значения как в input задания); в
                                                             stderr — какой снимок взят и сколько ему
  check MODEL [k=v ...]                                      проверка входа по каталогу (ошибки и предупреждения)
  selftest [--offline]                                       встроенные проверки: снимок при обрыве и возраст снимка
                                                             (без каталога), затем калькулятор и валидатор по снимку
                                                             --snapshot; --offline — только первая часть

SNAP — имя папки в 99-raw/cache/polza/ (например 2026-09-23), путь к папке или к api-v1-models.json; по умолчанию —
последний снимок. Все цены — рубли по каталогу (top_provider.pricing или providers[].pricing).

Семантика ступеней цены (tiers) выведена из каталога и спецификации OpenAPI (ClientTierPresenter, unitParam) и НЕ
описана polza явно [не проверено]: выбирается ступень, все условия которой выполнены для эффективных значений
(явное значение из input → default каталога → производное: has_video, input_images_count), с наибольшим числом
условий; ступень с пустыми условиями [] — запасная (её цена часто равна максимальной). При unitParam=duration
cost_rub ступени — ставка за секунду.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.client
import json
import math
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

VERSION = "1.0 (2026-09-23)"
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("ai-media")                # перенос: kb/ai-media
CACHE = kbpaths.cache("ai-media", "polza")
BASE = "https://polza.ai/api"
MSK = dt.timezone(dt.timedelta(hours=3))
MEDIA_TYPES = ("image", "video")
UA = "polza_catalog.py/1.0 (ai-media-research; catalog snapshot)"

# ---------------------------------------------------------------------------------------------------------------
# Справочные константы (с источниками). Скоропортящееся — с датой.
# ---------------------------------------------------------------------------------------------------------------

# Курс, по которому polza переводит долларовые цены токенных провайдеров (openai, google-*, openrouter, Alibaba):
# 3 модели дают ровно 117.992 (B-notes §3; 99-raw/experiments/B/05-polza-vs-kie-fx). Курс ЦБ 23.09.2026 — 84.0657.
FX_POLZA_USD_RUB = 117.992

# Выходные image-токены за картинку (для токенных провайдеров). Источники: Gemini API pricing
# (ai.google.dev/gemini-api/docs/pricing, снято 2026-09-23), OpenAI image generation guide (gpt-image-1 family).
IMAGE_OUTPUT_TOKENS = {
    "google/gemini-3.1-flash-image": {"0.5K": 747, "1K": 1120, "2K": 1680, "4K": 2520},
    "google/gemini-3.1-flash-image-preview": {"0.5K": 747, "1K": 1120, "2K": 1680, "4K": 2520},
    "google/gemini-3-pro-image-preview": {"1K": 1120, "2K": 1120, "4K": 2000},
    "google/gemini-3.1-flash-lite-image": {"1K": 1120},
    "google/gemini-2.5-flash-image": {"1K": 1290},
    # gpt-image-1 / 1-mini: 1024x1024 low 272 / medium 1056 / high 4160 токенов (OpenAI guide). Какой тир качества
    # использует polza для openai/gpt-5-image(-mini) — неизвестно [не проверено]; берём medium, диапазон low..high.
    "openai/gpt-5-image-mini": {"low": 272, "medium": 1056, "high": 4160},
    "openai/gpt-5-image": {"low": 272, "medium": 1056, "high": 4160},
}
# Токены входной картинки-референса (Gemini 3 Pro Image: 560). Для прочих — та же оценка.
IMAGE_INPUT_TOKENS = 560

# Разрешение, скрытое за «качеством» или «режимом» (из описаний параметров каталога и документации KIE для Kling 3.0).
RESOLUTION_MAP = {
    "bytedance/seedream-4.5": ("quality", {"basic": "2K", "high": "4K"}),
    "bytedance/seedream-5-lite": ("quality", {"basic": "2K", "high": "3K"}),
    "seedream/5-pro-text-to-image": ("quality", {"basic": "1K", "high": "2K"}),
    "kling/v3": ("mode", {"std": "720p", "pro": "1080p", "4K": "2160p"}),
    "kling/v3-motion-control": ("mode", {"720p": "720p", "1080p": "1080p"}),
    "kling/v2.6-motion-control": ("mode", {"720p": "720p", "1080p": "1080p"}),
}

# Единые имена полей (нормализация): канонический ключ → имена параметров polza.
UNIFIED = [
    ("prompt", ["prompt"]),
    ("negative_prompt", ["negative_prompt"]),
    ("ref_images", ["images"]),
    ("ref_videos", ["videos"]),
    ("mask", ["mask_url"]),
    ("aspect_ratio", ["aspect_ratio"]),
    ("resolution", ["image_resolution", "resolution"]),
    ("quality", ["quality"]),
    ("mode", ["mode"]),
    ("duration", ["duration"]),
    ("seed", ["seed", "seeds"]),
    ("audio", ["generate_audio", "sound"]),
    ("fixed_camera", ["fixed_lens"]),
    ("multi_shot", ["multi_shots"]),
    ("generation_type", ["generationType", "character_orientation"]),
    ("output_format", ["output_format"]),
    ("background", ["background"]),
    ("prompt_enhance", ["enhance_prompt", "isEnhance", "enable_prompt_expansion"]),
    ("prompt_translate", ["enableTranslation"]),
    ("watermark", ["watermark"]),
    ("upscale_factor", ["upscale_factor"]),
    ("guidance_scale", ["guidance_scale"]),
    ("strength", ["strength"]),
    ("audio_ids", ["audio_ids"]),
    ("character_ids", ["character_ids"]),
]

# Поля, которые принимает Media API сверх параметров каталога (OpenAPI ImageInputDto/VideoInputDto).
ALLOWED_EXTRA = {"callBackUrl"}

# Расхождения документации и каталога, известные по чтению docs-repo (18.09.2026) и каталога 23.09.2026 (кураторские,
# не генерируются). Ключ — id модели; ссылки — на файлы docs-repo/ и на B-notes.
DOC_VS_CATALOG = {
    "google/veo3": [
        "prompt: гайд veo-3-1.mdx «до 2 000 символов», каталог max_length 60000",
        "images: каталог max 2 (FIRST_AND_LAST_FRAMES_2_VIDEO); гайд: Quality до 2, Fast до 3",
        "длительности и разрешения нет в параметрах; у KIE Veo 3.1 есть duration 4/6/8 и resolution 720p/1080p/4k — polza их не выставляет",
        "operations: upscale_4k в каталоге async=true, в media/operations.mdx — «синхронная»",
        "extend: каталог prompt max_length 16000 + seeds/watermark/model; operations.mdx — prompt, seeds, duration 3–10 с",
    ],
    "google/veo3_fast": [
        "prompt: гайд «до 2 000 символов», каталог max_length 60000",
        "REFERENCE_2_VIDEO — только Fast (values каталога совпадают с гайдом)",
        "в cURL гайда id без префикса: veo3 / veo3_fast",
    ],
    "bytedance/seedance-2": ["prompt: описание «до 1536 символов», max_length 20000; гайд — 3–20000",
                             "resolution: гайд 480p/720p, каталог ещё 1080p («по документации KIE»)",
                             "гайд шлёт multi_shots, которого нет в параметрах каталога"],
    "bytedance/seedance-2-fast": ["prompt: описание «до 1536 символов», max_length 20000"],
    "bytedance/seedance-1.5-pro": ["цена: условие ступени sound=…, а параметр называется generate_audio"],
    "kling/v3": ["sound: «обязательно true при multi_shots», но multi_shots нет в параметрах каталога",
                 "aspect_ratio: default 1:1 (у KIE — 16:9); игнорируется при start frame"],
    "google/gemini-3-pro-image-preview": ["images: у mie max 8, у bananalab 14, у Google (Gemini API) до 14"],
    "google/gemini-3.1-flash-image-preview": ["гайд nanobanano-2.mdx: «до 8 референсов» и путь /v1/media/nanobanano-2; каталог mie — 14",
                                              "результат по гайду — output.url (в status.mdx — data.url)"],
    "google/gemini-3.1-flash-image": ["нет parameters ни у одного провайдера — как вызывать через /v1/media, неизвестно"],
    "openai/gpt-5.4-image-2": ["гайд: провайдер openai «по умолчанию», каталог: top_provider = mie",
                               "гайд: выбор провайдера @-синтаксисом openai/gpt-5.4-image-2@mie, aliases.mdx: для Media API алиасы не работают"],
    "openai/gpt-5-image": ["mask_url «чёрные = менять, белые = оставить» — противоположно qwen/image-2.1"],
    "qwen/image-2.1": ["mask_url «белое — менять, чёрное — оставить» — противоположно openai/gpt-5-image"],
    "topaz/image-upscale": ["upscale_factor 8 есть в каталоге; у KIE — 1/2/4 (агент P)"],
    "bytedance/seedream-4": ["последний cURL гайда использует id bytedance/seedream-v4 (ошибка)"],
    "gemini-omni-video": ["гайд: async «по умолчанию true» и «обязателен»; OpenAPI MediaRequestDto: async default false"],
}

# ---------------------------------------------------------------------------------------------------------------
# Общие утилиты
# ---------------------------------------------------------------------------------------------------------------

def now_msk() -> dt.datetime:
    return dt.datetime.now(MSK)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def as_str(v) -> str | None:
    """Значение для сравнения с условиями ступеней и values каталога."""
    if v is None:
        return None
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return str(int(v)) if v.is_integer() else repr(v)
    return str(v)


def to_num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    try:
        f = float(str(v).replace(",", "."))
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return None


def fmt_rub(x) -> str:
    """12.825 → '12,825'; 4 → '4,00'; 9.43936 → '9,4394' (ставки не округляются до копеек)."""
    if x is None:
        return "—"
    s = f"{float(x):,.4f}".rstrip("0")
    if len(s.split(".")[1]) < 2:
        s = f"{float(x):,.2f}"
    return s.replace(",", " ").replace(".", ",")


def http_get(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, dict(r.headers.items()), r.read()


# ---------------------------------------------------------------------------------------------------------------
# Снимки
# ---------------------------------------------------------------------------------------------------------------

def find_snapshot(ref: str | None = None) -> Path:
    """Папка снимка по имени/пути; None или 'latest' — последняя по имени папка с api-v1-models.json."""
    if ref and ref != "latest":
        p = Path(ref)
        if p.is_file():
            return p.parent
        if p.is_dir():
            return p
        q = CACHE / ref
        if q.is_dir():
            return q
        raise SystemExit(f"снимок не найден: {ref}")
    dirs = sorted(d for d in snapshot_dirs(CACHE) if (d / "api-v1-models.json").exists())
    if not dirs:
        raise SystemExit(f"нет снимков в {CACHE}")
    return dirs[-1]


def snapshot_dirs(root: Path) -> list[Path]:
    """Папки снимков в корне кэша; временная папка снимка, который ещё качается (имя с точки), снимком не считается."""
    return [d for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")]


class Snapshot:
    def __init__(self, ref: str | None = None, providers_ref: str | None = None):
        self.dir = find_snapshot(ref)
        raw = json.loads((self.dir / "api-v1-models.json").read_text())
        self.models = raw["data"] if isinstance(raw, dict) else raw
        self.by_id = {m["id"]: m for m in self.models}
        meta_p = self.dir / "snapshot.meta.json"
        self.meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
        self.providers = {}
        self.providers_source = None
        if providers_ref == "auto":
            # в выбранном снимке нет providers[] — берём ближайший более поздний снимок с include_providers
            providers_ref = None
            if not (self.dir / "api-v1-models.providers.json").exists():
                later = sorted(d for d in snapshot_dirs(CACHE) if d.name >= self.dir.name
                               and (d / "api-v1-models.providers.json").exists())
                providers_ref = str(later[0]) if later else None
        pdir = find_snapshot(providers_ref) if providers_ref else self.dir
        pfile = pdir / "api-v1-models.providers.json"
        if pfile.exists():
            praw = json.loads(pfile.read_text())
            for m in (praw["data"] if isinstance(praw, dict) else praw):
                if m.get("providers") is not None:
                    self.providers[m["id"]] = m["providers"]
            self.providers_source = str(pfile.relative_to(ROOT)) if pfile.is_relative_to(ROOT) else str(pfile)

    def media(self, types=MEDIA_TYPES):
        return [m for m in self.models if m.get("type") in types]

    def fetched_at(self) -> str:
        return self.meta.get("fetched_at_msk") or dt.datetime.fromtimestamp(
            (self.dir / "api-v1-models.json").stat().st_mtime, MSK).isoformat(timespec="seconds")


class SnapshotError(Exception):
    """Снимок не снят: сеть оборвалась или канал ответил не каталогом."""


NET_ERRORS = (urllib.error.URLError, http.client.HTTPException, TimeoutError, ConnectionError, OSError)
REQUIRED_FILES = ("api-v1-models.json", "api-v1-models.providers.json")   # без них цены и параметры считать не по чему
STALE_TMP_S = 3600        # временная папка старше часа — след прерванного снимка, её убирает следующий запуск


def fmt_age(seconds: float) -> str:
    m = int(max(seconds, 0) // 60)
    if m < 60:
        return f"{m} мин"
    return f"{m // 60} ч" if m < 48 * 60 else f"{m // 1440} дн"


def age_note(name: str, fetched_at: str | None, complete: bool = True, refresh: str = "polza_catalog.py snapshot",
             now: dt.datetime | None = None) -> tuple[str, bool]:
    """Строка о снимке каталога, по которому считается оценка, и признак «свериться перед серией». Норма серии —
    снимок за сегодня (kb/ai-media/02-providers-platforms/01-polza-api.md, чек-лист): цены и параметры меняются без
    объявления, а утилиты берут последнюю папку — оценка называет её и её возраст, а не выбирает молча. Папка без
    snapshot.meta.json — снимок, снятый не до конца или не утилитой."""
    now = now or now_msk()
    try:
        t = dt.datetime.fromisoformat(fetched_at) if fetched_at else None
    except ValueError:
        t = None
    if t is not None and t.tzinfo is None:
        t = t.replace(tzinfo=MSK)
    text = f"снимок каталога {name}"
    stale = t is None or t.astimezone(MSK).date() != now.astimezone(MSK).date()
    if t is not None:
        text += f" — снят {t.astimezone(MSK):%d.%m.%Y %H:%M} МСК, {fmt_age((now - t).total_seconds())} назад"
    if not complete:
        text += "; в папке нет snapshot.meta.json — снимок снят не до конца или не утилитой"
    if stale:
        text += f": не за сегодня — цены и параметры могли измениться; перед серией — {refresh} (бесплатный GET)"
    return text, stale or not complete


def snapshot_note(snap: Snapshot, now: dt.datetime | None = None) -> tuple[str, bool]:
    return age_note(snap.dir.name, snap.fetched_at(), (snap.dir / "snapshot.meta.json").exists(), now=now)


def take_snapshot(root: Path, *, with_openapi=False, no_providers=False, get=http_get, pause: float = 1.0,
                  stamp: dt.datetime | None = None) -> tuple[Path, Snapshot, dict]:
    """Снять снимок в root/<дата>[_ЧЧММ]/ → (папка, снимок, метаданные). Файлы качаются во временную папку рядом и
    встают на место одним переименованием, когда скачаны и разобраны все: недокачанная папка с api-v1-models.json
    стала бы «последним снимком» для всех утилит. Обрыв сети, ответ не 200 или не каталог у обязательного файла —
    SnapshotError; временная папка убирается, последним остаётся прежний снимок."""
    stamp = stamp or now_msk()
    root.mkdir(parents=True, exist_ok=True)
    d = root / stamp.strftime("%Y-%m-%d")
    if (d / "api-v1-models.json").exists():
        d = root / stamp.strftime("%Y-%m-%d_%H%M")
    if d.exists() and any(d.iterdir()):
        raise SnapshotError(f"папка уже существует и не пуста: {d} — повторите через минуту")
    for old in root.glob(".snapshot-*.part"):
        if old.is_dir() and time.time() - old.stat().st_mtime > STALE_TMP_S:
            shutil.rmtree(old, ignore_errors=True)
    tmp = root / f".snapshot-{stamp:%Y%m%d-%H%M%S}-{os.getpid()}.part"
    tmp.mkdir()
    plan = [("api-v1-models.json", f"{BASE}/v1/models")]
    if not no_providers:
        plan.append(("api-v1-models.providers.json", f"{BASE}/v1/models?include_providers=true"))
    for t in MEDIA_TYPES:
        plan.append((f"api-v1-models-catalog.{t}.json", f"{BASE}/v1/models/catalog?type={t}&limit=100"))
    if with_openapi:
        plan.append(("openapi.json", f"{BASE}/openapi.json"))
    meta = {"tool": f"polza_catalog.py {VERSION}", "fetched_at_msk": stamp.isoformat(timespec="seconds"),
            "fetched_at_utc": stamp.astimezone(dt.timezone.utc).isoformat(timespec="seconds"), "files": {}}
    keep = ("date", "server", "content-type", "cache-control", "x-cache", "x-trace-id", "x-ratelimit-limit",
            "x-ratelimit-remaining", "x-ratelimit-reset", "age", "etag", "last-modified")
    try:
        for i, (name, url) in enumerate(plan):
            if i and pause:
                time.sleep(pause)  # вежливость: публичный каталог отвечает x-ratelimit-limit: 30
            t0 = time.time()
            try:
                status, headers, body = get(url)
            except urllib.error.HTTPError as e:
                status, headers, body = e.code, dict(e.headers.items()), e.read()
            except NET_ERRORS as e:
                raise SnapshotError(f"{name}: сеть оборвалась ({type(e).__name__}: {e}) ← {url}") from e
            if name in REQUIRED_FILES:
                try:
                    raw = json.loads(body)
                    models = raw["data"] if isinstance(raw, dict) else raw
                except (ValueError, KeyError, TypeError):
                    models = None
                if status != 200 or not isinstance(models, list) or not models:
                    raise SnapshotError(f"{name}: ответ {status}, {len(body)} байт — не каталог моделей ← {url}")
            (tmp / name).write_bytes(body)
            h = {k.lower(): v for k, v in headers.items() if k.lower() in keep}
            meta["files"][name] = {"url": url, "status": status, "bytes": len(body), "sha256": sha256_bytes(body),
                                   "seconds": round(time.time() - t0, 2), "headers": h}
            print(f"{status} {len(body):>9} байт  {name}  ← {url}")
        (tmp / "snapshot.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
        norm = normalize_snapshot(Snapshot(str(tmp)))
        for k in ("snapshot_dir", "providers_source"):          # пути — места, куда снимок встанет
            if isinstance(norm.get(k), str):
                norm[k] = norm[k].replace(str(tmp), str(d.relative_to(ROOT)) if d.is_relative_to(ROOT) else str(d))
        (tmp / "media-models.normalized.json").write_text(json.dumps(norm, ensure_ascii=False, indent=1))
        tmp.rename(d)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return d, Snapshot(str(d)), meta


def cmd_snapshot(a):
    root = Path(a.root) if a.root else CACHE
    try:
        d, snap, _ = take_snapshot(root, with_openapi=a.with_openapi, no_providers=a.no_providers)
    except SnapshotError as e:
        prev = sorted(x.name for x in snapshot_dirs(root) if (x / "api-v1-models.json").exists()) if root.is_dir() else []
        sys.exit(f"снимок не снят: {e}; последним остаётся " + (f"снимок {prev[-1]}" if prev else "прежнее состояние: "
                                                                 "снимков нет") + " — повторите позже")
    n = {t: sum(1 for m in snap.models if m.get("type") == t) for t in MEDIA_TYPES}
    print(f"снимок: {d.relative_to(ROOT) if d.is_relative_to(ROOT) else d} — моделей {len(snap.models)}, "
          f"картинки {n['image']}, видео {n['video']}; нормализовано → media-models.normalized.json")


# ---------------------------------------------------------------------------------------------------------------
# Цена
# ---------------------------------------------------------------------------------------------------------------

def pricing_kind(pr: dict) -> str:
    if not pr:
        return "none"
    if pr.get("tiers"):
        return "tiers_per_unit" if pr.get("unitParam") else "tiers"
    if pr.get("per_request") is not None:
        return "per_request"
    if pr.get("video_per_second") is not None:
        return "per_second"
    if any(k.endswith("_per_million") for k in pr):
        return "tokens"
    return "unknown"


def tier_keys(pr: dict) -> list[str]:
    keys = []
    for t in pr.get("tiers") or []:
        for c in t.get("conditions") or []:
            k = c.split("=", 1)[0]
            if k not in keys:
                keys.append(k)
    return keys


def price_params(model: dict, pr: dict | None = None, params: dict | None = None) -> list[str]:
    """Параметры input, от которых зависит цена (по условиям ступеней, unitParam и видео за секунду)."""
    pr = pr if pr is not None else model.get("top_provider", {}).get("pricing") or {}
    params = params if params is not None else (model.get("parameters") or {})
    out = []
    for k in tier_keys(pr):
        if k == "has_video":
            k = "videos"
        elif k == "input_images_count":
            k = "images"
        elif k == "sound" and "sound" not in params and "generate_audio" in params:
            k = "generate_audio"
        if k not in out:
            out.append(k)
    if (pr.get("unitParam") or pr.get("video_per_second") is not None) and "duration" in params and "duration" not in out:
        out.append("duration")
    return out


def provider_view(model: dict, provider: str | None, providers: list | None):
    """(имя, pricing, parameters) выбранного провайдера; None — top_provider."""
    tp = model.get("top_provider") or {}
    if not provider or provider == tp.get("name"):
        return tp.get("name"), tp.get("pricing") or {}, (model.get("parameters") or tp.get("parameters") or {})
    for p in providers or []:
        if p.get("name") == provider:
            return p["name"], p.get("pricing") or {}, (p.get("parameters") or {})
    raise KeyError(f"провайдер {provider!r} не найден у модели {model['id']} (нужен снимок с include_providers)")


def effective_price_values(model: dict, inp: dict, pr: dict, params: dict):
    """Эффективные значения ключей условий ступеней: из input, из default каталога, производные."""
    vals, src = {}, {}
    inp = inp or {}
    for k in tier_keys(pr) + ([pr["unitParam"]] if pr.get("unitParam") else []):
        if k in vals:
            continue
        if k == "has_video":
            v = inp.get("videos")
            vals[k] = "true" if isinstance(v, list) and len(v) > 0 else "false"
            src[k] = "derived"
            continue
        if k == "input_images_count":
            v = inp.get("images")
            vals[k] = str(len(v)) if isinstance(v, list) else "0"
            src[k] = "derived"
            continue
        name = k
        if k == "sound" and "sound" not in params and "generate_audio" in params:
            name = "generate_audio"   # у Seedance 1.5 Pro условие sound=…, параметр generate_audio
        if name in inp and inp[name] is not None:
            vals[k] = as_str(inp[name])
            src[k] = "input" if name == k else f"input:{name}"
        elif name in params and params[name].get("default") is not None:
            vals[k] = as_str(params[name]["default"])
            src[k] = "default" if name == k else f"default:{name}"
        else:
            vals[k] = None
            src[k] = "absent"
    return vals, src


def match_tier(tiers: list, vals: dict):
    best, best_n, ties = None, -1, []
    fallback = None
    for t in tiers:
        conds = t.get("conditions") or []
        if not conds:
            fallback = t
            continue
        ok = True
        for c in conds:
            k, _, v = c.partition("=")
            if vals.get(k) != v:
                ok = False
                break
        if not ok:
            continue
        n = len(conds)
        if n > best_n:
            best, best_n, ties = t, n, [t]
        elif n == best_n:
            ties.append(t)
    if len(ties) > 1:
        best = max(ties, key=lambda t: float(t["cost_rub"]))
    return best, fallback, (len(ties) > 1)


def estimate(model: dict, inp: dict | None = None, *, provider: str | None = None, providers: list | None = None,
             ref_seconds: float | None = None, quality_assumption: str = "medium", text_out_tokens: int = 0) -> dict:
    """Оценка цены задания по каталогу. Возвращает словарь с rub, диапазоном, формулой и предупреждениями."""
    inp = inp or {}
    name, pr, params = provider_view(model, provider, providers)
    kind = pricing_kind(pr)
    res = {"model": model["id"], "provider": name, "kind": kind, "rub": None, "rub_low": None, "rub_high": None,
           "tier": None, "unit_param": pr.get("unitParam"), "units": None, "rate_rub": None, "fallback_rub": None,
           "values_used": {}, "sources": {}, "warnings": [], "formula": ""}
    W = res["warnings"]

    def units_from_duration():
        d = inp.get("duration", params.get("duration", {}).get("default") if "duration" in params else None)
        if "duration" not in params:
            # цена за секунду без параметра duration: длительность = длина входного видео (Motion Control, Topaz Video)
            if ref_seconds is not None:
                return float(ref_seconds), "ref_seconds"
            if model["id"].endswith("motion-control"):
                orient = inp.get("character_orientation")
                cap = 10 if orient == "image" else 30
                W.append(f"длительность = длина видео движения (не задана): оценка по потолку {cap} с "
                         f"(character_orientation={orient or '—'}); передайте meta.ref_video_seconds")
                return float(cap), "cap"
            W.append("длительность = длина входного видео (не задана): передайте meta.ref_video_seconds")
            return None, "unknown"
        if d is None:
            W.append("длительность не задана и нет default в каталоге")
            return None, "absent"
        dn = to_num(d)
        auto = params["duration"].get("auto_value")
        if auto is not None and dn == auto:
            if ref_seconds is not None:
                return float(ref_seconds), "ref_seconds"
            mx = params["duration"].get("max")
            W.append(f"duration={auto}: длительность берётся из референсного видео — оценка по максимуму {mx} с")
            return float(mx) if mx is not None else None, "cap"
        return (float(dn) if dn is not None else None), ("input" if "duration" in inp else "default")

    if kind == "per_request":
        res["rub"] = float(pr["per_request"])
        res["formula"] = f"{fmt_rub(res['rub'])} ₽ за запрос"
    elif kind == "per_second":
        rate = float(pr["video_per_second"])
        u, usrc = units_from_duration()
        res.update(rate_rub=rate, units=u, unit_param="duration")
        res["sources"]["duration"] = usrc
        if u is not None:
            res["rub"] = round(rate * u, 6)
            res["formula"] = f"{fmt_rub(rate)} ₽/с × {u:g} с = {fmt_rub(res['rub'])} ₽"
    elif kind in ("tiers", "tiers_per_unit"):
        vals, src = effective_price_values(model, inp, pr, params)
        res["values_used"], res["sources"] = vals, src
        tier, fb, tie = match_tier(pr["tiers"], vals)
        res["fallback_rub"] = float(fb["cost_rub"]) if fb else None
        for k, s in src.items():
            if s == "absent" and k not in ("has_video", "input_images_count"):
                W.append(f"ценовой параметр {k!r} не задан и нет default — polza может применить запасную ступень "
                         f"[] = {fmt_rub(res['fallback_rub'])} ₽; задайте явно")
        if tie:
            W.append("несколько ступеней одинаковой точности — взята самая дорогая")
        if tier is None:
            tier = fb
            if fb is not None:
                W.append(f"ни одна ступень не подошла — запасная ступень [] = {fmt_rub(res['fallback_rub'])} ₽")
        if tier is None:
            W.append("нет подходящей ступени и нет запасной")
        else:
            res["tier"] = tier
            rate = float(tier["cost_rub"])
            cond = ", ".join(tier.get("conditions") or []) or "[] (запасная)"
            if kind == "tiers_per_unit":
                u, usrc = units_from_duration() if pr.get("unitParam") == "duration" else (None, "unknown")
                res.update(rate_rub=rate, units=u)
                res["sources"]["duration"] = usrc
                if u is not None:
                    res["rub"] = round(rate * u, 6)
                    res["formula"] = f"{fmt_rub(rate)} ₽/с × {u:g} с = {fmt_rub(res['rub'])} ₽ (ступень {cond})"
            else:
                res["rub"] = rate
                res["formula"] = f"{fmt_rub(rate)} ₽ (ступень {cond})"
    elif kind == "tokens":
        mid = model["id"]
        table = IMAGE_OUTPUT_TOKENS.get(mid)
        p_in = float(pr.get("prompt_per_million") or 0)
        p_out = float(pr.get("completion_per_million") or 0)
        p_img = float(pr.get("image_output_per_million") or 0)
        prompt = str(inp.get("prompt") or "")
        # грубо: ~3 символа на токен для смешанного русского/английского текста [практика]
        t_prompt = max(1, math.ceil(len(prompt) / 3)) if prompt else 0
        n_imgs = len(inp.get("images") or [])
        t_in = t_prompt + n_imgs * IMAGE_INPUT_TOKENS
        if not p_img:
            W.append("у провайдера нет цены за выходную картинку (image_output_per_million) — вероятно, только текст; "
                     "для генерации картинок не годится")
        elif not table:
            W.append("число выходных image-токенов для этой модели в источниках не найдено — цена неизвестна; "
                     "используйте провайдера с ценой за запрос или provider.max_price")
        else:
            res_key = as_str(inp.get("image_resolution")) or ("1K" if "1K" in table else quality_assumption)
            if res_key not in table:
                res_key = quality_assumption if quality_assumption in table else next(iter(table))
            t_img = table[res_key]
            lo_img = min(table.values()) if "medium" in table else t_img
            hi_img = max(table.values()) if "medium" in table else t_img
            base = t_in * p_in / 1e6
            res["rub"] = round(base + t_img * p_img / 1e6 + text_out_tokens * p_out / 1e6, 6)
            res["rub_low"] = round(base + lo_img * p_img / 1e6, 6)
            res["rub_high"] = round(base + hi_img * p_img / 1e6 + 1000 * p_out / 1e6, 6)
            res["units"] = {"prompt_tokens": t_in, "image_output_tokens": t_img, "assumed": res_key}
            res["formula"] = (f"{t_in} вх. ток. × {fmt_rub(p_in)} ₽/1M + {t_img} вых. image-ток. ({res_key}) × "
                              f"{fmt_rub(p_img)} ₽/1M ≈ {fmt_rub(res['rub'])} ₽ (+ текст/рассуждение модели: до "
                              f"{fmt_rub(res['rub_high'])} ₽)")
            W.append("токенная цена: оценка по таблицам вендора, фактическая — в usage.cost_rub [не проверено]")
    else:
        W.append(f"неизвестная схема цены: {sorted(pr)}")
    if res["rub"] is not None and res["rub_low"] is None:
        res["rub_low"] = res["rub_high"] = res["rub"]
    return res


def operation_estimate(model: dict, op: str) -> dict:
    for o in model.get("operations") or []:
        if o["id"] == op:
            pr = o.get("pricing") or {}
            rub = float(pr["per_request"]) if pr.get("per_request") is not None else None
            return {"model": model["id"], "operation": op, "async": o.get("async"), "rub": rub,
                    "formula": f"{fmt_rub(rub)} ₽ за операцию", "params": o.get("parameters") or {}}
    raise KeyError(f"операции {op!r} нет у модели {model['id']} (есть: "
                   f"{[o['id'] for o in model.get('operations') or []]})")


# ---------------------------------------------------------------------------------------------------------------
# Приведение типов, заполнение и проверка входа
# ---------------------------------------------------------------------------------------------------------------

BOOL_STR = {"true", "false"}


def coerce_value(name: str, spec: dict, v):
    """Значение в представлении каталога: values → строка; duration → строка (OpenAPI VideoInputDto.duration: string,
    гайды шлют "5"); числовой диапазон → число; булево с default-строкой → строка, с default-bool → bool."""
    if v is None or name in ("images", "videos", "audio_ids", "character_ids"):
        return v
    vals = spec.get("values")
    if vals:
        s = as_str(v)
        # "jpg" Media API сам превращает в jpeg (OpenAPI), но values каталога — jpeg
        return s
    if name == "duration":
        n = to_num(v)
        return as_str(n) if n is not None else v
    d = spec.get("default")
    if isinstance(d, bool):
        if isinstance(v, str) and v.lower() in BOOL_STR:
            return v.lower() == "true"
        return v
    if isinstance(d, str) and d in BOOL_STR:
        if isinstance(v, bool):
            return "true" if v else "false"
        return v
    if ("min" in spec or "max" in spec) and not isinstance(v, bool):
        n = to_num(v)
        return n if n is not None else v
    return v


def coerce_input(params: dict, inp: dict) -> tuple[dict, list]:
    out, notes = {}, []
    for k, v in (inp or {}).items():
        spec = params.get(k)
        if spec is None:
            out[k] = v
            continue
        nv = coerce_value(k, spec, v)
        if nv is not v and nv != v or type(nv) is not type(v):
            if not (isinstance(v, (list, dict))):
                notes.append(f"{k}: {v!r} → {nv!r} (представление каталога)")
        out[k] = nv
    return out, notes


def fill_defaults(model: dict, inp: dict, params: dict, pr: dict) -> tuple[dict, list, list]:
    """Явно подставляет default каталога для ценовых и обязательных параметров. Возвращает (input, filled, missing)."""
    out = dict(inp or {})
    filled, missing = [], []
    need = price_params(model, pr, params)
    for k, spec in params.items():
        if spec.get("required") and k not in need:
            need.append(k)
    for k in need:
        if k in ("images", "videos"):
            continue
        spec = params.get(k)
        if spec is None:
            continue
        if k in out and out[k] is not None:
            continue
        d = spec.get("default")
        if d is not None:
            out[k] = coerce_value(k, spec, d)
            filled.append(k)
        else:
            missing.append(k)
    return out, filled, missing


CYR = re.compile(r"[А-Яа-яЁё]")


def _len_items(v):
    return len(v) if isinstance(v, list) else (0 if v is None else 1)


def validate(model: dict, inp: dict, *, provider: str | None = None, providers: list | None = None,
             strict: bool = True, ref_seconds: float | None = None) -> list[dict]:
    """Проверка input по каталогу. Уровни: error (запрос не отправлять), warn, info."""
    issues = []

    def add(level, param, msg):
        issues.append({"level": level, "param": param, "msg": msg})

    name, pr, params = provider_view(model, provider, providers)
    mid = model["id"]
    if not isinstance(inp, dict):
        add("error", None, "input должен быть объектом")
        return issues
    if not params:
        add("warn", None, "у модели/провайдера нет parameters в каталоге — проверка невозможна "
                          "(вызов через /v1/media не документирован)")
    for k, v in inp.items():
        if k in params or k in ALLOWED_EXTRA:
            continue
        if k == "prompt" and v in ("", None):
            add("info", k, "пустой prompt у модели без prompt в каталоге (так в гайде topaz-upscale.mdx)")
            continue
        add("error" if strict else "warn", k, f"параметра нет в каталоге модели ({name}); polza может ответить 400 "
                                              f"(строгая валидация, как у Lyria) — уберите или --allow-unknown")
    for k, spec in params.items():
        v = inp.get(k)
        present = k in inp and v is not None
        if spec.get("required") and not present:
            add("error", k, "обязательный параметр не задан" + (f" (default каталога {spec['default']!r})"
                                                                 if spec.get("default") is not None else ""))
        if not present:
            continue
        if k in ("images", "videos", "audio_ids", "character_ids"):
            if not isinstance(v, list):
                add("error", k, "ожидается массив")
                continue
            n = len(v)
            mn, mx = spec.get("min"), spec.get("max")
            if mn is not None and n < mn:
                add("error", k, f"нужно не меньше {mn}, передано {n}")
            if mx is not None and n > mx:
                add("error", k, f"допустимо не больше {mx}, передано {n}")
            if k in ("images", "videos"):
                for i, it in enumerate(v):
                    if isinstance(it, dict):
                        if it.get("type") not in ("url", "base64") or not it.get("data"):
                            add("error", f"{k}[{i}]", "объект файла: {type: url|base64, data} (OpenAPI MediaFileDto)")
                    elif not isinstance(it, str):
                        add("error", f"{k}[{i}]", "ожидается URL, путь к файлу или {type, data}")
            continue
        vals = spec.get("values")
        if vals is not None:
            s = as_str(v)
            if s not in vals:
                add("error", k, f"значение {v!r} не из допустимых {vals}")
            elif not isinstance(v, str):
                add("info", k, f"каталог перечисляет строки; {v!r} будет отправлено как {s!r}")
        mxl = spec.get("max_length")
        if mxl is not None and isinstance(v, str) and len(v) > mxl:
            add("error", k, f"длина {len(v)} > max_length {mxl}")
        if vals is None and ("min" in spec or "max" in spec) and k not in ("images", "videos"):
            n = to_num(v)
            auto = spec.get("auto_value")
            if n is None:
                add("error", k, f"ожидается число, передано {v!r}")
            elif auto is not None and n == auto:
                pass
            else:
                if spec.get("min") is not None and n < spec["min"]:
                    add("error", k, f"{n} < min {spec['min']}")
                if spec.get("max") is not None and n > spec["max"]:
                    add("error", k, f"{n} > max {spec['max']}")
        desc = spec.get("description") or ""
        m = re.search(r"до\s+(\d[\d\s]*)\s+символ", desc)
        if k == "prompt" and m and isinstance(v, str):
            lim = int(m.group(1).replace(" ", ""))
            if len(v) > lim and (mxl is None or lim < mxl):
                add("warn", k, f"описание каталога: «до {lim} символов», max_length {mxl} — длиннее {lim} [спорно]")
    # --- перекрёстные правила по моделям (описания параметров каталога, гайды, документация KIE) ---
    ar = inp.get("aspect_ratio")
    res = inp.get("image_resolution")
    # Flare: id до 25.09.2026 — gpt-image-2-5-flare, с 25.09.2026 — openai/gpt-image-2.5-flare (снимок 2026-09-25_1411; агент U)
    if mid in ("openai/gpt-image-2.5-sunburst", "openai/gpt-image-2.5-flare", "gpt-image-2-5-flare", "openai/gpt-5.4-image-2") and name == "mie":
        if (ar in (None, "auto")) and as_str(res) not in (None, "1K"):
            add("error", "image_resolution", "при aspect_ratio=auto или без него доступен только 1K (описание каталога)")
        if ar == "1:1" and as_str(res) == "4K":
            add("error", "image_resolution", "для 1:1 недоступен 4K (описание каталога)")
        if ar in ("27:16", "16:27", "9:8", "8:9") and as_str(res) not in (None, "1K"):
            add("warn", "image_resolution", f"{ar}: у KIE только 1K (документация KIE, агент P) [не проверено]")
    if mid == "qwen/image-2.1":
        if inp.get("mask_url"):
            if _len_items(inp.get("images")) != 1:
                add("error", "mask_url", "маска — только с одним референсом (описание каталога)")
            if inp.get("background") == "transparent":
                add("error", "mask_url", "маска несовместима с прозрачным фоном (описание каталога)")
        if inp.get("background") == "transparent" and inp.get("output_format", "png") not in ("png", "webp"):
            add("error", "output_format", "background=transparent требует png или webp (описание каталога)")
    if mid == "openai/gpt-5-image" and name == "mie" and not inp.get("prompt") and not inp.get("images"):
        add("error", "prompt", "prompt обязателен, если нет images (описание каталога)")
    if mid in ("google/veo3", "google/veo3_fast"):
        gt = inp.get("generationType")
        n = _len_items(inp.get("images"))
        need = {"TEXT_2_VIDEO": (0, 0), "FIRST_AND_LAST_FRAMES_2_VIDEO": (1, 2), "REFERENCE_2_VIDEO": (1, 3)}
        if gt in need and not (need[gt][0] <= n <= need[gt][1]):
            add("error", "generationType", f"{gt} требует {need[gt][0]}–{need[gt][1]} картинок, передано {n}")
        if gt is None and n:
            add("info", "generationType", "не задан — polza определит по числу картинок (1–2 → кадры у Quality; "
                                          "у Fast неоднозначно: кадры или референсы) — задайте явно")
        if gt == "REFERENCE_2_VIDEO":
            add("info", "generationType", "KIE: REFERENCE_2_VIDEO — только 8 с и 16:9 [документация KIE]")
        et = as_str(inp.get("enableTranslation", "true"))
        if et == "false" and CYR.search(str(inp.get("prompt") or "")):
            add("warn", "enableTranslation", "кириллица при enableTranslation=false: KIE отвечает «Only English "
                                             "prompts are supported» [документация KIE]")
        if et == "true":
            add("info", "enableTranslation", "по умолчанию промт переводится на английский (текст в кадре тоже)")
    if mid in ("kling/v3", "kling/v2.6") and inp.get("images") and "aspect_ratio" in inp:
        add("info", "aspect_ratio", "игнорируется при стартовом кадре — соотношение берётся из картинки")
    if mid == "bytedance/seedance-2-5":
        d = to_num(inp.get("duration"))
        if d == -1 and not inp.get("videos"):
            add("error", "duration", "-1 (по длине референса) допустимо только вместе с videos")
    if mid == "gemini-omni-video":
        q = _len_items(inp.get("images")) + 2 * _len_items(inp.get("videos")) + _len_items(inp.get("character_ids"))
        if q > 7:
            add("error", "images", f"квота images + 2×videos + character_ids = {q} > 7 (описание каталога)")
    if mid.endswith("motion-control") and ref_seconds is not None:
        cap = 10 if inp.get("character_orientation") == "image" else 30
        if ref_seconds > cap:
            add("error", "videos", f"видео движения {ref_seconds:g} с > {cap} с для character_orientation="
                                   f"{inp.get('character_orientation')}")
    # --- линты расходов и «опасных» умолчаний ---
    for k in ("generate_audio", "sound"):
        spec = params.get(k)
        if spec is not None:
            v = as_str(inp.get(k, spec.get("default")))
            if v == "true":
                add("warn", k, ("включён звук" + ("" if k in inp else " (default каталога)") +
                                ": для фоновых петель и синемаграфов ставьте false"))
    if "duration" in params and "duration" not in inp:
        dflt = params["duration"].get("default")
        if dflt is not None and (to_num(dflt) or 0) >= 8:
            add("warn", "duration", f"default каталога {dflt} с — задайте длительность явно (цена за секунду)")
    if "aspect_ratio" in params and "aspect_ratio" not in inp and model.get("type") == "video":
        dflt = params["aspect_ratio"].get("default")
        if dflt not in (None, "16:9", "auto", "Auto"):
            add("warn", "aspect_ratio", f"default каталога {dflt} — задайте соотношение явно")
    return issues


# ---------------------------------------------------------------------------------------------------------------
# Нормализация
# ---------------------------------------------------------------------------------------------------------------

def _ptype(spec: dict, name: str | None = None) -> str:
    if name in ("images", "videos"):
        return "file_list"          # [{type: url|base64, data}] (OpenAPI MediaFileDto)
    if name in ("audio_ids", "character_ids"):
        return "id_list"
    if name == "mask_url":
        return "url"
    vals = spec.get("values")
    if vals is not None:
        if set(vals) <= BOOL_STR:
            return "bool_string"
        return "enum_string"
    d = spec.get("default")
    if isinstance(d, bool):
        return "bool"
    if isinstance(d, str) and d in BOOL_STR:
        return "bool_string"
    if "min" in spec or "max" in spec:
        return "number"
    if "max_length" in spec:
        return "string"
    return "any"


def _price_summary(model: dict, pr: dict, params: dict) -> dict:
    kind = pricing_kind(pr)
    out = {"kind": kind, "currency": pr.get("currency", "RUB"), "unit_param": pr.get("unitParam"),
           "price_params": price_params(model, pr, params), "raw": pr}
    if kind in ("tiers", "tiers_per_unit"):
        costs = [float(t["cost_rub"]) for t in pr["tiers"]]
        fb = [float(t["cost_rub"]) for t in pr["tiers"] if not t.get("conditions")]
        out.update(rate_min=min(costs), rate_max=max(costs), fallback=fb[0] if fb else None)
    elif kind == "per_request":
        out.update(rate_min=float(pr["per_request"]), rate_max=float(pr["per_request"]))
    elif kind == "per_second":
        out.update(rate_min=float(pr["video_per_second"]), rate_max=float(pr["video_per_second"]))
    elif kind == "tokens":
        out["usd_per_million"] = {k: round(float(v) / FX_POLZA_USD_RUB, 4) for k, v in pr.items()
                                  if k.endswith(("_per_million", "_per_thousand"))}
    try:
        e = estimate(model, {}, provider=None)
    except Exception:  # noqa: BLE001
        e = None
    if e is not None:
        out["with_defaults_rub"] = e["rub"]
        out["with_defaults_rate"] = e["rate_rub"]
        out["with_defaults_formula"] = e["formula"] or (
            f"{fmt_rub(e['rate_rub'])} ₽/с × длительность" if e.get("rate_rub") is not None else "")
        out["with_defaults_warnings"] = e["warnings"]
    return out


def _dur_pick(params: dict, want: int = 5):
    """Длительность для примера: want, если допустима, иначе ближайшая допустимая."""
    spec = params.get("duration")
    if not spec:
        return None
    if spec.get("values"):
        vals = [to_num(v) for v in spec["values"]]
        best = min(vals, key=lambda v: (abs(v - want), v))
        return as_str(best)
    lo, hi = spec.get("min", want), spec.get("max", want)
    return int(min(max(want, lo), hi))


def price_grid(model: dict, provider: str | None = None, providers: list | None = None, want_seconds: int = 5,
               max_rows: int = 64) -> list[dict]:
    """Сетка цен по всем значениям ценовых параметров (для таблиц «разрешение × звук × видео-референс»).
    Для видео с ценой за секунду длительность = want_seconds (или ближайшая допустимая); если длительность сама —
    ценовой параметр ступеней (цена за ролик), перебираются все её значения."""
    name, pr, params = provider_view(model, provider, providers)
    kind = pricing_kind(pr)
    axes = []
    tk = tier_keys(pr)
    for p in price_params(model, pr, params):
        if p == "duration":
            if "duration" in tk and params.get("duration", {}).get("values"):
                axes.append(("duration", list(params["duration"]["values"])))
            continue
        if p == "videos":
            axes.append(("videos", [None, [{"type": "url", "data": "https://example.com/ref.mp4"}]]))
            continue
        if p == "images":
            mx = int(params.get("images", {}).get("max") or 0)
            axes.append(("images", [None, ["ref"] * 1, ["ref"] * mx] if mx > 1 else [None, ["ref"]]))
            continue
        vals = (params.get(p) or {}).get("values")
        if vals:
            axes.append((p, list(vals)))
    base = {}
    if "duration" in params and not any(a[0] == "duration" for a in axes):
        d = _dur_pick(params, want_seconds)
        if d is not None:
            base["duration"] = d
    rows = []

    def rec(i, cur):
        if len(rows) >= max_rows:
            return
        if i == len(axes):
            inp = {k: v for k, v in cur.items() if v is not None}
            e = estimate(model, inp, provider=provider, providers=providers)
            show = {k: (f"{len(v)} шт." if isinstance(v, list) else v) for k, v in inp.items()}
            rows.append({"input": show, "rub": e["rub"], "rate_rub": e["rate_rub"], "units": e["units"],
                         "formula": e["formula"]})
            return
        k, vals = axes[i]
        for v in vals:
            cur2 = dict(cur)
            cur2[k] = v
            rec(i + 1, cur2)

    rec(0, dict(base))
    return rows


def _unified(model_id: str, params: dict) -> dict:
    u = {}
    for canon, names in UNIFIED:
        for n in names:
            if n in params:
                spec = dict(params[n])
                spec["param"] = n
                spec["type"] = _ptype(params[n], n)
                if canon in ("resolution", "quality", "mode") and model_id in RESOLUTION_MAP:
                    rp, mp = RESOLUTION_MAP[model_id]
                    if rp == n:
                        spec["means_resolution"] = mp
                u[canon] = spec
                break
    return u


def _derived_notes(m: dict, params: dict, pr: dict) -> list[str]:
    notes = []
    for k in ("generate_audio", "sound"):
        if k in params and as_str(params[k].get("default")) == "true":
            notes.append(f"{k}: default true — звук включён по умолчанию")
    if "duration" in params:
        dflt = params["duration"].get("default")
        if dflt is not None and (to_num(dflt) or 0) >= 8:
            notes.append(f"duration: default {dflt} с (дорого при цене за секунду)")
        if params["duration"].get("auto_value") is not None:
            notes.append(f"duration: auto_value {params['duration']['auto_value']} — длительность по референсу")
    if m.get("type") == "video" and "aspect_ratio" in params:
        dflt = params["aspect_ratio"].get("default")
        if dflt not in (None, "16:9", "auto", "Auto"):
            notes.append(f"aspect_ratio: default {dflt}")
    fb = [t for t in pr.get("tiers") or [] if not t.get("conditions")]
    if fb:
        costs = [float(t["cost_rub"]) for t in pr["tiers"]]
        if float(fb[0]["cost_rub"]) == max(costs) and len(set(costs)) > 1:
            notes.append(f"запасная ступень [] = максимум ({fb[0]['cost_rub'].rstrip('0').rstrip('.')} ₽) — "
                         "передавайте ценовые параметры явно")
    for k in tier_keys(pr):
        base = {"has_video": "videos", "input_images_count": "images"}.get(k, k)
        if base not in params and not (k == "sound" and "generate_audio" in params):
            notes.append(f"условие цены {k!r} не соответствует ни одному параметру")
        if k == "sound" and "sound" not in params and "generate_audio" in params:
            notes.append("цена: условие sound=…, параметр generate_audio (калькулятор сопоставляет)")
    for k, spec in params.items():
        desc = spec.get("description") or ""
        mm = re.search(r"до\s+(\d[\d\s]*)\s+символ", desc)
        if mm and spec.get("max_length") and int(mm.group(1).replace(" ", "")) != spec["max_length"]:
            notes.append(f"{k}: описание «до {mm.group(1)} символов», max_length {spec['max_length']}")
    return notes


def normalize_model(m: dict, providers: list | None = None) -> dict:
    tp = m.get("top_provider") or {}
    params = m.get("parameters") or tp.get("parameters") or {}
    pr = tp.get("pricing") or {}
    out = {
        "id": m["id"], "name": m.get("name"), "type": m.get("type"),
        "created": dt.datetime.fromtimestamp(m["created"], dt.timezone.utc).date().isoformat() if m.get("created") else None,
        "provider": tp.get("name"),
        "endpoints": m.get("endpoints"),
        "input_modalities": (m.get("architecture") or {}).get("input_modalities"),
        "output_modalities": (m.get("architecture") or {}).get("output_modalities"),
        "flags": {"fz152": tp.get("is_fz152_compliant"), "data_in_russia": tp.get("stores_data_in_russia"),
                  "hosted_on_polza": tp.get("is_hosted_on_polza_infrastructure"), "moderated": tp.get("is_moderated")},
        "context_length": tp.get("context_length"),
        "unified": _unified(m["id"], params),
        "params": params,
        "param_types": {k: _ptype(v, k) for k, v in params.items()},
        "required": [k for k, v in params.items() if v.get("required")],
        "defaults": {k: v["default"] for k, v in params.items() if "default" in v},
        "pricing": _price_summary(m, pr, params),
        "price_grid": price_grid(m) if pr else [],
        "operations": [{"id": o["id"], "name": o.get("name"), "async": o.get("async"),
                        "rub": float(o["pricing"]["per_request"]) if (o.get("pricing") or {}).get("per_request") else None,
                        "params": o.get("parameters")} for o in m.get("operations") or []],
        "notes": _derived_notes(m, params, pr),
        "doc_vs_catalog": DOC_VS_CATALOG.get(m["id"], []),
        "short_description": m.get("short_description"),
    }
    if providers is not None:
        plist = []
        for p in providers:
            pp = p.get("parameters") or {}
            ppr = p.get("pricing") or {}
            item = {"name": p.get("name"), "is_top": p.get("name") == tp.get("name"),
                    "flags": {"fz152": p.get("is_fz152_compliant"), "data_in_russia": p.get("stores_data_in_russia"),
                              "hosted_on_polza": p.get("is_hosted_on_polza_infrastructure"),
                              "moderated": p.get("is_moderated")},
                    "pricing_kind": pricing_kind(ppr), "pricing": ppr,
                    "param_names": sorted(pp), "params_differ": pp != params}
            if pp != params and pp:
                diff = {}
                for k in sorted(set(pp) | set(params)):
                    if pp.get(k) != params.get(k):
                        diff[k] = {"top": params.get(k), "this": pp.get(k)}
                item["param_diff_vs_top"] = diff
            if m.get("type") == "image":
                try:
                    ex = {}
                    for r in ("1K", "2K", "4K"):
                        inp = {"prompt": "x" * 300}
                        if "image_resolution" in pp or pricing_kind(ppr) == "tokens":
                            inp["image_resolution"] = r
                        e = estimate(m, inp, provider=p.get("name"), providers=providers)
                        ex[r] = e["rub"]
                    item["example_rub_by_resolution"] = ex
                    item["example_note"] = "промт 300 символов, без референсов; токенные — оценка по таблицам вендора"
                except Exception as e:  # noqa: BLE001
                    item["example_error"] = str(e)
            plist.append(item)
        out["providers"] = plist
    return out


def normalize_snapshot(snap: Snapshot) -> dict:
    media = snap.media()
    models = [normalize_model(m, snap.providers.get(m["id"]) if snap.providers else None) for m in media]
    models.sort(key=lambda x: (x["type"], x["id"]))
    return {
        "schema": "polza-media-normalized/1",
        "generated_by": f"99-raw/tools/polza_catalog.py {VERSION}",
        "generated_at": now_msk().isoformat(timespec="seconds"),
        "checked": now_msk().date().isoformat(),
        "snapshot_dir": str(snap.dir.relative_to(ROOT)) if snap.dir.is_relative_to(ROOT) else str(snap.dir),
        "snapshot_fetched_at": snap.fetched_at(),
        "source_sha256": sha256_bytes((snap.dir / "api-v1-models.json").read_bytes()),
        "providers_source": snap.providers_source,
        "fx_usd_rub_polza": FX_POLZA_USD_RUB,
        "tier_semantics": "самая точная подходящая ступень (больше условий), иначе [] — вывод по каталогу [не проверено]",
        "counts": {"all": len(snap.models), "image": sum(1 for m in media if m["type"] == "image"),
                   "video": sum(1 for m in media if m["type"] == "video")},
        "unified_fields": {c: n for c, n in UNIFIED},
        "models": models,
    }


def cmd_normalize(a):
    snap = Snapshot(a.snapshot, a.providers)
    data = normalize_snapshot(snap)
    out = Path(a.out) if a.out else snap.dir / "media-models.normalized.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{out} — {data['counts']['image']} картинок, {data['counts']['video']} видео; "
          f"провайдеры: {data['providers_source'] or 'нет (снимок без include_providers)'}")


# ---------------------------------------------------------------------------------------------------------------
# Таблица
# ---------------------------------------------------------------------------------------------------------------

def _vals(spec):
    if not spec:
        return "—"
    if spec.get("values"):
        v = "/".join(spec["values"])
        return v + (f" (по умолч. {spec['default']})" if spec.get("default") is not None else "")
    parts = []
    if "min" in spec or "max" in spec:
        parts.append(f"{spec.get('min', '')}–{spec.get('max', '')}")
    if spec.get("default") is not None:
        parts.append(f"по умолч. {spec['default']}")
    return ", ".join(parts) or "есть"


def _price_cell(n: dict) -> str:
    p = n["pricing"]
    k = p["kind"]
    if k == "per_request":
        return f"{fmt_rub(p['rate_min'])} ₽/запрос"
    if k == "per_second":
        return f"{fmt_rub(p['rate_min'])} ₽/с"
    if k == "tiers":
        return f"{fmt_rub(p['rate_min'])}–{fmt_rub(p['rate_max'])} ₽ по {', '.join(p['price_params'])}"
    if k == "tiers_per_unit":
        return f"{fmt_rub(p['rate_min'])}–{fmt_rub(p['rate_max'])} ₽/с по {', '.join(x for x in p['price_params'] if x != 'duration')}"
    if k == "tokens":
        pr = p["raw"]
        return f"токены: вых. картинка {fmt_rub(float(pr.get('image_output_per_million', 0)))} ₽/1M"
    return k


def table_md(snap: Snapshot, types=MEDIA_TYPES) -> str:
    norm = normalize_snapshot(snap)
    lines = [f"<!-- polza_catalog.py table · снимок {norm['snapshot_dir']} ({norm['snapshot_fetched_at']}) -->", ""]
    for t in types:
        ms = [m for m in norm["models"] if m["type"] == t]
        ms.sort(key=lambda x: x["created"] or "", reverse=True)
        lines.append(f"### {'Картинки' if t == 'image' else 'Видео'} ({len(ms)})")
        lines.append("")
        if t == "image":
            lines.append("| id | провайдер | цена | с умолч. | реф. | соотношения | разрешение/качество | прочее |")
            lines.append("|---|---|---|---|---|---|---|---|")
        else:
            lines.append("| id | провайдер | цена | с умолч. | длительность, с | разрешение/режим | реф. карт./видео | звук | соотношения | прочее |")
            lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for m in ms:
            u = m["unified"]
            ref = u.get("ref_images")
            refs = f"{ref.get('min', 0)}–{ref.get('max', '?')}" if ref else "—"
            res = u.get("resolution") or u.get("mode") or u.get("quality")
            rescell = _vals(res)
            if res and res.get("means_resolution"):
                rescell += " = " + "/".join(f"{k}→{v}" for k, v in res["means_resolution"].items())
            other = [k for k in ("negative_prompt", "mask", "seed", "background", "output_format", "fixed_camera",
                                 "multi_shot", "generation_type", "prompt_enhance", "prompt_translate",
                                 "upscale_factor", "watermark", "strength", "guidance_scale") if k in u]
            other_s = ", ".join(f"`{u[k]['param']}`" for k in other) or "—"
            wd = m["pricing"].get("with_defaults_rub")
            wr = m["pricing"].get("with_defaults_rate")
            wd_s = (f"{fmt_rub(wd)} ₽" if wd is not None else (f"{fmt_rub(wr)} ₽/с × длит." if wr is not None else "—"))
            if t == "image":
                lines.append(f"| `{m['id']}` | {m['provider']} | {_price_cell(m)} | {wd_s} | {refs} | "
                             f"{_vals(u.get('aspect_ratio'))} | {rescell} | {other_s} |")
            else:
                vref = u.get("ref_videos")
                vrefs = f"{vref.get('min', 0)}–{vref.get('max', '?')}" if vref else "—"
                lines.append(f"| `{m['id']}` | {m['provider']} | {_price_cell(m)} | {wd_s} | {_vals(u.get('duration'))} | "
                             f"{rescell} | {refs} / {vrefs} | {_vals(u.get('audio'))} | {_vals(u.get('aspect_ratio'))} | {other_s} |")
        lines.append("")
    return "\n".join(lines)


def cmd_table(a):
    snap = Snapshot(a.snapshot)
    types = (a.type,) if a.type else MEDIA_TYPES
    md = table_md(snap, types)
    if a.out:
        Path(a.out).write_text(md + "\n")
        print(a.out)
    else:
        print(md)


# ---------------------------------------------------------------------------------------------------------------
# Сравнение снимков
# ---------------------------------------------------------------------------------------------------------------

def _jd(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def diff_snapshots(a: Snapshot, b: Snapshot, all_types: bool = False) -> dict:
    ta = {m["id"]: m for m in (a.models if all_types else a.media())}
    tb = {m["id"]: m for m in (b.models if all_types else b.media())}
    res = {"a": str(a.dir.name), "b": str(b.dir.name), "a_fetched": a.fetched_at(), "b_fetched": b.fetched_at(),
           "counts_a": {}, "counts_b": {}, "added": [], "removed": [], "changed": {}}
    for s, key in ((a, "counts_a"), (b, "counts_b")):
        c = {}
        for m in s.models:
            c[m.get("type")] = c.get(m.get("type"), 0) + 1
        res[key] = dict(sorted(c.items()))
    res["added"] = [{"id": i, "type": tb[i].get("type"), "name": tb[i].get("name"),
                     "provider": (tb[i].get("top_provider") or {}).get("name")} for i in sorted(set(tb) - set(ta))]
    res["removed"] = [{"id": i, "type": ta[i].get("type"), "name": ta[i].get("name")} for i in sorted(set(ta) - set(tb))]
    for i in sorted(set(ta) & set(tb)):
        ma, mb = ta[i], tb[i]
        ch = {}
        tpa, tpb = ma.get("top_provider") or {}, mb.get("top_provider") or {}
        if tpa.get("name") != tpb.get("name"):
            ch["top_provider"] = [tpa.get("name"), tpb.get("name")]
        if _jd(tpa.get("pricing")) != _jd(tpb.get("pricing")):
            pa, pb = tpa.get("pricing") or {}, tpb.get("pricing") or {}
            if pa.get("tiers") or pb.get("tiers"):
                sa = {",".join(sorted(t["conditions"])): t["cost_rub"] for t in pa.get("tiers") or []}
                sb = {",".join(sorted(t["conditions"])): t["cost_rub"] for t in pb.get("tiers") or []}
                tch = {}
                for k in sorted(set(sa) | set(sb)):
                    if sa.get(k) != sb.get(k):
                        tch[k or "[]"] = [sa.get(k), sb.get(k)]
                ch["tiers"] = tch
            other = {k: [pa.get(k), pb.get(k)] for k in sorted(set(pa) | set(pb)) if k != "tiers" and pa.get(k) != pb.get(k)}
            if other:
                ch["pricing"] = other
        pa_, pb_ = ma.get("parameters") or {}, mb.get("parameters") or {}
        if _jd(pa_) != _jd(pb_):
            pc = {"added": sorted(set(pb_) - set(pa_)), "removed": sorted(set(pa_) - set(pb_)), "changed": {}}
            for k in sorted(set(pa_) & set(pb_)):
                if _jd(pa_[k]) != _jd(pb_[k]):
                    fields = {}
                    for f in sorted(set(pa_[k]) | set(pb_[k])):
                        if pa_[k].get(f) != pb_[k].get(f):
                            fields[f] = [pa_[k].get(f), pb_[k].get(f)]
                    pc["changed"][k] = fields
            ch["parameters"] = pc
        if _jd(ma.get("operations")) != _jd(mb.get("operations")):
            ch["operations"] = True
        for f in ("name", "endpoints", "short_description"):
            if ma.get(f) != mb.get(f):
                ch[f] = [ma.get(f), mb.get(f)]
        fl = {}
        for f in ("is_fz152_compliant", "stores_data_in_russia", "is_hosted_on_polza_infrastructure", "is_moderated"):
            if tpa.get(f) != tpb.get(f):
                fl[f] = [tpa.get(f), tpb.get(f)]
        if fl:
            ch["flags"] = fl
        if a.providers and b.providers and i in a.providers and i in b.providers:
            na = {p["name"]: p for p in a.providers[i]}
            nb = {p["name"]: p for p in b.providers[i]}
            pch = {}
            if set(na) != set(nb):
                pch["added"] = sorted(set(nb) - set(na))
                pch["removed"] = sorted(set(na) - set(nb))
            for n in sorted(set(na) & set(nb)):
                if _jd(na[n].get("pricing")) != _jd(nb[n].get("pricing")):
                    pch.setdefault("pricing_changed", []).append(n)
                if _jd(na[n].get("parameters")) != _jd(nb[n].get("parameters")):
                    pch.setdefault("parameters_changed", []).append(n)
            if pch:
                ch["providers"] = pch
        if ch:
            res["changed"][i] = ch
    return res


def diff_md(d: dict) -> str:
    L = [f"# Сравнение снимков polza: {d['a']} → {d['b']}", "",
         f"- A: `{d['a']}` ({d['a_fetched']}), B: `{d['b']}` ({d['b_fetched']})",
         f"- модели по типам A: {d['counts_a']}", f"- модели по типам B: {d['counts_b']}", ""]
    L.append(f"## Новые ({len(d['added'])})")
    L += [f"- `{x['id']}` ({x['type']}, {x['name']}, провайдер {x.get('provider')})" for x in d["added"]] or ["- нет"]
    L.append("")
    L.append(f"## Удалённые ({len(d['removed'])})")
    L += [f"- `{x['id']}` ({x['type']}, {x['name']})" for x in d["removed"]] or ["- нет"]
    L.append("")
    L.append(f"## Изменённые ({len(d['changed'])})")
    if not d["changed"]:
        L.append("- нет")
    for i, ch in d["changed"].items():
        L.append(f"### `{i}`")
        for k, v in ch.items():
            if k == "tiers":
                for cond, (x, y) in v.items():
                    L.append(f"- ступень `{cond}`: {x} → {y}")
            elif k == "parameters":
                if v["added"]:
                    L.append(f"- параметры добавлены: {', '.join(v['added'])}")
                if v["removed"]:
                    L.append(f"- параметры удалены: {', '.join(v['removed'])}")
                for p, fields in v["changed"].items():
                    for f, (x, y) in fields.items():
                        L.append(f"- `{p}.{f}`: {_jd(x)} → {_jd(y)}")
            else:
                L.append(f"- {k}: {_jd(v)}")
        L.append("")
    return "\n".join(L)


def cmd_diff(a):
    sa, sb = Snapshot(a.a), Snapshot(a.b)
    d = diff_snapshots(sa, sb, a.all_types)
    print(json.dumps(d, ensure_ascii=False, indent=1) if a.json else diff_md(d))


# ---------------------------------------------------------------------------------------------------------------
# price / check / selftest
# ---------------------------------------------------------------------------------------------------------------

def parse_kv(items: list[str]) -> dict:
    out = {}
    for it in items or []:
        k, _, v = it.partition("=")
        if v.startswith("[") or v.startswith("{"):
            out[k] = json.loads(v)
        elif re.fullmatch(r"-?\d+", v):
            out[k] = int(v)
        elif re.fullmatch(r"-?\d+\.\d+", v):
            out[k] = float(v)
        elif k in ("images", "videos"):
            out[k] = [x for x in v.split(",") if x]
        else:
            out[k] = v
    return out


def cmd_price(a):
    snap = Snapshot(a.snapshot)
    m = snap.by_id.get(a.model) or sys.exit(f"нет модели {a.model}")
    inp = parse_kv(a.kv)
    e = estimate(m, inp, provider=a.provider, providers=snap.providers.get(a.model), ref_seconds=a.ref_seconds)
    print(json.dumps(e, ensure_ascii=False, indent=1))
    note, check = snapshot_note(snap)
    print(("! " if check else "") + note, file=sys.stderr)


def cmd_check(a):
    snap = Snapshot(a.snapshot)
    m = snap.by_id.get(a.model) or sys.exit(f"нет модели {a.model}")
    inp = parse_kv(a.kv)
    name, pr, params = provider_view(m, a.provider, snap.providers.get(a.model))
    inp2, notes = coerce_input(params, inp)
    inp3, filled, missing = fill_defaults(m, inp2, params, pr)
    for n in notes:
        print("приведено:", n)
    if filled:
        print("подставлено из default каталога:", ", ".join(f"{k}={inp3[k]!r}" for k in filled))
    if missing:
        print("ценовые/обязательные параметры без default:", ", ".join(missing))
    for i in validate(m, inp3, provider=a.provider, providers=snap.providers.get(a.model)):
        print(f"[{i['level']}] {i['param']}: {i['msg']}")
    print(json.dumps(inp3, ensure_ascii=False))


def selftest_offline() -> int:
    """Проверки без снимка каталога и без сети: снимок при обрыве и при ответе не каталогом, возраст снимка. Каталог и
    ответы канала — вымышленные, во временной папке. Возвращает число ошибок."""
    import contextlib
    import io
    import tempfile
    global CACHE
    bad = 0

    def take(*args, **kw):       # строки хода снимка самопроверке не нужны: итог — строки OK и FAIL
        with contextlib.redirect_stdout(io.StringIO()):
            return take_snapshot(*args, **kw)

    def ok(name, cond, got=""):
        nonlocal bad
        bad += not cond
        print(("OK  " if cond else "FAIL"), name + (f" — {got}" if got != "" and not cond else ""))

    body = json.dumps({"data": [{"id": "demo/image", "type": "image", "name": "Demo Image", "top_provider": {
        "name": "demo", "pricing": {"per_request": 1.5}, "parameters": {"prompt": {"type": "string"}}}}]}).encode()

    def good(url):
        return 200, {"Content-Type": "application/json"}, body

    def failing(exc_at=None, status_at=None):
        calls = []

        def get(url):
            calls.append(url)
            if len(calls) == exc_at:
                raise http.client.IncompleteRead(body[:40], len(body) - 40)
            if len(calls) == status_at:
                return 502, {"Content-Type": "text/html"}, b"<html>Bad Gateway</html>"
            return good(url)
        return get

    def names(root):
        return sorted(x.name for x in root.iterdir())

    cache = CACHE
    try:
        with tempfile.TemporaryDirectory(prefix="polza-catalog-selftest-") as t:
            root = CACHE = Path(t)
            t1 = dt.datetime(2026, 1, 10, 9, 0, tzinfo=MSK)
            d1, snap1, meta = take(root, get=good, pause=0, stamp=t1)
            norm = json.loads((d1 / "media-models.normalized.json").read_text())
            ok("снимок: папка даты с метаданными и нормализацией, временной папки нет",
               names(root) == ["2026-01-10"] and len(meta["files"]) == 4 and (d1 / "snapshot.meta.json").exists()
               and norm["snapshot_dir"] == str(d1) and len(snap1.models) == 1, (names(root), norm.get("snapshot_dir")))
            for label, get in (("обрыв сети на втором файле", failing(exc_at=2)),
                               ("обрыв сети на первом файле", failing(exc_at=1)),
                               ("ответ 502 вместо каталога", failing(status_at=1))):
                try:
                    take(root, get=get, pause=0, stamp=t1 + dt.timedelta(hours=2))
                    err = None
                except SnapshotError as e:
                    err = str(e)
                ok(f"{label}: снимок не снят, новой и временной папок нет", err is not None and names(root) == ["2026-01-10"],
                   (err, names(root)))
                ok(f"{label}: последним остаётся прежний снимок", find_snapshot(None) == d1, find_snapshot(None))
            half = root / ".snapshot-20260110-120000-1.part"
            half.mkdir()
            (half / "api-v1-models.json").write_bytes(body)
            ok("временная папка идущего снимка — не «последний снимок»", find_snapshot(None) == d1, find_snapshot(None))
            d2, _, _ = take(root, get=failing(status_at=3), pause=0, stamp=t1 + dt.timedelta(hours=3))
            ok("вспомогательный файл с ответом не 200 снимок не срывает: статус — в метаданных",
               d2.name == "2026-01-10_1200" and json.loads((d2 / "snapshot.meta.json").read_text())["files"][
                   "api-v1-models-catalog.image.json"]["status"] == 502, d2.name)
            note, check = snapshot_note(snap1, now=t1 + dt.timedelta(hours=3))
            ok("возраст: снимок за сегодня — строка с папкой и возрастом, без отметки",
               not check and "2026-01-10" in note and "3 ч назад" in note, note)
            note, check = snapshot_note(snap1, now=t1 + dt.timedelta(hours=30))
            ok("возраст: снимок не за сегодня — отметка и команда обновления",
               check and "не за сегодня" in note and "polza_catalog.py snapshot" in note, note)
            (d1 / "snapshot.meta.json").unlink()
            note, check = snapshot_note(Snapshot(str(d1)), now=dt.datetime.fromtimestamp(d1.stat().st_mtime, MSK))
            ok("возраст: папка без snapshot.meta.json — отметка «не до конца»", check and "не до конца" in note, note)
    finally:
        CACHE = cache
    return bad


def cmd_selftest(a):
    bad = selftest_offline()
    if a.offline:
        print("ИТОГО:", "все проверки пройдены" if not bad else f"{bad} ошибок")
        sys.exit(1 if bad else 0)
    snap = Snapshot(a.snapshot)
    by = snap.by_id
    cases = [
        ("tongyi-mai/z-image", {}, 1.40),
        ("openai/gpt-image-2.5-sunburst", {"image_resolution": "2K"}, 7.0),
        ("openai/gpt-image-2.5-sunburst", {}, 4.0),                      # default 1K
        ("qwen/image", {"aspect_ratio": "16:9"}, 2.25),
        ("seedream/5-pro-text-to-image", {"quality": "high", "images": ["a", "b", "c"]}, 10.6),
        ("seedream/5-pro-text-to-image", {"quality": "basic"}, 5.0),
        ("kling/v3", {"mode": "pro", "sound": False, "duration": 5}, 60.0),
        ("bytedance/seedance-1.5-pro", {"resolution": "480p", "duration": "4", "generate_audio": "false"}, 5.25),
        ("bytedance/seedance-2", {"resolution": "480p", "duration": 5}, 64.125),
        ("bytedance/seedance-2", {"resolution": "720p", "duration": 5, "videos": ["v"]}, 168.75),
        ("grok-imagine-video-1-5", {"resolution": "480p", "duration": 1}, 1.62),
        ("gemini-omni-video", {"resolution": "4k", "duration": "8"}, 82.0),
        ("gemini-omni-video", {"resolution": "4k", "videos": ["v"]}, 115.0),
        ("alibaba/wan-3.0", {"duration": "5"}, 117.992),
        ("minimax/hailuo-3-max", {}, 47.1968),
        ("wan/2.6", {"resolution": "1080p", "duration": "15"}, 236.25),
        ("topaz/video-upscale", {"upscale_factor": "4"}, None),
        ("google/veo3", {}, 187.5),
    ]
    for mid, inp, want in cases:
        e = estimate(by[mid], inp, ref_seconds=None)
        got = e["rub"]
        ok = (got is None and want is None) or (got is not None and want is not None and abs(got - want) < 1e-6)
        bad += not ok
        print(("OK  " if ok else "FAIL"), mid, inp, "→", got, "ожидалось", want, "|", e["formula"])
    iss = validate(by["openai/gpt-image-2.5-sunburst"], {"prompt": "x", "aspect_ratio": "1:1", "image_resolution": "4K"})
    ok = any(i["level"] == "error" and "1:1" in i["msg"] for i in iss)
    bad += not ok
    print(("OK  " if ok else "FAIL"), "gpt-image-2.5 1:1+4K → ошибка")
    fid = "openai/gpt-image-2.5-flare" if "openai/gpt-image-2.5-flare" in by else "gpt-image-2-5-flare"   # id сменился 25.09.2026
    if fid in by:
        iss = validate(by[fid], {"prompt": "x", "aspect_ratio": "1:1", "image_resolution": "4K"})
        ok = any(i["level"] == "error" and "1:1" in i["msg"] for i in iss)
        bad += not ok
        print(("OK  " if ok else "FAIL"), f"{fid} 1:1+4K → ошибка (правило mie для Flare)")
    print("ИТОГО:", "все проверки пройдены" if not bad else f"{bad} ошибок")
    sys.exit(1 if bad else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("snapshot")
    s.add_argument("--root")
    s.add_argument("--with-openapi", action="store_true")
    s.add_argument("--no-providers", action="store_true")
    s.set_defaults(fn=cmd_snapshot)
    s = sp.add_parser("normalize")
    s.add_argument("snapshot", nargs="?")
    s.add_argument("--providers", help="снимок, из которого взять providers[] (если в основном их нет)")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_normalize)
    s = sp.add_parser("table")
    s.add_argument("snapshot", nargs="?")
    s.add_argument("--type", choices=MEDIA_TYPES)
    s.add_argument("--out")
    s.set_defaults(fn=cmd_table)
    s = sp.add_parser("diff")
    s.add_argument("a")
    s.add_argument("b")
    s.add_argument("--all-types", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_diff)
    for nm, fn in (("price", cmd_price), ("check", cmd_check)):
        s = sp.add_parser(nm)
        s.add_argument("model")
        s.add_argument("kv", nargs="*")
        s.add_argument("--snapshot")
        s.add_argument("--provider")
        s.add_argument("--ref-seconds", type=float)
        s.set_defaults(fn=fn)
    s = sp.add_parser("selftest")
    s.add_argument("--snapshot", default="2026-09-23")
    s.add_argument("--offline", action="store_true", help="только проверки без снимка каталога: обрыв снимка, возраст")
    s.set_defaults(fn=cmd_selftest)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
