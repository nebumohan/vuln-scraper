import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/"
all_quotes = []

while url:
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        print(f"Stopping: got {r.status_code} on {url}")
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
        all_quotes.append((author, text))

    print(f"{url} -> {len(quotes)} quotes")

    next_a = soup.select_one("li.next > a")
    url = urljoin(url, next_a["href"]) if next_a else None

    time.sleep(1)

print(f"Total: {len(all_quotes)}")