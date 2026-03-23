"""
Seed the FSSAI compliance database with real regulatory data.
Sources:
  - FSS (Food Products Standards & Food Additives) Regulations, 2011 — Schedule I
  - FSS (Labelling & Display) Regulations, 2020
  - FSS (Advertising & Claims) Regulations, 2018
  - FSS (Packaging & Labelling) Regulations, 2011
  - FSS (Licensing & Registration) Regulations, 2011
"""

import os
import sqlite3
from init_db import init_database, DB_PATH


# ──────────────────────────────────────────────
# 1. FOOD ADDITIVES  (50+ entries)
#    Based on FSSAI Schedule I
# ──────────────────────────────────────────────

ADDITIVES = [
    # (e_code, name, function, status, max_limit_ppm, permitted_categories, notes)

    # ── Colorants ──
    ("E100", "Curcumin", "Colorant", "approved", 100, "All food categories", "Natural yellow colorant from turmeric"),
    ("E101", "Riboflavin", "Colorant", "approved", 50, "All food categories", "Vitamin B2, natural yellow"),
    ("E102", "Tartrazine", "Colorant", "restricted", 100, "Beverages, confectionery, snacks", "Synthetic yellow; may cause hyperactivity in children"),
    ("E104", "Quinoline Yellow", "Colorant", "restricted", 50, "Confectionery, beverages", "Synthetic; restricted in infant foods"),
    ("E110", "Sunset Yellow FCF", "Colorant", "restricted", 100, "Beverages, confectionery, snacks", "Synthetic orange-yellow; requires allergen warning in some countries"),
    ("E120", "Carmine", "Colorant", "approved", 100, "Confectionery, dairy, beverages", "Natural red from cochineal insects"),
    ("E122", "Carmoisine", "Colorant", "restricted", 50, "Beverages, confectionery", "Synthetic red; banned in some countries"),
    ("E124", "Ponceau 4R", "Colorant", "restricted", 50, "Confectionery, beverages", "Synthetic red; restricted in children's foods"),
    ("E127", "Erythrosine", "Colorant", "restricted", 50, "Cherries, confectionery", "Synthetic pink-red; restricted use"),
    ("E129", "Allura Red", "Colorant", "restricted", 100, "Beverages, confectionery, snacks", "Synthetic red; common in processed foods"),
    ("E131", "Patent Blue V", "Colorant", "restricted", 50, "Confectionery", "Synthetic blue; limited applications"),
    ("E132", "Indigo Carmine", "Colorant", "restricted", 50, "Confectionery, beverages", "Synthetic blue"),
    ("E133", "Brilliant Blue FCF", "Colorant", "restricted", 100, "Beverages, confectionery, dairy", "Synthetic blue"),
    ("E140", "Chlorophyll", "Colorant", "approved", None, "All food categories", "Natural green from plants"),
    ("E141", "Copper Chlorophyll", "Colorant", "approved", 100, "All food categories", "Semi-synthetic green"),
    ("E150a", "Caramel Color (Plain)", "Colorant", "approved", None, "All food categories", "Natural brown; widely used"),
    ("E153", "Carbon Black", "Colorant", "banned", None, None, "Banned in food use in India"),
    ("E160a", "Beta-Carotene", "Colorant", "approved", None, "All food categories", "Natural orange; provitamin A"),
    ("E160b", "Annatto", "Colorant", "approved", 50, "Dairy, bakery, snacks", "Natural orange-red from seeds"),
    ("E171", "Titanium Dioxide", "Colorant", "banned", None, None, "Banned by FSSAI in 2022 for food use"),

    # ── Preservatives ──
    ("E200", "Sorbic Acid", "Preservative", "approved", 1000, "Dairy, bakery, beverages, sauces", "Effective against molds and yeasts"),
    ("E202", "Potassium Sorbate", "Preservative", "approved", 1000, "Dairy, beverages, sauces, processed foods", "Salt of sorbic acid; widely used"),
    ("E210", "Benzoic Acid", "Preservative", "approved", 600, "Beverages, sauces, pickles", "Effective in acidic foods"),
    ("E211", "Sodium Benzoate", "Preservative", "approved", 600, "Beverages, sauces, pickles, jams", "Most common preservative; can form benzene with vitamin C"),
    ("E212", "Potassium Benzoate", "Preservative", "approved", 600, "Beverages, sauces", "Alternative to sodium benzoate"),
    ("E220", "Sulphur Dioxide", "Preservative", "restricted", 350, "Dried fruits, wine, fruit juices", "Can trigger asthma; must be declared if >10ppm"),
    ("E223", "Sodium Metabisulphite", "Preservative", "restricted", 350, "Dried fruits, wine, fruit juices", "Sulphite-based; allergen risk"),
    ("E234", "Nisin", "Preservative", "approved", 12.5, "Dairy, canned foods", "Natural antimicrobial peptide"),
    ("E249", "Potassium Nitrite", "Preservative", "restricted", 200, "Cured meats", "Restricted to meat products only"),
    ("E250", "Sodium Nitrite", "Preservative", "restricted", 200, "Cured meats, processed meats", "Forms nitrosamines; restricted to meat curing"),
    ("E251", "Sodium Nitrate", "Preservative", "restricted", 500, "Cured meats", "Converts to nitrite; restricted to meats"),
    ("E260", "Acetic Acid", "Preservative", "approved", None, "All food categories", "Vinegar; natural preservative"),
    ("E270", "Lactic Acid", "Preservative", "approved", None, "All food categories", "Natural; produced by fermentation"),
    ("E280", "Propionic Acid", "Preservative", "approved", 3000, "Bakery products, cheese", "Prevents mold in bread"),
    ("E281", "Sodium Propionate", "Preservative", "approved", 3000, "Bakery products", "Salt of propionic acid"),

    # ── Antioxidants ──
    ("E300", "Ascorbic Acid", "Antioxidant", "approved", None, "All food categories", "Vitamin C"),
    ("E301", "Sodium Ascorbate", "Antioxidant", "approved", None, "All food categories", "Salt of vitamin C"),
    ("E304", "Ascorbyl Palmitate", "Antioxidant", "approved", 500, "Oils, fats, bakery", "Fat-soluble vitamin C derivative"),
    ("E306", "Tocopherols", "Antioxidant", "approved", None, "Oils, fats", "Natural vitamin E"),
    ("E307", "Alpha-Tocopherol", "Antioxidant", "approved", None, "Oils, fats", "Synthetic vitamin E"),
    ("E310", "Propyl Gallate", "Antioxidant", "restricted", 200, "Oils, fats, snacks", "Synthetic; restricted in infant foods"),
    ("E319", "TBHQ", "Antioxidant", "restricted", 200, "Oils, fats, snacks, noodles", "Tertiary butylhydroquinone; widely used in fried foods"),
    ("E320", "BHA", "Antioxidant", "restricted", 200, "Oils, fats, snacks", "Butylated hydroxyanisole; potential endocrine disruptor"),
    ("E321", "BHT", "Antioxidant", "restricted", 200, "Oils, fats, cereals, snacks", "Butylated hydroxytoluene; controversial safety profile"),
    ("E330", "Citric Acid", "Acidity Regulator", "approved", None, "All food categories", "Natural; from citrus fruits"),
    ("E331", "Sodium Citrate", "Acidity Regulator", "approved", None, "All food categories", "Buffering agent"),
    ("E332", "Potassium Citrate", "Acidity Regulator", "approved", None, "All food categories", "Buffering agent"),
    ("E334", "Tartaric Acid", "Acidity Regulator", "approved", None, "Beverages, confectionery", "Natural; from grapes"),
    ("E338", "Phosphoric Acid", "Acidity Regulator", "approved", None, "Beverages (cola drinks)", "Common in carbonated drinks"),

    # ── Emulsifiers & Stabilizers ──
    ("E322", "Soy Lecithin", "Emulsifier", "approved", None, "Chocolate, bakery, margarine", "Natural from soybeans; SOY ALLERGEN"),
    ("E407", "Carrageenan", "Stabilizer", "approved", None, "Dairy, beverages, desserts", "Natural from seaweed"),
    ("E410", "Locust Bean Gum", "Thickener", "approved", None, "Dairy, sauces, ice cream", "Natural; from carob seeds"),
    ("E412", "Guar Gum", "Thickener", "approved", None, "Dairy, sauces, bakery, ice cream", "Natural; from guar beans"),
    ("E414", "Gum Arabic", "Stabilizer", "approved", None, "Confectionery, beverages", "Natural; from acacia trees"),
    ("E415", "Xanthan Gum", "Thickener", "approved", None, "Sauces, dressings, dairy, bakery", "Produced by fermentation"),
    ("E440", "Pectin", "Gelling Agent", "approved", None, "Jams, jellies, fruit products", "Natural; from fruit peels"),
    ("E450", "Diphosphates", "Raising Agent", "approved", None, "Bakery products", "Leavening agent"),
    ("E460", "Cellulose", "Bulking Agent", "approved", None, "All food categories", "Natural plant fiber"),
    ("E466", "Carboxymethyl Cellulose", "Thickener", "approved", None, "Sauces, ice cream, bakery", "Modified cellulose"),
    ("E471", "Mono- and Diglycerides", "Emulsifier", "approved", None, "Bakery, margarine, ice cream", "May be from plant or animal origin"),
    ("E472e", "DATEM", "Emulsifier", "approved", None, "Bakery products", "Dough conditioner"),
    ("E500", "Sodium Bicarbonate", "Raising Agent", "approved", None, "Bakery products", "Baking soda"),
    ("E501", "Potassium Carbonate", "Raising Agent", "approved", None, "Bakery, confectionery", "Alkalizing agent"),

    # ── Sweeteners ──
    ("E420", "Sorbitol", "Sweetener", "approved", None, "Sugar-free products, confectionery", "Sugar alcohol; may cause laxative effect"),
    ("E950", "Acesulfame-K", "Sweetener", "approved", 600, "Beverages, confectionery, dairy", "200x sweeter than sugar"),
    ("E951", "Aspartame", "Sweetener", "approved", 600, "Beverages, confectionery, dairy", "Contains phenylalanine; must declare for PKU"),
    ("E952", "Cyclamate", "Sweetener", "banned", None, None, "Banned in India"),
    ("E954", "Saccharin", "Sweetener", "approved", 500, "Beverages, confectionery", "Oldest artificial sweetener"),
    ("E955", "Sucralose", "Sweetener", "approved", 400, "Beverages, dairy, bakery", "600x sweeter than sugar"),
    ("E960", "Steviol Glycosides", "Sweetener", "approved", 350, "Beverages, dairy, confectionery", "Natural from stevia plant"),
    ("E967", "Xylitol", "Sweetener", "approved", None, "Chewing gum, confectionery", "Sugar alcohol; dental benefits"),

    # ── Flavour Enhancers ──
    ("E620", "Glutamic Acid", "Flavour Enhancer", "restricted", 10000, "Snacks, soups, sauces, noodles", "Naturally occurring amino acid"),
    ("E621", "Monosodium Glutamate (MSG)", "Flavour Enhancer", "restricted", 10000, "Snacks, soups, sauces, noodles", "Controversial; banned in infant foods; Chinese Restaurant Syndrome debate"),
    ("E627", "Disodium Guanylate", "Flavour Enhancer", "restricted", 500, "Snacks, soups, noodles", "Often used with MSG"),
    ("E631", "Disodium Inosinate", "Flavour Enhancer", "restricted", 500, "Snacks, soups, noodles", "Often used with MSG"),
    ("E635", "Disodium 5-Ribonucleotides", "Flavour Enhancer", "restricted", 500, "Snacks, soups", "Combination of E627 and E631"),
]


# ──────────────────────────────────────────────
# 2. ALLERGEN KEYWORDS  (60+ entries)
#    Based on FSSAI Labelling & Display Reg 2020
#    8 major allergen categories
# ──────────────────────────────────────────────

ALLERGEN_KEYWORDS = [
    # (keyword, allergen_category)

    # Category 1: Cereals containing gluten
    ("wheat", "Cereals containing gluten"),
    ("maida", "Cereals containing gluten"),
    ("semolina", "Cereals containing gluten"),
    ("suji", "Cereals containing gluten"),
    ("atta", "Cereals containing gluten"),
    ("rye", "Cereals containing gluten"),
    ("barley", "Cereals containing gluten"),
    ("oats", "Cereals containing gluten"),
    ("spelt", "Cereals containing gluten"),
    ("seitan", "Cereals containing gluten"),
    ("gluten", "Cereals containing gluten"),
    ("wheat flour", "Cereals containing gluten"),
    ("whole wheat", "Cereals containing gluten"),
    ("refined wheat flour", "Cereals containing gluten"),

    # Category 2: Crustacean shellfish
    ("shrimp", "Crustacean shellfish"),
    ("prawn", "Crustacean shellfish"),
    ("crab", "Crustacean shellfish"),
    ("lobster", "Crustacean shellfish"),
    ("crayfish", "Crustacean shellfish"),
    ("shrimp paste", "Crustacean shellfish"),
    ("lobster extract", "Crustacean shellfish"),
    ("crustacean", "Crustacean shellfish"),

    # Category 3: Eggs
    ("egg", "Eggs"),
    ("albumin", "Eggs"),
    ("lysozyme", "Eggs"),
    ("meringue", "Eggs"),
    ("egg white", "Eggs"),
    ("egg yolk", "Eggs"),
    ("egg powder", "Eggs"),
    ("ovalbumin", "Eggs"),
    ("egg lecithin", "Eggs"),

    # Category 4: Fish
    ("fish", "Fish"),
    ("anchovy", "Fish"),
    ("fish sauce", "Fish"),
    ("fish oil", "Fish"),
    ("fish extract", "Fish"),
    ("anchovy extract", "Fish"),
    ("cod liver oil", "Fish"),
    ("sardine", "Fish"),
    ("tuna", "Fish"),

    # Category 5: Peanuts
    ("peanut", "Peanuts"),
    ("groundnut", "Peanuts"),
    ("peanut oil", "Peanuts"),
    ("peanut butter", "Peanuts"),
    ("groundnut oil", "Peanuts"),
    ("arachis oil", "Peanuts"),
    ("peanut flour", "Peanuts"),

    # Category 6: Soybeans
    ("soy", "Soybeans"),
    ("soya", "Soybeans"),
    ("soybean", "Soybeans"),
    ("soy lecithin", "Soybeans"),
    ("soybean oil", "Soybeans"),
    ("soy protein", "Soybeans"),
    ("soy sauce", "Soybeans"),
    ("tofu", "Soybeans"),
    ("edamame", "Soybeans"),
    ("miso", "Soybeans"),
    ("tempeh", "Soybeans"),
    ("soy flour", "Soybeans"),

    # Category 7: Milk (including lactose)
    ("milk", "Milk"),
    ("casein", "Milk"),
    ("whey", "Milk"),
    ("lactose", "Milk"),
    ("ghee", "Milk"),
    ("curd", "Milk"),
    ("yogurt", "Milk"),
    ("butter", "Milk"),
    ("cheese", "Milk"),
    ("cream", "Milk"),
    ("skimmed milk", "Milk"),
    ("milk powder", "Milk"),
    ("milk solids", "Milk"),
    ("buttermilk", "Milk"),
    ("whey protein", "Milk"),
    ("paneer", "Milk"),
    ("khoa", "Milk"),
    ("lactalbumin", "Milk"),
    ("dairy", "Milk"),

    # Category 8: Tree nuts
    ("almond", "Tree nuts"),
    ("cashew", "Tree nuts"),
    ("pistachio", "Tree nuts"),
    ("walnut", "Tree nuts"),
    ("hazelnut", "Tree nuts"),
    ("pecan", "Tree nuts"),
    ("macadamia", "Tree nuts"),
    ("brazil nut", "Tree nuts"),
    ("pine nut", "Tree nuts"),
    ("badam", "Tree nuts"),
    ("kaju", "Tree nuts"),
    ("pista", "Tree nuts"),
    ("akhrot", "Tree nuts"),
]


# ──────────────────────────────────────────────
# 3. CLAIMS RULES  (9 entries)
#    Based on FSS (Advertising & Claims) Reg 2018
# ──────────────────────────────────────────────

CLAIMS_RULES = [
    # (claim, condition_field, operator, threshold, unit, regulation)
    ("sugar free", "sugar_g", "<=", 0.5, "g per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("low sugar", "sugar_g", "<=", 5.0, "g per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("fat free", "total_fat_g", "<=", 0.5, "g per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("low fat", "total_fat_g", "<=", 3.0, "g per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("high protein", "protein_g", ">=", 20.0, "% of energy", "FSS Advertising & Claims Regulations, 2018"),
    ("low sodium", "sodium_mg", "<=", 120.0, "mg per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("trans fat free", "trans_fat_g", "<=", 0.2, "g per 100g", "FSSAI 2022 Trans Fat Mandate"),
    ("no added sugar", "sugar_g", "<=", 0.5, "g per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("high fibre", "fiber_g", ">=", 6.0, "g per 100g", "FSS Advertising & Claims Regulations, 2018"),
]


# ──────────────────────────────────────────────
# 4. MANDATORY LABEL FIELDS  (9 entries)
#    Based on FSS Packaging & Labelling Reg 2011
#    + FSS Labelling & Display Reg 2020
# ──────────────────────────────────────────────

MANDATORY_FIELDS = [
    # (field_name, json_key, fssai_reference)
    ("Product name", "product_name", "FSS Packaging & Labelling Regulations, 2011"),
    ("Ingredients list", "ingredients", "FSS Packaging & Labelling Regulations, 2011"),
    ("Net quantity/weight", "net_weight", "FSS Packaging & Labelling Regulations, 2011"),
    ("FSSAI license number", "fssai_license", "FSS Packaging & Labelling Regulations, 2011"),
    ("Manufacturing date", "manufacturing_date", "FSS Packaging & Labelling Regulations, 2011"),
    ("Best before / Expiry date", "expiry_date", "FSS Packaging & Labelling Regulations, 2011"),
    ("Nutritional information", "nutritional_info", "FSS Labelling & Display Regulations, 2020"),
    ("Allergen declaration", "declared_allergens", "FSS Labelling & Display Regulations, 2020"),
    ("Veg/Non-veg symbol", "vegetarian_status", "FSS Packaging & Labelling Regulations, 2011"),
]


def seed_database():
    """Drop existing data and re-seed all tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM additives")
    cursor.execute("DELETE FROM allergen_keywords")
    cursor.execute("DELETE FROM claims_rules")
    cursor.execute("DELETE FROM mandatory_fields")

    # Insert additives
    cursor.executemany(
        "INSERT INTO additives (e_code, name, function, status, max_limit_ppm, permitted_categories, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ADDITIVES,
    )
    print(f"Inserted {len(ADDITIVES)} additives")

    # Insert allergen keywords
    cursor.executemany(
        "INSERT INTO allergen_keywords (keyword, allergen_category) VALUES (?, ?)",
        ALLERGEN_KEYWORDS,
    )
    print(f"Inserted {len(ALLERGEN_KEYWORDS)} allergen keywords")

    # Insert claims rules
    cursor.executemany(
        "INSERT INTO claims_rules (claim, condition_field, operator, threshold, unit, regulation) VALUES (?, ?, ?, ?, ?, ?)",
        CLAIMS_RULES,
    )
    print(f"Inserted {len(CLAIMS_RULES)} claims rules")

    # Insert mandatory fields
    cursor.executemany(
        "INSERT INTO mandatory_fields (field_name, json_key, fssai_reference) VALUES (?, ?, ?)",
        MANDATORY_FIELDS,
    )
    print(f"Inserted {len(MANDATORY_FIELDS)} mandatory fields")

    conn.commit()
    conn.close()
    print("Database seeded successfully!")


if __name__ == "__main__":
    init_database()
    seed_database()
