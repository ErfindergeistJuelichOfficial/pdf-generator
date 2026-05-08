# pdf-termine

Generiert Terminübersichten als PDF für den **Erfindergeist Jülich e.V.**
Die Termine werden live von [erfindergeist.org](https://erfindergeist.org) abgerufen.

## Voraussetzungen

- [Podman](https://podman.io) mit `podman-compose` **oder** [Docker](https://www.docker.com) mit `docker compose`

## PDFs generieren

```bash
podman compose up --build
```

Die fertigen PDFs liegen danach im Ordner `output/`:

| Datei | Format | Inhalt |
|---|---|---|
| `terminuebersicht_hoch_kurz.pdf` | A4 Hochformat | nächste 7 Termine |
| `terminuebersicht_quer_kurz.pdf` | A4 Querformat | nächste 7 Termine |
| `terminuebersicht_hoch_alle.pdf` | A4 Hochformat | alle Termine |
| `terminuebersicht_quer_alle.pdf` | A4 Querformat | alle Termine |

## Konfiguration

Die API-URL ist in `compose.yaml` hinterlegt und zeigt auf die Live-Daten von erfindergeist.org.
Für eine abweichende URL kann eine `.env`-Datei angelegt werden (siehe `.env.example`).

## Automatische Generierung

Via GitHub Actions wird am **1. jedes Monats um 06:00 Uhr** automatisch ein neuer
[Release](../../releases) mit allen vier PDFs erstellt.
Der Workflow lässt sich auch manuell unter **Actions → Termine PDF generieren → Run workflow** starten.

---

[erfindergeist.org](https://erfindergeist.org) · kontakt@erfindergeist.org
