FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Public Mozilla CA bundle for TLS database connections (TiDB Cloud Serverless).
COPY deploy/cacert.pem /etc/ssl/certs/tidbcloud-cacert.pem

EXPOSE 8000

# Render injects $PORT for the container; default to 8000 for local Docker runs.
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} app:app