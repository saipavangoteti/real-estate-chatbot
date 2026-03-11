from langchain.tools import tool
from utils.data_manager import (
    search_properties, get_property_by_id,
    properties_to_text, property_to_text,
    save_lead, format_price,
    get_all_property_types, get_all_cities,
)


@tool
def tool_search_properties(query: str) -> str:
    """
    Search for properties based on user requirements.
    Input should be a pipe-separated string of filters:
    city|type|min_price|max_price|min_bedrooms|max_bedrooms|location
    Use empty string for any filter you don't want to apply.
    Example: "Hyderabad|Apartment|3000000|8000000|2|3|Gachibowli"
    """
    try:
        parts = [p.strip() for p in query.split("|")]
        while len(parts) < 7:
            parts.append("")

        city        = parts[0]
        prop_type   = parts[1]
        min_price   = float(parts[2]) if parts[2] else 0
        max_price   = float(parts[3]) if parts[3] else float("inf")
        min_beds    = int(parts[4])   if parts[4] else 0
        max_beds    = int(parts[5])   if parts[5] else 99
        location    = parts[6]

        df = search_properties(
            city=city, prop_type=prop_type,
            min_price=min_price, max_price=max_price,
            min_bedrooms=min_beds, max_bedrooms=max_beds,
            location=location,
        )
        return properties_to_text(df)
    except Exception as e:
        return f"Error searching properties: {str(e)}"


@tool
def tool_get_property_details(property_id: str) -> str:
    """
    Get detailed information about a specific property by its ID.
    Input: Property ID (e.g., P001, P002)
    """
    prop = get_property_by_id(property_id.strip())
    if not prop:
        return f"No property found with ID '{property_id}'. Please check the ID."
    return property_to_text(prop)


@tool
def tool_schedule_site_visit(details: str) -> str:
    """
    Schedule a property site visit.
    Input should be a pipe-separated string:
    name|email|phone|property_id|preferred_date|preferred_time|message
    Example: "John Doe|john@email.com|9876543210|P001|2024-12-25|10:00 AM|Interested in the villa"
    """
    try:
        parts = [p.strip() for p in details.split("|")]
        while len(parts) < 7:
            parts.append("")

        name      = parts[0]
        email     = parts[1]
        phone     = parts[2]
        prop_id   = parts[3]
        date      = parts[4]
        time      = parts[5]
        message   = parts[6]

        # Get property name
        prop = get_property_by_id(prop_id) if prop_id else {}
        prop_name = prop.get("name", "General Inquiry")

        lead_id = save_lead(
            name=name, email=email, phone=phone,
            inquiry_type="Site Visit",
            property_id=prop_id, property_name=prop_name,
            preferred_date=date, preferred_time=time,
            message=message,
        )

        return (
            f"✅ Site visit scheduled successfully!\n"
            f"  • Booking ID: {lead_id}\n"
            f"  • Name: {name}\n"
            f"  • Property: {prop_name} ({prop_id})\n"
            f"  • Date & Time: {date} at {time}\n"
            f"  • Contact: {phone} | {email}\n\n"
            f"Our team will confirm the appointment within 2 hours."
        )
    except Exception as e:
        return f"Error scheduling site visit: {str(e)}"


@tool
def tool_book_consultation(details: str) -> str:
    """
    Book a consultation call with a real estate expert.
    Input should be a pipe-separated string:
    name|email|phone|preferred_date|preferred_time|message
    Example: "Jane Smith|jane@email.com|9876543210|2024-12-26|2:00 PM|Looking for investment properties"
    """
    try:
        parts = [p.strip() for p in details.split("|")]
        while len(parts) < 6:
            parts.append("")

        name    = parts[0]
        email   = parts[1]
        phone   = parts[2]
        date    = parts[3]
        time    = parts[4]
        message = parts[5]

        lead_id = save_lead(
            name=name, email=email, phone=phone,
            inquiry_type="Consultation",
            preferred_date=date, preferred_time=time,
            message=message,
        )

        return (
            f"✅ Consultation booked successfully!\n"
            f"  • Booking ID: {lead_id}\n"
            f"  • Name: {name}\n"
            f"  • Date & Time: {date} at {time}\n"
            f"  • Contact: {phone} | {email}\n\n"
            f"A senior real estate advisor will call you at the scheduled time."
        )
    except Exception as e:
        return f"Error booking consultation: {str(e)}"


@tool
def tool_calculate_emi(details: str) -> str:
    """
    Calculate home loan EMI.
    Input should be pipe-separated: loan_amount|interest_rate|tenure_years
    Example: "5000000|8.5|20"
    """
    try:
        parts = [p.strip() for p in details.split("|")]
        principal     = float(parts[0])
        annual_rate   = float(parts[1])
        tenure_years  = int(parts[2])

        monthly_rate  = annual_rate / (12 * 100)
        n_months      = tenure_years * 12

        if monthly_rate == 0:
            emi = principal / n_months
        else:
            emi = principal * monthly_rate * (1 + monthly_rate) ** n_months / ((1 + monthly_rate) ** n_months - 1)

        total_payment = emi * n_months
        total_interest = total_payment - principal

        return (
            f"🏦 **EMI Calculation**\n"
            f"  • Loan Amount: {format_price(principal)}\n"
            f"  • Interest Rate: {annual_rate}% per annum\n"
            f"  • Tenure: {tenure_years} years ({n_months} months)\n"
            f"  • **Monthly EMI: {format_price(emi)}**\n"
            f"  • Total Interest: {format_price(total_interest)}\n"
            f"  • Total Payment: {format_price(total_payment)}\n\n"
            f"_Note: Actual EMI may vary based on bank policies and credit score._"
        )
    except Exception as e:
        return f"Error calculating EMI: {str(e)}"


@tool
def tool_get_available_options(query: str) -> str:
    """
    Get available property types and cities.
    Input: "types" to get property types, "cities" to get cities, "all" for both.
    """
    query = query.lower().strip()
    result = []
    if query in ("types", "all"):
        types = get_all_property_types()
        result.append(f"Available Property Types: {', '.join(types)}")
    if query in ("cities", "all"):
        cities = get_all_cities()
        result.append(f"Available Cities: {', '.join(cities)}")
    return "\n".join(result) if result else "No data available."


# Export all tools
REAL_ESTATE_TOOLS = [
    tool_search_properties,
    tool_get_property_details,
    tool_schedule_site_visit,
    tool_book_consultation,
    tool_calculate_emi,
    tool_get_available_options,
]
