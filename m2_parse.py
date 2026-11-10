import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/"

r = requests.get(URL, timeout=10)
soup = BeautifulSoup(r.text, "html.parser")

quotes = soup.select("div.quote")

if len(quotes) != 10:
    print(f"WARNING: expected 10 quotes, got {len(quotes)}")

for q in quotes:
    text_el = q.select_one("span.text")
    author_el = q.select_one("small.author")

    text = text_el.get_text(strip=True) if text_el else "N/A"
    author = author_el.get_text(strip=True) if author_el else "N/A"

    print(f"{author}: {text}")

