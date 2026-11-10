import requests

URL = "https://quotes.toscrape.com/"

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def looks_blocked(resp):
    ctype = resp.headers.get("Content-Type", "")
    if "text/html" not in ctype:
        return True
    if resp.status_code in (403, 429):
        return True
    if "captcha" in resp.text.lower():
        return True
    return False


r1 = requests.get(URL, timeout=10)
r2 = requests.get(URL, headers=browser_headers, timeout=10)

for name, r in (("default", r1), ("browser-like", r2)):
    print(name, r.status_code, len(r.content), r.headers.get("Content-Type"))
    print("  blocked?", looks_blocked(r))

print("\nr1 sent:", dict(r1.request.headers))
print("\nr2 sent:", dict(r2.request.headers))