# pdf-termine

Generates event schedule PDFs for **Erfindergeist Jülich e.V.**
Events are fetched live from [erfindergeist.org](https://erfindergeist.org).

## Prerequisites

- [Podman](https://podman.io) with `podman-compose` **or** [Docker](https://www.docker.com) with `docker compose`

## Generate PDFs

```bash
podman compose up --build
```

The finished PDFs will be placed in the `output/` folder:

| File | Format | Content |
|---|---|---|
| `terminuebersicht_hoch.pdf` | A4 Portrait | next 9 events |
| `terminuebersicht_quer.pdf` | A4 Landscape | next 6 events |
| `repaircafe_hoch.pdf` | A4 Portrait | Repair Café — all events |
| `repaircafe_quer.pdf` | A4 Landscape | Repair Café — all events |

## Configuration

The API URL is defined in `compose.yaml` and points to the live data from erfindergeist.org.
For a different URL, create a `.env` file (see `.env.example`).

## Automated Generation

A GitHub Actions workflow runs **every Monday at 03:00 UTC** and publishes a new
[Release](../../releases) with all four PDFs.
The workflow can also be triggered manually via **Actions → Termine PDF generieren → Run workflow**.

## VS Code Extensions

This project recommends two extensions (`.vscode/extensions.json`):

- **[PDF Preview](https://marketplace.visualstudio.com/items?itemName=tomoki1207.pdf)** (`tomoki1207.pdf`) — preview generated PDFs directly in the editor without leaving VS Code.
- **[Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml)** (`samuelcolvin.jinjahtml`) — syntax highlighting for the Jinja2 HTML templates in `src/templates/`, suppresses false HTML error markers caused by `{{ }}` and `{% %}` expressions.

---

[erfindergeist.org](https://erfindergeist.org) · kontakt@erfindergeist.org
