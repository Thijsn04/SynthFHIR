from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(
    title="SynthFHIR",
    description=(
        "A 100% free, open-source, locally hosted synthetic FHIR patient data generator. "
        "Generates fully relational clinical datasets — patients, practitioners, organizations, "
        "conditions, allergies, encounters, and observations — all perfectly linked by ID. "
        "No external APIs. No paid services. Pure Faker, running locally."
    ),
    version="1.0.0",
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
)

app.include_router(router, prefix="/api")


@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "SynthFHIR is running.",
        "docs": "/docs",
        "endpoints": {
            "cohort":       "/api/generate/cohort",
            "patient":      "/api/generate/patient",
            "conditions":   "/api/conditions",
            "observations": "/api/observations",
        },
    }
