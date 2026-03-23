import copy
from models.schemas import LabelData, NutritionalInfo, AdditiveInfo
from services.compliance_checker import run_all_checks
from routers.simulate import _apply_modifications


def _test_label():
    """Label with known allergen issues for simulation testing."""
    return LabelData(
        product_name="Test Product",
        brand="TestBrand",
        ingredients=["Wheat Flour", "Sugar", "Milk Powder", "Salt"],
        additives=[AdditiveInfo(name="Tartrazine", e_code="E102")],
        declared_allergens=[],  # deliberately missing declarations
        nutritional_claims=["Sugar Free"],
        fssai_license="10123456789012",
        manufacturing_date="Jan 2025",
        expiry_date="Jan 2026",
        vegetarian_status="veg",
        nutritional_info=NutritionalInfo(
            energy_kcal=200, protein_g=5, sugar_g=12.0,
            total_fat_g=3.0, carbohydrates_g=30.0,
        ),
    )


def test_remove_ingredient_changes_findings():
    label = _test_label()
    modified = _apply_modifications(
        copy.deepcopy(label),
        {"remove_ingredients": ["Wheat Flour"]},
    )
    assert "Wheat Flour" not in modified.ingredients
    findings = run_all_checks(modified)
    # Should no longer flag wheat/gluten allergen
    wheat_critical = [
        f for f in findings
        if f.severity == "CRITICAL" and f.module == "allergens"
        and ("wheat" in f.title.lower() or "gluten" in f.title.lower())
    ]
    assert len(wheat_critical) == 0


def test_add_allergen_declaration_fixes_critical():
    label = _test_label()
    # Original should have undeclared Milk allergen
    original_findings = run_all_checks(label)
    milk_critical = [
        f for f in original_findings
        if f.severity == "CRITICAL" and "milk" in f.title.lower()
    ]
    assert len(milk_critical) >= 1

    # Adding Milk declaration should fix it
    modified = _apply_modifications(
        copy.deepcopy(label),
        {"add_allergen_declaration": ["Milk"]},
    )
    new_findings = run_all_checks(modified)
    milk_critical_after = [
        f for f in new_findings
        if f.severity == "CRITICAL" and "milk" in f.title.lower()
    ]
    assert len(milk_critical_after) == 0


def test_invalid_license_modification():
    label = _test_label()
    modified = _apply_modifications(
        copy.deepcopy(label),
        {"set_fssai_license": "bad"},
    )
    findings = run_all_checks(modified)
    license_critical = [
        f for f in findings
        if f.severity == "CRITICAL" and f.module == "license"
    ]
    assert len(license_critical) >= 1


def test_remove_claim_changes_findings():
    label = _test_label()
    # "Sugar Free" with sugar_g=12 should be CRITICAL (misleading)
    original_findings = run_all_checks(label)
    claim_critical = [
        f for f in original_findings
        if f.severity == "CRITICAL" and f.module == "claims"
    ]
    assert len(claim_critical) >= 1

    # Remove the misleading claim
    modified = _apply_modifications(
        copy.deepcopy(label),
        {"remove_claim": "Sugar Free"},
    )
    new_findings = run_all_checks(modified)
    claim_critical_after = [
        f for f in new_findings
        if f.severity == "CRITICAL" and f.module == "claims"
    ]
    assert len(claim_critical_after) == 0


def test_original_data_not_mutated():
    label = _test_label()
    original_ingredients = list(label.ingredients)
    original_allergens = list(label.declared_allergens)

    label_copy = copy.deepcopy(label)
    _apply_modifications(label_copy, {
        "remove_ingredients": ["Wheat Flour"],
        "add_allergen_declaration": ["Milk"],
    })

    # Original should be unchanged
    assert label.ingredients == original_ingredients
    assert label.declared_allergens == original_allergens
