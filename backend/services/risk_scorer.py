"""
Risk Scoring Engine — converts compliance findings into a weighted score and grade.

Weights (total = 100):
  - Additives:  25  (serious health risk)
  - Allergens:  30  (life-threatening if undeclared)
  - Claims:     20  (misleading consumers)
  - License:    10  (regulatory/legal)
  - Labelling:  15  (consumer information)

Scoring logic per module:
  - Start at 100
  - Each CRITICAL finding: -25 points
  - Each WARNING finding:  -10 points
  - INFO findings: no penalty
  - Floor at 0
"""

from models.schemas import ComplianceFinding, RiskScore, ModuleScore

MODULE_WEIGHTS = {
    "additives": 25,
    "allergens": 30,
    "claims": 20,
    "license": 10,
    "labelling": 15,
}

CRITICAL_PENALTY = 25
WARNING_PENALTY = 10


def calculate_risk_score(findings: list[ComplianceFinding]) -> RiskScore:
    """Calculate overall risk score from compliance findings."""

    # Group findings by module
    by_module: dict[str, list[ComplianceFinding]] = {m: [] for m in MODULE_WEIGHTS}
    for f in findings:
        if f.module in by_module:
            by_module[f.module].append(f)

    modules = []
    weighted_total = 0

    for module, weight in MODULE_WEIGHTS.items():
        module_findings = by_module[module]

        critical = sum(1 for f in module_findings if f.severity == "CRITICAL")
        warning = sum(1 for f in module_findings if f.severity == "WARNING")

        # Calculate module score
        raw_score = 100 - (critical * CRITICAL_PENALTY) - (warning * WARNING_PENALTY)
        score = max(0, min(100, raw_score))

        modules.append(ModuleScore(
            module=module,
            score=score,
            findings_count=len(module_findings),
            critical_count=critical,
            warning_count=warning,
        ))

        weighted_total += score * weight

    overall = round(weighted_total / 100)

    # Determine grade
    if overall >= 90:
        grade = "A"
    elif overall >= 70:
        grade = "B"
    elif overall >= 50:
        grade = "C"
    else:
        grade = "F"

    return RiskScore(overall_score=overall, grade=grade, modules=modules)


def build_summary(findings: list[ComplianceFinding], score: RiskScore) -> str:
    """Build a human-readable summary string."""
    critical = sum(1 for f in findings if f.severity == "CRITICAL")
    warning = sum(1 for f in findings if f.severity == "WARNING")

    parts = []
    if critical:
        parts.append(f"{critical} critical issue{'s' if critical != 1 else ''}")
    if warning:
        parts.append(f"{warning} warning{'s' if warning != 1 else ''}")

    if parts:
        return f"Grade {score.grade} ({score.overall_score}/100) — {', '.join(parts)} found."
    return f"Grade {score.grade} ({score.overall_score}/100) — No issues found. Full compliance."
