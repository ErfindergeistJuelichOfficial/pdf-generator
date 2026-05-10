import pathlib
from datetime import datetime

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

load_dotenv()

from fetch import fetch  # noqa: E402 — after load_dotenv

SRC_DIR = pathlib.Path(__file__).parent
ASSETS_DIR = SRC_DIR / "assets"
OUTPUT_DIR = pathlib.Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

env = Environment(loader=FileSystemLoader(str(SRC_DIR / "templates")))
template_termine = env.get_template("termine.html")
template_rc = env.get_template("repaircafe.html")

heute = datetime.now().strftime("%d.%m.%Y")
termine = fetch()
repaircafe = [t for t in termine if "#repaircafe" in t.get("tags", [])]

# (dateiname, template, orientierung, events, termine_pro_seite, alle_seiten)
CONFIGS = [
    ("terminuebersicht_hoch.pdf", template_termine, "portrait",  termine,    9, False),
    ("terminuebersicht_quer.pdf", template_termine, "landscape", termine,    6, False),
    ("repaircafe_hoch.pdf",       template_rc,      "portrait",  repaircafe, 15, True),
    ("repaircafe_quer.pdf",       template_rc,      "landscape", repaircafe, 10, True),
]


def _chunk(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def _render(tmpl, chunks, orientation):
    html_str = tmpl.render(chunks=chunks, orientation=orientation, erstellt=heute)
    return HTML(string=html_str, base_url=str(ASSETS_DIR)).render()


for filename, tmpl, orientation, events, per_page, alle in CONFIGS:
    if alle:
        chunks = _chunk(events, per_page)
    else:
        chunks = [events[:per_page]]
    doc = _render(tmpl, chunks, orientation)
    doc.write_pdf(str(OUTPUT_DIR / filename))
    total = sum(len(c) for c in chunks)
    pages = len(doc.pages)
    print(f"  {filename} ({total} Termine, {pages} Seite{'n' if pages > 1 else ''})")

print(f"\nFertig — {len(CONFIGS)} PDFs in {OUTPUT_DIR}")
