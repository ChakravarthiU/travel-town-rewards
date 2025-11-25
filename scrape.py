
import json
import time
import requests
from bs4 import BeautifulSoup
import os

SOURCE_NAME = "frvr"
SOURCE_URL = "https://frvr.com/blog/travel-town-free-energy-links"
RAW_HTML_FILE = "data/raw_page.html"
OUTPUT_FILE = "data/codes.json"

def fetch_html(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    with open(RAW_HTML_FILE, "w", encoding="utf-8") as raw_file:
        raw_file.write(response.text)
    return response.text

def parse_frvr(html):
    soup = BeautifulSoup(html, "lxml")
    entries = []
    # Look for links in article content
    for a in soup.select("article a[href]"):
        href = a.get("href")
        text = a.get_text(strip=True)
        if href and href.startswith("https://") and "travel-town" in href:
            entries.append({
                "reward": text if text else "Free Energy",
                "url": href,
                "source": SOURCE_NAME,
                "date": None
            })
    return entries

def main():
    html = fetch_html(SOURCE_URL)
    parsed_entries = parse_frvr(html)

    # Remove duplicates
    seen = set()
    unique_entries = []
    for e in parsed_entries:
        if e["url"] not in seen:
            seen.add(e["url"])
            unique_entries.append(e)

    payload = {
        "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "entries": unique_entries
    }

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Scraped {len(unique_entries)} links from FRVR Blog and saved to data/codes.json")

if __name__ == "__main__":
    main()
