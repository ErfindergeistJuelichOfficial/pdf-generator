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

# (dateiname, orientierung, termine_pro_seite, alle_seiten)
CONFIGS = [
    ("terminuebersicht_hoch_kurz.pdf", "portrait",  9, False),
    ("terminuebersicht_quer_kurz.pdf",  "landscape", 6, False),
    ("terminuebersicht_hoch_alle.pdf",  "portrait",  9, True),
    ("terminuebersicht_quer_alle.pdf",  "landscape", 6, True),
]

env = Environment(loader=FileSystemLoader(str(SRC_DIR / "templates")))
template = env.get_template("termine.html")

heute = datetime.now().strftime("%d.%m.%Y")
termine = fetch()


def _chunk(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def _render(chunks, orientation):
    html_str = template.render(chunks=chunks, orientation=orientation, erstellt=heute)
    return HTML(string=html_str, base_url=str(ASSETS_DIR)).render()


for filename, orientation, per_page, alle in CONFIGS:
    if alle:
        chunks = _chunk(termine, per_page)
    else:
        chunks = [termine[:per_page]]
    doc = _render(chunks, orientation)
    doc.write_pdf(str(OUTPUT_DIR / filename))
    total = sum(len(c) for c in chunks)
    pages = len(doc.pages)
    print(f"  {filename} ({total} Termine, {pages} Seite{'n' if pages > 1 else ''})")

print(f"\nFertig — {len(CONFIGS)} PDFs in {OUTPUT_DIR}")
