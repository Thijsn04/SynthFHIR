from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="SynthFHIR",
    description=(
        "A 100% free, open-source, locally hosted synthetic FHIR patient data generator. "
        "Produces valid FHIR R4 and R5 Patient resources using only local Faker data — "
        "no external APIs or paid services required."
    ),
    version="1.0.0",
    license_info={"name": "MIT"},
)

app.include_router(router, prefix="/api")


@app.get("/", include_in_schema=False)
def root():
    return {"message": "SynthFHIR is running. Visit /docs for the Swagger UI."}
