import pathlib
from datetime import datetime

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

load_dotenv()

from fetch import fetch  # noqa: E402 — after load_dotenv

SRC_DIR = pathlib.Path(__file__).parent
OUTPUT_DIR = pathlib.Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_WERKSTATT = OUTPUT_DIR / "Angebote" / "Werkstatt"
OUTPUT_WERKSTATT.mkdir(parents=True, exist_ok=True)
OUTPUT_REPAIRCAFE = OUTPUT_DIR / "Angebote" / "Repaircafe"
OUTPUT_REPAIRCAFE.mkdir(parents=True, exist_ok=True)
OUTPUT_VEREIN = OUTPUT_DIR / "Verein"
OUTPUT_VEREIN.mkdir(exist_ok=True)
OUTPUT_COMPLIANCE = OUTPUT_VEREIN / "Compliance"
OUTPUT_COMPLIANCE.mkdir(exist_ok=True)

env = Environment(loader=FileSystemLoader(str(SRC_DIR / "templates")))
template_termine = env.get_template("termine.html")
template_rc = env.get_template("termine_repaircafe.html")

heute = datetime.now().strftime("%d.%m.%Y")
termine = fetch()
repaircafe = [t for t in termine if "#repaircafe" in t.get("tags", [])]

# (dateiname, template, orientierung, events, termine_pro_seite, alle_seiten, out_dir)
CONFIGS = [
    ("terminuebersicht_hoch.pdf",    template_termine, "portrait",  termine,    7,  False, OUTPUT_VEREIN),
    ("terminuebersicht_quer.pdf",    template_termine, "landscape", termine,    5,  False, OUTPUT_VEREIN),
    ("termine_repaircafe_hoch.pdf",  template_rc,      "portrait",  repaircafe, 15, True,  OUTPUT_REPAIRCAFE),
    ("termine_repaircafe_quer.pdf",  template_rc,      "landscape", repaircafe, 10, True,  OUTPUT_REPAIRCAFE),
]


def _chunk(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def _render(tmpl, chunks, orientation):
    html_str = tmpl.render(chunks=chunks, orientation=orientation, erstellt=heute)
    return HTML(string=html_str, base_url=str(SRC_DIR / "templates")).render()


for filename, tmpl, orientation, events, per_page, alle, out_dir in CONFIGS:
    if alle:
        chunks = _chunk(events, per_page)
    else:
        chunks = [events[:per_page]]
    doc = _render(tmpl, chunks, orientation)
    doc.write_pdf(str(out_dir / filename))
    total = sum(len(c) for c in chunks)
    pages = len(doc.pages)
    print(f"  {out_dir.relative_to(OUTPUT_DIR)}/{filename} ({total} Termine, {pages} Seite{'n' if pages > 1 else ''})")

STATIC_TEMPLATES = [
    ("repaircafe_haftungsbegrenzung", OUTPUT_REPAIRCAFE),
    ("repaircafe_laufzettel",         OUTPUT_REPAIRCAFE),
    ("datenschutz",                   OUTPUT_COMPLIANCE),
    ("vereinssatzung",                OUTPUT_VEREIN),
    ("einweisung_werkstatt",          OUTPUT_WERKSTATT),
    ("verhaltensregeln",              OUTPUT_WERKSTATT),
]

for name, out_dir in STATIC_TEMPLATES:
    tmpl = env.get_template(f"{name}.html")
    doc = HTML(string=tmpl.render(erstellt=heute), base_url=str(SRC_DIR / "templates")).render()
    doc.write_pdf(str(out_dir / f"{name}.pdf"))
    pages = len(doc.pages)
    print(f"  {out_dir.name}/{name}.pdf (statisch, {pages} Seite{'n' if pages > 1 else ''})")

print(f"\nFertig — {len(CONFIGS) + len(STATIC_TEMPLATES)} PDFs in {OUTPUT_DIR}")
