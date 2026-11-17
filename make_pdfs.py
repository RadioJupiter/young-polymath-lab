#!/usr/bin/env python3
"""Print the combined Unit 1 and Unit 2 worksheet HTML to Letter PDFs with headless Chrome."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "printables"
CHROME = "google-chrome"

def print_pdf(html: Path, pdf: Path):
    cmd = [
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer", f"--print-to-pdf={pdf}", html.resolve().as_uri(),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not pdf.exists():
        sys.stderr.write(r.stderr)
        raise SystemExit(f"failed to print {html}")
    print(f"wrote {pdf} ({pdf.stat().st_size} bytes)")

def main():
    for unit in (1, 2):
        html = OUT / f"unit-{unit}-worksheets.html"
        if not html.exists():
            raise SystemExit(f"missing {html}; run build.py first")
        print_pdf(html, OUT / f"unit-{unit}-worksheets.pdf")

if __name__ == "__main__":
    main()
