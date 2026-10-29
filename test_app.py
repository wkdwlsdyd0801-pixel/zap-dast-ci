"""Unit tests: assert the insecure route is missing the headers the secure
route adds. These run in CI *before* the DAST scan as a fast sanity gate."""

import app as target


def client():
    # Flask's built-in test client exercises routes without a live server.
    return target.app.test_client()


def test_insecure_route_has_no_csp():
    # The whole demo depends on "/" lacking a CSP so ZAP has something to find.
    resp = client().get("/")
    assert resp.status_code == 200
    assert "Content-Security-Policy" not in resp.headers


def test_secure_route_sets_all_hardening_headers():
    # Every header in the hardened set must actually be present on /secure,
    # otherwise the "fixed" surface would still trip the scanner.
    resp = client().get("/secure")
    assert resp.status_code == 200
    for name in target.SECURE_HEADERS:
        assert name in resp.headers


def test_healthz_ok():
    # CI polls this before scanning; it must return 200 with status ok.
    resp = client().get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
