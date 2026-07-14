"""R4 Device resource mapper. Spec: https://hl7.org/fhir/R4/device.html"""
from mappers._helpers import build_meta, ref

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Device"
_US_CORE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-implantable-device"
_SNOMED = "http://snomed.info/sct"


def map_device(dev: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Device",
        "id": dev["id"],
        "meta": build_meta(_US_CORE if us_core else _PROFILE),
        "status": dev["status"],
        "udiCarrier": [
            {
                "deviceIdentifier": dev["udi_di"],
                "issuer": "https://www.gs1.org/",
                "carrierHRF": dev["udi_carrier"],
            }
        ],
        "type": {
            "coding": [{"system": _SNOMED, "code": dev["type_code"], "display": dev["type_display"]}],
            "text": dev["type_display"],
        },
        "patient": ref("Patient", dev["patient_id"]),
    }
