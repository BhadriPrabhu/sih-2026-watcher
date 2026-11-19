import hashlib
import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.sih.gov.in/"
WEBHOOK_URL = os.environ["WEBHOOK_URL"]  # Discord/Slack/ntfy.sh URL
KEYWORDS = ["shortlisted", "result", "grand finale 2026","results out"]

def check_sih():
    res = requests.get(URL, timeout=15)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    # Option 1: Keyword trigger
    found = [kw for kw in KEYWORDS if kw in text]
    
    # Option 2: Hash the announcements/marquee section to detect ANY update
    page_hash = hashlib.sha256(text.encode()).hexdigest()
    
    # Compare with last saved hash (stored in a repo file or GitHub Actions cache)
    last_hash = ""
    if os.path.exists("last_hash.txt"):
        with open("last_hash.txt", "r") as f:
            last_hash = f.read().strip()

    if page_hash != last_hash:
        with open("last_hash.txt", "w") as f:
            f.write(page_hash)
        
        msg = f"SIH 2026 site updated! Keywords matched: {found}\nCheck: {URL}"
        requests.post(WEBHOOK_URL, data=msg.encode("utf-8"))

if __name__ == "__main__":
    check_sih()
