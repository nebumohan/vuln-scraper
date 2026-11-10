# vuln-scraper

Build-to-break project #2: a Python web scraper used to learn HTTP internals, rate limiting and bot detection. I built a deliberately weak target server, got past its defenses, then fixed it.

> Everything here runs against practice sites (`quotes.toscrape.com`) or my own local server. Never point these techniques at systems you don't own or have permission to test.

## Stack
Python, requests, BeautifulSoup, Flask, Flask-Limiter

## Milestones

| # | Topic | File |
|---|-------|------|
| 1 | HTTP internals: request/response, headers, User-Agent | `m1_http.py` |
| 2 | Parsing, pagination, retry with backoff on 429, JSON export | `m2_parse.py`, `m2_paginate.py`, `m2_final.py` |
| 3 | Defense: per-IP rate limit + User-Agent block on my own server | `target_fixed.py` |
| 4 | Evasion: `X-Forwarded-For` rate-limit bypass, then the fix | `target_vuln.py`, `target_fixed.py` |

## Findings

### 1. User-Agent blocking is trivially bypassed
- **Weakness:** the server returns 403 for `python-requests` in the User-Agent.
- **PoC:** send a browser-like `User-Agent` header.
- **Lesson:** the header is self-declared by the client, so it's a weak signal on its own. It also blocks legitimate `requests`-based integrations (false positives).

### 2. Rate-limit bypass via trusted `X-Forwarded-For`
- **Weakness:** `target_vuln.py` keys the rate limiter on the first value of the `X-Forwarded-For` header, which the client controls.
- **PoC:** the scraper (`m2_final.py`) sends a random fake IP in `X-Forwarded-For` on every request, so each request gets a fresh rate-limit bucket. The 5-per-minute limit never triggers.
- **Root cause:** trusting client-supplied input for a security decision.
- **Fix** (`target_fixed.py`): key the limiter on `get_remote_address`, the real connection address. Behind a real reverse proxy, use Werkzeug's `ProxyFix` with `x_for=1` so only one trusted hop is honored.

## Defensive takeaways
- Never trust headers a client can set (`X-Forwarded-For`, `User-Agent`) for security decisions.
- Per-IP limiting alone isn't enough: attackers rotate IPs and many real users share one. Layer per-IP, per-account and per-session limits with behavioral signals and challenges.
- Scrapers should retry on 429 (honor `Retry-After`, back off exponentially) but not on 403.
- Detect failure by missing structure (expected elements absent), not by guessing block-page wording.

## Run it
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4 flask flask-limiter

python target_fixed.py      # or target_vuln.py
python m2_final.py          # in a second terminal
```

Related: [vuln-notes-app](https://github.com/nebumohan/vuln-notes-app) (project 1: IDOR, session forgery, reset tokens, rate limiting)