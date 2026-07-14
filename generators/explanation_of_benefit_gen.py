"""ExplanationOfBenefit generator.

One ExplanationOfBenefit per Claim, representing the payer's adjudication. The
payer covers most of the charge and the patient owes the remainder.

Output keys: id, patient_id, claim_id, coverage_id, organization_id, created,
item_code, item_display, amount, paid, patient_responsibility.
"""
import random

from generators._rng import new_uuid


def generate_eobs_for_claims(claims: list[dict]) -> list[dict]:
    """One ExplanationOfBenefit per Claim."""
    results: list[dict] = []
    for claim in claims:
        amount = claim["amount"]
        covered_fraction = random.uniform(0.6, 0.9)
        paid = round(amount * covered_fraction, 2)
        results.append(
            {
                "id": new_uuid(),
                "patient_id": claim["patient_id"],
                "claim_id": claim["id"],
                "coverage_id": claim["coverage_id"],
                "organization_id": claim.get("organization_id", ""),
                "created": claim.get("created", ""),
                "item_code": claim["item_code"],
                "item_display": claim["item_display"],
                "amount": amount,
                "paid": paid,
                "patient_responsibility": round(amount - paid, 2),
            }
        )
    return results
