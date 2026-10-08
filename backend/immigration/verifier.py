from backend.immigration.passport import verify_passport
from backend.immigration.visa import verify_visa


def verify_immigration(passport_details):
    """
    Run passport and visa verification together.

    Expected passport_details:
    {
        "passport_number": "DEMO-P-1001",
        "name": "JOHN CARTER",
        "date_of_birth": "1998-08-15",
        "nationality": "USA"
    }

    Returns the shared immigration contract:
    {
        "passport_found": bool,
        "visa_required": bool,
        "visa_valid": bool,
        "visa_passport_match": bool
    }
    """

    # ---------------------------------------------------------
    # 1. Verify passport against synthetic passport database
    # ---------------------------------------------------------
    passport_result = verify_passport(passport_details)

    passport_found = passport_result.get("passport_found", False)

    # If passport does not exist, immigration verification
    # cannot safely continue.
    if not passport_found:
        return {
            "passport_found": False,
            "visa_required": False,
            "visa_valid": False,
            "visa_passport_match": False,
            "reason": "Passport not found in synthetic database"
        }

    # If passport exists but its details do not match the
    # database, flag the inconsistency.
    if not passport_result.get("details_match", False):
        return {
            "passport_found": True,
            "visa_required": True,
            "visa_valid": False,
            "visa_passport_match": False,
            "reason": passport_result.get(
                "reason",
                "Passport details do not match database"
            ),
            "mismatched_fields": passport_result.get(
                "mismatched_fields",
                []
            )
        }

    # ---------------------------------------------------------
    # 2. Determine nationality
    # ---------------------------------------------------------
    nationality = passport_details.get("nationality", "").upper()

    # Indian citizens do not require an Indian visa.
    # This keeps the system aligned with the intended
    # immigration screening flow.
    if nationality in {
        "INDIA",
        "INDIAN",
        "IND"
    }:
        return {
            "passport_found": True,
            "visa_required": False,
            "visa_valid": True,
            "visa_passport_match": True,
            "reason": None
        }

    # ---------------------------------------------------------
    # 3. Foreign national: verify Indian visa/ETA
    # ---------------------------------------------------------
    passport_number = passport_details.get("passport_number")

    visa_result = verify_visa(passport_number)

    return {
        "passport_found": True,
        "visa_required": True,
        "visa_valid": visa_result.get("visa_valid", False),
        "visa_passport_match": visa_result.get(
            "visa_passport_match",
            False
        ),
        "reason": visa_result.get("reason"),
    }


# -------------------------------------------------------------
# Manual test block
# -------------------------------------------------------------
if __name__ == "__main__":

    test_cases = [
        {
            "name": "Valid foreign traveler",
            "data": {
                "passport_number": "DEMO-P-1001",
                "name": "JOHN CARTER",
                "date_of_birth": "1998-08-15",
                "nationality": "USA"
            }
        },
        {
            "name": "Expired visa traveler",
            "data": {
                "passport_number": "DEMO-P-1002",
                "name": "EMILY JOHNSON",
                "date_of_birth": "1995-03-22",
                "nationality": "USA"
            }
        },
        {
            "name": "Indian citizen",
            "data": {
                "passport_number": "DEMO-P-1003",
                "name": "ARJUN MENON",
                "date_of_birth": "1999-11-10",
                "nationality": "INDIA"
            }
        },
        {
            "name": "Unknown passport",
            "data": {
                "passport_number": "DEMO-P-9998",
                "name": "UNKNOWN PERSON",
                "date_of_birth": "2000-01-01",
                "nationality": "USA"
            }
        }
    ]

    for test in test_cases:
        print("\n" + "=" * 60)
        print(test["name"])
        print("=" * 60)

        result = verify_immigration(test["data"])

        for key, value in result.items():
            print(f"{key}: {value}")