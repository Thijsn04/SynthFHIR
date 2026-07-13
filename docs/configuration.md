# Configuration

SynthFHIR needs almost no configuration. It is stateless, stores nothing, and by
default makes no outbound connections. The few available settings are read from
environment variables at startup and matter mainly when you expose the service
beyond your own machine.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `SYNTHFHIR_CORS_ORIGINS` | `*` | Comma-separated list of allowed CORS origins. `*` allows any origin. |
| `SYNTHFHIR_API_KEY` | unset | When set, every `/api` request must present this key. Unset means no authentication. |

## CORS

By default any origin may call the API, which is convenient for local use and for
the bundled web console. To restrict it, set a comma-separated list:

```bash
export SYNTHFHIR_CORS_ORIGINS="https://example.org,https://app.example.org"
uvicorn main:app
```

## API key

The API is open by default. To require a key, set `SYNTHFHIR_API_KEY`:

```bash
export SYNTHFHIR_API_KEY="choose-a-long-random-value"
uvicorn main:app
```

Clients then authenticate with either header:

```bash
curl -H "X-API-Key: choose-a-long-random-value" \
     "http://localhost:8000/api/generate/cohort?count=5"

curl -H "Authorization: Bearer choose-a-long-random-value" \
     "http://localhost:8000/api/generate/cohort?count=5"
```

`GET /health` stays open so liveness probes keep working. If you enable the key
and still want to use the web console, open Advanced in the console and note that
the console does not send a key; for keyed deployments, call the API directly or
place the console behind the same auth at your proxy.

## Docker

Pass environment variables through Compose:

```yaml
services:
  synthfhir:
    image: synthfhir:latest
    environment:
      SYNTHFHIR_API_KEY: choose-a-long-random-value
      SYNTHFHIR_CORS_ORIGINS: "https://app.example.org"
    ports:
      - "8000:8000"
```

or with `docker run`:

```bash
docker run --rm -p 8000:8000 \
  -e SYNTHFHIR_API_KEY=choose-a-long-random-value \
  synthfhir
```

## Server host and port

Host and port are set on the server command, not through environment variables:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
# or
synthfhir serve --host 0.0.0.0 --port 8080
```

## Request limits

The cohort size is capped at 1000 patients per request and other parameters have
documented ranges (see the [REST API reference](rest-api.md)). For very large
datasets, use `format=ndjson` so the response streams.
