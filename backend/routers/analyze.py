from fastapi import APIRouter, UploadFile, File, HTTPException
import sqlite3
import os

from models.schemas import (
    AnalysisResponse,
    LabelData,
    ComplianceFinding,
    RiskScore,
    ModuleScore,
    AdditiveRecord,
    AllergenRecord,
)
from services.nlp_parser import extract_label_data
from services.compliance_checker import run_all_checks
from services.risk_scorer import calculate_risk_score, build_summary

router = APIRouter()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "fssai_compliance.db")


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_label(file: UploadFile = File(...)):
    """
    Upload a food label image and get full FSSAI compliance analysis.
    Phase 2: Claude Vision extracts structured data from the image.
    Phase 3 will add real compliance checks — currently uses placeholder findings.
    """
    # Validate file type
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        raise HTTPException(status_code=400, detail="Only image files (JPG, PNG, WebP) are supported.")

    # Read image bytes
    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    # Enforce 10MB file size limit
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    # Extract structured data using Claude Vision
    try:
        label_data = extract_label_data(image_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze label: {str(e)}")

    # Run all 5 compliance modules
    findings = run_all_checks(label_data)

    # Calculate weighted risk score
    risk_score = calculate_risk_score(findings)

    # Build human-readable summary
    summary = build_summary(findings, risk_score)

    return AnalysisResponse(
        label_data=label_data,
        findings=findings,
        risk_score=risk_score,
        summary=summary,
    )


@router.get("/additives", response_model=list[AdditiveRecord])
def get_additives():
    """Browse the full FSSAI additive database."""
    conn = _get_db()
    rows = conn.execute("SELECT e_code, name, function, status, max_limit_ppm, permitted_categories, notes FROM additives ORDER BY e_code").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.get("/allergens", response_model=list[AllergenRecord])
def get_allergens():
    """Browse allergen keyword mappings."""
    conn = _get_db()
    rows = conn.execute("SELECT keyword, allergen_category FROM allergen_keywords ORDER BY allergen_category, keyword").fetchall()
    conn.close()
    return [dict(row) for row in rows]
