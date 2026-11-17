#!/usr/bin/env python3
"""Checks that every internal link and anchor in docs/ resolves. Exit 1 on any failure."""
import re, sys
from pathlib import Path
from html.parser import HTMLParser
OUT = Path(__file__).resolve().parent / "docs"
class P(HTMLParser):
    def __init__(s): super().__init__(); s.links, s.ids = [], set()
    def handle_starttag(s, tag, a):
        a = dict(a)
        if "id" in a: s.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k): s.links.append(a[k])
pages = {}
for f in OUT.rglob("*.html"):
    p = P(); p.feed(f.read_text()); pages[f.resolve()] = p
bad, n = [], 0
for f, p in pages.items():
    for l in p.links:
        if re.match(r"^(https?:|mailto:|data:|javascript:)", l): continue
        n += 1
        path, _, frag = l.partition("#")
        target = (f.parent / path).resolve() if path else f
        if not target.exists(): bad.append(f"{f.relative_to(OUT.resolve())}: missing {l}"); continue
        if frag and target.suffix == ".html" and frag not in pages[target].ids:
            bad.append(f"{f.relative_to(OUT.resolve())}: missing anchor {l}")
print(f"{len(pages)} pages, {n} internal links checked, {len(bad)} broken")
for b in bad: print("  " + b)
sys.exit(1 if bad else 0)
