"""QuestionnaireResponse generator.

The survey Observations (PHQ-9, GAD-7) also make sense as QuestionnaireResponse
resources, which is how many systems capture screening instruments. One
QuestionnaireResponse is produced per survey Observation, carrying the total
score as the answer.

Output keys: id, patient_id, encounter_id, authored, questionnaire, title,
link_id, question_text, score.
"""
from generators._rng import new_uuid

# Map the survey observation LOINC to a public questionnaire canonical and title.
_QUESTIONNAIRES = {
    "44249-1": ("http://loinc.org/q/44249-1", "PHQ-9 quick depression assessment panel"),
    "69737-5": ("http://loinc.org/q/69737-5", "GAD-7 generalized anxiety disorder panel"),
}
_DEFAULT_QUESTIONNAIRE = ("http://loinc.org/q/survey", "Screening questionnaire")


def generate_questionnaire_responses(observations: list[dict]) -> list[dict]:
    """One QuestionnaireResponse per survey Observation."""
    results: list[dict] = []
    for obs in observations:
        if obs.get("category_code") != "survey":
            continue
        canonical, title = _QUESTIONNAIRES.get(obs.get("loinc_code", ""), _DEFAULT_QUESTIONNAIRE)
        results.append(
            {
                "id": new_uuid(),
                "patient_id": obs["patient_id"],
                "encounter_id": obs.get("encounter_id", ""),
                "authored": obs.get("effective_datetime", ""),
                "questionnaire": canonical,
                "title": title,
                "link_id": obs.get("loinc_code", "score"),
                "question_text": f"{obs.get('display', title)} total score",
                "score": int(obs.get("value", 0)),
            }
        )
    return results
