from models.schemas import LabelData, NutritionalInfo
from services.compliance_checker import check_labelling


def test_all_fields_present(label_data):
    """Fully populated label should have no WARNING findings."""
    findings = check_labelling(label_data)
    warnings = [f for f in findings if f.severity == "WARNING"]
    assert len(warnings) == 0


def test_all_fields_missing(empty_label):
    """Empty label should produce WARNING for each mandatory field."""
    findings = check_labelling(empty_label)
    warnings = [f for f in findings if f.severity == "WARNING"]
    # Should warn about: product_name, ingredients, net_weight, fssai_license,
    # manufacturing_date, expiry/best_before, nutritional_info, allergens, veg_status
    assert len(warnings) >= 7


def test_best_before_substitutes_expiry():
    """If expiry_date is missing but best_before is present, should NOT be critical."""
    label = LabelData(
        product_name="Test",
        ingredients=["Water"],
        net_weight="500ml",
        fssai_license="10123456789012",
        manufacturing_date="Jan 2025",
        expiry_date=None,
        best_before="Dec 2025",
        vegetarian_status="veg",
        nutritional_info=NutritionalInfo(energy_kcal=0),
        declared_allergens=["None"],
    )
    findings = check_labelling(label)
    # best_before present should count as acceptable
    expiry_warnings = [
        f for f in findings
        if f.severity == "WARNING" and ("expiry" in f.title.lower() or "best before" in f.title.lower())
    ]
    assert len(expiry_warnings) == 0


def test_partial_fields():
    """Only some fields present — should get a mix of INFO and WARNING."""
    label = LabelData(
        product_name="Test Product",
        ingredients=["Sugar", "Water"],
    )
    findings = check_labelling(label)
    info = [f for f in findings if f.severity == "INFO"]
    warnings = [f for f in findings if f.severity == "WARNING"]
    assert len(info) >= 2  # product_name and ingredients present
    assert len(warnings) >= 5  # many fields missing
