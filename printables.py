#!/usr/bin/env python3
"""Build printable Letter-size worksheets and a printables index into docs/printables/."""
from __future__ import annotations
import html, re
from pathlib import Path
import markdown

# ----- per-day worksheet copy (matches the lessons) -----
DAYS = {
"d01": dict(
    title="Unit 1 · Day 1 · How far is the Moon?", unit=1, n=1,
    nb_title="The Earth–Moon model",
    draw="Draw the Earth and Moon objects and the gap between them. You may compress the gap on the page, but write the real model distance.",
    bank="Earth · Moon · kilometre (km) · centimetre (cm) · metre (m) · model · scale · distance · diameter",
    stems=["The Earth in the model is about ________.", "The Moon in the model is about ________.", "The gap between them is about ________.", "What surprised me was ________."],
    numbers="Write the calculation for each model size (Earth, Moon, distance). Then write one question about the Moon.",
    model="The Moon is far away.",
    write_task="Copy the model sentence on the first line. Then finish the stems in your best handwriting. Say each sentence aloud before you write it.",
    guide="Draw first. Label from the word bank. The student says each sentence before writing. If handwriting is a struggle, write the student's own words in light pencil to trace or copy.",
    sp_title="Hola, and acting out words",
    sp_copy=["Hola.", "Me llamo __________.", "Sí.  No."],
    sp_task="Copy the words. Then draw a line from each command to its meaning.",
    sp_match=[("Levántate", "stand up"), ("Siéntate", "sit down"), ("Mira", "look"), ("Para", "stop"), ("Señala", "point")],
    la_title="Salvē: puer and puella",
    la_copy=["Salvē!", "Aulus est puer.", "Gaia est puella."],
    la_task="Copy the Latin. Then write the English meaning next to each line (after you have read the lesson).",
),
"d02": dict(
    title="Unit 1 · Day 2 · Ordering the planets", unit=1, n=2,
    nb_title="The Solar System on a strip",
    draw="Sketch your scale strip in miniature. Mark the Sun and the planets.",
    bank="Sun · Mercury · Venus · Earth · Mars · Jupiter · Saturn · Uranus · Neptune · million · kilometre · inner planets · gap · scale",
    stems=["The four inner planets are ________.", "The biggest gaps are ________.", "I notice that ________."],
    numbers="Write the eight model lengths you marked on the strip.",
    model="The inner planets are close together.",
    write_task="Copy the model sentence. Then finish the stems. One careful noticing sentence is enough.",
    guide="Help with the long paper strip if needed. Keep the word bank in view. Do not push for a paragraph today.",
    sp_title="People and size",
    sp_copy=["Es un niño.", "Es una niña.", "Es grande.", "Es pequeña."],
    sp_task="Copy the sentences. Then label two figures of different sizes: niño / niña, grande / pequeña.",
    sp_match=[],
    la_title="Familia",
    la_copy=["Aulus est fīlius.", "Gaia est fīlia.", "Celer est canis."],
    la_task="Copy the Latin. Write the English meaning beside each line.",
),
"d03": dict(
    title="Unit 1 · Day 3 · Adding up the worlds", unit=1, n=3,
    nb_title="How big is the Sun?",
    draw="Draw Earth as a 1 cm circle, Jupiter at the same scale (about 11.2 cm across), and a piece of the Sun's edge. Write how wide the whole Sun would be (109 cm).",
    bank="Earth · Jupiter · Sun · diameter · scale · centimetre · wider · curve · huge · edge",
    stems=["Earth is drawn ________.", "Jupiter is about ________ times as wide as Earth.", "The whole Sun at this scale would be ________."],
    bbs="The Sun is huge",
    numbers="Check: is 11 × 12,756 close to 142,984? Is 109 × 12,756 close to 1,391,400? Show your rounding or working.",
    model="The Sun is huge because it is much wider than Earth.",
    write_task="Copy the model. Then finish the same opening three ways: because, but, so.",
    guide="New step: because / but / so. Ask 'because why?' rather than dictating the ending. The student speaks each full sentence first.",
    sp_title="Colours",
    sp_copy=["Es rojo.", "Es azul.", "Es amarillo.", "Es verde.", "El sol es amarillo."],
    sp_task="Copy the sentences. Colour or label four shapes: rojo, azul, amarillo, verde.",
    sp_match=[],
    la_title="Vīlla and hortus",
    la_copy=["Vīlla est magna.", "Aulus est in vīllā.", "Gaia est in hortō."],
    la_task="Copy the Latin. Draw a simple house and garden and label vīlla, hortus, via.",
),
"d04": dict(
    title="Unit 1 · Day 4 · How much farther?", unit=1, n=4,
    nb_title="The Moon journal begins",
    draw="Draw the Moon as it looks tonight (or the last time it was seen), large, with any markings you can really see. Do not look at the Sun.",
    bank="Moon · date · time · sky · cloudy · shape · crescent · half · full · prediction · week",
    stems=["Tonight the Moon looks ________.", "I saw it ________.", "In one week the Moon will look ________ because ________."],
    numbers="Add the date and time. Prepare a row of boxes for the next week's evening drawings (you may use the back of this sheet).",
    model="The Moon changes shape.",
    write_task="Copy the model. Then write your prediction with because.",
    guide="If it is cloudy, draw the last Moon actually seen and write 'cloudy tonight'. Help set up the week's boxes.",
    sp_title="El cielo",
    sp_copy=["El sol.", "La luna.", "Una estrella.", "El cielo.", "Veo la luna."],
    sp_task="Copy the words. Draw a sun, a moon and a star and label them in Spanish.",
    sp_match=[],
    la_title="Canis Celer",
    la_copy=["Celer est canis.", "Celer est magnus.", "Celer currit.", "Celer dormit."],
    la_task="Copy the Latin. Next to currit and dormit, sketch the action.",
),
"d05": dict(
    title="Unit 1 · Day 5 · Walking the Solar System", unit=1, n=5,
    nb_title="The model walk map",
    draw="Draw a map of the walk: the Sun at the start, the path, and each planet marker you reached.",
    bank="Sun · Mercury · Venus · Earth · Mars · Jupiter · Saturn · map · pace · scale · empty · surprising · orbit",
    stems=["The part of the walk that surprised me most was ________.", "Books do not draw the Solar System to scale because ________."],
    expand=("The walk was surprising.", "Add where or when, then why."),
    numbers="Write one question you now want answered.",
    model="The walk was surprising because space is emptier than a picture shows.",
    write_task="Copy the model. Then expand the kernel: first add where or when, then add because.",
    guide="Ask the expansion questions one at a time. The student says the longer sentence before writing it.",
    sp_title="A short sky story",
    sp_copy=["Es de noche.", "Ana mira el cielo.", "Ana ve la luna.", "¡Hola, luna!"],
    sp_task="Copy the story sentences in order. Draw Ana looking at the moon.",
    sp_match=[],
    la_title="A short family story",
    la_copy=["Aulus est puer.", "Gaia est puella.", "Celer est canis.", "Gaia est in hortō."],
    la_task="Copy the lines. Then write, from memory if you can: Gaia dicit: —Salvē, Celer!",
),
"d06": dict(
    title="Unit 2 · Day 6 · Laps around the Earth", unit=2, n=6,
    nb_title="Spotting the Station",
    draw="Draw Earth as a circle 12.8 cm across. Draw the ISS orbit only 4 mm above the surface. (Optional: a small Moon-journal box in a corner.)",
    bank="Earth · ISS · orbit · kilometre · millimetre · scale · slow · fast · sky · pass · horizon",
    stems=["The Station's orbit on this scale is only ________ above Earth.", "The Moon, on the same scale, would be ________ away (from Day 1)."],
    bbs="The Station looks slow",
    numbers="If you have a pass time from Spot the Station, write it here.",
    model="The Station looks slow because it is far away.",
    write_task="Copy the model. Then finish The Station looks slow because / but / so.",
    guide="Help measure 4 mm. Because / but / so today. Look up a pass together if you use NASA's site.",
    sp_title="Numbers 1–10",
    sp_copy=["uno dos tres cuatro cinco", "seis siete ocho nueve diez", "Veo ocho estrellas."],
    sp_task="Copy the numbers. Write the Spanish number next to 3, 6 and 10. Draw and count stars up to eight.",
    sp_match=[("tres", "3"), ("seis", "6"), ("diez", "10"), ("ocho", "8")],
    la_title="Aulus canem videt",
    la_copy=["Aulus canem videt.", "Gaia lūnam videt.", "Celer Aulum videt."],
    la_task="Copy the Latin. In each sentence, underline who sees and circle what is seen.",
),
"d07": dict(
    title="Unit 2 · Day 7 · Riding the Earth around the Sun", unit=2, n=7,
    nb_title="A clock for Mars",
    draw="Invent and draw a clock face or calendar for people living on Mars. Label the hours, and any extra time you include.",
    bank="Mars · sol · hour · minute · clock · calendar · Earth time · extra · advantage · problem",
    stems=["My Mars clock ________.", "One advantage is ________.", "One problem is ________."],
    numbers="After 3 sols, how far behind Earth time is a Mars-time worker? After 9 sols? Show the working.",
    model="A day on Mars is a little longer than a day on Earth.",
    write_task="Copy the model. Then write three connected sentences about your design: what it is, one advantage, one problem.",
    guide="The design must be the student's. Oral rehearsal of the three sentences first. Number them 1, 2, 3 if that helps.",
    sp_title="El perro y el gato",
    sp_copy=["El perro es grande.", "El gato es pequeño.", "El perro corre.", "El gato duerme."],
    sp_task="Copy the sentences. Draw a dog and a cat and label them.",
    sp_match=[],
    la_title="Numbers ūnus to decem",
    la_copy=["ūnus duo trēs quattuor quīnque", "sex septem octō novem decem", "I II III IV V  VI VII VIII IX X"],
    la_task="Copy the words and numerals. Write the Latin word for 3, 5 and 10.",
),
"d08": dict(
    title="Unit 2 · Day 8 · Years on other worlds", unit=2, n=8,
    nb_title="Predicting the full Moon",
    draw="Draw the Sun on one side, Earth in the middle, and the Moon in four positions around Earth. Shade the half of each Moon that faces away from the Sun. Mark which position is a full Moon as seen from Earth.",
    bank="Sun · Earth · Moon · full · new · quarter · reflects · sunlight · shade · prediction · opposite",
    stems=["A full Moon happens when ________.", "My predicted date for the next full Moon is ________."],
    bbs="A full Moon happens",
    numbers="Add 29 or 30 days to the last full Moon you recorded (or looked up) and write the predicted date.",
    model="The Moon reflects sunlight.",
    write_task="Copy the model. Then finish A full Moon happens because / but / so.",
    guide="Help the student shade the unlit half first, then ask which position looks full from Earth. Do not answer first.",
    sp_title="Tiene y quiere",
    sp_copy=["Ana tiene un gato.", "Yo tengo un lápiz.", "El perro quiere agua."],
    sp_task="Copy the sentences. Then write one new sentence: Yo tengo ________.",
    sp_match=[],
    la_title="Sōl and lūna",
    la_copy=["Sōl est magnus.", "Lūna est in caelō.", "Gaia lūnam spectat.", "Aulus sōlem non spectat."],
    la_task="Copy the Latin. Write why the last line is important, in English.",
),
"d09": dict(
    title="Unit 2 · Day 9 · Messages at the speed of light", unit=2, n=9,
    nb_title="Graphing the pendulum",
    draw="Draw your graph: length (cm) along the bottom, time of one swing (s) up the side. Plot three points and join them with a smooth curve. Then sketch a pendulum clock.",
    bank="pendulum · length · time · seconds · centimetre · graph · curve · clock · Huygens · predict · swing",
    stems=[],
    outline=True,
    outline_topic="The pendulum's time depends on its length.",
    numbers="From your graph, how long should a pendulum be for one swing of 1.5 s? Record the test of 10 swings.",
    model="The pendulum's time depends on its length.",
    write_task="Copy the topic sentence. Write two or three short notes (not sentences), then a closing sentence. Draft a short paragraph on the lines from that outline only.",
    guide="Notes in the outline are not full sentences. You may scribe the notes; the student still says the sentences of the draft.",
    sp_title="La casa y el jardín",
    sp_copy=["La casa.", "El jardín.", "Ana está en el jardín.", "Ana mira la luna."],
    sp_task="Copy the sentences. Draw a house and a garden and label la casa and el jardín.",
    sp_match=[],
    la_title="Commands: venī, spectā, tacē",
    la_copy=["Salvē!", "Venī!", "Spectā!", "Tacē!", "Valē!", "Aule! Venī!", "Gaia! Spectā lūnam!"],
    la_task="Copy the commands. Next to each of venī, spectā and tacē, sketch the action.",
),
"d10": dict(
    title="Unit 2 · Day 10 · Mission planning day", unit=2, n=10,
    nb_title="Design a mission",
    draw="Draw your spacecraft from two views (side and front), with labels, the way Leonardo da Vinci drew machines.",
    bank="spacecraft · destination · Moon · Mars · Jupiter · distance · light-time · travel · power · food · message · problem · question",
    stems=[],
    outline=True,
    outline_topic="This mission goes to ________.",
    numbers="Write the distance, the light-time for messages, and a travel time at a speed you choose (show the division). List three problems and one idea for each if they did not all fit in the paragraph.",
    model="This mission goes to the Moon.",
    write_task="Use the model only if you chose the Moon; otherwise write your own topic sentence. Add notes for distance or light-time, one problem and an idea, and a closing question. Then draft a short paragraph from the outline.",
    guide="The design must be the student's. Help with numbers already in the unit. If handwriting is tiring after the unit check, scribe the paragraph exactly as spoken, for the student to copy.",
    sp_title="Review story",
    sp_copy=["Es de noche.", "Ana está en el jardín.", "Ana mira el cielo.", "Ana ve la luna.", "¡Hola, luna!"],
    sp_task="Copy two sentences you can now read alone. Then write or copy one more from this week's Spanish.",
    sp_match=[],
    la_title="Review story",
    la_copy=["Aulus est puer.", "Gaia est puella.", "Aulus canem videt.", "Gaia lūnam spectat.", "Valē, Aule!"],
    la_task="Copy two lines you can now read alone. Write the English meaning of Aulus canem videt.",
),
}


ITEM_RE = re.compile(r"^(\d+)\.\s+(.*)$")


def _md_sections(text: str):
    """Return list of (heading, body) for ## and ### headings, in order."""
    parts = re.split(r"^(#{2,3} .+)$", text, flags=re.M)
    out = []
    # parts[0] is intro
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip(), parts[i + 1] if i + 1 < len(parts) else ""))
    return out


def parse_math_blocks(md_text: str):
    """Collect mental-math items, practice/unit-check items, and their keys."""
    secs = _md_sections(md_text)
    mental_items, practice_items = [], []
    mental_key, practice_key = "", ""
    pending = None  # 'mental' or 'practice'
    for heading, body in secs:
        h = heading.lstrip("# ").strip()
        # drop "{#id}"
        h = re.sub(r"\s*\{#[^}]+\}\s*$", "", h)
        if heading.startswith("## ") and h.lower().startswith("mental math"):
            mental_items = list(_items_with_heads(body))
            pending = "mental"
        elif heading.startswith("### ") and h.lower().startswith("practice"):
            practice_items.extend(_items_with_heads(body))
            pending = "practice"
        elif heading.startswith("## ") and h.lower().startswith("unit check"):
            practice_items.extend(_items_with_heads(body))
            pending = "practice"
        elif heading.startswith("### ") and h.lower().startswith("unit check"):
            practice_items.extend(_items_with_heads(body))
            pending = "practice"
        elif heading.startswith("### ") and h.lower().startswith("answer key"):
            if pending == "mental":
                mental_key = body.strip()
            elif pending == "practice":
                practice_key = (practice_key + "\n" + body.strip()).strip()
            pending = None
        elif heading.startswith("## "):
            pending = None
    return mental_items, practice_items, mental_key, practice_key


def _items_with_heads(body: str):
    """Yield ('head', text) for bold part labels or ('item', '1. ...'). Skip meta/html."""
    acc = []
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("<p class="):
            continue
        if s.startswith("**Part ") or (s.startswith("**") and s.endswith("**") and len(s) < 80):
            acc.append(("head", s.strip("*").strip()))
            continue
        m = ITEM_RE.match(s)
        if m:
            acc.append(("item", f"{m.group(1)}. {m.group(2)}"))
            continue
        # continuation of previous item
        if acc and acc[-1][0] == "item" and not s.startswith("#") and not s.startswith("###"):
            acc[-1] = ("item", acc[-1][1] + " " + s)
    return acc


def esc(s):
    return html.escape(s, quote=True)

def md_html(text):
    return markdown.markdown(text or '', extensions=['tables', 'fenced_code', 'sane_lists'], output_format='html5')


def lines(n, cls="hw"):
    return "".join(f'<div class="{cls}"></div>' for _ in range(n))


def sheet_page(title, inner, css_rel, home_rel, extra_toolbar=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{esc(title)} · Polymath Lab</title>
<link rel="stylesheet" href="{css_rel}">
</head><body>
<div class="toolbar no-print">
<a href="{home_rel}">Printables</a>
{extra_toolbar}
<button type="button" onclick="window.print()">Print</button>
</div>
{inner}
</body></html>
"""


def sheet_wrap(kind, d, body, footer_right):
    return f"""<article class="sheet" data-kind="{esc(kind)}">
<div class="hd"><div>
<h1>{esc(d['title'])}</h1>
<p class="sub">{esc(kind)} · Polymath Lab · {esc(footer_right)}</p>
</div></div>
<div class="meta-line"><span>Name</span><span>Date</span></div>
{body}
</article>
"""


def math_body(d, mental, practice):
    parts = ['<p class="sub">Work in pencil. Use the boxes for working. Do not open the answer key until you have finished.</p>']
    if mental:
        parts.append("<h2>Mental math</h2><p>Say how you got each answer, then write it.</p><ol>")
        # already numbered in text; use list without forcing new numbers if messy
        parts[-1] = "<h2>Mental math</h2><p>Say how you got each answer, then write it.</p>"
        for kind, t in mental:
            if kind == "head":
                parts.append(f"<h2>{esc(t)}</h2>")
            else:
                parts.append(f"<div class=\"item\"><p>{esc(t)}</p><div class=\"work short\"></div></div>")
    if practice:
        parts.append("<h2>Practice</h2>")
        for kind, t in practice:
            if kind == "head":
                parts.append(f"<h2>{esc(t)}</h2>")
            else:
                tall = "tall" if any(w in t.lower() for w in ("draw", "bar model", "area model", "show")) else ""
                parts.append(f"<div class=\"item\"><p>{esc(t)}</p><div class=\"work {tall}\"></div></div>")
    return "\n".join(parts)


def notebook_body(d):
    parts = [
        f"<h2>Notebook · {esc(d['nb_title'])}</h2>",
        "<p><strong>1. Draw first.</strong> " + esc(d["draw"]) + "</p>",
        '<div class="draw"></div>',
        "<p><strong>2. Label</strong> from the word bank. Point, say the word, then write it on the drawing.</p>",
        f"<div class=\"bank\"><strong>Word bank</strong> — {esc(d['bank'])}</div>",
        "<p><strong>3. Write.</strong> Say each sentence aloud, then write it on the lines.</p>",
    ]
    for s in d.get("stems") or []:
        parts.append(f'<p class="stem">{esc(s)}</p>' + lines(1))
    if d.get("bbs"):
        parts.append("<p>Finish all three, with the same opening:</p>")
        for conj in ("because", "but", "so"):
            parts.append(f'<p class="stem">{esc(d["bbs"])} {conj} ________.</p>' + lines(1))
    if d.get("expand"):
        kernel, hint = d["expand"]
        parts.append(f"<p>Kernel: <strong>{esc(kernel)}</strong> — {esc(hint)}</p>")
        parts.append("<p>Expanded sentence:</p>" + lines(2))
    if d.get("outline"):
        parts.append(f"<p>Topic sentence: <strong>{esc(d['outline_topic'])}</strong></p>" + lines(1))
        parts.append("<p>Notes (not full sentences):</p>" + lines(2))
        parts.append("<p>Closing sentence:</p>" + lines(1))
        parts.append("<p>Short paragraph, written from the outline only:</p>" + lines(4))
    parts.append("<p><strong>4. Numbers and questions.</strong> " + esc(d["numbers"]) + "</p>")
    parts.append('<div class="work tall"></div>')
    parts.append(f"<p class=\"guide\"><strong>For the guide:</strong> {esc(d['guide'])}</p>")
    return "\n".join(parts)


def writing_body(d):
    parts = [
        "<h2>Handwriting and writing scaffold</h2>",
        f"<p>{esc(d['write_task'])}</p>",
        "<p>Model sentence (copy on the line below):</p>",
        f"<p><strong>{esc(d['model'])}</strong></p>",
        lines(2),
        "<p>Your sentences:</p>",
    ]
    if d.get("stems"):
        for s in d["stems"]:
            parts.append(f'<p class="stem">{esc(s)}</p>' + lines(1))
    if d.get("bbs"):
        for conj in ("because", "but", "so"):
            parts.append(f'<p class="stem">{esc(d["bbs"])} {conj} ________.</p>' + lines(1))
    if d.get("expand"):
        kernel, hint = d["expand"]
        parts.append(f"<p>Expand: <strong>{esc(kernel)}</strong> — {esc(hint)}</p>" + lines(2))
    if d.get("outline"):
        parts.append("<p>Outline and paragraph:</p>" + lines(6))
    if not d.get("stems") and not d.get("bbs") and not d.get("expand") and not d.get("outline"):
        parts.append(lines(4))
    parts.append(f"<p class=\"guide\"><strong>For the guide:</strong> {esc(d['guide'])} After the draft is down, tidy spelling from the word bank. Do not correct every error in the first writing.</p>")
    return "\n".join(parts)


def lang_body(d, lang):
    if lang == "spanish":
        title, copy, task, match = d["sp_title"], d["sp_copy"], d["sp_task"], d.get("sp_match") or []
        head = "Spanish"
    else:
        title, copy, task, match = d["la_title"], d["la_copy"], d["la_task"], []
        head = "Latin"
    parts = [
        f"<h2>{esc(head)} · {esc(title)}</h2>",
        f"<p>{esc(task)}</p>",
        "<p>Copy:</p>",
    ]
    for c in copy:
        parts.append(f"<p><strong>{esc(c)}</strong></p>" + lines(1))
    if match:
        parts.append("<p>Draw a line from each word to its meaning:</p>")
        parts.append('<div class="match">')
        left = "".join(f"<p>{esc(a)}</p>" for a, _ in match)
        rights = [b for _, b in match][::-1]
        right = "".join(f"<p>{esc(b)}</p>" for b in rights)
        parts.append(f"<div>{left}</div><div>{right}</div></div>")
    parts.append("<p>Write or draw one more thing from today's lesson:</p>")
    parts.append('<div class="work short"></div>')
    parts.append('<p class="guide"><strong>For the guide:</strong> Listen and point first. Speaking is welcome but not required. Accept close attempts.</p>')
    return "\n".join(parts)


def parse_lang_keys(md_text):
    """Return dict id -> (heading, key text) for spanish, latin, notebook."""
    secs = _md_sections(md_text)
    found = {}
    current = None
    heading = ""
    for h0, body in secs:
        h = re.sub(r"\s*\{#[^}]+\}\s*$", "", h0.lstrip("# ").strip())
        if h0.startswith("## "):
            current = None
            heading = h
            if " {#" in h0:
                pass
            hid = None
            m = re.search(r"\{#([a-z-]+)\}", h0)
            if m:
                hid = m.group(1)
            if hid in ("spanish", "latin", "notebook"):
                current = hid
                found[hid] = [h, ""]
        elif h0.startswith("### ") and h.lower().startswith("answer key") and current:
            found[current][1] = body.strip()
            current = None
    return found


def key_inner(d, mental_key, practice_key, lang_keys):
    parts = [f"<h2>Answer keys · {esc(d['title'])}</h2>",
             "<p>These keys are for the printable sheets. Open them only after the work is done. Sample sentences are examples; other honest sentences may be just as good.</p>"]
    parts.append("<h2>Math · mental math</h2>")
    parts.append("<div class='ans'>" + md_html(mental_key) + "</div>")
    parts.append("<h2>Math · practice</h2>")
    parts.append("<div class='ans'>" + md_html(practice_key) + "</div>")
    for hid, label in (("spanish", "Spanish"), ("latin", "Latin"), ("notebook", "Notebook")):
        if hid in lang_keys:
            h, body = lang_keys[hid]
            parts.append(f"<h2>{esc(label)}</h2>")
            parts.append("<div class='ans'>" + md_html(body) + "</div>")
    parts.append("<p class='guide'>Writing stems: there is no single correct sentence. Check that the sentence is complete, uses the word bank honestly, and (where asked) gives a reason, a contrast, or a result.</p>")
    return "\n".join(parts)


def build_printables(site, src: Path, out: Path, page_fn):
    days_dir = src / "days"
    pdir = out / "printables"
    kdir = pdir / "keys"
    pdir.mkdir(parents=True, exist_ok=True)
    kdir.mkdir(exist_ok=True)

    unit_sheets = {1: [], 2: []}
    index_rows = {1: [], 2: []}

    for did in site["days"]:
        d = DAYS[did]
        md = (days_dir / f"{did}.md").read_text()
        mental, practice, mkey, pkey = parse_math_blocks(md)
        lang_keys = parse_lang_keys(md)

        math = sheet_wrap("Math practice", d, math_body(d, mental, practice), f"{did} · math")
        nb = sheet_wrap("Notebook project", d, notebook_body(d), f"{did} · notebook")
        wr = sheet_wrap("Handwriting and writing scaffold", d, writing_body(d), f"{did} · writing")
        sp = sheet_wrap("Spanish", d, lang_body(d, "spanish"), f"{did} · Spanish")
        la = sheet_wrap("Latin", d, lang_body(d, "latin"), f"{did} · Latin")
        kinds = [
            ("math", "Math practice", math),
            ("notebook", "Notebook project", nb),
            ("writing", "Writing scaffold", wr),
            ("spanish", "Spanish", sp),
            ("latin", "Latin", la),
        ]
        for slug, label, article in kinds:
            path = pdir / f"{did}-{slug}.html"
            path.write_text(sheet_page(
                f"{d['title']} · {label}",
                article,
                "../assets/print-sheet.css",
                "index.html",
                extra_toolbar=f'<a href="{did}.html">This day</a> <a href="keys/{did}.html">Answer key</a>',
            ))
        unit_sheets[d["unit"]].extend(article for _, _, article in kinds)

        # day landing (site chrome)
        links = "\n".join(
            f'<li><a href="{did}-{slug}.html">{esc(label)}</a></li>'
            for slug, label, _ in kinds
        )
        landing = (
            f"<h1>Printables · {esc(d['title'])}</h1>"
            "<p>Print on Letter paper, in black and white. Use the Print button on each sheet. "
            "The answer key is separate.</p>"
            f"<ul>{links}</ul>"
            f'<p><a href="keys/{did}.html">Answer keys for these sheets</a> · '
            f'<a href="../days/{did}.html">Back to the lessons</a> · '
            f'<a href="../keys/{did}.html">Lesson answer keys</a></p>'
        )
        (pdir / f"{did}.html").write_text(page_fn(f"Printables · {d['title']}", landing, 1))
        index_rows[d["unit"]].append(
            f'<tr><td><a href="{did}.html">{esc(d["title"])}</a></td>'
            + "".join(f'<td><a href="{did}-{slug}.html">{esc(label)}</a></td>' for slug, label, _ in kinds)
            + f'<td><a href="keys/{did}.html">Key</a></td></tr>'
        )

        key_article = f"<article class='sheet'>{key_inner(d, mkey, pkey, lang_keys)}</article>"
        (kdir / f"{did}.html").write_text(sheet_page(
            f"Keys · {d['title']}",
            key_article,
            "../../assets/print-sheet.css",
            "../index.html",
            extra_toolbar=f'<a href="../{did}.html">Sheets for this day</a>',
        ))

    # combined unit HTML (for printing / PDF)
    pdf_notes = []
    for unit, articles in unit_sheets.items():
        combined = sheet_page(
            f"Unit {unit} worksheets",
            "\n".join(articles),
            "../assets/print-sheet.css",
            "index.html",
            extra_toolbar="<span>All student sheets for this unit (no answer keys). Print, or use the combined PDF if present.</span>",
        )
        (pdir / f"unit-{unit}-worksheets.html").write_text(combined)
        pdf_notes.append(unit)

    # index
    def table(unit):
        head = ("<table><thead><tr><th>Day</th><th>Math</th><th>Notebook</th>"
                "<th>Writing</th><th>Spanish</th><th>Latin</th><th>Keys</th></tr></thead><tbody>")
        return head + "\n".join(index_rows[unit]) + "</tbody></table>"

    index_body = f"""
<p>The language of instruction is English. These sheets are for Units 1 and 2. Print them on <strong>Letter</strong> paper, in black and white. Use the Print button. Answer keys are on separate pages and are not in the combined PDFs.</p>
<p>Each day has five student sheets: math practice, the notebook project (drawing box, word bank, stems and lines), a handwriting and writing scaffold, Spanish, and Latin.</p>
<h2>Unit 1</h2>
{table(1)}
<p><a href="unit-1-worksheets.html">All Unit 1 sheets on one page</a> · <a href="unit-1-worksheets.pdf">Unit 1 combined PDF</a></p>
<h2>Unit 2</h2>
{table(2)}
<p><a href="unit-2-worksheets.html">All Unit 2 sheets on one page</a> · <a href="unit-2-worksheets.pdf">Unit 2 combined PDF</a></p>
<p>How to use the notebook sheets is explained in <a href="../notebook.html">How the notebook works</a>.</p>
"""
    (pdir / "index.html").write_text(page_fn("Printables", "<h1>Printables</h1>\n" + index_body, 1))
    print(f"printables: {len(site['days'])} days, unit HTML for {pdf_notes}")


if __name__ == "__main__":
    import json, sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    # smoke-test the parser only
    root = Path(__file__).resolve().parent
    for did in DAYS:
        md = (root / "content/days" / f"{did}.md").read_text()
        m, p, mk, pk = parse_math_blocks(md)
        lk = parse_lang_keys(md)
        print(did, "mental", len(m), "practice", len(p), "keys", bool(mk), bool(pk), "lang", list(lk))
        if not m or not p or not mk or not pk or set(lk) != {"spanish", "latin", "notebook"}:
            print("  WARN incomplete", "mkey", mk[:80] if mk else None, "pkey", pk[:80] if pk else None)
