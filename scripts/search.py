#!/usr/bin/env python3
"""Rank indexed skills by keywords (BM25-lite). Prints only top-N lines.
Usage: search.py kw1 kw2 ... [--top 8] [--full]"""
import math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_index import build, load_cfg  # noqa: E402

TOK = re.compile(r"[a-zа-яё0-9]+", re.I)


def toks(s):
    return [t.lower() for t in TOK.findall(s)]


def stem(t):
    for suf in ("ing", "ers", "er", "es", "s", "ed"):
        if len(t) > len(suf) + 3 and t.endswith(suf):
            return t[: -len(suf)]
    return t


def main():
    args = sys.argv[1:]
    top = load_cfg().get("top", 8)
    full = "--full" in args
    if "--top" in args:
        i = args.index("--top")
        top = int(args[i + 1])
        del args[i : i + 2]
    kws = [stem(t) for a in args if not a.startswith("--") for t in toks(a)]
    if not kws:
        print("usage: search.py kw1 kw2 ... [--top N]")
        return
    idx, _ = build()
    rows = []
    with open(idx, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) == 3:
                rows.append(p)
    N = len(rows) or 1
    docs = []
    df = {}
    for name, desc, path in rows:
        nt = [stem(t) for t in toks(name.replace("-", " "))]
        dt = [stem(t) for t in toks(desc)]
        docs.append((nt, dt))
        for t in set(nt + dt):
            df[t] = df.get(t, 0) + 1
    scored = []
    for (nt, dt), row in zip(docs, rows):
        s, hit = 0.0, 0
        for k in set(kws):
            idf = math.log(1 + N / (1 + df.get(k, 0)))
            tf_n = sum(1 for t in nt if t == k or (len(k) > 3 and t.startswith(k)))
            tf_d = sum(1 for t in dt if t == k or (len(k) > 3 and t.startswith(k)))
            if tf_n or tf_d:
                hit += 1
                s += idf * (3.0 * min(tf_n, 2) + min(tf_d, 3) / (1 + 0.02 * len(dt)) * 2)
        if s:
            s *= 1 + 0.3 * (hit - 1)  # reward covering several keywords
            scored.append((s, row))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print(f"no local matches among {len(rows)} skills")
        return
    print(f"# {len(scored)} matches / {len(rows)} skills; top {min(top, len(scored))}")
    for s, (name, desc, path) in scored[:top]:
        d = desc if full else desc[:110]
        print(f"{name} | {d} | {path}")


if __name__ == "__main__":
    main()
