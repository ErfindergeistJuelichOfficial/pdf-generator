import os
import pathlib
from datetime import datetime

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

load_dotenv()

from fetch import fetch  # noqa: E402 — after load_dotenv

SRC_DIR = pathlib.Path(__file__).parent
TEMPLATES_DIR = SRC_DIR / "templates"
ASSETS_DIR = SRC_DIR / "assets"
OUTPUT_DIR = pathlib.Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

CONFIGS = [
    ("terminuebersicht_hoch_kurz.pdf", "portrait", 7),
    ("terminuebersicht_quer_kurz.pdf", "landscape", 7),
    ("terminuebersicht_hoch_alle.pdf", "portrait", None),
    ("terminuebersicht_quer_alle.pdf", "landscape", None),
]

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
template = env.get_template("termine.html")

heute = datetime.now().strftime("%d.%m.%Y")
termine = fetch()

for filename, orientation, max_items in CONFIGS:
    data = termine[:max_items] if max_items is not None else termine
    html_str = template.render(termine=data, orientation=orientation, erstellt=heute)
    out_path = OUTPUT_DIR / filename
    HTML(string=html_str, base_url=str(ASSETS_DIR)).write_pdf(str(out_path))
    print(f"  {filename} ({len(data)} Termine)")

print(f"\nFertig — {len(CONFIGS)} PDFs in {OUTPUT_DIR}")
