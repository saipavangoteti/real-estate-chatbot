import pandas as pd
import os
import uuid
from datetime import datetime
from config import PROPERTIES_CSV, LEADS_CSV


# ─── Property Operations ─────────────────────────────────────────────────────

def load_properties() -> pd.DataFrame:
    """Load properties from CSV."""
    if not os.path.exists(PROPERTIES_CSV):
        return pd.DataFrame()
    df = pd.read_csv(PROPERTIES_CSV)
    df.fillna("", inplace=True)
    return df


def search_properties(
    city: str = "",
    prop_type: str = "",
    min_price: float = 0,
    max_price: float = float("inf"),
    min_bedrooms: int = 0,
    max_bedrooms: int = 99,
    location: str = "",
    status: str = "Available",
) -> pd.DataFrame:
    """Search properties based on filters."""
    df = load_properties()
    if df.empty:
        return df

    if status:
        df = df[df["status"].str.lower() == status.lower()]
    if city:
        df = df[df["city"].str.lower().str.contains(city.lower(), na=False)]
    if location:
        df = df[df["location"].str.lower().str.contains(location.lower(), na=False)]
    if prop_type:
        df = df[df["type"].str.lower().str.contains(prop_type.lower(), na=False)]
    if min_price > 0:
        df = df[df["price"].astype(float) >= min_price]
    if max_price < float("inf"):
        df = df[df["price"].astype(float) <= max_price]
    if min_bedrooms > 0:
        df = df[df["bedrooms"].astype(int) >= min_bedrooms]
    if max_bedrooms < 99:
        df = df[df["bedrooms"].astype(int) <= max_bedrooms]

    return df


def get_property_by_id(prop_id: str) -> dict:
    """Get a single property by ID."""
    df = load_properties()
    row = df[df["id"].str.upper() == prop_id.upper()]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


def get_all_property_types() -> list:
    df = load_properties()
    return sorted(df["type"].dropna().unique().tolist()) if not df.empty else []


def get_all_cities() -> list:
    df = load_properties()
    return sorted(df["city"].dropna().unique().tolist()) if not df.empty else []


def format_price(price) -> str:
    """Format price as Indian currency."""
    try:
        price = float(price)
        if price >= 10_000_000:
            return f"₹{price/10_000_000:.2f} Cr"
        elif price >= 100_000:
            return f"₹{price/100_000:.2f} L"
        else:
            return f"₹{price:,.0f}"
    except Exception:
        return str(price)


def property_to_text(prop: dict) -> str:
    """Convert property dict to readable text for the AI."""
    if not prop:
        return "Property not found."
    return (
        f"🏠 **{prop.get('name')}** (ID: {prop.get('id')})\n"
        f"  • Type: {prop.get('type')} | Location: {prop.get('location')}, {prop.get('city')}\n"
        f"  • Price: {format_price(prop.get('price', 0))}\n"
        f"  • Bedrooms: {prop.get('bedrooms')} | Bathrooms: {prop.get('bathrooms')} | Area: {prop.get('area_sqft')} sq.ft\n"
        f"  • Amenities: {prop.get('amenities')}\n"
        f"  • Status: {prop.get('status')}\n"
        f"  • {prop.get('description')}"
    )


def properties_to_text(df: pd.DataFrame) -> str:
    """Convert multiple properties to readable text."""
    if df.empty:
        return "No properties found matching your criteria."
    lines = [f"Found **{len(df)} properties**:\n"]
    for _, row in df.iterrows():
        lines.append(property_to_text(row.to_dict()))
        lines.append("")
    return "\n".join(lines)


# ─── Leads Operations ────────────────────────────────────────────────────────

def save_lead(
    name: str,
    email: str,
    phone: str,
    inquiry_type: str,          # "Site Visit" | "Consultation" | "General Inquiry"
    property_id: str = "",
    property_name: str = "",
    preferred_date: str = "",
    preferred_time: str = "",
    message: str = "",
) -> str:
    """Save a lead to the CSV. Returns the lead ID."""
    lead_id = f"L{datetime.now().strftime('%Y%m%d%H%M%S')}"

    new_row = {
        "id": lead_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name,
        "email": email,
        "phone": phone,
        "inquiry_type": inquiry_type,
        "property_id": property_id,
        "property_name": property_name,
        "preferred_date": preferred_date,
        "preferred_time": preferred_time,
        "message": message,
        "status": "New",
    }

    # Load or create leads dataframe
    if os.path.exists(LEADS_CSV) and os.path.getsize(LEADS_CSV) > 0:
        df = pd.read_csv(LEADS_CSV)
    else:
        df = pd.DataFrame(columns=new_row.keys())

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(LEADS_CSV, index=False)
    return lead_id


def load_leads() -> pd.DataFrame:
    """Load all leads."""
    if not os.path.exists(LEADS_CSV) or os.path.getsize(LEADS_CSV) == 0:
        return pd.DataFrame(columns=[
            "id","timestamp","name","email","phone","inquiry_type",
            "property_id","property_name","preferred_date","preferred_time","message","status"
        ])
    df = pd.read_csv(LEADS_CSV)
    df.fillna("", inplace=True)
    return df


def update_lead_status(lead_id: str, status: str):
    """Update status of a lead."""
    if not os.path.exists(LEADS_CSV):
        return
    df = pd.read_csv(LEADS_CSV)
    df.loc[df["id"] == lead_id, "status"] = status
    df.to_csv(LEADS_CSV, index=False)
