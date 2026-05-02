"""Wraps a flat list of R4 FHIR resources into a Bundle resource."""
from generators._rng import new_uuid
from mappers._helpers import utcnow


def build_bundle(resources: list[dict], bundle_type: str = "collection") -> dict:
    """Builds a FHIR Bundle of the given type around a list of resources.

    For 'transaction' bundles each entry includes a request element so the
    bundle can be POSTed directly to a FHIR server for atomic ingestion.
    Each entry gets a urn:uuid fullUrl matching the resource's id, which
    allows inter-resource references to resolve within the bundle.
    """
    is_transaction = bundle_type == "transaction"
    entries = []
    for r in resources:
        entry: dict = {
            "fullUrl": f"urn:uuid:{r['id']}",
            "resource": r,
        }
        if is_transaction:
            entry["request"] = {
                "method": "POST",
                "url": r["resourceType"],
            }
        entries.append(entry)

    return {
        "resourceType": "Bundle",
        "id": new_uuid(),
        "meta": {"lastUpdated": utcnow()},
        "type": bundle_type,
        "timestamp": utcnow(),
        "total": len(entries),
        "entry": entries,
    }
