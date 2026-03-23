from models.schemas import LabelData, AdditiveInfo
from services.compliance_checker import check_additives


def _label_with_additives(additives):
    return LabelData(additives=additives)


def test_banned_additive_critical():
    label = _label_with_additives([AdditiveInfo(name="Carbon Black", e_code="E153")])
    findings = check_additives(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) >= 1
    assert any("banned" in f.title.lower() or "banned" in f.description.lower() for f in critical)


def test_approved_additive_info():
    label = _label_with_additives([AdditiveInfo(name="Curcumin", e_code="E100")])
    findings = check_additives(label)
    assert all(f.severity != "CRITICAL" for f in findings)


def test_restricted_additive_flagged():
    label = _label_with_additives([AdditiveInfo(name="Tartrazine", e_code="E102")])
    findings = check_additives(label)
    has_warning_or_critical = any(f.severity in ("WARNING", "CRITICAL") for f in findings)
    assert has_warning_or_critical


def test_unknown_additive_warning():
    label = _label_with_additives([AdditiveInfo(name="Mystery Chemical X")])
    findings = check_additives(label)
    warnings = [f for f in findings if f.severity == "WARNING"]
    assert len(warnings) >= 1


def test_no_additives_empty():
    label = _label_with_additives([])
    findings = check_additives(label)
    assert findings == []


def test_ecode_lookup_without_name():
    label = _label_with_additives([AdditiveInfo(name="", e_code="E171")])
    findings = check_additives(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) >= 1
