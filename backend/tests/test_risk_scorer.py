from models.schemas import ComplianceFinding
from services.risk_scorer import calculate_risk_score, build_summary


def _finding(module, severity):
    return ComplianceFinding(
        module=module,
        severity=severity,
        title=f"Test {severity} in {module}",
        description="Test description",
    )


def test_all_info_high_score():
    """All INFO findings should give a perfect or near-perfect score."""
    findings = [
        _finding("additives", "INFO"),
        _finding("allergens", "INFO"),
        _finding("claims", "INFO"),
        _finding("license", "INFO"),
        _finding("labelling", "INFO"),
    ]
    score = calculate_risk_score(findings)
    assert score.overall_score == 100
    assert score.grade == "A"


def test_many_criticals_low_score():
    """Many CRITICAL findings should produce a very low score."""
    findings = []
    for module in ["additives", "allergens", "claims", "license", "labelling"]:
        for _ in range(5):
            findings.append(_finding(module, "CRITICAL"))
    score = calculate_risk_score(findings)
    assert score.overall_score == 0
    assert score.grade == "F"


def test_mixed_findings():
    """Mix of severities should produce a mid-range score."""
    findings = [
        _finding("additives", "CRITICAL"),
        _finding("allergens", "WARNING"),
        _finding("allergens", "WARNING"),
        _finding("claims", "INFO"),
        _finding("license", "INFO"),
        _finding("labelling", "WARNING"),
    ]
    score = calculate_risk_score(findings)
    assert 30 <= score.overall_score <= 90


def test_allergen_weight_highest():
    """A CRITICAL in allergens should hurt more than a CRITICAL in license."""
    allergen_findings = [_finding("allergens", "CRITICAL")]
    license_findings = [_finding("license", "CRITICAL")]

    allergen_score = calculate_risk_score(allergen_findings)
    license_score = calculate_risk_score(license_findings)

    # Allergen weight=30, license weight=10
    # Allergen CRITICAL: module=75, weighted impact = 75*30/100 vs 100*30/100
    # License CRITICAL: module=75, weighted impact = 75*10/100 vs 100*10/100
    # So allergen CRITICAL causes a bigger drop in overall score
    assert allergen_score.overall_score < license_score.overall_score


def test_grade_a_boundary():
    """Score >= 90 should be grade A."""
    # Single WARNING in labelling (weight=15): module=90, weighted=90*15/100=13.5
    # All others 100: 100*85/100=85. Total=98.5 → 99
    findings = [_finding("labelling", "WARNING")]
    score = calculate_risk_score(findings)
    assert score.grade == "A"
    assert score.overall_score >= 90


def test_summary_format():
    """Summary should mention grade, score, and finding counts."""
    findings = [
        _finding("additives", "CRITICAL"),
        _finding("allergens", "WARNING"),
    ]
    score = calculate_risk_score(findings)
    summary = build_summary(findings, score)
    assert str(score.overall_score) in summary
    assert score.grade in summary
    assert "1 critical" in summary.lower()
