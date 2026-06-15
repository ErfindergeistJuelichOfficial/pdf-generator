import os
import requests
from datetime import datetime

WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
MONTHS_DE = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]
TAGS_JSON_URL = "https://share.erfindergeist.org/config/tags.json"
CHRONICLE_JSON_URL = "https://share.erfindergeist.org/config/chronicle.json"
LINKS_JSON_URL = "https://share.erfindergeist.org/config/links.json"

def _load_links() -> dict[str, dict]:
    response = requests.get(LINKS_JSON_URL, timeout=15)
    response.raise_for_status()
    data = response.json()
    result = {}
    for list_item in data.get("itemListElement", []):
        # @id / url / title live inside a nested "item" object
        inner = list_item.get("item", list_item)
        uid = inner.get("@id", "")
        url = inner.get("url", "")
        title = inner.get("title", "")
        if uid and url:
            result[uid] = {"url": url, "titel": title}
    return result


def _load_tags() -> tuple[dict, dict]:
    response = requests.get(TAGS_JSON_URL, timeout=15)
    response.raise_for_status()
    data = response.json()
    location_tags = {f"#{tag}": v["location"] for tag, v in data.get("location_tags", {}).items()}
    description_tags = {f"#{tag}": v["description"] for tag, v in data.get("description_tags", {}).items()}
    return location_tags, description_tags


def _parse_tags(description: str) -> list[str]:
    return [word.lower() for word in description.split() if word.startswith("#")]


def _resolve_location(tags: list[str], fallback: str, location_tags: dict) -> str:
    for tag in tags:
        if tag in location_tags:
            return location_tags[tag]
    return fallback or ""


def _resolve_description(tags: list[str], description_tags: dict) -> str:
    for tag in tags:
        if tag in description_tags:
            return description_tags[tag]
    return ""


def _fmt_date(iso: str) -> str:
    dt = datetime.fromisoformat(iso)
    wd = WEEKDAYS[dt.weekday()]
    return f"{wd}, {dt.day:02d}.{dt.month:02d}.{dt.year}"


def _fmt_time(iso: str) -> str:
    dt = datetime.fromisoformat(iso)
    return f"{dt.hour:02d}:{dt.minute:02d}"


def fetch_chronicle() -> dict[int, list[dict]]:
    links_map = _load_links()
    response = requests.get(CHRONICLE_JSON_URL, timeout=15)
    response.raise_for_status()
    data = response.json()

    by_year: dict[int, list[dict]] = {}
    for item in data.get("itemListElement", []):
        date_str = item.get("date", "")
        if not date_str:
            continue
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year = dt.year
        wd = WEEKDAYS[dt.weekday()]
        raw_link_ids = item.get("link_ids") or []
        event = {
            "titel": item.get("title", ""),
            "datum": f"{wd}, {dt.day:02d}.{dt.month:02d}.{dt.year}",
            "datum_iso": date_str,
            "monat_num": dt.month,
            "ort": item.get("location") or "",
            "tags": item.get("tags") or [],
            "beschreibung": item.get("description") or "",
            "links": [links_map[lid] for lid in raw_link_ids if lid in links_map],
        }
        by_year.setdefault(year, []).append(event)

    for year_events in by_year.values():
        year_events.sort(key=lambda e: e["datum_iso"])

    return dict(sorted(by_year.items()))


def fetch() -> list[dict]:
    location_tags, description_tags = _load_tags()

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
            "ort": _resolve_location(tags, event.get("location", ""), location_tags),
            "beschreibung": _resolve_description(tags, description_tags),
            "tags": tags,
            "_sort_key": event["dtstart"],
        })

    termine.sort(key=lambda e: e["_sort_key"])
    for t in termine:
        del t["_sort_key"]
    return termine
