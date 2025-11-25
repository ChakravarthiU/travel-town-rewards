import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta

URL = "https://mobilegamecentral.com/freebies/free-travel-town-energy-links-updated-daily/"
URL = "https://frvr.com/blog/travel-town-free-energy-links/"
OUTPUT_FILE = "data/codes.json"
RAW_HTML_FILE = "data/raw_page.html"
DAYS_TO_LOOK_BACK = 5

def fetch_codes():
    response = requests.get(URL)

    # Save raw HTML response
    with open(RAW_HTML_FILE, "w", encoding="utf-8") as raw_file:
        raw_file.write(response.text)

    soup = BeautifulSoup(response.text, "html.parser")

    # Build list of date formats to match (e.g., "May 6, 2025" and "May 06, 2025")
    valid_dates = set()
    for i in range(DAYS_TO_LOOK_BACK):
        dt = datetime.utcnow() - timedelta(days=i)
        base_date = dt.strftime("%B %-d, %Y") if os.name != "nt" else dt.strftime("%B %#d, %Y")
        padded_date = dt.strftime("%B %d, %Y")
        valid_dates.add(base_date)
        valid_dates.add(padded_date)

    codes = []
    headings = soup.find_all(["h3"])
    for h in headings:
        date_text = h.get_text(strip=True)
        if any(valid_date in date_text for valid_date in valid_dates):
            ol = h.find_next_sibling("ol")
            if ol:
                for li in ol.find_all("li"):
                    link = li.find("a")
                    if link and link.get("href"):
                        full_text = li.get_text(" ", strip=True)
                        energy_text = full_text.replace(link.get_text(strip=True), "").strip(" -")
                        codes.append({
                            "code": link.get("href"),
                            "text": link.get_text(strip=True),
                            "energy": energy_text,
                            "date": date_text,
                        })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(codes, f, indent=2)

if __name__ == "__main__":
    fetch_codes()
