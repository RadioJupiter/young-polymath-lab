"""Build one short review sheet per lesson into docs/printables/.

Each sheet is one page (at most two) and only practices what that lesson taught:
the Remember card, the Check questions, and a few matching practice items.
No combined unit packets. Answer keys stay on the day's key page, not on the sheet.
"""
from __future__ import annotations
import json, re, html
from pathlib import Path

SEC_RE = re.compile(r"^## (.+?)\s*\{#([a-z0-9-]+)\}\s*$", re.M)
ITEM_RE = re.compile(r"^\s*\d+\.\s+(.*?)(?=^\s*\d+\.\s+|\Z)", re.M | re.S)


def split_title(text: str):
    lines = text.strip().splitlines()
    return lines[0][2:].strip(), "\n".join(lines[1:])


def parse_day(path: Path):
    title, rest = split_title(path.read_text())
    m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->", rest, re.S)
    if m:
        rest = rest[m.end():]
    parts = SEC_RE.split(rest)
    secs = []
    for i in range(1, len(parts), 3):
        name, sid, body = parts[i], parts[i + 1], parts[i + 2]
        lesson, _, key = body.partition("### Answer key")
        secs.append({"name": name.strip(), "id": sid, "lesson": lesson, "key": key.strip()})
    return title, secs


def _inner_div(lesson: str, cls: str) -> str:
    m = re.search(rf'<div class="{cls}"[^>]*>(.*?)</div>', lesson, re.S)
    return m.group(1).strip() if m else ""


def remember_text(lesson: str) -> str:
    inner = _inner_div(lesson, "remember")
    if not inner:
        return ""
    inner = re.sub(r'<p class="kicker">Remember</p>\s*', "", inner, count=1)
    return inner.strip()


def numbered_items(text: str) -> list[str]:
    if not text:
        return []
    items = []
    for m in ITEM_RE.finditer(text):
        item = m.group(1).strip()
        item = re.sub(r"\n+", " ", item)
        item = re.sub(r"<[^>]+>", "", item)
        item = re.sub(r"\s+", " ", item).strip()
        if item:
            items.append(item)
    return items


def check_items(lesson: str) -> list[str]:
    inner = _inner_div(lesson, "check")
    inner = re.sub(r"<h3>Check</h3>\s*", "", inner)
    inner = re.sub(r"<p>These questions.*?</p>\s*", "", inner)
    return numbered_items(inner)


def practice_items(lesson: str) -> list[str]:
    m = re.search(r"\n### (?:Practice|Exercises|Unit check|Two-week check)\b(.*)$", lesson, re.S)
    if not m:
        return []
    return numbered_items(m.group(1))


def review_items(lesson: str, limit: int = 6) -> list[str]:
    checks = check_items(lesson)
    practice = practice_items(lesson)
    items = list(checks)
    for p in practice:
        if len(items) >= limit:
            break
        # Skip a practice item that already appeared as a check (same start).
        if any(p[:40] == c[:40] for c in checks):
            continue
        items.append(p)
    return items[:limit]


def md_lite(text: str) -> str:
    """Very small markdown-to-HTML for Remember cards (emphasis and inline code)."""
    if not text:
        return ""
    s = html.escape(re.sub(r"<[^>]+>", "", text))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = s.replace("\n\n", "</p><p>").replace("\n", " ")
    return f"<p>{s}</p>"


def fmt_item(text: str) -> str:
    s = html.escape(text)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def item_box(n: int, text: str, tall: bool = False) -> str:
    low = text.lower()
    asks_draw = any(w in low for w in ("draw ", "draw a", "draw the", "bar model", "on a chart", "on a place-value", "graph"))
    if tall or asks_draw or len(text) > 220:
        kind = "work tall"
    else:
        kind = "work short"
    return f'<div class="item"><p><strong>{n}.</strong> {fmt_item(text)}</p><div class="{kind}"></div></div>\n'


def sheet_html(site_title: str, day_title: str, day_id: str, sec: dict, items: list[str], remember: str, css_href: str) -> str:
    title = sec["name"]
    banner = (
        "Review sheet — use this after the lesson. These questions practice only "
        "what this lesson taught. Answers are on the day's answer-key page, not here."
    )
    rem = f'<div class="remember"><p class="kicker">Remember</p>{md_lite(remember)}</div>' if remember else ""
    if items:
        body_items = "".join(item_box(i, t) for i, t in enumerate(items, 1))
    else:
        body_items = (
            '<p>This lesson\'s work is the task on the lesson page. Use this sheet only '
            "to write the Remember card in your own words and to note one example you can still do.</p>"
            '<div class="work tall"></div>'
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Review · {html.escape(title)} · {html.escape(site_title)}</title>
<link rel="stylesheet" href="{css_href}">
</head><body>
<div class="toolbar">
  <button type="button" onclick="window.print()">Print</button>
  <a href="index.html">All review sheets</a>
  · <a href="../days/{html.escape(day_id)}.html#{html.escape(sec['id'])}">Back to the lesson</a>
  · <a href="../keys/{html.escape(day_id)}.html#{html.escape(sec['id'])}">Answer key</a>
</div>
<article class="sheet">
  <header class="hd">
    <div>
      <h1>{html.escape(title)}</h1>
      <p class="sub">{html.escape(day_title)} · one-lesson review</p>
    </div>
  </header>
  <p class="review-banner">{banner}</p>
  <div class="meta-line"><span>Name</span><span>Date</span></div>
  {rem}
  {body_items}
  <p class="guide">Work in writing. Then mark from the answer key and rework every miss the next day.</p>
</article>
</body></html>
"""


def build_printables(site, src: Path, out: Path, page_fn):
    pdir = out / "printables"
    pdir.mkdir(parents=True, exist_ok=True)
    # CSS lives in assets/; sheets sit one level below docs/
    css_href = "../assets/print-sheet.css"
    site_title = site["title"]
    groups = []
    total = 0
    for f in site["days"]:
        path = src / "days" / f"{f}.md"
        day_title, secs = parse_day(path)
        links = []
        for sec in secs:
            items = review_items(sec["lesson"])
            rem = remember_text(sec["lesson"])
            fname = f"{f}-{sec['id']}.html"
            (pdir / fname).write_text(
                sheet_html(site_title, day_title, f, sec, items, rem, css_href),
                encoding="utf-8",
            )
            links.append((fname, sec["name"], len(items)))
            total += 1
        groups.append((f, day_title, links))

    index_bits = [
        f"<h1>Review sheets</h1>",
        "<p>Each lesson has its own short review sheet (one page, at most two). "
        "Use it after the lesson, for retention. It practices only what that lesson taught. "
        "There are no combined unit packets. Answer keys stay on each day's key page.</p>",
    ]
    for day_id, day_title, links in groups:
        index_bits.append(f'<h2><a href="../days/{html.escape(day_id)}.html">{html.escape(day_title)}</a></h2>')
        index_bits.append("<ul>")
        for fname, name, n in links:
            label = f"{name} — review sheet"
            index_bits.append(
                f'<li><a href="{html.escape(fname)}">{html.escape(label)}</a></li>'
            )
        index_bits.append("</ul>")
    (pdir / "index.html").write_text(page_fn("Review sheets", "\n".join(index_bits), 1), encoding="utf-8")
    print(f"printables: {total} review sheets in {pdir}")
