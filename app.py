"""Tiny Flask target app used to demonstrate automated DAST with OWASP ZAP.

The app exposes the SAME page two ways so a baseline scan shows a clear
before/after:

* ``/``        - serves the page WITHOUT security response headers, so the
                 ZAP baseline scan raises passive-scan alerts
                 (missing CSP, missing anti-clickjacking header, etc.).
* ``/secure``  - serves the identical page WITH a hardened header set, so the
                 same alerts disappear.

DAST (Dynamic Application Security Testing) scans a *running* app from the
outside, the way an attacker sees it, so this app is the thing ZAP talks to.
It is deliberately minimal and has no database or user input - the point is
the scanning pipeline, not the app.
"""

from flask import Flask, Response

app = Flask(__name__)

# A single HTML body reused by both routes so the only difference a scanner
# sees is the response headers, not the markup.
PAGE = b"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>ZAP DAST demo</title></head>
<body><h1>ZAP DAST demo</h1><p>Compare / and /secure headers.</p></body>
</html>"""

# The hardened header set. Each line maps to a specific passive-scan alert that
# ZAP's baseline scan raises when the header is absent.
SECURE_HEADERS = {
    # Blocks the page from being framed -> defeats clickjacking.
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
    # Legacy clickjacking defence for older browsers that ignore CSP.
    "X-Frame-Options": "DENY",
    # Stops the browser from MIME-sniffing a response into an executable type.
    "X-Content-Type-Options": "nosniff",
    # Forces HTTPS for the configured lifetime -> prevents SSL-strip downgrade.
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    # Do not leak the full URL (query string, path) to cross-origin targets.
    "Referrer-Policy": "no-referrer",
}


@app.get("/")
def insecure():
    # No security headers are set here on purpose: this is the "vulnerable"
    # surface the baseline scan is expected to flag.
    return Response(PAGE, mimetype="text/html")


@app.get("/secure")
def secure():
    resp = Response(PAGE, mimetype="text/html")
    # Applying the same header set a real app would ship with makes the
    # corresponding ZAP alerts go away - this is the "fixed" surface.
    for name, value in SECURE_HEADERS.items():
        resp.headers[name] = value
    return resp


@app.get("/healthz")
def healthz():
    # Lightweight liveness probe the CI job polls before it starts the scan,
    # so the scan never runs against an app that has not finished booting.
    return {"status": "ok"}


if __name__ == "__main__":
    # Bind to all interfaces so the scanner container can reach the app over
    # the Docker network in CI. Host-only in local use.
    app.run(host="0.0.0.0", port=5000)
