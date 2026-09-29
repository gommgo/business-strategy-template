#!/usr/bin/env python3
"""Контекст фоновых агентов по их журналам JSONL (Р201): печатает только числа, содержимое журнала в вывод не идёт.
  ctxwatch.py once ИМЯ=ФАЙЛ …            — текущий контекст каждого
  ctxwatch.py watch ПОРОГ ИМЯ=ФАЙЛ …     — строка события, когда контекст агента ≥ ПОРОГ (один раз на агента)
ФАЙЛ — output_file из ответа Agent о запуске (`…/tasks/<agentId>.output`). Оркестратор держит `watch 940000 …` под
Monitor, пока агенты работают; на событии — SendMessage агенту: зафиксировать результат в отчёте и завершиться.
"""
import json, os, sys, time

def ctx(path):
    """Контекст последнего ответа модели: input + cache_creation + cache_read."""
    try:
        size = os.path.getsize(path)
    except OSError:
        return None
    with open(path, "rb") as f:
        f.seek(max(0, size - 2_000_000))
        tail = f.read().decode("utf-8", "replace").splitlines()
    for line in reversed(tail):
        if '"usage"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        u = (d.get("message") or {}).get("usage") or d.get("usage")
        if isinstance(u, dict) and "input_tokens" in u:
            return (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + \
                   (u.get("cache_read_input_tokens") or 0)
    return None

def pairs(args):
    return [a.split("=", 1) for a in args]

if sys.argv[1] == "once":
    for name, p in pairs(sys.argv[2:]):
        print(f"{name}: {ctx(p)}")
else:
    limit = int(sys.argv[2]); agents = pairs(sys.argv[3:]); fired = set()
    while len(fired) < len(agents):
        for name, p in agents:
            if name in fired:
                continue
            c = ctx(p)
            if c is not None and c >= limit:
                print(f"КОНТЕКСТ {name}: {c} ≥ {limit}", flush=True); fired.add(name)
        time.sleep(30)
