import json
from datetime import date
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "visas.json"
)


def load_visas():
    """Load synthetic visa records from the demo database."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def verify_visa(passport_number):
    """
    Verify whether a valid visa exists for the supplied passport.

    Returns:
        visa_required
        visa_valid
        visa_passport_match
        reason
    """

    visas = load_visas()

    for visa in visas:
        if visa.get("passport_number") == passport_number:

            expiry_date = date.fromisoformat(
                visa["expiry_date"]
            )

            if expiry_date < date.today():
                return {
                    "visa_required": True,
                    "visa_valid": False,
                    "visa_passport_match": True,
                    "reason": "Visa has expired"
                }

            if visa.get("status") != "ACTIVE":
                return {
                    "visa_required": True,
                    "visa_valid": False,
                    "visa_passport_match": True,
                    "reason": "Visa is not active"
                }

            return {
                "visa_required": True,
                "visa_valid": True,
                "visa_passport_match": True,
                "reason": None
            }

    return {
        "visa_required": True,
        "visa_valid": False,
        "visa_passport_match": False,
        "reason": "No visa found for passport"
    }