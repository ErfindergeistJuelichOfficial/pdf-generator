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

env = Environment(loader=FileSystemLoader(str(SRC_DIR / "templates")))
template_termine = env.get_template("termine.html")
template_rc = env.get_template("termine_repaircafe.html")
template_haftung = env.get_template("repaircafe_haftungsbegrenzung.html")
template_laufzettel = env.get_template("repaircafe_laufzettel.html")
template_datenschutz = env.get_template("datenschutz.html")
template_vereinssatzung = env.get_template("vereinssatzung.html")
template_einweisung = env.get_template("einweisung_werkstatt.html")

heute = datetime.now().strftime("%d.%m.%Y")
termine = fetch()
repaircafe = [t for t in termine if "#repaircafe" in t.get("tags", [])]

# (dateiname, template, orientierung, events, termine_pro_seite, alle_seiten)
CONFIGS = [
    ("terminuebersicht_hoch.pdf", template_termine, "portrait",  termine,    9, False),
    ("terminuebersicht_quer.pdf", template_termine, "landscape", termine,    6, False),
    ("termine_repaircafe_hoch.pdf",       template_rc,      "portrait",  repaircafe, 15, True),
    ("repaircafe_quer.pdf",       template_rc,      "landscape", repaircafe, 10, True),
]


def _chunk(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def _render(tmpl, chunks, orientation):
    html_str = tmpl.render(chunks=chunks, orientation=orientation, erstellt=heute)
    return HTML(string=html_str).render()


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

doc_haftung = HTML(string=template_haftung.render()).render()
doc_haftung.write_pdf(str(OUTPUT_DIR / "repaircafe_haftungsbegrenzung.pdf"))
print(f"  repaircafe_haftungsbegrenzung.pdf (statisch, {len(doc_haftung.pages)} Seite)")

doc_laufzettel = HTML(string=template_laufzettel.render()).render()
doc_laufzettel.write_pdf(str(OUTPUT_DIR / "repaircafe_laufzettel.pdf"))
print(f"  repaircafe_laufzettel.pdf (statisch, {len(doc_laufzettel.pages)} Seite)")

doc_datenschutz = HTML(string=template_datenschutz.render()).render()
doc_datenschutz.write_pdf(str(OUTPUT_DIR / "datenschutz.pdf"))
print(f"  datenschutz.pdf (statisch, {len(doc_datenschutz.pages)} Seite)")

doc_vereinssatzung = HTML(string=template_vereinssatzung.render()).render()
doc_vereinssatzung.write_pdf(str(OUTPUT_DIR / "vereinssatzung.pdf"))
print(f"  vereinssatzung.pdf (statisch, {len(doc_vereinssatzung.pages)} Seite(n))")

doc_einweisung = HTML(string=template_einweisung.render()).render()
doc_einweisung.write_pdf(str(OUTPUT_DIR / "einweisung_werkstatt.pdf"))
print(f"  einweisung_werkstatt.pdf (statisch, {len(doc_einweisung.pages)} Seite(n))")

print(f"\nFertig — {len(CONFIGS) + 5} PDFs in {OUTPUT_DIR}")
