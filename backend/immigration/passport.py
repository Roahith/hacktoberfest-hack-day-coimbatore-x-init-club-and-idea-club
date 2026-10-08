import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "passports.json"
)


def load_passports():
    """Load synthetic passport records from the demo database."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def verify_passport(passport_details):
    """
    Verify passport details against the synthetic passport database.

    Expected input:
    {
        "passport_number": "DEMO-P-1001",
        "name": "JOHN CARTER",
        "dob": "1998-08-15",
        "nationality": "USA"
    }
    """

    passports = load_passports()

    passport_number = passport_details.get("passport_number")

    if not passport_number:
        return {
            "passport_found": False,
            "details_match": False,
            "reason": "Passport number is missing"
        }

    for passport in passports:
        if passport.get("passport_number") == passport_number:

            fields_to_check = [
                "name",
                "date_of_birth",
                "nationality"
            ]

            mismatches = []

            for field in fields_to_check:
                supplied_value = passport_details.get(field)
                database_value = passport.get(field)

                if supplied_value != database_value:
                    mismatches.append(field)

            if mismatches:
                return {
                    "passport_found": True,
                    "details_match": False,
                    "reason": "Passport details do not match database",
                    "mismatched_fields": mismatches
                }

            return {
                "passport_found": True,
                "details_match": True,
                "reason": None
            }

    return {
        "passport_found": False,
        "details_match": False,
        "reason": "Passport not found in synthetic database"
    }