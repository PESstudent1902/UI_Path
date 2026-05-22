import os
import json
from typing import Dict, Any, List, Tuple

# Pricing Database Loading Helper
DEFAULT_DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "sample-data",
    "pricing_database.json"
)

def load_pricing_database(db_path: str = DEFAULT_DATABASE_PATH) -> Dict[str, Any]:
    try:
        with open(db_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading pricing database at {db_path}: {e}. Using inline default pricing.")
        # Inline fallback defaults
        return {
            "pricing_database": {
                "Main fabric - Cotton Pique": 4.50,
                "Rib fabric - collar/cuffs": 3.20,
                "Interlining - collar": 1.80,
                "Thread - main": 0.02,
                "Buttons - 3 hole": 0.05,
                "Care label": 0.08,
                "Size label": 0.06
            },
            "cmt_rates": {
                "T-shirt": 2.50,
                "Polo Shirt": 3.20,
                "Shirt": 4.50,
                "Dress": 6.00,
                "Jacket": 12.00
            }
        }


def find_matching_price(item_name: str, pricing_db: Dict[str, float]) -> float:
    """Robust lookup that performs exact, case-insensitive, and substring matching."""
    item_lower = item_name.lower()
    
    # 1. Exact match
    if item_name in pricing_db:
        return pricing_db[item_name]
        
    # 2. Case-insensitive match
    for db_item, price in pricing_db.items():
        if db_item.lower() == item_lower:
            return price
            
    # 3. Substring matching (e.g. "Main fabric" matches "Main fabric - Cotton Pique")
    for db_item, price in pricing_db.items():
        db_item_lower = db_item.lower()
        if db_item_lower in item_lower or item_lower in db_item_lower:
            return price
            
    # 4. Keyword Fallback
    if "fabric" in item_lower:
        if "rib" in item_lower:
            return pricing_db.get("Rib fabric - collar/cuffs", 3.20)
        return pricing_db.get("Main fabric - Cotton Pique", 4.50)
    elif "thread" in item_lower:
        return pricing_db.get("Thread - main", 0.02)
    elif "button" in item_lower:
        return pricing_db.get("Buttons - 3 hole", 0.05)
    elif "label" in item_lower:
        return pricing_db.get("Care label", 0.08)
        
    return 0.10 # Standard fallback default


def calculate_fabric_consumption(garment_type: str, measurements: Dict[str, Any], fabric_width: float) -> float:
    """
    Geometric formula for initial fabric consumption estimate in yards per piece.
    Includes seam allowances and a standard 10% wastage multiplier.
    """
    # Extract Medium or closest size as baseline
    chest_sizes = measurements.get("chest", {})
    length_sizes = measurements.get("length", {})
    
    sizes = list(chest_sizes.keys())
    if not sizes:
        chest = 40.0 # Default fallback
    elif "M" in sizes:
        chest = float(chest_sizes["M"])
    elif "L" in sizes:
        chest = float(chest_sizes["L"])
    else:
        # Get middle element
        chest = float(chest_sizes[sizes[len(sizes)//2]])
        
    if not length_sizes:
        length = 28.0 # Default fallback
    elif "M" in length_sizes:
        length = float(length_sizes["M"])
    elif "L" in length_sizes:
        length = float(length_sizes["L"])
    else:
        length = float(length_sizes[list(length_sizes.keys())[len(length_sizes)//2]])
        
    # Garment type multipliers (calibrated for consumption volume details)
    type_factors = {
        "T-shirt": 1.0,
        "Polo Shirt": 1.15,  # Placket and collar trims
        "Shirt": 1.3,        # Yoke, button cuffs, and long sleeves
        "Dress": 1.8,        # Large skirt area and waist gathers
        "Jacket": 2.2,       # Lining, panels, and pockets
        "Pants": 1.4         # Front/back rises and waistband
    }
    
    factor = type_factors.get(garment_type, 1.0)
    
    # Seam allowance = 2 inches total
    seam_allowance = 2.0
    chest_factor = chest / fabric_width
    
    # Core geometric formula
    consumption_base = (2.0 * (length + seam_allowance) / 36.0) * chest_factor * factor
    
    # 10% Cutting and Pattern Matching Wastage
    consumption_with_wastage = consumption_base * 1.10
    
    return round(consumption_with_wastage, 2)


def process_costing(style_data: Dict[str, Any], order_quantity: Dict[str, int], markup_percentage: float = None) -> Dict[str, Any]:
    """
    Core costing calculations.
    Returns structured BOM breakdowns, fabric consumption details, factory cost, and FOB price.
    """
    db = load_pricing_database()
    pricing_db = db.get("pricing_database", {})
    cmt_rates = db.get("cmt_rates", {})
    
    garment_type = style_data.get("garment_type", "T-shirt")
    measurements = style_data.get("measurements", {})
    fabric_width = style_data.get("fabric_width", 60.0)
    bom_items = style_data.get("bill_of_materials", [])
    
    # 1. Calculate main fabric consumption
    main_fabric_cons = calculate_fabric_consumption(garment_type, measurements, fabric_width)
    
    # 2. Compile Material Costs
    material_breakdown = []
    total_material_cost = 0.0
    
    for item in bom_items:
        item_name = item.get("item", "")
        unit = item.get("unit", "")
        extracted_cons = item.get("consumption_per_piece", 0.0)
        if extracted_cons is None:
            extracted_cons = 0.0
        
        # Override fabric consumption with geometric calculation if it represents main fabric
        is_main_fabric = "main fabric" in item_name.lower() or ("fabric" in item_name.lower() and not "rib" in item_name.lower())
        is_rib_fabric = "rib fabric" in item_name.lower() or "collar" in item_name.lower()
        
        consumption = extracted_cons
        if is_main_fabric:
            consumption = main_fabric_cons
        elif is_rib_fabric and extracted_cons == 0:
            # Estimate rib as ~18% of main fabric consumption
            consumption = round(main_fabric_cons * 0.18, 2)
        
        if consumption is None:
            consumption = 0.0

            
        rate = find_matching_price(item_name, pricing_db)
        cost = round(consumption * rate, 2)
        total_material_cost += cost
        
        material_breakdown.append({
            "item": item_name,
            "consumption": consumption,
            "unit": unit,
            "rate": rate,
            "cost": cost
        })
        
    total_material_cost = round(total_material_cost, 2)
    
    # 3. CMT rates lookup
    cmt_cost = cmt_rates.get(garment_type, 3.00)
    
    # 4. Factory and FOB Cost
    factory_cost = round(total_material_cost + cmt_cost, 2)
    if markup_percentage is not None:
        markup_pct = float(markup_percentage)
    else:
        markup_pct = float(os.environ.get("DEFAULT_MARKUP", 0.15))
    markup_cost = round(factory_cost * markup_pct, 2)
    fob_price = round(factory_cost + markup_cost, 2)
    
    # 5. Order Quantities & Value
    total_qty = sum(order_quantity.values()) if order_quantity else 0
    if total_qty == 0:
        # Default mock order quantities for demo
        order_quantity = {"S": 1000, "M": 1500, "L": 1200, "XL": 800}
        total_qty = sum(order_quantity.values())
        
    total_order_value = round(fob_price * total_qty, 2)
    
    # Prepare details response
    from datetime import datetime
    costing_sheet = {
        "style_name": style_data.get("style_name", "Unknown Style"),
        "style_number": style_data.get("style_number", "N/A"),
        "costing_date": datetime.now().strftime("%Y-%m-%d"),
        "currency": "USD",
        "fabric_consumption": {
            "main_fabric_yards_per_piece": main_fabric_cons,
            "fabric_width_inches": fabric_width,
            "garment_type_factor": garment_type
        },
        "material_cost_breakdown": material_breakdown,
        "total_material_cost": total_material_cost,
        "cmt_cost": cmt_cost,
        "factory_cost_per_piece": factory_cost,
        "markup_percentage": int(markup_pct * 100),
        "fob_price_per_piece": fob_price,
        "order_quantity": {**order_quantity, "total": total_qty},
        "total_order_value": total_order_value,
        "notes": [
            "Main fabric consumption calculated dynamically using geometric body specification math.",
            "Material rates sourced from regional pricing catalog (sample-data/pricing_database.json).",
            "FOB price includes default factory markup margins."
        ]
    }
    
    return costing_sheet
