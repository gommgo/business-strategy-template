#!/usr/bin/env python3
"""polza.py — клиент Media API polza.ai для ai-media-research: сухой прогон по умолчанию, трата только с --live.

Агент B, волна 1, 2026-09-23. Python 3.13, только стандартная библиотека (+ polza_catalog.py рядом).
Проверен на локальном макете сервера (99-raw/experiments/B/01-mock-server), НЕ на настоящем polza (ключа нет).

Подкоманды:
  models [--type image|video] [--search S] [--fresh]   модели из снимка каталога (или свежий бесплатный GET)
  show MODEL [--provider P] [--json]                   параметры, цены, операции, провайдеры, заметки
  estimate JOB.json|JOBS.jsonl                         проверка по каталогу + цена + бюджет, без сети
  run JOB.json                                         одно задание (сухой прогон; --live — отправить)
  batch JOBS.jsonl [--parallel 2]                      серия (не больше 3 параллельно)
  status ID                                            статус генерации (GET /v1/media/{id})
  download ID                                          скачать результат готовой генерации + паспорт
  upload FILE [--permanent]                            загрузить файл в хранилище polza (TEMP_UPLOAD 24 ч / PERMANENT)
  ops ID extend|upscale_1080p|upscale_4k [--params JSON]   операция над готовым видео (Veo 3.1)
  ledger [--sum] [--agent X] [--tail N]                журнал затрат
  balance                                              GET /v2/balance и /v1/key (предполётная проверка)
  history ID                                           GET /v1/history/generations/{id} (провайдер, clientCost)

Задание (JSON): {"model": "...", "input": {...}, "provider": {...}?, "tag": "...", "agent": "B", "notes": "...",
  "variant": 1?, "max_rub": 10?, "out_dir": "..."?, "meta": {"ref_video_seconds": 7.5}?, "user": "..."?}
Файлы в input.images / input.videos: URL, data:URI, локальный путь (≤ 4 МБ — base64, больше — загрузка в хранилище)
или объект {"type": "url"|"base64", "data": ...} (OpenAPI MediaFileDto).

Окружение: POLZA_API_KEY или файл ~/.config/polza/api_key (права 600); POLZA_BASE_URL (по умолчанию
https://polza.ai/api); POLZA_CATALOG (снимок); POLZA_LEDGER; POLZA_OUT_ROOT; POLZA_BUDGET_TOTAL (2000);
POLZA_BUDGET_AGENT; POLZA_MAX_JOB (60). Ключ никогда не печатается и не пишется в журнал и паспорта.

Коды выхода: 0 — успех; 1 — ошибка задания/проверки; 2 — отказ по бюджету или цене; 3 — таймаут опроса (генерацию
можно дожать: download ID --live); 4 — генерация failed/cancelled; 5 — HTTP-ошибка; 6 — ошибка скачивания.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import datetime as dt
import fcntl
import hashlib
import json
import mimetypes
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
import polza_catalog as pc  # noqa: E402

VERSION = "polza.py 1.0 (2026-09-23)"
ROOT = pc.ROOT
DEFAULT_BASE = "https://polza.ai/api"
DEFAULT_LEDGER = kbpaths.out("ai-media") / "_ledger.jsonl"  # перенос: журнал затрат — общий с mp_client
DEFAULT_OUT_ROOT = kbpaths.out("ai-media", "_polza")
KEY_FILE = Path(os.environ.get("POLZA_KEY_FILE", str(Path.home() / ".config" / "polza" / "api_key")))
INLINE_MAX = 4 * 1024 * 1024          # до 4 МБ — base64 в теле, больше — загрузка в хранилище (media-input.mdx: «больше нескольких МБ — через хранилище»)
MAX_PARALLEL = 3
TERMINAL = ("completed", "failed", "cancelled")
EXIT_OK, EXIT_JOB, EXIT_BUDGET, EXIT_TIMEOUT, EXIT_FAILED, EXIT_HTTP, EXIT_DOWNLOAD = 0, 1, 2, 3, 4, 5, 6

_print_lock = threading.Lock()
_SECRET: str | None = None


# ---------------------------------------------------------------------------------------------------------------
# Секрет и вывод
# ---------------------------------------------------------------------------------------------------------------

def load_key() -> str | None:
    """Ключ из POLZA_API_KEY или ~/.config/polza/api_key. Значение нигде не печатается."""
    global _SECRET
    k = os.environ.get("POLZA_API_KEY")
    if not k and KEY_FILE.exists():
        mode = KEY_FILE.stat().st_mode & 0o777
        if mode & 0o077:
            say(f"! файл ключа {KEY_FILE} доступен не только владельцу (права {oct(mode)}): chmod 600", err=True)
        k = KEY_FILE.read_text().strip()
    _SECRET = k or None
    return _SECRET


def redact(s):
    if _SECRET and isinstance(s, str) and _SECRET in s:
        return s.replace(_SECRET, "***")
    return s


def redact_obj(o):
    if isinstance(o, dict):
        return {k: ("***" if k.lower() in ("authorization", "api_key", "apikey", "key") and isinstance(v, str)
                    else redact_obj(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [redact_obj(x) for x in o]
    return redact(o)


def say(*parts, err=False):
    msg = " ".join(str(p) for p in parts)
    with _print_lock:
        print(redact(msg), file=sys.stderr if err else sys.stdout, flush=True)


def now_iso() -> str:
    return dt.datetime.now(pc.MSK).isoformat(timespec="seconds")


def jdump(o, indent=1) -> str:
    return json.dumps(o, ensure_ascii=False, indent=indent)


def short_b64(obj):
    """Копия тела запроса для печати/паспорта: base64 заменён описанием (длина, sha256)."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == "data" and isinstance(v, str) and (v.startswith("data:") or len(v) > 512) and obj.get("type") == "base64":
                raw = v.split(",", 1)[1] if v.startswith("data:") else v
                out[k] = f"<base64 {len(raw)} симв., sha256 {hashlib.sha256(raw.encode()).hexdigest()[:16]}…>"
            else:
                out[k] = short_b64(v)
        return out
    if isinstance(obj, list):
        return [short_b64(x) for x in obj]
    return obj


# ---------------------------------------------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------------------------------------------

class ApiError(Exception):
    def __init__(self, status, code, message, body=None, headers=None, ambiguous=False):
        super().__init__(f"HTTP {status} {code}: {message}")
        self.status, self.code, self.message, self.body, self.headers = status, code, message, body, headers or {}
        self.ambiguous = ambiguous   # запрос мог быть принят сервером (сетевой сбой после отправки)


class Resp:
    def __init__(self, status, headers, body: bytes):
        self.status, self.headers, self.body = status, {k.lower(): v for k, v in headers.items()}, body
        try:
            self.json = json.loads(body.decode("utf-8")) if body else None
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.json = None


class Http:
    def __init__(self, base_url: str, key: str | None, live: bool, timeout: float = 60, curl: bool = False):
        self.base = base_url.rstrip("/")
        self.key, self.live, self.timeout, self.curl = key, live, timeout, curl

    def url(self, path: str) -> str:
        return self.base + path

    def show(self, method, path, body=None, ctype="application/json", note=None):
        say(f"{method} {self.url(path)}")
        say("Authorization: Bearer $POLZA_API_KEY" + ("" if self.key else "   # ключ не найден (для --live нужен)"))
        if body is not None:
            say(f"Content-Type: {ctype}")
            say("")
            say(jdump(short_b64(body)) if isinstance(body, (dict, list)) else body)
        if note:
            say(note)
        if self.curl and isinstance(body, (dict, list)):
            say("\n# то же через curl (ключ из переменной окружения):")
            say(f"curl -sS -X {method} '{self.url(path)}' -H \"Authorization: Bearer $POLZA_API_KEY\" "
                f"-H 'Content-Type: application/json' --data @- <<'JSON'\n{jdump(short_b64(body), None)}\nJSON")

    def request(self, method: str, path: str, *, body=None, raw: bytes | None = None, ctype="application/json",
                timeout=None, retries=None, retry_post=False) -> Resp:
        if not self.live:
            raise RuntimeError("сеть без --live запрещена")
        if not self.key:
            raise ApiError(0, "NO_KEY", "ключ не найден: POLZA_API_KEY или ~/.config/polza/api_key")
        data = raw if raw is not None else (json.dumps(body, ensure_ascii=False).encode() if body is not None else None)
        headers = {"Authorization": f"Bearer {self.key}", "Accept": "application/json", "User-Agent": VERSION}
        if data is not None:
            headers["Content-Type"] = ctype
        is_get = method == "GET"
        n_try = retries if retries is not None else (5 if is_get else 3)
        delay = 2.0
        for attempt in range(1, n_try + 1):
            req = urllib.request.Request(self.url(path), data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r:
                    resp = Resp(r.status, dict(r.headers.items()), r.read())
                self._ratelimit_pause(resp.headers)
                return resp
            except urllib.error.HTTPError as e:
                resp = Resp(e.code, dict(e.headers.items()), e.read())
                err = (resp.json or {}).get("error") if isinstance(resp.json, dict) else None
                code = (err or {}).get("code") or f"HTTP_{e.code}"
                msg = (err or {}).get("message") or resp.body[:300].decode("utf-8", "replace")
                retryable = e.code == 429 or (is_get and e.code in (500, 502, 503, 504)) or (retry_post and e.code == 503)
                if retryable and attempt < n_try:
                    wait = self._retry_after(resp.headers, delay)
                    say(f"  … {e.code} {code}: повтор через {wait:.1f} с (попытка {attempt + 1}/{n_try})", err=True)
                    time.sleep(wait)
                    delay = min(delay * 2, 30)
                    continue
                raise ApiError(e.code, code, msg, resp.json if resp.json is not None else resp.body[:2000], resp.headers)
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
                if is_get and attempt < n_try:
                    say(f"  … сеть: {e}; повтор через {delay:.0f} с", err=True)
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
                    continue
                # POST: запрос мог дойти до сервера — повторять нельзя (двойное списание)
                raise ApiError(0, "NETWORK", str(e), ambiguous=not is_get)
        raise ApiError(0, "RETRIES", "исчерпаны попытки")

    @staticmethod
    def _retry_after(h: dict, fallback: float) -> float:
        for k in ("retry-after", "x-ratelimit-reset"):
            v = h.get(k)
            if v:
                try:
                    return max(0.5, min(float(v), 60.0))
                except ValueError:
                    pass
        return fallback

    @staticmethod
    def _ratelimit_pause(h: dict):
        rem, reset = h.get("x-ratelimit-remaining"), h.get("x-ratelimit-reset")
        try:
            if rem is not None and int(rem) <= 0 and reset:
                time.sleep(min(float(reset), 10))
        except ValueError:
            pass

    def download(self, url: str, dest: Path, timeout: float = 300, tries: int = 3) -> dict:
        """Скачивание результата (URL CDN polza — без ключа). Атомарная запись, sha256."""
        last = None
        for attempt in range(1, tries + 1):
            tmp = dest.with_suffix(dest.suffix + ".part")
            h = hashlib.sha256()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": VERSION})
                with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as f:
                    ctype = r.headers.get("Content-Type", "")
                    n = 0
                    while True:
                        chunk = r.read(1 << 16)
                        if not chunk:
                            break
                        f.write(chunk)
                        h.update(chunk)
                        n += len(chunk)
                tmp.replace(dest)
                return {"path": str(dest), "url": url, "bytes": n, "sha256": h.hexdigest(), "content_type": ctype}
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}"
                if e.code in (403, 404, 410):
                    break            # истёк срок хранения или нет файла — повтор не поможет
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last = str(e)
            finally:
                if tmp.exists() and not dest.exists():
                    tmp.unlink(missing_ok=True)
            time.sleep(2 * attempt)
        raise ApiError(0, "DOWNLOAD", f"не удалось скачать {url}: {last}")


def multipart(fields: dict, files: dict) -> tuple[bytes, str]:
    boundary = "----polza" + uuid.uuid4().hex
    out = bytearray()
    for k, v in fields.items():
        out += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    for k, (fname, data, mime) in files.items():
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fname}\"\r\n"
                f"Content-Type: {mime}\r\n\r\n").encode()
        out += data + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


# ---------------------------------------------------------------------------------------------------------------
# Журнал затрат (append-only JSONL, события по uid)
# ---------------------------------------------------------------------------------------------------------------

class Ledger:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()

    def append(self, ev: dict):
        ev = {"ts": now_iso(), **ev}
        line = json.dumps(redact_obj(ev), ensure_ascii=False) + "\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, open(self.path, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(line)
            f.flush()
            fcntl.flock(f, fcntl.LOCK_UN)

    def events(self) -> list[dict]:
        if not self.path.exists():
            return []
        out = []
        for ln in self.path.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except json.JSONDecodeError:
                    pass
        return out

    def jobs(self) -> dict:
        """uid → сводка: последнее состояние, id, стоимость (факт или резерв по оценке)."""
        js = {}
        for e in self.events():
            uid = e.get("uid")
            if not uid:
                continue
            j = js.setdefault(uid, {"uid": uid, "events": 0})
            j["events"] += 1
            for k in ("agent", "tag", "model", "base_url", "request_hash", "estimate_rub", "id", "files",
                      "passport", "cost_rub", "operation", "parent_id"):
                if e.get(k) is not None:
                    j[k] = e[k]
            j["state"] = e.get("event")
            j["ts"] = e.get("ts")
        for j in js.values():
            st = j.get("state")
            if st in ("completed",):
                j["spent"] = float(j.get("cost_rub") if j.get("cost_rub") is not None else j.get("estimate_rub") or 0)
            elif st in ("failed", "cancelled"):
                j["spent"] = float(j.get("cost_rub") or 0)
            elif st in ("http_error", "cache_hit", "upload", "rejected"):
                j["spent"] = 0.0
            else:   # submit / created / timeout / unknown — резерв по оценке (консервативно)
                j["spent"] = float(j.get("estimate_rub") or 0)
        return js

    def spent(self, base_url: str, agent: str | None = None) -> float:
        return round(sum(j["spent"] for j in self.jobs().values()
                         if j.get("base_url") == base_url and (agent is None or j.get("agent") == agent)), 6)

    def find_cached(self, request_hash: str, base_url: str):
        for j in reversed(list(self.jobs().values())):
            if j.get("request_hash") == request_hash and j.get("base_url") == base_url and j.get("state") == "completed":
                files = j.get("files") or []
                if files and all(absp(f).exists() for f in files):
                    return j
        return None

    def find_by_id(self, gen_id: str):
        for j in reversed(list(self.jobs().values())):
            if j.get("id") == gen_id:
                return j
        return None


# ---------------------------------------------------------------------------------------------------------------
# Контекст
# ---------------------------------------------------------------------------------------------------------------

class Ctx:
    def __init__(self, a):
        self.a = a
        self.live = bool(getattr(a, "live", False))
        self.base = (a.base_url or os.environ.get("POLZA_BASE_URL") or DEFAULT_BASE).rstrip("/")
        self.key = load_key()
        self.http = Http(self.base, self.key, self.live, timeout=a.http_timeout, curl=a.curl)
        self.snap = pc.Snapshot(a.catalog or os.environ.get("POLZA_CATALOG"), providers_ref="auto")
        self.ledger = Ledger(Path(a.ledger or os.environ.get("POLZA_LEDGER") or DEFAULT_LEDGER))
        self.out_root = Path(a.out or os.environ.get("POLZA_OUT_ROOT") or DEFAULT_OUT_ROOT)
        self.budget_total = float(a.budget_total if a.budget_total is not None else os.environ.get("POLZA_BUDGET_TOTAL", 2000))
        ba = a.budget_agent if a.budget_agent is not None else os.environ.get("POLZA_BUDGET_AGENT")
        self.budget_agent = float(ba) if ba not in (None, "") else None
        self.max_job = float(a.max_job if a.max_job is not None else os.environ.get("POLZA_MAX_JOB", 60))
        self.default_agent = a.agent or os.environ.get("POLZA_AGENT") or "unknown"
        self._preflight_done = False
        self._budget_lock = threading.Lock()
        self.stop = threading.Event()

    def model(self, mid: str) -> dict:
        m = self.snap.by_id.get(mid)
        if m is None:
            near = [x for x in self.snap.by_id if mid.split("/")[-1][:5] in x][:8]
            raise SystemExit(f"модели {mid!r} нет в снимке {self.snap.dir.name}" + (f"; похожие: {near}" if near else ""))
        return m


# ---------------------------------------------------------------------------------------------------------------
# Подготовка задания
# ---------------------------------------------------------------------------------------------------------------

def load_jobs(path: str) -> list[dict]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix == ".jsonl":
        jobs = []
        for i, ln in enumerate(text.splitlines(), 1):
            s = ln.strip()
            if not s or s.startswith("#") or s.startswith("//"):
                continue
            try:
                jobs.append(json.loads(s))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{i}: не JSON: {e}")
        return jobs
    obj = json.loads(text)
    return obj if isinstance(obj, list) else [obj]


def ffprobe(path: Path) -> dict | None:
    if not shutil.which("ffprobe"):
        return None
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams",
                            str(path)], capture_output=True, text=True, timeout=30)
        d = json.loads(r.stdout or "{}")
    except (subprocess.SubprocessError, json.JSONDecodeError):
        return None
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a_ = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    fps = None
    if v.get("avg_frame_rate") and v["avg_frame_rate"] != "0/0":
        n, _, dd = v["avg_frame_rate"].partition("/")
        fps = round(float(n) / float(dd or 1), 3)
    dur = d.get("format", {}).get("duration")
    return {"duration_s": round(float(dur), 3) if dur else None, "width": v.get("width"), "height": v.get("height"),
            "codec": v.get("codec_name"), "fps": fps, "has_audio": a_ is not None}


def image_info(path: Path) -> dict | None:
    try:
        from PIL import Image  # системный Pillow 11.3 (необязателен)
        with Image.open(path) as im:
            return {"width": im.width, "height": im.height, "mode": im.mode, "format": im.format,
                    "has_alpha": im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info}
    except Exception:  # noqa: BLE001
        return None


class Prepared:
    """Задание после проверки: тело запроса, оценка, хэш, файлы к загрузке."""

    def __init__(self):
        self.job = {}
        self.model = None
        self.provider = None
        self.body = {}
        self.estimate = {}
        self.issues = []
        self.notes = []
        self.filled = []
        self.missing = []
        self.uploads = []          # (json-путь в input, локальный путь) — загрузить в хранилище перед отправкой
        self.request_hash = ""
        self.ref_seconds = None
        self.uid = uuid.uuid4().hex[:12]
        self.agent = "unknown"
        self.tag = "job"

    @property
    def errors(self):
        return [i for i in self.issues if i["level"] == "error"]


def resolve_file_item(item, key: str, idx: int, prep: Prepared, allow_upload=True):
    """URL/data:/путь/объект → MediaFileDto. Для хэша — sha256 содержимого локального файла."""
    if isinstance(item, dict):
        return item, {"type": item.get("type"), "data": (item.get("data") if item.get("type") == "url"
                                                          else hashlib.sha256(str(item.get("data")).encode()).hexdigest())}
    s = str(item)
    if s.startswith(("http://", "https://")):
        return {"type": "url", "data": s}, {"type": "url", "data": s}
    if s.startswith("data:"):
        raw = s.split(",", 1)[1] if "," in s else s
        return {"type": "base64", "data": s}, {"type": "base64", "sha256": hashlib.sha256(raw.encode()).hexdigest()}
    p = Path(s).expanduser()
    if not p.is_absolute():
        base = Path(prep.job.get("_dir", "."))
        p = (base / p) if (base / p).exists() else p
    if not p.exists():
        prep.issues.append({"level": "error", "param": f"{key}[{idx}]", "msg": f"файл не найден: {s}"})
        return {"type": "url", "data": s}, {"missing": s}
    data = p.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    if key == "videos":
        info = ffprobe(p)
        if info and info.get("duration_s"):
            prep.ref_seconds = (prep.ref_seconds or 0) + info["duration_s"]
    if len(data) <= INLINE_MAX:
        b64 = base64.b64encode(data).decode()
        return {"type": "base64", "data": f"data:{mime};base64,{b64}"}, {"type": "file", "sha256": digest}
    if not allow_upload:
        prep.issues.append({"level": "error", "param": f"{key}[{idx}]", "msg": "файл > 4 МБ и загрузка недоступна"})
    prep.uploads.append((key, idx, str(p)))
    return {"type": "url", "data": f"<будет загружен в хранилище polza: {p.name}, {len(data)} байт>"}, \
        {"type": "file", "sha256": digest}


def prepare(ctx: Ctx, job: dict, *, fill=True, allow_unknown=False, raw=False) -> Prepared:
    prep = Prepared()
    prep.job = job
    prep.agent = str(job.get("agent") or ctx.default_agent)
    prep.tag = re.sub(r"[^\w.-]+", "-", str(job.get("tag") or "job"))[:60]
    if not job.get("model"):
        prep.issues.append({"level": "error", "param": "model", "msg": "не задан model"})
        return prep
    m = ctx.model(job["model"])
    prep.model = m
    inp = dict(job.get("input") or {})
    prov = job.get("provider") or None
    pname = None
    if isinstance(prov, dict):
        only = prov.get("only") or []
        order = prov.get("order") or []
        pname = only[0] if len(only) == 1 else (order[0] if order else None)
        if len(only) > 1:
            prep.notes.append(f"provider.only из {len(only)} — цена оценена по первому в order или по top_provider")
        if pname and prov.get("allow_fallbacks") is not False:
            prep.notes.append("provider задан, но allow_fallbacks не false — polza может уйти к другому провайдеру "
                              "с другой ценой; для точной цены ставьте \"allow_fallbacks\": false")
    try:
        name, pr, params = pc.provider_view(m, pname, ctx.snap.providers.get(m["id"]))
    except KeyError as e:
        prep.issues.append({"level": "error", "param": "provider", "msg": str(e)})
        return prep
    prep.provider = name
    if pname and name != (m.get("top_provider") or {}).get("name"):
        prep.notes.append(f"провайдер {name}: параметры и цена этого провайдера (не top_provider)")
    # файлы
    hash_files = {}
    for key in ("images", "videos"):
        if key in inp and isinstance(inp[key], list) and not raw:
            conv, hv = [], []
            for i, it in enumerate(inp[key]):
                c, h = resolve_file_item(it, key, i, prep)
                conv.append(c)
                hv.append(h)
            inp[key] = conv
            hash_files[key] = hv
    # поля-ссылки (строка URL): локальный файл → /v1/storage/upload → URL; путь — относительно файла задания, как у images
    # (оркестратор, 23.09.2026 19:10: раньше mask_url искался от текущей папки — из корня проекта путь уходил в API строкой;
    # first_frame_url / last_frame_url — поля GA google/gemini-omni-1.1-flash, снимок 2026-09-23_1745)
    for ukey in URL_FILE_KEYS:
        v = inp.get(ukey)
        if not isinstance(v, str) or raw or v.startswith(("http://", "https://", "data:")):
            continue
        p = Path(v).expanduser()
        if not p.is_absolute():
            base = Path(job.get("_dir", "."))
            p = (base / p) if (base / p).exists() else p
        if p.exists():
            prep.uploads.append((ukey, None, str(p)))
            hash_files[ukey] = {"type": "file", "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            inp[ukey] = f"<будет загружен в хранилище polza: {p.name}>"
        else:
            prep.issues.append({"level": "error", "param": ukey,
                                "msg": f"файл не найден: {v} (поле ждёт URL: локальный файл загружается в хранилище)"})
    if not raw:
        inp, prep.notes_coerce = pc.coerce_input(params, inp)
        prep.notes += prep.notes_coerce
        if fill:
            inp, prep.filled, prep.missing = pc.fill_defaults(m, inp, params, pr)
        # модели без prompt в каталоге (Topaz): Media API требует prompt (OpenAPI), гайд topaz-upscale шлёт ""
        if "prompt" not in params and "prompt" not in inp:
            inp["prompt"] = ""
            prep.notes.append("prompt: \"\" добавлен (у модели нет prompt в каталоге; так в гайде topaz-upscale.mdx)")
    meta = job.get("meta") or {}
    if meta.get("ref_video_seconds") is not None:
        prep.ref_seconds = float(meta["ref_video_seconds"])
    prep.issues += pc.validate(m, inp, provider=pname, providers=ctx.snap.providers.get(m["id"]),
                               strict=not allow_unknown, ref_seconds=prep.ref_seconds)
    for k in prep.missing:
        prep.issues.append({"level": "error", "param": k, "msg": "ценовой/обязательный параметр без default в каталоге — "
                                                                 "задайте явно (иначе polza может взять запасную ступень)"})
    for k in prep.filled:
        lvl = "warn" if k in ("duration", "generate_audio", "sound", "resolution", "mode") else "info"
        prep.issues.append({"level": lvl, "param": k, "msg": f"подставлено из default каталога: {inp.get(k)!r}"})
    prep.estimate = pc.estimate(m, inp, provider=pname, providers=ctx.snap.providers.get(m["id"]),
                                ref_seconds=prep.ref_seconds)
    if not fill and not raw:
        # ценовые параметры не переданы явно: polza может взять default каталога или запасную ступень [] —
        # для бюджета считаем худший случай
        implicit = [k for k, src in (prep.estimate.get("sources") or {}).items() if str(src).startswith("default")]
        fb = prep.estimate.get("fallback_rub")
        if implicit and fb is not None:
            units = prep.estimate.get("units")
            fb_total = fb * units if prep.estimate.get("unit_param") and isinstance(units, (int, float)) else fb
            prep.estimate["rub_high"] = max(prep.estimate.get("rub_high") or 0, fb_total)
            prep.issues.append({"level": "warn", "param": ",".join(implicit),
                                "msg": f"не передано явно (--no-fill): polza возьмёт default каталога или запасную "
                                       f"ступень [] — худший случай {pc.fmt_rub(fb_total)} ₽ учтён в лимитах"})
    body = {"model": m["id"], "input": inp, "async": True}
    if prov:
        body["provider"] = prov
    if job.get("user"):
        body["user"] = job["user"]
    prep.body = body
    hinp = {k: (hash_files[k] if k in hash_files else v) for k, v in inp.items()}
    canon = {"model": m["id"], "input": hinp, "provider": prov, "variant": job.get("variant")}
    prep.request_hash = hashlib.sha256(json.dumps(canon, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return prep


def media_kind(m: dict) -> str:
    return "video" if m.get("type") == "video" else "image"


# ---------------------------------------------------------------------------------------------------------------
# Бюджет и предполётная проверка
# ---------------------------------------------------------------------------------------------------------------

def price_for_limits(prep: Prepared):
    e = prep.estimate
    return e.get("rub_high") if e.get("rub_high") is not None else e.get("rub")


def budget_check(ctx: Ctx, prep: Prepared, extra_reserved: float = 0.0) -> tuple[bool, str]:
    rub = price_for_limits(prep)
    if rub is None:
        if ctx.a.allow_unknown_price:
            return True, "цена неизвестна (разрешено --allow-unknown-price)"
        return False, "цена по каталогу неизвестна — уточните параметры (meta.ref_video_seconds) или --allow-unknown-price"
    cap = min(ctx.max_job, float(prep.job.get("max_rub"))) if prep.job.get("max_rub") is not None else ctx.max_job
    if rub > cap + 1e-9:
        return False, f"оценка {pc.fmt_rub(rub)} ₽ > лимита на задание {pc.fmt_rub(cap)} ₽ (--max-job / max_rub)"
    spent = ctx.ledger.spent(ctx.base) + extra_reserved
    if spent + rub > ctx.budget_total + 1e-9:
        return False, (f"общий бюджет: потрачено/зарезервировано {pc.fmt_rub(spent)} ₽ + {pc.fmt_rub(rub)} ₽ > "
                       f"{pc.fmt_rub(ctx.budget_total)} ₽")
    if ctx.budget_agent is not None:
        sa = ctx.ledger.spent(ctx.base, prep.agent)
        if sa + rub > ctx.budget_agent + 1e-9:
            return False, (f"бюджет агента {prep.agent}: {pc.fmt_rub(sa)} ₽ + {pc.fmt_rub(rub)} ₽ > "
                           f"{pc.fmt_rub(ctx.budget_agent)} ₽")
    return True, (f"бюджет: {pc.fmt_rub(spent)} из {pc.fmt_rub(ctx.budget_total)} ₽ потрачено/в резерве; после задания "
                  f"останется {pc.fmt_rub(ctx.budget_total - spent - rub)} ₽")


def preflight(ctx: Ctx, need_rub: float | None):
    """GET /v2/balance и /v1/key: хватит ли денег и лимита ключа. Один раз на процесс."""
    if ctx._preflight_done or ctx.a.no_preflight:
        return
    ctx._preflight_done = True
    try:
        b = ctx.http.request("GET", "/v2/balance").json or {}
        avail = pc.to_num(b.get("available"))
        say(f"  баланс: available {b.get('available')} ₽, amount {b.get('amount')} ₽, резерв {b.get('reservedAmount')}")
        if need_rub is not None and avail is not None and avail < need_rub:
            say(f"  ОТКАЗ: недостаточно средств — available {avail} ₽ < {need_rub} ₽", err=True)
            raise SystemExit(EXIT_BUDGET)
    except ApiError as e:
        say(f"  ! /v2/balance: {e}", err=True)
        if e.status in (401, 403):
            raise SystemExit(EXIT_HTTP)
    try:
        k = ctx.http.request("GET", "/v1/key").json or {}
        say(f"  ключ {k.get('label')}: лимит {k.get('limit')} ({k.get('limit_reset')}), остаток {k.get('limit_remaining')}, "
            f"потрачено сегодня {k.get('usage_daily')}")
        rem = pc.to_num(k.get("limit_remaining"))
        if need_rub is not None and rem is not None and rem < need_rub:
            say(f"  ОТКАЗ: остаток лимита ключа {rem} ₽ < {need_rub} ₽", err=True)
            raise SystemExit(EXIT_BUDGET)
    except ApiError as e:
        say(f"  ! /v1/key: {e}", err=True)


# ---------------------------------------------------------------------------------------------------------------
# Результат: URL, скачивание, паспорт
# ---------------------------------------------------------------------------------------------------------------

URL_KEYS = ("url", "video_url", "image_url", "file_url", "audio_url")
URL_FILE_KEYS = ("mask_url", "first_frame_url", "last_frame_url")   # поля input со ссылкой на файл (загрузка перед отправкой)
THUMB_KEYS = ("thumbnail_url", "cover_url", "poster_url", "preview_url")


def extract_urls(st: dict) -> tuple[list[str], list[str]]:
    """URL результата из ответа статуса: data.url (status.mdx), data[].url (Lyria), output.url (гайд NB2), urls[]."""
    urls, thumbs = [], []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in URL_KEYS and isinstance(v, str) and v.startswith(("http://", "https://")):
                    urls.append(v)
                elif k in THUMB_KEYS and isinstance(v, str):
                    thumbs.append(v)
                elif k == "urls" and isinstance(v, list):
                    urls.extend(u for u in v if isinstance(u, str))
                else:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and x.startswith(("http://", "https://")):
            urls.append(x)

    for key in ("data", "output", "result", "results"):
        if key in (st or {}):
            walk(st[key])
    seen, uniq = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq, thumbs


EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif", "image/avif": ".avif",
       "video/mp4": ".mp4", "video/webm": ".webm", "video/quicktime": ".mov", "audio/mpeg": ".mp3", "audio/wav": ".wav"}


def out_dir_for(ctx: Ctx, prep_or_job) -> Path:
    job = prep_or_job.job if isinstance(prep_or_job, Prepared) else (prep_or_job or {})
    agent = (prep_or_job.agent if isinstance(prep_or_job, Prepared) else job.get("agent")) or ctx.default_agent
    d = Path(job["out_dir"]) if job.get("out_dir") else ctx.out_root / str(agent) / dt.date.today().isoformat()
    if not d.is_absolute():
        d = ROOT / d
    d.mkdir(parents=True, exist_ok=True)
    return d


def rel(p) -> str:
    """Путь относительно корня проекта (если внутри него) — журнал и паспорта переносимы."""
    p = Path(p)
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def absp(p) -> Path:
    p = Path(p)
    return p if p.is_absolute() else ROOT / p


def slug(s: str) -> str:
    return re.sub(r"[^\w.-]+", "-", s).strip("-")[:60]


def fetch_results(ctx: Ctx, st: dict, prep_like, gen_id: str, model_id: str) -> list[dict]:
    urls, _ = extract_urls(st)
    if not urls:
        raise ApiError(0, "NO_URL", "в ответе completed нет URL результата (data/output)")
    d = out_dir_for(ctx, prep_like)
    tag = prep_like.tag if isinstance(prep_like, Prepared) else slug(str((prep_like or {}).get("tag") or "job"))
    files = []
    for i, u in enumerate(urls):
        ext = Path(urllib.parse.urlparse(u).path).suffix.lower() or ".bin"
        base = f"{tag}__{slug(model_id)}__{slug(gen_id)}" + (f"_{i + 1}" if len(urls) > 1 else "")
        dest = d / (base + ext)
        info = ctx.http.download(u, dest)
        ct = (info.get("content_type") or "").split(";")[0].strip()
        if ct in EXT and dest.suffix != EXT[ct] and dest.suffix in (".bin", ""):
            new = dest.with_suffix(EXT[ct])
            dest.replace(new)
            info["path"] = str(new)
            dest = new
        media = image_info(dest) if ct.startswith("image/") or dest.suffix in (".png", ".jpg", ".jpeg", ".webp") else None
        if media is None and (ct.startswith("video/") or dest.suffix in (".mp4", ".webm", ".mov")):
            media = ffprobe(dest)
        info["media"] = media
        info["path"] = rel(dest)
        files.append(info)
        say(f"  ↓ {dest}  ({info['bytes']} байт, sha256 {info['sha256'][:16]}…)")
    return files


def write_passport(files: list[dict], passport: dict) -> str:
    """Паспорт рядом с файлом: <тег>__<модель>__<id>.passport.json (для нескольких файлов — без суффикса _N)."""
    first = absp(files[0]["path"])
    stem = re.sub(r"_\d+$", "", first.stem) if len(files) > 1 else first.stem
    path = first.with_name(stem + ".passport.json")
    path.write_text(jdump(redact_obj(passport)))
    return rel(path)


def usage_cost(st: dict):
    u = (st or {}).get("usage") or {}
    v = u.get("cost_rub", u.get("cost"))
    return float(v) if isinstance(v, (int, float)) else pc.to_num(v)


def get_history(ctx: Ctx, gen_id: str):
    if ctx.a.no_history:
        return None
    try:
        return ctx.http.request("GET", f"/v1/history/generations/{gen_id}", retries=2).json
    except ApiError as e:
        return {"_error": str(e)}


# ---------------------------------------------------------------------------------------------------------------
# Живой цикл
# ---------------------------------------------------------------------------------------------------------------

def poll(ctx: Ctx, gen_id: str, kind: str, label: str):
    interval = ctx.a.poll_interval or (4.0 if kind == "image" else 8.0)     # docs: 3–5 с картинки, 5–10 с видео
    max_wait = ctx.a.max_wait or (600.0 if kind == "image" else 1800.0)
    t0, n, last = time.time(), 0, None
    st = {}
    while True:
        st = ctx.http.request("GET", f"/v1/media/{gen_id}").json or {}
        n += 1
        s = st.get("status")
        if s != last:
            say(f"  [{label}] {time.time() - t0:6.1f} с  {s}")
            last = s
        if s in TERMINAL:
            return st, n, time.time() - t0
        if time.time() - t0 > max_wait:
            return st, n, time.time() - t0
        time.sleep(interval * random.uniform(0.85, 1.15))


def upload_file(ctx: Ctx, path: str, permanent=False, external_user_id=None) -> dict:
    p = Path(path)
    data = p.read_bytes()
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    fields = {"storagePolicy": "PERMANENT" if permanent else "TEMP_UPLOAD"}
    if external_user_id:
        fields["externalUserId"] = external_user_id
    body, ctype = multipart(fields, {"file": (p.name, data, mime)})
    r = ctx.http.request("POST", "/v1/storage/upload", raw=body, ctype=ctype, timeout=max(ctx.a.http_timeout, 120),
                         retries=2)
    return r.json or {}


def run_prepared(ctx: Ctx, prep: Prepared, *, force=False, batch_reserved=None) -> int:
    """Живой прогон подготовленного задания. Возвращает код выхода."""
    m = prep.model
    label = f"{prep.tag}·{m['id']}"
    if not force:
        hit = ctx.ledger.find_cached(prep.request_hash, ctx.base)
        if hit:
            ctx.ledger.append({"event": "cache_hit", "uid": prep.uid, "agent": prep.agent, "tag": prep.tag,
                               "model": m["id"], "base_url": ctx.base, "request_hash": prep.request_hash,
                               "source_uid": hit["uid"], "id": hit.get("id"), "files": hit.get("files")})
            say(f"  [{label}] кэш: тот же запрос уже выполнен ({hit.get('id')}), файлы: {hit.get('files')} — "
                f"0 ₽ (повтор — --force или другой variant)")
            return EXIT_OK
    with ctx._budget_lock:
        ok, msg = budget_check(ctx, prep, extra_reserved=0.0)
        if not ok:
            say(f"  [{label}] ОТКАЗ: {msg}", err=True)
            return EXIT_BUDGET
        rub = price_for_limits(prep)
        ctx.ledger.append({"event": "submit", "uid": prep.uid, "agent": prep.agent, "tag": prep.tag, "model": m["id"],
                           "provider": prep.provider, "provider_req": prep.job.get("provider"), "base_url": ctx.base,
                           "request_hash": prep.request_hash, "estimate_rub": rub, "notes": prep.job.get("notes")})
    # загрузка крупных локальных файлов в хранилище (TEMP_UPLOAD, 24 ч)
    uploaded = {}              # один файл в нескольких полях (петля [A,A]: first_frame_url = last_frame_url) — одна загрузка
    for key, idx, path in prep.uploads:
        up = uploaded.get(path)
        if up is None:
            up = uploaded[path] = upload_file(ctx, path)
            ctx.ledger.append({"event": "upload", "uid": "upl_" + uuid.uuid4().hex[:10], "agent": prep.agent,
                               "base_url": ctx.base, "file_id": up.get("id"), "url": up.get("url"), "src": path})
        if key in URL_FILE_KEYS:
            prep.body["input"][key] = up.get("url")
        else:
            prep.body["input"][key][idx] = {"type": "url", "data": up.get("url")}
        say(f"  [{label}] загружен {path} → {up.get('url')} (до {up.get('expiresAt')})")
    t_submit = time.time()
    submitted_at = now_iso()
    try:
        r = ctx.http.request("POST", "/v1/media", body=prep.body, retries=3)
    except ApiError as e:
        ev = "unknown" if e.ambiguous else "http_error"
        ctx.ledger.append({"event": ev, "uid": prep.uid, "base_url": ctx.base, "http_status": e.status,
                           "code": e.code, "message": e.message, "body": e.body if isinstance(e.body, dict) else None})
        say(f"  [{label}] ОШИБКА создания: {e}" + ("  — запрос мог быть принят: проверьте history, резерв оставлен в "
                                                   "журнале" if e.ambiguous else ""), err=True)
        if e.status in (401, 402, 403):
            ctx.stop.set()
        if e.status == 400 and isinstance(e.body, dict):
            say(jdump(e.body), err=True)
        return EXIT_HTTP
    created = r.json or {}
    gen_id = created.get("id")
    ctx.ledger.append({"event": "created", "uid": prep.uid, "id": gen_id, "status": created.get("status"),
                       "base_url": ctx.base})
    say(f"  [{label}] создано {gen_id} ({created.get('status')}), оценка {pc.fmt_rub(rub)} ₽")
    if created.get("warnings"):
        say(f"  [{label}] предупреждения polza: {created['warnings']}")
    if created.get("status") in TERMINAL:
        st, n, wall = created, 0, time.time() - t_submit
    else:
        st, n, wall = poll(ctx, gen_id, media_kind(m), label)
    status = st.get("status")
    cost = usage_cost(st)
    if status not in TERMINAL:
        ctx.ledger.append({"event": "timeout", "uid": prep.uid, "id": gen_id, "status": status, "base_url": ctx.base})
        say(f"  [{label}] ТАЙМАУТ опроса ({wall:.0f} с, статус {status}). Дожать: polza.py download {gen_id} --live",
            err=True)
        return EXIT_TIMEOUT
    if status != "completed":
        ctx.ledger.append({"event": status, "uid": prep.uid, "id": gen_id, "cost_rub": cost or 0.0,
                           "error": st.get("error"), "base_url": ctx.base})
        say(f"  [{label}] {status.upper()}: {jdump(st.get('error'), None)}; списано {cost or 0} ₽", err=True)
        return EXIT_FAILED
    try:
        files = fetch_results(ctx, st, prep, gen_id, m["id"])
    except ApiError as e:
        ctx.ledger.append({"event": "completed", "uid": prep.uid, "id": gen_id, "cost_rub": cost, "files": [],
                           "download_error": str(e), "base_url": ctx.base})
        say(f"  [{label}] ОШИБКА скачивания: {e}. Результат хранится 7 дней: polza.py download {gen_id} --live",
            err=True)
        return EXIT_DOWNLOAD
    hist = get_history(ctx, gen_id)
    passport = {
        "schema": "polza-passport/1", "client": VERSION, "uid": prep.uid, "request_hash": prep.request_hash,
        "job": {k: prep.job.get(k) for k in ("tag", "agent", "notes", "variant", "model", "provider", "meta")},
        "prompt": prep.body["input"].get("prompt"),
        "seed": prep.body["input"].get("seed", prep.body["input"].get("seeds")),
        "request": {"method": "POST", "url": ctx.http.url("/v1/media"), "body": short_b64(prep.body)},
        "catalog": {"snapshot": ctx.snap.dir.name, "fetched_at": ctx.snap.fetched_at(), "provider": prep.provider,
                    "estimate": prep.estimate, "filled_defaults": prep.filled,
                    "issues": prep.issues},
        "response_create": created, "response_final": st, "history": hist,
        "provider_actual": (hist or {}).get("provider") or (hist or {}).get("finalEndpointSlug"),
        "timing": {"submitted_at": submitted_at, "completed_at": now_iso(), "wall_s": round(time.time() - t_submit, 2),
                   "polls": n},
        "cost": {"usage_cost_rub": cost, "estimate_rub": prep.estimate.get("rub"),
                 "delta_rub": (round(cost - prep.estimate["rub"], 4) if cost is not None and prep.estimate.get("rub")
                               is not None else None)},
        "files": files, "base_url": ctx.base,
    }
    pp = write_passport(files, passport)
    ctx.ledger.append({"event": "completed", "uid": prep.uid, "id": gen_id, "cost_rub": cost,
                       "estimate_rub": rub, "files": [f["path"] for f in files], "passport": pp, "base_url": ctx.base,
                       "provider_actual": passport["provider_actual"], "wall_s": passport["timing"]["wall_s"]})
    delta = passport["cost"]["delta_rub"]
    say(f"  [{label}] ГОТОВО за {passport['timing']['wall_s']} с; цена {cost} ₽ (оценка {prep.estimate.get('rub')}"
        + (f", разница {delta:+}" if delta else "") + f"); паспорт {pp}")
    return EXIT_OK


# ---------------------------------------------------------------------------------------------------------------
# Печать сухого прогона и оценки
# ---------------------------------------------------------------------------------------------------------------

def print_issues(prep: Prepared):
    for n in prep.notes:
        say(f"#   · {n}")
    for i in prep.issues:
        mark = {"error": "✗", "warn": "!", "info": "·"}[i["level"]]
        say(f"#   {mark} [{i['level']}] {i['param']}: {i['msg']}")


def print_plan(ctx: Ctx, prep: Prepared, show_request=True):
    e = prep.estimate
    m = prep.model
    say(f"# ── {prep.tag} · {m['id']} · провайдер {prep.provider} · агент {prep.agent}")
    if show_request:
        ctx.http.show("POST", "/v1/media", prep.body)
        for key, idx, path in prep.uploads:
            say(f"# перед отправкой: POST {ctx.http.url('/v1/storage/upload')} (multipart, TEMP_UPLOAD) ← {path}")
    rng = ""
    if e.get("rub_low") is not None and e.get("rub_high") is not None and e["rub_low"] != e["rub_high"]:
        rng = f" (диапазон {pc.fmt_rub(e['rub_low'])}–{pc.fmt_rub(e['rub_high'])} ₽)"
    say(f"# Оценка: {pc.fmt_rub(e.get('rub'))} ₽{rng} — {e.get('formula') or e.get('kind')}")
    for w in e.get("warnings") or []:
        say(f"#   ! цена: {w}")
    print_issues(prep)
    ok, msg = budget_check(ctx, prep)
    say(f"# {'Бюджет OK' if ok else 'ОТКАЗ'}: {msg}")
    hit = ctx.ledger.find_cached(prep.request_hash, ctx.base)
    say(f"# Кэш: {'есть — ' + str(hit.get('files')) if hit else 'нет'} (хэш {prep.request_hash[:16]}…)")


# ---------------------------------------------------------------------------------------------------------------
# Команды
# ---------------------------------------------------------------------------------------------------------------

def cmd_models(ctx: Ctx, a):
    if a.fresh:
        # бесплатный публичный GET (без ключа) — разрешён и в сухом режиме
        st, _, body = pc.http_get(f"{ctx.base}/v1/models" + (f"?type={a.type}" if a.type else ""))
        models = json.loads(body)["data"]
        say(f"# свежий GET {ctx.base}/v1/models — {st}, {len(models)} моделей")
    else:
        models = ctx.snap.models
        say(f"# снимок {ctx.snap.dir.name} ({ctx.snap.fetched_at()})")
    rows = []
    for m in models:
        if a.type and m.get("type") != a.type:
            continue
        if not a.type and m.get("type") not in pc.MEDIA_TYPES:
            continue
        if a.search and a.search.lower() not in (m["id"] + " " + (m.get("name") or "")).lower():
            continue
        n = pc.normalize_model(m)
        rows.append((m.get("type"), m["id"], n["provider"], pc._price_cell(n), n["created"]))
    rows.sort(key=lambda r: (r[0], r[1]))
    for t, i, p, price, c in rows:
        say(f"{t:5}  {i:42}  {p:22}  {price}  (с {c})")
    say(f"# всего {len(rows)}")


def cmd_show(ctx: Ctx, a):
    m = ctx.model(a.model)
    n = pc.normalize_model(m, ctx.snap.providers.get(m["id"]))
    if a.json:
        say(jdump(n))
        return
    say(f"{m['id']} — {m.get('name')} · {m.get('type')} · провайдер {n['provider']} · добавлена {n['created']}")
    say(f"флаги: 152-ФЗ {n['flags']['fz152']}, данные в РФ {n['flags']['data_in_russia']}, "
        f"на инфраструктуре polza {n['flags']['hosted_on_polza']}, модерация {n['flags']['moderated']}")
    name, pr, params = pc.provider_view(m, a.provider, ctx.snap.providers.get(m["id"]))
    say(f"\nпараметры ({name}):")
    for k, spec in params.items():
        say(f"  {k:24} {pc._ptype(spec, k):12} {pc._vals(spec)}" + ("  ОБЯЗ." if spec.get("required") else "")
            + (f"  max_length {spec['max_length']}" if spec.get("max_length") else "")
            + (f"  — {spec['description']}" if spec.get("description") else ""))
    say(f"\nцена: {pc._price_cell(n)}; ценовые параметры: {n['pricing']['price_params']}")
    for r in pc.price_grid(m, provider=a.provider, providers=ctx.snap.providers.get(m["id"])):
        say(f"  {jdump(r['input'], None):60} → {pc.fmt_rub(r['rub'])} ₽   {r['formula']}")
    if n["operations"]:
        say("\nоперации:")
        for o in n["operations"]:
            say(f"  {o['id']:14} async={o['async']}  {pc.fmt_rub(o['rub'])} ₽  параметры: {list((o['params'] or {}).keys())}")
    if n.get("providers"):
        say("\nпровайдеры:")
        for p in n["providers"]:
            ex = p.get("example_rub_by_resolution")
            say(f"  {p['name']:30} {'TOP ' if p['is_top'] else '    '}{p['pricing_kind']:15}"
                + (f" пример 1K/2K/4K: {ex}" if ex else "") + ("  параметры отличаются" if p["params_differ"] else ""))
    for s in n["notes"] + n["doc_vs_catalog"]:
        say(f"  ! {s}")


def cmd_estimate(ctx: Ctx, a):
    jobs = load_jobs(a.job)
    total, bad = 0.0, 0
    for j in jobs:
        j.setdefault("_dir", str(Path(a.job).resolve().parent))
        prep = prepare(ctx, j, fill=not a.no_fill, allow_unknown=a.allow_unknown, raw=a.raw)
        if prep.model is None:
            print_issues(prep)
            bad += 1
            continue
        print_plan(ctx, prep, show_request=a.verbose)
        bad += bool(prep.errors)
        total += price_for_limits(prep) or 0
        say("")
    say(f"# ИТОГО: заданий {len(jobs)}, с ошибками {bad}, оценка суммы {pc.fmt_rub(total)} ₽ "
        f"(потрачено {pc.fmt_rub(ctx.ledger.spent(ctx.base))} из {pc.fmt_rub(ctx.budget_total)} ₽)")
    return EXIT_JOB if bad else EXIT_OK


def _single_job(ctx, a, j):
    j.setdefault("_dir", str(Path(a.job).resolve().parent) if getattr(a, "job", None) else ".")
    prep = prepare(ctx, j, fill=not a.no_fill, allow_unknown=a.allow_unknown, raw=a.raw)
    return prep


def cmd_run(ctx: Ctx, a):
    jobs = load_jobs(a.job)
    if len(jobs) != 1:
        raise SystemExit("run принимает одно задание; для нескольких — batch")
    prep = _single_job(ctx, a, jobs[0])
    if prep.model is None:
        print_issues(prep)
        return EXIT_JOB
    if not ctx.live:
        say("# СУХОЙ ПРОГОН — ничего не отправлено (для реального вызова добавьте --live)")
        print_plan(ctx, prep)
        if prep.errors:
            return EXIT_JOB
        return EXIT_OK if budget_check(ctx, prep)[0] else EXIT_BUDGET
    if prep.errors and not a.no_validate:
        print_plan(ctx, prep, show_request=False)
        say("# ОТКАЗ: ошибки проверки по каталогу (обойти: --no-validate)", err=True)
        return EXIT_JOB
    say(f"# ЖИВОЙ ВЫЗОВ → {ctx.base}")
    print_plan(ctx, prep, show_request=False)
    preflight(ctx, price_for_limits(prep))
    return run_prepared(ctx, prep, force=a.force)


def cmd_batch(ctx: Ctx, a):
    jobs = load_jobs(a.job)
    preps = [_single_job(ctx, a, j) for j in jobs]
    bad = [p for p in preps if p.model is None or (p.errors and not a.no_validate)]
    total = sum(price_for_limits(p) or 0 for p in preps if p.model is not None)
    par = max(1, min(a.parallel, MAX_PARALLEL))
    for p in preps:
        if p.model is not None:
            print_plan(ctx, p, show_request=not ctx.live and a.verbose)
        else:
            print_issues(p)
        say("")
    spent = ctx.ledger.spent(ctx.base)
    say(f"# СЕРИЯ: {len(preps)} заданий, с ошибками {len(bad)}, оценка {pc.fmt_rub(total)} ₽; потрачено "
        f"{pc.fmt_rub(spent)} из {pc.fmt_rub(ctx.budget_total)} ₽; параллельно {par}")
    if bad:
        say("# ОТКАЗ: исправьте ошибки (или --no-validate)", err=True)
        return EXIT_JOB
    if spent + total > ctx.budget_total + 1e-9:
        say(f"# ОТКАЗ: серия {pc.fmt_rub(total)} ₽ не помещается в бюджет", err=True)
        return EXIT_BUDGET
    if not ctx.live:
        say("# СУХОЙ ПРОГОН серии — ничего не отправлено (--live для реального вызова)")
        return EXIT_OK
    preflight(ctx, total)
    codes = []

    def worker(p):
        if ctx.stop.is_set():
            say(f"  [{p.tag}] пропущено: серия остановлена после фатальной ошибки", err=True)
            return EXIT_HTTP
        try:
            return run_prepared(ctx, p, force=a.force)
        except Exception as e:  # noqa: BLE001
            say(f"  [{p.tag}] исключение: {e}", err=True)
            return EXIT_HTTP

    with cf.ThreadPoolExecutor(max_workers=par) as ex:
        codes = list(ex.map(worker, preps))
    say(f"# СЕРИЯ ГОТОВА: коды {codes}; потрачено теперь {pc.fmt_rub(ctx.ledger.spent(ctx.base))} ₽")
    return max(codes) if codes else EXIT_OK


def cmd_status(ctx: Ctx, a):
    if not ctx.live:
        say("# СУХОЙ ПРОГОН (бесплатный GET, но с ключом — только с --live)")
        ctx.http.show("GET", f"/v1/media/{a.id}")
        return EXIT_OK
    st = ctx.http.request("GET", f"/v1/media/{a.id}").json or {}
    say(jdump(redact_obj(st)))
    j = ctx.ledger.find_by_id(a.id)
    if j and st.get("status") in ("failed", "cancelled") and j.get("state") not in TERMINAL:
        ctx.ledger.append({"event": st["status"], "uid": j["uid"], "id": a.id, "cost_rub": usage_cost(st) or 0.0,
                           "error": st.get("error"), "base_url": ctx.base})
    return EXIT_OK


def cmd_download(ctx: Ctx, a):
    if not ctx.live:
        say("# СУХОЙ ПРОГОН")
        ctx.http.show("GET", f"/v1/media/{a.id}", note="# затем скачивание URL из data (без ключа) и паспорт")
        return EXIT_OK
    st = ctx.http.request("GET", f"/v1/media/{a.id}").json or {}
    if st.get("status") != "completed":
        say(f"статус {st.get('status')} — скачивать нечего" + (f": {st.get('error')}" if st.get("error") else ""))
        return EXIT_TIMEOUT if st.get("status") not in TERMINAL else EXIT_FAILED
    j = ctx.ledger.find_by_id(a.id) or {}
    job = {"tag": j.get("tag") or "download", "agent": j.get("agent") or ctx.default_agent}
    model_id = st.get("model") or j.get("model") or "model"
    files = fetch_results(ctx, st, job, a.id, model_id)
    hist = get_history(ctx, a.id)
    cost = usage_cost(st)
    pp = write_passport(files, {"schema": "polza-passport/1", "client": VERSION, "uid": j.get("uid"),
                                "request_hash": j.get("request_hash"), "job": job, "response_final": st,
                                "history": hist, "cost": {"usage_cost_rub": cost, "estimate_rub": j.get("estimate_rub")},
                                "files": files, "base_url": ctx.base, "downloaded_at": now_iso(),
                                "note": "скачано командой download (запрос см. в журнале по uid)"})
    ev = {"event": "completed", "uid": j.get("uid") or ("dl_" + uuid.uuid4().hex[:10]), "id": a.id, "cost_rub": cost,
          "files": [f["path"] for f in files], "passport": pp, "base_url": ctx.base, "model": model_id,
          "agent": job["agent"], "tag": job["tag"]}
    if j.get("estimate_rub") is not None:
        ev["estimate_rub"] = j["estimate_rub"]
    ctx.ledger.append(ev)
    say(f"паспорт {pp}")
    return EXIT_OK


def cmd_upload(ctx: Ctx, a):
    p = Path(a.file)
    if not p.exists():
        raise SystemExit(f"нет файла {p}")
    pol = "PERMANENT" if a.permanent else "TEMP_UPLOAD"
    if not ctx.live:
        say("# СУХОЙ ПРОГОН — ничего не отправлено")
        ctx.http.show("POST", "/v1/storage/upload", f"multipart/form-data: file=@{p.name} ({p.stat().st_size} байт, "
                                                   f"{mimetypes.guess_type(p.name)[0]}), storagePolicy={pol}"
                      + (f", externalUserId={a.external_user_id}" if a.external_user_id else ""), ctype="multipart/form-data")
        say(f"# {pol}: " + ("бессрочно, в лимите хранилища организации" if a.permanent else "24 часа"))
        return EXIT_OK
    up = upload_file(ctx, str(p), a.permanent, a.external_user_id)
    ctx.ledger.append({"event": "upload", "uid": "upl_" + uuid.uuid4().hex[:10], "agent": ctx.default_agent,
                       "base_url": ctx.base, "file_id": up.get("id"), "url": up.get("url"), "src": str(p),
                       "storagePolicy": up.get("storagePolicy"), "expiresAt": up.get("expiresAt")})
    say(jdump(redact_obj(up)))
    return EXIT_OK


def cmd_ops(ctx: Ctx, a):
    j = ctx.ledger.find_by_id(a.id) or {}
    model_id = a.model or j.get("model")
    if not model_id:
        raise SystemExit("не знаю модель генерации: укажите --model (в журнале нет этого id)")
    m = ctx.model(model_id)
    oe = pc.operation_estimate(m, a.operation)
    params = json.loads(Path(a.params[1:]).read_text()) if (a.params or "").startswith("@") else json.loads(a.params or "{}")
    issues = []
    for k, spec in (oe["params"] or {}).items():
        v = params.get(k)
        if spec.get("required") and v is None:
            issues.append(f"обязательный параметр {k} не задан")
        if v is not None and spec.get("values") and pc.as_str(v) not in spec["values"]:
            issues.append(f"{k}={v!r} не из {spec['values']}")
        if v is not None and spec.get("max_length") and isinstance(v, str) and len(v) > spec["max_length"]:
            issues.append(f"{k}: длина {len(v)} > {spec['max_length']}")
        n = pc.to_num(v) if v is not None and not spec.get("values") else None
        if n is not None and spec.get("min") is not None and n < spec["min"]:
            issues.append(f"{k}={n} < {spec['min']}")
        if n is not None and spec.get("max") is not None and n > spec["max"]:
            issues.append(f"{k}={n} > {spec['max']}")
    for k in params:
        if k not in (oe["params"] or {}):
            issues.append(f"параметра {k} нет у операции (есть: {list((oe['params'] or {}).keys())})")
    body = {"operation": a.operation, "params": params, "async": bool(oe["async"])}
    prep = Prepared()
    prep.model, prep.job, prep.agent, prep.tag = m, {"tag": f"{a.operation}-{a.id}", "agent": j.get("agent")}, \
        j.get("agent") or ctx.default_agent, slug(f"{j.get('tag') or 'op'}-{a.operation}")
    prep.provider = (m.get("top_provider") or {}).get("name")
    prep.estimate = {"rub": oe["rub"], "rub_low": oe["rub"], "rub_high": oe["rub"], "formula": oe["formula"]}
    prep.request_hash = hashlib.sha256(json.dumps({"op": a.operation, "id": a.id, "params": params},
                                                  sort_keys=True).encode()).hexdigest()
    say(f"# операция {a.operation} над {a.id} ({model_id}): {oe['formula']}; async={oe['async']} (по каталогу)")
    for i in issues:
        say(f"#   ✗ {i}")
    ok, msg = budget_check(ctx, prep)
    say(f"# {'Бюджет OK' if ok else 'ОТКАЗ'}: {msg}")
    if not ctx.live:
        say("# СУХОЙ ПРОГОН — ничего не отправлено")
        ctx.http.show("POST", f"/v1/media/{a.id}/operations", body)
        return EXIT_JOB if issues else EXIT_OK
    if issues:
        return EXIT_JOB
    if not ok:
        return EXIT_BUDGET
    ctx.ledger.append({"event": "submit", "uid": prep.uid, "agent": prep.agent, "tag": prep.tag, "model": model_id,
                       "operation": a.operation, "parent_id": a.id, "base_url": ctx.base,
                       "request_hash": prep.request_hash, "estimate_rub": oe["rub"]})
    t0 = time.time()
    try:
        r = ctx.http.request("POST", f"/v1/media/{a.id}/operations", body=body,
                             timeout=(ctx.a.http_timeout if oe["async"] else max(ctx.a.http_timeout, 150)))
    except ApiError as e:
        ctx.ledger.append({"event": "unknown" if e.ambiguous else "http_error", "uid": prep.uid, "base_url": ctx.base,
                           "http_status": e.status, "code": e.code, "message": e.message})
        say(f"ОШИБКА: {e}", err=True)
        return EXIT_HTTP
    st = r.json or {}
    new_id = st.get("id") or a.id
    ctx.ledger.append({"event": "created", "uid": prep.uid, "id": new_id, "status": st.get("status"), "base_url": ctx.base})
    if st.get("status") not in TERMINAL:
        st, n, _ = poll(ctx, new_id, "video", prep.tag)
    if st.get("status") != "completed":
        ev = st.get("status") if st.get("status") in TERMINAL else "timeout"
        ctx.ledger.append({"event": ev, "uid": prep.uid, "id": new_id, "cost_rub": usage_cost(st) or 0.0,
                           "error": st.get("error"), "base_url": ctx.base})
        say(f"операция: {ev} {st.get('error') or ''}", err=True)
        return EXIT_FAILED if ev != "timeout" else EXIT_TIMEOUT
    files = fetch_results(ctx, st, prep, new_id, model_id)
    cost = usage_cost(st)
    pp = write_passport(files, {"schema": "polza-passport/1", "client": VERSION, "uid": prep.uid,
                                "operation": a.operation, "parent_id": a.id, "request": {"method": "POST",
                                "url": ctx.http.url(f"/v1/media/{a.id}/operations"), "body": body},
                                "response_final": st, "cost": {"usage_cost_rub": cost, "estimate_rub": oe["rub"]},
                                "timing": {"wall_s": round(time.time() - t0, 2)}, "files": files, "base_url": ctx.base})
    ctx.ledger.append({"event": "completed", "uid": prep.uid, "id": new_id, "cost_rub": cost, "estimate_rub": oe["rub"],
                       "files": [f["path"] for f in files], "passport": pp, "base_url": ctx.base})
    say(f"готово: {cost} ₽, паспорт {pp}")
    return EXIT_OK


def cmd_ledger(ctx: Ctx, a):
    js = list(ctx.ledger.jobs().values())
    if a.agent:
        js = [j for j in js if j.get("agent") == a.agent]
    if a.sum:
        by = {}
        for j in js:
            key = (j.get("base_url"), j.get("agent"))
            b = by.setdefault(key, {"jobs": 0, "spent": 0.0, "completed": 0, "failed": 0, "reserved": 0.0})
            b["jobs"] += 1
            b["spent"] += j["spent"]
            b["completed"] += j.get("state") == "completed"
            b["failed"] += j.get("state") in ("failed", "cancelled", "http_error")
            if j.get("state") in ("submit", "created", "timeout", "unknown"):
                b["reserved"] += j["spent"]
        say(f"{'base_url':34} {'агент':10} {'заданий':>7} {'готово':>6} {'ошибок':>6} {'₽ всего':>10} {'₽ в резерве':>12}")
        for (bu, ag), b in sorted(by.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
            say(f"{str(bu):34} {str(ag):10} {b['jobs']:>7} {b['completed']:>6} {b['failed']:>6} "
                f"{pc.fmt_rub(b['spent']):>10} {pc.fmt_rub(b['reserved']):>12}")
        say(f"# журнал {ctx.ledger.path}; бюджет {pc.fmt_rub(ctx.budget_total)} ₽ для {ctx.base}: потрачено "
            f"{pc.fmt_rub(ctx.ledger.spent(ctx.base))} ₽")
        return EXIT_OK
    evs = ctx.ledger.events()
    if a.agent:
        uids = {j["uid"] for j in js}
        evs = [e for e in evs if e.get("uid") in uids]
    by_uid = {j["uid"]: j for j in js}
    for e in evs[-a.tail:]:
        j = by_uid.get(e.get("uid"), {})
        e = {**{k: j.get(k) for k in ("agent", "tag", "model") if j.get(k)}, **e}
        say(json.dumps(e, ensure_ascii=False) if a.json else
            f"{e.get('ts')} {e.get('event'):10} {str(e.get('agent') or ''):8} {str(e.get('tag') or ''):20} "
            f"{str(e.get('model') or ''):32} {str(e.get('id') or ''):24} "
            f"{('оценка ' + str(e['estimate_rub'])) if e.get('estimate_rub') is not None else ''} "
            f"{('цена ' + str(e['cost_rub'])) if e.get('cost_rub') is not None else ''}")
    return EXIT_OK


def cmd_balance(ctx: Ctx, a):
    if not ctx.live:
        say("# СУХОЙ ПРОГОН")
        ctx.http.show("GET", "/v2/balance")
        ctx.http.show("GET", "/v1/key")
        return EXIT_OK
    for path in ("/v2/balance", "/v1/key"):
        try:
            say(path, jdump(redact_obj(ctx.http.request("GET", path).json)))
        except ApiError as e:
            say(f"{path}: {e}", err=True)
    return EXIT_OK


def cmd_history(ctx: Ctx, a):
    if not ctx.live:
        say("# СУХОЙ ПРОГОН")
        ctx.http.show("GET", f"/v1/history/generations/{a.id}")
        return EXIT_OK
    say(jdump(redact_obj(ctx.http.request("GET", f"/v1/history/generations/{a.id}").json)))
    return EXIT_OK


# ---------------------------------------------------------------------------------------------------------------

def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    g = common.add_argument_group("общие")
    g.add_argument("--live", action="store_true", help="реально отправлять запросы (иначе сухой прогон)")
    g.add_argument("--catalog", help="снимок каталога (имя папки в 99-raw/cache/polza, путь); по умолчанию последний")
    g.add_argument("--base-url", help="база API (по умолчанию POLZA_BASE_URL или https://polza.ai/api)")
    g.add_argument("--ledger", help="журнал затрат (по умолчанию 99-raw/experiments/_ledger.jsonl)")
    g.add_argument("--out", help="корень для результатов (по умолчанию 99-raw/experiments/_polza/<агент>/<дата>)")
    g.add_argument("--agent", help="агент по умолчанию для заданий без поля agent")
    g.add_argument("--budget-total", type=float, help="общий лимит ₽ по журналу (по умолчанию 2000)")
    g.add_argument("--budget-agent", type=float, help="лимит ₽ на агента по журналу")
    g.add_argument("--max-job", type=float, help="лимит ₽ на одно задание (по умолчанию 60)")
    g.add_argument("--force", action="store_true", help="не брать результат из кэша")
    g.add_argument("--curl", action="store_true", help="в сухом прогоне напечатать и curl-команду")
    g.add_argument("--verbose", "-v", action="store_true")
    g.add_argument("--poll-interval", type=float, help="пауза опроса, с (по умолчанию 4 — картинки, 8 — видео)")
    g.add_argument("--max-wait", type=float, help="таймаут опроса, с (по умолчанию 600 — картинки, 1800 — видео)")
    g.add_argument("--http-timeout", type=float, default=60.0)
    g.add_argument("--no-history", action="store_true", help="не запрашивать /v1/history для паспорта")
    g.add_argument("--no-preflight", action="store_true", help="не проверять /v2/balance и /v1/key перед тратой")
    g.add_argument("--no-validate", action="store_true", help="отправлять даже при ошибках проверки по каталогу")
    g.add_argument("--no-fill", action="store_true", help="не подставлять default каталога для ценовых параметров")
    g.add_argument("--allow-unknown", action="store_true", help="параметры вне каталога — предупреждение, а не ошибка")
    g.add_argument("--allow-unknown-price", action="store_true", help="разрешить задания с неизвестной ценой")
    g.add_argument("--raw", action="store_true", help="input как есть: без приведения типов и файлов")
    ap = argparse.ArgumentParser(prog="polza.py", description=__doc__.split("\n")[0], epilog=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("models", parents=[common])
    s.add_argument("--type", choices=pc.MEDIA_TYPES)
    s.add_argument("--search")
    s.add_argument("--fresh", action="store_true", help="бесплатный GET /v1/models вместо снимка")
    s.set_defaults(fn=cmd_models)
    s = sp.add_parser("show", parents=[common])
    s.add_argument("model")
    s.add_argument("--provider")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_show)
    for name, fn in (("estimate", cmd_estimate), ("run", cmd_run), ("batch", cmd_batch)):
        s = sp.add_parser(name, parents=[common])
        s.add_argument("job")
        if name == "batch":
            s.add_argument("--parallel", type=int, default=2)
        s.set_defaults(fn=fn)
    for name, fn in (("status", cmd_status), ("download", cmd_download), ("history", cmd_history)):
        s = sp.add_parser(name, parents=[common])
        s.add_argument("id")
        s.set_defaults(fn=fn)
    s = sp.add_parser("upload", parents=[common])
    s.add_argument("file")
    s.add_argument("--permanent", action="store_true")
    s.add_argument("--external-user-id")
    s.set_defaults(fn=cmd_upload)
    s = sp.add_parser("ops", parents=[common])
    s.add_argument("id")
    s.add_argument("operation", choices=["extend", "upscale_1080p", "upscale_4k"])
    s.add_argument("--params", help='JSON параметров операции или @файл, напр. \'{"prompt": "...", "seeds": 12345}\'')
    s.add_argument("--model", help="модель исходной генерации (если её нет в журнале)")
    s.set_defaults(fn=cmd_ops)
    s = sp.add_parser("ledger", parents=[common])
    s.add_argument("--sum", action="store_true")
    s.add_argument("--tail", type=int, default=30)
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_ledger)
    s = sp.add_parser("balance", parents=[common])
    s.set_defaults(fn=cmd_balance)
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    ctx = Ctx(a)
    try:
        code = a.fn(ctx, a)
    except ApiError as e:
        say(f"ОШИБКА API: {e}", err=True)
        if isinstance(e.body, dict):
            say(jdump(redact_obj(e.body)), err=True)
        code = EXIT_HTTP
    except KeyboardInterrupt:
        say("прервано; незавершённые генерации см. polza.py ledger", err=True)
        code = 130
    sys.exit(code or 0)


if __name__ == "__main__":
    main()
