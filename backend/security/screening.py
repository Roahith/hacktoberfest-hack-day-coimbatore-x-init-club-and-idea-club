import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "security_records.json"
)


def load_security_records():
    """Load synthetic security records from the demo database."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def screen_security(passport_details):
    """
    Check passport details against the synthetic security database.

    Expected input:
    {
        "name": "JOHN CARTER",
        "dob": "1998-08-15",
        "passport_number": "DEMO-P-1001"
    }

    Returns:
    {
        "match": false,
        "status": "CLEAR",
        "reason": null
    }
    """

    records = load_security_records()

    passport_number = passport_details.get("passport_number")
    name = passport_details.get("name")
    dob = passport_details.get("dob")

    for record in records:

        if record["passport_number"] != passport_number:
            continue

        # Passport number exists in the synthetic security database.
        if (
            record["name"] == name
            and record["date_of_birth"] == dob
        ):
            if record["status"] == "REVIEW":
                return {
                    "match": True,
                    "status": "REVIEW",
                    "reason": record["reason"]
                }

            return {
                "match": False,
                "status": "CLEAR",
                "reason": None
            }

        # Passport number exists but personal details do not match.
        return {
            "match": True,
            "status": "REVIEW",
            "reason": "Passport details do not match the synthetic security record"
        }

    # No matching security record found.
    return {
        "match": False,
        "status": "CLEAR",
        "reason": None
    }