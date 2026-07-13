from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import config
from api.routes import router

app = FastAPI(
    title="SynthFHIR",
    description=(
        "A free, open-source, locally hosted synthetic FHIR patient data generator. "
        "Generates fully relational clinical datasets: patients, practitioners, "
        "organizations, conditions, allergies, encounters, and observations, all "
        "linked by ID. No external APIs. No paid services. Runs locally."
    ),
    version="0.4.0",
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def require_api_key(
    x_api_key: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> None:
    """Enforce the optional API key when SYNTHFHIR_API_KEY is configured."""
    if not config.API_KEY:
        return
    provided = x_api_key
    if not provided and authorization and authorization.lower().startswith("bearer "):
        provided = authorization.split(" ", 1)[1]
    if provided != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


app.include_router(router, prefix="/api", dependencies=[Depends(require_api_key)])


@app.get("/health", tags=["System"], summary="Liveness probe")
def health() -> dict:
    """Lightweight health check for uptime monitoring and the web console."""
    return {"status": "ok", "service": "synthfhir", "version": app.version}


@app.get("/api", include_in_schema=False)
def api_index() -> dict:
    """Machine-readable index of the primary API endpoints."""
    return {
        "service": "SynthFHIR",
        "version": app.version,
        "docs": "/docs",
        "endpoints": {
            "cohort": "/api/generate/cohort",
            "patient": "/api/generate/patient",
            "practitioner": "/api/generate/practitioner",
            "organization": "/api/generate/organization",
            "conditions": "/api/conditions",
            "observations": "/api/observations",
            "metadata": "/api/metadata",
        },
    }


# Serve the static web console at the site root. Mounted last so explicit
# routes (/api, /health, /docs) always take precedence over the catch-all.
_WEB_DIR = Path(__file__).parent / "web"
if _WEB_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(_WEB_DIR), html=True), name="web")
