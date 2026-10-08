"""
VeriLens AI - Immigration Screening Pipeline

Combines:
    1. Passport verification
    2. Visa verification
    3. Synthetic security screening

This module provides one unified function for the rest of
the VeriLens backend to call.

All databases used by this prototype are synthetic/demo data.
"""

from .passport import verify_passport
from .visa import verify_visa
from ..security.screening import screen_security


def verify_immigration(passport_details):
    """
    Perform complete immigration pre-screening.

    Expected input:

    {
        "passport_number": "DEMO-P-1001",
        "name": "JOHN CARTER",
        "date_of_birth": "1998-08-15",
        "nationality": "USA"
    }

    Returns:

    {
        "traveler": {...},
        "immigration": {...},
        "security": {...},
        "final_status": "CLEAR"
    }
    """

    # ---------------------------------------------------------
    # 1. BASIC INPUT VALIDATION
    # ---------------------------------------------------------

    if not isinstance(passport_details, dict):
        return {
            "traveler": {},
            "immigration": {
                "passport_found": False,
                "details_match": False,
                "visa_required": False,
                "visa_valid": False,
                "visa_passport_match": False,
                "reason": "Invalid passport details input"
            },
            "security": {
                "match": False,
                "status": "CLEAR",
                "reason": None
            },
            "final_status": "REVIEW"
        }

    passport_number = passport_details.get("passport_number")
    name = passport_details.get("name")
    date_of_birth = passport_details.get("date_of_birth")
    nationality = passport_details.get("nationality")

    # ---------------------------------------------------------
    # 2. CREATE TRAVELER SUMMARY
    # ---------------------------------------------------------

    traveler = {
        "name": name,
        "passport_number": passport_number,
        "date_of_birth": date_of_birth,
        "nationality": nationality
    }

    # ---------------------------------------------------------
    # 3. VERIFY PASSPORT
    # ---------------------------------------------------------

    passport_result = verify_passport(passport_details)

    passport_found = passport_result.get(
        "passport_found",
        False
    )

    details_match = passport_result.get(
        "details_match",
        False
    )

    # ---------------------------------------------------------
    # 4. DETERMINE VISA REQUIREMENT
    # ---------------------------------------------------------
    #
    # For our synthetic prototype:
    #
    # INDIA -> visa not required
    # Other nationalities -> visa required
    #
    # This is only demo logic and is NOT real immigration policy.
    # ---------------------------------------------------------

    normalized_nationality = str(
        nationality or ""
    ).strip().upper()

    if normalized_nationality in {
        "INDIA",
        "INDIAN",
        "IN"
    }:
        visa_required = False
    else:
        visa_required = True

    # ---------------------------------------------------------
    # 5. VERIFY VISA
    # ---------------------------------------------------------

    if visa_required and passport_found and details_match:

        visa_result = verify_visa(
            passport_number
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

    else:

        # Indian citizens do not require a visa
        # in this prototype.

        if not visa_required:

            visa_valid = True
            visa_passport_match = True
            visa_reason = None

        else:

            visa_valid = False
            visa_passport_match = False

            if not passport_found:

                visa_reason = (
                    "Passport not found, "
                    "visa verification skipped"
                )

            elif not details_match:

                visa_reason = (
                    "Passport details mismatch, "
                    "visa verification requires review"
                )

            else:

                visa_reason = (
                    "Visa verification could not be completed"
                )

    # ---------------------------------------------------------
    # 6. SYNTHETIC SECURITY SCREENING
    # ---------------------------------------------------------

    security_result = screen_security(
        passport_details
    )

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
    # 7. BUILD IMMIGRATION RESULT
    # ---------------------------------------------------------

    immigration_result = {
        "passport_found": passport_found,
        "details_match": details_match,
        "visa_required": visa_required,
        "visa_valid": visa_valid,
        "visa_passport_match": visa_passport_match,
        "reason": visa_reason
    }

    # ---------------------------------------------------------
    # 8. DETERMINE FINAL STATUS
    # ---------------------------------------------------------
    #
    # CLEAR
    #   Passport valid
    #   Details match
    #   Visa valid if required
    #   Visa belongs to passport
    #   Security clear
    #
    # REVIEW
    #   Something requires human/secondary review
    #
    # SECURITY_ALERT
    #   Security database match
    # ---------------------------------------------------------

    if security_match:

        final_status = "SECURITY_ALERT"

    elif not passport_found:

        final_status = "REVIEW"

    elif not details_match:

        final_status = "REVIEW"

    elif visa_required and not visa_valid:

        final_status = "REVIEW"

    elif visa_required and not visa_passport_match:

        final_status = "REVIEW"

    else:

        final_status = "CLEAR"

    # ---------------------------------------------------------
    # 9. RETURN UNIFIED RESULT
    # ---------------------------------------------------------

    return {
        "traveler": traveler,
        "immigration": immigration_result,
        "security": {
            "match": security_match,
            "status": security_status,
            "reason": security_reason
        },
        "final_status": final_status
    }


# -------------------------------------------------------------
# SIMPLE COMMAND-LINE TESTING
# -------------------------------------------------------------

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("VERILENS AI - IMMIGRATION SCREENING PIPELINE")
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
                "date_of_birth": "1997-06-20",
                "nationality": "INDIA"
            }
        },

        {
            "name": "Wrong DOB",
            "data": {
                "passport_number": "DEMO-P-1001",
                "name": "JOHN CARTER",
                "date_of_birth": "2000-01-01",
                "nationality": "USA"
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
                "date_of_birth": "1995-03-22",
                "nationality": "USA"
            }
        }

    ]

    for test in test_cases:

        print()
        print("-" * 70)
        print(test["name"])
        print("-" * 70)

        result = verify_immigration(
            test["data"]
        )

        print()
        print("TRAVELER")
        print(
            "  Name:",
            result["traveler"]["name"]
        )
        print(
            "  Passport:",
            result["traveler"]["passport_number"]
        )
        print(
            "  Nationality:",
            result["traveler"]["nationality"]
        )

        print()
        print("IMMIGRATION")

        print(
            "  Passport found:",
            result["immigration"]["passport_found"]
        )

        print(
            "  Details match:",
            result["immigration"]["details_match"]
        )

        print(
            "  Visa required:",
            result["immigration"]["visa_required"]
        )

        print(
            "  Visa valid:",
            result["immigration"]["visa_valid"]
        )

        print(
            "  Visa passport match:",
            result["immigration"]["visa_passport_match"]
        )

        print(
            "  Reason:",
            result["immigration"]["reason"]
        )

        print()
        print("SECURITY")

        print(
            "  Match:",
            result["security"]["match"]
        )

        print(
            "  Status:",
            result["security"]["status"]
        )

        print(
            "  Reason:",
            result["security"]["reason"]
        )

        print()
        print(
            "FINAL STATUS:",
            result["final_status"]
        )

    print()
    print("=" * 70)
    print("PIPELINE TEST COMPLETE")
    print("=" * 70)