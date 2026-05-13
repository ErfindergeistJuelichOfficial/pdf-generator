# CLAUDE.md — pdf-termine

## Ausführen

Niemals `pip install` oder `python` direkt auf dem Host. Alles via Container:

```bash
podman compose up --build
```
Werden die Limits geändert, müssen **README.md** und **`.github/workflows/generate-pdf.yml`** (Release-Body-Tabelle) synchron angepasst werden.
Umbenennung von Datein müssen in **README.md**, **`.github/workflows/generate-pdf.yml`** (Release-Body-Tabelle), den python scripten und im template Ordner synchron angepasst werden.

## Nicht-offensichtliche Logik

- `src/fetch.py` liest Tags aus dem `description`-Feld der API und leitet daraus Ort und Beschreibungstext ab.
- Events werden gefiltert wenn: `status != "CONFIRMED"`, Titel enthält `"PLATZHALTER"`, oder Tag `#platzhalter` gesetzt ist.
- Assets liegen auf https://share.erfindergeist.org/ es gibt dort folgende config jsons:
  - Font assets: https://share.erfindergeist.org/config/fonts.json
  - QR Assets: https://share.erfindergeist.org/config/qr.json
  - Bilder Assets: https://share.erfindergeist.org/config/img.json
