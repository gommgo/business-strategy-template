#!/usr/bin/env python3
"""kbpaths — пути скилла design-deep-dive и окружения его утилит. Только стандартная библиотека.

Утилиты скилла находят базу, соседние утилиты, данные, выходы, блокировки, бинарники и ключи через этот модуль, а не
через пути, зашитые в код. Корень скилла вычисляется от этого файла (`scripts/lib/kbpaths.py` → два уровня вверх),
поэтому скилл работает в любом клоне шаблона. Окружение (venv, npm, бинарники, модели, браузеры, выходы, блокировки)
живёт вне репозитория: `$DDD_HOME`, иначе `$XDG_CACHE_HOME/design-deep-dive`, иначе `~/.cache/design-deep-dive` —
одно на машину для всех клонов.

Подключение в утилите `scripts/<домен>/<утилита>.py`:

    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
    import kbpaths

    kbpaths.kb("site", "02-site-types", "vocabulary.yaml")   # файл базы site
    kbpaths.use("ui"); import ui_audit                          # модуль соседнего домена
    kbpaths.out("creative", "audit")                            # каталог выходов (создаётся)
    with kbpaths.lock("browser"): ...                           # общая блокировка браузера, с ожиданием

Диагностика: `python3 kbpaths.py` — где что лежит; `python3 kbpaths.py --selftest` — самопроверка без сети.
"""
import contextlib
import fcntl
import os
import shutil
import sys
import time
from pathlib import Path

LIB = Path(__file__).resolve().parent                  # .../design-deep-dive/scripts/lib
SCRIPTS = LIB.parent                                    # .../design-deep-dive/scripts
SKILL = SCRIPTS.parent                                  # .../.claude/skills/design-deep-dive
KB = SKILL / "kb"
ASSETS = SKILL / "assets"

BASES = ("ux", "ui", "site", "text", "creative", "ai-media", "blender", "claude-design")
DOMAINS = BASES + ("lib", "maint", "tests")            # папки scripts/
OLD_SUFFIX = "-research"                                # имена баз в источнике: <база>-research

ENV_HOME = "DDD_HOME"
ENV_BIN = {                                             # переопределение пути к бинарнику (иначе $DDD_HOME/bin, затем PATH)
    "blender": "DDD_BLENDER",
    "node": "DDD_NODE",
    "npx": "DDD_NPX",
    "npm": "DDD_NPM",
    "ffmpeg": "DDD_FFMPEG",
    "ffprobe": "DDD_FFPROBE",
    "brave": "DDD_BRAVE",
    "chromium": "DDD_CHROMIUM",
}


# ------------------------------------------------------------------ имена

def base_name(name):
    """Имя базы в раскладке скилла: «site-research» → «site»; неизвестное имя — ValueError."""
    n = str(name).strip().strip("/")
    if n.endswith(OLD_SUFFIX):
        n = n[: -len(OLD_SUFFIX)]
    if n not in BASES:
        raise ValueError(f"неизвестная база: {name!r} (есть: {', '.join(BASES)})")
    return n


def domain_name(name):
    n = str(name).strip().strip("/")
    if n.endswith(OLD_SUFFIX):
        n = n[: -len(OLD_SUFFIX)]
    if n not in DOMAINS:
        raise ValueError(f"неизвестный домен scripts/: {name!r} (есть: {', '.join(DOMAINS)})")
    return n


# ------------------------------------------------------------------ скилл и репозиторий

def skill(*parts):
    """Корень скилла `.claude/skills/design-deep-dive/` (+ части пути)."""
    return SKILL.joinpath(*parts)


def repo(*parts):
    """Корень репозитория шаблона: skill → skills → .claude → корень."""
    return SKILL.parents[2].joinpath(*parts)


def kb(base=None, *parts):
    """База знаний: kb() — `kb/`, kb("site", "04-blocks", "blocks.yaml") — файл базы. Принимает и «site-research»."""
    if base is None:
        return KB.joinpath(*parts)
    return KB.joinpath(base_name(base), *parts)


def scripts(domain=None, *parts):
    """Утилиты: scripts() — `scripts/`, scripts("ai-media", "page_accept.py") — файл утилиты домена."""
    if domain is None:
        return SCRIPTS.joinpath(*parts)
    return SCRIPTS.joinpath(domain_name(domain), *parts)


def data(domain, *parts):
    """Данные, которые читает только код: `scripts/<домен>/data/…`."""
    return scripts(domain, "data", *parts)


def assets(*parts):
    """Ассеты скилла (`assets/calibration/…`)."""
    return ASSETS.joinpath(*parts)


def use(domain):
    """Подключить модули соседнего домена: добавить `scripts/<домен>/` в sys.path (один раз). Возвращает путь."""
    p = str(scripts(domain))
    if p not in sys.path:
        sys.path.insert(0, p)
    return Path(p)


# ------------------------------------------------------------------ окружение вне репозитория

def home(*parts):
    """Домашний каталог окружения: $DDD_HOME → $XDG_CACHE_HOME/design-deep-dive → ~/.cache/design-deep-dive."""
    h = os.environ.get(ENV_HOME)
    if h:
        base = Path(h).expanduser()
    else:
        xdg = os.environ.get("XDG_CACHE_HOME")
        base = (Path(xdg).expanduser() if xdg else Path.home() / ".cache") / "design-deep-dive"
    return base.joinpath(*parts)


def _dir(p, create):
    if create:
        p.mkdir(parents=True, exist_ok=True)
    return p


def venv(*parts):
    return home("venv", *parts)


def python():
    """Python окружения скилла (venv с зависимостями), иначе текущий интерпретатор."""
    p = venv("bin", "python")
    return str(p) if p.exists() else sys.executable


def node_home(*parts):
    """Каталог npm-зависимостей: `$DDD_HOME/node/` (package.json скилла ставится сюда)."""
    return home("node", *parts)


def node_modules(*parts):
    return node_home("node_modules", *parts)


def bin_dir(*parts):
    """Бинарники, которые ставит install.sh: `$DDD_HOME/bin/`."""
    return home("bin", *parts)


def models(*parts):
    """Модели ONNX: `$DDD_HOME/models/`."""
    return home("models", *parts)


def browsers():
    """Браузеры Playwright, если их ставил install.sh: `$DDD_HOME/browsers/`."""
    return home("browsers")


def out(domain, *parts, create=True):
    """Каталог выходов утилиты: `$DDD_HOME/out/<домен>/…` (создаётся). Вместо `<база>/99-raw/cache/…` источника."""
    return _dir(home("out", domain_name(domain), *parts), create)


def cache(domain, *parts, create=True):
    """Каталог кэша утилиты (снимки каталогов, ответы API): `$DDD_HOME/cache/<домен>/…` (создаётся)."""
    return _dir(home("cache", domain_name(domain), *parts), create)


# ------------------------------------------------------------------ блокировки

def locks_dir(create=True):
    return _dir(home("locks"), create)


def lock_path(name="browser", domain=None):
    """Файл блокировки. Общая (вместо `app-design/.locks/<name>.lock`): lock_path("browser") →
    `$DDD_HOME/locks/browser.lock`. Своя у домена (вместо `<база>/99-raw/tools/.locks/<name>.lock`):
    lock_path("browser", "site") → `$DDD_HOME/locks/site/browser.lock` — имя файла то же, что в источнике."""
    d = locks_dir()
    if domain is not None:
        d = _dir(d / domain_name(domain), True)
    return str(d / f"{name}.lock")


@contextlib.contextmanager
def lock(name="browser", domain=None, timeout=900.0, poll=0.5):
    """Исключительная блокировка flock с ожиданием (до timeout секунд, затем TimeoutError); None — ждать без предела."""
    path = lock_path(name, domain)
    f = open(path, "a")
    t0 = time.monotonic()
    try:
        while True:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if timeout is not None and time.monotonic() - t0 > timeout:
                    raise TimeoutError(f"{path} занят дольше {timeout:.0f} с")
                time.sleep(poll)
        yield path
    finally:
        try:
            fcntl.flock(f, fcntl.LOCK_UN)
        finally:
            f.close()


# ------------------------------------------------------------------ бинарники, Node, Playwright, ключи

def which(name, env=None, names=()):
    """Путь к бинарнику: переменная окружения (env или DDD_<ИМЯ> из ENV_BIN) → `$DDD_HOME/bin/<имя>` или
    `$DDD_HOME/bin/<имя>/<имя>` → `$DDD_HOME/node/node_modules/.bin/<имя>` → PATH. Не найден — возвращает имя как есть:
    ошибка проявится при вызове, а импорт и --help утилиты работают без бинарника."""
    var = env or ENV_BIN.get(name)
    if var and os.environ.get(var):
        return os.environ[var]
    for n in (name,) + tuple(names):
        for cand in (bin_dir(n), bin_dir(n, n), node_modules(".bin", n)):
            if cand.is_file() and os.access(cand, os.X_OK):
                return str(cand)
        p = shutil.which(n)
        if p:
            return p
    return name


def blender():
    return which("blender")


def node():
    return which("node")


def npx():
    return which("npx")


def ffmpeg():
    return which("ffmpeg")


def ffprobe():
    return which("ffprobe")


def brave():
    return which("brave", names=("brave-browser", "brave-browser-stable"))


def node_env(env=None):
    """Окружение для вызова node/npx: PATH с каталогом node и `node_modules/.bin` скилла, NODE_PATH на node_modules."""
    e = dict(os.environ if env is None else env)
    extra = [str(node_modules(".bin"))]
    n = node()
    if os.sep in n:
        extra.append(os.path.dirname(n))
    e["PATH"] = os.pathsep.join(extra + [e.get("PATH", "")])
    e.setdefault("NODE_PATH", str(node_modules()))
    return e


def playwright_env(env=None):
    """Окружение для Playwright: PLAYWRIGHT_BROWSERS_PATH на `$DDD_HOME/browsers`, если браузеры поставлены туда
    и переменная не задана; иначе Playwright ищет браузеры в своём месте по умолчанию."""
    e = dict(os.environ if env is None else env)
    b = browsers()
    if "PLAYWRIGHT_BROWSERS_PATH" not in e and b.is_dir():
        e["PLAYWRIGHT_BROWSERS_PATH"] = str(b)
    return e


def key(name, required=False):
    """Ключ API — только из переменной окружения владельца (в репозитории ключей нет, Р53)."""
    v = os.environ.get(name)
    if required and not v:
        raise SystemExit(f"нет ключа: задайте переменную окружения {name}")
    return v


def _init_env():
    b = browsers()
    if "PLAYWRIGHT_BROWSERS_PATH" not in os.environ and b.is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(b)


_init_env()


# ------------------------------------------------------------------ диагностика

def describe():
    rows = [("skill", SKILL), ("repo", repo()), ("kb", KB), ("scripts", SCRIPTS), ("home", home()),
            ("python", python()), ("node_modules", node_modules()), ("bin", bin_dir()), ("models", models()),
            ("browsers", browsers()), ("locks", home("locks")), ("out", home("out")), ("cache", home("cache"))]
    for b in BASES:
        rows.append((f"kb/{b}", kb(b)))
    for n in ("blender", "node", "npx", "ffmpeg", "ffprobe", "brave"):
        rows.append((n, which(n) if n != "brave" else brave()))
    return rows


def _selftest():
    import tempfile
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    check("корень скилла от файла: scripts/lib → skill", LIB.name == "lib" and SCRIPTS.name == "scripts")
    check("kb('site-research') == kb('site')", kb("site-research") == kb("site") == KB / "site")
    try:
        kb("kimi")
        check("неизвестная база — ValueError", False)
    except ValueError:
        check("неизвестная база — ValueError", True)
    check("scripts('ai-media', 'x.py')", scripts("ai-media", "x.py") == SCRIPTS / "ai-media" / "x.py")
    check("data('blender')", data("blender") == SCRIPTS / "blender" / "data")
    with tempfile.TemporaryDirectory() as td:
        old = os.environ.get(ENV_HOME)
        os.environ[ENV_HOME] = td
        try:
            check("DDD_HOME переопределяет home()", home() == Path(td))
            check("out() создаёт каталог", out("ui", "audit").is_dir())
            check("cache() создаёт каталог", cache("ai-media", "polza").is_dir())
            check("lock_path общая", lock_path() == str(Path(td) / "locks" / "browser.lock"))
            check("lock_path домена (имя файла как в источнике)",
                  lock_path("browser", "site") == str(Path(td) / "locks" / "site" / "browser.lock"))
            with lock("browser", timeout=5) as p:
                check("lock() берёт блокировку", os.path.exists(p))
            os.environ["DDD_BLENDER"] = "/nonexistent/blender"
            check("DDD_BLENDER переопределяет поиск", blender() == "/nonexistent/blender")
            del os.environ["DDD_BLENDER"]
            check("не найденный бинарник — имя как есть", which("ddd-no-such-binary") == "ddd-no-such-binary")
        finally:
            if old is None:
                os.environ.pop(ENV_HOME, None)
            else:
                os.environ[ENV_HOME] = old
    check("key() без переменной — None", key("DDD_NO_SUCH_KEY_FOR_TEST") is None)
    before = list(sys.path)
    use("ui")
    check("use('ui') добавляет scripts/ui в sys.path", str(SCRIPTS / "ui") in sys.path)
    sys.path[:] = before
    print("kbpaths selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(_selftest())
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print(__doc__)
        sys.exit(0)
    for k, v in describe():
        print(f"{k:<16} {v}")
