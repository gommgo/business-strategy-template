#!/usr/bin/env python3
"""polza.py — клиент Media API polza.ai: сухой прогон по умолчанию, трата только с --live.

Python 3.13, только стандартная библиотека (+ polza_catalog.py рядом).

Подкоманды:
  models [--type image|video] [--search S] [--fresh]   модели из снимка каталога (или свежий бесплатный GET)
  show MODEL [--provider P] [--json]                   параметры, цены, операции, провайдеры, заметки
  estimate JOB.json|JOBS.jsonl [--ops OP[,OP…]]        проверка по каталогу + цена + бюджет, без сети; --ops —
                                                       операции над готовым результатом (extend, upscale_1080p,
                                                       upscale_4k): строка сметы на операцию, цена — в сумме
  run JOB.json                                         одно задание (сухой прогон; --live — отправить)
  batch JOBS.jsonl [--parallel 2]                      серия (не больше 3 параллельно)
  status ID                                            статус генерации (GET /v1/media/{id})
  download ID                                          скачать результат готовой генерации + паспорт
  upload FILE [--permanent]                            загрузить файл в хранилище polza (TEMP_UPLOAD 24 ч / PERMANENT)
  ops ID extend|upscale_1080p|upscale_4k [--params JSON]   операция над готовым видео (Veo 3.1); результат сверяется
                                                       с исходником: тот же id и тот же файл — операция не выполнена
  ledger [--sum] [--agent X] [--tail N]                журнал затрат
  ledger --ops                                         сверка записей операций с сохранёнными ответами, без сети
  ledger --balance [--baseline RUB]                    сверка журнала с балансом канала: spentAmount из /v2/balance
                                                       против суммы журнала; --baseline — траты ключа вне журнала;
                                                       чтение, не трата — идёт без --live; расхождение — код 1
  balance                                              GET /v2/balance и /v1/key: баланс и лимит ключа; чтение, не
                                                       трата — идёт без --live
  history ID                                           GET /v1/history/generations/{id} (провайдер, clientCost)
  selftest                                             самопроверка на подменном канале: операции, смета с операцией,
                                                       баланс и сверка журнала, один файл — одна загрузка, размер
                                                       результата в паспорте; без сети и без ключа

Задание (JSON): {"model": "...", "input": {...}, "provider": {...}?, "tag": "...", "agent": "...", "notes": "...",
  "variant": 1?, "max_rub": 10?, "out_dir": "..."?, "meta": {"ref_video_seconds": 7.5}?, "user": "..."?}
Файлы в input.images / input.videos: URL, data:URI, локальный путь (≤ 4 МБ — base64, больше — загрузка в хранилище)
или объект {"type": "url"|"base64", "data": ...} (OpenAPI MediaFileDto). Один локальный файл в нескольких местах
задания (петля: первый кадр = последний) загружается в хранилище один раз, во все места встаёт одна ссылка.
Паспорт результата (<тег>__<модель>__<id>.passport.json) несёт поле size: заказанную ступень размера и фактические
ширину и высоту файла — ступень каталога (1K, 2K, 720p) называет цену, кадр внутри неё выбирает модель.

Окружение: POLZA_API_KEY или файл ~/.config/polza/api_key (права 600); POLZA_BASE_URL (по умолчанию
https://polza.ai/api); POLZA_CATALOG (снимок каталога: имя папки в $DDD_HOME/cache/ai-media/polza или путь, по
умолчанию — последний); POLZA_LEDGER (журнал затрат, по умолчанию $DDD_HOME/out/ai-media/_ledger.jsonl);
POLZA_OUT_ROOT (корень результатов, по умолчанию $DDD_HOME/out/ai-media/_polza; файлы — в <корень>/<агент>/<дата>/);
POLZA_BUDGET_TOTAL (2000); POLZA_BUDGET_AGENT; POLZA_MAX_JOB (60). Ключ никогда не печатается и не пишется в журнал
и паспорта.

Коды выхода: 0 — успех; 1 — ошибка задания/проверки; 2 — отказ по бюджету или цене; 3 — таймаут опроса (генерацию
можно дожать: download ID --live); 4 — генерация failed/cancelled или операция не выполнена (канал вернул исходник);
5 — HTTP-ошибка; 6 — ошибка скачивания.
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
sys.path.insert(0, str(TOOLS.parent / "lib"))  # scripts/lib: kbpaths
import kbpaths  # noqa: E402
import polza_catalog as pc  # noqa: E402

VERSION = "polza.py 1.0 (2026-09-23)"
ROOT = pc.ROOT
DEFAULT_BASE = "https://polza.ai/api"
DEFAULT_LEDGER = kbpaths.out("ai-media") / "_ledger.jsonl"  # журнал затрат — общий с mp_client.py
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

def summarize_jobs(events: list[dict]) -> dict:
    """События журнала → uid → сводка: последнее состояние, id, стоимость (факт или резерв по оценке)."""
    js = {}
    for e in events:
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
        return summarize_jobs(self.events())

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

    def find_by_id(self, gen_id: str, with_ops: bool = False):
        """Запись генерации по id. Операция, которой канал ответил записью исходника, носит его id: без with_ops такая
        запись пропускается — иначе status и download приписали бы операции цену и файлы исходной генерации."""
        for j in reversed(list(self.jobs().values())):
            if j.get("id") == gen_id and (with_ops or not (j.get("operation") and j.get("parent_id") == gen_id)):
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


def image_size(path: Path) -> tuple[int, int] | None:
    """Ширина и высота PNG, GIF, WebP, JPEG по заголовку файла — без Pillow."""
    try:
        with open(path, "rb") as f:
            head = f.read(1 << 18)
    except OSError:
        return None
    if head[:8] == b"\x89PNG\r\n\x1a\n" and len(head) >= 24:
        return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
    if head[:6] in (b"GIF87a", b"GIF89a") and len(head) >= 10:
        return int.from_bytes(head[6:8], "little"), int.from_bytes(head[8:10], "little")
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP" and len(head) >= 30:
        if head[12:16] == b"VP8X":
            return int.from_bytes(head[24:27], "little") + 1, int.from_bytes(head[27:30], "little") + 1
        if head[12:16] == b"VP8L":
            bits = int.from_bytes(head[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if head[12:16] == b"VP8 ":
            return int.from_bytes(head[26:28], "little") & 0x3FFF, int.from_bytes(head[28:30], "little") & 0x3FFF
    if head[:2] == b"\xff\xd8":
        i = 2
        while i + 9 <= len(head):
            if head[i] != 0xFF:
                i += 1
                continue
            marker = head[i + 1]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):      # кадр SOF: высота, затем ширина
                return int.from_bytes(head[i + 7:i + 9], "big"), int.from_bytes(head[i + 5:i + 7], "big")
            if marker in (0x01, 0xD8, 0xFF) or 0xD0 <= marker <= 0xD7:           # маркер без длины
                i += 1 if marker == 0xFF else 2
                continue
            i += 2 + int.from_bytes(head[i + 2:i + 4], "big")
    return None


def image_info(path: Path) -> dict | None:
    try:
        from PIL import Image  # Pillow необязателен: без него — размер по заголовку файла
        with Image.open(path) as im:
            return {"width": im.width, "height": im.height, "mode": im.mode, "format": im.format,
                    "has_alpha": im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info}
    except Exception:  # noqa: BLE001
        wh = image_size(path)
        return {"width": wh[0], "height": wh[1]} if wh else None


SIZE_KEYS = ("image_resolution", "resolution", "aspect_ratio", "quality", "mode", "upscale_factor")


def result_size(inp: dict, files: list[dict]) -> dict:
    """Поле size паспорта: заказанная ступень размера (параметры input) и фактические ширина и высота каждого файла
    результата. Ступень каталога — имя ступени цены: кадр внутри неё выбирает модель, и от вызова к вызову он
    меняется; размер, с которым работает вёрстка, — фактический."""
    return {"requested": {k: inp[k] for k in SIZE_KEYS if k in (inp or {})},
            "actual": [{"path": f.get("path"), "width": (f.get("media") or {}).get("width"),
                        "height": (f.get("media") or {}).get("height")} for f in files]}


def size_note(size: dict) -> str:
    dims = [f"{s['width']}×{s['height']}" for s in size["actual"] if s.get("width") and s.get("height")]
    return ("; размер " + ", ".join(dims)) if dims else ""


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
        self.digests = {}          # локальный путь → sha256 содержимого: один файл — одна загрузка
        self.repeated = set()      # sha256 файлов, стоящих в задании больше одного раза
        self.request_hash = ""
        self.ref_seconds = None
        self.uid = uuid.uuid4().hex[:12]
        self.agent = "unknown"
        self.tag = "job"

    @property
    def errors(self):
        return [i for i in self.issues if i["level"] == "error"]


def local_file(item, job: dict) -> Path | None:
    """Локальный файл поля задания (путь — от папки файла задания) или None: URL, data:URI, объект, файла нет."""
    if not isinstance(item, str) or item.startswith(("http://", "https://", "data:")):
        return None
    p = Path(item).expanduser()
    if not p.is_absolute():
        base = Path(job.get("_dir", "."))
        p = (base / p) if (base / p).exists() else p
    return p if p.is_file() else None


def repeated_files(inp: dict, job: dict) -> set:
    """sha256 локальных файлов, которые стоят в input больше одного раза (в images, videos и полях-ссылках)."""
    places = {}
    for key in ("images", "videos") + URL_FILE_KEYS:
        v = inp.get(key)
        for it in (v if isinstance(v, list) else [v]):
            p = local_file(it, job)
            if p is not None:
                d = file_sha256(p)
                places[d] = places.get(d, 0) + 1
    return {d for d, n in places.items() if n > 1}


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
    if len(data) <= INLINE_MAX and digest not in prep.repeated:
        b64 = base64.b64encode(data).decode()
        return {"type": "base64", "data": f"data:{mime};base64,{b64}"}, {"type": "file", "sha256": digest}
    if not allow_upload:
        prep.issues.append({"level": "error", "param": f"{key}[{idx}]", "msg": "файл > 4 МБ и загрузка недоступна"})
    prep.uploads.append((key, idx, str(p)))
    prep.digests[str(p)] = digest
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
    # файлы; один файл в нескольких местах задания (петля [A, A]) идёт загрузкой в хранилище — одной на все места:
    # встроенный base64 занял бы тело запроса столько раз, сколько мест
    hash_files = {}
    if not raw:
        prep.repeated = repeated_files(inp, job)
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
            prep.digests[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
            hash_files[ukey] = {"type": "file", "sha256": prep.digests[str(p)]}
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
# Операция над готовой генерацией: сверка результата с исходником и цена операции
# ---------------------------------------------------------------------------------------------------------------

OP_NOT_APPLIED = "OPERATION_NOT_APPLIED"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def known_results(jobs: dict, gen_id: str) -> dict:
    """Что журнал (сводка jobs: uid → задание) знает о генерации до операции: sha256 → путь каждого файла, который уже
    выдавался под этим id (исходник и результаты прежних операций над ним), и цена самой генерации. Отпечаток берётся
    из паспорта — он снят при скачивании; без паспорта — с файла на диске."""
    files, cost = {}, None
    for j in jobs.values():
        if j.get("id") != gen_id:
            continue
        if not j.get("operation") and j.get("cost_rub") is not None:
            cost = float(j["cost_rub"])
        recorded = {}
        pp = absp(j["passport"]) if j.get("passport") else None
        if pp is not None and pp.exists():
            try:
                for f in json.loads(pp.read_text(encoding="utf-8")).get("files") or []:
                    if f.get("sha256") and f.get("path"):
                        recorded[f["sha256"]] = f["path"]
            except (OSError, json.JSONDecodeError):
                pass
        if not recorded:
            for f in j.get("files") or []:
                if absp(f).is_file():
                    recorded[file_sha256(absp(f))] = f
        for digest, path in recorded.items():
            if digest not in files or not absp(files[digest]).is_file():
                files[digest] = path
    return {"sha256": files, "cost_rub": cost}


def operation_cost(source_id: str, known: dict, op_resp: dict, final: dict) -> tuple[float | None, bool]:
    """Цена операции по её ответу и признак «у операции своя запись».

    Своя запись — id в ответе на запрос операции не равен id исходника: usage этой записи и есть цена операции. Иначе
    канал ответил записью исходной генерации, и usage при опросе — цена исходника, а не операции: цена берётся только
    из ответа на сам запрос операции и только если она не совпала с ценой исходника из журнала. Цены в ответе нет —
    None: журнал держит оценку по каталогу, а не чужое списание."""
    op_id = (op_resp or {}).get("id")
    own = bool(op_id) and op_id != source_id
    if own:
        cost = usage_cost(final)
        return (cost if cost is not None else usage_cost(op_resp)), True
    cost = usage_cost(op_resp)
    if cost is not None and known.get("cost_rub") is not None and abs(cost - known["cost_rub"]) < 1e-9:
        cost = None
    return cost, False


def operation_outcome(source_id: str, known: dict, op_resp: dict, final: dict, files: list[dict]) -> dict:
    """Итог завершённой операции. Тот же id и только те файлы, что уже выдавались под этим id, — канал вернул
    исходник: операция не выполнена, цена 0, код OP_NOT_APPLIED."""
    cost, own = operation_cost(source_id, known, op_resp, final)
    got = [f.get("sha256") for f in files]
    same = [known["sha256"][h] for h in got if h in known["sha256"]]
    if not own and got and len(same) == len(got):
        return {"applied": False, "own_record": False, "code": OP_NOT_APPLIED, "cost_rub": 0.0, "same_as": same}
    return {"applied": True, "own_record": own, "code": None, "cost_rub": cost, "same_as": same}


def check_operations(ledger: Ledger) -> list[dict]:
    """Сверка записей операций журнала с их сохранёнными ответами: паспорт операции против файлов, которые журнал знал
    под id исходника до неё. Строка на операцию: applied — выполнена ли (None — паспорта нет, сверить не с чем), spent
    — сколько за неё стоит в журнале, phantom — деньги записаны за операцию, которая не выполнена."""
    events = ledger.events()
    rows = []
    for uid, j in summarize_jobs(events).items():
        if not j.get("operation") or not j.get("parent_id"):
            continue
        first = next(i for i, e in enumerate(events) if e.get("uid") == uid)
        known = known_results(summarize_jobs(events[:first]), j["parent_id"])
        pp = absp(j["passport"]) if j.get("passport") else None
        try:
            pas = json.loads(pp.read_text(encoding="utf-8")) if pp is not None and pp.exists() else None
        except (OSError, json.JSONDecodeError):
            pas = None
        applied = None
        if pas is not None:
            op_resp = pas.get("response_operation") or {"id": j.get("id")}
            applied = operation_outcome(j["parent_id"], known, op_resp, pas.get("response_final") or {},
                                        pas.get("files") or [])["applied"]
        rows.append({"uid": uid, "tag": j.get("tag"), "operation": j["operation"], "parent_id": j["parent_id"],
                     "state": j.get("state"), "spent": j["spent"], "applied": applied,
                     "phantom": applied is False and j["spent"] > 0})
    return rows


def drop_copies(files: list[dict], known: dict) -> list[str]:
    """Убрать скачанные копии исходника: файл с именем операции, а содержимым исходника, сошёл бы за её результат.
    Копия снимается, только когда тот же файл лежит на диске под своим именем."""
    removed = []
    for f in files:
        src = known["sha256"].get(f.get("sha256"))
        if not src:
            continue
        copy, orig = absp(f["path"]), absp(src)
        if orig.is_file() and copy.is_file() and copy.resolve() != orig.resolve() and file_sha256(orig) == f["sha256"]:
            copy.unlink()
            removed.append(f["path"])
    return removed


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
    uploaded = {}              # sha256 → ответ хранилища: один файл в нескольких местах задания — одна загрузка
    for key, idx, path in prep.uploads:
        same = prep.digests.get(path, path)
        up = uploaded.get(same)
        if up is None:
            up = uploaded[same] = upload_file(ctx, path)
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
        "files": files, "size": result_size(prep.body["input"], files), "base_url": ctx.base,
    }
    pp = write_passport(files, passport)
    ctx.ledger.append({"event": "completed", "uid": prep.uid, "id": gen_id, "cost_rub": cost,
                       "estimate_rub": rub, "files": [f["path"] for f in files], "passport": pp, "base_url": ctx.base,
                       "provider_actual": passport["provider_actual"], "wall_s": passport["timing"]["wall_s"]})
    delta = passport["cost"]["delta_rub"]
    say(f"  [{label}] ГОТОВО за {passport['timing']['wall_s']} с; цена {cost} ₽ (оценка {prep.estimate.get('rub')}"
        + (f", разница {delta:+}" if delta else "") + f"){size_note(passport['size'])}; паспорт {pp}")
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
        once = {}
        for key, idx, path in prep.uploads:
            once.setdefault(prep.digests.get(path, path), []).append(path)
        for paths in once.values():
            say(f"# перед отправкой: POST {ctx.http.url('/v1/storage/upload')} (multipart, TEMP_UPLOAD) ← {paths[0]}"
                + (f" — одна загрузка, мест в задании — {len(paths)}" if len(paths) > 1 else ""))
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


def say_catalog(ctx: Ctx):
    """Какой снимок каталога взят для оценки и сколько ему: снимок не за сегодня — с отметкой «!»."""
    note, check = pc.snapshot_note(ctx.snap)
    say(("# ! " if check else "# ") + note)


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
    ops = [x.strip() for x in (getattr(a, "ops", None) or "").split(",") if x.strip()]
    total, ops_total, bad = 0.0, 0.0, 0
    say_catalog(ctx)
    for j in jobs:
        j.setdefault("_dir", str(Path(a.job).resolve().parent))
        prep = prepare(ctx, j, fill=not a.no_fill, allow_unknown=a.allow_unknown, raw=a.raw)
        if prep.model is None:
            print_issues(prep)
            bad += 1
            continue
        print_plan(ctx, prep, show_request=a.verbose)
        failed = bool(prep.errors)
        total += price_for_limits(prep) or 0
        for op in ops:              # операция над готовым результатом — отдельный запрос и отдельная цена каталога
            try:
                oe = pc.operation_estimate(prep.model, op)
            except KeyError as e:
                say(f"#   ✗ операция {op}: {e.args[0]}")
                failed = True
                continue
            if oe["rub"] is None:
                say(f"#   ✗ операция {op}: цены операции в каталоге нет")
                failed = True
                continue
            say(f"# Операция {op} над результатом: {oe['formula']} (polza.py ops ID {op})")
            ops_total += oe["rub"]
        bad += failed
        say("")
    say(f"# ИТОГО: заданий {len(jobs)}, с ошибками {bad}, оценка суммы {pc.fmt_rub(total + ops_total)} ₽ "
        + (f"(задания {pc.fmt_rub(total)} ₽ + операции {pc.fmt_rub(ops_total)} ₽) " if ops else "")
        + f"(потрачено {pc.fmt_rub(ctx.ledger.spent(ctx.base))} из {pc.fmt_rub(ctx.budget_total)} ₽)")
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
    say_catalog(ctx)
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
    say_catalog(ctx)
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
                                "files": files, "size": result_size({}, files), "base_url": ctx.base,
                                "downloaded_at": now_iso(),
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
    j = ctx.ledger.find_by_id(a.id) or ctx.ledger.find_by_id(a.id, with_ops=True) or {}
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
    known = known_results(ctx.ledger.jobs(), a.id)     # до записи операции: её события носят тот же id
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
    op_resp = r.json or {}
    st = op_resp
    new_id = op_resp.get("id") or a.id
    ctx.ledger.append({"event": "created", "uid": prep.uid, "id": new_id, "status": st.get("status"), "base_url": ctx.base})
    if st.get("status") not in TERMINAL:
        st, n, _ = poll(ctx, new_id, "video", prep.tag)
    if st.get("status") != "completed":
        ev = st.get("status") if st.get("status") in TERMINAL else "timeout"
        cost, _ = operation_cost(a.id, known, op_resp, st)
        ctx.ledger.append({"event": ev, "uid": prep.uid, "id": new_id, "cost_rub": cost or 0.0,
                           "error": st.get("error"), "base_url": ctx.base})
        say(f"операция: {ev} {st.get('error') or ''}", err=True)
        return EXIT_FAILED if ev != "timeout" else EXIT_TIMEOUT
    files = fetch_results(ctx, st, prep, new_id, model_id)
    res = operation_outcome(a.id, known, op_resp, st, files)
    cost = res["cost_rub"]
    passport = {"schema": "polza-passport/1", "client": VERSION, "uid": prep.uid,
                "operation": a.operation, "parent_id": a.id, "request": {"method": "POST",
                "url": ctx.http.url(f"/v1/media/{a.id}/operations"), "body": body},
                "response_operation": op_resp, "response_final": st, "outcome": res,
                "cost": {"usage_cost_rub": cost, "estimate_rub": oe["rub"]},
                "timing": {"wall_s": round(time.time() - t0, 2)}, "files": files, "base_url": ctx.base}
    if not res["applied"]:
        msg = (f"канал вернул исходную генерацию — тот же id {a.id} и тот же файл "
               f"(sha256 {files[0]['sha256'][:16]}…): операция {a.operation} не выполнена")
        res["removed_copies"] = drop_copies(files, known)
        pp = write_passport(files, passport)
        ctx.ledger.append({"event": "failed", "uid": prep.uid, "id": new_id, "cost_rub": 0.0, "estimate_rub": oe["rub"],
                           "error": {"code": OP_NOT_APPLIED, "message": msg}, "passport": pp, "base_url": ctx.base})
        say(f"ОШИБКА {OP_NOT_APPLIED}: {msg}; цена 0 ₽, файл исходника — {res['same_as'][0]}; паспорт {pp}", err=True)
        return EXIT_FAILED
    if not res["own_record"] and not known["sha256"]:
        say(f"! исходника {a.id} нет в журнале или нет его файлов — результат с ним не сверен: проверь файл сам "
            f"(ffprobe, sha256)", err=True)
    pp = write_passport(files, passport)
    ctx.ledger.append({"event": "completed", "uid": prep.uid, "id": new_id, "cost_rub": cost, "estimate_rub": oe["rub"],
                       "files": [f["path"] for f in files], "passport": pp, "base_url": ctx.base})
    say(f"готово: {cost} ₽, паспорт {pp}" if cost is not None else
        f"готово: цены операции в ответе нет — в журнале оценка по каталогу {pc.fmt_rub(oe['rub'])} ₽ "
        f"(сверь с балансом: polza.py balance --live); паспорт {pp}")
    return EXIT_OK


def read_http(ctx: Ctx):
    """Канал для чтения без траты (баланс, лимит ключа): запрос с ключом идёт и без --live."""
    h = ctx.http
    return h if getattr(h, "live", True) else Http(h.base, h.key, True, timeout=h.timeout, curl=h.curl)


def reconcile(ledger: Ledger, base: str, balance: dict, baseline: float | None) -> dict:
    """Сверка журнала с балансом канала. balance — ответ GET /v2/balance: spentAmount — всё, что списано с ключа.
    Журнал — сумма по base без резерва незавершённых заданий (reserved — отдельно: их исход неизвестен). outside =
    spentAmount − журнал — траты вне журнала; baseline называет, сколько их должно быть: ok — сошлось до копейки,
    diff — расхождение. Без baseline ok = None: сверять не с чем, outside — в отчёт. Без spentAmount в ответе (у ключа
    участника с личным лимитом поля нет) — ok = None и reason."""
    jobs = [j for j in ledger.jobs().values() if j.get("base_url") == base]
    reserved = round(sum(j["spent"] for j in jobs if j.get("state") in ("submit", "created", "timeout", "unknown")), 6)
    fact = round(sum(j["spent"] for j in jobs) - reserved, 6)
    res = {"ok": None, "ledger": fact, "reserved": reserved, "channel_spent": None, "outside": None,
           "baseline": baseline, "diff": None, "reason": None}
    spent = pc.to_num((balance or {}).get("spentAmount"))
    if spent is None:
        res["reason"] = "в ответе /v2/balance нет spentAmount"
        return res
    res["channel_spent"] = float(spent)
    res["outside"] = round(float(spent) - fact, 2)
    if baseline is not None:
        res["diff"] = round(res["outside"] - float(baseline), 2)
        res["ok"] = abs(res["diff"]) < 0.005
    return res


def cmd_ledger(ctx: Ctx, a):
    if getattr(a, "balance", False):
        try:
            bal = read_http(ctx).request("GET", "/v2/balance").json or {}
        except ApiError as e:
            say(f"/v2/balance: {e}", err=True)
            return EXIT_HTTP
        r = reconcile(ctx.ledger, ctx.base, bal, a.baseline)
        say(f"# журнал {ctx.ledger.path}: по {ctx.base} потрачено {pc.fmt_rub(r['ledger'])} ₽"
            + (f", в резерве незавершённых {pc.fmt_rub(r['reserved'])} ₽" if r["reserved"] else ""))
        if r["reason"]:
            say(f"# канал: {r['reason']} — сверить не с чем", err=True)
            return EXIT_JOB
        say(f"# канал: spentAmount {pc.fmt_rub(r['channel_spent'])} ₽, available {bal.get('available')} ₽, резерв "
            f"{bal.get('reservedAmount')}; вне журнала {pc.fmt_rub(r['outside'])} ₽")
        if r["ok"] is None:
            say("# сверка: траты вне журнала назвать ключом --baseline RUB — тогда расхождение даст код 1")
            return EXIT_OK
        say("# сверка: сходится до копейки" if r["ok"] else
            f"# сверка: РАСХОЖДЕНИЕ {r['diff']:+.2f} ₽ (вне журнала {pc.fmt_rub(r['outside'])} ₽ против "
            f"{pc.fmt_rub(r['baseline'])} ₽) — незавершённые и оборванные задания: polza.py ledger, history ID")
        return EXIT_OK if r["ok"] else EXIT_JOB
    if a.ops:
        rows = check_operations(ctx.ledger)
        words = {True: "выполнена", False: "не выполнена — канал вернул исходник (тот же id и тот же файл)",
                 None: "паспорта операции нет — с исходником не сверить"}
        for r in rows:
            say(f"{'✗' if r['phantom'] else '·'} {r['uid']} {r['operation']} над {r['parent_id']} [{r['state']}]: "
                f"{words[r['applied']]}; в журнале {pc.fmt_rub(r['spent'])} ₽"
                + (" — за невыполненную операцию должно быть 0 ₽" if r["phantom"] else ""))
        bad = sum(r["phantom"] for r in rows)
        say(f"# операций {len(rows)}, с деньгами за невыполненную — {bad}; журнал {ctx.ledger.path}: по {ctx.base} "
            f"потрачено {pc.fmt_rub(ctx.ledger.spent(ctx.base))} ₽ — сверь с балансом канала: polza.py balance --live "
            f"(бесплатный GET)")
        return EXIT_JOB if bad else EXIT_OK
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
        say(f"# журнал {ctx.ledger.path}; потрачено по {ctx.base}: {pc.fmt_rub(ctx.ledger.spent(ctx.base))} ₽"
            + (f" из бюджета {pc.fmt_rub(ctx.budget_total)} ₽" if ctx.budget_total > 0 else ""))
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
    """Баланс и лимит ключа — чтение, не трата: запрос идёт и без --live."""
    http = read_http(ctx)
    for path in ("/v2/balance", "/v1/key"):
        try:
            say(path, jdump(redact_obj(http.request("GET", path).json)))
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
# Самопроверка: операции на подменном канале
# ---------------------------------------------------------------------------------------------------------------

class _FakeHttp:
    """Канал самопроверки: ответы и байты результата — из сценария, сети нет."""

    def __init__(self, base: str, replies: dict, blobs: dict):
        self.base, self.replies, self.blobs, self.calls, self.sent = base, replies, blobs, [], []

    def url(self, path: str) -> str:
        return self.base + path

    def show(self, *args, **kw):
        pass

    def request(self, method: str, path: str, **kw) -> Resp:
        self.calls.append((method, path))
        self.sent.append((method, path, kw.get("body")))
        queue = self.replies[(method, path)]
        reply = queue.pop(0) if len(queue) > 1 else queue[0]
        return Resp(200, {}, json.dumps(reply).encode())

    def download(self, url: str, dest: Path, timeout: float = 300, tries: int = 3) -> dict:
        data = self.blobs[url]
        dest.write_bytes(data)
        return {"path": str(dest), "url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                "content_type": "application/octet-stream"}


def selftest() -> int:
    """Операции над готовой генерацией, смета с операцией, баланс и сверка журнала с ним, один файл — одна загрузка,
    размер результата в паспорте — на вымышленных данных: каталог, журнал, исходник и ответы канала — во временной
    папке."""
    import contextlib
    import io
    import tempfile
    global KEY_FILE
    base, model, src_id, src_cost, op_rub = "https://channel.test/api", "demo/video-fast", "gen_source", 45.0, 10.0
    src_bytes, up_bytes, ext_bytes = b"source 720p", b"upscaled 1080p", b"extended"
    cdn = "https://cdn.test/"
    blobs = {cdn + "source.bin": src_bytes, cdn + "up.bin": up_bytes, cdn + "ext.bin": ext_bytes}
    catalog = {"data": [{"id": model, "type": "video", "name": "Demo Video Fast",
                         "top_provider": {"name": "demo", "pricing": {"per_request": src_cost}},
                         "parameters": {"prompt": {"max_length": 500}, "images": {"min": 0, "max": 2},
                                        "resolution": {"default": "720p", "values": ["720p", "1080p"]}},
                         "operations": [
                             {"id": "upscale_1080p", "async": False, "pricing": {"per_request": op_rub},
                              "parameters": {"index": {"type": "number", "min": 0}}},
                             {"id": "extend", "async": True, "pricing": {"per_request": 45},
                              "parameters": {"prompt": {"type": "string", "required": True, "max_length": 200}}}]}]}
    src_record = {"id": src_id, "status": "completed", "data": {"url": cdn + "source.bin"},
                  "usage": {"cost_rub": src_cost}}
    checks = []

    def ok(name, cond, got=""):
        checks.append(bool(cond))
        say(f"{'OK  ' if cond else 'FAIL'} {name}" + (f" — {got}" if got != "" and not cond else ""))

    def stage(tmp: Path, name: str, argv: list[str], replies: dict, budget: str = "60") -> tuple:
        """Свежие журнал и папка результатов с исходной генерацией → (ctx, код выхода, запись операции, исходник)."""
        root = tmp / name
        out = root / "out"
        out.mkdir(parents=True)
        src = out / f"clip__{slug(model)}__{src_id}.bin"
        src.write_bytes(src_bytes)
        src_pp = write_passport([{"path": str(src), "sha256": hashlib.sha256(src_bytes).hexdigest()}],
                                {"schema": "polza-passport/1", "files": [
                                    {"path": str(src), "sha256": hashlib.sha256(src_bytes).hexdigest()}]})
        a = build_parser().parse_args(argv + ["--live", "--catalog", str(tmp / "catalog"), "--ledger",
                                              str(root / "ledger.jsonl"), "--out", str(out), "--base-url", base,
                                              "--agent", "selftest", "--budget-total", budget, "--max-job", "60",
                                              "--poll-interval", "0.01", "--no-history"])
        ctx = Ctx(a)
        ctx.http = _FakeHttp(base, replies, blobs)
        for ev in ({"event": "submit", "agent": "selftest", "tag": "clip", "model": model, "estimate_rub": src_cost},
                   {"event": "created", "id": src_id, "status": "pending"},
                   {"event": "completed", "id": src_id, "cost_rub": src_cost, "files": [str(src)], "passport": src_pp}):
            ctx.ledger.append({"uid": "source", "base_url": base, **ev})
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = cmd_ops(ctx, a)       # печать хода операции самопроверке не нужна: итог — строки OK и FAIL
        job = next((j for j in ctx.ledger.jobs().values() if j.get("operation")), {})
        return ctx, code, job, src

    env_key = os.environ.pop("POLZA_API_KEY", None)
    key_file = KEY_FILE
    try:
        with tempfile.TemporaryDirectory(prefix="polza-selftest-") as t:
            tmp = Path(t)
            KEY_FILE = tmp / "no-key"
            (tmp / "catalog").mkdir()
            (tmp / "catalog" / "api-v1-models.json").write_text(json.dumps(catalog))
            (tmp / "catalog" / "api-v1-models.providers.json").write_text(json.dumps({"data": []}))
            up = ["ops", src_id, "upscale_1080p"]
            op_path = ("POST", f"/v1/media/{src_id}/operations")
            poll_src = ("GET", f"/v1/media/{src_id}")

            # канал отвечает записью исходника и тем же файлом: операция не выполнена
            ctx, code, job, src = stage(tmp, "same-file", up, {
                op_path: [{"id": src_id, "status": "processing"}], poll_src: [src_record]})
            pp = json.loads(absp(job["passport"]).read_text(encoding="utf-8")) if job.get("passport") else {}
            ok("исходник в ответе: код выхода 4", code == EXIT_FAILED, code)
            ok("исходник в ответе: запись failed, цена 0", job.get("state") == "failed" and job.get("spent") == 0.0, job)
            ok("исходник в ответе: в журнале потрачена только генерация", ctx.ledger.spent(base) == src_cost,
               ctx.ledger.spent(base))
            ok("исходник в ответе: код ошибки в паспорте", (pp.get("outcome") or {}).get("code") == OP_NOT_APPLIED
               and pp.get("cost", {}).get("usage_cost_rub") == 0.0 and pp.get("response_operation") is not None, pp)
            ok("исходник в ответе: копия с именем операции снята, исходник на месте",
               list(src.parent.rglob("*.bin")) == [src], sorted(p.name for p in src.parent.rglob("*")))
            ok("исходник в ответе: download и status видят запись генерации, а не операции",
               (ctx.ledger.find_by_id(src_id) or {}).get("uid") == "source", ctx.ledger.find_by_id(src_id))
            nxt = Prepared()
            nxt.estimate = {"rub": op_rub}
            ok("исходник в ответе: следующее задание проходит бюджет", budget_check(ctx, nxt)[0], budget_check(ctx, nxt))
            rows = check_operations(ctx.ledger)
            ok("сверка записей: операция не выполнена, денег за неё в журнале нет",
               [(r["applied"], r["spent"], r["phantom"]) for r in rows] == [(False, 0.0, False)], rows)
            ctx.ledger.append({"event": "completed", "uid": job["uid"], "id": src_id, "cost_rub": src_cost,
                               "base_url": base})
            rows = check_operations(ctx.ledger)
            ok("сверка записей: цена исходника, записанная операции, — деньги за невыполненную",
               [(r["applied"], r["spent"], r["phantom"]) for r in rows] == [(False, src_cost, True)], rows)

            # тот же id, новый файл, в ответе на запрос цены нет: usage опроса — цена исходника, в журнале оценка
            ctx, code, job, src = stage(tmp, "same-id-new-file", up, {
                op_path: [{"id": src_id, "status": "processing"}],
                poll_src: [{**src_record, "data": {"url": cdn + "up.bin"}}]})
            ok("та же запись, новый файл: код 0, completed", code == EXIT_OK and job.get("state") == "completed", (code, job))
            ok("та же запись, новый файл: цена исходника операции не приписана",
               job.get("cost_rub") is None and job.get("spent") == op_rub, job)
            ok("сверка записей: выполненная операция — без замечаний",
               [(r["applied"], r["phantom"]) for r in check_operations(ctx.ledger)] == [(True, False)])

            # синхронный ответ с ценой операции
            ctx, code, job, src = stage(tmp, "sync-priced", up, {
                op_path: [{"id": src_id, "status": "completed", "data": {"url": cdn + "up.bin"},
                           "usage": {"cost_rub": op_rub}}]})
            ok("синхронный ответ: цена из ответа операции", code == EXIT_OK and job.get("cost_rub") == op_rub, (code, job))
            ok("синхронный ответ: опроса исходника нет", poll_src not in ctx.http.calls, ctx.http.calls)

            # синхронный ответ — эхо записи исходника с его ценой, но файл новый
            ctx, code, job, src = stage(tmp, "sync-echo", up, {
                op_path: [{**src_record, "data": {"url": cdn + "up.bin"}}]})
            ok("эхо записи исходника: его цена операции не приписана",
               code == EXIT_OK and job.get("cost_rub") is None and job.get("spent") == op_rub, (code, job))

            # своя запись операции: цена — её usage
            ctx, code, job, src = stage(tmp, "own-record", ["ops", src_id, "extend", "--params", '{"prompt": "go on"}'], {
                op_path: [{"id": "gen_extended", "status": "pending"}],
                ("GET", "/v1/media/gen_extended"): [{"id": "gen_extended", "status": "processing"},
                                                    {"id": "gen_extended", "status": "completed",
                                                     "data": {"url": cdn + "ext.bin"}, "usage": {"cost_rub": 45}}]},
                budget="200")
            ok("своя запись: код 0, цена из записи операции",
               code == EXIT_OK and job.get("id") == "gen_extended" and job.get("cost_rub") == 45, (code, job))
            ok("своя запись: исходник находится по своему id", (ctx.ledger.find_by_id(src_id) or {}).get("uid") == "source")

            # операция упала в записи исходника: его цена — не цена операции
            ctx, code, job, src = stage(tmp, "failed", up, {
                op_path: [{"id": src_id, "status": "processing"}],
                poll_src: [{**src_record, "status": "failed", "error": {"code": "BAD_GATEWAY"}}]})
            ok("отказ операции: код 4, цена 0", code == EXIT_FAILED and job.get("spent") == 0.0, (code, job))

            def ctx_for(name: str, argv: list[str], replies: dict, budget: str = "200") -> tuple:
                """Свежие журнал и папка результатов, подменный канал → (ctx, разобранные ключи)."""
                root = tmp / name
                (root / "out").mkdir(parents=True)
                a = build_parser().parse_args(argv + ["--catalog", str(tmp / "catalog"), "--ledger",
                                                      str(root / "ledger.jsonl"), "--out", str(root / "out"),
                                                      "--base-url", base, "--agent", "selftest", "--budget-total",
                                                      budget, "--max-job", "60", "--no-history", "--no-preflight"])
                ctx = Ctx(a)
                ctx.http = _FakeHttp(base, replies, blobs)
                return ctx, a

            def quiet(fn, *args) -> tuple:
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                    code = fn(*args)
                return code, out.getvalue()

            # смета с операцией над готовым результатом
            job_file = tmp / "clip.job.json"
            job_file.write_text(json.dumps({"model": model, "tag": "clip", "input": {"prompt": "demo clip"}}))
            ctx, a = ctx_for("estimate-ops", ["estimate", str(job_file), "--ops", "upscale_1080p"], {})
            code, text = quiet(cmd_estimate, ctx, a)
            ok("смета с операцией: строка операции, сумма — задание и операция",
               code == EXIT_OK and "Операция upscale_1080p над результатом" in text
               and f"оценка суммы {pc.fmt_rub(src_cost + op_rub)} ₽" in text
               and f"операции {pc.fmt_rub(op_rub)} ₽" in text, text)
            ctx, a = ctx_for("estimate-plain", ["estimate", str(job_file)], {})
            code, text = quiet(cmd_estimate, ctx, a)
            ok("смета без --ops: сумма — только задание", code == EXIT_OK and "Операция" not in text
               and f"оценка суммы {pc.fmt_rub(src_cost)} ₽" in text, text)
            ctx, a = ctx_for("estimate-bad-op", ["estimate", str(job_file), "--ops", "no_such_op"], {})
            code, text = quiet(cmd_estimate, ctx, a)
            ok("смета с операцией, которой нет у модели: ошибка задания, код 1",
               code == EXIT_JOB and "✗ операция no_such_op" in text, (code, text))

            # баланс — чтение без --live; сверка журнала с балансом на записанном образце ответа
            balance = {"amount": "500.00000000", "available": "480.00000000", "reservedAmount": "20.00000000",
                       "spentAmount": "145.00000000", "updatedAt": "2030-01-31T10:00:00.000Z"}
            key_info = {"label": "demo", "limit": 300, "limit_remaining": 155, "limit_reset": "never", "usage": 145}
            channel = {("GET", "/v2/balance"): [balance], ("GET", "/v1/key"): [key_info]}
            ctx, a = ctx_for("balance", ["balance"], channel)
            code, text = quiet(cmd_balance, ctx, a)
            ok("баланс без --live: оба чтения сделаны, ответ канала напечатан",
               code == EXIT_OK and not ctx.live and ctx.http.calls == [("GET", "/v2/balance"), ("GET", "/v1/key")]
               and "480.00000000" in text and "limit_remaining" in text, (code, ctx.http.calls, text))
            dry = Http(base, None, False)
            reader = read_http(type("Dry", (), {"http": dry})())
            ok("баланс без --live: канал чтения — тот же адрес и ключ, отправка разрешена только ему",
               reader.live and not dry.live and reader.base == dry.base and reader.key == dry.key)
            ctx, a = ctx_for("reconcile", ["ledger", "--balance", "--baseline", "100"], channel)
            ctx.ledger.append({"event": "completed", "uid": "done", "base_url": base, "cost_rub": src_cost})
            ctx.ledger.append({"event": "submit", "uid": "running", "base_url": base, "estimate_rub": op_rub})
            code, text = quiet(cmd_ledger, ctx, a)
            ok("сверка с балансом: spentAmount − траты вне журнала = журнал — сходится, код 0",
               code == EXIT_OK and "сходится до копейки" in text and not ctx.live, (code, text))
            a.baseline = 90.0
            code, text = quiet(cmd_ledger, ctx, a)
            ok("сверка с балансом: расхождение — код 1 и разница", code == EXIT_JOB and "РАСХОЖДЕНИЕ +10.00 ₽" in text,
               (code, text))
            r = reconcile(ctx.ledger, base, balance, None)
            ok("сверка с балансом без --baseline: траты вне журнала — в отчёт, резерв незавершённых — отдельно",
               r["ok"] is None and r["ledger"] == src_cost and r["reserved"] == op_rub
               and r["outside"] == 145.0 - src_cost, r)
            r = reconcile(ctx.ledger, base, {"amount": "500.00000000"}, 100.0)
            ok("сверка с балансом: в ответе нет spentAmount — сверить не с чем", r["ok"] is None and bool(r["reason"]), r)

            # сумма журнала: без бюджета — без строки бюджета
            ctx, a = ctx_for("sum-no-budget", ["ledger", "--sum"], {}, budget="0")
            code, text = quiet(cmd_ledger, ctx, a)
            ok("ledger --sum без бюджета: строки бюджета нет", code == EXIT_OK and "потрачено" in text
               and "бюджет" not in text, text)
            ctx, a = ctx_for("sum-budget", ["ledger", "--sum"], {}, budget="300")
            code, text = quiet(cmd_ledger, ctx, a)
            ok("ledger --sum с бюджетом: сумма против бюджета", f"из бюджета {pc.fmt_rub(300)} ₽" in text, text)

            # один файл в двух местах задания — одна загрузка; размер результата — в паспорте
            png = (b"\x89PNG\r\n\x1a\n" + b"\0\0\0\rIHDR" + (16).to_bytes(4, "big") + (9).to_bytes(4, "big")
                   + b"\x08\x02\0\0\0" + b"\0" * 4)
            (tmp / "frame.png").write_bytes(png)
            blobs[cdn + "result.png"] = png
            loop = {"model": model, "tag": "loop", "_dir": str(tmp),
                    "input": {"prompt": "demo loop", "resolution": "1080p", "images": ["frame.png", "frame.png"]}}
            ctx, a = ctx_for("one-upload", ["run", str(job_file), "--live"], {
                ("POST", "/v1/storage/upload"): [{"id": "file_demo", "url": cdn + "stored.png"}],
                ("POST", "/v1/media"): [{"id": "gen_loop", "status": "completed", "data": {"url": cdn + "result.png"},
                                         "usage": {"cost_rub": src_cost}}]})
            prep = prepare(ctx, loop)
            ok("один файл в двух местах: в теле запроса нет base64, оба места ждут загрузки",
               not prep.errors and len(prep.uploads) == 2 and "base64" not in json.dumps(prep.body), prep.issues)
            single = prepare(ctx, {**loop, "input": {**loop["input"], "images": ["frame.png"]}})
            ok("один файл в одном месте: уходит в теле запроса, загрузки нет",
               not single.uploads and single.body["input"]["images"][0]["type"] == "base64", single.uploads)
            code, text = quiet(run_prepared, ctx, prep)
            media = [b for _, p, b in ctx.http.sent if p == "/v1/media"]
            ok("один файл — одна загрузка: хранилище вызвано один раз, оба места — одна ссылка",
               code == EXIT_OK and ctx.http.calls.count(("POST", "/v1/storage/upload")) == 1 and len(media) == 1
               and media[0]["input"]["images"] == [{"type": "url", "data": cdn + "stored.png"}] * 2,
               (code, ctx.http.calls, text))
            done = next((j for j in ctx.ledger.jobs().values() if j.get("id") == "gen_loop"), {})
            pas = json.loads(absp(done["passport"]).read_text(encoding="utf-8")) if done.get("passport") else {}
            size = pas.get("size") or {}
            ok("паспорт: поле size — заказанная ступень и фактический размер файла",
               size.get("requested") == {"resolution": "1080p"}
               and [(s["width"], s["height"]) for s in size.get("actual") or []] == [(16, 9)] and "размер 16×9" in text,
               (size, text))
            jpg = (b"\xff\xd8\xff\xe0\x00\x04\x00\x00\xff\xc0\x00\x11\x08" + (9).to_bytes(2, "big")
                   + (16).to_bytes(2, "big") + b"\0" * 12)
            webp = (b"RIFF\0\0\0\0WEBPVP8X\x0a\0\0\0\0\0\0\0" + (15).to_bytes(3, "little")
                    + (8).to_bytes(3, "little"))
            got = []
            for name, data in (("size.png", png), ("size.jpg", jpg), ("size.webp", webp), ("size.bin", b"not an image")):
                (tmp / name).write_bytes(data)
                got.append(image_size(tmp / name))
            ok("размер по заголовку файла без Pillow: PNG, JPEG, WebP; не картинка — None",
               got == [(16, 9), (16, 9), (16, 9), None], got)
    finally:
        KEY_FILE = key_file
        if env_key is not None:
            os.environ["POLZA_API_KEY"] = env_key
    say(f"# selftest: {sum(checks)}/{len(checks)} PASS")
    return EXIT_OK if all(checks) else EXIT_JOB


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    g = common.add_argument_group("общие")
    g.add_argument("--live", action="store_true", help="реально отправлять запросы (иначе сухой прогон)")
    g.add_argument("--catalog", help="снимок каталога: имя папки в $DDD_HOME/cache/ai-media/polza или путь (по "
                                     "умолчанию POLZA_CATALOG, иначе последний снимок)")
    g.add_argument("--base-url", help="база API (по умолчанию POLZA_BASE_URL или https://polza.ai/api)")
    g.add_argument("--ledger", help="журнал затрат (по умолчанию POLZA_LEDGER, иначе "
                                    "$DDD_HOME/out/ai-media/_ledger.jsonl)")
    g.add_argument("--out", help="корень результатов (по умолчанию POLZA_OUT_ROOT, иначе $DDD_HOME/out/ai-media/_polza); "
                                 "файлы и паспорта — в <корень>/<агент>/<дата>/")
    g.add_argument("--agent", help="агент по умолчанию для заданий без поля agent")
    g.add_argument("--budget-total", type=float, help="общий лимит ₽ по журналу (по умолчанию POLZA_BUDGET_TOTAL, "
                                                      "иначе 2000)")
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
        s.add_argument("job", help="файл задания: .json (объект или массив заданий) или .jsonl (строка — задание); "
                                   "пути файлов в input — от папки этого файла")
        if name == "estimate":
            s.add_argument("--ops", metavar="OP[,OP…]",
                           help="операции над готовым результатом каждого задания (extend, upscale_1080p, upscale_4k): "
                                "строка сметы на операцию, цена операции по каталогу — в сумме")
        if name == "batch":
            s.add_argument("--parallel", type=int, default=2,
                           help="сколько заданий идёт одновременно (по умолчанию 2, не больше 3)")
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
    s.add_argument("--ops", action="store_true", help="сверить записи операций с их сохранёнными ответами: деньги за "
                                                      "операцию, вернувшую исходник, — код выхода 1")
    s.add_argument("--balance", action="store_true",
                   help="сверить журнал с балансом канала (GET /v2/balance: чтение, не трата — без --live): "
                        "spentAmount против суммы журнала")
    s.add_argument("--baseline", type=float, metavar="RUB",
                   help="с --balance: траты ключа вне журнала; расхождение с ними — код выхода 1")
    s.add_argument("--tail", type=int, default=30)
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_ledger)
    s = sp.add_parser("balance", parents=[common])
    s.set_defaults(fn=cmd_balance)
    sp.add_parser("selftest", parents=[common])
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    if a.cmd == "selftest":         # свои каталог, журнал и канал во временной папке: окружение машины не читается
        sys.exit(selftest())
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
