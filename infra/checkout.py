#!/usr/bin/env python3
"""
Magic Hair Styler — checkout service.

Listens on 127.0.0.1:$PORT. Caddy on magichairstyler.com reverse-proxies
/api/* to this service.

Endpoints
---------
GET  /api/healthz              Liveness probe.
GET  /api/config               Returns publishable key + price/currency so
                               the browser can mount Stripe Elements.
POST /api/checkout             Tier 2: hosted Checkout Session. Returns
                               { url, id } for a top-level redirect.
POST /api/embedded-session     Tier 3: embedded Checkout Session. Returns
                               { clientSecret, id } for stripe.initEmbedded-
                               Checkout({ clientSecret }).

Env
---
STRIPE_API_KEY             required, sk_live_* or sk_test_*
STRIPE_PUBLISHABLE_KEY     optional, pk_live_* or pk_test_*. If absent,
                           /api/config returns publishableKey=null and the
                           Tier 3 frontend silently falls back to Tier 2.
STRIPE_PRICE_ID            optional, defaults to AirStyler GBP 49.99 price.
PORT                       optional, defaults to 8095.
ORIGIN                     optional, defaults to https://magichairstyler.com.

Dependencies: Python standard library only.
"""
import http.server
import json
import os
import socketserver
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from http import HTTPStatus

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "").strip()
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "").strip()
STRIPE_PRICE_ID = os.environ.get(
    "STRIPE_PRICE_ID", "price_1T9GkIG8rZzTnbqHJCu8j00r"
).strip()
PORT = int(os.environ.get("PORT", "8095"))
ORIGIN = os.environ.get("ORIGIN", "https://magichairstyler.com").rstrip("/")

FINISHES = {
    "white": "White & Gold Edition",
    "pink": "Blush Pink Edition",
    "navy": "Navy & Gold Edition",
    "black": "Midnight Black Edition",
}

SHIPPING_COUNTRIES = [
    "GB", "US", "CA", "AU", "NZ", "IE",
    "FR", "DE", "ES", "IT", "NL", "BE", "AT", "PT", "SE", "DK", "NO", "FI",
    "CH", "PL", "CZ", "AE", "SG", "HK", "JP", "KR",
]

_rate_buckets = {}


def rate_limited(ip: str) -> bool:
    now = time.time()
    window, limit = 60.0, 30
    bucket = _rate_buckets.setdefault(ip, deque())
    while bucket and bucket[0] < now - window:
        bucket.popleft()
    if len(bucket) >= limit:
        return True
    bucket.append(now)
    return False


def stripe_post(path: str, params):
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.stripe.com/v1/{path}",
        data=data,
        headers={
            "Authorization": f"Bearer {STRIPE_API_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Stripe-Version": "2024-06-20",
            "Idempotency-Key": os.urandom(16).hex(),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8", errors="replace"))
        except Exception:
            return {"error": {"message": f"HTTP {e.code}"}}
    except urllib.error.URLError as e:
        return {"error": {"message": f"upstream error: {e.reason}"}}


def _finish_common_params(finish: str):
    """Finish / metadata / shipping / custom fields shared by both
    hosted and embedded sessions."""
    finish_key = finish if finish in FINISHES else "white"
    finish_label = FINISHES[finish_key]
    params = [
        ("mode", "payment"),
        ("line_items[0][price]", STRIPE_PRICE_ID),
        ("line_items[0][quantity]", "1"),
        ("allow_promotion_codes", "true"),
        ("billing_address_collection", "required"),
        ("phone_number_collection[enabled]", "true"),
        ("consent_collection[terms_of_service]", "required"),
        ("metadata[finish]", finish_key),
        ("metadata[finish_label]", finish_label),
        ("metadata[source]", "magichairstyler.com"),
        ("custom_text[submit][message]",
         f"You selected the {finish_label}. Confirm below."),
    ]
    for i, cc in enumerate(SHIPPING_COUNTRIES):
        params.append(
            (f"shipping_address_collection[allowed_countries][{i}]", cc)
        )
    # Forced finish-confirmation dropdown
    params.extend([
        ("custom_fields[0][key]", "finish"),
        ("custom_fields[0][label][type]", "custom"),
        ("custom_fields[0][label][custom]", "Confirm finish"),
        ("custom_fields[0][type]", "dropdown"),
        ("custom_fields[0][optional]", "false"),
    ])
    for i, (k, v) in enumerate(FINISHES.items()):
        params.append(
            (f"custom_fields[0][dropdown][options][{i}][label]", v)
        )
        params.append(
            (f"custom_fields[0][dropdown][options][{i}][value]", k)
        )
    return params


def build_hosted_session_params(finish: str):
    params = _finish_common_params(finish)
    params.extend([
        ("success_url", f"{ORIGIN}/thank-you.html?session_id={{CHECKOUT_SESSION_ID}}"),
        ("cancel_url", f"{ORIGIN}/?order=cancelled"),
    ])
    return params


def build_embedded_session_params(finish: str):
    params = _finish_common_params(finish)
    params.extend([
        ("ui_mode", "embedded"),
        ("return_url", f"{ORIGIN}/thank-you.html?session_id={{CHECKOUT_SESSION_ID}}"),
        ("redirect_on_completion", "always"),
    ])
    return params


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "magichairstyler-checkout/1.1"

    def log_message(self, fmt, *args):
        print(f"[{self.address_string()}] {fmt % args}", flush=True)

    def _send_json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/healthz", "/api/healthz"):
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "service": "checkout",
                    "tier3_ready": bool(STRIPE_PUBLISHABLE_KEY),
                },
            )
            return
        if path == "/api/config":
            self._send_json(
                HTTPStatus.OK,
                {
                    "publishableKey": STRIPE_PUBLISHABLE_KEY or None,
                    "amount": 4999,
                    "currency": "gbp",
                    "amountDisplay": "£49.99",
                    "productName": "AirStyler 5-in-1 Magic Hair Styler",
                    "finishes": FINISHES,
                },
            )
            return
        if path == "/api/session":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            sid = (qs.get("session_id") or [""])[0]
            if not sid or not sid.startswith("cs_"):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "session_id required"})
                return
            try:
                req = urllib.request.Request(
                    f"https://api.stripe.com/v1/checkout/sessions/{sid}",
                    headers={"Authorization": f"Bearer {STRIPE_API_KEY}"},
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = json.load(r)
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "id": data.get("id"),
                        "status": data.get("status"),
                        "payment_status": data.get("payment_status"),
                        "customer_email": (data.get("customer_details") or {}).get("email"),
                        "amount_total": data.get("amount_total"),
                        "currency": data.get("currency"),
                        "metadata": data.get("metadata"),
                    },
                )
            except Exception as e:
                self._send_json(HTTPStatus.BAD_GATEWAY, {"error": str(e)[:200]})
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self):
        ip = (self.headers.get("X-Forwarded-For")
              or self.client_address[0] or "0.0.0.0").split(",")[0].strip()
        if rate_limited(ip):
            self._send_json(
                HTTPStatus.TOO_MANY_REQUESTS, {"error": "rate limited"}
            )
            return
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
            if not isinstance(body, dict):
                body = {}
        except Exception:
            body = {}
        finish = str(body.get("finish") or "white").lower()

        if not STRIPE_API_KEY:
            self._send_json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {"error": "checkout not configured"},
            )
            return

        if path in ("/api/checkout", "/checkout"):
            resp = stripe_post("checkout/sessions", build_hosted_session_params(finish))
            if "error" in resp:
                print("[stripe-error]", json.dumps(resp.get("error"))[:300], flush=True)
                self._send_json(
                    HTTPStatus.BAD_GATEWAY,
                    {"error": "unable to create checkout session"},
                )
                return
            url = resp.get("url")
            sid = resp.get("id")
            if not url:
                self._send_json(HTTPStatus.BAD_GATEWAY, {"error": "invalid stripe response"})
                return
            print(f"[checkout:hosted] {sid} finish={finish} ip={ip}", flush=True)
            self._send_json(HTTPStatus.OK, {"url": url, "id": sid})
            return

        if path == "/api/embedded-session":
            resp = stripe_post("checkout/sessions", build_embedded_session_params(finish))
            if "error" in resp:
                print("[stripe-error]", json.dumps(resp.get("error"))[:300], flush=True)
                self._send_json(
                    HTTPStatus.BAD_GATEWAY,
                    {"error": "unable to create embedded session"},
                )
                return
            cs = resp.get("client_secret")
            sid = resp.get("id")
            if not cs:
                self._send_json(HTTPStatus.BAD_GATEWAY, {"error": "invalid stripe response"})
                return
            print(f"[checkout:embedded] {sid} finish={finish} ip={ip}", flush=True)
            self._send_json(HTTPStatus.OK, {"clientSecret": cs, "id": sid})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    if not STRIPE_API_KEY:
        print(
            "WARNING: STRIPE_API_KEY not set — /api/checkout will return 503",
            file=sys.stderr,
        )
    if not STRIPE_PUBLISHABLE_KEY:
        print(
            "INFO: STRIPE_PUBLISHABLE_KEY not set — Tier 3 embedded checkout "
            "will fall back to Tier 2 hosted. Paste pk_live_* into backend.env "
            "and restart to enable.",
            file=sys.stderr,
        )
    with Server(("127.0.0.1", PORT), Handler) as httpd:
        print(
            f"magichairstyler-checkout listening on 127.0.0.1:{PORT} "
            f"(price={STRIPE_PRICE_ID}, origin={ORIGIN}, "
            f"tier3={'on' if STRIPE_PUBLISHABLE_KEY else 'fallback'})",
            flush=True,
        )
        httpd.serve_forever()


if __name__ == "__main__":
    main()
