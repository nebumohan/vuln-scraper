import json
import time
import requests
import random
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def fake_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch(url, retries=3):
    for attempt in range(retries):
        headers = {**browser_headers, "X-Forwarded-For": fake_ip()}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After", "")
            wait = int(retry_after) if retry_after.isdigit() else 2 ** attempt
            print(f"429 on {url}, waiting {wait}s")
            time.sleep(wait)
            continue
        return r
    return None


url = "http://127.0.0.1:5000/"
all_quotes = []

while url:
    r = fetch(url)
    if r is None or r.status_code != 200:
        print(f"Stopping on {url}")
        break

    soup = BeautifulSoup(r.text, "html.parser")
    quotes = soup.select("div.quote")
    if not quotes:
        print(f"Stopping: no quotes found on {url}")
        break

    for q in quotes:
        text_el = q.select_one("span.text")
        author_el = q.select_one("small.author")
        text = text_el.get_text(strip=True) if text_el else "N/A"
        author = author_el.get_text(strip=True) if author_el else "N/A"
        all_quotes.append({"author": author, "text": text})

    print(f"{url} -> {len(quotes)} quotes")

    next_a = soup.select_one("li.next > a")
    url = urljoin(url, next_a["href"]) if next_a else None
    time.sleep(1)

with open("quotes.json", "w", encoding="utf-8") as f:
    json.dump(all_quotes, f, indent=2, ensure_ascii=False)

print(f"Saved {len(all_quotes)} quotes to quotes.json")