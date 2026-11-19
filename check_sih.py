import hashlib
import os
import requests
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup

URL = "https://www.sih.gov.in/"
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
KEYWORDS = ["shortlisted", "result", "grand finale 2026", "results out"]

def check_sih():
    print("1. Fetching SIH website with Chrome TLS fingerprint...", flush=True)
    res = curl_requests.get(URL, impersonate="chrome", timeout=20)
    print(f"2. Got status code: {res.status_code}", flush=True)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    found = [kw for kw in KEYWORDS if kw in text]
    page_hash = hashlib.sha256(text.encode()).hexdigest()

    last_hash = ""
    if os.path.exists("last_hash.txt"):
        with open("last_hash.txt", "r") as f:
            last_hash = f.read().strip()

    if page_hash != last_hash:
        print("3. Change detected! Saving hash and sending alert...", flush=True)
        with open("last_hash.txt", "w") as f:
            f.write(page_hash)

        msg = f"SIH 2026 site updated! Keywords matched: {found}\nCheck: {URL}"
        r = requests.post(
            WEBHOOK_URL,
            data=msg.encode("utf-8"),
            headers={"Title": "SIH 2026 Update", "Priority": "high"},
            timeout=15
        )
        print(f"4. Notification sent! Status: {r.status_code}", flush=True)
    else:
        print("3. No changes detected.", flush=True)

if __name__ == "__main__":
    check_sih()
