from copy import deepcopy

from fastapi import APIRouter

from models.schemas import SimulationRequest, AnalysisResponse, LabelData, AdditiveInfo
from services.compliance_checker import run_all_checks
from services.risk_scorer import calculate_risk_score, build_summary

router = APIRouter()


@router.post("/simulate", response_model=AnalysisResponse)
async def run_simulation(request: SimulationRequest):
    """
    Run a 'what-if' scenario simulation.
    Apply modifications to the label data, then re-run all compliance checks.

    Supported modifications:
      - remove_ingredients: list of ingredient names to remove
      - add_allergen_declaration: list of allergens to add to declared list
      - remove_additives: list of additive names to remove
      - add_claim: claim string to add
      - remove_claim: claim string to remove
      - set_fssai_license: new license number
    """
    label = deepcopy(request.label_data)
    mods = request.modifications

    # Apply modifications
    if "remove_ingredients" in mods:
        remove_set = {r.lower() for r in mods["remove_ingredients"]}
        label.ingredients = [i for i in label.ingredients if i.lower() not in remove_set]

    if "add_allergen_declaration" in mods:
        for allergen in mods["add_allergen_declaration"]:
            if allergen not in label.declared_allergens:
                label.declared_allergens.append(allergen)

    if "remove_allergen_declaration" in mods:
        remove_set = {r.lower() for r in mods["remove_allergen_declaration"]}
        label.declared_allergens = [a for a in label.declared_allergens if a.lower() not in remove_set]

    if "remove_additives" in mods:
        remove_set = {r.lower() for r in mods["remove_additives"]}
        label.additives = [a for a in label.additives if a.name.lower() not in remove_set]

    if "add_claim" in mods:
        claim = mods["add_claim"]
        if claim not in label.nutritional_claims:
            label.nutritional_claims.append(claim)

    if "remove_claim" in mods:
        claim_lower = mods["remove_claim"].lower()
        label.nutritional_claims = [c for c in label.nutritional_claims if c.lower() != claim_lower]

    if "set_fssai_license" in mods:
        label.fssai_license = mods["set_fssai_license"]

    # Re-run compliance on modified data
    findings = run_all_checks(label)
    risk_score = calculate_risk_score(findings)
    summary = build_summary(findings, risk_score)

    return AnalysisResponse(
        label_data=label,
        findings=findings,
        risk_score=risk_score,
        summary=summary,
    )
