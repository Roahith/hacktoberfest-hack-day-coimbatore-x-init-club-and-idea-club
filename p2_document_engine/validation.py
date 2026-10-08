import re


def normalize(value):
    """Normalize a value before comparison."""

    if value is None:
        return ""

    return re.sub(
        r"[^A-Z0-9]",
        "",
        str(value).upper()
    )


def compare_values(value1, value2):
    """Compare two values after normalization."""

    return normalize(value1) == normalize(value2)


def extract_passport_number_from_ocr(text):
    """Try to find a passport number in OCR text."""

    patterns = [
        r"PASSPORT\s*(?:NO|NUMBER|#)?\s*[:\-]?\s*([A-Z0-9]{6,12})",
        r"PASSPORT\s*[:\-]?\s*([A-Z0-9]{6,12})",
    ]

    text = text.upper()

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return match.group(1)

    return None


def extract_date_of_birth(text):
    """Try to find a date of birth in OCR text."""

    patterns = [
        r"(?:DATE OF BIRTH|DOB)\s*[:\-]?\s*(\d{2}[\/\-]\d{2}[\/\-]\d{4})",
        r"(?:DATE OF BIRTH|DOB)\s*[:\-]?\s*(\d{4}[\/\-]\d{2}[\/\-]\d{2})",
    ]

    text = text.upper()

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return match.group(1)

    return None


def database_comparison(
    passport,
    database_record
):
    """
    Compare extracted passport information
    against the synthetic database.

    database_record will be supplied by P3.
    """

    if not database_record:
        return {
            "available": False,
            "match": None,
            "mismatches": []
        }

    mismatches = []

    fields = [
        "passport_number",
        "nationality",
        "date_of_birth"
    ]

    for field in fields:

        passport_value = passport.get(
            field
        )

        database_value = database_record.get(
            field
        )

        if not compare_values(
            passport_value,
            database_value
        ):

            mismatches.append(field)

    passport_name = normalize(
        passport.get("surname", "")
        + passport.get("given_names", "")
    )

    database_name = normalize(
        database_record.get("name", "")
    )

    if passport_name and database_name:

        if passport_name != database_name:
            mismatches.append("name")

    return {
        "available": True,
        "match": len(mismatches) == 0,
        "mismatches": mismatches
    }


def calculate_tamper_indicators(
    mrz,
    database_result
):
    """Generate evidence-based document warnings."""

    indicators = []

    # MRZ missing
    if not mrz.get("detected", False):

        indicators.append({
            "code": "MRZ_NOT_DETECTED",
            "message": "Passport MRZ could not be detected.",
            "severity": "HIGH"
        })

    # MRZ check digits failed
    elif not mrz.get("valid", False):

        indicators.append({
            "code": "MRZ_CHECK_DIGIT_FAILURE",
            "message": "One or more MRZ check digits failed.",
            "severity": "HIGH"
        })

    # Database mismatch
    if database_result.get("available"):

        if not database_result.get("match"):

            indicators.append({
                "code": "DATABASE_MISMATCH",
                "message": "Passport information does not match the database.",
                "severity": "HIGH"
            })

    if not indicators:

        return {
            "suspicious": False,
            "severity": "LOW",
            "indicators": []
        }

    severity_order = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3
    }

    highest = max(
        indicators,
        key=lambda x: severity_order[x["severity"]]
    )["severity"]

    return {
        "suspicious": True,
        "severity": highest,
        "indicators": indicators
    }