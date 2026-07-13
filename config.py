"""Runtime configuration from environment variables.

SynthFHIR needs almost no configuration: it is stateless and generates only
synthetic data. These few settings cover the cases that matter when the service
is exposed beyond a local machine.
"""
import os


def _cors_origins() -> list[str]:
    raw = os.getenv("SYNTHFHIR_CORS_ORIGINS", "*").strip()
    if raw == "*" or not raw:
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


# Allowed CORS origins. Default is open, appropriate for local and internal use.
CORS_ORIGINS: list[str] = _cors_origins()

# Optional API key. When set, every /api request must present it via the
# X-API-Key header or an Authorization: Bearer header. Unset means no auth.
API_KEY: str | None = os.getenv("SYNTHFHIR_API_KEY") or None
