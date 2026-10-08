"""
VeriLens AI
Immigration Screening Service

This module provides ONE simple entry point for the rest of the application.

It combines:
    1. Passport verification
    2. Visa verification
    3. Security screening

P1 and P4 can call this module without needing to know
the internal implementation of each individual module.
"""

from typing import Any, Dict

from backend.immigration.passport import verify_passport
from backend.immigration.visa import verify_visa
from backend.security.screening import screen_security


def run_immigration_screening(traveler: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete immigration screening pipeline.

    Expected traveler fields:

        {
            "passport_number": "DEMO-P-1001",
            "name": "JOHN CARTER",
            "date_of_birth": "1998-08-15",
            "nationality": "USA"
        }

    Returns a stable JSON-compatible structure that can be
    consumed by FastAPI, the frontend, and the AI decision engine.
    """

    passport_number = traveler.get("passport_number")

    if not passport_number:
        return {
            "success": False,
            "traveler": traveler,
            "immigration": {
                "passport_found": False,
                "details_match": False,
                "visa_required": False,
                "visa_valid": False,
                "visa_passport_match": False,
                "reason": "Passport number is required"
            },
            "security": {
                "match": False,
                "status": "CLEAR",
                "reason": None
            },
            "final_status": "REVIEW",
            "reasons": [
                "Passport number is required"
            ]
        }

    # ---------------------------------------------------------
    # 1. PASSPORT VERIFICATION
    # ---------------------------------------------------------

    passport_result = verify_passport(traveler)

    passport_found = passport_result.get(
        "passport_found",
        False
    )

    details_match = passport_result.get(
        "details_match",
        False
    )

    passport_reason = passport_result.get(
        "reason"
    )

    # ---------------------------------------------------------
    # 2. VISA VERIFICATION
    # ---------------------------------------------------------

    # If passport does not exist in our synthetic database,
    # visa verification should not be trusted.
    if passport_found:
        visa_result = verify_visa(traveler)
    else:
        visa_result = {
            "visa_required": True,
            "visa_valid": False,
            "visa_passport_match": False,
            "reason": "Passport not found, visa verification skipped"
        }

    visa_required = visa_result.get(
        "visa_required",
        False
    )

    visa_valid = visa_result.get(
        "visa_valid",
        False
    )

    visa_passport_match = visa_result.get(
        "visa_passport_match",
        False
    )

    visa_reason = visa_result.get(
        "reason"
    )

    # ---------------------------------------------------------
    # 3. SECURITY SCREENING
    # ---------------------------------------------------------

    security_result = screen_security(traveler)

    security_match = security_result.get(
        "match",
        False
    )

    security_status = security_result.get(
        "status",
        "CLEAR"
    )

    security_reason = security_result.get(
        "reason"
    )

    # ---------------------------------------------------------
    # 4. COLLECT REASONS
    # ---------------------------------------------------------

    reasons = []

    if not passport_found:
        reasons.append(
            "Passport not found in synthetic database"
        )

    elif not details_match:
        reasons.append(
            passport_reason
            or "Passport details do not match database"
        )

    if visa_required and not visa_valid:
        reasons.append(
            visa_reason
            or "Visa is invalid"
        )

    if visa_required and not visa_passport_match:
        # Avoid duplicate visa messages when visa verification
        # already supplied a useful reason.
        if visa_reason:
            if visa_reason not in reasons:
                reasons.append(visa_reason)
        else:
            reasons.append(
                "Visa does not belong to passport"
            )

    if security_match:
        reasons.append(
            security_reason
            or "Security screening match detected"
        )

    # Remove duplicate reasons while preserving order.
    reasons = list(dict.fromkeys(reasons))

    # ---------------------------------------------------------
    # 5. FINAL STATUS
    # ---------------------------------------------------------

    #
    # SECURITY ALERT
    #
    if security_match:
        final_status = "SECURITY_ALERT"

    #
    # REVIEW
    #
    elif (
        not passport_found
        or not details_match
        or (
            visa_required
            and not visa_valid
        )
        or (
            visa_required
            and not visa_passport_match
        )
    ):
        final_status = "REVIEW"

    #
    # CLEAR
    #
    else:
        final_status = "CLEAR"

    # ---------------------------------------------------------
    # 6. FINAL RESPONSE
    # ---------------------------------------------------------

    return {
        "success": True,

        "traveler": {
            "name": traveler.get("name"),
            "passport_number": passport_number,
            "date_of_birth": traveler.get("date_of_birth"),
            "nationality": traveler.get("nationality")
        },

        "immigration": {
            "passport_found": passport_found,
            "details_match": details_match,
            "visa_required": visa_required,
            "visa_valid": visa_valid,
            "visa_passport_match": visa_passport_match,
            "reason": passport_reason or visa_reason
        },

        "security": {
            "match": security_match,
            "status": security_status,
            "reason": security_reason
        },

        "final_status": final_status,

        "reasons": reasons,

        "checks": {
            "passport": passport_found and details_match,

            "visa": (
                not visa_required
                or (
                    visa_valid
                    and visa_passport_match
                )
            ),

            "security": not security_match
        }
    }


# -------------------------------------------------------------
# LOCAL TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 70)
    print("VERILENS AI - IMMIGRATION SCREENING SERVICE")
    print("=" * 70)

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
            "name": "Indian citizen",

            "data": {
                "passport_number": "DEMO-P-1003",
                "name": "ARUN KUMAR",
                "date_of_birth": "2000-01-01",
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
        },

        {
            "name": "Security review traveler",

            "data": {
                "passport_number": "DEMO-P-1002",
                "name": "EMILY JOHNSON",
                "date_of_birth": "1995-05-20",
                "nationality": "USA"
            }
        },

        {
            "name": "Wrong date of birth",

            "data": {
                "passport_number": "DEMO-P-1001",
                "name": "JOHN CARTER",
                "date_of_birth": "2000-01-01",
                "nationality": "USA"
            }
        }
    ]

    for test in test_cases:

        print("\n")
        print("=" * 70)
        print(test["name"])
        print("=" * 70)

        result = run_immigration_screening(
            test["data"]
        )

        print("\nTRAVELER")
        print("-" * 40)

        for key, value in result["traveler"].items():
            print(f"{key}: {value}")

        print("\nIMMIGRATION")
        print("-" * 40)

        for key, value in result["immigration"].items():
            print(f"{key}: {value}")

        print("\nSECURITY")
        print("-" * 40)

        for key, value in result["security"].items():
            print(f"{key}: {value}")

        print("\nCHECKS")
        print("-" * 40)

        for key, value in result["checks"].items():
            print(f"{key}: {value}")

        print("\nFINAL STATUS")
        print("-" * 40)

        print(result["final_status"])

        if result["reasons"]:
            print("\nREASONS")

            for reason in result["reasons"]:
                print(f"- {reason}")

    print("\n")
    print("=" * 70)
    print("SCREENING SERVICE TEST COMPLETE")
    print("=" * 70)