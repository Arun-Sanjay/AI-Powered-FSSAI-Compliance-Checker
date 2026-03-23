"""
Claude Vision service — sends a food label image to Claude and gets structured JSON back.
Uses claude-sonnet-4-20250514 for cost efficiency (~$0.005 per scan).
"""

import base64
import json
import os

import anthropic
from dotenv import load_dotenv

from models.schemas import LabelData

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(dotenv_path, override=True)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

EXTRACTION_PROMPT = """You are a food label analysis expert. Analyze this food product label image and extract ALL information into a structured JSON format.

Extract the following fields. If a field is not visible or not present on the label, use null for strings/objects or [] for arrays. Do NOT guess or fabricate information — only extract what is actually visible on the label.

Return ONLY valid JSON (no markdown, no code blocks, no explanation) with this exact structure:

{
  "product_name": "string or null",
  "brand": "string or null",
  "food_category": "string or null — e.g., Snacks, Beverages, Dairy, Bakery, Confectionery, Cereals, Condiments, Ready-to-eat, Frozen foods, etc.",
  "net_weight": "string or null — include unit, e.g., '200g', '500ml'",
  "ingredients": ["ingredient1", "ingredient2", ...],
  "additives": [
    {"name": "Additive Name", "e_code": "E-number or null", "function": "function or null"}
  ],
  "declared_allergens": ["allergen1", "allergen2", ...],
  "nutritional_claims": ["claim1", "claim2", ...],
  "fssai_license": "14-digit number as string, or null",
  "manufacturing_date": "string or null — keep original format from label",
  "expiry_date": "string or null",
  "best_before": "string or null",
  "vegetarian_status": "veg or non-veg or not_specified",
  "detected_languages": ["English", "Hindi", ...],
  "nutritional_info": {
    "energy_kcal": number or null,
    "protein_g": number or null,
    "carbohydrates_g": number or null,
    "sugar_g": number or null,
    "total_fat_g": number or null,
    "saturated_fat_g": number or null,
    "trans_fat_g": number or null,
    "sodium_mg": number or null,
    "fiber_g": number or null
  }
}

Important extraction rules:
1. For INGREDIENTS: Split the full ingredients list into individual ingredients. Include sub-ingredients. Preserve the original names.
2. For ADDITIVES: Identify food additives by name or E-code. Common additives include preservatives, emulsifiers, colorants, antioxidants, sweeteners, thickeners, flavour enhancers. If an ingredient IS an additive (e.g., "Sodium Benzoate", "E322", "MSG"), include it in BOTH the ingredients list AND the additives array.
3. For ALLERGENS: Only include allergens explicitly declared in a "Contains" or "Allergen Information" section on the label. Do NOT infer allergens from ingredients — that is done separately by the compliance engine.
4. For NUTRITIONAL INFO: Extract values per 100g if available, otherwise per serving. Convert sodium from mg if given in g (multiply by 1000). All values should be numbers, not strings.
5. For FSSAI LICENSE: Look for a 14-digit number, often near the FSSAI logo or at the bottom of the label. It may be prefixed with "Lic. No." or "FSSAI Lic."
6. For NUTRITIONAL CLAIMS: Look for claims like "Sugar Free", "No Trans Fat", "High Protein", "Low Fat", "Natural", "No Artificial Colors", "No Added Sugar", "Whole Grain", etc.
7. If the label contains Hindi or other Indian language text alongside English, extract the English text. If only Hindi is present, transliterate to English.
8. Fix obvious OCR-like reading errors in printed text (e.g., "Sod1um" → "Sodium").
9. For DETECTED LANGUAGES: List all languages visible on the label (e.g., ["English", "Hindi", "Tamil"]). Include every script/language you can identify."""


def extract_label_data(image_bytes: bytes, content_type: str = "image/jpeg") -> LabelData:
    """
    Send a food label image to Claude Vision and get structured label data back.

    Args:
        image_bytes: Raw image bytes
        content_type: MIME type (image/jpeg, image/png, image/webp)

    Returns:
        LabelData: Parsed and validated label data
    """
    # Encode image to base64
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    # Map content types
    media_type = content_type
    if media_type not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
        media_type = "image/jpeg"

    # Call Claude Vision
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT,
                    },
                ],
            }
        ],
    )

    # Parse the response
    raw_text = message.content[0].text.strip()

    # Handle case where Claude wraps JSON in code blocks
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]  # remove first line (```json)
        raw_text = raw_text.rsplit("```", 1)[0]  # remove last ```
        raw_text = raw_text.strip()

    data = json.loads(raw_text)

    # Validate through Pydantic
    return LabelData.model_validate(data)
