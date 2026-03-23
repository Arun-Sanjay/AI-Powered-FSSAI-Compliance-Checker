from models.schemas import LabelData, NutritionalInfo
from services.compliance_checker import check_claims


def _label_with_claims(claims, **nutrition_kwargs):
    ni = NutritionalInfo(**nutrition_kwargs) if nutrition_kwargs else None
    return LabelData(nutritional_claims=claims, nutritional_info=ni)


def test_valid_sugar_free():
    label = _label_with_claims(["Sugar Free"], sugar_g=0.3, energy_kcal=100)
    findings = check_claims(label)
    info = [f for f in findings if f.severity == "INFO"]
    assert len(info) >= 1
    assert any("verified" in f.title.lower() for f in info)


def test_invalid_sugar_free():
    label = _label_with_claims(["Sugar Free"], sugar_g=5.0, energy_kcal=100)
    findings = check_claims(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) >= 1
    assert any("misleading" in f.title.lower() for f in critical)


def test_valid_high_protein():
    """protein_g=10, energy=150 → 10*4/150*100 = 26.7% ≥ 20% → valid."""
    label = _label_with_claims(["High Protein"], protein_g=10.0, energy_kcal=150.0)
    findings = check_claims(label)
    info = [f for f in findings if f.severity == "INFO"]
    assert len(info) >= 1
    assert any("verified" in f.title.lower() for f in info)


def test_invalid_high_protein():
    """protein_g=5, energy=400 → 5*4/400*100 = 5% < 20% → misleading."""
    label = _label_with_claims(["High Protein"], protein_g=5.0, energy_kcal=400.0)
    findings = check_claims(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) >= 1
    assert any("misleading" in f.title.lower() for f in critical)


def test_no_added_sugar_always_warning():
    label = _label_with_claims(["No Added Sugar"], sugar_g=15.0, energy_kcal=200)
    findings = check_claims(label)
    warnings = [f for f in findings if f.severity == "WARNING"]
    assert len(warnings) >= 1
    assert any("cannot" in f.title.lower() or "cannot" in f.description.lower() for f in warnings)


def test_missing_nutritional_info_warning():
    label = LabelData(nutritional_claims=["Low Fat"])
    findings = check_claims(label)
    warnings = [f for f in findings if f.severity == "WARNING"]
    assert len(warnings) >= 1


def test_unknown_claim_warning():
    label = _label_with_claims(["Super Organic Plus"], energy_kcal=100)
    findings = check_claims(label)
    warnings = [f for f in findings if f.severity == "WARNING"]
    assert len(warnings) >= 1
    assert any("unverifiable" in f.title.lower() for f in warnings)


def test_no_claims_no_findings():
    label = _label_with_claims([])
    findings = check_claims(label)
    assert findings == []
