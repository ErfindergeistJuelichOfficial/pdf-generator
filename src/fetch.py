import os
import requests
from datetime import datetime

WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

LOCATION_TAGS = {
    "#awo": "Erfindergeist Werkstatt, Jülich",
    "#stadtbücherei": "Stadtbücherei Jülich",
}

DESCRIPTION_TAGS = {
    "#offenewerkstatt": (
        "Wir bieten der Öffentlichkeit eine offene Werkstatt mit Raum, Maschinen und "
        "Werkzeug zur erfolgreichen Umsetzung eigener Projekte."
    ),
    "#stammtisch": (
        "Lockerer Austausch für Mitglieder, bringt eure aktuellen Ideen oder Prototypen "
        "mit und lasst uns in entspannter Runde fachsimpeln."
    ),
    "#repaircafe": (
        "Möchtest du etwas reparieren lassen oder reparierst selber gerne kaputte Dinge? "
        "Dann bist du im Repair Café genau richtig. Komm einfach unangemeldet vorbei und "
        "bring deinen defekten Gebrauchsgegenstand mit."
    ),
}


def _parse_tags(description: str) -> list[str]:
    return [word.lower() for word in description.split() if word.startswith("#")]


def _resolve_location(tags: list[str], fallback: str) -> str:
    for tag in tags:
        if tag in LOCATION_TAGS:
            return LOCATION_TAGS[tag]
    return fallback or ""


def _resolve_description(tags: list[str]) -> str:
    for tag in tags:
        if tag in DESCRIPTION_TAGS:
            return DESCRIPTION_TAGS[tag]
    return ""


def _fmt_date(iso: str) -> str:
    dt = datetime.fromisoformat(iso)
    wd = WEEKDAYS[dt.weekday()]
    return f"{wd}, {dt.day:02d}.{dt.month:02d}.{dt.year}"


def _fmt_time(iso: str) -> str:
    dt = datetime.fromisoformat(iso)
    return f"{dt.hour:02d}:{dt.minute:02d}"


def fetch() -> list[dict]:
    url = os.environ["TERMINE_JSON_URL"]
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    raw = response.json()

    termine = []
    for event in raw:
        title = event.get("summary", "")
        desc_raw = event.get("description", "")
        status = event.get("status", "")

        if status != "CONFIRMED":
            continue
        if "PLATZHALTER" in title.upper():
            continue

        tags = _parse_tags(desc_raw)
        if "#platzhalter" in tags:
            continue

        termine.append({
            "titel": title,
            "datum": _fmt_date(event["dtstart"]),
            "zeit": f"{_fmt_time(event['dtstart'])}–{_fmt_time(event['dtend'])}",
            "ort": _resolve_location(tags, event.get("location", "")),
            "beschreibung": _resolve_description(tags),
            "_sort_key": event["dtstart"],
        })

    termine.sort(key=lambda e: e["_sort_key"])
    for t in termine:
        del t["_sort_key"]
    return termine
