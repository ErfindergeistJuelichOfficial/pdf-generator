# CLAUDE.md — pdf-termine

## Ausführen

Niemals `pip install` oder `python` direkt auf dem Host. Alles via Container:

```bash
podman compose up --build
```

## Die 4 Ausgaben und ihre Limits

| Datei | Template | Format | Termine pro Seite |
| --- | --- | --- | --- |
| `terminuebersicht_hoch.pdf` | termine.html | A4 Hochformat | 9 (nur 1 Seite) |
| `terminuebersicht_quer.pdf` | termine.html | A4 Querformat | 6 (nur 1 Seite) |
| `repaircafe_hoch.pdf` | repaircafe.html | A4 Hochformat | 15 pro Seite, nur `#repaircafe`-Termine |
| `repaircafe_quer.pdf` | repaircafe.html | A4 Querformat | 10 pro Seite, nur `#repaircafe`-Termine |

Werden die Limits geändert, müssen **README.md** und **`.github/workflows/generate-pdf.yml`** (Release-Body-Tabelle) synchron angepasst werden.

## Nicht-offensichtliche Logik

- `src/fetch.py` liest Tags aus dem `description`-Feld der API und leitet daraus Ort und Beschreibungstext ab.
- Events werden gefiltert wenn: `status != "CONFIRMED"`, Titel enthält `"PLATZHALTER"`, oder Tag `#platzhalter` gesetzt ist.
- Assets (Logo, QR-Code, Caveat-Font) liegen statisch in `src/assets/` — nicht zur Laufzeit laden.
