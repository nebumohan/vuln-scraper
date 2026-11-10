from flask import Flask, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

def client_key():
    xff = request.headers.get("X-Forwarded-For")
    return xff.split(",")[0].strip() if xff else request.remote_addr


limiter = Limiter(
    client_key,
    app=app,
    default_limits=["5 per minute"],
    headers_enabled=True,
)


@app.before_request
def block_bots():
    ua = request.headers.get("User-Agent", "")
    if "python-requests" in ua:
        abort(403)


@app.route("/", defaults={"n": 1})
@app.route("/page/<int:n>/")
def page(n):
    if n > 10:
        abort(404)
    quotes = "".join(
        f'<div class="quote"><span class="text">Quote {n}-{i}</span>'
        f'<small class="author">Author {i}</small></div>'
        for i in range(1, 11)
    )
    nxt = f'<li class="next"><a href="/page/{n+1}/">Next</a></li>' if n < 10 else ""
    return f"<html><body>{quotes}<ul>{nxt}</ul></body></html>"


if __name__ == "__main__":
    app.run(port=5000)