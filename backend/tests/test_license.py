from models.schemas import LabelData
from services.compliance_checker import check_license


def _label_with_license(lic):
    return LabelData(fssai_license=lic)


def test_valid_14_digit_license():
    label = _label_with_license("10123456789012")
    findings = check_license(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) == 0
    info = [f for f in findings if f.severity == "INFO"]
    assert len(info) >= 1


def test_missing_license_critical():
    label = _label_with_license(None)
    findings = check_license(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) >= 1


def test_too_short_critical():
    label = _label_with_license("12345")
    findings = check_license(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) >= 1


def test_non_numeric_critical():
    label = _label_with_license("ABCDEFGHIJKLMN")
    findings = check_license(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) >= 1


def test_spaces_and_dashes_stripped():
    label = _label_with_license("1012-3456-7890-12")
    findings = check_license(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) == 0
