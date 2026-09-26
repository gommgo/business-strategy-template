#!/usr/bin/env python3
"""vote_server.py — локальный сервер страницы «Кадр против кадра» (испытание 15-showcase, 25.09.2026).

    python3 vote_server.py [--port 8790] [--dir .]      # только 127.0.0.1

Раздаёт папку страницы (index.html, pairs.json, img/…) и принимает голоса:
  GET  /api/ping                 → {"ok": true}
  GET  /api/votes?voter=ID       → документ голосующего или null
  POST /api/votes {voter, doc}   → пишет votes/<voter>.json (атомарно)
  GET  /api/all                  → {voter: doc, …} — для итогов оркестратора
Голоса лежат в <dir>/votes/*.json.
"""
import json
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ARGS = sys.argv[1:]
PORT = int(ARGS[ARGS.index("--port") + 1]) if "--port" in ARGS else 8790
ROOT = os.path.abspath(ARGS[ARGS.index("--dir") + 1]) if "--dir" in ARGS else os.path.dirname(os.path.abspath(__file__))
VOTES = os.path.join(ROOT, "votes")
SAFE = re.compile(r"^[A-Za-z0-9_.:@+-]{1,120}$")


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def _json(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def guess_type(self, path):
        # страница без своего <meta charset> (его ставит обёртка при публикации) — кодировку сообщает сервер
        t = super().guess_type(path)
        if t in ("text/html", "application/json", "text/javascript", "application/javascript", "text/css", "text/plain"):
            return t + "; charset=utf-8"
        return t

    def end_headers(self):
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/ping":
            return self._json(200, {"ok": True})
        if u.path == "/api/votes":
            voter = (parse_qs(u.query).get("voter") or [""])[0]
            if not SAFE.match(voter):
                return self._json(400, {"error": "bad voter"})
            p = os.path.join(VOTES, voter + ".json")
            return self._json(200, json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None)
        if u.path == "/api/all":
            out = {}
            if os.path.isdir(VOTES):
                for f in sorted(os.listdir(VOTES)):
                    if f.endswith(".json"):
                        out[f[:-5]] = json.load(open(os.path.join(VOTES, f), encoding="utf-8"))
            return self._json(200, out)
        return super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/api/votes":
            return self._json(404, {"error": "not found"})
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > 512 * 1024:
            return self._json(413, {"error": "size"})
        try:
            body = json.loads(self.rfile.read(n).decode("utf-8"))
            voter, doc = body["voter"], body["doc"]
        except Exception:
            return self._json(400, {"error": "bad json"})
        if not SAFE.match(str(voter)) or not isinstance(doc, dict):
            return self._json(400, {"error": "bad voter or doc"})
        os.makedirs(VOTES, exist_ok=True)
        p = os.path.join(VOTES, voter + ".json")
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        os.replace(tmp, p)
        return self._json(200, {"ok": True})

    def log_message(self, fmt, *a):
        if "/api/" in (a[0] if a else ""):
            sys.stderr.write("[vote] " + (fmt % a) + "\n")


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"vote_server: http://127.0.0.1:{PORT}/  (папка {ROOT})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
