import json
import time
import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://frvr.com/blog/travel-town-free-energy-links"
SOURCE_NAME = "frvr"
OUTPUT_FILE = "data/codes.json"
RAW_HTML_FILE = "data/raw_page.html"


def make_soup(html: str) -> BeautifulSoup:
    """Create BeautifulSoup with lxml, fallback to html.parser."""
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


def fetch_html(url: str) -> str:
    response = requests.get(url, timeout=25)
    response.raise_for_status()
    with open(RAW_HTML_FILE, "w", encoding="utf-8") as raw_file:
        raw_file.write(response.text)
    return response.text


def norm(text: str) -> str:
    return " ".join((text or "").split())


def parse_tables_for_entries(soup: BeautifulSoup) -> list[dict]:
    """
    Parse all <table> elements assuming columns: Date | Reward | Link.
    Returns list of dicts: {date, reward, url, source}.
    """
    entries: list[dict] = []
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows or len(rows) < 2:
            continue

        # Skip header row; parse data rows
        for tr in rows[1:]:
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            date = norm(tds[0].get_text())
            reward = norm(tds[1].get_text())
            link_tag = tds[2].find("a", href=True)
            url = link_tag["href"] if link_tag else None
            if url:
                entries.append(
                    {
                        "date": date or None,
                        "reward": reward or None,
                        "url": url,
                        "source": SOURCE_NAME,
                    }
                )
    return entries


def dedupe_by_url(entries: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for e in entries:
        u = e.get("url")
        if u and u not in seen:
            seen.add(u)
            unique.append(e)
    return unique


def write_json(entries: list[dict], out_path: str = "data/codes.json"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    payload = {
        "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "entries": entries,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(entries)} entries to {out_path}")


def main():
    html = fetch_html(SOURCE_URL)

    soup = make_soup(html)
    entries = parse_tables_for_entries(soup)
    entries = dedupe_by_url(entries)
    write_json(entries, OUTPUT_FILE)


if __name__ == "__main__":
    main()
