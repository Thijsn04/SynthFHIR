# SynthFHIR container image.
# Build:  docker build -t synthfhir .
# Run:    docker run --rm -p 8000:8000 synthfhir
FROM python:3.12-slim AS base

# Keep Python lean and unbuffered for clean container logs.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so the layer caches across code changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source.
COPY . .

# Run as a non-root user.
RUN useradd --create-home --uid 10001 synthfhir \
    && chown -R synthfhir:synthfhir /app
USER synthfhir

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS dev

USER root
RUN pip install --no-cache-dir pytest pytest-asyncio httpx ruff mypy
USER synthfhir
