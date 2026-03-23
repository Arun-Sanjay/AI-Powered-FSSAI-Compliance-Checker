import sys
import os
import pytest

# Ensure backend/ is on the Python path
sys.path.insert(0, os.path.dirname(__file__))

from models.schemas import LabelData, NutritionalInfo, AdditiveInfo


@pytest.fixture
def label_data():
    """Fully populated label for testing — a fictional biscuit product."""
    return LabelData(
        product_name="Choco Cream Biscuits",
        brand="SnackCo",
        food_category="Bakery",
        net_weight="200g",
        ingredients=[
            "Wheat Flour", "Sugar", "Palm Oil", "Cocoa Powder",
            "Milk Solids", "Salt", "Emulsifier (Soy Lecithin)",
            "Raising Agent (E500)", "Artificial Flavour",
        ],
        additives=[
            AdditiveInfo(name="Soy Lecithin", e_code="E322", function="Emulsifier"),
            AdditiveInfo(name="Sodium Bicarbonate", e_code="E500", function="Raising Agent"),
        ],
        declared_allergens=["Wheat", "Milk", "Soy"],
        nutritional_claims=[],
        fssai_license="10123456789012",
        manufacturing_date="Jan 2025",
        expiry_date="Jan 2026",
        best_before=None,
        vegetarian_status="veg",
        nutritional_info=NutritionalInfo(
            energy_kcal=480.0,
            protein_g=6.5,
            carbohydrates_g=65.0,
            sugar_g=28.0,
            total_fat_g=22.0,
            saturated_fat_g=11.0,
            trans_fat_g=0.0,
            sodium_mg=350.0,
            fiber_g=2.0,
        ),
    )


@pytest.fixture
def empty_label():
    """Empty label — all fields at defaults."""
    return LabelData()


@pytest.fixture
def nutritional_info():
    """Standalone nutritional info fixture."""
    return NutritionalInfo(
        energy_kcal=250.0,
        protein_g=8.0,
        carbohydrates_g=30.0,
        sugar_g=5.0,
        total_fat_g=10.0,
        saturated_fat_g=4.0,
        trans_fat_g=0.1,
        sodium_mg=200.0,
        fiber_g=3.0,
    )
