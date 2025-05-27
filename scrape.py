import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

URL = "https://mobilegamecentral.com/freebies/free-travel-town-energy-links-updated-daily/"
OUTPUT_FILE = "data/codes.json"

def fetch_codes():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    codes = []
    for li in soup.select('li'):  # Adjust this selector based on actual structure
        text = li.get_text(strip=True)
        if "Reward Code:" in text:
            code = text.split("Reward Code:")[-1].strip()
            codes.append({"code": code, "date": datetime.utcnow().isoformat()})

    with open(OUTPUT_FILE, "w") as f:
        json.dump(codes, f, indent=2)

if __name__ == "__main__":
    fetch_codes()
