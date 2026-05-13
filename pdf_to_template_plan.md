# PDF → HTML-Template: Leitfaden

Prozess um ein bestehendes PDF-Dokument als HTML-Template in dieses Projekt aufzunehmen,
damit es automatisch bei `podman compose up` und im CI-Release mitgeneriert wird.

---

## Checkliste

1. **PDF lesen** — Claude Code kann `.pdf`-Dateien direkt lesen und visualisieren
2. **Layout analysieren** — statisch oder dynamisch? (siehe Entscheidungsbaum)
3. **Template erstellen** — `src/templates/<name>.html` (Design System beachten)
4. **`src/main.py` eintragen** — Template laden + Render-Aufruf ergänzen
5. **`README.md` updaten** — neue Zeile in der Ausgabetabelle
6. **`.github/workflows/generate-pdf.yml` updaten** — neue Zeile in der Release-Body-Tabelle

---

## Entscheidungsbaum: Statisch oder Dynamisch?

```text
Braucht das Dokument Termine/Event-Daten aus der API?
│
├─ Nein → Statisches Template
│          └─ Kein chunks-Rendering, kein orientation-Parameter nötig
│             Render-Aufruf: template.render()
│
└─ Ja  → Dynamisches Template (wie termine.html / termine_repaircafe.html)
           └─ chunks-Variable, orientation-Parameter
              → Eintrag in CONFIGS-Liste in main.py
```

---

## Design System (statische Templates)

Alle statischen Templates verwenden diese einheitlichen Werte:

| Eigenschaft | Wert |
| --- | --- |
| Font | `Arial, Helvetica, sans-serif` |
| Body-Größe | `9.5pt` |
| Body-Farbe | `#111` |
| Line-height | `1.4` |
| Titel (h1) | `13pt`, fett, zentriert |
| Abschnittsüberschriften | `9.5pt`, fett |
| Beschriftungen / Stand | `8pt #555` |
| Absatzabstand | `margin-bottom: 3mm` |
| Unterschrifts-Linie | `border-bottom: 1px solid #111`, `height: 6mm` |
| Unterschrifts-Label | `8pt #555` |

```css
/* Basis-Reset für alle statischen Templates */
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 9.5pt;
  color: #111;
  line-height: 1.4;
}

h1 {
  font-size: 13pt;
  font-weight: bold;
  text-align: center;
}

h2 {
  font-size: 9.5pt;
  font-weight: bold;
}

.stand, .sig-label, .section-label {
  font-size: 8pt;
  color: #555;
}

.sig-line {
  border-bottom: 1px solid #111;
  height: 6mm;
}
```

---

## Vorlage: Statisches Template

Für Formulare, Aushänge, Merkblätter — kein Event-Feed.

```html
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  @page { size: A4 portrait; margin: 0; }   /* oder landscape */
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 9.5pt;
    color: #111;
    line-height: 1.4;
    padding: 20mm 22mm 18mm;
  }
  /* Design System (siehe oben) */
</style>
</head>
<body>
  <!-- Inhalt hier -->
</body>
</html>
```

**main.py-Ergänzungen:**

```python
# In STATIC_TEMPLATES eintragen (Name ohne Erweiterung):
STATIC_TEMPLATES = [
    ...
    "xyz",
]
```

Kein weiterer Aufwand — die Schleife übernimmt Laden, Rendern und Ausgabe automatisch.

---

## Vorlage: Dynamisches Template

Für Inhalte die sich aus dem Event-Feed ergeben (wie termine.html / termine_repaircafe.html).

```html
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<style>
  @page { size: A4 {{ orientation }}; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: Arial, Helvetica, sans-serif; }
</style>
</head>
<body>
{% for chunk in chunks %}
{% if not loop.first %}<div style="page-break-before: always;"></div>{% endif %}
{% for t in chunk %}
  <!-- t.titel, t.datum, t.zeit, t.ort, t.beschreibung, t.tags -->
{% endfor %}
{% endfor %}
</body>
</html>
```

**main.py-Ergänzungen:**

```python
# Oben:
template_neu = env.get_template("neu.html")

# In CONFIGS hinzufügen:
# (dateiname,      template,     orientierung,  events,   pro_seite, alle_seiten)
("neu_hoch.pdf",   template_neu, "portrait",    termine,  9,         False),
("neu_quer.pdf",   template_neu, "landscape",   termine,  6,         False),
```

---

## Assets (Webserver)

Alle Assets liegen auf `https://share.erfindergeist.org/` — lokaler `assets/`-Ordner existiert nicht mehr.

| Asset | URL |
| --- | --- |
| Erfindergeist-Logo (breit) | `https://share.erfindergeist.org/img/logo_with_typeface_wide.svg` |
| Erfindergeist-Schriftzug | `https://share.erfindergeist.org/img/logo.svg` |
| Repair-Café-Logo | `https://share.erfindergeist.org/img/RC_blueorange.png` |
| QR-Code Linktree | `https://share.erfindergeist.org/qr/qr_link_to_linktree_H30_stl.svg` |
| Caveat Bold (Font) | `https://share.erfindergeist.org/fonts/Caveat-Bold.ttf` |
| Caveat Regular (Font) | `https://share.erfindergeist.org/fonts/Caveat-Regular.ttf` |

In Templates direkt als absolute URL einbinden — kein `base_url` nötig.

---

## Bereits vorhandene Templates

| Template | Output | Beschreibung |
| --- | --- | --- |
| `termine.html` | `terminuebersicht_hoch/quer.pdf` | Alle Termine, 1 Seite |
| `termine_repaircafe.html` | `termine_repaircafe_hoch.pdf` / `repaircafe_quer.pdf` | Repair-Café-Termine, mehrseitig |
| `repaircafe_haftungsbegrenzung.html` | `repaircafe_haftungsbegrenzung.pdf` | Statisches Formular, 2× A5 auf A4 Quer |
| `repaircafe_laufzettel.html` | `repaircafe_laufzettel.pdf` | Statisches Formular, 2× A5 auf A4 Quer |
| `datenschutz.html` | `datenschutz.pdf` | Statisches Dokument, A4 Hoch |
| `vereinssatzung.html` | `vereinssatzung.pdf` | Statisches Dokument, A4 Hoch, 6 Seiten |
| `einweisung_werkstatt.html` | `einweisung_werkstatt.pdf` | Statisches Formular, A4 Hoch, 2 Seiten |
