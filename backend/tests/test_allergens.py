from models.schemas import LabelData
from services.compliance_checker import check_allergens


def _label_with(ingredients, declared=None):
    return LabelData(ingredients=ingredients, declared_allergens=declared or [])


def test_undeclared_allergen_critical():
    label = _label_with(["Milk Powder", "Sugar"], declared=[])
    findings = check_allergens(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    assert len(critical) >= 1
    assert any("milk" in f.title.lower() for f in critical)


def test_declared_allergen_info():
    label = _label_with(["Milk Powder", "Sugar"], declared=["Milk"])
    findings = check_allergens(label)
    critical = [f for f in findings if f.severity == "CRITICAL" and "milk" in f.title.lower()]
    assert len(critical) == 0


def test_cocoa_butter_not_flagged_as_milk():
    label = _label_with(["Cocoa Butter", "Sugar", "Vanilla"], declared=[])
    findings = check_allergens(label)
    milk_critical = [
        f for f in findings
        if f.severity == "CRITICAL" and "milk" in f.title.lower()
    ]
    assert len(milk_critical) == 0


def test_nutmeg_not_flagged_as_eggs():
    label = _label_with(["Nutmeg", "Salt", "Pepper"], declared=[])
    findings = check_allergens(label)
    egg_findings = [f for f in findings if "egg" in f.title.lower() and f.severity == "CRITICAL"]
    assert len(egg_findings) == 0


def test_cream_of_tartar_not_flagged_as_milk():
    label = _label_with(["Cream of Tartar", "Baking Soda"], declared=[])
    findings = check_allergens(label)
    milk_critical = [
        f for f in findings
        if f.severity == "CRITICAL" and "milk" in f.title.lower()
    ]
    assert len(milk_critical) == 0


def test_multiple_undeclared_allergens():
    label = _label_with(["Wheat Flour", "Egg White", "Milk Powder"], declared=[])
    findings = check_allergens(label)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    # Should flag Wheat/Gluten, Eggs, and Milk
    assert len(critical) >= 3


def test_word_boundary_egg_in_nutmeg():
    """'egg' should NOT match inside 'nutmeg'."""
    label = _label_with(["Nutmeg"], declared=[])
    findings = check_allergens(label)
    egg_critical = [f for f in findings if f.severity == "CRITICAL" and "egg" in f.title.lower()]
    assert len(egg_critical) == 0


def test_no_ingredients_no_findings():
    label = _label_with([], declared=[])
    findings = check_allergens(label)
    assert findings == []
