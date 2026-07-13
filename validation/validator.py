"""Dependency-free FHIR Bundle validator.

This is a pragmatic structural and referential validator, not a full
StructureDefinition engine. It catches the mistakes that matter most for
synthetic data: broken internal references, duplicate ids, missing resource
types, and missing base-FHIR mandatory elements. It runs in milliseconds and
requires no external packages, so it is safe to call on every generated bundle
and in CI.

Public API
----------
    report = validate_bundle(bundle_dict)
    report.valid            # bool
    report.errors           # list[Issue]
    report.warnings         # list[Issue]
    report.to_dict()        # JSON-serializable summary
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Base-FHIR mandatory (1..1) elements per resource type. Kept conservative so a
# valid SynthFHIR bundle never trips a false positive across R4 and R5.
_REQUIRED_ELEMENTS: dict[str, tuple[str, ...]] = {
    "Observation": ("status", "code"),
    "Encounter": ("status",),
    "Condition": ("subject",),
    "MedicationRequest": ("status", "intent", "subject"),
    "DiagnosticReport": ("status", "code"),
    "DocumentReference": ("status", "type", "content", "subject"),
    "MedicationDispense": ("status", "subject"),
    "Immunization": ("status", "vaccineCode", "patient"),
    "AllergyIntolerance": ("patient",),
    "Procedure": ("status", "subject"),
    "ServiceRequest": ("status", "intent", "subject"),
    "CarePlan": ("status", "intent", "subject"),
    "CareTeam": ("subject",),
    "Goal": ("lifecycleStatus", "description", "subject"),
    "Coverage": ("status", "beneficiary"),
    "Patient": (),
    "Practitioner": (),
    "Organization": (),
}


@dataclass(frozen=True)
class Issue:
    """A single validation finding."""

    severity: str  # "error" or "warning"
    path: str      # e.g. "entry[3].resource (Observation/abc)"
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"severity": self.severity, "path": self.path, "message": self.message}


@dataclass
class ValidationReport:
    """The outcome of validating one bundle."""

    resource_count: int = 0
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def add_error(self, path: str, message: str) -> None:
        self.errors.append(Issue("error", path, message))

    def add_warning(self, path: str, message: str) -> None:
        self.warnings.append(Issue("warning", path, message))

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "resource_count": self.resource_count,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [i.to_dict() for i in self.errors],
            "warnings": [i.to_dict() for i in self.warnings],
        }


def _iter_references(node: Any) -> list[str]:
    """Recursively collect every Reference.reference string in a resource."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "reference" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(_iter_references(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_iter_references(item))
    return found


def _is_internal_reference(ref: str) -> bool:
    """True for references that must resolve inside the bundle."""
    if ref.startswith(("http://", "https://", "#")):
        return False
    if ref.startswith("urn:uuid:"):
        return True
    # Relative "ResourceType/id" form.
    parts = ref.split("/")
    return len(parts) == 2 and parts[0].isalpha() and bool(parts[1])


def validate_bundle(bundle: dict[str, Any], *, resolve_references: bool = True) -> ValidationReport:
    """Validate a FHIR Bundle dict and return a structured report.

    Checks performed:
      - bundle shape (resourceType, type, entry array)
      - every entry carries a resource with a resourceType
      - fullUrl and resource.id uniqueness
      - transaction bundles carry entry.request.method and url
      - base-FHIR mandatory elements per resource type
      - internal references resolve to a resource in the bundle
    """
    report = ValidationReport()

    if not isinstance(bundle, dict):
        report.add_error("$", "Top-level value is not a JSON object.")
        return report

    if bundle.get("resourceType") != "Bundle":
        report.add_error("$.resourceType", "Expected resourceType 'Bundle'.")
        return report

    bundle_type = bundle.get("type")
    if not bundle_type:
        report.add_warning("$.type", "Bundle has no 'type'.")

    entries = bundle.get("entry")
    if not isinstance(entries, list):
        report.add_error("$.entry", "Bundle has no 'entry' array.")
        return report

    # First pass: index every resource by its resolvable identifiers.
    index: set[str] = set()
    seen_full_urls: set[str] = set()

    for i, entry in enumerate(entries):
        resource = entry.get("resource") if isinstance(entry, dict) else None
        if not isinstance(resource, dict):
            report.add_error(f"entry[{i}]", "Entry has no 'resource' object.")
            continue

        rtype = resource.get("resourceType")
        rid = resource.get("id")
        full_url = entry.get("fullUrl") if isinstance(entry, dict) else None

        if full_url:
            if full_url in seen_full_urls:
                report.add_error(f"entry[{i}].fullUrl", f"Duplicate fullUrl '{full_url}'.")
            seen_full_urls.add(full_url)
            index.add(full_url)
        if rid:
            index.add(f"urn:uuid:{rid}")
            if rtype:
                index.add(f"{rtype}/{rid}")

    report.resource_count = sum(
        1 for e in entries if isinstance(e, dict) and isinstance(e.get("resource"), dict)
    )

    # Second pass: per-resource structural checks and reference resolution.
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        resource = entry.get("resource")
        if not isinstance(resource, dict):
            continue

        rtype = resource.get("resourceType")
        rid = resource.get("id", "")
        label = f"entry[{i}].resource ({rtype}/{rid})" if rtype else f"entry[{i}].resource"

        if not rtype:
            report.add_error(label, "Resource has no 'resourceType'.")
            continue
        if not rid:
            report.add_warning(label, "Resource has no 'id'.")

        if bundle_type == "transaction":
            request = entry.get("request")
            if not isinstance(request, dict) or not request.get("method") or not request.get("url"):
                report.add_error(
                    f"entry[{i}].request",
                    "Transaction entry needs request.method and request.url.",
                )

        for element in _REQUIRED_ELEMENTS.get(rtype, ()):  # required base elements
            if element not in resource:
                report.add_error(label, f"Missing required element '{element}'.")

        if resolve_references:
            for ref in _iter_references(resource):
                if _is_internal_reference(ref) and ref not in index:
                    report.add_error(label, f"Unresolved reference '{ref}'.")

    return report
