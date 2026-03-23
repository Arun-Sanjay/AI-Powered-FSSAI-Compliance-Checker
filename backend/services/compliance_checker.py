"""
FSSAI Compliance Engine — 5 rule-based modules that check extracted label data
against FSSAI regulations stored in SQLite.

This is entirely custom logic, not AI. Each module returns a list of ComplianceFinding objects.
"""

import os
import re
import sqlite3

from models.schemas import LabelData, ComplianceFinding


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "fssai_compliance.db")


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODULE 1: Additive Compliance Checker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_additives(label: LabelData) -> list[ComplianceFinding]:
    """Check each additive against FSSAI Schedule I database."""
    findings = []
    if not label.additives:
        return findings

    conn = _get_db()
    food_category = (label.food_category or "").lower()

    for additive in label.additives:
        # Try matching by e_code first, then by name
        row = None
        if additive.e_code:
            row = conn.execute(
                "SELECT * FROM additives WHERE LOWER(e_code) = LOWER(?)", (additive.e_code,)
            ).fetchone()

        if not row:
            row = conn.execute(
                "SELECT * FROM additives WHERE LOWER(name) LIKE ?", (f"%{additive.name.lower()}%",)
            ).fetchone()

        if not row:
            # Unknown additive — not in our database
            findings.append(ComplianceFinding(
                module="additives",
                severity="WARNING",
                title=f"Unknown Additive: {additive.name}",
                description=f"'{additive.name}' (E-code: {additive.e_code or 'N/A'}) was not found in the FSSAI additive database. Cannot verify compliance.",
                regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I",
                recommendation="Verify this additive is approved by FSSAI for use in food products.",
            ))
            continue

        status = row["status"]
        name = row["name"]
        e_code = row["e_code"]
        permitted = (row["permitted_categories"] or "").lower()

        if status == "banned":
            findings.append(ComplianceFinding(
                module="additives",
                severity="CRITICAL",
                title=f"Banned Additive: {name} ({e_code})",
                description=f"'{name}' is BANNED by FSSAI for use in food products. {row['notes'] or ''}",
                regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I",
                recommendation=f"Remove {name} from the product formulation immediately.",
            ))
        elif status == "restricted":
            # Check if it's permitted in this food category
            category_match = (
                not food_category
                or "all food categories" in permitted
                or any(cat.strip() in food_category for cat in permitted.split(","))
                or any(food_category in cat.strip() for cat in permitted.split(","))
            )
            if not category_match and food_category:
                findings.append(ComplianceFinding(
                    module="additives",
                    severity="CRITICAL",
                    title=f"Restricted Additive in Wrong Category: {name} ({e_code})",
                    description=f"'{name}' is restricted and only permitted in: {row['permitted_categories']}. This product's category '{label.food_category}' may not be covered.",
                    regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I",
                    recommendation=f"Verify that {name} is permitted in the '{label.food_category}' category, or remove it.",
                ))
            else:
                findings.append(ComplianceFinding(
                    module="additives",
                    severity="WARNING",
                    title=f"Restricted Additive: {name} ({e_code})",
                    description=f"'{name}' is a restricted additive. {row['notes'] or ''} Max limit: {row['max_limit_ppm'] or 'N/A'} ppm. Permitted in: {row['permitted_categories'] or 'N/A'}.",
                    regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I",
                    recommendation=f"Ensure {name} usage is within FSSAI permitted limits for this food category.",
                ))
        # approved additives → INFO only if noteworthy
        elif status == "approved" and row["notes"] and ("allergen" in row["notes"].lower() or "declare" in row["notes"].lower()):
            findings.append(ComplianceFinding(
                module="additives",
                severity="INFO",
                title=f"Approved Additive with Note: {name} ({e_code})",
                description=f"'{name}' is approved. Note: {row['notes']}",
                regulation="FSS Food Products Standards & Food Additives Regulations, 2011 — Schedule I",
            ))

    conn.close()
    return findings


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODULE 2: Allergen Cross-Reference Checker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Ingredients that contain allergen keywords but don't belong to that allergen category
ALLERGEN_EXCEPTIONS = {
    "butter": {"Milk": ["cocoa butter", "shea butter"]},
    "cream": {"Milk": ["cream of tartar"]},
    "egg": {"Eggs": ["nutmeg", "eggplant"]},
}


def _is_allergen_exception(keyword: str, category: str, ingredient: str) -> bool:
    """Check if this keyword match is a known false positive for the given category."""
    ing_lower = ingredient.lower()
    exceptions = ALLERGEN_EXCEPTIONS.get(keyword, {}).get(category, [])
    return any(exc in ing_lower for exc in exceptions)


def check_allergens(label: LabelData) -> list[ComplianceFinding]:
    """
    Cross-reference ingredients against allergen keyword database.
    Flag any allergen detected in ingredients but missing from declared allergens.
    """
    findings = []
    if not label.ingredients:
        return findings

    conn = _get_db()
    allergen_rows = conn.execute("SELECT keyword, allergen_category FROM allergen_keywords").fetchall()
    conn.close()

    # Build a lookup: keyword → allergen category
    keyword_map = {row["keyword"].lower(): row["allergen_category"] for row in allergen_rows}

    # Normalize declared allergens for comparison
    declared = {a.lower().strip() for a in label.declared_allergens}

    # Scan each ingredient for allergen keywords using word-boundary matching
    detected_allergens = {}  # category → list of triggering ingredients

    for keyword, category in keyword_map.items():
        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
        for ing in label.ingredients:
            if pattern.search(ing) and not _is_allergen_exception(keyword, category, ing):
                if category not in detected_allergens:
                    detected_allergens[category] = []
                if ing not in detected_allergens[category]:
                    detected_allergens[category].append(ing)

    # Compare detected vs declared
    for category, triggering_ingredients in detected_allergens.items():
        # Check if this allergen category is covered in declarations
        category_declared = any(
            cat_word in declared
            for cat_word in [category.lower()] + category.lower().split()
        )
        # Also check if any of the specific keywords are declared
        if not category_declared:
            for d in declared:
                if d in category.lower() or category.lower() in d:
                    category_declared = True
                    break
                for ing in triggering_ingredients:
                    if d in ing.lower() or ing.lower() in d:
                        category_declared = True
                        break

        if not category_declared:
            findings.append(ComplianceFinding(
                module="allergens",
                severity="CRITICAL",
                title=f"Undeclared Allergen: {category}",
                description=f"Allergen category '{category}' detected in ingredients ({', '.join(triggering_ingredients)}) but NOT declared in the allergen section. FSSAI requires all allergens to be explicitly declared.",
                regulation="FSS Labelling & Display Regulations, 2020",
                recommendation=f"Add '{category}' to the allergen declaration ('Contains: ...' section).",
            ))
        else:
            findings.append(ComplianceFinding(
                module="allergens",
                severity="INFO",
                title=f"Allergen Declared: {category}",
                description=f"Allergen '{category}' correctly declared. Triggering ingredients: {', '.join(triggering_ingredients)}.",
                regulation="FSS Labelling & Display Regulations, 2020",
            ))

    # If no allergens detected but some declared — that's fine (extra caution)
    if not detected_allergens and label.declared_allergens:
        findings.append(ComplianceFinding(
            module="allergens",
            severity="INFO",
            title="Allergen Declaration Present",
            description=f"Declared allergens: {', '.join(label.declared_allergens)}. No hidden allergens detected in ingredients.",
            regulation="FSS Labelling & Display Regulations, 2020",
        ))

    return findings


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODULE 3: Claims Verification
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_claims(label: LabelData) -> list[ComplianceFinding]:
    """Validate nutritional claims against FSSAI thresholds."""
    findings = []
    if not label.nutritional_claims:
        return findings

    conn = _get_db()
    claims_rows = conn.execute("SELECT * FROM claims_rules").fetchall()
    conn.close()

    # Build lookup by normalized claim name
    rules = {row["claim"].lower(): dict(row) for row in claims_rows}

    nutritional = label.nutritional_info

    for claim in label.nutritional_claims:
        claim_lower = claim.lower().strip()

        # Find matching rule
        matched_rule = None
        for rule_claim, rule_data in rules.items():
            if rule_claim in claim_lower or claim_lower in rule_claim:
                matched_rule = rule_data
                break

        if not matched_rule:
            findings.append(ComplianceFinding(
                module="claims",
                severity="WARNING",
                title=f"Unverifiable Claim: '{claim}'",
                description=f"The claim '{claim}' could not be matched to any known FSSAI claim rule. Manual verification may be needed.",
                regulation="FSS Advertising & Claims Regulations, 2018",
                recommendation="Verify this claim meets FSSAI advertising regulations.",
            ))
            continue

        # Special case: "No Added Sugar" cannot be validated from nutritional info alone
        if "no added sugar" in claim_lower:
            findings.append(ComplianceFinding(
                module="claims",
                severity="WARNING",
                title=f"Cannot Fully Verify: '{claim}'",
                description=f"'{claim}' means no mono/disaccharides were added during manufacturing. This cannot be validated from the nutrition panel alone — natural sugars (from fruit, milk, etc.) may be present without violating this claim. Manual verification of the ingredient list is required.",
                regulation=matched_rule["regulation"],
                recommendation="Verify that no sugars, honey, syrups, or fruit juice concentrates were added as ingredients.",
            ))
            continue

        # If we don't have nutritional info, can't verify
        if not nutritional:
            findings.append(ComplianceFinding(
                module="claims",
                severity="WARNING",
                title=f"Cannot Verify Claim: '{claim}'",
                description=f"Nutritional information was not found on the label, so the claim '{claim}' cannot be verified against FSSAI thresholds.",
                regulation=matched_rule["regulation"],
                recommendation="Ensure nutritional information is present on the label.",
            ))
            continue

        # Special case: "High Protein" uses % of energy, not raw grams
        if "high protein" in claim_lower:
            if nutritional.protein_g is not None and nutritional.energy_kcal and nutritional.energy_kcal > 0:
                protein_energy_pct = (nutritional.protein_g * 4 / nutritional.energy_kcal) * 100
                threshold = matched_rule["threshold"]
                if protein_energy_pct >= threshold:
                    findings.append(ComplianceFinding(
                        module="claims",
                        severity="INFO",
                        title=f"Claim Verified: '{claim}'",
                        description=f"'{claim}' is valid — protein provides {protein_energy_pct:.1f}% of total energy (threshold: >= {threshold}%).",
                        regulation=matched_rule["regulation"],
                    ))
                else:
                    findings.append(ComplianceFinding(
                        module="claims",
                        severity="CRITICAL",
                        title=f"Misleading Claim: '{claim}'",
                        description=f"'{claim}' is INVALID — protein provides only {protein_energy_pct:.1f}% of total energy but must be >= {threshold}% to make this claim.",
                        regulation=matched_rule["regulation"],
                        recommendation=f"Remove the '{claim}' claim from packaging, or increase protein content.",
                    ))
            else:
                findings.append(ComplianceFinding(
                    module="claims",
                    severity="WARNING",
                    title=f"Cannot Verify Claim: '{claim}'",
                    description=f"Both protein (g) and energy (kcal) values are needed to verify '{claim}' (protein must provide >= 20% of total energy).",
                    regulation=matched_rule["regulation"],
                    recommendation="Ensure both protein and energy values are declared in the nutritional information.",
                ))
            continue

        # Get the actual value for the relevant field
        field = matched_rule["condition_field"]
        actual_value = getattr(nutritional, field, None)

        if actual_value is None:
            findings.append(ComplianceFinding(
                module="claims",
                severity="WARNING",
                title=f"Cannot Verify Claim: '{claim}'",
                description=f"The required nutritional field '{field}' was not found on the label to verify the '{claim}' claim.",
                regulation=matched_rule["regulation"],
                recommendation=f"Ensure '{field}' is declared in the nutritional information table.",
            ))
            continue

        # Evaluate the claim condition
        threshold = matched_rule["threshold"]
        operator = matched_rule["operator"]
        unit = matched_rule["unit"]

        if operator == "<=":
            claim_valid = actual_value <= threshold
        elif operator == ">=":
            claim_valid = actual_value >= threshold
        elif operator == "<":
            claim_valid = actual_value < threshold
        elif operator == ">":
            claim_valid = actual_value > threshold
        else:
            claim_valid = actual_value == threshold

        if claim_valid:
            findings.append(ComplianceFinding(
                module="claims",
                severity="INFO",
                title=f"Claim Verified: '{claim}'",
                description=f"'{claim}' is valid — {field} is {actual_value} {unit} (threshold: {operator} {threshold} {unit}).",
                regulation=matched_rule["regulation"],
            ))
        else:
            findings.append(ComplianceFinding(
                module="claims",
                severity="CRITICAL",
                title=f"Misleading Claim: '{claim}'",
                description=f"'{claim}' is INVALID — {field} is {actual_value} {unit} but must be {operator} {threshold} {unit} to make this claim.",
                regulation=matched_rule["regulation"],
                recommendation=f"Remove the '{claim}' claim from packaging, or reformulate the product to meet the threshold.",
            ))

    # Check for "Natural" claim contradictions
    natural_claims = [c for c in label.nutritional_claims if "natural" in c.lower()]
    if natural_claims and label.additives:
        artificial_additives = [
            a for a in label.additives
            if a.function and any(word in a.function.lower() for word in ["artificial", "synthetic"])
        ]
        # Also flag if there are colorants/flavour enhancers which are typically synthetic
        synthetic_indicators = [
            a for a in label.additives
            if a.e_code and a.e_code in ("E102", "E110", "E122", "E124", "E127", "E129", "E131", "E132", "E133", "E621")
        ]
        if artificial_additives or synthetic_indicators:
            flagged = artificial_additives + synthetic_indicators
            names = [f"{a.name} ({a.e_code})" if a.e_code else a.name for a in flagged]
            findings.append(ComplianceFinding(
                module="claims",
                severity="CRITICAL",
                title="Contradictory 'Natural' Claim",
                description=f"Product claims to be 'Natural' but contains synthetic/artificial additives: {', '.join(names)}.",
                regulation="FSS Advertising & Claims Regulations, 2018",
                recommendation="Remove the 'Natural' claim or reformulate without artificial additives.",
            ))

    return findings


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODULE 4: FSSAI License Validator
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LICENSE_TYPES = {
    "10": "Central License (large manufacturers, importers)",
    "20": "State License (medium manufacturers)",
    "21": "State License (storage/transport)",
    "22": "State License (retailers/restaurants)",
}


def check_license(label: LabelData) -> list[ComplianceFinding]:
    """Validate the FSSAI license number format and type."""
    findings = []

    if not label.fssai_license:
        findings.append(ComplianceFinding(
            module="license",
            severity="CRITICAL",
            title="Missing FSSAI License Number",
            description="No FSSAI license number was found on the label. All packaged food products sold in India MUST display a valid FSSAI license number.",
            regulation="FSS Licensing & Registration Regulations, 2011",
            recommendation="Ensure the FSSAI license number is clearly printed on the packaging.",
        ))
        return findings

    license_num = label.fssai_license.strip()

    # Remove any spaces or dashes
    clean_license = re.sub(r"[\s\-]", "", license_num)

    # Check if it's all digits
    if not clean_license.isdigit():
        findings.append(ComplianceFinding(
            module="license",
            severity="CRITICAL",
            title=f"Invalid FSSAI License Format: '{license_num}'",
            description="FSSAI license number must contain only digits. Non-numeric characters detected.",
            regulation="FSS Licensing & Registration Regulations, 2011",
            recommendation="Verify and correct the FSSAI license number.",
        ))
        return findings

    # Check length — must be exactly 14 digits
    if len(clean_license) != 14:
        findings.append(ComplianceFinding(
            module="license",
            severity="CRITICAL",
            title=f"Invalid FSSAI License Length: '{license_num}'",
            description=f"FSSAI license number must be exactly 14 digits. Found {len(clean_license)} digits.",
            regulation="FSS Licensing & Registration Regulations, 2011",
            recommendation="Verify the complete FSSAI license number.",
        ))
        return findings

    # Check prefix for license type
    prefix = clean_license[:2]
    if prefix in LICENSE_TYPES:
        findings.append(ComplianceFinding(
            module="license",
            severity="INFO",
            title=f"FSSAI License Valid Format",
            description=f"License number '{license_num}' has valid format. Type: {LICENSE_TYPES[prefix]}.",
            regulation="FSS Licensing & Registration Regulations, 2011",
        ))
    else:
        findings.append(ComplianceFinding(
            module="license",
            severity="WARNING",
            title=f"Unknown FSSAI License Type: prefix '{prefix}'",
            description=f"License number '{license_num}' has an unrecognized prefix '{prefix}'. Known prefixes: 10 (Central), 20/21/22 (State).",
            regulation="FSS Licensing & Registration Regulations, 2011",
            recommendation="Verify the license number with FSSAI's online portal.",
        ))

    return findings


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODULE 5: Labelling Completeness Checker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_labelling(label: LabelData) -> list[ComplianceFinding]:
    """Check whether all mandatory FSSAI label fields are present."""
    findings = []

    conn = _get_db()
    mandatory_rows = conn.execute("SELECT * FROM mandatory_fields").fetchall()
    conn.close()

    for row in mandatory_rows:
        field_name = row["field_name"]
        json_key = row["json_key"]
        regulation = row["fssai_reference"]

        # Get the value from label data
        value = getattr(label, json_key, None)

        # Check if the field is present and non-empty
        is_present = False
        if value is None:
            is_present = False
        elif isinstance(value, str):
            is_present = len(value.strip()) > 0
        elif isinstance(value, list):
            is_present = len(value) > 0
        else:
            # For objects like nutritional_info
            is_present = value is not None

        if is_present:
            findings.append(ComplianceFinding(
                module="labelling",
                severity="INFO",
                title=f"Present: {field_name}",
                description=f"'{field_name}' is present on the label.",
                regulation=regulation,
            ))
        else:
            # Missing expiry_date is OK if best_before is present (and vice versa)
            if json_key == "expiry_date" and label.best_before:
                findings.append(ComplianceFinding(
                    module="labelling",
                    severity="INFO",
                    title=f"Present: {field_name}",
                    description=f"Expiry date not found but 'Best Before' date is present.",
                    regulation=regulation,
                ))
                continue

            findings.append(ComplianceFinding(
                module="labelling",
                severity="WARNING",
                title=f"Missing: {field_name}",
                description=f"Mandatory field '{field_name}' was not found on the label.",
                regulation=regulation,
                recommendation=f"Ensure '{field_name}' is clearly displayed on the packaging.",
            ))

    return findings


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MASTER: Run all 5 modules
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all_checks(label: LabelData) -> list[ComplianceFinding]:
    """Run all 5 compliance modules and return combined findings."""
    findings = []
    findings.extend(check_additives(label))
    findings.extend(check_allergens(label))
    findings.extend(check_claims(label))
    findings.extend(check_license(label))
    findings.extend(check_labelling(label))
    return findings
