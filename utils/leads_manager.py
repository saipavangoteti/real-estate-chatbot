"""
leads_manager.py
Handles all read/write operations for leads.csv
"""

import csv
import os
from datetime import datetime

LEADS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "leads.csv")

FIELDNAMES = [
    "timestamp", "name", "phone", "email", "query_type",
    "property_id", "property_title", "preferred_date", "preferred_time",
    "budget", "location_preference", "message", "status"
]


def _ensure_file():
    """Create leads.csv with headers if it doesn't exist."""
    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def save_lead(data: dict) -> bool:
    """
    Save a lead to leads.csv.
    data keys should match FIELDNAMES (missing keys default to empty string).
    Returns True on success, False on failure.
    """
    _ensure_file()
    try:
        row = {field: data.get(field, "") for field in FIELDNAMES}
        row["timestamp"] = row["timestamp"] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row["status"] = row["status"] or "New"

        with open(LEADS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(row)
        return True
    except Exception as e:
        print(f"[LeadsManager] Error saving lead: {e}")
        return False


def get_all_leads() -> list[dict]:
    """Return all leads as a list of dicts."""
    _ensure_file()
    try:
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception:
        return []


def update_lead_status(timestamp: str, new_status: str) -> bool:
    """Update the status of a lead by its timestamp."""
    _ensure_file()
    leads = get_all_leads()
    updated = False
    for lead in leads:
        if lead["timestamp"] == timestamp:
            lead["status"] = new_status
            updated = True
            break
    if updated:
        try:
            with open(LEADS_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(leads)
        except Exception:
            return False
    return updated
