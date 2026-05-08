# CLAUDE.md — pdf-termine

## Projekt

Generiert 4 Terminübersicht-PDFs für den **Erfindergeist Jülich e.V.** aus der Live-API von erfindergeist.org.

## Ausführen — immer via Container

**Niemals** `pip install`, `python src/main.py` o.ä. direkt auf dem Host ausführen.
Alles läuft isoliert im Container:

```bash
podman compose up --build
```

Die fertigen PDFs landen in `output/`.

## Stack

- Python 3.12 + Jinja2 + WeasyPrint (HTML → PDF)
- Podman Compose lokal, GitHub Actions monatlich (1. des Monats, 06:00 UTC)

## Die 4 Ausgaben

| Datei | Format | Termine pro Seite |
|---|---|---|
| `terminuebersicht_hoch_kurz.pdf` | A4 Hochformat | 9 (nur 1 Seite) |
| `terminuebersicht_quer_kurz.pdf` | A4 Querformat | 6 (nur 1 Seite) |
| `terminuebersicht_hoch_alle.pdf` | A4 Hochformat | 9 pro Seite, alle Termine |
| `terminuebersicht_quer_alle.pdf` | A4 Querformat | 6 pro Seite, alle Termine |

## Architektur

- `src/fetch.py` — API-Abruf, Filterung, Tag-Mapping (Ort + Beschreibung)
- `src/main.py` — Chunking + Rendering aller 4 PDFs
- `src/templates/termine.html` — einziges HTML-Template, parametrisiert nach `chunks` und `orientation`
- `src/assets/` — statische Assets (Logo, QR-Code, Caveat-Font) — **nicht via URL laden, sind im Repo**

## Design-Farben

- Primär: `#159989` (Teal) — Kopf-Akzent, Divider-Linie, Fußleiste
- Sekundär: `#F9B338` (Gold) — horizontale Trennlinie
- Schrift: Caveat (Regular + Bold) für Überschriften, Arial für Fließtext

## Konfiguration

`TERMINE_JSON_URL` in `.env` (lokal) oder als Env-Variable im CI-Workflow.
Beispiel: `.env.example`.

## Tag-Mapping in fetch.py

Ort-Tags (aus `description`-Feld der API):
- `#awo` → `"Erfindergeist Werkstatt, Jülich"`
- `#stadtbücherei` → `"Stadtbücherei Jülich"`

Beschreibungs-Tags:
- `#offenewerkstatt`, `#stammtisch`, `#repaircafe` → langer Erklärtext

Filter: Events mit `status != "CONFIRMED"`, Titel enthält `"PLATZHALTER"` oder Tag `#platzhalter` werden ausgeblendet.
