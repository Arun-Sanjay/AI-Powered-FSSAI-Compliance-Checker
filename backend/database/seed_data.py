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

    # ── Additional Colorants ──
    ("E101a", "Riboflavin-5-Phosphate", "Colorant", "approved", 50, "All food categories", "Sodium salt of riboflavin"),
    ("E150b", "Caustic Sulphite Caramel", "Colorant", "approved", None, "Beverages, sauces", "Caramel variant; used in spirits"),
    ("E150c", "Ammonia Caramel", "Colorant", "approved", None, "Beverages, soy sauce, bakery", "Caramel variant; used in beer and soy sauce"),
    ("E150d", "Sulphite Ammonia Caramel", "Colorant", "approved", None, "Beverages, confectionery", "Most common caramel color in soft drinks"),
    ("E155", "Brown HT", "Colorant", "restricted", 50, "Confectionery, bakery", "Synthetic brown; banned in some countries"),
    ("E160c", "Paprika Extract", "Colorant", "approved", None, "Snacks, sauces, dairy", "Natural red-orange from capsicum"),
    ("E160d", "Lycopene", "Colorant", "approved", None, "Beverages, dairy, sauces", "Natural red from tomatoes"),
    ("E160e", "Beta-Apo-8-Carotenal", "Colorant", "approved", 50, "Dairy, bakery", "Semi-synthetic carotenoid"),
    ("E161b", "Lutein", "Colorant", "approved", None, "Bakery, dairy, confectionery", "Natural yellow from marigold"),
    ("E162", "Beetroot Red", "Colorant", "approved", None, "Dairy, confectionery, beverages", "Natural red from beetroot"),
    ("E163", "Anthocyanins", "Colorant", "approved", None, "Beverages, dairy, confectionery", "Natural purple-red from berries"),
    ("E172", "Iron Oxides", "Colorant", "restricted", 50, "Confectionery, coatings", "Synthetic; limited to surface coloring"),
    ("E174", "Silver", "Colorant", "restricted", None, "Confectionery (varq)", "Traditional Indian use; limited applications"),
    ("E175", "Gold", "Colorant", "restricted", None, "Confectionery (varq)", "Traditional Indian use; limited applications"),

    # ── Additional Preservatives ──
    ("E214", "Ethyl Paraben", "Preservative", "restricted", 1000, "Sauces, pickles", "Paraben; restricted in infant foods"),
    ("E218", "Methyl Paraben", "Preservative", "restricted", 1000, "Sauces, pickles, beverages", "Paraben; restricted in infant foods"),
    ("E230", "Biphenyl", "Preservative", "restricted", 70, "Citrus fruit surfaces", "Post-harvest fungicide; surface treatment only"),
    ("E231", "Orthophenyl Phenol", "Preservative", "restricted", 12, "Citrus fruit surfaces", "Post-harvest fungicide"),
    ("E235", "Natamycin", "Preservative", "approved", 20, "Cheese, sausage surfaces", "Natural antifungal from Streptomyces"),
    ("E242", "Dimethyl Dicarbonate", "Preservative", "approved", 250, "Beverages", "Cold sterilant; decomposes in beverage"),
    ("E282", "Calcium Propionate", "Preservative", "approved", 3000, "Bakery products", "Mold inhibitor; most common in bread"),
    ("E283", "Potassium Propionate", "Preservative", "approved", 3000, "Bakery products", "Salt of propionic acid"),
    ("E285", "Sodium Tetraborate", "Preservative", "banned", None, None, "Borax; banned in food in India"),

    # ── Additional Antioxidants & Acidity Regulators ──
    ("E302", "Calcium Ascorbate", "Antioxidant", "approved", None, "All food categories", "Calcium salt of vitamin C"),
    ("E303", "Potassium Ascorbate", "Antioxidant", "approved", None, "All food categories", "Potassium salt of vitamin C"),
    ("E315", "Erythorbic Acid", "Antioxidant", "approved", 500, "Meat products, beverages", "Isomer of ascorbic acid"),
    ("E316", "Sodium Erythorbate", "Antioxidant", "approved", 500, "Meat products", "Salt of erythorbic acid"),
    ("E325", "Sodium Lactate", "Acidity Regulator", "approved", None, "Meat, bakery, confectionery", "Sodium salt of lactic acid"),
    ("E326", "Potassium Lactate", "Acidity Regulator", "approved", None, "Meat products", "Potassium salt of lactic acid"),
    ("E327", "Calcium Lactate", "Acidity Regulator", "approved", None, "Bakery, confectionery, canned fruit", "Calcium salt of lactic acid"),
    ("E333", "Calcium Citrate", "Acidity Regulator", "approved", None, "All food categories", "Calcium salt of citric acid"),
    ("E335", "Sodium Tartrate", "Acidity Regulator", "approved", None, "Bakery, beverages", "Sodium salt of tartaric acid"),
    ("E336", "Potassium Tartrate", "Acidity Regulator", "approved", None, "Bakery", "Cream of tartar"),
    ("E337", "Sodium Potassium Tartrate", "Acidity Regulator", "approved", None, "Bakery, confectionery", "Rochelle salt"),
    ("E339", "Sodium Phosphate", "Acidity Regulator", "approved", None, "Dairy, meat, beverages", "Emulsifying salt"),
    ("E340", "Potassium Phosphate", "Acidity Regulator", "approved", None, "Dairy, beverages", "Buffer and emulsifying salt"),
    ("E341", "Calcium Phosphate", "Acidity Regulator", "approved", None, "Bakery, dairy, confectionery", "Firming agent and anti-caking"),
    ("E350", "Sodium Malate", "Acidity Regulator", "approved", None, "Beverages, confectionery", "Sodium salt of malic acid"),
    ("E351", "Potassium Malate", "Acidity Regulator", "approved", None, "Beverages", "Potassium salt of malic acid"),
    ("E352", "Calcium Malate", "Acidity Regulator", "approved", None, "Confectionery, bakery", "Calcium salt of malic acid"),
    ("E354", "Calcium Tartrate", "Acidity Regulator", "approved", None, "Bakery", "Calcium salt of tartaric acid"),
    ("E355", "Adipic Acid", "Acidity Regulator", "approved", None, "Beverages, confectionery", "Acidulant with smooth taste"),
    ("E380", "Triammonium Citrate", "Acidity Regulator", "approved", None, "Dairy, confectionery", "Ammonium salt of citric acid"),
    ("E385", "Calcium Disodium EDTA", "Sequestrant", "restricted", 75, "Canned foods, dressings, sauces", "Metal chelator; preserves color"),
    ("E296", "Malic Acid", "Acidity Regulator", "approved", None, "Beverages, confectionery", "Natural; found in apples"),

    # ── Additional Emulsifiers & Stabilizers ──
    ("E401", "Sodium Alginate", "Thickener", "approved", None, "Dairy, beverages, desserts", "Natural from seaweed"),
    ("E402", "Potassium Alginate", "Thickener", "approved", None, "Dairy, beverages", "Potassium salt of alginic acid"),
    ("E403", "Ammonium Alginate", "Thickener", "approved", None, "Beverages, desserts", "Ammonium salt of alginic acid"),
    ("E404", "Calcium Alginate", "Thickener", "approved", None, "Restructured foods", "Gelling agent"),
    ("E405", "Propylene Glycol Alginate", "Thickener", "approved", None, "Dressings, beverages, ice cream", "Stabilizer in acidic products"),
    ("E406", "Agar", "Gelling Agent", "approved", None, "Confectionery, desserts, dairy", "Natural from seaweed"),
    ("E416", "Karaya Gum", "Thickener", "approved", None, "Sauces, dairy, bakery", "Natural exudate gum"),
    ("E417", "Tara Gum", "Thickener", "approved", None, "Dairy, sauces, ice cream", "Natural from tara seeds"),
    ("E418", "Gellan Gum", "Gelling Agent", "approved", None, "Dairy, beverages, confectionery", "Produced by fermentation"),
    ("E425", "Konjac Gum", "Thickener", "approved", None, "Noodles, confectionery", "Natural from konjac plant"),
    ("E431", "Polyoxyethylene Stearate", "Emulsifier", "restricted", 5000, "Bakery", "Synthetic emulsifier"),
    ("E432", "Polysorbate 20", "Emulsifier", "approved", 5000, "Ice cream, confectionery", "Tween 20"),
    ("E433", "Polysorbate 80", "Emulsifier", "approved", 5000, "Ice cream, sauces, bakery", "Tween 80; widely used"),
    ("E434", "Polysorbate 40", "Emulsifier", "approved", 5000, "Ice cream, confectionery", "Tween 40"),
    ("E435", "Polysorbate 60", "Emulsifier", "approved", 5000, "Bakery, confectionery", "Tween 60"),
    ("E436", "Polysorbate 65", "Emulsifier", "approved", 5000, "Ice cream, confectionery", "Tween 65"),
    ("E442", "Ammonium Phosphatides", "Emulsifier", "approved", None, "Chocolate, cocoa products", "Chocolate emulsifier"),
    ("E461", "Methyl Cellulose", "Thickener", "approved", None, "Sauces, bakery, ice cream", "Modified cellulose; vegan gelatin substitute"),
    ("E463", "Hydroxypropyl Cellulose", "Thickener", "approved", None, "Bakery, sauces", "Modified cellulose"),
    ("E464", "Hydroxypropyl Methyl Cellulose", "Thickener", "approved", None, "Bakery, sauces, confectionery", "Modified cellulose; film former"),
    ("E465", "Ethyl Methyl Cellulose", "Thickener", "approved", None, "Foamed toppings", "Modified cellulose"),
    ("E470a", "Sodium/Potassium/Calcium Stearate", "Emulsifier", "approved", None, "Bakery, confectionery", "Fatty acid salts"),
    ("E470b", "Magnesium Stearate", "Emulsifier", "approved", None, "Confectionery, supplements", "Anti-caking agent"),
    ("E473", "Sucrose Esters", "Emulsifier", "approved", 5000, "Bakery, beverages, dairy", "Sugar-based emulsifiers"),
    ("E474", "Sucroglycerides", "Emulsifier", "approved", 5000, "Bakery, dairy", "Mixed sugar/glycerol esters"),
    ("E475", "Polyglycerol Esters", "Emulsifier", "approved", None, "Bakery, confectionery", "Bread improver"),
    ("E476", "Polyglycerol Polyricinoleate", "Emulsifier", "approved", None, "Chocolate, confectionery", "PGPR; chocolate viscosity reducer"),
    ("E477", "Propylene Glycol Esters", "Emulsifier", "approved", 5000, "Bakery, toppings", "Whipped topping stabilizer"),
    ("E481", "Sodium Stearoyl Lactylate", "Emulsifier", "approved", 5000, "Bakery products", "SSL; dough conditioner"),
    ("E482", "Calcium Stearoyl Lactylate", "Emulsifier", "approved", 5000, "Bakery products", "CSL; dough conditioner"),
    ("E491", "Sorbitan Monostearate", "Emulsifier", "approved", 5000, "Confectionery, bakery, toppings", "Span 60"),
    ("E492", "Sorbitan Tristearate", "Emulsifier", "approved", 5000, "Chocolate, confectionery", "Span 65"),
    ("E495", "Sorbitan Monopalmitate", "Emulsifier", "approved", 5000, "Confectionery, bakery", "Span 40"),

    # ── Anti-caking Agents ──
    ("E535", "Sodium Ferrocyanide", "Anti-caking Agent", "approved", 20, "Salt", "Prevents caking in table salt"),
    ("E536", "Potassium Ferrocyanide", "Anti-caking Agent", "approved", 20, "Salt, wine", "Anti-caking in salt"),
    ("E538", "Calcium Ferrocyanide", "Anti-caking Agent", "approved", 20, "Salt", "Anti-caking in salt"),
    ("E541", "Sodium Aluminium Phosphate", "Raising Agent", "restricted", None, "Bakery products", "Contains aluminium; restricted"),
    ("E551", "Silicon Dioxide", "Anti-caking Agent", "approved", 10000, "Powdered foods, spices", "Silica; prevents clumping"),
    ("E552", "Calcium Silicate", "Anti-caking Agent", "approved", 10000, "Salt, powdered foods", "Prevents caking"),
    ("E553a", "Magnesium Silicate", "Anti-caking Agent", "approved", None, "Confectionery, supplements", "Talc; surface treatment"),
    ("E554", "Sodium Aluminosilicate", "Anti-caking Agent", "restricted", None, "Salt, powdered foods", "Contains aluminium"),
    ("E570", "Stearic Acid", "Anti-caking Agent", "approved", None, "Confectionery, chewing gum", "Fatty acid; glazing agent"),
    ("E572", "Magnesium Stearate", "Anti-caking Agent", "approved", None, "Confectionery, supplements", "Flow agent"),

    # ── Glazing Agents & Gases ──
    ("E900", "Dimethylpolysiloxane", "Anti-foaming Agent", "approved", 10, "Cooking oils, beverages", "Silicone-based anti-foamer"),
    ("E901", "Beeswax", "Glazing Agent", "approved", None, "Confectionery, fruit coatings", "Natural wax"),
    ("E903", "Carnauba Wax", "Glazing Agent", "approved", None, "Confectionery, fruit, chewing gum", "Natural plant wax"),
    ("E904", "Shellac", "Glazing Agent", "approved", None, "Confectionery, fruit, pharmaceutical", "Natural resin from lac insects"),
    ("E914", "Oxidized Polyethylene Wax", "Glazing Agent", "restricted", None, "Fruit surfaces", "Synthetic; limited to surface coating"),
    ("E938", "Argon", "Propellant Gas", "approved", None, "Modified atmosphere packaging", "Inert gas"),
    ("E941", "Nitrogen", "Propellant Gas", "approved", None, "Modified atmosphere packaging, beverages", "Inert gas; used in nitro coffee"),
    ("E942", "Nitrous Oxide", "Propellant Gas", "approved", None, "Whipped cream dispensers", "Propellant for aerosol cream"),
    ("E948", "Oxygen", "Packaging Gas", "approved", None, "Modified atmosphere packaging", "For meat packaging"),

    # ── Additional Sweeteners ──
    ("E953", "Isomalt", "Sweetener", "approved", None, "Sugar-free confectionery", "Sugar alcohol; half the calories of sugar"),
    ("E956", "Alitame", "Sweetener", "approved", None, "Beverages, confectionery", "2000x sweeter than sugar"),
    ("E957", "Thaumatin", "Sweetener", "approved", None, "Confectionery, chewing gum", "Natural protein sweetener"),
    ("E961", "Neotame", "Sweetener", "approved", 33, "Beverages, dairy, bakery", "8000x sweeter than sugar; aspartame derivative"),
    ("E962", "Aspartame-Acesulfame Salt", "Sweetener", "approved", None, "Beverages, confectionery", "Combined sweetener"),
    ("E965", "Maltitol", "Sweetener", "approved", None, "Sugar-free confectionery, bakery", "Sugar alcohol"),
    ("E966", "Lactitol", "Sweetener", "approved", None, "Sugar-free confectionery", "Sugar alcohol from lactose"),
    ("E968", "Erythritol", "Sweetener", "approved", None, "Beverages, confectionery, bakery", "Zero-calorie sugar alcohol"),
    ("E969", "Advantame", "Sweetener", "approved", 5, "Beverages, dairy", "20000x sweeter than sugar"),
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

    # Category 9: Sesame
    ("sesame", "Sesame"),
    ("til", "Sesame"),
    ("gingelly", "Sesame"),
    ("sesame oil", "Sesame"),
    ("sesame seeds", "Sesame"),
    ("tahini", "Sesame"),
    ("sesame paste", "Sesame"),
    ("til oil", "Sesame"),

    # Category 10: Mustard
    ("mustard", "Mustard"),
    ("mustard oil", "Mustard"),
    ("mustard seed", "Mustard"),
    ("mustard powder", "Mustard"),
    ("sarson", "Mustard"),
    ("rai", "Mustard"),

    # Category 11: Celery
    ("celery", "Celery"),
    ("celeriac", "Celery"),
    ("celery salt", "Celery"),
    ("celery seed", "Celery"),

    # Category 12: Lupin
    ("lupin", "Lupin"),
    ("lupini", "Lupin"),
    ("lupin flour", "Lupin"),

    # Category 13: Molluscs
    ("squid", "Molluscs"),
    ("octopus", "Molluscs"),
    ("snail", "Molluscs"),
    ("clam", "Molluscs"),
    ("mussel", "Molluscs"),
    ("oyster", "Molluscs"),

    # Category 14: Sulphites
    ("sulphite", "Sulphites"),
    ("sulfite", "Sulphites"),
    ("sulphur dioxide", "Sulphites"),
    ("metabisulphite", "Sulphites"),
    ("sodium metabisulphite", "Sulphites"),
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
    ("source of protein", "protein_g", ">=", 10.0, "% of energy", "FSS Advertising & Claims Regulations, 2018"),
    ("source of fibre", "fiber_g", ">=", 3.0, "g per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("sodium free", "sodium_mg", "<=", 5.0, "mg per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("low energy", "energy_kcal", "<=", 40.0, "kcal per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("energy free", "energy_kcal", "<=", 4.0, "kcal per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("low saturated fat", "saturated_fat_g", "<=", 1.5, "g per 100g", "FSS Advertising & Claims Regulations, 2018"),
    ("saturated fat free", "saturated_fat_g", "<=", 0.1, "g per 100g", "FSS Advertising & Claims Regulations, 2018"),
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
