# Polymath Lab

A mastery-based mathematics course for a gifted young mathematician who loves space and physics: solid foundations, hard problems every day, and a Leonardo-style notebook. It is a static website (plain HTML, CSS and JavaScript, no server, no accounts, no tracking). Progress is saved only in the browser's local storage on the device you use.

## Open it

- Open `docs/index.html` in any browser, or
- serve the folder: `cd docs && python3 -m http.server 8000`, then visit http://localhost:8000.

## The method, in brief

| Choice | Why |
|---|---|
| **Mastery and acceleration** | Move on when a level is mastered, not by calendar. A century of research shows acceleration helps high-ability students (Steenbergen-Hu et al., 2016). Depth is kept by never skipping the challenge and circle problems. |
| **Concrete → pictorial → abstract** | Bruner's three modes of representation; the backbone of Singapore mathematics since 1981. The pictures (place value charts, arrays, area models) are what make methods understood. |
| **Singapore bar models** | The model method (1983) turns word problems into structure and leads directly to algebra. |
| **Daily challenge problems (Beast Academy / AoPS style)** | Real problem solving, with being stuck as a normal, valuable part of it. Hints come in stages. |
| **Russian math circle** | One rich problem a day from the tradition of Fomin, Genkin and Itenberg: logic, counting, parity, invariants, pigeonhole. Every one ends with "why", the beginning of proof. |
| **Mental math** | Ten minutes daily of strategies explained aloud: fluency frees thinking, and retrieval strengthens memory. |
| **Space and physics in every lesson** | Real data from NASA, the BIPM and the IAU, rounded honestly; household experiments (scale walks, pendulums, the Moon journal). |
| **Leonardo-style notebook** | An hour of observing, measuring, drawing from life and inventing. |
| **No gamification** | No points, badges or streaks; motivation from interesting problems and visible growth. |

Full rationale: `content/pages/methods.md` (the Method page). References: [SOURCES.md](SOURCES.md).

## Daily structure

About 1 hour 40 minutes of focused mathematics (mental math, core lesson, challenge, math circle) with breaks, then about an hour of notebook and project work.

## What is complete

- Placement check with answer key and starting-level routing (Levels 1–8, plus problem-solving readiness).
- Level map: 12 levels with mathematics and space themes.
- **Unit 1 (Level 4: large numbers, Days 1–5)** and **Unit 2 (Level 5: multiplication and division, Days 6–10)**: 10 full days, each with mental math, a CPA core lesson, challenge problems, a math circle problem, a notebook task, guide notes, and a separate answer key.
- Daily plan, Today page (counts school days from a start date you set), notebook guide, progress page (checkboxes saved in your browser, with export and import).

## Planned

- Lessons for Levels 1–3 (for a student who places below Level 4) and Levels 6–12.
- Unit checks for each level.
- Until those are written: if placement shows a start below Level 4 or above Level 5, the placement key suggests published materials to use alongside this site's circle and notebook work.

## Build

Content is Markdown in `content/`. To rebuild `docs/`:

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py
.venv/bin/python check_links.py
```

## Privacy

The site contains no personal information and sends no data anywhere. Progress lives only in your browser.
