#!/usr/bin/env python3
"""Static site builder. Reads content/ and writes the finished site to docs/.

Content model
  content/site.json        site title, navigation, timetable, list of day files
  content/pages/*.md       standalone pages (first line '# Title')
  content/days/dNN.md      one school day: '# Title', then one '## Section {#id}'
                           per lesson. Everything after a '### Answer key' heading
                           inside a section goes to the separate key page.
Usage: python3 build.py   (needs the 'markdown' package: pip install -r requirements.txt)
"""
import json, re, shutil, html
from pathlib import Path
import markdown
import printables

ROOT = Path(__file__).resolve().parent
SRC, OUT = ROOT / "content", ROOT / "docs"
site = json.loads((SRC / "site.json").read_text())
MD_EXT = ["tables", "fenced_code", "attr_list", "md_in_html", "sane_lists", "footnotes"]


VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SKIP_MD_TAGS = {"svg", "script", "style", "pre", "code", "textarea", "math"}
CONTENT_DIV_RE = re.compile(r'\bclass\s*=\s*["\']([^"\']*)["\']')
CONTENT_DIV_CLASSES = {"learn", "remember", "watch", "together", "check", "note", "pic-cap"}
INNER_MD_TAGS = {"p", "li", "td", "th", "ol", "ul", "details", "summary", "blockquote"}
BLOCK_OPEN = re.compile(r'(>)([^\S\n]*)(<(?:div|ol|ul|table|details|svg|blockquote|section|article|aside|p|h1|h2|h3|h4|h5|h6)\b)', re.I)
_OPEN_OR_CLOSE = re.compile(
    r"(?s)<!--.*?-->|<!\[CDATA\[.*?\]\]>|</([A-Za-z][\w:.-]*)\s*>|<([A-Za-z][\w:.-]*)(\s[^>]*?)?\s*/?>"
)

_MD_MARK = re.compile(r"\*\*|`")

def _has_md_markup(s: str) -> bool:
    return bool(_MD_MARK.search(s or ""))

def _div_needs_md(attrs: str) -> bool:
    if re.search(r'\bdata-listen\b', attrs or ""):
        return True
    m = CONTENT_DIV_RE.search(attrs or "")
    if not m:
        return False
    classes = set(m.group(1).split())
    return bool(classes & CONTENT_DIV_CLASSES)

def _isolate_block_html(text: str) -> str:
    """Put glued block-level tags on their own line so md_in_html does not wrap them in <p>."""
    return BLOCK_OPEN.sub(r'>\n\3', text)

def enable_md_in_html(text: str) -> str:
    """Add markdown=\"1\" so Python-Markdown's md_in_html extension renders emphasis,
    lists and inline code inside raw HTML wrappers (learn/watch/together/details, etc.).
    Decorative diagrams (number bonds, discs, bar models, SVG) are left alone."""
    text = _isolate_block_html(text)
    skip = []
    out = []
    pos = 0
    for m in _OPEN_OR_CLOSE.finditer(text):
        out.append(text[pos:m.start()])
        token = m.group(0)
        pos = m.end()
        if token.startswith("<!--") or token.startswith("<![CDATA"):
            out.append(token)
            continue
        if token.startswith("</"):
            name = m.group(1).lower()
            if skip and skip[-1] == name:
                skip.pop()
            out.append(token)
            continue
        name = m.group(2).lower()
        attrs = m.group(3) or ""
        self_closing = token.rstrip().endswith("/>") or name in VOID_TAGS
        if skip:
            out.append(token)
            if not self_closing and name in SKIP_MD_TAGS:
                skip.append(name)
            continue
        if name in SKIP_MD_TAGS and not self_closing:
            skip.append(name)
            out.append(token)
            continue
        needs = False
        if name == "div" and _div_needs_md(attrs):
            needs = True
        elif name in INNER_MD_TAGS:
            needs = True
        if needs and not self_closing and not re.search(r'\bmarkdown\s*=', attrs, re.I):
            core = token[:-1].rstrip()
            out.append(core + ' markdown="1">')
            continue
        out.append(token)
    out.append(text[pos:])
    return "".join(out)

def md(text):
    html = markdown.markdown(enable_md_in_html(text), extensions=MD_EXT, output_format="html5")
    # md_in_html strips this attribute when it processes a tag; remove any leftover.
    return re.sub(r'\smarkdown="1"', "", html)

def page(title, body, depth=0, extra_head=""):
    pre = "../" * depth
    nav = "".join(f'<a href="{pre}{href}">{html.escape(label)}</a>' for label, href in site["nav"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{html.escape(title)} · {html.escape(site['title'])}</title>
<link rel="stylesheet" href="{pre}assets/style.css">{extra_head}
</head><body data-site="{site['storage_key']}" data-root="{pre}">
<header class="top"><a class="brand" href="{pre}index.html">{html.escape(site['title'])}</a>
<nav>{nav}</nav></header>
<main>{body}</main>
<footer><p>{site['footer']}</p></footer>
<script src="{pre}assets/days.js"></script><script src="{pre}assets/app.js"></script><script src="{pre}assets/listen.js"></script>
</body></html>"""

def split_title(text):
    lines = text.strip().splitlines()
    assert lines[0].startswith("# "), "first line must be '# Title'"
    return lines[0][2:].strip(), "\n".join(lines[1:])

SEC_RE = re.compile(r"^## (.+?)\s*\{#([a-z0-9-]+)\}\s*$", re.M)

def parse_day(path):
    title, rest = split_title(path.read_text())
    meta = {}
    m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->", rest, re.S)
    if m:
        meta = json.loads(m.group(1)); rest = rest[m.end():]
    parts = SEC_RE.split(rest)
    intro, secs = parts[0], []
    for i in range(1, len(parts), 3):
        name, sid, body = parts[i], parts[i + 1], parts[i + 2]
        lesson, _, key = body.partition("### Answer key")
        secs.append({"name": name.strip(), "id": sid, "lesson": lesson, "key": key.strip()})
    return title, meta, intro, secs

def build():
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT / "days").mkdir(parents=True); (OUT / "keys").mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")
    days = []
    for f in site["days"]:
        p = SRC / "days" / f"{f}.md"
        title, meta, intro, secs = parse_day(p)
        days.append({"id": f, "title": title, "meta": meta,
                     "sections": [{"id": f"{f}-{s['id']}", "name": s["name"]} for s in secs]})
        crumbs = f'<p class="crumbs"><a href="../index.html">Home</a> · <a href="../today.html">Today</a> · <a href="../keys/{f}.html">Answer keys for this day</a>'
        if site.get("has_printables"):
            crumbs += ' · <a href="../printables/index.html">Review sheets</a>'
        crumbs += "</p>"
        body = [crumbs,
                f"<h1>{html.escape(title)}</h1>", md(intro)]
        body.append('<nav class="toc">' + "".join(f'<a href="#{s["id"]}">{html.escape(s["name"])}</a>' for s in secs) + "</nav>")
        kbody = [f'<p class="crumbs"><a href="../days/{f}.html">Back to the lessons</a></p>',
                 f"<h1>Answer keys · {html.escape(title)}</h1>",
                 '<p class="note">Attempt every exercise in writing before opening this page. Mark your work, then rework every miss from scratch the next day.</p>']
        for s in secs:
            uid = f"{f}-{s['id']}"
            review = (f'<p class="keylink"><a href="../printables/{f}-{s["id"]}.html">Review sheet for this lesson</a> (one page, only what this lesson taught)</p>'
                      if site.get("has_printables") else "")
            body.append(f'<section class="lesson" id="{s["id"]}"><div class="lesson-head"><h2>{html.escape(s["name"])}</h2>'
                        f'<label class="done"><input type="checkbox" data-done="{uid}"> Done</label></div>'
                        f'{md(s["lesson"])}'
                        + review
                        + (f'<p class="keylink"><a href="../keys/{f}.html#{s["id"]}">Answer key →</a></p>' if s["key"] else "")
                        + "</section>")
            if s["key"]:
                kbody.append(f'<section class="lesson key" id="{s["id"]}"><h2>{html.escape(s["name"])}</h2>{md(s["key"])}</section>')
        (OUT / "days" / f"{f}.html").write_text(page(title, "\n".join(body), 1))
        (OUT / "keys" / f"{f}.html").write_text(page("Key · " + title, "\n".join(kbody), 1))
    (OUT / "assets" / "days.js").write_text("window.SCHOOL = " + json.dumps(
        {"days": days, "timetable": site["timetable"], "key": site["storage_key"]}, ensure_ascii=False) + ";\n")
    for p in sorted((SRC / "pages").glob("*.md")):
        title, rest = split_title(p.read_text())
        (OUT / f"{p.stem}.html").write_text(page(title, f"<h1>{html.escape(title)}</h1>\n" + md(rest)))
    for extra, name in (("SOURCES.md", "sources"), ("TEACHING_AUDIT.md", "teaching-audit")):
        f = ROOT / extra
        if f.exists():
            title, rest = split_title(f.read_text())
            (OUT / f"{name}.html").write_text(page(title, f"<h1>{html.escape(title)}</h1>\n" + md(rest)))
    if site.get("has_printables"):
        printables.build_printables(site, SRC, OUT, page)
    print(f"built {len(days)} days and {len(list((SRC/'pages').glob('*.md')))} pages into {OUT}")

if __name__ == "__main__":
    build()
