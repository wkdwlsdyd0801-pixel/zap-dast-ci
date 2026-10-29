# Small, pinned base so the scan target is reproducible across runs.
FROM python:3.12-slim

WORKDIR /app

# Install deps first so this layer is cached when only source changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Run under a non-root user: a scan target should not model bad container
# hygiene on top of the deliberately missing HTTP headers.
RUN useradd --create-home appuser
USER appuser

EXPOSE 5000

# gunicorn is the production server ZAP scans, not Flask's dev server.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
