# Deployment

SynthFHIR is a single stateless process. It stores no data and needs no
database or network access, so it is simple to run anywhere.

## Docker

Build and run the image:

```bash
docker build -t synthfhir .
docker run --rm -p 8000:8000 synthfhir
```

The image runs as a non-root user and defines a `/health` healthcheck. Open
`http://localhost:8000/`.

## Docker Compose

```bash
docker compose up --build
```

This builds the image and runs it on port 8000 with the healthcheck wired in.

## Running with uvicorn directly

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Multiple workers are safe. Generation is serialized per process to keep seeded
output reproducible (see [Reproducibility](reproducibility.md)), so if you need
higher throughput for seeded workloads, scale out with more workers or processes
behind a load balancer.

## Behind a reverse proxy

Serve it behind nginx, Caddy, or a cloud load balancer. The application is
entirely under `/`, with the API under `/api`, the docs at `/docs`, and the web
console at `/`. Forward the standard proxy headers. If you terminate TLS at the
proxy, no application change is needed.

## Configuration notes

- CORS is open by default (`allow_origins=["*"]`) because the tool is meant for
  local and internal use. If you expose it more widely, restrict origins in
  `main.py`.
- There is no authentication. The service only generates synthetic data and
  never returns anything sensitive, but if you place it on a shared network you
  may still want to gate it at the proxy.
- The service is stateless. You can run as many replicas as you like; there is
  nothing to persist or share between them.

## Health and monitoring

`GET /health` returns a small JSON payload and is suitable for liveness and
readiness probes:

```bash
curl http://localhost:8000/health
```

## Resource use

Memory and CPU scale with the size of the cohort you request. A cohort of 1000
patients with several years of history produces tens of thousands of resources;
prefer `format=ndjson` for large requests so the response streams instead of
being buffered in memory as one document.
