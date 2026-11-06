#!/usr/bin/env python3
"""Build a compact index (name\tdesc\tpath) of all SKILL.md files. Stdlib only."""
import json, os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "..", "config.json")
CACHE = os.path.expanduser("~/.cache/skill-stack")
INDEX = os.path.join(CACHE, "index.tsv")
STAMP = os.path.join(CACHE, "stamp.json")


def load_cfg():
    with open(CFG, encoding="utf-8") as f:
        return json.load(f)


def roots(cfg):
    out = []
    for p in cfg["paths"]:
        p = os.path.abspath(os.path.expanduser(p))
        if os.path.isdir(p) and p not in out:
            out.append(p)
    return out


def fingerprint(rs):
    # cheap: mtime of each root + its direct children (skill dirs)
    fp = {}
    for r in rs:
        try:
            m = os.stat(r).st_mtime
            for e in os.scandir(r):
                if e.is_dir():
                    m = max(m, e.stat().st_mtime)
            fp[r] = m
        except OSError:
            pass
    return fp


def parse(path, limit):
    name = desc = ""
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            head = f.read(4000)
    except OSError:
        return None
    m = re.match(r"^---\s*\n(.*?)\n---", head, re.S)
    if m:
        fm = m.group(1)
        n = re.search(r"^name:\s*(.+)$", fm, re.M)
        d = re.search(r"^description:\s*(.+)$", fm, re.M)
        name = n.group(1).strip().strip("\"'") if n else ""
        desc = d.group(1).strip().strip("\"'") if d else ""
    if not name:
        name = os.path.basename(os.path.dirname(path))
    desc = re.sub(r"\s+", " ", desc)[:limit]
    return name, desc


def build(force=False):
    cfg = load_cfg()
    rs = roots(cfg)
    fp = fingerprint(rs)
    if not force and os.path.exists(INDEX) and os.path.exists(STAMP):
        try:
            with open(STAMP) as f:
                if json.load(f) == fp:
                    return INDEX, False
        except Exception:
            pass
    os.makedirs(CACHE, exist_ok=True)
    seen, rows = set(), []
    for r in rs:
        for dp, dns, fns in os.walk(r, followlinks=True):
            dns[:] = [d for d in dns if d not in ("node_modules", ".git", "__pycache__")]
            if "SKILL.md" in fns:
                p = os.path.join(dp, "SKILL.md")
                real = os.path.realpath(p)
                if real in seen:
                    continue
                seen.add(real)
                res = parse(p, cfg.get("desc_chars", 160))
                if res:
                    rows.append(f"{res[0]}\t{res[1]}\t{dp}".replace("\n", " "))
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))
    with open(STAMP, "w") as f:
        json.dump(fp, f)
    return INDEX, True


if __name__ == "__main__":
    idx, rebuilt = build("--force" in sys.argv)
    n = sum(1 for _ in open(idx, encoding="utf-8")) if os.path.getsize(idx) else 0
    print(f"{'rebuilt' if rebuilt else 'cached'}: {n} skills -> {idx}")
