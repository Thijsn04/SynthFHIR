"""R5 Device resource mapper. Spec: https://hl7.org/fhir/R5/device.html

R5 differences: Device.type is a list of CodeableConcept and the direct
Device.patient element was removed (patient linkage moved out of Device).
"""
from mappers._helpers import build_meta

_PROFILE = "http://hl7.org/fhir/StructureDefinition/Device"
_SNOMED = "http://snomed.info/sct"


def map_device(dev: dict, us_core: bool = False) -> dict:
    return {
        "resourceType": "Device",
        "id": dev["id"],
        "meta": build_meta(_PROFILE),
        "status": dev["status"],
        "udiCarrier": [
            {
                "deviceIdentifier": dev["udi_di"],
                "carrierHRF": dev["udi_carrier"],
            }
        ],
        "type": [
            {
                "coding": [{"system": _SNOMED, "code": dev["type_code"], "display": dev["type_display"]}],
                "text": dev["type_display"],
            }
        ],
    }
