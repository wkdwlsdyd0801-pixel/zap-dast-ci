# zap-dast-ci

Automated **DAST** (dynamic security scanning) of a running web app with the
OWASP ZAP baseline scan, wired into GitHub Actions and reproducible locally.

A tiny Flask app serves the same page two ways: `/` ships **without** security
headers (so the scan flags it) and `/secure` ships **with** them (so it passes).
`rules.tsv` marks the missing-header alerts as hard failures, so a regression
that drops a header breaks the build.

> ⚠️ The `/` route is intentionally insecure. Run locally only.

## Run

```bash
# Tests + the app
pip install -r requirements.txt
pytest -q
gunicorn --bind 0.0.0.0:5000 app:app

# Full ZAP baseline scan locally (needs Docker) -> writes zap-report.html
./zap_baseline.sh
```

## CI

The GitHub Actions workflow lives at `ci/zap-baseline.yml`. To activate it,
copy it into `.github/workflows/` (the push token needs the `workflow` scope):

```bash
mkdir -p .github/workflows && cp ci/zap-baseline.yml .github/workflows/
```
