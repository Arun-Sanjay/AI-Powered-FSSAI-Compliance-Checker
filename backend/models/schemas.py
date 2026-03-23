from pydantic import BaseModel
from typing import Optional


# --- Structures extracted by Claude Vision from the label image ---

class AdditiveInfo(BaseModel):
    name: str
    e_code: Optional[str] = None
    function: Optional[str] = None  # preservative, emulsifier, colorant, etc.


class NutritionalInfo(BaseModel):
    energy_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    sugar_g: Optional[float] = None
    total_fat_g: Optional[float] = None
    saturated_fat_g: Optional[float] = None
    trans_fat_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    fiber_g: Optional[float] = None


class LabelData(BaseModel):
    product_name: Optional[str] = None
    brand: Optional[str] = None
    food_category: Optional[str] = None
    net_weight: Optional[str] = None
    ingredients: list[str] = []
    additives: list[AdditiveInfo] = []
    declared_allergens: list[str] = []
    nutritional_claims: list[str] = []
    fssai_license: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    best_before: Optional[str] = None
    vegetarian_status: Optional[str] = None  # veg / non-veg / not_specified
    nutritional_info: Optional[NutritionalInfo] = None


# --- Compliance engine output ---

class ComplianceFinding(BaseModel):
    module: str  # additives, allergens, claims, license, labelling
    severity: str  # CRITICAL, WARNING, INFO
    title: str
    description: str
    regulation: Optional[str] = None
    recommendation: Optional[str] = None


class ModuleScore(BaseModel):
    module: str
    score: int  # 0-100 for this module
    findings_count: int
    critical_count: int
    warning_count: int


class RiskScore(BaseModel):
    overall_score: int  # 0-100
    grade: str  # A, B, C, F
    modules: list[ModuleScore] = []


# --- Full API response ---

class AnalysisResponse(BaseModel):
    label_data: LabelData
    findings: list[ComplianceFinding] = []
    risk_score: RiskScore
    summary: str  # e.g., "3 critical issues found, 2 warnings"


# --- Database browse responses ---

class AdditiveRecord(BaseModel):
    e_code: str
    name: str
    function: str
    status: str  # approved, restricted, banned
    max_limit_ppm: Optional[float] = None
    permitted_categories: Optional[str] = None
    notes: Optional[str] = None


class AllergenRecord(BaseModel):
    keyword: str
    allergen_category: str


# --- Scenario simulation ---

class SimulationRequest(BaseModel):
    label_data: LabelData
    modifications: dict = {}  # e.g., {"remove_ingredients": ["Soy Lecithin"], "add_allergen_declaration": ["Soy"]}
