import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

URL = "https://mobilegamecentral.com/freebies/free-travel-town-energy-links-updated-daily/"
OUTPUT_FILE = "data/codes.json"
RAW_HTML_FILE = "data/raw_page.html"


def fetch_codes():
    response = requests.get(URL)

    # Save raw HTML response
    with open(RAW_HTML_FILE, "w", encoding="utf-8") as raw_file:
        raw_file.write(response.text)

    soup = BeautifulSoup(response.text, "html.parser")

    codes = []
    today = datetime.utcnow().strftime("%B %d, %Y")  # e.g., "May 27, 2025"
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%B %d, %Y")

    # Find all headings with date
    headings = soup.find_all(["h3"])
    for h in headings:
        date_text = h.get_text(strip=True)
        if today in date_text or yesterday in date_text:
            ol = h.find_next_sibling("ol")
            if ol:
                for li in ol.find_all("li"):
                    link = li.find("a")
                    if link and link.get("href"):
                        codes.append(
                            {
                                "code": link.get("href"),
                                "text": link.get_text(strip=True),
                                "date": date_text,
                            }
                        )

    with open(OUTPUT_FILE, "w") as f:
        json.dump(codes, f, indent=2)


if __name__ == "__main__":
    fetch_codes()
