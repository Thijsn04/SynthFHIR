"""Wraps a flat list of R5 FHIR resources into a Bundle resource."""
import uuid

from mappers._helpers import utcnow


def build_bundle(resources: list[dict], bundle_type: str = "collection") -> dict:
    entries = [
        {
            "fullUrl": f"urn:uuid:{r['id']}",
            "resource": r,
        }
        for r in resources
    ]
    return {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "meta": {"lastUpdated": utcnow()},
        "type": bundle_type,
        "timestamp": utcnow(),
        "total": len(entries),
        "entry": entries,
    }
